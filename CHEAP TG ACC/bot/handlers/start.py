import logging
from telethon import TelegramClient, events
from bot.handlers import get_ctx
from bot.keyboards.main import owner_keyboard, user_keyboard
from bot.middlewares.admin import is_admin
from bot.middlewares.antiflood import AntiFloodMiddleware
from bot.middlewares.errors import ErrorMiddleware
from bot.utils.templates import welcome_owner, welcome_user

_flood = None

def register(bot, ctx):
    global _flood
    _flood = AntiFloodMiddleware(ctx.rate_limiter)

    @bot.on(events.NewMessage(incoming=True, pattern=r"^/start(?:@\w+)?(?:\s|$)"))
    @ErrorMiddleware.handler
    async def start_handler(event):
        if not await _flood.check(event):
            return
        uid = event.sender_id
        await get_ctx().repo.init_user(uid)
        logging.getLogger("bot").info("/start %s", uid)
        if is_admin(uid):
            await event.respond(welcome_owner(), buttons=owner_keyboard(), parse_mode="html")
        else:
            await event.respond(welcome_user(), buttons=user_keyboard(), parse_mode="html")
