"""Batched normalized correlation for padded arrow masks."""

import math

import cv2
import numpy as np

from .deadline import check_deadline


class TemplateMatcher:
    """Compute CCOEFF_NORMED for every direction in one matrix product.

    Inputs come from terminal._normalize: a four-pixel zero border means
    translations of at most two pixels never discard nonzero input pixels.
    All search windows therefore share a mean and variance. Zero template
    borders contribute nothing to dot products; the mean correction still
    uses the complete normalized image.
    """

    def __init__(self, templates, radius=0):
        if radius not in (0, 1, 2):
            raise ValueError("Template translation radius must be 0, 1, or 2.")
        self.radius = radius
        self.groups = {}
        arrays = []
        for direction, variants in templates.items():
            start = len(arrays)
            arrays.extend(variants)
            self.groups[direction] = slice(start, len(arrays))
        self.shape = arrays[0].shape
        values = np.array(arrays, dtype=np.float64)
        vectors = values.reshape(len(arrays), -1)
        centered = vectors - vectors.mean(axis=1, keepdims=True)
        norms = np.linalg.norm(centered, axis=1, keepdims=True)
        self.constant = norms[:, 0] == 0
        safe_norms = np.where(norms == 0, 1, norms)
        self.correction = vectors.sum(axis=1) / safe_norms[:, 0]
        support = np.any(values != 0, axis=0).astype(np.uint8)
        self.bounds = x, y, w, h = cv2.boundingRect(support)
        if not w or not h:
            self.bounds = x, y, w, h = (0, 0, self.shape[1], self.shape[0])
        vectors = values[:, y:y+h, x:x+w].reshape(len(arrays), -1) / safe_norms
        # Contiguous double precision is faster for this small GEMM shape and
        # avoids the float32 accumulation error of repeated template matching.
        self.matrix = np.ascontiguousarray(vectors.T)

    def scores(self, normalized):
        check_deadline()
        if normalized.shape != self.shape:
            raise ValueError("Normalized arrow and templates must have the same shape.")
        mean, std = cv2.meanStdDev(normalized)
        norm = float(std[0, 0]) * math.sqrt(normalized.size)
        radius = self.radius
        padded = (cv2.copyMakeBorder(normalized, radius, radius, radius, radius,
                                    cv2.BORDER_CONSTANT, value=0) if radius else normalized)
        padded = padded.astype(np.float64)
        x, y, w, h = self.bounds
        search = padded[y:y+h+2*radius, x:x+w+2*radius]
        # Bounds come from the template and the padded input has exactly the
        # required translation margin. Avoid copying uint8 windows before
        # converting every overlapping patch to double precision.
        span = 2 * radius + 1
        windows = np.lib.stride_tricks.as_strided(
            search, shape=(span, span, h, w), strides=search.strides * 2,
            writeable=False)
        patches = windows.reshape(span * span, w*h)
        if norm == 0:
            best = np.zeros(self.matrix.shape[1])
        else:
            correlations = (patches @ self.matrix) / norm
            best = np.clip(correlations.max(axis=0)
                           - (float(mean[0, 0]) / norm) * self.correction, -1, 1)
        best[self.constant] = 1
        return {direction: float(best[group].max()) for direction, group in self.groups.items()}
