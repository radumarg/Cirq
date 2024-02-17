# Copyright 2024 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Target gateset used for compiling circuits to IonQ native gates."""
import cirq
import numpy as np

from cirq import linalg
from cirq.linalg.tolerance import near_zero_mod
from cirq import ops

from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from .ionq_native_gates import GPIGate, GPI2Gate, MSGate, ZZGate, VirtualZGate

class IonqNativeGatesetBase(cirq.TwoQubitCompilationTargetGateset):
    """Base class for IonQ native gate sets.
    """

    def _decompose_single_qubit_operation(self, op: cirq.Operation, _) -> cirq.OP_TREE:
        qubit = op.qubits[0]
        mat = cirq.unitary(op)
        for gate in _single_qubit_matrix_to_gates(mat, self.atol):
            yield gate(qubit)

    def _decompose_two_qubit_operation(self, op: cirq.Operation, _) -> cirq.OP_TREE:
        raise Exception()
    
    # TODO - implement
    def _decompose_multi_qubit_operation(self, op: 'cirq.Operation', moment_idx: int) -> cirq.OP_TREE:
        raise Exception()

    @property
    def postprocess_transformers(self) -> List['cirq.TRANSFORMER']:
        """List of transformers which should be run after decomposing individual operations."""
        return [cirq.drop_negligible_operations, cirq.drop_empty_moments]

    def _value_equality_values_(self) -> Any:
        return self.atol

    def _json_dict_(self) -> Dict[str, Any]:
        return cirq.obj_to_dict_helper(self, ['atol'])

    @classmethod
    def _from_json_dict_(cls, atol, **kwargs):
        return cls(atol=atol)


class AriaNativeGateset(IonqNativeGatesetBase):
    """Target IonQ native gateset for compiling circuits.

    The gates forming this gateset are: 
    GPIGate, GPI2Gate, MSGate and VirtualZGate
    """

    def __init__(self, *, atol: float = 1e-8):
        """Initializes AriaNativeGateset

        Args:
            atol: A limit on the amount of absolute error introduced by the decomposition.
        """
        super().__init__(
            GPIGate,
            GPI2Gate,
            MSGate,
            #VirtualZGate,
            ops.MeasurementGate,
            unroll_circuit_op=False,
        )
        self.atol = atol

    def __repr__(self) -> str:
        return f'cirq_ionq.AriaNativeGateset(atol={self.atol})'


class ForteNativeGateset(IonqNativeGatesetBase):
    """Target IonQ native gateset for compiling circuits.

    The gates forming this gateset are:
    GPIGate, GPI2Gate, MSGate, ZZGate and VirtualZGate
    """

    def __init__(self, *, atol: float = 1e-8):
        """Initializes ForteNativeGateset

        Args:
            atol: A limit on the amount of absolute error introduced by the decomposition.
        """
        super().__init__(
            GPIGate,
            GPI2Gate,
            MSGate,
            ZZGate,
            #VirtualZGate,
            ops.MeasurementGate,
            unroll_circuit_op=False,
        )
        self.atol = atol

    def __repr__(self) -> str:
        return f'cirq_ionq.ForteNativeGateset(atol={self.atol})'
    

def _single_qubit_matrix_to_gates(mat: np.ndarray, tolerance: float) -> List[cirq.Gate]:
    """Implements a single-qubit operation with few gates.
       Code is based on existing implementation from Cirq core.

    Args:
        mat: The 2x2 unitary matrix of the operation to implement.
        tolerance: A limit on the amount of error introduced by the
            construction.

    Returns:
        A list of gates that, when applied in order, perform the desired
            operation.
    """
    rotations = _single_qubit_matrix_to_pauli_rotations(mat, tolerance)
    return [pauli**ht for pauli, ht in rotations]


def _single_qubit_matrix_to_pauli_rotations(mat: np.ndarray, atol: float) -> List[Tuple[cirq.Gate, float]]:
    """Implements a single-qubit operation with few rotations.
       Code is based on existing implementation from Cirq core.

    Args:
        mat: The 2x2 unitary matrix of the operation to implement.
        atol: A limit on the amount of absolute error introduced by the
            construction.

    Returns:
        A list of (Pauli, half_turns) tuples that, when applied in order,
        perform the desired operation.
    """

    def is_clifford_rotation(half_turns):
        return near_zero_mod(half_turns, 0.5, atol=atol)

    def to_quarter_turns(half_turns):
        return round(2 * half_turns) % 4

    def is_quarter_turn(half_turns):
        return is_clifford_rotation(half_turns) and to_quarter_turns(half_turns) % 2 == 1

    def is_half_turn(half_turns):
        return is_clifford_rotation(half_turns) and to_quarter_turns(half_turns) == 2

    def is_no_turn(half_turns):
        return is_clifford_rotation(half_turns) and to_quarter_turns(half_turns) == 0

    # Decompose matrix
    z_rad_before, y_rad, z_rad_after = linalg.deconstruct_single_qubit_matrix_into_angles(mat)
    z_ht_before = z_rad_before / np.pi - 0.5
    m_ht = y_rad / np.pi
    m_pauli = GPIGate(phi=0)
    z_ht_after = z_rad_after / np.pi + 0.5
    
    # Clean up angles
    if is_clifford_rotation(z_ht_before):
        if (is_quarter_turn(z_ht_before) or is_quarter_turn(z_ht_after)) ^ (
            is_half_turn(m_ht) and is_no_turn(z_ht_before - z_ht_after)
        ):
            z_ht_before += 0.5
            z_ht_after -= 0.5
            m_pauli = GPIGate(phi=np.pi/2)
        if is_half_turn(z_ht_before) or is_half_turn(z_ht_after):
            z_ht_before -= 1
            z_ht_after += 1
            m_ht = -m_ht
    if is_no_turn(m_ht):
        z_ht_before += z_ht_after
        z_ht_after = 0
    elif is_half_turn(m_ht):
        z_ht_after -= z_ht_before
        z_ht_before = 0

    # Generate operations
    #rotation_list = [(ops.Z, z_ht_before), (m_pauli, m_ht), (ops.Z, z_ht_after)] !!
    #rotation_list = [(VirtualZGate(theta=np.pi), z_ht_before), (m_pauli, m_ht), (VirtualZGate(theta=np.pi), z_ht_after)]
    rotation_list = [(m_pauli, m_ht)]
    return [(pauli, ht) for pauli, ht in rotation_list if not is_no_turn(ht)]