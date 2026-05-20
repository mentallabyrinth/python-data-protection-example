from dataclasses import dataclass
from enum import StrEnum


class RedactorKind(StrEnum):
    SECRET_HMAC = "secret_hmac"
    MASKED = "masked"
    ERASE = "erase"
    AGE_BAND_FROM_DOB = "age_band_from_dob"
    NULL = "null"


@dataclass(frozen=True, slots=True)
class Classification:
    label: str
    redactor: RedactorKind = RedactorKind.MASKED


def classification(label: str, *, redactor: RedactorKind = RedactorKind.MASKED) -> Classification:
    return Classification(label=label, redactor=redactor)
