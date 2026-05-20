def redact_erase(value: str) -> str:
    if not value:
        return ""
    return "*" * len(value)
