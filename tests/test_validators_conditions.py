from __future__ import annotations

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
    ("cont", "This word(s) contains in text", "in"),
    ("len_eq", "Length Equal", 12),
    ("len_eq", [1, 2, 3], 3),
    ("len_ne", "Length Not equal", 0),
    ("len_ne", [], 1),
    ("len_min", "Minimum length", 3),
    ("len_min", [1, 2, 3, 4, 5], 3),
    ("len_max", "Maximum length", 15),
    ("len_max", [1, 2, 3, 4, 5], 5),
    ("startswith", "codeshow", "code"),
    ("endswith", "codeshow", "show"),
]


@pytest.mark.parametrize("data", positive_conditions)
def test_conditions(data):
    assert getattr(validator_conditions, data[0])(data[1], data[2])


negative_conditions = [
    ("eq", 1, 2),
    ("ne", 1, 1),
    ("gt", 4, 4),
    ("lt", 3, 3),
    ("gte", 5, 6),
    ("lte", 5, 4),
    ("identity", None, 1),
    ("is_type_of", 42, str),
    ("is_in", 42, [55, 34]),
    ("is_not_in", 42, [42, 34]),
    ("cont", "This word(s) contains in text", "out"),
    ("len_eq", "Length Equal", 0),
    ("len_eq", [1, 2, 3], 4),
    ("len_ne", "Length Not equal", 16),
    ("len_ne", [], 0),
    ("len_min", "Minimum length", 15),
    ("len_min", [1, 2, 3, 4, 5], 6),
    ("len_max", "Maximum length", 3),
    ("len_max", [1, 2, 3, 4, 5], 4),
    ("startswith", "codeshow", "show"),
    ("endswith", "codeshow", "code"),
]


@pytest.mark.parametrize("data", negative_conditions)
def test_negative_conditions(data):
    assert not getattr(validator_conditions, data[0])(data[1], data[2])
