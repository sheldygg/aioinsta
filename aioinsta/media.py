import json

from .types import Media
from .extractors import extract_media_gql, excract_url_code
from .request import RequestClient

class MediaClient(RequestClient):
    async def media_info_graphql(self, shortcode: str) -> dict:
        before_variables = {
            "shortcode": shortcode,
            "child_comment_count": 3,
            "fetch_comment_count": 40,
            "parent_comment_count": 24,
            "has_threaded_comments": False,
        }
        params = {
            "variables": json.dumps(before_variables),
            "query_hash": "477b65a610463740ccdb83135b2014db",
        }
        media_info = await self.public_request(method="GET", params=params)
        return extract_media_gql(media_info["data"]["shortcode_media"])

    async def media_info(self, url: str) -> Media:
        shortcode = excract_url_code(url)
        return await self.media_info_graphql(shortcode)