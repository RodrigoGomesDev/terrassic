"""Styracosaurus: the three moves of the epic duel (06/11/2026): lunge, parry, stagger, with the fixed lengths the
generic Java duel expects (LUNGE_T 1.8 s, the hit at 0.50 s; PARRY_T 1.5 s, the counter at 0.60 s; STAGGER_T 1.6 s).

From its own body and its own study (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md; Padian & Horner 2011): the crown
of spikes is for show and for taking blows, the ONE long nose horn is the weapon; 5.5 m and 2.7 t, a third of a
Triceratops, quicker and more nervous. It fights front on too, but where the Triceratops drives a short heavy shove
this one STABS, like a fencer:
  * lunge: a quick coil (the crown flashed up at the rival, the tail lashing), then a bound of the forefeet with the
    neck shooting out, the nose horn in at 0.50 s straight from the neck with the shoulders behind it, a flick of the
    point up as it goes through, a hind foot skipping up behind, and a springy settle back into the guard;
  * parry: the head rolled so the blow lands flat on the crown's spikes (they ring), the rebound turned into a low
    cock of the nose horn, and a shove with the nose, in and UP (0.60 s);
  * stagger: knocked off line to its left, light and skittish: the forefeet skip sideways together, a hind foot
    crosses, the crown wobbles and pulls the head about, and at the end the crown is rattled in a quick shake (its
    `head_shake`), back to the guard.
Every move starts and ends on the guard's own pose (styraflow.guard at t = 0). Signs as in triceratops/ceraflow.py.
"""
import math

import ceraflow as C
import styracoanims as A
import styraflow as FL
from anim2 import add, smooth, ease_in, ease_out, back_out

tr, f, bump, ring, kick = C.tr, C.f, C.bump, C.ring, C.kick
Q = FL.Q
SIDES = A.SIDES
LUNGE_T, PARRY_T, STAGGER_T = 1.8, 1.5, 1.6
LEGS = ("thigh", "shin", "foot", "toes", "arm", "forearm", "hand")
G_FORE, G_HIND, G_FDX = (-2.0, -2.0), (0.5, 0.5), (0.6, -0.6)        # the guard's stance (styraflow.guard)
_G0 = {b: v for b, v in FL.guard(0.0).items() if not b.startswith(LEGS)}


def _base():
    return {b: ([*v[0]], [*v[1]]) + tuple(v[2:]) for b, v in _G0.items()}


def _breath(p, t, L, n, k=1.0):
    b = math.sin(2 * math.pi * n * t / L) * math.sin(math.pi * t / L)
    add(p, "body", rot=(0.4 * k * b, 0, 0))
    add(p, "neck", rot=(-0.5 * k * b, 0, 0))


def _fade(t, L):
    return 1.0 - smooth((t - (L - 0.5)) / 0.42)


def _feet(p, t, fore=None, hind=None, meta=None):
    fore, hind, meta = fore or {}, hind or {}, meta or {}
    Q.counter_legs(p)
    Q.lift(p, 0.3)                                     # continuous (ceraflow.Quad.lift)
    for i, s in enumerate(SIDES):
        Q.plan(p, t, s, "h", hind.get(s, ()), base=(G_HIND[i], 0.0), meta=meta.get(s, 0.0))
        Q.plan(p, t, s, "f", fore.get(s, ()), base=(G_FORE[i], G_FDX[i]))
    return p


# ------------------------------------------------------------------ lunge: the fencer's stab (hit 0.50 s)
L_COIL = tr((0, 0), (0.26, 1, ease_out), (0.33, 0.9), (0.47, 0, ease_in), (1.8, 0))
L_GO = tr((0, 0), (0.3, 0), (0.5, 1, smooth), (0.64, 1.06, smooth), (0.9, 0.96), (1.8, 0, back_out))
L_JAB = tr((0, 0), (0.36, 0), (0.5, 1, ease_in), (0.55, 0.55, ease_out), (0.72, 0.15), (0.95, 0))
L_FLICK = tr((0, 0), (0.5, 0), (0.58, 1, ease_out), (0.72, 0.3), (1.05, 0, smooth))
L_PUSH = tr((0, 0), (0.3, 0), (0.48, 1, ease_in), (0.75, 0.5), (1.1, 0, smooth), (1.8, 0))


def lunge(t):
    """coil with the crown flashed up, bound in, the nose horn straight in at 0.50 s, flick up, spring back"""
    p = _base()
    ck, go, jb, fl = f(L_COIL, t), f(L_GO, t), f(L_JAB, t), f(L_FLICK, t)
    imp = kick(t, 0.5, 0.09, 0.03)
    flash = math.sin(2 * math.pi * t / 0.26) * ck            # the crown rocks as it coils: the spikes flash
    _breath(p, t, LUNGE_T, 3, 0.7)
    add(p, "body", rot=(2.5 * ck - 2.6 * min(go, 1.0) + 1.2 * fl, 0, 1.5 * flash),
        pos=(0, -0.6 * ck - 0.9 * go - 0.3 * imp, 2.2 * ck - 4.0 * go))
    A.horn_level(p, -0.3 * ck + 0.3 * jb - 0.1 * fl)
    Q.head(p, 11 * ck - 11 * jb + 2 * imp + 14 * fl, 0, 8 * flash - 4 * fl, k=0.6)
    A.jaw(p, -2.5 * ck - 3.0 * fl)
    fd = _fade(t, LUNGE_T)
    Q.trail(p, t, lambda u: fd * (-3.5 * f(L_COIL, u) + 2.5 * min(1.0, f(L_GO, u)) - 1.5 * f(L_FLICK, u)), delay=0.05, axis=0,
            gain=Q.gains(0.5, 0.35))
    Q.trail(p, t, lambda u: fd * 5.0 * math.sin(2 * math.pi * u / 0.42) * (f(L_COIL, u) + f(L_FLICK, u)), delay=0.06)
    push = f(L_PUSH, t)
    return _feet(p, t,
                 fore={"l": ((0.22, 0.49, -5.0, 0.0, 2.8), (1.0, 1.3, 0.0, 0.0, 3.4)),
                       "r": ((0.26, 0.5, -4.5, 0.0, 2.8), (1.12, 1.42, 0.0, 0.0, 3.4))},
                 hind={"l": ((0.55, 0.8, -2.5, 0.0, 3.4), (1.28, 1.58, 0.0, 0.0, 3.0))},
                 meta={"r": 14 * push})            # the left hind skips up: only the right drives


# ------------------------------------------------------------------ parry: the crown takes it, the nose shoves (0.60 s)
P_YAW = tr((0, 0), (0.09, -14, ease_out), (0.25, -11), (0.42, 5, smooth), (0.6, 1, smooth), (1.5, 0, smooth))
P_ROLL = tr((0, 0), (0.09, -24, ease_out), (0.25, -19), (0.42, 6, smooth), (0.6, 2), (1.5, 0, smooth))
P_COCK = tr((0, 0), (0.22, 0), (0.42, 1, ease_out), (0.5, 0.85), (0.6, 0, ease_in), (1.5, 0))
P_GO = tr((0, 0), (0.42, 0), (0.6, 1, smooth), (0.72, 1.05, smooth), (0.92, 0.85), (1.5, 0, back_out))
P_SHOVE = tr((0, 0), (0.46, 0), (0.6, 1, ease_in), (0.7, 0.6, ease_out), (0.95, 0))
P_UP = tr((0, 0), (0.58, 0), (0.7, 1, ease_out), (1.05, 0, smooth))


def parry(t):
    """the crown rolled into the blow (the spikes ring), the rebound cocks the nose horn low, the shove in and up"""
    p = _base()
    yw, rl, ck, go, sv, up = f(P_YAW, t), f(P_ROLL, t), f(P_COCK, t), f(P_GO, t), f(P_SHOVE, t), f(P_UP, t)
    imp = kick(t, 0.1, 0.12, 0.03)
    rg = ring(t, 0.1, 5.0, 0.12)                          # the spikes ring, fast and light
    dfl = -yw / 14.0
    _breath(p, t, PARRY_T, 3, 0.7)
    add(p, "body", rot=(1.8 * ck - 2.2 * min(go, 1.0) + 0.8 * imp, 3.0 * dfl, 3.0 * dfl - 1.5 * imp),
        pos=(0, -0.5 * ck - 0.8 * go, 1.6 * ck - 3.2 * go + 1.0 * imp))
    A.horn_level(p, 0.3 * ck + 0.2 * sv)
    Q.head(p, 5 * imp + 4 * ck - 8 * sv + 12 * up, yw - 2 * rg, rl + 6 * rg, k=0.5)
    A.jaw(p, -2.0 * up)
    fd = _fade(t, PARRY_T)
    Q.trail(p, t, lambda u: fd * (4.0 * f(P_ROLL, u) / 24.0 - 2.5 * f(P_UP, u)), delay=0.06)
    Q.trail(p, t, lambda u: fd * (-2.5 * f(P_COCK, u) + 2.0 * min(1.0, f(P_GO, u))), delay=0.05, axis=0, gain=Q.gains(0.5, 0.35))
    push = f(tr((0, 0), (0.42, 0), (0.6, 1, ease_in), (1.0, 0, smooth)), t)
    return _feet(p, t,
                 fore={"l": ((0.02, 0.3, 0.0, 1.6, 2.8), (0.9, 1.2, 0.0, 0.0, 3.2)),
                       "r": ((0.34, 0.6, -3.5, 0.0, 2.8), (1.05, 1.38, 0.0, 0.0, 3.2))},
                 meta={"l": 12 * push, "r": 12 * push})


# ------------------------------------------------------------------ stagger: parried, light and skittish
S_JOLT = tr((0, 0), (0.14, 1, ease_out), (0.45, 0.8), (1.0, 0.25, smooth), (1.6, 0, smooth))
S_LOST = tr((0, 0), (0.12, 1, ease_out), (0.9, 0.6), (1.5, 0, smooth))


def stagger(t):
    """knocked off line to its left: the forefeet skip sideways together, a hind foot crosses, the crown wobbles
    and pulls the head about; a rattle of the crown at the end and back to the guard"""
    p = _base()
    j, lost = f(S_JOLT, t), f(S_LOST, t)
    wob = ring(t, 0.06, 2.1, 0.32)
    sh = ring(t, 1.0, 4.6, 0.11)                        # the crown rattled (head_shake)
    hop = math.sin(math.pi * smooth((t - 0.1) / 0.32)) if 0.1 < t < 0.42 else 0.0
    _breath(p, t, STAGGER_T, 4, 1.0)
    add(p, "body", rot=(1.0 * hop - 1.0 * wob, -6.0 * j - 2.0 * wob, -7.0 * j - 2.5 * wob),
        pos=(1.4 * j, -0.6 * j + 0.4 * hop, 1.2 * j))
    A.horn_level(p, -0.5 * lost)
    Q.head(p, 14 * j + 5 * wob, 16 * j + 9 * wob - 3 * sh, -12 * j - 10 * wob + 12 * sh, k=0.5)
    A.jaw(p, -3.5 * f(tr((0, 0), (0.12, 1, ease_out), (0.5, 0.3), (1.0, 0)), t))
    fd = _fade(t, STAGGER_T)
    Q.trail(p, t, lambda u: fd * (6.0 * f(S_JOLT, u) + 4.0 * ring(u, 0.06, 2.1, 0.4)), delay=0.06)
    Q.trail(p, t, lambda u: fd * -2.0 * f(S_JOLT, u), delay=0.05, axis=0, gain=Q.gains(0.5, 0.35))
    return _feet(p, t,
                 fore={"l": ((0.1, 0.4, 0.0, 2.2, 3.0), (0.92, 1.2, 0.0, 0.0, 3.0)),
                       "r": ((0.12, 0.42, 0.0, 2.0, 3.0), (1.05, 1.34, 0.0, 0.0, 3.0))},
                 hind={"r": ((0.3, 0.6, 0.6, 1.8, 3.2), (1.12, 1.42, 0.0, 0.0, 3.0)),
                       "l": ((0.42, 0.8, 0.4, 1.2, 0.0), (1.22, 1.52, 0.0, 0.0, 3.0))})


ANIMS = {
    "lunge": (lunge, LUNGE_T, False, "Duelo", "o bote do esgrimista: a coroa relampeja, a frente salta, o chifre do nariz entra em 0,5 s e dá um tranco para cima"),
    "parry": (parry, PARRY_T, False, "Duelo", "a coroa de espinhos recebe o golpe (vibram), o chifre do nariz arma baixo e empurra para cima em 0,6 s"),
    "stagger": (stagger, STAGGER_T, False, "Duelo", "aparado: patas da frente pulam de lado, uma de trás cruza, a coroa balança e chacoalha no fim"),
}
