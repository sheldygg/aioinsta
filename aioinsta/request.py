import random
import time
from urllib.parse import urljoin

from aiohttp import ClientSession
from aiohttp.client_exceptions import ContentTypeError

from aioinsta import parametrs, login
from aioinsta.enums import ErrorTypes
from aioinsta.exceptions import ChallengeRequired, RateLimit
from aioinsta.helpers import generate_uuid


class PrivateRequestClient:
    def __init__(self, login_client: "login.Login"):
        self.login_client = login_client
        self.session = ClientSession()
        self.last_response = {}

    async def _request(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        params: dict | None = None,
        headers: dict | None = None,
        raise_for_status: bool = False,
    ):
        async with self.session.request(
            method=method,
            url=url,
            data=data,
            params=params,
            headers=headers,
        ) as resp:
            response_headers = resp.headers
            try:
                response = await resp.json()
            except ContentTypeError:
                response = await resp.read()
            self.last_response = response
            if raise_for_status and not resp.ok:
                error_type = response.get("error_type")
                message = response.get("message")
                if resp.status == 400:
                    if error_type == ErrorTypes.RATE_LIMIT_ERROR:
                        raise RateLimit(
                            "Please wait a few minutes before you try again."
                        )
                    elif message == ErrorTypes.CHALLENGE_REQUIRED:
                        raise ChallengeRequired("Challenge Required")
            return dict(response=response, headers=response_headers)

    async def close(self):
        return await self.session.close()

    def set_user_agent(self, user_agent: str | None = None):
        data = dict(self.login_client.device_settings, locale=self.login_client.locale)
        self.login_client.user_agent = user_agent or parametrs.USER_AGENT_BASE.format(
            **data
        )
        self.login_client.settings["user_agent"] = self.login_client.user_agent

    def base_headers(self):
        locale = self.login_client.locale.replace("-", "_")
        accept_language = ["en-US"]
        if locale:
            lang = locale.replace("_", "-")
            if lang not in accept_language:
                accept_language.insert(0, lang)
        headers = {
            "User-Agent": self.login_client.user_agent,
            "Accept-Encoding": "gzip, deflate",
            "Accept": "*/*",
            "Connection": "keep-alive",
            "X-IG-App-Locale": locale,
            "X-IG-Device-Locale": locale,
            "X-IG-Mapped-Locale": locale,
            "X-Pigeon-Session-Id": generate_uuid("UFS-", "-1"),
            "X-Pigeon-Rawclienttime": str(round(time.time(), 3)),
            "X-IG-Bandwidth-Speed-KBPS": str(random.randint(2500000, 3000000) / 1000),
            "X-IG-Bandwidth-TotalBytes-B": str(random.randint(5000000, 90000000)),
            "X-IG-Bandwidth-TotalTime-MS": str(random.randint(2000, 9000)),
            "X-IG-App-Startup-Country": self.login_client.country.upper(),
            "X-Bloks-Version-Id": self.login_client.bloks_versioning_id,
            "X-IG-WWW-Claim": "0",
            "X-Bloks-Is-Layout-RTL": "false",
            "X-Bloks-Is-Panorama-Enabled": "true",
            "X-IG-Device-ID": self.login_client.uuid,
            "X-IG-Family-Device-ID": self.login_client.phone_id,
            "X-IG-Android-ID": self.login_client.android_device_id,
            "X-IG-Timezone-Offset": str(self.login_client.timezone_offset),
            "X-IG-Connection-Type": "WIFI",
            "X-IG-Capabilities": "3brTvx0=",
            "X-IG-App-ID": self.login_client.app_id,
            "Priority": "u=3",
            "Accept-Language": ", ".join(accept_language),
            "X-FB-HTTP-Engine": "Liger",
            "X-FB-Client-IP": "True",
            "X-FB-Server-Cluster": "True",
            "IG-INTENDED-USER-ID": "0",
            "X-IG-Nav-Chain": "9MV:self_profile:2,ProfileMediaTabFragment:self_profile:3,9Xf:self_following:4",
            "X-IG-SALT-IDS": str(random.randint(1061162222, 1061262222)),
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Authorization": self.login_client.authorization_token(),
        }
        if self.login_client.mid:
            headers.update({"X-MID": self.login_client.mid})
        user_id = self.login_client.user_id()
        if user_id:
            next_year = time.time() + 31536000
            headers.update(
                {
                    "IG-U-DS-USER-ID": str(user_id),
                    "IG-U-IG-DIRECT-REGION-HINT": f"LLA,{user_id},{next_year}:01f7bae7d8b131877d8e0ae1493252280d72f6d0d554447cb1dc9049b6b2c507c08605b7",
                    "IG-U-SHBID": f"12695,{user_id},{next_year}:01f778d9c9f7546cf3722578fbf9b85143cd6e5132723e5c93f40f55ca0459c8ef8a0d9f",
                    "IG-U-SHBTS": f"{int(time.time())},{user_id},{next_year}:01f7ace11925d0388080078d0282b75b8059844855da27e23c90a362270fddfb3fae7e28",
                    "IG-U-RUR": f"RVA,{user_id},{next_year}:01f7f627f9ae4ce2874b2e04463efdb184340968b1b006fa88cb4cc69a942a04201e544c",
                }
            )
        if self.login_client.ig_u_rur:
            headers.update({"IG-U-RUR": self.login_client.ig_u_rur})
        if self.login_client.ig_www_claim:
            headers.update({"X-IG-WWW-Claim": self.login_client.ig_www_claim})
        return headers

    async def private_request(
        self,
        method: str,
        path: str,
        data: dict | None = None,
        params: dict | None = None,
        raise_for_status: bool = False,
    ):
        url = urljoin(parametrs.API_DOMAIN + "api/v1/", path)
        try:
            response = await self._request(
                method=method,
                url=url,
                data=data,
                params=params,
                headers=self.base_headers(),
                raise_for_status=raise_for_status,
            )
            self.login_client.mid = response.get("headers", {}).get("ig-set-x-mid")
            return response
        except ChallengeRequired:
            return await self.login_client.resolve_challenge(self.last_response)


class PublicRequestClient:
    def __init__(self, login_client: "login.Login"):
        self.login_client = login_client
        self.session = ClientSession()

    async def public_request(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        params: dict | None = None,
        headers: dict | None = None,
    ):
        async with self.session.request(
            method=method,
            url=url,
            data=data,
            params=params,
            headers=headers,
        ) as resp:
            response_headers = resp.headers
            try:
                response = await resp.json()
            except ContentTypeError:
                response = await resp.read()

            return dict(response=response, headers=response_headers)

    async def public_a1_request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
    ):
        url = urljoin(parametrs.PUBLIC_API_DOMAIN, path)
        params = params or {}
        params.update({"__a": 1, "__d": "dis"})
        response = (await self.public_request(method=method, url=url, params=params)).get("response")
        if response.get("message", "") == "Please wait a few minutes before you try again.":
            raise RateLimit("Please wait a few minutes before you try again.")
        return response.get("graphql", {})
