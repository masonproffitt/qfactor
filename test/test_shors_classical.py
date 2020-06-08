import pytest

from qfactor.shors_classical import run_shors_algorithm, calculate_new_primality_confidence


def test_shors_algorithm_bad_type():
    with pytest.raises(TypeError):
        run_shors_algorithm('asdf', 0.5)
    with pytest.raises(TypeError):
        run_shors_algorithm(15, 'asdf')


def test_shors_algorithm_bad_value():
    with pytest.raises(ValueError):
        run_shors_algorithm(15, -1)
    with pytest.raises(ValueError):
        run_shors_algorithm(15, 2)


def test_shors_algorithm_prime():
    assert run_shors_algorithm(3, 0.95) is None


def test_shors_algorithm_composite():
    assert run_shors_algorithm(15, 1) == (3, 5)


def test_primality_confidence_bad_type():
    with pytest.raises(TypeError):
        calculate_new_primality_confidence('asdf')


def test_primality_confidence_bad_value():
    with pytest.raises(ValueError):
        calculate_new_primality_confidence(-1)
    with pytest.raises(ValueError):
        calculate_new_primality_confidence(2)


def test_primality_confidence_good():
    assert calculate_new_primality_confidence(0) == 0.5
    assert calculate_new_primality_confidence(0.5) == 0.75
    assert calculate_new_primality_confidence(0.75) == 0.875
