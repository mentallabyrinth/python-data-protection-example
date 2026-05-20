import pytest
from fastapi.testclient import TestClient

from data_protection.api.app import create_app


@pytest.fixture
def env_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
    monkeypatch.setenv("GROK_API_KEY", "grok-test-key")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-test-key")
    monkeypatch.setenv("REDACTION_HMAC_KEY_ID", "1")
    monkeypatch.setenv("REDACTION_HMAC_KEY", "test-hmac-secret")
    monkeypatch.setenv("PERSON_FAKER_SEED", "42")


@pytest.fixture
def client(env_config: None) -> TestClient:
    with TestClient(create_app()) as test_client:
        yield test_client


def test_list_persons_redacted_count(client: TestClient) -> None:
    response = client.get("/persons", params={"count": 3})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    assert body[0]["date_of_birth"] == "30-39" or isinstance(body[0]["date_of_birth"], str)
    assert "*" in body[0]["ssn"]
    assert "@" not in body[0]["email"] or "***" in body[0]["email"]


def test_list_persons_internal_full_pii(client: TestClient) -> None:
    response = client.get("/internal/persons", params={"count": 3})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    assert "ssn" in body[0]
    assert len(body[0]["ssn"]) == 11
    assert "-" in body[0]["date_of_birth"]


def test_list_persons_default_count(client: TestClient) -> None:
    response = client.get("/persons")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_list_persons_count_over_max_returns_422(client: TestClient) -> None:
    response = client.get("/persons", params={"count": 101})
    assert response.status_code == 422


def test_list_persons_count_zero_returns_422(client: TestClient) -> None:
    response = client.get("/persons", params={"count": 0})
    assert response.status_code == 422


def test_redacted_differs_from_internal(client: TestClient) -> None:
    redacted = client.get("/persons", params={"count": 1}).json()
    internal = client.get("/internal/persons", params={"count": 1}).json()
    assert redacted[0]["ssn"] != internal[0]["ssn"]
    assert redacted[0]["email"] != internal[0]["email"]


def test_same_seed_same_internal_email_across_requests(client: TestClient) -> None:
    first = client.get("/internal/persons", params={"count": 1}).json()[0]["email"]
    second = client.get("/internal/persons", params={"count": 1}).json()[0]["email"]
    assert first == second
