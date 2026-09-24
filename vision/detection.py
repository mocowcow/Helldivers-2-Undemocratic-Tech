"""Locate a Terminal arrow row in a full screenshot using shape and alignment."""

from dataclasses import dataclass
import json
from pathlib import Path

import cv2
import numpy as np

from .deadline import check_deadline
from .matching import TemplateMatcher

from .terminal import (
    DEFAULT_TEMPLATES, SLANTED_TEMPLATES, RecognitionConfig, RecognitionError,
    _clean_mask, _contour_mask, _grayscale, _load_templates, _normalize,
    _segment, _write_image, recognize_directions,
)


@dataclass
class Detection:
    roi: tuple[int, int, int, int]
    slope: float
    intercept: float
    anchors: int
    symbols: tuple[tuple[int, int, int, int], ...]


class ScreenshotRecognitionError(RecognitionError):
    def __init__(self, message, roi):
        super().__init__(message)
        self.roi = roi


def _candidates(gray, cleanup_sizes=(3,), *, cache=None):
    # Share work between cleanup strengths within this screenshot only.
    cache = {} if cache is None else cache
    config = RecognitionConfig(antialias=True)
    if "templates" not in cache:
        banks = [_load_templates(folder, config) for folder in (DEFAULT_TEMPLATES, SLANTED_TEMPLATES)]
        cache["templates"] = {d: sum((bank[d] for bank in banks), []) for d in banks[0]}
    templates = cache["templates"]
    if "matcher" not in cache:
        cache["matcher"] = TemplateMatcher(templates, radius=2)
    matcher = cache["matcher"]
    score_cache = cache.setdefault("scores", {})
    scale = gray.shape[0] / 1080
    candidates = []
    for method in ("otsu", "tophat", "adaptive"):
        check_deadline()
        if method not in cache:
            cache[method] = _segment(gray, method)[1]
        raw = cache[method]
        for cleanup in cleanup_sizes:
            binary = _clean_mask(raw, cleanup)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                check_deadline()
                bounds = x, y, w, h = cv2.boundingRect(contour)
                if not (cv2.contourArea(contour) >= 70 * scale ** 2
                        and 10 * scale <= min(w, h) and max(w, h) <= 150 * scale
                        and 0.35 <= w / h <= 2.8):
                    continue
                mask = _normalize(_contour_mask(contour, bounds), 48, antialias=True)
                key = mask.tobytes()
                scores = score_cache.get(key)
                if scores is None:
                    scores = sorted(matcher.scores(mask).values(), reverse=True)
                    score_cache[key] = scores
                if scores[0] >= 0.55:
                    candidates.append({"box": bounds, "score": scores[0],
                                       "anchor": scores[0] >= 0.78 and scores[0] - scores[1] >= 0.08})
    # Merge duplicate observations of the same contour across segmentations.
    selected = []
    selected_boxes = np.empty((len(candidates), 4), dtype=np.int64)
    for item in sorted(candidates, key=lambda c: (c["anchor"], c["score"]), reverse=True):
        check_deadline()
        x, y, w, h = item["box"]
        boxes = selected_boxes[:len(selected)]
        overlap = np.maximum(0, np.minimum((x+w, y+h), boxes[:, :2]+boxes[:, 2:])
                             - np.maximum((x, y), boxes[:, :2]))
        duplicate = np.any(overlap[:, 0]*overlap[:, 1]
                           / np.minimum(w*h, boxes[:, 2]*boxes[:, 3]) > 0.6)
        if not duplicate:
            selected_boxes[len(selected)] = item["box"]
            selected.append(item)
    return selected


def _locate_arrow_row(gray, *, cleanup_size=3, debug_dir=None, cache=None):
    candidates = _candidates(gray, (cleanup_size,), cache=cache)
    anchors = [c for c in candidates if c["anchor"]][:100]
    if len(anchors) < 3:
        raise RecognitionError("No reliable arrow row found in the screenshot.")
    boxes = np.array([c["box"] for c in anchors], float)
    centers = boxes[:, :2] + boxes[:, 2:] / 2
    rows = []
    for i, a in enumerate(centers):
        check_deadline()
        for j in range(i + 1, len(centers)):
            b = centers[j]
            mw, mh = np.median(boxes[[i, j], 2:], axis=0)
            if not mw < abs(b[0] - a[0]) < 6 * mw:
                continue
            slope = (b[1]-a[1])/(b[0]-a[0])
            if abs(slope) > 0.8:
                continue
            intercept = a[1] - slope*a[0]
            residual = abs(centers[:, 1] - slope*centers[:, 0] - intercept) / np.hypot(slope, 1)
            mask = ((residual < 0.45*mh) & (boxes[:, 2] > mw/2) & (boxes[:, 2] < mw*2)
                    & (boxes[:, 3] > mh/2) & (boxes[:, 3] < mh*2))
            indices = sorted(np.flatnonzero(mask), key=lambda k: centers[k, 0])
            groups = [[]]
            for k in indices:
                if groups[-1] and centers[k, 0]-centers[groups[-1][-1], 0] > 4*mw:
                    groups.append([])
                groups[-1].append(k)
            group = next((g for g in groups if i in g and j in g), [])
            if len(group) >= 3:
                rows.append((len(group), sum(anchors[k]["score"] for k in group), group))
    if not rows:
        raise RecognitionError("Candidates do not establish an arrow row.")
    _, _, indices = max(rows, key=lambda r: r[:2])
    if any(len(group) >= max(3, len(indices)-1) and not set(group).intersection(indices)
           for _, _, group in rows):
        raise RecognitionError("Multiple plausible arrow rows; refusing ambiguous ROI.")
    points = centers[indices]
    slope, intercept = np.polyfit(points[:, 0], points[:, 1], 1)
    mw, mh = np.median(boxes[indices, 2:], axis=0)
    chosen = [anchors[i] for i in indices]

    def contrast(box):
        x, y, w, h = box
        low, high = np.percentile(gray[y:y+h, x:x+w], (10, 90))
        return high - low

    row_contrast = np.median([contrast(c["box"]) for c in chosen])
    # Extend through nearby unknown shapes with comparable local contrast.
    for _ in range(len(candidates)):
        check_deadline()
        left = min(c["box"][0] for c in chosen)
        right = max(c["box"][0]+c["box"][2] for c in chosen)
        additions = []
        for c in candidates:
            x, y, w, h = c["box"]
            # Adaptive thresholding can turn faint panel texture into a weak
            # extra symbol. Keep genuine shape anchors regardless of brightness.
            residual = abs(y+h/2-slope*(x+w/2)-intercept)/np.hypot(slope, 1)
            if (c not in chosen and mw*0.4 < w < mw*2 and mh*0.4 < h < mh*2
                    and residual < mh*0.5 and left-2*mw < x+w/2 < right+2*mw):
                if not c["anchor"] and contrast(c["box"]) < row_contrast * 0.25:
                    continue
                additions.append(c)
        if not additions:
            break
        chosen.extend(additions)
    bound = np.array([c["box"] for c in chosen])
    lo = np.floor(bound[:, :2].min(axis=0) - max(4, mh*0.25)).astype(int)
    hi = np.ceil((bound[:, :2]+bound[:, 2:]).max(axis=0) + max(4, mh*0.25)).astype(int)
    lo = np.maximum(lo, 0)
    hi = np.minimum(hi, [gray.shape[1], gray.shape[0]])
    detection = Detection(tuple(int(v) for v in (*lo, *(hi-lo))), float(slope), float(intercept), len(indices),
                          tuple(tuple(int(v) for v in c["box"]) for c in sorted(chosen, key=lambda c: c["box"][0])))
    if debug_dir is not None:
        folder = Path(debug_dir)
        folder.mkdir(parents=True, exist_ok=True)
        annotated = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        for c in candidates:
            x, y, w, h = c["box"]
            cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 180, 0) if c["anchor"] else (0, 0, 180), 1)
        cv2.rectangle(annotated, tuple(lo), tuple(hi), (255, 255, 0), 2)
        _write_image(folder / "detection.png", annotated)
        (folder / "detection.json").write_text(json.dumps({
            "roi": detection.roi, "slope": detection.slope, "intercept": detection.intercept,
            "anchors": detection.anchors, "candidates": candidates,
            "symbols": detection.symbols,
        }, indent=2), encoding="utf-8")
    return detection


def locate_arrow_row(image, *, debug_dir=None):
    """Compare weak and strong cleanup without replacing one row's end symbols."""
    detections = []
    gray = _grayscale(image)
    cache = {}
    for size in (3, 5):
        try:
            detections.append(_locate_arrow_row(
                gray, cleanup_size=size, cache=cache,
                debug_dir=Path(debug_dir)/f"locate{size}" if debug_dir else None))
        except RecognitionError:
            continue
    if not detections:
        raise RecognitionError("No unambiguous arrow row found in the screenshot.")
    result = detections[0]
    if len(detections) == 2:
        other = detections[1]
        middle = (result.roi[0]+result.roi[2]/2 + other.roi[0]+other.roi[2]/2)/2
        height = np.median([box[3] for box in result.symbols])
        if (abs(result.slope-other.slope) > 0.15
                or abs((result.slope-other.slope)*middle+result.intercept-other.intercept) > height):
            raise RecognitionError("Cleanup methods located different rows; refusing ambiguous ROI.")
        x = min(result.roi[0], other.roi[0])
        y = min(result.roi[1], other.roi[1])
        right = max(d.roi[0]+d.roi[2] for d in detections)
        bottom = max(d.roi[1]+d.roi[3] for d in detections)
        support = max(detections, key=lambda d: len(d.symbols))
        result = Detection((x, y, right-x, bottom-y), result.slope, result.intercept,
                           max(d.anchors for d in detections), support.symbols)
    if debug_dir is not None:
        folder = Path(debug_dir)
        folder.mkdir(parents=True, exist_ok=True)
        annotated = cv2.cvtColor(_grayscale(image), cv2.COLOR_GRAY2BGR)
        x, y, w, h = result.roi
        cv2.rectangle(annotated, (x, y), (x+w, y+h), (255, 255, 0), 2)
        _write_image(folder/"detection.png", annotated)
        (folder/"detection.json").write_text(json.dumps({"roi": result.roi,
            "symbols": result.symbols, "anchors": result.anchors}, indent=2), encoding="utf-8")
    return result


def recognize_screenshot(image, *, config=None, template_dir=DEFAULT_TEMPLATES, debug_dir=None):
    """Return (direction sequence, detected ROI), without reading annotations."""
    detection = locate_arrow_row(image, debug_dir=debug_dir)
    try:
        sequence = recognize_directions(image, roi=detection.roi, config=config, template_dir=template_dir,
                                        debug_dir=Path(debug_dir)/"recognition" if debug_dir else None)
        if len(sequence) < len(detection.symbols):
            raise RecognitionError("Fewer recognized symbols than row candidates; refusing a partial sequence.")
    except RecognitionError as error:
        raise ScreenshotRecognitionError(str(error), detection.roi) from error
    return sequence, detection.roi
