from typing import Annotated

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from data_protection.classification import RedactorKind, classification


class AppConfig(BaseSettings):
    """Secrets from Doppler (env); non-sensitive options from optional `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    person_faker_seed: int = Field(default=42, ge=0)

    anthropic_api_key: Annotated[
        SecretStr,
        classification("api_credential", redactor=RedactorKind.SECRET_HMAC),
    ]
    grok_api_key: Annotated[
        SecretStr,
        classification("api_credential", redactor=RedactorKind.SECRET_HMAC),
    ]
    gemini_api_key: Annotated[
        SecretStr,
        classification("api_credential", redactor=RedactorKind.SECRET_HMAC),
    ]

    redaction_hmac_key_id: int = Field(default=1, ge=1)
    redaction_hmac_key: Annotated[
        SecretStr,
        classification("api_credential", redactor=RedactorKind.SECRET_HMAC),
    ]
