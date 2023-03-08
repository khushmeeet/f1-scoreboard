import httpx


class HTTPXClient:
    def start(self):
        self.client = httpx.AsyncClient()

    async def stop(self):
        await self.client.aclose()

    def __call__(self):
        assert self.client is not None
        return self.client
