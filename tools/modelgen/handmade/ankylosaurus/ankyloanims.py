"""Ankylosaurus animations, written for it from its own study (page "Anquilossauro 1.5", section "movimento"; the 1.5
decisions delegated to the threads on 02/11/2026).

Shared with the Triceratops and the Parasaurolophus is only the plumbing (the leg and arm IK, the plant helpers, bake
and export); every pose and every cycle is the Ankylosaurus' own, from what the study says the animal was:
- a heavy, low, wide quadruped on short legs: a slow lateral walk, the broad body rolling over each planted foot, the
  head low and steady; when it hurries it TROTS (diagonal pairs, short quick steps), it never gallops;
- the tail is its weapon (Arbour 2009; Arbour & Snively 2009): the base is flexible and swings the stiff handle like a
  bat, sideways, with the club at the height of a theropod's shin. The swing comes from the hips and the base of the
  tail, the body twisting AGAINST it on the planted forefeet (club_l / club_r: to its left or right, at whatever is at
  its side or behind). Before it swings it warns: the tail lifted off the ground and swung slowly from side to side
  (club_warn), the head held low, the body turned so the club faces the threat;
- rival males club each other on the flanks (healed broken flank plates in Zuul, Arbour et al. 2022): flank_club, a
  braced stance and two slower blows to the side;
- the defence of an armoured animal against something at its head: it drops flat on its belly with the legs splayed and
  the head drawn down between the shoulder plates (hunker), so only armour faces up;
- it feeds low, under 1 m (a low browser, the head never far from the ground): it crops ferns (graze), roots with a
  forefoot and its beak (dig), and snorts through its big looping nasal passages (snort, Miyashita et al. 2011);
- it does not roll onto its side: lying, knocked out or dying, it stays on its belly (an armoured back and a belly
  twice as wide as it is deep), the legs splayed out.

Signs on this rig: body +x = nose up; neck/skull -x = down; jaw -x = open; tail pitch + = down; yaw + = the far end
of the tail toward the animal's left (+x, the "_l" bones); thigh/arm +x = the foot swings forward.
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
import ankylo as TC
from anim2 import add, world, chain_angle, solve_leg, Track, smooth, ease_out, ease_in

W = lambda t, T: 2 * math.pi * t / T


def tr(*keys): return Track(keys)


def f(track, t): return float(track(t))


def window(t, a, b, fade=0.25):
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


def model():
    m = TC.build("male", saddle_on=True); P.pack(m, TC.TEX_W); return m.spec()


S = model()
SIDES = ("l", "r")
TAILS = ("tail1", "tail2", "tail3", "tail4", "tail5")
BASE = (1.0, 0.55, 0.12, 0.08, 0.05)      # the swing: almost all of it at the root, the handle stiff (Arbour 2009)
SOFT = (1.0, 0.8, 0.5, 0.35, 0.25)        # a lazy sway at rest
BALL = {s: world(S, {}, f"toes_{s}") for s in SIDES}
REST_META = {s: chain_angle(S, {}, [f"foot_{s}"]) for s in SIDES}
WRIST = {s: world(S, {}, f"hand_{s}") for s in SIDES}
REST_HAND = {s: chain_angle(S, {}, [f"hand_{s}"]) for s in SIDES}
HIND = {s: {f"{b}_{s}" for b in ("thigh", "shin", "foot", "toes")} for s in SIDES}
FORE = {s: {f"{b}_{s}" for b in ("arm", "forearm", "hand")} for s in SIDES}
HEADB = {"head", "skull", "jaw"}
SKIP = {"saddle", "young_tail"}
STAND_DROP = 0.6


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
        add(p, "neck", rot=(1.5, 0, 0))
    return p


def lift_tail(p, clear=0.3):
    for i, b in enumerate(TAILS):
        for _ in range(25):
            if low_of(p, set(TAILS[i:]) | {"adult_club"}) >= clear: break
            add(p, b, rot=(-1.2, 0, 0))
    return p


def stand(p, fore=(0, 0), hind=(0, 0), clear=0.3):
    lift_head(p, clear)
    lift_tail(p, 0.3)
    for i, s in enumerate(SIDES):
        plant_h(p, s, 0, hind[i])
        plant_f(p, s, 0, fore[i])
    return p


def head(p, pitch=0.0, yaw=0.0, roll=0.0, k=0.55):
    """a head movement spread over the short neck (k) and the skull"""
    add(p, "neck", rot=(pitch * k, yaw * k, roll * k))
    add(p, "skull", rot=(pitch * (1 - k), yaw * (1 - k), roll * (1 - k)))


def jaw(p, a): add(p, "jaw", rot=(a, 0, 0))


def tail(p, yaw=0.0, pitch=0.0, prof=SOFT):
    for b, k in zip(TAILS, prof): add(p, b, rot=(pitch * k, yaw * k, 0))


def tail_sway(p, t, Tc, yaw, pitch=0.0, ph=0.0):
    for i, (b, k) in enumerate(zip(TAILS, SOFT)):
        a = W(t, Tc) + ph - 0.35 * i
        add(p, b, rot=(pitch * k * math.sin(2 * a - 0.6), yaw * k * math.sin(a), 0))


def breathe(p, t, T=3.6, amp=1.0, drop=STAND_DROP):
    """the wide ribcage: the breath shows as a slow swell of the flanks, the body rising a little"""
    br = math.sin(W(t, T))
    add(p, "body", rot=(0.25 * amp * br, 0, 0), pos=(0, -drop - 0.2 * amp * (1 + br), 0))
    head(p, -0.4 * amp * br)
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


# ------------------------------------------------------------------ gaits
LATERAL = {"lh": 0.0, "lf": 0.75, "rh": 0.5, "rf": 0.25}      # walk: four even beats
TROT = {"lh": 0.0, "rf": 0.02, "rh": 0.5, "lf": 0.52}          # trot: the diagonal pairs together


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
            clear = 0.6 * math.sin(math.pi * sw) ** 0.5
        if kind == "h":
            meta = 14 * heel + 12 * (1 - smooth(sw / 0.4)) * (sw > 0) - 8 * math.sin(math.pi * sw)
            toe = -10 * math.sin(math.pi * min(1, sw * 1.1))
            plant_h(p, s, ly, dz, meta, toe, clear)
        else:
            pitch = -12 * heel - 22 * math.sin(math.pi * min(1, sw * 1.15))
            plant_f(p, s, ly, dz, pitch, clear)


WALK = (1.8, 30, 0.7, 3.5, 0.5)
TROTP = (0.9, 40, 0.5, 5.0, 1.0)


def walk(t):
    """the heavy lateral walk: short steps, the wide body ROLLING onto each planted side (the widest roll of any rig),
    the head low and kept steady by the neck, the tail swaying from its root with the club trailing"""
    Tc, stride, duty, lift, bob = WALK
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    roll = 3.4 * math.sin(w + 0.4)
    add(p, "body", rot=(0.3 * math.sin(2 * w - 0.5), 1.2 * math.sin(w), roll),
        pos=(0, -STAND_DROP - bob * (0.5 + 0.5 * math.cos(2 * w - 0.8)), 0))
    head(p, 0.6 * math.sin(2 * w - 1.6), -1.0 * math.sin(w - 0.4), -roll * 0.7)
    tail_sway(p, t, Tc, 5.0, 0.4, ph=-1.2)
    foot_cycle(p, ph, LATERAL, stride, duty, lift, lift)
    return settle(lift_tail(lift_head(p, 1.0), 0.6))


def run(t):
    """the hurry of a heavy low animal: a short quick trot, diagonal pairs, the body bouncing a little and rolling less,
    the head a touch up, the tail out stiff behind (it does not gallop)"""
    Tc, stride, duty, lift, bob = TROTP
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    add(p, "body", rot=(0.8 + 0.6 * math.sin(2 * w), 0.8 * math.sin(w), 1.4 * math.sin(w + 0.3)),
        pos=(0, -STAND_DROP - 0.3 - bob * (0.5 + 0.5 * math.cos(2 * w + 0.5)), 0))
    head(p, 2 + 1.2 * math.sin(2 * w - 1.2), 0, -0.8 * math.sin(w + 0.3))
    tail(p, pitch=-3, prof=SOFT)
    tail_sway(p, t, Tc, 2.0, 0.8, ph=-0.8)
    foot_cycle(p, ph, TROT, stride, duty, lift, lift)
    return settle(lift_tail(lift_head(p, 1.0), 0.6))


def swim(t):
    """swims low and heavy, only the armour of the back awash: the legs paddle in diagonal pairs, the head up, the tail
    sculling slowly from the root"""
    Tc = 1.8; w = W(t, Tc); p = {}
    add(p, "body", rot=(5 + 0.8 * math.sin(2 * w), 1.0 * math.sin(w), 2.0 * math.sin(w + 0.5)), pos=(0, 0.5 * math.sin(2 * w - 1), 0))
    head(p, 14 - 1.2 * math.sin(2 * w - 1.3), -1.5 * math.sin(w - 0.8))
    for i, (b, k) in enumerate(zip(TAILS, SOFT)):
        add(p, b, rot=(0, 7 * k * math.sin(w - 0.5 * i), 0))
    for s, o in (("l", 0.0), ("r", math.pi)):
        add(p, f"thigh_{s}", rot=(-10 + 22 * math.sin(w + o), 0, 0))
        add(p, f"shin_{s}", rot=(-6 + 16 * math.sin(w + o - 1.2), 0, 0))
        add(p, f"arm_{s}", rot=(-4 + 18 * math.sin(w + o + math.pi), 0, 0))
        add(p, f"forearm_{s}", rot=(8 + 12 * math.sin(w + o + math.pi - 1.2), 0, 0))
    return p


# ------------------------------------------------------------------ standing / everyday
def idle(t):
    """on four, breathing slowly; the head low, now and then lifted to look, a crop of the beak at the ground; the
    tail resting off the ground, swinging a little; the weight shifting from one side to the other"""
    p = {}; breathe(p, t, 3.8)
    a = window(t, 1.4, 3.2, 0.5); b = window(t, 4.2, 5.6, 0.45)
    head(p, 6 * a - 4 * b, 16 * a - 18 * b, -2 * a + 2 * b)
    sniff = window(t, 6.4, 7.4, 0.15) * math.sin(W(t, 0.3))
    add(p, "skull", rot=(1.2 * sniff, 0, 0))
    tail_sway(p, t, 8.0, 3.0, 0.3)
    add(p, "body", rot=(0, 0, 1.0 * math.sin(W(t, 8.0))))
    return stand(p)


def hurt(t):
    p = {}
    k = f(tr((0, 0), (0.08, 1, ease_out), (0.6, 0, smooth)), t)
    add(p, "body", rot=(-2 * k, -3 * k, -3 * k), pos=(0, -STAND_DROP - 0.25 * k, 0.8 * k))
    head(p, -8 * k, 10 * k, 4 * k)
    tail(p, yaw=10 * k, pitch=-3 * k, prof=BASE)
    return stand(p)


def attack(t):
    """the head hook: something right in front of it (or the rider's target) gets a short sideways jab of the head, the
    cheek horns leading; the forefeet braced (the hit at 0.35 s)"""
    p = {}
    cock = f(tr((0, 0), (0.22, 1, ease_out), (0.3, 1), (0.4, -1, ease_in), (0.55, -0.8), (0.9, 0, smooth)), t)
    dn = f(tr((0, 0), (0.2, 1, ease_out), (0.6, 1), (0.9, 0, smooth)), t)
    add(p, "body", rot=(-1.5 * dn, 3 * cock, -2 * cock), pos=(0, -STAND_DROP - 0.6 * dn, -1.0 * dn))
    head(p, -8 * dn, 26 * cock, -12 * cock, k=0.5)
    tail(p, yaw=-6 * cock, prof=BASE)
    return stand(p, fore=(-2 * dn, -2 * dn))


def _club(t, side=1.0, power=1.0, T0=0.0):
    """one swing of the club to the given side (+1 = its left). The weight goes onto the forefeet, the hips swing the
    other way, the tail is wound up toward the far side first, then whipped through; the body twists against it on the
    planted forefeet; the head held low and turned away. The impact (the club's widest point) is at T0 + 0.55 s"""
    p = {}
    wind = f(tr((T0 + 0, 0), (T0 + 0.35, 1, ease_out), (T0 + 0.42, 1)), t)
    hit = f(tr((T0 + 0, 0), (T0 + 0.42, 0), (T0 + 0.6, 1, ease_in), (T0 + 0.72, 1.12, ease_out), (T0 + 1.0, 0.8),
               (T0 + 1.5, 0, smooth)), t)
    swing = (-0.7 * wind * (1 - smooth(hit * 2)) + hit) * side * power
    brace = f(tr((T0 + 0, 0), (T0 + 0.3, 1, ease_out), (T0 + 1.1, 1), (T0 + 1.5, 0, smooth)), t)
    add(p, "body", rot=(-2.5 * brace, -14 * swing, -4 * swing), pos=(-2.0 * swing, -STAND_DROP - 0.8 * brace, -1.0 * brace))
    head(p, -10 * brace, 14 * swing, 3 * swing)
    for b, k in zip(TAILS, BASE):
        add(p, b, rot=(-6 * brace * k, 52 * swing * k, -6 * swing * k))
    return p, brace


def club_l(t):
    """the swing to its left: the club sweeps out and round at shin height"""
    p, br = _club(t, 1.0)
    return settle(stand(p, fore=(-2 * br, -2 * br)))


def club_r(t):
    p, br = _club(t, -1.0)
    return settle(stand(p, fore=(-2 * br, -2 * br)))


def club_warn(t):
    """the warning: the tail lifted off the ground and swung slowly from side to side, the club rocking at the end of the
    stiff handle like a pendulum, the body low and braced, the head down and still"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (2.6, 1), (3.0, 0, smooth)), t)
    breathe(p, t, 1.5, 0.6)
    add(p, "body", rot=(-2 * k, 0, 0), pos=(0, -0.8 * k, 0))
    head(p, -8 * k, 0, 0)
    sw = math.sin(W(t - 0.4, 1.3)) * window(t, 0.4, 2.7, 0.3)
    for i, (b, kk) in enumerate(zip(TAILS, BASE)):
        add(p, b, rot=(-10 * k * kk, 22 * sw * kk * (1 + 0.3 * i), 0))
    return settle(stand(p, fore=(-1.5 * k, -1.5 * k)))


def flank_club(t):
    """two males side by side: braced, two slow blows of the club against the rival's flank (to its left), not the full
    swing of the defence"""
    p, br = _club(t, 1.0, 0.55)
    q, br2 = _club(t, 1.0, 0.55, T0=1.5)
    if t > 1.5: p, br = q, br2
    add(p, "body", rot=(0, 0, 2 * br))
    return settle(stand(p, fore=(-1.5 * br, -1.5 * br)))


def hunker(t):
    """flat on its belly against a threat at its head: the legs splay out to the sides, the body sinks onto the ground,
    the head drawn down and in between the shoulder plates, the tail laid along one side ready; it holds, breathing
    hard, then rises"""
    p = {}
    k = f(tr((0, 0), (0.45, 1, ease_in), (2.6, 1), (3.2, 0, smooth)), t)
    br = math.sin(W(t, 0.9)) * window(t, 0.5, 2.6, 0.2)
    lie(p, k, splay=1.0)
    add(p, "body", pos=(0, 0.15 * br, 0))
    head(p, -18 * k, 0, 0, k=0.7)
    add(p, "skull", rot=(-6 * k, 0, 0))
    tail(p, yaw=16 * k, prof=SOFT)
    return settle(lift_tail(lift_head(p, 0.0), 0.0))


def snort(t):
    """a snort through the big looping nasal passages: the head lifts, a sharp blow with a toss, a shake"""
    p = {}; breathe(p, t, 2.0, 0.5)
    up = f(tr((0, 0), (0.3, 1, ease_out), (0.5, 1), (0.6, -0.5, ease_in), (0.9, 0, smooth)), t)
    sh = window(t, 0.9, 1.7, 0.12) * math.sin(W(t, 0.26))
    head(p, 10 * up, 12 * sh, 8 * sh)
    add(p, "body", rot=(0.8 * up, 0, 0), pos=(0, -0.3 * max(0, -up), 0))
    return stand(p)


def dig(t):
    """roots for food: a forefoot scrapes the ground twice, then the beak noses into the scrape and crops"""
    p = {}; breathe(p, t, 3.0, 0.4)
    dn = f(tr((0, 0), (1.3, 0), (1.7, 1, smooth), (2.8, 1), (3.2, 0, smooth)), t)
    head(p, -22 * dn - 6 * window(t, 0.0, 1.3, 0.3), 0, 0)
    root = sum(window(t, c, c + 0.18, 0.06) for c in (1.9, 2.3))
    jaw(p, -6 * root)
    add(p, "skull", rot=(-3 * root, 0, 0))
    tail_sway(p, t, 3.2, 2.0)
    stand(p, fore=(0, 0))
    # the scraping forefoot (the left), lifted and drawn back twice, after the stand has planted it
    for c in (0.25, 0.75):
        u = window(t, c, c + 0.4, 0.1)
        if u > 0:
            ph = (t - c) / 0.4
            plant_f(p, "l", 2.5 * math.sin(math.pi * min(1, ph)) * u, 5 * u - 9 * smooth(ph) * u, -10 * u, clear=None)
    return settle(p)


def eat(t):
    """takes what is at its beak: the head down to the ground, a crop, then the chew (the jaw rises and falls, short)"""
    p = {}
    dn = f(tr((0, 0), (0.45, 1, smooth), (0.8, 1), (1.0, 0.4, ease_out), (2.2, 0.4), (2.6, 0, smooth)), t)
    breathe(p, t, 2.6, 0.5)
    head(p, -20 * dn)
    jaw(p, f(tr((0, 0), (0.5, -8, ease_out), (0.7, -1, ease_in), (2.6, 0)), t))
    chew = window(t, 1.0, 2.3, 0.1) * max(0.0, math.sin(W(t - 1.0, 0.42)))
    jaw(p, -3 * chew)
    tail_sway(p, t, 2.6, 2.0)
    return stand(p, fore=(-1.0 * dn, -1.0 * dn))


def graze(t):
    """crops low ferns: the head swung low in short arcs, the narrow beak clipping, then a chew with the head up"""
    p = {}
    dn = f(tr((0, 0), (0.5, 1, smooth), (2.3, 1), (2.7, 0.3, smooth), (3.4, 0, smooth)), t)
    breathe(p, t, 3.4, 0.5)
    sweep = math.sin(W(t - 0.5, 0.9)) * window(t, 0.5, 2.3, 0.15)
    head(p, -18 * dn, 12 * sweep, -3 * sweep)
    clip = sum(window(t, c - 0.12, c, 0.05) for c in (0.8, 1.25, 1.7, 2.15))
    jaw(p, -7 * clip)
    chew = window(t, 2.6, 3.3, 0.1) * max(0.0, math.sin(W(t - 2.6, 0.4)))
    jaw(p, -3 * chew)
    tail_sway(p, t, 3.4, 2.0)
    return stand(p, clear=0.2)


def drink(t):
    """at the water: the forelegs spread, the head right down (the neck is short, so the front sinks too), laps"""
    p = {}
    dn = f(tr((0, 0), (0.7, 1, smooth), (2.6, 1), (3.0, 0.2, smooth), (3.6, 0, smooth)), t)
    breathe(p, t, 3.6, 0.4)
    add(p, "body", rot=(-4 * dn, 0, 0), pos=(0, -1.2 * dn, 0))
    lap = window(t, 0.9, 2.5, 0.15) * math.sin(W(t, 0.4))
    head(p, -26 * dn + 2 * lap)
    jaw(p, -3 * max(0, lap))
    for s, sx in (("l", 1), ("r", -1)): add(p, f"arm_{s}", rot=(0, 0, 5 * sx * dn))
    return stand(p, fore=(-3.0 * dn, -3.0 * dn), clear=0.0)


# ------------------------------------------------------------------ lying down: flat on the belly, legs splayed
FOLD_F = (-50.0, 110.0, -40.0)
BELLY_STAND = []


def lie(p, k=1.0, kf=None, splay=0.0):
    """the belly down on the ground, the hind legs folded under, the forelegs folded under the chest or, splayed, out to
    the sides; k = how far the body is down; kf = how far the front is (unused: it rises level)"""
    if not BELLY_STAND:
        q = {}; add(q, "body", pos=(0, -STAND_DROP, 0)); BELLY_STAND.append(low_of(q, {"body"}))
    kf = k if kf is None else kf
    add(p, "body", pos=(0, -STAND_DROP, 0))
    b = low_of(p, {"body"}); goal = BELLY_STAND[0] * (1 - k) - 0.2 * k
    add(p, "body", pos=(0, goal - b, 0))
    tail(p, pitch=-1 * k)
    wf = smooth((kf - 0.3) / 0.7)
    for s, sx in (("l", 1), ("r", -1)):
        plant_h(p, s, 0.0, 3 * k, meta=-30 * k, toe=0.0, clear=0.0)
        plant_f(p, s, 0.0, -3 * kf, pitch=0.0, clear=0.0)
        if wf > 0:
            for bone, fa in zip(("arm", "forearm", "hand"), FOLD_F):
                e = p[f"{bone}_{s}"]; e[0][0] = e[0][0] * (1 - wf) + fa * wf
        if splay:
            add(p, f"thigh_{s}", rot=(0, 0, 26 * sx * splay * k)); add(p, f"arm_{s}", rot=(0, 0, 30 * sx * splay * k))
    return p


def ko_pose(p, k=1.0, t=0.0):
    """knocked out: flat on its belly (it does not roll), the legs splayed out loose, the head on the ground turned a
    little, the tail limp on the ground"""
    br = math.sin(W(t, 4.4))
    lie(p, k, splay=1.0)
    head(p, -14 * k + 0.4 * br, 10 * k, -8 * k, k=0.6)
    jaw(p, -3 * k)
    add(p, "body", rot=(0, 0, 4 * k), pos=(0, 0.2 * br * k, 0))
    tail(p, yaw=10 * k, pitch=4 * k)
    return p


def sit(t):
    """lying awake on its belly, the head up off the ground, a slow look round, a chew now and then"""
    p = {}; br = math.sin(W(t, 4.2))
    lie(p)
    add(p, "body", rot=(0.25 * br, 0, 0), pos=(0, 0.12 * (1 + br), 0))
    a = window(t, 2.5, 4.4, 0.6)
    head(p, 2 - 0.3 * br, -18 * a, 2 * a)
    chew = window(t, 5.4, 7.0, 0.1) * max(0.0, math.sin(W(t - 5.4, 0.45)))
    jaw(p, -3 * chew)
    return settle(lift_tail(lift_head(p, 0.0), 0.0))


def sleep(t):
    """asleep on its belly, the chin flat on the ground in front of the forefeet, the tail curled round one side so the
    club lies by the head"""
    p = {}; br = math.sin(W(t, 5.2))
    lie(p)
    add(p, "body", rot=(0.3 * br, 0, 0), pos=(0, 0.12 * (1 + br), 0))
    head(p, -16, 6, -4, k=0.6)
    for i, b in enumerate(TAILS): add(p, b, rot=(1, 14 * (0.6 + 0.15 * i), 0))
    return settle(lift_tail(lift_head(p, 0.0), 0.0))


def wake_sleep(t):
    """wakes: the head up, the tail swung back out, then it pushes up LEVEL on all four at once (the armour is too heavy
    to rock up one end first), and shakes"""
    p = {}
    kb = f(tr((0, 1), (0.8, 0, smooth), (2.6, 0)), t)
    k = f(tr((0, 1), (0.9, 1), (1.8, 0, ease_out), (2.6, 0)), t)
    lie(p, k)
    head(p, -16 * kb, 6 * kb, -4 * kb, k=0.6)
    for i, b in enumerate(TAILS): add(p, b, rot=(0, 14 * kb * (0.6 + 0.15 * i), 0))
    sh = window(t, 1.9, 2.5, 0.08)
    add(p, "body", rot=(0, 0, 3 * sh * math.sin(W(t, 0.2))))
    return settle(lift_tail(lift_head(p, 0.0), 0.0))


def knocked_out(t):
    return shift_to_ground(ko_pose({}, 1.0, t))


def wake(t):
    """from the knockout: the head lifts and shakes, the legs come in under it, it pushes up"""
    roll = f(tr((0, 1), (0.6, 1), (1.4, 0, smooth), (3.2, 0)), t)
    k = f(tr((0, 1), (1.8, 1), (2.6, 0, ease_out), (3.2, 0)), t)
    p = {}
    lie(p, k, splay=roll)
    sh = window(t, 0.4, 1.3, 0.12)
    head(p, -14 * roll + 4 * sh, 10 * roll + 12 * sh * math.sin(W(t, 0.32)), -8 * roll, k=0.6)
    return settle(lift_tail(lift_head(p, 0.0), 0.0))


_DOWN = []


def death(t):
    """the legs give, the hind first: it sinks onto its belly and settles, the head drops forward to the ground, the
    tail goes limp; it stays upright on its belly"""
    p = {}
    kh = f(tr((0, 0), (0.3, 0), (0.9, 1, ease_in), (3.0, 1)), t)
    k = f(tr((0, 0), (0.6, 0), (1.3, 1, ease_in), (1.45, 0.94), (1.6, 1, smooth), (3.0, 1)), t)
    st = window(t, 0.0, 0.6, 0.2)
    add(p, "body", rot=(6 * (k - kh), 2 * st * math.sin(W(t, 0.6)), 3 * st))
    lie(p, max(k, kh * 0.6), splay=smooth((t - 1.3) / 0.8))
    hd = f(tr((0, 0), (1.2, 0.2), (2.0, 1, ease_in), (3.0, 1)), t)
    head(p, -20 * hd, 8 * hd, -6 * hd, k=0.6)
    tail(p, yaw=6 * hd, pitch=5 * hd)
    return shift_to_ground(lift_head(p, 0.0))


# ------------------------------------------------------------------ with its owner
def beg(t):
    """asks for food: the head low and pushed toward the owner, a snort, a nudge of the beak"""
    p = {}; breathe(p, t, 2.4)
    nudge = sum(window(t, c, c + 0.18, 0.07) for c in (0.5, 1.5))
    note = window(t, 1.0, 1.25, 0.08)
    head(p, -6 + 3 * nudge + 6 * note, 3 * math.sin(W(t, 2.4)), 0)
    add(p, "body", rot=(0.6 * note, 0, 0), pos=(0, 0, -1.0 * nudge))
    tail_sway(p, t, 2.4, 6.0)
    return stand(p, fore=(-1.0 * nudge, -1.0 * nudge))


def tame(t):
    """accepts its owner: it lets the tail drop and go slack (the club down, no threat), lowers the head and turns it to
    them, then a soft snort"""
    p = {}
    dn = f(tr((0, 0), (0.6, 1, smooth), (2.4, 1), (3.0, 0, smooth)), t)
    sn = window(t, 1.6, 1.9, 0.08)
    breathe(p, t, 3.0, 0.6)
    head(p, -10 * dn + 6 * sn, 18 * dn, 0)
    tail(p, pitch=6 * dn)
    add(p, "body", pos=(0, -0.6 * dn, 0))
    return stand(p, fore=(-1.0 * dn, -1.0 * dn))


ANIMS = {
    "idle": (idle, 8.0, True, "Parado", "em quatro patas, respira, cabeça baixa, olha em volta, a cauda balança fora do chão"),
    "walk": (walk, WALK[0], True, "Movimento", "passo lateral curto, o corpo largo ROLA de um lado para o outro"),
    "run": (run, TROTP[0], True, "Movimento", "a pressa dele é um TROTE curto em pares diagonais; não galopa"),
    "swim": (swim, 1.8, True, "Movimento", "nada baixo, só o dorso de fora, a cauda rema pela raiz"),
    "club_l": (club_l, 1.6, False, "Só dele", "o golpe de clava para a ESQUERDA: arma, o quadril gira e a clava varre à altura da canela"),
    "club_r": (club_r, 1.6, False, "Só dele", "o mesmo para a direita"),
    "club_warn": (club_warn, 3.0, False, "Só dele", "o aviso: cauda erguida balançando devagar, a clava como pêndulo"),
    "flank_club": (flank_club, 3.0, False, "Só dele", "dois machos lado a lado: dois golpes mais lentos no flanco (Zuul)"),
    "hunker": (hunker, 3.2, False, "Só dele", "achatar: barriga no chão, pernas abertas, cabeça recolhida entre as placas"),
    "snort": (snort, 1.8, False, "Só dele", "bufa pelas vias do nariz: ergue a cabeça, sopra e sacode"),
    "dig": (dig, 3.2, False, "Só dele", "cava raízes: a pata da frente raspa duas vezes e o bico fuça"),
    "drink": (drink, 3.6, False, "Só dele", "bebe: patas abertas, a frente desce junto, o bico na água"),
    "attack": (attack, 0.9, False, "Combate", "gancho de cabeça para o que está na frente (os chifres da bochecha primeiro)"),
    "hurt": (hurt, 0.6, False, "Combate", "ao levar dano"),
    "death": (death, 3.0, False, "Combate", "as pernas cedem e ele assenta de barriga; não tomba de lado"),
    "eat": (eat, 2.6, False, "Comer", "come o que está no chão, à frente do bico, e mastiga"),
    "graze": (graze, 3.4, False, "Comer", "corta samambaia rente ao chão em arcos curtos"),
    "sit": (sit, 8.0, True, "Descanso", "deitado de barriga, cabeça erguida"),
    "sleep": (sleep, 10.0, True, "Descanso", "dorme de barriga, o queixo no chão, a cauda dobrada com a clava junto da cabeça"),
    "wake_sleep": (wake_sleep, 2.6, False, "Descanso", "acorda: levanta nivelado, nas quatro patas de uma vez, e sacode"),
    "knocked_out": (knocked_out, 4.4, True, "Descanso", "nocauteado de barriga, pernas abertas (não vira de lado)"),
    "wake": (wake, 3.2, False, "Descanso", "acorda do nocaute: sacode a cabeça, recolhe as pernas e levanta"),
    "beg": (beg, 2.4, True, "Domado", "pede comida: cabeça baixa para o dono, bufa, empurra com o bico"),
    "tame": (tame, 3.0, False, "Domado", "aceita o dono: a cauda cai e afrouxa, a cabeça baixa virada para ele"),
}


# ------------------------------------------------------------------ the fluid set and the duel (06/11/2026, ankyflow.py)
import ankyflow as FLOW  # noqa: E402
for _n in ("idle", "walk", "run", "swim", "club_l", "club_r", "club_warn", "flank_club", "hunker", "snort", "dig", "drink",
           "attack", "hurt", "death", "eat", "graze", "sit", "sleep", "wake_sleep", "knocked_out", "wake", "beg", "tame"):
    ANIMS[_n] = (getattr(FLOW, _n),) + ANIMS[_n][1:]
ANIMS.update({
    "club_duel": (FLOW.club_duel, FLOW.DUEL_T, False, "Duelo", "golpe de clava no flanco do rival: grande preparo, golpe em 1,35 s (Zuul)"),
    "guard": (FLOW.guard, FLOW.GUARD_T, True, "Duelo", "em guarda: o flanco virado para o rival, a cauda armada do outro lado"),
    "strafe_left": (FLOW.strafe_left, FLOW.STRAFE_T, True, "Duelo", "anda de lado para a esquerda nas quatro patas, flanco para o rival"),
    "strafe_right": (FLOW.strafe_right, FLOW.STRAFE_T, True, "Duelo", "anda de lado para a direita"),
    "turn_left": (FLOW.turn_left, FLOW.TURN_T, True, "Movimento", "gira no lugar para a esquerda: a frente pisa para dentro, a traseira para fora"),
    "turn_right": (FLOW.turn_right, FLOW.TURN_T, True, "Movimento", "gira no lugar para a direita"),
    "feint": (FLOW.feint, FLOW.FEINT_T, False, "Duelo", "meio golpe: arma a clava, começa o giro e segura"),
    "block": (FLOW.block, FLOW.BLOCK_T, False, "Duelo", "aguenta a clava do rival no flanco blindado, pernas abertas"),
    "recoil": (FLOW.recoil, FLOW.RECOIL_T, False, "Duelo", "a clava bateu em armadura: a cauda volta e vibra, um passo para trás"),
    "submit": (FLOW.submit, FLOW.SUBMIT_T, False, "Duelo", "desiste: clava no chão, barriga baixa, vira as costas blindadas"),
    "lie_down": (FLOW.lie_down, FLOW.LIE_DOWN_T, False, "Descanso", "deita de barriga (a traseira cede primeiro)"),
    "get_up": (FLOW.get_up, FLOW.GET_UP_T, False, "Descanso", "levanta nivelado nas quatro patas e balança"),
    "idle_tired": (FLOW.idle_tired, FLOW.IDLE_TIRED_T, True, "Parado", "cansado: os flancos arfam, bico aberto, cabeça baixa"),
    "walk_tired": (FLOW.walk_tired, FLOW.WALK_TIRED_T, True, "Movimento", "andando cansado: passos curtos, cabeça pendurada"),
})

# 06/11/2026: the three moves of the new duel (ankyfight.py): lunge, parry, stagger (fixed lengths for the Java)
import ankyfight as FIGHT  # noqa: E402
ANIMS.update(FIGHT.NEW)
