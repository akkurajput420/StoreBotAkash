import logging
from telethon import TelegramClient, events, errors
from bot.constants import *
from bot.handlers import get_ctx
from bot.handlers.owner_account import on_account_logged_in, finalize_account, disconnect_stored_client
from bot.keyboards.main import cancel_button, owner_keyboard
from bot.middlewares.admin import is_admin
from bot.middlewares.antiflood import AntiFloodMiddleware
from bot.middlewares.errors import ErrorMiddleware
from bot.utils.country import detect_country
from bot.utils.security import session_path
from bot.utils.templates import loading, success, error, stats_panel
from bot.utils import templates as tpl
from bot.utils.validators import validate_phone, validate_user_id, validate_amount

logger = logging.getLogger("admin")
_flood = None

def register(bot, ctx):
    global _flood
    _flood = AntiFloodMiddleware(ctx.rate_limiter)

    @bot.on(events.NewMessage(incoming=True))
    @ErrorMiddleware.handler
    async def owner_handler(event):
        if event.pattern_match:
            return
        raw = (event.raw_text or "").strip()
        if raw.startswith("/start"):
            return
        uid = event.sender_id
        if not is_admin(uid):
            return
        if not await _flood.check(event):
            return
        ctx = get_ctx()

        if raw in ("/cancel","❌ Cancel Operation"):
            await disconnect_stored_client(uid)
            ctx.states.clear(uid)
            await event.respond(tpl.warn("Cancelled",""), buttons=owner_keyboard(), parse_mode="html")
            return

        st = ctx.states.get(uid)
        state = st.get("state")

        if raw == "➕ Add Account":
            ctx.states.set(uid, STATE_AWAITING_PHONE)
            await event.respond("<b>📱 Add Account</b>\nSend phone +country code:", buttons=cancel_button(), parse_mode="html")
        elif raw == "📊 Stats":
            u,s,e = await ctx.repo.get_stats()
            await event.respond(stats_panel(u,s,e,0), parse_mode="html")
        elif raw == "💰 Add Money":
            ctx.states.set(uid, STATE_AWAITING_ADD_MONEY_CHAT_ID)
            await event.respond("User ID:", buttons=cancel_button(), parse_mode="html")
        elif raw == "🏷️ Change Price":
            c = await ctx.repo.get_default_price()
            ctx.states.set(uid, STATE_AWAITING_NEW_PRICE)
            await event.respond(f"Current: {c}\nNew price:", buttons=cancel_button(), parse_mode="html")
        elif state == STATE_AWAITING_PHONE:
            phone = validate_phone(raw)
            if not phone:
                await event.respond("Invalid phone", parse_mode="html")
                return
            iso, cn, fl = detect_country(phone)
            client = TelegramClient(session_path(phone, ctx.settings.sessions_dir),
                ctx.settings.api_id, ctx.settings.api_hash)
            await client.connect()
            try:
                if not await client.is_user_authorized():
                    sent = await client.send_code_request(phone)
                    ctx.states.set(uid, STATE_AWAITING_OTP, phone=phone, client=client,
                        phone_code_hash=sent.phone_code_hash, country_code=iso, country_name=cn)
                    await event.respond(f"OTP sent {fl} {cn}", buttons=cancel_button(), parse_mode="html")
                else:
                    await on_account_logged_in(event, uid, client, phone)
            except Exception as e:
                await event.respond(error("Err",str(e)), parse_mode="html")
                ctx.states.clear(uid)
        elif state == STATE_AWAITING_OTP:
            try:
                await st["client"].sign_in(st["phone"], raw.strip(), phone_code_hash=st["phone_code_hash"])
                await on_account_logged_in(event, uid, st["client"], st["phone"])
            except errors.SessionPasswordNeededError:
                ctx.states.set(uid, STATE_AWAITING_2FA, phone=st["phone"], client=st["client"],
                    country_code=st.get("country_code"), country_name=st.get("country_name"),
                    spam_free=st.get("spam_free"), spam_note=st.get("spam_note"))
                await event.respond("2FA password:", buttons=cancel_button(), parse_mode="html")
            except Exception as e:
                await event.respond(error("Err",str(e)), parse_mode="html")
                ctx.states.clear(uid)
        elif state == STATE_AWAITING_2FA:
            try:
                await st["client"].sign_in(password=raw.strip())
                await on_account_logged_in(event, uid, st["client"], st["phone"])
            except Exception as e:
                await event.respond(error("2FA",str(e)), parse_mode="html")
                ctx.states.clear(uid)
        elif state == STATE_AWAITING_ACCOUNT_PRICE:
            p = validate_amount(raw, min_val=1)
            if p: await finalize_account(uid, p, st, event)
        elif state == STATE_AWAITING_NEW_PRICE:
            p = validate_amount(raw, min_val=1)
            if p and await ctx.repo.set_default_price(p):
                await event.respond(success("OK",f"{p} INR"), buttons=owner_keyboard(), parse_mode="html")
            ctx.states.clear(uid)
        elif state == STATE_AWAITING_ADD_MONEY_CHAT_ID:
            t = validate_user_id(raw)
            if t:
                ctx.states.set(uid, STATE_AWAITING_ADD_MONEY_AMOUNT, target_id=t)
                await event.respond("Amount:", buttons=cancel_button(), parse_mode="html")
        elif state == STATE_AWAITING_ADD_MONEY_AMOUNT:
            a = validate_amount(raw)
            if a:
                await ctx.repo.update_balance(st["target_id"], a)
                await event.respond(success("Added",f"+{a}"), buttons=owner_keyboard(), parse_mode="html")
                ctx.states.clear(uid)
