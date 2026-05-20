import pytest

from data_protection.redaction.engine import RedactionEngine


@pytest.fixture
def hmac_key() -> bytes:
    return b"test-hmac-key-material"


@pytest.fixture
def engine(hmac_key: bytes) -> RedactionEngine:
    return RedactionEngine(
        hmac_key_id=1,
        hmac_key=hmac_key,
        reference_date=__import__("datetime").date(2026, 5, 19),
    )
