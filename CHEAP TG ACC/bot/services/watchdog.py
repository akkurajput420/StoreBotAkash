import asyncio, logging

class Watchdog:
    def __init__(self, ctx):
        self.ctx=ctx; self._t=None
    async def start(self):
        self._t=asyncio.create_task(self._loop())
    async def _loop(self):
        while True:
            await asyncio.sleep(300)
    async def stop(self):
        if self._t: self._t.cancel()
