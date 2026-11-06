"""Triceratops: the fluid set and the fighting set (06/11/2026), from its own body and its own study.

The study (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md): the lesions on the squamosal and the frill of many skulls
are where the brow horns of another Triceratops went in (Farke et al. 2009); real skulls fitted together lock horn
with horn (Farke 2004). So it fights FRONT ON, always: it turns its hind end round its forefeet to keep the horns on
the threat, braces, charges; against another Triceratops it locks horns, pushes and twists.

What its body makes of the principles of the T. rex study (docs/estudos/08_ANIMACAO_RAXIORES.md):
  * 9 m and 6-12 t on pillar legs: everything is SLOW and heavy. Its loops are long (the guard 3 s, the turn and the
    strafe 2 s), its steps short, its sway small but its drop after each footfall deep; the head, two metres of skull
    and horn on a short neck, is held still against the body (the neck takes the body's roll back) and nods late;
  * the weapon is the two brow horns: the fighting pose is the face tucked down until the horns point ahead and the
    frill stands up behind them like a shield (`horns`), the weight thrown onto the forelegs, which brace wide;
  * no bite, no growl: it SNORTS (a jolt of the head and a puff of the body, short envelopes), and it hooks UP;
  * it does not dodge: the strafe is a slow crab step that keeps the horns where they were, the block takes the blow
    on the frill (the head ducks INTO it), and it gives in by turning the frill edge-on and the face away.
Signs as in ceraflow.py.
"""
import math

import ceraflow as C
import triceranims as A
from anim2 import add, smooth, ease_in, ease_out, back_out

tr, f, wave, window, bump, ring, kick, tremor = C.tr, C.f, C.wave, C.window, C.bump, C.ring, C.kick, C.tremor
Q = C.Quad(A, A.horns, hind=(18, 12, 16), fore=(16, 28), head_k=0.55, scap=(0.25, 0.05))
SIDES = A.SIDES
Q.adopt()                                           # the originals plant their feet through the stable IK too
_O = {n: v[0] for n, v in A.ANIMS.items()}          # the originals, wrapped below


# ------------------------------------------------------------------ gaits with weight
def walk(t):
    """the heavy four-beat walk: the hips drop deep on the swinging side, the head held still and nodding late"""
    # the same cycle and stride as before (the game's walk speed), the stance a little shorter (0.62 of the cycle,
    # was 0.68) so the swing of these pillar legs gets 0.57 s instead of 0.48 and the knee folds without snapping
    Tc, stride, duty, lift = A.WALK[:4]
    return Q.gait(t, Tc, stride, 0.62, lift, A.LATERAL, bob=0.9, lean=0.0, hd=-1, roll=4.5, yaw=1.6, nod=0.7, head_keep=0.9,
                  head_lag=0.14, neck_roll=0.85, tail_yaw=2.6, tail_lag=0.09, tail_pitch=0.6)


def run(t):
    Tc, stride, duty, lift, bob, rock = A.RUNP
    return Q.gait(t, Tc, stride, duty, lift, A.GALLOP, flift=lift * 1.1, bob=bob, drop=1.0, lean=-1.0, hd=-3, roll=2.2,
                  yaw=1.2, rock=rock, nod=0.8, head_keep=0.8, head_lag=0.12, neck_roll=0.7, tail_yaw=2.2, tail_lag=0.08,
                  tail_pitch=2.0)


def charge(t):
    Tc, stride, duty, lift, bob, rock = A.CHARGEP
    duty = 0.33                                          # was 0.38: a longer swing, the legs fold without snapping
    return Q.gait(t, Tc, stride, duty, lift, A.GALLOP, flift=lift * 1.1, bob=bob, drop=1.0, lean=-2.5, hd=-2, roll=1.6,
                  yaw=0.8, rock=rock, nod=0.6, head_keep=0.9, head_lag=0.1, neck_roll=0.9, tail_yaw=1.4, tail_lag=0.07,
                  tail_pitch=1.6, tail_base=-3.0, weapon=0.9, jaw=-2.0)


WALK_TIRED_T = 1.9


def walk_tired(t):
    """spent: slower, shorter steps (32 px a cycle of 1.9 s), the horns hanging low, the beak open, heaving"""
    return Q.gait(t, WALK_TIRED_T, 32, 0.72, 4.0, A.LATERAL, bob=1.3, drop=0.6, lean=-1.5, hd=-12, roll=5.5, yaw=1.8,
                  nod=1.2, head_keep=0.6, head_lag=0.2, neck_roll=0.6, tail_yaw=2.0, tail_lag=0.1, tail_pitch=0.8,
                  tail_base=2.0, jaw=-6.0, pant=4.0)


# ------------------------------------------------------------------ standing: the idle, never still
IDLE_T = 8.0
LOOK = tr((0, (0, 0)), (1.6, (0, 0)), (2.5, (2, 15), ease_out), (3.6, (1, 13)), (4.4, (-1, -12), ease_out), (5.2, (-2, -11)),
          (6.1, (-7, 2), ease_out), (7.1, (-6, 0)), (8.0, (0, 0), ease_in))


def idle(t):
    """the slow breath of a big barrel (three in a loop), the weight drifting over the left hind foot while the right
    rests on its toe like a horse's, the head swinging to look and dipping to sniff, the tail in a lazy S; no two
    cycles peak together"""
    T = IDLE_T; p = {}
    br = Q.alive(p, t, k=1.3, period=T / 3)
    shift = wave(t, T, -0.9) + 0.25 * wave(t, T / 2, 0.7)
    rest = A.window(t, 1.0, 5.6, 0.9)
    lp, ly = LOOK(t)
    add(p, "body", rot=(0.0, 0.5 * shift + 0.06 * ly, 1.2 * shift - 1.8 * rest), pos=(0, -A.STAND_DROP - 0.4 * rest, 0))
    Q.head(p, lp + 0.6 * wave(t, T / 5, 0.4), ly + 1.0 * wave(t, T / 5, 1.3), -0.2 * ly + 0.8 * wave(t, T / 4, 0.2))
    flick = bump(t, 6.6, 0.07) - 0.6 * bump(t, 6.78, 0.07)        # the frill twitches, as an ear would
    add(p, "skull", rot=(0, 0, 3.0 * flick))
    A.jaw(p, -1.0 * window(t, 6.1, 7.0, 0.3) * max(0.0, math.sin(2 * math.pi * t / 0.4)))
    for i, b in enumerate(A.TAILS):
        add(p, b, rot=(0.3 * i * wave(t, T / 3, -0.5 * i), (0.8 + 1.1 * i) * wave(t, T, -0.9 * i) + 0.5 * i * wave(t, T / 2, 0.4 - 0.8 * i), 0))
    Q.counter_legs(p)
    A.lift_head(p)
    Q.foot(p, "l", "h")
    Q.foot(p, "r", "h", 1.4 * rest, -2.5 * rest, 0.0, meta=26 * rest, toe=-20 * rest, clear=-0.05 if rest < 0.05 else 0.0)
    for s in SIDES: Q.foot(p, s, "f")
    return p


IDLE_TIRED_T = 3.0


def idle_tired(t):
    """after a long fight: the barrel heaves four times a loop, the beak hangs open, the horns droop toward the
    ground, the forelegs splayed to hold the weight of the head"""
    T = IDLE_TIRED_T; p = {}
    pant = wave(t, T / 4)
    add(p, "body", rot=(-1.5 + 1.4 * pant, 0.6 * wave(t, T, 0.3), 0.8 * wave(t, T, -0.4)), pos=(0, -A.STAND_DROP - 1.0 + 0.7 * pant, 0))
    Q.head(p, -16 - 1.6 * wave(t, T / 4, -0.7), 2.0 * wave(t, T, 0.9), 0)
    add(p, "skull", rot=(-1.0 * wave(t, T / 4, -1.3), 0, 0))
    A.jaw(p, -7 - 4 * max(0.0, wave(t, T / 4, -0.5)))
    for i, b in enumerate(A.TAILS):
        add(p, b, rot=(2.0 + 0.4 * i * pant, (0.6 + 0.6 * i) * wave(t, T, -0.8 * i), 0))
    return Q.stance(p, fore=(-1.5, -1.5), fdx=(1.2, -1.2), clear=0.4)


# ------------------------------------------------------------------ the fight
GUARD_T = 3.0


def guard(t):
    """facing a rival: the face tucked so the brow horns point at it and the frill stands behind them, the weight on
    the forelegs (braced wide and forward), the horns weaving slowly to follow it; it breathes hard through the nose
    and snorts twice a loop, each snort a jolt of the head and a puff of the body"""
    T = GUARD_T; p = {}
    snort = sum(kick(t, c, 0.12, 0.04) for c in (0.9, 2.3))
    sn_late = sum(kick(t, c + 0.06, 0.16, 0.05) for c in (0.9, 2.3))
    br = wave(t, T / 2)
    weave = wave(t, T, 0.6)
    add(p, "body", rot=(-2.5 + 0.5 * br - 0.8 * snort, 0.8 * weave, 0.5 * wave(t, T / 2, 1.1)), pos=(0, -A.STAND_DROP - 1.4 - 0.4 * (1 + br), -1.6))
    A.horns(p, 1.0)
    Q.head(p, -3 + 4 * sn_late - 0.6 * wave(t, T / 2, -0.6), 3.5 * weave + 1.0 * wave(t, T / 3, 0.2), -1.5 * weave)
    A.jaw(p, -1.5 * snort)
    for i, b in enumerate(A.TAILS):
        add(p, b, rot=(-1.0 * (0.5 + 0.2 * i) + 0.2 * i * br, -(0.6 + 0.6 * i) * wave(t, T, 0.6 - 0.7 * (i + 1)), 0))
    return Q.stance(p, fore=(-2.5, -2.5), hind=(1.0, 1.0), fdx=(1.0, -1.0), clear=0.3)


STRAFE_T = 2.0


def _strafe_extra(p, t, w):
    A.horns(p, 0.15 * math.sin(2 * w - 1.0) ** 2)     # the horns dip on each heavy step and come up level again


def strafe_left(t): return Q.strafe(t, "left", STRAFE_T, step_dx=2.4, lift=3.2, lean=1.2, guard=0.9, look=4.0, tail_yaw=1.6, drop=1.4, extra=_strafe_extra)
def strafe_right(t): return Q.strafe(t, "right", STRAFE_T, step_dx=2.4, lift=3.2, lean=1.2, guard=0.9, look=4.0, tail_yaw=1.6, drop=1.4, extra=_strafe_extra)


TURN_T = 2.0


def turn_left(t): return Q.turn(t, "left", TURN_T, fore_dx=3.2, hind_dx=2.6, lift=3.4, lead_yaw=6.0, body_yaw=2.5, roll=1.2, bob=0.7, tail_yaw=2.0)
def turn_right(t): return Q.turn(t, "right", TURN_T, fore_dx=3.2, hind_dx=2.6, lift=3.4, lead_yaw=6.0, body_yaw=2.5, roll=1.2, bob=0.7, tail_yaw=2.0)


FEINT_T = 1.6
F_BACK = tr((0, 0), (0.35, 1, ease_out), (0.5, 0.8), (0.62, 0, ease_in), (1.6, 0))
F_GO = tr((0, 0), (0.42, 0), (0.72, 1, smooth), (0.85, 1.04), (1.0, 0.9), (1.6, 0, back_out))   # the body arrives; the head stops dead


def feint(t):
    """the false charge: it rocks back onto its hind legs with the nose up, throws its weight forward with the horns
    levelled and a forefoot stamped ahead, and stops dead; the head carries on and flicks up, then it settles back"""
    p = {}
    bk, go = f(F_BACK, t), f(F_GO, t)
    stop = ring(t, 0.8, 2.6, 0.22)
    Q.alive(p, t, k=0.6, period=1.6)
    add(p, "body", rot=(3.0 * bk - 3.0 * go, 0, 0), pos=(0, -A.STAND_DROP - 0.6 * bk - 1.8 * go, 2.2 * bk - 4.5 * go))
    A.horns(p, 0.4 + 0.6 * go)
    Q.head(p, 6 * bk - 3 * go + 7 * stop, 0, 0)
    A.jaw(p, -2.0 * bump(t, 0.85, 0.06))
    Q.trail(p, t, lambda u: 3.0 * f(F_GO, u) - 2.0 * f(F_BACK, u), delay=0.07, axis=0, gain=Q.gains(0.4, 0.3))
    step = min(1.0, max(0.0, (t - 0.5) / 0.3)); back = min(1.0, max(0.0, (t - 1.05) / 0.35))
    Q.counter_legs(p); A.lift_head(p)
    for s in SIDES: Q.foot(p, s, "h", 0, 1.5 * bk + 2.0 * go)
    Q.step(p, "l", "f", step if t < 1.05 else back, dz0=0 if t < 1.05 else -6.0, dz1=-6.0 if t < 1.05 else 0.0, lift=4.0)
    Q.foot(p, "r", "f", 0, -2.0 * go)
    return p


BLOCK_T = 1.0


def block(t):
    """the blow lands on the frill: the face ducks INTO it (the frill the shield), the impact drives the head up and
    back and the whole animal back onto its hind legs, a hind foot braces back, the frill rings, it comes down"""
    p = {}
    duck = f(tr((0, 0), (0.1, 1, ease_out), (0.5, 0.6), (1.0, 0, ease_out)), t)
    hit = kick(t, 0.12, 0.2, 0.04)
    rg = ring(t, 0.14, 3.2, 0.2)
    Q.alive(p, t, k=0.5, period=1.0)
    add(p, "body", rot=(2.0 * hit, -2.0 * hit, 1.5 * hit), pos=(0, -A.STAND_DROP - 0.5 * duck, 2.8 * hit))
    A.horns(p, 0.6 * duck)
    Q.head(p, 9 * hit + 3 * rg, -5 * hit, 6 * hit + 4 * rg)
    Q.trail(p, t, lambda u: 5.0 * kick(u, 0.12, 0.25, 0.04), delay=0.06)
    Q.counter_legs(p); A.lift_head(p)
    Q.step(p, "r", "h", (t - 0.18) / 0.3, dz0=0.0, dz1=3.0, lift=2.5)
    Q.foot(p, "l", "h", 0, 1.0 * hit)
    for s in SIDES: Q.foot(p, s, "f", 0, 1.5 * hit)
    return p


RECOIL_T = 1.1


def recoil(t):
    """its horns met the other's frill and glanced off: the head thrown aside and up, a forefoot stepping back to
    catch the weight, a slow heavy shake of the head"""
    p = {}
    hit = kick(t, 0.06, 0.24, 0.04)
    sh = ring(t, 0.45, 2.4, 0.22)
    Q.alive(p, t, k=0.5, period=1.1)
    add(p, "body", rot=(-1.0 * hit, 3.0 * hit, -2.0 * hit), pos=(0, -A.STAND_DROP - 0.6 * hit, 2.4 * hit))
    A.horns(p, 0.7 * (1 - smooth((t - 0.1) / 0.6)))
    Q.head(p, 7 * hit, 14 * hit + 5 * sh, -8 * hit - 9 * sh)
    Q.trail(p, t, lambda u: -6.0 * kick(u, 0.06, 0.3, 0.04) - 3 * ring(u, 0.45, 2.4, 0.25), delay=0.07)
    Q.counter_legs(p); A.lift_head(p)
    for s in SIDES: Q.foot(p, s, "h", 0, 1.0 * hit)
    Q.step(p, "r", "f", (t - 0.1) / 0.35, dz0=0.0, dz1=3.5, lift=3.0)
    Q.foot(p, "l", "f", 0, 0.8 * hit)
    return p


SUBMIT_T = 2.6


def submit(t):
    """beaten: it lifts its face, so the horns point to the sky and the frill turns edge-on, turns the head and the
    shoulders away, steps a forefoot back and lets the tail hang; the breath comes fast"""
    p = {}
    k = f(tr((0, 0), (0.7, 1, ease_out), (2.6, 1)), t)
    turn = f(tr((0, 0), (0.6, 0), (1.5, 1, ease_out), (2.6, 1)), t)
    Q.alive(p, t, k=0.9, period=0.65)
    add(p, "body", rot=(1.0 * k, -6 * turn, 2 * turn), pos=(0, -A.STAND_DROP - 0.8 * k, 1.0 * k))
    Q.head(p, 10 * k, -20 * turn, 10 * turn)
    add(p, "skull", rot=(6 * k, 0, 0))
    for i, b in enumerate(A.TAILS): add(p, b, rot=(2.0 * k * (0.5 + 0.3 * i), 2.0 * turn * (0.4 + 0.2 * i), 0))
    Q.counter_legs(p); A.lift_head(p)
    for s in SIDES: Q.foot(p, s, "h", 0, 0.8 * k)
    Q.step(p, "l", "f", (t - 0.7) / 0.5, dz0=0, dz1=3.0, dx1=0.8, lift=3.0)
    Q.foot(p, "r", "f", 0, 0.8 * k)
    return p


ATTACK_T = 1.0
AT_BACK = tr((0, 0), (0.24, 1, ease_out), (0.34, 0.7), (0.45, 0, ease_in))
AT_LUNGE = tr((0, 0), (0.24, 0), (0.45, 1, smooth), (0.6, 0.75), (1.0, 0, back_out))   # the body arrives, the horns strike
AT_TOSS = tr((0, 0), (0.45, 0), (0.58, 1.08, ease_out), (0.7, 1), (1.0, 0, smooth))
AT_TOSS_BODY = tr((0, 0), (0.45, 0), (0.68, 1, smooth), (1.0, 0, smooth))


def attack(t):
    """the toss in three beats (the hit at 0.45 s, as before): it rocks back with the horns cocked to one side, drives
    in from the hind legs with the horns levelled, then hooks them UP and to the side past the top and settles"""
    p = {}
    bk, lg, ts = f(AT_BACK, t), f(AT_LUNGE, t), f(AT_TOSS, t)
    dn = smooth(t / 0.25) * (1 - smooth((t - 0.5) / 0.25))
    Q.alive(p, t, k=0.5, period=1.0)
    # the drive comes from the hind legs and goes along the body (z), not down: a pitched-down chest would fold the
    # straight forelegs in a frame at the moment of the hit
    tb = f(AT_TOSS_BODY, t)                                # the body follows the toss a beat later and softer
    add(p, "body", rot=(2.0 * bk - 1.2 * lg + 3.0 * tb, -2.0 * bk - 3.0 * tb, 1.5 * bk + 2.0 * tb),
        pos=(0, -A.STAND_DROP - 0.5 * bk - 0.7 * dn, 1.6 * bk - 4.0 * lg))
    A.horns(p, dn)
    drive = f(tr((0, 0), (0.3, 0), (0.45, 1, ease_in), (0.55, 0.3, ease_out), (0.8, 0)), t)     # the horns' own snap in
    Q.head(p, 3 * bk - 4 * lg - 6 * drive + 30 * ts, -6 * bk + 8 * ts, 4 * bk - 14 * ts, k=0.5)
    A.jaw(p, -4 * ts)
    Q.trail(p, t, lambda u: 2.0 * f(AT_BACK, u) + 4.0 * f(AT_TOSS, u), delay=0.07)
    Q.trail(p, t, lambda u: -2.5 * f(AT_LUNGE, u), delay=0.06, axis=0, gain=Q.gains(0.5, 0.25))
    return Q.stance(p)                                  # the feet stay where they are: the body moves over them


# ------------------------------------------------------------------ horn lock: start, the loop, the break
LOCK_T = 3.2


def _lock(p, t, k, lt):
    """the locked pose at engagement k (0..1) and loop time lt: the horns down and twisted against the rival's, the
    weight thrown forward, two pushes a loop, a twist one way and the other, the hind feet braced back and the left
    one slipping in the second push and stepped back in; effort trembles in the neck while it pushes"""
    T = LOCK_T
    push = 0.5 - 0.5 * math.cos(2 * math.pi * (2 * lt / T - 0.15))         # two shoves a loop
    tw = math.sin(2 * math.pi * lt / T - 0.4)                               # the twist, one way and the other
    eff = C.loop_tremor(lt, T, (23, 31, 17), (0.8, 0.5, 0.3)) * (0.4 + 0.6 * push)
    add(p, "body", rot=(k * (-3.0 - 1.5 * push + 0.3 * eff), k * 2.0 * tw, k * (-2.5 * tw)), pos=(0, -A.STAND_DROP - k * (1.6 + 0.6 * push), -k * (2.0 + 2.5 * push)))
    A.horns(p, 1.1 * k)
    Q.head(p, k * (-3 * push + 0.6 * eff), k * 6 * tw, k * 20 * tw)
    add(p, "skull", rot=(k * 0.5 * eff, 0, 0))
    A.jaw(p, -k * 2.0 * push)
    for i, b in enumerate(A.TAILS):
        add(p, b, rot=(-k * (2.0 + 1.0 * push) * (0.6 + 0.2 * i), -k * 3.5 * (1 + 0.4 * i) * math.sin(2 * math.pi * lt / T - 0.4 - 0.5 * (i + 1)), 0))


def _lock_feet(p, k, lt):
    T = LOCK_T
    # the slip: in the second shove the left hind foot is driven back along the ground, then picked up and set in
    slip = smooth((lt - 1.75) / 0.35) * (1 - smooth((lt - 2.45) / 0.01)) if lt < 2.45 else 0.0
    st = (lt - 2.45) / 0.45
    Q.counter_legs(p); A.lift_head(p)
    hb = 2.5 * k
    Q.foot(p, "r", "h", 0, hb + 0.6 * k * math.sin(2 * math.pi * (2 * lt / T - 0.4)))
    if 0.0 < st < 1.0:
        Q.step(p, "l", "h", st, dz0=hb + 2.6, dz1=hb, lift=3.0)
    else:
        Q.foot(p, "l", "h", 0, hb + 2.6 * slip)
    for i, s in enumerate(SIDES):
        Q.foot(p, s, "f", 0, -2.5 * k, (1.2 if s == "l" else -1.2) * k)


def horn_lock(t):
    """the loop (3.2 s, the old one-shot's length): locked, pushing, twisting, the feet bracing and slipping"""
    p = {}
    Q.alive(p, t, k=0.9, period=LOCK_T / 4)
    _lock(p, t, 1.0, t % LOCK_T)
    _lock_feet(p, 1.0, t % LOCK_T)
    return p


LOCK_START_T = 1.2


def horn_lock_start(t):
    """into the lock: the head goes down as it steps in, a last lunge, the clack of horn on horn (0.7 s), and it is
    braced in the loop's first pose"""
    p = {}
    k = f(tr((0, 0), (0.55, 0.85, ease_in), (0.7, 1.12, ease_out), (0.85, 0.97), (1.2, 1.0, smooth)), t)
    clack = kick(t, 0.7, 0.1, 0.03)
    Q.alive(p, t - LOCK_START_T, k=0.9, period=LOCK_T / 4)        # in step with the loop it hands over to
    _lock(p, 0.0, min(k, 1.0), 0.0)
    add(p, "body", pos=(0, 0, -1.5 * max(0.0, k - 1.0) / 0.12 + 1.2 * clack))
    Q.head(p, 4 * clack, 0, 0)
    stepping = (t - 0.15) / 0.45
    Q.counter_legs(p); A.lift_head(p)
    kk = min(k, 1.0)
    Q.foot(p, "l", "h", 0, 2.5 * kk)
    Q.foot(p, "r", "h", 0, kk * (2.5 + 0.6 * math.sin(-0.8 * math.pi)))
    Q.step(p, "l", "f", stepping, dz0=0.0, dz1=-2.5, dx0=0.0, dx1=1.2, lift=3.5)
    Q.step(p, "r", "f", stepping - 0.25, dz0=0.0, dz1=-2.5, dx0=0.0, dx1=-1.2, lift=3.5)
    return p


LOCK_BREAK_T = 1.4


def horn_lock_break(t):
    """out of the lock: a last wrench to the side frees the horns, the head tossed up, a step back with a forefoot
    and the hind end, a shake, and it stands"""
    p = {}
    k = f(tr((0, 1), (0.3, 1), (0.75, 0, ease_out), (1.4, 0)), t)
    wrench = f(tr((0, 0), (0.12, 1, ease_in), (0.3, 1.1), (0.6, 0, ease_out)), t)
    toss = kick(t, 0.32, 0.22, 0.08)
    sh = ring(t, 0.7, 2.6, 0.2)
    Q.alive(p, t, k=0.9, period=LOCK_T / 4)
    _lock(p, 0.0, k, 0.0)
    add(p, "body", rot=(2.0 * toss, -3.0 * wrench, 2.0 * wrench), pos=(0, 0, 1.6 * toss))
    Q.head(p, 18 * toss, -10 * wrench + 3 * sh, -18 * wrench + 8 * sh)
    Q.trail(p, t, lambda u: 6 * f(tr((0, 0), (0.12, 1, ease_in), (0.3, 1.1), (0.6, 0, ease_out)), u) + 3 * ring(u, 0.7, 2.6, 0.24), delay=0.07)
    Q.counter_legs(p); A.lift_head(p)
    Q.step(p, "l", "f", (t - 0.35) / 0.4, dz0=-2.5, dz1=0.0, dx0=1.2, dx1=0.0, lift=3.5)
    Q.step(p, "r", "f", (t - 0.6) / 0.4, dz0=-2.5, dz1=0.0, dx0=-1.2, dx1=0.0, lift=3.5)
    Q.foot(p, "l", "h", 0, 2.5 * k)
    Q.foot(p, "r", "h", 0, k * (2.5 + 0.6 * math.sin(-0.8 * math.pi)))
    return p


# ------------------------------------------------------------------ lying down and getting up (front last, front first)
LIE_DOWN_T = 2.6


def lie_down(t):
    """the hind end goes down first (the body tips nose-up on straight forelegs), then the front folds onto the
    wrists, a grunt as the chest lands, the head settles; it ends in `sit`'s pose"""
    p = {}
    k = f(tr((0, 0), (0.3, 0.02), (1.3, 1.0, smooth), (2.6, 1.0)), t)
    kf = f(tr((0, 0), (0.9, 0.05), (1.95, 1.0, smooth), (2.6, 1.0)), t)
    land = kick(t, 1.95, 0.18, 0.05)
    A.lie(p, k, kf=min(kf, 1.0))
    add(p, "body", rot=(-0.8 * land, 0, 0))
    Q.head(p, -5 * land - 4 * window(t, 0.3, 1.6, 0.4), 0, 0)
    A.jaw(p, -2.5 * land)
    Q.alive_upper(p, t, k=0.6, period=1.3)
    Q.trail(p, t, lambda u: 2.0 * kick(u, 1.95, 0.25, 0.05), delay=0.07, axis=0)
    p = A.settle(A.lift_tail(A.lift_head(p, 0.0)))
    w = smooth((t - 2.2) / 0.4)
    return C.blend(p, sit(0.0), w) if w > 0 else p


GET_UP_T = 2.4


def get_up(t):
    """from `sit`: the head swings up and forward, the forelegs straighten FIRST (the body tips nose-up), then the
    hind end heaves up; a wobble of the weight, the tail answering"""
    p = {}
    kf = f(tr((0, 1), (0.35, 1), (1.1, 0, smooth), (2.4, 0)), t)
    k = f(tr((0, 1), (0.9, 1), (1.75, 0, smooth), (2.4, 0)), t)
    swing = bump(t, 0.5, 0.2)
    wob = ring(t, 1.75, 1.8, 0.3)
    A.lie(p, k, kf=kf)
    Q.head(p, 6 * swing - 4 * bump(t, 1.2, 0.25), 0, 0)
    add(p, "body", rot=(0, 0, 1.6 * wob))
    Q.alive_upper(p, t, k=0.6, period=1.2)
    Q.trail(p, t, lambda u: -2.5 * ring(u, 1.75, 1.8, 0.35), delay=0.07)
    p = A.settle(A.lift_tail(A.lift_head(p, 0.0)))
    w = 1 - smooth(t / 0.35)
    return C.blend(sit(0.0), p, 1 - w) if w > 0 else p


# ------------------------------------------------------------------ the old ones, made fluid
def _upper(name, k=0.5, period=None, tail=None):
    """wrap an original: the breathing layer and a slow tail sway on top (the feet already planted)"""
    fn = _O[name]
    L = A.ANIMS[name][1]
    per = period or (L / max(1, round(L / 1.6)))

    def g(t):
        p = fn(t)
        before = Q.head_low(p)
        Q.alive_upper(p, t, k=k, period=per, slow=L if A.ANIMS[name][2] else None)
        if tail: tail(p, t)
        A.lift_tail(p)                                  # a tail lying on the ground must not breathe into it
        return Q.keep_head(p, before)
    g.__doc__ = fn.__doc__
    return g


_HS = tr((0, 0), (0.25, -1, ease_out), (0.5, 1, ease_in), (0.7, 1), (1.2, 0, smooth))
horn_sweep = _upper("horn_sweep", 0.4, tail=lambda p, t: Q.trail(p, t, lambda u: -5.0 * f(_HS, u), delay=0.07))
hurt = _upper("hurt", 0.4, tail=lambda p, t: Q.trail(p, t, lambda u: 4.0 * math.exp(-u / 0.2) * smooth(u / 0.05), delay=0.05))
stamp = _upper("stamp", 0.6, tail=lambda p, t: Q.trail(p, t, lambda u: 2.5 * sum(bump(u, c + 0.15, 0.1) for c in (0.45, 0.95)), delay=0.06, axis=0))
pivot = _upper("pivot", 0.6, tail=lambda p, t: Q.trail(p, t, lambda u: 3.0 * math.sin(2 * math.pi * (u - 0.5) / 0.9) * window(u, 0.3, 2.0, 0.3), delay=0.1))
eat, graze, plow, shear = _upper("eat", 0.4), _upper("graze", 0.4), _upper("plow", 0.4), _upper("shear", 0.5)
beg = _upper("beg", 0.6, period=1.2)
tame = _upper("tame", 0.6)
butt_play = _upper("butt_play", 0.4)
sit = _upper("sit", 0.5, period=8.0 / 3)
sleep = _upper("sleep", 0.4, period=10.0 / 3)
knocked_out = _upper("knocked_out", 0.3, period=4.2)
wake_sleep = _upper("wake_sleep", 0.5, tail=lambda p, t: Q.trail(p, t, lambda u: 3.0 * ring(u, 1.6, 2.2, 0.3), delay=0.08))
wake = _upper("wake", 0.5, tail=lambda p, t: Q.trail(p, t, lambda u: 4.0 * window(u, 1.2, 1.9, 0.12) * math.sin(2 * math.pi * u / 0.3), delay=0.08))
wallow = _upper("wallow", 0.4)


def _quad(u): u = min(1.0, max(0.0, u)); return u * u


def _going_down(t):
    """the old fall (the head first, the forelegs buckle, the hind end sits), its tracks eased so the legs fold over
    several frames instead of in one (they were ease_in cubes: 60-75 deg a frame at the end)"""
    p = {}
    st = window(t, 0.0, 0.6, 0.2)
    hd = f(tr((0, 0), (0.4, 1, smooth), (2.0, 1)), t)
    kf = f(tr((0, 0), (0.3, 0), (0.95, 1, _quad), (2.0, 1)), t)
    k = f(tr((0, 0), (0.6, 0), (1.3, 1, _quad), (2.0, 1)), t)
    add(p, "body", rot=(0, 3 * st * math.sin(2 * math.pi * t / 0.6), 5 * st), pos=(1.5 * st, 0, 0))
    A.lie(p, k, kf=kf, pitch=-10 * (kf - k))
    A.head(p, -18 * hd + 8 * kf, -8 * st, 6 * hd)
    A.jaw(p, -8 * hd)
    return A.settle(A.lift_tail(A.lift_head(p, 0.0)))


_DOWN = []


def death(t):
    """the fall, then two last breaths that fade and the tail tip going still"""
    if t <= 1.4:
        p = _going_down(t)
    else:
        if not _DOWN: _DOWN.append(_going_down(1.4))
        roll = f(tr((1.4, 0), (2.05, 1, _quad), (2.17, 0.95), (2.3, 1, smooth), (2.8, 1)), t)
        p = A.shift_to_ground(A.blend(_DOWN[0], A.ko_pose({}, 1.0), roll))
    fade = 1.0 - smooth((t - 1.6) / 1.1)
    for c, a in ((1.0, 0.8), (2.4, 1.0), (2.7, 0.5)):
        g = bump(t, c, 0.14) * a
        add(p, "body", rot=(1.0 * g, 0, 0)); A.jaw(p, -2.5 * g)
    tw = sum(a * bump(t, c, 0.06) for c, a in ((1.5, 1.0), (1.85, -0.6), (2.45, 0.3)))
    for i, b in enumerate(A.TAILS): add(p, b, rot=(0, 2.0 * (i + 1) * tw * fade, 0))
    return p


ANIMS = {
    "idle": (idle, IDLE_T, True, "Parado", "respira fundo (três por laço), descansa uma pata de trás, olha e fareja; nada em fase"),
    "walk": (walk, A.WALK[0], True, "Movimento", "passo pesado: o quadril cai do lado da pata no ar, a cabeça firme acena atrasada"),
    "run": (run, A.RUNP[0], True, "Movimento", "galope de rinoceronte com o peso no lombo e a cauda atrasada"),
    "charge": (charge, A.CHARGEP[0], True, "Só dele", "a carga: chifres nivelados, cabeça firme, cauda dura"),
    "attack": (attack, ATTACK_T, False, "Combate", "a chifrada em três tempos: recua, investe (golpe em 0,45 s), engancha para cima"),
    "horn_sweep": (horn_sweep, 1.2, False, "Só dele", "varre os chifres de um lado para o outro, a cauda responde atrasada"),
    "horn_lock": (horn_lock, LOCK_T, True, "Só dele", "LAÇO: chifres travados com o rival, empurra duas vezes, torce, os pés firmam e escorregam"),
    "horn_lock_start": (horn_lock_start, LOCK_START_T, False, "Só dele", "entra no engalfinhar: abaixa, avança e trava os chifres (estalo em 0,7 s)"),
    "horn_lock_break": (horn_lock_break, LOCK_BREAK_T, False, "Só dele", "sai do engalfinhar: torce, solta, joga a cabeça e recua"),
    "guard": (guard, GUARD_T, True, "Duelo", "em guarda: chifres apontados, babado de escudo, peso nas patas da frente, bufa"),
    "strafe_left": (strafe_left, STRAFE_T, True, "Duelo", "passo de lado para a esquerda, pesado, chifres no rival"),
    "strafe_right": (strafe_right, STRAFE_T, True, "Duelo", "passo de lado para a direita, pesado, chifres no rival"),
    "turn_left": (turn_left, TURN_T, True, "Movimento", "gira no lugar para a esquerda: patas da frente para dentro da curva, as de trás para fora"),
    "turn_right": (turn_right, TURN_T, True, "Movimento", "gira no lugar para a direita"),
    "feint": (feint, FEINT_T, False, "Duelo", "carga falsa: recua, joga o peso à frente com uma pisada e para seco"),
    "block": (block, BLOCK_T, False, "Duelo", "apara o golpe com o babado: abaixa a cara contra ele, o tranco o empurra para trás"),
    "recoil": (recoil, RECOIL_T, False, "Duelo", "a chifrada bateu no babado do outro: a cabeça vai de lado, recua uma pata"),
    "submit": (submit, SUBMIT_T, False, "Duelo", "perdeu: ergue a cara, vira o babado de lado e o corpo para longe"),
    "lie_down": (lie_down, LIE_DOWN_T, False, "Descanso", "deita: primeiro o quadril, depois a frente; termina como sit"),
    "get_up": (get_up, GET_UP_T, False, "Descanso", "levanta de sit: primeiro a frente, depois o quadril"),
    "idle_tired": (idle_tired, IDLE_TIRED_T, True, "Parado", "cansado: ofega, bico aberto, chifres caídos"),
    "walk_tired": (walk_tired, WALK_TIRED_T, True, "Movimento", "andando cansado: 32 px por ciclo de 1,9 s, cabeça baixa, ofegando"),
    "stamp": (stamp, 1.9, False, "Só dele", "antes da carga: bate a pata e bufa (com respiração e cauda)"),
    "pivot": (pivot, 2.4, False, "Só dele", "gira o quadril em volta das patas da frente (com respiração e cauda)"),
    "hurt": (hurt, 0.6, False, "Combate", "ao levar dano, a cauda chicoteia atrasada"),
    "death": (death, 2.8, False, "Combate", "a queda antiga e dois últimos fôlegos"),
    "eat": (eat, 2.8, False, "Comer", "come (com respiração)"),
    "graze": (graze, 3.4, False, "Comer", "pasta (com respiração)"),
    "plow": (plow, 2.9, False, "Só dele", "ara o chão (com respiração)"),
    "shear": (shear, 3.2, False, "Só dele", "arranca galho (com respiração)"),
    "wallow": (wallow, 6.0, False, "Só dele", "rola na lama (com respiração)"),
    "butt_play": (butt_play, 1.8, False, "Só dele", "filhote brinca (com respiração)"),
    "sit": (sit, 8.0, True, "Descanso", "deitado como boi, respirando"),
    "sleep": (sleep, 10.0, True, "Descanso", "dorme, respirando fundo"),
    "wake_sleep": (wake_sleep, 2.4, False, "Descanso", "acorda, a cauda acompanha"),
    "knocked_out": (knocked_out, 4.2, True, "Descanso", "nocauteado, respirando"),
    "wake": (wake, 3.4, False, "Descanso", "acorda do nocaute, a cauda acompanha a sacudida"),
    "beg": (beg, 2.4, True, "Domado", "pede comida (com respiração)"),
    "tame": (tame, 2.6, False, "Domado", "aceita o dono (com respiração)"),
}
