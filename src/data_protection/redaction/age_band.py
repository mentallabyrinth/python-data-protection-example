from datetime import date


def exact_age(dob: date, reference: date) -> int:
    return reference.year - dob.year - (
        (reference.month, reference.day) < (dob.month, dob.day)
    )


def age_band(age: int) -> str:
    if age >= 90:
        return "90+"
    lower = (age // 10) * 10
    return f"{lower}-{lower + 9}"


def redact_age_band_from_dob(
    value: date | str,
    *,
    reference_date: date,
) -> str:
    if isinstance(value, str):
        dob = date.fromisoformat(value)
    else:
        dob = value
    if dob > reference_date:
        raise ValueError("date of birth cannot be in the future")
    return age_band(exact_age(dob, reference_date))
