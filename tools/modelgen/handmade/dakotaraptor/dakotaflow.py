"""Dakotaraptor: the fluid set (06/11/2026), in its own style. The techniques are the T. rex's (docs/estudos/08: nothing
stops, nothing switches, three beats, the chain follows late, the breath under everything); the body and the moves are
its own (docs/estudos/10, its study page "1.9"): a big dromaeosaurid of 5.5 m with long runner's legs, the great sickle
claws, a deep head on a two-bone neck, and big barred wings that open three ways (FLASH, MANTLE, SUN). It fights like
a hawk on the ground: it pounces, pins with a foot, and uses the WINGS in every exchange, to balance, to shield, to
look bigger, to cover. Where the Velociraptor is quick and twitchy (bird-head snaps, hops), this one is long and
flowing: the neck weaves like a heron's, the tail is a long rod with a feathered fan that sways late, its steps are
long and gliding.
"""
import math

from anim2 import add, Track, smooth, ease_in, ease_out, back_out, ground_fit
import dakotaanims as A

T, S = A.T, A.S
tr, window, wings, neck, f_ = A.tr, A.window, A.wings, A.neck, A.f_
FLASH, MANTLE, SUN = A.FLASH, A.MANTLE, A.SUN
SIDES = A.SIDES                    # (side, mirror sign)
PH = (("l", 0.0), ("r", 0.5))      # (side, gait phase)
TAILS = A.TAILS
BASE = A.BASE


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def tremor(t, f=(8.1, 12.7, 5.3), amp=(1.0, 0.55, 0.35), phase=0.0):
    return sum(a * math.sin(2 * math.pi * fr * t + phase * (i + 1) + 1.3 * i) for i, (fr, a) in enumerate(zip(f, amp)))


TAIL_GAIN = (0.7, 0.8, 0.9, 1.0, 1.15)    # a long feathered rod: the base leads, the fan at the end sways a little more


def trail(p, t, fn, delay=0.06, axis=1, loop=None, gain=TAIL_GAIN):
    for k, b in enumerate(TAILS):
        u = t - delay * (k + 1)
        u = u % loop if loop else max(0.0, u)
        r = [0.0, 0.0, 0.0]; r[axis] = fn(u) * gain[k]
        add(p, b, rot=tuple(r))


def alive_upper(p, t, k=1.0, period=2.0):
    neck(p, -0.7 * k * wave(t, period, -0.5))
    add(p, "skull", rot=(-0.4 * k * wave(t, period, -1.0), 0, 0))
    add(p, "jaw", rot=(-0.6 * k * max(0.0, wave(t, period, -0.7)), 0, 0))
    for s, sx in SIDES:
        add(p, f"arm_{s}", rot=(1.0 * k * wave(t, period, -0.9), 0, sx * 1.2 * k * wave(t, period, -1.1)))   # wings breathe out
    trail(p, t, lambda u: 0.6 * k * wave(u, period * 2, -0.6), delay=0.1, loop=period * 2)


def alive(p, t, k=1.0, period=2.0):
    br = wave(t, period)
    add(p, "body", rot=(0.7 * k * br, 0, 0), pos=(0, 0.25 * k * br, 0))
    alive_upper(p, t, k, period)
    return br


# ------------------------------------------------------------------ the gait: long gliding strides, the wings lag
def gait2(t, Tc, stride, duty, lift, bob, lean=0.0, drop=0.0, head=0.0, tail_up=0.0, roll=6.0, yaw=4.0, whip=1.0,
          wing=0.0, splay=2.5, stance_clear=-0.05):
    K = T.K
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}

    def landing(x):
        x %= 1.0
        return -1.0 + 2.0 * smooth(x / 0.3) if x < 0.3 else 1.0 - 2.0 * smooth((x - 0.3) / 0.7)
    b2 = landing(2 * ph + 0.06)
    hroll = roll * math.sin(w + 0.25)
    hyaw = yaw * math.sin(w - 0.6)
    add(p, "body", rot=(lean + 1.2 * b2, hyaw, hroll), pos=(0, K * (bob * b2 - 0.6 - drop), 0))
    # the heron's neck: it glides level while the hips rise and fall, a slow forward-back of the head on each step
    neck(p, head - lean * 0.6 - 1.4 * landing(2 * ph - 0.05) + 1.8 * math.sin(2 * w - 1.2), -0.9 * hyaw, -0.8 * hroll)
    add(p, "skull", rot=(head * 0.3 - lean * 0.4 + 1.0 * landing(2 * ph - 0.15) - 1.2 * math.sin(2 * w - 1.6), -0.15 * hyaw,
                         -0.2 * hroll))
    add(p, "jaw", rot=(-1.0 - 0.8 * max(0.0, landing(2 * ph - 0.2)), 0, 0))
    trail(p, t, lambda u: -whip * (2.0 + 0.8 * yaw) * math.sin(2 * math.pi * u / Tc - 1.0), delay=Tc * 0.05, loop=Tc)
    trail(p, t, lambda u: tail_up + 0.9 * landing(2 * u / Tc - 0.1), delay=Tc * 0.04, axis=0, loop=Tc)
    # the folded wings swing a little against the hips, late; opened for balance at speed
    if wing:
        wings(p, wing, 0.12 * math.sin(2 * w - 1.0))
    for s, sx in SIDES:
        add(p, f"arm_{s}", rot=(2.0 * math.sin(w + (0 if s == "l" else math.pi) - 2.4) + 1.2 * landing(2 * ph - 0.3), 0, sx * 1.5 * math.sin(w - 2.0)))
    for s, o in PH:
        sx = 1 if s == "l" else -1
        u = (ph + o) % 1.0
        swing = 0.0 if u < duty else math.sin(math.pi * (u - duty) / (1 - duty))
        add(p, f"thigh_{s}", rot=(0, -hyaw, -hroll + sx * splay * swing))
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0
            meta = 34 * smooth(max(0, (st - 0.55) / 0.45)); clear = stance_clear
            toe = 6 * (1 - smooth(min(1.0, st / 0.18))) + 8 * smooth(max(0, (st - 0.72) / 0.28))
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e
            ly = lift * math.sin(math.pi * min(1, sw * 1.15)) ** 1.3
            meta = 34 * (1 - smooth(sw / 0.5)) - 18 * math.sin(math.pi * sw)
            toe = 8 * (1 - smooth(sw / 0.15)) - 28 * math.sin(math.pi * min(1, sw * 1.1)) + 6 * smooth((sw - 0.7) / 0.3)
            clear = stance_clear + 1.25 * math.sin(math.pi * sw) ** 0.5     # ends where the stance begins: the seam closes
        T.plant(p, s, ly, dz - 6, meta, toe, clear)
    return p


# the game reads walk 1.3 s / 40 px, run 0.56 s / 68 px, stalk 1.911 s (Eudromaeosaur.WALK/RUN/STALK). 1.9.5: the run's
# stride 84 -> 68 px: at 84 the thigh hit its range and the knee flipped for part of the swing (a 96 deg snap of the foot)
def walk(t): return gait2(t, 1.3, 40, 0.6, 6, 1.0, roll=6.5, yaw=4.0)
def run(t): return gait2(t, 0.56, 68, 0.38, 11, 2.0, lean=6, drop=3, head=-4, tail_up=3, roll=3.0, yaw=2.5, whip=0.6, wing=0.25,
                         splay=1.5, stance_clear=0.2)


STALK_T = 1.3 * 1.47


def stalk(t):
    p = gait2(t, STALK_T, 40 * 0.78, 0.74, 6 * 0.78, 0.44, lean=3, drop=7, head=-9, tail_up=1, roll=3.0, yaw=2.0, whip=0.4)
    # the head weaves slowly side to side, low, the eyes fixed (a heron hunting), one weave per two steps
    neck(p, 0, 7 * math.sin(2 * math.pi * t / STALK_T), 0); add(p, "skull", rot=(0, -4 * math.sin(2 * math.pi * t / STALK_T - 0.5), 0))
    return p


# ------------------------------------------------------------------ idle: 8 s, the long body never quite still
IDLE_T = 8.0
LOOK = Track([(0, (0, 0)), (1.0, (0, 0)), (1.7, (4, 18), ease_out), (3.1, (3, 16)), (3.7, (-3, -12), ease_out), (5.2, (-2, -10)),
              (5.8, (6, 3), ease_out), (7.1, (5, 4)), (7.8, (0, 0), ease_in), (8.0, (0, 0))])


def idle(t):
    p = {}
    Ti = IDLE_T
    br = alive(p, t, k=1.0, period=Ti / 4)                    # a breath every 2 s
    shift = wave(t, Ti, 0.6) + 0.3 * wave(t, Ti / 2, 1.4)
    hroll = 1.8 + 2.0 * shift; hyaw = -1.5 + 1.3 * shift
    add(p, "body", rot=(0, hyaw, hroll), pos=(0, -0.2 * abs(shift), 0))
    lp, ly = LOOK(t)
    neck(p, 0.5 * lp + 1.0 * wave(t, Ti / 5, 0.2), -0.8 * hyaw + 0.5 * ly, -0.7 * hroll)
    add(p, "skull", rot=(0.6 * lp + 0.6 * wave(t, Ti / 5, 1.4), 0.5 * ly, -0.15 * ly))
    # the tail fan: a slow S from the base out, and a lift of the fan now and then
    trail(p, t, lambda u: 2.5 * wave(u, Ti, -0.8) + 1.0 * wave(u, Ti / 2, 0.6) - 1.2 * hyaw, delay=0.14, loop=Ti)
    trail(p, t, lambda u: 0.6 * wave(u, Ti / 4, -0.4), delay=0.1, axis=0, loop=Ti)
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, -hyaw, -hroll))
    T.plant(p, "l")
    T.plant(p, "r", 0.0, -3.0)
    return p


# ------------------------------------------------------------------ voice, made fluid
def call(t):
    """a rolling coo with the throat working and the neck rising, the wings shrugging once"""
    p = {}
    k = f_(tr((0, 0), (0.5, 1, ease_out), (2.0, 1), (2.6, 0, ease_in)), t)
    env = window(t, 0.45, 2.05, 0.25)
    hum = tremor(t, (10.3, 14.9, 7.3), (0.8, 0.45, 0.3)) * env
    add(p, "body", rot=(2 * k + 0.3 * hum, 0, 0))
    neck(p, 10 * k + 0.6 * hum); add(p, "skull", rot=(-8 * k - 0.6 * hum, 0, 0)); add(p, "jaw", rot=(-2 * env - 0.6 * hum, 0, 0))
    wings(p, 0.15 * math.exp(-((t - 1.2) / 0.25) ** 2))
    trail(p, t, lambda u: 2.0 * math.exp(-((u - 1.3) / 0.4) ** 2), delay=0.08)
    alive(p, t, k=1.0 - 0.6 * k)
    return T.stand(p)


def threat(t):
    """the warning: head low and weaving, the jaws open with a hiss that trembles, the wings lifted from the flanks, a
    scrape of one foot"""
    p = {}
    k = f_(tr((0, 0), (0.4, 1, ease_out), (2.0, 1), (2.4, 0, ease_in)), t)
    scrape = f_(tr((0, 0), (0.6, 0), (0.95, 1, ease_out), (1.2, 0, ease_in), (2.4, 0)), t)
    hiss = tremor(t, (9.7, 13.9, 6.3)) * window(t, 0.35, 2.0, 0.2)
    add(p, "body", rot=(5 * k, 0, -2 * scrape), pos=(0, -2 * k, 0))
    neck(p, -10 * k + 0.6 * hiss, 8 * k * math.sin(2 * math.pi * t / 1.2), 0); add(p, "skull", rot=(-2 * k + 0.8 * hiss, -4 * k * math.sin(2 * math.pi * t / 1.2 - 0.6), 0))
    add(p, "jaw", rot=(-18 * k - 1.6 * hiss, 0, 0))
    wings(p, 0.35 * k, 0.05 * hiss)
    trail(p, t, lambda u: 5 * f_(tr((0, 0), (0.4, 1, ease_out), (2.0, 1), (2.4, 0, ease_in)), u) * math.sin(2 * math.pi * u / 0.8), delay=0.06)
    alive_upper(p, t, k=0.5)
    T.plant(p, "r"); T.plant(p, "l", 5 * scrape, 3 * scrape, 0, -10 * scrape)
    return p


# ------------------------------------------------------------------ the bites, three beats
def attack(t):
    """the quick bite (0.9 s): the head drawn back on the S of the neck, a strike, a pull back with a snap, the wings flick"""
    p = {}
    n = tr((0, (0, 0)), (0.16, (10, 4), ease_out), (0.28, (-16, 0), ease_in), (0.45, (-11, 0)), (0.9, (0, 0), back_out))(t)
    j = f_(tr((0, 0), (0.15, -30, ease_out), (0.28, -2, ease_in), (0.5, -4), (0.9, 0, ease_out)), t)
    push = f_(tr((0, 0), (0.15, 1.2, ease_out), (0.28, -3.5, ease_in), (0.5, -2.8), (0.9, 0, back_out)), t)
    add(p, "body", rot=(-0.25 * n[0], 0.3 * n[1], 0), pos=(0, 0, T.K * push))
    neck(p, n[0], n[1], 0); add(p, "skull", rot=(0.5 * n[0], 0.5 * n[1], 0)); add(p, "jaw", rot=(j, 0, 0))
    wings(p, 0.2 * math.exp(-((t - 0.3) / 0.12) ** 2), 0.2 * math.exp(-((t - 0.3) / 0.1) ** 2))
    trail(p, t, lambda u: -0.4 * tr((0, (0, 0)), (0.16, (10, 4), ease_out), (0.28, (-16, 0), ease_in), (0.45, (-11, 0)), (0.9, (0, 0), back_out))(u)[1] + 1.5 * math.exp(-((u - 0.3) / 0.1) ** 2), delay=0.05)
    alive(p, t, k=0.5)
    return T.stand(p)


BITE_T = 2.0


def bite(t):
    """the hold-and-tear bite of a raptor: strike, then the head pulls up and back in jerks, the wings beating once"""
    p = {}
    pt = f_(tr((0, 0), (0.3, 10, ease_out), (0.45, -16, ease_in), (0.6, -12), (1.5, -8), (2.0, 0, back_out)), t)
    tears = sum(a * math.exp(-((t - c) / 0.08) ** 2) for c, a in ((0.85, 1.0), (1.1, 0.75), (1.35, 0.5)))
    j = f_(tr((0, 0), (0.3, -34, ease_out), (0.45, -2, ease_in), (1.5, -3), (1.7, -14, ease_out), (2.0, 0)), t)
    add(p, "body", rot=(-0.3 * pt - 3 * tears, 0, 0), pos=(0, 0, T.K * (-2.5 * window(t, 0.35, 1.5, 0.2) + 1.0 * tears)))
    neck(p, pt + 9 * tears, 4 * tears, 0); add(p, "skull", rot=(0.5 * pt + 5 * tears, 0, -6 * tears)); add(p, "jaw", rot=(j, 0, 0))
    wings(p, 0.3 * window(t, 0.6, 1.5, 0.3), 0.4 * tears, how=MANTLE)
    trail(p, t, lambda u: 3 * sum(a * math.exp(-((u - c) / 0.1) ** 2) for c, a in ((0.85, 1.0), (1.1, -0.75), (1.35, 0.5))), delay=0.06)
    alive(p, t, k=0.5)
    return T.stand(p)


def hurt(t):
    p = {}; e = math.exp(-(t / 0.15)) * smooth(t / 0.04)
    add(p, "body", rot=(-6 * e, 6 * e, -4 * e), pos=(0, -1.2 * e, 2.5 * e))
    neck(p, 12 * e, -8 * e, 0); add(p, "skull", rot=(8 * e, -6 * e, 6 * e)); add(p, "jaw", rot=(-22 * e, 0, 0))
    ew = math.exp(-max(0.0, t - 0.08) / 0.25) * smooth(t / 0.12)        # the wings jerk out a little slower than the head
    wings(p, 0.22 * ew, 0.2 * ew, how=MANTLE)
    trail(p, t, lambda u: -7 * math.exp(-(u / 0.2)) * smooth(u / 0.05), delay=0.04)
    alive(p, t, k=0.4)
    return T.stand(p)


# ------------------------------------------------------------------ the duel set, the Dakotaraptor's way: the wings fight too
GUARD_T = 2.4


def guard(t):
    """a hawk over the ground: crouched, the wings half spread low and forward (mantled at the rival, to look bigger),
    the tail fan raised and quivering, the long neck drawn back in an S and the head weaving slowly, ready to strike or
    to leap"""
    p = {}
    Tg = GUARD_T
    rock = wave(t, Tg)
    hiss = tremor(t, (19 / Tg, 29 / Tg, 13 / Tg), (0.8, 0.45, 0.3))
    add(p, "body", rot=(7 + 1.0 * rock, 1.0 * wave(t, Tg, 1.0), 1.2 * wave(t, Tg / 2, 0.4)), pos=(0, T.K * (-3.0 + 0.4 * rock), 0))
    neck(p, 12 - 1.5 * rock + 0.4 * hiss, 6 * wave(t, Tg, 0.9), 0)     # drawn back: the S, cocked
    add(p, "skull", rot=(-14 + 0.6 * hiss, -4 * wave(t, Tg, 0.3), 2 * wave(t, Tg, 1.4)))
    add(p, "jaw", rot=(-8 - 3 * max(0.0, wave(t, Tg / 2, -0.4)) - 1.2 * hiss, 0, 0))
    wings(p, 0.45 + 0.04 * wave(t, Tg / 2, 0.7), 0.04 * hiss, how=MANTLE)
    trail(p, t, lambda u: 2.5 * wave(u, Tg, -0.5) + 0.4 * tremor(u, (21 / Tg, 32 / Tg, 15 / Tg)), delay=0.08, loop=Tg)
    trail(p, t, lambda u: -5.0 + 0.8 * wave(u, Tg / 2, -0.7), delay=0.06, axis=0, loop=Tg)
    for s, sx in SIDES:
        add(p, f"thigh_{s}", rot=(0, 0, 2.5 * sx - 0.8 * wave(t, Tg, 0.4)))
    # the right foot forward, its sickle lifting and lowering (the toes pitched up), the left back to push
    T.plant(p, "l", 0.0, 3.0)
    T.plant(p, "r", 0.0, -4.0, 0, -8 - 6 * max(0.0, wave(t, Tg, 1.2)))
    return p


STRAFE_T = 1.6


def strafe(t, side):
    """a long sideways glide with crossing steps, the outer wing opened and dipped like a hawk banking on the ground,
    the inner one folded; the head and neck stay on the rival while the body slides past under them"""
    d = 1.0 if side == "left" else -1.0
    ph = (t / STRAFE_T) % 1.0; w = 2 * math.pi * ph; p = {}
    add(p, "body", rot=(6, 0, -4.0 * d + 1.5 * math.sin(2 * w)), pos=(T.K * 1.2 * d * math.sin(2 * w), T.K * (-2.6 + 0.5 * math.cos(2 * w)), 0))
    neck(p, 6, -2.0 * d, 4.0 * d - 1.5 * math.sin(2 * w)); add(p, "skull", rot=(-8, 0, 0.8 * d))
    add(p, "jaw", rot=(-6 - 1.0 * tremor(t, (13 / STRAFE_T, 19 / STRAFE_T, 8 / STRAFE_T), (0.7, 0.4, 0.3)), 0, 0))
    # the wing on the far side of the travel opens and dips for balance, the near one stays half folded
    out = "r" if d > 0 else "l"; inn = "l" if d > 0 else "r"
    for s, sx in SIDES:
        k = 0.7 + 0.06 * math.sin(2 * w - 1.0) if s == out else 0.15
        (ax, ay, az), fx, hx = FLASH
        add(p, f"arm_{s}", rot=(ax * k, ay * k * sx, (az * k - 12 * k * math.sin(2 * w - 1.2)) * sx))
        add(p, f"forearm_{s}", rot=(fx * k, 0, 0)); add(p, f"hand_{s}", rot=(hx * k, 0, 0))
    trail(p, t, lambda u: -d * 5.0 - 2.0 * math.sin(2 * math.pi * u / STRAFE_T - 0.9), delay=0.08, loop=STRAFE_T)
    for s, o in PH:
        sx = 1 if s == "l" else -1
        u = (ph + o) % 1.0
        if u < 0.42:
            sw = u / 0.42
            add(p, f"thigh_{s}", rot=(0, 0, d * 10.0 * (sw - 0.5) + 2.5 * sx))
            T.plant(p, s, 5.0 * math.sin(math.pi * sw) ** 1.2, 0.0, 10 * math.sin(math.pi * sw), -18 * math.sin(math.pi * sw),
                    clear=0.8 * math.sin(math.pi * sw) ** 0.5)
        else:
            st = (u - 0.42) / 0.58
            add(p, f"thigh_{s}", rot=(0, 0, -d * 10.0 * (st - 0.5) + 2.5 * sx))
            T.plant(p, s)
    return p


def strafe_left(t): return strafe(t, "left")
def strafe_right(t): return strafe(t, "right")


TURN_T = 1.3


def turn(t, side):
    """it steps round with long slow steps; the long neck swings into the turn first in a curve (+ yaw is to the
    animal's right in game: a left turn leads with - yaw), the outer wing lifts a little off the flank, the tail fan
    sweeps out the other way and arrives last"""
    d = 1.0 if side == "left" else -1.0
    lead = -d
    ph = (t / TURN_T) % 1.0; w = 2 * math.pi * ph; p = {}
    add(p, "body", rot=(0, lead * (4.0 + 1.5 * math.sin(w)), 2.5 * math.sin(w + 0.3)), pos=(0, T.K * (-0.8 + 0.5 * math.cos(2 * w)), 0))
    neck(p, -1.0, lead * (16.0 + 2.5 * math.sin(w - 0.6)), lead * 3.0)
    add(p, "skull", rot=(0, lead * (6.0 + 1.5 * math.sin(w - 1.2)), -lead * 4.0))
    out = "r" if lead < 0 else "l"
    wings(p, 0.0)
    sx = 1 if out == "l" else -1
    add(p, f"arm_{out}", rot=(6, 0, sx * (10 + 3 * math.sin(w - 1.0))))
    trail(p, t, lambda u: -lead * 6.0 - 2.5 * math.sin(2 * math.pi * u / TURN_T - 0.8), delay=0.1, loop=TURN_T)
    alive_upper(p, t, k=0.6, period=TURN_T / 2)
    for s, o in PH:
        u = (ph + o) % 1.0
        if u < 0.4:
            sw = u / 0.4
            ly = 6.0 * math.sin(math.pi * sw) ** 1.2
            dz = -3.0 * math.cos(math.pi * sw)
            toe = -20 * math.sin(math.pi * sw); meta = 12 * math.sin(math.pi * sw); clear = 1.0 * math.sin(math.pi * sw) ** 0.5
            add(p, f"thigh_{s}", rot=(0, lead * 6.0 * math.sin(math.pi * sw), 0))
        else:
            ly, dz, toe, meta, clear = 0.0, 3.0 - 6.0 * ((u - 0.4) / 0.6), 0.0, 0.0, -0.05
        add(p, f"thigh_{s}", rot=(0, -lead * 4.0, -2.5 * math.sin(w + 0.3)))
        T.plant(p, s, ly, dz, meta, toe, clear)
    return p


def turn_left(t): return turn(t, "left")
def turn_right(t): return turn(t, "right")


FEINT_T = 1.3


def feint(t):
    """the half flash: the wings snap half open and the tail fan up as it rocks forward on the toes with the sickle foot
    lifting, as if to pounce; it stops, the wings close and it settles back"""
    p = {}
    k = f_(tr((0, 0), (0.18, 0.3, ease_out), (0.38, 1, ease_out), (0.6, 0.85), (0.95, 0.1, ease_in), (1.3, 0, ease_out)), t)
    rock = f_(tr((0, 0), (0.18, -0.4, ease_out), (0.42, 1, ease_out), (0.62, 0.7), (1.0, -0.15, ease_in), (1.3, 0, back_out)), t)
    add(p, "body", rot=(5 * rock, 0, 0), pos=(0, T.K * (-1.5 * abs(rock) + 0.8 * k), T.K * -3.0 * rock))
    neck(p, -10 * rock, 0, 0); add(p, "skull", rot=(-4 * rock, 0, 0))
    add(p, "jaw", rot=(-24 * k - 1.2 * tremor(t) * k, 0, 0))
    wings(p, 0.55 * k, 0.15 * k * math.sin(2 * math.pi * t / 0.15))
    trail(p, t, lambda u: -8 * f_(tr((0, 0), (0.18, 0.3, ease_out), (0.38, 1, ease_out), (0.6, 0.85), (0.95, 0.1, ease_in), (1.3, 0, ease_out)), u), delay=0.05, axis=0)
    alive_upper(p, t, k=0.4)
    T.plant(p, "l")
    lift = max(0.0, rock)
    T.plant(p, "r", 6 * lift, -3 * lift, -8 * lift, -30 * lift)
    return p


BLOCK_T = 0.9


def block(t):
    """the wings as a shield: both thrown forward and up in front of the chest, the body rearing back from the blow,
    then folded down again"""
    p = {}
    e = math.exp(-max(0.0, t - 0.08) / 0.3) * smooth(t / 0.08)
    add(p, "body", rot=(-7 * e, 3 * e, 2 * e), pos=(0, T.K * 0.5 * e, T.K * 2.0 * e))
    neck(p, 14 * e, 6 * e, 0); add(p, "skull", rot=(6 * e, 4 * e, 6 * e)); add(p, "jaw", rot=(-12 * e, 0, 0))
    ew = math.exp(-max(0.0, t - 0.2) / 0.3) * smooth(t / 0.2)        # the big wings take four frames to come round
    wings(p, 0.6 * ew, 0.15 * ew * math.sin(2 * math.pi * 6 * t), how=MANTLE)
    trail(p, t, lambda u: 6 * math.exp(-max(0.0, u - 0.08) / 0.3) * smooth(u / 0.08), delay=0.05, axis=0)
    alive_upper(p, t, k=0.4)
    return T.stand(p)


RECOIL_T = 1.1


def recoil(t):
    """its blow met the wings: the head knocked up and aside, two quick beats of the wings to keep its feet, a long
    step back"""
    p = {}
    e = math.exp(-max(0.0, t - 0.05) / 0.25) * smooth(t / 0.05)
    beats = sum(math.exp(-((t - c) / 0.07) ** 2) for c in (0.2, 0.42))
    add(p, "body", rot=(-5 * e, -5 * e, 3 * e), pos=(0, 0, T.K * 2.5 * e))
    neck(p, 10 * e, -14 * e, -4 * e); add(p, "skull", rot=(6 * e, -8 * e, -8 * e)); add(p, "jaw", rot=(-14 * e, 0, 0))
    ew = math.exp(-max(0.0, t - 0.2) / 0.3) * smooth(t / 0.2)
    wings(p, 0.35 * ew + 0.1 * beats, 0.5 * beats, how=MANTLE)
    trail(p, t, lambda u: 7 * math.exp(-max(0.0, u - 0.05) / 0.3) * smooth(u / 0.05), delay=0.05)
    alive_upper(p, t, k=0.4)
    T.plant(p, "l")
    s = math.sin(math.pi * min(1.0, max(0.0, (t - 0.12) / 0.5)))
    T.plant(p, "r", 6 * s ** 2, 5 * smooth((t - 0.12) / 0.5) * (1 - smooth((t - 0.65) / 0.4)), 0, -12 * s)
    return p


SUBMIT_T = 2.4


def submit(t):
    """it gives in: crouches low, the wings fold tight and flat to the flanks, the tail fan comes down and closes, the
    head drops below the shoulders and turns away, and it backs off sideways"""
    p = {}
    k = f_(tr((0, 0), (0.6, 1, ease_out), (2.4, 1)), t)
    turn_ = f_(tr((0, 0), (0.8, 0), (1.6, 1, ease_out), (2.4, 1)), t)
    whine = math.exp(-((t - 0.9) / 0.14) ** 2)
    add(p, "body", rot=(5 * k, 14 * turn_, -3 * turn_), pos=(0, T.K * -4.0 * k, 0))
    neck(p, -24 * k, 14 * turn_, 0); add(p, "skull", rot=(-4 * k, 6 * turn_, 6 * k)); add(p, "jaw", rot=(-2 - 6 * whine, 0, 0))
    for s, sx in SIDES:
        add(p, f"arm_{s}", rot=(-6 * k, 0, -sx * 4 * k))
    trail(p, t, lambda u: -6 * f_(tr((0, 0), (0.6, 1, ease_out), (2.4, 1)), u), delay=0.08, axis=0)
    trail(p, t, lambda u: -5 * f_(tr((0, 0), (0.8, 0), (1.6, 1, ease_out), (2.4, 1)), u), delay=0.1)
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, -14 * turn_, 0))
    alive_upper(p, t, k=0.8)
    return T.stand(p)


# ------------------------------------------------------------------ rest transitions and tiredness
LIE_DOWN_T = 2.0


def lie_down(t):
    """it folds down like a big bird settling on a nest: the legs fold, the keel sinks, the wings shuffle and settle
    over the flanks, the tail fan last"""
    p = {}
    k = f_(tr((0, 0), (0.25, 0.04), (1.3, 0.93, ease_in), (1.5, 1.03), (2.0, 1.0, ease_out)), t)
    look = f_(tr((0, 0), (0.35, 1, ease_out), (1.3, 1), (2.0, 0, ease_out)), t)
    T.lie(p, k)
    neck(p, -8 * look, 0, 0); add(p, "skull", rot=(-4 * look, 0, 0))
    shuffle = math.exp(-((t - 1.55) / 0.12) ** 2)
    wings(p, 0.15 * shuffle, 0.4 * shuffle * math.sin(2 * math.pi * 7 * t))
    trail(p, t, lambda u: 3.0 * math.exp(-((u - 1.45) / 0.15) ** 2), delay=0.07, axis=0)
    alive_upper(p, t, k=0.5)
    return ground_fit(S, p)


GET_UP_T = 1.8


def get_up(t):
    """the head swings forward and the wings half open to lift it, the legs push it up, a shake of the feathers"""
    p = {}
    k = f_(tr((0, 1.0), (0.35, 1.02), (1.15, 0.04, ease_out), (1.35, -0.02), (1.8, 0.0, ease_out)), t)
    push = math.exp(-((t - 0.55) / 0.2) ** 2)
    T.lie(p, max(0.0, k))
    neck(p, -14 * push, 0, 0); add(p, "skull", rot=(-6 * push, 0, 0))
    wings(p, 0.35 * push, 0.2 * push)
    ruff = math.exp(-((t - 1.5) / 0.14) ** 2) * math.sin(2 * math.pi * 7 * (t - 1.5))
    neck(p, 0, 2 * ruff, 6 * ruff); add(p, "skull", rot=(0, 3 * ruff, 8 * ruff))
    trail(p, t, lambda u: 3.0 * math.exp(-((u - 1.55) / 0.15) ** 2) * math.sin(2 * math.pi * 7 * (u - 1.5)), delay=0.05)
    alive_upper(p, t, k=0.5)
    return ground_fit(S, p)


IDLE_TIRED_T = 3.0


def idle_tired(t):
    """spent: the wings hang half open off the flanks to shed the heat, the mouth open, the throat fluttering fast (a
    bird's gular flutter on top of the panting), the head and tail low"""
    p = {}
    Ti = IDLE_TIRED_T
    pant = wave(t, Ti / 5)
    flutter = wave(t, Ti / 20)
    add(p, "body", rot=(3 + 1.6 * pant, 0, 0.8 * wave(t, Ti, 0.4)), pos=(0, T.K * (-1.4 + 0.5 * pant), 0))
    neck(p, -12 - 1.6 * wave(t, Ti / 5, -0.6), 2 * wave(t, Ti, 0.5), 0)
    add(p, "skull", rot=(-3 - 1.0 * wave(t, Ti / 5, -1.2) + 0.4 * flutter, 1.5 * wave(t, Ti, -0.5), 0))
    add(p, "jaw", rot=(-14 - 5 * max(0.0, wave(t, Ti / 5, -0.4)) - 1.0 * flutter, 0, 0))
    wings(p, 0.3 + 0.03 * wave(t, Ti / 5, -0.8), how=SUN)
    trail(p, t, lambda u: 1.5 * wave(u, Ti, -0.8), delay=0.1, loop=Ti)
    trail(p, t, lambda u: -3 + 0.5 * wave(u, Ti / 5, -0.5), delay=0.06, axis=0, loop=Ti)
    return T.stand(p)


WALK_TIRED_T = 1.6


def walk_tired(t):
    p = gait2(t, WALK_TIRED_T, 32, 0.64, 4.5, 1.3, lean=2, drop=1.5, head=-10, tail_up=-2, roll=7.0, yaw=3.5, whip=0.8)
    add(p, "jaw", rot=(-12 - 5 * max(0.0, wave(t, WALK_TIRED_T / 2)), 0, 0))
    neck(p, -1.4 * wave(t, WALK_TIRED_T / 2, -0.5), 0, 0)
    wings(p, 0.15, how=SUN)
    return p


# ------------------------------------------------------------------ its own, made fluid (same moves, breath and trailing tail)
def _upper(fn, k=0.5):
    def g(t):
        p = fn(t); alive_upper(p, t, k=k); return p
    g.__name__ = fn.__name__; g.__doc__ = fn.__doc__
    return g


pounce = A.pounce          # airborne, its own; it already has its three beats
def wing_flash(t):
    """the wings thrown open, the tail fan raised, a hiss with the jaws open; then folded (06/11: the opening takes 0.28 s
    instead of 0.12 with an overshoot, which turned the hand 185 deg in one frame; still a sudden flash, now readable)"""
    p = {}
    k = f_(tr((0, 0), (0.28, 1, smooth), (0.38, 1.03), (1.0, 1), (1.4, 0, ease_in)), t)
    add(p, "body", rot=(6 * k, 0, 0), pos=(0, 1 * k, 0))
    neck(p, 10 * k, 0)
    hiss = tremor(t, (11.3, 15.9, 7.7)) * window(t, 0.15, 1.1, 0.12)
    add(p, "jaw", rot=(-22 * k - 1.5 * hiss, 0, 0))
    wings(p, k, 0.06 * hiss * k)
    trail(p, t, lambda u: -10 * f_(tr((0, 0), (0.28, 1, smooth), (0.38, 1.03), (1.0, 1), (1.4, 0, ease_in)), u), delay=0.04, axis=0)
    alive_upper(p, t, k=0.4)
    return T.stand(p)


pin, mantle, sun, preen = _upper(A.pin, 0.4), _upper(A.mantle, 0.5), _upper(A.sun), _upper(A.preen, 0.4)
sniff, look_back, shake, stretch, yawn, eat, drink, tame = (_upper(BASE[n][0], 0.5) for n in
                                                            ("sniff", "look_back", "shake", "stretch", "yawn", "eat", "drink", "tame"))
