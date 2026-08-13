from telethon import TelegramClient, events
from bot.constants import STATE_AWAITING_ACCOUNT_AGE, STATE_AWAITING_ACCOUNT_PRICE
from bot.handlers import get_ctx
from bot.keyboards.inline import account_age_buttons
from bot.keyboards.main import owner_keyboard
from bot.utils.country import detect_country
from bot.utils.templates import loading, success, error
from bot.utils import templates as tpl

async def on_account_logged_in(event, owner_id, client, phone):
    ctx = get_ctx()
    iso, name, flag = detect_country(phone)
    p = await event.respond(loading("Auto setup"), parse_mode="html")
    setup = await ctx.account_setup.setup_account(client)
    spam = "✅ Spam Free" if setup["spam_free"] else "⚠️ Limits may apply"
    await p.edit(
        f"<b>✅ Logged in</b>\n{tpl.divider()}\n"
        f"🌍 {flag} <b>{name}</b>\n📱 <code>{phone}</code>\n{spam}\n\n<b>Select age:</b>",
        buttons=account_age_buttons(), parse_mode="html")
    ctx.states.set(owner_id, STATE_AWAITING_ACCOUNT_AGE, phone=phone, client=client,
        country_code=iso, country_name=name, country_flag=flag,
        spam_free=setup["spam_free"], spam_note=setup.get("spam_note",""))

async def finalize_account(owner_id, price, st, event):
    ctx = get_ctx()
    ok = await ctx.repo.add_account(st["phone"], price,
        country_code=st.get("country_code","XX"), country_name=st.get("country_name","?"),
        account_age=st.get("account_age","FRESH"), spam_free=bool(st.get("spam_free")),
        spam_note=st.get("spam_note",""))
    c = st.get("client")
    if c:
        try: await c.disconnect()
        except Exception: pass
    ctx.states.clear(owner_id)
    if ok:
        await event.respond(success("Listed", f"{st.get('country_flag')} {st.get('country_name')} • ₹{price}"),
            buttons=owner_keyboard(), parse_mode="html")
    else:
        await event.respond(error("Failed","DB error"), buttons=owner_keyboard(), parse_mode="html")

async def disconnect_stored_client(owner_id):
    c = get_ctx().states.get(owner_id).get("client")
    if c:
        try: await c.disconnect()
        except Exception: pass
