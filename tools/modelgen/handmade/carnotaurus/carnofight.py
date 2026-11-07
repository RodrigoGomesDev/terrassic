"""Carnotaurus: the epic duel (06/11/2026). Rodrigo found the fights "muito estáticas, monótonas"; the new duel (Java)
holds both in GUARD side-on and strings JAB, LUNGE, PARRY and STAGGER. These are its three committed moves, at the fixed
lengths the generic Java expects (LUNGE_T, PARRY_T, STAGGER_T; hit at 0.50 s in the lunge and 0.60 s in the parry).

Its own, from docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md (horns and a braced skull for head blows, Mazzetta et al.
1998, 2009; a weak quick bite; the fastest of the big theropods) and against the T. rex (rexfight.py, the crushing bite)
and the Giganotosaurus (gigafight.py, the cut):
  * LUNGE = a head-down charge with the horns: it coils low on its long legs with the head dropped level and the stiff
    tail up, then springs in two quick strides and drives the horn boss in at 0.50 s; the skull takes the shock (it
    jolts back up the neck), the horns HOOK up through the rival and it skips back light. The mouth stays shut: it
    does not bite to hold;
  * PARRY = a dry sideways head-butt that knocks the blow away (0 to 0.25 s), the swing coiled into a low uppercut of
    the horns that lands at 0.60 s;
  * STAGGER = light and quick: a sharp jolt aside, two hopping steps (one crossing), the head flicked about in hawk
    jumps, the stiff tail swung like a lever, a rapid shake of the horned head, and it is back on its toes by 1.35 s.
Fluid rules as in carnoflow.py: breathing under all, envelopes, three beats with back_out, the stiff tail (STIFF) late.
All three start and end on the guard's stance (carnoflow.guard without its loops).
"""
import math

import carnoanims as A
import carnoflow as F
from anim2 import add, smooth, ease_in, ease_out, back_out
from theropod import window, SIDES

T = A.T
TAILS = A.TAILS
tr = A.tr
arms = A.arms
STIFF = F.STIFF
wave, tremor, trail, alive, alive_upper = F.wave, F.tremor, F.trail, F.alive, F.alive_upper
bump, decay, steps = F.bump, F.decay, F.steps

LUNGE_T = 1.8
PARRY_T = 1.5
STAGGER_T = 1.6
GUARD_DZ = {"l": 3.0, "r": -4.0}        # carnoflow.guard: the left foot back, the right forward


def jolt(t, at, tau, rise=0.025):
    return math.exp(-max(0.0, t - at) / tau) * smooth((t - at + rise) / rise)


def stance(p):
    """the guard at rest: low, the horns presented, the stiff tail a little up, the arms tense"""
    add(p, "body", rot=(6, 0, 0), pos=(0, -3.4, 0))
    T.neck(p, (-11, 0, 0)); add(p, "skull", rot=(-6, 0, 0)); add(p, "jaw", rot=(-3, 0, 0))
    for b, g in zip(TAILS, STIFF):
        if g:
            add(p, b, rot=(-2.0 * g, 0, 0))
    arms(p, -10, 8)


def legs_under(p, yaw, roll, extra=None):
    for s, _ in SIDES:
        sx = 1 if s == "l" else -1
        add(p, f"thigh_{s}", rot=(0, -yaw, -roll + 3.0 * sx + (extra or {}).get(s, 0.0)))


def swing_plant(p, s, t, a, b, h, dz, clear_k=0.8):
    """a foot lifted between a and b (arch h) and set at dz"""
    up = steps(t, a, b, h)
    u = min(1.0, max(0.0, (t - a) / (b - a)))
    T.plant(p, s, up, dz, 10 * math.sin(math.pi * u), -18 * min(1.0, up / max(h, 1e-6)),
            clear=clear_k * min(1.0, up / 3.0) - 0.05)


# ------------------------------------------------------------------ LUNGE: coil, two strides, horns in, hook, skip back
L_COIL = tr((0, 0), (0.28, 1, ease_out), (0.36, 0.9), (0.48, 0, ease_in), (1.8, 0))
L_GO = tr((0, 0), (0.33, 0), (0.5, 1, ease_in), (0.6, 0.72, ease_out), (0.85, 0.66), (1.4, 0, back_out), (1.8, 0))
L_HOOK = tr((0, 0), (0.52, 0), (0.64, 1, ease_out), (0.78, 0.6), (1.05, 0, smooth), (1.8, 0))


def lunge(t):
    p = {}
    stance(p)
    coil = float(L_COIL(t)); go = float(L_GO(t)); hook = float(L_HOOK(t))
    hit = jolt(t, 0.5, 0.09)
    shock = tremor(t, (11.3, 16.9, 7.7), (1.0, 0.6, 0.4)) * window(t, 0.5, 0.72, 0.05)
    clear_head = decay(t, 1.0, 0.11, 6.5)                 # a quick shake of the horned head after the blow
    bob = 0.6 * math.sin(2 * math.pi * 6.0 * t) * window(t, 0.36, 0.5, 0.04)    # the two quick strides of the charge
    add(p, "body", rot=(1 * coil - 11 * go + 3 * hit + 0.4 * shock + 3 * hook, 0, 0),
        pos=(0, -3.8 * coil - 2.2 * go + 0.8 * hit + bob, 4.0 * coil - 6.0 * go + 2.5 * hit))
    # the head drops level so the horns lead; the shock runs back up the neck; then the horns hook up through
    T.neck(p, (-13 * coil - 4 * go + 6 * hit + 0.6 * shock + 11 * hook, 0, 0))
    add(p, "skull", rot=(-10 * coil - 8 * go + 9 * hit + 0.9 * shock + 8 * hook, 3 * clear_head, 9 * clear_head))
    add(p, "jaw", rot=(2 * coil + 2 * go - 5 * hit - 4 * hook, 0, 0))           # shut, popped open by the shock
    trail(p, t, lambda u: -4.0 * float(L_COIL(u)) - 2.5 * float(L_GO(u)) + 3.5 * float(L_HOOK(u))
          - 3 * jolt(u, 0.5, 0.12), axis=0, delay=0.05)
    trail(p, t, lambda u: 4 * decay(u, 0.5, 0.2, 3.5), delay=0.05)
    arms(p, -6 * coil - 12 * go + 6 * hit, 10 * go)
    alive(p, t, k=0.35)
    legs_under(p, 0.0, 0.0)
    # the charge: the right strides in (0.3-0.48) and takes the hit; the left drives; a skip back after the hook
    r_z = GUARD_DZ["r"] - 9 * smooth((t - 0.3) / 0.18) + 9 * smooth((t - 0.92) / 0.23)
    up = steps(t, 0.3, 0.48, 9.0) + steps(t, 0.92, 1.15, 5.0)
    T.plant(p, "r", up, r_z + 2 * coil, 10 * math.sin(math.pi * min(1, max(0, (t - 0.3) / 0.18))), -18 * min(1.0, up / 9.0),
            clear=0.8 * min(1.0, up / 3.0) - 0.05)
    push = smooth((t - 0.34) / 0.14) * (1 - smooth((t - 0.9) / 0.4))
    l_up = steps(t, 1.17, 1.42, 4.0)
    T.plant(p, "l", l_up, GUARD_DZ["l"] + 2 * coil + 3 * push, 24 * push, 10 * push - 14 * min(1.0, l_up / 4.0),
            clear=0.6 * min(1.0, l_up / 2.0) - 0.05)
    return p


# ------------------------------------------------------------------ PARRY: a dry sideways butt, then the horn uppercut
P_YAW = tr((0, 0), (0.07, -1, ease_out), (0.22, -0.9), (0.45, 0.55, smooth), (0.6, -0.42, ease_in), (0.75, -0.3),
           (1.5, 0, back_out))
P_PITCH = tr((0, 0), (0.07, 0.2), (0.25, 0.1), (0.45, -1, smooth), (0.6, 1.0, ease_in), (0.75, 0.8), (1.5, 0, back_out))


def parry(t):
    p = {}
    stance(p)
    yw = float(P_YAW(t)); pt = float(P_PITCH(t))
    butt = jolt(t, 0.06, 0.1)                         # the skull meets the blow side-on
    hit = jolt(t, 0.6, 0.08)
    snort = bump(t, 0.82, 0.05)
    byaw = 8 * yw
    broll = -4 * butt + 3 * max(0.0, -pt)
    add(p, "body", rot=(1.5 * pt + 2 * hit, byaw, broll),
        pos=(0, -1.2 * max(0.0, -pt) - 0.6 * butt, 1.2 * butt - 2.5 * smooth((t - 0.45) / 0.15) * (1 - smooth((t - 0.8) / 0.6))))
    T.neck(p, (6 * pt + 4 * hit, 22 * yw, -4 * butt))
    add(p, "skull", rot=(5 * pt + 6 * hit + 3 * snort, 10 * yw, -14 * butt + 8 * max(0.0, yw) - 6 * hit))
    add(p, "jaw", rot=(-4 * butt - 5 * hit - 6 * snort, 0, 0))
    trail(p, t, lambda u: -0.8 * 8 * float(P_YAW(u)) + 5 * decay(u, 0.07, 0.15, 4.0), delay=0.05)
    trail(p, t, lambda u: 2.5 * float(P_PITCH(u)), axis=0, delay=0.05)
    arms(p, -6 * max(0.0, -pt) + 5 * butt + 6 * hit, 4 * hit)
    alive(p, t, k=0.35)
    # a light skip out with the left foot as it butts, then the right steps in under the uppercut
    l_side = 3.5 * smooth(t / 0.18) * (1 - smooth((t - 0.84) / 0.22))
    legs_under(p, byaw, broll, {"l": l_side})
    l_up = steps(t, 0.0, 0.2, 4.0) + steps(t, 0.84, 1.06, 3.0)
    T.plant(p, "l", l_up, GUARD_DZ["l"], 0, -14 * min(1.0, l_up / 4.0), clear=0.6 * min(1.0, l_up / 2.0) - 0.05)
    r_in = smooth((t - 0.42) / 0.16) * (1 - smooth((t - 1.1) / 0.25))
    r_up = steps(t, 0.42, 0.58, 5.0) + steps(t, 1.1, 1.35, 3.5)
    T.plant(p, "r", r_up, GUARD_DZ["r"] - 4 * r_in, 8 * math.sin(math.pi * min(1, max(0, (t - 0.42) / 0.16))),
            -16 * min(1.0, r_up / 5.0), clear=0.7 * min(1.0, r_up / 2.5) - 0.05)
    return p


# ------------------------------------------------------------------ STAGGER: a sharp jolt, two hops, a rapid head shake
S_LURCH = tr((0, 0), (0.08, 1, ease_out), (0.3, 0.8), (0.7, 0.35), (1.25, 0, smooth), (1.6, 0))
HEAD_JUMPS = ((0.0, (0, 0)), (0.05, (-6, 1.0)), (0.3, (4, 0.55)), (0.55, (-3, 0.8)), (0.8, (2, 0.2)), (1.25, (0, 0)))


def hawk(t):
    """the head flicked in jumps, each landing with an overshoot (carnoflow.snap) and the last one easing home"""
    cur = (0.0, 0.0)
    for tk, v in HEAD_JUMPS:
        if t < tk:
            break
        u = back_out(min(1.0, (t - tk) / 0.12), 1.4)
        cur = (cur[0] + (v[0] - cur[0]) * u, cur[1] + (v[1] - cur[1]) * u)
    return cur


def stagger(t):
    p = {}
    stance(p)
    lu = float(S_LURCH(t)); hp, hy = hawk(t)
    shake = decay(t, 0.95, 0.12, 7.0) * (1 - smooth((t - 1.3) / 0.1))
    byaw, broll = 12 * lu, -8 * lu
    hop = steps(t, 0.1, 0.3, 1.0) + steps(t, 0.3, 0.48, 0.8)         # the body bobs with the hops
    add(p, "body", rot=(-2 * lu, byaw, broll), pos=(0, -1.2 * lu + hop, 1.2 * lu))
    T.neck(p, (hp, -26 * hy + 5 * shake, 5 * hy))
    add(p, "skull", rot=(0.6 * hp, -10 * hy + 4 * shake, 8 * hy + 13 * shake))
    add(p, "jaw", rot=(-8 * window(t, 0.06, 0.5, 0.1) - 3 * abs(shake), 0, 0))
    # the stiff tail swings out like a lever, quickly, and its wobble dies fast
    trail(p, t, lambda u: -1.2 * 12 * float(S_LURCH(u)) + 6 * decay(u, 0.2, 0.22, 2.2), gain=(1.0, 0.9, 0.5, 0.15, 0.0), delay=0.05)
    trail(p, t, lambda u: -2.5 * float(S_LURCH(u)), axis=0, delay=0.05)
    arms(p, 6 * lu + 3 * decay(t, 0.1, 0.2, 4.0), -6 * lu)
    alive(p, t, k=0.35)
    # the left foot crosses in front to catch it (0.1-0.3), the right hops back (0.3-0.48), the left uncrosses (0.7-0.95)
    cross = smooth((t - 0.1) / 0.2) * (1 - smooth((t - 0.7) / 0.25))
    back = smooth((t - 0.3) / 0.18) * (1 - smooth((t - 0.95) / 0.3))
    legs_under(p, byaw, broll, {"l": -7.0 * cross, "r": -1.5 * back})
    l_up = steps(t, 0.1, 0.3, 7.0) + steps(t, 0.7, 0.95, 4.5)
    T.plant(p, "l", l_up, GUARD_DZ["l"] - 5 * cross, 8 * math.sin(math.pi * min(1, max(0, (t - 0.1) / 0.2))), -16 * min(1.0, l_up / 7.0),
            clear=0.8 * min(1.0, l_up / 3.0) - 0.05)
    r_up = steps(t, 0.3, 0.48, 4.0) + steps(t, 0.95, 1.2, 3.0)
    T.plant(p, "r", r_up, GUARD_DZ["r"] + 4 * back, 6 * back, -14 * min(1.0, r_up / 4.0) - 6 * back,
            clear=0.6 * min(1.0, r_up / 2.0) - 0.05)
    return p


NEW = {
    "lunge": (lunge, LUNGE_T, False, "Duelo", "investida de cabeça baixa: dois passos de carga, chifrada (0,50 s), engancha para cima, pula atrás"),
    "parry": (parry, PARRY_T, False, "Duelo", "cabeçada lateral seca que desvia o golpe e chifrada de baixo para cima (0,60 s)"),
    "stagger": (stagger, STAGGER_T, False, "Duelo", "foi aparado: tranco seco, dois pulinhos (um cruzado), sacode os chifres e volta rápido"),
}
