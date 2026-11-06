"""
Builds the Pachycephalosaurus into the mod: the third of the six remakes of the 1.5 package, under the
one-dino-at-a-time rule (its own study, page "Paquicefalossauro: estudo e modelo", 02/11/2026). A hand-made rig drawn
at 32 px per metre (game scale 0.5, real 4.5 m), per-face UV on a 256-wide skin for male and female (the male "mel
listrado", honey with pale stripes and a bleached crown on the dome, the female a darker honey), the adult dome on its
own bones (adult_dome, adult_dome_male, adult_dome_female) and the young's spikes on theirs (young_spikes): the growth
series. No saddle (not rideable: the study says why). 23 animations of its own (pachyanims.py). Writes:

  common/.../geo/entity/pachycephalosaurus.geo.json
  common/.../animations/entity/pachycephalosaurus.animation.json
  common/.../textures/entity/pachycephalosaurus_male.png, pachycephalosaurus_female.png
  art/build_report.json (its row; gen_species reads the bounds)

usage:  python3 -B tools/modelgen/handmade/pachycephalosaurus/build.py

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
import pachy as TC  # noqa: E402
import pachyanims as A  # noqa: E402
from anim2 import bake, to_geckolib  # noqa: E402
from jsongif import pose_at  # noqa: E402
from sprites import save_png  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
REPORT = os.path.join(ROOT, "art", "build_report.json")
FPS = 20
FPS_OF = {"run": 40, "attack": 40, "flank_butt": 40}
# every frame (no in-between keys) only where the catmull-rom between two keys swept a foot into the ground
EVERY_FRAME = ("walk", "run", "attack", "death", "wake", "wake_sleep", "graze", "dome_clash", "hop_play",
               "turn_left", "turn_right", "walk_tired", "strafe_left", "strafe_right", "feint", "block", "recoil")
# long slow loops: a key every fourth frame is enough for the breathing
SLOW = ("idle", "sit", "sleep", "knocked_out")
LINEAR = ("hurt", "attack", "death", "dome_clash", "flank_butt", "wake", "wake_sleep", "block", "recoil")
# poses that stand on both feet (the off-the-ground check); swim floats by design; the young's hop leaves the ground
STANDING = ("idle", "dome_display", "eat", "sniff", "pluck", "beg", "tame", "hurt", "flank_butt", "idle_tired", "guard", "submit")
AIRBORNE = ("swim", "hop_play")


def main():
    m = TC.build()
    qa.single_face_planes(m)
    left = qa.separate_coplanar(m)
    P.pack(m, TC.TEX_W)
    geo_path = os.path.join(ASSETS, "geo", "entity", "pachycephalosaurus.geo.json")
    with open(geo_path, "w") as f:
        json.dump(P.geo_json(m), f, indent=1)
    bugs = []
    for sex in ("male", "female"):
        tex = TC.paint_sex(m, sex)
        bugs += [(sex,) + b for b in qa.pixel_bugs(m, tex, cutout=qa.CUTOUT + ("bristle",))]
        save_png(tex, os.path.join(ASSETS, "textures", "entity", f"pachycephalosaurus_{sex}.png"))

    anims = {}
    for name, (fn, length, loop, _cat, _when) in A.ANIMS.items():
        fps = FPS_OF.get(name, FPS)
        anims[f"animation.pachycephalosaurus.{name}"] = to_geckolib(bake(fn, length, fps), length, fps, loop,
                                                           every=1 if name in EVERY_FRAME else 4 if name in SLOW else 2,
                                                           lerp="linear" if name in LINEAR else "catmullrom")
        print(name, len(json.dumps(anims[f"animation.pachycephalosaurus.{name}"])) // 1024, "KB", flush=True)
    anim_path = os.path.join(ASSETS, "animations", "entity", "pachycephalosaurus.animation.json")
    with open(anim_path, "w") as f:
        json.dump({"format_version": "1.8.0", "animations": anims}, f, separators=(",", ":"))

    # ground, read back from the exported files, between the keyframes too; the young's spikes are hidden on adults
    # (and the baby is the same rig scaled down), so they do not count
    spec = geo.load_geo(geo_path)
    skip = {"young_spikes"}
    ground = []
    for key, an in anims.items():
        n = key.split(".")[-1]; L = an["animation_length"]; N = max(2, int(round(L * 40)))
        lows = [min(q[:, 1].min() for c, q in geo.cube_points(spec, pose_at(an, L * i / N)) if c["bone"] not in skip)
                for i in range(N + 1)]
        if n not in AIRBORNE and (min(lows) < -0.3 or (n in STANDING and max(lows) > 0.3)):
            ground.append((n, round(min(lows), 2), round(max(lows), 2)))

    pts = [p for c, q in geo.cube_points(spec) if c["bone"] not in skip for p in q]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    report = {}
    if os.path.exists(REPORT):
        with open(REPORT) as f:
            report = json.load(f)
    report["pachycephalosaurus"] = {
        "bones": len(m.bones), "cubes": len(m.cubes), "texture": [m.tw, m.th],
        "bounds_px": [[float(v) for v in lo], [float(v) for v in hi]],
        "animations": list(anims), "render_scale": 0.5, "handmade": True,
    }
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=1)
    print("pachycephalosaurus", json.dumps(report["pachycephalosaurus"]["bounds_px"]), "animations", os.path.getsize(anim_path) // 1024, "KB")
    print("QA: coplanar", left, "| pixel bugs", len(bugs), "| off the ground", len(ground))
    for b in bugs + ground:
        print("  ", b)
    # the universal colour rule (docs/CORES.md): a colour of its own
    import colourcheck
    clash, old, near = colourcheck.check("pachycephalosaurus")
    print("colour: nearest", ", ".join(f"{o} {d:.1f}" for d, o in near), "| clashes with remade", clash, "| old ones to recolour", [o for _, o in old])
    if left or bugs or ground or clash:
        sys.exit(1)


if __name__ == "__main__":
    main()
