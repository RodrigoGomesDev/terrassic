"""T. rex: states with transitions, more bites and tiredness (06/11/2026, from the study of seven dinosaur mods,
docs/estudos/09_MODS_DE_DINOS_E_IDEIAS.md: the good ones never jump from standing to lying, vary their blows and
show when the animal is spent).
  * LIE_DOWN / GET_UP / FALL_ASLEEP: the rest is entered and left through its own movement (the hind legs fold
    first, the chest goes down, the head settles; getting up pushes with the legs, the head swinging forward for
    balance, a wobble);
  * BITE_LOW: for something small at its feet, the head swept low along the ground;
  * BITE_SIDE: the head swings in from the side in an arc, the jaws closing at the end of the arc;
  * WALK_TIRED / IDLE_TIRED: after a long chase, the head hangs, the mouth stays open panting, the steps drag.
"""
import math

from anim2 import add, smooth, ease_in, ease_out, back_out
import rexanims as A
import rexflow as F

SIDES = A.SIDES
tr = A.tr
plant, stand = A.plant, A.stand
wave, tremor, trail, alive, alive_upper = F.wave, F.tremor, F.trail, F.alive, F.alive_upper

LIE_DOWN_T = 2.2


def lie_down(t):
    p = {}
    k = float(tr((0, 0), (0.3, 0.05), (1.5, 0.92, ease_in), (1.75, 1.03), (2.2, 1.0, ease_out))(t))
    look = float(tr((0, 0), (0.4, 1, ease_out), (1.4, 1), (2.2, 0, ease_out))(t))
    A.lie(p, k)
    add(p, "neck", rot=(-6 * look, 0, 0)); add(p, "skull", rot=(-4 * look, 0, 0))     # it looks down where it lies
    land = math.exp(-((t - 1.6) / 0.1) ** 2)
    add(p, "body", rot=(0.8 * land, 0, 0)); add(p, "jaw", rot=(-3 * land, 0, 0))
    trail(p, t, lambda u: 2.5 * math.exp(-((u - 1.6) / 0.15) ** 2), gain=(0.5, 0.9, 1.3, 1.7), axis=0, delay=0.06)
    alive_upper(p, t, k=0.5)
    return A.ground_fit(A.S, p)


GET_UP_T = 2.2


def get_up(t):
    p = {}
    k = float(tr((0, 1.0), (0.45, 1.02), (1.35, 0.05, ease_out), (1.6, -0.02), (2.2, 0.0, ease_out))(t))
    push = math.exp(-((t - 0.6) / 0.2) ** 2)
    A.lie(p, max(0.0, k))
    add(p, "neck", rot=(-12 * push, 0, 0)); add(p, "skull", rot=(-6 * push, 0, 0))   # the head swings forward to rise
    wob = math.exp(-max(0.0, t - 1.4) / 0.25) * math.sin(2 * math.pi * 2.4 * (t - 1.4)) * smooth((t - 1.35) / 0.1)
    add(p, "body", rot=(0, 0, 2.5 * wob))
    trail(p, t, lambda u: -3.0 * math.exp(-max(0.0, u - 1.4) / 0.3) * math.sin(2 * math.pi * 2.4 * (u - 1.4)) * smooth((u - 1.35) / 0.1),
          gain=(0.5, 0.9, 1.3, 1.8), delay=0.07)
    alive_upper(p, t, k=0.5)
    return A.ground_fit(A.S, p)


FALL_ASLEEP_T = 3.6


def fall_asleep(t):
    """from standing: it lies down, looks round once, yawns, and the head sinks to the ground"""
    p = {}
    k = float(tr((0, 0), (0.3, 0.05), (1.5, 0.92, ease_in), (1.75, 1.03), (2.1, 1.0, ease_out), (3.6, 1.0))(t))
    head = float(tr((0, 0), (2.4, 0), (3.5, 1.0, ease_in), (3.6, 1.0))(t))
    A.lie(p, k, head_down=head)
    yawn = float(tr((0, 0), (1.9, 0), (2.25, -30, ease_out), (2.45, -28), (2.7, -2, ease_in), (3.6, 0))(t))
    add(p, "jaw", rot=(yawn, 0, 0)); add(p, "skull", rot=(0.25 * -yawn, 0, 0))
    add(p, "neck", rot=(0, 10 * F.window(t, 2.0, 2.4, 0.2), 0))
    alive_upper(p, t, k=0.4)
    return A.ground_fit(A.S, p)


BITE_LOW_T = 1.2


def bite_low(t):
    """the head swept down along the ground at something small (the hit at 0.42 s)"""
    p = {}
    n = tr((0, (0, 0)), (0.2, (6, 2), ease_out), (0.38, (-26, -2), ease_in), (0.5, (-24, 0)), (1.2, (0, 0), back_out))(t)
    j = float(tr((0, 0), (0.18, -28, ease_out), (0.36, -32), (0.43, -3, ease_in), (0.7, -5), (1.2, 0, ease_out))(t))
    add(p, "body", rot=(-0.35 * n[0], 0.3 * n[1], 0), pos=(0, 0.06 * n[0], 0.1 * n[0]))
    add(p, "neck", rot=(n[0], n[1], 0)); add(p, "skull", rot=(0.4 * n[0], 0.5 * n[1], 0)); add(p, "jaw", rot=(j, 0, 0))
    trail(p, t, lambda u: 0.15 * -tr((0, (0, 0)), (0.2, (6, 2), ease_out), (0.38, (-26, -2), ease_in), (0.5, (-24, 0)), (1.2, (0, 0), back_out))(u)[0],
          gain=(0.5, 0.8, 1.1, 1.4), axis=0, delay=0.06)
    alive(p, t, k=0.5)
    return stand(p)


BITE_SIDE_T = 1.3


def bite_side(t):
    """the head swings in from one side in an arc, the jaws snapping shut at the end of it (the hit at 0.45 s)"""
    p = {}
    yw = float(tr((0, 0), (0.25, 24, ease_out), (0.45, -10, ease_in), (0.6, -14), (1.3, 0, back_out))(t))
    pt = float(tr((0, 0), (0.25, 6, ease_out), (0.45, -10, ease_in), (0.6, -8), (1.3, 0, back_out))(t))
    j = float(tr((0, 0), (0.22, -34, ease_out), (0.4, -38), (0.47, -3, ease_in), (0.8, -5), (1.3, 0, ease_out))(t))
    add(p, "body", rot=(-0.2 * pt, 0.35 * yw, -0.15 * yw), pos=(0, 0, -1.5 * smooth((t - 0.3) / 0.15) * (1 - smooth((t - 0.7) / 0.5))))
    add(p, "neck", rot=(pt, 0.55 * yw, 0.1 * yw)); add(p, "skull", rot=(0.6 * pt, 0.45 * yw, 0.35 * yw)); add(p, "jaw", rot=(j, 0, 0))
    trail(p, t, lambda u: -0.35 * float(tr((0, 0), (0.25, 24, ease_out), (0.45, -10, ease_in), (0.6, -14), (1.3, 0, back_out))(u)),
          gain=(0.5, 0.9, 1.4, 2.0), delay=0.06)
    alive(p, t, k=0.5)
    return stand(p)


WALK_TIRED_T = 2.4


def walk_tired(t):
    """the walk with nothing left: slower and shorter steps, the head hanging, the mouth open, the breath heaving"""
    p = A.gait2(t, WALK_TIRED_T, 56, 0.66, 6, 2.2, lean=2, drop=1.5, head=-9, tail_up=-2, roll=9.0, yaw=4.0, whip=0.8, arms=7.0)
    pant = wave(t, WALK_TIRED_T / 3)
    add(p, "jaw", rot=(-10 - 5 * max(0.0, pant), 0, 0)); add(p, "neck", rot=(-1.4 * wave(t, WALK_TIRED_T / 3, -0.5), 0, 0))
    return p


IDLE_TIRED_T = 3.0


def idle_tired(t):
    """spent after a chase: the chest heaves fast, the mouth hangs open, the head low, the tail low"""
    p = {}
    pant = wave(t, IDLE_TIRED_T / 4)
    add(p, "body", rot=(2.5 + 2.0 * pant, 0, 0), pos=(0, -1.2 + 0.8 * pant, 0))
    add(p, "neck", rot=(-10 - 1.8 * wave(t, IDLE_TIRED_T / 4, -0.6), 2 * wave(t, IDLE_TIRED_T, 0.5), 0))
    add(p, "skull", rot=(-4 - 1.2 * wave(t, IDLE_TIRED_T / 4, -1.2), 1.5 * wave(t, IDLE_TIRED_T, -0.5), 0))
    add(p, "jaw", rot=(-12 - 6 * max(0.0, wave(t, IDLE_TIRED_T / 4, -0.4)), 0, 0))
    for i in range(1, 5):
        add(p, f"tail{i}", rot=(-1.5 * (0.5 + 0.3 * i) + 0.4 * i * pant, (0.8 + 0.8 * i) * wave(t, IDLE_TIRED_T, -0.8 * i), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(6 + 2.5 * wave(t, IDLE_TIRED_T / 4, -0.8 - o), 0, 0))
    return stand(p)
