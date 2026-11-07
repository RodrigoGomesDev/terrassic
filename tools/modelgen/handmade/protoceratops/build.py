"""
Builds the Protoceratops into the mod. The third species made under the one-dino-at-a-time rule and the first small
one (its own study, page "Protoceratops: estudo e modelo, passo a passo"): a hand-made rig drawn at 48 px per metre
(game scale 1/3, real 1.9 m), per-face UV on a 128 x 128 skin for male and female in the "penhasco" scheme, no saddle
(not rideable), and 26 animations of its own (protoanims.py), the first quadruped gait of the hand-made rigs. Writes:

  common/.../geo/entity/protoceratops.geo.json
  common/.../animations/entity/protoceratops.animation.json
  common/.../textures/entity/protoceratops_male.png, protoceratops_female.png
  art/build_report.json (its row; gen_species reads the bounds)

usage:  python3 -B tools/modelgen/handmade/protoceratops/build.py

The animation file is kept small on purpose (the Carnotaurus and Giganotosaurus files passed 6 MB): 20 fps, a keyframe
every other frame with catmull-rom in between, every frame only where a foot would sink between two keyframes.
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
import protocera as PC  # noqa: E402
import protoanims as A  # noqa: E402
from anim2 import bake, to_geckolib  # noqa: E402
from jsongif import pose_at  # noqa: E402
from sprites import save_png  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
REPORT = os.path.join(ROOT, "art", "build_report.json")
FPS = 20
# baked at 40 fps: the fast ones swept a foot into the ground between two frames at 20
FPS_OF = {"run_biped": 40, "death": 40, "run": 40}     # the trot: 11 frames a stride at 20 fps
# every frame (no in-between keys) only where the catmull-rom between two keys swept a foot into the ground
EVERY_FRAME = ("run", "run_biped", "attack", "death", "dig", "scrape_rest", "wake",
               # 06/11, protoflow.py: the stepping loops (short legs, quick steps), the snaps of the fight, the shiver
               "walk", "turn_left", "turn_right", "strafe_left", "strafe_right", "walk_tired", "guard", "frill_shove", "feint",
               "block", "recoil", "submit", "lie_down", "get_up", "freeze", "hurt",
               # 06/11, the epic duel (protofight.py): the committed moves, every frame
               "lunge", "parry", "stagger")
# long slow loops: a key every fourth frame is enough for the breathing
SLOW = ("sit", "sleep", "huddle", "knocked_out")     # the idle left this list: its sniff is quicker than four frames
LINEAR = ("hurt", "attack", "run_biped", "death", "frill_shove", "block", "recoil")
# poses that stand on all four feet (the off-the-ground check); swim floats by design, the baby run is on two
STANDING = ("idle", "eat", "graze", "beg", "tame", "hurt", "attack", "bite_hold", "shove", "frill_show", "sail_sway",
            "freeze", "sand_shake", "guard", "strafe_left", "strafe_right", "turn_left", "turn_right", "frill_shove", "feint",
            "block", "recoil", "submit", "idle_tired", "walk_tired", "lunge", "parry", "stagger")


def main():
    m = PC.build("male")
    qa.single_face_planes(m)
    left = qa.separate_coplanar(m)
    P.pack(m, PC.TEX_W)
    geo_path = os.path.join(ASSETS, "geo", "entity", "protoceratops.geo.json")
    with open(geo_path, "w") as f:
        json.dump(P.geo_json(m), f, indent=1)
    bugs = []
    for sex in ("male", "female"):
        tex = PC.paint_sex(m, sex)
        bugs += [(sex,) + b for b in qa.pixel_bugs(m, tex)]
        save_png(tex, os.path.join(ASSETS, "textures", "entity", f"protoceratops_{sex}.png"))

    anims = {}
    for name, (fn, length, loop, _cat, _when) in A.ANIMS.items():
        fps = FPS_OF.get(name, FPS)
        anims[f"animation.protoceratops.{name}"] = to_geckolib(bake(fn, length, fps), length, fps, loop,
                                                             every=1 if name in EVERY_FRAME else 4 if name in SLOW else 2,
                                                             lerp="linear" if name in LINEAR else "catmullrom")
        print(name, len(json.dumps(anims[f"animation.protoceratops.{name}"])) // 1024, "KB", flush=True)
    anim_path = os.path.join(ASSETS, "animations", "entity", "protoceratops.animation.json")
    with open(anim_path, "w") as f:
        json.dump({"format_version": "1.8.0", "animations": anims}, f, separators=(",", ":"))

    # ground, read back from the exported files (swim floats by design), between the keyframes too; the female's
    # bump is hidden on the male and the other way round, the teeth do not count
    spec = geo.load_geo(geo_path)
    skip = {c["name"] for c in m.cubes if c["mat"] in ("teeth",) or c["bone"] == "female_display"}
    ground = []
    for key, an in anims.items():
        n = key.split(".")[-1]; L = an["animation_length"]; N = max(2, int(round(L * 40)))
        lows = [min(q[:, 1].min() for c, q in geo.cube_points(spec, pose_at(an, L * i / N)) if c["name"] not in skip)
                for i in range(N + 1)]
        if n not in ("swim",) and (min(lows) < -0.3 or (n in STANDING and max(lows) > 0.3)):
            ground.append((n, round(min(lows), 2), round(max(lows), 2)))

    pts = [p for c, q in geo.cube_points(spec) if c["name"] not in skip for p in q]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    report = {}
    if os.path.exists(REPORT):
        with open(REPORT) as f:
            report = json.load(f)
    report["protoceratops"] = {
        "bones": len(m.bones), "cubes": len(m.cubes), "texture": [m.tw, m.th],
        "bounds_px": [[float(v) for v in lo], [float(v) for v in hi]],
        "animations": list(anims), "render_scale": 0.3333, "handmade": True,
    }
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=1)
    print("protoceratops", json.dumps(report["protoceratops"]["bounds_px"]), "animations", os.path.getsize(anim_path) // 1024, "KB")
    print("QA: coplanar", left, "| pixel bugs", len(bugs), "| off the ground", len(ground))
    for b in bugs + ground:
        print("  ", b)
    # the universal colour rule (docs/CORES.md): a colour of its own
    import colourcheck
    clash, old, near = colourcheck.check("protoceratops")
    print("colour: nearest", ", ".join(f"{o} {d:.1f}" for d, o in near), "| clashes with remade", clash, "| old ones to recolour", [o for _, o in old])
    if left or bugs or ground or clash:
        sys.exit(1)


if __name__ == "__main__":
    main()
