"""Therizinosaurus animations, written for it from its own study (page "Terizinossauro: estudo e modelo").

The plumbing is shared (anim2: easing, leg IK; theropod.Plan: planting the feet, the neck spread over its bones, and
the family's common set for what every biped does the same way: breathing, sniffing, swimming, the knockout). What it
does that no other animal of the mod does is its own:
- it feeds high: rises on its legs, hooks a branch with the claws of one hand, pulls it to the beak and strips it
  (Lautenschlager 2014: hook and pull; digging ruled out);
- the display: it rears, spreads both arms with the quill fans open, the six blades out, and clacks them; the male
  lifts his head to show the red throat (Qin et al. 2023: claws more for show than for work);
- it fights with the arms: a downward slash with one hand, a scissor cut with both, a chest shove at close range;
- two males face off with the arms open, never touching, until one turns its head away;
- it rests SITTING on its wide pelvis (Russell & Russell 1993), the trunk upright and the arms folded in front, and
  sleeps that way with the head down on the arms;
- the walk is heavy and slow on four-toed feet, the trunk rocking from side to side, the arms folded so the claws
  clear the ground.
"""
import math
import os
import sys
_H = os.path.dirname(os.path.abspath(__file__))
_E = os.path.join(_H, "..", "_engine")
sys.path[:0] = [_H, _E, os.path.join(_E, "plans")]
import proto as P
import theri
import theropod
from anim2 import add, Track, smooth, ease_out, ease_in, back_out, lowest
from theropod import window, W, SIDES

TAILS = ("tail1", "tail2", "tail3", "tail4")
NECKS = ("neck1", "neck2", "neck3")


def model():
    m = theri.build(saddle_on=True); P.pack(m, theri.TEX_W); return m.spec()


S = model()
T = theropod.Plan(S, K=1.0, necks=NECKS, tails=TAILS, lie_drop=24.0, walk=(2.2, 56, 0.64, 7, 1.2),
                  run=(1.1, 96, 0.5, 11, 2.2), arms=0.5, jaw=0.3, reach=0.8)
SADDLE_MATS = theri.SADDLE_MATS


def tr(*keys): return Track(keys)


def neck(p, pitch=0.0, yaw=0.0, roll=0.0, s=(0.45, 0.3, 0.25)):
    for b, k in zip(NECKS, s):
        add(p, b, rot=(pitch * k, yaw * k, roll * k))


def tail(p, yaw=0.0, pitch=0.0):
    for k, b in enumerate(TAILS):
        w = (1.0, 0.85, 0.7, 0.55)[k]
        add(p, b, rot=(pitch * w, yaw * w, 0))


def arm(p, s, a=0.0, f=0.0, h=0.0, out=0.0, twist=0.0):
    """one arm: a = upper arm swing (positive forward and up), f = forearm, h = hand, out = spread sideways"""
    sx = 1 if s == "l" else -1
    add(p, f"arm_{s}", rot=(a, twist * sx, out * sx))
    add(p, f"forearm_{s}", rot=(f, 0, 0.2 * out * sx))
    if h: add(p, f"hand_{s}", rot=(h, 0, 0))


def arms(p, a=0.0, f=0.0, h=0.0, out=0.0):
    for s, _ in SIDES: arm(p, s, a, f, h, out)


def fold(p, k):
    """the arms drawn in a little tighter than at rest (walking, resting): the rest pose already holds them folded"""
    arms(p, -4 * k, 10 * k, 8 * k, 4 * k)


# ------------------------------------------------------------------ movement
def walk(t):
    p = T.walk(t)
    fold(p, 0.8)
    return p


def run(t):
    p = T.run(t); fold(p, 1.0); return p


def swim(t):
    p = T.swim(t); fold(p, 0.6); return p


# ------------------------------------------------------------------ standing
def idle(t):
    p = T.idle(t)
    br = math.sin(W(t, 2.0))
    arms(p, 1.0 * br, -1.5 * br)
    # now and then the claws of one hand tap together
    tap = window(t, 5.0, 6.2, 0.15) * math.sin(2 * math.pi * 3 * t)
    add(p, "hand_r", rot=(6 * tap, 0, 0))
    return p


def browse(t):
    """it rises on its legs and stretches the neck up, reaches high with the left arm, hooks a branch with the
    claws, pulls it down to the beak and strips the leaves in three nips, then lets the branch spring back"""
    p = {}
    up = float(tr((0, 0), (0.6, 1, ease_out), (3.6, 1), (4.2, 0))(t))
    reach = float(tr((0, 0), (0.5, 0), (1.1, 1, ease_out), (1.4, 1), (2.2, 0.35, ease_in), (3.4, 0.35), (3.8, 0))(t))
    nip = sum(math.exp(-((t - c) / 0.06) ** 2) for c in (2.4, 2.75, 3.1))
    add(p, "body", rot=(12 * up, 0, 2 * up), pos=(0, 3 * up, 0))
    neck(p, 26 * up - 12 * (1 - reach) * up, 0)
    add(p, "skull", rot=(-8 * up + 6 * nip, 0, 0)); add(p, "jaw", rot=(-10 * nip, 0, 0))
    arm(p, "l", 140 * reach + 30 * (1 - reach) * up, -20 * reach + 20 * (1 - reach) * up, 10 * reach, 10 * reach)
    arm(p, "r", 10 * up, 20 * up, 10 * up)
    tail(p, pitch=-4 * up)
    return T.stand(p)


def claw_display(t):
    """the warning: it rears, the arms spread wide with the quill fans open and the blades out, and the claws clack
    three times; the head lifts (the male's red throat shows); then it drops back"""
    p = {}
    k = float(tr((0, 0), (0.5, 1, back_out), (2.8, 1), (3.4, 0))(t))
    clack = sum(math.exp(-((t - c) / 0.06) ** 2) for c in (1.2, 1.6, 2.0))
    add(p, "body", rot=(16 * k, 0, 0), pos=(0, 1.5 * k, 0))
    neck(p, 18 * k, 0); add(p, "skull", rot=(-12 * k, 0, 0)); add(p, "jaw", rot=(-6 * k, 0, 0))
    for s, _ in SIDES:
        arm(p, s, 28 * k + 8 * clack, -14 * k + 16 * clack, -10 * k + 18 * clack, 82 * k - 22 * clack)
    tail(p, pitch=-6 * k)
    return T.stand(p)


def rival(t):
    """two males face to face: arms half open, the trunk upright, the head turning to show one side and the other,
    a sway; at the end it turns its head away"""
    p = {}
    k = float(tr((0, 0), (0.6, 1, ease_out), (4.2, 1), (4.8, 0))(t))
    sw = math.sin(2 * math.pi * 0.6 * t)
    away = window(t, 3.6, 4.6, 0.2)
    add(p, "body", rot=(10 * k, 4 * sw * k, 3 * sw * k), pos=(0, 2 * k, 0))
    neck(p, 10 * k, 14 * sw * k + 40 * away, 0); add(p, "skull", rot=(-6 * k, 10 * sw * k, -6 * sw * k))
    for s, _ in SIDES:
        arm(p, s, 25 * k, -10 * k, 10 * k, 34 * k)
    tail(p, yaw=-6 * sw * k)
    return T.stand(p)


def preen(t):
    """quill care: the neck curls down to the left forearm and the beak runs along the fan"""
    p = {}
    k = float(tr((0, 0), (0.6, 1, ease_out), (3.2, 1), (3.8, 0))(t))
    nib = math.sin(2 * math.pi * 5 * t) * window(t, 0.8, 3.0, 0.2)
    add(p, "body", rot=(-4 * k, 10 * k, 0))
    neck(p, -50 * k, 60 * k, 0, s=(0.4, 0.35, 0.25)); add(p, "skull", rot=(-20 * k + 4 * nib, 20 * k, 0))
    add(p, "jaw", rot=(-4 * max(0, nib), 0, 0))
    arm(p, "l", 30 * k, 10 * k, 10 * k, 30 * k)
    return T.stand(p)


# ------------------------------------------------------------------ feeding
def eat(t):
    """from low plants or the hand: the neck comes down, nips twice, lifts and swallows"""
    p = {}
    down = float(tr((0, 0), (0.5, 1, ease_out), (2.0, 1), (2.6, 0))(t))
    nip = sum(math.exp(-((t - c) / 0.06) ** 2) for c in (0.9, 1.4))
    gulp = math.exp(-((t - 2.3) / 0.1) ** 2)
    add(p, "body", rot=(-10 * down, 0, 0), pos=(0, -2 * down, 0))
    neck(p, -70 * down + 6 * gulp, 0); add(p, "skull", rot=(-10 * down + 4 * nip, 0, 0))
    add(p, "jaw", rot=(-12 * nip, 0, 0))
    fold(p, 0.5 * down)
    tail(p, pitch=6 * down)
    return T.stand(p)


# ------------------------------------------------------------------ combat
def attack(t):
    """the slash: the right arm rises high and back and cuts down and across with the blades; the body leans into it"""
    p = {}
    raise_ = float(tr((0, 0), (0.35, 1, ease_out), (0.45, 1), (0.6, -0.4, ease_in), (0.8, -0.3), (1.2, 0))(t))
    add(p, "body", rot=(8 * max(0, raise_) - 6 * max(0, -raise_), -10 * raise_, 4 * raise_))
    neck(p, 6 * raise_, -8 * raise_)
    arm(p, "r", 150 * max(0, raise_) - 40 * max(0, -raise_), -20 * max(0, raise_), -10 * max(0, raise_), 20 * max(0, raise_))
    arm(p, "l", 20 * abs(raise_), 10, 10, 10 * abs(raise_))
    tail(p, yaw=8 * raise_)
    return T.stand(p)


def scissor(t):
    """both arms open wide and cut in together, crossing in front: the blades meet like shears"""
    p = {}
    k = float(tr((0, 0), (0.4, 1, ease_out), (0.5, 1), (0.65, -0.5, ease_in), (0.9, -0.4), (1.4, 0))(t))
    add(p, "body", rot=(10 * max(0, k) - 4 * max(0, -k), 0, 0), pos=(0, 2 * max(0, k), -3 * max(0, -k)))
    neck(p, 8 * max(0, k) - 10 * max(0, -k), 0)
    for s, _ in SIDES:
        arm(p, s, 80 * max(0, k) + 30 * max(0, -k), -10, -10, 60 * max(0, k) - 30 * max(0, -k))
    tail(p, pitch=-4 * k)
    return T.stand(p)


def shove(t):
    """at close range: it drops the trunk and drives the chest forward"""
    p = {}
    k = float(tr((0, 0), (0.3, -0.5), (0.45, 1, ease_in), (0.6, 1), (1.0, 0))(t))
    add(p, "body", rot=(-8 * k, 0, 0), pos=(0, -2 * abs(k), -8 * k))
    neck(p, -10 * k, 0); fold(p, 0.6)
    tail(p, pitch=4 * k)
    return T.stand(p)


def threat(t):
    """the short warning before a fight: a half display with one arm, the claws clacked once"""
    p = {}
    k = float(tr((0, 0), (0.4, 1, ease_out), (1.6, 1), (2.0, 0))(t))
    clack = math.exp(-((t - 1.0) / 0.06) ** 2)
    add(p, "body", rot=(8 * k, 0, 0))
    neck(p, 6 * k, 0); add(p, "skull", rot=(-6 * k, 0, 0))
    arm(p, "r", 50 * k, -10 * k + 10 * clack, 10 * clack, 36 * k)
    arm(p, "l", 20 * k, 10 * k, 0, 16 * k)
    return T.stand(p)


def hurt(t):
    p = T.hurt(t); e = math.exp(-(t / 0.16)) * smooth(t / 0.04)
    arms(p, 20 * e, 10 * e, 0, 16 * e)
    return p


# ------------------------------------------------------------------ resting: sitting on the pelvis
def ground_fit(p):
    lo = lowest(S, p, skip_mats=SADDLE_MATS); add(p, "root", pos=(0, -lo, 0)); return p


SEAT = {"thigh": (70, 0, 0), "shin": (-120, 0, 0), "foot": (50, 0, 0)}


def seat(p, k):
    """k = 0 standing .. 1 sitting on the pelvis: the hips go down to the ground, the legs fold forward under it,
    the trunk turns upright and the arms fold in front of the chest"""
    add(p, "body", rot=(26 * k, 0, 0), pos=(0, -38 * k, 6 * k))
    for s, _ in SIDES:
        for b, r in SEAT.items(): add(p, f"{b}_{s}", rot=tuple(x * smooth(k) for x in r))
    neck(p, -20 * k, 0); add(p, "skull", rot=(-6 * k, 0, 0))
    arms(p, 20 * k, 60 * k, 30 * k, -6 * k)
    tail(p, pitch=12 * k)
    return p


def sit(t):
    p = {}; br = math.sin(W(t, 3.4))
    seat(p, 1.0); add(p, "body", rot=(0.8 * br, 0, 0))
    look = float(tr((0, 0), (1.2, 0), (1.6, 1, ease_out), (3.2, 1), (3.6, 0), (6.0, 0))(t))
    neck(p, -0.6 * br, 24 * look); add(p, "skull", rot=(0, 14 * look, -6 * look))
    return ground_fit(p)


def head_rest(p, k):
    """sleeping: the neck lowers and the head rests on the folded arms"""
    neck(p, -60 * k, 0, 0, s=(0.5, 0.3, 0.2)); add(p, "skull", rot=(-10 * k, 0, 0))


def sleep(t):
    p = {}; br = math.sin(W(t, 4.6))
    seat(p, 1.0); head_rest(p, 1.0)
    add(p, "body", rot=(-6 + 0.8 * br, 0, 0), pos=(0, 0.3 * br, 0))
    return ground_fit(p)


def wake_sleep(t):
    p = {}
    hd = float(tr((0, 1), (0.8, 0, ease_out), (2.8, 0))(t))
    up = float(tr((0, 1), (1.4, 1), (2.3, 0, back_out), (2.8, 0))(t))
    seat(p, up); head_rest(p, hd)
    add(p, "body", rot=(-6 * hd, 0, 0))
    sh = window(t, 1.0, 1.4, 0.08) * math.sin(2 * math.pi * 7 * t)
    add(p, "body", rot=(0, 0, 3 * sh)); arms(p, 0, 0, 0, 14 * abs(sh))
    return ground_fit(p)


def brood(t):
    """on the buried clutch: sitting, the arms spread low over the ground, the head turning"""
    p = {}; br = math.sin(W(t, 3.4))
    seat(p, 1.0)
    arms(p, 20, -30, -10, 26)
    look = math.sin(2 * math.pi * t / 7.0)
    neck(p, -10 - 0.6 * br, 20 * look); add(p, "skull", rot=(0, 10 * look, 0))
    return ground_fit(p)


def knocked_out(t):
    p = T.knocked_out(t); fold(p, 0.6); arms(p, 10, 0, 0, 10); return ground_fit(p)


def wake(t):
    p = T.wake(t); fold(p, 0.8); return ground_fit(p)


def death(t):
    p = T.death(t)
    k = smooth((t - 0.2) / 0.6)
    arms(p, 20 * window(t, 0.1, 1.0, 0.2), 20 * k, 10 * k, 20 * window(t, 0.1, 1.0, 0.2))
    return ground_fit(p)


# ------------------------------------------------------------------ with its owner
def beg(t):
    """asks for food: the head low toward the owner, a little bob, the claws of one hand tapping"""
    p = {}; br = math.sin(W(t, 1.6))
    add(p, "body", rot=(-6, 0, 0), pos=(0, -1.0, 0))
    neck(p, -30 + 4 * br, 0); add(p, "skull", rot=(10, 0, 8 * math.sin(W(t, 3.2))))
    tap = math.sin(2 * math.pi * 3 * t)
    arm(p, "r", -10, 20, 10 + 8 * tap, 6)
    fold(p, 0.4)
    tail(p, yaw=3 * math.sin(W(t, 1.6)))
    return T.stand(p)


def tame(t):
    """the moment it accepts the owner: the arms come down and fold, the neck lowers, a slow shake of the quills"""
    p = {}
    k = float(tr((0, 0), (0.5, 1, ease_out), (1.8, 1), (2.6, 0))(t))
    sh = window(t, 1.2, 1.8, 0.1) * math.sin(2 * math.pi * 8 * t)
    add(p, "body", rot=(-6 * k, 0, 3 * sh), pos=(0, -2 * k, 0))
    neck(p, -34 * k, 0); add(p, "skull", rot=(8 * k, 0, 0))
    fold(p, k); arms(p, 0, 0, 0, 10 * abs(sh))
    return T.stand(p)


def baby_browse(t):
    """the young copy the adults on low bushes: a reach with one arm and a nip"""
    p = {}
    k = float(tr((0, 0), (0.4, 1, ease_out), (1.8, 1), (2.3, 0))(t))
    nip = math.exp(-((t - 1.3) / 0.07) ** 2)
    neck(p, -10 * k, 0); add(p, "skull", rot=(4 * nip, 0, 0)); add(p, "jaw", rot=(-10 * nip, 0, 0))
    arm(p, "r", 60 * k, 20 * k, -10 * k, 6 * k)
    return T.stand(p)


BASE = T.anims()
ANIMS = {
    "idle": (idle, 8.0, True, "Parado", "respira, olha em volta; às vezes bate as garras de uma mão"),
    "sniff": BASE["sniff"], "look_back": BASE["look_back"], "shake": BASE["shake"], "stretch": BASE["stretch"],
    "walk": (walk, T.walk_p[0], True, "Movimento", "passo pesado de quatro dedos, o tronco balança, garras dobradas"),
    "run": (run, T.run_p[0], True, "Movimento", "trote pesado, garras recolhidas"),
    "swim": (swim, 1.6, True, "Movimento", "dentro da água"),
    "call": BASE["call"],
    "browse": (browse, 4.2, False, "Só dele", "ergue-se, engancha um galho alto com as garras, puxa e arranca as folhas"),
    "claw_display": (claw_display, 3.4, False, "Só dele", "a exibição: ergue-se, abre os braços com os leques e bate as garras"),
    "rival": (rival, 4.8, False, "Só dele", "dois machos frente a frente de braços abertos, até um virar a cabeça"),
    "preen": (preen, 3.8, False, "Só dele", "cuida das penas do braço com o bico"),
    "eat": (eat, 2.6, False, "Comer", "abaixa o pescoço, belisca e engole"),
    "drink": BASE["drink"],
    "attack": (attack, 1.2, False, "Combate", "corte de cima para baixo com as lâminas de um braço"),
    "scissor": (scissor, 1.4, False, "Só dele", "corte duplo: os dois braços fecham como tesoura"),
    "shove": (shove, 1.0, False, "Só dele", "empurrão de peito quando o alvo está colado"),
    "threat": (threat, 2.0, False, "Combate", "aviso curto: meio braço erguido, bate as garras"),
    "hurt": (hurt, 0.6, False, "Combate", "ao levar dano"),
    "death": (death, 3.0, False, "Combate", "ao morrer"),
    "sit": (sit, 6.0, True, "Descanso", "sentado sobre o quadril, tronco em pé, braços dobrados à frente"),
    "sleep": (sleep, 9.0, True, "Descanso", "dorme sentado, a cabeça apoiada nos braços"),
    "wake_sleep": (wake_sleep, 2.8, False, "Descanso", "acorda, sacode as penas e levanta"),
    "brood": (brood, 7.0, True, "Só dele", "sobre o ninho enterrado, braços abertos baixos"),
    "knocked_out": (knocked_out, 4.0, True, "Descanso", "nocauteado, de lado"),
    "wake": (wake, 3.0, False, "Descanso", "acorda do nocaute"),
    "beg": (beg, 1.6, True, "Domado", "pede comida: cabeça baixa, bate as garras de leve"),
    "tame": (tame, 2.6, False, "Domado", "abaixa os braços e o pescoço, sacode as penas"),
    "baby_browse": (baby_browse, 2.3, False, "Só dele", "o filhote imita os adultos nos arbustos baixos"),
}


# ------------------------------------------------------------------ the fluid set and its own fighting (06/11/2026, theriflow.py)
import theriflow as FLOW  # noqa: E402
for _n in ("idle", "walk", "run", "swim", "browse", "claw_display", "rival", "preen", "eat", "attack", "scissor", "shove", "threat",
           "hurt", "death", "sit", "sleep", "wake_sleep", "brood", "knocked_out", "wake", "beg", "tame", "baby_browse"):
    ANIMS[_n] = (getattr(FLOW, _n),) + ANIMS[_n][1:]
ANIMS.update({
    "claw_slash": (FLOW.claw_slash, FLOW.SLASH_T, False, "Duelo", "combo: corte da direita (0,55 s), revés da esquerda (1,1 s) e tesoura (1,75 s)"),
    "guard": (FLOW.guard, FLOW.GUARD_T, True, "Duelo", "em guarda: tronco erguido, pescoço recolhido, os dois braços como foices"),
    "strafe_left": (FLOW.strafe_left, FLOW.STRAFE_T, True, "Duelo", "passo lateral arrastado para a esquerda (não cruza os pés)"),
    "strafe_right": (FLOW.strafe_right, FLOW.STRAFE_T, True, "Duelo", "passo lateral arrastado para a direita"),
    "turn_left": (FLOW.turn_left, FLOW.TURN_T, True, "Movimento", "gira no lugar para a esquerda: pivota no pé de dentro"),
    "turn_right": (FLOW.turn_right, FLOW.TURN_T, True, "Movimento", "gira no lugar para a direita"),
    "feint": (FLOW.feint, FLOW.FEINT_T, False, "Duelo", "blefe: os leques se abrem e o peito salta, sem corte, e recua"),
    "block": (FLOW.block, FLOW.BLOCK_T, False, "Duelo", "escudo: o leque do antebraço cruzado na frente do peito"),
    "recoil": (FLOW.recoil, FLOW.RECOIL_T, False, "Duelo", "o corte bateu em defesa: o braço volta, os leques tremem, um passo atrás"),
    "submit": (FLOW.submit, FLOW.SUBMIT_T, False, "Duelo", "desiste: braços dobrados no peito, leques fechados, afunda e vira a cabeça"),
    "lie_down": (FLOW.lie_down, FLOW.LIE_DOWN_T, False, "Descanso", "senta sobre o quadril (de pé para sentado)"),
    "get_up": (FLOW.get_up, FLOW.GET_UP_T, False, "Descanso", "levanta de sentado, o pescoço joga o peso para a frente"),
    "idle_tired": (FLOW.idle_tired, FLOW.IDLE_TIRED_T, True, "Parado", "cansado: a barriga arfa, bico aberto, braços pendurados"),
    "walk_tired": (FLOW.walk_tired, FLOW.WALK_TIRED_T, True, "Movimento", "andando cansado: passos curtos, o tronco rola mais"),
})

# 06/11: the epic duel's three moves (therifight.py; the Java slides the body in the lunge and turns it in the stagger)
import therifight as FIGHT  # noqa: E402
for _n, _when in (
        ("lunge", "bote do duelo: recua no quadril com os braços no alto, passo largo e as duas garras-lâmina cortam em cruz aos 0,50 s, a barriga balança depois, volta à guarda"),
        ("parry", "apara: o antebraço esquerdo cruza com as garras viradas e desvia o golpe, a cabeça atrás do braço; no giro de volta o braço direito corta aos 0,60 s"),
        ("stagger", "foi aparado: a barriga rola para a direita, braços abertos buscando equilíbrio, leques tremendo, passo largo de lado e o outro pé arrastado, sacode as penas")):
    ANIMS[_n] = (getattr(FIGHT, _n), getattr(FIGHT, _n.upper() + "_T"), False, "Duelo", _when)
