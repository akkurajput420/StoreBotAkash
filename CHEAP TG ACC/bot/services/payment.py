import asyncio
from telethon import Button
from bot.services.fampay import FamPayClient, PaymentError
from bot.utils import templates as tpl

def payment_action_buttons(oid, pending=None):
    o=oid.replace(" ","")
    return [[Button.inline("✅ I've Paid — Check", f"paychk_{o}"),
             Button.inline("❌ Cancel", f"paycan_{o}")]]

def add_balance_amount_buttons(pending_acc_id=None, suggested=None):
    amounts=[50,100,200,500,1000]
    if suggested and int(suggested) not in amounts:
        amounts=[int(suggested)]+amounts[:4]
    btns,r=[],[]
    for a in amounts[:6]:
        s=f"_{pending_acc_id}" if pending_acc_id else ""
        r.append(Button.inline(f"₹{a}", f"abl_{a}{s}"))
        if len(r)==2: btns.append(r); r=[]
    if r: btns.append(r)
    btns.append([Button.inline("✏️ Custom", f"ablcust{'_'+str(pending_acc_id) if pending_acc_id else ''}")])
    return btns

class PaymentService:
    def __init__(self, bot, settings, repo):
        self.bot=bot; self.settings=settings; self.repo=repo
        self.fampay=FamPayClient(settings)
        self._poll={}

    def _amount_error(self, amount):
        if amount < self.settings.payment_min_amount:
            return f"Min ₹{self.settings.payment_min_amount:g}"
        if amount > self.settings.payment_max_amount:
            return "Too large"
        return None

    async def start_payment(self, user_id, amount, pending_acc_id=None, reply_to=None):
        err=self._amount_error(amount)
        if err:
            t=tpl.error("Invalid", err)
            if reply_to: await reply_to.edit(t, parse_mode="html")
            else: await self.bot.send_message(user_id,t, parse_mode="html")
            return
        amount=round(amount,2)
        try:
            order=await self.fampay.generate_order(amount)
        except PaymentError as e:
            t=tpl.error("Payment", str(e))
            if reply_to: await reply_to.edit(t, parse_mode="html")
            return
        except Exception:
            t=tpl.error("Payment", "Server unreachable")
            if reply_to: await reply_to.edit(t, parse_mode="html")
            return
        oid=order["order_id"]
        paid=float(order.get("amount",amount))
        note=""
        if abs(paid-amount)>0.009:
            note=f"\n<i>Entered ₹{amount:g} → pay ₹{paid:.2f}</i>"
        await self.repo.create_payment_order(oid,user_id,paid,pending_acc_id)
        text=tpl.payment_order(oid,paid,self.settings.fampay_upi_id,order.get("upi_link",""),note)
        btns=payment_action_buttons(oid,pending_acc_id)
        qr=order.get("qr_code","")
        if qr:
            if reply_to:
                try: await reply_to.delete()
                except Exception: pass
            msg=await self.bot.send_file(user_id,qr,caption=text,buttons=btns,parse_mode="html")
        elif reply_to:
            await reply_to.edit(text,buttons=btns,parse_mode="html",link_preview=False)
            msg=reply_to
        else:
            msg=await self.bot.send_message(user_id,text,buttons=btns,parse_mode="html",link_preview=False)
        self._poll[oid]=asyncio.create_task(self._poll_pay(user_id,oid,msg.id))

    async def _poll_pay(self, uid, oid, mid):
        for _ in range(self.settings.payment_poll_timeout//self.settings.payment_poll_interval):
            await asyncio.sleep(self.settings.payment_poll_interval)
            row=await self.repo.get_payment_order(oid)
            if row and row.get("credited"): return
            try:
                res=await self.fampay.verify_payment(oid)
            except Exception:
                continue
            if res.get("payment") and res.get("success"):
                if await self.repo.credit_payment_order(oid):
                    bal=await self.repo.get_balance(uid)
                    try:
                        await self.bot.edit_message(uid,mid,
                            tpl.payment_success(float(res.get("amount",row["amount"])),oid,bal),
                            parse_mode="html")
                    except Exception:
                        pass
                return

    async def check_payment_now(self, uid, oid, mid):
        row=await self.repo.get_payment_order(oid)
        if not row or row["user_id"]!=uid: return "Invalid order"
        if row.get("credited"):
            return f"Done. Balance {await self.repo.get_balance(uid):.2f}"
        try:
            res=await self.fampay.verify_payment(oid)
        except Exception:
            return "Server error"
        if res.get("payment") and await self.repo.credit_payment_order(oid):
            return f"✅ Added! Balance {await self.repo.get_balance(uid):.2f}"
        return res.get("msg","Not paid yet")

    def cancel_polling(self, oid):
        t=self._poll.pop(oid,None)
        if t and not t.done(): t.cancel()

    async def stop_all(self):
        for t in list(self._poll.values()):
            t.cancel()
