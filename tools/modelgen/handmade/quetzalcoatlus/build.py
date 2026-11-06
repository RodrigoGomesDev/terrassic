"""
Builds the Quetzalcoatlus into the mod (its own study, page "1.9: estudos do Quetzalcoatlus, do Edmontossauro e do
Dakotaraptor", approved by Rodrigo on 06/11/2026). A hand-made rig at 16 px per metre (game scale 1.0, 10.9 m of
wingspan): the azhdarchid's long stiff neck and huge spear beak, short broad wings cut in 1 px membrane panels that
fold with the bones, long limbs on which it stands upright on all fours. The pterosaur plumbing (the wing fold, the
ground stance by IK, the flight poses) is the Pteranodon's, the proportions and its own animations are not
(quetzanims3.py: stalk, the spear strike, swallowing whole, the crest display, the long drink).

usage:  python3 -B tools/modelgen/handmade/quetzalcoatlus/build.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "_engine")]
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "spritegen"))

import geo  # noqa: E402
import proto as P  # noqa: E402
import quetz  # noqa: E402
import quetzanim as A  # noqa: E402
import quetzanims2 as B  # noqa: E402
import quetzanims3 as C  # noqa: E402
from anim2 import bake, to_geckolib  # noqa: E402
from sprites import save_png  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
REPORT = os.path.join(ROOT, "art", "build_report.json")
FPS = 20

# name: (pose function, length s, loop, when the game plays it)
ANIMS = {
    "idle": (A.idle_pose, A.IDLE_T, True, "on the ground, standing still (breathes, looks round, clacks the beak)"),
    "walk": (A.walk_pose, A.WALK_T, True, "on the ground, moving slowly (all fours, wing finger folded)"),
    "run": (B.run_pose, B.RUN_T, True, "on the ground, moving fast (bounding)"),
    "fly": (A.fly_pose, A.FLAP_T, True, "in the air while climbing or slow (flapping)"),
    "glide": (A.glide_pose, A.GLIDE_T, True, "in the air, level or descending (soaring)"),
    "bank_left": (B.bank_left, B.BANK_T, True, "gliding and turning left (yaw rate above a threshold)"),
    "bank_right": (B.bank_right, B.BANK_T, True, "gliding and turning right"),
    "takeoff": (A.takeoff_pose, A.TAKEOFF_T, False, "leaving the ground (then fly)"),
    "land": (A.land_pose, A.LAND_T, False, "touching down (then idle)"),
    "dive": (B.dive_pose, B.DIVE_T, False, "fishing sortie: the plunge at a fish (from glide)"),
    "scoop": (B.scoop_pose, B.SCOOP_T, False, "fishing sortie: skimming the surface and snapping a fish"),
    "swim": (B.swim_pose, B.SWIM_T, True, "floating on water (y = 0 of the animation is the water surface)"),
    "water_takeoff": (B.water_takeoff_pose, B.WATER_TAKEOFF_T, False, "taking off from the water (then fly)"),
    "eat": (C.swallow_pose, C.SWALLOW_T, False, "eating: the prey tossed up and swallowed whole"),
    "attack": (C.attack_pose, C.ATTACK_T, False, "the spear strike at prey on the ground (damage at ~0.36 s)"),
    "stalk": (C.stalk_pose, C.STALK_T, True, "on the ground with a target: the hunting walk, head low and steady"),
    "drink": (C.drink_pose, C.DRINK_T, False, "at the water's edge"),
    "call": (B.call_pose, B.CALL_T, False, "ambient call at the colony (sync the voice at 0.4 s)"),
    "display": (C.display_pose, C.DISPLAY_T, False, "males near a female: the crested head turned broadside, the beak clattering"),
    "preen": (B.preen_pose, B.PREEN_T, False, "idle extra at the colony"),
    "sun": (B.sun_pose, B.SUN_T, False, "idle extra in the sun (wings opened to dry, after swimming)"),
    "shake": (B.shake_pose, B.SHAKE_T, False, "after leaving water"),
    "beg": (B.beg_pose, B.BEG_T, True, "babies near a parent, or a tame one when the owner holds fish"),
    "sit": (B.sit_pose, B.SIT_T, True, "sitting order / resting at the colony"),
    "sleep": (B.sleep_pose, B.SLEEP_T, True, "asleep (night at the colony)"),
    "knocked_out": (B.knocked_out_pose, 3.0, True, "knocked out on the ground"),
    "knocked_out_air": (B.knocked_air_pose, B.KNOCKED_AIR_T, True, "knocked out while airborne, until it lands (limp spiral)"),
    "wake": (B.wake_pose, B.WAKE_T, False, "waking from the knockout (then idle)"),
    "death": (B.death_pose, B.DEATH_T, False, "dying (hold the last frame)"),
}
# keyframe every frame for the fast or jolting ones, linear where a curve would overshoot a hit
EVERY_FRAME = ("run", "attack", "shake", "wake", "death", "takeoff", "water_takeoff", "eat", "beg", "knocked_out_air", "stalk", "walk")
LINEAR = ("attack", "death", "knocked_out_air")


def main(only=None):
    m = quetz.build(saddle=True)
    import qa
    qa.single_face_planes(m)
    qa.separate_coplanar(m)
    P.pack(m, 256)
    geo_json = P.geo_json(m)
    with open(os.path.join(ASSETS, "geo", "entity", "quetzalcoatlus.geo.json"), "w") as f:
        json.dump(geo_json, f, indent=1)
    for sex in ("male", "female"):
        save_png(quetz.paint_sex(m, sex), os.path.join(ASSETS, "textures", "entity", f"quetzalcoatlus_{sex}.png"))

    anims = {}
    for name, (fn, length, loop, _when) in ANIMS.items():
        if only and name not in only:
            continue
        frames = bake(fn, length, FPS)
        anims[f"animation.quetzalcoatlus.{name}"] = to_geckolib(frames, length, FPS, loop, every=1 if name in EVERY_FRAME else 2,
                                                            lerp="linear" if name in LINEAR else "catmullrom")
        print(name, flush=True)
    with open(os.path.join(ASSETS, "animations", "entity", "quetzalcoatlus.animation.json"), "w") as f:
        json.dump({"format_version": "1.8.0", "animations": anims}, f, indent=1)

    spec = geo.load_geo(os.path.join(ASSETS, "geo", "entity", "quetzalcoatlus.geo.json"))
    pts = [p for _c, q in geo.cube_points(spec) for p in q]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    report = {}
    if os.path.exists(REPORT):
        with open(REPORT) as f:
            report = json.load(f)
    report["quetzalcoatlus"] = {
        "bones": len(geo_json["minecraft:geometry"][0]["bones"]), "cubes": len(m.cubes),
        "texture": [m.tw, m.th], "bounds_px": [[float(v) for v in lo], [float(v) for v in hi]],
        "animations": list(anims), "handmade": True,
    }
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=1)
    print("quetzalcoatlus", json.dumps(report["quetzalcoatlus"]["bounds_px"]))


if __name__ == "__main__":
    main(set(sys.argv[1:]) or None)
