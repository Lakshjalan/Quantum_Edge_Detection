#!/usr/bin/env python3
# =============================================================================
# run.py  -  ONE-CLICK LAUNCHER for Quantum Edge Detection
# =============================================================================
#
#   Just double-click this file  OR  run:  python run.py
#
#   Works on a brand-new machine with only Python installed.
#   It will automatically:
#       1. Upgrade pip
#       2. Install / verify every required library
#       3. Launch main.py
#
# =============================================================================

import sys
import subprocess
import importlib
import os

# ---------------------------------------------------------------------------
# Package map: { import_name : pip_install_name }
# ---------------------------------------------------------------------------
REQUIRED = {
    "qiskit":           "qiskit>=1.0.0",
    "qiskit_aer":       "qiskit-aer>=0.14.0",
    "numpy":            "numpy>=1.24.0",
    "scipy":            "scipy>=1.11.0",
    "matplotlib":       "matplotlib>=3.7.0",
    "PIL":              "Pillow>=9.0.0",
    "skimage":          "scikit-image>=0.21.0",
    "networkx":         "networkx>=3.0",
    "sympy":            "sympy>=1.12",
    "mpmath":           "mpmath>=1.3.0",
    "pylatexenc":       "pylatexenc>=2.10",
}


def pip_install(package_spec):
    """Install a package via pip."""
    print(f"  [install] pip install {package_spec}")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", package_spec, "--quiet"],
        capture_output=False
    )
    if result.returncode != 0:
        print(f"  [ERROR] Failed to install {package_spec}. "
              f"Please install it manually and re-run.")
        sys.exit(1)


def check_and_install_all():
    """Check every required package and install if missing."""
    print("=" * 60)
    print("  Quantum Edge Detection  -  Dependency Checker")
    print("=" * 60)

    # 1. Upgrade pip silently first
    print("\n[Step 1] Upgrading pip...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--quiet"],
        capture_output=False
    )
    print("  pip is up to date.")

    # 2. Check / install each dependency
    print("\n[Step 2] Checking dependencies...")
    missing = []
    for import_name, pip_spec in REQUIRED.items():
        try:
            importlib.import_module(import_name)
            print(f"  [OK]     {import_name}")
        except ImportError:
            print(f"  [MISSING] {import_name}  ->  will install {pip_spec}")
            missing.append(pip_spec)

    if missing:
        print(f"\n[Step 3] Installing {len(missing)} missing package(s)...")
        for pkg in missing:
            pip_install(pkg)
        print("\n  All packages installed successfully!")
    else:
        print("\n[Step 3] All packages already installed. Nothing to do.")

    # 3. Additional check: qiskit.circuit.library must have RYGate
    print("\n[Step 4] Verifying Qiskit API compatibility...")
    try:
        from qiskit.circuit.library import RYGate
        from qiskit_aer import Aer
        print("  [OK] Qiskit + Aer API is compatible.")
    except ImportError as e:
        print(f"  [ERROR] Qiskit API check failed: {e}")
        print("  Attempting to fix by reinstalling qiskit and qiskit-aer...")
        pip_install("qiskit>=1.0.0")
        pip_install("qiskit-aer>=0.14.0")

    print("\n" + "=" * 60)
    print("  All checks passed. Launching the project...")
    print("=" * 60 + "\n")


def run_main():
    """Run main.py from the same directory as this script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_path  = os.path.join(script_dir, "main.py")

    if not os.path.isfile(main_path):
        print(f"[ERROR] main.py not found at {main_path}")
        print("  Make sure run.py is in the same folder as main.py.")
        sys.exit(1)

    # Run main.py as a subprocess so it inherits the current environment
    result = subprocess.run([sys.executable, main_path], cwd=script_dir)
    sys.exit(result.returncode)


if __name__ == "__main__":
    check_and_install_all()
    run_main()
