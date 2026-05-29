#!/usr/bin/env python3
"""
Compensate for the local-Y lift in coaster.buf by subtracting the same
amount from the `from[1]` (world-Y origin) of every keyframed `position`
attribute in the coaster animation buffers.

Since the engine reconstructs world Y as `raw/scale * delta + from`,
subtracting Y_SHIFT from `from` shifts every reconstructed Y by the
same amount without changing any of the packed integer body bytes.

Run from repo root.
"""

import json
import struct
import shutil
from pathlib import Path

Y_SHIFT = 0.018

ANIM_FILES = [
    "public/models/coaster_hero_animation.buf",
    "public/models/COASTER_FLIP_ANIM.buf",
    "public/models/featuresAnimations/COASTER_ANIM.buf",
]


def shift_file(path: Path) -> None:
    raw = path.read_bytes()
    header_len = struct.unpack("<I", raw[:4])[0]
    header_json = raw[4 : 4 + header_len].decode("utf-8")
    body = raw[4 + header_len :]

    meta = json.loads(header_json)

    backup = path.with_suffix(path.suffix + ".preshift")
    if not backup.exists():
        shutil.copy2(path, backup)

    changed = False
    for attr in meta.get("attributes", []):
        if attr.get("id") != "position":
            continue
        pc = attr.get("packedComponents")
        if not pc or len(pc) < 2:
            continue
        old = pc[1]["from"]
        pc[1]["from"] = old - Y_SHIFT
        changed = True
        print(f"  {path}: position.from[1] {old:+.6f} -> {pc[1]['from']:+.6f}")

    if not changed:
        print(f"  {path}: no position attr changed")
        return

    new_header_bytes = json.dumps(meta, separators=(", ", ": ")).encode("utf-8")
    body_offset = 4 + len(new_header_bytes)
    pad = (-body_offset) % 4
    if pad:
        new_header_bytes = new_header_bytes + b" " * pad

    out = (
        struct.pack("<I", len(new_header_bytes))
        + new_header_bytes
        + body
    )
    path.write_bytes(out)


def main() -> None:
    for f in ANIM_FILES:
        shift_file(Path(f))


if __name__ == "__main__":
    main()
