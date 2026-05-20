import re
from datetime import date

import pytest

from data_protection.redaction.age_band import age_band, exact_age, redact_age_band_from_dob
from data_protection.redaction.erase import redact_erase
from data_protection.redaction.masked import redact_masked
from data_protection.redaction.secret_hmac import redact_secret_hmac

HMAC_PATTERN = re.compile(r"^\d+:[A-Za-z0-9+/=]+$")


def test_masked_long_string() -> None:
    assert redact_masked("jane.doe@example.com") == "jan***com"


def test_masked_short_string() -> None:
    assert redact_masked("abc") == "a***c"


def test_masked_empty() -> None:
    assert redact_masked("") == ""


def test_erase() -> None:
    assert redact_erase("123-45-6789") == "***********"


def test_secret_hmac_format(hmac_key: bytes) -> None:
    token = redact_secret_hmac("secret-value", key_id=1, key_material=hmac_key)
    assert HMAC_PATTERN.match(token)
    assert token.startswith("1:")


def test_secret_hmac_stable(hmac_key: bytes) -> None:
    a = redact_secret_hmac("same", key_id=1, key_material=hmac_key)
    b = redact_secret_hmac("same", key_id=1, key_material=hmac_key)
    assert a == b


def test_secret_hmac_key_id_prefix(hmac_key: bytes) -> None:
    one = redact_secret_hmac("same", key_id=1, key_material=hmac_key)
    two = redact_secret_hmac("same", key_id=2, key_material=hmac_key)
    assert one.startswith("1:")
    assert two.startswith("2:")
    assert one != two


def test_age_band_examples() -> None:
    assert age_band(7) == "0-9"
    assert age_band(15) == "10-19"
    assert age_band(29) == "20-29"
    assert age_band(35) == "30-39"
    assert age_band(94) == "90+"


def test_exact_age_birthday_not_yet_occurred() -> None:
    reference = date(2026, 5, 19)
    dob = date(1990, 12, 1)
    assert exact_age(dob, reference) == 35


def test_redact_age_band_from_dob() -> None:
    assert redact_age_band_from_dob(date(1990, 6, 15), reference_date=date(2026, 5, 19)) == "30-39"


def test_redact_age_band_future_dob() -> None:
    with pytest.raises(ValueError, match="future"):
        redact_age_band_from_dob(date(2030, 1, 1), reference_date=date(2026, 5, 19))
