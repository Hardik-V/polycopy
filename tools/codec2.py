from __future__ import annotations

import json
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

STORAGE_INFO: dict[str, tuple[type, int, bool]] = {
    "Int8Array":    (np.int8,    1, True),
    "Uint8Array":   (np.uint8,   1, False),
    "Int16Array":   (np.int16,   2, True),
    "Uint16Array":  (np.uint16,  2, False),
    "Float32Array": (np.float32, 4, False),
}

@dataclass
class Attribute:
    id: str
    component_size: int
    storage_type: str
    needs_pack: bool
    packed_from: list[float] = field(default_factory=list)
    packed_delta: list[float] = field(default_factory=list)
    data: np.ndarray | None = None

    @property
    def dtype(self) -> type:
        return STORAGE_INFO[self.storage_type][0]

    @property
    def bytes_per_element(self) -> int:
        return STORAGE_INFO[self.storage_type][1]

    @property
    def signed(self) -> bool:
        return STORAGE_INFO[self.storage_type][2]

    def to_meta(self) -> dict[str, Any]:
        meta: dict[str, Any] = {
            "id": self.id,
            "needsPack": self.needs_pack,
            "componentSize": self.component_size,
            "storageType": self.storage_type,
        }
        if self.needs_pack:
            meta["packedComponents"] = [
                {"from": float(self.packed_from[i]), "delta": float(self.packed_delta[i])}
                for i in range(self.component_size)
            ]
        return meta

@dataclass
class BufFile:
    vertex_count: int
    index_count: int
    mesh_type: str = "Mesh"
    attributes: list[Attribute] = field(default_factory=list)
    extra_meta: dict[str, Any] = field(default_factory=dict)

    def attr(self, id_: str) -> Attribute | None:
        for a in self.attributes:
            if a.id == id_:
                return a
        return None

    def count_for(self, attr: Attribute) -> int:
        return self.index_count if attr.id == "indices" else self.vertex_count

def _unpack(raw: np.ndarray, attr: Attribute) -> np.ndarray:
    if not attr.needs_pack:
        return raw.astype(np.float32) if attr.storage_type != "Float32Array" else raw

    F = 1 << (attr.bytes_per_element * 8)
    offset = F * 0.5 if attr.signed else 0
    scale = 1.0 / (F - 1)

    raw_f = raw.astype(np.float64).reshape(-1, attr.component_size)
    out = np.empty_like(raw_f, dtype=np.float32)
    for c in range(attr.component_size):
        out[:, c] = ((raw_f[:, c] + offset) * scale * attr.packed_delta[c]
                     + attr.packed_from[c]).astype(np.float32)
    return out.reshape(-1) if attr.component_size == 1 else out

def _pack(values: np.ndarray, attr: Attribute) -> np.ndarray:
    if not attr.needs_pack:
        return values.astype(attr.dtype)

    F = 1 << (attr.bytes_per_element * 8)
    offset = F * 0.5 if attr.signed else 0
    scale = F - 1

    v = values.astype(np.float64).reshape(-1, attr.component_size)
    out = np.empty_like(v, dtype=np.int64)
    for c in range(attr.component_size):
        d = attr.packed_delta[c]
        f = attr.packed_from[c]
        if d == 0:
            out[:, c] = 0
        else:
            normed = (v[:, c] - f) / d
            out[:, c] = np.round(normed * scale).astype(np.int64) - int(offset)

    if attr.signed:
        info = np.iinfo(attr.dtype)
        out = np.clip(out, info.min, info.max)
    else:
        info = np.iinfo(attr.dtype)
        out = np.clip(out, info.min, info.max)
    return out.astype(attr.dtype).reshape(-1)

def parse(path: str | Path) -> BufFile:
    data = Path(path).read_bytes()
    (header_len,) = struct.unpack("<I", data[:4])
    meta = json.loads(data[4:4 + header_len].decode("utf-8"))
    body = data[4 + header_len:]

    buf = BufFile(
        vertex_count=meta["vertexCount"],
        index_count=meta.get("indexCount", 0),
        mesh_type=meta.get("meshType", "Mesh"),
    )
    for k, v in meta.items():
        if k not in {"vertexCount", "indexCount", "attributes", "meshType"}:
            buf.extra_meta[k] = v

    offset = 0
    for am in meta["attributes"]:
        attr = Attribute(
            id=am["id"],
            component_size=am["componentSize"],
            storage_type=am["storageType"],
            needs_pack=am["needsPack"],
        )
        if attr.needs_pack:
            pc = am["packedComponents"]
            attr.packed_from = [c["from"] for c in pc]
            attr.packed_delta = [c["delta"] for c in pc]

        count = buf.count_for(attr)
        bytes_needed = count * attr.component_size * attr.bytes_per_element
        raw = np.frombuffer(body, dtype=attr.dtype,
                            count=count * attr.component_size,
                            offset=offset)
        attr.data = _unpack(raw, attr)
        offset += bytes_needed
        buf.attributes.append(attr)

    return buf

def serialize(buf: BufFile) -> bytes:
    meta: dict[str, Any] = {
        "vertexCount": int(buf.vertex_count),
        "indexCount": int(buf.index_count),
        "attributes": [a.to_meta() for a in buf.attributes],
        "meshType": buf.mesh_type,
    }
    for k, v in buf.extra_meta.items():
        meta[k] = v

    header_json = json.dumps(meta, separators=(",", ":"))
    header_bytes = header_json.encode("utf-8")

    body_offset = 4 + len(header_bytes)
    pad = (-body_offset) % 4
    if pad:
        header_bytes = header_bytes + b" " * pad

    body = bytearray()
    for attr in buf.attributes:
        count = buf.count_for(attr)
        if attr.data is None:
            raise ValueError(f"attribute {attr.id} has no data")
        expected = count * attr.component_size
        flat_count = (attr.data.size
                      if attr.component_size == 1 or attr.data.ndim == 1
                      else attr.data.shape[0] * attr.data.shape[1])
        if flat_count != expected:
            raise ValueError(
                f"attribute {attr.id}: expected {expected} components, "
                f"got {flat_count}"
            )
        raw = _pack(attr.data, attr)
        body.extend(raw.tobytes())

    return struct.pack("<I", len(header_bytes)) + header_bytes + bytes(body)

def auto_pack_params(values: np.ndarray, component_size: int) -> tuple[list[float], list[float]]:
    v = np.asarray(values, dtype=np.float64).reshape(-1, component_size)
    mins = v.min(axis=0)
    maxs = v.max(axis=0)
    return mins.tolist(), (maxs - mins).tolist()

def export_to_obj(buf: BufFile, out_path: str):
    pos_attr = buf.attr("position")
    idx_attr = buf.attr("indices")

    if not pos_attr or not idx_attr:
        print(f"Error: Missing position or index data in {out_path}")
        return

    vertices = pos_attr.data.reshape(-1, 3)
    indices = idx_attr.data.reshape(-1, 3)

    print(f"Exporting {len(vertices)} vertices and {len(indices)} faces to {out_path}...")
    
    with open(out_path, 'w') as f:
        f.write("# Exported from .buf format\n")
        for v in vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        for face in indices:
            f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
            
    print("Export complete!")

def import_from_obj(obj_path: str) -> BufFile:
    """Reads a .obj file (with normals and UVs) and constructs a BufFile."""
    raw_v, raw_vt, raw_vn = [], [], []
    out_v, out_vt, out_vn, out_indices = [], [], [], []
    
    # OBJ files can have independent indices for pos/uv/normal. 
    # WebGL requires them unified, so we map them here.
    vertex_map = {}
    
    with open(obj_path, 'r') as f:
        for line in f:
            if line.startswith('v '):
                raw_v.append([float(x) for x in line.split()[1:4]])
            elif line.startswith('vt '):
                raw_vt.append([float(x) for x in line.split()[1:3]])
            elif line.startswith('vn '):
                raw_vn.append([float(x) for x in line.split()[1:4]])
            elif line.startswith('f '):
                parts = line.split()[1:]
                face_indices = []
                for p in parts[:3]: # Ensure we only read 3 points (triangles)
                    vals = p.split('/')
                    # FIX: Cast to float first to handle weird .0 formats, then int
                    v_idx = int(float(vals[0])) - 1
                    vt_idx = int(float(vals[1])) - 1 if len(vals) > 1 and vals[1] else -1
                    vn_idx = int(float(vals[2])) - 1 if len(vals) > 2 and vals[2] else -1
                    
                    key = (v_idx, vt_idx, vn_idx)
                    if key not in vertex_map:
                        vertex_map[key] = len(out_v)
                        out_v.append(raw_v[v_idx])
                        out_vt.append(raw_vt[vt_idx] if vt_idx >= 0 else [0.0, 0.0])
                        out_vn.append(raw_vn[vn_idx] if vn_idx >= 0 else [0.0, 1.0, 0.0])
                        
                    face_indices.append(vertex_map[key])
                out_indices.extend(face_indices)
                
    # Convert to flat numpy arrays
    pos_data = np.array(out_v, dtype=np.float32).flatten()
    uv_data = np.array(out_vt, dtype=np.float32).flatten()
    norm_data = np.array(out_vn, dtype=np.float32).flatten()
    idx_data = np.array(out_indices, dtype=np.uint32)
    cd_data = np.ones(len(out_v), dtype=np.float32) # Default color to 1.0 everywhere
    
    # Calculate Bounding Box and Sphere for the engine
    v_reshaped = pos_data.reshape(-1, 3)
    vmin = v_reshaped.min(axis=0)
    vmax = v_reshaped.max(axis=0)
    center = (vmin + vmax) / 2.0
    radius = float(np.max(np.linalg.norm(v_reshaped - center, axis=1)))
    
    bounds = {
        "boundingBox": {"min": vmin.tolist(), "max": vmax.tolist()},
        "boundingSphere": {"center": center.tolist(), "radius": radius}
    }
    
    # Calculate packing parameters
    p_from, p_delta = auto_pack_params(pos_data, 3)
    n_from, n_delta = auto_pack_params(norm_data, 3)
    u_from, u_delta = auto_pack_params(uv_data, 2)
    c_from, c_delta = auto_pack_params(cd_data, 1)

    # Prevent division by zero if an attribute is entirely uniform
    n_delta = [max(d, 1e-6) for d in n_delta]
    u_delta = [max(d, 1e-6) for d in u_delta]
    p_delta = [max(d, 1e-6) for d in p_delta]
    c_delta = [max(d, 1e-6) for d in c_delta]

    # Build the 5 required attributes exactly as the engine expects
    attributes = [
        Attribute(id="Cd", component_size=1, storage_type="Int16Array", needs_pack=True, packed_from=c_from, packed_delta=c_delta, data=cd_data),
        Attribute(id="indices", component_size=1, storage_type="Uint16Array" if len(out_v) <= 65535 else "Uint32Array", needs_pack=False, data=idx_data),
        Attribute(id="normal", component_size=3, storage_type="Uint16Array", needs_pack=True, packed_from=n_from, packed_delta=n_delta, data=norm_data),
        Attribute(id="position", component_size=3, storage_type="Uint16Array", needs_pack=True, packed_from=p_from, packed_delta=p_delta, data=pos_data),
        Attribute(id="uv", component_size=2, storage_type="Int16Array", needs_pack=True, packed_from=u_from, packed_delta=u_delta, data=uv_data),
    ]
    
    return BufFile(
        vertex_count=len(out_v),
        index_count=len(idx_data),
        attributes=attributes,
        extra_meta=bounds
    )
    
    with open(obj_path, 'r') as f:
        for line in f:
            if line.startswith('v '):
                parts = line.split()
                vertices.extend([float(parts[1]), float(parts[2]), float(parts[3])])
            elif line.startswith('f '):
                parts = line.split()
                indices.extend([int(parts[1].split('/')[0]) - 1, 
                                int(parts[2].split('/')[0]) - 1, 
                                int(parts[3].split('/')[0]) - 1])
                
    pos_data = np.array(vertices, dtype=np.float32)
    idx_data = np.array(indices, dtype=np.uint16)
    
    v_reshaped = pos_data.reshape(-1, 3)
    vmin = v_reshaped.min(axis=0)
    vmax = v_reshaped.max(axis=0)
    center = (vmin + vmax) / 2.0
    radius = np.max(np.linalg.norm(v_reshaped - center, axis=1))
    
    bounds = {
        "boundingBox": {"min": vmin.tolist(), "max": vmax.tolist()},
        "boundingSphere": {"center": center.tolist(), "radius": float(radius)}
    }
    
    mins, deltas = auto_pack_params(pos_data, 3)
    
    pos_attr = Attribute(
        id="position", component_size=3, storage_type="Uint16Array",
        needs_pack=True, packed_from=mins, packed_delta=deltas, data=pos_data
    )
    
    idx_attr = Attribute(
        id="indices", component_size=1, storage_type="Uint16Array",
        needs_pack=False, data=idx_data
    )
    
    return BufFile(
        vertex_count=len(pos_data) // 3,
        index_count=len(idx_data),
        attributes=[idx_attr, pos_attr], 
        extra_meta=bounds
    )

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Decode: python buf_codec.py decode <path_to_buf_file>")
        print("  Encode: python buf_codec.py encode <path_to_obj_file>")
        sys.exit(1)
        
    command = sys.argv[1].lower()
    file_path = sys.argv[2]
    
    if command == "decode":
        parsed_buf = parse(file_path)
        out_name = str(Path(file_path).with_suffix('.obj'))
        export_to_obj(parsed_buf, out_name)
    elif command == "encode":
        buf = import_from_obj(file_path)
        out_path = Path(file_path).with_suffix('.buf')
        out_path.write_bytes(serialize(buf))
        print(f"Successfully encoded to {out_path}!")
    else:
        print(f"Unknown command: {command}. Use 'encode' or 'decode'.")