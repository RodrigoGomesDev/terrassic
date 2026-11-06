"""Pachycephalosaurus animations, written for it from its own study (page "Paquicefalossauro: estudo e modelo",
section "movimento").

Only the plumbing is shared (anim2: easing, leg IK with planted feet, export; theropod.Plan: plant/stand). The poses
are its own, from what the study says the animal was:
- a heavy, wide-hipped walker: the hips roll from side to side with each step (a waddle), the head is held low and
  steady in front of the shoulders on the short S of the neck;
- the tail is STIFF from its middle back (the basket of ossified tendons, Brown & Schlaikjer 1943): it swings and
  lifts only at the root and the rest follows as one beam, never a whip;
- the butt: the head drops so the dome faces forward and the neck straightens into line with the back (Galton
  1970); two males meet dome to dome (the healed lesions on the domes, Peterson et al. 2013) and shove; at a smaller
  foe it swings the dome into the flank (Carpenter 1997);
- the dome is shown side-on as a display, the head tilted and bobbed (Goodwin & Horner 2004: display as much as
  combat);
- a big nose (large olfactory bulbs, Giffin 1989): it sniffs along the forest floor for fallen fruit, and picks
  berries and buds with the small front teeth, rising to reach them (a selective browser);
- the young (the flat-headed, spiky stage) bounce and spin at play instead of butting: the dome is not there yet.
"""
import math
import os
import sys
_H = os.path.dirname(os.path.abspath(__file__))
_E = os.path.join(_H, "..", "_engine")
sys.path[:0] = [_H, _E, os.path.join(_E, "plans")]
import proto as P
import pachy
import theropod
from anim2 import add, Track, smooth, ease_out, ease_in, back_out, lowest
from theropod import window, W, SIDES

TAILS = ("tail1", "tail2", "tail3", "tail4", "tail5", "tail6")
NECKS = ("neck1", "neck2")


def model():
    m = pachy.build(); P.pack(m, pachy.TEX_W); return m.spec()


S = model()
T = theropod.Plan(S, K=1.0, necks=NECKS, tails=TAILS)
SKIP = ("bristle",)


def tr(*keys): return Track(keys)


def tail(p, yaw=0.0, pitch=0.0):
    """the stiff tail: it bends at the root (tail1, tail2) and the tendon-wrapped rest follows as one beam"""
    for b, w in zip(TAILS, (1.0, 0.7, 0.12, 0.05, 0.03, 0.02)):
        add(p, b, rot=(pitch * w, yaw * w, 0))


def neck(p, pitch=0.0, yaw=0.0, roll=0.0):
    for b, k in zip(NECKS, (0.55, 0.45)):
        add(p, b, rot=(pitch * k, yaw * k, roll * k))


RAM = {"body": (-4, 0, 0), "neck1": (-40, 0, 0), "neck2": (10, 0, 0), "skull": (-75, 0, 0)}


def ram(p, k):
    """the butting posture: the head dropped so the dome faces forward, the neck straight in line with the back"""
    for b, r in RAM.items(): add(p, b, rot=tuple(x * k for x in r))


REACH = {"body": (-12, 0, 0), "neck1": (-50, 0, 0), "neck2": (8, 0, 0), "skull": (-10, 0, 0)}


def reach(p, k):
    """nose to the ground: the body tips forward over the legs and the short neck reaches down"""
    for b, r in REACH.items(): add(p, b, rot=tuple(x * k for x in r))


def arms(p, a=0.0, f=0.0):
    for s in ("l", "r"):
        add(p, f"arm_{s}", rot=(a, 0, 0)); add(p, f"forearm_{s}", rot=(f, 0, 0))


# ------------------------------------------------------------------ gait: a heavy waddle, steady head, stiff tail
WALK = (1.1, 44, 0.64, 7, 0.8)
RUN = (0.55, 100, 0.38, 13, 2.2)


def gait(t, Tc, stride, duty, lift, bob, lean=0.0, drop=0.0, head=0.0, roll=3.2, stance_clear=-0.05, rammed=0.0):
    ph = (t / Tc) % 1.0; w = 2 * math.pi * ph; p = {}
    # the wide hips roll over each stance leg and yaw a little; the body bobs twice a cycle
    br = roll * math.sin(w + 0.3); by = 1.6 * math.sin(w)
    add(p, "body", rot=(lean + 0.5 * math.sin(2 * w - 0.4), by, br), pos=(0, -bob * math.cos(2 * w - 0.9) - 0.4 - drop, 0))
    # the head held steady: the neck cancels the body's roll and yaw, a small nod with the steps
    neck(p, head - lean * 0.7 + 1.5 * math.sin(2 * w - 1.3), -by * 0.8, -br * 0.9)
    add(p, "skull", rot=(-head * 0.3 - 0.8 * math.sin(2 * w - 1.6), 0, -br * 0.2))
    if rammed: ram(p, rammed)
    tail(p, yaw=-3.0 * math.sin(w - 0.6), pitch=lean * 0.5 + 0.6 * math.sin(2 * w - 1.2))
    arms(p, 3 * math.sin(2 * w - 2.0), 2 * math.sin(2 * w - 2.4))
    for s, o in SIDES:
        u = (ph + o) % 1.0
        if u < duty:
            st = u / duty; dz = -stride * duty / 2 + stride * duty * st; ly = 0.0
            meta = 26 * smooth(max(0, (st - 0.6) / 0.4)); toe = 0.0; clear = stance_clear
        else:
            sw = (u - duty) / (1 - duty); e = 0.5 - 0.5 * math.cos(math.pi * sw)
            dz = stride * duty / 2 - stride * duty * e
            ly = lift * math.sin(math.pi * min(1, sw * 1.1)) ** 1.2
            meta = 26 * (1 - smooth(sw / 0.45)) - 16 * math.sin(math.pi * sw)
            toe = -24 * math.sin(math.pi * min(1, sw * 1.1)) + 4 * smooth((sw - 0.75) / 0.25)
            clear = 1.0 * math.sin(math.pi * sw) ** 0.5
        T.plant(p, s, ly, dz - 2, meta, toe, clear)
    return p


def walk(t):
    return gait(t, *WALK)


def run(t):
    """the heavy run: the body drops and levels, the head comes down half way to the butting line, the tail lifts as a
    beam"""
    p = gait(t, *RUN, lean=4, drop=2.5, head=-10, roll=1.6, stance_clear=0.2, rammed=0.35)
    tail(p, pitch=3)
    return p


def swim(t):
    """the legs paddle in turn, the head held up and the dome clear of the water, the stiff tail steers from the root"""
    Tc = 1.4; w = W(t, Tc); p = {}
    add(p, "body", rot=(3 + 1.5 * math.sin(2 * w), 2 * math.sin(w), 3 * math.sin(w + 0.4)), pos=(0, 1.0 * math.sin(2 * w), 0))
    neck(p, 22 - 2 * math.sin(2 * w + 0.5), -2 * math.sin(w)); add(p, "skull", rot=(-10, 0, 0))
    tail(p, yaw=7 * math.sin(w - 0.8), pitch=1)
    for s, o in SIDES:
        f = w + o * 2 * math.pi
        add(p, f"thigh_{s}", rot=(-8 + 28 * math.sin(f), 0, 0)); add(p, f"shin_{s}", rot=(-20 - 26 * math.cos(f), 0, 0))
        add(p, f"foot_{s}", rot=(26 + 22 * math.cos(f + 0.6), 0, 0)); add(p, f"toes_{s}", rot=(-30 * math.sin(f + 1.0), 0, 0))
    arms(p, -16, 10)
    return p


# ------------------------------------------------------------------ standing
def idle(t):
    """breathing; it looks about slowly, the head turned with the whole short neck, and now and then it shifts its
    weight from one broad hip to the other"""
    p = {}; br = math.sin(W(t, 2.4))
    shift = 1.6 * math.sin(W(t, 8.0))
    add(p, "body", rot=(0.6 * br, 0, shift), pos=(0, 0.3 * br, 0))
    look = tr((0, (0, 0)), (1.2, (0, 0)), (1.8, (3, 18), ease_out), (3.4, (3, 18)), (4.0, (-2, -14), ease_out),
              (5.6, (-2, -14)), (6.3, (0, 0)))
    lp, ly = look(t)
    neck(p, lp - 0.6 * br, ly * 0.8, -shift)
    add(p, "skull", rot=(lp * 0.5, ly * 0.3, 0))
    add(p, "jaw", rot=(-0.6 - 0.6 * max(0, br), 0, 0))
    tail(p, yaw=1.2 * math.sin(W(t, 8.0) - 0.6), pitch=0.4 * math.sin(W(t, 2.4) - 0.8))
    arms(p, 1.2 * br)
    return T.stand(p)


def dome_display(t):
    """the dome shown: it turns side-on to the other, lifts the head high and tilts it so the dome is seen in full,
    bobs it twice, then holds and lowers it"""
    p = {}
    k = float(tr((0, 0), (0.6, 1, ease_out), (3.4, 1), (4.0, 0))(t))
    bob = sum(math.exp(-((t - c) / 0.12) ** 2) for c in (1.4, 2.0))
    add(p, "body", rot=(4 * k, -14 * k, 0), pos=(0, 1.5 * k, 0))
    neck(p, 26 * k - 10 * bob, 22 * k, 0)
    add(p, "skull", rot=(-10 * k + 8 * bob, 10 * k, -22 * k))
    tail(p, yaw=10 * k, pitch=-2 * k)
    arms(p, -6 * k)
    T.plant(p, "l", 0, -2 * k, 0, 0); T.plant(p, "r", 0, 2 * k, 0, 0)
    return p


def warn(t):
    """the warning to one who comes too close without food: the head drops into the butting line and swings a little
    from side to side, a hind foot scuffs the ground, the stiff tail lifts"""
    p = {}
    k = float(tr((0, 0), (0.35, 1, ease_out), (1.6, 1), (2.0, 0))(t))
    sway = math.sin(2 * math.pi * 1.4 * t) * window(t, 0.4, 1.6, 0.2)
    ram(p, 0.8 * k)
    add(p, "body", rot=(0, 3 * sway, 0), pos=(0, -1.5 * k, 0))
    neck(p, 0, 8 * sway, 0)
    tail(p, pitch=-5 * k, yaw=-3 * sway)
    scuff = window(t, 0.7, 1.2, 0.1)
    T.plant(p, "l")
    T.plant(p, "r", 3 * scuff, 4 * scuff - 6 * smooth((t - 0.8) / 0.3) * scuff, 0, -10 * scuff)
    return p


def sniff(t):
    """nose to the forest floor: it walks the snout along in short sniffs, finds a fallen fruit, mouths it up and
    tips the head back to swallow"""
    p = {}
    down = float(tr((0, 0), (0.4, 1, ease_out), (2.4, 1), (2.8, 0, ease_out), (3.4, 0))(t))
    sn = sum(math.exp(-((t - c) / 0.06) ** 2) for c in (0.6, 0.85, 1.1, 1.5, 1.75))
    sweep = math.sin(2 * math.pi * 0.6 * (t - 0.4)) * window(t, 0.4, 2.0, 0.2)
    pick = math.exp(-((t - 2.2) / 0.08) ** 2)
    swallow = window(t, 2.8, 3.2, 0.1)
    reach(p, down)
    neck(p, 3 * sn, 14 * sweep, 0); add(p, "skull", rot=(-2 * sn + 6 * swallow, 8 * sweep, 0))
    add(p, "jaw", rot=(-10 * pick - 4 * swallow, 0, 0))
    tail(p, pitch=3 * down)
    return T.stand(p)


def pluck(t):
    """a selective browser: it rises tall on its hind legs to a bush, picks with the front of the beak (it had teeth
    there), pulls each berry off with a jerk, and chews"""
    p = {}
    k = float(tr((0, 0), (0.5, 1, ease_out), (2.8, 1), (3.3, 0))(t))
    picks = [math.exp(-((t - c) / 0.07) ** 2) for c in (1.0, 1.6, 2.2)]
    jerk = sum(picks)
    chew = math.sin(2 * math.pi * 4 * t) * window(t, 2.6, 3.4, 0.1)
    add(p, "body", rot=(10 * k, 0, 0), pos=(0, 0.8 * k, 0))
    neck(p, 20 * k + 6 * jerk, 4 * math.sin(2 * math.pi * 0.7 * t) * k)
    add(p, "skull", rot=(-12 * k - 8 * jerk, 0, 0))
    add(p, "jaw", rot=(-8 * jerk - 3 * max(0, chew), 0, 0))
    arms(p, -40 * k, 30 * k)
    tail(p, pitch=-6 * k)
    T.plant(p, "l", 0, 0, 0, 0); T.plant(p, "r", 0, 0, 0, 0)
    return p


# ------------------------------------------------------------------ feeding
def eat(t):
    """it crops a mouthful at chest height with the beak and chews it (cheek teeth), the jaw working sideways"""
    p = {}
    down = float(tr((0, 0), (0.3, 0.6, ease_out), (0.7, 0.6), (1.0, 0, ease_out), (2.6, 0))(t))
    bite = math.exp(-((t - 0.55) / 0.07) ** 2)
    chew = math.sin(2 * math.pi * 3.5 * t) * window(t, 1.0, 2.4, 0.15)
    reach(p, down)
    add(p, "jaw", rot=(-10 * bite - 3 * max(0, chew), 2 * chew, 0))
    add(p, "skull", rot=(0, 0, 1.5 * chew))
    tail(p, pitch=2 * down)
    return T.stand(p)


def graze(t):
    """crops low ferns: the nose down, two bites with a pull of the head, a step forward, chewing"""
    p = {}
    down = float(tr((0, 0), (0.4, 1, ease_out), (2.4, 1), (2.9, 0))(t))
    bites = sum(math.exp(-((t - c) / 0.07) ** 2) for c in (0.9, 1.6))
    pull = sum(math.exp(-((t - c) / 0.12) ** 2) for c in (1.0, 1.7))
    chew = math.sin(2 * math.pi * 3.5 * t) * window(t, 1.9, 2.9, 0.15)
    reach(p, down)
    neck(p, 6 * pull, 0); add(p, "skull", rot=(4 * pull, 0, 0))
    add(p, "jaw", rot=(-10 * bites - 3 * max(0, chew), 1.5 * chew, 0))
    tail(p, pitch=3 * down)
    step = window(t, 1.9, 2.4, 0.1)
    T.plant(p, "l", 3 * step, -5 * smooth((t - 1.9) / 0.5), 0, -15 * step)
    T.plant(p, "r")
    return p


# ------------------------------------------------------------------ combat: the dome
def attack(t):
    """the butt: it drops into the butting line, drives forward off both legs, the dome hits, and it recoils"""
    p = {}
    k = float(tr((0, 0), (0.2, 1, ease_out), (0.75, 1), (1.0, 0))(t))
    drive = float(tr((0, 0), (0.25, -0.3), (0.42, 1, ease_in), (0.5, 0.8), (0.7, 0), (1.0, 0))(t))
    ram(p, k)
    add(p, "body", rot=(-3 * drive, 0, 0), pos=(0, -1.5 * k, -5 * drive))
    neck(p, -4 * drive, 0)
    tail(p, pitch=-4 * k + 3 * drive)
    arms(p, -10 * k)
    T.plant(p, "l", 0, 2, 10 * max(0, drive), 0); T.plant(p, "r", 0, -2, 10 * max(0, drive), 0)
    return p


def flank_butt(t):
    """the side blow (Carpenter 1997): head down, it swings the dome sideways into the foe's flank with a twist of the
    whole neck, then straightens"""
    p = {}
    k = float(tr((0, 0), (0.2, 1, ease_out), (0.7, 1), (1.0, 0))(t))
    sw = float(tr((0, 0), (0.25, -1, ease_out), (0.45, 1, ease_in), (0.55, 0.9), (0.85, 0))(t))
    ram(p, 0.7 * k)
    add(p, "body", rot=(0, 10 * sw, 4 * sw))
    neck(p, 0, 34 * sw, 12 * sw)
    add(p, "skull", rot=(0, 10 * sw, 14 * sw))
    tail(p, yaw=-12 * sw)
    T.plant(p, "l", 0, 0, 0, 0); T.plant(p, "r", 0, 0, 0, 0)
    return p


def dome_clash(t):
    """two males meet dome to dome (Peterson et al. 2013): a stare with the dome shown, a backward step, the head
    drops, a short rush, the hit (the whole body jars and the tail flicks up), a shove dome against dome, and it
    backs off shaking its head"""
    p = {}
    show = window(t, 0.0, 0.9, 0.25)
    k = float(tr((0, 0), (0.9, 0), (1.2, 1, ease_out), (3.0, 1), (3.4, 0))(t))
    rush = float(tr((0, 0), (1.1, 0), (1.3, -0.4), (1.6, 1, ease_in), (1.7, 0.7), (2.0, 0.85), (2.8, 0.85), (3.2, 0))(t))
    hit = math.exp(-((t - 1.65) / 0.05) ** 2)
    shove = math.sin(2 * math.pi * 2.5 * t) * window(t, 1.9, 2.8, 0.1)
    shake = math.sin(2 * math.pi * 7 * t) * window(t, 3.3, 3.9, 0.08)
    add(p, "body", rot=(2 * show, 0, 0))
    neck(p, 12 * show, 0, 0); add(p, "skull", rot=(0, 0, -10 * show))
    ram(p, k)
    add(p, "body", rot=(-3 * rush + 3 * hit, 0, 2 * shove), pos=(0, -1.5 * k - 1.0 * hit, -6 * rush + 1.5 * shove))
    tail(p, pitch=-4 * k + 10 * hit, yaw=-4 * shove)
    add(p, "skull", rot=(0, 18 * shake, 10 * shake))
    T.plant(p, "l", 0, 3 + 2 * max(0, rush), 12 * max(0, rush), 0, clear=0.15)
    T.plant(p, "r", 0, -3 + 2 * max(0, rush), 12 * max(0, rush), 0, clear=0.15)
    return p


def hurt(t):
    """flinch: it ducks the head and twists away, the stiff tail jerks up"""
    p = {}
    k = float(tr((0, 0), (0.08, 1, ease_out), (0.6, 0))(t))
    add(p, "body", rot=(2 * k, 6 * k, 3 * k), pos=(0, 0, 1.5 * k))
    neck(p, -8 * k, -12 * k); add(p, "skull", rot=(-6 * k, 0, 8 * k)); add(p, "jaw", rot=(-8 * k, 0, 0))
    tail(p, pitch=-6 * k, yaw=5 * k)
    return T.stand(p)


# ------------------------------------------------------------------ resting
def ground_fit(p):
    lo = lowest(S, p, skip_mats=SKIP); add(p, "root", pos=(0, 0.1 - lo, 0)); return p


LIE_LEGS = {f"{b}_{s}": (a, 0, 0) for s, _ in SIDES for b, a in (("thigh", 50), ("shin", -96), ("foot", 112))}


def fold(p, k, neck_up=1.0):
    """k = 0 standing .. 1 lying on its folded legs, the heavy belly on the ground; the head stays up"""
    add(p, "body", rot=(-2 * k, 0, 0), pos=(0, -20 * k, 0))
    neck(p, 6 * k * neck_up, 0); add(p, "skull", rot=(-3 * k * neck_up, 0, 0))
    tail(p, pitch=-4 * k)
    arms(p, 6 * k)
    for n, r in LIE_LEGS.items(): add(p, n, rot=tuple(x * smooth(k) for x in r))
    return p


def sit(t):
    p = {}; br = math.sin(W(t, 3.0))
    fold(p, 1.0); add(p, "body", rot=(0.6 * br, 0, 0))
    look = tr((0, (0, 0)), (1.4, (0, 0)), (2.0, (2, 20), ease_out), (3.4, (2, 20)), (4.0, (0, -16), ease_out),
              (5.2, (0, -16)), (6.0, (0, 0)))
    lp, ly = look(t)
    neck(p, lp - 0.6 * br, ly * 0.8); add(p, "skull", rot=(lp * 0.5, ly * 0.3, 0))
    return ground_fit(p)


def doze(p, k):
    """the head lowered to rest the chin on the ground in front, the dome forward like a pillow-stone"""
    neck(p, -34 * k, 6 * k); add(p, "skull", rot=(10 * k, 4 * k, 6 * k))
    tail(p, yaw=-10 * k)


def sleep(t):
    p = {}; br = math.sin(W(t, 4.8))
    fold(p, 1.0); doze(p, 1.0)
    add(p, "body", rot=(0.7 * br, 0, 0), pos=(0, 0.3 * br, 0))
    return ground_fit(p)


def wake_sleep(t):
    """from sleep: the head comes up, a long stretch of the neck forward, then it stands in two pushes (heavy)"""
    p = {}
    dz = float(tr((0, 1), (0.6, 0, ease_out), (2.8, 0))(t))
    up = float(tr((0, 1), (1.2, 1), (1.7, 0.5, ease_out), (1.9, 0.5), (2.5, 0, back_out), (2.8, 0))(t))
    fold(p, up); doze(p, dz)
    st = window(t, 0.6, 1.2, 0.15)
    neck(p, -10 * st, 0); add(p, "skull", rot=(-14 * st, 0, 0)); add(p, "jaw", rot=(-10 * st, 0, 0))
    return ground_fit(p)


def _on_side(p, k):
    add(p, "root", rot=(0, 0, 78 * k))
    neck(p, -16 * k, 0, -10 * k); add(p, "skull", rot=(-6 * k, 0, -10 * k))


def knocked_out(t):
    p = {}; br = math.sin(W(t, 4.0))
    fold(p, 0.6, neck_up=0.0); _on_side(p, 1.0)
    add(p, "body", rot=(0.8 * br, 0, 0)); add(p, "jaw", rot=(-4 - 1.5 * br, 0, 0))
    add(p, "thigh_l", rot=(16, 0, 0)); add(p, "shin_l", rot=(18, 0, 0))
    arms(p, 14)
    return ground_fit(p)


def wake(t):
    """from the knockout: rolls onto its folded legs, the heavy head wobbles up, a shake of the dome, it stands"""
    p = {}
    roll = float(tr((0, 1), (0.3, 1), (0.9, 0, ease_out), (3.0, 0))(t))
    k = float(tr((0, 0.6), (0.9, 1.0), (1.8, 1.0), (2.5, 0, back_out), (3.0, 0))(t))
    fold(p, k, neck_up=1 - roll); _on_side(p, roll)
    env = math.exp(-((t - 1.4) / 0.2) ** 2)
    neck(p, -12 * roll + 6 * env * math.sin(2 * math.pi * 3 * t), 8 * env * math.sin(2 * math.pi * 3 * t))
    add(p, "skull", rot=(0, 12 * env * math.sin(2 * math.pi * 7 * t), 16 * env * math.sin(2 * math.pi * 7 * t)))
    return ground_fit(p)


def death(t):
    """the legs give, it sits back hard on the heavy belly, the head with the dome sinks to the ground, it rolls"""
    p = {}
    g = float(tr((0, 0), (0.25, 0.1), (0.8, 0.85, ease_in), (3.0, 0.85))(t))
    nk = float(tr((0, 0), (0.7, 0), (1.3, 1, ease_in), (1.45, 0.9), (1.6, 1.0), (3.0, 1.0))(t))
    rl = float(tr((0, 0), (1.4, 0), (1.9, 1.0, ease_in), (2.05, 0.94), (2.2, 1.0), (3.0, 1.0))(t))
    fold(p, g, neck_up=0.0)
    neck(p, 14 * window(t, 0.0, 0.6, 0.2) - 36 * nk * (1 - rl), 0)
    add(p, "skull", rot=(10 * nk * (1 - rl), 0, 0))
    _on_side(p, rl)
    add(p, "jaw", rot=(-12 * window(t, 0.1, 0.7) - 5 * smooth((t - 1.9) / 0.4), 0, 0))
    tail(p, pitch=3 * smooth((t - 0.8) / 0.4))
    return ground_fit(p)


# ------------------------------------------------------------------ with its owner and the young
def beg(t):
    """asks for food: the nose up toward the owner, short sniffs, a bob of the dome"""
    p = {}; br = math.sin(W(t, 1.6))
    sn = sum(math.exp(-((t - c) / 0.05) ** 2) for c in (0.3, 0.5, 1.1, 1.3))
    add(p, "body", rot=(3 + 0.6 * br, 0, 0))
    neck(p, 16 + 2 * sn, 0); add(p, "skull", rot=(12 - 3 * sn, 0, 6 * math.sin(W(t, 1.6))))
    add(p, "jaw", rot=(-3 * sn, 0, 0))
    tail(p, yaw=2 * math.sin(W(t, 1.6)), pitch=1)
    return T.stand(p)


def tame(t):
    """it accepts the owner: the head drops low with the dome turned aside (no threat), then rubs the side of the
    dome against them once and looks up"""
    p = {}
    k = float(tr((0, 0), (0.5, 1, ease_out), (1.8, 1), (2.6, 0))(t))
    rub = math.sin(2 * math.pi * 1.5 * t) * window(t, 0.8, 1.8, 0.15)
    add(p, "body", rot=(-6 * k, 0, 0), pos=(0, -2 * k, 0))
    neck(p, -24 * k, 10 * rub, 0); add(p, "skull", rot=(-4 * k, 0, 24 * k + 8 * rub))
    tail(p, pitch=2 * k, yaw=4 * rub)
    return T.stand(p)


def hop_play(t):
    """the young (the spiky stage, no dome to butt with) bounce at play: a crouch, a stiff-legged hop with a twist of
    the body and the tail, a landing, and again"""
    p = {}
    ph = (t % 0.8) / 0.8
    crouch = math.sin(math.pi * min(1, ph / 0.3)) * (ph < 0.3)
    air = math.sin(math.pi * max(0, min(1, (ph - 0.3) / 0.45)))
    side = 1 if int(t / 0.8) % 2 == 0 else -1
    add(p, "root", rot=(0, 18 * air * side, 0), pos=(0, 8 * air - 3 * crouch, 0))
    add(p, "body", rot=(-4 * air, 0, 6 * air * side))
    neck(p, 10 * air - 6 * crouch, -10 * air * side); add(p, "skull", rot=(0, 0, 10 * air * side))
    tail(p, yaw=-14 * air * side, pitch=-6 * air)
    for s in ("l", "r"):
        add(p, f"thigh_{s}", rot=(-10 * air, 0, 0)); add(p, f"shin_{s}", rot=(10 * air, 0, 0))
    if air < 0.05:
        T.stand(p)
    return p


ANIMS = {
    "idle": (idle, 8.0, True, "Parado", "respira, olha em volta virando o pescoço curto inteiro, troca o peso de quadril"),
    "walk": (walk, WALK[0], True, "Movimento", "passo pesado: o quadril largo balança de um lado para o outro, a cabeça fica firme, a cauda rígida só mexe na raiz"),
    "run": (run, RUN[0], True, "Movimento", "corrida pesada, cabeça a meio caminho da linha da cabeçada, cauda erguida como viga"),
    "swim": (swim, 1.4, True, "Movimento", "as pernas remam, a cúpula fica fora d'água, a cauda dirige pela raiz"),
    "dome_display": (dome_display, 4.0, False, "Só dele", "mostra a cúpula de lado: ergue e inclina a cabeça, sacode duas vezes"),
    "warn": (warn, 2.0, False, "Só dele", "aviso a quem chega sem comida: baixa a cúpula na linha da cabeçada, balança, raspa o pé"),
    "sniff": (sniff, 3.4, False, "Só dele", "fareja o chão da mata, acha uma fruta caída, apanha e engole"),
    "pluck": (pluck, 3.4, False, "Só dele", "ergue-se até um arbusto e arranca frutinhas uma a uma com os dentes da frente"),
    "eat": (eat, 2.6, False, "Comer", "corta um bocado e mastiga de lado"),
    "graze": (graze, 2.9, False, "Comer", "corta samambaia baixa com puxões de cabeça, dá um passo, mastiga"),
    "attack": (attack, 1.0, False, "Combate", "a cabeçada: baixa a cúpula, empurra com as duas pernas, bate e recua"),
    "flank_butt": (flank_butt, 1.0, False, "Só dele", "a pancada de lado: gira a cúpula no flanco do adversário"),
    "dome_clash": (dome_clash, 4.0, False, "Só dele", "dois machos: encaram, recuam, correm, batem cúpula com cúpula, empurram e sacodem a cabeça"),
    "hurt": (hurt, 0.6, False, "Combate", "abaixa a cabeça e torce o corpo; a cauda rígida dá um tranco"),
    "death": (death, 3.0, False, "Combate", "as pernas cedem, senta pesado, a cúpula desce ao chão, rola de lado"),
    "sit": (sit, 6.0, True, "Descanso", "deitado sobre as pernas dobradas, barriga no chão, cabeça erguida"),
    "sleep": (sleep, 9.0, True, "Descanso", "dorme com o queixo no chão e a cúpula para a frente"),
    "wake_sleep": (wake_sleep, 2.8, False, "Descanso", "ergue a cabeça, estica o pescoço, levanta em dois empurrões"),
    "knocked_out": (knocked_out, 4.0, True, "Descanso", "nocauteado, de lado"),
    "wake": (wake, 3.0, False, "Descanso", "acorda do nocaute: rola, a cabeça pesada balança, sacode a cúpula, levanta"),
    "beg": (beg, 1.6, True, "Domado", "pede comida: focinho para o dono, fungadas curtas"),
    "tame": (tame, 2.6, False, "Domado", "aceita o dono: abaixa a cabeça com a cúpula virada de lado e esfrega nele"),
    "hop_play": (hop_play, 1.6, False, "Só dele", "filhote brincando: agacha, pula de pernas duras com uma torção, pousa"),
}

# 06/11/2026: the fluid set and the duel (pachyflow.py, docs/estudos/10_LUTA_E_FLUIDEZ_POR_ESPECIE.md): the same names
# and lengths, the fluid versions bound in their place, the new ones after
import pachyflow as FLOW  # noqa: E402
ANIMS_BEFORE_FLOW = ANIMS
ANIMS = FLOW.rebind(ANIMS)
