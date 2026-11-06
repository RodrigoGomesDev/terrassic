"""Triceratops animations, written for it from its own study (page "Triceratops: estudo e modelo", approved by Rodrigo on
02/11/2026, the decisions of the 1.5 package delegated to the threads).

Shared with the Protoceratops is only the plumbing (the forelimb IK, the plant helpers, the lying blend, bake and
export); every pose and every cycle is the Triceratops' own, from what a 9 m, 6-12 t horned grazer would do:
- a heavy walker: a slow four-beat walk (left hind, left fore, right hind, right fore) with the hips rolling over the
  standing leg and the big head held STILL (the neck works against the body so the horns stay level);
- the run is a rhino's gallop (Paul & Christiansen 2000 gave the big ceratopsids a rhino's gait): hind pair, fore pair,
  the back rocking once a stride; the charge is the same gallop with the head down and the horns level;
- it fights with the horns, not the beak: the attack is a toss (head down, a step in, the horns hooked up and to one
  side), a sweep to the side now and then; two males lock horns and twist (Farke 2004 fitted real skulls together);
- it turns to face a predator by walking its hind end round its planted forefeet (the pivot) and stamps a forefoot
  before a charge;
- it feeds low and tough: plows the beak along the ground for roots and ferns, and shears a branch with the scissor
  cheek teeth (the jaw goes straight up and down, not sideways);
- rests a hind leg like a horse in the idle, wallows in mud on one flank and then the other, sleeps like a cow (belly
  down, the heavy head laid on its cheek, the frill up), and gets up FRONT FIRST;
- dying, the head goes down first and plows the ground, the forelegs buckle onto the wrists, then it rolls;
- the calf butts (butt_play), short hops with the head down, the play of young horned animals.

Signs on this rig (as on the Protoceratops' engine): body +x = nose up; neck/skull -x = down; jaw -x = open; tail pitch
+ = down; yaw + = to its left; thigh/arm +x = the foot swings forward.
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
import tricera as TC
from anim2 import add, world, chain_angle, solve_leg, Track, smooth, ease_out, ease_in

W = lambda t, T: 2 * math.pi * t / T


def tr(*keys): return Track(keys)


def f(track, t): return float(track(t))


def window(t, a, b, fade=0.25):
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


def model():
    m = TC.build("male"); P.pack(m, TC.TEX_W); return m.spec()


S = model()
SIDES = ("l", "r")
TAILS = ("tail1", "tail2", "tail3", "tail4", "tail5")
BEND = (1.0, 1.0, 0.9, 0.8, 0.7)
BALL = {s: world(S, {}, f"toes_{s}") for s in SIDES}
REST_META = {s: chain_angle(S, {}, [f"foot_{s}"]) for s in SIDES}
WRIST = {s: world(S, {}, f"hand_{s}") for s in SIDES}
REST_HAND = {s: chain_angle(S, {}, [f"hand_{s}"]) for s in SIDES}
HIND = {s: {f"{b}_{s}" for b in ("thigh", "shin", "foot", "toes")} for s in SIDES}
FORE = {s: {f"{b}_{s}" for b in ("arm", "forearm", "hand")} for s in SIDES}
STAND_DROP = 1.0        # the body sits this much lower than the model so the knees and elbows give a little
HORNS = {b["name"] for b in S["bones"] if b["name"].startswith(("brow_horn", "young_horn", "adult_horns"))}
HEADB = {"neck", "head", "skull", "jaw", "frill"} | HORNS


def low_of(p, bones=None, skip=()):
    return min(q[:, 1].min() for c, q in geo.cube_points(S, p)
               if (bones is None or c["bone"] in bones) and c["bone"] not in skip)


# ------------------------------------------------------------------ plumbing (the Protoceratops' IK, re-fitted)
def solve_arm(pose, s, target, pitch, iters=20):
    names = [f"arm_{s}", f"forearm_{s}"]
    th0 = np.array([pose.get(n, ([0, 0, 0],))[0][0] for n in names], float)
    th = th0 + np.array([-8.0, 16.0])

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


def plant_f(p, s, dy=0.0, dz=0.0, pitch=0.0, clear=-0.05, scap=0.25):
    w = WRIST[s]; target = (w[1] + dy, w[2] + dz)
    if scap: add(p, f"arm_{s}", pos=(0, -0.05 * abs(dz), scap * dz))
    for _ in range(4):
        solve_arm(p, s, target, REST_HAND[s] + pitch)
        if clear is None: break
        lo = low_of(p, FORE[s])
        if lo > clear - 0.02: break
        target = (target[0] + clear - lo, target[1])


def lift_head(p, clear=0.3):
    for _ in range(30):
        if low_of(p, HEADB) >= clear: break
        add(p, "neck", rot=(1.5, 0, 0))
    return p


def stand(p, fore=(0, 0), hind=(0, 0), clear=0.3):
    lift_head(p, clear)
    for s in SIDES:
        plant_h(p, s, 0, hind[0] if s == "l" else hind[1])
        plant_f(p, s, 0, fore[0] if s == "l" else fore[1])
    return p


def head(p, pitch=0.0, yaw=0.0, roll=0.0, k=0.55):
    """a head movement spread over the short neck (k) and the skull"""
    add(p, "neck", rot=(pitch * k, yaw * k, roll * 0.3))
    add(p, "skull", rot=(pitch * (1 - k), yaw * (1 - k), roll * 0.7))


def horns(p, k=1.0):
    """the horns levelled at something: the face tucked down until the brow horns point ahead and the frill stands
    up behind them like a shield, the neck lifting so the beak clears the ground (a plain "head down" only sinks the
    already low beak into the dirt)"""
    add(p, "skull", rot=(-30 * k, 0, 0))
    add(p, "neck", rot=(14 * k, 0, 0))


def jaw(p, a): add(p, "jaw", rot=(a, 0, 0))


def tail(p, yaw=0.0, pitch=0.0):
    for b, k in zip(TAILS, BEND): add(p, b, rot=(pitch * k, yaw * k, 0))


def tail_wave(p, t, Tc, yaw, pitch=0.0, lag=0.6, ph=0.0):
    for i, (b, k) in enumerate(zip(TAILS, BEND)):
        a = W(t, Tc) - lag * i + ph
        add(p, b, rot=(pitch * k * math.sin(2 * a - 0.6), yaw * k * math.sin(a), 0))


def breathe(p, t, T=3.6, amp=1.0, drop=STAND_DROP):
    """slow and deep: a big barrel"""
    br = math.sin(W(t, T))
    add(p, "body", rot=(0.4 * amp * br, 0, 0), pos=(0, -drop - 0.3 * amp * (1 + br), 0))
    head(p, -0.4 * amp * br)
    return br


def settle(p):
    """a lying or rolling pose must not sink into the ground: lift the whole animal by what went under"""
    lo = low_of(p)
    if lo < -0.05: add(p, "root", pos=(0, -lo, 0))
    return p


def shift_to_ground(p, skip=()):
    lo = low_of(p, skip=skip); add(p, "root", pos=(0, -lo, 0)); return p


def blend(a, b, w):
    out = {}
    for bone in set(a) | set(b):
        ea = a.get(bone, ([0, 0, 0], [0, 0, 0])); eb = b.get(bone, ([0, 0, 0], [0, 0, 0]))
        out[bone] = ([ea[0][i] * (1 - w) + eb[0][i] * w for i in range(3)], [ea[1][i] * (1 - w) + eb[1][i] * w for i in range(3)])
    return out


# ------------------------------------------------------------------ gaits
LATERAL = {"lh": 0.0, "lf": 0.75, "rh": 0.5, "rf": 0.25}      # walk: LH, LF, RH, RF (four even beats)
GALLOP = {"lh": 0.0, "rh": 0.12, "lf": 0.48, "rf": 0.6}       # the rhino's transverse gallop: hind pair, fore pair


def foot_cycle(p, ph, feet, stride, duty, lift, flift, hz=0.0):
    for foot, o in feet.items():
        s, kind = foot[0], foot[1]
        u = (ph + o) % 1.0
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0; clear = -0.05
            heel = smooth(max(0.0, (st - 0.65) / 0.35)); sw = 0.0
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e; heel = 0.0
            ly = (lift if kind == "h" else flift) * math.sin(math.pi * min(1, sw * 1.1)) ** 1.2
            clear = 0.8 * math.sin(math.pi * sw) ** 0.5
        if kind == "h":
            meta = 18 * heel + 18 * (1 - smooth(sw / 0.4)) * (sw > 0) - 12 * math.sin(math.pi * sw)
            toe = -16 * math.sin(math.pi * min(1, sw * 1.1)) + 3 * smooth((sw - 0.7) / 0.3) * (sw > 0)
            plant_h(p, s, ly, dz + hz, meta, toe, clear)
        else:
            pitch = -16 * heel - 28 * math.sin(math.pi * min(1, sw * 1.15))
            plant_f(p, s, ly, dz, pitch, clear)


def walk_cycle(t, Tc, stride, duty, lift, bob, lean=0.0, hd=0.0, roll=1.0):
    """the heavy walk: the hips roll over the standing hind leg, the shoulders sway, the head stays level"""
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    bp = 0.5 * math.sin(2 * w - 0.5)
    add(p, "body", rot=(lean + bp, 1.4 * roll * math.sin(w), 3.0 * roll * math.sin(w + 0.3)),
        pos=(0, -STAND_DROP - bob * (0.5 + 0.5 * math.cos(2 * w - 0.8)), 0))
    # the head held still: the neck takes back the body's pitch and roll, only a small late nod is left
    add(p, "neck", rot=(hd * 0.6 - bp - lean * 0.8 + 0.6 * math.sin(2 * w - 1.6), -1.2 * roll * math.sin(w - 0.4), -1.8 * roll * math.sin(w + 0.3)))
    add(p, "skull", rot=(hd * 0.4 - lean * 0.2 + 0.4 * math.sin(2 * w - 2.2), -0.5 * roll * math.sin(w - 0.9), -1.0 * roll * math.sin(w + 0.3)))
    for i, (b, k) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(-lean * 0.2 + 0.6 * math.sin(2 * w - 1.0 - 0.5 * i), -4.5 * k * math.sin(w - 1.0 - 0.6 * i), 0))
    lift_head(p, 1.0)
    foot_cycle(p, ph, LATERAL, stride, duty, lift, lift * 0.9)
    return p


def gallop(t, Tc, stride, duty, lift, bob, rock, lean=0.0, hd=0.0, charge=0.0, hk=0.0):
    """the rhino gallop: hind pair, then fore pair; the back rocks once a stride (nose down as the hind legs drive,
    nose up as the forefeet take the weight); charge = the head down, horns level, the tail out stiff"""
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    rk = rock * math.sin(w - 0.4)
    add(p, "body", rot=(lean + rk, 1.2 * math.sin(w), 1.6 * math.sin(w + 0.5)),
        pos=(0, -STAND_DROP - 1.0 - bob * (0.5 + 0.5 * math.cos(2 * w + 0.6)), 0))
    add(p, "neck", rot=(hd * 0.6 - rk * 0.8 - lean * 0.7 + 1.2 * math.sin(w - 1.4), -0.8 * math.sin(w - 0.5), 0))
    add(p, "skull", rot=(hd * 0.4 - lean * 0.3 + 1.0 * math.sin(w - 2.0), 0, -1.0 * math.sin(w)))
    jaw(p, -2.0 * charge)
    for i, (b, k) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(-lean * 0.3 - 3 * charge * k + 2.5 * math.sin(w - 1.2 - 0.5 * i), -2.5 * k * math.sin(w - 0.9 - 0.55 * i), 0))
    if hk: horns(p, hk)
    lift_head(p, 1.5)
    foot_cycle(p, ph, GALLOP, stride, duty, lift, lift * 1.1)
    return p


WALK = (1.5, 40, 0.68, 5.0, 0.6)
RUNP = (0.72, 84, 0.4, 9.0, 2.2, 3.5)
CHARGEP = (0.62, 92, 0.38, 9.0, 2.4, 3.0)


def walk(t):
    return walk_cycle(t, *WALK, hd=-1)


def run(t):
    return gallop(t, *RUNP, lean=-1.0, hd=-3)


def charge(t):
    return gallop(t, *CHARGEP, lean=-2.5, hd=-2, charge=1.0, hk=0.9)


def swim(t):
    """swims low, only the head and the top of the frill out: the legs row slowly in pairs, the tail sculls"""
    Tc = 1.8; w = W(t, Tc); p = {}
    add(p, "body", rot=(6 + 1.2 * math.sin(2 * w), 1.5 * math.sin(w), 2.5 * math.sin(w + 0.5)), pos=(0, 0.8 * math.sin(2 * w - 1), 0))
    head(p, 18 - 1.2 * math.sin(2 * w - 1.3), -2 * math.sin(w - 0.8))
    tail_wave(p, t, Tc, 9, 1.0, lag=0.7)
    for s, o in (("l", 0.0), ("r", math.pi)):
        add(p, f"thigh_{s}", rot=(-14 + 22 * math.sin(w + o), 0, 0))
        add(p, f"shin_{s}", rot=(-8 + 18 * math.sin(w + o - 1.2), 0, 0))
        add(p, f"foot_{s}", rot=(8 + 16 * math.sin(w + o - 1.8), 0, 0))
        add(p, f"arm_{s}", rot=(-6 + 20 * math.sin(w + o + math.pi * 0.5), 0, 0))
        add(p, f"forearm_{s}", rot=(10 + 14 * math.sin(w + o + math.pi * 0.5 - 1.2), 0, 0))
        add(p, f"hand_{s}", rot=(-8 + 16 * math.sin(w + o + math.pi * 0.5 - 1.8), 0, 0))
    return p


# ------------------------------------------------------------------ lying down
FOLD_F = (-60.0, 140.0, -60.0)     # lying: the upper arm back, the forearm folded under the chest, the hand flat
BELLY_STAND = None


def lift_tail(p, clear=0.0):
    for i, b in enumerate(TAILS):
        for _ in range(20):
            if low_of(p, set(TAILS[i:])) >= clear: break
            add(p, b, rot=(-1.5, 0, 0))
    return p


def lie(p, k=1.0, pitch=0.0, sink=0.0, kf=None):
    """the belly down, the hind legs folded under, the forelegs folded under the chest like a cow's. k = how far down;
    kf = how far the FRONT is down (getting up front first: kf falls before k)"""
    global BELLY_STAND
    if BELLY_STAND is None:
        q = {}; add(q, "body", pos=(0, -STAND_DROP, 0)); BELLY_STAND = low_of(q, {"body"})
    kf = k if kf is None else kf
    add(p, "body", rot=(pitch, 0, 0), pos=(0, -STAND_DROP, 0))
    b = low_of(p, {"body"}); goal = BELLY_STAND * (1 - k) - sink * k
    add(p, "body", pos=(0, goal - b, 0))
    # the front up on straightened forelegs while the hind end is still down: the body pitches nose-up about the hip
    up = (k - kf)
    if up > 0:
        add(p, "body", rot=(14 * up, 0, 0))
    tail(p, pitch=-2 * k)
    # the head held up level, as a resting cow holds it: the neck lifts the head off the ground and the face tips
    # back down so the frill stands and the horns point ahead (raising the neck alone tipped the face to the sky)
    add(p, "neck", rot=(30 * k, 0, 0)); add(p, "skull", rot=(-22 * k, 0, 0))
    wf = smooth((kf - 0.3) / 0.7)
    for s in SIDES:
        plant_h(p, s, 0.0, 4 * k, meta=-34 * k, toe=0.0, clear=0.0)
        plant_f(p, s, 0.0, -4 * kf, pitch=0.0, clear=0.0)
        if wf > 0:
            for bone, fa in zip(("arm", "forearm", "hand"), FOLD_F):
                e = p[f"{bone}_{s}"]; e[0][0] = e[0][0] * (1 - wf) + fa * wf
    lift_tail(p)
    return p


def cheek_down(p, k=1.0, side=1.0):
    """asleep: the head laid on the ground on one cheek (the jugal horn), turned a little, the frill standing up"""
    head(p, -10 * k, 16 * k * side, -22 * k * side, k=0.6)
    add(p, "skull", rot=(-6 * k, 4 * k * side, -10 * k * side))
    for i, b in enumerate(TAILS): add(p, b, rot=(2 * k, 8 * k * side * (0.6 + 0.2 * i), 0))


def ko_pose(p, k=1.0, t=0.0):
    """knocked out: on its side, the legs out loose, the head on the ground"""
    br = math.sin(W(t, 4.2))
    add(p, "body", rot=(0, 0, 80 * k), pos=(0, -9.0 * k, 0))
    head(p, -4 * k + 0.5 * br, 0, 10 * k)
    jaw(p, -3 * k)
    tail(p, pitch=-2 * k)
    for s, sg in (("l", 1), ("r", -1)):
        add(p, f"thigh_{s}", rot=(12 * k, 0, -6 * k * sg)); add(p, f"shin_{s}", rot=(-8 * k, 0, 0)); add(p, f"foot_{s}", rot=(16 * k, 0, 0))
        add(p, f"arm_{s}", rot=(16 * k, 0, -4 * k * sg)); add(p, f"forearm_{s}", rot=(-6 * k, 0, 0)); add(p, f"hand_{s}", rot=(18 * k, 0, 0))
    add(p, "body", pos=(0, 0.3 * br * k, 0))
    return p


def sit(t):
    """lying awake, a cow at rest: belly down, the head up, a slow look to one side, an ear-flick of the frill"""
    p = {}; br = math.sin(W(t, 4.0))
    lie(p)
    add(p, "body", rot=(0.3 * br, 0, 0), pos=(0, 0.15 * (1 + br), 0))
    a = window(t, 2.5, 4.4, 0.6)
    head(p, 6 - 0.4 * br, -18 * a, 4 * a)
    tail(p, yaw=-3 * a)
    return settle(lift_tail(lift_head(p, 0.0)))


def sleep(t):
    p = {}; br = math.sin(W(t, 5.0))
    lie(p)
    add(p, "body", rot=(0.4 * br, 0, 0), pos=(0, 0.15 * (1 + br), 0))
    cheek_down(p)
    head(p, -0.5 * br)
    return settle(lift_tail(lift_head(p, 0.0)))


def wake_sleep(t):
    """wakes: the head off the ground, a look round, then up FRONT FIRST (forelegs, then the hind end)"""
    p = {}
    kh = f(tr((0, 1), (0.8, 0, smooth), (2.4, 0)), t)
    kf = f(tr((0, 1), (0.9, 1), (1.5, 0, smooth), (2.4, 0)), t)
    k = f(tr((0, 1), (1.4, 1), (2.1, 0, smooth), (2.4, 0)), t)
    lie(p, k, kf=kf)
    cheek_down(p, kh)
    head(p, 6 * (1 - kh) * kf, 12 * window(t, 0.6, 1.2, 0.2))
    return settle(lift_tail(lift_head(p, 0.0)))


def knocked_out(t):
    return shift_to_ground(ko_pose({}, 1.0, t))


def wake(t):
    """from the knocked-out pose: rolls onto its belly, shakes the frill, gets up front first"""
    roll = f(tr((0, 1), (0.3, 1), (1.1, 0, smooth), (3.4, 0)), t)
    if roll > 0:
        return shift_to_ground(blend(lift_tail(lift_head(lie({}), 0.0)), ko_pose({}, 1.0), roll))
    p = {}
    kf = f(tr((0, 1), (2.0, 1), (2.6, 0, smooth), (3.4, 0)), t)
    k = f(tr((0, 1), (2.5, 1), (3.1, 0, smooth), (3.4, 0)), t)
    lie(p, k, kf=kf)
    sh = window(t, 1.2, 1.9, 0.12)
    head(p, 3 * sh, 0, 16 * sh * math.sin(W(t, 0.3)))
    return settle(lift_tail(lift_head(p, 0.0)))


def _going_down(t):
    """the head drops first and its weight takes the front down: the beak plows the ground, the forelegs buckle onto
    the wrists, then the hind end sits down"""
    p = {}
    st = window(t, 0.0, 0.6, 0.2)
    hd = f(tr((0, 0), (0.35, 1, ease_in), (2.0, 1)), t)
    kf = f(tr((0, 0), (0.4, 0), (0.85, 1, ease_in), (2.0, 1)), t)
    k = f(tr((0, 0), (0.7, 0), (1.2, 1, ease_in), (2.0, 1)), t)
    add(p, "body", rot=(0, 3 * st * math.sin(W(t, 0.6)), 5 * st), pos=(1.5 * st, 0, 0))
    lie(p, k, kf=kf, pitch=-10 * (kf - k))
    head(p, -18 * hd + 8 * kf, -8 * st, 6 * hd)
    jaw(p, -8 * hd)
    return settle(lift_tail(lift_head(p, 0.0)))


_DOWN = []


def death(t):
    """staggers, the head goes down and the forelegs give, the hind end sits, then it rolls onto its side"""
    if t <= 1.3:
        return _going_down(t)
    if not _DOWN: _DOWN.append(_going_down(1.3))
    roll = f(tr((1.3, 0), (2.0, 1, ease_in), (2.12, 0.95), (2.26, 1, smooth), (2.8, 1)), t)
    return shift_to_ground(blend(_DOWN[0], ko_pose({}, 1.0), roll))


# ------------------------------------------------------------------ standing / everyday
def idle(t):
    """breathing slowly; rests the right hind leg like a horse (the hip drops on that side), the heavy head swings
    slowly to look, the tail flicks"""
    p = {}; br = breathe(p, t, 3.6)
    rest = window(t, 1.0, 5.6, 0.6)
    a = window(t, 2.0, 3.4, 0.5); b = window(t, 4.0, 5.2, 0.45); c = window(t, 6.2, 7.2, 0.3)
    add(p, "body", rot=(0, 1.5 * a - 1.5 * b, -2.2 * rest), pos=(0, -0.4 * rest, 0))
    head(p, 2 * a - 8 * c, 16 * a - 14 * b, -3 * a + 3 * b)
    jaw(p, -1.2 * c * max(0, math.sin(W(t, 0.35))))
    tail_wave(p, t, 8.0, 2.5, 0.3)
    flick = window(t, 6.4, 6.9, 0.12)
    tail(p, yaw=10 * flick * math.sin(W(t - 6.4, 0.5)))
    lift_head(p)
    plant_h(p, "l")
    plant_h(p, "r", 1.4 * rest, -2.5 * rest, meta=26 * rest, toe=-20 * rest, clear=-0.05 if rest < 0.05 else 0.0)
    for s in SIDES: plant_f(p, s)
    return p


def hurt(t):
    p = {}
    k = f(tr((0, 0), (0.08, 1, ease_out), (0.6, 0, smooth)), t)
    add(p, "body", rot=(3 * k, -5 * k, -3 * k), pos=(0, -STAND_DROP - 0.6 * k, 1.5 * k))
    head(p, 8 * k, 12 * k, 10 * k); jaw(p, -10 * k)
    tail(p, yaw=7 * k, pitch=-3 * k)
    return stand(p)


def attack(t):
    """the toss: the head goes down so the brow horns point ahead, a lunge from the hind legs, the horns driven in
    (the hit at 0.45 s), then hooked UP and to the side with a twist of the neck"""
    p = {}
    dn = f(tr((0, 0), (0.25, 1, ease_out), (0.45, 1), (0.6, 0, ease_out), (1.0, 0, smooth)), t)
    lunge = f(tr((0, 0), (0.25, 0), (0.45, 1, ease_in), (0.6, 0.6), (1.0, 0, smooth)), t)
    toss = f(tr((0, 0), (0.45, 0), (0.6, 1, ease_out), (0.75, 1), (1.0, 0, smooth)), t)
    add(p, "body", rot=(-3 * dn + 3 * toss, -3 * toss, 2 * toss), pos=(0, -STAND_DROP - 1.4 * dn, -4 * lunge))
    horns(p, dn)
    head(p, -4 * lunge + 30 * toss, 8 * toss, -14 * toss, k=0.5)
    jaw(p, -4 * toss)
    tail(p, yaw=-4 * toss, pitch=-3 * lunge)
    return stand(p, fore=(-2 * lunge, -2 * lunge), hind=(2 * lunge, 2 * lunge))


def horn_sweep(t):
    """a side swipe: the head swung low from one side to the other, the brow horns raking across, a step into it"""
    p = {}
    k = f(tr((0, 0), (0.2, 1, ease_out), (0.9, 1), (1.2, 0, smooth)), t)
    sw = f(tr((0, 0), (0.25, -1, ease_out), (0.5, 1, ease_in), (0.7, 1), (1.2, 0, smooth)), t)
    add(p, "body", rot=(-2 * k, 5 * sw, -3 * sw), pos=(0, -STAND_DROP - 1.0 * k, -1.5 * k))
    horns(p, 0.8 * k)
    head(p, 0, 26 * sw, -12 * sw, k=0.6)
    tail(p, yaw=-8 * sw)
    return stand(p, fore=(-1.5 * k, -1.5 * k))


def eat(t):
    """takes a mouthful from the hand or the ground: head down, a bite with the beak, then the jaw straight up and down
    (the scissor teeth slice, they do not grind)"""
    p = {}
    dn = f(tr((0, 0), (0.5, 1, smooth), (0.9, 1), (1.1, 0.4, ease_out), (2.4, 0.4), (2.8, 0, smooth)), t)
    breathe(p, t, 2.8, 0.5)
    add(p, "body", rot=(-4 * dn, 0, 0), pos=(0, -1.0 * dn, 0))
    head(p, -26 * dn - 4 * window(t, 0.9, 1.05, 0.08))
    chew = window(t, 1.1, 2.4, 0.1) * max(0, math.sin(W(t - 1.1, 0.42)))
    jaw(p, f(tr((0, 0), (0.55, -12, ease_out), (0.75, -1, ease_in), (2.8, 0)), t) - 8 * chew)
    tail_wave(p, t, 2.8, 2.0)
    return stand(p, fore=(-2 * dn, -2 * dn))


def graze(t):
    """crops low plants: the beak at the ground, three bites cut with a pull BACK (not sideways), then chews"""
    p = {}
    dn = f(tr((0, 0), (0.6, 1, smooth), (2.3, 1), (2.8, 0.3, smooth), (3.4, 0, smooth)), t)
    breathe(p, t, 3.4, 0.5)
    add(p, "body", rot=(-5 * dn, 0, 0), pos=(0, -1.2 * dn, 0))
    pull = sum(window(t, c, c + 0.22, 0.08) for c in (0.85, 1.4, 1.95))
    head(p, -30 * dn + 4 * pull, 5 * window(t, 1.3, 1.75, 0.2), 0)
    add(p, "body", pos=(0, 0, 1.0 * pull))
    bites = sum(window(t, c - 0.15, c, 0.06) for c in (0.85, 1.4, 1.95))
    chew = window(t, 2.4, 3.3, 0.1) * max(0, math.sin(W(t - 2.4, 0.4)))
    jaw(p, -12 * bites - 7 * chew)
    tail_wave(p, t, 3.4, 2.0)
    return stand(p, fore=(-2.5 * dn, -2.5 * dn))


def beg(t):
    """asks for food: the head low and pushed toward the owner, a nudge with the beak, a step closer; the tail swings"""
    p = {}; br = breathe(p, t, 2.4)
    nudge = sum(window(t, c, c + 0.18, 0.07) for c in (0.5, 1.4))
    head(p, -6 + 2 * br + 3 * nudge, 4 * math.sin(W(t, 2.4)), 0, k=0.5)
    add(p, "body", pos=(0, 0, -1.6 * nudge))
    jaw(p, -4 * window(t, 1.0, 1.2, 0.06))
    tail_wave(p, t, 2.4, 6.0)
    return stand(p, fore=(-1.2 * nudge, -1.2 * nudge))


def tame(t):
    """accepts its owner: a long breath out, the head sinks, then it turns the frill to show its side and settles"""
    p = {}
    k = f(tr((0, 0), (0.7, 1, ease_out), (1.8, 1), (2.6, 0, smooth)), t)
    sd = window(t, 0.9, 1.9, 0.3)
    breathe(p, t, 2.6, 0.8)
    add(p, "body", rot=(-3 * k, 0, 0), pos=(0, -1.2 * k, 0))
    head(p, -14 * k, 14 * sd, 16 * sd, k=0.4)
    tail(p, pitch=3 * k)
    return stand(p, fore=(-1.2 * k, -1.2 * k))


# ------------------------------------------------------------------ only the Triceratops
def stamp(t):
    """before a charge: the head down, the horns levelled, a forefoot lifted high and stamped twice, a snort"""
    p = {}
    k = f(tr((0, 0), (0.3, 1, ease_out), (1.6, 1), (1.9, 0, smooth)), t)
    breathe(p, t, 0.9, 0.6)
    add(p, "body", rot=(-2 * k, 0, -1.5 * k), pos=(0, -1.0 * k, 0))
    snort = window(t, 1.35, 1.45, 0.04)
    horns(p, k)
    head(p, 4 * snort, 0, 0, k=0.6)
    jaw(p, -3 * snort)
    tail(p, pitch=-2 * k)
    lift_head(p)
    for s in SIDES: plant_h(p, s)
    plant_f(p, "l", 0, -1.0 * k)
    st = sum(window(t, c, c + 0.2, 0.1) for c in (0.45, 0.95))
    plant_f(p, "r", 6.0 * st, -2.0 * st, -30 * st, clear=-0.05 if st < 0.05 else 0.4)
    return p


def pivot(t):
    """turns to face a predator: the forefeet planted, the hind end walked round them in four sideways steps (the game
    turns the body while it plays), the head low with the horns toward the threat"""
    p = {}
    k = f(tr((0, 0), (0.3, 1, ease_out), (2.0, 1), (2.4, 0, smooth)), t)
    breathe(p, t, 1.2, 0.6)
    add(p, "body", rot=(-2 * k, -4 * k * math.sin(W(t - 0.3, 0.9)), 0), pos=(0, -0.8 * k, 0))
    horns(p, 0.8 * k)
    head(p, 0, 4 * k * math.sin(W(t - 0.3, 0.9)), 0)
    tail(p, yaw=8 * k * math.sin(W(t - 0.5, 0.9)))
    lift_head(p)
    for s in SIDES: plant_f(p, s, 0, -1.0 * k)
    for s, o in (("l", 0.3), ("r", 0.75)):
        u = [(t - o - 0.9 * i) / 0.4 for i in range(2)]
        st = sum(math.sin(math.pi * x) for x in u if 0 <= x <= 1)
        plant_h(p, s, 3.0 * st, -1.5 * st, meta=10 * st, toe=-10 * st, clear=-0.05 if st < 0.05 else 0.4)
    return p


def horn_lock(t):
    """two males: the heads down, horns interlocked; a push forward, a twist one way, the other, a shove, they part"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (2.8, 1), (3.2, 0, smooth)), t)
    push = sum(window(t, c, c + 0.4, 0.15) for c in (0.6, 2.0))
    tw = window(t, 1.1, 1.9, 0.18) * math.sin(W(t - 1.1, 0.8))
    breathe(p, t, 1.0, 0.8)
    add(p, "body", rot=(-3 * k - 2 * push, 3 * tw, -3 * tw), pos=(0, -1.4 * k, -4.0 * push))
    horns(p, 1.1 * k)
    head(p, -3 * push, 6 * tw, 22 * tw, k=0.55)
    tail(p, yaw=-5 * tw, pitch=-3 * push)
    return stand(p, fore=(-2.5 * k, -2.5 * k), hind=(2.5 * k + 1.5 * push, 2.5 * k + 1.5 * push))


def plow(t):
    """roots for ferns and tubers: the beak pushed along the ground like a plough, two strokes forward, a toss of the
    head to throw the soil, a bite"""
    p = {}
    dn = f(tr((0, 0), (0.5, 1, smooth), (2.4, 1), (2.9, 0, smooth)), t)
    stroke = sum(window(t, c, c + 0.45, 0.15) for c in (0.6, 1.3))
    toss = window(t, 2.0, 2.25, 0.08)
    breathe(p, t, 2.9, 0.5)
    add(p, "body", rot=(-5 * dn, 0, 0), pos=(0, -1.4 * dn, -2.5 * stroke))
    head(p, -32 * dn + 14 * toss, -6 * toss, 10 * toss, k=0.5)
    jaw(p, -10 * window(t, 2.25, 2.45, 0.06))
    tail_wave(p, t, 2.9, 2.0)
    return stand(p, fore=(-2.5 * dn - 1.5 * stroke, -2.5 * dn - 1.5 * stroke), hind=(1.5 * stroke, 1.5 * stroke), clear=-0.25)


def shear(t):
    """browses a shrub at chest height: bites a branch, pulls it off with a twist of the head, then the scissor chew,
    the jaw going straight up and down"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (2.8, 1), (3.2, 0, smooth)), t)
    bite = window(t, 0.45, 0.65, 0.06)
    twist = f(tr((0, 0), (0.65, 0), (0.9, 1, ease_out), (1.1, 0, smooth)), t)
    chew = window(t, 1.2, 2.8, 0.1) * max(0, math.sin(W(t - 1.2, 0.36)))
    breathe(p, t, 3.2, 0.5)
    head(p, 10 * k - 6 * twist, -10 * twist, -18 * twist, k=0.45)
    jaw(p, -14 * f(tr((0, 0), (0.3, 1, ease_out), (0.5, 0, ease_in), (3.2, 0)), t) - 6 * chew)
    add(p, "body", rot=(1.5 * k, 0, 0), pos=(0, 0, 1.2 * twist))
    tail_wave(p, t, 3.2, 2.5)
    return stand(p)


def wallow(t):
    """in the mud: lies down, rolls onto one flank and rubs, rolls back, the other flank, gets up front first"""
    p = {}
    ly = f(tr((0, 0), (0.8, 1, smooth), (4.8, 1), (5.6, 0, smooth), (6.0, 0)), t)
    lf = f(tr((0, 0), (0.8, 1, smooth), (4.7, 1), (5.2, 0, smooth), (6.0, 0)), t)
    rl = f(tr((0, 0), (1.0, 0), (1.5, 1, smooth), (2.4, 1), (2.9, 0, smooth), (3.1, 0), (3.6, -1, smooth), (4.2, -1), (4.6, 0, smooth)), t)
    rub = (window(t, 1.5, 2.4, 0.15) + window(t, 3.6, 4.2, 0.15)) * math.sin(W(t, 0.5))
    lie(p, ly, kf=lf)
    add(p, "body", rot=(0, 2 * rub, 26 * rl + 2 * rub), pos=(0, 2.0 * abs(rl), 0))
    head(p, 4 * ly - 6 * abs(rl), -10 * rl, -16 * rl)
    tail(p, yaw=-10 * rl)
    lift_tail(lift_head(p, 0.0))
    return shift_to_ground(p) if abs(rl) > 0.02 else settle(p)


def butt_play(t):
    """the calf at play: head down, two little hops forward with a butt of the head, a skip to the side"""
    p = {}
    k = f(tr((0, 0), (0.25, 1, ease_out), (1.5, 1), (1.8, 0, smooth)), t)
    hop = sum(math.sin(math.pi * min(1, max(0, (t - c) / 0.3))) for c in (0.35, 0.85))
    butt = sum(window(t, c, c + 0.12, 0.05) for c in (0.55, 1.05))
    add(p, "body", rot=(-3 * k + 4 * hop, 6 * window(t, 1.2, 1.6, 0.12), 0), pos=(0, -0.8 * k + 3.0 * hop, -2.0 * hop))
    horns(p, k)
    head(p, 8 * butt, 0, 0)
    tail(p, pitch=-6 * hop)
    tail_wave(p, t, 0.5, 4.0 * k)
    lift_head(p)
    for s in SIDES:
        plant_h(p, s, 0, 0, clear=-0.05 if hop < 0.05 else None)
        plant_f(p, s, 0, -1.5 * k, -10 * hop, clear=-0.05 if hop < 0.05 else None)
    return settle(p)


ANIMS = {
    "idle": (idle, 8.0, True, "Parado", "respira devagar; descansa uma pata de trás como cavalo, olha, mexe a cauda"),
    "walk": (walk, WALK[0], True, "Movimento", "passo pesado em quatro tempos, o quadril rola e a cabeça fica firme"),
    "run": (run, RUNP[0], True, "Movimento", "galope de rinoceronte: par de trás, par da frente, o lombo balança"),
    "charge": (charge, CHARGEP[0], True, "Só dele", "a carga: o mesmo galope com a cabeça baixa e os chifres nivelados"),
    "swim": (swim, 1.8, True, "Movimento", "nada baixo, só a cabeça e o alto do babado fora d'água"),
    "attack": (attack, 1.0, False, "Combate", "a chifrada: cabeça baixa, avança e joga os chifres para cima e de lado"),
    "horn_sweep": (horn_sweep, 1.2, False, "Só dele", "varre os chifres de um lado para o outro, baixo"),
    "horn_lock": (horn_lock, 3.2, False, "Só dele", "dois machos travam os chifres, empurram e torcem"),
    "stamp": (stamp, 1.9, False, "Só dele", "antes da carga: cabeça baixa, bate a pata da frente duas vezes e bufa"),
    "pivot": (pivot, 2.4, False, "Só dele", "gira o quadril em volta das patas da frente para encarar o predador"),
    "hurt": (hurt, 0.6, False, "Combate", "ao levar dano"),
    "death": (death, 2.8, False, "Combate", "a cabeça cai primeiro e ara o chão, as patas da frente dobram, cai de lado"),
    "eat": (eat, 2.8, False, "Comer", "bica e mastiga com a mandíbula subindo e descendo (dentes de tesoura)"),
    "graze": (graze, 3.4, False, "Comer", "corta planta baixa com puxões para trás"),
    "plow": (plow, 2.9, False, "Só dele", "ara o chão com o bico atrás de raiz e samambaia, joga a terra"),
    "shear": (shear, 3.2, False, "Só dele", "arranca um galho na altura do peito com uma torção e corta"),
    "wallow": (wallow, 6.0, False, "Só dele", "deita na lama, esfrega um flanco, depois o outro, levanta pela frente"),
    "butt_play": (butt_play, 1.8, False, "Só dele", "o filhote brinca: pulinhos com cabeçadas"),
    "sit": (sit, 8.0, True, "Descanso", "deitado como boi, cabeça erguida"),
    "sleep": (sleep, 10.0, True, "Descanso", "dorme com a bochecha no chão e o babado em pé"),
    "wake_sleep": (wake_sleep, 2.4, False, "Descanso", "acorda: cabeça, depois a frente, por fim o quadril"),
    "knocked_out": (knocked_out, 4.2, True, "Descanso", "nocauteado, deitado de lado"),
    "wake": (wake, 3.4, False, "Descanso", "acorda do nocaute: rola, sacode o babado, levanta pela frente"),
    "beg": (beg, 2.4, True, "Domado", "pede comida: empurra o bico para o dono, chega mais perto"),
    "tame": (tame, 2.6, False, "Domado", "solta o ar, abaixa a cabeça e mostra o babado de lado"),
}


# 06/11: the fluid set and the fighting set (trikeflow.py, on the ceratopsians' ceraflow.py): the names above that
# it remakes are rebound here, the new ones (guard, strafes, turns, feint, block, recoil, submit, lie_down, get_up,
# idle_tired, walk_tired, horn_lock_start/_break) added; horn_lock becomes a loop
import trikeflow as FLOW  # noqa: E402
ANIMS = dict(ANIMS)
ANIMS.update(FLOW.ANIMS)
