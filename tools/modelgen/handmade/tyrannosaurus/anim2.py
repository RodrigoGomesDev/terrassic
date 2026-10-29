"""Animation engine of the hand-made rigs: layered poses, planar leg IK with planted feet, easing, GeckoLib export."""
import math, json
import numpy as np
import geo

# ---------------------------------------------------------------- easing / keyframe tracks
def smooth(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
def ease_out(u): u = min(1, max(0, u)); return 1 - (1 - u) ** 3
def ease_in(u): u = min(1, max(0, u)); return u ** 3
def back_out(u, k=1.6):
    """overshoot then settle"""
    u = min(1, max(0, u)) - 1; return 1 + (k + 1) * u ** 3 + k * u ** 2

class Track:
    """keyframes (t, value) with a per-segment easing; value can be a number or a tuple"""
    def __init__(self, keys):
        self.k = [(k[0], np.array(k[1], float), k[2] if len(k) > 2 else smooth) for k in keys]
    def __call__(self, t):
        k = self.k
        if t <= k[0][0]: return k[0][1]
        for (t0, v0, _), (t1, v1, e) in zip(k, k[1:]):
            if t <= t1: return v0 + (v1 - v0) * e((t - t0) / max(1e-9, t1 - t0))
        return k[-1][1]

# ---------------------------------------------------------------- pose helpers
def add(pose, bone, rot=(0, 0, 0), pos=(0, 0, 0)):
    r, p = pose.get(bone, ([0, 0, 0], [0, 0, 0]))
    pose[bone] = ([r[i] + rot[i] for i in range(3)], [p[i] + pos[i] for i in range(3)])

def world(spec, pose, bone, local=None):
    m = geo.bone_mats(spec, pose)[bone]
    b = next(x for x in spec["bones"] if x["name"] == bone)
    p = b["origin"] if local is None else local
    return (m @ np.array([*p, 1.0]))[:3]

def chain_angle(spec, pose, bones):
    """world pitch (deg) of the toes pad: rest is 0 when the pad is flat"""
    mats = geo.bone_mats(spec, pose); m = mats[bones[-1]]
    fwd = m[:3, :3] @ np.array([0, 0, -1.0])
    return math.degrees(math.atan2(fwd[1], -fwd[2]))

# ---------------------------------------------------------------- leg IK (numeric, planar)
def solve_leg(spec, pose, side, target, meta_pitch, toe_pitch, iters=12):
    """move thigh/shin/foot (x rotation) so the ball of the foot (toes origin) reaches `target` (y, z)
    and the metatarsus has world pitch `meta_pitch`; then set the toes so the pad has `toe_pitch`."""
    names = [f"thigh_{side}", f"shin_{side}", f"foot_{side}"]
    th = np.array([pose.get(n, ([0, 0, 0],))[0][0] for n in names], float)
    def res(th):
        q = dict(pose)
        for n, a in zip(names, th):
            r, p = q.get(n, ([0, 0, 0], [0, 0, 0])); q[n] = ([a, r[1], r[2]], p)
        ball = world(spec, q, f"toes_{side}")
        mp = chain_angle(spec, q, [f"foot_{side}"])
        return np.array([ball[1] - target[0], ball[2] - target[1], 0.35 * (mp - meta_pitch)]), q
    lam = 1e-2
    for _ in range(iters):
        r0, _q = res(th)
        J = np.zeros((3, 3))
        for j in range(3):
            d = np.zeros(3); d[j] = 0.25
            J[:, j] = (res(th + d)[0] - r0) / 0.25
        step = np.linalg.solve(J.T @ J + lam * np.eye(3), -J.T @ r0)
        th = th + step
        if np.abs(r0[:2]).max() < 0.02: break
    r0, q = res(th)
    # toes: pad pitch relative to world
    cur = chain_angle(spec, q, [f"toes_{side}"])
    r, p = q.get(f"toes_{side}", ([0, 0, 0], [0, 0, 0])); q[f"toes_{side}"] = ([r[0] + (toe_pitch - cur), r[1], r[2]], p)
    pose.update(q)
    return float(np.abs(r0[:2]).max())

# ---------------------------------------------------------------- sampling / export
def bake(fn, length, fps=20):
    n = int(round(length * fps))
    return [fn(i / fps) for i in range(n + 1)]

def to_geckolib(frames, length, fps=20, loop=True, every=2, lerp="catmullrom"):
    """frames: list of pose dicts (B-space deltas). Export keyframes every `every` frames (catmull-rom in GeckoLib)."""
    bones = sorted({b for f in frames for b in f})
    out = {}
    idx = list(range(0, len(frames), every))
    if idx[-1] != len(frames) - 1: idx.append(len(frames) - 1)
    for b in bones:
        rot, pos = {}, {}
        for i in idx:
            r, p = frames[i].get(b, ([0, 0, 0], [0, 0, 0]))
            t = f"{i / fps:.4g}"
            rot[t] = {"post": [round(-r[0], 3), round(-r[1], 3), round(r[2], 3)], "lerp_mode": lerp}
            pos[t] = {"post": [round(-p[0], 3), round(p[1], 3), round(p[2], 3)], "lerp_mode": lerp}
        d = {}
        if any(any(abs(x) > 1e-3 for x in v["post"]) for v in rot.values()): d["rotation"] = rot
        if any(any(abs(x) > 1e-3 for x in v["post"]) for v in pos.values()): d["position"] = pos
        if d: out[b] = d
    a = {"animation_length": round(length, 4), "bones": out}
    if loop: a["loop"] = True
    return a

def solve_leg2(spec, pose, side, ball, ankle, w_ankle=0.6, toe_pitch=0.0, iters=16):
    """least squares on thigh/shin/foot so the ball reaches `ball` (y, z) and the ankle sits near `ankle` (y, z)"""
    names = [f"thigh_{side}", f"shin_{side}", f"foot_{side}"]
    th = np.array([pose.get(n, ([0, 0, 0],))[0][0] for n in names], float)
    def res(th):
        q = dict(pose)
        for n, a in zip(names, th):
            r, p = q.get(n, ([0, 0, 0], [0, 0, 0])); q[n] = ([a, r[1], r[2]], p)
        b = world(spec, q, f"toes_{side}"); a = world(spec, q, f"foot_{side}")
        return np.array([b[1] - ball[0], b[2] - ball[1], w_ankle * (a[1] - ankle[0]), w_ankle * (a[2] - ankle[1]), 0.02 * th[0], 0.02 * th[1], 0.02 * th[2]]), q
    lam = 1e-2
    for _ in range(iters):
        r0, _q = res(th)
        J = np.zeros((len(r0), 3))
        for j in range(3):
            d = np.zeros(3); d[j] = 0.25; J[:, j] = (res(th + d)[0] - r0) / 0.25
        th = th + np.linalg.solve(J.T @ J + lam * np.eye(3), -J.T @ r0)
    r0, q = res(th)
    cur = chain_angle(spec, q, [f"toes_{side}"])
    r, p = q.get(f"toes_{side}", ([0, 0, 0], [0, 0, 0])); q[f"toes_{side}"] = ([r[0] + (toe_pitch - cur), r[1], r[2]], p)
    pose.update(q)
    return float(np.abs(r0[:2]).max())

def lowest(spec, pose, skip_mats=("teeth", "teeth_lo")):
    return min(q[:, 1].min() for c, q in geo.cube_points(spec, pose) if c.get("mat") not in skip_mats)

def ground_fit(spec, pose):
    """lift or drop the whole animal so its lowest point touches y = 0"""
    lo = lowest(spec, pose); add(pose, "root", pos=(0, -lo, 0)); return pose
