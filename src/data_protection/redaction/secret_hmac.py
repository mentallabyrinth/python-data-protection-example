import base64
import hmac
from hashlib import sha256


def redact_secret_hmac(
    plaintext: str,
    *,
    key_id: int,
    key_material: bytes,
) -> str:
    digest = hmac.new(key_material, plaintext.encode("utf-8"), sha256).digest()
    return f"{key_id}:{base64.b64encode(digest).decode('ascii')}"
