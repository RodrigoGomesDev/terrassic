"""Velociraptor: the fluid set (06/11/2026), after the T. rex's (docs/estudos/08_ANIMACAO_RAXIORES.md) and in the raptor's
own style (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md: the 1971 "Fighting Dinosaurs" fossil, the sickle in the
throat of the Protoceratops; prey restraint with the feet, Fowler et al. 2011; leaps, kicks, hops back out of reach).

The same rules as the T. rex, at a raptor's speed and weight:
  * NOTHING STOPS: every one-shot carries the breathing (`alive` / `alive_upper`), fast and shallow (a small animal);
    the idle cycles divide its 5.4 s loop and never line up (breath 1.35 s, weight 5.4 s, tail 2.7 s).
  * NOTHING SWITCHES: the bird head still snaps to look and holds (that is the raptor), but every snap now overshoots a
    little and settles (`bird`), and the head drifts while it holds; every effect has an envelope.
  * THREE BEATS: anticipation (the weight back, the foot drawn up, the head cocked), a fast strike, follow-through and
    a settle that passes rest and comes back (`back_out`).
  * LIGHT AND SPRINGY: the gait drops fast onto each foot and rebounds fast (a light runner, not a heavy one); the hips
    roll over the stance foot and each thigh cancels it, so the planted foot does not slide.
  * THE TAIL IS A ROD: it swings from its base and the rest only gives a little, late (`rod`); the wings lag the body.
"""
import math

from anim2 import Track, smooth, ease_in, ease_out, back_out, ground_fit, solve_leg2
import raptanims as A

add, tr, window, plant, stand, wings, lids, tail = A.add, A.tr, A.window, A.plant, A.stand, A.wings, A.lids, A.tail
SIDES = A.SIDES
S = A.S

_SNIFF, _LOOK_BACK, _PREEN, _EAT, _DRINK, _TAME, _POUNCE, _STRETCH = (A.sniff, A.look_back, A.preen, A.eat, A.drink, A.tame,
                                                                     A.pounce, A.stretch)


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def tremor(t, f=(9.3, 14.1, 6.7), amp=(1.0, 0.55, 0.35), phase=0.0):
    """an organic shiver: three sines that never line up (a small animal trembles faster than the T. rex)"""
    return sum(a * math.sin(2 * math.pi * fr * t + phase * (i + 1) + 1.3 * i) for i, (fr, a) in enumerate(zip(f, amp)))


def rod(p, t, fn, delay=0.05, pitch=None, loop=None):
    """the stiff tail: the base takes fn(t - delay) whole, each section behind gives a little more, a little later"""
    for k, (b, g) in enumerate((("tail1", 1.0), ("tail2", 0.22), ("tail3", 0.16), ("tail4", 0.12))):
        u = t - delay * (k + 1)
        u = u % loop if loop else max(0.0, u)
        add(p, b, rot=((pitch(u) * g if pitch else 0.0), fn(u) * g, 0))


def bird(t, keys, dur=0.13):
    """bird head: a quick move that overshoots a hair and settles, then holds (the hold still drifts: see idle)"""
    out = [(0.0, keys[0][1])]
    for t0, v in keys[1:]:
        out.append((t0, out[-1][1])); out.append((t0 + dur, v, back_out))
    return float(Track(out)(t))


def alive(p, t, k=1.0, period=1.35):
    """the breathing every one-shot carries (moves the hips: call it before the feet are planted)"""
    br = wave(t, period)
    add(p, "body", rot=(0.7 * k * br, 0, 0), pos=(0, 0.12 * k * br, 0))
    alive_upper(p, t, k, period)
    return br


def alive_upper(p, t, k=1.0, period=1.35):
    """the breathing without the hips (poses whose feet step or lie)"""
    add(p, "neck", rot=(-0.6 * k * wave(t, period, -0.5), 0, 0))
    add(p, "skull", rot=(-0.4 * k * wave(t, period, -1.0), 0, 0))
    add(p, "jaw", rot=(-0.6 * k * max(0.0, wave(t, period, -0.7)), 0, 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(1.4 * k * wave(t, period, -0.8 - o), 0, 0))
        add(p, f"forearm_{s}", rot=(1.6 * k * wave(t, period * 2, -1.5 - o), 0, 0))
    add(p, "tail1", rot=(0.5 * k * wave(t, period, -0.6), 0.9 * k * wave(t, period * 2, -0.9), 0))


# ------------------------------------------------------------------ the gait: light, springy, the weight from foot to foot
def gait2(t, T, stride, duty, lift, bob, lean=0.0, drop=0.0, head=0.0, tail_up=0.0, roll=6.0, yaw=4.0, whip=1.0,
          wing=0.0, arms=3.0, splay=2.0, toe_sw=-35):
    ph = (t / T) % 1.0; w = 2 * math.pi * ph; p = {}

    def landing(x):
        # a light runner: the drop onto the foot is quick and so is the rebound (spring), then it floats
        x %= 1.0
        return -1.0 + 2.0 * smooth(x / 0.22) if x < 0.22 else 1.0 - 2.0 * smooth((x - 0.22) / 0.78)
    b2 = landing(2 * ph + 0.05)
    hroll = roll * math.sin(w + 0.25)
    hyaw = yaw * math.sin(w - 0.6)
    add(p, "body", rot=(lean + 1.2 * b2, hyaw, hroll), pos=(0, bob * b2 - 0.3 - drop, 0))
    # the bird head: the neck soaks up the bob and the roll, the skull holds the eye level (a touch late)
    add(p, "neck", rot=(head - lean * 0.7 - 1.4 * landing(2 * ph - 0.03), -0.9 * hyaw, -0.8 * hroll))
    add(p, "skull", rot=(head * 0.3 - lean * 0.3 + 1.0 * landing(2 * ph - 0.12), -0.1 * hyaw + 0.6 * math.sin(w - 1.9),
                         -0.2 * hroll))
    add(p, "jaw", rot=(-0.8 - 0.8 * max(0.0, landing(2 * ph - 0.2)), 0, 0))
    # the rod: swings against the hips from its base, late; the tip lifts a little after each landing
    rod(p, t, lambda u: -whip * (yaw * 0.9 + 2.5) * math.sin(2 * math.pi * u / T - 1.4), delay=T * 0.06,
        pitch=lambda u: tail_up + 1.2 * landing(2 * (u / T) - 0.1), loop=T)
    if wing:
        wings(p, wing, flap=0.15 * math.sin(2 * w - 0.8))
    for s, sx in (("l", 1), ("r", -1)):
        o = 0.0 if s == "l" else math.pi
        add(p, f"arm_{s}", rot=(20 + arms * math.sin(w + o - 2.3) + 1.5 * landing(2 * ph - 0.25), 0, sx * 6))
        add(p, f"forearm_{s}", rot=(arms * 0.8 * math.sin(w + o - 3.0), 0, 0))
    for s, o in SIDES:
        sx = 1 if s == "l" else -1
        u = (ph + o) % 1.0
        swing = 0.0 if u < duty else math.sin(math.pi * (u - duty) / (1 - duty))
        add(p, f"thigh_{s}", rot=(0, -hyaw, -hroll + sx * splay * swing))
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0
            meta = 30 * smooth(max(0, (st - 0.5) / 0.5)); clear = -0.05
            # the toes come down from where the swing left them (5 deg) and curl again at push-off
            toe = 5 * (1 - smooth(min(1.0, st / 0.2))) + 8 * smooth(max(0, (st - 0.75) / 0.25))
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e
            ly = lift * math.sin(math.pi * min(1, sw * 1.15)) ** 1.3
            meta = 30 * (1 - smooth(sw / 0.5)) - 15 * math.sin(math.pi * sw)
            toe = 8 * (1 - smooth(sw / 0.15)) + toe_sw * math.sin(math.pi * min(1, sw * 1.1)) + 5 * smooth((sw - 0.7) / 0.3)
            clear = -0.05 + 0.85 * math.sin(math.pi * sw) ** 0.5     # ends where the stance begins: the seam closes
        plant(p, s, ly, dz - 1, meta, toe, clear)
    return p


# the speeds the game reads (Raptor.WALK/RUN/STALK: px and ticks per cycle) stay the same
def walk(t): return gait2(t, 0.8, 16, 0.6, 3.0, 0.5, roll=5.0, yaw=3.5)
def run(t): return gait2(t, 0.4, 28, 0.38, 4.5, 1.1, lean=8, drop=0.5, head=-6, tail_up=3, roll=2.5, yaw=2.0, whip=0.6,
                         wing=0.35, arms=1.5, splay=1.0)


def stalk(t):
    p = gait2(t, 1.3, 8, 0.72, 1.2, 0.25, lean=4, drop=2.0, head=-14, tail_up=-1, roll=2.5, yaw=1.5, whip=0.4, arms=1.0,
              splay=1.0)
    # it creeps with the head held still in space and snapping from one look to the next, once a cycle
    add(p, "skull", rot=(4, bird(t % 1.3, [(0, 0), (0.25, 10), (0.7, -8), (1.1, 0)]), 0))
    return p


# ------------------------------------------------------------------ idle: 5.4 s, the bird head on a living body
IDLE_T = 5.4


def idle(t):
    p = {}
    T = IDLE_T
    br = alive(p, t, k=1.0, period=T / 4)                       # a quick shallow breath, 1.35 s
    shift = wave(t, T, 0.3) + 0.3 * wave(t, T / 2, 1.2)          # the weight drifts from one foot to the other
    hroll = 1.6 + 1.6 * shift; hyaw = -1.2 + 1.0 * shift
    add(p, "body", rot=(0, hyaw, hroll), pos=(0, -0.15 * abs(shift), 0))
    yaw = bird(t, [(0, 0), (0.9, 18), (2.2, -6), (3.2, -22), (4.4, 4), (5.1, 0)])
    pit = bird(t, [(0, 0), (0.9, 4), (2.2, -2), (3.2, 6), (4.4, 0)])
    tilt = bird(t, [(0, 0), (0.9, -8), (2.2, 0), (3.2, 10), (4.4, 0)])
    drift = 0.8 * wave(t, T / 3, 0.4) + 0.5 * wave(t, T / 5, 1.7)    # the held head still floats a little
    add(p, "neck", rot=(pit * 0.3, yaw * 0.35 - 0.8 * hyaw, -0.7 * hroll)); add(p, "skull", rot=(pit * 0.7 + 0.5 * drift, yaw * 0.65 + drift, tilt))
    lids(p, window(t, 2.75, 2.85, 0.05) + window(t, 4.9, 5.0, 0.05))
    rod(p, t, lambda u: 2.0 * wave(u, T, -0.8) + 0.8 * wave(u, T / 2, 0.5) - 1.2 * hyaw, delay=0.12,
        pitch=lambda u: 0.6 * wave(u, T / 4, -0.5), loop=T)
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, -hyaw, -hroll))
    plant(p, "l")
    plant(p, "r", 0.0, -1.2)
    return p


# ------------------------------------------------------------------ voice
def call(t):
    """a chirping trill: chin up, the throat pulses three times, each chirp a little shiver, never a switch"""
    p = {}
    k = float(tr((0, 0), (0.3, 1, ease_out), (1.6, 1), (2.0, 0, ease_in))(t))
    pulses = sum(math.exp(-((t - c) / 0.06) ** 2) for c in (0.55, 0.85, 1.15))
    shiv = tremor(t) * window(t, 0.45, 1.3, 0.12)
    add(p, "neck", rot=(14 * k + 0.4 * shiv, 0, 0)); add(p, "skull", rot=(10 * k + 3 * pulses + 0.6 * shiv, 0, 0))
    add(p, "jaw", rot=(-14 * pulses - 0.8 * shiv * pulses, 0, 0))
    rod(p, t, lambda u: 1.5 * math.exp(-((u - 0.85) / 0.35) ** 2), pitch=lambda u: 2 * float(tr((0, 0), (0.3, 1, ease_out), (1.6, 1), (2.0, 0, ease_in))(u)))
    alive(p, t, k=0.7)
    return stand(p)


def screech(t):
    """the hunting cry: a crouch to fill the lungs, the head thrown up and forward, the cry with a shiver in the throat
    (an envelope), the wings flicked out, then it settles past rest and back"""
    p = {}
    k = float(tr((0, 0), (0.25, -0.4, ease_out), (0.5, 1, ease_out), (1.4, 0.9), (1.8, 0, back_out))(t))
    a = max(0, k); c = max(0, -k) / 0.4
    env = window(t, 0.5, 1.4, 0.14)
    shiv = tremor(t, (13.1, 17.9, 8.3)) * env
    add(p, "body", rot=(-6 * a + 4 * c + 0.3 * shiv, 0, 0), pos=(0, -1.5 * c, 0))
    add(p, "neck", rot=(30 * a - 10 * c + 0.8 * shiv, 0, 0)); add(p, "skull", rot=(12 * a + 1.2 * shiv, 0, 0))
    add(p, "jaw", rot=(-45 * a - 1.6 * shiv, 0, 0))
    wings(p, 0.45 * a, flap=0.12 * shiv)
    rod(p, t, lambda u: 0.0, pitch=lambda u: 6 * max(0.0, float(tr((0, 0), (0.25, -0.4, ease_out), (0.5, 1, ease_out), (1.4, 0.9), (1.8, 0, back_out))(u))))
    alive(p, t, k=0.5)
    return stand(p)


def display(t):
    """threat: crouched, wings spread wide, the ruff up, a hiss that trembles, the tail lashing late"""
    p = {}
    k = float(tr((0, 0), (0.42, 1, ease_out), (1.9, 1), (2.3, 0, ease_in))(t))
    hiss = window(t, 0.5, 1.6, 0.15)
    add(p, "body", rot=(6 * k, 0, 0), pos=(0, -2.5 * k, 0))
    add(p, "neck", rot=(-16 * k, 0, 0)); add(p, "skull", rot=(4 * k + 0.8 * tremor(t) * hiss, 6 * math.sin(2 * math.pi * t / 1.15) * k, 0))
    add(p, "jaw", rot=(-30 * hiss - 2 * tremor(t, (11.3, 15.7, 7.1)) * hiss, 0, 0))
    wings(p, k, flap=0.12 * tremor(t, (6.1, 9.7, 3.9)) * k)
    rod(p, t, lambda u: 10 * math.sin(2 * math.pi * 1.2 * u) * float(tr((0, 0), (0.3, 1), (1.9, 1), (2.3, 0))(u)), delay=0.06,
        pitch=lambda u: 6 * float(tr((0, 0), (0.3, 1), (1.9, 1), (2.3, 0))(u)))
    alive(p, t, k=0.6)
    return stand(p)


# ------------------------------------------------------------------ combat
# the bite: the jaws close at 0.3 s (RaptorStrikeGoal.BITE_HIT, tick 6)
BN = tr((0, (0, 0)), (0.15, (10, -3), ease_out), (0.3, (-18, 0), ease_in), (0.45, (-14, 14)), (0.6, (-14, -10)),
        (1.0, (0, 0), back_out))


def attack(t):
    """three beats: the head cocks back with the jaws open, strikes, tears to one side and the other, settles"""
    p = {}
    n = BN(t)
    j = float(tr((0, 0), (0.15, -38, ease_out), (0.3, -2, ease_in), (0.75, -3), (1.0, 0, ease_out))(t))
    push = float(tr((0, 0), (0.15, 1.2, ease_out), (0.3, -3, smooth), (0.7, -2), (1.0, 0, back_out))(t))   # the body lunges over the planted feet
    hunch = float(tr((0, 0), (0.15, 1, ease_out), (0.7, 1), (1.0, 0, ease_out))(t))
    add(p, "body", rot=(4 * hunch, 0.25 * n[1], 0), pos=(0, -0.8 * hunch, push))
    add(p, "neck", rot=(n[0], n[1] * 0.6, 0)); add(p, "skull", rot=(n[0] * 0.5, n[1] * 0.4, -n[1] * 0.6))
    add(p, "jaw", rot=(j, 0, 0))
    wings(p, 0.35 * hunch)
    rod(p, t, lambda u: -0.5 * BN(u)[1], delay=0.05, pitch=lambda u: 3 * float(tr((0, 0), (0.15, 1, ease_out), (0.7, 1), (1.0, 0, ease_out))(u)))
    alive(p, t, k=0.5)
    return stand(p)


# the kick: the slash lands at 0.5 s (RaptorStrikeGoal.KICK_HIT, tick 10); the foot is back on the ground by 0.8 s
# the kicking leg is in the air, so it is posed joint by joint (thigh, shin, metatarsus, toes) instead of by IK: the IK
# with the drumstick's soft thigh limit flipped the knee between two solutions once the foot came up past ~7 px.
# The sickle is on the toes: cocked up with the knee at the chest, then driven forward and down and raked back.
KF = tr((0, (0, 0, 0, 0)), (0.3, (48, -66, 26, -45), ease_out), (0.42, (50, -72, 30, -52)), (0.5, (50, -20, -18, 25), ease_in),
        (0.62, (40, -18, -12, 12), ease_out), (0.8, (8, -5, -2, 0), smooth), (0.9, (0, 0, 0, 0)))
KB = tr((0, 0), (0.3, 1, ease_out), (0.42, 1.05), (0.5, -0.35, ease_in), (0.62, -0.2), (0.82, 0.08, ease_out), (0.9, 0))


def kick(t):
    """the 1971 fossil's blow: the weight shifts onto the left foot and back, the right knee comes up to the chest with
    the sickle cocked, a beat, then the foot drives down and forward and the claw rakes; the wings flare for balance,
    the rod of the tail goes up against the leg, the head stays on the target"""
    p = {}
    b = float(KB(t)); a = max(0.0, b); f = max(0.0, -b) / 0.35
    alive(p, t, k=0.4)
    hroll = 5 * a + 2 * f
    add(p, "body", rot=(-8 * a + 5 * f, 2 * a, hroll), pos=(0, 0.5 * a - 0.6 * f, 1.5 * a - 1.5 * f))
    add(p, "neck", rot=(7 * a - 5 * f, -1.5 * a, -0.8 * hroll)); add(p, "skull", rot=(2 * a - 2 * f, 0, -0.2 * hroll))
    add(p, "jaw", rot=(-20 * window(t, 0.2, 0.6, 0.12), 0, 0))
    wings(p, 0.6 * window(t, 0.08, 0.7, 0.15), flap=0.25 * math.exp(-((t - 0.52) / 0.08) ** 2))
    rod(p, t, lambda u: 3 * max(0.0, float(KB(u))), delay=0.05, pitch=lambda u: 6 * max(0.0, float(KB(u))) - 4 * max(0.0, -float(KB(u))))
    add(p, "thigh_l", rot=(0, -2 * a, -hroll))
    plant(p, "l")
    for bone, v in zip(("thigh_r", "shin_r", "foot_r", "toes_r"), KF(t)):
        add(p, bone, rot=(float(v), 0, 0))
    add(p, "thigh_r", rot=(0, 0, -hroll * smooth(t / 0.15) * (1 - smooth((t - 0.75) / 0.15))))
    return p


LEAP_BACK_T = 0.85
# airborne 0.1 - 0.5 s (the hop back after a blow, RaptorStrikeGoal.hopBack); h = how high the root goes (v2b px)
LB_H = tr((0, 0), (0.1, 0), (0.29, 4.2, ease_out), (0.5, 0, ease_in), (0.85, 0))
LB_C = tr((0, 0), (0.08, 1, ease_out), (0.16, -0.35, ease_out), (0.46, -0.1), (0.57, 1.0, ease_out), (0.85, 0, back_out))
LB_AIR = tr((0, 0), (0.1, 0), (0.2, 1, ease_out), (0.42, 1), (0.5, 0, ease_in), (0.85, 0))


def leap_back(t):
    """the spring backwards out of reach after a kick: a quick crouch, the push off both feet, airborne with the body
    leaning back, the feet reaching back for the ground, wings flared, the head kept on the target; it lands in a
    crouch that takes the weight and comes up past rest and back"""
    p = {}
    h = float(LB_H(t)); c = float(LB_C(t)); air = float(LB_AIR(t))
    land = math.exp(-((t - 0.55) / 0.06) ** 2)
    add(p, "root", pos=(0, h, 0))
    add(p, "body", rot=(5 * max(0, c) - 9 * air + 2 * land, 0, 0), pos=(0, -2.2 * c, 0))
    # the head stays on the target: the neck cancels the body's lean
    add(p, "neck", rot=(-4 * max(0, c) + 7 * air - 2 * land, 0, 0)); add(p, "skull", rot=(2 * air, 0, 0))
    add(p, "jaw", rot=(-22 * window(t, 0.12, 0.62, 0.1) - 1.5 * tremor(t) * window(t, 0.15, 0.6, 0.1), 0, 0))
    wings(p, 0.8 * window(t, 0.04, 0.58, 0.2), flap=0.3 * air * math.sin(2 * math.pi * (t - 0.1) / 0.4))
    rod(p, t, lambda u: 2.0 * math.exp(-((u - 0.58) / 0.1) ** 2), delay=0.05,
        pitch=lambda u: 8 * float(LB_AIR(u)) - 6 * math.exp(-((u - 0.58) / 0.08) ** 2))
    alive_upper(p, t, k=0.4)
    for s, _ in SIDES:
        # in the air the feet tuck up and reach back (it is going backwards), the sickles raised
        plant(p, s, h + 2.5 * air, 2.5 * air, -10 * air, -30 * air, clear=-0.05)
    return p


def hurt(t):
    p = {}; e = math.exp(-(t / 0.12)) * smooth(t / 0.03)
    add(p, "body", rot=(-6 * e, 6 * e, -5 * e), pos=(0, -0.5 * e, 1.5 * e))
    add(p, "neck", rot=(14 * e, -10 * e, 0)); add(p, "skull", rot=(8 * e, -6 * e, 8 * e)); add(p, "jaw", rot=(-25 * e, 0, 0))
    wings(p, 0.35 * math.exp(-max(0.0, t - 0.1) / 0.15) * smooth(t / 0.1))
    rod(p, t, lambda u: -8 * math.exp(-(u / 0.15)) * smooth(u / 0.03), delay=0.03,
        pitch=lambda u: 4 * math.exp(-(u / 0.15)) * smooth(u / 0.03))
    alive(p, t, k=0.4)
    return stand(p)


def pounce(t):
    p = _POUNCE(t)
    alive_upper(p, t, k=0.5)
    return p


# ------------------------------------------------------------------ the duel set, the raptor's way
GUARD_T = 1.6


def guard(t):
    """crouched and springy, rocking on the toes, the head held level and still on the rival (a bird's), the wings half
    open and trembling, the rod of the tail high, the sickles flicking: it waits for the moment to leap"""
    p = {}
    T = GUARD_T
    bounce = wave(t, T / 2)
    add(p, "body", rot=(6 + 1.0 * bounce, 1.2 * wave(t, T, 0.8), 1.5 * wave(t, T, 0.2)), pos=(0, -1.8 + 0.4 * bounce, -0.4 * wave(t, T, 0.5)))
    add(p, "neck", rot=(-10 - 1.0 * bounce, -1.2 * wave(t, T, 1.0), -1.2 * wave(t, T, 0.2)))
    hiss = tremor(t, (16 / T, 23 / T, 11 / T), (0.8, 0.45, 0.3))      # harmonics of the loop: it closes
    add(p, "skull", rot=(4 + 0.5 * hiss, 1.5 * wave(t, T / 2, 0.4), 0))
    add(p, "jaw", rot=(-8 - 3 * max(0.0, wave(t, T / 2, -0.6)) - 1.2 * hiss, 0, 0))
    wings(p, 0.35 + 0.04 * wave(t, T / 4, 0.3), flap=0.06 * hiss)
    rod(p, t, lambda u: 3 * wave(u, T, -0.6), delay=0.06, pitch=lambda u: 8 + 1.0 * wave(u, T / 2, -0.8), loop=T)
    for s, o in SIDES:
        sx = 1 if s == "l" else -1
        add(p, f"thigh_{s}", rot=(0, 0, 2.5 * sx - 1.5 * wave(t, T, 0.2)))
    flick_l = max(0.0, wave(t, T, 0.0)) ** 3; flick_r = max(0.0, wave(t, T, math.pi)) ** 3
    plant(p, "l", 0.0, -1.5, 0, -10 * flick_l)
    plant(p, "r", 0.0, 1.5, 0, -10 * flick_r)
    return p


STRAFE_T = 0.8
# two side-hops per loop: both feet push off together and land together (a bird's bound, not the crossing steps of a
# big theropod); on the ground 55% of each hop, the rest in the air
HOP_AIR = 0.45


def strafe(t, side):
    """bounding sideways round the rival on both feet at once, the body square to it and leaning into the travel, the
    head held still in space like a bird's, the wings half open for balance, the rod of the tail swung out the other way"""
    d = 1.0 if side == "left" else -1.0               # + model x is the animal's left in game
    ph = (2 * t / STRAFE_T) % 1.0; p = {}
    g = 1.0 - HOP_AIR
    if ph < g:                                         # on the ground: absorb, then load the spring
        st = ph / g
        h = 0.0; c = math.sin(math.pi * st) ** 2; air = 0.0
    else:
        sw = (ph - g) / HOP_AIR
        h = 2.6 * math.sin(math.pi * sw); c = -0.25 * math.sin(math.pi * sw); air = math.sin(math.pi * sw)
    add(p, "root", pos=(0, h, 0))
    add(p, "body", rot=(5 + 2 * c, 0, -4.0 * d - 2.0 * d * air), pos=(0.6 * d * air, -1.2 - 1.2 * c, 0))
    # the neck cancels the body so the head stays still while the body bounds under it
    add(p, "neck", rot=(-8 - 2 * c, 0, 4.0 * d + 2.0 * d * air)); add(p, "skull", rot=(4, 0, 0.6 * d))
    add(p, "jaw", rot=(-5 - 1.0 * tremor(t, (13 / STRAFE_T, 18 / STRAFE_T, 9 / STRAFE_T), (0.7, 0.4, 0.3)), 0, 0))
    wings(p, 0.3 + 0.15 * air, flap=0.25 * air * d)
    rod(p, t, lambda u: -d * 7.0 - 2.5 * math.sin(4 * math.pi * u / STRAFE_T - 0.6), delay=0.05,
        pitch=lambda u: 6.0 + 2.0 * math.sin(4 * math.pi * u / STRAFE_T - 1.0), loop=STRAFE_T)
    for s, _ in SIDES:
        sx = 1 if s == "l" else -1
        # the legs reach a little toward the travel in the air (the leading leg more)
        add(p, f"thigh_{s}", rot=(0, 0, d * 6.0 * air + 2.0 * sx))
        plant(p, s, h + 1.2 * air, 0.0, 6 * air, -14 * air, clear=-0.05)
    return p


def strafe_left(t): return strafe(t, "left")
def strafe_right(t): return strafe(t, "right")


TURN_T = 0.8


def turn(t, side):
    """quick little steps round: the head snaps into the turn first (+ yaw looks to the animal's right in game, so a
    left turn leads with - yaw), the hips follow, the rod of the tail swings out the other way and lags"""
    d = 1.0 if side == "left" else -1.0
    lead = -d
    ph = (t / TURN_T) % 1.0; w = 2 * math.pi * ph; p = {}
    add(p, "body", rot=(0, lead * (5.0 + 2.0 * math.sin(w)), 2.0 * math.sin(w + 0.3)), pos=(0, -0.5 + 0.4 * math.cos(2 * w), 0))
    add(p, "neck", rot=(-1.0, lead * (12.0 + 2.0 * math.sin(w - 0.6)), -1.5 * math.sin(w + 0.3)))
    add(p, "skull", rot=(0, lead * (10.0 + 1.5 * math.sin(w - 1.2)), -1.0 * math.sin(w)))
    rod(p, t, lambda u: -lead * 8.0 - 3.0 * math.sin(2 * math.pi * u / TURN_T - 0.8), delay=0.06, pitch=lambda u: 2.0, loop=TURN_T)
    alive_upper(p, t, k=0.5, period=TURN_T / 2)
    for s, o in SIDES:
        u = (ph + o) % 1.0
        if u < 0.4:
            sw = u / 0.4
            ly = 3.5 * math.sin(math.pi * sw) ** 1.2
            dz = -1.5 * math.cos(math.pi * sw)
            toe = -20 * math.sin(math.pi * sw); meta = 12 * math.sin(math.pi * sw); clear = 0.6 * math.sin(math.pi * sw) ** 0.5
            add(p, f"thigh_{s}", rot=(0, lead * 7.0 * math.sin(math.pi * sw), 0))
        else:
            ly, dz, toe, meta, clear = 0.0, 1.5 - 3.0 * ((u - 0.4) / 0.6), 0.0, 0.0, -0.05
        add(p, f"thigh_{s}", rot=(0, -lead * 5.0, -2.0 * math.sin(w + 0.3)))
        plant(p, s, ly, dz, meta, toe, clear)
    return p


def turn_left(t): return turn(t, "left")
def turn_right(t): return turn(t, "right")


FEINT_T = 0.9
FT_C = tr((0, 0), (0.14, 1, ease_out), (0.28, -0.6, ease_out), (0.45, -0.3), (0.62, 0.3, ease_in), (0.9, 0, back_out))


def feint(t):
    """a leap that never leaves: the crouch, the pop up and forward with the wings flared and the jaws snapping on air,
    the feet still down, the pull back"""
    p = {}
    c = float(FT_C(t)); a = max(0.0, c); e = max(0.0, -c) / 0.6
    add(p, "body", rot=(5 * a - 6 * e, 0, 0), pos=(0, -2.0 * a + 0.8 * e, -2.5 * e + 0.8 * a))
    add(p, "neck", rot=(-6 * a - 10 * e, 0, 0)); add(p, "skull", rot=(-4 * e, 0, 0))
    add(p, "jaw", rot=(float(tr((0, -4), (0.2, -30, ease_out), (0.3, -2, ease_in), (0.36, -24, ease_out), (0.44, -2, ease_in), (0.9, -3))(t)), 0, 0))
    wings(p, 0.55 * e + 0.2 * a, flap=0.2 * e)
    rod(p, t, lambda u: 0.0, delay=0.05, pitch=lambda u: (lambda cc: 8 * max(0.0, -cc) / 0.6 - 4 * max(0.0, cc))(float(FT_C(u))))
    alive(p, t, k=0.4)
    return stand(p)


BLOCK_T = 0.6


def block(t):
    """the blow meets the wing: the near arm flicks up and out in front, feathers spread, the body twists away from it
    and the head pulls back; then it all comes back past rest"""
    p = {}
    e = math.exp(-max(0.0, t - 0.06) / 0.2) * smooth(t / 0.06)
    add(p, "body", rot=(-3 * e, 7 * e, 3 * e), pos=(0, -0.5 * e, 1.2 * e))
    add(p, "neck", rot=(10 * e, 14 * e, 4 * e)); add(p, "skull", rot=(6 * e, 8 * e, 8 * e)); add(p, "jaw", rot=(-14 * e, 0, 0))
    ew = math.exp(-max(0.0, t - 0.15) / 0.22) * smooth(t / 0.15)      # the wing rises over three frames, not one
    wings(p, 0.65 * ew, flap=0.25 * ew, side="l"); wings(p, 0.2 * ew, side="r")
    rod(p, t, lambda u: -8 * math.exp(-max(0.0, u - 0.06) / 0.22) * smooth(u / 0.06), delay=0.04)
    alive(p, t, k=0.4)
    return stand(p)


RECOIL_T = 0.7


def recoil(t):
    """its blow was turned aside: the head knocked away, wings flung out, a quick hop-step back with one foot"""
    p = {}
    e = math.exp(-max(0.0, t - 0.04) / 0.16) * smooth(t / 0.04)
    wob = math.exp(-max(0.0, t - 0.08) / 0.14) * math.sin(2 * math.pi * 5.0 * (t - 0.08)) * smooth((t - 0.06) / 0.04)
    add(p, "body", rot=(-4 * e, 5 * e, -3 * e), pos=(0, -0.4 * e, 2.0 * e))
    add(p, "neck", rot=(6 * e, -14 * e + 4 * wob, -5 * e)); add(p, "skull", rot=(4 * e, -10 * e + 5 * wob, -9 * e))
    add(p, "jaw", rot=(-16 * e, 0, 0))
    ew = math.exp(-max(0.0, t - 0.15) / 0.2) * smooth(t / 0.15)
    wings(p, 0.45 * ew, flap=0.3 * wob)
    rod(p, t, lambda u: 8 * math.exp(-max(0.0, u - 0.04) / 0.2) * smooth(u / 0.04), delay=0.04)
    alive_upper(p, t, k=0.4)
    plant(p, "l")
    s = math.sin(math.pi * min(1.0, max(0.0, (t - 0.08) / 0.32)))
    plant(p, "r", 3.5 * s ** 2, 3 * smooth((t - 0.08) / 0.32) * (1 - smooth((t - 0.4) / 0.3)), 0, -14 * s, clear=-0.05)
    return p


SUBMIT_T = 2.0


def submit(t):
    """beaten: it drops low, the wings folded tight, the tail rod down, the head low and turned away, a soft whine"""
    p = {}
    k = float(tr((0, 0), (0.5, 1, ease_out), (2.0, 1))(t))
    turn_ = float(tr((0, 0), (0.6, 0), (1.3, 1, ease_out), (2.0, 1))(t))
    whine = math.exp(-((t - 0.8) / 0.12) ** 2) + 0.6 * math.exp(-((t - 1.1) / 0.1) ** 2)
    add(p, "body", rot=(5 * k, 12 * turn_, 0), pos=(0, -2.5 * k, 0))
    add(p, "neck", rot=(-18 * k, 12 * turn_, 0)); add(p, "skull", rot=(-6 * k, 8 * turn_, 6 * k)); add(p, "jaw", rot=(-2 - 7 * whine, 0, 0))
    for s, sx in (("l", 1), ("r", -1)):
        add(p, f"arm_{s}", rot=(-8 * k, 0, -sx * 4 * k))              # wings pressed in
    rod(p, t, lambda u: -6 * float(tr((0, 0), (0.6, 0), (1.3, 1, ease_out), (2.0, 1))(u)), delay=0.08,
        pitch=lambda u: -8 * float(tr((0, 0), (0.5, 1, ease_out), (2.0, 1))(u)))
    for s_, _ in SIDES:
        add(p, f"thigh_{s_}", rot=(0, -12 * turn_, 0))
    alive_upper(p, t, k=0.8)
    return stand(p)


# ------------------------------------------------------------------ rest transitions and tiredness
LIE_DOWN_T = 1.5


def lie_down(t):
    """from standing to resting on the belly like a bird: the legs fold, the keel goes down, a little bump as it lands,
    the feathers settle"""
    p = {}
    k = float(tr((0, 0), (0.2, 0.04), (1.0, 0.93, ease_in), (1.15, 1.03), (1.5, 1.0, ease_out))(t))
    look = float(tr((0, 0), (0.25, 1, ease_out), (0.95, 1), (1.5, 0, ease_out))(t))
    A.lie(p, k)
    add(p, "neck", rot=(-8 * look, 0, 0)); add(p, "skull", rot=(-4 * look, 0, 0))
    land = math.exp(-((t - 1.05) / 0.08) ** 2)
    add(p, "body", rot=(0.8 * land, 0, 0))
    wings(p, 0.15 * land, flap=0.4 * land * math.sin(2 * math.pi * 9 * t))
    rod(p, t, lambda u: 0.0, delay=0.05, pitch=lambda u: 2.5 * math.exp(-((u - 1.05) / 0.12) ** 2))
    alive_upper(p, t, k=0.5)
    return ground_fit(S, p)


GET_UP_T = 1.3


def get_up(t):
    """the head swings forward to lift the weight, the legs push it up, a wobble and a ruffle once up"""
    p = {}
    k = float(tr((0, 1.0), (0.25, 1.02), (0.85, 0.04, ease_out), (1.0, -0.02), (1.3, 0.0, ease_out))(t))
    push = math.exp(-((t - 0.4) / 0.15) ** 2)
    A.lie(p, max(0.0, k))
    add(p, "neck", rot=(-12 * push, 0, 0)); add(p, "skull", rot=(-6 * push, 0, 0))
    ruff = math.exp(-((t - 1.05) / 0.12) ** 2) * math.sin(2 * math.pi * 8 * (t - 1.05))
    add(p, "neck", rot=(0, 2 * ruff, 6 * ruff)); add(p, "skull", rot=(0, 3 * ruff, 9 * ruff))
    wings(p, 0.2 * abs(ruff), flap=0.3 * ruff)
    rod(p, t, lambda u: -3.0 * math.exp(-max(0.0, u - 0.9) / 0.2) * math.sin(2 * math.pi * 3.0 * (u - 0.9)) * smooth((u - 0.85) / 0.06), delay=0.05)
    alive_upper(p, t, k=0.5)
    return ground_fit(S, p)


IDLE_TIRED_T = 2.4


def idle_tired(t):
    """spent after a chase: it pants fast with the mouth open like a hot bird, the wings drooping from the body to
    shed heat, the head low, the tail rod low"""
    p = {}
    T = IDLE_TIRED_T
    pant = wave(t, T / 6)
    add(p, "body", rot=(3 + 1.6 * pant, 0.8 * wave(t, T, 0.4), 1.0 * wave(t, T, 1.0)), pos=(0, -1.0 + 0.3 * pant, 0))
    add(p, "neck", rot=(-10 - 1.6 * wave(t, T / 6, -0.6), 2 * wave(t, T, 0.5), 0))
    add(p, "skull", rot=(-3 - 1.0 * wave(t, T / 6, -1.2), 1.5 * wave(t, T, -0.5), 0))
    add(p, "jaw", rot=(-16 - 6 * max(0.0, wave(t, T / 6, -0.4)), 0, 0))
    for s, sx in (("l", 1), ("r", -1)):
        add(p, f"arm_{s}", rot=(-12 + 1.5 * wave(t, T / 6, -0.8), 0, sx * (14 + 1.5 * wave(t, T / 2, 0.3))))   # wings held off the body
    rod(p, t, lambda u: 2 * wave(u, T, -0.8), delay=0.08, pitch=lambda u: -4 + 0.6 * wave(u, T / 6, -0.5), loop=T)
    return stand(p)


WALK_TIRED_T = 1.0


def walk_tired(t):
    """the walk with nothing left: slower, shorter steps that drop heavier, the head low, the mouth open panting"""
    p = gait2(t, WALK_TIRED_T, 14, 0.64, 2.4, 0.7, lean=2, drop=0.8, head=-10, tail_up=-3, roll=6.0, yaw=3.0, whip=0.7, arms=2.0)
    add(p, "jaw", rot=(-12 - 5 * max(0.0, wave(t, WALK_TIRED_T / 2)), 0, 0))
    add(p, "neck", rot=(-1.2 * wave(t, WALK_TIRED_T / 2, -0.5), 0, 0))
    for s, sx in (("l", 1), ("r", -1)):
        add(p, f"arm_{s}", rot=(-10, 0, sx * 10))
    return p


# ------------------------------------------------------------------ the quieter ones: the breath and the tail under them
def _upper(fn, k=0.5):
    def g(t):
        p = fn(t); alive_upper(p, t, k=k); return p
    g.__name__ = fn.__name__; g.__doc__ = fn.__doc__
    return g


sniff, look_back, preen, eat, drink, tame, stretch = (_upper(_SNIFF), _upper(_LOOK_BACK), _upper(_PREEN, 0.4), _upper(_EAT, 0.4),
                                                      _upper(_DRINK, 0.4), _upper(_TAME), _upper(_STRETCH, 0.4))
