from telethon import Button

def owner_keyboard():
    return [
        [Button.text("➕ Add Account",resize=True), Button.text("📢 Announcement")],
        [Button.text("💰 Add Money"), Button.text("📊 Stats")],
        [Button.text("🔍 Check Fund"), Button.text("🗑️ Delete Fund")],
        [Button.text("🏷️ Change Price"), Button.text("📋 Admin Panel")],
    ]

def user_keyboard():
    return [
        [Button.text("👤 My Account",resize=True), Button.text("🛒 Buy ID")],
        [Button.text("📜 Purchase History"), Button.text("🎟️ Redeem Coupon")],
        [Button.text("💰 Add Balance"), Button.text("🎫 Support")],
        [Button.text("🔄 Refresh Shop")],
    ]

def cancel_button():
    return [Button.text("❌ Cancel Operation", resize=True)]
