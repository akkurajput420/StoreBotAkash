from bot.utils.rate_limit import RateLimiter
from telethon import events

class AntiFloodMiddleware:
    def __init__(self, limiter: RateLimiter):
        self.limiter = limiter

    async def check(self, event: events.NewMessage.Event) -> bool:
        if self.limiter.is_allowed(event.sender_id):
            return True
        await event.respond("<b>⚠️ Slow down!</b>", parse_mode="html")
        return False
