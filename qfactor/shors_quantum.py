import math

import qiskit

from .gates import get_min_n_bits_for_modulus, ModularFixedExponentiator, QFT


def get_order(x, n):
    q = get_q(n)

    print(f'Attempting to find the order of {x} relative to {n}...')

    while True:
        c = get_c(x, n, q)

        print(f'Quantum circuit measurement led to a value of {c}.')

        if c == 0:
            print('Zero value does not allow for estimation of the order. Retrying...')

        r_candidate = find_nearest_fraction(c / q, n - 1)[1]

        print(f'By continued fraction expansion, this suggests an order of {r_candidate}.')

        if x ** r_candidate % n == 1:
            print(f'Verified that {r_candidate} is the order of {x} relative to {n}.')
            return r_candidate
        else:
            print(f'{r_candidate} is not the order of {x} relative to {n}. Retrying...')


def get_q(n):
    return 2 ** math.ceil(2 * math.log2(n))


def get_c(x, n, q):
    result = get_circuit_result(x, n, q, 1)
    return int(list(result.get_counts())[0], 2)


def get_circuit_result(x, n, q, shots):
    first_register = qiskit.QuantumRegister(get_min_n_bits_for_modulus(q))
    second_register = qiskit.QuantumRegister(get_min_n_bits_for_modulus(n))
    ancilla_register = qiskit.QuantumRegister(get_min_n_bits_for_modulus(n) + 2)
    measurement_register = qiskit.ClassicalRegister(first_register.size)
    circuit = qiskit.QuantumCircuit(first_register,
                                    second_register,
                                    ancilla_register,
                                    measurement_register)
    circuit.h(first_register)
    circuit.append(ModularFixedExponentiator(first_register.size, second_register.size, x, n),
                   circuit.qubits)
    circuit.append(QFT(first_register.size), first_register)
    circuit.measure(first_register, measurement_register)
    backend = qiskit.Aer.get_backend('qasm_simulator')
    job = qiskit.execute(circuit, backend, shots=shots)
    result = job.result()
    return result


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
        if math.isclose(fractional_part, 0, abs_tol=1e-9) or get_fraction(expansion)[1] >= max_denominator:
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
