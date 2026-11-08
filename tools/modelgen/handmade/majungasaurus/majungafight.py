"""Majungasaurus: the duel's committed moves at the fixed lengths the generic Java expects (DuelStyle: LUNGE 36 ticks
with the hit at 10, PARRY 30 ticks with the counter at 12, STAGGER 32 ticks); its signature blow, the dome shove, is
in majungaanims.py.

Its own, from the study (docs/estudos/13, "No jogo" 5): low and stubborn, it hardly dodges and hardly staggers (the
low centre of gravity), it bites and holds and pushes with the dome from below (the Carnotaurus rams).
  * LUNGE = a short low reach: a coil, one step, the jaws shut at 0.50 s and it HOLDS, wrenching the head twice
    before it lets go;
  * PARRY = it takes the blow on the lowered head (0 to 0.3 s) and, at 0.60 s, shoves its DOME up into the rival from
    below (the dome shove as counter);
  * STAGGER = it barely gives: a lurch, one catching step, back in guard by 1.2 s.
All start and end on the guard's stance (majungaanims.guard without its loops).
"""
import math

import majungaanims as A
from anim2 import smooth, ease_in, ease_out, back_out
from theropod import window, SIDES

T = A.T
add = A.add                # the translations scaled to this rig (majungaanims.Q)
tr = A.tr
arms, trail, alive, alive_upper, tremor, bump, decay, steps = (A.arms, A.trail, A.alive, A.alive_upper, A.tremor,
                                                                A.bump, A.decay, A.steps)

LUNGE_T = 1.8
PARRY_T = 1.5
STAGGER_T = 1.6
GUARD_DZ = {"l": 4.0, "r": -5.0}


def jolt(t, at, tau, rise=0.025):
    return math.exp(-max(0.0, t - at) / tau) * smooth((t - at + rise) / rise)


def stance(p):
    add(p, "body", rot=(-4, 0, 0), pos=(0, -2.6, 0))
    T.neck(p, (-9, 0, 0)); add(p, "skull", rot=(-4, 0, 0)); add(p, "jaw", rot=(-4, 0, 0))
    for b, g in zip(A.TAILS, A.BEND):
        add(p, b, rot=(-1.0 * g, 0, 0))
    arms(p, -8, 6)


def legs_under(p, yaw, roll, extra=None):
    for s, _ in SIDES:
        sx = 1 if s == "l" else -1
        add(p, f"thigh_{s}", rot=(0, -yaw, -roll + 3.0 * sx + (extra or {}).get(s, 0.0)))


# ------------------------------------------------------------------ LUNGE: a short coil, one long step, the head shoots in
L_COIL = tr((0, 0), (0.22, 1, ease_out), (0.3, 0.9), (0.46, 0, ease_in), (1.8, 0))
L_GO = tr((0, 0), (0.28, 0), (0.5, 1, ease_in), (0.6, 0.85, ease_out), (0.8, 0.4), (1.3, 0, back_out), (1.8, 0))
L_JAW = tr((0, 0), (0.2, -6), (0.4, -40, ease_out), (0.47, -42), (0.52, -3, ease_in), (1.1, -3), (1.25, -18, ease_out), (1.45, -4), (1.8, -4))


def lunge(t):
    p = {}
    stance(p)
    coil = float(L_COIL(t)); go = float(L_GO(t))
    hit = jolt(t, 0.5, 0.08)
    flick = 2.0 * math.sin(2 * math.pi * 2.6 * (t - 0.58)) * window(t, 0.58, 1.12, 0.08)   # the wrench of the hold
    add(p, "body", rot=(1.5 * coil - 5 * go + 1.5 * hit, 3 * flick, 0),
        pos=(0, -2.4 * coil - 1.4 * go + 0.4 * hit, 2.5 * coil - 6.5 * go + 1.0 * hit))
    T.neck(p, (8 * coil - 14 * go + 3 * hit, 6 * flick, 0))
    add(p, "skull", rot=(5 * coil - 8 * go + 5 * hit, 3 * flick, 6 * flick))
    add(p, "jaw", rot=(float(L_JAW(t)) + 4, 0, 0))
    trail(p, t, lambda u: -2.5 * float(L_COIL(u)) - 2.0 * float(L_GO(u)) - 2 * jolt(u, 0.5, 0.1), axis=0, delay=0.06)
    trail(p, t, lambda u: -5 * decay(u, 0.56, 0.14, 3.5), delay=0.06)
    arms(p, -6 * coil - 10 * go, 8 * go)
    alive(p, t, k=0.3)
    legs_under(p, 3 * flick, 0)
    # the right foot takes the long step in (0.26-0.48) and back out (0.85-1.15); the left braces
    r_up = steps(t, 0.26, 0.48, 8.0) + steps(t, 0.85, 1.15, 5.0)
    r_z = GUARD_DZ["r"] - 9 * smooth((t - 0.26) / 0.22) + 9 * smooth((t - 0.85) / 0.3)
    T.plant(p, "r", r_up, r_z + 2 * coil, 10 * math.sin(math.pi * min(1, max(0, (t - 0.26) / 0.22))), -16 * min(1.0, r_up / 8.0),
            clear=0.8 * min(1.0, r_up / 3.0) - 0.05)
    push = smooth((t - 0.3) / 0.16) * (1 - smooth((t - 0.85) / 0.4))
    T.plant(p, "l", 0, GUARD_DZ["l"] + 2 * coil + 2 * push, 20 * push, 8 * push)
    return p


# ------------------------------------------------------------------ PARRY: it takes the blow on the turned head, then the brow butt
P_SLIP = tr((0, 0), (0.08, 1, ease_out), (0.3, 0.9), (0.5, 0.3, smooth), (0.65, -0.5, ease_in), (0.85, -0.4), (1.5, 0, back_out))
P_JAW = tr((0, 0), (0.3, -3), (1.5, -2))
P_BUTT = tr((0, 0), (0.35, 0), (0.5, -0.6, ease_out), (0.6, 1, ease_in), (0.72, 0.9), (1.5, 0, back_out))


def parry(t):
    p = {}
    stance(p)
    sl = float(P_SLIP(t)) * (1 - smooth((t - 0.35) / 0.15))
    k = float(P_BUTT(t))
    hit = jolt(t, 0.6, 0.1)
    add(p, "body", rot=(-3 * max(0.0, k) + 2 * hit, -4 * sl, 2 * max(0.0, sl)),
        pos=(0, -1.4 * max(0.0, sl) - 1.2 * max(0.0, -k), 4.5 * max(0.0, k) - 1.5 * max(0.0, -k)))
    T.neck(p, (-3 * max(0.0, sl) - 10 * max(0.0, k) + 5 * min(0.0, k) + 4 * hit, 12 * sl, -3 * max(0.0, sl)))
    add(p, "skull", rot=(-20 * max(0.0, k) + 5 * min(0.0, k) + 6 * hit, 6 * sl, -5 * sl + 3 * decay(t, 0.65, 0.15, 5.0)))
    add(p, "jaw", rot=(float(P_JAW(t)), 0, 0))
    trail(p, t, lambda u: 5 * float(P_SLIP(u)) * (1 - smooth((u - 0.35) / 0.15)), delay=0.06)
    trail(p, t, lambda u: 4 * jolt(u, 0.6, 0.18), axis=0, delay=0.06)
    arms(p, -6 * max(0.0, k) + 4 * hit, 3 * hit)
    alive(p, t, k=0.3)
    legs_under(p, -4 * sl, 2 * max(0.0, sl))
    # the head turns the blow (no hop: it is heavy), then one step in with the left for the butt (0.4-0.6) and back
    l_up = steps(t, 0.4, 0.6, 6.0) + steps(t, 0.95, 1.25, 4.0)
    l_in = smooth((t - 0.4) / 0.2) * (1 - smooth((t - 0.95) / 0.3))
    T.plant(p, "l", l_up, GUARD_DZ["l"] - 7 * l_in, 6 * l_up / 6.0, -12 * min(1.0, l_up / 6.0), clear=0.7 * min(1.0, l_up / 2.0) - 0.05)
    T.plant(p, "r", 0, GUARD_DZ["r"] + 2 * l_in, 12 * l_in, 6 * l_in)
    return p


# ------------------------------------------------------------------ STAGGER: knocked aside, two quick catching steps
S_LURCH = tr((0, 0), (0.1, 0.55, ease_out), (0.35, 0.5), (0.7, 0.2), (1.2, 0, smooth), (1.6, 0))


def stagger(t):
    p = {}
    stance(p)
    lu = float(S_LURCH(t))
    shake = decay(t, 0.8, 0.15, 5.0) * (1 - smooth((t - 1.25) / 0.15))
    byaw, broll = 8 * lu, -8 * lu
    add(p, "body", rot=(-2 * lu, byaw, broll), pos=(0, -1.2 * lu, 1.5 * lu))
    T.neck(p, (-3 * lu, -14 * lu + 4 * shake, 4 * lu)); add(p, "skull", rot=(-2 * lu, -7 * lu + 3 * shake, 7 * lu + 10 * shake))
    add(p, "jaw", rot=(-7 * window(t, 0.06, 0.5, 0.1) - 2 * abs(shake), 0, 0))
    trail(p, t, lambda u: -8 * float(S_LURCH(u)) + 4 * decay(u, 0.2, 0.25, 2.2), delay=0.06)
    trail(p, t, lambda u: -2.0 * float(S_LURCH(u)), axis=0, delay=0.06)
    arms(p, 6 * lu + 2 * decay(t, 0.1, 0.2, 3.5), -5 * lu)
    alive(p, t, k=0.3)
    catch = smooth((t - 0.1) / 0.2) * (1 - smooth((t - 0.75) / 0.3))
    legs_under(p, byaw, broll, {"l": -5.0 * catch})
    l_up = steps(t, 0.1, 0.3, 6.0) + steps(t, 0.75, 1.0, 3.0)
    T.plant(p, "l", l_up, GUARD_DZ["l"] - 4 * catch, 8 * math.sin(math.pi * min(1, max(0, (t - 0.1) / 0.2))),
            -14 * min(1.0, l_up / 6.0), clear=0.8 * min(1.0, l_up / 3.0) - 0.05)
    r_up = steps(t, 0.32, 0.52, 4.0)
    T.plant(p, "r", r_up, GUARD_DZ["r"] + 2 * smooth((t - 0.32) / 0.2) * (1 - smooth((t - 1.0) / 0.4)), 5 * r_up / 4.0,
            -10 * min(1.0, r_up / 4.0), clear=0.6 * min(1.0, r_up / 2.0) - 0.05)
    return p


NEW = {
    "lunge": (lunge, LUNGE_T, False, "Duelo", "bote baixo: encolhe, um passo, fecha (0,50 s) e segura sacudindo"),
    "parry": (parry, PARRY_T, False, "Duelo", "aguenta o golpe na cabeça baixa e responde com o domo por baixo (0,60 s)"),
    "stagger": (stagger, STAGGER_T, False, "Duelo", "foi aparado: quase não cede, um passo e volta à guarda"),
}
