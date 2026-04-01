# Quantum Edge Detection — Tutorial

This tutorial walks you through running the project from scratch, understanding the outputs, customising inputs, and fixing common errors.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Getting the Code](#2-getting-the-code)
3. [Running on a Fresh Device (One Command)](#3-running-on-a-fresh-device-one-command)
4. [Running Manually (Step by Step)](#4-running-manually-step-by-step)
5. [Understanding the Output](#5-understanding-the-output)
6. [Using Your Own Image](#6-using-your-own-image)
7. [Running the Jupyter Notebook](#7-running-the-jupyter-notebook)
8. [Troubleshooting Common Errors](#8-troubleshooting-common-errors)
9. [How the Code Works (Technical Overview)](#9-how-the-code-works-technical-overview)

---

## 1. Prerequisites

All you need before you start:

| Requirement | Minimum Version | How to Check |
|---|---|---|
| Python | 3.8+ | `python --version` |
| pip | 21+ | `pip --version` |
| git | any | `git --version` |

> If Python is not installed, download it from [python.org](https://www.python.org/downloads/). Make sure to tick **"Add Python to PATH"** during installation on Windows.

---

## 2. Getting the Code

Open a terminal (Command Prompt / PowerShell on Windows, Terminal on macOS/Linux) and run:

```bash
git clone https://github.com/AJAX-ed/Quantum_Edge_Detection.git
cd Quantum_Edge_Detection
```

Or download the ZIP from GitHub and extract it.

---

## 3. Running on a Fresh Device (One Command)

This is the **recommended way**. It works whether you have never installed any of the libraries before or not.

```bash
python run.py
```

That is it. `run.py` will:

1. Upgrade `pip` to the latest version
2. Check each required library one by one
3. Install any library that is missing (using `pip` automatically)
4. Verify that Qiskit and Qiskit-Aer are API-compatible
5. Launch `main.py`

You will see output like this in your terminal:

```
============================================================
  Quantum Edge Detection  -  Dependency Checker
============================================================

[Step 1] Upgrading pip...
  pip is up to date.

[Step 2] Checking dependencies...
  [OK]     qiskit
  [OK]     qiskit_aer
  [MISSING] numpy  ->  will install numpy>=1.24.0
  [install] pip install numpy>=1.24.0
  ...

[Step 3] Installing 3 missing package(s)...
  All packages installed successfully!

[Step 4] Verifying Qiskit API compatibility...
  [OK] Qiskit + Aer API is compatible.

============================================================
  All checks passed. Launching the project...
============================================================
```

After that, `main.py` starts automatically.

---

## 4. Running Manually (Step by Step)

### Step 1 — Create a virtual environment (recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages. It may take a few minutes on the first run.

### Step 3 — Run the project

```bash
python main.py
```

---

## 5. Understanding the Output

When the project runs, it produces several matplotlib windows in sequence. **Close each window to proceed to the next one.**

### Window 1 — QPIE Circuit Diagram

Shows the full quantum circuit built by the QPIE (Quantum Probability Image Encoding) encoder for the 4×4 test image. Each column of gates represents one step of the encoding.

### Window 2 — QPIE Edge Detection (4-panel plot)

| Panel | What it shows |
|---|---|
| Original Image | The input 4×4 binary pattern |
| H-Edges (QPIE) | Edges detected in the horizontal direction |
| V-Edges (QPIE) | Edges detected in the vertical direction |
| Combined Edges (QPIE) | Logical OR of H-Edges and V-Edges |

### Window 3 — FRQI Circuit Diagram

Same as Window 1 but for the FRQI (Flexible Representation of Quantum Images) encoder. FRQI encodes pixel values as rotation angles.

### Window 4 — FRQI Edge Detection (4-panel plot)

Same four-panel format as Window 2 but using the FRQI encoder.

### Window 5 — Comparison Summary (`showdiff`)

Shows the original image, the QPIE edge result, and the FRQI edge result side by side for easy comparison.

---

## 6. Using Your Own Image

By default, the project uses a hardcoded 4×4 array. To use a real grayscale image:

1. Put your image in the `assets/images/` folder (e.g. `myimage.png`)
2. Open `main.py` in any text editor
3. Find the commented-out lines near the top:

```python
# from quantumimageencoding.QPIE import QPIE as _tmp
# _enc = _tmp()
# arr = numpy.array(_enc.preProcessImage(Image.open('./assets/images/test4edges.png').convert('L')), dtype=float)
```

4. Uncomment those three lines and change the filename to your image:

```python
from quantumimageencoding.QPIE import QPIE as _tmp
_enc = _tmp()
arr = numpy.array(_enc.preProcessImage(Image.open('./assets/images/myimage.png').convert('L')), dtype=float)
```

5. Comment out or remove the hardcoded `arr = numpy.array([...])` block above it
6. Save and run `python main.py` (or `python run.py`)

> **Important:** The image will be automatically resized to the nearest 2ⁿ × 2ⁿ square. Larger images need exponentially more qubits and will be much slower to simulate.

---

## 7. Running the Jupyter Notebook

The notebook version is great for exploring step by step:

```bash
pip install notebook
jupyter notebook Quantum_Edge_Detection.ipynb
```

Your browser will open automatically. Click through each cell with **Shift + Enter**.

---

## 8. Troubleshooting Common Errors

### `ModuleNotFoundError: No module named 'qiskit_aer'`

Since Qiskit 1.0, the Aer simulator is a **separate package**. Install it:

```bash
pip install qiskit-aer>=0.14.0
```

### `ModuleNotFoundError: No module named 'quantumimageencoding'`

This usually means you are running `python main.py` from the wrong directory. Make sure you are inside the `Quantum_Edge_Detection` folder:

```bash
cd Quantum_Edge_Detection
python main.py
```

### `ImportError: cannot import name 'execute' from 'qiskit'`

The `execute()` function was removed in Qiskit 1.0. All files in this repo have been fixed to use `transpile()` + `backend.run()` instead. Make sure you have the latest code from this repo.

### `AttributeError: 'QuantumCircuit' object has no attribute 'c_if'` or similar

Again this is a Qiskit 1.0 API change — `c_if` was removed. The code in this repo uses `if_test()` context manager instead. Pull the latest code.

### `ValueError: multichannel` (scikit-image error)

Newer versions of scikit-image replaced `multichannel=False` with `channel_axis=None`. This has been fixed in `BaseQuantumEncoder.py`. Make sure you have the latest code.

### Plots are not showing / window freezes

Close the current matplotlib window to proceed to the next step. The script pauses at each `plt.show()` call until you close the window.

### Everything installs but the circuit simulation is very slow

This is expected. Quantum simulation is exponential in the number of qubits. The default 4×4 image uses ~5 qubits (QPIE) and is fast. A real 64×64 image would use ~13 qubits and take significantly longer on a CPU simulator.

---

## 9. How the Code Works (Technical Overview)

### File Roles

| File | Role |
|---|---|
| `run.py` | Launcher — installs dependencies, then runs main.py |
| `main.py` | Entry point — demonstrates QPIE and FRQI encoding + edge detection |
| `utils.py` | `showdiff()` — displays images side by side and computes MSE/SSIM |
| `quantumimageencoding/BaseQuantumEncoder.py` | Abstract base class with shared methods (preprocess, MSE, SSIM) |
| `quantumimageencoding/QPIE.py` | QPIE encoder — encodes pixels as probability amplitudes |
| `quantumimageencoding/FRQI.py` | FRQI encoder — encodes pixels as RY rotation angles |

### Encoding Flow (QPIE)

1. **Amplitude encoding**: pixel values are normalised so `sum(values²) = 1`, then loaded as the initial state vector of `2·log₂(N)` qubits
2. **QHED**: a Hadamard gate on qubit 0 + a cyclic unitary shift + another Hadamard create interference that highlights differences between adjacent pixels
3. **Read-out**: the imaginary-odd-index amplitudes of the final statevector above a threshold are 1 (edge) or 0 (no edge)

### Encoding Flow (FRQI)

1. **Angle encoding**: each pixel intensity `p` is mapped to an angle `θ = arcsin(p)`, then encoded as a controlled-RY rotation
2. The Gray-code ordering of pixel positions minimises the number of X gates needed between consecutive controlled rotations
3. **QHED** is then applied identically to the QPIE case

### Why 2ⁿ × 2ⁿ Only?

Quantum image encoding requires an exact power-of-two number of pixels so that the position register has an integer number of qubits. The `preProcessImage()` method pads the image with zeros to achieve this.
