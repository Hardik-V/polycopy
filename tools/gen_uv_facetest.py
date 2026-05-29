"""
gen_uv_facetest.py

Second diagnostic. This one is designed to answer ONE question:
do the top and bottom faces of the disc sample different regions
of the texture, or the same region?

Strategy: split the texture into 4 distinct zones with VERY different
colours + giant labels. We will then look at the rendered scene from
angles where bottom of the disc is visible (encryption flip, AI section
during mid-flip) and see which zone shows up.

Zones:
  - TOP-HALF  (upper half of texture, v in [0, 0.5])  → bright RED with "TOP" letters
  - BOT-HALF  (lower half of texture, v in [0.5, 1])  → bright BLUE with "BOT" letters
  - LEFT-RING  (outer left strip)                     → bright GREEN with "L"
  - RIGHT-RING (outer right strip)                    → bright YELLOW with "R"
  - CENTER spot (small disc at 512,512)               → bright MAGENTA "C"

Reading the result:
  - If the disc top face shows RED everywhere → top face uses upper half of texture
  - If the disc top face shows MIXED red+blue → top face uses both halves
  - If the disc bottom face shows BLUE → bottom uses lower half (separate region!)
  - If the disc bottom face also shows RED+BLUE mix → bottom is mirrored top
"""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SIZE = 1024
TEXTURE_PATH = Path("public/textures/coaster/DIFF.webp")
BACKUP_PATH = Path("public/textures/coaster/DIFF.original.webp")
OUT_PATH = Path("tools/_uv_facetest.png")


def load_font(px: int) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, px)
    return ImageFont.load_default()


def main() -> None:
    if not BACKUP_PATH.exists():
        shutil.copy2(TEXTURE_PATH, BACKUP_PATH)

    img = Image.new("RGB", (SIZE, SIZE), (255, 255, 255))
    d = ImageDraw.Draw(img, "RGBA")

    d.rectangle((0, 0, SIZE, SIZE // 2), fill=(220, 30, 30))
    d.rectangle((0, SIZE // 2, SIZE, SIZE), fill=(30, 80, 220))

    f_huge = load_font(220)
    for x in (200, 720):
        d.text((x - 90, 60), "T", font=f_huge, fill=(255, 255, 255))
        d.text((x - 90, 220), "O", font=f_huge, fill=(255, 255, 255))
        d.text((x - 90, 380), "P", font=f_huge, fill=(255, 255, 255))
    for x in (200, 720):
        d.text((x - 90, SIZE // 2 + 60), "B", font=f_huge, fill=(255, 255, 255))
        d.text((x - 90, SIZE // 2 + 220), "O", font=f_huge, fill=(255, 255, 255))
        d.text((x - 90, SIZE // 2 + 380), "T", font=f_huge, fill=(255, 255, 255))

    f_arrow = load_font(140)
    d.text((SIZE // 2 - 50, 30), "↑", font=f_arrow, fill=(255, 255, 0))
    d.text((SIZE // 2 - 50, SIZE - 180), "↓", font=f_arrow, fill=(255, 255, 0))

    d.rectangle((0, 0, 80, SIZE), fill=(30, 200, 30))
    d.rectangle((SIZE - 80, 0, SIZE, SIZE), fill=(230, 220, 30))
    f_side = load_font(64)
    for y in range(80, SIZE, 200):
        d.text((10, y), "L", font=f_side, fill=(255, 255, 255))
        d.text((SIZE - 70, y), "R", font=f_side, fill=(0, 0, 0))

    cx, cy = SIZE // 2, SIZE // 2
    d.ellipse((cx - 80, cy - 80, cx + 80, cy + 80), fill=(220, 30, 220))
    f_c = load_font(120)
    d.text((cx - 40, cy - 70), "C", font=f_c, fill=(255, 255, 255))

    img.save(OUT_PATH, "PNG")
    img.save(TEXTURE_PATH, "WEBP", quality=95, method=6)
    print(f"wrote {TEXTURE_PATH}")


if __name__ == "__main__":
    main()
