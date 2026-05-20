from datetime import date

import pytest
from pydantic import ValidationError

from data_protection.models import AppConfig, Person
from data_protection.redaction import redact_model


@pytest.fixture
def env_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
    monkeypatch.setenv("GROK_API_KEY", "grok-test-key")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-test-key")
    monkeypatch.setenv("REDACTION_HMAC_KEY_ID", "1")
    monkeypatch.setenv("REDACTION_HMAC_KEY", "test-hmac-secret")


def test_person_valid() -> None:
    person = Person(
        first_name="Jane",
        last_name="Doe",
        date_of_birth=date(1990, 6, 15),
        email="jane@example.com",
        phone="+15551234567",
        ssn="123-45-6789",
    )
    assert person.first_name == "Jane"


def test_person_invalid_email() -> None:
    with pytest.raises(ValidationError):
        Person(
            first_name="Jane",
            last_name="Doe",
            date_of_birth=date(1990, 6, 15),
            email="not-an-email",
            phone="+15551234567",
            ssn="123-45-6789",
        )


def test_person_invalid_phone() -> None:
    with pytest.raises(ValidationError):
        Person(
            first_name="Jane",
            last_name="Doe",
            date_of_birth=date(1990, 6, 15),
            email="jane@example.com",
            phone="555",
            ssn="123-45-6789",
        )


def test_person_invalid_ssn() -> None:
    with pytest.raises(ValidationError):
        Person(
            first_name="Jane",
            last_name="Doe",
            date_of_birth=date(1990, 6, 15),
            email="jane@example.com",
            phone="+15551234567",
            ssn="123456789",
        )


def test_person_future_dob() -> None:
    with pytest.raises(ValidationError):
        Person(
            first_name="Jane",
            last_name="Doe",
            date_of_birth=date(2099, 1, 1),
            email="jane@example.com",
            phone="+15551234567",
            ssn="123-45-6789",
        )


def test_app_config_from_env(env_config: None) -> None:
    config = AppConfig()
    assert config.redaction_hmac_key_id == 1


def test_redact_person(env_config: None) -> None:
    person = Person(
        first_name="Jane",
        last_name="Doe",
        date_of_birth=date(1990, 6, 15),
        email="jane.doe@example.com",
        phone="+15551234567",
        ssn="123-45-6789",
    )
    redacted = redact_model(
        person,
        hmac_key_id=1,
        hmac_key=b"test-hmac-secret",
        reference_date=date(2026, 5, 19),
    )
    assert redacted["date_of_birth"] == "30-39"
    assert redacted["ssn"] == "***********"
    assert "123-45-6789" not in str(redacted.values())
    assert "1990-06-15" not in str(redacted.values())
    assert "Jane" not in redacted["first_name"]


def test_redact_app_config(env_config: None) -> None:
    config = AppConfig()
    redacted = redact_model(
        config,
        hmac_key_id=1,
        hmac_key=b"test-hmac-secret",
    )
    assert redacted["anthropic_api_key"].startswith("1:")
    assert "sk-ant-test-key" not in str(redacted.values())
