"""Offline check of the ceratopsians' fluid set (no export, no build report): for each animation of a species, sampled
at 20 fps from the pose functions themselves on the species' rig (geo.cube_points, as rexanims.S):
  low   lowest point of the model (px; must be >= -0.3 except swim)
  high  the highest of the per-frame lowest points (a standing pose must not float: <= 0.3)
  seam  for loops, the largest bone rotation difference between t = 0 and t = length (deg; < 0.5 closes)
  jump  the largest rotation change of any bone between two frames at 20 fps (deg), and of the leg bones
  jerk  the largest change of that per-frame change on a leg bone (deg/frame/frame): a fast but smooth swing of a
        heavy leg reads 10-15 here; a pop (a leg that jumps and comes back, or snaps into a new solution) reads
        as large as the jump itself, so legs flag above 20. The gallops (a stride of 11-14 frames at 20 fps) are
        exported at 40 fps (FPS_OF); for those the jerk is also given at 40 fps (j40) and that one decides

usage: uv run -q --with numpy --with pillow python3 tools/modelgen/handmade/triceratops/flowcheck.py <species> [names...]
       species: triceratops | styracosaurus | protoceratops
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPECIES = {"triceratops": "triceranims", "styracosaurus": "styracoanims", "protoceratops": "protoanims"}
sp = sys.argv[1]
os.environ.setdefault("CERAFLOW_CHECK", "1")
sys.path[:0] = [os.path.join(HERE, "..", sp), os.path.join(HERE, "..", "_engine")]
A = __import__(SPECIES[sp])
import geo  # noqa: E402

SKIP = {"saddle"}
LEG = ("thigh", "shin", "foot", "toes", "arm", "forearm", "hand")
names = sys.argv[2:] or list(A.ANIMS)
FPS = 20


def low(p):
    return min(q[:, 1].min() for c, q in geo.cube_points(A.S, p) if c["bone"] not in SKIP)


def rot(p, b):
    e = p.get(b)
    return e[0] if e else (0, 0, 0)


FAST = ("run", "charge", "run_biped")


def leg_jerk(frames):
    prev, jerk = {}, 0.0
    for a, b in zip(frames, frames[1:]):
        for bn in b:
            if not bn.startswith(LEG): continue
            dv = [y - x for x, y in zip(rot(a, bn), rot(b, bn))]
            if bn in prev: jerk = max(jerk, max(abs(v - w) for v, w in zip(dv, prev[bn])))
            prev[bn] = dv
    return jerk


bad = []
print(f"{'name':18}{'len':>5} loop {'low':>7}{'high':>7}{'seam':>7}{'jump':>7} {'bone':14}{'legjump':>8}{'jerk':>6}")
for n in names:
    fn, L, loop = A.ANIMS[n][:3]
    N = int(round(L * FPS))
    frames = [fn(i / FPS) for i in range(N + 1)]
    lows = [low(p) for p in frames]
    bones = sorted({b for p in frames for b in p})
    jump, jb, leg, jerk = 0.0, "", 0.0, 0.0
    prev = {}
    for a, b in zip(frames, frames[1:]):
        for bn in bones:
            dv = [y - x for x, y in zip(rot(a, bn), rot(b, bn))]
            d = max(abs(v) for v in dv)
            if d > jump: jump, jb = d, bn
            if bn.startswith(LEG):
                leg = max(leg, d)
                if bn in prev: jerk = max(jerk, max(abs(v - w) for v, w in zip(dv, prev[bn])))
                prev[bn] = dv
    seam = 0.0
    if loop:
        e = fn(L)
        seam = max(max(abs(x - y) for x, y in zip(rot(frames[0], bn), rot(e, bn))) for bn in bones)
    flag = []
    if n != "swim" and min(lows) < -0.3: flag.append("UNDER")
    if loop and seam >= 0.5: flag.append("SEAM")
    j40 = leg_jerk([fn(i / 40) for i in range(int(round(L * 40)) + 1)]) if n in FAST else None
    if (j40 if j40 is not None else jerk) > 20: flag.append("LEGPOP")
    if flag: bad.append((n, flag))
    if j40 is not None: flag.append(f"(j40 {j40:.1f})")
    print(f"{n:18}{L:5.2f} {'yes ' if loop else 'no  '}{min(lows):7.2f}{max(lows):7.2f}{seam:7.2f}{jump:7.1f} {jb:14}{leg:8.1f}{jerk:6.1f} {' '.join(flag)}", flush=True)
print("flags:", bad or "none")
