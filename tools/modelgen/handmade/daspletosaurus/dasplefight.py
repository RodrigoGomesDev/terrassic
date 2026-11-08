"""Daspletosaurus: the duel's committed moves at the fixed lengths the generic Java expects (DuelStyle: LUNGE 36 ticks
with the hit at 10, PARRY 30 ticks with the counter at 12, STAGGER 32 ticks), and its signature blow.

Its own, from the study (docs/estudos/13, "No jogo" 1): the most patient duel of the tyrannosaurids. It blocks a lot
with the heavy skull and hardly dodges; the T. rex shoves, this one BITES THE FACE: the bitten skulls of TMP 85.62.1
(Tanke & Currie 1998) and the face bites of Hone & Tanke (2015).
  * LUNGE = a heavy bite at the rival's head: it sinks on the haunches, drives forward one long step and the deep
    skull comes down from above, the jaws shut at 0.50 s, a short wrench, it backs out;
  * PARRY = the blow taken on the side of the skull (0 to 0.25 s), the head turned under the rival's and, at 0.60 s,
    the FACE BITE from below and the side, a twist, let go;
  * STAGGER = heavy: a lurch aside on stiff legs, one big step to catch the weight, the head shaken slowly, back in
    guard by 1.4 s;
  * FACE_BITE (its signature blow, DuelStyle special, hit at 0.55 s, 28 ticks): the head rises over the rival's and
    bites down across its snout, holds, twists.
All start and end on the guard's stance (daspleanims.guard without its loops).
"""
import math

import daspleanims as A
from anim2 import add, smooth, ease_in, ease_out, back_out
from theropod import window, SIDES

T = A.T
tr = A.tr
arms, trail, alive, alive_upper, tremor, bump, decay, steps = (A.arms, A.trail, A.alive, A.alive_upper, A.tremor,
                                                                A.bump, A.decay, A.steps)

LUNGE_T = 1.8
PARRY_T = 1.5
STAGGER_T = 1.6
FACE_BITE_T = 1.4
GUARD_DZ = {"l": 4.0, "r": -5.0}


def jolt(t, at, tau, rise=0.025):
    return math.exp(-max(0.0, t - at) / tau) * smooth((t - at + rise) / rise)


def stance(p):
    add(p, "body", rot=(-3, 0, 0), pos=(0, -2.6, 0))
    T.neck(p, (-9, 0, 0)); add(p, "skull", rot=(-4, 0, 0)); add(p, "jaw", rot=(-4, 0, 0))
    for b, g in zip(A.TAILS, A.BEND):
        add(p, b, rot=(-1.0 * g, 0, 0))
    arms(p, -8, 6)


def legs_under(p, yaw, roll, extra=None):
    for s, _ in SIDES:
        sx = 1 if s == "l" else -1
        add(p, f"thigh_{s}", rot=(0, -yaw, -roll + 3.0 * sx + (extra or {}).get(s, 0.0)))


# ------------------------------------------------------------------ LUNGE: sink, one long step, the skull down, wrench
L_COIL = tr((0, 0), (0.25, 1, ease_out), (0.34, 0.9), (0.48, 0, ease_in), (1.8, 0))
L_GO = tr((0, 0), (0.3, 0), (0.5, 1, ease_in), (0.62, 0.8, ease_out), (0.95, 0.7), (1.45, 0, back_out), (1.8, 0))
L_JAW = tr((0, 0), (0.2, -6), (0.4, -40, ease_out), (0.47, -42), (0.52, -3, ease_in), (0.95, -4), (1.15, -14, ease_out),
           (1.4, -4), (1.8, -4))


def lunge(t):
    p = {}
    stance(p)
    coil = float(L_COIL(t)); go = float(L_GO(t))
    hit = jolt(t, 0.5, 0.1)
    wrench = math.sin(2 * math.pi * 2.6 * (t - 0.62)) * window(t, 0.62, 1.0, 0.06)
    add(p, "body", rot=(2 * coil - 6 * go + 2 * hit, 4 * wrench, 3 * wrench),
        pos=(0, -3.0 * coil - 1.8 * go + 0.6 * hit, 3.0 * coil - 5.5 * go + 1.5 * hit))
    T.neck(p, (10 * coil - 12 * go + 4 * hit, 10 * wrench, 0))
    add(p, "skull", rot=(6 * coil - 10 * go + 6 * hit, 5 * wrench, 9 * wrench))
    add(p, "jaw", rot=(float(L_JAW(t)) + 4, 0, 0))
    trail(p, t, lambda u: -3.0 * float(L_COIL(u)) - 2.0 * float(L_GO(u)) - 2 * jolt(u, 0.5, 0.12), axis=0, delay=0.06)
    trail(p, t, lambda u: -7 * math.sin(2 * math.pi * 2.6 * (u - 0.62)) * window(u, 0.62, 1.0, 0.06), delay=0.06)
    arms(p, -6 * coil - 10 * go, 8 * go)
    alive(p, t, k=0.3)
    legs_under(p, 4 * wrench, 3 * wrench)
    # the right foot takes the long step in (0.28-0.5) and back out (1.0-1.3); the left braces
    r_up = steps(t, 0.28, 0.5, 8.0) + steps(t, 1.0, 1.3, 5.0)
    r_z = GUARD_DZ["r"] - 8 * smooth((t - 0.28) / 0.22) + 8 * smooth((t - 1.0) / 0.3)
    T.plant(p, "r", r_up, r_z + 2 * coil, 10 * math.sin(math.pi * min(1, max(0, (t - 0.28) / 0.22))), -16 * min(1.0, r_up / 8.0),
            clear=0.8 * min(1.0, r_up / 3.0) - 0.05)
    push = smooth((t - 0.32) / 0.16) * (1 - smooth((t - 1.0) / 0.4))
    T.plant(p, "l", 0, GUARD_DZ["l"] + 2 * coil + 2 * push, 20 * push, 8 * push)
    return p


# ------------------------------------------------------------------ PARRY: the blow on the skull, then the face bite
P_YAW = tr((0, 0), (0.07, -1, ease_out), (0.22, -0.9), (0.45, 0.4, smooth), (0.6, 0.7, ease_in), (0.85, 0.6), (1.5, 0, back_out))
P_UP = tr((0, 0), (0.25, 0), (0.45, -0.8, smooth), (0.6, 0.6, ease_in), (0.85, 0.5), (1.5, 0, back_out))
P_JAW = tr((0, 0), (0.3, -3), (0.5, -38, ease_out), (0.58, -40), (0.63, -3, ease_in), (1.0, -4), (1.5, -4))


def parry(t):
    p = {}
    stance(p)
    yw = float(P_YAW(t)); up = float(P_UP(t))
    butt = jolt(t, 0.06, 0.12)
    hit = jolt(t, 0.6, 0.09)
    twist = math.sin(2 * math.pi * 2.2 * (t - 0.7)) * window(t, 0.7, 1.05, 0.06)
    add(p, "body", rot=(1.5 * up + 2 * hit, 6 * yw, -3 * butt), pos=(0, -1.0 * butt, 1.0 * butt - 2.0 * smooth((t - 0.45) / 0.15) * (1 - smooth((t - 0.9) / 0.5))))
    T.neck(p, (6 * up + 3 * hit, 16 * yw, -3 * butt))
    add(p, "skull", rot=(4 * up + 4 * hit, 8 * yw + 4 * twist, -12 * butt + 14 * max(0.0, yw) + 8 * twist))
    add(p, "jaw", rot=(float(P_JAW(t)) + 4, 0, 0))
    trail(p, t, lambda u: -5 * float(P_YAW(u)) + 4 * decay(u, 0.07, 0.16, 3.5), delay=0.06)
    trail(p, t, lambda u: 2.0 * float(P_UP(u)), axis=0, delay=0.06)
    arms(p, -6 * max(0.0, -up) + 5 * butt + 5 * hit, 4 * hit)
    alive(p, t, k=0.3)
    legs_under(p, 6 * yw, -3 * butt)
    T.plant(p, "l", 0, GUARD_DZ["l"])
    r_up = steps(t, 0.4, 0.58, 4.0) + steps(t, 1.05, 1.3, 3.0)
    r_in = smooth((t - 0.4) / 0.18) * (1 - smooth((t - 1.05) / 0.25))
    T.plant(p, "r", r_up, GUARD_DZ["r"] - 3 * r_in, 6 * math.sin(math.pi * min(1, max(0, (t - 0.4) / 0.18))),
            -14 * min(1.0, r_up / 4.0), clear=0.7 * min(1.0, r_up / 2.0) - 0.05)
    return p


# ------------------------------------------------------------------ STAGGER: a heavy lurch, one big catching step
S_LURCH = tr((0, 0), (0.1, 1, ease_out), (0.35, 0.85), (0.8, 0.35), (1.35, 0, smooth), (1.6, 0))


def stagger(t):
    p = {}
    stance(p)
    lu = float(S_LURCH(t))
    shake = decay(t, 0.9, 0.18, 4.5) * (1 - smooth((t - 1.35) / 0.15))
    byaw, broll = 9 * lu, -7 * lu
    add(p, "body", rot=(-2 * lu, byaw, broll), pos=(0, -1.6 * lu, 1.5 * lu))
    T.neck(p, (-4 * lu, -16 * lu + 4 * shake, 4 * lu)); add(p, "skull", rot=(-2 * lu, -8 * lu + 3 * shake, 7 * lu + 10 * shake))
    add(p, "jaw", rot=(-8 * window(t, 0.06, 0.6, 0.1) - 2 * abs(shake), 0, 0))
    trail(p, t, lambda u: -1.0 * 9 * float(S_LURCH(u)) + 4 * decay(u, 0.25, 0.3, 1.8), delay=0.07)
    trail(p, t, lambda u: -2.0 * float(S_LURCH(u)), axis=0, delay=0.07)
    arms(p, 6 * lu + 2 * decay(t, 0.1, 0.25, 3.0), -5 * lu)
    alive(p, t, k=0.3)
    catch = smooth((t - 0.12) / 0.25) * (1 - smooth((t - 0.85) / 0.35))
    legs_under(p, byaw, broll, {"l": -6.0 * catch})
    l_up = steps(t, 0.12, 0.37, 7.0) + steps(t, 0.85, 1.2, 4.0)
    T.plant(p, "l", l_up, GUARD_DZ["l"] - 4 * catch, 8 * math.sin(math.pi * min(1, max(0, (t - 0.12) / 0.25))),
            -14 * min(1.0, l_up / 7.0), clear=0.8 * min(1.0, l_up / 3.0) - 0.05)
    T.plant(p, "r", 0, GUARD_DZ["r"])
    return p


# ------------------------------------------------------------------ FACE_BITE: over the rival's head, down across the snout
F_UP = tr((0, 0), (0.35, 1, ease_out), (0.55, -0.6, ease_in), (0.7, -0.5), (1.0, -0.4), (1.4, 0, back_out))
F_JAW = tr((0, 0), (0.15, -4), (0.42, -42, ease_out), (0.5, -44), (0.56, -3, ease_in), (1.05, -4), (1.2, -12, ease_out),
           (1.4, -4))


def face_bite(t):
    p = {}
    stance(p)
    up = float(F_UP(t))
    hit = jolt(t, 0.55, 0.1)
    twist = math.sin(2 * math.pi * 2.4 * (t - 0.65)) * window(t, 0.65, 1.0, 0.06)
    add(p, "body", rot=(4 * up + 2 * hit, 3 * twist, 2 * twist), pos=(0, 1.2 * max(0.0, up) - 0.6 * hit, -3.0 * smooth((t - 0.3) / 0.25) * (1 - smooth((t - 1.0) / 0.4))))
    T.neck(p, (16 * up + 4 * hit, 6 * twist, 0))
    add(p, "skull", rot=(8 * up + 6 * hit, 4 * twist, 14 * twist))
    add(p, "jaw", rot=(float(F_JAW(t)) + 4, 0, 0))
    trail(p, t, lambda u: -3.0 * float(F_UP(u)), axis=0, delay=0.06)
    trail(p, t, lambda u: -6 * math.sin(2 * math.pi * 2.4 * (u - 0.65)) * window(u, 0.65, 1.0, 0.06), delay=0.06)
    arms(p, -10 * max(0.0, up), 6 * max(0.0, up))
    alive(p, t, k=0.3)
    legs_under(p, 3 * twist, 2 * twist)
    r_up = steps(t, 0.3, 0.52, 6.0) + steps(t, 1.0, 1.3, 4.0)
    r_in = smooth((t - 0.3) / 0.22) * (1 - smooth((t - 1.0) / 0.3))
    T.plant(p, "r", r_up, GUARD_DZ["r"] - 5 * r_in, 8 * math.sin(math.pi * min(1, max(0, (t - 0.3) / 0.22))),
            -14 * min(1.0, r_up / 6.0), clear=0.7 * min(1.0, r_up / 2.5) - 0.05)
    T.plant(p, "l", 0, GUARD_DZ["l"])
    return p


NEW = {
    "lunge": (lunge, LUNGE_T, False, "Duelo", "bote pesado: afunda, um passo longo, o crânio desce na cabeça do rival (0,50 s), tranco, recua"),
    "parry": (parry, PARRY_T, False, "Duelo", "toma o golpe no lado do crânio e devolve a mordida na cara (0,60 s)"),
    "stagger": (stagger, STAGGER_T, False, "Duelo", "foi aparado: tranco pesado de lado, um passo grande para se segurar"),
    "face_bite": (face_bite, FACE_BITE_T, False, "Duelo", "mordida na cara: a cabeça sobe sobre a do rival e morde o focinho (0,55 s)"),
}
