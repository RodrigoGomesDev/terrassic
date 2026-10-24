"""Buried-part check: python3 buried.py <species> [anim:t ...]
Samples points on the outer faces of every cube (in the rest pose and the given poses) and reports the cubes
whose surface is mostly inside other cubes, i.e. parts that cannot be seen in game (an arm sunk in the chest,
a horn inside the skull). Cubes listed in OK_HIDDEN (teeth and tongue behind closed jaws) are expected."""
import sys, os, importlib
_here = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [_here, os.path.join(_here, 'species')]
import numpy as np
from pybench import Rig, pose_at

OK_HIDDEN = ("fang", "fang_low", "tongue", "fang_l", "fang_r")
HIDE = {"saddle", "female_display"}


def cube_mats(rig, pose):
    mats = rig.bone_matrices(pose)
    out = []
    for c in rig.spec["cubes"]:
        M = mats[c["bone"]]
        if any(c.get("rotation", [0, 0, 0])):
            from pybench import affine
            M = M @ affine(c["rotation"], c["origin"])
        out.append((c, M, np.linalg.inv(M)))
    return out


def hidden_bones(rig):
    hb = set()
    for n in rig.order:
        b = rig.bones[n]
        if n in HIDE or b["parent"] in hb:
            hb.add(n)
    return hb


def check(rig, pose, label, thresh=0.8):
    cm = cube_mats(rig, pose)
    hb = hidden_bones(rig)
    cm = [x for x in cm if x[0]["bone"] not in hb]
    bad = []
    for i, (c, M, _) in enumerate(cm):
        lo, hi = np.array(c["from"], float), np.array(c["to"], float)
        pts = []
        for ax in range(3):
            for side in (lo[ax], hi[ax]):
                a, b = [k for k in range(3) if k != ax]
                for u in np.linspace(0.1, 0.9, 4):
                    for v in np.linspace(0.1, 0.9, 4):
                        p = np.empty(3); p[ax] = side; p[a] = lo[a] + u * (hi[a] - lo[a]); p[b] = lo[b] + v * (hi[b] - lo[b])
                        pts.append(p)
        W = (M @ np.c_[np.array(pts), np.ones(len(pts))].T).T[:, :3]
        inside = np.zeros(len(W), bool)
        for j, (c2, _M2, Mi) in enumerate(cm):
            if j == i:
                continue
            L = (Mi @ np.c_[W, np.ones(len(W))].T).T[:, :3]
            l2, h2 = np.array(c2["from"], float) - 0.05, np.array(c2["to"], float) + 0.05
            inside |= np.all((L > l2 + 0.1) & (L < h2 - 0.1), axis=1)
        frac = inside.mean()
        if frac >= thresh and not c["name"].startswith(OK_HIDDEN):
            bad.append((frac, c["bone"], c["name"]))
    for frac, bone, name in sorted(bad, reverse=True):
        print(f"{label:14s} BURIED {frac:4.0%}  {bone:14s} {name}")
    return bad


if __name__ == "__main__":
    name = sys.argv[1]
    m = importlib.import_module(name).build(); spec = m.spec(); rig = Rig(spec)
    n = len(check(rig, None, "rest"))
    for a in sys.argv[2:]:
        an, t = (a.split(":") + ["0.5"])[:2]
        anim = next(x for x in spec["animations"] if x["name"].endswith("." + an))
        n += len(check(rig, pose_at(anim, float(t) * anim["length"]), a))
    print("buried cubes:", n)
