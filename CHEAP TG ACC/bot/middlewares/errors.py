import logging, traceback
from functools import wraps

logger = logging.getLogger("errors")

class ErrorMiddleware:
    @staticmethod
    def handler(func):
        @wraps(func)
        async def wrapper(event, *a, **k):
            try:
                return await func(event, *a, **k)
            except Exception as e:
                logger.error("%s: %s\n%s", func.__name__, e, traceback.format_exc())
                try:
                    await event.respond("<b>❌ Error.</b> Try again.", parse_mode="html")
                except Exception:
                    pass
        return wrapper

    @staticmethod
    def callback(func):
        @wraps(func)
        async def wrapper(event, *a, **k):
            try:
                return await func(event, *a, **k)
            except Exception as e:
                logger.error("%s: %s", func.__name__, e)
                try:
                    await event.answer("Error.", alert=True)
                except Exception:
                    pass
        return wrapper
