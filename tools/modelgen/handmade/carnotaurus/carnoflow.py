"""Carnotaurus: the fluid set and its fighting moves (06/11/2026). Rodrigo: "quase um jogo de luta entre dinos, cada
um com sua animacao unica e fluida, lembrando que tem que ter um estudo por tras sempre".

Two studies behind it:
  * docs/estudos/08_ANIMACAO_RAXIORES.md, the rules of the fluid T. rex (rexflow.py): nothing stops (a breathing layer
    under every one-shot), nothing switches on or off (envelopes), three beats per action (anticipation, strike,
    settle that passes the rest pose a little), the tail and the neck follow late, tremors are sums of sines that never
    line up, loop periods divide the loop so the seams close;
  * docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md, its row: horns and a braced skull for head blows (Mazzetta et al.
    1998, 2009), a weak quick bite, the fastest of the big theropods. It does not bite to hold: it BUTTS with the horns,
    from the front and from the side, snaps and cuts quickly and moves a lot sideways.

What makes it itself here, against the T. rex:
  * light and long-legged: a springy gait with less hip roll than the T. rex, quick cycles, the head held still;
  * the back half of the tail is locked (caudal ribs): every tail layer bends only tail1-tail3 (STIFF gains), the rest
    rides along straight, so its follow-through is a stiff lever swinging from the root;
  * the head aims in hawk jumps that now land with a small overshoot instead of stopping dead;
  * its signature blows: `ram` (head down, a short charge, the horns driven in) and `head_clash` (brace, impact, shove).
"""
import math

import carnoanims as A
from anim2 import add, smooth, ease_in, ease_out, back_out, Track
from theropod import window, SIDES

S, T = A.S, A.T
TAILS = A.TAILS
tr = A.tr
arms = A.arms
tail = A.tail
fold, ground_fit = A.fold, A.ground_fit

STIFF = (1.0, 0.85, 0.4, 0.1, 0.0)        # how much each tail bone takes of a follow-through (the back half locked)


# ------------------------------------------------------------------ helpers (the same ideas as rexflow, on this rig)
def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def tremor(t, f=(7.9, 12.3, 5.1), amp=(1.0, 0.55, 0.35), phase=0.0):
    """an organic shiver: three sines at frequencies that never line up"""
    return sum(a * math.sin(2 * math.pi * fr * t + phase * (i + 1) + 1.3 * i) for i, (fr, a) in enumerate(zip(f, amp)))


def trail(p, t, fn, gain=STIFF, delay=0.06, axis=1, loop=None):
    """follow-through down the tail: bone k takes fn(t - (k+1)*delay) * gain[k] (the locked bones take ~nothing)"""
    for k, b in enumerate(TAILS):
        if not gain[k]:
            continue
        u = t - delay * (k + 1)
        v = fn(u % loop if loop else max(0.0, u)) * gain[k]
        r = [0.0, 0.0, 0.0]; r[axis] = v
        add(p, b, rot=tuple(r))


def alive(p, t, k=1.0, period=2.4):
    """the breathing layer under every one-shot (call before the feet are planted: it moves the body)"""
    br = wave(t, period)
    add(p, "body", rot=(0.6 * k * br, 0, 0), pos=(0, 0.35 * k * br, 0))
    alive_upper(p, t, k, period)
    return br


def alive_upper(p, t, k=1.0, period=2.4, slow=None):
    """the breath without the hips (safe after the feet are planted); in a loop, `slow` = a period that divides it"""
    s1, s2 = (slow, slow) if slow else (period * 1.5, period * 2)
    T.neck(p, (-0.5 * k * wave(t, period, -0.5), 0, 0))
    add(p, "skull", rot=(-0.35 * k * wave(t, period, -1.0), 0, 0))
    add(p, "jaw", rot=(-0.5 * k * max(0.0, wave(t, period, -0.6)), 0, 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(1.2 * k * wave(t, period, -0.8 - o), 0, 0))
        add(p, f"forearm_{s}", rot=(1.0 * k * wave(t, s1, -1.4 - o), 0, 0))
    for i, (b, g) in enumerate(zip(TAILS, STIFF)):
        if g:
            add(p, b, rot=(0.4 * k * g * wave(t, period, -0.5 * i), 0.9 * k * g * wave(t, s2, -0.7 * i), 0))


def snap(t, keys, dur=0.16):
    """the hawk aim: jumps between held aims, each landing with a ~5% overshoot (back_out) instead of a dead stop"""
    cur = (0.0, 0.0)
    for tk, v in keys:
        if t < tk:
            break
        u = back_out(min(1.0, (t - tk) / dur), 1.2)
        cur = (cur[0] + (v[0] - cur[0]) * u, cur[1] + (v[1] - cur[1]) * u)
    return cur


def bump(t, c, w):
    return math.exp(-((t - c) / w) ** 2)


def decay(t, at, tau, f):
    """a wobble that starts at `at` and dies out (eased in over 0.05 s so it never pops)"""
    return math.exp(-max(0.0, t - at) / tau) * math.sin(2 * math.pi * f * (t - at)) * smooth((t - at + 0.02) / 0.05)


def steps(t, a, b, h):
    """a foot lifted between a and b: 0 outside, a smooth arch of height h inside"""
    u = min(1.0, max(0.0, (t - a) / (b - a)))
    return h * math.sin(math.pi * u) ** 1.3


# ------------------------------------------------------------------ the gait with weight (gait2 on a light runner)
def landing(x):
    """-1 just after a heel strike, +1 mid-stance: the drop comes fast, the rise slow"""
    x %= 1.0
    return -1.0 + 2.0 * smooth(x / 0.26) if x < 0.26 else 1.0 - 2.0 * smooth((x - 0.26) / 0.74)


def gait2(t, Tc, stride, duty, lift, bob, lean=0.0, drop=0.0, head=0.0, roll=5.0, yaw=3.0, whip=1.0, splay=2.5,
          still=0.88, stance_clear=-0.05, arm_amp=3.0, tail_up=0.0):
    """the hips roll over the stance leg and yaw with the swinging one, each thigh cancels them so the foot stays put,
    the chest counters and the head floats still (its hawk gaze), the stiff tail swings from its root, late"""
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    b2 = landing(2 * ph + 0.06)
    hroll = roll * math.sin(w + 0.25)
    hyaw = yaw * math.sin(w - 0.6)
    bp = 1.0 * b2
    add(p, "body", rot=(lean + bp, hyaw, hroll), pos=(0, bob * b2 - 0.6 - drop, 0))
    T.neck(p, (head - lean * still - 1.0 * still * landing(2 * ph - 0.03), -0.9 * hyaw - 1.2 * math.sin(w - 1.4),
               -0.75 * hroll))
    add(p, "skull", rot=(-head * 0.3 + 0.7 * landing(2 * ph - 0.12), -0.1 * hyaw + 0.8 * math.sin(w - 2.0),
                         -0.25 * hroll + 0.8 * math.sin(w - 1.2)))
    add(p, "jaw", rot=(-0.8 - 0.8 * max(0.0, landing(2 * ph - 0.2)), 0, 0))
    for k, (b, g) in enumerate(zip(TAILS, STIFF)):        # the lever: the root swings, the locked half rides it, late
        if not g:
            continue
        lag = 0.7 * (k + 1)
        add(p, b, rot=(tail_up * g - 0.9 * g * landing(2 * ph - 0.08 * (k + 1)),
                       -2.8 * whip * g * (1.0 + 0.4 * k) * math.sin(w - 0.6 - lag), 0.6 * whip * g * math.sin(w - 0.4 - lag)))
    for s, o in SIDES:                                    # the stubby arms jiggle, a beat late
        f = w + o * 2 * math.pi
        add(p, f"arm_{s}", rot=(arm_amp * math.sin(2 * f - 2.2) + 1.5 * landing(2 * ph - 0.25), 0, 0))
        add(p, f"forearm_{s}", rot=(1.5 * landing(2 * ph - 0.35), 0, 0))
    for s, o in SIDES:
        sx = 1 if s == "l" else -1
        u = (ph + o) % 1.0
        swing = 0.0 if u < duty else math.sin(math.pi * (u - duty) / (1 - duty))
        add(p, f"thigh_{s}", rot=(0, -hyaw, -hroll + sx * splay * swing))
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0
            meta = 36 * smooth(max(0, (st - 0.5) / 0.5)); clear = stance_clear
            toe = 8 * (1 - smooth(min(1.0, st / 0.18))) + 10 * smooth(max(0, (st - 0.7) / 0.3))
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e
            ly = lift * math.sin(math.pi * min(1, sw * 1.1)) ** 1.1
            meta = 36 * (1 - smooth(sw / 0.45)) - 26 * math.sin(math.pi * sw)
            toe = -34 * math.sin(math.pi * min(1, sw * 1.1)) + 8 * smooth((sw - 0.7) / 0.3)
            clear = stance_clear + 1.2 * math.sin(math.pi * sw) ** 0.5     # meets the stance value at both ends
        T.plant(p, s, ly, dz - 4, meta, toe, clear)
    return p


WALK, RUN = A.WALK, A.RUN        # lengths and strides stay: the Java ties the cycle speed to them (Abelisaur WALK_PX...)


def walk(t):
    return gait2(t, *WALK)


def run(t):
    """the sprint: the body low and level, the neck straight out, the hips hardly roll, the tail a rigid counterweight"""
    p = gait2(t, *RUN, lean=7, drop=4, head=-6, roll=2.6, yaw=1.8, whip=0.55, splay=1.5, still=0.95, stance_clear=0.2,
              arm_amp=1.5, tail_up=2)
    arms(p, -14, 12)
    return p


def stalk(t):
    Tw, st, du, li, bo = WALK
    p = gait2(t, Tw * 1.6, st * 0.7, 0.72, li * 0.7, bo * 0.4, lean=4, drop=8, head=-10, roll=2.2, yaw=1.2, whip=0.4,
              still=1.0, arm_amp=1.0, tail_up=-2)
    return p


# ------------------------------------------------------------------ idle: 8 s, the hawk aims, nothing in step
IDLE_T = 8.0
AIM = [(0.0, (0, 0)), (1.1, (3, 14)), (2.4, (3, 22)), (3.3, (-2, -8)), (4.9, (5, -18)), (5.6, (1, -6)), (7.1, (0, 0))]


def idle(t):
    p = {}
    Tl = IDLE_T
    br = wave(t, Tl / 4)                                     # a breath every 2 s (light, quick)
    shift = wave(t, Tl, 0.4) + 0.3 * wave(t, Tl / 2, 1.1)    # the weight drifts from one foot to the other
    hroll = 1.6 + 2.0 * shift
    hyaw = -1.4 + 1.1 * shift
    add(p, "body", rot=(0.7 * br - 0.3, hyaw, hroll), pos=(0, 0.35 * br - 0.12 * shift * shift, 0))
    hp, hy = snap(t, AIM)
    drift = 1.0 * wave(t, Tl / 5, 0.3)
    T.neck(p, (hp * 0.4 - 0.5 * wave(t, Tl / 4, -0.5), hy * 0.4 - 0.8 * hyaw + drift, -0.7 * hroll))
    add(p, "skull", rot=(hp * 0.6 - 0.35 * wave(t, Tl / 4, -1.0) + 0.5 * wave(t, Tl / 5, 1.6), hy * 0.6, -hy * 0.1 - 0.2 * hroll))
    add(p, "jaw", rot=(-0.6 - 1.0 * smooth(max(0.0, wave(t, Tl / 4, -0.9))), 0, 0))
    for k, (b, g) in enumerate(zip(TAILS, STIFF)):           # the lever sways slowly from its root
        if g:
            add(p, b, rot=(0.4 * g * wave(t, Tl / 4, -0.5 * k) - 0.3 * g,
                           g * (1.4 * wave(t, Tl, -0.9 * k) + 0.6 * wave(t, Tl / 2, 0.6 - 0.8 * k)), 0))
    tw = window(t, 6.15, 6.6, 0.1)                           # once in a while the little arms tremble
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(1.6 * wave(t, Tl / 2, -1.0 - 3 * o) + 1.0 * br + 5 * tw * tremor(t, (13.0, 17.3, 9.1), phase=o * 4), 0, 0))
        add(p, f"forearm_{s}", rot=(-2 + 1.8 * wave(t, Tl / 2, -1.7 - 3 * o) + 5 * tw * tremor(t, (15.1, 11.7, 8.3), phase=1 + o * 4), 0, 0))
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, -hyaw, -hroll))
    T.plant(p, "l")
    T.plant(p, "r", 0.0, -3.0)
    return p


# ------------------------------------------------------------------ voice
ROAR_T = 2.8
ROAR_RISE = tr((0, 0), (0.4, -0.35, ease_out), (0.75, 1.0, ease_out), (2.2, 0.85), (2.55, 0.1, ease_in), (2.8, 0.0))
# the short skull opens only so far: the bellows pulse around -20, irregular, never quite shut while it roars
ROAR_JAW = tr((0, 0), (0.4, -2), (0.55, -5, ease_out), (0.78, -22, ease_out), (1.0, -16), (1.22, -25), (1.43, -18),
              (1.68, -27), (1.9, -19), (2.15, -23), (2.45, -4), (2.8, 0, ease_out))
ROAR_SWEEP = tr((0, 0), (0.75, 0), (1.3, 7, ease_out), (1.9, -6), (2.3, -2), (2.8, 0))


def roar(t):
    p = {}
    up = float(ROAR_RISE(t)); a = max(0.0, up); c = max(0.0, -up) / 0.35
    sw = float(ROAR_SWEEP(t))
    env = window(t, 0.75, 2.25, 0.2)
    shiv = tremor(t) * env
    shk = decay(t, 2.25, 0.16, 4.0)                          # a quick shake of the head as the roar ends
    add(p, "body", rot=(-3 * a + 3 * c + 0.3 * shiv, 0.2 * sw, 0.15 * sw), pos=(0, -1.0 * a - 1.2 * c, 0.8 * a))
    T.neck(p, (10 * a - 6 * c + 0.8 * shiv, 0.5 * sw + 4 * shk, -0.2 * sw))
    add(p, "skull", rot=(6 * a - 3 * c + 1.1 * tremor(t, (9.1, 13.6, 5.8), phase=0.7) * env, 0.4 * sw + 5 * shk, -0.3 * sw - 6 * shk))
    add(p, "jaw", rot=(float(ROAR_JAW(t)) - 1.4 * tremor(t, (10.3, 14.9, 6.7), phase=1.9) * env, 0, 0))
    trail(p, t, lambda u: -3.0 * max(0.0, float(ROAR_RISE(u))) + 1.2 * max(0.0, -float(ROAR_RISE(u))), axis=0, delay=0.08)
    trail(p, t, lambda u: -0.4 * float(ROAR_SWEEP(u)) - 3.0 * decay(u, 2.25, 0.2, 4.0), delay=0.07)
    arms(p, -6 * a + 1.5 * shiv, 4 * a + 1.2 * shiv)
    alive(p, t, k=1.0 - 0.8 * smooth((t - 0.35) / 0.35) * (1 - smooth((t - 2.3) / 0.4)))
    return T.stand(p)


def call(t):
    """three low grunts, the mouth barely open, the throat and chest pumping and humming with each one"""
    p = {}
    k = float(tr((0, 0), (0.3, 1, ease_out), (2.2, 1), (2.6, 0, ease_in))(t))
    g = sum(window(t, c, c + 0.28, 0.07) for c in (0.5, 1.05, 1.6))
    hum = tremor(t, (11.3, 15.1, 8.3), (0.8, 0.45, 0.3)) * window(t, 0.45, 1.95, 0.12)
    add(p, "body", rot=(2 * k + 2 * g + 0.3 * hum, 0, 0), pos=(0, 0.8 * g, 0))
    T.neck(p, (6 * k + 3 * g + 0.6 * hum, 0, 0)); add(p, "skull", rot=(4 * k + 2 * g - 0.5 * hum, 0, 0))
    add(p, "jaw", rot=(-3 * k - 7 * g - 0.5 * hum, 0, 0))
    trail(p, t, lambda u: 1.5 * sum(window(u, c, c + 0.28, 0.07) for c in (0.5, 1.05, 1.6)), axis=0, delay=0.07)
    alive(p, t, k=1.0 - 0.6 * k)
    return T.stand(p)


def threat(t):
    """head low showing the horns from the front, a growl, a snort, a foot scraping the ground twice"""
    p = {}
    k = float(tr((0, 0), (0.35, 1, ease_out), (2.4, 1), (2.8, 0, ease_in))(t))
    snort = bump(t, 0.7, 0.06)
    growl = tremor(t, (10.1, 13.9, 7.1), (0.9, 0.5, 0.3)) * window(t, 0.3, 2.4, 0.2)
    weave = 3.0 * wave(t, 1.4) * window(t, 0.4, 2.4, 0.3)    # the horned head weaves while it warns
    add(p, "body", rot=(6 * k + 0.3 * growl, 0.4 * weave, 0), pos=(0, -3 * k, 0))
    T.neck(p, (-12 * k + 0.5 * growl, weave, 0)); add(p, "skull", rot=(-14 * k + 4 * snort + 0.6 * growl, 0.5 * weave, -0.4 * weave))
    add(p, "jaw", rot=(-3 * k - 4 * snort - 1.0 * growl, 0, 0))
    tail(p, pitch=3 * k)
    trail(p, t, lambda u: -1.2 * 3.0 * wave(u, 1.4) * window(u, 0.4, 2.4, 0.3), delay=0.08)
    alive_upper(p, t, k=0.5)
    T.plant(p, "l")
    sc = sum(window(t, c, c + 0.35, 0.08) for c in (1.0, 1.6))
    back = sum(smooth((t - c) / 0.3) * (1 - smooth((t - c - 0.3) / 0.08)) for c in (1.0, 1.6))
    T.plant(p, "r", 3 * sc, 6 * k - 14 * back, 0, -6 * sc, clear=-0.05)
    return p


# ------------------------------------------------------------------ combat: quick snaps and cuts
# the bite-and-pull: the hit at 0.45 s (Abelisaur BITE_PULL, tick 9)
ATT_LUNGE = tr((0, 0), (0.25, -0.35, ease_out), (0.45, 1, ease_in), (0.55, 1), (0.95, -1, ease_out), (1.3, -0.8),
               (1.8, 0, back_out))
ATT_JAW = tr((0, 0), (0.22, -30, ease_out), (0.38, -34), (0.45, -3, ease_in), (1.3, -4), (1.45, -14, ease_out), (1.62, -5),
             (1.8, 0, ease_out))


def pull_shake(t):
    """the rip back: two quick wrenches of the head, the first the widest"""
    return bump(t, 0.82, 0.08) - 0.7 * bump(t, 1.0, 0.08) + 0.35 * bump(t, 1.16, 0.07)


def attack(t):
    p = {}
    lunge = float(ATT_LUNGE(t)); a = max(0.0, lunge); b = max(0.0, -lunge)
    sh = pull_shake(t)
    add(p, "body", rot=(5 * a - 6 * b, 4 * sh, -2 * sh), pos=(0, -1.5 * a - 1.0 * b, -6 * a + 7 * b))
    T.neck(p, (-14 * a + 10 * b, 12 * sh, -3 * sh))
    add(p, "skull", rot=(-6 * a + 8 * b, 7 * sh, -10 * sh))
    add(p, "jaw", rot=(float(ATT_JAW(t)), 0, 0))
    trail(p, t, lambda u: -6 * pull_shake(u), delay=0.05)
    trail(p, t, lambda u: (lambda l: -3 * max(0, l) + 4 * max(0, -l))(float(ATT_LUNGE(u))), axis=0, delay=0.06)
    arms(p, -10 * a, 8 * a)
    alive(p, t, k=0.4)
    T.plant(p, "l", 0, -5 * a + 4 * b, 0, 0)
    T.plant(p, "r", 0, 3 * a - 6 * b, 0, 0)
    return p


# the snaps: the first lands at 0.2 s (SNAP, tick 4); each a little to a different side (it moves a lot sideways)
SNAPS = ((0.19, 4.0), (0.47, -3.5), (0.75, 2.0))


def attack_quick(t):
    p = {}
    out = sum(bump(t, c, 0.07) for c, _ in SNAPS)
    cock = sum(bump(t, c - 0.1, 0.05) for c, _ in SNAPS)
    side = sum(y * bump(t, c, 0.09) for c, y in SNAPS)
    jaw = sum(-26 * bump(t, c - 0.07, 0.055) for c, _ in SNAPS)
    settle = float(tr((0, 0), (0.75, 0), (0.95, 0, back_out))(t))
    add(p, "body", rot=(2 * out - 1.0 * cock, 0.4 * side, -0.3 * side), pos=(0, 0, -2.5 * out + 0.8 * cock + settle))
    T.neck(p, (-10 * out + 4 * cock, side, 0)); add(p, "skull", rot=(-4 * out + 2 * cock, 0.6 * side, -0.5 * side))
    add(p, "jaw", rot=(jaw, 0, 0))
    trail(p, t, lambda u: -0.8 * sum(y * bump(u, c, 0.09) for c, y in SNAPS), delay=0.05)
    trail(p, t, lambda u: -1.5 * sum(bump(u, c, 0.07) for c, _ in SNAPS), axis=0, delay=0.05)
    arms(p, -8 * window(t, 0.05, 0.85, 0.1))
    alive(p, t, k=0.5)
    return T.stand(p)


# the horn flick: the hit at 0.45 s (HOOK, tick 9)
HOOK_K = tr((0, 0), (0.3, 1, ease_out), (0.4, 1), (0.53, -0.6, ease_in), (0.78, -0.45), (1.2, 0, back_out))


def hook(t):
    p = {}
    k = float(HOOK_K(t)); a = max(0.0, k); b = max(0.0, -k)
    add(p, "body", rot=(3 * a, 6 * a - 6 * b, -1.5 * a + 1.5 * b))
    T.neck(p, (-10 * a + 6 * b, 14 * a - 18 * b, 0))
    add(p, "skull", rot=(-6 * a + 10 * b, 6 * a - 10 * b, 26 * a - 30 * b + 4 * decay(t, 0.55, 0.12, 5.0)))
    add(p, "jaw", rot=(-3 * b, 0, 0))
    trail(p, t, lambda u: (lambda kk: -7 * max(0, kk) + 8 * max(0, -kk))(float(HOOK_K(u))), delay=0.05)
    arms(p, -6 * a)
    alive(p, t, k=0.5)
    return T.stand(p)


def shove(t):
    """horns against the rival: head low, legs spread back, pushing; the pushes come in uneven surges and it strains"""
    p = {}
    k = float(tr((0, 0), (0.4, 1, ease_out), (2.2, 1), (2.7, 0, ease_in))(t))
    push = 0.5 + 0.3 * math.sin(2 * math.pi * 1.2 * (t - 0.4)) + 0.2 * math.sin(2 * math.pi * 1.9 * (t - 0.4) + 0.7)
    strain = tremor(t, (8.3, 12.7, 5.9), (0.8, 0.45, 0.3)) * window(t, 0.45, 2.2, 0.2)
    jostle = math.sin(2 * math.pi * 0.9 * t) * k
    add(p, "body", rot=(6 * k + 0.3 * strain, 1.0 * jostle, 1.6 * jostle), pos=(0, -4 * k, -2 * k * push))
    T.neck(p, (-16 * k + 0.5 * strain, -1.2 * jostle, 0)); add(p, "skull", rot=(-12 * k + 0.7 * strain, 0, -1.0 * jostle))
    add(p, "jaw", rot=(-3 * k - 0.8 * strain, 0, 0))
    tail(p, pitch=4 * k)
    trail(p, t, lambda u: -2.5 * math.sin(2 * math.pi * 0.9 * u) * float(tr((0, 0), (0.4, 1, ease_out), (2.2, 1), (2.7, 0, ease_in))(u)), delay=0.08)
    alive_upper(p, t, k=0.4)
    for s, sx in (("l", 1), ("r", -1)):
        add(p, f"thigh_{s}", rot=(0, 0, -1.6 * jostle))
    T.plant(p, "l", 0, 6 * k, 6 * k * push, 0)
    T.plant(p, "r", 0, 12 * k, 6 * k * push, 0)
    return p


def lock_on(t):
    """it stops, drops the head and stares with both forward eyes: nothing moves but a quick, shallow breath and the
    tail root, tense"""
    p = {}
    k = float(tr((0, 0), (0.25, 1, ease_out), (1.8, 1), (2.2, 0, ease_in))(t))
    br = wave(t, 0.55) * 0.5
    add(p, "body", rot=(5 * k + br, 0, 0), pos=(0, -3 * k + 0.2 * br, 0))
    T.neck(p, (-14 * k - 0.4 * br, 0, 0)); add(p, "skull", rot=(4 * k + 0.6 * bump(t, 0.32, 0.06), 0, 0))
    add(p, "jaw", rot=(-2 * k, 0, 0))
    tail(p, pitch=3 * k)
    trail(p, t, lambda u: 1.5 * wave(u, 1.1) * float(tr((0, 0), (0.25, 1, ease_out), (1.8, 1), (2.2, 0, ease_in))(u)), delay=0.09)
    arms(p, -6 * k + 0.8 * br, 0)
    return T.stand(p)


def hurt(t):
    """the flinch: a jolt away from the blow, the stiff tail whipped after it, gathered again with no hold"""
    p = {}
    e = math.exp(-(t / 0.14)) * smooth(t / 0.04)
    add(p, "body", rot=(5 * e, 3 * e, 3 * e), pos=(0, -0.8 * e, 2 * e))
    T.neck(p, (10 * e, -6 * e, 0)); add(p, "skull", rot=(6 * e, 0, 6 * e)); add(p, "jaw", rot=(-14 * e, 0, 0))
    trail(p, t, lambda u: 5 * math.exp(-(u / 0.18)) * smooth(u / 0.05), delay=0.04)
    trail(p, t, lambda u: -2.5 * math.exp(-(u / 0.18)) * smooth(u / 0.05), axis=0, delay=0.04)
    arms(p, -14 * e, 10 * e)
    alive(p, t, k=0.5)
    return T.stand(p)


# ------------------------------------------------------------------ fast movement
def skid_turn(t):
    """turning left at speed: leans into the curve, the outer foot skids, the stiff tail swings out wide and comes back
    late, past the middle"""
    p = {}
    kf = tr((0, 0), (0.15, 1, ease_out), (0.6, 1), (0.9, 0, back_out))
    k = float(kf(t))
    add(p, "body", rot=(5 * k, 18 * k, 12 * k), pos=(0, -3 * k, 0))
    T.neck(p, (-4 * k, 16 * k, -6 * k)); add(p, "skull", rot=(0, 8 * k, -4 * k))
    tail(p, yaw=-10 * k, pitch=2 * k)
    trail(p, t, lambda u: -5 * float(kf(u)), delay=0.06)
    T.plant(p, "l", 0, -8 * k, 6 * k, 0)
    T.plant(p, "r", 0, 10 * k, -4 * k, 0)
    for b in ("thigh_r", "shin_r"):
        add(p, b, rot=(0, 0, -5 * k))
    arms(p, -12 * k, 10 * k)
    return p


def skid_turn_r(t):
    return A._mirror(skid_turn(t))


def brake(t):
    """from the sprint: legs pushed forward, the body thrown back, the tail up as a counterweight; it rocks forward
    once past the rest and settles"""
    p = {}
    kf = tr((0, 0), (0.12, 1, ease_out), (0.5, 1), (0.9, 0, back_out))
    k = float(kf(t))
    add(p, "body", rot=(-9 * k, 0, 0), pos=(0, -2 * k, 4 * k))
    T.neck(p, (14 * k, 0, 0)); add(p, "skull", rot=(-6 * k + 3 * bump(t, 0.6, 0.1), 0, 0)); add(p, "jaw", rot=(-6 * k, 0, 0))
    tail(p, pitch=4 * k)
    trail(p, t, lambda u: 3 * float(kf(u)), axis=0, delay=0.06)
    T.plant(p, "l", 0, -16 * k, -10 * k, 0)
    T.plant(p, "r", 0, -6 * k, -6 * k, 0)
    arms(p, -20 * k, 15 * k)
    return p


# ------------------------------------------------------------------ the fight (the common set, its way)
GUARD_T = 1.6


def guard(t):
    """light on its feet: low, the horns presented, the head weaving side to side, the weight bouncing, the little arms
    tense; it waits to dart in"""
    p = {}
    L = GUARD_T
    bounce = wave(t, L / 2)
    weave = wave(t, L)
    growl = tremor(t, (16 / L, 22 / L, 11 / L), (0.7, 0.4, 0.3))     # harmonics of the loop: it closes
    hroll = 2.0 * weave
    add(p, "body", rot=(6 + 0.8 * bounce, 2.5 * weave, hroll), pos=(0, -3.4 + 0.6 * bounce, -0.4 * bounce))
    T.neck(p, (-11 - 0.8 * wave(t, L / 2, -0.6) + 0.4 * growl, -2.5 * weave + 6 * wave(t, L, -0.9), -0.8 * hroll))
    add(p, "skull", rot=(-6 + 0.6 * wave(t, L / 2, -1.2) + 0.5 * growl, 3 * wave(t, L, -1.5), -2 * wave(t, L, -1.3)))
    add(p, "jaw", rot=(-3 - 1.5 * max(0.0, wave(t, L / 2, -0.5)) - 0.8 * growl, 0, 0))
    for k, (b, g) in enumerate(zip(TAILS, STIFF)):
        if g:
            add(p, b, rot=(-2.0 * g + 0.4 * g * wave(t, L / 2, -0.6 * k), -3.5 * g * wave(t, L, -0.8 - 0.7 * k), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(-10 + 1.5 * wave(t, L / 2, -1 - 3 * o) + 0.6 * tremor(t, (24 / L, 31 / L, 19 / L), (0.6, 0.4, 0.3), phase=o * 3), 0, 0))
        add(p, f"forearm_{s}", rot=(8 + 1.5 * wave(t, L / 2, -1.6 - 3 * o), 0, 0))
        sx = 1 if s == "l" else -1
        add(p, f"thigh_{s}", rot=(0, -2.5 * weave, -hroll + 3.0 * sx))
    T.plant(p, "l", 0.0, 3.0)
    T.plant(p, "r", 0.0, -4.0)
    return p


STRAFE_T = 1.0


def strafe(t, side):
    """quick crossing steps round the rival, the body facing it and leaning into the travel, the head on it; the stiff
    tail swings out the other way like a rudder"""
    d = 1.0 if side == "left" else -1.0                 # + model x is the animal's left in game
    ph = (t / STRAFE_T) % 1.0; w = 2 * math.pi * ph; p = {}
    lean = -3.5 * d
    sk = landing(2 * ph + 0.1)                           # a skip: each foot lands hard, the body springs up slowly
    add(p, "body", rot=(6 + 0.8 * sk, 0, lean + 1.2 * math.sin(2 * w)), pos=(0, -3.0 + 1.1 * sk, 0))
    T.neck(p, (-10 - 0.8 * landing(2 * ph + 0.02), 2.5 * d * math.sin(w), -0.7 * lean - 0.8 * math.sin(2 * w - 0.3)))
    add(p, "skull", rot=(-5 + 0.5 * math.sin(2 * w - 1.0), 0, 0.5 * d))
    add(p, "jaw", rot=(-3 - 0.8 * tremor(t, (13 / STRAFE_T, 19 / STRAFE_T, 9 / STRAFE_T), (0.7, 0.4, 0.3)), 0, 0))
    for k, (b, g) in enumerate(zip(TAILS, STIFF)):
        if g:
            add(p, b, rot=(-1.5 * g, g * (-5.0 * d - 1.5 * math.sin(2 * w - 0.8 - 0.7 * k)), 0))
    for s, o in SIDES:
        sx = 1 if s == "l" else -1
        u = (ph + o) % 1.0
        add(p, f"arm_{s}", rot=(-10 + 2.5 * math.sin(w + o * 2 * math.pi - 2.0), 0, 0))
        if u < 0.42:                                    # the foot lifts and swings across, toward the travel
            sw = u / 0.42
            ly = 7.0 * math.sin(math.pi * sw) ** 1.2
            add(p, f"thigh_{s}", rot=(0, 0, d * 8.0 * (sw - 0.5) + 2.5 * sx - lean))
            T.plant(p, s, ly, 0.0, 8 * math.sin(math.pi * sw), -18 * math.sin(math.pi * sw), clear=0.8 * math.sin(math.pi * sw) ** 0.5)
        else:                                           # planted, the body passing over it
            st = (u - 0.42) / 0.58
            add(p, f"thigh_{s}", rot=(0, 0, -d * 8.0 * (st - 0.5) + 2.5 * sx - lean))
            T.plant(p, s)
    return p


def strafe_left(t): return strafe(t, "left")
def strafe_right(t): return strafe(t, "right")


TURN_T = 1.2


def turn(t, side):
    """stepping round on the spot, quick little steps: the head snaps into the turn first, the hips follow, the stiff
    tail swings out the other way. A + yaw swings the head to the animal's RIGHT in game: a left turn leads with - yaw"""
    d = 1.0 if side == "left" else -1.0
    ph = (t / TURN_T) % 1.0; w = 2 * math.pi * ph; p = {}
    lead = -d
    h = (2 * ph) % 1.0                                  # the hawk again: at every step the head jumps ahead into the
    jump = smooth(h / 0.12) * (1 - smooth((h - 0.12) / 0.88))     # turn and the body catches up under it
    add(p, "body", rot=(0, lead * (3.5 + 1.5 * math.sin(w)), 2.4 * math.sin(w + 0.3)), pos=(0, -0.6 + 0.5 * math.cos(2 * w), 0))
    T.neck(p, (-1.0, lead * (9.0 + 6.0 * jump), -1.5 * math.sin(w + 0.3)))
    add(p, "skull", rot=(0.8 * jump, lead * (6.0 + 4.0 * jump), -0.6 * math.sin(w)))
    add(p, "jaw", rot=(-0.8, 0, 0))
    for k, (b, g) in enumerate(zip(TAILS, STIFF)):
        if g:
            add(p, b, rot=(0.4 * g * math.sin(2 * w - 0.6 * k), g * (-lead * 6.0 - 2.0 * math.sin(w - 0.8 * (k + 1))), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(3 * math.sin(w + o * 2 * math.pi - 2.0), 0, 0))
        u = (ph + o) % 1.0
        if u < 0.4:
            sw = u / 0.4
            ly = 7.0 * math.sin(math.pi * sw) ** 1.2
            dz = -3.0 * math.cos(math.pi * sw)
            toe = -22 * math.sin(math.pi * sw); meta = 12 * math.sin(math.pi * sw); clear = 1.0 * math.sin(math.pi * sw) ** 0.5
            add(p, f"thigh_{s}", rot=(0, lead * 6.0 * math.sin(math.pi * sw), 0))
        else:
            ly, dz, toe, meta, clear = 0.0, 3.0 - 6.0 * ((u - 0.4) / 0.6), 0.0, 0.0, -0.05
        add(p, f"thigh_{s}", rot=(0, -lead * 3.5, -2.4 * math.sin(w + 0.3)))
        T.plant(p, s, ly, dz, meta, toe, clear)
    return p


def turn_left(t): return turn(t, "left")
def turn_right(t): return turn(t, "right")


FEINT_T = 1.0


def feint(t):
    """a ram that stops short: the horns dip and it jerks forward, stops dead a step short, snorts and pulls back"""
    p = {}
    n = tr((0, (0, 0)), (0.18, (5, 2), ease_out), (0.36, (-14, -1), ease_in), (0.46, (-12, 0)), (1.0, (0, 0), back_out))(t)
    lunge = float(tr((0, 0), (0.18, 1.5, ease_out), (0.36, -5.0, ease_in), (0.48, -4.5), (1.0, 0, back_out))(t))
    snort = bump(t, 0.42, 0.05)
    add(p, "body", rot=(-0.3 * n[0], 0.3 * n[1], 0), pos=(0, -1.2 * smooth(t / 0.3) * (1 - smooth((t - 0.5) / 0.4)), lunge))
    T.neck(p, (n[0], n[1], 0)); add(p, "skull", rot=(0.6 * n[0] + 3 * snort, 0.5 * n[1], 0))
    add(p, "jaw", rot=(-2 - 6 * snort, 0, 0))
    trail(p, t, lambda u: 2.5 * bump(u, 0.38, 0.1), axis=0, delay=0.05)
    trail(p, t, lambda u: 2.0 * decay(u, 0.36, 0.18, 3.0), delay=0.05)
    arms(p, -6 * smooth(t / 0.2) * (1 - smooth((t - 0.6) / 0.3)))
    alive(p, t, k=0.5)
    return T.stand(p)


BLOCK_T = 0.8


def block(t):
    """it meets the blow with the braced skull: the head dips to turn the horn boss into it, the jolt runs back through
    the neck into the body, the stiff tail whips"""
    p = {}
    dip = float(tr((0, 0), (0.07, 1, ease_out), (0.12, 1), (0.8, 0, ease_out))(t))
    e = math.exp(-max(0.0, t - 0.08) / 0.18) * smooth((t - 0.06) / 0.04)
    add(p, "body", rot=(3 * e, -4 * e, 3 * e), pos=(0, -0.8 * e, 2.5 * e))
    T.neck(p, (-6 * dip + 6 * e, -6 * e, 2 * e)); add(p, "skull", rot=(-8 * dip + 9 * e, -5 * e, 6 * e))
    add(p, "jaw", rot=(-6 * e, 0, 0))
    trail(p, t, lambda u: 6 * math.exp(-max(0.0, u - 0.08) / 0.22) * smooth((u - 0.06) / 0.04), delay=0.04)
    alive_upper(p, t, k=0.5)
    return T.stand(p)


RECOIL_T = 0.9


def recoil(t):
    """its blow was turned: the horned head knocked aside, a skip back on the left foot, a shake to clear the head"""
    p = {}
    e = math.exp(-max(0.0, t - 0.04) / 0.18) * smooth(t / 0.04)
    wob = decay(t, 0.1, 0.16, 4.5)
    add(p, "body", rot=(-3 * e, 5 * e, -3 * e), pos=(0, -0.6 * e, 3.0 * e))
    clear_head = decay(t, 0.42, 0.12, 6.0)                # then a quick shake of the horned head to clear it
    T.neck(p, (6 * e, 14 * e + 4 * wob, -5 * e)); add(p, "skull", rot=(4 * e, 10 * e + 5 * wob + 3 * clear_head, -10 * e + 9 * clear_head))
    add(p, "jaw", rot=(-10 * e, 0, 0))
    trail(p, t, lambda u: -6 * math.exp(-max(0.0, u - 0.04) / 0.22) * smooth(u / 0.04), delay=0.04)
    alive_upper(p, t, k=0.5)
    T.plant(p, "r")
    lift = steps(t, 0.06, 0.36, 7.0)                     # a light skip back on the left foot
    T.plant(p, "l", lift, 5 * smooth((t - 0.06) / 0.3), 0, -12 * lift / 7.0, clear=-0.05)
    return p


SUBMIT_T = 2.2


def submit(t):
    """beaten: the horns go down and away, the tail drops, it crouches and turns aside (then it runs)"""
    p = {}
    k = float(tr((0, 0), (0.5, 1, ease_out), (2.2, 1))(t))
    turn_ = float(tr((0, 0), (0.6, 0), (1.4, 1, ease_out), (2.2, 1))(t))
    whine = bump(t, 0.8, 0.12)
    add(p, "body", rot=(-4 * k, 12 * turn_, 0), pos=(0, -3 * k, 0))
    T.neck(p, (-18 * k, 10 * turn_, 0)); add(p, "skull", rot=(-6 * k, 6 * turn_, 8 * turn_)); add(p, "jaw", rot=(-2 - 6 * whine, 0, 0))
    tail(p, pitch=5 * k)
    trail(p, t, lambda u: -4 * float(tr((0, 0), (0.6, 0), (1.4, 1, ease_out), (2.2, 1))(u)), delay=0.08)
    arms(p, 8 * k, -6 * k)
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, -12 * turn_, 0))
    alive_upper(p, t, k=0.8, period=1.1)
    T.plant(p, "l")                                     # a runner: it hops round on the right foot, ready to bolt
    hop = steps(t, 0.75, 1.2, 7.0)
    T.plant(p, "r", hop, -4 * smooth((t - 0.75) / 0.45), 8 * hop / 7.0, -14 * hop / 7.0, clear=-0.05)
    return p


# ------------------------------------------------------------------ transitions and tiredness
LIE_DOWN_T = 2.0


def lie_down(t):
    """the legs fold, the heavy chest goes down first, a small bump as the keel lands, the head looks down at it"""
    p = {}
    k = float(tr((0, 0), (0.25, 0.05), (1.35, 0.92, ease_in), (1.55, 1.03), (2.0, 1.0, ease_out))(t))
    look = float(tr((0, 0), (0.35, 1, ease_out), (1.3, 1), (2.0, 0, ease_out))(t))
    fold(p, k)
    T.neck(p, (-6 * look, 0, 0)); add(p, "skull", rot=(-4 * look, 0, 0))
    land = bump(t, 1.5, 0.09)
    add(p, "body", rot=(0.8 * land, 0, 0)); add(p, "jaw", rot=(-3 * land, 0, 0))
    trail(p, t, lambda u: 2.0 * bump(u, 1.5, 0.14), axis=0, delay=0.06)
    alive_upper(p, t, k=0.5)
    return ground_fit(S, p)


GET_UP_T = 2.0


def get_up(t):
    """a push with the legs, the head thrown forward for balance, a little wobble on the long legs"""
    p = {}
    k = float(tr((0, 1.0), (0.4, 1.02), (1.2, 0.05, ease_out), (1.45, -0.02), (2.0, 0.0, ease_out))(t))
    push = bump(t, 0.55, 0.18)
    fold(p, max(0.0, k))
    T.neck(p, (-12 * push, 0, 0)); add(p, "skull", rot=(-6 * push, 0, 0))
    wob = decay(t, 1.25, 0.22, 2.8)
    add(p, "body", rot=(0, 0, 2.5 * wob))
    trail(p, t, lambda u: -3.0 * decay(u, 1.25, 0.25, 2.8), delay=0.07)
    alive_upper(p, t, k=0.5)
    return ground_fit(S, p)


WALK_TIRED_T = 2.4


def walk_tired(t):
    """the walk with nothing left: shorter steps (the cycle the Java plays at 56 px every 2.4 s), the head hanging, the
    mouth open panting, the stiff tail sagging"""
    p = gait2(t, WALK_TIRED_T, 56, 0.66, 7, 1.6, lean=2, drop=1.5, head=-9, roll=6.0, yaw=3.5, whip=0.8, arm_amp=2.0, tail_up=1.5)
    pant = wave(t, WALK_TIRED_T / 4)
    add(p, "jaw", rot=(-9 - 5 * max(0.0, pant), 0, 0)); T.neck(p, (-1.2 * wave(t, WALK_TIRED_T / 4, -0.5), 0, 0))
    return p


IDLE_TIRED_T = 2.4


def idle_tired(t):
    """spent after a sprint: the flanks heave fast, the short jaw hangs open, the head low, the arms limp"""
    p = {}
    L = IDLE_TIRED_T
    pant = wave(t, L / 4)
    shift = wave(t, L, 0.3)
    add(p, "body", rot=(2.5 + 1.8 * pant, 0, 1.2 * shift), pos=(0, -1.2 + 0.7 * pant, 0))
    T.neck(p, (-10 - 1.6 * wave(t, L / 4, -0.6), 2 * wave(t, L, 0.5), -0.8 * shift))
    add(p, "skull", rot=(-4 - 1.1 * wave(t, L / 4, -1.2), 1.5 * wave(t, L, -0.5), 0))
    add(p, "jaw", rot=(-10 - 5 * max(0.0, wave(t, L / 4, -0.4)), 0, 0))
    for k, (b, g) in enumerate(zip(TAILS, STIFF)):
        if g:
            add(p, b, rot=(2.5 * g + 0.4 * g * pant, 1.5 * g * wave(t, L, -0.8 * (k + 1)), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(8 + 2.0 * wave(t, L / 4, -0.8 - o), 0, 0)); add(p, f"forearm_{s}", rot=(4, 0, 0))
        add(p, f"thigh_{s}", rot=(0, 0, -1.2 * shift))
    return T.stand(p)


# ------------------------------------------------------------------ its signature blows (the study: horns and skull)
RAM_T = 1.6
# the horns land at 0.75 s (tick 15): lower the head and rock back, two quick strides of charge, the impact, drive
# through, back off and settle
RAM_GO = tr((0, 0), (0.38, -1.0, ease_out), (0.73, 1.0, ease_in), (0.75, 1.0), (0.95, 1.1, ease_out), (1.2, 0.6),
            (1.6, 0.0, back_out))
RAM_HEAD = tr((0, 0), (0.3, 1.0, ease_out), (1.0, 1.0), (1.45, 0.0, ease_out), (1.6, 0.0))


def ram(t):
    p = {}
    go = float(RAM_GO(t)); fwd = max(0.0, go); back = max(0.0, -go)
    hd = float(RAM_HEAD(t))
    hit = math.exp(-max(0.0, t - 0.75) / 0.09) * smooth((t - 0.73) / 0.03)       # the jolt of the impact
    shock = tremor(t, (11.3, 16.9, 7.7), (1.0, 0.6, 0.4)) * window(t, 0.76, 1.0, 0.07)
    add(p, "body", rot=(-4 * hd - 2 * fwd + 3 * hit + 0.4 * shock, 0, 0), pos=(0, -2.5 * hd - 1.5 * fwd + 0.6 * hit, 3.5 * back - 9 * fwd + 2.5 * hit))
    T.neck(p, (-12 * hd - 4 * fwd + 5 * hit + 0.6 * shock, 0, 0))
    add(p, "skull", rot=(-10 * hd + 8 * hit + 0.8 * shock, 0, 0))
    add(p, "jaw", rot=(-2 * hd - 6 * hit, 0, 0))
    trail(p, t, lambda u: (lambda g: -3.5 * max(0.0, -g) + 2.5 * max(0.0, g))(float(RAM_GO(u)))
          - 4 * math.exp(-max(0.0, u - 0.75) / 0.12) * smooth((u - 0.73) / 0.03), axis=0, delay=0.06)
    trail(p, t, lambda u: 4 * decay(u, 0.76, 0.2, 3.5), delay=0.06)
    arms(p, -14 * fwd + 6 * hit, 10 * fwd)
    alive_upper(p, t, k=0.4)
    # the charge: the right foot strides forward, the left drives off; after the hit the right comes back under it
    r_up = steps(t, 0.38, 0.66, 9.0) + steps(t, 1.05, 1.42, 6.0)
    r_z = -10 * smooth((t - 0.38) / 0.28) + 10 * smooth((t - 1.05) / 0.37)
    T.plant(p, "r", r_up, r_z + 3.5 * back, 10 * math.sin(math.pi * min(1, max(0, (t - 0.38) / 0.28))), -18 * r_up / 9.0,
            clear=0.8 * min(1.0, r_up / 3.0) - 0.05)
    l_push = smooth((t - 0.45) / 0.25) * (1 - smooth((t - 1.0) / 0.45))
    T.plant(p, "l", 0, 3.5 * back + 6 * l_push, 22 * l_push, 8 * l_push)
    return p


HEAD_CLASH_T = 2.2
# the heads meet at 0.45 s (tick 9): brace, impact (the jolt runs down the neck into the body), shove in surges, part
CL_BRACE = tr((0, 0), (0.32, 1, ease_out), (1.75, 1), (2.2, 0, ease_out))


def head_clash(t):
    p = {}
    br_ = float(CL_BRACE(t))
    drive = smooth((t - 0.32) / 0.12) * (1 - smooth((t - 0.45) / 0.05))
    hit = math.exp(-max(0.0, t - 0.45) / 0.12) * smooth((t - 0.43) / 0.03)
    shock = tremor(t, (10.7, 15.3, 7.3), (1.0, 0.6, 0.4)) * window(t, 0.46, 0.85, 0.08)
    sh = window(t, 0.7, 1.7, 0.2)
    surge = sh * (0.55 + 0.3 * math.sin(2 * math.pi * 1.3 * (t - 0.7)) + 0.15 * math.sin(2 * math.pi * 2.3 * (t - 0.7) + 1.1))
    strain = tremor(t, (8.9, 13.1, 6.1), (0.7, 0.4, 0.3)) * sh
    jostle = math.sin(2 * math.pi * 0.8 * (t - 0.7)) * sh
    add(p, "body", rot=(-5 * br_ + 3 * hit + 0.4 * shock + 0.3 * strain, 1.5 * jostle, 2.0 * jostle),
        pos=(0, -3.5 * br_, -3 * drive + 4 * hit - 4 * surge))
    T.neck(p, (-12 * br_ + 6 * hit + 0.7 * shock + 0.4 * strain, -2 * jostle, 0))
    add(p, "skull", rot=(-9 * br_ + 10 * hit + 0.9 * shock + 0.5 * strain, 0, -1.5 * jostle))
    add(p, "jaw", rot=(-2 * br_ - 8 * hit - 0.6 * strain, 0, 0))
    trail(p, t, lambda u: -4.5 * math.exp(-max(0.0, u - 0.45) / 0.15) * smooth((u - 0.43) / 0.03) - 2.0 * float(CL_BRACE(u)), axis=0, delay=0.05)
    trail(p, t, lambda u: 3 * decay(u, 0.46, 0.18, 4.0) - 2.5 * math.sin(2 * math.pi * 0.8 * (u - 0.7)) * window(u, 0.7, 1.7, 0.2), delay=0.07)
    arms(p, -12 * br_ + 4 * hit, 8 * br_)
    alive_upper(p, t, k=0.4)
    for s, sx in (("l", 1), ("r", -1)):                 # legs spread wide and planted back: braced
        add(p, f"thigh_{s}", rot=(0, 0, 4 * sx * br_ - 2.0 * jostle))
    T.plant(p, "l", 0, 6 * br_ + 2 * hit, 18 * surge, 6 * surge)
    T.plant(p, "r", 0, 2 * br_ + 2 * hit, 18 * surge, 6 * surge)
    return p


# ------------------------------------------------------------------ the fluid layer over the rest of the set
def _with_breath(fn, k=0.5, period=2.4, slow=None):
    def g(t):
        p = fn(t)
        alive_upper(p, t, k=k, period=period, slow=slow)
        return p
    g.__name__ = fn.__name__
    g.__doc__ = fn.__doc__
    return g


def _with_tail_follow(fn, k=0.5):
    """breath plus a tail that answers the body's turns late (from the body yaw the pose itself sets)"""
    def g(t):
        p = fn(t)
        alive_upper(p, t, k=k)
        yaw_of = lambda u: fn(max(0.0, u)).get("body", ([0, 0, 0],))[0][1]
        trail(p, t, lambda u: -0.4 * yaw_of(u), gain=(0.6, 0.5, 0.25, 0.05, 0.0), delay=0.1)
        return p
    g.__name__ = fn.__name__
    return g


look_back = _with_tail_follow(A.look_back, 0.6)
sniff = _with_breath(A.sniff, 0.5)
shake = _with_breath(A.shake, 0.3)
yawn = _with_breath(A.yawn, 0.4)
stretch = _with_breath(A.stretch, 0.4)
horn_rub = _with_tail_follow(A.horn_rub, 0.5)
eat = _with_breath(A.eat, 0.4)
drink = _with_breath(A.drink, 0.3)
beg = _with_breath(A.beg, 0.5, period=2.0, slow=2.0)
tame = _with_breath(A.tame, 0.5)
arm_twitch = _with_breath(A.arm_twitch, 0.4, period=1.2)

# existing names -> their fluid version (rebound in carnoanims.ANIMS; lengths and hit times unchanged)
REBIND = {
    "idle": idle, "walk": walk, "run": run, "stalk": stalk, "skid_turn": skid_turn, "skid_turn_r": skid_turn_r,
    "brake": brake, "lock_on": lock_on, "attack_quick": attack_quick, "attack": attack, "shove": shove, "hook": hook,
    "threat": threat, "roar": roar, "call": call, "hurt": hurt, "look_back": look_back, "sniff": sniff, "shake": shake,
    "yawn": yawn, "stretch": stretch, "horn_rub": horn_rub, "eat": eat, "drink": drink, "beg": beg, "tame": tame,
    "arm_twitch": arm_twitch,
}

# the new ones: name -> (fn, length, loop, category, when)
NEW = {
    "guard": (guard, GUARD_T, True, "Duelo", "em guarda: baixo, chifres à frente, a cabeça balança de lado, o peso pulando"),
    "strafe_left": (strafe_left, STRAFE_T, True, "Duelo", "passos cruzados rápidos para a esquerda em volta do rival"),
    "strafe_right": (strafe_right, STRAFE_T, True, "Duelo", "passos cruzados rápidos para a direita em volta do rival"),
    "turn_left": (turn_left, TURN_T, True, "Movimento", "girando no lugar para a esquerda (passinhos rápidos)"),
    "turn_right": (turn_right, TURN_T, True, "Movimento", "girando no lugar para a direita"),
    "feint": (feint, FEINT_T, False, "Duelo", "finta: a investida que para curta, bufa e recua"),
    "block": (block, BLOCK_T, False, "Duelo", "apara o golpe com o crânio reforçado e os chifres"),
    "recoil": (recoil, RECOIL_T, False, "Duelo", "o golpe foi aparado: a cabeça vai de lado, um pulinho atrás"),
    "submit": (submit, SUBMIT_T, False, "Duelo", "perdeu: abaixa os chifres e a cauda, vira de lado e foge"),
    "lie_down": (lie_down, LIE_DOWN_T, False, "Descanso", "deitando (de pé para sentado)"),
    "get_up": (get_up, GET_UP_T, False, "Descanso", "levantando (de sentado para de pé)"),
    "idle_tired": (idle_tired, IDLE_TIRED_T, True, "Parado", "parado cansado, ofegando rápido"),
    "walk_tired": (walk_tired, WALK_TIRED_T, True, "Movimento", "andando cansado depois de uma arrancada"),
    "ram": (ram, RAM_T, False, "Combate", "investida de chifres: abaixa a cabeça, dois passos de carga, cabeçada (golpe em 0,75 s)"),
    "head_clash": (head_clash, HEAD_CLASH_T, False, "Duelo", "choque de cabeças com outro: firma, impacto (0,45 s), empurra"),
}
