"""Protoceratops animations, written for it from its own study (page "Protoceratops: estudo e modelo", the steps
Rodrigo approved on 01/11/2026).

Only the plumbing is shared (anim2: easing, the hind-leg IK, export). It is the first quadruped of the hand-made rigs,
so the gait, the forelimb IK and every pose are its own:
- a small, low, sturdy animal: short quick steps, the head low and nodding with the forefeet, the tall flat tail
  swinging behind;
- the walk is a lateral sequence (left hind, left fore, right hind, right fore), the run a trot (diagonal pairs);
- the baby runs on its hind legs (Slowiak 2019: the young were partly bipedal);
- it fights with the beak and holds on (the Fighting Dinosaurs fossil: a Protoceratops holding a Velociraptor's arm),
  shows the frill head-down, sways the sail of its tail, digs with the forefeet, shoves heads, freezes when a predator
  is near, scrapes a bed in the sand at noon and shakes the sand off like a dog.

Signs on this rig (checked on the model, anim/signs.png): body +x = nose up; neck/skull -x = down; jaw -x = open;
tail pitch + = down; yaw + = to its left; thigh/arm +x = the foot swings forward.
"""
import math
import os
import sys
_H = os.path.dirname(os.path.abspath(__file__))
_E = os.path.join(_H, "..", "_engine")
sys.path[:0] = [_H, _E]
import numpy as np
import geo
import proto as P
import protocera as PC
from anim2 import add, world, chain_angle, solve_leg, Track, smooth, ease_out, ease_in, back_out

W = lambda t, T: 2 * math.pi * t / T


def tr(*keys): return Track(keys)


def f(track, t): return float(track(t))


def window(t, a, b, fade=0.25):
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


def model():
    m = PC.build("male"); P.pack(m, PC.TEX_W); return m.spec()


S = model()
SIDES = ("l", "r")
TAILS = ("tail1", "tail2", "tail3", "tail4")
BEND = (1.0, 1.0, 0.9, 0.8)
BALL = {s: world(S, {}, f"toes_{s}") for s in SIDES}
REST_META = {s: chain_angle(S, {}, [f"foot_{s}"]) for s in SIDES}
WRIST = {s: world(S, {}, f"hand_{s}") for s in SIDES}
REST_HAND = {s: chain_angle(S, {}, [f"hand_{s}"]) for s in SIDES}
HIND = {s: {f"{b}_{s}" for b in ("thigh", "shin", "foot", "toes")} for s in SIDES}
FORE = {s: {f"{b}_{s}" for b in ("arm", "forearm", "hand")} for s in SIDES}
LEGS = set().union(*HIND.values(), *FORE.values())
STAND_DROP = 0.8        # the forelimb is all but straight at rest: the body sits this much lower so the elbow gives


def low_of(p, bones=None, skip=()):
    return min(q[:, 1].min() for c, q in geo.cube_points(S, p)
               if (bones is None or c["bone"] in bones) and c["bone"] not in skip)


# ------------------------------------------------------------------ forelimb IK (arm + forearm, wrist target)
def solve_arm(pose, s, target, pitch, iters=20):
    names = [f"arm_{s}", f"forearm_{s}"]
    th0 = np.array([pose.get(n, ([0, 0, 0],))[0][0] for n in names], float)
    th = th0 + np.array([-10.0, 20.0])      # start with the elbow bent back: the straight limb is a singular seed

    def res(th):
        q = dict(pose)
        for n, a in zip(names, th):
            e = q.get(n, ([0, 0, 0], [0, 0, 0])); q[n] = ([a, e[0][1], e[0][2]], e[1]) + tuple(e[2:])
        h = world(S, q, f"hand_{s}")
        return np.array([h[1] - target[0], h[2] - target[1], 0.004 * (th[0] - th0[0]), 0.004 * (th[1] - th0[1])]), q
    for _ in range(iters):
        r0, _q = res(th)
        if np.abs(r0[:2]).max() < 0.02: break
        J = np.zeros((4, 2))
        for j in range(2):
            d = np.zeros(2); d[j] = 0.25; J[:, j] = (res(th + d)[0] - r0) / 0.25
        th = th + np.linalg.solve(J.T @ J + 1e-2 * np.eye(2), -J.T @ r0)
    r0, q = res(th)
    cur = chain_angle(S, q, [f"hand_{s}"])
    e = q.get(f"hand_{s}", ([0, 0, 0], [0, 0, 0])); q[f"hand_{s}"] = ([e[0][0] + pitch - cur, e[0][1], e[0][2]], e[1]) + tuple(e[2:])
    pose.update(q)


def plant_h(p, s, dy=0.0, dz=0.0, meta=0.0, toe=0.0, clear=-0.05):
    b = BALL[s]; target = (b[1] + dy, b[2] + dz)
    for _ in range(4):
        solve_leg(S, p, s, target, REST_META[s] + meta, toe)
        if clear is None: break
        lo = low_of(p, HIND[s])
        if lo > clear - 0.02: break
        target = (target[0] + clear - lo, target[1])


def plant_f(p, s, dy=0.0, dz=0.0, pitch=0.0, clear=-0.05, scap=0.3):
    """the forefoot to the ground. scap: the shoulder blade slides with the foot (a share of dz), which is what lets
    the short straight forelimb keep up with the hind legs' stride"""
    w = WRIST[s]; target = (w[1] + dy, w[2] + dz)
    if scap: add(p, f"arm_{s}", pos=(0, -0.06 * abs(dz), scap * dz))
    for _ in range(4):
        solve_arm(p, s, target, REST_HAND[s] + pitch)
        if clear is None: break
        lo = low_of(p, FORE[s])
        if lo > clear - 0.02: break
        target = (target[0] + clear - lo, target[1])


HEADB = ("neck", "head", "skull", "jaw", "frill")


def lift_head(p, clear=0.3):
    """a head brought down by several layers must stop at the ground: raise the neck until the beak clears it"""
    for _ in range(30):
        if low_of(p, HEADB) >= clear: break
        add(p, "neck", rot=(1.5, 0, 0))
    return p


def stand(p, fore=(0, 0), hind=(0, 0)):
    """all four feet on the ground (fore/hind: dz of the feet, + = back)"""
    lift_head(p)
    for s in SIDES:
        plant_h(p, s, 0, hind[0] if s == "l" else hind[1])
        plant_f(p, s, 0, fore[0] if s == "l" else fore[1])
    return p


# ------------------------------------------------------------------ helpers
def head(p, pitch=0.0, yaw=0.0, roll=0.0, k=0.6):
    """a head movement spread over the neck (k) and the skull"""
    add(p, "neck", rot=(pitch * k, yaw * k, roll * 0.3))
    add(p, "skull", rot=(pitch * (1 - k), yaw * (1 - k), roll * 0.7))


def jaw(p, a): add(p, "jaw", rot=(a, 0, 0))


def tail(p, yaw=0.0, pitch=0.0):
    for b, k in zip(TAILS, BEND): add(p, b, rot=(pitch * k, yaw * k, 0))


def tail_wave(p, t, Tc, yaw, pitch=0.0, lag=0.6, ph=0.0):
    for i, (b, k) in enumerate(zip(TAILS, BEND)):
        a = W(t, Tc) - lag * i + ph
        add(p, b, rot=(pitch * k * math.sin(2 * a - 0.6), yaw * k * math.sin(a), 0))


def breathe(p, t, T=2.6, amp=1.0, drop=STAND_DROP):
    br = math.sin(W(t, T))
    add(p, "body", rot=(0.5 * amp * br, 0, 0), pos=(0, -drop - 0.25 * amp * (1 + br), 0))
    head(p, -0.5 * amp * br)
    return br


def shift_to_ground(p, skip=()):
    lo = low_of(p, skip=skip); add(p, "root", pos=(0, -lo, 0)); return p


# ------------------------------------------------------------------ gaits
LATERAL = {"lh": 0.0, "lf": 0.75, "rh": 0.5, "rf": 0.25}      # walk: LH, LF, RH, RF
TROT = {"lh": 0.0, "rf": 0.0, "rh": 0.5, "lf": 0.5}            # run: diagonal pairs


def gait(t, Tc, stride, duty, lift, bob, feet, lean=0.0, drop=STAND_DROP, hd=0.0, tail_amp=1.0, roll=1.0, nod=1.0,
         flift=None):
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    bp = 0.7 * nod * math.sin(2 * w - 0.5)
    add(p, "body", rot=(lean + bp, 1.6 * roll * math.sin(w), 2.2 * roll * math.sin(w + 0.4)),
        pos=(0, -drop - bob * (0.5 + 0.5 * math.cos(2 * w - 0.8)), 0))
    add(p, "neck", rot=(hd * 0.6 - bp - lean * 0.7 + 1.6 * nod * math.sin(2 * w - 1.4), -1.4 * roll * math.sin(w - 0.5), 0))
    add(p, "skull", rot=(hd * 0.4 - lean * 0.3 + 1.2 * nod * math.sin(2 * w - 2.0), -0.6 * roll * math.sin(w - 1.0), -1.6 * roll * math.sin(w)))
    for i, (b, k) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(-lean * 0.25 + 0.9 * math.sin(2 * w - 1.0 - 0.5 * i), -3.4 * tail_amp * k * math.sin(w - 0.9 - 0.55 * i), 0))
    flift = lift * 0.85 if flift is None else flift
    for foot, o in feet.items():
        s, kind = foot[0], foot[1]
        u = (ph + o) % 1.0
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0; clear = -0.05
            heel = smooth(max(0.0, (st - 0.6) / 0.4)); sw = 0.0
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e; heel = 0.0
            ly = (lift if kind == "h" else flift) * math.sin(math.pi * min(1, sw * 1.1)) ** 1.2
            clear = 0.8 * math.sin(math.pi * sw) ** 0.5
        if kind == "h":
            meta = 24 * heel + 24 * (1 - smooth(sw / 0.4)) * (sw > 0) - 16 * math.sin(math.pi * sw)
            toe = -22 * math.sin(math.pi * min(1, sw * 1.1)) + 4 * smooth((sw - 0.7) / 0.3) * (sw > 0)
            plant_h(p, s, ly, dz, meta, toe, clear)
        else:
            pitch = -22 * heel - 34 * math.sin(math.pi * min(1, sw * 1.15))
            plant_f(p, s, ly, dz, pitch, clear)
    return p


WALK = (1.0, 30, 0.66, 4.5, 0.5)
TROTP = (0.56, 56, 0.42, 6.0, 1.2)
BIPED = (0.44, 48, 0.38, 6.5, 1.0)


def walk(t):
    return gait(t, *WALK, LATERAL, hd=-2)


def run(t):
    """a trot: diagonal pairs, the body low and level, the head held out in front"""
    return gait(t, *TROTP, TROT, lean=-1.5, drop=2.4, hd=-4, roll=0.6, tail_amp=0.7)


def run_biped(t):
    """the baby's run: up on its hind legs, the forelegs tucked, the tail held out behind as a counterweight"""
    Tc, stride, duty, lift, bob = BIPED
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    lean = 38
    add(p, "body", rot=(lean + 1.5 * math.sin(2 * w - 0.6), 3 * math.sin(w), 3 * math.sin(w + 0.4)),
        pos=(0, -1.2 - bob * (0.5 + 0.5 * math.cos(2 * w - 0.8)), 0))
    head(p, -lean * 0.85 + 2 * math.sin(2 * w - 1.6), -3 * math.sin(w - 0.6))
    for i, (b, k) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(-22 * k + 1.2 * math.sin(2 * w - 1.0 - 0.5 * i), -4 * k * math.sin(w - 0.9 - 0.5 * i), 0))
    for s in SIDES:
        add(p, f"arm_{s}", rot=(-55 + 6 * math.sin(w + (0 if s == "l" else math.pi)), 0, 0))
        add(p, f"forearm_{s}", rot=(95, 0, 0)); add(p, f"hand_{s}", rot=(-40, 0, 0))
    for s, o in (("l", 0.0), ("r", 0.5)):
        u = (ph + o) % 1.0
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0; clear = -0.05
            meta = 26 * smooth(max(0, (st - 0.55) / 0.45)); toe = 0.0
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e
            ly = lift * math.sin(math.pi * min(1, sw * 1.1)) ** 1.2
            meta = 26 * (1 - smooth(sw / 0.45)) - 18 * math.sin(math.pi * sw)
            toe = -26 * math.sin(math.pi * min(1, sw * 1.1)); clear = 0.8 * math.sin(math.pi * sw) ** 0.5
        plant_h(p, s, ly, dz - 2, meta, toe, clear)
    return p


def swim(t):
    """paddling: the legs row in pairs, the tall tail sculls, the head held up out of the water"""
    Tc = 1.4; w = W(t, Tc); p = {}
    add(p, "body", rot=(5 + 1.5 * math.sin(2 * w), 2 * math.sin(w), 3 * math.sin(w + 0.5)), pos=(0, 0.8 * math.sin(2 * w - 1), 0))
    head(p, 14 - 1.5 * math.sin(2 * w - 1.3), -2 * math.sin(w - 0.8))
    tail_wave(p, t, Tc, 13, 1.0, lag=0.7)
    for s, o in (("l", 0.0), ("r", math.pi)):
        add(p, f"thigh_{s}", rot=(-18 + 26 * math.sin(w + o), 0, 0))
        add(p, f"shin_{s}", rot=(-10 + 22 * math.sin(w + o - 1.2), 0, 0))
        add(p, f"foot_{s}", rot=(10 + 20 * math.sin(w + o - 1.8), 0, 0))
        add(p, f"arm_{s}", rot=(-8 + 24 * math.sin(w + o + math.pi * 0.5), 0, 0))
        add(p, f"forearm_{s}", rot=(14 + 18 * math.sin(w + o + math.pi * 0.5 - 1.2), 0, 0))
        add(p, f"hand_{s}", rot=(-10 + 20 * math.sin(w + o + math.pi * 0.5 - 1.8), 0, 0))
    return p


# ------------------------------------------------------------------ lying down (sit, sleep, knocked out)
FOLD_F = (-55.0, 131.0, -80.0)     # lying: the upper arm back, the forearm flat on the ground pointing forward
BELLY_STAND = None


def lift_tail(p, clear=0.0):
    """a tail laid down must rest on the ground, not in it: lift each bone from the root out until it clears"""
    for i, b in enumerate(TAILS):
        for _ in range(20):
            if low_of(p, set(TAILS[i:])) >= clear: break
            add(p, b, rot=(-1.5, 0, 0))
    return p


def lie(p, k=1.0, pitch=0.0, sink=0.1):
    """the belly down on the ground, the hind legs folded under, the forearms flat in front. k = how far down
    (0 standing, 1 lying): the body comes down to the ground by the belly, the hind legs fold by IK and the forelegs
    blend from the planted foot into the fold, so wake/scrape/death go through it"""
    global BELLY_STAND
    if BELLY_STAND is None:
        q = {}; add(q, "body", pos=(0, -STAND_DROP, 0)); BELLY_STAND = low_of(q, {"body"})
    add(p, "body", rot=(pitch * k, 0, 0), pos=(0, -STAND_DROP, 0))
    b = low_of(p, {"body"}); goal = BELLY_STAND * (1 - k) - sink * k
    add(p, "body", pos=(0, goal - b, 0))
    tail(p, pitch=-2 * k)
    wf = smooth((k - 0.3) / 0.7)
    for s in SIDES:
        plant_h(p, s, 0.0, 7 * k, meta=-30 * k, toe=0.0, clear=0.0)
        plant_f(p, s, 0.0, -5 * k, pitch=0.0, clear=0.0)
        if wf > 0:
            for bone, fa in zip(("arm", "forearm", "hand"), FOLD_F):
                e = p[f"{bone}_{s}"]; e[0][0] = e[0][0] * (1 - wf) + fa * wf
    lift_tail(p)
    return p


def lie_head_rest(p, k=1.0, side=1.0):
    """asleep: the neck laid down and turned back along the flank, the chin on the ground, the tail curled forward"""
    head(p, -14 * k, 34 * k * side, -14 * k * side, k=0.65)
    add(p, "skull", rot=(-6 * k, 10 * k * side, -6 * k * side))
    for i, b in enumerate(TAILS): add(p, b, rot=(2 * k, 12 * k * side * (0.6 + 0.2 * i), 0))


def ko_pose(p, k=1.0, t=0.0):
    """knocked out: on its side, the legs loose, the head down"""
    br = math.sin(W(t, 3.4))
    add(p, "body", rot=(0, 0, 84 * k), pos=(0, -8.0 * k, 0))
    head(p, -6 * k + 0.6 * br, 0, 12 * k)
    jaw(p, -4 * k)
    tail(p, yaw=0, pitch=-2 * k)
    for s, sg in (("l", 1), ("r", -1)):
        add(p, f"thigh_{s}", rot=(10 * k, 0, -8 * k * sg)); add(p, f"shin_{s}", rot=(-10 * k, 0, 0)); add(p, f"foot_{s}", rot=(20 * k, 0, 0))
        add(p, f"arm_{s}", rot=(18 * k, 0, -6 * k * sg)); add(p, f"forearm_{s}", rot=(-8 * k, 0, 0)); add(p, f"hand_{s}", rot=(20 * k, 0, 0))
    add(p, "body", pos=(0, 0.25 * br * k, 0))
    return p


def sit(t):
    """lying awake: chest down, the head up and watching; a slow look to one side"""
    p = {}; br = math.sin(W(t, 3.2))
    lie(p)
    add(p, "body", rot=(0.4 * br, 0, 0), pos=(0, 0.12 * (1 + br), 0))
    a = window(t, 2.2, 3.6, 0.5)
    head(p, 4 - 0.5 * br, 22 * a)
    tail(p, yaw=4 * a)
    return lift_tail(lift_head(p, 0.0))


def sleep(t):
    p = {}; br = math.sin(W(t, 4.5))
    lie(p, sink=0.0)
    add(p, "body", rot=(0.5 * br, 0, 0), pos=(0, 0.12 * (1 + br), 0))
    lie_head_rest(p)
    head(p, -0.6 * br)
    return lift_tail(lift_head(p, 0.0))


def huddle(t):
    """the baby's sleep: curled tight, the head tucked against the flank, the tail wrapped round to the nose"""
    p = {}; br = math.sin(W(t, 3.0))
    lie(p)
    add(p, "body", rot=(0.4 * br, 4, 0), pos=(0, 0.12 * (1 + br), 0))
    head(p, -18, 58, -20, k=0.7)
    add(p, "skull", rot=(-6, 22, -8))
    for i, b in enumerate(TAILS): add(p, b, rot=(3, 22 * (0.7 + 0.15 * i), 0))
    return lift_tail(lift_head(p, 0.0))


def wake_sleep(t):
    """wakes: lifts the head and looks, then the chest, then gets up from behind"""
    p = {}
    kh = f(tr((0, 1), (0.7, 0, smooth), (2.0, 0)), t)
    kb = f(tr((0, 1), (0.6, 1), (1.6, 0, smooth), (2.0, 0)), t)
    fr = f(tr((0, 0), (0.6, 0), (1.0, 1, smooth), (1.6, 0, smooth), (2.0, 0)), t)
    lie(p, kb, pitch=6 * fr / max(kb, 0.3))
    lie_head_rest(p, kh)
    head(p, 4 * (1 - kh) * kb, 10 * window(t, 0.6, 1.2, 0.2))
    return lift_tail(lift_head(p, 0.0))


def knocked_out(t):
    return shift_to_ground(ko_pose({}, 1.0, t))


def blend(a, b, w):
    """per-bone linear mix of two poses (rotations and offsets)"""
    out = {}
    for bone in set(a) | set(b):
        ea = a.get(bone, ([0, 0, 0], [0, 0, 0])); eb = b.get(bone, ([0, 0, 0], [0, 0, 0]))
        out[bone] = ([ea[0][i] * (1 - w) + eb[0][i] * w for i in range(3)], [ea[1][i] * (1 - w) + eb[1][i] * w for i in range(3)])
    return out


def wake(t):
    """from the knocked-out pose: rolls onto its belly, shakes the head, gets up front first"""
    roll = f(tr((0, 1), (0.3, 1), (1.0, 0, smooth), (3.0, 0)), t)
    if roll > 0:
        return shift_to_ground(blend(lift_tail(lift_head(lie({}), 0.0)), ko_pose({}, 1.0), roll))
    p = {}
    ly = f(tr((0, 1), (1.8, 1), (2.6, 0, smooth), (3.0, 0)), t)
    lie(p, ly, pitch=8 * window(t, 1.9, 2.4, 0.2))
    sh = window(t, 1.1, 1.8, 0.12)
    head(p, 4 * sh, 0, 22 * sh * math.sin(W(t, 0.24)))
    return lift_tail(lift_head(p, 0.0))


def _going_down(t):
    p = {}
    st = window(t, 0.0, 0.5, 0.15)
    down = f(tr((0, 0), (0.45, 0), (1.0, 1, ease_in), (2.4, 1)), t)
    add(p, "body", rot=(-14 * math.sin(math.pi * down), 4 * st * math.sin(W(t, 0.5)), 6 * st), pos=(0, 0, 1.5 * st))
    lie(p, down)
    head(p, 10 * st - 14 * down, -10 * st)
    jaw(p, -10 * st)
    return lift_tail(lift_head(p, 0.0))


_DOWN = []


def death(t):
    """staggers, the forelegs give way, it goes down on its chest and rolls onto its side; ends as knocked_out"""
    if t <= 1.0:
        return _going_down(t)
    if not _DOWN: _DOWN.append(_going_down(1.0))
    roll = f(tr((1.0, 0), (1.6, 1, ease_in), (1.75, 0.96), (1.9, 1, smooth), (2.4, 1)), t)
    return shift_to_ground(blend(_DOWN[0], ko_pose({}, 1.0), roll))


# ------------------------------------------------------------------ standing / everyday
def idle(t):
    """breathing, the head low; a look to the left, a look to the right, a sniff at the ground"""
    p = {}; br = breathe(p, t, 3.0)
    a = window(t, 1.2, 2.6, 0.35); b = window(t, 3.6, 4.6, 0.3); c = window(t, 5.0, 5.8, 0.25)
    head(p, -10 * c + 2 * a, 24 * a - 20 * b, -4 * a + 3 * b)
    jaw(p, -1.5 * c * max(0, math.sin(W(t, 0.3))))
    tail_wave(p, t, 6.0, 3.0, 0.4)
    add(p, "body", rot=(-1.5 * c, 3 * a - 2 * b, 0))
    return stand(p)


def hurt(t):
    p = {}
    k = f(tr((0, 0), (0.07, 1, ease_out), (0.5, 0, smooth)), t)
    add(p, "body", rot=(4 * k, -6 * k, -4 * k), pos=(0, -STAND_DROP - 0.5 * k, 1.8 * k))
    head(p, 10 * k, 14 * k, 8 * k); jaw(p, -8 * k)
    tail(p, yaw=8 * k, pitch=-4 * k)
    return stand(p)


def attack(t):
    """the beak bite: draws the head back with the beak open, snaps forward and down (the hit at 0.38 s), a short
    tug, lets go"""
    p = {}
    back = f(tr((0, 0), (0.22, 1, ease_out), (0.32, 0, ease_in), (0.8, 0)), t)
    hit = f(tr((0, 0), (0.24, 0), (0.38, 1, ease_in), (0.5, 1), (0.8, 0, smooth)), t)
    tug = window(t, 0.42, 0.58, 0.06)
    add(p, "body", rot=(3 * back - 5 * hit, 0, 0), pos=(0, -STAND_DROP - 1.2 * hit, 1.5 * back - 3.5 * hit))
    head(p, 10 * back - 14 * hit + 6 * tug, -4 * tug, 8 * tug)
    jaw(p, f(tr((0, -2), (0.2, -26, ease_out), (0.34, -28), (0.4, -2, ease_in), (0.6, -2), (0.8, 0)), t))
    tail(p, yaw=3 * tug, pitch=-3 * back + 2 * hit)
    return stand(p, fore=(-1.5 * hit, -1.5 * hit))


def bite_hold(t):
    """the Fighting Dinosaurs grip: bites and does not let go; braced on all fours it pulls back and wrenches the head
    side to side three times, then lets go and steps back"""
    p = {}
    hit = f(tr((0, 0), (0.15, 0), (0.32, 1, ease_in), (1.8, 1), (2.2, 0, smooth)), t)
    pull = f(tr((0, 0), (0.35, 0), (0.55, 1, ease_out), (1.75, 1), (2.2, 0, smooth)), t)
    wr = window(t, 0.6, 1.7, 0.12) * math.sin(W(t - 0.6, 0.38))
    add(p, "body", rot=(-4 * hit + 3 * pull, 4 * wr, -5 * wr), pos=(0, -STAND_DROP - 1.6 * pull, -3 * hit + 3.5 * pull))
    head(p, -12 * hit + 4 * pull, -12 * wr, 18 * wr)
    jaw(p, f(tr((0, -2), (0.15, -24, ease_out), (0.3, -2, ease_in), (1.8, -2), (1.92, -16, ease_out), (2.2, 0)), t))
    tail(p, yaw=-6 * wr, pitch=-4 * pull)
    return stand(p, fore=(-3 * pull, -3 * pull), hind=(-2 * pull, -2 * pull))


def eat(t):
    """takes a bite from the hand or the ground: head down, bites and pulls up, three shearing chews"""
    p = {}
    dn = f(tr((0, 0), (0.45, 1, smooth), (0.85, 1), (1.05, 0.45, ease_out), (2.2, 0.45), (2.6, 0, smooth)), t)
    breathe(p, t, 2.6, 0.6)
    add(p, "body", rot=(-5 * dn, 0, 0), pos=(0, -1.0 * dn, 0))
    head(p, -30 * dn - 6 * window(t, 0.85, 1.0, 0.08))
    chew = window(t, 1.05, 2.15, 0.1) * max(0, math.sin(W(t - 1.05, 0.36)))
    jaw(p, f(tr((0, 0), (0.5, -14, ease_out), (0.7, -1, ease_in), (2.6, 0)), t) - 7 * chew)
    add(p, "skull", rot=(0, 0, 3 * chew))
    tail_wave(p, t, 2.6, 2.0)
    return stand(p, fore=(-2 * dn, -2 * dn))


def graze(t):
    """crops low plants: the head at the ground, three bites with a sideways tug, then up to chew"""
    p = {}
    dn = f(tr((0, 0), (0.5, 1, smooth), (2.1, 1), (2.6, 0.3, smooth), (3.2, 0, smooth)), t)
    breathe(p, t, 3.2, 0.6)
    add(p, "body", rot=(-6 * dn, 0, 0), pos=(0, -1.2 * dn, 0))
    tug = sum(window(t, c, c + 0.18, 0.07) for c in (0.75, 1.25, 1.75))
    side = sum(window(t, c, c + 0.18, 0.07) * sg for c, sg in ((0.75, 1), (1.25, -1), (1.75, 1)))
    head(p, -34 * dn + 5 * tug, 10 * side, 6 * side)
    bites = sum(window(t, c - 0.15, c, 0.06) for c in (0.75, 1.25, 1.75))
    chew = window(t, 2.2, 3.1, 0.1) * max(0, math.sin(W(t - 2.2, 0.32)))
    jaw(p, -14 * bites - 6 * chew)
    tail_wave(p, t, 3.2, 2.5)
    return stand(p, fore=(-2.5 * dn, -2.5 * dn))


def rake(p, s, u, period=0.5):
    """one stroke of a hind foot's shovel claws (u = time since the stroke began): the foot comes up and forward
    under the belly, bites into the ground and rakes back hard, throwing the sand out behind"""
    ph = u / period
    if ph < 0.4:
        e = smooth(ph / 0.4); dz = 2 - 9 * e; dy = 3.5 * math.sin(math.pi * e); meta = -10 * e; toe = -20 * math.sin(math.pi * e)
    elif ph < 0.85:
        e = smooth((ph - 0.4) / 0.45); dz = -7 + 15 * e; dy = 0.0; meta = 10 * e; toe = 0.0
    else:
        e = smooth((ph - 0.85) / 0.15); dz = 8 - 6 * e; dy = 1.5 * math.sin(math.pi * e); meta = 10 - 10 * e; toe = -15 * math.sin(math.pi * e)
    plant_h(p, s, dy, dz, meta, toe, clear=-0.05 if dy < 0.05 else 0.4)


def dig_strokes(p, t, t0, n, period=0.5):
    """n alternating strokes of the hind feet from t0; the foot not raking stands"""
    for s, o in (("l", 0.0), ("r", period)):
        busy = False
        for i in range(n):
            u = t - t0 - o - 2 * period * i
            if 0 <= u < period:
                rake(p, s, u, period); busy = True
        if not busy: plant_h(p, s)


def dig(t):
    """digs with the shovel claws of the hind feet: four strokes, left and right in turn, throwing the sand back; the
    weight forward on the forelegs, the head up and watching (from the study: the hind claws were flat, spade-like)"""
    p = {}
    k = f(tr((0, 0), (0.3, 1, smooth), (2.4, 1), (2.6, 0, smooth)), t)
    add(p, "body", rot=(-3 * k, 0, 0), pos=(0, -STAND_DROP - 0.8 * k, -1.5 * k))
    br = math.sin(W(t, 0.5))
    head(p, 6 * k + 1.5 * br * k, 14 * window(t, 0.9, 1.6, 0.25) - 10 * window(t, 1.7, 2.3, 0.25))
    tail(p, pitch=-3 * k)
    tail_wave(p, t, 0.5, 2.5 * k)
    add(p, "body", rot=(0, 0, 2 * k * math.sin(W(t - 0.35, 1.0))))
    for s in SIDES: plant_f(p, s, 0, -1.5 * k)
    dig_strokes(p, t, 0.35, 2, 0.5)
    return p


def beg(t):
    """asks for food: the head up to the owner, pawing the ground with one forefoot, then the other"""
    p = {}; br = breathe(p, t, 2.0)
    head(p, 14 + 2 * br, 6 * math.sin(W(t, 2.0)), 4 * math.sin(W(t, 2.0)))
    jaw(p, -3 * window(t, 0.9, 1.1, 0.06))
    tail_wave(p, t, 2.0, 5.0)
    for s, c in (("l", 0.45), ("r", 1.45)):
        k = window(t, c - 0.2, c + 0.2, 0.15)
        plant_f(p, s, 4.0 * k, -3.0 * k + 3.0 * window(t, c, c + 0.25, 0.1) * k, -30 * k, clear=-0.05 if k < 0.05 else 0.4)
    for s in SIDES: plant_h(p, s)
    return p


def tame(t):
    """accepts its owner: lowers the head and shows the top of the frill to them, holds, lifts it calmly"""
    p = {}
    k = f(tr((0, 0), (0.6, 1, ease_out), (1.6, 1), (2.4, 0, smooth)), t)
    breathe(p, t, 2.4, 0.5)
    add(p, "body", rot=(-4 * k, 0, 0), pos=(0, -1.0 * k, 0))
    head(p, -26 * k, 0, 0, k=0.4)
    tail(p, pitch=4 * k)
    return stand(p, fore=(-1.5 * k, -1.5 * k))


# ------------------------------------------------------------------ only the Protoceratops
def frill_show(t):
    """shows the frill to a rival: nose down so the frill stands up like a shield, a slow turn to show it to one side,
    then the other, and two nods"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (2.2, 1), (2.6, 0, smooth)), t)
    sw = window(t, 0.5, 1.2, 0.25) - window(t, 1.3, 2.0, 0.25)
    nod = sum(window(t, c, c + 0.12, 0.06) for c in (1.05, 2.05))
    breathe(p, t, 1.6, 0.8)
    add(p, "body", rot=(-3 * k, 6 * sw, -3 * sw), pos=(0, -1.0 * k, 0))
    head(p, -16 * k - 6 * nod, 22 * sw, -10 * sw, k=0.35)
    add(p, "skull", rot=(-10 * k, 0, 0))
    tail(p, yaw=-6 * sw, pitch=-3 * k)
    return stand(p, fore=(-2 * k, -2 * k))


def sail_sway(t):
    """the tall tail lifted and swung in a slow wide arc, the sail turned to the side to be seen"""
    p = {}
    k = f(tr((0, 0), (0.35, 1, ease_out), (2.0, 1), (2.4, 0, smooth)), t)
    breathe(p, t, 2.4, 0.6)
    for i, (b, kk) in enumerate(zip(TAILS, BEND)):
        a = W(t - 0.3, 1.6) - 0.55 * i
        add(p, b, rot=(-5 * k * kk, 15 * k * kk * math.sin(a), 0))
    add(p, "body", rot=(0, -3 * k * math.sin(W(t - 0.3, 1.6)), 2 * k * math.sin(W(t - 0.3, 1.6))))
    head(p, 2 * k, 14 * window(t, 0.6, 1.8, 0.3))
    return stand(p)


def scrape_rest(t):
    """noon on the sand: scrapes a shallow bed with the hind claws, turns a little, lies down in it and wriggles in;
    ends lying as in sit"""
    p = {}
    ly = f(tr((0, 0), (1.4, 0), (2.4, 1, smooth), (3.6, 1)), t)
    wr = window(t, 2.4, 3.1, 0.15) * math.sin(W(t - 2.4, 0.35))
    turn = window(t, 1.2, 2.6, 0.3)
    add(p, "body", rot=(0, 8 * turn, 3 * wr))
    if ly < 0.02:
        dn = f(tr((0, 0), (0.2, 1, smooth), (1.2, 1), (1.4, 0, smooth)), t)
        add(p, "body", rot=(-3 * dn, 0, 0), pos=(0, -STAND_DROP - 0.8 * dn, -1.5 * dn))
        head(p, 4 * dn, -10 * window(t, 0.5, 1.1, 0.2))
        for s in SIDES: plant_f(p, s, 0, -1.5 * dn)
        dig_strokes(p, t, 0.15, 1, 0.45)
    else:
        lie(p, ly)
        head(p, 4 * ly, 0)
    tail(p, yaw=-8 * turn + 5 * wr)
    return lift_tail(lift_head(p, 0.0))


def sand_shake(t):
    """shakes the sand off like a dog: a wave from the head down the body to the tip of the tail"""
    p = {}
    env = window(t, 0.15, 1.3, 0.2)
    w = W(t, 0.2)
    breathe(p, t, 1.6, 0.5)
    head(p, -4 * env, 6 * env * math.sin(w), 28 * env * math.sin(w))
    add(p, "body", rot=(0, 3 * env * math.sin(w - 1.0), 9 * env * math.sin(w - 1.0)))
    for i, (b, kk) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(0, 9 * env * kk * math.sin(w - 1.8 - 0.6 * i), 0))
    jaw(p, -2 * env)
    return stand(p)


def freeze(t):
    """a predator near: it stops dead, the head jerks up toward it, the body low; utterly still, then lets go"""
    p = {}
    k = f(tr((0, 0), (0.12, 1, ease_out), (1.9, 1), (2.4, 0, smooth)), t)
    twitch = window(t, 1.0, 1.08, 0.03)
    add(p, "body", rot=(1 * k, 0, 0), pos=(0, -STAND_DROP - 1.4 * k, 0))
    head(p, 12 * k + 2 * twitch, 12 * k - 5 * twitch, -3 * k)
    tail(p, pitch=3 * k)
    if k < 0.98:
        add(p, "body", rot=(0.4 * math.sin(W(t, 2.4)), 0, 0))
    return stand(p)


def shove(t):
    """head-to-head with a rival: the frill lowered like a shield, two hard shoves forward from braced hind legs"""
    p = {}
    k = f(tr((0, 0), (0.3, 1, ease_out), (1.5, 1), (1.8, 0, smooth)), t)
    push = sum(window(t, c, c + 0.22, 0.1) for c in (0.45, 0.95))
    add(p, "body", rot=(-4 * k - 2 * push, 0, 0), pos=(0, -STAND_DROP - 1.6 * k, -4.5 * push))
    head(p, -10 * k + 3 * push, 0, 0, k=0.5)
    add(p, "skull", rot=(-12 * k, 0, 0))
    tail(p, pitch=-3 * push)
    return stand(p, fore=(-2 * k, -2 * k), hind=(2 * k, 2 * k))


ANIMS = {
    "idle": (idle, 6.0, True, "Parado", "respira de cabeça baixa; olha para um lado, para o outro, fareja o chão"),
    "walk": (walk, WALK[0], True, "Movimento", "passo de quadrúpede: traseira, dianteira do mesmo lado, cabeça balançando"),
    "run": (run, TROTP[0], True, "Movimento", "trote: patas em diagonal, corpo baixo"),
    "run_biped": (run_biped, BIPED[0], True, "Só dele", "o filhote corre em duas patas, as da frente encolhidas"),
    "swim": (swim, 1.4, True, "Movimento", "rema com as quatro patas, a cauda alta ajuda"),
    "attack": (attack, 0.8, False, "Combate", "bicada: puxa a cabeça, bica para a frente e para baixo"),
    "bite_hold": (bite_hold, 2.2, False, "Só dele", "morde e não solta: firma as patas e torce a cabeça (o fóssil Fighting Dinosaurs)"),
    "shove": (shove, 1.8, False, "Só dele", "empurrão: crista abaixada como escudo, dois empurrões contra o rival"),
    "frill_show": (frill_show, 2.6, False, "Só dele", "mostra a crista: focinho baixo, crista em pé, vira de um lado e do outro"),
    "sail_sway": (sail_sway, 2.4, False, "Só dele", "ergue a cauda alta e balança devagar, mostrando a vela"),
    "freeze": (freeze, 2.4, False, "Só dele", "predador perto: para seco, cabeça alta, imóvel"),
    "hurt": (hurt, 0.5, False, "Combate", "ao levar dano"),
    "death": (death, 2.4, False, "Combate", "cambaleia, as patas da frente cedem, cai de lado"),
    "eat": (eat, 2.6, False, "Comer", "bica, puxa e mastiga com o bico"),
    "graze": (graze, 3.2, False, "Comer", "corta planta baixa com puxões de lado"),
    "dig": (dig, 2.6, False, "Só dele", "cava com as garras de pá das patas de trás, cabeça erguida vigiando"),
    "sand_shake": (sand_shake, 1.6, False, "Só dele", "sacode a areia como um cachorro, da cabeça à cauda"),
    "scrape_rest": (scrape_rest, 3.6, False, "Só dele", "meio-dia na areia: cava uma cova rasa com as patas de trás e deita nela"),
    "sit": (sit, 6.0, True, "Descanso", "deitado acordado, cabeça erguida"),
    "sleep": (sleep, 9.0, True, "Descanso", "dorme com a cabeça virada para o flanco e a cauda dobrada"),
    "huddle": (huddle, 6.0, True, "Só dele", "o filhote dorme enrolado, cabeça no flanco"),
    "wake_sleep": (wake_sleep, 2.0, False, "Descanso", "acorda: cabeça, peito, depois o quadril"),
    "knocked_out": (knocked_out, 3.4, True, "Descanso", "nocauteado, deitado de lado"),
    "wake": (wake, 3.0, False, "Descanso", "acorda do nocaute: rola, sacode a cabeça, levanta"),
    "beg": (beg, 2.0, True, "Domado", "pede comida: olha o dono e cava o chão com uma pata, depois a outra"),
    "tame": (tame, 2.4, False, "Domado", "abaixa a cabeça e mostra a crista ao dono"),
}


# 06/11: the fluid set and the fighting set (protoflow.py, on the ceratopsians' triceratops/ceraflow.py): the names
# above that it remakes are rebound here, the new ones (frill_shove, guard, strafes, turns, feint, block, recoil,
# submit, lie_down, get_up, idle_tired, walk_tired) added
import protoflow as FLOW  # noqa: E402
ANIMS = dict(ANIMS)
ANIMS.update(FLOW.ANIMS)

# 06/11: the epic duel's three moves (protofight.py): lunge (bite 0.50 s), parry (counter bite 0.60 s), stagger
import protofight as FIGHT  # noqa: E402
ANIMS.update(FIGHT.ANIMS)
