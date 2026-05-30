import trimesh
import numpy as np
from matplotlib.textpath import TextPath
from matplotlib.path import Path

print("Generating 2D text path...")
tp = TextPath((0, 0), "HARDIK VERMA", size=1, prop={"weight": "bold", "family": "sans-serif"})

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

with open("temp_text.svg", "w") as f:
    f.write(f'<svg xmlns="http://www.w3.org/2000/svg"><path d="{svg_path}" /></svg>')

print("Building true ribbon wireframe...")
path2d = trimesh.load_path("temp_text.svg")

vertices = []
faces = []

# Traces the invisible 2D vector lines
for line in path2d.discrete:
    n = len(line)
    if n < 2:
        continue
        
    base = len(vertices)
    
    # Create the front (Z=0) and back (Z=1.0) point for every curve
    for x, y in line:
        vertices.append([x, y, 0.0])
        vertices.append([x, y, 1.0])
        
    # Connect the dots into paper-thin walls
    for i in range(n - 1):
        f0 = base + i * 2       
        b0 = f0 + 1             
        f1 = base + (i + 1) * 2 
        b1 = f1 + 1             
        
        faces.append([f0, b0, f1])
        faces.append([f1, b0, b1])

final_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

# 1. Center the text perfectly
final_mesh.apply_translation(-final_mesh.centroid)

# 2. THE MIRROR & UPSIDE-DOWN FIX: 180 DEGREE Z-ROTATION
# This spins the text like a steering wheel, fixing X and Y simultaneously
rotation = trimesh.transformations.rotation_matrix(np.pi, [0, 0, 1])
final_mesh.apply_transform(rotation)

# 3. Align Z exactly to 0
z_min = final_mesh.bounds[0][2]
final_mesh.apply_translation([0, 0, -z_min])

# 4. Scale to match original width (~1.0) while keeping Z depth at 1.0
target_width = 1.0
current_width = final_mesh.extents[0]
scale_factor = target_width / current_width
final_mesh.apply_scale([scale_factor, scale_factor, 1.0])

out_file = 'hardik_outline.obj'
final_mesh.export(out_file)

print(f"Success! Exported {out_file}")
print(f"Vertices: {len(final_mesh.vertices)} | Faces: {len(final_mesh.faces)}")