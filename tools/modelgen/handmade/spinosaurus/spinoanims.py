"""Spinosaurus animations: the big-theropod template (26 poses of the T. rex, on this rig: two neck bones, five tail
bones, shorter legs) + its own four: fish, sail display, thumb-claw swipe and a tail-driven swim (replaces the
template's)."""
import math
import os
import sys
_E = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_engine")
sys.path[:0] = [_E, os.path.join(_E, "plans")]
import proto as P
import spino
import theropod
from anim2 import add, Track, smooth, ease_out, ease_in, back_out, ground_fit
from theropod import tr, window, W, SIDES


def model():
    m = spino.build(); P.pack(m, 256); return m.spec()


S = model()
T = theropod.Plan(S, K=0.9, necks=("neck", "neck2"), tails=("tail1", "tail2", "tail3", "tail4", "tail5"),
                  lie_drop=25.0, lie_ankle_y=3.6, walk=(2.0, 62, 0.62, 8, 1.4), run=(0.85, 108, 0.42, 14, 2.6), jaw=0.62, reach=0.6)
TAILS = T.tails


def fish(t):
    """wading strike: head low over the water, still as a heron, the snap, the toss and the gulp"""
    p = {}
    low = float(tr((0, 0), (0.7, 1), (2.0, 1), (2.12, 1.25, ease_in), (2.35, 0.55, ease_out), (3.0, 0.4), (3.8, 0))(t))
    snap = math.exp(-((t - 2.12) / 0.06) ** 2)
    toss = float(tr((0, 0), (2.3, 0), (2.5, 1, ease_out), (2.75, 0.2), (3.0, 0.8), (3.2, 0))(t))
    add(p, "body", rot=(-7 * low, 0, 0), pos=(0, -2.5 * low, -2 * snap))
    T.neck(p, (-22 * low + 22 * toss, 0, 0))
    add(p, "skull", rot=(-8 * low - 5 * snap + 14 * toss, 0, 8 * math.sin(2 * math.pi * 3 * t) * window(t, 2.4, 3.1, 0.1)))
    jaw = float(tr((0, 0), (1.9, -2), (2.05, -24, ease_out), (2.14, -2, ease_in), (2.5, -4), (2.6, -16), (2.7, -3), (2.85, -14), (2.95, -2), (3.8, 0))(t))
    add(p, "jaw", rot=(jaw, 0, 0))
    add(p, "skull", rot=(8 * math.exp(-((t - 3.3) / 0.1) ** 2), 0, 0))      # gulp
    T.tail(p, t, yaw=0.5, T=4, base_pitch=4 * low)
    T.arms(p, -6 * low, 10 * low)
    return T.stand(p)


def display(t):
    """the sail shown: rear up a little, arch the back so the sail stands tall, turn it to the rival, hiss"""
    p = {}
    k = float(tr((0, 0), (0.6, 1, ease_out), (2.6, 1), (3.2, 0))(t))
    turn = math.sin(2 * math.pi * (t - 0.6) / 2.0) * window(t, 0.6, 2.6, 0.3)
    add(p, "body", rot=(-6 * k, 6 * turn, 7 * turn * k), pos=(0, 1.5 * k, 0))
    T.neck(p, (16 * k, -10 * turn, 0)); add(p, "skull", rot=(-8 * k, -6 * turn, 0))
    hiss = window(t, 1.0, 2.4, 0.2)
    add(p, "jaw", rot=(-10 * hiss - 1.2 * math.sin(2 * math.pi * 13 * t) * hiss, 0, 0))
    T.tail(p, t, yaw=3 * k, T=2.0, base_pitch=3 * k)
    T.arms(p, -18 * k, 22 * k)
    for s, sx in (("l", 1), ("r", -1)): add(p, f"hand_{s}", rot=(-20 * k, 0, 0))
    return T.stand(p)


def swipe(t):
    """thumb-claw swipe with the left arm, the head pulled back out of the way"""
    p = {}
    wind = float(tr((0, 0), (0.3, 1, ease_out), (0.42, 1), (0.55, -1, ease_in), (0.8, -0.6), (1.3, 0))(t))
    a = max(0, wind); b = max(0, -wind)
    add(p, "body", rot=(-4 * a + 5 * b, 6 * a - 8 * b, -3 * a + 4 * b), pos=(0, 0, -3 * b))
    T.neck(p, (8 * a - 4 * b, -10 * a + 6 * b, 0)); add(p, "skull", rot=(4 * a, -4 * a, 0)); add(p, "jaw", rot=(-10 * a - 6 * b, 0, 0))
    add(p, "arm_l", rot=(-75 * a + 50 * b, 0, 14 * a - 6 * b)); add(p, "forearm_l", rot=(40 * a - 45 * b, 0, 0)); add(p, "hand_l", rot=(25 * a - 45 * b, 0, 0))
    add(p, "arm_r", rot=(-10 * a, 0, 0))
    T.tail(p, t, yaw=2, T=1.3, lag=0.4)
    return T.stand(p)


def swim(t):
    """tail-driven: the paddle sweeps in a wave from hip to tip, the legs trail and kick slowly, arms folded"""
    Tm = 1.8; w = W(t, Tm); p = {}
    add(p, "root", pos=(0, -17, 0))      # ~1 block lower: in game the whole flank rode above the water line
    add(p, "body", rot=(2 + 1.0 * math.sin(2 * w), 4 * math.sin(w), 2 * math.sin(w + 0.4)), pos=(0, 0.8 * math.sin(2 * w), 0))
    T.neck(p, (-6 - 1.5 * math.sin(2 * w + 0.5), -3 * math.sin(w - 0.4), 0)); add(p, "skull", rot=(10, -2 * math.sin(w - 0.9), 0))
    for i, b in enumerate(TAILS):
        add(p, b, rot=(0, -(4 + 3.2 * i) * math.sin(w - 0.7 * (i + 1)), 0))
    for s, o in SIDES:
        f = w + o * 2 * math.pi       # one slow kick per stroke (w * 0.5 left the loop open: the legs jumped at the seam)
        add(p, f"thigh_{s}", rot=(-30 + 12 * math.sin(f), 0, 0)); add(p, f"shin_{s}", rot=(-10 - 10 * math.cos(f), 0, 0))
        add(p, f"foot_{s}", rot=(40 + 10 * math.cos(f + 0.6), 0, 0)); add(p, f"toes_{s}", rot=(-30, 0, 0))
    T.arms(p, -30, 30)
    return p


ANIMS = T.anims()
ANIMS["swim"] = (swim, 1.8, True, "Movimento", "dentro da água: nada com a cauda (o dorso e a vela ficam fora d'água)")
ANIMS["fish"] = (fish, 3.8, False, "Comer", "pescando na beira do rio ou no raso (o bote acerta aos 2,1 s)")
ANIMS["display"] = (display, 3.2, False, "Voz", "mostra a vela a um rival ou a quem chega perto, antes de atacar")
ANIMS["swipe"] = (swipe, 1.3, False, "Combate", "golpe com a garra do polegar, alternando com a mordida (acerta aos 0,55 s)")
STANDING = theropod.STANDING + ("fish", "display", "swipe")

# 06/11: the fluid set (spinoflow.py, docs/estudos/08 and 10): the same names made fluid, its sail display and gaff
# hook, and the duel and rest sets of ApexTheropod (so the Spinosaurus is ready when its duel is switched on). The jaw
# of every new pose is scaled like the template's (T.jaw: the long thin jaws open less).
import spinoflow as FLOW  # noqa: E402
for _n in ("idle", "walk", "run", "stalk", "roar", "call", "threat", "attack", "attack_quick", "hurt", "swipe", "display", "fish",
           "sniff", "look_back", "shake", "yawn", "stretch", "eat", "drink", "tame"):
    ANIMS[_n] = (T.scaled(getattr(FLOW, _n)),) + ANIMS[_n][1:]
ANIMS["swipe"] = (T.scaled(FLOW.swipe), 1.3, False, "Combate", "golpe com a garra do polegar esquerdo, alternando com a mordida (acerta aos 0,55 s)")
ANIMS["attack"] = (T.scaled(FLOW.attack), 2.0, False, "Combate", "bote de crocodilo: a cabeça vem de lado, fecha aos 0,55 s e sacode")
ANIMS["attack_quick"] = (T.scaled(FLOW.attack_quick), 0.9, False, "Combate", "bote de garça: o focinho dispara reto e fecha aos 0,3 s")
for _n, _when, _cat in (
        ("sail_display", "vira de lado para o rival em dois passos, arqueia o dorso e mostra a vela inteira, e volta", "Voz"),
        ("claw_swipe", "gancho duplo: ergue os dois braços e crava as garras dos polegares puxando para o peito (acerta aos 0,62 s)", "Combate"),
        ("guard", "em guarda: de lado para o rival, braços erguidos com as garras armadas, focinho apontado", "Duelo"),
        ("strafe_left", "passos pesados de lado para a esquerda, a vela virada para o rival", "Duelo"),
        ("strafe_right", "passos pesados de lado para a direita", "Duelo"),
        ("turn_left", "girando no lugar para a esquerda: o focinho entra na curva, a vela balança atrasada", "Movimento"),
        ("turn_right", "girando no lugar para a direita", "Movimento"),
        ("feint", "finta: ergue a garra e lança o focinho, mas recolhe os dois", "Duelo"),
        ("block", "apara a mordida com o antebraço na frente do focinho", "Duelo"),
        ("recoil", "o bote bateu no braço do outro: o focinho vai de lado, um passo atrás", "Duelo"),
        ("submit", "perdeu: abaixa, vira a vela para longe, focinho no chão, volta para a água", "Duelo"),
        ("shove", "pancada de flanco: joga o lado e a vela contra o rival", "Duelo"),
        ("bite_low", "colherada rente ao chão, como quem tira peixe do raso (fecha aos 0,4 s)", "Combate"),
        ("bite_side", "varrida de lado com as mandíbulas abertas (fecha aos 0,45 s)", "Combate"),
        ("snort", "gesto sorteado parado: bufa e sacode o focinho", "Parado"),
        ("settle", "gesto sorteado parado: troca o peso de pé, a vela balança depois", "Parado"),
        ("scan", "gesto sorteado parado: ergue o focinho e olha a água de lado a lado", "Parado"),
        ("lie_down", "deitando (de pé para sentado)", "Descanso"),
        ("get_up", "levantando (de sentado para de pé)", "Descanso"),
        ("fall_asleep", "deitando para dormir: boceja e abaixa a cabeça", "Descanso"),
        ("idle_tired", "cansado: boca aberta como crocodilo, peito arfando", "Parado"),
        ("walk_tired", "andando cansado depois de uma perseguição", "Movimento")):
    _len = {"snort": 1.4}.get(_n) or getattr(FLOW, _n.upper().replace("_LEFT", "").replace("_RIGHT", "") + "_T")
    _loop = _n in ("guard", "strafe_left", "strafe_right", "turn_left", "turn_right", "idle_tired", "walk_tired")
    ANIMS[_n] = (T.scaled(getattr(FLOW, _n)), _len, _loop, _cat, _when)
STANDING = STANDING + ("guard", "block", "feint", "claw_swipe", "bite_low", "bite_side", "snort", "scan", "idle_tired")

# 06/11: the epic duel's three moves (spinofight.py; the Java slides the body in the lunge and turns it in the stagger)
import spinofight as FIGHT  # noqa: E402
for _n, _when in (
        ("lunge", "bote do duelo: focinho armado de lado, empurra com a perna de trás e fecha de lado como crocodilo aos 0,50 s, os ganchos dos polegares vêm junto, sacode e volta à guarda"),
        ("parry", "apara: a garra do polegar varre o golpe para fora, o focinho recua; aproveita o giro e estala de volta aos 0,60 s"),
        ("stagger", "foi aparado: tranco para a direita, cabeça jogada, um pé cruza e o outro arrasta, a vela balança duas vezes, sacode o focinho")):
    ANIMS[_n] = (T.scaled(getattr(FIGHT, _n)), getattr(FIGHT, _n.upper() + "_T"), False, "Duelo", _when)
STANDING = STANDING + ("lunge", "parry", "stagger")
