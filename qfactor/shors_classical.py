import random
import math

from .shors_quantum import get_order


# Run the classical part of Shor's algorithm, with
# the quantum part contained in a call to get_order().
def run_shors_algorithm(n, p_min):
    # Ensure that n is an integer
    if n % 1 != 0:
        raise TypeError(f'Input must be an integer; found {n} instead')

    # Ensure that the minimum confidence can be interpreted as a probability
    if not 0 <= p_min <= 1:
        raise ValueError(f'Minimum confidence must be in [0, 1]; found {p_min} instead')

    p = 0
    while p < p_min:
        # First step is to pick a random x
        x = random.randrange(2, n)

        # If x shares a non-trivial factor with n, we're already done
        factor = math.gcd(x, n)
        if factor != 1:
            factors = [factor, n // factor]
            factors.sort()
            return tuple(factors)
        else:
            # Run the quantum part of the algorithm to get the order of x
            r = get_order(x, n)
            # The order is guaranteed to share a factor with n if these two conditions hold
            if r % 2 == 0 and x ** (r // 2) % n != n - 1:
                # Find the actual factors of n and return them
                factor = math.gcd(x ** (r // 2) - 1, n)
                factors = [factor, n // factor]
                factors.sort()
                return tuple(factors)
            # Otherwise we build confidence that n is prime
            else:
                p = calculate_new_primality_confidence(p)

    return None


# Calculate the new confidence in the primality of n based on the previous probability
def calculate_new_primality_confidence(p):
    # Ensure that p can be interpreted as a probability
    if 0 <= p <= 1:
        # Each order has at least a 50% chance to share a factor with n if n is not prime.
        # Thus each order that does not share a factor with n halves the probability
        # that n is composite.
        return 1 - 0.5 * (1 - p)
    else:
        raise ValueError(f'Input confidence must be in [0, 1]; found {p} instead')
