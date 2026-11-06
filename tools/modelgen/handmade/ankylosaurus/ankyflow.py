"""Ankylosaurus: the fluid set and its own duel (06/11/2026). Rodrigo: "quase um jogo de luta entre dinos, cada um com sua
animacao unica e fluida... sempre um estudo por tras".

Techniques from the study of the Raxiores T. rex (docs/estudos/08_ANIMACAO_RAXIORES.md): nothing stops (a breathing
layer under every action), nothing switches on or off (envelopes), three beats per action (anticipation, strike,
settle past the rest and back), the chain follows with a growing delay, organic tremor (non-commensurate sines),
loop periods that divide the loop.

What is its own (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md, page "Anquilossauro 1.5"):
  * it is a low, wide, armoured tank on short legs: it never rears, never lunges, never ducks the head like a biped.
    Its fighting is done with the BACK HALF. The tail base is flexible and the handle is stiffened by ossified tendons
    (Arbour 2009; Arbour & Snively 2009), so the whip is at the root: the base moves first, the stiff handle follows
    late as one piece and the knob arrives last (HANDLE gains, small delays);
  * Zuul crurivastator carries broken and healed spikes on its FLANKS (Arbour et al. 2022): rivals clubbed each other
    on the sides. So its guard is to TURN THE FLANK to the threat, the tail cocked to the other side; it sidesteps by
    crabbing its four splayed feet, keeping the flank presented; it feints with a half swing; it blocks by bracing the
    armoured flank into the blow (legs spread, body sunk); it gives in by laying the club flat on the ground and
    turning the armoured back, the head drawn in;
  * the walk is a four-beat lateral sequence with the broad body rolling onto each planted side (the roll falls fast
    onto the new foot and rises slowly), the head steadied, the club swinging late behind;
  * breathing shows in the flanks (the wide ribcage), not in the neck; tiredness is a fast heave and an open beak.

Signs: body +x = nose up, +z = roll to its right; neck/skull -x = down; jaw -x = open; tail pitch + = down, tail yaw + =
the club toward its left; a + head yaw looks to its RIGHT; thigh/arm z + (left side) = the foot out to the left.
"""
import math

from anim2 import add, smooth, ease_in, ease_out, back_out, Track
import ankyloanims as A

tr, f, window, head, jaw = A.tr, A.f, A.window, A.head, A.jaw
settle, plant_h, plant_f = A.settle, A.plant_h, A.plant_f
_stand = A.stand


def _copy(p):
    return {k: (list(v[0]), list(v[1])) + tuple(v[2:]) for k, v in p.items()}


def stand(p, fore=(0, 0), hind=(0, 0), clear=0.3):
    """stand, but never with a foot hanging: the rest arm is nearly straight, so a body that rises a little (a breath, a
    nose-up pitch) left the forefoot short of the ground and the IK snapped it back a frame later (a 23 deg pop seen in
    the old snort). Here the body is lowered just enough for every foot to reach, which changes smoothly frame to frame."""
    # the body a touch lower than the old stand, so the elbows keep a bend (near straight the IK is singular and a pixel
    # of shoulder height swings the elbow ~20 deg in one frame)
    add(p, "body", pos=(0, -SLACK, 0))
    for _ in range(5):
        q = _copy(p)
        _stand(q, fore, hind, clear)
        lo = max(max(A.low_of(q, A.FORE[s]), A.low_of(q, A.HIND[s])) for s in A.SIDES)
        if lo < 0.06:
            break
        add(p, "body", pos=(0, -(lo + 0.02), 0))
    p.clear(); p.update(q); return p


SLACK = 0.6


A.stand = stand            # the originals (eat, graze, dig, hunker...) look `stand` up at call time: they get it too
lift_head, lift_tail, lie = A.lift_head, A.lift_tail, A.lie
TAILS = A.TAILS
DROP = A.STAND_DROP
SX = {"l": 1, "r": -1}
HANDLE = (1.0, 0.55, 0.14, 0.09, 0.06)      # the whip at the root, the handle stiff (Arbour 2009)
SWAY = (1.0, 0.8, 0.45, 0.3, 0.2)           # a lazy sway at rest: the base carries it
lin = lambda u: min(1.0, max(0.0, u))


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def tremor(t, f=(7.3, 11.1, 4.7), amp=(1.0, 0.55, 0.35), phase=0.0):
    return sum(a * math.sin(2 * math.pi * fr * t + phase * (i + 1) + 1.3 * i) for i, (fr, a) in enumerate(zip(f, amp)))


def trail(p, t, fn, gain=HANDLE, delay=0.05, axis=1, bones=TAILS, loop=None, club=0.0):
    """segment k takes fn(t - k*delay) * gain[k]; `club` adds a last, latest lag on the knob itself"""
    for k, b in enumerate(bones):
        u = t - delay * (k + 1)
        v = fn(u % loop if loop else max(0.0, u)) * gain[k]
        r = [0.0, 0.0, 0.0]; r[axis] = v
        add(p, b, rot=tuple(r))
    if club:                                      # a gain, like the others: the knob lags the handle a little more
        u = t - delay * (len(bones) + 1.5)
        r = [0.0, 0.0, 0.0]; r[axis] = club * fn(u % loop if loop else max(0.0, u))
        add(p, "adult_club", rot=tuple(r))


def flanks(p, t, k=1.0, period=3.6, drop=True):
    """the breath of a barrel-chested animal: the body swells and lifts, the head follows a beat later, the beak parts
    a little on the out-breath"""
    br = wave(t, period)
    add(p, "body", rot=(0.3 * k * br, 0, 0), pos=(0, (-DROP if drop else 0.0) - 0.14 * k * (1 + br), 0))
    head(p, -0.6 * k * wave(t, period, -0.7))
    jaw(p, -0.8 * k * max(0.0, wave(t, period, -1.1)))
    return br


def upper(p, t, k=1.0, period=3.6):
    """the breathing layer without the body (for poses already planted: moving the body would move the feet)"""
    head(p, -0.7 * k * wave(t, period, -0.7), 0.6 * k * wave(t, period * 2, 0.4))
    jaw(p, -0.8 * k * max(0.0, wave(t, period, -1.1)))
    trail(p, t, lambda u: 1.6 * k * wave(u, period * 2), gain=SWAY, delay=0.12, loop=period * 2)


def hold_legs(p, roll):
    """each limb cancels the body's roll, so a planted foot does not slide sideways"""
    for s in ("l", "r"):
        add(p, f"thigh_{s}", rot=(0, 0, -roll)); add(p, f"arm_{s}", rot=(0, 0, -roll))


# ------------------------------------------------------------------ gaits
def walk(t):
    """the four-beat walk with weight: the broad body falls onto each new foot and rises slowly off it, the hips swing
    with the hind leg that passes, the head is steadied a beat late, the handle and club swing behind the base"""
    Tc, stride, duty, lift, bob = A.WALK
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    roll = 4.4 * math.sin(w + 0.4 + 0.22 * math.sin(2 * w + 0.8))
    yaw = 1.6 * math.sin(w - 0.3)
    v = 0.5 + 0.5 * math.cos(2 * w - 0.8 + 0.4 * math.sin(2 * w - 0.8))
    add(p, "body", rot=(0.45 * math.sin(2 * w - 0.5), yaw, roll), pos=(0, -DROP - bob * v, 0))
    hold_legs(p, roll)
    lr = 4.4 * math.sin(w + 0.4 - 0.5 + 0.22 * math.sin(2 * w + 0.3))
    head(p, 0.9 * math.sin(2 * w - 1.9), -0.9 * 1.6 * math.sin(w - 0.9), -0.75 * lr)
    trail(p, t, lambda u: 5.5 * wave(u, Tc, -1.0), gain=(1.0, 0.7, 0.3, 0.2, 0.15), delay=0.08, loop=Tc, club=0.15)
    trail(p, t, lambda u: 0.7 * wave(u, Tc / 2, -0.6), gain=(0.8, 0.5, 0.3, 0.2, 0.1), delay=0.07, axis=0, loop=Tc)
    A.foot_cycle(p, ph, A.LATERAL, stride, duty, lift, lift)
    return settle(lift_tail(lift_head(p, 1.0), 0.6))


def run(t):
    """the trot: short diagonal steps, a bounce, less roll, the handle carried out stiff and bobbing late"""
    Tc, stride, duty, lift, bob = A.TROTP
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    roll = 1.6 * math.sin(w + 0.3)
    add(p, "body", rot=(0.8 + 0.7 * math.sin(2 * w), 0.8 * math.sin(w), roll),
        pos=(0, -DROP - 0.3 - bob * (0.5 + 0.5 * math.cos(2 * w + 0.5 + 0.35 * math.sin(2 * w))), 0))
    hold_legs(p, roll)
    head(p, 2 + 1.2 * math.sin(2 * w - 1.6), -0.5 * math.sin(w - 0.8), -0.8 * math.sin(w - 0.2))
    A.tail(p, pitch=-3, prof=A.SOFT)
    trail(p, t, lambda u: 2.4 * wave(u, Tc, -0.8), gain=(1.0, 0.7, 0.35, 0.2, 0.1), delay=0.05, loop=Tc, club=0.12)
    trail(p, t, lambda u: 1.4 * wave(u, Tc / 2, -0.9), gain=(0.8, 0.6, 0.4, 0.3, 0.2), delay=0.05, axis=0, loop=Tc)
    A.foot_cycle(p, ph, A.TROT, stride, duty, lift, lift)
    return settle(lift_tail(lift_head(p, 1.0), 0.6))


WALK_TIRED_T = 2.4


def walk_tired(t):
    """spent: slower, shorter steps (it is a tank, it tires fast), the head hung low, the beak open, the flanks heaving,
    the club dragging low behind"""
    Tc, stride, duty, lift = WALK_TIRED_T, 24, 0.74, 2.8
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    roll = 5.2 * math.sin(w + 0.4 + 0.25 * math.sin(2 * w + 0.8))
    pant = wave(t, Tc / 4)
    add(p, "body", rot=(-1.0 + 0.5 * pant, 1.4 * math.sin(w - 0.3), roll),
        pos=(0, -DROP - 0.4 - 0.6 * (0.5 + 0.5 * math.cos(2 * w - 0.8)) + 0.25 * pant, 0))
    hold_legs(p, roll)
    head(p, -7 + 0.8 * wave(t, Tc / 4, -0.8), -0.8 * math.sin(w - 0.9), -0.7 * roll)
    jaw(p, -7 - 3 * max(0.0, wave(t, Tc / 4, -0.5)))
    trail(p, t, lambda u: 4.0 * wave(u, Tc, -1.0), gain=(1.0, 0.7, 0.3, 0.2, 0.15), delay=0.1, loop=Tc, club=0.15)
    A.tail(p, pitch=2.0, prof=A.SOFT)
    A.foot_cycle(p, ph, A.LATERAL, stride, duty, lift, lift)
    return settle(lift_tail(lift_head(p, 0.6), 0.4))


# ------------------------------------------------------------------ idle family
IDLE_T = 8.0
LOOK = Track([(0, (0, 0)), (1.3, (0, 0)), (1.9, (5, -15), ease_out), (3.2, (5, -15)), (3.7, (-3, 12), ease_out),
              (5.1, (-3, 12)), (5.6, (-6, 2), ease_out), (7.2, (-6, 2)), (7.8, (0, 0), smooth), (8.0, (0, 0))])


def idle(t):
    """never still: the flanks swell (one breath every 2.67 s), the weight drifts from one side to the other over 8 s,
    the head looks round on a slow track with the neck leading and the beak trailing, a crop now and then, a snuffle
    through the big nasal loops, the tail an S that starts at the root and dies at the knob"""
    p = {}
    T = IDLE_T
    br = flanks(p, t, 1.0, T / 3)
    shift = wave(t, T, 0.4) + 0.3 * wave(t, T / 2, 1.1)
    roll = 1.6 * shift
    add(p, "body", rot=(0, 0.6 * shift, roll))
    hold_legs(p, roll)
    lp, ly = LOOK(t)
    lag = LOOK(max(0.0, t - 0.15))
    add(p, "neck", rot=(0.6 * lp, 0.6 * ly, -0.5 * roll))
    add(p, "skull", rot=(0.4 * lag[0] + 0.5 * wave(t, T / 5, 1.6), 0.4 * lag[1], -0.1 * lag[1]))
    snuff = window(t, 6.2, 7.1, 0.18)
    add(p, "skull", rot=(0.7 * snuff * tremor(t, (6.4, 9.1, 3.9)), 0, 0))
    crop = window(t, 0.35, 0.95, 0.2)
    head(p, -4 * crop); jaw(p, -4 * crop * max(0.0, wave(t, 0.4)))
    trail(p, t, lambda u: 3.0 * wave(u, T, -0.5) + 1.0 * wave(u, T / 2, 0.6), gain=SWAY, delay=0.18, loop=T, club=0.12)
    trail(p, t, lambda u: 0.5 * wave(u, T / 3, -0.4), gain=SWAY, delay=0.12, axis=0, loop=T)
    return stand(p)


IDLE_TIRED_T = 3.0


def idle_tired(t):
    """after a fight or a run: the flanks heave fast (four breaths a loop), the beak hangs open, the head low, the club
    resting near the ground, a slow sag from side to side"""
    p = {}
    T = IDLE_TIRED_T
    pant = wave(t, T / 4)
    add(p, "body", rot=(-0.8 + 0.7 * pant, 0, 1.2 * wave(t, T, 0.3)), pos=(0, -DROP - 0.5 + 0.45 * pant, 0))
    hold_legs(p, 1.2 * wave(t, T, 0.3))
    head(p, -8 - 1.2 * wave(t, T / 4, -0.7), 2.0 * wave(t, T, 0.6), -0.8 * wave(t, T, 0.0))
    jaw(p, -6 - 4 * max(0.0, wave(t, T / 4, -0.5)))
    A.tail(p, pitch=2.5, prof=A.SOFT)
    trail(p, t, lambda u: 1.6 * wave(u, T, -0.6), gain=SWAY, delay=0.14, loop=T)
    return stand(p, clear=0.2)


# ------------------------------------------------------------------ the club, in three beats
def club_curve(t, keys):
    return float(Track(keys)(t))


# club_l / club_r: the hit lands at 0.55 s (Ankylosaurid.SWING_HIT, tick 11)
SWING_KEYS = [(0, 0), (0.34, -0.78, ease_out), (0.42, -0.84), (0.5, -0.2, ease_in), (0.55, 0.78, lin),
              (0.66, 1.12, ease_out), (0.92, 0.78), (1.28, -0.08, smooth), (1.6, 0.0, smooth)]
BRACE_KEYS = [(0, 0), (0.3, 1, ease_out), (1.05, 1), (1.5, 0, smooth), (1.6, 0)]


def swing_pose(t, side, keys, brace_keys, hit, power=1.0, look=True):
    """the swing: anticipation (the weight onto the forefeet, the head turns to the target, the tail wound to the far
    side), the strike (the hips whip round, the base first, the stiff handle late, the knob last), the settle (the
    body twists back past rest and comes home). The body twists AGAINST the tail on the planted forefeet."""
    p = {}
    sw = lambda u: club_curve(u, keys) * side * power
    s = sw(t)
    brace = float(Track(brace_keys)(t))
    jolt = math.exp(-((t - hit) / 0.06) ** 2)
    shud = tremor(t, (9.3, 13.7, 6.1)) * math.exp(-max(0.0, t - hit) / 0.12) * smooth((t - hit + 0.02) / 0.04)
    add(p, "body", rot=(-2.5 * brace, -13 * s, -4 * s + 0.5 * shud * side), pos=(-2.0 * s, -DROP - 0.8 * brace, -1.0 * brace))
    hold_legs(p, -4 * s)
    lk = -12 * side * window(t, 0.05, hit - 0.05, 0.18) if look else 0.0
    head(p, -9 * brace - 2 * jolt, lk + 12 * s, 3 * s)
    jaw(p, -5 * window(t, hit - 0.05, hit + 0.25, 0.08))
    trail(p, t, lambda u: 50 * sw(u), gain=A.BASE, delay=0.025, club=0.05)
    trail(p, t, lambda u: -6 * brace * abs(sw(u)), gain=A.BASE, delay=0.03, axis=0)
    flanks(p, t, 0.5, 1.6, drop=False)
    return p, brace


def club_l(t):
    p, br = swing_pose(t, 1.0, SWING_KEYS, BRACE_KEYS, 0.55)
    return settle(stand(p, fore=(-2 * br, -2 * br)))


def club_r(t):
    p, br = swing_pose(t, -1.0, SWING_KEYS, BRACE_KEYS, 0.55)
    return settle(stand(p, fore=(-2 * br, -2 * br)))


def flank_club(t):
    """two males side by side: two slower blows against the rival's flank, at 0.55 s and 2.05 s; the second follows on
    from the first's settle (no switch between them)"""
    k1 = [(0, 0), (0.34, -0.7, ease_out), (0.42, -0.74), (0.5, -0.2, ease_in), (0.55, 0.6, lin), (0.68, 0.85, ease_out),
          (1.0, 0.4), (1.42, -0.55, smooth), (1.5, -0.7), (1.58, -0.2, ease_in), (2.05, 0.65, smooth), (2.18, 0.86, ease_out),
          (2.55, 0.35), (2.85, -0.05, smooth), (3.0, 0, smooth)]
    bk = [(0, 0), (0.3, 1, ease_out), (2.5, 1), (3.0, 0, smooth)]
    p, br = swing_pose(t, 1.0, k1, bk, 0.55, power=0.6, look=False)
    j2 = math.exp(-((t - 2.05) / 0.06) ** 2)
    add(p, "body", rot=(0, 0, 2 * br - 0.6 * j2))
    head(p, 0, -8 * br, 0)
    return settle(stand(p, fore=(-1.5 * br, -1.5 * br)))


# club_duel: the hit at 1.35 s (tick 27)
DUEL_T = 3.0
DUEL_HIT = 1.35
DUEL_KEYS = [(0, 0), (0.35, -0.12, ease_out), (1.0, -1.18, smooth), (1.14, -1.22), (1.27, -0.35, ease_in), (1.35, 0.8, lin),
             (1.47, 1.18, ease_out), (1.58, 0.96), (1.72, 1.05), (2.3, 0.18, smooth), (2.68, -0.07, smooth), (3.0, 0, smooth)]
DUEL_BRACE = [(0, 0), (0.45, 0.6, ease_out), (1.05, 1.25, smooth), (1.6, 1.25), (2.4, 0.3, smooth), (3.0, 0, smooth)]


def club_duel(t):
    """the duel blow of two rivals, flank to flank (Zuul: the healed broken flank spikes, Arbour et al. 2022): it turns
    its flank, looks back over the shoulder at the rival, coils the whole back half the other way in a long wind-up
    (the forefeet spread wide to brace, the effort trembling in the held tail), then the hips whip round and the knob
    lands on the rival's flank at 1.35 s; it bounces off the armour, the tail rebounds and follows through, the body
    sways back past rest and settles, blowing hard"""
    p, br = swing_pose(t, 1.0, DUEL_KEYS, DUEL_BRACE, DUEL_HIT, look=False)
    over = window(t, 0.25, 1.3, 0.3)
    head(p, 2 * over, -20 * over, -4 * over)                              # the look back at the rival on its left
    held = window(t, 0.95, 1.22, 0.07)
    trail(p, t, lambda u: 2.2 * held * tremor(u, (8.1, 12.3, 5.2)), gain=HANDLE, delay=0.02)
    add(p, "body", rot=(0, 0, 1.5 * over), pos=(0, 0, 0))
    spread = float(Track([(0, 0), (0.6, 1, smooth), (2.2, 1), (3.0, 0, smooth)])(t))
    for s in ("l", "r"):
        add(p, f"arm_{s}", rot=(0, 0, 5 * SX[s] * spread))
    blow = window(t, 1.5, 2.6, 0.2)
    jaw(p, -4 * blow * (0.6 + 0.4 * wave(t, 0.45)))
    return settle(stand(p, fore=(-2.2 * br, -2.2 * br)))


def club_warn(t):
    """the warning: the tail lifted off the ground and swung slowly like a pendulum, the knob arriving late at each end,
    the body low and braced and turned a little so the club faces the threat"""
    p = {}
    k = f(tr((0, 0), (0.45, 1, ease_out), (2.55, 1), (3.0, 0, smooth)), t)
    flanks(p, t, 0.7, 1.5)
    add(p, "body", rot=(-2 * k, 3 * k, 0), pos=(0, -0.8 * k, 0))
    head(p, -8 * k, -3 * k, 0)
    env = window(t, 0.35, 2.7, 0.35)
    pend = lambda u: 20 * wave(u - 0.4, 1.3) * window(u, 0.35, 2.7, 0.35)
    trail(p, t, pend, gain=(1.0, 0.65, 0.3, 0.2, 0.15), delay=0.06, club=0.1)
    A.tail(p, pitch=-10 * k, prof=A.BASE)
    add(p, "skull", rot=(0.5 * env * tremor(t, (6.8, 10.1, 4.4)), 0, 0))
    return settle(stand(p, fore=(-1.5 * k, -1.5 * k)))


# ------------------------------------------------------------------ the common set, its own way
GUARD_T = 2.4


def guard(t):
    """its guard is the flank: the body turned so the armoured left side faces the rival, sunk low on spread legs, the
    head low and turned to watch, the tail lifted and cocked to the right with the knob rocking slowly (the club ready
    to come round), the weight rocking side to side; a snuffle of the nose"""
    p = {}
    T = GUARD_T
    rock = wave(t, T)
    add(p, "body", rot=(-2.2 + 0.4 * wave(t, T / 2), 8 + 1.0 * wave(t, T, 0.6), 1.6 * rock), pos=(-1.0, -DROP - 1.1 + 0.25 * wave(t, T / 2), 0))
    hold_legs(p, 1.6 * rock)
    for s in ("l", "r"):
        add(p, f"arm_{s}", rot=(0, 0, 4 * SX[s])); add(p, f"thigh_{s}", rot=(0, 0, 2.5 * SX[s]))
    head(p, -9 + 0.8 * wave(t, T / 2, -0.8), -16 + 1.5 * wave(t, T, 1.2), -2)
    add(p, "skull", rot=(0.5 * tremor(t, (16 / T, 23 / T, 9 / T)), 0, 0))
    jaw(p, -1.0 - 1.2 * max(0.0, wave(t, T / 2, -1.0)))
    A.tail(p, pitch=-9, prof=A.BASE)
    trail(p, t, lambda u: -16 + 5 * wave(u, T, -0.4), gain=(1.0, 0.65, 0.3, 0.2, 0.15), delay=0.08, loop=T, club=0.1)
    flanks(p, t, 0.6, T / 2, drop=False)
    return settle(stand(p, fore=(-1.5, -1.5)))


STRAFE_T = 2.0


def strafe(t, side):
    """crabbing sideways on the four splayed legs, the flank kept to the rival: a lateral sequence of short side
    steps (each foot lifted only a little, it is heavy), the body leaning into the travel and rolling over each new
    foot, the tail swinging out the other way and arriving late"""
    d = 1.0 if side == "left" else -1.0
    ph = (t / STRAFE_T) % 1.0; w = 2 * math.pi * ph; p = {}
    roll = -1.8 * d + 1.4 * math.sin(2 * w + 0.5)
    add(p, "body", rot=(-1.5, 4 * d, roll), pos=(0.6 * d * math.sin(2 * w), -DROP - 0.9 + 0.3 * math.cos(2 * w), 0))
    hold_legs(p, roll)
    head(p, -6, 10 * d + 1.5 * math.sin(w - 0.6), 0.6 * roll)
    A.tail(p, pitch=-6, prof=A.BASE)
    trail(p, t, lambda u: -10 * d - 3 * math.sin(2 * math.pi * u / STRAFE_T - 0.6), gain=(1.0, 0.65, 0.3, 0.2, 0.15), delay=0.08,
          loop=STRAFE_T, club=0.15)
    flanks(p, t, 0.5, STRAFE_T / 2, drop=False)
    for foot, o in (("lf", 0.0), ("rh", 0.25), ("rf", 0.5), ("lh", 0.75)):
        s, kind = foot[0], foot[1]
        u = (ph + o) % 1.0
        bone = "thigh" if kind == "h" else "arm"
        A_ = 7.0
        if u < 0.3:
            sw = u / 0.3; e = 0.5 - 0.5 * math.cos(math.pi * sw)
            z = d * A_ * (2 * e - 1); ly = 2.6 * math.sin(math.pi * sw); clear = 0.5 * math.sin(math.pi * sw) ** 0.5
        else:
            st = (u - 0.3) / 0.7
            z = d * A_ * (1 - 2 * st); ly = 0.0; clear = -0.05
        add(p, f"{bone}_{s}", rot=(0, 0, z))
        if kind == "h":
            plant_h(p, s, ly, 0.0, 0.0, -6 * ly / 2.6, clear)
        else:
            plant_f(p, s, ly, -1.5, -10 * ly / 2.6, clear)
    return settle(lift_tail(lift_head(p, 0.6), 0.5))


def strafe_left(t): return strafe(t, "left")
def strafe_right(t): return strafe(t, "right")


TURN_T = 2.0


def turn(t, side):
    """turning on the spot the quadruped's way: the forefeet step toward the turn and the hind feet away from it, so
    the broad body pivots round its middle; the head leads into the turn, the club is dragged round late on the
    outside"""
    d = 1.0 if side == "left" else -1.0
    lead = -d                                         # a + yaw looks right, so a left turn leads with - yaw
    ph = (t / TURN_T) % 1.0; w = 2 * math.pi * ph; p = {}
    roll = 1.6 * math.sin(2 * w + 0.4)
    add(p, "body", rot=(0.3 * math.sin(2 * w), lead * (3.0 + 1.0 * math.sin(2 * w - 0.5)), roll),
        pos=(0, -DROP - 0.4 * (0.5 + 0.5 * math.cos(2 * w - 0.8)), 0))
    hold_legs(p, roll)
    head(p, 0.8 * math.sin(2 * w - 1.6), lead * (12 + 2 * math.sin(2 * w - 1.2)), -0.6 * roll)
    trail(p, t, lambda u: -lead * (7 + 2.5 * math.sin(4 * math.pi * u / TURN_T - 1.0)), gain=(1.0, 0.65, 0.3, 0.2, 0.15),
          delay=0.1, loop=TURN_T, club=0.15)
    flanks(p, t, 0.5, TURN_T / 2, drop=False)
    for foot, o in (("lf", 0.0), ("rh", 0.25), ("rf", 0.5), ("lh", 0.75)):
        s, kind = foot[0], foot[1]
        u = (ph + o) % 1.0
        dirn = d if kind == "f" else -d                   # the forefeet step into the turn, the hind feet out of it
        bone = "thigh" if kind == "h" else "arm"
        A_ = 6.0
        if u < 0.3:
            sw = u / 0.3; e = 0.5 - 0.5 * math.cos(math.pi * sw)
            z = dirn * A_ * (2 * e - 1); ly = 3.0 * math.sin(math.pi * sw); clear = 0.5 * math.sin(math.pi * sw) ** 0.5
        else:
            st = (u - 0.3) / 0.7
            z = dirn * A_ * (1 - 2 * st); ly = 0.0; clear = -0.05
        add(p, f"{bone}_{s}", rot=(0, 0, z))
        if kind == "h":
            plant_h(p, s, ly, 0.0, 0.0, -6 * ly / 3.0, clear)
        else:
            plant_f(p, s, ly, 0.0, -12 * ly / 3.0, clear)
    return settle(lift_tail(lift_head(p, 1.0), 0.6))


def turn_left(t): return turn(t, "left")
def turn_right(t): return turn(t, "right")


FEINT_T = 1.5
FEINT_KEYS = [(0, 0), (0.36, -0.82, ease_out), (0.46, -0.86), (0.6, -0.15, ease_in), (0.7, 0.18, ease_out), (0.84, 0.05),
              (1.15, -0.06, smooth), (1.5, 0, smooth)]


def feint(t):
    """the half swing: the full wind-up and the hips start round, but the tail is checked behind it (no blow); the
    rival sees the club coming and flinches. A short grunt of effort as it checks"""
    p, br = swing_pose(t, 1.0, FEINT_KEYS, [(0, 0), (0.3, 1, ease_out), (0.9, 1), (1.4, 0, smooth), (1.5, 0)], 0.62)
    return settle(stand(p, fore=(-2 * br, -2 * br)))


BLOCK_T = 1.0


def block(t):
    """the rival's club meets its flank: it has braced the armoured side into the blow, legs spread and the body sunk,
    so the hit is a shove: the body is knocked a little sideways and rolls with it, the head draws in, the tail flicks
    out to balance; the armour takes it and it comes back up"""
    p = {}
    pre = smooth(t / 0.12)
    e = math.exp(-max(0.0, t - 0.14) / 0.24) * smooth((t - 0.04) / 0.1)
    wob = math.exp(-max(0.0, t - 0.15) / 0.2) * math.sin(2 * math.pi * 3.2 * (t - 0.15)) * smooth((t - 0.12) / 0.05)
    sink = pre * (1 - smooth((t - 0.6) / 0.4))
    roll = -5 * e + 1.2 * wob
    add(p, "body", rot=(-1.5 * sink, 3 * e, roll), pos=(-2.0 * e, -DROP - 1.2 * sink, 0))
    hold_legs(p, roll)
    for s in ("l", "r"):
        add(p, f"arm_{s}", rot=(0, 0, 4 * SX[s] * sink)); add(p, f"thigh_{s}", rot=(0, 0, 2 * SX[s] * sink))
    head(p, -6 * sink - 4 * e, 6 * e, 3 * e)
    jaw(p, -4 * e)
    trail(p, t, lambda u: 14 * math.exp(-max(0.0, u - 0.1) / 0.25) * smooth((u - 0.06) / 0.05), gain=HANDLE, delay=0.04, club=0.1)
    upper(p, t, 0.5, 1.0)
    return settle(stand(p))


RECOIL_T = 1.1


def recoil(t):
    """its own club met armour (or the rival's club met it head on): the shock runs back up the stiff handle, the tail
    rebounds and rings, the hips are thrown back the other way and a hind foot steps to catch the weight"""
    p = {}
    e = math.exp(-max(0.0, t - 0.08) / 0.22) * smooth(t / 0.09)
    ring = math.exp(-max(0.0, t - 0.05) / 0.25) * math.sin(2 * math.pi * 4.5 * (t - 0.05)) * smooth(t / 0.05)
    add(p, "body", rot=(1.2 * e, 6 * e, -3 * e), pos=(1.5 * e, -DROP - 0.5 * e, 0))
    hold_legs(p, -3 * e)
    head(p, 4 * e, -8 * e, -3 * e)
    jaw(p, -3 * e)
    trail(p, t, lambda u: -22 * math.exp(-max(0.0, u - 0.04) / 0.22) * smooth(u / 0.04) + 9 * math.exp(-max(0.0, u - 0.05) / 0.25)
          * math.sin(2 * math.pi * 4.5 * (u - 0.05)) * smooth(u / 0.05), gain=A.BASE, delay=0.03, club=0.05)
    upper(p, t, 0.5, 1.1)
    step = math.sin(math.pi * min(1.0, max(0.0, (t - 0.12) / 0.45))) ** 2
    stand(p)
    plant_h(p, "r", 3.0 * step, 3 * smooth((t - 0.12) / 0.45) * (1 - smooth((t - 0.7) / 0.35)), 0, -6 * step, clear=-0.05)
    _ = ring
    return settle(p)


SUBMIT_T = 2.6


def submit(t):
    """it gives in the armoured animal's way: it lays the club flat on the ground (no threat), sinks onto its belly so
    only the armour faces up, the head drawn in low, and turns its back half away from the rival"""
    p = {}
    k = f(tr((0, 0), (0.7, 0.55, ease_out), (2.6, 0.6)), t)
    drop_tail = f(tr((0, 0), (0.25, 0), (1.0, 1, smooth), (2.6, 1)), t)
    turn_ = f(tr((0, 0), (0.9, 0), (1.8, 1, smooth), (2.6, 1)), t)
    lie(p, k)
    add(p, "body", rot=(0, -6 * turn_, 0))
    head(p, -10 * k - 4 * drop_tail, 10 * turn_, 0, k=0.7)
    A.tail(p, pitch=6 * drop_tail, prof=A.SOFT)
    trail(p, t, lambda u: -8 * f(tr((0, 0), (0.9, 0), (1.8, 1, smooth), (2.6, 1)), u), gain=SWAY, delay=0.12)
    br = wave(t, 1.3) * smooth((t - 0.6) / 0.4)
    add(p, "body", pos=(0, 0.2 * br, 0))
    return settle(lift_tail(lift_head(p, 0.0), 0.0))


LIE_DOWN_T = 2.4
GET_UP_T = 2.4


def _rest_end(p):
    add(p, "body", pos=(0, 0.12, 0)); head(p, 2)


def lie_down(t):
    """from standing onto the belly: the hind legs give first (the rear sinks a little before the front), then the whole
    tank settles level with a soft thump, the head sinks and comes back up, the club laid down last"""
    p = {}
    k = f(tr((0, 0), (0.3, 0.06), (1.5, 0.94, ease_in), (1.65, 1.0, ease_out), (2.4, 1.0)), t)
    rear = window(t, 0.25, 1.35, 0.35)
    lie(p, k)
    add(p, "body", rot=(2.0 * rear, 0, 0))
    land = math.exp(-((t - 1.6) / 0.09) ** 2)
    add(p, "body", pos=(0, -0.4 * land, 0))
    head(p, -4 * window(t, 0.3, 1.7, 0.3) + 2 * smooth((t - 1.8) / 0.5) - 2 * land)
    add(p, "body", pos=(0, 0.12 * smooth((t - 1.8) / 0.5), 0))
    trail(p, t, lambda u: 2.0 * math.exp(-((u - 1.6) / 0.15) ** 2), gain=SWAY, delay=0.07, axis=0)
    upper(p, t, 0.4, 1.2)
    c = 0.3 * (1 - k)
    return settle(lift_tail(lift_head(p, c), c))


def get_up(t):
    """off the belly: the head lifts and swings forward, all four legs push at once (the armour is too heavy to rock
    up one end first), a wobble from side to side as it finds its feet, the tail swung out to balance"""
    p = {}
    k = f(tr((0, 1.0), (0.4, 1.0), (1.5, 0.03, ease_out), (1.7, 0.0, smooth), (2.4, 0.0)), t)
    lie(p, k)
    push = math.exp(-((t - 0.6) / 0.22) ** 2)
    head(p, 2 * (1 - smooth((t - 0.3) / 0.5)) + 4 * push)
    add(p, "body", pos=(0, 0.12 * (1 - smooth((t - 0.3) / 0.4)), 0))
    wob = math.exp(-max(0.0, t - 1.45) / 0.3) * math.sin(2 * math.pi * 2.0 * (t - 1.45)) * smooth((t - 1.35) / 0.12)
    add(p, "body", rot=(0, 0, 2.2 * wob))
    trail(p, t, lambda u: -4.0 * math.exp(-max(0.0, u - 1.45) / 0.35) * math.sin(2 * math.pi * 2.0 * (u - 1.45)) * smooth((u - 1.35) / 0.12),
          gain=SWAY, delay=0.08, club=0.12)
    upper(p, t, 0.5, 1.2)
    c = 0.3 * (1 - k)
    return settle(lift_tail(lift_head(p, c), c))


# ------------------------------------------------------------------ the rest, made fluid (originals + the living layer)
def _alive(fn, k=0.6, period=3.6):
    def g(t):
        p = fn(t)
        upper(p, t, k, period)
        return p
    g.__doc__ = fn.__doc__
    return g


def hurt(t):
    """the flinch: the body jolts away from the blow and rolls, the tail whips out after it and rings down"""
    p = {}
    e = math.exp(-max(0.0, t - 0.05) / 0.15) * smooth(t / 0.08)
    add(p, "body", rot=(-2 * e, -3 * e, -3.5 * e), pos=(0, -DROP - 0.3 * e, 0.8 * e))
    hold_legs(p, -3.5 * e)
    head(p, -8 * e, 10 * e, 4 * e)
    trail(p, t, lambda u: 11 * math.exp(-(u / 0.2)) * smooth(u / 0.05), gain=HANDLE, delay=0.04, club=0.1)
    upper(p, t, 0.5, 1.2)
    return stand(p)


def attack(t):
    """the head hook (the hit at 0.35 s): it cocks the head away and drops the front, hooks it across with the cheek
    horns leading, the shoulders behind it, then lets it swing back past and settle"""
    p = {}
    cock = f(tr((0, 0), (0.22, 1, ease_out), (0.3, 1), (0.37, -1, ease_in), (0.5, -0.85), (0.72, 0.12, smooth), (0.9, 0, smooth)), t)
    dn = f(tr((0, 0), (0.2, 1, ease_out), (0.55, 1), (0.9, 0, smooth)), t)
    add(p, "body", rot=(-1.5 * dn, 3 * cock, -2 * cock), pos=(0, -DROP - 0.6 * dn, -1.0 * dn))
    hold_legs(p, -2 * cock)
    head(p, -8 * dn, 26 * cock, -12 * cock, k=0.5)
    jaw(p, -4 * math.exp(-((t - 0.36) / 0.07) ** 2))
    trail(p, t, lambda u: -6 * f(tr((0, 0), (0.22, 1, ease_out), (0.3, 1), (0.37, -1, ease_in), (0.5, -0.85), (0.72, 0.12, smooth),
                                    (0.9, 0, smooth)), u), gain=A.BASE, delay=0.04)
    flanks(p, t, 0.5, 1.8, drop=False)
    return stand(p, fore=(-2 * dn, -2 * dn))


def snort(t):
    """a blast through the looping nasal passages (Miyashita et al. 2011): the head lifts as it fills, the blow with a
    toss, then a shake that rings and dies out (an envelope, never a switch)"""
    p = {}
    flanks(p, t, 0.6, 1.8)
    up = f(tr((0, 0), (0.32, 1, ease_out), (0.48, 1), (0.6, -0.5, ease_in), (0.95, 0.05, smooth), (1.8, 0, smooth)), t)
    sh = math.exp(-max(0.0, t - 0.95) / 0.3) * math.sin(2 * math.pi * 3.8 * (t - 0.95)) * smooth((t - 0.85) / 0.12)
    buzz = tremor(t, (11.3, 15.7, 7.9), (0.8, 0.5, 0.3)) * window(t, 0.5, 0.75, 0.06)
    head(p, 10 * up + buzz, 10 * sh, 7 * sh)
    add(p, "body", rot=(0.8 * up, 0, 0), pos=(0, -0.3 * max(0, -up), 0))
    trail(p, t, lambda u: 3 * math.exp(-max(0.0, u - 0.95) / 0.3) * math.sin(2 * math.pi * 3.8 * (u - 0.95)) * smooth((u - 0.85) / 0.12),
          gain=SWAY, delay=0.08)
    return stand(p)


def death(t):
    p = A.death(t)
    fade = 1.0 - smooth((t - 1.6) / 1.2)
    for c, a in ((1.7, 1.0), (2.35, 0.5)):
        g = math.exp(-((t - c) / 0.22) ** 2) * a
        add(p, "body", rot=(0.8 * g, 0, 0)); jaw(p, -2 * g)
    tw = sum(a * math.exp(-((t - c) / 0.07) ** 2) for c, a in ((1.4, 1.0), (1.85, -0.6), (2.4, 0.3)))
    trail(p, t, lambda u: 6 * tw * fade, gain=SWAY, delay=0.0)
    return A.shift_to_ground(p)



hunker = _alive(A.hunker, 0.5, 1.6)
dig = _alive(A.dig, 0.5, 3.2)
eat = _alive(A.eat, 0.5, 2.6)
graze = _alive(A.graze, 0.5, 3.4)
drink = _alive(A.drink, 0.4, 3.6)
beg = _alive(A.beg, 0.5, 1.2)
tame = _alive(A.tame, 0.5, 3.0)
wake = _alive(A.wake, 0.5, 1.6)
wake_sleep = _alive(A.wake_sleep, 0.5, 2.6)


def swim(t):
    p = A.swim(t)
    trail(p, t, lambda u: 3.0 * wave(u, 1.8, -0.5), gain=SWAY, delay=0.1, loop=1.8, club=0.12)
    return p


def sit(t):
    p = A.sit(t)
    trail(p, t, lambda u: 1.2 * wave(u, 8.0, 0.3), gain=SWAY, delay=0.2, loop=8.0)
    return p


def sleep(t):
    """asleep on its belly, the chin down, the tail curled round with the club by the head; the breath is 5 s (the old
    5.2 s did not close the 10 s loop), a twitch of the tail tip and the knob now and then"""
    p = {}; br = math.sin(2 * math.pi * t / 5.0)
    lie(p)
    add(p, "body", rot=(0.3 * br, 0, 0), pos=(0, 0.12 * (1 + br), 0))
    head(p, -16 - 0.4 * math.sin(2 * math.pi * t / 5.0 - 0.8), 6, -4, k=0.6)
    for i, b in enumerate(TAILS): add(p, b, rot=(1, 14 * (0.6 + 0.15 * i), 0))
    settle(lift_tail(lift_head(p, 0.0), 0.0))
    flick = math.exp(-((t - 6.3) / 0.12) ** 2)
    add(p, "tail5", rot=(0, 3 * flick, 0)); add(p, "adult_club", rot=(0, 2 * math.exp(-((t - 6.4) / 0.14) ** 2), 0))
    return p


def knocked_out(t):
    p = A.knocked_out(t)
    tw = math.exp(-((t - 2.9) / 0.07) ** 2)
    add(p, "tail4", rot=(0, 2 * tw, 0)); add(p, "skull", rot=(0.8 * tw, 0, 0))
    return p
