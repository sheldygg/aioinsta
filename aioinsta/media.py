from urllib.parse import urlparse

from aioinsta import login
from aioinsta.extractors import extract_media_gql, extract_media_v1
from aioinsta.idcodec import InstagramIdCodec
from aioinsta.types.media import Media
from aioinsta.exceptions import RateLimit


class MediaClient:
    def __init__(self, login_client: "login.Login"):
        self.login_client = login_client

    @staticmethod
    def media_pk(media_id: str) -> str:
        media_pk = str(media_id)
        if "_" in media_pk:
            media_pk, _ = media_id.split("_")
        return str(media_pk)

    @staticmethod
    def media_code_from_pk(media_pk: str) -> str:
        return InstagramIdCodec.encode(media_pk)

    @staticmethod
    def media_pk_from_code(code: str):
        return InstagramIdCodec.decode(code[:11])

    def media_pk_from_url(self, url: str):
        path = urlparse(url).path
        parts = [p for p in path.split("/") if p]
        return self.media_pk_from_code(parts.pop())

    async def media_info_a1(self, media_pk: str, max_id: str | None = None) -> Media:
        media_pk = self.media_pk(media_pk)
        shortcode = self.media_code_from_pk(media_pk)
        params = {"max_id": max_id} if max_id else None
        response = await self.login_client.public_a1_request(
            method="GET", path=f"/p/{shortcode}", params=params
        )
        # raise RateLimit()
        return extract_media_gql(response.get("shortcode_media"))

    async def media_info_v1(self, media_pk: str) -> Media:
        response = await self.login_client.private_request(
            method="GET",
            path=f"media/{media_pk}/info/",
            raise_for_status=True
        )
        return extract_media_v1(response.get("response").get("items", {}).pop())

    async def media_info(self, media_pk) -> Media:
        try:
            return await self.media_info_a1(media_pk)
        except RateLimit:
            return await self.media_info_v1(media_pk)
