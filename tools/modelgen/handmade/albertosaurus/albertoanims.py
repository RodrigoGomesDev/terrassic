"""Albertosaurus animations, from its own study (docs/estudos/13_PREDADORES_1_10.md, "No jogo" and "Animações além do
padrão"). The plumbing is shared (anim2: easing, leg IK, export; theropod.Plan: plant/stand/lie and the T. rex poses
the template gives for the quiet gestures); the set follows the Daspletosaurus pilot (daspleanims.py) and every pose
that makes this animal is its own:
- the runner: a long, light stride on long legs, little roll, the head level and forward, the thin tail whipping;
  a real run and a longer, flatter SPRINT for the long chase; the juveniles' DRIVE, a banked run in an arc with the
  head low (they push the prey toward the adults);
- the pack: an adult calls the others before the hunt ("call_pack", head up, the throat pulsing) and they answer
  ("answer"); the adults wait crouched for the prey the young drive in ("ambush_crouch");
- the bite: quick and light, it shuts and lets go ("attack"); a snap without stopping ("snap_bite", upper body only,
  over the run); in a duel it steps aside ("sidestep") and bites the rival's neck as it passes ("pass_bite");
- after the long chase it stands panting, mouth wide, flanks heaving ("pant").
The fluid rules of docs/estudos/08 (breathing under everything, envelopes, three beats, the tail late). Signs on this
rig: body +x = nose up; neck/skull -x = down; jaw -x = open; tail pitch + = down; a + yaw swings the head to the
animal's RIGHT in game.
"""
import math
import os
import sys
_H = os.path.dirname(os.path.abspath(__file__))
_E = os.path.join(_H, "..", "_engine")
sys.path[:0] = [_H, _E, os.path.join(_E, "plans")]
import proto as P  # noqa: E402
import alberto  # noqa: E402
import theropod  # noqa: E402
from anim2 import add, Track, smooth, ease_out, ease_in, back_out, lowest  # noqa: E402
from theropod import window, W, SIDES  # noqa: E402

TAILS = alberto.TAILS
BEND = (0.9, 0.95, 0.9, 0.8, 0.7)         # the thin tail bends all along, the tip as much as the root
SADDLE = ("hide", "fur", "strap", "iron", "bone")
K = 0.8                                   # this rig against the T. rex the template's poses were written on


def model():
    m = alberto.build(saddle_on=True); P.pack(m, alberto.TEX_W); return m.spec()


S = model()
T = theropod.Plan(S, K=K, necks=("neck1", "neck2"), tails=TAILS, lie_drop=27.0, lie_ankle_y=4.4 * K, arms=0.8, jaw=0.85)
BASE = T.anims()


def tr(*keys): return Track(keys)


# ------------------------------------------------------------------ helpers
def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def tremor(t, f=(7.1, 10.9, 4.9), amp=(1.0, 0.55, 0.35), phase=0.0):
    """an organic shiver: three sines at frequencies that never line up"""
    return sum(a * math.sin(2 * math.pi * fr * t + phase * (i + 1) + 1.3 * i) for i, (fr, a) in enumerate(zip(f, amp)))


def bump(t, c, w):
    return math.exp(-((t - c) / w) ** 2)


def decay(t, at, tau, f):
    return math.exp(-max(0.0, t - at) / tau) * math.sin(2 * math.pi * f * (t - at)) * smooth((t - at + 0.02) / 0.05)


def steps(t, a, b, h):
    u = min(1.0, max(0.0, (t - a) / (b - a)))
    return h * math.sin(math.pi * u) ** 1.3


def landing(x):
    """-1 just after a heel strike, +1 mid-stance: the drop comes fast, the rise slow"""
    x %= 1.0
    return -1.0 + 2.0 * smooth(x / 0.26) if x < 0.26 else 1.0 - 2.0 * smooth((x - 0.26) / 0.74)


def tail(p, yaw=0.0, pitch=0.0):
    for b, k in zip(TAILS, BEND):
        add(p, b, rot=(pitch * k, yaw * k, 0))


def trail(p, t, fn, gain=BEND, delay=0.07, axis=1, loop=None):
    """follow-through down the tail: bone k takes fn(t - (k+1)*delay) * gain[k]"""
    for k, b in enumerate(TAILS):
        u = t - delay * (k + 1)
        v = fn(u % loop if loop else max(0.0, u)) * gain[k]
        r = [0.0, 0.0, 0.0]; r[axis] = v
        add(p, b, rot=tuple(r))


def arms(p, a=0.0, f=0.0):
    for s, _ in SIDES:
        add(p, f"arm_{s}", rot=(a, 0, 0)); add(p, f"forearm_{s}", rot=(f, 0, 0))


def alive_upper(p, t, k=1.0, period=3.0, slow=None):
    """the breath without the hips (safe after the feet are planted); in a loop, `slow` = a period that divides it"""
    s1, s2 = (slow, slow) if slow else (period * 1.5, period * 2)
    T.neck(p, (-0.5 * k * wave(t, period, -0.5), 0, 0))
    add(p, "skull", rot=(-0.35 * k * wave(t, period, -1.0), 0, 0))
    add(p, "jaw", rot=(-0.4 * k * max(0.0, wave(t, period, -0.6)), 0, 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(1.4 * k * wave(t, period, -0.8 - o), 0, 0))
        add(p, f"forearm_{s}", rot=(1.2 * k * wave(t, s1, -1.4 - o), 0, 0))
    for i, (b, g) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(0.4 * k * g * wave(t, period, -0.5 * i), 1.0 * k * g * wave(t, s2, -0.7 * i), 0))


def alive(p, t, k=1.0, period=3.0):
    """the breathing layer under every one-shot (before the feet are planted: it moves the body)"""
    br = wave(t, period)
    add(p, "body", rot=(0.6 * k * br, 0, 0), pos=(0, 0.3 * k * br, 0))
    alive_upper(p, t, k, period)
    return br


def ground_fit(p):
    """the lowest point on the ground; the saddle does not count (an unsaddled one must not float)"""
    lo = lowest(S, p, skip_mats=("teeth", "teeth_lo") + SADDLE)
    add(p, "root", pos=(0, -lo, 0))
    return p


def regrounded(fn):
    """a template pose that lies on the ground, re-fitted without the saddle"""
    def g(t):
        return ground_fit(fn(t))
    g.__name__ = fn.__name__
    return g


def with_breath(fn, k=0.5, period=3.0, slow=None):
    def g(t):
        p = fn(t)
        alive_upper(p, t, k=k, period=period, slow=slow)
        return p
    g.__name__ = fn.__name__
    return g


# ------------------------------------------------------------------ the gait: heavy, rolling, the head still
def gait(t, Tc, stride, duty, lift, bob, lean=0.0, drop=0.0, head=0.0, roll=5.5, yaw=3.0, whip=1.0, splay=2.5,
         still=0.9, stance_clear=-0.05, arm_amp=3.0, tail_up=0.0, bank=0.0, turn=0.0):
    """bank: the body leans into a turn (deg, + = to its right); turn: the body and head swing into it"""
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    b2 = landing(2 * ph + 0.06)
    hroll = roll * math.sin(w + 0.25) + bank
    hyaw = yaw * math.sin(w - 0.6) + turn
    add(p, "body", rot=(lean + 1.1 * b2, hyaw, hroll), pos=(0, bob * b2 - 0.6 - drop, 0))
    T.neck(p, (head - lean * still - 1.1 * still * landing(2 * ph - 0.03), -0.9 * hyaw - 1.0 * math.sin(w - 1.4) + 2.2 * turn,
               -0.8 * hroll))
    add(p, "skull", rot=(-head * 0.3 + 0.6 * landing(2 * ph - 0.12), -0.1 * hyaw + 0.6 * math.sin(w - 2.0),
                         -0.25 * hroll + 0.6 * math.sin(w - 1.2)))
    add(p, "jaw", rot=(-0.6 - 0.6 * max(0.0, landing(2 * ph - 0.2)), 0, 0))
    for k, (b, g) in enumerate(zip(TAILS, BEND)):          # a slow wide wave down the whole tail, late
        lag = 0.55 * (k + 1)
        add(p, b, rot=(tail_up * g - 0.8 * g * landing(2 * ph - 0.08 * (k + 1)),
                       -2.4 * whip * g * (1.0 + 0.25 * k) * math.sin(w - 0.6 - lag) - 1.6 * turn * g, 0.6 * whip * g * math.sin(w - 0.4 - lag)))
    for s, o in SIDES:
        f = w + o * 2 * math.pi
        add(p, f"arm_{s}", rot=(arm_amp * math.sin(f - 2.0) + 1.5 * landing(2 * ph - 0.25), 0, 0))
        add(p, f"forearm_{s}", rot=(1.2 * arm_amp * math.sin(f - 2.6), 0, 0))
    for s, o in SIDES:
        sx = 1 if s == "l" else -1
        u = (ph + o) % 1.0
        swing = 0.0 if u < duty else math.sin(math.pi * (u - duty) / (1 - duty))
        add(p, f"thigh_{s}", rot=(0, -hyaw, -hroll + sx * splay * swing))
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0
            meta = 34 * smooth(max(0, (st - 0.55) / 0.45)); clear = stance_clear
            toe = 6 * (1 - smooth(min(1.0, st / 0.18))) + 8 * smooth(max(0, (st - 0.7) / 0.3))
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e
            ly = lift * math.sin(math.pi * min(1, sw * 1.1)) ** 1.2
            meta = 34 * (1 - smooth(sw / 0.5)) - 20 * math.sin(math.pi * sw)
            toe = -28 * math.sin(math.pi * min(1, sw * 1.1)) + 6 * smooth((sw - 0.7) / 0.3)
            clear = stance_clear + 1.2 * math.sin(math.pi * sw) ** 0.5
        T.plant(p, s, ly, dz - 5, meta, toe, clear)
    return p


# (period s, stride in T. rex units, duty, lift, bob): the ground covered per cycle is stride * K model px
WALK = (1.8, 84, 0.62, 10, 1.3)
RUN = (0.8, 140, 0.40, 16, 2.2)
SPRINT = (0.7, 166, 0.34, 18, 2.4)
STALK = (WALK[0] * 1.5, WALK[1] * 0.7)


def walk(t):
    """the long light stride: little roll, the head level and forward, the thin tail swinging"""
    return gait(t, *WALK, roll=3.4, yaw=2.2, whip=1.3, still=0.85, arm_amp=2.0)


def run(t):
    """a real run: the body level and low, the head out in front, the tail straight out and whipping"""
    p = gait(t, *RUN, lean=8, drop=3, head=-6, roll=2.0, yaw=1.4, whip=1.0, still=0.95, stance_clear=0.2,
             arm_amp=1.2, tail_up=3)
    arms(p, -12, 10)
    return p


def sprint(t):
    """the long chase: flatter and more stretched than the run, the neck and tail one straight line"""
    p = gait(t, *SPRINT, lean=11, drop=4.5, head=-8, roll=1.5, yaw=1.0, whip=0.8, still=1.0, stance_clear=0.25,
             arm_amp=0.8, tail_up=4)
    arms(p, -16, 14)
    return p


def drive(t):
    """the juvenile's drive: a banked run in a wide arc, the head low and turned in toward the prey, the tail
    swinging out of the turn"""
    p = gait(t, *RUN, lean=9, drop=4, head=-12, roll=1.6, yaw=1.0, whip=0.9, still=1.0, stance_clear=0.2,
             arm_amp=1.0, tail_up=2, bank=-7, turn=-5)
    arms(p, -14, 12)
    return p


def stalk(t):
    Tw, st, du, li, bo = WALK
    return gait(t, STALK[0], STALK[1], 0.72, li * 0.7, bo * 0.4, lean=3, drop=6, head=-11, roll=2.0, yaw=1.0,
                whip=0.4, still=1.0, arm_amp=1.0, tail_up=-1)


# ------------------------------------------------------------------ standing
IDLE_T = 8.0
LOOK = tr((0, (0, 0)), (1.3, (0, 0)), (1.9, (3, 12), ease_out), (3.3, (3, 12)), (3.8, (-1, -8), ease_out),
          (5.2, (-1, -8)), (5.8, (5, 4), ease_out), (7.2, (5, 4)), (8.0, (0, 0)))


def idle(t):
    """the base: light breathing, the weight shifting from one leg to the other, the head turned now and then with
    the whole neck, the thin tail swinging"""
    p = {}
    br = wave(t, 2.0)
    sh = wave(t, IDLE_T)
    add(p, "body", rot=(0.8 * br, 0.8 * sh, 1.6 * sh), pos=(0, 0.35 * br * K, 0))
    lp, ly = LOOK(t)
    T.neck(p, (-0.6 * br + lp * 0.5, ly * 0.55, -0.9 * sh))
    add(p, "skull", rot=(lp * 0.5 - 0.4 * br, ly * 0.45, -ly * 0.15))
    add(p, "jaw", rot=(-0.6 - 0.6 * max(0, br), 0, 0))
    for i, (b, g) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(0.4 * g * wave(t, 2.0, -0.5 * i), 2.2 * g * wave(t, IDLE_T / 2, -0.6 * i), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(1.5 * wave(t, 2.0, -0.8 - 3 * o), 0, 0))
        add(p, f"thigh_{s}", rot=(0, 0, -1.6 * sh))
    return T.stand(p)


def snort(t):
    """a short blow through the nose: the head jerks up a little, the jaw shut, a shake of the snout"""
    p = {}
    s = bump(t, 0.35, 0.08)
    add(p, "body", rot=(1.2 * s, 0, 0))
    T.neck(p, (3 * s, 0, 0)); add(p, "skull", rot=(4 * s, 2 * decay(t, 0.4, 0.15, 6.0), 4 * decay(t, 0.4, 0.15, 6.0)))
    add(p, "jaw", rot=(-1.5 * s, 0, 0))
    trail(p, t, lambda u: 1.5 * bump(u, 0.4, 0.15), axis=0)
    alive(p, t, k=0.6)
    return T.stand(p)


SETTLE_T = 2.6


def settle(t):
    """the weight moved onto the other leg with one step, the body sinking a little as it settles"""
    p = {}
    k = float(tr((0, 0), (0.6, 1, smooth), (2.0, 1), (2.6, 0, smooth))(t))
    add(p, "body", rot=(0, 2 * k, -3 * k), pos=(0, -0.6 * k, 0))
    T.neck(p, (0, -2 * k, 2 * k)); tail(p, yaw=-3 * k)
    alive(p, t, k=0.6)
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, -2 * k, 3 * k))
    up = steps(t, 0.7, 1.2, 5.0)
    T.plant(p, "l", up, 2.0 * smooth((t - 0.7) / 0.5) * (1 - smooth((t - 1.9) / 0.6)), 6 * up / 5, -10 * up / 5, clear=0.6 * min(1.0, up / 2.0) - 0.05)
    T.plant(p, "r")
    return p


SCAN_T = 5.0


def scan(t):
    """it lifts the head and looks over the forest, left, right, then back"""
    p = {}
    up = float(tr((0, 0), (0.6, 1, ease_out), (4.3, 1), (5.0, 0, smooth))(t))
    yaw = float(tr((0, 0), (0.8, 0), (1.6, -16, smooth), (2.5, -16), (3.4, 14, smooth), (4.2, 14), (5.0, 0, smooth))(t))
    add(p, "body", rot=(2 * up, 0.2 * yaw, 0))
    T.neck(p, (8 * up, 0.6 * yaw, 0)); add(p, "skull", rot=(2 * up, 0.4 * yaw, -0.1 * yaw))
    trail(p, t, lambda u: -0.15 * float(tr((0, 0), (0.8, 0), (1.6, -16, smooth), (2.5, -16), (3.4, 14, smooth), (4.2, 14), (5.0, 0, smooth))(u)), delay=0.12)
    alive(p, t, k=0.7)
    return T.stand(p)


# ------------------------------------------------------------------ voice
ROAR_T = 3.4
R_RISE = tr((0, 0), (0.5, -0.4, ease_out), (0.9, 1.0, ease_out), (2.6, 0.85), (3.0, 0.1, ease_in), (3.4, 0.0))
R_JAW = tr((0, 0), (0.45, -1.5), (0.6, -6, ease_out), (0.92, -34, ease_out), (1.2, -27), (1.48, -36), (1.78, -28),
           (2.1, -38), (2.6, -30), (2.95, -4, ease_in), (3.4, 0))
R_SWEEP = tr((0, 0), (0.9, 0), (1.6, 9, ease_out), (2.3, -8), (2.7, -3), (3.4, 0))


def roar(t):
    """the roar forward and low (not to the sky): the head drawn back and down, thrust out level, the jaws wide, a
    slow sweep from side to side; the body leans into it"""
    p = {}
    k = float(R_RISE(t)); sw = float(R_SWEEP(t))
    shake = tremor(t, (9.3, 13.1, 6.7), (1.0, 0.6, 0.4)) * window(t, 0.95, 2.6, 0.2)
    add(p, "body", rot=(2 * k + 0.3 * shake, 0.4 * sw, 0), pos=(0, -1.2 * max(0.0, -k), 2.0 * k))
    T.neck(p, (-6 * max(0.0, -k) + 4 * k + 0.5 * shake, 0.8 * sw, 0))
    add(p, "skull", rot=(3 * k + 0.6 * shake, 0.4 * sw, -0.2 * sw))
    add(p, "jaw", rot=(float(R_JAW(t)), 0, 0))
    trail(p, t, lambda u: -0.5 * float(R_SWEEP(u)), delay=0.08)
    trail(p, t, lambda u: -2.0 * float(R_RISE(u)), axis=0, delay=0.08)
    arms(p, -8 * max(0.0, k), 6 * max(0.0, k))
    alive_upper(p, t, k=0.4)
    return T.stand(p)


ROAR_LOUD_T = 4.4
RL_UP = tr((0, 0), (0.6, -0.5, ease_out), (1.1, 1.0, ease_out), (3.6, 0.9), (4.0, 0.1, ease_in), (4.4, 0))
RL_JAW = tr((0, 0), (0.6, -3), (1.1, -42, ease_out), (1.5, -32), (1.9, -44), (2.3, -32), (2.7, -45), (3.4, -36),
            (3.9, -4, ease_in), (4.4, 0))


def roar_loud(t):
    """the loud roar: one step forward, the head up and out, three pulses of the whole body"""
    p = {}
    k = float(RL_UP(t))
    pulse = sum(bump(t, c, 0.12) for c in (1.2, 1.95, 2.75))
    shake = tremor(t, (10.1, 14.3, 7.2), (1.0, 0.6, 0.4)) * window(t, 1.1, 3.5, 0.2)
    add(p, "body", rot=(5 * k + 1.5 * pulse, 0, 0), pos=(0, -1.5 * max(0.0, -k), 2.5 * k))
    T.neck(p, (-10 * max(0.0, -k) + 14 * k + 3 * pulse + 0.6 * shake, 0, 0))
    add(p, "skull", rot=(4 * k + 2 * pulse + 0.8 * shake, 0, 0))
    add(p, "jaw", rot=(float(RL_JAW(t)), 0, 0))
    trail(p, t, lambda u: -3.0 * float(RL_UP(u)) - 1.5 * sum(bump(u, c, 0.12) for c in (1.2, 1.95, 2.75)), axis=0, delay=0.08)
    arms(p, -14 * max(0.0, k), 10 * max(0.0, k))
    alive_upper(p, t, k=0.3)
    stepf = steps(t, 0.55, 1.0, 6.0)
    T.plant(p, "l", stepf, -6 * smooth((t - 0.55) / 0.45) * (1 - smooth((t - 3.7) / 0.6)), 8 * stepf / 6, -14 * stepf / 6, clear=0.6 * min(1.0, stepf / 2) - 0.05)
    T.plant(p, "r")
    return p


GROWL_T = 2.4


def growl_low(t):
    """the warning: the mouth shut, the head low and turned a little aside to show the face, a rumble that shakes
    the throat and chest; the lips lift off the teeth for a moment"""
    p = {}
    k = float(tr((0, 0), (0.4, 1, ease_out), (1.9, 1), (2.4, 0, smooth))(t))
    rum = tremor(t, (14.2, 19.7, 9.3), (0.8, 0.5, 0.3)) * k
    lip = bump(t, 1.2, 0.25)
    add(p, "body", rot=(-2 * k + 0.25 * rum, 0, 0), pos=(0, -1.2 * k, 0))
    T.neck(p, (-10 * k + 0.4 * rum, -6 * k, 0)); add(p, "skull", rot=(-4 * k + 0.3 * rum, -4 * k, 6 * k))
    add(p, "jaw", rot=(-0.8 * k - 4 * lip - 0.3 * abs(rum), 0, 0))
    tail(p, pitch=-1.5 * k)
    trail(p, t, lambda u: 0.6 * tremor(u, (3.1, 4.7, 2.3), (1, 0.5, 0.3)), delay=0.08)
    arms(p, -6 * k)
    alive_upper(p, t, k=0.4)
    return T.stand(p)


# ------------------------------------------------------------------ blows
BITE_T = 1.4          # the "attack" strike: the jaws shut at 0.50 s (tick 10), the next one at 1.4 s (tick 28)
SB_PITCH = tr((0, 0), (0.3, 7, ease_out), (0.5, -12, ease_in), (0.58, -10), (0.8, -3, ease_out), (1.4, 0, smooth))
SB_JAW = tr((0, 0), (0.1, -4), (0.34, -38, ease_out), (0.45, -40), (0.51, -3, ease_in), (0.75, -6, ease_out),
            (1.0, -2), (1.4, 0))
SB_LUNGE = tr((0, 0), (0.3, 2.0, ease_out), (0.5, -6.5, ease_in), (0.6, -6.0), (0.9, -2.0, ease_out), (1.4, 0, smooth))


def slash_bite(t):
    """the light bite: a quick reach of the long head, the jaws shut at 0.50 s and it lets go at once, a flick of
    the head as it pulls out (it bites and goes, it does not hold like the tyrannosaurines)"""
    p = {}
    pt = float(SB_PITCH(t)); lu = float(SB_LUNGE(t))
    hit = math.exp(-max(0.0, t - 0.5) / 0.08) * smooth((t - 0.48) / 0.03)
    flick = decay(t, 0.55, 0.12, 3.5)
    add(p, "body", rot=(0.3 * pt + 1.5 * hit, 2 * flick, 0), pos=(0, -1.2 * max(0.0, -lu) / 6, lu))
    T.neck(p, (pt, 6 * flick, 0)); add(p, "skull", rot=(0.5 * pt + 3 * hit, 4 * flick, 8 * flick))
    add(p, "jaw", rot=(float(SB_JAW(t)), 0, 0))
    trail(p, t, lambda u: -6 * decay(u, 0.55, 0.14, 3.5), delay=0.06)
    trail(p, t, lambda u: -0.3 * float(SB_PITCH(u)), axis=0, delay=0.06)
    arms(p, -10 * smooth((t - 0.25) / 0.2) * (1 - smooth((t - 0.9) / 0.3)), 8 * hit)
    alive_upper(p, t, k=0.3)
    return T.stand(p)


SNAP_T = 0.7          # the snap without stopping: upper body only, over the run (jaws shut at 0.25 s, tick 5)


def snap_bite(t):
    """a snap of the jaws on the move: only the neck, head and jaw (the legs keep running under it)"""
    p = {}
    o = float(tr((0, 0), (0.13, 1, ease_out), (0.25, 0, ease_in), (0.7, 0))(t))
    hit = math.exp(-max(0.0, t - 0.25) / 0.07) * smooth((t - 0.23) / 0.03)
    T.neck(p, (4 * o - 7 * hit, 0, 0)); add(p, "skull", rot=(5 * o + 2 * hit, 2 * decay(t, 0.3, 0.1, 4.0), 0))
    add(p, "jaw", rot=(-34 * o, 0, 0))
    for b, g in zip(TAILS, BEND):
        add(p, b, rot=(0, 1.5 * g * decay(t, 0.3, 0.15, 2.5), 0))
    return p


QUICK_T = 0.9         # ApexTheropod QUICK_BITE: the jaws shut at 0.30 s (tick 6)


def attack_quick(t):
    p = {}
    o = float(tr((0, 0), (0.15, 1, ease_out), (0.3, 0, ease_in), (0.9, 0))(t))
    lu = float(tr((0, 0), (0.15, 1.0, ease_out), (0.3, -4.0, ease_in), (0.45, -3.5), (0.9, 0, back_out))(t))
    hit = math.exp(-max(0.0, t - 0.3) / 0.08) * smooth((t - 0.28) / 0.03)
    add(p, "body", rot=(2 * o - 1 * hit, 0, 0), pos=(0, 0, lu))
    T.neck(p, (6 * o - 8 * hit - 2 * smooth((t - 0.3) / 0.05) * (1 - smooth((t - 0.5) / 0.3)), 0, 0))
    add(p, "skull", rot=(4 * o + 2 * hit, 0, 0)); add(p, "jaw", rot=(-30 * o, 0, 0))
    trail(p, t, lambda u: 1.5 * bump(u, 0.32, 0.1), axis=0)
    alive_upper(p, t, k=0.3)
    return T.stand(p)


BITE_LOW_T = 1.2      # hit at 0.40 s (tick 8)


def bite_low(t):
    """something small: the head swept low along the ground, the bite at the bottom of the sweep"""
    p = {}
    d = float(tr((0, 0), (0.25, 0.5, ease_out), (0.4, 1, ease_in), (0.6, 0.9), (1.2, 0, smooth))(t))
    o = float(tr((0, 0), (0.25, 1, ease_out), (0.4, 0, ease_in), (1.2, 0))(t))
    add(p, "body", rot=(-8 * d, 0, 0), pos=(0, -2.5 * d, -2.0 * d))
    T.neck(p, (-26 * d, 0, 0)); add(p, "skull", rot=(-8 * d, 0, 0)); add(p, "jaw", rot=(-34 * o, 0, 0))
    tail(p, pitch=-4 * d)
    arms(p, 8 * d)
    alive_upper(p, t, k=0.3)
    return T.stand(p)


BITE_SIDE_T = 1.3     # hit at 0.45 s (tick 9)


def bite_side(t):
    """the head swings in from the side in an arc, the jaws shutting at the end of the arc"""
    p = {}
    y = float(tr((0, 0), (0.25, -1, ease_out), (0.45, 0.6, ease_in), (0.6, 0.5), (1.3, 0, smooth))(t))
    o = float(tr((0, 0), (0.25, 1, ease_out), (0.45, 0, ease_in), (1.3, 0))(t))
    add(p, "body", rot=(0, 8 * y, -3 * y))
    T.neck(p, (-4 * abs(y), 22 * y, -4 * y)); add(p, "skull", rot=(0, 10 * y, 14 * y)); add(p, "jaw", rot=(-32 * o, 0, 0))
    trail(p, t, lambda u: -6 * float(tr((0, 0), (0.25, -1, ease_out), (0.45, 0.6, ease_in), (0.6, 0.5), (1.3, 0, smooth))(u)), delay=0.07)
    alive_upper(p, t, k=0.3)
    return T.stand(p)


STOMP_T = 1.7         # ApexTheropod STOMP: the foot lands at 0.90 s (tick 18)


def stomp(t):
    p = {}
    k = float(tr((0, 0), (0.5, 1, ease_out), (1.2, 1), (1.7, 0, smooth))(t))
    land = bump(t, 0.92, 0.05)
    add(p, "body", rot=(-6 * k + 2 * land, 0, -4 * k), pos=(0, -1.0 * k - 1.0 * land, 0))
    T.neck(p, (-16 * k, 0, 0)); add(p, "skull", rot=(-6 * k, 0, 0)); add(p, "jaw", rot=(-6 * land, 0, 0))
    trail(p, t, lambda u: 3 * bump(u, 0.95, 0.12), axis=0)
    alive_upper(p, t, k=0.3)
    up = steps(t, 0.3, 0.9, 12.0)
    T.plant(p, "l", up, -4 * smooth((t - 0.3) / 0.5) * (1 - smooth((t - 1.2) / 0.5)), 10 * up / 12, -16 * up / 12, clear=0.6 * min(1.0, up / 2) - 0.05)
    T.plant(p, "r")
    return p


SHOVE_T = 1.4         # chest to chest: the shoulder shove (hit at 0.65 s, tick 13)


def shove(t):
    p = {}
    k = float(tr((0, 0), (0.45, -0.6, ease_out), (0.65, 1, ease_in), (0.85, 0.9), (1.4, 0, smooth))(t))
    add(p, "body", rot=(0, 10 * k, -6 * k), pos=(0, -1.0 * abs(k), 2.0 * k))
    T.neck(p, (-4 * abs(k), -10 * k, 0)); add(p, "skull", rot=(0, -4 * k, 0)); add(p, "jaw", rot=(-4 * max(0.0, k), 0, 0))
    trail(p, t, lambda u: -6 * float(tr((0, 0), (0.45, -0.6, ease_out), (0.65, 1, ease_in), (0.85, 0.9), (1.4, 0, smooth))(u)), delay=0.07)
    alive_upper(p, t, k=0.3)
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, -10 * k, 0))
    return T.stand(p)


# ------------------------------------------------------------------ eating
EAT_T = 3.2


def rip_feed(t):
    """eating: the head down, a bite, then a pull back and up with the whole neck that tears a piece off, the head
    tossed to swallow"""
    p = {}
    dn = float(tr((0, 0), (0.5, 1, ease_out), (1.1, 1), (1.6, 0.4, ease_out), (2.1, 0.6), (2.6, -0.2, ease_out), (3.2, 0, smooth))(t))
    o = float(tr((0, 0), (0.4, 1, ease_out), (0.6, 0, ease_in), (2.4, 0), (2.6, 0.5, ease_out), (2.8, 0), (3.2, 0))(t))
    pull = bump(t, 1.35, 0.18)
    add(p, "body", rot=(-7 * dn + 2 * pull, 0, 0), pos=(0, -2.5 * dn, -1.5 * dn + 2.0 * pull))
    T.neck(p, (-22 * dn + 8 * pull, 0, 0)); add(p, "skull", rot=(-6 * dn + 4 * pull, 4 * decay(t, 1.2, 0.2, 4.0), 6 * decay(t, 1.2, 0.2, 4.0)))
    add(p, "jaw", rot=(-30 * o - 2, 0, 0))
    tail(p, pitch=-3 * dn)
    trail(p, t, lambda u: 2.5 * bump(u, 1.45, 0.2), axis=0)
    arms(p, 8 * dn)
    alive_upper(p, t, k=0.3)
    T.plant(p, "l", 0, -3 * dn); T.plant(p, "r")
    return p


# ------------------------------------------------------------------ the duel's loops and reactions
GUARD_T = 2.0


def guard(t):
    """the runner's guard: side-on and up on its toes, the long head low and forward, the mouth just open, a quick
    weave, ready to step out"""
    p = {}
    L = GUARD_T
    bounce = wave(t, L / 2)
    weave = wave(t, L)
    growl = tremor(t, (16 / L, 22 / L, 11 / L), (0.6, 0.4, 0.3))
    add(p, "body", rot=(-3 + 0.8 * bounce, 2.6 * weave, 2.0 * weave), pos=(0, -1.8 + 0.6 * bounce, 0))
    T.neck(p, (-9 - 0.6 * wave(t, L / 2, -0.6) + 0.4 * growl, -2 * weave + 4 * wave(t, L, -0.9), -0.8 * weave))
    add(p, "skull", rot=(-4 + 0.5 * wave(t, L / 2, -1.2) + 0.4 * growl, 2 * wave(t, L, -1.5), -1.5 * wave(t, L, -1.3)))
    add(p, "jaw", rot=(-4 - 1.5 * max(0.0, wave(t, L / 2, -0.5)) - 0.6 * growl, 0, 0))
    for k, (b, g) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(-1.0 * g + 0.4 * g * wave(t, L / 2, -0.6 * k), -3.0 * g * wave(t, L, -0.8 - 0.7 * k), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(-8 + 1.2 * wave(t, L / 2, -1 - 3 * o), 0, 0)); add(p, f"forearm_{s}", rot=(6, 0, 0))
        sx = 1 if s == "l" else -1
        add(p, f"thigh_{s}", rot=(0, -2 * weave, -1.6 * weave + 3.0 * sx))
    T.plant(p, "l", 0.0, 4.0)
    T.plant(p, "r", 0.0, -5.0)
    return p


STRAFE_T = 1.4


def strafe(t, side):
    """slow heavy side steps round the rival, the body facing it, the head on it"""
    d = 1.0 if side == "left" else -1.0
    ph = (t / STRAFE_T) % 1.0; w = 2 * math.pi * ph; p = {}
    lean = -3.0 * d
    sk = landing(2 * ph + 0.1)
    add(p, "body", rot=(-3 + 0.6 * sk, 0, lean + 1.4 * math.sin(2 * w)), pos=(0, -2.4 + 0.8 * sk, 0))
    T.neck(p, (-8 - 0.6 * landing(2 * ph + 0.02), 2 * d * math.sin(w), -0.7 * lean))
    add(p, "skull", rot=(-4, 0, 0.5 * d)); add(p, "jaw", rot=(-3, 0, 0))
    for k, (b, g) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(-1.0 * g, g * (-4.0 * d - 1.5 * math.sin(2 * w - 0.8 - 0.7 * k)), 0))
    for s, o in SIDES:
        sx = 1 if s == "l" else -1
        u = (ph + o) % 1.0
        add(p, f"arm_{s}", rot=(-8 + 2 * math.sin(w + o * 2 * math.pi - 2.0), 0, 0))
        if u < 0.42:
            sw = u / 0.42
            ly = 6.0 * math.sin(math.pi * sw) ** 1.2
            add(p, f"thigh_{s}", rot=(0, 0, d * 7.0 * (sw - 0.5) + 2.5 * sx - lean))
            T.plant(p, s, ly, 0.0, 8 * math.sin(math.pi * sw), -16 * math.sin(math.pi * sw), clear=0.8 * math.sin(math.pi * sw) ** 0.5)
        else:
            st = (u - 0.42) / 0.58
            add(p, f"thigh_{s}", rot=(0, 0, -d * 7.0 * (st - 0.5) + 2.5 * sx - lean))
            T.plant(p, s)
    return p


def strafe_left(t): return strafe(t, "left")
def strafe_right(t): return strafe(t, "right")


TURN_T = 1.4


def turn(t, side):
    """stepping round on the spot: the head turns first, the heavy body follows, the tail swings out the other way"""
    d = 1.0 if side == "left" else -1.0
    ph = (t / TURN_T) % 1.0; w = 2 * math.pi * ph; p = {}
    lead = -d
    add(p, "body", rot=(0, lead * (3.0 + 1.2 * math.sin(w)), 2.6 * math.sin(w + 0.3)), pos=(0, -0.6 + 0.5 * math.cos(2 * w), 0))
    T.neck(p, (-1.0, lead * 10.0, -1.5 * math.sin(w + 0.3)))
    add(p, "skull", rot=(0, lead * 6.0, -0.6 * math.sin(w))); add(p, "jaw", rot=(-0.6, 0, 0))
    for k, (b, g) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(0.4 * g * math.sin(2 * w - 0.6 * k), g * (-lead * 5.0 - 2.0 * math.sin(w - 0.8 * (k + 1))), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(3 * math.sin(w + o * 2 * math.pi - 2.0), 0, 0))
        u = (ph + o) % 1.0
        if u < 0.4:
            sw = u / 0.4
            ly = 6.0 * math.sin(math.pi * sw) ** 1.2
            dz = -3.0 * math.cos(math.pi * sw)
            toe = -20 * math.sin(math.pi * sw); meta = 10 * math.sin(math.pi * sw); clear = 1.0 * math.sin(math.pi * sw) ** 0.5
            add(p, f"thigh_{s}", rot=(0, lead * 6.0 * math.sin(math.pi * sw), 0))
        else:
            ly, dz, toe, meta, clear = 0.0, 3.0 - 6.0 * ((u - 0.4) / 0.6), 0.0, 0.0, -0.05
        add(p, f"thigh_{s}", rot=(0, -lead * 3.0, -2.6 * math.sin(w + 0.3)))
        T.plant(p, s, ly, dz, meta, toe, clear)
    return p


def turn_left(t): return turn(t, "left")
def turn_right(t): return turn(t, "right")


FEINT_T = 1.2


def feint(t):
    """a bite that stops short: the head darts in, the jaws snap on nothing a step short, it pulls back"""
    p = {}
    n = tr((0, (0, 0)), (0.2, (5, 0), ease_out), (0.42, (-10, 0), ease_in), (0.55, (-9, 0)), (1.2, (0, 0), back_out))(t)
    lunge = float(tr((0, 0), (0.2, 1.5, ease_out), (0.42, -4.0, ease_in), (0.55, -3.5), (1.2, 0, back_out))(t))
    o = float(tr((0, 0), (0.25, 1, ease_out), (0.45, 0.1, ease_in), (1.2, 0))(t))
    add(p, "body", rot=(-0.3 * n[0], 0, 0), pos=(0, -1.0 * smooth(t / 0.3) * (1 - smooth((t - 0.6) / 0.4)), lunge))
    T.neck(p, (n[0], 0, 0)); add(p, "skull", rot=(0.5 * n[0], 0, 0)); add(p, "jaw", rot=(-28 * o, 0, 0))
    trail(p, t, lambda u: 2.0 * bump(u, 0.45, 0.12), axis=0)
    trail(p, t, lambda u: 1.5 * decay(u, 0.42, 0.2, 2.5))
    alive(p, t, k=0.5)
    return T.stand(p)


BLOCK_T = 0.8


def block(t):
    """it takes the blow on the heavy skull: the head dips into it, the jolt runs back into the body"""
    p = {}
    dip = float(tr((0, 0), (0.07, 1, ease_out), (0.12, 1), (0.8, 0, ease_out))(t))
    e = math.exp(-max(0.0, t - 0.08) / 0.18) * smooth((t - 0.06) / 0.04)
    add(p, "body", rot=(3 * e, -3 * e, 3 * e), pos=(0, -0.8 * e, 2.0 * e))
    T.neck(p, (-7 * dip + 5 * e, -5 * e, 2 * e)); add(p, "skull", rot=(-8 * dip + 7 * e, -4 * e, 6 * e))
    add(p, "jaw", rot=(-4 * e, 0, 0))
    trail(p, t, lambda u: 5 * math.exp(-max(0.0, u - 0.08) / 0.22) * smooth((u - 0.06) / 0.04), delay=0.05)
    alive_upper(p, t, k=0.5)
    return T.stand(p)


RECOIL_T = 0.9


def recoil(t):
    """its blow was turned: the head knocked aside, a heavy step back, a shake of the head"""
    p = {}
    e = math.exp(-max(0.0, t - 0.04) / 0.2) * smooth(t / 0.04)
    wob = decay(t, 0.1, 0.18, 4.0)
    add(p, "body", rot=(-3 * e, 4 * e, -3 * e), pos=(0, -0.6 * e, 2.5 * e))
    T.neck(p, (5 * e, 12 * e + 3 * wob, -4 * e)); add(p, "skull", rot=(4 * e, 8 * e + 4 * wob, -9 * e + 6 * decay(t, 0.45, 0.12, 5.0)))
    add(p, "jaw", rot=(-8 * e, 0, 0))
    trail(p, t, lambda u: -5 * math.exp(-max(0.0, u - 0.04) / 0.24) * smooth(u / 0.04), delay=0.05)
    alive_upper(p, t, k=0.5)
    T.plant(p, "r")
    lift = steps(t, 0.06, 0.4, 6.0)
    T.plant(p, "l", lift, 4 * smooth((t - 0.06) / 0.34), 0, -10 * lift / 6.0, clear=-0.05)
    return p


SUBMIT_T = 2.4


def submit(t):
    """beaten: the head goes down and aside, the mouth shut, the tail low, it turns away"""
    p = {}
    k = float(tr((0, 0), (0.5, 1, ease_out), (2.4, 1))(t))
    turn_ = float(tr((0, 0), (0.7, 0), (1.5, 1, ease_out), (2.4, 1))(t))
    add(p, "body", rot=(-4 * k, 10 * turn_, 0), pos=(0, -2.5 * k, 0))
    T.neck(p, (-16 * k, 10 * turn_, 0)); add(p, "skull", rot=(-6 * k, 6 * turn_, 8 * turn_)); add(p, "jaw", rot=(-1, 0, 0))
    tail(p, pitch=4 * k)
    trail(p, t, lambda u: -4 * float(tr((0, 0), (0.7, 0), (1.5, 1, ease_out), (2.4, 1))(u)), delay=0.08)
    arms(p, 8 * k, -6 * k)
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, -10 * turn_, 0))
    alive_upper(p, t, k=0.8, period=1.3)
    T.plant(p, "l")
    hop = steps(t, 0.8, 1.3, 6.0)
    T.plant(p, "r", hop, -3 * smooth((t - 0.8) / 0.5), 8 * hop / 6.0, -12 * hop / 6.0, clear=-0.05)
    return p


# ------------------------------------------------------------------ the pack, the dodge, the long chase
SIDESTEP_T = 0.7


def sidestep(t):
    """the dodge: a quick hop to the side off the far foot, the body leaning away, the head kept on the rival"""
    p = {}
    k = float(tr((0, 0), (0.12, 1, ease_out), (0.38, 0.9), (0.7, 0, smooth))(t))
    add(p, "body", rot=(-1.5 * k, -4 * k, 7 * k), pos=(0, -1.2 * k + 1.0 * bump(t, 0.2, 0.08), 0))
    T.neck(p, (-3 * k, 8 * k, -5 * k)); add(p, "skull", rot=(-2 * k, 4 * k, -4 * k)); add(p, "jaw", rot=(-3 * k, 0, 0))
    trail(p, t, lambda u: 6 * float(tr((0, 0), (0.12, 1, ease_out), (0.38, 0.9), (0.7, 0, smooth))(u)), delay=0.05)
    arms(p, -6 * k)
    alive_upper(p, t, k=0.3)
    up = steps(t, 0.05, 0.35, 6.0)
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, 4 * k, -7 * k + (5 * k if s == "l" else -2 * k)))
    T.plant(p, "l", up, -1.5 * up / 6, 6 * up / 6, -12 * up / 6, clear=0.7 * min(1.0, up / 2) - 0.05)
    T.plant(p, "r")
    return p


CALL_PACK_T = 2.8
CP_UP = tr((0, 0), (0.5, 1, ease_out), (2.2, 1), (2.8, 0, smooth))
CP_JAW = tr((0, 0), (0.55, -3), (0.8, -22, ease_out), (1.1, -16), (1.35, -24), (1.65, -17), (1.95, -20), (2.3, -2, ease_in), (2.8, 0))


def call_pack(t):
    """the adult calls the pack before the hunt: the head raised high and turned a little, a rising, pulsing call
    (the throat beats with it), the tail lifted"""
    p = {}
    k = float(CP_UP(t))
    pulse = sum(bump(t, c, 0.1) for c in (0.85, 1.35, 1.9))
    add(p, "body", rot=(4 * k + 0.8 * pulse, 0, 0), pos=(0, 0.6 * k, 0))
    T.neck(p, (18 * k + 2 * pulse, 6 * k * math.sin(2 * math.pi * (t - 0.6) / 2.2), 0))
    add(p, "skull", rot=(6 * k + 1.5 * pulse, 3 * k, 0))
    add(p, "jaw", rot=(float(CP_JAW(t)), 0, 0))
    trail(p, t, lambda u: -3.0 * float(CP_UP(u)), axis=0, delay=0.08)
    arms(p, -8 * k, 6 * k)
    alive_upper(p, t, k=0.3)
    return T.stand(p)


ANSWER_T = 2.0
AN_UP = tr((0, 0), (0.25, 0), (0.6, 1, ease_out), (1.5, 1), (2.0, 0, smooth))
AN_JAW = tr((0, 0), (0.6, -2), (0.8, -16, ease_out), (1.05, -10), (1.3, -14), (1.6, -2, ease_in), (2.0, 0))


def answer(t):
    """a pack member answers the call: the head comes up and turns toward it, one short call"""
    p = {}
    k = float(AN_UP(t))
    add(p, "body", rot=(2.5 * k, 3 * k, 0))
    T.neck(p, (12 * k, 8 * k, 0)); add(p, "skull", rot=(4 * k, 4 * k, -2 * k))
    add(p, "jaw", rot=(float(AN_JAW(t)), 0, 0))
    trail(p, t, lambda u: -2.0 * float(AN_UP(u)), axis=0, delay=0.08)
    alive_upper(p, t, k=0.4)
    return T.stand(p)


AMBUSH_T = 3.0


def ambush_crouch(t):
    """an adult waiting for the prey the young drive in: crouched low on bent legs, the head low and level and
    dead still on the prey, the tail low, only the tip twitching (loop)"""
    p = {}
    L = AMBUSH_T
    br = wave(t, L / 2)
    add(p, "body", rot=(-5 + 0.4 * br, 0, 0), pos=(0, -9 + 0.3 * br, 1.0))
    T.neck(p, (-10 - 0.3 * br, 0, 0)); add(p, "skull", rot=(-3, 0, 0))
    add(p, "jaw", rot=(-1.0 - 0.6 * max(0.0, wave(t, L / 2, -0.4)), 0, 0))
    for k, (b, g) in enumerate(zip(TAILS, BEND)):
        twitch = 3.0 * math.sin(2 * math.pi * 2 * t / L - 0.9 * k) * (k >= 3)
        add(p, b, rot=(2.5 * g, twitch, 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(10 + 1.0 * wave(t, L / 2, -1 - 3 * o), 0, 0)); add(p, f"forearm_{s}", rot=(-6, 0, 0))
    return T.stand(p)


PANT_T = 3.0


def pant(t):
    """spent after the long chase: it stops, the head hangs, the jaws wide, the flanks heaving fast"""
    p = {}
    k = float(tr((0, 0), (0.4, 1, ease_out), (2.5, 1), (3.0, 0, smooth))(t))
    hv = wave(t, 0.5)
    add(p, "body", rot=(3 * k + 2.2 * k * hv, 0, 0), pos=(0, -1.6 * k + 0.8 * k * hv, 0))
    T.neck(p, (-14 * k - 1.8 * k * wave(t, 0.5, -0.6), 0, 0))
    add(p, "skull", rot=(-5 * k - 1.2 * k * wave(t, 0.5, -1.2), 0, 0))
    add(p, "jaw", rot=(-18 * k - 6 * k * max(0.0, wave(t, 0.5, -0.4)), 0, 0))
    for b, g in zip(TAILS, BEND):
        add(p, b, rot=(3.0 * g * k + 0.5 * g * k * hv, 0, 0))
    arms(p, 10 * k, 4 * k)
    return T.stand(p)


# ------------------------------------------------------------------ transitions and tiredness
LIE_DOWN_T = 2.2


def lie_down(t):
    p = {}
    k = float(tr((0, 0), (0.3, 0.05), (1.5, 0.92, ease_in), (1.75, 1.03), (2.2, 1.0, ease_out))(t))
    look = float(tr((0, 0), (0.4, 1, ease_out), (1.4, 1), (2.2, 0, ease_out))(t))
    T.lie(p, k)
    T.neck(p, (-6 * look, 0, 0)); add(p, "skull", rot=(-4 * look, 0, 0))
    land = bump(t, 1.6, 0.1)
    add(p, "body", rot=(0.8 * land, 0, 0)); add(p, "jaw", rot=(-3 * land, 0, 0))
    trail(p, t, lambda u: 2.5 * bump(u, 1.6, 0.15), axis=0, delay=0.06)
    alive_upper(p, t, k=0.5)
    return ground_fit(p)


GET_UP_T = 2.2


def get_up(t):
    p = {}
    k = float(tr((0, 1.0), (0.4, 1.02), (1.3, 0.05, ease_out), (1.55, -0.02), (2.2, 0.0, ease_out))(t))
    push = bump(t, 0.6, 0.2)
    T.lie(p, max(0.0, k))
    T.neck(p, (-12 * push, 0, 0)); add(p, "skull", rot=(-6 * push, 0, 0))
    wob = decay(t, 1.35, 0.25, 2.4)
    add(p, "body", rot=(0, 0, 2.0 * wob))
    trail(p, t, lambda u: -3.0 * decay(u, 1.35, 0.28, 2.4), delay=0.07)
    alive_upper(p, t, k=0.5)
    return ground_fit(p)


FALL_ASLEEP_T = 3.6


def fall_asleep(t):
    """lying awake, the head sinks to the ground in two nods and the eyes close"""
    p = {}
    hd = float(tr((0, 0), (0.8, 0.3, smooth), (1.3, 0.15, smooth), (2.6, 1.0, smooth), (3.6, 1.0))(t))
    T.lie(p, 1.0, head_down=hd)
    add(p, "jaw", rot=(-2 * bump(t, 1.9, 0.3), 0, 0))
    alive_upper(p, t, k=0.4, period=3.6)
    return ground_fit(p)


WALK_TIRED_T = 2.4


def walk_tired(t):
    """the walk with nothing left: shorter steps (70 x K = 56 px every 2.4 s, the pace DinosaurEntity gives it), the head hanging, the mouth open panting"""
    p = gait(t, WALK_TIRED_T, 70, 0.66, 7, 1.6, lean=2, drop=1.5, head=-9, roll=5.0, yaw=3.0, whip=0.8, arm_amp=1.5,
             tail_up=1.5)
    pant = wave(t, WALK_TIRED_T / 4)
    add(p, "jaw", rot=(-9 - 5 * max(0.0, pant), 0, 0)); T.neck(p, (-1.2 * wave(t, WALK_TIRED_T / 4, -0.5), 0, 0))
    return p


IDLE_TIRED_T = 3.0


def idle_tired(t):
    p = {}
    L = IDLE_TIRED_T
    pant = wave(t, L / 5)
    shift = wave(t, L, 0.3)
    add(p, "body", rot=(2.5 + 1.8 * pant, 0, 1.2 * shift), pos=(0, -1.2 + 0.7 * pant, 0))
    T.neck(p, (-10 - 1.5 * wave(t, L / 5, -0.6), 2 * wave(t, L, 0.5), -0.8 * shift))
    add(p, "skull", rot=(-4 - 1.0 * wave(t, L / 5, -1.2), 1.5 * wave(t, L, -0.5), 0))
    add(p, "jaw", rot=(-11 - 5 * max(0.0, wave(t, L / 5, -0.4)), 0, 0))
    for k, (b, g) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(2.5 * g + 0.4 * g * pant, 1.5 * g * wave(t, L, -0.8 * (k + 1)), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(8 + 2.0 * wave(t, L / 5, -0.8 - o), 0, 0)); add(p, f"forearm_{s}", rot=(4, 0, 0))
        add(p, f"thigh_{s}", rot=(0, 0, -1.2 * shift))
    return T.stand(p)


# ------------------------------------------------------------------ the set
ANIMS = {
    "idle": (idle, IDLE_T, True, "Parado", "base: respiração leve, o peso passa de uma perna à outra, olha de lado com o pescoço"),
    "sniff": (with_breath(BASE["sniff"][0]), 3.0, False, "Parado", "fareja o chão"),
    "look_back": (with_breath(BASE["look_back"][0]), 3.2, False, "Parado", "olha para trás"),
    "shake": (with_breath(BASE["shake"][0], 0.3), 2.0, False, "Parado", "sacode do focinho à cauda; ao sair da água"),
    "yawn": (with_breath(BASE["yawn"][0], 0.4), 3.0, False, "Parado", "bocejo"),
    "stretch": (with_breath(BASE["stretch"][0], 0.4), 3.6, False, "Parado", "espreguiça"),
    "snort": (snort, 1.2, False, "Parado", "bufa pelo nariz"),
    "settle": (settle, SETTLE_T, False, "Parado", "troca o peso de perna com um passo"),
    "scan": (scan, SCAN_T, False, "Parado", "ergue a cabeça e olha a mata"),
    "walk": (walk, WALK[0], True, "Movimento", "passada longa e leve, cabeça à frente, cauda fina balançando"),
    "run": (run, RUN[0], True, "Movimento", "corrida de verdade: corpo baixo, cabeça e cauda numa linha"),
    "sprint": (sprint, SPRINT[0], True, "Movimento", "a perseguição longa: mais esticada e rente que a corrida"),
    "drive": (drive, RUN[0], True, "Movimento", "o jovem toca a presa: corrida inclinada em arco, cabeça baixa"),
    "stalk": (stalk, STALK[0], True, "Movimento", "chegando perto, baixo, cabeça no alvo"),
    "swim": (BASE["swim"][0], 1.6, True, "Movimento", "nadando"),
    "turn_left": (turn_left, TURN_T, True, "Movimento", "girando no lugar para a esquerda"),
    "turn_right": (turn_right, TURN_T, True, "Movimento", "girando no lugar para a direita"),
    "walk_tired": (walk_tired, WALK_TIRED_T, True, "Movimento", "andando cansado, boca aberta"),
    "idle_tired": (idle_tired, IDLE_TIRED_T, True, "Parado", "parado cansado, ofegando"),
    "pant": (pant, PANT_T, False, "Parado", "para depois da perseguição longa: cabeça caída, boca aberta, flancos arfando"),
    "roar": (roar, ROAR_T, False, "Voz", "rugido baixo e para a frente"),
    "roar_loud": (roar_loud, ROAR_LOUD_T, False, "Voz", "rugido forte: um passo à frente, cabeça alta, três pulsos"),
    "call": (with_breath(BASE["call"][0], 0.4), 2.6, False, "Voz", "ronco chamando o bando"),
    "call_pack": (call_pack, CALL_PACK_T, False, "Voz", "o adulto chama o bando antes da caça: cabeça alta, chamado em pulsos"),
    "answer": (answer, ANSWER_T, False, "Voz", "responde ao chamado: ergue a cabeça e vira para quem chamou"),
    "threat": (growl_low, GROWL_T, False, "Voz", "rosnado de boca fechada, cabeça baixa de lado"),
    "attack": (slash_bite, BITE_T, False, "Combate", "mordida leve: estica a cabeça, fecha (0,50 s) e solta logo"),
    "attack_quick": (attack_quick, QUICK_T, False, "Combate", "mordida rápida (0,30 s)"),
    "snap_bite": (snap_bite, SNAP_T, False, "Combate", "mordida sem parar: só pescoço e cabeça, por cima da corrida (0,25 s)"),
    "bite_low": (bite_low, BITE_LOW_T, False, "Combate", "varre a cabeça rente ao chão (0,40 s)"),
    "bite_side": (bite_side, BITE_SIDE_T, False, "Combate", "a cabeça vem de lado em arco (0,45 s)"),
    "stomp": (stomp, STOMP_T, False, "Combate", "pisão em coisa pequena (0,90 s)"),
    "shove": (shove, SHOVE_T, False, "Combate", "empurrão de ombro, peito a peito"),
    "hurt": (with_breath(BASE["hurt"][0], 0.2), 0.6, False, "Combate", "ao levar dano"),
    "death": (regrounded(BASE["death"][0]), 3.0, False, "Combate", "ao morrer"),
    "eat": (rip_feed, EAT_T, False, "Comer", "arranca pedaços puxando com o pescoço"),
    "drink": (with_breath(BASE["drink"][0], 0.3), 4.0, False, "Comer", "bebendo"),
    "ambush_crouch": (ambush_crouch, AMBUSH_T, True, "Caça", "adulto agachado esperando a presa que os jovens tocam"),
    "guard": (guard, GUARD_T, True, "Duelo", "em guarda: leve, de lado, pronto para sair"),
    "strafe_left": (strafe_left, STRAFE_T, True, "Duelo", "passos de lado, para a esquerda"),
    "strafe_right": (strafe_right, STRAFE_T, True, "Duelo", "passos de lado, para a direita"),
    "sidestep": (sidestep, SIDESTEP_T, False, "Duelo", "esquiva: um pulo de lado, a cabeça no rival"),
    "feint": (feint, FEINT_T, False, "Duelo", "finta: a mordida que para curta"),
    "block": (block, BLOCK_T, False, "Duelo", "apara com o crânio"),
    "recoil": (recoil, RECOIL_T, False, "Duelo", "o golpe foi aparado: cabeça de lado, um passo atrás"),
    "submit": (submit, SUBMIT_T, False, "Duelo", "perdeu: cabeça baixa de lado, vira e vai"),
    "sit": (regrounded(BASE["sit"][0]), 6.0, True, "Descanso", "deitado acordado"),
    "sleep": (regrounded(BASE["sleep"][0]), 8.0, True, "Descanso", "dormindo"),
    "wake_sleep": (regrounded(BASE["wake_sleep"][0]), 2.4, False, "Descanso", "acorda de um sono normal"),
    "lie_down": (lie_down, LIE_DOWN_T, False, "Descanso", "deitando"),
    "get_up": (get_up, GET_UP_T, False, "Descanso", "levantando"),
    "fall_asleep": (fall_asleep, FALL_ASLEEP_T, False, "Descanso", "a cabeça desce em dois cochilos e dorme"),
    "knocked_out": (regrounded(BASE["knocked_out"][0]), 4.0, True, "Descanso", "nocauteado, deitado de lado"),
    "wake": (regrounded(BASE["wake"][0]), 3.0, False, "Descanso", "acorda do nocaute"),
    "beg": (with_breath(BASE["beg"][0], 0.5, period=2.0, slow=2.0), 2.0, True, "Domado", "pede comida ao dono"),
    "tame": (with_breath(BASE["tame"][0], 0.5), 2.4, False, "Domado", "ao ser domado"),
}

# the duel's committed moves at the fixed lengths (albertofight.py): lunge, parry (the pass bite as counter), stagger,
# and its signature blow, the pass bite
import albertofight as FIGHT  # noqa: E402
ANIMS.update(FIGHT.NEW)


# ------------------------------------------------------------------ taming and birth (docs/ROSTER.md, "Domesticação")
KNOCKOUT_T = 2.2


def knockout(t):
    """going down from the torpor: it sways, the legs give, the chest hits the ground and it rolls onto its side
    (ends in the knocked_out pose)"""
    p = {}
    g = float(tr((0, 0), (0.6, 0.15), (1.3, 0.8, ease_in), (2.2, 0.8))(t))
    rl = float(tr((0, 0), (0.8, -5), (1.35, 82, ease_in), (1.5, 76), (1.65, 80), (2.2, 80))(t))
    sway = math.sin(2 * math.pi * 1.4 * t) * (1 - smooth((t - 0.9) / 0.3))
    T.lie(p, g); add(p, "root", rot=(0, 0, rl))
    add(p, "body", rot=(0, 4 * sway, 0))
    s2 = smooth((t - 1.3) / 0.3)
    T.neck(p, (-4 - 6 * s2, -5 * sway, -14 * s2)); add(p, "skull", rot=(-6 * s2, 0, -10 * s2))
    add(p, "jaw", rot=(-6 * window(t, 0.3, 1.2) - 9 * s2, 0, 0))
    arms(p, 20 * s2)
    return ground_fit(p)


HATCH_T = 2.6


def hatch(t):
    """the hatchling out of the egg: curled, the head comes up, the first small call, a shake of the wet head"""
    p = {}
    hd = float(tr((0, 1.0), (0.6, 1.0), (1.3, 0.0, ease_out), (2.6, 0.0))(t))
    T.lie(p, 1.0, head_down=hd)
    tail(p, yaw=-14)
    call = bump(t, 1.6, 0.15)
    add(p, "jaw", rot=(-16 * call, 0, 0)); T.neck(p, (6 * call, 0, 0))
    sh = decay(t, 2.0, 0.18, 6.0)
    add(p, "skull", rot=(0, 5 * sh, 14 * sh))
    alive_upper(p, t, k=0.6, period=1.3)
    return ground_fit(p)


ANIMS["knockout"] = (knockout, KNOCKOUT_T, False, "Descanso", "cai no torpor: balança, as pernas cedem e rola de lado")
ANIMS["hatch"] = (hatch, HATCH_T, False, "Domado", "o filhote sai do ovo: ergue a cabeça, primeiro pio, sacode")
