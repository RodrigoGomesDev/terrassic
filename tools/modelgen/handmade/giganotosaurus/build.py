"""
Builds the Giganotosaurus into the mod. The second species made under the one-dino-at-a-time rule (its own study,
page "Giganotosaurus: estudo e modelo, passo a passo"): a hand-made rig drawn at 24 px per metre (game scale 0.667,
real 12.5 m), per-face UV on a 256 x 256 skin for male and female in the "tubarao" scheme, its own saddle (a
Patagonian recado), and 35 animations of its own (gigaanims.py; the list Rodrigo approved on 01/11). Writes:

  common/.../geo/entity/giganotosaurus.geo.json
  common/.../animations/entity/giganotosaurus.animation.json
  common/.../textures/entity/giganotosaurus_male.png, giganotosaurus_female.png
  art/build_report.json (its row; gen_species reads the bounds)

usage:  python3 -B tools/modelgen/handmade/giganotosaurus/build.py

The build stops (exit 1) when the QA fails: coplanar faces, pixel bugs, or a standing pose off the ground, all
measured on the exported files the way GeckoLib plays them.
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
import giga  # noqa: E402
import gigaanims as A  # noqa: E402
from anim2 import bake, to_geckolib  # noqa: E402
from jsongif import pose_at  # noqa: E402
from sprites import save_png  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
REPORT = os.path.join(ROOT, "art", "build_report.json")
FPS = 20
EVERY_FRAME = ("walk", "run", "stalk", "back_off", "circle", "beg", "wake", "wake_sleep", "death", "hurt",
               "attack_quick", "slash", "lunge", "rip", "stomp", "eye_aim")
LINEAR = ("wake", "wake_sleep", "death", "hurt", "attack_quick", "slash", "lunge", "stomp")
# baked at 40 fps: the fast ones swept a foot into the ground between two keyframes at 20
FPS_OF = {"walk": 40, "run": 40, "death": 40, "wake": 40, "wake_sleep": 40, "slash": 40, "lunge": 40, "stomp": 40, "rip": 40}
SADDLE = giga.SADDLE_MATS
# poses that stand on both feet (the off-the-ground check); swim floats by design
STANDING = ("idle", "sniff", "look_side", "eye_aim", "shake", "yawn", "roar", "call", "gape", "crest_show",
            "attack_quick", "hurt", "beg", "tame")


def main():
    m = giga.build(saddle_on=True)
    qa.single_face_planes(m)
    left = qa.separate_coplanar(m)
    P.pack(m, giga.TEX_W)
    geo_path = os.path.join(ASSETS, "geo", "entity", "giganotosaurus.geo.json")
    with open(geo_path, "w") as f:
        json.dump(P.geo_json(m), f, indent=1)
    bugs = []
    for sex in ("male", "female"):
        tex = giga.paint_sex(m, sex)
        bugs += [(sex,) + b for b in qa.pixel_bugs(m, tex)]
        save_png(tex, os.path.join(ASSETS, "textures", "entity", f"giganotosaurus_{sex}.png"))

    anims = {}
    for name, (fn, length, loop, _cat, _when) in A.ANIMS.items():
        fps = FPS_OF.get(name, FPS)
        anims[f"animation.giganotosaurus.{name}"] = to_geckolib(bake(fn, length, fps), length, fps, loop,
                                                             every=1 if name in EVERY_FRAME else 2,
                                                             lerp="linear" if name in LINEAR else "catmullrom")
        print(name, flush=True)
    anim_path = os.path.join(ASSETS, "animations", "entity", "giganotosaurus.animation.json")
    with open(anim_path, "w") as f:
        json.dump({"format_version": "1.8.0", "animations": anims}, f, indent=1)

    # ground, read back from the exported files (swim floats; drink dips the snout 1.7 px into the water by design), between the keyframes too; the saddle does not count (unsaddled
    # animals must not float) and neither do the teeth
    spec = geo.load_geo(geo_path)
    skip = {c["name"] for c in m.cubes if c["mat"] in SADDLE + ("teeth", "teeth_lo")}
    ground = []
    for key, an in anims.items():
        n = key.split(".")[-1]; L = an["animation_length"]; N = max(2, int(round(L * 40)))
        lows = [min(q[:, 1].min() for c, q in geo.cube_points(spec, pose_at(an, L * i / N)) if c["name"] not in skip)
                for i in range(N + 1)]
        if n not in ("swim", "drink") and (min(lows) < -0.3 or (n in STANDING and max(lows) > 0.3)):
            ground.append((n, round(min(lows), 2), round(max(lows), 2)))

    pts = [p for c, q in geo.cube_points(spec) if c["name"] not in skip for p in q]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    report = {}
    if os.path.exists(REPORT):
        with open(REPORT) as f:
            report = json.load(f)
    report["giganotosaurus"] = {
        "bones": len(m.bones), "cubes": len(m.cubes), "texture": [m.tw, m.th],
        "bounds_px": [[float(v) for v in lo], [float(v) for v in hi]],
        "animations": list(anims), "render_scale": 0.667, "handmade": True,
    }
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=1)
    print("giganotosaurus", json.dumps(report["giganotosaurus"]["bounds_px"]))
    print("QA: coplanar", left, "| pixel bugs", len(bugs), "| off the ground", len(ground))
    for b in bugs + ground:
        print("  ", b)
    if left or bugs or ground:
        sys.exit(1)


if __name__ == "__main__":
    main()
