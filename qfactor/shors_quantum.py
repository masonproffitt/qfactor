import math

import qiskit

from .gates import ModularFixedExponentiator


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
    first_register = qiskit.QuantumRegister(get_min_n_bits(q))
    second_register = qiskit.QuantumRegister(get_min_n_bits(n))
    ancilla_register = qiskit.QuantumRegister(get_min_n_bits(n) + 2)
    measurement_register = qiskit.ClassicalRegister(first_register.size)
    circuit = qiskit.QuantumCircuit(first_register,
                                    second_register,
                                    ancilla_register,
                                    measurement_register)
    circuit.h(first_register)
    circuit.append(ModularFixedExponentiator(first_register.size, second_register.size, x, n),
                   circuit.qubits)
    circuit.measure(first_register, measurement_register)
    backend = qiskit.Aer.get_backend('qasm_simulator')
    job = qiskit.execute(circuit, backend, shots=1)
    result = job.result()
    return int(list(result.get_counts(circuit))[0], 2)


def get_min_n_bits(value):
    return math.ceil(math.log2(value))


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
