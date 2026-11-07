"""Giganotosaurus: the epic duel (06/11/2026). Rodrigo found the fights "muito estáticas, monótonas"; the new duel (Java)
holds both in GUARD side-on and strings JAB, LUNGE, PARRY and STAGGER. These are its three committed moves, at the fixed
lengths the generic Java expects (LUNGE_T, PARRY_T, STAGGER_T; hit at 0.50 s in the lunge and 0.60 s in the parry).

NAME: this rig already has a "lunge" (the low strike at the leg of big prey, Giganotosaurine.LUNGE, hit at 0.6 s, 1.6 s
long) that the Java plays by name, so the duel's committed strike is exported as "duel_lunge"; the old one is untouched.

Its own, from docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md (blade teeth for cutting, Coria & Currie 2006; the
carcharodontosaurids wounded and waited: it cuts and backs off, heavy and patient) and against the T. rex (rexfight.py,
the crushing bite) and the Carnotaurus (carnofight.py, the horns):
  * DUEL_LUNGE = a committed slash: it winds the head to its right with the skull turned on its side and the jaws
    spread on the blades, the weight drawn back and low, then throws the whole body in; the head sweeps low and across
    and the jaws shut at 0.50 s mid-sweep, and the head goes on RIPPING across to the other side (the blades sawing),
    lets go, pulls back and takes one heavy step back to its guard (it cuts and backs off);
  * PARRY = it pulls the long neck back and up out of the blow (0 to 0.25 s), the body rocking back, coils the head on
    its side with the jaws spread, and cuts back across at 0.60 s with a short drag;
  * STAGGER = heavy and slow: the lurch builds instead of snapping, the head is carried on past by its own weight and
    swings back slowly, a heavy crossed step, a dragged foot, the long tail swinging wide, a slow shake of the head.
Fluid rules as in gigaflow.py: slow deep breathing under all, envelopes, three beats with back_out, the whole long tail
following late (WHIP). All three start and end on the guard's stance (gigaflow.guard without its loops).
"""
import math

import gigaanims as A
import gigaflow as F
from anim2 import add, smooth, ease_in, ease_out, back_out
from theropod import window, SIDES

T = A.T
TAILS, BEND = A.TAILS, A.BEND
tr = A.tr
arms, jaw, eye = A.arms, A.jaw, A.eye
wave, tremor, trail, alive, alive_upper = F.wave, F.tremor, F.trail, F.alive, F.alive_upper
bump, decay, arch = F.bump, F.decay, F.arch

LUNGE_T = 1.8
PARRY_T = 1.5
STAGGER_T = 1.6
GUARD_DZ = {"l": -4.0, "r": 2.0}        # gigaflow.guard: the left foot forward, the right back


def jolt(t, at, tau, rise=0.03):
    return math.exp(-max(0.0, t - at) / tau) * smooth((t - at + rise) / rise)


def stance(p):
    """the guard at rest: heavy and low, the head on its side with one eye on the rival, the jaws ajar on the blades"""
    add(p, "body", rot=(4, 0, 0), pos=(0, -2.5, 0))
    eye(p, 0.75, 1.0, low=6)
    jaw(p, -7)
    for b, g in zip(TAILS, BEND):
        add(p, b, rot=(-1.0 * g, 0, 0))
    arms(p, -8, 10)


def legs_under(p, yaw, roll, extra=None):
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, -yaw, -roll + (extra or {}).get(s, 0.0)))


# ------------------------------------------------------------------ DUEL_LUNGE: wind up, throw the body in, rip across
L_SWEEP = tr((0, 0), (0.3, 1.0, ease_out), (0.37, 1.05), (0.5, -0.3, ease_in), (0.85, -1.1, ease_out), (0.95, -1.12),
             (1.6, 0, back_out), (1.8, 0))
L_LOAD = tr((0, 0), (0.3, 1, ease_out), (0.38, 0.9), (0.5, 0, ease_in), (1.8, 0))
L_GO = tr((0, 0), (0.34, 0), (0.5, 1, ease_in), (0.7, 1.08, ease_out), (0.9, 0.95), (1.55, 0, back_out), (1.8, 0))
L_JAW = tr((0, 0), (0.08, -5), (0.3, -46, ease_out), (0.42, -48), (0.5, -1, ease_in), (0.84, -3), (0.94, -26, ease_out),
           (1.15, -8), (1.8, 0, smooth))


def duel_lunge(t):
    p = {}
    stance(p)
    sw = float(L_SWEEP(t)); load = float(L_LOAD(t)); go = float(L_GO(t))
    hit = jolt(t, 0.5, 0.12)
    saw = tremor(t, (13.1, 17.9, 9.7), (0.7, 0.4, 0.3)) * window(t, 0.5, 0.85, 0.06)        # the blades sawing
    byaw, broll = 10 * sw, 3 * sw - 2 * go
    add(p, "body", rot=(3 * load - 8 * go + 1.5 * hit, byaw, broll),
        pos=(0, -1.5 * load - 2.2 * go + 0.5 * hit, 3.0 * load - 6.0 * go + 1.0 * hit))
    T.neck(p, (4 * load - 14 * go + 3 * hit + 0.4 * saw, 24 * sw, 0))
    add(p, "skull", rot=(2 * load - 4 * go + 3 * hit + 0.6 * saw, 10 * sw, -14 * sw - 6 * go + 0.8 * saw))   # on its side, blades leading
    jaw(p, float(L_JAW(t)) + 0.8 * saw)
    trail(p, t, lambda u: -9 * float(L_SWEEP(u)), delay=0.09)
    trail(p, t, lambda u: -2.0 * float(L_LOAD(u)) - 2.5 * float(L_GO(u)), axis=0, delay=0.09)
    arms(p, -4 * load - 10 * go + 5 * hit, 8 * go)
    alive(p, t, k=0.35)
    legs_under(p, byaw, broll)
    # the front (left) foot strides in heavily and takes the weight at the cut; it steps back in the recovery
    l_up = arch(t, 0.28, 0.5, 6.0) + arch(t, 1.05, 1.5, 4.5)
    l_z = GUARD_DZ["l"] - 7 * smooth((t - 0.28) / 0.22) + 7 * smooth((t - 1.05) / 0.45)
    T.plant(p, "l", l_up, l_z, 8 * math.sin(math.pi * min(1, max(0, (t - 0.28) / 0.22))), -16 * min(1.0, l_up / 6.0),
            clear=0.8 * min(1.0, l_up / 3.0) - 0.05)
    push = smooth((t - 0.32) / 0.18) * (1 - smooth((t - 0.95) / 0.6))
    T.plant(p, "r", 0.0, GUARD_DZ["r"] + 2.5 * push, 20 * push, 8 * push)
    return p


# ------------------------------------------------------------------ PARRY: the neck pulled back, then the cut back across
P_BACK = tr((0, 0), (0.12, 1, ease_out), (0.25, 0.95), (0.45, 0.4, smooth), (0.6, 0, ease_in), (1.5, 0))
P_SWEEP = tr((0, 0), (0.12, -0.4, ease_out), (0.25, -0.3), (0.45, 1.0, smooth), (0.6, -0.15, ease_in), (0.8, -0.55, ease_out),
             (1.5, 0, back_out))
P_IN = tr((0, 0), (0.42, 0), (0.6, 1, ease_in), (0.78, 1.05), (1.5, 0, back_out))
P_JAW = tr((0, 0), (0.1, -3), (0.28, -12), (0.47, -46, ease_out), (0.53, -47), (0.6, -1, ease_in), (0.82, -3), (0.92, -20, ease_out),
           (1.1, -7), (1.5, 0, smooth))


def parry(t):
    p = {}
    stance(p)
    bk = float(P_BACK(t)); sw = float(P_SWEEP(t)); fin = float(P_IN(t))
    glance = jolt(t, 0.1, 0.18)                       # the blow glances off the shoulder
    hit = jolt(t, 0.6, 0.12)
    saw = tremor(t, (12.7, 18.3, 9.1), (0.7, 0.4, 0.3)) * window(t, 0.6, 0.8, 0.05)
    byaw, broll = 7 * sw - 4 * glance, 4 * glance + 2 * sw
    add(p, "body", rot=(3 * bk - 4 * fin + 1.5 * hit, byaw, broll),
        pos=(0, -0.6 * bk - 1.2 * fin, 3.0 * bk - 3.5 * fin + 1.0 * hit))
    T.neck(p, (14 * bk - 8 * fin + 3 * hit + 0.4 * saw, 22 * sw - 6 * bk, 0))
    add(p, "skull", rot=(4 * bk - 3 * fin + 3 * hit + 0.6 * saw, 8 * sw, -12 * max(0.0, sw) + 10 * bk + 0.8 * saw))
    jaw(p, float(P_JAW(t)) + 0.8 * saw)
    trail(p, t, lambda u: -8 * float(P_SWEEP(u)) + 4 * decay(u, 0.1, 0.35, 1.2), delay=0.09)
    trail(p, t, lambda u: 2.5 * float(P_BACK(u)) - 2.0 * float(P_IN(u)), axis=0, delay=0.09)
    arms(p, 4 * bk - 8 * fin + 4 * glance, 6 * fin)
    alive(p, t, k=0.35)
    legs_under(p, byaw, broll)
    # the front (left) foot steps back as it pulls away (0.02-0.3), then in again under the cut (0.4-0.62)
    back = smooth(t / 0.28) * (1 - smooth((t - 0.4) / 0.22))
    l_up = arch(t, 0.02, 0.3, 4.0) + arch(t, 0.4, 0.62, 4.5)
    T.plant(p, "l", l_up, GUARD_DZ["l"] + 5 * back - 2 * fin, 0, -14 * min(1.0, l_up / 4.0), clear=0.6 * min(1.0, l_up / 2.0) - 0.05)
    T.plant(p, "r", 0.0, GUARD_DZ["r"], 10 * fin, 4 * fin)
    return p


# ------------------------------------------------------------------ STAGGER: the lurch builds, the head swings on, slowly
S_LURCH = tr((0, 0), (0.3, 1, ease_out), (0.6, 0.85), (0.95, 0.4), (1.4, 0, smooth), (1.6, 0))
S_HEAD = tr((0, 0), (0.12, -0.2), (0.45, 1, ease_out), (0.8, 0.45), (1.2, 0.15), (1.6, 0, smooth))


def stagger(t):
    p = {}
    stance(p)
    lu = float(S_LURCH(t)); hd = float(S_HEAD(t))
    wob = decay(t, 0.45, 0.45, 1.4)                   # the long head swinging back on the neck, slowly
    shake = decay(t, 1.12, 0.22, 3.0) * (1 - smooth((t - 1.48) / 0.1))
    byaw, broll = 11 * lu, -9 * lu
    add(p, "body", rot=(-2.5 * lu, byaw, broll), pos=(0, -2.0 * lu, 1.5 * lu))
    T.neck(p, (-5 * hd + 3 * wob, -28 * hd + 5 * wob + 4 * shake, 4 * hd))
    add(p, "skull", rot=(-3 * hd + 2 * wob, -10 * hd + 3 * shake, 12 * hd + 10 * shake))    # the eye rolled away
    jaw(p, -12 * window(t, 0.15, 0.85, 0.2) - 3 * abs(shake))
    trail(p, t, lambda u: -1.0 * 11 * float(S_LURCH(u)) + 4 * decay(u, 0.4, 0.3, 0.9), delay=0.1)
    trail(p, t, lambda u: -2.5 * float(S_LURCH(u)), axis=0, delay=0.1)
    arms(p, 6 * lu + 3 * decay(t, 0.3, 0.4, 1.8), -5 * lu)
    alive(p, t, k=0.35)
    # the rear (right) foot crosses behind the front one to catch the weight (0.25-0.7), back out (1.05-1.45); the
    # front (left) drags its toes (0.7-1.1)
    cross = smooth((t - 0.25) / 0.45) * (1 - smooth((t - 1.05) / 0.4))
    drag = smooth((t - 0.7) / 0.4) * (1 - smooth((t - 1.1) / 0.4))
    legs_under(p, byaw, broll, {"r": 6.0 * cross, "l": 2.0 * drag})
    r_up = arch(t, 0.25, 0.7, 5.0) + arch(t, 1.05, 1.45, 3.5)
    T.plant(p, "r", r_up, GUARD_DZ["r"] - 3 * cross, 6 * math.sin(math.pi * min(1, max(0, (t - 0.25) / 0.45))), -14 * min(1.0, r_up / 5.0),
            clear=0.8 * min(1.0, r_up / 3.0) - 0.05)
    l_up = arch(t, 0.72, 1.02, 1.0)
    T.plant(p, "l", l_up, GUARD_DZ["l"] + 3 * drag, 12 * drag, -18 * drag, clear=-0.05 + 0.3 * min(1.0, l_up))
    return p


NEW = {
    "duel_lunge": (duel_lunge, LUNGE_T, False, "Duelo", "bote do duelo: arma de lado de boca aberta, joga o corpo, corta (0,50 s) e rasga atravessando"),
    "parry": (parry, PARRY_T, False, "Duelo", "recua o pescoço para fora do golpe e corta de volta atravessando (0,60 s)"),
    "stagger": (stagger, STAGGER_T, False, "Duelo", "foi aparado: tranco pesado e lento, a cabeça passa do ponto, cruza o pé, sacode devagar"),
}
