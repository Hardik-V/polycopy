import trimesh
import numpy as np
from matplotlib.textpath import TextPath
from matplotlib.path import Path

print("Generating 2D text path...")
# 1. Use matplotlib to extract the mathematically perfect font curves
tp = TextPath((0, 0), "HARDIK VERMA", size=1, prop={"weight": "bold", "family": "sans-serif"})

# 2. Convert matplotlib paths to standard SVG format
svg_path = ""
for verts, code in tp.iter_segments():
    if code == Path.MOVETO:
        svg_path += f"M {verts[0]} {verts[1]} "
    elif code == Path.LINETO:
        svg_path += f"L {verts[0]} {verts[1]} "
    elif code == Path.CURVE3:
        svg_path += f"Q {verts[0]} {verts[1]} {verts[2]} {verts[3]} "
    elif code == Path.CURVE4:
        svg_path += f"C {verts[0]} {verts[1]} {verts[2]} {verts[3]} {verts[4]} {verts[5]} "
    elif code == Path.CLOSEPOLY:
        svg_path += "Z "

# Write to a temporary SVG file
svg_xml = f'<svg xmlns="http://www.w3.org/2000/svg"><path d="{svg_path}" /></svg>'
with open("temp_text.svg", "w") as f:
    f.write(svg_xml)

print("Extruding SVG into 3D...")
# 3. Trimesh parses the SVG flawlessly, calculating holes inside letters (like R, D, A) automatically
path2d = trimesh.load_path("temp_text.svg")

# 4. Extrude every separate polygon (each letter/part)
meshes = []
for polygon in path2d.polygons_full:
    mesh = trimesh.creation.extrude_polygon(polygon, height=1.0)
    meshes.append(mesh)

# Combine them all into one 3D object
final_mesh = trimesh.util.concatenate(meshes)

# 5. Flip Y axis (SVG coordinates are upside-down compared to standard 3D space)
final_mesh.apply_scale([1, 1, -1])

# 6. Center the text perfectly
final_mesh.apply_translation(-final_mesh.centroid)

# 7. Scale to match original coaster bounds (~1.0 width)
target_width = 1.0
current_width = final_mesh.extents[0]
final_mesh.apply_scale(target_width / current_width)

# 8. Export!
out_file = 'hardik_text.obj'
final_mesh.export(out_file)

print(f"Success! Exported {out_file}")
print(f"Vertices: {len(final_mesh.vertices)} | Faces: {len(final_mesh.faces)}")