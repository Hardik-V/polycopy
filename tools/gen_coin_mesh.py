"""
gen_coin_mesh.py

Generates a flat coin/medallion mesh and writes it as a .buf file that
drops in as public/models/coaster.buf.

Spec:
  - Diameter   88.6 mm (X, Z extent matches the original coaster mesh so
                        the engine's camera framing, animation positions,
                        and bounding logic do not move)
  - Thickness  5.0  mm (down from the coaster's 17.5 mm)
  - Sitting orientation matches the original: bottom near Y=0,
                        top of coin at Y = +0.005
  - 256 angular subdivisions for a smooth silhouette
  - Sharp edges between top/bottom/side via duplicated edge vertices
  - Planar UV from above: u = (x/R + 1) / 2, v = (z/R + 1) / 2
  - Vertex normals: +Y for top face, -Y for bottom face, radial for side
  - Cd (vertex colour / AO) = 1.0 everywhere (no baked AO darkening)

Vertex count: 4*N + 2 = 1026   for N=256
Triangle count: 4*N = 1024     -> 3072 indices

Usage:
    python3 tools/gen_coin_mesh.py [--n SEGMENTS] [--out PATH]
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import numpy as np

from buf_codec import Attribute, BufFile, auto_pack_params, serialize


RADIUS = 0.04493
THICKNESS = 0.005

SDF_BODY_TOP_Y = 0.0172
ESCAPE_MARGIN = 0.0008

Y_BOTTOM = SDF_BODY_TOP_Y + ESCAPE_MARGIN
Y_TOP = Y_BOTTOM + THICKNESS

UV_SCALE = 1.0 / 3.0

DEFAULT_OUT = Path("public/models/coaster.buf")
BACKUP = DEFAULT_OUT.with_suffix(".original.buf")


def build_mesh(segments: int = 256):
    n = segments
    theta = np.linspace(0.0, 2 * np.pi, n, endpoint=False)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)

    rim_x = RADIUS * cos_t
    rim_z = RADIUS * sin_t

    positions: list[tuple[float, float, float]] = []
    normals:   list[tuple[float, float, float]] = []
    uvs:       list[tuple[float, float]] = []

    def uv_planar(x: float, z: float) -> tuple[float, float]:
        u = (x / RADIUS + 1.0) * 0.5
        v = (z / RADIUS + 1.0) * 0.5
        cx, cz = 0.5, 0.5
        return (cx + (u - cx) * UV_SCALE, cz + (v - cz) * UV_SCALE)

    top_center_idx = len(positions)
    positions.append((0.0, Y_TOP, 0.0))
    normals.append((0.0, 1.0, 0.0))
    uvs.append(uv_planar(0.0, 0.0))

    top_rim_start = len(positions)
    for i in range(n):
        positions.append((float(rim_x[i]), Y_TOP, float(rim_z[i])))
        normals.append((0.0, 1.0, 0.0))
        uvs.append(uv_planar(float(rim_x[i]), float(rim_z[i])))

    side_top_start = len(positions)
    for i in range(n):
        nx, nz = float(cos_t[i]), float(sin_t[i])
        positions.append((float(rim_x[i]), Y_TOP, float(rim_z[i])))
        normals.append((nx, 0.0, nz))
        uvs.append(uv_planar(float(rim_x[i]), float(rim_z[i])))

    side_bot_start = len(positions)
    for i in range(n):
        nx, nz = float(cos_t[i]), float(sin_t[i])
        positions.append((float(rim_x[i]), Y_BOTTOM, float(rim_z[i])))
        normals.append((nx, 0.0, nz))
        uvs.append(uv_planar(float(rim_x[i]), float(rim_z[i])))

    bot_rim_start = len(positions)
    for i in range(n):
        positions.append((float(rim_x[i]), Y_BOTTOM, float(rim_z[i])))
        normals.append((0.0, -1.0, 0.0))
        uvs.append(uv_planar(float(rim_x[i]), float(rim_z[i])))

    bot_center_idx = len(positions)
    positions.append((0.0, Y_BOTTOM, 0.0))
    normals.append((0.0, -1.0, 0.0))
    uvs.append(uv_planar(0.0, 0.0))

    indices: list[int] = []

    for i in range(n):
        a = top_rim_start + i
        b = top_rim_start + (i + 1) % n
        indices.extend([top_center_idx, a, b])

    for i in range(n):
        t0 = side_top_start + i
        t1 = side_top_start + (i + 1) % n
        b0 = side_bot_start + i
        b1 = side_bot_start + (i + 1) % n
        indices.extend([t0, b0, b1])
        indices.extend([t0, b1, t1])

    for i in range(n):
        a = bot_rim_start + i
        b = bot_rim_start + (i + 1) % n
        indices.extend([bot_center_idx, b, a])

    positions_arr = np.asarray(positions, dtype=np.float32)
    normals_arr   = np.asarray(normals,   dtype=np.float32)
    uvs_arr       = np.asarray(uvs,       dtype=np.float32)
    indices_arr   = np.asarray(indices,   dtype=np.uint32)
    cd_arr        = np.ones(len(positions), dtype=np.float32)

    return positions_arr, normals_arr, uvs_arr, indices_arr, cd_arr


def build_buf(segments: int) -> BufFile:
    positions, normals, uvs, indices, cd = build_mesh(segments)

    vertex_count = positions.shape[0]
    index_count = indices.shape[0]

    p_from, p_delta = auto_pack_params(positions.reshape(-1), 3)
    n_from, n_delta = auto_pack_params(normals.reshape(-1), 3)
    u_from, u_delta = auto_pack_params(uvs.reshape(-1), 2)
    c_from, c_delta = auto_pack_params(cd, 1)

    n_delta = [max(d, 1e-6) for d in n_delta]
    u_delta = [max(d, 1e-6) for d in u_delta]
    p_delta = [max(d, 1e-6) for d in p_delta]
    c_delta = [max(d, 1e-6) for d in c_delta]

    buf = BufFile(
        vertex_count=vertex_count,
        index_count=index_count,
        mesh_type="Mesh",
    )
    buf.attributes = [
        Attribute(
            id="Cd",
            component_size=1,
            storage_type="Int16Array",
            needs_pack=True,
            packed_from=c_from,
            packed_delta=c_delta,
            data=cd,
        ),
        Attribute(
            id="indices",
            component_size=1,
            storage_type="Uint16Array" if vertex_count <= 65535 else "Uint32Array",
            needs_pack=False,
            data=indices,
        ),
        Attribute(
            id="normal",
            component_size=3,
            storage_type="Uint16Array",
            needs_pack=True,
            packed_from=n_from,
            packed_delta=n_delta,
            data=normals,
        ),
        Attribute(
            id="position",
            component_size=3,
            storage_type="Uint16Array",
            needs_pack=True,
            packed_from=p_from,
            packed_delta=p_delta,
            data=positions,
        ),
        Attribute(
            id="uv",
            component_size=2,
            storage_type="Int16Array",
            needs_pack=True,
            packed_from=u_from,
            packed_delta=u_delta,
            data=uvs,
        ),
    ]
    return buf


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=256, help="angular segments")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--no-backup", action="store_true")
    args = p.parse_args()

    if not args.no_backup and args.out.exists() and not BACKUP.exists():
        shutil.copy2(args.out, BACKUP)
        print(f"backup -> {BACKUP}")

    buf = build_buf(args.n)
    data = serialize(buf)
    args.out.write_bytes(data)

    print(f"wrote {args.out}")
    print(f"  vertex_count = {buf.vertex_count}")
    print(f"  index_count  = {buf.index_count}")
    print(f"  triangles    = {buf.index_count // 3}")
    print(f"  bytes        = {len(data)}")


if __name__ == "__main__":
    main()
