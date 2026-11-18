"""
Builds the Pachyrhinosaurus v4, "o bisão" (silhouette B of the 1.11 study, docs/estudos/15_HERBIVOROS_1_11.md), into the
mod in the 1.10 standard: drawn at skin2.PX_PER_M so it shows at ~16 texels per block, the skin drawn by hand in body
space (pachy.py), the head of the padrão v3 drawn from its own anatomy (the boss, the hooks), two sexes and the calf's
own skin, its pack saddle and its own animations (pachyanims.py). Writes:

  common/.../geo/entity/pachyrhinosaurus.geo.json
  common/.../animations/entity/pachyrhinosaurus.animation.json
  common/.../textures/entity/pachyrhinosaurus_male.png, _female.png, _baby.png
  art/build_report.json (its row; gen_species reads the bounds)

usage:  python3 -B tools/modelgen/handmade/pachyrhinosaurus/build.py [--skin]   (--skin: repaint the skins only)

The build stops (exit 1) when the QA fails: coplanar faces, pixel bugs, a standing pose off the ground, a density
outside 16 +- 2 texels per block, a head under the padrão v2 numbers, a head too close to another remade head (also
against the remade ceratopsians and hadrosaurs), or a colour closer than 10 to a remade species.
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
import headcheck  # noqa: E402
import uniquecheck  # noqa: E402
import colourcheck  # noqa: E402
import proto as P  # noqa: E402
import qa  # noqa: E402
import skin2  # noqa: E402
import pachy  # noqa: E402
from anim2 import bake, to_geckolib  # noqa: E402
from jsongif import pose_at  # noqa: E402
from sprites import save_png  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
REPORT = os.path.join(ROOT, "art", "build_report.json")
REAL_M = 8.0
FPS = 20
FPS_OF = {"run": 40, "charge": 40, "attack": 40, "wake": 40, "wake_sleep": 40, "get_up": 40, "lie_down": 30,
          "boss_ram": 40, "head_toss": 40, "lunge": 40, "parry": 40, "stagger": 40, "knockout": 40, "death": 40,
          "horn_lock_start": 40, "horn_lock_break": 40, "feint": 40, "block": 40, "recoil": 40}
EVERY_FRAME = ("walk", "run", "charge", "wade", "attack", "death", "wake", "turn_left", "turn_right", "strafe_left",
               "strafe_right", "walk_tired", "boss_ram", "head_toss", "lunge", "parry", "stagger", "knockout",
               "wake_sleep", "get_up", "lie_down", "horn_lock_start", "horn_lock_break", "feint", "recoil")
SLOW = ("idle", "sit", "sleep", "knocked_out", "nap")
LINEAR = ("hurt", "attack", "death", "wake", "wake_sleep", "boss_ram", "head_toss", "lunge", "parry", "stagger",
          "knockout", "horn_lock_start", "recoil")
STANDING = ("idle", "call", "eat", "graze", "drink", "beg", "tame", "hurt", "idle_tired", "brace", "guard", "block",
            "hesitate", "boss_rub", "snow_dig", "head_toss", "roar", "horn_lock", "boss_push")
FLOATS = ("swim",)
# the uniqueness check also against the remade hadrosaurs it must not look like (study 15)
OTHERS = tuple(uniquecheck.HEADS) + ("triceratops", "styracosaurus", "protoceratops", "maiasaura", "corythosaurus")


def main():
    m = pachy.build(saddle_on=True)
    qa.single_face_planes(m)
    left = qa.separate_coplanar(m)
    P.pack(m, pachy.TEX_W)
    geo_path = os.path.join(ASSETS, "geo", "entity", "pachyrhinosaurus.geo.json")
    with open(geo_path, "w") as f:
        json.dump(P.geo_json(m), f, indent=1)
    bugs, colours, heads = [], {}, []
    for sex in ("male", "female", "baby"):
        tex = pachy.paint_sex(m, sex)
        bugs += [(sex,) + b for b in qa.pixel_bugs(m, tex)]
        colours[sex] = skin2.colour_count(tex)
        if sex != "baby":
            p = pachy.pal_for(sex)
            fails, nums = headcheck.check(m, tex, [p["iris"], p["iris2"]], p["glint"], sex=sex)
            print(headcheck.line("pachyrhinosaurus", sex, nums))
            heads += [("head", sex, x) for x in fails]
        save_png(tex, os.path.join(ASSETS, "textures", "entity", f"pachyrhinosaurus_{sex}.png"))
    uniquecheck.SPECIES.setdefault("maiasaura", "maiasaura/maia.py")
    uniquecheck.SPECIES.setdefault("corythosaurus", "corythosaurus/cory.py")
    uniquecheck.SPECIES.setdefault("pachyrhinosaurus", "pachyrhinosaurus/pachy.py")
    ufails, urows = uniquecheck.check("pachyrhinosaurus", others=list(OTHERS))
    print(uniquecheck.table(urows, top=5))
    heads += [("unique", x) for x in ufails]
    clash, _old, near = colourcheck.check("pachyrhinosaurus", against=("male",), remade_only=True)
    print("colour --remade: nearest", ", ".join(f"{o} {d:.1f}" for d, o in near))
    heads += [("colour", c) for c in clash]

    if "--skin" in sys.argv:
        print("QA: coplanar", left, "| pixel bugs", len(bugs), "| head", len(heads), "| colours", colours, bugs[:8])
        for b in heads:
            print("  ", b)
        sys.exit(1 if left or bugs or heads else 0)
    import pachyanims as A
    anims = {}
    for name, (fn, length, loop, _cat, _when) in A.ANIMS.items():
        fps = FPS_OF.get(name, FPS)
        anims[f"animation.pachyrhinosaurus.{name}"] = to_geckolib(bake(fn, length, fps), length, fps, loop,
                                                           every=1 if name in EVERY_FRAME else 4 if name in SLOW else 2,
                                                           lerp="linear" if name in LINEAR else "catmullrom")
        print(name, flush=True)
    anim_path = os.path.join(ASSETS, "animations", "entity", "pachyrhinosaurus.animation.json")
    with open(anim_path, "w") as f:
        json.dump({"format_version": "1.8.0", "animations": anims}, f, separators=(",", ":"))

    spec = geo.load_geo(geo_path)
    skip = {"saddle"}
    ground = []
    for key, an in anims.items():
        n = key.split(".")[-1]; L = an["animation_length"]; N = max(2, int(round(L * 40)))
        lows = [min(q[:, 1].min() for c, q in geo.cube_points(spec, pose_at(an, L * i / N))
                    if c["bone"] not in skip and c.get("name", "").find("beak_edge") < 0 and c.get("mat") != "teeth")
                for i in range(N + 1)]
        if n not in FLOATS and (min(lows) < -0.3 or (n in STANDING and max(lows) > 0.3)):
            ground.append((n, round(min(lows), 2), round(max(lows), 2)))

    pts = [p for c, q in geo.cube_points(spec) if c["bone"] not in skip for p in q]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    length = hi[2] - lo[2]
    dens = skin2.density(length, REAL_M)
    report = {}
    if os.path.exists(REPORT):
        with open(REPORT) as f:
            report = json.load(f)
    report["pachyrhinosaurus"] = {
        "bones": len(m.bones), "cubes": len(m.cubes), "texture": [m.tw, m.th],
        "bounds_px": [[float(v) for v in lo], [float(v) for v in hi]],
        "animations": list(anims), "render_scale": round(16.0 / pachy.PX_M, 4), "handmade": True,
        "px_per_m": round(pachy.PX_M, 3), "texels_per_block": round(dens, 2), "colours": colours,
    }
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=1)
    print("pachyrhinosaurus", json.dumps(report["pachyrhinosaurus"]["bounds_px"]), "animations", os.path.getsize(anim_path) // 1024, "KB")
    print(f"density {dens:.2f} tx/block (length {length:.1f} px for {REAL_M} m) | colours {colours}")
    print("QA: coplanar", left, "| pixel bugs", len(bugs), "| off the ground", len(ground), "| head", len(heads),
          "| animations", len(anims))
    for b in bugs + ground + heads:
        print("  ", b)
    if left or bugs or ground or heads or not 14.0 <= dens <= 18.0:
        sys.exit(1)


if __name__ == "__main__":
    main()
