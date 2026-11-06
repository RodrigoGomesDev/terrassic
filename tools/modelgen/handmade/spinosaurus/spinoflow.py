"""Spinosaurus: the fluid set (06/11/2026), in its own style. The techniques come from the T. rex (docs/estudos/08:
nothing stops, nothing switches, three beats, the chain follows late, the breath under everything); the body and the
fighting from its own study (docs/estudos/10): a semi-aquatic hunter (Ibrahim et al. 2020) with short hind legs, a long
two-bone neck and a crocodile's snout (narrow jaws, built to snap sideways at fish, not to crush), big arms with hooked
thumb claws (Charig & Milner 1997, Baryonyx) and the great sail, a display (it shows it broadside before a fight).

So, unlike the T. rex: it does not rear and bite down; it SNAPS SIDEWAYS like a crocodile and shakes, DARTS the snout
like a heron, and HOOKS with the thumb claws; its guard holds the arms up like hooks and the snout aimed like a spear;
it parries with the forearm; it fights side-on, showing the sail. Heavy: the steps are slow and short, and the SAIL
(on the hip bone, "body") sways late and wide, carried on after the hips by its own weight.
"""
import math

from anim2 import add, Track, smooth, ease_in, ease_out, back_out, ground_fit
import spinoanims as A

T, S = A.T, A.S
tr, window, W = A.tr, A.window, A.W
TAILS = A.TAILS
PH = (("l", 0.0), ("r", 0.5))
MS = (("l", 1), ("r", -1))

_BASE = {n: v[0] for n, v in A.ANIMS.items()}


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def tremor(t, f=(6.1, 9.7, 4.1), amp=(1.0, 0.55, 0.35), phase=0.0):
    return sum(a * math.sin(2 * math.pi * fr * t + phase * (i + 1) + 1.3 * i) for i, (fr, a) in enumerate(zip(f, amp)))


TAIL_GAIN = (0.5, 0.9, 1.4, 2.0, 2.7)    # the paddle tail: supple, the swing grows a lot to the tip (a swimmer's tail)


def trail(p, t, fn, delay=0.08, axis=1, loop=None, gain=TAIL_GAIN):
    for k, b in enumerate(TAILS):
        u = t - delay * (k + 1)
        u = u % loop if loop else max(0.0, u)
        r = [0.0, 0.0, 0.0]; r[axis] = fn(u) * gain[k]
        add(p, b, rot=tuple(r))


def neck(p, pitch=0.0, yaw=0.0, roll=0.0):
    T.neck(p, (pitch, yaw, roll))


def arms(p, arm=0.0, fore=0.0, hand=0.0, side=None, spread=0.0):
    for s, sx in MS:
        if side and s != side: continue
        add(p, f"arm_{s}", rot=(arm, 0, sx * spread)); add(p, f"forearm_{s}", rot=(fore, 0, 0)); add(p, f"hand_{s}", rot=(hand, 0, 0))


def alive_upper(p, t, k=1.0, period=3.6):
    neck(p, -0.7 * k * wave(t, period, -0.5))
    add(p, "skull", rot=(-0.4 * k * wave(t, period, -1.0), 0, 0))
    add(p, "jaw", rot=(-0.4 * k * max(0.0, wave(t, period, -0.7)), 0, 0))
    for s, o in PH:
        add(p, f"arm_{s}", rot=(1.4 * k * wave(t, period, -0.8 - 3 * o), 0, 0))
        add(p, f"hand_{s}", rot=(2.0 * k * wave(t, period, -1.6 - 3 * o), 0, 0))     # the claws curl and open
    trail(p, t, lambda u: 0.8 * k * wave(u, period * 2, -0.6), delay=0.12, loop=period * 2)


def alive(p, t, k=1.0, period=3.6):
    """the breath: slow and deep, the sail rising and settling with it"""
    br = wave(t, period)
    add(p, "body", rot=(0.6 * k * br, 0, 0.3 * k * wave(t, period * 2, -0.9)), pos=(0, 0.4 * k * br * T.K, 0))
    alive_upper(p, t, k, period)
    return br


# ------------------------------------------------------------------ the gait: heavy, short legs, the sail sways late
def gait2(t, Tc, stride, duty, lift, bob, lean=0.0, drop=0.0, head=0.0, tail_up=0.0, roll=7.0, yaw=4.0, whip=1.0,
          lag=0.9, arm_sw=4.0, splay=3.0, stance_clear=-0.05):
    K = T.K
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}

    def landing(x):
        x %= 1.0
        return -1.0 + 2.0 * smooth(x / 0.32) if x < 0.32 else 1.0 - 2.0 * smooth((x - 0.32) / 0.68)
    b2 = landing(2 * ph + 0.08)
    # the sail is on the hip bone: its roll comes LATE (lag) and wide, the weight of the sail carrying on past the step
    hroll = roll * math.sin(w + 0.25 - lag)
    hyaw = yaw * math.sin(w - 0.6)
    add(p, "body", rot=(lean + 1.0 * b2, hyaw, hroll), pos=(0, K * (bob * b2 - 0.6 - drop), 0))
    # the long neck carries the snout level and low, steadied against the sway, a beat behind
    neck(p, head - lean * 0.6 - 1.2 * landing(2 * ph - 0.06), -0.85 * hyaw - 1.5 * math.sin(w - 1.5), -0.8 * hroll)
    add(p, "skull", rot=(head * 0.3 - lean * 0.3 + 0.9 * landing(2 * ph - 0.15), -0.15 * hyaw + 1.0 * math.sin(w - 2.1), -0.2 * hroll))
    add(p, "jaw", rot=(-0.8 - 0.6 * max(0.0, landing(2 * ph - 0.2)), 0, 0))
    trail(p, t, lambda u: -whip * (1.6 + 0.4 * yaw) * math.sin(2 * math.pi * u / Tc - 1.0), delay=Tc * 0.045, loop=Tc)
    trail(p, t, lambda u: tail_up + 0.7 * landing(2 * u / Tc - 0.1), delay=Tc * 0.04, axis=0, loop=Tc, gain=(0.6, 0.7, 0.8, 0.9, 1.0))
    for s, o in PH:
        f = w + o * 2 * math.pi
        add(p, f"arm_{s}", rot=(arm_sw * math.sin(f - 2.3) + 1.5 * landing(2 * ph - 0.25), 0, 0))
        add(p, f"forearm_{s}", rot=(arm_sw * 1.1 * math.sin(f - 3.0), 0, 0))
        add(p, f"hand_{s}", rot=(arm_sw * 1.2 * math.sin(f - 3.6), 0, 0))
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


# the game reads walk 2.0 s / 62 px, run 0.85 s / 108 px, stalk 2.94 s (Spinosaur.WALK/RUN/STALK): kept
def walk(t): return gait2(t, 2.0, 62, 0.62, 8, 1.4)
def run(t): return gait2(t, 0.85, 108, 0.42, 14, 2.6, lean=6, drop=3, head=-4, tail_up=3, roll=4.0, yaw=2.5, whip=0.7, lag=0.7,
                         arm_sw=2.5, splay=2.0, stance_clear=0.2)


STALK_T = 2.0 * 1.47


def stalk(t):
    """the heron: the head held low and dead still in space while the body creeps under it"""
    p = gait2(t, STALK_T, 62 * 0.78, 0.74, 8 * 0.78, 0.6, lean=3, drop=7, head=-12, tail_up=1, roll=4.0, yaw=2.0, whip=0.5,
              lag=1.0, arm_sw=1.5, splay=1.5)
    add(p, "jaw", rot=(1, 0, 0))
    return p


# ------------------------------------------------------------------ idle: 8 s, the sail rocking slowly
IDLE_T = 8.0
LOOK = Track([(0, (0, 0)), (1.3, (0, 0)), (2.0, (-4, 14), ease_out), (3.4, (-3, 12)), (4.0, (-8, -6), ease_out), (5.4, (-7, -5)),
              (6.0, (2, -12), ease_out), (7.2, (2, -10)), (7.8, (0, 0), ease_in), (8.0, (0, 0))])


def idle(t):
    p = {}
    Ti = IDLE_T
    alive(p, t, k=1.0, period=Ti / 2)                       # a slow breath every 4 s
    shift = wave(t, Ti, 0.5) + 0.3 * wave(t, Ti / 2, 1.3)
    sail = wave(t, Ti, -0.5) + 0.25 * wave(t, Ti / 4, 0.8)    # the sail rocks a little behind the weight
    hroll = 1.6 + 1.8 * shift + 1.2 * sail; hyaw = -1.5 + 1.3 * shift
    add(p, "body", rot=(0, hyaw, hroll), pos=(0, -0.25 * abs(shift) * T.K, 0))
    lp, ly = LOOK(t)
    # head low and still like a fisher, looking down at the water now and then (the LOOK dips)
    neck(p, -2 + 0.5 * lp + 0.8 * wave(t, Ti / 5, 0.3), -0.8 * hyaw + 0.5 * ly, -0.7 * hroll)
    add(p, "skull", rot=(0.6 * lp + 0.5 * wave(t, Ti / 5, 1.5), 0.45 * ly, -0.12 * ly))
    # the claws: the thumbs flex slowly, out of step with each other
    for s, o in PH:
        add(p, f"hand_{s}", rot=(3.0 * wave(t, Ti / 2, -1.0 - 3 * o), 0, 0))
    trail(p, t, lambda u: 1.6 * wave(u, Ti, -0.8) + 0.6 * wave(u, Ti / 2, 0.6) - 0.8 * hyaw, delay=0.16, loop=Ti)
    for s, _ in PH:
        add(p, f"thigh_{s}", rot=(0, -hyaw, -hroll))
    T.plant(p, "l")
    T.plant(p, "r", 0.0, -3.0)
    return p


# ------------------------------------------------------------------ voice
ROAR_T = 3.4


def roar(t):
    """not a T. rex's roar: the long snout lifts at a slant, the narrow jaws open in a hissing bellow that shivers
    through the throat, the head sways side to side with the sail rolling after it"""
    p = {}
    up = f_(tr((0, 0), (0.5, -0.3, ease_out), (0.95, 1, ease_out), (2.5, 0.9), (3.0, 0.1, ease_in), (3.4, 0)), t)
    a = max(0.0, up); c = max(0.0, -up) / 0.3
    env = window(t, 0.95, 2.6, 0.25)
    shiv = tremor(t) * env
    sw = f_(tr((0, 0), (1.0, 0), (1.6, 1, ease_out), (2.2, -1), (2.6, -0.3), (3.4, 0)), t)
    swl = f_(tr((0, 0), (1.2, 0), (1.85, 1, ease_out), (2.45, -1), (2.85, -0.3), (3.4, 0)), t)       # the sail, late
    add(p, "body", rot=(-4 * a + 4 * c + 0.3 * shiv, 1.5 * sw, 3.0 * swl), pos=(0, T.K * (-1.5 * c + 0.6 * a), 0))
    neck(p, 18 * a - 8 * c + 0.8 * shiv, 10 * sw, -2 * sw)
    add(p, "skull", rot=(8 * a - 5 * c + 1.1 * tremor(t, (7.9, 11.3, 5.1), phase=0.7) * env, 5 * sw, -4 * sw))
    jaw = f_(tr((0, 0), (0.5, -2), (1.0, -32, ease_out), (1.4, -26), (1.8, -34), (2.2, -28), (2.55, -32), (2.95, -4), (3.4, 0, ease_out)), t)
    add(p, "jaw", rot=(jaw - 1.4 * tremor(t, (8.7, 12.1, 5.9), phase=1.9) * env, 0, 0))
    arms(p, -12 * a + 0.6 * shiv, 10 * a, -10 * a)
    trail(p, t, lambda u: -2.5 * f_(tr((0, 0), (1.0, 0), (1.6, 1, ease_out), (2.2, -1), (2.6, -0.3), (3.4, 0)), u), delay=0.1)
    alive(p, t, k=1.0 - 0.8 * smooth((t - 0.4) / 0.4) * (1 - smooth((t - 2.8) / 0.5)))
    return T.stand(p)


def f_(track, t): return float(track(t))


def call(t):
    """a low hum with the snout tucked, the throat pulsing, the sail lifting with the chest"""
    p = {}
    k = f_(tr((0, 0), (0.5, 1, ease_out), (2.0, 1), (2.6, 0, ease_in)), t)
    env = window(t, 0.45, 2.05, 0.25)
    hum = tremor(t, (9.9, 13.7, 7.1), (0.8, 0.45, 0.3)) * env
    add(p, "body", rot=(2 * k + 0.3 * hum, 0, 0), pos=(0, T.K * 0.8 * k, 0))
    neck(p, -8 * k + 0.7 * hum); add(p, "skull", rot=(-10 * k - 0.7 * hum, 0, 0)); add(p, "jaw", rot=(0.5 - 0.3 * hum, 0, 0))
    trail(p, t, lambda u: 1.2 * wave(u, 2.6, -0.4) * f_(tr((0, 0), (0.5, 1, ease_out), (2.0, 1), (2.6, 0, ease_in)), u), delay=0.12)
    alive(p, t, k=1.0 - 0.6 * k)
    return T.stand(p)


def threat(t):
    """the warning: the snout aimed low at the intruder, the jaws parted, both arms lifted with the claws hooked, a slow
    sway of the sail, one foot stamped"""
    p = {}
    k = f_(tr((0, 0), (0.4, 1, ease_out), (2.0, 1), (2.4, 0, ease_in)), t)
    stamp = f_(tr((0, 0), (0.5, 0), (0.9, 1, ease_out), (1.05, 0, ease_in), (2.4, 0)), t)
    jolt = math.exp(-((t - 1.08) / 0.08) ** 2)
    hiss = tremor(t, (8.9, 12.7, 5.7)) * window(t, 0.3, 2.0, 0.2)
    sail = math.sin(2 * math.pi * (t - 0.3) / 1.4) * window(t, 0.3, 2.1, 0.3)
    add(p, "body", rot=(4 * k + 2 * jolt, 0, 4 * sail - 2 * stamp), pos=(0, T.K * (-2.5 * k - 1.0 * jolt), 0))
    neck(p, -8 * k + 0.6 * hiss, 0, 0); add(p, "skull", rot=(-2 * k + 2 * jolt + 0.8 * hiss, 0, 0))
    add(p, "jaw", rot=(-10 * k - 4 * jolt - 1.2 * hiss, 0, 0))
    arms(p, -22 * k, 26 * k, -24 * k)
    trail(p, t, lambda u: 3 * math.sin(2 * math.pi * (u - 0.3) / 1.4) * window(u, 0.3, 2.1, 0.3), delay=0.1)
    alive_upper(p, t, k=0.5)
    T.plant(p, "r"); T.plant(p, "l", 11 * stamp, -5 * stamp, 0, -10 * stamp)
    return p


# ------------------------------------------------------------------ the snout: snaps sideways and darts, never bites down
# the heavy bite: the jaws shut at 0.55 s (ApexTheropod.BITE, tick 11)
SN_YAW = Track([(0, 0), (0.32, 22, ease_out), (0.5, -10, ease_in), (0.6, -12), (1.5, -6), (2.0, 0, back_out)])
SN_PIT = Track([(0, 0), (0.32, 6, ease_out), (0.5, -10, ease_in), (0.6, -9), (1.5, -6), (2.0, 0, back_out)])


def croc_shake(t):
    return sum(a * math.exp(-((t - c) / w) ** 2) for c, a, w in ((0.8, 1.0, 0.09), (0.98, -0.85, 0.08), (1.15, 0.6, 0.08), (1.31, -0.35, 0.08)))


def attack(t):
    """the crocodile snap: the head swings out to one side with the long jaws open, sweeps back across and snaps shut,
    then thrashes side to side to tear (shakes that die away), and lets go"""
    p = {}
    yw, pt = float(SN_YAW(t)), float(SN_PIT(t))
    sh = croc_shake(t)
    jaw = f_(tr((0, 0), (0.1, -4), (0.36, -40, ease_out), (0.48, -42), (0.55, -2, ease_in), (1.45, -3), (1.62, -20, ease_out), (1.8, -4), (2.0, 0, ease_out)), t)
    add(p, "body", rot=(-0.2 * pt, 0.3 * yw + 3 * sh, -0.15 * yw - 2 * sh),
        pos=(0, T.K * -1.0 * smooth(t / 0.5) * (1 - smooth((t - 1.5) / 0.45)), T.K * -2.0 * smooth((t - 0.35) / 0.2) * (1 - smooth((t - 1.4) / 0.6))))
    neck(p, pt, 0.6 * yw + 14 * sh, -0.1 * yw - 3 * sh)
    add(p, "skull", rot=(0.5 * pt, 0.4 * yw + 9 * sh, 0.25 * yw - 12 * sh)); add(p, "jaw", rot=(jaw, 0, 0))
    arms(p, -10 * window(t, 0.3, 1.5, 0.2), 14 * window(t, 0.3, 1.5, 0.2), -12 * window(t, 0.3, 1.5, 0.2))
    trail(p, t, lambda u: -0.25 * float(SN_YAW(u)) - 4 * croc_shake(u), delay=0.07)
    alive(p, t, k=0.5)
    return T.stand(p)


# the quick snap: the jaws shut at 0.3 s (QUICK_BITE, tick 6)
def attack_quick(t):
    """the heron's dart: the neck straightens and the snout shoots forward in a line, a snap, the head drawn back to its
    S; the body barely moves"""
    p = {}
    n = f_(tr((0, 0), (0.12, 1, ease_out), (0.28, -1, ease_in), (0.42, -0.8), (0.9, 0, back_out)), t)
    a = max(0.0, n); d = max(0.0, -n)
    j = f_(tr((0, 0), (0.14, -26, ease_out), (0.24, -27), (0.3, -1, ease_in), (0.55, -3), (0.9, 0, ease_out)), t)
    add(p, "body", rot=(1.5 * d, 0, 0), pos=(0, 0, T.K * (0.8 * a - 2.0 * d)))
    T.neck(p, (8 * a - 12 * d, 0, 0)); add(p, "neck", rot=(-4 * a + 6 * d, 0, 0))     # the base draws back, then the neck throws out straight
    add(p, "skull", rot=(-3 * a - 3 * d, 0, 0)); add(p, "jaw", rot=(j, 0, 0))
    trail(p, t, lambda u: 1.2 * math.exp(-((u - 0.3) / 0.12) ** 2), delay=0.06)
    alive(p, t, k=0.6)
    return T.stand(p)


# the thumb-claw swipe (Spinosaur.SWIPE: the hit at 0.55 s, 1.3 s)
SW = Track([(0, 0), (0.3, 1, ease_out), (0.4, 1.05), (0.55, -1, smooth), (0.75, -0.65), (1.3, 0, back_out)])


def swipe(t):
    """the left arm cocked up and back, the body winding with it, then the hook sweeps down and across; the snout pulls
    up and away from its own claw, the sail swings after the twist"""
    p = {}
    w = float(SW(t)); a = max(0.0, w); b = max(0.0, -w)
    add(p, "body", rot=(-4 * a + 4 * b, 7 * a - 9 * b, -3 * a + 4 * b), pos=(0, 0, T.K * -2.5 * b))
    neck(p, 8 * a + 3 * b, -10 * a + 8 * b, 0); add(p, "skull", rot=(4 * a + 4 * b, -4 * a + 4 * b, 0)); add(p, "jaw", rot=(-8 * a - 6 * b, 0, 0))
    add(p, "arm_l", rot=(-75 * a + 50 * b, 0, 14 * a - 6 * b)); add(p, "forearm_l", rot=(40 * a - 45 * b, 0, 0)); add(p, "hand_l", rot=(25 * a - 45 * b, 0, 0))
    add(p, "arm_r", rot=(-10 * a + 6 * b, 0, 0))
    trail(p, t, lambda u: -4 * float(SW(u)), delay=0.08)
    alive(p, t, k=0.5)
    return T.stand(p)


CLAW_SWIPE_T = 1.5
CS = Track([(0, 0), (0.36, 1, ease_out), (0.46, 1.06), (0.62, -1, smooth), (0.85, -0.8), (1.5, 0, back_out)])


def claw_swipe(t):
    """the gaff hook (Baryonyx's thumb, Charig & Milner 1997): both arms raised high and wide, the body leaning back on
    its haunches with the snout lifted out of the way, then both hooks come down together and rake back toward the
    chest as it drops its weight forward; the hit lands at 0.62 s"""
    p = {}
    w = float(CS(t)); a = max(0.0, w); b = max(0.0, -w)
    add(p, "body", rot=(-6 * a + 6 * b, 0, 0), pos=(0, T.K * (0.6 * a - 1.4 * b), T.K * (1.2 * a - 2.5 * b)))
    neck(p, 14 * a - 4 * b, 0, 0); add(p, "skull", rot=(6 * a - 2 * b, 0, 0)); add(p, "jaw", rot=(-6 * a - 10 * b, 0, 0))
    for s, sx in MS:
        add(p, f"arm_{s}", rot=(-85 * a + 40 * b, 0, sx * (18 * a - 4 * b)))
        add(p, f"forearm_{s}", rot=(30 * a - 55 * b, 0, 0))
        add(p, f"hand_{s}", rot=(30 * a - 50 * b, 0, 0))
    trail(p, t, lambda u: 5 * max(0.0, float(CS(u))) - 4 * max(0.0, -float(CS(u))), delay=0.08, axis=0, gain=(0.6, 0.7, 0.8, 0.9, 1.0))
    alive(p, t, k=0.5)
    return T.stand(p)


def hurt(t):
    p = {}; e = math.exp(-(t / 0.18)) * smooth(t / 0.04)
    el = math.exp(-max(0.0, t - 0.1) / 0.25) * smooth((t - 0.06) / 0.06)      # the sail answers late
    add(p, "body", rot=(-5 * e, 5 * e, -4 * e + 3 * el), pos=(0, T.K * -1.2 * e, T.K * 2.5 * e))
    neck(p, 10 * e, -10 * e, 0); add(p, "skull", rot=(6 * e, -8 * e, 6 * e)); add(p, "jaw", rot=(-16 * e, 0, 0))
    arms(p, -10 * e, 12 * e, 0)
    trail(p, t, lambda u: -4 * math.exp(-(u / 0.22)) * smooth(u / 0.05), delay=0.05)
    alive(p, t, k=0.4)
    return T.stand(p)


# ------------------------------------------------------------------ the sail: its display
SAIL_DISPLAY_T = 4.4


def sail_display(t):
    """it turns broadside to the rival in two slow steps, rolls the sail toward it and arches the back so the sail
    stands at its tallest, the head turned back over the shoulder to keep the rival in sight, the jaws parted; it holds,
    swaying slowly so the sail catches the light, then turns back"""
    p = {}
    side = f_(tr((0, 0), (0.25, 0), (1.25, 1, smooth), (3.4, 1), (4.3, 0, smooth), (4.4, 0)), t)
    arch = f_(tr((0, 0), (0.8, 0), (1.5, 1, ease_out), (3.3, 1), (3.9, 0, ease_in), (4.4, 0)), t)
    sway = math.sin(2 * math.pi * (t - 1.5) / 1.6) * window(t, 1.5, 3.3, 0.35)
    swl = math.sin(2 * math.pi * (t - 1.7) / 1.6) * window(t, 1.7, 3.5, 0.35)      # the sail itself, behind the hips
    turn = 32 * side
    add(p, "root", rot=(0, turn, 0))
    add(p, "body", rot=(-4 * arch, 0, -6 * arch + 2.5 * swl), pos=(0, T.K * 1.2 * arch, 0))
    # the head turns back to the rival, the neck carrying most of it
    neck(p, 6 * arch, -0.85 * turn + 3 * sway, 2 * arch)
    add(p, "skull", rot=(-4 * arch, -0.35 * turn - 2 * sway, 3 * arch))
    hiss = window(t, 1.6, 3.2, 0.3)
    add(p, "jaw", rot=(-8 * hiss - 1.0 * tremor(t, (8.3, 12.1, 5.3)) * hiss, 0, 0))
    arms(p, -10 * arch, 12 * arch, -14 * arch)
    trail(p, t, lambda u: -0.3 * 32 * f_(tr((0, 0), (0.25, 0), (1.25, 1, smooth), (3.4, 1), (4.3, 0, smooth), (4.4, 0)), u)
          + 1.6 * math.sin(2 * math.pi * (u - 1.5) / 1.6) * window(u, 1.5, 3.3, 0.35), delay=0.12)
    alive_upper(p, t, k=0.7)
    # the steps that carry the turn: each foot lifts once going round and once coming back
    for s, c0, c1 in (("l", 0.5, 3.6), ("r", 0.95, 4.05)):
        lift = 0.0
        for c in (c0, c1):
            u = (t - c) / 0.45
            if 0 < u < 1: lift = 7 * math.sin(math.pi * u) ** 1.3
        add(p, f"thigh_{s}", rot=(0, 0, 0))
        T.plant(p, s, lift, 0, 10 * lift / 7, -16 * lift / 7, clear=-0.05 if lift < 0.05 else 0.8)
    return p


def display(t):
    p = _BASE["display"](t)
    alive_upper(p, t, k=0.5)
    return p


# ------------------------------------------------------------------ the duel set, the Spinosaurus's way
GUARD_T = 3.2


def guard(t):
    """a boxer with hooks: the arms raised in front of the chest with the thumb claws cocked, the snout aimed low at the
    rival like a spear, the jaws a little open; it stands side-on, the sail toward the rival, rocking slowly"""
    p = {}
    Tg = GUARD_T
    rock = wave(t, Tg)
    sail = wave(t, Tg, -0.9)
    hiss = tremor(t, (19 / Tg, 28 / Tg, 13 / Tg), (0.7, 0.4, 0.3))
    add(p, "body", rot=(4 + 0.8 * rock, -8 + 1.0 * wave(t, Tg, 1.0), -4 + 1.5 * sail), pos=(0, T.K * (-2.2 + 0.4 * rock), 0))
    neck(p, -8 - 1.0 * rock + 0.4 * hiss, 9 + 1.5 * wave(t, Tg / 2, 0.6), 2)
    add(p, "skull", rot=(-2 + 0.6 * hiss, 2 - 1.2 * wave(t, Tg / 2, 1.0), 0))
    add(p, "jaw", rot=(-6 - 2 * max(0.0, wave(t, Tg / 2, -0.5)) - 1.0 * hiss, 0, 0))
    for s, o in PH:
        add(p, f"arm_{s}", rot=(-34 + 3 * wave(t, Tg, -1 - 3 * o), 0, 0))
        add(p, f"forearm_{s}", rot=(30 + 3 * wave(t, Tg, -1.6 - 3 * o), 0, 0))
        add(p, f"hand_{s}", rot=(-30 + 6 * max(0.0, wave(t, Tg / 2, -2.0 - 3 * o)) ** 2, 0, 0))     # the hooks flex
    trail(p, t, lambda u: 2.5 * wave(u, Tg, -0.6), delay=0.12, loop=Tg)
    trail(p, t, lambda u: -2.0 + 0.5 * wave(u, Tg / 2, -0.8), delay=0.08, axis=0, loop=Tg, gain=(0.6, 0.7, 0.8, 0.9, 1.0))
    for s, sx in MS:
        add(p, f"thigh_{s}", rot=(0, 8, 2.5 * sx + 4 - 1.5 * sail))
    T.plant(p, "l", 0.0, 3.0)
    T.plant(p, "r", 0.0, -3.5)
    return p


STRAFE_T = 2.2


def strafe(t, side):
    """heavy sidesteps round the rival, slow and wide, the sail rolled toward it and swaying late after each step, the
    arms held up, the snout on the rival"""
    d = 1.0 if side == "left" else -1.0
    ph = (t / STRAFE_T) % 1.0; w = 2 * math.pi * ph; p = {}
    add(p, "body", rot=(4, 0, -4.0 * d + 2.0 * math.sin(2 * w - 0.9)), pos=(T.K * 1.4 * d * math.sin(2 * w), T.K * (-2.2 + 0.6 * math.cos(2 * w)), 0))
    neck(p, -7, 0, 4.0 * d - 2.0 * math.sin(2 * w - 0.9)); add(p, "skull", rot=(-2, 0, d))
    add(p, "jaw", rot=(-4 - 0.8 * tremor(t, (13 / STRAFE_T, 20 / STRAFE_T, 9 / STRAFE_T), (0.7, 0.4, 0.3)), 0, 0))
    arms(p, -26, 24, -20)
    trail(p, t, lambda u: -d * 3.0 - 1.4 * math.sin(2 * math.pi * u / STRAFE_T - 0.9), delay=0.12, loop=STRAFE_T)
    for s, o in PH:
        sx = 1 if s == "l" else -1
        u = (ph + o) % 1.0
        if u < 0.38:
            sw = u / 0.38
            add(p, f"thigh_{s}", rot=(0, 0, d * 8.0 * (sw - 0.5) + 2.5 * sx))
            T.plant(p, s, 6.0 * math.sin(math.pi * sw) ** 1.2, 0.0, 8 * math.sin(math.pi * sw), -14 * math.sin(math.pi * sw),
                    clear=0.8 * math.sin(math.pi * sw) ** 0.5)
        else:
            st = (u - 0.38) / 0.62
            add(p, f"thigh_{s}", rot=(0, 0, -d * 8.0 * (st - 0.5) + 2.5 * sx))
            T.plant(p, s)
    return p


def strafe_left(t): return strafe(t, "left")
def strafe_right(t): return strafe(t, "right")


TURN_T = 2.2


def turn(t, side):
    """it steps round slowly: the snout swings into the turn first in a long arc (+ yaw is to the animal's right in game,
    a left turn leads with - yaw), the hips follow, and the sail swings out the other way, late, and settles"""
    d = 1.0 if side == "left" else -1.0
    lead = -d
    ph = (t / TURN_T) % 1.0; w = 2 * math.pi * ph; p = {}
    add(p, "body", rot=(0, lead * (4.0 + 1.5 * math.sin(w)), -lead * 2.5 + 2.5 * math.sin(w + 0.3 - 0.9)), pos=(0, T.K * (-0.8 + 0.5 * math.cos(2 * w)), 0))
    neck(p, -2.0, lead * (14.0 + 2.0 * math.sin(w - 0.6)), 0)
    add(p, "skull", rot=(0, lead * (5.0 + 1.5 * math.sin(w - 1.2)), 0))
    trail(p, t, lambda u: -lead * 3.0 - 1.4 * math.sin(2 * math.pi * u / TURN_T - 0.8), delay=0.14, loop=TURN_T)
    alive_upper(p, t, k=0.6, period=TURN_T / 2)
    for s, o in PH:
        u = (ph + o) % 1.0
        if u < 0.4:
            sw = u / 0.4
            ly = 6.5 * math.sin(math.pi * sw) ** 1.2
            dz = -3.0 * math.cos(math.pi * sw)
            toe = -18 * math.sin(math.pi * sw); meta = 12 * math.sin(math.pi * sw); clear = 1.0 * math.sin(math.pi * sw) ** 0.5
            add(p, f"thigh_{s}", rot=(0, lead * 6.0 * math.sin(math.pi * sw), 0))
        else:
            ly, dz, toe, meta, clear = 0.0, 3.0 - 6.0 * ((u - 0.4) / 0.6), 0.0, 0.0, -0.05
        add(p, f"thigh_{s}", rot=(0, -lead * 4.0, -2.5 * math.sin(w + 0.3 - 0.9) + lead * 2.5))
        T.plant(p, s, ly, dz, meta, toe, clear)
    return p


def turn_left(t): return turn(t, "left")
def turn_right(t): return turn(t, "right")


FEINT_T = 1.4


def feint(t):
    """a hook that never lands: the right arm flies up as if to swipe and the snout darts in beside it, then both pull
    back; testing the rival"""
    p = {}
    k = f_(tr((0, 0), (0.25, 1, ease_out), (0.4, 1.05), (0.55, 0.4, ease_in), (0.8, 0.5), (1.4, 0, back_out)), t)
    dart = f_(tr((0, 0), (0.35, 0), (0.48, 1, ease_out), (0.62, 0.9), (0.9, -0.2, ease_in), (1.4, 0, back_out)), t)
    j = f_(tr((0, -2), (0.38, -20, ease_out), (0.52, -22), (0.58, -2, ease_in), (1.4, -2)), t)
    add(p, "body", rot=(-2 * k + 2 * dart, 5 * k, 2 * k), pos=(0, 0, T.K * -2.0 * dart))
    neck(p, 6 * k - 8 * dart, -6 * k, 0); add(p, "skull", rot=(2 * k - 3 * dart, -3 * k, 0)); add(p, "jaw", rot=(j, 0, 0))
    add(p, "arm_r", rot=(-60 * k, 0, -10 * k)); add(p, "forearm_r", rot=(30 * k, 0, 0)); add(p, "hand_r", rot=(20 * k, 0, 0))
    add(p, "arm_l", rot=(-15 * k, 0, 0))
    trail(p, t, lambda u: 3 * f_(tr((0, 0), (0.25, 1, ease_out), (0.4, 1.05), (0.55, 0.4, ease_in), (0.8, 0.5), (1.4, 0, back_out)), u), delay=0.09)
    alive(p, t, k=0.4)
    return T.stand(p)


BLOCK_T = 1.0


def block(t):
    """the parry: the near forearm swung up across the snout so the bite meets the arm, the head drawn back and away,
    the sail rocking with the twist, then back"""
    p = {}
    e = math.exp(-max(0.0, t - 0.14) / 0.3) * smooth(t / 0.14)
    el = math.exp(-max(0.0, t - 0.2) / 0.35) * smooth((t - 0.12) / 0.1)
    add(p, "body", rot=(-3 * e, -7 * e, 3 * e - 3 * el), pos=(0, 0, T.K * 1.6 * e))
    neck(p, 10 * e, 12 * e, 4 * e); add(p, "skull", rot=(6 * e, 6 * e, 6 * e)); add(p, "jaw", rot=(-6 * e, 0, 0))
    add(p, "arm_l", rot=(-60 * e, 0, -14 * e)); add(p, "forearm_l", rot=(55 * e, 0, 0)); add(p, "hand_l", rot=(-20 * e, 0, 0))
    add(p, "arm_r", rot=(-15 * e, 0, 0))
    trail(p, t, lambda u: 5 * math.exp(-max(0.0, u - 0.08) / 0.35) * smooth(u / 0.08), delay=0.06)
    alive_upper(p, t, k=0.4)
    return T.stand(p)


RECOIL_T = 1.2


def recoil(t):
    """its snap met an arm: the long snout knocked aside, the head wobbling on the long neck, a heavy step back, the sail
    lurching after"""
    p = {}
    e = math.exp(-max(0.0, t - 0.05) / 0.25) * smooth(t / 0.05)
    wob = math.exp(-max(0.0, t - 0.12) / 0.22) * math.sin(2 * math.pi * 3.2 * (t - 0.12)) * smooth((t - 0.1) / 0.06)
    el = math.exp(-max(0.0, t - 0.2) / 0.3) * smooth((t - 0.15) / 0.1)
    add(p, "body", rot=(-3 * e, 4 * e, -3 * e + 4 * el), pos=(0, 0, T.K * 3.0 * e))
    neck(p, 6 * e, 16 * e + 5 * wob, -4 * e); add(p, "skull", rot=(3 * e, 10 * e + 6 * wob, -8 * e)); add(p, "jaw", rot=(-12 * e, 0, 0))
    arms(p, -10 * e, 10 * e, 0)
    trail(p, t, lambda u: -5 * math.exp(-max(0.0, u - 0.05) / 0.3) * smooth(u / 0.05), delay=0.06)
    alive_upper(p, t, k=0.4)
    T.plant(p, "l")
    s = math.sin(math.pi * min(1.0, max(0.0, (t - 0.15) / 0.55)))
    T.plant(p, "r", 6 * s ** 2, 4 * smooth((t - 0.15) / 0.55) * (1 - smooth((t - 0.75) / 0.45)), 0, -10 * s)
    return p


SUBMIT_T = 2.6


def submit(t):
    """beaten: it lowers itself and turns the sail AWAY (the display reversed), the snout down to the ground, the arms
    folded in, and turns to go back to the water"""
    p = {}
    k = f_(tr((0, 0), (0.7, 1, ease_out), (2.6, 1)), t)
    turn_ = f_(tr((0, 0), (0.9, 0), (1.8, 1, ease_out), (2.6, 1)), t)
    add(p, "body", rot=(4 * k, 14 * turn_, 6 * k), pos=(0, T.K * -3.0 * k, 0))
    neck(p, -22 * k, 10 * turn_, 0); add(p, "skull", rot=(-6 * k, 5 * turn_, 0)); add(p, "jaw", rot=(-1, 0, 0))
    arms(p, 14 * k, -10 * k, 10 * k)
    trail(p, t, lambda u: -4 * f_(tr((0, 0), (0.9, 0), (1.8, 1, ease_out), (2.6, 1)), u), delay=0.12)
    trail(p, t, lambda u: -3 * f_(tr((0, 0), (0.7, 1, ease_out), (2.6, 1)), u), delay=0.1, axis=0, gain=(0.6, 0.7, 0.8, 0.9, 1.0))
    for s, _ in PH:
        add(p, f"thigh_{s}", rot=(0, -14 * turn_, -6 * k))
    alive_upper(p, t, k=0.7)
    return T.stand(p)


SHOVE_T = 1.6


def shove(t):
    """the flank slam: it swings its side into the rival, the sail and the weight of the hips behind it, the head held
    away from the blow"""
    p = {}
    k = f_(tr((0, 0), (0.45, -0.5, ease_out), (0.7, 1, ease_in), (0.85, 0.85), (1.6, 0, back_out)), t)
    a = max(0.0, k); c = max(0.0, -k) / 0.5
    jolt = math.exp(-((t - 0.72) / 0.07) ** 2)
    add(p, "body", rot=(2 * jolt, 10 * a - 6 * c, 9 * a - 5 * c), pos=(T.K * (2.5 * a - 1.2 * c), T.K * -1.2 * (a + c), 0))
    neck(p, -2 * a, -16 * a + 6 * c, -4 * a); add(p, "skull", rot=(2 * jolt, -6 * a, 0)); add(p, "jaw", rot=(-10 * jolt, 0, 0))
    arms(p, -12 * a, 10 * a, 0)
    trail(p, t, lambda u: -8 * max(0.0, f_(tr((0, 0), (0.45, -0.5, ease_out), (0.7, 1, ease_in), (0.85, 0.85), (1.6, 0, back_out)), u)), delay=0.07)
    alive_upper(p, t, k=0.4)
    for s, _ in PH:
        add(p, f"thigh_{s}", rot=(0, -10 * a + 6 * c, -9 * a + 5 * c))
    return T.stand(p)


BITE_LOW_T = 1.2


def bite_low(t):
    """the scoop: the snout swept low along the ground like a fish taken from the shallows (jaws shut at 0.4 s)"""
    p = {}
    n = tr((0, (0, 0)), (0.2, (4, -14), ease_out), (0.38, (-26, 8), ease_in), (0.5, (-22, 10)), (1.2, (0, 0), back_out))(t)
    j = f_(tr((0, 0), (0.18, -26, ease_out), (0.34, -28), (0.41, -2, ease_in), (0.7, -4), (1.2, 0, ease_out)), t)
    add(p, "body", rot=(-0.3 * n[0], 0.2 * n[1], 0), pos=(0, T.K * 0.05 * n[0], 0))
    neck(p, n[0], n[1], 0); add(p, "skull", rot=(0.4 * n[0], 0.5 * n[1], -0.3 * n[1])); add(p, "jaw", rot=(j, 0, 0))
    trail(p, t, lambda u: -0.2 * tr((0, (0, 0)), (0.2, (4, -14), ease_out), (0.38, (-26, 8), ease_in), (0.5, (-22, 10)), (1.2, (0, 0), back_out))(u)[1], delay=0.07)
    alive(p, t, k=0.5)
    return T.stand(p)


BITE_SIDE_T = 1.3


def bite_side(t):
    """a sideways sweep of the long jaws, wide open, snapping at the end of the arc (0.45 s); the sail rolls after"""
    p = {}
    yw = f_(tr((0, 0), (0.25, -26, ease_out), (0.45, 12, ease_in), (0.6, 15), (1.3, 0, back_out)), t)
    j = f_(tr((0, 0), (0.2, -36, ease_out), (0.4, -38), (0.47, -2, ease_in), (0.8, -4), (1.3, 0, ease_out)), t)
    lag = f_(tr((0, 0), (0.4, -26), (0.62, 12, ease_in), (0.78, 15), (1.3, 0, back_out)), t)
    add(p, "body", rot=(0, 0.3 * yw, -0.12 * lag), pos=(0, 0, T.K * -1.5 * smooth((t - 0.3) / 0.15) * (1 - smooth((t - 0.7) / 0.5))))
    neck(p, -4 * smooth(t / 0.4), 0.6 * yw, 0.08 * yw); add(p, "skull", rot=(0, 0.4 * yw, 0.3 * yw)); add(p, "jaw", rot=(j, 0, 0))
    trail(p, t, lambda u: -0.2 * f_(tr((0, 0), (0.25, -26, ease_out), (0.45, 12, ease_in), (0.6, 15), (1.3, 0, back_out)), u), delay=0.07)
    alive(p, t, k=0.5)
    return T.stand(p)


def snort(t):
    """water out of the nostrils: the snout flicks up and shakes side to side twice, quick"""
    p = {}
    k = f_(tr((0, 0), (0.25, 1, ease_out), (0.7, 0.8), (1.4, 0, ease_out)), t)
    shk = math.exp(-((t - 0.6) / 0.18) ** 2) * math.sin(2 * math.pi * 6.0 * (t - 0.6))
    neck(p, 4 * k, 0, 0); add(p, "skull", rot=(8 * k, 5 * shk, 9 * shk)); add(p, "jaw", rot=(-5 * math.exp(-((t - 0.3) / 0.06) ** 2), 0, 0))
    trail(p, t, lambda u: 1.6 * math.exp(-((u - 0.6) / 0.25) ** 2), delay=0.08)
    alive(p, t, k=0.8)
    return T.stand(p)


SETTLE_T = 2.8


def settle(t):
    """it moves its weight onto the left foot, lifts the right and sets it down a little out; the sail sways over and
    back after the hips"""
    p = {}
    wgt = f_(tr((0, 0), (0.6, 1, ease_out), (1.7, 1), (2.4, 0, ease_out), (2.8, 0)), t)
    sl = f_(tr((0, 0), (0.85, 1.1, ease_out), (1.9, 1), (2.65, -0.12, ease_out), (2.8, 0)), t)
    step = f_(tr((0, 0), (0.7, 0), (1.1, 1, ease_out), (1.4, 1), (1.7, 0, ease_in), (2.8, 0)), t)
    hroll = 4.0 * sl
    add(p, "body", rot=(0, -2.0 * wgt, hroll))
    neck(p, 0, 1.6 * wgt, -0.8 * hroll)
    trail(p, t, lambda u: 2.0 * f_(tr((0, 0), (0.6, 1, ease_out), (1.7, 1), (2.4, 0, ease_out), (2.8, 0)), u), delay=0.12)
    alive_upper(p, t, k=0.8)
    for s, _ in PH:
        add(p, f"thigh_{s}", rot=(0, 2.0 * wgt, -hroll))
    T.plant(p, "l")
    lift = 7.0 * math.sin(math.pi * min(1.0, max(0.0, (t - 0.7) / 1.0))) ** 2
    T.plant(p, "r", lift, -3 * smooth((t - 0.7) / 0.9), 8 * step, -12 * step, clear=-0.05)
    return p


SCAN_T = 5.0


def scan(t):
    """it lifts the snout and looks over the water from one side to the other, slowly"""
    p = {}
    up = f_(tr((0, 0), (0.6, 1, ease_out), (4.3, 1), (5.0, 0, ease_out)), t)
    yw = f_(tr((0, 0), (0.6, 0), (1.5, 20, ease_out), (2.1, 18), (3.1, -18, ease_out), (3.8, -20), (4.5, 0, ease_out), (5.0, 0)), t)
    add(p, "body", rot=(-1 * up, 0.12 * yw, 0)); neck(p, 6 * up, 0.5 * yw, 0); add(p, "skull", rot=(3 * up, 0.45 * yw, -0.1 * yw))
    trail(p, t, lambda u: -0.1 * f_(tr((0, 0), (0.6, 0), (1.5, 20, ease_out), (2.1, 18), (3.1, -18, ease_out), (3.8, -20), (4.5, 0, ease_out), (5.0, 0)), u), delay=0.14)
    alive(p, t, k=0.9)
    return T.stand(p)


# ------------------------------------------------------------------ rest transitions and tiredness
LIE_DOWN_T = 2.4


def lie_down(t):
    """the short hind legs fold, the chest goes down, the arms reach for the ground, the sail sways as it lands"""
    p = {}
    k = f_(tr((0, 0), (0.3, 0.05), (1.6, 0.93, ease_in), (1.85, 1.03), (2.4, 1.0, ease_out)), t)
    look = f_(tr((0, 0), (0.4, 1, ease_out), (1.5, 1), (2.4, 0, ease_out)), t)
    T.lie(p, k)
    neck(p, -6 * look); add(p, "skull", rot=(-4 * look, 0, 0))
    land = math.exp(-((t - 1.75) / 0.12) ** 2)
    sl = math.exp(-max(0.0, t - 1.8) / 0.3) * math.sin(2 * math.pi * 1.8 * (t - 1.8)) * smooth((t - 1.75) / 0.08)
    add(p, "body", rot=(0.8 * land, 0, 2.0 * sl))
    trail(p, t, lambda u: 2.0 * math.exp(-((u - 1.75) / 0.15) ** 2), delay=0.07, axis=0, gain=(0.6, 0.7, 0.8, 0.9, 1.0))
    alive_upper(p, t, k=0.5)
    return ground_fit(S, p)


GET_UP_T = 2.4


def get_up(t):
    p = {}
    k = f_(tr((0, 1.0), (0.5, 1.02), (1.45, 0.05, ease_out), (1.7, -0.02), (2.4, 0.0, ease_out)), t)
    push = math.exp(-((t - 0.7) / 0.22) ** 2)
    T.lie(p, max(0.0, k))
    neck(p, -12 * push); add(p, "skull", rot=(-6 * push, 0, 0))
    arms(p, 10 * push, -10 * push, 0)
    wob = math.exp(-max(0.0, t - 1.5) / 0.3) * math.sin(2 * math.pi * 2.0 * (t - 1.5)) * smooth((t - 1.45) / 0.1)
    add(p, "body", rot=(0, 0, 3.0 * wob))
    trail(p, t, lambda u: -2.0 * math.exp(-max(0.0, u - 1.5) / 0.35) * math.sin(2 * math.pi * 2.0 * (u - 1.5)) * smooth((u - 1.45) / 0.1), delay=0.08)
    alive_upper(p, t, k=0.5)
    return ground_fit(S, p)


FALL_ASLEEP_T = 3.8


def fall_asleep(t):
    p = {}
    k = f_(tr((0, 0), (0.3, 0.05), (1.6, 0.93, ease_in), (1.85, 1.03), (2.2, 1.0, ease_out), (3.8, 1.0)), t)
    head = f_(tr((0, 0), (2.5, 0), (3.6, 1.0, ease_in), (3.8, 1.0)), t)
    T.lie(p, k, head_down=head)
    yawn = f_(tr((0, 0), (2.0, 0), (2.35, -24, ease_out), (2.55, -22), (2.8, -2, ease_in), (3.8, 0)), t)
    add(p, "jaw", rot=(yawn, 0, 0)); add(p, "skull", rot=(0.25 * -yawn, 0, 0))
    alive_upper(p, t, k=0.4)
    return ground_fit(S, p)


IDLE_TIRED_T = 3.6


def idle_tired(t):
    """spent: the long jaws hang open (a crocodile's gape, to cool), the chest heaving, the arms hanging, the snout low,
    the sail tilting slowly with each heavy breath"""
    p = {}
    Ti = IDLE_TIRED_T
    pant = wave(t, Ti / 4)
    add(p, "body", rot=(2.5 + 1.8 * pant, 0, 1.0 * wave(t, Ti, 0.6) + 0.6 * wave(t, Ti / 4, -0.8)), pos=(0, T.K * (-1.4 + 0.7 * pant), 0))
    neck(p, -10 - 1.5 * wave(t, Ti / 4, -0.6), 2 * wave(t, Ti, 0.5), 0)
    add(p, "skull", rot=(-3 - 1.0 * wave(t, Ti / 4, -1.2), 1.2 * wave(t, Ti, -0.5), 0))
    add(p, "jaw", rot=(-16 - 4 * max(0.0, wave(t, Ti / 4, -0.4)), 0, 0))
    for s, o in PH:
        add(p, f"arm_{s}", rot=(8 + 2 * wave(t, Ti / 4, -0.8 - 3 * o), 0, 0)); add(p, f"hand_{s}", rot=(6, 0, 0))
    trail(p, t, lambda u: 1.4 * wave(u, Ti, -0.8), delay=0.12, loop=Ti)
    trail(p, t, lambda u: -2.0 + 0.4 * wave(u, Ti / 4, -0.5), delay=0.08, axis=0, loop=Ti, gain=(0.6, 0.7, 0.8, 0.9, 1.0))
    return T.stand(p)


WALK_TIRED_T = 2.6


def walk_tired(t):
    p = gait2(t, WALK_TIRED_T, 50, 0.66, 6, 1.8, lean=2, drop=1.5, head=-9, tail_up=-2, roll=9.0, yaw=3.5, whip=0.8, lag=1.1, arm_sw=5.0)
    add(p, "jaw", rot=(-12 - 4 * max(0.0, wave(t, WALK_TIRED_T / 2)), 0, 0))
    neck(p, -1.4 * wave(t, WALK_TIRED_T / 2, -0.5))
    return p


# ------------------------------------------------------------------ the quieter ones
def _upper(fn, k=0.5):
    def g(t):
        p = fn(t); alive_upper(p, t, k=k); return p
    g.__name__ = getattr(fn, "__name__", "f"); g.__doc__ = fn.__doc__
    return g


fish = _upper(_BASE["fish"], 0.3)
sniff, look_back, shake, yawn, stretch, eat, drink, tame = (_upper(_BASE[n], 0.5) for n in
                                                            ("sniff", "look_back", "shake", "yawn", "stretch", "eat", "drink", "tame"))
