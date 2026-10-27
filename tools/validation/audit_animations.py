"""Audit existing animation sources without exporting or modifying game assets.

Run: python3 -B tools/validation/audit_animations.py [--render]
Requires the modelgen dependencies (numpy, Pillow). Ground measurements use its
Catmull-Rom preview evaluator, not GeckoLib or terrain collision. They are probes,
not a certificate of visual quality. Only --out receives files.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
MODELGEN = ROOT / "tools/modelgen"
sys.path[:0] = [str(MODELGEN), str(MODELGEN / "species")]
from build_all import ALL, clean_anim  # noqa: E402
from pybench import Rig, anim_json, geo_json, pose_at, render  # noqa: E402

ASSETS = ROOT / "common/src/main/resources/assets/terrassic"
HIDDEN = ("saddle", "female_display")
REPRESENTATIVES = ("tyrannosaurus", "triceratops", "argentinosaurus",
                   "velociraptor", "pteranodon", "mosasaurus")


def points(rig, pose):
    return np.array([w for _, _, corners, _ in rig.cube_faces(pose, hidden=HIDDEN)
                     for _, w in corners.values()])


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(name):
    spec = importlib.import_module(name).build().spec()
    rig = Rig(spec)
    animations = {a["name"].rsplit(".", 1)[1]: a for a in spec["animations"]}
    exported = ASSETS / "animations/entity" / f"{name}.animation.json"
    current = json.loads(exported.read_text())
    geometry = json.loads((ASSETS / "geo/entity" / f"{name}.geo.json").read_text())
    # Bounds are metadata; compare every bone/cube/UV used for the preview.
    geo_match = (geo_json(spec, [0, 0, 0], [0, 0, 0])["minecraft:geometry"][0]["bones"]
                 == geometry["minecraft:geometry"][0]["bones"])
    probes = {}
    for clip in ("sit", "knocked_out", "wake"):
        a = animations.get(clip)
        if not a:
            continue
        count = 37 if clip == "wake" else 9
        times = np.linspace(0, a["length"], count)
        lows = [float(points(rig, pose_at(a, float(t)))[:, 1].min()) for t in times]
        first, last = pose_at(a, 0), pose_at(a, a["length"])
        seam = max((abs(x - y) for bone in first for i in range(3)
                    for x, y in zip(first[bone][i], last[bone][i])), default=0)
        probes[clip] = {"length_s": a["length"], "samples": count,
                        "min_y_px": round(min(lows), 3), "max_of_min_y_px": round(max(lows), 3),
                        "worst_time_s": round(float(times[int(np.argmin(lows))]), 3),
                        "loop": a["loop"], "endpoint_component_delta": round(seam, 4)}
    ko = animations.get("knocked_out", {})
    dynamic = []
    for bone, tracks in ko.get("bones", {}).items():
        for channel, keys in tracks.items():
            if len({tuple(k[1:]) for k in keys}) > 1:
                dynamic.append(f"{bone}.{channel}")
    overlaps = {}
    for action in ("attack", "wake", "eat", "roar"):
        if action in animations and "walk" in animations:
            overlaps[action] = sorted(set(animations[action]["bones"]) & set(animations["walk"]["bones"]))
    return spec, {"species": name, "clips": sorted(animations),
                  "source_matches_export": clean_anim(json.dumps(anim_json(spec))) == current,
                  "geometry_matches_export": geo_match,
                  "knocked_out_dynamic_tracks": dynamic, "ground_probes": probes,
                  "action_walk_shared_bones": overlaps}


def illustrations(specs, rows, out):
    # Existing texture UVs must match the source geometry before rendering.
    cell, row_h = 280, 255
    sheet = Image.new("RGB", (cell * 4, row_h * len(REPRESENTATIVES)), "white")
    draw = ImageDraw.Draw(sheet)
    for row, name in enumerate(REPRESENTATIVES):
        spec = specs[name]
        rig = Rig(spec)
        tex = Image.open(ASSETS / "textures/entity" / f"{name}_male.png").convert("RGBA")
        anims = {a["name"].rsplit(".", 1)[1]: a for a in spec["animations"]}
        result = next(r for r in rows if r["species"] == name)
        worst = result["ground_probes"]["wake"]["worst_time_s"]
        frames = [("sit", 0), ("knocked_out", 0), ("wake", worst), ("wake", anims["wake"]["length"])]
        cloud = np.concatenate([points(rig, pose_at(anims[clip], t)) for clip, t in frames]
                               + [points(rig, pose_at(anims["wake"], float(t)))
                                  for t in np.linspace(0, anims["wake"]["length"], 31)])
        low, high = cloud.min(0), cloud.max(0)
        centre = (low + high) / 2
        direction = np.array([1.8, .6, -1.8]); direction /= np.linalg.norm(direction)
        forward = -direction
        right = np.cross(forward, [0, 1, 0]); right /= np.linalg.norm(right)
        up = np.cross(right, forward)
        local = cloud - centre
        depth = local @ forward
        f = 1.45 / np.tan(np.radians(40) / 2)
        distance = max(np.max(np.abs(local @ right) * f * (row_h - 38) / cell - depth),
                       np.max(np.abs(local @ up) * f - depth)) * 1.16
        cam = {"position": (centre + direction * distance).tolist(),
               "target": centre.tolist(), "fov": 40}
        for col, (clip, t) in enumerate(frames):
            pose = pose_at(anims[clip], t)
            img = render(rig, tex, cam, size=(cell, row_h - 38), pose=pose, hidden=HIDDEN)
            sheet.paste(img.convert("RGB"), (col * cell, row * row_h + 38))
            y = points(rig, pose)[:, 1].min()
            draw.text((col * cell + 6, row * row_h + 4), f"{name} | {clip} {t:.2f}s", fill="black")
            draw.text((col * cell + 6, row * row_h + 19), f"min y: {y:.2f} px (ground = 0)", fill="black")
        if name == "tyrannosaurus":
            gif = []
            # Shared camera: no auto-centring that could hide root translation.
            for t in np.linspace(0, anims["wake"]["length"], 31):
                pose = pose_at(anims["wake"], float(t))
                img = render(rig, tex, cam, size=(560, 400), pose=pose, hidden=HIDDEN).convert("RGB")
                ImageDraw.Draw(img).text((8, 8), f"CURRENT wake | {t:.2f}s | source preview", fill="black")
                gif.append(img)
            gif[0].save(out / "tyrannosaurus_wake_atual.gif", save_all=True,
                        append_images=gif[1:], duration=60, loop=0)
    sheet.save(out / "poses_atuais.png")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--out", type=Path, default=ROOT / "art/estudos/animacoes/v1")
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    # Fingerprint inputs before and after; importing/building must not change assets.
    sources = sorted([*MODELGEN.rglob("*.py"), * (ASSETS / "animations/entity").glob("*.json"),
                      * (ASSETS / "geo/entity").glob("*.json"),
                      * (ASSETS / "textures/entity").glob("*.png"),
                      * (ROOT / "common/src/main/java/com/terrassic/entity").rglob("*.java"),
                      * (ROOT / "common/src/main/java/com/terrassic/client").rglob("*.java")])
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in sources}
    rows, specs = [], {}
    for name in ALL:
        spec, row = audit(name)
        specs[name] = spec
        rows.append(row)
        print(name, "export=", row["source_matches_export"], flush=True)
    if args.render:
        if any(not r["source_matches_export"] or not r["geometry_matches_export"] for r in rows):
            raise RuntimeError("Source/export mismatch: resolve before drawing source previews")
        illustrations(specs, rows, out)
    assert hashes == {str(p.relative_to(ROOT)): digest(p) for p in sources}, "Inputs changed during audit"
    report = {"base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "method": "modelgen sources, flat y=0, Catmull-Rom preview, male, no saddle; not game validation",
              "species_count": len(rows), "sources_unchanged": True,
              "source_hashes": hashes, "species": rows}
    (out / "auditoria.json").write_text(json.dumps(report, indent=2) + "\n")
    counts = {clip: sum(clip in r["clips"] for r in rows)
              for clip in ("sit", "knocked_out", "wake", "sleep", "death", "dead", "lie_down", "stand_up", "knockout")}
    print(json.dumps({"coverage": counts, "matches": sum(r["source_matches_export"] for r in rows)}, indent=2))


if __name__ == "__main__":
    main()
