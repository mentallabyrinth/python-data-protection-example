from fastapi import Request

from data_protection.models.config import AppConfig
from data_protection.redaction.engine import RedactionEngine
from data_protection.repositories.person_repository import PersonRepository


def get_config(request: Request) -> AppConfig:
    return request.app.state.config


def get_redaction_engine(request: Request) -> RedactionEngine:
    return request.app.state.engine


def get_person_repository(request: Request) -> PersonRepository:
    return request.app.state.repository
