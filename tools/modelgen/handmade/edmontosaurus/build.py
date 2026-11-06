"""
Builds the Edmontosaurus into the mod (its own study, page "1.9: estudos do Quetzalcoatlus, do Edmontossauro e do
Dakotaraptor", approved by Rodrigo on 06/11/2026). A hand-made rig drawn at 20 px per metre (game scale 0.8, real
12 m): the long low head with the broadest bill, the nasal sacs (sac_l / sac_r) that swell in the bellow, the grown
male's fleshy comb (adult_comb under male_display), the segmented frill along the back and tail, its own traveller's
saddle, and its animations (edmontoanims.py). Writes the geo, the animations, the two skins and its row of
art/build_report.json; stops (exit 1) when the QA fails.

usage:  python3 -B tools/modelgen/handmade/edmontosaurus/build.py
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
import edmonto as TC  # noqa: E402
import edmontoanims as A  # noqa: E402
from anim2 import bake, to_geckolib  # noqa: E402
from jsongif import pose_at  # noqa: E402
from sprites import save_png  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
REPORT = os.path.join(ROOT, "art", "build_report.json")
FPS = 20
FPS_OF = {"death": 24, "run": 40, "attack": 40, "wake": 24, "wake_sleep": 30, "kick_back": 40, "body_shove": 40}
# every frame (no in-between keys) only where the catmull-rom between two keys swept a foot into the ground
EVERY_FRAME = ("walk", "run", "attack", "death", "wake", "turn_left", "turn_right", "walk_tired", "kick_back", "body_shove")
# long slow loops: a key every fourth frame is enough for the breathing
SLOW = ("idle", "sit", "sleep", "knocked_out")
LINEAR = ("hurt", "attack", "death", "wake", "wake_sleep", "kick_back", "body_shove")
# poses that stand on both feet (the off-the-ground check); swim floats by design; in the kick one foot is up
STANDING = ("idle", "vigilant", "call", "answer", "peep", "eat", "graze", "drink", "beg", "tame", "hurt", "bellow", "browse_high", "idle_tired", "body_shove")


def main():
    m = TC.build("male", saddle_on=True)
    qa.single_face_planes(m)
    left = qa.separate_coplanar(m)
    P.pack(m, TC.TEX_W)
    geo_path = os.path.join(ASSETS, "geo", "entity", "edmontosaurus.geo.json")
    with open(geo_path, "w") as f:
        json.dump(P.geo_json(m), f, indent=1)
    bugs = []
    for sex in ("male", "female"):
        tex = TC.paint_sex(m, sex)
        bugs += [(sex,) + b for b in qa.pixel_bugs(m, tex, cutout=qa.CUTOUT)]
        save_png(tex, os.path.join(ASSETS, "textures", "entity", f"edmontosaurus_{sex}.png"))

    anims = {}
    for name, (fn, length, loop, _cat, _when) in A.ANIMS.items():
        fps = FPS_OF.get(name, FPS)
        anims[f"animation.edmontosaurus.{name}"] = to_geckolib(bake(fn, length, fps), length, fps, loop,
                                                           every=1 if name in EVERY_FRAME else 4 if name in SLOW else 2,
                                                           lerp="linear" if name in LINEAR else "catmullrom")
        print(name, len(json.dumps(anims[f"animation.edmontosaurus.{name}"])) // 1024, "KB", flush=True)
    anim_path = os.path.join(ASSETS, "animations", "entity", "edmontosaurus.animation.json")
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
    report["edmontosaurus"] = {
        "bones": len(m.bones), "cubes": len(m.cubes), "texture": [m.tw, m.th],
        "bounds_px": [[float(v) for v in lo], [float(v) for v in hi]],
        "animations": list(anims), "render_scale": 0.8, "handmade": True,
    }
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=1)
    print("edmontosaurus", json.dumps(report["edmontosaurus"]["bounds_px"]), "animations", os.path.getsize(anim_path) // 1024, "KB")
    print("QA: coplanar", left, "| pixel bugs", len(bugs), "| off the ground", len(ground))
    for b in bugs + ground:
        print("  ", b)
    # the universal colour rule (docs/CORES.md): a colour of its own
    import colourcheck
    clash, old, near = colourcheck.check("edmontosaurus")
    print("colour: nearest", ", ".join(f"{o} {d:.1f}" for d, o in near), "| clashes with remade", clash, "| old ones to recolour", [o for _, o in old])
    if left or bugs or ground or clash:
        sys.exit(1)


if __name__ == "__main__":
    main()
