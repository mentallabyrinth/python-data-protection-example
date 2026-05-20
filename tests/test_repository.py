from data_protection.repositories.person_repository import PersonRepository


def test_list_persons_is_deterministic_for_same_seed_and_count() -> None:
    repo = PersonRepository(seed=42)
    first = repo.list_persons(3)
    second = repo.list_persons(3)
    assert [p.model_dump() for p in first] == [p.model_dump() for p in second]


def test_list_persons_prefix_matches_larger_count() -> None:
    repo = PersonRepository(seed=42)
    three = repo.list_persons(3)
    ten = repo.list_persons(10)
    assert [p.model_dump() for p in three] == [p.model_dump() for p in ten[:3]]
