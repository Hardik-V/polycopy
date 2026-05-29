#!/usr/bin/env python3
"""
Bake STACK.webp (product-selector imposter) for the gold coin.

The product-selector ramp in coasterStackFrag does:

    imgBasedPos4 = u_imgBasedMVP * vec4(v_modelPosition, 1.0);
    imgBased    = texture2D(u_imgBasedTexture, imgBasedPos4.xy / imgBasedPos4.w);
    gl_FragColor.rgb = mix(gl_FragColor.rgb, imgBased, u_imgBasedOpacity);

So each surface point of the coin must map to a UV inside STACK.webp at the
projected coin silhouette. We:

  1. Project all coin vertices through the engine's MVP into UV space.
  2. Take the convex hull of those UVs as the on-screen silhouette.
  3. Fill the silhouette with a smooth radial gold gradient.
  4. Stamp an "H" emblem centered on the silhouette.
  5. Save as STACK.webp (RGB WebP, same dimensions as the original).

This avoids any per-triangle shading artifacts and yields a clean imposter.
"""

from __future__ import annotations

import json
import math
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REPO = Path(__file__).resolve().parent.parent
MESH_PATH = REPO / "public/models/coaster.buf"
OUT_PATH = REPO / "public/textures/coaster/STACK.webp"
BACKUP_PATH = REPO / "public/textures/coaster/STACK.original.webp"
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

MVP_ROWS = [
    [5.24828, -0.203069, -0.456906, 0.247969],
    [0, 8.61441, -4.37579, 0.172101],
    [0, 0.020409, 0.0459202, -0.0299466],
    [0, -0.406138, -0.913812, 0.495937],
]
MVP = np.array(MVP_ROWS, dtype=np.float64)

OUT_SIZE = 512

GOLD_CORE = (244, 200, 120)
GOLD_MID = (212, 156, 64)
GOLD_EDGE = (148, 92, 24)
BG_COLOR = (8, 5, 2)
H_COLOR = (108, 60, 12)


def load_positions(path: Path) -> np.ndarray:
    raw = path.read_bytes()
    header_len = struct.unpack("<I", raw[:4])[0]
    meta = json.loads(raw[4 : 4 + header_len])
    body = raw[4 + header_len :]

    offset = 0
    n = meta["vertexCount"]
    for attr in meta["attributes"]:
        size = attr["componentSize"]
        st = attr["storageType"]
        if st == "Float32Array":
            elem = 4
            dtype = np.float32
        elif st == "Int16Array":
            elem = 2
            dtype = np.int16
        elif st == "Uint16Array":
            elem = 2
            dtype = np.uint16
        else:
            raise RuntimeError(st)
        nbytes = n * size * elem
        a = offset % elem
        if a:
            offset += elem - a
        if attr["id"] == "position":
            arr = np.frombuffer(body, dtype=dtype, count=n * size, offset=offset).reshape(n, size).astype(np.float64)
            if attr.get("needsPack"):
                pc = attr["packedComponents"]
                max_int = float(np.iinfo(dtype).max)
                min_int = float(np.iinfo(dtype).min) if dtype == np.int16 else 0.0
                scale = max_int - min_int
                arr = (arr - min_int) / scale
                for c in range(size):
                    arr[:, c] = arr[:, c] * pc[c]["delta"] + pc[c]["from"]
            return arr
        offset += nbytes
    raise RuntimeError("position attr not found")


def project_to_pixels(positions: np.ndarray) -> np.ndarray:
    homo = np.concatenate([positions, np.ones((positions.shape[0], 1))], axis=1)
    clip = homo @ MVP.T
    w = clip[:, 3]
    u = clip[:, 0] / w
    v = clip[:, 1] / w
    px = u * OUT_SIZE
    py = (1.0 - v) * OUT_SIZE
    return np.stack([px, py], axis=1)


def convex_hull(points: np.ndarray) -> np.ndarray:
    pts = sorted({(float(p[0]), float(p[1])) for p in points})
    if len(pts) < 3:
        return np.array(pts)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return np.array(lower[:-1] + upper[:-1])


def load_font(size_px: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size_px)
    return ImageFont.load_default()


def main() -> None:
    positions = load_positions(MESH_PATH)
    pix = project_to_pixels(positions)

    hull = convex_hull(pix)
    hull_int = [(int(round(x)), int(round(y))) for x, y in hull]

    mask = Image.new("L", (OUT_SIZE, OUT_SIZE), 0)
    ImageDraw.Draw(mask).polygon(hull_int, fill=255)

    soft_mask = mask.filter(ImageFilter.GaussianBlur(radius=1.0))
    mask_np = np.array(soft_mask, dtype=np.float32) / 255.0

    cx = float(np.mean(hull[:, 0]))
    cy = float(np.mean(hull[:, 1]))
    rx = float(np.max(hull[:, 0]) - np.min(hull[:, 0])) * 0.5
    ry = float(np.max(hull[:, 1]) - np.min(hull[:, 1])) * 0.5
    rr = max(rx, ry)

    yy, xx = np.mgrid[0:OUT_SIZE, 0:OUT_SIZE].astype(np.float32)
    nx = (xx - cx) / max(rx, 1.0)
    ny = (yy - cy) / max(ry, 1.0)
    r = np.sqrt(nx * nx + ny * ny)
    r = np.clip(r, 0.0, 1.4)

    light_dx, light_dy = 0.35, -0.35
    light_dot = nx * light_dx + ny * light_dy
    light_term = np.clip(0.62 + 0.38 * light_dot, 0.0, 1.0)

    def lerp(a, b, t):
        return a + (b - a) * t

    t_outer = np.clip((r - 0.55) / 0.45, 0.0, 1.0)
    t_mid = np.clip(r / 0.55, 0.0, 1.0)

    mid = np.stack(
        [
            lerp(GOLD_CORE[0], GOLD_MID[0], t_mid),
            lerp(GOLD_CORE[1], GOLD_MID[1], t_mid),
            lerp(GOLD_CORE[2], GOLD_MID[2], t_mid),
        ],
        axis=-1,
    )
    edge = np.stack(
        [
            lerp(GOLD_MID[0], GOLD_EDGE[0], t_outer),
            lerp(GOLD_MID[1], GOLD_EDGE[1], t_outer),
            lerp(GOLD_MID[2], GOLD_EDGE[2], t_outer),
        ],
        axis=-1,
    )
    base = np.where(r[..., None] < 0.55, mid, edge)
    base = base * light_term[..., None]

    bg = np.array(BG_COLOR, dtype=np.float32).reshape(1, 1, 3)
    composite = base * mask_np[..., None] + bg * (1.0 - mask_np[..., None])
    composite = np.clip(composite, 0.0, 255.0).astype(np.uint8)

    img = Image.fromarray(composite, "RGB")

    h_size = int(rr * 1.1)
    font = load_font(h_size)
    h_layer = Image.new("RGBA", (OUT_SIZE, OUT_SIZE), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(h_layer)
    bbox = h_draw.textbbox((0, 0), "H", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = int(cx - tw / 2 - bbox[0])
    ty = int(cy - th / 2 - bbox[1])
    h_draw.text((tx, ty), "H", fill=H_COLOR + (160,), font=font)
    h_layer = h_layer.filter(ImageFilter.GaussianBlur(radius=1.2))
    img = Image.alpha_composite(img.convert("RGBA"), h_layer).convert("RGB")

    if OUT_PATH.exists() and not BACKUP_PATH.exists():
        BACKUP_PATH.write_bytes(OUT_PATH.read_bytes())

    img.save(OUT_PATH, "WEBP", quality=92, method=6)
    print(f"wrote {OUT_PATH}")
    print(f"  hull bounds px: ({hull[:,0].min():.1f},{hull[:,1].min():.1f}) - "
          f"({hull[:,0].max():.1f},{hull[:,1].max():.1f}) center ({cx:.1f},{cy:.1f})")


if __name__ == "__main__":
    main()
