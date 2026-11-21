"""Corythosaurus animations, from its own study (docs/estudos/15_HERBIVOROS_1_11.md).

v4 (16/11/2026, the "leque alto" silhouette): the same 37 names on the new posture (the trunk pitched up 18 degrees on
long forelegs, the neck almost upright in three pieces). The neck comes all the way down to graze and drink
(reach_down; it drinks with the forelegs splayed like a giraffe), it gallops on four instead of running on two, and the
FAN of blades moves in almost everything (fan(): open, raise, lay back, shiver); helmet_display springs it open.

The hadrosaur plumbing (the forelimb IK, the plant helpers, walking on four, rising onto the hind legs, lying down hind
end first) follows the Maiasaura's (maiaanims.py; the same body plan, here on longer legs and with the neck carried
up). What the Corythosaurus does that the others do not is its own (the voice and the ear of the forest):
- the DEEP CALL through the helmet (deep_call): the neck stretched up and forward, the helmet raised, the bill SHUT
  (the call goes through the S-bent nasal canal inside the crest, Weishampel 1981), the throat and the chest pulsing in
  slow deep beats; the herd hears it at 64 blocks. A shorter harder one with a half-rear is the alarm (alarm);
- the EAR (listen): it stops, the head goes up and the helmet turns slowly one way, holds, and the other way, as a
  bird turns its head to hear (stapes and eardrum of a sensitive ear, Schmitz & Motani 2011);
- the NAP (nap): catemeral, it dozes standing in short shifts, the head sinking with the helmet, a hind foot resting,
  the breath slow; different from the lying sleep;
- FRUIT in the forest: it rears onto the hind legs to the high fruit and twists the head sideways to pull it with the
  narrow beak (fruit_pick), and plucks berries from a bush, the head on its side, tugging (pluck);
- the HELMET in profile (helmet_display): broadside to the rival, the head raised and swung slowly up and down so the
  whole helmet shows, never a blow; whoever lowers the head first leaves;
- wading in the shallows with the head high (wade).

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
import cory as TC
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
STIFF = (1.0, 0.4, 0.26, 0.18)       # the ossified tendons: most of any bend is at the root
BALL = {s: world(S, {}, f"toes_{s}") for s in SIDES}
REST_META = {s: chain_angle(S, {}, [f"foot_{s}"]) for s in SIDES}
WRIST = {s: world(S, {}, f"hand_{s}") for s in SIDES}
REST_HAND = {s: chain_angle(S, {}, [f"hand_{s}"]) for s in SIDES}
HIND = {s: {f"{b}_{s}" for b in ("thigh", "shin", "foot", "toes")} for s in SIDES}
FORE = {s: {f"{b}_{s}" for b in ("arm", "forearm", "hand")} for s in SIDES}
FANS = tuple(n for n, *_ in TC.FAN)
FANS_M = tuple(n for n, *_ in TC.FAN_MALE)
HEADB = {"head", "skull", "jaw", "cheek_l", "cheek_r", "adult_crest", "male_display", "young_crest"} | set(FANS) | set(FANS_M)
SKIP = {"saddle"}
STAND_DROP = 1.5
HIND_LEN, FORE_LEN = 55.0, 62.0


def low_of(p, bones=None, skip=SKIP):
    return min(q[:, 1].min() for c, q in geo.cube_points(S, p)
               if (bones is None or c["bone"] in bones) and c["bone"] not in skip and c.get("mat") != "teeth")


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
        add(p, "neck1", rot=(1.5, 0, 0))
    return p


def stand(p, fore=(0, 0), hind=(0, 0), clear=0.3):
    lift_head(p, clear)
    for i, s in enumerate(SIDES):
        plant_h(p, s, 0, hind[i])
        plant_f(p, s, 0, fore[i])
    return p


def stand_hind(p, hind=(0, 0), clear=0.3):
    lift_head(p, clear)
    for i, s in enumerate(SIDES): plant_h(p, s, 0, hind[i])
    return p


def head(p, pitch=0.0, yaw=0.0, roll=0.0, k=(0.35, 0.35, 0.3)):
    for b, w in zip(("neck1", "neck2", "skull"), k):
        add(p, b, rot=(pitch * w, yaw * w, roll * w))


def jaw(p, a): add(p, "jaw", rot=(a, 0, 0))


# where each blade sits in the fan, front (0) to back (4); the male's two long blades lie between 1-2 and 3-4
FAN_AT = {**{n: k for k, n in enumerate(FANS)}, FANS_M[0]: 1.5, FANS_M[1]: 3.5}


def fan(p, spread=0.0, lift=0.0, fold=0.0, quiver=0.0, t=0.0):
    """the fan of blades (the helmet of v4): `spread` opens it (degrees between neighbouring blades, the front ones
    forward and the back ones back, around the middle blade), `lift` raises the whole crest forward and up, `fold`
    lays it back flat (the front blades fall onto the back one), `quiver` rattles the blades (a cockatoo's shiver)"""
    if lift:
        add(p, "adult_crest", rot=(-lift, 0, 0))
    for n, k in FAN_AT.items():
        q = quiver * math.sin(2 * math.pi * 7.0 * t + 1.3 * k) if quiver else 0.0
        add(p, n, rot=(spread * (k - 2.0) + fold * (4.0 - k) / 4.0 + q, 0, 0))


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
    """follow-through on the stiff tail: the root takes fn late, each bone behind it a little later"""
    for k, (b, w) in enumerate(zip(TAILS, STIFF)):
        u = t - delay * (1 + 0.5 * k)
        v = fn(u % loop if loop else max(0.0, u)) * w
        r = [0.0, 0.0, 0.0]; r[axis] = v
        add(p, b, rot=tuple(r))


def alive_upper(p, t, k=1.0, period=3.4, slow=None):
    head(p, -0.6 * k * wave(t, period, -0.5))
    add(p, "jaw", rot=(-0.3 * k * max(0.0, wave(t, period, -0.8)), 0, 0))
    for i, (b, w) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0.5 * k * w * wave(t, period, -0.5 - 0.3 * i), 1.5 * k * w * wave(t, (slow or period * 2.2), -0.7 - 0.3 * i), 0))


def breathe(p, t, T=3.2, amp=1.0, drop=STAND_DROP):
    br = math.sin(W(t, T))
    add(p, "body", rot=(0.4 * amp * br, 0, 0), pos=(0, -drop - 0.2 * amp * (1 + br), 0))
    head(p, -0.5 * amp * br)
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


FOLD = (-34.0, 78.0, 30.0)       # the forelegs folded under the chest when it is up on two legs


def fold_arms(p, k, spread=0.0):
    for s, sx in (("l", 1), ("r", -1)):
        for bone, a in zip(("arm", "forearm", "hand"), FOLD):
            add(p, f"{bone}_{s}", rot=(a * k, 0, spread * sx if bone == "arm" else 0))


def rear(p, deg):
    add(p, "body", rot=(deg, 0, 0))


def landing(x):
    x %= 1.0
    return -1.0 + 2.0 * smooth(x / 0.3) if x < 0.3 else 1.0 - 2.0 * smooth((x - 0.3) / 0.7)


def counter_legs(p, roll, shift_x=0.0, yaw=0.0):
    hx = math.degrees(math.atan2(-shift_x, HIND_LEN)); fx = math.degrees(math.atan2(-shift_x, FORE_LEN))
    for s in SIDES:
        add(p, f"thigh_{s}", rot=(0, -yaw, -roll + hx)); add(p, f"arm_{s}", rot=(0, -yaw, -roll + fx))


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
            meta = 22 * heel + 20 * (1 - smooth(sw / 0.4)) * (sw > 0) - 14 * math.sin(math.pi * sw)
            toe = -24 * math.sin(math.pi * min(1, sw * 1.1)) + 3 * smooth((sw - 0.7) / 0.3) * (sw > 0)
            plant_h(p, s, ly, dz, meta, toe, clear)
        else:
            pitch = -20 * heel - 36 * math.sin(math.pi * min(1, sw * 1.15))
            plant_f(p, s, ly, dz, pitch, clear)


WALK = (1.6, 44, 0.66, 5.5, 0.6)      # cycle s, stride px, duty, lift px, bob px (the long legs of v4)
RUNP = (0.62, 92, 0.34, 12.0, 2.2)    # the gallop of the long legs: cycle s, stride px, duty, lift px, bob px



def walk(t, Tc=None, stride=None, lift=None, bob=None, roll=3.4, yaw=2.2, head_p=-2.0, tail_amp=5.0):
    """on four: the lateral walk of a heavy hadrosaur; the high hips roll over each standing hind leg, the short head
    rides level, nodding a little, the stiff tail swings late as one beam"""
    Tc = Tc or WALK[0]; stride = stride or WALK[1]; duty = WALK[2]; lift = lift or WALK[3]; bob = WALK[4] if bob is None else bob
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    b2 = landing(2 * ph + 0.05)
    hroll = roll * math.sin(w + 0.3); hyaw = yaw * math.sin(w - 0.5)
    add(p, "body", rot=(0.5 * b2, hyaw, hroll), pos=(0, -STAND_DROP - bob * (0.5 - 0.5 * b2), 0))
    head(p, head_p - 1.2 * landing(2 * ph - 0.14) + 1.6 * math.sin(2 * w - 2.0), -0.8 * hyaw - 1.2 * math.sin(w - 1.6), -0.85 * hroll)
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(k * 0.8 * landing(2 * ph - 0.1 - 0.04 * i), -k * tail_amp * math.sin(w - 1.3 - 0.35 * i), 0))
    counter_legs(p, hroll, yaw=hyaw)
    lift_head(p, 1.0)
    foot_cycle(p, ph, LATERAL, stride, duty, lift, lift * 0.8, fstride=stride * 0.9)
    return p


WALK_TIRED_T = 2.5


def walk_tired(t):
    p = walk(t, Tc=WALK_TIRED_T, stride=22, lift=2.8, bob=0.8, roll=4.4, yaw=2.6, head_p=-12, tail_amp=6.0)
    pant = max(0.0, wave(t, WALK_TIRED_T / 3))
    add(p, "jaw", rot=(-4 - 3 * pant, 0, 0))
    add(p, "root", pos=(0, 0.25, 0))       # the slow cycle's curves dip between keys: a hair of clearance
    return p


def _biped(t, cyc, rise, headp, arms=1.0, settle_it=True):
    """on two legs: the front up, the arms folded under the chest, the tail a level beam"""
    Tc, stride, duty, lift, bob = cyc
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    bp = 1.0 * math.sin(2 * w - 0.4)
    rear(p, rise + bp)
    add(p, "body", rot=(0, 1.4 * math.sin(w), 2.4 * math.sin(w + 0.35)),
        pos=(0, -STAND_DROP - 1.0 - bob * (0.5 + 0.5 * math.cos(2 * w - 0.9)), 0))
    head(p, headp - bp + 2.5 * math.sin(2 * w - 1.3), -1.2 * math.sin(w), -2 * math.sin(w + 0.35))
    fold_arms(p, arms, spread=6)
    for s, o in (("l", 0.0), ("r", math.pi)):
        add(p, f"arm_{s}", rot=(5 * math.sin(w + o), 0, 0))
    tail(p, pitch=-rise * 0.8)
    tail_sway(p, t, Tc, 2.0, 0.6)
    lift_head(p, 1.0)
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
    return settle(p) if settle_it else p


GALLOP = {"lh": 0.0, "rh": 0.12, "lf": 0.48, "rf": 0.6}


def run(t):
    """it gallops on its four long legs like a giraffe (the forelegs are longer than the hind legs: it never rises
    onto two): the hind pair push off together, the front pair reach far ahead, the long neck pumps forward and back
    with the stride, the fan laid back in the wind, the tail a high stiff beam"""
    Tc, stride, duty, lift, bob = RUNP
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    pump = math.sin(w - 0.6)
    add(p, "body", rot=(-3 + 2.5 * math.sin(w + 0.4), 0.8 * math.sin(w), 1.2 * math.sin(w + 0.3)),
        pos=(0, -STAND_DROP - 1.0 - bob * (0.5 + 0.5 * math.cos(w + 0.4)), 0))
    add(p, "neck1", rot=(-14 - 7 * pump, 0, 0)); add(p, "neck2", rot=(-4 - 3 * pump, 0, 0))
    add(p, "neck3", rot=(8 + 5 * pump, 0, 0)); add(p, "skull", rot=(10 + 4 * pump, 0, 0))
    fan(p, fold=16 + 3 * math.sin(2 * w))
    tail(p, pitch=-4)
    beam(p, t, lambda u: -2.5 * math.sin(2 * math.pi * u / Tc - 1.0), axis=0, delay=0.04, loop=Tc)
    tail_sway(p, t, Tc, 2.0, 0.0)
    lift_head(p, 1.0)
    foot_cycle(p, ph, GALLOP, stride, duty, lift, lift * 1.1, fstride=stride * 1.05)
    return settle(p)


def swim(t):
    Tc = 1.6; w = W(t, Tc); p = {}
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


# ------------------------------------------------------------------ standing
IDLE_T = 8.0
LOOK = Track([(0, (0, 0)), (1.0, (0, 0)), (1.8, (8, -18), ease_out), (3.0, (8, -18)), (3.8, (3, 22), ease_out),
              (5.0, (3, 22)), (5.8, (0, 0), smooth), (8.0, (0, 0))])


def idle(t):
    """on four, breathing; the short head swings round to look, it chews with the cheeks flexing, the weight drifting
    from one side to the other, the tail beam swaying late"""
    p = {}
    Ti = IDLE_T
    br = wave(t, Ti / 3)
    shift = wave(t, Ti, 0.4) + 0.3 * wave(t, Ti / 2, 1.0)
    hroll = 1.2 * shift; hyaw = 0.7 * shift
    add(p, "body", rot=(0.4 * br, hyaw, hroll), pos=(0, -STAND_DROP - 0.2 * (1 + br), 0))
    lp, ly = LOOK(t)
    head(p, lp - 0.5 * wave(t, Ti / 3, -0.6) + 0.6 * wave(t, Ti / 5, 1.2), ly - 0.8 * hyaw, -0.85 * hroll + 0.15 * ly)
    chew(p, t, 5.8, 7.6, 0.55)
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0.6 * k * wave(t, Ti / 3, -0.6 - 0.3 * i), k * (2.5 * wave(t, Ti, -1.0 - 0.3 * i) + 0.8 * wave(t, Ti / 2, 0.5 - 0.3 * i)), 0))
    counter_legs(p, hroll, yaw=hyaw)
    return stand(p)


IDLE_TIRED_T = 3.6


def idle_tired(t):
    p = {}
    Ti = IDLE_TIRED_T
    heave = wave(t, Ti / 4)
    add(p, "body", rot=(-1.5 + 0.8 * heave, 0, 0.6 * wave(t, Ti, 0.3)), pos=(0, -STAND_DROP - 0.4 - 0.3 * heave, 0))
    head(p, -18 - 1.5 * wave(t, Ti / 4, -0.6), 3 * wave(t, Ti, 0.5), 0)
    add(p, "jaw", rot=(-5 - 3 * max(0.0, wave(t, Ti / 4, -0.4)), 0, 0))
    tail(p, pitch=3)
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0.6 * k * heave, 1.5 * k * wave(t, Ti, -0.8 - 0.3 * i), 0))
    counter_legs(p, 0.6 * wave(t, Ti, 0.3))
    return stand(p)


TURN_T = 2.2
TURN_ORDER = {"rh": 0.0, "rf": 0.25, "lh": 0.5, "lf": 0.75}


def turn(t, side, Tt=TURN_T, lead_deg=12.0, roll=2.8):
    d = 1.0 if side == "left" else -1.0
    ph = (t / Tt) % 1.0; w = 2 * math.pi * ph; p = {}
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


def vigil(t):
    """the head high and still on what it watches (used by the alarm and the taming stare)"""
    p = {}
    k = f(tr((0, 0), (0.35, 1, ease_out), (2.7, 1), (3.0, 0.8)), t)
    add(p, "body", rot=(2.5 * k + 0.2 * math.sin(W(t, 2.6)), 0, 0), pos=(0, -STAND_DROP, 0))
    head(p, 30 * k, 0, 0, k=(0.5, 0.25, 0.25))
    tail(p, pitch=-5 * k)
    return stand(p, fore=(1.0 * k, 1.0 * k))


def hurt(t):
    p = {}
    e = math.exp(-t / 0.17) * smooth(t / 0.05)
    add(p, "body", rot=(3 * e, -5 * e, -3 * e), pos=(0, -STAND_DROP - 0.4 * e, 1.0 * e))
    head(p, 10 * e, 14 * e, 6 * e)
    fan(p, fold=14 * e)
    beam(p, t, lambda u: 9 * math.exp(-u / 0.22) * smooth(u / 0.05), delay=0.06)
    beam(p, t, lambda u: -4 * math.exp(-u / 0.22) * smooth(u / 0.05), axis=0, delay=0.06)
    alive_upper(p, t, k=0.5)
    counter_legs(p, -3 * e)
    return stand(p)


def attack(t):
    """cornered (it only strikes back then): the weight back, the head drawn up and to the side, then swung down and
    across into the target, a side blow of the helmet with the shoulder behind it (the hit at 0.5 s)"""
    p = {}
    back = f(tr((0, 0), (0.3, 1, ease_out), (0.42, 1), (0.5, 0, ease_in), (1.2, 0)), t)
    lunge = f(tr((0, 0), (0.4, 0), (0.52, 1, ease_in), (0.7, 0.8), (1.2, 0, smooth)), t)
    rear(p, 6 * back - 3 * lunge)
    add(p, "body", rot=(0, 5 * lunge, -3 * lunge), pos=(-0.6 * lunge, -STAND_DROP - 0.4 * lunge, 2 * back - 4 * lunge))
    head(p, 10 * back - 22 * lunge, 14 * back - 18 * lunge, -10 * back + 14 * lunge)
    fan(p, spread=5 * back, lift=12 * back + 6 * lunge)
    tail(p, yaw=-6 * lunge, pitch=-3 * back)
    beam(p, t, lambda u: -5 * f(tr((0, 0), (0.4, 0), (0.52, 1, ease_in), (0.7, 0.8), (1.2, 0, smooth)), u), delay=0.06)
    lift_head(p)
    for s in SIDES: plant_h(p, s, 0, 1.8 * lunge)
    for s in SIDES:
        plant_f(p, s, 2.0 * back * (1 - lunge), -3 * lunge, clear=None if back > 0.05 else -0.05)
    return settle(p)


KICK_BACK_T = 1.6
KB_LOAD = tr((0, 0), (0.46, 1, ease_out), (0.54, 1.0), (0.67, 0.25, ease_in), (1.05, 0.0, smooth), (1.6, 0))
KB_DRIVE = tr((0, 0), (0.52, 0), (0.64, 1, ease_in), (0.74, 0.9), (1.2, 0, smooth), (1.6, 0))
KB_LOOK = tr((0, 0), (0.3, 1, ease_out), (1.15, 1), (1.6, 0, smooth))


def kick_back(t):
    """something at its tail: the head swings round the flank to see it, the weight goes forward, the right hind drawn
    up and driven back (the blow at 0.64 s), the tail swung aside"""
    p = {}
    load = float(KB_LOAD(t)); drive = float(KB_DRIVE(t)); look = float(KB_LOOK(t))
    tip = max(load, drive)
    roll = -3.2 * tip
    add(p, "body", rot=(-3.0 * tip - 2.0 * drive, 4 * look, roll), pos=(0.5 * tip, -STAND_DROP - 0.7 * tip, -1.5 * tip))
    head(p, -10 * look, 40 * look, -10 * look)
    tail(p, yaw=6 * tip, pitch=-2 * tip)
    beam(p, t, lambda u: 12 * float(KB_DRIVE(u)) + 4 * float(KB_LOAD(u)), delay=0.07)
    alive_upper(p, t, k=0.5)
    counter_legs(p, roll, shift_x=0.5 * tip)
    add(p, "thigh_r", rot=(0, 0, -8 * drive))
    lift_head(p)
    plant_h(p, "l")
    plant_h(p, "r", 5.5 * load + 5 * drive, 2 * load + 12 * drive, -22 * load + 36 * drive, -18 * load + 10 * drive, clear=None)
    for s in SIDES: plant_f(p, s, 0, -1.0 * tip)
    return settle(p)


BODY_SHOVE_T = 1.6
HC = tr((0, 0), (0.48, -1.0, ease_out), (0.56, -0.95), (0.66, 1.0, ease_in), (0.76, 1.1), (1.6, 0, back_out))


def body_shove(t):
    """the hip check: the rump and the base of the tail slewed sideways into the attacker at the flank (0.66 s)"""
    p = {}
    s_ = float(HC(t)); a = max(0.0, s_); b = max(0.0, -s_)
    jolt = math.exp(-((t - 0.68) / 0.05) ** 2)
    yaw = -7.0 * a + 3.0 * b
    roll = 4.0 * a - 2.5 * b
    shift = -1.2 * a + 0.6 * b
    add(p, "body", rot=(-1.5 * a + 0.5 * jolt, yaw, roll), pos=(shift, -STAND_DROP - 0.4 * a - 0.3 * jolt, 0))
    head(p, -6 * a - 4 * b, 26 * a - 14 * b - 0.8 * yaw, -4 * a)
    tail(p, yaw=-12 * a + 5 * b)
    beam(p, t, lambda u: -14 * max(0.0, float(HC(u))) + 4 * max(0.0, -float(HC(u))), delay=0.08)
    alive_upper(p, t, k=0.5)
    counter_legs(p, roll, shift_x=shift, yaw=yaw)
    return stand(p)


def reach_down(p, k, low=1.0):
    """the tall neck brought down: the base swings forward and down from the withers, the middle stays straight, the
    top bends back so the head arrives bill-first; the front of the body dips (the withers lower). low = 1 reaches the
    ground, 0.5 a bush"""
    add(p, "neck1", rot=(-88 * k * low, 0, 0))
    add(p, "neck2", rot=(-16 * k * low, 0, 0))
    add(p, "neck3", rot=(18 * k * low, 0, 0))
    add(p, "skull", rot=(14 * k * low, 0, 0))
    rear(p, -14 * k * low)


def eat(t):
    """takes a mouthful from the hand: the neck comes down to the hand, a clip with the narrow bill, the chew with the
    cheeks flexing back up high"""
    p = {}
    dn = f(tr((0, 0), (0.45, 1, smooth), (0.8, 1), (1.1, 0.25, ease_out), (2.4, 0.25), (2.8, 0, smooth)), t)
    breathe(p, t, 2.8, 0.5)
    reach_down(p, dn, 0.45)
    jaw(p, f(tr((0, 0), (0.5, -10, ease_out), (0.7, -1, ease_in), (2.8, 0)), t))
    chew(p, t, 1.0, 2.5, 0.45)
    fan(p, fold=6 * dn)
    tail_sway(p, t, 2.8, 2.0)
    alive_upper(p, t, k=0.3)
    return stand(p, fore=(-1.0 * dn, -1.0 * dn))


def graze(t):
    """crops low ferns: the long neck swings down to the ground, short side-to-side clips with the narrow bill, then
    the neck comes back up and it chews, looking round"""
    p = {}
    dn = f(tr((0, 0), (0.7, 1, smooth), (2.2, 1), (2.7, 0.15, smooth), (3.4, 0, smooth)), t)
    breathe(p, t, 3.4, 0.5)
    reach_down(p, dn, 0.95)
    sweep = math.sin(W(t - 0.7, 0.9)) * window(t, 0.7, 2.2, 0.15)
    head(p, 0, 12 * sweep, -4 * sweep)
    clip = sum(window(t, c - 0.12, c, 0.05) for c in (0.95, 1.4, 1.85, 2.15))
    jaw(p, -9 * clip)
    chew(p, t, 2.6, 3.4, 0.4)
    fan(p, fold=10 * dn)
    tail(p, pitch=-4 * dn)
    tail_sway(p, t, 3.4, 2.0)
    alive_upper(p, t, k=0.3)
    return stand(p, fore=(-2.0 * dn, -2.0 * dn), clear=0.2)


def drink(t):
    """drinks like a giraffe: the forelegs splay wide, the front of the body sinks between them, the neck comes all the
    way down and the bill skims the water; it comes up quickly between sips, the fan laid back"""
    p = {}
    dn = f(tr((0, 0), (0.8, 1, smooth), (2.7, 1), (3.1, 0.2, smooth), (3.6, 0, smooth)), t)
    sp = f(tr((0, 0), (0.6, 1, ease_out), (3.0, 1), (3.6, 0, smooth)), t)
    breathe(p, t, 3.6, 0.4)
    reach_down(p, dn, 1.0)
    rear(p, -4 * sp)
    add(p, "body", pos=(0, -5 * sp, 0))
    lap = window(t, 1.0, 2.6, 0.15) * math.sin(W(t, 0.36))
    head(p, 2 * lap)
    jaw(p, -4 * max(0, lap))
    fan(p, fold=12 * dn)
    for s, sx in (("l", 1), ("r", -1)):
        add(p, f"arm_{s}", rot=(0, 0, 20 * sx * sp))
        add(p, f"forearm_{s}", rot=(0, 0, -6 * sx * sp))
    tail(p, pitch=-6 * dn)
    stand(p, fore=(-3.0 * sp, -3.0 * sp), clear=0.0)
    add(p, "root", pos=(0, 0.25, 0))       # the splayed forefeet: a hair of clearance between keys
    return p


def fruit_pick(t):
    """the high fruit: it rears onto the hind legs, the forelegs off the ground and held in, the neck stretched up, the
    head TWISTED on its side so the narrow beak gets round the fruit; two pulls with a jerk back, a chew up there,
    then down on all fours"""
    p = {}
    up = f(tr((0, 0), (0.8, 1, ease_out), (3.4, 1), (4.2, 0, smooth)), t)
    twist = f(tr((0, 0), (0.9, 0), (1.2, 1, ease_out), (2.3, 1), (2.6, 0, smooth)), t)
    pull = sum(math.exp(-((t - c) / 0.07) ** 2) for c in (1.45, 2.05))
    rear(p, 36 * up)
    add(p, "body", pos=(0, -STAND_DROP, 0))
    head(p, 4 * up - 7 * pull, 6 * twist, 0)
    add(p, "skull", rot=(-6 * pull, 0, 24 * twist))
    jaw(p, -9 * window(t, 1.1, 1.4, 0.06) - 7 * window(t, 1.75, 2.0, 0.06))
    chew(p, t, 2.6, 3.4, 0.42)
    for s, sx in (("l", 1), ("r", -1)):
        add(p, f"arm_{s}", rot=(-50 * up, 0, 3 * sx * up)); add(p, f"forearm_{s}", rot=(42 * up, 0, 0))
        add(p, f"hand_{s}", rot=(28 * up, 0, 0))
    tail(p, pitch=-26 * up)
    if up < 0.05:
        return settle(stand(p))
    stand_hind(p)
    lift_tail(p, 0.4)
    return settle(p)


def pluck(t):
    """berries from a bush: the neck down to bush height and the head turned on its side, three short tugs back with
    the beak, the berries chewed with the head up"""
    p = {}
    dn = f(tr((0, 0), (0.5, 1, smooth), (2.0, 1), (2.4, 0.2, smooth), (3.2, 0, smooth)), t)
    tug = sum(math.exp(-((t - c) / 0.06) ** 2) for c in (0.85, 1.3, 1.75))
    breathe(p, t, 3.2, 0.4)
    reach_down(p, dn, 0.6)
    head(p, 5 * tug, 14 * dn, 0)
    add(p, "skull", rot=(0, 0, 22 * dn))
    add(p, "body", pos=(0, 0, 0.6 * tug))
    jaw(p, -6 * window(t, 0.6, 1.9, 0.1) * (1 - tug))
    chew(p, t, 2.3, 3.1, 0.4)
    fan(p, fold=6 * dn, quiver=0.8 * tug, t=t)
    tail_sway(p, t, 3.2, 2.0)
    alive_upper(p, t, k=0.3)
    return stand(p, fore=(-1.0 * dn, -1.0 * dn), clear=0.0)

# ------------------------------------------------------------------ the voice: through the helmet, the bill shut
def _resonate_pose(p, k, beat, rise=1.0, shut=True):
    """the neck stretched up and forward, the helmet raised, the bill shut (or just parted), the throat and the chest
    pulsing on each beat"""
    head(p, 22 * k * rise, 0, 0, k=(0.55, 0.3, 0.15))
    add(p, "skull", rot=(6 * k * rise - 2 * beat, 0, 0))
    add(p, "body", rot=(1.5 * k + 0.8 * beat, 0, 0), pos=(0, 0.3 * beat, 0))
    add(p, "neck1", rot=(-1.6 * beat, 0, 0)); add(p, "neck2", rot=(1.2 * beat, 0, 0))
    jaw(p, (-0.5 if shut else -3.0) * k * (0.5 + 0.5 * beat))
    fan(p, spread=2.5 * k + 1.5 * beat, lift=6 * k * rise + 2 * beat)


def deep_call(t):
    """the deep call through the helmet: the neck stretched up, the helmet high, the bill shut, three long slow beats of
    the throat and the chest (the S-bent canal inside the crest as a resonating chamber, Weishampel 1981; heard by the
    herd at 64 blocks)"""
    p = {}
    k = f(tr((0, 0), (0.6, 1, ease_out), (3.8, 1), (4.6, 0, smooth)), t)
    beat = sum(window(t, c, c + 0.75, 0.2) for c in (0.9, 1.9, 2.9)) * (0.8 + 0.2 * math.sin(W(t, 0.12)))
    breathe(p, t, 4.6, 0.3)
    _resonate_pose(p, k, beat)
    tail(p, pitch=-3 * k)
    beam(p, t, lambda u: -1.5 * sum(window(u, c, c + 0.75, 0.2) for c in (0.9, 1.9, 2.9)), axis=0, delay=0.08)
    return stand(p, fore=(0.8 * k, 0.8 * k))


def call(t):
    """the short contact call: one note through the helmet, the head half up"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (1.8, 1), (2.4, 0, smooth)), t)
    beat = window(t, 0.6, 1.5, 0.15)
    breathe(p, t, 2.4, 0.4)
    _resonate_pose(p, k, beat, rise=0.6)
    return stand(p)


def answer(t):
    """answers another's call: two short notes, the helmet turned toward it"""
    p = {}
    k = f(tr((0, 0), (0.35, 1, ease_out), (1.5, 1), (2.0, 0, smooth)), t)
    beat = window(t, 0.5, 0.8, 0.08) + window(t, 1.0, 1.3, 0.08)
    breathe(p, t, 2.0, 0.4)
    _resonate_pose(p, k, beat, rise=0.5)
    head(p, 0, 10 * k, 0)
    return stand(p)


def alarm(t):
    """the alarm: a hard deep blast with a half-rear, the forefeet off the ground, the tail up, then down on all fours
    ready to run with the herd"""
    p = {}
    k = f(tr((0, 0), (0.15, 1, ease_out), (1.6, 1), (2.2, 0, smooth)), t)
    up = f(tr((0, 0), (0.15, 0), (0.4, 1, ease_out), (1.3, 1), (1.8, 0, ease_in), (2.2, 0)), t)
    beat = window(t, 0.5, 1.2, 0.1)
    rear(p, 14 * up)
    add(p, "body", pos=(0, -STAND_DROP, 0))
    _resonate_pose(p, k, 1.3 * beat, rise=1.1, shut=False)
    fan(p, spread=6 * up, lift=10 * up, quiver=1.2 * beat, t=t)
    fold_arms(p, 0.5 * up)
    tail(p, pitch=-12 * k)
    lift_head(p)
    for s in SIDES: plant_h(p, s)
    for s in SIDES:
        plant_f(p, s, 0, 0, clear=-0.05 if up < 0.03 else None)
    return settle(p)


LISTEN_T = 4.4


def listen(t):
    """the ear of the forest: it stops dead, the head goes up and the helmet turns slowly to one side, holds, then to the
    other, the head tipped as it turns (the sound heard through the trees, no line of sight)"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (3.8, 1), (4.4, 0, smooth)), t)
    turn_ = f(tr((0, 0), (0.5, 0), (1.2, 1, smooth), (1.9, 1), (2.8, -1, smooth), (3.5, -1), (4.2, 0, smooth)), t)
    add(p, "body", rot=(1.5 * k, 0, 0), pos=(0, -STAND_DROP, 0))
    head(p, 20 * k, 26 * turn_ * k, 0, k=(0.45, 0.35, 0.2))
    add(p, "skull", rot=(0, 0, -10 * turn_ * k))
    fan(p, lift=8 * k, spread=1.5 * k)
    tail(p, pitch=-4 * k)
    for i, (b, w) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0, 1.0 * w * wave(t, LISTEN_T, -0.5 - 0.3 * i), 0))
    return stand(p)


NAP_T = 6.0


def nap(t):
    """the catemeral nap, STANDING: the neck sinks until the helmet hangs low, the weight settles back, one hind foot
    resting on its toe, the breath long and slow, a small jerk of the head now and then (a loop)"""
    p = {}
    br = wave(t, NAP_T / 2)
    jerk = math.exp(-((t - 4.1) / 0.12) ** 2)
    add(p, "body", rot=(-1.5 + 0.5 * br, 0, -1.2), pos=(0, -STAND_DROP - 0.8 - 0.3 * br, 0.4))
    head(p, -30 + 1.5 * br + 7 * jerk, 4, 3, k=(0.5, 0.3, 0.2))
    add(p, "skull", rot=(-6, 0, 0))
    fan(p, fold=22 + 2 * br)
    tail(p, pitch=4)
    for i, (b, w) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0.4 * w * br, 0.8 * w * wave(t, NAP_T, -0.5 - 0.3 * i), 0))
    counter_legs(p, -1.2)
    lift_head(p, 0.6)
    plant_h(p, "l")
    plant_h(p, "r", 0.6, 1.5, meta=14, toe=-10, clear=None)
    for s in SIDES: plant_f(p, s)
    return settle(p)


DISPLAY_T = 4.8


def helmet_display(t):
    """broadside to the rival (the Java turns the body side-on): it draws itself up, the neck stretched tall, and the
    FAN springs open like a cockatoo's crest (0.5 to 0.9 s): the front blades swing forward, the back ones back,
    the whole crest raised; held open, the blades shivering, the head bowed slowly forward and up so the open fan
    sweeps across the rival's view; then the fan snaps shut and it settles. Never a blow."""
    p = {}
    k = f(tr((0, 0), (0.5, 1, ease_out), (4.2, 1), (4.8, 0, smooth)), t)
    op = f(tr((0, 0), (0.45, 0), (0.85, 1, back_out), (3.7, 1), (4.15, 0, ease_in), (4.8, 0)), t)
    bow = math.sin(W(t - 1.0, 2.6)) * window(t, 1.0, 3.7, 0.35)
    rear(p, 5 * k + 1.5 * bow)
    add(p, "body", pos=(0, -STAND_DROP, 0))
    head(p, (14 - 12 * bow) * k, -4 * k, -3 * bow * k, k=(0.45, 0.35, 0.2))
    add(p, "neck3", rot=(-6 * bow * k, 0, 0))
    add(p, "skull", rot=(-8 * bow * k, 0, 0))
    fan(p, spread=11 * op, lift=14 * op, quiver=1.6 * op * window(t, 1.0, 3.6, 0.2), t=t)
    tail(p, pitch=-8 * k)
    for i, (b, w) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0, 1.5 * w * bow, 0))
    return stand(p, fore=(0.6 * k, 0.6 * k))


def wade(t):
    """in the shallows: the walk with the head held high and the feet lifted higher"""
    p = walk(t, Tc=1.8, stride=26, lift=7.0, bob=0.6, roll=2.6, yaw=1.8, head_p=14, tail_amp=3.5)
    return p


# ------------------------------------------------------------------ lying down
FOLD_F = (-58.0, 128.0, -50.0)


def lift_tail(p, clear=0.0):
    for i, b in enumerate(TAILS):
        for _ in range(20):
            if low_of(p, set(TAILS[i:])) >= clear: break
            add(p, b, rot=(-1.5, 0, 0))
    return p


BELLY_STAND = []


def lie(p, k=1.0, kh=None):
    if not BELLY_STAND:
        q = {}; add(q, "body", pos=(0, -STAND_DROP, 0)); BELLY_STAND.append(low_of(q, {"body"}))
    kh = k if kh is None else kh
    add(p, "body", pos=(0, -STAND_DROP, 0))
    b = low_of(p, {"body"}); goal = BELLY_STAND[0] * (1 - k)
    add(p, "body", pos=(0, goal - b, 0))
    up = k - kh
    if up > 0: add(p, "body", rot=(-12 * up, 0, 0))
    tail(p, pitch=-2 * k)
    head(p, 22 * k, 0, 0)
    fan(p, fold=18 * k)
    wf = smooth((k - 0.3) / 0.7)
    for s in SIDES:
        plant_h(p, s, 0.0, 3.5 * kh, meta=-40 * kh, toe=0.0, clear=0.0)
        plant_f(p, s, 0.0, -2 * k, pitch=0.0, clear=0.0)
        if wf > 0:
            for bone, fa in zip(("arm", "forearm", "hand"), FOLD_F):
                e = p[f"{bone}_{s}"]; e[0][0] = e[0][0] * (1 - wf) + fa * wf
    lift_tail(p)
    return p


def head_back(p, k=1.0, side=1.0):
    add(p, "neck1", rot=(-6 * k, 50 * k * side, 0)); add(p, "neck2", rot=(-6 * k, 56 * k * side, -14 * k * side))
    add(p, "skull", rot=(-12 * k, 26 * k * side, -18 * k * side))
    tail(p, yaw=14 * k * side)


def ko_pose(p, k=1.0, t=0.0):
    br = math.sin(W(t, 4.2))
    add(p, "body", rot=(0, 0, 82 * k), pos=(0, -6.0 * k, 0))
    head(p, -8 * k + 0.5 * br, 0, 12 * k)
    jaw(p, -2 * k)
    tail(p, pitch=-2 * k)
    for s, sg in (("l", 1), ("r", -1)):
        add(p, f"thigh_{s}", rot=(14 * k, 0, -6 * k * sg)); add(p, f"shin_{s}", rot=(-10 * k, 0, 0)); add(p, f"foot_{s}", rot=(18 * k, 0, 0))
        add(p, f"arm_{s}", rot=(18 * k, 0, -4 * k * sg)); add(p, f"forearm_{s}", rot=(-6 * k, 0, 0)); add(p, f"hand_{s}", rot=(14 * k, 0, 0))
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
    """the knockout: it staggers, the hind legs give, it sits back and rolls onto its side (into knocked_out)"""
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
    """out of the egg: curled tight, the head pushes up and out, a shake, a first look round, then up onto its legs"""
    p = {}
    k = f(tr((0, 1), (1.3, 1), (2.0, 0, smooth), (2.4, 0)), t)
    up = f(tr((0, 0), (0.25, 0), (0.6, 1, back_out), (2.4, 1)), t)
    sh = window(t, 0.65, 1.1, 0.08)
    lie(p, k)
    head(p, -30 * (1 - up) + 18 * up * k, 12 * sh * math.sin(W(t, 0.16)), 8 * sh * math.sin(W(t, 0.16)))
    head_back(p, 1.0 - up)
    jaw(p, -6 * window(t, 1.2, 1.5, 0.08))
    p = settle(lift_tail(lift_head(p, 0.0)))
    add(p, "root", pos=(0, 0.25, 0))       # the calf's curl dips between keys: a hair of clearance
    return p


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
def beg(t):
    p = {}; breathe(p, t, 2.4)
    nudge = sum(window(t, c, c + 0.18, 0.07) for c in (0.5, 1.5))
    note = window(t, 1.0, 1.3, 0.08)
    head(p, -10 + 3 * nudge + 8 * note, 4 * math.sin(W(t, 2.4)), 0)
    jaw(p, -3 * note)
    add(p, "body", rot=(0.8 * note, 0, 0), pos=(0, 0, -1.0 * nudge))
    tail_sway(p, t, 2.4, 5.0)
    return stand(p, fore=(-0.8 * nudge, -0.8 * nudge))


def tame(t):
    p = {}
    k = f(tr((0, 0), (0.5, 1, ease_out), (1.4, 1), (1.9, 0, smooth)), t)
    dn = f(tr((0, 0), (1.5, 0), (2.2, 1, smooth), (2.8, 1), (3.2, 0, smooth)), t)
    beat = window(t, 0.6, 1.3, 0.15) * (0.7 + 0.3 * math.sin(W(t, 0.2)))
    breathe(p, t, 3.2, 0.6)
    _resonate_pose(p, k, beat, rise=0.6)
    head(p, -18 * dn, 0, 0)
    tail(p, pitch=3 * dn)
    return stand(p, fore=(-1.0 * dn, -1.0 * dn))


ANIMS = {
    "idle": (idle, IDLE_T, True, "Parado", "em quatro patas, pescoço alto, respira, vira a cabeça com o elmo para olhar, rumina"),
    "walk": (walk, WALK[0], True, "Movimento", "anda em quatro patas longas, o leque alto, a cauda dura balança inteira"),
    "run": (run, RUNP[0], True, "Movimento", "galopa nas quatro patas longas como a girafa, o pescoço bombeando, o leque deitado"),
    "swim": (swim, 1.6, True, "Movimento", "nada com a cabeça fora d'água, a cauda funda rema pela raiz"),
    "wade": (wade, 1.8, True, "Só dele", "anda na água rasa de cabeça alta, levantando bem os pés"),
    "turn_left": (turn_left, TURN_T, True, "Movimento", "gira no lugar para a esquerda"),
    "turn_right": (turn_right, TURN_T, True, "Movimento", "gira no lugar para a direita"),
    "walk_tired": (walk_tired, WALK_TIRED_T, True, "Movimento", "anda cansado, cabeça pendida, boca aberta"),
    "idle_tired": (idle_tired, IDLE_TIRED_T, True, "Parado", "parado cansado: os flancos arfam, o bico aberto"),
    "deep_call": (deep_call, 4.6, False, "Só dele", "o chamado grave pelo elmo: pescoço esticado, elmo alto, bico fechado, três batidas lentas da garganta (a manada ouve a 64 blocos)"),
    "call": (call, 2.4, False, "Só dele", "o chamado curto de contato pelo elmo"),
    "answer": (answer, 2.0, False, "Só dele", "responde ao chamado de outro, o elmo virado para ele"),
    "alarm": (alarm, 2.2, False, "Só dele", "o alarme: um sopro grave e duro, meio empinado; a manada foge junta"),
    "listen": (listen, LISTEN_T, False, "Só dele", "o ouvido da mata: para, ergue a cabeça e vira o elmo devagar para um lado e para o outro"),
    "nap": (nap, NAP_T, True, "Só dele", "o cochilo catemeral em pé: a cabeça desce com o elmo, uma pata de trás descansa"),
    "fruit_pick": (fruit_pick, 4.2, False, "Só dele", "empina nas patas de trás e arranca o fruto alto com a cabeça de lado"),
    "pluck": (pluck, 3.2, False, "Só dele", "arranca bagas do arbusto com o bico estreito, a cabeça de lado, puxando"),
    "helmet_display": (helmet_display, DISPLAY_T, False, "Só dele", "de perfil para o rival: o leque abre num estalo e fica aberto tremendo, a cabeça em reverência"),
    "hatch": (hatch, 2.4, False, "Domado", "sai do ovo: a cabeça empurra para cima, sacode, olha e levanta"),
    "eat": (eat, 2.8, False, "Comer", "pega da mão e mastiga, as bochechas abrindo"),
    "graze": (graze, 3.4, False, "Comer", "come baixo com o bico estreito, cortes curtos"),
    "drink": (drink, 3.6, False, "Comer", "bebe como a girafa: patas da frente bem abertas, o pescoço desce até a água"),
    "attack": (attack, 1.2, False, "Combate", "encurralado: puxa a cabeça de lado e bate com o elmo e o ombro (golpe em 0,5 s)"),
    "kick_back": (kick_back, KICK_BACK_T, False, "Combate", "encurralado: olha para trás e chuta com a pata de trás (golpe em 0,64 s)"),
    "body_shove": (body_shove, BODY_SHOVE_T, False, "Combate", "a quadrilada: joga a anca e a base da cauda de lado (golpe em 0,66 s)"),
    "hurt": (hurt, 0.6, False, "Combate", "ao levar dano"),
    "death": (death, 3.0, False, "Combate", "as patas de trás cedem, senta, a frente desce e rola de lado"),
    "knockout": (knockout, 2.0, False, "Descanso", "nocauteado: cambaleia, senta e rola de lado"),
    "knocked_out": (knocked_out, 4.2, True, "Descanso", "nocauteado de lado"),
    "wake": (wake, 3.4, False, "Descanso", "acorda do nocaute: rola, sacode a cabeça, levanta pelo quadril"),
    "sit": (sit, 8.0, True, "Descanso", "deitado de barriga, cabeça erguida, rumina"),
    "sleep": (sleep, 10.0, True, "Descanso", "o cochilo deitado da noite, a cabeça no flanco (curto: catemeral)"),
    "wake_sleep": (wake_sleep, 2.4, False, "Descanso", "acorda: traz a cabeça, levanta o quadril primeiro, depois a frente"),
    "lie_down": (lie_down, LIE_DOWN_T, False, "Descanso", "deita: o quadril assenta primeiro, depois o peito"),
    "get_up": (get_up, GET_UP_T, False, "Descanso", "levanta pelo quadril primeiro, depois a frente"),
    "beg": (beg, 2.4, True, "Domado", "pede comida: cabeça baixa para o dono, um empurrão"),
    "tame": (tame, 3.2, False, "Domado", "responde ao dono com um chamado curto e baixa a cabeça para ele"),
}
