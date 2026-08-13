from bot.config import get_settings

# Yahan par baki admins ki Telegram User IDs add kar dein
EXTRA_ADMIN_IDS = [987654321, 1122334455] 

def is_admin(user_id: int) -> bool:
    settings = get_settings()
    
    # Owner ID + Extra Admins dono allow honge
    allowed_admins = {settings.owner_id, *EXTRA_ADMIN_IDS}
    return user_id in allowed_admins
