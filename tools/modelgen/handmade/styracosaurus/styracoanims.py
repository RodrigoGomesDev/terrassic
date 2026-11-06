"""Styracosaurus animations, written for it from its own study (page "Estiracossauro: estudo para a 1.8", approved by
Rodrigo on 05/11/2026: "animações únicas").

Shared with the Triceratops is only the plumbing (the forelimb IK, the leg planting, the lying blend, bake and
export); every pose and every cycle is the Styracosaurus' own, from what a 5.5 m, 2.7 t horned animal of a river
plain herd would do:
- a lighter, brisker walker than the Triceratops: a quicker four-beat walk with a nod of the big head on every
  forefoot (the head is not held still: the crown bobs);
- the run is a short bounding gallop; the charge carries the head LOW with the nose horn pointing ahead, the crown
  laid back over the neck like a shield;
- it fights with the one long horn: the attack is the gore, a dip and an upward hook of the nose horn; one hit in
  three is the side hook, the head swung in from the side;
- before a charge it scrapes the ground with a forefoot, dragging it back twice (paw_scrape);
- the crown is for show (Padian & Horner 2011): facing a threat it lifts the nose, tilts the frill toward it and
  swings it slowly from side to side so the fan of spikes flashes (crown_display); two males stand side by side,
  head to tail, show their crowns and bob, never touching (rival_display);
- it rubs its nose horn on the ground like a rhino (horn_rub), shakes the flies off its crown (head_shake), calls
  the herd with the nose up and the throat pumping (call);
- calves push frill against frill, side on (frill_shove);
- rests like a cow, sleeps with the head laid on the chin and the crown up, gets up hind end first (unlike the
  Triceratops, which rises front first); dying it sags to one side, the crown hitting the ground.

Signs on this rig: body +x = nose up; neck/skull -x = down; jaw -x = open; tail pitch + = down; yaw + = to its
left; thigh/arm +x = the foot swings forward.
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
import styraco as SC
from anim2 import add, world, chain_angle, solve_leg, Track, smooth, ease_out, ease_in

W = lambda t, T: 2 * math.pi * t / T


def tr(*keys): return Track(keys)


def f(track, t): return float(track(t))


def window(t, a, b, fade=0.25):
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


def model():
    m = SC.build("male"); P.pack(m, SC.TEX_W); return m.spec()


S = model()
SIDES = ("l", "r")
TAILS = ("tail1", "tail2", "tail3", "tail4")
BEND = (1.0, 0.95, 0.85, 0.7)
BALL = {s: world(S, {}, f"toes_{s}") for s in SIDES}
REST_META = {s: chain_angle(S, {}, [f"foot_{s}"]) for s in SIDES}
WRIST = {s: world(S, {}, f"hand_{s}") for s in SIDES}
REST_HAND = {s: chain_angle(S, {}, [f"hand_{s}"]) for s in SIDES}
HIND = {s: {f"{b}_{s}" for b in ("thigh", "shin", "foot", "toes")} for s in SIDES}
FORE = {s: {f"{b}_{s}" for b in ("arm", "forearm", "hand")} for s in SIDES}
STAND_DROP = 1.0


def _subtree(root):
    kids = {root}
    changed = True
    while changed:
        changed = False
        for b in S["bones"]:
            if b.get("parent") in kids and b["name"] not in kids:
                kids.add(b["name"]); changed = True
    return kids


HEADB = _subtree("neck")
# the crown never decides the head's clearance (it rises well above the skull)
LOWHEAD = {b for b in HEADB if "spike" not in b and b not in ("male_display", "female_display", "adult_frill", "young_frill")}


def low_of(p, bones=None, skip=()):
    return min(q[:, 1].min() for c, q in geo.cube_points(S, p)
               if (bones is None or c["bone"] in bones) and c["bone"] not in skip)


# ------------------------------------------------------------------ plumbing (shared IK)
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
        if low_of(p, LOWHEAD) >= clear: break
        add(p, "neck", rot=(1.5, 0, 0))
    return p


def stand(p, fore=(0, 0), hind=(0, 0), clear=0.3):
    lift_head(p, clear)
    for s in SIDES:
        plant_h(p, s, 0, hind[0] if s == "l" else hind[1])
        plant_f(p, s, 0, fore[0] if s == "l" else fore[1])
    return p


def head(p, pitch=0.0, yaw=0.0, roll=0.0, k=0.5):
    add(p, "neck", rot=(pitch * k, yaw * k, roll * 0.3))
    add(p, "skull", rot=(pitch * (1 - k), yaw * (1 - k), roll * 0.7))


def horn_level(p, k=1.0):
    """the nose horn levelled at something: the face tucked down until the horn points ahead, the crown laid back
    over the neck, the neck lifting so the beak clears the ground"""
    add(p, "skull", rot=(-38 * k, 0, 0))
    add(p, "neck", rot=(12 * k, 0, 0))


def jaw(p, a): add(p, "jaw", rot=(a, 0, 0))


def tail(p, yaw=0.0, pitch=0.0):
    for b, k in zip(TAILS, BEND): add(p, b, rot=(pitch * k, yaw * k, 0))


def tail_wave(p, t, Tc, yaw, pitch=0.0, lag=0.6, ph=0.0):
    for i, (b, k) in enumerate(zip(TAILS, BEND)):
        a = W(t, Tc) - lag * i + ph
        add(p, b, rot=(pitch * k * math.sin(2 * a - 0.6), yaw * k * math.sin(a), 0))


def breathe(p, t, T=3.0, amp=1.0, drop=STAND_DROP):
    br = math.sin(W(t, T))
    add(p, "body", rot=(0.4 * amp * br, 0, 0), pos=(0, -drop - 0.3 * amp * (1 + br), 0))
    head(p, -0.5 * amp * br)
    return br


def settle(p):
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
LATERAL = {"lh": 0.0, "lf": 0.75, "rh": 0.5, "rf": 0.25}
BOUND = {"lh": 0.0, "rh": 0.08, "lf": 0.5, "rf": 0.58}        # the short bounding gallop: hind pair, fore pair


def foot_cycle(p, ph, feet, stride, duty, lift, flift):
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
            meta = 16 * heel + 16 * (1 - smooth(sw / 0.4)) * (sw > 0) - 12 * math.sin(math.pi * sw)
            toe = -14 * math.sin(math.pi * min(1, sw * 1.1)) + 3 * smooth((sw - 0.7) / 0.3) * (sw > 0)
            plant_h(p, s, ly, dz, meta, toe, clear)
        else:
            pitch = -14 * heel - 30 * math.sin(math.pi * min(1, sw * 1.15))
            plant_f(p, s, ly, dz, pitch, clear)


def walk_cycle(t, Tc, stride, duty, lift, bob, lean=0.0, hd=0.0):
    """the brisk walk: the hips roll a little, the big head nods down on every forefoot so the crown bobs"""
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    bp = 0.6 * math.sin(2 * w - 0.5)
    add(p, "body", rot=(lean + bp, 1.6 * math.sin(w), 2.4 * math.sin(w + 0.3)),
        pos=(0, -STAND_DROP - bob * (0.5 + 0.5 * math.cos(2 * w - 0.8)), 0))
    nod = 2.2 * math.sin(2 * w - 2.0)          # a nod on each forefoot strike (twice a cycle)
    add(p, "neck", rot=(hd * 0.6 - bp - lean * 0.8 + 0.4 * nod, -1.5 * math.sin(w - 0.4), -1.4 * math.sin(w + 0.3)))
    add(p, "skull", rot=(hd * 0.4 - lean * 0.2 + 0.6 * nod, -0.8 * math.sin(w - 0.9), -0.8 * math.sin(w + 0.3)))
    for i, (b, k) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(-lean * 0.2 + 0.8 * math.sin(2 * w - 1.0 - 0.5 * i), -5.5 * k * math.sin(w - 1.0 - 0.6 * i), 0))
    lift_head(p, 1.0)
    foot_cycle(p, ph, LATERAL, stride, duty, lift, lift * 0.9)
    return p


def gallop(t, Tc, stride, duty, lift, bob, rock, lean=0.0, hd=0.0, charge=0.0):
    """the bounding gallop: hind pair, fore pair; the back rocks once a stride. charge = the head low, the nose horn
    pointing ahead and the crown laid back, the tail out stiff"""
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    rk = rock * math.sin(w - 0.3)
    add(p, "body", rot=(lean + rk, 1.0 * math.sin(w), 1.4 * math.sin(w + 0.5)),
        pos=(0, -STAND_DROP - 1.0 - bob * (0.5 + 0.5 * math.cos(2 * w + 0.6)), 0))
    add(p, "neck", rot=(hd * 0.6 - rk * 0.9 - lean * 0.7 + 1.5 * math.sin(w - 1.4), -0.8 * math.sin(w - 0.5), 0))
    add(p, "skull", rot=(hd * 0.4 - lean * 0.3 + 1.2 * math.sin(w - 2.0), 0, -1.0 * math.sin(w)))
    jaw(p, -2.5 * charge)
    for i, (b, k) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(-lean * 0.3 - 4 * charge * k + 3 * math.sin(w - 1.2 - 0.5 * i), -2.5 * k * math.sin(w - 0.9 - 0.55 * i), 0))
    if charge: horn_level(p, charge)
    lift_head(p, 1.5)
    foot_cycle(p, ph, BOUND, stride, duty, lift, lift * 1.1)
    return p


WALK = (1.15, 40, 0.66, 5.0, 0.7)
RUNP = (0.56, 96, 0.38, 10.0, 2.4, 4.5)
CHARGEP = (0.5, 104, 0.36, 10.0, 2.6, 3.5)


def walk(t):
    return walk_cycle(t, *WALK, hd=-1)


def run(t):
    return gallop(t, *RUNP, lean=-1.0, hd=-2)


def charge(t):
    return gallop(t, *CHARGEP, lean=-2.0, hd=-2, charge=1.0)


def swim(t):
    """swims with the head and the crown out, paddling diagonally (left fore with right hind), the tail sculling"""
    Tc = 1.6; w = W(t, Tc); p = {}
    add(p, "body", rot=(8 + 1.0 * math.sin(2 * w), 1.5 * math.sin(w), 2.0 * math.sin(w + 0.5)), pos=(0, 0.8 * math.sin(2 * w - 1), 0))
    head(p, 20 - 1.5 * math.sin(2 * w - 1.3), -2 * math.sin(w - 0.8))
    tail_wave(p, t, Tc, 10, 1.0, lag=0.7)
    for s, o in (("l", 0.0), ("r", math.pi)):
        add(p, f"thigh_{s}", rot=(-12 + 24 * math.sin(w + o), 0, 0))
        add(p, f"shin_{s}", rot=(-8 + 18 * math.sin(w + o - 1.2), 0, 0))
        add(p, f"foot_{s}", rot=(8 + 16 * math.sin(w + o - 1.8), 0, 0))
        add(p, f"arm_{s}", rot=(-6 + 22 * math.sin(w + o + math.pi), 0, 0))
        add(p, f"forearm_{s}", rot=(10 + 14 * math.sin(w + o + math.pi - 1.2), 0, 0))
        add(p, f"hand_{s}", rot=(-8 + 16 * math.sin(w + o + math.pi - 1.8), 0, 0))
    return p


# ------------------------------------------------------------------ lying down
FOLD_F = (-58.0, 136.0, -60.0)
BELLY_STAND = None


def lift_tail(p, clear=0.0):
    for i, b in enumerate(TAILS):
        for _ in range(20):
            if low_of(p, set(TAILS[i:])) >= clear: break
            add(p, b, rot=(-1.5, 0, 0))
    return p


def lie(p, k=1.0, pitch=0.0, sink=0.0, kh=None):
    """the belly down, the hind legs folded under, the forelegs folded under the chest. k = how far the FRONT is
    down; kh = how far the hind end is (it gets up hind end first: kh falls before k)"""
    global BELLY_STAND
    if BELLY_STAND is None:
        q = {}; add(q, "body", pos=(0, -STAND_DROP, 0)); BELLY_STAND = low_of(q, {"body"})
    kh = k if kh is None else kh
    add(p, "body", rot=(pitch, 0, 0), pos=(0, -STAND_DROP, 0))
    b = low_of(p, {"body"}); goal = BELLY_STAND * (1 - k) - sink * k
    add(p, "body", pos=(0, goal - b, 0))
    up = (k - kh)
    if up > 0:                         # the hind end up first: the body pitches nose-down about the shoulder
        add(p, "body", rot=(-12 * up, 0, 0), pos=(0, 6 * up, 0))
    tail(p, pitch=-2 * k)
    add(p, "neck", rot=(26 * k, 0, 0)); add(p, "skull", rot=(-18 * k, 0, 0))
    wf = smooth((k - 0.3) / 0.7)
    for s in SIDES:
        plant_h(p, s, 0.0, 3 * kh, meta=-32 * kh, toe=0.0, clear=0.0)
        plant_f(p, s, 0.0, -3 * k, pitch=0.0, clear=0.0)
        if wf > 0:
            for bone, fa in zip(("arm", "forearm", "hand"), FOLD_F):
                e = p[f"{bone}_{s}"]; e[0][0] = e[0][0] * (1 - wf) + fa * wf
    lift_tail(p)
    return p


def chin_down(p, k=1.0):
    """asleep: the head laid straight down on the chin and the beak, the crown standing up behind it"""
    head(p, -14 * k, 3 * k, 0, k=0.6)
    add(p, "skull", rot=(-8 * k, 0, 0))
    for i, b in enumerate(TAILS): add(p, b, rot=(2 * k, 10 * k * (0.5 + 0.2 * i), 0))


def ko_pose(p, k=1.0, t=0.0):
    br = math.sin(W(t, 4.0))
    add(p, "body", rot=(0, 0, -82 * k), pos=(0, -7.0 * k, 0))
    head(p, -6 * k + 0.5 * br, 0, -14 * k)
    jaw(p, -4 * k)
    tail(p, pitch=-2 * k)
    for s, sg in (("l", 1), ("r", -1)):
        add(p, f"thigh_{s}", rot=(14 * k, 0, 6 * k * sg)); add(p, f"shin_{s}", rot=(-10 * k, 0, 0)); add(p, f"foot_{s}", rot=(14 * k, 0, 0))
        add(p, f"arm_{s}", rot=(18 * k, 0, 4 * k * sg)); add(p, f"forearm_{s}", rot=(-8 * k, 0, 0)); add(p, f"hand_{s}", rot=(16 * k, 0, 0))
    add(p, "body", pos=(0, 0.3 * br * k, 0))
    return p


def sit(t):
    """lying awake, chewing the cud; now and then the crown turns to one side to look"""
    p = {}; br = math.sin(W(t, 3.6))
    lie(p)
    add(p, "body", rot=(0.3 * br, 0, 0), pos=(0, 0.15 * (1 + br), 0))
    a = window(t, 2.2, 4.0, 0.5)
    head(p, 6 - 0.4 * br, 20 * a, -4 * a)
    jaw(p, -2.5 * window(t, 4.6, 7.0, 0.2) * max(0, math.sin(W(t - 4.6, 0.6))))
    tail(p, yaw=4 * a)
    return settle(lift_tail(lift_head(p, 0.0)))


def sleep(t):
    p = {}; br = math.sin(W(t, 4.6))
    lie(p)
    add(p, "body", rot=(0.4 * br, 0, 0), pos=(0, 0.15 * (1 + br), 0))
    chin_down(p)
    head(p, -0.6 * br)
    return settle(lift_tail(lift_head(p, 0.0)))


def wake_sleep(t):
    """wakes: the head up, a shake of the crown, then up HIND END FIRST"""
    p = {}
    kc = f(tr((0, 1), (0.7, 0, smooth), (2.2, 0)), t)
    kh = f(tr((0, 1), (1.1, 1), (1.6, 0, smooth), (2.2, 0)), t)
    k = f(tr((0, 1), (1.4, 1), (2.0, 0, smooth), (2.2, 0)), t)
    lie(p, k, kh=kh)
    chin_down(p, kc)
    sh = window(t, 0.7, 1.1, 0.1)
    head(p, 0, 0, 14 * sh * math.sin(W(t, 0.25)))
    return settle(lift_tail(lift_head(p, 0.0)))


def knocked_out(t):
    return shift_to_ground(ko_pose({}, 1.0, t))


def wake(t):
    roll = f(tr((0, 1), (0.3, 1), (1.0, 0, smooth), (3.2, 0)), t)
    if roll > 0:
        return shift_to_ground(blend(lift_tail(lift_head(lie({}), 0.0)), ko_pose({}, 1.0), roll))
    p = {}
    kh = f(tr((0, 1), (1.8, 1), (2.4, 0, smooth), (3.2, 0)), t)
    k = f(tr((0, 1), (2.3, 1), (2.9, 0, smooth), (3.2, 0)), t)
    lie(p, k, kh=kh)
    sh = window(t, 1.1, 1.7, 0.12)
    head(p, 2 * sh, 0, 18 * sh * math.sin(W(t, 0.28)))
    return settle(lift_tail(lift_head(p, 0.0)))


def _going_down(t):
    """it staggers to one side, the hind legs give, then the front, and it sags onto its flank, the crown hitting the
    ground"""
    p = {}
    st = window(t, 0.0, 0.7, 0.2)
    kh = f(tr((0, 0), (0.35, 0), (0.8, 1, ease_in), (1.8, 1)), t)
    k = f(tr((0, 0), (0.6, 0), (1.1, 1, ease_in), (1.8, 1)), t)
    add(p, "body", rot=(0, -4 * st * math.sin(W(t, 0.7)), -6 * st), pos=(-1.5 * st, 0, 0))
    lie(p, k, kh=max(kh, k))
    head(p, -10 * k, 10 * st, -8 * k)
    jaw(p, -10 * k)
    return settle(lift_tail(lift_head(p, 0.0)))


_DOWN = []


def death(t):
    if t <= 1.2:
        return _going_down(t)
    if not _DOWN: _DOWN.append(_going_down(1.2))
    roll = f(tr((1.2, 0), (1.9, 1, ease_in), (2.02, 0.95), (2.15, 1, smooth), (2.6, 1)), t)
    return shift_to_ground(blend(_DOWN[0], ko_pose({}, 1.0), roll))


# ------------------------------------------------------------------ standing / everyday
def idle(t):
    """breathing; the head swings to look over the herd, an ear-like twitch of the crown (a quick roll), a weight
    shift from one forefoot to the other, the tail flicks"""
    p = {}; breathe(p, t, 3.0)
    a = window(t, 1.2, 2.6, 0.45); b = window(t, 3.4, 4.6, 0.45)
    tw = window(t, 5.2, 5.6, 0.08)
    sh = window(t, 2.8, 5.0, 0.6)
    add(p, "body", rot=(0, 1.2 * a - 1.2 * b, 1.8 * sh), pos=(0.6 * sh, 0, 0))
    head(p, 3 * a - 2 * b, 18 * a - 16 * b, -2 * a + 2 * b + 7 * tw * math.sin(W(t - 5.2, 0.2)))
    tail_wave(p, t, 6.0, 3.0, 0.3)
    flick = window(t, 6.2, 6.7, 0.1)
    tail(p, yaw=12 * flick * math.sin(W(t - 6.2, 0.45)))
    lift_head(p)
    for s in SIDES:
        plant_h(p, s)
        plant_f(p, s, 0.6 * sh if s == "l" else 0.0)
    return p


def hurt(t):
    p = {}
    k = f(tr((0, 0), (0.07, 1, ease_out), (0.55, 0, smooth)), t)
    add(p, "body", rot=(4 * k, 6 * k, 4 * k), pos=(0, -STAND_DROP - 0.8 * k, 1.8 * k))
    head(p, 12 * k, -14 * k, -12 * k); jaw(p, -12 * k)
    tail(p, yaw=-8 * k, pitch=-4 * k)
    return stand(p)


def attack(t):
    """the gore: the head dips so the nose horn points ahead, a lunge from the hind legs (the hit at 0.4 s), then
    the horn hooked UP, the crown flung back"""
    p = {}
    dn = f(tr((0, 0), (0.22, 1, ease_out), (0.4, 1), (0.55, 0, ease_out), (0.9, 0, smooth)), t)
    lunge = f(tr((0, 0), (0.22, 0), (0.4, 1, ease_in), (0.55, 0.5), (0.9, 0, smooth)), t)
    hook = f(tr((0, 0), (0.4, 0), (0.52, 1, ease_out), (0.64, 1), (0.9, 0, smooth)), t)
    add(p, "body", rot=(-3 * dn + 4 * hook, 0, 0), pos=(0, -STAND_DROP - 1.2 * dn, -4 * lunge))
    horn_level(p, dn)
    head(p, -4 * lunge + 34 * hook, 0, 0, k=0.45)
    jaw(p, -5 * hook)
    tail(p, pitch=-4 * lunge)
    return stand(p, fore=(-2 * lunge, -2 * lunge), hind=(2 * lunge, 2 * lunge))


def horn_hook(t):
    """the side hook: the head swung out to one side, then driven in and up across the front, the horn raking"""
    p = {}
    k = f(tr((0, 0), (0.2, 1, ease_out), (0.75, 1), (1.0, 0, smooth)), t)
    sw = f(tr((0, 0), (0.25, 1, ease_out), (0.45, -1, ease_in), (0.6, -1), (1.0, 0, smooth)), t)
    up = window(t, 0.42, 0.62, 0.08)
    add(p, "body", rot=(-2 * k, 5 * sw, 3 * sw), pos=(0, -STAND_DROP - 0.8 * k, -1.5 * k))
    horn_level(p, 0.7 * k)
    head(p, 22 * up, 28 * sw, 14 * sw, k=0.55)
    tail(p, yaw=-9 * sw)
    return stand(p, fore=(-1.5 * k, -1.5 * k))


def eat(t):
    """a mouthful from the hand or the ground: the head down, a bite with the narrow beak, the scissor chew"""
    p = {}
    dn = f(tr((0, 0), (0.45, 1, smooth), (0.85, 1), (1.05, 0.35, ease_out), (2.2, 0.35), (2.6, 0, smooth)), t)
    breathe(p, t, 2.6, 0.5)
    add(p, "body", rot=(-4 * dn, 0, 0), pos=(0, -0.9 * dn, 0))
    head(p, -28 * dn - 4 * window(t, 0.85, 1.0, 0.07))
    chew = window(t, 1.05, 2.2, 0.1) * max(0, math.sin(W(t - 1.05, 0.38)))
    jaw(p, f(tr((0, 0), (0.5, -13, ease_out), (0.7, -1, ease_in), (2.6, 0)), t) - 8 * chew)
    tail_wave(p, t, 2.6, 2.5)
    return stand(p, fore=(-2 * dn, -2 * dn))


def graze(t):
    """crops low ferns: the beak at the ground, a bite with a twist of the head to tear the frond, twice, then chews"""
    p = {}
    dn = f(tr((0, 0), (0.55, 1, smooth), (2.1, 1), (2.6, 0.3, smooth), (3.2, 0, smooth)), t)
    breathe(p, t, 3.2, 0.5)
    add(p, "body", rot=(-5 * dn, 0, 0), pos=(0, -1.1 * dn, 0))
    tear = sum(window(t, c, c + 0.25, 0.08) for c in (0.85, 1.6))
    side = 1 if t < 1.4 else -1
    head(p, -32 * dn + 3 * tear, 6 * tear * side, 14 * tear * side)
    bites = sum(window(t, c - 0.15, c, 0.06) for c in (0.85, 1.6))
    chew = window(t, 2.2, 3.1, 0.1) * max(0, math.sin(W(t - 2.2, 0.38)))
    jaw(p, -12 * bites - 7 * chew)
    tail_wave(p, t, 3.2, 2.5)
    return stand(p, fore=(-2.5 * dn, -2.5 * dn))


def beg(t):
    """asks for food: the head held up and tilted so the crown fans toward the owner, a toss of the nose, a step"""
    p = {}; br = breathe(p, t, 2.2)
    toss = sum(window(t, c, c + 0.2, 0.07) for c in (0.5, 1.4))
    head(p, 8 + 2 * br + 8 * toss, 6 * math.sin(W(t, 2.2)), 8 * math.sin(W(t, 2.2)), k=0.5)
    add(p, "body", pos=(0, 0, -1.4 * toss))
    jaw(p, -4 * window(t, 1.0, 1.2, 0.06))
    tail_wave(p, t, 2.2, 7.0)
    return stand(p, fore=(-1.2 * toss, -1.2 * toss))


def tame(t):
    """accepts its owner: the crown lowered, the head pushed gently forward, a long breath out"""
    p = {}
    k = f(tr((0, 0), (0.6, 1, ease_out), (1.7, 1), (2.4, 0, smooth)), t)
    breathe(p, t, 2.4, 0.9)
    add(p, "body", rot=(-3 * k, 0, 0), pos=(0, -1.0 * k, -1.0 * k))
    head(p, -18 * k, 0, 6 * window(t, 0.8, 1.6, 0.3), k=0.4)
    tail(p, pitch=3 * k)
    return stand(p, fore=(-1.0 * k, -1.0 * k))


# ------------------------------------------------------------------ only the Styracosaurus
def paw_scrape(t):
    """before a charge: the head low with the horn ahead, a forefoot dragged BACK along the ground twice, a snort"""
    p = {}
    k = f(tr((0, 0), (0.3, 1, ease_out), (1.6, 1), (1.9, 0, smooth)), t)
    breathe(p, t, 0.8, 0.6)
    add(p, "body", rot=(-2 * k, 0, 1.5 * k), pos=(0, -0.9 * k, 0))
    snort = window(t, 1.35, 1.45, 0.04)
    horn_level(p, 0.8 * k)
    head(p, 5 * snort, 0, 0, k=0.6)
    jaw(p, -3 * snort)
    tail(p, pitch=-3 * k, yaw=4 * window(t, 0.4, 1.4, 0.2) * math.sin(W(t, 0.5)))
    lift_head(p)
    for s in SIDES: plant_h(p, s)
    plant_f(p, "r", 0, -1.0 * k)
    # the scrape: lifted forward, set down, dragged back along the ground
    dz = 0.0; dy = 0.0
    for c in (0.4, 0.95):
        u = (t - c) / 0.5
        if 0 <= u <= 1:
            if u < 0.35:
                e = smooth(u / 0.35); dz = -4.0 * e; dy = 3.0 * math.sin(math.pi * e)
            else:
                e = smooth((u - 0.35) / 0.65); dz = -4.0 + 7.0 * e; dy = 0.0
    plant_f(p, "l", dy, dz, -18 * (dy > 0.2), clear=-0.05 if dy < 0.05 else 0.3)
    return p


def crown_display(t):
    """faces a threat and shows the crown: the nose lifted, the frill tipped toward it, then swung slowly from side
    to side so the fan of spikes flashes; a deep snort at the end"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (2.8, 1), (3.3, 0, smooth)), t)
    sw = window(t, 0.6, 2.6, 0.3) * math.sin(W(t - 0.6, 2.0))
    breathe(p, t, 1.1, 0.6)
    add(p, "body", rot=(2 * k, 4 * sw, 0), pos=(0, -0.4 * k, 0))
    head(p, -10 * k, 22 * sw, 20 * sw, k=0.5)        # the face down a little: the crown stands up toward the threat
    jaw(p, -4 * window(t, 2.75, 2.95, 0.05))
    tail(p, yaw=-6 * sw, pitch=-2 * k)
    return stand(p, fore=(-0.8 * k, -0.8 * k))


def rival_display(t):
    """two males side by side: the head turned to show the crown to the other, a bob, a step, a turn of the frill,
    never touching (the frill is for show)"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (3.2, 1), (3.6, 0, smooth)), t)
    bob = sum(window(t, c, c + 0.3, 0.1) for c in (0.8, 1.5, 2.4))
    breathe(p, t, 1.2, 0.7)
    add(p, "body", rot=(1.5 * k, -6 * k, 3 * k), pos=(0, -0.5 * k - 0.8 * bob, 0))
    head(p, -8 * k - 10 * bob, 34 * k, 16 * k, k=0.5)
    jaw(p, -3 * window(t, 2.0, 2.2, 0.05))
    tail(p, yaw=6 * k, pitch=-2 * k)
    step = window(t, 1.8, 2.3, 0.15)
    return stand(p, fore=(-1.0 * k - 1.5 * step, -1.0 * k), hind=(0, 1.5 * step))


def horn_rub(t):
    """rubs the nose horn on the ground like a rhino: the head down, the horn scraped forward and back, twice, a
    shake of the head"""
    p = {}
    dn = f(tr((0, 0), (0.5, 1, smooth), (2.3, 1), (2.8, 0, smooth)), t)
    rub = window(t, 0.6, 2.0, 0.15) * math.sin(W(t - 0.6, 0.7))
    shake = window(t, 2.1, 2.5, 0.08) * math.sin(W(t, 0.2))
    breathe(p, t, 2.8, 0.5)
    add(p, "body", rot=(-6 * dn, 0, 0), pos=(0, -1.5 * dn, -2.0 * rub))
    head(p, -34 * dn - 5 * rub, 4 * rub, 12 * shake, k=0.5)
    tail_wave(p, t, 2.8, 2.0)
    return stand(p, fore=(-2.5 * dn - 1.5 * rub, -2.5 * dn - 1.5 * rub), clear=-0.3)


def head_shake(t):
    """shakes the flies off the crown: a quick roll of the head one way and the other, the body shivering"""
    p = {}
    k = window(t, 0.15, 1.1, 0.12)
    rl = k * math.sin(W(t, 0.32))
    breathe(p, t, 1.4, 0.4)
    add(p, "body", rot=(0, 0, 1.2 * rl), pos=(0, 0, 0))
    head(p, 4 * k, 6 * rl, 26 * rl, k=0.4)
    jaw(p, -3 * k)
    tail_wave(p, t, 0.6, 6.0 * k)
    return stand(p)


def call(t):
    """calls the herd: the nose up, the throat pumping, two long notes"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (2.2, 1), (2.6, 0, smooth)), t)
    note = window(t, 0.6, 1.2, 0.1) + window(t, 1.5, 2.1, 0.1)
    breathe(p, t, 1.3, 0.8)
    add(p, "body", rot=(3 * k, 0, 0), pos=(0, -0.4 * k, 0))
    head(p, 20 * k + 3 * note * math.sin(W(t, 0.15)), 0, 0, k=0.6)
    jaw(p, -10 * note)
    tail(p, pitch=-2 * k)
    return stand(p)


def frill_shove(t):
    """the calves at play: side on, frill against frill, a push, a skip back, another push"""
    p = {}
    k = f(tr((0, 0), (0.25, 1, ease_out), (1.6, 1), (1.9, 0, smooth)), t)
    push = sum(window(t, c, c + 0.3, 0.1) for c in (0.35, 1.0))
    skip = math.sin(math.pi * min(1, max(0, (t - 0.7) / 0.25)))
    add(p, "body", rot=(-2 * k + 3 * skip, 4 * k, -6 * push), pos=(1.8 * push, 2.0 * skip, 0))
    head(p, -6 * k, 26 * k, -18 * k - 10 * push, k=0.5)
    tail_wave(p, t, 0.5, 5.0 * k)
    lift_head(p)
    for s in SIDES:
        plant_h(p, s, 0, 0, clear=-0.05 if skip < 0.05 else None)
        plant_f(p, s, 0, -1.0 * k, -10 * skip, clear=-0.05 if skip < 0.05 else None)
    return settle(p)


ANIMS = {
    "idle": (idle, 7.0, True, "Parado", "respira, olha o bando, mexe a coroa de leve, troca o peso das patas"),
    "walk": (walk, WALK[0], True, "Movimento", "passo ligeiro em quatro tempos, a cabeça grande acena a cada pata da frente"),
    "run": (run, RUNP[0], True, "Movimento", "galope curto aos saltos: par de trás, par da frente"),
    "charge": (charge, CHARGEP[0], True, "Só dele", "a investida: cabeça baixa, chifre do nariz apontado, coroa deitada"),
    "swim": (swim, 1.6, True, "Movimento", "nada com a cabeça e a coroa fora d'água, patas em diagonal"),
    "attack": (attack, 0.9, False, "Combate", "a chifrada: abaixa, avança e engancha o chifre para cima"),
    "horn_hook": (horn_hook, 1.0, False, "Só dele", "o gancho de lado: a cabeça vem de fora para dentro, o chifre rasga"),
    "paw_scrape": (paw_scrape, 1.9, False, "Só dele", "antes da investida: raspa o chão duas vezes, puxando a pata para trás"),
    "crown_display": (crown_display, 3.3, False, "Só dele", "encara a ameaça e balança a coroa de espinhos devagar"),
    "rival_display": (rival_display, 3.6, False, "Só dele", "dois machos lado a lado mostram a coroa e acenam, sem encostar"),
    "horn_rub": (horn_rub, 2.8, False, "Só dele", "esfrega o chifre do nariz no chão, como rinoceronte"),
    "head_shake": (head_shake, 1.3, False, "Só dele", "sacode a coroa para espantar as moscas"),
    "call": (call, 2.6, False, "Só dele", "chama o bando: nariz para cima, duas notas longas"),
    "frill_shove": (frill_shove, 1.9, False, "Só dele", "os filhotes empurram gola contra gola, de lado"),
    "hurt": (hurt, 0.55, False, "Combate", "ao levar dano"),
    "death": (death, 2.6, False, "Combate", "cambaleia, o quadril cede, depois a frente, e cai de lado com a coroa no chão"),
    "eat": (eat, 2.6, False, "Comer", "bica com o bico estreito e corta"),
    "graze": (graze, 3.2, False, "Comer", "arranca samambaia com uma torção da cabeça"),
    "sit": (sit, 7.0, True, "Descanso", "deitado ruminando, vira a coroa para olhar"),
    "sleep": (sleep, 9.0, True, "Descanso", "dorme com o queixo no chão e a coroa em pé"),
    "wake_sleep": (wake_sleep, 2.2, False, "Descanso", "acorda, sacode a coroa, levanta primeiro o quadril"),
    "knocked_out": (knocked_out, 4.0, True, "Descanso", "nocauteado, deitado de lado"),
    "wake": (wake, 3.2, False, "Descanso", "acorda do nocaute: rola, sacode a cabeça, levanta pelo quadril"),
    "beg": (beg, 2.2, True, "Domado", "pede comida: ergue a cabeça e mostra a coroa ao dono"),
    "tame": (tame, 2.4, False, "Domado", "abaixa a coroa e empurra a cabeça de leve para o dono"),
}


# 06/11: the fluid set and the fighting set (styraflow.py, on the ceratopsians' triceratops/ceraflow.py): the names
# above that it remakes are rebound here, the new ones (nose_jab, guard, strafes, turns, feint, block, recoil, submit,
# lie_down, get_up, idle_tired, walk_tired) added
import styraflow as FLOW  # noqa: E402
ANIMS = dict(ANIMS)
ANIMS.update(FLOW.ANIMS)
