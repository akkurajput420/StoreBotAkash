import time
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self, max_per_minute=30):
        self.max_per_minute = max_per_minute
        self._hits = defaultdict(deque)

    def is_allowed(self, user_id: int) -> bool:
        now = time.monotonic()
        q = self._hits[user_id]
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= self.max_per_minute:
            return False
        q.append(now)
        return True

class TaskQueue:
    def __init__(self, workers=3):
        import asyncio
        self._queue = asyncio.Queue()
        self._tasks = []

    async def start(self):
        import asyncio
        for _ in range(3):
            self._tasks.append(asyncio.create_task(self._worker()))

    async def _worker(self):
        import asyncio
        while True:
            coro = await self._queue.get()
            try:
                if asyncio.iscoroutine(coro):
                    await coro
                elif callable(coro):
                    r = coro()
                    if asyncio.iscoroutine(r):
                        await r
            except Exception:
                pass
            self._queue.task_done()

    def enqueue(self, coro):
        self._queue.put_nowait(coro)

    async def shutdown(self):
        for t in self._tasks:
            t.cancel()
