import asyncio, time
from dataclasses import dataclass, field

@dataclass
class UserState:
    state: str
    data: dict = field(default_factory=dict)
    updated_at: float = field(default_factory=time.monotonic)

class StateManager:
    def __init__(self, ttl=3600):
        self._s = {}
        self.ttl = ttl
        self._task = None

    def get(self, uid):
        u = self._s.get(uid)
        return {"state": u.state, **u.data} if u else {}

    def set(self, uid, state, **data):
        self._s[uid] = UserState(state=state, data=data)

    def clear(self, uid):
        self._s.pop(uid, None)

    def get_state(self, uid):
        u = self._s.get(uid)
        return u.state if u else None

    async def start_cleanup_loop(self):
        async def loop():
            while True:
                await asyncio.sleep(300)
                n = time.monotonic()
                for k in [x for x,u in self._s.items() if n-u.updated_at>self.ttl]:
                    self._s.pop(k, None)
        self._task = asyncio.create_task(loop())

    async def stop(self):
        if self._task:
            self._task.cancel()
