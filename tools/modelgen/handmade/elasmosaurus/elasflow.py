"""Elasmosaurus: the fluid set (06/11/2026), in the spirit of the T. rex pass (docs/estudos/08_ANIMACAO_RAXIORES.md) but
in its own style: a stiff trunk that FLIES, a seven-bone neck that bends little, four flippers and a short tail.

  * THE FLIPPERS ARE WINGS WITH SOFT TIPS: each of the three pieces of a flipper takes the stroke a little later and
    twists a little more (`stroke`, tip lag ~0.08 of the cycle), so the tip whips through at the end of every down- and
    upstroke instead of the whole flipper turning as one plank. The hind pair still runs behind the fore pair.
  * THE NECK TRAILS THE BODY: every bob or turn of the trunk runs out along the neck with a delay that grows from the
    base to the head (`neck_trail`); the skull steadies the gaze against it. Gestures that start at the head (looking,
    diving nose first) run the other way, from the tip to the base (`neck_lead`).
  * THE TAIL IS THE END OF THE WAVE: each tail segment later and wider (`trail`).
  * NOTHING STOPS: every one-shot carries the breathing layer (`alive`) and keeps sculling; loops use periods that divide
    their length, so their seams close (the old walk, sit and idle had a 6 s / 5 s / 10 s cycle in 3 / 8 / 8 s loops).
  * THREE BEATS: the neck strike coils the neck into a shallow S (the base to its left, the front back to centre and
    down), holds with a tension shiver, then straightens from the base to the tip in ~0.13 s, the jaws shutting at
    0.55 s, overshoots into the opposite curve and settles; the fish is shaken twice. The study: the long neck lets the
    small head reach the shoal while the body stays back (Zammit et al. 2008; Noè et al. 2017: more side and down than up).
  * ORGANIC TREMOR: sums of non-commensurate sines under envelopes (`tremor`), never a switched sine: the blow at the
    surface, the tension before the strike, the death thrash.

Signs on this rig (elasmoanims): body +x = nose up, z = roll; neck*/skull -x = down, y = to its left; jaw -x = open.
"""
import math

from anim2 import add, Track, smooth, ease_out, ease_in, back_out
import elasmoanims as A

NECKS, TAILS, SIDES = A.NECKS, A.TAILS, A.SIDES
tr, window, ground = A.tr, A.window, A.ground
TAU = 2 * math.pi

# the originals some of the new ones are built on
_WAKE, _WAKE_SLEEP, _TAME, _NUZZLE = A.wake, A.wake_sleep, A.tame, A.nuzzle


def wave(t, period, phase=0.0):
    return math.sin(TAU * t / period + phase)


def tremor(t, f=(7.3, 11.1, 4.7), amp=(1.0, 0.55, 0.35), phase=0.0):
    """an organic shiver: three sines at frequencies that never line up (-1.9 .. 1.9 at most)"""
    return sum(a * math.sin(TAU * fr * t + phase * (i + 1) + 1.3 * i) for i, (fr, a) in enumerate(zip(f, amp)))


def trail(p, t, fn, gain=(0.8, 1.4, 2.2), delay=0.07, axis=1, bones=TAILS, loop=None):
    """follow-through down a chain: segment k takes fn(t - (k+1)*delay) * gain[k] on `axis` (a loop wraps the delay)"""
    for k, b in enumerate(bones):
        u = t - delay * (k + 1)
        v = fn(u % loop if loop else max(0.0, u)) * gain[k]
        r = [0.0, 0.0, 0.0]; r[axis] = v
        add(p, b, rot=tuple(r))


NECK_GAIN = (0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2)


def neck_trail(p, t, fn, delay=0.04, axis=0, gain=NECK_GAIN, loop=None):
    """the neck follows the trunk: bone k (from the base) late by (k+1)*delay"""
    trail(p, t, fn, gain=gain, delay=delay, axis=axis, bones=NECKS, loop=loop)


def neck_lead(p, t, fn, delay=0.06, axis=1, gain=NECK_GAIN, loop=None):
    """a gesture led by the head: the front bone first, each one toward the base later"""
    trail(p, t, fn, gain=tuple(reversed(gain)), delay=delay, axis=axis, bones=tuple(reversed(NECKS)), loop=loop)


def stroke(p, t, T, amp, lag=0.3, sweep=8.0, glide=0.0, tip=0.08, feather=18.0, phase=0.0):
    """the flight stroke with soft tips: down and back with the flipper flat, up and forward feathered; each piece
    later (by `tip` of the cycle) and more twisted than the one before; the hind pair lags by `lag`"""
    g = glide
    for which, ph in (("fore", 0.0), ("hind", lag)):
        a0 = TAU * t / T - TAU * ph + phase
        for s, sx in SIDES:
            down = amp * math.sin(a0) * (1 - g) + 4 * g
            fe = -feather * math.cos(a0) * (1 - g)
            sw = sweep * math.sin(a0 + 1.2) * (1 - g) + 10 * g
            add(p, f"{which}_{s}", rot=(fe, sw * sx, -down * sx))
            for j, (gd, gf) in ((1, (0.30, 0.45)), (2, (0.40, 0.65))):
                aj = a0 - TAU * tip * j
                dj = amp * gd * math.sin(aj) * (1 - g) - 1.5 * g          # gliding, the tips curl up a touch
                fj = -feather * gf * math.cos(aj) * (1 - g)
                add(p, f"{which}{j}_{s}", rot=(fj, 0, -dj * sx))


def thrust(p, t, T, amp, lag=0.3, phase=0.0, surge=0.0):
    """the trunk answers the strokes: it rises on each downstroke (fore and hind), nose a little up as the fore pair
    bites the water, and surges a touch"""
    a = TAU * t / T + phase
    up = 0.6 * math.sin(a) + 0.4 * math.sin(a - TAU * lag)
    add(p, "body", rot=(0.5 * amp * math.sin(a + 0.8), 0, 0), pos=(0, amp * up, -surge * max(0.0, math.sin(a - 0.4))))
    return up


def alive(p, t, k=1.0, period=3.0, slow=None):
    """the breathing layer every one-shot carries: the chest swells, the neck lifts a hair late, the jaw parts on the
    out-breath, the tail drifts (`slow`: the drift period; loops pass one that divides them)"""
    slow = slow or period * 2.1
    br = wave(t, period)
    add(p, "body", rot=(0.5 * k * br, 0, 0), pos=(0, 0.35 * k * br, 0))
    for i, b in enumerate(NECKS):
        add(p, b, rot=(-0.12 * k * wave(t, period, -0.5 - 0.12 * i), 0.15 * k * wave(t, slow, -0.3 * i), 0))
    add(p, "skull", rot=(0.4 * k * wave(t, period, -1.4), 0, 0))
    add(p, "jaw", rot=(-0.8 * k * max(0.0, wave(t, period, -0.6)), 0, 0))
    for i, b in enumerate(TAILS):
        add(p, b, rot=(0.3 * k * (i + 1) * wave(t, period, -0.5 * i), 0.8 * k * (i + 1) * wave(t, slow, -0.7 * i), 0))
    return br


def steady(p, k=0.5):
    """the skull holds the gaze level against the neck's pitch"""
    pitch = sum(p.get(b, ([0, 0, 0],))[0][0] for b in NECKS)
    add(p, "skull", rot=(-k * pitch * 0.25, 0, 0))


# ------------------------------------------------------------------ loops in the water
IDLE_T = 8.0
LOOK = Track([(0, 0), (1.0, 0), (1.9, 16, ease_out), (3.0, 16), (3.4, 13), (4.4, -13, smooth), (5.6, -13),
              (6.3, -4, ease_out), (7.2, -4), (8.0, 0, smooth)])


def idle(t):
    """hovering: slow sculling, the trunk rising with the strokes and the breath, the head leading a slow look round
    that runs back down the neck, the tail in a lazy S"""
    p = {}
    T = IDLE_T
    stroke(p, t, T / 2, 9, lag=0.5, sweep=4, tip=0.1)
    thrust(p, t, T / 2, 0.4, lag=0.5)
    br = alive(p, t, k=1.0, period=T / 3, slow=T)
    neck_lead(p, t, lambda u: float(LOOK(u)) / 7, delay=0.09, axis=1, loop=T)
    for i, b in enumerate(NECKS):
        add(p, b, rot=(-0.6 + 0.35 * wave(t, T, 0.4 - 0.25 * i) + 0.2 * wave(t, T / 4, 1.0 - 0.3 * i), 0, 0))
    add(p, "skull", rot=(1.2 * wave(t, T / 4, 1.7), 0.2 * float(LOOK(t)), 0))
    add(p, "jaw", rot=(-0.6 - 1.0 * smooth(max(0.0, br)), 0, 0))
    trail(p, t, lambda u: 2.4 * wave(u, T / 2) + 1.2 * wave(u, T, 0.7), gain=(0.6, 1.1, 1.8), delay=0.35, loop=T)
    steady(p, 0.4)
    return p


SWIM_T = 1.6


def swim(t):
    """cruising flight: full strokes with whipping tips, the trunk rising on each downstroke, the neck straight ahead
    taking the bob late from base to head, the skull steady, the tail ending the wave"""
    p = {}
    T = SWIM_T
    stroke(p, t, T, 18, lag=0.3, sweep=8, tip=0.09)
    thrust(p, t, T, 0.8, lag=0.3, surge=0.4)
    for b in NECKS:
        add(p, b, rot=(-4 / 7, 0, 0))
    neck_trail(p, t, lambda u: -0.35 * wave(u, T, 0.8), delay=0.05, loop=T)
    neck_trail(p, t, lambda u: 0.25 * wave(u, T, 0.3), delay=0.05, axis=1, loop=T)
    steady(p, 0.6)
    trail(p, t, lambda u: 1.6 * wave(u, T), gain=(0.7, 1.2, 1.9), delay=0.12, loop=T)
    trail(p, t, lambda u: 1.2 * wave(u, T, 1.0), gain=(0.7, 1.1, 1.6), delay=0.1, axis=0, loop=T)
    alive(p, t, k=0.3, period=T, slow=T)
    return p


WALK_T = 3.0


def walk(t):
    """slow swim: a stroke, then a glide with the flippers held out and the tips curling; the neck drifts"""
    p = {}
    T = WALK_T
    ph = (t % T) / T
    g = smooth((ph - 0.45) / 0.15) * (1 - smooth((ph - 0.9) / 0.1))
    stroke(p, t, T, 14, lag=0.25, sweep=6, glide=g, tip=0.09)
    thrust(p, t, T, 0.5, lag=0.25, surge=0.3)
    for b in NECKS:
        add(p, b, rot=(-5 / 7, 0, 0))
    neck_trail(p, t, lambda u: 0.6 * wave(u, T), delay=0.08, axis=1, loop=T)
    neck_trail(p, t, lambda u: -0.3 * wave(u, T, 0.8), delay=0.06, loop=T)
    steady(p, 0.5)
    trail(p, t, lambda u: 1.8 * wave(u, T) + 0.8 * wave(u, T / 2, 0.5), gain=(0.6, 1.1, 1.8), delay=0.18, loop=T)
    alive(p, t, k=0.6, period=T / 2, slow=T)
    return p


RUN_T = 0.9


def run(t):
    """the burst: fast deep strokes, tips whipping hard, the neck stretched ahead taking the surge late, the tail beating"""
    p = {}
    T = RUN_T
    stroke(p, t, T, 22, lag=0.2, sweep=10, tip=0.1, feather=22)
    thrust(p, t, T, 1.0, lag=0.2, surge=0.8)
    for b in NECKS:
        add(p, b, rot=(-2 / 7, 0, 0))
    neck_trail(p, t, lambda u: -0.5 * wave(u, T, 0.8), delay=0.03, loop=T)
    steady(p, 0.7)
    for b in TAILS:
        add(p, b, rot=(-1.5, 0, 0))
    trail(p, t, lambda u: 2.2 * wave(u, T), gain=(0.7, 1.3, 2.0), delay=0.07, loop=T)
    add(p, "jaw", rot=(-1.5 - 1.0 * max(0.0, wave(t, T / 2)), 0, 0))
    return p


STRANDED_T = 2.4


def stranded(t):
    """on land: belly down, the flippers pushing in turn (the tips dragging behind the push), the chest heaving, the
    neck lifting from its base and dropping heavily, the mouth panting"""
    p = {}
    T = STRANDED_T
    for which, ph in (("fore", 0.0), ("hind", 0.5)):
        for s, sx in SIDES:
            a = TAU * t / T - TAU * ph
            add(p, f"{which}_{s}", rot=(0, -10 * math.cos(a) * sx, -(8 + 8 * math.sin(a)) * sx))
            for j in (1, 2):
                aj = a - TAU * 0.09 * j
                add(p, f"{which}{j}_{s}", rot=(2 * math.cos(aj), 0, -(2.4 + 2.8 * j * math.sin(aj)) * sx))
    lift = lambda u: 1.0 - math.cos(TAU * u / T)                        # 0 .. 2, smooth, one lift per push
    neck_trail(p, t, lambda u: -0.6 + 0.9 * lift(u), delay=0.06, loop=T)
    neck_trail(p, t, lambda u: 0.6 * wave(u, T, 0.9), delay=0.08, axis=1, loop=T)
    add(p, "skull", rot=(-1.5 * lift(t - 0.5), 0, 0))
    add(p, "body", rot=(0.8 * wave(t, T / 2), 0, 0.8 * wave(t, T)))
    add(p, "jaw", rot=(-4 - 4 * max(0.0, wave(t, T / 2, -0.6)), 0, 0))
    trail(p, t, lambda u: 3.5 * wave(u, T), gain=(0.7, 1.2, 1.8), delay=0.12, loop=T)
    return ground(p)


SIT_T = 8.0


def sit(t):
    """resting where it was told: hanging in the water, slow sculls (4 s, it divides the loop now), a long breath, the
    neck a little down drifting"""
    p = {}
    T = SIT_T
    stroke(p, t, T / 2, 4, lag=0.5, sweep=3, tip=0.1)
    thrust(p, t, T / 2, 0.25, lag=0.5)
    alive(p, t, k=0.9, period=T / 3, slow=T)
    for b in NECKS:
        add(p, b, rot=(-8 / 7, 0, 0))
    neck_lead(p, t, lambda u: 0.45 * wave(u, T), delay=0.12, loop=T)
    neck_trail(p, t, lambda u: 0.2 * wave(u, T / 2, 0.4), delay=0.1, axis=0, loop=T)
    trail(p, t, lambda u: 1.5 * wave(u, T / 2), gain=(0.6, 1.1, 1.7), delay=0.3, loop=T)
    return p


SLEEP_T = 9.0


def sleep(t):
    """asleep floating at the surface, the neck laid out along the water rising and falling with a slow breath that
    runs to the head; the flippers drift with the swell, the tips last"""
    p = {}
    T = SLEEP_T
    br = wave(t, T / 2)
    add(p, "body", rot=(0.7 * br, 0, 0.6 * wave(t, T, 0.5)), pos=(0, 0.4 * br, 0))
    for which, ph in (("fore", 0.0), ("hind", 0.4)):
        for s, sx in SIDES:
            a = TAU * t / T - TAU * ph
            add(p, f"{which}_{s}", rot=(1.5 * math.cos(a), 10 * sx, (4 - 1.5 * math.sin(a)) * sx))
            for j in (1, 2):
                add(p, f"{which}{j}_{s}", rot=(0, 0, -0.8 * j * math.sin(a - 0.6 * j) * sx))
    for b in NECKS:
        add(p, b, rot=(6 / 7, 10 / 7, 0))
    neck_trail(p, t, lambda u: -0.25 * wave(u, T / 2, 0.3), delay=0.15, loop=T)
    neck_lead(p, t, lambda u: 0.3 * wave(u, T), delay=0.2, loop=T)
    add(p, "skull", rot=(-4, 4, 0))
    add(p, "jaw", rot=(-0.8 * max(0.0, wave(t, T / 2, -0.8)), 0, 0))
    trail(p, t, lambda u: 1.2 * wave(u, T), gain=(0.6, 1.0, 1.5), delay=0.4, loop=T)
    return p


def _ko(p, k, t, period=4.4):
    """belly up: the flippers limp, swaying with the water, the tips late"""
    br = wave(t, period)
    add(p, "body", rot=(0, 0, 170 * k), pos=(0, 0.3 * br * k, 0))
    for which, ph in (("fore", 0.0), ("hind", 0.35)):
        for s, sx in SIDES:
            a = TAU * t / period - TAU * ph
            add(p, f"{which}_{s}", rot=(1.5 * k * math.cos(a), 6 * k * sx, (12 + 2 * math.sin(a)) * k * sx))
            for j in (1, 2):
                add(p, f"{which}{j}_{s}", rot=(0, 0, -1.2 * j * k * math.sin(a - 0.7 * j) * sx))
    for b in NECKS:
        add(p, b, rot=(6 * k / 7, 10 * k / 7, 0))
    jawv = -8 * k - 1.5 * k * max(0.0, br)
    add(p, "jaw", rot=(jawv, 0, 0))
    return br


KO_T = 4.4


def knocked_out(t):
    p = {}
    _ko(p, 1.0, t, KO_T)
    neck_trail(p, t, lambda u: 0.3 * wave(u, KO_T, 0.3), delay=0.12, loop=KO_T)
    neck_trail(p, t, lambda u: 0.25 * wave(u, KO_T / 2, 1.1), delay=0.12, axis=1, loop=KO_T)
    trail(p, t, lambda u: 1.0 * wave(u, KO_T), gain=(0.6, 1.0, 1.5), delay=0.3, loop=KO_T)
    tw = math.exp(-((t - 2.9) / 0.06) ** 2)                            # a twitch of a fore flipper tip
    add(p, "fore2_l", rot=(0, 0, -6 * tw))
    return p


BEG_T = 2.2


def beg(t):
    """asks for food: the head brought round to the owner (the old one turned on a 4.4 s cycle in a 2.2 s loop: the
    seam jumped), a nod that runs down the neck, the jaws parting, the tail wagging slow"""
    p = {}
    T = BEG_T
    stroke(p, t, T, 8, lag=0.5, tip=0.1)
    thrust(p, t, T, 0.4, lag=0.5)
    for b in NECKS:
        add(p, b, rot=(4 / 7, 9 / 7, 0))
    neck_lead(p, t, lambda u: 0.45 * wave(u, T / 2), delay=0.05, axis=0, loop=T)
    neck_lead(p, t, lambda u: 0.5 * wave(u, T), delay=0.07, axis=1, loop=T)
    add(p, "skull", rot=(2 * wave(t, T / 2, -0.6), 4, 3 * wave(t, T, 0.4)))
    add(p, "jaw", rot=(-3 - 5 * smooth(max(0.0, wave(t, T, -0.9))), 0, 0))
    trail(p, t, lambda u: 1.6 * wave(u, T / 2), gain=(0.6, 1.0, 1.6), delay=0.1, loop=T)
    alive(p, t, k=0.5, period=T, slow=T)
    return p


# ------------------------------------------------------------------ the neck strike: coil, strike, overshoot, settle
# Java triggers it on the hit (Plesiosaurid.doHurtTarget); the jaws shut at HIT on screen
STRIKE_T = 1.1
HIT = 0.55
COIL_YAW = (4.0, 5.0, 4.0, 1.0, -3.0, -5.0, -5.0)      # a shallow S: the base to its left, the front back to the line
COIL_PITCH = (1.0, 1.0, 0.0, -1.5, -2.5, -3.0, -2.0)   # and the front drawn down and back
STRIKE_LIFT = (0.0, 0.0, 0.5, 1.0, 1.5, 2.0, 2.0)      # the flick goes in and a little up


def _release(i):
    return 0.39 + 0.018 * i            # base first (0.39 s), the front last (0.50 s): straight at the hit


def coil(t, i):
    r = _release(i)
    return float(tr((0, 0), (0.36, 1, ease_out), (r, 1), (r + 0.075, -0.32, ease_in), (0.82, 0.08, smooth), (STRIKE_T, 0, smooth))(t))


def lift(t, i):
    r = _release(i)
    return float(tr((0, 0), (r, 0), (r + 0.08, 1, ease_out), (0.75, 0.6), (STRIKE_T, 0, back_out))(t))


def strike_shake(t):
    """the fish is shaken twice, the second smaller"""
    return sum(a * math.exp(-((t - c) / w) ** 2) for c, a, w in ((0.68, 1.0, 0.05), (0.8, -0.6, 0.05), (0.9, 0.25, 0.05)))


def neck_strike(t):
    p = {}
    # the body: drawn back on the coil, a power stroke that drives the lunge through the hit, then it coasts
    back = float(tr((0, 0), (0.36, 1, ease_out), (0.42, 1), (HIT, -1.4, ease_in), (0.7, -1.1), (STRIKE_T, 0, back_out))(t))
    add(p, "body", rot=(0.8 * max(0.0, back), 1.2 * max(0.0, back), 0), pos=(0, 0, 1.6 * back))
    amp = float(tr((0, 6), (0.3, 10), (HIT, 22, ease_out), (0.8, 10), (STRIKE_T, 6))(t))
    stroke(p, t, STRIKE_T, amp, lag=0.25, sweep=8, tip=0.09, phase=math.pi / 2 - TAU * 0.5 / STRIKE_T)
    # the neck: each bone coils, holds with a shiver of tension, releases base first, overshoots, settles
    tense = 0.35 * tremor(t, (8.3, 12.7, 5.9)) * window(t, 0.3, 0.45, 0.06)
    sh = strike_shake(t)
    for i, b in enumerate(NECKS):
        c = coil(t, i)
        add(p, b, rot=(COIL_PITCH[i] * c + STRIKE_LIFT[i] * lift(t, i) + 0.2 * tense,
                       COIL_YAW[i] * c + 0.1 * tense + (0.6 + 0.25 * i) * sh, 0))
    # the head: cocked up and aimed during the coil, pitched in with the flick, shaking the fish
    cock = float(tr((0, 0), (0.36, 1, ease_out), (0.5, 1), (HIT, -0.4, ease_in), (0.7, -0.2), (STRIKE_T, 0, back_out))(t))
    add(p, "skull", rot=(6 * cock, -3 * cock + 5 * sh, -6 * sh))
    j = float(tr((0, 0), (0.2, -2), (0.46, -34, ease_out), (0.5, -36), (HIT, -1, ease_in), (0.66, -4), (0.75, -1), (STRIKE_T, 0))(t))
    add(p, "jaw", rot=(j + 0.8 * tense, 0, 0))
    # the tail answers the body's twist and the lunge, late and growing
    trail(p, t, lambda u: -2.5 * max(0.0, float(tr((0, 0), (0.36, 1, ease_out), (0.42, 1), (HIT, -1.4, ease_in), (0.7, -1.1),
                                                     (STRIKE_T, 0, back_out))(u))), gain=(0.6, 1.1, 1.7), delay=0.06)
    trail(p, t, lambda u: -3 * strike_shake(u), gain=(0.4, 0.8, 1.3), delay=0.05)
    alive(p, t, k=0.4)
    return p


attack = neck_strike


# ------------------------------------------------------------------ the other one-shots, made fluid
EAT_T = 2.2


def eat(t):
    """takes a fish: a cocked head, a snap, a toss up to turn it head first, three gulps that run down the long neck"""
    p = {}
    stroke(p, t, EAT_T / 2, 6, lag=0.5, tip=0.1)
    o = float(tr((0, 0), (0.12, 0.3), (0.2, 1, ease_out), (0.3, 0, ease_in), (0.48, 0.25), (0.56, 0, ease_in), (EAT_T, 0))(t))
    upf = tr((0, 0), (0.35, 0), (0.48, -0.15), (0.75, 1, ease_out), (1.75, 1), (EAT_T, 0, back_out))
    up = float(upf(t))
    for b in NECKS:
        add(p, b, rot=(-6 / 7, 0, 0))
    neck_lead(p, t, lambda u: (6 / 7) * float(upf(u)), delay=0.05, axis=0)
    add(p, "skull", rot=(14 * up, 0, 0))
    add(p, "jaw", rot=(-20 * o, 0, 0))
    # the gulps: a bump that runs from the head down to the base
    for c in (0.95, 1.3, 1.62):
        for i, b in enumerate(NECKS):
            d = c + (6 - i) * 0.05
            add(p, b, rot=(1.6 * math.exp(-((t - d) / 0.06) ** 2), 0, 0))
        add(p, "jaw", rot=(-3 * math.exp(-((t - c + 0.04) / 0.05) ** 2), 0, 0))
    trail(p, t, lambda u: 1.5 * float(upf(u)), gain=(0.5, 0.8, 1.2), delay=0.1, axis=0)
    alive(p, t, k=0.6)
    return p


GASTRO_T = 3.0


def gastrolith(t):
    """swallows stones: the trunk tips, the neck goes down from its base to the bottom, two scoops (the head pushing
    into the sand, the jaw raking), then the head up first, the neck after it, and a gulp running down"""
    p = {}
    stroke(p, t, GASTRO_T / 2, 6, lag=0.5, tip=0.1)
    dnf = tr((0, 0), (0.85, 1, smooth), (2.35, 1), (GASTRO_T, 0, smooth))
    dn = float(dnf(t))
    add(p, "body", rot=(-8 * dn, 0, 0))
    neck_trail(p, t, lambda u: -4.3 * float(dnf(u)), delay=0.05, gain=(0.8, 0.85, 0.9, 1.0, 1.1, 1.15, 1.2))
    scoop = sum(window(t, c, c + 0.32, 0.1) for c in (1.0, 1.65))
    push = sum(math.exp(-((t - c) / 0.08) ** 2) for c in (1.08, 1.73))
    add(p, "skull", rot=(-10 * dn + 12 * scoop - 3 * push, 2 * wave(t, 0.65) * scoop, 0))
    add(p, "jaw", rot=(-14 * scoop - 4 * tremor(t, (9.1, 13.3, 6.4)) * scoop * 0.3, 0, 0))
    for i, b in enumerate(NECKS):
        d = 2.6 + (6 - i) * 0.05
        add(p, b, rot=(1.4 * math.exp(-((t - d) / 0.07) ** 2), 0, 0))
    add(p, "jaw", rot=(-6 * window(t, 2.45, 2.62, 0.06), 0, 0))
    trail(p, t, lambda u: 3 * float(dnf(u)), gain=(0.5, 0.8, 1.2), delay=0.12, axis=0)
    alive(p, t, k=0.5)
    return p


BREATHE_T = 2.8


def breathe(t):
    """up for air: the neck rises in a long slope from its base, only the top of the head breaks the surface, a blow
    (a shiver of the jaw and skull under an envelope), a breath in, and back down head last"""
    p = {}
    stroke(p, t, BREATHE_T / 2, 8, lag=0.5, sweep=4, tip=0.1)
    kf = tr((0, 0), (0.9, 1, ease_out), (2.0, 1), (BREATHE_T, 0, smooth))
    k = float(kf(t))
    add(p, "body", rot=(6 * k, 0, 0))
    neck_trail(p, t, lambda u: 2.0 * float(kf(u)), delay=0.05)
    add(p, "skull", rot=(-8 * k, 0, 0))
    blow = window(t, 1.05, 1.35, 0.08)
    inhale = window(t, 1.45, 1.8, 0.12)
    add(p, "skull", rot=(1.2 * tremor(t, (8.6, 12.9, 5.3), phase=0.7) * blow + 1.5 * inhale, 0, 0))
    add(p, "jaw", rot=(-3 * blow - 1.2 * tremor(t, (9.4, 13.7, 6.1), phase=1.9) * blow - 2 * inhale, 0, 0))
    trail(p, t, lambda u: -2 * float(kf(u)), gain=(0.5, 0.8, 1.2), delay=0.12, axis=0)
    alive(p, t, k=0.4, period=BREATHE_T)
    return p


DIVE_T = 2.2


def dive(t):
    """nose first: the head goes down first and the neck after it, the trunk tips, two strong strokes (soft tips), the
    tail last"""
    p = {}
    kf = tr((0, 0), (0.6, 1, ease_out), (1.8, 1), (DIVE_T, 0, smooth))
    k = float(kf(t))
    neck_lead(p, t, lambda u: -0.9 * float(kf(u)), delay=0.04, axis=0)
    add(p, "skull", rot=(-4 * float(kf(t + 0.1)), 0, 0))
    bk = float(kf(max(0.0, t - 0.15)))
    add(p, "body", rot=(-24 * bk, 0, 0))
    amp = float(tr((0, 8), (0.3, 30, ease_out), (1.6, 30), (DIVE_T, 10))(t))
    stroke(p, t, 1.1, amp, lag=0.25, sweep=12, tip=0.1)
    trail(p, t, lambda u: 4.5 * float(kf(max(0.0, u - 0.15))), gain=(0.5, 0.8, 1.2), delay=0.1, axis=0)
    trail(p, t, lambda u: 1.6 * wave(u, 1.1), gain=(0.6, 1.1, 1.7), delay=0.1)
    alive(p, t, k=0.3)
    return p


HURT_T = 0.55


def hurt(t):
    """the flinch: the trunk jolts and rolls away, the jolt runs out along the neck to the head and down the tail,
    the flippers clap in, and it gathers itself (no hold)"""
    p = {}
    e = lambda u: math.exp(-(max(0.0, u) / 0.13)) * smooth(u / 0.035)
    k = e(t)
    add(p, "body", rot=(4 * k, 0, 8 * k), pos=(0, 0, 1.2 * k))
    neck_trail(p, t, lambda u: 1.0 * e(u), delay=0.025)
    neck_trail(p, t, lambda u: -1.0 * e(u), delay=0.025, axis=1)
    add(p, "skull", rot=(4 * e(t - 0.15), 3 * e(t - 0.15), 0))
    add(p, "jaw", rot=(-14 * e(t - 0.03), 0, 0))
    for which in ("fore", "hind"):
        for s, sx in SIDES:
            add(p, f"{which}_{s}", rot=(0, 6 * k * sx, -8 * k * sx))
            add(p, f"{which}2_{s}", rot=(0, 0, -4 * e(t - 0.06) * sx))
    trail(p, t, lambda u: -5 * e(u), gain=(0.6, 1.0, 1.6), delay=0.035)
    alive(p, t, k=0.4)
    return p


DEATH_T = 3.0


def death(t):
    """a last thrash (an organic shiver that fades), it rolls belly up, two last breaths, and sinks, the neck sagging
    from its base to the head and the flippers going loose"""
    p = {}
    kf = tr((0, 0), (0.6, 0), (1.7, 1, smooth), (DEATH_T, 1))
    k = float(kf(t))
    _ko(p, k, t)
    thr = tremor(t, (2.9, 4.3, 1.7), (1.0, 0.6, 0.4)) * window(t, 0.0, 0.85, 0.2)
    add(p, "body", rot=(-6 * k, 1.5 * thr, 2 * thr), pos=(0, -8 * smooth((t - 1.4) / 1.6), 0))
    neck_trail(p, t, lambda u: -2.0 * float(kf(u)), delay=0.08)
    neck_trail(p, t, lambda u: 1.4 * tremor(u, (2.9, 4.3, 1.7), (1.0, 0.6, 0.4)) * window(u, 0.0, 0.85, 0.2), delay=0.04, axis=1)
    trail(p, t, lambda u: 4 * tremor(u, (2.9, 4.3, 1.7)) * window(u, 0.0, 0.85, 0.2), gain=(0.6, 1.0, 1.6), delay=0.06)
    stroke(p, t, 0.6, 20 * (1 - k) * (1 - smooth((t - 0.6) / 0.6)), tip=0.1)
    fade = 1 - smooth((t - 1.8) / 1.0)
    for c, a in ((1.9, 1.0), (2.45, 0.5)):
        g = math.exp(-((t - c) / 0.2) ** 2) * a
        add(p, "body", rot=(1.2 * g, 0, 0)); add(p, "jaw", rot=(-3 * g, 0, 0))
    tw = sum(a * math.exp(-((t - c) / 0.06) ** 2) for c, a in ((1.7, 1.0), (2.15, -0.6), (2.6, 0.3)))
    add(p, "fore2_l", rot=(0, 0, -5 * tw * (0.4 + 0.6 * fade)))
    add(p, "tail3", rot=(0, 4 * tw, 0))
    return p


def wake(t):
    p = _WAKE(t)
    neck_trail(p, t, lambda u: 1.5 * window(u, 1.4, 2.0, 0.1) * math.sin(TAU * u / 0.3), delay=0.04, axis=1)
    trail(p, t, lambda u: 3 * math.exp(-((u - 1.5) / 0.3) ** 2) * math.sin(TAU * 2.5 * u), gain=(0.6, 1.0, 1.6), delay=0.08)
    alive(p, t, k=0.5)
    return p


def wake_sleep(t):
    p = _WAKE_SLEEP(t)
    trail(p, t, lambda u: 2.5 * math.exp(-((u - 1.2) / 0.3) ** 2) * math.sin(TAU * 2 * u), gain=(0.6, 1.0, 1.6), delay=0.08)
    alive(p, t, k=0.5)
    return p


def tame(t):
    p = _TAME(t)
    trail(p, t, lambda u: 2 * float(tr((0, 0), (0.8, 1, ease_out), (2.0, 1), (2.6, 0, smooth))(u)), gain=(0.5, 0.9, 1.4), delay=0.12)
    alive(p, t, k=0.7, period=2.6)
    return p


def nuzzle(t):
    p = _NUZZLE(t)
    trail(p, t, lambda u: 1.8 * float(tr((0, 0), (0.6, 1, ease_out), (1.8, 1), (2.4, 0, smooth))(u)), gain=(0.5, 0.9, 1.4), delay=0.12)
    alive(p, t, k=0.6)
    return p
