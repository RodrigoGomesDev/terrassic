"""Gallimimus: the fluid set (06/11/2026). Rodrigo asked for the T. rex's fluidity on the remade species, each in its own
way and with a study behind it (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md: "corredor; sem armas: foge; encurralado,
chute"). The principles are the T. rex's (docs/estudos/08: nothing stops, nothing snaps on or off, three beats per
action, the chain follows late, breathing under every action); the body is an ostrich's, not a tyrant's:
  * the stride is LIGHT: the hips roll and yaw little (~3 deg), the head is pushed fore and aft with each step and the
    supple tail (no ossified tendons here) whips with a lag growing to the tip; the feathered arms trail, passive;
  * the head moves like a bird's: quick looks that stop dead, but each now lands with a small overshoot and settles,
    and the breath and the weight never stop under them;
  * it turns like a bird: the head snaps round first, then two high, quick steps per foot bring the body after it,
    the tail flicking out as a counterweight;
  * it rests like an ostrich: down onto the heels first, then the belly, the neck upright all the way; it gets up with
    a forward rock and a pump of the neck, and shakes its plumage smooth;
  * spent, it pants as birds do: a fast gular flutter of the throat with the beak open and the arms held away from the
    body to shed heat;
  * cornered (it has no weapon but its legs): it kicks forward (`attack`) or, with something behind it, it tips forward,
    looks back with one eye and drives one leg back and up (`kick_back`).
"""
import math

from anim2 import add, smooth, ease_in, ease_out, back_out, Track
import gallianims as A

SIDES = A.SIDES
T = A.T
TAILS, NECKS = A.TAILS, A.NECKS
neck, tail, arms, reach, fold, ground_fit, eye_look = A.neck, A.tail, A.arms, A.reach, A.fold, A.ground_fit, A.eye_look


def tr(*keys): return Track(keys)


def window(t, a, b, fade=0.25):
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def whip(p, t, fn, axis=1, delay=0.05, gain=(0.6, 0.85, 1.1, 1.35, 1.6, 1.85), loop=None):
    """follow-through down the supple tail: each bone takes fn later and wider than the one before"""
    for k, b in enumerate(TAILS):
        u = t - delay * (k + 1)
        v = fn(u % loop if loop else max(0.0, u)) * gain[k]
        r = [0.0, 0.0, 0.0]; r[axis] = v
        add(p, b, rot=tuple(r))


def alive_upper(p, t, k=1.0, period=2.4, slow=None):
    """a bird's breath (quicker than a big animal's), on the neck, the beak, the arms and the tail"""
    add(p, "neck1", rot=(-0.5 * k * wave(t, period, -0.4), 0, 0))
    add(p, "neck3", rot=(0.3 * k * wave(t, period, -0.9), 0, 0))
    add(p, "jaw", rot=(-0.4 * k * max(0.0, wave(t, period, -0.6)), 0, 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(1.2 * k * wave(t, period, -0.8 - o), 0, 0.8 * k * wave(t, period, -1.0)))
    for i, b in enumerate(TAILS):
        add(p, b, rot=(0.3 * k * wave(t, period, -0.4 * i), 0.5 * k * (1 + 0.3 * i) * wave(t, (slow or period * 2.5), -0.6 * i), 0))


def landing(x):
    x %= 1.0
    return -1.0 + 2.0 * smooth(x / 0.25) if x < 0.25 else 1.0 - 2.0 * smooth((x - 0.25) / 0.75)


def snap(t, keys, dur=0.22):
    """a bird's look: quick moves that stop with a small overshoot and settle (back_out), keys = [(t, (p, y, r))]"""
    cur = (0.0, 0.0, 0.0)
    for tk, v in keys:
        if t < tk: break
        x = min(1.0, (t - tk) / dur)
        u = 1.06 * smooth(x / 0.7) if x < 0.7 else 1.06 - 0.06 * smooth((x - 0.7) / 0.3)      # a little past, back
        cur = tuple(cur[i] + (v[i] - cur[i]) * u for i in range(3))
    return cur


# the old poses' bird looks (sentinel, sit, brood) stopped dead in 0.08-0.1 s: a 50 deg jump in one frame. Still quick,
# now over 4 frames, a little past and back
A.snap = lambda t, keys, dur=0.1: snap(t, keys, max(dur, 0.26))


# ------------------------------------------------------------------ the light stride
def gait(t, Tc, stride, duty, lift, bob, lean=0.0, drop=0.0, head=0.0, roll=3.0, yaw=2.6, stance_clear=-0.05,
         swing=1.0, arm_out=0.0, tail_amp=1.0, turn=None):
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    if turn: add(p, "body", rot=turn[0], pos=turn[1])          # (the jink) before the feet are planted
    b2 = landing(2 * ph + 0.05)
    hroll = roll * math.sin(w + 0.3); hyaw = yaw * math.sin(w - 0.5)
    add(p, "body", rot=(lean + 0.8 * b2, hyaw, hroll), pos=(0, bob * b2 - 0.5 - drop, 0))
    # the head is pushed forward as a foot lands, held while the body catches up (the bird's head-bob), the base of the
    # neck cancelling the hips so the head travels level
    nod = swing * 4.0 * math.sin(2 * w - 1.3)
    neck(p, head - lean * 0.8 - 0.8 * b2 + nod, -0.8 * hyaw, -0.85 * hroll)
    add(p, "skull", rot=(-head * 0.3 - nod * 0.7 + 0.5 * landing(2 * ph - 0.15), 0.6 * math.sin(w - 1.8), -0.25 * hroll))
    # the supple tail: a whip, each bone later and wider, bobbing late after the landing
    for k, b in enumerate(TAILS):
        lag = 0.6 + 0.4 * k
        add(p, b, rot=(lean * 0.06 + 0.5 * landing(2 * ph - 0.08 - 0.05 * k), -tail_amp * (0.8 + 0.4 * k) * math.sin(w - 0.6 - lag), 0))
    for s, o in SIDES:
        f = w + o * 2 * math.pi
        sx = 1 if s == "l" else -1
        add(p, f"arm_{s}", rot=(2.5 * math.sin(f - 2.4) + 1.5 * landing(2 * ph - 0.3), 0, arm_out * sx))
        add(p, f"forearm_{s}", rot=(3.0 * math.sin(f - 3.0) + 2.0 * landing(2 * ph - 0.4), 0, 0))
    for s, o in SIDES:
        sx = 1 if s == "l" else -1
        u = (ph + o) % 1.0
        sw_ = 0.0 if u < duty else math.sin(math.pi * (u - duty) / (1 - duty))
        add(p, f"thigh_{s}", rot=(0, -hyaw, -hroll + sx * 2.0 * sw_))
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0
            meta = 30 * smooth(max(0, (st - 0.55) / 0.45)); clear = stance_clear
            toe = 10 * (1 - smooth(min(1.0, st / 0.15))) + 12 * smooth(max(0, (st - 0.7) / 0.3))
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e
            ly = lift * math.sin(math.pi * min(1, sw * 1.1)) ** 1.1
            meta = 30 * (1 - smooth(sw / 0.4)) - 30 * math.sin(math.pi * sw)
            toe = -55 * math.sin(math.pi * min(1, sw * 1.15)) + 10 * smooth((sw - 0.75) / 0.25)
            clear = 1.2 * math.sin(math.pi * sw) ** 0.5 + 0.5 * math.sin(math.pi * sw)   # the curling toes swept 0.4 px under between keys
        T.plant(p, s, ly, dz - 2, meta, toe, clear)
    return p


def walk(t):
    # the stance foot kept a hair up: between two exported keys the rolling hips swept the planted toes 0.4 px down
    return gait(t, *A.WALK, stance_clear=0.15)


def run(t, turn=None):
    """the sprint: the neck reaches forward and low, the tail a level beam that still flicks at the tip, the arms a
    little open (balance)"""
    p = gait(t, *A.RUN, lean=6, drop=3, head=-36, roll=1.6, yaw=1.6, stance_clear=0.2, swing=0.5, arm_out=10, tail_amp=0.6,
             turn=turn)
    arms(p, -16, 14)
    tail(p, pitch=-3)
    return p


WALK_TIRED_T = 1.6


def walk_tired(t):
    """spent: shorter, slower steps, the neck low and the beak open, the throat fluttering, the arms held out"""
    p = gait(t, WALK_TIRED_T, 40, 0.66, 6, 1.2, drop=1.0, head=-14, roll=3.6, yaw=2.4, swing=0.7, arm_out=12,
             stance_clear=0.15)
    flutter = 0.6 + 0.4 * wave(t, WALK_TIRED_T / 2)
    add(p, "jaw", rot=(-9 - 2.5 * flutter * (0.5 + 0.5 * wave(t, WALK_TIRED_T / 16)), 0, 0))
    return p


# ------------------------------------------------------------------ standing
IDLE_T = 8.0
LOOKS = [(0.0, (0, 0, 0)), (0.9, (2, 22, -14)), (2.3, (4, 30, -18)), (3.1, (0, 0, 0)), (4.2, (-2, -26, 16)),
         (5.6, (3, -14, 8)), (6.8, (0, 0, 0))]


def idle(t):
    """breathing; it looks about with one eye at a time in bird's jerks that settle, the weight drifting from foot to
    foot, the tail making a slow S"""
    p = {}
    Ti = IDLE_T
    br = wave(t, Ti / 4)
    shift = wave(t, Ti, 0.4) + 0.3 * wave(t, Ti / 2, 1.0)
    hroll = 1.2 * shift; hyaw = 0.8 * shift
    add(p, "body", rot=(0.6 * br, hyaw, hroll), pos=(0, 0.25 * br - 0.2 * abs(shift), 0))
    hp, hy, hr = snap(t, LOOKS)
    neck(p, hp * 0.6 - 0.6 * wave(t, Ti / 4, -0.5), hy * 0.6 - 0.8 * hyaw, -0.8 * hroll)
    add(p, "skull", rot=(hp * 0.4 + 0.5 * wave(t, Ti / 5, 1.2), hy * 0.4, hr))
    add(p, "jaw", rot=(-0.4 - 0.6 * smooth(max(0.0, wave(t, Ti / 4, -0.9))), 0, 0))
    for k, b in enumerate(TAILS):
        add(p, b, rot=(0.4 * wave(t, Ti / 4, -0.5 - 0.4 * k), (0.6 + 0.35 * k) * wave(t, Ti, -0.9 - 0.6 * k) + 0.4 * wave(t, Ti / 2, 0.5 - 0.7 * k), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(1.2 * br + 1.0 * wave(t, Ti / 2, -1 - 3 * o), 0, 0))
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, -hyaw, -hroll))
    return T.stand(p)


IDLE_TIRED_T = 3.2


def idle_tired(t):
    """after a long run: the beak open and the throat fluttering fast (birds shed heat so), the arms held away from the
    body, the neck lower, the chest heaving"""
    p = {}
    Ti = IDLE_TIRED_T
    heave = wave(t, Ti / 4)
    flutter = wave(t, Ti / 24) * (0.7 + 0.3 * wave(t, Ti / 4, 0.6))       # ~7.5 Hz, swelling with each breath
    add(p, "body", rot=(-2 + 1.2 * heave, 0, 0.6 * wave(t, Ti, 0.3)), pos=(0, -1.0 + 0.5 * heave, 0))
    neck(p, -16 - 1.5 * wave(t, Ti / 4, -0.6), 3 * wave(t, Ti, 0.5))
    add(p, "skull", rot=(6 + 0.6 * flutter, 2 * wave(t, Ti, -0.4), 0))
    add(p, "jaw", rot=(-10 - 1.5 * flutter, 0, 0))
    for k, b in enumerate(TAILS):
        add(p, b, rot=(1.5 + 0.4 * heave, (0.5 + 0.3 * k) * wave(t, Ti, -0.7 * k), 0))
    arms(p, -6 + 1.5 * heave, 6, 14 + 2 * wave(t, Ti / 4, -0.8))
    return T.stand(p)


# ------------------------------------------------------------------ turning on the spot: head first, then quick steps
TURN_T = 0.8


def turn(t, side):
    # + yaw swings the head to the animal's RIGHT in game, so a turn to the left leads with - yaw
    d = 1.0 if side == "left" else -1.0
    ph = (t / TURN_T) % 1.0; w = 2 * math.pi * ph; p = {}
    lead = -d
    add(p, "body", rot=(0, lead * (3.0 + 1.0 * math.sin(2 * w)), 1.8 * math.sin(2 * w + 0.3)), pos=(0, -0.4 + 0.4 * math.cos(2 * w), 0))
    # the head is already round where it is going (a bird's head leads), the neck carries it, the body follows
    neck(p, 2.0, lead * (22.0 + 3.0 * math.sin(2 * w - 0.6)), lead * 4.0)
    add(p, "skull", rot=(0, lead * 10.0, -lead * 8.0))
    for k, b in enumerate(TAILS):
        add(p, b, rot=(0.3 * math.sin(2 * w - 0.5 * k), -lead * (1.5 + 0.8 * k) - (0.5 + 0.3 * k) * math.sin(2 * w - 1.0 - 0.5 * k), 0))
    for s, o in SIDES:
        f = w + o * 2 * math.pi
        add(p, f"arm_{s}", rot=(2 * math.sin(f - 2.0), 0, 0))
        u = (ph + o) % 1.0
        if u < 0.45:                             # a high quick step, the toes curled shut in the air
            sw = u / 0.45
            ly = 8.0 * math.sin(math.pi * sw) ** 1.2
            dz = -3.0 * math.cos(math.pi * sw)
            add(p, f"thigh_{s}", rot=(0, lead * 5.0 * math.sin(math.pi * sw), 0))
            T.plant(p, s, ly, dz, 14 * math.sin(math.pi * sw), -45 * math.sin(math.pi * sw), clear=1.0 * math.sin(math.pi * sw) ** 0.5)
        else:
            T.plant(p, s, 0.0, 3.0 - 6.0 * (u - 0.45) / 0.55)
        add(p, f"thigh_{s}", rot=(0, -lead * 3.0, 0))
    return p


def turn_left(t): return turn(t, "left")
def turn_right(t): return turn(t, "right")


# ------------------------------------------------------------------ combat: the legs
ATTACK_T = 1.0
K_UP = tr((0, 0), (0.28, 1, ease_out), (0.38, 1.05), (0.48, -0.15, ease_in), (0.66, 0.05), (1.0, 0, smooth))
K_STRIKE = tr((0, 0), (0.36, 0), (0.47, 1, ease_in), (0.56, 0.7), (0.85, 0, smooth), (1.0, 0))


def attack(t):
    """the forward kick, in three beats: the weight onto the left leg, the right knee drawn high with the toes curled
    (anticipation), the foot driven forward and down (the blow at 0.47 s), a peck follows, and it settles"""
    p = {}
    up = float(K_UP(t)); strike = float(K_STRIKE(t))
    peck = math.exp(-((t - 0.7) / 0.07) ** 2)
    u = max(0.0, up)
    add(p, "body", rot=(4 * u - 3 * strike, 0, -3 * u), pos=(-1.2 * u, 0, -1.0 * strike))
    neck(p, 6 * u - 26 * peck, 0); add(p, "skull", rot=(-4 * peck, 0, 0)); add(p, "jaw", rot=(-12 * peck, 0, 0))
    arms(p, -18 * u, 10 * u, 18 * u + 6 * strike)
    whip(p, t, lambda v: 2.5 * float(K_UP(v)) - 4 * float(K_STRIKE(v)), axis=0, delay=0.04)
    alive_upper(p, t, k=0.5)
    T.plant(p, "l")
    T.plant(p, "r", 22 * u + 4 * strike, -14 * u - 18 * strike, -30 * u + 30 * strike, -30 * u, clear=None)
    return p


KICK_BACK_T = 1.2
KICK_BACK_HIT = 0.46
KB_LOAD = tr((0, 0), (0.3, 1, ease_out), (0.4, 1.0), (0.5, 0.2, ease_in), (0.75, 0.0), (1.2, 0, smooth))
KB_DRIVE = tr((0, 0), (0.36, 0), (0.46, 1, ease_in), (0.56, 0.85), (0.9, 0.05, smooth), (1.2, 0, smooth))
KB_LOOK = tr((0, 0), (0.2, 1, ease_out), (0.85, 1), (1.2, 0, smooth))


def kick_back(t):
    """something behind it: the head snaps round to look back with one eye, the body tips forward over the left leg,
    the right knee is drawn up under the belly (anticipation), then the foot is driven straight back and up (the blow
    at 0.46 s), the tail swinging aside out of its way; the foot comes back down and the body levels"""
    p = {}
    load = float(KB_LOAD(t)); drive = float(KB_DRIVE(t)); look = float(KB_LOOK(t))
    tip = max(load, drive)
    add(p, "body", rot=(-8 * tip - 4 * drive, 0, -3 * tip), pos=(-1.2 * tip, -1.0 * tip, 0))
    neck(p, -6 * tip, -38 * look, -6 * look)
    eye_look(p, -1.0, look)
    add(p, "jaw", rot=(-6 * math.exp(-((t - 0.46) / 0.08) ** 2), 0, 0))
    arms(p, -10 * tip, 8 * tip, 16 * tip + 8 * drive)
    whip(p, t, lambda v: 10 * float(KB_DRIVE(v)) + 3 * float(KB_LOAD(v)), delay=0.04)
    whip(p, t, lambda v: -4 * float(KB_DRIVE(v)), axis=0, delay=0.04)
    alive_upper(p, t, k=0.5)
    T.plant(p, "l")
    T.plant(p, "r", 14 * load + 12 * drive, 2 * load + 26 * drive, -20 * load + 50 * drive, -35 * load + 20 * drive, clear=None)
    return p


def hurt(t):
    """flinch: the body jerks away, the neck whips up and back, the wings flick open and fold again"""
    p = {}
    e = math.exp(-t / 0.13) * smooth(t / 0.04)
    add(p, "body", rot=(4 * e, 0, 3 * e), pos=(0, 0, 2 * e))
    neck(p, 16 * e, -8 * e); add(p, "skull", rot=(10 * e, 0, 8 * e)); add(p, "jaw", rot=(-10 * e, 0, 0))
    whip(p, t, lambda u: 6 * math.exp(-u / 0.18) * smooth(u / 0.05), delay=0.035)
    arms(p, -14 * e, 10 * e, 24 * e)
    alive_upper(p, t, k=0.5)
    return T.stand(p)


# ------------------------------------------------------------------ resting: down on the heels first, up with a rock
LIE_DOWN_T = 2.2


def lie_down(t):
    """an ostrich's sit: it drops onto its heels first (the legs fold, the body low but still up), a pause, then the
    belly goes down; the neck stays upright all the way and the plumage is shaken smooth at the end"""
    p = {}
    k = float(tr((0, 0), (0.2, 0.03), (0.75, 0.62, ease_in), (1.05, 0.64), (1.6, 1.0, ease_in), (2.2, 1.0))(t))
    land = math.exp(-((t - 1.62) / 0.08) ** 2)
    sh = window(t, 1.75, 2.1, 0.08) * math.sin(2 * math.pi * 9 * t)
    fold(p, k)
    neck(p, 4 * window(t, 0.2, 1.5, 0.3) - 2 * land, 0); add(p, "skull", rot=(2 * land, 0, 0))
    add(p, "body", rot=(0.8 * land, 0, 3 * sh)); arms(p, 0, 0, 10 * abs(sh))
    whip(p, t, lambda u: -2.5 * math.exp(-((u - 1.62) / 0.12) ** 2), axis=0, delay=0.05)
    alive_upper(p, t, k=0.5)
    return ground_fit(p)


GET_UP_T = 1.8


def get_up(t):
    """a rock forward with the neck pumped low and forward, then up in one push off the heels, the neck swinging back
    up; a shake of the plumage"""
    p = {}
    k = float(tr((0, 1.0), (0.45, 1.0), (1.0, 0.0, ease_out), (1.8, 0.0))(t))
    rock = math.exp(-((t - 0.5) / 0.16) ** 2)
    sh = window(t, 1.25, 1.6, 0.08) * math.sin(2 * math.pi * 9 * t)
    fold(p, k)
    add(p, "body", rot=(-6 * rock, 0, 3 * sh))
    neck(p, -22 * rock + 6 * math.exp(-((t - 0.95) / 0.15) ** 2), 0)
    arms(p, -6 * rock, 0, 10 * rock + 10 * abs(sh))
    whip(p, t, lambda u: 3 * math.exp(-((u - 0.5) / 0.2) ** 2), axis=0, delay=0.05)
    alive_upper(p, t, k=0.5)
    return ground_fit(p)


# ------------------------------------------------------------------ the rest: the breathing layer under the old poses
def lively(fn, k=0.5, period=None):
    """the breath under an old pose (in a loop, `period` = the loop's length so the seam still closes)"""
    def g(t):
        p = fn(t)
        if period: alive_upper(p, t, k=k, period=period, slow=period)
        else: alive_upper(p, t, k=k)
        return p
    g.__name__ = fn.__name__
    g.__doc__ = fn.__doc__
    return g


def jink(t):
    """the escape side-step on the fluid run"""
    k = float(tr((0, 0), (0.12, 1, ease_out), (0.36, 1), (0.6, 0, smooth))(t))
    p = run(t % A.RUN[0], turn=((0, 16 * k, 12 * k), (1.5 * k, -1.0 * k, 0)))
    neck(p, 0, -20 * k, -10 * k)
    whip(p, t, lambda u: -8 * float(tr((0, 0), (0.12, 1, ease_out), (0.36, 1), (0.6, 0, smooth))(u)), delay=0.04)
    add(p, "arm_l", rot=(-10 * k, 0, 40 * k)); add(p, "forearm_l", rot=(14 * k, 0, 12 * k))
    return p


def beg(t):
    """asks for food: quick little pecks in the air toward the owner, the head tilted to look with one eye; the old
    one's wing flutter ran 9.6 cycles in the 1.6 s loop (a 2 deg jump at the seam): now 10"""
    p = {}; br = math.sin(2 * math.pi * t / 1.6)
    add(p, "body", rot=(-4 + 0.6 * br, 0, 0), pos=(0, -1.5, 0))
    pk = sum(math.exp(-((t - c) / 0.05) ** 2) for c in (0.3, 0.5, 1.1, 1.3))
    neck(p, -14 - 8 * pk, 0); eye_look(p, 1.0, 0.7)
    add(p, "skull", rot=(-6 * pk, 0, 0)); add(p, "jaw", rot=(-8 * pk, 0, 0))
    arms(p, -4, 0, 6 + 4 * math.sin(2 * math.pi * 6.25 * t))
    tail(p, yaw=2 * br, pitch=2)
    alive_upper(p, t, k=0.4, period=1.6, slow=1.6)
    return T.stand(p)


NEW = {
    "turn_left": (turn_left, TURN_T, True, "Movimento", "girando no lugar para a esquerda: a cabeça vira primeiro, dois passos altos e rápidos"),
    "turn_right": (turn_right, TURN_T, True, "Movimento", "girando no lugar para a direita"),
    "lie_down": (lie_down, LIE_DOWN_T, False, "Descanso", "deita como avestruz: primeiro nos calcanhares, depois a barriga; pescoço em pé"),
    "get_up": (get_up, GET_UP_T, False, "Descanso", "levanta balançando para a frente com o pescoço, num impulso; sacode as penas"),
    "idle_tired": (idle_tired, IDLE_TIRED_T, True, "Parado", "cansado: bico aberto, a garganta vibra rápido, braços afastados do corpo"),
    "walk_tired": (walk_tired, WALK_TIRED_T, True, "Movimento", "andando cansado, pescoço baixo, bico aberto"),
    "kick_back": (kick_back, KICK_BACK_T, False, "Combate", "coice para trás: olha para trás com um olho e chuta para trás e para cima (golpe em 0,46 s)"),
}

REPLACED = {
    "idle": idle, "walk": walk, "run": run, "jink": jink, "attack": attack, "hurt": hurt,
    "sentinel": lively(A.sentinel, 0.3), "preen": lively(A.preen, 0.4), "wing_display": lively(A.wing_display, 0.4),
    "eat": lively(A.eat, 0.3), "graze": lively(A.graze, 0.3), "grit": lively(A.grit, 0.3), "sift": lively(A.sift, 0.3),
    "browse": lively(A.browse, 0.4), "beg": beg, "tame": lively(A.tame, 0.4),
}


def rebind(anims):
    out = {n: ((REPLACED[n],) + v[1:]) if n in REPLACED else v for n, v in anims.items()}
    for n, v in NEW.items():
        out.setdefault(n, v)
    return out
