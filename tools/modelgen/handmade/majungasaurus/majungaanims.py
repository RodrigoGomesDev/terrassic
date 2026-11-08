"""Majungasaurus animations, from its own study (docs/estudos/13_PREDADORES_1_10.md, "No jogo" and "Animações além
do padrão"). The plumbing is shared (anim2: easing, leg IK, export; theropod.Plan: plant/stand/lie and the T. rex
poses the template gives for the quiet gestures); the set follows the Daspletosaurus pilot, the Albertosaurus and the
Carcharodontosaurus, and every pose that makes this animal is its own, and NOT the Carnotaurus' (which runs on long
legs and rams with its horns):
- the bulldog: short quick steps on short thick legs, the body low and level, the broad head carried low and still;
  a short run and the BURST, a few explosive strides out of a crouch, low to the ground;
- the HOLD: the bite that closes and does not open ("bite_hold"), the head wrenched side to side with the prey in the
  jaws ("hold_shake", a loop the Java plays while it holds) and the jaws opened with a toss ("hold_release");
- the dome: shown head-down and turned ("dome_display"), the low DOME SHOVE in a duel ("dome_shove", also its parry
  counter: a push from below, never a running butt), the threat at the waterhole ("waterhole_threat");
- the cannibal at a carcass: crouched over it, growling at whoever comes ("carcass_guard"), and the shed tooth spat
  out after a meal ("tooth_spit": it replaced its teeth every two months, D'Emic et al. 2019).
The fluid rules of docs/estudos/08 (breathing under everything, envelopes, three beats, the tail late). Signs on this
rig: body +x = nose up; neck/skull -x = down; jaw -x = open; tail pitch + = down; a + yaw swings the head to the
animal's RIGHT in game.

The poses were first written for the Carcharodontosaurus' long legs (hip 56 px); here the hip is at 27, so every body
translation written in this file goes through Q (add() below) and the steps through K (theropod.Plan.plant).
"""
import math

import os
import sys
_H = os.path.dirname(os.path.abspath(__file__))
_E = os.path.join(_H, "..", "_engine")
sys.path[:0] = [_H, _E, os.path.join(_E, "plans")]
import proto as P  # noqa: E402
import majunga  # noqa: E402
import theropod  # noqa: E402
from anim2 import add as add_raw, Track, smooth, ease_out, ease_in, back_out, lowest  # noqa: E402
from theropod import window, W, SIDES  # noqa: E402

TAILS = majunga.TAILS
BEND = (0.5, 0.7, 0.9, 0.95, 0.9)         # the thick base bends little, the thinner end more
SADDLE = ("hide", "fur", "strap", "iron", "bone", "rope")
K = 0.44                                  # this rig against the T. rex the template's poses were written on
Q = 0.5                                   # body translations against the Carcharodontosaurus' they were written for


def add(p, bone, rot=(0, 0, 0), pos=(0, 0, 0), scale=None):
    """anim2.add with the translations scaled to this short-legged rig"""
    return add_raw(p, bone, rot=rot, pos=tuple(Q * v for v in pos), scale=scale)


def model():
    m = majunga.build(saddle_on=True); P.pack(m, majunga.TEX_W); return m.spec()


S = model()
T = theropod.Plan(S, K=K, necks=("neck1", "neck2"), tails=TAILS, lie_drop=12.5, lie_ankle_y=4.4 * K, arms=0.5, jaw=1.0)
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
    add_raw(p, "root", pos=(0, -lo, 0))
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

# ------------------------------------------------------------------ the gait: heavy, deliberate, the head low
# (period s, stride in T. rex units, duty, lift, bob): the ground covered per cycle is stride * K model px
WALK = (1.4, 72, 0.62, 10, 1.4)
RUN = (0.7, 120, 0.42, 15, 2.4)
BURST = (0.55, 132, 0.36, 16, 2.6)
STALK = (WALK[0] * 1.5, WALK[1] * 0.7)


def walk(t):
    """the bulldog's walk: short quick steps, the low body rolling, the broad head low and still, the tail swinging
    late"""
    return gait(t, *WALK, roll=5.0, yaw=2.6, whip=1.0, still=0.95, arm_amp=1.0, head=-4)


def run(t):
    """its run: short and hard, the body level and low, the head out in front, the tail straight out"""
    p = gait(t, *RUN, lean=6, drop=3, head=-6, roll=2.6, yaw=1.6, whip=0.8, still=0.95, stance_clear=0.2,
             arm_amp=0.6, tail_up=2)
    arms(p, -6, 6)
    return p


def burst(t):
    """the burst (study 13, "Arrancada curta e baixa"): a few explosive strides low to the ground, the head and neck
    thrust out level, the jaws already parting, the tail a straight beam"""
    p = gait(t, *BURST, lean=9, drop=5, head=-10, roll=1.8, yaw=1.0, whip=0.6, still=1.0, stance_clear=0.25,
             arm_amp=0.4, tail_up=4)
    add(p, "jaw", rot=(-8 - 4 * max(0.0, wave(t, BURST[0] / 2)), 0, 0))
    arms(p, -10, 8)
    return p


def stalk(t):
    Tw, st, du, li, bo = WALK
    return gait(t, STALK[0], STALK[1], 0.74, li * 0.7, bo * 0.4, lean=3, drop=7, head=-12, roll=2.0, yaw=1.0,
                whip=0.3, still=1.0, arm_amp=0.5, tail_up=-1)


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
    """the plain bite: a reach of the deep head, the jaws shut at 0.50 s and it lets go, a flick of the head as it
    pulls out"""
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
GUARD_T = 2.6


def guard(t):
    """its guard: square and low, the broad head low and the dome forward, the mouth shut, a slow weave; it waits
    for the rival to come"""
    p = {}
    L = GUARD_T
    bounce = wave(t, L / 2)
    weave = wave(t, L)
    growl = tremor(t, (16 / L, 22 / L, 11 / L), (0.6, 0.4, 0.3))
    add(p, "body", rot=(-4 + 0.5 * bounce, 1.6 * weave, 1.2 * weave), pos=(0, -2.6 + 0.4 * bounce, 0))
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


# ------------------------------------------------------------------ its own: the crouch, the hold, the dome
AMBUSH_T = 4.0


def ambush_crouch(t):
    """crouched low and dead still by the water or in the dry grass (study 13, "ambush_crouch"): the short legs folded,
    the belly near the ground, the broad head low and level; only the head turns a fraction and the tail tip stirs"""
    p = {}
    L = AMBUSH_T
    br = wave(t, L / 2)
    look = float(tr((0, 0), (1.2, 0), (1.5, 3, ease_out), (2.4, 3), (2.7, -2, ease_out), (3.6, -2), (4.0, 0, smooth))(t))
    add(p, "body", rot=(-3 + 0.2 * br, 0, 0), pos=(0, -9 + 0.15 * br, 1.0))
    T.neck(p, (-7 - 0.15 * br, 0.6 * look, 0)); add(p, "skull", rot=(-2, look, 0))
    add(p, "jaw", rot=(-0.8, 0, 0))
    for k, (b, g) in enumerate(zip(TAILS, BEND)):
        twitch = 2.5 * math.sin(2 * math.pi * 2 * t / L - 0.9 * k) * (k >= 3)
        add(p, b, rot=(3.0 * g, twitch, 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(8 + 0.5 * wave(t, L / 2, -1 - 3 * o), 0, 0))
    return T.stand(p)


AMBUSH_LOOK_T = 2.6


def ambush_look(t):
    """its only gesture in the crouch: the head turns slowly to one side, holds on something, and back"""
    p = ambush_crouch(t)
    k = float(tr((0, 0), (0.6, 1, ease_out), (1.8, 1), (2.6, 0, smooth))(t))
    T.neck(p, (1.0 * k, 10 * k, 0)); add(p, "skull", rot=(0.5 * k, 6 * k, -2 * k))
    return p


# THE HOLD: bite_hold closes on the prey and ends in HOLD, the pose hold_shake loops on and hold_release starts from
def hold_pose(p, k=1.0):
    """braced and low, leaning back on the haunches, the neck bowed down and pulling, the jaws shut on the prey"""
    add(p, "body", rot=(-5 * k, 0, 0), pos=(0, -4 * k, 3 * k))
    T.neck(p, (-12 * k, 0, 0)); add(p, "skull", rot=(-6 * k, 0, 0)); add(p, "jaw", rot=(-3 * k, 0, 0))
    for b, g in zip(TAILS, BEND):
        add(p, b, rot=(-2.0 * g * k, 0, 0))
    arms(p, -8 * k, 6 * k)


def hold_legs(p, k=1.0, extra_l=0.0, extra_r=0.0):
    """the feet spread for the pull: the left forward, the right braced back"""
    T.plant(p, "l", 0, -3 * k + extra_l)
    T.plant(p, "r", 0, 6 * k + extra_r)


BITE_HOLD_T = 1.2     # the bite that holds: the jaws shut at 0.35 s (tick 7) and stay shut; the next blow at tick 24
BH_IN = tr((0, 0), (0.18, -0.4, ease_out), (0.35, 1, ease_in), (0.45, 0.95), (0.8, 0, smooth), (1.2, 0))
BH_JAW = tr((0, 0), (0.08, -4), (0.26, -38, ease_out), (0.33, -40), (0.37, -3, ease_in), (1.2, -3))


def bite_hold(t):
    """the bite that holds (study 13, "Segura e não solta"): a short hard reach low and in, the jaws slam shut at
    0.35 s and stay shut; the head does not let go but wrenches back and down into the hold, the feet bracing"""
    p = {}
    k = float(BH_IN(t))
    hold = smooth((t - 0.4) / 0.4)
    hit = math.exp(-max(0.0, t - 0.35) / 0.08) * smooth((t - 0.33) / 0.03)
    add(p, "body", rot=(1.5 * max(0.0, k) + 1.5 * hit, 0, 0), pos=(0, -1.5 * abs(k), -5.0 * max(0.0, k) + 2.0 * max(0.0, -k)))
    T.neck(p, (-6 * max(0.0, k) + 6 * min(0.0, k) + 3 * hit, 0, 0))
    add(p, "skull", rot=(-2 * max(0.0, k) + 4 * hit, 0, 0))
    add(p, "jaw", rot=(float(BH_JAW(t)) + 3 * hold, 0, 0))
    hold_pose(p, hold)
    trail(p, t, lambda u: 3 * math.exp(-max(0.0, u - 0.35) / 0.18) * smooth((u - 0.33) / 0.03), axis=0, delay=0.06)
    alive_upper(p, t, k=0.2)
    up = steps(t, 0.45, 0.75, 5.0)
    T.plant(p, "l", 0, -3 * hold)
    T.plant(p, "r", up, 6 * smooth((t - 0.45) / 0.3), 6 * up / 5.0, -10 * min(1.0, up / 5.0), clear=0.7 * min(1.0, up / 2.0) - 0.05)
    return p


HOLD_SHAKE_T = 0.8


def hold_shake(t):
    """holding on (loop, 2 to 3 s in game): the head wrenched hard to one side and the other, twice a loop, the body
    twisting against it and the tail swinging the other way; the jaws never open"""
    p = {}
    L = HOLD_SHAKE_T
    sh = math.sin(2 * math.pi * 2 * t / L)
    sh2 = math.sin(2 * math.pi * 2 * t / L - 0.6)
    hold_pose(p)
    add(p, "body", rot=(0.8 * abs(sh), -4 * sh2, 3 * sh2), pos=(0, -0.6 * abs(sh), 0))
    T.neck(p, (-2 * abs(sh), 18 * sh, -6 * sh)); add(p, "skull", rot=(0, 8 * sh, 14 * sh))
    add(p, "jaw", rot=(-0.6 * abs(sh), 0, 0))
    for k, (b, g) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(0, 5 * g * math.sin(2 * math.pi * 2 * t / L - 1.2 - 0.6 * k), 0))
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, 4 * sh2, 0))
    hold_legs(p)
    return p


HOLD_RELEASE_T = 1.0


def hold_release(t):
    """letting go: the jaws open with a toss of the head up and aside (the prey thrown off), one step back out of the
    hold, and it stands"""
    p = {}
    k = 1 - smooth((t - 0.15) / 0.6)
    toss = bump(t, 0.28, 0.1)
    hold_pose(p, k)
    add(p, "body", rot=(2 * toss, 0, 0))
    T.neck(p, (10 * toss, -12 * toss, 0)); add(p, "skull", rot=(8 * toss, -6 * toss, -8 * toss))
    add(p, "jaw", rot=(-28 * window(t, 0.18, 0.55, 0.1), 0, 0))
    trail(p, t, lambda u: 4 * bump(u, 0.35, 0.15), delay=0.06)
    alive_upper(p, t, k=0.3)
    back = steps(t, 0.4, 0.75, 4.0)
    T.plant(p, "l", back, -3 * k)
    T.plant(p, "r", 0, 6 * k)
    return p


DOME_SHOVE_T = 1.3    # the duel's signature blow: the dome drives in from below at 0.45 s (tick 9), 26 ticks


def dome_shove(t):
    """the low dome shove (study 13, "Duelo baixo"; the dome was hollow, so a push, never a running butt): the head
    dips below the rival's and turns the dome forward, one short heavy step, and the whole low body pushes UP and in
    from beneath at 0.45 s; it does not lift its feet off"""
    p = {}
    k = float(tr((0, 0), (0.25, -0.6, ease_out), (0.45, 1, ease_in), (0.6, 0.9), (1.3, 0, back_out))(t))
    hit = math.exp(-max(0.0, t - 0.45) / 0.1) * smooth((t - 0.43) / 0.03)
    add(p, "body", rot=(-4 * max(0.0, -k) + 4 * max(0.0, k) + 2 * hit, 0, 0),
        pos=(0, -3.0 * max(0.0, -k) - 1.0 * max(0.0, k), -5.0 * max(0.0, k) + 2.0 * max(0.0, -k)))
    T.neck(p, (-14 * max(0.0, -k) - 8 * max(0.0, k) + 3 * hit, 0, 0))
    add(p, "skull", rot=(-18 * abs(k) + 6 * hit, 0, 3 * decay(t, 0.5, 0.15, 5.0)))
    add(p, "jaw", rot=(-1.0, 0, 0))
    trail(p, t, lambda u: 4 * math.exp(-max(0.0, u - 0.45) / 0.18) * smooth((u - 0.43) / 0.03), axis=0, delay=0.06)
    trail(p, t, lambda u: 3 * decay(u, 0.5, 0.2, 2.5), delay=0.06)
    arms(p, -6 * max(0.0, k))
    alive_upper(p, t, k=0.3)
    up = steps(t, 0.2, 0.42, 4.0) + steps(t, 0.85, 1.1, 3.0)
    fwd = smooth((t - 0.2) / 0.22) * (1 - smooth((t - 0.85) / 0.25))
    T.plant(p, "l", up, -6 * fwd, 6 * up / 4.0, -10 * min(1.0, up / 4.0), clear=0.7 * min(1.0, up / 2.0) - 0.05)
    T.plant(p, "r", 0, 3 * fwd, 14 * fwd, 6 * fwd)
    return p


DOME_DISPLAY_T = 2.6


def dome_display(t):
    """to a rival or a player who comes close (study 13: it warns at 8 blocks): the head lowered and turned half aside
    so the dome stands against the sky, the neck arched, a low rumble; then back"""
    p = {}
    k = float(tr((0, 0), (0.5, 1, ease_out), (2.0, 1), (2.6, 0, smooth))(t))
    rum = tremor(t, (13.0, 18.1, 8.7), (0.5, 0.3, 0.2)) * window(t, 0.6, 1.9, 0.15)
    add(p, "body", rot=(-2 * k, 5 * k, -2 * k), pos=(0, -1.5 * k, 0))
    T.neck(p, (-10 * k + 0.3 * rum, 18 * k, -4 * k)); add(p, "skull", rot=(-10 * k, 10 * k, -18 * k + 0.4 * rum))
    add(p, "jaw", rot=(-1.5 * k - 0.4 * abs(rum), 0, 0))
    trail(p, t, lambda u: -5 * float(tr((0, 0), (0.5, 1, ease_out), (2.0, 1), (2.6, 0, smooth))(u)), delay=0.08)
    arms(p, -4 * k)
    alive_upper(p, t, k=0.3)
    return T.stand(p)


WATERHOLE_T = 2.8


def waterhole_threat(t):
    """guarding the waterhole in the dry season (study 13, a hypothesis after Rogers 2005): the head down so the dome
    faces whoever comes, the jaws parted in a hiss, a stamp of the left foot at 1.0 s, the tail lashing once"""
    p = {}
    k = float(tr((0, 0), (0.4, 1, ease_out), (2.3, 1), (2.8, 0, smooth))(t))
    hs = tremor(t, (15.0, 21.3, 9.9), (0.6, 0.4, 0.3)) * window(t, 0.4, 2.2, 0.1)
    land = bump(t, 1.05, 0.05)
    add(p, "body", rot=(-3 * k + 1.0 * land, 0, 0), pos=(0, -2.0 * k - 1.0 * land, 0))
    T.neck(p, (-12 * k + 0.4 * hs, 0, 0)); add(p, "skull", rot=(-12 * k + 0.4 * hs, 0, 0))
    add(p, "jaw", rot=(-10 * k * window(t, 0.5, 2.0, 0.2) - 0.8 * abs(hs), 0, 0))
    trail(p, t, lambda u: 8 * decay(u, 1.1, 0.3, 1.6), delay=0.08)
    arms(p, -6 * k)
    alive_upper(p, t, k=0.3)
    up = steps(t, 0.7, 1.05, 6.0)
    T.plant(p, "l", up, -2 * smooth((t - 0.7) / 0.35), 6 * up / 6.0, -12 * min(1.0, up / 6.0), clear=0.6 * min(1.0, up / 2.0) - 0.05)
    T.plant(p, "r")
    return p


CARCASS_GUARD_T = 3.0


def carcass_guard(t):
    """over a carcass, its own kind's too (Rogers, Krause & Curry Rogers 2003; loop): crouched over the meat, the head
    low over it and the eyes up, a growl shaking the throat, a snap of the jaws at 1.8 s"""
    p = {}
    L = CARCASS_GUARD_T
    br = wave(t, L / 2)
    growl = tremor(t, (14 / L * 3, 19 / L * 3, 9 / L * 3), (0.7, 0.4, 0.3))
    snap = window(t, 1.65, 1.95, 0.06)
    add(p, "body", rot=(-5 + 0.3 * br, 0, 0), pos=(0, -6 + 0.2 * br, 0))
    T.neck(p, (-14 + 0.4 * growl + 4 * snap, 2 * wave(t, L, 0.4), 0)); add(p, "skull", rot=(6 + 0.3 * growl, 0, 0))
    add(p, "jaw", rot=(-2 - 0.6 * abs(growl) - 24 * snap, 0, 0))
    for k, (b, g) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(1.5 * g, 2.0 * g * wave(t, L, -0.7 * k), 0))
    arms(p, 6)
    return T.stand(p)


TOOTH_SPIT_T = 1.8


def tooth_spit(t):
    """after eating: the jaws work, the head shakes, and a shed tooth is spat out with a jerk at 1.0 s (it replaced its
    whole set every couple of months, D'Emic et al. 2019)"""
    p = {}
    chew = math.sin(2 * math.pi * 3.0 * t) * window(t, 0.1, 0.8, 0.1)
    jerk = bump(t, 1.0, 0.07)
    add(p, "body", rot=(-1 * jerk, 0, 0), pos=(0, 0, -1.5 * jerk))
    T.neck(p, (-4 + 6 * jerk, 2 * chew, 0)); add(p, "skull", rot=(-3 + 4 * jerk, 3 * chew, 6 * chew))
    add(p, "jaw", rot=(-4 - 4 * max(0.0, chew) - 18 * window(t, 0.95, 1.15, 0.05), 0, 0))
    trail(p, t, lambda u: 1.5 * bump(u, 1.05, 0.15), axis=0)
    alive(p, t, k=0.5)
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
    "scan": (scan, SCAN_T, False, "Parado", "ergue a cabeça e olha em volta"),
    "walk": (walk, WALK[0], True, "Movimento", "andar de buldogue: passos curtos, corpo baixo, cabeça parada"),
    "run": (run, RUN[0], True, "Movimento", "corrida curta: corpo baixo, cabeça à frente"),
    "burst": (burst, BURST[0], True, "Movimento", "a arrancada curta: passadas explosivas e rentes, cabeça esticada"),
    "stalk": (stalk, STALK[0], True, "Movimento", "chegando perto, baixo, cabeça no alvo"),
    "swim": (BASE["swim"][0], 1.6, True, "Movimento", "nadando"),
    "turn_left": (turn_left, TURN_T, True, "Movimento", "girando no lugar para a esquerda"),
    "turn_right": (turn_right, TURN_T, True, "Movimento", "girando no lugar para a direita"),
    "walk_tired": (walk_tired, WALK_TIRED_T, True, "Movimento", "andando cansado, boca aberta"),
    "idle_tired": (idle_tired, IDLE_TIRED_T, True, "Parado", "parado cansado, ofegando"),
    "roar": (roar, ROAR_T, False, "Voz", "rugido baixo e para a frente"),
    "roar_loud": (roar_loud, ROAR_LOUD_T, False, "Voz", "rugido forte: um passo à frente, cabeça alta, três pulsos"),
    "call": (with_breath(BASE["call"][0], 0.4), 2.6, False, "Voz", "ronco baixo"),
    "threat": (growl_low, GROWL_T, False, "Voz", "rosnado de boca fechada, cabeça baixa de lado"),
    "dome_display": (dome_display, DOME_DISPLAY_T, False, "Voz", "cabeça baixa e meio de lado: mostra o domo, ronco baixo"),
    "waterhole_threat": (waterhole_threat, WATERHOLE_T, False, "Voz", "guarda do bebedouro: domo à frente, sopro, pisão"),
    "attack": (slash_bite, BITE_T, False, "Combate", "mordida: estica a cabeça, fecha (0,50 s) e solta"),
    "bite_hold": (bite_hold, BITE_HOLD_T, False, "Combate", "morde (0,35 s) e não solta: puxa para trás e para baixo"),
    "hold_shake": (hold_shake, HOLD_SHAKE_T, True, "Combate", "segurando: sacode a cabeça de um lado para o outro"),
    "hold_release": (hold_release, HOLD_RELEASE_T, False, "Combate", "solta: abre a boca jogando a cabeça de lado"),
    "attack_quick": (attack_quick, QUICK_T, False, "Combate", "mordida rápida (0,30 s)"),
    "bite_low": (bite_low, BITE_LOW_T, False, "Combate", "varre a cabeça rente ao chão (0,40 s)"),
    "bite_side": (bite_side, BITE_SIDE_T, False, "Combate", "a cabeça vem de lado em arco (0,45 s)"),
    "stomp": (stomp, STOMP_T, False, "Combate", "pisão em coisa pequena (0,90 s)"),
    "shove": (shove, SHOVE_T, False, "Combate", "empurrão de ombro, peito a peito"),
    "hurt": (with_breath(BASE["hurt"][0], 0.2), 0.6, False, "Combate", "ao levar dano"),
    "death": (regrounded(BASE["death"][0]), 3.0, False, "Combate", "ao morrer"),
    "eat": (rip_feed, EAT_T, False, "Comer", "arranca pedaços puxando com o pescoço"),
    "drink": (with_breath(BASE["drink"][0], 0.3), 4.0, False, "Comer", "bebendo"),
    "ambush_crouch": (ambush_crouch, AMBUSH_T, True, "Caça", "agachado rente ao chão, cabeça baixa, imóvel"),
    "carcass_guard": (carcass_guard, CARCASS_GUARD_T, True, "Comer", "agachado sobre a carcaça, rosna e estala a boca"),
    "tooth_spit": (tooth_spit, TOOTH_SPIT_T, False, "Comer", "depois de comer: mastiga, sacode e cospe um dente"),
    "ambush_look": (ambush_look, AMBUSH_LOOK_T, False, "Caça", "o único gesto na tocaia: a cabeça vira devagar, sem levantar"),
    "guard": (guard, GUARD_T, True, "Duelo", "em guarda: baixo, o domo à frente, espera"),
    "strafe_left": (strafe_left, STRAFE_T, True, "Duelo", "passos de lado, para a esquerda"),
    "strafe_right": (strafe_right, STRAFE_T, True, "Duelo", "passos de lado, para a direita"),
    "feint": (feint, FEINT_T, False, "Duelo", "finta: a mordida que para curta"),
    "block": (block, BLOCK_T, False, "Duelo", "apara com o crânio"),
    "recoil": (recoil, RECOIL_T, False, "Duelo", "o golpe foi aparado: cabeça de lado, um passo atrás"),
    "submit": (submit, SUBMIT_T, False, "Duelo", "perdeu: cabeça baixa de lado, vira e vai"),
    "dome_shove": (dome_shove, DOME_SHOVE_T, False, "Duelo", "empurrão de domo por baixo (0,45 s)"),
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

# the duel's committed moves at the fixed lengths (majungafight.py): lunge (it bites and holds), parry (the dome
# butt as its counter), stagger
import majungafight as FIGHT  # noqa: E402
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
