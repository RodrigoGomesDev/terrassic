"""
Pteranodon v3 (hand-made rig, the T. rex standard). Pteranodon longiceps, ~6.5 m wingspan, toothless beak and a
long backward crest (big and banded on males, short and dull on females).

v3 (29/10, Rodrigo: "muito simplório, tem que ser mais na pegada do T. rex"): built like the T. rex instead of a
stick figure. Heavy flight muscles (barrel chest, big shoulders, a ruff of pycnofibres round the neck base), a thick
neck, a deep skull with brow, cheek and a bare coloured face patch, a beak in three tapering parts, thick wing bones
with knuckles, and the membrane as real 1 px thick panels stepped along the trailing edge (so the wing has an edge
seen from the side and folds as solid panels). Texture drawn by form: fur strokes in three tones, countershading,
speckles on the neck, banded crest, fibres and mottling on the membrane.

Anatomy that drives the rig:
  * the wing is an arm: short stout humerus, long forearm, a very long metacarpal, three small clawed fingers at its
    end, then the enormous fourth finger in two parts (the wing finger);
  * the membrane (brachiopatagium) runs from the wing-finger tip to the thigh, with a small front membrane
    (propatagium) held by the pteroid between shoulder and wrist; it is cut in panels, one bone each, so it folds
    with the arm (on the ground the panels are scaled down along the chord and the folded wing sits up behind the
    shoulder);
  * on the ground it walks on all fours: the three small fingers on the ground, the wing finger folded back up.

Coordinates as in the T. rex: px, x+ = left, z- = forward, y up; rest pose stands on its feet with the wings open.
"""
import math
import zlib
import numpy as np
import proto as P, geo, skin
from proto import hx, h32

PAL = {
    # membrane (male): charcoal brown, a warmer inner panel, darker trailing band
    "w0": hx("161314"), "w1": hx("2b2626"), "w2": hx("3e3532"), "w3": hx("5a4a40"), "w4": hx("7a6450"), "wv": hx("231f1f"),
    "we": hx("8a7a66"),                                                       # pale fringe spots on the trailing edge
    "wu0": hx("5f564d"), "wu1": hx("7a6f63"), "wu2": hx("968a7b"), "wuv": hx("6a6057"),   # underside, countershaded
    # body: charcoal slate above, pale grey-white below, steel-blue flecks on the neck
    "g0": hx("1f2326"), "g1": hx("2d3236"), "g2": hx("3e4449"), "g3": hx("545b60"),
    "p0": hx("8f8d87"), "p1": hx("b2afa7"), "p2": hx("cfcbc1"), "p3": hx("e6e2d8"),
    "b1": hx("4f6f7c"), "b2": hx("7395a0"),
    # bare face skin round the eye
    "r0": hx("5e1a16"), "r1": hx("8e2a20"), "r2": hx("b8442c"),
    # beak (horn)
    "k0": hx("5f533f"), "k1": hx("8f7f5c"), "k2": hx("bcab80"), "k3": hx("ddcfa4"), "kt": hx("2f2923"), "kd": hx("47403a"),
    # crest (male display): banded
    "c0": hx("2a1512"), "c1": hx("6e2216"), "c2": hx("a8381b"), "c3": hx("d2662a"), "c4": hx("e9ad4f"),
    # legs, claws, eye
    "l0": hx("2a2522"), "l1": hx("443c36"), "l2": hx("61574d"), "l3": hx("7c7064"),
    "claw": hx("1a1614"), "clawl": hx("7f7568"),
    "eye": hx("140d0a"), "ring": hx("c8902c"), "ring2": hx("8a5a1c"), "glint": hx("f3ecd2"), "mask": hx("1f2326"),
    "mouth": hx("4a2220"),
}
FEMALE = {
    # warm brown body, buff below, rust flecks, dull face, short olive-and-cream banded crest, tawny membrane
    "g0": hx("2b231d"), "g1": hx("3d3128"), "g2": hx("524236"), "g3": hx("6c5946"),
    "p0": hx("8c7b63"), "p1": hx("ad9a7c"), "p2": hx("c8b694"), "p3": hx("dccbaa"),
    "b1": hx("7a4a2c"), "b2": hx("9c6438"),
    "r0": hx("4a2c1c"), "r1": hx("6e4228"), "r2": hx("8e5a34"),
    "c0": hx("2c281a"), "c1": hx("4c4a2c"), "c2": hx("6e6b40"), "c3": hx("9a9460"), "c4": hx("cfc495"),
    "w0": hx("2a1f18"), "w1": hx("4a3726"), "w2": hx("624a32"), "w3": hx("7a5d3e"), "w4": hx("94744c"), "wv": hx("3a2b1f"),
    "we": hx("c2a77a"),
    "wu0": hx("7a6650"), "wu1": hx("94806a"), "wu2": hx("ad9a82"), "wuv": hx("86735e"),
}

# wing outline (rest pose, left side): leading edge and trailing edge z for a span position x
WING_X0, WING_TIP = 5.0, 109.0
def lead_z(x):
    if 6.0 <= x <= 34.0:                                  # propatagium in front of the arm, shoulder to wrist
        return -6.0 - 4.5 * math.sin(math.pi * (x - 6.0) / 28.0) ** 0.8
    return -6.0 + 1.2 * max(0.0, (x - 70.0) / 39.0) ** 2   # the leading edge sweeps back a little at the tip
def trail_z(x):
    s = min(1.0, max(0.0, (x - WING_X0) / (WING_TIP - WING_X0)))
    chord = 24.0 * (1.0 - s ** 1.7) ** 0.85              # broad at the body, pointed at the tip
    notch = 2.5 * math.exp(-((x - 14.0) / 6.0) ** 2)      # the membrane meets the thigh with a soft notch
    return -6.0 + chord - notch

# membrane panels per wing bone: span breakpoints (integers, so every panel is whole texels)
PANELS = {"arm": [5, 10, 15, 19], "forearm": [19, 25, 31, 37, 42], "hand": [42, 49, 56, 63, 70],
          "finger1": [70, 77, 84, 91], "finger2": [91, 96, 101, 105, 109]}
JOINT_X = {"arm": 6, "forearm": 19, "hand": 42, "finger1": 70, "finger2": 91}

def build(saddle=True):
    m = P.Model("pteranodon")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 26, 0))
    # barrel chest packed with flight muscle, a deep keel, heavy shoulders, a ruff round the neck base
    m.cube(body, (-7, 21, -11), (7, 33, 5), name="torso")
    m.cube(body, (-6, 18, -12), (6, 23, -1), name="keel", mat="belly", rot=(-10, 0, 0), origin=(0, 23, -1))
    m.pair(body, body, (5, 26, -12), (9, 34, -2), name="shoulder", rot=(0, 0, -8), origin=(7, 30, -7))
    m.cube(body, (-5, 26, -15), (5, 35, -9), name="ruff", mat="ruff", rot=(-14, 0, 0), origin=(0, 30, -9))
    m.cube(body, (-5, 20, 4), (5, 30, 12), name="hips")
    m.cube(body, (-3, 27, 11), (3, 31, 15), name="rump", rot=(12, 0, 0), origin=(0, 29, 11))
    m.cube(body, (-1, 26, 14), (1, 28, 20), name="tail", mat="spar")
    # neck, two parts, held up in an S
    n1 = m.bone("neck1", body, (0, 29, -9), (34, 0, 0))
    m.cube(n1, (-3.5, 25.5, -23), (3.5, 32.5, -8), name="neck1")
    m.cube(n1, (-2.5, 24, -21), (2.5, 27, -10), name="throat", mat="belly")
    n2 = m.bone("neck2", n1, (0, 29, -20), (-8, 0, 0))
    m.cube(n2, (-3, 26, -32), (3, 32, -19), name="neck2")
    head = m.bone("head", n2, (0, 29, -30))
    skull = m.bone("skull", head, (0, 29, -30), (-24, 0, 0))
    m.cube(skull, (-5, 24.5, -45), (5, 34.5, -30), name="cranium")
    m.cube(skull, (-3.5, 27, -32), (3.5, 33, -27), name="occiput")
    m.pair(skull, skull, (3, 32, -43), (5, 34, -36), name="brow", mat="brow", rot=(0, -6, 0), origin=(4, 33, -36))
    m.pair(skull, skull, (3.5, 25, -44), (5, 29, -33), name="cheek")
    m.cube(skull, (-3.5, 25, -61), (3.5, 33, -44), name="beak", mat="beak", rot=(-4, 0, 0), origin=(0, 33, -44))
    m.cube(skull, (-2.5, 26, -76), (2.5, 31, -60), name="beak2", mat="beak", rot=(-7, 0, 0), origin=(0, 31, -60))
    m.cube(skull, (-1.5, 27, -85), (1.5, 30, -75), name="beak3", mat="beak_tip", rot=(-10, 0, 0), origin=(0, 30, -75))
    jaw = m.bone("jaw", skull, (0, 26.5, -40))
    m.cube(jaw, (-3.5, 22, -59), (3.5, 26, -39), name="jaw", mat="beak", rot=(3, 0, 0), origin=(0, 26, -40))
    m.cube(jaw, (-2.5, 22.5, -74), (2.5, 25.5, -58), name="jaw2", mat="beak", rot=(5, 0, 0), origin=(0, 25.5, -58))
    m.cube(jaw, (-1.5, 23, -83), (1.5, 25, -73), name="jaw3", mat="beak_tip", rot=(7, 0, 0), origin=(0, 25, -73))
    m.cube(jaw, (-2.5, 21, -44), (2.5, 23, -34), name="gular", mat="belly")
    # crest: the male's long blade sweeps back and up, the female's is a short stub; built as a chain of plates,
    # each starting where the last one ends
    cm = m.bone("male_display", skull, (0, 33, -38))
    crest(m, cm, "crest_m", (33.0, -40.0), [(15, 10, 3, 12), (13, 8, 2, 16), (11, 5, 2, 20)])
    cf = m.bone("female_display", skull, (0, 33, -38))
    crest(m, cf, "crest_f", (33.0, -40.0), [(12, 7, 2, 12), (8, 4, 2, 16)])
    # wings
    for s, sx in (("l", 1), ("r", -1)):
        arm = m.bone(f"arm_{s}", body, (6 * sx, 31, -6))
        fore = m.bone(f"forearm_{s}", arm, (19 * sx, 31, -6))
        hand = m.bone(f"hand_{s}", fore, (42 * sx, 31, -6))
        m.bone(f"fingers_{s}", hand, (69 * sx, 31, -6))
        f1 = m.bone(f"finger1_{s}", hand, (70 * sx, 31, -6))
        m.bone(f"finger2_{s}", f1, (91 * sx, 31, -5.5))
        for b, piv in JOINT_X.items():
            m.bone(f"mem_{b}_{s}", f"{b}_{s}", (piv * sx, 31, -6))
    m.pair("arm_l", "arm_r", (6, 28, -9), (20, 34, -3), name="humerus", mat="spar")
    m.pair("arm_l", "arm_r", (8, 25, -9), (14, 28, -4), name="crest_dp", mat="spar")
    m.pair("forearm_l", "forearm_r", (19, 29, -8), (43, 33, -4), name="forearm", mat="spar")
    m.pair("forearm_l", "forearm_r", (20, 30, -13), (22, 32, -8), name="pteroid", mat="spar", rot=(0, -20, 0), origin=(21, 31, -8))
    m.pair("hand_l", "hand_r", (41, 29, -8), (45, 33, -4), name="wrist", mat="spar")
    m.pair("hand_l", "hand_r", (44, 29, -8), (70, 32, -5), name="metacarpal", mat="spar")
    m.pair("fingers_l", "fingers_r", (66, 29, -12), (68, 31, -7), name="digit1", mat="claw", rot=(0, 18, 0), origin=(67, 30, -7))
    m.pair("fingers_l", "fingers_r", (68, 29, -12), (70, 31, -7), name="digit2", mat="claw", rot=(0, 6, 0), origin=(69, 30, -7))
    m.pair("fingers_l", "fingers_r", (70, 29, -11), (72, 31, -7), name="digit3", mat="claw", rot=(0, -8, 0), origin=(71, 30, -7))
    m.pair("finger1_l", "finger1_r", (69, 30, -8), (73, 33, -4), name="knuckle", mat="spar")
    m.pair("finger1_l", "finger1_r", (73, 30, -7), (92, 32, -5), name="phalanx1", mat="spar")
    m.pair("finger2_l", "finger2_r", (91, 30, -6.5), (109, 31, -5), name="phalanx2", mat="spar")
    # membrane panels, 1 px thick, the trailing edge stepped panel by panel
    for b, xs in PANELS.items():
        for k, (x0, x1) in enumerate(zip(xs, xs[1:])):
            zl = min(lead_z(x) for x in np.linspace(x0, x1, 12))
            tip = b == "finger2" and k == len(xs) - 2
            zt = trail_z(x0 + (x1 - x0) * (0.25 if tip else 0.5))
            z0 = math.floor(zl); z1 = max(z0 + 2, round(zt))
            m.pair(f"mem_{b}_l", f"mem_{b}_r", (x0, 30.5, z0), (x1, 31.5, z1), name=f"mem_{b}{k}", mat="mem")
    # legs: short, muscular thighs, scaled shins, broad four-toed feet
    for s, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{s}", body, (4 * sx, 24, 8), (-12, 0, 0))
        sh = m.bone(f"shin_{s}", th, (4.5 * sx, 15, 8), (20, 0, 0))
        m.bone(f"foot_{s}", sh, (4.5 * sx, 4, 8), (-8, 0, 0))
    m.pair("thigh_l", "thigh_r", (2, 14, 5), (7, 27, 11), name="thigh")
    m.pair("shin_l", "shin_r", (2.5, 3.5, 6), (6.5, 15.5, 10), name="shin", mat="leg")
    m.pair("foot_l", "foot_r", (2, 1.5, 2), (7, 4.5, 10), name="foot", mat="leg")
    for k, x in enumerate((2, 3.5, 5, 6)):
        m.pair("foot_l", "foot_r", (x, 1.5, -0.5 + (k % 3 == 0) * 1.0), (x + 1, 3, 2), name=f"toe{k + 1}", mat="claw")
    if saddle:
        add_saddle(m, body)
    separate_coplanar(m)
    lo = min(p[:, 1].min() for c, p in geo.cube_points({"bones": m.bones, "cubes": m.cubes}))
    m.shift(-lo)
    return m

# face -> (from/to, axis, outward sign)
FACE_AX = {"east": ("to", 0, 1), "west": ("from", 0, -1), "up": ("to", 1, 1), "down": ("from", 1, -1),
           "south": ("to", 2, 1), "north": ("from", 2, -1)}
EXCLUSIVE = {"male_display", "female_display"}       # never shown together

def _mirror_all(m):
    for c in m.cubes:
        src = c["mirror_of"]
        if src is not None:
            c["from"] = [-src["to"][0], src["from"][1], src["from"][2]]
            c["to"] = [-src["from"][0], src["to"][1], src["to"][2]]

def coplanar_pairs(m):
    """faces of two different cubes lying in the same plane, facing the same way and overlapping (z-fighting)"""
    for c in m.cubes: c["uv"] = {f: (0, 0, 1, 1) for f in c["faces"]}
    quads = []
    for c, f, cs, r in geo.faces({"bones": m.bones, "cubes": m.cubes}):
        pts = np.array([cs[k] for k in ((0, 0), (1, 0), (1, 1), (0, 1))])
        n = np.cross(pts[1] - pts[0], pts[3] - pts[0]); nn = np.linalg.norm(n)
        if nn > 1e-9: quads.append((c, f, pts, n / nn))
    out = []
    for i in range(len(quads)):
        c1, f1, p1, n1 = quads[i]
        for c2, f2, p2, n2 in quads[i + 1:]:
            if c1 is c2 or n1 @ n2 < 0.999 or abs((p2[0] - p1[0]) @ n1) > 0.01: continue
            if c1["bone"] in EXCLUSIVE and c2["bone"] in EXCLUSIVE and c1["bone"] != c2["bone"]: continue
            e1 = p1[1] - p1[0]; e1 = e1 / np.linalg.norm(e1); e2 = np.cross(n1, e1)
            b1 = [(p1 @ e).min() for e in (e1, e2)] + [(p1 @ e).max() for e in (e1, e2)]
            b2 = [(p2 @ e).min() for e in (e1, e2)] + [(p2 @ e).max() for e in (e1, e2)]
            ox = min(b1[2], b2[2]) - max(b1[0], b2[0]); oy = min(b1[3], b2[3]) - max(b1[1], b2[1])
            if ox > 0.05 and oy > 0.05:
                out.append((c1, f1, c2, f2))
    for c in m.cubes: c.pop("uv", None)
    return out

def separate_coplanar(m, eps=0.05, rounds=5):
    """the T. rex rule, 0 coplanar faces: where two faces share a plane, push the smaller cube's face out a hair so
    the detail sits on top (mirrored cubes follow their source)"""
    def area(c, f):
        d = [c["to"][k] - c["from"][k] for k in range(3)]
        ax = FACE_AX[f][1]; return np.prod([d[k] for k in range(3) if k != ax])
    for _ in range(rounds):
        pairs = coplanar_pairs(m)
        if not pairs: return
        done = set()
        for c1, f1, c2, f2 in pairs:
            c, f = (c1, f1) if area(c1, f1) <= area(c2, f2) else (c2, f2)
            if c["mirror_of"] is not None:
                c = c["mirror_of"]; f = {"east": "west", "west": "east"}.get(f, f)
            if (id(c), f) in done: continue
            done.add((id(c), f))
            end, ax, sg = FACE_AX[f]
            c[end][ax] += sg * eps
        _mirror_all(m)

def crest(m, bone, name, start, parts):
    """plates (length, height, thickness, angle up from backwards) laid end to end from `start` (y, z)"""
    y, z = start
    for k, (L, h, t, a) in enumerate(parts):
        r = math.radians(a)
        m.cube(bone, (-t / 2, y - h * 0.45, z), (t / 2, y + h * 0.55, z + L + 1.5), name=f"{name}{k}", mat="crest",
               rot=(-a, 0, 0), origin=(0, y, z))
        y, z = y + L * math.sin(r), z + L * math.cos(r)

def add_saddle(m, body):
    """the flyer's light harness: a pad, a low seat, a tall grab bar in front, straps round the wing roots"""
    sd = m.bone("saddle", body, (0, 34, -2))
    m.cube(sd, (-6, 32.5, -9), (6, 35, 3), name="pad", mat="pad")
    m.cube(sd, (-4, 35, -5), (4, 36, 2), name="seat", mat="leather")
    m.cube(sd, (-3, 36, 1), (3, 38, 3), name="cantle", mat="leather")
    m.cube(sd, (-0.5, 35, -9), (0.5, 41, -7), name="grab", mat="wood")
    m.cube(sd, (-2.5, 40, -9), (2.5, 41, -7), name="grab_bar", mat="wood")
    m.pair(sd, sd, (6.5, 22, -8), (7.5, 34, -6), name="strap", mat="strap")
    m.pair(sd, sd, (6.5, 22, 0), (7.5, 34, 2), name="strap_b", mat="strap")

# ---------------------------------------------------------------- skin
def strokes(t, dark, base, light, seed=0, dense=5):
    """pycnofibre fur: short strokes 2 texels long running back along the body, in three tones (designed, no noise:
    a stroke every few texels, offset row by row, its tone picked per stroke)"""
    u, v = skin.face_uv_coords(t)
    i, j = math.floor(u), math.floor(v)
    if t.face in ("up", "down"):
        i, j = math.floor(t.L[0]), math.floor(t.L[2])
    k = math.floor((j + (i * 3) % 2) / 1)
    stroke = math.floor((j + 2 * (i % 2)) / 2)
    if (i * 7 + stroke * 3) % dense == 0:
        return dark if h32(i, stroke, seed) % 3 else light
    return base

def membrane(t):
    """wing panel: fibres sloping back to the tip, mottling, a lighter inner panel, a dark trailing band with pale
    fringe spots; countershaded below; edges of the panel dark"""
    p = PAL; x = abs(t.L[0]); z = t.L[2]
    f = t.face
    if f not in ("up", "down"):
        return p["w0"] if f != "north" else p["w2"]
    under = f == "down"
    zt = trail_z(x)
    c = t.cube; z1 = c["to"][2]
    d_te = z1 - z                      # distance to this panel's trailing edge
    d_le = z - c["from"][2]
    U = (lambda k: p["wu" + k]) if under else (lambda k: p["w" + k])
    if d_te < 1.0:
        if not under and (math.floor(x) % 5 == 2): return p["we"]
        return U("0")
    if d_le < 1.0: return U("2") if under else p["w3"]
    fib = (x * 0.55 + z * 0.9)
    if (math.floor(fib / 3.0) % 3 == 0) and (fib % 3.0) < 1.0:
        return p["wuv"] if under else p["wv"]
    if under:
        return p["wu1"] if x > 30 else p["wu2"]
    if d_te < 3.0: return p["w1"]
    # mottling: big soft cells, darker toward the tip
    d1, d2, cell = skin.voronoi(math.floor(x) + 0.5, math.floor(z) + 0.5, 6.0, 31)
    dark = h32(cell[0], cell[1], 5) % 100 < 20 + 50 * min(1.0, x / 100.0)
    if x < 30 and d_le < 6: return p["w4"] if not dark else p["w3"]
    if d2 - d1 < 0.8: return p["w1"]
    if dark: return p["w1"]
    light = h32(cell[0], cell[1], 6) % 100 < 45 - 40 * min(1.0, x / 70.0)
    return p["w3"] if light else p["w2"]

def flecks(t):
    """sparse light flecks in pairs, on the neck and the shoulders"""
    u, v = skin.face_uv_coords(t)
    i, j = math.floor(u), math.floor(v)
    g = h32(i // 3, j // 2, 17)
    if g % 7 == 0 and (i % 3) < 2 and j % 2 == 0:
        return PAL["b2"] if g % 2 else PAL["b1"]
    return None

def shader(t):
    c = t.cube; n = c["name"]; f = t.face; v = t.rel[1]; p = PAL; mat = c["mat"]
    if mat == "mem": return membrane(t)
    if mat == "claw": return p["clawl"] if (f in ("north", "up") and t.j == 0) else p["claw"]
    if mat == "leather":
        edge = t.i in (0, t.w - 1) or t.j in (0, t.h - 1)
        return hx("2e1d14") if edge else (hx("b89b6a") if (t.i + t.j) % 4 == 0 and f == "up" else hx("4a2f1f"))
    if mat == "pad":
        # fish-skin pad: slate with lighter scales, dark edge
        if t.j in (0, t.h - 1) or t.i in (0, t.w - 1): return hx("2a2f33")
        return hx("a0a8a8") if (t.i + 2 * t.j) % 5 == 0 else hx("78807f")
    if mat == "wood": return hx("a4824f") if (f == "up" or t.j == 0) else hx("7a5e3e")
    if mat == "strap": return hx("2e1d14") if t.i in (0, t.w - 1) else hx("4a2f1f")
    if mat == "beak" or mat == "beak_tip":
        if mat == "beak_tip": return p["kt"] if f != "up" else p["kd"]
        if f == "down": return p["k1"]
        along = (t.P[2] + 44.0) / -37.0           # 0 at the base of the beak, 1 near the tip
        if f == "up":
            if along < 0.08: return p["kd"]
            return p["k3"] if t.i == t.w // 2 else (p["k1"] if (math.floor(abs(t.L[2])) % 7 == 0) else p["k2"])
        if f in ("east", "west"):
            top = n.startswith("beak") and t.j == 0
            edge = (n.startswith("jaw") and t.j == 0) or (n.startswith("beak") and t.j == t.h - 1)
            if edge: return p["k0"]
            if along < 0.08: return p["kd"]
            if top: return p["k3"]
            # horn grain: long streaks, a darker lateral stripe along the upper beak
            if n.startswith("beak") and t.j == t.h - 3: return p["k1"]
            return p["k1"] if (t.j * 5 + math.floor(abs(t.L[2])) // 5) % 6 == 0 else p["k2"]
        return p["k2"]
    if mat == "crest":
        # banded display blade: dark root, coloured bands broken by dark chevrons, a pale rim on top
        along = min(1.0, max(0.0, (t.P[2] + 40.0) / 52.0))
        if f == "up" or (f in ("east", "west") and t.j == 0): return p["c4"] if along > 0.2 else p["c3"]
        if f == "down": return p["c0"]
        if f in ("east", "west") and t.j == t.h - 1: return p["c0"]
        if along < 0.08: return p["c0"]
        zz = abs(t.L[2]) + 0.6 * t.j          # chevrons lean back
        band = math.floor(zz / 4.0)
        if zz % 4.0 < 1.0: return p["c0"] if along < 0.75 else p["c1"]
        ramp = ["c1", "c2", "c2", "c3", "c3", "c4"]
        k = min(len(ramp) - 1, int(along * len(ramp)) + (band % 2))
        return p[ramp[k]]
    if mat == "spar":
        # wing bones: dark on top and in front, paler below, knuckles lighter
        if f == "down": return p["p0"]
        if n in ("knuckle", "wrist") and f == "up": return p["g3"]
        if f == "up": return p["g2"] if (t.i // 3) % 4 else p["g3"]
        if f == "north": return p["g2"]
        return p["g1"] if t.j < t.h / 2 else p["g0"]
    if mat == "leg":
        k = math.floor(t.L[1] if f != "up" else t.L[2]) % 3
        if f in ("east", "west", "north", "south") and k == 0 and t.i % 4 != 2: return p["l1"] if t.i % 2 else p["l0"]
        if f == "up": return p["l3"] if k == 1 else p["l2"]
        return p["l1"] if k != 1 else p["l2"]
    if mat == "brow":
        if f == "down": return p["g0"]
        return p["g3"] if (f == "up" and t.i % 3 == 0) else p["g1"]
    if mat == "ruff":
        # longer fibres round the neck base: dark with pale tips in rows
        if f == "down": return p["p1"]
        u, w = skin.face_uv_coords(t)
        row = math.floor(w) % 3
        tip = row == 0 and (math.floor(u) + math.floor(w)) % 2 == 0
        return p["g3"] if tip else (p["g1"] if row == 1 else p["g2"])
    if mat == "belly" or f == "down":
        return strokes(t, p["p1"], p["p3"], p["p2"], seed=3, dense=4)
    seed = zlib.crc32(n.encode()) % 97
    if n == "cranium" or n == "occiput" or n == "cheek":
        if f == "up": return strokes(t, p["g0"], p["g1"], p["g2"], seed)
        if f in ("east", "west"):
            if n == "cheek": return p["r1"] if v > 0.5 else strokes(t, p["p1"], p["p2"], p["p3"], seed, 4)
            if v > 0.78: return strokes(t, p["g0"], p["g1"], p["g2"], seed)
            if v < 0.3: return strokes(t, p["p1"], p["p2"], p["p3"], seed, 4)
            return strokes(t, p["g1"], p["g2"], p["g3"], seed)
        return strokes(t, p["g1"], p["g2"], p["g3"], seed)
    # body, neck, thigh: dark back, a jagged line down the flanks, pale belly; flecks on the neck and shoulders
    if f == "up": return strokes(t, p["g0"], p["g1"], p["g2"], seed)
    if f in ("east", "west", "north", "south"):
        jag = (0, 1, 1, 0, -1, -1)[math.floor(abs(t.P[2]) / 2) % 6] / max(1, t.h)
        line = {"torso": 0.4, "hips": 0.45, "neck1": 0.55, "neck2": 0.5, "thigh": 0.2, "shoulder": 0.25, "rump": 0.2}.get(n, 0.5)
        if v + jag < line - 0.06:
            return strokes(t, p["p1"], p["p2"], p["p3"], seed, 4)
        if v + jag < line + 0.02:
            return p["g3"] if t.i % 2 else p["p0"]
        if n in ("neck1", "neck2", "shoulder"):
            fl = flecks(t)
            if fl: return fl
        return strokes(t, p["g0"], p["g1"], p["g2"], seed) if v > 0.75 else strokes(t, p["g1"], p["g2"], p["g3"], seed)
    return p["p2"]

def decals(img, m):
    C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
    pal = {"E": PAL["eye"], "R": PAL["ring"], "r": PAL["ring2"], "g": PAL["glint"], "M": PAL["mask"], "m": PAL["g1"],
           "K": PAL["kt"], "o": PAL["mouth"], "s": PAL["r0"], "S": PAL["r1"], "T": PAL["r2"]}
    cr = C["cranium"]
    # the eye in a patch of bare red skin, high on the skull, a dark streak running back from it
    eye = ["..sSSSs.......",
           ".sSTTTSs......",
           "sSMMMMMSsmm...",
           "sSMRRRrMSmmmm.",
           "sTMREgRMSsmm..",
           "sTMREErMSs....",
           ".sSMrrMSs.....",
           "..sSSSSs......",
           "...sss........"]
    P.stamp(img, m, cr, "east", eye, pal, at=(0, 1))
    # gape line where the beak meets the skull
    P.stamp(img, m, cr, "east", ["ooooo....", "oooo....."], pal, at=(0, 0), anchor="front-bottom")
    # nostril slit on the upper beak
    P.stamp(img, m, C["beak"], "east", [".......KKKKK"], pal, at=(0, 2))

def paint_sex(m, sex):
    keep = dict(PAL)
    try:
        if sex == "female": PAL.update(FEMALE)
        return P.paint(m, shader, [decals])
    finally:
        PAL.clear(); PAL.update(keep)
