import json
import logging
from typing import Any


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        context = getattr(record, "context", None)
        if context is not None:
            payload["context"] = context
        return json.dumps(payload, default=str)


def configure_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter())
    root.addHandler(handler)
