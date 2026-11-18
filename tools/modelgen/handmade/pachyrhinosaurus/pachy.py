"""Pachyrhinosaurus canadensis v4, "o bisão" (16/11/2026), made by hand from the silhouette Rodrigo chose: variant B,
"bisão", of the 1.11 silhouette study (tools/modelgen/handmade/_silhuetas/pachyrhinosaurus.py, `bison`).

The old recipe (a level barrel, a straight tail, thin legs; only the head changed) was refused for the Maiasaura and
the Corythosaurus ("muito padrão, mais do mesmo"), so this one came from the silhouette, in black, measured against
the other horned and duck-billed herbivores (_silhuetas/sil.py; silcheck.py here):

1. the POSTURE of a bison: an enormous hump over the shoulders, the back coming down from it in STEPS to the short
   tail (each step a tier of the hair cape), the trunk a barrel on short thick legs, the forelegs longer than the
   hind ones so the shoulders stand above the hips;
2. the HEAD of a battering ram, hung low on a short thick neck: the boss of P. canadensis (one flat rough mass of
   horn over the nose, the brow bosses almost fused to it behind) pointing at the ground, a deep hooked beak with a
   cutting edge under it, a small deep eye under the brow boss; a short broad frill behind, its two parietal HOOKS
   curving up and forward over the head like a ram's horns (the frill's own bone, adult_hooks; the calf has neither
   boss nor hooks, only a brow, young_brow);
3. the SKIN drawn, not generated: the pardo-tundra of study 15 with a bison's dark CAPE over the hump and the
   shoulders, hanging in a fringe of locks down the flank and the upper forelegs, a paler rump (garupa), dark legs
   like a musk ox's, a near-white belly and throat; the boss worn horn grey with cracks and pores and its edges worn
   pale, the hooks horn with dark tips, the male's ocre-gold at the base of the hooks (the accent of the head);
   a fine scale only as one tone step on the lower flank.

Bones the Java looks for: root, body, neck, head, skull, jaw, adult_boss, young_brow, frill, adult_hooks (hook_l0..2,
hook_r0..2), male_display, female_display, saddle, tail1..3, thigh/shin/foot/toes, arm/forearm/hand.
"""
import math

import numpy as np
import proto as P
import skin2
from proto import hx, h32

TEX_W = 256
PX_M = skin2.PX_PER_M
OUT = lambda *d: [f for f in P.geo.FACES if f not in d]

# ------------------------------------------------------------------ palette ("pardo-tundra", study 15)
SCHEME = {
    "k0": "241a12", "k1": "36281c", "k2": "4b4034", "k3": "6c5e4c", "k4": "8c7a64", "k5": "a28e76",
    "b0": "bcab92", "b1": "d2c6b0", "b2": "e4dccb", "b3": "f2ece0",
    # the cape: the bison's dark wool, a hair warmer than the legs
    "c0": "35251a", "c1": "4b3424", "c2": "64472f", "c3": "805f40",
    # the boss and the hooks: worn horn, grey, never bone white
    "h0": "2c2926", "h1": "47423d", "h2": "666059", "h3": "8a8379", "h4": "aea698",
    # the male's ocre-gold at the base of the hooks
    "o0": "6a5e1e", "o1": "988a2e", "o2": "bcae3e", "o3": "d4c662",
    "bk0": "1a1816", "bk1": "2e2b27", "bk2": "48433d",
    "female": {"o0": "3a3128", "o1": "4b4034", "o2": "6c5e4c", "o3": "8c7a64"},
}
PAL = {
    "iris": hx("5c3c22"), "iris2": hx("7a5434"), "ring": hx("9a8a72"), "pupil": hx("0b0a09"), "glint": hx("f4efe6"),
    "mouth": hx("3a2622"), "tongue": hx("7a4c46"), "gum": hx("58363a"),
    "edge": hx("d8d0c0"), "edge2": hx("a69e8e"),
    "hoof0": hx("17140f"), "hoof1": hx("2c2720"), "hoof2": hx("454036"),
}
# the calf: paler and smooth, no cape yet (a light wash of the dark only on the hump), no horn
CALF = {"k2": "5e5244", "k3": "7f705c", "k4": "9a8a72", "k5": "ae9c84",
        "c0": "4b4034", "c1": "5a4d3e", "c2": "6c5e4c", "c3": "7f705c"}


def pal_for(sex):
    p = dict(PAL)
    for k, v in SCHEME.items():
        if k != "female":
            p[k] = hx(v)
    if sex in ("female", "baby"):
        for k, v in SCHEME["female"].items():
            p[k] = hx(v)
    if sex == "baby":
        for k, v in CALF.items():
            p[k] = hx(v)
    return p


# ------------------------------------------------------------------ geometry
# Model px at PX_M (16.94 px per metre: the blocking's metres x 16.94), the body's middle at z = 0, the ground at y = 0
# (after _ground), the beak toward -z. Signs (geo.rot_matrix): +x lifts what lies in front (-z), lowers what lies
# behind (+z) and sweeps what stands up backward; a hanging limb with +x swings its far end forward.
REST = {"neck": -22, "skull": -26, "frill": 90,
        "hook0": -2, "hook1": -72, "hook2": -62,
        "thigh": 4, "shin": -10, "foot": 6, "toes": 0,
        "arm": -2, "forearm": 6, "hand": -4,
        "tail1": 22, "tail2": 8, "tail3": 4}
BODY_Y = 34
SADDLE_MATS = ("hide", "leather", "wool", "fringe", "cord", "bone", "pack")


def _ground(m):
    import geo
    lo = min(q[:, 1].min() for c, q in geo.cube_points({"bones": m.bones, "cubes": m.cubes})
             if c["mat"] not in SADDLE_MATS + ("teeth",))
    m.shift(-lo)


# THE BACK: the hump and the steps down to the tail, (name, x half width, y0, y1, z0, z1); the hump is a ridge
# (narrower as it rises), every step a tier of the cape a little lower and shorter than the one in front
BACK = (("withers", 17, 46, 68, -34, -22),
        ("hump_a", 16, 50, 78, -26, -15),
        ("hump_b", 15, 52, 83, -17, -4),
        ("step_1", 16, 50, 78, -6, 5),
        ("step_2", 17, 48, 72, 3, 12),
        ("step_3", 18, 45, 65, 10, 19),
        ("step_4", 18.5, 42, 58, 17, 26),
        ("step_5", 18, 40, 52, 24, 32),
        ("step_6", 17, 38, 45, 30, 38))
LIFT = 5      # the barrel stands this much higher on the legs than the blocking (a gap under the belly)
CAPE_TOP = {n: (y1, hw) for n, hw, _y0, y1, _z0, _z1 in BACK}
CAPE_TOP.update({n + "_cap": (y1 + 2, hw - 3) for n, hw, _y0, y1, _z0, _z1 in BACK})


def trunk(m, body):
    """the barrel: a deep chest under the hump, the belly, the hips; then the hump and its steps"""
    m.cube(body, (-19, 18, -34), (19, 52, -10), name="chest")
    m.cube(body, (-21, 17, -11), (21, 50, 14), name="torso")
    m.cube(body, (-19, 21, 13), (19, 45, 38), name="hips")
    m.cube(body, (-17, 15, -26), (17, 19, 30), name="belly", mat="belly", faces=OUT("up"))
    m.cube(body, (-14, 16, -38), (14, 34, -32), name="brisket", mat="belly", faces=OUT("south"))
    for n, hw, y0, y1, z0, z1 in BACK:
        m.cube(body, (-hw, y0, z0), (hw, y1, z1), name=n)
        # the roll of wool on top of each tier: a cap set in from the sides, so the hump reads round
        m.cube(body, (-hw + 3, y1, z0 + 1), (hw - 3, y1 + 2, z1 - 1), name=n + "_cap", faces=OUT("down"))


NECKS = ("neck",)


def head(m, parent, y, z):
    """the ram's head of P. canadensis, held low. (y, z): the occipital joint. In skull space the face runs toward -z;
    the rest pitch hangs it nose-down, so the boss's flat top faces forward and the ground"""
    sk = m.bone("skull", parent, (0, y, z), (REST["skull"], 0, 0))

    def B(x0, y0, z0, x1, y1, z1):
        return (x0, y + y0, z + z0), (x1, y + y1, z + z1)
    # the braincase and the deep face, the beak under the boss
    m.cube(sk, *B(-12, -13, -15, 12, 11, 2), name="cranium")
    m.cube(sk, *B(-10, -12, -28, 10, 7, -14), name="face", faces=OUT("south"))
    m.cube(sk, *B(-5, -13, -37, 5, 1, -27), name="beak", mat="beak", faces=OUT("south"))
    m.cube(sk, *B(-3.5, -16, -38, 3.5, -12, -33), name="beak_tip", mat="beak", faces=OUT("up", "south"))
    # the jugal flares under the eye, the cheek horn of every ceratopsid, short and blunt here
    m.pair(sk, sk, *B(10, -16, -15, 13, -10, -11), name="jugal", mat="horn", faces=OUT("west"))
    # THE BOSS (adult_boss: one rough mass of horn over the nose, its top flat and wide; behind it the brow bosses,
    # almost fused to it, over the eyes). One mass: a body and a rounded cap set into it, never stacked bricks
    ab = m.bone("adult_boss", sk, (0, y + 6, z - 26))
    m.cube(ab, *B(-12, 2, -38, 12, 11, -8), name="boss", mat="boss")
    m.cube(ab, *B(-10, 11, -36, 10, 13, -10), name="boss_cap", mat="boss", faces=OUT("down"))
    m.cube(ab, *B(-10, 0, -39, 10, 9, -38), name="boss_lip", mat="boss", faces=OUT("south"))
    m.cube(ab, *B(-13, 4, -20, 13, 10, -9), name="brow_boss", mat="boss", faces=OUT("up", "down"))
    # the calf's brow: a low swelling where the boss will grow
    yb = m.bone("young_brow", sk, (0, y + 6, z - 22))
    m.cube(yb, *B(-8, 6, -27, 8, 10, -12), name="young_nub", mat="horn")
    # the lower jaw: a deep dentary and the predentary under the beak
    jaw = m.bone("jaw", sk, (0, y - 9, z - 6))
    m.cube(jaw, *B(-9, -18, -27, 9, -11, -4), name="dentary")
    m.cube(jaw, *B(-4, -18, -33, 4, -13, -27), name="predentary", mat="beak", faces=OUT("south"))
    m.cube(jaw, *B(-7, -12, -31, 7, -11, -6), name="mouth", mat="mouth", faces=["up"])
    # the beak's cutting edge, a pale line of horn along its lower rim (what shows of the "teeth" with the mouth shut)
    m.pair(sk, sk, *B(5.25, -13, -36, 5.25, -12, -28), name="beak_edge", mat="teeth")
    frill(m, sk, y, z)
    return sk


# THE HOOKS: (length, half width) of the three pieces of each, laid straight toward -z from the top corner of the
# frill and bent by the bones (REST hook0..2): up and forward off the frill, then over and down like a ram's horn
HOOK = ((12, 3.0), (10, 2.5), (8, 2.0))
HOOK_X = 12


def frill(m, sk, y, z):
    """the short broad frill behind the head, leaning back, a rim of small horn points along its edge; the two hooks
    from its top corners (adult_hooks)"""
    by, bz = y + 9, z + 1
    fr = m.bone("frill", sk, (0, by, bz), (REST["frill"], 0, 0))
    # a rounded top edge: the middle plate tallest, the wings lower and thinner
    m.cube(fr, (-14, by, bz - 3), (14, by + 24, bz + 3), name="frill_plate", mat="frill")
    m.pair(fr, fr, (14, by + 1, bz - 2.5), (21, by + 19, bz + 2.5), name="frill_wing", mat="frill", faces=OUT("west"))
    m.cube(fr, (-16, by - 2, bz - 4), (16, by + 12, bz + 4), name="frill_root", mat="frill")
    for k, (xc, top) in enumerate(((-18, 19), (-8, 24), (-2, 24), (4, 24), (18, 19))):
        m.cube(fr, (xc - 1.5, by + top, bz - 1.5), (xc + 1.5, by + top + 3, bz + 1.5), name=f"frill_pt{k}", mat="horn", pt=k)
    ah = m.bone("adult_hooks", fr, (0, by + 22, bz))
    for side, sx in (("l", 1), ("r", -1)):
        par = ah
        zc = bz
        for k, (L, w) in enumerate(HOOK):
            b = m.bone(f"hook_{side}{k}", par, (HOOK_X * sx, by + 22, zc), (REST[f"hook{k}"], 0, 0))
            par = b
            zc -= L
    zc = bz
    for k, (L, w) in enumerate(HOOK):
        m.pair(f"hook_l{k}", f"hook_r{k}", (HOOK_X - w, by + 22 - w, zc - L - (1 if k < 2 else 0)),
               (HOOK_X + w, by + 22 + w, zc), name=f"hook{k}", mat="hook", seg=k)
        zc -= L
    # the male's collar at the root of each hook (male_display): ocre-gold skin, half way up the horn
    md = m.bone("male_display", fr, (0, by + 22, bz))
    m.pair(md, md, (HOOK_X - 3.5, by + 20, bz - 3.5), (HOOK_X + 3.5, by + 23, bz + 3.5), name="hook_collar", mat="collar")
    m.bone("female_display", fr, (0, by + 22, bz))


def neck(m, body):
    """short and thick, the head hung from it nose-down; a pale dewlap of skin under it"""
    n = m.bone("neck", body, (0, 42, -32), (REST["neck"], 0, 0))
    m.cube(n, (-13, 27, -44), (13, 52, -30), name="neck")
    m.cube(n, (-9, 23, -42), (9, 28, -32), name="dewlap", mat="belly", faces=OUT("up"))
    hd = m.bone("head", n, (0, 41, -44))
    head(m, hd, 41, -44)


def hind_legs(m, body):
    """short and pillar-thick: the thigh deep in the barrel, a short shin, a broad foot with four hoofed toes"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (13 * sx, 30, 25), (REST["thigh"], 0, 0))
        sh = m.bone(f"shin_{side}", th, (13 * sx, 14, 25), (REST["shin"], 0, 0))
        ft = m.bone(f"foot_{side}", sh, (13 * sx, 5, 25), (REST["foot"], 0, 0))
        m.bone(f"toes_{side}", ft, (13 * sx, 1.5, 19), (REST["toes"], 0, 0))
    m.pair("thigh_l", "thigh_r", (7, 13, 16), (20, 37, 33), name="thigh")
    m.pair("shin_l", "shin_r", (8, 4, 20), (18, 15, 30), name="shin")
    m.pair("foot_l", "foot_r", (7, 1, 18), (19, 6, 31), name="pes")
    m.pair("toes_l", "toes_r", (7.5, 1, 15), (18.5, 3, 19), name="toes")
    for k, xc in enumerate((9.0, 13.0, 17.0)):
        m.pair("toes_l", "toes_r", (xc - 1.5, 0, 13.5), (xc + 1.5, 2, 15.5), name=f"hoof_h{k}", mat="hoof", faces=OUT("south"))


def fore_legs(m, body):
    """longer than the hind legs (the shoulders stand above the hips): a deep upper arm under the hump, a thick
    forearm, a broad hand of hoofed fingers"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (14 * sx, 34, -20), (REST["arm"], 0, 0))
        fa = m.bone(f"forearm_{side}", a, (14 * sx, 18, -20), (REST["forearm"], 0, 0))
        m.bone(f"hand_{side}", fa, (14 * sx, 5, -20), (REST["hand"], 0, 0))
    m.pair("arm_l", "arm_r", (8, 17, -28), (21, 40, -12), name="arm")
    m.pair("forearm_l", "forearm_r", (9, 4, -25), (19, 19, -15), name="forearm")
    m.pair("hand_l", "hand_r", (7.5, 1, -27), (20.5, 6, -13), name="hand")
    for k, xc in enumerate((9.5, 13.0, 16.5)):
        m.pair("hand_l", "hand_r", (xc - 1.5, 0, -29), (xc + 1.5, 2, -27), name=f"hoof_f{k}", mat="hoof", faces=OUT("south"))


TAILS = ("tail1", "tail2", "tail3")


def tail(m, body):
    """short and hung low off the last step, three pieces that overlap and taper"""
    segs = [("tail1", 37, 35, 49, 8, 30, 44), ("tail2", 47, 46, 57, 5.5, 32, 41), ("tail3", 55, 54, 63, 3.5, 34, 39)]
    parent = body
    for n, pz, z0, z1, hw, y0, y1 in segs:
        b = m.bone(n, parent, (0, 37, pz), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b


def build(saddle_on=True):
    m = P.Model("pachyrhinosaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, BODY_Y, 0))
    trunk(m, body)
    neck(m, body)
    fore_legs(m, body); hind_legs(m, body); tail(m, body)
    if saddle_on:
        saddle(m, body)
    _lift(m, LIFT)
    _ground(m)
    return m


def _lift(m, dy):
    """everything above the knees and the elbows up by dy; the shins and the forearms grow by dy to follow"""
    low = ("foot", "toes", "hand")
    grow = ("shin", "forearm")
    for b in m.bones:
        k = b["name"].rsplit("_", 1)[0]
        if k not in low and k not in grow:
            b["origin"][1] += dy
        elif k in grow:
            b["origin"][1] += dy
    for c in m.cubes:
        k = c["bone"].rsplit("_", 1)[0]
        if k in grow:
            c["to"][1] += dy
        elif k not in low:
            c["from"][1] += dy; c["to"][1] += dy; c["origin"][1] += dy


# ------------------------------------------------------------------ the saddle: the pack saddle ("sela de carga")
SADDLE_PAL = {   # its own: a thick felted blanket over the steps behind the hump, a low hide seat, packs at the sides
    "W0": hx("3e2e22"), "W1": hx("5a4230"), "W2": hx("7a5a3e"), "W3": hx("9c7a52"),
    "H0": hx("2a2420"), "H1": hx("443830"), "H2": hx("5e4c40"),
    "L0": hx("221a16"), "L1": hx("3a2c22"),
    "F0": hx("6e5a3a"), "F1": hx("8c7650"),
    "C0": hx("5e5440"), "C1": hx("7c7056"), "B0": hx("bcb49c"), "B1": hx("dcd6c2"),
    "P0": hx("4a4230"), "P1": hx("665c44"), "P2": hx("807456"),
}


def saddle(m, body):
    """The pack saddle: a thick felted blanket over the first steps behind the hump, a low hide seat in the dip, a
    bone grip to hold against the hump, two lashed packs hanging at the flanks (it carries: cargo rows), a girth of
    cord under the barrel. Faces lying on the body are left out."""
    sd = m.bone("saddle", body, (0, 76, 10))
    # the blanket over step 2 and step 3: thicker behind, so the seat stays level on the stepped back
    m.cube(sd, (-15, 73, 2), (15, 77, 11), name="blanket", mat="wool", faces=OUT("down"))
    m.cube(sd, (-16, 66, 11), (16, 77, 19), name="blanket_back", mat="wool", faces=OUT("down"))
    m.pair(sd, sd, (17, 50, 3), (19, 73, 18), name="blanket_side", mat="wool", faces=OUT("west"))
    m.pair(sd, sd, (17.5, 48, 4), (19.5, 50, 17), name="fringe", mat="fringe", faces=OUT("west"))
    m.cube(sd, (-9, 77, 3), (9, 79, 17), name="seat", mat="hide", faces=OUT("down"))
    m.cube(sd, (-7, 79, 14), (7, 82, 17), name="cantle", mat="leather")
    m.cube(sd, (-1, 79, 1), (1, 84, 3), name="grip", mat="bone")
    m.cube(sd, (-2, 83, 0), (2, 85, 4), name="grip_top", mat="bone")
    m.pair(sd, sd, (19.5, 50, 5), (25.5, 64, 16), name="pack", mat="pack")
    m.pair(sd, sd, (20, 64, 6), (25, 66, 15), name="pack_lid", mat="leather", faces=OUT("down"))
    m.pair(sd, sd, (21.5, 36, 8), (22.5, 66, 11), name="girth_side", mat="cord", faces=OUT("west"))
    m.cube(sd, (-22.5, 35, 8), (22.5, 36, 11), name="girth_under", mat="cord", faces=OUT("up"))


def saddle_px(t):
    c = t.cube; mat = c["mat"]; f = t.face; p = SADDLE_PAL
    i, j, w, h = t.i, t.j, t.w, t.h
    if mat == "wool":
        # the felted blanket: broad woven bands across, the edge darker
        if j == h - 1 and f != "up":
            return p["W0"]
        band = (j if f != "up" else i) // 3 % 3
        return p[("W1", "W2", "W3")[band]] if (i + j) % 7 else p["W1"]
    if mat == "fringe":
        return p["F1"] if i % 2 == 0 else p["F0"]
    if mat == "cord":
        return p["C1"] if (i + j) % 3 else p["C0"]
    if mat == "bone":
        return p["B1"] if f == "up" or j == 0 else p["B0"]
    if mat == "leather":
        return p["L1"] if j < h - 1 else p["L0"]
    if mat == "pack":
        if j in (2, h - 3) or i in (1, w - 2):
            return p["C1"]
        return p["P1"] if h32(i // 2, j // 2, 9) % 3 else p["P2"] if f != "down" else p["P0"]
    if f == "up":
        return p["H2"] if (i * 3 + j) % 11 else p["H1"]
    return p["H0"] if j == h - 1 else p["H1"]


def preview_faces(m):
    """previews only: swap east/west on cubes that drop one of them, so the preview shows the face the game shows"""
    for c in m.cubes:
        f = c["faces"]
        if ("east" in f) != ("west" in f):
            c["faces"] = [{"east": "west", "west": "east"}.get(x, x) for x in f]
    return m


# ------------------------------------------------------------------ the skin: DRAWN
BACKS = {n for n, *_ in BACK} | {n + "_cap" for n, *_ in BACK}
TRUNK = {"chest", "torso", "hips", "neck"} | BACKS | set(TAILS)
UNDER = {"belly", "brisket", "dewlap"}
LEG = {"shin", "pes", "toes", "forearm", "hand"}
LIMB = {"thigh", "arm"}
HEAD = {"cranium", "face", "dentary"}


def fringe_y(z, x=0.0):
    """the lower edge of the cape (body space, y up from the hip line), hanging in LOCKS: low over the shoulder and
    the forearm, rising along the back so the rump is bare. Each lock is 2-3 texels wide and of its own length"""
    zz = z
    if zz < -24:
        base = 14.0                                     # the shoulder and the chest: the cape hangs low
    elif zz < 14:
        base = 14.0 + (zz + 24) * 0.42                   # rising along the flank
    else:
        base = 30.0 + (zz - 14) * 0.9                   # off the rump
    lock = math.floor(zz / 2.5)
    hang = (h32(lock, 77) % 7) - 1.5 + 2.4 * math.sin(lock * 0.9)
    return base - hang


def cape_hair(t, inside):
    """the wool: vertical strokes of hair, a step lighter near the top of each tier (the cape is stepped, each tier a
    roll of wool), the very edge of the fringe the darkest"""
    u = math.floor(t.P[2] if t.face in ("east", "west") else t.P[0])
    v = math.floor(t.P[1] / 4)
    hy = t.P[1] - HIPW[1]
    # the wool lighter high on the hump, darker down toward the fringe (a bison's cape)
    base = "c3" if hy > 34 else "c2" if hy > 22 else "c1"
    stroke = h32(u, v, 31) % 5
    if stroke == 0:
        return {"c3": "c2", "c2": "c1", "c1": "c0"}[base]
    if stroke == 1 and base != "c3":
        return {"c2": "c3", "c1": "c2"}[base]
    return base


def body_tone(t, prof, calf=False):
    """the palette key of a body texel"""
    n = t.cube["name"]; f = t.face
    z, y = t.P[2], t.P[1] - HIPW[1]
    if n in UNDER:
        if f == "down" and h32(math.floor(t.P[0] / 3), math.floor(t.P[2] / 2), 3) % 6 == 0:
            return "b2"
        return "b3" if f == "down" else "b2"
    if f == "down":
        return "b1"
    # the hump and its steps: the cape over the top, each tier's top edge a step lighter (the roll of wool)
    if n in BACKS:
        top = CAPE_TOP[n][0]
        if f == "up":
            # the wool on top: strokes running front to back, the parting of the hair
            return "c2" if h32(t.i, t.j // 4, 44) % 11 == 0 else "c3"
        if calf:
            return "c2" if t.P[1] > top - 4 else "k4"
        if f in ("east", "west", "north", "south") and t.P[1] > top - 1.5:
            # the roll of wool along the tier's edge, broken by locks
            return "c2" if h32(math.floor((t.P[2] if f in ("east", "west") else t.P[0]) / 2), 52) % 3 == 0 else "c3"
        if f == "south" and n.startswith("step"):
            return "c2" if (t.i + t.j) % 4 else "c1"
        return cape_hair(t, True)
    if n == "neck":
        if f == "up":
            return "c2"
        if calf:
            return "k3"
        # the neck under the cape, the locks hanging to the throat
        fy = 10.0 + 3.0 * math.sin(math.floor(t.P[2] / 2.5) * 1.3) + (h32(math.floor(t.P[2] / 2.5), 5) % 4)
        hy = t.P[1] - (NECK_Y[0])
        if f in ("east", "west", "north") and hy > fy:
            return cape_hair(t, True)
        return "k3" if hy > fy - 4 else "k4"
    if n in TAILS:
        if f == "up":
            return "k1" if h32(t.i, t.j // 2, 12) % 4 else "k2"
        v = float(t.rel[1])
        base = "k1" if v > 0.6 else "k2" if v > 0.3 else "k3"
        if h32(math.floor(t.P[2] / 2), math.floor(t.P[1]), 19) % 5 == 0:
            base = skin2.step(base, 1)
        return base
    # chest, torso, hips: the cape's fringe of locks over the flank, the bare flank below, the paler rump
    if f == "up":
        return "c1"
    h = prof.height(t)
    if not calf and f in ("east", "west", "north", "south") and y > fringe_y(z):
        return cape_hair(t, True)
    if not calf and f in ("east", "west") and fringe_y(z) - 2.0 < y <= fringe_y(z):
        return "k2"                                       # the shadow under the locks
    b = skin2.bands(h, z, (0.12, 0.24, 0.42, 0.70), amp=0.04, seed=41)
    base = ["b2", "b0", "k4", "k5", "k5"][b]
    if n == "hips" and f in ("east", "west", "south") and b >= 2:
        # the paler rump (garupa): a soft light patch round the base of the tail
        dz, dy = t.P[2] - RUMP[0], t.P[1] - RUMP[1]
        if dz * dz / 160.0 + dy * dy / 90.0 < 1.0 + 0.15 * math.sin(t.P[1] * 0.7 + t.P[2] * 0.4):
            base = "b0"
    if f == "north" and n == "chest":
        base = "k3"
    if calf:
        return base
    # the fine scale, only one tone step, sparse, on the bare lower flank
    if 0.12 < h < 0.62 and skin2.scales(t, cell=5.0, seed=35, flat=0.32) == "edge":
        base = skin2.step(base, -1)
    return base


def limb_tone(t, calf=False):
    """legs: the dark legs of a musk ox (pardo-breu); the cape's long hair over the upper forelegs (the bison's
    chaps), the knees and the feet darkest; scutes on the front of the feet"""
    n = t.cube["name"]; f = t.face
    if n == "arm":
        if f == "up":
            return "c1"
        if not calf and f in ("east", "west", "north", "south"):
            # the chaps: long locks from the shoulder down to below the elbow
            lock = math.floor((t.P[2] if f in ("east", "west") else t.P[0]) / 2.0)
            edge = 3 + (h32(lock, 13) % 5)
            if t.L[1] - t.cube["from"][1] > edge:
                return cape_hair(t, True)
        return "k1" if f in ("south", "down") else "k2"
    if n == "thigh":
        if f == "up":
            return "k3"
        v = t.L[1] - t.cube["from"][1]
        H = t.cube["to"][1] - t.cube["from"][1]
        if f in ("east", "west", "south"):
            # the thigh: the rump's paler skin at the top, darkening down into the dark leg
            return "k4" if v > H * 0.7 else "k3" if v > H * 0.42 else "k2"
        return "k2"
    if n in ("shin", "forearm"):
        base = "k1" if f in ("north", "east", "west") else "k0"
        if f in ("east", "west") and (h32(math.floor(t.L[1]), math.floor(t.L[2] / 2), 3) % 9 == 0):
            return "k2"
        return base
    # the feet and the hands: darkest, the toes scuted across
    if f in ("north", "up"):
        k = math.floor(t.L[1] if f != "up" else t.L[2]) % 2
        if k == 0 and t.i % 3 != 1:
            return "k0"
    return "k1" if f in ("north", "east", "west", "up") else "k0"


# ------------------------------------------------------------------ the head of the padrão v3, its own
def head_tone(t, sex):
    """the face: deep WRINKLES fanning back from the boss (no round scale), the dark of the face under the brow boss,
    the pale throat; the jaw a tone lighter at its lower rim"""
    n = t.cube["name"]; f = t.face
    if f == "down":
        return "b1"
    if n == "dentary":
        if f == "up":
            return "k3"
        if t.j == 0:
            return "k2"
        if f in ("east", "west") and (t.i + 3 * t.j) % 4 == 0:
            return "k3"
        return "b0" if t.rel[1] < 0.35 else "k4"
    if f == "up":
        return "k2" if (t.i + 2 * t.j) % 5 else "k1"
    if n == "cranium" and f in ("east", "west"):
        dz = t.P[2] - EYE[0]; dy = t.P[1] - EYE[1]
        # the deep socket: the brow boss's shadow over the eye
        if dz * dz / 10.0 + dy * dy / 5.0 < 1.0:
            return "k1"
    # the wrinkles: lines fanning from the boss (its centre in body space at BOSSW) across the face, 1 texel deep
    if f in ("east", "west", "north", "south"):
        dz = t.P[2] - BOSSW[0]; dy = t.P[1] - BOSSW[1]
        ang = math.atan2(dy, dz)
        r = math.hypot(dz, dy)
        ray = (ang * 11.0 / math.pi + 0.35 * math.sin(r * 0.45)) % 1.0
        if r > 7 and ray < 0.18:
            return "k1" if r < 16 else "k2"
        if r > 7 and ray < 0.34:
            return "k5" if r < 14 else "k4"
    # the fine creases of thick hide between the folds, short and broken (never round scale)
    cr = (t.P[1] * 0.9 + 0.8 * math.sin(t.P[2] * 0.7)) % 3.0
    if cr < 0.8 and h32(math.floor(t.P[2] / 2), math.floor(t.P[1] / 3), 8) % 3:
        return "k2"
    hv = float(t.rel[1]) if f in ("east", "west") else 0.5
    return "k3" if hv > 0.45 else "k4"


def plates(t, cell=4.5, seed=91):
    """the boss's plates: a Voronoi of irregular horn plates in body space; returns (plate id, on a crack)"""
    u, v = skin2.surface_uv(t)
    uc, vc = math.floor(u) + 0.5, math.floor(v) + 0.5
    gx, gy = math.floor(uc / cell), math.floor(vc / cell)
    best = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            cx, cy = gx + dx, gy + dy
            px = (cx + 0.15 + 0.7 * (h32(cx, cy, seed, 1) % 1000) / 1000) * cell
            py = (cy + 0.15 + 0.7 * (h32(cx, cy, seed, 2) % 1000) / 1000) * cell
            best.append((math.hypot(uc - px, (vc - py) * 1.2), (cx, cy), vc - py))
    best.sort()
    (d1, cid, dy), (d2, _c, _y) = best[0], best[1]
    return h32(*cid, seed, 3), d2 - d1 < 0.7, dy


def boss_px(t, p):
    """the boss: worn horn, one mass of irregular plates 3-5 texels across, each plate one tone, split by dark cracks,
    the upper edge of every plate worn pale, a pore now and then. The plates run on over the cube edges (body space),
    so the boss reads as one rough mass"""
    f = t.face
    pid, crack, dy = plates(t)
    if crack:
        return p["h0"] if f in ("east", "west", "south") else p["h1"]
    u, v = skin2.surface_uv(t)
    if h32(math.floor(u), math.floor(v), 17) % 29 == 0:
        return p["h1"]
    worn = f in ("up", "north") or t.cube["name"] == "boss_cap"
    tone = ("h2", "h3", "h3", "h4")[pid % 4] if worn else ("h2", "h2", "h3", "h3")[pid % 4]
    if f in ("east", "west") and dy > 1.2:
        tone = {"h2": "h3", "h3": "h4", "h4": "h4"}[tone]     # the plate's upper edge, worn pale
    # its root in the skin (the ornament grows from the skull): the lowest row the face's colour
    if f in ("east", "west") and t.j == t.h - 1 and t.cube["name"] != "boss_lip":
        return p["k2"]
    return p[tone]


def hook_px(t, p, sex):
    """the hooks: horn, darker toward the tip; the male's ocre-gold skin rises half way up the first piece"""
    seg = t.cube.get("seg", 0)
    f = t.face
    along = 1.0 - float(t.rel[2]) if f not in ("north", "south") else (1.0 if f == "north" else 0.0)
    if seg == 2:
        return p["h0"] if along > 0.45 or f == "north" else p["h1"]
    if seg == 1:
        return p["h1"] if along > 0.6 else p["h2"]
    if sex == "male" and along < 0.5 and f != "north":
        return p["o2"] if (t.i + t.j) % 3 else p["o3"]
    return p["h3"] if f == "up" else p["h2"]


def frill_px(t, p, sex):
    """the frill: a tone darker than the body, its rim pale (neve-suja), the small points along the rim horn-coloured;
    the back of the frill under the cape's colour"""
    n = t.cube["name"]; f = t.face
    if t.cube.get("pt") is not None:
        return p["h3"] if f == "up" else p["h2"]
    if n == "frill_root":
        return p["c1"] if f in ("south", "up") else p["k3"]
    if f == "south":
        return p["c2"] if h32(t.i, t.j // 3, 21) % 3 == 0 else p["c1"]
    if f == "up":
        return p["b3"] if (t.i + t.j) % 3 else p["b1"]
    v = float(t.rel[1])
    if n == "frill_wing":
        v = v * 19.0 / 24.0
    if f in ("north", "east", "west") and v > 0.86:
        return p["b3"]
    if f in ("north", "east", "west") and v > 0.78:
        return p["b1"]
    # the male's accent where the hooks rise from the frill (the collar continues onto the plate)
    if sex == "male" and f == "north" and v > 0.62 and abs(abs(t.P[0]) - HOOK_X) < 4.0:
        return p["o2"] if (t.i + t.j) % 3 else p["o3"]
    # broad soft vascular grooves running up the frill
    if f == "north" and math.floor(t.P[0] + 2 * math.sin(v * 5.0)) % 4 == 0:
        return p["k2"] if v < 0.5 else p["k3"]
    return p["k4"] if v > 0.4 else p["k3"]


def beak_px(t, p):
    n = t.cube["name"]; f = t.face
    if f == "up":
        return p["bk2"] if (t.i * 2 + t.j) % 3 else p["bk1"]
    if f == "down":
        return p["bk0"]
    if f in ("east", "west") and (t.i + 2 * t.j) % 5 == 0:
        return p["bk2"]
    if n == "beak_tip":
        return p["bk2"] if t.j == t.h - 1 else p["bk1"]
    return p["bk1"] if t.j > 0 else p["bk2"]


def shader_for(sex):
    p = pal_for(sex)
    calf = sex == "baby"

    def sh(t):
        mat = t.cube["mat"]; f = t.face; n = t.cube["name"]
        if mat in SADDLE_MATS:
            return saddle_px(t)
        if mat == "hoof":
            if f == "up":
                return p["hoof2"]
            return p["hoof1"] if t.j < t.h - 1 else p["hoof0"]
        if mat == "boss":
            return boss_px(t, p)
        if mat == "hook":
            return hook_px(t, p, sex)
        if mat == "collar":
            if sex == "male":
                return p["o2"] if (t.i + t.j) % 4 else p["o1"]
            return p["k3"]
        if mat == "frill":
            return frill_px(t, p, sex)
        if mat == "horn":
            if n == "jugal":
                return p["h2"] if f != "down" else p["h1"]
            if n == "young_nub":
                return p["k3"] if (t.i + t.j) % 3 else p["k2"]
            return p["h2"]
        if mat == "beak":
            return beak_px(t, p)
        if mat == "teeth":
            if f not in ("east", "west"):
                return None
            return p["edge"] if int(t.L[2] - t.cube["from"][2]) < 6 else p["edge2"]
        if mat == "mouth":
            return p["tongue"] if (t.i + t.j) % 4 else p["gum"]
        if n in TRUNK or n in UNDER:
            return p[body_tone(t, PROF[0], calf)]
        if n in LEG or n in LIMB:
            return p[limb_tone(t, calf)]
        if n in HEAD:
            return p[head_tone(t, sex)]
        return p["k3"]
    return sh


PROF = [None]
HIPW = [0.0, 0.0, 0.0]
RUMP = [0.0, 0.0]
EYE = [0.0, 0.0]
BOSSW = [0.0, 0.0]
NECK_Y = [0.0]

# ------------------------------------------------------------------ the drawn details of the head
# east = the animal's left (mirrored onto the right); column 0 at the FRONT, row 0 at the TOP
EYE_ART = [
    "kkkkk",
    "krgik",
    "kpppk",
    ".kIk.",
]
NOSTRIL = [
    "kk",
    "kh",
]


def decals_for(sex):
    p = pal_for(sex)
    cm = {"k": p["k0"], "g": p["glint"], "i": p["iris"], "I": p["iris2"], "p": p["pupil"], "r": p["ring"],
          "n": p["k0"], "h": p["k1"]}

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        P.stamp(img, m, C["cranium"], "east", EYE_ART, cm, at=(1, 11))
        P.stamp(img, m, C["face"], "east", NOSTRIL, cm, at=(3, 2))
    return dec


def paint_sex(m, sex="male"):
    import geo
    PROF[0] = skin2.Profile(m, {"chest", "torso", "hips", "belly"} | BACKS)
    mats = geo.bone_mats(m.spec())
    pts = {c["name"]: q for c, q in geo.cube_points(m.spec())}
    hp = pts["hips"]
    HIPW[:] = [0.0, float(hp[:, 1].min()), float(hp[:, 2].mean())]
    RUMP[:] = [float(hp[:, 2].max()) - 4.0, float(hp[:, 1].max()) - 6.0]
    NECK_Y[:] = [float(pts["neck"][:, 1].min())]
    bq = pts["boss"]
    BOSSW[:] = [float(bq[:, 2].mean()), float(bq[:, 1].mean())]
    c = next(c for c in m.cubes if c["name"] == "cranium")
    loc = [0.0, c["to"][1] - 13.0, c["from"][2] + 3.0]
    w = mats[c["bone"]] @ [loc[0], loc[1], loc[2], 1.0]
    EYE[:] = [float(w[2]), float(w[1])]
    return P.paint(m, shader_for(sex), decals=(decals_for(sex),))
