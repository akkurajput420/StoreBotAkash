from bot.constants import VIP_LEVELS

def divider():
    return "━━━━━━━━━━━━━━━━━━━━━━"

def welcome_user():
    bar = divider()
    return (
        f"<b>✨ Welcome to TelegramAcc Seller ✨</b>\n{bar}\n\n"
        "🚀 Premium Telegram Account Marketplace\n"
        "⚡ Instant Delivery System\n"
        "🔐 Safe • Fast • Automated\n"
        "📩 Auto OTP Forwarding\n"
        "💎 High Quality Accounts\n\n"
        f"{bar}\n"
        "🛒 Buy Accounts in One Click\n"
        "💰 Secure Wallet System\n"
        "🔥 Smooth & Fast Experience\n"
        f"{bar}\n\n"
        "🔹 <i>Use the buttons below to continue.</i>"
    )

def welcome_owner():
    return f"<b>👋 Admin Dashboard</b>\n{divider()}\nReady."

def loading(t="Processing"):
    return f"<b>{t}</b>\n{divider()}\n<code>◐ ◓ ◑ ◒</code>"

def success(t,b): return f"<b>✅ {t}</b>\n{divider()}\n{b}"
def error(t,b): return f"<b>❌ {t}</b>\n{divider()}\n{b}"
def warn(t,b): return f"<b>⚠️ {t}</b>\n{divider()}\n{b}"

def vip_rank(bal):
    r=VIP_LEVELS[0][1]
    for th,n in VIP_LEVELS:
        if bal>=th: r=n
    return r

def account_dashboard(uid,bal,vip,n):
    return (f"<b>👤 Account</b>\n{divider()}\n"
            f"🆔 <code>{uid}</code>\n💰 <b>{bal:.2f} INR</b>\n🏅 {vip}\n🛒 {n} purchases")

def shop_header(stock,page):
    return f"<b>🛒 Available Accounts</b>\n{divider()}\n📦 <code>{stock}</code> | Page {page+1}"

def shop_account_label(acc):
    from bot.utils.country import _flag
    f=_flag(acc.get("country_code","XX"))
    return f"{f} {acc.get('country_name','?')} • {acc.get('account_age','—')} — ₹{float(acc['price']):.0f}"

def account_preview(acc, blurred):
    from bot.utils.country import _flag
    f=_flag(acc.get("country_code","XX"))
    spam="✅ Spam Free" if acc.get("spam_free") in (1,True) else "⚠️ Limits may apply"
    return (f"<b>📋 Preview</b>\n{divider()}\n"
            f"🌍 {f} {acc.get('country_name')}\n📅 {acc.get('account_age')}\n"
            f"📱 <code>{blurred}</code>\n🛡️ {spam}\n💵 <b>{float(acc['price']):.2f} INR</b>\n"
            f"{divider()}\n<i>Confirm to pay & reveal number.</i>")

def purchase_success(phone, acc=None):
    extra=""
    if acc:
        from bot.utils.country import _flag
        extra=f"\n🌍 {_flag(acc.get('country_code'))} {acc.get('country_name')}"
    return (f"<b>🎉 Purchased!</b>\n{divider()}\n📱 <code>{phone}</code>{extra}\n"
            "Tap <b>Get OTP</b> for codes.")

def insufficient_balance(bal, price, short):
    return (f"<b>❌ Low Balance</b>\n{divider()}\n💰 {bal:.2f} | Need {price:.2f}\n"
            f"📉 Add <b>{short:.2f} INR</b> more")

def add_balance_menu(bal):
    return f"<b>💰 Add Balance</b>\n{divider()}\nBalance: <code>{bal:.2f} INR</code>\nSelect amount:"

def payment_order(order_id, amount, upi_id, upi_link, amount_note=""):
    link=f'<a href="{upi_link}">Open UPI App</a>\n' if upi_link else ""
    return (f"<b>💳 UPI Payment</b>\n{divider()}\n"
            f"💵 <b>{amount:.2f} INR</b>{amount_note}\n🧾 <code>{order_id}</code>\n"
            f"📲 <code>{upi_id}</code>\n{link}{divider()}\n"
            "1️⃣ Scan QR below\n2️⃣ Pay exact via any UPI app\n3️⃣ Tap <b>I've Paid — Check</b>")

def payment_success(amount, order_id, balance, paid_by=""):
    return f"<b>✅ Paid!</b>\n+{amount:.2f} INR\nBalance: <b>{balance:.2f}</b>"

def stats_panel(u,s,e,d):
    return f"<b>📊 Stats</b>\n{divider()}\n👥 {u}\n📦 {s}"
