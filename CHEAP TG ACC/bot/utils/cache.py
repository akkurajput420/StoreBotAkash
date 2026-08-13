import time
from dataclasses import dataclass

@dataclass
class _E:
    value: object
    exp: float

class MemoryCache:
    def __init__(self, ttl=30.0):
        self._b = {}
        self._s = {}
        self.ttl = ttl

    def get_balance(self, uid):
        e = self._b.get(uid)
        return e.value if e and time.monotonic() <= e.exp else None

    def set_balance(self, uid, v):
        self._b[uid] = _E(v, time.monotonic() + self.ttl)

    def invalidate_balance(self, uid):
        self._b.pop(uid, None)

    def get_setting(self, k):
        e = self._s.get(k)
        return e.value if e and time.monotonic() <= e.exp else None

    def set_setting(self, k, v, ttl=60.0):
        self._s[k] = _E(v, time.monotonic() + ttl)

    def invalidate_stock(self):
        pass

cache = MemoryCache()
