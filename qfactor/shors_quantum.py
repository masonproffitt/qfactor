import math


def get_order(x, n):
    q = get_q(n)

    while True:
        c = get_c(x, n, q)
        r_candidate = find_nearest_fraction(c / q, n - 1)[1]
        if x ** r_candidate % n == 1:
            return r_candidate


def get_q(n):
    return 2 ** math.ceil(2 * math.log2(n))


def get_c(x, n, q):
    raise NotImplementedError('Quantum part of algorithm not yet implemented')


def find_nearest_fraction(original_number, max_denominator):
    if original_number < 0:
        raise ValueError('Original number must be greater than or equal to 0;'
                         + f' found {original_number} instead')

    if max_denominator < 1:
        raise ValueError('Max denominator must be greater than or equal to 1;'
                         + f' found {max_denominator} instead')

    expansion = []
    current_number = original_number
    while True:
        integer_part = math.floor(current_number)
        fractional_part = current_number % 1
        expansion.append(integer_part)
        if fractional_part == 0 or get_fraction(expansion)[1] >= max_denominator:
            break
        else:
            current_number = fractional_part ** -1

    if get_fraction(expansion)[1] > max_denominator:
        fraction_to_return = list(get_fraction(expansion[:-2]))
        second_to_last_fraction = get_fraction(expansion[:-1])
        while fraction_to_return[1] + second_to_last_fraction[1] <= max_denominator:
            fraction_to_return[0] += second_to_last_fraction[0]
            fraction_to_return[1] += second_to_last_fraction[1]
        return tuple(fraction_to_return)
    else:
        return get_fraction(expansion)


def get_fraction(expansion):
    if len(expansion) == 0:
        raise IndexError('Continued fraction expansion cannot be empty')
    elif len(expansion) == 1:
        if expansion[0] % 1 != 0:
            raise ValueError('Continued fraction expansion must be composed of integers;'
                             + f' found {expansion[0]} instead')
        return (expansion[0], 1)
    else:
        nested_fraction = get_fraction(expansion[1:])
        return (expansion[0] * nested_fraction[0] + nested_fraction[1], nested_fraction[0])
