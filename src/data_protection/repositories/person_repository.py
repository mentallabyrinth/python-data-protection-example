from faker import Faker
from pydantic import ValidationError

from data_protection.models.person import PHONE_PATTERN, Person

MAX_PERSON_COUNT = 100
_MAX_GENERATION_ATTEMPTS = 50


class PersonRepository:
    def __init__(self, *, seed: int) -> None:
        self._seed = seed

    def list_persons(self, count: int) -> list[Person]:
        Faker.seed(self._seed)
        faker = Faker("en_US")
        persons: list[Person] = []
        for _ in range(count):
            persons.append(self._generate_person(faker))
        return persons

    def _generate_person(self, faker: Faker) -> Person:
        for _ in range(_MAX_GENERATION_ATTEMPTS):
            phone = faker.numerify(text="+1##########")
            if not PHONE_PATTERN.match(phone):
                continue
            try:
                return Person(
                    first_name=faker.first_name(),
                    last_name=faker.last_name(),
                    date_of_birth=faker.date_of_birth(minimum_age=18, maximum_age=90),
                    email=faker.email(),
                    phone=phone,
                    ssn=faker.ssn(),
                )
            except ValidationError:
                continue
        raise RuntimeError("failed to generate a valid Person within attempt limit")
