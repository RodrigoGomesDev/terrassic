"""Render menu studies from shipped geometry, animation and textures, without generative repainting.

Requires numpy, Pillow, moderngl and bpy. Minecraft's local client JAR supplies vanilla scenery textures;
it is read in place, never copied into this repository. Outputs are proposals, not packaged menu resources.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import zipfile

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "common/src/main/resources/assets/terrassic"
sys.path[:0] = [str(ROOT / "tools/capagen"), str(ROOT / "tools/modelgen")]
os.environ["BACKEND"] = "cycles"
import cenas as cn
import gl
import voxels as vx
from pybench import Rig, geo_json, pose_at


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def original_model(name, animation, fraction, sex, evidence):
    """Invert the exporter's Bedrock coordinate conversion; verify the inverse by round-trip.

    The geometry and UV offsets come from the actual packaged geo, not a freshly rebuilt species generator.
    """
    geo_path = ASSETS / "geo/entity" / (name + ".geo.json")
    anim_path = ASSETS / "animations/entity" / (name + ".animation.json")
    tex_path = ASSETS / "textures/entity" / (name + "_" + sex + ".png")
    geo = json.loads(geo_path.read_text())["minecraft:geometry"][0]
    spec = {"id": name, "texture_width": geo["description"]["texture_width"],
            "texture_height": geo["description"]["texture_height"], "bones": [], "cubes": []}
    for bone in geo["bones"]:
        pivot = bone["pivot"]
        rotation = bone.get("rotation", [0, 0, 0])
        spec["bones"].append(dict(name=bone["name"], parent=bone.get("parent"),
                                  origin=[-pivot[0], *pivot[1:]],
                                  rotation=[-rotation[0], -rotation[1], rotation[2]]))
        for cube in bone.get("cubes", []):
            if cube.get("mirror") or not isinstance(cube["uv"], list):
                raise ValueError("This study only supports unmirrored box-UV cubes")
            origin, size = cube["origin"], cube["size"]
            lo = [-origin[0] - size[0], origin[1], origin[2]]
            pivot = cube.get("pivot", [0, 0, 0])
            rotation = cube.get("rotation", [0, 0, 0])
            spec["cubes"].append(dict(bone=bone["name"], name="original", **{
                "from": lo, "to": [lo[i] + size[i] for i in range(3)],
                "origin": [-pivot[0], *pivot[1:]],
                "rotation": [-rotation[0], -rotation[1], rotation[2]],
                "uv_offset": cube["uv"], "inflate": cube.get("inflate", 0)}))
    # This checks every shipped pivot, rotation, dimension, inflation and UV offset, not just cube counts.
    exported = geo_json(spec, [0, 0, 0], [1, 1, 1])["minecraft:geometry"][0]
    assert exported["bones"] == geo["bones"], name + ": geometry round-trip mismatch"
    animations = json.loads(anim_path.read_text())["animations"]
    entry = animations["animation." + name + "." + animation]
    tracks = {"bones": {}}
    for bone, channels in entry["bones"].items():
        tracks["bones"][bone] = {}
        for channel, frames in channels.items():
            keys = []
            for timestamp, value in frames.items():
                vector = value["post"] if isinstance(value, dict) else value
                if channel == "rotation":
                    vector = [-vector[0], -vector[1], vector[2]]
                elif channel == "position":
                    vector = [-vector[0], vector[1], vector[2]]
                keys.append([float(timestamp), *vector])
            tracks["bones"][bone][channel] = keys
    evidence.append({"species": name, "animation": animation, "fraction": fraction, "sex": sex,
                     "geometry_roundtrip": True, "cubes": len(spec["cubes"]),
                     "sources": {str(p.relative_to(ROOT)): fingerprint(p) for p in (geo_path, anim_path, tex_path)}})
    return Rig(spec), Image.open(tex_path).convert("RGBA"), pose_at(tracks, fraction * entry["animation_length"])


def place(scene, name, animation, fraction, position, yaw, length, evidence, sex="male"):
    rig, texture, pose = original_model(name, animation, fraction, sex, evidence)
    hidden = ("female_display" if sex == "male" else "male_display", "saddle")
    mesh = vx.dino_mesh(rig, texture, pose, hidden, position, yaw, length)
    scene.add(mesh)


def vanilla_textures(client):
    """Sample actual 16px vanilla textures locally. No extracted source textures are distributed."""
    with zipfile.ZipFile(client) as jar:
        def tile(name, tint=None):
            image = Image.open(io.BytesIO(jar.read("assets/minecraft/textures/block/" + name + ".png"))).convert("RGBA")
            data = np.array(image.crop((0, 0, 16, 16)))
            if tint:
                data[:, :, :3] = (data[:, :, :3] * np.array(tint)).clip(0, 255).astype(np.uint8)
            return data
        textures = {"grass_top": tile("grass_block_top", (0.58, 0.78, 0.36)),
                    "grass_side": tile("grass_block_side"), "dirt": tile("dirt"),
                    "stone": tile("stone"), "sand": tile("sand"), "gravel": tile("gravel"),
                    "log": tile("spruce_log"), "log_top": tile("spruce_log_top"),
                    "leaves": tile("spruce_leaves", (0.40, 0.66, 0.44)),
                    "fern": tile("fern", (0.58, 0.78, 0.36)), "grass_plant": tile("grass", (0.58, 0.78, 0.36))}
    return textures


def forest(textures, W, H):
    rng = np.random.default_rng(271)
    world = vx.World()
    def height(x, z):
        # Quiet integer terraces, including a flat clearing; one unit remains one block.
        return 64 + int(max(0, 58 - z) // 13) + (1 if x < 30 and z < 105 else 0)
    vx.terrain(world, 0, 0, 145, 145, height, under="dirt")
    for _ in range(165):
        x, z = int(rng.integers(4, 140)), int(rng.integers(3, 135))
        if z > 64 and 46 < x < 116:
            continue
        if z > 108 and x > 40:
            continue
        vx.conifer(world, x, height(x, z) + 1, z, int(rng.integers(10, 19)), rng,
                   log="log", leaves="leaves")
    for _ in range(1600):
        x, z = int(rng.integers(2, 142)), int(rng.integers(2, 140))
        if (x, height(x, z) + 1, z) not in world.blocks:
            world.plants.append((x, height(x, z) + 1, z, "fern" if rng.random() < .45 else "grass_plant", 1))
    atlas, uv = vx.atlas(textures)
    scene = cn.Shot(W, H)
    scene.add(gl.Mesh(world.mesh(uv), atlas))
    return scene, height


LOOK = dict(top=(0.25, 0.40, 0.62), mid=(0.63, 0.68, 0.72), hor=(0.98, 0.79, 0.54),
            glow=(1.0, 0.72, 0.38), sun_col=(1.20, 1.02, 0.77), sky_amb=(.5, .55, .65),
            gnd_amb=(.3, .32, .28), fog_col=(0.77, 0.79, 0.77), fog_density=.009,
            fog_height=70, water_deep=(.1, .2, .3), clouds=0, sun_size=.0007,
            sky_strength=.85, sun_strength=5.0, fill=.8, fog_scale=.35, fog_aniso=.55)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-jar", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=ROOT / "art/menu_vanilla/v1")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--samples", type=int, default=32)
    parser.add_argument("--scene", choices=["confronto", "nevoa"], default="confronto")
    args = parser.parse_args()
    W, H = args.width, round(args.width * 9 / 16)
    cn.SAMPLES = args.samples
    # Render wider and crop the left portion, just like menu_cenas.py's Cycles lens shift.
    print("Building voxel scenery from local vanilla textures", flush=True)
    scene, height = forest(vanilla_textures(args.client_jar), round(W * 1.28), H)
    evidence = []
    if args.scene == "confronto":
        place(scene, "tyrannosaurus", "attack", .28, (91, height(91, 83) + 1, 83), 90, 12.5, evidence)
        place(scene, "triceratops", "attack", .42, (78, height(78, 84) + 1, 84), -90, 9.0, evidence)
    else:
        place(scene, "tyrannosaurus", "walk", .25, (85, height(85, 84) + 1, 84), 135, 12.5, evidence)
    print("Original geometry verified; starting Cycles", flush=True)
    image = cn.shoot(scene, (73, 67.5, 104), (84, 68, 83), 45, (-.55, .38, -.75), LOOK,
                     None, None, None, fog_box=((75, 78, 65), (155, 34, 150)), exposure=.45)
    args.out.mkdir(parents=True, exist_ok=True)
    output = args.out / (args.scene + ".png")
    image.crop((0, 0, W, H)).save(output)
    metadata = {"method": "Blender Cycles; original packaged Terrassic geometry, animations and textures",
                "scene": args.scene, "size": [W, H], "samples": args.samples,
                "vanilla_client_sha256": fingerprint(args.client_jar), "models": evidence,
                "output_sha256": fingerprint(output)}
    output.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n")
    print("Rendered original assets:", output, flush=True)


if __name__ == "__main__":
    main()
