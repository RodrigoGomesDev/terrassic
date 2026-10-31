"""
Velociraptor v3 (hand-made rig in the T. rex / Pteranodon standard, approved by Rodrigo 30/10 20:45Z).
Velociraptor mongoliensis, Djadokhta Formation (Mongolia, ~75 Ma): 2.07 m long, ~0.5 m at the hip, 15-20 kg.

Why a v3 (Rodrigo 30/10): v1 "devia ser mais assustador", v2b "ficou muito simples, não está no padrão do projeto".
Measured against the T. rex v2, the Pteranodon v3 and Alex's Caves' Vallumraptor, v2b failed on:
  * resolution: 61 px long, 1.9k painted texels (T. rex 37.6k, Pteranodon 14.3k): every face was 2-5 px, too small
    to draw anything, so the skin read as flat blocks;
  * the eye was a 3x1 slit (T. rex 9x7, Pteranodon ~6x5 in a red patch): no eye reads as no face;
  * stick limbs (1-2 px), no fingers, no toes, small spines: no secondary forms;
  * an almost monochrome dark brown with no accent.
v3 is drawn at ~48 px per metre (100 px nose to tail fan, 1.64x v2b), with a head of 14 cubes (cranium, three-step
snout with the upturned tip, brow ridges, jaw-muscle cheeks, two jaw parts, four tooth planes, lids), three clawed
fingers per hand, two toes plus the raised sickle toe, wing feathers in two layers, a frond tail fan tilted into a
shallow V so it reads from the side, and a nuchal crest. Skin drawn by form on every face: staggered feather cells
with a shadowed tip and a lit edge, scutes on the legs, small scales and a lip row on the snout.

Coordinates as in the T. rex: px, x+ = left, z- = forward, y up. 1 texel = 1 px of texture.
"""
import math
import zlib
import numpy as np
import proto as P, geo, skin
from proto import hx, h32

PAL = {
    # plumage: umber back, tawny flanks, cream belly
    "d0": hx("1b1612"), "d1": hx("2b221b"), "d2": hx("3d3026"), "d3": hx("574533"), "d4": hx("7a6146"), "d5": hx("9c8059"),
    "b0": hx("8f7d5f"), "b1": hx("b5a27e"), "b2": hx("d1c19c"), "b3": hx("e6dabb"),
    # the accent: a steel-blue sheen on the crest, the wing coverts and the tail fan (iridescence is attested in
    # Microraptor, Li et al. 2012)
    "u0": hx("1c2830"), "u1": hx("2c4350"), "u2": hx("436577"), "u3": hx("6a8fa0"),
    # warm rim on the front edge of the bars
    "r1": hx("6e3a1f"), "r2": hx("94532a"),
    "k0": hx("0e0b09"), "k1": hx("1a1512"), "w2": hx("e2d8bd"),
    # bare scaly skin (snout, legs, feet)
    "sc0": hx("221e1b"), "sc1": hx("383029"), "sc2": hx("51463c"), "sc3": hx("6e6154"), "sc4": hx("8c7d6c"),
    "claw": hx("17120f"), "clawl": hx("e2d8bd"), "claw2": hx("b0a487"),
    "tooth": hx("f0e9d3"), "tooth2": hx("c9bd98"), "gum": hx("6b2424"), "mouth": hx("2e1211"), "tongue": hx("8e3a33"),
    "eye": hx("f0a830"), "eye_hi": hx("ffd766"), "eye2": hx("a9681a"), "pupil": hx("0a0706"), "glint": hx("fff4cf"),
    "lea0": hx("2e1d14"), "lea1": hx("4a2f1f"), "lea2": hx("6b4429"), "stitch": hx("b89b6a"), "bone": hx("ddd2b4"), "bone0": hx("a89c7c"),
}
UP = {"d0": "d1", "d1": "d2", "d2": "d3", "d3": "d4", "d4": "d5", "d5": "d5", "b0": "b1", "b1": "b2", "b2": "b3", "b3": "b3",
      "u0": "u1", "u1": "u2", "u2": "u3", "u3": "u3", "sc0": "sc1", "sc1": "sc2", "sc2": "sc3", "sc3": "sc4", "sc4": "sc4"}
DN = {v: k for k, v in UP.items() if k != v}; DN.update({"d0": "k1", "b0": "d4", "u0": "k1", "sc0": "k1"})

# the female: ash grey-brown, the sheen muted to slate, the same bars
FEMALE = {
    "d0": hx("1a1816"), "d1": hx("2a2723"), "d2": hx("3b3731"), "d3": hx("534d44"), "d4": hx("736b5e"), "d5": hx("938a7b"),
    "b0": hx("8a8270"), "b1": hx("aba28d"), "b2": hx("c6bea8"), "b3": hx("dcd5c1"),
    "u0": hx("23272a"), "u1": hx("343b40"), "u2": hx("4b555c"), "u3": hx("68737a"),
    "r1": hx("5a3c2a"), "r2": hx("7a5640"),
}

HIP_Y = 26
BARRED = ("torso", "rump", "neck", "neck2", "tail1", "tail2", "tail3", "thigh")


def build(harness=False):
    m = P.Model("velociraptor")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, HIP_Y, 0))
    m.cube(body, (-4.5, 19, -14), (4.5, 29, 1), name="torso")
    m.cube(body, (-3.5, 16, -14), (3.5, 19.5, -3), name="keel", mat="belly")
    m.cube(body, (-4, 21, 0), (4, 28.5, 7), name="rump")
    m.cube(body, (-0.15, 29, -12), (-0.15, 32, 5), name="crest_back", mat="crest", faces=["east", "west"])
    # neck: a forward S, thick at the base; the nuchal crest of longer feathers along the top
    neck = m.bone("neck", body, (0, 25.5, -13), (36, 0, 0))
    m.cube(neck, (-3, 21.5, -21), (3, 28.5, -12), name="neck")
    m.cube(neck, (-2.5, 20.5, -20), (2.5, 21.5, -13), name="throat", mat="belly")
    m.cube(neck, (0.05, 28.5, -21), (0.05, 32.5, -12), name="crest_neck", mat="crest", faces=["east", "west"])
    neck2 = m.bone("neck2", neck, (0, 25, -20), (-28, 0, 0))
    m.cube(neck2, (-2.5, 21.5, -27), (2.5, 27.5, -19), name="neck2")
    m.cube(neck2, (-0.05, 27.5, -27), (-0.05, 31.5, -19), name="crest_neck2", mat="crest", faces=["east", "west"])
    head = m.bone("head", neck2, (0, 25, -26))
    skull = m.bone("skull", head, (0, 25, -26), (-12, 0, 0))
    # the skull: long and low, flat on top, the snout dished with an upturned tip
    m.cube(skull, (-3.5, 21, -32), (3.5, 28, -24), name="cranium")
    m.cube(skull, (-2.5, 21, -39), (2.5, 26, -32), name="snout1")
    m.cube(skull, (-2, 21, -45), (2, 25, -39), name="snout2")
    m.cube(skull, (-1.5, 25, -45), (1.5, 26, -42), name="nose")
    m.cube(skull, (0.15, 28, -30), (0.15, 31, -23), name="crest_head", mat="crest", faces=["east", "west"])
    m.pair(skull, skull, (2.5, 26.5, -32), (4, 28.5, -26), name="brow", mat="brow", rot=(-12, 0, 0), origin=(3.25, 27.5, -26))
    m.pair(skull, skull, (3, 21.5, -30), (4, 24.5, -25.5), name="cheek")
    # eyelids: planes hidden just inside the skull; the sleep, knockout and blink poses slide them out over the eyes
    m.bone("lid_l", skull, (3.1, 25, -28.5)); m.bone("lid_r", skull, (-3.1, 25, -28.5))
    m.pair("lid_l", "lid_r", (3.1, 23, -31), (3.1, 27, -26), name="lid", mat="lid", faces=["east"])
    # upper teeth: alpha planes hanging below the snout, outside the narrow lower jaw: they show with the mouth shut
    m.pair(skull, skull, (1.7, 19, -44.5), (1.7, 21, -39), name="teeth_up", mat="teeth")
    m.pair(skull, skull, (2.2, 19, -39), (2.2, 21, -32), name="teeth_up2", mat="teeth")
    jaw = m.bone("jaw", skull, (0, 21.5, -26))
    m.cube(jaw, (-3, 18.5, -33), (3, 21.5, -25), name="jaw_back")
    m.cube(jaw, (-1.5, 19.5, -44), (1.5, 21.5, -33), name="jaw_front")
    m.pair(jaw, jaw, (1.25, 21.5, -43.5), (1.25, 23, -33), name="teeth_lo", mat="teeth_lo")
    # arms carried forward and ready; three clawed fingers; the wing feathers in two layers hang under the forearm
    # and hand (quill knobs on the ulna: Turner et al. 2007). The arm sits AX outside the leg so no arm face shares a
    # plane with a leg face (they z-fought in walk and sit); the hand is a hair slimmer than the forearm for the same
    # reason when the wing is stretched straight
    AX = 0.3
    for side, sx in (("l", 1), ("r", -1)):
        arm = m.bone(f"arm_{side}", body, ((5.5 + AX) * sx, 22, -10.5), (-30, 0, 0))
        fore = m.bone(f"forearm_{side}", arm, ((5.5 + AX) * sx, 16.5, -10.5), (105, 0, 0))
        m.bone(f"hand_{side}", fore, ((5.5 + AX) * sx, 10.5, -10.5), (10, 0, 0))
    m.pair("arm_l", "arm_r", (4 + AX, 16, -12), (7 + AX, 23, -9), name="humerus")
    m.pair("arm_l", "arm_r", (7.1 + AX, 16, -11), (7.1 + AX, 22, -6), name="tertials", mat="covert", faces=["east", "west"])
    m.pair("forearm_l", "forearm_r", (4.5 + AX, 10, -11.5), (6.5 + AX, 17, -9.5), name="forearm")
    m.pair("forearm_l", "forearm_r", (6.6 + AX, 10, -10.5), (6.6 + AX, 17, -5), name="secondaries", mat="wing", faces=["east", "west"])
    m.pair("forearm_l", "forearm_r", (6.8 + AX, 12, -10.5), (6.8 + AX, 17, -7), name="coverts", mat="covert", faces=["east", "west"])
    m.pair("hand_l", "hand_r", (4.6 + AX, 6, -11.4), (6.4 + AX, 11, -9.6), name="hand")
    m.pair("hand_l", "hand_r", (6.6 + AX, 4, -10.5), (6.6 + AX, 11, -5), name="primaries", mat="wing", faces=["east", "west"])
    m.pair("hand_l", "hand_r", (5.5 + AX, 1, -11.5), (6.5 + AX, 6, -10.5), name="claw_f2", mat="claw", rot=(-55, 0, 0), origin=(6 + AX, 6, -11))
    m.pair("hand_l", "hand_r", (4.5 + AX, 2.5, -11.5), (5.5 + AX, 6, -10.5), name="claw_f1", mat="claw", rot=(-55, 0, 0), origin=(5 + AX, 6, -11))
    m.pair("hand_l", "hand_r", (5 + AX, 3.5, -10.5), (6 + AX, 6, -9.5), name="claw_f3", mat="claw", rot=(-45, 0, 0), origin=(5.5 + AX, 6, -10))
    # legs: feathered drumstick, slender shin, long scaly metatarsus, toes III and IV on the ground, toe II up with the
    # sickle claw (6.5 cm on the fossil)
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (5.5 * sx, 26, 0.5), (40, 0, 0))
        sh = m.bone(f"shin_{side}", th, (5.5 * sx, 18, 0.5), (-88, 0, 0))
        mt = m.bone(f"foot_{side}", sh, (5.5 * sx, 7.5, 0.5), (62, 0, 0))
        m.bone(f"toes_{side}", mt, (5.5 * sx, -0.5, 0.5), (-14, 0, 0))
    m.pair("thigh_l", "thigh_r", (3, 17, -3), (8, 28, 4), name="thigh")
    m.pair("shin_l", "shin_r", (4, 12, -1.5), (7, 19, 2.5), name="shin")
    m.pair("shin_l", "shin_r", (4.5, 7, -1), (6.5, 12, 1.5), name="shank")
    m.pair("foot_l", "foot_r", (4.5, -1, -0.5), (6.5, 8, 1.5), name="meta")
    m.pair("toes_l", "toes_r", (4.5, -2, -8), (5.5, 0, 0.5), name="toe3")
    m.pair("toes_l", "toes_r", (5.5, -2, -7), (6.5, 0, 0.5), name="toe4")
    m.pair("toes_l", "toes_r", (4.5, -2, -9.5), (5.5, -0.5, -8), name="claw3", mat="claw")
    m.pair("toes_l", "toes_r", (5.5, -2, -8.5), (6.5, -0.5, -7), name="claw4", mat="claw")
    m.pair("toes_l", "toes_r", (3.5, -1, -3), (4.5, 1.5, 0.5), name="toe2")
    m.pair("toes_l", "toes_r", (3.5, 1, -6.5), (4.5, 2.5, -2.5), name="sickle", mat="claw")
    m.pair("toes_l", "toes_r", (3.5, -1.5, -7.5), (4.5, 1, -5.5), name="sickle_tip", mat="claw")
    # tail: a stiff rod in four sections; the frond fan on the last two, tilted into a shallow V
    t1 = m.bone("tail1", body, (0, 25, 6.5), (-4, 0, 0))
    m.cube(t1, (-3.5, 22, 6), (3.5, 28, 16), name="tail1")
    t2 = m.bone("tail2", t1, (0, 25, 15.5), (2, 0, 0))
    m.cube(t2, (-2.5, 23, 15.5), (2.5, 27, 28), name="tail2")
    t3 = m.bone("tail3", t2, (0, 25, 27.5), (1, 0, 0))
    m.cube(t3, (-1.5, 23.5, 27.5), (1.5, 26.5, 40), name="tail3")
    m.pair(t3, t3, (0, 25, 31), (4, 25, 40), name="fan3", mat="fan", faces=["up", "down"], rot=(0, 0, -10), origin=(0, 25, 35))
    t4 = m.bone("tail4", t3, (0, 25, 39.5), (1, 0, 0))
    m.cube(t4, (-1, 24, 39.5), (1, 26, 49), name="tail4")
    m.pair(t4, t4, (0, 25, 39.5), (5.5, 25, 56), name="fan4", mat="fan", faces=["up", "down"], rot=(0, 0, -12), origin=(0, 25, 48))
    if harness:
        add_harness(m, body)
    lo = min(p[:, 1].min() for c, p in geo.cube_points({"bones": m.bones, "cubes": m.cubes}) if c["mat"] not in ("teeth", "teeth_lo"))
    m.shift(-lo)
    single_face_planes(m)
    return m


def single_face_planes(m):
    """a cube with no thickness (crest, teeth, wing feathers, tail fan) keeps ONE face. GeckoLib draws entities without
    back-face culling, so the plane already shows from both sides; with two faces they sit in the same plane facing
    away from each other and z-fight (seen in game on the tail fan, 30/10). The kept face is the outer one: up for
    the fan, east (x+) on the left and centred cubes, west on the right-hand mirrors."""
    for c in m.cubes:
        d = [c["to"][k] - c["from"][k] for k in range(3)]
        if min(d) > 1e-6: continue
        ax = d.index(min(d))
        keep = {0: "east", 1: "up", 2: "south"}[ax]
        if ax == 0 and c["mirror_of"] is not None: keep = "west"
        c["faces"] = [keep]


def add_harness(m, body):
    """the hunting harness (not a saddle: a 20 kg animal carries nobody): a leather vest over the shoulders that
    wraps down both flanks, a chest strap in front of the keel, a bone plate on the withers and a ring for a lead"""
    hb = m.bone("saddle", body, (0, 29, -6))   # named "saddle" so DinoGeoModel shows it only on a harnessed raptor
    # the faces that lie on the body are left out: GeckoLib draws without back-face culling, so a face lying on the
    # torso fights with it. Careful with x: GeckoLib mirrors x once more on top of the bedrock flip that geo_json
    # writes, so in game a model "east" face lands on the -x side of its cube and "west" on the +x side. The inner
    # face of a strap on the +x flank is therefore "east" here (rc3 and rc4 dropped "west" and lost the outer face
    # instead; found in game on the Mac, 31/10). Only x is affected: north/south and up/down are as written.
    out = lambda *drop: [f for f in geo.FACES if f not in drop]
    m.cube(hb, (-5, 29, -12), (5, 30, -1), name="vest", mat="leather", faces=out("down"))
    m.pair(hb, hb, (4.5, 23, -12.5), (5.5, 29, -10), name="flank", mat="leather", faces=out("east"))
    # the girth lies where the legs swing forward (walk, stalk, kick); the shank (x 4.5-6.5) then wraps the whole
    # strap thickness, so the leg hides it and nothing pokes out. Moving it forward or up only meets the knee instead
    m.pair(hb, hb, (4.5, 19.5, -3.5), (5.5, 29, -1.5), name="girth", mat="strap", faces=out("east"))
    m.cube(hb, (-3.8, 16.5, -15), (3.8, 28, -14), name="chest_strap", mat="strap", faces=out("south"))
    m.cube(hb, (-2.5, 30, -10.5), (2.5, 31, -5), name="plate", mat="boneplate", faces=out("down"))
    m.cube(hb, (-0.5, 30, -4), (0.5, 33, -2.5), name="ring", mat="iron", faces=out("down"))


# ---------------------------------------------------------------- skin
def uv(t):
    if t.face in ("up", "down"): return t.L[2], t.L[0]
    return skin.face_uv_coords(t)


def plumage(t, base, seed=0):
    """contour feathers by form: staggered rows of small feathers (3 px wide, 2 tall) pointing down and back; the tip
    row of each is shadowed on its trailing side and some carry a lit leading edge"""
    u, v = uv(t)
    if t.face in ("up", "down"): u, v = t.L[2], t.L[0]
    row = math.floor(v / 2); off = 1.5 * (row % 2)
    c = math.floor((u + off + seed) / 3); i = (u + off + seed) - 3 * c; j = v - 2 * row
    if j < 1 and i >= 1: return PAL[DN[base]]
    if j >= 1 and i < 1 and h32(c, row, seed) % 4 == 0: return PAL[UP[base]]
    return PAL[base]


def bar(t):
    """the mark: dark bars slanting back from the spine, a warm rim on the front edge, tapering down the flank and
    broken in places; across the back they meet as chevrons"""
    if t.face not in ("east", "west", "up"): return None
    n = t.cube["name"]; v = t.rel[1]
    depth = 1.0 if t.face == "up" else (v - 0.3) / 0.7
    if depth <= 0: return None
    z = t.P[2] + 0.55 * (t.P[1] - 26) + (0.8 * abs(t.P[0]) if t.face == "up" else 0)
    per = 7.0 if not n.startswith("tail") else 6.0
    k = math.floor(z / per); z0 = k * per + 3
    half = (1.4 + (h32(k, 7) % 2) * 0.5) * (0.45 + 0.55 * depth)
    if half < 0.75: return None
    if h32(k, zlib.crc32(n.encode()) % 13) % 5 == 0: return None                               # a bar left out
    if h32(k, 3) % 3 == 0 and 0.35 < depth < 0.6: return None                                   # broken low on the flank
    dz = z - z0
    if abs(dz) <= half:
        if dz < -half + 1.0: return "r2" if depth > 0.5 else "r1"     # warm rim on the front edge
        return "k1" if depth > 0.45 else "d1"
    return None


def quill(t, h, tall_back=True):
    """a crest of longer feathers (alpha plane): spikes 2 px wide leaning back, dark with the blue sheen near the tip"""
    z = t.L[2] - t.cube["from"][2]; y = t.L[1] - t.cube["from"][1]
    L = t.cube["to"][2] - t.cube["from"][2]
    i = math.floor(z); f = z - i
    s = (z / max(1.0, L))
    top = h * ((0.55 + 0.45 * s) if tall_back else (1.0 - 0.45 * s))
    top -= (0.0, 1.2, 0.5, 1.6, 0.2, 0.9)[h32(i, 17) % 6]           # ragged: no two neighbours the same
    if i % 3 == 2: top -= 1.0
    top -= f * 0.8                                   # each feather leans back: its tip on the front edge
    if y > top: return None
    if y > top - 1: return PAL["u2"] if i % 2 == 0 else PAL["u1"]
    if y > top - 2: return PAL["u1"] if i % 2 == 0 else PAL["d1"]
    return PAL["k1"]


def scutes_leg(t, base="sc2"):
    k = math.floor(t.L[1] if t.face != "up" else t.L[2]) % 3
    if t.face in ("east", "west", "north", "south") and k == 0: return PAL[DN[base]] if t.i % 3 != 1 else PAL[base]
    if k == 2 and t.i % 3 == 0: return PAL[UP[base]]
    return PAL[base]


def shader(t):
    c = t.cube; n = c["name"]; f = t.face; p = PAL; mat = c["mat"]
    v = t.rel[1]
    if mat == "teeth":    # triangles hanging from the gum line, long and short alternating
        if f not in ("east", "west"): return None
        col = int(math.floor(t.L[2])); row = t.h - 1 - t.j   # row 0 = bottom
        k = (col + 300) % 2
        if k == 0: return (p["tooth"] if row > 0 else p["tooth2"]) if (row > 0 or h32(col, 5) % 2) else None
        return None
    if mat == "teeth_lo":
        if f not in ("east", "west"): return None
        col = int(math.floor(t.L[2]))
        return p["tooth2"] if col % 2 == 1 else None
    if mat == "claw":
        # pale horn with a dark root and a dark keel line: the claws are the brightest thing on the animal
        hi = (f in ("north", "up")) or (f in ("east", "west") and t.i == 0)
        if n.startswith("claw_f"):
            if t.j == 0 and f != "down": return p["claw"]
            return p["clawl"] if hi else p["claw2"]
        if n in ("sickle", "sickle_tip"):
            if f == "south" or (f in ("east", "west") and n == "sickle" and t.i == t.w - 1): return p["claw2"]
            return p["clawl"]
        return p["claw2"] if (f == "north" and t.j == t.h - 1) else p["claw"]
    if mat == "leather":
        edge = t.i in (0, t.w - 1) or t.j in (0, t.h - 1)
        if edge: return p["lea0"]
        return p["stitch"] if (f == "up" and (t.i + t.j) % 3 == 0) else p["lea1"]
    if mat == "strap": return p["lea0"] if t.i in (0, t.w - 1) else p["lea1"]
    if mat == "boneplate": return p["bone"] if (f == "up" and (t.i + t.j) % 4) else p["bone0"]
    if mat == "iron": return hx("8f8f88")
    if mat == "crest":
        return quill(t, c["to"][1] - c["from"][1], tall_back=(n != "crest_back"))
    if mat == "wing" or mat == "covert":
        # pennaceous feathers on a 0-thickness plane (alpha): two rows of texels per feather lying back from the bone
        # (+z); a lit edge row, a dark subterminal band and a pale tip on the flight feathers, the sheen on the coverts
        y0 = c["from"][1]; z0 = c["from"][2]; z1 = c["to"][2]; H = c["to"][1] - y0; L = z1 - z0
        along = t.L[2] - z0; yy = t.L[1] - y0; fe = math.floor(yy / 2); edge = (yy - 2 * fe) >= 1
        if n == "primaries": reach = L - fe * 1.2
        elif n == "secondaries": reach = L - 1 - (fe % 2) * 0.7
        else: reach = L - (fe % 2) * 1.0 - fe * 0.4
        if along > reach: return None
        if mat == "covert":
            if along > reach - 1: return p["u2"] if edge else p["u1"]
            return p["u1"] if edge else p["u0"]
        if along > reach - 1: return p["w2"] if n == "primaries" else p["d4"]
        if along > reach - 2.5: return p["k1"]
        return p["d3"] if edge else p["d2"]
    if mat == "fan":
        # the tail frond: feathers fanning out from the shaft, the sheen near the base, a dark band, pale tips
        x = abs(t.L[0]); z = t.L[2] - c["from"][2]; L = c["to"][2] - c["from"][2]; W = abs(c["to"][0] - c["from"][0])
        fe = math.floor(x)
        reach = L - (fe % 2) * 1.0 - max(0, fe - 2) * 0.8
        if z < (x - 1.0) * 2.0: return None             # the fan widens from the tail
        if z > reach: return None
        if z > reach - 1: return p["w2"]
        if z > reach - 3: return p["k1"]
        if x < 1.0: return p["d1"]
        return p["u1"] if (math.floor(z) + fe) % 3 else p["u0"]
    if mat == "brow":
        if f == "down": return p["k0"]
        if f == "up": return p["d2"] if (t.i + t.j) % 3 else p["d3"]
        return p["k1"] if t.j == t.h - 1 else (p["d3"] if t.j == 0 else p["d2"])
    if mat == "lid":
        return p["k1"] if t.j == t.h - 1 else p["d2"]
    if mat == "belly" or (f == "down" and n not in ("snout1", "snout2", "cranium", "nose", "jaw_back", "jaw_front")):
        return plumage(t, "b2" if (h32(math.floor(t.L[2]), math.floor(t.L[0])) % 7) else "b1", 1)
    # ---- bare skin: hands, legs and feet are scaly
    if n in ("shank", "meta", "toe3", "toe4", "toe2", "hand"):
        if f == "down" and n.startswith("toe"): return p["sc1"]          # pads
        return scutes_leg(t, "sc3" if f in ("north", "up") else "sc2")
    if n in ("jaw_back", "jaw_front"):
        if f == "up": return p["mouth"] if t.i in (0, t.w - 1) else (p["tongue"] if 1 <= t.i <= t.w - 2 and n == "jaw_back" else p["gum"])
        if f == "down": return p["b1"] if (t.i + t.j) % 3 else p["b0"]
        if t.j == 0: return p["k0"]                                       # the mouth line
        sc = skin.scales(*uv(t), cell=2.2, seed=31)
        base = "b0" if v < 0.5 else "sc2"
        return p[DN[base]] if sc == "edge" else (p[UP[base]] if sc == "hi" else p[base])
    if n in ("snout1", "snout2", "nose", "cranium", "cheek"):
        if f == "down": return p["mouth"] if n != "cheek" else p["b1"]
        if n == "cranium" and f == "up": return plumage(t, "d1", 2)
        if n == "cranium" and f in ("east", "west", "south") and v > 0.45: return plumage(t, "d2" if v < 0.8 else "d1", 3)
        if n == "cranium" and f == "south": return plumage(t, "d2", 3)
        if n == "cheek": return plumage(t, "d3" if v > 0.4 else "b0", 4)
        sc = skin.scales(*uv(t), cell=2.4, seed=zlib.crc32(n.encode()) % 97)
        base = "d2" if f == "up" else ("d3" if v > 0.6 else ("sc2" if v > 0.3 else "b0"))
        if f == "north": base = "d2"
        return p[DN[base]] if sc == "edge" else (p[UP[base]] if sc == "hi" else p[base])
    # ---- feathered body: umber back, tawny flanks with the bars, a cream belly under a ragged line
    if f == "up":
        base = "d2"
    elif f in ("east", "west", "north", "south"):
        jag = (0, 1, 1, 0, 2, 1)[int(math.floor(t.P[2])) % 6] / max(1, t.h)
        if n in ("torso", "rump", "neck", "neck2", "tail1") and v < 0.18 + jag: return plumage(t, "b1", 1)
        base = "d2" if v > 0.8 else ("d3" if v > 0.5 else "d4")
    else:
        base = "d3"
    if n in BARRED:
        b = bar(t)
        if b is not None: return p[b]
    if n == "thigh" and f in ("east", "west"):
        u_, w_ = skin.face_uv_coords(t)
        r = skin.ring(u_, w_, (c["from"][2] + c["to"][2]) / 2 + 0.5, c["from"][1] + 0.6 * (c["to"][1] - c["from"][1]), 3.2, 4.6)
        if r == "line": return p["d1"]
        if r == "hi": return p["d5"]
    return plumage(t, base, zlib.crc32(n.encode()) % 3)


def decals(img, m):
    C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
    pal = {"E": PAL["eye"], "e": PAL["eye2"], "Y": PAL["eye_hi"], "p": PAL["pupil"], "g": PAL["glint"], "D": PAL["k0"], "d": PAL["k1"],
           "o": PAL["sc1"], "O": PAL["sc0"], "n": PAL["k0"], "h": PAL["sc4"], "b": PAL["b2"], "B": PAL["b0"], "u": PAL["u1"], "U": PAL["u2"]}
    cr, s1, s2 = C["cranium"], C["snout1"], C["snout2"]
    # the eye: amber, a dark rim, a vertical pupil, a glint; sunk under the brow; a dark streak runs back from it
    P.stamp(img, m, cr, "east", ["DDDDDd..",
                                 "DYgYEDdd",
                                 "DYpEeD.d",
                                 "DEpeeD..",
                                 ".DDDD..."], pal, at=(1, 1))
    # antorbital fenestra: the shadowed recess on the side of the snout, a jugal highlight below the eye
    P.stamp(img, m, s1, "east", [".ooo..",
                                 "oOOoo.",
                                 ".oooo."], pal, at=(1, 1))
    P.stamp(img, m, cr, "east", ["hhhh"], pal, at=(1, 6))
    # nostril
    P.stamp(img, m, s2, "east", ["nn", "n."], pal, at=(0, 0))
    # lip scales over the mouth line (the mouth line itself is the jaw's top row)
    for sn in (s1, s2):
        w = sn["uv"]["east"][2]
        P.stamp(img, m, sn, "east", ["".join("bB"[(i // 1) % 2] for i in range(w))], pal, at=(0, 0), anchor="front-bottom")
    w = s2["uv"]["north"][2]
    P.stamp(img, m, s2, "north", ["n" + "." * (w - 2) + "n"], pal, at=(0, 1))
    # mouth interior: palate ridges
    for name in ("snout1", "snout2", "cranium"):
        c = C[name]; u, v, ww, hh = c["uv"]["down"]
        for j in range(hh):
            for i in range(ww):
                rim = i in (0, ww - 1)
                col = PAL["gum"] if rim or (i % 3 == 1 and j % 2 == 0) else PAL["mouth"]
                img[v + j, u + i] = (*col, 255)


def paint_sex(m, sex):
    keep = dict(PAL)
    try:
        if sex == "female": PAL.update(FEMALE)
        return P.paint(m, shader, [decals])
    finally:
        PAL.clear(); PAL.update(keep)


# ---------------------------------------------------------------- coplanar rule (as in the Pteranodon)
FACE_AX = {"east": ("to", 0, 1), "west": ("from", 0, -1), "up": ("to", 1, 1), "down": ("from", 1, -1),
           "south": ("to", 2, 1), "north": ("from", 2, -1)}


def _mirror_all(m):
    for c in m.cubes:
        src = c["mirror_of"]
        if src is not None:
            c["from"] = [-src["to"][0], src["from"][1], src["from"][2]]
            c["to"] = [-src["from"][0], src["to"][1], src["to"][2]]


def coplanar_pairs(m):
    for c in m.cubes: c["uv"] = {f: (0, 0, 1, 1) for f in c["faces"]}
    quads = []
    for c, f, cs, r in geo.faces({"bones": m.bones, "cubes": m.cubes}):
        pts = np.array([cs[k] for k in ((0, 0), (1, 0), (1, 1), (0, 1))])
        nrm = np.cross(pts[1] - pts[0], pts[3] - pts[0]); nn = np.linalg.norm(nrm)
        if nn > 1e-9: quads.append((c, f, pts, nrm / nn))
    out = []
    for i in range(len(quads)):
        c1, f1, p1, n1 = quads[i]
        for c2, f2, p2, n2 in quads[i + 1:]:
            if c1 is c2 or n1 @ n2 < 0.999 or abs((p2[0] - p1[0]) @ n1) > 0.01: continue
            e1 = p1[1] - p1[0]; e1 = e1 / np.linalg.norm(e1); e2 = np.cross(n1, e1)
            b1 = [(p1 @ e).min() for e in (e1, e2)] + [(p1 @ e).max() for e in (e1, e2)]
            b2 = [(p2 @ e).min() for e in (e1, e2)] + [(p2 @ e).max() for e in (e1, e2)]
            ox = min(b1[2], b2[2]) - max(b1[0], b2[0]); oy = min(b1[3], b2[3]) - max(b1[1], b2[1])
            if ox > 0.05 and oy > 0.05:
                out.append((c1, f1, c2, f2))
    for c in m.cubes: c.pop("uv", None)
    return out


def separate_coplanar(m, eps=0.05, rounds=6):
    def area(c, f):
        d = [c["to"][k] - c["from"][k] for k in range(3)]
        ax = FACE_AX[f][1]; return np.prod([d[k] for k in range(3) if k != ax])
    for _ in range(rounds):
        pairs = coplanar_pairs(m)
        if not pairs: return 0
        done = set()
        for c1, f1, c2, f2 in pairs:
            c, f = (c1, f1) if area(c1, f1) <= area(c2, f2) else (c2, f2)
            if c["mirror_of"] is not None:
                c = c["mirror_of"]; f = {"east": "west", "west": "east"}.get(f, f)
            if (id(c), f) in done: continue
            done.add((id(c), f))
            end, ax, sg = FACE_AX[f]
            if c["to"][ax] - c["from"][ax] < 1e-6:
                # a plane moves whole: thickening it would leave its one face on the far side in game, where
                # GeckoLib draws an x face (see add_harness), still in the plane it should leave (wing feathers)
                c["from"][ax] += sg * eps; c["to"][ax] += sg * eps
            else:
                c[end][ax] += sg * eps
        _mirror_all(m)
    return len(coplanar_pairs(m))
