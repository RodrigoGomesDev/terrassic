"""Pteranodon v3, the rest of the animation set (Rodrigo 30/10: "não esqueça das animações diferentes"): every one
its own, from what a big fishing pterosaur does: plunge and skim for fish, float and take off from the water, toss
and swallow a fish, preen the membrane, call, show the crest, bound, jab, beg, sun the wings, shake off water,
bank in a turn, sit, sleep with the beak laid along the back, knockout on the ground and a limp spiral when knocked
out in the air, wake, death."""
import math
import numpy as np
import pteranim as A
from pteranim import S, SIDES, mir, stance, fly_pose, glide_pose, flight_body, lerp_pose, lowest, FLAP_T
from anim2 import add, smooth, ease_out, ease_in, back_out, Track

WING = ("arm", "forearm", "hand", "finger1", "finger2", "fingers")
MEMS = ("arm", "forearm", "hand", "finger1", "finger2")

def copy(p):
    return {k: (list(v[0]), list(v[1]), *(v[2:] if len(v) > 2 else ())) for k, v in p.items()}

def mix(a, b, u, bones):
    """a with the listed bones blended toward b"""
    out = copy(a); l = lerp_pose({k: a[k] for k in bones if k in a}, {k: b[k] for k in bones if k in b}, u)
    out.update(l); return out

def wing_bones(s):
    return [f"{b}_{s}" for b in WING] + [f"mem_{b}_{s}" for b in MEMS]

def on_ground(p, clearance=0.0):
    """lift or drop the whole animal so its lowest point rests on y = 0 (lying, sitting, floating poses)"""
    lo = lowest(S, p); add(p, "root", pos=(0, clearance - lo, 0)); return p

_ST = {}
def base(pitch=A.STANCE_PITCH, lift=0.0):
    """the ground stance, cached (the IK is slow)"""
    key = (round(pitch, 2), round(lift, 2))
    if key not in _ST: _ST[key] = stance(None, pitch=pitch, lift=lift)
    return copy(_ST[key])

def head(p, n1=(0, 0, 0), n2=(0, 0, 0), sk=(0, 0, 0), jaw=0.0):
    add(p, "neck1", rot=n1); add(p, "neck2", rot=n2); add(p, "skull", rot=sk)
    if jaw: add(p, "jaw", rot=(-jaw, 0, 0))
    return p

def breath(t, per=2.4, amp=0.3):
    return amp * math.sin(2 * math.pi * t / per)

# ------------------------------------------------------------------ on the ground
SIT_T = 4.0
def sit_pose(t):
    """resting on the belly, wings tucked tight, a slow breath"""
    p = base(pitch=10, lift=-12.0)
    for s_, sx in SIDES:
        add(p, f"mem_forearm_{s_}", scale=(1, 1, 0.6)); add(p, f"mem_hand_{s_}", scale=(1, 1, 0.7))
    b = breath(t, 4.0)
    head(p, n1=(14 - b * 3, 0, 0), n2=(6, 0, 0), sk=(-6, 0, 0))
    add(p, "body", pos=(0, b, 0))
    return on_ground(p)

SLEEP_T = 6.0
_SLEEP = {}
def sleep_head():
    """neck1, neck2 and skull angles that swing the head round and lay the beak back along the left flank"""
    if "q" not in _SLEEP:
        p = base(pitch=12, lift=-9.0)
        bones = ["neck1", "neck2", "skull"]
        for b, r in (("neck1", (-10, 80, 0)), ("neck2", (0, 50, 0)), ("skull", (0, 40, 0))):
            e = p.get(b, ([0, 0, 0], [0, 0, 0])); p[b] = ([e[0][i] + r[i] for i in range(3)], list(e[1]))
        params = [(b, k) for b in bones for k in (0, 1, 2)]
        want = A.unit((0.28, -0.12, 0.95))               # skull forward (-z local) pointing back and a little down
        def res(q):
            fwd = A.bdir(S, q, "skull", (0, 0, -1))
            hp = A.world(S, q, "skull")
            body = A.world(S, q, "body")
            r = list(4.0 * (fwd - want))
            r += [0.3 * (hp[0] - 9.0), 0.3 * (hp[1] - (body[1] + 6.0)), 0.15 * (hp[2] - (body[2] - 12.0))]
            r += [0.02 * q[b][0][k] for b, k in params]   # keep the bends small
            return np.array(r)
        A.solve(S, p, params, res, iters=40)
        _SLEEP["q"] = {b: list(p[b][0]) for b in bones}
    return _SLEEP["q"]

def sleep_pose(t):
    """settled low, the neck swung round and the long beak laid back along the flank, slow deep breaths"""
    p = base(pitch=12, lift=-9.0)
    for b, r in sleep_head().items():
        p[b] = (list(r), list(p.get(b, ([0, 0, 0], [0, 0, 0]))[1]))
    b = breath(t, 6.0, 0.5)
    add(p, "body", pos=(0, b, 0)); add(p, "neck1", rot=(-b * 2, 0, 0))
    return on_ground(p)

def knocked_out_pose(t=0.0):
    """sprawled flat on its belly: wings crumpled open on the ground (the wing finger swept back), neck stretched out
    on the ground, the head fallen on its side with the beak ajar, legs splayed back"""
    gl = glide_pose(0.0)
    p = {k: v for k, v in copy(gl).items() if not k.startswith(("thigh", "shin", "foot", "neck", "skull", "jaw", "body"))}
    add(p, "body", rot=(-3, 0, 5), pos=(0, 6, 0))
    for s_, sx in SIDES:
        add(p, f"arm_{s_}", rot=mir((0, -10, -9), sx)); add(p, f"forearm_{s_}", rot=mir((0, 25, -2), sx))
        add(p, f"hand_{s_}", rot=mir((0, -30, 0), sx)); add(p, f"finger1_{s_}", rot=mir((0, 85, 0), sx))
        add(p, f"finger2_{s_}", rot=mir((0, -8, 0), sx))
        for b, k in (("hand", 0.6), ("finger1", 0.45), ("finger2", 0.5)):
            add(p, f"mem_{b}_{s_}", scale=(1, 1, k))
        add(p, f"thigh_{s_}", rot=(-75, 0, 16 * sx)); add(p, f"shin_{s_}", rot=(-8, 0, 0)); add(p, f"foot_{s_}", rot=(35, 0, 0))
    br = math.sin(2 * math.pi * t / 3.0)
    head(p, n1=(-34, -10, 0), n2=(-8, -8, 0), sk=(4, 0, 70), jaw=6 + 1.5 * br)
    add(p, "body", pos=(0, 0.3 * br, 0))
    return on_ground(p)

WAKE_T = 2.8
def _wings_from(a, b, u):
    return mix(a, b, u, wing_bones("l") + wing_bones("r"))

def _lift_wings(p, u, amt=50):
    """while the wings swing between crumpled-open and folded, carry them up over the back, not through the ground"""
    for s_, sx in SIDES:
        add(p, f"arm_{s_}", rot=mir((0, 0, amt * math.sin(math.pi * u)), sx))
    return p

def _ko_folded():
    """the knockout pose with the wings already gathered in (the in-between of waking and of dying)"""
    ko = knocked_out_pose(0.0); sit = sit_pose(0.0)
    return on_ground(_wings_from(ko, sit, 1.0))

def wake_pose(t):
    """from the knockout: lifts the head, gathers the wings in, rolls up onto the belly, stands, shakes the head"""
    ko = knocked_out_pose(0.0)
    if t < 0.6:
        p = copy(ko); head(p, n1=(20 * smooth(t / 0.6), 10 * smooth(t / 0.6), 0), sk=(0, 0, -40 * smooth(t / 0.6)))
        return p
    kf = _ko_folded(); head(kf, n1=(20, 10, 0), sk=(0, 0, -40))
    if t < 1.3:
        p = copy(ko); head(p, n1=(20, 10, 0), sk=(0, 0, -40))
        u = smooth((t - 0.6) / 0.7)
        return on_ground(_lift_wings(lerp_pose(p, kf, u), u))
    sit = sit_pose(0.0)
    if t < 1.8:
        return on_ground(lerp_pose(kf, sit, smooth((t - 1.3) / 0.5)))
    st = base()
    if t < 2.4:
        return on_ground(lerp_pose(sit, st, ease_out((t - 1.8) / 0.6)))
    p = base(); u = (t - 2.4) / 0.4
    head(p, sk=(0, 14 * math.sin(u * 3 * math.pi) * (1 - u), 8 * math.sin(u * 3 * math.pi) * (1 - u)))
    return p

DEATH_T = 2.6
def death_pose(t):
    """a stagger, the legs give, it slumps onto the belly, then the wings flop open and it goes still"""
    st = base()
    if t < 0.5:
        p = copy(st); u = smooth(t / 0.5)
        head(p, n1=(-14 * u, 0, 0), sk=(-10 * u, 0, 0), jaw=10 * u)
        return p
    sit = sit_pose(0.0); head(sit, n1=(-14, 0, 0), sk=(-10, 0, 0), jaw=10)
    if t < 1.1:
        st2 = copy(st); head(st2, n1=(-14, 0, 0), sk=(-10, 0, 0), jaw=10)
        return on_ground(lerp_pose(st2, sit, ease_in((t - 0.5) / 0.6)))
    kf = _ko_folded()
    if t < 1.5:
        return on_ground(lerp_pose(sit, kf, smooth((t - 1.1) / 0.4)))
    ko = knocked_out_pose(0.0); head(ko, jaw=-2)
    if t < 2.0:
        u = ease_out((t - 1.5) / 0.5)
        return on_ground(_lift_wings(lerp_pose(kf, ko, u), u, 35))
    return ko

EAT_T = 1.6
def eat_pose(t):
    """a fish: grab it low, toss the head up, open, gulp it down (the throat pulses)"""
    p = base()
    dip = Track([(0, 0), (0.25, 0.55), (0.45, 0.55), (0.75, -1.2), (1.2, -1.2), (1.6, 0)])(t)
    jaw = Track([(0, 0), (0.2, 14), (0.35, 2), (0.8, 2), (0.9, 22, ease_out), (1.05, 4), (1.2, 18), (1.35, 0)])(t)
    head(p, n1=(-14 * dip, 0, 0), n2=(-6 * dip, 0, 0), sk=(-18 * dip, 0, 0), jaw=float(jaw))
    gul = math.exp(-((t - 1.15) / 0.08) ** 2) + math.exp(-((t - 1.4) / 0.08) ** 2)
    add(p, "jaw", scale=(1 + 0.25 * gul, 1 + 0.4 * gul, 1))
    return p

PREEN_T = 4.0
def preen_pose(t):
    """turns round and runs the beak along the lifted wing, nibbling the membrane"""
    p = base()
    u = Track([(0, 0), (0.6, 1), (3.4, 1), (4.0, 0)])(t)
    slide = math.sin(2 * math.pi * (t - 0.6) / 1.4) if 0.6 < t < 3.4 else 0.0
    nib = 6 * max(0.0, math.sin(2 * math.pi * t / 0.35)) * (1 if 0.6 < t < 3.4 else 0)
    head(p, n1=(30 * u, -70 * u - 8 * slide * u, 0), n2=(6 * u, -40 * u, 0), sk=(6 * u, -20 * u, 20 * u), jaw=nib)
    add(p, "arm_l", rot=(0, -10 * u, 18 * u)); add(p, "forearm_l", rot=(0, 0, 8 * u))
    return p

CALL_T = 2.2
def call_pose(t):
    """head up, beak wide, two hoarse calls with the throat pumping"""
    p = base()
    u = Track([(0, 0), (0.4, 1), (1.9, 1), (2.2, 0)])(t)
    c = max(0.0, math.sin(2 * math.pi * (t - 0.4) / 0.75)) if 0.4 < t < 1.9 else 0.0
    head(p, n1=(28 * u, 0, 0), n2=(8 * u, 0, 0), sk=(26 * u + 6 * c, 0, 0), jaw=4 * u + 26 * c)
    add(p, "jaw", scale=(1 + 0.2 * c, 1 + 0.3 * c, 1))
    return p

DISPLAY_T = 3.4
def display_pose(t):
    """the crest show: neck high, the head swung side to side broadside on, wings half raised and trembling"""
    p = base()
    u = Track([(0, 0), (0.5, 1), (2.9, 1), (3.4, 0)])(t)
    sw = math.sin(2 * math.pi * (t - 0.5) / 1.2) if 0.5 < t < 2.9 else 0.0
    head(p, n1=(30 * u, 12 * sw * u, 0), n2=(6 * u, 18 * sw * u, 0), sk=(4 * u, 22 * sw * u, -16 * sw * u), jaw=3 * u)
    tr = 3 * math.sin(2 * math.pi * t / 0.18) * u
    for s, sx in SIDES:
        add(p, f"arm_{s}", rot=mir((0, -8 * u, 30 * u + tr), sx)); add(p, f"forearm_{s}", rot=mir((0, 0, 10 * u), sx))
    return p

ATTACK_T = 0.9
def attack_pose(t):
    """a lunge: rear back, then a long jab with the beak and a snap"""
    p = base()
    k = Track([(0, 0), (0.25, -1, ease_out), (0.42, 1.2, ease_in), (0.55, 1.2), (0.9, 0)])(t)
    jaw = Track([(0, 0), (0.25, 18), (0.45, 22), (0.5, 0, ease_in), (0.9, 0)])(t)
    head(p, n1=(-22 * k, 0, 0), n2=(-10 * k, 0, 0), sk=(14 * max(0, float(k)), 0, 0), jaw=float(jaw))
    return p

BEG_T = 1.2
def beg_pose(t):
    """crouched, beak up and open, wings fluttering half out (a youngster, or a tame one asking for fish)"""
    p = base(lift=-3.0)
    f = math.sin(2 * math.pi * t / 0.3)
    head(p, n1=(26, 4 * math.sin(2 * math.pi * t / 1.2), 0), n2=(8, 0, 0), sk=(30, 0, 0), jaw=18 + 6 * math.sin(2 * math.pi * t / 0.6))
    for s, sx in SIDES:
        add(p, f"arm_{s}", rot=mir((0, -10, 38 + 14 * f), sx)); add(p, f"forearm_{s}", rot=mir((0, 0, 10 + 6 * f), sx))
    return p

SUN_T = 5.0
def sun_pose(t):
    """sunning: the wings opened out and held up to dry, a slow sway, head turned to the light"""
    st = base(); gl = glide_pose(0.0)
    u = Track([(0, 0), (1.0, 1), (4.0, 1), (5.0, 0)])(t)
    p = copy(st)
    for s, sx in SIDES:
        p = mix(p, gl, 0.6 * u, [f"{b}_{s}" for b in ("finger1", "finger2")] + [f"mem_{b}_{s}" for b in MEMS])
        add(p, f"arm_{s}", rot=mir((0, -10 * u, 40 * u + 3 * math.sin(2 * math.pi * t / 2.5) * u), sx))
        add(p, f"forearm_{s}", rot=mir((0, 0, 20 * u), sx)); add(p, f"hand_{s}", rot=mir((0, 30 * u, 0), sx))
        add(p, f"mem_forearm_{s}", scale=(1, 1, 1 - 0.3 * u))
    head(p, n1=(12 * u, 20 * u, 0), sk=(10 * u, 10 * u, 0))
    return p

SHAKE_T = 1.2
def shake_pose(t):
    """shakes off the water: a fast twist from the head down the body, wings rattled"""
    p = base()
    e = math.sin(math.pi * min(1, t / SHAKE_T))
    w = math.sin(2 * math.pi * t / 0.16) * e
    head(p, n1=(0, 10 * w, 0), n2=(0, 14 * w, 0), sk=(0, 10 * w, 24 * w))
    for s, sx in SIDES:
        add(p, f"arm_{s}", rot=mir((0, 0, 14 * e + 5 * w), sx))
    return p

RUN_T = 0.7
def run_pose(t):
    """a bounding run: both hands push off together, then both feet, the body rocking"""
    ph = (t / RUN_T) % 1.0; w = 2 * math.pi * ph
    p = {}
    add(p, "body", rot=(A.STANCE_PITCH + 6 * math.sin(w), 0, 0), pos=(0, A.BODY_Y + 2.2 * max(0, math.sin(w)), -2))
    head(p, n1=(-36 - 5 * math.sin(w - 0.6), 0, 0), n2=(12, 0, 0), sk=(-10 + 4 * math.sin(w - 1.0), 0, 0))
    def step(u, L):
        if u < 0.5: return L / 2 - L * (u / 0.5), 0.0
        sw = (u - 0.5) / 0.5
        return -L / 2 + L * smooth(sw), 5.0 * math.sin(math.pi * sw)
    for s, sx in SIDES:
        dz, lift = step(ph, 10.0)
        add(p, f"fingers_{s}", rot=(54 - 30 * min(1.0, lift / 2.0), 0, 0))
        A.hand_down(p, s, sx, (A.HAND_X * sx, A.HAND_Y + lift, A.HAND_Z - 1 - dz), hum_dir=A.HUM, fore_dir=A.FORE)
        A.fold_wing(p, s, sx)
        dz, lift = step((ph + 0.5) % 1.0, 9.0)
        A.foot_down(p, s, sx, (6 * sx, A.FOOT_Y + lift, 15 - dz))
    return p

# ------------------------------------------------------------------ in the air
BANK_T = 3.0
def bank_pose(t, side=1):
    """a gliding turn: rolled into the turn, the inner wing lowered and the outer raised, head into the turn"""
    p = glide_pose(t * GLIDE_SCALE)
    add(p, "body", rot=(0, 6 * side, -24 * side))
    head(p, n1=(0, 14 * side, 0), sk=(0, 10 * side, 16 * side))
    for s, sx in SIDES:
        inner = (sx == side)
        add(p, f"arm_{s}", rot=mir((0, 0, -6 if inner else 6), sx)); add(p, f"hand_{s}", rot=mir((0, 4 if inner else -2, 0), sx))
    return p
GLIDE_SCALE = 4.0 / 3.0
def bank_left(t): return bank_pose(t, 1)
def bank_right(t): return bank_pose(t, -1)

DIVE_T = 1.4
def dive_pose(t):
    """the plunge: from a glide it folds the wings half back and drops nose first at the water"""
    gl = glide_pose(0.0)
    u = smooth(min(1, t / 0.6))
    p = copy(gl)
    add(p, "body", rot=(-62 * u, 0, 0))
    head(p, n1=(10 * u, 0, 0), sk=(-6 * u, 0, 0))
    for s, sx in SIDES:
        add(p, f"arm_{s}", rot=mir((0, 52 * u, 18 * u), sx)); add(p, f"forearm_{s}", rot=mir((0, -60 * u, 0), sx))
        add(p, f"hand_{s}", rot=mir((0, 40 * u, 0), sx)); add(p, f"finger1_{s}", rot=mir((0, 12 * u, -6 * u), sx))
        for b, k in (("arm", 0.7), ("forearm", 0.55), ("hand", 0.6), ("finger1", 0.75)):
            add(p, f"mem_{b}_{s}", scale=(1, 1, 1 - (1 - k) * u))
    jit = 0.6 * math.sin(2 * math.pi * t / 0.12) * u
    add(p, "body", rot=(0, 0, jit))
    return p

SCOOP_T = 1.8
def scoop_pose(t):
    """skimming low: wings held up in a V clear of the water, neck down, the lower beak trailing, a snap shut"""
    p = glide_pose(0.0)
    u = Track([(0, 0), (0.4, 1), (1.4, 1), (1.8, 0)])(t)
    jaw = Track([(0, 0), (0.4, 24), (1.05, 24), (1.15, 0, ease_in), (1.8, 0)])(t)
    head(p, n1=(-26 * u, 0, 0), n2=(-10 * u, 0, 0), sk=(-6 * u, 0, 0), jaw=float(jaw))
    for s, sx in SIDES:
        add(p, f"arm_{s}", rot=mir((0, 0, 22 * u + 2 * math.sin(2 * math.pi * t / 0.5)), sx)); add(p, f"finger1_{s}", rot=mir((0, 0, -10 * u), sx))
    add(p, "body", rot=(8 * u, 0, 0))
    return p

def knocked_air_pose(t):
    """knocked out in the air: limp, nose down, turning in a slow spiral as it falls, wings trailing up"""
    gl = glide_pose(0.0)
    p = copy(gl)
    a = 360.0 * (t / 1.6)
    add(p, "body", rot=(-48, a, 0))
    head(p, n1=(30, 0, 10), n2=(20, 0, 0), sk=(20, 0, 0), jaw=10)
    for s, sx in SIDES:
        add(p, f"arm_{s}", rot=mir((0, 18, 38 + 4 * math.sin(2 * math.pi * t / 0.4)), sx)); add(p, f"forearm_{s}", rot=mir((0, -30, 10), sx))
        add(p, f"hand_{s}", rot=mir((0, 24, 6), sx))
        add(p, f"thigh_{s}", rot=(30, 0, 0))
    return p
KNOCKED_AIR_T = 1.6

# ------------------------------------------------------------------ on the water
def float_base():
    p = base(pitch=8, lift=-6.0)
    for s, sx in SIDES:
        for b in ("thigh", "shin", "foot"):
            p.pop(f"{b}_{s}", None)
    return p

SWIM_T = 2.0
WATERLINE = 6.0
def swim_pose(t):
    """floating like a gull: sits high on the water, wings folded, the feet paddling under, the head bobbing"""
    p = float_base()
    w = 2 * math.pi * t / SWIM_T
    head(p, n1=(22 + 3 * math.sin(w), 0, 0), sk=(4 - 2 * math.sin(w - 0.8), 0, 0))
    add(p, "body", rot=(1.5 * math.sin(w), 0, 2 * math.sin(w / 2)), pos=(0, 0.4 * math.sin(w), 0))
    for s, sx, ph in (("l", 1, 0.0), ("r", -1, math.pi)):
        add(p, f"thigh_{s}", rot=(-40 + 18 * math.sin(w + ph), 0, 0)); add(p, f"shin_{s}", rot=(20 * math.cos(w + ph), 0, 0))
        add(p, f"foot_{s}", rot=(30 + 20 * math.sin(w + ph), 0, 0))
    lo = lowest(S, {k: v for k, v in p.items()})
    add(p, "root", pos=(0, -WATERLINE - lo, 0))   # about a third of the body under the surface (y = 0 is the water)
    return p

WATER_TAKEOFF_T = 1.8
def water_takeoff_pose(t):
    """from the water: wings swing out, hard strokes beating the surface, then it lifts away"""
    sw = swim_pose(0.0)
    opened = mix(sw, glide_pose(0.0), 1.0, wing_bones("l") + wing_bones("r"))
    _lift_wings(opened, 0.5, 30)
    if t < 0.4:
        return lerp_pose(sw, opened, smooth(t / 0.4))
    u = smooth((t - 0.4) / 1.4)
    p = lerp_pose(opened, fly_pose((t - 0.4) * 1.0), min(1.0, (t - 0.4) / 0.3))
    # keep the body where it floated, then climb away
    y0 = A.world(S, opened, "body")[1]; y1 = A.world(S, p, "body")[1]
    add(p, "root", pos=(0, (y0 - y1) + 24 * smooth((t - 0.4) / 0.3) + 20 * u, 0))
    return p

ANIMS = {
    # name: (fn, length, loop)
    "sit": (sit_pose, SIT_T, True), "sleep": (sleep_pose, SLEEP_T, True),
    "knocked_out": (knocked_out_pose, 3.0, True), "knocked_out_air": (knocked_air_pose, KNOCKED_AIR_T, True),
    "wake": (wake_pose, WAKE_T, False), "death": (death_pose, DEATH_T, False),
    "eat": (eat_pose, EAT_T, False), "preen": (preen_pose, PREEN_T, False), "call": (call_pose, CALL_T, False),
    "display": (display_pose, DISPLAY_T, False), "attack": (attack_pose, ATTACK_T, False), "beg": (beg_pose, BEG_T, True),
    "sun": (sun_pose, SUN_T, False), "shake": (shake_pose, SHAKE_T, False), "run": (run_pose, RUN_T, True),
    "bank_left": (bank_left, BANK_T, True), "bank_right": (bank_right, BANK_T, True),
    "dive": (dive_pose, DIVE_T, False), "scoop": (scoop_pose, SCOOP_T, False),
    "swim": (swim_pose, SWIM_T, True), "water_takeoff": (water_takeoff_pose, WATER_TAKEOFF_T, False),
}
