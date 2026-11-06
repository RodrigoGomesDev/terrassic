"""Quetzalcoatlus: the animations that are its own (the study: a stalker of open country, Witton & Naish 2008).

- stalk: the hunting walk. Slower than the walk, the neck lowered and swung forward, the huge head held still in space
  while the body moves under it (as storks and herons do), scanning from side to side in slow turns;
- attack: the strike of a stalker. The head drops like a spear onto the prey on the ground, the beak closes, and it
  flicks the catch up;
- swallow (the "eat" of a caught animal): it tosses the prey up into the throat and gulps it whole, three gulps
  running down the long neck;
- display: the males stand tall, the neck stretched up, and turn the crested head slowly broadside to one side and
  the other, the beak clattering, the wings half lifted;
- drink: the long reach down to the water, a scoop and the head lifted to let it run down;
- sun: on a hot day it stands with the wings spread and held open to the sun, turned away from the light.
"""
import math
import quetzanim as A
import quetzanims2 as B
from quetzanim import SIDES, mir, stance, lowest, S
from anim2 import add, smooth, ease_out, ease_in, Track

STALK_T = A.WALK_T * 1.7


def stalk_pose(t):
    p = A.walk_pose(t / 1.7)
    w = 2 * math.pi * (t / STALK_T)
    scan = math.sin(w * 0.5)
    # the neck forward and down, the head kept level and steady while the body rocks under it
    add(p, "neck1", rot=(-22, 10 * scan, 0)); add(p, "neck2", rot=(-6, 8 * scan, 0))
    add(p, "skull", rot=(24 - 1.5 * math.sin(2 * w), 6 * scan, -4 * scan))
    return p


ATTACK_T = 1.1


def attack_pose(t):
    p = B.base()
    k = Track([(0, 0), (0.18, -0.25, ease_out), (0.36, 1.0, ease_in), (0.5, 1.0), (0.75, -0.3, ease_out), (1.1, 0)])(t)
    jaw = Track([(0, 0), (0.18, 14), (0.34, 18), (0.42, 0, ease_in), (1.1, 0)])(t)
    down = max(0.0, float(k))
    flick = max(0.0, -float(k))
    B.head(p, n1=(-46 * down + 20 * flick, 0, 0), n2=(-14 * down, 0, 0), sk=(-10 * down + 30 * flick, 0, 0), jaw=float(jaw))
    add(p, "body", rot=(-6 * down, 0, 0))
    return p


SWALLOW_T = 2.0


def swallow_pose(t):
    p = B.base()
    up = Track([(0, 0), (0.3, 1, ease_out), (1.6, 1), (2.0, 0)])(t)
    toss = math.exp(-((t - 0.45) / 0.08) ** 2)
    gul = [math.exp(-((t - c) / 0.09) ** 2) for c in (0.9, 1.15, 1.4)]
    B.head(p, n1=(24 * up, 0, 0), n2=(6 * up, 0, 0), sk=(44 * up + 10 * toss, 0, 0), jaw=22 * toss + 4 * up)
    for b, g in zip(("neck3", "neck2", "neck1"), gul):
        add(p, b, scale=(1 + 0.25 * g, 1 + 0.25 * g, 1))
    return p


DISPLAY_T = 4.2


def display_pose(t):
    p = B.base()
    u = Track([(0, 0), (0.6, 1), (3.6, 1), (4.2, 0)])(t)
    turn = Track([(0, 0), (0.9, 0), (1.5, 1), (2.2, 1), (2.9, -1), (3.5, -1), (4.2, 0)])(t)
    clat = math.sin(2 * math.pi * t / 0.09) * (1 if 1.5 < t < 3.5 else 0)
    B.head(p, n1=(18 * u, 10 * turn * u, 0), n2=(6 * u, 12 * turn * u, 0), sk=(18 * u, 40 * turn * u, -10 * turn * u),
           jaw=3 * u + 3 * max(0.0, clat))
    for s, sx in SIDES:
        add(p, f"arm_{s}", rot=mir((0, 0, 14 * u + 2 * math.sin(2 * math.pi * t / 0.5)), sx))
    add(p, "body", rot=(4 * u, 0, 0))
    return p


DRINK_T = 3.6


def drink_pose(t):
    p = B.base()
    down = Track([(0, 0), (0.8, 1, ease_out), (2.0, 1), (2.4, 0.2), (3.6, 0)])(t)
    lift = math.exp(-((t - 2.6) / 0.25) ** 2)
    B.head(p, n1=(-60 * down + 10 * lift, 0, 0), n2=(-14 * down, 0, 0), sk=(-6 * down + 30 * lift, 0, 0), jaw=6 * down)
    add(p, "body", rot=(-10 * down, 0, 0))
    return p


ANIMS = {
    "stalk": (stalk_pose, STALK_T, True),
    "attack": (attack_pose, ATTACK_T, False),
    "eat": (swallow_pose, SWALLOW_T, False),
    "display": (display_pose, DISPLAY_T, False),
    "drink": (drink_pose, DRINK_T, False),
}
