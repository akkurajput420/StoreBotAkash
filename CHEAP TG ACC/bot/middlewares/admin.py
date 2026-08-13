from bot.config import get_settings

def is_admin(user_id: int) -> bool:
    return user_id == get_settings().owner_id
