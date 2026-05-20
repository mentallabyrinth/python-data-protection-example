import re
from datetime import date
from typing import Annotated, Self

from pydantic import BaseModel, EmailStr, field_validator, model_validator

from data_protection.classification import RedactorKind, classification

PHONE_PATTERN = re.compile(r"^\+?[1-9]\d{6,14}$")
SSN_PATTERN = re.compile(r"^\d{3}-\d{2}-\d{4}$")


class Person(BaseModel):
    model_config = {"str_strip_whitespace": True}

    first_name: Annotated[str, classification("pii_identity", redactor=RedactorKind.MASKED)]
    last_name: Annotated[str, classification("pii_identity", redactor=RedactorKind.MASKED)]
    date_of_birth: Annotated[
        date,
        classification("pii_sensitive", redactor=RedactorKind.AGE_BAND_FROM_DOB),
    ]
    email: Annotated[EmailStr, classification("pii_contact", redactor=RedactorKind.MASKED)]
    phone: Annotated[str, classification("pii_contact", redactor=RedactorKind.MASKED)]
    ssn: Annotated[str, classification("pii_sensitive", redactor=RedactorKind.ERASE)]

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not PHONE_PATTERN.match(value):
            raise ValueError("phone must be E.164-ish format (e.g. +15551234567)")
        return value

    @field_validator("ssn")
    @classmethod
    def validate_ssn(cls, value: str) -> str:
        if not SSN_PATTERN.match(value):
            raise ValueError("ssn must match ###-##-####")
        return value

    @model_validator(mode="after")
    def validate_date_of_birth_not_future(self) -> Self:
        if self.date_of_birth > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return self
