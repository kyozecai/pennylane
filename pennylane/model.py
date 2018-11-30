# Copyright 2018 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# pylint: disable=protected-access
r"""
Models
======

**Module name:** :mod:`pennylane.model`

.. currentmodule:: pennylane.model

This module provides functions representing  circuits of common quantum
machine learning architectures to make it easy to use them as building blocks
for quantum machine learning models.

For example, you can define and call a circuit-centric quantum classifier
:cite:`schuld2018circuit`on an arbitrary number of wires and with an arbitrary
number of blocks in the following way:

.. code-block:: python

    import pennylane as qml
    from pennylane import numpy as np

    num_wires=4
    num_blocks=3
    dev = qml.device('default.qubit', wires=num_wires)

    @qml.qnode(dev)
    def circuit(weights, x=None):
        qml.BasisState(x, wires=range(num_wires))
        qml.model.CircuitCentricClassifier(weights, periodic=True, wires=range(num_wires))
        return qml.expval.PauliZ(0)

    np.random.seed(0)
    weights=np.random.randn(num_blocks, num_wires, 3)
    print(circuit(weights, x=np.array(np.random.randint(0,1,num_wires))))


Summary
^^^^^^^

.. autosummary::
  variational_quantum_classifyer

Code details
^^^^^^^^^^^^
"""
import logging as log
import pennylane as qml

log.getLogger()

def CircuitCentricClassifier(weights, periodic=True, ranges=None, wires=None):
    """A circuit-centric classifier circuit.

    Constructs a circuit-centric quantum classifier :cite:`schuld2018circuit`
    with len(weights) blocks on the given wires with the provided weights.
    Each element of weights must be a an array of size len(wires)*3.

    Args:
        weights (array[float]): number of blocks*len(wires)*3 array of weights
        periodic (bool): whether to use periodic boundary conditions when
                         applying controlled gates
        ranges (Sequence[int]): the ranges of the controlled gates in the
                                respective blocks
        wires (Sequence[int]): the wires the model acts on
    """
    if ranges is None:
        ranges = [1]*len(weights)
    for block_weights, block_range in zip(weights, ranges):
        CircuitCentricClassifierBlock(block_weights, block_range, periodic, wires)


def CircuitCentricClassifierBlock(weights, periodic=True, r=1, wires=None):
    """A block of a circuit-centric classifier circuit.

    Args:
        weights (array[float]): len(wires)*3 array of weights
        periodic (bool): whether to use periodic boundary conditions when
                         applying controlled gates
        r (Sequence[int]): the ranges of the controlled gates of this block
        wires (Sequence[int]): the wires the model acts on
    """
    for i, wire in enumerate(wires):
        qml.ops.Rot(weights[i, 0], weights[i, 1], weights[i, 2], wires=wire)

    num_wires = len(wires)
    for i in range(num_wires) if periodic else range(num_wires-1):
        qml.ops.CNOT(wires=[wires[i], wires[(i+r) % num_wires]])
