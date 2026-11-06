"""Protoceratops: the fluid set and the fighting set (06/11/2026), from its own body and its own study.

The study (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md): the "Fighting Dinosaurs" of the Djadokhta (Mongolia,
1971), a Velociraptor and a Protoceratops buried in the act: the raptor's sickle claw at the throat, its right arm
caught in the Protoceratops' beak, crushed. It has no horns: a parrot's beak that bites and holds, a bony frill to
shove with, a tall tail; it is 2 m and the weight of a big sheep, low on short straight legs.

What its body makes of the T. rex study's principles (docs/estudos/08_ANIMACAO_RAXIORES.md):
  * small and quick: the shortest loops of the three (the guard 2 s, the strafe 1 s, the turn 1.2 s), quick short
    steps, a jittery weight; its head is light and works on its own;
  * the weapon is the beak, so its guard is low with the beak half open and clacking, the frill up as a shield, the
    tall tail raised and flagging from side to side (the sail shown, as in `sail_sway`);
  * it is stubborn: it does not give ground, it scuttles sideways in a crouch, its feint is a snap of the beak at
    the air with a hop of the forefeet, it blocks by ducking the frill and clamping the beak, and its signature
    `frill_shove` is one explosive heave of the frill from the hind legs;
  * it gives in by flattening to the ground, the head turned away and the sail laid down.
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
import protoanims as A  # noqa: E402
from anim2 import add, smooth, ease_in, ease_out, back_out  # noqa: E402

tr, f, wave, window, bump, ring, kick, tremor = C.tr, C.f, C.wave, C.window, C.bump, C.ring, C.kick, C.tremor


def shield(p, k=1.0):
    """the frill up as a shield: the nose tucked down so the frill stands, the beak just off the ground"""
    add(p, "skull", rot=(-14 * k, 0, 0)); add(p, "neck", rot=(-4 * k, 0, 0))


Q = C.Quad(A, shield, hind=(24, 16, 22), fore=(22, 34), head_k=0.6, scap=(0.3, 0.06))
SIDES = A.SIDES
Q.adopt()                                           # the originals plant their feet through the stable IK too
_O = {n: v[0] for n, v in A.ANIMS.items()}


def _ground(p):
    """the lying poses of this rig: the head and the tail off the ground, nothing under it"""
    return A.lift_tail(A.lift_head(p, 0.0))


# ------------------------------------------------------------------ gaits
def walk(t):
    """the quick walk: the hips roll on short legs, the head bobbing on its own a beat late, the tall tail swaying"""
    Tc, stride, duty, lift = A.WALK[:4]               # the game's cycle and stride; a shorter stance (0.56), a gentler swing
    return Q.gait(t, Tc, stride, 0.56, lift, A.LATERAL, bob=0.6, hd=-2, roll=3.4, yaw=2.4, nod=1.3, head_keep=0.5, head_lag=0.13,
                  neck_roll=0.6, tail_yaw=3.4, tail_lag=0.1, tail_pitch=0.9)


def run(t):
    """the trot: diagonal pairs, low and level, the head out in front and the sail swinging"""
    Tc, stride, duty, lift, bob = A.TROTP
    duty = 0.36                                          # was 0.42: a longer swing, the short legs fold without snapping
    return Q.gait(t, Tc, stride, duty, lift, A.TROT, flift=lift * 0.85, bob=bob, drop=1.6, lean=-1.5, hd=-4, roll=1.8,
                  yaw=1.4, nod=0.8, head_keep=0.7, head_lag=0.1, neck_roll=0.6, tail_yaw=2.4, tail_lag=0.08, tail_pitch=1.0)


WALK_TIRED_T = 1.3


def walk_tired(t):
    """spent: 22 px a cycle of 1.3 s, the beak open and panting, the head and the sail low"""
    return Q.gait(t, WALK_TIRED_T, 22, 0.7, 3.6, A.LATERAL, bob=0.9, drop=0.5, lean=-1.0, hd=-8, roll=4.0, yaw=2.2,
                  nod=1.6, head_keep=0.4, head_lag=0.2, neck_roll=0.5, tail_yaw=2.2, tail_lag=0.11, tail_pitch=0.7,
                  tail_base=3.0, jaw=-8.0, pant=6.0)


# ------------------------------------------------------------------ the idle
IDLE_T = 6.0
LOOK = tr((0, (0, 0)), (0.8, (0, 0)), (1.2, (2, 22), ease_out), (2.3, (1, 20)), (2.65, (0, -18), ease_out), (3.6, (-1, -16)),
          (4.3, (-10, -2), ease_out), (5.3, (-9, 0)), (6.0, (0, 0), ease_in))


def idle(t):
    """a small animal never quite still: quick looks with holds, a sniff at the ground, a quick breath (three a
    loop), the weight jittering between the forefeet and the tall tail swaying in a slow S"""
    T = IDLE_T; p = {}
    Q.alive(p, t, k=1.0, period=T / 3)
    lp, ly = LOOK(t)
    sniff = window(t, 4.4, 5.2, 0.15) * max(0.0, math.sin(2 * math.pi * t / 0.3))
    shift = wave(t, T, 0.8) + 0.35 * wave(t, T / 3, -0.6)
    add(p, "body", rot=(-1.2 * window(t, 4.2, 5.4, 0.4), 0.1 * ly, 1.6 * shift), pos=(0, -A.STAND_DROP, 0))
    Q.head(p, lp + 1.5 * sniff + 0.7 * wave(t, T / 4, 0.3), ly + 1.2 * wave(t, T / 5, 1.1), -0.2 * ly)
    A.jaw(p, -1.2 * sniff)
    for i, b in enumerate(A.TAILS):
        add(p, b, rot=(0.4 * i * wave(t, T / 3, -0.5 * i), (1.2 + 1.5 * i) * wave(t, T, -0.9 * i) + 0.6 * i * wave(t, T / 2, 0.2 - 0.7 * i), 0))
    return Q.stance(p, fore=(-0.4 * max(0.0, shift), -0.4 * max(0.0, -shift)), clear=0.3)


IDLE_TIRED_T = 2.0


def idle_tired(t):
    """spent: fast panting with the beak wide (five a loop), the head hung low, the sail drooping"""
    T = IDLE_TIRED_T; p = {}
    pant = wave(t, T / 5)
    add(p, "body", rot=(-1.0 + 1.5 * pant, 0, 1.2 * wave(t, T, 0.4)), pos=(0, -A.STAND_DROP - 0.6 + 0.4 * pant, 0))
    Q.head(p, -14 - 1.6 * wave(t, T / 5, -0.7), 4.0 * wave(t, T, 1.0), 0)
    A.jaw(p, -12 - 5 * max(0.0, wave(t, T / 5, -0.5)))
    for i, b in enumerate(A.TAILS):
        add(p, b, rot=(3.0 + 0.5 * i * pant, (0.8 + 0.8 * i) * wave(t, T, -0.8 * i), 0))
    return Q.stance(p, fore=(-0.8, -0.8), fdx=(0.5, -0.5), clear=0.3)


# ------------------------------------------------------------------ the fight
GUARD_T = 2.0


def guard(t):
    """crouched low and stubborn: the frill up as a shield, the beak half open and clacking twice a loop, a hiss
    shivering in the jaw, the weight jittering on short legs, the tall tail raised and flagged from side to side"""
    T = GUARD_T; p = {}
    jit = wave(t, T / 4, 0.4)
    hiss = C.loop_tremor(t, T, (17, 25, 11), (0.8, 0.45, 0.3))
    clack = sum(bump(t, c, 0.05) for c in (0.62, 1.38))
    Q.alive(p, t, k=0.7, period=T / 4)
    add(p, "body", rot=(-1.5 + 0.4 * jit, 1.4 * wave(t, T, 0.2), 0.8 * jit), pos=(0, -A.STAND_DROP - 1.6 + 0.3 * jit, -0.8))
    shield(p, 1.0)
    Q.head(p, -2 + 2.5 * clack, 3.0 * wave(t, T, 1.0), 0)
    A.jaw(p, -9 + 8 * clack - 1.0 * hiss)
    for i, b in enumerate(A.TAILS):
        add(p, b, rot=(-3.0 * (0.6 + 0.2 * i), (2.5 + 2.5 * i) * wave(t, T, -0.7 * (i + 1)), 0))
    return Q.stance(p, fore=(-1.0, -1.0), hind=(0.8, 0.8), fdx=(0.5, -0.5), clear=0.3)


STRAFE_T = 1.0


def _sail(side):
    d = 1.0 if side == "left" else -1.0

    def extra(p, t, w):
        A.jaw(p, -6 - 2 * max(0.0, math.sin(2 * w)))
        for i, b in enumerate(A.TAILS): add(p, b, rot=(-2.5 * (0.5 + 0.2 * i), 0, 0))     # the sail up as it scuttles
    return extra


def strafe_left(t): return Q.strafe(t, "left", STRAFE_T, step_dx=2.0, lift=2.8, lean=2.6, guard=0.8, look=5.0, tail_yaw=4.0, drop=1.6, extra=_sail("left"))
def strafe_right(t): return Q.strafe(t, "right", STRAFE_T, step_dx=2.0, lift=2.8, lean=2.6, guard=0.8, look=5.0, tail_yaw=4.0, drop=1.6, extra=_sail("right"))


TURN_T = 1.2


def turn_left(t): return Q.turn(t, "left", TURN_T, fore_dx=2.2, hind_dx=1.8, lift=2.8, lead_yaw=12.0, body_yaw=3.5, roll=1.6, bob=0.4, tail_yaw=4.5)
def turn_right(t): return Q.turn(t, "right", TURN_T, fore_dx=2.2, hind_dx=1.8, lift=2.8, lead_yaw=12.0, body_yaw=3.5, roll=1.6, bob=0.4, tail_yaw=4.5)


FEINT_T = 1.0
FN_GO = tr((0, 0), (0.15, -0.4, ease_out), (0.32, 1, ease_in), (0.4, 1.1), (0.55, 0.6), (1.0, 0, back_out))
FN_HOP = tr((0, 0), (0.22, 0), (0.32, 1, ease_out), (0.44, 0, ease_in), (1.0, 0))


def feint(t):
    """a snap at the air: it rocks back, darts the head out with a hop of the forefeet, the beak snapping shut on
    nothing a hand short of the rival, the frill flaring, and back into its crouch"""
    p = {}
    go, hop = f(FN_GO, t), f(FN_HOP, t)
    Q.alive(p, t, k=0.6, period=0.5)
    add(p, "body", rot=(2.0 * hop - 1.5 * max(0.0, go), 0, 0), pos=(0, -A.STAND_DROP - 1.0 + 0.4 * hop, -2.2 * go))
    shield(p, 0.6 - 0.4 * max(0.0, go))
    Q.head(p, -6 * max(0.0, go) + 6 * max(0.0, -go), 0, 0)
    A.jaw(p, f(tr((0, -4), (0.2, -26, ease_out), (0.36, -28), (0.4, -1, ease_in), (0.6, -3), (1.0, -6)), t))
    add(p, "skull", rot=(4 * bump(t, 0.42, 0.05), 0, 0))
    Q.trail(p, t, lambda u: -3.0 * f(FN_HOP, u) + 1.5 * f(FN_GO, u), delay=0.05, axis=0, gain=Q.gains(0.5, 0.4))
    Q.counter_legs(p); A.lift_head(p)
    for s in SIDES: Q.foot(p, s, "h", 0, 1.0 * max(0.0, go))
    for s in SIDES: Q.foot(p, s, "f", 2.5 * hop, -1.6 * max(0.0, go), pitch=-16 * hop, clear=-0.05 if hop < 0.05 else 0.3)
    return p


BLOCK_T = 0.7


def block(t):
    """the blow taken on the frill: it ducks the frill into it and clamps the beak, and being small it is knocked
    sideways off its feet a little, a forefoot skipping out to catch it, the sail flicking up"""
    p = {}
    duck = f(tr((0, 0), (0.06, 1, ease_out), (0.35, 0.6), (0.7, 0, ease_out)), t)
    hit = kick(t, 0.1, 0.16, 0.07)                      # the shove builds over a frame or two: the legs follow it
    Q.alive(p, t, k=0.5, period=0.7)
    add(p, "body", rot=(0.8 * hit, 4.0 * hit, 6.0 * hit), pos=(0, -A.STAND_DROP - 0.8 * duck, 1.0 * hit))
    shield(p, 0.6 + 0.6 * duck)
    Q.head(p, 4 * hit, 10 * hit, -10 * hit)
    A.jaw(p, -1.0 + 1.0 * duck)
    Q.trail(p, t, lambda u: -5.0 * kick(u, 0.08, 0.2, 0.03), delay=0.04, axis=0, gain=Q.gains(0.4, 0.4))
    Q.counter_legs(p); A.lift_head(p)
    Q.step(p, "r", "f", (t - 0.08) / 0.3, dx1=-1.6, lift=2.2)
    Q.foot(p, "l", "f", 0, 0.4 * hit)
    Q.step(p, "r", "h", (t - 0.22) / 0.34, dx1=-1.0, lift=2.0)
    Q.foot(p, "l", "h", 0, 0.4 * hit)
    return p


RECOIL_T = 0.8


def recoil(t):
    """its bite slid off the other's frill: the head jerked back with the beak snapping shut, and a quick scuttle of
    both forefeet back, then a shake of the head"""
    p = {}
    hit = kick(t, 0.04, 0.16, 0.03)
    sh = ring(t, 0.32, 4.4, 0.14)
    Q.alive(p, t, k=0.5, period=0.8)
    add(p, "body", rot=(2.0 * hit, 2.0 * hit, 0), pos=(0, -A.STAND_DROP - 0.6, 1.4 * hit))
    Q.head(p, 12 * hit, 6 * hit + 4 * sh, 16 * sh)
    A.jaw(p, f(tr((0, -20), (0.06, -2, ease_in), (0.8, -3)), t))
    Q.trail(p, t, lambda u: 3.0 * ring(u, 0.32, 4.4, 0.18), delay=0.05)
    Q.counter_legs(p); A.lift_head(p)
    Q.step(p, "l", "f", (t - 0.06) / 0.28, dz1=2.0, lift=2.5)
    Q.step(p, "r", "f", (t - 0.22) / 0.28, dz1=2.0, lift=2.5)
    for s in SIDES: Q.foot(p, s, "h", 0, 0.5 * hit)
    return p


SUBMIT_T = 2.0


def submit(t):
    """beaten: it flattens to the ground, the head turned away and low, the frill turned edge-on, the sail laid down
    and to the side, quick shallow breaths"""
    p = {}
    k = f(tr((0, 0), (0.5, 1, ease_out), (2.0, 1)), t)
    turn = f(tr((0, 0), (0.3, 0), (1.0, 1, ease_out), (2.0, 1)), t)
    Q.alive(p, t, k=0.8, period=0.4)
    add(p, "body", rot=(-1.0 * k, 6 * turn, 2 * turn), pos=(0, -A.STAND_DROP - 3.0 * k, 0.5 * k))
    Q.head(p, -8 * k, 26 * turn, 14 * turn)
    for i, b in enumerate(A.TAILS): add(p, b, rot=(5.0 * k * (0.5 + 0.2 * i), -6.0 * turn * (0.4 + 0.3 * i), 0))
    return Q.stance(p, fore=(0.8 * k, 0.8 * k), hind=(-0.5 * k, -0.5 * k), clear=0.3)


ATTACK_T = 0.8
AT_BACK = tr((0, 0), (0.18, 1, ease_out), (0.26, 0.7), (0.34, 0, ease_in))
AT_HIT = tr((0, 0), (0.22, 0), (0.38, 1, ease_in), (0.48, 1.05), (0.8, 0, back_out))
AT_BODY = tr((0, 0), (0.2, 0), (0.4, 1, smooth), (0.8, 0, smooth))               # the body under the snap, softer
AT_TUG_BODY = tr((0, 0), (0.4, 0), (0.55, 1, smooth), (0.8, 0, smooth))
AT_TUG = tr((0, 0), (0.4, 0), (0.48, 1, ease_out), (0.6, 0, ease_in), (0.8, 0))


def attack(t):
    """the beak bite in three beats (the hit at 0.38 s, as before): the head drawn back with the beak gaping, the
    snap forward and down, a short wrench to tear, and the settle past rest and back"""
    p = {}
    bk, ht, tg = f(AT_BACK, t), f(AT_HIT, t), f(AT_TUG, t)
    Q.alive(p, t, k=0.5, period=0.8)
    hb, tb = f(AT_BODY, t), f(AT_TUG_BODY, t)
    add(p, "body", rot=(2.0 * bk - 1.5 * hb, 1.5 * tb, -2.0 * tb), pos=(0, -A.STAND_DROP - 0.4 * bk - 0.4 * hb, 1.2 * bk - 2.4 * hb))
    Q.head(p, 10 * bk - 14 * ht + 5 * tg, -5 * tg, 9 * tg)
    A.jaw(p, f(tr((0, -2), (0.18, -28, ease_out), (0.34, -30), (0.39, -1, ease_in), (0.6, -2), (0.8, 0)), t))
    Q.trail(p, t, lambda u: 3.0 * f(AT_TUG, u), delay=0.05)
    Q.trail(p, t, lambda u: -2.5 * f(AT_BACK, u) + 2.0 * f(AT_HIT, u), delay=0.05, axis=0, gain=Q.gains(0.5, 0.3))
    return Q.stance(p)


FRILL_SHOVE_T = 1.2
FS_LOAD = tr((0, 0), (0.28, 1, ease_out), (0.36, 0.8), (0.44, 0, ease_in), (1.2, 0))
FS_DRIVE = tr((0, 0), (0.3, 0), (0.42, 1, ease_in), (0.6, 1.08), (0.75, 0.9), (1.2, 0, back_out))


def frill_shove(t):
    """THE SIGNATURE (the hit at 0.42 s): one heave of the frill. It sinks onto its hind legs with the nose tucked so
    the frill stands up, then drives the whole body forward from the hind feet, the frill lifting into the rival as it
    connects (an upward heave, not a butt), holds the push with the forefeet braced, and lets go. Stubborn, low,
    from the ground up; the Triceratops pushes with its horns locked, this one shoves with the shield"""
    p = {}
    ld, dv = f(FS_LOAD, t), f(FS_DRIVE, t)
    heave = kick(t, 0.42, 0.18, 0.06)
    eff = tremor(t, (13.1, 17.9, 9.3), (0.8, 0.4, 0.3)) * window(t, 0.45, 0.8, 0.1)
    Q.alive(p, t, k=0.5, period=1.2)
    add(p, "body", rot=(1.5 * ld - 1.5 * dv + 2.5 * heave + 0.3 * eff, 0, 0),
        pos=(0, -A.STAND_DROP - 1.0 * ld - 0.6 * dv, 1.6 * ld - 3.0 * dv))
    shield(p, 0.5 + 0.7 * ld + 0.5 * dv)
    Q.head(p, -3 * ld + 7 * heave + 0.6 * eff, 0, 0)
    A.jaw(p, -2.0 * dv)
    Q.trail(p, t, lambda u: 3.0 * f(FS_LOAD, u) - 3.5 * f(FS_DRIVE, u), delay=0.05, axis=0, gain=Q.gains(0.5, 0.4))
    return Q.stance(p, fore=(-1.8 * dv, -1.8 * dv), hind=(1.0 * ld + 1.8 * dv, 1.0 * ld + 1.8 * dv))


# ------------------------------------------------------------------ lying down and getting up
LIE_DOWN_T = 1.8


def lie_down(t):
    """the hind legs fold first (the chest still up, nose high), then the chest goes down onto the forearms with a
    little bounce, the head looks round; it ends in `sit`'s pose"""
    p = {}
    k = f(tr((0, 0), (0.2, 0.02), (1.2, 1.03, ease_in), (1.38, 1.0, ease_out), (1.8, 1.0)), t)
    up = window(t, 0.25, 1.0, 0.3)                    # the front lags: the body pitched nose-up
    land = kick(t, 1.2, 0.14, 0.04)
    A.lie(p, min(k, 1.0), pitch=7 * up)
    add(p, "body", rot=(-0.6 * land, 0, 0))
    Q.head(p, 4 * up - 3 * land, 8 * window(t, 1.0, 1.6, 0.2), 0)
    Q.alive_upper(p, t, k=0.6, period=0.9)
    Q.trail(p, t, lambda u: 2.5 * kick(u, 1.2, 0.2, 0.04), delay=0.05, axis=0)
    p = _ground(p)
    w = smooth((t - 1.45) / 0.35)
    return C.blend(p, sit(0.0), w) if w > 0 else p


GET_UP_T = 1.6


def get_up(t):
    """from `sit`: the head up, the chest pushed up on the forelegs, then the hind end, a shake of the frill"""
    p = {}
    k = f(tr((0, 1), (0.25, 1), (1.05, 0, ease_out), (1.6, 0)), t)
    up = window(t, 0.25, 0.85, 0.25)
    sh = ring(t, 1.1, 4.0, 0.14)
    A.lie(p, k, pitch=8 * up)
    Q.head(p, 5 * bump(t, 0.3, 0.15), 0, 14 * sh)
    Q.alive_upper(p, t, k=0.6, period=0.8)
    Q.trail(p, t, lambda u: 3.0 * ring(u, 1.1, 4.0, 0.18), delay=0.05)
    p = _ground(p)
    w = 1 - smooth(t / 0.25)
    return C.blend(sit(0.0), p, 1 - w) if w > 0 else p


# ------------------------------------------------------------------ the old ones, made fluid
def _upper(name, k=0.5, period=None, tail=None):
    fn = _O[name]
    L = A.ANIMS[name][1]
    per = period or (L / max(1, round(L / 1.0)))

    def g(t):
        p = fn(t)
        before = Q.head_low(p)
        Q.alive_upper(p, t, k=k, period=per, slow=L if A.ANIMS[name][2] else None)
        if tail: tail(p, t)
        A.lift_tail(p)                                  # a tail lying on the ground must not breathe into it
        return Q.keep_head(p, before)
    g.__doc__ = fn.__doc__
    return g


bite_hold = _upper("bite_hold", 0.4, tail=lambda p, t: Q.trail(p, t, lambda u: -4.0 * window(u, 0.6, 1.7, 0.12) * math.sin(2 * math.pi * (u - 0.6) / 0.38), delay=0.05))
shove = _upper("shove", 0.4, tail=lambda p, t: Q.trail(p, t, lambda u: -2.5 * sum(window(u, c, c + 0.22, 0.1) for c in (0.45, 0.95)), delay=0.05, axis=0))
frill_show = _upper("frill_show", 0.5)
sail_sway = _upper("sail_sway", 0.4)
hurt = _upper("hurt", 0.4, tail=lambda p, t: Q.trail(p, t, lambda u: 5.0 * math.exp(-u / 0.15) * smooth(u / 0.04), delay=0.04))
eat, graze, dig = _upper("eat", 0.4), _upper("graze", 0.4), _upper("dig", 0.3)
sand_shake, scrape_rest = _upper("sand_shake", 0.3), _upper("scrape_rest", 0.4)
beg = _upper("beg", 0.6, period=1.0)
tame = _upper("tame", 0.6)


def _rake(p, s, u, period=0.5):
    """the dig stroke of protoanims.rake, made continuous: it starts and ends where the standing foot is (the old one
    began 2 px back and ended 2 px back, and dropped its heel and its toe clearance in one frame)"""
    ph = u / period
    if ph < 0.38:
        e = smooth(ph / 0.38); dz = -9 * e; dy = 3.5 * math.sin(math.pi * e); meta = -10 * e; toe = -20 * math.sin(math.pi * e)
    elif ph < 0.75:
        e = smooth((ph - 0.38) / 0.37); dz = -9 + 17 * e; dy = 0.0; meta = -10 + 20 * e; toe = 0.0
    else:
        e = smooth((ph - 0.75) / 0.25); dz = 8 - 8 * e; dy = 1.5 * math.sin(math.pi * e); meta = 10 - 10 * e; toe = -15 * math.sin(math.pi * e)
    A.plant_h(p, s, dy, dz, meta, toe, clear=-0.05 + 0.3 * min(1.0, dy))


A.rake = _rake                                      # dig and scrape_rest rake through it


SIT_T = 6.0


def sit(t):
    """lying awake, chest down, the head up and watching: the breath now divides the loop (three a loop; the old one
    breathed every 3.2 s and jumped at the seam), a slow look to one side and back, the sail swaying"""
    T = SIT_T; p = {}
    br = wave(t, T / 3)
    A.lie(p)
    add(p, "body", rot=(0.4 * br, 0, 0), pos=(0, 0.12 * (1 + br), 0))
    look = f(tr((0, 0), (2.0, 0), (2.6, 1, ease_out), (3.6, 1), (4.3, 0, smooth), (6.0, 0)), t)
    Q.head(p, 4 - 0.5 * wave(t, T / 3, -0.6) + 0.8 * wave(t, T / 2, 0.4), 22 * look + 1.5 * wave(t, T, 0.9), 0)
    for i, b in enumerate(A.TAILS):
        add(p, b, rot=(0, 4 * look + (0.6 + 0.6 * i) * wave(t, T, -0.8 * i), 0))
    return _ground(p)

sleep = _upper("sleep", 0.4, period=3.0)
huddle = _upper("huddle", 0.4, period=3.0)
knocked_out = _upper("knocked_out", 0.3, period=3.4)
wake_sleep = _upper("wake_sleep", 0.5)
wake = _upper("wake", 0.5, tail=lambda p, t: Q.trail(p, t, lambda u: 3.5 * window(u, 1.1, 1.8, 0.12) * math.sin(2 * math.pi * u / 0.24), delay=0.05))


def freeze(t):
    """a predator near: it stops dead and holds, but a frozen animal still breathes: fast and shallow, the throat
    fluttering, one twitch of the head; then it lets go"""
    p = _O["freeze"](t)
    k = f(tr((0, 0), (0.12, 1, ease_out), (1.9, 1), (2.4, 0, smooth)), t)
    flutter = 0.35 * k * tremor(t, (6.1, 8.9, 4.3), (1.0, 0.5, 0.3))
    add(p, "neck", rot=(0.25 * k * wave(t, 0.4) + 0.2 * flutter, 0, 0))
    A.jaw(p, -0.4 * k * max(0.0, wave(t, 0.4, -0.5)))
    for i, b in enumerate(A.TAILS): add(p, b, rot=(0.15 * (1 + i) * k * wave(t, 0.4, -0.4 * i), 0, 0))
    Q.alive_upper(p, t, k=1.0 - 0.8 * k, period=1.2)
    return p


def _quad(u): u = min(1.0, max(0.0, u)); return u * u


def _going_down(t):
    """the old fall (it staggers, the forelegs give, it goes down on its chest), eased so the legs fold over several
    frames instead of in one"""
    p = {}
    st = window(t, 0.0, 0.5, 0.15)
    down = f(tr((0, 0), (0.3, 0), (0.95, 1, _quad), (2.4, 1)), t)
    add(p, "body", rot=(-14 * math.sin(math.pi * down), 4 * st * math.sin(2 * math.pi * t / 0.5), 6 * st), pos=(0, 0, 1.5 * st))
    A.lie(p, down)
    A.head(p, 10 * st - 14 * down, -10 * st)
    A.jaw(p, -10 * st)
    return _ground(p)


_DOWN = []


def death(t):
    if t <= 1.0:
        p = _going_down(t)
    else:
        if not _DOWN: _DOWN.append(_going_down(1.0))
        roll = f(tr((1.0, 0), (1.6, 1, _quad), (1.75, 0.96), (1.9, 1, smooth), (2.4, 1)), t)
        p = A.shift_to_ground(A.blend(_DOWN[0], A.ko_pose({}, 1.0), roll))
    fade = 1.0 - smooth((t - 1.3) / 1.0)
    for c, a in ((0.7, 0.8), (1.95, 1.0), (2.2, 0.5)):
        g = bump(t, c, 0.12) * a
        add(p, "body", rot=(1.2 * g, 0, 0)); A.jaw(p, -3 * g)
    tw = sum(a * bump(t, c, 0.05) for c, a in ((1.2, 1.0), (1.5, -0.6), (2.0, 0.3)))
    for i, b in enumerate(A.TAILS): add(p, b, rot=(0, 3.0 * (i + 1) * tw * fade, 0))
    return p


ANIMS = {
    "idle": (idle, IDLE_T, True, "Parado", "nunca parado: olhadas com pausas, fareja o chão, o peso troca de pata, a vela balança"),
    "walk": (walk, A.WALK[0], True, "Movimento", "passo curto e ligeiro, a cabeça acena atrasada, a vela balança"),
    "run": (run, A.TROTP[0], True, "Movimento", "trote em diagonal, baixo, a vela atrás"),
    "attack": (attack, ATTACK_T, False, "Combate", "a bicada em três tempos: puxa com o bico aberto, bica (golpe em 0,38 s), torce, assenta"),
    "frill_shove": (frill_shove, FRILL_SHOVE_T, False, "Combate", "ASSINATURA: um empurrão de crista das patas de trás, a crista sobe no rival (golpe em 0,42 s)"),
    "bite_hold": (bite_hold, 2.2, False, "Só dele", "morde e não solta (com respiração e a cauda nos puxões)"),
    "shove": (shove, 1.8, False, "Só dele", "dois empurrões (com respiração e cauda)"),
    "guard": (guard, GUARD_T, True, "Duelo", "em guarda agachado: crista de escudo, bico entreaberto batendo, vela alta balançando"),
    "strafe_left": (strafe_left, STRAFE_T, True, "Duelo", "anda agachado de lado para a esquerda, bico aberto, vela alta"),
    "strafe_right": (strafe_right, STRAFE_T, True, "Duelo", "anda agachado de lado para a direita, bico aberto, vela alta"),
    "turn_left": (turn_left, TURN_T, True, "Movimento", "gira no lugar para a esquerda, passinhos rápidos, a vela abre para fora"),
    "turn_right": (turn_right, TURN_T, True, "Movimento", "gira no lugar para a direita"),
    "feint": (feint, FEINT_T, False, "Duelo", "bica o ar: pulinho das patas da frente, o bico fecha no vazio"),
    "block": (block, BLOCK_T, False, "Duelo", "apara com a crista, bico travado; leve, é jogado de lado e corrige com as patas"),
    "recoil": (recoil, RECOIL_T, False, "Duelo", "a bicada escorregou: a cabeça volta, o bico fecha, recua as patas da frente"),
    "submit": (submit, SUBMIT_T, False, "Duelo", "perdeu: rente ao chão, cabeça virada, vela deitada"),
    "lie_down": (lie_down, LIE_DOWN_T, False, "Descanso", "deita: as patas de trás dobram primeiro, depois o peito; termina como sit"),
    "get_up": (get_up, GET_UP_T, False, "Descanso", "levanta de sit: o peito, depois o quadril, sacode a crista"),
    "idle_tired": (idle_tired, IDLE_TIRED_T, True, "Parado", "cansado: ofega com o bico aberto, vela caída"),
    "walk_tired": (walk_tired, WALK_TIRED_T, True, "Movimento", "andando cansado: 22 px por ciclo de 1,3 s, ofegando"),
    "frill_show": (frill_show, 2.6, False, "Só dele", "mostra a crista (com respiração)"),
    "sail_sway": (sail_sway, 2.4, False, "Só dele", "balança a vela (com respiração)"),
    "freeze": (freeze, 2.4, False, "Só dele", "predador perto: congela, mas respira curto e rápido"),
    "hurt": (hurt, 0.5, False, "Combate", "ao levar dano, a cauda chicoteia"),
    "death": (death, 2.4, False, "Combate", "a queda antiga e os últimos fôlegos"),
    "eat": (eat, 2.6, False, "Comer", "come (com respiração)"),
    "graze": (graze, 3.2, False, "Comer", "pasta (com respiração)"),
    "dig": (dig, 2.6, False, "Só dele", "cava (com respiração)"),
    "sand_shake": (sand_shake, 1.6, False, "Só dele", "sacode a areia (com respiração)"),
    "scrape_rest": (scrape_rest, 3.6, False, "Só dele", "cava a cova e deita (com respiração)"),
    "sit": (sit, SIT_T, True, "Descanso", "deitado acordado: respira em ritmo que fecha o laço, olha de lado"),
    "sleep": (sleep, 9.0, True, "Descanso", "dorme, respirando fundo"),
    "huddle": (huddle, 6.0, True, "Só dele", "o filhote dorme enrolado, respirando"),
    "wake_sleep": (wake_sleep, 2.0, False, "Descanso", "acorda (com respiração)"),
    "knocked_out": (knocked_out, 3.4, True, "Descanso", "nocauteado, respirando"),
    "wake": (wake, 3.0, False, "Descanso", "acorda do nocaute, a cauda acompanha"),
    "beg": (beg, 2.0, True, "Domado", "pede comida (com respiração)"),
    "tame": (tame, 2.4, False, "Domado", "aceita o dono (com respiração)"),
}
