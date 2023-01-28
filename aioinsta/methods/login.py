import base64
import time
import hashlib
import json
import random
import uuid

from Cryptodome.Cipher import AES, PKCS1_v1_5
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes

from ..request import RequestClient
from ..utils import generate_jazoest
from .. import config


class LoginClient(RequestClient):
    settings = {}

    username = None
    password = None
    authorization = ""
    authorization_data = {}
    last_login = None
    relogin_attempt = 0
    device_settings = {}
    client_session_id = ""
    tray_session_id = ""
    advertising_id = ""
    android_device_id = ""
    request_id = ""
    phone_id = ""
    app_id = "567067343352427"
    uuid = ""
    mid = ""
    country = "US"
    country_code = 1
    locale = "en_US"
    timezone_offset: int = -14400
    ig_u_rur = ""
    ig_www_claim = ""

    def before_start(self):
        self.authorization_data = self.settings.get("authorization_data", {})
        self.last_login = self.settings.get("last_login")
        self.set_timezone_offset(
            self.settings.get("timezone_offset", self.timezone_offset)
        )
        self.set_device(self.settings.get("device_settings"))
        self.bloks_versioning_id = hashlib.sha256(
            json.dumps(self.device_settings).encode()
        ).hexdigest()
        self.set_user_agent(self.settings.get("user_agent"))
        self.set_uuids(self.settings.get("uuids", {}))
        self.set_locale(self.settings.get("locale", self.locale))
        self.set_country(self.settings.get("country", self.country))
        self.set_country_code(self.settings.get("country_code", self.country_code))
        self.mid = self.settings.get("mid", {})
        self.set_ig_u_rur(self.settings.get("ig_u_rur"))
        self.set_ig_www_claim(self.settings.get("ig_www_claim"))
        headers = self.base_headers
        bearer = self.get_bearer_authorization()
        if bearer:
            headers.update({
                "Authorization": bearer
            })
        self.private_headers.update(headers)

    @property
    def base_headers(self):
        locale = self.locale.replace("-", "_")
        accept_language = ["en-US"]
        if locale:
            lang = locale.replace("_", "-")
            if lang not in accept_language:
                accept_language.insert(0, lang)
        headers = {
            "X-IG-App-Locale": locale,
            "X-IG-Device-Locale": locale,
            "X-IG-Mapped-Locale": locale,
            "X-Pigeon-Session-Id": self.generate_uuid("UFS-", "-1"),
            "X-Pigeon-Rawclienttime": str(round(time.time(), 3)),
            "X-IG-Bandwidth-Speed-KBPS": str(
                random.randint(2500000, 3000000) / 1000
            ),
            "X-IG-Bandwidth-TotalBytes-B": str(
                random.randint(5000000, 90000000)
            ),
            "X-IG-Bandwidth-TotalTime-MS": str(random.randint(2000, 9000)),
            "X-IG-App-Startup-Country": self.country.upper(),
            "X-Bloks-Version-Id": self.bloks_versioning_id,
            "X-IG-WWW-Claim": "0",
            "X-Bloks-Is-Layout-RTL": "false",
            "X-Bloks-Is-Panorama-Enabled": "true",
            "X-IG-Device-ID": self.uuid,
            "X-IG-Family-Device-ID": self.phone_id,
            "X-IG-Android-ID": self.android_device_id,
            "X-IG-Timezone-Offset": str(self.timezone_offset),
            "X-IG-Connection-Type": "WIFI",
            "X-IG-Capabilities": "3brTvx0=",  # "3brTvwE=" in instabot
            "X-IG-App-ID": self.app_id,
            "Priority": "u=3",
            "User-Agent": self.user_agent,
            "Accept-Language": ", ".join(accept_language),
            "X-MID": self.mid or "",
            "Accept-Encoding": "gzip, deflate",  # ignore zstd
            "Host": config.API_DOMAIN,
            "X-FB-HTTP-Engine": "Liger",
            "Connection": "keep-alive",
            "X-FB-Client-IP": "True",
            "X-FB-Server-Cluster": "True",
            "IG-INTENDED-USER-ID": str(0),
            "X-IG-Nav-Chain": "9MV:self_profile:2,ProfileMediaTabFragment:self_profile:3,9Xf:self_following:4",
            "X-IG-SALT-IDS": str(random.randint(1061162222, 1061262222)),
        }
        user_id = self.get_user_id_from_auth()
        if user_id:
            next_year = time.time() + 31536000
            headers.update({
                "IG-U-DS-USER-ID": str(user_id),
                "IG-U-IG-DIRECT-REGION-HINT": f"LLA,{user_id},{next_year}:01f7bae7d8b131877d8e0ae1493252280d72f6d0d554447cb1dc9049b6b2c507c08605b7",
                "IG-U-SHBID": f"12695,{user_id},{next_year}:01f778d9c9f7546cf3722578fbf9b85143cd6e5132723e5c93f40f55ca0459c8ef8a0d9f",
                "IG-U-SHBTS": f"{int(time.time())},{user_id},{next_year}:01f7ace11925d0388080078d0282b75b8059844855da27e23c90a362270fddfb3fae7e28",
                "IG-U-RUR": f"RVA,{user_id},{next_year}:01f7f627f9ae4ce2874b2e04463efdb184340968b1b006fa88cb4cc69a942a04201e544c",
            })
        bearer = self.get_bearer_authorization()
        if bearer:
            headers.update({
                "Authorization": bearer
            })
        if self.ig_u_rur:
            headers.update({"IG-U-RUR": self.ig_u_rur})
        if self.ig_www_claim:
            headers.update({"X-IG-WWW-Claim": self.ig_www_claim})
        self.private_headers.update(headers)
        return headers
    
    def get_user_id_from_auth(self):
        user_id = self.authorization_data.get("ds_user_id")
        if user_id:
            return user_id
        return None

    def generate_uuid(self, prefix: str = "", suffix: str = "") -> str:
        """
        Helper to generate uuids

        Returns
        -------
        str
            A stringified UUID
        """
        return f"{prefix}{uuid.uuid4()}{suffix}"

    def set_ig_u_rur(self, value):
        self.settings["ig_u_rur"] = self.ig_u_rur = value
        return True

    def set_ig_www_claim(self, value):
        self.settings["ig_www_claim"] = self.ig_www_claim = value
        return True

    def generate_android_device_id(self) -> str:
        """
        Helper to generate Android Device ID

        Returns
        -------
        str
            A random android device id
        """
        return "android-%s" % hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]

    def set_country_code(self, country_code: int = 1):
        """Set country calling code

        Parameters
        ----------
        country_code: int

        Returns
        -------
        bool
            A boolean value
        """
        self.settings["country_code"] = self.country_code = int(country_code)
        return True

    def set_locale(self, locale: str = "en_US"):
        """Set you locale (ISO 3166-1/3166-2)

        Parameters
        ----------
        locale: str
            Your locale code (ISO 3166-1/3166-2) string identifier (e.g. US, UK, RU)
            Advise to specify the locale code of your proxy

        Returns
        -------
        bool
            A boolean value
        """
        user_agent = (self.settings.get("user_agent") or "").replace(
            self.locale, locale
        )
        self.settings["locale"] = self.locale = str(locale)
        self.set_user_agent(user_agent)  # update locale in user_agent
        if "_" in locale:
            self.set_country(locale.rsplit("_", 1)[1])
        return True

    def set_country(self, country: str = "US"):
        """Set you country code (ISO 3166-1/3166-2)

        Parameters
        ----------
        country: str
            Your country code (ISO 3166-1/3166-2) string identifier (e.g. US, UK, RU)
            Advise to specify the country code of your proxy

        Returns
        -------
        bool
            A boolean value
        """
        self.settings["country"] = self.country = str(country)
        return True

    def set_timezone_offset(self, seconds: int = 0):
        """Set you timezone offset in seconds

        Parameters
        ----------
        seconds: int
            Specify the offset in seconds from UTC

        Returns
        -------
        bool
            A boolean value
        """
        self.settings["timezone_offset"] = self.timezone_offset = int(seconds)
        return True

    def set_device(self, device: dict = None, reset: bool = False) -> bool:
        """
        Helper to set a device for login

        Parameters
        ----------
        device: Dict, optional
            Dict of device settings, default is None

        Returns
        -------
        bool
            A boolean value
        """
        self.device_settings = device or {
            "app_version": "203.0.0.29.118",
            "android_version": 26,
            "android_release": "8.0.0",
            "dpi": "480dpi",
            "resolution": "1080x1920",
            "manufacturer": "Xiaomi",
            "device": "capricorn",
            "model": "MI 5s",
            "cpu": "qcom",
            "version_code": "314665256",
        }
        self.settings["device_settings"] = self.device_settings
        if reset:
            self.set_uuids({})
            # self.settings = self.get_settings()
        return True

    def set_user_agent(self, user_agent: str = "", reset: bool = False) -> bool:
        """
        Helper to set user agent

        Parameters
        ----------
        user_agent: str, optional
            User agent, default is ""

        Returns
        -------
        bool
            A boolean value
        """
        data = dict(self.device_settings, locale=self.locale)
        self.user_agent = user_agent or config.USER_AGENT_BASE.format(**data)
        # self.private.headers.update({"User-Agent": self.user_agent})  # changed in base_headers
        self.settings["user_agent"] = self.user_agent
        if reset:
            self.set_uuids({})
            # self.settings = self.get_settings()
        return True

    def set_uuids(self, uuids: dict = None) -> bool:
        """
        Helper to set uuids

        Parameters
        ----------
        uuids: Dict, optional
            UUIDs, default is None

        Returns
        -------
        bool
            A boolean value
        """
        self.phone_id = uuids.get("phone_id", self.generate_uuid())
        self.uuid = uuids.get("uuid", self.generate_uuid())
        self.client_session_id = uuids.get("client_session_id", self.generate_uuid())
        self.advertising_id = uuids.get("advertising_id", self.generate_uuid())
        self.android_device_id = uuids.get(
            "android_device_id", self.generate_android_device_id()
        )
        self.request_id = uuids.get("request_id", self.generate_uuid())
        self.tray_session_id = uuids.get("tray_session_id", self.generate_uuid())
        # self.device_id = uuids.get("device_id", self.generate_uuid())
        self.settings["uuids"] = uuids
        return True

    async def sync_launcher(self, login: bool = False) -> dict:
        """
        Sync Launcher

        Parameters
        ----------
        login: bool, optional
            Whether to login or not

        Returns
        -------
        Dict
            A dictionary of response from the call
        """
        data = {
            "id": self.uuid,
            "server_config_retrieval": "1",
        }
        if login is False:
            data["_uid"] = self.user_id
            data["_uuid"] = self.uuid
            data["_csrftoken"] = self.token
        return await self.private_request(path="launcher/sync/", data=data)

    async def set_contact_point_prefill(self, usage: str = "prefill") -> dict:
        """
        Sync Launcher

        Parameters
        ----------
        usage: str, optional
            Default "prefill"

        Returns
        -------
        Dict
            A dictionary of response from the call
        """
        data = {
            "phone_id": self.phone_id,
            "usage": usage,
            # "_csrftoken": self.token
        }
        return await self.private_request(
            path="accounts/contact_point_prefill/", data=data
        )

    async def before_login(self):
        await self.set_contact_point_prefill()
        await self.sync_launcher(True)

    async def login(self, username: str, password: str):
        self.username = username
        self.password = password
        await self.before_login()

        enc_password = await self.password_encrypt(password)

        data = {
            "jazoest": generate_jazoest(self.phone_id),
            "country_codes": '[{"country_code":"%d","source":["default"]}]'
            % int(self.country_code),
            "phone_id": self.phone_id,
            "enc_password": enc_password,
            "username": username,
            "adid": self.advertising_id,
            "guid": self.uuid,
            "device_id": self.android_device_id,
            "google_tokens": "[]",
            "login_attempt_count": "0",
        }
        logged = await self.private_request(path="accounts/login/", data=data)
        authorization = logged["headers"].get("ig-set-authorization")
        if authorization:
            self.authorization = authorization
        self.authorization_data = self.parse_authorization(
            logged["headers"].get("ig-set-authorization")
        )
    
    def get_settings(self) -> dict:
        """
        Get current session settings

        Returns
        -------
        Dict
            Current session settings as a Dict
        """
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
            "last_login": self.last_login,
            "device_settings": self.device_settings,
            "user_agent": self.user_agent,
            "country": self.country,
            "country_code": self.country_code,
            "locale": self.locale,
            "timezone_offset": self.timezone_offset,
        }

    def parse_authorization(self, authorization) -> dict:
        """Parse authorization header"""
        b64part = authorization.rsplit(":", 1)[-1]
        return json.loads(base64.b64decode(b64part))
    
    def get_bearer_authorization(self):
        if self.authorization_data:
            b64part = base64.b64encode(
                json.dumps(self.authorization_data).encode()
            ).decode()
            return f'Bearer IGT:2:{b64part}'
        # return ''

    async def password_encrypt(self, password):
        publickeyid, publickey = await self.password_publickeys()
        session_key = get_random_bytes(32)
        iv = get_random_bytes(12)
        timestamp = str(int(time.time()))
        decoded_publickey = base64.b64decode(publickey.encode())
        recipient_key = RSA.import_key(decoded_publickey)
        cipher_rsa = PKCS1_v1_5.new(recipient_key)
        rsa_encrypted = cipher_rsa.encrypt(session_key)
        cipher_aes = AES.new(session_key, AES.MODE_GCM, iv)
        cipher_aes.update(timestamp.encode())
        aes_encrypted, tag = cipher_aes.encrypt_and_digest(password.encode("utf8"))
        size_buffer = len(rsa_encrypted).to_bytes(2, byteorder="little")
        payload = base64.b64encode(
            b"".join(
                [
                    b"\x01",
                    publickeyid.to_bytes(1, byteorder="big"),
                    iv,
                    size_buffer,
                    rsa_encrypted,
                    tag,
                    aes_encrypted,
                ]
            )
        )
        return f"#PWD_INSTAGRAM:4:{timestamp}:{payload.decode()}"

    async def password_publickeys(self):
        resp = await self.public_request(url="https://i.instagram.com/api/v1/qe/sync/")
        publickeyid = int(resp.get("ig-set-password-encryption-key-id"))
        publickey = resp.get("ig-set-password-encryption-pub-key")
        return publickeyid, publickey
