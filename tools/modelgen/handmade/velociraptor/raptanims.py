"""Velociraptor v3: the animation set (ANIMS lists them with when the game plays each).
Every function maps time (s) -> pose; feet are planted by IK, lying poses are ground-fitted.

What makes it a raptor and not a small T. rex:
  * the tail is a stiff rod: it swings from its base (tail1) and the other two sections barely bend;
  * the head moves like a bird's: quick snaps that then hold still, while the body moves under it;
  * the arms are folded wings: they open for balance when running, turning, leaping and pinning prey;
  * toe II is held up; the sickle claw comes down only in the kick and the pin.
"""
import math
import numpy as np
import geo, proto as P, raptor
from anim2 import *

# v3 is drawn 1.64x bigger than v2b (48 px per metre): every translation written below is in v2b pixels and scales
K = 1.64
_add = add


def add(pose, bone, rot=(0, 0, 0), pos=(0, 0, 0), scale=None):
    return _add(pose, bone, rot, tuple(K * x for x in pos), scale)



def model():
    m = raptor.build(); raptor.separate_coplanar(m); P.pack(m, 256); return m.spec()


S = model()
BALL = {s: world(S, {}, f"toes_{s}") for s in ("l", "r")}
REST_META = {s: chain_angle(S, {}, [f"foot_{s}"]) for s in ("l", "r")}
ANKLE = {s: world(S, {}, f"foot_{s}") for s in ("l", "r")}
HIP_Y = world(S, {}, "body")[1]
LIE_HIP = 10.4          # hip height lying on the belly (keel on the ground)
LEG = {s: {f"{b}_{s}" for b in ("thigh", "shin", "foot", "toes")} for s in ("l", "r")}
SIDES = (("l", 0.0), ("r", 0.5))
W = lambda t, T: 2 * math.pi * t / T


def tr(*keys): return Track(keys)


def window(t, a, b, fade=0.25):
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


def leg_low(pose, s):
    return min(q[:, 1].min() for c, q in geo.cube_points(S, pose) if c["bone"] in LEG[s])


def plant(pose, s, dy=0.0, dz=0.0, meta=0.0, toe=0.0, clear=-0.05):
    b = BALL[s]; target = (b[1] + K * dy, b[2] + K * dz); clear = None if clear is None else (K * clear if clear > 0 else clear)
    for _ in range(4):
        solve_leg(S, pose, s, target, REST_META[s] + meta, toe)
        if clear is None: break
        lo = leg_low(pose, s)
        if lo > clear - 0.02: break
        target = (target[0] + clear - lo, target[1])


def stand(pose, crouch=0.0):
    if crouch: add(pose, "body", pos=(0, -crouch, 0))
    for s, _ in SIDES: plant(pose, s)
    return pose


def tail(pose, yaw=0.0, pitch=0.0):
    """the stiff tail: almost all of the motion at the base, a little give further back"""
    add(pose, "tail1", rot=(pitch, yaw, 0))
    add(pose, "tail2", rot=(pitch * 0.15, yaw * 0.12, 0))
    add(pose, "tail3", rot=(pitch * 0.1, yaw * 0.08, 0))


def wings(pose, k, flap=0.0, side=None):
    """k = 0 carried ready (claws forward) .. 1 spread wide (display, pin); flap adds a beat (-1..1). The arm turns
    about its own long axis first so the feathers face forward and down when it swings out, as in a mantling bird."""
    for s, sx in (("l", 1), ("r", -1)):
        if side and s != side: continue
        add(pose, f"arm_{s}", rot=(30 * k, sx * 50 * k, sx * (80 * k + 25 * flap)))
        add(pose, f"forearm_{s}", rot=(-95 * k, 0, 0))
        add(pose, f"hand_{s}", rot=(-5 * k, 0, sx * 8 * flap))


def breathe(pose, t, T=1.4, amp=1.0):
    br = math.sin(W(t, T))
    add(pose, "body", rot=(0.8 * amp * br, 0, 0), pos=(0, 0.15 * amp * br, 0))
    add(pose, "neck", rot=(-0.6 * amp * br, 0, 0))
    return br


def snaps(t, keys):
    """bird head: quick moves (0.08 s) that then hold"""
    out = [(0.0, keys[0][1])]
    for i in range(1, len(keys)):
        t0, v = keys[i]
        out.append((t0, out[-1][1])); out.append((t0 + 0.08, v, ease_out))
    tk = Track(out)
    return tk(t)


# ------------------------------------------------------------------ gaits
def gait(t, T, stride, duty, lift, bob, lean=0.0, drop=0.0, head=0.0, tail_up=0.0, sway=1.0, wing=0.0, roll=2.0, toe_sw=-35):
    ph = (t / T) % 1.0; w = 2 * math.pi * ph; pose = {}
    add(pose, "body", rot=(lean + 1.0 * math.sin(2 * w - 0.4), 2.0 * sway * math.sin(w), roll * sway * math.sin(w + 0.35)),
        pos=(0, -bob * math.cos(2 * w - 0.9) - 0.3 - drop, 0))
    # bird head: the neck absorbs the bob so the eye stays level
    add(pose, "neck", rot=(head - lean * 0.7 + 1.6 * math.sin(2 * w - 0.4), -2.0 * sway * math.sin(w - 0.2), 0))
    add(pose, "skull", rot=(head * 0.3 - lean * 0.3 - 0.8 * math.sin(2 * w - 0.6), 0, -1.0 * sway * math.sin(w)))
    tail(pose, yaw=-4.0 * sway * math.sin(w - 0.6), pitch=tail_up + 1.2 * math.sin(2 * w - 1.2))
    if wing: wings(pose, wing, flap=0.15 * math.sin(2 * w))
    # arms a little forward and out while walking so the elbow clears the knee as the leg swings through
    for s, sx in (("l", 1), ("r", -1)):
        add(pose, f"arm_{s}", rot=(20 + 3 * math.sin(w + (0 if s == "l" else math.pi) - 2.0), 0, sx * 6))
    for s, o in SIDES:
        u = (ph + o) % 1.0
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0
            meta = 30 * smooth(max(0, (st - 0.5) / 0.5)); toe = 0.0; clear = -0.05
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e
            ly = lift * math.sin(math.pi * min(1, sw * 1.15)) ** 1.3
            meta = 30 * (1 - smooth(sw / 0.5)) - 15 * math.sin(math.pi * sw)
            toe = toe_sw * math.sin(math.pi * min(1, sw * 1.1)) + 5 * smooth((sw - 0.7) / 0.3)
            clear = 0.8 * math.sin(math.pi * sw) ** 0.5
        plant(pose, s, ly, dz - 1, meta, toe, clear)
    return pose


def walk(t): return gait(t, 0.8, 16, 0.6, 3.0, 0.5)
def run(t): return gait(t, 0.4, 28, 0.38, 4.5, 1.2, lean=8, drop=0.5, head=-6, tail_up=3, sway=0.5, wing=0.35, roll=1.0)
def stalk(t):
    p = gait(t, 1.3, 8, 0.72, 1.2, 0.25, lean=4, drop=2.0, head=-14, tail_up=-1, sway=0.4, roll=0.6)
    add(p, "skull", rot=(4, snaps(t % 2.6, [(0, 0), (0.6, 10), (1.5, -8), (2.3, 0)]), 0))
    return p


def swim(t):
    T = 0.7; w = W(t, T); p = {}
    add(p, "body", rot=(-10 + 1.5 * math.sin(2 * w), 0, 3 * math.sin(w)), pos=(0, 0.6 * math.sin(2 * w), 0))
    add(p, "neck", rot=(22, 0, 0)); add(p, "skull", rot=(-6, 0, 0))
    tail(p, yaw=6 * math.sin(w), pitch=6)
    wings(p, 0.25, flap=0.3 * math.sin(2 * w))
    for s, o in SIDES:
        f = w + o * 2 * math.pi
        add(p, f"thigh_{s}", rot=(-15 + 35 * math.sin(f), 0, 0)); add(p, f"shin_{s}", rot=(-20 - 25 * math.cos(f), 0, 0))
        add(p, f"foot_{s}", rot=(25 + 25 * math.cos(f + 0.6), 0, 0)); add(p, f"toes_{s}", rot=(-30 * math.sin(f + 1.0), 0, 0))
    return p


def leap(t):
    """the jump at the prey (LeapAtTargetGoal): crouch, launch, airborne with both feet forward and the sickle claws
    raised, wings out for balance, land"""
    p = {}
    c = float(tr((0, 0), (0.18, 1), (0.28, -0.4, ease_out), (0.75, -0.4), (0.9, 0.6, ease_in), (1.1, 0))(t))
    air = window(t, 0.26, 0.82, 0.08)
    add(p, "body", rot=(6 * max(0, c) - 10 * air, 0, 0), pos=(0, -3 * max(0, c), 0))
    add(p, "neck", rot=(-10 * max(0, c) + 8 * air, 0, 0)); add(p, "skull", rot=(-6 * air, 0, 0))
    add(p, "jaw", rot=(-28 * air, 0, 0))
    tail(p, pitch=10 * air - 6 * max(0, c))
    wings(p, 0.9 * air, flap=0.3 * air)
    if air > 0.01:
        for s, _ in SIDES:
            # legs swing forward under the chest, feet up and claws forward
            add(p, f"thigh_{s}", rot=(50 * air, 0, 0)); add(p, f"shin_{s}", rot=(-30 * air, 0, 0))
            add(p, f"foot_{s}", rot=(10 * air, 0, 0)); add(p, f"toes_{s}", rot=(-30 * air, 0, 0))
        add(p, "root", pos=(0, 3 * math.sin(math.pi * min(1, max(0, (t - 0.26) / 0.56))), 0))
        if t < 0.3 or t > 0.78:
            for s, _ in SIDES: plant(p, s)
    else:
        for s, _ in SIDES: plant(p, s)
    return p


# ------------------------------------------------------------------ idle family
def idle(t):
    """breathing, a slow weight shift and the bird head: snaps to look, holds, snaps again"""
    p = {}; breathe(p, t)
    sh = math.sin(W(t, 6.0))
    add(p, "body", rot=(0, 0.8 * sh, 1.0 * sh))
    yaw = snaps(t, [(0, 0), (0.9, 18), (2.0, 18), (2.2, -6), (3.2, -22), (4.4, 4), (5.4, 0)])
    pit = snaps(t, [(0, 0), (0.9, 4), (2.2, -2), (3.2, 6), (4.4, 0)])
    tilt = snaps(t, [(0, 0), (0.9, -8), (2.2, 0), (3.2, 10), (4.4, 0)])
    add(p, "neck", rot=(pit * 0.3, yaw * 0.35, 0)); add(p, "skull", rot=(pit * 0.7, yaw * 0.65, tilt))
    lids(p, window(t, 2.75, 2.85, 0.05) + window(t, 4.9, 5.0, 0.05))
    tail(p, yaw=1.5 * math.sin(W(t, 6.0) - 0.8), pitch=0.6 * math.sin(W(t, 1.4) - 0.5))
    return stand(p)


def sniff(t):
    p = {}; breathe(p, t)
    down = float(tr((0, 0), (0.4, 1), (2.2, 1), (2.6, 0))(t))
    add(p, "body", rot=(-6 * down, 0, 0)); add(p, "neck", rot=(-28 * down, 0, 0)); add(p, "skull", rot=(-6 * down, 0, 0))
    sn = sum(math.exp(-((t - c) / 0.05) ** 2) for c in (0.8, 1.0, 1.4, 1.6, 1.8))
    add(p, "skull", rot=(3 * sn, snaps(t, [(0, 0), (0.7, 8), (1.3, -8), (2.0, 0)]), 0))
    tail(p, pitch=4 * down)
    return stand(p)


def preen(t):
    """turns the head back and runs the wing feathers through the jaws, a nibble at a time"""
    p = {}; breathe(p, t)
    k = float(tr((0, 0), (0.5, 1), (2.7, 1), (3.2, 0))(t))
    nib = math.sin(2 * math.pi * 5 * t) * window(t, 0.6, 2.7, 0.1)
    add(p, "body", rot=(0, 10 * k, -6 * k))
    add(p, "neck", rot=(-10 * k, 60 * k, 0)); add(p, "skull", rot=(-25 * k + 3 * nib, 55 * k, -15 * k))
    add(p, "jaw", rot=(-8 * k * (0.5 + 0.5 * nib), 0, 0))
    wings(p, 0.25 * k, side="l")
    tail(p, yaw=8 * k)
    return stand(p)


def ruffle(t):
    """the feather shake: a shiver from the head back to the tail, wings lifted a little"""
    p = {}
    env = lambda d: math.exp(-((t - 0.7 - d) / 0.3) ** 2)
    for bone, a, d in (("skull", 16, 0.0), ("neck", 10, 0.04), ("body", 5, 0.1)):
        add(p, bone, rot=(0, a * 0.3 * env(d) * math.sin(2 * math.pi * 8 * (t - d)), a * env(d) * math.sin(2 * math.pi * 8 * (t - d))))
    add(p, "tail1", rot=(0, 6 * env(0.16) * math.sin(2 * math.pi * 8 * (t - 0.16)), 0))
    wings(p, 0.25 * env(0.08), flap=0.4 * env(0.08) * math.sin(2 * math.pi * 8 * t))
    add(p, "neck", rot=(6 * window(t, 0.2, 1.2), 0, 0))
    return stand(p)


def stretch(t):
    """bird stretch: one wing and the leg on the same side reach back together, then the other side"""
    p = {}; breathe(p, t, amp=0.5)
    a = float(tr((0, 0), (0.6, 1), (1.3, 1), (1.7, 0), (3.6, 0))(t)); b = float(tr((0, 0), (1.7, 0), (2.3, 1), (3.0, 1), (3.6, 0))(t))
    for s, k, sx in (("l", a, 1), ("r", b, -1)):
        add(p, f"arm_{s}", rot=(-20 * k, 0, sx * 25 * k)); add(p, f"forearm_{s}", rot=(-90 * k, 0, 0)); add(p, f"hand_{s}", rot=(-10 * k, 0, 0))
    add(p, "body", rot=(2 * (a + b), 0, 3 * (a - b)))
    add(p, "neck", rot=(10 * max(a, b), 0, 0))
    plant(p, "r" if a > 0.01 else "l")
    if a > 0.01:
        plant(p, "l", 3 * a, 8 * a, -20 * a, 30 * a, clear=0.0)
    else:
        plant(p, "r", 3 * b, 8 * b, -20 * b, 30 * b, clear=0.0)
    tail(p, pitch=3 * max(a, b))
    return p


def look_back(t):
    p = {}; breathe(p, t)
    k = float(tr((0, 0), (0.3, 0), (0.6, 1), (1.8, 1), (2.1, 0.2), (2.4, 0))(t))
    add(p, "body", rot=(0, 6 * k, 0)); add(p, "neck", rot=(4 * k, 40 * k, 0)); add(p, "skull", rot=(2 * k, 40 * k, -10 * k))
    tail(p, yaw=5 * k)
    return stand(p)


# ------------------------------------------------------------------ voice and display
def call(t):
    """chirping trill: chin up, throat pulses, three short calls"""
    p = {}
    k = float(tr((0, 0), (0.3, 1), (1.6, 1), (2.0, 0))(t))
    pulses = sum(math.exp(-((t - c) / 0.06) ** 2) for c in (0.55, 0.85, 1.15))
    add(p, "neck", rot=(14 * k, 0, 0)); add(p, "skull", rot=(10 * k + 3 * pulses, 0, 0))
    add(p, "jaw", rot=(-14 * pulses, 0, 0))
    tail(p, pitch=2 * k)
    return stand(p)


def screech(t):
    """the hunting cry before a chase: head thrown up and forward, mouth wide, wings flicked out"""
    p = {}
    k = float(tr((0, 0), (0.25, -0.4), (0.5, 1, ease_out), (1.4, 1), (1.8, 0, back_out))(t))
    a = max(0, k); c = max(0, -k) / 0.4
    vib = math.sin(2 * math.pi * 14 * t) * window(t, 0.5, 1.4, 0.1)
    add(p, "body", rot=(-6 * a + 4 * c, 0, 0), pos=(0, -1.5 * c, 0))
    add(p, "neck", rot=(30 * a - 10 * c + vib, 0, 0)); add(p, "skull", rot=(12 * a + vib, 0, 0))
    add(p, "jaw", rot=(-45 * a - 1.5 * vib, 0, 0))
    wings(p, 0.45 * a, flap=0.2 * vib)
    tail(p, pitch=6 * a)
    return stand(p)


def display(t):
    """threat: crouched, wings spread wide and held, neck ruff up, a hiss with the mouth open, the tail lashes once"""
    p = {}
    k = float(tr((0, 0), (0.3, 1, ease_out), (1.9, 1), (2.3, 0))(t))
    hiss = window(t, 0.5, 1.6, 0.15)
    add(p, "body", rot=(6 * k, 0, 0), pos=(0, -2.5 * k, 0))
    add(p, "neck", rot=(-16 * k, 0, 0)); add(p, "skull", rot=(4 * k, 6 * math.sin(W(t, 1.2)) * k, 0))
    add(p, "jaw", rot=(-30 * hiss, 0, 0))
    wings(p, k, flap=0.15 * math.sin(2 * math.pi * 3 * t) * k)
    tail(p, yaw=10 * math.sin(2 * math.pi * 1.2 * t) * k, pitch=6 * k)
    return stand(p)


# ------------------------------------------------------------------ combat
def attack(t):
    """lunge and bite, a sideways tear, back off"""
    p = {}
    n = tr((0, (0, 0)), (0.15, (10, 0), ease_out), (0.3, (-18, 0), ease_in), (0.45, (-14, 14)), (0.6, (-14, -10)), (1.0, (0, 0)))(t)
    j = float(tr((0, 0), (0.15, -38, ease_out), (0.3, -2, ease_in), (0.75, -2), (1.0, 0))(t))
    push = float(tr((0, 0), (0.15, 1.5), (0.3, -3, ease_in), (0.7, -2), (1.0, 0))(t))
    add(p, "body", rot=(4 * window(t, 0.15, 0.7, 0.1), 0, 0), pos=(0, -0.8 * window(t, 0.15, 0.7, 0.1), push))
    add(p, "neck", rot=(n[0], n[1] * 0.6, 0)); add(p, "skull", rot=(n[0] * 0.5, n[1] * 0.4, -n[1] * 0.6))
    add(p, "jaw", rot=(j, 0, 0))
    wings(p, 0.35 * window(t, 0.1, 0.7, 0.1))
    tail(p, yaw=-6 * math.sin(2 * math.pi * t), pitch=3 * window(t, 0.15, 0.7, 0.1))
    return stand(p)


def kick(t):
    """the sickle-claw kick: weight back, one foot raised high, slash down and forward, recover"""
    p = {}
    up = float(tr((0, 0), (0.3, 1, ease_out), (0.42, 1), (0.55, -0.2, ease_in), (0.9, 0))(t))
    a = max(0, up)
    add(p, "body", rot=(-8 * a, 0, 3 * a), pos=(0, 0.5 * a, 1.5 * a))
    add(p, "neck", rot=(6 * a, 0, 0)); add(p, "jaw", rot=(-20 * window(t, 0.2, 0.6, 0.1), 0, 0))
    wings(p, 0.6 * window(t, 0.1, 0.7, 0.1))
    tail(p, pitch=-6 * a)
    plant(p, "l")
    plant(p, "r", 9 * a, -8 * a, -25 * a, -45 * a, clear=None)
    return p


def pounce(t):
    """RPR (Fowler et al. 2011): lands on top of the prey, pins it under both feet, flaps to stay on, bites down"""
    p = {}
    k = float(tr((0, 0), (0.2, 1, ease_out), (2.4, 1), (2.8, 0))(t))
    flap = math.sin(2 * math.pi * 3.2 * t) * window(t, 0.2, 2.3, 0.15)
    add(p, "root", pos=(0, 4 * k, 0))
    add(p, "body", rot=(14 * k + 2 * flap, 0, 0), pos=(0, -1 * k, 0))
    add(p, "neck", rot=(-38 * k, 0, 0)); add(p, "skull", rot=(-10 * k, 0, 0))
    bites = sum(math.exp(-((t - c) / 0.07) ** 2) for c in (0.7, 1.3, 1.9))
    add(p, "jaw", rot=(-30 * (k - bites) * (k > 0.5), 0, 0))
    add(p, "neck", rot=(-8 * bites, 0, 0))
    wings(p, k, flap=0.8 * flap)
    tail(p, pitch=10 * k, yaw=4 * flap)
    for s, _ in SIDES:
        plant(p, s, 4 * k, -2 * k, 5 * k, -20 * k, clear=None)
    return p


def hurt(t):
    p = {}; e = math.exp(-(t / 0.12)) * smooth(t / 0.03)
    add(p, "body", rot=(-6 * e, 6 * e, -5 * e), pos=(0, -0.5 * e, 1.5 * e))
    add(p, "neck", rot=(14 * e, -10 * e, 0)); add(p, "skull", rot=(8 * e, -6 * e, 8 * e)); add(p, "jaw", rot=(-25 * e, 0, 0))
    wings(p, 0.5 * e)
    tail(p, yaw=-8 * e, pitch=4 * e)
    return stand(p)


# ------------------------------------------------------------------ eating and drinking
def eat(t):
    """head down, bite, a back-tug with a twist, swallow with the head up like a bird"""
    p = {}
    down = float(tr((0, 0), (0.35, 1), (1.6, 1), (1.85, 0.2), (2.4, 0.2), (2.6, 0))(t))
    tug = sum(math.exp(-((t - c) / 0.08) ** 2) for c in (0.75, 1.25))
    add(p, "body", rot=(-11 * down, 0, 0), pos=(0, -0.3 * down, 0))
    add(p, "neck", rot=(-2 * down + 10 * tug, 0, 0)); add(p, "skull", rot=(-8 * down + 6 * tug, 8 * tug, -14 * tug))
    j = float(tr((0, 0), (0.35, -25), (0.55, -2, ease_in), (1.0, -20), (1.15, -2, ease_in), (1.6, 0), (2.0, -10), (2.1, 0), (2.25, -10), (2.35, 0))(t))
    add(p, "jaw", rot=(j, 0, 0))
    gulp = window(t, 1.85, 2.4, 0.08); add(p, "skull", rot=(18 * gulp, 0, 0))
    wings(p, 0.15 * down)
    tail(p, pitch=8 * down)
    return stand(p)


def drink(t):
    """dips the snout, then tips the head up to let the water run down, twice"""
    p = {}
    seq = tr((0, 0), (0.4, 1), (0.9, 1), (1.2, -0.6), (1.6, -0.6), (2.0, 1), (2.5, 1), (2.8, -0.6), (3.2, -0.6), (3.6, 0))
    k = float(seq(t)); d = max(0, k); u = max(0, -k) / 0.6
    add(p, "body", rot=(-13 * d, 0, 0), pos=(0, -0.4 * d, 0))
    add(p, "neck", rot=(-5 * d + 18 * u, 0, 0)); add(p, "skull", rot=(-6 * d + 22 * u, 0, 0))
    add(p, "jaw", rot=(-4 * d, 0, 0))
    tail(p, pitch=8 * d)
    return stand(p)


# ------------------------------------------------------------------ resting
def lie(p, k, head_down=0.0):
    """k = 0 standing .. 1 resting on the belly with the metatarsi flat, like a resting bird"""
    _add(p, "body", rot=(3 * k, 0, 0), pos=(0, -(HIP_Y - LIE_HIP) * k, 0))
    add(p, "neck", rot=(-10 * k - 30 * head_down, 0, 0)); add(p, "skull", rot=(6 * k, 0, 0))
    tail(p, pitch=-6 * k)
    for s, sx in (("l", 1), ("r", -1)): add(p, f"arm_{s}", rot=(0, 0, sx * 10 * k))    # folded arms clear the toes
    for s, _ in SIDES:
        b = BALL[s]
        a = ANKLE[s]; lie_ankle = (1.6, b[2] - 2 * K + 8.0)
        solve_leg2(S, p, s, (b[1] + 0.2 * k, b[2] - 2 * K * k), (a[1] + (lie_ankle[0] - a[1]) * k, a[2] + (lie_ankle[1] - a[2]) * k), w_ankle=0.8 * k + 0.05)
    return p


def sit(t):
    p = {}; br = math.sin(W(t, 2.0))
    lie(p, 1.0); add(p, "body", rot=(0.6 * br, 0, 0))
    yaw = snaps(t % 6.0, [(0, 0), (1.5, 20), (3.0, -15), (4.5, 0)])
    add(p, "neck", rot=(0, yaw * 0.4, 0)); add(p, "skull", rot=(0, yaw * 0.6, 0))
    return ground_fit(S, p)


def lids(p, k):
    """k = 0 open .. 1 shut"""
    add(p, "lid_l", pos=(0.35 * k, 0, 0)); add(p, "lid_r", pos=(-0.35 * k, 0, 0))


def sleep(t):
    """the Mei long posture: lying down, the neck curled round and the head laid back along the body, eyes shut, the
    tail curled round"""
    p = {}; br = math.sin(W(t, 3.0))
    lie(p, 1.0); lids(p, 1.0)
    add(p, "neck", rot=(-30, 70, 0)); add(p, "skull", rot=(0, 80, -20))
    add(p, "body", rot=(0.6 * br, 0, 0), pos=(0, 0.1 * br, 0))
    add(p, "tail1", rot=(0, 28, 0)); add(p, "tail2", rot=(0, 18, 0)); add(p, "tail3", rot=(0, 14, 0))
    return ground_fit(S, p)


def wake_sleep(t):
    p = {}
    hd = float(tr((0, 1), (0.7, 0), (2.0, 0))(t))
    up = float(tr((0, 1), (0.9, 1), (1.6, 0, back_out), (2.0, 0))(t))
    lie(p, up); lids(p, float(tr((0, 1), (0.35, 1), (0.5, 0))(t)))
    add(p, "neck", rot=(-30 * hd, 70 * hd, 0)); add(p, "skull", rot=(0, 80 * hd, -20 * hd))
    tc = hd
    add(p, "tail1", rot=(0, 28 * tc, 0)); add(p, "tail2", rot=(0, 18 * tc, 0))
    env = math.exp(-((t - 1.75) / 0.12) ** 2)
    wings(p, 0.3 * env, flap=0.5 * env * math.sin(2 * math.pi * 9 * t))
    return ground_fit(S, p)


def knocked_out(t):
    p = {}; br = math.sin(W(t, 3.0))
    lie(p, 0.8); lids(p, 1.0)
    add(p, "root", rot=(0, 0, 82))
    add(p, "body", rot=(0.6 * br, 0, 0)); add(p, "neck", rot=(-6, 0, -18)); add(p, "skull", rot=(-6, 0, -10)); add(p, "jaw", rot=(-12 - 2 * br, 0, 0))
    wings(p, 0.2)
    # the upper leg drawn a little forward and out, so its sickle claw lies on the flank instead of in it
    add(p, "thigh_r", rot=(10, 0, -4))
    return ground_fit(S, p)


def wake(t):
    p = {}
    roll = float(tr((0, 82), (0.25, 82), (0.7, 0, ease_out), (2.2, 0))(t))
    k = float(tr((0, 0.8), (0.7, 1.0), (1.2, 1.0), (1.8, 0, back_out), (2.2, 0))(t))
    lie(p, k); lids(p, float(tr((0, 1), (0.5, 1), (0.6, 0), (0.75, 0.6), (0.85, 0))(t)))
    add(p, "root", rot=(0, 0, roll))
    side = roll / 82.0
    add(p, "neck", rot=(-6 * side, 0, -18 * side)); add(p, "skull", rot=(-6 * side, 0, -10 * side)); add(p, "jaw", rot=(-12 * side, 0, 0))
    env = math.exp(-((t - 1.0) / 0.15) ** 2)
    add(p, "skull", rot=(0, 5 * env * math.sin(2 * math.pi * 8 * t), 14 * env * math.sin(2 * math.pi * 8 * t)))
    wings(p, 0.2 * side + 0.4 * env, flap=0.4 * env * math.sin(2 * math.pi * 8 * t))
    return ground_fit(S, p)


def death(t):
    p = {}
    g = float(tr((0, 0), (0.4, 0.15), (0.9, 0.8, ease_in), (2.4, 0.8))(t))
    rl = float(tr((0, 0), (0.55, -6), (0.95, 86, ease_in), (1.1, 78), (1.25, 83), (2.4, 82))(t))
    lie(p, g); lids(p, smooth((t - 1.6) / 0.5))
    add(p, "root", rot=(0, 0, rl))
    k = smooth((t - 0.9) / 0.3)
    add(p, "neck", rot=(10 * window(t, 0, 0.7) - 8 * k, 0, -18 * k)); add(p, "skull", rot=(-6 * k, 0, -10 * k))
    add(p, "jaw", rot=(-25 * window(t, 0.1, 0.8) - 12 * k, 0, 0))
    wings(p, 0.6 * window(t, 0.1, 0.9, 0.15) + 0.2 * k, flap=0.6 * window(t, 0.1, 0.8, 0.1) * math.sin(2 * math.pi * 6 * t))
    return ground_fit(S, p)


# ------------------------------------------------------------------ tamed
def beg(t):
    """head bobs, a soft chirp, shifting from foot to foot"""
    T = 1.0; w = W(t, T); p = {}
    add(p, "body", rot=(-3, 0, 2 * math.sin(w)), pos=(0, 0.3 * abs(math.sin(w)), 0))
    bob = max(0, math.sin(2 * w))
    add(p, "neck", rot=(16 + 5 * bob, 0, 0)); add(p, "skull", rot=(8 - 6 * bob, 0, 10 * math.sin(w - 1)))
    add(p, "jaw", rot=(-10 * max(0, math.sin(2 * w + 1.2)), 0, 0))
    tail(p, yaw=5 * math.sin(w), pitch=2)
    for s, o in SIDES:
        f = w + o * 2 * math.pi
        plant(p, s, 2 * max(0, math.sin(f)) ** 2, 0, 0, -6 * max(0, math.sin(f)), clear=-0.05)
    return p


def tame(t):
    """accepts you: a head toss, wings flicked twice, tail lifted"""
    p = {}
    k = float(tr((0, 0), (0.3, 1, ease_out), (1.4, 1), (2.0, 0))(t))
    toss = math.exp(-((t - 0.4) / 0.12) ** 2)
    flick = sum(math.exp(-((t - c) / 0.08) ** 2) for c in (0.8, 1.1))
    add(p, "neck", rot=(18 * k + 8 * toss, 0, 0)); add(p, "skull", rot=(10 * k, 0, 12 * math.sin(2 * math.pi * 1.5 * t) * k))
    add(p, "jaw", rot=(-14 * toss, 0, 0))
    wings(p, 0.55 * flick)
    tail(p, pitch=6 * k, yaw=4 * math.sin(2 * math.pi * 2 * t) * k)
    return stand(p)


# name: (fn, length, loop, category, when it plays)
ANIMS = {
    "idle": (idle, 5.4, True, "Parado", "base: respira, cabeça de pássaro (vira rápido e para)"),
    "sniff": (sniff, 2.6, False, "Parado", "gesto sorteado parado: fareja o chão"),
    "look_back": (look_back, 2.4, False, "Parado", "gesto sorteado parado"),
    "preen": (preen, 3.2, False, "Parado", "gesto sorteado parado: arruma as penas da asa com a boca"),
    "ruffle": (ruffle, 1.4, False, "Parado", "gesto sorteado; ao sair da água ou da chuva: arrepia e sacode as penas"),
    "stretch": (stretch, 3.6, False, "Parado", "gesto sorteado; ao acordar: estica asa e perna do mesmo lado, como ave"),
    "walk": (walk, 0.8, True, "Movimento", "andando"),
    "run": (run, 0.4, True, "Movimento", "correndo; asas meio abertas para equilíbrio"),
    "stalk": (stalk, 1.3, True, "Movimento", "chegando perto da presa, agachado"),
    "swim": (swim, 0.7, True, "Movimento", "na água"),
    "leap": (leap, 1.1, False, "Movimento", "o salto sobre a presa (já existe o LeapAtTargetGoal)"),
    "call": (call, 2.0, False, "Voz", "trinado curto chamando o bando"),
    "screech": (screech, 1.8, False, "Voz", "grito de caça antes da corrida"),
    "display": (display, 2.3, False, "Voz", "ameaça: asas abertas, chiado de boca aberta"),
    "attack": (attack, 1.0, False, "Combate", "mordida com puxão"),
    "kick": (kick, 0.9, False, "Combate", "chute com a garra em foice"),
    "pounce": (pounce, 2.8, False, "Combate", "monta na presa pequena, prende com os pés e bate as asas (RPR)"),
    "hurt": (hurt, 0.5, False, "Combate", "ao levar dano"),
    "death": (death, 2.4, False, "Combate", "ao morrer"),
    "eat": (eat, 2.6, False, "Comer", "comendo carne ou carcaça; engole erguendo a cabeça"),
    "drink": (drink, 3.6, False, "Comer", "bebe como ave: molha o bico e ergue a cabeça"),
    "sit": (sit, 6.0, True, "Descanso", "sentado (domado) ou descansando"),
    "sleep": (sleep, 6.0, True, "Descanso", "dormindo na pose do Mei long: cabeça dobrada sobre a asa"),
    "wake_sleep": (wake_sleep, 2.0, False, "Descanso", "acordando de um sono normal"),
    "knocked_out": (knocked_out, 3.0, True, "Descanso", "nocauteado"),
    "wake": (wake, 2.2, False, "Descanso", "levantando do nocaute"),
    "beg": (beg, 1.0, True, "Domado", "pedindo comida ao dono"),
    "tame": (tame, 2.0, False, "Domado", "no momento em que é domesticado"),
}
