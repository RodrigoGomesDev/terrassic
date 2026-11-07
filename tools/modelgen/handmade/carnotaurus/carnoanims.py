"""Carnotaurus animations, written for it from its own study (page "Carnotaurus: estudo e modelo", section 6).

Only the plumbing is shared (anim2: easing, leg IK with planted feet, export; theropod.Plan: plant/stand, spreading a
rotation over the neck bones). Every pose below is its own, from what the study says the animal was:
- a runner: long stride, high foot, the body low and level at speed, the head held still while the body moves;
- the back half of the tail was stiff (the caudal ribs lock it): only tail1-tail2 bend, tail3 a little, the rest
  follows straight;
- a short, weak jaw on a strong neck: quick snaps and bites that pull back with the whole body, not crushing holds;
- the horns: shoving and hooking a rival, rubbing on trunks;
- head movements in short, quick jumps that stop dead (a hawk aiming with its head), not slow sweeps.
"""
import math
import os
import sys
_H = os.path.dirname(os.path.abspath(__file__))
_E = os.path.join(_H, "..", "_engine")
sys.path[:0] = [_H, _E, os.path.join(_E, "plans")]
import proto as P
import carno
import theropod
from anim2 import add, Track, smooth, ease_out, ease_in, back_out, solve_leg2, lowest
from theropod import window, W, SIDES

TAILS = ("tail1", "tail2", "tail3", "tail4", "tail5")
STIFF = (1.0, 0.8, 0.35, 0.0, 0.0)      # how much each tail bone bends: the back half is locked


def model():
    m = carno.build(saddle_on=True); P.pack(m, carno.TEX_W); return m.spec()


S = model()
T = theropod.Plan(S, K=1.0, necks=("neck1", "neck2"), tails=TAILS)


def tr(*keys): return Track(keys)


def tail(p, yaw=0.0, pitch=0.0):
    """bend the tail at its root: the stiff back half rides along straight"""
    for b, k in zip(TAILS, STIFF):
        if k: add(p, b, rot=(pitch * k, yaw * k, 0))


def snap_head(t, keys):
    """head aim in quick jumps that stop dead: keys = [(t, (pitch, yaw))]; each jump takes 0.12 s"""
    cur = (0.0, 0.0)
    for tk, v in keys:
        if t < tk: break
        u = ease_out(min(1.0, (t - tk) / 0.12))
        cur = (cur[0] + (v[0] - cur[0]) * u, cur[1] + (v[1] - cur[1]) * u)
    return cur


def arms(p, a=0.0, f=0.0):
    for s, _ in SIDES:
        add(p, f"arm_{s}", rot=(a, 0, 0)); add(p, f"forearm_{s}", rot=(f, 0, 0))


# ------------------------------------------------------------------ gait (its own: level body, still head, stiff tail)
# signs on this rig: body +x = nose up; neck/skull -x = down; jaw -x = open; tail pitch + = down


def gait(t, Tc, stride, duty, lift, bob, lean=0.0, drop=0.0, head=0.0, sway=1.0, stance_clear=-0.05, still=0.85):
    """one stride cycle. still = how much of the body's bob and sway the neck cancels so the head stays put"""
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    bp = 0.8 * math.sin(2 * w - 0.4); by = 1.6 * sway * math.sin(w); br = 1.4 * sway * math.sin(w + 0.35)
    add(p, "body", rot=(lean + bp, by, br), pos=(0, -bob * math.cos(2 * w - 0.9) - 0.6 - drop, 0))
    T.neck(p, (head - lean * still - bp * still, -by * still, -br * still * 0.6))
    add(p, "skull", rot=(-head * 0.3, 0, -br * 0.3))
    tail(p, yaw=-2.2 * sway * math.sin(w - 0.9), pitch=lean * 0.5 + 0.6 * math.sin(2 * w - 1.2))
    for s, o in SIDES:      # the stubby arms hardly swing: a small jiggle a beat late
        add(p, f"arm_{s}", rot=(3 * math.sin(2 * w + o * 2 * math.pi - 2.2), 0, 0))
    for s, o in SIDES:
        u = (ph + o) % 1.0
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0
            meta = 36 * smooth(max(0, (st - 0.5) / 0.5)); toe = 0.0; clear = stance_clear
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e
            ly = lift * math.sin(math.pi * min(1, sw * 1.1)) ** 1.1       # a high, folded foot
            meta = 36 * (1 - smooth(sw / 0.45)) - 26 * math.sin(math.pi * sw)
            toe = -34 * math.sin(math.pi * min(1, sw * 1.1)) + 8 * smooth((sw - 0.7) / 0.3)
            clear = 1.2 * math.sin(math.pi * sw) ** 0.5
        T.plant(p, s, ly, dz - 4, meta, toe, clear)
    return p


WALK = (1.5, 70, 0.6, 11, 1.0)
RUN = (0.6, 128, 0.36, 20, 2.2)


def walk(t):
    return gait(t, *WALK)


def run(t):
    """the sprint: the body drops and levels out, neck straight forward, the tail a rigid counterweight"""
    p = gait(t, *RUN, lean=7, drop=4, head=-6, sway=0.45, stance_clear=0.2, still=0.95)
    tail(p, pitch=2)
    arms(p, -14, 12)
    return p


def stalk(t):
    """low and slow, the head locked on the target (held level while the body rolls under it)"""
    Tw, st, du, li, bo = WALK
    p = gait(t, Tw * 1.6, st * 0.7, 0.72, li * 0.7, bo * 0.4, lean=4, drop=8, head=-10, sway=0.4, still=1.0)
    tail(p, pitch=-2)
    return p


# ------------------------------------------------------------------ standing
def idle(t):
    """breathing; the head aims in short jumps and holds, like a hawk; the arms twitch once"""
    p = {}; br = math.sin(W(t, 2.2))
    add(p, "body", rot=(0.7 * br, 0, 0), pos=(0, 0.3 * br, 0))
    hp, hy = snap_head(t, [(0.0, (0, 0)), (1.1, (3, 14)), (2.4, (3, 22)), (3.3, (-2, -8)), (4.9, (5, -18)),
                           (5.6, (1, -6)), (7.1, (0, 0))])
    T.neck(p, (hp * 0.4 - 0.5 * br, hy * 0.4, 0))
    add(p, "skull", rot=(hp * 0.6, hy * 0.6, -hy * 0.1))
    add(p, "jaw", rot=(-0.6 - 0.6 * max(0, br), 0, 0))
    tail(p, yaw=1.2 * math.sin(W(t, 8.0)), pitch=0.4 * math.sin(W(t, 2.2) - 0.8))
    tw = window(t, 6.2, 6.6, 0.05)
    arms(p, 1.2 * br + 7 * tw * math.sin(2 * math.pi * 14 * t), -2 + 9 * tw * math.sin(2 * math.pi * 14 * t + 1))
    return T.stand(p)


def look_back(t):
    """head first, then the body: the neck turns, holds, and the shoulders follow late"""
    p = {}; br = math.sin(W(t, 2.2))
    add(p, "body", rot=(0.7 * br, 0, 0))
    k = float(tr((0, 0), (0.4, 0), (0.55, 1, ease_out), (2.3, 1), (2.45, 0, ease_out), (3.2, 0))(t))
    b = float(tr((0, 0), (0.9, 0), (1.5, 1), (2.4, 1), (3.0, 0))(t))
    add(p, "body", rot=(0, 10 * b, -2 * b))
    T.neck(p, (4 * k, 40 * k - 8 * b, 0)); add(p, "skull", rot=(2 * k, 24 * k, -6 * k))
    tail(p, yaw=-4 * b)
    return T.stand(p)


def lock_on(t):
    """stops, drops the head and stares with both forward eyes; nothing moves but the breath. Warns the player
    before the sprint"""
    p = {}
    k = float(tr((0, 0), (0.25, 1, ease_out), (1.8, 1), (2.2, 0))(t))
    br = math.sin(W(t, 0.9)) * 0.5
    add(p, "body", rot=(5 * k + br, 0, 0), pos=(0, -3 * k, 0))
    T.neck(p, (-14 * k, 0, 0)); add(p, "skull", rot=(4 * k, 0, 0))
    add(p, "jaw", rot=(-2 * k, 0, 0))
    tail(p, pitch=3 * k)
    arms(p, -6 * k, 0)
    return T.stand(p)


def arm_twitch(t):
    """the tiny arms tremble fast when it is excited (the forearm hardly moves: the elbow was stiff)"""
    p = {}; br = math.sin(W(t, 1.2))
    add(p, "body", rot=(0.6 * br, 0, 0))
    e = window(t, 0.15, 1.05, 0.08)
    for s, o in SIDES:
        add(p, f"arm_{s}", rot=(-10 * e + 9 * e * math.sin(2 * math.pi * 16 * t + o * 5), 0, 3 * e * math.sin(2 * math.pi * 13 * t)))
        add(p, f"forearm_{s}", rot=(3 * e * math.sin(2 * math.pi * 16 * t + 1 + o * 5), 0, 0))
    add(p, "skull", rot=(0, 3 * e * math.sin(2 * math.pi * 3 * t), 0))
    return T.stand(p)


# ------------------------------------------------------------------ fast movement
def skid_turn(t):
    """turning left at speed (the head goes to model -x, the animal's left in game): leans into the curve, the outer
    foot skids sideways, the stiff tail swings out wide"""
    p = {}
    k = float(tr((0, 0), (0.15, 1, ease_out), (0.6, 1), (0.9, 0))(t))
    add(p, "body", rot=(5 * k, 18 * k, 12 * k), pos=(0, -3 * k, 0))
    T.neck(p, (-4 * k, 16 * k, -6 * k)); add(p, "skull", rot=(0, 8 * k, -4 * k))
    tail(p, yaw=-14 * k, pitch=2 * k)
    T.plant(p, "l", 0, -8 * k, 6 * k, 0)
    T.plant(p, "r", 0, 10 * k, -4 * k, 0)
    for b in ("thigh_r", "shin_r"): add(p, b, rot=(0, 0, -5 * k))      # the outer leg braced out
    arms(p, -12 * k, 10 * k)
    return p


def _mirror(p):
    """the same pose on the other side: left and right bones swap, side-to-side moves and turns flip"""
    q = {}
    for b, e in p.items():
        o = b[:-2] + {"_l": "_r", "_r": "_l"}[b[-2:]] if b[-2:] in ("_l", "_r") else b
        q[o] = ([e[0][0], -e[0][1], -e[0][2]], [-e[1][0], e[1][1], e[1][2]], *e[2:])
    return q


def skid_turn_r(t):
    """skid_turn to the other side (that one turns left in game, this one right): the Java picks it by the turn"""
    return _mirror(skid_turn(t))


def brake(t):
    """from the sprint: legs pushed forward, body thrown back, the tail up as a counterweight"""
    p = {}
    k = float(tr((0, 0), (0.12, 1, ease_out), (0.55, 1), (0.9, 0, back_out))(t))
    add(p, "body", rot=(-9 * k, 0, 0), pos=(0, -2 * k, 4 * k))
    T.neck(p, (14 * k, 0, 0)); add(p, "skull", rot=(-6 * k, 0, 0)); add(p, "jaw", rot=(-6 * k, 0, 0))
    tail(p, pitch=6 * k)
    T.plant(p, "l", 0, -16 * k, -10 * k, 0)
    T.plant(p, "r", 0, -6 * k, -6 * k, 0)
    arms(p, -20 * k, 15 * k)
    return p


# ------------------------------------------------------------------ combat
def attack_quick(t):
    """snap: three short, quick bites, the head darting out and back on the strong neck"""
    p = {}
    out = sum(math.exp(-((t - c) / 0.07) ** 2) for c in (0.18, 0.46, 0.74))
    jaw = sum(-26 * math.exp(-((t - c) / 0.06) ** 2) for c in (0.12, 0.40, 0.68))
    add(p, "body", rot=(2 * out, 0, 0), pos=(0, 0, -2.5 * out))
    T.neck(p, (-10 * out, 2 * math.sin(2 * math.pi * 2 * t), 0)); add(p, "skull", rot=(-4 * out, 0, 0))
    add(p, "jaw", rot=(jaw, 0, 0))
    tail(p, pitch=-1.5 * out)
    arms(p, -8 * window(t, 0.05, 0.9, 0.1))
    return T.stand(p)


def attack(t):
    """bite_pull: the jaw is weak, so it bites and rips back with the whole body, the legs doing the work"""
    p = {}
    lunge = float(tr((0, 0), (0.25, -0.3), (0.42, 1, ease_in), (0.55, 1), (0.95, -1, ease_out), (1.3, -0.8), (1.8, 0))(t))
    a = max(0, lunge); b = max(0, -lunge)
    add(p, "body", rot=(5 * a - 6 * b, 0, 0), pos=(0, -1.5 * a - 1.0 * b, -6 * a + 7 * b))
    T.neck(p, (-14 * a + 10 * b, 0, 0)); add(p, "skull", rot=(-6 * a + 8 * b, 0, 4 * b * math.sin(2 * math.pi * 5 * t)))
    jaw = float(tr((0, 0), (0.25, -30, ease_out), (0.42, -34), (0.5, -4, ease_in), (1.3, -4), (1.5, -14), (1.8, 0))(t))
    add(p, "jaw", rot=(jaw, 0, 0))
    tail(p, pitch=-3 * a + 4 * b, yaw=3 * b * math.sin(2 * math.pi * 2.5 * t))
    T.plant(p, "l", 0, -5 * a + 4 * b, 0, 0)
    T.plant(p, "r", 0, 3 * a - 6 * b, 0, 0)
    arms(p, -10 * a, 8 * a)
    return p


def shove(t):
    """horns against the rival: head low, legs spread back, pushing slowly, the shove pulses"""
    p = {}
    k = float(tr((0, 0), (0.4, 1, ease_out), (2.2, 1), (2.7, 0))(t))
    push = 0.5 + 0.5 * math.sin(2 * math.pi * 1.2 * (t - 0.4))
    add(p, "body", rot=(6 * k, 0, 1.2 * k * math.sin(2 * math.pi * 1.2 * t)), pos=(0, -4 * k, -2 * k * push))
    T.neck(p, (-16 * k, 0, 0)); add(p, "skull", rot=(-12 * k, 0, 0))
    add(p, "jaw", rot=(-3 * k, 0, 0))
    tail(p, pitch=4 * k)
    T.plant(p, "l", 0, 6 * k, 0, 0)
    T.plant(p, "r", 0, 12 * k, 0, 0)
    return p


def hook(t):
    """turns the head on its side and flicks the target away with a horn"""
    p = {}
    k = float(tr((0, 0), (0.3, 1, ease_out), (0.42, 1), (0.55, -0.6, ease_in), (0.8, -0.4), (1.2, 0))(t))
    a = max(0, k); b = max(0, -k)
    add(p, "body", rot=(3 * a, 6 * a - 6 * b, 0))
    T.neck(p, (-10 * a + 6 * b, 14 * a - 18 * b, 0)); add(p, "skull", rot=(-6 * a + 10 * b, 6 * a - 10 * b, 26 * a - 30 * b))
    tail(p, yaw=-6 * a + 6 * b)
    return T.stand(p)


def threat(t):
    """head low showing the horns from the front, a snort, a foot scraping the ground twice"""
    p = {}
    k = float(tr((0, 0), (0.35, 1, ease_out), (2.4, 1), (2.8, 0))(t))
    snort = math.exp(-((t - 0.7) / 0.06) ** 2)
    add(p, "body", rot=(6 * k, 0, 0), pos=(0, -3 * k, 0))
    T.neck(p, (-12 * k, 0, 0)); add(p, "skull", rot=(-14 * k + 4 * snort, 0, 0))
    add(p, "jaw", rot=(-3 * k - 4 * snort, 0, 0))
    tail(p, pitch=3 * k, yaw=2 * k * math.sin(W(t, 0.8)))
    T.plant(p, "l")
    sc = sum(window(t, c, c + 0.35, 0.08) for c in (1.0, 1.6))
    back = sum(smooth((t - c) / 0.3) * (1 - smooth((t - c - 0.3) / 0.08)) for c in (1.0, 1.6))
    T.plant(p, "r", 3 * sc, 6 - 14 * back, 0, -6 * sc, clear=-0.05)
    return p


def roar(t):
    """short and deep, the mouth only a little open (the skull is short), the throat swelling"""
    p = {}
    k = float(tr((0, 0), (0.4, -0.3), (0.75, 1, ease_out), (2.2, 1), (2.8, 0))(t))
    a = max(0, k); b = max(0, -k)
    vib = 1.0 * math.sin(2 * math.pi * 10 * t) * window(t, 0.75, 2.2, 0.1)
    add(p, "body", rot=(-3 * a + 2 * b, 0, 0), pos=(0, -1 * a, 0))
    T.neck(p, (10 * a - 6 * b, 0, 0)); add(p, "skull", rot=(6 * a + vib, 0, 0))
    add(p, "jaw", rot=(-24 * a - 2 * b - vib, 0, 0))
    tail(p, pitch=-3 * a)
    arms(p, -6 * a + 3 * vib, 4 * a)
    return T.stand(p)



# ------------------------------------------------------------------ resting (its own: the stiff tail lies flat as a plank)
def ground_fit(S, p):
    """the lowest point of the animal on the ground; the saddle does not count (its stirrups hang below the body when
    it lies on its side, and an unsaddled Carnotaurus would float)"""
    lo = lowest(S, p, skip_mats=("teeth", "teeth_lo", "hide", "fur", "strap", "iron")); add(p, "root", pos=(0, -lo, 0)); return p


LIE = 40.0      # the keel is 38 px up; with the knees folded up beside the belly it rests on the ground


# the folded legs, found by a search over the joint angles (knee forward and up beside the belly, the metatarsus flat
# on the ground, the toes and the keel touching it together); fold() blends to them, so no leg ever flips mid-way
LIE_LEGS = {f"{b}_{s}": (a, 0, 0) for s, _ in SIDES for b, a in (("thigh", 60), ("shin", -120), ("foot", 60))}


def fold(p, k, head_down=0.0):
    """k = 0 standing .. 1 on the belly, the knees folded up beside it and the metatarsi flat. The chest goes down
    first (heavy front, light hips), the stiff tail stays straight and drops as one piece from its root"""
    add(p, "body", rot=(-1 * k, 0, 0), pos=(0, -LIE * k, 0))
    T.neck(p, (-4 * k - 22 * head_down, 0, 0)); add(p, "skull", rot=(3 * k - 6 * head_down, 0, 0))
    tail(p, pitch=5 * k)                 # (tail pitch: + lowers it)
    arms(p, -10 * k, 14 * k)
    for n, r in LIE_LEGS.items(): add(p, n, rot=tuple(x * smooth(k) for x in r))
    return p


def sit(t):
    """lying on its belly but awake: the head up and still, aiming in short jumps; the tail a straight plank"""
    p = {}; br = math.sin(W(t, 3.0))
    fold(p, 1.0); add(p, "body", rot=(0.8 * br, 0, 0))
    hp, hy = snap_head(t, [(0.0, (0, 0)), (1.4, (2, 18)), (3.0, (0, 6)), (4.3, (3, -14)), (5.4, (0, 0))])
    T.neck(p, (8 - 0.6 * br + hp * 0.4, hy * 0.4, 0)); add(p, "skull", rot=(hp * 0.6, hy * 0.6, -hy * 0.1))
    return ground_fit(S, p)


def sleep(t):
    """the chin laid flat on the ground in front, the neck turned a little to one side; slow breathing in the flanks"""
    p = {}; br = math.sin(W(t, 4.5))
    fold(p, 1.0, head_down=1.0)
    add(p, "body", rot=(1.1 * br, 0, 0), pos=(0, 0.4 * br, 0))
    T.neck(p, (-0.6 * br, 12, -4)); add(p, "skull", rot=(0, 6, -8))
    add(p, "jaw", rot=(-1.0 * max(0, br), 0, 0))
    tail(p, yaw=-4)
    return ground_fit(S, p)


def wake_sleep(t):
    """from sleep: the head snaps up first and looks around in two jumps, then it pushes up in one go"""
    p = {}
    hd = float(tr((0, 1), (0.35, 0, ease_out), (2.4, 0))(t))
    up = float(tr((0, 1), (1.1, 1), (1.8, 0, back_out), (2.4, 0))(t))
    fold(p, up, head_down=hd)
    hp, hy = snap_head(t, [(0.0, (0, 0)), (0.5, (2, 16)), (0.85, (2, -12)), (1.2, (0, 0))])
    T.neck(p, ((1 - hd) * 8 * up + hp * 0.4, hy * 0.4 + 12 * hd, -4 * hd)); add(p, "skull", rot=(hp * 0.6, hy * 0.6 + 6 * hd, -8 * hd))
    return ground_fit(S, p)


def _on_side(p, k):
    """lying on its right side: the head and neck rest flat, the stiff tail too"""
    add(p, "root", rot=(0, 0, 82 * k))
    T.neck(p, (-2 * k, 0, -10 * k)); add(p, "skull", rot=(-4 * k, 0, -10 * k))


def knocked_out(t):
    """out cold on its side; slow breathing, the upper leg loose, a twitch of the arm now and then"""
    p = {}; br = math.sin(W(t, 4.0))
    fold(p, 0.7); _on_side(p, 1.0)
    add(p, "body", rot=(0.8 * br, 0, 0)); add(p, "jaw", rot=(-5 - 1.5 * br, 0, 0))
    add(p, "thigh_l", rot=(16, 0, 0)); add(p, "shin_l", rot=(14, 0, 0))
    tw = window(t, 2.6, 2.9, 0.05)
    arms(p, 18 + 6 * tw * math.sin(2 * math.pi * 12 * t), 0)
    return ground_fit(S, p)


def wake(t):
    """from the knockout: rolls onto its belly, shakes the head hard, stands up with a stagger"""
    p = {}
    roll = float(tr((0, 1), (0.3, 1), (0.9, 0, ease_out), (3.0, 0))(t))
    k = float(tr((0, 0.75), (0.9, 1.0), (1.6, 1.0), (2.3, 0, back_out), (3.0, 0))(t))
    fold(p, k, head_down=0.4 * roll); _on_side(p, roll)
    env = math.exp(-((t - 1.25) / 0.18) ** 2)
    add(p, "skull", rot=(0, 7 * env * math.sin(2 * math.pi * 7 * t), 16 * env * math.sin(2 * math.pi * 7 * t)))
    st = window(t, 2.2, 2.9, 0.15)
    add(p, "body", rot=(0, 0, 4 * st * math.sin(2 * math.pi * 1.6 * t)))
    return ground_fit(S, p)


def death(t):
    """a runner's fall: the legs give out under the heavy front, it drops on the chest, rolls on its side; the stiff
    tail falls as one straight piece"""
    p = {}
    g = float(tr((0, 0), (0.35, 0.2), (0.85, 0.85, ease_in), (3.0, 0.85))(t))
    pitch = float(tr((0, 0), (0.6, -6), (0.85, -10, ease_in), (1.2, -4), (3.0, -4))(t))
    rl = float(tr((0, 0), (0.9, 0), (1.35, 1.03, ease_in), (1.5, 0.95), (1.65, 1.0), (3.0, 1.0))(t))
    fold(p, g); add(p, "body", rot=(pitch, 0, 0)); _on_side(p, rl)
    sway = math.sin(2 * math.pi * 1.4 * t) * (1 - smooth((t - 0.6) / 0.3))
    add(p, "body", rot=(0, 3 * sway, 0))
    add(p, "jaw", rot=(-16 * window(t, 0.1, 0.8) - 8 * smooth((t - 1.3) / 0.4), 0, 0))
    tail(p, pitch=3 * smooth((t - 0.8) / 0.4))
    arms(p, 20 * smooth((t - 1.0) / 0.3))
    return ground_fit(S, p)


# ------------------------------------------------------------------ small gestures
def hurt(t):
    """flinch: the body jerks away from the hit, the head snaps up and back, the arms twitch"""
    p = {}
    k = float(tr((0, 0), (0.08, 1, ease_out), (0.6, 0))(t))
    add(p, "body", rot=(5 * k, 0, 3 * k), pos=(0, 0, 2 * k))
    T.neck(p, (10 * k, -6 * k, 0)); add(p, "skull", rot=(6 * k, 0, 6 * k)); add(p, "jaw", rot=(-14 * k, 0, 0))
    tail(p, pitch=-2 * k, yaw=3 * k)
    arms(p, -14 * k, 10 * k)
    return T.stand(p)


def sniff(t):
    """the nose aims in jumps: down at the ground, a quick double sniff, then up into the wind"""
    p = {}
    hp, hy = snap_head(t, [(0.0, (0, 0)), (0.3, (-18, 6)), (1.25, (-14, -8)), (1.9, (10, 4)), (2.6, (0, 0))])
    add(p, "body", rot=(-4 * smooth(t / 0.4) * (1 - smooth((t - 1.8) / 0.4)), 0, 0))
    T.neck(p, (hp * 0.6, hy * 0.5, 0))
    sn = sum(math.exp(-((t - c) / 0.05) ** 2) for c in (0.6, 0.75, 1.5, 1.62, 2.15, 2.3))
    add(p, "skull", rot=(hp * 0.4 + 2.5 * sn, hy * 0.5, -hy * 0.1)); add(p, "jaw", rot=(-0.5 - 1.5 * sn, 0, 0))
    tail(p, yaw=1.5 * math.sin(W(t, 3.0)))
    return T.stand(p)


def shake(t):
    """the shake runs from the head down the neck and the chest; it stops at the hips, the stiff tail only swings
    from its root as one piece"""
    p = {}; e = window(t, 0.2, 1.6, 0.15); f = 2 * math.pi * 5.5 * t
    add(p, "body", rot=(0, 2 * e * math.sin(f - 1.0), 6 * e * math.sin(f - 0.8)))
    T.neck(p, (0, 6 * e * math.sin(f), 14 * e * math.sin(f + 0.3))); add(p, "skull", rot=(0, 5 * e * math.sin(f + 0.6), 16 * e * math.sin(f + 0.8)))
    add(p, "jaw", rot=(-3 * e, 0, 0))
    tail(p, yaw=-4 * e * math.sin(f - 1.6))
    arms(p, -6 * e, 6 * e * math.sin(f))
    return T.stand(p)


def yawn(t):
    """the short jaw opens as wide as it can, the head tips back, the arms stretch out stiff"""
    p = {}
    k = float(tr((0, 0), (0.7, 1, ease_out), (1.8, 1), (2.4, 0, ease_in), (3.0, 0))(t))
    add(p, "body", rot=(3 * k, 0, 0))
    T.neck(p, (10 * k, 0, 0)); add(p, "skull", rot=(10 * k, 0, 4 * k)); add(p, "jaw", rot=(-26 * k, 0, 0))
    arms(p, -16 * k, 12 * k)
    tail(p, pitch=-1 * k)
    return T.stand(p)


def stretch(t):
    """arches the back with the chest low, then each leg pushes back in turn; the tail lifts as one stiff piece"""
    p = {}
    a = float(tr((0, 0), (0.7, 1, ease_out), (1.6, 1), (2.0, 0))(t))
    b = window(t, 1.5, 2.2, 0.15); c = window(t, 2.5, 3.2, 0.15)
    add(p, "body", rot=(-8 * a, 0, 0), pos=(0, -5 * a, 0))
    T.neck(p, (-6 * a + 6 * (b + c), 0, 0)); add(p, "skull", rot=(4 * a, 0, 0)); add(p, "jaw", rot=(-3 * a, 0, 0))
    tail(p, pitch=2 * a)                 # the body tips the stiff tail up; this only softens it
    arms(p, -14 * a, 10 * a)
    T.plant(p, "l", 3 * b, -8 * b, -20 * b, 10 * b)
    T.plant(p, "r", 3 * c, -8 * c, -20 * c, 10 * c)
    return p


def horn_rub(t):
    """rubs one horn on a trunk: head turned on its side, short scrapes up and down, the body leaning into it"""
    p = {}
    k = float(tr((0, 0), (0.5, 1, ease_out), (3.0, 1), (3.5, 0))(t))
    rub = math.sin(2 * math.pi * 1.6 * (t - 0.5)) * window(t, 0.6, 3.0, 0.15)
    add(p, "body", rot=(2 * k, 6 * k, -3 * k), pos=(0, -1.5 * k - 1.2 * rub, 0))
    T.neck(p, (-4 * k + 5 * rub, 18 * k, 0)); add(p, "skull", rot=(2 * rub, 8 * k, 28 * k))
    tail(p, yaw=-5 * k)
    return T.stand(p)


# ------------------------------------------------------------------ eating and drinking
def eat(t):
    """the jaw is weak: it pins the meat with one foot and tears a piece off by pulling back with the whole body,
    then tosses its head to swallow"""
    p = {}
    down = float(tr((0, 0), (0.4, 1, ease_out), (2.4, 1), (2.6, 0.2, ease_out), (3.4, 0))(t))
    pulls = sum(window(t, c, c + 0.35, 0.08) for c in (0.8, 1.6))
    bite = sum(math.exp(-((t - c) / 0.08) ** 2) for c in (0.6, 1.4))
    toss = math.exp(-((t - 2.8) / 0.12) ** 2)
    add(p, "body", rot=(-15 * down + 5 * pulls, 0, 2 * pulls), pos=(0, -7 * down, 3 * pulls))
    T.neck(p, (-32 * down + 6 * pulls + 16 * toss, 3 * pulls, 0)); add(p, "skull", rot=(-10 * down + 6 * pulls + 10 * toss, 0, 5 * pulls))
    add(p, "jaw", rot=(-16 * bite - 4 * down * (1 - pulls) - 14 * toss, 0, 0))
    tail(p, pitch=8 * down - 3 * pulls)
    T.plant(p, "l", 0, -6 * down, 0, 0)
    T.plant(p, "r", 0, 0, 0, 0)
    arms(p, -6 * down)
    return p


def drink(t):
    """the neck is short: to reach the water it spreads and bends the legs, then laps quickly and lifts the head to
    swallow, twice"""
    p = {}
    down = float(tr((0, 0), (0.6, 1, ease_out), (3.4, 1), (4.0, 0))(t))
    up = sum(window(t, c, c + 0.45, 0.12) for c in (1.6, 2.8))
    lap = sum(math.exp(-((t - c) / 0.05) ** 2) for c in (0.9, 1.1, 1.3, 2.1, 2.3, 2.5))
    add(p, "body", rot=(-17 * down + 8 * up, 0, 0), pos=(0, -9 * down + 3 * up, 0))
    T.neck(p, (-34 * down + 22 * up, 0, 0)); add(p, "skull", rot=(-10 * down + 12 * up, 0, 0))
    add(p, "jaw", rot=(-5 * lap - 2 * down, 0, 0))
    tail(p, pitch=10 * down - 5 * up)
    for s, sx in (("l", 1), ("r", -1)): add(p, f"thigh_{s}", rot=(0, 0, 6 * sx * down))
    T.plant(p, "l", 0, -3 * down, 0, 0); T.plant(p, "r", 0, 3 * down, 0, 0)
    return p


# ------------------------------------------------------------------ swimming
def swim(t):
    """swims like the theropod trackways show: the long legs paddle in turn, the body low in the water with the head
    held up and level; only the tail root sculls"""
    Tc = 1.4; w = W(t, Tc); p = {}
    add(p, "body", rot=(3 + 1.5 * math.sin(2 * w), 2 * math.sin(w), 3 * math.sin(w + 0.4)), pos=(0, 1.2 * math.sin(2 * w), 0))
    T.neck(p, (12 - 1.5 * math.sin(2 * w + 0.5), -2 * math.sin(w), 0)); add(p, "skull", rot=(-4, 0, 0))
    tail(p, yaw=7 * math.sin(w - 0.8), pitch=2)
    for s, o in SIDES:
        f = w + o * 2 * math.pi
        add(p, f"thigh_{s}", rot=(-14 + 32 * math.sin(f), 0, 0)); add(p, f"shin_{s}", rot=(-20 - 26 * math.cos(f), 0, 0))
        add(p, f"foot_{s}", rot=(28 + 22 * math.cos(f + 0.6), 0, 0)); add(p, f"toes_{s}", rot=(-26 * math.sin(f + 1.0), 0, 0))
    arms(p, -18, 14)
    return p


# ------------------------------------------------------------------ with its owner and its herd
def beg(t):
    """asks the owner for food: head low and tilted, little clicks of the jaw, the arms trembling"""
    p = {}; br = math.sin(W(t, 2.0))
    add(p, "body", rot=(-4 + 0.6 * br, 0, 0), pos=(0, -1.5, 0))
    tilt = 10 * math.sin(W(t, 2.0))
    T.neck(p, (-8, 4, 0)); add(p, "skull", rot=(0, 4, tilt))
    clk = sum(math.exp(-((t - c) / 0.04) ** 2) for c in (0.3, 0.45, 1.3, 1.45))
    add(p, "jaw", rot=(-6 * clk, 0, 0))
    arms(p, -8 + 5 * math.sin(2 * math.pi * 12 * t), 4)
    tail(p, yaw=2 * math.sin(W(t, 2.0)), pitch=2)
    return T.stand(p)


def tame(t):
    """the moment it accepts the owner: it lowers the horns to the ground in front of them, holds, and lifts the head
    calmly, without the hawk jumps"""
    p = {}
    k = float(tr((0, 0), (0.6, 1, ease_out), (1.5, 1), (2.4, 0, smooth))(t))
    add(p, "body", rot=(-10 * k, 0, 0), pos=(0, -4 * k, 0))
    T.neck(p, (-24 * k, 0, 0)); add(p, "skull", rot=(-10 * k, 0, 0)); add(p, "jaw", rot=(-2 * k, 0, 0))
    tail(p, pitch=6 * k)
    arms(p, -4 * k)
    return T.stand(p)


def call(t):
    """calling others: three low grunts, the mouth barely open, the throat and chest pumping with each one"""
    p = {}
    k = float(tr((0, 0), (0.3, 1, ease_out), (2.2, 1), (2.6, 0))(t))
    g = sum(window(t, c, c + 0.28, 0.06) for c in (0.5, 1.05, 1.6))
    add(p, "body", rot=(2 * k + 2 * g, 0, 0), pos=(0, 0.8 * g, 0))
    T.neck(p, (6 * k + 3 * g, 0, 0)); add(p, "skull", rot=(4 * k + 2 * g, 0, 0))
    add(p, "jaw", rot=(-3 * k - 7 * g, 0, 0))
    tail(p, pitch=1.5 * g)
    return T.stand(p)

ANIMS = {
    "idle": (idle, 8.0, True, "Parado", "base, sempre que está parado: mira a cabeça aos saltos"),
    "look_back": (look_back, 3.2, False, "Parado", "vira a cabeça primeiro, o corpo depois"),
    "arm_twitch": (arm_twitch, 1.2, False, "Parado", "agitado: os bracinhos tremem"),
    "walk": (walk, WALK[0], True, "Movimento", "andando: passada longa, pé alto, cauda rígida atrás"),
    "run": (run, RUN[0], True, "Movimento", "arrancada: corpo baixo e reto, cabeça parada"),
    "stalk": (stalk, WALK[0] * 1.6, True, "Movimento", "chegando perto da presa, cabeça travada no alvo"),
    "skid_turn": (skid_turn, 0.9, False, "Movimento", "curva em velocidade, derrapando"),
    "skid_turn_r": (skid_turn_r, 0.9, False, "Movimento", "a mesma derrapagem, na curva para a direita"),
    "brake": (brake, 0.9, False, "Movimento", "freada no fim da arrancada"),
    "lock_on": (lock_on, 2.2, False, "Combate", "trava no alvo antes da arrancada (aviso para o jogador)"),
    "attack_quick": (attack_quick, 0.95, False, "Combate", "três mordidas rápidas"),
    "attack": (attack, 1.8, False, "Combate", "morde e puxa com o corpo todo"),
    "shove": (shove, 2.7, False, "Combate", "empurra um rival com os chifres"),
    "hook": (hook, 1.2, False, "Combate", "gira a cabeça e joga o alvo de lado com o chifre"),
    "threat": (threat, 2.8, False, "Voz", "aviso: chifres de frente, bufa e raspa o pé"),
    "roar": (roar, 2.8, False, "Voz", "rugido curto e grave"),
    "call": (call, 2.6, False, "Voz", "três roncos graves chamando outros"),
    "hurt": (hurt, 0.6, False, "Combate", "ao levar dano"),
    "death": (death, 3.0, False, "Combate", "cai de peito e rola de lado, a cauda dura cai reta"),
    "sniff": (sniff, 2.8, False, "Parado", "fareja o chão aos saltos, depois o vento"),
    "shake": (shake, 1.8, False, "Parado", "sacode da cabeça ao quadril; a cauda dura só balança"),
    "yawn": (yawn, 3.0, False, "Parado", "bocejo: a mandíbula curta abre tudo que pode"),
    "stretch": (stretch, 3.5, False, "Parado", "arqueia as costas e empurra uma perna de cada vez"),
    "horn_rub": (horn_rub, 3.5, False, "Parado", "esfrega um chifre num tronco"),
    "eat": (eat, 3.4, False, "Comer", "prende a carne com o pé e arranca puxando o corpo"),
    "drink": (drink, 4.0, False, "Comer", "abre e dobra as pernas para alcançar a água"),
    "swim": (swim, 1.4, True, "Movimento", "nadando: pernas remam, cabeça erguida"),
    "sit": (sit, 6.0, True, "Descanso", "deitado acordado, cabeça alta"),
    "sleep": (sleep, 9.0, True, "Descanso", "dormindo com o queixo no chão"),
    "wake_sleep": (wake_sleep, 2.4, False, "Descanso", "acorda: a cabeça primeiro, depois levanta de uma vez"),
    "knocked_out": (knocked_out, 4.0, True, "Descanso", "nocauteado, deitado de lado"),
    "wake": (wake, 3.0, False, "Descanso", "acorda do nocaute: rola, sacode a cabeça, cambaleia"),
    "beg": (beg, 2.0, True, "Domado", "pede comida ao dono"),
    "tame": (tame, 2.4, False, "Domado", "baixa os chifres diante do dono ao ser domado"),
}

# 06/11: the fluid set and the fighting moves (carnoflow.py, from docs/estudos/08 and 10): the names above keep their
# length and hit times and get their fluid version; the new ones join the list
import carnoflow as FLOW  # noqa: E402
for _name, _fn in FLOW.REBIND.items():
    ANIMS[_name] = (_fn,) + ANIMS[_name][1:]
ANIMS.update(FLOW.NEW)

# 06/11: the epic duel's committed moves (carnofight.py, from docs/estudos/10): lunge, parry, stagger (fixed lengths)
import carnofight as FIGHT  # noqa: E402
ANIMS.update(FIGHT.NEW)
