"""Elasmosaurus animations, written for it from its own study (page "Elasmossauro: estudo para a 1.8", approved by
Rodrigo on 05/11/2026). Shared with the other rigs is only bake and export.

From what a 10 m plesiosaur with a 7 m neck would do:
- it FLIES under water: the four flippers beat like wings, the fore pair and the hind pair out of step (the studies of
  plesiosaur swimming find the hind pair a little behind the fore pair), the stroke down and back, the flipper
  feathered on the way up; the trunk is stiff, it hardly bends; the neck held straight ahead, a little down, and it
  bends only a little, more to the side and down than up (Zammit et al. 2008; Noè et al. 2017): no swan's S;
- it hunts by stealth: the long neck lets the small head come at a shoal from below while the body, far behind, does
  not scare it; the strike is a quick sideways and upward flick of the front of the neck (neck_strike);
- it swallows stones from the bottom (gastroliths, found in many elasmosaurids): the head down to the floor, a scoop,
  a gulp (gastrolith);
- it breathes at the surface with only the top of the head out, the neck rising in a long gentle slope (breathe), and
  dives nose first with a strong stroke (dive);
- stranded on land it cannot carry its weight: it lies on its belly, the flippers pushing in turn, the neck lifting
  and dropping (stranded);
- it sleeps floating at the surface, the neck laid along the water (sleep); knocked out it rolls belly up.

Signs on this rig: body +x = nose up, z = roll; neck*/skull -x = down, y = to its left; jaw -x = open; flipper roots:
z (times the side) = the flipper down, x = feathered (leading edge up).
"""
import math
import os
import sys
_H = os.path.dirname(os.path.abspath(__file__))
_E = os.path.join(_H, "..", "_engine")
sys.path[:0] = [_H, _E]
import geo
import proto as P
import elasmo as EL
from anim2 import add, Track, smooth, ease_out, ease_in

W = lambda t, T: 2 * math.pi * t / T
NECKS = [f"neck{i}" for i in range(1, 8)]
TAILS = ("tail1", "tail2", "tail3")
SIDES = (("l", 1), ("r", -1))


def tr(*keys): return Track(keys)


def f(track, t): return float(track(t))


def window(t, a, b, fade=0.25):
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


def model():
    m = EL.build("male"); P.pack(m, EL.TEX_W); return m.spec()


S = model()


def low_of(p):
    return min(q[:, 1].min() for c, q in geo.cube_points(S, p) if c["bone"] != "saddle")


def ground(p):
    lo = low_of(p); add(p, "root", pos=(0, -lo, 0)); return p


def neck(p, pitch=0.0, yaw=0.0, roll=0.0, front=0.0):
    """spread a bend over the seven neck bones; front > 0 puts more of it in the front half (a flick)"""
    for i, b in enumerate(NECKS):
        w = 1.0 + front * (i - 3) / 3.0
        add(p, b, rot=(pitch / 7 * w, yaw / 7 * w, roll / 7))


def head(p, pitch=0.0, yaw=0.0): add(p, "skull", rot=(pitch, yaw, 0))


def jaw(p, a): add(p, "jaw", rot=(a, 0, 0))


def tail(p, yaw=0.0, pitch=0.0):
    for i, b in enumerate(TAILS): add(p, b, rot=(pitch * (0.6 + 0.3 * i), yaw * (0.6 + 0.3 * i), 0))


def flip(p, which, s, sx, down=0.0, feather=0.0, sweep=0.0):
    """one flipper: down (+ down), feather (leading edge up), sweep (+ back); the outer pieces bend to follow"""
    add(p, f"{which}_{s}", rot=(feather, sweep * sx, -down * sx))
    add(p, f"{which}1_{s}", rot=(feather * 0.4, 0, -down * 0.3 * sx))
    add(p, f"{which}2_{s}", rot=(feather * 0.3, 0, -down * 0.35 * sx))


def stroke(p, t, T, amp, lag=0.3, sweep=8.0, glide=0.0):
    """the flight stroke: down and back with the flipper flat, up and forward feathered; the hind pair lags"""
    for which, ph in (("fore", 0.0), ("hind", lag)):
        a = W(t, T) - 2 * math.pi * ph
        down = amp * math.sin(a) * (1 - glide)
        feather = -18 * math.cos(a) * (1 - glide)
        for s, sx in SIDES:
            flip(p, which, s, sx, down=down + 4 * glide, feather=feather, sweep=sweep * math.sin(a + 1.2) + 10 * glide)


def bob(p, t, T, amp):
    add(p, "body", rot=(0.6 * amp * math.sin(W(t, T) + 0.8), 0, 0), pos=(0, amp * math.sin(W(t, T)), 0))


# ------------------------------------------------------------------ in the water
def idle(t):
    """hovering: slow sculling strokes out of step, the neck swinging slowly to look, the head turning"""
    p = {}; bob(p, t, 4.0, 0.5)
    stroke(p, t, 4.0, 10, lag=0.5, sweep=4)
    a = window(t, 1.0, 3.2, 0.6); b = window(t, 4.2, 6.0, 0.6)
    neck(p, -4 + 2 * math.sin(W(t, 8.0)), 14 * a - 12 * b)
    head(p, 0, 8 * a - 6 * b)
    tail(p, yaw=3 * math.sin(W(t, 4.0)))
    return p


def swim(t):
    """cruising flight: full strokes, the body rising a little on each downstroke, the neck straight ahead"""
    p = {}; bob(p, t, 1.6, 0.8)
    stroke(p, t, 1.6, 18, lag=0.3, sweep=8)
    neck(p, -4 - 1.5 * math.sin(W(t, 1.6) - 0.6), 0)
    tail(p, yaw=2 * math.sin(W(t, 1.6)), pitch=2 * math.sin(W(t, 1.6) + 1))
    return p


def walk(t):
    """slow swim: a stroke, then a glide with the flippers held out"""
    p = {}; ph = (t % 3.0) / 3.0
    g = smooth((ph - 0.45) / 0.15) * (1 - smooth((ph - 0.9) / 0.1))
    bob(p, t, 3.0, 0.5)
    stroke(p, t, 3.0, 14, lag=0.25, sweep=6, glide=g)
    neck(p, -5, 4 * math.sin(W(t, 6.0)))
    return p


def run(t):
    """the burst: fast deep strokes, the flippers swept back on the recovery, the neck stretched ahead"""
    p = {}; bob(p, t, 0.9, 1.0)
    stroke(p, t, 0.9, 22, lag=0.2, sweep=10)
    neck(p, -2, 0)
    tail(p, pitch=-3)
    return p


def stranded(t):
    """on land: belly down, the flippers pushing in turn against the ground, the neck lifting and dropping heavily"""
    p = {}
    for which, ph in (("fore", 0.0), ("hind", 0.5)):
        a = W(t, 2.4) - 2 * math.pi * ph
        for s, sx in SIDES:
            flip(p, which, s, sx, down=8 + 8 * math.sin(a), feather=0, sweep=-10 * math.cos(a))
    lift = max(0.0, math.sin(W(t, 2.4)))
    neck(p, -3 + 6 * lift, 4 * math.sin(W(t, 4.8)))
    jaw(p, -6 * window(t, 0.8, 1.4, 0.15))
    tail(p, yaw=6 * math.sin(W(t, 2.4)))
    return ground(p)


def breathe(t):
    """up for air: the neck rises in a long gentle slope, only the top of the head breaks the surface, a breath, back
    down"""
    p = {}
    k = f(tr((0, 0), (0.9, 1, ease_out), (2.0, 1), (2.8, 0, smooth)), t)
    stroke(p, t, 2.8, 8, lag=0.5, sweep=4)
    add(p, "body", rot=(6 * k, 0, 0))
    neck(p, 14 * k, 0)
    head(p, -8 * k, 0)
    jaw(p, -3 * window(t, 1.2, 1.5, 0.1))
    return p


def dive(t):
    """nose first: the body tips down, two strong strokes"""
    p = {}
    k = f(tr((0, 0), (0.6, 1, ease_out), (1.8, 1), (2.2, 0, smooth)), t)
    add(p, "body", rot=(-24 * k, 0, 0))
    stroke(p, t, 1.1, 30 * k + 8, lag=0.25, sweep=12)
    neck(p, -6 * k, 0)
    tail(p, pitch=4 * k)
    return p


def neck_strike(t):
    """the strike at a shoal: the front of the neck drawn back and to one side, then flicked in and up, the jaws snap"""
    p = {}
    back = f(tr((0, 0), (0.3, 1, ease_out), (0.45, 1), (0.55, -0.4, ease_in), (0.9, 0, smooth)), t)
    o = f(tr((0, 0), (0.35, 1, ease_out), (0.52, 1), (0.58, 0, ease_in), (0.9, 0)), t)
    stroke(p, t, 2.0, 8, lag=0.5, sweep=4)
    neck(p, -10 * back, 22 * back, 0, front=0.9)
    head(p, 10 * max(0.0, -back), -10 * back)
    jaw(p, -30 * o)
    return p


attack = neck_strike


def eat(t):
    """takes a fish: a snap, then the head tips up and the fish goes down the long neck in a few gulps"""
    p = {}
    o = f(tr((0, 0), (0.2, 1, ease_out), (0.32, 0, ease_in), (2.2, 0)), t)
    up = f(tr((0, 0), (0.4, 0), (0.8, 1, ease_out), (1.8, 1), (2.2, 0, smooth)), t)
    gulp = window(t, 0.9, 1.7, 0.1) * max(0, math.sin(W(t - 0.9, 0.27)))
    stroke(p, t, 2.2, 6, lag=0.5)
    neck(p, -6 + 6 * up, 0)
    head(p, 14 * up, 0)
    jaw(p, -20 * o - 4 * gulp)
    return p


def gastrolith(t):
    """swallows stones: the head goes down to the bottom, scoops twice, the head up and a gulp"""
    p = {}
    dn = f(tr((0, 0), (0.8, 1, smooth), (2.4, 1), (3.0, 0, smooth)), t)
    scoop = sum(window(t, c, c + 0.35, 0.1) for c in (1.0, 1.7))
    stroke(p, t, 3.0, 6, lag=0.5)
    add(p, "body", rot=(-8 * dn, 0, 0))
    neck(p, -30 * dn, 0, 0, front=0.4)
    head(p, -10 * dn + 12 * scoop, 0)
    jaw(p, -14 * scoop - 6 * window(t, 2.6, 2.9, 0.1))
    return p


def hurt(t):
    p = {}
    k = f(tr((0, 0), (0.07, 1, ease_out), (0.55, 0, smooth)), t)
    add(p, "body", rot=(4 * k, 0, 8 * k))
    neck(p, 6 * k, -6 * k, 0, front=0.5)
    jaw(p, -14 * k)
    stroke(p, t, 0.5, 8 * k)
    return p


def _ko(p, k, t):
    br = math.sin(W(t, 4.4))
    add(p, "body", rot=(0, 0, 170 * k), pos=(0, 0.3 * br * k, 0))
    for which in ("fore", "hind"):
        for s, sx in SIDES:
            flip(p, which, s, sx, down=-12 * k, feather=0, sweep=6 * k)
    neck(p, 6 * k, 10 * k, 0)
    jaw(p, -8 * k)
    return p


def knocked_out(t):
    return _ko({}, 1.0, t)


def wake(t):
    """rolls back upright, shakes its head, a strong stroke"""
    p = {}
    k = f(tr((0, 1), (0.4, 1), (1.3, 0, smooth), (3.0, 0)), t)
    _ko(p, k, t)
    sh = window(t, 1.4, 2.0, 0.1) * math.sin(W(t, 0.3))
    neck(p, 0, 14 * sh, 0, front=0.6)
    stroke(p, t, 1.2, 20 * (1 - k))
    return p


def death(t):
    """rolls belly up and sinks, the flippers going loose, the neck sagging"""
    p = {}
    k = f(tr((0, 0), (0.6, 0), (1.6, 1, ease_in), (3.0, 1)), t)
    thrash = window(t, 0.0, 0.8, 0.15) * math.sin(W(t, 0.35))
    _ko(p, k, t)
    add(p, "body", rot=(-6 * k, 0, 0), pos=(0, -8 * smooth((t - 1.4) / 1.6), 0))
    neck(p, -14 * k, 12 * thrash, 0)
    stroke(p, t, 0.6, 20 * (1 - k))
    return p


def sit(t):
    """resting where it was told: hanging still in the water, flippers spread, the neck a little down"""
    p = {}; bob(p, t, 5.0, 0.3)
    stroke(p, t, 5.0, 4, lag=0.5)
    neck(p, -8, 3 * math.sin(W(t, 10.0)))
    return p


def sleep(t):
    """asleep floating at the surface, the neck laid out along the water, a slow breath"""
    p = {}; bob(p, t, 6.0, 0.4)
    for which in ("fore", "hind"):
        for s, sx in SIDES:
            flip(p, which, s, sx, down=-4, sweep=10)
    neck(p, 6, 10, 0)
    head(p, -4, 4)
    return p


def wake_sleep(t):
    p = {}
    k = f(tr((0, 1), (0.6, 1), (1.6, 0, smooth), (2.0, 0)), t)
    for which in ("fore", "hind"):
        for s, sx in SIDES:
            flip(p, which, s, sx, down=-4 * k, sweep=10 * k)
    neck(p, 6 * k, 10 * k, 0)
    stroke(p, t, 1.0, 14 * (1 - k))
    return p


def beg(t):
    """asks for food: the head brought round to the owner, the jaws parting, a little nod"""
    p = {}; bob(p, t, 2.2, 0.4)
    stroke(p, t, 2.2, 8, lag=0.5)
    nod = math.sin(W(t, 1.1))
    neck(p, 4 + 3 * nod, 10 * math.sin(W(t, 4.4)), 0, front=0.5)
    jaw(p, -8 * window(t, 0.4, 1.6, 0.3))
    return p


def tame(t):
    """accepts its owner: the neck laid slowly down and round toward the owner, a long breath"""
    p = {}
    k = f(tr((0, 0), (0.8, 1, ease_out), (2.0, 1), (2.6, 0, smooth)), t)
    bob(p, t, 2.6, 0.6)
    stroke(p, t, 2.6, 6, lag=0.5)
    neck(p, -14 * k, 24 * k, 0, front=0.4)
    head(p, -6 * k, 8 * k)
    return p


def nuzzle(t):
    """a mother and her calf: the head brought down beside the other, a slow touch of the snout"""
    p = {}
    k = f(tr((0, 0), (0.6, 1, ease_out), (1.8, 1), (2.4, 0, smooth)), t)
    stroke(p, t, 2.4, 6, lag=0.5)
    neck(p, -10 * k, -20 * k, 0, front=0.5)
    head(p, -6 * k, -10 * k + 4 * window(t, 0.9, 1.5, 0.2))
    return p


ANIMS = {
    "idle": (idle, 8.0, True, "Parado", "paira com remadas lentas, o pescoço vira devagar para olhar"),
    "swim": (swim, 1.6, True, "Movimento", "o voo debaixo d'água: as quatro nadadeiras batem como asas"),
    "walk": (walk, 3.0, True, "Movimento", "nada devagar: uma remada e um planeio"),
    "run": (run, 0.9, True, "Movimento", "a arrancada: remadas fundas e rápidas, o pescoço esticado"),
    "stranded": (stranded, 2.4, True, "Só dele", "encalhado: de barriga no chão, as nadadeiras empurram, o pescoço pesa"),
    "breathe": (breathe, 2.8, False, "Só dele", "respira na superfície com só o alto da cabeça fora d'água"),
    "dive": (dive, 2.2, False, "Só dele", "mergulha de nariz, duas remadas fortes"),
    "neck_strike": (neck_strike, 0.9, False, "Só dele", "o bote de pescoço: a frente do pescoço recua de lado e chicoteia"),
    "attack": (attack, 0.9, False, "Combate", "a mordida é o bote de pescoço"),
    "gastrolith": (gastrolith, 3.0, False, "Só dele", "engole pedras no fundo"),
    "nuzzle": (nuzzle, 2.4, False, "Só dele", "a mãe e o filhote encostam o focinho"),
    "eat": (eat, 2.2, False, "Comer", "pega o peixe e engole erguendo a cabeça"),
    "hurt": (hurt, 0.55, False, "Combate", "ao levar dano"),
    "death": (death, 3.0, False, "Combate", "vira de barriga para cima e afunda"),
    "sit": (sit, 8.0, True, "Descanso", "parado na água, nadadeiras abertas"),
    "sleep": (sleep, 9.0, True, "Descanso", "dorme boiando, o pescoço deitado na água"),
    "wake_sleep": (wake_sleep, 2.0, False, "Descanso", "acorda e volta a nadar"),
    "knocked_out": (knocked_out, 4.4, True, "Descanso", "nocauteado, de barriga para cima"),
    "wake": (wake, 3.0, False, "Descanso", "desvira, sacode a cabeça e nada"),
    "beg": (beg, 2.2, True, "Domado", "pede comida: vira a cabeça para o dono e abre a boca"),
    "tame": (tame, 2.6, False, "Domado", "deita o pescoço devagar na direção do dono"),
}

# 06/11/2026: the fluid set (elasflow.py) takes over every name; the originals above stay as the bases it builds on
import elasflow as FLOW  # noqa: E402

for _n in list(ANIMS):
    _fn, _L, _loop, _cat, _when = ANIMS[_n]
    ANIMS[_n] = (getattr(FLOW, _n), _L, _loop, _cat, _when)
ANIMS["neck_strike"] = (FLOW.neck_strike, FLOW.STRIKE_T, False, "Só dele",
                        "o bote de pescoço em três tempos: enrola em S, estica da base à ponta (boca fecha em 0,55 s), passa e assenta")
ANIMS["attack"] = (FLOW.attack, FLOW.STRIKE_T, False, "Combate", "a mordida é o bote de pescoço (boca fecha em 0,55 s)")
