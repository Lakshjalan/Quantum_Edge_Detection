# =============================================================================
# main.py  -  Quantum Edge Detection  (QPIE + FRQI demo)
# =============================================================================

import numpy
from matplotlib import pyplot as plt
from PIL import Image
from skimage.morphology import skeletonize

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
    img_arr = numpy.array(img_gray, dtype=float) / 255.0
    H, W = img_arr.shape

    pad_h = (tile_size - H % tile_size) % tile_size
    pad_w = (tile_size - W % tile_size) % tile_size
    padded = numpy.pad(img_arr, ((0, pad_h), (0, pad_w)), mode='edge')
    PH, PW = padded.shape

    edge_map = numpy.zeros((PH, PW), dtype=float)
    h_map    = numpy.zeros((PH, PW), dtype=float)
    v_map    = numpy.zeros((PH, PW), dtype=float)

    total = (PH // tile_size) * (PW // tile_size)
    done  = 0

    for row in range(0, PH, tile_size):
        for col in range(0, PW, tile_size):
            tile = padded[row:row+tile_size, col:col+tile_size]

            # Skip blank tiles (all-zero causes NaN division in QPIE)
            if tile.max() < 1e-6:
                done += 1
                print(f"\r  Processing tiles: {done}/{total}", end='', flush=True)
                continue

            # Normalise so sum of squares = 1
            tile = tile / numpy.sqrt(numpy.sum(tile ** 2))

            enc = encoder_cls()
            enc.encode(tile)
            try:
                e, h, v = enc.detectEdges()
                if e.max() > 1: e = e / e.max()
                if h.max() > 1: h = h / h.max()
                if v.max() > 1: v = v / v.max()
                edge_map[row:row+tile_size, col:col+tile_size] = e
                h_map   [row:row+tile_size, col:col+tile_size] = h
                v_map   [row:row+tile_size, col:col+tile_size] = v
            except Exception:
                pass
            done += 1
            print(f"\r  Processing tiles: {done}/{total}", end='', flush=True)

    print()
    edge_map = edge_map[:H, :W]
    h_map    = h_map   [:H, :W]
    v_map    = v_map   [:H, :W]
    return edge_map, h_map, v_map


def thin_edges(edge_img):
    binary = (edge_img > 0.1).astype(bool)
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

    arr = numpy.array(img_gray, dtype=float) / 255.0
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

if USE_TILING:
    print(f"[QPIE] Tiled mode — tile size: {TILE}x{TILE}")
    qpie_edge_img, h_img, v_img = process_large_image(img_gray, QPIE, TILE)
    qpie_edge_img = thin_edges(qpie_edge_img)
    h_img         = thin_edges(h_img)
    v_img         = thin_edges(v_img)
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

if USE_TILING:
    print(f"[FRQI] Tiled mode — tile size: {TILE}x{TILE}")
    frqi_edge_img, h_img_f, v_img_f = process_large_image(img_gray, FRQI, TILE)
    frqi_edge_img = thin_edges(frqi_edge_img)
    h_img_f       = thin_edges(h_img_f)
    v_img_f       = thin_edges(v_img_f)
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
Encoder_QPIE = QPIE()
Encoder_QPIE.encode(arr if not USE_TILING else numpy.zeros((TILE, TILE)))

if qpie_edge_img is not None and frqi_edge_img is not None:
    showdiff(Encoder_QPIE, arr, qpie_edge_img, frqi_edge_img)
elif qpie_edge_img is not None:
    showdiff(Encoder_QPIE, arr, qpie_edge_img)
else:
    showdiff(Encoder_QPIE, arr)

print("\n[Done] All steps completed.")
