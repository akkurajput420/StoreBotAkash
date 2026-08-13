import re
def highlight_otp(text):
    m=re.search(r"\b(\d{5,6})\b", text)
    if not m: return text, None
    c=m.group(1)
    return text.replace(c,f"<b><code>{c}</code></b>",1), c

def otp_message(phone, text, highlighted=None):
    from bot.utils.templates import divider
    body=highlighted or text
    return f"<b>📩 OTP</b>\n{divider()}\n📱 <code>{phone}</code>\n\n{body}"
