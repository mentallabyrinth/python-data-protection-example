from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic.types import SecretStr

from data_protection.classification import Classification, RedactorKind
from data_protection.redaction.age_band import redact_age_band_from_dob
from data_protection.redaction.erase import redact_erase
from data_protection.redaction.masked import redact_masked
from data_protection.redaction.null import redact_null
from data_protection.redaction.secret_hmac import redact_secret_hmac


def get_classification(field_info: FieldInfo) -> Classification | None:
    for meta in field_info.metadata:
        if isinstance(meta, Classification):
            return meta
    return None


class RedactionEngine:
    def __init__(
        self,
        *,
        hmac_key_id: int = 1,
        hmac_key: bytes | str | None = None,
        reference_date: date | None = None,
    ) -> None:
        self.hmac_key_id = hmac_key_id
        self.hmac_key = self._coerce_key_material(hmac_key)
        self.reference_date = reference_date or date.today()

    @staticmethod
    def _coerce_key_material(hmac_key: bytes | str | None) -> bytes | None:
        if hmac_key is None:
            return None
        if isinstance(hmac_key, bytes):
            return hmac_key
        return hmac_key.encode("utf-8")

    def redact_value(self, value: Any, field_classification: Classification) -> Any:
        redactor = field_classification.redactor
        if redactor == RedactorKind.NULL:
            return redact_null(value)
        if redactor == RedactorKind.AGE_BAND_FROM_DOB:
            return redact_age_band_from_dob(value, reference_date=self.reference_date)
        if redactor == RedactorKind.SECRET_HMAC:
            if self.hmac_key is None:
                raise ValueError("hmac_key is required for SECRET_HMAC redaction")
            return redact_secret_hmac(
                str(value),
                key_id=self.hmac_key_id,
                key_material=self.hmac_key,
            )
        text = str(value)
        if redactor == RedactorKind.MASKED:
            return redact_masked(text)
        if redactor == RedactorKind.ERASE:
            return redact_erase(text)
        raise ValueError(f"unknown redactor: {redactor}")

    def redact_model(self, model: BaseModel) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for name, field_info in type(model).model_fields.items():
            value = getattr(model, name)
            if isinstance(value, SecretStr):
                value = value.get_secret_value()
            field_classification = get_classification(field_info)
            if field_classification is None:
                result[name] = value
            else:
                result[name] = self.redact_value(value, field_classification)
        return result


def redact_model(
    model: BaseModel,
    *,
    hmac_key_id: int = 1,
    hmac_key: bytes | str | None = None,
    reference_date: date | None = None,
) -> dict[str, Any]:
    engine = RedactionEngine(
        hmac_key_id=hmac_key_id,
        hmac_key=hmac_key,
        reference_date=reference_date,
    )
    return engine.redact_model(model)
