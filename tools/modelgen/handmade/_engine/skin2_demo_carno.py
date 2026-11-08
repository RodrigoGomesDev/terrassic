import os, sys, json, math
H = __import__("os").path.abspath(__import__("os").path.join(__import__("os").path.dirname(__file__), ".."))
sys.path[:0] = [H + "/carnotaurus", H + "/_engine", H + "/_engine/plans"]
import proto as P, geo, shots, carno, skin2
from PIL import Image
OUT = sys.argv[1]  # usage: python3 -B skin2_demo_carno.py <out dir> (old vs new skin of the Carnotaurus, not used in game)
m = carno.build(saddle_on=False)
P.pack(m, carno.TEX_W)
gp = OUT + "/carno.geo.json"; json.dump(P.geo_json(m), open(gp, "w"))
prof = skin2.Profile(m, {"chest", "keel", "torso", "belly", "hips", "back", "shoulders", "neck1", "neck2", "throat",
                         "tail1", "tail2", "tail3", "tail4", "tail5", "tail_muscle"})
old_sh = carno.shader_for("male")
def new_sh(t):
    n = t.cube["name"]
    if n not in carno.BODY_PARTS:
        return old_sh(t)
    p = carno.pal_for("male")
    z, y = t.P[2], t.P[1]
    if n in carno.LEG or n in ("arm", "forearm", "hand"):
        base = "k3"
        if skin2.scales(t, cell=3.2, seed=5) == "edge": base = skin2.step(base, -1)
        return p[base]
    if n in ("thigh", "knee"):
        h = 0.35 + 0.5 * t.rel[1]
    else:
        h = prof.height(t)
    b = skin2.bands(h, z, (0.20, 0.25, 0.52, 0.80), amp=0.05)
    base = ["b1", "b0", "k4", "k3", "k2"][b]
    if b == 0:
        import skin
        u, v = skin2.surface_uv(t)
        k = skin.scutes(u, v, row=3, width=6)
        return p[{"seam": "b0", "hi": "b2", "base": "b1"}[k]]
    if b >= 2 and h > 0.55 and n not in ("thigh", "knee") and skin2.stripe(z, y, [s[0] for s in carno.SADDLES], 3.5, slant=-0.12) is not None:
        base = "k1"
    if b >= 2:
        base = skin2.step(base, skin2.mottle(t, cell=7, strength=0.2, seed=3))
    if b >= 1 and skin2.scales(t, cell=5.0, seed=9) == "edge":
        base = skin2.step(base, -1)
    return p[base]
for name, sh in (("old", old_sh), ("new", new_sh)):
    tex = P.paint(m, sh, decals=(carno.decals_for("male"),))
    tex.save(f"{OUT}/carno_{name}.png")
    spec = geo.load_geo(gp)
    shots.shot(spec, tex, 90, 0, (1400, 560)).save(f"{OUT}/{name}_side.png")
    shots.shot(spec, tex, 35, 18, (1200, 760)).save(f"{OUT}/{name}_tq.png")
    print(name, skin2.colour_count(tex))
