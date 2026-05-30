#!/usr/bin/env python3
"""
Bake STACK.webp (product-selector imposter) for the gold coin.

Instead of a painted gradient, we project the coin's top face through the
engine's MVP matrix (StackScene.coasterImgBaseMVP) and sample the existing
DIFF.webp texture for every output pixel.  Uncovered borders are filled via
edge-extension (dilation) so the whole 512×512 is valid gold — no black gaps.
"""

from __future__ import annotations
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

REPO       = Path(__file__).resolve().parent.parent
DIFF_PATH  = REPO / "public/textures/coaster/DIFF.webp"
OUT_PATH   = REPO / "public/textures/coaster/STACK.webp"
BACKUP_PATH = REPO / "public/textures/coaster/STACK.original.webp"

# Exact MVP from the engine (StackScene.coasterImgBaseMVP)
MVP = np.array([
    [5.24828, -0.203069, -0.456906,  0.247969],
    [0,        8.61441,  -4.37579,   0.172101],
    [0,        0.020409,  0.0459202, -0.0299466],
    [0,       -0.406138, -0.913812,  0.495937],
], dtype=np.float64)

OUT_SIZE     = 512
COIN_RADIUS  = 0.044
COIN_Y       = 0.003   # top face of the coin


def main() -> None:
    diff = Image.open(DIFF_PATH).convert("RGB")
    diff_w, diff_h = diff.size
    diff_arr = np.array(diff)

    # Dense grid covering the coin's top face disc
    N = 3072
    xs = np.linspace(-COIN_RADIUS, COIN_RADIUS, N)
    zs = np.linspace(-COIN_RADIUS, COIN_RADIUS, N)
    XX, ZZ = np.meshgrid(xs, zs)
    inside = (XX**2 + ZZ**2) <= COIN_RADIUS**2

    # Project model positions through MVP → texture pixel coords
    ones = np.ones_like(XX)
    YY   = np.full_like(XX, COIN_Y)
    flat = np.stack([XX, YY, ZZ, ones], axis=-1).reshape(-1, 4)
    clip = (MVP @ flat.T).T
    w  = clip[:, 3]
    px = clip[:, 0] / w * OUT_SIZE
    py = (1.0 - clip[:, 1] / w) * OUT_SIZE

    inside_flat = inside.ravel()
    px_int = np.round(px).astype(int)
    py_int = np.round(py).astype(int)

    valid = (inside_flat &
             (px_int >= 0) & (px_int < OUT_SIZE) &
             (py_int >= 0) & (py_int < OUT_SIZE))

    # Map model XZ → DIFF UV
    u_diff_px = np.clip(
        ((XX.ravel()[valid] + COIN_RADIUS) / (2 * COIN_RADIUS) * diff_w).astype(int),
        0, diff_w - 1)
    v_diff_px = np.clip(
        ((ZZ.ravel()[valid] + COIN_RADIUS) / (2 * COIN_RADIUS) * diff_h).astype(int),
        0, diff_h - 1)

    colors = diff_arr[v_diff_px, u_diff_px]

    # Accumulate (average overlapping samples)
    out_rgb   = np.zeros((OUT_SIZE, OUT_SIZE, 3), dtype=np.float64)
    out_count = np.zeros((OUT_SIZE, OUT_SIZE),    dtype=np.float64)
    np.add.at(out_rgb,   (py_int[valid], px_int[valid]), colors.astype(np.float64))
    np.add.at(out_count, (py_int[valid], px_int[valid]), 1.0)

    mask_covered = out_count > 0
    result = np.zeros((OUT_SIZE, OUT_SIZE, 3), dtype=np.uint8)
    result[mask_covered] = (
        out_rgb[mask_covered] / out_count[mask_covered, None]
    ).clip(0, 255).astype(np.uint8)

    # Edge-extension dilation to fill uncovered borders
    img_tmp      = Image.fromarray(result)
    coverage_mask = Image.fromarray((mask_covered * 255).astype(np.uint8), "L")

    for i in range(24):
        size = 7 if i < 8 else 5
        img_dilated  = img_tmp.filter(ImageFilter.MaxFilter(size))
        mask_dilated = coverage_mask.filter(ImageFilter.MaxFilter(size))
        img_arr      = np.array(img_tmp)
        mask_arr     = np.array(coverage_mask)
        newly = (np.array(mask_dilated) > 0) & (mask_arr == 0)
        img_arr[newly] = np.array(img_dilated)[newly]
        mask_arr[newly] = 255
        img_tmp       = Image.fromarray(img_arr)
        coverage_mask = Image.fromarray(mask_arr, "L")

    result = np.array(img_tmp)

    # Any pixels still uncovered: fill with average center gold
    still_uncovered = np.array(coverage_mask) == 0
    if still_uncovered.any():
        cx_d, cy_d = diff_w // 2, diff_h // 2
        fill_color = diff_arr[cy_d-32:cy_d+32, cx_d-32:cx_d+32].mean(axis=(0,1)).astype(np.uint8)
        result[still_uncovered] = fill_color

    # Light gaussian blur on the gap-filled top strip to smooth dilation seam
    proj_top = py_int[valid].min() if valid.any() else 0
    img_out = Image.fromarray(result, "RGB")
    if proj_top > 2:
        strip = img_out.crop((0, 0, OUT_SIZE, proj_top + 20))
        img_out.paste(strip.filter(ImageFilter.GaussianBlur(radius=2)), (0, 0))

    if OUT_PATH.exists() and not BACKUP_PATH.exists():
        BACKUP_PATH.write_bytes(OUT_PATH.read_bytes())

    img_out.save(OUT_PATH, "WEBP", quality=95, method=6)
    print(f"Written: {OUT_PATH}")


if __name__ == "__main__":
    main()