#!/usr/bin/env python3
"""
Regenerate sustainability_text*.buf by warping the original Lusion meshes.

The peel shader bakes curveu, perimeter, radius, and outline topology into the
assets. Re-triangulating from scratch breaks lighting and animation. Instead we
keep the original connectivity and remap XY (plus outline offsets) to fit new
copy inside the same bounds.

Usage (from repo root):
    python3 tools/gen_sustainability_text.py "hardik verma"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np
from matplotlib import font_manager as fm
from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MplPath

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from buf_codec import Attribute, BufFile, auto_pack_params, parse, serialize

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REF_FILL = ROOT / "public/models/sustainability_text.buf.orig-sustainability"
REF_OUTLINE = ROOT / "public/models/sustainability_text_outline.buf.orig-sustainability"
FALLBACK_FILL = ROOT / "public/models/sustainability_text.buf"
FALLBACK_OUTLINE = ROOT / "public/models/sustainability_text_outline.buf"


def _ref_paths() -> tuple[Path, Path]:
    fill = REF_FILL if REF_FILL.exists() else FALLBACK_FILL
    outline = REF_OUTLINE if REF_OUTLINE.exists() else FALLBACK_OUTLINE
    return fill, outline


def _layout_polys(text: str, target_w: float, target_h: float) -> list[np.ndarray]:
    """Build letter outlines scaled to the original sustainability bounds."""
    prop = fm.FontProperties(fname=FONT, size=100)
    tp = TextPath((0, 0), text, prop=prop)
    polys = [p for p in tp.to_polygons() if len(p) >= 3]
    if not polys:
        raise ValueError(f"no polygons for {text!r}")

    pts = np.vstack(polys)
    minxy, maxxy = pts.min(0), pts.max(0)
    size = maxxy - minxy
    # Fill width like the original word; slightly shorter height for descenders
    sx = (target_w * 0.96) / max(size[0], 1e-6)
    sy = (target_h * 0.88) / max(size[1], 1e-6)
    scale = min(sx, sy)
    center = (minxy + maxxy) * 0.5

    out = []
    for poly in polys:
        p = (poly - center) * scale
        out.append(p.astype(np.float64))
    return out


def _point_in_polys(x: float, y: float, polys: list[np.ndarray]) -> bool:
    for poly in polys:
        if MplPath(poly).contains_point((x, y)):
            return True
    return False


def _nearest_on_boundary(x: float, y: float, polys: list[np.ndarray]) -> np.ndarray:
    """Nearest point on polygon edges to (x, y)."""
    p = np.array([x, y], dtype=np.float64)
    best = p
    best_d = np.inf
    for poly in polys:
        for i in range(len(poly)):
            a = poly[i]
            b = poly[(i + 1) % len(poly)]
            seg = b - a
            seg_len2 = float(np.dot(seg, seg)) + 1e-12
            t = float(np.clip(np.dot(p - a, seg) / seg_len2, 0.0, 1.0))
            proj = a + t * seg
            d = float(np.linalg.norm(proj - p))
            if d < best_d:
                best_d = d
                best = proj
    return best


def _remap_xy(
    xy: np.ndarray,
    src_bounds: tuple[float, float, float, float],
    dst_polys: list[np.ndarray],
) -> np.ndarray:
    """Proportional horizontal remap + vertical snap to new glyph shapes."""
    sx0, sx1, sy0, sy1 = src_bounds
    xs = xy[:, 0]
    ys = xy[:, 1]
    t = (xs - sx0) / max(sx1 - sx0, 1e-9)

  # target horizontal span from layout polys
    allp = np.vstack(dst_polys)
    dx0, dx1 = float(allp[:, 0].min()), float(allp[:, 0].max())
    dy0, dy1 = float(allp[:, 1].min()), float(allp[:, 1].max())

    nx = dx0 + t * (dx1 - dx0)
    # preserve relative vertical position within word band, then snap to surface
    rel_y = (ys - sy0) / max(sy1 - sy0, 1e-9)
    ny = dy0 + rel_y * (dy1 - dy0)

    out = np.column_stack([nx, ny])
    # Pull interior points onto fill; boundary points handled separately
    for i in range(len(out)):
        if _point_in_polys(out[i, 0], out[i, 1], dst_polys):
            continue
        out[i] = _nearest_on_boundary(out[i, 0], out[i, 1], dst_polys)
    return out


def _warp_fill(text: str, ref: BufFile) -> BufFile:
    ref_pos = ref.attr("position").data.copy()
    sx0, sx1 = float(ref_pos[:, 0].min()), float(ref_pos[:, 0].max())
    sy0, sy1 = float(ref_pos[:, 1].min()), float(ref_pos[:, 1].max())
    target_w, target_h = sx1 - sx0, sy1 - sy0

    polys = _layout_polys(text, target_w, target_h)
    new_xy = _remap_xy(ref_pos[:, :2], (sx0, sx1, sy0, sy1), polys)

    out = ref_pos.copy()
    out[:, :2] = new_xy
    # Keep original curveu (position.z) — encodes peel timing along strokes

    pos_attr = ref.attr("position")
    from_list, delta_list = auto_pack_params(out, 3)
    pos_attr.data = out.astype(np.float32)
    pos_attr.packed_from = from_list
    pos_attr.packed_delta = delta_list

    return ref


def _warp_outline(text: str, ref: BufFile, fill_bounds) -> BufFile:
    inner = ref.attr("position").data.copy()
    outer = ref.attr("OP").data.copy()
    src_bounds = fill_bounds

    polys = _layout_polys(text, src_bounds[2], src_bounds[3])
    inner[:, :2] = _remap_xy(inner[:, :2], src_bounds, polys)

    # Preserve original inner→outer offset vectors (thickness + peel normals)
    offset = outer[:, :2] - ref.attr("position").data[:, :2]
    outer[:, :2] = inner[:, :2] + offset
    # Keep OP.z (perimeter), id, radius, indices unchanged

    for attr in ref.attributes:
        if attr.id == "position":
            f, d = auto_pack_params(inner, 3)
            attr.data = inner.astype(np.float32)
            attr.packed_from, attr.packed_delta = f, d
        elif attr.id == "OP":
            f, d = auto_pack_params(outer, 3)
            attr.data = outer.astype(np.float32)
            attr.packed_from, attr.packed_delta = f, d

    return ref


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="?", default="hardik verma")
    args = parser.parse_args()

    fill_path = ROOT / "public/models/sustainability_text.buf"
    outline_path = ROOT / "public/models/sustainability_text_outline.buf"
    ref_fill_path, ref_outline_path = _ref_paths()

    ref_fill = parse(ref_fill_path)
    ref_outline = parse(ref_outline_path)

    orig_fill_pos = ref_fill.attr("position").data.copy()
    fill_bounds = (
        float(orig_fill_pos[:, 0].min()),
        float(orig_fill_pos[:, 0].max()),
        float(orig_fill_pos[:, 1].min()),
        float(orig_fill_pos[:, 1].max()),
    )

    fill = _warp_fill(args.text, ref_fill)
    outline = _warp_outline(args.text, ref_outline, fill_bounds)

    for p in (fill_path, outline_path):
        bak = p.with_suffix(p.suffix + ".orig-sustainability")
        if not bak.exists() and p.exists():
            bak.write_bytes(p.read_bytes())

    fill_path.write_bytes(serialize(fill))
    outline_path.write_bytes(serialize(outline))
    print(f"Warped fill -> {fill_path} ({fill.vertex_count} verts)")
    print(f"Warped outline -> {outline_path} ({outline.vertex_count} verts)")


if __name__ == "__main__":
    main()
