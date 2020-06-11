import pytest

from qfactor.factoring import *


def test_factorize_bad_type():
    with pytest.raises(TypeError):
        factorize('asdf')


def test_factorize_bad_value():
    with pytest.raises(ValueError):
        factorize(2.5)
    with pytest.raises(ValueError):
        factorize(-1)
    with pytest.raises(ValueError):
        factorize(0)
    with pytest.raises(ValueError):
        factorize(1)


def test_factorize_prime():
    assert factorize(2) is None
    assert factorize(3) is None


def test_factorize_composite_even():
    assert factorize(4) == (2, 2)
    assert factorize(6) == (2, 3)


def test_factorize_composite_odd_power():
    assert factorize(9) == (3, 3)
    assert factorize(27) == (3, 9)


def test_factorize_composite_odd_non_power():
    assert factorize(15) == (3, 5)


def test_find_integer_root_bad_type():
    with pytest.raises(TypeError):
        find_integer_root('asdf')


def test_find_integer_root_none():
    assert find_integer_root(-4) is None
    assert find_integer_root(0.5) is None
    assert find_integer_root(2) is None


def test_find_integer_root_self():
    assert find_integer_root(0) == 0
    assert find_integer_root(1) == 1


def test_find_integer_root_good():
    assert find_integer_root(4) == 2
    assert find_integer_root(8) == 2
    assert find_integer_root(9) == 3
