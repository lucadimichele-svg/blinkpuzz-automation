"""Entry point executed inside Blender. A transparent sprite atlas shares the set camera."""

import json
import math
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


def world(p):
    return ((p[0] - 540) / 100, (960 - p[1]) / 100, p[2] / 100)


def rgb(hexcode):
    def linear(x):
        c = int(x, 16) / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return tuple(linear(hexcode[i : i + 2]) for i in (1, 3, 5)) + (1,)


def mesh_for(n):
    kind = n["kind"]
    if kind == "box":
        w, d, h = n["size"]
        outer = [[-w / 2, -d / 2], [w / 2, -d / 2], [w / 2, d / 2], [-w / 2, d / 2]]
    elif kind == "disc":
        r, h, count = n["r"], n["h"], n["n"]
        outer = [
            [r * math.cos(math.tau * i / count), r * math.sin(math.tau * i / count)]
            for i in range(count)
        ]
    elif kind == "profile":
        outer, h = n["outline"], n["h"]
    else:
        sx, sy, sz = n["size"]
        rings = 10
        seg = 24
        v = [(0, 0, sz / 100)]
        f = []
        for j in range(1, rings):
            for i in range(seg):
                a, b = math.pi * j / rings, math.tau * i / seg
                v.append(
                    (
                        sx * math.sin(a) * math.cos(b) / 100,
                        sy * math.sin(a) * math.sin(b) / 100,
                        sz * math.cos(a) / 100,
                    )
                )
        v.append((0, 0, -sz / 100))
        for i in range(seg):
            k = (i + 1) % seg
            f.append((0, 1 + i, 1 + k))
            for j in range(rings - 2):
                u = 1 + j * seg
                f.append((u + i, u + i + seg, u + k + seg, u + k))
            u = 1 + (rings - 2) * seg
            f.append((u + i, len(v) - 1, u + k))
        return v, f
    hole = n.get("hole")
    contours = [outer, hole] if hole else [outer]
    v = [(x / 100, -y / 100, z / 100) for pts in contours for z in (-h / 2, h / 2) for x, y in pts]
    m = len(outer)
    f = []
    for i in range(m):
        j = (i + 1) % m
        f.append((i, m + i, m + j, j))
        if hole:
            f.extend(
                [
                    (2 * m + i, 2 * m + j, 3 * m + j, 3 * m + i),
                    (m + i, 3 * m + i, 3 * m + j, m + j),
                    (i, j, 2 * m + j, 2 * m + i),
                ]
            )
    if not hole:
        f.extend([tuple(range(m)), tuple(reversed(range(m, 2 * m)))])
    return v, f


def render(spec, out):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 9
    sc.cycles.use_denoising = False
    sc.cycles.max_bounces = 3
    sc.cycles.diffuse_bounces = 2
    sc.cycles.glossy_bounces = 2
    sc.render.resolution_x = 1080
    sc.render.resolution_y = 1920
    sc.render.resolution_percentage = 75
    sc.render.threads_mode = "FIXED"
    sc.render.threads = 2
    sc.world = bpy.data.worlds.new("Studio ambient")
    sc.world.use_nodes = True
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.56, 0.64, 0.76, 1)
    sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.38
    mats = {}
    for name, (col, metal, rough) in spec["palette"].items():
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        nt = m.node_tree
        bs = nt.nodes.get("Principled BSDF")
        bs.inputs["Base Color"].default_value = rgb(col)
        bs.inputs["Metallic"].default_value = metal
        bs.inputs["Roughness"].default_value = rough
        if name == "lume":
            bs.inputs["Emission Color"].default_value = rgb(col)
            bs.inputs["Emission Strength"].default_value = 0.9
        if name in (
            "walnut",
            "oak",
            "stone",
            "sand",
            "linen",
            "slate",
            "velvet",
            "jade",
            "wing",
            "copper",
        ):
            noise = nt.nodes.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value = 34 if name != "walnut" else 8
            noise.inputs["Detail"].default_value = 2
            bump = nt.nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value = 0.23
            bump.inputs["Distance"].default_value = 0.035
            nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
            nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
        mats[name] = m
    tilt = math.radians(spec["tilt"])
    camera = bpy.data.cameras.new("Ortho")
    cam = bpy.data.objects.new("CAMERA", camera)
    sc.collection.objects.link(cam)
    cam.location = (0, -30 * math.sin(tilt), 30 * math.cos(tilt))
    cam.rotation_euler = (tilt, 0, 0)
    camera.type = "ORTHO"
    camera.ortho_scale = 19.2
    sc.camera = cam

    def light(name, loc, energy, size, color):
        l = bpy.data.lights.new(name, "AREA")
        l.energy = energy
        l.shape = "DISK"
        l.size = size
        l.color = color
        obj = bpy.data.objects.new(name, l)
        sc.collection.objects.link(obj)
        obj.location = loc
        obj.rotation_euler = (-Vector(loc)).to_track_quat("-Z", "Y").to_euler()

    warm = spec["family"] in ("search", "maze", "shadow", "gears")
    light("Window", (-5, 4, 10), 1500, 6, (1, 0.82, 0.62) if warm else (0.75, 0.9, 1))
    light("Rim", (5, -2, 7), 920, 4, (0.72, 0.88, 1) if warm else (1, 0.74, 0.51))
    light("Softbox", (0, 6, 8), 470, 7, (1, 0.95, 0.83))
    static = []
    groups = {}
    measurements = {}
    for i, n in enumerate(spec["nodes"]):
        name = n.get("tag", f"part-{i}")
        if n["kind"] == "tube":
            mesh = bpy.data.curves.new(name, "CURVE")
            mesh.dimensions = "3D"
            mesh.resolution_u = 1
            mesh.bevel_depth = n["r"] / 100
            mesh.bevel_resolution = 3
            mesh.use_fill_caps = True
            spline = mesh.splines.new("POLY")
            spline.points.add(len(n["points"]) - 1)
            origin = Vector(world(n["pos"]))
            for pt, coord in zip(spline.points, n["points"]):
                pt.co = (*(Vector(world(coord)) - origin), 1)
        else:
            vertices, faces = mesh_for(n)
            mesh = bpy.data.meshes.new(name)
            mesh.from_pydata(vertices, [], faces)
            mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        sc.collection.objects.link(obj)
        obj.location = world(n["pos"])
        obj.rotation_euler.z = -math.radians(n.get("angle", 0))
        mesh.materials.append(mats[n["mat"]])
        if n.get("bevel", 0) > 0:
            mod = obj.modifiers.new("Milled edge", "BEVEL")
            mod.width = n["bevel"] / 100
            mod.segments = 2
            mod.affect = "EDGES"
            obj.modifiers.new("Face normals", "WEIGHTED_NORMAL")
        if n["kind"] == "ball":
            for face in mesh.polygons:
                face.use_smooth = True
        if n.get("tag"):
            measurements[name] = obj
        if n.get("group"):
            groups.setdefault(n["group"], []).append(obj)
            obj.hide_render = True
        else:
            static.append(obj)
    bpy.context.view_layer.update()

    def project(co):
        q = world_to_camera_view(sc, cam, co)
        return [round(q.x * 1080, 3), round((1 - q.y) * 1920, 3)]

    receipt = {k: project(obj.matrix_world.translation) for k, obj in measurements.items()}
    (out / "projection.json").write_text(json.dumps(receipt))

    def save(name):
        sc.render.image_settings.file_format = "PNG"
        sc.render.image_settings.color_mode = "RGBA"
        sc.render.filepath = str(out / name)
        bpy.ops.render.render(write_still=True)

    save("stage.png")
    if groups:
        for obj in static:
            obj.hide_render = True
        sc.render.film_transparent = True
        for i, (key, objects) in enumerate(groups.items()):
            x, y = spec["sprites"][key]["center"]
            # The biggest individual silhouette fits inside a 320 x 320 native tile.
            ax, ay = 180 + 360 * (i % 3), 190 + 340 * (i // 3)
            spec["sprites"][key]["atlas"] = [ax, ay]
            shift = Vector(((ax - x) / 100, (y - ay) / (100 * math.cos(tilt)), 0))
            for obj in objects:
                obj.hide_render = False
                obj.location += shift
        save("atlas.png")
    (out / "sprites.json").write_text(json.dumps(spec["sprites"]))


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1 :]
    render(json.loads(Path(args[0]).read_text()), Path(args[1]))
