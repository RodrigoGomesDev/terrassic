"""Deinosuchus: the fluid set and its own way of fighting (06/11/2026). Rodrigo: "quase um jogo de luta entre dinos,
cada um com sua animacao unica e fluida... sempre um estudo por tras".

Techniques from the study of the Raxiores T. rex (docs/estudos/08_ANIMACAO_RAXIORES.md): nothing stops, nothing
switches on or off, three beats per action with a settle past the rest, the chain follows with a growing delay,
organic tremor with envelopes, loop periods that divide the loop.

What is its own (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md; page "Deinossuco: estudo para a 1.8"):
  * it is an ambush animal, not a duellist: bite marks of Deinosuchus on dinosaur bones (Rivera-Sylva et al. 2009;
    Schwimmer 2002) say it took big prey at the water's edge. So its fight is ONE explosive move, the lunge, and the
    death roll; it does not circle or sidestep on land (no guard-and-strafe of a theropod);
  * the living crocodylians give the rest (Garrick & Lang 1977 on their signals): the THREAT is the body raised and
    inflated on straight legs with the jaws gaping and a hiss (gape_threat; its guard is that posture held); the
    FEINT is a short lunge that snaps on nothing and drops back; SUBMISSION is the snout lifted steeply with the jaws
    shut, then it sinks and backs off; after a hard effort it is spent fast (crocodylians tire on land), lying low
    with the mouth open and the throat pumping;
  * on land the high walk: the spine bends side to side with the steps as a wave that runs on down the tail, growing
    toward the tip; the long head is held level against the bend; the turn on the spot is a C-bend of the whole body
    with both ends toward the turn while the feet step round.

Signs: body +x = nose up, +z = roll to its right; neck/skull -x = down; jaw -x = open; tail yaw + = to its left; a +
head yaw looks to its RIGHT; leg(swing + = forward, lift = the foot raised out to the side).
"""
import math

from anim2 import add, Track, smooth, ease_out, ease_in, back_out
import deinoanims as A

tr, f, window = A.tr, A.f, A.window
head, jaw, gape, tail, tail_wave, leg, stance, lie, ground, low_of = (A.head, A.jaw, A.gape, A.tail, A.tail_wave, A.leg, A.stance,
                                                                     A.lie, A.ground, A.low_of)
TAILS = A.TAILS
SIDES = A.SIDES
WHIP = (0.5, 0.75, 1.0, 1.25, 1.5, 1.8)
LEGS = {f"{b}_{s}" for b in ("thigh", "shin", "foot", "toes", "arm", "forearm", "hand") for s in ("l", "r")}
HEADB = {"neck", "head", "skull", "jaw"}
SUPPORT = LEGS | {"body"} | set(TAILS)          # a crocodylian's tail lies on the ground; only the head is left out
lin = lambda u: min(1.0, max(0.0, u))


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def tremor(t, f=(6.3, 8.9, 4.1), amp=(1.0, 0.55, 0.35), phase=0.0):
    """kept under 10 Hz: at 20 fps a faster shiver would alias into a jump"""
    return sum(a * math.sin(2 * math.pi * fr * t + phase * (i + 1) + 1.3 * i) for i, (fr, a) in enumerate(zip(f, amp)))


def trail(p, t, fn, gain=WHIP, delay=0.06, axis=1, bones=TAILS, loop=None):
    for k, b in enumerate(bones):
        u = t - delay * (k + 1)
        v = fn(u % loop if loop else max(0.0, u)) * gain[k]
        r = [0.0, 0.0, 0.0]; r[axis] = v
        add(p, b, rot=tuple(r))


def ground_on(p, bones=None):
    """set the pose down on its support (the legs, the belly and the tail base), then lay the rest of the tail along
    the ground and lift the head clear of it: a tail pressed down by a rearing body or a snout that dips does not
    throw the whole animal up a few pixels (which the old ground-on-the-lowest-point did, frame to frame)"""
    lo = low_of(p, bones or (LEGS | {"body", "tail1"})); add(p, "root", pos=(0, -lo, 0))
    for i in range(1, len(TAILS)):
        for _ in range(40):
            if low_of(p, set(TAILS[i:])) >= -0.1: break
            add(p, TAILS[i], rot=(-0.5, 0, 0))
    for _ in range(40):
        if low_of(p, HEADB) >= -0.1: break
        add(p, "neck", rot=(0.5, 0, 0))
    return p


def throat(p, t, k=1.0, period=4.0):
    """the breath: the flank swells a little, the throat pumps (the jaw floor), the head follows late"""
    br = wave(t, period)
    add(p, "body", rot=(0.25 * k * br, 0, 0), pos=(0, 0.2 * k * (1 + br), 0))
    add(p, "jaw", rot=(-0.6 * k * max(0.0, wave(t, period / 2, -0.8)), 0, 0))
    head(p, 0.4 * k * wave(t, period, -0.9))
    return br


def upper(p, t, k=1.0, period=4.0):
    add(p, "jaw", rot=(-0.6 * k * max(0.0, wave(t, period / 2, -0.8)), 0, 0))
    head(p, 0.5 * k * wave(t, period, -0.9), 0.6 * k * wave(t, period * 2, 0.3))
    trail(p, t, lambda u: 1.2 * k * wave(u, period * 2), delay=0.15, loop=period * 2)


# ------------------------------------------------------------------ gaits
def walk(t):
    """the high walk with the spine's wave running on down the tail, growing to the tip and arriving late; the head
    held level against the bend, the throat breathing"""
    Tc = A.WALK[0]
    p = A.walk(t)
    trail(p, t, lambda u: 3.2 * wave(u, Tc, -1.4), delay=0.08, loop=Tc)
    head(p, 0.5 * wave(t, Tc / 2, -1.0), 1.2 * wave(t, Tc, -0.9))
    add(p, "jaw", rot=(-0.5 * max(0.0, wave(t, Tc / 2, -0.8)), 0, 0))
    return p


def run(t):
    Tc = A.RUNP[0]
    p = A.run(t)
    trail(p, t, lambda u: 4.5 * wave(u, Tc, -1.2), delay=0.05, loop=Tc)
    head(p, 0, 1.0 * wave(t, Tc, -0.8))
    return p


WALK_TIRED_T = 2.0


def walk_tired(t):
    """spent: it drops from the high walk to the belly sprawl, the legs out to the sides, the belly nearly dragging,
    the mouth open, the throat pumping fast"""
    p = A.walk_cycle(t, WALK_TIRED_T, 16, 10, 0.35, 6.0, hd=-2, low=0.0)
    trail(p, t, lambda u: 3.0 * wave(u, WALK_TIRED_T, -1.4), delay=0.1, loop=WALK_TIRED_T)
    add(p, "jaw", rot=(-6 - 3 * max(0.0, wave(t, WALK_TIRED_T / 4, -0.5)), 0, 0))
    add(p, "skull", rot=(4 + 1.0 * wave(t, WALK_TIRED_T / 4, -0.9), 0, 0))
    return p


# ------------------------------------------------------------------ idle family
IDLE_T = 8.0
LOOK = Track([(0, (0, 0)), (1.4, (0, 0)), (2.1, (3, -14), ease_out), (3.4, (3, -14)), (3.9, (1, 11), ease_out), (5.3, (1, 11)),
              (5.8, (-2, 2), ease_out), (7.2, (-2, 2)), (7.8, (0, 0), smooth), (8.0, (0, 0))])


def idle(t):
    """low on the legs, never quite still: the slow breath (every 4 s), the throat pumping, the head turning on a slow
    track (the neck first, the long snout late), a slow open-mouth rest now and then, the tail an S that runs to the
    tip and back"""
    p = {}
    Tl = IDLE_T
    throat(p, t, 1.0, Tl / 2)
    stance(p, 0.55 + 0.03 * wave(t, Tl, 0.4))
    lp, ly = LOOK(t)
    lag = LOOK(max(0.0, t - 0.2))
    add(p, "neck", rot=(0.4 * lp, 0.5 * ly, 0))
    add(p, "skull", rot=(0.6 * lag[0], 0.5 * lag[1], -0.05 * lag[1]))
    g = window(t, 5.9, 7.2, 0.45)
    gape(p, 9 * g)
    add(p, "body", rot=(0, 0.8 * wave(t, Tl, 0.2), 0.5 * wave(t, Tl, 1.0)))
    trail(p, t, lambda u: 2.2 * wave(u, Tl, -0.5) + 0.9 * wave(u, Tl / 2, 0.6), delay=0.2, loop=Tl)
    return ground(p)


IDLE_TIRED_T = 3.0


def idle_tired(t):
    """exhausted on land (crocodylians tire fast): the belly down, the mouth held open, the throat pumping fast, the
    flanks heaving four times a loop"""
    p = {}
    Tl = IDLE_TIRED_T
    pant = wave(t, Tl / 4)
    stance(p, 0.25)
    add(p, "body", rot=(0.6 * pant, 0, 0), pos=(0, 0.4 * pant, 0))
    gape(p, 14 + 3 * max(0.0, wave(t, Tl / 4, -0.6)))
    head(p, -1 + 0.8 * wave(t, Tl / 4, -1.0), 2 * wave(t, Tl, 0.4))
    trail(p, t, lambda u: 1.4 * wave(u, Tl, -0.5), delay=0.15, loop=Tl)
    return ground_on(p)


# ------------------------------------------------------------------ the strike
# lunge: the jaws shut at 0.45 s (as before); the clip is longer only for the settle
LUNGE_T = 1.5


def lunge(t):
    """the ambush from the water's edge in three beats: it sinks and cocks the tail to one side (the coil), then the
    tail sweeps across and drives the front half up and forward, the forelegs reaching, the jaws gaping wide with the
    head tilted to bite sideways; they slam shut at 0.45 s; two short tearing shakes; it drops back past its rest and
    settles, the tail's last sweep dying down to the tip"""
    p = {}
    up = f(tr((0, 0), (0.16, -0.25, ease_out), (0.42, 1, ease_out), (0.6, 0.9), (0.95, 0.15, ease_in), (1.1, -0.08, ease_out),
              (1.5, 0, smooth)), t)
    o = f(tr((0, 0), (0.12, 0.1), (0.36, 1.0, ease_out), (0.42, 1.05), (0.46, 0, ease_in), (0.9, 0.0), (1.05, 0.25, smooth),
             (1.3, 0, smooth)), t)
    shake = sum(a * math.exp(-((t - c) / 0.07) ** 2) for c, a in ((0.6, 1.0), (0.76, -0.7)))
    snap = math.exp(-((t - 0.46) / 0.05) ** 2)
    hi, lo = max(0.0, up), max(0.0, -up)
    stance(p, 0.45 + 0.45 * hi - 0.3 * lo)
    add(p, "body", rot=(13 * hi - 2 * lo + 1.5 * snap, 4 * shake, 3 * shake), pos=(0, 4 * hi - 1.0 * lo, -10 * hi + 1.5 * lo))
    head(p, -8 * hi + 3 * lo, 10 * shake, 10 * hi * window(t, 0.25, 0.9, 0.15) + 6 * shake)
    gape(p, 38 * o)
    sweep = lambda u: -14 * f(tr((0, 0), (0.16, 1, ease_out), (0.38, -1, ease_in), (0.6, -0.6), (1.1, 0.15, smooth), (1.5, 0, smooth)), u)
    trail(p, t, sweep, delay=0.04)
    tail(p, pitch=-3 * hi)
    for s, _ in SIDES:
        leg(p, "f", s, swing=24 * hi, lift=10 * hi)
    return ground_on(p)


FEINT_T = 1.2


def feint(t):
    """the lunge feint: a short burst forward (half a lunge), the jaws snapping shut on nothing at 0.32 s, then it
    drops back quickly and holds low, watching"""
    p = {}
    up = f(tr((0, 0), (0.12, -0.2, ease_out), (0.3, 0.55, ease_out), (0.42, 0.45), (0.7, -0.12, ease_in), (1.2, 0, smooth)), t)
    o = f(tr((0, 0), (0.1, 0.1), (0.26, 0.8, ease_out), (0.32, 0, ease_in), (1.2, 0)), t)
    hi, lo = max(0.0, up), max(0.0, -up)
    stance(p, 0.5 + 0.4 * hi - 0.25 * lo)
    add(p, "body", rot=(8 * hi - 2 * lo, 0, 0), pos=(0, 2 * hi - 0.8 * lo, -6 * hi + 1.5 * lo))
    head(p, -4 * hi, 0)
    gape(p, 30 * o)
    trail(p, t, lambda u: -8 * f(tr((0, 0), (0.12, 1, ease_out), (0.3, -0.8, ease_in), (0.7, 0.2), (1.2, 0, smooth)), u), delay=0.04)
    for s, _ in SIDES:
        leg(p, "f", s, swing=14 * hi, lift=6 * hi)
    upper(p, t, 0.4, 1.2)
    return ground_on(p)


# ------------------------------------------------------------------ threat, guard and the rest of the set
GAPE_T = 2.4


def gape_threat(t):
    """the threat (Garrick & Lang 1977): it rises on straight legs and inflates, the jaws gape wide toward the threat
    and it hisses (the throat shivering in an envelope), the tail curls to the side ready to sweep; then the jaws close
    slowly and it sinks back"""
    p = {}
    k = f(tr((0, 0), (0.45, 1, ease_out), (1.85, 1), (2.4, 0, smooth)), t)
    o = f(tr((0, 0), (0.25, 0), (0.6, 1, ease_out), (1.7, 0.95), (2.25, 0, smooth), (2.4, 0)), t)
    hiss = tremor(t) * window(t, 0.55, 1.75, 0.2)
    stance(p, 0.55 + 0.4 * k)
    add(p, "body", rot=(2 * k + 0.25 * hiss, 0, 0), pos=(0, 1.2 * k, 0))
    head(p, -3 * k, 0)
    gape(p, 32 * o + 0.8 * hiss)
    trail(p, t, lambda u: 10 * f(tr((0, 0), (0.45, 1, ease_out), (1.85, 1), (2.4, 0, smooth)), u), delay=0.07)
    return ground_on(p)


GUARD_T = 2.4


def guard(t):
    """its guard is the threat posture held: up on straight legs, the body puffed, the head low and pointed at the
    rival, the jaws parted, a hiss that comes and goes, the tail curled to the side and twitching, ready to sweep"""
    p = {}
    Tg = GUARD_T
    hiss = tremor(t, (15 / Tg, 21 / Tg, 10 / Tg)) * (0.5 + 0.5 * wave(t, Tg, -0.4)) ** 2
    stance(p, 0.92 + 0.04 * wave(t, Tg, 0.3))
    add(p, "body", rot=(1.5 + 0.4 * wave(t, Tg / 2), 0.8 * wave(t, Tg, 0.8), 0), pos=(0, 1.1 + 0.3 * wave(t, Tg / 2, -0.5), 0))
    head(p, -2 + 0.6 * wave(t, Tg / 2, -1.0), 1.5 * wave(t, Tg, 1.2))
    gape(p, 7 + 3 * max(0.0, wave(t, Tg, -0.4)) + 0.6 * hiss)
    trail(p, t, lambda u: 9 + 3 * wave(u, Tg, -0.6) + 1.5 * wave(u, Tg / 3, 0.4), delay=0.08, loop=Tg)
    return ground_on(p)


TURN_T = 1.6


def turn(t, side):
    """the pivot of a long sprawling body: it bends into a C with the head AND the tail toward the turn and walks the
    feet round, the forefeet into the turn and the hind feet out of it"""
    d = 1.0 if side == "left" else -1.0
    lead = -d                                         # a + yaw looks right, so a left turn leads with - yaw
    ph = (t / TURN_T) % 1.0; w = 2 * math.pi * ph; p = {}
    bend = 6.0 + 1.5 * math.sin(2 * w - 0.6)
    add(p, "body", rot=(0, 0.6 * lead * bend, 0.8 * math.sin(2 * w + 0.4)))
    head(p, 0.6 * math.sin(2 * w - 1.4), lead * (1.6 * bend + 2))
    trail(p, t, lambda u: -lead * (5.0 + 1.6 * math.sin(4 * math.pi * u / TURN_T - 1.0)), delay=0.08, loop=TURN_T)
    for foot, o in A.LATERAL.items():
        s, kind = foot[0], foot[1]
        sx = 1 if s == "l" else -1
        u = (ph + o) % 1.0
        dirn = d * sx * (-1 if kind == "f" else 1)         # left turn: the left forefoot back, the right forefoot forward
        amp = 10.0
        if u < 0.7:
            sw = dirn * (amp - 2 * amp * (u / 0.7)); lf = 0.0
        else:
            e = (u - 0.7) / 0.3
            sw = dirn * (-amp + 2 * amp * (0.5 - 0.5 * math.cos(math.pi * e))); lf = 12 * math.sin(math.pi * e)
        leg(p, kind, s, swing=sw, lift=lf, high=(34 if kind == "h" else 30) * 0.9, knee=6 * lf / 12)
    upper(p, t, 0.4, TURN_T / 2)
    return ground_on(p)


def turn_left(t): return turn(t, "left")
def turn_right(t): return turn(t, "right")


RECOIL_T = 1.0


def recoil(t):
    """knocked back by a kick or a horn: the head thrown up and aside, the jaws gaping, the body slewing round and the
    tail whipping out the other way to catch it; it sinks back down"""
    p = {}
    e = math.exp(-max(0.0, t - 0.04) / 0.22) * smooth(t / 0.04)
    stance(p, 0.6)
    add(p, "body", rot=(3 * e, -8 * e, 4 * e), pos=(0, 0, 3 * e))
    head(p, 10 * e, 16 * e, 6 * e); gape(p, 16 * e)
    trail(p, t, lambda u: 9 * math.exp(-max(0.0, u - 0.04) / 0.25) * smooth(u / 0.04), delay=0.05)
    upper(p, t, 0.4, 1.0)
    return ground_on(p)


SUBMIT_T = 2.8


def submit(t):
    """it gives in the crocodylian way: the snout lifted steeply with the jaws shut (the subordinate's signal), held,
    then it sinks onto its belly and the head comes down, turned away"""
    p = {}
    lift = f(tr((0, 0), (0.6, 1, ease_out), (1.6, 1), (2.3, 0.15, smooth), (2.8, 0.15)), t)
    down = f(tr((0, 0), (1.3, 0), (2.3, 1, smooth), (2.8, 1)), t)
    stance(p, 0.55 * (1 - down) + 0.2)
    lie(p, 0.7 * down)
    head(p, 30 * lift, 12 * down, k=0.55)
    add(p, "body", rot=(4 * lift, -4 * down, 0))
    trail(p, t, lambda u: -6 * f(tr((0, 0), (1.3, 0), (2.3, 1, smooth), (2.8, 1)), u), delay=0.1)
    br = wave(t, 1.4) * smooth((t - 0.5) / 0.4)
    add(p, "body", pos=(0, 0.2 * br, 0))
    return ground_on(p)


LIE_DOWN_T = 2.0
GET_UP_T = 2.2


def lie_down(t):
    """the belly drop: the legs swing out to the sides and it lowers itself (the back half first), the belly meets the
    ground with a soft slap, the chin comes down last and the tail settles"""
    p = {}
    k = f(tr((0, 0), (0.2, 0.05), (1.15, 0.94, ease_in), (1.25, 1.0, ease_out), (2.0, 1.0)), t)
    hind = window(t, 0.15, 1.05, 0.3)
    lie(p, k)
    stance(p, 0.55 * (1 - k))
    add(p, "body", rot=(1.5 * hind, 0, 0))
    land = math.exp(-((t - 1.22) / 0.08) ** 2)
    add(p, "body", pos=(0, -0.3 * land, 0))
    head(p, 2 * window(t, 0.3, 1.3, 0.3) - 1.5 * land)
    trail(p, t, lambda u: 2.5 * math.exp(-((u - 1.22) / 0.15) ** 2), delay=0.06)
    upper(p, t, 0.4, 2.0)
    return ground_on(p)


def get_up(t):
    """up from the belly into the high walk: the head lifts, the forelegs push the front up, the hind legs follow, a
    sway as the tail swings once to balance"""
    p = {}
    k = f(tr((0, 1), (0.3, 1), (1.4, 0.0, smooth), (2.2, 0)), t)
    front = window(t, 0.35, 1.2, 0.3)
    lie(p, k)
    stance(p, 0.55 * (1 - k))
    add(p, "body", rot=(2.0 * front, 0, 0))
    head(p, 4 * window(t, 0.1, 1.2, 0.3))
    sway = math.exp(-max(0.0, t - 1.3) / 0.35) * math.sin(2 * math.pi * 1.6 * (t - 1.3)) * smooth((t - 1.2) / 0.15)
    add(p, "body", rot=(0, 2 * sway, 0))
    trail(p, t, lambda u: -4 * math.exp(-max(0.0, u - 1.3) / 0.35) * math.sin(2 * math.pi * 1.6 * (u - 1.3)) * smooth((u - 1.2) / 0.15), delay=0.07)
    upper(p, t, 0.4, 2.2)
    return ground_on(p)


# ------------------------------------------------------------------ the rest, made fluid
def attack(t):
    """the side snap in three beats: the head swings away and the jaws open (0.18 s), it whips across and shuts hard at
    0.35 s, a short pull back that passes the rest and settles; the tail answers late"""
    p = {}
    o = f(tr((0, 0), (0.18, 1, ease_out), (0.31, 1.05), (0.36, 0, ease_in), (0.85, 0)), t)
    sw = f(tr((0, 0), (0.16, -0.3, ease_out), (0.34, 1, ease_in), (0.5, 0.95), (0.72, -0.08, smooth), (0.85, 0, smooth)), t)
    pull = f(tr((0, 0), (0.36, 0), (0.5, 1, ease_out), (0.85, 0, smooth)), t)
    stance(p, 0.65)
    add(p, "body", rot=(2 * o, 6 * sw, 0), pos=(0, 0, -3 * max(0.0, sw) + 2 * pull))
    head(p, -4 * pull, 18 * sw, 6 * sw)
    gape(p, 34 * o)
    trail(p, t, lambda u: -9 * f(tr((0, 0), (0.16, -0.3, ease_out), (0.34, 1, ease_in), (0.5, 0.95), (0.72, -0.08, smooth),
                                     (0.85, 0, smooth)), u), delay=0.04)
    return ground_on(p)


def _death_roll_raw(t):
    """the roll, grounded on its belly only (no hop as a leg comes round), the head held with the prey, the tail
    trailing the spin"""
    p = {}
    k = window(t, 0.0, 1.8, 0.15)
    spin = f(tr((0, 0), (0.15, 0), (1.65, 720, smooth), (1.8, 720)), t)
    add(p, "body", rot=(0, 0, spin))
    jaw(p, -3 * (1 - k))
    for s, sx in SIDES:
        add(p, f"thigh_{s}", rot=(-40 * k, 0, -20 * k * sx)); add(p, f"arm_{s}", rot=(-50 * k, 0, -20 * k * sx))
    tail(p, yaw=-10 * k)
    trail(p, t, lambda u: 6 * math.sin(math.radians(f(tr((0, 0), (0.15, 0), (1.65, 720, smooth), (1.8, 720)), u)) * 2), delay=0.05)
    head(p, -4 * k)
    return p


def death_roll(t):
    """the roll, set on a smoothed ground line (no hop each time a leg comes round)"""
    p = _death_roll_raw(t)
    add(p, "root", pos=(0, ROLL_LIFT(t), 0))
    return p


def _roll_lift():
    """the lowest point of the roll, smoothed: sampled once, the running maximum over 0.3 s, then eased, so the body
    rides over its tucked legs without a hop"""
    import numpy as np
    ts = np.arange(0, 1.8001, 0.025)
    lows = []
    for t in ts:
        lows.append(-low_of(_death_roll_raw(t)))
    lows = np.array(lows)
    m = np.array([lows[max(0, i - 6):i + 7].max() for i in range(len(lows))])
    g = np.exp(-0.5 * (np.arange(-8, 9) / 3.0) ** 2); g /= g.sum()
    sm = np.convolve(np.pad(m, 8, mode="edge"), g, mode="same")[8:-8]
    return lambda t: float(np.interp(t, ts, sm))


ROLL_LIFT = None


ROLL_LIFT = _roll_lift()


def tail_sweep(t):
    """the body bent like a bow (the wind-up), the tail whipped round from the base to the tip (the base first, the tip
    last, at 0.5 s), the follow-through past and back"""
    p = {}
    swk = [(0, 0), (0.25, -1, ease_out), (0.45, 0.6, ease_in), (0.55, 1.05, ease_out), (0.75, 0.9), (1.0, -0.1, smooth), (1.1, 0, smooth)]
    sw = f(tr(*swk), t)
    stance(p, 0.7)
    add(p, "body", rot=(0, -10 * sw, 0))
    head(p, 2, 14 * sw)
    trail(p, t, lambda u: -20 * f(tr(*swk), u), gain=(0.9, 1.0, 1.1, 1.2, 1.3, 1.4), delay=0.025)
    return ground_on(p)


def bellow(t):
    """the male's bellow: head and tail raised, the back held at the water line, shivering (an organic tremor in
    envelopes, under 10 Hz so it does not alias) so the water dances on it; three calls, each with a throat pump"""
    p = {}
    k = f(tr((0, 0), (0.5, 1, ease_out), (3.4, 1), (4.0, 0, smooth)), t)
    env = sum(window(t, c, c + 0.6, 0.12) for c in (0.8, 1.8, 2.8))
    shiv = tremor(t, (7.9, 9.4, 5.6), (0.8, 0.5, 0.35)) * env
    stance(p, 0.3)
    add(p, "body", rot=(2 * k + 0.3 * shiv, 0, 0), pos=(0, 0.15 * shiv, 0))
    head(p, 16 * k + 0.6 * shiv, 0)
    trail(p, t, lambda u: -8 * f(tr((0, 0), (0.5, 1, ease_out), (3.4, 1), (4.0, 0, smooth)), u), gain=(0.7, 0.85, 1.0, 1.1, 1.2, 1.3), delay=0.08, axis=0)
    jaw(p, -3 * env)
    trail(p, t, lambda u: 0.8 * tremor(u, (6.1, 8.3, 4.4)) * sum(window(u, c, c + 0.6, 0.12) for c in (0.8, 1.8, 2.8)), delay=0.03)
    return ground_on(p)


def head_slap(t):
    """the head raised (wind-up), slapped down so the underside of the jaw smacks the water (0.85 s), a rebound and a
    settle; grounded on the legs so the slap does not lift the body"""
    p = {}
    up = f(tr((0, 0), (0.5, 1, ease_out), (0.72, 1.05), (0.85, -0.3, ease_in), (0.98, -0.2, ease_out), (1.2, 0.08, smooth), (1.5, 0, smooth)), t)
    stance(p, 0.4)
    head(p, 22 * up, 0, k=0.6)
    jaw(p, -2 * max(0.0, up))
    add(p, "body", rot=(1.5 * max(0.0, up), 0, 0))
    trail(p, t, lambda u: 3 * math.exp(-((u - 0.86) / 0.1) ** 2), delay=0.05, axis=0)
    return ground_on(p)


def hurt(t):
    p = {}
    k = f(tr((0, 0), (0.07, 1, ease_out), (0.55, 0, smooth)), t)
    stance(p, 0.6)
    add(p, "body", rot=(2 * k, -8 * k, 4 * k))
    head(p, 6 * k, 16 * k); gape(p, 14 * k)
    trail(p, t, lambda u: 11 * math.exp(-(max(0.0, u) / 0.18)) * smooth(u / 0.05), delay=0.035)
    return ground_on(p)


def float_(t):
    """resting in the water like a log, now closing on itself: every period divides the 5 s loop"""
    p = {}; br = wave(t, 5.0)
    add(p, "body", rot=(0.4 * br, 0, 0), pos=(0, 0.3 * br, 0))
    for s, sx in SIDES:
        leg(p, "h", s, swing=-10, lift=10); leg(p, "f", s, swing=-6, lift=12)
    tail(p, yaw=4)
    trail(p, t, lambda u: 1.6 * wave(u, 5.0, -0.5), delay=0.25, loop=5.0)
    g = window(t, 2.0, 3.6, 0.6)
    head(p, 2 * g, 6 * g)
    return p


def sit(t):
    """flat on the belly at rest; the head lifts a little and turns (an 8 s loop that closes)"""
    p = {}; A.breathe(p, t, 4.0, 0.6)
    lie(p)
    a = window(t, 2.5, 4.5, 0.6)
    lag = window(t, 2.7, 4.7, 0.6)
    add(p, "neck", rot=(1.6 * a, 4.8 * a, 0)); add(p, "skull", rot=(2.4 * lag, 7.2 * lag, 0))
    trail(p, t, lambda u: 1.4 * wave(u, 8.0, -0.4), delay=0.2, loop=8.0)
    return ground(p)


def _alive(fn, k=0.5, period=4.0):
    def g(t):
        p = fn(t)
        upper(p, t, k, period)
        return p
    g.__doc__ = fn.__doc__
    return g


eat = _alive(A.eat, 0.3, 2.4)
beg = _alive(A.beg, 0.4, 1.1)
tame = _alive(A.tame, 0.4, 2.6)
chirp = A.chirp
bask = _alive(A.bask, 0.4, 3.0)
wake_sleep = _alive(A.wake_sleep, 0.4, 2.2)
wake = A.wake
sleep = A.sleep
knocked_out = A.knocked_out
death = A.death


def swim(t):
    p = A.swim(t)
    trail(p, t, lambda u: 2.5 * wave(u, 1.4, -0.6), delay=0.06, loop=1.4)
    return p
