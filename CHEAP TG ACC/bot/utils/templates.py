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


def success(title: str, body: str) -> str:
    return f"<b>✅ {title}</b>\n{divider()}\n{body}"


def loading(text: str = "Processing...") -> str:
    return f"<b>⏳ {text}</b>"


def shop_account_label(a) -> str:
    if isinstance(a, dict):
        country = a.get('country', 'Account')
        price = a.get('price', 0)
    else:
        country = getattr(a, 'country', 'Account')
        price = getattr(a, 'price', 0)
    return f"{country} - ₹{price}"


def shop_header(balance: float = 0.0) -> str:
    return (
        f"<b>🛒 ACCOUNT STORE</b>\n{divider()}\n"
        f"💰 <b>Your Balance:</b> ₹{balance:.2f}\n"
        f"👇 <i>Select an account to view details/purchase:</i>"
    )


def account_preview(acc) -> str:
    country = acc.get('country', 'N/A') if isinstance(acc, dict) else getattr(acc, 'country', 'N/A')
    price = acc.get('price', 0) if isinstance(acc, dict) else getattr(acc, 'price', 0)
    age = acc.get('age', 'N/A') if isinstance(acc, dict) else getattr(acc, 'age', 'N/A')
    
    return (
        f"<b>📦 ACCOUNT DETAILS</b>\n{divider()}\n"
        f"🌍 <b>Country:</b> {country}\n"
        f"⏳ <b>Age:</b> {age}\n"
        f"💵 <b>Price:</b> ₹{price:.2f}\n"
        f"{divider()}\n"
        "<i>Click below to confirm your purchase.</i>"
    )


def add_balance_menu(balance: float) -> str:
    return (
        f"<b>💰 RECHARGE WALLET</b>\n{divider()}\n"
        f"Current Balance: <b>₹{balance:.2f}</b>\n\n"
        "Enter amount or choose quick payment option."
    )


def insufficient_balance(price: float, balance: float) -> str:
    shortfall = price - balance
    return (
        f"<b>⚠️ INSUFFICIENT BALANCE</b>\n{divider()}\n"
        f"Item Price: ₹{price:.2f}\n"
        f"Your Balance: ₹{balance:.2f}\n"
        f"Required: <b>₹{shortfall:.2f}</b>\n\n"
        "Please recharge your wallet to proceed."
    )


def purchase_success(acc_id: str, details: str = "") -> str:
    return (
        f"<b>🎉 PURCHASE SUCCESSFUL!</b>\n{divider()}\n"
        f"📦 Order ID: <code>{acc_id}</code>\n"
        f"{details}\n"
        "Thank you for buying with us!"
    )


def stats_panel(users: int = 0, sales: float = 0.0, stock: int = 0) -> str:
    return (
        f"<b>📊 SYSTEM ANALYTICS</b>\n{divider()}\n"
        f"👥 Total Users: <b>{users}</b>\n"
        f"💰 Total Sales: <b>₹{sales:.2f}</b>\n"
        f"📦 Live Stock: <b>{stock}</b>"
    )
