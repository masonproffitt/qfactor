import math

import qiskit

from .gates import get_min_n_bits_for_modulus, ModularFixedExponentiator, QFT


# Get the order of x relative to n.
# That is, find the smallest integer r > 0 such that x ** r % n == 1.
def get_order(x, n):
    # Ensure that n is a valid integer
    if n % 1 != 0 or n < 3:
        raise ValueError(f'n must be an integer greater than 2; found {n} instead')

    # Ensure that x is a valid integer
    if x % 1 != 0 or x < 2 or x >= n:
        raise ValueError(f'x must be an integer in [2, n); found {x} instead')

    # Determine the value of q, a power of 2 such that n ** 2 <= q < 2 * n ** 2
    q = get_q(n)

    print(f'Attempting to find the order of {x} relative to {n}...')

    while True:
        # Run the quantum circuit experiment to get a measured value
        c = get_c(x, n, q)

        print(f'Quantum circuit measurement led to a value of {c}.')

        if c == 0:
            print('Zero value does not allow for estimation of the order. Retrying...')

        # Try to figure out the order by assuming c / q = d / r for some integer d
        r_candidate = find_nearest_fraction(c / q, n - 1)[1]

        print(f'By continued fraction expansion, this suggests an order of {r_candidate}.')

        # Check whether this is actually the order of x. Otherwise try again.
        if x ** r_candidate % n == 1:
            print(f'Verified that {r_candidate} is the order of {x} relative to {n}.')
            return r_candidate
        else:
            print(f'{r_candidate} is not the order of {x} relative to {n}. Retrying...')


# Return the value of q
def get_q(n):
    return 2 ** math.ceil(2 * math.log2(n))


# Return the value of c
def get_c(x, n, q):
    # Run quantum circuit and get a single measurement
    result = get_circuit_result(x, n, q, 1)

    # get_counts() returns a dictionary. The single key is a string of a binary number.
    binary_representation = list(result.get_counts())[0]

    # Convert to an integer representation of the measurement and return it
    c = int(binary_representation, 2)
    return c


# Simulate the quantum circuit that measures the value of c
def get_circuit_result(x, n, q, shots):
    # Exponent and final result register
    first_register = qiskit.QuantumRegister(get_min_n_bits_for_modulus(q))

    # Register for exponentiation result
    second_register = qiskit.QuantumRegister(get_min_n_bits_for_modulus(n))

    # Ancilla qubits for modular additions and multiplications
    ancilla_register = qiskit.QuantumRegister(get_min_n_bits_for_modulus(n) + 2)

    # Measurement of result register is stored in this register of classical bits
    measurement_register = qiskit.ClassicalRegister(first_register.size)
    circuit = qiskit.QuantumCircuit(first_register,
                                    second_register,
                                    ancilla_register,
                                    measurement_register)

    # Place exponent register in equal superposition of all states with no relative phases by
    # applying Hadamard gate to all qubits. Equivalent to a QFT on |0>.
    circuit.h(first_register)

    # Exponentiate x by the first register, modulo n, and store the result in the second register
    circuit.append(ModularFixedExponentiator(first_register.size, second_register.size, x, n),
                   circuit.qubits)

    # Apply a QFT
    circuit.append(QFT(first_register.size), first_register)

    # Measure the first register
    circuit.measure(first_register, measurement_register)

    # Get simulation backend
    backend = qiskit.Aer.get_backend('qasm_simulator')

    # Run circuit
    job = qiskit.execute(circuit, backend, shots=shots)

    # Retrieve and return final measurement results from simulation
    result = job.result()
    return result


# Construct the continued fraction expansion of a number and find the closest rational
# approximation up to a maximum denominator. Returns the (numerator, denominator) pair.
def find_nearest_fraction(original_number, max_denominator):
    if original_number < 0:
        raise ValueError('Original number must be greater than or equal to 0;'
                         + f' found {original_number} instead')

    if max_denominator < 1:
        raise ValueError('Max denominator must be greater than or equal to 1;'
                         + f' found {max_denominator} instead')

    # Initialize the list holding the integers of the continued fraction expansion
    expansion = []
    current_number = original_number
    while True:
        # Break into integer and fractional components
        integer_part = math.floor(current_number)
        fractional_part = current_number % 1

        # Store the next number in the expansion
        expansion.append(integer_part)

        # Stop if fractional part is 0 (expansion is exact) or if overall denominator exceeds max
        if fractional_part < 1e-9 or get_fraction(expansion)[1] >= max_denominator:
            break
        else:
            # Run next iteration with reciprocal of current fractional component
            current_number = fractional_part ** -1

    # If the overall denominator is larger than the max, we need to backtrack a bit
    if get_fraction(expansion)[1] > max_denominator:
        # Start from the third to last fraction representation
        fraction_to_return = list(get_fraction(expansion[:-2]))
        second_to_last_fraction = get_fraction(expansion[:-1])
        # Add the second to last numerator and denominator to the third to last numerator and
        # denominator, respectively, until we reach the largest denominator below the max
        while fraction_to_return[1] + second_to_last_fraction[1] <= max_denominator:
            fraction_to_return[0] += second_to_last_fraction[0]
            fraction_to_return[1] += second_to_last_fraction[1]
        # Return this best fractional approximation
        return tuple(fraction_to_return)
    # Otherwise just return the fraction for the full expansion
    else:
        return get_fraction(expansion)


# Convert a continued fraction expansion into a simple fraction with an integer numerator and
# integer denominator. Returns the (numerator, denominator) pair.
def get_fraction(expansion):
    # Expansion should not be empty
    if len(expansion) == 0:
        raise IndexError('Continued fraction expansion cannot be empty')
    elif len(expansion) == 1:
        # All elements should be integers
        if expansion[0] % 1 != 0:
            raise ValueError('Continued fraction expansion must be composed of integers;'
                             + f' found {expansion[0]} instead')

        # Integers are their own one-element expansion.
        # Turn them into a fraction with a denominator of 1
        return (expansion[0], 1)
    else:
        # Recursively unroll the continued fraction, combining each level into a single fraction
        nested_fraction = get_fraction(expansion[1:])
        return (expansion[0] * nested_fraction[0] + nested_fraction[1], nested_fraction[0])
