"""
Builds the Velociraptor into the mod. A hand-made rig in the T. rex standard, third species after the T. rex and the
Pteranodon (30/10, Rodrigo approved the v3 look at 20:45Z after measuring it against the T. rex and the Pteranodon):
86 designed cubes with per-face UV (78 for the animal, 8 for the hunting harness), a 256 px wide skin drawn by form
for male and female, three clawed fingers, two toes plus the raised sickle claw, wing feathers in two layers, a frond
tail fan and a nuchal crest, 28 animations baked from poses (legs on the ground by IK). Writes:

  common/.../geo/entity/velociraptor.geo.json
  common/.../animations/entity/velociraptor.animation.json
  common/.../textures/entity/velociraptor_male.png, velociraptor_female.png
  art/build_report.json (its row: bones, cubes, texture, bounds, animations; gen_species reads the bounds)

usage:  python3 -B tools/modelgen/handmade/velociraptor/build.py      (or build_all.py velociraptor)

Same GeckoLib note as the T. rex: proto.geo_json flips u on the east/west faces; preview from the exported file.
Drawn at 48 px per metre (100 px long): MODEL_SCALE 0.5 shows it at 3.1 m, 1.5x the real 2.07 m (Rodrigo's size
choice, the same kind of exception as the Pteranodon), so it reads as a threat next to a player.
The harness hangs on a bone named "saddle", so DinoGeoModel shows it only while the raptor wears one.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "spritegen"))

import geo  # noqa: E402
import proto as P  # noqa: E402
import raptor  # noqa: E402
import raptanims as A  # noqa: E402
from anim2 import bake, to_geckolib  # noqa: E402
from sprites import save_png  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
REPORT = os.path.join(ROOT, "art", "build_report.json")
FPS = 20

# when the game plays each one (raptanims.ANIMS holds the pose function, length and loop)
WHEN = {
    "idle": "standing still (breathes, bird head: snaps to look, holds, snaps again)",
    "sniff": "idle extra: sniffs the ground",
    "look_back": "idle extra: looks back over the shoulder",
    "preen": "idle extra: runs the wing feathers through the jaws",
    "ruffle": "idle extra; also on leaving water or in rain (feather shake)",
    "stretch": "idle extra; also right after wake_sleep (wing and leg of one side, then the other)",
    "walk": "moving slowly",
    "run": "moving fast (wings half open for balance)",
    "stalk": "closing on a target it has not attacked yet (crouched creep)",
    "swim": "in water (y = 0 of the animation is the water line)",
    "leap": "LeapAtTargetGoal jump: airborne 0.26-0.82 s",
    "call": "ambient voice, pack contact (chirps at 0.55, 0.85, 1.15 s)",
    "screech": "hunting cry when the pack picks a target, before the chase (mouth open at 0.5 s)",
    "display": "threat: a player or a bigger animal comes close and it is not hunting; tame ones on the attack order",
    "attack": "bite (the jaws close at 0.3 s: deal the damage there)",
    "kick": "sickle-claw kick, alternates with the bite (the slash lands at 0.5 s)",
    "pounce": "after a leap that lands on prey smaller than itself: pins it (bites at 0.7, 1.3, 1.9 s)",
    "hurt": "on damage",
    "death": "dying (hold the last frame)",
    "eat": "eating meat or a carcass",
    "drink": "drinking at water",
    "sit": "sit order (tame) or resting",
    "sleep": "asleep (by day: it is nocturnal), the Mei long pose",
    "wake_sleep": "waking from sleep (then stretch)",
    "knocked_out": "knocked out",
    "wake": "getting up from a knockout",
    "beg": "tame, owner holds its food",
    "tame": "the moment it is tamed",
}
# keyframe every frame for the fast or jolting ones, linear where a curve would overshoot a hit
EVERY_FRAME = ("walk", "run", "stalk", "leap", "kick", "attack", "hurt", "death", "wake", "wake_sleep", "beg", "ruffle", "idle")
LINEAR = ("kick", "hurt", "death", "wake", "wake_sleep")


def main(only=None):
    m = raptor.build(harness=True)
    raptor.separate_coplanar(m)
    P.pack(m, 256)
    geo_json = P.geo_json(m)
    with open(os.path.join(ASSETS, "geo", "entity", "velociraptor.geo.json"), "w") as f:
        json.dump(geo_json, f, indent=1)
    for sex in ("male", "female"):
        save_png(raptor.paint_sex(m, sex), os.path.join(ASSETS, "textures", "entity", f"velociraptor_{sex}.png"))

    anims = {}
    for name, (fn, length, loop, _cat, _pt) in A.ANIMS.items():
        if only and name not in only:
            continue
        frames = bake(fn, length, FPS)
        anims[f"animation.velociraptor.{name}"] = to_geckolib(frames, length, FPS, loop, every=1 if name in EVERY_FRAME else 2,
                                                              lerp="linear" if name in LINEAR else "catmullrom")
        print(name, flush=True)
    with open(os.path.join(ASSETS, "animations", "entity", "velociraptor.animation.json"), "w") as f:
        json.dump({"format_version": "1.8.0", "animations": anims}, f, indent=1)

    spec = geo.load_geo(os.path.join(ASSETS, "geo", "entity", "velociraptor.geo.json"))
    pts = [p for _c, q in geo.cube_points(spec) for p in q]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    report = {}
    if os.path.exists(REPORT):
        with open(REPORT) as f:
            report = json.load(f)
    report["velociraptor"] = {
        "bones": len(geo_json["minecraft:geometry"][0]["bones"]), "cubes": len(m.cubes),
        "texture": [m.tw, m.th], "bounds_px": [[float(v) for v in lo], [float(v) for v in hi]],
        "animations": list(anims), "handmade": True,
    }
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=1)
    print("velociraptor", json.dumps(report["velociraptor"]["bounds_px"]))


if __name__ == "__main__":
    main(set(sys.argv[1:]) or None)
