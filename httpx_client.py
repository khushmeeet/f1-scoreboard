import httpx
import httpx_cache


class HTTPXClient:
    def start(self):
        self.client = httpx.AsyncClient(
            transport=httpx_cache.AsyncCacheControlTransport(
                cache=httpx_cache.FileCache("./cache")
            )
        )

    async def stop(self):
        await self.client.aclose()

    def __call__(self):
        assert self.client is not None
        return self.client
