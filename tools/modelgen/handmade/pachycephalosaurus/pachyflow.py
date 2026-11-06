"""Pachycephalosaurus: the fluid set and the duel (06/11/2026). Rodrigo asked for the T. rex's fluidity on the remade
species, "almost a fighting game between dinos, each with its own unique, fluid animation, always with a study behind
it" (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md). The principles are the T. rex's (docs/estudos/08: nothing stops,
nothing switches on or off, three beats per action, the chain follows late, breathing under every action); the poses
are the Pachycephalosaurus' own:
  * the WADDLE carries real weight now: the wide hips roll ~6 deg over each stance leg and yaw with the swinging one,
    the drop after the heel strike is quick and the rise slow, the short neck counters the hips so the dome travels
    level, and the thighs cancel the roll so the planted foot stays put;
  * the tail stays a BEAM (the basket of ossified tendons, Brown & Schlaikjer 1943): it bends only at the root, but
    the beam now arrives late (`beam`), so a turn of the hips swings it after them instead of with them;
  * the dome is its weapon (healed lesions on the domes, Peterson et al. 2013: it butted head-on and to the flank):
    the head-on butt (`attack`) and the side blow (`flank_butt`) are rebuilt in three beats, and the duel set fights
    with the dome: the GUARD carries it low and pointed at the rival, the FEINT dips into the butting line and pulls
    out of it, the BLOCK meets a blow with the dome (it was built to take one), the RECOIL is the head bounced back by
    the other's dome, and SUBMIT turns the dome away and lifts the nose (as in `tame`: no threat).
"""
import math

from anim2 import add, smooth, ease_in, ease_out, back_out, Track
import pachyanims as A

SIDES = A.SIDES
T = A.T
TAILS = A.TAILS
neck, tail, ram, reach, arms, fold, ground_fit = A.neck, A.tail, A.ram, A.reach, A.arms, A.fold, A.ground_fit
STIFF = (1.0, 0.7, 0.12, 0.05, 0.03, 0.02)       # A.tail's weights: the root bends, the rest is one beam


def tr(*keys): return Track(keys)


def window(t, a, b, fade=0.25):
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def tremor(t, f=(7.3, 11.1, 4.7), amp=(1.0, 0.55, 0.35), phase=0.0):
    """an organic shiver: three sines at frequencies that never line up"""
    return sum(a * math.sin(2 * math.pi * fr * t + phase * (i + 1) + 1.3 * i) for i, (fr, a) in enumerate(zip(f, amp)))


def beam(p, t, fn, axis=1, delay=0.06, gain=1.0, loop=None):
    """follow-through on the stiff tail: the root takes fn late, the beam behind it later still (and stiffly)"""
    for k, (b, w) in enumerate(zip(TAILS, STIFF)):
        u = t - delay * (1 + min(k, 2))
        v = fn(u % loop if loop else max(0.0, u)) * w * gain
        r = [0.0, 0.0, 0.0]; r[axis] = v
        add(p, b, rot=tuple(r))


def alive_upper(p, t, k=1.0, period=3.0, slow=None):
    """the breathing layer without the hips (safe on top of planted feet)"""
    add(p, "neck1", rot=(-0.5 * k * wave(t, period, -0.4), 0, 0))
    add(p, "neck2", rot=(-0.3 * k * wave(t, period, -0.7), 0, 0))
    add(p, "skull", rot=(-0.4 * k * wave(t, period, -1.0), 0, 0))
    add(p, "jaw", rot=(-0.5 * k * max(0.0, wave(t, period, -0.6)), 0, 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(1.4 * k * wave(t, period, -0.8 - o), 0, 0))
        add(p, f"forearm_{s}", rot=(1.6 * k * wave(t, (slow or period * 1.3), -1.4 - o), 0, 0))
    for i, (b, w) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0.6 * k * w * wave(t, period, -0.5 - 0.3 * i), 1.2 * k * w * wave(t, (slow or period * 2.1), -0.7 - 0.3 * i), 0))


def alive(p, t, k=1.0, period=3.0):
    """the full breathing layer (the hips too): only where the feet are planted afterwards"""
    br = wave(t, period)
    add(p, "body", rot=(0.6 * k * br, 0, 0), pos=(0, 0.35 * k * br, 0))
    alive_upper(p, t, k, period)
    return br


def landing(x):
    """-1 just after a heel strike, +1 mid-stance: the drop is fast, the rise slow"""
    x %= 1.0
    return -1.0 + 2.0 * smooth(x / 0.28) if x < 0.28 else 1.0 - 2.0 * smooth((x - 0.28) / 0.72)


# ------------------------------------------------------------------ the weighty waddle
def gait(t, Tc, stride, duty, lift, bob, lean=0.0, drop=0.0, head=0.0, roll=6.0, yaw=3.5, stance_clear=-0.05,
         rammed=0.0, splay=2.5, tail_up=0.0, swing=1.0):
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    b2 = landing(2 * ph + 0.06)
    hroll = roll * math.sin(w + 0.25)
    hyaw = yaw * math.sin(w - 0.6)
    add(p, "body", rot=(lean + 1.1 * b2, hyaw, hroll), pos=(0, bob * b2 - 0.4 - drop, 0))
    # the short neck counters the hips; the skull steadies the dome a beat later
    neck(p, head - lean * 0.7 - 1.3 * landing(2 * ph - 0.04), -0.85 * hyaw - 1.2 * swing * math.sin(w - 1.4), -0.8 * hroll)
    add(p, "skull", rot=(-head * 0.3 + 0.9 * landing(2 * ph - 0.12), -0.15 * hyaw + 0.8 * swing * math.sin(w - 2.0),
                         -0.2 * hroll + 0.6 * math.sin(w - 1.2)))
    add(p, "jaw", rot=(-0.6 - 0.6 * max(0.0, landing(2 * ph - 0.2)), 0, 0))
    if rammed: ram(p, rammed)
    # the beam: it swings late after the hips and bobs late after the landing
    for k, (b, wt) in enumerate(zip(TAILS, STIFF)):
        lag = 0.75 + 0.45 * min(k, 2)
        add(p, b, rot=(wt * (tail_up + 1.0 * landing(2 * ph - 0.1 - 0.06 * min(k, 2))), -wt * 3.6 * math.sin(w - 0.6 - lag), 0))
    for s, o in SIDES:
        f = w + o * 2 * math.pi
        add(p, f"arm_{s}", rot=(3.0 * math.sin(f - 2.2) + 1.5 * landing(2 * ph - 0.25), 0, 0))
        add(p, f"forearm_{s}", rot=(3.5 * math.sin(f - 2.9) + 2.0 * landing(2 * ph - 0.35), 0, 0))
    for s, o in SIDES:
        sx = 1 if s == "l" else -1
        u = (ph + o) % 1.0
        sw_ = 0.0 if u < duty else math.sin(math.pi * (u - duty) / (1 - duty))
        add(p, f"thigh_{s}", rot=(0, -hyaw, -hroll + sx * splay * sw_))
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0
            meta = 26 * smooth(max(0, (st - 0.6) / 0.4)); clear = stance_clear
            toe = 6 * (1 - smooth(min(1.0, st / 0.18))) + 8 * smooth(max(0, (st - 0.7) / 0.3))
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e
            ly = lift * math.sin(math.pi * min(1, sw * 1.1)) ** 1.2
            meta = 26 * (1 - smooth(sw / 0.45)) - 16 * math.sin(math.pi * sw)
            toe = -24 * math.sin(math.pi * min(1, sw * 1.1)) + 6 * smooth((sw - 0.75) / 0.25)
            clear = 1.0 * math.sin(math.pi * sw) ** 0.5 + 0.4 * math.sin(math.pi * sw)   # no toe sweeping under between keys
        T.plant(p, s, ly, dz - 2, meta, toe, clear)
    return p


def walk(t):
    return gait(t, *A.WALK)


def run(t):
    """the heavy run: the dome half way down to the butting line, the beam lifted, the hips rolling less"""
    return gait(t, *A.RUN, lean=4, drop=2.5, head=-10, roll=2.6, yaw=2.0, stance_clear=0.2, rammed=0.35, tail_up=-3,
                swing=0.5)


WALK_TIRED_T = 1.5


def walk_tired(t):
    """spent: shorter, slower steps, the hips rolling more (it sways), the head hanging, the beak open panting"""
    p = gait(t, WALK_TIRED_T, 34, 0.68, 5, 1.1, drop=1.0, head=-10, roll=8.0, yaw=3.0, tail_up=2, stance_clear=0.15)
    pant = wave(t, WALK_TIRED_T / 2)
    add(p, "jaw", rot=(-6 - 3 * max(0.0, pant), 0, 0)); add(p, "neck1", rot=(-1.0 * wave(t, WALK_TIRED_T / 2, -0.5), 0, 0))
    return p


# ------------------------------------------------------------------ idle: 8 s, nothing still, nothing in step
IDLE_T = 8.0
LOOK = Track([(0, (0, 0)), (1.2, (0, 0)), (1.8, (3, 18), ease_out), (3.4, (3, 18)), (4.0, (-2, -14), ease_out),
              (5.6, (-2, -14)), (6.4, (0, 0)), (8.0, (0, 0))])


def idle(t):
    p = {}
    Ti = IDLE_T
    br = wave(t, Ti / 3)
    shift = wave(t, Ti, 0.4) + 0.3 * wave(t, Ti / 2, 1.1)
    hroll = 1.4 + 2.2 * shift
    hyaw = -1.2 + 1.2 * shift
    add(p, "body", rot=(0.7 * br - 0.3, hyaw, hroll), pos=(0, 0.35 * br - 0.25 * abs(shift), 0))
    lp, ly = LOOK(t)
    neck(p, lp - 0.6 * wave(t, Ti / 3, -0.6), 0.8 * ly - 0.8 * hyaw + 1.2 * wave(t, Ti / 5, 0.3), -0.8 * hroll)
    add(p, "skull", rot=(0.5 * lp - 0.4 * wave(t, Ti / 3, -1.2) + 0.6 * wave(t, Ti / 5, 1.6), 0.3 * ly, -0.2 * hroll - 0.1 * ly))
    add(p, "jaw", rot=(-0.5 - 1.0 * smooth(max(0.0, wave(t, Ti / 3, -0.9))), 0, 0))
    for k, (b, wt) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(wt * (0.6 * wave(t, Ti / 3, -0.6 - 0.4 * k) - 0.3),
                       wt * (2.0 * wave(t, Ti, -0.95 - 0.5 * k) + 0.8 * wave(t, Ti / 2, 0.6 - 0.6 * k)), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(1.6 * wave(t, Ti / 2, -1.0 - 3 * o) + 0.8 * br, 0, 0))
        add(p, f"forearm_{s}", rot=(2.0 * wave(t, Ti / 2, -1.7 - 3 * o), 0, 0))
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, -hyaw, -hroll))
    T.plant(p, "l")
    T.plant(p, "r", 0.0, -2.0)
    return p


IDLE_TIRED_T = 3.0


def idle_tired(t):
    """after a chase or a clash: the flanks heave fast, the beak hangs open, the dome low, the beam drooping"""
    p = {}
    Ti = IDLE_TIRED_T
    pant = wave(t, Ti / 4)
    add(p, "body", rot=(-2 + 1.6 * pant, 0, 0.8 * wave(t, Ti, 0.3)), pos=(0, -1.0 + 0.6 * pant, 0))
    neck(p, -10 - 1.6 * wave(t, Ti / 4, -0.6), 2.5 * wave(t, Ti, 0.5))
    add(p, "skull", rot=(-3 - 1.0 * wave(t, Ti / 4, -1.2), 1.2 * wave(t, Ti, -0.5), 0))
    add(p, "jaw", rot=(-7 - 4 * max(0.0, wave(t, Ti / 4, -0.4)), 0, 0))
    for k, (b, wt) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(wt * (3.0 + 0.8 * wave(t, Ti / 4, -0.5 - 0.4 * k)), wt * 1.8 * wave(t, Ti, -0.8 - 0.5 * k), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(5 + 2 * wave(t, Ti / 4, -0.8 - o), 0, 0))
    return T.stand(p)


# ------------------------------------------------------------------ turning on the spot: a waddling pivot
# Not the T. rex's slow stepping round: the short-legged, wide-hipped Pachycephalosaurus pivots in quick little
# shuffles, two per foot each loop, the heavy hips rolling hard over each one and the dome swung into the turn
# first; the tail beam swings out the other way in one piece, late.
TURN_T = 1.2


def shuffle(p, ph, s, o, n=2, up=0.32, lift=3.5, dz=1.5):
    """foot s steps n times per loop (phase offset o): a short quick lift, set down, the rest planted"""
    u = (n * (ph + o)) % 1.0
    if u < up:
        sw = u / up
        T.plant(p, s, lift * math.sin(math.pi * sw) ** 1.3, -dz * math.cos(math.pi * sw), 8 * math.sin(math.pi * sw),
                -14 * math.sin(math.pi * sw), clear=0.7 * math.sin(math.pi * sw) ** 0.5)
        return math.sin(math.pi * sw)
    T.plant(p, s, 0.0, dz - 2 * dz * (u - up) / (1 - up))
    return 0.0


def turn(t, side):
    # + yaw swings the head to the animal's RIGHT in game, so a turn to the left leads with - yaw
    d = 1.0 if side == "left" else -1.0
    ph = (t / TURN_T) % 1.0; w = 2 * math.pi * ph; p = {}
    lead = -d
    hroll = 5.0 * math.sin(2 * w + 0.4)                      # it rolls over each of the four shuffles
    add(p, "body", rot=(0.6 * math.cos(4 * w), lead * (5.0 + 1.0 * math.sin(2 * w)), hroll), pos=(0, -1.0 + 0.4 * math.cos(4 * w), 0))
    neck(p, -2.0 + 0.8 * math.sin(4 * w - 0.8), lead * (16.0 + 2.5 * math.sin(2 * w - 0.7)), -0.8 * hroll)
    add(p, "skull", rot=(0.6 * math.sin(4 * w - 1.4), lead * 4.0, -0.2 * hroll + lead * 4.0))
    for k, (b, wt) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(wt * 0.8 * math.sin(4 * w - 0.9 - 0.4 * min(k, 2)), wt * (-lead * 9.0 - 2.0 * math.sin(2 * w - 1.0 - 0.5 * min(k, 2))), 0))
    arms(p, 2.5 * math.sin(4 * w - 2.0))
    for s, o in SIDES:
        add(p, f"thigh_{s}", rot=(0, -lead * 4.0, -hroll))
        shuffle(p, ph, s, o / 2)
    return p


def turn_left(t): return turn(t, "left")
def turn_right(t): return turn(t, "right")


# ------------------------------------------------------------------ the dome: head-on and to the flank
ATTACK_T = 1.0
A_RAM = tr((0, 0), (0.12, 0.15), (0.32, 1.0, ease_out), (0.62, 1.0), (1.0, 0, smooth))
A_DRIVE = tr((0, 0), (0.24, -0.45, ease_out), (0.32, -0.4), (0.42, 1.0, ease_in), (0.5, 0.82), (0.66, 0.15, ease_out), (1.0, 0, back_out))


def attack(t):
    """the butt, in three beats: it rocks back onto its heels with the dome rising (anticipation), drops the head into
    the butting line and drives off both legs (the dome lands at 0.42 s), the whole body jars and the stiff tail flicks
    up, and it settles back past its stance and returns"""
    p = {}
    k = float(A_RAM(t)); drive = float(A_DRIVE(t))
    jolt = math.exp(-((t - 0.44) / 0.045) ** 2)
    ram(p, k)
    add(p, "body", rot=(-3 * max(0, drive) + 4 * max(0, -drive) + 1.5 * jolt, 0, 0), pos=(0, -1.5 * k - 0.6 * jolt, -5 * drive))
    neck(p, -4 * max(0, drive) + 6 * max(0, -drive) + 5 * jolt, 0)
    add(p, "skull", rot=(3 * jolt, 0, 0)); add(p, "jaw", rot=(-3 * jolt, 0, 0))
    beam(p, t, lambda u: -4 * float(A_RAM(u)) - 9 * math.exp(-((u - 0.44) / 0.07) ** 2), axis=0, delay=0.05)
    arms(p, -10 * k)
    alive_upper(p, t, k=0.5)
    T.plant(p, "l", 0, 2, 10 * max(0, drive), 0); T.plant(p, "r", 0, -2, 10 * max(0, drive), 0)
    return p


FLANK_T = 1.0
FLANK_HIT = 0.36
F_SWING = tr((0, 0), (0.28, -0.75, ease_out), (0.36, 1.0, ease_in), (0.44, 1.08), (1.0, 0, back_out))
F_RAM = tr((0, 0), (0.25, 0.75, ease_out), (0.6, 0.75), (1.0, 0, smooth))


def flank_butt(t):
    """the side blow (Carpenter 1997; the flank lesions, Peterson et al. 2013): head down, the neck cocks away and the
    weight goes onto the far foot (anticipation), the dome whips sideways into the flank with a twist of the whole body
    (the hit at 0.36 s), carries through, swings back a little past centre and settles; the beam swings the other way
    late"""
    p = {}
    sw = float(F_SWING(t)); k = float(F_RAM(t))
    jolt = math.exp(-((t - FLANK_HIT - 0.01) / 0.04) ** 2)
    ram(p, k)
    add(p, "body", rot=(0, 9 * sw, 4 * sw), pos=(0, -1.0 * k, 0))
    neck(p, 0, 32 * sw - 6 * jolt, 12 * sw)
    add(p, "skull", rot=(2 * jolt, 9 * sw, 14 * sw))
    beam(p, t, lambda u: -11 * float(F_SWING(u)), delay=0.06)
    arms(p, -6 * k)
    alive_upper(p, t, k=0.5)
    for s in ("l", "r"):
        sx = 1 if s == "l" else -1
        add(p, f"thigh_{s}", rot=(0, -9 * sw, -4 * sw + 2.0 * sx * k))
    T.plant(p, "l"); T.plant(p, "r")
    return p


def hurt(t):
    """the flinch: a jolt away from the blow, the head ducks and twists, the beam jerks up late; it gathers itself"""
    p = {}
    e = math.exp(-t / 0.15) * smooth(t / 0.04)
    add(p, "body", rot=(2 * e, 6 * e, 3 * e), pos=(0, 0, 1.5 * e))
    neck(p, -8 * e, -12 * e); add(p, "skull", rot=(-6 * e, 0, 8 * e)); add(p, "jaw", rot=(-8 * e, 0, 0))
    beam(p, t, lambda u: -6 * math.exp(-u / 0.2) * smooth(u / 0.05), axis=0, delay=0.04)
    beam(p, t, lambda u: 5 * math.exp(-u / 0.2) * smooth(u / 0.05), delay=0.04)
    alive_upper(p, t, k=0.5)
    return T.stand(p)


# ------------------------------------------------------------------ the duel
GUARD_T = 2.0


def guard(t):
    """squared up to a rival: the dome carried low and pointed at it, the neck weaving a little to keep it aimed, the
    weight rocking on a wide staggered stance, the beam up and stiff, a snort now and then"""
    p = {}
    Tg = GUARD_T
    rock = wave(t, Tg)
    snort = math.exp(-((t - 1.3) / 0.06) ** 2)
    ram(p, 0.55 + 0.06 * wave(t, Tg, -0.6))
    add(p, "body", rot=(0.8 * rock, 1.0 * wave(t, Tg, 1.0), 0.8 * wave(t, Tg / 2, 0.4)), pos=(0, -2.0 + 0.4 * rock, -0.6 * rock))
    neck(p, -0.8 * rock + 2 * snort, 3.0 * wave(t, Tg, 1.4), 0)
    add(p, "skull", rot=(0.5 * wave(t, Tg / 2, -0.8) - 2 * snort, 0.8 * wave(t, Tg / 2, 0.3), 0))
    add(p, "jaw", rot=(-0.5 - 2 * snort, 0, 0))
    for k, (b, wt) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(wt * (-4 + 0.6 * wave(t, Tg, -0.5 * k)), wt * 2.0 * wave(t, Tg, -0.8 - 0.5 * min(k, 2)), 0))
    for s, o in SIDES:
        sx = 1 if s == "l" else -1
        add(p, f"arm_{s}", rot=(-8 + 2 * wave(t, Tg, -1 - 3 * o), 0, 0))
        add(p, f"thigh_{s}", rot=(0, 0, 3.0 * sx - 0.6 * wave(t, Tg, 0.4)))
    T.plant(p, "l", 0.0, 2.0)
    T.plant(p, "r", 0.0, -3.0)
    return p


STRAFE_T = 1.2


def strafe(t, side):
    """side = 'left' or 'right' (the animal's). Not a stalking cross-step: it shuffles sideways low and wide, step
    and close, never crossing its short legs, the hips rolling over each step; the dome stays on the rival and is
    tilted to show its side (the dome as a display, Goodwin & Horner 2004), the beam swings out away from the travel"""
    d = 1.0 if side == "left" else -1.0
    ph = (t / STRAFE_T) % 1.0; w = 2 * math.pi * ph; p = {}
    ram(p, 0.4)
    hroll = 4.0 * math.sin(2 * w + 0.3)
    add(p, "body", rot=(0.5 * math.cos(2 * w), 0, -2.5 * d + hroll), pos=(0.8 * d * math.sin(2 * w), -2.4 + 0.5 * math.cos(2 * w), 0))
    neck(p, 0.6 * math.sin(2 * w - 0.8), 0, 2.0 * d - 0.8 * hroll)
    add(p, "skull", rot=(0, 0, -12 * d + 1.5 * math.sin(2 * w - 1.2)))
    for k, (b, wt) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(-3 * wt, wt * (-d * 6.0 - 2.5 * math.sin(2 * w - 1.0 - 0.5 * min(k, 2))), 0))
    arms(p, -8 + 2 * math.sin(2 * w - 2.0))
    for s, o in SIDES:
        sx = 1 if s == "l" else -1
        lead_foot = sx == d
        # the leading foot steps out first (phase 0), the trailing one closes half a loop later; step-close
        off = 0.0 if lead_foot else 0.5
        u = (ph + off) % 1.0
        if u < 0.32:
            sw = u / 0.32; out = d * (-3.0 + 6.0 * smooth(sw))
            add(p, f"thigh_{s}", rot=(0, 0, out - hroll + 2.0 * sx))
            T.plant(p, s, 4.0 * math.sin(math.pi * sw) ** 1.2, 0.0, 6 * math.sin(math.pi * sw), -12 * math.sin(math.pi * sw),
                    clear=0.7 * math.sin(math.pi * sw) ** 0.5)
        else:
            st = (u - 0.32) / 0.68; out = d * (3.0 - 6.0 * st)
            add(p, f"thigh_{s}", rot=(0, 0, out - hroll + 2.0 * sx))
            T.plant(p, s)
    return p


def strafe_left(t): return strafe(t, "left")
def strafe_right(t): return strafe(t, "right")


FEINT_T = 1.0
FN_RAM = tr((0, 0.5), (0.18, 0.95, ease_out), (0.42, 1.0), (0.55, 0.35, ease_out), (1.0, 0.5, smooth))
FN_LUNGE = tr((0, 0), (0.18, 1.6, ease_out), (0.36, -3.8, ease_in), (0.46, -3.4), (1.0, 0, back_out))


def feint(t):
    """the dome dips into the butting line and lunges half a step, stops short with a toss of the head and pulls back
    (testing the other's nerve); from and back to the guard"""
    p = {}
    k = float(FN_RAM(t)); lunge = float(FN_LUNGE(t))
    toss = math.exp(-((t - 0.5) / 0.08) ** 2)
    ram(p, k)
    add(p, "body", rot=(-0.3 * max(0.0, -lunge) + 1.5 * toss, 0, 0), pos=(0, -2.0, lunge))
    neck(p, 5 * toss, 0); add(p, "skull", rot=(4 * toss, 0, 0))
    beam(p, t, lambda u: -3 - 3 * math.exp(-((u - 0.4) / 0.12) ** 2), axis=0, delay=0.06)
    alive_upper(p, t, k=0.5)
    T.plant(p, "l", 0.0, 2.0); T.plant(p, "r", 0.0, -3.0)
    return p


BLOCK_T = 0.8


def block(t):
    """the other's dome comes: it tucks its own dome into the line to take the blow (the thick dome was built for it),
    the impact drives the whole body back half a step, it braces and comes forward again"""
    p = {}
    tuck = float(tr((0, 0.5), (0.1, 1.0, ease_out), (0.4, 1.0), (0.8, 0.5, smooth))(t))
    e = math.exp(-max(0.0, t - 0.1) / 0.18) * smooth((t - 0.08) / 0.04)
    ram(p, tuck)
    add(p, "body", rot=(3 * e, 0, 0), pos=(0, -2.0 - 0.8 * e, 2.5 * e))
    neck(p, 8 * e, 0); add(p, "skull", rot=(-4 * e, 2 * e, 0)); add(p, "jaw", rot=(-4 * e, 0, 0))
    beam(p, t, lambda u: -7 * math.exp(-max(0.0, u - 0.1) / 0.22) * smooth((u - 0.08) / 0.04), axis=0, delay=0.05)
    alive_upper(p, t, k=0.5)
    step = math.sin(math.pi * min(1.0, max(0.0, (t - 0.12) / 0.4)))
    T.plant(p, "l", 0.0, 2.0)
    T.plant(p, "r", 3.5 * step ** 2, -3.0 + 2.5 * smooth((t - 0.12) / 0.4), 0, -8 * step, clear=-0.05)
    return p


RECOIL_T = 0.9


def recoil(t):
    """its butt met the other's dome: the head bounces up and aside, the body jars back, a step back, a shake of the
    dome to clear it"""
    p = {}
    e = math.exp(-max(0.0, t - 0.04) / 0.2) * smooth(t / 0.04)
    wob = math.exp(-max(0.0, t - 0.3) / 0.2) * math.sin(2 * math.pi * 5.0 * (t - 0.3)) * smooth((t - 0.28) / 0.05)
    ram(p, 0.5 * (1 - e))
    add(p, "body", rot=(4 * e, 4 * e, -3 * e), pos=(0, -0.6 * e, 3.0 * e))
    neck(p, 14 * e, 10 * e + 3 * wob, -4 * e)
    add(p, "skull", rot=(6 * e, 6 * wob, -8 * e + 10 * wob)); add(p, "jaw", rot=(-6 * e, 0, 0))
    beam(p, t, lambda u: -6 * math.exp(-max(0.0, u - 0.04) / 0.25) * smooth(u / 0.04), delay=0.05)
    alive_upper(p, t, k=0.5)
    st = math.sin(math.pi * min(1.0, max(0.0, (t - 0.08) / 0.42)))
    T.plant(p, "l")
    T.plant(p, "r", 5 * st ** 2, 3 * smooth((t - 0.08) / 0.42), 0, -10 * st, clear=-0.05)
    return p


SUBMIT_T = 2.2


def submit(t):
    """beaten: it lifts the nose and turns the dome AWAY (the weapon hidden, as when it accepts its owner), the beam
    drops, it crouches and turns aside before it runs"""
    p = {}
    k = float(tr((0, 0), (0.5, 1, ease_out), (2.2, 1))(t))
    turn_ = float(tr((0, 0), (0.7, 0), (1.5, 1, ease_out), (2.2, 1))(t))
    add(p, "body", rot=(-2 * k, 12 * turn_, 0), pos=(0, -2.0 * k, 0))
    neck(p, 10 * k, 16 * turn_ + 6 * k, 0); add(p, "skull", rot=(8 * k, 6 * turn_, -18 * k))
    for k_, (b, wt) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(wt * 5 * k, -wt * 5 * turn_, 0))
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, -12 * turn_, 0))
    alive_upper(p, t, k=0.8)
    return T.stand(p)


# ------------------------------------------------------------------ lying down and getting up
LIE_DOWN_T = 2.4


def lie_down(t):
    """from standing: it looks down where it will lie, the legs fold and the heavy belly settles with a bump, the head
    comes back up"""
    p = {}
    k = float(tr((0, 0), (0.3, 0.04), (1.6, 0.94, ease_in), (1.85, 1.0), (2.4, 1.0))(t))
    look = float(tr((0, 0), (0.4, 1, ease_out), (1.5, 1), (2.4, 0, ease_out))(t))
    land = math.exp(-((t - 1.75) / 0.1) ** 2)
    fold(p, k)
    neck(p, -10 * look - 3 * land, 0); add(p, "skull", rot=(-4 * look + 2 * land, 0, 0))
    add(p, "body", rot=(0.8 * land, 0, 0)); add(p, "jaw", rot=(-2 * land, 0, 0))
    beam(p, t, lambda u: 3.0 * math.exp(-((u - 1.75) / 0.15) ** 2), axis=0, delay=0.06)
    alive_upper(p, t, k=0.5)
    return ground_fit(p)


GET_UP_T = 2.4


def get_up(t):
    """heavy: a first push leaves it half up, the head swings forward for balance, a second push stands it, a wobble"""
    p = {}
    k = float(tr((0, 1.0), (0.4, 1.0), (0.95, 0.5, ease_out), (1.2, 0.5), (1.8, 0.0, ease_out), (2.4, 0.0))(t))
    push = math.exp(-((t - 0.6) / 0.18) ** 2) + math.exp(-((t - 1.4) / 0.18) ** 2)
    fold(p, k)
    neck(p, -10 * push, 0); add(p, "skull", rot=(-4 * push, 0, 0))
    wob = math.exp(-max(0.0, t - 1.8) / 0.25) * math.sin(2 * math.pi * 2.4 * (t - 1.8)) * smooth((t - 1.75) / 0.1)
    add(p, "body", rot=(0, 0, 2.0 * wob))
    beam(p, t, lambda u: -3.0 * math.exp(-max(0.0, u - 1.8) / 0.3) * math.sin(2 * math.pi * 2.4 * (u - 1.8)) * smooth((u - 1.75) / 0.1), delay=0.07)
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


def dome_clash(t):
    """the old clash (the domes meet at 1.65 s, Pachycephalosaurid.CLASH_HIT) with the breath under it and the beam
    following the hit late"""
    p = A.dome_clash(t)
    beam(p, t, lambda u: -6 * math.exp(-((u - 1.65) / 0.08) ** 2), axis=0, delay=0.05)
    alive_upper(p, t, k=0.4)
    return p


NEW = {
    "turn_left": (turn_left, TURN_T, True, "Movimento", "girando no lugar para a esquerda: passos, a cúpula entra na curva primeiro"),
    "turn_right": (turn_right, TURN_T, True, "Movimento", "girando no lugar para a direita"),
    "lie_down": (lie_down, LIE_DOWN_T, False, "Descanso", "deitando (de pé para sentado), a barriga pesada assenta"),
    "get_up": (get_up, GET_UP_T, False, "Descanso", "levantando em dois empurrões, a cabeça à frente"),
    "idle_tired": (idle_tired, IDLE_TIRED_T, True, "Parado", "parado cansado, ofegando, a cúpula baixa"),
    "walk_tired": (walk_tired, WALK_TIRED_T, True, "Movimento", "andando cansado, balançando mais o quadril"),
    "guard": (guard, GUARD_T, True, "Duelo", "em guarda: cúpula baixa apontada para o rival, peso balançando"),
    "strafe_left": (strafe_left, STRAFE_T, True, "Duelo", "anda de lado para a esquerda em volta do rival, a cúpula nele"),
    "strafe_right": (strafe_right, STRAFE_T, True, "Duelo", "anda de lado para a direita em volta do rival"),
    "feint": (feint, FEINT_T, False, "Duelo", "finta: mergulha a cúpula e avança meio passo, para e recua"),
    "block": (block, BLOCK_T, False, "Duelo", "apara a cabeçada com a própria cúpula, recua meio passo"),
    "recoil": (recoil, RECOIL_T, False, "Duelo", "a cabeçada bateu na cúpula do outro: a cabeça quica, um passo atrás"),
    "submit": (submit, SUBMIT_T, False, "Duelo", "perdeu: ergue o focinho, esconde a cúpula, abaixa a cauda e vira"),
}

REPLACED = {
    "idle": idle, "walk": walk, "run": run, "attack": attack, "flank_butt": flank_butt, "hurt": hurt, "dome_clash": dome_clash,
    "dome_display": lively(A.dome_display, 0.5), "warn": lively(A.warn, 0.4), "sniff": lively(A.sniff, 0.3),
    "pluck": lively(A.pluck, 0.4), "eat": lively(A.eat, 0.4), "graze": lively(A.graze, 0.3), "beg": lively(A.beg, 0.4, period=A.ANIMS["beg"][1]),
    "tame": lively(A.tame, 0.4),
}


def rebind(anims):
    """the species' ANIMS with the fluid versions in place (same names, lengths and loops) and the new ones after"""
    out = {n: ((REPLACED[n],) + v[1:]) if n in REPLACED else v for n, v in anims.items()}
    for n, v in NEW.items():
        out.setdefault(n, v)
    return out
