"""Therizinosaurus: the fluid set and its own way of fighting (06/11/2026). Rodrigo: "quase um jogo de luta entre
dinos, cada um com sua animacao unica e fluida... sempre um estudo por tras".

Techniques from the study of the Raxiores T. rex (docs/estudos/08_ANIMACAO_RAXIORES.md): nothing stops, nothing
switches on or off, three beats per action with a settle past the rest, the chain follows with a growing delay,
organic tremor with envelopes, loop periods that divide the loop.

What is its own (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md; page "Terizinossauro: estudo e modelo"):
  * a HEAVY-BELLIED, wide-hipped biped (the pubis turned back, a gut for fermenting leaves, Zanno 2010), slow, on
    four-toed feet: the walk rolls the whole barrel from foot to foot, the belly bounces a beat after each footfall,
    the long neck counters it so the small head floats level, the arm fans sway like heavy cloth and arrive late;
  * the claws (up to ~50 cm) were for display and defence, not for killing or digging (Lautenschlager 2014; Qin et
    al. 2023). So it does not fight like a predator: it never drops the head forward to bite, it keeps the fragile
    head and neck BACK, out of reach, and puts the arms between itself and the rival. Its guard is upright with both
    arms raised forward like a pair of scythes; it shuffles sideways (step and close, the belly too heavy to cross
    the feet); it pivots on one foot; its feint is a BLUFF (the fans flare wide and the chest jumps forward, then it
    pulls back); it blocks with the forearm fan held across like a shield; it gives in by folding the arms to the
    chest, closing the fans and sinking back toward its sitting rest;
  * its signature combo, `claw_slash`: a downward cut with the right hand, a rising backhand with the left, and the
    scissor of both, each on a twist of the barrel body.

Signs: body +x = nose up; neck/skull -x = down; tail pitch + = down, tail yaw + = to its left; a + head yaw looks to
its RIGHT; arm(a = forward and up, f = forearm, h = hand, out = spread sideways).
"""
import math

from anim2 import add, Track, smooth, ease_out, ease_in, back_out
import therianims as A

T = A.T
tr, neck, tail, arm, arms, fold, seat, ground_fit = A.tr, A.neck, A.tail, A.arm, A.arms, A.fold, A.seat, A.ground_fit
window = A.window
TAILS = A.TAILS
SIDES = (("l", 0.0), ("r", 0.5))
SX = {"l": 1, "r": -1}
lin = lambda u: min(1.0, max(0.0, u))


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def tremor(t, f=(7.3, 11.1, 4.7), amp=(1.0, 0.55, 0.35), phase=0.0):
    return sum(a * math.sin(2 * math.pi * fr * t + phase * (i + 1) + 1.3 * i) for i, (fr, a) in enumerate(zip(f, amp)))


def trail(p, t, fn, gain=(0.6, 1.0, 1.4, 1.9), delay=0.07, axis=1, bones=TAILS, loop=None):
    for k, b in enumerate(bones):
        u = t - delay * (k + 1)
        v = fn(u % loop if loop else max(0.0, u)) * gain[k]
        r = [0.0, 0.0, 0.0]; r[axis] = v
        add(p, b, rot=tuple(r))


def fans(p, t, fn, delay=0.08, loop=None, k_out=1.0, k_fwd=0.4):
    """the arm fans follow the trunk late: the upper arm takes fn(t - delay), the forearm and its fan later still"""
    for s, o in SIDES:
        u1 = t - delay; u2 = t - 2 * delay
        g = (lambda u: fn(u % loop if loop else max(0.0, u), s))
        a1, a2 = g(u1), g(u2)
        add(p, f"arm_{s}", rot=(k_fwd * a1[0], 0, SX[s] * k_out * a1[1]))
        add(p, f"forearm_{s}", rot=(k_fwd * a2[0] * 1.2, 0, SX[s] * 0.5 * k_out * a2[1]))


def belly(p, t, k=1.0, period=2.4):
    """the barrel breathes: the belly swells, the gola of feathers lifts, the neck follows a beat later"""
    br = wave(t, period)
    add(p, "body", rot=(0.7 * k * br, 0, 0), pos=(0, 0.5 * k * br, 0))
    neck(p, -0.6 * k * wave(t, period, -0.6))
    add(p, "skull", rot=(-0.4 * k * wave(t, period, -1.1), 0, 0))
    arms(p, 0.9 * k * wave(t, period, -0.8), -1.2 * k * wave(t, period, -1.3))
    return br


def upper(p, t, k=1.0, period=2.4):
    """the breathing without the body (for poses already planted)"""
    neck(p, -0.8 * k * wave(t, period, -0.6), 0.8 * k * wave(t, period * 2, 0.3))
    add(p, "skull", rot=(-0.5 * k * wave(t, period, -1.1), 0, 0))
    arms(p, 1.0 * k * wave(t, period, -0.8), -1.3 * k * wave(t, period, -1.3))
    trail(p, t, lambda u: 1.2 * k * wave(u, period * 2), delay=0.1, loop=period * 2)


def hold_legs(p, roll, yaw=0.0):
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, -yaw, -roll))


# ------------------------------------------------------------------ gaits
def gait(t, Tc, stride, duty, lift, bob, roll_a=6.0, yaw_a=3.0, lean=0.0, drop=0.0, head=0.0, arm_sway=1.0, stance_clear=-0.05,
         neck_k=1.0, out=0.0):
    """the heavy barrel walk: the hips roll onto the planted foot (fast down, slow up), swing with the passing leg, the
    belly drops a beat after each footfall; each thigh cancels the roll so the planted foot stays; the long neck
    counters roll and yaw so the head floats; the fans swing after the trunk"""
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    roll = roll_a * math.sin(w + 0.35 + 0.22 * math.sin(2 * w + 0.7))
    yaw = yaw_a * math.sin(w - 0.2)
    v = math.cos(2 * w - 0.9 + 0.45 * math.sin(2 * w - 0.9))
    add(p, "body", rot=(lean + 1.0 * math.sin(2 * w - 0.4), yaw, roll), pos=(0, -bob * v - 0.6 - drop, 0))
    hold_legs(p, roll, yaw)
    lr = roll_a * math.sin(w + 0.35 - 0.45)
    neck(p, head + neck_k * (0.8 * math.sin(2 * w - 1.2) - 0.5 * lean), neck_k * -0.8 * yaw_a * math.sin(w - 0.7), -0.8 * lr)
    add(p, "skull", rot=(0.6 * math.sin(2 * w - 2.0) - 0.4 * head, -0.3 * yaw_a * math.sin(w - 1.2), -0.25 * lr))
    add(p, "jaw", rot=(-0.6 - 0.6 * math.sin(2 * w - 2.5), 0, 0))
    trail(p, t, lambda u: -1.3 * yaw_a * wave(u, Tc, -0.5), gain=(0.6, 1.0, 1.4, 1.8), delay=0.09, loop=Tc)
    trail(p, t, lambda u: 0.9 * wave(u, Tc / 2, -0.9), gain=(0.5, 0.8, 1.0, 1.2), delay=0.07, axis=0, loop=Tc)
    fans(p, t, lambda u, s: (arm_sway * 3.0 * math.sin(2 * math.pi * u / Tc + (0 if s == "l" else math.pi) - 1.6),
                             arm_sway * (-0.7 * roll_a * SX[s] * math.sin(2 * math.pi * u / Tc + 0.35) + 2.0 * math.sin(4 * math.pi * u / Tc - 1.2)) + out),
         delay=0.1, loop=Tc)
    for s, o in SIDES:
        u = (ph + o) % 1.0
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0
            meta = 30 * smooth(max(0, (st - 0.55) / 0.45)); toe = 0.0; clear = stance_clear
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e
            ly = lift * math.sin(math.pi * min(1, sw * 1.15)) ** 1.3
            meta = 30 * (1 - smooth(sw / 0.5)) - 16 * math.sin(math.pi * sw)
            toe = -24 * math.sin(math.pi * min(1, sw * 1.1)) + 6 * smooth((sw - 0.7) / 0.3)
            clear = 1.2 * math.sin(math.pi * sw) ** 0.5
        T.plant(p, s, ly, dz - 6, meta, toe, clear)
    return p


def walk(t):
    Tc, st, du, li, bo = T.walk_p
    p = gait(t, Tc, st, du, li, bo + 0.4)
    fold(p, 0.8)
    return p


def run(t):
    Tc, st, du, li, bo = T.run_p
    p = gait(t, Tc, st, du, li, bo, roll_a=3.5, yaw_a=2.0, lean=5, drop=2.5, head=-3, arm_sway=0.6, stance_clear=0.2, neck_k=0.8)
    fold(p, 1.0)
    return p


WALK_TIRED_T = 2.8


def walk_tired(t):
    """worn out: slow short steps, the barrel rolling deeper, the neck sagging, the beak open, the arms hanging"""
    p = gait(t, WALK_TIRED_T, 44, 0.68, 5, 1.6, roll_a=7.5, yaw_a=2.5, lean=-2, drop=1.0, head=-10, arm_sway=1.3)
    pant = wave(t, WALK_TIRED_T / 4)
    add(p, "jaw", rot=(-8 - 4 * max(0.0, pant), 0, 0))
    neck(p, -1.5 * wave(t, WALK_TIRED_T / 4, -0.5))
    arms(p, 6, -6, 0, 3)
    return p


# ------------------------------------------------------------------ idle family
IDLE_T = 8.0
LOOK = Track([(0, (0, 0)), (1.1, (0, 0)), (1.7, (6, 18), ease_out), (3.1, (6, 18)), (3.6, (2, -14), ease_out), (5.0, (2, -14)),
              (5.5, (10, 4), ease_out), (7.1, (10, 4)), (7.7, (0, 0), smooth), (8.0, (0, 0))])


def idle(t):
    """never still: the barrel breathes (every 2.67 s), the weight drifts from one foot to the other, the long neck
    looks round on a slow track (the base leads, the skull arrives late), the fans hang and sway after the trunk, a
    tap of the claws of one hand now and then, the short tail an S"""
    p = {}
    Tl = IDLE_T
    br = wave(t, Tl / 3)
    shift = wave(t, Tl, 0.4) + 0.3 * wave(t, Tl / 2, 1.1)
    roll = 2.4 * shift; yaw = -1.2 + 1.4 * shift
    add(p, "body", rot=(0.9 * br, yaw, roll), pos=(0, 0.6 * br - 0.3 * abs(shift), 0))
    hold_legs(p, roll, yaw)
    lp, ly = LOOK(t)
    lag = LOOK(max(0.0, t - 0.18))
    add(p, "neck1", rot=(0.5 * lp - 0.5 * wave(t, Tl / 3, -0.6), 0.45 * ly - 0.6 * yaw, -0.4 * roll))
    add(p, "neck2", rot=(0.3 * lag[0] - 0.3 * wave(t, Tl / 3, -0.9), 0.3 * lag[1], -0.3 * roll))
    add(p, "neck3", rot=(-0.4 * lag[0] + 0.6 * wave(t, Tl / 5, 0.7), 0.25 * lag[1], 0))
    add(p, "skull", rot=(0.4 * lag[0] - 0.4 * wave(t, Tl / 3, -1.2), 0.3 * lag[1], -0.1 * lag[1]))
    add(p, "jaw", rot=(-0.6 - 0.8 * smooth(max(0.0, wave(t, Tl / 3, -0.9))), 0, 0))
    fans(p, t, lambda u, s: (1.6 * wave(u, Tl / 2, -1.0 - 3 * (s == "r")), -1.4 * SX[s] * (2.4 * (wave(u, Tl, 0.4) + 0.3 * wave(u, Tl / 2, 1.1)))
                             + 1.2 * wave(u, Tl / 3, -0.8)), delay=0.12, loop=Tl)
    tap = window(t, 5.0, 6.2, 0.2) * tremor(t, (3.1, 4.4, 2.3), (1.0, 0.4, 0.3))
    add(p, "hand_r", rot=(5 * tap, 0, 0))
    trail(p, t, lambda u: 1.4 * wave(u, Tl, -0.5) + 0.6 * wave(u, Tl / 2, 0.6), delay=0.15, loop=Tl)
    trail(p, t, lambda u: 0.5 * wave(u, Tl / 3, -0.4), gain=(0.5, 0.7, 0.9, 1.1), delay=0.1, axis=0, loop=Tl)
    return T.stand(p)


IDLE_TIRED_T = 3.0


def idle_tired(t):
    """spent: the barrel heaves (four breaths a loop), the beak open, the neck sagging low but the head kept up off the
    ground, the arms hanging forward, the fans limp"""
    p = {}
    Tl = IDLE_TIRED_T
    pant = wave(t, Tl / 4)
    add(p, "body", rot=(-2 + 1.6 * pant, 0, 1.4 * wave(t, Tl, 0.3)), pos=(0, -1.2 + 0.9 * pant, 0))
    hold_legs(p, 1.4 * wave(t, Tl, 0.3))
    neck(p, -14 - 1.6 * wave(t, Tl / 4, -0.6), 2 * wave(t, Tl, 0.6))
    add(p, "skull", rot=(8 - 1.0 * wave(t, Tl / 4, -1.1), 0, 0))
    add(p, "jaw", rot=(-9 - 5 * max(0.0, wave(t, Tl / 4, -0.4)), 0, 0))
    arms(p, 8 + 1.5 * wave(t, Tl / 4, -0.9), -8, 0, -2)
    trail(p, t, lambda u: 1.0 * wave(u, Tl, -0.6), delay=0.12, loop=Tl)
    tail(p, pitch=3)
    return T.stand(p)


# ------------------------------------------------------------------ strikes, in three beats
# attack: the cut lands at ~0.55 s (the arm comes through the target between 0.48 and 0.6)
ATK = [(0, 0), (0.34, 0.95, ease_out), (0.41, 1.0), (0.49, 0.6, ease_in), (0.58, -0.2, lin), (0.7, -0.5, ease_out), (0.88, -0.35), (1.2, 0, back_out)]


def slash(t, side, keys, power=1.0, look=True):
    """one cut with one hand: anticipation (the barrel twists away, the arm rises high and back, the fans open, the
    neck draws the head back out of reach), the cut (down and across, the body twisting into it), the follow-through
    (the arm passes low across the body) and the settle"""
    p = {}
    sx = SX[side]
    r = float(Track(keys)(t)) * power
    up, dn = max(0.0, r), max(0.0, -r)
    hit = next(k[0] for k in keys[1:] if k[1] < 0)
    add(p, "body", rot=(6 * up - 4 * dn, sx * (9 * up - 12 * dn), sx * (-3 * up + 4 * dn)), pos=(0, 0.8 * up - 1.0 * dn, 1.5 * up - 2.5 * dn))
    neck(p, 8 * up - 4 * dn, sx * (6 * up - 6 * dn))
    add(p, "skull", rot=(-4 * up, 0, 0))
    arm(p, side, 125 * up - 40 * dn, -24 * up + 10 * dn, -12 * up + 8 * dn, 24 * up - 16 * dn, twist=-10 * dn)
    other = "l" if side == "r" else "r"
    arm(p, other, 20 * (up + dn), 12, 6, 14 * up + 6 * dn)
    jolt = math.exp(-((t - hit) / 0.06) ** 2)
    add(p, "jaw", rot=(-4 * jolt, 0, 0))
    trail(p, t, lambda u: -sx * 7 * float(Track(keys)(u)) * power, delay=0.06)
    return p


def attack(t):
    p = slash(t, "r", ATK)
    belly(p, t, 0.5, 1.2)
    return T.stand(p)


SCISSOR = [(0, 0), (0.4, 1, ease_out), (0.47, 1.05), (0.54, 0.65, ease_in), (0.63, -0.2, lin), (0.75, -0.5, ease_out), (0.95, -0.35), (1.4, 0, back_out)]


def scissor_pose(t, keys, power=1.0):
    p = {}
    k = float(Track(keys)(t)) * power
    up, dn = max(0.0, k), max(0.0, -k)
    hit = next(k[0] for k in keys[1:] if k[1] < 0)
    add(p, "body", rot=(10 * up - 4 * dn, 0, 0), pos=(0, 2 * up, -3 * dn))
    neck(p, 8 * up - 6 * dn, 0)
    add(p, "skull", rot=(-5 * up, 0, 0))
    clash = math.exp(-((t - hit) / 0.05) ** 2)
    for s, _ in SIDES:
        arm(p, s, 80 * up + 30 * dn, -10, -10 + 6 * clash, 62 * up - 34 * dn)
    trail(p, t, lambda u: 4 * float(Track(keys)(u)) * power, gain=(0.5, 0.8, 1.0, 1.2), delay=0.07, axis=0)
    return p


def scissor(t):
    p = scissor_pose(t, SCISSOR)
    belly(p, t, 0.5, 1.4)
    return T.stand(p)


def shove(t):
    """at close range: it rocks back (anticipation), drives the chest and the full belly forward, and settles"""
    p = {}
    k = float(tr((0, 0), (0.28, -0.55, ease_out), (0.45, 1, ease_in), (0.58, 1.05), (0.8, 0.2, ease_out), (1.0, 0, smooth))(t))
    add(p, "body", rot=(-7 * k, 0, 0), pos=(0, -1.6 * abs(k), -7 * k))
    neck(p, 10 * max(0.0, k) - 6 * max(0.0, -k), 0)
    fold(p, 0.6)
    trail(p, t, lambda u: 4 * float(tr((0, 0), (0.28, -0.55, ease_out), (0.45, 1, ease_in), (0.58, 1.05), (0.8, 0.2, ease_out),
                                       (1.0, 0, smooth))(u)), gain=(0.5, 0.8, 1.0, 1.2), axis=0, delay=0.05)
    upper(p, t, 0.4, 1.0)
    return T.stand(p)


# claw_slash: right cut at 0.55 s, left backhand at 1.1 s, the scissor at 1.75 s
SLASH_T = 2.6
CS_R = [(0, 0), (0.34, 0.95, ease_out), (0.41, 1.0), (0.49, 0.6, ease_in), (0.58, -0.2, lin), (0.68, -0.5, ease_out), (0.8, -0.3), (1.05, 0.0, smooth), (2.6, 0)]
CS_L = [(0, 0), (0.55, 0), (0.85, 0.75, ease_out), (0.96, 0.8), (1.04, 0.45, ease_in), (1.12, -0.2, lin), (1.2, -0.55, ease_out), (1.38, -0.3), (1.6, 0, smooth), (2.6, 0)]
CS_X = [(0, 0), (1.15, 0), (1.52, 1, ease_out), (1.6, 1.05), (1.67, 0.65, ease_in), (1.76, -0.2, lin), (1.88, -0.5, ease_out), (2.1, -0.3), (2.6, 0, back_out)]


def claw_slash(t):
    """the combo: a downward cut with the right hand, a rising backhand across with the left on the twist back, then
    both arms wide and the scissor; between the blows the arms never stop, the barrel swinging under them"""
    p = {}
    for part in (slash(t, "r", CS_R), slash(t, "l", CS_L), scissor_pose(t, CS_X)):
        for b, e in part.items():
            add(p, b, rot=tuple(e[0]), pos=tuple(e[1]))
    belly(p, t, 0.6, 1.3)
    blow = window(t, 1.95, 2.55, 0.15)
    add(p, "jaw", rot=(-3 * blow, 0, 0))
    return T.stand(p)


# ------------------------------------------------------------------ the common set, its own way
GUARD_T = 2.4


def guard(t):
    """upright and wary: the trunk raised, the long neck drawn back into an S so the small head is out of reach, both
    arms raised forward like a pair of scythes, the blades pointing at the rival, one hand a little higher and the two
    trading places slowly; the fans half open and quivering; the weight rocking"""
    p = {}
    Tg = GUARD_T
    rock = wave(t, Tg)
    q = tremor(t, (17 / Tg, 26 / Tg, 11 / Tg), (0.7, 0.4, 0.3))
    add(p, "body", rot=(10 + 1.2 * wave(t, Tg / 2, -0.4), 1.2 * wave(t, Tg, 0.6), 1.6 * rock), pos=(0, 1.2 + 0.4 * wave(t, Tg / 2), 1.0))
    hold_legs(p, 1.6 * rock, 1.2 * wave(t, Tg, 0.6))
    add(p, "neck1", rot=(14 + 0.8 * wave(t, Tg / 2, -0.8), 0, -1.2 * rock))
    add(p, "neck2", rot=(-6, 1.5 * wave(t, Tg, 1.0), 0))
    add(p, "neck3", rot=(-10 + 0.6 * wave(t, Tg / 2, -1.2), 0, 0))
    add(p, "skull", rot=(-4, 1.0 * wave(t, Tg, 1.6), 0))
    alt = wave(t, Tg, 0.3)
    for s, _ in SIDES:
        h = 1 if s == "l" else -1
        arm(p, s, 46 + 8 * h * alt, -16 + 4 * h * alt, -6, 26 + 2.0 * q)
        add(p, f"hand_{s}", rot=(1.2 * tremor(t, (13 / Tg, 19 / Tg, 8 / Tg), (0.6, 0.4, 0.3), phase=h), 0, 0))
    trail(p, t, lambda u: 1.6 * wave(u, Tg, -0.6), delay=0.1, loop=Tg)
    tail(p, pitch=-3)
    for s, _ in SIDES:
        add(p, f"thigh_{s}", rot=(0, 0, 2.5 * SX[s]))
    T.plant(p, "l", 0.0, 3.0)
    T.plant(p, "r", 0.0, -3.0)
    return p


STRAFE_T = 2.0


def strafe(t, side):
    """the side shuffle of a heavy belly: the lead foot steps out to the side, the body rolls over it, the trailing
    foot closes up (it never crosses its feet); the arms stay raised toward the rival, the fans swinging with the roll"""
    d = 1.0 if side == "left" else -1.0
    ph = (t / STRAFE_T) % 1.0; w = 2 * math.pi * ph; p = {}
    lead, trail_ = ("l", "r") if d > 0 else ("r", "l")
    # 0..0.35: the lead foot out; 0.5..0.85: the trailing foot closes
    def step(u0, u):
        x = (u - u0) / 0.35
        return 0.0 if x <= 0 or x >= 1 else math.sin(math.pi * x)
    def prog(u0, u):
        return smooth((u - u0) / 0.35)
    lead_out = prog(0.0, ph) * (1 - prog(0.5, ph))     # how far the lead foot is out (it returns as the body passes over)
    shift = smooth(ph / 0.45) * (1 - smooth((ph - 0.5) / 0.45))
    roll = -d * (1.5 + 3.0 * shift) + 1.0 * math.sin(2 * w)
    add(p, "body", rot=(8, 2 * d, roll), pos=(0, 0.6 - 0.6 * math.cos(2 * w - 0.4), 0.5))
    hold_legs(p, roll)
    neck(p, 6 + 1.0 * math.sin(2 * w - 1.0), 6 * d, 0.6 * roll)
    add(p, "skull", rot=(-3, -2 * d, 0))
    for s, _ in SIDES:
        arm(p, s, 38, -12, -4, 22)
    fans(p, t, lambda u, s: (0.0, -2.5 * d * SX[s] * math.sin(2 * math.pi * u / STRAFE_T * 2 - 0.4)), delay=0.1, loop=STRAFE_T)
    trail(p, t, lambda u: -d * (2.5 + 1.5 * math.sin(4 * math.pi * u / STRAFE_T - 0.8)), delay=0.09, loop=STRAFE_T)
    zl = 9.0 * lead_out
    zt = 9.0 * (prog(0.5, ph) * (1 - prog(1.0, ph))) * 0.0
    add(p, f"thigh_{lead}", rot=(0, 0, SX[lead] * zl))
    add(p, f"thigh_{trail_}", rot=(0, 0, -SX[trail_] * 5.0 * step(0.5, ph)))
    T.plant(p, lead, 6.0 * step(0.0, ph) ** 1.2, 0.0, 8 * step(0.0, ph), -14 * step(0.0, ph), clear=0.8 * step(0.0, ph) ** 0.5 - 0.05 * (step(0.0, ph) == 0))
    T.plant(p, trail_, 5.0 * step(0.5, ph) ** 1.2, 0.0, 8 * step(0.5, ph), -14 * step(0.5, ph), clear=0.8 * step(0.5, ph) ** 0.5 - 0.05 * (step(0.5, ph) == 0))
    _ = zt
    return p


def strafe_left(t): return strafe(t, "left")
def strafe_right(t): return strafe(t, "right")


TURN_T = 2.2


def turn(t, side):
    """the pivot of a wide-hipped biped: it plants the inside foot and walks the outside foot round it in two short
    steps; the long neck leads well into the turn, the barrel follows, the fans swing out on the outside"""
    d = 1.0 if side == "left" else -1.0
    lead = -d                                         # a + yaw looks right, so a left turn leads with - yaw
    inside, outside = ("l", "r") if d > 0 else ("r", "l")
    ph = (t / TURN_T) % 1.0; w = 2 * math.pi * ph; p = {}
    roll = 2.0 * math.sin(2 * w + 0.4)
    add(p, "body", rot=(0.6 * math.sin(2 * w), lead * (4.0 + 1.5 * math.sin(2 * w - 0.5)), roll), pos=(0, -0.6 - 0.5 * math.cos(2 * w - 0.8), 0))
    hold_legs(p, roll)
    neck(p, 1.0 * math.sin(2 * w - 1.4), lead * (16 + 3 * math.sin(2 * w - 1.0)), -0.6 * roll)
    add(p, "skull", rot=(0, lead * (5 + 1.5 * math.sin(2 * w - 1.6)), 0))
    fans(p, t, lambda u, s: (2.0 * math.sin(4 * math.pi * u / TURN_T - 1.0), (3.0 if s == outside else 0.5) + 2.0 * math.sin(4 * math.pi * u / TURN_T - 1.3)),
         delay=0.1, loop=TURN_T)
    fold(p, 0.6)
    trail(p, t, lambda u: -lead * (4 + 1.5 * math.sin(4 * math.pi * u / TURN_T - 0.9)), delay=0.1, loop=TURN_T)
    # the outside foot takes two steps per loop round the planted inside one, which only shuffles once
    uo = (2 * ph) % 1.0
    so = math.sin(math.pi * min(1.0, uo / 0.45)) if uo < 0.45 else 0.0
    oz = -3.0 * math.cos(math.pi * uo / 0.45) if uo < 0.45 else 3.0 - 6.0 * ((uo - 0.45) / 0.55)
    add(p, f"thigh_{outside}", rot=(0, lead * 6 * so, 0))
    T.plant(p, outside, 7.0 * so ** 1.2, oz, 10 * so, -18 * so, clear=1.0 * so ** 0.5 - 0.05 * (so == 0))
    ui = (ph + 0.5) % 1.0
    si = math.sin(math.pi * min(1.0, ui / 0.3)) if ui < 0.3 else 0.0
    add(p, f"thigh_{inside}", rot=(0, lead * 4 * si, 0))
    T.plant(p, inside, 3.0 * si ** 1.2, 0.0, 4 * si, -8 * si, clear=0.5 * si ** 0.5 - 0.05 * (si == 0))
    return p


def turn_left(t): return turn(t, "left")
def turn_right(t): return turn(t, "right")


FEINT_T = 1.4


def feint(t):
    """the bluff: a gather (the arms drawn in, the barrel rocks back), then the fans FLARE wide and the chest jumps
    forward a step's worth, the claws flashing open, without a cut; it holds a beat and pulls back"""
    p = {}
    k = float(tr((0, 0), (0.25, -0.5, ease_out), (0.42, 1, ease_out), (0.62, 0.95), (1.0, 0.1, smooth), (1.4, 0, smooth))(t))
    up, dn = max(0.0, k), max(0.0, -k)
    add(p, "body", rot=(10 * up - 3 * dn, 0, 0), pos=(0, 1.5 * up - 0.8 * dn, -4 * up + 1.5 * dn))
    neck(p, 6 * up - 4 * dn, 0)
    add(p, "skull", rot=(-6 * up, 0, 0)); add(p, "jaw", rot=(-7 * up, 0, 0))
    flare = tremor(t, (9.2, 13.4, 6.3), (0.8, 0.5, 0.3)) * window(t, 0.4, 0.7, 0.08)
    for s, _ in SIDES:
        arm(p, s, 40 * up + 10 * dn, -14 * up + 30 * dn, -14 * up + 20 * dn, 70 * up - 10 * dn + 3 * flare)
    trail(p, t, lambda u: 3 * float(tr((0, 0), (0.25, -0.5, ease_out), (0.42, 1, ease_out), (0.62, 0.95), (1.0, 0.1, smooth), (1.4, 0, smooth))(u)),
          gain=(0.5, 0.8, 1.0, 1.2), axis=0, delay=0.06)
    upper(p, t, 0.4, 1.4)
    return T.stand(p)


BLOCK_T = 1.0


def block(t):
    """the shield: the near (left) forearm swings across in front of the chest, the fan spread flat like a shield, the
    blades turned out; the barrel twists away from the blow and the neck pulls the head behind the arm; the blow lands
    (0.15 s), it rocks and comes back"""
    p = {}
    k = float(tr((0, 0), (0.12, 1, ease_out), (0.55, 0.9), (1.0, 0, smooth))(t))
    e = math.exp(-max(0.0, t - 0.15) / 0.2) * smooth((t - 0.12) / 0.04)
    add(p, "body", rot=(2 * k, 10 * k + 4 * e, -3 * k - 2 * e), pos=(0, 0, 1.0 * k + 1.5 * e))
    neck(p, 6 * k, 18 * k, 0); add(p, "skull", rot=(-4 * k, 6 * k, 0))
    arm(p, "l", 50 * k, -30 * k, -10 * k, -12 * k - 6 * e, twist=20 * k)
    arm(p, "r", 20 * k, 10 * k, 0, 10 * k)
    add(p, "adult_l", rot=(0, 0, 0))
    trail(p, t, lambda u: -7 * float(tr((0, 0), (0.12, 1, ease_out), (0.55, 0.9), (1.0, 0, smooth))(u)), delay=0.06)
    upper(p, t, 0.4, 1.0)
    return T.stand(p)


RECOIL_T = 1.0


def recoil(t):
    """its cut met a raised arm or a horn: the striking arm is thrown back up and out, the fans ruffle and shiver, the
    barrel rocks back and one foot steps back to catch it"""
    p = {}
    e = math.exp(-max(0.0, t - 0.08) / 0.22) * smooth(t / 0.09)
    ruff = tremor(t, (10.3, 14.9, 6.7)) * math.exp(-max(0.0, t - 0.05) / 0.3) * smooth(t / 0.05)
    add(p, "body", rot=(5 * e, -6 * e, 3 * e), pos=(0, 0, 3 * e))
    neck(p, 8 * e, -8 * e); add(p, "skull", rot=(4 * e, -6 * e, 0))
    arm(p, "r", 60 * e, -20 * e, 10 * e, 30 * e + 2 * ruff)
    arm(p, "l", 10 * e, 0, 0, 10 * e + 1.5 * ruff)
    trail(p, t, lambda u: 6 * math.exp(-max(0.0, u - 0.04) / 0.25) * smooth(u / 0.04), delay=0.05)
    upper(p, t, 0.4, 1.0)
    T.plant(p, "l")
    st = math.sin(math.pi * min(1.0, max(0.0, (t - 0.1) / 0.45)))
    T.plant(p, "r", 6 * st ** 2, 4 * smooth((t - 0.1) / 0.45), 0, -10 * st, clear=-0.05)
    return p


SUBMIT_T = 2.6


def submit(t):
    """it gives in: the arms fold tight to the chest and the fans close, the neck sinks and turns the head away, it
    sinks back halfway toward its sitting rest, small and harmless"""
    p = {}
    k = float(tr((0, 0), (0.7, 1, ease_out), (2.6, 1))(t))
    sink = float(tr((0, 0), (0.5, 0), (1.6, 0.4, smooth), (2.6, 0.42))(t))
    away = float(tr((0, 0), (0.9, 0), (1.7, 1, smooth), (2.6, 1))(t))
    seat(p, sink)
    neck(p, -24 * k, 30 * away, 0); add(p, "skull", rot=(-6 * k, 10 * away, -6 * away))
    arms(p, -4 * k, 30 * k, 20 * k, -8 * k)
    tail(p, pitch=6 * k)
    br = wave(t, 1.3) * smooth((t - 0.6) / 0.4)
    add(p, "body", rot=(0.6 * br, -8 * away, 0))
    return ground_fit(p)


LIE_DOWN_T = 3.0
GET_UP_T = 2.8


def lie_down(t):
    """down onto its rest, sitting on the wide pelvis (Russell & Russell 1993): the weight goes back, the legs fold
    forward under it, the hips touch down with a soft bump, the trunk comes upright and the arms fold in front"""
    p = {}
    k = float(tr((0, 0), (0.3, 0.03), (2.15, 0.97, smooth), (2.3, 1.0, ease_out), (3.0, 1.0))(t))
    seat(p, k)
    land = math.exp(-((t - 2.2) / 0.1) ** 2)
    add(p, "body", rot=(-1.2 * land, 0, 0), pos=(0, -0.5 * land, 0))
    look = window(t, 0.3, 2.0, 0.35)
    neck(p, -8 * look, 0)
    trail(p, t, lambda u: 2.5 * math.exp(-((u - 2.2) / 0.15) ** 2), gain=(0.5, 0.8, 1.0, 1.2), axis=0, delay=0.06)
    upper(p, t, 0.4, 1.3)
    return ground_fit(p)


def get_up(t):
    """up from sitting: the neck swings forward to move the weight over the feet, the legs push, the barrel rises and
    tips forward, a wobble as it finds its balance, the fans swinging"""
    p = {}
    k = float(tr((0, 1.0), (0.35, 1.0), (1.95, 0.03, smooth), (2.1, 0.0, smooth), (2.8, 0.0))(t))
    seat(p, k)
    push = math.exp(-((t - 0.75) / 0.25) ** 2)
    neck(p, -14 * push, 0)
    wob = math.exp(-max(0.0, t - 1.95) / 0.3) * math.sin(2 * math.pi * 2.2 * (t - 1.95)) * smooth((t - 1.85) / 0.1)
    add(p, "body", rot=(0, 0, 2.2 * wob))
    arms(p, 0, 0, 0, 4 * wob)
    trail(p, t, lambda u: -3.0 * math.exp(-max(0.0, u - 1.95) / 0.3) * math.sin(2 * math.pi * 2.2 * (u - 1.95)) * smooth((u - 1.85) / 0.1), delay=0.07)
    upper(p, t, 0.4, 1.2)
    return ground_fit(p)


# ------------------------------------------------------------------ the rest, made fluid
def claw_display(t):
    """the warning: it rears and spreads the arms wide in a rising sweep, the fans opening last; the claws clack three
    times (irregularly, the third the hardest) while the fans shiver; it holds, then lowers"""
    p = {}
    k = float(tr((0, 0), (0.55, 1, back_out), (2.75, 1), (3.4, 0, smooth))(t))
    kl = float(tr((0, 0), (0.7, 1, back_out), (2.85, 1), (3.4, 0, smooth))(t))
    clack = sum(a * math.exp(-((t - c) / 0.07) ** 2) for c, a in ((1.15, 0.8), (1.52, 0.7), (2.0, 1.0)))
    shiv = tremor(t, (8.7, 12.9, 5.8), (0.9, 0.5, 0.3)) * window(t, 0.7, 2.7, 0.3)
    add(p, "body", rot=(16 * k + 0.3 * shiv, 0, 0), pos=(0, 1.5 * k, 0))
    neck(p, 18 * k, 0); add(p, "skull", rot=(-12 * k, 0, 0)); add(p, "jaw", rot=(-6 * k - 3 * clack, 0, 0))
    for s, _ in SIDES:
        arm(p, s, 28 * kl + 8 * clack, -14 * kl + 16 * clack, -10 * kl + 18 * clack, 82 * kl - 22 * clack + 1.8 * shiv)
    trail(p, t, lambda u: -4 * float(tr((0, 0), (0.55, 1, back_out), (2.75, 1), (3.4, 0, smooth))(u)), gain=(0.6, 0.8, 1.0, 1.2), axis=0, delay=0.08)
    belly(p, t, 0.6, 1.7)
    return T.stand(p)


def threat(t):
    """the short warning: a half display with the right arm, the claws clacked once with a shiver of the fan"""
    p = {}
    k = float(tr((0, 0), (0.42, 1, ease_out), (1.55, 1), (2.0, 0, smooth))(t))
    clack = math.exp(-((t - 1.0) / 0.07) ** 2)
    shiv = tremor(t, (9.1, 13.3, 6.0), (0.8, 0.5, 0.3)) * window(t, 0.5, 1.5, 0.2)
    add(p, "body", rot=(8 * k, -3 * k, 0))
    neck(p, 6 * k, 4 * k); add(p, "skull", rot=(-6 * k, 0, 0)); add(p, "jaw", rot=(-4 * clack, 0, 0))
    arm(p, "r", 50 * k, -10 * k + 10 * clack, 10 * clack, 36 * k + 1.5 * shiv)
    arm(p, "l", 20 * k, 10 * k, 0, 16 * k)
    trail(p, t, lambda u: 3 * float(tr((0, 0), (0.42, 1, ease_out), (1.55, 1), (2.0, 0, smooth))(u)), delay=0.08)
    belly(p, t, 0.6, 1.0)
    return T.stand(p)


def hurt(t):
    p = T.hurt(t)
    e = math.exp(-(t / 0.16)) * smooth(t / 0.04)
    fans(p, t, lambda u, s: (20 * math.exp(-(max(0.0, u) / 0.18)) * smooth(u / 0.04), 16 * math.exp(-(max(0.0, u) / 0.2)) * smooth(u / 0.04)),
         delay=0.04, k_fwd=0.6)
    arms(p, 0, 10 * e)
    return p


def _alive(fn, k=0.6, period=2.4):
    def g(t):
        p = fn(t)
        upper(p, t, k, period)
        return p
    g.__doc__ = fn.__doc__
    return g


def sit(t):
    """sitting on the pelvis: the barrel breathes (6 s / 2), a slow look round, the fans settling"""
    p = {}; br = wave(t, 3.0)
    seat(p, 1.0); add(p, "body", rot=(0.8 * br, 0, 0))
    look = float(tr((0, 0), (1.2, 0), (1.7, 1, ease_out), (3.2, 1), (3.8, 0, smooth), (6.0, 0))(t))
    lag = float(tr((0, 0), (1.35, 0), (1.85, 1, ease_out), (3.35, 1), (3.95, 0, smooth), (6.0, 0))(t))
    neck(p, -0.6 * wave(t, 3.0, -0.5), 24 * look); add(p, "skull", rot=(0, 14 * lag, -6 * lag))
    arms(p, 0.8 * wave(t, 3.0, -0.8), -1.0 * wave(t, 3.0, -1.2))
    trail(p, t, lambda u: 1.0 * wave(u, 6.0, 0.3), delay=0.15, loop=6.0)
    return ground_fit(p)


def sleep(t):
    p = {}; br = wave(t, 4.5)
    seat(p, 1.0); A.head_rest(p, 1.0)
    add(p, "body", rot=(-6 + 0.8 * br, 0, 0), pos=(0, 0.3 * br, 0))
    neck(p, -0.5 * wave(t, 4.5, -0.6))
    tw = math.exp(-((t - 6.2) / 0.07) ** 2)
    add(p, "hand_l", rot=(-6 * tw, 0, 0)); add(p, "tail4", rot=(0, 3 * math.exp(-((t - 6.4) / 0.1) ** 2), 0))
    return ground_fit(p)


def brood(t):
    p = {}; br = wave(t, 3.5)
    seat(p, 1.0)
    arms(p, 20, -30, -10, 26 + 1.2 * wave(t, 3.5, -0.8))
    look = wave(t, 7.0)
    neck(p, -10 - 0.6 * br, 20 * look); add(p, "skull", rot=(0, 10 * wave(t, 7.0, -0.4), 0))
    add(p, "body", rot=(0.6 * br, 0, 0))
    return ground_fit(p)


def wake_sleep(t):
    """wakes sitting: the head lifts off the arms, a long breath, it rises (no overshoot below the ground: smooth),
    then a shake of the quills that rings down"""
    p = {}
    hd = float(tr((0, 1), (0.8, 0, ease_out), (2.8, 0))(t))
    up = float(tr((0, 1), (0.8, 1), (2.2, 0, smooth), (2.8, 0))(t))
    seat(p, up); A.head_rest(p, hd)
    add(p, "body", rot=(-6 * hd, 0, 0))
    sh = math.exp(-max(0.0, t - 2.25) / 0.2) * math.sin(2 * math.pi * 5.0 * (t - 2.25)) * smooth((t - 2.15) / 0.1)
    add(p, "body", rot=(0, 0, 2.5 * sh)); arms(p, 0, 0, 0, 8 * abs(sh))
    upper(p, t, 0.4, 1.4)
    return ground_fit(p)


def death(t):
    p = A.death(t)
    fade = 1.0 - smooth((t - 1.6) / 1.2)
    for c, a in ((1.75, 1.0), (2.4, 0.5)):
        g = math.exp(-((t - c) / 0.22) ** 2) * a
        add(p, "body", rot=(1.0 * g, 0, 0)); add(p, "jaw", rot=(-2 * g, 0, 0))
    tw = sum(a * math.exp(-((t - c) / 0.07) ** 2) for c, a in ((1.5, 1.0), (1.95, -0.6)))
    add(p, "hand_r", rot=(-8 * tw * fade, 0, 0))
    return p


browse = _alive(A.browse, 0.5, 2.1)
rival = _alive(A.rival, 0.6, 2.4)
preen = _alive(A.preen, 0.4, 1.9)
eat = _alive(A.eat, 0.5, 1.3)
_beg = _alive(A.beg, 0.4, 0.8)


def beg(t):
    """the old beg tapped the claws at 3 Hz, which does not close a 1.6 s loop (4.8 taps): 2.5 Hz (4 taps) does"""
    p = _beg(t)
    add(p, "hand_r", rot=(8 * (math.sin(2 * math.pi * 2.5 * t) - math.sin(2 * math.pi * 3 * t)), 0, 0))
    return p
tame = _alive(A.tame, 0.5, 1.3)
baby_browse = _alive(A.baby_browse, 0.5, 2.3)
knocked_out = A.knocked_out
wake = _alive(A.wake, 0.4, 1.5)


def swim(t):
    p = A.swim(t)
    trail(p, t, lambda u: 2.0 * wave(u, 1.6, -0.4), delay=0.1, loop=1.6)
    return p
