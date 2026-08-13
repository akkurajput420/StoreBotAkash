import json, logging
from datetime import datetime, timezone
from bot.constants import STATUS_AVAILABLE, STATUS_SOLD
from bot.database.connection import Database
from bot.utils.cache import cache
from bot.config import get_settings

logger = logging.getLogger("bot")

class Repository:
    def __init__(self, db: Database):
        self.db = db
        self.settings = get_settings()

    async def init_user(self, uid):
        o = 1 if uid == self.settings.owner_id else 0
        await self.db.execute("INSERT OR IGNORE INTO users (user_id,balance,is_owner) VALUES (?,0,?)", (uid,o))
        await self.db.execute("UPDATE users SET last_active=? WHERE user_id=?", (self._now(), uid))

    async def get_balance(self, uid):
        c = cache.get_balance(uid)
        if c is not None: return c
        r = await self.db.execute("SELECT balance FROM users WHERE user_id=?", (uid,), fetch="one")
        b = float(r["balance"]) if r else 0.0
        cache.set_balance(uid, b)
        return b

    async def update_balance(self, uid, delta):
        await self.db.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (delta, uid))
        cache.invalidate_balance(uid)
        return True

    async def get_default_price(self):
        r = await self.db.execute("SELECT value FROM settings WHERE key='default_price'", fetch="one")
        return float(r["value"]) if r else 100.0

    async def set_default_price(self, p):
        await self.db.execute("INSERT OR REPLACE INTO settings VALUES ('default_price',?)", (str(p),))
        return True

    async def get_stats(self):
        u = await self.db.execute("SELECT COUNT(*) FROM users", fetch="val") or 0
        s = await self.db.execute("SELECT COUNT(*) FROM accounts WHERE status=?", (STATUS_AVAILABLE,), fetch="val") or 0
        return int(u), int(s), 0.0

    async def get_daily_earnings(self):
        return 0.0

    async def list_available_accounts(self, limit=5, offset=0, category=None):
        rows = await self.db.execute(
            "SELECT * FROM accounts WHERE status=? ORDER BY id LIMIT ? OFFSET ?",
            (STATUS_AVAILABLE, limit, offset), fetch="all")
        return [dict(r) for r in rows or []]

    async def count_available(self, category=None):
        return int(await self.db.execute(
            "SELECT COUNT(*) FROM accounts WHERE status=?", (STATUS_AVAILABLE,), fetch="val") or 0)

    async def get_account(self, aid):
        r = await self.db.execute("SELECT * FROM accounts WHERE id=?", (aid,), fetch="one")
        return dict(r) if r else None

    async def add_account(self, phone, price, *, country_code="XX", country_name="Unknown",
                          account_age="FRESH", spam_free=False, spam_note=""):
        await self.db.execute(
            """INSERT OR REPLACE INTO accounts
               (phone,price,status,country_code,country_name,account_age,spam_free,spam_note)
               VALUES (?,?,?,?,?,?,?,?)""",
            (phone, price, STATUS_AVAILABLE, country_code, country_name, account_age,
             1 if spam_free else 0, spam_note[:500]))
        cache.invalidate_stock()
        return True

    async def purchase_account(self, uid, aid):
        acc = await self.get_account(aid)
        if not acc or acc["status"] != STATUS_AVAILABLE:
            return False, None, "unavailable"
        price = float(acc["price"])
        if await self.get_balance(uid) < price:
            return False, None, "insufficient_funds"
        try:
            async with await self.db.transaction():
                await self.db.execute("UPDATE users SET balance=balance-? WHERE user_id=?", (price, uid))
                await self.db.execute("UPDATE accounts SET status=? WHERE id=?", (STATUS_SOLD, aid))
                await self.db.execute(
                    "INSERT INTO purchase_logs (user_id,account_id,phone,price,created_at) VALUES (?,?,?,?,?)",
                    (uid, aid, acc["phone"], price, self._now()))
            cache.invalidate_balance(uid)
            return True, acc, "ok"
        except Exception as e:
            logger.error("purchase: %s", e)
            return False, None, "error"

    async def get_purchase_history(self, uid, limit=10):
        rows = await self.db.execute(
            "SELECT * FROM purchase_logs WHERE user_id=? ORDER BY id DESC LIMIT ?", (uid, limit), fetch="all")
        return [dict(r) for r in rows or []]

    async def get_top_buyers(self, limit=10):
        return []

    async def all_user_ids(self):
        rows = await self.db.execute("SELECT user_id FROM users", fetch="all")
        return [int(r["user_id"]) for r in rows or []]

    async def redeem_coupon(self, uid, code):
        return False, "No coupons", 0.0

    async def create_payment_order(self, order_id, uid, amount, pending_acc_id=None):
        await self.db.execute(
            "INSERT OR REPLACE INTO payment_orders (order_id,user_id,amount,pending_acc_id) VALUES (?,?,?,?)",
            (order_id, uid, amount, pending_acc_id))

    async def get_payment_order(self, oid):
        r = await self.db.execute("SELECT * FROM payment_orders WHERE order_id=?", (oid,), fetch="one")
        return dict(r) if r else None

    async def credit_payment_order(self, order_id, transaction_id=None, utr=None):
        row = await self.get_payment_order(order_id)
        if not row or row.get("credited"):
            return False
        await self.update_balance(int(row["user_id"]), float(row["amount"]))
        await self.db.execute(
            "UPDATE payment_orders SET credited=1,status='paid' WHERE order_id=?", (order_id,))
        return True

    async def update_payment_status(self, oid, st):
        await self.db.execute("UPDATE payment_orders SET status=? WHERE order_id=?", (st, oid))

    async def pending_recharges(self):
        return []

    async def approve_recharge(self, x):
        return False

    async def log_activity(self, uid, action, details=None):
        pass

    async def log_failed_purchase(self, uid, aid, reason):
        pass

    async def add_favorite(self, uid, aid):
        pass

    async def get_user_profile(self, uid):
        r = await self.db.execute("SELECT * FROM users WHERE user_id=?", (uid,), fetch="one")
        return dict(r) if r else {"user_id": uid, "balance": 0}

    async def export_users_csv(self):
        return "user_id,balance\n"

    async def export_accounts_csv(self):
        return "id,phone,price\n"

    async def create_coupon(self, *a, **k):
        pass

    def _now(self):
        return datetime.now(timezone.utc).isoformat()
