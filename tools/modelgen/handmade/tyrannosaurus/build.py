"""
Builds the T. rex into the mod. It is a hand-made rig (the new standard of the 29/10 model study), not an archetype
of species/: 78 designed cubes with per-face UV, a 256 x 256 skin drawn by form, 28 animations baked from poses with
planted feet (leg IK). Writes:

  common/.../geo/entity/tyrannosaurus.geo.json
  common/.../animations/entity/tyrannosaurus.animation.json
  common/.../textures/entity/tyrannosaurus_male.png, tyrannosaurus_female.png
  common/.../textures/particle/roar_wave_0..7.png + particles/roar_wave.json   (the loud roar's burst)
  art/build_report.json (its row: bones, cubes, texture, bounds, animations; gen_species reads the bounds)

usage:  python3 -B tools/modelgen/handmade/tyrannosaurus/build.py      (or build_all.py tyrannosaurus)

GeckoLib note: it draws the east/west faces with u reversed from the old preview renderer, so proto.geo_json flips u
on the side faces and geo.load_geo reads the files the way the game draws them. Preview from the exported file.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "spritegen"))

import geo  # noqa: E402
import proto as P  # noqa: E402
import rex2  # noqa: E402
import rexanims as A  # noqa: E402
import roar_wave  # noqa: E402
from anim2 import bake, to_geckolib  # noqa: E402
from sprites import save_png  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
REPORT = os.path.join(ROOT, "art", "build_report.json")
FPS = 20
# keyframe every frame for the fast or jolting ones, linear where a curve would overshoot a hit
EVERY_FRAME = ("walk", "run", "stalk", "stomp", "threat", "beg", "wake", "wake_sleep", "death", "hurt", "attack_quick")
LINEAR = ("stomp", "threat", "wake", "wake_sleep", "death", "hurt", "attack_quick")


def main():
    m = rex2.build()
    P.pack(m, 256)
    geo_json = P.geo_json(m)
    with open(os.path.join(ASSETS, "geo", "entity", "tyrannosaurus.geo.json"), "w") as f:
        json.dump(geo_json, f, indent=1)
    for sex in ("male", "female"):
        save_png(rex2.paint_sex(m, sex), os.path.join(ASSETS, "textures", "entity", f"tyrannosaurus_{sex}.png"))

    anims = {}
    for name, (fn, length, loop, _cat, _when) in A.ANIMS.items():
        frames = bake(fn, length, FPS)
        anims[f"animation.tyrannosaurus.{name}"] = to_geckolib(frames, length, FPS, loop, every=1 if name in EVERY_FRAME else 2,
                                                               lerp="linear" if name in LINEAR else "catmullrom")
        print(name, flush=True)
    with open(os.path.join(ASSETS, "animations", "entity", "tyrannosaurus.animation.json"), "w") as f:
        json.dump({"format_version": "1.8.0", "animations": anims}, f, indent=1)

    for k in range(roar_wave.N):
        save_png(roar_wave.frame(k), os.path.join(ASSETS, "textures", "particle", f"roar_wave_{k}.png"))
    os.makedirs(os.path.join(ASSETS, "particles"), exist_ok=True)
    with open(os.path.join(ASSETS, "particles", "roar_wave.json"), "w") as f:
        json.dump({"textures": [f"terrassic:roar_wave_{k}" for k in range(roar_wave.N)]}, f, indent=1)

    spec = geo.load_geo(os.path.join(ASSETS, "geo", "entity", "tyrannosaurus.geo.json"))
    pts = [p for _c, q in geo.cube_points(spec) for p in q]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    report = {}
    if os.path.exists(REPORT):
        with open(REPORT) as f:
            report = json.load(f)
    report["tyrannosaurus"] = {
        "bones": len(geo_json["minecraft:geometry"][0]["bones"]), "cubes": len(m.cubes),
        "texture": [m.tw, m.th], "bounds_px": [[float(v) for v in lo], [float(v) for v in hi]],
        "animations": list(anims), "render_scale": 0.5, "handmade": True,
    }
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=1)
    print("tyrannosaurus", json.dumps(report["tyrannosaurus"]["bounds_px"]))


if __name__ == "__main__":
    main()
