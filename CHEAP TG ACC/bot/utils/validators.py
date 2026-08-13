import re
_PHONE=re.compile(r'^\+?\d{10,15}$')
def validate_phone(phone):
    c=phone.strip().replace(" ","").replace("-","")
    if not _PHONE.match(c): return None
    return c if c.startswith("+") else "+"+c
def validate_user_id(t):
    t=t.strip()
    return int(t) if t.isdigit() and int(t)>0 else None
def validate_amount(t, min_val=0.01, max_val=1e6):
    try:
        v=float(t.strip())
        return round(v,2) if min_val<=v<=max_val else None
    except ValueError:
        return None

def session_path(phone, d):
    import os
    return os.path.join(d, phone.replace("+",""))
