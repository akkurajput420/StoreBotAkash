import asyncio
from telethon import TelegramClient
from bot.database.repository import Repository
from bot.config import Settings

class BroadcastService:
    def __init__(self, bot, repo, settings):
        self.bot=bot; self.repo=repo
        self.sem=asyncio.Semaphore(settings.broadcast_workers)

    async def send_bulk(self, messages, progress_callback=None):
        uids=await self.repo.all_user_ids()
        ok=0
        async def one(uid):
            nonlocal ok
            async with self.sem:
                try:
                    for m in messages:
                        await self.bot.send_message(uid,m)
                    await asyncio.sleep(0.05)
                    return True
                except Exception:
                    return False
        for i in range(0,len(uids),50):
            res=await asyncio.gather(*[one(u) for u in uids[i:i+50]])
            ok+=sum(1 for x in res if x)
            if progress_callback:
                await progress_callback(ok,len(uids))
        return ok, len(uids)-ok
