from bot.services.app_context import AppContext

_ctx = None

def set_ctx(ctx):
    global _ctx
    _ctx = ctx

def get_ctx():
    if _ctx is None:
        raise RuntimeError("AppContext not initialized")
    return _ctx

def register_handlers(bot, ctx):
    set_ctx(ctx)
    from bot.handlers import callbacks, owner, start, user
    start.register(bot, ctx)
    owner.register(bot, ctx)
    user.register(bot, ctx)
    callbacks.register(bot, ctx)
