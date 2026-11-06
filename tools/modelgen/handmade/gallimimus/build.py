"""
Builds the Gallimimus into the mod: the second of the six remakes of the 1.5 package, under the one-dino-at-a-time rule
(its own study, page "Gallimimus: estudo e modelo", 02/11/2026). A hand-made rig drawn at 32 px per metre (game scale
0.5, real 6 m), per-face UV on a 256-wide skin for male and female (the male "grafite-azulado" blue-black with chalk
underparts, the female "canela"), the adults' wing fans on their own bones (adult_l / adult_r, hidden on the young),
its own riding pad (shown when saddled) and 24 animations of its own (gallianims.py). Writes:

  common/.../geo/entity/gallimimus.geo.json
  common/.../animations/entity/gallimimus.animation.json
  common/.../textures/entity/gallimimus_male.png, gallimimus_female.png
  art/build_report.json (its row; gen_species reads the bounds)

usage:  python3 -B tools/modelgen/handmade/gallimimus/build.py

The animation file is kept small: 20 fps, a keyframe every other frame with catmull-rom in between, every frame only
where a foot would sink between two keys, every fourth frame on the long slow loops. The build stops (exit 1) when the
QA fails: coplanar faces, pixel bugs, a standing pose off the ground or a pose through it, or a colour too close to
another remade species.
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
import galli as TC  # noqa: E402
import gallianims as A  # noqa: E402
from anim2 import bake, to_geckolib  # noqa: E402
from jsongif import pose_at  # noqa: E402
from sprites import save_png  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
REPORT = os.path.join(ROOT, "art", "build_report.json")
FPS = 20
FPS_OF = {"death": 40, "run": 40, "jink": 40, "attack": 40, "wake": 40, "wake_sleep": 40, "kick_back": 40, "lie_down": 40, "get_up": 40}
# every frame (no in-between keys) only where the catmull-rom between two keys swept a foot into the ground
EVERY_FRAME = ("walk", "run", "jink", "attack", "death", "wake", "wake_sleep", "graze", "turn_left", "turn_right",
               "walk_tired", "kick_back", "lie_down", "get_up")
# long slow loops: a key every fourth frame is enough for the breathing
SLOW = ("idle", "sit", "sleep", "knocked_out", "brood")
LINEAR = ("hurt", "attack", "death", "jink", "wake", "wake_sleep", "kick_back")
# poses that stand on both feet (the off-the-ground check); swim floats by design; in the kick one foot is up
STANDING = ("idle", "sentinel", "preen", "wing_display", "eat", "grit", "sift", "browse", "beg", "tame", "hurt", "idle_tired")


def main():
    m = TC.build(saddle_on=True)
    qa.single_face_planes(m)
    left = qa.separate_coplanar(m)
    P.pack(m, TC.TEX_W)
    geo_path = os.path.join(ASSETS, "geo", "entity", "gallimimus.geo.json")
    with open(geo_path, "w") as f:
        json.dump(P.geo_json(m), f, indent=1)
    bugs = []
    for sex in ("male", "female"):
        tex = TC.paint_sex(m, sex)
        bugs += [(sex,) + b for b in qa.pixel_bugs(m, tex, cutout=qa.CUTOUT + ("plume",))]
        save_png(tex, os.path.join(ASSETS, "textures", "entity", f"gallimimus_{sex}.png"))

    anims = {}
    for name, (fn, length, loop, _cat, _when) in A.ANIMS.items():
        fps = FPS_OF.get(name, FPS)
        anims[f"animation.gallimimus.{name}"] = to_geckolib(bake(fn, length, fps), length, fps, loop,
                                                           every=1 if name in EVERY_FRAME else 4 if name in SLOW else 2,
                                                           lerp="linear" if name in LINEAR else "catmullrom")
        print(name, len(json.dumps(anims[f"animation.gallimimus.{name}"])) // 1024, "KB", flush=True)
    anim_path = os.path.join(ASSETS, "animations", "entity", "gallimimus.animation.json")
    with open(anim_path, "w") as f:
        json.dump({"format_version": "1.8.0", "animations": anims}, f, separators=(",", ":"))

    # ground, read back from the exported files (swim floats by design), between the keyframes too; the saddle is
    # hidden unless saddled and never reaches the ground standing
    spec = geo.load_geo(geo_path)
    skip = {"saddle"}
    ground = []
    for key, an in anims.items():
        n = key.split(".")[-1]; L = an["animation_length"]; N = max(2, int(round(L * 40)))
        lows = [min(q[:, 1].min() for c, q in geo.cube_points(spec, pose_at(an, L * i / N)) if c["bone"] not in skip)
                for i in range(N + 1)]
        if n not in ("swim",) and (min(lows) < -0.3 or (n in STANDING and max(lows) > 0.3)):
            ground.append((n, round(min(lows), 2), round(max(lows), 2)))

    pts = [p for c, q in geo.cube_points(spec) if c["bone"] not in skip for p in q]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    report = {}
    if os.path.exists(REPORT):
        with open(REPORT) as f:
            report = json.load(f)
    report["gallimimus"] = {
        "bones": len(m.bones), "cubes": len(m.cubes), "texture": [m.tw, m.th],
        "bounds_px": [[float(v) for v in lo], [float(v) for v in hi]],
        "animations": list(anims), "render_scale": 0.5, "handmade": True,
    }
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=1)
    print("gallimimus", json.dumps(report["gallimimus"]["bounds_px"]), "animations", os.path.getsize(anim_path) // 1024, "KB")
    print("QA: coplanar", left, "| pixel bugs", len(bugs), "| off the ground", len(ground))
    for b in bugs + ground:
        print("  ", b)
    # the universal colour rule (docs/CORES.md): a colour of its own
    import colourcheck
    clash, old, near = colourcheck.check("gallimimus")
    print("colour: nearest", ", ".join(f"{o} {d:.1f}" for d, o in near), "| clashes with remade", clash, "| old ones to recolour", [o for _, o in old])
    if left or bugs or ground or clash:
        sys.exit(1)


if __name__ == "__main__":
    main()
