"""Styracosaurus: the fluid set and the fighting set (06/11/2026), from its own body and its own study.

The study (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md and the page "Estiracossauro: estudo para a 1.8"): the long
spikes of the crown are for show (Padian & Horner 2011), the one long nose horn is the weapon. So it fights by
SHOWING first and stabbing short: it tips the crown at the rival and swings it so the spikes flash, bobs the head,
and when it strikes it is a quick jab of the nose horn, not a long shove; it is a 5.5 m, 2.7 t herd animal, a third
of a Triceratops, quicker and more nervous.

What its body makes of the T. rex study's principles (docs/estudos/08_ANIMACAO_RAXIORES.md):
  * brisk: short loops (the guard 2.4 s, the turn and the strafe 1.6 s), longer and higher steps for its size, a
    springier body; its head is NOT held still: the big crown bobs on every forefoot and nods late (the walk's own
    signature, kept and made heavier);
  * the guard is half display: the nose horn levelled but the crown tilted toward the rival and rocking, with two
    sharp challenge bobs a loop;
  * the strafe turns the crown toward the rival as it circles; the feint is a short mock charge in which the front
    hops off the ground and the crown flashes; the block takes the blow on the crown's side, the spikes ringing fast;
  * it gives in by laying the crown back flat over its neck, nose up, the one thing it never does in a fight.
Signs as in triceratops/ceraflow.py.
"""
import importlib.util
import math
import os
import sys

_CF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "triceratops", "ceraflow.py")
if "ceraflow" not in sys.modules:
    _spec = importlib.util.spec_from_file_location("ceraflow", _CF)
    sys.modules["ceraflow"] = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sys.modules["ceraflow"])
import ceraflow as C  # noqa: E402
import styracoanims as A  # noqa: E402
from anim2 import add, smooth, ease_in, ease_out, back_out  # noqa: E402

tr, f, wave, window, bump, ring, kick, tremor = C.tr, C.f, C.wave, C.window, C.bump, C.ring, C.kick, C.tremor
Q = C.Quad(A, A.horn_level, hind=(16, 12, 14), fore=(14, 30), head_k=0.5, scap=(0.25, 0.05))
SIDES = A.SIDES
Q.adopt()                                           # the originals plant their feet through the stable IK too
_O = {n: v[0] for n, v in A.ANIMS.items()}


# ------------------------------------------------------------------ gaits
def walk(t):
    """brisk: the hips roll, the crown bobs down on every forefoot and comes up late, the tail swings wide"""
    Tc, stride, duty, lift = A.WALK[:4]               # the game's cycle and stride; a shorter stance (0.6), a gentler swing
    return Q.gait(t, Tc, stride, 0.6, lift, A.LATERAL, bob=0.8, hd=-1, roll=3.6, yaw=2.2, nod=1.9, head_keep=0.35, head_lag=0.16,
                  neck_roll=0.5, tail_yaw=4.0, tail_lag=0.1, tail_pitch=0.9)


def run(t):
    Tc, stride, duty, lift, bob, rock = A.RUNP
    duty = 0.31                                          # was 0.38: a longer swing, the legs fold without snapping
    return Q.gait(t, Tc, stride, duty, lift, A.BOUND, flift=lift * 1.1, bob=bob, drop=1.0, lean=-1.0, hd=-2, roll=2.0,
                  yaw=1.4, rock=rock, nod=1.4, head_keep=0.55, head_lag=0.14, neck_roll=0.5, tail_yaw=3.0, tail_lag=0.08,
                  tail_pitch=2.6)


def charge(t):
    Tc, stride, duty, lift, bob, rock = A.CHARGEP
    duty = 0.29                                          # was 0.36: a longer swing
    return Q.gait(t, Tc, stride, duty, lift, A.BOUND, flift=lift * 1.1, bob=bob, drop=1.0, lean=-2.0, hd=-2, roll=1.4,
                  yaw=1.0, rock=rock, nod=0.8, head_keep=0.85, head_lag=0.1, neck_roll=0.8, tail_yaw=1.8, tail_lag=0.07,
                  tail_pitch=2.0, tail_base=-4.0, weapon=1.0, jaw=-2.5)


WALK_TIRED_T = 1.5


def walk_tired(t):
    """spent: 30 px a cycle of 1.5 s, the crown sagging, the mouth open, the nod gone heavy and slow"""
    return Q.gait(t, WALK_TIRED_T, 30, 0.7, 4.0, A.LATERAL, bob=1.1, drop=0.5, lean=-1.2, hd=-9, roll=4.4, yaw=2.0,
                  nod=2.2, head_keep=0.3, head_lag=0.22, neck_roll=0.4, tail_yaw=2.6, tail_lag=0.11, tail_pitch=0.7,
                  tail_base=2.0, jaw=-6.0, pant=5.0)


# ------------------------------------------------------------------ the idle
IDLE_T = 7.0
LOOK = tr((0, (0, 0)), (1.0, (0, 0)), (1.6, (3, 18), ease_out), (2.5, (2, 16)), (3.0, (-1, -16), ease_out), (3.9, (-2, -14)),
          (4.6, (2, 4), ease_out), (5.6, (1, 3)), (6.3, (-5, 0), ease_out), (7.0, (0, 0), ease_in))


def idle(t):
    """a herd animal on watch: quick looks over the herd with holds, the crown twitching like ears, the weight
    passing from one forefoot to the other, a quick breath (three a loop) and the tail never quite still"""
    T = IDLE_T; p = {}
    Q.alive(p, t, k=1.1, period=T / 3)
    lp, ly = LOOK(t)
    shift = wave(t, T, 0.5) + 0.3 * wave(t, T / 2, -0.8)
    add(p, "body", rot=(0, 0.08 * ly, 1.4 * shift), pos=(0, -A.STAND_DROP, 0))
    tw = ring(t, 5.15, 4.5, 0.12) + 0.7 * ring(t, 2.55, 4.5, 0.1)
    Q.head(p, lp + 0.8 * wave(t, T / 5, 0.6), ly + 1.2 * wave(t, T / 5, -0.4), -0.15 * ly + 6 * tw)
    for i, b in enumerate(A.TAILS):
        add(p, b, rot=(0.3 * i * wave(t, T / 3, -0.5 * i), (1.0 + 1.3 * i) * wave(t, T, -0.9 * i) + 0.7 * i * wave(t, T / 2, 0.5 - 0.8 * i), 0))
    fl = bump(t, 6.45, 0.12)
    A.tail(p, yaw=8 * fl * math.sin(2 * math.pi * (t - 6.3) / 0.4))
    return Q.stance(p, fore=(-0.6 * max(0.0, shift), 0.0), clear=0.3)


IDLE_TIRED_T = 2.5


def idle_tired(t):
    """after a fight: quick shallow panting (five a loop), the mouth open, the crown down to the shoulders, the weight
    shifting from foot to foot"""
    T = IDLE_TIRED_T; p = {}
    pant = wave(t, T / 5)
    add(p, "body", rot=(-1.0 + 1.2 * pant, 0, 1.4 * wave(t, T, 0.4)), pos=(0, -A.STAND_DROP - 0.8 + 0.6 * pant, 0))
    Q.head(p, -12 - 1.4 * wave(t, T / 5, -0.7), 3.0 * wave(t, T, 1.2), 2.0 * wave(t, T, -0.3))
    A.jaw(p, -8 - 4 * max(0.0, wave(t, T / 5, -0.5)))
    for i, b in enumerate(A.TAILS):
        add(p, b, rot=(2.0 + 0.4 * i * pant, (0.8 + 0.8 * i) * wave(t, T, -0.8 * i), 0))
    return Q.stance(p, fore=(-1.0, -1.0), fdx=(0.8, -0.8), clear=0.4)


# ------------------------------------------------------------------ the fight
GUARD_T = 2.4


def guard(t):
    """half guard, half display: the nose horn at the rival, the face tipped so the crown fans toward it and rocks
    from side to side, the weight springing on the forelegs, two sharp challenge bobs a loop, the tail lashing"""
    T = GUARD_T; p = {}
    rock = wave(t, T, 0.3)
    bob = sum(bump(t, c, 0.07) for c in (0.55, 1.75)) - 0.5 * sum(bump(t, c + 0.12, 0.08) for c in (0.55, 1.75))
    spring = wave(t, T / 2, -0.4)
    Q.alive(p, t, k=0.8, period=T / 3)
    add(p, "body", rot=(-1.5 - 0.6 * spring, 1.2 * rock, -1.0 * rock), pos=(0, -A.STAND_DROP - 0.9 + 0.5 * spring - 0.6 * bob, -1.0 - 0.6 * spring))
    A.horn_level(p, 0.75)
    Q.head(p, -4 - 8 * bob, 4.0 * rock, 14 * rock)
    A.jaw(p, -2.0 * bump(t, 1.2, 0.15))
    for i, b in enumerate(A.TAILS):
        add(p, b, rot=(-1.0 * (0.5 + 0.2 * i), -(1.5 + 1.4 * i) * wave(t, T / 2, 0.5 - 0.8 * (i + 1)), 0))
    return Q.stance(p, fore=(-2.0, -2.0), hind=(0.5, 0.5), fdx=(0.6, -0.6), clear=0.3)


STRAFE_T = 1.6


def _crown_to_rival(side):
    d = 1.0 if side == "left" else -1.0

    def extra(p, t, w):
        # the crown kept turned toward the rival as it circles: the face rolled so the spikes face it
        add(p, "skull", rot=(0, 0, -d * (10 + 3 * math.sin(2 * w - 0.8))))
    return extra


def strafe_left(t): return Q.strafe(t, "left", STRAFE_T, step_dx=3.0, lift=4.5, lean=2.2, guard=0.7, look=6.0, tail_yaw=3.0, drop=0.9, extra=_crown_to_rival("left"))
def strafe_right(t): return Q.strafe(t, "right", STRAFE_T, step_dx=3.0, lift=4.5, lean=2.2, guard=0.7, look=6.0, tail_yaw=3.0, drop=0.9, extra=_crown_to_rival("right"))


TURN_T = 1.6


def turn_left(t): return Q.turn(t, "left", TURN_T, fore_dx=3.4, hind_dx=2.6, lift=4.5, lead_yaw=10.0, body_yaw=3.0, roll=1.8, bob=0.6, tail_yaw=3.2)
def turn_right(t): return Q.turn(t, "right", TURN_T, fore_dx=3.4, hind_dx=2.6, lift=4.5, lead_yaw=10.0, body_yaw=3.0, roll=1.8, bob=0.6, tail_yaw=3.2)


FEINT_T = 1.2
FT_GO = tr((0, 0), (0.18, -0.3, ease_out), (0.42, 1, ease_in), (0.52, 1.08), (0.7, 0.8), (1.2, 0, back_out))
FT_HOP = tr((0, 0), (0.3, 0), (0.42, 1, ease_out), (0.55, 0, ease_in), (1.2, 0))


def feint(t):
    """the mock charge: a crouch, a dart forward in which the front leaves the ground in a short hop, the nose horn
    hooking up at nothing and the crown flashing to one side; then it backs off"""
    p = {}
    go, hop = f(FT_GO, t), f(FT_HOP, t)
    flash = window(t, 0.45, 0.8, 0.12)
    Q.alive(p, t, k=0.6, period=0.6)
    add(p, "body", rot=(3.0 * hop - 2.0 * max(0.0, go), 0, -2.0 * flash), pos=(0, -A.STAND_DROP - 0.8 * max(0.0, go) + 0.6 * hop, -3.5 * go))
    A.horn_level(p, 0.6 + 0.4 * max(0.0, go))
    Q.head(p, 10 * bump(t, 0.56, 0.08) - 3 * hop, 5 * flash, 18 * flash)
    Q.trail(p, t, lambda u: -3.0 * f(FT_HOP, u) + 2.0 * f(FT_GO, u), delay=0.06, axis=0, gain=Q.gains(0.4, 0.35))
    Q.trail(p, t, lambda u: 3.0 * window(u, 0.45, 0.8, 0.12), delay=0.07)
    Q.counter_legs(p); A.lift_head(p)
    for s in SIDES: Q.foot(p, s, "h", 0, 1.5 * max(0.0, go))
    for s in SIDES: Q.foot(p, s, "f", 3.5 * hop, -2.5 * max(0.0, go), pitch=-14 * hop, clear=-0.05 if hop < 0.05 else 0.3)
    return p


BLOCK_T = 0.8


def block(t):
    """the blow taken on the side of the crown: the head turned to catch it on the spikes, knocked sideways, the
    crown ringing fast and light, a forefoot stepping out to catch the weight"""
    p = {}
    catch = f(tr((0, 0), (0.08, 1, ease_out), (0.4, 0.5), (0.8, 0, ease_out)), t)
    hit = kick(t, 0.1, 0.16, 0.03)
    rg = ring(t, 0.12, 4.6, 0.15)
    Q.alive(p, t, k=0.5, period=0.8)
    add(p, "body", rot=(1.0 * hit, 3.0 * hit, 4.0 * hit), pos=(0, -A.STAND_DROP - 0.4 * catch, 1.2 * hit))
    A.horn_level(p, 0.4 * catch)
    Q.head(p, 4 * hit, 8 * catch + 10 * hit, -16 * catch + 9 * rg)
    Q.trail(p, t, lambda u: -6.0 * kick(u, 0.1, 0.2, 0.03), delay=0.05)
    Q.counter_legs(p); A.lift_head(p)
    Q.step(p, "r", "f", (t - 0.12) / 0.25, dx0=0.0, dx1=-2.0, dz1=0.8, lift=3.0)
    Q.foot(p, "l", "f", 0, 0.5 * hit)
    for s in SIDES: Q.foot(p, s, "h", 0, 0.6 * hit)
    return p


RECOIL_T = 0.9


def recoil(t):
    """its jab skidded off the other's crown: the nose snapped up and back, the crown shivering, both forefeet
    skipping back a little, a shake"""
    p = {}
    hit = kick(t, 0.05, 0.18, 0.03)
    sh = ring(t, 0.35, 3.8, 0.16)
    hop = math.sin(math.pi * smooth((t - 0.06) / 0.3))
    Q.alive(p, t, k=0.5, period=0.9)
    add(p, "body", rot=(2.5 * hit, -2.0 * hit, 0), pos=(0, -A.STAND_DROP + 0.5 * hop, 1.8 * hit))
    A.horn_level(p, 0.8 * (1 - smooth((t - 0.05) / 0.3)))
    Q.head(p, 14 * hit, -6 * hit + 4 * sh, 12 * sh)
    Q.trail(p, t, lambda u: -3.5 * kick(u, 0.05, 0.22, 0.03), delay=0.05, axis=0, gain=Q.gains(0.5, 0.3))
    Q.trail(p, t, lambda u: 3.0 * ring(u, 0.35, 3.8, 0.2), delay=0.06)
    Q.counter_legs(p); A.lift_head(p)
    back = 2.5 * smooth((t - 0.06) / 0.3)
    for s in SIDES:
        Q.foot(p, s, "f", 2.5 * hop, back, pitch=-10 * hop, clear=-0.05 if hop < 0.05 else 0.3)
        Q.foot(p, s, "h", 0, 0.6 * hit)
    return p


SUBMIT_T = 2.2


def submit(t):
    """beaten: the crown laid back flat over the neck (nose up, the spikes hidden), the body turned away and low,
    the tail clamped, quick breaths"""
    p = {}
    k = f(tr((0, 0), (0.5, 1, ease_out), (2.2, 1)), t)
    turn = f(tr((0, 0), (0.4, 0), (1.2, 1, ease_out), (2.2, 1)), t)
    Q.alive(p, t, k=0.9, period=0.55)
    add(p, "body", rot=(0.5 * k, 7 * turn, -2.5 * turn), pos=(0, -A.STAND_DROP - 1.2 * k, 0.8 * k))
    Q.head(p, 14 * k, 18 * turn, -6 * turn, k=0.4)
    add(p, "skull", rot=(10 * k, 0, 0))
    for i, b in enumerate(A.TAILS): add(p, b, rot=(3.0 * k * (0.5 + 0.3 * i), -3.0 * turn * (0.4 + 0.3 * i), 0))
    Q.counter_legs(p); A.lift_head(p)
    Q.step(p, "r", "f", (t - 0.5) / 0.35, dz1=2.5, dx1=-0.8, lift=3.5)
    Q.foot(p, "l", "f", 0, 0.6 * k)
    for s in SIDES: Q.foot(p, s, "h", 0, 0.5 * k)
    return p


ATTACK_T = 0.9
AT_BACK = tr((0, 0), (0.2, 1, ease_out), (0.3, 0.8), (0.4, 0, ease_in))
AT_LUNGE = tr((0, 0), (0.2, 0), (0.4, 1, smooth), (0.55, 0.6), (0.9, 0, back_out))       # the body arrives, the horn strikes
AT_HOOK = tr((0, 0), (0.4, 0), (0.5, 1.1, ease_out), (0.62, 1), (0.9, 0, smooth))
AT_HOOK_BODY = tr((0, 0), (0.4, 0), (0.6, 1, smooth), (0.9, 0, smooth))


def attack(t):
    """the gore in three beats (the hit at 0.4 s, as before): the head flung up and back with the crown flaring, the
    dip and lunge with the nose horn levelled, the hook UP past the top, the crown thrown back, and the settle"""
    p = {}
    bk, lg, hk = f(AT_BACK, t), f(AT_LUNGE, t), f(AT_HOOK, t)
    dn = smooth((t - 0.12) / 0.15) * (1 - smooth((t - 0.45) / 0.15))
    Q.alive(p, t, k=0.5, period=0.9)
    hb = f(AT_HOOK_BODY, t)                                 # the body follows the hook later and softer
    add(p, "body", rot=(2.0 * bk - 1.2 * lg + 3.0 * hb, 0, 0), pos=(0, -A.STAND_DROP - 0.4 * bk - 0.6 * dn, 1.4 * bk - 3.6 * lg))
    A.horn_level(p, dn)
    drive = f(tr((0, 0), (0.26, 0), (0.4, 1, ease_in), (0.5, 0.3, ease_out), (0.75, 0)), t)
    Q.head(p, 9 * bk - 4 * lg - 6 * drive + 34 * hk, 0, 4 * bk * math.sin(2 * math.pi * t / 0.2), k=0.45)
    A.jaw(p, -5 * hk)
    Q.trail(p, t, lambda u: 3.0 * f(AT_BACK, u) - 3.5 * f(AT_LUNGE, u) - 2.0 * f(AT_HOOK, u), delay=0.06, axis=0, gain=Q.gains(0.5, 0.3))
    return Q.stance(p)                                  # the feet stay where they are: the body moves over them


NOSE_JAB_T = 0.8
NJ_COCK = tr((0, 0), (0.16, 1, ease_out), (0.24, 0.6), (0.3, 0, ease_in), (0.8, 0))
NJ_JAB = tr((0, 0), (0.17, 0), (0.3, 1, ease_in), (0.36, 1.05), (0.46, 0.4, ease_out), (0.8, 0, back_out))
NJ_FLICK = tr((0, 0), (0.3, 0), (0.38, 1, ease_out), (0.5, 0.2), (0.8, 0, smooth))


def nose_jab(t):
    """THE SIGNATURE: a short stab of the nose horn (the hit at 0.3 s), quick as a fencer's: the head cocked up with a
    flick of the crown, the jab straight in from the neck with the shoulders behind it, a little upward flick of the
    point, and back on guard. No lunge of the whole body, as the Triceratops does: only the front leans in"""
    p = {}
    ck, jb, fl = f(NJ_COCK, t), f(NJ_JAB, t), f(NJ_FLICK, t)
    Q.alive(p, t, k=0.4, period=0.8)
    # the shoulders barely sink (the straight pillar of the foreleg would fold fast under any drop): the neck jabs
    add(p, "body", rot=(0.8 * ck - 0.8 * jb, 0, 0), pos=(0, -A.STAND_DROP - 0.2 * ck - 0.3 * jb, 0.6 * ck - 2.0 * jb))
    A.horn_level(p, 0.55 + 0.45 * jb - 0.3 * ck)
    Q.head(p, 8 * ck - 8 * jb + 12 * fl, -3 * ck, 7 * ck, k=0.6)
    Q.trail(p, t, lambda u: 1.8 * f(NJ_COCK, u) - 2.4 * f(NJ_JAB, u), delay=0.05, axis=0, gain=Q.gains(0.5, 0.3))
    Q.trail(p, t, lambda u: -2.0 * f(NJ_COCK, u), delay=0.06)
    return Q.stance(p, fore=(-1.6 * jb, -1.6 * jb), hind=(0.8 * jb, 0.8 * jb))


# ------------------------------------------------------------------ lying down (front first) and getting up (hind first)
LIE_DOWN_T = 2.2


def lie_down(t):
    """it kneels FRONT first, as a cow does (the body tips nose-down over folded wrists), then the hind end sinks,
    the crown tilts once to look round; it ends in `sit`'s pose"""
    p = {}
    k = f(tr((0, 0), (0.2, 0.02), (1.1, 1.0, smooth), (2.2, 1.0)), t)
    kh = f(tr((0, 0), (0.7, 0.02), (1.65, 1.0, smooth), (2.2, 1.0)), t)
    land = kick(t, 1.65, 0.16, 0.05)
    A.lie(p, k, kh=min(kh, 1.0))
    add(p, "body", rot=(0.8 * land, 0, 0))
    Q.head(p, -3 * land, 6 * window(t, 1.0, 1.7, 0.25), 0)
    Q.alive_upper(p, t, k=0.6, period=1.1)
    Q.trail(p, t, lambda u: 2.0 * kick(u, 1.65, 0.22, 0.05), delay=0.06, axis=0)
    p = A.settle(A.lift_tail(A.lift_head(p, 0.0)))
    w = smooth((t - 1.85) / 0.35)
    return C.blend(p, sit(0.0), w) if w > 0 else p


GET_UP_T = 2.0


def get_up(t):
    """from `sit`: a toss of the crown, the hind end up first (nose-down), then the front, a skip of the weight"""
    p = {}
    kh = f(tr((0, 1), (0.3, 1), (1.0, 0, smooth), (2.0, 0)), t)
    k = f(tr((0, 1), (0.75, 1), (1.5, 0, smooth), (2.0, 0)), t)
    toss = ring(t, 0.15, 3.0, 0.15)
    wob = ring(t, 1.5, 2.4, 0.22)
    A.lie(p, k, kh=kh)
    Q.head(p, 4 * bump(t, 0.9, 0.2), 0, 12 * toss)
    add(p, "body", rot=(0, 0, 1.4 * wob))
    Q.alive_upper(p, t, k=0.6, period=1.0)
    Q.trail(p, t, lambda u: -2.5 * ring(u, 1.5, 2.4, 0.26), delay=0.06)
    p = A.settle(A.lift_tail(A.lift_head(p, 0.0)))
    w = 1 - smooth(t / 0.3)
    return C.blend(sit(0.0), p, 1 - w) if w > 0 else p


# ------------------------------------------------------------------ the old ones, made fluid
def _upper(name, k=0.5, period=None, tail=None):
    fn = _O[name]
    L = A.ANIMS[name][1]
    per = period or (L / max(1, round(L / 1.3)))

    def g(t):
        p = fn(t)
        before = Q.head_low(p)
        Q.alive_upper(p, t, k=k, period=per, slow=L if A.ANIMS[name][2] else None)
        if tail: tail(p, t)
        A.lift_tail(p)                                  # a tail lying on the ground must not breathe into it
        return Q.keep_head(p, before)
    g.__doc__ = fn.__doc__
    return g


_HH = tr((0, 0), (0.25, 1, ease_out), (0.45, -1, ease_in), (0.6, -1), (1.0, 0, smooth))
horn_hook = _upper("horn_hook", 0.4, tail=lambda p, t: Q.trail(p, t, lambda u: -5.0 * f(_HH, u), delay=0.06))
hurt = _upper("hurt", 0.4, tail=lambda p, t: Q.trail(p, t, lambda u: -4.0 * math.exp(-u / 0.18) * smooth(u / 0.05), delay=0.05))
paw_scrape = _upper("paw_scrape", 0.5)
crown_display = _upper("crown_display", 0.5, tail=lambda p, t: Q.trail(p, t, lambda u: -3.0 * window(u, 0.6, 2.6, 0.3) * math.sin(2 * math.pi * (u - 0.6) / 2.0), delay=0.1))
rival_display = _upper("rival_display", 0.5)
horn_rub = _upper("horn_rub", 0.4)
head_shake = _upper("head_shake", 0.3, tail=lambda p, t: Q.trail(p, t, lambda u: 4.0 * window(u, 0.15, 1.1, 0.12) * math.sin(2 * math.pi * u / 0.32), delay=0.06))
frill_shove = _upper("frill_shove", 0.4)
eat, graze = _upper("eat", 0.4), _upper("graze", 0.4)
beg = _upper("beg", 0.6, period=1.1)
tame = _upper("tame", 0.6)
SIT_T = 7.0


def sit(t):
    """lying awake chewing the cud: the breath now divides the loop (three a loop; the old one breathed every 3.6 s
    and jumped at the seam), the crown turned to look round and back, the jaw working, the tail never still"""
    T = SIT_T; p = {}
    br = wave(t, T / 3)
    A.lie(p)
    add(p, "body", rot=(0.3 * br, 0, 0), pos=(0, 0.15 * (1 + br), 0))
    look = f(tr((0, 0), (2.0, 0), (2.7, 1, ease_out), (3.8, 1), (4.5, 0, smooth), (7.0, 0)), t)
    Q.head(p, 6 - 0.4 * wave(t, T / 3, -0.6) + 0.8 * wave(t, T / 2, 0.5), 20 * look + 1.2 * wave(t, T, 1.1), -4 * look)
    A.jaw(p, -2.5 * window(t, 4.6, 6.6, 0.3) * max(0.0, math.sin(2 * math.pi * (t - 4.6) / 0.6)))
    for i, b in enumerate(A.TAILS):
        add(p, b, rot=(0, 4 * look + (0.5 + 0.6 * i) * wave(t, T, -0.8 * i), 0))
    return A.settle(A.lift_tail(A.lift_head(p, 0.0)))
sleep = _upper("sleep", 0.4, period=3.0)
knocked_out = _upper("knocked_out", 0.3, period=4.0)
wake_sleep = _upper("wake_sleep", 0.5, tail=lambda p, t: Q.trail(p, t, lambda u: 3.0 * window(u, 0.7, 1.1, 0.1) * math.sin(2 * math.pi * u / 0.25), delay=0.06))
wake = _upper("wake", 0.5, tail=lambda p, t: Q.trail(p, t, lambda u: 3.5 * window(u, 1.1, 1.7, 0.12) * math.sin(2 * math.pi * u / 0.28), delay=0.06))


CALL_T = 2.6


def call(t):
    """calls the herd: the nose up, two long notes from a pumping throat; the shiver of each note is organic (three
    sines that never line up, under an envelope) and the breath is drawn between them"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (2.2, 1), (2.6, 0, smooth)), t)
    e1, e2 = window(t, 0.6, 1.2, 0.12), window(t, 1.5, 2.1, 0.12)
    note = e1 + e2
    inhale = bump(t, 1.35, 0.1)
    thr = tremor(t, (8.3, 12.7, 5.9), (1.0, 0.5, 0.35)) * note
    Q.alive(p, t, k=0.5 * (1 - 0.6 * k), period=1.3)
    add(p, "body", rot=(3 * k + 0.6 * inhale + 0.3 * thr, 0, 0), pos=(0, -A.STAND_DROP - 0.4 * k, 0))
    Q.head(p, 20 * k + 1.2 * thr - 2 * inhale, 3 * e2 - 2 * e1, 0, k=0.6)
    A.jaw(p, -9 * note - 1.2 * tremor(t, (10.1, 14.3, 6.7), (1.0, 0.5, 0.3), phase=1.4) * note + 1.5 * inhale)
    Q.trail(p, t, lambda u: -1.5 * f(tr((0, 0), (0.4, 1, ease_out), (2.2, 1), (2.6, 0, smooth)), u), delay=0.08, axis=0)
    return Q.stance(p)


def _quad(u): u = min(1.0, max(0.0, u)); return u * u


def _going_down(t):
    """the old fall (it staggers, the hind legs give, then the front, it sags onto its flank), its tracks eased so
    the legs fold over several frames instead of in one"""
    p = {}
    st = window(t, 0.0, 0.7, 0.2)
    kh = f(tr((0, 0), (0.25, 0), (0.85, 1, _quad), (1.8, 1)), t)
    k = f(tr((0, 0), (0.5, 0), (1.15, 1, _quad), (1.8, 1)), t)
    add(p, "body", rot=(0, -4 * st * math.sin(2 * math.pi * t / 0.7), -6 * st), pos=(-1.5 * st, 0, 0))
    A.lie(p, k, kh=max(kh, k))
    A.head(p, -10 * k, 10 * st, -8 * k)
    A.jaw(p, -10 * k)
    return A.settle(A.lift_tail(A.lift_head(p, 0.0)))


_DOWN = []


def death(t):
    if t <= 1.2:
        p = _going_down(t)
    else:
        if not _DOWN: _DOWN.append(_going_down(1.2))
        roll = f(tr((1.2, 0), (1.9, 1, _quad), (2.02, 0.95), (2.15, 1, smooth), (2.6, 1)), t)
        p = A.shift_to_ground(A.blend(_DOWN[0], A.ko_pose({}, 1.0), roll))
    fade = 1.0 - smooth((t - 1.5) / 1.0)
    for c, a in ((0.9, 0.8), (2.25, 1.0), (2.5, 0.5)):
        g = bump(t, c, 0.12) * a
        add(p, "body", rot=(1.0 * g, 0, 0)); A.jaw(p, -2.5 * g)
    tw = sum(a * bump(t, c, 0.05) for c, a in ((1.4, 1.0), (1.7, -0.6), (2.3, 0.3)))
    for i, b in enumerate(A.TAILS): add(p, b, rot=(0, 2.5 * (i + 1) * tw * fade, 0))
    return p


ANIMS = {
    "idle": (idle, IDLE_T, True, "Parado", "vigia o bando: olhadas com pausas, a coroa se mexe como orelha, troca o peso das patas da frente"),
    "walk": (walk, A.WALK[0], True, "Movimento", "passo ligeiro: o quadril rola, a coroa acena atrasada a cada pata da frente"),
    "run": (run, A.RUNP[0], True, "Movimento", "galope curto aos saltos, com o peso no lombo"),
    "charge": (charge, A.CHARGEP[0], True, "Só dele", "investida: cabeça baixa, chifre do nariz apontado, coroa deitada"),
    "attack": (attack, ATTACK_T, False, "Combate", "a chifrada em três tempos: ergue, avança (golpe em 0,4 s), engancha para cima"),
    "nose_jab": (nose_jab, NOSE_JAB_T, False, "Combate", "ASSINATURA: estocada curta do chifre do nariz (golpe em 0,3 s), só a frente avança"),
    "horn_hook": (horn_hook, 1.0, False, "Só dele", "o gancho de lado (com respiração e cauda)"),
    "guard": (guard, GUARD_T, True, "Duelo", "em guarda e exibindo: chifre no rival, coroa inclinada balançando, dois acenos"),
    "strafe_left": (strafe_left, STRAFE_T, True, "Duelo", "passo ligeiro de lado para a esquerda, coroa virada para o rival"),
    "strafe_right": (strafe_right, STRAFE_T, True, "Duelo", "passo ligeiro de lado para a direita, coroa virada para o rival"),
    "turn_left": (turn_left, TURN_T, True, "Movimento", "gira no lugar para a esquerda, a cabeça entra primeiro"),
    "turn_right": (turn_right, TURN_T, True, "Movimento", "gira no lugar para a direita"),
    "feint": (feint, FEINT_T, False, "Duelo", "carga falsa: dispara, a frente salta do chão, a coroa relampeja, recua"),
    "block": (block, BLOCK_T, False, "Duelo", "apara com o lado da coroa: os espinhos vibram, uma pata sai de lado"),
    "recoil": (recoil, RECOIL_T, False, "Duelo", "a estocada escorregou na coroa do outro: nariz para cima, pulinho para trás"),
    "submit": (submit, SUBMIT_T, False, "Duelo", "perdeu: deita a coroa sobre o pescoço (nariz para cima), vira e encolhe a cauda"),
    "lie_down": (lie_down, LIE_DOWN_T, False, "Descanso", "deita pela frente, como boi; termina como sit"),
    "get_up": (get_up, GET_UP_T, False, "Descanso", "levanta de sit: primeiro o quadril, depois a frente"),
    "idle_tired": (idle_tired, IDLE_TIRED_T, True, "Parado", "cansado: ofega rápido, boca aberta, coroa baixa"),
    "walk_tired": (walk_tired, WALK_TIRED_T, True, "Movimento", "andando cansado: 30 px por ciclo de 1,5 s, a coroa pesa"),
    "paw_scrape": (paw_scrape, 1.9, False, "Só dele", "raspa o chão (com respiração)"),
    "crown_display": (crown_display, 3.3, False, "Só dele", "balança a coroa (com respiração e cauda)"),
    "rival_display": (rival_display, 3.6, False, "Só dele", "exibição lado a lado (com respiração)"),
    "horn_rub": (horn_rub, 2.8, False, "Só dele", "esfrega o chifre (com respiração)"),
    "head_shake": (head_shake, 1.3, False, "Só dele", "sacode a coroa, a cauda acompanha"),
    "call": (call, CALL_T, False, "Só dele", "chama o bando: duas notas com tremor orgânico e fôlego entre elas"),
    "frill_shove": (frill_shove, 1.9, False, "Só dele", "filhotes empurram gola contra gola (com respiração)"),
    "hurt": (hurt, 0.55, False, "Combate", "ao levar dano, a cauda chicoteia"),
    "death": (death, 2.6, False, "Combate", "a queda antiga e os últimos fôlegos"),
    "eat": (eat, 2.6, False, "Comer", "come (com respiração)"),
    "graze": (graze, 3.2, False, "Comer", "pasta (com respiração)"),
    "sit": (sit, SIT_T, True, "Descanso", "deitado ruminando: respira em ritmo que fecha o laço, vira a coroa para olhar"),
    "sleep": (sleep, 9.0, True, "Descanso", "dorme, respirando fundo"),
    "wake_sleep": (wake_sleep, 2.2, False, "Descanso", "acorda, a cauda acompanha a sacudida"),
    "knocked_out": (knocked_out, 4.0, True, "Descanso", "nocauteado, respirando"),
    "wake": (wake, 3.2, False, "Descanso", "acorda do nocaute, a cauda acompanha"),
    "beg": (beg, 2.2, True, "Domado", "pede comida (com respiração)"),
    "tame": (tame, 2.4, False, "Domado", "aceita o dono (com respiração)"),
}
