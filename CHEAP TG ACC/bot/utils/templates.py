from bot.constants import VIP_LEVELS


def divider() -> str:
    return "━━━━━━━━━━━━━━━━━━━━━━"


def welcome_user() -> str:
    bar = divider()
    return (
        f"<b>✨ Welcome to TelegramAcc Seller ✨</b>\n{bar}\n\n"
        "🚀 Premium Telegram Account Marketplace\n"
        "⚡ Instant Delivery System\n"
        "🔐 Safe • Fast • Automated Auto-Pay\n"
        "💎 High Quality Accounts\n\n"
        f"{bar}\n"
        "🔹 <i>Select an option below to proceed.</i>"
    )


def seller_dashboard(total_sales: float, total_orders: int, stock_count: int) -> str:
    return (
        f"<b>🏪 SELLER DASHBOARD</b>\n{divider()}\n"
        f"💰 <b>Total Sales:</b> ₹{total_sales:.2f}\n"
        f"📦 <b>Completed Orders:</b> {total_orders}\n"
        f"📈 <b>Live Stock:</b> {stock_count} Accounts Available\n"
        f"{divider()}\n"
        "<i>Use admin panel options to manage stock & pricing.</i>"
    )


def payment_order(order_id: str, amount: float, upi_id: str, upi_link: str = "", amount_note: str = "") -> str:
    link_html = f'🔗 <a href="{upi_link}"><b>Click Here To Direct Pay</b></a>\n' if upi_link else ""
    return (
        f"<b>💳 AUTO PAYMENT SCANNER</b>\n{divider()}\n"
        f"💵 <b>Paying Amount:</b> <code>₹{amount:.2f}</code>{amount_note}\n"
        f"🧾 <b>Order ID:</b> <code>{order_id}</code>\n"
        f"📲 <b>UPI ID:</b> <code>{upi_id}</code>\n"
        f"{link_html}{divider()}\n"
        "1️⃣ Scan the attached QR Code Image below\n"
        "2️⃣ Pay exact amount (Auto-Set in Scanner)\n"
        "3️⃣ Balance credits automatically upon payment completion!"
    )


def payment_success(amount: float, order_id: str, balance: float) -> str:
    return (
        f"<b>✅ PAYMENT CONFIRMED!</b>\n{divider()}\n"
        f"➕ Credited: <b>+₹{amount:.2f} INR</b>\n"
        f"🧾 Order ID: <code>{order_id}</code>\n"
        f"💰 Current Wallet Balance: <b>₹{balance:.2f} INR</b>"
    )


def error(title: str, body: str) -> str:
    return f"<b>❌ {title}</b>\n{divider()}\n{body}"


# Fix: Missing function added below
def shop_account_label(a: dict | object) -> str:
    if isinstance(a, dict):
        country = a.get('country', 'Account')
        price = a.get('price', 0)
    else:
        country = getattr(a, 'country', 'Account')
        price = getattr(a, 'price', 0)
    return f"{country} - ₹{price}"
