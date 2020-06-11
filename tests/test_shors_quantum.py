import pytest

from qfactor.shors_quantum import *


def test_get_order_bad_type():
    with pytest.raises(TypeError):
        get_order('asdf', 15)
        get_order(2, 'asdf')


def test_get_order_bad_value():
    with pytest.raises(ValueError):
        get_order(-1, 15)
    with pytest.raises(ValueError):
        get_order(0, 15)
    with pytest.raises(ValueError):
        get_order(0.5, 15)


def test_get_order_good():
    assert get_order(2, 3) == 2
    assert get_order(7, 15) == 4


def test_get_q_bad_type():
    with pytest.raises(TypeError):
        get_q('asdf')


def test_get_q_good():
    assert get_q(3) == 16
    assert get_q(15) == 256


def test_find_nearest_fraction_bad_type():
    with pytest.raises(TypeError):
        find_nearest_fraction('asdf', 1)
    with pytest.raises(TypeError):
        find_nearest_fraction(0, 'asdf')


def test_find_nearest_fraction_bad_value():
    with pytest.raises(ValueError):
        find_nearest_fraction(-1, 1)
    with pytest.raises(ValueError):
        find_nearest_fraction(0, -1)
    with pytest.raises(ValueError):
        find_nearest_fraction(0, 0)
    with pytest.raises(ValueError):
        find_nearest_fraction(0, 0.5)


def test_find_nearest_fraction():
    assert find_nearest_fraction(0.4, 2) == (1, 2)
    assert find_nearest_fraction(0.6, 3) == (2, 3)


def test_get_fraction_bad_size():
    with pytest.raises(IndexError):
        get_fraction([])


def test_get_fraction_bad_type():
    with pytest.raises(TypeError):
        get_fraction(['asdf'])


def test_get_fraction_bad_value():
    with pytest.raises(ValueError):
        get_fraction([0.5])


def test_get_fraction_good():
    assert get_fraction([2]) == (2, 1)
    assert get_fraction([0, 2]) == (1, 2)
    assert get_fraction([0, 2, 3]) == (3, 7)
