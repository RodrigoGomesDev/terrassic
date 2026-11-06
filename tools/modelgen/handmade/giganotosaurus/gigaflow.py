"""Giganotosaurus: the fluid set and its fighting moves (06/11/2026). Rodrigo: "quase um jogo de luta entre dinos, cada
um com sua animacao unica e fluida, lembrando que tem que ter um estudo por tras sempre".

Two studies behind it:
  * docs/estudos/08_ANIMACAO_RAXIORES.md, the rules of fluid motion: nothing stops (breath under every one-shot),
    nothing switches on or off (envelopes), three beats per action with a settle that passes the rest a little, the
    tail follows late, tremors are sums of sines that never line up, loop periods divide the loop;
  * docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md, its row: blade teeth for cutting (Coria & Currie 2006); the
    carcharodontosaurids wounded and waited for the prey to bleed. It cuts and backs off, circles, waits: heavy,
    patient, few feints. Its own study adds: the eyes look sideways from under a bony eave (it aims with ONE eye, the
    head turned on its side), the head is carried low in line with the back, the whole long tail bends (no stiff half).

What makes it itself here, against the T. rex and the Carnotaurus:
  * the heaviest gait of the three: a deep hip roll and a slow, wide tail whip that runs to the tip of the whole tail,
    a long heavy drop after each heel strike, the head steady and low;
  * every look and every aim is the one-eyed tilt; it never snaps (the Carnotaurus) and never rears (the T. rex);
  * slow cycles everywhere: the guard breathes over 3.2 s, the sidestep takes 2 s, the turn 2 s;
  * the fight: a long sideways `slash` that drags the blades across, and `grab_shake` (lift a smaller animal and shake
    it like a shark), against the T. rex's crushing bite and the Carnotaurus's horns.
"""
import math

import gigaanims as A
from anim2 import add, smooth, ease_in, ease_out, back_out, lowest
from theropod import window, SIDES
import giga

S, T = A.S, A.T
TAILS, BEND = A.TAILS, A.BEND
tr = A.tr
arms, jaw, eye, tail = A.arms, A.jaw, A.eye, A.tail
fold, ground_fit = A.fold, A.ground_fit

WHIP = (0.6, 0.95, 1.3, 1.65, 1.95)       # a follow-through grows down the long tail (BEND already thins the tip bone)


# ------------------------------------------------------------------ helpers (the ideas of rexflow, on this rig)
def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def tremor(t, f=(6.1, 9.7, 3.9), amp=(1.0, 0.55, 0.4), phase=0.0):
    """an organic shiver, lower than the others' (a bigger throat): three sines that never line up"""
    return sum(a * math.sin(2 * math.pi * fr * t + phase * (i + 1) + 1.3 * i) for i, (fr, a) in enumerate(zip(f, amp)))


def trail(p, t, fn, gain=WHIP, delay=0.09, axis=1, loop=None):
    """follow-through down the whole tail: bone k takes fn(t - (k+1)*delay) * gain[k] * BEND[k]"""
    for k, b in enumerate(TAILS):
        u = t - delay * (k + 1)
        v = fn(u % loop if loop else max(0.0, u)) * gain[k] * BEND[k]
        r = [0.0, 0.0, 0.0]; r[axis] = v
        add(p, b, rot=tuple(r))


def alive(p, t, k=1.0, period=3.4):
    """the slow, deep breathing layer under every one-shot (before the feet are planted: it moves the body)"""
    br = wave(t, period)
    add(p, "body", rot=(0.7 * k * br, 0, 0), pos=(0, 0.5 * k * br, 0))
    alive_upper(p, t, k, period)
    return br


def alive_upper(p, t, k=1.0, period=3.4, slow=None):
    s1, s2 = (slow, slow) if slow else (period * 1.4, period * 2)
    T.neck(p, (-0.5 * k * wave(t, period, -0.5), 0, 0))
    add(p, "skull", rot=(-0.3 * k * wave(t, period, -1.0), 0, 0))
    jaw(p, -0.6 * k * max(0.0, wave(t, period, -0.6)))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(1.3 * k * wave(t, period, -0.8 - o), 0, 0))
        add(p, f"forearm_{s}", rot=(1.4 * k * wave(t, s1, -1.4 - o), 0, 0))
    for i, (b, g) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(0.35 * k * (i + 1) * g * wave(t, period, -0.45 * i), 0.8 * k * (i + 1) * g * wave(t, s2, -0.6 * i), 0))


def bump(t, c, w):
    return math.exp(-((t - c) / w) ** 2)


def decay(t, at, tau, f):
    return math.exp(-max(0.0, t - at) / tau) * math.sin(2 * math.pi * f * (t - at)) * smooth((t - at + 0.02) / 0.05)


def arch(t, a, b, h):
    u = min(1.0, max(0.0, (t - a) / (b - a)))
    return h * math.sin(math.pi * u) ** 1.3


# ------------------------------------------------------------------ the heavy gait
def landing(x):
    """-1 just after a heel strike, +1 mid-stance: a 6 t body lands hard and is pushed up slowly"""
    x %= 1.0
    return -1.0 + 2.0 * smooth(x / 0.32) if x < 0.32 else 1.0 - 2.0 * smooth((x - 0.32) / 0.68)


def gait2(t, Tc, stride, duty, lift, bob, lean=0.0, drop=0.0, head=0.0, roll=7.0, yaw=4.5, whip=1.0, splay=2.5,
          still=0.9, back=False, arm_amp=2.5, tail_up=0.0):
    ph = (t / Tc) % 1.0
    if back:
        ph = 1.0 - ph
    w = 2 * math.pi * ph; p = {}
    b2 = landing(2 * ph + 0.05)
    hroll = roll * math.sin(w + 0.3)
    hyaw = yaw * math.sin(w - 0.6)
    add(p, "body", rot=(lean + 0.9 * b2, hyaw, hroll), pos=(0, bob * b2 - 0.6 - drop, 0))
    T.neck(p, (head - lean * still - 0.9 * still * landing(2 * ph - 0.05), -0.9 * hyaw - 1.0 * math.sin(w - 1.5),
               -0.8 * hroll))
    add(p, "skull", rot=(-head * 0.3 + 0.8 * landing(2 * ph - 0.15), -0.1 * hyaw + 0.8 * math.sin(w - 2.1),
                         -0.2 * hroll + 1.0 * math.sin(w - 1.3)))
    jaw(p, -1.0 - 1.0 * max(0.0, landing(2 * ph - 0.25)))
    for k, (b, g) in enumerate(zip(TAILS, BEND)):       # the long whip: wider and later at every bone
        lag = 0.75 * (k + 1)
        add(p, b, rot=(tail_up * g - 0.8 * g * (0.6 + 0.3 * k) * landing(2 * ph - 0.09 * (k + 1)),
                       -2.4 * whip * g * (1.0 + 0.55 * k) * math.sin(w - 0.7 - lag), 0.5 * whip * g * math.sin(w - 0.4 - lag)))
    for s, o in SIDES:
        f = w + o * 2 * math.pi
        add(p, f"arm_{s}", rot=(arm_amp * math.sin(f - 2.3) + 1.5 * landing(2 * ph - 0.3), 0, 0))
        add(p, f"forearm_{s}", rot=(arm_amp * math.sin(f - 3.0) + 1.8 * landing(2 * ph - 0.4), 0, 0))
    for s, o in SIDES:
        sx = 1 if s == "l" else -1
        u = (ph + o) % 1.0
        swing = 0.0 if u < duty else math.sin(math.pi * (u - duty) / (1 - duty))
        add(p, f"thigh_{s}", rot=(0, -hyaw, -hroll + sx * splay * swing))
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0
            meta = 30 * smooth(max(0, (st - 0.55) / 0.45)); clear = -0.05
            toe = 6 * (1 - smooth(min(1.0, st / 0.2))) + 8 * smooth(max(0, (st - 0.72) / 0.28))
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e
            ly = lift * math.sin(math.pi * min(1, sw * 1.1)) ** 1.2
            meta = 30 * (1 - smooth(sw / 0.45)) - 20 * math.sin(math.pi * sw)
            toe = -26 * math.sin(math.pi * min(1, sw * 1.1)) + 6 * smooth((sw - 0.7) / 0.3)
            clear = -0.05 + 1.0 * math.sin(math.pi * sw) ** 0.5     # meets the stance value at both ends
        T.plant(p, s, ly, dz - 3, meta, toe, clear)
    return p


WALK, MARCH = A.WALK, A.MARCH        # lengths and strides stay (Giganotosaurine WALK_PX / RUN_PX ...)


def walk(t):
    return gait2(t, *WALK)


def run(t):
    """the forced march: one foot always down, the body leaning into it, the hips still rolling, the head low and steady"""
    p = gait2(t, *MARCH, lean=5, drop=2.5, head=-5, roll=4.5, yaw=3.0, whip=0.75, still=0.95, arm_amp=1.5)
    arms(p, -10, 8)
    return p


def stalk(t):
    Tw, st, du, li, bo = WALK
    return gait2(t, Tw * 1.5, st * 0.7, 0.72, li * 0.7, bo * 0.4, lean=3, drop=6, head=-9, roll=3.0, yaw=2.0, whip=0.5,
                 still=1.0, arm_amp=1.0)


def back_off(t):
    """after the cut: short heavy steps backwards, the head low and on the target, the jaws a little open"""
    Tw, st, du, li, bo = WALK
    p = gait2(t, 1.6, 44, 0.66, li * 0.8, bo * 0.6, lean=-2, drop=1, head=-6, roll=3.5, yaw=2.0, whip=0.6, still=1.0,
              back=True, arm_amp=1.0)
    jaw(p, -4 - 1.5 * max(0.0, wave(t, 0.8)))
    return p


def circle(t):
    """walking sideways round the prey: the body turned in toward it, the head turned further and on its side to watch
    with one eye, the long tail swung out wide"""
    Tc = 1.8
    p = gait2(t, Tc, 26, 0.64, 8, 0.8, drop=2, head=-4, roll=3.0, yaw=1.5, whip=1.3, still=1.0, arm_amp=1.0)
    add(p, "body", rot=(0, 14, 0))
    eye(p, 0.8 + 0.08 * wave(t, Tc, 0.5), 1.0, low=4); T.neck(p, (0, 14, 0))
    w = 2 * math.pi * t / Tc
    for s in ("l", "r"):
        add(p, f"thigh_{s}", rot=(0, 0, 5 * math.sin(w + (0 if s == "l" else math.pi))))
    tail(p, yaw=-8)
    lo = lowest(S, p, skip_mats=("teeth", "teeth_lo") + giga.SADDLE_MATS)
    if lo < 0:
        add(p, "root", pos=(0, -lo, 0))
    return p


# ------------------------------------------------------------------ idle: 8 s, slow, low, the one-eyed look
IDLE_T = 8.0
EYE_A = tr((0, 0), (1.6, 0), (2.3, 1, ease_out), (3.9, 1), (4.6, 0, smooth), (8.0, 0))
EYE_B = tr((0, 0), (5.2, 0), (5.8, 1, ease_out), (6.7, 1), (7.4, 0, smooth), (8.0, 0))


def idle(t):
    p = {}
    L = IDLE_T
    br = wave(t, L / 2)                                       # one deep, slow breath every 4 s
    shift = wave(t, L, 0.9) + 0.25 * wave(t, L / 2, 0.2)
    hroll = 2.0 + 2.6 * shift
    hyaw = 1.2 - 1.0 * shift
    add(p, "body", rot=(0.8 * br, hyaw, hroll), pos=(0, 0.5 * br - 0.15 * shift * shift, 0))
    a, b = float(EYE_A(t)), float(EYE_B(t))
    T.neck(p, (-0.6 * wave(t, L / 2, -0.5) + 0.8 * wave(t, L / 3, 1.0), -0.8 * hyaw + 1.2 * wave(t, L / 3, 0.2), -0.75 * hroll))
    eye(p, a, 1.0); eye(p, 0.6 * b, -1.0)
    add(p, "skull", rot=(-0.4 * wave(t, L / 2, -1.0), 0, -0.2 * hroll))
    jaw(p, -0.8 - 1.4 * smooth(max(0.0, wave(t, L / 2, -0.9))))
    for i, (bn, g) in enumerate(zip(TAILS, BEND)):            # a slow S from the root to the tip, then back
        add(p, bn, rot=(0.4 * (i + 1) * g * wave(t, L / 2, -0.5 * i) - 0.3,
                        g * ((1.0 + 0.8 * i) * wave(t, L, -0.8 * i) + 0.5 * (i + 1) * wave(t, L / 3, 0.4 - 0.7 * i)), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(1.6 * wave(t, L / 2, -1.0 - 3 * o), 0, 0))
        add(p, f"forearm_{s}", rot=(2.0 * wave(t, L / 2, -1.6 - 3 * o) + 0.8 * br, 0, 0))
        add(p, f"thigh_{s}", rot=(0, -hyaw, -hroll))
    T.plant(p, "l", 0.0, -2.5)
    T.plant(p, "r")
    return p


# ------------------------------------------------------------------ voice (low and forward, never at the sky)
ROAR_T = 3.4
ROAR_K = tr((0, 0), (0.45, -0.35, ease_out), (0.85, 1.0, ease_out), (2.6, 0.9), (3.0, 0.1, ease_in), (3.4, 0.0))
ROAR_JAW = tr((0, 0), (0.45, -3), (0.6, -8, ease_out), (0.9, -38, ease_out), (1.18, -31), (1.45, -43), (1.75, -35), (2.05, -46),
              (2.33, -37), (2.6, -41), (3.0, -5), (3.4, 0, ease_out))
ROAR_SWEEP = tr((0, 0), (0.85, 0), (1.6, 8, ease_out), (2.4, -7), (2.8, -2), (3.4, 0))


def roar(t):
    p = {}
    k = float(ROAR_K(t)); a = max(0.0, k); c = max(0.0, -k) / 0.35
    sw = float(ROAR_SWEEP(t))
    env = window(t, 0.85, 2.65, 0.25)
    shiv = tremor(t) * env
    shk = decay(t, 2.65, 0.28, 2.3)                          # a slow, heavy shake of the long head at the end
    add(p, "body", rot=(2 * a - 3 * c + 0.3 * shiv, 0.2 * sw, 0.2 * sw), pos=(0, -1.5 * a - 1.5 * c, -3 * a + 2 * c))
    T.neck(p, (-6 * a + 7 * c + 0.7 * shiv, 0.5 * sw + 4 * shk, -0.2 * sw))
    add(p, "skull", rot=(4 * a - 2 * c + 1.0 * tremor(t, (7.3, 10.9, 4.6), phase=0.7) * env, 0.4 * sw + 4 * shk, -0.4 * sw - 6 * shk))
    jaw(p, float(ROAR_JAW(t)) - 1.6 * tremor(t, (8.1, 11.7, 5.3), phase=1.9) * env)
    trail(p, t, lambda u: -2.5 * max(0.0, float(ROAR_K(u))) + 1.5 * max(0.0, -float(ROAR_K(u))) / 0.35, axis=0)
    trail(p, t, lambda u: -0.5 * float(ROAR_SWEEP(u)) - 3.0 * decay(u, 2.65, 0.3, 2.3))
    arms(p, -8 * a + 1.2 * shiv, 6 * a + 1.2 * shiv)
    alive(p, t, k=1.0 - 0.8 * smooth((t - 0.4) / 0.4) * (1 - smooth((t - 2.8) / 0.5)))
    return T.stand(p)


LOUD_K = tr((0, 0), (0.6, -0.4, ease_out), (1.1, 1.0, ease_out), (3.5, 0.92), (4.0, 0.1, ease_in), (4.4, 0.0))
LOUD_JAW = tr((0, 0), (0.6, -4), (0.8, -10, ease_out), (1.15, -46, ease_out), (1.5, -38), (1.85, -52), (2.2, -42), (2.55, -54),
              (2.9, -44), (3.25, -50), (3.7, -6), (4.4, 0, ease_out))


def roar_loud(t):
    """the big one: a heavy step forward, the whole body thrown behind the low, stretched head, roaring in bellows"""
    p = {}
    k = float(LOUD_K(t)); a = max(0.0, k); c = max(0.0, -k) / 0.4
    env = window(t, 1.1, 3.55, 0.3)
    shiv = tremor(t, (5.6, 8.9, 3.6), (1.0, 0.6, 0.45)) * env
    pulse = sum(bump(t, cc, 0.16) for cc in (1.5, 2.2, 2.9))
    shk = decay(t, 3.55, 0.3, 2.1)
    add(p, "body", rot=(3 * a - 3 * c + 1.0 * pulse + 0.4 * shiv, 0, 0), pos=(0, -2.5 * a - 1.5 * c, -6 * a + 3 * c))
    T.neck(p, (-10 * a + 8 * c - 2 * pulse + 0.9 * shiv, 5 * shk, 0))
    add(p, "skull", rot=(6 * a + 1.3 * tremor(t, (7.0, 10.3, 4.4), phase=0.9) * env, 4 * shk, -7 * shk))
    jaw(p, float(LOUD_JAW(t)) - 2.0 * tremor(t, (7.9, 11.3, 5.1), phase=2.3) * env)
    trail(p, t, lambda u: -4.0 * max(0.0, float(LOUD_K(u))) + 1.5 * sum(bump(u, cc, 0.18) for cc in (1.5, 2.2, 2.9)), axis=0)
    trail(p, t, lambda u: -3.5 * decay(u, 3.55, 0.32, 2.1))
    arms(p, -12 * a + 1.2 * shiv, 8 * a)
    alive(p, t, k=1.0 - 0.85 * smooth((t - 0.5) / 0.5) * (1 - smooth((t - 3.7) / 0.5)))
    step = smooth((t - 0.75) / 0.4)                           # the left foot steps forward and stays
    T.plant(p, "l", arch(t, 0.75, 1.15, 7.0), -10 * a * step, 0, -10 * arch(t, 0.75, 1.15, 1.0), clear=-0.05)
    T.plant(p, "r", 0, 4 * a, 0, 0)
    return p


def gape(t):
    """the warning in profile: the huge mouth opens slowly on the blades, holds with a hiss that shivers, and shuts"""
    p = {}
    k = float(tr((0, 0), (0.6, 1, ease_out), (2.2, 1), (2.8, 0, ease_in))(t))
    o = float(tr((0, 0), (0.4, 0), (1.1, 1, ease_out), (2.0, 0.95), (2.5, 0, ease_in), (2.8, 0))(t))
    hiss = tremor(t, (8.7, 12.9, 6.1), (0.9, 0.5, 0.3)) * window(t, 1.05, 2.05, 0.15)
    add(p, "body", rot=(2 * k + 0.2 * hiss, 6 * k, 0), pos=(0, -1 * k, 0))
    T.neck(p, (-4 * k + 0.4 * hiss, 24 * k, 0)); add(p, "skull", rot=(4 * o + 0.6 * hiss, 8 * k, -10 * k))
    jaw(p, -50 * o - 1.2 * hiss)
    tail(p, pitch=2 * k)
    trail(p, t, lambda u: -4 * float(tr((0, 0), (0.6, 1, ease_out), (2.2, 1), (2.8, 0, ease_in))(u)))
    arms(p, -6 * k, 6 * k)
    alive(p, t, k=0.6)
    return T.stand(p)


def call(t):
    """the call to its mate: two deep notes, the throat humming with each"""
    p = {}
    k = float(tr((0, 0), (0.4, 1, ease_out), (2.2, 1), (2.6, 0, ease_in))(t))
    g = sum(window(t, c, c + 0.45, 0.1) for c in (0.6, 1.4))
    hum = tremor(t, (9.3, 13.1, 6.7), (0.8, 0.45, 0.3)) * window(t, 0.55, 1.95, 0.15)
    add(p, "body", rot=(2 * k + 2.5 * g + 0.3 * hum, 0, 0), pos=(0, 1.0 * g, 0))
    T.neck(p, (8 * k + 3 * g + 0.5 * hum, 0, 0)); add(p, "skull", rot=(4 * k + 2 * g - 0.5 * hum, 0, 0))
    jaw(p, -2 * k - 8 * g - 0.6 * hum)
    trail(p, t, lambda u: 1.5 * sum(window(u, c, c + 0.45, 0.1) for c in (0.6, 1.4)), axis=0)
    alive(p, t, k=1.0 - 0.6 * k)
    return T.stand(p)


# ------------------------------------------------------------------ combat: cut and wait
# the long sideways cut, the hit at 0.5 s (Giganotosaurine SLASH, tick 10): wind up to its right with the jaws wide and
# the head on its side, sweep in low and across, shut on the hit, DRAG the blades on across to the other side, let go,
# pull the head back, settle past the rest
SL_YAW = tr((0, 0), (0.32, 1.0, ease_out), (0.42, 1.05), (0.5, 0.35, ease_in), (0.82, -1.0, ease_out), (0.95, -1.05),
            (1.4, 0, back_out))
SL_LOW = tr((0, 0), (0.3, 0.3, ease_out), (0.5, 1.0, ease_in), (0.82, 0.9), (1.0, -0.4, ease_out), (1.4, 0, back_out))
SL_JAW = tr((0, 0), (0.28, -44, ease_out), (0.42, -46), (0.5, -2, ease_in), (0.84, -3), (0.92, -24, ease_out), (1.1, -8),
            (1.4, 0, ease_out))


def slash(t):
    p = {}
    yw = float(SL_YAW(t)); lo = float(SL_LOW(t)); dn = max(0.0, lo); up = max(0.0, -lo)
    saw = tremor(t, (13.1, 17.9, 9.7), (0.7, 0.4, 0.3)) * window(t, 0.52, 0.82, 0.06)     # the blades sawing
    add(p, "body", rot=(2 * dn - 4 * up, 9 * yw, 3 * yw), pos=(0, -1.4 * dn, -4 * dn + 4 * up))
    cocked = smooth(t / 0.3) * (1 - smooth((t - 0.42) / 0.1))           # the head lifts a little as it winds up
    T.neck(p, (-14 * dn + 10 * up + 4 * cocked + 0.4 * saw, 26 * yw, 0))
    add(p, "skull", rot=(-4 * dn + 4 * up + 0.6 * saw, 12 * yw, -16 * yw + 0.8 * saw))     # on its side, the blades leading
    jaw(p, float(SL_JAW(t)))
    trail(p, t, lambda u: -8 * float(SL_YAW(u)), delay=0.08)
    trail(p, t, lambda u: (lambda l: -2 * max(0, l) + 2 * max(0, -l))(float(SL_LOW(u))), axis=0)
    arms(p, -8 * dn, 6 * dn)
    alive(p, t, k=0.4)
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, -9 * yw, -3 * yw))
    T.plant(p, "l", 0, -4 * dn + 3 * up, 0, 0)
    T.plant(p, "r", 0, 2 * dn + 4 * up, 0, 0)
    return p


# the short cut from the saddle: the hit at 0.3 s (QUICK_BITE, tick 6)
AQ_HIT = tr((0, 0), (0.15, -0.3, ease_out), (0.3, 1, ease_in), (0.42, 1), (1.0, 0, back_out))
AQ_DRAG = tr((0, 0), (0.3, 0), (0.5, 1, ease_out), (1.0, 0, smooth))


def attack_quick(t):
    p = {}
    h = float(AQ_HIT(t)); hit = max(0.0, h); cock = max(0.0, -h) / 0.3
    drag = float(AQ_DRAG(t))
    j = float(tr((0, 0), (0.16, -36, ease_out), (0.3, -2, ease_in), (0.5, -2), (0.6, -14, ease_out), (1.0, 0))(t))
    add(p, "body", rot=(2 * hit - 1 * cock, -4 * drag + 2 * cock, 0), pos=(0, -0.8 * hit, -3 * hit + 1 * cock))
    T.neck(p, (-10 * hit + 3 * cock, 14 * hit - 22 * drag + 4 * cock, 0)); add(p, "skull", rot=(-3 * hit, -10 * drag, 12 * drag - 6 * cock))
    jaw(p, j)
    trail(p, t, lambda u: 6 * float(AQ_DRAG(u)) - 2 * max(0.0, -float(AQ_HIT(u))))
    alive(p, t, k=0.5)
    return T.stand(p)


# the low strike at the leg of big prey: the hit at 0.6 s (LUNGE, tick 12)
LG_COIL = tr((0, 0), (0.35, 1, ease_out), (0.42, 1), (0.55, 0, ease_in), (1.6, 0))
LG_OUT = tr((0, 0), (0.42, 0), (0.6, 1, ease_in), (0.85, 1), (1.3, -0.12, ease_out), (1.6, 0, smooth))


def lunge(t):
    p = {}
    coil = float(LG_COIL(t)); out = float(LG_OUT(t))
    j = float(tr((0, 0), (0.4, -10), (0.52, -40, ease_out), (0.6, -2, ease_in), (1.2, -2), (1.6, 0))(t))
    add(p, "body", rot=(3 * coil - 5 * out, 0, 0), pos=(0, -1 * coil - 4 * out, 5 * coil - 9 * out))
    T.neck(p, (8 * coil - 22 * out, 0, 0)); add(p, "skull", rot=(4 * coil + 6 * out + 3 * bump(t, 0.62, 0.05), 0, 0))
    jaw(p, j)
    trail(p, t, lambda u: -3 * float(LG_COIL(u)) + 5 * float(LG_OUT(u)), axis=0)
    trail(p, t, lambda u: 3 * decay(u, 0.62, 0.25, 2.0))
    arms(p, -10 * out, 10 * out)
    alive(p, t, k=0.4)
    T.plant(p, "l", 0, 5 * coil - 10 * out, 0, 0)
    T.plant(p, "r", 0, 3 * coil + 6 * out, 0, 0)
    return p


def rip_shake(t):
    """the tear on big prey: shark shakes with the legs braced, uneven in time and size, building and dying"""
    env = window(t, 0.55, 1.7, 0.15)
    return env * (0.75 * math.sin(2 * math.pi * 2.8 * (t - 0.5)) + 0.25 * math.sin(2 * math.pi * 4.3 * (t - 0.5) + 0.8))


# holds on and shakes; the hit at 0.45 s (RIP, tick 9)
def rip(t):
    p = {}
    k = float(tr((0, 0), (0.3, 1, ease_out), (1.8, 1), (2.2, 0, ease_out))(t))
    bite = float(tr((0, 0), (0.25, 0), (0.45, 1, ease_in), (1.75, 1), (1.85, 0), (2.2, 0))(t))
    sh = rip_shake(t)
    j = float(tr((0, 0), (0.25, -38, ease_out), (0.45, -4, ease_in), (1.75, -4), (1.85, -24), (2.2, 0))(t))
    add(p, "body", rot=(-3 * bite, 4 * sh, 3 * sh), pos=(0, -1.5 * k, 3 * bite))
    T.neck(p, (-12 * k + 8 * bite, 16 * sh, 0)); add(p, "skull", rot=(-4 * k, 14 * sh, 16 * sh))
    jaw(p, j)
    tail(p, pitch=2 * bite)
    trail(p, t, lambda u: -7 * rip_shake(u))
    alive_upper(p, t, k=0.4)
    T.plant(p, "l", 0, 6 * bite, 0, 0)
    T.plant(p, "r", 0, 10 * bite, 0, 0)
    return p


def stomp(t):
    """a small thing at its feet: the right foot lifted high, held, the whole weight brought down (the hit at 0.9 s)"""
    p = {}
    upf = tr((0, 0), (0.55, 1, ease_out), (0.75, 1), (0.9, 0, ease_in), (1.7, 0))
    up = float(upf(t))
    land = bump(t, 0.92, 0.06)
    add(p, "body", rot=(-3 * up + 2 * land, 0, -3 * up), pos=(0, -1.5 * land, 0))
    T.neck(p, (-8 * up - 4 * land, 0, 0)); add(p, "skull", rot=(-6 * up + 2 * bump(t, 1.0, 0.1), 0, 0)); jaw(p, -6 * land)
    trail(p, t, lambda u: -2 * float(upf(u)) + 4 * bump(u, 0.92, 0.1), axis=0)
    alive_upper(p, t, k=0.5)
    T.plant(p, "l")
    T.plant(p, "r", 18 * up, -14 * up, -20 * up, -10 * up)
    return p


def hurt(t):
    """the long neck pulls in and the heavy body flinches aside; the tail swings after it, slowly"""
    p = {}
    e = math.exp(-(t / 0.18)) * smooth(t / 0.05)
    add(p, "body", rot=(4 * e, -4 * e, 4 * e), pos=(0, -0.6 * e, 2 * e))
    T.neck(p, (8 * e, -10 * e, 0)); add(p, "skull", rot=(4 * e, -4 * e, 8 * e)); jaw(p, -16 * e)
    trail(p, t, lambda u: 5 * math.exp(-(u / 0.25)) * smooth(u / 0.06), delay=0.06)
    arms(p, -12 * e, 10 * e)
    alive(p, t, k=0.5)
    return T.stand(p)


# ------------------------------------------------------------------ the fight (the common set, its way: patient)
GUARD_T = 3.2


def guard(t):
    """it does not bounce or weave: it stands heavy and low, the head on its side and one eye on the rival, the jaws ajar
    on the blades with a low hiss, the body leaning slowly toward the rival and back; the long tail moves in a slow S"""
    p = {}
    L = GUARD_T
    lean = wave(t, L)
    hiss = tremor(t, (19 / L, 27 / L, 13 / L), (0.7, 0.4, 0.3))     # harmonics of the loop: it closes
    add(p, "body", rot=(4 + 0.8 * lean, 0.8 * wave(t, L, 1.2), 1.2 * wave(t, L / 2, 0.3)), pos=(0, -2.5 + 0.4 * lean, -1.0 * lean))
    eye(p, 0.75 + 0.1 * wave(t, L, -0.8), 1.0, low=6)
    T.neck(p, (-0.8 * lean + 0.3 * hiss, -0.8 * wave(t, L, 1.2), 0))
    add(p, "skull", rot=(0.4 * hiss + 0.5 * wave(t, L / 2, -0.4), 0, 0))
    jaw(p, -7 - 2.0 * max(0.0, wave(t, L / 2, -0.6)) - 1.0 * hiss)
    for i, (b, g) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(-1.0 * g + 0.3 * (i + 1) * g * wave(t, L / 2, -0.5 * i), g * (1.0 + 0.7 * i) * wave(t, L, -0.7 * i), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(-8 + 1.5 * wave(t, L / 2, -1 - 3 * o), 0, 0)); add(p, f"forearm_{s}", rot=(10 + 1.5 * wave(t, L / 2, -1.6 - 3 * o), 0, 0))
        add(p, f"thigh_{s}", rot=(0, -0.8 * wave(t, L, 1.2), -1.2 * wave(t, L / 2, 0.3)))
    T.plant(p, "l", 0.0, -4.0)
    T.plant(p, "r", 0.0, 2.0)
    return p


STRAFE_T = 2.0


def strafe(t, side):
    """heavy sideways steps: each foot swung wide and set down slowly, the hips rolling over it, the body turned in
    a little toward the rival and the head on its side watching it with the near eye, the long tail swinging out"""
    d = 1.0 if side == "left" else -1.0
    ph = (t / STRAFE_T) % 1.0; w = 2 * math.pi * ph; p = {}
    hroll = -2.5 * d + 2.5 * math.sin(2 * w + 0.4)
    add(p, "body", rot=(3 + 0.6 * math.cos(2 * w), -6 * d, hroll), pos=(0, -2.0 + 0.8 * math.cos(2 * w + 0.3), 0))
    eye(p, 0.6, -d, low=4)                                  # the eye on the rival's side up (it moves round it)
    T.neck(p, (0.6 * math.sin(2 * w - 0.8), 6 * d, -0.7 * hroll))
    jaw(p, -4 - 0.8 * tremor(t, (11 / STRAFE_T, 17 / STRAFE_T, 7 / STRAFE_T), (0.6, 0.4, 0.3)))
    for i, (b, g) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(0.3 * (i + 1) * g * math.sin(2 * w - 1.0 - 0.6 * i), g * (5.0 * d * (0.5 + 0.25 * i) - (0.8 + 0.6 * i) * math.sin(2 * w - 1.0 - 0.7 * i)), 0))
    for s, o in SIDES:
        sx = 1 if s == "l" else -1
        u = (ph + o) % 1.0
        add(p, f"arm_{s}", rot=(-6 + 2 * math.sin(w + o * 2 * math.pi - 2.4), 0, 0))
        if u < 0.36:
            sw = u / 0.36
            ly = 5.5 * math.sin(math.pi * sw) ** 1.3
            add(p, f"thigh_{s}", rot=(0, 6 * d, d * 7.0 * (sw - 0.5) + 2.5 * sx - hroll))
            T.plant(p, s, ly, 0.0, 6 * math.sin(math.pi * sw), -14 * math.sin(math.pi * sw), clear=0.8 * math.sin(math.pi * sw) ** 0.5)
        else:
            st = (u - 0.36) / 0.64
            add(p, f"thigh_{s}", rot=(0, 6 * d, -d * 7.0 * (st - 0.5) + 2.5 * sx - hroll))
            T.plant(p, s)
    return p


def strafe_left(t): return strafe(t, "left")
def strafe_right(t): return strafe(t, "right")


TURN_T = 2.0


def turn(t, side):
    """a slow heavy turn on the spot: the long neck sweeps round first and the head tips on its side to look with the
    leading eye, the hips follow a beat later, the whole tail swings wide the other way. A + yaw swings the head to the
    animal's RIGHT in game: a left turn leads with - yaw"""
    d = 1.0 if side == "left" else -1.0
    ph = (t / TURN_T) % 1.0; w = 2 * math.pi * ph; p = {}
    lead = -d
    add(p, "body", rot=(0, lead * (3.0 + 1.5 * math.sin(w - 0.5)), 3.5 * math.sin(w + 0.3)), pos=(0, -0.8 + 0.7 * math.cos(2 * w), 0))
    T.neck(p, (-1.0, lead * (14.0 + 2.5 * math.sin(w - 0.2)), -2.4 * math.sin(w + 0.3)))
    add(p, "skull", rot=(1.0, lead * (6.0 + 1.5 * math.sin(w - 0.8)), lead * 12.0))      # the leading eye up
    jaw(p, -1.0 - 0.6 * max(0.0, math.sin(2 * w)))
    for k, (b, g) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(0.3 * (k + 1) * g * math.sin(2 * w - 0.6 * k), g * (-lead * (2.5 + 1.2 * k) - (1.0 + 0.8 * k) * math.sin(w - 0.9 * (k + 1))), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(3 * math.sin(w + o * 2 * math.pi - 2.2), 0, 0))
        u = (ph + o) % 1.0
        if u < 0.36:
            sw = u / 0.36
            ly = 5.5 * math.sin(math.pi * sw) ** 1.3
            dz = -3.0 * math.cos(math.pi * sw)
            toe = -18 * math.sin(math.pi * sw); meta = 10 * math.sin(math.pi * sw); clear = 0.9 * math.sin(math.pi * sw) ** 0.5
            add(p, f"thigh_{s}", rot=(0, lead * 5.0 * math.sin(math.pi * sw), 0))
        else:
            ly, dz, toe, meta, clear = 0.0, 3.0 - 6.0 * ((u - 0.36) / 0.64), 0.0, 0.0, -0.05
        add(p, f"thigh_{s}", rot=(0, -lead * 3.0, -3.5 * math.sin(w + 0.3)))
        T.plant(p, s, ly, dz, meta, toe, clear)
    return p


def turn_left(t): return turn(t, "left")
def turn_right(t): return turn(t, "right")


FEINT_T = 1.4


def feint(t):
    """a cut it does not finish: the head cocks on its side and the jaws spread on the blades, it swings in half way
    and stops with the mouth still open, then draws back slowly, watching (it tests, it does not snap at air)"""
    p = {}
    yw = float(tr((0, 0), (0.35, 1.0, ease_out), (0.55, 0.3, ease_in), (0.7, 0.25), (1.4, 0, smooth))(t))
    dn = float(tr((0, 0), (0.35, 0.3, ease_out), (0.55, 0.8, ease_in), (0.7, 0.75), (1.4, 0, back_out))(t))
    j = float(tr((0, 0), (0.3, -40, ease_out), (0.75, -36), (1.15, -6, ease_in), (1.4, 0))(t))
    stop = bump(t, 0.57, 0.05)
    add(p, "body", rot=(1.5 * dn, 6 * yw, 2 * yw), pos=(0, -1.0 * dn, -3.5 * dn + 0.8 * stop))
    T.neck(p, (-10 * dn + 2 * stop, 18 * yw, 0)); add(p, "skull", rot=(-3 * dn + 2 * stop, 6 * yw, -16 * yw))
    jaw(p, j)
    trail(p, t, lambda u: -5 * float(tr((0, 0), (0.35, 1.0, ease_out), (0.55, 0.3, ease_in), (0.7, 0.25), (1.4, 0, smooth))(u)))
    alive(p, t, k=0.5)
    return T.stand(p)


BLOCK_T = 0.9


def block(t):
    """it keeps its long head out of the way: the head swings up and away and the blow lands on the thick shoulder; the
    heavy body takes it with a slow sway"""
    p = {}
    away = float(tr((0, 0), (0.1, 1, ease_out), (0.3, 0.9), (0.9, 0, ease_out))(t))
    e = math.exp(-max(0.0, t - 0.08) / 0.28) * smooth((t - 0.05) / 0.05)
    add(p, "body", rot=(-1.5 * e, -5 * e, 4 * e), pos=(0, -0.6 * e, 1.5 * e))
    T.neck(p, (8 * away, -18 * away, 0)); add(p, "skull", rot=(4 * away, -6 * away, 10 * away)); jaw(p, -4 * away)
    trail(p, t, lambda u: 5 * math.exp(-max(0.0, u - 0.08) / 0.3) * smooth((u - 0.05) / 0.05))
    alive_upper(p, t, k=0.5)
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, 5 * e, -4 * e))
    return T.stand(p)


RECOIL_T = 1.0


def recoil(t):
    """its cut glanced off: the open jaws slide along and off, the head carried on past by its own weight, and one
    heavy step back with the left foot"""
    p = {}
    slide = float(tr((0, 0), (0.12, 1, ease_out), (0.4, 0.8), (1.0, 0, ease_out))(t))
    e = math.exp(-max(0.0, t - 0.05) / 0.25) * smooth(t / 0.05)
    add(p, "body", rot=(-2 * e, -6 * slide, -2 * slide), pos=(0, -0.5 * e, 2.5 * e))
    T.neck(p, (4 * e, -20 * slide, 0)); add(p, "skull", rot=(3 * e, -8 * slide, 8 * slide)); jaw(p, -18 * e)
    trail(p, t, lambda u: 7 * float(tr((0, 0), (0.12, 1, ease_out), (0.4, 0.8), (1.0, 0, ease_out))(u)))
    alive_upper(p, t, k=0.5)
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, 6 * slide, 2 * slide))
    lift = arch(t, 0.15, 0.6, 5.0)
    T.plant(p, "l", lift, 4 * smooth((t - 0.15) / 0.45), 0, -10 * lift / 5.0, clear=-0.05)
    T.plant(p, "r")
    return p


SUBMIT_T = 2.8


def submit(t):
    """beaten: it shuts the mouth on the blades, sinks the head slowly, turns it on its side away from the winner
    (the eye hidden), and swings the heavy body round to go"""
    p = {}
    k = float(tr((0, 0), (0.8, 1, ease_out), (2.8, 1))(t))
    turn_ = float(tr((0, 0), (1.0, 0), (2.2, 1, smooth), (2.8, 1))(t))
    add(p, "body", rot=(-3 * k, 10 * turn_, 0), pos=(0, -2.5 * k, 0))
    T.neck(p, (-14 * k, 12 * turn_, 0)); add(p, "skull", rot=(-4 * k, 4 * turn_, 18 * k))
    jaw(p, 0.5 * k)
    tail(p, pitch=4 * k)
    trail(p, t, lambda u: -5 * float(tr((0, 0), (1.0, 0), (2.2, 1, smooth), (2.8, 1))(u)))
    arms(p, 6 * k, -4 * k)
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, -10 * turn_, 0))
    alive_upper(p, t, k=0.9, period=2.2)
    return T.stand(p)


# ------------------------------------------------------------------ transitions and tiredness
LIE_DOWN_T = 2.6


def lie_down(t):
    """slow and heavy: the legs fold, the deep chest goes down and lands with a bump, the long head comes down last"""
    p = {}
    k = float(tr((0, 0), (0.35, 0.05), (1.75, 0.94, ease_in), (1.95, 1.02), (2.6, 1.0, ease_out))(t))
    head = float(tr((0, 0), (0.5, 0.6, ease_out), (1.8, 0.6), (2.6, 0, ease_out))(t))
    fold(p, k)
    T.neck(p, (6 * head, 0, 0))                            # it holds the head up while the body goes down
    land = bump(t, 1.9, 0.1)
    add(p, "body", rot=(0.8 * land, 0, 0)); jaw(p, -3 * land)
    trail(p, t, lambda u: 2.5 * bump(u, 1.9, 0.16), axis=0)
    alive_upper(p, t, k=0.5)
    return ground_fit(S, p)


GET_UP_T = 2.6


def get_up(t):
    """the head swings forward and down to throw the weight over the feet, the legs push, a slow sway as it stands"""
    p = {}
    k = float(tr((0, 1.0), (0.55, 1.02), (1.65, 0.05, ease_out), (1.9, -0.02), (2.6, 0.0, ease_out))(t))
    push = bump(t, 0.75, 0.25)
    fold(p, max(0.0, k))
    T.neck(p, (-10 * push, 0, 0)); add(p, "skull", rot=(-4 * push, 0, 0))
    wob = decay(t, 1.7, 0.35, 1.6)
    add(p, "body", rot=(0, 0, 2.2 * wob))
    trail(p, t, lambda u: -3.0 * decay(u, 1.7, 0.4, 1.6))
    alive_upper(p, t, k=0.5)
    return ground_fit(S, p)


WALK_TIRED_T = 2.4


def walk_tired(t):
    """dragging the weight: short steps (the 56 px every 2.4 s the Java plays), the hips rolling deep, the head
    hanging low, the long jaws open, the tail low"""
    p = gait2(t, WALK_TIRED_T, 56, 0.68, 6, 2.0, lean=2, drop=2, head=-8, roll=9.0, yaw=4.0, whip=0.9, arm_amp=1.5, tail_up=2.0)
    pant = wave(t, WALK_TIRED_T / 3)
    jaw(p, -12 - 6 * max(0.0, pant)); T.neck(p, (-1.4 * wave(t, WALK_TIRED_T / 3, -0.5), 0, 0))
    return p


IDLE_TIRED_T = 3.2


def idle_tired(t):
    """spent: the deep chest heaves slowly and hard, the long jaws hang wide, the head almost to the ground and
    tilted, the weight sagging onto one leg"""
    p = {}
    L = IDLE_TIRED_T
    pant = wave(t, L / 3)
    sag = 2.5 + 0.8 * wave(t, L, 0.4)
    add(p, "body", rot=(2.0 + 2.2 * pant, 0, sag), pos=(0, -1.8 + 0.9 * pant, 0))
    T.neck(p, (-12 - 1.8 * wave(t, L / 3, -0.6), 1.5 * wave(t, L, 0.5), -0.7 * sag))
    add(p, "skull", rot=(-3 - 1.2 * wave(t, L / 3, -1.2), 0, -6))
    jaw(p, -16 - 7 * max(0.0, wave(t, L / 3, -0.4)))
    for i, (b, g) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(1.5 * g + 0.3 * (i + 1) * g * pant, g * (0.8 + 0.6 * i) * wave(t, L, -0.8 * (i + 1)), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(8 + 2.0 * wave(t, L / 3, -0.8 - o), 0, 0))
        add(p, f"thigh_{s}", rot=(0, 0, -sag))
    return T.stand(p)


# ------------------------------------------------------------------ its signature: grab and shake (smaller prey)
GRAB_SHAKE_T = 2.4
# the jaws shut at 0.45 s (tick 9): aim with one eye, strike down, LIFT the animal off the ground, shake it like a
# shark (uneven shakes, the first the widest, the body and the tail answering late), fling it aside, settle
GS_UP = tr((0, 0), (0.25, 0.25, ease_out), (0.45, -1.0, ease_in), (0.55, -0.9), (0.8, 1.0, ease_out), (1.7, 0.9),
           (1.95, 0.4), (2.4, 0, back_out))
GS_JAW = tr((0, 0), (0.25, -40, ease_out), (0.38, -42), (0.45, -3, ease_in), (1.78, -4), (1.88, -28, ease_out), (2.1, -8),
            (2.4, 0, ease_out))
GS_EYE = tr((0, 0), (0.22, 1, ease_out), (0.42, 0.2, ease_in), (2.4, 0))


def grab_shake(t):
    s = 0.0
    for c, amp, w in ((0.92, 1.0, 0.09), (1.1, -0.9, 0.085), (1.27, 0.75, 0.08), (1.43, -0.55, 0.08), (1.58, 0.3, 0.07)):
        s += amp * math.exp(-((t - c) / w) ** 2)
    return s


def grab_shake_pose(t):
    p = {}
    u = float(GS_UP(t)); up = max(0.0, u); dn = max(0.0, -u)
    sh = grab_shake(t)
    fling = bump(t, 1.85, 0.08)
    add(p, "body", rot=(3 * up - 2 * dn, 4 * sh + 4 * fling, 3 * sh), pos=(0, -1.2 * dn + 0.5 * up, -3 * dn + 1.5 * up))
    T.neck(p, (14 * up - 14 * dn, 18 * sh + 16 * fling, 0))
    add(p, "skull", rot=(5 * up - 6 * dn, 10 * sh + 8 * fling, -14 * sh - 10 * fling))
    eye(p, float(GS_EYE(t)), 1.0, low=4)
    jaw(p, float(GS_JAW(t)))
    trail(p, t, lambda v: -8 * grab_shake(v) - 6 * bump(v, 1.85, 0.1))
    trail(p, t, lambda v: (lambda uu: -2.5 * max(0, uu) + 2 * max(0, -uu))(float(GS_UP(v))), axis=0)
    arms(p, -10 * up + 3 * sh, 8 * up)
    alive_upper(p, t, k=0.4)
    for s_, _ in SIDES:
        add(p, f"thigh_{s_}", rot=(0, -4 * sh, -3 * sh))
    T.plant(p, "l", 0, -3 * up, 0, 0)
    T.plant(p, "r", 0, 3 * up, 0, 0)
    return p


# ------------------------------------------------------------------ the fluid layer over the rest
def _with_breath(fn, k=0.5, period=3.4, slow=None):
    def g(t):
        p = fn(t)
        alive_upper(p, t, k=k, period=period, slow=slow)
        return p
    g.__name__ = fn.__name__
    return g


def _with_tail_follow(fn, k=0.5):
    def g(t):
        p = fn(t)
        alive_upper(p, t, k=k)
        trail(p, t, lambda u: -0.3 * fn(max(0.0, u)).get("body", ([0, 0, 0],))[0][1] - 0.15 * sum(
            fn(max(0.0, u)).get(n, ([0, 0, 0],))[0][1] for n in ("neck1", "neck2")))
        return p
    g.__name__ = fn.__name__
    return g


def sit(t):
    """lying awake, as before (gigaanims.sit), but the breath every 3 s: its 3.6 s breath did not divide the 6 s loop and
    the seam jumped 0.6 deg"""
    p = {}; br = wave(t, 3.0)
    fold(p, 1.0); add(p, "body", rot=(0.7 * br, 0, 0))
    a = float(tr((0, 0), (1.8, 0), (2.4, 1, ease_out), (3.8, 1), (4.4, 0, smooth), (6.0, 0))(t))
    T.neck(p, (6 - 0.5 * br, 0, 0)); eye(p, a, 1.0)
    A.tail_wave(p, t, 6.0, 1.2)
    return ground_fit(S, p)


look_side = _with_tail_follow(A.look_side, 0.6)
eye_aim = _with_breath(A.eye_aim, 0.4, period=1.1)
crest_show = _with_tail_follow(A.crest_show, 0.5)
sniff = _with_breath(A.sniff, 0.4)
shake = _with_breath(A.shake, 0.3)
yawn = _with_breath(A.yawn, 0.4)
stretch = _with_breath(A.stretch, 0.4)
jaw_rub = _with_breath(A.jaw_rub, 0.4)
eat = _with_breath(A.eat, 0.4)
drink = _with_breath(A.drink, 0.3)
beg = _with_breath(A.beg, 0.5, period=2.0, slow=2.0)
tame = _with_breath(A.tame, 0.5)

REBIND = {
    "idle": idle, "walk": walk, "run": run, "stalk": stalk, "back_off": back_off, "circle": circle, "slash": slash,
    "attack_quick": attack_quick, "lunge": lunge, "rip": rip, "stomp": stomp, "hurt": hurt, "gape": gape, "roar": roar,
    "roar_loud": roar_loud, "call": call, "look_side": look_side, "eye_aim": eye_aim, "crest_show": crest_show,
    "sniff": sniff, "shake": shake, "yawn": yawn, "stretch": stretch, "jaw_rub": jaw_rub, "eat": eat, "drink": drink,
    "beg": beg, "tame": tame, "sit": sit,
}

NEW = {
    "guard": (guard, GUARD_T, True, "Duelo", "em guarda: pesado e baixo, a cabeça de lado e um olho no rival, boca entreaberta chiando"),
    "strafe_left": (strafe_left, STRAFE_T, True, "Duelo", "passos pesados de lado para a esquerda, olhando com um olho"),
    "strafe_right": (strafe_right, STRAFE_T, True, "Duelo", "passos pesados de lado para a direita, olhando com um olho"),
    "turn_left": (turn_left, TURN_T, True, "Movimento", "girando no lugar para a esquerda: o pescoço varre primeiro"),
    "turn_right": (turn_right, TURN_T, True, "Movimento", "girando no lugar para a direita"),
    "feint": (feint, FEINT_T, False, "Duelo", "finta: arma o corte de boca aberta, para no meio e recua devagar"),
    "block": (block, BLOCK_T, False, "Duelo", "tira a cabeça do caminho e recebe o golpe no ombro"),
    "recoil": (recoil, RECOIL_T, False, "Duelo", "o corte escorregou: a cabeça passa de lado, um passo pesado atrás"),
    "submit": (submit, SUBMIT_T, False, "Duelo", "perdeu: fecha a boca, abaixa e esconde o olho, vira o corpo e vai"),
    "lie_down": (lie_down, LIE_DOWN_T, False, "Descanso", "deitando devagar (de pé para sentado)"),
    "get_up": (get_up, GET_UP_T, False, "Descanso", "levantando devagar (de sentado para de pé)"),
    "idle_tired": (idle_tired, IDLE_TIRED_T, True, "Parado", "parado cansado, o peito arfando fundo"),
    "walk_tired": (walk_tired, WALK_TIRED_T, True, "Movimento", "andando cansado, arrastando o peso"),
    "grab_shake": (grab_shake_pose, GRAB_SHAKE_T, False, "Combate", "presa menor: morde (0,45 s), ergue e sacode como tubarão, joga de lado"),
}
