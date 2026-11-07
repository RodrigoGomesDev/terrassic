"""T. rex: the epic duel (06/11/2026). Rodrigo found the fights "muito estáticas, monótonas" and asked for something
dynamic and epic, after the Raxiores duel (studied in fight_study.md: ideas only). The new duel (Java) holds both in
GUARD side-on, circling, and strings JAB, LUNGE, PARRY and STAGGER; these are the three new moves, fixed lengths because
the Java is generic (LUNGE_T, PARRY_T, STAGGER_T, hit at 0.50 s in the lunge and 0.60 s in the parry).

What makes them the T. rex's (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md, its row):
  * LUNGE = the bone-crushing bite (Gignac & Erickson 2017): the 9 t animal rears back on the rear leg with the jaws
    gaping, then throws its whole weight in, the front foot taking it, and the jaws shut at 0.50 s; it does not shake
    (the Giganotosaurus cuts, the Carnotaurus butts): it BEARS DOWN, the neck pressing and the body sinking onto the
    bite with the jaw trembling under the force, then lets go and backs onto its guard;
  * PARRY = the bite marks on the faces of other tyrannosaurs (Peterson et al. 2009): it takes the incoming bite on the
    side of the head and the shoulder, the head swung aside and the chest turned into it, and the twist it got carries
    the head round into a bite to the rival's FACE (high, from the side) at 0.60 s, with a short tug before it lets go;
  * STAGGER = a heavy body thrown off balance: the hips lurch to its right, the head is flung the other way late and
    heavily, the left foot crosses over to catch the weight, the right drags its toes, the long tail swings out wide
    to bring it back, and a slow shake of the head clears it. It never falls.
Same rules as the fluid set (rexflow.py): breathing under all, envelopes instead of switches, three beats with a
back_out settle, the tail following late. All three start and end on the guard's stance (rexduel.guard at rest).
"""
import math

from anim2 import add, smooth, ease_in, ease_out, back_out
import rexanims as A
import rexflow as F

SIDES = A.SIDES
tr = A.tr
window = A.window
plant = A.plant
wave, tremor, trail, alive, alive_upper = F.wave, F.tremor, F.trail, F.alive, F.alive_upper

LUNGE_T = 1.8
PARRY_T = 1.5
STAGGER_T = 1.6
GUARD_DZ = {"l": 2.0, "r": -3.0}        # rexduel.guard: the left foot back, the right forward


def bump(t, c, w):
    return math.exp(-((t - c) / w) ** 2)


def decay(t, at, tau, f):
    """a wobble that starts at `at` and dies out (eased in so it never pops)"""
    return math.exp(-max(0.0, t - at) / tau) * math.sin(2 * math.pi * f * (t - at)) * smooth((t - at + 0.02) / 0.05)


def jolt(t, at, tau, rise=0.03):
    """the jolt of an impact: up in `rise` s, dying over `tau`"""
    return math.exp(-max(0.0, t - at) / tau) * smooth((t - at + rise) / rise)


def arch(t, a, b, h):
    u = min(1.0, max(0.0, (t - a) / (b - a)))
    return h * math.sin(math.pi * u) ** 1.3


def stance(p):
    """the guard at rest (rexduel.guard without its loops): low, head forward, mouth ajar, tail up"""
    add(p, "body", rot=(6, 0, 0), pos=(0, -3.2, 0))
    add(p, "neck", rot=(-9, 0, 0)); add(p, "skull", rot=(5, 0, 0)); add(p, "jaw", rot=(-7, 0, 0))
    for i in range(1, 5):
        add(p, f"tail{i}", rot=(2.5 * (0.5 + 0.3 * i), 0, 0))
    for s, _ in SIDES:
        add(p, f"arm_{s}", rot=(-12, 0, 0)); add(p, f"forearm_{s}", rot=(16, 0, 0))


def legs_under(p, yaw, roll, extra=None):
    """the thighs cancel the body's yaw and roll (the planted feet stay put) and keep the guard's straddle"""
    for s, _ in SIDES:
        sx = 1 if s == "l" else -1
        add(p, f"thigh_{s}", rot=(0, -yaw, -roll + 3.0 * sx + (extra or {}).get(s, 0.0)))


# ------------------------------------------------------------------ LUNGE: rear back, throw the weight in, crush
L_LOAD = tr((0, 0), (0.33, 1, ease_out), (0.42, 0.6), (0.5, 0, ease_in), (1.8, 0))
L_GO = tr((0, 0), (0.35, 0), (0.5, 1, ease_in), (0.66, 1.12, ease_out), (0.9, 1.0), (1.55, 0, back_out), (1.8, 0))
L_JAW = tr((0, 0), (0.1, -4), (0.36, -50, ease_out), (0.45, -54), (0.5, -1, ease_in), (0.92, -2.5), (1.06, -16, ease_out),
           (1.3, -6), (1.8, 0, smooth))
L_PRESS = tr((0, 0), (0.52, 0), (0.7, 1, ease_out), (0.88, 0.9), (1.1, 0, smooth), (1.8, 0))


def lunge(t):
    p = {}
    stance(p)
    load = float(L_LOAD(t)); go = float(L_GO(t)); press = float(L_PRESS(t))
    hit = jolt(t, 0.5, 0.11)
    crush = tremor(t, (13.7, 19.3, 8.9), (1.0, 0.6, 0.4)) * window(t, 0.52, 0.92, 0.06)    # the jaw straining shut
    roll = -2.5 * go
    add(p, "body", rot=(4 * load - 9 * go + 1.5 * hit - 1.5 * press, 0, roll),
        pos=(0, -1.6 * load - 2.0 * go - 1.0 * press + 0.6 * hit, 3.0 * load - 6.0 * go + 1.2 * hit))
    cock = smooth(t / 0.3) * (1 - smooth((t - 0.38) / 0.1))                 # the head rears up as the jaws spread
    add(p, "neck", rot=(9 * load + 3 * cock - 17 * go + 3 * hit - 5 * press + 0.5 * crush, 0, -0.6 * roll))
    add(p, "skull", rot=(5 * load - 5 * go + 5 * hit - 2 * press + 0.7 * crush, 0, 4 * press))     # a twist bearing down
    add(p, "jaw", rot=(float(L_JAW(t)) + 0.9 * crush, 0, 0))
    # the tail lifts as the counterweight of the head going in, late and growing to the tip, and swings after the hit
    trail(p, t, lambda u: -2.5 * float(L_LOAD(u)) - 3.5 * float(L_GO(u)), gain=(0.5, 0.8, 1.1, 1.4), axis=0, delay=0.07)
    trail(p, t, lambda u: 5 * decay(u, 0.5, 0.3, 1.6) + 2.0 * float(L_GO(u)), gain=(0.5, 0.9, 1.4, 2.0), delay=0.07)
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(-3 * load - 8 * go + 6 * hit, 0, 0))
        add(p, f"forearm_{s}", rot=(-4 * go + 8 * jolt(t, 0.54, 0.12), 0, 0))
    alive(p, t, k=0.4)
    legs_under(p, 0.0, roll)
    # the front (right) foot strides in and takes the weight at the hit; it steps back under the guard in the recovery
    r_up = arch(t, 0.3, 0.5, 7.0) + arch(t, 1.02, 1.45, 5.0)
    r_z = GUARD_DZ["r"] - 8 * smooth((t - 0.3) / 0.2) + 8 * smooth((t - 1.02) / 0.43)
    plant(p, "r", r_up, r_z, 10 * math.sin(math.pi * min(1, max(0, (t - 0.3) / 0.2))), -18 * min(1.0, r_up / 7.0),
          clear=0.8 * min(1.0, r_up / 3.0) - 0.05)
    # the rear (left) leg drives: the heel comes up and the leg straightens behind the body
    push = smooth((t - 0.33) / 0.17) * (1 - smooth((t - 0.95) / 0.6))
    plant(p, "l", 0.0, GUARD_DZ["l"] + 3 * push, 24 * push, 10 * push)
    return p


# ------------------------------------------------------------------ PARRY: take it on the side of the head, bite the face
P_YAW = tr((0, 0), (0.1, -1, ease_out), (0.25, -0.85), (0.43, -1.1, smooth), (0.6, 0.38, ease_in), (0.8, 0.28),
           (1.5, 0, back_out))
P_UP = tr((0, 0), (0.1, 1, ease_out), (0.43, 1.2), (0.6, 0.3, ease_in), (0.85, 0.1), (1.5, 0, smooth))
P_JAW = tr((0, 0), (0.08, -12, ease_out), (0.22, -8), (0.32, -18), (0.5, -52, ease_out), (0.54, -53), (0.6, -1, ease_in),
           (0.9, -3), (1.02, -16, ease_out), (1.22, -6), (1.5, 0, smooth))
P_IN = tr((0, 0), (0.4, 0.2), (0.6, 1, ease_in), (0.75, 1.05), (1.5, 0, back_out))


def parry(t):
    p = {}
    stance(p)
    yw = float(P_YAW(t)); up = float(P_UP(t)); fwd = float(P_IN(t))
    defl = jolt(t, 0.09, 0.14)                      # the incoming bite meets the side of the head and the shoulder
    hit = jolt(t, 0.6, 0.1)
    tug = bump(t, 0.74, 0.07)                       # it pulls once at the face it holds
    byaw = 9 * yw
    broll = 5 * defl - 2 * fwd
    add(p, "body", rot=(-2 * defl - 2 * fwd, byaw, broll), pos=(0, -0.8 * defl - 0.8 * fwd, 1.5 * defl - 3.5 * fwd + 1.5 * tug))
    add(p, "neck", rot=(8 * up + 3 * hit, 22 * yw - 4 * tug, -6 * defl))
    add(p, "skull", rot=(4 * up + 4 * hit, 9 * yw - 5 * tug, -12 * defl + 8 * smooth((t - 0.45) / 0.15) * (1 - smooth((t - 0.9) / 0.4))))
    add(p, "jaw", rot=(float(P_JAW(t)), 0, 0))
    trail(p, t, lambda u: -0.8 * 9 * float(P_YAW(u)) + 6 * decay(u, 0.1, 0.25, 2.0), gain=(0.5, 0.9, 1.4, 2.0), delay=0.07)
    trail(p, t, lambda u: -2.0 * float(P_UP(u)), gain=(0.5, 0.7, 0.9, 1.1), axis=0, delay=0.07)
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(-5 * fwd + 6 * defl, 0, 0)); add(p, f"forearm_{s}", rot=(5 * hit, 0, 0))
    alive(p, t, k=0.4)
    # the left foot steps out to brace against the blow, then back; the right holds
    l_up = arch(t, 0.02, 0.26, 4.0) + arch(t, 0.95, 1.3, 3.0)
    side = 4.0 * smooth(t / 0.24) * (1 - smooth((t - 0.95) / 0.35))
    legs_under(p, byaw, broll, {"l": side})
    plant(p, "l", l_up, GUARD_DZ["l"] + 1.5 * smooth(t / 0.24) * (1 - smooth((t - 0.95) / 0.35)), 0, -14 * min(1.0, l_up / 4.0),
          clear=0.6 * min(1.0, l_up / 2.0) - 0.05)
    plant(p, "r", 0.0, GUARD_DZ["r"], 8 * fwd, 4 * fwd)
    return p


# ------------------------------------------------------------------ STAGGER: thrown off balance, a crossed step, a shake
S_LURCH = tr((0, 0), (0.14, 1, ease_out), (0.45, 0.85), (0.85, 0.4), (1.45, 0, smooth), (1.6, 0))
S_HEAD = tr((0, 0), (0.08, -0.25), (0.3, 1, ease_out), (0.6, 0.55), (1.1, 0.15), (1.6, 0, smooth))


def stagger(t):
    p = {}
    stance(p)
    lu = float(S_LURCH(t)); hd = float(S_HEAD(t))
    wob = decay(t, 0.3, 0.3, 2.2)                     # the head bounces on the neck, heavily
    shake = decay(t, 1.12, 0.17, 4.5) * (1 - smooth((t - 1.5) / 0.1))      # it clears the head
    byaw, broll = 13 * lu, -9 * lu
    add(p, "body", rot=(-2 * lu, byaw, broll), pos=(0, -1.4 * lu, 1.5 * lu))
    add(p, "neck", rot=(-4 * hd + 3 * wob, -30 * hd + 4 * wob + 4 * shake, 6 * hd))
    add(p, "skull", rot=(-3 * hd + 2 * wob, -10 * hd + 3 * shake, 9 * hd + 11 * shake))
    add(p, "jaw", rot=(-10 * window(t, 0.1, 0.7, 0.15) - 4 * abs(shake), 0, 0))       # slack, then shut
    # the tail swings out wide to bring the weight back, then its wave dies
    trail(p, t, lambda u: -1.1 * 13 * float(S_LURCH(u)) + 5 * decay(u, 0.35, 0.3, 1.1), gain=(0.5, 0.9, 1.4, 2.0), delay=0.08)
    trail(p, t, lambda u: -3.0 * float(S_LURCH(u)), gain=(0.4, 0.6, 0.8, 1.0), axis=0, delay=0.08)
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(6 * lu + 3 * decay(t, 0.2, 0.3, 2.5 + o), 0, 0)); add(p, f"forearm_{s}", rot=(-6 * lu, 0, 0))
    alive(p, t, k=0.4)
    # the left foot crosses over in front to catch the weight (0.15-0.5), uncrosses later (1.0-1.4); the right drags
    cross = smooth((t - 0.15) / 0.35) * (1 - smooth((t - 1.0) / 0.4))
    l_up = arch(t, 0.15, 0.5, 6.0) + arch(t, 1.0, 1.4, 4.0)
    drag = smooth((t - 0.5) / 0.4) * (1 - smooth((t - 1.05) / 0.45))
    r_up = arch(t, 0.52, 0.92, 1.2)
    legs_under(p, byaw, broll, {"l": -7.0 * cross, "r": -2.0 * drag})
    plant(p, "l", l_up, GUARD_DZ["l"] - 5 * cross, 8 * math.sin(math.pi * min(1, max(0, (t - 0.15) / 0.35))), -16 * min(1.0, l_up / 6.0),
          clear=0.8 * min(1.0, l_up / 3.0) - 0.05)
    plant(p, "r", r_up, GUARD_DZ["r"] + 3 * drag, 14 * drag, -22 * drag, clear=-0.05 + 0.3 * min(1.0, r_up))
    return p


NEW = {
    "lunge": (lunge, LUNGE_T, False, "Duelo", "bote comprometido: recua no pé de trás, joga as 9 t e esmaga com a mordida (golpe em 0,50 s)"),
    "parry": (parry, PARRY_T, False, "Duelo", "apara com a cabeça e o ombro e morde o rosto do rival (contra-golpe em 0,60 s)"),
    "stagger": (stagger, STAGGER_T, False, "Duelo", "foi aparado: o quadril vai de lado, a cabeça é jogada, cruza o pé, sacode a cabeça"),
}
