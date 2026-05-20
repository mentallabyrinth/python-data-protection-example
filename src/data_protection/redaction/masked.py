def redact_masked(value: str) -> str:
    if not value:
        return ""
    if len(value) > 6:
        return f"{value[:3]}***{value[-3:]}"
    return f"{value[0]}***{value[-1]}"
