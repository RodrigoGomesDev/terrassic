"""Protoceratops: the three moves of the epic duel (06/11/2026): lunge, parry, stagger, with the fixed lengths the
generic Java duel expects (LUNGE_T 1.8 s, the bite at 0.50 s; PARRY_T 1.5 s, the counter bite at 0.60 s;
STAGGER_T 1.6 s).

From its own body and its own study (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md): the "Fighting Dinosaurs" of
1971, the Velociraptor's arm caught and crushed in its beak. No horns: a parrot's beak that bites and HOLDS, a bony
frill to shove with, a tall tail; 2 m, low on short legs, small and stubborn.
  * lunge: it sinks into a crouch with the beak gaping and the sail of the tail raised, then darts in LOW, the head
    under the rival's guard, the forefeet scuttling, the beak snapping shut at 0.50 s and staying shut: it holds,
    braced back on its hind legs, and wrenches the head twice to tear, lets go and backs into its crouch;
  * parry: it ducks the frill into the blow and heaves it aside (the shield), the head swings round with the beak
    opening, and bites (0.60 s), a short tug, back on guard;
  * stagger: light, it is knocked well off its feet: a quick sideways skip of the forefeet, a hind foot hopping and
    the other dragged, the sail flagging, a fast shake of the head, and it is back in its crouch before the others.
Every move starts and ends on the guard's own pose (protoflow.guard at t = 0). Signs as in triceratops/ceraflow.py.
"""
import math

import ceraflow as C
import protoanims as A
import protoflow as FL
from anim2 import add, smooth, ease_in, ease_out, back_out

tr, f, bump, ring, kick = C.tr, C.f, C.bump, C.ring, C.kick
Q = FL.Q
SIDES = A.SIDES
shield = FL.shield
LUNGE_T, PARRY_T, STAGGER_T = 1.8, 1.5, 1.6
LEGS = ("thigh", "shin", "foot", "toes", "arm", "forearm", "hand")
G_FORE, G_HIND, G_FDX = (-1.0, -1.0), (0.8, 0.8), (0.5, -0.5)        # the guard's stance (protoflow.guard)
_G0 = {b: v for b, v in FL.guard(0.0).items() if not b.startswith(LEGS)}


def _base():
    return {b: ([*v[0]], [*v[1]]) + tuple(v[2:]) for b, v in _G0.items()}


def _breath(p, t, L, n, k=1.0):
    b = math.sin(2 * math.pi * n * t / L) * math.sin(math.pi * t / L)
    add(p, "body", rot=(0.5 * k * b, 0, 0))
    add(p, "neck", rot=(-0.5 * k * b, 0, 0))


def _fade(t, L):
    return 1.0 - smooth((t - (L - 0.45)) / 0.38)


def _feet(p, t, fore=None, hind=None, meta=None):
    fore, hind, meta = fore or {}, hind or {}, meta or {}
    Q.counter_legs(p)
    Q.lift(p, 0.3)                                     # continuous (ceraflow.Quad.lift)
    for i, s in enumerate(SIDES):
        Q.plan(p, t, s, "h", hind.get(s, ()), base=(G_HIND[i], 0.0), meta=meta.get(s, 0.0))
        Q.plan(p, t, s, "f", fore.get(s, ()), base=(G_FORE[i], G_FDX[i]))
    return p


# ------------------------------------------------------------------ lunge: the low dart, the bite that holds (0.50 s)
L_SINK = tr((0, 0), (0.3, 1, ease_out), (0.36, 0.95), (0.48, 0, ease_in), (1.8, 0))
L_GO = tr((0, 0), (0.3, 0), (0.53, 1, smooth), (0.62, 1.05, smooth), (0.9, 0.8), (1.8, 0, back_out))
L_DIVE = tr((0, 0), (0.34, 0), (0.5, 1, ease_in), (0.56, 0.8, ease_out), (0.95, 0.6), (1.3, 0, smooth))
L_PULL = tr((0, 0), (0.52, 0), (0.66, 1, ease_out), (0.95, 1), (1.25, 0, smooth))
# the beak (on top of the guard's half-open -9): gapes to -31, snaps shut at 0.50 s and stays shut, lets go
L_JAW = tr((0, 0), (0.3, -22, ease_out), (0.42, -23), (0.5, 9, ease_in), (0.98, 9), (1.1, -6, ease_out), (1.45, 0, smooth))


def lunge(t):
    """crouch with the beak agape, dart in low, snap shut at 0.50 s and hold, two wrenches, let go, back off"""
    p = _base()
    sk, go, dv, pl = f(L_SINK, t), f(L_GO, t), f(L_DIVE, t), f(L_PULL, t)
    imp = kick(t, 0.5, 0.08, 0.02)
    wr = C.window(t, 0.62, 0.95, 0.07) * math.sin(2 * math.pi * (t - 0.62) / 0.17)
    _breath(p, t, LUNGE_T, 4, 0.8)
    add(p, "body", rot=(1.5 * sk - 2.0 * min(go, 1.0) + 1.0 * pl, 2.0 * wr, -2.5 * wr),
        pos=(0, -1.0 * sk - 0.6 * go - 0.6 * dv - 0.3 * imp, 1.8 * sk - 3.4 * go + 1.4 * pl))
    shield(p, 0.35 * sk - 0.3 * dv)
    Q.head(p, 5 * sk - 3 * dv + 1 * imp + 3 * pl, 9 * wr, 13 * wr, k=0.6)
    jd = f(L_JAW, t)
    A.jaw(p, jd)
    add(p, "neck", rot=(0.45 * max(0.0, -jd), 0, 0))       # the gaping beak carried clear of the ground
    fd = _fade(t, LUNGE_T)
    Q.trail(p, t, lambda u: fd * (-4.0 * f(L_SINK, u) + 2.5 * min(1.0, f(L_GO, u))), delay=0.05, axis=0, gain=Q.gains(0.5, 0.4))
    Q.trail(p, t, lambda u: fd * -4.0 * C.window(u, 0.62, 0.95, 0.07) * math.sin(2 * math.pi * (u - 0.62) / 0.17), delay=0.05)
    brace = f(tr((0, 0), (0.3, 0), (0.5, 1, smooth), (0.66, 0.7), (0.95, 0.9), (1.25, 0, smooth)), t)
    return _feet(p, t,
                 fore={"l": ((0.2, 0.48, -3.2, 0.0, 2.0), (0.96, 1.26, 0.0, 0.0, 2.0)),
                       "r": ((0.23, 0.5, -3.0, 0.0, 2.0), (1.1, 1.4, 0.0, 0.0, 2.0))},
                 hind={"r": ((0.52, 0.82, -1.5, 0.0, 2.0), (1.24, 1.52, 0.0, 0.0, 2.0))},
                 meta={"l": 16 * brace})            # the right hind steps up: only the left drives


# ------------------------------------------------------------------ parry: the frill heaves it aside, then the bite (0.60 s)
P_DUCK = tr((0, 0), (0.08, 1, ease_out), (0.24, 0.8), (0.42, 0, smooth), (1.5, 0))
P_HEAVE = tr((0, 0), (0.12, 1, ease_out), (0.3, 0.3), (0.45, 0, smooth))
P_YAW = tr((0, 0), (0.1, 14, ease_out), (0.25, 11), (0.44, -5, smooth), (0.6, 0, smooth), (1.5, 0))
P_GO = tr((0, 0), (0.42, 0), (0.63, 1, smooth), (0.72, 1.04, smooth), (0.9, 0.8), (1.5, 0, back_out))
P_DART = tr((0, 0), (0.46, 0), (0.6, 1, ease_in), (0.66, 0.6, ease_out), (0.95, 0))
P_JAW = tr((0, 0), (0.26, 0), (0.46, -22, ease_out), (0.6, 9, ease_in), (0.85, 8), (1.0, -3, ease_out), (1.3, 0, smooth))


def parry(t):
    """the frill ducked into the blow and heaved aside, the head swinging round with the beak open, the bite"""
    p = _base()
    dk, hv, yw, go, dt = f(P_DUCK, t), f(P_HEAVE, t), f(P_YAW, t), f(P_GO, t), f(P_DART, t)
    imp = kick(t, 0.08, 0.1, 0.03)
    tug = C.window(t, 0.66, 0.9, 0.06) * math.sin(2 * math.pi * (t - 0.66) / 0.24)
    _breath(p, t, PARRY_T, 3, 0.8)
    add(p, "body", rot=(1.5 * hv - 1.8 * min(go, 1.0), -0.25 * yw + 2 * tug, -0.3 * yw + 2.5 * imp),
        pos=(-0.6 * imp, -0.6 * dk - 0.5 * go - 0.5 * dt, 1.2 * imp - 2.6 * go))
    shield(p, 0.6 * dk)
    Q.head(p, 2 * imp + 8 * hv - 3 * dt, yw + 6 * tug, 0.7 * yw + 8 * tug, k=0.6)
    jd = f(P_JAW, t)
    A.jaw(p, jd)
    add(p, "neck", rot=(0.45 * max(0.0, -jd), 0, 0))
    fd = _fade(t, PARRY_T)
    Q.trail(p, t, lambda u: fd * (-3.0 * f(P_YAW, u) / 14.0 - 3.0 * C.window(u, 0.66, 0.9, 0.06) * math.sin(2 * math.pi * (u - 0.66) / 0.24)), delay=0.05)
    Q.trail(p, t, lambda u: fd * (-2.5 * f(P_HEAVE, u) + 2.0 * min(1.0, f(P_GO, u))), delay=0.05, axis=0, gain=Q.gains(0.5, 0.4))
    push = f(tr((0, 0), (0.4, 0), (0.6, 1, smooth), (0.95, 0, smooth)), t)
    return _feet(p, t,
                 fore={"r": ((0.02, 0.3, 0.0, -1.2, 1.8), (0.34, 0.6, -2.2, 0.0, 2.0), (0.98, 1.28, 0.0, 0.0, 2.0)),
                       "l": ((0.32, 0.6, -2.2, 0.0, 2.0), (1.08, 1.38, 0.0, 0.0, 2.0))},
                 meta={"l": 14 * push, "r": 14 * push})


# ------------------------------------------------------------------ stagger: light, quick, off its feet
S_JOLT = tr((0, 0), (0.12, 1, ease_out), (0.4, 0.7), (0.85, 0.15, smooth), (1.3, 0, smooth), (1.6, 0))
S_LOST = tr((0, 0), (0.1, 1, ease_out), (0.7, 0.5), (1.25, 0, smooth), (1.6, 0))


def stagger(t):
    """knocked hard to its right: the forefeet skip sideways, a hind foot hops and the other drags, the sail flags,
    a fast shake of the head at 0.75 s, and it is back in its crouch by 1.3 s"""
    p = _base()
    j, lost = f(S_JOLT, t), f(S_LOST, t)
    wob = ring(t, 0.05, 2.8, 0.25)
    sh = ring(t, 0.72, 6.0, 0.11)
    _breath(p, t, STAGGER_T, 5, 1.0)
    add(p, "body", rot=(-1.0 * j, 6.0 * j + 2.0 * wob, 10.0 * j + 3.0 * wob), pos=(-2.0 * j, -0.5 * j, 1.0 * j))
    shield(p, -0.6 * lost)
    Q.head(p, 10 * j + 4 * wob, -20 * j - 8 * wob + 5 * sh, 8 * j + 6 * wob + 14 * sh, k=0.6)
    A.jaw(p, 7.0 * lost - 4.0 * bump(t, 0.75, 0.08))       # the beak clamps on the jolt, gasps in the shake
    fd = _fade(t, STAGGER_T)
    Q.trail(p, t, lambda u: fd * (-7.0 * f(S_JOLT, u) - 5.0 * ring(u, 0.05, 2.8, 0.3)), delay=0.05)
    Q.trail(p, t, lambda u: fd * -3.0 * f(S_LOST, u), delay=0.05, axis=0, gain=Q.gains(0.5, 0.4))
    return _feet(p, t,
                 fore={"r": ((0.06, 0.3, 0.0, -2.0, 2.2), (0.8, 1.04, 0.0, 0.0, 2.2)),
                       "l": ((0.1, 0.34, 0.0, -1.8, 2.2), (0.9, 1.14, 0.0, 0.0, 2.2))},
                 hind={"r": ((0.16, 0.4, 0.4, -1.6, 2.2), (0.98, 1.22, 0.0, 0.0, 2.0)),
                       "l": ((0.3, 0.62, 0.3, -1.0, 0.0), (1.06, 1.3, 0.0, 0.0, 2.0))})


ANIMS = {
    "lunge": (lunge, LUNGE_T, False, "Duelo", "o bote baixo: agacha de bico aberto, dispara por baixo, o bico fecha em 0,5 s e PRENDE, torce duas vezes e solta"),
    "parry": (parry, PARRY_T, False, "Duelo", "o babado empurra o golpe para o lado, a cabeça volta de bico aberto e morde em 0,6 s"),
    "stagger": (stagger, STAGGER_T, False, "Duelo", "aparado: leve, sai do lugar, patas pulam de lado, uma arrasta, sacode a cabeça rápido"),
}
