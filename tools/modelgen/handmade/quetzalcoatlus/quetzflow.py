"""Quetzalcoatlus: the fluid set (06/11/2026), after the T. rex (docs/estudos/08_ANIMACAO_RAXIORES.md) but in the
azhdarchid's own way (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md: crests for display, Bennett 1992; the beak a
spear, Witton & Naish 2008).

What is its own:
  * THE NECK IS STIFF. A giraffe's neck, not a swan's: it bends at the shoulder (neck1) and at the head joint
    (skull), the middle segments only follow a little, late. So the follow-through runs down a short, stiff chain,
    and the head is kept steady in space while the body moves under it (storks and herons do the same).
  * THE HEAD LEADS. When it looks round the eyes go first: the skull turns, then neck3, neck2, neck1, each a beat late.
  * THE WINGS ARE HEAVY. In the flap the downstroke is fast and the upstroke slow, with the wing half gathered on
    the way up; every segment out to the wing finger turns a little later than the one before (the tip arrives last).
    The glide never freezes: slow gusts run out along the wing to the tip and ripple the trailing edge.
  * NOTHING STOPS, NOTHING SWITCHES: every one-shot carries the breathing (`alive`), every effect has an envelope
    (`window`), the shivers are sums of sines that never line up (`tremor`); in a loop they are whole cycles per loop
    (`loop_tremor`), so the seam closes.
  * EVERY STRIKE HAS THREE BEATS: the neck draws back (anticipation), the spear goes in fast (the hit), and it
    settles past the rest pose a little and back (`back_out`).

The feet and hands are planted by IK on the cached stance (quetzanims2.base); nothing here moves the body on the
ground except through a cached stance, so the claws stay where they are.
"""
import math

import quetzanim as A
import quetzanims2 as B
import quetzanims3 as C
from quetzanim import S, SIDES, mir, lowest
from anim2 import add, smooth, ease_in, ease_out, back_out, Track

NECK = ("neck1", "neck2", "neck3", "skull")
WING = ("arm", "forearm", "hand", "finger1", "finger2")


def tr(*keys):
    return Track(list(keys))


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def window(t, a, b, fade=0.2):
    """1 between a and b, faded in and out (never a switch)"""
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


def tremor(t, f=(7.3, 11.1, 4.7), amp=(1.0, 0.55, 0.35), phase=0.0):
    """an organic shiver: three sines whose frequencies never line up"""
    return sum(a * math.sin(2 * math.pi * fr * t + phase * (i + 1) + 1.3 * i) for i, (fr, a) in enumerate(zip(f, amp)))


def loop_tremor(t, T, cycles=(7, 11, 17), amp=(1.0, 0.55, 0.35), phase=0.0):
    """the same shiver for a loop: whole cycles per loop (prime counts, so they still never line up)"""
    return sum(a * math.sin(2 * math.pi * c * t / T + phase * (i + 1) + 1.3 * i) for i, (c, a) in enumerate(zip(cycles, amp)))


def trail(p, t, fn, bones=NECK, gain=(1.0, 0.6, 0.45, 0.7), delay=0.05, axis=1, loop=None, sx=None):
    """follow-through down a chain: bone k takes fn(t - k*delay) * gain[k] on `axis` (wraps in a loop); with sx the
    rotation is mirrored for a wing side"""
    for k, b in enumerate(bones):
        u = t - delay * k
        v = fn(u % loop if loop else max(0.0, u)) * gain[k]
        r = [0.0, 0.0, 0.0]; r[axis] = v
        add(p, b, rot=mir(tuple(r), sx) if sx else tuple(r))


def alive(p, t, k=1.0, period=2.4):
    """the breathing every pose on the ground carries: the long neck rises a little on the in-breath, the head a beat
    later, the beak parts on the out-breath, the folded membranes swell and settle"""
    add(p, "neck1", rot=(-0.6 * k * wave(t, period), 0, 0))
    add(p, "neck2", rot=(0.25 * k * wave(t, period, -0.4), 0, 0))
    add(p, "neck3", rot=(0.25 * k * wave(t, period, -0.7), 0, 0))
    add(p, "skull", rot=(0.5 * k * wave(t, period, -1.0), 0, 0))
    add(p, "jaw", rot=(-0.8 * k * max(0.0, wave(t, period, -0.6)), 0, 0))
    for s, sx in SIDES:
        add(p, f"mem_forearm_{s}", scale=(1, 1, 1 + 0.02 * k * wave(t, period, -0.3)))
        add(p, f"finger2_{s}", rot=mir((0, 0.5 * k * wave(t, period, -1.1), 0), sx))


def mirror(p):
    """the pose seen in a mirror (left and right swapped)"""
    out = {}
    for k, v in p.items():
        n = k[:-2] + ("_r" if k.endswith("_l") else "_l") if k.endswith(("_l", "_r")) else k
        r, q = v[0], v[1]
        out[n] = ([r[0], -r[1], -r[2]], [-q[0], q[1], q[2]], *(v[2:] if len(v) > 2 else ()))
    return out


# ================================================================== on the ground
IDLE_T = 6.0
LOOK = tr((0, (0, 0)), (0.7, (0, 0)), (1.3, (5, 20), ease_out), (2.5, (6, 23)), (2.95, (-4, -17), ease_out), (4.1, (-3, -19)),
          (4.7, (2, 5), ease_out), (5.4, (1, 3)), (6.0, (0, 0)))


def idle(t):
    """standing tall: breathes, looks round (the head first, the neck after), the beak clacks, a fold settles"""
    T = IDLE_T
    br = wave(t, T / 3)
    p = A._cached_stance(round(0.3 * br, 1))
    for k, b in enumerate(("skull", "neck3", "neck2", "neck1")):
        lp, ly = LOOK((t - 0.09 * k) % T)
        g = (0.3, 0.2, 0.25, 0.4)[k]
        add(p, b, rot=(lp * (0.5 if b == "skull" else 0.15), ly * g, -ly * 0.15 if b == "skull" else 0))
    # the slow drift that keeps the head alive between the looks
    add(p, "neck1", rot=(-0.6 * br + 0.7 * wave(t, T, 0.3), 1.6 * wave(t, T, 1.2), 0))
    add(p, "skull", rot=(0.8 * wave(t, T / 5, 0.6), 1.0 * wave(t, T / 2, -0.4), 1.2 * wave(t, T, 2.0)))
    clack = math.exp(-((t - 5.0) / 0.06) ** 2) + 0.8 * math.exp(-((t - 5.22) / 0.06) ** 2)
    add(p, "jaw", rot=(-8 * clack - 0.8 * max(0.0, wave(t, T / 3, -0.6)), 0, 0))
    add(p, "skull", rot=(1.5 * math.exp(-((t - 5.1) / 0.12) ** 2), 0, 0))
    # a folded wing settles: a short shiver of the finger on one side, faded in and out
    sh = tremor(t, (9.1, 13.7, 6.3), (1.0, 0.5, 0.3)) * window(t, 3.2, 3.7, 0.15)
    add(p, "finger1_l", rot=mir((0, 1.2 * sh, 0.8 * sh), 1)); add(p, "mem_finger1_l", scale=(1, 1, 1 + 0.03 * sh))
    for s, sx in SIDES:
        add(p, f"mem_forearm_{s}", scale=(1, 1, 1 + 0.02 * br))
    return p


def walk(t):
    """the walk with the head carried steady: the neck takes the sway late, the skull cancels it"""
    p = A.walk_pose(t)
    T = A.WALK_T
    trail(p, t, lambda u: 1.4 * wave(u, T, -0.3), bones=("neck2", "neck3", "skull"), gain=(0.8, 0.6, -1.2), delay=0.07, loop=T)
    trail(p, t, lambda u: 1.0 * wave(u, T / 2, -0.8), bones=("neck2", "neck3", "skull"), gain=(0.6, 0.5, -1.0), delay=0.06, axis=0, loop=T)
    add(p, "jaw", rot=(-0.6 - 0.6 * max(0.0, wave(t, T, -0.6)), 0, 0))
    return p


def run(t):
    """the bounding run: the long neck lags the bounce, the beak a little open"""
    p = B.run_pose(t)
    T = B.RUN_T
    trail(p, t, lambda u: 3.0 * wave(u, T, -0.6), bones=NECK, gain=(0.5, 0.7, 0.8, -0.8), delay=0.04, axis=0, loop=T)
    add(p, "jaw", rot=(-4 - 3 * max(0.0, wave(t, T, -1.0)), 0, 0))
    return p


STALK_T = 2.4   # one walk cycle stretched 1.71x (was 2.38, which is not a whole number of 20 fps frames: the seam missed)
SCAN = tr((0, 0), (0.25, 0), (0.85, 1, ease_out), (1.1, 0.9), (1.75, -1, ease_out), (2.05, -0.95), (STALK_T, 0, ease_out))


def stalk(t):
    """the hunting walk: neck forward and low, the head held still in space while the body rocks under it; it scans
    from side to side, the head first and the neck after"""
    T = STALK_T
    p = A.walk_pose(t * A.WALK_T / T)
    w = 2 * math.pi * t / T
    add(p, "neck1", rot=(-22, 0, 0)); add(p, "neck2", rot=(-6, 0, 0)); add(p, "skull", rot=(24 - 1.5 * math.sin(2 * w), 0, 0))
    for k, (b, g) in enumerate((("skull", 6), ("neck3", 3), ("neck2", 8), ("neck1", 10))):
        sc = float(SCAN((t - 0.08 * k) % T))
        add(p, b, rot=(0, g * sc, -4 * sc if b == "skull" else 0))
    add(p, "jaw", rot=(-0.5 * max(0.0, wave(t, T, -0.6)), 0, 0))
    return p


# ------------------------------------------------------------------ turning on the spot: it steps round
TURN_T = 1.6
_TURN_N = 16
_TURN = {}
# which limb steps when (lead with the hand on the side it turns to), and the swing share of each step
_TURN_ORDER = (("hand", "r", 0.0), ("foot", "l", 0.25), ("hand", "l", 0.5), ("foot", "r", 0.75))
_SWING = 0.32


def _turn_key(i):
    """the turn to the RIGHT at grid step i: planted limbs slide to the left as the body swings right over them, the
    stepping one goes round to the right (the hands); the hind feet swing the other way round the centre"""
    if i not in _TURN:
        u0 = i / _TURN_N
        p = {}
        add(p, "body", rot=(A.STANCE_PITCH, 0, 0), pos=(0, A.BODY_Y, -2))
        add(p, "neck1", rot=(A.NECK1, 0, 0)); add(p, "neck2", rot=(A.NECK2, 0, 0)); add(p, "skull", rot=(A.SKULL, 0, 0))
        for limb, s, off in _TURN_ORDER:
            sx = 1 if s == "l" else -1
            u = (u0 - off) % 1.0
            if u < _SWING:
                sw = u / _SWING
                d = -0.5 + smooth(sw); lift = 3.5 * math.sin(math.pi * sw)
            else:
                d = 0.5 - (u - _SWING) / (1 - _SWING); lift = 0.0
            # the animal's right is -x: hands step to -x, feet to +x
            if limb == "hand":
                dx = -5.0 * d
                add(p, f"fingers_{s}", rot=(54 - 30 * min(1.0, lift / 2.0), 0, 0))
                A.hand_down(p, s, sx, (A.HAND_X * sx + dx, A.HAND_Y + lift, A.HAND_Z), hum_dir=A.HUM, fore_dir=A.FORE)
                A.fold_wing(p, s, sx)
            else:
                dx = 3.5 * d
                A.foot_down(p, s, sx, (6 * sx + dx, A.FOOT_Y + lift, 16))
        _TURN[i] = p
    return B.copy(_TURN[i])


def turn_right(t):
    """turning on the spot to its right (+ yaw): the head swings into the turn first, the neck after, the four limbs
    step round one after the other (right hand, left foot, left hand, right foot)"""
    T = TURN_T
    x = (t / T) % 1.0 * _TURN_N
    i = int(x) % _TURN_N
    p = A.lerp_pose(_turn_key(i), _turn_key((i + 1) % _TURN_N), x - int(x))
    for k, (b, g) in enumerate((("skull", 9), ("neck3", 3), ("neck2", 5), ("neck1", 8))):
        add(p, b, rot=(0, g + 1.5 * wave(t - 0.06 * k, T / 2, -0.4), 2.5 if b == "skull" else 0))
    # each step of a hand rocks the head a little (it is held steady, so only a little)
    add(p, "neck1", rot=(-0.8 * wave(t, T / 2, 0.3), 0, 0)); add(p, "skull", rot=(0.6 * wave(t, T / 2, -0.4), 0, 0))
    alive(p, t, k=0.5, period=T)
    return p


def turn_left(t):
    """the mirror of turn_right: led with - yaw"""
    return mirror(turn_right(t))


IDLE_TIRED_T = 3.0


def idle_tired(t):
    """spent after a chase or a long flight: lower on its legs, the neck down, the beak hanging open, panting fast
    (the body heaves on its planted limbs), the folded wings slack"""
    T = IDLE_TIRED_T
    pant = wave(t, T / 4)
    p = B.base(lift=round(-1.6 + 0.4 * pant, 1))
    add(p, "neck1", rot=(-12 - 1.4 * wave(t, T / 4, -0.5), 2.0 * wave(t, T, 0.5), 0))
    add(p, "neck2", rot=(-4 - 0.4 * wave(t, T / 4, -0.8), 1.2 * wave(t, T, -0.1), 0))
    add(p, "neck3", rot=(-0.3 * wave(t, T / 4, -1.0), 0, 0))
    add(p, "skull", rot=(8 - 1.0 * wave(t, T / 4, -1.2), 1.5 * wave(t, T, -0.6), 1.0 * wave(t, T, 1.0)))
    add(p, "jaw", rot=(-9 - 5 * max(0.0, wave(t, T / 4, -0.4)), 0, 0))
    for s, sx in SIDES:
        add(p, f"mem_forearm_{s}", scale=(1, 1, 1.05 + 0.02 * pant))
        add(p, f"mem_hand_{s}", scale=(1, 1, 1.04))
        add(p, f"finger1_{s}", rot=mir((0, 0, -2.0 + 0.6 * wave(t, T / 4, -0.9 - 0.5 * sx)), sx))
    return p


# ------------------------------------------------------------------ the strikes
JAB_T = 1.0
JAB_HIT = 0.34
# the spear thrust at a standing target ahead: the neck coils back and up (anticipation), the beak shut, then
# shoots forward and down so the beak drives in level (the hit at 0.34 s), a jolt on contact, it pulls the beak
# out and settles past the rest pose and back
J_N1 = tr((0, 0), (0.24, 16, ease_out), (0.34, -26, ease_in), (0.44, -24), (0.6, -6, ease_out), (1.0, 0, back_out))
J_N2 = tr((0, 0), (0.24, -10, ease_out), (0.34, 2, ease_in), (0.44, 1), (1.0, 0, back_out))
J_SK = tr((0, 0), (0.24, -12, ease_out), (0.34, 18, ease_in), (0.44, 16), (0.6, 4, ease_out), (1.0, 0, back_out))
J_YAW = tr((0, 0), (0.24, -4, ease_out), (0.34, 0.5, ease_in), (0.5, 0), (1.0, 0))
J_JAW = tr((0, 0), (0.1, 2), (0.24, 0), (0.34, 0), (0.5, 0), (0.58, 9, ease_out), (0.7, 0, ease_in), (1.0, 0))


def jab(t):
    p = B.base()
    jolt = math.exp(-((t - 0.37) / 0.04) ** 2)
    add(p, "neck1", rot=(float(J_N1(t)) + 2.5 * jolt, float(J_YAW(t)), 0))
    # the middle of the stiff neck follows late and only a little
    add(p, "neck2", rot=(float(J_N2(max(0.0, t - 0.03))), 0.6 * float(J_YAW(max(0.0, t - 0.04))), 0))
    add(p, "neck3", rot=(0.3 * float(J_N2(max(0.0, t - 0.05))), 0.4 * float(J_YAW(max(0.0, t - 0.06))), 0))
    add(p, "skull", rot=(float(J_SK(t)) - 3 * jolt, 0.5 * float(J_YAW(t)), 0))
    add(p, "jaw", rot=(-float(J_JAW(t)), 0, 0))
    # the folded wings take the push of the thrust a beat late
    for s, sx in SIDES:
        add(p, f"finger1_{s}", rot=mir((0, 0, -3 * math.exp(-((t - 0.42) / 0.1) ** 2)), sx))
    alive(p, t, k=0.4)
    return p


ATTACK_T = C.ATTACK_T   # 1.1 s, the damage at ~0.36 s (unchanged)
# the spear at prey on the ground: draws the head up and back, opens; drops like a spear (closing on contact at 0.36),
# a jolt, the catch flicked up, settles
K_DOWN = tr((0, 0), (0.2, -0.3, ease_out), (0.36, 1.0, ease_in), (0.5, 0.95), (0.75, -0.32, ease_out), (1.1, 0, back_out))
K_JAW = tr((0, 0), (0.2, 14, ease_out), (0.33, 18), (0.39, 0, ease_in), (0.7, 0), (0.78, 6), (0.9, 0), (1.1, 0))


def attack(t):
    p = B.base()
    jolt = math.exp(-((t - 0.39) / 0.04) ** 2)
    for k, b in enumerate(("neck1", "neck2", "neck3", "skull")):
        v = float(K_DOWN(max(0.0, t - 0.025 * k)))
        down, flick = max(0.0, v), max(0.0, -v)
        g = {"neck1": (-46, 20), "neck2": (-14, 0), "neck3": (-4, 4), "skull": (-10, 30)}[b]
        add(p, b, rot=(g[0] * down + g[1] * flick + (2 * jolt if b == "neck1" else -2 * jolt if b == "skull" else 0), 0, 0))
    add(p, "jaw", rot=(-float(K_JAW(t)), 0, 0))
    for s, sx in SIDES:
        add(p, f"finger1_{s}", rot=mir((0, 0, -3 * math.exp(-((t - 0.45) / 0.1) ** 2)), sx))
    alive(p, t, k=0.4)
    return p


# ------------------------------------------------------------------ display, call, eating
DISPLAY_T = C.DISPLAY_T   # 4.2 s
# it rises tall onto its forelimbs, then turns the crested head broadside to one side, holds, sweeps it through to the
# other side (the neck after the head) and holds again, the beak clattering in bursts, the wings half lifted
D_UP = tr((0, 0), (0.7, 1.04, ease_out), (0.95, 1.0), (3.6, 1.0), (4.2, 0, ease_in))
D_TURN = tr((0, 0), (0.85, 0), (1.45, 1.06, ease_out), (1.65, 1.0), (2.2, 0.94), (2.85, -1.06, ease_out), (3.05, -1.0), (3.5, -0.94),
            (4.05, 0.04, ease_out), (4.2, 0))
_TALL = {}


def _tall():
    if "q" not in _TALL:
        _TALL["q"] = B.base(pitch=A.STANCE_PITCH + 6)
    return B.copy(_TALL["q"])


def display(t):
    u = float(D_UP(t))
    p = A.lerp_pose(B.base(), _tall(), min(1.0, max(0.0, u)))
    # the clatter: bursts of the beak rattling, each burst an envelope, the rattle an organic shiver
    burst = window(t, 1.45, 2.15, 0.12) + window(t, 2.9, 3.5, 0.12)
    clat = max(0.0, tremor(t, (11.3, 15.7, 8.1), (1.0, 0.6, 0.4))) * burst
    for k, (b, g) in enumerate((("skull", 40), ("neck3", 6), ("neck2", 12), ("neck1", 10))):
        tu = float(D_TURN(max(0.0, t - 0.07 * k)))
        add(p, b, rot=(0, g * tu * u, -10 * tu * u if b == "skull" else 0))
    add(p, "neck1", rot=(18 * u, 0, 0)); add(p, "neck2", rot=(6 * u, 0, 0)); add(p, "skull", rot=(18 * u + 0.8 * clat, 0, 0))
    # a nod each time the crest comes broadside (the accent of the show)
    nod = math.exp(-((t - 1.5) / 0.1) ** 2) + math.exp(-((t - 2.9) / 0.1) ** 2)
    add(p, "skull", rot=(-4 * nod, 0, 0))
    add(p, "jaw", rot=(-(2.5 * u + 5 * clat), 0, 0))
    lift = window(t, 0.6, 3.6, 0.45)
    for s, sx in SIDES:
        sh = tremor(t, (7.9, 12.3, 5.3), (1.0, 0.5, 0.3), phase=0.8 * sx) * lift
        add(p, f"arm_{s}", rot=mir((0, 0, 14 * lift + 1.2 * sh), sx))
        add(p, f"finger1_{s}", rot=mir((0, 0, 2 * lift + 0.8 * sh), sx))
        add(p, f"mem_finger1_{s}", scale=(1, 1, 1 + 0.12 * lift))
    alive(p, t, k=0.6, period=2.1)
    return p


CALL_T = B.CALL_T   # 2.2 s, the voice at 0.4 s
C_UP = tr((0, 0), (0.38, 1, ease_out), (1.9, 1), (2.2, 0, ease_in))
# two hoarse calls, the second shorter: the beak opens in pulses (not held), the throat shivering under them
C_JAW = tr((0, 0), (0.35, 3), (0.42, 6), (0.6, 24, ease_out), (0.78, 20), (0.92, 26), (1.08, 6, ease_in), (1.2, 4),
           (1.32, 18, ease_out), (1.5, 21), (1.68, 4, ease_in), (1.9, 3), (2.2, 0))


def call(t):
    p = B.base()
    u = float(C_UP(t))
    env = window(t, 0.45, 1.75, 0.15)
    shiv = tremor(t, (9.4, 13.7, 6.1)) * env
    add(p, "neck1", rot=(28 * u + 0.4 * shiv, 0, 0))
    add(p, "neck2", rot=(8 * float(C_UP(max(0.0, t - 0.04))), 0, 0))
    add(p, "neck3", rot=(0.6 * tremor(t, (8.2, 12.6, 5.1), phase=0.9) * env, 0, 0))
    add(p, "skull", rot=(26 * float(C_UP(max(0.0, t - 0.06))) + 0.2 * float(C_JAW(t)) + 0.8 * shiv, 0, 0))
    j = float(C_JAW(t))
    add(p, "jaw", rot=(-(j + 1.2 * tremor(t, (10.7, 14.3, 7.9), phase=1.7) * env), 0, 0))
    add(p, "jaw", scale=(1 + 0.008 * j, 1 + 0.012 * j, 1))
    alive(p, t, k=1.0 - 0.7 * u)
    return p


EAT_T = C.SWALLOW_T   # 2.0 s


def eat(t):
    """the prey tossed up and swallowed whole: a dip to gather it, the toss, three gulps running down the neck, each
    one nodding the head, and the settle"""
    p = B.base()
    up = float(tr((0, 0), (0.18, -0.15, ease_out), (0.36, 1.05, ease_out), (0.5, 1.0), (1.55, 1.0), (2.0, 0, back_out))(t))
    toss = math.exp(-((t - 0.45) / 0.08) ** 2)
    add(p, "neck1", rot=(24 * up, 0, 0))
    add(p, "neck2", rot=(6 * float(tr((0, 0), (0.18, -0.15), (0.4, 1.0, ease_out), (1.6, 1.0), (2.0, 0, ease_out))(t)), 0, 0))
    add(p, "skull", rot=(44 * up + 10 * toss, 0, 0))
    add(p, "jaw", rot=(-(22 * toss + 4 * max(0.0, up)), 0, 0))
    for b, c in zip(("neck3", "neck2", "neck1"), (0.9, 1.15, 1.4)):
        g = math.exp(-((t - c) / 0.09) ** 2)
        add(p, b, scale=(1 + 0.25 * g, 1 + 0.25 * g, 1))
        add(p, "skull", rot=(2.5 * math.exp(-((t - c + 0.04) / 0.08) ** 2), 0, 0))
    alive(p, t, k=0.5)
    return p


DRINK_T = C.DRINK_T   # 3.6 s


def drink(t):
    """the long reach down, the beak scooping in a few laps, the head lifted to let it run down (two gulps)"""
    p = C.drink_pose(t)
    lap = window(t, 0.9, 2.0, 0.2)
    add(p, "jaw", rot=(-3 * lap * (0.5 + 0.5 * wave(t, 0.45)), 0, 0))
    add(p, "skull", rot=(1.5 * lap * wave(t, 0.45, -0.7), 0, 0))
    for b, c in zip(("neck3", "neck2", "neck1"), (2.85, 3.0, 3.15)):
        g = math.exp(-((t - c) / 0.08) ** 2)
        add(p, b, scale=(1 + 0.2 * g, 1 + 0.2 * g, 1))
    add(p, "neck3", rot=(1.5 * window(t, 0.5, 2.6, 0.4) * wave(t, 1.8), 0, 0))
    alive(p, t, k=0.5)
    return p


PREEN_T = B.PREEN_T   # 4.0 s


def preen(t):
    """turns round and runs the beak along the lifted wing, nibbling (the slide and the nibbles fade in and out)"""
    p = B.base()
    u = float(tr((0, 0), (0.6, 1, ease_out), (3.4, 1), (4.0, 0, ease_in))(t))
    env = window(t, 0.6, 3.4, 0.3)
    slide = wave(t - 0.6, 1.4) * env
    nib = 6 * max(0.0, wave(t, 0.35)) * env
    for k, (b, g) in enumerate((("skull", -20), ("neck3", -8), ("neck2", -40), ("neck1", -70))):
        uu = float(tr((0, 0), (0.6, 1, ease_out), (3.4, 1), (4.0, 0, ease_in))(max(0.0, t - 0.05 * k)))
        add(p, b, rot=(0, g * uu, 0))
    add(p, "neck1", rot=(30 * u, -8 * slide * u, 0)); add(p, "neck2", rot=(6 * u, 0, 0)); add(p, "skull", rot=(6 * u, 0, 20 * u))
    add(p, "jaw", rot=(-nib, 0, 0))
    add(p, "arm_l", rot=(0, -10 * u, 18 * u)); add(p, "forearm_l", rot=(0, 0, 8 * u))
    alive(p, t, k=0.5)
    return p


SHAKE_T = B.SHAKE_T   # 1.2 s


def shake(t):
    """shaking off the water: the head starts, the twist runs down the neck to the body, the wings rattle last"""
    p = B.base()

    def wob(u, d, a):
        e = math.exp(-((u - 0.5 - d) / 0.28) ** 2)
        return a * e * math.sin(2 * math.pi * 5.0 * (u - d))   # 4 frames a cycle at 20 fps
    add(p, "skull", rot=(0, 0.4 * wob(t, 0.0, 22), wob(t, 0.0, 22)))
    for k, (b, a) in enumerate((("neck3", 10), ("neck2", 12), ("neck1", 9))):
        add(p, b, rot=(0, wob(t, 0.04 * (k + 1), a), 0))
    for s, sx in SIDES:
        add(p, f"arm_{s}", rot=mir((0, 0, 10 * math.exp(-((t - 0.65) / 0.3) ** 2) + wob(t, 0.18, 4)), sx))
        add(p, f"finger1_{s}", rot=mir((0, 0, wob(t, 0.24, 3)), sx))
    add(p, "jaw", rot=(-5 * math.exp(-((t - 0.5) / 0.3) ** 2), 0, 0))
    alive(p, t, k=0.5)
    return p


SUN_T = B.SUN_T   # 5.0 s


def sun(t):
    p = B.sun_pose(t)
    u = window(t, 0.0, 5.0, 1.0)
    gust = tremor(t, (1.3, 2.9, 0.7), (1.0, 0.6, 0.5)) * u
    for s, sx in SIDES:
        trail(p, t, lambda v: 0.8 * tremor(v, (1.3, 2.9, 0.7), (1.0, 0.6, 0.5)) * window(v, 0.0, 5.0, 1.0),
              bones=tuple(f"{b}_{s}" for b in ("hand", "finger1", "finger2")), gain=(0.6, 1.0, 1.5), delay=0.08, axis=2, sx=sx)
        add(p, f"mem_finger2_{s}", scale=(1, 1, 1 + 0.01 * gust))
    alive(p, t, k=0.8, period=2.5)
    return p


SIT_T, SLEEP_T = B.SIT_T, B.SLEEP_T   # 4.0 s, 6.0 s


def sit(t):
    p = B.sit_pose(t)
    T = SIT_T
    for k, b in enumerate(("skull", "neck3", "neck2", "neck1")):
        add(p, b, rot=(0, (4, 1, 2, 3)[k] * wave(t - 0.1 * k, T, 0.5), 0))
    add(p, "skull", rot=(0.8 * wave(t, T / 2, 0.3), 0, 0))
    add(p, "jaw", rot=(-0.8 * max(0.0, wave(t, T, -0.6)), 0, 0))
    return p


def sleep(t):
    p = B.sleep_pose(t)
    tw = math.exp(-((t - 4.1) / 0.06) ** 2) + 0.6 * math.exp(-((t - 4.3) / 0.06) ** 2)
    add(p, "jaw", rot=(-3 * tw - 1.0 * max(0.0, wave(t, SLEEP_T, -0.6)), 0, 0))
    add(p, "skull", rot=(0.8 * tw, 0, 0))
    for s, sx in SIDES:
        add(p, f"finger1_{s}", rot=mir((0, 0, 1.5 * tw), sx))
    return p


# ================================================================== in the air
FLAP_T = A.FLAP_T   # 0.8 s
_DOWN = 0.42        # the share of the beat spent in the downstroke: heavy and fast down, slow and gathered up


def _warp(u):
    """beat phase -> stroke phase: 0..0.5 the downstroke (in _DOWN of the beat), 0.5..1 the upstroke"""
    u %= 1.0
    return 0.5 * u / _DOWN if u < _DOWN else 0.5 + 0.5 * (u - _DOWN) / (1 - _DOWN)


def fly(t):
    """the heavy flap: a fast downstroke that lifts the body (a little late), a slow upstroke with the wing half
    gathered; each segment out to the wing finger turns later (the tip arrives last); the neck takes the bob so the
    head stays level; the legs trail and swing late"""
    T = FLAP_T
    u = (t / T) % 1.0
    ph = _warp(u)
    w = 2 * math.pi * ph
    bob = -2.4 * math.cos(2 * math.pi * _warp(u - 0.08))
    pitch = -1.8 * math.sin(2 * math.pi * _warp(u - 0.05))
    pose = {}
    A.flight_body(pose, bob=bob, pitch=pitch)
    # the head steady: the neck chain cancels the bob, each segment a little later
    trail(pose, t, lambda v: 1.6 * math.cos(2 * math.pi * _warp(v / T - 0.08)), bones=("neck1", "neck2", "neck3", "skull"),
          gain=(1.0, 0.5, 0.3, -0.9), delay=0.03, axis=0, loop=T)
    add(pose, "jaw", rot=(-1.0, 0, 0))
    gather = 0.5 - 0.5 * math.cos(2 * math.pi * max(0.0, ph - 0.5) * 2) if ph > 0.5 else 0.0   # 0..1..0 over the upstroke
    for s, sx in SIDES:
        add(pose, f"arm_{s}", rot=mir((0, -5 * gather, 6 + 34 * math.cos(w)), sx))
        lag = 0.0
        for b, amp, yw in (("forearm", 9, -14), ("hand", 11, 10), ("finger1", 14, 5), ("finger2", 11, 0)):
            lag += 0.075
            wl = 2 * math.pi * _warp(u - lag)
            add(pose, f"{b}_{s}", rot=mir((0, yw * gather, amp * math.cos(wl)), sx))
        for b, k in (("hand", 0.12), ("finger1", 0.18), ("finger2", 0.2)):
            add(pose, f"mem_{b}_{s}", scale=(1, 1, 1 - k * gather))
        add(pose, f"thigh_{s}", rot=(2.2 * math.sin(2 * math.pi * _warp(u - 0.2)), 0, 0))
        add(pose, f"foot_{s}", rot=(3.0 * math.sin(2 * math.pi * _warp(u - 0.3)), 0, 0))
    return pose


GLIDE_T = A.GLIDE_T   # 4.0 s


def _glide_life(p, t, T, k=1.0):
    """the soaring never freezes: slow gusts run out along each wing to the tip (whole cycles per loop), the trailing
    edge ripples, the head looks round with the neck after it, the legs drift"""
    for s, sx in SIDES:
        g = lambda v, sx=sx: k * loop_tremor(v, T, (2, 3, 5), (1.0, 0.6, 0.4), phase=0.9 * sx)
        trail(p, t, g, bones=tuple(f"{b}_{s}" for b in WING), gain=(0.4, 0.3, 0.6, 1.0, 1.4), delay=0.09, axis=2, loop=T, sx=sx)
        add(p, f"mem_finger2_{s}", scale=(1, 1, 1 + 0.012 * k * loop_tremor(t, T, (23, 31, 41), (1.0, 0.6, 0.4), phase=sx)))
        add(p, f"mem_finger1_{s}", scale=(1, 1, 1 + 0.008 * k * loop_tremor(t, T, (19, 29, 37), (1.0, 0.6, 0.4), phase=0.5 * sx)))
        add(p, f"thigh_{s}", rot=(1.2 * k * wave(t, T, 0.7 * sx), 0, 0))
    trail(p, t, lambda v: 3.0 * k * wave(v, T, 0.4) + 1.5 * k * wave(v, T / 2, 1.1), bones=("skull", "neck3", "neck2", "neck1"),
          gain=(1.0, 0.4, 0.6, 0.8), delay=0.12, loop=T)
    trail(p, t, lambda v: 1.0 * k * wave(v, T / 2, -0.4), bones=("neck1", "neck2", "skull"), gain=(1.0, 0.5, -0.8), delay=0.1, axis=0, loop=T)


def glide(t):
    p = A.glide_pose(t)
    _glide_life(p, t, GLIDE_T)
    return p


BANK_T = B.BANK_T   # 3.0 s


def _bank(t, side):
    """the gliding turn: rolled in, the head leads into the turn and the neck follows, the outer wing tip lifts late"""
    p = B.bank_pose(t, side)
    _glide_life(p, t * B.GLIDE_SCALE, GLIDE_T, k=0.8)
    for k, (b, g) in enumerate((("skull", 6), ("neck3", 2), ("neck2", 3), ("neck1", 4))):
        add(p, b, rot=(0, side * g * (1 + 0.15 * wave(t - 0.1 * k, BANK_T)), 0))
    for s, sx in SIDES:
        inner = (sx == side)
        add(p, f"finger1_{s}", rot=mir((0, 0, -3 if inner else 2 + 1.0 * wave(t - 0.15, BANK_T)), sx))
        add(p, f"finger2_{s}", rot=mir((0, 0, -2 if inner else 3 + 1.5 * wave(t - 0.25, BANK_T)), sx))
    return p


def bank_left(t):
    return _bank(t, 1)


def bank_right(t):
    return _bank(t, -1)


# the takeoff ends in the flap: let it end in the new one (both modules call the flap by its module name)
A.fly_pose = fly
B.fly_pose = fly
