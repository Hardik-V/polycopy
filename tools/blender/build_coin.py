"""
build_coin.py

Builds a "HARDIK" gold coin in Blender, sets up studio lighting, and
renders two top-down 1024x1024 textures intended to drop in as:

  public/textures/coaster/DIFF.webp    (albedo / colour, baked with lighting)
  public/textures/coaster/HEIGHT.webp  (height / displacement map)

Design:
  - Disc: 36 mm dia, ~3 mm thick. Slight depression on top to mirror the
    coaster's well (so the existing mesh geometry reads correctly when the
    texture is painted on).
  - Centered serif "H" in raised relief (Literata-equivalent serif fallback).
  - Two concentric ring borders around the H.
  - 24-point decorative star pattern around the rim (symmetric, mirror-safe).
  - Reeded edge (vertical ridges) around the side cylinder.
  - Gold material: warm yellow metallic with subtle anisotropy.
  - Top-down orthographic camera so the render maps 1:1 to the planar UV
    projection the engine uses for the disc top face.

Run:
    tools/bin/blender --background --python tools/blender/build_coin.py -- \
        --diff tools/out/coin_DIFF.png \
        --height tools/out/coin_HEIGHT.png \
        --res 1024

The output PNGs are then converted to WebP and placed in
public/textures/coaster/ by tools/install_coin_textures.py.
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from pathlib import Path

import bpy  # type: ignore  # available in Blender Python


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    p = argparse.ArgumentParser()
    p.add_argument("--diff", required=True, help="output PNG path for diffuse/albedo render")
    p.add_argument("--height", required=True, help="output PNG path for height map render")
    p.add_argument("--res", type=int, default=1024, help="square output resolution")
    p.add_argument("--samples", type=int, default=256, help="cycles samples")
    return p.parse_args(argv)


def reset_scene() -> None:
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    for img in list(bpy.data.images):
        if img.users == 0:
            bpy.data.images.remove(img)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam)
    for light in list(bpy.data.lights):
        bpy.data.lights.remove(light)
    for c in list(bpy.data.collections):
        if c.name != "Collection":
            bpy.data.collections.remove(c)


def add_disc(name: str, radius: float, thickness: float, segments: int = 256):
    """Add a flat cylinder representing the coin body."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=segments,
        radius=radius,
        depth=thickness,
        end_fill_type="NGON",
        location=(0, 0, 0),
    )
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.shade_smooth()
    bpy.ops.object.modifier_add(type="BEVEL")
    bevel = obj.modifiers["Bevel"]
    bevel.width = thickness * 0.10
    bevel.segments = 4
    bevel.limit_method = "ANGLE"
    bevel.angle_limit = math.radians(30)
    return obj


def add_reeded_edge(coin_obj, radius: float, thickness: float, count: int = 144) -> None:
    """Add small rectangular ridges around the side of the coin (reeding)."""
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    parent = bpy.context.active_object
    parent.name = "ReedingGroup"

    ridge_h = thickness * 0.62
    ridge_w = (2 * math.pi * radius) / (count * 2.4)
    ridge_d = radius * 0.012

    for i in range(count):
        theta = (i / count) * 2 * math.pi
        x = (radius + ridge_d * 0.45) * math.cos(theta)
        y = (radius + ridge_d * 0.45) * math.sin(theta)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0))
        ridge = bpy.context.active_object
        ridge.name = f"Reed{i:03d}"
        ridge.scale = (ridge_d, ridge_w, ridge_h)
        ridge.rotation_euler = (0, 0, theta)
        ridge.parent = parent

    bpy.ops.object.select_all(action="DESELECT")
    for child in parent.children:
        child.select_set(True)
    bpy.context.view_layer.objects.active = parent.children[0]
    bpy.ops.object.join()
    reed = bpy.context.active_object
    reed.name = "Reeding"
    bpy.ops.object.shade_smooth()
    return reed


def add_centered_text(text: str, depth: float, z: float, size: float, font_path: str | None = None):
    bpy.ops.object.text_add(location=(0, 0, z))
    obj = bpy.context.active_object
    obj.data.body = text
    obj.data.size = size
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.extrude = depth
    obj.data.bevel_depth = depth * 0.10
    obj.data.bevel_resolution = 2
    if font_path and Path(font_path).exists():
        obj.data.font = bpy.data.fonts.load(font_path)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.active_object
    obj.name = "TextH"
    bpy.ops.object.shade_smooth()
    return obj


def add_ring(radius: float, tube: float, z: float, segs: int = 256, ring_segs: int = 24):
    bpy.ops.mesh.primitive_torus_add(
        align="WORLD",
        location=(0, 0, z),
        major_radius=radius,
        minor_radius=tube,
        major_segments=segs,
        minor_segments=ring_segs,
    )
    obj = bpy.context.active_object
    bpy.ops.object.shade_smooth()
    return obj


def add_perimeter_dots(radius: float, dot_r: float, z: float, count: int = 36):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    parent = bpy.context.active_object
    parent.name = "Dots"
    for i in range(count):
        theta = (i / count) * 2 * math.pi
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=dot_r,
            location=(x, y, z),
            segments=24,
            ring_count=12,
        )
        dot = bpy.context.active_object
        dot.parent = parent

    bpy.ops.object.select_all(action="DESELECT")
    for child in parent.children:
        child.select_set(True)
    bpy.context.view_layer.objects.active = parent.children[0]
    bpy.ops.object.join()
    obj = bpy.context.active_object
    obj.name = "Dots"
    bpy.ops.object.shade_smooth()
    return obj


def make_gold_material(name: str = "Gold") -> bpy.types.Material:
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (400, 0)

    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    bsdf.inputs["Base Color"].default_value = (0.88, 0.46, 0.05, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.34
    bsdf.inputs["IOR"].default_value = 1.45

    if "Anisotropic" in bsdf.inputs:
        bsdf.inputs["Anisotropic"].default_value = 0.20

    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-600, -200)
    noise.inputs["Scale"].default_value = 280.0
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Roughness"].default_value = 0.55

    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (-300, -200)
    bump.inputs["Strength"].default_value = 0.06
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_height_material() -> bpy.types.Material:
    """Emission shader that writes per-fragment world-Z as greyscale.

    We use this for the height-map render: every coin object is assigned this
    material, then we render with no lights. The Emission RGB encodes Z.
    """
    mat = bpy.data.materials.new(name="HeightEncode")
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (400, 0)

    geom = nt.nodes.new("ShaderNodeNewGeometry")
    geom.location = (-700, 0)

    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    sep.location = (-500, 0)
    nt.links.new(geom.outputs["Position"], sep.inputs["Vector"])

    map_range = nt.nodes.new("ShaderNodeMapRange")
    map_range.location = (-300, 0)
    map_range.inputs["From Min"].default_value = -0.0030
    map_range.inputs["From Max"].default_value =  0.0030
    map_range.inputs["To Min"].default_value = 0.0
    map_range.inputs["To Max"].default_value = 1.0
    map_range.clamp = True
    nt.links.new(sep.outputs["Z"], map_range.inputs["Value"])

    emit = nt.nodes.new("ShaderNodeEmission")
    emit.location = (-100, 0)
    nt.links.new(map_range.outputs["Result"], emit.inputs["Color"])

    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    return mat


def setup_camera(disc_radius: float, frame_scale: float = 2.0) -> None:
    cam_data = bpy.data.cameras.new("OrthoCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = disc_radius * frame_scale
    cam_obj = bpy.data.objects.new("OrthoCam", cam_data)
    cam_obj.location = (0, 0, 0.40)
    cam_obj.rotation_euler = (0, 0, 0)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj


def add_backdrop(extent: float, z: float = -0.0005) -> bpy.types.Object:
    """A large flat gold plane behind the coin so the corners of the texture
    sample gold metal instead of transparent void."""
    bpy.ops.mesh.primitive_plane_add(size=extent, location=(0, 0, z))
    plane = bpy.context.active_object
    plane.name = "Backdrop"
    return plane


def setup_lights() -> None:
    """Studio softbox rig + warm sky dome.

    Energies and distances are tuned for an 18mm coin viewed top-down.
    Light intensity falls off as 1/r^2, so the small scale needs much
    lower wattage than typical product renders. Film exposure is reduced
    to keep the gold from blowing out.
    """
    for (name, energy, size, loc, rot, colour) in [
        ("KeyLight",   18.0, 0.40, ( 0.30,  0.20, 0.50), (math.radians(-25), math.radians( 30), 0), (1.0, 0.96, 0.88)),
        ("FillLight",   8.0, 0.60, (-0.40, -0.10, 0.45), (math.radians( 20), math.radians(-30), 0), (1.0, 0.98, 0.92)),
        ("RimLight",   12.0, 0.30, ( 0.00,  0.50, 0.40), (math.radians(-55), 0, 0),                  (1.0, 0.92, 0.78)),
        ("TopGlow",     6.0, 0.80, ( 0.00,  0.00, 0.80), (0, 0, 0),                                  (1.0, 0.97, 0.90)),
    ]:
        l = bpy.data.lights.new(name=name, type="AREA")
        l.size = size
        l.energy = energy
        l.color = colour
        obj = bpy.data.objects.new(name, l)
        obj.location = loc
        obj.rotation_euler = rot
        bpy.context.scene.collection.objects.link(obj)

    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    world.use_nodes = True
    bpy.context.scene.world = world
    for n in list(world.node_tree.nodes):
        world.node_tree.nodes.remove(n)
    out_w = world.node_tree.nodes.new("ShaderNodeOutputWorld")
    bg = world.node_tree.nodes.new("ShaderNodeBackground")
    grad = world.node_tree.nodes.new("ShaderNodeTexGradient")
    coord = world.node_tree.nodes.new("ShaderNodeTexCoord")
    ramp = world.node_tree.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.02, 0.02, 0.03, 1.0)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (0.25, 0.22, 0.18, 1.0)
    world.node_tree.links.new(coord.outputs["Generated"], grad.inputs["Vector"])
    world.node_tree.links.new(grad.outputs["Fac"], ramp.inputs["Fac"])
    world.node_tree.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.6
    world.node_tree.links.new(bg.outputs["Background"], out_w.inputs["Surface"])

    bpy.context.scene.view_settings.view_transform = "Standard"
    bpy.context.scene.view_settings.look = "None"
    bpy.context.scene.view_settings.exposure = -2.4
    bpy.context.scene.view_settings.gamma = 1.0


def configure_render(res: int, samples: int) -> None:
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.cycles.samples = samples
    s.cycles.use_denoising = True
    s.render.resolution_x = res
    s.render.resolution_y = res
    s.render.resolution_percentage = 100
    s.render.film_transparent = False
    s.render.image_settings.file_format = "PNG"
    s.render.image_settings.color_mode = "RGBA"
    s.render.image_settings.color_depth = "8"


def assign_material(obj, mat) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def build_coin(radius: float, thickness: float) -> list:
    """Build the coin design ONLY in the inner ~25% of the texture frame.

    The engine's planar UV samples the centre of the texture into the disc's
    inner well and the outer parts of the texture onto the rim/slope/side.
    To get a clean "H in the well, polished gold rim" read, we keep ALL
    decorative elements inside the inner zone and leave the rest of the
    frame as plain gold backdrop.

    `radius` here is the COIN body radius. The decoration sits well inside.
    """
    objs = []

    body = add_disc("CoinBody", radius=radius, thickness=thickness, segments=256)
    objs.append(body)

    reeding = add_reeded_edge(body, radius=radius, thickness=thickness, count=144)
    objs.append(reeding)

    deco_extent = radius * 0.55

    outer_ring = add_ring(
        radius=deco_extent * 1.00,
        tube=radius * 0.012,
        z=thickness * 0.5 + 0.0001,
    )
    outer_ring.name = "RingOuter"
    objs.append(outer_ring)

    inner_ring = add_ring(
        radius=deco_extent * 0.88,
        tube=radius * 0.008,
        z=thickness * 0.5 + 0.0001,
    )
    inner_ring.name = "RingInner"
    objs.append(inner_ring)

    h_text = add_centered_text(
        text="H",
        depth=thickness * 0.22,
        z=thickness * 0.5,
        size=deco_extent * 1.40,
        font_path="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    )
    objs.append(h_text)

    return objs


def render_to(path: str) -> None:
    bpy.context.scene.render.filepath = os.path.abspath(path)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    args = parse_args()
    Path(args.diff).parent.mkdir(parents=True, exist_ok=True)
    Path(args.height).parent.mkdir(parents=True, exist_ok=True)

    radius = 0.018
    thickness = 0.0030

    reset_scene()
    setup_camera(disc_radius=radius, frame_scale=2.06)
    setup_lights()
    configure_render(args.res, args.samples)

    gold = make_gold_material("Gold")

    backdrop = add_backdrop(extent=radius * 8.0, z=thickness * 0.5 - 0.00005)
    assign_material(backdrop, gold)

    objs = build_coin(radius=radius, thickness=thickness)
    for o in objs:
        assign_material(o, gold)
    objs.append(backdrop)

    render_to(args.diff)
    print(f"wrote DIFF -> {args.diff}")

    height_mat = make_height_material()
    for o in objs:
        assign_material(o, height_mat)

    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.cycles.samples = max(64, args.samples // 4)
    for l_obj in [o for o in bpy.data.objects if o.type == "LIGHT"]:
        bpy.data.objects.remove(l_obj, do_unlink=True)
    world = bpy.context.scene.world
    if world and world.node_tree:
        bg = world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Strength"].default_value = 0.0

    render_to(args.height)
    print(f"wrote HEIGHT -> {args.height}")


if __name__ == "__main__":
    main()
