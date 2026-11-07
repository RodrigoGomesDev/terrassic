"""Triceratops: the three moves of the epic duel (06/11/2026): lunge, parry, stagger, with the fixed lengths the
generic Java duel expects (LUNGE_T 1.8 s, the hit at 0.50 s; PARRY_T 1.5 s, the counter at 0.60 s; STAGGER_T 1.6 s).

From its own body and its own study (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md; Farke et al. 2009): it fights
FRONT ON, never side on, the brow horns levelled and the frill standing firm behind them like a shield (the frill
never flaps: it is bone). 9 m and 6 t: what makes it epic is the mass behind a SHORT move.
  * lunge: it rocks back onto its haunches with the horns cocked and the tail up, then a short burst from the hind
    legs (the heels come up as they drive) with six tonnes behind the horns, a forefoot slammed ahead to take the
    weight, the horns driving in (0.50 s) and hooking UP and to the side; a hind foot dragged up behind, the tail
    whipping late, and a heavy settle back into the guard;
  * parry: it turns the head hard so the blow lands on a brow horn and the frill (dry, fast, the body twisting
    under it, a forefoot bracing out), uses the swing back to cock the horns low, and stabs straight in (0.60 s);
  * stagger: knocked off line, the whole barrel tips, the heavy head swings like a bell on its short neck and pulls
    the body after it, the four feet stumble (a forefoot crossing over, a hind foot dragged), the tail swings
    out to catch the weight, a slow heavy shake of the head and back to the guard.
Every move starts and ends on the guard's own pose (trikeflow.guard at t = 0), so the change of animation does not
snap. Signs as in ceraflow.py.
"""
import math

import ceraflow as C
import triceranims as A
import trikeflow as FL
from anim2 import add, smooth, ease_in, ease_out, back_out

tr, f, bump, ring, kick = C.tr, C.f, C.bump, C.ring, C.kick
Q = FL.Q
SIDES = A.SIDES
LUNGE_T, PARRY_T, STAGGER_T = 1.8, 1.5, 1.6
LEGS = ("thigh", "shin", "foot", "toes", "arm", "forearm", "hand")
G_FORE, G_HIND, G_FDX = (-2.5, -2.5), (1.0, 1.0), (1.0, -1.0)        # the guard's stance (trikeflow.guard)
_G0 = {b: v for b, v in FL.guard(0.0).items() if not b.startswith(LEGS)}


def _base():
    """the guard's upper pose at t = 0 (body, neck, skull, jaw, tail), the start and the end of every move"""
    return {b: ([*v[0]], [*v[1]]) + tuple(v[2:]) for b, v in _G0.items()}


def _breath(p, t, L, n, k=1.0):
    """a breath with whole cycles in the move, zero at both ends (the guard's pose is not disturbed there)"""
    b = math.sin(2 * math.pi * n * t / L) * math.sin(math.pi * t / L)
    add(p, "body", rot=(0.4 * k * b, 0, 0))
    add(p, "neck", rot=(-0.4 * k * b, 0, 0))


def _fade(t, L):
    """the tail's delayed layers must be spent before the end (the tip reads them 0.4 s late)"""
    return 1.0 - smooth((t - (L - 0.55)) / 0.45)


def _feet(p, t, fore=None, hind=None, meta=None):
    fore, hind, meta = fore or {}, hind or {}, meta or {}
    Q.counter_legs(p)
    Q.lift(p, 0.3)                                     # continuous (ceraflow.Quad.lift)
    for i, s in enumerate(SIDES):
        Q.plan(p, t, s, "h", hind.get(s, ()), base=(G_HIND[i], 0.0), meta=meta.get(s, 0.0))
        Q.plan(p, t, s, "f", fore.get(s, ()), base=(G_FORE[i], G_FDX[i]))
    return p


# ------------------------------------------------------------------ lunge: the committed charge (hit 0.50 s)
L_BACK = tr((0, 0), (0.3, 1, ease_out), (0.36, 0.92), (0.49, 0, ease_in), (1.8, 0))
L_GO = tr((0, 0), (0.3, 0), (0.52, 1, smooth), (0.7, 1.08, smooth), (0.9, 1.0), (1.8, 0, back_out))   # the body: no stop dead
                                                                                    # (the pillar legs would flip)
L_DRIVE = tr((0, 0), (0.36, 0), (0.5, 1, ease_in), (0.57, 0.45, ease_out), (0.8, 0))
L_HOOK = tr((0, 0), (0.5, 0), (0.64, 1, ease_out), (0.8, 0.85), (1.35, 0, smooth), (1.8, 0))
L_PUSH = tr((0, 0), (0.34, 0), (0.48, 1, ease_in), (0.8, 0.55), (1.2, 0, smooth), (1.8, 0))


def lunge(t):
    """rock back, burst from the hind legs, horns in at 0.50 s, hook up and aside, the weight on, settle"""
    p = _base()
    bk, go, dr, hk = f(L_BACK, t), f(L_GO, t), f(L_DRIVE, t), f(L_HOOK, t)
    imp = kick(t, 0.5, 0.12, 0.03)                       # the jolt of the hit runs back through the body
    _breath(p, t, LUNGE_T, 2, 0.8)
    add(p, "body", rot=(3.0 * bk - 3.0 * min(go, 1.0) + 1.5 * hk, -2.0 * bk + 3.0 * hk, 1.2 * bk + 2.5 * hk),
        pos=(0, -1.0 * bk - 1.4 * go - 0.4 * imp, 2.8 * bk - 4.2 * go))
    A.horns(p, 0.25 * bk + 0.1 * dr - 0.25 * hk)
    Q.head(p, 4 * bk - 9 * dr + 3 * imp + 26 * hk, -5 * bk + 9 * hk, 4 * bk - 15 * hk, k=0.5)
    A.jaw(p, -1.5 * kick(t, 0.12, 0.1, 0.03) - 2.0 * hk - 1.2 * kick(t, 1.3, 0.08, 0.03))   # snorts, the gasp of the toss
    fd = _fade(t, LUNGE_T)
    Q.trail(p, t, lambda u: fd * (-4.0 * f(L_BACK, u) + 2.5 * min(1.0, f(L_GO, u))), delay=0.07, axis=0, gain=Q.gains(0.5, 0.3))
    Q.trail(p, t, lambda u: fd * (2.0 * f(L_BACK, u) + 6.0 * f(L_HOOK, u)), delay=0.08)
    push = f(L_PUSH, t)
    return _feet(p, t,
                 fore={"l": ((0.28, 0.5, -6.0, 0.0, 3.2), (1.05, 1.42, 0.0, 0.0, 3.5))},
                 hind={"r": ((0.56, 0.86, -3.5, 0.0, 3.0), (1.25, 1.62, 0.0, 0.0, 3.0))},
                 meta={"l": 16 * push})            # the right hind steps up: only the left drives


# ------------------------------------------------------------------ parry: horn and frill take it, then the stab (0.60 s)
P_YAW = tr((0, 0), (0.1, 24, ease_out), (0.25, 20), (0.42, -8, smooth), (0.6, -3, smooth), (0.85, 2), (1.5, 0, smooth))
P_ROLL = tr((0, 0), (0.1, 20, ease_out), (0.25, 16), (0.42, -6, smooth), (0.6, -2), (1.5, 0, smooth))
P_LOAD = tr((0, 0), (0.2, 0), (0.42, 1, ease_out), (0.5, 0.9), (0.6, 0, ease_in), (1.5, 0))
P_GO = tr((0, 0), (0.44, 0), (0.6, 1, ease_in), (0.7, 1.05, ease_out), (0.9, 0.85), (1.5, 0, back_out))
P_STAB = tr((0, 0), (0.46, 0), (0.6, 1, ease_in), (0.66, 0.4, ease_out), (0.85, 0))
P_HOOK = tr((0, 0), (0.6, 0), (0.72, 1, ease_out), (1.1, 0, smooth))


def parry(t):
    """the head turned hard into the blow (a horn and the frill), the swing back cocks the horns, the stab in"""
    p = _base()
    yw, rl, ld, go, st, hk = f(P_YAW, t), f(P_ROLL, t), f(P_LOAD, t), f(P_GO, t), f(P_STAB, t), f(P_HOOK, t)
    imp = kick(t, 0.11, 0.14, 0.03); rg = ring(t, 0.12, 3.0, 0.18)
    dfl = yw / 24.0
    _breath(p, t, PARRY_T, 2, 0.8)
    add(p, "body", rot=(2.0 * ld - 2.5 * min(go, 1.0) + 1.0 * imp, -4.0 * dfl, -3.0 * dfl + 1.5 * imp),
        pos=(0, -0.6 * ld - 1.0 * go, 1.8 * ld - 3.5 * go + 1.0 * imp))
    A.horns(p, 0.2 * ld + 0.1 * st)
    Q.head(p, 6 * imp + 4 * ld - 9 * st + 10 * hk + 2 * rg, yw + 3 * rg, rl + 4 * rg, k=0.5)
    A.jaw(p, -1.5 * kick(t, 0.6, 0.12, 0.03))
    fd = _fade(t, PARRY_T)
    Q.trail(p, t, lambda u: fd * (-4.0 * f(P_YAW, u) / 24.0 + 3.0 * f(P_HOOK, u)), delay=0.08)
    Q.trail(p, t, lambda u: fd * (-2.5 * f(P_LOAD, u) + 2.0 * min(1.0, f(P_GO, u))), delay=0.07, axis=0, gain=Q.gains(0.5, 0.3))
    push = f(tr((0, 0), (0.44, 0), (0.6, 1, ease_in), (1.0, 0, smooth)), t)
    return _feet(p, t,
                 fore={"r": ((0.03, 0.3, -0.5, -1.6, 3.0), (0.95, 1.3, 0.0, 0.0, 3.0)),
                       "l": ((0.38, 0.6, -4.0, 0.0, 3.0), (1.08, 1.45, 0.0, 0.0, 3.0))},
                 meta={"l": 14 * push, "r": 14 * push})


# ------------------------------------------------------------------ stagger: parried, off balance
S_JOLT = tr((0, 0), (0.16, 1, ease_out), (0.5, 0.85), (1.1, 0.3, smooth), (1.6, 0, smooth))
S_LOST = tr((0, 0), (0.12, 1, ease_out), (1.0, 0.7), (1.6, 0, smooth))


def stagger(t):
    """thrown off line to its right: the barrel tips, the head swings like a bell and drags the body, a forefoot
    crosses over, a hind foot drags, the tail swings out; a heavy shake and back to the guard"""
    p = _base()
    j, lost = f(S_JOLT, t), f(S_LOST, t)
    sway = ring(t, 0.08, 1.25, 0.42)                    # the heavy head, a bell on a short neck
    sh = ring(t, 1.05, 2.6, 0.14)                       # the shake at the end
    _breath(p, t, STAGGER_T, 3, 1.0)
    add(p, "body", rot=(-1.5 * j - 1.2 * sway, 5.0 * j + 2.0 * sway, 6.0 * j + 2.5 * sway),
        pos=(-1.6 * j, -0.8 * j, 1.4 * j))
    A.horns(p, -0.55 * lost)
    Q.head(p, 12 * j + 4 * sway, -16 * j - 9 * sway + 4 * sh, 10 * j + 8 * sway + 10 * sh, k=0.5)
    A.jaw(p, -4.0 * f(tr((0, 0), (0.15, 1, ease_out), (0.6, 0.3), (1.2, 0)), t))
    fd = _fade(t, STAGGER_T)
    Q.trail(p, t, lambda u: fd * (-5.0 * f(S_JOLT, u) - 4.0 * ring(u, 0.08, 1.25, 0.5)), delay=0.08)
    Q.trail(p, t, lambda u: fd * 2.0 * f(S_JOLT, u), delay=0.07, axis=0, gain=Q.gains(0.5, 0.3))
    return _feet(p, t,
                 fore={"r": ((0.1, 0.42, -0.5, -2.4, 3.5), (0.95, 1.28, 0.0, 0.0, 3.0)),
                       "l": ((0.32, 0.66, 0.5, -2.0, 3.0), (1.12, 1.46, 0.0, 0.0, 3.0))},
                 hind={"r": ((0.4, 0.72, 1.0, -1.6, 3.0), (1.18, 1.5, 0.0, 0.0, 2.5)),
                       "l": ((0.5, 0.95, 0.6, -1.2, 0.0), (1.25, 1.58, 0.0, 0.0, 2.5))})


ANIMS = {
    "lunge": (lunge, LUNGE_T, False, "Duelo", "o bote: senta nos quadris, arranca curto com 6 t atrás, chifres entram em 0,5 s e engancham para cima"),
    "parry": (parry, PARRY_T, False, "Duelo", "apara com o chifre e o babado (cabeça virada seca), aproveita o giro e estoca em 0,6 s"),
    "stagger": (stagger, STAGGER_T, False, "Duelo", "aparado: o corpo tomba de lado, a cabeça pesada balança como sino, as patas tropeçam"),
}
