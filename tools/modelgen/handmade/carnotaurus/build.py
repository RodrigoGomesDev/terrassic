"""
Builds the Carnotaurus into the mod. The first species made under the one-dino-at-a-time rule (its own study, page
"Carnotaurus: estudo e modelo, passo a passo"): a hand-made rig drawn at 24 px per metre (game scale 0.667), per-face
UV on a 256 x 128 skin for male and female in the "ferrugem" scheme, its own racing saddle, and 34 animations of its
own (carnoanims.py: the 26 every big theropod needs and 7 that are only its: lock_on, skid_turn, brake, shove, hook,
horn_rub, arm_twitch; skid_turn_r is skid_turn mirrored, for turns to the right). Rodrigo approved the model and the
first animations on 01/11. Writes:

  common/.../geo/entity/carnotaurus.geo.json
  common/.../animations/entity/carnotaurus.animation.json
  common/.../textures/entity/carnotaurus_male.png, carnotaurus_female.png
  art/build_report.json (its row; gen_species reads the bounds)

usage:  python3 -B tools/modelgen/handmade/carnotaurus/build.py

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
import carno  # noqa: E402
import carnoanims as A  # noqa: E402
from anim2 import bake, to_geckolib  # noqa: E402
from jsongif import pose_at  # noqa: E402
from sprites import save_png  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
REPORT = os.path.join(ROOT, "art", "build_report.json")
FPS = 20
EVERY_FRAME = ("walk", "run", "stalk", "threat", "beg", "wake", "wake_sleep", "death", "hurt", "attack_quick",
               "skid_turn", "skid_turn_r", "brake", "hook", "arm_twitch", "eat",
               # 06/11 (carnoflow.py): the tremors, the skips and the stepping loops would be smoothed away between keys
               "attack", "roar", "call", "shove", "guard", "strafe_left", "strafe_right", "turn_left", "turn_right",
               "feint", "block", "recoil", "submit", "walk_tired", "ram", "head_clash",
               # 06/11 (carnofight.py): the duel's committed moves
               "lunge", "parry", "stagger")
LINEAR = ("threat", "wake", "wake_sleep", "death", "hurt", "attack_quick", "hook", "arm_twitch", "brake")
# baked at 40 fps: at 20 the fast ones (the run's lift-off, the brake's plant, the bite's lunge, the rolls) swept a foot
# up to 1 px into the ground between two keyframes
FPS_OF = {"run": 40, "death": 40, "wake": 40, "wake_sleep": 40, "brake": 40, "attack": 40, "ram": 40, "head_clash": 40,
          "strafe_left": 40, "strafe_right": 40, "recoil": 40,
          "lunge": 40, "parry": 40, "stagger": 40}
SADDLE = ("hide", "fur", "strap", "iron")
# poses that stand on both feet (the off-the-ground check); swim floats by design
STANDING = ("idle", "sniff", "look_back", "shake", "yawn", "roar", "call", "attack", "attack_quick", "hurt", "eat",
            "drink", "tame", "beg", "lock_on", "arm_twitch", "hook", "horn_rub", "shove", "guard", "feint", "block",
            "idle_tired", "head_clash", "lunge", "parry", "stagger")


def main():
    m = carno.build(saddle_on=True)
    qa.single_face_planes(m)
    left = qa.separate_coplanar(m)
    P.pack(m, carno.TEX_W)
    geo_path = os.path.join(ASSETS, "geo", "entity", "carnotaurus.geo.json")
    with open(geo_path, "w") as f:
        json.dump(P.geo_json(m), f, indent=1)
    bugs = []
    for sex in ("male", "female"):
        tex = carno.paint_sex(m, sex)
        bugs += [(sex,) + b for b in qa.pixel_bugs(m, tex)]
        save_png(tex, os.path.join(ASSETS, "textures", "entity", f"carnotaurus_{sex}.png"))

    anims = {}
    for name, (fn, length, loop, _cat, _when) in A.ANIMS.items():
        fps = FPS_OF.get(name, FPS)
        anims[f"animation.carnotaurus.{name}"] = to_geckolib(bake(fn, length, fps), length, fps, loop,
                                                             every=1 if name in EVERY_FRAME else 2,
                                                             lerp="linear" if name in LINEAR else "catmullrom")
        print(name, flush=True)
    anim_path = os.path.join(ASSETS, "animations", "entity", "carnotaurus.animation.json")
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
    report["carnotaurus"] = {
        "bones": len(m.bones), "cubes": len(m.cubes), "texture": [m.tw, m.th],
        "bounds_px": [[float(v) for v in lo], [float(v) for v in hi]],
        "animations": list(anims), "render_scale": 0.667, "handmade": True,
    }
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=1)
    print("carnotaurus", json.dumps(report["carnotaurus"]["bounds_px"]))
    print("QA: coplanar", left, "| pixel bugs", len(bugs), "| off the ground", len(ground))
    for b in bugs + ground:
        print("  ", b)
    if left or bugs or ground:
        sys.exit(1)


if __name__ == "__main__":
    main()
