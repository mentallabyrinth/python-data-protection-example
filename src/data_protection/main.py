import logging
import sys
from datetime import date

from pydantic import ValidationError

from data_protection.logging import configure_logging, log_model
from data_protection.models import AppConfig, Person


def main() -> None:
    configure_logging()
    logger = logging.getLogger("data_protection")

    try:
        config = AppConfig()
    except ValidationError as exc:
        print(
            "Failed to load configuration. Secrets must be injected via Doppler, e.g.\n"
            "  doppler setup   # once per machine\n"
            "  doppler run -- uv run data-protection",
            file=sys.stderr,
        )
        print(exc, file=sys.stderr)
        sys.exit(1)

    person = Person(
        first_name="Jane",
        last_name="Doe",
        date_of_birth=date(1990, 6, 15),
        email="jane.doe@example.com",
        phone="+15551234567",
        ssn="123-45-6789",
    )

    hmac_key = config.redaction_hmac_key.get_secret_value()
    hmac_key_id = config.redaction_hmac_key_id

    log_model(
        logger,
        logging.INFO,
        "application configuration loaded",
        model=config,
        hmac_key_id=hmac_key_id,
        hmac_key=hmac_key,
    )
    log_model(
        logger,
        logging.INFO,
        "person record created",
        model=person,
        hmac_key_id=hmac_key_id,
        hmac_key=hmac_key,
    )


if __name__ == "__main__":
    main()
