import cmath

import qiskit

from qfactor.gates import *


backend = qiskit.Aer.get_backend('statevector_simulator')


def run(circuit):
    job = qiskit.execute(circuit, backend)
    result = job.result()
    statevector = result.get_statevector(circuit)
    return statevector


def test_get_min_n_bits_for_modulus():
    assert get_min_n_bits_for_modulus(1) == 1
    assert get_min_n_bits_for_modulus(2) == 1
    assert get_min_n_bits_for_modulus(3) == 2


def test_get_min_n_bits_for_value():
    assert get_min_n_bits_for_value(0) == 1
    assert get_min_n_bits_for_value(1) == 1
    assert get_min_n_bits_for_value(2) == 2


def test_initialize_to_value_1bit():
    qc = qiskit.QuantumCircuit(1)
    initialize_to_value(qc, 1)
    assert abs(run(qc)[1]) == 1


def test_initialize_to_value_2bits():
    qc = qiskit.QuantumCircuit(2)
    initialize_to_value(qc, 2)
    assert abs(run(qc)[2]) == 1


def test_Rk():
    qc = qiskit.QuantumCircuit(1)
    initialize_to_value(qc, 1)
    qc.append(Rk(1), qc.qubits)
    assert cmath.phase(run(qc)[1]) == 2 * math.pi / 2 ** 1
    qc = qiskit.QuantumCircuit(1)
    initialize_to_value(qc, 1)
    qc.append(Rk(2), qc.qubits)
    assert cmath.phase(run(qc)[1]) == 2 * math.pi / 2 ** 2
    qc = qiskit.QuantumCircuit(1)
    initialize_to_value(qc, 1)
    qc.append(Rk(3), qc.qubits)
    assert cmath.phase(run(qc)[1]) == 2 * math.pi / 2 ** 3


def test_reverse_qubits_1bit():
    qc = qiskit.QuantumCircuit(1)
    reverse_qubits(qc)
    assert abs(run(qc)[0]) == 1


def test_reverse_qubits_2bits():
    qc = qiskit.QuantumCircuit(2)
    qc.x(qc.qubits[0])
    reverse_qubits(qc)
    assert abs(run(qc)[2]) == 1


def test_reverse_qubits_3bits():
    qc = qiskit.QuantumCircuit(3)
    qc.x(qc.qubits[2])
    reverse_qubits(qc)
    assert abs(run(qc)[1]) == 1


def test_reverse_qubits_4bits():
    qc = qiskit.QuantumCircuit(4)
    qc.x(qc.qubits[0])
    qc.x(qc.qubits[2])
    reverse_qubits(qc)
    assert abs(run(qc)[10]) == 1


def test_QFT_1bit():
    qc = qiskit.QuantumCircuit(1)
    qc.append(QFT(qc.num_qubits), qc.qubits)
    statevector = run(qc)
    assert cmath.phase(statevector[0]) == 0
    assert cmath.isclose(statevector[1], statevector[0])


def test_QFT_2bits():
    qc = qiskit.QuantumCircuit(2)
    initialize_to_value(qc, 1)
    qc.append(QFT(qc.num_qubits), qc.qubits)
    statevector = run(qc)
    assert abs(cmath.phase(statevector[0])) < 1e-9
    assert cmath.isclose(cmath.phase(statevector[1]), math.pi / 2)
    assert cmath.isclose(abs(cmath.phase(statevector[2])), math.pi)
    assert cmath.isclose(cmath.phase(statevector[3]), -math.pi / 2)


def test_FixedQFTAdder_1bit():
    qc = qiskit.QuantumCircuit(1)
    qc.append(QFT(qc.num_qubits), qc.qubits)
    qc.append(FixedQFTAdder(qc.num_qubits, 1), qc.qubits)
    qc.append(QFT(qc.num_qubits).inverse(), qc.qubits)
    assert abs(run(qc)[1]) == 1


def test_FixedQFTAdder_2bits():
    qc = qiskit.QuantumCircuit(2)
    initialize_to_value(qc, 1)
    qc.append(QFT(qc.num_qubits), qc.qubits)
    qc.append(FixedQFTAdder(qc.num_qubits, 2), qc.qubits)
    qc.append(QFT(qc.num_qubits).inverse(), qc.qubits)
    assert abs(run(qc)[3]) == 1


def test_CCModularFixedQFTAdder_control_off():
    qc = qiskit.QuantumCircuit(5)
    qc.append(QFT(2), qc.qubits[2:-1])
    qc.append(CCModularFixedQFTAdder(1, 1, 2), qc.qubits)
    qc.append(QFT(2).inverse(), qc.qubits[2:-1])
    assert abs(run(qc)[0]) == 1
    qc = qiskit.QuantumCircuit(5)
    qc.x(qc.qubits[0])
    qc.append(QFT(2), qc.qubits[2:-1])
    qc.append(CCModularFixedQFTAdder(1, 1, 2), qc.qubits)
    qc.append(QFT(2).inverse(), qc.qubits[2:-1])
    assert abs(run(qc)[1]) == 1
    qc = qiskit.QuantumCircuit(5)
    qc.x(qc.qubits[1])
    qc.append(QFT(2), qc.qubits[2:-1])
    qc.append(CCModularFixedQFTAdder(1, 1, 2), qc.qubits)
    qc.append(QFT(2).inverse(), qc.qubits[2:-1])
    assert abs(run(qc)[2]) == 1


def test_CCModularFixedQFTAdder_control_on():
    qc = qiskit.QuantumCircuit(6)
    qc.x(qc.qubits[0])
    qc.x(qc.qubits[1])
    qc.x(qc.qubits[3])
    qc.append(QFT(3), qc.qubits[2:-1])
    qc.append(CCModularFixedQFTAdder(2, 2, 3), qc.qubits)
    qc.append(QFT(3).inverse(), qc.qubits[2:-1])
    assert abs(run(qc)[7]) == 1


def test_CPartialModularFixedMultiplier_control_off():
    qc = qiskit.QuantumCircuit(5)
    qc.x(qc.qubits[1])
    qc.append(CPartialModularFixedMultiplier(1, 1, 2), qc.qubits)
    assert abs(run(qc)[2]) == 1


def test_CPartialModularFixedMultiplier_control_on():
    qc = qiskit.QuantumCircuit(9)
    qc.x(qc.qubits[0])
    qc.x(qc.qubits[2])
    qc.x(qc.qubits[4])
    qc.append(CPartialModularFixedMultiplier(3, 3, 5), qc.qubits)
    assert cmath.isclose(abs(run(qc)[37]), 1)


def test_get_modular_inverse():
    assert get_modular_inverse(2, 5) == 3
    assert get_modular_inverse(3, 5) == 2
    assert get_modular_inverse(2, 7) == 4


def test_CModularFixedMultiplier_control_off():
    qc = qiskit.QuantumCircuit(7)
    qc.x(qc.qubits[1])
    qc.append(CModularFixedMultiplier(2, 2, 3), qc.qubits)
    assert cmath.isclose(abs(run(qc)[2]), 1)


def test_CModularFixedMultiplier_control_on():
    qc = qiskit.QuantumCircuit(9)
    qc.x(qc.qubits[0])
    qc.x(qc.qubits[2])
    qc.append(CModularFixedMultiplier(3, 3, 5), qc.qubits)
    assert cmath.isclose(abs(run(qc)[3]), 1)


def test_ModularFixedExponentiator():
    qc = qiskit.QuantumCircuit(8)
    qc.x(qc.qubits[0])
    qc.x(qc.qubits[1])
    qc.append(ModularFixedExponentiator(2, 2, 2, 3), qc.qubits)
    assert cmath.isclose(abs(run(qc)[11]), 1)
