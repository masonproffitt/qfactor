import math


# Factor a number into two smaller numbers or return None if prime
def factorize(n):
    # Ensure that n is an integer
    if n % 1 != 0:
        raise ValueError(f'Input must be an integer; found {n} instead')

    # Ensure that n is positive and greater than 1
    if n < 2:
        raise ValueError(f'Input must be greater than or equal to 2; found {n} instead')

    # Two is a special case as the only even prime number
    if n == 2:
        return None

    # Otherwise, if n is even, factoring is nearly trivial
    elif n % 2 == 0:
        return (2, n / 2)

    # Handle the case of an integer power of an integer
    integer_root = find_integer_root(n)
    if integer_root is not None:
        return (integer_root, n / integer_root)

    # From here, it is guaranteed that n is an odd integer greater than 1 which is not an integer power higher than 1 of a prime

    raise NotImplementedError('Full factorization algorithm not yet implemented')


# Search for an integer root
def find_integer_root(n):
    if n < 0:
        return None
    elif n == 0 or n == 1:
        return n
    else:
        for j in range(2, math.floor(math.log2(n)) + 1):
            root = n ** (j ** -1)
            if root % 1 == 0:
                return int(root)
        return None
