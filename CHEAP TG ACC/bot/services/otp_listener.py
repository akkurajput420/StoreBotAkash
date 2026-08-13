import asyncio, logging
from telethon import TelegramClient, events
from bot.constants import TELEGRAM_OTP_USER_ID
from bot.utils.security import session_path as sp
from bot.utils.otp_extractor import highlight_otp, otp_message

logger = logging.getLogger("bot")

class OTPListenerService:
    def __init__(self, bot, settings, repo):
        self.bot=bot; self.settings=settings; self.repo=repo
        self._tasks={}

    async def start_forwarding(self, phone, user_id):
        if phone in self._tasks and not self._tasks[phone].done():
            return
        self._tasks[phone]=asyncio.create_task(self._run(phone,user_id))

    async def _run(self, phone, user_id):
        path=sp(phone, self.settings.sessions_dir)
        client=TelegramClient(path, self.settings.api_id, self.settings.api_hash)
        try:
            await client.connect()
            if not await client.is_user_authorized():
                return
            @client.on(events.NewMessage(from_users=TELEGRAM_OTP_USER_ID))
            async def h(ev):
                t=ev.raw_text or ""
                ht,code=highlight_otp(t)
                await self.bot.send_message(user_id, otp_message(phone,t,ht), parse_mode="html")
            await asyncio.sleep(self.settings.otp_listener_timeout)
        except Exception as e:
            logger.error("otp %s: %s", phone, e)
        finally:
            await client.disconnect()
            self._tasks.pop(phone,None)

    async def stop_all(self):
        for t in list(self._tasks.values()):
            t.cancel()
