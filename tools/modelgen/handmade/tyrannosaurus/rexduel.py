"""T. rex: the duel set (06/11/2026). Rodrigo asked for better fights between dinosaurs, after a Raxiores short. What a
fight between two big animals reads as, and the moves here for it (the AI that strings them is ApexBiteGoal's duel):
  * GUARD: crouched and tense, head low and forward with the eyes on the rival, the mouth half open growling, the
    tail up and stiff, the weight rocking on the toes: it waits for an opening;
  * STRAFE: it sidesteps round the rival, the body still facing it, the feet crossing, the tail swinging out;
  * FEINT: a lunge that stops short, the jaws snapping on air, and a quick pull back (testing the other);
  * BLOCK: the bite comes and it turns the head up and aside so the teeth find the thick of the neck;
  * RECOIL: the attacker whose bite was blocked is knocked aside and staggers back a step;
  * SHOVE: the chest and shoulder driven into the rival (the alpha's shove, now any T. rex's);
  * SUBMIT: the loser drops the head and the tail, crouches and turns away before it runs.
"""
import math

from anim2 import add, smooth, ease_in, ease_out, back_out
import rexanims as A
import rexflow as F
import alphaanims as AA

SIDES = A.SIDES
tr = A.tr
window = A.window
plant, stand = A.plant, A.stand
wave, tremor, trail, alive, alive_upper = F.wave, F.tremor, F.trail, F.alive, F.alive_upper

GUARD_T = 2.4


def guard(t):
    p = {}
    T = GUARD_T
    rock = wave(t, T)                                     # the weight rocks forward and back on the toes
    growl = tremor(t, (22 / T, 30 / T, 15 / T), (0.8, 0.45, 0.3))     # harmonics of the loop: it closes
    add(p, "body", rot=(6 + 1.2 * rock, 1.2 * wave(t, T, 1.0), 0.8 * wave(t, T, 0.4)), pos=(0, -3.2 + 0.5 * rock, -0.8 * rock))
    add(p, "neck", rot=(-9 - 1.0 * rock + 0.5 * growl, -1.0 * wave(t, T, 1.4), 0))
    add(p, "skull", rot=(5 + 0.6 * wave(t, T, -0.8) + 0.7 * growl, 0.8 * wave(t, T / 2, 0.3), 0))
    add(p, "jaw", rot=(-7 - 2.0 * max(0.0, wave(t, T / 2, -0.5)) - 1.2 * growl, 0, 0))
    for i in range(1, 5):
        add(p, f"tail{i}", rot=(2.5 * (0.5 + 0.3 * i) + 0.4 * i * wave(t, T, -0.5 * i), (0.8 + 0.9 * i) * wave(t, T, -0.8 * i), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(-12 + 2 * wave(t, T, -1 - 3 * o), 0, 0)); add(p, f"forearm_{s}", rot=(16 + 2 * wave(t, T, -1.6 - 3 * o), 0, 0))
        sx = 1 if s == "l" else -1
        add(p, f"thigh_{s}", rot=(0, 0, 3.0 * sx - 0.8 * wave(t, T, 0.4)))
    plant(p, "l", 0.0, 2.0)
    plant(p, "r", 0.0, -3.0)
    return p


STRAFE_T = 1.4


def strafe(t, side):
    """side = 'left' or 'right' (the animal's): crossing steps, the body facing ahead, leaning into the travel"""
    d = 1.0 if side == "left" else -1.0               # + model x is the animal's left in game
    ph = (t / STRAFE_T) % 1.0; w = 2 * math.pi * ph; p = {}
    add(p, "body", rot=(5, 0, -3.0 * d + 1.5 * math.sin(2 * w)), pos=(1.2 * d * math.sin(2 * w), -2.6 + 0.7 * math.cos(2 * w), 0))
    add(p, "neck", rot=(-8 + 0.8 * math.sin(2 * w), 0, 2.4 * d)); add(p, "skull", rot=(4, 0, 0.8 * d))
    add(p, "jaw", rot=(-5 - 1.0 * tremor(t, (13 / STRAFE_T, 18 / STRAFE_T, 9 / STRAFE_T), (0.7, 0.4, 0.3)), 0, 0))
    for i in range(1, 5):
        add(p, f"tail{i}", rot=(1.5 * (0.5 + 0.3 * i), -d * (2.0 + 1.5 * i) - (0.6 + 0.6 * i) * math.sin(w - 0.7 * i), 0))
    for s, o in SIDES:
        sx = 1 if s == "l" else -1
        u = (ph + o) % 1.0
        add(p, f"arm_{s}", rot=(-10 + 3 * math.sin(w + o * 2 * math.pi - 2.0), 0, 0))
        if u < 0.4:                                     # the foot lifts and swings across, toward the travel
            sw = u / 0.4
            ly = 6.0 * math.sin(math.pi * sw) ** 1.2
            add(p, f"thigh_{s}", rot=(0, 0, d * 9.0 * (sw - 0.5) * 0.8 + 2.5 * sx))
            plant(p, s, ly, 0.0, 8 * math.sin(math.pi * sw), -16 * math.sin(math.pi * sw), clear=0.8 * math.sin(math.pi * sw) ** 0.5)
        else:                                           # planted, the body passing over it
            st = (u - 0.4) / 0.6
            add(p, f"thigh_{s}", rot=(0, 0, -d * 9.0 * (st - 0.5) * 0.8 + 2.5 * sx))
            plant(p, s)
    return p


def strafe_left(t): return strafe(t, "left")
def strafe_right(t): return strafe(t, "right")


FEINT_T = 1.2


def feint(t):
    p = {}
    n = tr((0, (0, 0)), (0.22, (8, 3), ease_out), (0.42, (-12, -1), ease_in), (0.55, (-10, 0)), (1.2, (0, 0), back_out))(t)
    jaw = float(tr((0, -6), (0.2, -10), (0.4, -40, ease_out), (0.5, -42), (0.56, -4, ease_in), (0.8, -7), (1.2, -6))(t))
    lunge = float(tr((0, 0), (0.22, 1.5, ease_out), (0.45, -4.5, ease_in), (0.6, -4.0), (1.2, 0, back_out))(t))
    add(p, "body", rot=(5 - 0.3 * n[0], 0.4 * n[1], 0), pos=(0, -2.6, lunge))
    add(p, "neck", rot=(-8 + n[0], n[1], 0)); add(p, "skull", rot=(4 + 0.6 * n[0], 0.5 * n[1], 0)); add(p, "jaw", rot=(jaw, 0, 0))
    trail(p, t, lambda u: 2.0 * math.exp(-((u - 0.45) / 0.12) ** 2), gain=(0.4, 0.8, 1.2, 1.7), axis=0, delay=0.06)
    alive_upper(p, t, k=0.5)
    return stand(p)


BLOCK_T = 0.8


def block(t):
    """the bite meets the side of the neck: the head jerks up and away, the body twists from it, then comes back"""
    p = {}
    e = math.exp(-max(0.0, t - 0.05) / 0.22) * smooth(t / 0.05)
    add(p, "body", rot=(-3 * e, -8 * e, 4 * e), pos=(0, -0.8 * e, 1.5 * e))
    add(p, "neck", rot=(10 * e, -16 * e, 6 * e)); add(p, "skull", rot=(8 * e, -12 * e, 10 * e)); add(p, "jaw", rot=(-10 * e, 0, 0))
    trail(p, t, lambda u: 8 * math.exp(-max(0.0, u - 0.05) / 0.25) * smooth(u / 0.05), gain=(0.5, 0.9, 1.4, 2.0), delay=0.04)
    alive_upper(p, t, k=0.5)
    return stand(p)


RECOIL_T = 0.9


def recoil(t):
    """the attacker whose jaws hit nothing but the side of the other's neck: the head knocked aside, a step back"""
    p = {}
    e = math.exp(-max(0.0, t - 0.04) / 0.2) * smooth(t / 0.04)
    wob = math.exp(-max(0.0, t - 0.1) / 0.18) * math.sin(2 * math.pi * 4.0 * (t - 0.1)) * smooth((t - 0.08) / 0.05)
    add(p, "body", rot=(-4 * e, 5 * e, -3 * e), pos=(0, -0.6 * e, 3.5 * e))
    add(p, "neck", rot=(6 * e, 14 * e + 4 * wob, -5 * e)); add(p, "skull", rot=(4 * e, 10 * e + 5 * wob, -9 * e)); add(p, "jaw", rot=(-14 * e, 0, 0))
    trail(p, t, lambda u: -7 * math.exp(-max(0.0, u - 0.04) / 0.25) * smooth(u / 0.04), gain=(0.5, 0.9, 1.4, 2.0), delay=0.04)
    alive_upper(p, t, k=0.5)
    plant(p, "l")
    plant(p, "r", 6 * math.sin(math.pi * min(1.0, max(0.0, (t - 0.1) / 0.45))) ** 2, 4 * smooth((t - 0.1) / 0.45), 0, -10 * math.sin(math.pi * min(1.0, max(0.0, (t - 0.1) / 0.45))), clear=-0.05)
    return p


SHOVE_T = 1.4
shove = AA.shove


SUBMIT_T = 2.4


def submit(t):
    """beaten: the head drops low, the tail drops, it crouches and turns away (then it runs)"""
    p = {}
    k = float(tr((0, 0), (0.6, 1, ease_out), (2.4, 1))(t))
    turn = float(tr((0, 0), (0.8, 0), (1.6, 1, ease_out), (2.4, 1))(t))
    whine = math.exp(-((t - 0.9) / 0.15) ** 2)
    add(p, "body", rot=(4 * k, 14 * turn, 0), pos=(0, -3.5 * k, 0))
    add(p, "neck", rot=(-20 * k, 10 * turn, 0)); add(p, "skull", rot=(-8 * k, 6 * turn, 0)); add(p, "jaw", rot=(-2 - 8 * whine, 0, 0))
    for i in range(1, 5):
        add(p, f"tail{i}", rot=(-3.0 * k * (0.5 + 0.3 * i), -4 * turn * (0.4 + 0.2 * i), 0))
    for s_, _ in SIDES:
        add(p, f"thigh_{s_}", rot=(0, -14 * turn, 0))
    alive_upper(p, t, k=0.8)
    return stand(p)
