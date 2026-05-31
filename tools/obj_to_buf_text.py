#!/usr/bin/env python3
"""
OBJ to .buf converter — TEXT mesh.

The text shader expects exactly TWO attributes:
  indices   (Uint16Array, 1 component) — face indices
  position  (Uint16Array, 3 components) — XYZ vertex position

Buffers are written contiguously with NO inter-buffer padding.
Only the JSON header length field is 4-byte aligned (the JSON itself is
padded with spaces to that alignment).

Usage:
  python3 obj_to_buf_text.py input.obj output.buf
"""

import sys, json, struct
import numpy as np


def read_obj(path):
    verts, indices = [], []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            p = line.split()
            if p[0] == 'v':
                verts.append([float(p[1]), float(p[2]), float(p[3])])
            elif p[0] == 'f':
                face = [int(float(x.split('/')[0])) - 1 for x in p[1:]]
                for i in range(1, len(face) - 1):
                    indices.extend([face[0], face[i], face[i + 1]])
    return np.array(verts, dtype=np.float64), indices


def align4(n):
    return (n + 3) & ~3


def pack_uint16(vals, from_val, delta):
    p = np.round((vals - from_val) / delta * 65535.0).astype(np.int64)
    return np.clip(p, 0, 65535).astype(np.uint16)


def obj_to_buf_text(obj_path, buf_path):
    print(f"Reading OBJ: {obj_path}")
    verts, idx_list = read_obj(obj_path)
    nv = len(verts)
    ni = len(idx_list)
    print(f"  {nv} vertices, {ni // 3} triangles ({ni} indices)")

    if nv > 65535:
        print(f"WARNING: {nv} vertices exceeds uint16 max (65535)")

    bb_min = verts.min(axis=0).tolist()
    bb_max = verts.max(axis=0).tolist()
    center = [(bb_min[i] + bb_max[i]) / 2 for i in range(3)]
    diffs = verts - np.array(center)
    radius = float(np.sqrt((diffs ** 2).sum(axis=1)).max())

    pos_deltas = [bb_max[i] - bb_min[i] if bb_max[i] != bb_min[i] else 1e-6 for i in range(3)]
    pos_packed = [{"from": bb_min[i], "delta": pos_deltas[i]} for i in range(3)]

    header = {
        "vertexCount": nv,
        "indexCount":  ni,
        "attributes": [
            {
                "id": "indices",
                "needsPack": False,
                "componentSize": 1,
                "storageType": "Uint16Array"
            },
            {
                "id": "position",
                "needsPack": True,
                "componentSize": 3,
                "storageType": "Uint16Array",
                "packedComponents": pos_packed
            }
        ],
        "meshType": "Mesh",
        "boundingBox":    {"min": bb_min, "max": bb_max},
        "boundingSphere": {"center": center, "radius": radius}
    }

    json_bytes = json.dumps(header, separators=(',', ':')).encode('utf-8')
    jla = align4(len(json_bytes))

    idx_buf = np.array(idx_list, dtype=np.uint16).tobytes()
    pos_packed_cols = [pack_uint16(verts[:, i], bb_min[i], pos_deltas[i]) for i in range(3)]
    pos_buf = np.column_stack(pos_packed_cols).tobytes()

    print(f"Writing BUF: {buf_path}")
    with open(buf_path, 'wb') as f:
        # 4-byte aligned length of JSON
        f.write(struct.pack('<I', jla))
        # JSON header padded with spaces
        f.write(json_bytes)
        f.write(b' ' * (jla - len(json_bytes)))
        # Binary buffers — NO inter-buffer padding
        f.write(idx_buf)
        f.write(pos_buf)

    total = 4 + jla + len(idx_buf) + len(pos_buf)
    print(f"  Done. {total} bytes written.")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 obj_to_buf_text.py <input.obj> <output.buf>")
        sys.exit(1)
    obj_to_buf_text(sys.argv[1], sys.argv[2])
