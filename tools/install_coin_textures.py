"""
install_coin_textures.py

Writes the two coin textures the engine consumes:

    public/textures/coaster/DIFF.webp    (albedo)
    public/textures/coaster/HEIGHT.webp  (bump source)

DIFF is generated directly in Python as a UNIFORM gold square. The
engine's coasterFrag shader does:

    albedo = pow(map.rgb, vec3(2.0));

so the stored sRGB value is pre-squared-rooted from the desired linear
gold tone. The H + rings are NOT in DIFF - putting them there would
darken via the pow(., 2.0) curve and create the "bowl-base" shadow that
keeps showing up in tilted / flipped views.

HEIGHT is the Blender bake (tools/out/coin_HEIGHT.png). The engine
shader uses HEIGHT's R channel as the alpha of the combined RGBA
texture and reads it via dFdx/dFdy as a bump-map gradient -
perturbNormalArb then carves the H + ring relief into the runtime
lighting from any camera angle.

DIFF therefore stays flat; all relief comes from HEIGHT through the
engine's dynamic lights.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image


SRC_DIR = Path("tools/out")
DST_DIR = Path("public/textures/coaster")
BACKUP_SUFFIX = ".original.webp"

DIFF_SIZE = 1024
DIFF_RGB = (235, 184, 102)


def _backup_if_needed(dst: Path) -> None:
    backup = DST_DIR / (dst.stem + BACKUP_SUFFIX)
    if dst.exists() and not backup.exists():
        shutil.copy2(dst, backup)
        print(f"backup -> {backup}")


def write_diff() -> None:
    dst = DST_DIR / "DIFF.webp"
    _backup_if_needed(dst)
    img = Image.new("RGB", (DIFF_SIZE, DIFF_SIZE), DIFF_RGB)
    img.save(dst, "WEBP", quality=92, method=6)
    print(f"wrote {dst}  ({dst.stat().st_size // 1024} KB)  (flat {DIFF_RGB})")


def composite_on(coin_png: Path, bg: tuple[int, int, int]) -> Image.Image:
    img = Image.open(coin_png).convert("RGBA")
    bg_img = Image.new("RGB", img.size, bg)
    bg_img.paste(img, mask=img.split()[3])
    return bg_img


def write_height() -> None:
    src = SRC_DIR / "coin_HEIGHT.png"
    if not src.exists():
        raise SystemExit(f"missing source render: {src}")
    dst = DST_DIR / "HEIGHT.webp"
    _backup_if_needed(dst)
    flat = composite_on(src, (96, 96, 96))
    flat.save(dst, "WEBP", quality=92, method=6)
    print(f"wrote {dst}  ({dst.stat().st_size // 1024} KB)")


def main() -> None:
    write_diff()
    write_height()


if __name__ == "__main__":
    main()
