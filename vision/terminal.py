"""Contour candidates and grayscale shape templates for one Terminal arrow row."""

from dataclasses import asdict, dataclass, replace
from functools import lru_cache
from contextvars import ContextVar, copy_context
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

import cv2
import numpy as np

from .deadline import check_deadline
from .matching import TemplateMatcher


DIRECTIONS = ("up", "down", "left", "right")
DEFAULT_TEMPLATES = Path(__file__).resolve().parent / "templates" / "terminal"
SLANTED_TEMPLATES = Path(__file__).resolve().parent / "templates" / "terminal_slanted"
_recognition_cache = ContextVar("terminal_recognition_cache", default=None)


@dataclass(frozen=True)
class RecognitionConfig:
    # Provisional values: calibrate against real screenshots before game use.
    segmentation: str = "auto"
    clean_thin_noise: bool = True
    cleanup_size: int = 3
    min_area: float = 25
    min_size: int = 6
    max_size: int = 200
    min_aspect: float = 0.35
    max_aspect: float = 2.8
    score_threshold: float = 0.75
    score_margin: float = 0.08
    row_tolerance: float = 0.6  # Perpendicular line residual / median arrow height.
    max_gap_ratio: float = 4.0  # Maximum center spacing / median width.
    normalized_size: int = 48
    deskew_fallback: bool = True
    view_fallback: bool = True
    background_method: str = "tophat"
    alignment_radius: int = 0
    alignment_fallback: bool = True
    antialias: bool = False
    antialias_fallback: bool = True
    template_fallback: bool = True


class RecognitionError(ValueError):
    """No reliable complete sequence; details are available in debug output."""


def read_image(path):
    """Support Windows paths containing non-ASCII characters."""
    image = cv2.imdecode(np.fromfile(Path(path), dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Cannot read image: {path}")
    return image


def _write_image(path, image):
    success, encoded = cv2.imencode(".png", image)
    if not success:
        raise ValueError(f"Cannot encode image: {path}")
    encoded.tofile(path)


def _grayscale(image):
    check_deadline()
    if not isinstance(image, np.ndarray) or image.dtype != np.uint8 or image.size == 0:
        raise ValueError("Expected a nonempty uint8 NumPy image.")
    cache = _recognition_cache.get()
    grays = cache.setdefault("grays", {}) if cache is not None else {}
    if id(image) in grays:
        return grays[id(image)][1]
    if image.ndim == 2:
        gray = image.copy()
    elif image.ndim == 3 and image.shape[2] in (3, 4):
        conversion = cv2.COLOR_BGR2GRAY if image.shape[2] == 3 else cv2.COLOR_BGRA2GRAY
        gray = cv2.cvtColor(image, conversion)
    else:
        raise ValueError("Expected grayscale, BGR, or BGRA image.")
    if cache is not None and len(grays) < 128:
        # Retain the source so Python cannot reuse its id during this request.
        grays[id(image)] = (image, gray)
    return gray


def _threshold(gray):
    # Bright shapes on a dark Terminal background; no hue filtering.
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]


def _segment(gray, method):
    """Keep clean template processing independent of screenshot illumination."""
    check_deadline()
    cache = _recognition_cache.get()
    if cache is None:
        return _segment_uncached(gray, method)
    segments = cache.setdefault("segments", {})
    key = (method, gray.shape, gray.tobytes())
    if key in segments:
        return segments[key]
    result = _segment_uncached(gray, method)
    if len(segments) < 64:
        segments[key] = result
    return result


def _segment_uncached(gray, method):
    if method == "otsu":
        return gray, _threshold(gray)
    if method == "tophat":
        # Remove background structures larger than the observed arrow strokes.
        corrected = _elliptic_tophat(gray)
        return corrected, _threshold(corrected)
    if method == "adaptive":
        return gray, cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 61, -8)
    if method == "gaussian":
        values = gray.astype(np.float32)
        background = cv2.GaussianBlur(values, (0, 0), 15)
        corrected = cv2.normalize(np.maximum(values - background, 0), None,
                                  0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        return corrected, _threshold(corrected)
    raise ValueError(f"Unknown segmentation method: {method}")


@lru_cache(maxsize=1)
def _ellipse_rectangles():
    """Exact union of centered rectangles for OpenCV's 61-pixel ellipse."""
    ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61))
    rectangles = []
    seen = set()
    for y in range(31):
        width = int(ellipse[y].sum())
        if width not in seen:
            rectangles.append(np.ones((61 - 2*y, width), dtype=np.uint8))
            seen.add(width)
    return rectangles


def _elliptic_tophat(gray):
    # Erosion over a union is the minimum of its erosions; dilation is the
    # maximum. Rectangular kernels use OpenCV's faster separable operations.
    rectangles = _ellipse_rectangles()
    eroded = cv2.erode(gray, rectangles[0])
    for kernel in rectangles[1:]:
        check_deadline()
        cv2.min(eroded, cv2.erode(gray, kernel), eroded)
    opened = cv2.dilate(eroded, rectangles[0])
    for kernel in rectangles[1:]:
        check_deadline()
        cv2.max(opened, cv2.dilate(eroded, kernel), opened)
    return cv2.subtract(gray, opened)


def _clean_mask(binary, size=3):
    """Remove thin reticle lines; stronger cleanup is a bounded fallback."""
    kernel = (np.ones((3, 3), dtype=np.uint8) if size == 3
              else cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    return cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)


def _normalize(mask, size, stretch=False, antialias=False):
    interpolation = cv2.INTER_AREA if antialias else cv2.INTER_NEAREST
    points = cv2.findNonZero(mask)
    if points is None:
        raise ValueError("Empty arrow mask.")
    x, y, w, h = cv2.boundingRect(points)
    if stretch:
        canvas = np.zeros((size, size), dtype=np.uint8)
        canvas[4:-4, 4:-4] = cv2.resize(
            mask[y:y + h, x:x + w], (size - 8, size - 8),
            interpolation=interpolation)
        return canvas
    scale = (size - 8) / max(w, h)
    resized = cv2.resize(mask[y:y + h, x:x + w],
                         (max(1, round(w * scale)), max(1, round(h * scale))),
                         interpolation=interpolation)
    canvas = np.zeros((size, size), dtype=np.uint8)
    top = (size - resized.shape[0]) // 2
    left = (size - resized.shape[1]) // 2
    canvas[top:top + resized.shape[0], left:left + resized.shape[1]] = resized
    return canvas


def _contour_mask(contour, bounds):
    x, y, w, h = bounds
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.drawContours(mask, [contour - np.array([[[x, y]]])], -1, 255, cv2.FILLED)
    return mask


@lru_cache(maxsize=128)
def _load_template(path, modified_ns, file_size, size, stretch, antialias):
    # File metadata invalidates cached shapes when a template is replaced.
    binary = _threshold(_grayscale(read_image(path)))
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError(f"No shape in template: {path}")
    contour = max(contours, key=cv2.contourArea)
    mask = _contour_mask(contour, cv2.boundingRect(contour))
    normalized = _normalize(mask, size, stretch, antialias)
    normalized.flags.writeable = False
    return normalized


def _load_templates(directory, config, stretch=False):
    check_deadline()
    cache = _recognition_cache.get()
    banks = cache.setdefault("banks", {}) if cache is not None else {}
    key = (Path(directory), config.normalized_size, stretch, config.antialias)
    if key in banks:
        return banks[key]
    templates = {}
    for direction in DIRECTIONS:
        files = sorted((Path(directory) / direction).glob("*.png"))
        if not files:
            raise ValueError(f"Missing templates: {Path(directory) / direction}/*.png")
        templates[direction] = []
        for path in files:
            check_deadline()
            stat = path.stat()
            templates[direction].append(_load_template(
                path.resolve(), stat.st_mtime_ns, stat.st_size,
                config.normalized_size, stretch, config.antialias))
    # Rescan on the next request, not on every recursive fallback.
    if cache is not None:
        banks[key] = templates
    return templates


def _template_score(normalized, template, radius=0):
    """Allow at most two pixels of translation after bounding-box normalization."""
    check_deadline()
    if radius:
        normalized = cv2.copyMakeBorder(normalized, radius, radius, radius, radius,
                                        cv2.BORDER_CONSTANT, value=0)
    return float(cv2.matchTemplate(normalized, template, cv2.TM_CCOEFF_NORMED).max())


def _select_row(records, config):
    """Fit a sloped row; discard low-confidence shapes wholly off the row.

    Unknown shapes intersecting the row are retained and cause rejection.
    Confident outliers are retained too: they may indicate a second arrow row.
    """
    anchors = [record for record in records if record["direction"] is not None]
    if len(anchors) < 3:
        return records, None, "Insufficient reliable arrows to establish a row."
    boxes = np.array([record["bounds"] for record in anchors], dtype=float)
    centers = boxes[:, :2] + boxes[:, 2:] / 2
    slopes = [(b[1] - a[1]) / (b[0] - a[0])
              for i, a in enumerate(centers) for b in centers[i + 1:]
              if abs(b[0] - a[0]) > 1]
    if not slopes:
        return records, None, "Cannot establish a left-to-right arrow row."
    slope = float(np.median(slopes))
    intercept = float(np.median(centers[:, 1] - slope * centers[:, 0]))
    norm = float(np.hypot(slope, 1))
    median_height = np.median(boxes[:, 3])
    tolerance = config.row_tolerance * median_height
    selected = []
    for record in records:
        x, y, w, h = record["bounds"]
        distance = abs(y + h / 2 - slope * (x + w / 2) - intercept) / norm
        # Projection of the bounding box onto the line normal. Requiring the
        # entire box to be away from the row avoids deleting damaged arrows.
        radius = (abs(slope) * w + h) / (2 * norm)
        excluded = (record["direction"] is None
                    and distance - radius > tolerance)
        record["line_distance"] = float(distance)
        record["excluded_reason"] = "low_confidence_off_row" if excluded else None
        if not excluded:
            selected.append(record)
    line = {"slope": slope, "intercept": intercept, "tolerance": float(tolerance)}
    if any(record["line_distance"] > tolerance for record in selected):
        return selected, line, "Candidates do not form one sloped row."
    return selected, line, None


def _crosses_row(contour, line, offset):
    """Check an unresolved foreground contour against the extrapolated row."""
    points = contour.reshape(-1, 2).astype(float) + np.asarray(offset)
    distances = (points[:, 1] - line["slope"] * points[:, 0] - line["intercept"])
    distances /= np.hypot(line["slope"], 1)
    return bool(distances.min() <= line["tolerance"]
                and distances.max() >= -line["tolerance"])


def _deskew_row(image, roi, config, method):
    """Estimate row shear from contour centers without direction labels."""
    gray = _grayscale(image)
    x, y, w, h = roi if roi is not None else (0, 0, gray.shape[1], gray.shape[0])
    crop = image[y:y + h, x:x + w]
    binary = _clean_mask(_segment(gray[y:y + h, x:x + w], method)[1], 3)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for contour in contours:
        bounds = cv2.boundingRect(contour)
        cw, ch = bounds[2:]
        if (cv2.contourArea(contour) >= config.min_area
                and config.min_size <= min(cw, ch) and max(cw, ch) <= config.max_size
                and config.min_aspect <= cw / ch <= config.max_aspect):
            boxes.append(bounds)
    if len(boxes) < 3:
        raise RecognitionError("Insufficient contours to estimate row shear.")
    boxes = np.asarray(boxes, dtype=float)
    centers = boxes[:, :2] + boxes[:, 2:] / 2
    separation = np.median(boxes[:, 2])
    slopes = [(b[1] - a[1]) / (b[0] - a[0])
              for i, a in enumerate(centers) for b in centers[i + 1:]
              if abs(b[0] - a[0]) > separation]
    if not slopes:
        raise RecognitionError("Insufficient horizontal separation to estimate shear.")
    slope = float(np.median(slopes))
    if not 0.05 < abs(slope) < 0.7:
        raise RecognitionError("Row shear is negligible or outside the supported range.")
    offset = max(0, slope * (w - 1))
    matrix = np.float32([[1, 0, 0], [-slope, 1, offset]])
    height = int(np.ceil(h + abs(slope) * (w - 1)))
    warped = cv2.warpAffine(crop, matrix, (w, height), borderMode=cv2.BORDER_REPLICATE)
    return warped, slope


def recognize_directions(image, *, roi=None, template_dir=DEFAULT_TEMPLATES,
                         config=None, debug_dir=None) -> list[str]:
    """Recognize a single row, or raise RecognitionError instead of guessing.

    image: uint8 grayscale/BGR/BGRA array. roi: optional (x, y, width, height).
    Without roi, image must already be cropped to one arrow row.
    No screen capture, input injection, or UI dependency.
    """
    # Recursive fallbacks share intermediates; separate requests never do.
    token = None
    if _recognition_cache.get() is None:
        token = _recognition_cache.set({})
    try:
        return _recognize_directions(image, roi=roi, template_dir=template_dir,
                                     config=config, debug_dir=debug_dir)
    finally:
        if token is not None:
            _recognition_cache.reset(token)


def _recognize_directions(image, *, roi, template_dir, config, debug_dir):
    config = config or RecognitionConfig()
    if config.background_method not in ("tophat", "gaussian"):
        raise ValueError("background_method must be tophat or gaussian.")
    if config.alignment_radius not in (0, 1, 2):
        raise ValueError("alignment_radius must be 0, 1, or 2.")
    if config.segmentation != "auto":
        return _recognize_single(image, roi=roi, template_dir=template_dir,
                                 config=config, debug_dir=debug_dir)
    attempts = []
    sequence = None
    selected_attempt = None
    methods = ("otsu", config.background_method)
    trials = [(method, config.cleanup_size) for method in methods]
    if config.clean_thin_noise and config.cleanup_size == 3 and not config.antialias:
        trials.extend((method, 5) for method in methods)
    for method, cleanup_size in trials:
        label = method if cleanup_size == 3 else f"{method}_cleanup{cleanup_size}"
        attempt_dir = Path(debug_dir) / label if debug_dir is not None else None
        try:
            sequence = _recognize_single(
                image, roi=roi, template_dir=template_dir,
                config=replace(config, segmentation=method, cleanup_size=cleanup_size),
                debug_dir=attempt_dir)
        except RecognitionError as error:
            attempts.append({"method": method, "cleanup_size": cleanup_size,
                             "debug_subdir": label, "error": str(error)})
        else:
            attempts.append({"method": method, "cleanup_size": cleanup_size,
                             "debug_subdir": label, "error": None})
            break
    # Independent width/height normalization compensates for foreshortening.
    # Only accept agreement from both weak-cleanup segmentations: strong cleanup
    # can erase a faint end symbol and produce a convincing partial sequence.
    if sequence is None and config.clean_thin_noise and config.cleanup_size == 3:
        stretched = []
        for method in methods:
            label = f"{method}_stretch"
            attempt_dir = Path(debug_dir) / label if debug_dir is not None else None
            try:
                candidate = _recognize_single(
                    image, roi=roi, template_dir=template_dir,
                    config=replace(config, segmentation=method, cleanup_size=3),
                    debug_dir=attempt_dir, stretch=True)
            except RecognitionError as error:
                attempts.append({"method": method, "cleanup_size": 3,
                                 "debug_subdir": label, "error": str(error)})
                break
            stretched.append(candidate)
            attempts.append({"method": method, "cleanup_size": 3,
                             "debug_subdir": label, "sequence": candidate,
                             "error": None})
        if len(stretched) == 2:
            if stretched[0] == stretched[1]:
                sequence = stretched[0]
            else:
                attempts[-1]["error"] = "Stretched segmentation sequences disagree."
                attempts[-1]["ambiguous"] = True
    if (sequence is None and config.deskew_fallback
            and config.clean_thin_noise and config.cleanup_size == 3):
        corrected_sequences = []
        slopes = []
        for method in methods:
            label = f"deskew_{method}"
            attempt = {"method": method, "debug_subdir": label, "error": None}
            attempts.append(attempt)
            try:
                warped, slope = _deskew_row(image, roi, config, method)
                attempt["slope"] = slope
                if slopes and abs(slope - slopes[0]) > 0.1:
                    attempt["ambiguous"] = True
                    raise RecognitionError("Row shear estimates disagree.")
                slopes.append(slope)
                folder = Path(debug_dir) / label if debug_dir is not None else None
                if folder is not None:
                    folder.mkdir(parents=True, exist_ok=True)
                    _write_image(folder / "deskewed.png", warped)
                candidate = recognize_directions(
                    warped, template_dir=template_dir,
                    config=replace(config, deskew_fallback=False, view_fallback=False,
                                   alignment_fallback=False, antialias_fallback=False,
                                   template_fallback=False), debug_dir=folder)
                corrected_sequences.append(candidate)
                attempt["sequence"] = candidate
            except RecognitionError as error:
                attempt["error"] = str(error)
                break
        if len(corrected_sequences) == 2:
            if corrected_sequences[0] == corrected_sequences[1]:
                sequence = corrected_sequences[0]
            else:
                attempts[-1]["error"] = "Deskewed segmentation sequences disagree."
                attempts[-1]["ambiguous"] = True
    if (sequence is None and config.view_fallback
            and config.clean_thin_noise and config.cleanup_size == 3):
        from .refinements import horizontal_views

        def recognize_view(shear, view, background):
            label = f"view_{shear:+.3f}_{background}"
            attempt = {"method": background, "shear": shear,
                       "debug_subdir": label, "error": None}
            folder = Path(debug_dir) / label if debug_dir is not None else None
            if folder is not None:
                folder.mkdir(parents=True, exist_ok=True)
                _write_image(folder / "input.png", view)
            try:
                attempt["sequence"] = recognize_directions(
                    view, template_dir=template_dir,
                    config=replace(config, view_fallback=False,
                                   background_method=background,
                                   alignment_fallback=False, antialias_fallback=False,
                                   template_fallback=False), debug_dir=folder)
            except RecognitionError:
                attempt["error"] = "Corrected view rejected."
            return attempt

        successful = []
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="terminal-view") as workers:
            pending = [workers.submit(copy_context().run, recognize_view, shear, view, background)
                       for shear, view in horizontal_views(image, roi)
                       for background in ("tophat", "gaussian")
                       if shear != 0 or background != config.background_method]
            # Preserve trial order and compare every successful result.
            for future in pending:
                attempt = future.result()
                attempts.append(attempt)
                if attempt["error"] is None:
                    successful.append(attempt)
        if successful:
            if all(item["sequence"] == successful[0]["sequence"] for item in successful):
                selected_attempt = successful[0]
                sequence = selected_attempt["sequence"]
            else:
                attempts.append({"method": "view_consensus", "debug_subdir": None,
                                 "ambiguous": True,
                                 "error": "Corrected views disagree; refusing ambiguous sequence."})
    if (sequence is None and config.alignment_fallback and config.alignment_radius == 0
            and config.clean_thin_noise and not any(a.get("ambiguous") for a in attempts)):
        label = "alignment2"
        attempt = {"method": label, "debug_subdir": label, "error": None}
        attempts.append(attempt)
        try:
            sequence = recognize_directions(
                image, roi=roi, template_dir=template_dir,
                config=replace(config, alignment_radius=2, alignment_fallback=False,
                               antialias_fallback=False, template_fallback=False),
                debug_dir=Path(debug_dir) / label if debug_dir is not None else None)
        except RecognitionError:
            attempt["error"] = "Aligned template matching rejected."
        else:
            attempt["sequence"] = sequence
            selected_attempt = attempt
    if (sequence is None and config.antialias_fallback and not config.antialias
            and config.view_fallback and config.deskew_fallback and config.clean_thin_noise
            and config.cleanup_size == 3 and not any(a.get("ambiguous") for a in attempts)):
        label = "antialias"
        attempt = {"method": label, "debug_subdir": label, "error": None}
        attempts.append(attempt)
        try:
            sequence = recognize_directions(
                image, roi=roi, template_dir=template_dir,
                config=replace(config, antialias=True, antialias_fallback=False,
                               template_fallback=False),
                debug_dir=Path(debug_dir) / label if debug_dir is not None else None)
        except RecognitionError:
            attempt["error"] = "Antialiased matching rejected."
        else:
            attempt["sequence"] = sequence
            selected_attempt = attempt
    if (sequence is None and config.template_fallback and config.view_fallback
            and config.deskew_fallback and config.clean_thin_noise and config.cleanup_size == 3
            and Path(template_dir).resolve() == DEFAULT_TEMPLATES.resolve()
            and not any(a.get("ambiguous") for a in attempts)):
        label = "slanted_templates"
        attempt = {"method": label, "debug_subdir": label, "error": None}
        attempts.append(attempt)
        try:
            sequence = recognize_directions(
                image, roi=roi, template_dir=SLANTED_TEMPLATES,
                config=replace(config, template_fallback=False),
                debug_dir=Path(debug_dir) / label if debug_dir is not None else None)
        except RecognitionError:
            attempt["error"] = "Slanted template bank rejected."
        else:
            attempt["sequence"] = sequence
            selected_attempt = attempt
    if (sequence is None and config.template_fallback
            and config.view_fallback and config.deskew_fallback
            and config.clean_thin_noise and config.cleanup_size == 3
            and Path(template_dir).resolve() == DEFAULT_TEMPLATES.resolve()
            and not any(a.get("ambiguous") for a in attempts)):
        # Perspective varies along long rows. One bank alone may not cover every
        # arrow; compare all directions against both banks, keeping score/margin.
        combined = []
        for method in methods:
            label = f"combined_{method}"
            attempt = {"method": label, "debug_subdir": label, "error": None}
            attempts.append(attempt)
            try:
                candidate = _recognize_single(
                    image, roi=roi, template_dir=template_dir,
                    config=replace(config, segmentation=method, antialias=True, alignment_radius=2),
                    debug_dir=Path(debug_dir) / label if debug_dir else None,
                    supplemental_templates=SLANTED_TEMPLATES)
                combined.append(candidate)
                attempt["sequence"] = candidate
            except RecognitionError as error:
                attempt["error"] = str(error)
        if combined and all(candidate == combined[0] for candidate in combined):
            sequence = combined[0]
            selected_attempt = next(a for a in attempts
                                    if a["method"].startswith("combined_")
                                    and a.get("sequence") == sequence)
        elif combined:
            attempts.append({"method": "combined_consensus", "debug_subdir": None,
                             "ambiguous": True,
                             "error": "Combined template segmentations disagree."})
    if debug_dir is not None:
        output = Path(debug_dir)
        output.mkdir(parents=True, exist_ok=True)
        selection = selected_attempt or attempts[-1]
        (output / "result.json").write_text(json.dumps({
            "config": asdict(config), "attempts": attempts, "sequence": sequence,
            "selected_method": selection["method"] if sequence is not None else None,
            "selected_debug_subdir": selection["debug_subdir"] if sequence is not None else None,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
    if sequence is None:
        raise RecognitionError("All segmentation attempts rejected: " + "; ".join(
            f"{attempt['debug_subdir']}: {attempt['error']}" for attempt in attempts))
    return sequence


def _recognize_single(image, *, roi, template_dir, config, debug_dir, stretch=False,
                               supplemental_templates=None):
    if config.cleanup_size not in (3, 5):
        raise ValueError("cleanup_size must be 3 or 5.")
    if not (0 <= config.score_threshold <= 1 and 0 <= config.score_margin <= 2):
        raise ValueError("Invalid confidence thresholds.")
    if (config.normalized_size < 16 or config.min_area <= 0
            or not 0 < config.min_size <= config.max_size
            or not 0 < config.min_aspect <= config.max_aspect
            or config.row_tolerance <= 0 or config.max_gap_ratio <= 0):
        raise ValueError("Invalid geometry parameters.")
    gray_full = _grayscale(image)
    height, width = gray_full.shape
    x, y, w, h = roi if roi is not None else (0, 0, width, height)
    if min(x, y) < 0 or min(w, h) <= 0 or x + w > width or y + h > height:
        raise ValueError("ROI must be entirely inside the image.")
    gray = gray_full[y:y + h, x:x + w]
    corrected, binary = _segment(gray, config.segmentation)
    raw_binary = binary
    if config.clean_thin_noise:
        binary = _clean_mask(binary, config.cleanup_size)
    debug = Path(debug_dir) if debug_dir is not None else None
    if debug:
        debug.mkdir(parents=True, exist_ok=True)
        _write_image(debug / "roi.png", image[y:y + h, x:x + w])
        _write_image(debug / "grayscale.png", gray)
        _write_image(debug / "corrected.png", corrected)
        _write_image(debug / "threshold_raw.png", raw_binary)
        _write_image(debug / "threshold.png", binary)
    templates = _load_templates(template_dir, config, stretch)
    if supplemental_templates is not None:
        additional = _load_templates(supplemental_templates, config, stretch)
        templates = {direction: variants + additional[direction]
                     for direction, variants in templates.items()}
    cache = _recognition_cache.get()
    matchers = cache.setdefault("matchers", {}) if cache is not None else {}
    matcher_key = (Path(template_dir), config.normalized_size, stretch, config.antialias,
                   config.alignment_radius, supplemental_templates)
    if matcher_key not in matchers:
        matchers[matcher_key] = TemplateMatcher(templates, config.alignment_radius)
    matcher = matchers[matcher_key]
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if debug:
        boxes_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        annotated = cv2.cvtColor(gray_full, cv2.COLOR_GRAY2BGR)
    candidates = []
    oversized = []
    for contour in contours:
        bounds = cx, cy, cw, ch = cv2.boundingRect(contour)
        valid = (cv2.contourArea(contour) >= config.min_area
                 and config.min_size <= min(cw, ch)
                 and max(cw, ch) <= config.max_size
                 and config.min_aspect <= cw / ch <= config.max_aspect)
        if debug:
            cv2.rectangle(boxes_image, (cx, cy), (cx + cw, cy + ch),
                          (0, 200, 0) if valid else (0, 0, 200), 1)
        if valid:
            candidates.append((bounds, contour))
        elif max(cw, ch) > config.max_size and cv2.contourArea(contour) >= config.min_area:
            oversized.append((bounds, contour))
    candidates.sort(key=lambda item: item[0][0])
    records = []
    for index, (bounds, contour) in enumerate(candidates):
        cx, cy, cw, ch = bounds
        normalized = _normalize(_contour_mask(contour, bounds), config.normalized_size, stretch, config.antialias)
        scores = matcher.scores(normalized)
        ranked = sorted(scores, key=scores.get, reverse=True)
        best, runner_up = ranked[:2]
        accepted = (scores[best] >= config.score_threshold
                    and scores[best] - scores[runner_up] >= config.score_margin)
        records.append({"bounds": [x + cx, y + cy, cw, ch], "scores": scores,
                        "direction": best if accepted else None})
        if debug:
            color = (0, 220, 0) if accepted else (0, 0, 255)
            cv2.rectangle(annotated, (x + cx, y + cy), (x + cx + cw, y + cy + ch), color, 1)
            cv2.putText(annotated, f"{best if accepted else 'unknown'} {scores[best]:.2f}",
                        (x + cx, max(12, y + cy - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            _write_image(debug / f"arrow_{index:02d}.png", gray[cy:cy + ch, cx:cx + cw])
            _write_image(debug / f"arrow_{index:02d}_normalized.png", normalized)
    selected, row_line, row_error = _select_row(records, config)
    blockers = [list(bounds) for bounds, contour in oversized
                if row_line is not None and _crosses_row(contour, row_line, (x, y))]
    error = None
    if not records:
        error = "No arrow candidates found. Check ROI and segmentation."
    elif any(record["direction"] is None for record in selected):
        error = "Unrecognized candidate; refusing to return a partial sequence."
    elif row_error:
        error = row_error
    elif blockers:
        error = "Oversized unresolved foreground intersects the row; symbols may be hidden."
    else:
        boxes = np.array([record["bounds"] for record in selected])
        centers_x = boxes[:, 0] + boxes[:, 2] / 2
        if np.any(np.diff(centers_x) > config.max_gap_ratio * np.median(boxes[:, 2])):
            error = "Large gap between candidates; a symbol may be missing."
    sequence = [record["direction"] for record in selected] if error is None else None
    if debug:
        for record in records:
            if record.get("excluded_reason"):
                bx, by, bw, bh = record["bounds"]
                cv2.rectangle(annotated, (bx, by), (bx + bw, by + bh), (0, 165, 255), 2)
                cv2.putText(annotated, "off-row", (bx, by + bh + 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 165, 255), 1)
        _write_image(debug / "contours.png", boxes_image)
        _write_image(debug / "result.png", annotated)
        (debug / "result.json").write_text(json.dumps({
            "roi": [x, y, w, h], "config": asdict(config), "stretch": stretch,
            "candidates": records, "row_line": row_line,
            "blocking_bounds_in_roi": blockers,
            "sequence": sequence, "error": error,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
    if error:
        raise RecognitionError(error)
    return sequence
