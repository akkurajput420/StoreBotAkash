from urllib.parse import quote, urljoin
import httpx
from bot.config import Settings


class PaymentError(Exception):
    """Custom Exception for FamPay Payment Errors"""
    pass


class FamPayClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        base_url = settings.fampay_api_base_url.strip()
        # Ensure trailing slash for proper urljoin behavior
        self.base_url = base_url if base_url.endswith("/") else f"{base_url}/"
        # Shared client configuration
        self.timeout = httpx.Timeout(30.0)

    async def _make_request(self, endpoint: str, params: dict) -> dict:
        """Helper method to handle HTTP requests safely."""
        url = urljoin(self.base_url, endpoint)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise PaymentError(f"HTTP Server Error ({e.response.status_code})") from e
        except httpx.RequestError as e:
            raise PaymentError(f"Network Connection Failed: {str(e)}") from e
        except ValueError as e:
            raise PaymentError("Invalid JSON response received from FamPay server.") from e

    async def generate_order(self, amount: float | int) -> dict:
        """Generate a new payment order with auto-generated dynamic QR code."""
        try:
            clean_amount = int(round(float(amount)))
            if clean_amount <= 0:
                raise PaymentError("Amount must be greater than zero.")
        except (ValueError, TypeError) as e:
            raise PaymentError("Invalid amount format provided.") from e

        data = await self._make_request("generate-order.php", params={"amount": clean_amount})

        if not data.get("success"):
            raise PaymentError(data.get("msg", "Failed to generate order."))

        # Extract UPI ID from response or config fallback
        upi_id = data.get("upi_id", self.settings.fampay_upi_id)
        upi_link = f"upi://pay?pa={upi_id}&pn=TgStoreSeller&am={clean_amount}&cu=INR"
        data["upi_link"] = upi_link

        # Dynamic Auto-Pay QR Code generator (If API doesn't return a direct image URL)
        if not data.get("qr_code"):
            encoded_link = quote(upi_link, safe="")
            data["qr_code"] = f"https://api.qrserver.com/v1/create-qr-code/?size=350x350&data={encoded_link}"

        return data

    async def verify_payment(self, order_id: str | int, utr: str = None) -> dict:
        """Verify the status of a payment order."""
        if not order_id:
            raise PaymentError("Order ID is required for verification.")

        params = {"order_id": str(order_id)}
        if utr:
            params["utr"] = str(utr).strip()

        return await self._make_request("verify-payment.php", params=params)
