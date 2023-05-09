import hashlib
import time
import uuid
from urllib.parse import quote_plus


def generate_jazoest(symbols: str) -> str:
    amount = sum(ord(s) for s in symbols)
    return f"2{amount}"


def generate_signature(data):
    return f"signed_body=SIGNATURE.{quote_plus(data)}"


def generate_uuid(prefix: str = "", suffix: str = "") -> str:
    return f"{prefix}{uuid.uuid4()}{suffix}"


def generate_android_device_id() -> str:
    return f"android-{hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]}"
