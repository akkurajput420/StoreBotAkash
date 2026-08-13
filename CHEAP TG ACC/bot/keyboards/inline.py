from telethon import Button
from bot.constants import ACCOUNTS_PER_PAGE, ACCOUNT_AGES

# Helper function to generate account label button text
def shop_account_label(a):
    country = a.get('country', 'Account') if isinstance(a, dict) else getattr(a, 'country', 'Account')
    price = a.get('price', 0) if isinstance(a, dict) else getattr(a, 'price', 0)
    return f"{country} - ₹{price}"

def account_list_buttons(accounts, page, has_more, category=""):
    btns = [[Button.inline(shop_account_label(a), f"buy_{a['id']}")] for a in accounts]
    nav = []
    if page > 0: nav.append(Button.inline("⬅️", f"page_{page-1}_{category}"))
    if has_more: nav.append(Button.inline("➡️", f"page_{page+1}_{category}"))
    if nav: btns.append(nav)
    btns.append([Button.inline("🔄 Refresh", f"refresh_shop_{page}_{category}")])
    return btns

def account_age_buttons():
    rows, r = [], []
    for age in ACCOUNT_AGES:
        r.append(Button.inline(age, f"setage_{age}"))
        if len(r) == 3: rows.append(r); r = []
    if r: rows.append(r)
    return rows

def account_preview_buttons(acc_id):
    return [[Button.inline("✅ Confirm & Pay", f"confirm_{acc_id}")],
            [Button.inline("❌ Cancel", b"cancel_buy")]]

def purchased_buttons(acc_id):
    return [[Button.inline("📩 Get OTP", f"getotp_{acc_id}")],
            [Button.inline("🛒 Shop", b"refresh_shop_0_")]]

def insufficient_balance_buttons(acc_id, shortfall):
    amt = int(shortfall) if shortfall == int(shortfall) else int(shortfall) + 1
    return [[Button.inline(f"💰 Add ₹{amt}", f"abl_{amt}_{acc_id}")],
            [Button.inline("« Shop", b"refresh_shop_0_")]]

def admin_panel_buttons():
    return [[Button.inline("📈 Stats", b"admin_analytics")]]

def recharge_approve_buttons(x):
    return [[Button.inline("✅", f"approve_req_{x}")]]
