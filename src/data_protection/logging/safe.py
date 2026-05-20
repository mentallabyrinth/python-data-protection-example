import logging
from datetime import date

from pydantic import BaseModel

from data_protection.redaction.engine import redact_model


def log_model(
    logger: logging.Logger,
    level: int,
    message: str,
    *,
    model: BaseModel,
    hmac_key_id: int = 1,
    hmac_key: bytes | str | None = None,
    reference_date: date | None = None,
) -> None:
    context = redact_model(
        model,
        hmac_key_id=hmac_key_id,
        hmac_key=hmac_key,
        reference_date=reference_date,
    )
    logger.log(level, message, extra={"context": context})
