"""Batched normalized correlation for padded arrow masks."""

import math

import cv2
import numpy as np

from .deadline import check_deadline


class TemplateMatcher:
    """Compute CCOEFF_NORMED for every direction in one matrix product.

    Inputs come from terminal._normalize: a four-pixel zero border means
    translations of at most two pixels never discard nonzero input pixels.
    All search windows therefore share a mean and variance. Centered template
    vectors cancel the input mean, allowing one reusable matrix of templates.
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
        vectors = np.array(arrays, dtype=np.float64).reshape(len(arrays), -1)
        vectors -= vectors.mean(axis=1, keepdims=True)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        self.constant = norms[:, 0] == 0
        vectors /= np.where(norms == 0, 1, norms)
        # Contiguous double precision is faster for this small GEMM shape and
        # avoids the float32 accumulation error of repeated template matching.
        self.matrix = np.ascontiguousarray(vectors.T)

    def scores(self, normalized):
        check_deadline()
        if normalized.shape != self.shape:
            raise ValueError("Normalized arrow and templates must have the same shape.")
        _, std = cv2.meanStdDev(normalized)
        norm = float(std[0, 0]) * math.sqrt(normalized.size)
        radius = self.radius
        padded = (cv2.copyMakeBorder(normalized, radius, radius, radius, radius,
                                    cv2.BORDER_CONSTANT, value=0) if radius else normalized)
        windows = np.lib.stride_tricks.sliding_window_view(padded, self.shape)
        patches = windows.reshape(-1, normalized.size).astype(np.float64)
        if norm == 0:
            best = np.zeros(self.matrix.shape[1])
        else:
            correlations = cv2.gemm(patches, self.matrix, 1 / norm, None, 0)
            best = np.clip(correlations.max(axis=0), -1, 1)
        best[self.constant] = 1
        return {direction: float(best[group].max()) for direction, group in self.groups.items()}
