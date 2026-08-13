_PREFIXES = [
    ("+91","IN","India"),("+1","US","USA"),("+44","GB","UK"),("+49","DE","Germany"),
    ("+33","FR","France"),("+7","RU","Russia"),("+86","CN","China"),("+81","JP","Japan"),
    ("+62","ID","Indonesia"),("+63","PH","Philippines"),("+92","PK","Pakistan"),
    ("+880","BD","Bangladesh"),("+971","AE","UAE"),("+966","SA","Saudi Arabia"),
]

def _flag(iso):
    if not iso or len(iso)!=2: return "🌍"
    return "".join(chr(ord(c)+127397) for c in iso.upper())

def detect_country(phone):
    p = phone.strip().replace(" ","")
    if not p.startswith("+"): p = "+"+p
    for pre, iso, name in sorted(_PREFIXES, key=lambda x:-len(x[0])):
        if p.startswith(pre):
            return iso, name, _flag(iso)
    return "XX","International","🌍"

def blur_phone(phone):
    p = phone.strip()
    if len(p)<=6: return "***"
    return p[:4]+("*"*(len(p)-7))+p[-3:]
