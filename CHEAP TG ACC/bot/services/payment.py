import asyncio
import logging
from pathlib import Path
from telethon import Button
from telethon.errors import MessageNotModifiedError, RPCError

from bot.services.fampay import FamPayClient, PaymentError
from bot.utils import templates as tpl

logger = logging.getLogger(__name__)


def payment_action_buttons(oid: str) -> list:
    clean_oid = oid.replace(" ", "")
    return [
        [
            Button.inline("✅ Check Payment", data=f"paychk_{clean_oid}"),
            Button.inline("❌ Cancel Order", data=f"paycan_{clean_oid}")
        ]
    ]


def add_balance_amount_buttons(pending_acc_id=None) -> list:
    amounts = [25, 50, 100, 200, 500]
    btns, row = [], []
    suffix = f"_{pending_acc_id}" if pending_acc_id else ""
    
    for a in amounts:
        row.append(Button.inline(f"₹{a}", data=f"abl_{a}{suffix}"))
        if len(row) == 2:
            btns.append(row)
            row = []
    if row:
        btns.append(row)
        
    btns.append([Button.inline("✏️ Custom Amount", data=f"ablcust{suffix}")])
    return btns


class PaymentService:
    def __init__(self, bot, settings, repo):
        self.bot = bot
        self.settings = settings
        self.repo = repo
        self.fampay = FamPayClient(settings)
        self._poll: dict[str, asyncio.Task] = {}

    async def start_payment(self, user_id: int, amount: float, pending_acc_id=None, reply_to=None):
        clean_amount = round(float(amount), 2)
        try:
            order = await self.fampay.generate_order(clean_amount)
        except Exception as e:
            text = tpl.error("Payment Request Failed", str(e))
            if reply_to:
                await reply_to.edit(text, parse_mode="html")
            return

        oid = order["order_id"]
        paid = float(order.get("amount", clean_amount))
        await self.repo.create_payment_order(oid, user_id, paid, pending_acc_id)
        
        text = tpl.payment_order(oid, paid, self.settings.fampay_upi_id, order.get("upi_link", ""))
        btns = payment_action_buttons(oid)

        # Dynamic Auto-Generated QR Code Scanner or Local Scanner Image Fallback
        qr = order.get("qr_code", "")
        custom_img = Path(self.settings.custom_qr_image_path)
        qr_file = custom_img if custom_img.exists() else qr

        if reply_to:
            try:
                await reply_to.delete()
            except Exception:
                pass

        msg = await self.bot.send_file(
            user_id,
            qr_file,
            caption=text,
            buttons=btns,
            parse_mode="html"
        )

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
                        except Exception:
                            pass
                    return
        except asyncio.CancelledError:
            pass
        finally:
            self._poll.pop(oid, None)

    def cancel_polling(self, oid: str):
        task = self._poll.pop(oid, None)
        if task and not task.done():
            task.cancel()
