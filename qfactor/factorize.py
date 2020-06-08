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

    # From here, it is guaranteed that n is an odd integer greater than 1
    raise NotImplementedError('Factorization of odd numbers not yet implemented')
