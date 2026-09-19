"""Bounded horizontal shear views; recognition never reads sample annotations."""

import cv2
import numpy as np


def horizontal_views(image, roi):
    """Yield the original ROI and eight mild horizontal shear corrections.

    Both signs use the same range and step. These are affine corrections, not
    full perspective rectification. Padding preserves the entire source ROI.
    """
    x, y, w, h = roi if roi is not None else (0, 0, image.shape[1], image.shape[0])
    crop = image[y:y + h, x:x + w]
    yield 0.0, crop
    for shear in (-0.5, -0.375, -0.25, -0.125, 0.125, 0.25, 0.375, 0.5):
        offset = max(0, shear * (h - 1))
        width = int(np.ceil(w + abs(shear) * (h - 1)))
        matrix = np.float32([[1, -shear, offset], [0, 1, 0]])
        yield shear, cv2.warpAffine(crop, matrix, (width, h),
                                   borderMode=cv2.BORDER_REPLICATE)
