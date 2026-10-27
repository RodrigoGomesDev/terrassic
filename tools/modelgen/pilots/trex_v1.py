"""Opt-in T. rex art pilot. Does not replace shipped species or write game assets.

Original geometry/poses authored for Terrassic. Alex's Caves was studied for
principles only: no imported models, textures, keyframes or code.
"""
from pathlib import Path
import sys
import math
import copy

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(HERE), str(HERE / "species")]
import tyrannosaurus as original
from pybench import Rig, pose_at

HIDE = ("saddle", "female_display")


def evaluate(animation, t):
    """Respect linear baking; the legacy preview evaluator assumes Catmull-Rom."""
    if animation.get("interp", "catmullrom") != "linear":
        return pose_at(animation, t)
    pose = {}
    for bone, tracks in animation["bones"].items():
        values = []
        for channel, default in (("rotation", (0,0,0)), ("position", (0,0,0)), ("scale", (1,1,1))):
            keys = tracks.get(channel)
            if not keys:
                values.append(default)
            else:
                values.append(tuple(float(np.interp(t, [k[0] for k in keys], [k[i] for k in keys]))
                                    for i in (1,2,3)))
        pose[bone] = tuple(values)
    return pose


def smooth(t, start, end):
    u = min(1., max(0., (t - start) / (end - start)))
    return u * u * (3 - 2 * u)


def point_cloud(rig, pose, bones=None):
    return np.array([w for cube, _, corners, _ in rig.cube_faces(pose, HIDE)
                     if bones is None or cube["bone"] in bones
                     for _, w in corners.values()])


def blank():
    return {}


def set_pose(p, bone, rot=(0, 0, 0), pos=(0, 0, 0), scale=(1, 1, 1)):
    p[bone] = (tuple(rot), tuple(pos), tuple(scale))


def collapse(t):
    """Failure of one leg, crouch, lateral fall, then delayed neck/tail settling."""
    p = blank()
    crouch = smooth(t, .12, .72)
    fall = smooth(t, .56, 1.46)
    settle = smooth(t, 1.46, 2.6)
    set_pose(p, "body", (-5 * crouch + 7 * fall, -3 * fall, 84 * fall),
             (8 * fall, -16 * crouch - 30 * fall, 4 * crouch))
    set_pose(p, "chest", (3 * smooth(t, .3, 1), 0, -3 * fall))
    for side, lag, sign in (("l", 0., 1), ("r", .2, -1)):
        bend = smooth(t, .1 + lag, .75 + lag)
        relax = smooth(t, 1.05 + lag, 1.9 + lag)
        set_pose(p, f"thigh_{side}", (46 * bend - 20 * relax, 5 * relax * sign, 8 * relax * sign))
        set_pose(p, f"shin_{side}", (-72 * bend + 24 * relax, 0, 0))
        set_pose(p, f"foot_{side}", (26 * bend - 4 * relax, 0, 0))
        set_pose(p, f"toes_{side}", (0, 0, 0))
        set_pose(p, f"arm_{side}", (16 * fall + 4 * sign * settle, 0, sign * 7 * fall))
    lag = smooth(t, .8, 1.9)
    set_pose(p, "neck1", (6 * crouch - 13 * lag, 6 * lag, -4 * lag))
    set_pose(p, "neck2", (-6 * lag, -3 * lag, 0))
    set_pose(p, "skull", (-4 * lag, 0, 2 * lag))
    set_pose(p, "jaw", (-13 * smooth(t, .25, .75) + 8 * settle, 0, 0))
    for i in range(1, 5):
        wave = math.sin(math.pi * smooth(t, .45 + .12 * i, 1.75 + .12 * i))
        set_pose(p, f"tail{i}", (2 * fall, (-1)**i * wave * (3 + i) + 2 * fall, -2 * fall))
    set_pose(p, "eyelids", scale=(1, 1, 1) if t >= 1.35 else (0, 0, 0))
    return p


def build():
    m = original.build()
    # Chest is a real joint, not loose ornamental cubes. Hips and tail remain independent.
    m.bone("chest", "body", (0, 57, -26))
    for b in m.bones:
        if b.name in ("neck1", "arm_l", "arm_r"):
            b.parent = "chest"
        if b.name in ("thigh_l", "thigh_r"):
            b.parent = "body"
    for c in m.cubes:
        if c.name in ("chest", "withers", "pectoral_l", "pectoral_r"):
            c.bone = "chest"
    # Broad anatomical layers: scapular mass, cheeks, lower throat. No extra tiny scales.
    for s in (-1, 1):
        x0, x1 = sorted((s * 10, s * 15))
        m.box("chest", (x0, 45, -43), (x1, 63, -29), name=f"scapular_mass_{s}",
              rot=(0, 0, s * -7), origin=(s * 11, 57, -34))
        x0, x1 = sorted((s * 11, s * 15))
        m.box("body", (x0, 41, -24), (x1, 63, -3), name=f"oblique_fold_{s}")
        x0, x1 = sorted((s * 9, s * 12))
        m.box("skull", (x0, 73, -74), (x1, 80, -67), name=f"cheek_pad_{s}")
    # Eyelids are hidden by scale in awake clips and close only in sleep/dead poses.
    m.bone("eyelids", "skull", (0, 81, -75))
    for s in (-1, 1):
        x0, x1 = sorted((s * 9, s * 10))
        m.box("eyelids", (x0, 79, -77), (x1, 84, -72), name=f"eyelid_{s}")
    # Parent-first order is required by both the exporter and FK evaluator.
    ordered = []
    def visit(parent):
        for b in m.bones:
            if b.parent == parent:
                ordered.append(b)
                visit(b.name)
    visit(None)
    m.bones = ordered
    rig = Rig(m.spec())
    original_anims = copy.deepcopy(m.animations)
    # Bake intended smooth easing at 20 Hz, export linear segments: no Catmull overshoot.
    new = []
    all_bones = [b.name for b in m.bones]

    def bake(name, duration, fn, loop=False):
        tracks = {b: {ch: [] for ch in ("rotation", "position", "scale")} for b in all_bones}
        for t in np.linspace(0, duration, round(duration * 20) + 1):
            p = fn(float(t))
            for b in all_bones:
                values = p.get(b, ((0, 0, 0), (0, 0, 0), (1, 1, 1)))
                for ch, v in zip(("rotation", "position", "scale"), values):
                    tracks[b][ch].append([round(float(t), 4), *[round(float(x), 4) for x in v]])
        # Constant channels need only two keys; retain explicit resets for exclusive clips.
        for bone in tracks.values():
            for channel, keys in bone.items():
                if all(k[1:] == keys[0][1:] for k in keys):
                    bone[channel] = [keys[0], keys[-1]]
        new.append({"name": f"animation.tyrannosaurus.{name}", "length": duration,
                    "loop": "loop" if loop else "once", "interp": "linear", "bones": tracks})

    # Contact is solved offline for this pilot. Report the correction separately;
    # it is not IK and must not be mistaken for terrain support in the game.
    corrections = []
    def grounded(p):
        low = point_cloud(rig, p)[:, 1].min()
        root = p.get("root", ((0, 0, 0), (0, 0, 0), (1, 1, 1)))
        dy = root[1][1] - float(low)
        set_pose(p, "root", root[0], (root[1][0], dy, root[1][2]), root[2])
        corrections.append(dy)
        return p

    dead = grounded(collapse(2.6))
    def falling(t):
        return grounded(collapse(t))
    bake("death", 2.6, falling)
    bake("knockout", 2.6, falling)
    bake("dead", 1, lambda t: copy.deepcopy(dead), True)
    def knocked(t):
        p = copy.deepcopy(dead)
        set_pose(p, "eyelids", scale=(1, 1, 1))
        set_pose(p, "chest", p["chest"][0], scale=(1 + .007 * math.sin(math.pi * t / 2)**2, 1, 1))
        return p
    bake("knocked_out", 4, knocked, True)

    # A compact sternal rest, distinct from lateral unconsciousness.
    rest = blank()
    set_pose(rest, "body", (1, 0, 0), (0, -30, 0))
    for side, sign in (("l", 1), ("r", -1)):
        set_pose(rest, f"thigh_{side}", (57, 0, 12 * sign))
        set_pose(rest, f"shin_{side}", (-104, 0, -24 * sign))
        set_pose(rest, f"foot_{side}", (47, 0, 12 * sign))
        set_pose(rest, f"toes_{side}", (-1, 0, 0))
    set_pose(rest, "neck1", (-6, 0, 0))
    set_pose(rest, "neck2", (-4, 0, 0))
    set_pose(rest, "skull", (7, 0, 0))
    set_pose(rest, "eyelids", scale=(0, 0, 0))
    rest = grounded(rest)
    def resting(t, asleep=False):
        p = copy.deepcopy(rest)
        set_pose(p, "chest", scale=(1 + .008 * math.sin(math.pi * t / 2)**2, 1, 1))
        set_pose(p, "eyelids", scale=(1, 1, 1) if asleep else (0, 0, 0))
        return p
    bake("sit", 4, resting, True)
    bake("sleep", 4, lambda t: resting(t, True), True)

    def blend(a, b, f):
        p = {}
        for bone in all_bones:
            va = a.get(bone, ((0, 0, 0), (0, 0, 0), (1, 1, 1)))
            vb = b.get(bone, ((0, 0, 0), (0, 0, 0), (1, 1, 1)))
            p[bone] = tuple(tuple(x * (1-f) + y*f for x, y in zip(v1, v2)) for v1, v2 in zip(va, vb))
        return p
    # Recovery first rolls onto a sternal support, then extends the legs. Not reverse death.
    def waking(t):
        if t <= 1.05:
            p = blend(dead, rest, smooth(t, .15, 1.05))
            p["jaw"] = ((0, 0, 0), (0, 0, 0), (1, 1, 1))
        else:
            p = blend(rest, {"eyelids": ((0, 0, 0), (0, 0, 0), (0, 0, 0))}, smooth(t, 1.05, 2.8))
        return grounded(p)
    bake("wake", 2.8, waking)
    awake = {"eyelids": ((0, 0, 0), (0, 0, 0), (0, 0, 0))}
    bake("lie_down", 2., lambda t: grounded(blend(awake, rest, smooth(t, 0, 2))))
    bake("stand_up", 2., lambda t: grounded(blend(rest, awake, smooth(t, 0, 2))))
    # Keep original identity/actions for comparison; only chest breathing added to idle.
    replace = {a["name"] for a in new}
    for a in original_anims:
        if a["name"] in replace:
            continue
        a["bones"]["eyelids"] = {"scale": [[0, 0, 0, 0], [a["length"], 0, 0, 0]]}
        if a["name"].endswith(".idle"):
            # Remove the original whole-body lift: breathing expands the ribcage.
            a["bones"].pop("body", None)
            a["bones"]["chest"] = {"scale": [[t, 1 + .008 * math.sin(math.pi*t/2)**2, 1, 1]
                                                        for t in np.linspace(0, 4, 17)]}
        new.append(a)
    m.animations = new
    m._pilot_ground_correction_range = [min(corrections), max(corrections)]
    return m
