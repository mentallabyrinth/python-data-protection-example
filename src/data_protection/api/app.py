from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import ValidationError
from scalar_fastapi import get_scalar_api_reference

from data_protection.api.routes import persons_router
from data_protection.logging.setup import configure_logging
from data_protection.models.config import AppConfig
from data_protection.redaction.engine import RedactionEngine
from data_protection.repositories.person_repository import PersonRepository

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        config = AppConfig()
    except ValidationError as exc:
        raise RuntimeError(
            "Failed to load configuration. Provide secrets via Doppler "
            "(doppler run) and optional PERSON_FAKER_SEED in .env."
        ) from exc

    app.state.config = config
    app.state.repository = PersonRepository(seed=config.person_faker_seed)
    app.state.engine = RedactionEngine(
        hmac_key_id=config.redaction_hmac_key_id,
        hmac_key=config.redaction_hmac_key.get_secret_value(),
    )
    yield


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="Data Protection Example API",
        description="""
        API for demonstrating data protection patterns.

        - `GET /persons` — returns records with PII redacted
        - `GET /internal/persons` — exposes full records with no redactions
        """,
        lifespan=lifespan,
        docs_url=None,  # Disable default Swagger UI
        redoc_url=None, # Disable ReDoc too (optional)
    )
    app.include_router(persons_router)

    @app.get("/docs", include_in_schema=False)
    async def scalar_docs():
        return get_scalar_api_reference(
            openapi_url="/openapi.json",
            title="Data Protection Example API",
        )

    return app
