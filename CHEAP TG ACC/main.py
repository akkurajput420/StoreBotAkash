"""Premium Telegram ID Store — entry point."""

from __future__ import annotations

import asyncio
import logging
import sys
import traceback
from pathlib import Path

from telethon import TelegramClient

from bot.config import get_settings
from bot.handlers import register_handlers
from bot.logs import setup_logging
from bot.services.app_context import AppContext
from bot.services.watchdog import Watchdog

logger = logging.getLogger("bot")


async def main() -> None:
    setup_logging()
    settings = get_settings()

    Path(settings.sessions_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.backup_dir).mkdir(parents=True, exist_ok=True)

    session_path = str(settings.project_root / settings.bot_session_name)
    bot = TelegramClient(session_path, settings.api_id, settings.api_hash)

    await bot.connect()
    if not await bot.is_user_authorized():
        await bot.start(bot_token=settings.bot_token)
    else:
        me = await bot.get_me()
        if not getattr(me, "bot", False):
            logger.warning("Re-authenticating as bot (was user session)")
            await bot.log_out()
            await bot.start(bot_token=settings.bot_token)

    me = await bot.get_me()
    logger.info("Logged in as @%s (id=%s, bot=%s)", me.username, me.id, getattr(me, "bot", False))

    ctx = await AppContext.create(bot, settings)
    register_handlers(bot, ctx)
    watchdog = Watchdog(ctx)
    await watchdog.start()

    logger.info("--- Bot v2.0.0 started ---")

    try:
        await bot.run_until_disconnected()
    finally:
        await watchdog.stop()
        await ctx.shutdown()
        await bot.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.getLogger("errors").critical("Fatal: %s\n%s", e, traceback.format_exc())
        sys.exit(1)
