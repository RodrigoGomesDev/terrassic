"""Mosasaurus animations, written for it from its own study (page "Mosassauro 1.5", section "movimento"; the 1.5
decisions delegated to the threads on 02/11/2026).

No legs, so no leg IK: the plumbing shared with the other remakes is only bake and export (anim2). Every pose and every
cycle is the Mosasaurus' own, from what the study says the animal was:
- it swims with the TAIL, the trunk stiff (a late mosasaur swam like a shark or a tuna, not like an eel: Lindgren et
  al. 2011, 2013): the wave grows from almost nothing at the hips to the fluke, which does most of the work; the
  flippers steer and brake, held out like a shark's pectorals, swept back flat against the body in a burst;
- it is an ambush hunter from below: it lies low in the water and rises at what is at the surface in a steep burst,
  the jaws opening late (ambush); a big one throws itself clear of the water now and then (breach);
- it breathes air: it comes up and lifts only the top of its head, where the nostrils are, out of the water (breathe);
- it swallows in steps: the jaws, bending half way along, and the teeth on the roof of the mouth walk the prey into the
  throat (the pterygoid "ratchet", swallow); big prey is shaken to pieces first (shake);
- males fought with their jaws, gaping and biting at each other's heads (spar: the bite scars of the study);
- it gave birth at sea to live young, tail first (birth: the mother's body curls and the tail base heaves);
- on land it is helpless: it lies on its belly and thrashes (stranded).

Signs on this rig: body +x = nose up; neck/skull -x = nose down; jaw -x = open; tail yaw: the wave's sign does not
matter; flipper_f/h l: z + = the tip up, y - = swept back (the right ones mirrored).
"""
import math
import os
import sys
_H = os.path.dirname(os.path.abspath(__file__))
_E = os.path.join(_H, "..", "_engine")
sys.path[:0] = [_H, _E]
from anim2 import add, Track, smooth, ease_out, ease_in

TAILS = ("tail1", "tail2", "tail3", "tail4", "fluke")
WAVE = (2.0, 4.5, 7.0, 10.0, 15.0)      # the amplitude grows toward the fluke: the trunk stiff, the fluke doing the work
LAG = (0.0, 0.55, 1.1, 1.6, 2.1)         # phase lag along the tail (radians)


def tr(*keys): return Track(keys)


def f(track, t): return float(track(t))


def window(t, a, b, fade=0.25):
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


def W(t, T): return 2 * math.pi * t / T


def flip(p, side, rot):
    """a flipper pair: the left one as given, the right one mirrored"""
    x, y, z = rot
    add(p, f"flipper_{side}l", rot=(x, y, z))
    add(p, f"flipper_{side}r", rot=(x, -y, -z))


def wave(p, t, T, amp=1.0, bias=0.0):
    """the swimming wave along the tail, one full beat per T seconds; bias bends the whole tail to one side (a turn)"""
    for i, b in enumerate(TAILS):
        add(p, b, rot=(0, amp * WAVE[i] * math.sin(W(t, T) - LAG[i]) + bias * (i + 1), 0))
    # the front answers the tail a little (a stiff trunk is not a rigid one)
    add(p, "body", rot=(0, -0.25 * amp * WAVE[0] * math.sin(W(t, T) + 0.4), 0))
    add(p, "neck", rot=(0, -0.3 * amp * math.sin(W(t, T) + 0.8), 0))


def jaw(p, a, front=0.0):
    """open the jaws by a (degrees); the front half bends on its own joint by front"""
    add(p, "jaw", rot=(-a, 0, 0))
    if front:
        add(p, "jaw_front", rot=(-front, 0, 0))


# ------------------------------------------------------------------ movement
def idle(t):
    """hovering: the flippers scull slowly, out of step, the tail sways a little, the body rises and falls"""
    T = 4.0; p = {}
    wave(p, t, T, 0.35)
    add(p, "root", pos=(0, 0.6 * math.sin(W(t, T)), 0))
    add(p, "body", rot=(0.8 * math.sin(W(t, T) + 1.0), 0, 0))
    flip(p, "f", (0, 4 * math.sin(W(t, T)), 5 * math.sin(W(t, T) + 0.6)))
    flip(p, "h", (0, 3 * math.sin(W(t, T) + 2.0), 4 * math.sin(W(t, T) + 2.6)))
    add(p, "neck", rot=(1.0 * math.sin(W(t, T) + 2.2), 0, 0))
    return p


def swim(t):
    """cruising: the tail beats, the trunk steady, the flippers held out like a shark's, trimming"""
    T = 1.6; p = {}
    wave(p, t, T, 1.0)
    flip(p, "f", (0, -8, 3 * math.sin(W(t, T) + 1.0)))
    flip(p, "h", (0, -10, 2 * math.sin(W(t, T) + 1.6)))
    add(p, "root", pos=(0, 0.4 * math.sin(2 * W(t, T)), 0))
    return p


def walk(t):
    """the slow patrol along the bottom: lazy beats, the flippers spread to hold the line"""
    T = 2.4; p = {}
    wave(p, t, T, 0.65)
    flip(p, "f", (0, -2, 4 + 2 * math.sin(W(t, T))))
    flip(p, "h", (0, -4, 3 + 2 * math.sin(W(t, T) + 1.0)))
    add(p, "neck", rot=(-1.5, 0, 0))
    return p


def run(t):
    """the burst: big fast beats from the fluke, the flippers swept back flat against the body, the head driving"""
    T = 0.8; p = {}
    wave(p, t, T, 1.5)
    flip(p, "f", (0, -40, 12))
    flip(p, "h", (0, -42, 10))
    add(p, "neck", rot=(-2, 0, 0))
    add(p, "root", pos=(0, 0.5 * math.sin(2 * W(t, T)), 0))
    return p


def stranded(t):
    """out of the water: on its belly, the head lifts and drops with a gasp, the tail swings in heavy arcs, the
    flippers row at nothing"""
    T = 1.6; p = {}
    s = math.sin(W(t, T))
    for i, b in enumerate(TAILS):
        add(p, b, rot=(-1.5 * (i > 2), 6 * s * (0.6 + 0.2 * i), 0))
    # the fluke folds over flat on the ground (the lower lobe would go into it)
    add(p, "fluke", rot=(-58, 0, 0))
    add(p, "tail4", rot=(-4, 0, 0))
    add(p, "root", pos=(0, 0.35, 0))
    add(p, "body", rot=(0, -2 * s, 1.5 * s))
    head = max(0.0, math.sin(W(t, T) + 0.8))
    add(p, "neck", rot=(6 * head, 3 * s, 0))
    jaw(p, 14 * head)
    add(p, "throat", scale=(1.0, 1.0 + 0.25 * head, 1.0))
    flip(p, "f", (0, -10 + 14 * math.sin(W(t, T)), 22 + 10 * math.sin(W(t, T) + 1.2)))
    flip(p, "h", (0, -8 + 10 * math.sin(W(t, T) + 1.6), 18 + 8 * math.sin(W(t, T) + 2.4)))
    return p


# ------------------------------------------------------------------ its own
def ambush(t):
    """from below: it tips its nose up at what is on the surface and drives up with a few hard beats, the jaws
    opening late, wide, the front of the jaw bending down on its joint, then the snap at 1.05 s and the level-out"""
    p = {}
    pitch = tr((0, 0), (0.35, 42, ease_out), (1.1, 46), (1.6, 0))
    add(p, "body", rot=(f(pitch, t), 0, 0))
    wave(p, t, 0.55, 1.6 * f(tr((0, 0.6), (0.3, 1.0), (1.1, 1.0), (1.6, 0.3)), t))
    flip(p, "f", (0, -42 * f(tr((0, 0), (0.3, 1), (1.2, 1), (1.6, 0)), t), 10))
    flip(p, "h", (0, -40 * f(tr((0, 0), (0.3, 1), (1.2, 1), (1.6, 0)), t), 8))
    g = f(tr((0, 0), (0.7, 0), (0.95, 1, ease_out), (1.05, 0, ease_in), (1.6, 0)), t)
    jaw(p, 34 * g, 8 * g)
    add(p, "neck", rot=(6 * g, 0, 0))
    add(p, "root", pos=(0, f(tr((0, 0), (1.05, 10, ease_out), (1.6, 0)), t), -f(tr((0, 0), (1.05, 6), (1.6, 0)), t)))
    return p


def breach(t):
    """the leap: up out of the water at a steep angle, the body arcing over in the air, nose down, back in; the
    flippers flared, the tail trailing (the jump itself is the game's push; this is the body)"""
    p = {}
    pitch = tr((0, 0), (0.4, 38, ease_out), (1.2, 10), (1.8, -40), (2.4, 0))
    add(p, "body", rot=(f(pitch, t), 0, f(tr((0, 0), (0.8, 8), (1.6, 14), (2.4, 0)), t)))
    k = f(tr((0, 1.4), (0.4, 1.0), (0.6, 0.2), (1.9, 0.2), (2.4, 0.8)), t)
    wave(p, t, 0.6, k)
    trail = f(tr((0, 0), (0.6, 0), (1.2, -6), (1.8, 8), (2.4, 0)), t)
    for i, b in enumerate(TAILS):
        add(p, b, rot=(trail * (0.4 + 0.2 * i), 0, 0))
    flip(p, "f", (0, -10, 22 * window(t, 0.4, 2.0, 0.2)))
    flip(p, "h", (0, -14, 16 * window(t, 0.4, 2.0, 0.2)))
    return p


def breathe(t):
    """up for air: the front of the body tilts up so only the top of the head, where the long nostril slits are,
    breaks the surface; the blow (the throat empties), a breath in (it fills), and back down"""
    p = {}
    up = f(tr((0, 0), (0.6, 1), (2.0, 1), (2.6, 0)), t)
    add(p, "body", rot=(10 * up, 0, 0))
    add(p, "neck", rot=(6 * up, 0, 0))
    add(p, "skull", rot=(4 * up, 0, 0))
    add(p, "root", pos=(0, 3 * up, 0))
    blow = f(tr((0, 1), (0.7, 1), (0.95, 0.8, ease_out), (1.5, 1.2), (2.2, 1.2), (2.6, 1.0)), t)
    add(p, "throat", scale=(1.0, blow, 1.0))
    wave(p, t, 2.6, 0.4)
    flip(p, "f", (0, 4, 10 * up))
    flip(p, "h", (0, 2, 6 * up))
    return p


def swallow(t):
    """the ratchet: head up, then three steps: the jaws open a little, the head is pushed forward over the prey (the
    teeth on the roof of the mouth hold it while the jaws reach), the jaws close; the throat swells and the bulge
    moves back down the neck"""
    p = {}
    up = f(tr((0, 0), (0.3, 1), (2.1, 1), (2.4, 0)), t)
    add(p, "neck", rot=(14 * up, 0, 0))
    steps = (0.35, 0.95, 1.55)
    g = 0.0; push = 0.0
    for k, s0 in enumerate(steps):
        u = (t - s0) / 0.55
        if 0 <= u <= 1:
            g = math.sin(math.pi * u)
            push = math.sin(math.pi * u)
            side = 1 if k % 2 == 0 else -1          # the two sides of the jaw walk in turn
            add(p, "jaw_front", rot=(0, 5 * side * g, 0))
    jaw(p, 12 * g, 4 * g)
    add(p, "skull", pos=(0, 0, -1.2 * push))
    swell = f(tr((0, 1.0), (0.4, 1.0), (1.0, 1.25), (1.6, 1.45), (2.1, 1.3), (2.4, 1.0)), t)
    add(p, "throat", scale=(1.0 + 0.3 * (swell - 1), swell, 1.0), pos=(0, 0, f(tr((0, 0), (1.2, 0), (2.4, 4)), t)))
    wave(p, t, 2.4, 0.3)
    return p


def shake(t):
    """the jaws clamped on something too big to swallow: three hard shakes of the head and neck, the body rolling
    against them, the tail beating to hold it in place"""
    p = {}
    k = window(t, 0.1, 1.2, 0.15)
    s = math.sin(W(t, 0.45))
    add(p, "neck", rot=(4 * k, 18 * s * k, 6 * s * k))
    add(p, "skull", rot=(0, 10 * s * k, 0))
    add(p, "body", rot=(0, -4 * s * k, -6 * s * k))
    jaw(p, f(tr((0, 0), (0.08, 10), (0.15, 2), (1.25, 2), (1.4, 0)), t))
    wave(p, t, 0.7, 1.1 * k + 0.2)
    return p


def spar(t):
    """two males: the gape held wide at the rival, the head tilted to show the teeth, then a sideways clamp at its
    head and a shake (the healed bite marks on the skulls of mosasaurs)"""
    p = {}
    gape = f(tr((0, 0), (0.4, 1, ease_out), (1.3, 1), (1.5, 0.15, ease_in), (2.2, 0.15), (2.6, 0)), t)
    jaw(p, 36 * gape, 10 * gape)
    tilt = f(tr((0, 0), (0.4, 16), (1.3, 16), (1.5, 0), (2.6, 0)), t)
    add(p, "neck", rot=(4 * gape, f(tr((0, 0), (1.3, 0), (1.5, 26, ease_out), (2.2, 26), (2.6, 0)), t), tilt))
    shk = window(t, 1.5, 2.2, 0.1) * math.sin(W(t, 0.3))
    add(p, "skull", rot=(0, 8 * shk, 0))
    add(p, "body", rot=(2 * gape, 0, -4 * gape))
    wave(p, t, 0.9, 0.7)
    flip(p, "f", (0, 6 * gape, 14 * gape))
    return p


def birth(t):
    """the mother gives birth at sea, tail first (the young of Carsosaurus lie head forward in the mother: Caldwell &
    Lee 2001): her body curls to one side, the base of the tail heaves twice, then she straightens and turns to the
    calf"""
    p = {}
    curl = f(tr((0, 0), (0.6, 1), (2.8, 1), (3.6, 0)), t)
    for i, b in enumerate(TAILS[:3]):
        add(p, b, rot=(0, 9 * curl * (1 - 0.25 * i), 0))
    add(p, "body", rot=(0, -4 * curl, 10 * curl))
    heave = sum(window(t, a, a + 0.5, 0.2) for a in (1.0, 1.9))
    add(p, "tail1", rot=(-8 * heave, 0, 0))
    add(p, "tail2", rot=(6 * heave, 0, 0))
    add(p, "neck", rot=(0, f(tr((0, 0), (2.8, 0), (3.3, -18), (3.6, -10)), t), 0))
    flip(p, "h", (0, 10 * curl, 18 * curl))
    flip(p, "f", (0, 4, 8 * curl))
    return p


# ------------------------------------------------------------------ combat
def attack(t):
    """the bite: the head draws back a touch, the jaws gape (the front of the jaw bowing down on its joint, the double
    hinge), the lunge, the snap at 0.42 s, the shake of the catch"""
    p = {}
    g = f(tr((0, 0), (0.22, 1, ease_out), (0.42, 0, ease_in), (0.8, 0)), t)
    jaw(p, 34 * g, 9 * g)
    add(p, "neck", rot=(f(tr((0, 0), (0.2, 6), (0.42, -4), (0.8, 0)), t), 0, 0))
    add(p, "root", pos=(0, 0, -f(tr((0, 0), (0.15, -2), (0.42, 7, ease_out), (0.8, 0)), t)))
    add(p, "body", rot=(f(tr((0, 0), (0.2, 3), (0.42, -2), (0.8, 0)), t), 0, 0))
    wave(p, t, 0.4, f(tr((0, 0.4), (0.3, 1.4), (0.8, 0.4)), t))
    flip(p, "f", (0, -30 * window(t, 0.15, 0.6, 0.1), 6))
    return p


def hurt(t):
    p = {}
    k = f(tr((0, 0), (0.08, 1, ease_out), (0.5, 0)), t)
    add(p, "body", rot=(0, 4 * k, -8 * k))
    add(p, "neck", rot=(6 * k, -10 * k, 0))
    jaw(p, 10 * k)
    for i, b in enumerate(TAILS):
        add(p, b, rot=(0, -6 * k * (i + 1) / 2, 0))
    return p


def _ko(p, roll, t, T=4.4):
    """on its side in the water, limp: the jaw slack, the flippers loose, a slow breath"""
    add(p, "body", rot=(0, 0, roll))
    br = math.sin(W(t, T))
    jaw(p, 8 + 2 * br)
    add(p, "neck", rot=(-4, 4, 0))
    flip(p, "f", (0, 8, -12 + 2 * br))
    flip(p, "h", (0, 6, -10))
    for i, b in enumerate(TAILS):
        add(p, b, rot=(2, 2 + 0.8 * i, 0))
    add(p, "throat", scale=(1, 1 + 0.06 * br, 1))


def knocked_out(t):
    p = {}
    _ko(p, 88, t)
    add(p, "root", pos=(0, -6, 0))
    return p


def wake(t):
    """from the knockout: it rolls back upright, shakes its head, a beat of the tail"""
    p = {}
    r = f(tr((0, 1), (0.9, 1), (1.6, 0, smooth), (2.6, 0)), t)
    _ko(p, 88 * r, t)
    add(p, "root", pos=(0, -6 * r, 0))
    s = window(t, 1.6, 2.4, 0.15) * math.sin(W(t, 0.35))
    add(p, "skull", rot=(0, 10 * s, 0))
    wave(p, t, 0.8, window(t, 1.4, 2.6, 0.2))
    return p


def death(t):
    """it rolls belly up and sinks: the pale belly turns to the light, the flippers go loose, the jaw falls open"""
    p = {}
    r = f(tr((0, 0), (0.4, 20), (2.0, 172, smooth), (3.0, 178)), t)
    add(p, "body", rot=(f(tr((0, 0), (3.0, -6)), t), 0, r))
    add(p, "root", pos=(0, -f(tr((0, 0), (1.0, 2), (3.0, 10)), t), 0))
    k = f(tr((0, 0), (1.0, 1), (3.0, 1)), t)
    jaw(p, 16 * k)
    flip(p, "f", (0, 10 * k, 20 * k))
    flip(p, "h", (0, 8 * k, 16 * k))
    for i, b in enumerate(TAILS):
        add(p, b, rot=(-3 * k, 3 * k * (1 + 0.5 * i), 0))
    add(p, "neck", rot=(-6 * k, 0, 0))
    add(p, "fluke", rot=(0, 6 * math.sin(W(t, 0.5)) * (1 - k), 0))
    return p


# ------------------------------------------------------------------ feeding, rest, tame
def eat(t):
    """takes a fish in front of it: a quick snap, then one step of the ratchet and the gulp down the throat"""
    p = {}
    g = f(tr((0, 0), (0.18, 1, ease_out), (0.32, 0, ease_in), (0.8, 0), (1.0, 0.35), (1.2, 0), (1.6, 0)), t)
    jaw(p, 26 * g, 6 * g)
    add(p, "neck", rot=(f(tr((0, 0), (0.18, -4), (0.32, 2), (1.0, 8), (1.6, 0)), t), 0, 0))
    add(p, "root", pos=(0, 0, -f(tr((0, 0), (0.25, 3), (0.8, 0)), t)))
    add(p, "throat", scale=(1, f(tr((0, 1), (1.0, 1), (1.25, 1.3), (1.6, 1)), t), 1))
    wave(p, t, 1.6, 0.4)
    return p


def sit(t):
    """resting where it was told: hanging still in the water, the head a little down, the flippers spread wide to
    hold it level, the tail barely moving"""
    T = 6.0; p = {}
    wave(p, t, T, 0.18)
    add(p, "neck", rot=(-3, 0, 0))
    flip(p, "f", (0, 6, 2 * math.sin(W(t, T))))
    flip(p, "h", (0, 4, 2 * math.sin(W(t, T) + 1.4)))
    add(p, "root", pos=(0, 0.4 * math.sin(W(t, T)), 0))
    return p


def sleep(t):
    """asleep on the bottom: the chin down, the flippers flat out on the sand, the body tipped a little nose down,
    one slow sway of the tail now and then"""
    T = 8.0; p = {}
    add(p, "body", rot=(-2, 0, 0))
    add(p, "neck", rot=(-3, 0, 0))
    flip(p, "f", (0, 10, 12))
    flip(p, "h", (0, 8, 12))
    s = math.sin(W(t, T))
    for i, b in enumerate(TAILS):
        add(p, b, rot=(-1, 2.0 * s * (i + 1) / 3, 0))
    add(p, "fluke", rot=(-58, 0, 0))
    add(p, "root", pos=(0, 0.75, 0))
    add(p, "throat", scale=(1, 1 + 0.05 * math.sin(W(t, T / 2)), 1))
    return p


def wake_sleep(t):
    """wakes: the head lifts off the sand, a yawn with the whole double-hinged gape, a beat of the tail and up"""
    p = {}
    r = f(tr((0, 1), (0.5, 0.6), (2.0, 0)), t)
    add(p, "body", rot=(-2 * r, 0, 0))
    add(p, "root", pos=(0, 0.75 * r, 0))
    add(p, "fluke", rot=(-58 * r, 0, 0))
    flip(p, "f", (0, 10 * r, 12 * r))
    flip(p, "h", (0, 8 * r, 12 * r))
    y = f(tr((0, 0), (0.5, 0), (0.9, 1, ease_out), (1.3, 1), (1.6, 0)), t)
    jaw(p, 38 * y, 12 * y)
    add(p, "neck", rot=(10 * y - 4 * r, 0, 0))
    wave(p, t, 0.9, window(t, 1.3, 2.0, 0.2))
    return p


def beg(t):
    """asks its owner for fish: the head up out of the water toward them, two claps of the jaws, sculling to hold"""
    T = 2.4; p = {}
    add(p, "body", rot=(8, 0, 0))
    add(p, "neck", rot=(10, 0, 0))
    add(p, "root", pos=(0, 3, 0))
    clap = sum(window(t, a, a + 0.25, 0.08) for a in (0.5, 1.0))
    jaw(p, 16 * clap, 4 * clap)
    wave(p, t, T / 2, 0.5)
    flip(p, "f", (0, 4 * math.sin(W(t, T / 2)), 8 + 4 * math.sin(W(t, T / 2) + 1)))
    return p


def tame(t):
    """accepts its owner: it rolls slowly onto its side and shows the pale belly, the jaws shut, then rolls back"""
    p = {}
    r = f(tr((0, 0), (0.9, 1), (2.0, 1), (3.0, 0)), t)
    add(p, "body", rot=(0, 0, 70 * r))
    add(p, "neck", rot=(0, -8 * r, 0))
    flip(p, "f", (0, 6 * r, 10 * r))
    flip(p, "h", (0, 4 * r, 8 * r))
    wave(p, t, 3.0, 0.3)
    return p


def gape(t):
    """the warning: a wild adult turns broadside-on to whoever comes too close in the water and opens the jaws as wide
    as they go, the front of the jaw bowing down on its own joint so the whole double hinge shows, the throat
    ballooning and the head tilted to bare the teeth on the roof of the mouth; held, a slow sideways sweep of the head,
    then a clap shut (the gape display of the monitors, its kin, on a jaw no lizard alive has)"""
    p = {}
    g = f(tr((0, 0), (0.45, 1, ease_out), (1.9, 1), (2.05, 0, ease_in), (2.8, 0)), t)
    jaw(p, 44 * g, 18 * g)
    add(p, "throat", scale=(1.0 + 0.15 * g, 1.0 + 0.5 * g, 1.0))
    sweep = window(t, 0.5, 1.9, 0.25) * math.sin(W(t - 0.5, 1.4))
    add(p, "neck", rot=(7 * g, 14 * sweep, 12 * g))
    add(p, "skull", rot=(4 * g, 0, 6 * g))
    add(p, "body", rot=(3 * g, 0, -5 * g))
    flip(p, "f", (0, 10 * g, 20 * g))
    flip(p, "h", (0, 6 * g, 12 * g))
    wave(p, t, 1.4, 0.5)
    return p


def spyhop(t):
    """it rises with the head straight up out of the water and hangs there, the flippers sculling, turning the head
    slowly to one side and the other to look over the surface, then slides back under (a whale's habit, the hypothesis
    of the study for an air-breathing hunter that hunts what is on top of the water)"""
    p = {}
    up = f(tr((0, 0), (0.8, 1, ease_out), (3.3, 1), (4.0, 0, ease_in)), t)
    add(p, "body", rot=(62 * up, 0, 0))
    add(p, "root", pos=(0, 12 * up, 4 * up))
    look = f(tr((0, 0), (1.0, 0), (1.6, 28), (2.3, 28), (2.9, -24), (3.3, -24), (3.7, 0)), t)
    add(p, "neck", rot=(-18 * up, 0.6 * look, 0))
    add(p, "skull", rot=(-10 * up, 0.4 * look, 0))
    for i, b in enumerate(TAILS):
        add(p, b, rot=(-6 * up * (i > 1), 5 * up * math.sin(W(t, 1.2) - LAG[i]), 0))
    flip(p, "f", (0, 12 * up * math.sin(W(t, 1.2)), 24 * up))
    flip(p, "h", (0, 8 * up * math.sin(W(t, 1.2) + 1.0), 14 * up))
    return p


ANIMS = {
    "idle": (idle, 4.0, True, "Parado", "paira na água: as nadadeiras remam devagar, fora de compasso, a cauda balança pouco"),
    "swim": (swim, 1.6, True, "Movimento", "nado de cruzeiro: o tronco firme, a cauda bate e a meia-lua faz o trabalho"),
    "walk": (walk, 2.4, True, "Movimento", "a ronda lenta rente ao fundo, batidas preguiçosas, nadadeiras abertas"),
    "run": (run, 0.8, True, "Movimento", "a arrancada: batidas largas e rápidas, nadadeiras coladas no corpo"),
    "stranded": (stranded, 1.6, True, "Só dele", "fora d'água: de barriga, a cabeça sobe e cai num arquejo, a cauda varre pesada"),
    "ambush": (ambush, 1.6, False, "Só dele", "a emboscada por baixo: aponta o focinho para a superfície e sobe em arrancada, a boca abre tarde"),
    "breach": (breach, 2.4, False, "Só dele", "o salto: sai da água num ângulo alto, arqueia no ar e volta de focinho"),
    "breathe": (breathe, 2.6, False, "Só dele", "sobe para respirar: só o alto da cabeça, onde ficam as narinas, sai da água"),
    "swallow": (swallow, 2.4, False, "Só dele", "engole em etapas: a mandíbula de duas dobras e os dentes do céu da boca puxam a presa"),
    "shake": (shake, 1.4, False, "Só dele", "presa grande demais: três sacudidas de cabeça, o corpo rolando contra"),
    "spar": (spar, 2.6, False, "Só dele", "dois machos: a boca escancarada, a cabeça de lado, a mordida na cabeça do rival"),
    "gape": (gape, 2.8, False, "Só dele", "o aviso: escancara a boca de lado para quem chega perto, a frente da mandíbula dobrando na junta, a garganta inchada"),
    "spyhop": (spyhop, 4.0, False, "Só dele", "põe a cabeça de pé para fora d'água e olha em volta, devagar, antes de afundar de novo"),
    "birth": (birth, 3.6, False, "Só dele", "a fêmea dá à luz no mar, a cauda do filhote primeiro: o corpo curva, a base da cauda força"),
    "attack": (attack, 0.8, False, "Combate", "a mordida: a frente da mandíbula dobra na junta do meio, o bote, o fechar"),
    "hurt": (hurt, 0.5, False, "Combate", "ao levar dano"),
    "death": (death, 3.0, False, "Combate", "vira de barriga para cima e afunda: a barriga clara para a luz"),
    "eat": (eat, 1.6, False, "Comer", "abocanha o peixe na frente, um passo da catraca e engole"),
    "sit": (sit, 6.0, True, "Descanso", "parado onde mandaram, nadadeiras abertas para ficar nivelado"),
    "sleep": (sleep, 8.0, True, "Descanso", "dorme no fundo: o queixo baixo, as nadadeiras na areia"),
    "wake_sleep": (wake_sleep, 2.0, False, "Descanso", "acorda: ergue a cabeça, boceja com a boca inteira e bate a cauda"),
    "knocked_out": (knocked_out, 4.4, True, "Descanso", "nocauteado de lado na água, a boca frouxa"),
    "wake": (wake, 2.6, False, "Descanso", "acorda do nocaute: rola de volta, sacode a cabeça"),
    "beg": (beg, 2.4, True, "Domado", "pede peixe: a cabeça para fora d'água na direção do dono, bate a boca duas vezes"),
    "tame": (tame, 3.0, False, "Domado", "aceita o dono: rola de lado devagar e mostra a barriga clara"),
}


# the fluid set (06/11/2026, mosaflow.py): the existing names rebound to their fluid versions, and the new ones
import mosaflow as FLOW  # noqa: E402
for _n, (_fn, _len) in FLOW.REBIND.items():
    _o = ANIMS[_n]
    ANIMS[_n] = (_fn, _len) + tuple(_o[2:])
ANIMS.update(FLOW.NEW)
