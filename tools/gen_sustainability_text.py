#!/usr/bin/env python3
"""
Regenerate sustainability_text.buf + sustainability_text_outline.buf with new copy.

The engine bakes peel-animation params into these meshes (position.z = curveu,
OP.z = perimeter, etc.). We regenerate fill + outline from a font outline while
preserving the same attribute layout the shaders expect.

Usage (from repo root):
    python3 tools/gen_sustainability_text.py "hardik verma"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import mapbox_earcut as earcut
import matplotlib

matplotlib.use("Agg")
import numpy as np
from matplotlib import font_manager as fm
from matplotlib.textpath import TextPath

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from buf_codec import Attribute, BufFile, auto_pack_params, parse, serialize

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def _pick_font() -> str:
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return str(p)
    raise FileNotFoundError("No usable font found for text mesh generation")


def _text_polys(text: str, target_w: float, target_h: float) -> list[np.ndarray]:
    prop = fm.FontProperties(fname=_pick_font(), size=100)
    path = TextPath((0, 0), text, prop=prop)
    polys = [p for p in path.to_polygons() if len(p) >= 3]
    if not polys:
        raise ValueError(f"No polygons for text: {text!r}")

    all_pts = np.vstack(polys)
    minxy = all_pts.min(0)
    maxxy = all_pts.max(0)
    size = maxxy - minxy
    scale = min(target_w / size[0], target_h / size[1]) * 0.92

    out: list[np.ndarray] = []
    for poly in polys:
        p = (poly - minxy - size / 2) * scale
        out.append(p.astype(np.float64))
    return out


def _triangulate_polys(polys: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    verts_list: list[np.ndarray] = []
    tris_list: list[np.ndarray] = []
    offset = 0
    for poly in polys:
        v = poly.astype(np.float32)
        tri = earcut.triangulate_float32(v, np.array([len(v)], dtype=np.uint32))
        tri = tri.reshape(-1, 3) + offset
        verts_list.append(v)
        tris_list.append(tri)
        offset += len(v)
    verts = np.vstack(verts_list)
    tris = np.vstack(tris_list)
    return verts, tris


def _build_fill(text: str, ref: BufFile) -> BufFile:
    ref_pos = ref.attr("position").data
    target_w = float(np.ptp(ref_pos[:, 0]))
    target_h = float(np.ptp(ref_pos[:, 1]))

    polys = _text_polys(text, target_w, target_h)
    verts, tris = _triangulate_polys(polys)

    curveu = (verts[:, 0] - verts[:, 0].min()) / (np.ptp(verts[:, 0]) + 1e-9)
    pos = np.column_stack([verts, curveu]).astype(np.float32)

    from_list, delta_list = auto_pack_params(pos, 3)
    pos_attr = Attribute(
        id="position",
        component_size=3,
        storage_type="Uint16Array",
        needs_pack=True,
        packed_from=from_list,
        packed_delta=delta_list,
        data=pos,
    )
    idx_attr = Attribute(
        id="indices",
        component_size=1,
        storage_type="Uint16Array",
        needs_pack=False,
        data=tris.reshape(-1).astype(np.uint16),
    )

    return BufFile(
        vertex_count=len(pos),
        index_count=len(tris) * 3,
        mesh_type=ref.mesh_type,
        attributes=[idx_attr, pos_attr],
        extra_meta=dict(ref.extra_meta),
    )


def _outline_from_fill(fill: BufFile, ref_outline: BufFile, thickness: float = 0.012) -> BufFile:
    """Build a simple outline mesh by offsetting fill vertices along 2D normals."""
    pos = fill.attr("position").data
    idx = fill.attr("indices").data.astype(np.int64).reshape(-1, 3)

    # Per-vertex normal via angle bisector from incident edges
    n_verts = len(pos)
    accum = np.zeros((n_verts, 2), dtype=np.float64)
    for tri in idx:
        for i in range(3):
            a, b, c = tri[i], tri[(i + 1) % 3], tri[(i + 2) % 3]
            e1 = pos[b, :2] - pos[a, :2]
            e2 = pos[c, :2] - pos[a, :2]
            ln1 = np.linalg.norm(e1)
            ln2 = np.linalg.norm(e2)
            if ln1 < 1e-9 or ln2 < 1e-9:
                continue
            n1 = np.array([-e1[1], e1[0]]) / ln1
            n2 = np.array([e2[1], -e2[0]]) / ln2
            accum[a] += n1 + n2

    norms = np.linalg.norm(accum, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-9)
    normals = accum / norms

    inner = pos.copy()
    outer = pos.copy()
    outer[:, :2] += normals * thickness
  # perimeter ~ word arc length scale stored in OP.z (match ref range)
    perimeter_val = float(ref_outline.attr("OP").data[:, 2].max())
    outer[:, 2] = perimeter_val * 0.85

    # id groups by x-cluster (glyph-ish)
    ids = np.zeros(n_verts, dtype=np.uint16)
    xbins = np.linspace(inner[:, 0].min(), inner[:, 0].max(), 16)
    for i in range(len(xbins) - 1):
        m = (inner[:, 0] >= xbins[i]) & (inner[:, 0] < xbins[i + 1])
        ids[m] = min(i, 13)

    radius = np.zeros(n_verts, dtype=np.uint8)
    # corners: vertices with large turning angle get radius 1
    for v in range(n_verts):
        neighbors = idx[(idx == v).any(axis=1)]
        if len(neighbors) < 2:
            continue
        angles = []
        for tri in neighbors[:6]:
            others = [t for t in tri if t != v]
            if len(others) != 2:
                continue
            e1 = pos[others[0], :2] - pos[v, :2]
            e2 = pos[others[1], :2] - pos[v, :2]
            c = np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2) + 1e-9)
            angles.append(np.arccos(np.clip(c, -1, 1)))
        if angles and min(angles) < np.pi * 0.55:
            radius[v] = 1

    # Outline uses the same triangle topology as the fill mesh.
    outline_idx = idx.reshape(-1).astype(np.uint16)

    def _packed_attr(id_: str, data: np.ndarray, storage: str) -> Attribute:
        if id_ in ("id", "radius"):
            return Attribute(
                id=id_,
                component_size=1,
                storage_type=storage,
                needs_pack=False,
                data=data,
            )
        from_list, delta_list = auto_pack_params(data, data.shape[1] if data.ndim > 1 else 1)
        return Attribute(
            id=id_,
            component_size=data.shape[1] if data.ndim > 1 else 1,
            storage_type=storage,
            needs_pack=True,
            packed_from=from_list,
            packed_delta=delta_list,
            data=data,
        )

    attrs = [
        _packed_attr("OP", outer.astype(np.float32), "Int16Array"),
        Attribute(id="id", component_size=1, storage_type="Uint16Array", needs_pack=False, data=ids),
        Attribute(
            id="indices",
            component_size=1,
            storage_type="Uint16Array",
            needs_pack=False,
            data=outline_idx.astype(np.uint16),
        ),
        _packed_attr("position", inner.astype(np.float32), "Uint16Array"),
        Attribute(id="radius", component_size=1, storage_type="Uint8Array", needs_pack=False, data=radius),
    ]

    return BufFile(
        vertex_count=n_verts,
        index_count=len(outline_idx),
        mesh_type=ref_outline.mesh_type,
        attributes=attrs,
        extra_meta=dict(ref_outline.extra_meta),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="?", default="hardik verma")
    args = parser.parse_args()

    text_path = ROOT / "public/models/sustainability_text.buf"
    outline_path = ROOT / "public/models/sustainability_text_outline.buf"

    ref_fill = parse(text_path)
    ref_outline = parse(outline_path)

    fill = _build_fill(args.text, ref_fill)
    outline = _outline_from_fill(fill, ref_outline)

    backup_suffix = ".orig-sustainability"
    for p in (text_path, outline_path):
        bak = p.with_suffix(p.suffix + backup_suffix)
        if not bak.exists():
            bak.write_bytes(p.read_bytes())

    text_path.write_bytes(serialize(fill))
    outline_path.write_bytes(serialize(outline))
    print(f"Wrote {text_path} ({fill.vertex_count} verts)")
    print(f"Wrote {outline_path} ({outline.vertex_count} verts)")


if __name__ == "__main__":
    main()
