import pytest

from qfactor import factorize


def test_bad_type():
    with pytest.raises(TypeError):
        factorize('asdf')


def test_bad_value():
    with pytest.raises(ValueError):
        factorize(2.5)
    with pytest.raises(ValueError):
        factorize(-1)
    with pytest.raises(ValueError):
        factorize(0)
    with pytest.raises(ValueError):
        factorize(1)


def test_prime():
    assert factorize(2) is None
    assert factorize(11) is None


def test_composite_even():
    assert factorize(4) == (2, 2)


def test_composite_odd():
    assert factorize(9) == (3, 3)
