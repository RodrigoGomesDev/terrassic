"""Thescelosaurus animations, from its own study (docs/estudos/15_HERBIVOROS_1_11.md, section Tescelossauro).

v4 (16/11/2026, the "tipo ave" silhouette): a ground bird's body (the short trunk pitched up 22 degrees, the neck in an
S, thick thighs over long shins, the stiff rod of a tail). Only the plumbing is shared (anim2: easing, leg IK with
planted feet, export; theropod.Plan: plant, lie). The poses are its own, from what the study says the animal was:
- a WARY animal of the undergrowth, prey of the Dakotaraptor and the young T. rex: it FREEZES dead in mid-step when it
  notices danger (freeze: one foot lifted on its toes, the head up and still, only the nostrils move), then BOLTS
  (bolt: a sprint in zigzag, the body low, the stiff tail RAISED showing its pale flag) and hides lying flat among the
  ferns (hide), lifting the head now and then to look (peek); tail_flag is the flag flicked up as a warning;
- a keen NOSE (olfactory bulbs ~3% of the brain, Button & Zanno 2023): it sniffs the ground walking slowly
  (sniff_ground) and the air with the head high (sniff_air), and digs roots and tubers with the hands and the snout
  (dig);
- the BURROW (a HYPOTHESIS of Button & Zanno 2023, with Oryctodromeus as the model): it digs at a bank with the
  forefeet and the snout and kicks the earth back (burrow_dig), and sleeps in it curled tight, the head along the
  flank and the tail wrapped round (burrow_sleep);
- cornered, it bites with the front teeth (attack) and kicks with the strong leg forward (kick) or back (kick_back).
No duel and no saddle (it is not rideable).

Signs on this rig: body +x = nose up; neck/skull -x = down; jaw -x = open; tail +x = the tip down; yaw + = to its
left; thigh +x = the foot swings forward.
"""
import math
import os
import sys
_H = os.path.dirname(os.path.abspath(__file__))
_E = os.path.join(_H, "..", "_engine")
sys.path[:0] = [_H, _E, os.path.join(_E, "plans")]
import numpy as np  # noqa: E402
import geo  # noqa: E402
import proto as P  # noqa: E402
import thes  # noqa: E402
import theropod  # noqa: E402
from anim2 import add, world, chain_angle, solve_leg2, Track, smooth, ease_out, ease_in, back_out, lowest  # noqa: E402

W = lambda t, T: 2 * math.pi * t / T
SIDES = (("l", 0.0), ("r", 0.5))
NECKS = thes.NECKS
TAILS = thes.TAILS


def tr(*keys): return Track(keys)


def f(track, t): return float(track(t))


def window(t, a, b, fade=0.25):
    return smooth((t - a) / fade) * (1 - smooth((t - b) / fade))


def model():
    m = thes.build(); P.pack(m, thes.TEX_W); return m.spec()


S = model()
T = theropod.Plan(S, K=1.0, necks=NECKS, tails=TAILS, lie_drop=10.0, lie_ankle_y=1.6)
BALL = T.BALL
ZC = 0.5 * (BALL["l"][2] + BALL["r"][2])          # the feet stand side by side here when it stands still
HEADB = {"head", "skull", "jaw", "cheek_l", "cheek_r", "male_display", "female_display"}
LEGB = {f"{b}_{s}" for b in ("thigh", "shin", "foot", "toes") for s in ("l", "r")}


def ground_fit(p):
    lo = lowest(S, p); add(p, "root", pos=(0, -lo, 0)); return p


def low_of(p, bones):
    return min(q[:, 1].min() for c, q in geo.cube_points(S, p) if c["bone"] in bones and c.get("mat") != "teeth")


# ------------------------------------------------------------------ pieces
def neck(p, pitch=0.0, yaw=0.0, roll=0.0, w=(0.45, 0.3, 0.25)):
    """a neck rotation spread over the three pieces of the S, most at the base"""
    for b, k in zip(NECKS, w):
        add(p, b, rot=(pitch * k, yaw * k, roll * k))


def skull(p, pitch=0.0, yaw=0.0, roll=0.0):
    add(p, "skull", rot=(pitch, yaw, roll))


def jaw(p, a): add(p, "jaw", rot=(a, 0, 0))


def cheeks(p, k):
    add(p, "cheek_l", rot=(0, 0, -6 * k)); add(p, "cheek_r", rot=(0, 0, 6 * k))


STIFF = (1.0, 0.35, 0.22, 0.15, 0.1)      # the ossified tendons: almost all of a bend is at the root


def tail(p, pitch=0.0, yaw=0.0):
    """the stiff rod: it swings from the root as one piece, a little give along it"""
    for b, k in zip(TAILS, STIFF):
        add(p, b, rot=(pitch * k, yaw * k, 0))


def tail_wave(p, t, Tc, yaw=0.0, pitch=0.0, ph=0.0):
    for i, (b, k) in enumerate(zip(TAILS, STIFF)):
        a = W(t, Tc) + ph - 0.18 * i
        add(p, b, rot=(pitch * k * math.sin(a - 0.4), yaw * k * math.sin(a), 0))


def arms(p, a=0.0, fa=0.0, out=0.0, h=0.0):
    for s, sx in (("l", 1), ("r", -1)):
        add(p, f"arm_{s}", rot=(a, 0, out * sx)); add(p, f"forearm_{s}", rot=(fa, 0, 0))
        if h:
            add(p, f"hand_{s}", rot=(h, 0, 0))


def nostrils(p, t, k=1.0, rate=5.0):
    """the sniff: quick small jerks of the snout (the skull) and the jaw a hair open"""
    s = max(0.0, math.sin(2 * math.pi * rate * t)) ** 3
    skull(p, 2.5 * k * s, 0, 0); jaw(p, -1.2 * k * s)
    return s


def plant(p, s, dy=0.0, z=None, meta=0.0, toe=0.0, clear=-0.05):
    """a foot on the ground at world z (None: under the hip, side by side with the other)"""
    zz = ZC if z is None else z
    T.plant(p, s, dy, zz - BALL[s][2], meta, toe, clear)


def stand(p, dz=(0.0, 0.0), clear=0.6):
    """both feet side by side on the ground (offset fore/aft by dz), the head kept off the ground"""
    for i, (s, _o) in enumerate(SIDES):
        plant(p, s, 0.0, ZC + dz[i])
    if clear is not None:
        for _ in range(30):
            if low_of(p, HEADB) >= clear:
                break
            add(p, "neck1", rot=(1.5, 0, 0))
    return p


def breathe(p, t, T_=2.4, amp=1.0):
    br = math.sin(W(t, T_))
    add(p, "body", rot=(0.7 * amp * br, 0, 0), pos=(0, 0.25 * amp * br, 0))
    neck(p, -0.5 * amp * br); skull(p, -0.3 * amp * br)
    arms(p, 1.5 * amp * br)
    return br


def snap(t, keys, dur=0.09):
    """head aim in quick jerks that stop dead (a ground bird's look): keys = [(t, (pitch, yaw, roll))]"""
    cur = (0.0, 0.0, 0.0)
    for tk, v in keys:
        if t < tk:
            break
        u = ease_out(min(1.0, (t - tk) / dur))
        cur = tuple(cur[i] + (v[i] - cur[i]) * u for i in range(3))
    return cur


# the head down to the ground: the trunk tips nose-down over the legs, the S of the neck opens from the base and the
# skull turns the snout to the ground (searched at import: the predentary 1.5 px off the ground with the feet planted)
REACH = {"body": [-30.0, 0, 0], "neck1": [-40.0, 0, 0], "neck2": [0.0, 0, 0], "neck3": [38.0, 0, 0], "skull": [14.0, 0, 0]}


def reach(p, k):
    for b, r in REACH.items():
        add(p, b, rot=tuple(x * k for x in r))


def _search_reach():
    best = None
    for n1 in np.arange(-10.0, -95.0, -2.5):
        p = {}
        REACH["neck1"][0] = n1
        reach(p, 1.0); stand(p, clear=None)
        lo = low_of(p, HEADB)
        if best is None or abs(lo - 1.5) < abs(best[1] - 1.5):
            best = (n1, lo)
        if lo < 1.5:
            break
    REACH["neck1"][0] = best[0]


_search_reach()


# ------------------------------------------------------------------ gaits
WALK = (1.0, 18.0, 0.6, 4.0, 0.7)        # cycle s, stride px, duty, foot lift px, body bob px
RUN = (0.6, 32.0, 0.38, 8.0, 1.8)
BOLT = (0.5, 30.0, 0.36, 8.0, 2.0)


def gait(t, Tc, stride, duty, lift, bob, lean=0.0, drop=0.0, head=0.0, sway=1.0, nod=4.0, tail_up=0.0, arm=0.0,
         stance_clear=-0.05, zs=0.0):
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    bp = 0.8 * math.sin(2 * w - 0.4); by = 1.6 * sway * math.sin(w); br = 2.0 * sway * math.sin(w + 0.35)
    add(p, "body", rot=(lean + bp, by, br), pos=(0, -bob * math.cos(2 * w - 0.9) - 0.4 - drop, 0))
    # the bird's head bob: thrust forward as a foot lands, held while the body catches up
    nd = nod * math.sin(2 * w - 1.2)
    neck(p, head - lean * 0.9 - bp + nd, -by * 0.6, -br * 0.8)
    skull(p, -head * 0.2 - nd * 0.8 + lean * 0.1, 0, -br * 0.3)
    tail(p, pitch=-lean * 0.8 - tail_up + 1.0 * math.sin(2 * w - 1.5), yaw=-2.0 * sway * math.sin(w - 0.8))
    arms(p, arm + 2 * math.sin(2 * w - 2.0), 0)
    for s, o in SIDES:
        u = (ph + o) % 1.0
        if u < duty:
            st = u / duty; dz = -stride / 2 + stride * st; ly = 0.0
            meta = 26 * smooth(max(0, (st - 0.6) / 0.4)); toe = 0.0; clear = stance_clear
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride / 2 - stride * e
            ly = lift * math.sin(math.pi * min(1, sw * 1.1)) ** 1.1
            meta = 26 * (1 - smooth(sw / 0.4)) - 24 * math.sin(math.pi * sw)
            toe = -40 * math.sin(math.pi * min(1, sw * 1.15))
            clear = 0.8 * math.sin(math.pi * sw) ** 0.5
        plant(p, s, ly, ZC + zs - dz, meta, toe, clear)
    return p


def walk(t):
    p = gait(t, *WALK)
    return p


def walk_tired(t):
    p = gait(t, 1.3, 15.0, 0.66, 3.0, 0.9, lean=-4, head=-14, nod=2.5, tail_up=-3)
    jaw(p, -6 - 2 * math.sin(W(t, 0.65)))
    return p


def run(t):
    """the sprint: the trunk levels, the neck reaches forward, the tail a level counterweight, the arms in"""
    p = gait(t, *RUN, lean=-8, drop=1.0, head=-40, sway=0.6, nod=2.0, tail_up=-2, arm=-20, stance_clear=0.2, zs=4.0)
    return p


def bolt(t):
    """the escape: a sprint in zigzag (the body slews and leans to one side, then the other, every two strides), the
    body low, the stiff tail RAISED showing the pale flag underneath"""
    Tc = BOLT[0]
    p = gait(t, *BOLT, lean=-10, drop=1.0, head=-44, sway=0.5, nod=1.5, tail_up=16, arm=-24, stance_clear=0.2, zs=4.0)
    zig = math.sin(W(t, 4 * Tc))
    add(p, "body", rot=(0, 10 * zig, -5 * zig))
    neck(p, 0, -8 * zig); skull(p, 0, -4 * zig)
    tail(p, yaw=-6 * zig)
    lo = low_of(p, LEGB)
    if lo < 0.0:
        add(p, "root", pos=(0, -lo, 0))     # the lean of the zigzag tips a foot into the ground: lift it out
    return p


def swim(t):
    """it swims: the legs paddle under it in turn, the neck stretched up, the tail sweeps from the root"""
    w = W(t, 1.2); p = {}
    add(p, "body", rot=(-14 + 2 * math.sin(2 * w), 3 * math.sin(w), 3 * math.sin(w + 0.4)), pos=(0, 1.2 * math.sin(2 * w), 0))
    neck(p, 18, 0); skull(p, -6, 0, 0)
    tail_wave(p, t, 1.2, yaw=10)
    for s, o in SIDES:
        f_ = w + o * 2 * math.pi
        add(p, f"thigh_{s}", rot=(-6 + 26 * math.sin(f_), 0, 0)); add(p, f"shin_{s}", rot=(-16 - 18 * math.cos(f_), 0, 0))
        add(p, f"foot_{s}", rot=(20 + 18 * math.cos(f_ + 0.6), 0, 0)); add(p, f"toes_{s}", rot=(-22 * math.sin(f_ + 1.0), 0, 0))
    arms(p, -20, 10)
    return p


TURN_T = 1.0


def turn(t, side):
    """steps round on the spot: small quick steps, the head leading into the turn"""
    sg = 1 if side == "left" else -1
    ph = (t / TURN_T) % 1.0; w = 2 * math.pi * ph; p = {}
    add(p, "body", rot=(0.5 * math.sin(2 * w), 6 * sg, 2 * math.sin(w)), pos=(0, -0.4 - 0.5 * math.cos(2 * w), 0))
    neck(p, 0, 16 * sg); skull(p, 0, 10 * sg)
    tail(p, yaw=-8 * sg)
    for s, o in SIDES:
        u = (ph + o) % 1.0
        ly = 3.0 * max(0.0, math.sin(2 * math.pi * u)) ** 1.2
        plant(p, s, ly, ZC + 2.0 * math.cos(2 * math.pi * u), 10 * max(0, math.sin(2 * math.pi * u)), 0, 0.3 if ly > 0.1 else -0.05)
    return p


def turn_left(t): return turn(t, "left")
def turn_right(t): return turn(t, "right")


# ------------------------------------------------------------------ standing
IDLE_T = 8.0


def idle(t):
    """on its two legs, breathing; the head looks about in bird jerks, a sniff now and then, the tail still"""
    p = {}
    breathe(p, t)
    hp, hy, hr = snap(t, [(0.0, (0, 0, 0)), (1.3, (3, 22, -8)), (2.6, (0, 4, 0)), (4.0, (6, -24, 8)), (5.4, (-4, -6, 0)),
                          (6.8, (0, 0, 0))])
    neck(p, hp * 0.5, hy * 0.6); skull(p, hp * 0.5, hy * 0.4, hr)
    nostrils(p, t, window(t, 4.4, 5.3, 0.15))
    tail(p, pitch=0.6 * math.sin(W(t, 4.0)), yaw=1.2 * math.sin(W(t, 8.0)))
    return stand(p, (1.0, -1.0))


def idle_tired(t):
    p = {}
    br = breathe(p, t, 0.9, 2.2)
    add(p, "body", rot=(-5, 0, 0), pos=(0, -1.2, 0))
    neck(p, -12); skull(p, -4); jaw(p, -7 - 3 * max(0, br))
    tail(p, pitch=3)
    return stand(p, (1.5, -1.5))


def freeze(t):
    """stopped dead in mid-step: one foot lifted onto its toes behind, the trunk and the tail held still, the head up
    and fixed on the danger; only the nostrils move and the breath is held short"""
    p = {}
    add(p, "body", rot=(3 + 0.25 * math.sin(W(t, 1.0)), 0, 0), pos=(0, 0.3, 0))
    neck(p, 10); skull(p, -4, 0, 0)
    s = max(0.0, math.sin(2 * math.pi * 3.2 * t)) ** 4 * window(t, 0.0, 2.0, 0.01)
    skull(p, 1.2 * s); jaw(p, -0.6 * s)
    tail(p, pitch=-2)
    arms(p, -6, 8)
    plant(p, "l", 0.0, ZC - 4.0)
    plant(p, "r", 1.2, ZC + 5.5, 34, -30, 0.3)
    return p


def sniff_ground(t):
    """nose to the ground: the head down and walking it along in small steps, short quick sniffs"""
    p = {}
    k = f(tr((0, 0), (0.5, 1, ease_out), (2.9, 1), (3.4, 0)), t)
    reach(p, 0.85 * k)
    sweep = math.sin(W(t, 1.6))
    neck(p, 0, 10 * sweep * k); skull(p, 0, 8 * sweep * k)
    nostrils(p, t, 1.4 * k, 6.0)
    tail(p, pitch=6 * k)
    return stand(p, (2.0 * k, -2.0 * k), clear=0.4)


def sniff_air(t):
    """the nose up into the wind: the neck stretched tall, the snout raised, quick sniffs, a turn to test the air"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (2.4, 1), (3.0, 0)), t)
    add(p, "body", rot=(6 * k, 0, 0))
    neck(p, 14 * k, 0); skull(p, 22 * k, 0, 0)
    turn_ = f(tr((0, 0), (1.2, 0), (1.5, 18), (2.2, 18), (2.5, 0)), t)
    neck(p, 0, turn_ * 0.6); skull(p, 0, turn_ * 0.4)
    nostrils(p, t, 1.6 * k, 6.5)
    return stand(p)


def eat(t):
    """takes a mouthful from the hand: the head comes down, a clip with the front teeth, the chew with the cheeks"""
    p = {}
    k = f(tr((0, 0), (0.5, 1, ease_out), (1.2, 1), (1.6, 0.35), (2.6, 0.35), (3.0, 0)), t)
    neck(p, -30 * k); skull(p, -18 * k)
    clip = math.exp(-((t - 1.0) / 0.08) ** 2)
    jaw(p, -10 * clip)
    c = window(t, 1.5, 2.7, 0.1) * max(0.0, math.sin(W(t - 1.5, 0.4)))
    cheeks(p, c); jaw(p, -3 * c)
    breathe(p, t)
    return stand(p)


def graze(t):
    """crops low ferns: the head down, short side-to-side clips with the front teeth, then up to chew looking round"""
    p = {}
    k = f(tr((0, 0), (0.5, 1, ease_out), (2.2, 1), (2.7, 0.2), (3.4, 0)), t)
    reach(p, k)
    clips = window(t, 0.6, 2.2, 0.1)
    neck(p, 0, 8 * math.sin(W(t, 0.7)) * clips)
    jaw(p, -6 * clips * max(0.0, math.sin(W(t, 0.35))))
    c = window(t, 2.3, 3.4, 0.1) * max(0.0, math.sin(W(t, 0.4)))
    cheeks(p, c)
    tail(p, pitch=6 * k)
    return stand(p, (1.5 * k, -1.5 * k), clear=0.4)


def drink(t):
    p = {}
    k = f(tr((0, 0), (0.6, 1, ease_out), (3.2, 1), (3.8, 0)), t)
    reach(p, 1.02 * k)
    lap = window(t, 0.8, 3.0, 0.2)
    jaw(p, -4 * lap * (0.5 + 0.5 * math.sin(2 * math.pi * 2.4 * t)))
    skull(p, 2.5 * lap * math.sin(2 * math.pi * 2.4 * t - 0.6))
    tail(p, pitch=6 * k)
    return stand(p, (2.0 * k, -2.0 * k), clear=-0.3)


def dig(t):
    """digs roots and tubers: the head low, the hands scratch the ground in turn, then the snout pushes in and tugs"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (2.8, 1), (3.2, 0)), t)
    reach(p, 0.9 * k)
    sc = window(t, 0.5, 1.8, 0.15)
    for s, o in (("l", 0.0), ("r", math.pi)):
        a = math.sin(2 * math.pi * 3.0 * t + o)
        add(p, f"arm_{s}", rot=(-30 * k + 26 * sc * a, 0, 0)); add(p, f"forearm_{s}", rot=(-20 * k * sc, 0, 0))
    tug = window(t, 1.9, 2.8, 0.1) * math.sin(2 * math.pi * 4.0 * t)
    neck(p, -4 * window(t, 1.9, 2.8, 0.1) + 3 * tug); skull(p, -6 * tug)
    tail(p, pitch=6 * k)
    return stand(p, (2.0 * k, -2.0 * k), clear=-0.2)


def burrow_dig(t):
    """at the bank: crouched with the head low, the forefeet rake in turn, the snout pushes into the earth, and one hind
    foot kicks the loose earth back"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (3.6, 1), (4.0, 0)), t)
    add(p, "body", rot=(-14 * k, 0, 0), pos=(0, -3.0 * k, 0))
    neck(p, -24 * k); skull(p, -8 * k)
    rk = window(t, 0.4, 2.4, 0.15)
    for s, o in (("l", 0.0), ("r", math.pi)):
        a = math.sin(2 * math.pi * 3.4 * t + o)
        add(p, f"arm_{s}", rot=(-40 * k + 34 * rk * a, 0, 0)); add(p, f"forearm_{s}", rot=(-30 * k * rk * max(0, a), 0, 0))
    push = window(t, 1.2, 2.6, 0.2) * max(0.0, math.sin(2 * math.pi * 1.6 * t))
    neck(p, -6 * push); skull(p, -6 * push)
    plant(p, "l", 0.0, ZC - 2.0)
    kick = window(t, 2.5, 3.6, 0.1)
    kk = max(0.0, math.sin(2 * math.pi * 2.6 * (t - 2.5))) * kick
    plant(p, "r", 3.0 * kk, ZC + 3.0 + 9.0 * kk, 20 * kk, -20 * kk, 0.3 if kk > 0.05 else -0.05)
    tail(p, pitch=4 * k, yaw=4 * kk)
    return p


# ------------------------------------------------------------------ hiding and resting
def lie(p, k, neck_down=0.0):
    """k = 0 standing .. 1 lying on its belly on folded legs (theropod.Plan.lie); neck_down lays the neck flat"""
    T.lie(p, k)
    add(p, "neck1", rot=(-58 * neck_down, 0, 0)); add(p, "neck3", rot=(46 * neck_down, 0, 0))
    skull(p, 8 * neck_down)
    tail(p, pitch=10 * k)
    return p


def hide(t):
    """hidden among the ferns: flat on its belly, the neck laid out on the ground, the head flat, the tail flat behind;
    only the slow breath and an eye that stays open"""
    p = {}; br = math.sin(W(t, 3.4))
    lie(p, 1.0, 1.0)
    add(p, "body", rot=(-14 + 0.5 * br, 0, 0))
    neck(p, -0.4 * br)
    return ground_fit(p)


def peek(t):
    """from the hide: the head comes up slowly over the ferns, looks one way and the other in jerks, and goes down"""
    p = {}
    up = f(tr((0, 0), (0.6, 1, ease_out), (2.4, 1), (3.0, 0)), t)
    lie(p, 1.0, 1.0 - up)
    add(p, "body", rot=(-14 * (1 - up), 0, 0))
    hp, hy, hr = snap(t, [(0.0, (0, 0, 0)), (0.8, (4, 26, -8)), (1.6, (2, -24, 8)), (2.3, (0, 0, 0))])
    neck(p, 14 * up + hp * 0.5 * up, hy * 0.6 * up); skull(p, hp * 0.4 * up, hy * 0.4 * up, hr * up)
    nostrils(p, t, up)
    return ground_fit(p)


def sit(t):
    p = {}; br = math.sin(W(t, 3.0))
    lie(p, 1.0)
    add(p, "body", rot=(0.8 * br, 0, 0))
    hp, hy, hr = snap(t, [(0.0, (0, 0, 0)), (1.6, (2, 20, -6)), (3.2, (0, 0, 0)), (4.6, (2, -20, 6)), (6.0, (0, 0, 0))])
    neck(p, 6 + hp * 0.5, hy * 0.6); skull(p, hp * 0.4, hy * 0.4, hr)
    return ground_fit(p)


TUCK = {"neck1": (-34, 0, 0), "neck2": (6, 52, 0), "neck3": (8, 56, 0), "skull": (12, 34, -16)}


def tuck(p, k):
    """curled as in a burrow: the neck bent back along the left flank, the head beside the thigh, the tail round the
    other way"""
    for b, r in TUCK.items():
        add(p, b, rot=tuple(x * k for x in r))
    tail(p, yaw=-34 * k)
    add(p, "tail2", rot=(0, -10 * k, 0)); add(p, "tail3", rot=(0, -10 * k, 0))


def sleep(t):
    """asleep in the open (no burrow): lying, the neck down along the ground, slow breaths"""
    p = {}; br = math.sin(W(t, 4.2))
    lie(p, 1.0, 0.8)
    add(p, "body", rot=(0.9 * br, 0, 0), pos=(0, 0.3 * br, 0))
    jaw(p, -1.0 * max(0, br))
    return ground_fit(p)


def burrow_sleep(t):
    """asleep in the burrow: curled tight, the head along the flank, the tail wrapped round; slow deep breaths"""
    p = {}; br = math.sin(W(t, 4.6))
    lie(p, 1.0); tuck(p, 1.0)
    add(p, "body", rot=(0.8 * br, 0, -4), pos=(0, 0.35 * br, 0))
    return ground_fit(p)


def wake_sleep(t):
    p = {}
    hd = f(tr((0, 0.8), (0.6, 0, ease_out), (2.4, 0)), t)
    up = f(tr((0, 1), (0.9, 1), (1.7, 0, back_out), (2.4, 0)), t)
    lie(p, up, hd)
    env = math.exp(-((t - 2.0) / 0.18) ** 2)
    skull(p, 0, 4 * env * math.sin(2 * math.pi * 6 * t), 10 * env * math.sin(2 * math.pi * 6 * t))
    return ground_fit(p)


LIE_DOWN_T, GET_UP_T = 1.4, 1.2


def lie_down(t):
    p = {}
    k = f(tr((0, 0), (1.2, 1, ease_in), (1.32, 0.96), (1.4, 1.0)), t)
    lie(p, k)
    return ground_fit(p)


def get_up(t):
    p = {}
    k = f(tr((0, 1), (0.2, 1.02), (1.0, 0, back_out), (1.2, 0)), t)
    lie(p, k)
    return ground_fit(p)


def _on_side(p, k):
    add(p, "root", rot=(0, 0, 80 * k))
    neck(p, -20 * k, 0, -10 * k); skull(p, -6 * k, 0, -8 * k)


def knocked_out(t):
    p = {}; br = math.sin(W(t, 4.0))
    lie(p, 0.7); _on_side(p, 1.0)
    add(p, "body", rot=(0.8 * br, 0, 0)); jaw(p, -4 - 1.5 * br)
    add(p, "thigh_l", rot=(16, 0, 0)); add(p, "shin_l", rot=(18, 0, 0))
    arms(p, 14, 0, 10)
    return ground_fit(p)


def knockout(t):
    """staggers, the legs give, it sits back and rolls onto its side (into knocked_out)"""
    p = {}
    g = f(tr((0, 0), (0.4, 0.2), (1.0, 0.7, ease_in), (2.0, 0.7)), t)
    rl = f(tr((0, 0), (0.9, 0), (1.5, 1.0, ease_in), (1.62, 0.94), (1.75, 1.0), (2.0, 1.0)), t)
    lie(p, g); _on_side(p, rl)
    sway = math.sin(2 * math.pi * 2.0 * t) * (1 - smooth((t - 0.8) / 0.3))
    add(p, "body", rot=(0, 6 * sway, 4 * sway))
    jaw(p, -8 * window(t, 0.2, 1.4))
    return ground_fit(p)


def wake(t):
    p = {}
    roll = f(tr((0, 1), (0.3, 1), (0.9, 0, ease_out), (3.0, 0)), t)
    k = f(tr((0, 0.7), (0.9, 1.0), (1.8, 1.0), (2.5, 0, back_out), (3.0, 0)), t)
    lie(p, k); _on_side(p, roll)
    env = math.exp(-((t - 1.4) / 0.2) ** 2)
    neck(p, 6 * env * math.sin(2 * math.pi * 3 * t), 8 * env * math.sin(2 * math.pi * 3 * t))
    skull(p, 0, 10 * env * math.sin(2 * math.pi * 8 * t), 18 * env * math.sin(2 * math.pi * 8 * t))
    return ground_fit(p)


def death(t):
    p = {}
    g = f(tr((0, 0), (0.3, 0.15), (0.8, 0.8, ease_in), (3.0, 0.8)), t)
    rl = f(tr((0, 0), (1.2, 0), (1.7, 1.0, ease_in), (1.85, 0.94), (2.0, 1.0), (3.0, 1.0)), t)
    lie(p, g, smooth((t - 0.6) / 0.6)); _on_side(p, rl)
    jaw(p, -12 * window(t, 0.1, 0.7) - 6 * smooth((t - 1.7) / 0.4))
    arms(p, 0, 0, 20 * window(t, 0.2, 1.0, 0.2) + 8 * rl)
    return ground_fit(p)


# ------------------------------------------------------------------ voice and fight
def call(t):
    """the contact hoot: the neck stretched up and forward, the bill a little open, two pulses of the throat"""
    p = {}
    k = f(tr((0, 0), (0.4, 1, ease_out), (1.6, 1), (2.2, 0)), t)
    pulse = sum(math.exp(-((t - c) / 0.12) ** 2) for c in (0.8, 1.25))
    add(p, "body", rot=(3 * k + 1.5 * pulse, 0, 0))
    neck(p, 12 * k + 3 * pulse); skull(p, 10 * k)
    jaw(p, -5 * k - 4 * pulse)
    breathe(p, t)
    return stand(p)


def tail_flag(t):
    """the warning flag: the stiff tail flicked up high twice, showing the pale underside, the head up"""
    p = {}
    fl = sum(math.exp(-((t - c) / 0.12) ** 2) for c in (0.35, 0.8))
    hold = f(tr((0, 0), (0.25, 1, ease_out), (1.0, 1), (1.3, 0)), t)
    tail(p, pitch=-22 * hold - 10 * fl)
    add(p, "body", rot=(-3 * hold, 0, 0))
    neck(p, 8 * hold); skull(p, -2 * hold)
    return stand(p, (1.0, -1.0))


def alarm(t):
    """a sharp honk with the tail flicked up: the others see the flag and run"""
    p = tail_flag(t * 1.3 / 1.6)
    k = math.exp(-((t - 0.5) / 0.15) ** 2)
    jaw(p, -12 * k); neck(p, 6 * k)
    return p


def attack(t):
    """cornered, the bite with the front teeth: drawn back, then the head darts forward and down, snaps, recoils (the
    blow lands at 0.45 s)"""
    p = {}
    N = tr((0, (0, 0, 0)), (0.3, (14, -4, 0)), (0.45, (-26, 2, 0), ease_in), (0.6, (-22, 0, 0)), (1.0, (0, 0, 0)))
    J = tr((0, 0), (0.3, -14), (0.45, -16), (0.5, 0, ease_in), (1.0, 0))
    B = tr((0, 0), (0.3, 4), (0.45, -8, ease_in), (0.7, -4), (1.0, 0))
    n = N(t)
    add(p, "body", rot=(float(B(t)), 0, 0), pos=(0, 0, -2.0 * window(t, 0.35, 0.6, 0.1)))
    neck(p, n[0], n[1]); skull(p, n[0] * 0.4); jaw(p, float(J(t)))
    tail(p, pitch=-float(B(t)) * 0.8)
    return stand(p, (2.0, -2.0))


def kick(t):
    """the strong leg forward: weight on one foot, the other thigh drawn up and the foot driven forward and down, the
    nails raking (the blow lands at 0.5 s)"""
    p = {}
    add(p, "body", rot=(6 * window(t, 0.15, 0.7, 0.1), 0, -3 * window(t, 0.1, 0.8, 0.1)), pos=(0, 0.6, 0))
    neck(p, -6 * window(t, 0.3, 0.7, 0.1)); skull(p, -4)
    plant(p, "r", 0.0, ZC + 1.0)
    K_ = tr((0, (0, 0, 0, 0)), (0.3, (9, -2, 30, -30)), (0.5, (5, -11, -10, 10), ease_in), (0.65, (2, -8, 5, 0)),
            (1.0, (0, 0, 0, 0)))
    dy, dz, meta, toe = K_(t)
    plant(p, "l", float(dy), ZC + float(dz), float(meta), float(toe), 0.3 if dy > 0.2 else -0.05)
    tail(p, pitch=4 * window(t, 0.2, 0.7, 0.1))
    return p


KICK_BACK_T = 1.1


def kick_back(t):
    """something at its tail: the head round the flank to see it, the weight forward, a hind foot driven back (the
    blow lands at 0.45 s)"""
    p = {}
    look = window(t, 0.0, 0.9, 0.15)
    add(p, "body", rot=(-8 * window(t, 0.2, 0.7, 0.1), 6 * look, 0))
    neck(p, -4 * look, 40 * look); skull(p, 0, 26 * look)
    plant(p, "l", 0.0, ZC - 2.0)
    K_ = tr((0, (0, 0, 0)), (0.25, (6, -3, 30)), (0.45, (3, 14, 50), ease_in), (0.6, (2, 10, 30)), (1.1, (0, 0, 0)))
    dy, dz, meta = K_(t)
    plant(p, "r", float(dy), ZC + float(dz), float(meta), -float(meta) * 0.5, 0.3 if dy > 0.2 else -0.05)
    tail(p, yaw=-10 * window(t, 0.3, 0.7, 0.1), pitch=-6 * window(t, 0.3, 0.7, 0.1))
    return p


def hurt(t):
    p = {}
    e = math.exp(-((t - 0.12) / 0.12) ** 2)
    add(p, "body", rot=(-5 * e, 6 * e, -4 * e), pos=(0, -1.0 * e, 1.5 * e))
    neck(p, 10 * e, -8 * e); skull(p, 6 * e, -6 * e, 6 * e); jaw(p, -14 * e)
    tail(p, pitch=-8 * e)
    return stand(p)


def look_back(t):
    p = {}
    k = f(tr((0, 0), (0.6, 1, ease_out), (2.2, 1), (3.0, 0)), t)
    add(p, "body", rot=(0, 8 * k, -2 * k)); neck(p, 4 * k, 46 * k); skull(p, 2 * k, 28 * k, -8 * k)
    breathe(p, t)
    return stand(p)


def shake(t):
    p = {}
    env = window(t, 0.3, 1.5, 0.12)
    for bone, a, d in (("skull", 14, 0.0), ("neck", 9, 0.05), ("body", 4, 0.12)):
        r = (0, a * 0.4 * env * math.sin(2 * math.pi * 7 * (t - d)), a * env * math.sin(2 * math.pi * 7 * (t - d)))
        neck(p, *r) if bone == "neck" else add(p, bone, rot=r)
    jaw(p, -5 * env)
    tail(p, yaw=4 * env * math.sin(2 * math.pi * 7 * (t - 0.15)))
    return stand(p)


def hatch(t):
    """out of the egg: curled tight, the head pushes up and out, a shake, a first look round, then up onto its legs"""
    p = {}
    up = f(tr((0, 1), (0.6, 1), (1.8, 0, back_out), (2.4, 0)), t)
    lie(p, up, 0.0); tuck(p, f(tr((0, 1), (0.5, 0, ease_out), (2.4, 0)), t))
    push = window(t, 0.2, 0.9, 0.15)
    neck(p, 20 * push)
    env = math.exp(-((t - 1.0) / 0.15) ** 2)
    skull(p, 0, 10 * env * math.sin(2 * math.pi * 8 * t), 14 * env * math.sin(2 * math.pi * 8 * t))
    return ground_fit(p)


def beg(t):
    """asks for food: quick little bobs toward the owner, the head tilted, a hand reaching"""
    p = {}; Tb = 1.6
    pk = sum(math.exp(-((t - c) / 0.06) ** 2) for c in (0.3, 0.5, 1.1, 1.3))
    add(p, "body", rot=(-4, 0, 0), pos=(0, -0.8, 0))
    neck(p, -12 - 6 * pk); skull(p, -4 * pk, 0, 12)
    jaw(p, -6 * pk)
    arms(p, -18 - 6 * math.sin(W(t, Tb)), 0)
    tail(p, yaw=2 * math.sin(W(t, Tb)))
    return stand(p)


def tame(t):
    """accepts the owner: a short hoot, the head lowered to them and a bob"""
    p = {}
    k = f(tr((0, 0), (0.5, 1, ease_out), (1.8, 1), (2.6, 0)), t)
    toss = math.exp(-((t - 0.5) / 0.15) ** 2)
    add(p, "body", rot=(-5 * k, 0, 0), pos=(0, 0.6 * toss, 0))
    neck(p, -20 * k + 8 * toss); skull(p, -6 * k)
    jaw(p, -10 * toss)
    tail_wave(p, t, 0.8, yaw=5 * k)
    return stand(p)


ANIMS = {
    "idle": (idle, IDLE_T, True, "Parado", "em pé nas duas pernas, respira, olha em trancos de ave, fareja de vez em quando"),
    "walk": (walk, WALK[0], True, "Movimento", "passo de ave do chão: a cabeça vai e volta com o passo, a cauda dura reta"),
    "run": (run, RUN[0], True, "Movimento", "corrida: o tronco nivela, o pescoço estica, a cauda contrapeso"),
    "bolt": (bolt, 4 * BOLT[0], True, "Só dele", "o disparo: corrida em ziguezague, baixo, a cauda erguida mostrando o lenço claro"),
    "swim": (swim, 1.2, True, "Movimento", "nada com o pescoço alto, as pernas remando"),
    "turn_left": (turn_left, TURN_T, True, "Movimento", "gira no lugar para a esquerda"),
    "turn_right": (turn_right, TURN_T, True, "Movimento", "gira no lugar para a direita"),
    "walk_tired": (walk_tired, 1.3, True, "Movimento", "anda cansado, cabeça baixa, bico aberto"),
    "idle_tired": (idle_tired, 2.7, True, "Parado", "parado cansado, ofegando"),
    "freeze": (freeze, 2.0, True, "Só dele", "congela no meio do passo: um pé na ponta, cabeça erguida e parada, só as narinas mexem"),
    "sniff_ground": (sniff_ground, 3.4, False, "Só dele", "fareja o chão, a cabeça baixa varrendo de um lado ao outro"),
    "sniff_air": (sniff_air, 3.0, False, "Só dele", "fareja o ar de focinho erguido e vira para testar o vento"),
    "sniff": (sniff_ground, 3.4, False, "Parado", "gesto sorteado parado: fareja o chão"),
    "dig": (dig, 3.2, False, "Só dele", "cava raízes: as mãos raspam o chão, o focinho entra e puxa"),
    "burrow_dig": (burrow_dig, 4.0, False, "Só dele", "cava a toca: as mãos raspam o barranco, o focinho empurra, um pé joga a terra para trás"),
    "burrow_sleep": (burrow_sleep, 9.2, True, "Só dele", "dorme na toca enrolado, a cabeça no flanco, a cauda dobrada em volta"),
    "hide": (hide, 6.8, True, "Só dele", "escondido no mato: deitado rente, o pescoço estendido no chão"),
    "peek": (peek, 3.0, False, "Só dele", "levanta a cabeça do esconderijo, olha de um lado e do outro e abaixa"),
    "tail_flag": (tail_flag, 1.3, False, "Só dele", "o lenço: a cauda dura sobe duas vezes mostrando a parte clara"),
    "alarm": (alarm, 1.6, False, "Só dele", "o alarme: um grito curto com a cauda erguida"),
    "call": (call, 2.2, False, "Voz", "o pio de contato: pescoço esticado, dois pulsos da garganta"),
    "look_back": (look_back, 3.0, False, "Parado", "gesto sorteado parado: olha para trás"),
    "shake": (shake, 1.8, False, "Parado", "gesto sorteado parado; ao sair da água"),
    "hatch": (hatch, 2.4, False, "Domado", "sai do ovo: a cabeça empurra, sacode, olha e levanta"),
    "eat": (eat, 3.0, False, "Comer", "pega da mão com os dentes da frente e mastiga, as bochechas abrindo"),
    "graze": (graze, 3.4, False, "Comer", "corta samambaia baixa com os dentes da frente"),
    "drink": (drink, 3.8, False, "Comer", "bebe com a cabeça até a água"),
    "attack": (attack, 1.0, False, "Combate", "encurralado: a mordida com os dentes da frente (golpe em 0,45 s)"),
    "kick": (kick, 1.0, False, "Combate", "encurralado: o chute para a frente com a perna forte (golpe em 0,5 s)"),
    "kick_back": (kick_back, KICK_BACK_T, False, "Combate", "olha para trás e chuta com a pata de trás (golpe em 0,45 s)"),
    "hurt": (hurt, 0.6, False, "Combate", "ao levar dano"),
    "death": (death, 3.0, False, "Combate", "as pernas cedem, deita e rola de lado"),
    "knockout": (knockout, 2.0, False, "Descanso", "nocauteado: cambaleia, senta e rola de lado"),
    "knocked_out": (knocked_out, 4.0, True, "Descanso", "nocauteado de lado"),
    "wake": (wake, 3.0, False, "Descanso", "acorda do nocaute: rola, sacode a cabeça e levanta"),
    "sit": (sit, 6.0, True, "Descanso", "deitado de barriga sobre as pernas dobradas, olhando em volta"),
    "sleep": (sleep, 8.4, True, "Descanso", "dorme deitado no mato, o pescoço no chão"),
    "wake_sleep": (wake_sleep, 2.4, False, "Descanso", "acorda e levanta"),
    "lie_down": (lie_down, LIE_DOWN_T, False, "Descanso", "deita sobre as pernas dobradas"),
    "get_up": (get_up, GET_UP_T, False, "Descanso", "levanta num impulso"),
    "beg": (beg, 1.6, True, "Domado", "pede comida: balança a cabeça para o dono"),
    "tame": (tame, 2.6, False, "Domado", "aceita o dono: um pio curto e a cabeça baixa"),
}
