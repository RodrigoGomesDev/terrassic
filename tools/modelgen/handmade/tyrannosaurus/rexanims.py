"""T. rex v2: the full animation set (28; ANIMS lists them with when the game plays each).
Every function maps time (s) -> pose; feet are planted by IK, lying poses are ground-fitted."""
import math
import numpy as np
import geo
from anim2 import *
import rexanim as R

S = R.S
BALL = R.REST_BALL
REST_META = {s: chain_angle(S, {}, [f"foot_{s}"]) for s in ("l", "r")}
LEG = {s: {f"{b}_{s}" for b in ("thigh", "shin", "foot", "toes")} for s in ("l", "r")}
SIDES = (("l", 0.0), ("r", 0.5))
W = lambda t, T: 2 * math.pi * t / T

def leg_low(pose, s):
    return min(q[:, 1].min() for c, q in geo.cube_points(S, pose) if c["bone"] in LEG[s])

def plant(pose, s, dy=0.0, dz=0.0, meta=0.0, toe=0.0, clear=-0.05):
    """put the ball of foot `s` at rest + (dy, dz); `clear` keeps the whole foot at least that high"""
    b = BALL[s]; target = (b[1] + dy, b[2] + dz)
    for _ in range(4):
        solve_leg(S, pose, s, target, REST_META[s] + meta, toe)
        if clear is None: break
        lo = leg_low(pose, s)
        if lo > clear - 0.02: break
        target = (target[0] + clear - lo, target[1])

def stand(pose):
    for s, _ in SIDES: plant(pose, s)
    return pose

def tail(pose, t, yaw=0.0, pitch=0.0, T=4.0, lag=0.5, amp=1.0, base_pitch=0.0):
    """tail follows with a delay growing to the tip"""
    for k in range(1, 5):
        a = amp * (0.6 + 0.35 * k)
        add(pose, f"tail{k}", rot=(base_pitch * (0.5 + 0.25 * k) + pitch * a * math.sin(W(t, T) - lag * k),
                                  yaw * a * math.sin(W(t, T) - 0.6 - lag * k), 0))

def breathe(pose, t, T=2.0, amp=1.0):
    br = math.sin(W(t, T))
    add(pose, "body", rot=(0.8 * amp * br, 0, 0), pos=(0, 0.35 * amp * br, 0))
    add(pose, "neck", rot=(-0.6 * amp * br, 0, 0)); add(pose, "skull", rot=(-0.4 * amp * br, 0, 0))
    for s, _ in SIDES: add(pose, f"arm_{s}", rot=(1.5 * amp * br, 0, 0))
    return br

def tr(*keys): return Track(keys)
def window(t, a, b, fade=0.25):
    """1 inside [a, b], easing in and out over `fade` s"""
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))

# ------------------------------------------------------------------ gaits
def gait(t, T, stride, duty, lift, bob, lean=0.0, drop=0.0, head=0.0, tail_up=0.0, sway=1.0, arms=5.0, roll=2.4):
    ph = (t / T) % 1.0; w = 2 * math.pi * ph; pose = {}
    add(pose, "body", rot=(lean + 1.2 * math.sin(2 * w - 0.4), 2.2 * sway * math.sin(w), roll * sway * math.sin(w + 0.35)),
        pos=(0, -bob * math.cos(2 * w - 0.9) - 0.6 - drop, 0))
    add(pose, "neck", rot=(head - lean * 0.6 - 1.0 * math.sin(2 * w - 0.4) + 1.4 * math.sin(2 * w - 1.6), -1.6 * sway * math.sin(w - 0.6), -1.2 * sway * math.sin(w + 0.35)))
    add(pose, "skull", rot=(head * 0.4 - lean * 0.4 + 0.9 * math.sin(2 * w - 2.1), -0.8 * sway * math.sin(w - 1.3), -1.0 * sway * math.sin(w)))
    add(pose, "jaw", rot=(-1.0 - 1.0 * math.sin(2 * w - 2.6), 0, 0))
    for k in range(1, 5):
        add(pose, f"tail{k}", rot=(tail_up * (0.4 + 0.2 * k) + 0.8 * math.sin(2 * w - 0.9 - 0.55 * k),
                                  -(1.6 + 1.1 * k) * sway * math.sin(w - 0.5 - 0.6 * k), 0.6 * math.sin(w - 0.6 * k)))
    for s, o in SIDES:
        add(pose, f"arm_{s}", rot=(arms * math.sin(w + o * 2 * math.pi - 2.0), 0, 0))
        add(pose, f"forearm_{s}", rot=(arms * 1.2 * math.sin(w + o * 2 * math.pi - 2.6), 0, 0))
    for s, o in SIDES:
        u = (ph + o) % 1.0
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0
            meta = 34 * smooth(max(0, (st - 0.55) / 0.45)); toe = 0.0; clear = -0.05
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e
            ly = lift * math.sin(math.pi * min(1, sw * 1.15)) ** 1.3
            meta = 34 * (1 - smooth(sw / 0.5)) - 18 * math.sin(math.pi * sw)
            toe = -28 * math.sin(math.pi * min(1, sw * 1.1)) + 6 * smooth((sw - 0.7) / 0.3)
            clear = 1.2 * math.sin(math.pi * sw) ** 0.5
        plant(pose, s, ly, dz - 6, meta, toe, clear)
    return pose

def walk(t): return gait(t, 1.9, 72, 0.62, 9, 1.6)
def run(t): return gait(t, 0.8, 128, 0.42, 16, 3.0, lean=6, drop=3, head=-4, tail_up=3, sway=0.6, arms=3, roll=1.2)
def stalk(t):
    p = gait(t, 2.8, 56, 0.74, 7, 0.7, lean=3, drop=7, head=-9, tail_up=1, sway=0.5, arms=2, roll=1.0)
    add(p, "skull", rot=(0, 6 * math.sin(W(t, 5.6)), 0)); add(p, "jaw", rot=(1, 0, 0))   # scans side to side, mouth shut
    return p
def swim(t):
    T = 1.6; w = W(t, T); p = {}
    add(p, "body", rot=(-4 + 1.5 * math.sin(2 * w), 3 * math.sin(w), 4 * math.sin(w + 0.4)), pos=(0, 1.5 * math.sin(2 * w), 0))
    add(p, "neck", rot=(10 - 1.5 * math.sin(2 * w + 0.5), -2 * math.sin(w - 0.5), 0)); add(p, "skull", rot=(6, -1.5 * math.sin(w - 1), 0))
    tail(p, t, yaw=6, T=T, lag=0.7)
    for s, o in SIDES:
        f = w + o * 2 * math.pi
        add(p, f"thigh_{s}", rot=(-10 + 28 * math.sin(f), 0, 0)); add(p, f"shin_{s}", rot=(-22 - 22 * math.cos(f), 0, 0))
        add(p, f"foot_{s}", rot=(30 + 20 * math.cos(f + 0.6), 0, 0)); add(p, f"toes_{s}", rot=(-25 * math.sin(f + 1.0), 0, 0))
        add(p, f"arm_{s}", rot=(-15, 0, 0))
    return p

# ------------------------------------------------------------------ idle family
idle = R.idle_pose
sniff = R.sniff_pose
def look_back(t):
    p = {}; breathe(p, t)
    k = tr((0, 0), (0.5, 0), (0.85, 1, ease_out), (2.2, 1), (2.6, 0.3), (3.2, 0))(t)
    k = float(k)
    add(p, "body", rot=(0, 9 * k, -2 * k)); add(p, "neck", rot=(4 * k, 34 * k, 0)); add(p, "skull", rot=(2 * k, 26 * k, -8 * k))
    tail(p, t, yaw=1.0, T=4, amp=0.8); [add(p, f"tail{i}", rot=(0, 5 * k * (0.5 + 0.3 * i), 0)) for i in range(1, 5)]
    return stand(p)
def shake(t):
    p = {}
    env = math.exp(-((t - 0.9) / 0.45) ** 2)
    for bone, a, d in (("skull", 14, 0.0), ("neck", 10, 0.05), ("body", 4, 0.12)):
        add(p, bone, rot=(0, a * 0.4 * env * math.sin(2 * math.pi * 5.5 * (t - d)), a * env * math.sin(2 * math.pi * 5.5 * (t - d))))
    for k in range(1, 5):
        d = 0.12 + 0.06 * k
        add(p, f"tail{k}", rot=(0, (2 + 2 * k) * math.exp(-((t - 0.9 - d) / 0.45) ** 2) * math.sin(2 * math.pi * 5.5 * (t - d)), 0))
    add(p, "jaw", rot=(-6 * env, 0, 0)); add(p, "neck", rot=(6 * window(t, 0.3, 1.5), 0, 0))
    return stand(p)
def yawn(t):
    p = {}; breathe(p, t, amp=0.6)
    up = float(tr((0, 0), (0.6, 1), (1.9, 1), (2.3, 0.2), (3.0, 0))(t))
    add(p, "neck", rot=(14 * up, 0, 0)); add(p, "skull", rot=(10 * up, 0, -4 * up))
    jaw = float(tr((0, 0), (0.4, -6), (1.3, -52, ease_out), (1.8, -50), (2.0, -2, ease_in), (3.0, 0))(t))
    add(p, "jaw", rot=(jaw + 1.0 * math.sin(2 * math.pi * 7 * t) * window(t, 1.2, 1.8, 0.1), 0, 0))
    add(p, "skull", rot=(0, 0, 5 * math.sin(2 * math.pi * 4 * t) * window(t, 2.1, 2.6, 0.12)))
    for s, _ in SIDES: add(p, f"arm_{s}", rot=(-10 * up, 0, 0)); add(p, f"forearm_{s}", rot=(14 * up, 0, 0))
    tail(p, t, yaw=0.6, T=4)
    return stand(p)
def stretch(t):
    p = {}
    k = float(tr((0, 0), (0.8, 1), (1.8, 1), (2.4, -0.4), (3.0, -0.4), (3.6, 0))(t))
    a = max(0, k); b = max(0, -k) / 0.4
    add(p, "body", rot=(-7 * a + 4 * b, 0, 0), pos=(0, -2 * a, 3 * a))
    add(p, "neck", rot=(-10 * a + 10 * b, 0, 0)); add(p, "skull", rot=(-8 * a + 6 * b, 0, 0))
    for i in range(1, 5): add(p, f"tail{i}", rot=(6 * a * (0.5 + 0.2 * i) - 3 * b, 0, 0))
    add(p, "jaw", rot=(-10 * b, 0, 0))
    for s, _ in SIDES: add(p, f"arm_{s}", rot=(-25 * a, 0, 0)); add(p, f"forearm_{s}", rot=(30 * a, 0, 0))
    return stand(p)

# ------------------------------------------------------------------ voice and display
roar = R.roar_pose
def call(t):
    """closed-mouth rumble: chin tucked, chest pushed out, the whole body hums"""
    p = {}; k = float(tr((0, 0), (0.5, 1), (2.0, 1), (2.6, 0))(t))
    hum = 0.9 * math.sin(2 * math.pi * 11 * t) * window(t, 0.5, 2.0, 0.15)
    add(p, "body", rot=(3 * k + hum * 0.5, 0, 0), pos=(0, 1.0 * k, 0))
    add(p, "neck", rot=(-10 * k + hum, 0, 0)); add(p, "skull", rot=(-14 * k - hum, 0, 0)); add(p, "jaw", rot=(1, 0, 0))
    tail(p, t, yaw=0.5, T=3, base_pitch=-2 * k)
    return stand(p)
def threat(t):
    """head low toward the target, mouth half open, one heavy stomp"""
    p = {}
    k = float(tr((0, 0), (0.4, 1), (2.0, 1), (2.4, 0))(t))
    stomp = float(tr((0, 0), (0.5, 0), (0.9, 1, ease_out), (1.05, 0, ease_in), (2.4, 0))(t))
    jolt = math.exp(-((t - 1.08) / 0.07) ** 2)
    add(p, "body", rot=(5 * k + 2 * jolt, 0, -2 * stomp), pos=(0, -3 * k - 1.2 * jolt, 0))
    add(p, "neck", rot=(-8 * k, 0, 0)); add(p, "skull", rot=(-4 * k + 3 * jolt, 0, 0))
    add(p, "jaw", rot=(-12 * k - 6 * jolt, 0, 0))
    tail(p, t, yaw=2.5 * k, T=0.9, base_pitch=3 * k)
    plant(p, "r"); plant(p, "l", 13 * stomp, -6 * stomp, 0, -10 * stomp, clear=-0.05)
    return p

def roar_loud(t):
    """the big roar: crouch and inhale, rear up with the snout to the sky, roar long with the throat shaking, settle"""
    p = {}
    up = float(tr((0, 0), (0.55, -0.35), (1.15, 1, ease_out), (3.0, 1), (3.9, 0, back_out), (4.4, 0))(t))
    a = max(0.0, up); c = max(0.0, -up) / 0.35
    vib = math.sin(2 * math.pi * 10 * t) * window(t, 1.15, 3.0, 0.15)
    sway = math.sin(2 * math.pi * (t - 1.15) / 1.85) * window(t, 1.15, 3.0, 0.3)
    add(p, "body", rot=(-14 * a + 6 * c + 0.6 * vib, 2 * sway, 0), pos=(0, -3 * c + 1.0 * a, 2.0 * a))
    add(p, "neck", rot=(46 * a - 12 * c + 1.2 * vib, 6 * sway, -2 * sway))
    add(p, "skull", rot=(30 * a - 8 * c + 1.5 * vib, 4 * sway, -3 * sway))
    jaw = float(tr((0, 0), (0.55, -3), (0.9, -8), (1.25, -40, ease_out), (2.9, -37), (3.25, -2, ease_in), (4.4, 0))(t))
    add(p, "jaw", rot=(jaw - 1.5 * vib, 0, 0))
    for i in range(1, 5):
        lag = max(0.0, t - 0.07 * i)
        ua = max(0.0, float(tr((0, 0), (0.55, -0.35), (1.15, 1, ease_out), (3.0, 1), (3.9, 0, back_out), (4.4, 0))(lag)))
        add(p, f"tail{i}", rot=(2.5 * ua * (0.5 + 0.25 * i) + 2 * c, 1.5 * i * sway * 0.5, 0))
    for s, _ in SIDES:
        add(p, f"arm_{s}", rot=(-20 * a, 0, 0)); add(p, f"forearm_{s}", rot=(-15 * a + 1.5 * vib, 0, 0))
    return stand(p)

# ------------------------------------------------------------------ combat
attack = R.bite_pose
def attack_quick(t):
    p = {}
    n = tr((0, (0, 0)), (0.15, (8, 4), ease_out), (0.27, (-14, 0), ease_in), (0.5, (-10, 0)), (0.9, (0, 0)))(t)
    j = float(tr((0, 0), (0.15, -32, ease_out), (0.27, -3, ease_in), (0.9, 0))(t))
    add(p, "body", rot=(3 * smooth((t - 0.15) / 0.12) * (1 - smooth((t - 0.5) / 0.4)), 0, 0), pos=(0, 0, -4 * smooth((t - 0.15) / 0.12) * (1 - smooth((t - 0.5) / 0.4))))
    add(p, "neck", rot=(n[0], n[1], 0)); add(p, "skull", rot=(n[0] * 0.6, n[1] * 0.5, 0)); add(p, "jaw", rot=(j, 0, 0))
    tail(p, t, yaw=1.5, T=0.9, lag=0.4)
    return stand(p)
def stomp(t):
    p = {}
    k = float(tr((0, 0), (0.55, 1, ease_out), (0.75, 1), (0.88, 0, ease_in), (1.6, 0))(t))
    jolt = math.exp(-((t - 0.9) / 0.08) ** 2)
    add(p, "body", rot=(-4 * k + 3 * jolt, 0, 4 * k), pos=(0, 2 * k - 2 * jolt, 0))
    add(p, "neck", rot=(-6 * k - 4 * jolt, -6 * k, 0)); add(p, "skull", rot=(-6 * k, -4 * k, 0)); add(p, "jaw", rot=(-8 * jolt, 0, 0))
    tail(p, t, yaw=1.0, T=1.6, base_pitch=5 * k)
    plant(p, "l"); plant(p, "r", 22 * k, -12 * k, -10 * k, -12 * k, clear=-0.05)
    return p
def hurt(t):
    p = {}; e = math.exp(-(t / 0.16)) * smooth(t / 0.04)
    add(p, "body", rot=(-6 * e, 6 * e, -4 * e), pos=(0, -1.5 * e, 3 * e))
    add(p, "neck", rot=(12 * e, -8 * e, 0)); add(p, "skull", rot=(8 * e, -6 * e, 6 * e)); add(p, "jaw", rot=(-22 * e, 0, 0))
    for k in range(1, 5):
        d = 0.04 * k; ek = math.exp(-max(0, t - d) / 0.2) * smooth((t - d) / 0.05)
        add(p, f"tail{k}", rot=(4 * ek, -6 * ek * k * 0.6, 0))
    return stand(p)

# ------------------------------------------------------------------ eating and drinking
def eat(t):
    """head down to the carcass, bite, tear back with a twist, gulp twice"""
    p = {}
    down = float(tr((0, 0), (0.6, 1), (1.4, 1), (1.7, 0.45, ease_out), (2.6, 0.45), (3.2, 0))(t))
    twist = float(tr((0, 0), (1.35, 0), (1.55, 1, ease_out), (1.9, -0.4), (2.2, 0))(t))
    add(p, "body", rot=(-8 * down, 0, 0), pos=(0, -3 * down, 0))
    add(p, "neck", rot=(-34 * down, 16 * twist, 0)); add(p, "skull", rot=(-20 * down, 8 * twist, -12 * twist))
    j = float(tr((0, 0), (0.6, -30), (0.9, -32), (1.05, -3, ease_in), (1.9, -3), (2.1, -12), (2.3, -2), (2.5, -12), (2.7, -2), (3.2, 0))(t))
    add(p, "jaw", rot=(j, 0, 0))
    gulp = math.exp(-((t - 2.75) / 0.1) ** 2)
    add(p, "skull", rot=(8 * gulp, 0, 0))
    tail(p, t, yaw=0.8, T=3.2, base_pitch=6 * down)
    return stand(p)
def drink(t):
    p = {}
    down = float(tr((0, 0), (0.9, 1), (3.0, 1), (3.7, 0), (4.0, 0))(t))
    add(p, "body", rot=(-12 * down, 0, 0), pos=(0, -5 * down, 2 * down))
    add(p, "neck", rot=(-31 * down, 0, 0)); add(p, "skull", rot=(-10 * down, 0, 0))
    lap = window(t, 1.1, 2.8, 0.15)
    add(p, "jaw", rot=(-6 * lap * (0.5 + 0.5 * math.sin(2 * math.pi * 2.5 * t)), 0, 0))
    add(p, "skull", rot=(3 * lap * math.sin(2 * math.pi * 2.5 * t - 0.6), 0, 0))
    gulp = math.exp(-((t - 3.75) / 0.1) ** 2); add(p, "skull", rot=(10 * gulp, 0, 0))
    tail(p, t, yaw=0.6, T=4, base_pitch=8 * down)
    for s, _ in SIDES: add(p, f"arm_{s}", rot=(10 * down, 0, 0))
    return stand(p)

# ------------------------------------------------------------------ resting
LIE = 28.0                 # how far the body drops to rest on the belly
def lie(p, k, head_down=0.0, breath=1.0, t=0.0):
    """k = 0 standing .. 1 lying on the belly with the legs folded"""
    add(p, "body", rot=(2 * k, 0, 0), pos=(0, -LIE * k, 0))
    add(p, "neck", rot=(-6 * k - 30 * head_down, 0, 0)); add(p, "skull", rot=(4 * k - 4 * head_down, 0, 0))
    for i in range(1, 5): add(p, f"tail{i}", rot=(-7 * k * (0.3 + 0.25 * i) + 4 * k * (i == 1), 0, 0))
    for s, _ in SIDES:
        add(p, f"arm_{s}", rot=(-15 * k, 0, 0)); add(p, f"forearm_{s}", rot=(20 * k, 0, 0))
        b = BALL[s]
        # the metatarsus ends flat on the ground with the ankle behind the toes, like resting birds
        solve_leg2(S, p, s, (b[1] + 0.5 * k, b[2] - 6 * k), (15.9 - 11.5 * k, 6.2 + 9 * k), w_ankle=0.8 * k + 0.05)
    return p
def sit(t):
    p = {}; br = math.sin(W(t, 3.0))
    lie(p, 1.0); add(p, "body", rot=(0.8 * br, 0, 0)); add(p, "neck", rot=(-0.6 * br + 2 * math.sin(W(t, 6.0)), 3 * math.sin(W(t, 6.0) - 1), 0))
    tail(p, t, yaw=0.5, T=6)
    return ground_fit(S, p)
def sleep(t):
    p = {}; br = math.sin(W(t, 4.0))
    lie(p, 1.0, head_down=1.0)
    add(p, "body", rot=(1.0 * br, 0, 0), pos=(0, 0.4 * br, 0)); add(p, "neck", rot=(-0.8 * br, 0, 0))
    add(p, "jaw", rot=(-1.5 * max(0, br), 0, 0))
    return ground_fit(S, p)
def wake_sleep(t):
    """from sleep: lift the head, blink awake, push up, shake it off"""
    p = {}
    hd = float(tr((0, 1), (0.6, 0, ease_out), (2.4, 0))(t))
    up = float(tr((0, 1), (0.8, 1), (1.7, 0, back_out), (2.4, 0))(t))
    lie(p, up, head_down=hd)
    env = math.exp(-((t - 2.0) / 0.18) ** 2)
    add(p, "skull", rot=(0, 4 * env * math.sin(2 * math.pi * 6 * t), 10 * env * math.sin(2 * math.pi * 6 * t)))
    p = ground_fit(S, p)
    return p
def wake(t):
    """the game plays this when a knockout ends: roll from the side onto the belly, shake the head, stand up"""
    p = {}
    roll = float(tr((0, 80), (0.3, 80), (0.9, 0, ease_out), (3.0, 0))(t))
    k = float(tr((0, 0.8), (0.9, 1.0), (1.5, 1.0), (2.4, 0, back_out), (3.0, 0))(t))
    hd = float(tr((0, 0.6), (0.9, 0.4), (1.3, 0, ease_out), (3.0, 0))(t))
    lie(p, k, head_down=hd)
    add(p, "root", rot=(0, 0, roll))
    side = roll / 80.0
    add(p, "neck", rot=(-4 * side, 0, -14 * side)); add(p, "skull", rot=(-6 * side, 0, -10 * side)); add(p, "jaw", rot=(-9 * side, 0, 0))
    env = math.exp(-((t - 1.2) / 0.2) ** 2)
    add(p, "skull", rot=(0, 5 * env * math.sin(2 * math.pi * 6 * t), 12 * env * math.sin(2 * math.pi * 6 * t)))
    return ground_fit(S, p)
def knocked_out(t):
    """out cold on its side, slow breathing, the jaw slack"""
    p = {}; br = math.sin(W(t, 4.0))
    lie(p, 0.8)
    add(p, "root", rot=(0, 0, 80))
    add(p, "body", rot=(0.8 * br, 0, 0)); add(p, "neck", rot=(-4, 0, -14)); add(p, "skull", rot=(-6, 0, -10)); add(p, "jaw", rot=(-9 - 1.5 * br, 0, 0))
    for i in range(1, 5): add(p, f"tail{i}", rot=(0, 0, -3))
    for s, _ in SIDES: add(p, f"arm_{s}", rot=(20, 0, 0))
    add(p, "thigh_r", rot=(18, 0, 0)); add(p, "shin_r", rot=(10, 0, 0))
    return ground_fit(S, p)
def death(t):
    """stagger, legs give, roll onto the side, last breath"""
    p = {}
    g = float(tr((0, 0), (0.5, 0.15), (1.1, 0.8, ease_in), (3.0, 0.8))(t))
    rl = float(tr((0, 0), (0.7, -6), (1.15, 84, ease_in), (1.3, 77), (1.45, 81), (3.0, 80))(t))
    lie(p, g)
    add(p, "root", rot=(0, 0, rl))
    sway = math.sin(2 * math.pi * 1.2 * t) * (1 - smooth((t - 0.8) / 0.3))
    add(p, "body", rot=(0, 4 * sway, 0)); add(p, "neck", rot=(6 * window(t, 0, 0.9) - 6 * smooth((t - 1.1) / 0.3), -6 * sway, -14 * smooth((t - 1.1) / 0.3)))
    add(p, "skull", rot=(-6 * smooth((t - 1.1) / 0.3), 0, -10 * smooth((t - 1.1) / 0.3)))
    add(p, "jaw", rot=(-18 * window(t, 0.2, 1.0) - 9 * smooth((t - 1.2) / 0.4), 0, 0))
    for s, _ in SIDES: add(p, f"arm_{s}", rot=(20 * smooth((t - 1.0) / 0.3), 0, 0))
    return ground_fit(S, p)

# ------------------------------------------------------------------ tamed
def beg(t):
    """eager: looks up at the player, shifts from foot to foot, snaps the jaw softly"""
    T = 2.0; w = W(t, T); p = {}
    add(p, "body", rot=(-3, 3 * math.sin(w), 2 * math.sin(w)), pos=(0, 0.6 * abs(math.sin(w)), 0))
    add(p, "neck", rot=(12 + 3 * math.sin(2 * w), 4 * math.sin(w - 0.5), 0)); add(p, "skull", rot=(10 + 3 * math.sin(2 * w - 0.6), 0, 8 * math.sin(w - 1)))
    add(p, "jaw", rot=(-6 * max(0, math.sin(2 * w)), 0, 0))
    tail(p, t, yaw=4, T=T / 2, lag=0.5)
    for s, o in SIDES:
        f = w + o * 2 * math.pi
        plant(p, s, 5 * max(0, math.sin(f)) ** 2, 0, 0, -6 * max(0, math.sin(f)), clear=-0.05)
    return p
def tame(t):
    """the moment it accepts you: head toss, rumbling call, tail wag"""
    p = {}
    k = float(tr((0, 0), (0.4, 1, ease_out), (1.6, 1), (2.4, 0))(t))
    toss = math.exp(-((t - 0.5) / 0.15) ** 2)
    add(p, "body", rot=(-4 * k, 0, 0), pos=(0, 1.0 * toss, 0))
    add(p, "neck", rot=(16 * k + 8 * toss, 0, 0)); add(p, "skull", rot=(12 * k, 0, 10 * math.sin(2 * math.pi * 1.5 * t) * k))
    hum = 0.8 * math.sin(2 * math.pi * 11 * t) * window(t, 0.8, 1.6, 0.12)
    add(p, "jaw", rot=(-16 * toss - 4 * k + hum, 0, 0))
    tail(p, t, yaw=6 * k, T=0.8, lag=0.5)
    return stand(p)

# name: (fn, length, loop, category, when it plays)
ANIMS = {
    "idle": (idle, 8.0, True, "Parado", "base, sempre que está parado"),
    "sniff": (sniff, 3.0, False, "Parado", "gesto sorteado parado"),
    "look_back": (look_back, 3.2, False, "Parado", "gesto sorteado parado"),
    "shake": (shake, 2.0, False, "Parado", "gesto sorteado parado; ao sair da água"),
    "yawn": (yawn, 3.0, False, "Parado", "gesto sorteado parado, mais à noite"),
    "stretch": (stretch, 3.6, False, "Parado", "gesto sorteado parado; depois de acordar"),
    "walk": (walk, 1.9, True, "Movimento", "andando"),
    "run": (run, 0.8, True, "Movimento", "correndo, caçando ou fugindo"),
    "stalk": (stalk, 2.8, True, "Movimento", "chegando perto da presa antes do ataque"),
    "swim": (swim, 1.6, True, "Movimento", "dentro da água"),
    "roar": (roar, 3.4, False, "Voz", "ao ver o alvo; domado, sob comando"),
    "roar_loud": (roar_loud, 4.4, False, "Voz", "rugido alto, raro: depois de abater presa grande, quando outro T. rex chega perto, ou sob comando do dono; o único com a onda no ar"),
    "call": (call, 2.6, False, "Voz", "ronco grave de vez em quando, chamando outros"),
    "threat": (threat, 2.4, False, "Voz", "aviso antes de atacar quem chega perto"),
    "attack": (attack, 2.0, False, "Combate", "mordida forte e sacudida"),
    "attack_quick": (attack_quick, 0.9, False, "Combate", "mordida rápida, alternando com a forte"),
    "stomp": (stomp, 1.6, False, "Combate", "pisão em alvo pequeno perto dos pés"),
    "hurt": (hurt, 0.6, False, "Combate", "ao levar dano"),
    "death": (death, 3.0, False, "Combate", "ao morrer"),
    "eat": (eat, 3.2, False, "Comer", "comendo carne ou carcaça"),
    "drink": (drink, 4.0, False, "Comer", "bebendo na beira da água"),
    "sit": (sit, 6.0, True, "Descanso", "sentado (domado) ou descansando"),
    "sleep": (sleep, 8.0, True, "Descanso", "dormindo"),
    "wake": (wake, 3.0, False, "Descanso", "ao acordar do nocaute (o jogo já chama)"),
    "wake_sleep": (wake_sleep, 2.4, False, "Descanso", "ao acordar de um sono normal"),
    "knocked_out": (knocked_out, 4.0, True, "Descanso", "nocauteado (domesticação)"),
    "beg": (beg, 2.0, True, "Domado", "pedindo comida ao dono"),
    "tame": (tame, 2.4, False, "Domado", "no momento em que é domesticado"),
}
