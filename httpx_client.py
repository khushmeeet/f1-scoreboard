import httpx
import httpx_cache


class HTTPXClient:
    def start(self):
        self.client = httpx.AsyncClient(
            transport=httpx_cache.CacheControlTransport(cache=httpx_cache.DictCache())
        )

    async def stop(self):
        await self.client.aclose()

    def __call__(self):
        assert self.client is not None
        return self.client
