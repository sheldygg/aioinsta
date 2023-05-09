import base64
import time

from Cryptodome.Cipher import AES, PKCS1_v1_5
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes

from aioinsta import login
from aioinsta.request import PrivateRequestClient


class PasswordClient:
    def __init__(self, login_client: "login.Login"):
        self.login_client = login_client

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
        response = await self.login_client.private_request(
            method="GET", path="qe/sync/"
        )
        headers = response.get("headers")
        publickeyid = int(headers.get("ig-set-password-encryption-key-id"))
        publickey = headers.get("ig-set-password-encryption-pub-key")
        return publickeyid, publickey
