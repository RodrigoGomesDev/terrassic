"""Pachycephalosaurus wyomingensis, made by hand from its own study (page "Paquicefalossauro: estudo e modelo",
02/11/2026, the third of the six remakes of the 1.5 package). Real size 4.5 m, about 450 kg (Paul 2010). Known
almost only from skulls (Brown & Schlaikjer 1943); the body follows its close relatives with skeletons, Stegoceras
and Homalocephale (Maryanska & Osmolska 1974; Sues & Galton 1987).

Drawn at 32 px = 1 m (game scale 0.5): the skull is about 0.6 m, so it gets 19 px for the dome, the knob rows, the
heavy brow over the eye and the short deep snout.

What makes it itself (each point from the study, none taken from another species of the mod):
- the HEAD leads the silhouette: a tall round dome of solid bone over the braincase, highest behind the eye and
  sloping smoothly forward onto the snout, dropping steeply at the back onto a shelf (the squamosal) set with a ring
  of blunt knobs; small blunt bosses on the snout; a heavy bony brow (the palpebrals) roofing a big eye;
- the GROWTH SERIES (Horner & Goodwin 2009): the young are flat-headed with long spikes at the back of the skull and
  on the snout (the "Dracorex" stage); the dome grows and the spikes are absorbed into knobs. In game the baby shows
  the bone "young_spikes" and hides "adult_dome" (DinoGeoModel);
- the dome of the male is taller than the female's (the two dome morphs of Stegoceras read as the sexes, Chapman et
  al. 1981: a hypothesis): the extra height sits on "adult_dome_male";
- a short thick neck in an S, carried so the head can be dropped into line with the back for a butt (Galton 1970;
  the healed lesions on the domes, Peterson et al. 2013);
- a very wide body: the broad hips and ribcage of the pachycephalosaurs, the gut carried back between the thighs
  into the deep root of the tail (Maryanska & Osmolska 1974);
- a stiff tail: from its middle back the tail was wrapped in a basket of ossified tendons (Brown & Schlaikjer 1943),
  so it moves at the root and the rest follows as one beam;
- a row of bristles along the top of the tail root, as on Psittacosaurus, a ceratopsian and so a close relative in
  the Marginocephalia (Mayr et al. 2002): a hypothesis;
- short arms with small five-fingered hands; legs of a walker, the shin a little longer than the thigh, four toes
  with blunt hoof-like claws (the first one small and high).

The colour ("castanha listrada", its own in docs/CORES.md): a forest animal of the Hell Creek floodplain woods. Rich
chestnut with thin pale stripes slanting down the flanks and the hips, the disruptive coat of the forest antelopes
(bongo, bushbuck) that breaks the outline in the dappled light; cream throat and belly, dark legs. The dome is a
display: on the male a pale horn colour with darker growth streaks running out from the crown, framed by the darker
knobs; on the female the dome takes the body colour and only its rim pales. Its own eye: pale olive-green iris deep
under the heavy brow.
"""
import math
import zlib

import proto as P
import skin
from proto import hx, h32

TEX_W = 256
PX_M = 32

# ------------------------------------------------------------------ palette (hue-shifted ramps: shadows lean
# red-violet, lights lean warm yellow)
PAL_M = {
    "d0": "3a220c", "d1": "5a3510", "d2": "7d4c14", "d3": "a0661a", "d4": "bf8326", "d5": "d6a347",
    "w0": "9c8a6e", "w1": "c2b08a", "w2": "d8c9a3", "w3": "e9dfc0",
    "l0": "1d1312", "l1": "2e1e1a", "l2": "433026", "l3": "5c4434",                   # dark legs
    "h0": "7d5a2a", "h1": "a8814a", "h2": "c4a36c", "h3": "d9c193", "h4": "ebdcb6",   # the male's bleached crown
    "n0": "3a2c22", "n1": "5a4636",                                                    # dome knobs and bosses
    "c0": "201816", "c1": "3a2e28",                                                    # claws
    "k0": "3d2e22", "k1": "5a4532", "k2": "6f5a44",                                    # beak keratin
}
PAL_F = dict(PAL_M)
PAL_F.update({   # the female: a duller, colder sepia, fewer and fainter stripes, the dome in body colour
    "d0": "301c0a", "d1": "4a2d0e", "d2": "683f12", "d3": "875617", "d4": "a16e20", "d5": "b98a33",
    "w0": "938670", "w1": "b4a689", "w2": "cabd9f", "w3": "dcd2b8",
    "h0": "4a2d0e", "h1": "683f12", "h2": "875617", "h3": "a16e20", "h4": "c4a476",
    "n0": "2a1c16", "n1": "433026",
})
EYE = {"lid": "160e0c", "sock": "2a1a14", "iris": "9aa466", "iris2": "6b7646", "pupil": "0d0b08", "glint": "f2ecd6",
       "brow": "4a2a1c"}


def pal_for(sex):
    src = PAL_M if sex == "male" else PAL_F
    p = {k: hx(v) for k, v in src.items()}
    p.update({k: hx(v) for k, v in EYE.items()})
    p["male"] = sex == "male"
    return p


# ------------------------------------------------------------------ geometry
REST = {   # bone rest angles (x: positive = the far end up for the neck and the tail, knee forward for the thigh)
    "neck1": 34, "neck2": -22, "skull": -14,
    "thigh": 16, "shin": -42, "foot": 34, "toes": -8,
    "arm": 24, "forearm": -84, "hand": 34,
    "tail1": -6, "tail2": 2, "tail3": 2, "tail4": 1, "tail5": 0, "tail6": 0,
}
OUT = lambda *d: [f for f in P.geo.FACES if f not in d]


def _ground(m):
    import geo
    lo = min(p[:, 1].min() for c, p in geo.cube_points({"bones": m.bones, "cubes": m.cubes})
             if c["mat"] not in ("bristle",) and not c["bone"].startswith("young"))
    m.shift(-lo)


# the dome profile, layer by layer (1 px tall, the sides stepping in by half a pixel): highest behind the eye, a
# long gentle slope forward over the bridge of the snout and a steep drop at the back onto the shelf. y, half width,
# front z, back z. Both sexes share the base; the female's crown ends low (6 px of dome, about 19 cm), the male's
# rises to 9 px (28 cm, the thickest domes known)
DOME = [(56, 5.0, -65, -47), (57, 5.0, -64, -47), (58, 5.0, -63, -47), (59, 4.5, -62, -48)]
CROWN_F = [(60, 4.0, -61, -49), (61, 3.0, -59, -50)]
CROWN_M = [(60, 4.5, -61, -48), (61, 4.5, -60, -49), (62, 4.0, -59, -50), (63, 3.0, -58, -51), (64, 2.0, -57, -52)]


def head(m, parent):
    """the skull, built along -z from the neck: braincase and cheeks, a short deep snout narrowing to a small beak,
    the heavy brow over the eye; the dome, the knob rows and the snout bosses on the adults' bones, the long spikes on
    the young's"""
    sk = m.bone("skull", parent, (0, 51.5, -50), (REST["skull"], 0, 0))
    # braincase and cheeks: wide at the back (the dome sits on it)
    m.cube(sk, (-5.5, 45, -61), (5.5, 56, -48), name="cranium")
    m.cube(sk, (-3, 46, -67), (3, 53, -61), name="snout")
    m.cube(sk, (-2, 46, -70), (2, 51, -67), name="muzzle")
    m.cube(sk, (-1.5, 46, -72), (1.5, 49, -70), name="beak", mat="beak")
    m.cube(sk, (-2.5, 53, -66), (2.5, 55, -61), name="nasal")             # the bridge rising toward the dome
    # the brow: a heavy shelf of bone over the eye, overhanging it to the side (the palpebrals)
    m.pair(sk, sk, (5.5, 52, -62), (6.5, 54, -56), name="brow")
    jaw = m.bone("jaw", sk, (0, 46.5, -52))
    m.cube(jaw, (-4.5, 42, -61), (4.5, 45, -50), name="jaw_back")
    m.cube(jaw, (-2.5, 42, -67), (2.5, 45, -61), name="jaw_mid")
    m.cube(jaw, (-1.5, 43, -71), (1.5, 45, -67), name="jaw_front", mat="beak")

    # ---- the adult dome and its knobs, hidden on the young. Few large steps, painted as one rounded mass: highest
    # behind the eye, a long slope forward onto the bridge, a steep drop at the back onto the shelf
    ad = m.bone("adult_dome", sk, (0, 56, -55))
    for k, (y, hw, zf, zb) in enumerate(DOME):
        m.cube(ad, (-hw, y, zf), (hw, y + 1, zb), name=f"dome{k}", mat="dome", faces=OUT("down") if k else None, ly=y)
    # the squamosal shelf behind the dome, its rim set with blunt knobs of different sizes (never an even row of
    # equal pale pins: that reads as teeth), the two at the back corners the biggest
    m.cube(ad, (-5, 52, -48), (5, 55, -46), name="shelf", mat="dome")
    knobs = [  # x0, y0, z0, sx, sy, sz (left side; mirrored)
        (4, 52.5, -46, 2, 2, 2), (1.5, 53, -46, 1, 1, 1), (5.5, 53.5, -50, 1, 2, 2), (5.5, 55.5, -53.5, 1, 1, 1),
        (5, 57.5, -57.5, 1, 1, 2), (4.5, 56.5, -62.5, 1, 1, 1)]
    for k, (x, y, z, a, b, c) in enumerate(knobs):
        m.pair(ad, ad, (x, y, z), (x + a, y + b, z + c), name=f"knob{k}", mat="knob")
    # the bosses on the snout: a low pair on the bridge and one over the nostrils
    m.pair(ad, ad, (1, 56, -66), (2, 57, -65), name="boss", mat="knob")
    m.cube(ad, (-0.5, 53, -69), (0.5, 54, -67), name="boss_front", mat="knob")
    # the female's crown (lower) and the male's (taller): the sexes' dome morphs (Chapman et al. 1981, a hypothesis)
    af = m.bone("adult_dome_female", ad, (0, 61, -55))
    for k, (y, hw, zf, zb) in enumerate(CROWN_F):
        m.cube(af, (-hw, y, zf), (hw, y + 1, zb), name=f"crown_f{k}", mat="dome", faces=OUT("down"), ly=y)
    am = m.bone("adult_dome_male", ad, (0, 61, -55))
    for k, (y, hw, zf, zb) in enumerate(CROWN_M):
        m.cube(am, (-hw, y, zf), (hw, y + 1, zb), name=f"crown_m{k}", mat="dome", faces=OUT("down"), ly=y)

    # ---- the young: flat-headed, with long spikes at the back of the skull and on the snout (Horner & Goodwin 2009)
    yg = m.bone("young_spikes", sk, (0, 56, -50))
    spikes = [  # x, y, z, length, pitch back (deg), splay out (deg)
        (4, 55, -48.5, 8, 60, 22), (2, 56, -49, 6, 48, 10), (5, 52.5, -50, 6, 78, 40)]
    for k, (x, y, z, ln, pitch, splay) in enumerate(spikes):
        m.pair(yg, yg, (x - 0.5, y, z - 0.5), (x + 0.5, y + ln, z + 0.5), name=f"spike{k}", mat="knob",
               rot=(pitch, 0, -splay), origin=(x, y, z))
    m.pair(yg, yg, (0.5, 55.5, -66), (1.5, 58.5, -65), name="nose_spike", mat="knob", rot=(-24, 0, -10), origin=(1, 55.5, -65.5))
    return sk


def neck(m, body):
    """short and thick, built straight along -z and bent into a low S by the rest angles"""
    n1 = m.bone("neck1", body, (0, 50, -32), (REST["neck1"], 0, 0))
    m.cube(n1, (-5.5, 45, -43), (5.5, 57, -30), name="neck1")
    n2 = m.bone("neck2", n1, (0, 51.5, -42), (REST["neck2"], 0, 0))
    m.cube(n2, (-4.5, 46.5, -51), (4.5, 56.5, -41), name="neck2")
    hd = m.bone("head", n2, (0, 51.5, -50))
    head(m, hd)


def arms(m, body):
    """short, with small five-fingered hands; held folded under the chest"""
    for side, sx in (("l", 1), ("r", -1)):
        a = m.bone(f"arm_{side}", body, (7 * sx, 44, -30), (REST["arm"], 0, 0))
        fa = m.bone(f"forearm_{side}", a, (7.5 * sx, 37, -30), (REST["forearm"], 0, 0))
        m.bone(f"hand_{side}", fa, (7.5 * sx, 31, -30), (REST["hand"], 0, 0))
    m.pair("arm_l", "arm_r", (6, 36, -31.5), (9, 46, -28.5), name="arm")
    m.pair("forearm_l", "forearm_r", (6.5, 30, -31), (8.5, 38, -29), name="forearm")
    m.pair("hand_l", "hand_r", (6.5, 27, -31.5), (8.5, 31, -28.5), name="hand")
    m.pair("hand_l", "hand_r", (6.5, 26, -31.5), (8.5, 27, -28.5), name="fingers", mat="claw")


def legs(m, body):
    """the walker's leg: a heavy thigh into the broad hip, the shin a little longer, a short metatarsus, three toes
    forward with blunt claws and the small first toe high on the inside"""
    for side, sx in (("l", 1), ("r", -1)):
        th = m.bone(f"thigh_{side}", body, (8 * sx, 48, 0), (REST["thigh"], 0, 2 * sx))
        sh = m.bone(f"shin_{side}", th, (8.5 * sx, 32, 0), (REST["shin"], 0, -3 * sx))
        ft = m.bone(f"foot_{side}", sh, (8.5 * sx, 16, -0.5), (REST["foot"], 0, 1 * sx))
        m.bone(f"toes_{side}", ft, (8.5 * sx, 7, -0.5), (REST["toes"], 0, 0))
    m.pair("thigh_l", "thigh_r", (4.5, 35, -6), (11.5, 54, 6), name="thigh")
    m.pair("thigh_l", "thigh_r", (5.5, 30, -4.5), (11.5, 36, 3.5), name="knee")
    m.pair("shin_l", "shin_r", (5.5, 23, -4), (11.5, 32, 3), name="calf")
    m.pair("shin_l", "shin_r", (6, 15, -3), (11, 24, 2), name="shin")
    m.pair("foot_l", "foot_r", (6.5, 6, -2.5), (10.5, 16, 1.5), name="meta")
    m.pair("toes_l", "toes_r", (7.5, 5, -8), (9.5, 7, 0), name="toe_mid")
    m.pair("toes_l", "toes_r", (9.5, 5, -6), (11.5, 7, 0), name="toe_out", rot=(0, -16, 0), origin=(9.5, 6, 0))
    m.pair("toes_l", "toes_r", (5.5, 5, -6), (7.5, 7, 0), name="toe_in", rot=(0, 16, 0), origin=(7.5, 6, 0))
    m.pair("toes_l", "toes_r", (7.5, 5, -10), (9.5, 6, -8), name="claw_mid", mat="claw")
    m.pair("toes_l", "toes_r", (10, 5, -8), (12, 6, -6), name="claw_out", mat="claw", rot=(0, -16, 0), origin=(9.5, 6, 0))
    m.pair("toes_l", "toes_r", (5, 5, -8), (7, 6, -6), name="claw_in", mat="claw", rot=(0, 16, 0), origin=(7.5, 6, 0))
    m.pair("foot_l", "foot_r", (5.5, 9, -1), (6.5, 11, 2), name="hallux", mat="claw")


def tail(m, body):
    """deep at the root (the gut runs back into it), then the stiff beam of the tendon basket; the bristles stand on
    the top of the root"""
    segs = [  # name, z0, z1, half width, y0, y1
        ("tail1", 10, 26, 7, 39, 59), ("tail2", 24, 37, 5.5, 42.5, 57.5), ("tail3", 35, 47, 4, 45, 55),
        ("tail4", 45, 56, 3, 46.5, 53.5), ("tail5", 54, 63, 2, 48, 52), ("tail6", 61, 68, 1, 49, 51)]
    parent = body
    for k, (n, z0, z1, hw, y0, y1) in enumerate(segs):
        b = m.bone(n, parent, (0, (y0 + y1) / 2, z0 + 2 if k else z0), (REST[n], 0, 0))
        m.cube(b, (-hw, y0, z0), (hw, y1, z1), name=n)
        parent = b
    # the bristles: a cut-out plane on the midline over the tail root (one face; GeckoLib draws it from both sides)
    m.cube("tail1", (0, 59, 12), (0, 64, 26), name="bristle1", mat="bristle", faces=["east"])
    m.cube("tail2", (0, 57.5, 24), (0, 61.5, 37), name="bristle2", mat="bristle", faces=["east"])
    m.cube("tail3", (0, 55, 35), (0, 58, 45), name="bristle3", mat="bristle", faces=["east"])


def build(saddle_on=False):
    m = P.Model("pachycephalosaurus")
    root = m.bone("root", None, (0, 0, 0))
    body = m.bone("body", root, (0, 48, 0))
    # the trunk: the chest narrower, the gut very wide, the hips broad and the highest point of the back
    m.cube(body, (-7, 37, -37), (7, 55, -22), name="chest")
    m.cube(body, (-9.5, 32, -24), (9.5, 58, -4), name="torso")
    m.cube(body, (-8.5, 30, -20), (8.5, 32, -7), name="belly", mat="belly")
    m.cube(body, (-9, 36, -6), (9, 61, 12), name="hips")
    neck(m, body)
    arms(m, body); legs(m, body); tail(m, body)
    _ground(m)
    return m


# ------------------------------------------------------------------ painting
# The rules against the "AI look" (Carnotaurus page): every mark has a cause in the animal, a short palette with
# hue-shifted ramps, borders that follow the body, one light from above, detail where the eye goes; the skin is always
# drawn scales (Rodrigo 01/11: smooth gradients read as AI).
UP = {"d0": "d1", "d1": "d2", "d2": "d3", "d3": "d4", "d4": "d5", "d5": "d5", "w0": "w1", "w1": "w2", "w2": "w3",
      "w3": "w3", "l0": "l1", "l1": "l2", "l2": "l3", "l3": "l3", "h0": "h1", "h1": "h2", "h2": "h3", "h3": "h4",
      "h4": "h4"}
DN = {"d5": "d4", "d4": "d3", "d3": "d2", "d2": "d1", "d1": "d0", "d0": "d0", "w3": "w2", "w2": "w1", "w1": "w0",
      "w0": "d4", "l3": "l2", "l2": "l1", "l1": "l0", "l0": "l0", "h4": "h3", "h3": "h2", "h2": "h1", "h1": "h0",
      "h0": "h0"}
LEGS = {"calf", "shin", "meta", "toe_mid", "toe_out", "toe_in", "hand", "forearm"}
# where the cream underside ends (fraction of the face height from the bottom)
UNDER = {"chest": 0.34, "torso": 0.2, "hips": 0.1, "neck1": 0.4, "neck2": 0.45, "tail1": 0.16, "tail2": 0.22,
         "tail3": 0.26, "tail4": 0.3, "tail5": 0.34, "tail6": 0.4, "cranium": 0.22, "snout": 0.28, "jaw_back": 1.0,
         "jaw_mid": 1.0}

# the stripes: thin pale lines slanting down and back over the flanks, hips and the tail root (bongo, bushbuck).
# z of the top end, length (fraction of the side's height), lean (px of z per px of y: + = the low end further back)
STRIPES_M = [(-19, 0.42, 0.10), (-14.5, 0.55, 0.14), (-10, 0.62, 0.18), (-5, 0.58, 0.22), (0, 0.66, 0.26),
             (4.5, 0.6, 0.3), (8.5, 0.52, 0.32), (13, 0.5, 0.3), (18, 0.44, 0.26), (23.5, 0.36, 0.22)]
STRIPES_F = [(-14.5, 0.4, 0.14), (-5, 0.46, 0.22), (4.5, 0.48, 0.3), (13, 0.4, 0.3), (23.5, 0.28, 0.22)]


def _uv(t):
    if t.face in ("up", "down"): return t.L[2], t.L[0]
    return skin.face_uv_coords(t)


def stripe_at(z, y, p, top_y, height):
    """True when the side texel (z, y) lies on a stripe. The lines are 1 px wide, wander a little and end at their
    own length; a stripe is broken where a scale seam crosses it (it lies on the scales, not over them)"""
    for k, (z0, ln, lean) in enumerate(STRIPES_M if p["male"] else STRIPES_F):
        depth = top_y - y
        if depth < 0 or depth > ln * height + (h32(k, 3) % 3) - 1: continue
        zc = z0 + lean * depth + 0.6 * math.sin(depth * 0.35 + k)
        if abs(z - zc) < 0.85: return True
    return False


def body_px(t, p):
    c = t.cube; n = c["name"]; f = t.face
    side = f in ("east", "west", "north", "south")
    u, v = _uv(t)
    seed = zlib.crc32(n.encode()) % 97
    rel = t.rel[1] if side else (1.0 if f == "up" else 0.0)
    sc = skin.scales(u, v, cell=5.4 if n not in ("cranium", "snout", "muzzle", "nasal", "neck2") else 3.8, seed=seed)
    if f == "down":
        base = "w1"
    elif side and n in UNDER and rel < UNDER[n] + 0.05 * math.sin((t.L[2] if f != "north" else t.L[0]) * 0.4 + seed) \
            and f in ("east", "west", "north"):
        base = "w2" if rel > UNDER[n] * 0.5 else "w1"
        if f == "north" and n.startswith("neck"): base = "w2"
    elif n == "belly":
        base = "w1"
    elif f == "up":
        base = "d2"
    else:
        zz = math.floor(t.L[2] / 3) * 3 if f in ("east", "west") else math.floor(t.L[0] / 3) * 3
        wob = 0.08 * math.sin(zz * 0.21 + seed) + 0.05 * math.sin(zz * 0.57)
        base = "d4" if rel < 0.45 + wob else ("d3" if rel < 0.82 + wob else "d2")
        if n in ("thigh", "knee"): base = "d3" if rel > 0.5 else "d4"
        if n in ("arm",): base = "d3"
    # the stripes on the flanks, the hips and the root of the tail (side faces only)
    if f in ("east", "west") and n in ("chest", "torso", "hips", "tail1", "tail2") and base.startswith("d"):
        top = c["to"][1]; hgt = c["to"][1] - c["from"][1]
        if n == "thigh":
            top, hgt = 58.0, 22.0
        if stripe_at(t.L[2], t.L[1], p, top, hgt):
            return p["w1"] if sc == "edge" else p["w3"]
    if sc == "edge": return p[DN[base]]
    if sc == "hi" and base.startswith("d") and rel > 0.5: return p[UP[base]]
    return p[base]


def leg_px(t, p):
    """the dark lower legs and forearms: rows of wide scales across the front of the shin and the metatarsus, small
    round ones on the sides; lit from above"""
    n = t.cube["name"]; f = t.face
    base = "l3" if f in ("north", "up") else "l2"
    if f == "down": return p["l0"]
    if f in ("north", "up") and n in ("shin", "meta", "toe_mid", "toe_out", "toe_in"):
        k = math.floor(t.L[1] if f != "up" else t.L[2]) % 3
        if k == 0: return p[DN[base]]
        return p[base]
    sc = skin.scales(*skin.face_uv_coords(t), cell=2.6, seed=zlib.crc32(n.encode()) % 97)
    return p[DN[base]] if sc == "edge" else p[base]


DOME_SIDE = {56: "d2", 57: "d3", 58: "d4", 59: "d5", 60: "h2", 61: "h2", 62: "h3", 63: "h3", 64: "h4"}
DOME_SIDE_F = {56: "d2", 57: "d3", 58: "d3", 59: "d4", 60: "d4", 61: "d5"}


def dome_px(t, p):
    """the dome: rough bone under the skin, painted as ONE rounded mass over its 1 px layers: the tone rises with the
    height (darker round the base where it grows out of the head, lighter at the crown), the half-pixel ledge on top
    of each layer catches the light, the surface is pitted (rugose) and, on the male, growth streaks run out from a
    pale crown (a display, Goodwin & Horner 2004). The female's dome stays in the head's colour"""
    f = t.face
    x, y, z = t.L
    yl = t.cube.get("ly", 56)
    zc = -55.5
    r = math.hypot(x / 4.5, (z - zc) / 8.5)
    if f == "down":
        return p["d1"]
    if f == "up":
        side = DOME_SIDE if p["male"] else DOME_SIDE_F
        base = UP[side.get(yl, "d4")]
        if p["male"] and yl >= 62: base = "h4" if r < 0.4 else "h3"
    else:
        base = (DOME_SIDE if p["male"] else DOME_SIDE_F).get(yl, "d3")
        if f == "south": base = DN[base]
    # growth streaks from the crown (male only), uneven in angle, broken
    if p["male"] and f == "up" and r > 0.25:
        ang = math.degrees(math.atan2(x, z - zc)) % 360
        k = int(ang // 45)
        if abs(ang - (k * 45 + 22 + (h32(k, 11) % 13) - 6)) < 5.0 and h32(int(r * 6), k) % 3:
            return p[DN[base]]
    # pits: now and then a darker texel, never in a row (the rugose bone)
    if h32(math.floor(x + 20), math.floor(z + 80), yl, f) % 9 == 0:
        return p[DN[base]]
    return p[base]


def knob_px(t, p):
    f = t.face
    if f == "up": return p["n1"]
    return p["n0"] if f in ("down", "south") else p["n1"]


def bristle_px(t, p):
    """the bristles on the tail root: a rank of stiff quills, one texel wide with a gap, their height swelling to the
    middle of the tail root and falling away behind (Psittacosaurus), each a little different; dark with a pale tip"""
    z = t.L[2]; y = t.L[1] - t.cube["from"][1]
    H = t.cube["to"][1] - t.cube["from"][1]
    i = int(math.floor(z))
    if i % 2: return None
    env = math.sin(math.pi * min(1.0, max(0.0, (z - 12) / 33.0))) ** 0.7
    reach = 1 + (H - 1) * env - (h32(i, 7) % 2)
    if y > reach: return None
    if y > reach - 1: return p["w0"]
    return p["d1"] if y < reach * 0.5 else p["d2"]


def shader_for(sex):
    p = pal_for(sex)

    def sh(t):
        mat = t.cube["mat"]; n = t.cube["name"]
        if mat == "bristle": return bristle_px(t, p)
        if mat == "dome": return dome_px(t, p)
        if mat == "knob": return knob_px(t, p)
        if mat == "claw": return p["c0"] if t.face != "up" else p["c1"]
        if mat == "beak":
            if t.face == "up": return p["k1"]
            if t.face == "down": return p["k0"]
            return p["k2"] if t.j == 0 else p["k1"]
        if n in LEGS: return leg_px(t, p)
        if n in ("muzzle",):
            if t.face == "down": return p["w1"]
            return p["d2"] if t.face != "up" else p["d3"]
        if n == "brow":
            return p["d3"] if t.face == "up" else (p["brow"] if t.face == "down" else p["d2"])
        return body_px(t, p)
    return sh


# the head, drawn face by face: east = the animal's left (mirrored to the right), column 0 the FRONT, row 0 the TOP
FACE_ART = {   # "." keeps the painted scales underneath
    ("cranium", "east"): [      # 13 wide x 11 tall: the eye under the brow, in a ring of smooth skin (the brow's
        ".............",        # shadow over it, the dark lid line, the iris in two tones, the pupil 2 px tall
        ".............",        # toward the snout with its glint, the dark socket); the ear opening behind; the pale
        "222222.......",        # cheek spot (as on a bongo) under the eye
        "3slllls3.....",
        "3sipgIs3.n...",
        "3sIpiIs3.n...",
        "33ssss33.....",
        "..3ww3.......",
        "..www........",
        ".............",
        "............."],
    ("snout", "east"): [        # 6 x 7: the nostril high at the front, the dark edge of the beak
        "......",
        "n.....",
        "n.....",
        "......",
        "......",
        "kkkkk.",
        "......"],
}


def decals_for(sex):
    p = pal_for(sex)
    cmap = {"2": p["d2"], "3": p["d3"], "4": p["d4"], "w": p["w1"], "s": p["sock"], "l": p["lid"], "i": p["iris"],
            "I": p["iris2"], "p": p["pupil"], "g": p["glint"], "n": p["d0"], "k": p["k1"]}

    def dec(img, m):
        C = {c["name"]: c for c in m.cubes if c["mirror_of"] is None}
        for (name, face), rows in FACE_ART.items():
            c = C.get(name)
            if not c or face not in c["uv"]: continue
            u, v, w, h = c["uv"][face]
            if w <= 0: continue
            assert (len(rows), len(rows[0])) == (h, w), (name, face, (w, h), (len(rows[0]), len(rows)))
            P.stamp(img, m, c, face, rows, cmap, at=(0, 0))
    return dec


def _clean(img, m):
    import qa
    qa.clean_orphans(img, m, cutout=("bristle",), keep=())


def paint_sex(m, sex="male"):
    return P.paint(m, shader_for(sex), decals=(decals_for(sex), _clean))


def preview_faces(m):
    """for previews only: swap east/west on the cubes that drop one of them"""
    for c in m.cubes:
        f = c["faces"]
        if ("east" in f) != ("west" in f):
            c["faces"] = [{"east": "west", "west": "east"}.get(x, x) for x in f]
    return m
