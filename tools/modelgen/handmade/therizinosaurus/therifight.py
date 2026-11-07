"""Therizinosaurus: the epic duel's three moves (06/11/2026). The duel AI (Java, generic) turns the body side-on in GUARD,
slides it 5 to 9 blocks in the LUNGE, makes it PARRY a blow that comes in and STAGGER when its own blow was parried.
Fixed lengths and beats: lunge 1.8 s with the hit at 0.50 s, parry 1.5 s with the counter at 0.60 s, stagger 1.6 s.

Its own way (docs/estudos/10: claws of up to ~50 cm for display and defence, Lautenschlager 2014, Qin et al. 2023; a
heavy-bellied, wide-hipped biped, Zanno 2010): it never puts the small head forward; it fights with the ARMS, the
head kept back behind them, and every blow rides on the swing of its heavy barrel.
  * LUNGE: it rocks back on its hips with both arms raised high and wide, the fans spread, the neck drawn back; then a
    long heavy step and both arms come down and across in front of it like shears, the blades crossing at 0.50 s; the
    arms carry on low across the body while the belly swings on after the hips; it steps back and raises the arms;
  * PARRY: the left forearm snaps up and across, the blades hooked out, catching the blow and turning it aside while
    the barrel twists away and the neck pulls the head behind the arm; on the untwist the right arm rises high and
    cuts down and across (0.60 s);
  * STAGGER: knocked over to its right, the arms flung wide searching for balance, the fans shaking, the barrel
    rolling over the planted foot; it catches itself with a wide step out to the side (the belly too heavy to cross
    the feet, as in its strafe) and drags the other foot after; the small head whips about at the end of the long
    neck, and it ends shaking out the feathers.
"""
import math

from anim2 import add, smooth, ease_in, ease_out, back_out
import theriflow as F

T = F.T
tr, window, neck, tail, arm, trail, upper, tremor, hold_legs = F.tr, F.window, F.neck, F.tail, F.arm, F.trail, F.upper, F.tremor, F.hold_legs
SX = F.SX
GUARD_FEET = {"l": 3.0, "r": -3.0}      # where theriflow.guard plants the feet (dz)
f_ = lambda track, t: float(track(t))
sq = lambda u: min(1.0, max(0.0, u)) ** 2

LUNGE_T = 1.8
PARRY_T = 1.5
STAGGER_T = 1.6


def guard_base(g):
    """the guard pose (its first frame) weighted by g; the feet are planted again by the move"""
    p = {}
    for b, e in F.guard(0.0).items():
        add(p, b, rot=tuple(g * v for v in e[0]), pos=tuple(g * v for v in e[1]))
    return p


def stepping(t, t0, t1):
    u = min(1.0, max(0.0, (t - t0) / (t1 - t0)))
    return smooth(u), math.sin(math.pi * u) ** 1.2


def plant(p, s, lift=0.0, dz=0.0, meta=0.0, toe=0.0):
    T.plant(p, s, lift, dz, meta, toe, clear=-0.05 if lift < 0.05 else 0.8 * min(1.0, lift / 4.0) ** 0.5)


def fan_shiver(p, t, k):
    """the quill fans on the forearms shiver (k = strength)"""
    for s in ("l", "r"):
        add(p, f"adult_{s}", rot=(0, 0, SX[s] * k * tremor(t, (10.3, 14.9, 6.7), (1.0, 0.55, 0.35), phase=1.0 if s == "l" else 2.0)))


# ------------------------------------------------------------------ lunge: the long step and the shears
LOAD = [(0, 0), (0.35, 1, ease_out), (0.4, 1.02), (0.5, 0, smooth), (1.8, 0)]
GO = [(0, 0), (0.32, 0), (0.5, 1, sq), (0.9, 1.06, ease_out), (1.35, 0.25, smooth), (1.8, 0, back_out)]
# the arms: raised (+) and cut (-), one curve so the swing never stops; at full speed through the clash (0.50 s)
ARMS = [(0, 0), (0.29, 1, ease_out), (0.33, 1.03), (0.55, -1.15, smooth), (0.9, -1.25, ease_out), (1.5, 0, smooth), (1.8, 0)]


def lunge(t):
    g = f_(tr((0, 1), (0.3, 0.6), (0.55, 0.3), (1.0, 0.4), (1.6, 1, smooth), (1.8, 1)), t)
    p = guard_base(g)
    ld, go, am = (f_(tr(*k), t) for k in (LOAD, GO, ARMS))
    up, dn = max(0.0, am), max(0.0, -am)
    belly = math.exp(-max(0.0, t - 0.55) / 0.3) * math.sin(2 * math.pi * (t - 0.55) / 0.7) * smooth((t - 0.48) / 0.1)
    clash = math.exp(-((t - 0.5) / 0.05) ** 2)
    # rocked back on the hips, then thrown forward over the long step; the barrel bounces on a beat late
    add(p, "body", rot=(6 * ld - 16 * go + 2 * belly, 0, 0), pos=(0, -1.0 * ld - 2.4 * go - 0.8 * belly, 2.0 * ld - 5.0 * go))
    hold_legs(p, 0.0)
    # the head kept back out of reach: drawn back in the load, it stays back and up even as the trunk goes forward
    neck(p, 12 * ld + 10 * go, 0, 0)
    add(p, "skull", rot=(-5 * ld - 4 * go, 0, 0)); add(p, "jaw", rot=(-5 * ld - 6 * clash, 0, 0))
    # both arms raised high and wide, then down and across in front, crossing at 0.50 s, carried on low
    for s in ("l", "r"):
        arm(p, s, 60 * up - 46 * dn, -12 * up + 16 * dn, -10 * up + 12 * dn + 4 * clash, 30 * up - 44 * dn)
    fan_shiver(p, t, 3.0 * window(t, 0.15, 0.4, 0.1) + 4.0 * math.exp(-max(0.0, t - 0.5) / 0.25) * smooth((t - 0.45) / 0.05))
    tail(p, pitch=-5 * ld + 4 * go)
    trail(p, t, lambda u: 3.0 * math.sin(2 * math.pi * (u - 0.5) / 0.8) * window(u, 0.5, 1.15, 0.15), delay=0.08)
    upper(p, t, 0.3, LUNGE_T)
    # the back foot pushes (heel up); the front one takes the long step out, and both come back to the guard stance
    pr, lf = stepping(t, 0.25, 0.48)
    bk, lb = stepping(t, 1.05, 1.45)
    hb = 1 - smooth((t - 1.0) / 0.4)
    plant(p, "l", 0.0, GUARD_FEET["l"], 24 * go * hb, 6 * go * hb)
    plant(p, "r", 7.0 * lf + 4.5 * lb, GUARD_FEET["r"] - 9.0 * pr + 9.0 * bk, 8 * lf + 6 * lb, -14 * lf - 10 * lb)
    return p


# ------------------------------------------------------------------ parry: the left forearm turns it, the right cuts
BLOCK = [(0, 0), (0.1, 0.7, smooth), (0.2, 1, ease_out), (0.4, 0.75), (0.65, 0.0, smooth), (1.5, 0)]
# the right arm: wound up (+) and the cut (-) in one curve, at full speed through the hit (0.60 s)
RIGHT = [(0, 0), (0.2, 0), (0.45, 1, smooth), (0.49, 1.03), (0.71, -1.15, smooth), (0.95, -1.1), (1.3, 0, smooth), (1.5, 0)]


def parry(t):
    g = f_(tr((0, 1), (0.2, 0.6), (0.8, 0.5), (1.5, 1, smooth)), t)
    p = guard_base(g)
    bl, rt = f_(tr(*BLOCK), t), f_(tr(*RIGHT), t)
    wd, sl = max(0.0, rt), max(0.0, -rt) / 1.15
    hit = math.exp(-max(0.0, t - 0.15) / 0.18) * smooth((t - 0.1) / 0.05)      # the blow lands on the arm
    # twisted away behind the blocking arm, then wound the other way and swung into the cut
    add(p, "body", rot=(2 * bl - 4 * sl, 10 * bl + 3 * hit + 12 * wd - 16 * sl, -3 * bl - 2 * hit + 3 * sl),
        pos=(0, -0.6 * sl, 1.2 * bl + 1.2 * hit - 2.5 * sl))
    hold_legs(p, -3 * bl - 2 * hit + 3 * sl, 10 * bl + 12 * wd - 16 * sl)
    neck(p, 6 * bl + 4 * wd + 4 * sl, 18 * bl - 4 * wd - 6 * sl, 0)
    add(p, "skull", rot=(-4 * bl, 6 * bl, 0)); add(p, "jaw", rot=(-5 * hit - 4 * math.exp(-((t - 0.6) / 0.06) ** 2), 0, 0))
    # left: up and across, the blades turned out to hook the blow aside
    arm(p, "l", 30 * bl, -26 * bl, -14 * bl, -36 * bl - 6 * hit, twist=20 * bl)
    # right: raised high and back on the twist, then the cut down and across
    arm(p, "r", 70 * wd - 70 * sl, -18 * wd + 18 * sl, -10 * wd + 12 * sl, 28 * wd - 44 * sl, twist=-10 * sl)
    fan_shiver(p, t, 4.0 * hit + 3.0 * math.exp(-max(0.0, t - 0.6) / 0.2) * smooth((t - 0.56) / 0.05))
    trail(p, t, lambda u: -6 * f_(tr(*BLOCK), u) - 5 * f_(tr(*RIGHT), u), delay=0.07)
    upper(p, t, 0.3, PARRY_T)
    # the weight goes back onto the left foot with the twist, then forward onto the right with the cut
    plant(p, "l", 0.0, GUARD_FEET["l"], 14 * sl, 4 * sl)
    plant(p, "r", 0.0, GUARD_FEET["r"], 8 * bl, 0.0)
    return p


# ------------------------------------------------------------------ stagger: the barrel rolls, the arms search
JOLT = [(0, 0), (0.12, 1, ease_out), (0.5, 0.85), (1.0, 0.2, smooth), (1.3, 0, smooth), (1.6, 0)]
TOSS = [(0, 0), (0.1, 1, ease_out), (0.35, 0.5), (0.8, 0.2, smooth), (1.6, 0, smooth)]


def roll_on(t):
    """the heavy barrel rolls on past the blow and back, twice, dying away"""
    return math.exp(-max(0.0, t - 0.2) / 0.45) * math.sin(2 * math.pi * 1.3 * (t - 0.2)) * smooth((t - 0.12) / 0.12) * (1 - smooth((t - 0.9) / 0.4))


def stagger(t):
    g = f_(tr((0, 1), (0.15, 0.4), (1.1, 0.5), (1.6, 1, smooth)), t)
    p = guard_base(g)
    e, hd = f_(tr(*JOLT), t), f_(tr(*TOSS), t)
    rl = roll_on(t)
    shake = window(t, 1.1, 1.45, 0.08)
    roll = 9 * e + 5 * rl
    add(p, "body", rot=(-4 * e, 10 * e, roll), pos=(-2.0 * e, -1.4 * e + 0.6 * rl, 1.6 * e))
    hold_legs(p, roll, 10 * e)
    # the small head whips on the long neck: thrown to its right, then lagging back
    whip = math.exp(-max(0.0, t - 0.3) / 0.35) * math.sin(2 * math.pi * 1.6 * (t - 0.3)) * smooth((t - 0.2) / 0.12)
    neck(p, 10 * hd - 6 * e, 24 * hd - 10 * whip, 6 * hd - 0.6 * roll + 5 * shake * math.sin(2 * math.pi * 6 * t))
    add(p, "skull", rot=(4 * hd, 8 * hd - 6 * whip, -10 * hd + 8 * shake * math.sin(2 * math.pi * 6 * t + 0.8)))
    add(p, "jaw", rot=(-8 * hd, 0, 0))
    # the arms flung wide and up for balance, the high (left) side wider, the fans shaking
    for s in ("l", "r"):
        k = 1.0 if s == "l" else 0.75
        arm(p, s, 10 * e * k + 6 * rl * SX[s], 14 * e, 10 * e, (34 * e + 8 * rl * SX[s]) * k)
    fan_shiver(p, t, 5.0 * e + 6.0 * shake)
    tail(p, pitch=-3 * e)
    trail(p, t, lambda u: -8 * f_(tr(*JOLT), u) + 6 * roll_on(u), delay=0.09)
    upper(p, t, 0.3, STAGGER_T)
    # the right foot steps wide out to its right to catch the barrel; the left drags after it; then both come home
    c1, l1 = stepping(t, 0.1, 0.48)
    d1, _ = stepping(t, 0.45, 0.95)
    c2, l2 = stepping(t, 0.85, 1.2)
    d2, l3 = stepping(t, 1.2, 1.55)
    out = c1 * (1 - c2); drag = d1 * (1 - d2)
    add(p, "thigh_r", rot=(0, 0, SX["r"] * 12 * out))
    add(p, "thigh_l", rot=(0, 0, -SX["l"] * 6 * drag))
    plant(p, "r", 6.0 * l1 + 4.5 * l2, GUARD_FEET["r"] + 1.0 * out, 8 * l1 + 6 * l2, -14 * l1 - 10 * l2)
    plant(p, "l", 3.0 * l3, GUARD_FEET["l"] - 2.5 * drag, 4 * drag, 10 * drag * (1 - d2) - 8 * l3)
    return p
