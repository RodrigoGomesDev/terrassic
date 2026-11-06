"""Parasaurolophus animations, written for it from its own study (page "Parassaurolofo: estudo e modelo", section
"movimento"; the 1.5 decisions delegated to the threads on 02/11/2026).

Shared with the Triceratops is only the plumbing (the forelimb IK, the plant helpers, bake and export); every pose
and every cycle is the Parasaurolophus' own, from what the study says the animal was:
- a facultative quadruped (Maidment & Barrett 2014): it WALKS on four, the slender forelegs taking a little weight
  on the hoof-like mittens, and RUNS on two, the front lifted, the arms folded, the stiff tail a level beam;
- it rises onto its hind legs to browse up to 4 m, and the male rears to show his crest broadside;
- the crest is for calling: the call is made with the BILL SHUT, the air going up the tube and back (Weishampel
  1981); the head is lifted and tipped back so the crest lies along the neck, the chest heaves with each note. A herd
  answers (answer), an alarm is sharper (alarm: a half-rear, three hard heaves, the tail lifted to show the black
  flag), the young peep with their small domes (peep) and the adults turn to them;
- it is a herd animal that lives by watching: the vigilant stare, head high and frozen (the taming is built on it);
- it chews: the jaw closes and the cheeks flex OUT (pleurokinesis, Norman & Weishampel 1985), the cheek bones swing;
- the tail is stiffened by ossified tendons: it bends at the root and swings as a beam, never a whip;
- it fights only when cornered or ridden: a shoulder barge with the head tucked and the crest laid back;
- it lies down like a big bird and gets up HIND END FIRST (a cow's way, the Triceratops gets up front first).

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
import para as TC
from anim2 import add, world, chain_angle, solve_leg, Track, smooth, ease_out, ease_in, back_out

W = lambda t, T: 2 * math.pi * t / T


def tr(*keys): return Track(keys)


def f(track, t): return float(track(t))


def window(t, a, b, fade=0.25):
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


def model():
    m = TC.build("male", saddle_on=True); P.pack(m, TC.TEX_W); return m.spec()


S = model()
SIDES = ("l", "r")
TAILS = ("tail1", "tail2", "tail3", "tail4", "tail5", "tail6")
STIFF = (1.0, 0.35, 0.22, 0.16, 0.12, 0.1)       # the tendons: most of any bend is at the root
BALL = {s: world(S, {}, f"toes_{s}") for s in SIDES}
REST_META = {s: chain_angle(S, {}, [f"foot_{s}"]) for s in SIDES}
WRIST = {s: world(S, {}, f"hand_{s}") for s in SIDES}
REST_HAND = {s: chain_angle(S, {}, [f"hand_{s}"]) for s in SIDES}
HIND = {s: {f"{b}_{s}" for b in ("thigh", "shin", "foot", "toes")} for s in SIDES}
FORE = {s: {f"{b}_{s}" for b in ("arm", "forearm", "hand")} for s in SIDES}
CRESTB = {b["name"] for b in S["bones"] if b["name"].startswith("adult_crest")}
HEADB = {"head", "skull", "jaw", "cheek_l", "cheek_r", "young_crest"} | CRESTB
SKIP = {"saddle"}
STAND_DROP = 0.8


def low_of(p, bones=None, skip=SKIP):
    return min(q[:, 1].min() for c, q in geo.cube_points(S, p)
               if (bones is None or c["bone"] in bones) and c["bone"] not in skip)


# ------------------------------------------------------------------ plumbing (the Triceratops' IK, re-fitted)
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
    """on the hind legs only (the forelegs are posed by the caller)"""
    lift_head(p, clear)
    for i, s in enumerate(SIDES): plant_h(p, s, 0, hind[i])
    return p


def head(p, pitch=0.0, yaw=0.0, roll=0.0, k=(0.35, 0.35, 0.3)):
    """a head movement spread over the two neck bones and the skull"""
    for b, w in zip(("neck1", "neck2", "skull"), k):
        add(p, b, rot=(pitch * w, yaw * w, roll * w))


def jaw(p, a): add(p, "jaw", rot=(a, 0, 0))


def cheeks(p, k):
    """pleurokinesis: the cheeks (the upper tooth rows) swing OUT as the jaw closes on them"""
    add(p, "cheek_l", rot=(0, 0, -7 * k)); add(p, "cheek_r", rot=(0, 0, 7 * k))


def chew(p, t, t0, t1, T=0.5):
    """the jaw rises and the cheeks flex out on each stroke"""
    c = window(t, t0, t1, 0.1) * max(0.0, math.sin(W(t - t0, T)))
    o = window(t, t0, t1, 0.1) * max(0.0, -math.sin(W(t - t0, T)))
    jaw(p, -5 * o); cheeks(p, c)
    return c


def tail(p, yaw=0.0, pitch=0.0):
    for b, k in zip(TAILS, STIFF): add(p, b, rot=(pitch * k, yaw * k, 0))


def tail_sway(p, t, Tc, yaw, pitch=0.0, ph=0.0):
    """the beam swings from the root, the far end following with a short lag"""
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        a = W(t, Tc) + ph - 0.25 * i
        add(p, b, rot=(pitch * k * math.sin(2 * a - 0.6), yaw * k * math.sin(a), 0))


def breathe(p, t, T=3.2, amp=1.0, drop=STAND_DROP):
    br = math.sin(W(t, T))
    add(p, "body", rot=(0.4 * amp * br, 0, 0), pos=(0, -drop - 0.25 * amp * (1 + br), 0))
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
    """the front up on the hind legs, pivoting at the hips"""
    add(p, "body", rot=(deg, 0, 0))


# ------------------------------------------------------------------ gaits
LATERAL = {"lh": 0.0, "lf": 0.75, "rh": 0.5, "rf": 0.25}      # walk on four: LH, LF, RH, RF


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
            clear = 0.8 * math.sin(math.pi * sw) ** 0.5
        if kind == "h":
            meta = 22 * heel + 20 * (1 - smooth(sw / 0.4)) * (sw > 0) - 14 * math.sin(math.pi * sw)
            toe = -24 * math.sin(math.pi * min(1, sw * 1.1)) + 3 * smooth((sw - 0.7) / 0.3) * (sw > 0)
            plant_h(p, s, ly, dz, meta, toe, clear)
        else:
            pitch = -20 * heel - 36 * math.sin(math.pi * min(1, sw * 1.15))
            plant_f(p, s, ly, dz, pitch, clear)


WALK = (1.7, 46, 0.66, 6.0, 0.7)
RUNP = (0.66, 112, 0.36, 14.0, 2.6)


def walk(t):
    """on four: the slow lateral walk, the long hind stride and the short quick fore step (the hand reaches less), the
    high hips rolling over the standing hind leg, the head nodding a little with the steps, the tail a swinging beam"""
    Tc, stride, duty, lift, bob = WALK
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    bp = 0.5 * math.sin(2 * w - 0.5)
    add(p, "body", rot=(bp, 1.6 * math.sin(w), 2.6 * math.sin(w + 0.3)),
        pos=(0, -STAND_DROP - bob * (0.5 + 0.5 * math.cos(2 * w - 0.8)), 0))
    head(p, -bp * 1.2 + 2.0 * math.sin(2 * w - 1.6), -1.4 * math.sin(w - 0.4), -2.0 * math.sin(w + 0.3))
    tail_sway(p, t, Tc, 4.0, 0.6, ph=-1.0)
    lift_head(p, 1.0)
    foot_cycle(p, ph, LATERAL, stride, duty, lift, lift * 0.8, fstride=stride * 0.9)
    return p


def run(t):
    """on two: the front lifted, the arms folded under the chest, a long bipedal stride; the body level, the neck
    stretched forward and the crest laid back along it; the tail a level beam that hardly moves"""
    Tc, stride, duty, lift, bob = RUNP
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    bp = 1.0 * math.sin(2 * w - 0.4)
    rear(p, 11 + bp)
    add(p, "body", rot=(0, 1.4 * math.sin(w), 2.4 * math.sin(w + 0.35)),
        pos=(0, -STAND_DROP - 1.5 - bob * (0.5 + 0.5 * math.cos(2 * w - 0.9)), 0))
    head(p, -14 - bp + 2.5 * math.sin(2 * w - 1.3), -1.2 * math.sin(w), -2 * math.sin(w + 0.35))
    fold_arms(p, 1.0, spread=6)
    for s, o in (("l", 0.0), ("r", math.pi)):
        add(p, f"arm_{s}", rot=(4 * math.sin(w + o), 0, 0))
    tail(p, pitch=-9)
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
            toe = -30 * math.sin(math.pi * min(1, sw * 1.15)); clear = 1.0 * math.sin(math.pi * sw) ** 0.5
        plant_h(p, s, ly, dz, meta, toe, clear)
    return settle(p)


def swim(t):
    """swims with the head and the crest up, the legs paddling in pairs and the deep flat tail sculling from the root"""
    Tc = 1.6; w = W(t, Tc); p = {}
    add(p, "body", rot=(4 + 1.2 * math.sin(2 * w), 1.5 * math.sin(w), 2.0 * math.sin(w + 0.5)), pos=(0, 0.8 * math.sin(2 * w - 1), 0))
    head(p, 20 - 1.5 * math.sin(2 * w - 1.3), -2 * math.sin(w - 0.8))
    for i, (b, k) in enumerate(zip(TAILS, (1.0, 0.8, 0.7, 0.6, 0.5, 0.5))):
        add(p, b, rot=(0, 9 * k * math.sin(w - 0.5 * i), 0))
    for s, o in (("l", 0.0), ("r", math.pi)):
        add(p, f"thigh_{s}", rot=(-12 + 24 * math.sin(w + o), 0, 0))
        add(p, f"shin_{s}", rot=(-6 + 20 * math.sin(w + o - 1.2), 0, 0))
        add(p, f"foot_{s}", rot=(10 + 18 * math.sin(w + o - 1.8), 0, 0))
        add(p, f"arm_{s}", rot=(-4 + 18 * math.sin(w + o + math.pi * 0.5), 0, 0))
        add(p, f"forearm_{s}", rot=(10 + 14 * math.sin(w + o + math.pi * 0.5 - 1.2), 0, 0))
    return p


# ------------------------------------------------------------------ standing / everyday
def idle(t):
    """on four, breathing; it lifts its head to look about, chews the cud with the cheeks flexing, the tail swings"""
    p = {}; breathe(p, t, 3.4)
    a = window(t, 1.2, 3.0, 0.5); b = window(t, 3.6, 5.0, 0.45)
    head(p, 10 * a + 4 * b, 18 * a - 22 * b, -3 * a + 3 * b)
    chew(p, t, 5.6, 7.6, 0.55)
    tail_sway(p, t, 8.0, 2.5, 0.3)
    shift = window(t, 0.5, 7.5, 1.0)
    add(p, "body", rot=(0, 0, 1.2 * shift * math.sin(W(t, 8.0))))
    return stand(p)


def vigilant(t):
    """the stare: the head high and frozen on the thing it watches, the neck straight up, the tail a little raised and
    stiff; only the breath moves, slowly (the taming waits on this: stand still while it looks)"""
    p = {}
    k = f(tr((0, 0), (0.35, 1, ease_out), (2.7, 1), (3.0, 0.8)), t)
    br = math.sin(W(t, 2.6))
    add(p, "body", rot=(2.5 * k + 0.2 * br, 0, 0), pos=(0, -STAND_DROP, 0))
    head(p, 34 * k, 0, 0, k=(0.5, 0.25, 0.25))
    add(p, "skull", rot=(-6 * k, 0, 0))
    tail(p, pitch=-5 * k)
    return stand(p, fore=(1.0 * k, 1.0 * k))


def hurt(t):
    p = {}
    k = f(tr((0, 0), (0.08, 1, ease_out), (0.6, 0, smooth)), t)
    add(p, "body", rot=(4 * k, -5 * k, -3 * k), pos=(0, -STAND_DROP - 0.5 * k, 1.5 * k))
    head(p, 12 * k, 14 * k, 8 * k)
    tail(p, yaw=8 * k, pitch=-4 * k)
    return stand(p)


def attack(t):
    """the barge: weight back on the hind legs, the head tucked down and the crest laid back out of harm, then the
    whole front thrown forward into the target with the shoulder (the hit at 0.5 s)"""
    p = {}
    back = f(tr((0, 0), (0.3, 1, ease_out), (0.42, 1), (0.5, 0, ease_in), (1.2, 0)), t)
    lunge = f(tr((0, 0), (0.4, 0), (0.52, 1, ease_in), (0.7, 0.8), (1.2, 0, smooth)), t)
    tuck = f(tr((0, 0), (0.25, 1, ease_out), (0.8, 1), (1.2, 0, smooth)), t)
    rear(p, 7 * back - 3 * lunge)
    add(p, "body", rot=(0, 6 * lunge, -4 * lunge), pos=(-1.0 * lunge, -STAND_DROP - 0.6 * lunge, 3 * back - 6 * lunge))
    head(p, -14 * tuck, -10 * lunge, 0)
    tail(p, yaw=-6 * lunge, pitch=-3 * back)
    lift_head(p)
    for s in SIDES: plant_h(p, s, 0, 2.5 * lunge)
    for s in SIDES:
        plant_f(p, s, 3.0 * back * (1 - lunge), -4 * lunge, clear=None if back > 0.05 else -0.05)
    return settle(p)


def eat(t):
    """takes a mouthful from the hand: the head down, a clip with the bill, then the chew: the jaw rises and the cheeks
    flex out on each stroke (pleurokinesis)"""
    p = {}
    dn = f(tr((0, 0), (0.45, 1, smooth), (0.8, 1), (1.0, 0.3, ease_out), (2.4, 0.3), (2.8, 0, smooth)), t)
    breathe(p, t, 2.8, 0.5)
    head(p, -22 * dn)
    jaw(p, f(tr((0, 0), (0.5, -10, ease_out), (0.7, -1, ease_in), (2.8, 0)), t))
    chew(p, t, 1.0, 2.5, 0.45)
    tail_sway(p, t, 2.8, 2.0)
    return stand(p, fore=(-1.5 * dn, -1.5 * dn))


def graze(t):
    """crops low plants with the broad bill: the head swept low from side to side clipping, then lifts and chews"""
    p = {}
    dn = f(tr((0, 0), (0.6, 1, smooth), (2.2, 1), (2.6, 0.25, smooth), (3.4, 0, smooth)), t)
    breathe(p, t, 3.4, 0.5)
    rear(p, -3 * dn)
    sweep = math.sin(W(t - 0.6, 0.8)) * window(t, 0.6, 2.2, 0.15)
    head(p, -40 * dn, 14 * sweep, -4 * sweep)
    clip = sum(window(t, c - 0.12, c, 0.05) for c in (0.85, 1.25, 1.65, 2.05))
    jaw(p, -9 * clip)
    chew(p, t, 2.6, 3.4, 0.4)
    tail_sway(p, t, 3.4, 2.0)
    return stand(p, fore=(-2.0 * dn, -2.0 * dn), clear=0.2)


def drink(t):
    """at the water: the forelegs set a little apart and forward, the head right down, the bill skims and laps, then
    the head comes up to swallow"""
    p = {}
    dn = f(tr((0, 0), (0.7, 1, smooth), (2.6, 1), (3.0, 0.2, smooth), (3.6, 0, smooth)), t)
    breathe(p, t, 3.6, 0.4)
    rear(p, -4 * dn)
    lap = window(t, 0.9, 2.5, 0.15) * math.sin(W(t, 0.36))
    head(p, -48 * dn + 2 * lap)
    jaw(p, -4 * max(0, lap))
    sw = window(t, 2.8, 3.3, 0.1)
    head(p, 10 * sw)
    for s, sx in (("l", 1), ("r", -1)): add(p, f"arm_{s}", rot=(0, 0, 6 * sx * dn))
    tail(p, pitch=-2 * dn)
    return stand(p, fore=(-3.0 * dn, -3.0 * dn), clear=0.0)


# ------------------------------------------------------------------ the crest: calls
def _call_pose(p, k, beat, rise=1.0):
    """bill shut, the head lifted and tipped back so the crest lies along the neck (the air goes up the tube and back),
    the chest heaving on each beat"""
    head(p, 26 * k * rise, 0, 0, k=(0.55, 0.3, 0.15))
    add(p, "skull", rot=(10 * k * rise + 3 * beat, 0, 0))
    add(p, "body", rot=(1.5 * k + 1.2 * beat, 0, 0), pos=(0, 0.6 * beat, 0))
    add(p, "neck1", rot=(-2.0 * beat, 0, 0))


def call(t):
    """the contact call: a long low note and a shorter one, the head up and back, the bill shut"""
    p = {}
    k = f(tr((0, 0), (0.6, 1, ease_out), (2.6, 1), (3.2, 0, smooth)), t)
    beat = window(t, 0.8, 1.9, 0.2) * (0.7 + 0.3 * math.sin(W(t, 0.18))) + window(t, 2.1, 2.5, 0.12)
    breathe(p, t, 3.2, 0.4)
    _call_pose(p, k, beat)
    tail(p, pitch=-2 * k)
    return stand(p)


def answer(t):
    """the reply to another's call: one softer note, the head not as high (the game turns it toward the caller)"""
    p = {}
    k = f(tr((0, 0), (0.45, 1, ease_out), (1.6, 1), (2.2, 0, smooth)), t)
    beat = window(t, 0.6, 1.5, 0.2) * (0.6 + 0.4 * math.sin(W(t, 0.22)))
    breathe(p, t, 2.2, 0.4)
    _call_pose(p, k, beat * 0.7, rise=0.6)
    return stand(p)


def alarm(t):
    """the alarm: the head snaps up, a half-rear with the forefeet off the ground, three hard short notes with the chest
    jolting, the tail lifted to show the black flag, then down on all fours ready to run"""
    p = {}
    k = f(tr((0, 0), (0.18, 1, ease_out), (1.9, 1), (2.6, 0, smooth)), t)
    up = f(tr((0, 0), (0.2, 0), (0.45, 1, ease_out), (1.6, 1), (2.1, 0, ease_in), (2.6, 0)), t)
    beat = sum(window(t, c, c + 0.16, 0.05) for c in (0.6, 0.95, 1.3))
    rear(p, 16 * up)
    add(p, "body", pos=(0, -STAND_DROP, 0))
    _call_pose(p, k, 1.6 * beat, rise=1.2)
    fold_arms(p, 0.6 * up)
    tail(p, pitch=-14 * k)
    lift_head(p)
    for s in SIDES: plant_h(p, s)
    for s in SIDES:
        plant_f(p, s, 0, 0, clear=-0.05 if up < 0.03 else None)
        if up >= 0.03:
            pass
    return settle(p)


def peep(t):
    """the young's call through its small dome (higher, Farke et al. 2013): two quick lifts of the head, bill shut"""
    p = {}
    b = sum(window(t, c, c + 0.14, 0.05) for c in (0.15, 0.45))
    breathe(p, t, 1.0, 0.4)
    head(p, 16 * b + 6 * window(t, 0.1, 0.8, 0.1), 0, 0, k=(0.5, 0.25, 0.25))
    add(p, "body", rot=(1.0 * b, 0, 0))
    return stand(p)


def crest_display(t):
    """the male's display: up on the hind legs, the head turned broadside so the crest shows its whole length in
    profile, swept slowly from one side to the other, a low call at the top; then down"""
    p = {}
    up = f(tr((0, 0), (0.7, 1, ease_out), (3.8, 1), (4.6, 0, smooth)), t)
    sw = f(tr((0, 0), (0.9, 0), (1.6, 1, smooth), (2.6, -1, smooth), (3.4, 0, smooth)), t)
    beat = window(t, 1.6, 2.4, 0.2) * (0.7 + 0.3 * math.sin(W(t, 0.2)))
    rear(p, 30 * up)
    add(p, "body", pos=(0, -STAND_DROP, 0))
    head(p, -18 * up, 70 * sw, 8 * sw, k=(0.4, 0.35, 0.25))
    add(p, "skull", rot=(4 * beat, 0, 0))
    add(p, "body", rot=(0.8 * beat, 0, 0))
    tail(p, pitch=-22 * up)          # held up as a level beam to balance the raised front, clear of the ground
    planted = stand({k: tuple(list(x) if isinstance(x, (list, tuple)) else x for x in v) for k, v in p.items()})
    fold_arms(p, 0.7 * up)
    stand_hind(p)
    w = smooth(min(1.0, up / 0.4))   # the hands leave the ground as it rises, and find it again as it comes down
    fb = FORE["l"] | FORE["r"]
    p.update(blend({b: planted[b] for b in fb if b in planted}, {b: p[b] for b in fb if b in p}, w))
    lift_tail(p, 0.4)
    return settle(p)


def browse_high(t):
    """up on the hind legs to the high leaves (to 4 m): the forelegs reach forward against the trunk, the bill clips
    twice, it chews up there, then drops back on all fours"""
    p = {}
    up = f(tr((0, 0), (0.8, 1, ease_out), (3.4, 1), (4.2, 0, smooth)), t)
    rear(p, 36 * up)
    add(p, "body", pos=(0, -STAND_DROP, 0))
    head(p, -6 * up + 6 * window(t, 1.0, 2.4, 0.2), 0, 0)
    clip = sum(window(t, c - 0.12, c, 0.05) for c in (1.3, 1.9))
    jaw(p, -11 * clip)
    chew(p, t, 2.2, 3.3, 0.45)
    for s, sx in (("l", 1), ("r", -1)):
        add(p, f"arm_{s}", rot=(-60 * up, 0, 4 * sx * up)); add(p, f"forearm_{s}", rot=(30 * up, 0, 0))
        add(p, f"hand_{s}", rot=(30 * up, 0, 0))
    tail(p, pitch=-26 * up)          # the tail held level, a counterweight, clear of the ground
    if up < 0.05:
        return settle(stand(p))
    stand_hind(p)
    lift_tail(p, 0.4)
    return settle(p)


# ------------------------------------------------------------------ lying down: a big bird's sit, up hind end first
FOLD_F = (-58.0, 128.0, -50.0)


def lift_tail(p, clear=0.0):
    for i, b in enumerate(TAILS):
        for _ in range(20):
            if low_of(p, set(TAILS[i:])) >= clear: break
            add(p, b, rot=(-1.5, 0, 0))
    return p


BELLY_STAND = []


def lie(p, k=1.0, kh=None):
    """the belly down, the hind legs folded under (sitting on the metatarsi), the forelegs folded under the chest.
    k = how far the FRONT is down; kh = how far the HIND end is down (getting up hind end first: kh falls first)"""
    if not BELLY_STAND:
        q = {}; add(q, "body", pos=(0, -STAND_DROP, 0)); BELLY_STAND.append(low_of(q, {"body"}))
    kh = k if kh is None else kh
    add(p, "body", pos=(0, -STAND_DROP, 0))
    b = low_of(p, {"body"}); goal = BELLY_STAND[0] * (1 - k)
    add(p, "body", pos=(0, goal - b, 0))
    up = k - kh                 # the hind end up on straightened legs while the chest is still down: nose down
    if up > 0: add(p, "body", rot=(-12 * up, 0, 0))
    tail(p, pitch=-2 * k)
    head(p, 22 * k, 0, 0)
    wf = smooth((k - 0.3) / 0.7)
    for s in SIDES:
        plant_h(p, s, 0.0, 5 * kh, meta=-40 * kh, toe=0.0, clear=0.0)
        plant_f(p, s, 0.0, -3 * k, pitch=0.0, clear=0.0)
        if wf > 0:
            for bone, fa in zip(("arm", "forearm", "hand"), FOLD_F):
                e = p[f"{bone}_{s}"]; e[0][0] = e[0][0] * (1 - wf) + fa * wf
    lift_tail(p)
    return p


def head_back(p, k=1.0, side=1.0):
    """asleep: the neck curled round, the head laid back along the flank with the bill on the shoulder and the crest
    lying down the back (the crest makes this the natural fold)"""
    add(p, "neck1", rot=(-6 * k, 52 * k * side, 0)); add(p, "neck2", rot=(-6 * k, 58 * k * side, -14 * k * side))
    add(p, "skull", rot=(-12 * k, 24 * k * side, -18 * k * side))
    tail(p, yaw=12 * k * side)


def ko_pose(p, k=1.0, t=0.0):
    """knocked out: on its side, the legs loose, the neck stretched out with the crest on the ground"""
    br = math.sin(W(t, 4.2))
    add(p, "body", rot=(0, 0, 82 * k), pos=(0, -8.0 * k, 0))
    head(p, -8 * k + 0.5 * br, 0, 12 * k)
    jaw(p, -2 * k)
    tail(p, pitch=-2 * k)
    for s, sg in (("l", 1), ("r", -1)):
        add(p, f"thigh_{s}", rot=(14 * k, 0, -6 * k * sg)); add(p, f"shin_{s}", rot=(-10 * k, 0, 0)); add(p, f"foot_{s}", rot=(18 * k, 0, 0))
        add(p, f"arm_{s}", rot=(18 * k, 0, -4 * k * sg)); add(p, f"forearm_{s}", rot=(-6 * k, 0, 0)); add(p, f"hand_{s}", rot=(14 * k, 0, 0))
    add(p, "body", pos=(0, 0.3 * br * k, 0))
    return p


def sit(t):
    """lying awake: belly down, head up, chewing now and then, a slow look round"""
    p = {}; br = math.sin(W(t, 4.0))
    lie(p)
    add(p, "body", rot=(0.3 * br, 0, 0), pos=(0, 0.15 * (1 + br), 0))
    a = window(t, 2.5, 4.4, 0.6)
    head(p, 4 - 0.4 * br, -22 * a, 3 * a)
    chew(p, t, 5.4, 7.2, 0.55)
    return settle(lift_tail(lift_head(p, 0.0)))


def sleep(t):
    p = {}; br = math.sin(W(t, 5.0))
    lie(p)
    add(p, "body", rot=(0.4 * br, 0, 0), pos=(0, 0.15 * (1 + br), 0))
    head(p, -22, 0, 0)
    head_back(p)
    return settle(lift_tail(lift_head(p, 0.0)))


def wake_sleep(t):
    """wakes: the head comes round from the flank, then up HIND END FIRST (the chest still down), then the front"""
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


def wake(t):
    """from the knockout: rolls onto its belly, shakes the head (the crest swinging), up hind end first"""
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


def _going_down(t):
    """the hind legs give first: it sits back on its haunches, the front following, the neck sagging"""
    p = {}
    st = window(t, 0.0, 0.6, 0.2)
    kh = f(tr((0, 0), (0.3, 0), (0.8, 1, ease_in), (2.0, 1)), t)
    k = f(tr((0, 0), (0.6, 0), (1.1, 1, ease_in), (2.0, 1)), t)
    add(p, "body", rot=(0, 3 * st * math.sin(W(t, 0.6)), 5 * st), pos=(1.5 * st, 0, 0))
    lie(p, max(k, 0.0), kh=max(kh, k))
    add(p, "body", rot=(10 * (kh - k), 0, 0))
    head(p, -20 * k, -8 * st, 6 * k)
    return settle(lift_tail(lift_head(p, 0.0)))


_DOWN = []


def death(t):
    """staggers, the hind legs give and it sits back, the front goes down, then it rolls onto its side"""
    if t <= 1.3:
        return _going_down(t)
    if not _DOWN: _DOWN.append(_going_down(1.3))
    roll = f(tr((1.3, 0), (2.0, 1, ease_in), (2.12, 0.95), (2.26, 1, smooth), (3.0, 1)), t)
    return shift_to_ground(blend(_DOWN[0], ko_pose({}, 1.0), roll))


# ------------------------------------------------------------------ with its owner
def beg(t):
    """asks for food: the head low and pushed toward the owner, a soft closed-bill note, a nudge"""
    p = {}; breathe(p, t, 2.4)
    nudge = sum(window(t, c, c + 0.18, 0.07) for c in (0.5, 1.5))
    note = window(t, 1.0, 1.3, 0.08)
    head(p, -10 + 3 * nudge + 8 * note, 4 * math.sin(W(t, 2.4)), 0)
    add(p, "body", rot=(0.8 * note, 0, 0), pos=(0, 0, -1.4 * nudge))
    tail_sway(p, t, 2.4, 5.0)
    return stand(p, fore=(-1.0 * nudge, -1.0 * nudge))


def tame(t):
    """accepts its owner: it answers with a call (head up, bill shut), then lowers the head to them and settles"""
    p = {}
    k = f(tr((0, 0), (0.5, 1, ease_out), (1.4, 1), (1.9, 0, smooth)), t)
    dn = f(tr((0, 0), (1.5, 0), (2.2, 1, smooth), (2.8, 1), (3.2, 0, smooth)), t)
    beat = window(t, 0.6, 1.3, 0.15) * (0.7 + 0.3 * math.sin(W(t, 0.2)))
    breathe(p, t, 3.2, 0.6)
    _call_pose(p, k, beat, rise=0.8)
    head(p, -18 * dn, 0, 0)
    tail(p, pitch=3 * dn)
    return stand(p, fore=(-1.0 * dn, -1.0 * dn))


ANIMS = {
    "idle": (idle, 8.0, True, "Parado", "em quatro patas, respira, ergue a cabeça para olhar, rumina com as bochechas abrindo"),
    "walk": (walk, WALK[0], True, "Movimento", "anda em quatro patas, passo lateral; o quadril alto rola, a cauda balança inteira"),
    "run": (run, RUNP[0], True, "Movimento", "corre em DUAS patas: a frente sobe, os braços dobram, a cauda vira uma viga"),
    "swim": (swim, 1.6, True, "Movimento", "nada com a cabeça e a crista fora d'água, a cauda funda rema pela raiz"),
    "call": (call, 3.2, False, "Só dele", "o chamado de contato: bico FECHADO, cabeça para trás, a crista ao longo do pescoço, o peito pulsa"),
    "answer": (answer, 2.2, False, "Só dele", "responde ao chamado de outro: uma nota mais baixa, virado para quem chamou"),
    "alarm": (alarm, 2.6, False, "Só dele", "o alarme: meio empinado, três notas fortes, a cauda sobe e mostra a bandeira preta"),
    "peep": (peep, 1.0, False, "Só dele", "o filhote chama pela cúpula pequena: duas erguidas rápidas da cabeça"),
    "vigilant": (vigilant, 3.0, False, "Só dele", "o vigia: cabeça alta e parada no que observa (a doma depende disso)"),
    "crest_display": (crest_display, 4.6, False, "Só dele", "a exibição do macho: empina e mostra a crista de perfil, de um lado ao outro"),
    "browse_high": (browse_high, 4.2, False, "Só dele", "empina nas patas de trás até as folhas altas e mastiga lá em cima"),
    "drink": (drink, 3.6, False, "Só dele", "bebe: patas da frente abertas, o bico raspa a água, ergue para engolir"),
    "eat": (eat, 2.8, False, "Comer", "pega da mão e mastiga: a mandíbula sobe e as bochechas abrem para fora"),
    "graze": (graze, 3.4, False, "Comer", "pasta com o bico largo, de um lado para o outro, e mastiga"),
    "attack": (attack, 1.2, False, "Combate", "o tranco de ombro: recua o peso, crista deitada, e joga a frente no alvo"),
    "hurt": (hurt, 0.6, False, "Combate", "ao levar dano"),
    "death": (death, 3.0, False, "Combate", "as patas de trás cedem, senta, a frente desce e rola de lado"),
    "sit": (sit, 8.0, True, "Descanso", "deitado de barriga, cabeça erguida, rumina"),
    "sleep": (sleep, 10.0, True, "Descanso", "dorme com a cabeça deitada no flanco e a crista ao longo do lombo"),
    "wake_sleep": (wake_sleep, 2.4, False, "Descanso", "acorda: traz a cabeça, levanta o QUADRIL primeiro, depois a frente"),
    "knocked_out": (knocked_out, 4.2, True, "Descanso", "nocauteado de lado, a crista no chão"),
    "wake": (wake, 3.4, False, "Descanso", "acorda do nocaute: rola, sacode a cabeça, levanta pelo quadril"),
    "beg": (beg, 2.4, True, "Domado", "pede comida: cabeça baixa para o dono, uma nota baixa, um empurrão"),
    "tame": (tame, 3.2, False, "Domado", "responde ao dono com um chamado e baixa a cabeça para ele"),
}

# 06/11/2026: the fluid set (paraflow.py, docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md): the same names and lengths,
# the fluid versions bound in their place, the new ones after
import paraflow as FLOW  # noqa: E402
ANIMS_BEFORE_FLOW = ANIMS
ANIMS = FLOW.rebind(ANIMS)
