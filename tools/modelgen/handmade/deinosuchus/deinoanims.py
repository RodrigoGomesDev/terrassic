"""Deinosuchus animations, written for it from its own study (page "Deinossuco: estudo para a 1.8", approved by Rodrigo
on 05/11/2026). Shared with the other rigs is only bake and export: the legs of a crocodylian sprawl to the sides, so
they are driven bone by bone (swing about the hip, lift out to the side), not by the upright-leg IK of the
ceratopsians, and every pose is set down on the ground by its lowest point.

From what a 12 m alligatoroid of the shore would do (the living alligators and crocodiles as the guide):
- on land the HIGH WALK, the belly carried clear of the ground, the spine bending side to side with the steps, the
  big head held level; the run is the same gait faster, the body lower and the tail swinging wide;
- in the water it swims with the tail alone, the legs laid back along the body; at rest it FLOATS like a log, only
  the eyes, the skull table and the nostril out (float);
- it ambushes from the water: the LUNGE, the tail driving the front half up and forward, the jaws wide (lunge); a
  held victim is rolled over and over (death_roll); on land a side snap (attack) and the tail swept round (tail_sweep);
- it BASKS on the bank with the mouth wide open, as crocodylians shed heat (bask); the male BELLOWS, head and tail
  raised, the back shivering so the water dances on it (bellow, as the American alligator, Vliet 1989); it slaps
  the water with the underside of the jaw (head_slap); the young chirp for the mother (chirp);
- it swallows by tossing the head back (eat); it rests flat on the belly, sleeps with the tail curled round;
  knocked out it rolls onto its back.

Signs on this rig: body +x = nose up, +z = roll to its right; neck/skull -x = down; jaw -x = open; tail pitch + =
down, yaw + = to its left; thigh/arm +x = the foot swings forward, z (times the side) = the leg lifted out.
"""
import math
import os
import sys
_H = os.path.dirname(os.path.abspath(__file__))
_E = os.path.join(_H, "..", "_engine")
sys.path[:0] = [_H, _E]
import geo
import proto as P
import deino as DN
from anim2 import add, Track, smooth, ease_out, ease_in

W = lambda t, T: 2 * math.pi * t / T


def tr(*keys): return Track(keys)


def f(track, t): return float(track(t))


def window(t, a, b, fade=0.25):
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


def model():
    m = DN.build("male"); P.pack(m, DN.TEX_W); return m.spec()


S = model()
SIDES = (("l", 1), ("r", -1))
TAILS = ("tail1", "tail2", "tail3", "tail4", "tail5", "tail6")
BEND = (0.7, 0.85, 1.0, 1.1, 1.2, 1.3)


def low_of(p, bones=None):
    return min(q[:, 1].min() for c, q in geo.cube_points(S, p) if bones is None or c["bone"] in bones)


def ground(p):
    """set the pose down on its lowest point"""
    lo = low_of(p); add(p, "root", pos=(0, -lo, 0)); return p


def head(p, pitch=0.0, yaw=0.0, roll=0.0, k=0.4):
    add(p, "neck", rot=(pitch * k, yaw * k, roll * 0.3))
    add(p, "skull", rot=(pitch * (1 - k), yaw * (1 - k), roll * 0.7))


def jaw(p, a): add(p, "jaw", rot=(a, 0, 0))


def gape(p, deg):
    """opens the mouth the crocodylian way: the upper head lifts, the lower jaw stays near level"""
    add(p, "skull", rot=(deg * 0.85, 0, 0))
    add(p, "jaw", rot=(-deg, 0, 0))


def tail(p, yaw=0.0, pitch=0.0):
    for b, k in zip(TAILS, BEND): add(p, b, rot=(pitch * k, yaw * k, 0))


def tail_wave(p, t, Tc, yaw, pitch=0.0, lag=0.7, ph=0.0):
    for i, (b, k) in enumerate(zip(TAILS, BEND)):
        a = W(t, Tc) - lag * i + ph
        add(p, b, rot=(pitch * k * math.sin(a - 0.6), yaw * k * math.sin(a), 0))


def leg(p, kind, s, swing=0.0, lift=0.0, high=0.0, knee=0.0):
    """one leg: swing (+ forward), lift (the foot raised out to the side), high (the leg turned under the body, the
    high walk), knee (the lower leg bent further)"""
    sx = 1 if s == "l" else -1
    up, low, end = ("thigh", "shin", "foot") if kind == "h" else ("arm", "forearm", "hand")
    add(p, f"{up}_{s}", rot=(swing, 0, (lift - high) * sx))
    add(p, f"{low}_{s}", rot=(knee - 0.4 * swing, 0, (high * 0.9 - lift * 0.6) * sx))
    add(p, f"{end}_{s}", rot=(-0.6 * swing - knee * 0.5, 0, (lift * 0.3) * sx))


def breathe(p, t, T=4.0, amp=1.0):
    br = math.sin(W(t, T))
    add(p, "body", rot=(0.3 * amp * br, 0, 0), pos=(0, 0.25 * amp * (1 + br), 0))
    return br


def stance(p, high=1.0, spread=0.0):
    """standing: high = how far the legs are turned under (0 flat on the belly, 1 the high walk)"""
    for s, _ in SIDES:
        leg(p, "h", s, high=34 * high - spread)
        leg(p, "f", s, high=30 * high - spread)


# ------------------------------------------------------------------ gaits
LATERAL = {"lh": 0.0, "lf": 0.25, "rh": 0.5, "rf": 0.75}     # the crocodylian walk: diagonal couplets


def walk_cycle(t, Tc, amp, lift, high, bend, hd=0.0, low=0.0):
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    # the spine bends toward the side whose hind leg swings forward; the head is held level against it
    add(p, "body", rot=(0, bend * math.sin(w), 1.0 * math.sin(w + 0.4)), pos=(0, -low, 0))
    add(p, "neck", rot=(hd * 0.5, -bend * 0.9 * math.sin(w - 0.3), 0))
    add(p, "skull", rot=(hd * 0.5, -bend * 0.4 * math.sin(w - 0.6), 0))
    for i, (b, k) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(0, 1.6 * bend * k * math.sin(w - 0.9 - 0.55 * i), 0))
    for foot, o in LATERAL.items():
        s, kind = foot[0], foot[1]
        u = (ph + o) % 1.0
        duty = 0.7
        if u < duty:
            sw = amp - 2 * amp * (u / duty); lf = 0.0
        else:
            e = (u - duty) / (1 - duty)
            sw = -amp + 2 * amp * (0.5 - 0.5 * math.cos(math.pi * e)); lf = lift * math.sin(math.pi * e)
        leg(p, kind, s, swing=sw, lift=lf, high=(34 if kind == "h" else 30) * high, knee=6 * lf / max(lift, 1))
    return ground(p)


WALK = (1.6, 22, 18, 1.0, 5.0)
RUNP = (0.9, 30, 22, 0.75, 8.0)


def walk(t):
    return walk_cycle(t, *WALK)


def run(t):
    return walk_cycle(t, *RUNP, hd=-1, low=0.5)


def swim(t):
    """the tail alone drives it: big waves running down the tail, the body following a little, the legs laid back"""
    Tc = 1.4; w = W(t, Tc); p = {}
    add(p, "body", rot=(0, 3 * math.sin(w), 0))
    add(p, "neck", rot=(0, -2.5 * math.sin(w - 0.3), 0))
    tail_wave(p, t, Tc, 16, 0.0, lag=0.75)
    for s, sx in SIDES:
        add(p, f"thigh_{s}", rot=(-55, 0, 6 * sx)); add(p, f"shin_{s}", rot=(-20, 0, 0)); add(p, f"foot_{s}", rot=(-30, 0, 0))
        add(p, f"arm_{s}", rot=(-60, 0, 8 * sx)); add(p, f"forearm_{s}", rot=(-15, 0, 0)); add(p, f"hand_{s}", rot=(-25, 0, 0))
    return p


def float_(t):
    """resting in the water like a log: still, the legs hanging out to the sides, the tail curved a little, a slow
    sway of the tail tip; only the head's top is meant to show above the water"""
    p = {}; br = math.sin(W(t, 5.0))
    add(p, "body", rot=(0.4 * br, 0, 0), pos=(0, 0.3 * br, 0))
    for s, sx in SIDES:
        leg(p, "h", s, swing=-10, lift=10); leg(p, "f", s, swing=-6, lift=12)
    tail(p, yaw=4)
    tail_wave(p, t, 6.0, 3.0)
    head(p, 2 * window(t, 2.0, 3.6, 0.6), 6 * window(t, 2.0, 3.6, 0.6))
    return p


# ------------------------------------------------------------------ lying down
def lie(p, k=1.0):
    """flat on the belly, the legs splayed out to the sides, the chin on the ground"""
    for s, _ in SIDES:
        leg(p, "h", s, swing=-20 * k, lift=6 * k, high=34 * (1 - k))
        leg(p, "f", s, swing=-10 * k, lift=8 * k, high=30 * (1 - k))
    head(p, -2 * k)
    return p


def ko_pose(p, k=1.0, t=0.0):
    """knocked out: rolled onto its back, the legs up and loose, the jaw slack"""
    br = math.sin(W(t, 4.0))
    add(p, "body", rot=(0, 0, 168 * k))
    jaw(p, -6 * k + 0.5 * br)
    for s, sx in SIDES:
        leg(p, "h", s, swing=10 * k, lift=-20 * k); leg(p, "f", s, swing=-5 * k, lift=-20 * k)
    tail(p, yaw=8 * k)
    head(p, 4 * k, 10 * k)
    return p


def blend(a, b, w):
    out = {}
    for bone in set(a) | set(b):
        ea = a.get(bone, ([0, 0, 0], [0, 0, 0])); eb = b.get(bone, ([0, 0, 0], [0, 0, 0]))
        out[bone] = ([ea[0][i] * (1 - w) + eb[0][i] * w for i in range(3)], [ea[1][i] * (1 - w) + eb[1][i] * w for i in range(3)])
    return out


def sit(t):
    """flat on the belly at rest; now and then the head lifts a little and turns"""
    p = {}; breathe(p, t, 4.5, 0.6)
    lie(p)
    a = window(t, 2.5, 4.5, 0.6)
    head(p, 4 * a, 12 * a)
    tail_wave(p, t, 9.0, 2.0)
    return ground(p)


def sleep(t):
    """asleep: flat, the chin down, the tail curled round to one side"""
    p = {}; breathe(p, t, 5.5, 0.5)
    lie(p)
    head(p, -2, -6)
    tail(p, yaw=12)
    return ground(p)


def wake_sleep(t):
    """wakes: the head up, then the body pushed up onto the legs"""
    p = {}
    k = f(tr((0, 1), (0.8, 1), (1.8, 0, smooth), (2.2, 0)), t)
    hk = f(tr((0, 0), (0.5, 1, ease_out), (1.6, 1), (2.2, 0, smooth)), t)
    lie(p, k)
    stance(p, 1 - k)
    head(p, 8 * hk)
    tail(p, yaw=12 * k)
    return ground(p)


def knocked_out(t):
    return ground(ko_pose({}, 1.0, t))


def wake(t):
    """from the knocked-out pose: thrashes, rolls back onto the belly, gets up"""
    roll = f(tr((0, 1), (0.4, 1), (1.3, 0, smooth), (3.0, 0)), t)
    thrash = window(t, 0.0, 0.8, 0.15) * math.sin(W(t, 0.35))
    p = blend(lie({}), ko_pose({}, 1.0), roll)
    add(p, "body", rot=(0, 0, 8 * thrash))
    tail(p, yaw=14 * thrash)
    up = f(tr((0, 0), (1.6, 0), (2.6, 1, smooth), (3.0, 1)), t)
    stance(p, up)
    return ground(p)


def death(t):
    """thrashes, the jaws snapping, then rolls over onto its back and goes still"""
    thrash = window(t, 0.0, 1.2, 0.2) * math.sin(W(t, 0.4))
    roll = f(tr((0, 0), (1.0, 0), (1.8, 1, ease_in), (1.95, 0.94), (2.1, 1, smooth), (2.6, 1)), t)
    p = blend(lie({}), ko_pose({}, 1.0), roll)
    add(p, "body", rot=(0, 6 * thrash, 6 * thrash))
    jaw(p, -14 * window(t, 0.1, 1.0, 0.1) * max(0, math.sin(W(t, 0.3))))
    tail(p, yaw=20 * thrash)
    return ground(p)


# ------------------------------------------------------------------ standing / everyday
def idle(t):
    """standing low on the legs, breathing; the head lifts and turns slowly, the jaw parts a little, the tail sways"""
    p = {}; breathe(p, t, 4.0)
    stance(p, 0.55)
    a = window(t, 1.5, 3.2, 0.6); b = window(t, 4.0, 5.4, 0.5)
    head(p, 3 * a, 14 * a - 10 * b)
    jaw(p, -4 * window(t, 5.8, 7.0, 0.3))
    tail_wave(p, t, 8.0, 3.0)
    return ground(p)


def hurt(t):
    p = {}
    k = f(tr((0, 0), (0.07, 1, ease_out), (0.55, 0, smooth)), t)
    stance(p, 0.6)
    add(p, "body", rot=(2 * k, -8 * k, 4 * k))
    head(p, 6 * k, 16 * k); gape(p, 14 * k)
    tail(p, yaw=12 * k)
    return ground(p)


def attack(t):
    """the side snap: the head swung toward the prey, the jaws wide, shut hard at 0.35 s, a short pull back"""
    p = {}
    o = f(tr((0, 0), (0.18, 1, ease_out), (0.32, 1), (0.36, 0, ease_in), (0.8, 0)), t)
    sw = f(tr((0, 0), (0.2, 1, ease_out), (0.5, 1), (0.85, 0, smooth)), t)
    pull = f(tr((0, 0), (0.36, 0), (0.5, 1, ease_out), (0.85, 0, smooth)), t)
    stance(p, 0.65)
    add(p, "body", rot=(2 * o, 6 * sw, 0), pos=(0, 0, -3 * sw + 2 * pull))
    head(p, -4 * pull, 18 * sw, 6 * sw)
    gape(p, 34 * o)
    tail(p, yaw=-12 * sw)
    return ground(p)


def lunge(t):
    """the ambush from the water's edge: the tail drives the front half up and forward, the jaws wide, they shut at
    0.45 s, then it drops back"""
    p = {}
    up = f(tr((0, 0), (0.15, 0.2), (0.4, 1, ease_out), (0.6, 0.8), (1.1, 0, smooth)), t)
    o = f(tr((0, 0), (0.2, 1, ease_out), (0.42, 1), (0.47, 0, ease_in), (1.1, 0)), t)
    stance(p, 0.4 + 0.4 * up)
    add(p, "body", rot=(14 * up, 0, 0), pos=(0, 4 * up, -10 * up))
    head(p, -8 * up, 0)
    gape(p, 36 * o)
    tail(p, pitch=-3 * up, yaw=10 * math.sin(W(t, 0.5)) * window(t, 0.0, 0.5, 0.1))
    for s, _ in SIDES:
        leg(p, "f", s, swing=24 * up, lift=10 * up)
    return ground(p)


def death_roll(t):
    """the prey held in the jaws, it spins over the long axis, the legs tucked, twice round"""
    p = {}
    k = window(t, 0.0, 1.8, 0.15)
    spin = f(tr((0, 0), (0.15, 0), (1.65, 720, smooth), (1.8, 720)), t)
    add(p, "body", rot=(0, 0, spin))
    jaw(p, -3 * (1 - k))
    for s, sx in SIDES:
        add(p, f"thigh_{s}", rot=(-40 * k, 0, -20 * k * sx)); add(p, f"arm_{s}", rot=(-50 * k, 0, -20 * k * sx))
    tail(p, yaw=-10 * k)
    head(p, -4 * k)
    return ground(p)


def tail_sweep(t):
    """on land: the body bent like a bow, the tail swept round to strike what is beside it"""
    p = {}
    sw = f(tr((0, 0), (0.25, -1, ease_out), (0.5, 1, ease_in), (0.65, 1), (1.1, 0, smooth)), t)
    stance(p, 0.7)
    add(p, "body", rot=(0, -10 * sw, 0))
    head(p, 2, 14 * sw)
    tail(p, yaw=-26 * sw)
    return ground(p)


def bask(t):
    """basking on the bank: flat on the belly, the mouth opened wide and held, a slow close at the end"""
    p = {}; breathe(p, t, 5.0, 0.5)
    lie(p)
    o = f(tr((0, 0), (1.0, 1, smooth), (5.0, 1), (6.0, 0, smooth)), t)
    gape(p, 34 * o)
    tail(p, yaw=6)
    return ground(p)


def bellow(t):
    """the male's bellow: the head and the tail raised, the back held at the water line, shivering so the water
    dances on it, the throat pumping; three calls"""
    p = {}
    k = f(tr((0, 0), (0.5, 1, ease_out), (3.4, 1), (4.0, 0, smooth)), t)
    shiver = sum(window(t, c, c + 0.6, 0.08) for c in (0.8, 1.8, 2.8)) * math.sin(W(t, 0.07))
    stance(p, 0.3)
    add(p, "body", rot=(2 * k, 0, 0), pos=(0, 0.25 * shiver, 0))
    head(p, 16 * k, 0)
    tail(p, pitch=-8 * k)
    jaw(p, -3 * sum(window(t, c, c + 0.6, 0.1) for c in (0.8, 1.8, 2.8)))
    return ground(p)


def head_slap(t):
    """lifts the head and slaps the underside of the jaw down on the water: a pop and a splash"""
    p = {}
    up = f(tr((0, 0), (0.5, 1, ease_out), (0.75, 1), (0.85, -0.4, ease_in), (1.0, -0.4), (1.5, 0, smooth)), t)
    stance(p, 0.4)
    head(p, 22 * up, 0, k=0.6)
    jaw(p, -2 * max(0.0, up))
    tail(p, pitch=-3 * max(0.0, up))
    return ground(p)


def chirp(t):
    """the young calling the mother: the head up, the jaws parting a little on each call"""
    p = {}; breathe(p, t, 1.0, 0.6)
    stance(p, 0.5)
    calls = sum(window(t, c, c + 0.15, 0.05) for c in (0.3, 0.7, 1.2))
    head(p, 12 + 3 * calls, 4 * math.sin(W(t, 1.6)))
    jaw(p, -8 * calls)
    tail_wave(p, t, 0.8, 5.0)
    return ground(p)


def eat(t):
    """takes a bite and swallows it the crocodylian way: the jaws snap, then the head is tossed back to send it down"""
    p = {}
    o = f(tr((0, 0), (0.25, 1, ease_out), (0.4, 0, ease_in), (0.9, 0), (1.05, 0.5), (1.2, 0, ease_in), (2.4, 0)), t)
    toss = sum(window(t, c, c + 0.25, 0.08) for c in (0.9, 1.4))
    stance(p, 0.5)
    head(p, -6 * (1 - toss) + 24 * toss, 0)
    gape(p, 26 * o)
    tail_wave(p, t, 2.4, 3.0)
    return ground(p)


def beg(t):
    """asks for food: the head raised toward the owner, the jaws parting, a small step"""
    p = {}; breathe(p, t, 2.2)
    stance(p, 0.55)
    o = window(t, 0.4, 1.6, 0.3)
    head(p, 10 * o + 2 * math.sin(W(t, 2.2)), 4 * math.sin(W(t, 2.2)))
    gape(p, 12 * o)
    tail_wave(p, t, 2.2, 6.0)
    return ground(p)


def tame(t):
    """accepts its owner: settles down onto the belly, the head laid on the ground toward the owner, a long breath"""
    p = {}
    k = f(tr((0, 0), (0.8, 1, ease_out), (2.0, 1), (2.6, 0, smooth)), t)
    breathe(p, t, 2.6, 0.8)
    lie(p, k); stance(p, 0.55 * (1 - k))
    head(p, -3 * k, 0)
    return ground(p)


ANIMS = {
    "idle": (idle, 8.0, True, "Parado", "respira baixo nas patas, ergue e vira a cabeça, abre um pouco a boca"),
    "walk": (walk, WALK[0], True, "Movimento", "andar alto: a barriga fora do chão, a coluna dobrando de lado a cada passo"),
    "run": (run, RUNP[0], True, "Movimento", "o mesmo andar mais rápido e baixo, a cauda abrindo"),
    "swim": (swim, 1.4, True, "Movimento", "só a cauda empurra, as patas deitadas junto ao corpo"),
    "float": (float_, 5.0, True, "Só dele", "boia parado como um tronco, as patas soltas para os lados"),
    "attack": (attack, 0.85, False, "Combate", "a mordida de lado: abre, vira a cabeça, fecha com força"),
    "lunge": (lunge, 1.1, False, "Só dele", "o bote da beira d'água: a cauda joga a frente para cima e para a frente"),
    "death_roll": (death_roll, 1.8, False, "Só dele", "o giro da morte: duas voltas com a presa na boca"),
    "tail_sweep": (tail_sweep, 1.1, False, "Só dele", "dobra o corpo e varre com a cauda o que está do lado"),
    "bask": (bask, 6.0, False, "Só dele", "toma sol deitado na margem com a boca bem aberta"),
    "bellow": (bellow, 4.0, False, "Só dele", "o berro: cabeça e cauda erguidas, as costas tremendo, a água dançando"),
    "head_slap": (head_slap, 1.5, False, "Só dele", "ergue a cabeça e bate a mandíbula na água"),
    "chirp": (chirp, 1.6, False, "Só dele", "o filhote chamando a mãe"),
    "eat": (eat, 2.4, False, "Comer", "morde e joga a cabeça para trás para engolir"),
    "hurt": (hurt, 0.55, False, "Combate", "ao levar dano"),
    "death": (death, 2.6, False, "Combate", "se debate e vira de barriga para cima"),
    "sit": (sit, 8.0, True, "Descanso", "deitado de barriga, a cabeça erguendo de vez em quando"),
    "sleep": (sleep, 9.0, True, "Descanso", "dorme de queixo no chão, a cauda curvada para o lado"),
    "wake_sleep": (wake_sleep, 2.2, False, "Descanso", "acorda e sobe nas patas"),
    "knocked_out": (knocked_out, 4.0, True, "Descanso", "nocauteado, de barriga para cima"),
    "wake": (wake, 3.0, False, "Descanso", "acorda do nocaute: se debate, desvira e levanta"),
    "beg": (beg, 2.2, True, "Domado", "pede comida: ergue a cabeça para o dono e abre a boca"),
    "tame": (tame, 2.6, False, "Domado", "deita e encosta a cabeça no chão virada para o dono"),
}
