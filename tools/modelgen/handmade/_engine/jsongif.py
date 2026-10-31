"""renders GIFs straight from the exported geo.json + animation.json (what GeckoLib will play), for QA and the page"""
import sys, json, numpy as np
from PIL import Image
import geo
BG = (198, 214, 230)
def load_anims(path):
    return json.load(open(path))["animations"]
def sample(ch, t):
    ks = sorted((float(k), v["post"]) for k, v in ch.items())
    if t <= ks[0][0]: return np.array(ks[0][1], float)
    for (t0, a), (t1, b) in zip(ks, ks[1:]):
        if t <= t1:
            u = (t - t0) / max(1e-9, t1 - t0); return np.array(a, float) * (1 - u) + np.array(b, float) * u
    return np.array(ks[-1][1], float)
def pose_at(an, t):
    p = {}
    for b, d in an["bones"].items():
        r = sample(d["rotation"], t) if "rotation" in d else np.zeros(3)
        q = sample(d["position"], t) if "position" in d else np.zeros(3)
        s = sample(d["scale"], t) if "scale" in d else None
        p[b] = ([-r[0], -r[1], r[2]], [-q[0], q[1], q[2]], list(s) if s is not None else None)
    return p
def lowest(spec, p, hidden):
    return min(q[:, 1].min() for c, q in geo.cube_points(spec, p, hidden))
if __name__ == "__main__":
    geo_path, anim_path, tex_path, outdir = sys.argv[1:5]
    names = sys.argv[5:]
    spec = geo.load_geo(geo_path); tex = Image.open(tex_path)
    A = load_anims(anim_path)
    hid = ("harness",)
    for n in names:
        an = A[f"animation.velociraptor.{n}"]; L = an["animation_length"]
        fps = 20 if L < 1.2 else 10; N = max(2, int(round(L * fps)))
        poses = [pose_at(an, L * i / N) for i in range(N + (0 if an.get("loop") else 1))]
        air = n in ("leap", "display", "pounce")
        yaw, pitch = (35, 18) if air else (65, 10)
        lows = [lowest(spec, p, hid) for p in poses]
        fits = [geo.render(spec, tex, yaw, pitch, (64, 48), pose=p, hidden=hid)[1] for p in poses[::max(1, len(poses) // 6)]]
        fit = (min(f[0] for f in fits), max(f[1] for f in fits), min(f[2] for f in fits), max(f[3] for f in fits))
        ims = [geo.render(spec, tex, yaw, pitch, (420, 300), pose=p, hidden=hid, fit=fit, bg=BG, margin=0.06)[0].convert("RGB") for p in poses]
        ims[0].save(f"{outdir}/{n}.gif", save_all=True, append_images=ims[1:], duration=int(1000 / fps), loop=0)
        print(f"{n:16s} frames {len(poses):3d} lowest {min(lows):6.2f}", flush=True)
