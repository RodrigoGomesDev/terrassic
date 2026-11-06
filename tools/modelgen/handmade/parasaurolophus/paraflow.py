"""Parasaurolophus: the fluid set (06/11/2026). Rodrigo asked for the T. rex's fluidity on the remade species, each in its
own way and with a study behind it (docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md: the hadrosaurs FLED; cornered, they
kicked and shoved; a healed tyrannosaur bite on an Edmontosaurus tail says some got away, DePalma et al. 2013). The
principles are the T. rex's (docs/estudos/08: nothing stops, nothing snaps on or off, three beats per action, the chain
follows late, breathing under every action); the body is a lambeosaur's that walks on four and runs on two:
  * the four-legged walk carries the weight: the high hips roll over each standing hind leg and the shoulders yaw a
    little after them, the head on the long neck counters both and rides level, the crest steady; the tail stays a
    beam (ossified tendons) but swings late after the hips; legs and arms cancel the roll so the feet do not slide;
  * the calls keep the bill shut and the crest along the neck (Weishampel 1981), and now the note shivers through the
    neck and the chest with an organic tremor that swells and fades with the note instead of a buzz switched on;
  * it turns on the spot by stepping its four feet round in order, the crest leading;
  * it lies down like a big bird (the hind end settles first) and gets up hind end first, as before;
  * cornered: `kick_back`, a hind foot driven back at what is behind (the head looking round over the shoulder, the
    beam swung aside out of the way), and `body_shove`, the shoulder thrown sideways into an attacker at its flank,
    the head and the crest turned away out of harm.
"""
import math

from anim2 import add, smooth, ease_in, ease_out, back_out, Track
import paraanims as A

SIDES = A.SIDES
TAILS, STIFF = A.TAILS, A.STIFF
STAND_DROP = A.STAND_DROP
head, jaw, tail, plant_h, plant_f, stand, settle, lie, lift_head, lift_tail, chew = (
    A.head, A.jaw, A.tail, A.plant_h, A.plant_f, A.stand, A.settle, A.lie, A.lift_head, A.lift_tail, A.chew)
HIND_LEN, FORE_LEN = 34.0, 26.0          # px, hip to sole and shoulder to hand: the lateral counter of a body shift


def tr(*keys): return Track(keys)


def window(t, a, b, fade=0.25):
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * t / period + phase)


def tremor(t, f=(7.3, 11.1, 4.7), amp=(1.0, 0.55, 0.35), phase=0.0):
    return sum(a * math.sin(2 * math.pi * fr * t + phase * (i + 1) + 1.3 * i) for i, (fr, a) in enumerate(zip(f, amp)))


def beam(p, t, fn, axis=1, delay=0.07, loop=None):
    """follow-through on the stiff tail: the root takes fn late, each bone behind it a little later"""
    for k, (b, w) in enumerate(zip(TAILS, STIFF)):
        u = t - delay * (1 + 0.5 * k)
        v = fn(u % loop if loop else max(0.0, u)) * w
        r = [0.0, 0.0, 0.0]; r[axis] = v
        add(p, b, rot=tuple(r))


def alive_upper(p, t, k=1.0, period=3.4, slow=None):
    """the breath on the neck, the head and the tail (safe on top of planted feet)"""
    head(p, -0.6 * k * wave(t, period, -0.5))
    add(p, "jaw", rot=(-0.3 * k * max(0.0, wave(t, period, -0.8)), 0, 0))
    for i, (b, w) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0.5 * k * w * wave(t, period, -0.5 - 0.3 * i), 1.5 * k * w * wave(t, (slow or period * 2.2), -0.7 - 0.3 * i), 0))


def landing(x):
    x %= 1.0
    return -1.0 + 2.0 * smooth(x / 0.3) if x < 0.3 else 1.0 - 2.0 * smooth((x - 0.3) / 0.7)


def counter_legs(p, roll, shift_x=0.0, yaw=0.0):
    """each leg cancels the body's roll (and a sideways shift of it), so the planted feet stay where they are"""
    hx = math.degrees(math.atan2(-shift_x, HIND_LEN)); fx = math.degrees(math.atan2(-shift_x, FORE_LEN))
    for s in SIDES:
        add(p, f"thigh_{s}", rot=(0, -yaw, -roll + hx)); add(p, f"arm_{s}", rot=(0, -yaw, -roll + fx))


# ------------------------------------------------------------------ gaits
def walk(t, Tc=None, stride=None, lift=None, bob=None, roll=3.4, yaw=2.2, head_p=0.0, tail_amp=5.0):
    """on four: the lateral walk; the hips roll over each standing hind leg, the head counters and rides level, the
    tail beam swings late"""
    W0 = A.WALK
    Tc = Tc or W0[0]; stride = stride or W0[1]; duty = W0[2]; lift = lift or W0[3]; bob = W0[4] if bob is None else bob
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    b2 = landing(2 * ph + 0.05)
    hroll = roll * math.sin(w + 0.3); hyaw = yaw * math.sin(w - 0.5)
    add(p, "body", rot=(0.5 * b2, hyaw, hroll), pos=(0, -STAND_DROP - bob * (0.5 - 0.5 * b2), 0))
    head(p, head_p - 0.8 * landing(2 * ph - 0.08) + 1.6 * math.sin(2 * w - 1.6), -0.8 * hyaw - 1.4 * math.sin(w - 1.2), -0.85 * hroll)
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(k * 0.8 * landing(2 * ph - 0.1 - 0.04 * i), -k * tail_amp * math.sin(w - 1.0 - 0.3 * i), 0))
    counter_legs(p, hroll, yaw=hyaw)
    lift_head(p, 1.0)
    A.foot_cycle(p, ph, A.LATERAL, stride, duty, lift, lift * 0.8, fstride=stride * 0.9)
    return p


WALK_TIRED_T = 2.4


def walk_tired(t):
    """spent: slower, shorter steps, the hips rolling more, the head low with the bill open, the crest sagging"""
    p = walk(t, Tc=WALK_TIRED_T, stride=34, lift=4.5, bob=1.0, roll=4.4, yaw=2.6, head_p=-10, tail_amp=6.0)
    add(p, "jaw", rot=(-5 - 3 * max(0.0, wave(t, WALK_TIRED_T / 3)), 0, 0))
    return p


def run(t):
    """the run on two (the old one), the head steadied a beat late and the beam flicking after the hips"""
    p = A.run(t)
    Tc = A.RUNP[0]; w = 2 * math.pi * ((t / Tc) % 1.0)
    head(p, 1.2 * math.sin(2 * w - 2.0), 0.8 * math.sin(w - 1.6), 0)
    beam(p, t, lambda u: -2.5 * math.sin(2 * math.pi * u / Tc - 1.0), delay=0.04, loop=Tc)
    return p


# ------------------------------------------------------------------ standing
IDLE_T = 8.0
LOOK = Track([(0, (0, 0)), (1.2, (0, 0)), (1.9, (10, 18), ease_out), (3.0, (10, 18)), (3.7, (4, -22), ease_out),
              (5.0, (4, -22)), (5.6, (0, 0), smooth), (8.0, (0, 0))])


def idle(t):
    """on four, breathing slow; it lifts its head to look about, chews the cud with the cheeks flexing, the weight
    drifting from one side to the other, the tail beam swaying late"""
    p = {}
    Ti = IDLE_T
    br = wave(t, Ti / 3)
    shift = wave(t, Ti, 0.4) + 0.3 * wave(t, Ti / 2, 1.0)
    hroll = 1.4 * shift; hyaw = 0.8 * shift
    add(p, "body", rot=(0.4 * br, hyaw, hroll), pos=(0, -STAND_DROP - 0.25 * (1 + br), 0))
    lp, ly = LOOK(t)
    head(p, lp - 0.5 * wave(t, Ti / 3, -0.6) + 0.6 * wave(t, Ti / 5, 1.2), ly - 0.8 * hyaw, -0.85 * hroll + 0.15 * ly)
    chew(p, t, 5.8, 7.6, 0.55)
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0.6 * k * wave(t, Ti / 3, -0.6 - 0.3 * i), k * (2.5 * wave(t, Ti, -1.0 - 0.3 * i) + 0.8 * wave(t, Ti / 2, 0.5 - 0.3 * i)), 0))
    counter_legs(p, hroll, yaw=hyaw)
    return stand(p)


IDLE_TIRED_T = 3.0


def idle_tired(t):
    """winded after a flight: the flanks heave fast, the bill hangs open, the head low with the crest drooping back,
    the tail beam lowered"""
    p = {}
    Ti = IDLE_TIRED_T
    heave = wave(t, Ti / 4)
    add(p, "body", rot=(-1.5 + 0.8 * heave, 0, 0.6 * wave(t, Ti, 0.3)), pos=(0, -STAND_DROP - 0.6 - 0.4 * heave, 0))
    head(p, -14 - 1.5 * wave(t, Ti / 4, -0.6), 3 * wave(t, Ti, 0.5), 0)
    add(p, "jaw", rot=(-6 - 3 * max(0.0, wave(t, Ti / 4, -0.4)), 0, 0))
    tail(p, pitch=3)
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0.6 * k * heave, 1.5 * k * wave(t, Ti, -0.8 - 0.3 * i), 0))
    counter_legs(p, 0.6 * wave(t, Ti, 0.3))
    return stand(p)


# ------------------------------------------------------------------ turning on the spot: four feet stepping round
TURN_T = 2.0
TURN_ORDER = {"rh": 0.0, "rf": 0.25, "lh": 0.5, "lf": 0.75}


def turn(t, side, Tt=TURN_T, lead_deg=14.0, roll=2.4):
    # + yaw swings the head to the animal's RIGHT in game, so a turn to the left leads with - yaw
    d = 1.0 if side == "left" else -1.0
    ph = (t / Tt) % 1.0; w = 2 * math.pi * ph; p = {}
    lead = -d
    hroll = roll * math.sin(2 * w + 0.4)
    add(p, "body", rot=(0.4 * math.sin(4 * w), lead * (3.0 + 0.8 * math.sin(2 * w)), hroll), pos=(0, -STAND_DROP, 0))
    head(p, 2.0 + 1.0 * math.sin(4 * w - 1.0), lead * (lead_deg + 2.0 * math.sin(2 * w - 0.8)), -0.8 * hroll)
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        add(p, b, rot=(0, k * (-lead * 7.0 - 2.0 * math.sin(2 * w - 1.2 - 0.3 * i)), 0))
    counter_legs(p, hroll, yaw=lead * 3.0)
    lift_head(p, 1.0)
    for foot, o in TURN_ORDER.items():
        s, kind = foot[0], foot[1]
        u = (ph + o) % 1.0
        if u < 0.22:
            sw = u / 0.22; up = math.sin(math.pi * sw)
            if kind == "h":
                plant_h(p, s, 4.5 * up ** 1.2, -2.0 * math.cos(math.pi * sw), 12 * up, -18 * up, clear=0.8 * up ** 0.5)
            else:
                plant_f(p, s, 3.5 * up ** 1.2, -1.6 * math.cos(math.pi * sw), -24 * up, clear=0.6 * up ** 0.5)
        else:
            dz = 2.0 - 4.0 * (u - 0.22) / 0.78
            plant_h(p, s, 0.0, dz) if kind == "h" else plant_f(p, s, 0.0, 0.8 * dz)
    return p


def turn_left(t): return turn(t, "left")
def turn_right(t): return turn(t, "right")


# ------------------------------------------------------------------ cornered: the kick and the shove
KICK_BACK_T = 1.4
KICK_BACK_HIT = 0.55
KB_LOAD = tr((0, 0), (0.38, 1, ease_out), (0.46, 1.0), (0.58, 0.25, ease_in), (0.9, 0.0, smooth), (1.4, 0))
KB_DRIVE = tr((0, 0), (0.44, 0), (0.55, 1, ease_in), (0.64, 0.9), (1.05, 0, smooth), (1.4, 0))
KB_LOOK = tr((0, 0), (0.25, 1, ease_out), (1.0, 1), (1.4, 0, smooth))


def kick_back(t):
    """something at its tail: it looks round over the right shoulder, the weight goes forward onto the forelegs and the
    left hind, the right hind is drawn up (anticipation), then driven back and a little out (the blow at 0.55 s), the
    tail beam swung aside to the left out of the way; the foot comes down and the weight goes back"""
    p = {}
    load = float(KB_LOAD(t)); drive = float(KB_DRIVE(t)); look = float(KB_LOOK(t))
    tip = max(load, drive)
    roll = -3.0 * tip
    add(p, "body", rot=(-3 * tip - 2 * drive, 3 * look, roll), pos=(0.6 * tip, -STAND_DROP - 0.8 * tip, -2.0 * tip))
    head(p, -4 * tip, 46 * look, -6 * look)
    jaw(p, -3 * math.exp(-((t - 0.56) / 0.08) ** 2))
    tail(p, yaw=4 * tip, pitch=-3 * tip)
    beam(p, t, lambda u: 10 * float(KB_DRIVE(u)) + 4 * float(KB_LOAD(u)), delay=0.05)
    alive_upper(p, t, k=0.5)
    counter_legs(p, roll, shift_x=0.6 * tip)
    add(p, "thigh_r", rot=(0, 0, -7 * drive))
    lift_head(p)
    plant_h(p, "l")
    plant_h(p, "r", 9 * load + 8 * drive, 3 * load + 20 * drive, -24 * load + 40 * drive, -20 * load + 10 * drive, clear=None)
    for s in SIDES: plant_f(p, s, 0, -1.5 * tip)
    return settle(p)


BODY_SHOVE_T = 1.4
BODY_SHOVE_HIT = 0.6
BS = tr((0, 0), (0.42, -1.0, ease_out), (0.5, -0.95), (0.6, 1.0, ease_in), (0.68, 1.1), (1.4, 0, back_out))


def body_shove(t):
    """an attacker at its right flank: it leans away to the left with the head and crest turned off and down out of
    harm (anticipation), then throws the shoulder and the whole flank sideways into it (the hit at 0.6 s), carries
    through, rocks back a little past upright and settles; the tail beam swings the other way, late"""
    p = {}
    s_ = float(BS(t)); a = max(0.0, s_); b = max(0.0, -s_)
    jolt = math.exp(-((t - BODY_SHOVE_HIT - 0.02) / 0.05) ** 2)
    roll = 6.0 * a - 4.0 * b
    shift = -2.4 * a + 1.2 * b                         # - x: to its right
    add(p, "body", rot=(-1.0 * a, 4.0 * a - 2.0 * b, roll), pos=(shift, -STAND_DROP - 0.8 * a - 0.4 * jolt, 0))
    head(p, -10 * b - 14 * a, -22 * b - 26 * a, 4 * b - 6 * a)          # turned away, the crest laid back
    beam(p, t, lambda u: 9 * float(BS(u)), delay=0.06)
    alive_upper(p, t, k=0.5)
    counter_legs(p, roll, shift_x=shift)
    return stand(p)


def hurt(t):
    """the flinch: a jolt away, the head thrown up and aside with the crest, the beam jerking late"""
    p = {}
    e = math.exp(-t / 0.15) * smooth(t / 0.04)
    add(p, "body", rot=(4 * e, -5 * e, -3 * e), pos=(0, -STAND_DROP - 0.5 * e, 1.5 * e))
    head(p, 12 * e, 14 * e, 8 * e)
    beam(p, t, lambda u: 8 * math.exp(-u / 0.2) * smooth(u / 0.05), delay=0.05)
    beam(p, t, lambda u: -4 * math.exp(-u / 0.2) * smooth(u / 0.05), axis=0, delay=0.05)
    alive_upper(p, t, k=0.5)
    counter_legs(p, -3 * e)
    return stand(p)


def attack(t):
    """the old shoulder barge (the hit at 0.5 s) with the breath under it and the beam following the lunge late"""
    p = A.attack(t)
    beam(p, t, lambda u: -5 * float(tr((0, 0), (0.4, 0), (0.52, 1, ease_in), (0.7, 0.8), (1.2, 0, smooth))(u)), delay=0.06)
    alive_upper(p, t, k=0.4)
    return p


# ------------------------------------------------------------------ the voice with an organic tremor
def voiced(fn, env, k_neck=0.6, k_body=0.25, f=(7.9, 11.7, 5.3)):
    """the note shivers through the neck and the chest: a tremor of three sines inside the note's own envelope"""
    def g(t):
        p = fn(t)
        e = env(t)
        if e > 1e-4:
            tm = tremor(t, f) * e          # (-1.9 .. 1.9) x e; the head takes it biased up, never down
            head(p, k_neck * (tm + 1.9 * e), 0.25 * k_neck * tremor(t, (6.1, 9.7, 13.3), phase=0.8) * e, 0)
            add(p, "neck1", rot=(-k_body * tm, 0, 0))   # the chest heave at the neck root: the body would lift the planted hands
        return p
    g.__name__ = fn.__name__
    g.__doc__ = fn.__doc__
    return g


call = voiced(A.call, lambda t: window(t, 0.8, 1.9, 0.2) + window(t, 2.1, 2.5, 0.12))
answer = voiced(A.answer, lambda t: 0.7 * window(t, 0.6, 1.5, 0.2))
alarm = voiced(A.alarm, lambda t: sum(window(t, c, c + 0.16, 0.05) for c in (0.6, 0.95, 1.3)), k_neck=0.9, k_body=0.4)
crest_display = voiced(A.crest_display, lambda t: 0.8 * window(t, 1.6, 2.4, 0.2))


# ------------------------------------------------------------------ lying down and getting up
LIE_DOWN_T = 2.6


def lie_down(t):
    """like a big bird: the hind end settles first (it sits back on its folded legs), the chest follows, the head
    looks down where it lies and comes back up"""
    p = {}
    kh = float(tr((0, 0), (0.3, 0), (1.1, 1, ease_in), (2.6, 1))(t))
    k = float(tr((0, 0), (0.7, 0), (1.75, 1, ease_in), (2.6, 1))(t))
    look = float(tr((0, 0), (0.4, 1, ease_out), (1.6, 1), (2.6, 0, smooth))(t))
    land = math.exp(-((t - 1.8) / 0.1) ** 2)
    lie(p, k, kh=max(kh, k))
    add(p, "body", rot=(8 * (kh - k) + 0.6 * land, 0, 0))
    head(p, -14 * look + 2 * land, 0, 0)
    beam(p, t, lambda u: -2.5 * math.exp(-((u - 1.8) / 0.14) ** 2), axis=0, delay=0.06)
    alive_upper(p, t, k=0.5)
    return settle(lift_tail(lift_head(p, 0.0)))


GET_UP_T = 2.4


def get_up(t):
    """hind end first (as it always does), the head swung forward for balance, then the front, a settling rock"""
    p = {}
    kh = float(tr((0, 1), (0.3, 1), (1.0, 0, smooth), (2.4, 0))(t))
    k = float(tr((0, 1), (0.8, 1), (1.6, 0, smooth), (2.4, 0))(t))
    push = math.exp(-((t - 1.1) / 0.2) ** 2)
    wob = math.exp(-max(0.0, t - 1.6) / 0.25) * math.sin(2 * math.pi * 2.2 * (t - 1.6)) * smooth((t - 1.55) / 0.1)
    lie(p, k, kh=kh)
    add(p, "body", rot=(0, 0, 1.6 * wob))
    head(p, -10 * push, 0, 0)
    beam(p, t, lambda u: -2.5 * math.exp(-max(0.0, u - 1.6) / 0.3) * math.sin(2 * math.pi * 2.2 * (u - 1.6)) * smooth((u - 1.55) / 0.1), delay=0.07)
    alive_upper(p, t, k=0.5)
    return settle(lift_tail(lift_head(p, 0.0)))


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


NEW = {
    "turn_left": (turn_left, TURN_T, True, "Movimento", "girando no lugar para a esquerda: as quatro patas dão passos em ordem, a crista na frente"),
    "turn_right": (turn_right, TURN_T, True, "Movimento", "girando no lugar para a direita"),
    "lie_down": (lie_down, LIE_DOWN_T, False, "Descanso", "deita como ave grande: o quadril assenta primeiro, depois o peito"),
    "get_up": (get_up, GET_UP_T, False, "Descanso", "levanta pelo QUADRIL primeiro, a cabeça à frente, depois a frente"),
    "idle_tired": (idle_tired, IDLE_TIRED_T, True, "Parado", "parado cansado: os flancos arfam, o bico aberto, a crista caída"),
    "walk_tired": (walk_tired, WALK_TIRED_T, True, "Movimento", "andando cansado em quatro patas, cabeça baixa, bico aberto"),
    "kick_back": (kick_back, KICK_BACK_T, False, "Combate", "encurralado: olha por cima do ombro e chuta para trás com a pata traseira (golpe em 0,55 s)"),
    "body_shove": (body_shove, BODY_SHOVE_T, False, "Combate", "encurralado: joga o ombro e o flanco de lado no atacante, crista virada (golpe em 0,6 s)"),
}

REPLACED = {
    "idle": idle, "walk": walk, "run": run, "attack": attack, "hurt": hurt, "call": call, "answer": answer, "alarm": alarm,
    "crest_display": crest_display, "vigilant": lively(A.vigilant, 0.2), "eat": lively(A.eat, 0.3),
    "graze": lively(A.graze, 0.3), "drink": lively(A.drink, 0.2), "beg": lively(A.beg, 0.4, period=A.ANIMS["beg"][1]), "tame": lively(A.tame, 0.4),
}


def rebind(anims):
    out = {n: ((REPLACED[n],) + v[1:]) if n in REPLACED else v for n, v in anims.items()}
    for n, v in NEW.items():
        out.setdefault(n, v)
    return out
