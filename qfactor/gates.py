import math

import qiskit


def add_CRk(qc, k, control, target):
    qc.cu1(2 * math.pi / 2 ** k, control, target)


def reverse_qubits(qc):
    for i in range(qc.num_qubits // 2):
        qc.swap(i, qc.num_qubits - 1 - i)


class QFT(qiskit.QuantumCircuit):
    def __init__(self, n_qubits):
        super().__init__(n_qubits, name='QFT')
        for i in range(n_qubits - 1, -1, -1):
            self.h(i)
            for j in range(i - 1, -1, -1):
                k = i - j + 1
                add_CRk(self, k, j, i)
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
            if reciprocal_sum != 0:
                self.u1(2 * math.pi * reciprocal_sum, i)


class ModularFixedQFTAdder(qiskit.QuantumCircuit):
    def __init__(self, n_data_qubits, c, n):
        super().__init__(n_data_qubits + 2, name=f'ModularFixedQFTAdder({c}) mod {n}')
        fixed_adder_c = FixedQFTAdder(n_data_qubits + 1, c).to_gate()
        self.append(fixed_adder_c, self.qubits[:-1])
        fixed_adder_n = FixedQFTAdder(n_data_qubits + 1, n).to_gate()
        self.append(fixed_adder_n.inverse(), self.qubits[:-1])
        qft = QFT(n_data_qubits + 1).to_gate()
        self.append(qft.inverse(), self.qubits[:-1])
        self.cx(n_data_qubits, n_data_qubits + 1)
        self.append(qft, self.qubits[:-1])
        self.append(fixed_adder_n.control(1), [self.qubits[-1]] + self.qubits[:-1])
        self.append(fixed_adder_c.inverse(), self.qubits[:-1])
        self.append(qft.inverse(), self.qubits[:-1])
        self.x(n_data_qubits)
        self.cx(n_data_qubits, n_data_qubits + 1)
        self.x(n_data_qubits)
        self.append(qft, self.qubits[:-1])
        self.append(fixed_adder_c, self.qubits[:-1])


class PartialModularFixedMultiplier(qiskit.QuantumCircuit):
    def __init__(self, n_data_qubits, c, n):
        super().__init__(2 * n_data_qubits + 2, name=f'PartialModularFixedMultiplier({c}) mod {n}')
        qft = QFT(n_data_qubits + 1).to_gate()
        self.append(qft, self.qubits[n_data_qubits:-1])
        for i in range(n_data_qubits):
            self.append(ModularFixedQFTAdder(n_data_qubits, 2 ** i * c, n).to_gate().control(1),
                        [self.qubits[i]] + self.qubits[n_data_qubits:])
        self.append(qft.inverse(), self.qubits[n_data_qubits:-1])


def get_modular_inverse(a, n):
    t = 0
    newt = 1
    r = n
    newr = a

    while newr != 0:
        quotient = r // newr
        t, newt = (newt, t - quotient * newt)
        r, newr = (newr, r - quotient * newr)

    if r > 1:
        return "a is not invertible"
    if t < 0:
        t = t + n

    return t


class ModularFixedMultiplier(qiskit.QuantumCircuit):
    def __init__(self, n_data_qubits, c, n):
        super().__init__(2 * n_data_qubits + 2, name=f'ModularFixedMultiplier({c}) mod {n}')
        self.append(PartialModularFixedMultiplier(n_data_qubits, c, n).to_gate(), self.qubits)
        c_inverse = get_modular_inverse(c, n)
        for i in range(n_data_qubits):
            self.swap(i, i + n_data_qubits)
        self.append(PartialModularFixedMultiplier(n_data_qubits, c_inverse, n).to_gate().inverse(),
                    self.qubits)


class ModularFixedExponentiator(qiskit.QuantumCircuit):
    def __init__(self, n_exponent_qubits, n_base_qubits, x, n):
        super().__init__(n_exponent_qubits + 2 * n_base_qubits + 2,
                         name=f'ModularFixedExponentiator({x}) mod {n}')
        self.x(n_exponent_qubits)
        for i in range(n_exponent_qubits):
            self.append(ModularFixedMultiplier(n_base_qubits,
                                               x ** (2 ** i),
                                               n).to_gate().control(1),
                        [self.qubits[i]] + self.qubits[-(2 * n_base_qubits + 2):])
