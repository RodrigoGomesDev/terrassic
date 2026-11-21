"""Pachyrhinosaurus animations, from its own study (docs/estudos/15_HERBIVOROS_1_11.md) on the v4 "bisão" rig.

The four-legged plumbing (the forelimb IK, the plant helpers, the lateral walk) follows the Corythosaurus'
(coryanims.py); here on short pillar legs under a barrel, the head hung low off a short neck. What the
Pachyrhinosaurus does that the others do not is its own (the wall, the boss and the river):
- the RING (ring_defence, brace): it swings to face out, shoulders into its neighbour and stands braced, the legs
  wide, the head low so the boss and the hooks face the predator; the brace is held as a loop;
- the BOSS: a short charge of three or four heavy steps that ends boss first (boss_ram, the blow at 0.60 s), the
  forehead pressed to the rival's and pushing, the legs dug in (boss_push / horn_lock), a quick toss of the head to
  the side as a threat or a jab (head_toss, the blow at 0.35 s), the boss rubbed on a trunk or a stone (boss_rub);
- the RIVER: it stops at the bank and lowers the head to smell the water, a forefoot tested on it (hesitate), and
  wades across with the head held high (wade);
- the COLD: it scrapes the snow aside with the beak and the boss to the plants under it (snow_dig);
- the duel's lunge, parry and stagger at the fixed times of every rig, the lunge being a boss ram.

Signs on this rig: body +x = nose up; neck/skull -x = down; jaw -x = open; tail pitch + = down; yaw + = to its left;
thigh/arm +x = the foot swings forward.
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
import pachy as TC
from anim2 import add, world, chain_angle, solve_leg, Track, smooth, ease_out, ease_in, back_out

W = lambda t, T: 2 * math.pi * t / T


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
STIFF = (1.0, 0.6, 0.4)
BALL = {s: world(S, {}, f"toes_{s}") for s in SIDES}
REST_META = {s: chain_angle(S, {}, [f"foot_{s}"]) for s in SIDES}
WRIST = {s: world(S, {}, f"hand_{s}") for s in SIDES}
REST_HAND = {s: chain_angle(S, {}, [f"hand_{s}"]) for s in SIDES}
HIND = {s: {f"{b}_{s}" for b in ("thigh", "shin", "foot", "toes")} for s in SIDES}
FORE = {s: {f"{b}_{s}" for b in ("arm", "forearm", "hand")} for s in SIDES}
HOOKS = tuple(f"hook_{s}{k}" for s in SIDES for k in range(3))
HEADB = {"head", "skull", "jaw", "adult_boss", "young_brow", "frill", "adult_hooks", "male_display",
         "female_display"} | set(HOOKS)
SKIP = {"saddle"}
STAND_DROP = 0.8
HIND_LEN, FORE_LEN = 30.0, 38.0


def low_of(p, bones=None, skip=SKIP):
    return min(q[:, 1].min() for c, q in geo.cube_points(S, p)
               if (bones is None or c["bone"] in bones) and c["bone"] not in skip and c.get("mat") != "teeth")


# ------------------------------------------------------------------ plumbing (from coryanims.py)
def solve_arm(pose, s, target, pitch, iters=20):
    names = [f"arm_{s}", f"forearm_{s}"]
    th0 = np.array([pose.get(n, ([0, 0, 0],))[0][0] for n in names], float)
    th = th0 + np.array([-4.0, 8.0])

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


def plant_f(p, s, dy=0.0, dz=0.0, pitch=0.0, clear=-0.05):
    w = WRIST[s]; target = (w[1] + dy, w[2] + dz)
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
    for i, s in enumerate(SIDES):
        plant_h(p, s, 0, hind[i])
        plant_f(p, s, 0, fore[i])
    return p


def head(p, pitch=0.0, yaw=0.0, roll=0.0, k=(0.55, 0.45)):
    for b, w in zip(("neck", "skull"), k):
        add(p, b, rot=(pitch * w, yaw * w, roll * w))


def jaw(p, a): add(p, "jaw", rot=(a, 0, 0))


def hooks(p, k=0.0, t=0.0, shake=0.0):
    """the frill raised a little (k), the hooks rattling on a shake"""
    if k:
        add(p, "frill", rot=(-6 * k, 0, 0))
    if shake:
        for s, sg in (("l", 1), ("r", -1)):
            add(p, f"hook_{s}0", rot=(shake * math.sin(W(t, 0.12)), 0, 0))


def tail(p, yaw=0.0, pitch=0.0):
    for b, k in zip(TAILS, STIFF): add(p, b, rot=(pitch * k, yaw * k, 0))


def tail_sway(p, t, Tc, yaw, pitch=0.0, ph=0.0):
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        a = W(t, Tc) + ph - 0.35 * i
        add(p, b, rot=(pitch * k * math.sin(2 * a - 0.6), yaw * k * math.sin(a), 0))


def flick(p, t, T=2.6, amp=12.0):
    """the short tail flicked aside now and then (flies)"""
    k = max(0.0, math.sin(W(t, T))) ** 6
    for i, (b, w) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0, amp * k * (0.6 + 0.4 * i), 0))


def breathe(p, t, T=3.2, amp=1.0, drop=STAND_DROP):
    br = math.sin(W(t, T))
    add(p, "body", rot=(0.3 * amp * br, 0, 0), pos=(0, -drop - 0.25 * amp * (1 + br), 0))
    head(p, -0.6 * amp * br)
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


def landing(x):
    x %= 1.0
    return -1.0 + 2.0 * smooth(x / 0.3) if x < 0.3 else 1.0 - 2.0 * smooth((x - 0.3) / 0.7)


def counter_legs(p, roll, shift_x=0.0, yaw=0.0):
    hx = math.degrees(math.atan2(-shift_x, HIND_LEN)); fx = math.degrees(math.atan2(-shift_x, FORE_LEN))
    for s in SIDES:
        add(p, f"thigh_{s}", rot=(0, -yaw, -roll + hx)); add(p, f"arm_{s}", rot=(0, -yaw, -roll + fx))


def splay(p, k):
    """the legs set wide (the brace, the push): the feet out, the body a little lower"""
    for s, sx in (("l", 1), ("r", -1)):
        add(p, f"thigh_{s}", rot=(0, 0, 7 * sx * k)); add(p, f"arm_{s}", rot=(0, 0, 8 * sx * k))
        add(p, f"shin_{s}", rot=(0, 0, -4 * sx * k)); add(p, f"forearm_{s}", rot=(0, 0, -5 * sx * k))


# ------------------------------------------------------------------ gaits
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
            meta = 7 * heel - 8 * math.sin(math.pi * sw)
            toe = -16 * math.sin(math.pi * min(1, sw * 1.1))
            plant_h(p, s, ly, dz, meta, toe, clear)
        else:
            pitch = -14 * heel - 28 * math.sin(math.pi * min(1, sw * 1.15))
            plant_f(p, s, ly, dz, pitch, clear)


WALK = (1.5, 26, 0.66, 4.0, 0.7)        # cycle s, stride px, duty, lift px, bob px (short heavy legs)
RUNP = (0.62, 54, 0.38, 8.0, 2.0)       # the lumbering gallop
CHARGEP = (0.56, 60, 0.36, 7.0, 2.4)    # the charge, head down


def walk(t, Tc=None, stride=None, lift=None, bob=None, roll=2.6, yaw=1.8, head_p=0.0, tail_amp=6.0, nod=4.0):
    """the bison's walk: the heavy head nods down at each forefoot's strike, the hump rolls over the shoulders, the
    short tail swings late"""
    Tc = Tc or WALK[0]; stride = stride or WALK[1]; duty = WALK[2]; lift = lift or WALK[3]; bob = WALK[4] if bob is None else bob
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    b2 = landing(2 * ph + 0.05)
    hroll = roll * math.sin(w + 0.3); hyaw = yaw * math.sin(w - 0.5)
    add(p, "body", rot=(0.5 * b2, hyaw, hroll), pos=(0, -STAND_DROP - bob * (0.5 - 0.5 * b2), 0))
    head(p, head_p - nod * (0.5 + 0.5 * math.sin(2 * w - 1.9)), -0.9 * hyaw - 1.0 * math.sin(w - 1.6), -0.7 * hroll)
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(k * 1.0 * landing(2 * ph - 0.1 - 0.05 * i), -k * tail_amp * math.sin(w - 1.3 - 0.4 * i), 0))
    counter_legs(p, hroll, yaw=hyaw)
    lift_head(p, 1.0)
    foot_cycle(p, ph, LATERAL, stride, duty, lift, lift * 0.9, fstride=stride)
    return settle(p)


WALK_TIRED_T = 2.3


def walk_tired(t):
    p = walk(t, Tc=WALK_TIRED_T, stride=16, lift=2.4, bob=0.6, roll=3.6, yaw=2.2, head_p=-10, tail_amp=3.0, nod=6.0)
    pant = max(0.0, wave(t, WALK_TIRED_T / 3))
    add(p, "jaw", rot=(-4 - 3 * pant, 0, 0))
    add(p, "root", pos=(0, 0.25, 0))
    return p


GALLOP = {"lh": 0.0, "rh": 0.1, "lf": 0.5, "rf": 0.6}


def _gallop(t, cyc, head_p, pump_k):
    Tc, stride, duty, lift, bob = cyc
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    pump = math.sin(w - 0.6)
    add(p, "body", rot=(-1 + 3.5 * math.sin(w + 0.4), 0.6 * math.sin(w), 1.0 * math.sin(w + 0.3)),
        pos=(0, -STAND_DROP - 0.6 - bob * (0.5 + 0.5 * math.cos(w + 0.4)), 0))
    head(p, head_p - pump_k * pump)
    hooks(p, t=t, shake=1.5)
    tail(p, pitch=-6)
    tail_sway(p, t, Tc, 3.0, 2.0)
    lift_head(p, 1.0)
    foot_cycle(p, ph, GALLOP, stride, duty, lift, lift * 1.1)
    return settle(p)


def run(t):
    """the lumbering gallop of a bison: the hump rocking, the head swinging low with the stride"""
    return _gallop(t, RUNP, -4, 5)


def charge(t):
    """with a target: the gallop with the head down and the boss levelled at it"""
    return _gallop(t, CHARGEP, -16, 3)


def swim(t):
    Tc = 1.8; w = W(t, Tc); p = {}
    add(p, "body", rot=(6 + 1.2 * math.sin(2 * w), 1.5 * math.sin(w), 2.0 * math.sin(w + 0.5)), pos=(0, 0.6 * math.sin(2 * w - 1), 0))
    head(p, 28 - 1.5 * math.sin(2 * w - 1.3), -2 * math.sin(w - 0.8))
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(-6 * k, 9 * k * math.sin(w - 0.5 * i), 0))
    for s, o in (("l", 0.0), ("r", math.pi)):
        add(p, f"thigh_{s}", rot=(-8 + 26 * math.sin(w + o), 0, 0))
        add(p, f"shin_{s}", rot=(-6 + 18 * math.sin(w + o - 1.2), 0, 0))
        add(p, f"arm_{s}", rot=(-4 + 24 * math.sin(w + o + math.pi * 0.5), 0, 0))
        add(p, f"forearm_{s}", rot=(10 + 16 * math.sin(w + o + math.pi * 0.5 - 1.2), 0, 0))
    return p


def wade(t):
    """across the river: the walk slowed, the head held high above the water, the feet lifted high"""
    p = walk(t, Tc=1.8, stride=20, lift=6.0, bob=0.5, roll=2.0, yaw=1.4, head_p=24, tail_amp=3.0, nod=2.0)
    hooks(p, 0.3)
    return p


# ------------------------------------------------------------------ standing
IDLE_T = 8.0
LOOK = Track([(0, (0, 0)), (1.0, (0, 0)), (1.8, (6, -16), ease_out), (3.0, (6, -16)), (3.8, (2, 18), ease_out),
              (5.0, (2, 18)), (5.8, (0, 0), smooth), (8.0, (0, 0))])


def idle(t):
    """on four, the head low, breathing; it swings the heavy head round to look, chews, the weight drifting, the short
    tail flicking flies"""
    p = {}
    Ti = IDLE_T
    br = wave(t, Ti / 3)
    shift = wave(t, Ti, 0.4) + 0.3 * wave(t, Ti / 2, 1.0)
    hroll = 1.0 * shift; hyaw = 0.6 * shift
    add(p, "body", rot=(0.3 * br, hyaw, hroll), pos=(0, -STAND_DROP - 0.25 * (1 + br), 0))
    lp, ly = LOOK(t)
    head(p, lp - 0.6 * wave(t, Ti / 3, -0.6), ly - 0.8 * hyaw, -0.7 * hroll + 0.1 * ly)
    c = window(t, 5.8, 7.6, 0.1) * max(0.0, -math.sin(W(t - 5.8, 0.55)))
    jaw(p, -4 * c)
    flick(p, t, Ti / 2)
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0.6 * k * wave(t, Ti / 3, -0.6 - 0.3 * i), 0, 0))
    counter_legs(p, hroll, yaw=hyaw)
    return stand(p)


IDLE_TIRED_T = 3.6


def idle_tired(t):
    p = {}
    Ti = IDLE_TIRED_T
    heave = wave(t, Ti / 4)
    add(p, "body", rot=(-1.0 + 0.8 * heave, 0, 0.5 * wave(t, Ti, 0.3)), pos=(0, -STAND_DROP - 0.5 - 0.35 * heave, 0))
    head(p, -14 - 1.5 * wave(t, Ti / 4, -0.6), 3 * wave(t, Ti, 0.5), 0)
    add(p, "jaw", rot=(-5 - 3 * max(0.0, wave(t, Ti / 4, -0.4)), 0, 0))
    tail(p, pitch=4)
    counter_legs(p, 0.5 * wave(t, Ti, 0.3))
    return stand(p)


TURN_T = 2.0
TURN_ORDER = {"rh": 0.0, "rf": 0.25, "lh": 0.5, "lf": 0.75}


def turn(t, side, Tt=TURN_T, lead_deg=14.0, roll=2.4, strafe=0.0):
    """in place (side = left/right); strafe: the guard's sidestep, the head kept on the rival"""
    d = 1.0 if side == "left" else -1.0
    ph = (t / Tt) % 1.0; w = 2 * math.pi * ph; p = {}
    lead = -d if not strafe else 0.0
    hroll = roll * math.sin(2 * w + 0.4)
    add(p, "body", rot=(0.4 * math.sin(4 * w), lead * (3.0 + 0.8 * math.sin(2 * w)), hroll),
        pos=(d * strafe * 1.2 * math.sin(2 * w), -STAND_DROP - (1.5 if strafe else 0.0), 0))
    head(p, (-10 if strafe else -3.0) + 1.0 * math.sin(4 * w - 1.0), lead * (lead_deg + 2.0 * math.sin(2 * w - 0.8)), -0.8 * hroll)
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0, k * (-lead * 8.0 - 2.0 * math.sin(2 * w - 1.2 - 0.3 * i)), 0))
    counter_legs(p, hroll, yaw=lead * 3.0)
    if strafe:
        splay(p, 0.6)
    lift_head(p, 1.0)
    for foot, o in TURN_ORDER.items():
        s, kind = foot[0], foot[1]
        u = (ph + o) % 1.0
        if u < 0.22:
            sw = u / 0.22; up = math.sin(math.pi * sw)
            if kind == "h":
                plant_h(p, s, 2.6 * up ** 1.2, -1.2 * math.cos(math.pi * sw), 8 * up, -12 * up, clear=0.5 * up ** 0.5)
            else:
                plant_f(p, s, 2.6 * up ** 1.2, -1.0 * math.cos(math.pi * sw), -20 * up, clear=0.4 * up ** 0.5)
        else:
            dz = 1.2 - 2.4 * (u - 0.22) / 0.78
            plant_h(p, s, 0.0, dz) if kind == "h" else plant_f(p, s, 0.0, 0.8 * dz)
    return p


def turn_left(t): return turn(t, "left")
def turn_right(t): return turn(t, "right")
def strafe_left(t): return turn(t, "left", Tt=1.4, strafe=1.0)
def strafe_right(t): return turn(t, "right", Tt=1.4, strafe=1.0)


def hurt(t):
    p = {}
    e = math.exp(-t / 0.17) * smooth(t / 0.05)
    add(p, "body", rot=(2 * e, -4 * e, -3 * e), pos=(0, -STAND_DROP - 0.4 * e, 1.0 * e))
    head(p, 10 * e, 12 * e, 6 * e)
    tail(p, yaw=8 * e, pitch=-6 * e)
    counter_legs(p, -3 * e)
    return stand(p)


# ------------------------------------------------------------------ the boss
def _ram_pose(p, load, drive, steps=0.0, t=0.0):
    """load: the weight back, the head drawn up; drive: the body thrown forward, the head swung down so the boss leads"""
    add(p, "body", rot=(3 * load - 4 * drive, 0, 0), pos=(0, -STAND_DROP - 0.8 * load - 1.0 * drive, 3 * load - 9 * drive))
    head(p, 10 * load - 26 * drive, 0, 0)
    add(p, "skull", rot=(-6 * drive, 0, 0))
    hooks(p, 0.5 * drive)
    tail(p, pitch=-10 * drive + 4 * load)


def boss_ram(t):
    """the short charge of three or four heavy steps, the head dropping at the end so the flat boss strikes first (the
    blow at 0.60 s), the rebound, then back on its feet"""
    p = {}
    load = f(tr((0, 0), (0.18, 1, ease_out), (0.3, 1), (0.42, 0, ease_in), (1.5, 0)), t)
    drive = f(tr((0, 0), (0.3, 0), (0.6, 1, ease_in), (0.7, 0.85), (1.1, 0.2, smooth), (1.5, 0, smooth)), t)
    jolt = math.exp(-((t - 0.62) / 0.05) ** 2)
    _ram_pose(p, load, drive)
    add(p, "body", rot=(-2 * jolt, 0, 0), pos=(0, 0, 2.5 * jolt))
    # the steps: the forefeet reach and stamp as it drives
    st = window(t, 0.3, 0.75, 0.08)
    lift_head(p)
    for i, s in enumerate(SIDES):
        ph = (t - 0.3) / 0.22 + 0.5 * i
        up = st * max(0.0, math.sin(math.pi * (ph % 1.0)))
        plant_f(p, s, 3.0 * up, -8 * drive - 2 * up, -18 * up, clear=None if up > 0.05 else -0.05)
        plant_h(p, s, 2.0 * up * 0.7, -6 * drive, 0, 0, clear=None if up > 0.05 else -0.05)
    return settle(p)


def head_toss(t):
    """the quick threat or jab: the head swung low to one side and tossed up and across (the blow at 0.35 s)"""
    p = {}
    dn = f(tr((0, 0), (0.18, 1, ease_out), (0.3, 1), (0.42, -0.6, ease_in), (0.6, -0.3), (0.9, 0, smooth)), t)
    side = f(tr((0, 0), (0.18, 1, ease_out), (0.3, 1), (0.42, -1, ease_in), (0.6, -0.6), (0.9, 0, smooth)), t)
    add(p, "body", rot=(0, 3 * side, -2 * side), pos=(0, -STAND_DROP, 0))
    head(p, -16 * dn, 22 * side, -14 * side)
    hooks(p, t=t, shake=2.0 * window(t, 0.3, 0.6, 0.05))
    tail(p, yaw=-6 * side)
    return stand(p)


BOSS_PUSH_T = 2.0


def boss_push(t):
    """forehead to forehead (the horn lock): the legs dug in and set wide, the body driving forward in slow heaves, the
    head low and twisting a little as each one pushes"""
    p = {}
    heave = math.sin(W(t, BOSS_PUSH_T))
    add(p, "body", rot=(-5 - 1.5 * heave, 1.5 * heave, 2 * math.sin(W(t, BOSS_PUSH_T / 2))), pos=(0, -STAND_DROP - 2.2, -3 - 1.5 * heave))
    head(p, -24 - 3 * heave, 4 * math.sin(W(t, BOSS_PUSH_T) + 0.8), 5 * heave)
    hooks(p, 0.5)
    splay(p, 1.0)
    tail(p, pitch=-8, yaw=3 * heave)
    for s in SIDES:
        plant_h(p, s, 0, 3.0 + 1.0 * heave, meta=12)
        plant_f(p, s, 0, -1.0)
    return settle(p)


def horn_lock(t):
    return boss_push(t)


def horn_lock_start(t):
    """the last step in and the foreheads meeting: a short ram into the push"""
    p = {}
    drive = f(tr((0, 0), (0.25, 1, ease_in), (0.35, 0.8), (1.0, 1, smooth)), t)
    jolt = math.exp(-((t - 0.27) / 0.05) ** 2)
    add(p, "body", rot=(-5 * drive - 2 * jolt, 0, 0), pos=(0, -STAND_DROP - 2.2 * drive, -3 * drive + 2 * jolt))
    head(p, -24 * drive, 0, 0)
    splay(p, drive)
    tail(p, pitch=-8 * drive)
    for s in SIDES:
        plant_h(p, s, 0, 3.0 * drive, meta=12 * drive)
        plant_f(p, s, 0, -1.0 * drive)
    return settle(p)


def horn_lock_break(t):
    """the foreheads part: it shoves off, backs two steps and shakes the head"""
    p = {}
    k = f(tr((0, 1), (0.4, 0, smooth), (1.2, 0)), t)
    back = f(tr((0, 0), (0.3, 1, ease_out), (0.8, 1), (1.2, 0, smooth)), t)
    sh = window(t, 0.5, 1.0, 0.08)
    add(p, "body", rot=(-5 * k + 2 * back, 0, 0), pos=(0, -STAND_DROP - 2.2 * k, -3 * k + 4 * back))
    head(p, -24 * k + 6 * back, 14 * sh * math.sin(W(t, 0.16)), 10 * sh * math.sin(W(t, 0.16)))
    hooks(p, t=t, shake=2 * sh)
    splay(p, k)
    for s in SIDES:
        plant_h(p, s, 0, 3.0 * k)
        plant_f(p, s, 0, -1.0 * k)
    return settle(p)


def attack(t):
    """the boss swung up into what is in front, from low to high, with the shoulder behind it (the hit at 0.5 s)"""
    p = {}
    load = f(tr((0, 0), (0.3, 1, ease_out), (0.42, 1), (0.5, 0, ease_in), (1.2, 0)), t)
    up = f(tr((0, 0), (0.42, 0), (0.52, 1, ease_in), (0.7, 0.7), (1.2, 0, smooth)), t)
    add(p, "body", rot=(-3 * load + 3 * up, 0, 0), pos=(0, -STAND_DROP - 1.0 * load, 2 * load - 4 * up))
    head(p, -20 * load + 22 * up, 0, 0)
    hooks(p, 0.4 * up)
    tail(p, pitch=-6 * up)
    stand(p, fore=(-2 * up, -2 * up))
    return settle(p)


# ------------------------------------------------------------------ the wall
def _brace_pose(p, k, t=0.0):
    add(p, "body", rot=(-2.5 * k, 0, 0), pos=(0, -STAND_DROP - 1.8 * k, 0))
    head(p, -22 * k + 1.2 * k * math.sin(W(t, 2.2)), 0, 0)
    add(p, "skull", rot=(-6 * k, 0, 0))
    hooks(p, 0.6 * k)
    splay(p, k)
    tail(p, pitch=-6 * k)


BRACE_T = 4.0


def brace(t):
    """braced in the ring: legs wide, weight forward, the head low so the boss and the hooks face out; it breathes hard,
    a forefoot stamps once, the head bobs at the threat (a loop)"""
    p = {}
    br = math.sin(W(t, BRACE_T / 2))
    _brace_pose(p, 1.0, t)
    add(p, "body", pos=(0, -0.3 * br, 0))
    stamp = window(t, 2.4, 2.8, 0.06)
    bob = window(t, 1.0, 1.6, 0.1) * math.sin(W(t, 0.3))
    head(p, 4 * bob, 0, 0)
    tail(p, yaw=4 * math.sin(W(t, BRACE_T)))
    lift_head(p, 0.6)
    for s in SIDES:
        plant_h(p, s, 0, 1.5, meta=8)
    plant_f(p, "l", 2.5 * stamp, -1.0, -10 * stamp, clear=None if stamp > 0.05 else -0.05)
    plant_f(p, "r", 0, -1.0)
    return settle(p)


def guard(t):
    """the duel's guard: the brace, face on to the rival"""
    return brace(t)


def ring_defence(t):
    """taking its place in the ring: it swings round to face out, a sidestep in against its neighbour (the shoulder
    leant into it), then settles into the brace"""
    p = {}
    sw = f(tr((0, 0), (0.6, 1, smooth), (1.6, 1)), t)
    lean = f(tr((0, 0), (0.6, 0), (0.9, 1, ease_out), (1.6, 0.4, smooth)), t)
    k = f(tr((0, 0), (0.8, 0), (1.4, 1, smooth), (1.6, 1)), t)
    add(p, "body", rot=(0, 10 * (1 - sw) * math.sin(math.pi * sw), 4 * lean), pos=(-1.2 * lean, 0, 0))
    _brace_pose(p, k, t)
    head(p, 0, 18 * math.sin(math.pi * sw), 0)
    counter_legs(p, 4 * lean, shift_x=-1.2 * lean)
    lift_head(p, 0.6)
    st = window(t, 0.2, 0.9, 0.08)
    for i, s in enumerate(SIDES):
        up = st * max(0.0, math.sin(math.pi * (((t - 0.2) / 0.35 + 0.5 * i) % 1.0)))
        plant_h(p, s, 2.0 * up, 1.5 * k, 8 * k, 0, clear=None if up > 0.05 else -0.05)
        plant_f(p, s, 2.4 * up, -1.0 * k, -12 * up, clear=None if up > 0.05 else -0.05)
    return settle(p)


def boss_rub(t):
    """the boss rubbed on a trunk or a stone in front: the head low, worked side to side and up and down"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, smooth), (2.6, 1), (3.0, 0, smooth)), t)
    rub = math.sin(W(t, 0.7)) * window(t, 0.4, 2.6, 0.2)
    add(p, "body", rot=(-1.5 * k, 2 * rub, 0), pos=(0, -STAND_DROP - 0.8 * k, -1.5 * k))
    head(p, -10 * k + 5 * math.sin(W(t, 1.4)) * k, 14 * rub, 10 * rub)
    tail(p, yaw=5 * rub)
    return stand(p, fore=(-1.2 * k, -1.2 * k))


def snow_dig(t):
    """in the snow: the head swept low side to side, the beak and the boss scraping the snow aside, then a mouthful"""
    p = {}
    dn = f(tr((0, 0), (0.5, 1, smooth), (2.4, 1), (2.8, 0.3, smooth), (3.2, 0, smooth)), t)
    sweep = math.sin(W(t - 0.5, 0.8)) * window(t, 0.5, 2.4, 0.15)
    add(p, "body", rot=(-2 * dn, 2 * sweep, 0), pos=(0, -STAND_DROP - 1.2 * dn, 0))
    head(p, -30 * dn, 20 * sweep, 12 * sweep)
    add(p, "skull", rot=(-8 * dn, 0, 0))
    jaw(p, -6 * window(t, 2.3, 2.7, 0.08))
    flick(p, t, 1.6, 8)
    return stand(p, fore=(-1.0 * dn, -1.0 * dn), clear=0.0)


def hesitate(t):
    """at the river bank: it stops, the head lowered to smell the water, a forefoot put out and drawn back, a look at
    the others behind"""
    p = {}
    dn = f(tr((0, 0), (0.5, 1, smooth), (1.6, 1), (2.0, 0.2, smooth), (2.6, 0, smooth)), t)
    test = window(t, 0.8, 1.4, 0.12)
    look = window(t, 1.8, 2.5, 0.15)
    add(p, "body", rot=(-1.5 * dn, 0, 0), pos=(0, -STAND_DROP - 0.6 * dn, 1.0 * test))
    head(p, -18 * dn + 2 * math.sin(W(t, 0.5)) * dn, 26 * look, 0)
    lift_head(p, 0.3)
    for s in SIDES:
        plant_h(p, s)
    plant_f(p, "l", 2.4 * math.sin(math.pi * min(1.0, test)), -5 * test, -16 * test, clear=None if test > 0.05 else -0.05)
    plant_f(p, "r")
    return settle(p)


def call(t):
    """the low call of the herd: the head stretched forward and a little up, the mouth opening on a long grunt"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (1.6, 1), (2.2, 0, smooth)), t)
    o = window(t, 0.5, 1.6, 0.15)
    breathe(p, t, 2.2, 0.5)
    add(p, "body", rot=(1.5 * k, 0, 0), pos=(0, 0.3 * o, 0))
    head(p, 12 * k, 0, 0)
    jaw(p, -9 * o)
    return stand(p)


def roar(t):
    """the winner's bellow: the head up, the jaw wide, a toss of the hooks"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (2.0, 1), (2.6, 0, smooth)), t)
    o = window(t, 0.5, 2.0, 0.15)
    add(p, "body", rot=(3 * k, 0, 0), pos=(0, -STAND_DROP, 0))
    head(p, 24 * k, 6 * math.sin(W(t, 1.2)) * o, 0)
    jaw(p, -16 * o)
    hooks(p, 0.6 * k, t=t, shake=1.5 * o)
    tail(p, pitch=-6 * k)
    return stand(p)


# ------------------------------------------------------------------ the duel's set (fixed times of every rig)
def lunge(t):
    """the duel's lunge (1.8 s, the blow at 0.50 s): a boss ram thrown far, the recovery longer"""
    p = {}
    load = f(tr((0, 0), (0.2, 1, ease_out), (0.32, 1), (0.44, 0, ease_in), (1.8, 0)), t)
    drive = f(tr((0, 0), (0.3, 0), (0.5, 1, ease_in), (0.62, 0.85), (1.3, 0.2, smooth), (1.8, 0, smooth)), t)
    jolt = math.exp(-((t - 0.52) / 0.05) ** 2)
    _ram_pose(p, load, drive)
    add(p, "body", rot=(-2 * jolt, 0, 0), pos=(0, 0, 2.5 * jolt))
    lift_head(p)
    for s in SIDES:
        plant_h(p, s, 0, -6 * drive)
        plant_f(p, s, 0, -8 * drive)
    return settle(p)


def parry(t):
    """the parry (1.5 s, the counter at 0.60 s): the head swung across to take the blow on the boss, then the toss back"""
    p = {}
    catch = f(tr((0, 0), (0.15, 1, ease_out), (0.45, 1), (0.6, -0.8, ease_in), (0.8, -0.5), (1.5, 0, smooth)), t)
    add(p, "body", rot=(0, 4 * catch, -2 * catch), pos=(0, -STAND_DROP - 1.0, 1.0 * max(0.0, catch)))
    head(p, -14, 22 * catch, -12 * catch)
    splay(p, 0.6)
    hooks(p, t=t, shake=1.5 * window(t, 0.55, 0.8, 0.05))
    return stand(p)


def stagger(t):
    """the stagger (1.6 s): shoved aside, the head swinging out, a hind leg crossing over, slow to square up (it hardly
    staggers: the movement is short)"""
    p = {}
    e = f(tr((0, 0), (0.12, 1, ease_out), (0.6, 0.7), (1.6, 0, smooth)), t)
    add(p, "body", rot=(1.5 * e, -8 * e, 6 * e), pos=(1.5 * e, -STAND_DROP - 0.8 * e, 0))
    head(p, 8 * e, -20 * e, 14 * e)
    counter_legs(p, 6 * e, shift_x=1.5 * e)
    tail(p, yaw=10 * e)
    lift_head(p)
    plant_h(p, "l", 2.0 * window(t, 0.2, 0.5, 0.08), 0, clear=None if 0.2 < t < 0.5 else -0.05)
    plant_h(p, "r")
    for s in SIDES: plant_f(p, s)
    return settle(p)


def feint(t):
    p = {}
    k = f(tr((0, 0), (0.25, 1, ease_out), (0.45, 1), (1.0, 0, smooth)), t)
    _ram_pose(p, 0.0, 0.45 * k)
    return stand(p)


def block(t):
    p = {}
    k = f(tr((0, 0), (0.15, 1, ease_out), (0.6, 1), (1.0, 0, smooth)), t)
    _brace_pose(p, k, t)
    head(p, -8 * k, 0, 0)
    return stand(p, fore=(-1 * k, -1 * k))


def recoil(t):
    p = {}
    e = math.exp(-t / 0.25) * smooth(t / 0.05)
    add(p, "body", rot=(4 * e, 0, 0), pos=(0, -STAND_DROP, 3 * e))
    head(p, 14 * e, 0, 4 * e)
    hooks(p, t=t, shake=2 * e)
    return stand(p)


def submit(t):
    """gives in: the head lowered and turned away, it backs off a step"""
    p = {}
    k = f(tr((0, 0), (0.5, 1, smooth), (2.0, 1), (2.4, 0, smooth)), t)
    add(p, "body", rot=(-2 * k, -6 * k, 0), pos=(0, -STAND_DROP - 1.0 * k, 2 * k))
    head(p, -26 * k, -28 * k, 8 * k)
    tail(p, pitch=6 * k)
    return stand(p)


# ------------------------------------------------------------------ eating
def eat(t):
    p = {}
    dn = f(tr((0, 0), (0.45, 1, smooth), (0.8, 1), (1.1, 0.2, ease_out), (2.4, 0.2), (2.8, 0, smooth)), t)
    breathe(p, t, 2.8, 0.5)
    head(p, -14 * dn, 0, 0)
    jaw(p, f(tr((0, 0), (0.5, -8, ease_out), (0.7, -1, ease_in), (2.8, 0)), t))
    c = window(t, 1.0, 2.5, 0.1) * max(0.0, -math.sin(W(t - 1.0, 0.45)))
    jaw(p, -4 * c)
    return stand(p)


def graze(t):
    p = {}
    dn = f(tr((0, 0), (0.6, 1, smooth), (2.2, 1), (2.7, 0.15, smooth), (3.4, 0, smooth)), t)
    breathe(p, t, 3.4, 0.5)
    add(p, "body", rot=(-2 * dn, 0, 0), pos=(0, -0.8 * dn, 0))
    head(p, -26 * dn, 0, 0)
    sweep = math.sin(W(t - 0.6, 0.9)) * window(t, 0.6, 2.2, 0.15)
    head(p, 0, 10 * sweep, -4 * sweep)
    clip = sum(window(t, c - 0.12, c, 0.05) for c in (0.9, 1.35, 1.8, 2.1))
    jaw(p, -7 * clip)
    flick(p, t, 1.7, 8)
    return stand(p, fore=(-1.0 * dn, -1.0 * dn), clear=0.0)


def drink(t):
    p = {}
    dn = f(tr((0, 0), (0.8, 1, smooth), (2.7, 1), (3.1, 0.2, smooth), (3.6, 0, smooth)), t)
    breathe(p, t, 3.6, 0.4)
    add(p, "body", rot=(-3 * dn, 0, 0), pos=(0, -1.2 * dn, 0))
    head(p, -32 * dn, 0, 0)
    lap = window(t, 1.0, 2.6, 0.15) * math.sin(W(t, 0.36))
    head(p, 2 * lap)
    jaw(p, -3 * max(0, lap))
    splay(p, 0.4 * dn)
    return stand(p, fore=(-1.5 * dn, -1.5 * dn), clear=0.0)


# ------------------------------------------------------------------ lying down
BELLY_STAND = []


def lie(p, k=1.0, kh=None):
    """down on the belly: the hind legs fold under, the forelegs fold back under the chest"""
    if not BELLY_STAND:
        q = {}; add(q, "body", pos=(0, -STAND_DROP, 0)); BELLY_STAND.append(low_of(q, {"body"}))
    kh = k if kh is None else kh
    add(p, "body", pos=(0, -STAND_DROP, 0))
    b = low_of(p, {"body"}); goal = BELLY_STAND[0] * (1 - k)
    add(p, "body", pos=(0, goal - b, 0))
    up = k - kh
    if up > 0: add(p, "body", rot=(-10 * up, 0, 0))
    head(p, 12 * k, 0, 0)
    tail(p, pitch=-4 * k)
    for s in SIDES:
        add(p, f"thigh_{s}", rot=(55 * kh, 0, 0)); add(p, f"shin_{s}", rot=(-110 * kh, 0, 0)); add(p, f"foot_{s}", rot=(55 * kh, 0, 0))
        add(p, f"arm_{s}", rot=(-50 * k, 0, 0)); add(p, f"forearm_{s}", rot=(110 * k, 0, 0)); add(p, f"hand_{s}", rot=(-60 * k, 0, 0))
    return p


def lift_tail(p, clear=0.0):
    for i, b in enumerate(TAILS):
        for _ in range(20):
            if low_of(p, set(TAILS[i:])) >= clear: break
            add(p, b, rot=(-1.5, 0, 0))
    return p


def head_back(p, k=1.0, side=1.0):
    add(p, "neck", rot=(6 * k, 40 * k * side, 0))
    add(p, "skull", rot=(-14 * k, 26 * k * side, -20 * k * side))


def ko_pose(p, k=1.0, t=0.0):
    br = math.sin(W(t, 4.2))
    add(p, "body", rot=(0, 0, 80 * k), pos=(0, -4.0 * k, 0))
    head(p, -6 * k + 0.5 * br, 0, 14 * k)
    jaw(p, -3 * k)
    for s, sg in (("l", 1), ("r", -1)):
        add(p, f"thigh_{s}", rot=(14 * k, 0, -6 * k * sg)); add(p, f"shin_{s}", rot=(-12 * k, 0, 0))
        add(p, f"arm_{s}", rot=(16 * k, 0, -4 * k * sg)); add(p, f"forearm_{s}", rot=(-8 * k, 0, 0))
    add(p, "body", pos=(0, 0.25 * br * k, 0))
    return p


def finish(p):
    return settle(lift_tail(lift_head(p, 0.0)))


def sit(t):
    p = {}; br = math.sin(W(t, 4.0))
    lie(p)
    add(p, "body", rot=(0.3 * br, 0, 0), pos=(0, 0.12 * (1 + br), 0))
    a = window(t, 2.5, 4.4, 0.6)
    head(p, -0.4 * br, -20 * a, 3 * a)
    c = window(t, 5.4, 7.2, 0.1) * max(0.0, -math.sin(W(t - 5.4, 0.55)))
    jaw(p, -4 * c)
    return finish(p)


def sleep(t):
    p = {}; br = math.sin(W(t, 5.0))
    lie(p)
    add(p, "body", rot=(0.4 * br, 0, 0), pos=(0, 0.12 * (1 + br), 0))
    head(p, -20, 0, 0)
    head_back(p)
    return finish(p)


def wake_sleep(t):
    p = {}
    kb = f(tr((0, 1), (0.8, 0, smooth), (2.4, 0)), t)
    kh = f(tr((0, 1), (0.9, 1), (1.5, 0, smooth), (2.4, 0)), t)
    k = f(tr((0, 1), (1.4, 1), (2.1, 0, smooth), (2.4, 0)), t)
    lie(p, k, kh=kh)
    head(p, -20 * kb, 0, 0)
    head_back(p, kb)
    return finish(p)


def knocked_out(t):
    return shift_to_ground(ko_pose({}, 1.0, t))


def _going_down(t):
    p = {}
    st = window(t, 0.0, 0.6, 0.2)
    kh = f(tr((0, 0), (0.3, 0), (0.8, 1, ease_in), (2.0, 1)), t)
    k = f(tr((0, 0), (0.6, 0), (1.1, 1, ease_in), (2.0, 1)), t)
    add(p, "body", rot=(0, 3 * st * math.sin(W(t, 0.6)), 5 * st), pos=(1.0 * st, 0, 0))
    lie(p, max(k, 0.0), kh=max(kh, k))
    head(p, -18 * k, -8 * st, 6 * k)
    return finish(p)


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
        return shift_to_ground(blend(finish(lie({})), ko_pose({}, 1.0), roll))
    p = {}
    kh = f(tr((0, 1), (2.0, 1), (2.6, 0, smooth), (3.4, 0)), t)
    k = f(tr((0, 1), (2.5, 1), (3.1, 0, smooth), (3.4, 0)), t)
    lie(p, k, kh=kh)
    sh = window(t, 1.2, 1.9, 0.12)
    head(p, 3 * sh, 14 * sh * math.sin(W(t, 0.32)), 10 * sh * math.sin(W(t, 0.32)))
    return finish(p)


def hatch(t):
    p = {}
    k = f(tr((0, 1), (1.3, 1), (2.0, 0, smooth), (2.4, 0)), t)
    up = f(tr((0, 0), (0.25, 0), (0.6, 1, back_out), (2.4, 1)), t)
    sh = window(t, 0.65, 1.1, 0.08)
    lie(p, k)
    head(p, -26 * (1 - up) + 14 * up * k, 12 * sh * math.sin(W(t, 0.16)), 8 * sh * math.sin(W(t, 0.16)))
    head_back(p, 1.0 - up)
    jaw(p, -6 * window(t, 1.2, 1.5, 0.08))
    p = finish(p)
    add(p, "root", pos=(0, 0.25, 0))
    return p


LIE_DOWN_T, GET_UP_T = 2.6, 2.4


def lie_down(t):
    p = {}
    kh = float(tr((0, 0), (0.3, 0), (1.1, 1, ease_in), (2.6, 1))(t))
    k = float(tr((0, 0), (0.7, 0), (1.75, 1, ease_in), (2.6, 1))(t))
    look = float(tr((0, 0), (0.4, 1, ease_out), (1.6, 1), (2.6, 0, smooth))(t))
    lie(p, k, kh=max(kh, k))
    head(p, -10 * look, 0, 0)
    return finish(p)


def get_up(t):
    p = {}
    k = float(tr((0, 1), (0.3, 1), (1.0, 0, smooth), (2.4, 0))(t))
    kh = float(tr((0, 1), (0.8, 1), (1.6, 0, smooth), (2.4, 0))(t))
    push = math.exp(-((t - 1.1) / 0.2) ** 2)
    lie(p, kh, kh=kh)
    if k < kh:
        # the forelegs first: the front rises while the hind end is still down
        add(p, "body", rot=(8 * (kh - k), 0, 0))
    head(p, -8 * push, 0, 0)
    return finish(p)


# ------------------------------------------------------------------ with its owner
def beg(t):
    p = {}; breathe(p, t, 2.4)
    nudge = sum(window(t, c, c + 0.18, 0.07) for c in (0.5, 1.5))
    note = window(t, 1.0, 1.3, 0.08)
    head(p, -6 + 4 * nudge + 8 * note, 4 * math.sin(W(t, 2.4)), 0)
    jaw(p, -4 * note)
    add(p, "body", rot=(0.8 * note, 0, 0), pos=(0, 0, -1.0 * nudge))
    flick(p, t, 1.2, 10)
    return stand(p)


def tame(t):
    p = {}
    k = f(tr((0, 0), (0.5, 1, ease_out), (1.4, 1), (1.9, 0, smooth)), t)
    dn = f(tr((0, 0), (1.5, 0), (2.2, 1, smooth), (2.8, 1), (3.2, 0, smooth)), t)
    breathe(p, t, 3.2, 0.6)
    head(p, 10 * k - 20 * dn, 0, 0)
    jaw(p, -7 * window(t, 0.5, 1.3, 0.12))
    tail(p, pitch=3 * dn)
    flick(p, t, 1.0, 10)
    return stand(p)


ANIMS = {
    "idle": (idle, IDLE_T, True, "Parado", "em quatro patas, cabeça baixa, respira, vira a cabeçorra para olhar, rumina, espanta mosca com a cauda"),
    "walk": (walk, WALK[0], True, "Movimento", "anda como o bisão: a cabeça cai a cada passo da frente, a corcova balança"),
    "run": (run, RUNP[0], True, "Movimento", "galope pesado, a corcova balançando"),
    "charge": (charge, CHARGEP[0], True, "Movimento", "galope com alvo, a cabeça baixa e a bossa apontada"),
    "swim": (swim, 1.8, True, "Movimento", "nada com a cabeça fora d'água"),
    "wade": (wade, 1.8, True, "Só dele", "atravessa o rio de cabeça alta, levantando bem os pés"),
    "turn_left": (turn_left, TURN_T, True, "Movimento", "gira no lugar para a esquerda"),
    "turn_right": (turn_right, TURN_T, True, "Movimento", "gira no lugar para a direita"),
    "strafe_left": (strafe_left, 1.4, True, "Combate", "passo de lado na guarda, a bossa no rival"),
    "strafe_right": (strafe_right, 1.4, True, "Combate", "passo de lado na guarda, a bossa no rival"),
    "walk_tired": (walk_tired, WALK_TIRED_T, True, "Movimento", "anda cansado, cabeça pendida, boca aberta"),
    "idle_tired": (idle_tired, IDLE_TIRED_T, True, "Parado", "parado cansado: os flancos arfam"),
    "ring_defence": (ring_defence, 1.6, False, "Só dele", "toma o lugar na roda: vira para fora e encosta o ombro no vizinho"),
    "brace": (brace, BRACE_T, True, "Só dele", "firme na roda: pernas abertas, cabeça baixa, a bossa e os ganchos para fora"),
    "boss_ram": (boss_ram, 1.5, False, "Só dele", "investida curta de três ou quatro passos, a bossa bate primeiro (golpe em 0,60 s)"),
    "boss_push": (boss_push, BOSS_PUSH_T, True, "Só dele", "testa colada, empurrando com as pernas fincadas"),
    "boss_rub": (boss_rub, 3.0, False, "Só dele", "esfrega a bossa num tronco ou numa pedra"),
    "snow_dig": (snow_dig, 3.2, False, "Só dele", "raspa a neve com o bico e a bossa"),
    "hesitate": (hesitate, 2.6, False, "Só dele", "para na margem, cheira a água, testa com a pata"),
    "head_toss": (head_toss, 0.9, False, "Combate", "sacode a cabeça para o lado: ameaça ou golpe rápido (0,35 s)"),
    "horn_lock_start": (horn_lock_start, 1.0, False, "Combate", "o último passo e as testas se encontram"),
    "horn_lock": (horn_lock, BOSS_PUSH_T, True, "Combate", "o empurrão de testa colada (o duelo de bossa)"),
    "horn_lock_break": (horn_lock_break, 1.2, False, "Combate", "solta, recua e sacode a cabeça"),
    "guard": (guard, BRACE_T, True, "Combate", "a guarda: de frente, firme, a bossa baixa"),
    "feint": (feint, 1.0, False, "Combate", "finta de investida"),
    "block": (block, 1.0, False, "Combate", "aguenta o golpe na bossa"),
    "recoil": (recoil, 0.8, False, "Combate", "recua com o golpe"),
    "submit": (submit, 2.4, False, "Combate", "cede: baixa a cabeça, vira e recua"),
    "lunge": (lunge, 1.8, False, "Combate", "o bote do duelo: investida de bossa (golpe em 0,50 s)"),
    "parry": (parry, 1.5, False, "Combate", "apara com a bossa e devolve (0,60 s)"),
    "stagger": (stagger, 1.6, False, "Combate", "cambaleia pouco, cruza a pata e se recompõe"),
    "attack": (attack, 1.2, False, "Combate", "sobe a bossa no que está à frente (golpe em 0,5 s)"),
    "hurt": (hurt, 0.6, False, "Combate", "ao levar dano"),
    "roar": (roar, 2.6, False, "Combate", "o mugido grave do vencedor"),
    "call": (call, 2.2, False, "Só dele", "o grunhido longo da manada"),
    "death": (death, 3.0, False, "Combate", "as pernas cedem, deita e rola de lado"),
    "knockout": (knockout, 2.0, False, "Descanso", "nocauteado: cambaleia, deita e rola de lado"),
    "knocked_out": (knocked_out, 4.2, True, "Descanso", "nocauteado de lado"),
    "wake": (wake, 3.4, False, "Descanso", "acorda do nocaute e levanta"),
    "sit": (sit, 8.0, True, "Descanso", "deitado de barriga, rumina"),
    "sleep": (sleep, 10.0, True, "Descanso", "dorme deitado, a cabeça no flanco"),
    "wake_sleep": (wake_sleep, 2.4, False, "Descanso", "acorda e levanta"),
    "lie_down": (lie_down, LIE_DOWN_T, False, "Descanso", "deita: o quadril primeiro, depois o peito"),
    "get_up": (get_up, GET_UP_T, False, "Descanso", "levanta pela frente primeiro, como o boi"),
    "eat": (eat, 2.8, False, "Comer", "pega da mão e mastiga"),
    "graze": (graze, 3.4, False, "Comer", "pasta baixo, cortes curtos com o bico"),
    "drink": (drink, 3.6, False, "Comer", "bebe com a cabeça baixa, as patas da frente abertas"),
    "hatch": (hatch, 2.4, False, "Domado", "sai do ovo"),
    "beg": (beg, 2.4, True, "Domado", "pede comida ao dono"),
    "tame": (tame, 3.2, False, "Domado", "responde ao dono com um grunhido e baixa a cabeça"),
}
