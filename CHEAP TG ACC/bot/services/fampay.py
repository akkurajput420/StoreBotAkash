import httpx
from urllib.parse import urljoin
from bot.config import Settings

class PaymentError(Exception):
    pass

class FamPayClient:
    def __init__(self, settings: Settings):
        b=settings.fampay_api_base_url
        self.base=b if b.endswith("/") else b+"/"

    async def generate_order(self, amount):
        async with httpx.AsyncClient(timeout=30) as c:
            r=await c.get(urljoin(self.base,"generate-order.php"), params={"amount":int(round(amount))})
            r.raise_for_status()
            d=r.json()
        if not d.get("success"):
            raise PaymentError(d.get("msg","Failed"))
        return d

    async def verify_payment(self, order_id, utr=None):
        p={"order_id":order_id}
        if utr: p["utr"]=utr
        async with httpx.AsyncClient(timeout=30) as c:
            r=await c.get(urljoin(self.base,"verify-payment.php"), params=p)
            r.raise_for_status()
            return r.json()
