from dataclasses import dataclass
from telethon import TelegramClient
from bot.config import Settings
from bot.database.connection import Database
from bot.database.repository import Repository
from bot.states.manager import StateManager
from bot.utils.rate_limit import RateLimiter, TaskQueue
from bot.services.otp_listener import OTPListenerService
from bot.services.broadcast import BroadcastService
from bot.services.payment import PaymentService
from bot.services.account_setup import AccountSetupService

@dataclass
class AppContext:
    settings: Settings
    bot: TelegramClient
    db: Database
    repo: Repository
    states: StateManager
    rate_limiter: RateLimiter
    task_queue: TaskQueue
    otp_service: OTPListenerService
    broadcast_service: BroadcastService
    payment_service: PaymentService
    account_setup: AccountSetupService

    @classmethod
    async def create(cls, bot, settings):
        db=Database(settings)
        await db.connect()
        repo=Repository(db)
        states=StateManager()
        await states.start_cleanup_loop()
        q=TaskQueue()
        await q.start()
        return cls(settings=settings,bot=bot,db=db,repo=repo,states=states,
            rate_limiter=RateLimiter(settings.rate_limit_per_minute),task_queue=q,
            otp_service=OTPListenerService(bot,settings,repo),
            broadcast_service=BroadcastService(bot,repo,settings),
            payment_service=PaymentService(bot,settings,repo),
            account_setup=AccountSetupService(settings))

    async def shutdown(self):
        await self.otp_service.stop_all()
        await self.payment_service.stop_all()
        await self.task_queue.shutdown()
        await self.states.stop()
        await self.db.close()
