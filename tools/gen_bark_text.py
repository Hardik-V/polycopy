#!/usr/bin/env python3
"""
Warp BARK.buf carved lettering to new text by remapping vertex XY in-place.

Keeps original bark topology, UVs, normals, and materials — only reshapes the
embossed letter silhouettes.

Usage:
    python3 tools/gen_bark_text.py "hardik verma"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from buf_codec import parse, serialize
from gen_sustainability_text import _layout_polys, _remap_xy

REF = ROOT / "public/models/BARK.buf.orig-sustainability"
FALLBACK = ROOT / "public/models/BARK.buf"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="?", default="hardik verma")
    args = parser.parse_args()

    src = REF if REF.exists() else FALLBACK
    out_path = ROOT / "public/models/BARK.buf"
    bak = out_path.with_suffix(".buf.orig-sustainability")
    if not bak.exists() and out_path.exists():
        bak.write_bytes(out_path.read_bytes())

    buf = parse(src)
    pos = buf.attr("position").data.copy()
    sx0, sx1 = float(pos[:, 0].min()), float(pos[:, 0].max())
    sy0, sy1 = float(pos[:, 1].min()), float(pos[:, 1].max())

    # Lettering lives in the central band of the bark patch
    letter_mask = pos[:, 1] > (sy0 + (sy1 - sy0) * 0.15)
    if letter_mask.sum() < 100:
        letter_mask = np.ones(len(pos), dtype=bool)

    target_w = (sx1 - sx0) * 0.85
    target_h = (sy1 - sy0) * 0.35
    polys = _layout_polys(args.text, target_w, target_h)

    # Baseline height from low vertices in letter band
    base_y = float(np.percentile(pos[~letter_mask, 1], 75)) if (~letter_mask).any() else float(
        np.percentile(pos[:, 1], 20)
    )

    rel = pos[letter_mask, 1] - base_y
    rel_height = np.clip(rel / max(rel.max(), 1e-6), 0, 1)

    new_xy = _remap_xy(pos[letter_mask, :2], (sx0, sx1, sy0, sy1), polys)
    out = pos.copy()
    out[letter_mask, :2] = new_xy
    # Restore emboss height profile
    out[letter_mask, 1] = base_y + rel_height * (rel.max() if rel.max() > 0 else 0.008)

    pos_attr = buf.attr("position")
    from buf_codec import auto_pack_params

    f, d = auto_pack_params(out, 3)
    pos_attr.data = out.astype(np.float32)
    pos_attr.packed_from = f
    pos_attr.packed_delta = d

    out_path.write_bytes(serialize(buf))
    print(f"Warped {out_path} ({buf.vertex_count} verts) -> {args.text!r}")


if __name__ == "__main__":
    main()
