"""
buf_codec.py

Parser + serializer for the Lusion .buf 3D-asset format used in
public/models/. Reverse-engineered from public/scripts/main.js.

File layout:
    [uint32 LE header_length]
    [JSON header of header_length bytes]
    [concatenated attribute payloads, in declaration order]

Each attribute in the JSON header has:
    id              : str          e.g. "position", "normal", "uv", "indices", "Cd", "side", "orient", "scale"
    componentSize   : int          components per element (1, 2, 3, 4)
    storageType     : str          one of "Int8Array", "Uint8Array", "Int16Array",
                                   "Uint16Array", "Float32Array"
    needsPack       : bool
    packedComponents: list?        only if needsPack — one entry per component:
                                       { "from": float, "delta": float }

Element count for an attribute is:
    indexCount   if id == "indices"
    vertexCount  otherwise

Engine's unpack formula (per component):
    F      = 1 << (bytesPerElement * 8)        # 256 or 65536
    offset = F * 0.5  if storageType starts with "Int"  else  0
    scale  = 1 / (F - 1)
    actual = (raw + offset) * scale * delta + from

Our pack formula is the algebraic inverse:
    raw    = round((actual - from) / delta * (F - 1)) - offset
"""

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

    header_json = json.dumps(meta, separators=(", ", ": "))
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
    """Compute (from, delta) per component from raw float data."""
    v = np.asarray(values, dtype=np.float64).reshape(-1, component_size)
    mins = v.min(axis=0)
    maxs = v.max(axis=0)
    return mins.tolist(), (maxs - mins).tolist()


def _roundtrip_test(path: str) -> None:
    print(f"--- roundtrip: {path}")
    orig = parse(path)
    serialized = serialize(orig)
    reparsed = BufFile(
        vertex_count=orig.vertex_count,
        index_count=orig.index_count,
        mesh_type=orig.mesh_type,
        attributes=orig.attributes,
    )
    reparsed2 = parse(path)
    out_path = Path(path).with_suffix(".roundtrip.buf")
    out_path.write_bytes(serialized)
    re = parse(out_path)
    for a, b in zip(orig.attributes, re.attributes):
        if a.data is None or b.data is None:
            continue
        if a.data.dtype.kind == "f":
            diff = np.max(np.abs(a.data.astype(np.float64) - b.data.astype(np.float64)))
            print(f"  {a.id:10s} max abs diff = {diff:.6g}")
        else:
            diff = int(np.max(np.abs(a.data.astype(np.int64) - b.data.astype(np.int64))))
            print(f"  {a.id:10s} max abs diff = {diff}")
    out_path.unlink()


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:] or ["public/models/coaster.buf"]:
        _roundtrip_test(p)
