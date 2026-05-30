from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import numpy as np

from buf_codec import Attribute, BufFile, auto_pack_params, serialize


RADIUS = 0.04493
THICKNESS = 0.005

Y_BOTTOM = 0.0
Y_TOP = THICKNESS

UV_SCALE = 1.0 / 3.0

DEFAULT_OUT = Path("public/models/coaster.buf")
BACKUP = DEFAULT_OUT.with_suffix(".original.buf")


def build_mesh(segments: int = 256):
    n = segments
    theta = np.linspace(0.0, 2 * np.pi, n, endpoint=False)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)

    positions: list[tuple[float, float, float]] = []
    normals:   list[tuple[float, float, float]] = []
    uvs:       list[tuple[float, float]] = []

    def uv_planar(x: float, z: float) -> tuple[float, float]:
        u = (x / RADIUS + 1.0) * 0.5
        v = (z / RADIUS + 1.0) * 0.5
        cx, cz = 0.5, 0.5
        return (cx + (u - cx) * UV_SCALE, cz + (v - cz) * UV_SCALE)

    # --- THE FULLY CONVEX MATH ---
    # Bevel controls the pillowy rounded edge
    bevel = 0.002 
    r_flat = RADIUS - bevel
    
    # Crown controls how much the center bulges outward (1.5mm)
    crown = 0.0015 
    
    # Resolution steps for perfectly smooth light gradients
    face_steps = 12
    bevel_steps = 8 
    
    profile_rings = []
    
    # 1. Top Face (The Gradual Center Bulge)
    # Uses a Smoothstep function to flawlessly blend the dome into the bevel
    for i in range(1, face_steps + 1):
        x = i / face_steps
        r = r_flat * x
        y = Y_TOP + crown * (1.0 - (3 * x**2 - 2 * x**3))
        
        # Calculate exact mathematical tangent for flawless lighting
        dy_dr = -6.0 * crown * (x - x**2) / r_flat
        L = np.sqrt(dy_dr**2 + 1.0)
        nr = -dy_dr / L
        ny = 1.0 / L
        profile_rings.append((r, y, nr, ny))
        
    # 2. Top Edge (The Bevel)
    for i in range(1, bevel_steps + 1):
        rad = np.radians((i / bevel_steps) * 90)
        r = r_flat + bevel * np.sin(rad)
        y = Y_TOP - bevel + bevel * np.cos(rad)
        profile_rings.append((r, y, np.sin(rad), np.cos(rad)))
        
    # 3. The Vertical Side Wall
    profile_rings.append((RADIUS, Y_TOP - bevel, 1.0, 0.0))
    profile_rings.append((RADIUS, Y_BOTTOM + bevel, 1.0, 0.0))

    # 4. Bottom Edge (The Bevel)
    for i in range(0, bevel_steps):
        rad = np.radians(90 - (i / bevel_steps) * 90)
        r = r_flat + bevel * np.sin(rad)
        y = Y_BOTTOM + bevel - bevel * np.cos(rad)
        profile_rings.append((r, y, np.sin(rad), -np.cos(rad)))
        
    # 5. Bottom Face (The Gradual Center Bulge)
    for i in range(face_steps - 1, 0, -1):
        x = i / face_steps
        r = r_flat * x
        y = Y_BOTTOM - crown * (1.0 - (3 * x**2 - 2 * x**3))
        
        dy_dr = 6.0 * crown * (x - x**2) / r_flat
        L = np.sqrt(dy_dr**2 + 1.0)
        profile_rings.append((r, y, dy_dr / L, -1.0 / L))

    # --- BUILD THE 3D VERTS ---
    # Top Center Vertex (Pushed outward by the crown height)
    top_center_idx = len(positions)
    positions.append((0.0, Y_TOP + crown, 0.0))
    normals.append((0.0, 1.0, 0.0))
    uvs.append(uv_planar(0.0, 0.0))

    # Sweep all the curved profile rings 360 degrees
    rings = []
    for pr, py, pnr, pny in profile_rings:
        start_idx = len(positions)
        rings.append(start_idx)
        for i in range(n):
            px = pr * float(cos_t[i])
            pz = pr * float(sin_t[i])
            nx = pnr * float(cos_t[i])
            nz = pnr * float(sin_t[i])
            positions.append((px, py, pz))
            normals.append((nx, pny, nz))
            uvs.append(uv_planar(px, pz))

    # Bottom Center Vertex (Pushed outward by the crown height)
    bot_center_idx = len(positions)
    positions.append((0.0, Y_BOTTOM - crown, 0.0))
    normals.append((0.0, -1.0, 0.0))
    uvs.append(uv_planar(0.0, 0.0))

    indices: list[int] = []

    # Stitch the mesh together
    top_rim = rings[0]
    for i in range(n):
        a = top_rim + i
        b = top_rim + (i + 1) % n
        indices.extend([top_center_idx, a, b])

    for r_idx in range(len(rings) - 1):
        r1 = rings[r_idx]
        r2 = rings[r_idx + 1]
        for i in range(n):
            t0 = r1 + i
            t1 = r1 + (i + 1) % n
            b0 = r2 + i
            b1 = r2 + (i + 1) % n
            indices.extend([t0, b0, b1])
            indices.extend([t0, b1, t1])

    bot_rim = rings[-1]
    for i in range(n):
        a = bot_rim + i
        b = bot_rim + (i + 1) % n
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
        Attribute(id="Cd", component_size=1, storage_type="Int16Array", needs_pack=True, packed_from=c_from, packed_delta=c_delta, data=cd),
        Attribute(id="indices", component_size=1, storage_type="Uint16Array" if vertex_count <= 65535 else "Uint32Array", needs_pack=False, data=indices),
        Attribute(id="normal", component_size=3, storage_type="Uint16Array", needs_pack=True, packed_from=n_from, packed_delta=n_delta, data=normals),
        Attribute(id="position", component_size=3, storage_type="Uint16Array", needs_pack=True, packed_from=p_from, packed_delta=p_delta, data=positions),
        Attribute(id="uv", component_size=2, storage_type="Int16Array", needs_pack=True, packed_from=u_from, packed_delta=u_delta, data=uvs),
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

    buf = build_buf(args.n)
    data = serialize(buf)
    args.out.write_bytes(data)
    
    # Export for viewing
    pos_attr = buf.attr("position")
    idx_attr = buf.attr("indices")
    if pos_attr and idx_attr:
        obj_out = args.out.with_suffix('.obj')
        vertices = pos_attr.data.reshape(-1, 3)
        indices = idx_attr.data.reshape(-1, 3)
        with open(obj_out, 'w') as f:
            f.write("# Generated Fully Convex Coin Mesh\n")
            for v in vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in indices:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()