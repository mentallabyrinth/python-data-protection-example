import logging
from datetime import date

import pytest

from data_protection.logging import configure_logging, log_model
from data_protection.models import Person


@pytest.fixture
def logger() -> logging.Logger:
    configure_logging()
    return logging.getLogger("test.data_protection")


def test_log_model_redacts_secrets(
    logger: logging.Logger,
    caplog: pytest.LogCaptureFixture,
) -> None:
    person = Person(
        first_name="Jane",
        last_name="Doe",
        date_of_birth=date(1990, 6, 15),
        email="jane.doe@example.com",
        phone="+15551234567",
        ssn="123-45-6789",
    )

    with caplog.at_level(logging.INFO):
        log_model(
            logger,
            logging.INFO,
            "person created",
            model=person,
            hmac_key_id=1,
            hmac_key=b"test-hmac-secret",
            reference_date=date(2026, 5, 19),
        )

    assert "123-45-6789" not in caplog.text
    assert "1990-06-15" not in caplog.text
    assert "jane.doe@example.com" not in caplog.text

    context = caplog.records[-1].context
    assert context["date_of_birth"] == "30-39"
    assert context["ssn"] == "***********"
