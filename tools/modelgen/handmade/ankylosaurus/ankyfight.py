"""Ankylosaurus: the three moves of the new duel (06/11/2026). The Java is generic (the same timings for every
species): guard, side steps, jab (the old `attack`), and these three, LUNGE (the committed blow: the Java slides the
body 5 to 9 blocks forward and locks its heading), PARRY (it turns the blow aside and counters) and STAGGER (it was
parried: the Java turns it aside and slows it ~2 s). Ideas from the study of the Raxiores fight (anticipation, a
blow that commits the whole body, a parry that rides the turn into the counter, a stunned victim); nothing copied.

What is its own (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md; page "Anquilossauro 1.5"; ankyflow.py):
  * it does not bite and never rears: its weapon is the knob at the end of a tail whose base is flexible and whose
    handle is stiffened by ossified tendons (Arbour 2009; Arbour & Snively 2009), and rivals clubbed each other on
    the flanks (Zuul's broken and healed flank spikes, Arbour et al. 2022). So every blow here comes out of the tail
    and the hips, and the clock of each move is the CLUB bone (adult_club), not the head;
  * LUNGE: the low body pivots on its planted forefeet. It winds the hips and the lifted tail to its right, then
    whips the hindquarters round to the left (the hind feet skip sideways after them) and the tail follows the hips
    in a huge arc that comes down to shin height: the knob reaches the end of its arc at 0.50 s. It rebounds off
    what it hit, the handle rings, and the body swings back square into the guard;
  * PARRY: it does not dodge, it takes the blow on the armour: it drops low and rolls its plated flank and back
    toward the blow (the head drawn in under the shoulder plates), the blow lands as a shove; the roll winds the
    hips and the tail the other way, and the club comes back round into the attacker at 0.60 s;
  * STAGGER: its own swing was turned aside, and the heavy tail keeps going: it drags the hips with it, the body
    lurches to the side and rolls, a hind foot steps out wide to catch the weight and a forefoot is dragged across;
    the tail swings back the other way (less), the hips follow it, and it shakes its head as it squares up.

Fixed by the Java: LUNGE_T = 1.8 s (knob at the end of its arc at 0.50 s), PARRY_T = 1.5 s (counter 0.60 s),
STAGGER_T = 1.6 s, no loops. Every move starts and ends on the guard (ankyflow.guard at t = 0): the guard layer runs
underneath at one guard cycle per move, so its phase is the guard's own at both ends.
"""
import math

from anim2 import add, world, smooth, ease_in, ease_out, back_out, Track
import ankyloanims as A
import ankyflow as FL

tr, head, jaw, trail, flanks, hold_legs, tremor, wave = A.tr, A.head, A.jaw, FL.trail, FL.flanks, FL.hold_legs, FL.tremor, FL.wave
plant_h, plant_f, settle, lift_head, lift_tail = A.plant_h, A.plant_f, A.settle, A.lift_head, A.lift_tail
SX, HANDLE, DROP, SIDES = FL.SX, FL.HANDLE, A.STAND_DROP, A.SIDES

LUNGE_T = 1.8
LUNGE_HIT = 0.50
PARRY_T = 1.5
PARRY_HIT = 0.60
STAGGER_T = 1.6
HIND_L = 25.7          # hip to foot, px: a thigh roll of asin(dx / HIND_L) carries the foot dx along x (+z = +x)
FORE_L = 19.5          # shoulder to hand
SHOULDER_Z = 50.0      # the forefeet are 50 px ahead of the body's pivot (the hips)
PIVOT = 1.0            # how much of the body's yaw is taken about the forefeet (1 = all of it: they stay put)
YAW_HOLD = 0.0         # the share of the body's yaw the limbs cancel (measured: any counter-yaw slid the feet more)


def bump(t, c, w):
    return math.exp(-((t - c) / w) ** 2)


def decay(t, t0, tau, rise=0.03):
    """a kick at t0 that dies away (zero before t0)"""
    return math.exp(-max(0.0, t - t0) / tau) * smooth((t - t0) / rise)


def lat(dx, L):
    return math.degrees(math.asin(max(-0.9, min(0.9, dx / L))))


def step(t, t0, t1, a, b, lift):
    """a step between t0 and t1 from a to b, lifted `lift`: (value, height, swing fraction; 0 when planted)"""
    if t <= t0: return a, 0.0, 0.0
    if t >= t1: return b, 0.0, 0.0
    sw = (t - t0) / (t1 - t0)
    return a + (b - a) * smooth(sw), lift * math.sin(math.pi * sw) ** 1.2, sw


# ------------------------------------------------------------------ the guard underneath (ankyflow.guard's terms)
def guard_layer(p, t, L, k=1.0):
    """ankyflow.guard's pose at guard phase t * GUARD_T / L (one cycle per move, so both ends are the guard's t = 0),
    its rocking scaled by k (an action takes the weight; the flank-on stance itself stays)"""
    T = FL.GUARD_T
    u = t * T / L
    rock = wave(u, T)
    add(p, "body", rot=(-2.2 + 0.4 * k * wave(u, T / 2), 8 + 1.0 * k * wave(u, T, 0.6), 1.6 * k * rock),
        pos=(-1.0, -DROP - 1.1 + 0.25 * k * wave(u, T / 2), 0))
    hold_legs(p, 1.6 * k * rock)
    for s in SIDES:
        add(p, f"arm_{s}", rot=(0, 0, 4 * SX[s])); add(p, f"thigh_{s}", rot=(0, 0, 2.5 * SX[s]))
    head(p, -9 + 0.8 * k * wave(u, T / 2, -0.8), -16 + 1.5 * k * wave(u, T, 1.2), -2)
    add(p, "skull", rot=(0.5 * k * tremor(u, (16 / T, 23 / T, 9 / T)), 0, 0))
    jaw(p, -1.0 - 1.2 * k * max(0.0, wave(u, T / 2, -1.0)))
    A.tail(p, pitch=-9, prof=A.BASE)
    trail(p, u, lambda v: -16 + 5 * k * wave(v, T, -0.4), gain=(1.0, 0.65, 0.3, 0.2, 0.15), delay=0.08, loop=T, club=0.1)
    flanks(p, u, 0.6 * k, T / 2, drop=False)


def pivot(p, yaw, roll=0.0, bx=0.0):
    """the body's action yaw taken about the forefeet (PIVOT of it): returns the hips' and the shoulders' sideways
    shift, so the feet can be held or stepped"""
    sx = PIVOT * SHOULDER_Z * math.sin(math.radians(yaw))
    add(p, "body", rot=(0, yaw, roll), pos=(sx + bx, 0, 0))
    hold_legs(p, roll)
    for s in SIDES:
        add(p, f"thigh_{s}", rot=(0, -YAW_HOLD * yaw, 0)); add(p, f"arm_{s}", rot=(0, -YAW_HOLD * yaw, 0))
    return sx + bx, sx + bx - SHOULDER_Z * math.sin(math.radians(yaw))


HAND_X = None                # the guard's hand x (set below, once the guard can be posed)


def feet(p, hips, shoulders, hind=None, fore=None):
    """plant the four feet: hind/fore = {side: (x, dy, dz, meta_or_pitch, swing)} offsets from the guard's places
    (x sideways in px); the limbs roll to put each foot at its x against the hips' / shoulders' shift"""
    hind = hind or {}; fore = fore or {}
    add(p, "body", pos=(0, -FL.SLACK, 0))
    for s in SIDES:
        x, dy, dz, m, sw = hind.get(s, (0.0, 0.0, 0.0, 0.0, 0.0))
        add(p, f"thigh_{s}", rot=(0, 0, lat(x - hips, HIND_L)))
        sn = math.sin(math.pi * sw) if sw else 0.0
        plant_h(p, s, dy, dz, m + 8 * sn, -14 * sn, 0.6 * sn ** 0.5 if sw else -0.05)
        x, dy, dz, m, sw = fore.get(s, (0.0, 0.0, 0.0, 0.0, 0.0))
        add(p, f"arm_{s}", rot=(0, 0, lat(x - shoulders, FORE_L)))
        sn = math.sin(math.pi * sw) if sw else 0.0
        for _ in range(3):           # the bent arm does not swing the hand by asin(dx / L): measure and correct
            plant_f(p, s, dy, -1.5 + dz, m - 10 * sn, 0.5 * sn ** 0.5 if sw else -0.05)
            err = HAND_X[s] + x - world(A.S, p, f"hand_{s}")[0]
            if abs(err) < 0.05: break
            add(p, f"arm_{s}", rot=(0, 0, lat(err, FORE_L)))
    return settle(lift_tail(lift_head(p, 0.3), 0.3))


# ------------------------------------------------------------------ LUNGE: the pivot and the great arc (1.8 s, the knob at 0.50 s)
L_YAW = tr((0, 0), (0.28, -4.0, ease_out), (0.32, -4.2), (0.49, 9.0, smooth), (0.62, 8.0, smooth), (0.95, 6.0, smooth),
           (1.8, 0.0, smooth))
L_SWING = tr((0, 0), (0.3, -0.8, ease_out), (0.34, -0.85), (0.45, 1.0, ease_in), (0.55, 0.74, ease_out), (0.68, 0.8, smooth),
             (0.95, 0.55, smooth), (1.5, -0.05, smooth), (1.8, 0.0, smooth))
L_LIFT = tr((0, 0), (0.33, 1.0, ease_out), (0.38, 1.0), (0.47, -0.25, ease_in), (0.6, -0.1, ease_out), (1.0, 0.0, smooth), (1.8, 0.0))
L_BRACE = tr((0, 0), (0.3, 1.0, ease_out), (1.0, 1.0), (1.6, 0.0, smooth), (1.8, 0.0))


def lunge(t):
    """0-0.35 s: the weight goes onto the forefeet, the hips wind to its right and the tail is lifted high and drawn
    round the same way (the knob up by the right flank), the head low and turned to the target; 0.35-0.5: the
    hindquarters whip round to the left on the planted forefeet, the hind feet skipping after them, the tail base
    first, the stiff handle late, the knob last, coming down in a great arc to shin height: the end of the arc at
    0.50 s; 0.5-0.9: it rebounds off the target and the handle rings, the body still swung round, blowing; 0.9-1.8:
    the hips come back square, the hind feet step back, the tail lowered into the guard's cock"""
    p = {}
    yaw = float(L_YAW(t)); br = float(L_BRACE(t)); lf = float(L_LIFT(t))
    guard_layer(p, t, LUNGE_T, k=1.0 - 0.8 * br)
    j = bump(t, LUNGE_HIT, 0.05)
    shud = tremor(t, (9.3, 13.7, 6.1)) * decay(t, LUNGE_HIT, 0.14, 0.04)
    hips, shoulders = pivot(p, yaw, roll=-3.0 * float(L_SWING(t)) + 0.5 * shud)
    add(p, "body", rot=(-2.5 * br + 0.8 * j, 0, 0), pos=(0, -0.8 * br, -1.0 * br))
    look = -yaw * 0.8 - 6 * br                                  # the eyes stay on the target while the body swings
    head(p, -6 * br - 2 * j, look, 2 * float(L_SWING(t)))
    jaw(p, -4 * FL.window(t, 0.48, 1.2, 0.1) * (0.6 + 0.4 * wave(t, 0.4)))
    trail(p, t, lambda u: 52 * float(L_SWING(u)), gain=A.BASE, delay=0.01, club=0.05)
    trail(p, t, lambda u: -14 * float(L_LIFT(u)), gain=A.BASE, delay=0.015, axis=0)
    trail(p, t, lambda u: 2.5 * tremor(u, (8.1, 12.3, 5.2)) * decay(u, LUNGE_HIT, 0.18, 0.03), gain=HANDLE, delay=0.02, club=0.2)
    flanks(p, t, 0.5, 1.2, drop=False)
    # the hind feet skip after the hips (the left first), and step back as the hips come home
    xl, yl, swl = step(t, 0.35, 0.53, 0.0, 7.0, 2.6)
    if t >= 0.53: xl, yl, swl = step(t, 1.05, 1.35, 7.0, 0.0, 2.2)
    xr, yr, swr = step(t, 0.41, 0.6, 0.0, 7.0, 2.6)
    if t >= 0.6: xr, yr, swr = step(t, 1.2, 1.5, 7.0, 0.0, 2.2)
    return feet(p, hips, shoulders,
                hind={"l": (xl, yl, 0.0, 0.0, swl), "r": (xr, yr, 0.0, 0.0, swr)},
                fore=None)


# ------------------------------------------------------------------ PARRY: the armour takes it, the club answers (1.5 s, the counter at 0.60 s)
P_HUNKER = tr((0, 0), (0.14, 1.0, ease_out), (0.35, 0.9), (0.6, 0.35, smooth), (1.5, 0.0, smooth))
P_YAW = tr((0, 0), (0.18, -1.5, ease_out), (0.42, -6.0, smooth), (0.56, 7.0, smooth), (0.75, 6.0), (1.5, 0.0, smooth))
P_SWING = tr((0, 0), (0.16, -0.25, ease_out), (0.42, -1.0, smooth), (0.545, 1.0, ease_in), (0.64, 0.74, ease_out), (0.78, 0.78),
             (1.5, 0.0, smooth))
P_HIT_IN = 0.16                                               # the rival's blow lands on the armour


def parry(t):
    """0-0.25 s: it drops low and rolls the plated flank and back toward the blow on its left, the head drawn in under
    the shoulder plates; the blow lands at 0.16 s as a shove to the right that the armour rides; 0.25-0.45: the roll
    winds the hips and the lifted tail round to the right; 0.60 s: the hips whip back and the club comes round into
    the attacker; then it carries through, the handle ringing, and settles into the guard"""
    p = {}
    hk = float(P_HUNKER(t)); yaw = float(P_YAW(t)); sw = float(P_SWING(t))
    guard_layer(p, t, PARRY_T, k=1.0 - 0.8 * max(hk, abs(sw)))
    shove = decay(t, P_HIT_IN, 0.18, 0.04)
    shud = tremor(t, (8.7, 13.1, 5.9)) * (decay(t, P_HIT_IN, 0.12, 0.03) + decay(t, PARRY_HIT, 0.12, 0.03))
    hips, shoulders = pivot(p, yaw, roll=-6.0 * hk - 2.0 * shove + 0.6 * shud, bx=-1.6 * shove)
    add(p, "body", rot=(-1.5 * hk, 0, 0), pos=(0, -1.4 * hk, 0))
    head(p, -10 * hk - 3 * shove, -yaw * 0.8 + 8 * hk, 4 * hk, k=0.7)
    jaw(p, -3 * shove - 3 * FL.window(t, 0.62, 1.2, 0.1))
    trail(p, t, lambda u: 48 * float(P_SWING(u)), gain=A.BASE, delay=0.01, club=0.05)
    trail(p, t, lambda u: -8 * max(0.0, -float(P_SWING(u))) + 2 * float(P_HUNKER(u)), gain=A.BASE, delay=0.015, axis=0)
    trail(p, t, lambda u: 6 * decay(u, P_HIT_IN, 0.2, 0.04), gain=HANDLE, delay=0.04)            # the shove jolts the tail
    trail(p, t, lambda u: 2.2 * tremor(u, (8.1, 12.3, 5.2)) * decay(u, PARRY_HIT, 0.18, 0.03), gain=HANDLE, delay=0.02, club=0.2)
    flanks(p, t, 0.5, 1.5, drop=False)
    return feet(p, hips, shoulders)


# ------------------------------------------------------------------ STAGGER: the tail keeps going (1.6 s)
def s_tail(u):
    """the heavy tail's swing once its blow is turned: out to the left, back past the middle, and dying away"""
    if u <= 0: return 0.0
    return 0.9 * math.exp(-u / 0.5) * math.sin(2 * math.pi * u / 0.95 + 0.3) * smooth(u / 0.12) * (1 - smooth((u - 1.0) / 0.45)) + 0.1 * smooth(u / 0.1) * (1 - smooth((u - 0.3) / 0.8))


S_LURCH = tr((0, 0), (0.14, 1.0, ease_out), (0.45, 0.8), (0.95, 0.25, smooth), (1.6, 0.0, smooth))


def stagger(t):
    """0-0.15 s: the turned blow throws it: the tail keeps going out to the left, the body lurches to its right and
    rolls; 0.15-0.5: the right hind foot steps out wide to catch the weight, the left forefoot is dragged in, the
    tail swings back across and the hips follow it late; 0.5-1.1: it rocks to a stop on the spread feet, the feet
    stepped back in; 1.1-1.45: a hard shake of the head, and it squares up into the guard"""
    p = {}
    lu = float(S_LURCH(t))
    guard_layer(p, t, STAGGER_T, k=1.0 - 0.8 * lu)
    kick = decay(t, 0.02, 0.14, 0.05)
    yaw = 9.0 * s_tail(t - 0.1)                                  # the hips dragged after the tail, late
    shake = FL.window(t, 1.1, 1.45, 0.07) * math.sin(2 * math.pi * 5.5 * (t - 1.1))
    hips, shoulders = pivot(p, yaw, roll=5.0 * lu + 2 * kick, bx=-2.6 * lu)
    add(p, "body", rot=(1.0 * kick - 1.0 * lu, 0, 0), pos=(0, -0.8 * lu, 0))
    head(p, -4 * lu + 3 * kick, 22 * lu * (1 - 0.5 * smooth((t - 0.3) / 0.6)) + 8 * kick - yaw + 8 * shake, 8 * lu + 7 * shake, k=0.6)
    jaw(p, -5 * kick - 2 * lu)
    trail(p, t, lambda u: 46 * s_tail(u), gain=A.BASE, delay=0.03, club=0.1)
    trail(p, t, lambda u: 4 * float(S_LURCH(u)), gain=A.BASE, delay=0.04, axis=0)               # the tail sags with the lurch
    flanks(p, t, 0.6, 0.8, drop=False)
    # the right hind foot steps out to catch it, then back; the left forefoot is dragged in, then stepped back out
    xr, yr, swr = step(t, 0.1, 0.36, 0.0, -6.0, 2.8)
    if t >= 0.36: xr, yr, swr = step(t, 0.85, 1.12, -6.0, 0.0, 2.2)
    drag = smooth((t - 0.14) / 0.4)
    xf, yf, swf = -3.5 * drag, 0.0, 0.0
    if t >= 0.75: xf, yf, swf = step(t, 1.0, 1.25, -3.5, 0.0, 2.2)
    return feet(p, hips, shoulders,
                hind={"r": (xr, yr, 0.0, 0.0, swr)},
                fore={"l": (xf, yf, 0.0, -6 * drag * (1 - smooth((t - 0.75) / 0.25)), swf)})


HAND_X = {s: float(world(A.S, FL.guard(0.0), f"hand_{s}")[0]) for s in SIDES}

NEW = {
    "lunge": (lunge, LUNGE_T, False, "Duelo", "bote: gira o quadril sobre as patas da frente e desce a clava num arco enorme (0,50 s)"),
    "parry": (parry, PARRY_T, False, "Duelo", "aparo: abaixa e vira a armadura do flanco para o golpe, responde com a clava (0,60 s)"),
    "stagger": (stagger, STAGGER_T, False, "Duelo", "aparado: a cauda pesada continua e puxa o quadril, cambaleia de lado"),
}
