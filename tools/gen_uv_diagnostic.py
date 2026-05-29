"""
gen_uv_diagnostic.py

Generates a 1024x1024 UV diagnostic image and writes it to
public/textures/coaster/DIFF.webp (after backing up the original).

The diagnostic is designed so that, when applied as the coaster's diffuse
texture, we can identify which texture region maps to which surface of the
3D disc (top face vs side strip vs bottom face) by simply looking at a
screenshot of the rendered scene.

Design:
  - 4x4 grid of brightly-coloured quadrants, each labelled Q01..Q16
    with a big letter and grid-coord text in each cell
  - White grid lines every 64 px (so we can also measure UV scale)
  - Concentric ring overlay centered on (512, 512) so we can spot
    radial / cylindrical UV layouts
  - Cardinal axis arrows (N/S/E/W) at the image edges
  - Large "TOP / SIDE / BOT" labels in distinct corners as anchor strings

Run from repo root:
    python3 tools/gen_uv_diagnostic.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SIZE = 1024
GRID = 4
CELL = SIZE // GRID
TEXTURE_PATH = Path("public/textures/coaster/DIFF.webp")
BACKUP_PATH = Path("public/textures/coaster/DIFF.original.webp")
OUT_PATH = Path("tools/_uv_diagnostic.png")


PALETTE = [
    (220,  30,  30), (220, 110,  30), (220, 190,  30), (160, 220,  30),
    ( 60, 200,  60), ( 30, 200, 150), ( 30, 180, 220), ( 30, 100, 220),
    ( 90,  30, 200), (170,  30, 200), (220,  30, 150), (220,  30,  90),
    (110, 110, 110), (170, 170, 170), ( 70,  70,  70), ( 40,  40,  40),
]


def load_font(px: int) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, px)
    return ImageFont.load_default()


def draw_text_centered(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill,
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((xy[0] - w / 2 - bbox[0], xy[1] - h / 2 - bbox[1]), text, font=font, fill=fill)


def build_diagnostic() -> Image.Image:
    img = Image.new("RGB", (SIZE, SIZE), (255, 255, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    big_font = load_font(96)
    mid_font = load_font(36)
    small_font = load_font(22)

    for row in range(GRID):
        for col in range(GRID):
            idx = row * GRID + col
            colour = PALETTE[idx]
            x0, y0 = col * CELL, row * CELL
            x1, y1 = x0 + CELL, y0 + CELL
            draw.rectangle((x0, y0, x1, y1), fill=colour)
            cx, cy = x0 + CELL // 2, y0 + CELL // 2
            draw_text_centered(
                draw, (cx, cy - 20), f"Q{idx + 1:02d}", big_font, (255, 255, 255)
            )
            draw_text_centered(
                draw,
                (cx, cy + 60),
                f"({col},{row})",
                mid_font,
                (255, 255, 255, 230),
            )

    for i in range(0, SIZE + 1, 64):
        light = 255 if i % CELL == 0 else 200
        width = 3 if i % CELL == 0 else 1
        draw.line([(i, 0), (i, SIZE)], fill=(light, light, light, 200), width=width)
        draw.line([(0, i), (SIZE, i)], fill=(light, light, light, 200), width=width)

    cx, cy = SIZE // 2, SIZE // 2
    for r in range(64, SIZE // 2 + 1, 64):
        draw.ellipse(
            (cx - r, cy - r, cx + r, cy + r),
            outline=(0, 0, 0, 180),
            width=2,
        )
    draw.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=(0, 0, 0))
    draw_text_centered(draw, (cx, cy + 36), "CENTER", small_font, (0, 0, 0))

    draw_text_centered(draw, (SIZE // 2,  24),         "NORTH (v=0)",   small_font, (0, 0, 0))
    draw_text_centered(draw, (SIZE // 2, SIZE - 24),   "SOUTH (v=1)",   small_font, (0, 0, 0))
    draw_text_centered(draw, (60,  SIZE // 2),         "W (u=0)",       small_font, (0, 0, 0))
    draw_text_centered(draw, (SIZE - 60, SIZE // 2),   "E (u=1)",       small_font, (0, 0, 0))

    for label, xy in [
        ("TOP?", (140, 140)),
        ("SIDE?", (SIZE - 160, 140)),
        ("BOT?", (140, SIZE - 140)),
        ("EDGE?", (SIZE - 160, SIZE - 140)),
    ]:
        draw_text_centered(draw, xy, label, mid_font, (255, 255, 255))

    return img


def main() -> None:
    if not TEXTURE_PATH.exists():
        raise SystemExit(f"Expected texture not found: {TEXTURE_PATH}")

    if not BACKUP_PATH.exists():
        shutil.copy2(TEXTURE_PATH, BACKUP_PATH)
        print(f"Backed up original -> {BACKUP_PATH}")
    else:
        print(f"Backup already exists at {BACKUP_PATH}; leaving it.")

    img = build_diagnostic()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT_PATH, "PNG")
    img.save(TEXTURE_PATH, "WEBP", quality=95, method=6)
    print(f"Wrote diagnostic -> {TEXTURE_PATH} (preview at {OUT_PATH})")


if __name__ == "__main__":
    main()
