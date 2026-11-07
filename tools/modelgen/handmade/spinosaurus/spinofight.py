"""Spinosaurus: the epic duel's three moves (06/11/2026). The duel AI (Java, generic) turns the body side-on in GUARD,
slides it 5 to 9 blocks in the LUNGE, makes it PARRY a blow that comes in and STAGGER when its own blow was parried.
Fixed lengths and beats (the Java does not know the species): lunge 1.8 s with the hit at 0.50 s, parry 1.5 s with the
counter at 0.60 s, stagger 1.6 s.

Its own way (docs/estudos/10: a semi-aquatic snapper with a crocodile's snout, Ibrahim et al. 2020; hooked thumb claws,
Charig & Milner 1997; the sail, a broadside display):
  * LUNGE: not a T. rex's bite from above. The long snout is cocked out to one side with the jaws gaping, the sail
    rolled toward the rival, both thumb hooks raised; it drives off the back leg with a step of the front one and the
    snout sweeps across and SNAPS shut at 0.50 s like a crocodile taking a fish, the hooks raking in with it a beat
    later; the head thrashes twice to tear, the sail lurching after; then it settles back into its guard;
  * PARRY: the near thumb claw sweeps the blow out to the side while the snout is pulled back out of its way and the
    body twists from it; it rides the twist back and the snout snaps in from the side (0.60 s);
  * STAGGER: knocked over to its right, the head thrown, the far foot crossing in front to catch the weight and the
    other dragging out; the big sail on the hips swings it on, rocking twice before it settles, and it ends shaking
    the water from the snout.
The poses start and end on its guard (spinoflow.guard at t = 0) and breathe on a period that divides the length.
"""
import math

from anim2 import add, smooth, ease_in, ease_out, back_out
import spinoflow as F

T = F.T
tr, window, f_, neck, arms, trail = F.tr, F.window, F.f_, F.neck, F.arms, F.trail
PH, MS = F.PH, F.MS
GUARD_FEET = {"l": 3.0, "r": -3.5}          # where spinoflow.guard plants the feet (dz)
TAIL_PITCH = (0.6, 0.7, 0.8, 0.9, 1.0)
sq = lambda u: min(1.0, max(0.0, u)) ** 2      # accelerating into the hit, not as late as ease_in

LUNGE_T = 1.8
PARRY_T = 1.5
STAGGER_T = 1.6


def guard_base(g):
    """the guard pose (its first frame), weighted: g = 1 is the guard, lower lets the move take over the yaw and roll
    that keep it side-on; the legs are planted again by the move"""
    p = {}
    for b, e in F.guard(0.0).items():
        add(p, b, rot=tuple(g * v for v in e[0]), pos=tuple(g * v for v in e[1]))
    return p


def stepping(t, t0, t1):
    """a step between t0 and t1: (progress 0..1, lift 0..1)"""
    u = min(1.0, max(0.0, (t - t0) / (t1 - t0)))
    return smooth(u), math.sin(math.pi * u) ** 1.2


def plant(p, s, lift=0.0, dz=0.0, meta=0.0, toe=0.0):
    T.plant(p, s, lift, dz, meta, toe, clear=-0.05 if lift < 0.05 else 0.8 * min(1.0, lift / 4.0) ** 0.5)


# ------------------------------------------------------------------ lunge: the crocodile's side snap, hooks with it
LOAD = [(0, 0), (0.35, 1, ease_out), (0.42, 0.92), (0.5, 0, ease_in), (1.8, 0)]
GO = [(0, 0), (0.33, 0), (0.5, 1, sq), (0.9, 1.08, ease_out), (1.35, 0.25, smooth), (1.8, 0, back_out)]
SIDE = [(0, 0), (0.35, -1, ease_out), (0.5, 0.45, ease_in), (0.62, 0.55), (1.0, 0.0, smooth), (1.8, 0)]
NECK = [(0, 0), (0.33, 0), (0.5, 1, sq), (0.62, 0.72, smooth), (0.9, 0.78), (1.35, 0.2, smooth), (1.8, 0, back_out)]   # out at the snap, drawn back to tear
HOOK = [(0, 0), (0.38, 0), (0.6, 1, smooth), (0.9, 0.9), (1.45, 0, smooth), (1.8, 0)]
JAW_L = [(0, 0), (0.1, -5), (0.36, -42, ease_out), (0.46, -45), (0.5, -1, ease_in), (0.95, -3), (1.2, -9), (1.5, -3), (1.8, 0, smooth)]


def tear(t):
    return sum(a * math.exp(-((t - c) / 0.05) ** 2) for c, a in ((0.64, 1.0), (0.77, -0.8), (0.9, 0.45)))


def lunge(t):
    g = f_(tr((0, 1), (0.32, 0.6), (0.5, 0.3), (0.95, 0.35), (1.6, 1.0, smooth), (1.8, 1)), t)
    p = guard_base(g)
    ld, go, sd, hk = (f_(tr(*k), t) for k in (LOAD, GO, SIDE, HOOK))
    sh = tear(t)
    K = T.K
    # the sail: rolled toward the rival while it loads, then it lurches after the snap, late and wide
    sail = math.exp(-max(0.0, t - 0.55) / 0.4) * math.sin(2 * math.pi * (t - 0.55) / 0.85) * smooth((t - 0.5) / 0.1)
    add(p, "body", rot=(3 * ld - 11 * go, 5 * sd + 2 * sh, -5 * ld - 3 * go + 4 * sail),
        pos=(0, K * (-1.2 * ld - 2.2 * go), K * (2.5 * ld - 4.0 * go)))
    # the snout cocked out to its left and up, then thrown across and down, straight out at the rival
    nk = f_(tr(*NECK), t)
    neck(p, 13 * ld - 17 * nk, -16 * sd + 7 * sh, -3 * sd - 3 * sh)
    add(p, "skull", rot=(-6 * ld - 3 * go, -6 * sd + 6 * sh, 4 * sd - 10 * sh))
    add(p, "jaw", rot=(f_(tr(*JAW_L), t), 0, 0))
    # both thumb hooks raised high, then raking in and down toward the chest a beat after the jaws
    arms(p, -48 * ld + 32 * hk - 6 * go, 34 * ld - 42 * hk, 26 * ld - 40 * hk, 14 * ld - 6 * hk)
    # the tail: up as a counterweight, then it whips across after the snap
    trail(p, t, lambda u: -5 * f_(tr(*LOAD), u) + 3 * f_(tr(*GO), u), delay=0.07, axis=0, gain=TAIL_PITCH)
    trail(p, t, lambda u: -2.5 * f_(tr(*SIDE), u) - 3 * tear(u), delay=0.08)
    F.alive_upper(p, t, k=0.4, period=LUNGE_T)
    # the back leg drives (heel up, the leg straightening as the hips go over it); the front foot steps out to take it
    pr, lf = stepping(t, 0.27, 0.5)
    back, lb = stepping(t, 1.05, 1.45)
    plant(p, "l", 0.0, GUARD_FEET["l"], 26 * go * (1 - smooth((t - 1.0) / 0.4)), 8 * go * (1 - smooth((t - 1.0) / 0.4)))
    plant(p, "r", 6.5 * lf + 4.0 * lb, GUARD_FEET["r"] - 6.0 * pr + 6.0 * back, 8 * lf + 6 * lb, -14 * lf - 10 * lb)
    return p


# ------------------------------------------------------------------ parry: the thumb claw sweeps it out, the snout snaps back
DEFL = [(0, 0), (0.12, 0.65, smooth), (0.22, 1, ease_out), (0.38, 0.6), (0.62, 0.0, smooth), (1.5, 0)]
WIND = [(0, 0), (0.22, 0), (0.45, 1, smooth), (0.53, 1.04), (0.6, 0, ease_in), (1.5, 0)]
CNTR = [(0, 0), (0.48, 0), (0.6, 1, ease_in), (0.82, 0.85), (1.5, 0, back_out)]
JAW_P = [(0, 0), (0.1, -10, ease_out), (0.24, -5), (0.48, -40, ease_out), (0.55, -42), (0.6, -1, ease_in), (0.9, -4), (1.5, 0, smooth)]


def parry(t):
    g = f_(tr((0, 1), (0.2, 0.55), (0.75, 0.45), (1.5, 1, smooth)), t)
    p = guard_base(g)
    dv, wd, ct = (f_(tr(*k), t) for k in (DEFL, WIND, CNTR))
    K = T.K
    lag = math.exp(-max(0.0, t - 0.12) / 0.35) * math.sin(2 * math.pi * (t - 0.12) / 0.9) * smooth((t - 0.08) / 0.1)
    snap = math.exp(-((t - 0.6) / 0.05) ** 2)
    # the body twists from the blow (to its left), then unwinds to its right into the counter, the sail rocking after
    add(p, "body", rot=(-3 * dv + 2 * wd - 6 * ct, -9 * dv + 5 * wd + 4 * ct, 4 * dv - 2 * wd - 3 * ct + 3 * lag),
        pos=(0, K * (-0.8 * dv - 1.2 * ct), K * (1.6 * dv + 0.8 * wd - 2.6 * ct)))
    neck(p, 11 * dv + 5 * wd - 15 * ct, -13 * dv - 4 * wd + 13 * ct + 4 * snap, 3 * dv)
    add(p, "skull", rot=(5 * dv - 2 * wd - 4 * ct, -6 * dv - 3 * wd + 8 * ct, 6 * dv - 5 * ct))
    add(p, "jaw", rot=(f_(tr(*JAW_P), t), 0, 0))
    # the right thumb claw sweeps up and out to its right, the hook turned out; the left one stays cocked
    add(p, "arm_r", rot=(-64 * dv + 10 * ct, 0, -24 * dv))
    add(p, "forearm_r", rot=(32 * dv - 12 * ct, 0, 0)); add(p, "hand_r", rot=(-34 * dv + 10 * ct, 0, 0))
    add(p, "arm_l", rot=(-12 * dv - 9 * wd + 10 * ct, 0, 5 * wd)); add(p, "forearm_l", rot=(7 * wd - 10 * ct, 0, 0))
    add(p, "hand_l", rot=(9 * wd - 12 * ct, 0, 0))
    trail(p, t, lambda u: 3.5 * f_(tr(*DEFL), u) - 2 * f_(tr(*WIND), u) - 3.5 * f_(tr(*CNTR), u), delay=0.08)
    trail(p, t, lambda u: -2.5 * f_(tr(*DEFL), u), delay=0.07, axis=0, gain=TAIL_PITCH)
    F.alive_upper(p, t, k=0.4, period=PARRY_T)
    # the weight goes onto the back foot with the twist, then the front heel lifts as it leans into the snap
    plant(p, "l", 0.0, GUARD_FEET["l"], 6 * dv, 0.0)
    plant(p, "r", 0.0, GUARD_FEET["r"], 12 * ct, 4 * ct)
    return p


# ------------------------------------------------------------------ stagger: thrown over, the sail swings it on
JOLT = [(0, 0), (0.12, 1, ease_out), (0.45, 0.85), (1.0, 0.2, smooth), (1.3, 0, smooth), (1.6, 0)]
TOSS = [(0, 0), (0.08, 1, ease_out), (0.3, 0.55), (0.6, 0.35, smooth), (1.2, 0.1, smooth), (1.6, 0, smooth)]


def sail_rock(t):
    return math.exp(-max(0.0, t - 0.18) / 0.45) * math.sin(2 * math.pi * 1.35 * (t - 0.18)) * smooth((t - 0.12) / 0.12) * (1 - smooth((t - 0.9) / 0.4))


def stagger(t):
    g = f_(tr((0, 1), (0.15, 0.4), (1.1, 0.5), (1.6, 1, smooth)), t)
    p = guard_base(g)
    e, hd = f_(tr(*JOLT), t), f_(tr(*TOSS), t)
    wob = sail_rock(t)
    shake = math.sin(2 * math.pi * 5.0 * (t - 1.08)) * window(t, 1.08, 1.45, 0.08)
    K = T.K
    # knocked over to its right (+z raises the left side), turned, a lurch back; the sail carries it on and rocks
    add(p, "body", rot=(-3 * e, 10 * e, 8 * e + 5 * wob), pos=(K * -2.2 * e, K * -1.6 * e, K * 1.8 * e))
    # the head thrown to its right and up, the jaws flung open, then the wobble on the long neck
    neck(p, 10 * hd - 4 * e, 22 * hd + 6 * wob, 6 * hd)
    add(p, "skull", rot=(5 * hd, 8 * hd + 7 * shake, -12 * hd + 11 * shake))
    add(p, "jaw", rot=(-18 * hd - 4 * abs(shake), 0, 0))
    # the arms thrown out for balance, the hooks open
    arms(p, -22 * e, 12 * e, 18 * e, 16 * e + 4 * wob)
    trail(p, t, lambda u: -9 * f_(tr(*JOLT), u) + 7 * sail_rock(u), delay=0.09)
    trail(p, t, lambda u: -4 * f_(tr(*JOLT), u), delay=0.07, axis=0, gain=TAIL_PITCH)
    F.alive_upper(p, t, k=0.4, period=STAGGER_T)
    # the left foot crosses in front to catch the weight, the right drags out; then both walk back under it
    c1, l1 = stepping(t, 0.1, 0.5)
    d1, _ = stepping(t, 0.42, 0.95)
    c2, l2 = stepping(t, 0.85, 1.2)
    d2, l3 = stepping(t, 1.2, 1.55)
    cross = c1 * (1 - c2)
    drag = d1 * (1 - d2)
    add(p, "thigh_l", rot=(0, 0, -9 * cross))
    add(p, "thigh_r", rot=(0, 0, -6 * drag))
    plant(p, "l", 6.0 * l1 + 5.0 * l2, GUARD_FEET["l"] - 5.0 * cross, 10 * l1 + 8 * l2, -16 * l1 - 12 * l2)
    plant(p, "r", 3.0 * l3, GUARD_FEET["r"] + 2.5 * drag, 4 * drag, 10 * drag * (1 - d2) - 8 * l3)
    return p
