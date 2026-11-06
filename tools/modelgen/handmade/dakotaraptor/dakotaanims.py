"""Dakotaraptor animations, from its own study (page "1.9: estudos do Quetzalcoatlus, do Edmontossauro e do
Dakotaraptor").

The plumbing is shared (anim2; theropod.Plan: planting the feet, the neck and tail helpers, and the common set every
biped does the same way: breathing, sniffing, swimming, the knockout). What a big raptor does that the others in the
mod do not is its own:
- the pounce: a crouch with the tail low, a leap feet first with the sickle claws forward, the wings flung out;
- the pin (raptor prey restraint, Fowler et al. 2011): one foot on the prey, the sickle driven in, the body low over it,
  the wings beating to keep its balance while the prey struggles;
- the mantle: the wings spread low over the kill to hide it, the head down tearing (as hawks and eagles do);
- the wing flash: wings thrown open at once and the tail fan raised, to startle prey into running or a rival away;
- it suns with the wings held open, and preens the long wing feathers through the beak... jaws.
"""
import math
import os
import sys
_H = os.path.dirname(os.path.abspath(__file__))
_E = os.path.join(_H, "..", "_engine")
sys.path[:0] = [_H, _E, os.path.join(_E, "plans")]
import proto as P
import dakota
import theropod
from anim2 import add, Track, smooth, ease_out, ease_in, back_out, lowest
from theropod import window, W

# the two sides with their mirror sign (theropod.SIDES holds the gait phase of each leg, not a sign)
SIDES = (("l", 1), ("r", -1))

TAILS = ("tail1", "tail2", "tail3", "tail4", "tail5")
NECKS = ("neck1", "neck2")


def model():
    m = dakota.build(saddle_on=True); P.pack(m, dakota.TEX_W); return m.spec()


S = model()
T = theropod.Plan(S, K=0.9, necks=NECKS, tails=TAILS, lie_drop=16.0, walk=(1.3, 40, 0.6, 6, 1.0),
                  run=(0.56, 84, 0.38, 11, 2.0), arms=0.6, jaw=0.8, reach=0.7)


def tr(*keys): return Track(keys)


def neck(p, pitch=0.0, yaw=0.0, roll=0.0):
    for b, k in zip(NECKS, (0.55, 0.45)):
        add(p, b, rot=(pitch * k, yaw * k, roll * k))


def tail(p, yaw=0.0, pitch=0.0):
    for k, b in enumerate(TAILS):
        w = (1.0, 0.8, 0.6, 0.45, 0.35)[k]
        add(p, b, rot=(pitch * w, yaw * w, 0))


# three ways of opening the folded wing, each found by measuring how much of the feather fan shows from where it is
# meant to be seen (the feathers are 1 px planes: open the wrong way they turn edge-on and vanish):
#   FLASH  straight out at the sides, the fan facing forward (seen by whoever is in front of it);
#   MANTLE forward and down round whatever lies at its feet, the fan facing out and up;
#   SUN    out at the sides and tilted, the fan facing up and out to the light.
FLASH = ((80, -45, 90), -40, 180)
MANTLE = ((150, 0, 40), -80, 105)
SUN = ((60, 0, 60), -40, 180)


def wings(p, k, beat=0.0, how=FLASH):
    """k = 0 folded .. 1 open (how); beat swings them up and down"""
    (ax, ay, az), fx, hx = how
    for s, sx in SIDES:
        add(p, f"arm_{s}", rot=(ax * k, ay * k * sx, (az * k + 25 * beat) * sx))
        add(p, f"forearm_{s}", rot=(fx * k, 0, 0))
        add(p, f"hand_{s}", rot=(hx * k, 0, 0))


# ------------------------------------------------------------------ its own
def pounce(t):
    """crouch, the leap feet first with the sickles forward, the wings flung out, the landing"""
    p = {}
    crouch = f_(tr((0, 0), (0.25, 1, ease_out), (0.4, 1), (0.5, 0, ease_in), (1.0, 0)), t)
    air = f_(tr((0, 0), (0.42, 0), (0.55, 1, ease_out), (0.8, 1), (0.95, 0, ease_in), (1.2, 0)), t)
    add(p, "body", rot=(-6 * crouch + 14 * air, 0, 0), pos=(0, -3 * crouch + 12 * air, -6 * air))
    neck(p, 10 * crouch - 18 * air, 0)
    tail(p, pitch=8 * crouch - 10 * air)
    wings(p, 0.9 * air, 0.3 * air)
    add(p, "jaw", rot=(-20 * air, 0, 0))
    if air > 0.3:
        k = (air - 0.3) / 0.7
        add(p, "body", pos=(0, 2.0, 0))     # off the ground before the legs swing
        for s, _ in SIDES:     # the feet swung forward, toes up, the sickles leading
            add(p, f"thigh_{s}", rot=(-60 * k, 0, 0)); add(p, f"shin_{s}", rot=(40 * k, 0, 0))
            add(p, f"foot_{s}", rot=(-20 * k, 0, 0)); add(p, f"toes_{s}", rot=(-30 * k, 0, 0))
        return p
    return T.stand(p)


def f_(track, t): return float(track(t))


def pin(t):
    """one foot on the prey, the body low over it, the wings beating to keep balance, the jaws striking down"""
    p = {}
    k = f_(tr((0, 0), (0.3, 1, ease_out), (2.6, 1), (3.0, 0)), t)
    beat = math.sin(2 * math.pi * t / 0.35) * k
    bite = sum(math.exp(-((t - c) / 0.07) ** 2) for c in (0.9, 1.6, 2.2))
    add(p, "body", rot=(-8 * k, 0, 3 * beat), pos=(0, -2 * k, -2 * k))
    neck(p, -16 * k - 6 * bite, 0)
    add(p, "jaw", rot=(-20 * bite, 0, 0))
    wings(p, 0.55 * k, 0.3 * beat, how=MANTLE)
    tail(p, pitch=-6 * k, yaw=4 * beat)
    T.plant(p, "l", 6 * k, -8 * k, -10 * k, -30 * k)     # the foot up on the prey
    T.plant(p, "r")
    return p


def mantle(t):
    """the wings spread low over the kill to hide it, the head down tearing, a glance up now and then"""
    p = {}
    k = f_(tr((0, 0), (0.6, 1, ease_out), (4.0, 1), (4.6, 0)), t)
    tear = sum(math.exp(-((t - c) / 0.12) ** 2) for c in (1.2, 1.9, 2.6, 3.2))
    look = math.exp(-((t - 2.25) / 0.2) ** 2)
    add(p, "body", rot=(-8 * k, 0, 0), pos=(0, -2 * k, 0))
    neck(p, -20 * k + 16 * look, 0)
    add(p, "skull", rot=(-6 * tear, 0, 8 * tear), pos=(0, 0, 0))
    add(p, "jaw", rot=(-16 * tear, 0, 0))
    wings(p, k, how=MANTLE)      # spread forward and down round the kill
    tail(p, pitch=-4 * k)
    return T.stand(p)


def wing_flash(t):
    """the wings thrown open at once, the tail fan raised, a hiss with the jaws open; then folded"""
    p = {}
    k = f_(tr((0, 0), (0.12, 1, back_out), (1.0, 1), (1.4, 0)), t)
    add(p, "body", rot=(6 * k, 0, 0), pos=(0, 1 * k, 0))
    neck(p, 10 * k, 0)
    add(p, "jaw", rot=(-22 * k, 0, 0))
    wings(p, k, 0.15 * math.sin(2 * math.pi * t / 0.12) * k)
    tail(p, pitch=-10 * k)
    return T.stand(p)


def sun(t):
    """sunning: the wings held open and drooping, the body still, the eyes half shut"""
    p = {}
    k = f_(tr((0, 0), (0.8, 1, ease_out), (4.2, 1), (5.0, 0)), t)
    T.breathe(p, t, T=3.0, amp=0.5)
    wings(p, k, how=SUN)
    neck(p, 4 * k, 0)
    return T.stand(p)


def preen(t):
    """the neck curls round and the jaws run along the wing feathers, the wing lifted"""
    p = {}
    k = f_(tr((0, 0), (0.5, 1, ease_out), (3.0, 1), (3.6, 0)), t)
    nib = math.sin(2 * math.pi * t / 0.3) * window(t, 0.6, 3.0, 0.2)
    neck(p, -20 * k, 70 * k, 10 * k)
    add(p, "skull", rot=(-16 * k + 3 * nib, 20 * k, 0)); add(p, "jaw", rot=(-5 * max(0, nib), 0, 0))
    add(p, "arm_l", rot=(40 * k, 0, 40 * k)); add(p, "forearm_l", rot=(-30 * k, 0, 0)); add(p, "hand_l", rot=(60 * k, 0, 0))
    return T.stand(p)


BASE = T.anims()
ANIMS = {
    "idle": BASE["idle"], "sniff": BASE["sniff"], "look_back": BASE["look_back"], "shake": BASE["shake"],
    "stretch": BASE["stretch"], "yawn": BASE["yawn"],
    "walk": BASE["walk"], "run": BASE["run"], "stalk": BASE["stalk"], "swim": BASE["swim"],
    "call": BASE["call"], "threat": BASE["threat"],
    "attack": BASE["attack_quick"], "bite": BASE["attack"], "hurt": BASE["hurt"], "death": BASE["death"],
    "eat": BASE["eat"], "drink": BASE["drink"],
    "sit": BASE["sit"], "sleep": BASE["sleep"], "wake": BASE["wake"], "wake_sleep": BASE["wake_sleep"],
    "knocked_out": BASE["knocked_out"], "beg": BASE["beg"], "tame": BASE["tame"],
    "pounce": (pounce, 1.2, False, "Só dele", "o bote: agacha, salta com as foices à frente e as asas abertas"),
    "pin": (pin, 3.0, False, "Só dele", "prende a presa com um pé, bate as asas para se equilibrar e morde"),
    "mantle": (mantle, 4.6, False, "Só dele", "cobre a presa com as asas abertas e come"),
    "wing_flash": (wing_flash, 1.4, False, "Só dele", "abre as asas de repente e ergue o leque da cauda para assustar"),
    "sun": (sun, 5.0, False, "Só dele", "toma sol de asas abertas"),
    "preen": (preen, 3.6, False, "Só dele", "passa as penas da asa pela boca"),
}

# 06/11: the fluid set (dakotaflow.py, docs/estudos/08 and 10): the same names made fluid, and its duel and rest sets
import dakotaflow as FLOW  # noqa: E402
for _n in ("idle", "walk", "run", "stalk", "call", "threat", "attack", "bite", "hurt", "pin", "mantle", "wing_flash", "sun",
           "preen", "sniff", "look_back", "shake", "stretch", "yawn", "eat", "drink", "tame"):
    ANIMS[_n] = (getattr(FLOW, _n),) + ANIMS[_n][1:]
ANIMS.update({
    "guard": (FLOW.guard, FLOW.GUARD_T, True, "Duelo", "em guarda: agachado, asas baixas abertas para a frente, pescoço em S, leque da cauda erguido"),
    "strafe_left": (FLOW.strafe_left, FLOW.STRAFE_T, True, "Duelo", "desliza de lado para a esquerda, a asa de fora aberta como gavião"),
    "strafe_right": (FLOW.strafe_right, FLOW.STRAFE_T, True, "Duelo", "desliza de lado para a direita"),
    "turn_left": (FLOW.turn_left, FLOW.TURN_T, True, "Movimento", "girando no lugar para a esquerda: o pescoço entra na curva primeiro"),
    "turn_right": (FLOW.turn_right, FLOW.TURN_T, True, "Movimento", "girando no lugar para a direita"),
    "feint": (FLOW.feint, FLOW.FEINT_T, False, "Duelo", "finta: meio susto de asas, ergue o pé da foice como quem vai dar o bote, e para"),
    "block": (FLOW.block, FLOW.BLOCK_T, False, "Duelo", "apara com as duas asas jogadas à frente do peito"),
    "recoil": (FLOW.recoil, FLOW.RECOIL_T, False, "Duelo", "o golpe bateu nas asas: cabeça de lado, duas batidas de asa, passo atrás"),
    "submit": (FLOW.submit, FLOW.SUBMIT_T, False, "Duelo", "perdeu: agacha, asas coladas, leque fechado e baixo, vira a cabeça"),
    "lie_down": (FLOW.lie_down, FLOW.LIE_DOWN_T, False, "Descanso", "deitando como ave no ninho"),
    "get_up": (FLOW.get_up, FLOW.GET_UP_T, False, "Descanso", "levantando com as asas meio abertas, sacode as penas"),
    "idle_tired": (FLOW.idle_tired, FLOW.IDLE_TIRED_T, True, "Parado", "cansado: asas soltas para esfriar, boca aberta, garganta vibrando"),
    "walk_tired": (FLOW.walk_tired, FLOW.WALK_TIRED_T, True, "Movimento", "andando cansado depois de uma perseguição"),
})
