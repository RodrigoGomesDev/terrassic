"""Pteranodon: the fluid set (06/11/2026), in the spirit of the T. rex's (docs/estudos/08_ANIMACAO_RAXIORES.md), in the
Pteranodon's own way: a big fishing glider, all neck, beak and wing, with no tail to whip.
  * NOTHING STOPS: on the ground every pose breathes (`stand` blends two cached IK stances, so the chest rises and
    falls with the hands and feet still planted, at no IK cost per frame), the neck floats, the folded wing finger
    and the membranes twitch; in the air the wing tips trail the stroke, each joint later and wider than the last.
  * NOTHING SNAPS ON OR OFF: the old `if a < t < b` switches (call, preen, display) became envelopes (`window`).
  * THE TREMOR IS ORGANIC: sums of sines that never line up (`tremor`), different for the neck, the skull and the jaw.
  * THREE BEATS: anticipation (the neck coils back), the strike (~0.1 s), a settle that passes the rest pose a
    little and comes back (`back_out`). The neck drives the strike from the base and the skull arrives last (`trail`).
  * LOOPS CLOSE: every period divides the loop length.
New here: `jab` (the heron spear: neck coiled in an S, the closed beak driven forward-down, hit at JAB_HIT),
`crest_display` (the crest flagged broadside at a rival, Bennett 1992: the crests are display structures),
`turn_left` / `turn_right` on all fours (steps sideways, the head leads into the turn) and `idle_tired`.
"""
import math

import pteranim as A
import pteranims2 as B
from pteranim import S, SIDES, mir, lerp_pose, STANCE_PITCH, FLAP_T, GLIDE_T
from anim2 import add, smooth, ease_in, ease_out, back_out, Track

NECK = ("neck1", "neck2", "skull")


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def tremor(t, f=(7.3, 11.1, 4.7), amp=(1.0, 0.55, 0.35), phase=0.0):
    """an organic shiver: three sines at frequencies that never line up (-1.9 .. 1.9 at most)"""
    return sum(a * math.sin(2 * math.pi * fr * t + phase * (i + 1) + 1.3 * i) for i, (fr, a) in enumerate(zip(f, amp)))


def window(t, a, b, fade=0.25):
    """1 inside [a, b], easing in and out over `fade` s"""
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


def tr(*keys):
    return Track(list(keys))


def trail(p, t, fn, gain=(1.0, 1.3, 1.6), delay=0.06, axis=0, bones=NECK, loop=None):
    """follow-through down a chain: link k takes fn(t - k*delay) * gain[k] on `axis` (in a loop the delay wraps)"""
    for k, b in enumerate(bones):
        u = t - delay * k
        v = fn(u % loop if loop else max(0.0, u)) * gain[k]
        r = [0.0, 0.0, 0.0]; r[axis] = v
        add(p, b, rot=tuple(r))


def wing_trail(p, t, fn, gain=(0.0, 0.4, 0.8, 1.3, 1.9), delay=0.05, axis=2, loop=None):
    """the same down a wing (arm, forearm, hand, finger1, finger2), mirrored per side: the tip arrives last and widest"""
    for s, sx in SIDES:
        trail(p, t, lambda u: fn(u) * sx, gain=gain, delay=delay, axis=axis,
              bones=tuple(f"{b}_{s}" for b in ("arm", "forearm", "hand", "finger1", "finger2")), loop=loop)


# ------------------------------------------------------------------ the breathing stance (no IK per frame)
LIFT = 1.0


def stand(lift=0.0):
    """the ground stance with the chest raised or lowered by `lift` px (-1 .. 1): a blend of two cached IK stances,
    so the hands and feet stay where they are while the body breathes"""
    u = min(1.0, max(0.0, (lift + LIFT) / (2 * LIFT)))
    return B.copy(lerp_pose(B.base(lift=-LIFT), B.base(lift=LIFT), u))


def alive_upper(p, t, k=1.0, period=2.0):
    """the breathing layer without the body (for poses already standing): the neck rises a beat after the chest, the
    beak parts on the out-breath, the folded wing finger and the membranes breathe"""
    add(p, "neck1", rot=(-0.8 * k * wave(t, period, -0.5), 0, 0))
    add(p, "neck2", rot=(0.4 * k * wave(t, period, -0.9), 0, 0))
    add(p, "skull", rot=(-0.6 * k * wave(t, period, -1.3), 0, 0))
    add(p, "jaw", rot=(-0.8 * k * max(0.0, wave(t, period, -0.7)), 0, 0))
    for s, sx in SIDES:
        add(p, f"finger1_{s}", rot=mir((0, 0, 0.8 * k * wave(t, period, -1.0)), sx))
        add(p, f"mem_forearm_{s}", scale=(1, 1, 1 + 0.025 * k * wave(t, period, -0.6)))


def stand_alive(t, k=1.0, period=2.0, crouch=0.0):
    p = stand(0.35 * k * wave(t, period) - crouch)
    alive_upper(p, t, k, period)
    return p


# ------------------------------------------------------------------ idle: 6 s, nothing still, nothing in step
IDLE_T = 6.0
LOOK = tr((0, (0, 0)), (0.8, (0, 0)), (1.2, (6, 22), ease_out), (2.6, (5, 22)), (3.0, (-4, -18), ease_out), (4.2, (-4, -17)),
          (4.7, (0, 0), ease_in), (6.0, (0, 0)))


def idle(t):
    T = IDLE_T
    p = stand_alive(t, 1.0, T / 3)
    # the head looks round: the base of the neck turns first, the skull last (and it overshoots a little)
    trail(p, t, lambda u: float(LOOK(u)[1]), gain=(0.4, 0.3, 0.32), delay=0.07, axis=1)
    trail(p, t, lambda u: float(LOOK(u)[0]), gain=(0.3, 0.0, 0.5), delay=0.07, axis=0)
    # a slow drift under the looks, never in step with the breath
    add(p, "neck1", rot=(0.8 * wave(t, T / 2, 0.4), 1.5 * wave(t, T, 1.1), 0.6 * wave(t, T, 0.2)))
    add(p, "skull", rot=(0.7 * wave(t, T / 5, 1.6), 1.0 * wave(t, T / 4, 0.3), -0.15 * float(LOOK(t)[1]) + 1.2 * wave(t, T / 2, -0.9)))
    # the beak clacks twice (now with a little head jolt each time)
    clack = math.exp(-((t - 5.2) / 0.06) ** 2) + math.exp(-((t - 5.45) / 0.06) ** 2)
    add(p, "jaw", rot=(-8 * clack, 0, 0)); add(p, "skull", rot=(1.2 * clack, 0, 0))
    # the wing finger settles against the arm now and then
    for s, sx in SIDES:
        add(p, f"finger1_{s}", rot=mir((0, 1.2 * wave(t, T / 3, 0.8 + sx), 0.8 * wave(t, T / 2, -0.4 * sx)), sx))
    return p


# ------------------------------------------------------------------ tired: after a long chase or flight
IDLE_TIRED_T = 3.0


def idle_tired(t):
    """spent: the chest heaves fast, the beak hangs open panting, the head and neck low, the wing membranes slack"""
    T = IDLE_TIRED_T
    pant = wave(t, T / 4)
    p = stand(-0.55 + 0.45 * pant)
    add(p, "neck1", rot=(-12 - 1.8 * wave(t, T / 4, -0.6), 2.5 * wave(t, T, 0.5), 0))
    add(p, "neck2", rot=(-4 + 0.8 * wave(t, T / 4, -1.0), 1.5 * wave(t, T, -0.2), 0))
    add(p, "skull", rot=(-6 - 1.2 * wave(t, T / 4, -1.4), 1.5 * wave(t, T, -0.6), 1.0 * wave(t, T / 2, 0.3)))
    add(p, "jaw", rot=(-10 - 5 * max(0.0, wave(t, T / 4, -0.4)), 0, 0))
    for s, sx in SIDES:
        add(p, f"finger1_{s}", rot=mir((0, -2.0, 1.0 * wave(t, T / 4, -1.2)), sx))
        for b in ("forearm", "hand"):
            add(p, f"mem_{b}_{s}", scale=(1, 1, 1.06 + 0.02 * pant))
    return p


# ------------------------------------------------------------------ the strikes
ATTACK_T, ATTACK_HIT = 0.9, 0.42      # Pteranodon melee: the damage at ~0.42 s
AT_N = tr((0, 0), (0.26, -1, ease_out), (0.42, 1.2, ease_in), (0.5, 1.05), (0.72, -0.12, ease_out), (0.9, 0, ease_in))
AT_JAW = tr((0, 0), (0.22, 20, ease_out), (0.32, 22), (0.42, 0, ease_out), (0.9, 0))


def attack(t):
    """three beats: the neck rears back with the beak opening, the lunge with a snap at the hit, a settle that passes
    the rest pose; the skull arrives a beat after the base of the neck"""
    p = stand_alive(t, 0.6, 0.9, crouch=0.5 * window(t, 0.1, 0.45, 0.15))
    trail(p, t, lambda u: -22 * float(AT_N(u)), gain=(1.0, 0.45, 0.0), delay=0.035)
    trail(p, t, lambda u: 20 * max(0.0, float(AT_N(u))) - 8 * max(0.0, -float(AT_N(u))), gain=(0.0, 0.0, 1.0), delay=0.008)
    add(p, "jaw", rot=(-float(AT_JAW(t)), 0, 0))
    hit = math.exp(-((t - 0.45) / 0.05) ** 2)
    add(p, "skull", rot=(0, 2 * hit * wave(t, 0.09), 3 * hit))
    wing_trail(p, t, lambda u: 1.5 * math.exp(-((u - 0.45) / 0.08) ** 2), gain=(0.0, 0.0, 0.0, 1.0, 1.6), axis=2)
    return p


JAB_T, JAB_HIT = 1.1, 0.40
# neck1 drives, neck2 uncoils the S, the skull aims: (neck1, neck2, skull)
JAB = tr((0, (0, 0, 0)), (0.30, (16, -24, 12), ease_out), (0.40, (-30, 12, -10), ease_in), (0.48, (-27, 10, -8)),
         (0.85, (3, -2, 2), ease_out), (1.1, (0, 0, 0), ease_in))


def jab(t):
    """the beak as a spear (a heron's stab): the neck coils back into an S and the head cocks, a beat of aim, then the
    closed beak is driven forward and down (the hit at 0.40 s), a jolt of the impact, the neck draws back and
    settles past the rest pose"""
    p = stand_alive(t, 0.6, 1.1, crouch=0.8 * window(t, 0.05, 0.42, 0.2))
    for k, b in enumerate(NECK):
        trail(p, t, lambda u, k=k: float(JAB(u)[k]), gain=(1.0,), delay=0.0, bones=(b,))
    # the aim: a small sideways hold during the coil, and the shiver of a held strike
    aim = window(t, 0.12, 0.32, 0.1)
    add(p, "skull", rot=(0.6 * tremor(t, (9.1, 13.7, 6.2)) * aim, 3 * aim, -2 * aim))
    jolt = math.exp(-((t - 0.43) / 0.05) ** 2)
    add(p, "skull", rot=(3 * jolt, 0, 0)); add(p, "neck2", rot=(-2 * jolt, 0, 0))
    add(p, "jaw", rot=(-1.0 * aim - 3 * math.exp(-((t - 0.6) / 0.08) ** 2), 0, 0))
    # the folded wing tips jerk with the impact, late and growing
    wing_trail(p, t, lambda u: 2.0 * math.exp(-((u - 0.44) / 0.07) ** 2) - 1.0 * math.exp(-((u - 0.6) / 0.1) ** 2),
               gain=(0.0, 0.0, 0.0, 1.0, 1.7), axis=2)
    return p


# ------------------------------------------------------------------ voice and display
CALL_T = 2.2                        # the voice starts 0.4 s in (Pterosaur CALL_VOICE)
C_UP = tr((0, 0), (0.4, 1, ease_out), (1.7, 0.95), (2.05, 0, ease_in), (2.2, 0))


def call(t):
    """head up, beak wide, two hoarse calls with the throat pumping (envelopes, not switches), the neck shivering"""
    u = float(C_UP(t))
    c = math.exp(-((t - 0.62) / 0.16) ** 2) + 0.85 * math.exp(-((t - 1.36) / 0.18) ** 2)
    env = window(t, 0.45, 1.6, 0.18)
    shiv = tremor(t, (8.3, 12.7, 5.1), (0.9, 0.5, 0.3)) * env * (0.4 + 0.6 * min(1.0, c))
    p = stand_alive(t, 0.5 * (1 - u) + 0.3, 1.1, crouch=-0.6 * u)
    trail(p, t, lambda w: 28 * float(C_UP(w)), gain=(1.0, 0.28, 0.0), delay=0.06)
    add(p, "skull", rot=(26 * u + 6 * c + 1.2 * shiv, 0, 0)); add(p, "neck1", rot=(0.6 * shiv, 0, 0))
    add(p, "jaw", rot=(-(4 * u + 26 * c) - 1.6 * tremor(t, (9.6, 14.1, 6.6), phase=1.7) * env, 0, 0))
    add(p, "jaw", scale=(1 + 0.2 * c, 1 + 0.3 * c, 1))
    return p


DISPLAY_T = 3.4
D_UP = tr((0, 0), (0.5, 1, ease_out), (2.75, 1), (3.2, 0, ease_in), (3.4, 0))


def display(t):
    """the crest show at the colony: neck high, the head swung side to side broadside on (the base of the neck first,
    the crest last), the wings half raised and trembling with an envelope"""
    u = float(D_UP(t))
    env = window(t, 0.5, 2.9, 0.4)
    p = stand_alive(t, 0.6, 1.7)
    sw = lambda w: wave(w - 0.5, 1.2) * window(w, 0.5, 2.7, 0.4)
    trail(p, t, lambda w: 30 * float(D_UP(w)), gain=(1.0, 0.2, 0.13), delay=0.06)
    trail(p, t, lambda w: 18 * sw(w), gain=(0.67, 1.0, 1.22), delay=0.08, axis=1)
    trail(p, t, lambda w: -16 * sw(w), gain=(0.0, 0.0, 1.0), delay=0.08, axis=2)
    add(p, "jaw", rot=(-3 * u, 0, 0))
    tre = 2.4 * tremor(t, (5.6, 8.9, 3.7), (1.0, 0.5, 0.3)) * env
    for s, sx in SIDES:
        add(p, f"arm_{s}", rot=mir((0, -8 * u, 30 * u + tre), sx)); add(p, f"forearm_{s}", rot=mir((0, 0, 10 * u + 0.6 * tre), sx))
        add(p, f"finger1_{s}", rot=mir((0, 0, 1.2 * tre), sx))
    return p


CREST_T = 3.6
CR_UP = tr((0, 0), (0.45, -0.25, ease_out), (0.95, 1, ease_out), (2.95, 1), (3.4, 0, ease_in), (3.6, 0))
# the head flagged broadside: right, held, left, held (degrees of yaw at the skull)
CR_FLAG = tr((0, 0), (0.95, 0), (1.35, 34, ease_out), (1.8, 30), (2.25, -34, ease_out), (2.7, -30), (3.15, 0, ease_out), (3.6, 0))


def crest_display(t):
    """at a rival or a female: a dip, then the neck rises straight and the beak tips up so the crest stands high; the
    head is turned broadside to one side, held with the crest trembling, then the other; it ends with a beak clack
    and a settle (Bennett 1992: the crest is for show)"""
    up = float(CR_UP(t)); a = max(0.0, up); c = max(0.0, -up) / 0.25
    env = window(t, 1.0, 3.0, 0.3)
    shiv = tremor(t, (6.9, 10.6, 4.4), (1.0, 0.55, 0.35)) * env
    p = stand_alive(t, 0.7, 1.2, crouch=0.8 * c - 0.5 * a)
    trail(p, t, lambda w: 36 * max(0.0, float(CR_UP(w))) - 10 * max(0.0, -float(CR_UP(w))) / 0.25, gain=(1.0, 0.3, 0.45), delay=0.07)
    trail(p, t, lambda w: float(CR_FLAG(w)), gain=(0.3, 0.45, 0.6), delay=0.09, axis=1)
    # the crest tilts toward the onlooker: the skull rolls with the flag, and trembles while it is held
    add(p, "skull", rot=(0.8 * shiv, 0.3 * shiv, -0.35 * float(CR_FLAG(max(0.0, t - 0.12))) + 1.4 * shiv))
    add(p, "neck2", rot=(0.5 * shiv, 0, 0))
    clack = math.exp(-((t - 3.15) / 0.05) ** 2) + 0.7 * math.exp(-((t - 3.32) / 0.05) ** 2)
    add(p, "jaw", rot=(-2 * a - 10 * clack, 0, 0)); add(p, "skull", rot=(1.5 * clack, 0, 0))
    for s, sx in SIDES:
        lift = 14 * a * env
        add(p, f"arm_{s}", rot=mir((0, -4 * a * env, lift + 1.0 * shiv), sx))
        add(p, f"finger1_{s}", rot=mir((0, 0, 0.8 * shiv), sx))
    return p


# ------------------------------------------------------------------ the old one-shots, made alive
def eat(t):
    p = B.eat_pose(t)
    alive_upper(p, t, 0.5, B.EAT_T / 2)
    return p


PREEN_T = 4.0
PR_U = tr((0, 0), (0.6, 1, ease_out), (3.3, 1), (3.75, 0, ease_in), (4.0, 0))


def preen(t):
    """turns round and runs the beak along the lifted wing, nibbling the membrane (the nibbling fades in and out)"""
    p = stand_alive(t, 0.6, 2.0)
    u = float(PR_U(t)); env = window(t, 0.7, 3.2, 0.25)
    slide = wave(t - 0.6, 1.4) * env
    nib = 6 * max(0.0, wave(t, 0.4)) * env
    trail(p, t, lambda w: -float(PR_U(w)), gain=(70, 40, 20), delay=0.08, axis=1)
    add(p, "neck1", rot=(30 * u, -8 * slide, 0)); add(p, "neck2", rot=(6 * u, 0, 0)); add(p, "skull", rot=(6 * u, 3 * slide, 20 * u))
    add(p, "jaw", rot=(-nib, 0, 0))
    add(p, "arm_l", rot=(0, -10 * u, 18 * u)); add(p, "forearm_l", rot=(0, 0, 8 * u))
    add(p, "finger1_l", rot=(0, 0, 1.5 * slide)); add(p, "mem_forearm_l", scale=(1, 1, 1 + 0.04 * nib / 6))
    return p


def sun(t):
    p = B.sun_pose(t)
    alive_upper(p, t, 0.6, B.SUN_T / 2)
    u = window(t, 1.0, 4.0, 0.6)
    # the opened membranes ripple in the breeze, the tips later and wider
    wing_trail(p, t, lambda w: 1.2 * (wave(w, 1.25) + 0.5 * wave(w, 0.625, 1.1)) * u, gain=(0.0, 0.3, 0.7, 1.2, 1.8), delay=0.08)
    return p


def shake(t):
    p = B.shake_pose(t)
    e = math.sin(math.pi * min(1.0, t / B.SHAKE_T))
    wing_trail(p, t, lambda w: 5 * math.sin(2 * math.pi * w / 0.16) * math.sin(math.pi * min(1.0, w / (B.SHAKE_T - 0.15))),
               gain=(0.0, 0.4, 0.8, 1.2, 1.6), delay=0.03)
    add(p, "jaw", rot=(-4 * e, 0, 0))
    return p


def beg(t):
    p = B.beg_pose(t)
    alive_upper(p, t, 0.5, B.BEG_T / 2)
    wing_trail(p, t, lambda w: 3 * wave(w, 0.3, -0.6), gain=(0.0, 0.0, 0.5, 1.0, 1.5), delay=0.04, loop=B.BEG_T)
    return p


def sit(t):
    p = B.sit_pose(t)
    T = B.SIT_T
    add(p, "neck1", rot=(0.6 * wave(t, T / 2, 0.7), 2.5 * wave(t, T, 0.3), 0))
    add(p, "skull", rot=(0.8 * wave(t, T / 2, -0.3), 2.0 * wave(t, T, -0.6), 1.0 * wave(t, T, 1.2)))
    add(p, "jaw", rot=(-0.6 * max(0.0, wave(t, T, -0.8)), 0, 0))
    return p


def sleep(t):
    p = B.sleep_pose(t)
    tw = math.exp(-((t - 4.1) / 0.07) ** 2) + 0.5 * math.exp(-((t - 4.35) / 0.07) ** 2)
    add(p, "jaw", rot=(-3 * tw - 0.8 * max(0.0, wave(t, B.SLEEP_T, -0.6)), 0, 0)); add(p, "skull", rot=(1.2 * tw, 0, 0))
    for s, sx in SIDES:
        add(p, f"finger1_{s}", rot=mir((0, 0, 1.5 * tw * (1 if s == "l" else 0.4)), sx))
    return p


def swim(t):
    p = B.swim_pose(t)
    T = B.SWIM_T
    trail(p, t, lambda w: 2.5 * wave(w, T), gain=(0.4, 0.8, 1.2), delay=0.12, axis=1, loop=T)
    add(p, "jaw", rot=(-0.8 * max(0.0, wave(t, T / 2, -0.5)), 0, 0))
    for s, sx in SIDES:
        add(p, f"finger1_{s}", rot=mir((0, 0, 0.8 * wave(t, T, 0.6 * sx)), sx))
    return p


# ------------------------------------------------------------------ in the air
_FLY, _GLIDE = A.fly_pose, A.glide_pose


def fly(t):
    """the flap with follow-through: the wing tips trail the stroke later and wider, the membrane bellies on the
    downstroke, the neck takes the bob a beat late so the head stays level, the legs trail"""
    p = _FLY(t)
    T = FLAP_T
    w = 2 * math.pi * t / T
    for s, sx in SIDES:
        add(p, f"finger1_{s}", rot=mir((0, 0, 5 * math.cos(w - 1.7)), sx))
        add(p, f"finger2_{s}", rot=mir((0, 0, 8 * math.cos(w - 2.2)), sx))
        add(p, f"hand_{s}", rot=mir((0, 2 * math.sin(w - 1.2), 0), sx))
        down = max(0.0, -math.sin(w - 0.4))
        for b in ("hand", "finger1"):
            add(p, f"mem_{b}_{s}", scale=(1, 1, 1 + 0.06 * down))
        add(p, f"thigh_{s}", rot=(2.5 * math.sin(w - 1.6), 0, 1.0 * math.sin(w - 1.9) * sx))
        add(p, f"foot_{s}", rot=(4 * math.sin(w - 2.2), 0, 0))
    trail(p, t, lambda u: -1.8 * math.sin(2 * math.pi * u / T - 0.5), gain=(1.0, 0.6, -0.9), delay=0.06, loop=T)
    add(p, "jaw", rot=(-0.6 * max(0.0, math.sin(w - 1.0)), 0, 0))
    return p


def glide(t):
    """soaring: the long slow sway, the tips flexing to the air under them (a gust layer of sines that divide the loop),
    the head looking down and round, a beat behind the roll"""
    p = _GLIDE(t)
    T = GLIDE_T
    gust = 0.9 * wave(t, T / 5, 0.3) + 0.5 * wave(t, T / 7, 1.9) + 0.3 * wave(t, T / 11, 0.7)
    gate = 0.6 + 0.4 * wave(t, T / 2, -0.4)
    for s, sx in SIDES:
        g = gust * gate * (1 if s == "l" else 0.8)
        add(p, f"hand_{s}", rot=mir((0, 0, 0.4 * g), sx))
        add(p, f"finger1_{s}", rot=mir((0, 0, 0.9 * g + 0.6 * wave(t, T / 3, -0.6 * sx)), sx))
        add(p, f"finger2_{s}", rot=mir((0, 0, 1.5 * g + 1.0 * wave(t, T / 3, -1.1 * sx)), sx))
        add(p, f"mem_finger1_{s}", scale=(1, 1, 1 + 0.02 * g))
        add(p, f"thigh_{s}", rot=(1.0 * wave(t, T / 2, -1.0 + 0.5 * sx), 0, 0))
    trail(p, t, lambda u: -2.5 * wave(u, T), gain=(0.4, 0.7, 1.0), delay=0.25, axis=2, loop=T)
    trail(p, t, lambda u: 1.5 * wave(u, T / 2, 0.8), gain=(0.6, 0.0, 0.8), delay=0.2, axis=0, loop=T)
    add(p, "skull", rot=(0, 2.5 * wave(t, T / 3, 0.4), 0))
    return p


# rebind the flight loops where the old moves start from or end in them (takeoff, landing, banks, water takeoff),
# so their seams meet the new loops
A.fly_pose = fly
A.glide_pose = glide
B.fly_pose = fly
B.glide_pose = glide

BANK_T = B.BANK_T


def _bank(t, side):
    p = B.bank_pose(t, side)
    T = BANK_T
    # the head leads into the turn and looks down the inner wing; the outer wing tip works the air
    trail(p, t, lambda u: 2.0 * side * wave(u, T, 0.3), gain=(0.5, 0.8, 1.1), delay=0.15, axis=1, loop=T)
    for s, sx in SIDES:
        outer = (sx != side)
        add(p, f"finger2_{s}", rot=mir((0, 0, (1.4 if outer else 0.5) * wave(t, T / 4, 0.7 * sx)), sx))
    return p


def bank_left(t): return _bank(t, 1)
def bank_right(t): return _bank(t, -1)


# ------------------------------------------------------------------ on all fours: walk, run, turn
WALK_T, RUN_T = A.WALK_T, B.RUN_T


def walk(t):
    """the walk with the neck counter-swinging a beat late and the head steadied; the folded wing finger bobs"""
    p = A.walk_pose(t)
    T = WALK_T
    trail(p, t, lambda u: -1.6 * wave(u, T, -0.4), gain=(0.6, 0.8, 0.7), delay=0.07, axis=1, loop=T)
    trail(p, t, lambda u: 1.2 * wave(u, T / 2, -0.9), gain=(0.6, 0.4, -0.8), delay=0.06, axis=0, loop=T)
    add(p, "jaw", rot=(-0.6 * max(0.0, wave(t, T / 2, -1.4)), 0, 0))
    for s, sx in SIDES:
        add(p, f"finger1_{s}", rot=mir((0, 0, 1.2 * wave(t, T / 2, -1.6)), sx))
    return p


def run(t):
    p = B.run_pose(t)
    T = RUN_T
    trail(p, t, lambda u: -3.0 * wave(u, T, -0.9), gain=(0.4, 0.5, -0.8), delay=0.05, axis=0, loop=T)
    add(p, "jaw", rot=(-2 - 2 * max(0.0, wave(t, T, -1.5)), 0, 0))
    for s, sx in SIDES:
        add(p, f"finger1_{s}", rot=mir((0, 0, 2.0 * wave(t, T, -1.9)), sx))
        add(p, f"mem_hand_{s}", scale=(1, 1, 1 + 0.03 * wave(t, T, -1.2)))
    return p


TURN_T = 1.4
_TURN = {}


def _side_step(u, L, lift=3.0):
    """stance 60 % (the planted limb slides across under the turning body), swing 40 % (lifted back across)"""
    if u < 0.6:
        return L / 2 - L * (u / 0.6), 0.0
    sw = (u - 0.6) / 0.4
    return -L / 2 + L * smooth(sw), lift * math.sin(math.pi * sw)


def _turn_right(t):
    """turning on the spot to its right, on all fours: the hands step to the right and the feet to the left, the body
    swings with each step, the head leads into the turn (+ yaw = the animal's right)"""
    key = int(round((t % TURN_T) * 200))
    if key in _TURN:
        return B.copy(_TURN[key])
    ph = (t / TURN_T) % 1.0
    w = 2 * math.pi * ph
    p = {}
    add(p, "body", rot=(STANCE_PITCH + 1.0 * math.sin(2 * w), 3.0 + 1.5 * math.sin(w), 1.2 * math.sin(w)),
        pos=(0, A.BODY_Y + 0.5 * math.cos(2 * w), -2))
    add(p, "neck1", rot=(-30 - 1.2 * math.sin(2 * w - 0.6), 8 + 1.5 * math.sin(w - 0.5), 0))
    add(p, "neck2", rot=(14, 6 + 1.2 * math.sin(w - 0.9), 0))
    add(p, "skull", rot=(-18 + 1.0 * math.sin(2 * w - 1.3), 6 + 1.0 * math.sin(w - 1.3), -2.5))
    for s, sx, oh, of in (("l", 1, 0.0, 0.5), ("r", -1, 0.5, 0.0)):
        dx, lift = _side_step((ph + oh) % 1.0, 5.0)
        add(p, f"fingers_{s}", rot=(54 - 30 * min(1.0, lift / 2.0), 0, 0))
        A.hand_down(p, s, sx, (A.HAND_X * sx - dx, A.HAND_Y + lift, A.HAND_Z - 1), hum_dir=A.HUM, fore_dir=A.FORE)
        A.fold_wing(p, s, sx)
        dx, lift = _side_step((ph + of) % 1.0, 4.0)
        A.foot_down(p, s, sx, (6 * sx + dx, A.FOOT_Y + lift, 15))
    _TURN[key] = B.copy(p)
    return p


def mirror(p):
    """the pose seen in a mirror: left and right swapped, yaw and roll reversed"""
    out = {}
    for k, v in p.items():
        k2 = k[:-2] + ("_r" if k.endswith("_l") else "_l") if k.endswith(("_l", "_r")) else k
        sc = v[2] if len(v) > 2 else None
        out[k2] = ([v[0][0], -v[0][1], -v[0][2]], [-v[1][0], v[1][1], v[1][2]], sc)
    return out


def turn_right(t):
    p = _turn_right(t)
    alive_upper(p, t, 0.5, TURN_T / 2)
    return p


def turn_left(t):
    p = mirror(_turn_right(t))
    alive_upper(p, t, 0.5, TURN_T / 2)
    return p
