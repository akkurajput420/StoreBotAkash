from telethon import TelegramClient, events
from bot.constants import ACCOUNTS_PER_PAGE, STATE_AWAITING_ACCOUNT_AGE, STATE_AWAITING_ACCOUNT_PRICE, STATE_AWAITING_ADD_BALANCE_AMOUNT
from bot.handlers import get_ctx
from bot.keyboards.inline import account_list_buttons, account_preview_buttons, purchased_buttons, insufficient_balance_buttons, admin_panel_buttons
from bot.middlewares.admin import is_admin
from bot.middlewares.errors import ErrorMiddleware
from bot.services.payment import add_balance_amount_buttons
from bot.utils.country import blur_phone
from bot.utils.templates import account_preview, add_balance_menu, insufficient_balance, purchase_success, shop_header, stats_panel
from bot.utils import templates as tpl

def register(bot, ctx):
    @bot.on(events.CallbackQuery)
    @ErrorMiddleware.callback
    async def cb(event):
        uid = event.sender_id
        data = event.data.decode("utf-8")
        c = get_ctx()

        if data.startswith("buy_"):
            aid = int(data.split("_")[1])
            acc = await c.repo.get_account(aid)
            if not acc or acc["status"] != "available":
                await event.answer("Sold!", alert=True)
                return
            bal = await c.repo.get_balance(uid)
            pr = float(acc["price"])
            if bal < pr:
                await event.answer(f"Need ₹{pr-bal:.0f} more", alert=True)
                await event.edit(insufficient_balance(bal,pr,pr-bal),
                    buttons=insufficient_balance_buttons(aid,pr-bal), parse_mode="html")
                return
            await event.edit(account_preview(acc, blur_phone(acc["phone"])),
                buttons=account_preview_buttons(aid), parse_mode="html")
        elif data.startswith("confirm_"):
            aid = int(data.split("_")[1])
            ok, acc, reason = await c.repo.purchase_account(uid, aid)
            if not ok:
                await event.answer(reason, alert=True)
                return
            await event.edit(purchase_success(acc["phone"], acc),
                buttons=purchased_buttons(aid), parse_mode="html")
        elif data.startswith("getotp_"):
            aid = int(data.split("_")[1])
            acc = await c.repo.get_account(aid)
            if acc:
                c.task_queue.enqueue(c.otp_service.start_forwarding(acc["phone"], uid))
                await event.answer("OTP listener on", alert=False)
        elif data.startswith("setage_") and is_admin(uid):
            age = data[7:]
            st = c.states.get(uid)
            if st.get("state") != STATE_AWAITING_ACCOUNT_AGE:
                await event.answer("Expired", alert=True)
                return
            c.states.set(uid, STATE_AWAITING_ACCOUNT_PRICE, **{k:st[k] for k in st if k!="state"}, account_age=age)
            await event.edit(f"Age: <code>{age}</code>\nEnter <b>price INR</b>:", parse_mode="html")
        elif data.startswith("abl_"):
            p = data.split("_")
            amt = float(p[1])
            pacc = int(p[2]) if len(p)>2 else None
            await c.payment_service.start_payment(uid, amt, pending_acc_id=pacc, reply_to=event)
        elif data.startswith("ablcust"):
            pacc = int(data.split("_")[1]) if "_" in data[7:] else None
            c.states.set(uid, STATE_AWAITING_ADD_BALANCE_AMOUNT, pending_acc_id=pacc)
            await event.answer("Send amount", alert=False)
        elif data == "add_bal" or data.startswith("ablmnu"):
            b = await c.repo.get_balance(uid)
            await event.edit(add_balance_menu(b), buttons=add_balance_amount_buttons(), parse_mode="html")
        elif data.startswith("paychk_"):
            msg = await c.payment_service.check_payment_now(uid, data[7:], event.message_id)
            await event.answer(msg, alert=True)
        elif data.startswith("paycan_"):
            c.payment_service.cancel_polling(data[7:])
            await event.edit(tpl.warn("Cancelled",""), parse_mode="html")
        elif data == "cancel_buy":
            await event.edit("Cancelled", parse_mode="html")
        elif data.startswith("page_") or data.startswith("refresh_shop"):
            parts = data.split("_")
            page = int(parts[1]) if "page" in data else int(parts[2] if len(parts)>2 else 0)
            accs = await c.repo.list_available_accounts(ACCOUNTS_PER_PAGE, page*ACCOUNTS_PER_PAGE)
            stock = await c.repo.count_available()
            await event.edit(shop_header(stock,page),
                buttons=account_list_buttons(accs,page,len(accs)==ACCOUNTS_PER_PAGE), parse_mode="html")
        elif data == "admin_analytics" and is_admin(uid):
            u,s,e = await c.repo.get_stats()
            await event.edit(stats_panel(u,s,e,0), buttons=admin_panel_buttons(), parse_mode="html")
