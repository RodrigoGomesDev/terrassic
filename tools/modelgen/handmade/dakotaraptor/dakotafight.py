"""Dakotaraptor: the epic duel's three moves (06/11/2026). The duel AI (Java, generic) turns the body side-on in GUARD,
slides it 5 to 9 blocks in the LUNGE, makes it PARRY a blow that comes in and STAGGER when its own blow was parried.
Fixed lengths and beats: lunge 1.8 s with the hit at 0.50 s, parry 1.5 s with the counter at 0.60 s, stagger 1.6 s.

Its own way (docs/estudos/10 and its study page "1.9": a big dromaeosaurid, the sickle claws, raptor prey restraint
and the wings used for balance, Fowler et al. 2011; DePalma et al. 2015): it fights with its FEET and its WINGS.
  * LUNGE: a crouch with the neck drawn back in its S and the tail fan up, then a short leap, feet first: both legs
    swing forward with the toes pulled up so the sickles lead, the wings flung open to steer; the sickles strike at
    0.50 s, rake down and back as it lands crouched, a beat of the wings to catch itself, and it folds back to guard.
    (No root travel: the Java carries the body; the leap is height and the legs swinging under it);
  * PARRY: the wing flash (FLASH, the fan to the front) thrown open in the rival's face while it rears back and twists
    away; on the twist it rocks onto the left foot, cocks the right sickle and kicks it out at 0.60 s, a wing beat to
    keep its feet, then folds;
  * STAGGER: knocked over to its right, the wings fling open uneven and beat hard to keep it up (a bird that lost its
    footing), a foot crosses in front, the other drags, the tail fan swings as a rudder; it ends with a ruffle.
The wings open only as fast as the 1 px feather planes stay readable (no hand turning more than ~25 deg a frame).
"""
import math

from anim2 import add, smooth, ease_in, ease_out, back_out
import geo
import dakotaflow as F

T = F.T
tr, window, f_, neck, wings, trail = F.tr, F.window, F.f_, F.neck, F.wings, F.trail
FLASH, MANTLE, SUN = F.FLASH, F.MANTLE, F.SUN
SIDES = F.SIDES                          # (side, mirror sign)
GUARD_FEET = {"l": 3.0, "r": -4.0}       # where dakotaflow.guard plants the feet (dz)
GUARD_TOE = {"l": 0.0, "r": -8 - 6 * math.sin(1.2)}   # its right sickle half raised in the guard
GUARD_WING = 0.45                        # its guard holds the wings MANTLE x 0.45
sq = lambda u: min(1.0, max(0.0, u)) ** 2

LUNGE_T = 1.8
PARRY_T = 1.5
STAGGER_T = 1.6


def guard_base(g, wing=1.0):
    """the guard pose (its first frame) weighted by g; wing = how much of its mantled wings is kept"""
    p = {}
    for b, e in F.guard(0.0).items():
        k = g * (wing if b.startswith(("arm_", "forearm_", "hand_")) else 1.0)
        add(p, b, rot=tuple(k * v for v in e[0]), pos=tuple(k * v for v in e[1]))
    return p


def stepping(t, t0, t1):
    u = min(1.0, max(0.0, (t - t0) / (t1 - t0)))
    return smooth(u), math.sin(math.pi * u) ** 1.2


def plant(p, s, lift=0.0, dz=0.0, meta=0.0, toe=0.0):
    T.plant(p, s, lift, dz, meta, toe, clear=-0.05 if lift < 0.05 else 0.8 * min(1.0, lift / 4.0) ** 0.5)


# ------------------------------------------------------------------ lunge: the short leap, sickles first
CROUCH = [(0, 0), (0.28, 1, ease_out), (0.33, 0.95), (0.47, 0, smooth), (0.66, 0), (0.8, 0.85, ease_out), (1.0, 0.55), (1.55, 0, smooth), (1.8, 0)]
AIR = [(0, 0), (0.27, 0), (0.5, 1, smooth), (0.6, 0.95), (0.8, 0, ease_in), (1.8, 0)]
LEGS = [(0, 0), (0.26, 0), (0.5, 1, lambda u: min(1.0, max(0.0, u)) ** 1.5), (0.58, 0.85), (0.8, 0.0, smooth), (1.8, 0)]        # the swing of both legs forward
OPEN = [(0, 0), (0.12, 0), (0.46, 0.8, smooth), (0.85, 0.75), (1.4, 0, smooth), (1.8, 0)]


def lunge(t):
    op = f_(tr(*OPEN), t)
    g = f_(tr((0, 1), (0.3, 0.75), (0.5, 0.35), (1.0, 0.45), (1.6, 1, smooth), (1.8, 1)), t)
    p = guard_base(g, 1 - op / 0.8)
    cr, air, lg = (f_(tr(*k), t) for k in (CROUCH, AIR, LEGS))
    K = T.K
    beat = math.exp(-((t - 0.62) / 0.07) ** 2) - 0.6 * math.exp(-((t - 0.8) / 0.07) ** 2)
    # crouch, the leap (the chest goes up, the feet come forward), the landing crouch
    add(p, "body", rot=(-5 * cr + 16 * air, 0, 0), pos=(0, K * (-3.2 * cr + 9.0 * air), K * (1.5 * cr - 2.0 * air)))
    # the neck cocked back in its S, then thrown forward with the jaws open for the follow-up bite
    neck(p, 12 * cr - 14 * air, 0, 0)
    add(p, "skull", rot=(-6 * cr + 4 * air, 0, 0))
    add(p, "jaw", rot=(f_(tr((0, 0), (0.25, -6), (0.45, -26, ease_out), (0.7, -22), (0.85, -4, ease_in), (1.8, 0)), t), 0, 0))
    wings(p, op, 0.35 * beat, how=FLASH)
    # the tail fan up as it crouches (a counterweight for the leap), then it swings down to balance the landing
    trail(p, t, lambda u: -6 * f_(tr(*CROUCH), u) + 7 * f_(tr(*AIR), u), delay=0.05, axis=0)
    trail(p, t, lambda u: 2.5 * math.sin(2 * math.pi * (u - 0.5) / 0.6) * window(u, 0.5, 1.3, 0.15), delay=0.07)
    F.alive_upper(p, t, k=0.3, period=LUNGE_T)
    # the feet: pushing off (heels up), swung forward toes up with the sickles leading (0.5 s), raked down and back to
    # the landing, and stepped back to the guard stance
    push = window(t, 0.12, 0.36, 0.1)
    rl, ll = stepping(t, 0.95, 1.25)
    rr, lr = stepping(t, 1.28, 1.58)
    for s, ahead in (("l", 12.0), ("r", 10.0)):
        land = {"l": GUARD_FEET["l"] - 6.0, "r": GUARD_FEET["r"] - 2.0}[s]
        home, lift_home = (rl, ll) if s == "l" else (rr, lr)
        base = land + (GUARD_FEET[s] - land) * home
        if t <= 0.5:
            dz = GUARD_FEET[s] + (-ahead - GUARD_FEET[s]) * lg
        else:                                          # raked from the strike to the landing spot
            dz = -ahead * lg + base * (1 - lg)
        lift = 7.0 * air + 4.0 * lift_home
        toe = -38 * lg + 10 * push * (1 - lg) - 12 * lift_home + GUARD_TOE[s] * (1 - lg)
        meta = 22 * push * (1 - lg) - 10 * lg + 8 * lift_home
        plant(p, s, lift, dz, meta, toe)
    # in the air the legs leave the IK and swing out free, sickles first (the pounce's pose), then rake down and back;
    # the two are cross-faded over four frames so nothing pops
    w = f_(tr((0, 0), (0.26, 0), (0.48, 1, smooth), (0.6, 1), (0.76, 0, smooth), (1.8, 0)), t)
    if w > 0:
        rake = f_(tr((0, 0), (0.5, 0), (0.7, 1, smooth), (1.8, 1)), t)
        swing = f_(tr((0, 0), (0.26, 0), (0.5, 1, smooth), (1.8, 1)), t)
        for s, k in (("l", 1.0), ("r", 0.85)):
            free = {"thigh": (42 * swing - 30 * rake) * k, "shin": -14 * swing + 4 * rake, "foot": -34 * swing + 22 * rake,
                    "toes": -40 * swing + 22 * rake}
            for b, v in free.items():
                e = p[f"{b}_{s}"]; r = list(e[0]); r[0] = (1 - w) * r[0] + w * v
                p[f"{b}_{s}"] = (r, e[1]) + tuple(e[2:])
        # the push-off: while the free swing is fading in, the toes must not dig into the ground (the body rides up)
        lo = min(q[:, 1].min() for c, q in geo.cube_points(F.S, p) if c["bone"] != "saddle")
        if lo < -0.05:
            add(p, "root", pos=(0, -0.05 - lo, 0))
    return p


# ------------------------------------------------------------------ parry: the wing flash, then the sickle kick
FLASH_K = [(0, 0), (0.28, 0.72, smooth), (0.5, 0.7), (0.75, 0.45), (1.3, 0, smooth), (1.5, 0)]
REAR = [(0, 0), (0.14, 1, ease_out), (0.3, 0.8), (0.55, 0.2, smooth), (1.5, 0)]
COCK = [(0, 0), (0.22, 0), (0.45, 1, smooth), (0.5, 1.0), (0.6, 0, ease_in), (1.5, 0)]
KICK = [(0, 0), (0.46, 0), (0.6, 1, sq), (0.72, 0.8), (1.05, 0, smooth), (1.5, 0)]


def parry(t):
    fk = f_(tr(*FLASH_K), t)
    g = f_(tr((0, 1), (0.25, 0.55), (0.9, 0.5), (1.5, 1, smooth)), t)
    p = guard_base(g, 1 - fk / 0.72)
    rr, ck, kk = (f_(tr(*k), t) for k in (REAR, COCK, KICK))
    K = T.K
    beat = math.exp(-((t - 0.64) / 0.07) ** 2)
    hiss = F.tremor(t, (11.3, 15.9, 7.7)) * window(t, 0.1, 0.6, 0.1)
    # it rears back and twists away from the blow behind the wings, then leans back further to kick
    add(p, "body", rot=(8 * rr + 4 * ck + 6 * kk, -10 * rr + 4 * ck, 3 * rr - 4 * ck),
        pos=(K * 1.0 * ck, K * (0.8 * rr - 0.8 * ck), K * (2.0 * rr + 0.8 * ck - 1.2 * kk)))
    neck(p, 14 * rr + 4 * ck - 8 * kk, -10 * rr + 4 * ck, 0)
    add(p, "skull", rot=(-4 * rr + 0.6 * hiss, -4 * rr, 4 * rr))
    add(p, "jaw", rot=(-20 * rr - 8 * ck - 1.4 * hiss, 0, 0))
    wings(p, fk, 0.3 * beat, how=FLASH)
    trail(p, t, lambda u: -7 * f_(tr(*REAR), u) + 4 * f_(tr(*KICK), u), delay=0.05, axis=0)
    trail(p, t, lambda u: 4 * f_(tr(*REAR), u) - 3 * f_(tr(*COCK), u), delay=0.07)
    F.alive_upper(p, t, k=0.3, period=PARRY_T)
    # the left foot takes the weight; the right is drawn up under the body, sickle raised, and kicked out at 0.60 s
    plant(p, "l", 0.0, GUARD_FEET["l"], 8 * kk, 0.0)
    lift = 6.0 * ck + 7.0 * kk
    dz = GUARD_FEET["r"] + 3.0 * ck - 9.0 * kk
    plant(p, "r", lift, dz, 10 * ck - 18 * kk, GUARD_TOE["r"] * (1 - ck) - 34 * ck - 40 * kk)
    return p


# ------------------------------------------------------------------ stagger: knocked off its feet, the wings save it
JOLT = [(0, 0), (0.12, 1, ease_out), (0.5, 0.8), (1.0, 0.2, smooth), (1.3, 0, smooth), (1.6, 0)]
TOSS = [(0, 0), (0.08, 1, ease_out), (0.3, 0.5), (0.7, 0.25, smooth), (1.6, 0, smooth)]
SPREAD = [(0, 0), (0.3, 0.6, smooth), (0.75, 0.5), (1.3, 0, smooth), (1.6, 0)]


def flap(t):
    """hard beats that die away (about 3.5 a second)"""
    return math.sin(2 * math.pi * 3.5 * (t - 0.2)) * math.exp(-max(0.0, t - 0.2) / 0.5) * smooth((t - 0.15) / 0.12) * (1 - smooth((t - 0.85) / 0.4))


def stagger(t):
    sp = f_(tr(*SPREAD), t)
    g = f_(tr((0, 1), (0.15, 0.4), (1.1, 0.5), (1.6, 1, smooth)), t)
    p = guard_base(g, 1 - sp / 0.6)
    e, hd = f_(tr(*JOLT), t), f_(tr(*TOSS), t)
    fl = flap(t)
    ruff = math.sin(2 * math.pi * 7.0 * (t - 1.15)) * window(t, 1.15, 1.45, 0.07)
    K = T.K
    add(p, "body", rot=(-3 * e + 2 * fl, 12 * e, 10 * e - 3 * fl), pos=(K * -2.0 * e, K * (-1.6 * e + 0.6 * fl), K * 1.6 * e))
    neck(p, 12 * hd - 6 * e, 24 * hd, 8 * hd + 4 * ruff)
    add(p, "skull", rot=(4 * hd, 8 * hd + 3 * ruff, -12 * hd + 9 * ruff))
    add(p, "jaw", rot=(-20 * hd, 0, 0))
    # the wings thrown open, the left (high side) wider, beating hard
    for s, sx in SIDES:
        k = sp * (1.0 if s == "l" else 0.75)
        (ax, ay, az), fx, hx = FLASH
        add(p, f"arm_{s}", rot=(ax * k, ay * k * sx, (az * k + 22 * fl * sp / 0.6) * sx))
        add(p, f"forearm_{s}", rot=(fx * k, 0, 0)); add(p, f"hand_{s}", rot=(hx * k, 0, 0))
    # the tail fan swung wide as a rudder against the fall
    trail(p, t, lambda u: -12 * f_(tr(*JOLT), u) + 4 * flap(u), delay=0.07)
    trail(p, t, lambda u: -5 * f_(tr(*JOLT), u), delay=0.05, axis=0)
    F.alive_upper(p, t, k=0.3, period=STAGGER_T)
    # the left foot crosses in front to catch it, the right drags out; then each steps back under it
    c1, l1 = stepping(t, 0.08, 0.45)
    d1, _ = stepping(t, 0.4, 0.9)
    c2, l2 = stepping(t, 0.85, 1.2)
    d2, l3 = stepping(t, 1.2, 1.55)
    cross = c1 * (1 - c2); drag = d1 * (1 - d2)
    add(p, "thigh_l", rot=(0, 0, -10 * cross))
    add(p, "thigh_r", rot=(0, 0, -7 * drag))
    plant(p, "l", 5.5 * l1 + 4.5 * l2, GUARD_FEET["l"] - 5.5 * cross, 10 * l1 + 8 * l2, -18 * l1 - 14 * l2)
    plant(p, "r", 3.5 * l3, GUARD_FEET["r"] + 3.0 * drag, 4 * drag, 10 * drag * (1 - d2) - 10 * l3 + GUARD_TOE["r"] * (1 - drag))
    return p
