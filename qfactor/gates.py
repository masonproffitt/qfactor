import math

import qiskit


def get_min_n_bits_for_modulus(modulus):
    if modulus == 1:
        return 1
    else:
        return math.ceil(math.log2(modulus))


def get_min_n_bits_for_value(value):
    return get_min_n_bits_for_modulus(value + 1)


def initialize_to_value(circuit, value):
    for i in range(get_min_n_bits_for_value(value)):
        if value & 2 ** i:
            circuit.x(i)


class Rk(qiskit.circuit.library.U1Gate):
    def __init__(self, k):
        super().__init__(2 * math.pi / 2 ** k, label=f'R_{k}')


def reverse_qubits(circuit):
    for i in range(circuit.num_qubits // 2):
        circuit.swap(i, circuit.num_qubits - 1 - i)


class QFT(qiskit.QuantumCircuit):
    def __init__(self, n_qubits):
        super().__init__(n_qubits, name='QFT')
        for i in range(n_qubits - 1, -1, -1):
            self.h(i)
            for j in range(i - 1, -1, -1):
                k = i - j + 1
                self.append(Rk(k).control(1), [self.qubits[j], self.qubits[i]])
        reverse_qubits(self)


class FixedQFTAdder(qiskit.QuantumCircuit):
    def __init__(self, n_qubits, c):
        super().__init__(n_qubits, name=f'FixedQFTAdder({c})')
        for i in range(n_qubits):
            reciprocal_sum = 0
            for j in range(n_qubits - 1 - i, -1, -1):
                if c & 2 ** j:
                    k = n_qubits - i - j
                    reciprocal_sum += 2 ** -k
            reciprocal_sum = reciprocal_sum % (2 * math.pi)
            self.u1(2 * math.pi * reciprocal_sum, self.qubits[i])


class CCModularFixedQFTAdder(qiskit.QuantumCircuit):
    def __init__(self, n_data_qubits, c, n):
        super().__init__(2 + n_data_qubits + 2, name=f'CCModularFixedQFTAdder({c}) mod {n}')
        fixed_adder_c = FixedQFTAdder(n_data_qubits + 1, c % n).to_gate()
        self.append(fixed_adder_c.control(2), self.qubits[:-1])
        fixed_adder_n = FixedQFTAdder(n_data_qubits + 1, n).to_gate()
        self.append(fixed_adder_n.inverse(), self.qubits[2:-1])
        qft = QFT(n_data_qubits + 1).to_gate()
        self.append(qft.inverse(), self.qubits[2:-1])
        self.cx(self.qubits[-2], self.qubits[-1])
        self.append(qft, self.qubits[2:-1])
        self.append(fixed_adder_n.control(1), [self.qubits[-1]] + self.qubits[2:-1])
        self.append(fixed_adder_c.inverse().control(2), self.qubits[:-1])
        self.append(qft.inverse(), self.qubits[2:-1])
        self.x(self.qubits[-2])
        self.cx(self.qubits[-2], self.qubits[-1])
        self.x(self.qubits[-2])
        self.append(qft, self.qubits[2:-1])
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


class CModularFixedMultiplier(qiskit.QuantumCircuit):
    def __init__(self, n_data_qubits, c, n):
        super().__init__(1 + 2 * n_data_qubits + 2, name=f'CModularFixedMultiplier({c}) mod {n}')
        self.append(CPartialModularFixedMultiplier(n_data_qubits, c, n).to_gate(), self.qubits)
        c_inverse = get_modular_inverse(c, n)
        for i in range(n_data_qubits):
            self.cswap(self.qubits[0], self.qubits[1 + i], self.qubits[1 + n_data_qubits + i])
        self.append(CPartialModularFixedMultiplier(n_data_qubits,
                                                   c_inverse,
                                                   n).to_gate().inverse(), self.qubits)


class ModularFixedExponentiator(qiskit.QuantumCircuit):
    def __init__(self, n_exponent_qubits, n_base_qubits, x, n):
        super().__init__(n_exponent_qubits + 2 * n_base_qubits + 2,
                         name=f'ModularFixedExponentiator({x}) mod {n}')
        self.x(self.qubits[n_exponent_qubits])
        for i in range(n_exponent_qubits):
            self.append(CModularFixedMultiplier(n_base_qubits, x ** (2 ** i), n).to_gate(),
                        [self.qubits[i]] + self.qubits[n_exponent_qubits:])
