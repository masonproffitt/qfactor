# qfactor

This project is intended to implement Shor's algorithm for factorization with a quantum computer. The quantum operations are simulated via [Qiskit](https://qiskit.org).

The primary function in the package is `factorize()`, which decomposes a positive integer into two factors. For example:

```python
import qfactor

qfactor.factorize(15)
```

Final output:

```
(3, 5)
```
