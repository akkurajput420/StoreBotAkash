from telethon import TelegramClient, events
from bot.constants import ACCOUNTS_PER_PAGE, STATE_AWAITING_ADD_BALANCE_AMOUNT, STATE_AWAITING_COUPON_CODE, STATE_AWAITING_SUPPORT
from bot.handlers import get_ctx
from bot.keyboards.inline import account_list_buttons
from bot.keyboards.main import cancel_button, user_keyboard
from bot.middlewares.admin import is_admin
from bot.middlewares.antiflood import AntiFloodMiddleware
from bot.middlewares.errors import ErrorMiddleware
from bot.services.payment import add_balance_amount_buttons
from bot.utils.templates import account_dashboard, add_balance_menu, shop_header, vip_rank
from bot.utils import templates as tpl
from bot.utils.validators import validate_amount

_flood = None

async def _shop(event, page=0):
    ctx = get_ctx()
    stock = await ctx.repo.count_available()
    accs = await ctx.repo.list_available_accounts(ACCOUNTS_PER_PAGE, page*ACCOUNTS_PER_PAGE)
    if not accs:
        await event.respond(tpl.warn("Empty","No stock"), parse_mode="html")
        return
    await event.respond(shop_header(stock,page),
        buttons=account_list_buttons(accs,page,len(accs)==ACCOUNTS_PER_PAGE), parse_mode="html")

def register(bot, ctx):
    global _flood
    _flood = AntiFloodMiddleware(ctx.rate_limiter)

    @bot.on(events.NewMessage(incoming=True))
    @ErrorMiddleware.handler
    async def user_handler(event):
        raw = (event.raw_text or "").strip()
        if event.pattern_match or raw.startswith("/start"):
            return
        uid = event.sender_id
        if is_admin(uid) and get_ctx().states.get_state(uid):
            return
        if raw in ("/cancel","❌ Cancel Operation") and not is_admin(uid):
            get_ctx().states.clear(uid)
            await event.respond(tpl.warn("Cancelled",""), buttons=user_keyboard(), parse_mode="html")
            return
        if not await _flood.check(event):
            return
        st = get_ctx().states.get(uid)
        state = st.get("state")

        if raw == "👤 My Account":
            await get_ctx().repo.init_user(uid)
            b = await get_ctx().repo.get_balance(uid)
            h = await get_ctx().repo.get_purchase_history(uid,100)
            await event.respond(account_dashboard(uid,b,vip_rank(b),len(h)), parse_mode="html")
        elif raw in ("🛒 Buy ID","🔄 Refresh Shop"):
            await _shop(event)
        elif raw == "💰 Add Balance":
            b = await get_ctx().repo.get_balance(uid)
            await event.respond(add_balance_menu(b), buttons=add_balance_amount_buttons(), parse_mode="html")
        elif raw == "📜 Purchase History":
            rows = await get_ctx().repo.get_purchase_history(uid)
            txt = "\n".join(f"• {r.get('phone')} — {r.get('price')}" for r in rows[:15]) or "None"
            await event.respond(f"<b>History</b>\n{txt}", parse_mode="html")
        elif raw == "🎟️ Redeem Coupon":
            get_ctx().states.set(uid, STATE_AWAITING_COUPON_CODE)
            await event.respond("Enter code:", buttons=cancel_button(), parse_mode="html")
        elif raw == "🎫 Support":
            get_ctx().states.set(uid, STATE_AWAITING_SUPPORT)
            await event.respond("Your message:", buttons=cancel_button(), parse_mode="html")
        elif state == STATE_AWAITING_ADD_BALANCE_AMOUNT:
            amt = validate_amount(raw, min_val=get_ctx().settings.payment_min_amount)
            if not amt:
                await event.respond("Invalid amount", parse_mode="html")
                return
            get_ctx().states.clear(uid)
            ld = await event.respond(tpl.loading("Payment"), parse_mode="html")
            await get_ctx().payment_service.start_payment(uid, amt, reply_to=ld)
        elif state == STATE_AWAITING_SUPPORT:
            await get_ctx().bot.send_message(get_ctx().settings.owner_id,
                f"Support {uid}: {raw}", parse_mode="html")
            get_ctx().states.clear(uid)
            await event.respond(tpl.success("Sent",""), buttons=user_keyboard(), parse_mode="html")
