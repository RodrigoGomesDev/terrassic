"""Gallimimus animations, written for it from its own study (page "Gallimimus: estudo e modelo", section "movimento").

Only the plumbing is shared (anim2: easing, leg IK with planted feet, export; theropod.Plan: plant/stand, spreading a
rotation over the neck bones). The poses are its own, from what the study says the animal was:
- a cursor built like an ostrich: the body carried level between long legs, the stride long and the foot folded high
  with the toes curled in the swing (as birds do), the neck swinging fore and aft with the steps;
- at speed the neck stretches forward and low, the tail is a level counterweight and the feathered arms open a
  little as rudders (ostriches use their wings to balance and turn); escaping, it jinks: a hard side-step;
- the eyes are on the sides of the head: it looks at things with ONE eye, the head turned and tilted (a bird's
  look), and a sentinel stands tall with the neck upright and scans in jerks;
- a toothless beak: it nips, pecks and tosses food back to swallow; it swallows grit (gastroliths, known in
  ornithomimids: Kobayashi et al. 1999), dabbles in shallow water (the filter-feeding idea of Norell et al. 2001,
  disputed: here it is one behaviour among others), hooks branches down with its hands (Nicholls & Russell 1985);
- the adults' feathered arms (Zelenitsky et al. 2012): the male's display, preening, brooding the clutch under them;
- it sleeps like Mei long and the birds: sitting on folded legs, the neck curled back along the body and the head
  tucked in beside the arm (Xu & Norell 2004).
"""
import math
import os
import sys
_H = os.path.dirname(os.path.abspath(__file__))
_E = os.path.join(_H, "..", "_engine")
sys.path[:0] = [_H, _E, os.path.join(_E, "plans")]
import proto as P
import galli
import theropod
from anim2 import add, Track, smooth, ease_out, ease_in, back_out, lowest
from theropod import window, W, SIDES

TAILS = ("tail1", "tail2", "tail3", "tail4", "tail5", "tail6")
NECKS = ("neck1", "neck2", "neck3")


def model():
    m = galli.build(saddle_on=True); P.pack(m, galli.TEX_W); return m.spec()


S = model()
T = theropod.Plan(S, K=1.0, necks=NECKS, tails=TAILS)
SADDLE_MATS = galli.SADDLE_MATS


def tr(*keys): return Track(keys)


def tail(p, yaw=0.0, pitch=0.0, lag=0.0, t=0.0):
    """the tail bends evenly along its length (no stiff half: the ornithomimid tail is long and supple at the root,
    straight at the end); lag delays the far bones for a whip"""
    for k, b in enumerate(TAILS):
        w = (1.0, 0.9, 0.75, 0.6, 0.45, 0.35)[k]
        add(p, b, rot=(pitch * w, yaw * w * (1 + lag * k * 0.3), 0))


def neck(p, pitch=0.0, yaw=0.0, roll=0.0, s=(0.45, 0.3, 0.25)):
    """a neck rotation spread over the three neck bones, most at the base (the S straightens from the shoulders)"""
    for b, k in zip(NECKS, s):
        add(p, b, rot=(pitch * k, yaw * k * 1.0, roll * k))


def eye_look(p, side=1.0, k=1.0, tilt=1.0):
    """the bird's look: the head turned to bring ONE eye on the thing and tilted so that eye looks up/forward"""
    add(p, "skull", rot=(2 * k, 28 * side * k, -18 * side * k * tilt))


def arms(p, a=0.0, f=0.0, out=0.0, h=0.0):
    """arm/forearm pitch, out = spread sideways (the wing fan opens with it), h = hand"""
    for s, sx in (("l", 1), ("r", -1)):
        add(p, f"arm_{s}", rot=(a, 0, out * sx)); add(p, f"forearm_{s}", rot=(f, 0, 0.3 * out * sx))
        if h: add(p, f"hand_{s}", rot=(h, 0, 0))


def snap(t, keys, dur=0.1):
    """head aim in quick jerks that stop dead (a bird's head): keys = [(t, (pitch, yaw, roll))]"""
    cur = (0.0, 0.0, 0.0)
    for tk, v in keys:
        if t < tk: break
        u = ease_out(min(1.0, (t - tk) / dur))
        cur = tuple(cur[i] + (v[i] - cur[i]) * u for i in range(3))
    return cur


REACH = {"body": (-20, 0, 0), "neck1": (-95, 0, 0), "neck2": (5, 0, 0), "neck3": (30, 0, 0), "skull": (25, 0, 0)}


def reach(p, k):
    """head down to the ground: the S of the neck opens from the shoulders and the body tips forward over the legs
    (k = 1: the beak tip 6 px off the ground, pointing down and forward)"""
    for b, r in REACH.items(): add(p, b, rot=tuple(x * k for x in r))


# ------------------------------------------------------------------ gait (its own: level body, swinging neck, curled toes)
WALK = (1.2, 56, 0.62, 9, 1.0)       # cycle s, stride px, duty, foot lift px, body bob px
RUN = (0.5, 120, 0.34, 16, 2.4)


def gait(t, Tc, stride, duty, lift, bob, lean=0.0, drop=0.0, head=0.0, sway=1.0, stance_clear=-0.05, swing=1.0,
         arm_out=0.0, turn=None):
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    if turn: add(p, "body", rot=turn[0], pos=turn[1])
    bp = 0.6 * math.sin(2 * w - 0.4); by = 1.4 * sway * math.sin(w); br = 1.8 * sway * math.sin(w + 0.35)
    add(p, "body", rot=(lean + bp, by, br), pos=(0, -bob * math.cos(2 * w - 0.9) - 0.5 - drop, 0))
    # the neck: fore and aft with each step (the head is pushed forward as a foot lands, then held while the body
    # catches up), the base cancels the body's roll so the head travels level
    nod = swing * 4.0 * math.sin(2 * w - 1.3)
    neck(p, head - lean * 0.8 - bp + nod, -by * 0.7, -br * 0.8)
    add(p, "skull", rot=(-head * 0.3 - nod * 0.7, 0, -br * 0.3))
    tail(p, yaw=-2.4 * sway * math.sin(w - 0.9), pitch=lean * 0.4 + 0.8 * math.sin(2 * w - 1.4))
    arms(p, 2 * math.sin(2 * w - 2.0), 0, arm_out)
    for s, o in SIDES:
        u = (ph + o) % 1.0
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0
            meta = 30 * smooth(max(0, (st - 0.55) / 0.45)); toe = 0.0; clear = stance_clear
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e
            ly = lift * math.sin(math.pi * min(1, sw * 1.1)) ** 1.1
            meta = 30 * (1 - smooth(sw / 0.4)) - 30 * math.sin(math.pi * sw)
            toe = -55 * math.sin(math.pi * min(1, sw * 1.15)) + 6 * smooth((sw - 0.75) / 0.25)   # the toes curl shut
            clear = 1.2 * math.sin(math.pi * sw) ** 0.5
        T.plant(p, s, ly, dz - 2, meta, toe, clear)
    return p


def walk(t):
    return gait(t, *WALK)


def run(t, turn=None):
    """the sprint: the body drops a little and levels, the neck reaches forward and low, the tail a level beam, the
    arms held a little open (balance)"""
    p = gait(t, *RUN, lean=6, drop=3, head=-36, sway=0.5, stance_clear=0.2, swing=0.5, arm_out=10, turn=turn)
    arms(p, -16, 14)
    tail(p, pitch=-3)
    return p


def jink(t):
    """the escape side-step at full speed: it leans hard to one side, the wing on the inside opens wide as a rudder,
    the tail swings out, and straightens again in the next stride"""
    k = float(tr((0, 0), (0.12, 1, ease_out), (0.36, 1), (0.6, 0))(t))
    p = run(t % RUN[0], turn=((0, 16 * k, 12 * k), (1.5 * k, -1.0 * k, 0)))
    neck(p, 0, -20 * k, -10 * k)
    tail(p, yaw=-12 * k, lag=0.6)
    add(p, "arm_l", rot=(-10 * k, 0, 40 * k)); add(p, "forearm_l", rot=(14 * k, 0, 12 * k))
    return p


def swim(t):
    """the long legs paddle in turn, the body low, the neck up and the head level; the tail sculls at the root"""
    Tc = 1.2; w = W(t, Tc); p = {}
    add(p, "body", rot=(2 + 1.5 * math.sin(2 * w), 2 * math.sin(w), 3 * math.sin(w + 0.4)), pos=(0, 1.0 * math.sin(2 * w), 0))
    neck(p, 18 - 2 * math.sin(2 * w + 0.5), -2 * math.sin(w)); add(p, "skull", rot=(-10, 0, 0))
    tail(p, yaw=6 * math.sin(w - 0.8), pitch=2)
    for s, o in SIDES:
        f = w + o * 2 * math.pi
        add(p, f"thigh_{s}", rot=(-10 + 30 * math.sin(f), 0, 0)); add(p, f"shin_{s}", rot=(-24 - 30 * math.cos(f), 0, 0))
        add(p, f"foot_{s}", rot=(30 + 26 * math.cos(f + 0.6), 0, 0)); add(p, f"toes_{s}", rot=(-40 * math.sin(f + 1.0), 0, 0))
    arms(p, -14, 10, 6)
    return p


# ------------------------------------------------------------------ standing
def idle(t):
    """breathing; it looks about with one eye at a time, in quick jerks, and holds each look"""
    p = {}; br = math.sin(W(t, 2.0))
    add(p, "body", rot=(0.6 * br, 0, 0), pos=(0, 0.25 * br, 0))
    hp, hy, hr = snap(t, [(0.0, (0, 0, 0)), (0.9, (2, 22, -14)), (2.3, (4, 30, -18)), (3.1, (0, 0, 0)),
                          (4.2, (-2, -26, 16)), (5.6, (3, -14, 8)), (6.8, (0, 0, 0))])
    neck(p, hp * 0.6 - 0.6 * br, hy * 0.6)
    add(p, "skull", rot=(hp * 0.4, hy * 0.4, hr))
    tail(p, yaw=1.6 * math.sin(W(t, 8.0)), pitch=0.5 * math.sin(W(t, 2.0) - 0.8))
    arms(p, 1.2 * br)
    return T.stand(p)


def sentinel(t):
    """the flock's lookout: it rises tall on straight legs, the neck upright, and scans the horizon with one eye and
    the other in sharp jerks, freezing between them"""
    p = {}
    k = float(tr((0, 0), (0.5, 1, ease_out), (3.6, 1), (4.2, 0))(t))
    add(p, "body", rot=(6 * k, 0, 0), pos=(0, 3 * k, 0))
    neck(p, 34 * k, 0)
    add(p, "skull", rot=(-24 * k, 0, 0))
    hp, hy, hr = snap(t, [(0.0, (0, 0, 0)), (0.7, (0, 40, -20)), (1.5, (2, 70, -26)), (2.2, (0, -40, 20)),
                          (2.9, (2, -72, 26)), (3.5, (0, 0, 0))], dur=0.08)
    neck(p, 0, hy * 0.5 * k, 0); add(p, "skull", rot=(hp * k, hy * 0.5 * k, hr * k))
    tail(p, pitch=-1.2 * k)
    arms(p, -6 * k, 0)
    T.plant(p, "l", 0, 0, -12 * k, 0); T.plant(p, "r", 0, 0, -12 * k, 0)
    return p


def preen(t):
    """feather care: the neck curls round and the beak runs through the wing fan, then nibbles the flank"""
    p = {}
    k = float(tr((0, 0), (0.6, 1, ease_out), (3.4, 1), (4.0, 0))(t))
    a = window(t, 0.7, 2.0, 0.2); b = window(t, 2.0, 3.3, 0.2)
    nib = math.sin(2 * math.pi * 6 * t)
    add(p, "body", rot=(2 * k, 6 * k, -3 * k))
    neck(p, -18 * k, 90 * k, 10 * k, s=(0.3, 0.35, 0.35))
    add(p, "skull", rot=(-40 * a - 26 * b + 3 * nib * k, 30 * k, 10 * k))
    add(p, "jaw", rot=(-6 * k * max(0, nib), 0, 0))
    add(p, "arm_l", rot=(-8 * a, 0, 26 * a)); add(p, "forearm_l", rot=(10 * a, 0, 10 * a))
    tail(p, yaw=-6 * k)
    return T.stand(p)


def wing_display(t):
    """the male's courtship (Zelenitsky et al. 2012: the adult wing fans were for display; the ostrich's dance): he
    drops on his heels, spreads both arms with the plumes open, pumps them in turn and swings the neck from side to
    side, then rises"""
    p = {}
    k = float(tr((0, 0), (0.6, 1, ease_out), (4.2, 1), (4.8, 0))(t))
    f = 2 * math.pi * 1.1 * t
    add(p, "body", rot=(-6 * k, 0, 6 * k * math.sin(f)), pos=(0, -10 * k, 0))
    neck(p, -12 * k, 34 * k * math.sin(f), 10 * k * math.sin(f), s=(0.5, 0.3, 0.2))
    add(p, "skull", rot=(10 * k, -10 * k * math.sin(f), 0))
    for s, sx, ph in (("l", 1, 0.0), ("r", -1, math.pi)):
        pump = 0.5 + 0.5 * math.sin(f + ph)
        add(p, f"arm_{s}", rot=(-30 * k, 0, sx * (40 + 30 * pump) * k))
        add(p, f"forearm_{s}", rot=(50 * k, 0, sx * 10 * k))
    tail(p, pitch=-2 * k, yaw=4 * k * math.sin(f - 1))
    T.plant(p, "l", 0, -2 * k, 18 * k, 0); T.plant(p, "r", 0, 2 * k, 18 * k, 0)
    return p


# ------------------------------------------------------------------ feeding
def eat(t):
    """pecks: quick nips at the food, and after each mouthful the head tosses back to swallow (no teeth to chew)"""
    p = {}
    down = float(tr((0, 0), (0.3, 1, ease_out), (2.4, 1), (2.8, 0))(t))
    pecks = sum(math.exp(-((t - c) / 0.05) ** 2) for c in (0.5, 0.8, 1.5, 1.75))
    toss = sum(math.exp(-((t - c) / 0.09) ** 2) for c in (1.15, 2.2))
    reach(p, 0.8 * down * (1 - 0.9 * toss))
    neck(p, 30 * toss - 6 * pecks, 0)
    add(p, "skull", rot=(34 * toss - 6 * pecks, 0, 0))
    add(p, "jaw", rot=(-10 * pecks - 14 * toss, 0, 0))
    tail(p, pitch=2 * down)
    return T.stand(p)


def graze(t):
    """crops low plants walking slowly: dips, nips twice with a side jerk of the head, lifts and swallows"""
    p = {}
    down = float(tr((0, 0), (0.4, 1, ease_out), (2.6, 1), (3.0, 0.3), (3.4, 0))(t))
    nip = sum(math.exp(-((t - c) / 0.06) ** 2) for c in (0.8, 1.3, 1.9, 2.4))
    jerk = math.sin(2 * math.pi * 2.5 * t) * window(t, 0.7, 2.5, 0.15)
    reach(p, down)
    neck(p, 0, 6 * jerk); add(p, "skull", rot=(0, 8 * jerk, 10 * jerk))
    add(p, "jaw", rot=(-8 * nip, 0, 0))
    tail(p, pitch=2 * down)
    step = window(t, 1.5, 2.0, 0.1)
    T.plant(p, "l", 4 * step, -6 * smooth((t - 1.5) / 0.5), 0, -20 * step)
    T.plant(p, "r")
    return p


def grit(t):
    """it picks up a pebble (gastroliths: the stomach stones of the ornithomimids, Kobayashi et al. 1999), lifts the
    head high and swallows it with a gulp that runs down the neck"""
    p = {}
    down = float(tr((0, 0), (0.4, 1, ease_out), (1.2, 1), (1.5, 0, ease_out), (2.8, 0))(t))
    up = window(t, 1.5, 2.5, 0.15)
    pick = math.exp(-((t - 0.95) / 0.07) ** 2)
    gulp = [math.exp(-((t - c) / 0.08) ** 2) for c in (1.9, 2.05, 2.2)]
    reach(p, down)
    neck(p, 20 * up, 0); add(p, "skull", rot=(26 * up - 4 * pick, 0, 0))
    add(p, "body", rot=(3 * up, 0, 0))
    add(p, "jaw", rot=(-12 * pick, 0, 0))
    for b, g in zip(NECKS[::-1], gulp): add(p, b, rot=(-3 * g, 0, 0))        # the lump going down the neck
    tail(p, pitch=2 * down)
    return T.stand(p)


def sift(t):
    """in shallow water: the beak goes in and dabbles from side to side in short bursts, then lifts to drain (the
    filter-feeding idea of Norell et al. 2001; Barrett 2005 argues for plants: here it is one behaviour among others)"""
    p = {}
    down = float(tr((0, 0), (0.5, 1, ease_out), (3.2, 1), (3.6, 0.2), (4.0, 0))(t))
    burst = window(t, 0.7, 1.6, 0.1) + window(t, 2.0, 3.0, 0.1)
    dab = math.sin(2 * math.pi * 7 * t) * burst
    lift = window(t, 1.6, 2.0, 0.1)
    reach(p, down * (1 - 0.35 * lift))
    neck(p, 0, 4 * dab); add(p, "skull", rot=(8 * lift, 10 * dab, 0))
    add(p, "jaw", rot=(-3 * burst * (0.5 + 0.5 * math.sin(2 * math.pi * 14 * t)) - 6 * lift, 0, 0))
    tail(p, pitch=2 * down)
    for s, sx in (("l", 1), ("r", -1)): add(p, f"thigh_{s}", rot=(0, 0, 4 * sx * down))
    T.plant(p, "l", 0, -3 * down, 0, 0); T.plant(p, "r", 0, 3 * down, 0, 0)
    return p


def browse(t):
    """reaches up to a branch, hooks it down with one hand (the three fingers as a hook, Nicholls & Russell 1985) and
    nips the leaves off it, then lets it go"""
    p = {}
    k = float(tr((0, 0), (0.5, 1, ease_out), (3.0, 1), (3.5, 0))(t))
    hook = float(tr((0, 0), (0.5, 0), (0.9, 1, ease_out), (2.8, 1), (3.1, 0))(t))
    pull = window(t, 1.0, 2.8, 0.25)
    nip = sum(math.exp(-((t - c) / 0.06) ** 2) for c in (1.5, 1.85, 2.2, 2.5))
    add(p, "body", rot=(10 * k - 4 * pull, 0, 0), pos=(0, 2 * k, 0))
    neck(p, 30 * k - 8 * pull, 0); add(p, "skull", rot=(-20 * k + 10 * nip, 0, 0))
    add(p, "jaw", rot=(-12 * nip, 0, 0))
    add(p, "arm_l", rot=(-70 * hook + 30 * pull, 0, 8 * hook)); add(p, "forearm_l", rot=(70 * hook - 20 * pull, 0, 0))
    add(p, "hand_l", rot=(-40 * hook, 0, 0))
    tail(p, pitch=-2 * k)
    T.plant(p, "l", 0, 0, -10 * k, 0); T.plant(p, "r", 0, 0, -10 * k, 0)
    return p


# ------------------------------------------------------------------ combat (it runs; cornered, it kicks)
def attack(t):
    """the kick of a cursor (as an ostrich defends itself): weight onto one leg, the other knee comes up and the
    foot strikes forward and down with the blunt claws; a peck with the beak follows"""
    p = {}
    up = float(tr((0, 0), (0.25, 1, ease_out), (0.4, 1), (0.52, -0.2, ease_in), (0.75, 0), (1.0, 0))(t))
    strike = float(tr((0, 0), (0.38, 0), (0.5, 1, ease_in), (0.62, 0.6), (0.9, 0))(t))
    peck = math.exp(-((t - 0.72) / 0.06) ** 2)
    add(p, "body", rot=(4 * max(0, up) - 3 * strike, 0, -3 * max(0, up)), pos=(-1.5 * max(0, up), 0, 0))
    neck(p, 6 * max(0, up) - 30 * peck, 0); add(p, "skull", rot=(-4 * peck, 0, 0))
    add(p, "jaw", rot=(-12 * peck, 0, 0))
    arms(p, -20 * max(0, up), 10, 18 * max(0, up))
    tail(p, pitch=1 * max(0, up))
    T.plant(p, "l")
    T.plant(p, "r", 22 * max(0, up) + 4 * strike, -14 * max(0, up) - 18 * strike, -30 * max(0, up) + 30 * strike, -30 * max(0, up), clear=None)
    return p


def hurt(t):
    """flinch: the body jerks away, the neck whips up and back, the wings flick open"""
    p = {}
    k = float(tr((0, 0), (0.08, 1, ease_out), (0.6, 0))(t))
    add(p, "body", rot=(4 * k, 0, 3 * k), pos=(0, 0, 2 * k))
    neck(p, 16 * k, -8 * k); add(p, "skull", rot=(10 * k, 0, 8 * k)); add(p, "jaw", rot=(-10 * k, 0, 0))
    tail(p, pitch=-3 * k, yaw=4 * k)
    arms(p, -14 * k, 10 * k, 24 * k)
    return T.stand(p)


# ------------------------------------------------------------------ resting: an ostrich's sit, a sleeping bird
def ground_fit(p):
    lo = lowest(S, p, skip_mats=SADDLE_MATS); add(p, "root", pos=(0, -lo, 0)); return p


LIE = 40.0
# the folded legs (searched over the joint angles: the metatarsus flat on the ground under the belly, the ankle
# behind, the toes in front, the knee up beside the belly); fold() blends to them so no leg flips mid-way
LIE_LEGS = {f"{b}_{s}": (a, 0, 0) for s, _ in SIDES for b, a in (("thigh", 54), ("shin", -92), ("foot", 114))}


def fold(p, k, neck_up=1.0):
    """k = 0 standing .. 1 sitting on its heels, the belly on the ground; the neck stays up (an ostrich sits upright)"""
    add(p, "body", rot=(2 * k, 0, 0), pos=(0, -LIE * k, 0))
    neck(p, 6 * k * neck_up, 0); add(p, "skull", rot=(-4 * k * neck_up, 0, 0))
    tail(p, pitch=-3 * k)
    arms(p, 4 * k)
    for n, r in LIE_LEGS.items(): add(p, n, rot=tuple(x * smooth(k) for x in r))
    return p


def sit(t):
    """sitting on its folded legs, awake: neck up, looking about with one eye"""
    p = {}; br = math.sin(W(t, 3.0))
    fold(p, 1.0); add(p, "body", rot=(0.7 * br, 0, 0))
    hp, hy, hr = snap(t, [(0.0, (0, 0, 0)), (1.2, (2, 24, -14)), (2.8, (0, 6, 0)), (4.1, (3, -22, 14)), (5.6, (0, 0, 0))])
    neck(p, -0.6 * br + hp * 0.5, hy * 0.6); add(p, "skull", rot=(hp * 0.5, hy * 0.4, hr))
    return ground_fit(p)


TUCK = {"neck1": (-48, 0, 0), "neck2": (8, 60, 0), "neck3": (10, 64, 0), "skull": (14, 40, -20)}


def tuck(p, k):
    """the sleeping bird's pose (Mei long, Xu & Norell 2004): the neck curled back along the left flank and the head
    tucked in beside the arm, the tail round the other side"""
    for b, r in TUCK.items(): add(p, b, rot=tuple(x * k for x in r))
    tail(p, yaw=-16 * k, pitch=-2 * k, lag=0.5)
    add(p, "arm_l", rot=(0, 0, 10 * k))


def sleep(t):
    p = {}; br = math.sin(W(t, 4.5))
    fold(p, 1.0); tuck(p, 1.0)
    add(p, "body", rot=(0.8 * br, 0, 0), pos=(0, 0.3 * br, 0))
    return ground_fit(p)


def wake_sleep(t):
    """from sleep: the head comes out from under the arm, a shake of the plumage, then it stands in one push"""
    p = {}
    tk = float(tr((0, 1), (0.6, 0, ease_out), (2.6, 0))(t))
    up = float(tr((0, 1), (1.5, 1), (2.2, 0, back_out), (2.6, 0))(t))
    fold(p, up); tuck(p, tk)
    sh = window(t, 0.8, 1.3, 0.08) * math.sin(2 * math.pi * 8 * t)
    add(p, "body", rot=(0, 0, 4 * sh)); arms(p, 0, 0, 12 * abs(sh))
    return ground_fit(p)


def brood(t):
    """on the nest: sitting over the clutch with both feathered arms spread over it like a hen (the brooding idea of
    Zelenitsky et al. 2012), turning an egg with the beak now and then"""
    p = {}; br = math.sin(W(t, 3.4))
    fold(p, 1.0)
    arms(p, -8, 6, 34)
    turn = window(t, 3.2, 4.6, 0.3)
    neck(p, -0.5 * br - 40 * turn, 0); add(p, "skull", rot=(-20 * turn, 0, 0))
    add(p, "body", rot=(0.7 * br, 0, 0))
    hp, hy, hr = snap(t, [(0.0, (0, 0, 0)), (1.0, (2, 22, -14)), (2.4, (0, 0, 0)), (5.2, (2, -20, 14)), (6.2, (0, 0, 0))])
    neck(p, hp * 0.5, hy * 0.6 * (1 - turn)); add(p, "skull", rot=(0, hy * 0.4 * (1 - turn), hr * (1 - turn)))
    return ground_fit(p)


def _on_side(p, k):
    """lying on its right side, the long neck laid out on the ground"""
    add(p, "root", rot=(0, 0, 80 * k))
    neck(p, -26 * k, 0, -10 * k); add(p, "skull", rot=(-6 * k, 0, -8 * k))


def knocked_out(t):
    """out cold on its side, the neck stretched on the ground, the upper leg loose; slow breaths"""
    p = {}; br = math.sin(W(t, 4.0))
    fold(p, 0.6, neck_up=0.0); _on_side(p, 1.0)
    add(p, "body", rot=(0.8 * br, 0, 0)); add(p, "jaw", rot=(-4 - 1.5 * br, 0, 0))
    add(p, "thigh_l", rot=(18, 0, 0)); add(p, "shin_l", rot=(20, 0, 0))
    arms(p, 14, 0, 10)
    return ground_fit(p)


def wake(t):
    """from the knockout: rolls onto its folded legs, lifts the neck in a wobble, shakes the head and stands"""
    p = {}
    roll = float(tr((0, 1), (0.3, 1), (0.9, 0, ease_out), (3.0, 0))(t))
    k = float(tr((0, 0.6), (0.9, 1.0), (1.8, 1.0), (2.5, 0, back_out), (3.0, 0))(t))
    fold(p, k, neck_up=1 - roll); _on_side(p, roll)
    env = math.exp(-((t - 1.4) / 0.2) ** 2)
    neck(p, -16 * roll + 6 * env * math.sin(2 * math.pi * 3 * t), 8 * env * math.sin(2 * math.pi * 3 * t))
    add(p, "skull", rot=(0, 10 * env * math.sin(2 * math.pi * 8 * t), 20 * env * math.sin(2 * math.pi * 8 * t)))
    st = window(t, 2.3, 3.0, 0.15)
    add(p, "body", rot=(0, 0, 4 * st * math.sin(2 * math.pi * 1.8 * t)))
    return ground_fit(p)


def death(t):
    """the legs buckle, it drops onto its heels and the chest, the long neck falls forward and lies along the ground,
    then the body rolls onto its side"""
    p = {}
    g = float(tr((0, 0), (0.3, 0.15), (0.8, 0.8, ease_in), (3.0, 0.8))(t))
    nk = float(tr((0, 0), (0.6, 0), (1.3, 1, ease_in), (1.45, 0.92), (1.6, 1.0), (3.0, 1.0))(t))
    rl = float(tr((0, 0), (1.3, 0), (1.8, 1.0, ease_in), (1.95, 0.94), (2.1, 1.0), (3.0, 1.0))(t))
    fold(p, g, neck_up=0.0)
    neck(p, 20 * window(t, 0.0, 0.6, 0.2) - 60 * nk * (1 - rl), 0)
    add(p, "skull", rot=(-10 * nk * (1 - rl), 0, 0))
    _on_side(p, rl)
    add(p, "jaw", rot=(-14 * window(t, 0.1, 0.7) - 6 * smooth((t - 1.8) / 0.4), 0, 0))
    arms(p, 0, 0, 30 * window(t, 0.2, 1.0, 0.2) + 10 * rl)
    tail(p, pitch=2 * smooth((t - 0.8) / 0.4))
    return ground_fit(p)


# ------------------------------------------------------------------ with its owner
def beg(t):
    """asks for food: quick little pecks in the air toward the owner, the head tilted to look with one eye"""
    p = {}; br = math.sin(W(t, 1.6))
    add(p, "body", rot=(-4 + 0.6 * br, 0, 0), pos=(0, -1.5, 0))
    pk = sum(math.exp(-((t - c) / 0.05) ** 2) for c in (0.3, 0.5, 1.1, 1.3))
    neck(p, -14 - 8 * pk, 0); eye_look(p, 1.0, 0.7)
    add(p, "skull", rot=(-6 * pk, 0, 0)); add(p, "jaw", rot=(-8 * pk, 0, 0))
    arms(p, -4, 0, 6 + 4 * math.sin(2 * math.pi * 6 * t))
    tail(p, yaw=2 * math.sin(W(t, 1.6)), pitch=2)
    return T.stand(p)


def tame(t):
    """the moment it accepts the owner: the neck lowers, the wings half open and close once, it shakes its plumage
    smooth and looks at them with one eye"""
    p = {}
    k = float(tr((0, 0), (0.5, 1, ease_out), (1.6, 1), (2.6, 0))(t))
    wing = window(t, 0.6, 1.4, 0.2)
    sh = window(t, 1.6, 2.1, 0.08) * math.sin(2 * math.pi * 9 * t)
    add(p, "body", rot=(-8 * k, 0, 4 * sh), pos=(0, -3 * k, 0))
    neck(p, -30 * k, 0); add(p, "skull", rot=(-8 * k, 0, 0))
    eye_look(p, -1.0, window(t, 1.9, 2.6, 0.15))
    arms(p, -10 * wing, 8 * wing, 30 * wing + 10 * abs(sh))
    tail(p, pitch=2 * k)
    return T.stand(p)


ANIMS = {
    "idle": (idle, 8.0, True, "Parado", "respira e olha com um olho de cada vez, em trancos de pássaro"),
    "walk": (walk, WALK[0], True, "Movimento", "passada longa de ave, corpo nivelado, pescoço vai e vem com o passo, dedos fecham no ar"),
    "run": (run, RUN[0], True, "Movimento", "corrida: pescoço esticado para frente e baixo, cauda reta, braços um pouco abertos"),
    "jink": (jink, 0.6, False, "Só dele", "na fuga, desvio brusco para o lado; a asa de dentro abre como leme"),
    "swim": (swim, 1.2, True, "Movimento", "as pernas remam, o pescoço em pé e a cabeça nivelada"),
    "sentinel": (sentinel, 4.2, False, "Só dele", "o vigia do bando: estica-se todo e varre o horizonte em trancos"),
    "preen": (preen, 4.0, False, "Só dele", "cuida das penas: passa o bico pelas penas do braço e pelo flanco"),
    "wing_display": (wing_display, 4.8, False, "Só dele", "a corte do macho: agacha, abre as asas e bombeia, balança o pescoço"),
    "eat": (eat, 2.8, False, "Comer", "bica e joga a cabeça para trás para engolir (não tem dentes)"),
    "graze": (graze, 3.4, False, "Comer", "corta planta baixa com trancos de lado, dá um passo"),
    "grit": (grit, 2.8, False, "Só dele", "engole uma pedrinha (gastrólito) e o bolo desce pelo pescoço"),
    "sift": (sift, 4.0, False, "Só dele", "na água rasa, peneira com o bico de um lado para o outro"),
    "browse": (browse, 3.5, False, "Só dele", "puxa um galho com a mão em gancho e belisca as folhas"),
    "attack": (attack, 1.0, False, "Combate", "o coice: levanta o joelho e golpeia à frente com o pé; uma bicada depois"),
    "hurt": (hurt, 0.6, False, "Combate", "ao levar dano: o pescoço chicoteia para trás e as asas abrem"),
    "death": (death, 3.0, False, "Combate", "as pernas dobram, o pescoço cai ao longo do chão, rola de lado"),
    "sit": (sit, 6.0, True, "Descanso", "sentado sobre as pernas dobradas, pescoço em pé, olhando"),
    "sleep": (sleep, 9.0, True, "Descanso", "dorme como ave: pescoço dobrado ao longo do corpo, cabeça junto ao braço"),
    "wake_sleep": (wake_sleep, 2.6, False, "Descanso", "tira a cabeça de baixo do braço, sacode as penas, levanta"),
    "brood": (brood, 7.0, True, "Só dele", "choca: sentado sobre os ovos com as asas abertas por cima"),
    "knocked_out": (knocked_out, 4.0, True, "Descanso", "nocauteado, de lado, o pescoço estendido no chão"),
    "wake": (wake, 3.0, False, "Descanso", "acorda do nocaute: rola, ergue o pescoço tonto, levanta"),
    "beg": (beg, 1.6, True, "Domado", "pede comida: bicadinhas no ar, olha o dono com um olho"),
    "tame": (tame, 2.6, False, "Domado", "abaixa o pescoço, abre as asas uma vez e olha o dono com um olho"),
}
