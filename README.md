<div align="center">

![Quantum_Edge_Detection](assets/images/Logo.png)

![Python](https://img.shields.io/badge/Python-3670A0?logo=python&logoColor=ffdd54)
![Qiskit](https://img.shields.io/badge/Qiskit-%236929C4.svg?logo=Qiskit&logoColor=white)
![Last Commit](https://img.shields.io/github/last-commit/AJAX-ed/Quantum_Edge_Detection)
![Issues](https://img.shields.io/github/issues/AJAX-ed/Quantum_Edge_Detection)
![Contributors](https://img.shields.io/github/contributors/AJAX-ed/Quantum_Edge_Detection)
![Stars](https://img.shields.io/github/stars/AJAX-ed/Quantum_Edge_Detection)

</div>

---

# Quantum Edge Detection

Quantum Edge Detection using three different Quantum Image Encoding strategies:

| Encoding | Description |
|---|---|
| **FRQI** | Flexible Representation of Quantum Images |
| **NEQR** | Novel Enhanced Quantum Representation |
| **QPIE** | Quantum Probability Image Encoding |

All three encoders feed into a modified **Quantum Hadamard Edge Detection (QHED)** algorithm to extract edges from images on a quantum circuit simulator.

This is the 7th semester project for **CS4084 – Quantum Computing** at university.

---

## Project Structure

```
Quantum_Edge_Detection/
├── run.py                         # ONE-CLICK launcher (auto-installs deps + runs project)
├── main.py                        # Main demo script (QPIE + FRQI encoding + edge detection)
├── utils.py                       # Helper: showdiff() for side-by-side image comparison
├── requirements.txt               # Python dependencies
├── quantumimageencoding/
│   ├── __init__.py                # Package marker
│   ├── BaseQuantumEncoder.py      # Abstract base class for all encoders
│   ├── FRQI.py                    # FRQI encoder + QHED edge detection
│   └── QPIE.py                    # QPIE encoder + QHED edge detection
├── assets/images/                 # Logo and sample images
├── documentation/                 # Project documentation
└── Quantum_Edge_Detection.ipynb   # Jupyter Notebook version (recommended for exploration)
```

---

## Quick Start — One Click

> **The easiest way to run the project on any machine (fresh or existing):**

```bash
python run.py
```

`run.py` will:
1. Upgrade `pip` automatically
2. Check every required library and install any that are missing
3. Verify Qiskit API compatibility
4. Launch `main.py`

You **only need Python 3.8+** installed. Everything else is handled automatically.

---

## Manual Setup

If you prefer to set things up yourself:

```bash
# 1. Clone the repo
git clone https://github.com/AJAX-ed/Quantum_Edge_Detection.git
cd Quantum_Edge_Detection

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate          # Linux / macOS
venv\Scripts\activate             # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the project
python main.py
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `qiskit >= 1.0.0` | Quantum circuit construction |
| `qiskit-aer >= 0.14.0` | Statevector simulator backend |
| `numpy` | Array maths |
| `matplotlib` | Circuit diagrams + image plots |
| `Pillow` | Image loading and preprocessing |
| `scikit-image` | MSE / SSIM quality metrics |
| `scipy` | Scientific utilities |

> **Note:** `qiskit-aer` is now a **separate** package from `qiskit` (since Qiskit 1.0). Both must be installed.

---

## How It Works

```
Input Image
    │
    ▼
Pre-process  →  Resize to 2ⁿ × 2ⁿ, convert to grayscale
    │
    ▼
Encode (QPIE / FRQI)  →  Build quantum circuit with amplitude / angle encoding
    │
    ▼
QHED  →  Apply Hadamard + Unitary shift operator to extract edges
    │
    ▼
Measure statevector  →  Decode into edge image
    │
    ▼
Visualize  →  Original | H-edges | V-edges | Combined edges
```

---

## Output

When you run the project you will see:

- **QPIE Circuit Diagram** – the full quantum circuit for probability image encoding
- **QPIE Edge Detection Plot** – original image vs. horizontal, vertical, and combined edges
- **FRQI Circuit Diagram** – the full quantum circuit for angle-based encoding
- **FRQI Edge Detection Plot** – same four-panel comparison
- **Comparison Summary** – `showdiff()` side-by-side original vs. both edge results

---

## Running the Notebook

For a step-by-step interactive exploration, open the Jupyter Notebook:

```bash
jupyter notebook Quantum_Edge_Detection.ipynb
```

---

## Tutorial

See **[TUTORIAL.md](TUTORIAL.md)** for a detailed walkthrough of:
- Installation on Windows, macOS, and Linux
- Running on a fresh device with one command
- Understanding the output plots
- Customizing the input image
- Troubleshooting common errors

---

## Authors

- **MohammadYehya** — original project author
- **AJAX-ed** — bug fixes, modernisation, run.py launcher

---

## License

This project is for academic purposes (CS4084 Quantum Computing coursework).
