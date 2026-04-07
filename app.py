# =============================================================================
# app.py  -  Flask web server for Quantum Edge Detection
# =============================================================================
# pip install flask
# python app.py  →  open http://localhost:5000
# =============================================================================

from flask import Flask, request, jsonify, send_from_directory
import numpy
from PIL import Image
from skimage.morphology import skeletonize
from scipy.ndimage import gaussian_filter
import io, base64, threading, uuid

from quantumimageencoding.FRQI import FRQI
from quantumimageencoding.QPIE import QPIE

app = Flask(__name__, static_folder=".")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MAX_DIM = 128   # resize longest side to this before processing
TILE    = 16    # tile size

# In-memory job store  { job_id: {"status": "running"|"done"|"error", "result": {...}} }
jobs = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def process_large_image(img_gray, encoder_cls, tile_size=TILE):
    """
    Overlapping tiled quantum edge detection with Hanning window blending
    to eliminate tile boundary artifacts.
    """
    img_arr = numpy.array(img_gray, dtype=float) / 255.0
    H, W = img_arr.shape

    overlap = tile_size // 2
    step    = tile_size - overlap

    pad    = tile_size
    padded = numpy.pad(img_arr, pad, mode='reflect')
    PH, PW = padded.shape

    edge_acc   = numpy.zeros((PH, PW), dtype=float)
    weight_acc = numpy.zeros((PH, PW), dtype=float)

    lin  = numpy.hanning(tile_size)
    mask = numpy.outer(lin, lin)

    rows  = list(range(0, PH - tile_size + 1, step))
    cols  = list(range(0, PW - tile_size + 1, step))
    total = len(rows) * len(cols)
    done  = 0

    for row in rows:
        for col in cols:
            tile = padded[row:row+tile_size, col:col+tile_size]

            if tile.max() < 1e-6:
                done += 1
                continue

            tile_norm = tile / numpy.sqrt(numpy.sum(tile ** 2))
            enc = encoder_cls()
            enc.encode(tile_norm)
            try:
                e, _, _ = enc.detectEdges()
                if e.max() > 1:
                    e = e / e.max()
                edge_acc  [row:row+tile_size, col:col+tile_size] += e * mask
                weight_acc[row:row+tile_size, col:col+tile_size] += mask
            except Exception:
                pass

            done += 1
            if done % 10 == 0:
                print(f"\r  Processing tiles: {done}/{total}", end='', flush=True)

    print()

    with numpy.errstate(invalid='ignore'):
        edge_map = numpy.where(weight_acc > 0, edge_acc / weight_acc, 0)
    edge_map = edge_map[pad:pad+H, pad:pad+W]
    return edge_map


def thin_edges(edge_img):
    """Smooth → threshold → skeletonize to get clean 1-pixel-wide edges."""
    smoothed = gaussian_filter(edge_img, sigma=0.5)
    binary   = (smoothed > 0.15).astype(bool)
    return skeletonize(binary).astype(float)


def array_to_png_base64(arr):
    img = Image.fromarray((arr * 255).astype(numpy.uint8))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def resize_for_quantum(img_gray, max_dim=MAX_DIM):
    """Resize so longest side <= max_dim, keeping aspect ratio."""
    W, H = img_gray.size
    if max(W, H) <= max_dim:
        return img_gray
    scale = max_dim / max(W, H)
    new_w = max(TILE, int(W * scale))
    new_h = max(TILE, int(H * scale))
    return img_gray.resize((new_w, new_h), Image.LANCZOS)


def run_job(job_id, img_bytes, method, tile_sz):
    try:
        img_color = Image.open(io.BytesIO(img_bytes))
        img_gray  = img_color.convert("L")
        orig_size = img_gray.size

        img_small = resize_for_quantum(img_gray, MAX_DIM)
        W, H = img_small.size
        print(f"[job {job_id[:8]}] {orig_size} → {W}×{H}  method={method.upper()}  tile={tile_sz}")

        encoder_cls = QPIE if method == "qpie" else FRQI
        edge_map = process_large_image(img_small, encoder_cls, tile_sz)
        edge_map = thin_edges(edge_map)

        gray_arr = numpy.array(img_small, dtype=float) / 255.0

        jobs[job_id] = {
            "status": "done",
            "result": {
                "original": array_to_png_base64(gray_arr),
                "edges":    array_to_png_base64(edge_map),
                "width":    W,
                "height":   H,
                "method":   method.upper(),
            }
        }
        print(f"[job {job_id[:8]}] done.")

    except Exception as e:
        import traceback; traceback.print_exc()
        jobs[job_id] = {"status": "error", "result": {"error": str(e)}}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/process", methods=["POST"])
def process():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    img_bytes = request.files["image"].read()
    method    = request.form.get("method", "qpie").lower()
    tile_sz   = int(request.form.get("tile", TILE))

    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running", "result": None}

    t = threading.Thread(target=run_job, args=(job_id, img_bytes, method, tile_sz), daemon=True)
    t.start()

    return jsonify({"job_id": job_id})


@app.route("/status/<job_id>")
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Unknown job"}), 404
    if job["status"] == "running":
        return jsonify({"status": "running"})
    if job["status"] == "error":
        return jsonify({"status": "error", "error": job["result"]["error"]}), 500
    result = job["result"]
    del jobs[job_id]
    return jsonify({"status": "done", **result})


if __name__ == "__main__":
    print("=" * 50)
    print("  Quantum Edge Detection — Web Server")
    print(f"  Max image dim : {MAX_DIM}px  |  Tile: {TILE}×{TILE}")
    print("  Open http://localhost:5000")
    print("=" * 50)
    app.run(debug=False, port=5000, threaded=True)
