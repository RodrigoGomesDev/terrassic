"""Giganotosaurus animations, written for it from its own study (page "Giganotosaurus: estudo e modelo", the list
Rodrigo approved on 01/11/2026 19:02Z).

Only the plumbing is shared (anim2: easing, leg IK, export; theropod.Plan: plant/stand, a rotation spread over the
neck bones). Every pose is its own, from what the study says the animal was:
- a land shark: it cuts and lets go, steps back and waits, circles, comes in again. No sprint: its fast gait is a
  forced march, one foot always on the ground (Sellers 2017);
- the eyes look sideways from under a bony eave: to aim it turns the head on its side and looks with one eye (the
  T. rex looks ahead, the Carnotaurus aims in jumps);
- the head is carried low, in line with the back, and the roar goes forward and low, never up at the sky;
- heavy and long: the pelvis rolls from side to side at the walk, the head stays still, the tail swings wide and
  slow, the whole of it bending (no stiff half like the Carnotaurus).
"""
import math
import os
import sys
_H = os.path.dirname(os.path.abspath(__file__))
_E = os.path.join(_H, "..", "_engine")
sys.path[:0] = [_H, _E, os.path.join(_E, "plans")]
import proto as P
import giga
import theropod
from anim2 import add, Track, smooth, ease_out, ease_in, back_out, lowest
from theropod import window, W, SIDES

TAILS = ("tail1", "tail2", "tail3", "tail4", "tail5")
BEND = (1.0, 0.9, 0.8, 0.7, 0.6)          # the whole tail bends, the tip a little less per bone (it is longer)


def model():
    m = giga.build(saddle_on=True); P.pack(m, giga.TEX_W); return m.spec()


S = model()
T = theropod.Plan(S, K=1.0, necks=("neck1", "neck2"), tails=TAILS)


def tr(*keys): return Track(keys)


# signs on this rig: body +x = nose up; neck/skull -x = down; jaw -x = open; tail pitch + = down; yaw + = to its left
def tail(p, yaw=0.0, pitch=0.0):
    for b, k in zip(TAILS, BEND):
        add(p, b, rot=(pitch * k, yaw * k, 0))


def tail_wave(p, t, Tc, yaw, pitch=0.0, lag=0.55, ph=0.0):
    """a slow wave running down the tail: each bone a little later than the one before"""
    for i, (b, k) in enumerate(zip(TAILS, BEND)):
        a = W(t, Tc) - lag * i + ph
        add(p, b, rot=(pitch * k * math.sin(a * 2 - 0.6), yaw * k * math.sin(a), 0))


def eye(p, k, side=1.0, low=0.0):
    """the head turned on its side to look with one eye: side +1 = the left eye up at the target"""
    T.neck(p, (-low * k, 12 * k * side, 0))
    add(p, "skull", rot=(2 * k, 10 * k * side, -34 * k * side))


def arms(p, a=0.0, f=0.0):
    for s, _ in SIDES:
        add(p, f"arm_{s}", rot=(a, 0, 0)); add(p, f"forearm_{s}", rot=(f, 0, 0))


def jaw(p, a):
    add(p, "jaw", rot=(a, 0, 0))


# ------------------------------------------------------------------ gait (its own: rolling pelvis, still head)
def gait(t, Tc, stride, duty, lift, bob, lean=0.0, drop=0.0, head=0.0, roll=1.0, still=0.9, back=False, tail_amp=1.0):
    """one stride cycle. roll = how far the pelvis rolls over the standing leg; still = how much of it the neck
    cancels so the head stays put. back: the same steps played backwards (stepping back, facing the target)"""
    ph = (t / Tc) % 1.0
    if back: ph = 1.0 - ph
    w = 2 * math.pi * ph; p = {}
    bp = 0.7 * math.sin(2 * w - 0.4); by = 2.0 * roll * math.sin(w); br = 3.0 * roll * math.sin(w + 0.3)
    add(p, "body", rot=(lean + bp, by, br), pos=(0, -bob * math.cos(2 * w - 0.9) - 0.6 - drop, 0))
    T.neck(p, (head - lean * still - bp * still, -by * still, -br * still * 0.7))
    add(p, "skull", rot=(-head * 0.3, 0, -br * 0.3))
    for i, (b, k) in enumerate(zip(TAILS, BEND)):       # wide and slow, the wave a beat behind the hips
        add(p, b, rot=(lean * 0.4 * k + 0.5 * math.sin(2 * w - 1.2 - 0.5 * i), -3.2 * tail_amp * k * math.sin(w - 0.9 - 0.45 * i), 0))
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(2.5 * math.sin(2 * w + o * 2 * math.pi - 2.2), 0, 0))
    for s, o in SIDES:
        u = (ph + o) % 1.0
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0
            meta = 30 * smooth(max(0, (st - 0.55) / 0.45)); toe = 0.0; clear = -0.05
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e
            ly = lift * math.sin(math.pi * min(1, sw * 1.1)) ** 1.2      # a low, heavy foot
            meta = 30 * (1 - smooth(sw / 0.45)) - 20 * math.sin(math.pi * sw)
            toe = -26 * math.sin(math.pi * min(1, sw * 1.1)) + 6 * smooth((sw - 0.7) / 0.3)
            clear = 1.0 * math.sin(math.pi * sw) ** 0.5
        T.plant(p, s, ly, dz - 3, meta, toe, clear)
    return p


WALK = (2.0, 84, 0.66, 9, 1.4)
MARCH = (1.15, 118, 0.56, 13, 2.0)        # the forced march: duty over 0.5, so one foot is always down


def walk(t):
    return gait(t, *WALK)


def run(t):
    """no sprint: a forced march, long quick steps, the body leaning into it, the head low and steady"""
    p = gait(t, *MARCH, lean=5, drop=2.5, head=-5, roll=0.7, still=0.95, tail_amp=0.8)
    arms(p, -10, 8)
    return p


def stalk(t):
    """low and slow, the neck stretched forward, the head held level while the body rolls under it"""
    Tw, st, du, li, bo = WALK
    p = gait(t, Tw * 1.5, st * 0.7, 0.72, li * 0.7, bo * 0.4, lean=3, drop=6, head=-9, roll=0.6, still=1.0, tail_amp=0.6)
    return p


def back_off(t):
    """after the cut: short steps backwards, the head low and on the target, the jaws a little open"""
    Tw, st, du, li, bo = WALK
    p = gait(t, 1.6, 44, 0.66, li * 0.8, bo * 0.6, lean=-2, drop=1, head=-6, roll=0.6, still=1.0, back=True, tail_amp=0.6)
    jaw(p, -4)
    return p


def circle(t):
    """walking sideways round the prey: the body turned in toward it, the head turned further and tilted to watch it
    with one eye; the legs step across under the body"""
    Tc = 1.8
    p = gait(t, Tc, 26, 0.64, 8, 0.8, drop=2, head=-4, roll=0.5, still=1.0, tail_amp=1.4)
    add(p, "body", rot=(0, 14, 0))
    eye(p, 0.8, 1.0, low=4); T.neck(p, (0, 14, 0))
    w = W(t, Tc)
    for s, sx in (("l", 1), ("r", -1)):          # the cross-step: each thigh swings out sideways as it lifts
        add(p, f"thigh_{s}", rot=(0, 0, 5 * math.sin(w + (0 if s == "l" else math.pi))))
    tail(p, yaw=-8)
    lo = lowest(S, p, skip_mats=("teeth", "teeth_lo") + giga.SADDLE_MATS)
    if lo < 0: add(p, "root", pos=(0, -lo, 0))     # the sideways swing must not push a toe into the ground
    return p


# ------------------------------------------------------------------ standing
def idle(t):
    """breathing slowly, the head low in line with the back; now and then it turns the head on its side to look with
    one eye, holds it, and comes back"""
    p = {}; br = math.sin(W(t, 3.2))
    add(p, "body", rot=(0.6 * br, 0, 0.4 * math.sin(W(t, 8.0))), pos=(0, 0.35 * br, 0))
    a = float(tr((0, 0), (1.6, 0), (2.2, 1, ease_out), (3.9, 1), (4.5, 0, smooth), (8.0, 0))(t))
    b = float(tr((0, 0), (5.3, 0), (5.8, 1, ease_out), (6.7, 1), (7.3, 0, smooth), (8.0, 0))(t))
    T.neck(p, (-0.6 * br, 0, 0))
    eye(p, a, 1.0); eye(p, 0.6 * b, -1.0)
    jaw(p, -0.8 - 0.8 * max(0, br))
    tail_wave(p, t, 8.0, 2.2, 0.3)
    arms(p, 1.0 * br)
    return T.stand(p)


def look_side(t):
    """a slow look to one side: the neck turns, the head lies over and one eye looks; then the other side"""
    p = {}; br = math.sin(W(t, 3.2))
    add(p, "body", rot=(0.6 * br, 0, 0))
    a = float(tr((0, 0), (0.6, 1, ease_out), (1.6, 1), (2.0, 0, smooth), (3.6, 0))(t))
    b = float(tr((0, 0), (2.0, 0), (2.5, 1, ease_out), (3.2, 1), (3.6, 0, smooth))(t))
    T.neck(p, (0, 26 * a - 22 * b, 0)); add(p, "body", rot=(0, 4 * a - 4 * b, 0))
    eye(p, a, 1.0); eye(p, b, -1.0)
    tail(p, yaw=-3 * a + 3 * b)
    return T.stand(p)


def eye_aim(t):
    """stopped after the cut: the head low and on its side, one eye on the prey; two small corrections of the aim,
    the jaws ajar, the breath heavy"""
    p = {}; br = math.sin(W(t, 1.1))
    k = float(tr((0, 0), (0.3, 1, ease_out), (1.2, 1), (1.5, 0, smooth))(t))
    add(p, "body", rot=(2 * k + 0.8 * br, 0, 0), pos=(0, -1.5 * k, 0))
    eye(p, k, 1.0, low=8)
    fix = sum(math.exp(-((t - c) / 0.05) ** 2) for c in (0.55, 0.9))
    add(p, "skull", rot=(0, 3 * fix, -4 * fix))
    jaw(p, -5 * k - 1.5 * max(0, br))
    tail(p, pitch=2 * k)
    return T.stand(p)


# ------------------------------------------------------------------ combat
def slash(t):
    """the cut: the head cocks to the side with the jaws wide, comes in low, closes (the hit, 0.5 s), drags across
    to cut with the blades, lets go at once and pulls back; then it stands back from the prey"""
    p = {}
    cock = float(tr((0, 0), (0.3, 1, ease_out), (0.42, 1), (0.52, 0, ease_in), (1.4, 0))(t))
    hit = float(tr((0, 0), (0.36, 0), (0.5, 1, ease_in), (0.62, 1), (1.4, 0))(t))
    drag = float(tr((0, 0), (0.5, 0), (0.72, 1, ease_out), (0.82, 1), (1.0, 0.6), (1.4, 0, smooth))(t))
    rec = float(tr((0, 0), (0.78, 0), (1.0, 1, ease_out), (1.2, 1), (1.4, 0.2, smooth))(t))
    j = float(tr((0, 0), (0.3, -42, ease_out), (0.42, -44), (0.5, -2, ease_in), (0.8, -2), (0.86, -22, ease_out), (1.1, -6), (1.4, -2))(t))
    add(p, "body", rot=(2 * hit - 4 * rec, 6 * cock - 6 * drag, 2 * drag), pos=(0, -1.2 * hit, -4 * hit + 4 * rec))
    T.neck(p, (4 * cock - 12 * hit + 10 * rec, 22 * cock - 30 * drag, 0))
    add(p, "skull", rot=(4 * cock - 4 * hit + 4 * rec, 6 * cock - 14 * drag, -16 * cock + 18 * drag))
    jaw(p, j)
    tail(p, yaw=-6 * cock + 8 * drag, pitch=-2 * hit + 2 * rec)
    T.plant(p, "l", 0, -4 * hit + 3 * rec, 0, 0)
    T.plant(p, "r", 0, 2 * hit + 4 * rec, 0, 0)
    arms(p, -8 * hit, 6 * hit)
    return p


def attack_quick(t):
    """the short cut (from the saddle): jaws open, close on the frame the hit lands (0.3 s), a drag to the side"""
    p = {}
    hit = float(tr((0, 0), (0.18, 0), (0.3, 1, ease_in), (0.42, 1), (1.0, 0, smooth))(t))
    drag = float(tr((0, 0), (0.3, 0), (0.48, 1, ease_out), (1.0, 0, smooth))(t))
    j = float(tr((0, 0), (0.16, -36, ease_out), (0.3, -2, ease_in), (0.5, -2), (0.58, -14), (1.0, 0))(t))
    add(p, "body", rot=(2 * hit, -4 * drag, 0), pos=(0, -0.8 * hit, -3 * hit))
    T.neck(p, (-10 * hit, 14 * hit - 22 * drag, 0)); add(p, "skull", rot=(-3 * hit, -10 * drag, 12 * drag))
    jaw(p, j)
    tail(p, yaw=6 * drag)
    return T.stand(p)


def lunge(t):
    """the low strike at the leg of big prey: it draws the neck back, then throws the head out long and low; the
    jaws shut at full stretch (0.6 s) and it hauls back"""
    p = {}
    coil = float(tr((0, 0), (0.35, 1, ease_out), (0.42, 1), (0.55, 0, ease_in), (1.6, 0))(t))
    out = float(tr((0, 0), (0.42, 0), (0.6, 1, ease_in), (0.85, 1), (1.3, 0, smooth), (1.6, 0))(t))
    j = float(tr((0, 0), (0.4, -10), (0.52, -40, ease_out), (0.6, -2, ease_in), (1.2, -2), (1.6, 0))(t))
    add(p, "body", rot=(3 * coil - 5 * out, 0, 0), pos=(0, -1 * coil - 4 * out, 5 * coil - 9 * out))
    T.neck(p, (8 * coil - 22 * out, 0, 0)); add(p, "skull", rot=(4 * coil + 6 * out, 0, 0))
    jaw(p, j)
    tail(p, pitch=-3 * coil + 5 * out)
    T.plant(p, "l", 0, 5 * coil - 10 * out, 0, 0)
    T.plant(p, "r", 0, 3 * coil + 6 * out, 0, 0)
    arms(p, -10 * out, 10 * out)
    return p


def rip(t):
    """holds on and shakes the head from side to side to tear a piece off, like a shark; the legs braced back"""
    p = {}
    k = float(tr((0, 0), (0.3, 1, ease_out), (1.8, 1), (2.2, 0, smooth))(t))
    bite = float(tr((0, 0), (0.25, 0), (0.45, 1, ease_in), (1.75, 1), (1.85, 0), (2.2, 0))(t))
    sh = math.sin(2 * math.pi * 2.8 * (t - 0.5)) * window(t, 0.55, 1.7, 0.08)
    j = float(tr((0, 0), (0.25, -38, ease_out), (0.45, -4, ease_in), (1.75, -4), (1.85, -24), (2.2, 0))(t))
    add(p, "body", rot=(-3 * bite, 4 * sh, 3 * sh), pos=(0, -1.5 * k, 3 * bite))
    T.neck(p, (-12 * k + 8 * bite, 16 * sh, 0)); add(p, "skull", rot=(-4 * k, 14 * sh, 16 * sh))
    jaw(p, j)
    tail(p, yaw=-8 * sh, pitch=2 * bite)
    T.plant(p, "l", 0, 6 * bite, 0, 0)
    T.plant(p, "r", 0, 10 * bite, 0, 0)
    return p


def stomp(t):
    """a small thing at its feet: it lifts the right foot high and brings the whole weight down on it (0.9 s)"""
    p = {}
    up = float(tr((0, 0), (0.55, 1, ease_out), (0.75, 1), (0.9, 0, ease_in), (1.7, 0))(t))
    land = math.exp(-((t - 0.92) / 0.06) ** 2)
    add(p, "body", rot=(-3 * up + 2 * land, 0, -3 * up), pos=(0, -1.5 * land, 0))
    T.neck(p, (-8 * up - 4 * land, 0, 0)); add(p, "skull", rot=(-6 * up, 0, 0)); jaw(p, -6 * land)
    tail(p, pitch=-2 * up + 3 * land)
    T.plant(p, "l")
    T.plant(p, "r", 18 * up, -14 * up, -20 * up, -10 * up)
    return p


# ------------------------------------------------------------------ voice
def gape(t):
    """the warning: the head turns to show its profile and the huge mouth opens slowly on the row of blades,
    holds with a hiss, and shuts"""
    p = {}
    k = float(tr((0, 0), (0.6, 1, ease_out), (2.2, 1), (2.8, 0, smooth))(t))
    o = float(tr((0, 0), (0.4, 0), (1.1, 1, ease_out), (2.0, 1), (2.5, 0, ease_in), (2.8, 0))(t))
    hiss = math.sin(2 * math.pi * 9 * t) * window(t, 1.1, 2.0, 0.1)
    add(p, "body", rot=(2 * k, 6 * k, 0), pos=(0, -1 * k, 0))
    T.neck(p, (-4 * k, 24 * k, 0)); add(p, "skull", rot=(4 * o, 8 * k, -10 * k))
    jaw(p, -50 * o - 1.0 * hiss)
    tail(p, yaw=-6 * k, pitch=2 * k)
    arms(p, -6 * k, 6 * k)
    return T.stand(p)


def roar(t):
    """low and forward, never at the sky: the neck stretches out level, the jaws wide, the tail up behind"""
    p = {}
    k = float(tr((0, 0), (0.45, -0.3), (0.8, 1, ease_out), (2.6, 1), (3.4, 0, smooth))(t))
    a = max(0, k); b = max(0, -k)
    vib = math.sin(2 * math.pi * 11 * t) * window(t, 0.8, 2.6, 0.1)
    add(p, "body", rot=(2 * a - 2 * b, 0, 0), pos=(0, -1.5 * a, -3 * a + 2 * b))
    T.neck(p, (-6 * a + 6 * b, 0, 0)); add(p, "skull", rot=(4 * a + 0.8 * vib, 0, 0))
    jaw(p, -40 * a - 4 * b - vib)
    tail(p, pitch=-4 * a)
    arms(p, -8 * a, 6 * a)
    return T.stand(p)


def roar_loud(t):
    """the big one: a step forward, the whole body thrown behind the low, stretched head, three pulses"""
    p = {}
    k = float(tr((0, 0), (0.6, -0.4), (1.1, 1, ease_out), (3.6, 1), (4.4, 0, smooth))(t))
    a = max(0, k); b = max(0, -k)
    pulse = sum(window(t, c, c + 0.5, 0.08) for c in (1.2, 1.9, 2.6))
    vib = math.sin(2 * math.pi * 10 * t) * window(t, 1.1, 3.6, 0.1)
    add(p, "body", rot=(3 * a - 3 * b + 1.5 * pulse, 0, 0), pos=(0, -2.5 * a, -6 * a + 3 * b))
    T.neck(p, (-10 * a + 8 * b - 2 * pulse, 0, 0)); add(p, "skull", rot=(6 * a + vib, 0, 0))
    jaw(p, -50 * a - 6 * b - 4 * pulse - vib)
    tail(p, pitch=-6 * a)
    T.plant(p, "l", 0, -10 * a, 0, 0)
    T.plant(p, "r", 0, 4 * a, 0, 0)
    arms(p, -12 * a, 8 * a)
    return p


def call(t):
    """the call to its mate: short and deep, the head a little up, the mouth barely open, the throat and chest
    swelling with each of the two notes"""
    p = {}
    k = float(tr((0, 0), (0.4, 1, ease_out), (2.2, 1), (2.6, 0))(t))
    g = sum(window(t, c, c + 0.45, 0.08) for c in (0.6, 1.4))
    add(p, "body", rot=(2 * k + 2.5 * g, 0, 0), pos=(0, 1.0 * g, 0))
    T.neck(p, (8 * k + 3 * g, 0, 0)); add(p, "skull", rot=(4 * k + 2 * g, 0, 0))
    jaw(p, -2 * k - 8 * g)
    tail(p, pitch=1.5 * g)
    return T.stand(p)


def crest_show(t):
    """the male's display: the head held up in profile to show the red-wine lumps of the snout and the hornlets,
    first one side, then a slow turn to the other"""
    p = {}
    k = float(tr((0, 0), (0.6, 1, ease_out), (2.4, 1), (3.0, 0, smooth))(t))
    s = float(tr((0, 1), (1.3, 1), (1.9, -1, smooth), (3.0, -1))(t))
    add(p, "body", rot=(4 * k, 0, 0), pos=(0, 1 * k, 0))
    T.neck(p, (16 * k, 26 * k * s, 0)); add(p, "skull", rot=(6 * k, 6 * k * s, 0))
    jaw(p, -2 * k)
    tail(p, pitch=-2 * k, yaw=-5 * k * s)
    arms(p, -4 * k)
    return T.stand(p)


# ------------------------------------------------------------------ resting
def ground_fit(S, p):
    """the lowest point of the animal on the ground; the saddle does not count (unsaddled it would float)"""
    lo = lowest(S, p, skip_mats=("teeth", "teeth_lo") + giga.SADDLE_MATS); add(p, "root", pos=(0, -lo, 0)); return p


LIE = 43.0      # the low keel of the chest is 45 px up: with the legs folded it rests on the ground
LIE_LEGS = {f"{b}_{s}": (a, 0, 0) for s, _ in SIDES for b, a in (("thigh", 62), ("shin", -118), ("foot", 56))}


def fold(p, k, head_down=0.0):
    """k = 0 standing .. 1 on the belly. The chest goes down first, the long tail lies straight behind"""
    add(p, "body", rot=(-1 * k, 0, 0), pos=(0, -LIE * k, 0))
    T.neck(p, (-2 * k - 10 * head_down, 0, 0)); add(p, "skull", rot=(2 * k - 2 * head_down, 0, 0))
    tail(p, pitch=3.5 * k)
    arms(p, -10 * k, 14 * k)
    for n, r in LIE_LEGS.items(): add(p, n, rot=tuple(x * smooth(k) for x in r))
    return p


def sit(t):
    """lying on its belly but awake: the head up off the ground, low; now and then a look with one eye"""
    p = {}; br = math.sin(W(t, 3.6))
    fold(p, 1.0); add(p, "body", rot=(0.7 * br, 0, 0))
    a = float(tr((0, 0), (1.8, 0), (2.4, 1, ease_out), (3.8, 1), (4.4, 0, smooth), (6.0, 0))(t))
    T.neck(p, (6 - 0.5 * br, 0, 0)); eye(p, a, 1.0)
    tail_wave(p, t, 6.0, 1.2)
    return ground_fit(S, p)


def sleep(t):
    """asleep with the neck and head stretched straight out on the ground in front of it; slow breath in the flanks"""
    p = {}; br = math.sin(W(t, 4.5))
    fold(p, 1.0, head_down=1.0)
    add(p, "body", rot=(1.0 * br, 0, 0), pos=(0, 0.4 * br, 0))
    T.neck(p, (-0.6 * br, 0, 0))
    jaw(p, -0.8 * max(0, br))
    tail(p, yaw=-3)
    return ground_fit(S, p)


def wake_sleep(t):
    """from sleep: the head lifts and looks with one eye, then the chest comes up, then the hips"""
    p = {}
    hd = float(tr((0, 1), (0.5, 0, ease_out), (2.4, 0))(t))
    up = float(tr((0, 1), (1.1, 1), (1.9, 0, smooth), (2.4, 0))(t))
    fold(p, up, head_down=hd)
    a = float(tr((0, 0), (0.4, 0), (0.7, 1, ease_out), (1.1, 1), (1.4, 0, smooth))(t))
    eye(p, a, 1.0)
    return ground_fit(S, p)


def _on_side(p, k):
    """lying on its right side: the long neck and head flat, the tail too"""
    add(p, "root", rot=(0, 0, 82 * k))
    T.neck(p, (-2 * k, 0, -10 * k)); add(p, "skull", rot=(-4 * k, 0, -8 * k))


def knocked_out(t):
    """out cold on its side; slow breathing, the jaw slack, the upper leg loose"""
    p = {}; br = math.sin(W(t, 4.0))
    fold(p, 0.7); _on_side(p, 1.0)
    add(p, "body", rot=(0.8 * br, 0, 0)); jaw(p, -6 - 1.5 * br)
    add(p, "thigh_l", rot=(16, 0, 0)); add(p, "shin_l", rot=(14, 0, 0))
    arms(p, 18)
    return ground_fit(S, p)


def wake(t):
    """from the knockout: rolls onto its belly, shakes the long head, stands up slowly with a stagger"""
    p = {}
    roll = float(tr((0, 1), (0.3, 1), (1.0, 0, ease_out), (3.0, 0))(t))
    k = float(tr((0, 0.75), (1.0, 1.0), (1.6, 1.0), (2.4, 0, smooth), (3.0, 0))(t))
    fold(p, k, head_down=0.4 * roll); _on_side(p, roll)
    env = math.exp(-((t - 1.3) / 0.2) ** 2)
    add(p, "skull", rot=(0, 6 * env * math.sin(2 * math.pi * 6 * t), 14 * env * math.sin(2 * math.pi * 6 * t)))
    st = window(t, 2.3, 2.95, 0.15)
    add(p, "body", rot=(0, 0, 4 * st * math.sin(2 * math.pi * 1.4 * t)))
    return ground_fit(S, p)


def death(t):
    """the legs give out, it drops onto the chest and rolls on its side; the long neck and the head come down last"""
    p = {}
    g = float(tr((0, 0), (0.4, 0.2), (0.95, 0.85, ease_in), (3.0, 0.85))(t))
    pitch = float(tr((0, 0), (0.7, -5), (0.95, -8, ease_in), (1.3, -3), (3.0, -3))(t))
    rl = float(tr((0, 0), (1.0, 0), (1.45, 1.03, ease_in), (1.6, 0.95), (1.75, 1.0), (3.0, 1.0))(t))
    fold(p, g); add(p, "body", rot=(pitch, 0, 0)); _on_side(p, rl)
    late = float(tr((0, 0), (1.2, 0), (1.5, 1, ease_out), (1.9, 0, ease_in), (3.0, 0))(t))   # the neck held up, then drops
    T.neck(p, (14 * late, 0, 0))
    jaw(p, -18 * window(t, 0.1, 0.9) - 8 * smooth((t - 1.8) / 0.4))
    tail(p, pitch=3 * smooth((t - 0.9) / 0.5))
    arms(p, 20 * smooth((t - 1.1) / 0.3))
    return ground_fit(S, p)


# ------------------------------------------------------------------ small gestures
def hurt(t):
    """the neck pulls in and the body flinches a step to the side"""
    p = {}
    k = float(tr((0, 0), (0.08, 1, ease_out), (0.6, 0))(t))
    add(p, "body", rot=(4 * k, -4 * k, 4 * k), pos=(-1.5 * k, 0, 2 * k))
    T.neck(p, (8 * k, -10 * k, 0)); add(p, "skull", rot=(4 * k, -4 * k, 8 * k)); jaw(p, -16 * k)
    tail(p, yaw=5 * k)
    arms(p, -12 * k, 10 * k)
    return T.stand(p)


def sniff(t):
    """the snout goes down and follows the trail in long touches, then comes up into the wind"""
    p = {}
    d = float(tr((0, 0), (0.5, 1, ease_out), (1.9, 1), (2.4, 0, smooth), (2.8, 0))(t))
    y = 10 * math.sin(2 * math.pi * (t - 0.5) / 1.4) * window(t, 0.5, 1.9, 0.2)
    add(p, "body", rot=(-4 * d, 0, 0), pos=(0, -2 * d, 0))
    T.neck(p, (-20 * d, y, 0))
    sn = sum(math.exp(-((t - c) / 0.05) ** 2) for c in (0.8, 0.95, 1.5, 1.65, 2.5))
    add(p, "skull", rot=(-6 * d + 2.5 * sn + 8 * window(t, 2.3, 2.7, 0.1), y * 0.4, 0)); jaw(p, -0.5 - 1.5 * sn)
    tail_wave(p, t, 2.8, 1.5)
    return T.stand(p)


def shake(t):
    """the shake runs from the snout down the neck and the body to the tip of the tail"""
    p = {}; e = window(t, 0.2, 1.6, 0.15); f = 2 * math.pi * 5.0 * t
    add(p, "body", rot=(0, 2 * e * math.sin(f - 1.0), 5 * e * math.sin(f - 0.8)))
    T.neck(p, (0, 6 * e * math.sin(f), 12 * e * math.sin(f + 0.3))); add(p, "skull", rot=(0, 5 * e * math.sin(f + 0.6), 14 * e * math.sin(f + 0.8)))
    jaw(p, -3 * e)
    for i, (b, k) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(0, 4 * e * k * math.sin(f - 1.6 - 0.7 * i), 0))
    arms(p, -6 * e, 6 * e * math.sin(f))
    return T.stand(p)


def yawn(t):
    """the long jaws open enormous and the head tips over to one side"""
    p = {}
    k = float(tr((0, 0), (0.8, 1, ease_out), (1.9, 1), (2.5, 0, ease_in), (3.0, 0))(t))
    add(p, "body", rot=(2 * k, 0, 0))
    T.neck(p, (8 * k, 6 * k, 0)); add(p, "skull", rot=(8 * k, 0, -14 * k)); jaw(p, -52 * k)
    arms(p, -14 * k, 10 * k)
    return T.stand(p)


def stretch(t):
    """the neck stretched far forward and low, the back arched; then one leg pushed back, then the other"""
    p = {}
    a = float(tr((0, 0), (0.7, 1, ease_out), (1.6, 1), (2.0, 0))(t))
    b = window(t, 1.5, 2.2, 0.15); c = window(t, 2.5, 3.2, 0.15)
    add(p, "body", rot=(-5 * a, 0, 0), pos=(0, -4 * a, 0))
    T.neck(p, (-10 * a + 4 * (b + c), 0, 0)); add(p, "skull", rot=(6 * a, 0, 0)); jaw(p, -3 * a)
    tail(p, pitch=-2 * a)
    arms(p, -14 * a, 10 * a)
    T.plant(p, "l", 3 * b, -8 * b, -18 * b, 10 * b)
    T.plant(p, "r", 3 * c, -8 * c, -18 * c, 10 * c)
    return p


def jaw_rub(t):
    """after eating: the head down on its side, the snout rubbed along the ground to clean the mouth"""
    p = {}
    k = float(tr((0, 0), (0.6, 1, ease_out), (2.6, 1), (3.2, 0, smooth))(t))
    rub = math.sin(2 * math.pi * 1.3 * (t - 0.6)) * window(t, 0.7, 2.6, 0.15)
    add(p, "body", rot=(-10 * k, 0, 0), pos=(0, -5 * k, 2 * rub * k))
    T.neck(p, (-22 * k + 3 * rub, 10 * k, 0)); add(p, "skull", rot=(-12 * k, 0, -30 * k))
    tail(p, pitch=6 * k, yaw=-3 * k)
    T.plant(p, "l", 0, -3 * k, 0, 0); T.plant(p, "r", 0, 2 * k, 0, 0)
    return p


# ------------------------------------------------------------------ eating and drinking
def eat(t):
    """the foot pins the meat, the jaws bite and the head tears sideways, twice; then a toss of the head to swallow"""
    p = {}
    down = float(tr((0, 0), (0.4, 1, ease_out), (2.4, 1), (2.6, 0.2, ease_out), (3.4, 0))(t))
    tears = [window(t, c, c + 0.35, 0.08) for c in (0.8, 1.6)]
    tear = tears[0] - tears[1]                      # one to each side
    bite = sum(math.exp(-((t - c) / 0.08) ** 2) for c in (0.6, 1.4))
    toss = math.exp(-((t - 2.8) / 0.12) ** 2)
    add(p, "body", rot=(-13 * down, 3 * tear, 2 * tear), pos=(0, -6 * down, 0))
    T.neck(p, (-22 * down + 16 * toss, 16 * tear, 0)); add(p, "skull", rot=(-10 * down + 10 * toss, 10 * tear, 12 * tear))
    jaw(p, -18 * bite - 3 * down - 16 * toss)
    tail(p, pitch=7 * down, yaw=-4 * tear)
    T.plant(p, "l", 0, -6 * down, 0, 0)
    T.plant(p, "r", 0, 0, 0, 0)
    arms(p, -6 * down)
    return p


def drink(t):
    """legs spread and bent, the chest low, only the tip of the snout in the water; lifts the head to swallow, twice"""
    p = {}
    down = float(tr((0, 0), (0.6, 1, ease_out), (3.4, 1), (4.0, 0))(t))
    up = sum(window(t, c, c + 0.45, 0.12) for c in (1.6, 2.8))
    lap = sum(math.exp(-((t - c) / 0.05) ** 2) for c in (0.9, 1.1, 1.3, 2.1, 2.3, 2.5))
    add(p, "body", rot=(-14 * down + 7 * up, 0, 0), pos=(0, -9 * down + 3 * up, 0))
    T.neck(p, (-30 * down + 20 * up, 0, 0)); add(p, "skull", rot=(-8 * down + 10 * up, 0, 0))
    jaw(p, -5 * lap - 2 * down)
    tail(p, pitch=8 * down - 4 * up)
    for s, sx in (("l", 1), ("r", -1)): add(p, f"thigh_{s}", rot=(0, 0, 6 * sx * down))
    T.plant(p, "l", 0, -3 * down, 0, 0); T.plant(p, "r", 0, 3 * down, 0, 0)
    return p


# ------------------------------------------------------------------ swimming
def swim(t):
    """the legs paddle in turn, the body low in the water, the head held up and level; the long tail sculls"""
    Tc = 1.5; w = W(t, Tc); p = {}
    add(p, "body", rot=(3 + 1.5 * math.sin(2 * w), 2 * math.sin(w), 3 * math.sin(w + 0.4)), pos=(0, 1.2 * math.sin(2 * w), 0))
    T.neck(p, (12 - 1.5 * math.sin(2 * w + 0.5), -2 * math.sin(w), 0)); add(p, "skull", rot=(-4, 0, 0))
    for i, (b, k) in enumerate(zip(TAILS, BEND)):
        add(p, b, rot=(2 * k, 8 * k * math.sin(w - 0.8 - 0.6 * i), 0))
    for s, o in SIDES:
        f = w + o * 2 * math.pi
        add(p, f"thigh_{s}", rot=(-14 + 30 * math.sin(f), 0, 0)); add(p, f"shin_{s}", rot=(-20 - 24 * math.cos(f), 0, 0))
        add(p, f"foot_{s}", rot=(26 + 20 * math.cos(f + 0.6), 0, 0)); add(p, f"toes_{s}", rot=(-24 * math.sin(f + 1.0), 0, 0))
    arms(p, -18, 14)
    return p


# ------------------------------------------------------------------ with its owner
def beg(t):
    """asks the owner for food: the head low and on its side, one eye on the owner, a small click of the jaws"""
    p = {}; br = math.sin(W(t, 2.0))
    add(p, "body", rot=(-3 + 0.6 * br, 0, 0), pos=(0, -1.5, 0))
    eye(p, 0.7 + 0.15 * br, 1.0, low=6)
    clk = sum(math.exp(-((t - c) / 0.04) ** 2) for c in (0.4, 0.55, 1.4))
    jaw(p, -6 * clk)
    tail(p, yaw=2 * math.sin(W(t, 2.0)), pitch=2)
    return T.stand(p)


def tame(t):
    """the moment it accepts its owner: the head goes down to the ground in front of them and turns on its side, one
    eye on them; then it lifts it calmly"""
    p = {}
    k = float(tr((0, 0), (0.6, 1, ease_out), (1.6, 1), (2.4, 0, smooth))(t))
    add(p, "body", rot=(-8 * k, 0, 0), pos=(0, -4 * k, 0))
    T.neck(p, (-18 * k, 0, 0)); eye(p, k, 1.0); jaw(p, -2 * k)
    tail(p, pitch=5 * k)
    arms(p, -4 * k)
    return T.stand(p)


ANIMS = {
    "idle": (idle, 8.0, True, "Parado", "base: cabeça baixa; de vez em quando deita a cabeça e olha com um olho"),
    "look_side": (look_side, 3.6, False, "Parado", "olha de lado com um olho, depois com o outro"),
    "eye_aim": (eye_aim, 1.5, False, "Combate", "olho de lado: parado depois do corte, mirando a presa com um olho"),
    "walk": (walk, WALK[0], True, "Movimento", "passada longa e pesada, quadril rolando, cabeça parada"),
    "run": (run, MARCH[0], True, "Movimento", "marcha forçada: sempre um pé no chão, sem arrancada"),
    "stalk": (stalk, WALK[0] * 1.5, True, "Movimento", "chegando perto, baixo, pescoço esticado"),
    "back_off": (back_off, 1.6, True, "Combate", "recuo: passos curtos para trás, cabeça na presa"),
    "circle": (circle, 1.8, True, "Combate", "cercar: anda de lado em volta da presa, olhando com um olho"),
    "slash": (slash, 1.4, False, "Combate", "corte: morde de lado, puxa cortando, solta e recua"),
    "attack_quick": (attack_quick, 1.0, False, "Combate", "corte curto (montado)"),
    "lunge": (lunge, 1.6, False, "Combate", "bote baixo na perna de uma presa grande"),
    "rip": (rip, 2.2, False, "Combate", "arrancar: segura e sacode a cabeça como um tubarão"),
    "stomp": (stomp, 1.7, False, "Combate", "pisão em coisa pequena junto aos pés"),
    "hurt": (hurt, 0.6, False, "Combate", "ao levar dano"),
    "death": (death, 3.0, False, "Combate", "cai de peito e rola de lado; o pescoço bate por último"),
    "gape": (gape, 2.8, False, "Voz", "mostrar a boca: aviso de perfil com a boca enorme aberta"),
    "roar": (roar, 3.4, False, "Voz", "rugido baixo e para a frente"),
    "roar_loud": (roar_loud, 4.4, False, "Voz", "rugido forte: um passo à frente, três pulsos"),
    "call": (call, 2.6, False, "Voz", "chamado do par: curto e grave"),
    "crest_show": (crest_show, 3.0, False, "Voz", "exibição do macho: os calombos vermelhos de perfil"),
    "sniff": (sniff, 2.8, False, "Parado", "segue o rastro em toques longos"),
    "shake": (shake, 1.8, False, "Parado", "sacode do focinho à ponta da cauda"),
    "yawn": (yawn, 3.0, False, "Parado", "bocejo enorme com a cabeça de lado"),
    "stretch": (stretch, 3.5, False, "Parado", "estica o pescoço e empurra uma perna de cada vez"),
    "jaw_rub": (jaw_rub, 3.2, False, "Comer", "limpar a boca: esfrega o focinho no chão"),
    "eat": (eat, 3.4, False, "Comer", "prende com o pé, corta com puxões de lado, joga a cabeça para engolir"),
    "drink": (drink, 4.0, False, "Comer", "abre as pernas e encosta a ponta do focinho na água"),
    "swim": (swim, 1.5, True, "Movimento", "nadando, a cauda comprida rema"),
    "sit": (sit, 6.0, True, "Descanso", "deitado acordado, olhando com um olho"),
    "sleep": (sleep, 9.0, True, "Descanso", "dorme com o pescoço e a cabeça esticados no chão"),
    "wake_sleep": (wake_sleep, 2.4, False, "Descanso", "acorda: a cabeça, o peito, depois o quadril"),
    "knocked_out": (knocked_out, 4.0, True, "Descanso", "nocauteado, deitado de lado"),
    "wake": (wake, 3.0, False, "Descanso", "acorda do nocaute: rola, sacode a cabeça, levanta devagar"),
    "beg": (beg, 2.0, True, "Domado", "pede comida olhando o dono com um olho"),
    "tame": (tame, 2.4, False, "Domado", "abaixa a cabeça e olha o dono de lado ao ser domado"),
}

# 06/11: the fluid set and the fighting moves (gigaflow.py, from docs/estudos/08 and 10): the names above keep their
# length and hit times and get their fluid version; the new ones join the list
import gigaflow as FLOW  # noqa: E402
for _name, _fn in FLOW.REBIND.items():
    ANIMS[_name] = (_fn,) + ANIMS[_name][1:]
ANIMS.update(FLOW.NEW)

# 06/11: the epic duel's committed moves (gigafight.py, from docs/estudos/10): duel_lunge (its "lunge" name is taken by
# the low strike at the leg), parry, stagger (fixed lengths)
import gigafight as FIGHT  # noqa: E402
ANIMS.update(FIGHT.NEW)
