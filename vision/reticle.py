"""Bounded grayscale cleanup for the screen-centered circular game reticle."""

import json
from pathlib import Path

import cv2
import numpy as np

from .deadline import check_deadline


def remove_circular_reticle(gray, roi, *, debug_dir=None):
    """Return a repaired copy only when a nearly complete thin circle is found.

    Detect in a small, resolution-normalized center patch. No color labels or
    arrow directions are used; inpainting is confined to a narrow annulus.
    """
    check_deadline()
    height, width = gray.shape
    scale = height / 1080
    half = round(150 * scale)
    cx, cy = width // 2, height // 2
    if half < 1 or cx < half or cy < half:
        return None
    x0, y0 = cx - half, cy - half
    patch = gray[y0:cy + half, x0:cx + half]
    normalized = cv2.resize(patch, (300, 300), interpolation=cv2.INTER_AREA)
    smooth = cv2.GaussianBlur(normalized, (5, 5), 1)
    circles = cv2.HoughCircles(
        smooth, cv2.HOUGH_GRADIENT, 1, 60,
        param1=60, param2=45, minRadius=60, maxRadius=125)
    check_deadline()
    if circles is None:
        return None
    edges = cv2.Canny(smooth, 30, 60)
    angles = np.linspace(0, 2 * np.pi, 180, endpoint=False)[:, None]
    accepted = []
    for x, y, radius in circles[0]:
        if np.hypot(x - 150, y - 150) > 10:
            continue
        radii = radius + np.arange(-5, 6)
        xs = np.rint(x + np.cos(angles) * radii).astype(int)
        ys = np.rint(y + np.sin(angles) * radii).astype(int)
        support = np.any(edges[ys, xs] != 0, axis=1)
        # Reject short arcs and round arrow/background fragments.
        if support.mean() >= 0.9 and np.all(support.reshape(12, 15).mean(axis=1) >= 0.6):
            accepted.append((float(x), float(y), float(radius)))
    if len(accepted) != 1:
        return None
    x, y, radius = accepted[0]
    factor = patch.shape[0] / 300
    mask = np.zeros_like(patch)
    cv2.circle(mask, (round(x * factor), round(y * factor)),
               round(radius * factor), 255, max(3, round(7 * factor)))
    rx, ry, rw, rh = roi
    left, top = max(rx, x0), max(ry, y0)
    right, bottom = min(rx + rw, cx + half), min(ry + rh, cy + half)
    if right <= left or bottom <= top or not np.any(mask[top-y0:bottom-y0, left-x0:right-x0]):
        return None
    check_deadline()
    repaired = cv2.inpaint(patch, mask, max(1, round(3 * factor)), cv2.INPAINT_TELEA)
    check_deadline()
    result = gray.copy()
    result[y0:cy + half, x0:cx + half] = repaired
    if debug_dir is not None:
        folder = Path(debug_dir)
        folder.mkdir(parents=True, exist_ok=True)
        for name, image in (("original", patch), ("mask", mask), ("repaired", repaired)):
            ok, encoded = cv2.imencode(".png", image)
            if not ok:
                raise ValueError(f"Cannot encode reticle debug image: {name}")
            encoded.tofile(folder / f"{name}.png")
        (folder / "circle.json").write_text(json.dumps({
            "center": [x0 + x * factor, y0 + y * factor],
            "radius": radius * factor, "patch_roi": [x0, y0, 2 * half, 2 * half],
        }, indent=2), encoding="utf-8")
    return result
