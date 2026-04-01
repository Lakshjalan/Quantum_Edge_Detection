from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import RYGate
from quantumimageencoding.BaseQuantumEncoder import QuantumEncoder
# qiskit-aer is now a separate package; Aer moved from qiskit to qiskit_aer
from qiskit_aer import Aer
from PIL import Image
import numpy

class QPIE(QuantumEncoder):
    def __init__(self):
        super().__init__()

    def amplitudeEncoder(self, img : numpy.ndarray) :
        img = img.astype(numpy.float64)
        rms = numpy.sqrt(numpy.sum(numpy.sum(img**2, axis=1)))
        amplitudes = (img/rms).reshape(img.shape[0]**2)
        return amplitudes

    def encode(self, image) -> None :
        img = numpy.array(image)
        h_amplitudes = self.amplitudeEncoder(img)
        v_amplitudes = self.amplitudeEncoder(img.T)

        controlbits = int(2 * numpy.log2(img.shape[0]))
        unitaryMatrix = numpy.identity(2**(controlbits+1))
        unitaryMatrix = numpy.roll(unitaryMatrix,1,axis=1)

        self.Qcirc = QuantumCircuit(controlbits+1)
        self.Qcirc.initialize(h_amplitudes, range(1, controlbits+1))
        self.Qcirc.h(0)
        self.Qcirc.unitary(unitaryMatrix, range(controlbits+1))
        self.Qcirc.h(0)

        self.Qcirc2 = QuantumCircuit(controlbits+1)
        self.Qcirc2.initialize(v_amplitudes, range(1, controlbits+1))
        self.Qcirc2.h(0)
        self.Qcirc2.unitary(unitaryMatrix, range(controlbits+1))
        self.Qcirc2.h(0)

        return self.Qcirc

    def decode(self, simulator : str, shots: int = 2**16) -> Image.Image :
        pass

    def detectEdges(self) -> Image.Image:
        back = Aer.get_backend('statevector_simulator')
        # execute() removed in Qiskit 1.0; use backend.run() after transpile
        qc1 = transpile(self.Qcirc, back)
        qc2 = transpile(self.Qcirc2, back)
        state_vector_h = back.run(qc1).result().get_statevector(qc1)
        state_vector_v = back.run(qc2).result().get_statevector(qc2)
        size = int(2**((self.Qcirc.num_qubits-1)/2))
        threshold = lambda amp: (amp > 1e-15 or amp < -1e-15)
        h_edge_scan_img = numpy.abs(numpy.array([1 if threshold(state_vector_h[(2*i)+1].real) else 0 for i in range(2**(self.Qcirc.num_qubits-1))])).reshape(size, size)
        v_edge_scan_img = numpy.abs(numpy.array([1 if threshold(state_vector_v[(2*i)+1].real) else 0 for i in range(2**(self.Qcirc2.num_qubits-1))])).reshape(size, size).T
        edge_scan_image = h_edge_scan_img | v_edge_scan_img
        return edge_scan_image, h_edge_scan_img, v_edge_scan_img
