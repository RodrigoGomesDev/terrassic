"""Conferência numérica de uma pose: python3 posecheck.py <especie> anim[:t] ...  -> extensão de cada cubo no mundo; marca o que afunda no chão (y < 0)."""
import sys, importlib
import os; _here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, _here); sys.path.insert(0, os.path.join(_here, 'species'))
import numpy as np
from pybench import Rig, pose_at

m = importlib.import_module(sys.argv[1]).build(); spec = m.spec(); rig = Rig(spec)
for arg in sys.argv[2:]:
    name, _, t = arg.partition(":"); t = float(t) if t else 0.5
    anim = next((a for a in spec["animations"] if a["name"].endswith("." + name)), None)
    pose = pose_at(anim, t)
    print(f"== {name} t={t}")
    ext = {}
    for c, face, corners, uv in rig.cube_faces(pose):
        key = (c["bone"], c.get("name", "?"))
        pts = np.array([w for (_, w) in corners.values()])
        lo, hi = pts.min(0), pts.max(0)
        if key in ext:
            ext[key] = (np.minimum(ext[key][0], lo), np.maximum(ext[key][1], hi))
        else:
            ext[key] = (lo, hi)
    for (bone, cname), (lo, hi) in ext.items():
        flag = "  <<< UNDER GROUND" if lo[1] < -0.5 else ""
        print(f"{bone:16s} {cname:12s} x[{lo[0]:6.1f},{hi[0]:6.1f}] y[{lo[1]:6.1f},{hi[1]:6.1f}] z[{lo[2]:6.1f},{hi[2]:6.1f}]{flag}")
    allo = np.min([e[0] for e in ext.values()], 0); alhi = np.max([e[1] for e in ext.values()], 0)
    print("ALL", allo.round(1), alhi.round(1))
