"""Dakotaraptor steini, made by hand from its own study (page "1.9: estudos do Quetzalcoatlus, do Edmontossauro e do
Dakotaraptor", approved by Rodrigo on 06/11/2026). 4.4 to 5.5 m, 220 to 350 kg (DePalma et al. 2015), Hell Creek.

Drawn at 20 px = 1 m (game scale 0.8). Not a big Velociraptor: the Velociraptor of the mod is a small long-snouted
hunter with an upturned nose; this one is a heavy cursor of the floodplain, and every proportion is its own:
- the HEAD: no skull of Dakotaraptor is known; it is drawn after its big relatives (Dromaeosaurus, Utahraptor): DEEP
  and boxy, a short tall snout with a straight top, a heavy jaw, a strong brow; no upturned tip;
- the LEGS long for its size (a runner: the long shin of the holotype), the second toe raised with the great SICKLE
  claw (24 cm with its sheath, the largest of the eudromaeosaurs);
- the ARMS long and the WINGS large: the quill knobs on the ulna (DePalma et al. 2015) held big feathers, here a
  broad wing of secondaries and primaries in two layers, barred and white-tipped;
- a thick neck in a gentle S, a deep chest, a long stiff tail with a narrow fan of feathers at the end, a crest of
  short plumes along the back of the head and the nape.
A note kept from the study: part of the original skeleton was a turtle bone (Arbour et al. 2016) and some think the
find is mixed; the rest is still a big raptor.

The colour ("castanho escuro", docs/CORES.md): a dark chestnut back, the flanks a warmer brown, a pale ash throat,
chest and belly (ash grey rather than cream: cream was the Velociraptor's, colourcheck); the wing and tail feathers barred dark with pale tips; the male's face with a dark band through the
eye. The female an ashier brown, her face plain.
"""
import math
import zlib

import proto as P
import skin
from proto import hx, h32

TEX_W = 256
PX_M = 20

PAL_M = {
    "d0": "1c0f0b", "d1": "2c1712", "d2": "42211a", "d3": "5a2e24", "d4": "723e30", "d5": "8a5040",   # chestnut
    "b0": "7e7a74", "b1": "98948c", "b2": "aeaaa2", "b3": "c4c0b8",                                  # ash-grey under
    "q0": "1a0e0a", "q1": "3a1e16", "q2": "e8dcc8", "q3": "b8a48c",                                  # barred quills
    "m0": "140a08",                                                                                  # face band
    "sc0": "241c18", "sc1": "3a2e26", "sc2": "54443a", "sc3": "706052",                              # bare legs
    "claw": "16100e", "clawl": "6a5a4e",
    "tooth": "efe6d0", "mouth": "3a1612",
    "eye": "d89a2a", "eye2": "8e5a18", "pupil": "0a0706", "glint": "fff2cc",
}
PAL_F = dict(PAL_M)
PAL_F.update({    # the female: an ashier brown, the face plain
    "d0": "1c1612", "d1": "2c241e", "d2": "40342c", "d3": "564840", "d4": "6e5e52", "d5": "867466",
    "q1": "3a302a", "m0": "40342c",
})
UP = {"d0": "d1", "d1": "d2", "d2": "d3", "d3": "d4", "d4": "d5", "d5": "d5", "b0": "b1", "b1": "b2", "b2": "b3", "b3": "b3"}
DN = {"d5": "d4", "d4": "d3", "d3": "d2", "d2": "d1", "d1": "d0", "d0": "d0", "b3": "b2", "b2": "b1", "b1": "b0", "b0": "d5"}


def pal_for(sex):
    return {k: hx(v) for k, v in (PAL_M if sex == "male" else PAL_F).items()}


REST = {
    "neck1": 34, "neck2": -26, "skull": -10,
    "thigh": 34, "shin": -80, "foot": 60, "toes": -14,
    "arm": -100, "forearm": 80, "hand": -140,   # the wing folded on the flank, the tips back
    "tail1": -6, "tail2": 2, "tail3": 2, "tail4": 1, "tail5": 1,
}
HIP = (0, 30, 0)
FEATHER = ("crest", "wing", "covert", "fan")


def _ground(m):
    import geo
    lo = min(p[:, 1].min() for c, p in geo.cube_points({"bones": m.bones, "cubes": m.cubes})
             if c["mat"] not in ("teeth", "teeth_lo") + FEATHER)
    m.shift(-lo)


def head(m, parent):
    """deep and boxy, after Dromaeosaurus and Utahraptor: a tall braincase, a short tall snout with a straight top, a
    heavy lower jaw, a strong brow, a crest of short plumes behind the eye"""
    sk = m.bone("skull", parent, (0, 31, -43), (REST["skull"], 0, 0))
    m.cube(sk, (-4.5, 25, -53), (4.5, 35, -42), name="cranium")
    m.cube(sk, (-3.5, 26, -61), (3.5, 34, -52), name="snout1")
    m.cube(sk, (-3, 26, -67), (3, 32, -60), name="snout2")
    m.pair(sk, sk, (3.4, 33, -53), (5.4, 35, -46), name="brow", mat="brow")
    m.pair(sk, sk, (4, 25.5, -50), (5, 28.5, -44), name="cheek")   # under the eye, not over it
    m.cube(sk, (0, 35, -51), (0, 39, -41), name="crest_head", mat="crest", faces=["east"])
    # the upper teeth: alpha planes outside the lower jaw, they show with the mouth shut
    m.pair(sk, sk, (2.6, 24, -66), (2.6, 26, -60), name="teeth_up", mat="teeth")
    m.pair(sk, sk, (3.1, 24, -60), (3.1, 26, -53), name="teeth_up2", mat="teeth")
    jaw = m.bone("jaw", sk, (0, 26, -45))
    m.cube(jaw, (-4, 22, -53), (4, 26, -43), name="jaw_back")
    m.cube(jaw, (-2.5, 22, -66), (2.5, 25, -53), name="jaw_front")
    m.pair(jaw, jaw, (2.0, 25, -65), (2.0, 26, -54), name="teeth_lo", mat="teeth_lo")
    return sk


def neck(m, body):
    n1 = m.bone("neck1", body, (0, 31, -22), (REST["neck1"], 0, 0))
    m.cube(n1, (-4, 27, -34), (4, 35, -21), name="neck1")
    m.cube(n1, (-3, 25, -32), (3, 27, -23), name="throat1", mat="belly")
    m.cube(n1, (0, 35, -34), (0, 39, -21), name="crest_neck", mat="crest", faces=["east"])
    n2 = m.bone("neck2", n1, (0, 31, -33), (REST["neck2"], 0, 0))
    m.cube(n2, (-3.5, 27.5, -44), (3.5, 34.5, -32), name="neck2")
    m.cube(n2, (0, 34.5, -44), (0, 37.5, -32), name="crest_neck2", mat="crest", faces=["east"])
    hd = m.bone("head", n2, (0, 31, -43))
    head(m, hd)


def arms(m, body):
    """long arms carried folded and ready, three clawed fingers, and a big wing in two layers: secondaries under the
    forearm, primaries under the hand, coverts over them (the quill knobs of the holotype)"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (6.3 * sx, 27, -18), (REST["arm"], 0, 0))
        fa = m.bone(f"forearm_{side}", a, (6.3 * sx, 18, -18), (REST["forearm"], 0, 0))
        m.bone(f"hand_{side}", fa, (6.3 * sx, 9, -18), (REST["hand"], 0, 0))
    m.pair("arm_l", "arm_r", (4.8, 17, -20), (7.8, 29, -16), name="humerus")
    m.pair("forearm_l", "forearm_r", (5.3, 8, -19.5), (7.3, 19, -16.5), name="forearm")
    m.pair("forearm_l", "forearm_r", (7.4, 4, -18), (7.4, 19, 0), name="secondaries", mat="wing", faces=["east"])
    m.pair("forearm_l", "forearm_r", (7.6, 11, -18), (7.6, 19, -8), name="coverts", mat="covert", faces=["east"])
    m.pair("hand_l", "hand_r", (5.4, 2, -19.4), (7.4, 9, -16.4), name="hand")
    m.pair("hand_l", "hand_r", (7.4, -6, -18), (7.4, 9, 2), name="primaries", mat="wing", faces=["east"])
    for k, (x0, ln, rot) in enumerate(((5.4, 4, -50), (6.2, 5, -55), (5.8, 3, -40))):
        m.pair("hand_l", "hand_r", (x0, 2 - ln, -19.4), (x0 + 1, 2, -18.4), name=f"claw_f{k}", mat="claw",
               rot=(rot, 0, 0), origin=(x0 + 0.5, 2, -19))


def legs(m, body):
    """the runner's leg: a big feathered drumstick, a long shin, a long scaly metatarsus, toes III and IV on the ground,
    toe II raised with the great sickle claw"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (7 * sx, 30, 0), (REST["thigh"], 0, 0))
        sh = m.bone(f"shin_{side}", th, (7 * sx, 17, 0), (REST["shin"], 0, 0))
        ft = m.bone(f"foot_{side}", sh, (7 * sx, 2, 0), (REST["foot"], 0, 0))
        m.bone(f"toes_{side}", ft, (7 * sx, -8, 0), (REST["toes"], 0, 0))
    m.pair("thigh_l", "thigh_r", (4, 15, -5), (10, 33, 5), name="thigh")
    m.pair("shin_l", "shin_r", (5, 1, -2.5), (9, 18, 2.5), name="shin")
    m.pair("foot_l", "foot_r", (5.5, -9, -1.5), (8.5, 3, 1.5), name="meta")
    m.pair("toes_l", "toes_r", (6.4, -10, -9), (8.4, -8, 1), name="toe3")
    m.pair("toes_l", "toes_r", (8.6, -10, -8), (10.6, -8, 1), name="toe4")
    m.pair("toes_l", "toes_r", (6.4, -10, -11), (8.4, -8, -9), name="claw3", mat="claw")
    m.pair("toes_l", "toes_r", (8.6, -10, -10), (10.6, -8, -8), name="claw4", mat="claw")
    # toe II held up off the ground, the sickle on it curving down and forward
    m.pair("toes_l", "toes_r", (4.4, -8, -3), (6.4, -5, 1), name="toe2")
    m.pair("toes_l", "toes_r", (4.5, -6, -8), (6.5, -3, -3), name="sickle", mat="claw")
    m.pair("toes_l", "toes_r", (4.5, -9, -9.5), (6.5, -6, -7.5), name="sickle_tip", mat="claw")


def tail(m, body):
    """long and stiff (ossified rods along it), held level, with a narrow fan of barred feathers at the end"""
    segs = [("tail1", 6, 18, 5, 24, 34), ("tail2", 17, 29, 4, 25, 33), ("tail3", 28, 40, 3, 26, 32),
            ("tail4", 39, 50, 2, 27, 31), ("tail5", 49, 58, 1.5, 27.5, 30.5)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 1 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b
        if n in ("tail4", "tail5"):
            m.pair(b, b, (0, (y0 + y1) / 2, z0), (4 if n == "tail4" else 5, (y0 + y1) / 2, z1 + (5 if n == "tail5" else 0)),
                   name=f"fan_{n}", mat="fan", faces=["up"], rot=(0, 0, -10), origin=(0, (y0 + y1) / 2, z0))


SADDLE_MATS = ("pad", "leather", "strap", "bone")


def saddle(m, body):
    """Its own light hunting saddle: a short pad over the hips (a fast rider leans forward), a low seat, knee rolls, a
    bone grip on the neck base, the girth in front of the thighs; nothing on the wings"""
    out = lambda *d: [f for f in P.geo.FACES if f not in d]
    sd = m.bone("saddle", body, (0, 36, -10))
    m.cube(sd, (-6, 36, -18), (6, 37, -2), name="pad", mat="pad", faces=out("down"))
    m.cube(sd, (-4, 37, -14), (4, 38, -4), name="seat", mat="leather", faces=out("down"))
    m.cube(sd, (-4, 38, -5), (4, 40, -3), name="cantle", mat="leather")
    m.pair(sd, sd, (3, 37, -15), (6, 39, -11), name="knee_roll", mat="leather")
    m.cube(sd, (-1, 37, -21), (1, 40, -19), name="grip", mat="bone")
    m.pair(sd, sd, (6, 23, -9), (7, 36, -7), name="girth", mat="strap", faces=out("west"))
    m.cube(sd, (-6, 22, -9), (6, 23, -7), name="girth_under", mat="strap", faces=out("up"))


def build(saddle_on=True):
    m = P.Model("dakotaraptor")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, HIP)
    # a deep chest, the back level, a narrow rump; a low crest of plumes down the middle of the back
    m.cube(body, (-6, 24, -24), (6, 36, 0), name="torso")
    m.cube(body, (-5, 21, -24), (5, 25, -9), name="keel", mat="belly", rot=(-8, 0, 0), origin=(0, 25, -9))
    m.cube(body, (-5, 26, -1), (5, 35, 8), name="rump")
    m.cube(body, (0, 36, -20), (0, 39, 4), name="crest_back", mat="crest", faces=["east"])
    neck(m, body)
    arms(m, body); legs(m, body); tail(m, body)
    if saddle_on:
        saddle(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ painting
UNDER = {"torso": 0.32, "rump": 0.28, "neck1": 0.45, "neck2": 0.45, "tail1": 0.25, "tail2": 0.3, "tail3": 0.35,
         "tail4": 0.4, "tail5": 0.4, "cranium": 0.3, "snout1": 0.35, "snout2": 0.4, "jaw_back": 1.0, "jaw_front": 1.0}
BARE = {"shin", "meta", "toe2", "toe3", "toe4", "hand"}


def _uv(t):
    if t.face in ("up", "down"): return t.L[2], t.L[0]
    return skin.face_uv_coords(t)


def plumage(t, base, p, seed=0):
    """small contour feathers: staggered rows of 3 x 2, the tip row shaded, a lit leading edge now and then"""
    u, v = _uv(t)
    row = math.floor(v / 2); off = 1.5 * (row % 2)
    c = math.floor((u + off + seed) / 3); i = (u + off + seed) - 3 * c; j = v - 2 * row
    if j < 1 and i >= 1: return p[DN[base]]
    if j >= 1 and i < 1 and h32(c, row, seed) % 4 == 0: return p[UP[base]]
    return p[base]


def quill_px(t, p, sex):
    """wing and tail feathers: each 1 px quill along its length, barred dark across (2 px bands) with a pale tip"""
    n = t.cube["name"]; c = t.cube
    if n.startswith("fan"):
        along = t.L[2] - c["from"][2]; L = c["to"][2] - c["from"][2]
        across = abs(t.L[0])
        if along > L - 1.2 - 0.8 * across: return p["q2"] if along > L - 2.5 - 0.8 * across else p["q1"]
        if along > L - 0.6 * across: return None
        return p["q0"] if (math.floor(along) // 2) % 2 == 0 else p["q1"]
    z = t.L[2] - c["from"][2]; y = t.L[1] - c["from"][1]
    D = c["to"][2] - c["from"][2]; H = c["to"][1] - c["from"][1]
    s = y / H                                       # 0 at the bottom (the feather tips), 1 at the bone
    reach = D * (0.55 + 0.45 * math.sin(math.pi * min(1.0, 0.25 + s * 0.9)))
    if n == "coverts": reach = D * (0.7 + 0.3 * s)
    reach -= (0, 0.6, 0.2, 1.0, 0.4)[int(math.floor(y)) % 5]
    if z > reach: return None
    if n == "coverts":
        return p["d3"] if (math.floor(y) + math.floor(z)) % 3 else p["d2"]
    if z > reach - 1.5: return p["q2"] if int(math.floor(y)) % 2 == 0 else p["q3"]       # the pale tips
    return p["q0"] if (math.floor(z) // 2) % 2 == 0 else p["q1"]


def crest_px(t, p):
    i = int(math.floor(t.L[2]))
    top = t.cube["to"][1] - t.cube["from"][1]; y = t.L[1] - t.cube["from"][1]
    drop = (0.0, 1.0, 0.5, 2.0, 1.0, 2.5, 0.5, 1.5)[(i + h32(i // 2, 7) % 5) % 8]
    if y > top - drop: return None
    return p["d1"] if (i + h32(i, 8) % 3) % 3 else p["d3"]


def body_px(t, p, sex):
    c = t.cube; n = c["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    seed = zlib.crc32(n.encode()) % 7
    rel = t.rel[1] if side else (1.0 if f == "up" else 0.0)
    if f == "down" or c["mat"] == "belly":
        return plumage(t, "b1", p, seed)
    if side and n in UNDER and f in ("east", "west", "north"):
        col = math.floor((t.L[2] if f != "north" else t.L[0] + 8) / 2)
        line = UNDER[n] + 0.05 * math.sin(col * 0.7 + seed) + (h32(col, seed) % 3) / max(1, t.h) * 0.6
        if f == "north" and n.startswith("neck"): line = 1.0          # the throat pale all the way up
        if rel < line:
            return plumage(t, "b2" if rel > line * 0.5 else "b1", p, seed)
    if n in ("cranium", "snout1") and f in ("east", "west") and sex == "male" and 0.45 < rel < 0.7:
        return p["m0"] if (t.i + t.j) % 5 else p["d1"]               # the dark band through the eye
    if f == "up":
        base = "d2" if n in ("torso", "rump", "neck1", "tail1") else "d3"
    else:
        wob = 0.06 * math.sin(math.floor(t.L[2]) * 0.4 + seed)
        base = "d4" if rel < 0.55 + wob else ("d3" if rel < 0.85 + wob else "d2")
        if n in ("thigh",): base = "d3" if rel > 0.35 else "d4"
        if n in ("humerus", "forearm"): base = "d3"
    return plumage(t, base, p, seed)


def bare_px(t, p):
    """the bare feet and hands: big scutes across the front, small scales on the sides"""
    n = t.cube["name"]; f = t.face
    if n == "shin" and t.rel[1] > 0.5 and f != "down":
        return p["d3"] if (math.floor(t.L[1]) + math.floor(t.L[2])) % 3 else p["d2"]   # feathered upper shin
    base = "sc2" if f in ("north", "up") else "sc1"
    if f == "down": return p["sc0"]
    if f in ("north", "up"):
        return p["sc0"] if math.floor(t.L[1] if f != "up" else t.L[2]) % 3 == 0 else p[base]
    sc = skin.scales(*skin.face_uv_coords(t), cell=2.2, seed=zlib.crc32(n.encode()) % 97)
    if sc == "edge": return p["sc0"]
    if sc == "hi": return p["sc3"]
    return p[base]


def saddle_px(t):
    mat = t.cube["mat"]; f = t.face; i, j, w, h = t.i, t.j, t.w, t.h
    if mat == "pad":
        if f == "up" and (i in (0, w - 1) or j in (0, h - 1)): return hx("2a2420")
        return hx("6a6050") if (i + 2 * j) % 5 else hx("54493c")
    if mat == "leather":
        if f == "up" and (i in (0, w - 1) or j in (0, h - 1)): return hx("2e1d14")
        return hx("5e3e28") if (i + j) % 4 else hx("4a2f1f")
    if mat == "bone": return hx("e2d8bd") if f == "up" else hx("b8ac90")
    return hx("3a2618") if (i + j) % 3 else hx("2a1c12")


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        mat = t.cube["mat"]
        if mat in SADDLE_MATS: return saddle_px(t)
        if mat in ("wing", "covert", "fan"): return quill_px(t, p, sex)
        if mat == "crest": return crest_px(t, p)
        if mat == "claw": return p["clawl"] if t.face in ("north", "up") and t.j == 0 else p["claw"]
        if mat in ("teeth", "teeth_lo"):
            return p["tooth"] if (t.i % 2 == 0) else None
        if mat == "brow":
            return p["d1"] if t.face != "up" else p["d3"]
        n = t.cube["name"]
        if n in BARE: return bare_px(t, p)
        return body_px(t, p, sex)
    return sh


FACE_ART = {
    ("cranium", "east"): [      # 11 wide x 10 tall (column 0 the front): the eye high in the deep skull, amber, a dark
        "...........",          # lid line over it under the brow
        "...........",
        ".llllll....",
        "lYYgpYl....",
        "lYpppYl....",
        ".lYYYl.....",
        "...........",
        "...........",
        "...........",
        "..........."],
}


def decals_for(sex):
    p = pal_for(sex)
    cmap = {"l": p["d0"], "Y": p["eye"], "y": p["eye2"], "p": p["pupil"], "g": p["glint"]}

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        for (name, face), rows in FACE_ART.items():
            c = C.get(name)
            if not c or face not in c["uv"]: continue
            u, v, w, h = c["uv"][face]
            assert (len(rows), len(rows[0])) == (h, abs(w)), (name, face, (w, h))
            P.stamp(img, m, c, face, rows, cmap, at=(0, 0))
    return dec


def _clean(img, m):
    import qa
    qa.clean_orphans(img, m, cutout=FEATHER + ("teeth", "teeth_lo"), keep=("teeth", "teeth_lo"))


def paint_sex(m, sex="male"):
    return P.paint(m, shader_for(sex), decals=(decals_for(sex), _clean))
