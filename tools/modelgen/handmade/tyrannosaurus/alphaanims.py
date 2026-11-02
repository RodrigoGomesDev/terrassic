"""T. rex alpha: the animations only the alpha has (docs/ALFAS.md; Rodrigo 02/11: "animacoes proprias dele").
The alpha owns its region, and these show it: an unhurried walk, a survey, marking a trunk, a stamping challenge,
bite-and-toss, a shoulder shove, guarding a kill, and a struggle to rise when it is knocked out.
Same rig and the same helpers as rexanims.py; build.py bakes them into tyrannosaurus.animation.json as
animation.tyrannosaurus.alpha_<name>."""
import math
from anim2 import *
import rexanims as X
from rexanims import S, SIDES, W, plant, stand, tail, breathe, tr, window, gait, lie

# ------------------------------------------------------------------ moving and watching
def walk(t):
    """the owner's walk: longer, slower stride, head carried high, almost no bob; it is in no hurry"""
    p = gait(t, 2.4, 86, 0.66, 8, 0.9, lean=-2, head=7, tail_up=1.5, sway=0.75, arms=2.5, roll=1.8)
    add(p, "skull", rot=(2, 5 * math.sin(W(t, 4.8)), 0))
    add(p, "jaw", rot=(1, 0, 0))
    return p

def survey(t):
    """head raised high, a slow sweep across the region from one side to the other, scenting at each end"""
    p = {}; breathe(p, t, T=2.4, amp=0.8)
    up = float(tr((0, 0), (0.8, 1, ease_out), (5.4, 1), (6.0, 0))(t))
    yaw = float(tr((0, 0), (0.8, 0), (1.9, -1), (2.6, -1), (4.1, 1), (4.8, 1), (5.6, 0))(t))
    add(p, "body", rot=(-5 * up, 7 * yaw, 0), pos=(0, 1.6 * up, 0))
    add(p, "neck", rot=(20 * up, 22 * yaw, -3 * yaw)); add(p, "skull", rot=(8 * up, 16 * yaw, -5 * yaw))
    sniff = window(t, 1.95, 2.55, 0.1) + window(t, 4.15, 4.75, 0.1)
    add(p, "skull", rot=(2.5 * sniff * math.sin(2 * math.pi * 6 * t), 0, 0))
    add(p, "jaw", rot=(-1.5 * sniff * max(0, math.sin(2 * math.pi * 6 * t)), 0, 0))
    tail(p, t, yaw=1.0, T=4, amp=0.8)
    [add(p, f"tail{i}", rot=(0, -4 * yaw * (0.4 + 0.25 * i), 0)) for i in range(1, 5)]
    return stand(p)

def jaw_rub(t):
    """marks a trunk: turns the side of the jaw to it and drags it down the bark three times, then a low rumble"""
    p = {}
    k = float(tr((0, 0), (0.6, 1, ease_out), (4.4, 1), (5.0, 0))(t))
    ph = (t - 0.7) / 1.1
    stroke = window(t, 0.7, 4.0, 0.2) * (0.5 - 0.5 * math.cos(2 * math.pi * ph))   # 3 strokes, up -> down
    add(p, "body", rot=(-2 * k, 12 * k, 4 * k), pos=(0, -2.5 * stroke * k, 0))
    add(p, "neck", rot=(6 * k - 14 * stroke, 24 * k, -10 * k)); add(p, "skull", rot=(4 * k - 8 * stroke, 14 * k, -24 * k))
    add(p, "jaw", rot=(-2 * k, 0, 0))
    hum = 0.8 * math.sin(2 * math.pi * 11 * t) * window(t, 4.0, 4.6, 0.12)
    add(p, "neck", rot=(hum, 0, 0))
    tail(p, t, yaw=1.5, T=3, amp=0.8)
    [add(p, f"tail{i}", rot=(0, -6 * k * (0.4 + 0.25 * i), 0)) for i in range(1, 5)]
    return stand(p)

# ------------------------------------------------------------------ fighting
def challenge(t):
    """in place of the threat: head low, the body rocks side to side and the feet stamp in turn, three times"""
    p = {}
    k = float(tr((0, 0), (0.4, 1), (2.9, 1), (3.3, 0))(t))
    rock = math.sin(2 * math.pi * (t - 0.5) / 1.6) * window(t, 0.5, 2.9, 0.3)
    st = [float(tr((0, 0), (a, 0), (a + 0.3, 1, ease_out), (a + 0.42, 0, ease_in), (3.3, 0))(t)) for a in (0.55, 1.35, 2.15)]
    jolt = sum(math.exp(-((t - a - 0.44) / 0.07) ** 2) for a in (0.55, 1.35, 2.15))
    add(p, "body", rot=(6 * k + 2 * jolt, 8 * rock, 5 * rock), pos=(0, -3.5 * k - 1.2 * jolt, 0))
    add(p, "neck", rot=(-12 * k, -5 * rock, -3 * rock)); add(p, "skull", rot=(-5 * k + 3 * jolt, -4 * rock, 0))
    add(p, "jaw", rot=(-14 * k - 6 * jolt, 0, 0))
    tail(p, t, yaw=4 * k, T=0.8, base_pitch=3 * k)
    plant(p, "l", 13 * (st[0] + st[2]), -5 * (st[0] + st[2]), 0, -10 * (st[0] + st[2]), clear=-0.05)
    plant(p, "r", 13 * st[1], -5 * st[1], 0, -10 * st[1], clear=-0.05)
    return p

def bite_toss(t):
    """bites, lifts the head with the prey in its teeth, and throws it aside with a wrench of the neck"""
    p = {}
    lunge = float(tr((0, 0), (0.3, 1, ease_out), (0.45, 1), (0.85, 0, ease_in), (2.2, 0))(t))
    lift = float(tr((0, 0), (0.45, 0), (0.9, 1, ease_out), (1.05, 1), (1.6, 0.3), (2.2, 0))(t))
    whip = float(tr((0, 0), (0.95, 0), (1.05, -0.35), (1.22, 1, ease_out), (1.5, 0.8), (2.2, 0))(t))
    j = float(tr((0, 0), (0.25, -38, ease_out), (0.42, -2, ease_in), (1.18, -2), (1.3, -30, ease_out), (1.7, -6), (2.2, 0))(t))
    add(p, "body", rot=(5 * lunge - 6 * lift, 10 * whip, -4 * whip), pos=(0, -1.5 * lunge + 1.0 * lift, -5 * lunge + 1.5 * lift))
    add(p, "neck", rot=(-16 * lunge + 26 * lift, 34 * whip, -10 * whip))
    add(p, "skull", rot=(-6 * lunge + 10 * lift, 22 * whip, -14 * whip)); add(p, "jaw", rot=(j, 0, 0))
    tail(p, t, yaw=1.5, T=1.1, lag=0.4)
    [add(p, f"tail{i}", rot=(0, -8 * whip * (0.4 + 0.25 * i), 0)) for i in range(1, 5)]
    return stand(p)

def shove(t):
    """turns its flank and drives the right shoulder into whatever is beside or behind it"""
    p = {}
    wind = float(tr((0, 0), (0.35, 1, ease_out), (0.5, 1), (0.62, 0, ease_in), (1.4, 0))(t))
    hit = float(tr((0, 0), (0.5, 0), (0.62, 1, ease_out), (0.8, 1), (1.4, 0))(t))
    jolt = math.exp(-((t - 0.63) / 0.06) ** 2)
    add(p, "body", rot=(2 * hit, 18 * wind - 22 * hit, -6 * wind + 12 * hit), pos=(-3 * wind + 6 * hit, -1.5 * hit - jolt, 0))
    add(p, "neck", rot=(-6 * hit, -12 * wind + 14 * hit, 4 * hit)); add(p, "skull", rot=(-4 * hit, -6 * wind + 8 * hit, 0))
    add(p, "jaw", rot=(-10 * hit - 6 * jolt, 0, 0))
    tail(p, t, yaw=1.5, T=1.2, lag=0.4)
    [add(p, f"tail{i}", rot=(0, (-10 * wind + 14 * hit) * (0.4 + 0.25 * i), 0)) for i in range(1, 5)]
    plant(p, "l"); plant(p, "r", 4 * wind, 3 * wind, 0, 0, clear=-0.05)
    return p

def mirrored(fn):
    """The same move on the other side: left and right bones swap, yaw and roll turn over, sideways moves flip."""
    def side(t):
        out = {}
        for bone, (r, q) in fn(t).items():
            other = bone[:-2] + ("_r" if bone.endswith("_l") else "_l") if bone[-2:] in ("_l", "_r") else bone
            out[other] = ([r[0], -r[1], -r[2]], [-q[0], q[1], q[2]])
        return out
    return side

# ------------------------------------------------------------------ after the kill, and beaten
def guard(t):
    """over its kill: one foot on the carcass, head low, a growl in the throat, eyes on whoever comes near"""
    p = {}
    k = float(tr((0, 0), (0.6, 1, ease_out), (5.4, 1), (6.0, 0))(t))
    look = math.sin(2 * math.pi * t / 6.0) * k
    growl = 0.9 * math.sin(2 * math.pi * 12 * t) * (0.5 + 0.5 * math.sin(2 * math.pi * t / 2.0)) * k
    add(p, "body", rot=(5 * k + 0.4 * growl, 6 * look, -2 * k), pos=(0, -2 * k, 0))
    add(p, "neck", rot=(-16 * k + growl, 16 * look, 0)); add(p, "skull", rot=(-4 * k - growl, 10 * look, 0))
    add(p, "jaw", rot=(-8 * k - 1.5 * abs(growl), 0, 0))
    tail(p, t, yaw=2.5, T=3.0, base_pitch=3 * k)
    plant(p, "l"); plant(p, "r", 18 * k, -20 * k, -14 * k, -8 * k, clear=None)   # the right foot up on the kill
    return p

def ko_struggle(t):
    """knocked out, near waking: lifts the head, heaves the body half up off its side, and drops back, heavy"""
    p = {}; br = math.sin(W(t, 4.0))
    heave = float(tr((0, 0), (0.5, 0), (1.3, 1, ease_out), (1.6, 1), (1.85, 0, ease_in), (3.0, 0))(t))
    head = float(tr((0, 0), (0.2, 0), (1.0, 1, ease_out), (1.65, 1), (1.9, 0, ease_in), (3.0, 0))(t))
    jolt = math.exp(-((t - 1.9) / 0.08) ** 2)
    lie(p, 0.8)
    add(p, "root", rot=(0, 0, 80 - 30 * heave + 4 * jolt))
    add(p, "body", rot=(0.8 * br, 0, 0))
    add(p, "neck", rot=(-4 + 20 * head, 0, -14 + 18 * head)); add(p, "skull", rot=(-6 + 10 * head, 0, -10 + 8 * head))
    add(p, "jaw", rot=(-9 - 1.5 * br - 10 * head * (1 - head) * 4, 0, 0))
    for i in range(1, 5): add(p, f"tail{i}", rot=(0, 0, -3))
    for s, _ in SIDES: add(p, f"arm_{s}", rot=(20 - 25 * heave, 0, 0))
    add(p, "thigh_r", rot=(18 - 30 * heave, 0, 0)); add(p, "shin_r", rot=(10 + 20 * heave, 0, 0))
    return ground_fit(S, p)

# name: (fn, length, loop, category, when it plays)
ANIMS = {
    "walk": (walk, 2.4, True, "Movimento", "andando calmo, no lugar do andar comum"),
    "survey": (survey, 6.0, False, "Parado", "parado, de vez em quando: vigia a região"),
    "jaw_rub": (jaw_rub, 5.0, False, "Parado", "perto de um tronco, raro: marca território"),
    "challenge": (challenge, 3.3, False, "Combate", "no lugar da ameaça: bate os pés antes de avançar"),
    "bite_toss": (bite_toss, 2.2, False, "Combate", "ataque forte de vez em quando: morde e arremessa"),
    "shove": (shove, 1.4, False, "Combate", "alvo do lado direito ou atrás: empurrão com o ombro direito"),
    "shove_left": (mirrored(shove), 1.4, False, "Combate", "alvo do lado esquerdo: o mesmo empurrão com o ombro esquerdo"),
    "guard": (guard, 6.0, False, "Comer", "sobre a presa que matou, rosnando para quem chega"),
    "ko_struggle": (ko_struggle, 3.0, False, "Descanso", "desmaiado, perto de acordar: tenta levantar"),
}
