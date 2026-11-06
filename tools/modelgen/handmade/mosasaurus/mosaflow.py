"""Mosasaurus: the fluid set (06/11/2026), in the spirit of the T. rex's (tyrannosaurus/rexflow.py, docs/estudos/
08_ANIMACAO_RAXIORES.md) but in the Mosasaurus' own style: a tuna-bodied ambush hunter of the open sea, not a walker.

What changes, and why it is this animal's:
  * THE SWIM IS A TRAVELLING WAVE THAT GROWS TO THE FLUKE. The trunk stays stiff (Lindgren et al. 2011, 2013: a late
    mosasaur swam like a shark), so the wave is almost nothing at the hips and each tail segment is later and wider than
    the one before; the fluke adds a flick at each reversal (a second harmonic). The front answers the tail: the body
    recoils against each beat (yaw and a little sideways drift), it rolls a touch, and the skull counters the neck so the
    eyes stay on the line of travel. The flippers trim a beat late, never held rigid.
  * NOTHING STOPS. It is an air-breather hanging in the water: every one-shot carries `alive` (a slow bob, the throat
    pumping, the flippers sculling out of step, the tail swaying from base to tip). The idle is 8 s of cycles whose
    periods divide the loop but never line up (breath 8/3 s, sculling 4 s and 8/5 s, drift 8 s), with a look round.
  * NOTHING SNAPS ON OR OFF: every effect fades in and out through `window`; the throat shiver of the gape and the growl
    of the spar are organic tremors (three sines that never repeat), not a switched buzz.
  * EVERY STRIKE HAS THREE BEATS: anticipation (the head draws back, the tail cocks), the strike (the jaws shut in under a
    tenth of a second), and a settle that passes the rest pose a little and comes back (`back_out`); the tail follows
    every move of the front with a growing delay (`trail`), the fluke last.
  * ITS OWN SIGNATURE: `ram_bite`, from the bitten skulls of mosasaurs (Lindgren et al. 2013, the healed and unhealed
    bite marks on the heads of other mosasaurs; a ram followed by a sideways clamp, as sharks and orcas do): it cocks
    the tail, drives in with hard beats of the fluke, rolls onto its side as it arrives so the jaws come in flat, rams with the
    head and clamps sideways (the hit at 0.75 s), wrenches twice and lets go.
  * `turn_left` / `turn_right`: the turn of a hovering swimmer, not of a walker: the body bends into a C (the head and the
    fluke both toward the inside), the inside fore flipper brakes, the outside one sculls, it banks into the turn.

Signs on this rig (mosaanims): body +x = nose up; neck/skull -x = nose down; jaw -x = open; + yaw on the neck swings the
head to the animal's right in game; flipper l: z + = the tip up, y - = swept back (r mirrored); root pos z - = forward.
"""
import math

from anim2 import add, smooth, ease_in, ease_out, back_out
import mosaanims as A

TAILS = A.TAILS
WAVE = A.WAVE
tr, f, window, flip, jaw, W = A.tr, A.f, A.window, A.flip, A.jaw, A.W

# the originals some fluid versions are built on
_O = {n: v[0] for n, v in A.ANIMS.items()}


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def tremor(t, f=(7.3, 11.1, 4.7), amp=(1.0, 0.55, 0.35), phase=0.0):
    """an organic shiver: three sines at frequencies that never line up (-1.9 .. 1.9 at most)"""
    return sum(a * math.sin(2 * math.pi * fr * t + phase * (i + 1) + 1.3 * i) for i, (fr, a) in enumerate(zip(f, amp)))


def trail(p, t, fn, gain=(0.5, 0.8, 1.2, 1.7, 2.3), delay=0.06, axis=1, bones=TAILS, loop=None):
    """follow-through down the tail: segment k takes fn(t - (k+1)*delay) * gain[k] on `axis`; the fluke arrives last"""
    for k, b in enumerate(bones):
        u = t - delay * (k + 1)
        v = fn(u % loop if loop else max(0.0, u)) * gain[k]
        r = [0.0, 0.0, 0.0]; r[axis] = v
        add(p, b, rot=tuple(r))


def bump(t, c, w):
    return math.exp(-((t - c) / w) ** 2)


def swimwave(p, t, T, amp=1.0, bias=0.0, lag=0.62):
    """the travelling wave: one beat per T seconds; each segment later (lag rad) and wider (WAVE) than the one before; the
    front recoils against it and the skull holds the gaze. bias bends the whole tail to one side (a turn)."""
    ph = W(t, T)
    for i, b in enumerate(TAILS):
        add(p, b, rot=(0, amp * WAVE[i] * math.sin(ph - lag * i) + bias * (i + 1), 0))
    add(p, "fluke", rot=(0, 0.18 * amp * WAVE[4] * math.sin(2 * ph - lag * 4 - 0.9), 0))   # the flick at each reversal
    by = -0.6 * amp * math.sin(ph + 0.35)
    ny = -0.9 * amp * math.sin(ph + 0.75)
    add(p, "body", rot=(0, by, 0.9 * amp * math.sin(ph - 0.3)), pos=(0.35 * amp * math.sin(ph + 0.5), 0, 0))
    add(p, "neck", rot=(0, ny, 0))
    add(p, "skull", rot=(0, -0.7 * (by + ny), -0.5 * amp * math.sin(ph - 0.3)))
    return ph


def alive(p, t, k=1.0, period=3.2):
    """the breathing layer of an air-breather hanging in the water: a slow bob, the throat pumping, the flippers sculling
    out of step, the tail swaying from base to tip, the jaw parting a hair on the out-breath"""
    br = wave(t, period)
    add(p, "root", pos=(0, 0.45 * k * br, 0))
    add(p, "body", rot=(0.5 * k * wave(t, period, -0.4), 0, 0))
    add(p, "neck", rot=(-0.6 * k * wave(t, period, -0.9), 0, 0))
    add(p, "skull", rot=(-0.4 * k * wave(t, period, -1.4), 0, 0))
    add(p, "jaw", rot=(-0.8 * k * max(0.0, wave(t, period, -1.0)), 0, 0))
    add(p, "throat", scale=(1.0, 1.0 + 0.05 * k * wave(t, period, -0.7), 1.0))
    flip(p, "f", (0, 2.0 * k * wave(t, period, -0.5), 3.0 * k * wave(t, period, -1.1)))
    flip(p, "h", (0, 1.5 * k * wave(t, period, -1.6), 2.4 * k * wave(t, period, -2.2)))
    for i, b in enumerate(TAILS):
        add(p, b, rot=(0, 0.5 * k * (i + 1) * wave(t, period * 2, -0.6 * i), 0))
    return br


# ------------------------------------------------------------------ movement
IDLE_T = 8.0
LOOK = tr((0, (0, 0)), (1.4, (0, 0)), (2.0, (2, 12), ease_out), (3.2, (2, 12)), (3.8, (-1, -9), ease_out), (5.2, (-1, -9)),
          (5.8, (3, 3), ease_out), (7.0, (3, 3)), (7.7, (0, 0), ease_in), (8.0, (0, 0)))


def idle(t):
    """hovering: lazy sculls out of step, a slow bob with the breath, the tail drifting in an S, a look round"""
    T = IDLE_T; p = {}
    br = wave(t, T / 3)
    drift = wave(t, T, 0.5) + 0.35 * wave(t, T / 2, 1.3)
    swimwave(p, t, T / 2, 0.32, bias=0.35 * drift)
    add(p, "root", pos=(0.3 * drift, 0.7 * br, 0))
    add(p, "body", rot=(0.8 * br, -0.6 * drift, 0.8 * wave(t, T, 2.0)))
    lp, ly = (float(v) for v in LOOK(t))
    add(p, "neck", rot=(-0.6 * wave(t, T / 3, -0.6) + 0.5 * lp, 0.5 * ly + 0.8 * drift, 0))
    add(p, "skull", rot=(-0.4 * wave(t, T / 3, -1.1) + 0.5 * lp, 0.5 * ly, -0.08 * ly))
    add(p, "jaw", rot=(-0.6 - 1.2 * smooth(max(0.0, wave(t, T / 3, -0.9))), 0, 0))
    add(p, "throat", scale=(1.0, 1.0 + 0.06 * wave(t, T / 3, -0.7), 1.0))
    flip(p, "f", (0, 4 * wave(t, T / 2), 5 * wave(t, T / 2, 0.7) + 1.2 * wave(t, T / 5, 0.2)))
    flip(p, "h", (0, 3 * wave(t, T / 2, 2.0), 4 * wave(t, T / 2, 2.7) + 1.0 * wave(t, T / 5, 1.9)))
    return p


def swim(t):
    """cruising: the wave grows from the stiff trunk to the fluke, the front recoils against it, the flippers trim late"""
    T = 1.6; p = {}
    ph = swimwave(p, t, T, 1.0)
    flip(p, "f", (0, -8 + 1.5 * math.sin(ph - 1.2), 3 * math.sin(ph + 1.0)))
    flip(p, "h", (0, -10 + 1.5 * math.sin(ph - 1.8), 2 * math.sin(ph + 1.6)))
    add(p, "root", pos=(0, 0.4 * math.sin(2 * ph), 0))
    add(p, "body", rot=(0.5 * math.sin(2 * ph - 0.5), 0, 0))
    add(p, "throat", scale=(1.0, 1.0 + 0.04 * math.sin(ph - 0.4), 1.0))
    return p


def walk(t):
    """the slow patrol along the bottom: lazy beats, the head a little down, the flippers spread and trimming"""
    T = 2.4; p = {}
    ph = swimwave(p, t, T, 0.65)
    flip(p, "f", (0, -2 + 1.2 * math.sin(ph - 1.0), 4 + 2 * math.sin(ph)))
    flip(p, "h", (0, -4 + 1.0 * math.sin(ph - 1.6), 3 + 2 * math.sin(ph + 1.0)))
    add(p, "neck", rot=(-1.5 + 0.5 * math.sin(ph - 0.8), 0, 0))
    add(p, "root", pos=(0, 0.3 * math.sin(2 * ph - 0.3), 0))
    add(p, "throat", scale=(1.0, 1.0 + 0.04 * math.sin(ph), 1.0))
    return p


def run(t):
    """the burst: big fast beats, the flippers swept flat, the head driving and held steady against the recoil"""
    T = 0.8; p = {}
    ph = swimwave(p, t, T, 1.5, lag=0.7)
    flip(p, "f", (0, -40 + 2 * math.sin(ph - 1.4), 12 + 1.5 * math.sin(ph - 0.6)))
    flip(p, "h", (0, -42 + 2 * math.sin(ph - 2.0), 10 + 1.5 * math.sin(ph - 1.2)))
    add(p, "neck", rot=(-2, 0, 0))
    add(p, "root", pos=(0, 0.5 * math.sin(2 * ph), 0))
    add(p, "body", rot=(-0.6 * math.sin(2 * ph - 0.4), 0, 0))
    return p


def _turn(t, s):
    """turning while hovering: the body bends into a C toward the inside (the head and the fluke both in), the inside
    fore flipper spread forward as a brake, the outside one sculling, the body banking; two slow beats per loop"""
    T = TURN_T; p = {}
    ph = swimwave(p, t, T / 2, 0.55, bias=-2.2 * s)
    k = 1.0 + 0.12 * wave(t, T, 0.4)                 # the bend breathes a little, never a held pose
    add(p, "body", rot=(0.4 * wave(t, T / 2, 1.0), 5 * s * k, 5 * s * k))
    add(p, "neck", rot=(0, 12 * s * k + 1.0 * wave(t, T / 2, 0.3), 0))
    add(p, "skull", rot=(0.4 * wave(t, T / 2, -0.8), 7 * s * k, 2 * s))
    ins, out = ("r", "l") if s > 0 else ("l", "r")
    m = 1 if ins == "l" else -1                      # the right flippers are mirrored on y and z
    add(p, f"flipper_f{ins}", rot=(0, m * (14 + 2 * wave(t, T / 2, 0.5)), m * (10 + 2 * wave(t, T / 2, 1.1))))
    add(p, f"flipper_f{out}", rot=(0, -m * (-6 + 9 * wave(t, T / 2)), -m * (4 + 5 * wave(t, T / 2, 0.8))))
    flip(p, "h", (0, -4 + 2 * wave(t, T / 2, 1.6), 3 * wave(t, T / 2, 2.2)))
    add(p, "root", pos=(0, 0.4 * wave(t, T / 2, 0.6), 0))
    add(p, "throat", scale=(1.0, 1.0 + 0.04 * wave(t, T / 2, -0.4), 1.0))
    return p


TURN_T = 2.0


def turn_left(t):
    return _turn(t, -1)


def turn_right(t):
    return _turn(t, 1)


def stranded(t):
    """out of the water: the old thrash, now with a gasp that shivers the throat and the tail following the body late"""
    p = _O["stranded"](t)
    gasp = max(0.0, math.sin(W(t, 1.6) + 0.8))
    add(p, "throat", scale=(1.0, 1.0 + 0.04 * tremor(t, (6.25, 9.375, 3.75)) * gasp, 1.0))
    add(p, "skull", rot=(1.2 * gasp, 0, 0.6 * tremor(t, (5.0, 8.125, 3.125), (0.6, 0.3, 0.2))))
    trail(p, t, lambda u: 2.0 * math.sin(W(u, 1.6) - 0.6), gain=(0.3, 0.6, 0.9, 1.2, 0.0), delay=0.07, loop=1.6)
    return p


# ------------------------------------------------------------------ its own, made fluid
def ambush(t):
    """the rise from below (snap kept at 1.05 s): now with the breath under it until the burst and the tail following the
    pitch-up late; the level-out passes a little nose-down and comes back"""
    p = _O["ambush"](t)
    alive(p, t, k=1.0 - smooth(t / 0.3) * (1 - smooth((t - 1.3) / 0.3)))
    trail(p, t, lambda u: -0.12 * float(tr((0, 0), (0.35, 42, ease_out), (1.1, 46), (1.6, 0))(u)), gain=(0.3, 0.5, 0.7, 0.9, 1.1),
          axis=0, delay=0.07)
    add(p, "body", rot=(-5 * bump(t, 1.45, 0.12), 0, 0))
    add(p, "skull", rot=(-3 * bump(t, 1.08, 0.05), 0, 0))     # the jolt of the snap
    return p


def breach(t):
    p = _O["breach"](t)
    trail(p, t, lambda u: 4.0 * math.sin(W(u, 0.6)) * window(u, 0.3, 1.0, 0.2), delay=0.07)
    splash = bump(t, 2.15, 0.1)
    add(p, "neck", rot=(-4 * splash, 0, 0)); add(p, "skull", rot=(-3 * bump(t, 2.22, 0.1), 0, 0))
    alive(p, t, k=1.0 - window(t, 0.2, 2.1, 0.2))
    return p


def breathe(t):
    """up for air: the blow now shivers the throat (a short organic tremor), the head settles after it"""
    p = _O["breathe"](t)
    env = window(t, 0.75, 1.05, 0.08)
    add(p, "throat", scale=(1.0, 1.0 + 0.05 * tremor(t, (9.1, 13.4, 6.2)) * env, 1.0))
    add(p, "skull", rot=(1.2 * tremor(t, (8.3, 12.7, 5.1)) * env, 0, 0))
    alive(p, t, k=0.6, period=2.6)
    return p


def swallow(t):
    p = _O["swallow"](t)
    alive(p, t, k=0.5, period=2.4)
    trail(p, t, lambda u: 1.5 * sum(bump(u, c, 0.15) * (1 if i % 2 == 0 else -1) for i, c in enumerate((0.62, 1.22, 1.82))), delay=0.08)
    return p


def shake(t):
    p = _O["shake"](t)
    k = window(t, 0.1, 1.2, 0.15)
    trail(p, t, lambda u: 5 * math.sin(W(u, 0.45)) * window(u, 0.1, 1.2, 0.15), gain=(0.4, 0.7, 1.0, 1.4, 1.8), delay=0.05)
    add(p, "throat", scale=(1.0, 1.0 + 0.04 * tremor(t) * k, 1.0))
    alive(p, t, k=0.5)
    return p


def spar(t):
    """two males: the gape held with a growl in the throat (an organic tremor, fading in and out), then the clamp at the
    rival's head in three beats: the head cocks away, swings in, clamps and wrenches, lets go and settles"""
    p = _O["spar"](t)
    env = window(t, 0.35, 1.35, 0.2)
    add(p, "throat", scale=(1.0, 1.0 + 0.08 * env + 0.05 * tremor(t, (8.7, 12.1, 5.6)) * env, 1.0))
    add(p, "jaw", rot=(-1.4 * tremor(t, (9.4, 13.7, 6.1), phase=1.9) * env, 0, 0))
    add(p, "neck", rot=(0, -8 * bump(t, 1.3, 0.1) + 4 * bump(t, 2.45, 0.12), 0))   # the cock before the clamp, the overshoot after
    trail(p, t, lambda u: -0.25 * float(tr((0, 0), (1.3, 0), (1.5, 26, ease_out), (2.2, 26), (2.6, 0))(u)), delay=0.07)
    alive(p, t, k=0.5)
    return p


def gape(t):
    """the warning gape: the throat shivers while the jaws are wide (an envelope, never a switch), the sweep leads the
    tail, and the clap shut jolts the head"""
    p = _O["gape"](t)
    env = window(t, 0.45, 1.9, 0.22)
    add(p, "throat", scale=(1.0, 1.0 + 0.06 * tremor(t, (7.1, 10.9, 4.3)) * env, 1.0))
    add(p, "jaw", rot=(-1.8 * tremor(t, (9.6, 14.1, 6.3), phase=0.7) * env, 0, 0))
    add(p, "skull", rot=(1.0 * tremor(t, (8.2, 12.4, 5.6), phase=1.3) * env + 3 * bump(t, 2.08, 0.06), 0, 0))
    trail(p, t, lambda u: -6 * window(u, 0.5, 1.9, 0.25) * math.sin(W(u - 0.5, 1.4)), gain=(0.3, 0.5, 0.8, 1.1, 1.5), delay=0.1)
    alive(p, t, k=0.4, period=2.8)
    return p


def spyhop(t):
    p = _O["spyhop"](t)
    alive(p, t, k=0.6, period=4.0)
    return p


def birth(t):
    p = _O["birth"](t)
    alive(p, t, k=0.6, period=3.6)
    trail(p, t, lambda u: 2.5 * sum(window(u, a, a + 0.5, 0.2) for a in (1.0, 1.9)), gain=(0, 0, 0.6, 1.0, 1.6), delay=0.1)
    return p


# ------------------------------------------------------------------ combat
ATTACK_T = 0.8
A_GAPE = tr((0, 0), (0.22, 1, ease_out), (0.36, 1.05), (0.42, 0, ease_in), (0.8, 0))
A_DRIVE = tr((0, 0), (0.2, -2.2, ease_out), (0.42, 7, ease_in), (0.8, 0, back_out))
A_NECK = tr((0, 0), (0.2, 6, ease_out), (0.42, -5, ease_in), (0.8, 0, back_out))


def attack(t):
    """the bite in three beats (the snap at 0.42 s, as before): the head draws back with the jaws gaping, the lunge, the
    snap; the settle passes the rest pose and comes back, the tail answering last"""
    p = {}
    g = f(A_GAPE, t)
    jaw(p, 34 * g, 9 * g)
    nk = f(A_NECK, t)
    add(p, "neck", rot=(nk, 0, 0)); add(p, "skull", rot=(0.4 * nk - 3 * bump(t, 0.44, 0.04), 0, 0))
    add(p, "root", pos=(0, 0, -f(A_DRIVE, t)))
    add(p, "body", rot=(0.4 * nk, 0, 0))
    swimwave(p, t, 0.4, f(tr((0, 0.4), (0.25, 1.4), (0.5, 1.0), (0.8, 0.4)), t))
    trail(p, t, lambda u: 0.35 * f(A_NECK, u), gain=(0.4, 0.6, 0.8, 1.0, 1.2), axis=0, delay=0.05)
    flip(p, "f", (0, -30 * window(t, 0.15, 0.6, 0.1), 6))
    alive(p, t, k=0.5)
    return p


RAM_T = 1.8
RAM_HIT = 0.75
R_DRIVE = tr((0, 0), (0.42, -2.5, ease_out), (0.74, 12, ease_in), (0.8, 10.5), (1.3, 9.5), (1.8, 0, back_out))
R_ROLL = tr((0, 0), (0.4, -4, ease_out), (0.72, 28, ease_out), (1.3, 26), (1.8, 0, back_out))
R_YAW = tr((0, 0), (0.42, -14, ease_out), (0.75, 9, ease_in), (0.85, 7), (1.3, 6), (1.8, 0, back_out))
R_GAPE = tr((0, 0), (0.4, 0.1), (0.66, 1, ease_out), (0.75, 0, ease_in), (1.32, 0.04), (1.42, 0.35, ease_out), (1.56, 0.05), (1.8, 0))
R_COCK = tr((0, 0), (0.42, 1, ease_out), (0.55, 0.6), (0.75, 0), (1.8, 0))


def wrench(t):
    """after the clamp: two hard wrenches of the head, the first the widest, dying out"""
    return sum(a * bump(t, c, 0.08) for c, a in ((0.95, 1.0), (1.14, -0.7), (1.3, 0.3)))


def ram_bite(t):
    """the ram and the side bite (Lindgren et al. 2013): the tail cocks to one side and the head draws back; hard beats
    of the fluke drive it in, the body rolling onto its side so the jaws come in flat; the head rams and clamps sideways (the
    hit at 0.75 s); two wrenches; it lets go, rolls back level and settles past the rest pose"""
    p = {}
    drive = f(R_DRIVE, t); roll = f(R_ROLL, t); yw = f(R_YAW, t); g = f(R_GAPE, t); cock = f(R_COCK, t)
    impact = bump(t, RAM_HIT + 0.03, 0.05)
    wr = wrench(t)
    add(p, "root", pos=(0, 0.6 * impact, -drive + 1.8 * impact))
    add(p, "body", rot=(-2 * cock + 2.5 * impact, 0.25 * yw + 3 * wr, roll))
    add(p, "neck", rot=(-4 * cock + 3 * impact, 0.6 * yw + 12 * wr, 3 * wr))
    add(p, "skull", rot=(-2 * cock - 4 * impact, 0.4 * yw + 7 * wr, 0.3 * roll - 6 * wr))
    jaw(p, 44 * g, 14 * g)
    add(p, "throat", scale=(1.0, 1.0 + 0.2 * g, 1.0))
    # the drive: hard beats inside a window (a beat and a half), the tail cocked to the other side before them
    beat = window(t, 0.36, 0.82, 0.08)
    for i, b in enumerate(TAILS):
        add(p, b, rot=(0, 1.3 * WAVE[i] * beat * math.sin(W(t - 0.36, 0.32) - 0.62 * i) + 2.4 * (i + 1) * cock, 0))
    trail(p, t, lambda u: -0.35 * f(R_YAW, u) - 6 * wrench(u) - 8 * bump(u, RAM_HIT + 0.03, 0.06), delay=0.06)
    flip(p, "f", (0, -40 * window(t, 0.3, 0.8, 0.16) + 12 * window(t, 0.86, 1.4, 0.2), 10 + 8 * window(t, 0.86, 1.4, 0.2)))
    flip(p, "h", (0, -36 * window(t, 0.3, 0.85, 0.16), 8))
    alive(p, t, k=0.5 * (1 - window(t, 0.35, 1.0, 0.15)))
    return p


def hurt(t):
    """the flinch: a jolt away from the blow, the tail whipping after it, gathering itself (no hold)"""
    p = {}
    e = math.exp(-t / 0.12) * smooth(t / 0.04)
    add(p, "body", rot=(0, 4 * e, -8 * e), pos=(0, 0, 2 * e))
    add(p, "neck", rot=(6 * e, -10 * e, 0)); add(p, "skull", rot=(4 * e, -5 * e, 4 * e))
    jaw(p, 12 * e)
    trail(p, t, lambda u: -7 * math.exp(-u / 0.15) * smooth(u / 0.05), gain=(0.4, 0.7, 1.1, 1.6, 2.2), delay=0.035)
    flip(p, "f", (0, 8 * e, 10 * e))
    alive(p, t, k=0.4, period=2.0)
    return p


def death(t):
    """the roll belly-up and the sinking, then life going: two last breaths that fade, the fluke twitching and still"""
    p = _O["death"](t)
    for c, a in ((1.4, 1.0), (2.2, 0.5)):
        g = bump(t, c, 0.22) * a
        add(p, "throat", scale=(1.0, 1.0 + 0.12 * g, 1.0)); add(p, "jaw", rot=(-4 * g, 0, 0))
    tw = sum(a * bump(t, c, 0.06) for c, a in ((1.1, 1.0), (1.6, -0.6), (2.3, 0.3)))
    for i, b in enumerate(TAILS):
        add(p, b, rot=(0, 1.5 * (i + 1) * tw, 0))
    return p


# ------------------------------------------------------------------ feeding, rest, tame
def eat(t):
    p = _O["eat"](t)
    alive(p, t, k=0.5, period=1.6)
    add(p, "skull", rot=(-2 * bump(t, 0.34, 0.05), 0, 0))
    return p


def sit(t):
    """hanging where it was told: a slow breath, the tail barely drifting, the head settling"""
    T = 6.0; p = _O["sit"](t)
    alive(p, t, k=0.8, period=T / 2)
    add(p, "neck", rot=(0.8 * wave(t, T, 0.3), 2.5 * wave(t, T, -1.0), 0))
    return p


def sleep(t):
    """asleep on the bottom: the deep slow breath in the throat, a dream twitch of the jaw and a flipper"""
    T = 8.0; p = _O["sleep"](t)
    br = wave(t, T / 2)
    add(p, "throat", scale=(1.0, 1.0 + 0.04 * br, 1.0))
    add(p, "neck", rot=(0.4 * wave(t, T / 2, -0.6), 0, 0))
    add(p, "jaw", rot=(-0.8 * max(0.0, br), 0, 0))
    tw = bump(t, 5.4, 0.07) + 0.6 * bump(t, 5.65, 0.07)
    add(p, "jaw", rot=(-3 * tw, 0, 0)); flip(p, "f", (0, 0, 3 * bump(t, 5.55, 0.08)))
    return p


def knocked_out(t):
    p = _O["knocked_out"](t)
    tw = bump(t, 2.9, 0.06)
    add(p, "fluke", rot=(0, 6 * tw, 0)); add(p, "tail4", rot=(0, 3 * bump(t, 2.84, 0.07), 0))
    return p


def wake(t):
    p = _O["wake"](t)
    trail(p, t, lambda u: 3.0 * window(u, 1.6, 2.4, 0.15) * math.sin(W(u, 0.35)), gain=(0.3, 0.6, 1.0, 1.4, 1.8), delay=0.07)
    alive(p, t, k=0.5 * smooth((t - 1.2) / 0.6), period=2.6)
    return p


def wake_sleep(t):
    p = _O["wake_sleep"](t)
    add(p, "jaw", rot=(-1.4 * tremor(t, (6.9, 10.2, 4.3)) * window(t, 0.9, 1.3, 0.1), 0, 0))
    alive(p, t, k=0.5 * smooth((t - 0.6) / 0.6), period=2.0)
    return p


def beg(t):
    p = _O["beg"](t)
    alive(p, t, k=0.5, period=1.2)
    trail(p, t, lambda u: 1.5 * math.sin(W(u, 1.2)), gain=(0.3, 0.6, 1.0, 1.4, 1.8), delay=0.08, loop=2.4)
    return p


def tame(t):
    p = _O["tame"](t)
    alive(p, t, k=0.5, period=3.0)
    return p


REBIND = {
    "idle": (idle, IDLE_T), "swim": (swim, 1.6), "walk": (walk, 2.4), "run": (run, 0.8), "stranded": (stranded, 1.6),
    "ambush": (ambush, 1.6), "breach": (breach, 2.4), "breathe": (breathe, 2.6), "swallow": (swallow, 2.4), "shake": (shake, 1.4),
    "spar": (spar, 2.6), "gape": (gape, 2.8), "spyhop": (spyhop, 4.0), "birth": (birth, 3.6), "attack": (attack, ATTACK_T),
    "hurt": (hurt, 0.5), "death": (death, 3.0), "eat": (eat, 1.6), "sit": (sit, 6.0), "sleep": (sleep, 8.0),
    "wake_sleep": (wake_sleep, 2.0), "knocked_out": (knocked_out, 4.4), "wake": (wake, 2.6), "beg": (beg, 2.4), "tame": (tame, 3.0),
}

NEW = {
    "ram_bite": (ram_bite, RAM_T, False, "Combate",
                 "investida e mordida de lado (Lindgren et al. 2013): arma a cauda, batidas fortes da meia-lua, rola de lado, bate "
                 "com a cabeça e fecha a boca de lado (golpe em 0,75 s), duas sacudidas, solta"),
    "turn_left": (turn_left, TURN_T, True, "Movimento", "girando parado na água para a esquerda: o corpo em C, a nadadeira de dentro freia"),
    "turn_right": (turn_right, TURN_T, True, "Movimento", "girando parado na água para a direita"),
}
