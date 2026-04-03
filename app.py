# =============================================================================
# app.py  -  Flask web server for Quantum Edge Detection
# =============================================================================
# Install Flask first:  pip install flask
# Run with:  python app.py
# Then open:  http://localhost:5000
# =============================================================================

from flask import Flask, request, jsonify, send_file, send_from_directory
import numpy
from PIL import Image
from skimage.morphology import skeletonize
import io
import base64
import os

from quantumimageencoding.FRQI import FRQI
from quantumimageencoding.QPIE import QPIE

app = Flask(__name__, static_folder=".")

TILE = 16  # tile size for tiled quantum processing


# ---------------------------------------------------------------------------
# Helpers (same logic as main.py)
# ---------------------------------------------------------------------------

def process_large_image(img_gray: Image.Image, encoder_cls, tile_size=TILE):
    img_arr = numpy.array(img_gray, dtype=float) / 255.0
    H, W = img_arr.shape

    pad_h = (tile_size - H % tile_size) % tile_size
    pad_w = (tile_size - W % tile_size) % tile_size
    padded = numpy.pad(img_arr, ((0, pad_h), (0, pad_w)), mode='edge')
    PH, PW = padded.shape

    edge_map = numpy.zeros((PH, PW), dtype=float)

    for row in range(0, PH, tile_size):
        for col in range(0, PW, tile_size):
            tile = padded[row:row+tile_size, col:col+tile_size]
            enc  = encoder_cls()
            enc.encode(tile)
            try:
                e, _, _ = enc.detectEdges()
                if e.max() > 1: e = e / e.max()
                edge_map[row:row+tile_size, col:col+tile_size] = e
            except Exception:
                pass

    edge_map = edge_map[:H, :W]
    return edge_map


def thin_edges(edge_img):
    binary = (edge_img > 0.1).astype(bool)
    return skeletonize(binary).astype(float)


def array_to_png_base64(arr):
    """Convert a float [0,1] numpy array to a base64-encoded PNG string."""
    img = Image.fromarray((arr * 255).astype(numpy.uint8))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


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

    file    = request.files["image"]
    method  = request.form.get("method", "qpie").lower()   # "qpie" or "frqi"
    tile_sz = int(request.form.get("tile", 16))

    img_color = Image.open(file.stream)
    img_gray  = img_color.convert("L")

    W, H = img_gray.size
    print(f"[INFO] Image: {W}×{H}  |  Method: {method.upper()}  |  Tile: {tile_sz}")

    encoder_cls = QPIE if method == "qpie" else FRQI

    edge_map = process_large_image(img_gray, encoder_cls, tile_sz)
    edge_map = thin_edges(edge_map)

    # Also return grayscale version of original for side-by-side display
    gray_arr = numpy.array(img_gray, dtype=float) / 255.0

    return jsonify({
        "original": array_to_png_base64(gray_arr),
        "edges":    array_to_png_base64(edge_map),
        "width":    W,
        "height":   H,
        "method":   method.upper(),
    })


if __name__ == "__main__":
    print("=" * 50)
    print("  Quantum Edge Detection — Web Server")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 50)
    app.run(debug=True, port=5000)
