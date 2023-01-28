from aiohttp import ClientSession
from urllib.parse import urljoin
from .exceptions import InstagramBadRequest


class RequestClient:
    PRIVATE_API_URL = "https://i.instagram.com/api/v1/"
    GRAPHQL_PUBLIC_API_URL = "https://www.instagram.com/graphql/query/"
    private_headers = {}

    async def public_request(
        self,
        method: str = "GET",
        url: str = GRAPHQL_PUBLIC_API_URL,
        data: dict = None,
        params: dict = None,
        headers: dict = None,
    ):
        async with ClientSession() as session:
            async with session.request(
                method=method, url=url, params=params, data=data, headers=headers
            ) as resp:
                response_headers = resp.headers
                content_type = response_headers.get("Content-Type")
                if "application/json;" in content_type:
                    return await resp.json()
                else:
                    return response_headers
    
    error_result = {'message': 'challenge_required', 'challenge': {'url': 'https://i.instagram.com/challenge/?next=/api/v1/users/horoshiiparen/usernameinfo/', 'api_path': '/challenge/', 'hide_webview_header': True, 'lock': True, 'logout': False, 'native_flow': True, 'flow_render_type': 0}, 'status': 'fail'}

    async def private_request(
        self,
        method: str = "POST",
        url: str = None,
        path: str = None,
        data: dict = None,
        params: dict = None,
        headers: dict = None,
    ):
        if not url:
            url = urljoin(self.PRIVATE_API_URL, path)
        async with ClientSession() as session:
            async with session.request(
                method=method,
                url=url,
                data=data,
                params=params,
                headers=self.private_headers,
            ) as resp:
                response_headers = resp.headers
                response: dict = await resp.json()
        if response.get("status") == "fail":
            raise InstagramBadRequest(response["message"])
        mid = response_headers.get("ig-set-x-mid")
        if mid:
            self.mid = mid
        return dict(json=response, headers=response_headers)
