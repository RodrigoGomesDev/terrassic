"""Pachycephalosaurus: the three moves of the new duel (06/11/2026). The Java is generic (the same timings for every
species): guard, side steps, jab (the old `attack`), and these three, LUNGE (the committed blow: the Java slides the
body 5 to 9 blocks forward and locks its heading), PARRY (it turns the blow aside and counters) and STAGGER (it was
parried: the Java turns it aside and slows it ~2 s). Ideas from the study of the Raxiores fight (anticipation, a
blow that commits the whole body, a parry that rides the turn into the counter, a stunned victim); nothing copied.

What is its own (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md; page "Paquicefalossauro: estudo e modelo"):
  * the weapon is the dome, and it was used head-on and to the flank (healed lesions on the domes, Peterson et al.
    2013; the side blow, Carpenter 1997). The butting posture lines the head, the short neck and the back up into
    one straight ram (Galton 1970) and the tail is a stiff beam (ossified tendons, Brown & Schlaikjer 1943), so:
  * LUNGE is a short charge with the head down: it rocks back on its heels with the dome pulled up and the beam
    lifted, drops the whole spine into one straight line and drives off the back leg, the back foot pushes off on
    its toes and comes through as a catch step; the dome lands at 0.50 s and is stopped dead (it jars back up),
    the body keeps going over the front foot, the beam flicks; it backs off a step into the guard.
  * PARRY is the body getting out of the way, not a block: it sways and side-steps to its left, the dome swept
    away from the blow, the twist winds the neck further round, and the dome comes back across in a side blow
    into the rival's flank (the hit at 0.60 s), then it settles.
  * STAGGER is a clashed head: thrown to its right, the dome knocked aside, the left foot crossing under it and the
    right one dragging, the beam swinging out to balance, the dazed head lolling round, a hard shake of the dome
    at the end to clear it.

Fixed by the Java: LUNGE_T = 1.8 s (hit 0.50 s), PARRY_T = 1.5 s (counter 0.60 s), STAGGER_T = 1.6 s, no loops.
Every move starts and ends on the guard (pachyflow.guard at t = 0): the guard layer runs underneath at one guard
cycle per move, so its phase is the guard's own at both ends.
"""
import math

from anim2 import add, smooth, ease_in, ease_out, back_out, Track
import pachyanims as A
import pachyflow as F

SIDES, T, TAILS, STIFF = A.SIDES, A.T, A.TAILS, F.STIFF
neck, ram, arms, beam, alive_upper, tremor, wave, window = A.neck, A.ram, A.arms, F.beam, F.alive_upper, F.tremor, F.wave, F.window

LUNGE_T = 1.8
LUNGE_HIT = 0.50
PARRY_T = 1.5
PARRY_HIT = 0.60
STAGGER_T = 1.6
LEG_L = 39.0          # hip to ball, px: a thigh roll of asin(dx / LEG_L) moves the foot dx sideways (+z = out to +x)


def tr(*keys): return Track(keys)


def latz(dx):
    """thigh roll (deg) that carries the foot dx px along x (+ = the animal's left)"""
    return math.degrees(math.asin(max(-0.9, min(0.9, dx / LEG_L))))


def bump(t, c, w):
    return math.exp(-((t - c) / w) ** 2)


def decay(t, t0, tau, rise=0.03):
    """a kick at t0 that dies away"""
    return math.exp(-max(0.0, t - t0) / tau) * smooth((t - t0 + rise) / rise)


# ------------------------------------------------------------------ the guard underneath (pachyflow.guard's terms)
def guard_layer(p, t, L, k=1.0):
    """pachyflow.guard's pose at guard phase t * GUARD_T / L (one cycle per move, so both ends are the guard's
    t = 0), its rocking scaled by k (an action takes the weight; the stance itself stays)"""
    Tg = F.GUARD_T
    u = t * Tg / L
    rock = wave(u, Tg)
    snort = math.exp(-((u - 1.3) / 0.06) ** 2) * k
    ram(p, 0.55 + 0.06 * k * wave(u, Tg, -0.6))
    add(p, "body", rot=(0.8 * k * rock, 1.0 * k * wave(u, Tg, 1.0), 0.8 * k * wave(u, Tg / 2, 0.4)),
        pos=(0, -2.0 + 0.4 * k * rock, -0.6 * k * rock))
    neck(p, -0.8 * k * rock + 2 * snort, 3.0 * k * wave(u, Tg, 1.4), 0)
    add(p, "skull", rot=(0.5 * k * wave(u, Tg / 2, -0.8) - 2 * snort, 0.8 * k * wave(u, Tg / 2, 0.3), 0))
    add(p, "jaw", rot=(-0.5 - 2 * snort, 0, 0))
    for i, (b, wt) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(wt * (-4 + 0.6 * k * wave(u, Tg, -0.5 * i)), wt * 2.0 * k * wave(u, Tg, -0.8 - 0.5 * min(i, 2)), 0))
    for s, o in SIDES:
        sx = 1 if s == "l" else -1
        add(p, f"arm_{s}", rot=(-8 + 2 * k * wave(u, Tg, -1 - 3 * o), 0, 0))
        add(p, f"thigh_{s}", rot=(0, 0, 3.0 * sx - 0.6 * k * wave(u, Tg, 0.4)))


GUARD_DZ = {"l": 2.0, "r": -3.0}      # the guard's staggered stance: the left foot back, the right forward


def foot(p, s, x=0.0, dy=0.0, dz=None, meta=0.0, toe=0.0, clear=-0.05, yaw=0.0, roll=0.0, bx=0.0):
    """plant foot s at lateral offset x (px from its guard place), height dy, depth dz (guard's if None); the thigh
    cancels the body's yaw, roll and sideways shift bx so a planted foot stays put"""
    add(p, f"thigh_{s}", rot=(0, -0.5 * yaw, -roll + latz(x - bx)))   # half: the ball sits ahead of the thigh axis (measured)
    T.plant(p, s, dy, GUARD_DZ[s] if dz is None else dz, meta, toe, clear)


def step(t, t0, t1, a, b, lift):
    """a step between t0 and t1 from a to b (any number) lifted `lift`: (value, height, swing fraction 0..1)"""
    if t <= t0: return a, 0.0, 0.0
    if t >= t1: return b, 0.0, 0.0
    sw = (t - t0) / (t1 - t0)
    return a + (b - a) * smooth(sw), lift * math.sin(math.pi * sw) ** 1.2, sw


def swing_foot(sw):
    """metatarsus, toe and clearance of a swinging foot at swing fraction sw (0 = planted)"""
    if sw <= 0.0: return 0.0, 0.0, -0.05
    s = math.sin(math.pi * sw)
    return 10 * s, -18 * s, 0.8 * s ** 0.5


# ------------------------------------------------------------------ LUNGE: the committed butt (1.8 s, the dome lands at 0.50 s)
L_COIL = tr((0, 0), (0.33, 1.0, ease_out), (0.37, 1.0), (0.47, 0.0, ease_in), (1.8, 0.0))
L_DRIVE = tr((0, 0), (0.33, 0.0), (0.50, 1.0, ease_in), (0.62, 0.82, ease_out), (0.9, 0.7, smooth), (1.8, 0.0, back_out))
L_RAM = tr((0, 0), (0.3, 0.0), (0.47, 1.0, smooth), (0.9, 0.85, smooth), (1.8, 0.0, smooth))     # the head lines up before contact
L_FOLLOW = tr((0, 0), (0.48, 0.0), (0.66, 1.0, ease_out), (0.9, 0.85), (1.6, 0.0, smooth), (1.8, 0.0))


def lunge(t):
    """0-0.35 s: it rocks back onto its heels, the dome pulled up and back, the beam lifted, the arms tucked; 0.35-0.5:
    the spine drops into one straight ram and it drives off the left (back) foot, the dome lands at 0.50 s and is
    stopped dead (the skull jars up, the beak snaps), 0.5-0.9: the body keeps going over the right foot, nose down, the
    left foot comes through as a catch step, the beam flicks down and up; 0.9-1.8: it backs the catch foot off and
    rocks back into the guard"""
    p = {}
    c = float(L_COIL(t)); d = float(L_DRIVE(t)); fo = float(L_FOLLOW(t)); rm = float(L_RAM(t))
    act = max(c, min(1.0, d), fo)
    guard_layer(p, t, LUNGE_T, k=1.0 - 0.8 * act)
    j = bump(t, LUNGE_HIT + 0.01, 0.035)
    rk = decay(t, LUNGE_HIT, 0.2, 0.03)                    # the head bounced back by the impact
    shud = tremor(t, (9.1, 14.3, 6.7)) * decay(t, LUNGE_HIT, 0.14)
    ram(p, -0.35 * c + 0.45 * rm)                             # 0.2 cocked up -> 1.0 the straight ram
    add(p, "body", rot=(3.5 * c - 5.0 * d - 2.5 * fo + 1.2 * j, 0, 0.4 * shud),
        pos=(0, -1.2 * c - 1.0 * d - 1.0 * fo, 3.5 * c - 5.5 * d - 0.6 * fo))
    neck(p, 9 * c - 4 * d + 9 * rk, 0, 0)
    add(p, "skull", rot=(5 * c + 5 * rk + 0.8 * shud, 0, 0.6 * shud))
    add(p, "jaw", rot=(-2 * c - 5 * j, 0, 0))
    beam(p, t, lambda u: -7 * float(L_COIL(u)) - 4 * min(1.0, float(L_DRIVE(u))) + 10 * bump(u, 0.56, 0.07)
         - 3 * bump(u, 0.74, 0.09), axis=0, delay=0.05)
    beam(p, t, lambda u: 2.5 * decay(u, LUNGE_HIT, 0.2) * math.sin(2 * math.pi * 3.0 * (u - LUNGE_HIT)), delay=0.06)
    arms(p, -10 * c - 6 * d, 8 * c)
    alive_upper(p, t, k=0.4)
    # the back (left) foot: it pushes off on its toes, comes through as a catch step, and is backed off again
    push = smooth((t - 0.24) / 0.16) * (1 - smooth((t - 0.46) / 0.2))
    z, ly, sw = step(t, 0.41, 0.7, GUARD_DZ["l"], -5.0, 5.0)
    if t >= 0.7:
        z, ly, sw = step(t, 1.12, 1.44, -5.0, GUARD_DZ["l"], 3.5)
    m, toe, clear = swing_foot(sw)
    foot(p, "l", dy=ly, dz=z, meta=m + 24 * push, toe=toe, clear=clear)
    # the front (right) foot takes the weight: planted, the heel rising a touch as the body goes over it
    foot(p, "r", meta=8 * fo * (1 - smooth((t - 1.0) / 0.4)))
    return p


# ------------------------------------------------------------------ PARRY: sway aside and the side blow (1.5 s, the dome hits at 0.60 s)
P_SWING = tr((0, 0), (0.18, -0.6, ease_out), (0.28, -0.66), (0.45, -1.0, smooth), (0.60, 1.0, ease_in), (0.7, 0.86, ease_out),
             (0.9, 0.72, smooth), (1.5, 0.0, back_out))
P_SWAY = tr((0, 0), (0.16, 1.0, ease_out), (0.32, 1.0), (0.58, -0.45, smooth), (0.85, -0.3), (1.5, 0.0, smooth))
P_LOW = tr((0, 0), (0.15, 0.6, ease_out), (0.5, 1.0, smooth), (0.85, 0.8), (1.5, 0.0, smooth))


def parry(t):
    """0-0.25 s: the body sways and side-steps to its left, the dome swept away to the left and the shoulders twisted
    out of the blow's line (the rival's head goes by on its right); 0.25-0.45: the twist winds the neck further round,
    the head down into the butting line; 0.60 s: the dome comes back across in a side blow into the rival's flank,
    the hips swinging behind it and the beam the other way; then it carries through and settles into the guard"""
    p = {}
    sw = float(P_SWING(t)); sy = float(P_SWAY(t)); lo = float(P_LOW(t))
    act = min(1.0, max(abs(sw), abs(sy), lo))
    guard_layer(p, t, PARRY_T, k=1.0 - 0.8 * act)
    j = bump(t, PARRY_HIT + 0.01, 0.035)
    shud = tremor(t, (8.7, 13.1, 5.9)) * decay(t, PARRY_HIT, 0.15)
    bx = 3.0 * sy
    yaw = 10 * sw
    roll = -3.5 * sy + 1.5 * max(0.0, sw)
    ram(p, 0.35 * lo)
    add(p, "body", rot=(-1.5 * lo + 1.0 * j, yaw, roll + 0.5 * shud), pos=(bx, -1.2 * lo, -1.0 * max(0.0, sw)))
    neck(p, -2 * lo + 4 * j, 30 * sw - 7 * j, 9 * sw)
    add(p, "skull", rot=(2 * j + 0.8 * shud, 8 * sw, 12 * sw))
    add(p, "jaw", rot=(-1.5 * lo - 4 * j, 0, 0))
    beam(p, t, lambda u: -12 * float(P_SWING(u)), delay=0.06)
    beam(p, t, lambda u: -3 * float(P_LOW(u)) + 5 * bump(u, 0.66, 0.08), axis=0, delay=0.05)
    arms(p, -6 * lo + 3 * j, 4 * lo)
    alive_upper(p, t, k=0.4)
    # the side-step: the left foot steps out as it sways, and back in once the blow is through
    x, ly, s1 = step(t, 0.02, 0.2, 0.0, 4.5, 4.0)
    if t >= 0.2:
        x, ly, s1 = step(t, 0.86, 1.16, 4.5, 0.0, 3.0)
    m, toe, clear = swing_foot(s1)
    foot(p, "l", x=x, dy=ly, meta=m, toe=toe, clear=clear, yaw=yaw, roll=roll, bx=bx)
    foot(p, "r", yaw=yaw, roll=roll, bx=bx, meta=6 * max(0.0, sw) * lo)
    return p


# ------------------------------------------------------------------ STAGGER: the clashed head (1.6 s)
S_THROW = tr((0, 0), (0.1, 1.0, ease_out), (0.3, 0.85), (0.75, 0.35, smooth), (1.15, 0.12, smooth), (1.6, 0.0, smooth))
S_DAZE = tr((0, 0), (0.15, 1.0, ease_out), (0.9, 0.8), (1.25, 0.15, smooth), (1.6, 0.0, smooth))


def stagger(t):
    """0-0.12 s: the dome knocked to its right, the body thrown after it and rolled; 0.12-0.55: the left foot crosses
    under it to catch the weight and the right one drags out sideways on its toes, the beam swings out to the left
    to balance and back; 0.55-1.1: dazed, the head lolls round in slow circles, the ram posture lost (the nose up),
    the feet stepped back into the stance one at a time; 1.1-1.45: a hard shake of the dome; back to the guard"""
    p = {}
    th = float(S_THROW(t)); dz_ = float(S_DAZE(t))
    guard_layer(p, t, STAGGER_T, k=1.0 - 0.8 * max(th, dz_))
    kick = decay(t, 0.04, 0.12, 0.04)
    lol = dz_ * window(t, 0.35, 1.15, 0.2)
    ph = 2 * math.pi * 1.4 * (t - 0.35)
    shake = window(t, 1.12, 1.42, 0.07) * math.sin(2 * math.pi * 6.5 * (t - 1.12))
    bx = -3.2 * th
    yaw = 9 * th + 2 * kick
    roll = 4.5 * th + 2 * kick
    ram(p, -0.45 * dz_)                                        # the head comes up out of the butting line
    add(p, "body", rot=(1.5 * th - 2 * kick, yaw, roll), pos=(bx, -1.4 * th, 1.5 * th))
    neck(p, 6 * kick + 5 * lol * math.cos(ph), 26 * th + 9 * kick + 8 * lol * math.sin(ph) + 5 * shake, 8 * th)
    add(p, "skull", rot=(-4 * kick + 3 * lol * math.cos(ph + 0.6), 6 * th + 4 * shake,
                         16 * th + 7 * lol * math.sin(ph + 0.9) + 14 * shake))
    add(p, "jaw", rot=(-7 * kick - 3 * lol, 0, 0))
    beam(p, t, lambda u: -16 * float(S_THROW(u)) * (1.0 - 0.6 * smooth((u - 0.3) / 0.4))
         + 6 * decay(u, 0.35, 0.3) * math.sin(2 * math.pi * 1.6 * (u - 0.35)), delay=0.08)
    beam(p, t, lambda u: -5 * float(S_THROW(u)), axis=0, delay=0.06)
    arms(p, 10 * kick - 4 * th + 3 * lol * math.sin(ph - 1.0), 6 * kick)
    alive_upper(p, t, k=0.5)
    # the left foot crosses toward the right under the body, then steps back out into the stance
    lx, l1, s_l = step(t, 0.1, 0.42, 0.0, -9.0, 4.5)
    lz = GUARD_DZ["l"] - 5.0 * smooth((t - 0.1) / 0.32) * (1 - smooth((t - 0.95) / 0.3))
    if t >= 0.42:
        lx, l1, s_l = step(t, 0.95, 1.25, -9.0, 0.0, 4.0)
    m, toe, clear = swing_foot(s_l)
    foot(p, "l", x=lx, dy=l1, dz=lz, meta=m, toe=toe, clear=clear, yaw=yaw, roll=roll, bx=bx)
    # the right foot drags out on its toes (heel up, toes on the ground), then steps back under
    drag = smooth((t - 0.12) / 0.45)
    rx, r1, s_r = -4.0 * drag, 0.0, 0.0
    if t >= 0.6:
        rx, r1, s_r = step(t, 0.66, 0.95, -4.0, 0.0, 3.5)
    m, toe, clear = swing_foot(s_r)
    foot(p, "r", x=rx, dy=r1, dz=GUARD_DZ["r"] + 1.5 * drag * (1 - smooth((t - 0.66) / 0.29)),
         meta=m + 14 * drag * (1 - smooth((t - 0.6) / 0.1)), toe=toe, clear=clear, yaw=yaw, roll=roll, bx=bx)
    return p


NEW = {
    "lunge": (lunge, LUNGE_T, False, "Duelo", "bote: corrida curta de cabeça baixa, coluna reta como aríete; a cúpula bate em 0,50 s"),
    "parry": (parry, PARRY_T, False, "Duelo", "aparo: desvia o corpo para a esquerda e devolve a cabeçada de lado em 0,60 s"),
    "stagger": (stagger, STAGGER_T, False, "Duelo", "aparado: jogado para a direita, pés tropeçando, tonto, sacode a cúpula"),
}
