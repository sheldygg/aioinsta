from aiohttp import ClientSession

class RequestClient:
    
    GRAPHQL_PUBLIC_API_URL = "https://www.instagram.com/graphql/query/"
    
    async def public_request(
        self,
        method: str = "GET",
        url: str = GRAPHQL_PUBLIC_API_URL,
        data: dict = None,
        params: dict = None,
        headers: dict = None
    ):
        async with ClientSession() as session:
            async with session.request(method=method, url=url, params=params, data=data, headers=headers) as resp:
                response = await resp.json()
        return response