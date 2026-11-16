"""Maiasaura v4 animations ("a mãe empinada", silhueta C da 1.11; study docs/estudos/15_HERBIVOROS_1_11.md).

The rest pose is HALF-REARED: the body tipped up 34 degrees on the hind legs, the tail down behind as the third leg
of a tripod, the arms hanging free, the head low on the S of the neck. Every animation is built on one layer,
posture(p, k): k = 0 is that tripod, k = 1 is down on all four (the body level, the neck and the tail brought round,
the hands on the ground through the arm IK); in between the hands go from hanging to planted. So:
- on the tripod (k ~ 0): idle, the calls and the alarm (higher), the nest guard, kick_back (on one foot and the
  tail), body_shove, eat from the hand, tame, beg, hurt, rear_browse (higher still);
- dropping forward (k from 0 toward 1 and back): graze, drink, cover_nest (pulls leaves on the side, comes up and
  drops them over the nest), feed_young, nuzzle, adopt, nest_dig (on four, hands scraping), the attack (the mother
  throws her chest and her deep head forward);
- on all four (k = 1): walk, walk_tired, turn_left/right, swim;
- on two legs, the body near level (k ~ 0.7): run; the calf's biped_walk and biped_run;
- lying (the body levelled first): sit, sleep, nest_sleep, nest_beg, lie_down, get_up, wake_sleep, knockout,
  knocked_out, wake, death, hatch.

Signs on this rig: body +x = nose up; neck/skull -x = down; jaw -x = open; tail pitch + = down; yaw + = to its
left; thigh/arm +x = the foot swings forward; cheek z out = +z on the left.
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
import maia as TC
import anim2
from anim2 import add, world, chain_angle, solve_leg, Track, smooth, ease_out, ease_in, back_out

W = lambda t, T: 2 * math.pi * t / T
# the thigh's soft limit is a delta from rest: on all four the body's tip swings the legs 36 degrees back, so the
# thigh's offset starts near +36 and needs the room forward (the Velociraptor's limit kept the IK from reaching)
anim2.THIGH_RANGE = (-60.0, 100.0)


def tr(*keys): return Track(keys)


def f(track, t): return float(track(t))


def window(t, a, b, fade=0.25):
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def model():
    m = TC.build(saddle_on=True); P.pack(m, TC.TEX_W); return m.spec()


S = model()
SIDES = ("l", "r")
TAILS = TC.TAILS
STIFF = (1.0, 0.4, 0.26, 0.18)       # the ossified tendons: most of any bend is at the root
BALL = {s: world(S, {}, f"toes_{s}") for s in SIDES}
REST_META = {s: chain_angle(S, {}, [f"foot_{s}"]) for s in SIDES}
HIND = {s: {f"{b}_{s}" for b in ("thigh", "shin", "foot", "toes")} for s in SIDES}
FORE = {s: {f"{b}_{s}" for b in ("arm", "forearm", "hand")} for s in SIDES}
HEADB = {"head", "skull", "jaw", "cheek_l", "cheek_r", "adult_bump"}
SKIP = {"saddle"}
STAND_DROP = 0.4
HIND_LEN, FORE_LEN = 38.0, 36.0
RISE = TC.RISE

# ------------------------------------------------------------------ the posture layer
LEVEL = RISE + 2.0          # on four the back slopes 2 degrees down to the shoulders
QCOMP = {"neck1": 9, "neck2": 18, "skull": 2, "tail1": 6, "tail2": 24, "tail3": 8, "tail4": 2,
         "arm": 30, "forearm": -4}


def posture(p, k):
    """k = 0 the tripod at rest, 1 level on all four: the body tips down about the hip, the neck and the tail are
    brought round so the head looks ahead and the tail runs out behind, the arms swing down under the shoulders"""
    if abs(k) < 1e-6:
        return p
    add(p, "body", rot=(-LEVEL * k, 0, 0))
    for b, a in QCOMP.items():
        if b in ("arm", "forearm"):
            for s in SIDES:
                add(p, f"{b}_{s}", rot=(a * k, 0, 0))
        else:
            add(p, b, rot=(a * k, 0, 0))
    return p


def low_of(p, bones=None, skip=SKIP):
    return min(q[:, 1].min() for c, q in geo.cube_points(S, p)
               if (bones is None or c["bone"] in bones) and c["bone"] not in skip and c.get("mat") != "teeth")


def _ground_hands():
    q = posture({}, 1.0)
    out = {}
    for s in SIDES:
        h = world(S, q, f"hand_{s}")
        out[s] = (h[1] - low_of(q, FORE[s]) + 0.6, h[2] - 1.0)
    return out


GROUND = _ground_hands()     # the hands' targets (y, z of the wrist) on all four


# ------------------------------------------------------------------ plumbing
def solve_arm(pose, s, target, pitch, iters=20):
    names = [f"arm_{s}", f"forearm_{s}"]
    th0 = np.array([pose.get(n, ([0, 0, 0],))[0][0] for n in names], float)
    th = th0 + np.array([-6.0, 12.0])

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


def plant_f(p, s, dy=0.0, dz=0.0, pitch=0.0, clear=-0.05, w=1.0):
    """the hand to its place on the ground (w = 1) or part of the way there from where it hangs (w < 1)"""
    g = GROUND[s]
    if w < 1.0:
        h = world(S, p, f"hand_{s}")
        target = (h[1] * (1 - w) + (g[0] + dy) * w, h[2] * (1 - w) + (g[1] + dz) * w)
    else:
        target = (g[0] + dy, g[1] + dz)
    for _ in range(4):
        solve_arm(p, s, target, pitch * w + chain_angle(S, p, [f"hand_{s}"]) * (1 - w) if w < 1 else pitch)
        if clear is None: break
        lo = low_of(p, FORE[s])
        if lo > clear - 0.02: break
        target = (target[0] + clear - lo, target[1])


def free_arms(p, clear=0.3):
    """hanging arms never through the ground: fold the elbow up until the hand clears it"""
    for s in SIDES:
        for _ in range(30):
            if low_of(p, FORE[s]) >= clear: break
            add(p, f"arm_{s}", rot=(-1.5, 0, 0)); add(p, f"forearm_{s}", rot=(2.5, 0, 0))


def lift_head(p, clear=0.3):
    for _ in range(30):
        if low_of(p, HEADB) >= clear: break
        add(p, "neck1", rot=(1.5, 0, 0))
    return p


def lift_tail(p, clear=0.0):
    for i, b in enumerate(TAILS):
        for _ in range(20):
            if low_of(p, set(TAILS[i:])) >= clear: break
            add(p, b, rot=(-1.5, 0, 0))
    return p


def stand(p, k=0.0, fore=(0, 0), hind=(0, 0), clear=0.3):
    """the stance at posture k: the hind feet planted, the tail and the head off the ground; the hands hang (k < 0.35),
    reach for the ground (0.35..0.9) or stand on it"""
    posture(p, k)
    lift_head(p, clear)
    lift_tail(p, 0.0)
    for i, s in enumerate(SIDES):
        plant_h(p, s, 0, hind[i])
    w = smooth((k - 0.35) / 0.55)
    if w > 0.01:
        for i, s in enumerate(SIDES):
            plant_f(p, s, 0, fore[i], w=w, clear=-0.05 if w > 0.98 else 0.2)
    else:
        free_arms(p)
    return p


def head(p, pitch=0.0, yaw=0.0, roll=0.0, k=(0.35, 0.35, 0.3)):
    for b, w in zip(("neck1", "neck2", "skull"), k):
        add(p, b, rot=(pitch * w, yaw * w, roll * w))


def jaw(p, a): add(p, "jaw", rot=(a, 0, 0))


def cheeks(p, k):
    add(p, "cheek_l", rot=(0, 0, -7 * k)); add(p, "cheek_r", rot=(0, 0, 7 * k))


def chew(p, t, t0, t1, T=0.5):
    c = window(t, t0, t1, 0.1) * max(0.0, math.sin(W(t - t0, T)))
    o = window(t, t0, t1, 0.1) * max(0.0, -math.sin(W(t - t0, T)))
    jaw(p, -5 * o); cheeks(p, c)
    return c


def tail(p, yaw=0.0, pitch=0.0):
    for b, k in zip(TAILS, STIFF): add(p, b, rot=(pitch * k, yaw * k, 0))


def tail_sway(p, t, Tc, yaw, pitch=0.0, ph=0.0):
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        a = W(t, Tc) + ph - 0.25 * i
        add(p, b, rot=(pitch * k * math.sin(2 * a - 0.6), yaw * k * math.sin(a), 0))


def beam(p, t, fn, axis=1, delay=0.07, loop=None):
    for k, (b, w) in enumerate(zip(TAILS, STIFF)):
        u = t - delay * (1 + 0.5 * k)
        v = fn(u % loop if loop else max(0.0, u)) * w
        r = [0.0, 0.0, 0.0]; r[axis] = v
        add(p, b, rot=tuple(r))


def arms_sway(p, t, T, amp=2.0):
    """the hanging arms swing a little after the body, the left a beat behind the right"""
    for s, o in (("l", 0.0), ("r", 1.1)):
        add(p, f"arm_{s}", rot=(amp * wave(t, T, o - 0.6), 0, 0))
        add(p, f"forearm_{s}", rot=(1.5 * amp * wave(t, T, o - 1.2), 0, 0))


def alive_upper(p, t, k=1.0, period=3.4, slow=None):
    head(p, -0.6 * k * wave(t, period, -0.5))
    add(p, "jaw", rot=(-0.3 * k * max(0.0, wave(t, period, -0.8)), 0, 0))
    for i, (b, w) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0.5 * k * w * wave(t, period, -0.5 - 0.3 * i), 1.5 * k * w * wave(t, (slow or period * 2.2), -0.7 - 0.3 * i), 0))


def breathe(p, t, T=3.2, amp=1.0, drop=STAND_DROP):
    """on the tripod the breath lifts the huge belly: the body rocks up on the in-breath"""
    br = math.sin(W(t, T))
    add(p, "body", rot=(0.6 * amp * br, 0, 0), pos=(0, -drop - 0.2 * amp * (1 + br), 0))
    head(p, -0.6 * amp * br)
    arms_sway(p, t, T, 1.2 * amp)
    return br


def settle(p):
    lo = low_of(p)
    if lo < -0.05: add(p, "root", pos=(0, -lo, 0))
    return p


def shift_to_ground(p):
    lo = low_of(p); add(p, "root", pos=(0, -lo, 0)); return p


def blend(a, b, w):
    out = {}
    for bone in set(a) | set(b):
        ea = a.get(bone, ([0, 0, 0], [0, 0, 0])); eb = b.get(bone, ([0, 0, 0], [0, 0, 0]))
        out[bone] = ([ea[0][i] * (1 - w) + eb[0][i] * w for i in range(3)], [ea[1][i] * (1 - w) + eb[1][i] * w for i in range(3)])
    return out


def rear(p, deg):
    add(p, "body", rot=(deg, 0, 0))


def landing(x):
    x %= 1.0
    return -1.0 + 2.0 * smooth(x / 0.3) if x < 0.3 else 1.0 - 2.0 * smooth((x - 0.3) / 0.7)


def counter_legs(p, roll, shift_x=0.0, yaw=0.0, fore=True):
    hx = math.degrees(math.atan2(-shift_x, HIND_LEN)); fx = math.degrees(math.atan2(-shift_x, FORE_LEN))
    for s in SIDES:
        add(p, f"thigh_{s}", rot=(0, -yaw, -roll + hx))
        if fore:
            add(p, f"arm_{s}", rot=(0, -yaw, -roll + fx))


# ------------------------------------------------------------------ gaits on four
LATERAL = {"lh": 0.0, "lf": 0.75, "rh": 0.5, "rf": 0.25}


def foot_cycle(p, ph, feet, stride, duty, lift, flift, fstride=None):
    fstride = stride if fstride is None else fstride
    for foot, o in feet.items():
        s, kind = foot[0], foot[1]
        st_ = stride if kind == "h" else fstride
        u = (ph + o) % 1.0
        if u < duty:
            st = u / duty; dz = -st_ * duty / 2 + st_ * duty * st; ly = 0.0; clear = -0.05
            heel = smooth(max(0.0, (st - 0.6) / 0.4)); sw = 0.0
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = st_ * duty / 2 - st_ * duty * e; heel = 0.0
            ly = (lift if kind == "h" else flift) * math.sin(math.pi * min(1, sw * 1.1)) ** 1.2
            clear = 0.6 * math.sin(math.pi * sw) ** 0.5
        if kind == "h":
            meta = 22 * heel + 20 * (1 - smooth(sw / 0.4)) * (sw > 0) - 14 * math.sin(math.pi * sw)
            toe = -24 * math.sin(math.pi * min(1, sw * 1.1)) + 3 * smooth((sw - 0.7) / 0.3) * (sw > 0)
            plant_h(p, s, ly, dz, meta, toe, clear)
        else:
            pitch = -20 * heel - 36 * math.sin(math.pi * min(1, sw * 1.15))
            plant_f(p, s, ly, dz, pitch, clear)


WALK = (1.8, 34, 0.66, 4.5, 0.6)      # cycle s, stride px, duty, lift px, bob px
RUNP = (0.62, 62, 0.36, 9.5, 1.8)
BWALK = (0.9, 30, 0.6, 5.0, 0.8)      # the calf's walk on two legs
BRUN = (0.5, 58, 0.38, 8.0, 1.4)


def walk(t, Tc=None, stride=None, lift=None, bob=None, roll=3.8, yaw=2.4, head_p=-3.0, tail_amp=5.5):
    """down on all four: the heavy lateral walk; the big belly swings under the rolling hips, the low head nods, the
    deep tail swings late as one beam"""
    Tc = Tc or WALK[0]; stride = stride or WALK[1]; duty = WALK[2]; lift = lift or WALK[3]; bob = WALK[4] if bob is None else bob
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    posture(p, 1.0)
    b2 = landing(2 * ph + 0.05)
    hroll = roll * math.sin(w + 0.3); hyaw = yaw * math.sin(w - 0.5)
    add(p, "body", rot=(0.5 * b2, hyaw, hroll), pos=(0, -STAND_DROP - bob * (0.5 - 0.5 * b2), 0))
    head(p, head_p - 1.4 * landing(2 * ph - 0.14) + 1.8 * math.sin(2 * w - 2.0), -0.8 * hyaw - 1.2 * math.sin(w - 1.6), -0.85 * hroll)
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(k * 0.8 * landing(2 * ph - 0.1 - 0.04 * i), -k * tail_amp * math.sin(w - 1.3 - 0.35 * i), 0))
    counter_legs(p, hroll, yaw=hyaw)
    lift_head(p, 1.0)
    foot_cycle(p, ph, LATERAL, stride, duty, lift, lift * 0.8, fstride=stride * 0.9)
    return p


WALK_TIRED_T = 2.6


def walk_tired(t):
    p = walk(t, Tc=WALK_TIRED_T, stride=24, lift=3.0, bob=0.9, roll=4.8, yaw=2.8, head_p=-14, tail_amp=6.0)
    pant = max(0.0, wave(t, WALK_TIRED_T / 3))
    add(p, "jaw", rot=(-4 - 3 * pant, 0, 0))
    return p


FOLD = (-40.0, 70.0, 30.0)       # the arms tucked under the chest on two legs


def fold_arms(p, k, spread=0.0):
    for s, sx in (("l", 1), ("r", -1)):
        for bone, a in zip(("arm", "forearm", "hand"), FOLD):
            add(p, f"{bone}_{s}", rot=(a * k, 0, spread * sx if bone == "arm" else 0))


def _biped(t, cyc, rise, headp, arms=1.0, settle_it=True):
    """on two legs with the body at `rise` degrees: the posture layer takes it there from the tripod"""
    Tc, stride, duty, lift, bob = cyc
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    bp = 1.0 * math.sin(2 * w - 0.4)
    posture(p, (RISE - rise) / LEVEL)
    for s in SIDES:      # posture swung the arms down for walking on them: here they stay up
        add(p, f"arm_{s}", rot=(-QCOMP["arm"] * (RISE - rise) / LEVEL, 0, 0))
    rear(p, bp)
    add(p, "body", rot=(0, 1.4 * math.sin(w), 2.4 * math.sin(w + 0.35)),
        pos=(0, -STAND_DROP - 1.0 - bob * (0.5 + 0.5 * math.cos(2 * w - 0.9)), 0))
    head(p, headp - bp + 2.5 * math.sin(2 * w - 1.3), -1.2 * math.sin(w), -2 * math.sin(w + 0.35))
    fold_arms(p, arms, spread=6)
    for s, o in (("l", 0.0), ("r", math.pi)):
        add(p, f"arm_{s}", rot=(5 * math.sin(w + o), 0, 0))
    tail_sway(p, t, Tc, 2.0, 0.6)
    lift_head(p, 1.0)
    lift_tail(p, 0.5)
    for s, o in (("l", 0.0), ("r", 0.5)):
        u = (ph + o) % 1.0
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0; clear = 0.1
            meta = 30 * smooth(max(0, (st - 0.5) / 0.5)); toe = 0.0
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e
            ly = lift * math.sin(math.pi * min(1, sw * 1.1)) ** 1.1
            meta = 30 * (1 - smooth(sw / 0.4)) - 26 * math.sin(math.pi * sw)
            toe = -30 * math.sin(math.pi * min(1, sw * 1.15)); clear = 0.8 * math.sin(math.pi * sw) ** 0.5
        plant_h(p, s, ly, dz, meta, toe, clear)
    free_arms(p)
    return settle(p) if settle_it else p


def run(t):
    """the grown one runs on TWO legs like every hadrosaur: the body tipped down from the tripod nearly level, the
    arms folded, the head low and stretched forward, the tail a beam flicking after the hips"""
    p = _biped(t, RUNP, 9, -10)
    beam(p, t, lambda u: -2.5 * math.sin(2 * math.pi * u / RUNP[0] - 1.0), delay=0.04, loop=RUNP[0])
    return p


def biped_walk(t):
    """the calf and the young walk on TWO legs (Cubo et al. 2015): the body tipped up like the mother's tripod,
    short quick steps, the big head bobbing, the little arms tucked"""
    p = _biped(t, BWALK, 20, -2, arms=0.8)
    beam(p, t, lambda u: -2.0 * math.sin(2 * math.pi * u / BWALK[0] - 1.0), delay=0.05, loop=BWALK[0])
    return p


def biped_run(t):
    p = _biped(t, BRUN, 9, -8)
    beam(p, t, lambda u: -3.0 * math.sin(2 * math.pi * u / BRUN[0] - 1.0), delay=0.04, loop=BRUN[0])
    return p


LEGS_LEVEL = {"thigh": 26, "shin": 14, "foot": -6}      # the legs as on a level body (swim, lying on the side)


def level_legs(p, k=1.0):
    for s in SIDES:
        for b, a in LEGS_LEVEL.items():
            add(p, f"{b}_{s}", rot=(a * k, 0, 0))


def swim(t):
    Tc = 1.6; w = W(t, Tc); p = {}
    posture(p, 1.0); level_legs(p)
    add(p, "body", rot=(4 + 1.2 * math.sin(2 * w), 1.5 * math.sin(w), 2.0 * math.sin(w + 0.5)), pos=(0, 0.6 * math.sin(2 * w - 1), 0))
    head(p, 20 - 1.5 * math.sin(2 * w - 1.3), -2 * math.sin(w - 0.8))
    for i, (b, k) in enumerate(zip(TAILS, (1.0, 0.8, 0.7, 0.6))):
        add(p, b, rot=(0, 9 * k * math.sin(w - 0.5 * i), 0))
    for s, o in (("l", 0.0), ("r", math.pi)):
        add(p, f"thigh_{s}", rot=(-12 + 24 * math.sin(w + o), 0, 0))
        add(p, f"shin_{s}", rot=(-6 + 20 * math.sin(w + o - 1.2), 0, 0))
        add(p, f"foot_{s}", rot=(10 + 18 * math.sin(w + o - 1.8), 0, 0))
        add(p, f"arm_{s}", rot=(-4 + 18 * math.sin(w + o + math.pi * 0.5), 0, 0))
        add(p, f"forearm_{s}", rot=(10 + 14 * math.sin(w + o + math.pi * 0.5 - 1.2), 0, 0))
    return p


# ------------------------------------------------------------------ on the tripod
IDLE_T = 8.0
LOOK = Track([(0, (0, 0)), (1.0, (0, 0)), (1.8, (-6, -16), ease_out), (3.0, (-6, -16)), (3.8, (2, 20), ease_out),
              (5.0, (2, 20)), (5.8, (0, 0), smooth), (8.0, (0, 0))])


def idle(t):
    """on the tripod, breathing: the huge belly heaves, the arms hang and swing a little, the low head looks down at
    the nest, then round to one side and the other; it chews; the weight drifts between the feet and the tail"""
    p = {}
    Ti = IDLE_T
    br = breathe(p, t, Ti / 3, 1.0)
    shift = wave(t, Ti, 0.4) + 0.3 * wave(t, Ti / 2, 1.0)
    hroll = 1.2 * shift; hyaw = 0.8 * shift
    add(p, "body", rot=(0, hyaw, hroll))
    lp, ly = LOOK(t)
    head(p, lp + 0.6 * wave(t, Ti / 5, 1.2), ly - 0.8 * hyaw, -0.85 * hroll + 0.15 * ly)
    chew(p, t, 5.8, 7.6, 0.55)
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0.6 * k * wave(t, Ti / 3, -0.6 - 0.3 * i), k * (2.5 * wave(t, Ti, -1.0 - 0.3 * i) + 0.8 * wave(t, Ti / 2, 0.5 - 0.3 * i)), 0))
    counter_legs(p, hroll, yaw=hyaw, fore=False)
    return stand(p)


IDLE_TIRED_T = 3.6


def idle_tired(t):
    """tired: sunk back onto the tail, the flanks heaving, the head hanging, the bill open"""
    p = {}
    Ti = IDLE_TIRED_T
    heave = wave(t, Ti / 4)
    add(p, "body", rot=(-2 + 1.0 * heave, 0, 0.6 * wave(t, Ti, 0.3)), pos=(0, -STAND_DROP - 0.8 - 0.3 * heave, 0.6))
    head(p, -16 - 1.5 * wave(t, Ti / 4, -0.6), 3 * wave(t, Ti, 0.5), 0)
    add(p, "jaw", rot=(-5 - 3 * max(0.0, wave(t, Ti / 4, -0.4)), 0, 0))
    tail(p, pitch=4)
    arms_sway(p, t, Ti / 4, 1.0)
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0.6 * k * heave, 1.5 * k * wave(t, Ti, -0.8 - 0.3 * i), 0))
    counter_legs(p, 0.6 * wave(t, Ti, 0.3), fore=False)
    return stand(p)


TURN_T = 2.4
TURN_ORDER = {"rh": 0.0, "rf": 0.25, "lh": 0.5, "lf": 0.75}


def turn(t, side, Tt=TURN_T, lead_deg=12.0, roll=2.8):
    d = 1.0 if side == "left" else -1.0
    ph = (t / Tt) % 1.0; w = 2 * math.pi * ph; p = {}
    posture(p, 1.0)
    lead = -d
    hroll = roll * math.sin(2 * w + 0.4)
    add(p, "body", rot=(0.4 * math.sin(4 * w), lead * (3.0 + 0.8 * math.sin(2 * w)), hroll), pos=(0, -STAND_DROP, 0))
    head(p, -3.0 + 1.0 * math.sin(4 * w - 1.0), lead * (lead_deg + 2.0 * math.sin(2 * w - 0.8)), -0.8 * hroll)
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0, k * (-lead * 7.0 - 2.0 * math.sin(2 * w - 1.2 - 0.3 * i)), 0))
    counter_legs(p, hroll, yaw=lead * 3.0)
    lift_head(p, 1.0)
    for foot, o in TURN_ORDER.items():
        s, kind = foot[0], foot[1]
        u = (ph + o) % 1.0
        if u < 0.22:
            sw = u / 0.22; up = math.sin(math.pi * sw)
            if kind == "h":
                plant_h(p, s, 3.2 * up ** 1.2, -1.4 * math.cos(math.pi * sw), 12 * up, -18 * up, clear=0.6 * up ** 0.5)
            else:
                plant_f(p, s, 2.5 * up ** 1.2, -1.1 * math.cos(math.pi * sw), -24 * up, clear=0.4 * up ** 0.5)
        else:
            dz = 1.4 - 2.8 * (u - 0.22) / 0.78
            plant_h(p, s, 0.0, dz) if kind == "h" else plant_f(p, s, 0.0, 0.8 * dz)
    return p


def turn_left(t): return turn(t, "left")
def turn_right(t): return turn(t, "right")


def hurt(t):
    p = {}
    e = math.exp(-t / 0.17) * smooth(t / 0.05)
    add(p, "body", rot=(4 * e, -5 * e, -3 * e), pos=(0, -STAND_DROP - 0.4 * e, 1.0 * e))
    head(p, 10 * e, 14 * e, 6 * e)
    for s in SIDES: add(p, f"arm_{s}", rot=(-14 * e, 0, 0))
    beam(p, t, lambda u: 9 * math.exp(-u / 0.22) * smooth(u / 0.05), delay=0.06)
    alive_upper(p, t, k=0.5)
    counter_legs(p, -3 * e, fore=False)
    return stand(p)


def attack(t):
    """the mother's charge: she rocks back onto the tail, the head tucked with the hump forward, then throws her whole
    front down and forward into the target, chest, arms and the deep head together (the hit at 0.5 s), and rocks back
    up onto the tripod"""
    p = {}
    back = f(tr((0, 0), (0.3, 1, ease_out), (0.42, 1), (0.5, 0, ease_in), (1.2, 0)), t)
    lunge = f(tr((0, 0), (0.38, 0), (0.5, 1, ease_in), (0.7, 0.85), (1.2, 0, smooth)), t)
    tuck = f(tr((0, 0), (0.25, 1, ease_out), (0.8, 1), (1.2, 0, smooth)), t)
    rear(p, 8 * back)
    posture(p, 0.55 * lunge)
    add(p, "body", rot=(0, 5 * lunge, -3 * lunge), pos=(-0.6 * lunge, -STAND_DROP - 0.6 * lunge, 2 * back - 6 * lunge))
    head(p, -16 * tuck + 6 * lunge, -6 * lunge, 0)
    for s in SIDES:
        add(p, f"arm_{s}", rot=(-10 * back + 28 * lunge, 0, 0)); add(p, f"forearm_{s}", rot=(-20 * lunge, 0, 0))
    tail(p, yaw=-6 * lunge, pitch=-3 * back)
    beam(p, t, lambda u: -5 * f(tr((0, 0), (0.38, 0), (0.5, 1, ease_in), (0.7, 0.85), (1.2, 0, smooth)), u), delay=0.06)
    lift_head(p)
    lift_tail(p)
    for s in SIDES: plant_h(p, s, 0, 2.0 * lunge)
    free_arms(p, 0.2)
    return settle(p)


KICK_BACK_T = 1.6
KB_LOAD = tr((0, 0), (0.46, 1, ease_out), (0.54, 1.0), (0.67, 0.25, ease_in), (1.05, 0.0, smooth), (1.6, 0))
KB_DRIVE = tr((0, 0), (0.52, 0), (0.64, 1, ease_in), (0.74, 0.9), (1.2, 0, smooth), (1.6, 0))
KB_LOOK = tr((0, 0), (0.3, 1, ease_out), (1.15, 1), (1.6, 0, smooth))


def kick_back(t):
    """something behind her: the head swings round the flank, she sits back on the tail and the left foot, and the
    right hind is drawn up and driven back (the blow at 0.64 s)"""
    p = {}
    load = float(KB_LOAD(t)); drive = float(KB_DRIVE(t)); look = float(KB_LOOK(t))
    tip = max(load, drive)
    roll = -3.2 * tip
    add(p, "body", rot=(2.0 * tip, 4 * look, roll), pos=(0.5 * tip, -STAND_DROP - 0.9 * tip, 0.8 * tip))
    head(p, -6 * look, 40 * look, -10 * look)
    tail(p, yaw=6 * tip, pitch=3 * tip)
    beam(p, t, lambda u: 12 * float(KB_DRIVE(u)) + 4 * float(KB_LOAD(u)), delay=0.07)
    alive_upper(p, t, k=0.5)
    counter_legs(p, roll, shift_x=0.5 * tip, fore=False)
    add(p, "thigh_r", rot=(0, 0, -8 * drive))
    lift_head(p); lift_tail(p)
    plant_h(p, "l")
    plant_h(p, "r", 5.5 * load + 5 * drive, 2 * load + 12 * drive, -22 * load + 36 * drive, -18 * load + 10 * drive, clear=None)
    free_arms(p)
    return settle(p)


BODY_SHOVE_T = 1.6
HC = tr((0, 0), (0.48, -1.0, ease_out), (0.56, -0.95), (0.66, 1.0, ease_in), (0.76, 1.1), (1.6, 0, back_out))


def body_shove(t):
    """the side swipe of the heavy body: she swings the belly, the hip and the root of the tail sideways into the
    attacker at her flank (0.66 s)"""
    p = {}
    s_ = float(HC(t)); a = max(0.0, s_); b = max(0.0, -s_)
    jolt = math.exp(-((t - 0.68) / 0.05) ** 2)
    yaw = -9.0 * a + 4.0 * b
    roll = 5.0 * a - 3.0 * b
    shift = -1.4 * a + 0.7 * b
    add(p, "body", rot=(-1.5 * a + 0.5 * jolt, yaw, roll), pos=(shift, -STAND_DROP - 0.4 * a - 0.3 * jolt, 0))
    head(p, -6 * a - 4 * b, 26 * a - 14 * b - 0.8 * yaw, -4 * a)
    tail(p, yaw=-12 * a + 5 * b)
    beam(p, t, lambda u: -14 * max(0.0, float(HC(u))) + 4 * max(0.0, -float(HC(u))), delay=0.08)
    for s, sx in (("l", 1), ("r", -1)):
        add(p, f"arm_{s}", rot=(0, 0, 10 * sx * a))
    alive_upper(p, t, k=0.5)
    counter_legs(p, roll, shift_x=shift, yaw=yaw, fore=False)
    return stand(p)


def eat(t):
    """takes a mouthful from the hand: the head down from the tripod, a clip with the broad bill, the chew"""
    p = {}
    dn = f(tr((0, 0), (0.45, 1, smooth), (0.8, 1), (1.0, 0.3, ease_out), (2.4, 0.3), (2.8, 0, smooth)), t)
    breathe(p, t, 2.8, 0.5)
    head(p, -18 * dn)
    jaw(p, f(tr((0, 0), (0.5, -10, ease_out), (0.7, -1, ease_in), (2.8, 0)), t))
    chew(p, t, 1.0, 2.5, 0.45)
    tail_sway(p, t, 2.8, 2.0)
    alive_upper(p, t, k=0.3)
    return stand(p, 0.2 * dn)


def graze(t):
    """drops forward onto all four, crops low plants with short side-to-side clips, then rocks back up and chews"""
    p = {}
    dn = f(tr((0, 0), (0.7, 1, smooth), (2.3, 1), (3.0, 0, smooth), (3.4, 0)), t)
    breathe(p, t, 3.4, 0.5)
    sweep = math.sin(W(t - 0.7, 0.9)) * window(t, 0.7, 2.3, 0.15)
    head(p, -40 * dn, 10 * sweep, -3 * sweep)
    clip = sum(window(t, c - 0.12, c, 0.05) for c in (0.95, 1.4, 1.85, 2.2))
    jaw(p, -9 * clip)
    chew(p, t, 2.6, 3.4, 0.4)
    tail_sway(p, t, 3.4, 2.0)
    alive_upper(p, t, k=0.3)
    return stand(p, dn, fore=(-1.5 * dn, -1.5 * dn), clear=0.2)


def drink(t):
    p = {}
    dn = f(tr((0, 0), (0.8, 1, smooth), (2.6, 1), (3.2, 0.0, smooth), (3.6, 0)), t)
    breathe(p, t, 3.6, 0.4)
    lap = window(t, 1.0, 2.5, 0.15) * math.sin(W(t, 0.36))
    head(p, -50 * dn + 2 * lap)
    jaw(p, -4 * max(0, lap))
    head(p, 10 * window(t, 2.7, 3.2, 0.1))
    for s, sx in (("l", 1), ("r", -1)): add(p, f"arm_{s}", rot=(0, 0, 6 * sx * dn))
    tail(p, pitch=-2 * dn)
    return stand(p, dn, fore=(-2.0 * dn, -2.0 * dn), clear=0.0)


def rear_browse(t):
    """she rears up off the tripod to the high leaves: the body nearly upright on the hind legs and the tail, the arms
    reaching forward, two clips of the bill, a chew up there, then back down onto the tripod"""
    p = {}
    up = f(tr((0, 0), (0.8, 1, ease_out), (3.4, 1), (4.2, 0, smooth)), t)
    rear(p, 22 * up)
    add(p, "body", pos=(0, -STAND_DROP, 0.8 * up))
    head(p, 18 * up + 6 * window(t, 1.0, 2.4, 0.2), 0, 0, k=(0.5, 0.3, 0.2))
    clip = sum(window(t, c - 0.12, c, 0.05) for c in (1.3, 1.9))
    jaw(p, -11 * clip)
    chew(p, t, 2.2, 3.3, 0.45)
    for s, sx in (("l", 1), ("r", -1)):
        add(p, f"arm_{s}", rot=(10 * up, 0, 4 * sx * up)); add(p, f"forearm_{s}", rot=(-30 * up, 0, 0))
        add(p, f"hand_{s}", rot=(-10 * up, 0, 0))
    tail(p, pitch=-14 * up)
    return settle(stand(p))


# ------------------------------------------------------------------ the voice: a plain nose, no sacs, no crest
def _call_pose(p, k, beat, rise=1.0, gape=4.0):
    """the head up off the nest and pushed forward, the bill a little open, the throat and the belly pulsing"""
    head(p, 20 * k * rise, 0, 0, k=(0.5, 0.3, 0.2))
    add(p, "skull", rot=(-3 * k * rise + 2 * beat, 0, 0))
    add(p, "body", rot=(2.0 * k + 1.2 * beat, 0, 0), pos=(0, 0.4 * beat, 0))
    add(p, "neck1", rot=(-2.0 * beat, 0, 0))
    jaw(p, -gape * k * (0.4 + 0.6 * beat))


def colony_call(t):
    """the colony's call: short and nasal, two quick notes with the head thrown up and forward off the tripod"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (2.0, 1), (2.6, 0, smooth)), t)
    beat = window(t, 0.55, 0.95, 0.1) + window(t, 1.2, 1.6, 0.1)
    breathe(p, t, 2.6, 0.4)
    _call_pose(p, k, beat)
    tail(p, pitch=-2 * k)
    beam(p, t, lambda u: -2.0 * (window(u, 0.55, 0.95, 0.1) + window(u, 1.2, 1.6, 0.1)), axis=0, delay=0.06)
    return stand(p)


def answer(t):
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (1.4, 1), (2.0, 0, smooth)), t)
    beat = window(t, 0.6, 1.1, 0.12)
    breathe(p, t, 2.0, 0.4)
    _call_pose(p, k, 0.7 * beat, rise=0.6, gape=3.0)
    return stand(p)


def call(t):
    p = {}
    k = f(tr((0, 0), (0.5, 1, ease_out), (2.2, 1), (2.8, 0, smooth)), t)
    beat = window(t, 0.7, 1.9, 0.2) * (0.7 + 0.3 * math.sin(W(t, 0.2)))
    breathe(p, t, 2.8, 0.4)
    _call_pose(p, k, beat, rise=0.8)
    return stand(p)


def alarm(t):
    """the alarm: she rears higher off the tripod with a short hard bellow, the arms flung up, the tail lifted, then
    drops back ready to run in a block"""
    p = {}
    k = f(tr((0, 0), (0.15, 1, ease_out), (1.5, 1), (2.2, 0, smooth)), t)
    up = f(tr((0, 0), (0.15, 0), (0.4, 1, ease_out), (1.3, 1), (1.8, 0, ease_in), (2.2, 0)), t)
    beat = window(t, 0.5, 1.0, 0.08)
    rear(p, 14 * up)
    add(p, "body", pos=(0, -STAND_DROP, 0.6 * up))
    _call_pose(p, k, 1.4 * beat, rise=1.2, gape=7.0)
    for s, sx in (("l", 1), ("r", -1)):
        add(p, f"arm_{s}", rot=(-22 * up, 0, 8 * sx * up)); add(p, f"forearm_{s}", rot=(30 * up, 0, 0))
    tail(p, pitch=-8 * k)
    return settle(stand(p))


# ------------------------------------------------------------------ the nest
def cover_nest(t):
    """the mother covers the eggs: she drops forward and to one side, tears a bunch of leaves and stems with the bill,
    rocks back up onto the tripod with them and lets them fall over the nest in front with a shake; then the other
    side (a HYPOTHESIS: rotting plants warming the eggs)"""
    p = {}
    T = 2.2
    u = t % T
    side = 1.0 if t < T else -1.0
    dn = f(tr((0, 0), (0.5, 1, smooth), (0.85, 1), (1.3, 0.1, ease_out), (1.8, 0.15), (2.2, 0, smooth)), u)
    swing = f(tr((0, 1), (0.85, 1), (1.4, 0, smooth), (2.2, 0)), u)
    pull = window(u, 0.55, 0.85, 0.08)
    drop = window(u, 1.45, 1.8, 0.06)
    breathe(p, t, 4.4, 0.4)
    head(p, -36 * dn + 4 * pull - 14 * window(u, 1.3, 1.9, 0.15), 30 * side * swing, -6 * side * swing)
    add(p, "body", rot=(0, 6 * side * swing * dn, 3 * side * dn))
    jaw(p, -7 * window(u, 0.4, 0.6, 0.06) - 9 * drop)
    add(p, "skull", rot=(0, 0, 8 * math.sin(W(u, 0.18)) * drop))
    tail_sway(p, t, 4.4, 2.0)
    alive_upper(p, t, k=0.3, period=4.4)
    return stand(p, 0.75 * dn, fore=(-1.0 * dn, -1.0 * dn), clear=0.0)


def feed_young(t):
    """feeds the calf in the nest: she bends down over the nest from the tripod, the neck heaves twice as the chewed
    leaves come up, the bill opens low and lets them fall, a nudge; HYPOTHESIS (Horner & Makela 1979; discussed)"""
    p = {}
    dn = f(tr((0, 0), (0.6, 1, smooth), (2.8, 1), (3.4, 0, smooth)), t)
    heave = sum(math.exp(-((t - c) / 0.18) ** 2) for c in (1.0, 1.6))
    heave2 = sum(math.exp(-((t - c - 0.15) / 0.18) ** 2) for c in (1.0, 1.6))
    breathe(p, t, 3.4, 0.4)
    head(p, -40 * dn, 0, 0)
    add(p, "neck1", rot=(4 * heave, 0, 0)); add(p, "neck2", rot=(-5 * heave2, 0, 0))
    add(p, "body", rot=(-1.5 * heave, 0, 0))
    jaw(p, -10 * window(t, 1.9, 2.5, 0.12))
    add(p, "skull", rot=(3 * window(t, 2.6, 2.9, 0.08), 0, 0))
    tail(p, pitch=-2 * dn)
    alive_upper(p, t, k=0.3)
    return stand(p, 0.45 * dn, clear=0.0)


NEST_GUARD_T = 4.0


def nest_guard(t):
    """over the nest when it is threatened: up on the tripod, the belly over the eggs, the arms held out to the
    sides, the head LOW and forward with the hump to the threat, rocking at it now and then (a loop)"""
    p = {}
    Ti = NEST_GUARD_T
    rock = wave(t, Ti, 0.3)
    add(p, "body", rot=(-4 + 1.2 * rock, 0, 0), pos=(0, -STAND_DROP - 0.6, -0.8 * rock))
    head(p, -14 + 3 * wave(t, Ti / 2), 6 * wave(t, Ti, 1.0), 0)
    jaw(p, -2 - 2 * max(0.0, wave(t, Ti / 2, 0.5)))
    tail(p, pitch=-6)
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0, 2 * k * wave(t, Ti, -0.5 - 0.3 * i), 0))
    for s, sx in (("l", 1), ("r", -1)):
        add(p, f"arm_{s}", rot=(-6, 0, 16 * sx)); add(p, f"forearm_{s}", rot=(10, 0, -6 * sx))
    return stand(p)


def nest_dig(t):
    """heaps the mound: down on all four, one hand scrapes back twice, then the other, the head down watching"""
    p = {}
    dn = f(tr((0, 0), (0.5, 1, smooth), (2.5, 1), (3.0, 0, smooth)), t)
    breathe(p, t, 3.0, 0.4)
    head(p, -26 * dn, 0, 0)
    tail_sway(p, t, 3.0, 1.5)
    posture(p, dn)
    lift_head(p, 0.3); lift_tail(p)
    for s in SIDES: plant_h(p, s)
    w = smooth((dn - 0.35) / 0.55)
    for s, t0 in (("l", 0.6), ("r", 1.55)):
        u = (t - t0) / 0.9
        if 0 <= u <= 1.0 and w > 0.9:
            sc = math.sin(math.pi * u)
            dz = 4.0 * math.cos(2 * math.pi * u)
            plant_f(p, s, 2.2 * max(0.0, math.sin(2 * math.pi * u)), dz - 1, pitch=-20 * sc, clear=None)
        elif w > 0.01:
            plant_f(p, s, 0, -1.0, w=w, clear=-0.05 if w > 0.98 else 0.2)
    if w <= 0.01:
        free_arms(p)
    add(p, "body", rot=(0, 0, 1.0 * window(t, 0.6, 1.5, 0.15) - 1.0 * window(t, 1.55, 2.45, 0.15)))
    return settle(p)


def nuzzle(t):
    """touches the calf with the bill: she bends low and to the side, a slow push and a lift"""
    p = {}
    dn = f(tr((0, 0), (0.6, 1, smooth), (1.8, 1), (2.4, 0, smooth)), t)
    push = window(t, 0.9, 1.5, 0.15)
    breathe(p, t, 2.4, 0.4)
    head(p, -40 * dn + 4 * push, 16 * dn, -6 * dn)
    add(p, "skull", rot=(-4 * push, 0, 0))
    tail_sway(p, t, 2.4, 2.0)
    return stand(p, 0.6 * dn, clear=0.0)


def adopt(t):
    """an orphan: she sniffs it head to tail, bent low (three quick sniffs), lifts the head, a soft call, accepts"""
    p = {}
    dn = f(tr((0, 0), (0.5, 1, smooth), (1.8, 1), (2.3, 0, smooth), (3.0, 0)), t)
    sweep = window(t, 0.5, 1.8, 0.15) * math.sin(W(t - 0.5, 1.3))
    sniff = sum(window(t, c, c + 0.08, 0.03) for c in (0.7, 1.1, 1.5))
    k = f(tr((0, 0), (2.2, 0), (2.5, 1, ease_out), (3.0, 0.6)), t)
    breathe(p, t, 3.0, 0.4)
    head(p, -36 * dn, 18 * sweep, 0)
    add(p, "skull", rot=(2 * sniff, 0, 0))
    _call_pose(p, k, window(t, 2.5, 2.85, 0.08), rise=0.5, gape=2.5)
    return stand(p, 0.6 * dn, clear=0.0)


# ------------------------------------------------------------------ lying down (the body levelled first)
FOLD_F = (-64.0, 132.0, -74.0)


def lie(p, k=1.0, kh=None):
    kh = k if kh is None else kh
    kk = max(k, kh)
    posture(p, kk)
    add(p, "body", pos=(0, -STAND_DROP * kk, 0))
    b0 = low_of(p, {"body"})
    q = {}; posture(q, 1.0); bq = low_of(q, {"body"})
    add(p, "body", pos=(0, -min(b0, bq) * k, 0))
    up = k - kh
    if up > 0: add(p, "body", rot=(-12 * up, 0, 0))
    tail(p, pitch=-2 * k)
    head(p, 22 * k, 0, 0)
    wf = smooth((k - 0.3) / 0.7)
    for s in SIDES:
        plant_h(p, s, 0.0, 3.5 * kh, meta=-40 * kh, toe=0.0, clear=0.0)
        if kk > 0.35:
            plant_f(p, s, 0.0, -2 * k, pitch=0.0, clear=0.0, w=smooth((kk - 0.35) / 0.55))
        if wf > 0:
            for bone, fa in zip(("arm", "forearm", "hand"), FOLD_F):
                add(p, f"{bone}_{s}")
                e = p[f"{bone}_{s}"]; e[0][0] = e[0][0] * (1 - wf) + fa * wf
    if kk <= 0.35:
        free_arms(p)
    lift_tail(p)
    return p


def head_back(p, k=1.0, side=1.0):
    add(p, "neck1", rot=(-6 * k, 50 * k * side, 0)); add(p, "neck2", rot=(-6 * k, 56 * k * side, -14 * k * side))
    add(p, "skull", rot=(-12 * k, 26 * k * side, -18 * k * side))
    tail(p, yaw=14 * k * side)


def ko_pose(p, k=1.0, t=0.0):
    br = math.sin(W(t, 4.2))
    posture(p, k); level_legs(p, k)
    add(p, "body", rot=(0, 0, 82 * k), pos=(0, -6.0 * k, 0))
    head(p, -8 * k + 0.5 * br, 0, 12 * k)
    jaw(p, -2 * k)
    tail(p, pitch=-2 * k)
    for s, sg in (("l", 1), ("r", -1)):
        add(p, f"thigh_{s}", rot=(14 * k, 0, -6 * k * sg)); add(p, f"shin_{s}", rot=(-10 * k, 0, 0)); add(p, f"foot_{s}", rot=(18 * k, 0, 0))
        add(p, f"arm_{s}", rot=(-12 * k, 0, -4 * k * sg)); add(p, f"forearm_{s}", rot=(-6 * k, 0, 0)); add(p, f"hand_{s}", rot=(14 * k, 0, 0))
    add(p, "body", pos=(0, 0.25 * br * k, 0))
    return p


def sit(t):
    p = {}; br = math.sin(W(t, 4.0))
    lie(p)
    add(p, "body", rot=(0.3 * br, 0, 0), pos=(0, 0.12 * (1 + br), 0))
    a = window(t, 2.5, 4.4, 0.6)
    head(p, 4 - 0.4 * br, -22 * a, 3 * a)
    chew(p, t, 5.4, 7.2, 0.55)
    return settle(lift_tail(lift_head(p, 0.0)))


def sleep(t):
    p = {}; br = math.sin(W(t, 5.0))
    lie(p)
    add(p, "body", rot=(0.4 * br, 0, 0), pos=(0, 0.12 * (1 + br), 0))
    head(p, -22, 0, 0)
    head_back(p)
    return settle(lift_tail(lift_head(p, 0.0)))


def nest_sleep(t):
    p = {}; br = math.sin(W(t, 2.6))
    lie(p)
    add(p, "body", rot=(0.6 * br, 0, 0), pos=(0, 0.1 * (1 + br), 0))
    head(p, -26, 0, 0)
    head_back(p, 1.15)
    tail(p, yaw=10)
    return settle(lift_tail(lift_head(p, 0.0)))


NEST_BEG_T = 1.6


def nest_beg(t):
    p = {}
    lie(p)
    bob = max(0.0, wave(t, NEST_BEG_T / 2))
    add(p, "body", rot=(4 + 2 * bob, 0, 0), pos=(0, 0.6 + 0.3 * bob, 0))
    head(p, 26 + 10 * bob, 6 * wave(t, NEST_BEG_T, 0.4), 0, k=(0.45, 0.35, 0.2))
    jaw(p, -12 - 6 * bob)
    return settle(lift_tail(lift_head(p, 0.0)))


def wake_sleep(t):
    p = {}
    kb = f(tr((0, 1), (0.8, 0, smooth), (2.4, 0)), t)
    kh = f(tr((0, 1), (0.9, 1), (1.5, 0, smooth), (2.4, 0)), t)
    k = f(tr((0, 1), (1.4, 1), (2.1, 0, smooth), (2.4, 0)), t)
    lie(p, k, kh=kh)
    head(p, -22 * kb, 0, 0)
    head_back(p, kb)
    return settle(lift_tail(lift_head(p, 0.0)))


def knocked_out(t):
    return shift_to_ground(ko_pose({}, 1.0, t))


def _going_down(t):
    p = {}
    st = window(t, 0.0, 0.6, 0.2)
    kh = f(tr((0, 0), (0.3, 0), (0.8, 1, ease_in), (2.0, 1)), t)
    k = f(tr((0, 0), (0.6, 0), (1.1, 1, ease_in), (2.0, 1)), t)
    add(p, "body", rot=(0, 3 * st * math.sin(W(t, 0.6)), 5 * st), pos=(1.0 * st, 0, 0))
    lie(p, max(k, 0.0), kh=max(kh, k))
    add(p, "body", rot=(10 * (kh - k), 0, 0))
    head(p, -20 * k, -8 * st, 6 * k)
    return settle(lift_tail(lift_head(p, 0.0)))


_DOWN = []


def death(t):
    if t <= 1.3:
        return _going_down(t)
    if not _DOWN: _DOWN.append(_going_down(1.3))
    roll = f(tr((1.3, 0), (2.0, 1, ease_in), (2.12, 0.95), (2.26, 1, smooth), (3.0, 1)), t)
    return shift_to_ground(blend(_DOWN[0], ko_pose({}, 1.0), roll))


def knockout(t):
    if t <= 1.1:
        return _going_down(t * 1.3 / 1.1)
    if not _DOWN: _DOWN.append(_going_down(1.3))
    roll = f(tr((1.1, 0), (1.7, 1, ease_in), (1.8, 0.95), (2.0, 1, smooth)), t)
    return shift_to_ground(blend(_DOWN[0], ko_pose({}, 1.0), roll))


def wake(t):
    roll = f(tr((0, 1), (0.3, 1), (1.1, 0, smooth), (3.4, 0)), t)
    if roll > 0:
        return shift_to_ground(blend(lift_tail(lift_head(lie({}), 0.0)), ko_pose({}, 1.0), roll))
    p = {}
    kh = f(tr((0, 1), (2.0, 1), (2.6, 0, smooth), (3.4, 0)), t)
    k = f(tr((0, 1), (2.5, 1), (3.1, 0, smooth), (3.4, 0)), t)
    lie(p, k, kh=kh)
    sh = window(t, 1.2, 1.9, 0.12)
    head(p, 3 * sh, 14 * sh * math.sin(W(t, 0.32)), 10 * sh * math.sin(W(t, 0.32)))
    return settle(lift_tail(lift_head(p, 0.0)))


def hatch(t):
    p = {}
    k = f(tr((0, 1), (1.3, 1), (2.0, 0, smooth), (2.4, 0)), t)
    up = f(tr((0, 0), (0.25, 0), (0.6, 1, back_out), (2.4, 1)), t)
    sh = window(t, 0.65, 1.1, 0.08)
    lie(p, k)
    head(p, -30 * (1 - up) + 18 * up * k, 12 * sh * math.sin(W(t, 0.16)), 8 * sh * math.sin(W(t, 0.16)))
    head_back(p, 1.0 - up)
    jaw(p, -6 * window(t, 1.2, 1.5, 0.08))
    return settle(lift_tail(lift_head(p, 0.0)))


LIE_DOWN_T, GET_UP_T = 2.9, 2.7


def lie_down(t):
    t = t * 2.6 / LIE_DOWN_T
    p = {}
    kh = float(tr((0, 0), (0.3, 0), (1.1, 1, ease_in), (2.6, 1))(t))
    k = float(tr((0, 0), (0.7, 0), (1.75, 1, ease_in), (2.6, 1))(t))
    look = float(tr((0, 0), (0.4, 1, ease_out), (1.6, 1), (2.6, 0, smooth))(t))
    land = math.exp(-((t - 1.8) / 0.1) ** 2)
    lie(p, k, kh=max(kh, k))
    add(p, "body", rot=(8 * (kh - k) + 0.6 * land, 0, 0))
    head(p, -14 * look + 2 * land, 0, 0)
    alive_upper(p, t, k=0.5)
    return settle(lift_tail(lift_head(p, 0.0)))


def get_up(t):
    t = t * 2.4 / GET_UP_T
    p = {}
    kh = float(tr((0, 1), (0.3, 1), (1.0, 0, smooth), (2.4, 0))(t))
    k = float(tr((0, 1), (0.8, 1), (1.6, 0, smooth), (2.4, 0))(t))
    push = math.exp(-((t - 1.1) / 0.2) ** 2)
    wob = math.exp(-max(0.0, t - 1.6) / 0.25) * math.sin(2 * math.pi * 2.2 * (t - 1.6)) * smooth((t - 1.55) / 0.1)
    lie(p, k, kh=kh)
    add(p, "body", rot=(0, 0, 1.4 * wob))
    head(p, -10 * push, 0, 0)
    alive_upper(p, t, k=0.5)
    return settle(lift_tail(lift_head(p, 0.0)))


# ------------------------------------------------------------------ with its owner
RIDDEN_T = 6.0


def ridden_idle(t):
    """standing still with a rider: level on all four (posture 1), so the saddle is not tipped 34 degrees; breathing,
    looking round, the tail swaying"""
    p = {}
    br = breathe(p, t, RIDDEN_T / 2, 0.8)
    lp, ly = LOOK(t * 8.0 / RIDDEN_T)
    head(p, 0.5 * lp, 0.7 * ly)
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0, k * 2.5 * wave(t, RIDDEN_T, -1.0 - 0.3 * i), 0))
    return stand(p, 1.0)


def beg(t):
    p = {}; breathe(p, t, 2.4)
    nudge = sum(window(t, c, c + 0.18, 0.07) for c in (0.5, 1.5))
    note = window(t, 1.0, 1.3, 0.08)
    head(p, -8 + 4 * nudge + 8 * note, 4 * math.sin(W(t, 2.4)), 0)
    jaw(p, -3 * note)
    add(p, "body", rot=(0.8 * note - 2 * nudge, 0, 0), pos=(0, 0, -1.0 * nudge))
    tail_sway(p, t, 2.4, 5.0)
    return stand(p)


def tame(t):
    p = {}
    k = f(tr((0, 0), (0.5, 1, ease_out), (1.4, 1), (1.9, 0, smooth)), t)
    dn = f(tr((0, 0), (1.5, 0), (2.2, 1, smooth), (2.8, 1), (3.2, 0, smooth)), t)
    beat = window(t, 0.6, 1.3, 0.15) * (0.7 + 0.3 * math.sin(W(t, 0.2)))
    breathe(p, t, 3.2, 0.6)
    _call_pose(p, k, beat, rise=0.8)
    head(p, -20 * dn, 0, 0)
    tail(p, pitch=3 * dn)
    return stand(p, 0.3 * dn)


ANIMS = {
    "idle": (idle, IDLE_T, True, "Parado", "no tripé (patas de trás e cauda), respira com a barriga enorme, braços pendurados, olha o ninho"),
    "walk": (walk, WALK[0], True, "Movimento", "cai para QUATRO patas e anda pesado, a barriga balançando, a cauda dura inteira"),
    "run": (run, RUNP[0], True, "Movimento", "corre em duas patas: o corpo desce do tripé quase nivelado, braços dobrados"),
    "biped_walk": (biped_walk, BWALK[0], True, "Só dele", "o filhote e o jovem andam em DUAS patas (Cubo et al. 2015), empinados como a mãe"),
    "biped_run": (biped_run, BRUN[0], True, "Só dele", "o jovem corre em duas patas, corpo nivelado, a cauda batendo"),
    "swim": (swim, 1.6, True, "Movimento", "nada nivelado com a cabeça fora d'água, a cauda funda rema pela raiz"),
    "turn_left": (turn_left, TURN_T, True, "Movimento", "gira no lugar para a esquerda, em quatro patas"),
    "turn_right": (turn_right, TURN_T, True, "Movimento", "gira no lugar para a direita"),
    "walk_tired": (walk_tired, WALK_TIRED_T, True, "Movimento", "anda cansado em quatro patas, cabeça pendida, boca aberta"),
    "idle_tired": (idle_tired, IDLE_TIRED_T, True, "Parado", "parado cansado, sentado na cauda: os flancos arfam, o bico aberto"),
    "colony_call": (colony_call, 2.6, False, "Só dele", "o chamado da colônia: duas notas nasais, a cabeça jogada para cima do tripé"),
    "call": (call, 2.8, False, "Só dele", "o chamado de contato, uma nota mais longa"),
    "answer": (answer, 2.0, False, "Só dele", "responde ao chamado de outro da colônia"),
    "alarm": (alarm, 2.2, False, "Só dele", "o alarme: empina mais alto, braços para cima, berro curto"),
    "cover_nest": (cover_nest, 4.4, False, "Só dele", "cobre os ovos: desce de lado, arranca folhas, volta ao tripé e solta no ninho (hipótese)"),
    "feed_young": (feed_young, 3.4, False, "Só dele", "alimenta o filhote: curvada sobre o ninho, o pescoço arfa duas vezes (hipótese)"),
    "nest_guard": (nest_guard, NEST_GUARD_T, True, "Só dele", "no tripé sobre o ninho, braços abertos, cabeça baixa com o calombo à frente"),
    "nest_dig": (nest_dig, 3.0, False, "Só dele", "desce às quatro patas e raspa a terra do ninho, uma mão e depois a outra"),
    "nuzzle": (nuzzle, 2.4, False, "Só dele", "curva-se e encosta o bico no filhote"),
    "adopt": (adopt, 3.0, False, "Só dele", "cheira o órfão de ponta a ponta, ergue a cabeça e chama baixo: aceito"),
    "rear_browse": (rear_browse, 4.2, False, "Só dele", "empina quase de pé sobre as patas e a cauda para as folhas altas"),
    "nest_beg": (nest_beg, NEST_BEG_T, True, "Só dele", "o filhote no ninho pede comida: deitado, cabeça para cima, boca aberta"),
    "nest_sleep": (nest_sleep, 5.2, True, "Só dele", "o filhote dorme no ninho, encolhido, a cabeça no flanco"),
    "hatch": (hatch, 2.4, False, "Domado", "sai do ovo: a cabeça empurra para cima, sacode, olha e levanta"),
    "eat": (eat, 2.8, False, "Comer", "pega da mão e mastiga, do tripé"),
    "graze": (graze, 3.4, False, "Comer", "desce às quatro patas e pasta baixo, volta ao tripé mastigando"),
    "drink": (drink, 3.6, False, "Comer", "desce às quatro patas e bebe"),
    "attack": (attack, 1.2, False, "Combate", "a investida da mãe: recua na cauda e joga o peito e a cabeça no alvo (golpe em 0,5 s)"),
    "kick_back": (kick_back, KICK_BACK_T, False, "Combate", "senta na cauda e chuta para trás com a pata (golpe em 0,64 s)"),
    "body_shove": (body_shove, BODY_SHOVE_T, False, "Combate", "joga a barriga, a anca e a base da cauda de lado (golpe em 0,66 s)"),
    "hurt": (hurt, 0.6, False, "Combate", "ao levar dano"),
    "death": (death, 3.0, False, "Combate", "desce do tripé, as patas de trás cedem, rola de lado"),
    "knockout": (knockout, 2.0, False, "Descanso", "nocauteado: cambaleia, desce e rola de lado"),
    "knocked_out": (knocked_out, 4.2, True, "Descanso", "nocauteado de lado"),
    "wake": (wake, 3.4, False, "Descanso", "acorda do nocaute: rola, sacode a cabeça, volta ao tripé"),
    "sit": (sit, 8.0, True, "Descanso", "deitado de barriga, cabeça erguida, rumina"),
    "sleep": (sleep, 10.0, True, "Descanso", "dorme com a cabeça no flanco"),
    "wake_sleep": (wake_sleep, 2.4, False, "Descanso", "acorda: traz a cabeça, levanta o quadril e volta ao tripé"),
    "lie_down": (lie_down, LIE_DOWN_T, False, "Descanso", "deita: desce do tripé, o quadril assenta, depois o peito"),
    "get_up": (get_up, GET_UP_T, False, "Descanso", "levanta pelo quadril e empina de volta ao tripé"),
    "ridden_idle": (ridden_idle, RIDDEN_T, True, "Domado", "parado com cavaleiro: nivelado em quatro patas, a sela reta"),
    "beg": (beg, 2.4, True, "Domado", "pede comida: inclina-se para o dono, um empurrão"),
    "tame": (tame, 3.2, False, "Domado", "responde ao dono com um chamado e baixa a cabeça para ele"),
}
