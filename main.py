# =============================================================================
# main.py  -  Quantum Edge Detection  (QPIE + FRQI demo)
# =============================================================================

import numpy
from matplotlib import pyplot as plt
from PIL import Image
from skimage.morphology import skeletonize
from scipy.ndimage import gaussian_filter

from quantumimageencoding.FRQI import FRQI
from quantumimageencoding.QPIE import QPIE
from utils import showdiff


def banner(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Tiled quantum edge detection — handles any image size
# ---------------------------------------------------------------------------
TILE = 16   # each tile is TILE×TILE pixels (power of 2: 4, 8, 16, 32)


def process_large_image(img_gray, encoder_cls, tile_size=TILE):
    """
    Split a grayscale PIL image into overlapping tile_size×tile_size patches,
    run quantum edge detection on each patch, blend back with a Hanning window
    to eliminate tile boundary artifacts. Returns edge_map as a numpy array.
    """
    img_arr = numpy.array(img_gray, dtype=float) / 255.0
    H, W = img_arr.shape

    overlap = tile_size // 2        # 50% overlap between tiles
    step    = tile_size - overlap   # step between tile starts

    # Pad so every position has a full tile available
    pad    = tile_size
    padded = numpy.pad(img_arr, pad, mode='reflect')
    PH, PW = padded.shape

    edge_acc   = numpy.zeros((PH, PW), dtype=float)
    weight_acc = numpy.zeros((PH, PW), dtype=float)

    # Hanning window — centre of each tile contributes more than edges
    lin  = numpy.hanning(tile_size)
    mask = numpy.outer(lin, lin)

    rows  = list(range(0, PH - tile_size + 1, step))
    cols  = list(range(0, PW - tile_size + 1, step))
    total = len(rows) * len(cols)
    done  = 0

    for row in rows:
        for col in cols:
            tile = padded[row:row+tile_size, col:col+tile_size]

            # Skip blank tiles (all-zero causes NaN in QPIE amplitude normalisation)
            if tile.max() < 1e-6:
                done += 1
                print(f"\r  Processing tiles: {done}/{total}", end='', flush=True)
                continue

            # Normalise so sum of squares = 1 (required by Qiskit initialise)
            tile_norm = tile / numpy.sqrt(numpy.sum(tile ** 2))

            enc = encoder_cls()
            enc.encode(tile_norm)
            try:
                e, _, _ = enc.detectEdges()
                if e.max() > 1:
                    e = e / e.max()
                # Accumulate weighted result — overlapping tiles blend smoothly
                edge_acc  [row:row+tile_size, col:col+tile_size] += e * mask
                weight_acc[row:row+tile_size, col:col+tile_size] += mask
            except Exception:
                pass

            done += 1
            print(f"\r  Processing tiles: {done}/{total}", end='', flush=True)

    print()

    # Normalise accumulated weights, then crop padding back out
    with numpy.errstate(invalid='ignore'):
        edge_map = numpy.where(weight_acc > 0, edge_acc / weight_acc, 0)
    edge_map = edge_map[pad:pad+H, pad:pad+W]
    return edge_map


def thin_edges(edge_img):
    """Smooth → threshold → skeletonize to get clean 1-pixel-wide edges."""
    smoothed = gaussian_filter(edge_img, sigma=0.5)
    binary   = (smoothed > 0.15).astype(bool)
    return skeletonize(binary).astype(float)


# ---------------------------------------------------------------------------
# Load image
# ---------------------------------------------------------------------------
IMAGE_PATH = r"C:\Users\laksh\Desktop\test.jpg"   # <-- change this to your image path

banner("IMAGE INPUT")
try:
    img_color = Image.open(IMAGE_PATH)
    img_gray  = img_color.convert("L")
    print(f"[INFO] Loaded  : {IMAGE_PATH}")
    print(f"[INFO] Size    : {img_color.size}  |  Mode: {img_color.mode}")

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(img_color)
    axes[0].set_title("Original (colour)")
    axes[0].axis("off")
    axes[1].imshow(img_gray, cmap="gray")
    axes[1].set_title("Grayscale")
    axes[1].axis("off")
    plt.tight_layout()
    plt.show()

    arr        = numpy.array(img_gray, dtype=float) / 255.0
    USE_TILING = True

except FileNotFoundError:
    print(f"[WARN] '{IMAGE_PATH}' not found — using built-in 4x4 demo pattern.")
    arr = numpy.array([
        [0, 0, 0, 0],
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 1, 1, 0]
    ], dtype=float)
    img_gray   = None
    USE_TILING = False


# ===========================================================================
# SECTION 1: QPIE
# ===========================================================================
banner("SECTION 1 : QPIE Encoding")

qpie_edge_img = None
h_img = v_img = None

if USE_TILING:
    print(f"[QPIE] Tiled mode — tile size: {TILE}x{TILE}  overlap: {TILE//2}")
    qpie_edge_img = process_large_image(img_gray, QPIE, TILE)
    qpie_edge_img = thin_edges(qpie_edge_img)
    h_img         = numpy.zeros_like(qpie_edge_img)
    v_img         = numpy.zeros_like(qpie_edge_img)
    print("[QPIE] Edge detection complete.")
else:
    Encoder_QPIE = QPIE()
    qc_qpie = Encoder_QPIE.encode(arr)
    print(f"[QPIE] Qubits: {qc_qpie.num_qubits}  |  Depth: {qc_qpie.depth()}")
    qc_qpie.draw(output='mpl', fold=-1)
    plt.title("QPIE Encoding Circuit")
    plt.tight_layout()
    plt.show()
    try:
        qpie_edge_img, h_img, v_img = Encoder_QPIE.detectEdges()
        qpie_edge_img = thin_edges(qpie_edge_img)
    except Exception as e:
        print(f"[QPIE] Edge detection failed: {e}")

if qpie_edge_img is not None:
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    axes[0].imshow(arr, cmap='gray')
    axes[0].set_title('Original')
    axes[1].imshow(h_img, cmap='gray')
    axes[1].set_title('H-Edges (QPIE)')
    axes[2].imshow(v_img, cmap='gray')
    axes[2].set_title('V-Edges (QPIE)')
    axes[3].imshow(qpie_edge_img, cmap='gray')
    axes[3].set_title('Combined Edges (QPIE)')
    for ax in axes:
        ax.axis('off')
    plt.suptitle('QPIE Quantum Edge Detection', fontsize=14)
    plt.tight_layout()
    plt.show()


# ===========================================================================
# SECTION 2: FRQI
# ===========================================================================
banner("SECTION 2 : FRQI Encoding")

frqi_edge_img = None
h_img_f = v_img_f = None

if USE_TILING:
    print(f"[FRQI] Tiled mode — tile size: {TILE}x{TILE}  overlap: {TILE//2}")
    frqi_edge_img = process_large_image(img_gray, FRQI, TILE)
    frqi_edge_img = thin_edges(frqi_edge_img)
    h_img_f       = numpy.zeros_like(frqi_edge_img)
    v_img_f       = numpy.zeros_like(frqi_edge_img)
    print("[FRQI] Edge detection complete.")
else:
    Encoder_FRQI = FRQI()
    qc_frqi = Encoder_FRQI.encode(arr)
    print(f"[FRQI] Qubits: {qc_frqi.num_qubits}  |  Depth: {qc_frqi.depth()}")
    qc_frqi.draw(output='mpl', fold=-1)
    plt.title("FRQI Encoding Circuit")
    plt.tight_layout()
    plt.show()
    try:
        frqi_edge_img, h_img_f, v_img_f = Encoder_FRQI.detectEdges()
        frqi_edge_img = thin_edges(frqi_edge_img)
    except Exception as e:
        print(f"[FRQI] Edge detection failed: {e}")

if frqi_edge_img is not None:
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    axes[0].imshow(arr, cmap='gray')
    axes[0].set_title('Original')
    axes[1].imshow(h_img_f, cmap='gray')
    axes[1].set_title('H-Edges (FRQI)')
    axes[2].imshow(v_img_f, cmap='gray')
    axes[2].set_title('V-Edges (FRQI)')
    axes[3].imshow(frqi_edge_img, cmap='gray')
    axes[3].set_title('Combined Edges (FRQI)')
    for ax in axes:
        ax.axis('off')
    plt.suptitle('FRQI Quantum Edge Detection', fontsize=14)
    plt.tight_layout()
    plt.show()


# ===========================================================================
# SECTION 3: Comparison
# ===========================================================================
banner("SECTION 3 : Comparison")

# Use a non-zero dummy tile so QPIE encode doesn't NaN
_dummy = numpy.ones((TILE, TILE)) / TILE
Encoder_QPIE = QPIE()
Encoder_QPIE.encode(arr if not USE_TILING else _dummy)

if qpie_edge_img is not None and frqi_edge_img is not None:
    showdiff(Encoder_QPIE, arr, qpie_edge_img, frqi_edge_img)
elif qpie_edge_img is not None:
    showdiff(Encoder_QPIE, arr, qpie_edge_img)
else:
    showdiff(Encoder_QPIE, arr)

print("\n[Done] All steps completed.")
