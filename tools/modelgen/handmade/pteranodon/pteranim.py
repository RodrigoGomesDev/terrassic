"""Pteranodon v2 animations: ground stance on all fours (wing finger folded), walk, flap, glide, takeoff, landing."""
import math
import numpy as np
import geo, proto as P, ptera
from anim2 import *

def model():
    m = ptera.build(saddle=False); P.pack(m, 256); return m.spec()

S = model()
SIDES = (("l", 1), ("r", -1))

def mir(rot, sx):
    return (rot[0], rot[1] * sx, rot[2] * sx)

def bdir(spec, pose, bone, axis=(1, 0, 0)):
    m = geo.bone_mats(spec, pose)[bone]; v = m[:3, :3] @ np.array(axis, float); return v / np.linalg.norm(v)

def solve(spec, pose, params, residual, iters=30, lam=1e-2):
    """params: list of (bone, axis index); least squares on those rotation channels (deg)"""
    th = np.array([pose.get(b, ([0, 0, 0],))[0][k] for b, k in params], float)
    def apply(th):
        q = {k: (list(v[0]), list(v[1]), *(v[2:] if len(v) > 2 else ())) for k, v in pose.items()}
        for (b, k), a in zip(params, th):
            e = q.get(b, ([0, 0, 0], [0, 0, 0])); r = list(e[0]); r[k] = a
            q[b] = (r, list(e[1]), *(e[2:] if len(e) > 2 else ()))
        return q
    for _ in range(iters):
        q = apply(th); r0 = residual(q)
        J = np.zeros((len(r0), len(th)))
        for j in range(len(th)):
            d = np.zeros(len(th)); d[j] = 0.3
            J[:, j] = (residual(apply(th + d)) - r0) / 0.3
        th = th + np.linalg.solve(J.T @ J + lam * np.eye(len(th)), -J.T @ r0)
    q = apply(th); pose.clear(); pose.update(q)
    return float(np.abs(residual(q)).max())

def unit(v):
    v = np.array(v, float); return v / np.linalg.norm(v)

# ------------------------------------------------------------------ ground stance
def place_arm(pose, s, sx, hand_target, hum_dir=(0.45, -0.55, 0.7), fore_dir=(0.25, -0.85, -0.45), meta_dir=(0.05, -1.0, -0.15)):
    """humerus, forearm and metacarpal to the wanted directions, fingers on hand_target (world)"""
    hd = unit((hum_dir[0] * sx, hum_dir[1], hum_dir[2])); fd = unit((fore_dir[0] * sx, fore_dir[1], fore_dir[2])); md = unit((meta_dir[0] * sx, meta_dir[1], meta_dir[2]))
    tgt = np.array(hand_target, float)
    ax = (sx, 0, 0)
    def res(q):
        r = []
        r += list(2.0 * (bdir(S, q, f"arm_{s}", ax) - hd))
        r += list(1.5 * (bdir(S, q, f"forearm_{s}", ax) - fd))
        r += list(1.0 * (bdir(S, q, f"hand_{s}", ax) - md))
        r += list(0.25 * (world(S, q, f"fingers_{s}") - tgt))
        r += [3.0 * max(0.0, 2.6 - world(S, q, f"hand_{s}")[1])]   # the wrist knob never goes into the ground
        return np.array(r)
    params = [(f"arm_{s}", 1), (f"arm_{s}", 2), (f"forearm_{s}", 1), (f"forearm_{s}", 2), (f"hand_{s}", 1), (f"hand_{s}", 2), (f"arm_{s}", 0), (f"hand_{s}", 0)]
    return solve(S, pose, params, res)

def low_on(pose, bones):
    return min(q[:, 1].min() for c, q in geo.cube_points(S, pose) if c["bone"] in bones)

def grounded(place, pose, s, sx, target, rest_y, bones, **kw):
    """place a limb, then nudge its target up or down until its lowest point sits where it should (0 when planted,
    the lift above 0 in a swing): the new model's knuckles, claws and toes reach lower than the bone targets"""
    want = max(0.05, target[1] - rest_y + 0.05)
    tgt = list(target); err = 0.0
    for _ in range(3):
        err = place(pose, s, sx, tuple(tgt), **kw)
        d = want - low_on(pose, bones)
        if abs(d) < 0.15: break
        tgt[1] += d
    return err

def hand_down(pose, s, sx, target, **kw):
    r = grounded(place_arm, pose, s, sx, target, HAND_Y, {f"hand_{s}", f"fingers_{s}", f"finger1_{s}", f"mem_hand_{s}"}, **kw)
    return r

def foot_down(pose, s, sx, target):
    return grounded(place_leg, pose, s, sx, target, FOOT_Y, {f"foot_{s}"})

FOLD_INIT = {}
FOLD_UP = 0.35
def fold_wing(pose, s, sx, amount=1.0):
    """call after the arm is placed"""
    """wing finger folded back up along the forearm, membranes gathered toward their spars"""
    if amount > 0:
        want = unit((0.24 * sx, FOLD_UP, 0.92))
        rest = bdir(S, pose, f"finger1_{s}", (sx, 0, 0))
        tgt = unit(rest * (1 - amount) + want * amount)
        res = lambda q: 3.0 * (bdir(S, q, f"finger1_{s}", (sx, 0, 0)) - tgt)
        # the fold has two solutions far apart; start from the stance one so a walk never flips between them
        best = None
        for init in ([FOLD_INIT[s]] if s in FOLD_INIT else []) + [(0, y * sx, z * sx) for y in (-150, -120, 120, 150) for z in (-40, 0, 40)]:
            q = {k: tuple(v) for k, v in pose.items()}
            e = q.get(f"finger1_{s}", ([0, 0, 0], [0, 0, 0])); q[f"finger1_{s}"] = (list(init), list(e[1]), *(e[2:] if len(e) > 2 else ()))
            err = solve(S, q, [(f"finger1_{s}", 1), (f"finger1_{s}", 2)], res, iters=15)
            if best is None or err < best[0] - 1e-3: best = (err, q)
            if err < 0.02: break
        pose.clear(); pose.update(best[1])
        FOLD_INIT.setdefault(s, list(pose[f"finger1_{s}"][0]))
        add(pose, f"finger2_{s}", rot=mir((0, -6 * amount, 0), sx))
    for b, k in (("arm", 0.6), ("forearm", 0.3), ("hand", 0.2), ("finger1", 0.28), ("finger2", 0.25)):
        f = 1 - (1 - k) * amount
        add(pose, f"mem_{b}_{s}", scale=(1, 1, f))

def place_leg(pose, s, sx, foot_target):
    tgt = np.array(foot_target, float)
    def res(q):
        r = list(1.5 * (world(S, q, f"foot_{s}") - tgt))
        fwd = bdir(S, q, f"foot_{s}", (0, 0, -1))
        r += [3.0 * fwd[1]]                     # sole flat
        r += [3.0 * bdir(S, q, f"foot_{s}", (1, 0, 0))[1]]   # and level across, when the body rolls in the walk
        return np.array(r)
    params = [(f"thigh_{s}", 0), (f"shin_{s}", 0), (f"foot_{s}", 0), (f"thigh_{s}", 2), (f"foot_{s}", 2)]
    return solve(S, pose, params, res)

STANCE_PITCH = 32.0
HAND_Y, FOOT_Y = 3.9, 2.5       # bone targets that put the claws and soles on y = 0
BODY_Y = -1.5                   # body low enough that the knees bend
HAND_X, HAND_Z = 13.0, -13.0
HUM, FORE = (0.35, -0.5, 0.8), (0.12, -0.9, -0.4)
def stance(pose=None, pitch=STANCE_PITCH, lift=0.0):
    pose = {} if pose is None else pose
    add(pose, "body", rot=(pitch, 0, 0), pos=(0, BODY_Y + lift, -2))
    add(pose, "neck1", rot=(-30, 0, 0)); add(pose, "neck2", rot=(14, 0, 0)); add(pose, "skull", rot=(-18, 0, 0))
    for s, sx in SIDES:
        add(pose, f"fingers_{s}", rot=(54, 0, 0))     # the three small claws turned down onto the ground
        hand_down(pose, s, sx, (HAND_X * sx, HAND_Y, HAND_Z), hum_dir=HUM, fore_dir=FORE)
        fold_wing(pose, s, sx)
        foot_down(pose, s, sx, (6 * sx, FOOT_Y, 16))
    return pose

# ------------------------------------------------------------------ flight
def flight_body(pose, bob=0.0, pitch=0.0, roll=0.0):
    """body level in the air, neck stretched forward, legs trailing back under the tail"""
    add(pose, "body", rot=(pitch, 0, roll), pos=(0, 14 + bob, 0))
    add(pose, "neck1", rot=(-40, 0, 0)); add(pose, "neck2", rot=(6, 0, 0)); add(pose, "skull", rot=(14, 0, 0))
    for s, sx in SIDES:
        add(pose, f"thigh_{s}", rot=(-68, 0, 4 * sx)); add(pose, f"shin_{s}", rot=(-14, 0, 0)); add(pose, f"foot_{s}", rot=(25, 0, 0))

FLAP_T = 0.8
def fly_pose(t):
    pose = {}
    w = 2 * math.pi * (t / FLAP_T)
    up = max(0.0, math.sin(w))            # 0..1 in the upstroke half
    flight_body(pose, bob=-2.2 * math.cos(w), pitch=-2.0 * math.sin(w))
    # the head stays level: the neck takes the bob
    add(pose, "neck1", rot=(1.5 * math.sin(w), 0, 0)); add(pose, "skull", rot=(-1.0 * math.sin(w), 0, 0))
    add(pose, "jaw", rot=(-1.0, 0, 0))
    for s, sx in SIDES:
        add(pose, f"arm_{s}", rot=mir((0, -6 * up, 6 + 34 * math.cos(w)), sx))
        add(pose, f"forearm_{s}", rot=mir((0, -14 * up, 8 * math.cos(w - 0.6)), sx))
        add(pose, f"hand_{s}", rot=mir((0, 10 * up, 10 * math.cos(w - 1.0)), sx))
        add(pose, f"finger1_{s}", rot=mir((0, 4 * up, 12 * math.cos(w - 1.4)), sx))
        add(pose, f"finger2_{s}", rot=mir((0, 0, 9 * math.cos(w - 1.8)), sx))
        for b in ("hand", "finger1", "finger2"):
            add(pose, f"mem_{b}_{s}", scale=(1, 1, 1 - 0.15 * up))
        add(pose, f"thigh_{s}", rot=(2 * math.sin(w - 1.0), 0, 0))
    return pose

GLIDE_T = 4.0
def glide_pose(t):
    pose = {}
    w = 2 * math.pi * t / GLIDE_T
    flight_body(pose, bob=0.6 * math.sin(w), pitch=1.0, roll=3.0 * math.sin(w))
    add(pose, "neck1", rot=(0, 6 * math.sin(w - 0.5), 0)); add(pose, "skull", rot=(0, 8 * math.sin(w - 0.9), -3 * math.sin(w)))
    for s, sx in SIDES:
        add(pose, f"arm_{s}", rot=mir((0, 0, 7 - 2.0 * math.sin(w) * sx), sx))
        add(pose, f"forearm_{s}", rot=mir((0, 0, -3), sx))
        add(pose, f"hand_{s}", rot=mir((0, 2, 1.5 * math.sin(w * 2)), sx))
        add(pose, f"finger1_{s}", rot=mir((0, 0, 4 + 1.5 * math.sin(w * 2 - 0.5)), sx))
        add(pose, f"finger2_{s}", rot=mir((0, 0, 5), sx))
    return pose

# ------------------------------------------------------------------ on the ground
IDLE_T = 6.0
LOOK = Track([(0, (0, 0)), (0.8, (0, 0)), (1.1, (6, 22), ease_out), (2.6, (6, 22)), (2.9, (-4, -18), ease_out), (4.2, (-4, -18)), (4.6, (0, 0))])
def idle_pose(t):
    pose = {}
    br = math.sin(2 * math.pi * t / 2.0)
    stance(pose, lift=0.3 * br)
    lp, ly = LOOK(t)
    add(pose, "neck1", rot=(lp * 0.3 - 0.6 * br, ly * 0.4, 0)); add(pose, "neck2", rot=(0, ly * 0.3, 0)); add(pose, "skull", rot=(lp * 0.5, ly * 0.3, -ly * 0.15))
    clack = math.exp(-((t - 5.2) / 0.06) ** 2) + math.exp(-((t - 5.45) / 0.06) ** 2)
    add(pose, "jaw", rot=(-8 * clack, 0, 0))
    return pose

WALK_T = 1.4
def walk_pose(t):
    """diagonal gait on all fours: left hand with right foot, a short stride, the body sways"""
    ph = (t / WALK_T) % 1.0
    w = 2 * math.pi * ph
    pose = {}
    add(pose, "body", rot=(STANCE_PITCH + 1.5 * math.sin(2 * w), 2.5 * math.sin(w), 2.0 * math.sin(w)), pos=(0, BODY_Y + 0.8 * math.cos(2 * w), -2))
    add(pose, "neck1", rot=(-30 - 1.5 * math.sin(2 * w - 0.5), -2.0 * math.sin(w - 0.4), 0)); add(pose, "neck2", rot=(14, 0, 0))
    add(pose, "skull", rot=(-18 + 1.2 * math.sin(2 * w - 1.2), -1.5 * math.sin(w - 0.9), 0))
    for s, sx, oh, of in (("l", 1, 0.0, 0.5), ("r", -1, 0.5, 0.0)):
        uh = (ph + oh) % 1.0; uf = (ph + of) % 1.0
        def step(u, STRIDE=9.0):
            if u < 0.6:
                return STRIDE / 2 - STRIDE * (u / 0.6), 0.0
            sw = (u - 0.6) / 0.4
            return -STRIDE / 2 + STRIDE * smooth(sw), 4.0 * math.sin(math.pi * sw)
        dz, lift = step(uh, 7.0)
        add(pose, f"fingers_{s}", rot=(54 - 30 * min(1.0, lift / 2.0), 0, 0))
        hand_down(pose, s, sx, (HAND_X * sx, HAND_Y + lift, HAND_Z - 1 - dz), hum_dir=HUM, fore_dir=FORE)
        fold_wing(pose, s, sx)
        dz, lift = step(uf)
        foot_down(pose, s, sx, (6 * sx, FOOT_Y + lift, 15 - dz))
    return pose

# ------------------------------------------------------------------ takeoff and landing
def lerp_pose(a, b, u):
    out = {}
    for k in set(a) | set(b):
        ea = a.get(k, ([0, 0, 0], [0, 0, 0], None)); eb = b.get(k, ([0, 0, 0], [0, 0, 0], None))
        sa = ea[2] if len(ea) > 2 and ea[2] is not None else (1, 1, 1); sb = eb[2] if len(eb) > 2 and eb[2] is not None else (1, 1, 1)
        out[k] = ([ea[0][i] + (eb[0][i] - ea[0][i]) * u for i in range(3)], [ea[1][i] + (eb[1][i] - ea[1][i]) * u for i in range(3)],
                  [sa[i] + (sb[i] - sa[i]) * u for i in range(3)])
    return out

def crouch_pose(drop, pitch=STANCE_PITCH):
    p = {}; stance(p, pitch=pitch, lift=-drop); return p

TAKEOFF_T = 1.78
def takeoff_pose(t):
    """the quad launch: crouch, vault off the arms, open the wings, first big downstroke"""
    if t < 0.35:
        return lerp_pose(stance(), crouch_pose(4.0, STANCE_PITCH + 4), smooth(t / 0.35))
    if t < 0.8:
        u = smooth((t - 0.35) / 0.45)
        a, b = crouch_pose(4.0, STANCE_PITCH + 4), launch_pose()
        p = lerp_pose(a, b, u)
        # the folded wing finger stays tucked until the arms have left the ground, then swings out
        late = lerp_pose(a, b, smooth(max(0.0, (u - 0.2) / 0.8)))
        for s, _sx in SIDES:
            for k in (f"finger1_{s}", f"finger2_{s}", f"mem_finger1_{s}", f"mem_finger2_{s}"):
                p[k] = late[k]
        # the hands stay planted while the arms push the body up (the vault), then let go, blending out
        if u < 0.85:
            q = {k: (list(v[0]), list(v[1]), *(v[2:] if len(v) > 2 else ())) for k, v in p.items()}
            for s, sx in SIDES:
                hand_down(q, s, sx, (13 * sx, HAND_Y, -13), hum_dir=(0.3, -0.7, 0.6), fore_dir=(0.1, -0.95, -0.2), meta_dir=(0.05, -1.0, 0.1))
            k = 1.0 - smooth((u - 0.35) / 0.5)
            arm = [f"{b}_{s}" for s, _ in SIDES for b in ("arm", "forearm", "hand")]
            p.update(lerp_pose({b: p[b] for b in arm if b in p}, {b: q[b] for b in arm if b in q}, k))
        return p
    if t < 1.18:
        u = smooth((t - 0.8) / 0.38)
        up = launch_pose(); top = fly_pose(0.0)
        add(top, "body", pos=(0, -4 * (1 - u), 0))
        return lerp_pose(up, top, u)
    p = fly_pose((t - 1.18) * 1.0)
    add(p, "body", pos=(0, 22 * smooth((t - 1.18) / 0.35), 0))   # still climbing off the vault, so the first downstroke clears the ground
    return p

def launch_pose():
    """the instant after the vault: body thrown up and forward, arms straight down behind, wings half open"""
    p = {}
    add(p, "body", rot=(18, 0, 0), pos=(0, 16, -6))
    add(p, "neck1", rot=(-36, 0, 0)); add(p, "neck2", rot=(10, 0, 0)); add(p, "skull", rot=(4, 0, 0))
    for s, sx in SIDES:
        add(p, f"arm_{s}", rot=mir((0, 6, 50), sx)); add(p, f"forearm_{s}", rot=mir((0, -18, 8), sx))
        add(p, f"hand_{s}", rot=mir((0, 22, 4), sx)); add(p, f"finger1_{s}", rot=mir((0, -26, 8), sx))
        for b, k in (("arm", 0.8), ("forearm", 0.7), ("hand", 0.55), ("finger1", 0.5), ("finger2", 0.5)):
            add(p, f"mem_{b}_{s}", scale=(1, 1, k))
        add(p, f"thigh_{s}", rot=(-40, 0, 0)); add(p, f"shin_{s}", rot=(-10, 0, 0)); add(p, f"foot_{s}", rot=(40, 0, 0))
    return p

LAND_T = 1.5
def flare_pose():
    """wings swept forward and cupped, body pitched up, legs reaching down"""
    p = {}
    add(p, "body", rot=(26, 0, 0), pos=(0, 16, 0))
    add(p, "neck1", rot=(-48, 0, 0)); add(p, "neck2", rot=(8, 0, 0)); add(p, "skull", rot=(-4, 0, 0))
    for s, sx in SIDES:
        add(p, f"arm_{s}", rot=mir((0, 22, 18), sx)); add(p, f"forearm_{s}", rot=mir((0, 8, -6), sx))
        add(p, f"hand_{s}", rot=mir((0, 4, -10), sx)); add(p, f"finger1_{s}", rot=mir((0, 0, -12), sx)); add(p, f"finger2_{s}", rot=mir((0, 0, -8), sx))
        add(p, f"thigh_{s}", rot=(-6, 0, 6 * sx)); add(p, f"shin_{s}", rot=(10, 0, 0)); add(p, f"foot_{s}", rot=(-10, 0, 0))
    return p

def land_pose(t):
    if t < 0.5:
        return lerp_pose(glide_pose(0.0), flare_pose(), smooth(t / 0.5))
    if t < 0.8:
        p = flare_pose(); add(p, "body", pos=(0, -6 * smooth((t - 0.5) / 0.3), 0))
        for s, sx in SIDES: add(p, f"arm_{s}", rot=mir((0, 0, 10 * math.sin(math.pi * (t - 0.5) / 0.3)), sx))
        return p
    u = smooth((t - 0.8) / 0.7)
    p = flare_pose(); add(p, "body", pos=(0, -6, 0))
    q = lerp_pose(p, stance(), u)
    lo = lowest(S, q)
    if lo < 0: add(q, "body", pos=(0, -lo, 0))
    return q

if __name__ == "__main__":
    import json, sys
    from view import export, sheet
    m = ptera.build(saddle=False); P.pack(m, 256)
    spec, tex = export(m)
    p = stance()
    print("lowest", lowest(spec, p))
    sheet(spec, tex, [(35, 15), (100, 5), (200, 10), (0, 85)], pose=p, out="stance.png", hidden=("female_display",))
    sheet(spec, tex, [(35, 15), (100, 5), (0, 85), (180, -30)], pose=fly_pose(0.0), out="fly0.png", hidden=("female_display",))
    sheet(spec, tex, [(35, 15), (100, 5), (0, 85), (180, -30)], pose=fly_pose(FLAP_T / 2), out="fly1.png", hidden=("female_display",))
