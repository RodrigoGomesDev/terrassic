"""
Builds the Mosasaurus into the mod: the sixth and last of the remakes of the 1.5 package, under the one-dino-at-a-time
rule (its own study, page "Mosassauro 1.5", 02/11/2026), and the first animal of the sea to be remade. A hand-made rig
drawn at 16 px per 17/12 m (game scale 0.706, real 12 m), per-face UV on a 256-wide skin for male and female
("garrafa": bottle-green back over an ivory belly, countershaded with a sharp wavering line; the male with healed bite scars on the
head), the double-hinged jaw (jaw / jaw_front), the throat on its own bone, the fluke on its own bone, its own diving
harness (shown when saddled) and 23 animations of its own (mosaanims.py). Writes:

  common/.../geo/entity/mosasaurus.geo.json
  common/.../animations/entity/mosasaurus.animation.json
  common/.../textures/entity/mosasaurus_male.png, mosasaurus_female.png
  art/build_report.json (its row; gen_species reads the bounds)

usage:  python3 -B tools/modelgen/handmade/mosasaurus/build.py

The animation file is kept small: 20 fps, a keyframe every other frame with catmull-rom in between, every fourth
frame on the long slow loops. The build stops (exit 1) when the QA fails: coplanar faces, pixel bugs, a pose that
lies on the ground (stranded, asleep on the bottom) going through it, or a colour too close to another remade species
(males AND females).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "_engine")
sys.path[:0] = [HERE, ENGINE]
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "spritegen"))

import geo  # noqa: E402
import proto as P  # noqa: E402
import qa  # noqa: E402
import mosa as MS  # noqa: E402
import mosaanims as A  # noqa: E402
from anim2 import bake, to_geckolib  # noqa: E402
from jsongif import pose_at  # noqa: E402
from sprites import save_png  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
REPORT = os.path.join(ROOT, "art", "build_report.json")
FPS = 20
FPS_OF = {"attack": 30, "hurt": 30, "run": 30, "shake": 30}
SLOW = ("idle", "sit", "sleep", "knocked_out", "walk")
LINEAR = ("hurt", "attack", "death")
# poses that lie on the ground (on land, or on the sea floor): nothing may go through it
ON_GROUND = ("stranded", "sleep")
CUTOUT = ("teeth", "teeth_lo")


def main():
    m = MS.build("male", saddle_on=True)
    qa.single_face_planes(m)
    left = qa.separate_coplanar(m)
    P.pack(m, MS.TEX_W)
    geo_path = os.path.join(ASSETS, "geo", "entity", "mosasaurus.geo.json")
    with open(geo_path, "w") as f:
        json.dump(P.geo_json(m), f, indent=1)
    bugs = []
    for sex in ("male", "female"):
        tex = MS.paint_sex(m, sex)
        bugs += [(sex,) + b for b in qa.pixel_bugs(m, tex, cutout=CUTOUT)]
        save_png(tex, os.path.join(ASSETS, "textures", "entity", f"mosasaurus_{sex}.png"))

    anims = {}
    for name, (fn, length, loop, _cat, _when) in A.ANIMS.items():
        fps = FPS_OF.get(name, FPS)
        anims[f"animation.mosasaurus.{name}"] = to_geckolib(bake(fn, length, fps), length, fps, loop,
                                                          every=4 if name in SLOW else 2,
                                                          lerp="linear" if name in LINEAR else "catmullrom")
    anim_path = os.path.join(ASSETS, "animations", "entity", "mosasaurus.animation.json")
    with open(anim_path, "w") as f:
        json.dump({"format_version": "1.8.0", "animations": anims}, f, separators=(",", ":"))

    # the poses on the ground, read back from the exported files, between the keyframes too
    spec = geo.load_geo(geo_path)
    skip = {"saddle"}
    ground = []
    for key, an in anims.items():
        n = key.split(".")[-1]
        if n not in ON_GROUND:
            continue
        L = an["animation_length"]; N = max(2, int(round(L * 40)))
        lows = [min(q[:, 1].min() for c, q in geo.cube_points(spec, pose_at(an, L * i / N)) if c["bone"] not in skip)
                for i in range(N + 1)]
        if min(lows) < -0.3:
            ground.append((n, round(min(lows), 2)))

    pts = [p for c, q in geo.cube_points(spec) if c["bone"] not in skip for p in q]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    report = {}
    if os.path.exists(REPORT):
        with open(REPORT) as f:
            report = json.load(f)
    report["mosasaurus"] = {
        "bones": len(m.bones), "cubes": len(m.cubes), "texture": [m.tw, m.th],
        "bounds_px": [[float(v) for v in lo], [float(v) for v in hi]],
        "animations": list(anims), "render_scale": 0.706, "handmade": True,
    }
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=1)
    print("mosasaurus", json.dumps(report["mosasaurus"]["bounds_px"]), "animations", os.path.getsize(anim_path) // 1024, "KB")
    print("QA: coplanar", left, "| pixel bugs", len(bugs), "| through the ground", len(ground))
    for b in bugs + ground:
        print("  ", b)
    # the universal colour rule (docs/CORES.md): a colour of its own, the male and the female
    import colourcheck
    clash = []
    for sex in ("male", "female"):
        e, old, near = colourcheck.check("mosasaurus", sex=sex)
        clash += e
        print(f"colour ({sex}): nearest", ", ".join(f"{o} {d:.1f}" for d, o in near), "| clashes with remade", e,
              "| old ones to recolour", [o for _, o in old])
    if left or bugs or ground or clash:
        sys.exit(1)


if __name__ == "__main__":
    main()
