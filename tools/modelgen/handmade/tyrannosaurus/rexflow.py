"""T. rex: the fluid set (06/11/2026). Rodrigo: "quero que realmente tenha mais fluidez em cada animacao... sempre manter
um bicho em movimento, ate mesmo parado ele tem que ter animacao de respirando bem fluida, nada abrupto, o ataque e
rugido tambem... aquela vibracao".

What the study of the Raxiores T. rex taught (docs/estudos/08_ANIMACAO_RAXIORES.md) and how it is done here:
  * NOTHING STOPS. Every one-shot carries the breathing layer (`alive`), so the animal never freezes between poses;
    the idle is made of slow cycles whose periods divide the loop but never line up (breath 8/3 s, arms 4 s, weight and
    tail 8 s), so no two bones peak together.
  * NOTHING SNAPS ON OR OFF. Every effect has an envelope that fades in and out (`window`), the tremor included (ours
    was a pure 9 Hz sine switched on at 1.0 s and off at 2.5 s).
  * THE VIBRATION IS ORGANIC: the throat tremor is the sum of three sines at frequencies that do not repeat (`tremor`),
    different for the neck, the skull and the jaw, so the chain shivers instead of buzzing.
  * THE ROAR BREATHES: the jaw opens in bellows (pulses that grow and fall, irregularly timed), not held open; the head
    sweeps slowly while it roars, and the end is a shake that dies out.
  * EVERY ACTION HAS THREE BEATS: anticipation (rear back, cock the head), a fast action (the strike lands in ~0.1 s),
    follow-through and a settle that passes the rest pose a little and comes back (`back_out`).
  * THE TAIL AND NECK FOLLOW: any motion of the hips runs down the tail with a growing delay and a growing swing
    (`trail`), so the tip arrives last.
"""
import math

from anim2 import add, smooth, ease_in, ease_out, back_out, Track
import rexanim as R
import rexanims as A

# the originals this module builds on (rexanims rebinds its names to the versions here once it imports this module)
_BEG, _TAME = A.beg, A.tame

SIDES = A.SIDES
tr = A.tr
window = A.window
plant, stand = A.plant, A.stand


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def tremor(t, f=(7.3, 11.1, 4.7), amp=(1.0, 0.55, 0.35), phase=0.0):
    """an organic shiver: three sines at frequencies that never line up (-1.9 .. 1.9 at most)"""
    return sum(a * math.sin(2 * math.pi * fr * t + phase * (i + 1) + 1.3 * i) for i, (fr, a) in enumerate(zip(f, amp)))


def trail(p, t, fn, gain=(1.0, 1.4, 1.9, 2.5), delay=0.07, axis=1, bones=("tail1", "tail2", "tail3", "tail4"), loop=None):
    """follow-through down a chain: segment k takes fn(t - k*delay) * gain[k] on `axis` (in a loop the delay wraps)"""
    for k, b in enumerate(bones):
        u = t - delay * (k + 1)
        v = fn(u % loop if loop else max(0.0, u)) * gain[k]
        r = [0.0, 0.0, 0.0]; r[axis] = v
        add(p, b, rot=tuple(r))


def alive(p, t, k=1.0, period=3.2):
    """the breathing layer every one-shot carries (k fades it, e.g. while the roar fills the lungs on its own)"""
    br = wave(t, period)
    add(p, "body", rot=(0.7 * k * br, 0, 0), pos=(0, 0.45 * k * br, 0))
    add(p, "neck", rot=(-0.45 * k * wave(t, period, -0.5), 0, 0))
    add(p, "skull", rot=(-0.35 * k * wave(t, period, -1.0), 0, 0))
    add(p, "jaw", rot=(-0.5 * k * max(0.0, wave(t, period, -0.6)), 0, 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(1.6 * k * wave(t, period, -0.8 - o), 0, 0))
        add(p, f"forearm_{s}", rot=(1.8 * k * wave(t, period * 1.3, -1.4 - o), 0, 0))
    for i in range(1, 5):
        add(p, f"tail{i}", rot=(0.35 * k * i * wave(t, period, -0.45 * i), 0.9 * k * i * wave(t, period * 2.1, -0.7 * i), 0))
    return br


# ------------------------------------------------------------------ idle: 8 s, nothing still, nothing in step
IDLE_T = 8.0
LOOK = Track([(0, (0, 0)), (1.2, (0, 0)), (1.75, (3, 14), ease_out), (3.1, (3, 14)), (3.55, (-2, -9), ease_out), (5.0, (-2, -9)),
              (5.5, (5, 4), ease_out), (7.0, (5, 4)), (7.7, (0, 0), ease_in), (8.0, (0, 0))])


def idle(t):
    p = {}
    T = IDLE_T
    br = wave(t, T / 3)                                   # one slow breath every 2.67 s
    shift = wave(t, T, 0.4) + 0.3 * wave(t, T / 2, 1.1)   # the weight drifts from one foot to the other and back
    # a relaxed, asymmetric stance: the hips a little turned and rolled over the left foot, the right one forward
    hroll = 2.2 + 2.4 * shift
    hyaw = -2.0 + 1.6 * shift
    add(p, "body", rot=(1.0 * br - 0.6, hyaw, hroll), pos=(0, 0.55 * br - 0.3 * abs(shift), 0))
    # the chest counters the hips and lifts with the breath a beat later; the head floats and looks round, holding
    lp, ly = LOOK(t)
    add(p, "neck", rot=(-0.6 * wave(t, T / 3, -0.6) + 0.4 * lp, -0.8 * hyaw + 0.45 * ly + 1.2 * wave(t, T / 5, 0.3), -0.7 * hroll))
    add(p, "skull", rot=(-0.5 * wave(t, T / 3, -1.2) + 0.6 * lp + 0.6 * wave(t, T / 5, 1.6), 0.55 * ly, -0.2 * hroll - ly * 0.1))
    # the mouth parts a little on each out-breath
    add(p, "jaw", rot=(-0.9 - 1.6 * smooth(max(0.0, wave(t, T / 3, -0.9))), 0, 0))
    # the tail: a slow S that starts at the base and runs to the tip
    for i in range(1, 5):
        add(p, f"tail{i}", rot=(0.5 * i * wave(t, T / 3, -0.5 * i) - 0.4,
                               (1.2 + 3.0 * (i - 1)) * wave(t, T, -0.95 * i) + 0.8 * i * wave(t, T / 2, 0.6 - 0.8 * i), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(2.2 * wave(t, T / 2, -1.0 - 3 * o), 0, 0))
        add(p, f"forearm_{s}", rot=(2.6 * wave(t, T / 2, -1.7 - 3 * o) + 1.2 * br, 0, 0))
    # the legs hold the hips where they are (each thigh cancels the roll and yaw) and the right foot rests forward
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, -hyaw, -hroll))
    plant(p, "l")
    plant(p, "r", 0.0, -3.0, 0.0, 0.0)
    return p


# ------------------------------------------------------------------ roar: inhale, rise, roar in bellows, shake, settle
ROAR_T = 3.4
RISE = Track([(0, 0), (0.55, -0.4, ease_out), (0.95, 1.0, ease_out), (2.55, 0.85), (3.0, 0.1, ease_in), (3.4, 0.0)])
# the bellows: the jaw opens in pulses that grow and fall, irregular, never quite shutting while the roar lasts
JAW = Track([(0, 0), (0.45, -1.5), (0.62, -6, ease_out), (0.95, -38, ease_out), (1.25, -30), (1.5, -42), (1.78, -33), (2.08, -46),
             (2.32, -36), (2.55, -40), (2.95, -5), (3.4, 0, ease_out)])
SWEEP = Track([(0, 0), (0.95, 0), (1.6, 12, ease_out), (2.3, -11), (2.6, -4), (3.4, 0)])


def roar(t):
    p = {}
    up = float(RISE(t)); a = max(0.0, up); c = max(0.0, -up) / 0.4
    sw = float(SWEEP(t))
    env = window(t, 0.95, 2.6, 0.22)                      # the throat shivers only while the roar is out, fading
    shiv = tremor(t) * env
    shake = math.exp(-max(0.0, t - 2.62) / 0.22) * math.sin(2 * math.pi * 3.1 * (t - 2.62)) * smooth((t - 2.6) / 0.06)
    add(p, "body", rot=(-7 * a + 5 * c + 0.35 * shiv, 0.25 * sw, 0.2 * sw), pos=(0, -2.2 * c + 0.8 * a, 1.2 * a))
    add(p, "neck", rot=(17 * a - 9 * c + 0.9 * shiv, 0.55 * sw + 6 * shake, -0.25 * sw))
    add(p, "skull", rot=(10 * a - 7 * c + 1.3 * tremor(t, (8.6, 12.9, 5.3), phase=0.7) * env, 0.45 * sw + 7 * shake, -0.4 * sw - 5 * shake))
    add(p, "jaw", rot=(float(JAW(t)) - 1.6 * tremor(t, (9.4, 13.7, 6.1), phase=1.9) * env, 0, 0))
    # the tail rises with the effort and swings late with the sweep and the shake
    for i in range(1, 5):
        lag = max(0.0, t - 0.09 * i)
        ua = max(0.0, float(RISE(lag)))
        lsh = math.exp(-max(0.0, lag - 2.62) / 0.25) * math.sin(2 * math.pi * 3.1 * (lag - 2.62)) * smooth((lag - 2.6) / 0.06)
        add(p, f"tail{i}", rot=(2.2 * ua * (0.5 + 0.3 * i) + 1.5 * c, -0.25 * i * float(SWEEP(lag)) - 2.2 * i * lsh, 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(-14 * a + 0.8 * shiv, 0, 0)); add(p, f"forearm_{s}", rot=(-10 * a + 1.2 * shiv, 0, 0))
    alive(p, t, k=1.0 - 0.8 * smooth((t - 0.4) / 0.4) * (1 - smooth((t - 2.8) / 0.5)))
    return stand(p)


def roar_loud(t):
    """the big roar: crouch and fill the lungs, rear up with the snout to the sky, roar long in bellows with the whole
    chain shivering, a great shake of the head, settle"""
    p = {}
    up = float(tr((0, 0), (0.55, -0.35, ease_out), (1.15, 1, ease_out), (3.0, 0.9), (3.6, 0.05, ease_in), (4.4, 0))(t))
    a = max(0.0, up); c = max(0.0, -up) / 0.35
    env = window(t, 1.15, 3.0, 0.25)
    shiv = tremor(t, (6.8, 10.3, 4.1), (1.0, 0.6, 0.45)) * env
    sway = float(tr((0, 0), (1.15, 0), (1.9, 1, ease_out), (2.6, -1), (3.0, -0.3), (3.6, 0))(t))
    shake = math.exp(-max(0.0, t - 3.02) / 0.26) * math.sin(2 * math.pi * 2.8 * (t - 3.02)) * smooth((t - 3.0) / 0.06)
    add(p, "body", rot=(-14 * a + 6 * c + 0.5 * shiv, 2.5 * sway, 1.2 * sway), pos=(0, -3 * c + 1.0 * a, 2.0 * a))
    add(p, "neck", rot=(46 * a - 12 * c + 1.3 * shiv, 6 * sway + 8 * shake, -2 * sway))
    add(p, "skull", rot=(30 * a - 8 * c + 1.8 * tremor(t, (8.2, 12.4, 5.6), phase=0.9) * env, 4 * sway + 9 * shake, -3 * sway - 7 * shake))
    jaw = float(tr((0, 0), (0.55, -3), (0.9, -8, ease_out), (1.25, -40, ease_out), (1.6, -32), (1.95, -45), (2.3, -36), (2.65, -48),
                   (2.95, -38), (3.4, -4), (4.4, 0, ease_out))(t))
    add(p, "jaw", rot=(jaw - 2.0 * tremor(t, (9.1, 13.3, 6.4), phase=2.3) * env, 0, 0))
    for i in range(1, 5):
        lag = max(0.0, t - 0.08 * i)
        ua = max(0.0, float(tr((0, 0), (0.55, -0.35), (1.15, 1, ease_out), (3.0, 0.9), (3.6, 0.05, ease_in), (4.4, 0))(lag)))
        lsw = float(tr((0, 0), (1.15, 0), (1.9, 1, ease_out), (2.6, -1), (3.0, -0.3), (3.6, 0))(lag))
        lsh = math.exp(-max(0.0, lag - 3.02) / 0.3) * math.sin(2 * math.pi * 2.8 * (lag - 3.02)) * smooth((lag - 3.0) / 0.06)
        add(p, f"tail{i}", rot=(2.5 * ua * (0.5 + 0.25 * i) + 2 * c, -1.6 * i * lsw - 2.6 * i * lsh, 0))
    for s, _ in SIDES:
        add(p, f"arm_{s}", rot=(-20 * a + 1.0 * shiv, 0, 0)); add(p, f"forearm_{s}", rot=(-15 * a + 1.6 * shiv, 0, 0))
    alive(p, t, k=1.0 - 0.85 * smooth((t - 0.5) / 0.5) * (1 - smooth((t - 3.2) / 0.6)))
    return stand(p)


def call(t):
    """closed-mouth rumble: chin tucked, the chest pushed out, the whole body hums (an envelope, never a switch)"""
    p = {}
    k = float(tr((0, 0), (0.5, 1, ease_out), (2.0, 1), (2.6, 0, ease_in))(t))
    env = window(t, 0.45, 2.05, 0.25)
    hum = tremor(t, (10.7, 14.3, 7.9), (0.8, 0.45, 0.3)) * env
    add(p, "body", rot=(3 * k + 0.4 * hum, 0, 0), pos=(0, 1.0 * k, 0))
    add(p, "neck", rot=(-10 * k + 0.9 * hum, 0, 0)); add(p, "skull", rot=(-14 * k - 0.8 * hum, 0, 0)); add(p, "jaw", rot=(1 - 0.4 * hum, 0, 0))
    A.tail(p, t, yaw=0.8, T=3, base_pitch=-2 * k)
    alive(p, t, k=1.0 - 0.6 * k)
    return stand(p)


# ------------------------------------------------------------------ the bite: rear back, strike, shake, release, settle
# the hit lands at 0.55 s (Tyrannosaurus.BITE, tick 11): the jaw is shut by then
BITE_T = 2.0
B_PITCH = Track([(0, 0), (0.34, 12, ease_out), (0.47, -18, ease_in), (0.58, -14), (1.45, -11), (1.75, 2, ease_out), (2.0, 0)])
B_YAW = Track([(0, 0), (0.34, -9, ease_out), (0.5, 0), (0.62, 0)])
B_JAW = Track([(0, 0), (0.12, -6), (0.38, -46, ease_out), (0.47, -48), (0.55, -3, ease_in), (1.45, -4), (1.62, -18, ease_out),
               (1.8, -6), (2.0, 0, ease_out)])
B_LUNGE = Track([(0, 0), (0.34, 2.5, ease_out), (0.5, -6.5, ease_in), (0.62, -5.5), (1.45, -4.5), (2.0, 0, back_out)])


def bite_shake(t):
    """the tear: three shakes, the first the widest, irregularly spaced, dying out"""
    s = 0.0
    for c, amp, w in ((0.78, 1.0, 0.11), (1.0, -0.8, 0.1), (1.19, 0.55, 0.1), (1.36, -0.3, 0.09)):
        s += amp * math.exp(-((t - c) / w) ** 2)
    return s


def attack(t):
    p = {}
    pt, yw = float(B_PITCH(t)), float(B_YAW(t))
    sh = bite_shake(t)
    lunge = float(B_LUNGE(t))
    add(p, "body", rot=(-0.35 * pt + 3 * sh * 0, 0.5 * yw + 5 * sh, -0.3 * yw - 2.5 * sh),
        pos=(0, -1.2 * smooth(t / 0.47) * (1 - smooth((t - 1.5) / 0.45)), lunge))
    add(p, "neck", rot=(pt, 0.9 * yw + 13 * sh, -4 * sh))
    add(p, "skull", rot=(0.6 * pt, 0.6 * yw + 8 * sh, 0.5 * yw - 11 * sh))
    add(p, "jaw", rot=(float(B_JAW(t)), 0, 0))
    # the tail answers the twist and the shakes late, growing to the tip
    trail(p, t, lambda u: -0.9 * float(B_YAW(u)) - 7 * bite_shake(u), gain=(0.6, 1.0, 1.5, 2.1), delay=0.06)
    trail(p, t, lambda u: 0.12 * float(B_PITCH(u)), gain=(0.5, 0.7, 0.9, 1.1), delay=0.07, axis=0)
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(-0.4 * pt + 4 * sh, 0, 0)); add(p, f"forearm_{s}", rot=(-0.5 * pt + 5 * bite_shake(max(0, t - 0.05)), 0, 0))
    alive(p, t, k=0.5)
    return stand(p)


# the quick bite: lands at 0.3 s (QUICK_BITE, tick 6)
def attack_quick(t):
    p = {}
    n = tr((0, (0, 0)), (0.14, (9, -5), ease_out), (0.27, (-15, 1), ease_in), (0.42, (-11, 0)), (0.9, (0, 0), back_out))(t)
    j = float(tr((0, 0), (0.15, -34, ease_out), (0.25, -36), (0.3, -2, ease_in), (0.55, -5), (0.9, 0, ease_out))(t))
    push = float(tr((0, 0), (0.14, 1.5, ease_out), (0.28, -4.5, ease_in), (0.5, -3.5), (0.9, 0, back_out))(t))
    add(p, "body", rot=(-0.25 * n[0], 0.4 * n[1], 0), pos=(0, 0, push))
    add(p, "neck", rot=(n[0], n[1], 0)); add(p, "skull", rot=(n[0] * 0.6, n[1] * 0.6, -0.3 * n[1])); add(p, "jaw", rot=(j, 0, 0))
    trail(p, t, lambda u: -0.7 * tr((0, (0, 0)), (0.14, (9, -5), ease_out), (0.27, (-15, 1), ease_in), (0.42, (-11, 0)), (0.9, (0, 0), back_out))(u)[1],
          gain=(0.6, 1.0, 1.5, 2.0), delay=0.05)
    alive(p, t, k=0.6)
    return stand(p)


# ------------------------------------------------------------------ the rest of the set, made fluid (06/11)
def alive_upper(p, t, k=1.0, period=3.2, slow=None):
    """the breathing layer without the hips (for poses whose feet step or lie: moving the body would move the feet)"""
    add(p, "neck", rot=(-0.7 * k * wave(t, period, -0.4), 0, 0))
    add(p, "skull", rot=(-0.5 * k * wave(t, period, -0.9), 0, 0))
    add(p, "jaw", rot=(-0.6 * k * max(0.0, wave(t, period, -0.6)), 0, 0))
    for s_, o in SIDES:
        add(p, f"arm_{s_}", rot=(1.6 * k * wave(t, period, -0.8 - o), 0, 0))
        add(p, f"forearm_{s_}", rot=(1.8 * k * wave(t, slow or period * 1.3, -1.4 - o), 0, 0))
    for i in range(1, 5):
        add(p, f"tail{i}", rot=(0.35 * k * i * wave(t, period, -0.45 * i), 1.0 * k * i * wave(t, slow or period * 2.1, -0.7 * i), 0))


def sniff(t):
    """raise the snout into the wind, three quick sniffs with the nostrils, then a look to where the smell is"""
    p = {}
    k = float(tr((0, 0), (0.55, 1, ease_out), (1.6, 1), (2.0, 0.6), (2.5, 0.6), (3.0, 0, ease_in))(t))
    side = float(tr((0, 0), (1.65, 0), (2.05, 1, ease_out), (2.55, 1), (3.0, 0, ease_in))(t))
    sn = sum(math.exp(-((t - c) / 0.07) ** 2) for c in (0.72, 0.98, 1.22))
    add(p, "body", rot=(-1.6 * k, -1.5 * side, 0.8 * side))
    add(p, "neck", rot=(8 * k + 1.0 * sn, 3 * k - 9 * side, 0))
    add(p, "skull", rot=(6 * k + 2.4 * sn, 3 * k - 7 * side, 2.5 * side))
    add(p, "jaw", rot=(-1.0 - 1.2 * sn, 0, 0))
    trail(p, t, lambda u: 1.6 * float(tr((0, 0), (1.65, 0), (2.05, 1, ease_out), (2.55, 1), (3.0, 0, ease_in))(u)), gain=(0.5, 0.9, 1.3, 1.8))
    alive(p, t, k=0.7)
    return stand(p)


def look_back(t):
    """something behind: the head turns first, the chest follows, the hips last; it holds, then comes round again"""
    p = {}
    hk = float(tr((0, 0), (0.45, 0), (0.85, 1, ease_out), (2.2, 1), (2.75, 0, ease_in), (3.2, 0))(t))
    ck = float(tr((0, 0), (0.6, 0), (1.1, 1, ease_out), (2.3, 1), (2.9, 0, ease_in), (3.2, 0))(t))
    add(p, "body", rot=(0, 8 * ck, -2 * ck)); add(p, "neck", rot=(4 * hk, 22 * hk + 10 * ck, -3 * hk))
    add(p, "skull", rot=(2 * hk, 24 * hk, -9 * hk))
    trail(p, t, lambda u: -6 * float(tr((0, 0), (0.6, 0), (1.1, 1, ease_out), (2.3, 1), (2.9, 0, ease_in), (3.2, 0))(u)),
          gain=(0.5, 0.9, 1.3, 1.7), delay=0.1)
    alive(p, t, k=0.9)
    return stand(p)


def shake(t):
    """the shake of a wet dog, from the head to the tail tip: each part starts a little later and dies out"""
    p = {}
    def wob(u, a, d, w=0.42):
        env = math.exp(-((u - 0.9 - d) / w) ** 2)
        return a * env * math.sin(2 * math.pi * 5.2 * (u - d))
    for bone, a, d in (("skull", 15, 0.0), ("neck", 10, 0.05), ("body", 4, 0.11)):
        add(p, bone, rot=(0, 0.4 * wob(t, a, d), wob(t, a, d)))
    for i in range(1, 5):
        add(p, f"tail{i}", rot=(0, wob(t, 2 + 2.2 * i, 0.12 + 0.06 * i), 0.3 * wob(t, 2 + i, 0.12 + 0.06 * i)))
    add(p, "jaw", rot=(-6 * math.exp(-((t - 0.9) / 0.45) ** 2), 0, 0)); add(p, "neck", rot=(6 * window(t, 0.3, 1.5), 0, 0))
    alive(p, t, k=0.6)
    return stand(p)


def yawn(t):
    """lift the head, the jaw opening slowly to its widest with a tremble, a snap shut, a little head shake"""
    p = {}
    up = float(tr((0, 0), (0.6, 1, ease_out), (1.9, 1), (2.3, 0.2), (3.0, 0, ease_out))(t))
    add(p, "neck", rot=(14 * up, 0, 0)); add(p, "skull", rot=(10 * up, 0, -4 * up))
    jaw = float(tr((0, 0), (0.4, -6), (1.3, -52, ease_out), (1.8, -50), (2.0, -2, ease_in), (3.0, 0))(t))
    add(p, "jaw", rot=(jaw + 1.1 * tremor(t, (6.9, 10.2, 4.3)) * window(t, 1.15, 1.85, 0.12), 0, 0))
    add(p, "skull", rot=(0, 1.5 * wob_shake(t, 2.35, 4.0), 5 * wob_shake(t, 2.35, 4.0)))
    for s_, _ in SIDES:
        add(p, f"arm_{s_}", rot=(-10 * up, 0, 0)); add(p, f"forearm_{s_}", rot=(14 * up, 0, 0))
    trail(p, t, lambda u: 2.0 * float(tr((0, 0), (0.6, 1, ease_out), (1.9, 1), (2.3, 0.2), (3.0, 0, ease_out))(u)), gain=(0.5, 0.8, 1.1, 1.4), axis=0, delay=0.1)
    alive(p, t, k=0.6)
    return stand(p)


def wob_shake(t, at, f, w=0.18):
    return math.exp(-((t - at) / w) ** 2) * math.sin(2 * math.pi * f * (t - at))


def stretch(t):
    """the long stretch: head and tail pushed out level, the back hollow, a shiver at the top, then it gathers itself"""
    p = {}
    k = float(tr((0, 0), (0.8, 1, ease_out), (1.8, 1), (2.4, -0.4, ease_in), (3.0, -0.4), (3.6, 0, ease_out))(t))
    a = max(0.0, k); b = max(0.0, -k) / 0.4
    shiv = tremor(t, (7.7, 11.9, 5.1), (0.8, 0.4, 0.3)) * window(t, 1.0, 1.75, 0.2)
    add(p, "body", rot=(-7 * a + 4 * b + 0.3 * shiv, 0, 0), pos=(0, -2 * a, 3 * a))
    add(p, "neck", rot=(-10 * a + 10 * b + 0.6 * shiv, 0, 0)); add(p, "skull", rot=(-8 * a + 6 * b + 0.8 * shiv, 0, 0))
    trail(p, t, lambda u: (lambda kk: 6 * max(0, kk) - 7 * max(0, -kk))(float(tr((0, 0), (0.8, 1, ease_out), (1.8, 1), (2.4, -0.4, ease_in), (3.0, -0.4), (3.6, 0, ease_out))(u))),
          gain=(0.6, 0.8, 1.0, 1.2), axis=0, delay=0.08)
    add(p, "jaw", rot=(-10 * b - 0.6 * shiv, 0, 0))
    for s_, _ in SIDES:
        add(p, f"arm_{s_}", rot=(-25 * a + shiv, 0, 0)); add(p, f"forearm_{s_}", rot=(30 * a + 1.5 * shiv, 0, 0))
    alive(p, t, k=0.5)
    return stand(p)


def threat(t):
    """head low toward the target, the mouth half open and trembling with a growl, one heavy stomp"""
    p = {}
    k = float(tr((0, 0), (0.4, 1, ease_out), (2.0, 1), (2.4, 0, ease_in))(t))
    stomp = float(tr((0, 0), (0.5, 0), (0.9, 1, ease_out), (1.05, 0, ease_in), (2.4, 0))(t))
    jolt = math.exp(-((t - 1.08) / 0.07) ** 2)
    growl = tremor(t, (9.7, 13.1, 6.6), (0.9, 0.5, 0.3)) * window(t, 0.3, 2.0, 0.2)
    add(p, "body", rot=(5 * k + 2 * jolt, 0, -2 * stomp), pos=(0, -3 * k - 1.2 * jolt, 0))
    add(p, "neck", rot=(-8 * k + 0.6 * growl, 0, 0)); add(p, "skull", rot=(-4 * k + 3 * jolt + 0.8 * growl, 0, 0))
    add(p, "jaw", rot=(-12 * k - 6 * jolt - 1.4 * growl, 0, 0))
    trail(p, t, lambda u: 3.0 * math.exp(-((u - 1.08) / 0.12) ** 2), gain=(0.5, 1.0, 1.5, 2.0), axis=0, delay=0.06)
    A.tail(p, t, yaw=2.5 * k, T=0.9, base_pitch=3 * k)
    alive_upper(p, t, k=0.5)
    plant(p, "r"); plant(p, "l", 13 * stomp, -6 * stomp, 0, -10 * stomp, clear=-0.05)
    return p


def stomp(t):
    """lift the foot high, hold a beat over the target, drive it down; the whole body follows the blow"""
    p = {}
    k = float(tr((0, 0), (0.55, 1, ease_out), (0.75, 1), (0.88, 0, ease_in), (1.6, 0))(t))
    jolt = math.exp(-((t - 0.9) / 0.08) ** 2)
    add(p, "body", rot=(-4 * k + 3 * jolt, 0, 4 * k), pos=(0, 2 * k - 2 * jolt, 0))
    add(p, "neck", rot=(-6 * k - 4 * jolt, -6 * k, 0)); add(p, "skull", rot=(-6 * k + 2 * math.exp(-((t - 1.0) / 0.1) ** 2), -4 * k, 0))
    add(p, "jaw", rot=(-8 * jolt, 0, 0))
    trail(p, t, lambda u: 5 * float(tr((0, 0), (0.55, 1, ease_out), (0.75, 1), (0.88, 0, ease_in), (1.6, 0))(u)) - 4 * math.exp(-((u - 0.9) / 0.1) ** 2),
          gain=(0.5, 0.8, 1.1, 1.5), axis=0, delay=0.06)
    alive_upper(p, t, k=0.5)
    plant(p, "l"); plant(p, "r", 22 * k, -12 * k, -10 * k, -12 * k, clear=-0.05)
    return p


def hurt(t):
    """the flinch: a jolt away from the blow, the tail whipping after it, then it gathers itself (no hold)"""
    p = {}
    e = math.exp(-(t / 0.16)) * smooth(t / 0.04)
    add(p, "body", rot=(-6 * e, 6 * e, -4 * e), pos=(0, -1.5 * e, 3 * e))
    add(p, "neck", rot=(12 * e, -8 * e, 0)); add(p, "skull", rot=(8 * e, -6 * e, 6 * e)); add(p, "jaw", rot=(-22 * e, 0, 0))
    trail(p, t, lambda u: -6 * math.exp(-(u / 0.2)) * smooth(u / 0.05), gain=(0.6, 1.0, 1.5, 2.0), delay=0.04)
    trail(p, t, lambda u: 4 * math.exp(-(u / 0.2)) * smooth(u / 0.05), gain=(1.0, 1.0, 1.0, 1.0), axis=0, delay=0.04)
    alive(p, t, k=0.5)
    return stand(p)


def eat(t):
    """head down to the carcass, bite, tear back with a twist, gulp twice; the throat works as it swallows"""
    p = {}
    downf = tr((0, 0), (0.6, 1, ease_out), (1.4, 1), (1.7, 0.45, ease_out), (2.6, 0.45), (3.2, 0, ease_out))
    down = float(downf(t))
    twist = float(tr((0, 0), (1.35, 0), (1.55, 1, ease_out), (1.9, -0.4), (2.2, 0, ease_out))(t))
    add(p, "body", rot=(-8 * down, 2 * twist, 0), pos=(0, -3 * down, 0))
    add(p, "neck", rot=(-34 * down, 16 * twist, 0)); add(p, "skull", rot=(-20 * down, 8 * twist, -12 * twist))
    j = float(tr((0, 0), (0.6, -30, ease_out), (0.9, -32), (1.05, -3, ease_in), (1.9, -3), (2.1, -12), (2.3, -2), (2.5, -12), (2.7, -2), (3.2, 0))(t))
    add(p, "jaw", rot=(j, 0, 0))
    for c in (2.2, 2.75):
        g = math.exp(-((t - c) / 0.1) ** 2)
        add(p, "skull", rot=(7 * g, 0, 0)); add(p, "neck", rot=(-2 * g, 0, 0))
    trail(p, t, lambda u: -3.5 * float(tr((0, 0), (1.35, 0), (1.55, 1, ease_out), (1.9, -0.4), (2.2, 0, ease_out))(u)), gain=(0.6, 1.0, 1.4, 1.9), delay=0.08)
    A.tail(p, t, yaw=0.8, T=3.2, base_pitch=6 * down)
    alive_upper(p, t, k=0.5)
    return stand(p)


def drink(t):
    p = {}
    down = float(tr((0, 0), (0.9, 1, ease_out), (3.0, 1), (3.7, 0, ease_in), (4.0, 0))(t))
    add(p, "body", rot=(-12 * down, 0, 0), pos=(0, -5 * down, 2 * down))
    add(p, "neck", rot=(-31 * down, 0, 0)); add(p, "skull", rot=(-10 * down, 0, 0))
    lap = window(t, 1.1, 2.8, 0.2)
    add(p, "jaw", rot=(-6 * lap * (0.5 + 0.5 * math.sin(2 * math.pi * 2.3 * t)), 0, 0))
    add(p, "skull", rot=(3 * lap * math.sin(2 * math.pi * 2.3 * t - 0.6), 0, 0))
    for c in (3.65, 3.85):
        g = math.exp(-((t - c) / 0.08) ** 2); add(p, "skull", rot=(8 * g, 0, 0))
    A.tail(p, t, yaw=0.9, T=4, base_pitch=8 * down)
    for s_, _ in SIDES:
        add(p, f"arm_{s_}", rot=(10 * down, 0, 0))
    alive_upper(p, t, k=0.4)
    return stand(p)


def _lying_life(p, t, period, k=1.0):
    """a resting animal still breathes deep, flicks the tail tip now and then and settles the head"""
    br = wave(t, period)
    add(p, "body", rot=(1.0 * k * br, 0, 0), pos=(0, 0.45 * k * br, 0))
    add(p, "neck", rot=(-0.7 * k * wave(t, period, -0.5), 0, 0)); add(p, "skull", rot=(-0.4 * k * wave(t, period, -1.0), 0, 0))
    for i in range(1, 5):
        add(p, f"tail{i}", rot=(0, (0.6 + 1.2 * (i - 1)) * k * wave(t, period * 2, -0.9 * i), 0))
    return br


def sit(t):
    p = {}
    A.lie(p, 1.0)
    _lying_life(p, t, 3.0)
    add(p, "neck", rot=(2 * wave(t, 6.0), 4 * wave(t, 6.0, -1), 0)); add(p, "skull", rot=(1.5 * wave(t, 6.0, -0.6), 3 * wave(t, 6.0, -1.6), 0))
    flick = math.exp(-((t - 4.3) / 0.12) ** 2)
    add(p, "tail4", rot=(0, 9 * flick, 0)); add(p, "tail3", rot=(0, 4 * math.exp(-((t - 4.2) / 0.14) ** 2), 0))
    return A.ground_fit(A.S, p)


def sleep(t):
    p = {}
    A.lie(p, 1.0, head_down=1.0)
    br = _lying_life(p, t, 4.0, 1.2)
    add(p, "jaw", rot=(-1.6 * max(0.0, br), 0, 0))
    # a dream twitch now and then: the jaw and a foot
    tw = math.exp(-((t - 5.6) / 0.07) ** 2) + 0.6 * math.exp(-((t - 5.85) / 0.07) ** 2)
    add(p, "jaw", rot=(-3 * tw, 0, 0)); add(p, "toes_r", rot=(-8 * tw, 0, 0)); add(p, "skull", rot=(1.5 * tw, 0, 0))
    return A.ground_fit(A.S, p)


def knocked_out(t):
    """out cold on its side: slow deep breathing, the jaw slack and moving with the breath, a twitch"""
    p = {}
    br = wave(t, 4.0)
    A.lie(p, 0.8)
    add(p, "root", rot=(0, 0, 80))
    add(p, "body", rot=(1.0 * br, 0, 0)); add(p, "neck", rot=(-4 - 0.6 * wave(t, 4.0, -0.6), 0, -14)); add(p, "skull", rot=(-6, 0, -10))
    add(p, "jaw", rot=(-9 - 2.0 * br, 0, 0))
    for i in range(1, 5):
        add(p, f"tail{i}", rot=(0, 0.4 * i * wave(t, 4.0, -0.5 * i), -3))
    for s_, _ in SIDES:
        add(p, f"arm_{s_}", rot=(20 + 1.5 * wave(t, 4.0, -1), 0, 0))
    tw = math.exp(-((t - 2.6) / 0.06) ** 2)
    add(p, "thigh_r", rot=(18 + 3 * tw, 0, 0)); add(p, "shin_r", rot=(10, 0, 0)); add(p, "toes_r", rot=(-10 * tw, 0, 0))
    return A.ground_fit(A.S, p)


def beg(t):
    """eager: looks up at the owner, shifts from foot to foot, snaps the jaw softly, the tail wagging slow"""
    p = _BEG(t)
    alive_upper(p, t, k=0.5, period=2.0, slow=2.0)
    trail(p, t, lambda u: 2.0 * math.sin(2 * math.pi * u / 1.0), gain=(0.6, 1.0, 1.4, 1.8), delay=0.08, loop=2.0)
    return p


def tame(t):
    p = _TAME(t)
    alive_upper(p, t, k=0.4)
    return p


# ------------------------------------------------------------------ new gestures (06/11)
def snort(t):
    """a short snort: the head jerks up and to one side, the jaw pops, a shake of the skull, back (cf. the study: the
    little head-twitch idles keep a standing animal from looking frozen)"""
    p = {}
    k = float(tr((0, 0), (0.28, 0.3, ease_out), (0.42, 1, ease_out), (0.75, 0.8), (1.6, 0, ease_out))(t))
    pop = math.exp(-((t - 0.45) / 0.06) ** 2)
    add(p, "body", rot=(-1.2 * k, 0, 0))
    add(p, "neck", rot=(5 * k, 2 * k, 2 * k)); add(p, "skull", rot=(9 * k + 2 * pop, 3 * k + 3 * wob_shake(t, 0.75, 5.5, 0.14), 6 * k + 6 * wob_shake(t, 0.75, 5.5, 0.14)))
    add(p, "jaw", rot=(-9 * pop - 2 * k, 0, 0))
    trail(p, t, lambda u: 2.5 * math.exp(-((u - 0.5) / 0.2) ** 2), gain=(0.4, 0.8, 1.3, 1.9), delay=0.07)
    alive(p, t, k=0.8)
    return stand(p)


SETTLE_T = 2.6
def settle(t):
    """after standing a while: it shifts its weight over the left foot, lifts the right and sets it down again a little
    further forward and out, rolls back over it; the tail follows every move"""
    p = {}
    w = float(tr((0, 0), (0.55, 1, ease_out), (1.6, 1), (2.2, 0, ease_out), (2.6, 0))(t))
    step = float(tr((0, 0), (0.6, 0), (1.0, 1, ease_out), (1.3, 1), (1.6, 0, ease_in), (2.6, 0))(t))
    land = math.exp(-((t - 1.62) / 0.07) ** 2)
    hroll = 4.5 * w
    add(p, "body", rot=(0.8 * land, -2.5 * w, hroll), pos=(0, -0.6 * land, 0))
    add(p, "neck", rot=(-0.6 * land, 2.0 * w, -0.8 * hroll)); add(p, "skull", rot=(0.8 * math.exp(-((t - 1.7) / 0.1) ** 2), 0.5 * w, -0.2 * hroll))
    trail(p, t, lambda u: 3.5 * float(tr((0, 0), (0.55, 1, ease_out), (1.6, 1), (2.2, 0, ease_out), (2.6, 0))(u)), gain=(0.6, 1.0, 1.4, 1.9), delay=0.09)
    alive_upper(p, t, k=0.8)
    for s_, _ in SIDES:
        add(p, f"thigh_{s_}", rot=(0, 2.5 * w, -hroll))
    plant(p, "l")
    lift = 8.0 * math.sin(math.pi * min(1.0, max(0.0, (t - 0.6) / 1.0))) ** 2      # 0 at 0.6 s and 1.6 s, up between
    plant(p, "r", lift, -4 * smooth((t - 0.6) / 0.9), 8 * step, -14 * step, clear=-0.05)
    return p


SCAN_T = 5.0
def scan(t):
    """a slow scan of the horizon: the head rises, sweeps from one side to the other with two little holds (looking),
    the chest following, and comes back"""
    p = {}
    up = float(tr((0, 0), (0.6, 1, ease_out), (4.3, 1), (5.0, 0, ease_out))(t))
    yw = float(tr((0, 0), (0.6, 0), (1.4, -22, ease_out), (2.0, -20), (3.0, 18, ease_out), (3.7, 20), (4.4, 0, ease_out), (5.0, 0))(t))
    add(p, "body", rot=(-1.5 * up, 0.15 * yw, 0)); add(p, "neck", rot=(6 * up, 0.45 * yw, 0)); add(p, "skull", rot=(4 * up, 0.5 * yw, -0.1 * yw))
    trail(p, t, lambda u: -0.15 * float(tr((0, 0), (0.6, 0), (1.4, -22, ease_out), (2.0, -20), (3.0, 18, ease_out), (3.7, 20), (4.4, 0, ease_out), (5.0, 0))(u)),
          gain=(0.6, 1.0, 1.4, 1.8), delay=0.12)
    alive(p, t, k=0.9)
    return stand(p)


_DEATH, _WAKE, _WAKE_SLEEP, _SWIM = A.death, A.wake, A.wake_sleep, A.swim


def death(t):
    """the old fall, then life leaving slowly: two last breaths that fade, the tail tip twitching and going still"""
    p = _DEATH(t)
    fade = 1.0 - smooth((t - 1.6) / 1.3)
    for c, a in ((1.75, 1.0), (2.4, 0.55)):
        g = math.exp(-((t - c) / 0.22) ** 2) * a
        add(p, "body", rot=(1.6 * g, 0, 0)); add(p, "jaw", rot=(-3 * g, 0, 0)); add(p, "neck", rot=(-1.0 * g, 0, 0))
    tw = sum(a * math.exp(-((t - c) / 0.06) ** 2) for c, a in ((1.5, 1.0), (1.9, -0.6), (2.5, 0.3)))
    for i in range(1, 5):
        add(p, f"tail{i}", rot=(0, 3.0 * i * tw * fade, 0))
    return p


def wake(t):
    p = _WAKE(t)
    trail(p, t, lambda u: 4.0 * math.exp(-((u - 1.2) / 0.25) ** 2) * math.sin(2 * math.pi * 3 * u), gain=(0.5, 0.9, 1.4, 2.0), delay=0.08)
    alive_upper(p, t, k=0.6)
    return p


def wake_sleep(t):
    p = _WAKE_SLEEP(t)
    trail(p, t, lambda u: 3.5 * math.exp(-((u - 2.0) / 0.25) ** 2) * math.sin(2 * math.pi * 3 * u), gain=(0.5, 0.9, 1.4, 2.0), delay=0.08)
    alive_upper(p, t, k=0.6)
    return p


def swim(t):
    """the swim with a real tail S: each segment later and wider, driving the body"""
    p = _SWIM(t)
    trail(p, t, lambda u: 3.0 * math.sin(2 * math.pi * u / 1.6), gain=(0.6, 1.1, 1.7, 2.4), delay=0.12, loop=1.6)
    return p
