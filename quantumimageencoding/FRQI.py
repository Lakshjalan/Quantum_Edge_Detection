from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, transpile
from qiskit.circuit.library import RYGate
from quantumimageencoding.BaseQuantumEncoder import QuantumEncoder
# qiskit-aer is now a separate package; Aer moved from qiskit to qiskit_aer in Qiskit 1.0+
from qiskit_aer import Aer
from PIL import Image
import numpy

class FRQI(QuantumEncoder):
    def __init__(self):
        super().__init__()

    def encode(self, image) -> QuantumCircuit:
        '''
        Encodes the corresponding angle values of each pixel
        onto two Quantum Circuits (horizontal + vertical scan).
        Accepts a PIL Image, numpy array, or nested list.
        '''
        img_array = numpy.array(image, dtype=float)
        angles_h = numpy.arcsin(img_array)
        angles_h = angles_h.reshape(angles_h.shape[0]**2)
        angles_v = numpy.arcsin(img_array.T)
        angles_v = angles_v.reshape(angles_v.shape[0]**2)

        controlbits = int(numpy.log2(angles_h.shape[0]))
        positions1 = QuantumRegister(controlbits, 'position')
        target1    = QuantumRegister(1, 'target')
        classical1 = ClassicalRegister(controlbits + 1, 'measure')
        positions2 = QuantumRegister(controlbits, 'position')
        target2    = QuantumRegister(1, 'target')
        classical2 = ClassicalRegister(controlbits + 1, 'measure')
        self.Qcirc  = self.createQuantumCircuit(target1, positions1, classical1)
        self.Qcirc2 = self.createQuantumCircuit(target2, positions2, classical2)

        # Apply Hadamard to all position qubits
        for i in range(1, controlbits + 1):
            self.Qcirc.h(i)
            self.Qcirc2.h(i)

        # Encode horizontal angles
        j = 0
        for angle in angles_h:
            state     = '{0:0{1}b}'.format(j - 1, controlbits)
            new_state = '{0:0{1}b}'.format(j, controlbits)
            if j != 0:
                c = numpy.array([])
                for k in range(controlbits):
                    if state[k] != new_state[k]:
                        c = numpy.append(c, int(k))
                if len(c) > 0:
                    self.Qcirc.x(numpy.abs(c.astype(int) - controlbits).tolist())
                cry = RYGate(2 * angle).control(controlbits)
                aux = [k + 1 for k in range(controlbits)] + [0]
                self.Qcirc.append(cry, aux)
            j += 1

        self.Qcirc.measure(0, 0)
        # c_if is removed in Qiskit 1.0; use if_test context manager instead
        with self.Qcirc.if_test((classical1, 0)):
            self.Qcirc.x(target1[0])

        # Encode vertical angles
        j = 0
        for angle in angles_v:
            state     = '{0:0{1}b}'.format(j - 1, controlbits)
            new_state = '{0:0{1}b}'.format(j, controlbits)
            if j != 0:
                c = numpy.array([])
                for k in range(controlbits):
                    if state[k] != new_state[k]:
                        c = numpy.append(c, int(k))
                if len(c) > 0:
                    self.Qcirc2.x(numpy.abs(c.astype(int) - controlbits).tolist())
                cry = RYGate(2 * angle).control(controlbits)
                aux = [k + 1 for k in range(controlbits)] + [0]
                self.Qcirc2.append(cry, aux)
            j += 1

        self.Qcirc2.measure(0, 0)
        with self.Qcirc2.if_test((classical2, 0)):
            self.Qcirc2.x(target2[0])

        # QHED unitary shift operator
        unitaryMatrix = numpy.identity(2 ** (controlbits + 1))
        unitaryMatrix = numpy.roll(unitaryMatrix, 1, axis=1)
        self.Qcirc.h(0)
        self.Qcirc.unitary(unitaryMatrix, list(range(controlbits + 1)))
        self.Qcirc.h(0)
        self.Qcirc2.h(0)
        self.Qcirc2.unitary(unitaryMatrix, list(range(controlbits + 1)))
        self.Qcirc2.h(0)

        return self.Qcirc

    def detectEdges(self):
        '''
        Runs both circuits on the Aer statevector simulator
        and returns (combined_edge_image, h_edges, v_edges).
        '''
        back = Aer.get_backend('statevector_simulator')
        # execute() was removed in Qiskit 1.0; use transpile + backend.run()
        qc1 = transpile(self.Qcirc,  back)
        qc2 = transpile(self.Qcirc2, back)
        sv_h = back.run(qc1).result().get_statevector(qc1)
        sv_v = back.run(qc2).result().get_statevector(qc2)

        size = int(2 ** ((self.Qcirc.num_qubits - 1) / 2))
        threshold = lambda amp: (amp > 1e-15 or amp < -1e-15)

        h_edge = numpy.abs(numpy.array(
            [1 if threshold(sv_h[(2 * i) + 1].real) else 0
             for i in range(2 ** (self.Qcirc.num_qubits - 1))]
        )).reshape(size, size)

        v_edge = numpy.abs(numpy.array(
            [1 if threshold(sv_v[(2 * i) + 1].real) else 0
             for i in range(2 ** (self.Qcirc2.num_qubits - 1))]
        )).reshape(size, size).T

        combined = h_edge | v_edge
        return combined, h_edge, v_edge
