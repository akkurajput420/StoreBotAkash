import asyncio
import logging
from telethon import Button
from telethon.errors import MessageNotModifiedError, RPCError

from bot.services.fampay import FamPayClient, PaymentError
from bot.utils import templates as tpl

logger = logging.getLogger(__name__)


def payment_action_buttons(oid: str, pending=None) -> list:
    clean_oid = oid.replace(" ", "")
    return [
        [
            Button.inline("✅ I've Paid — Check", data=f"paychk_{clean_oid}"),
            Button.inline("❌ Cancel", data=f"paycan_{clean_oid}")
        ]
    ]


def add_balance_amount_buttons(pending_acc_id=None, suggested=None) -> list:
    amounts = [25, 50, 100, 200, 500]
    if suggested:
        try:
            s_val = int(suggested)
            if s_val not in amounts and s_val > 0:
                amounts = [s_val] + amounts[:4]
        except (ValueError, TypeError):
            pass

    btns, row = [], []
    suffix = f"_{pending_acc_id}" if pending_acc_id else ""
    
    for a in amounts[:6]:
        row.append(Button.inline(f"₹{a}", data=f"abl_{a}{suffix}"))
        if len(row) == 2:
            btns.append(row)
            row = []
            
    if row:
        btns.append(row)
        
    btns.append([Button.inline("✏️ Custom", data=f"ablcust{suffix}")])
    return btns


class PaymentService:
    def __init__(self, bot, settings, repo):
        self.bot = bot
        self.settings = settings
        self.repo = repo
        self.fampay = FamPayClient(settings)
        self._poll: dict[str, asyncio.Task] = {}

    def _amount_error(self, amount: float) -> str | None:
        if amount < self.settings.payment_min_amount:
            return f"Min ₹{self.settings.payment_min_amount:g}"
        if amount > self.settings.payment_max_amount:
            return f"Max ₹{self.settings.payment_max_amount:g}"
        return None

    async def start_payment(self, user_id: int, amount: float, pending_acc_id=None, reply_to=None):
        err = self._amount_error(amount)
        if err:
            text = tpl.error("Invalid Amount", err)
            if reply_to:
                await reply_to.edit(text, parse_mode="html")
            else:
                await self.bot.send_message(user_id, text, parse_mode="html")
            return

        clean_amount = round(float(amount), 2)
        try:
            order = await self.fampay.generate_order(clean_amount)
        except PaymentError as e:
            text = tpl.error("Payment Error", str(e))
            if reply_to:
                await reply_to.edit(text, parse_mode="html")
            return
        except Exception as e:
            logger.error(f"Order generation exception: {e}")
            text = tpl.error("Payment", "Server unreachable, please try again later.")
            if reply_to:
                await reply_to.edit(text, parse_mode="html")
            return

        oid = order["order_id"]
        paid = float(order.get("amount", clean_amount))
        note = ""
        if abs(paid - clean_amount) > 0.009:
            note = f"\n<i>Entered ₹{clean_amount:g} → Pay ₹{paid:.2f}</i>"

        await self.repo.create_payment_order(oid, user_id, paid, pending_acc_id)
        text = tpl.payment_order(oid, paid, self.settings.fampay_upi_id, order.get("upi_link", ""), note)
        btns = payment_action_buttons(oid, pending_acc_id)
        qr = order.get("qr_code", "")

        msg = None
        if qr:
            if reply_to:
                try:
                    await reply_to.delete()
                except Exception:
                    pass
            msg = await self.bot.send_file(user_id, qr, caption=text, buttons=btns, parse_mode="html")
        elif reply_to:
            try:
                await reply_to.edit(text, buttons=btns, parse_mode="html", link_preview=False)
                msg = reply_to
            except MessageNotModifiedError:
                msg = reply_to
            except RPCError:
                msg = await self.bot.send_message(user_id, text, buttons=btns, parse_mode="html", link_preview=False)
        else:
            msg = await self.bot.send_message(user_id, text, buttons=btns, parse_mode="html", link_preview=False)

        if msg:
            self.cancel_polling(oid)
            self._poll[oid] = asyncio.create_task(self._poll_pay(user_id, oid, msg.id))

    async def _poll_pay(self, uid: int, oid: str, mid: int):
        try:
            total_polls = int(self.settings.payment_poll_timeout // self.settings.payment_poll_interval)
            for _ in range(total_polls):
                await asyncio.sleep(self.settings.payment_poll_interval)
                
                row = await self.repo.get_payment_order(oid)
                if row and row.get("credited"):
                    return

                try:
                    res = await self.fampay.verify_payment(oid)
                except Exception:
                    continue

                if res.get("payment") and res.get("success"):
                    if await self.repo.credit_payment_order(oid):
                        bal = await self.repo.get_balance(uid)
                        credited_amount = float(res.get("amount", row["amount"] if row else 0))
                        try:
                            await self.bot.edit_message(
                                uid, mid,
                                tpl.payment_success(credited_amount, oid, bal),
                                parse_mode="html"
                            )
                        except Exception as e:
                            logger.warning(f"Failed to edit success msg for order {oid}: {e}")
                    return
        except asyncio.CancelledError:
            pass
        finally:
            self._poll.pop(oid, None)

    async def check_payment_now(self, uid: int, oid: str, mid: int) -> str:
        row = await self.repo.get_payment_order(oid)
        if not row or row["user_id"] != uid:
            return "Invalid order."

        if row.get("credited"):
            self.cancel_polling(oid)
            bal = await self.repo.get_balance(uid)
            return f"Done. Balance: ₹{bal:.2f}"

        try:
            res = await self.fampay.verify_payment(oid)
        except Exception as e:
            logger.error(f"Manual check verify exception for {oid}: {e}")
            return "Server error while verifying."

        if res.get("payment") and res.get("success"):
            if await self.repo.credit_payment_order(oid):
                self.cancel_polling(oid)
                bal = await self.repo.get_balance(uid)
                credited_amount = float(res.get("amount", row["amount"]))
                try:
                    await self.bot.edit_message(
                        uid, mid,
                        tpl.payment_success(credited_amount, oid, bal),
                        parse_mode="html"
                    )
                except Exception:
                    pass
                return f"✅ Added! Balance: ₹{bal:.2f}"

        return res.get("msg", "Payment not received yet.")

    def cancel_polling(self, oid: str):
        task = self._poll.pop(oid, None)
        if task and not task.done():
            task.cancel()

    async def stop_all(self):
        for oid, task in list(self._poll.items()):
            if not task.done():
                task.cancel()
        self._poll.clear()
