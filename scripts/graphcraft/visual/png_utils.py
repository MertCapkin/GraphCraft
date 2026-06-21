"""PNG utilities for visual review (stdlib + optional Pillow)."""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Any


def png_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", data[16:24])
    return int(width), int(height)


def pixel_similarity(reference: Path, candidate: Path) -> dict[str, Any]:
    dims_ref = png_dimensions(reference)
    dims_cand = png_dimensions(candidate)

    result: dict[str, Any] = {
        "reference": str(reference),
        "candidate": str(candidate),
        "reference_dims": dims_ref,
        "candidate_dims": dims_cand,
        "method": "dimensions",
        "similarity": None,
        "overall": "WARN",
    }

    if dims_ref is None or dims_cand is None:
        result["overall"] = "FAIL"
        result["error"] = "Invalid or missing PNG"
        return result

    if dims_ref != dims_cand:
        result["overall"] = "WARN"
        result["error"] = f"Dimension mismatch {dims_ref} vs {dims_cand}"
        return result

    try:
        from PIL import Image  # type: ignore
    except ImportError:
        result["similarity"] = 1.0 if dims_ref == dims_cand else 0.0
        result["note"] = "Install Pillow for pixel diff: pip install MertCapkin_GraphCraft[visual]"
        result["overall"] = "WARN"
        return result

    ref = Image.open(reference).convert("RGBA")
    cand = Image.open(candidate).convert("RGBA")
    if ref.size != cand.size:
        ref = ref.resize(cand.size)

    ref_px = list(ref.getdata())
    cand_px = list(cand.getdata())
    total = len(ref_px)
    if total == 0:
        result["overall"] = "FAIL"
        return result

    diff_sum = 0
    for rp, cp in zip(ref_px, cand_px):
        diff_sum += sum(abs(int(rp[i]) - int(cp[i])) for i in range(3))
    max_diff = total * 3 * 255
    similarity = 1.0 - (diff_sum / max_diff)
    result["method"] = "pixel_rms"
    result["similarity"] = round(similarity, 4)

    if similarity >= 0.95:
        result["overall"] = "PASS"
    elif similarity >= 0.85:
        result["overall"] = "WARN"
    else:
        result["overall"] = "FAIL"
    return result
