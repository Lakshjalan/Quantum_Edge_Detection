from matplotlib import pyplot as plt
from quantumimageencoding.BaseQuantumEncoder import QuantumEncoder
from PIL import Image
import numpy

def showdiff(Encoder: QuantumEncoder, *images):
    """
    Display one or more images side-by-side in a matplotlib figure.
    Each item in *images may be a PIL Image, a numpy array, or a plain list.
    Optionally computes MSE/SSI between the first two images if available.
    """
    if len(images) == 0:
        print("[showdiff] No images provided.")
        return

    # Convert everything to numpy arrays for display
    np_images = []
    for img in images:
        if isinstance(img, Image.Image):
            np_images.append(numpy.array(img))
        else:
            np_images.append(numpy.array(img))

    # Optionally print quality metrics between first two images
    if len(np_images) >= 2:
        try:
            print('MSE: ', Encoder.calculateMSE(np_images[0], np_images[1]))
        except Exception:
            pass
        try:
            print('SSI: ', Encoder.calculateSSI(np_images[0], np_images[1]))
        except Exception:
            pass

    # Plot all images side by side
    n = len(np_images)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5))
    if n == 1:
        axes = [axes]  # make iterable when only one subplot
    for i, (ax, img) in enumerate(zip(axes, np_images)):
        ax.imshow(img, cmap='gray')
        ax.set_title(f'Image {i + 1}')
        ax.axis('off')
    plt.suptitle('Image Comparison', fontsize=13)
    plt.tight_layout()
    plt.show()
