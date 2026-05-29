#!/usr/bin/env python3
"""
Re-emboss BARK.buf with new text and refresh bark.webp albedo.

The sustainability bark close-up ships with "sustainability" carved into the
geometry (BARK.buf) and painted into bark.webp. DOM copy changes do not affect
either — this script flattens the old lettering in UV space and stamps new text.

Usage (from repo root):
    python3 tools/gen_bark_text.py "hardik verma"
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
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from buf_codec import parse, serialize

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def _pick_font() -> str:
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return str(p)
    raise FileNotFoundError("No font for bark text")


def _render_text_mask(size: int, text: str) -> np.ndarray:
    """Return float32 height mask in [0, 1] with text centered."""
    prop = fm.FontProperties(fname=_pick_font())
    font_size = 120
    tp = None
    while font_size > 20:
        prop.set_size(font_size)
        tp = TextPath((0, 0), text, prop=prop)
        polys = [p for p in tp.to_polygons() if len(p) >= 3]
        if not polys:
            font_size -= 8
            continue
        pts = np.vstack(polys)
        if np.ptp(pts[:, 0]) < size * 0.78:
            break
        font_size -= 6
    if tp is None:
        raise ValueError(f"Could not layout text: {text!r}")

    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch
    from matplotlib.transforms import Affine2D

    polys = [p for p in tp.to_polygons() if len(p) >= 3]
    pts = np.vstack(polys)
    cx, cy = pts.mean(0)
    offset = Affine2D().translate(size / 2 - cx, size / 2 - cy)

    fig = plt.figure(figsize=(size / 100, size / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, size)
    ax.set_ylim(0, size)
    ax.axis("off")
    ax.add_patch(
        PathPatch(tp, facecolor="white", edgecolor="none", transform=offset + ax.transData)
    )
    fig.canvas.draw()
    mask = np.asarray(fig.canvas.buffer_rgba())[..., 0].astype(np.float32) / 255.0
    plt.close(fig)
    return mask


def _update_bark_mesh(bark_path: Path, text_mask: np.ndarray, emboss: float = 0.0075) -> None:
    buf = parse(bark_path)
    pos = buf.attr("position").data.copy()
    uv = buf.attr("uv").data
    size = text_mask.shape[0]

    # Height field from mesh (max Y per texel)
    y_grid = np.full((size, size), -1e9, dtype=np.float32)
    counts = np.zeros((size, size), dtype=np.int32)
    ui = np.clip((uv[:, 0] * (size - 1)).astype(np.int32), 0, size - 1)
    vi = np.clip((uv[:, 1] * (size - 1)).astype(np.int32), 0, size - 1)
    for i in range(len(pos)):
        u, v = ui[i], vi[i]
        if pos[i, 1] > y_grid[v, u]:
            y_grid[v, u] = pos[i, 1]

    valid = counts  # unused but kept for clarity
    base = y_grid.copy()
    # Low-pass: approximate bark without lettering
    from numpy.lib.stride_tricks import sliding_window_view

    k = 31
    pad = k // 2
    padded = np.pad(y_grid, pad, mode="edge")
    windows = sliding_window_view(padded, (k, k))
    smooth = windows.mean(axis=(2, 3))
    smooth[y_grid < -1e8] = 0

    # Old letter relief = positive residual
    residual = np.maximum(y_grid - smooth, 0)
    letter_mask = residual > 0.0012

    # Flatten vertices sitting on old embossed letters
    ui_v = ui
    vi_v = vi
    for i in range(len(pos)):
        r = residual[vi_v[i], ui_v[i]]
        if r > 0.001:
            pos[i, 1] -= r * 0.95

    # Recompute local base after flatten
    y_flat_grid = np.full((size, size), -1e9, dtype=np.float32)
    for i in range(len(pos)):
        u, v = ui[i], vi[i]
        if pos[i, 1] > y_flat_grid[v, u]:
            y_flat_grid[v, u] = pos[i, 1]
    padded2 = np.pad(y_flat_grid, pad, mode="edge")
    base2 = sliding_window_view(padded2, (k, k)).mean(axis=(2, 3))

    # Stamp new text
    for i in range(len(pos)):
        h = text_mask[vi[i], ui[i]]
        if h < 0.05:
            continue
        base_y = base2[vi[i], ui[i]]
        if base_y < -1e8:
            base_y = pos[i, 1]
        pos[i, 1] = base_y + emboss * h

    buf.attr("position").data = pos.astype(np.float32)
    bark_path.write_bytes(serialize(buf))


def _update_bark_texture(tex_path: Path, text_mask: np.ndarray) -> None:
    img = Image.open(tex_path).convert("RGB")
    arr = np.array(img, dtype=np.float32)
    # Soften old text area then darken new letters slightly
    letter = text_mask > 0.1
    blur = Image.fromarray((text_mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))
    blur_arr = np.array(blur, dtype=np.float32) / 255.0
    for c in range(3):
        channel = arr[..., c]
        # inpaint old letters by local blur blend
        channel = channel * (1 - blur_arr * 0.35) + channel.mean() * blur_arr * 0.35
        # carve tone
        channel = channel * (1 - letter * 0.18)
        arr[..., c] = channel
    # highlight ridges
    arr = np.clip(arr + letter[..., None] * 22, 0, 255)
    Image.fromarray(arr.astype(np.uint8)).save(tex_path, quality=92)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="?", default="hardik verma")
    parser.add_argument("--res", type=int, default=512)
    args = parser.parse_args()

    bark_path = ROOT / "public/models/BARK.buf"
    tex_path = ROOT / "public/textures/sustainability/bark.webp"

    mask = _render_text_mask(args.res, args.text)
    # Upscale mask to texture res
    tex_size = Image.open(tex_path).size[0]
    mask_img = Image.fromarray((mask * 255).astype(np.uint8)).resize((tex_size, tex_size), Image.Resampling.LANCZOS)
    mask_hi = np.array(mask_img, dtype=np.float32) / 255.0

    bak = bark_path.with_suffix(".buf.orig-sustainability")
    if not bak.exists():
        bak.write_bytes(bark_path.read_bytes())
    tex_bak = tex_path.with_suffix(".webp.orig-sustainability")
    if not tex_bak.exists():
        tex_bak.write_bytes(tex_path.read_bytes())

    _update_bark_mesh(bark_path, mask, emboss=0.008)
    _update_bark_texture(tex_path, mask_hi)
    print(f"Updated {bark_path} and {tex_path} with text: {args.text!r}")


if __name__ == "__main__":
    main()
