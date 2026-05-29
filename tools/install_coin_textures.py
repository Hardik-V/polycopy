"""
install_coin_textures.py

Convert tools/out/coin_DIFF.png + coin_HEIGHT.png to WebP and copy them in
to public/textures/coaster/, backing up whatever's currently there.

The dev server picks up the change live (Astro doesn't process /public files
so a browser reload is enough).
"""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageEnhance


SRC_DIR = Path("tools/out")
DST_DIR = Path("public/textures/coaster")
BACKUP_SUFFIX = ".original.webp"

DIFF_SATURATION = 1.45
DIFF_CONTRAST = 1.20
DIFF_BRIGHTNESS = 0.92

TARGETS = [
    ("coin_DIFF.png",   "DIFF.webp",   95, True),
    ("coin_HEIGHT.png", "HEIGHT.webp", 92, False),
]


def composite_on(coin_png: Path, bg: tuple[int, int, int]) -> Image.Image:
    """Coin renders are RGBA with transparent surrounds. Flatten on a
    neutral colour so the engine's planar UV sampler reads a stable value
    outside the disc circle (no alpha haloing through the rim shader)."""
    img = Image.open(coin_png).convert("RGBA")
    bg_img = Image.new("RGB", img.size, bg)
    bg_img.paste(img, mask=img.split()[3])
    return bg_img


def colour_punch(img: Image.Image) -> Image.Image:
    """Boost saturation + contrast + slightly darken so the gold survives the
    engine's white-key lighting and still reads as gold metal on the disc."""
    img = ImageEnhance.Color(img).enhance(DIFF_SATURATION)
    img = ImageEnhance.Contrast(img).enhance(DIFF_CONTRAST)
    img = ImageEnhance.Brightness(img).enhance(DIFF_BRIGHTNESS)
    return img


def main() -> None:
    for src_name, dst_name, quality, punch in TARGETS:
        src = SRC_DIR / src_name
        dst = DST_DIR / dst_name
        backup = DST_DIR / (dst.stem + BACKUP_SUFFIX)

        if not src.exists():
            raise SystemExit(f"missing source render: {src}")

        if dst.exists() and not backup.exists():
            shutil.copy2(dst, backup)
            print(f"backup -> {backup}")

        bg = (10, 7, 4) if "DIFF" in dst_name else (128, 128, 128)
        flat = composite_on(src, bg)
        if punch:
            flat = colour_punch(flat)
        flat.save(dst, "WEBP", quality=quality, method=6)
        print(f"wrote {dst}  ({dst.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
