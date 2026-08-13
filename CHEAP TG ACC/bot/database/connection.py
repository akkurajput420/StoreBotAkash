import asyncio, logging, shutil
from datetime import datetime, timezone
from pathlib import Path
import aiosqlite
from bot.config import get_settings

logger = logging.getLogger("bot")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0.0, is_owner INTEGER DEFAULT 0,
    favorites TEXT DEFAULT '[]', created_at TEXT, last_active TEXT);
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT UNIQUE, price REAL, status TEXT DEFAULT 'available',
    country_code TEXT DEFAULT 'XX', country_name TEXT DEFAULT 'Unknown', account_age TEXT DEFAULT 'FRESH',
    spam_free INTEGER DEFAULT 0, spam_note TEXT DEFAULT '', created_at TEXT);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS purchase_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, account_id INTEGER, phone TEXT, price REAL, created_at TEXT);
CREATE TABLE IF NOT EXISTS payment_orders (
    order_id TEXT PRIMARY KEY, user_id INTEGER, amount REAL, status TEXT DEFAULT 'pending',
    credited INTEGER DEFAULT 0, pending_acc_id INTEGER, created_at TEXT);
CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts(status);
"""

class Database:
    def __init__(self, settings=None):
        self.settings = settings or get_settings()
        self._conn = None
        self._lock = asyncio.Lock()

    async def connect(self):
        path = self.settings.sqlite_path
        self._conn = await aiosqlite.connect(path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(SCHEMA)
        await self._conn.execute("INSERT OR IGNORE INTO settings VALUES ('default_price','100.0')")
        await self._migrate()
        await self._conn.commit()
        logger.info("DB: %s", path)

    async def _migrate(self):
        c = await self._conn.execute("PRAGMA table_info(accounts)")
        cols = {r[1] for r in await c.fetchall()}
        for n, t in [("country_code","TEXT"),("country_name","TEXT"),("account_age","TEXT DEFAULT 'FRESH'"),
                     ("spam_free","INTEGER DEFAULT 0"),("spam_note","TEXT")]:
            if n not in cols:
                await self._conn.execute(f"ALTER TABLE accounts ADD COLUMN {n} {t}")

    async def execute(self, sql, params=(), fetch=None):
        async with self._lock:
            cur = await self._conn.execute(sql, params)
            if fetch == "one":
                return await cur.fetchone()
            if fetch == "all":
                return await cur.fetchall()
            if fetch == "val":
                r = await cur.fetchone()
                return r[0] if r else None
            await self._conn.commit()
            return cur

    async def transaction(self):
        return _Tx(self)

    async def close(self):
        if self._conn:
            await self._conn.close()

class _Tx:
    def __init__(self, db): self.db = db
    async def __aenter__(self):
        await self.db._conn.execute("BEGIN")
        return self.db
    async def __aexit__(self, *a):
        if a[0]:
            await self.db._conn.execute("ROLLBACK")
        else:
            await self.db._conn.commit()
