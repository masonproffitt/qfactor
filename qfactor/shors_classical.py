import random
import math

from .shors_quantum import get_order


def run_shors_algorithm(n, p_min):
    if n % 1 != 0:
        raise TypeError(f'Input must be an integer; found {n} instead')

    if not 0 <= p_min <= 1:
        raise ValueError(f'Minimum confidence must be in [0, 1]; found {p_min} instead')

    p = 0
    while p < p_min:
        x = random.randrange(2, n)
        factor = math.gcd(x, n)
        if factor != 1:
            factors = [factor, n // factor]
            factors.sort()
            return tuple(factors)
        else:
            r = get_order(x, n)
            if r % 2 == 0 and x ** (r // 2) % n != n - 1:
                factor = math.gcd(x ** (r // 2) - 1, n)
                factors = [factor, n // factor]
                factors.sort()
                return tuple(factors)
            else:
                p = calculate_new_primality_confidence(p)

    return None


def calculate_new_primality_confidence(p):
    if 0 <= p <= 1:
        return 1 - 0.5 * (1 - p)
    else:
        raise ValueError(f'Input confidence must be in [0, 1]; found {p} instead')
