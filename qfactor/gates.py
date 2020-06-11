import math

import qiskit


# Get the minimum number of bits needed to represent
# any non-negative integer less than the modulus given.
def get_min_n_bits_for_modulus(modulus):
    if modulus == 1:
        return 1
    else:
        return math.ceil(math.log2(modulus))


# Get the minimum number of bits needed to represent the given value
def get_min_n_bits_for_value(value):
    return get_min_n_bits_for_modulus(value + 1)


# Initialize the qubits of a circuit to the given value
def initialize_to_value(circuit, value):
    for i in range(get_min_n_bits_for_value(value)):
        if value & 2 ** i:
            circuit.x(i)


# Implementation of an R_k gate, a single-qubit gate which advances the phase of the |1> component
# by 2 * pi / 2 ** k. Equivalent to a z-rotation up to an overall phase.
class Rk(qiskit.circuit.library.U1Gate):
    def __init__(self, k):
        super().__init__(2 * math.pi / 2 ** k, label=f'R_{k}')


# Reverse the ordering of all qubits of a quantum circuit via SWAP gates
def reverse_qubits(circuit):
    for i in range(circuit.num_qubits // 2):
        circuit.swap(i, circuit.num_qubits - 1 - i)


# Implementation of the quantum Fourier transform
class QFT(qiskit.QuantumCircuit):
    def __init__(self, n_qubits):
        super().__init__(n_qubits, name='QFT')
        for i in range(n_qubits - 1, -1, -1):
            self.h(i)
            for j in range(i - 1, -1, -1):
                k = i - j + 1
                self.append(Rk(k).control(1), [self.qubits[j], self.qubits[i]])
        reverse_qubits(self)


# Gate which maps QFT(b) to QFT(b + c), where c is a constant compiled into the circuit
class FixedQFTAdder(qiskit.QuantumCircuit):
    def __init__(self, n_qubits, c):
        super().__init__(n_qubits, name=f'FixedQFTAdder({c})')
        # Loop over each input qubit
        for i in range(n_qubits):
            # Variable to keep track of total phase to apply to the current qubit
            reciprocal_sum = 0
            # Loop over bits of c
            for j in range(n_qubits - 1 - i, -1, -1):
                # Action is controlled by value in current bit position of c
                if c & 2 ** j:
                    k = n_qubits - i - j
                    # Add effect of current bit of c to this qubit
                    reciprocal_sum += 2 ** -k
            # Apply the cumulative action of all bits of c to the current qubit
            self.u1(2 * math.pi * reciprocal_sum, self.qubits[i])


# Doubly controlled gate which maps QFT(b) to QFT((b + c) % n), where both c and n are
# constants compiled into the circuit
class CCModularFixedQFTAdder(qiskit.QuantumCircuit):
    def __init__(self, n_data_qubits, c, n):
        super().__init__(2 + n_data_qubits + 2, name=f'CCModularFixedQFTAdder({c}) mod {n}')

        # Construct the component gates needed
        fixed_adder_c = FixedQFTAdder(n_data_qubits + 1, c % n).to_gate()
        fixed_adder_n = FixedQFTAdder(n_data_qubits + 1, n).to_gate()
        qft = QFT(n_data_qubits + 1).to_gate()

        # First add c
        self.append(fixed_adder_c.control(2), self.qubits[:-1])

        # Subtract n
        self.append(fixed_adder_n.inverse(), self.qubits[2:-1])

        # Invert QFT in order to store state of most significant (carry) qubit in an ancilla qubit.
        # This records whether b + c - n is negative (i.e. whether b + c < n). Then restore QFT.
        self.append(qft.inverse(), self.qubits[2:-1])
        self.cx(self.qubits[-2], self.qubits[-1])
        self.append(qft, self.qubits[2:-1])

        # Add n back if b + c - n was negative
        self.append(fixed_adder_n.control(1), [self.qubits[-1]] + self.qubits[2:-1])

        # Subtract c
        self.append(fixed_adder_c.inverse().control(2), self.qubits[:-1])

        # Invert QFT to use most significant bit again to restore the last (ancilla) qubit to 0 if
        # it was flipped earlier. Then restore QFT.
        self.append(qft.inverse(), self.qubits[2:-1])
        self.x(self.qubits[-2])
        self.cx(self.qubits[-2], self.qubits[-1])
        self.x(self.qubits[-2])
        self.append(qft, self.qubits[2:-1])

        # Finally, add c back in
        self.append(fixed_adder_c.control(2), self.qubits[:-1])


class CPartialModularFixedMultiplier(qiskit.QuantumCircuit):
    def __init__(self, n_data_qubits, c, n):
        super().__init__(1 + 2 * n_data_qubits + 2,
                         name=f'CPartialModularFixedMultiplier({c}) mod {n}')
        qft = QFT(n_data_qubits + 1).to_gate()
        self.append(qft, self.qubits[-(n_data_qubits + 2):-1])
        for i in range(n_data_qubits):
            self.append(CCModularFixedQFTAdder(n_data_qubits, 2 ** i * c, n).to_gate(),
                        ([self.qubits[0]]
                         + [self.qubits[1 + i]]
                         + self.qubits[-(n_data_qubits + 2):]))
        self.append(qft.inverse(), self.qubits[-(n_data_qubits + 2):-1])


# Euclidean algorithm for finding modular inverse of a relative to n (such that a * a^-1 % n == 1)
def get_modular_inverse(a, n):
    t = 0
    new_t = 1
    r = n
    new_r = a

    while new_r != 0:
        q = r // new_r
        t, new_t = (new_t, t - q * new_t)
        r, new_r = (new_r, r - q * new_r)

    if r > 1:
        raise ValueError(f'{a} is not invertible relative to {n}')

    if t < 0:
        t += n

    return t


# Controlled gate which maps |b> to |b * c % n> where c and an are compiled into the circuit
class CModularFixedMultiplier(qiskit.QuantumCircuit):
    def __init__(self, n_data_qubits, c, n):
        super().__init__(1 + 2 * n_data_qubits + 2, name=f'CModularFixedMultiplier({c}) mod {n}')

        # Perform multiplication
        self.append(CPartialModularFixedMultiplier(n_data_qubits, c, n).to_gate(), self.qubits)

        # Need modular inverse of c in order to undo action on ancilla qubits
        c_inverse = get_modular_inverse(c, n)

        # SWAP qubits between data register and ancilla register
        for i in range(n_data_qubits):
            self.cswap(self.qubits[0], self.qubits[1 + i], self.qubits[1 + n_data_qubits + i])

        # Reversibly reset ancilla register to 0
        self.append(CPartialModularFixedMultiplier(n_data_qubits,
                                                   c_inverse,
                                                   n).to_gate().inverse(), self.qubits)


# Circuit which maps |a>|0> to |a>|x ** a % n>. x and n are compiled into the circuit.
class ModularFixedExponentiator(qiskit.QuantumCircuit):
    def __init__(self, n_exponent_qubits, n_base_qubits, x, n):
        super().__init__(n_exponent_qubits + 2 * n_base_qubits + 2,
                         name=f'ModularFixedExponentiator({x}) mod {n}')

        # Initialize result register to 1 before any multiplication
        self.x(self.qubits[n_exponent_qubits])

        # Loop over qubits of exponent register
        for i in range(n_exponent_qubits):
            # Multiply by x ** (2 ** i), controlled by current exponent qubit
            self.append(CModularFixedMultiplier(n_base_qubits, x ** (2 ** i), n).to_gate(),
                        [self.qubits[i]] + self.qubits[n_exponent_qubits:])
