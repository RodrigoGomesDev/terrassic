"""Floating-part check: python3 floating.py <species>  -> cubes that touch no other cube in the rest pose."""
import sys, os, importlib
_here = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [_here, os.path.join(_here, 'species')]
import numpy as np
from pybench import Rig
from buried import cube_mats, hidden_bones
m = importlib.import_module(sys.argv[1]).build(); rig = Rig(m.spec())
cm = [x for x in cube_mats(rig, None) if x[0]["bone"] not in hidden_bones(rig)]
def corners(c, M):
    lo, hi = np.array(c["from"], float), np.array(c["to"], float)
    P = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    # plus face centres and the centre, so thin plates touching only by a face are caught
    P = np.vstack([P, (lo + hi) / 2] + [np.where(np.arange(3) == ax, s, (lo + hi) / 2) for ax in range(3) for s in (lo[ax], hi[ax])])
    return (M @ np.c_[P, np.ones(len(P))].T).T[:, :3]
n = 0
for i, (c, M, _) in enumerate(cm):
    W = corners(c, M)
    touch = False
    for j, (c2, _M, Mi) in enumerate(cm):
        if i == j: continue
        L = (Mi @ np.c_[W, np.ones(len(W))].T).T[:, :3]
        if np.any(np.all((L >= np.array(c2["from"]) - 0.6) & (L <= np.array(c2["to"]) + 0.6), axis=1)):
            touch = True; break
    if not touch:
        n += 1; print("FLOATING", c["bone"], c["name"])
print("floating cubes:", n)
