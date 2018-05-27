# coding: utf-8
import pytest
from dynaconf import validator_conditions


positive_conditions = [
    ('eq', 1, 1),
    ('ne', 1, 2),
    ('gt', 4, 3),
    ('lt', 3, 4),
    ('gte', 5, 5),
    ('lte', 5, 5),
    ('identity', None, None),
    ('is_type_of', 42, int),
    ('is_in', 42, [42, 34]),
    ('is_not_in', 42, [55, 34]),
]


@pytest.mark.parametrize("data", positive_conditions)
def test_conditions(data):
    assert getattr(validator_conditions, data[0])(data[1], data[2])
