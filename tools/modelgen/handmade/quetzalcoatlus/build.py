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
import quetzflow as F  # noqa: E402  (06/11: the fluid set, rebinds the takeoff's flap)
from anim2 import bake, to_geckolib  # noqa: E402
from sprites import save_png  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
REPORT = os.path.join(ROOT, "art", "build_report.json")
FPS = 20

# name: (pose function, length s, loop, when the game plays it)
ANIMS = {
    "idle": (F.idle, F.IDLE_T, True, "on the ground, standing still (breathes, looks round, clacks the beak)"),
    "walk": (F.walk, A.WALK_T, True, "on the ground, moving slowly (all fours, wing finger folded)"),
    # the bounding run's leg IK flips its Euler branch mid-stride (a 1888 deg spin of the shin in game, 06/11): the run
    # is the walk's quadrupedal stride at a quicker beat until that IK is redone
    "run": (lambda t: F.walk(t * A.WALK_T / B.RUN_T), B.RUN_T, True, "on the ground, moving fast (the walk's stride, quicker)"),
    "fly": (F.fly, F.FLAP_T, True, "in the air while climbing or slow (flapping)"),
    "glide": (F.glide, F.GLIDE_T, True, "in the air, level or descending (soaring)"),
    "bank_left": (F.bank_left, F.BANK_T, True, "gliding and turning left (yaw rate above a threshold)"),
    "bank_right": (F.bank_right, F.BANK_T, True, "gliding and turning right"),
    "takeoff": (A.takeoff_pose, A.TAKEOFF_T, False, "leaving the ground (then fly)"),
    "land": (A.land_pose, A.LAND_T, False, "touching down (then idle)"),
    "dive": (B.dive_pose, B.DIVE_T, False, "fishing sortie: the plunge at a fish (from glide)"),
    "scoop": (B.scoop_pose, B.SCOOP_T, False, "fishing sortie: skimming the surface and snapping a fish"),
    "swim": (B.swim_pose, B.SWIM_T, True, "floating on water (y = 0 of the animation is the water surface)"),
    "water_takeoff": (B.water_takeoff_pose, B.WATER_TAKEOFF_T, False, "taking off from the water (then fly)"),
    "eat": (F.eat, F.EAT_T, False, "eating: the prey tossed up and swallowed whole"),
    "attack": (F.attack, F.ATTACK_T, False, "the spear strike at prey on the ground (damage at ~0.36 s)"),
    "stalk": (F.stalk, F.STALK_T, True, "on the ground with a target: the hunting walk, head low and steady"),
    "drink": (F.drink, F.DRINK_T, False, "at the water's edge"),
    "call": (F.call, F.CALL_T, False, "ambient call at the colony (sync the voice at 0.4 s)"),
    "display": (F.display, F.DISPLAY_T, False, "males near a female: the crested head turned broadside, the beak clattering"),
    "jab": (F.jab, F.JAB_T, False, "the beak thrust at a standing target ahead, beak shut (hit at 0.34 s)"),
    "turn_left": (F.turn_left, F.TURN_T, True, "on the ground, turning on the spot to the left (steps round, head first)"),
    "turn_right": (F.turn_right, F.TURN_T, True, "on the ground, turning on the spot to the right"),
    "idle_tired": (F.idle_tired, F.IDLE_TIRED_T, True, "on the ground, spent after a chase or a long flight: panting"),
    "preen": (F.preen, F.PREEN_T, False, "idle extra at the colony"),
    "sun": (F.sun, F.SUN_T, False, "idle extra in the sun (wings opened to dry, after swimming)"),
    "shake": (F.shake, F.SHAKE_T, False, "after leaving water"),
    "beg": (B.beg_pose, B.BEG_T, True, "babies near a parent, or a tame one when the owner holds fish"),
    "sit": (F.sit, F.SIT_T, True, "sitting order / resting at the colony"),
    "sleep": (F.sleep, F.SLEEP_T, True, "asleep (night at the colony)"),
    "knocked_out": (B.knocked_out_pose, 3.0, True, "knocked out on the ground"),
    "knocked_out_air": (B.knocked_air_pose, B.KNOCKED_AIR_T, True, "knocked out while airborne, until it lands (limp spiral)"),
    "wake": (B.wake_pose, B.WAKE_T, False, "waking from the knockout (then idle)"),
    "death": (B.death_pose, B.DEATH_T, False, "dying (hold the last frame)"),
}
# keyframe every frame for the fast or jolting ones, linear where a curve would overshoot a hit
EVERY_FRAME = ("run", "attack", "shake", "wake", "death", "takeoff", "water_takeoff", "eat", "beg", "knocked_out_air", "stalk", "walk",
               "jab", "turn_left", "turn_right", "call", "display", "fly")
LINEAR = ("attack", "jab", "death", "knocked_out_air")


def unwrap(frames):
    """the leg IK may hand back the same angle plus whole turns between two frames (the run's shin jumped 1888 deg in
    a frame, 06/11): each rotation is brought within 180 deg of the previous frame's"""
    prev = {}
    for f in frames:
        for bone, entry in f.items():
            r = list(entry[0])
            if bone in prev:
                for k in range(3):
                    while r[k] - prev[bone][k] > 180.0:
                        r[k] -= 360.0
                    while r[k] - prev[bone][k] < -180.0:
                        r[k] += 360.0
            prev[bone] = r
            f[bone] = (r,) + tuple(entry[1:])
    return frames


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
        frames = unwrap(bake(fn, length, FPS))
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
