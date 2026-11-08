"""
Builds the Daspletosaurus into the mod: the pilot of the 1.10.1 standard (docs/estudos/14, "Decisões do Rodrigo"),
drawn at skin2.PX_PER_M so it shows at ~16 texels per block, the skin in body space (skin2), two sexes, its own tyrant
saddle and its own animations (daspleanims.py, dasplefight.py). Writes:

  common/.../geo/entity/daspletosaurus.geo.json
  common/.../animations/entity/daspletosaurus.animation.json
  common/.../textures/entity/daspletosaurus_male.png, daspletosaurus_female.png
  art/build_report.json (its row; gen_species reads the bounds)

usage:  python3 -B tools/modelgen/handmade/daspletosaurus/build.py [--skin]   (--skin: repaint the skins only)

The build stops (exit 1) when the QA fails: coplanar faces, pixel bugs, a standing pose off the ground, a density
outside 16 +- 2 texels per block, or a head under the padrão v2 numbers (_engine/headcheck.py); all measured on the
exported files the way GeckoLib plays them.
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
import proto as P  # noqa: E402
import qa  # noqa: E402
import skin2  # noqa: E402
import dasple  # noqa: E402
import daspleanims as A  # noqa: E402
from anim2 import bake, to_geckolib  # noqa: E402
from jsongif import pose_at  # noqa: E402
from sprites import save_png  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
REPORT = os.path.join(ROOT, "art", "build_report.json")
REAL_M = 9.5
FPS = 20
LINEAR = ("hurt", "stagger", "recoil", "block", "knockout")
FAST = ("run", "death", "wake", "wake_sleep", "attack", "attack_quick", "lunge", "parry", "stagger", "face_bite",
        "strafe_left", "strafe_right", "recoil", "block", "bite_low", "bite_side", "stomp", "knockout", "steal_roar")
SADDLE = ("hide", "fur", "strap", "iron", "bone")
FLOATS = ("swim", "drink")
STANDING = ("idle", "sniff", "look_back", "shake", "yawn", "stretch", "snort", "settle", "scan", "roar", "roar_loud",
            "call", "threat", "jaw_test", "attack", "attack_quick", "bite_low", "bite_side", "hurt", "eat", "tame",
            "guard", "feint", "block", "idle_tired", "lunge", "parry", "face_bite", "carcass_guard", "face_rub", "shove")


def main():
    m = dasple.build(saddle_on=True)
    qa.single_face_planes(m)
    left = qa.separate_coplanar(m)
    P.pack(m, dasple.TEX_W)
    geo_path = os.path.join(ASSETS, "geo", "entity", "daspletosaurus.geo.json")
    with open(geo_path, "w") as f:
        json.dump(P.geo_json(m), f, indent=1)
    bugs, colours, heads = [], {}, []
    for sex in ("male", "female"):
        tex = dasple.paint_sex(m, sex)
        bugs += [(sex,) + b for b in qa.pixel_bugs(m, tex)]
        colours[sex] = skin2.colour_count(tex)
        p = dasple.pal_for(sex)
        fails, nums = headcheck.check(m, tex, p["iris"], p["glint"], sex=sex)     # the padrão v2 head
        print(headcheck.line("daspletosaurus", sex, nums))
        heads += [("head", sex, x) for x in fails]
        save_png(tex, os.path.join(ASSETS, "textures", "entity", f"daspletosaurus_{sex}.png"))

    if "--skin" in sys.argv:      # repaint only (the skins and the pixel QA), the animations stay
        print("QA: coplanar", left, "| pixel bugs", len(bugs), "| head", len(heads), "| colours", colours)
        for b in heads:
            print("  ", b)
        sys.exit(1 if left or bugs or heads else 0)
    anims = {}
    for name, (fn, length, loop, _cat, _when) in A.ANIMS.items():
        fps = 40 if name in FAST else FPS
        anims[f"animation.daspletosaurus.{name}"] = to_geckolib(bake(fn, length, fps), length, fps, loop, every=1,
                                                                lerp="linear" if name in LINEAR else "catmullrom")
        print(name, flush=True)
    anim_path = os.path.join(ASSETS, "animations", "entity", "daspletosaurus.animation.json")
    with open(anim_path, "w") as f:
        json.dump({"format_version": "1.8.0", "animations": anims}, f, indent=1)

    spec = geo.load_geo(geo_path)
    skip = {c["name"] for c in m.cubes if c["mat"] in SADDLE + ("teeth", "teeth_lo")}
    ground = []
    for key, an in anims.items():
        n = key.split(".")[-1]; L = an["animation_length"]; N = max(2, int(round(L * 40)))
        lows = [min(q[:, 1].min() for c, q in geo.cube_points(spec, pose_at(an, L * i / N)) if c["name"] not in skip)
                for i in range(N + 1)]
        if n not in FLOATS and (min(lows) < -0.3 or (n in STANDING and max(lows) > 0.3)):
            ground.append((n, round(min(lows), 2), round(max(lows), 2)))

    pts = [p for c, q in geo.cube_points(spec) if c["name"] not in skip for p in q]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    length = hi[2] - lo[2]
    dens = skin2.density(length, REAL_M)
    report = {}
    if os.path.exists(REPORT):
        with open(REPORT) as f:
            report = json.load(f)
    report["daspletosaurus"] = {
        "bones": len(m.bones), "cubes": len(m.cubes), "texture": [m.tw, m.th],
        "bounds_px": [[float(v) for v in lo], [float(v) for v in hi]],
        "animations": list(anims), "render_scale": round(16.0 / dasple.PX_M, 4), "handmade": True,
        "px_per_m": round(dasple.PX_M, 3), "texels_per_block": round(dens, 2), "colours": colours,
    }
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=1)
    print("daspletosaurus", json.dumps(report["daspletosaurus"]["bounds_px"]))
    print(f"density {dens:.2f} tx/block (length {length:.1f} px for {REAL_M} m) | colours {colours}")
    print("QA: coplanar", left, "| pixel bugs", len(bugs), "| off the ground", len(ground), "| head", len(heads),
          "| animations", len(anims))
    for b in bugs + ground + heads:
        print("  ", b)
    if left or bugs or ground or heads or not 14.0 <= dens <= 18.0:
        sys.exit(1)


if __name__ == "__main__":
    main()
