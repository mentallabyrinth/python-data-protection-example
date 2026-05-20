# Data Protection Example

A small Python project mirroring data protection practices from other APIs I've developed, demonstrated across four concerns:

- **Configuration**: non-sensitive config via `.env`; secrets injected at runtime via **Doppler** or **Infisical**, never committed to source control.
- **Model classification**: sensitive fields are annotated at definition time using **Pydantic** models and field-level **`classification`** metadata.
- **Log redaction**: all model values are redacted before they reach logs, preventing accidental PII exposure.
- **API boundary redaction**: public endpoints return redacted payloads; internal endpoints return full data for trusted consumers only.

## Concepts

- **Classify at definition**: sensitive fields are marked with `Annotated[..., classification(...)]` on the model.
- **Redact at log time**: `log_model()` always runs values through `redact_model()` before they reach logs.
- **Redact at the public API**: `GET /persons` returns redacted payloads; `GET /internal/persons` returns full data.
- **Secrets via Doppler or Infisical**: API keys and HMAC material are injected at runtime with `doppler run` or `infisical run`.
- **Non-sensitive config via `.env`**: `PERSON_FAKER_SEED` for reproducible fake data (see [`.env.example`](.env.example)).

## Configuration

> No AI integrations. This is a proof of concept only.

| Source | Variables |
|--------|-----------|
| **Doppler** or **Infisical** | `ANTHROPIC_API_KEY`, `GROK_API_KEY`, `GEMINI_API_KEY`, `REDACTION_HMAC_KEY`, `REDACTION_HMAC_KEY_ID` |
| **`.env`** (optional) | `PERSON_FAKER_SEED` (default: `42`) |

```bash
cp .env.example .env   # optional: seed only
```

**Doppler:**
```bash
doppler login
doppler setup
# set secrets in Doppler: see secrets/secrets.example
```

**Infisical:**
```bash
infisical login
infisical init
# set secrets in Infisical: see secrets/secrets.example
```

## HTTP API

| Route | Description |
|-------|-------------|
| `GET /persons` | Redacted list of persons (safe for external use) |
| `GET /internal/persons` | Full record no redaction |

**Query parameter `count`** (both routes): default `5`, range `1`–`100` (values outside this range return **422**).

```bash
# Doppler
doppler run -- uv run data-protection-api
# Infisical
infisical run -- uv run data-protection-api
# Open http://127.0.0.1:8000/docs
curl "http://127.0.0.1:8000/persons?count=3"
curl "http://127.0.0.1:8000/internal/persons?count=3"
```

## CLI Demo

```bash
# Doppler
doppler run -- uv run data-protection
# Infisical
infisical run -- uv run data-protection
```

## Redactors

| Kind | Output |
|------|--------|
| `SECRET_HMAC` | `{keyId}:{base64(hmac_sha256)}` (versioned for key rotation) |
| `MASKED` | First/last 3 chars (or 1 for short strings) with `***` in the middle |
| `ERASE` | Same-length `*` string |
| `AGE_BAND_FROM_DOB` | 10-year bands (`0–9`, …, `80–89`, `90+`) |
| `NULL` | No change |

## Tests

```bash
uv run pytest
```

## Key Rotation (HMAC)

Similar to `Microsoft.Extensions.Compliance.Redaction.HmacRedactor`.

1. In Doppler or Infisical, set a new `REDACTION_HMAC_KEY` and bump `REDACTION_HMAC_KEY_ID` to `2`.
2. New log lines and HMAC-redacted fields will use the `2:` prefix.
3. Retire old key material after log retention allows.