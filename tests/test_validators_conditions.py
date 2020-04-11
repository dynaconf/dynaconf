import pytest

from dynaconf import validator_conditions


positive_conditions = [
    ("eq", 1, 1),
    ("ne", 1, 2),
    ("gt", 4, 3),
    ("lt", 3, 4),
    ("gte", 5, 5),
    ("lte", 5, 5),
    ("identity", None, None),
    ("is_type_of", 42, int),
    ("is_in", 42, [42, 34]),
    ("is_not_in", 42, [55, 34]),
    ("contd", "This word(s) contains in text", "in"),
    ("len_eq", "Length Equal", 12),
    ("len_ne", "Length Not equal", 0),
    ("len_min", "Minimum length", 3),
    ("len_max", "Maximum lenght", 15),
]


@pytest.mark.parametrize("data", positive_conditions)
def test_conditions(data):
    assert getattr(validator_conditions, data[0])(data[1], data[2])
