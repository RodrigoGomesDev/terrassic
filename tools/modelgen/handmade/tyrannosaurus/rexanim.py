"""T. rex v2: the rig the animations are baked on (no saddle), and the walk, idle, roar and bite."""
import math
import numpy as np
import geo, proto as P, rex2
from anim2 import *

def model():
    m = rex2.build(saddle=False); P.pack(m, 256); return m.spec()

S = model()
REST_BALL = {s: world(S, {}, f"toes_{s}") for s in ("l", "r")}

# ------------------------------------------------------------------ walk
WALK_T = 1.9          # s per cycle: heavy, unhurried
STRIDE = 72.0         # px per cycle (4.5 m)
DUTY = 0.62           # share of the cycle each foot is on the ground
LIFT = 9.0            # px foot clearance

def foot_path(u):
    """u in [0,1): 0 = heel strike. returns (dz backward, lift, stance progress or None)"""
    if u < DUTY:
        s = u / DUTY
        return -STRIDE * DUTY / 2 + STRIDE * DUTY * s, 0.0, s
    s = (u - DUTY) / (1 - DUTY)
    e = 0.5 - 0.5 * math.cos(math.pi * s)                       # accelerate then brake
    dz = STRIDE * DUTY / 2 - STRIDE * DUTY * e
    lift = LIFT * math.sin(math.pi * min(1, s * 1.15)) ** 1.3    # lift early, set down gently
    return dz, max(0.0, lift), None

def walk_pose(t, speed_scale=1.0):
    ph = (t / WALK_T) % 1.0
    pose = {}
    w = 2 * math.pi * ph
    # weight: lowest just after each heel strike, highest mid-stance (2 per cycle)
    bob = -1.6 * math.cos(2 * w - 0.9) - 0.6
    add(pose, "body", rot=(1.2 * math.sin(2 * w - 0.4), 2.2 * math.sin(w), 2.4 * math.sin(w + 0.35)), pos=(0, bob, 0))
    # head stays steady: neck and skull cancel most of the body motion, then lag a little
    add(pose, "neck", rot=(-1.0 * math.sin(2 * w - 0.4) + 1.4 * math.sin(2 * w - 1.6), -1.6 * math.sin(w - 0.6), -1.2 * math.sin(w + 0.35)))
    add(pose, "skull", rot=(0.9 * math.sin(2 * w - 2.1), -0.8 * math.sin(w - 1.3), -1.0 * math.sin(w)))
    add(pose, "jaw", rot=(-1.0 - 1.0 * math.sin(2 * w - 2.6), 0, 0))
    # tail: counter-sway with a delay that grows towards the tip
    for k in range(1, 5):
        add(pose, f"tail{k}", rot=(0.8 * math.sin(2 * w - 0.9 - 0.55 * k), -(1.6 + 1.1 * k) * math.sin(w - 0.5 - 0.6 * k), 0.6 * math.sin(w - 0.6 * k)))
    # little arms: passive, late
    for s, o in (("l", 0), ("r", math.pi)):
        add(pose, f"arm_{s}", rot=(5 * math.sin(w + o - 2.0), 0, 0))
        add(pose, f"forearm_{s}", rot=(6 * math.sin(w + o - 2.6), 0, 0))
    # legs: planted feet via IK
    for s, o in (("l", 0.0), ("r", 0.5)):
        u = (ph + o) % 1.0
        dz, lift, st = foot_path(u)
        b = REST_BALL[s]
        target = (b[1] + lift, b[2] + dz - 6)
        if st is not None:
            meta = 0 + 34 * smooth(max(0, (st - 0.55) / 0.45))            # heel rises in late stance
            toe = 0.0
        else:
            sw = (u - DUTY) / (1 - DUTY)
            meta = 34 * (1 - smooth(sw / 0.5)) - 18 * math.sin(math.pi * sw)   # foot folds, then reaches forward
            toe = -28 * math.sin(math.pi * min(1, sw * 1.1)) + 6 * smooth((sw - 0.7) / 0.3)
        rest_meta = chain_angle(S, {}, [f"foot_{s}"])
        for _ in range(4):                        # keep every claw above the ground
            solve_leg(S, pose, s, target, rest_meta + meta, toe)
            lo = leg_low(pose, s); need = -0.05 if st is not None else 1.2 * math.sin(math.pi * (u - DUTY) / (1 - DUTY)) ** 0.5
            if lo > need - 0.02: break
            target = (target[0] + need - lo, target[1])
    return pose

LEG = {s: {f"{b}_{s}" for b in ("thigh", "shin", "foot", "toes")} for s in ("l", "r")}
def leg_low(pose, s):
    return min(q[:, 1].min() for c, q in geo.cube_points(S, pose) if c["bone"] in LEG[s])

# ------------------------------------------------------------------ idle: breathing, weight shift, quick head turns that hold
IDLE_T = 8.0
LOOK = Track([(0, (0, 0)), (0.9, (0, 0)), (1.25, (4, 16), ease_out), (3.0, (4, 16)), (3.3, (-2, -10), ease_out), (3.5, (-2, -10)),
              (5.2, (-2, -10)), (5.5, (6, 4), ease_out), (7.2, (6, 4)), (7.7, (0, 0))])
def idle_pose(t):
    pose = {}
    br = math.sin(2 * math.pi * t / 2.0)                         # one breath every 2 s
    sh = math.sin(2 * math.pi * t / IDLE_T)                      # slow weight shift
    add(pose, "body", rot=(0.8 * br, 0.8 * sh, 1.4 * sh), pos=(0, 0.35 * br, 0))
    add(pose, "neck", rot=(-0.6 * br, 0, -0.8 * sh))
    lp, ly = LOOK(t)
    add(pose, "neck", rot=(lp * 0.4, ly * 0.45, 0))
    add(pose, "skull", rot=(lp * 0.6 - 0.4 * br, ly * 0.55, -ly * 0.12))
    add(pose, "jaw", rot=(-0.8 - 0.8 * max(0, br), 0, 0))
    for k in range(1, 5):
        add(pose, f"tail{k}", rot=(0.5 * math.sin(2 * math.pi * t / 2.0 - 0.5 * k), -(0.8 + 0.7 * k) * math.sin(2 * math.pi * t / IDLE_T - 0.45 * k), 0))
    for s in ("l", "r"):
        add(pose, f"arm_{s}", rot=(1.5 * br, 0, 0)); add(pose, f"forearm_{s}", rot=(-2 * math.sin(2 * math.pi * t / 2.0 - 0.8), 0, 0))
        b = REST_BALL[s]
        solve_leg(S, pose, s, (b[1], b[2]), chain_angle(S, {}, [f"foot_{s}"]), 0.0)
    return pose

# ------------------------------------------------------------------ roar: crouch, inhale, roar with a sweep, hold, settle
ROAR_T = 3.4
R_BODY = Track([(0, (0, 0)), (0.3, (6, 0)), (0.75, (-9, 0), ease_out), (1.0, (-4, 0)), (2.6, (-4, 0)), (3.4, (0, 0), back_out)])
R_DROP = Track([(0, 0), (0.3, -3.0), (0.75, 1.0, ease_out), (1.0, -1.0), (2.6, -1.0), (3.4, 0)])
R_NECK = Track([(0, (0, 0, 0)), (0.3, (-8, 0, 0)), (0.75, (18, 0, 0), ease_out), (1.0, (12, 0, 0), ease_out), (1.6, (10, 14, 0)),
                (2.2, (10, -14, 0)), (2.6, (2, 0, 0)), (3.4, (0, 0, 0), back_out)])
R_SKULL = Track([(0, (0, 0, 0)), (0.3, (-10, 0, 0)), (0.75, (14, 0, 0), ease_out), (1.0, (2, 0, 0), ease_out), (1.6, (2, 10, -8)),
                 (2.2, (2, -10, 8)), (2.6, (-2, 0, 0)), (3.4, (0, 0, 0), back_out)])
R_JAW = Track([(0, 0), (0.3, -2), (0.75, -10), (1.0, -42, ease_out), (2.5, -38), (2.75, -2, ease_in), (3.4, 0)])
R_TAIL = Track([(0, 0), (0.3, -2), (0.75, 7, ease_out), (2.6, 5), (3.4, 0, back_out)])
def roar_pose(t):
    pose = {}
    bp, by = R_BODY(t)
    add(pose, "body", rot=(bp, by, 0), pos=(0, float(R_DROP(t)), 0))
    add(pose, "neck", rot=tuple(R_NECK(t)))
    sk = R_SKULL(t)
    # throat vibration while roaring
    vib = 1.2 * math.sin(2 * math.pi * t * 9) * (1.0 <= t <= 2.5)
    add(pose, "skull", rot=(sk[0] + vib, sk[1], sk[2]))
    add(pose, "jaw", rot=(float(R_JAW(t)) - vib, 0, 0))
    tv = float(R_TAIL(t))
    for k in range(1, 5):
        lag = max(0, t - 0.08 * k)
        add(pose, f"tail{k}", rot=(float(R_TAIL(lag)) * (0.6 + 0.2 * k) * 0.5, 0, 0))
    for s in ("l", "r"):
        add(pose, f"arm_{s}", rot=(-8 * smooth(t / 0.75) * (t < 2.6) - 8 * (1 - smooth((t - 2.6) / 0.8)) * (t >= 2.6), 0, 0))
        b = REST_BALL[s]
        solve_leg(S, pose, s, (b[1], b[2]), chain_angle(S, {}, [f"foot_{s}"]), 0.0)
    return pose

# ------------------------------------------------------------------ bite and shake
BITE_T = 2.0
B_NECK = Track([(0, (0, 0, 0)), (0.3, (10, 0, 0), ease_out), (0.45, (-16, 0, 0), ease_in), (0.6, (-12, 0, 0)), (0.8, (-12, 16, 0)), (0.98, (-12, -16, 0)),
                (1.16, (-12, 14, 0)), (1.32, (-12, -10, 0)), (1.5, (-8, 0, 0)), (2.0, (0, 0, 0), back_out)])
B_SKULL = Track([(0, (0, 0, 0)), (0.3, (8, 0, 0), ease_out), (0.45, (-10, 0, 0), ease_in), (0.6, (-6, 0, 0)), (0.8, (-6, 8, -10)), (0.98, (-6, -8, 10)),
                 (1.16, (-6, 7, -9)), (1.32, (-6, -5, 6)), (1.5, (-4, 0, 0)), (2.0, (0, 0, 0), back_out)])
B_JAW = Track([(0, 0), (0.3, -36, ease_out), (0.45, -40), (0.52, -4, ease_in), (1.5, -4), (1.7, -14), (2.0, 0)])
B_BODY = Track([(0, (0, 0)), (0.3, (-3, 0)), (0.45, (6, 0), ease_in), (0.8, (5, 3)), (0.98, (5, -3)), (1.16, (5, 3)), (1.5, (3, 0)), (2.0, (0, 0), back_out)])
B_PUSH = Track([(0, 0), (0.3, 2), (0.45, -6, ease_in), (1.5, -5), (2.0, 0)])
def bite_pose(t):
    pose = {}
    bp, by = B_BODY(t)
    add(pose, "body", rot=(bp, by, -by * 0.5), pos=(0, -1.5 * smooth(t / 0.45) * (t < 1.5) - 1.5 * (1 - smooth((t - 1.5) / 0.5)) * (t >= 1.5), float(B_PUSH(t))))
    add(pose, "neck", rot=tuple(B_NECK(t))); add(pose, "skull", rot=tuple(B_SKULL(t))); add(pose, "jaw", rot=(float(B_JAW(t)), 0, 0))
    for k in range(1, 5):
        lag = max(0, t - 0.07 * k)
        add(pose, f"tail{k}", rot=(-0.4 * B_BODY(lag)[0], -0.9 * k * B_BODY(lag)[1], 0))
    for s in ("l", "r"):
        b = REST_BALL[s]
        solve_leg(S, pose, s, (b[1], b[2]), chain_angle(S, {}, [f"foot_{s}"]), 0.0)
    return pose

# ------------------------------------------------------------------ sniff (idle fidget): raise the snout, three quick sniffs, look
SNIFF_T = 3.0
F_NECK = Track([(0, (0, 0)), (0.5, (12, 6)), (1.6, (12, 6)), (2.0, (6, -10), ease_out), (2.4, (6, -10)), (3.0, (0, 0))])
def sniff_pose(t):
    pose = {}
    np_, ny = F_NECK(t)
    add(pose, "body", rot=(-1.5 * smooth(t / 0.5) * (t < 2.4) - 1.5 * (1 - smooth((t - 2.4) / 0.6)) * (t >= 2.4), 0, 0))
    add(pose, "neck", rot=(np_ * 0.6, ny * 0.5, 0))
    sn = sum(math.exp(-((t - c) / 0.07) ** 2) for c in (0.75, 1.0, 1.25))   # three short sniffs
    add(pose, "skull", rot=(np_ * 0.6 + 2.5 * sn, ny * 0.5, -ny * 0.15))
    add(pose, "jaw", rot=(-1 - 1.5 * sn, 0, 0))
    for k in range(1, 5):
        add(pose, f"tail{k}", rot=(0.4 * k * smooth(t / 0.6) * (t < 2.4), -0.6 * k * math.sin(2 * math.pi * t / SNIFF_T - 0.4 * k), 0))
    for s in ("l", "r"):
        b = REST_BALL[s]
        solve_leg(S, pose, s, (b[1], b[2]), chain_angle(S, {}, [f"foot_{s}"]), 0.0)
    return pose

ANIMS = {"walk": (walk_pose, WALK_T, True), "idle": (idle_pose, IDLE_T, True), "roar": (roar_pose, ROAR_T, False),
         "attack": (bite_pose, BITE_T, False), "sniff": (sniff_pose, SNIFF_T, False)}
