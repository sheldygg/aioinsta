import re
import base64
import json

from aioinsta.challenge import ChallengeClient
from aioinsta.helpers import generate_android_device_id, generate_jazoest, generate_uuid
from aioinsta.media import MediaClient
from aioinsta.password import PasswordClient
from aioinsta.request import PrivateRequestClient, PublicRequestClient
from aioinsta.user import UserClient
from aioinsta.exceptions import IncorrectPassword


class Login(
    PrivateRequestClient,
    PublicRequestClient,
    PasswordClient,
    ChallengeClient,
    UserClient,
    MediaClient,
):
    def __init__(self, settings: dict):
        self.settings: dict = settings
        self.username = None
        self.user_agent = None
        self.authorization_data = {}
        self.device_settings = None
        self.uuid = None
        self.phone_id = None
        self.device_id = None
        self.client_session_id = None
        self.advertising_id = None
        self.android_device_id = None
        self.request_id = None
        self.tray_session_id = None
        self.last_login = None
        self.mid = ""
        self.locale = "en_US"
        self.country = "US"
        self.country_code = 1
        self.timezone_offset: int = -14400
        self.bloks_versioning_id = (
            "ce555e5500576acd8e84a66018f54a05720f2dce29f0bb5a1f97f0c10d6fac48"
        )
        self.ig_u_rur = ""
        self.ig_www_claim = ""
        self.app_id = "567067343352427"
        super().__init__(self)

    def init(self):
        self.set_uuids(self.settings.get("uuids", {}))
        self.locale = self.settings.get("locale", self.locale)
        self.country = self.settings.get("country", self.country)
        self.set_device(self.settings.get("device_settings"))
        self.authorization_data = self.settings.get("authorization_data", {})
        self.mid = self.settings.get("mid")
        self.set_user_agent(self.settings.get("user_agent"))

    def set_uuids(self, uuids: dict = None) -> None:
        self.phone_id = uuids.get("phone_id", generate_uuid())
        self.uuid = uuids.get("uuid", generate_uuid())
        self.client_session_id = uuids.get("client_session_id", generate_uuid())
        self.advertising_id = uuids.get("advertising_id", generate_uuid())
        self.android_device_id = uuids.get(
            "android_device_id", generate_android_device_id()
        )
        self.request_id = uuids.get("request_id", generate_uuid())
        self.tray_session_id = uuids.get("tray_session_id", generate_uuid())
        self.device_id = uuids.get("device_id", generate_uuid())
        self.settings["uuids"] = uuids

    def set_device(self, device: dict = None, reset: bool = False) -> bool:
        self.device_settings = device or {
            "app_version": "269.0.0.18.75",
            "android_version": 26,
            "android_release": "8.0.0",
            "dpi": "480dpi",
            "resolution": "1080x1920",
            "manufacturer": "OnePlus",
            "device": "devitron",
            "model": "6T Dev",
            "cpu": "qcom",
            "version_code": "314665256",
        }
        self.settings["device_settings"] = self.device_settings
        if reset:
            self.set_uuids({})
        return True

    async def sync_launcher(self, login: bool = False):
        data = {
            "id": self.uuid,
            "server_config_retrieval": "1",
        }
        if login is False:
            data["_uuid"] = self.uuid
        return await self.private_request(
            method="POST",
            path="launcher/sync/",
            data=data,
        )

    async def pre_login_flow(self):
        return await self.sync_launcher(True)

    @staticmethod
    def parse_authorization(authorization) -> dict:
        b64part = authorization.rsplit(":", 1)[-1]
        if not b64part:
            return {}
        return json.loads(base64.b64decode(b64part))

    def authorization_token(self) -> str:
        if self.authorization_data:
            b64part = base64.b64encode(
                json.dumps(self.authorization_data).encode()
            ).decode()
            return f"Bearer IGT:2:{b64part}"
        return ""

    def user_id(self) -> int | None:
        user_id = self.authorization_data.get("ds_user_id")
        if user_id:
            return int(user_id)

    async def login_by_session_id(self, session_id: str):
        self.settings["cookies"] = {"sessionid": session_id}
        self.init()
        user_id = re.search(r"^\d+", session_id).group()
        self.authorization_data = {
            "ds_user_id": user_id,
            "sessionid": session_id,
            "should_use_header_over_cookies": True,
        }

    async def login(self, username: str, password: str):
        self.username = username
        await self.pre_login_flow()
        enc_password = await self.password_encrypt(password)
        data = {
            "jazoest": generate_jazoest(self.phone_id),
            "country_codes": json.dumps(
                [{"country_code": str(self.country_code), "source": ["default"]}]
            ),
            "phone_id": self.phone_id,
            "enc_password": enc_password,
            "username": username,
            "adid": self.advertising_id,
            "guid": self.uuid,
            "device_id": self.android_device_id,
            "google_tokens": "[]",
            "login_attempt_count": "0",
        }
        loggin_data = await self.private_request(
            method="POST", path="accounts/login/", data=data, raise_for_status=True
        )
        response = loggin_data.get("response")
        if response.get("status") == "fail" and response.get("error_title") == "Incorrect password":
            raise IncorrectPassword("Entered incorrect password, doblecheck please")
        headers = loggin_data.get("headers")
        self.authorization_data = self.parse_authorization(
            headers.get("ig-set-authorization")
        )

    def get_settings(self) -> dict:
        return {
            "uuids": {
                "phone_id": self.phone_id,
                "uuid": self.uuid,
                "client_session_id": self.client_session_id,
                "advertising_id": self.advertising_id,
                "android_device_id": self.android_device_id,
                "request_id": self.request_id,
                "tray_session_id": self.tray_session_id,
            },
            "mid": self.mid,
            "ig_u_rur": self.ig_u_rur,
            "ig_www_claim": self.ig_www_claim,
            "authorization_data": self.authorization_data,
            "cookies": {},
            "last_login": self.last_login,
            "device_settings": self.device_settings,
            "user_agent": self.user_agent,
            "country": self.country,
            "country_code": self.country_code,
            "locale": self.locale,
            "timezone_offset": self.timezone_offset,
        }
