from typing import Any

from fastapi import APIRouter, Depends, Query

from data_protection.api.constants import DEFAULT_PERSON_COUNT, MAX_PERSON_COUNT
from data_protection.api.dependencies import get_person_repository, get_redaction_engine
from data_protection.models.person import Person
from data_protection.redaction.engine import RedactionEngine
from data_protection.repositories.person_repository import PersonRepository

router = APIRouter()


@router.get("/persons")
def list_persons_redacted(
    count: int = Query(default=DEFAULT_PERSON_COUNT, ge=1, le=MAX_PERSON_COUNT),
    engine: RedactionEngine = Depends(get_redaction_engine),
    repo: PersonRepository = Depends(get_person_repository),
) -> list[dict[str, Any]]:
    return [engine.redact_model(person) for person in repo.list_persons(count)]


@router.get("/internal/persons", tags=["internal"])
def list_persons_internal(
    count: int = Query(default=DEFAULT_PERSON_COUNT, ge=1, le=MAX_PERSON_COUNT),
    repo: PersonRepository = Depends(get_person_repository),
) -> list[Person]:
    return repo.list_persons(count)
