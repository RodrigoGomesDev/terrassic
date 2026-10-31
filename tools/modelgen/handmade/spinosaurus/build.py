"""
Builds the Spinosaurus into the mod. Fourth hand-made rig of the T. rex standard and the first one built on the shared
engine (handmade/_engine) and the big-theropod body plan (_engine/plans/theropod.py): 73 designed cubes with per-face
UV, a 256 x 256 skin drawn by form for male and female, the sail and the tail paddle as 1 px panels with a cut-out
outline, 29 animations (26 from the template, 4 of its own: fish, display, swipe, swim). Rodrigo approved the look
on 31/10 (03:44Z). Writes:

  common/.../geo/entity/spinosaurus.geo.json
  common/.../animations/entity/spinosaurus.animation.json
  common/.../textures/entity/spinosaurus_male.png, spinosaurus_female.png
  art/build_report.json (its row; gen_species reads the bounds)

usage:  python3 -B tools/modelgen/handmade/spinosaurus/build.py      (about 2 min: the legs use IK on every frame)

The build stops (exit 1) when the QA fails: coplanar faces, pixel bugs (stretched texels, holes, stray dots on the
cut-outs, sub-pixel cubes) or a standing pose off the ground, all measured on the exported files.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "_engine")
sys.path[:0] = [HERE, ENGINE, os.path.join(ENGINE, "plans")]
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "spritegen"))

import geo  # noqa: E402
import proto as P  # noqa: E402
import qa  # noqa: E402
import spino  # noqa: E402
import spinoanims as A  # noqa: E402
from anim2 import bake, to_geckolib  # noqa: E402
from jsongif import pose_at  # noqa: E402
from sprites import save_png  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
REPORT = os.path.join(ROOT, "art", "build_report.json")
FPS = 20
EVERY_FRAME = ("walk", "run", "stalk", "threat", "beg", "wake", "wake_sleep", "death", "hurt", "attack_quick", "fish", "swipe")
LINEAR = ("threat", "wake", "wake_sleep", "death", "hurt", "attack_quick", "swipe")
# baked at 40 fps: at 20 the run's foot (lift-off) and the death roll swept up to 0.74 px into the ground between two keyframes
FPS_OF = {"run": 40, "death": 40}


def main():
    m = spino.build()
    qa.single_face_planes(m)
    left = qa.separate_coplanar(m)
    P.pack(m, 256)
    geo_path = os.path.join(ASSETS, "geo", "entity", "spinosaurus.geo.json")
    with open(geo_path, "w") as f:
        json.dump(P.geo_json(m), f, indent=1)
    bugs = []
    for sex in ("male", "female"):
        tex = spino.paint_sex(m, sex)
        bugs += [(sex,) + b for b in qa.pixel_bugs(m, tex)]
        save_png(tex, os.path.join(ASSETS, "textures", "entity", f"spinosaurus_{sex}.png"))

    anims = {}
    for name, (fn, length, loop, _cat, _when) in A.ANIMS.items():
        fps = FPS_OF.get(name, FPS)
        anims[f"animation.spinosaurus.{name}"] = to_geckolib(bake(fn, length, fps), length, fps, loop,
                                                             every=1 if name in EVERY_FRAME else 2,
                                                             lerp="linear" if name in LINEAR else "catmullrom")
        print(name, flush=True)
    anim_path = os.path.join(ASSETS, "animations", "entity", "spinosaurus.animation.json")
    with open(anim_path, "w") as f:
        json.dump({"format_version": "1.8.0", "animations": anims}, f, indent=1)

    # ground, read back from the exported files the way GeckoLib plays them
    spec = geo.load_geo(geo_path)
    ground = []
    for key, an in anims.items():
        n = key.split(".")[-1]; L = an["animation_length"]; N = max(2, int(round(L * 40)))   # between the keyframes too
        lows = [min(q[:, 1].min() for _c, q in geo.cube_points(spec, pose_at(an, L * i / N))) for i in range(N + 1)]
        if n != "swim" and (min(lows) < -0.3 or (n in A.STANDING and max(lows) > 0.3)):
            ground.append((n, round(min(lows), 2), round(max(lows), 2)))

    pts = [p for _c, q in geo.cube_points(spec) for p in q]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    report = {}
    if os.path.exists(REPORT):
        with open(REPORT) as f:
            report = json.load(f)
    report["spinosaurus"] = {
        "bones": len(m.bones), "cubes": len(m.cubes), "texture": [m.tw, m.th],
        "bounds_px": [[float(v) for v in lo], [float(v) for v in hi]],
        "animations": list(anims), "render_scale": 0.5, "handmade": True,
    }
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=1)
    print("spinosaurus", json.dumps(report["spinosaurus"]["bounds_px"]))
    print("QA: coplanar", left, "| pixel bugs", len(bugs), "| off the ground", len(ground))
    for b in bugs + ground:
        print("  ", b)
    if left or bugs or ground:
        sys.exit(1)


if __name__ == "__main__":
    main()
