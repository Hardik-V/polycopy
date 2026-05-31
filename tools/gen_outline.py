#!/usr/bin/env python3
"""
gen_outline.py  —  Ribbonised outline (progressive arc-length Z sweep)
════════════════════════════════════════════════════════════════════════
Reverse-engineered from sustainability_text_outline.buf:

  • Each letter boundary ring (outer + inner holes) becomes ONE ribbon strip.
  • As you trace the ring in XY, Z sweeps from 0 → 1 proportional to
    cumulative arc-length  →  Z[i] = arc_len[i] / total_len * DEPTH
  • At every sample point a perpendicular cross-section is created:
      L  =  centre − perp * HALF_WIDTH   (left edge)
      R  =  centre + perp * HALF_WIDTH   (right edge)
  • Adjacent [L,R] pairs are stitched into quads (2 triangles each).
  • No front cap, no back cap  —  pure ribbon walls.

Ring is left OPEN at the seam (Z jumps 1→0 there); in 3D this seam is
on the back/far face so it is hidden from the +Z camera.

Change TEXT at the top.  Output: <slug>_outline.obj
"""

import os, re
import trimesh
import numpy as np
from matplotlib.textpath import TextPath
from matplotlib.path import Path
from matplotlib.font_manager import FontProperties

# ── CONFIG ────────────────────────────────────────────────────────────────────
TEXT       = "HARDIK VERMA"   # ← change me
FONT_BOLD  = True
DEPTH      = 1.0
HALF_WIDTH = 0.015            # ribbon half-width in scaled space (0.3% of width)
OUT        = re.sub(r"[^a-zA-Z0-9]+", "_", TEXT.lower()).strip("_") + "_outline.obj"


def _ribbon_ring(pts_closed, depth, half_width):
    """
    Build ribbon geometry for one closed 2-D ring.

    pts_closed : (N+1, 2)  — Shapely coords, first == last point.
    Returns (verts, faces) as numpy arrays, or (None, None) if degenerate.
    """
    ring = pts_closed[:-1].astype(np.float64)   # N unique points
    N = len(ring)
    if N < 3:
        return None, None

    # ── arc-length parameterised Z ────────────────────────────────────────────
    diffs     = np.diff(ring, axis=0)                       # (N-1, 2)
    seg_lens  = np.linalg.norm(diffs, axis=1)               # (N-1,)
    # closing segment length (last point back to first)
    closing   = np.linalg.norm(ring[0] - ring[-1])
    all_segs  = np.append(seg_lens, closing)                # (N,)
    cum_len   = np.concatenate([[0.0], np.cumsum(all_segs[:-1])])  # (N,)
    total_len = cum_len[-1] + all_segs[-1]

    if total_len < 1e-12:
        return None, None

    z_vals = (cum_len / total_len * depth).astype(np.float64)

    # ── per-sample tangent → perpendicular ───────────────────────────────────
    verts  = np.empty((N * 2, 3), dtype=np.float64)
    for i in range(N):
        ni = (i + 1) % N
        tang = ring[ni] - ring[i]
        tn   = np.linalg.norm(tang)
        if tn < 1e-12:
            pi   = (i - 1) % N
            tang = ring[i] - ring[pi]
            tn   = np.linalg.norm(tang)
        if tn < 1e-12:
            tang = np.array([1.0, 0.0])
        else:
            tang /= tn

        # 90° CCW from tangent  →  outward-facing for CCW rings
        perp = np.array([-tang[1], tang[0]])

        x, y, z = ring[i, 0], ring[i, 1], z_vals[i]
        verts[i * 2    ] = [x - perp[0]*half_width,
                             y - perp[1]*half_width, z]   # L
        verts[i * 2 + 1] = [x + perp[0]*half_width,
                             y + perp[1]*half_width, z]   # R

    # ── stitch quads between consecutive samples ──────────────────────────────
    # Ring is left OPEN (no face wrapping step N-1 → 0).
    faces = np.empty(((N - 1) * 2, 3), dtype=np.int64)
    for i in range(N - 1):
        L0, R0 = i * 2,       i * 2 + 1
        L1, R1 = (i+1) * 2,  (i+1) * 2 + 1
        faces[i * 2    ] = [L0, L1, R0]   # tri 1
        faces[i * 2 + 1] = [R0, L1, R1]  # tri 2

    return verts, faces


# ── 1. Font → SVG ─────────────────────────────────────────────────────────────
print(f"[1/5] Font path for {TEXT!r} …")
fp = FontProperties(weight="bold" if FONT_BOLD else "regular", family="sans-serif")
tp = TextPath((0, 0), TEXT, size=1, prop=fp)
cmds = []
for v, code in tp.iter_segments():
    if   code == Path.MOVETO:    cmds.append(f"M {v[0]:.6f} {v[1]:.6f}")
    elif code == Path.LINETO:    cmds.append(f"L {v[0]:.6f} {v[1]:.6f}")
    elif code == Path.CURVE3:    cmds.append(f"Q {v[0]:.6f} {v[1]:.6f} {v[2]:.6f} {v[3]:.6f}")
    elif code == Path.CURVE4:    cmds.append(f"C {v[0]:.6f} {v[1]:.6f} {v[2]:.6f} {v[3]:.6f} {v[4]:.6f} {v[5]:.6f}")
    elif code == Path.CLOSEPOLY: cmds.append("Z")
SVG = "_tmp.svg"
with open(SVG, "w") as f:
    f.write(f'<svg xmlns="http://www.w3.org/2000/svg"><path d="{" ".join(cmds)}"/></svg>')

# ── 2. Extract closed rings from Shapely polygons ─────────────────────────────
print("[2/5] Extracting closed rings …")
path2d = trimesh.load_path(SVG)
polys  = list(path2d.polygons_full)

rings = []
for poly in polys:
    rings.append(np.array(poly.exterior.coords))
    for interior in poly.interiors:
        rings.append(np.array(interior.coords))
print(f"  {len(polys)} polygons  →  {len(rings)} closed rings "
      f"(exterior + interior/hole boundaries)")

# ── 3. Build ribbon strips ────────────────────────────────────────────────────
print("[3/5] Building progressive-Z ribbon strips …")
all_verts, all_faces = [], []
skipped = 0

for pts in rings:
    verts, faces = _ribbon_ring(pts, DEPTH, HALF_WIDTH)
    if verts is None:
        skipped += 1
        continue
    offset = sum(len(v) for v in all_verts)
    all_verts.append(verts)
    all_faces.append(faces + offset)

if skipped:
    print(f"  ⚠ {skipped} degenerate ring(s) skipped")

V_raw = np.vstack(all_verts)
F_raw = np.vstack(all_faces)
print(f"  raw ribbon: {len(V_raw)} verts, {len(F_raw)} faces")

# Confirm no intermediate-Z verts (every vertex should be at a ring's Z value,
# which spans 0…1, but none are "cross-letter" diagonal artefacts).
ribbon = trimesh.Trimesh(vertices=V_raw, faces=F_raw, process=False)

# ── 4. Center → align Z → scale ───────────────────────────────────────────────
print("[4/5] Transform …")
ribbon.apply_translation(-(ribbon.bounds[0] + ribbon.bounds[1]) / 2.0)
# ORIENTATION FLIP — uncomment if engine renders Y inverted:
# ribbon.apply_transform(trimesh.transformations.rotation_matrix(np.pi,[1,0,0]))
ribbon.apply_translation([0, 0, -ribbon.bounds[0][2]])
s = 1.0 / ribbon.extents[0]
ribbon.apply_transform(np.diag([s, s, 1.0, 1.0]))

# ── 5. Verify + export ────────────────────────────────────────────────────────
print("[5/5] Verify + export …")
Vf = ribbon.vertices
b, e = ribbon.bounds, ribbon.extents

# Cross-letter jump check (same-Z XY edges only)
xl = []
for tri in ribbon.faces:
    for a, bi in [(0,1),(1,2),(0,2)]:
        va, vb = Vf[tri[a]], Vf[tri[bi]]
        if abs(va[2] - vb[2]) < 1e-4:
            xl.append(np.linalg.norm(va[:2] - vb[:2]))
xl  = np.array(xl)
bad = np.sum(xl > 0.25)

print(f"  X [{b[0][0]:+.4f}…{b[1][0]:+.4f}]  "
      f"Y [{b[0][1]:+.4f}…{b[1][1]:+.4f}]  "
      f"Z [{b[0][2]:+.4f}…{b[1][2]:+.4f}]")
print(f"  XY edge max={xl.max():.5f}  cross-letter jumps(>0.25): {bad} "
      f"{'✓' if bad==0 else '✗'}")

ribbon.export(OUT)
os.remove(SVG)
print(f"\n✓  {OUT}  ({len(ribbon.vertices)} verts | {len(ribbon.faces)} faces)")
