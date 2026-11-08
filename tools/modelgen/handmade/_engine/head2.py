"""The head of the "padrão v2" (docs/estudos/14_POR_QUE_PARECE_IA.md, section "Padrão v2", 08/11/2026): the pieces the
four 1.10.1 predators share, so each species' file keeps only what is its own (the shape, the ornaments, the marks).

- the face is the focus: small scales and rugosity laid in BODY space (continuous over the cubes), one tone step;
- the teeth show: an upper row hung just outside the lower jaw, the lips covering only its base, a dark mouth line;
- the eye sits in a socket: a dark rim, an iris of the species' colour of 2 texels, a pupil and a glint, under a
  brow (a cube or a drawn shelf);
- the body keeps the v1 calm but carries its own scales at one tone step (body_scales).

Checked by headcheck.py in every build.
"""
import math

import skin
import skin2
from proto import h32


# ------------------------------------------------------------------ the skin of the face
def face_scale(t, cell=2.4, seed=0, lift=4):
    """-1, 0 or +1 tone step for small scales over the face in body space: the seam on the shaded side of each scale
    one step darker, one scale in `lift` raised one step lighter (a tubercle). Continuous from cube to cube."""
    u, v = skin2.surface_uv(t)
    uc, vc = math.floor(u) + 0.5, math.floor(v) + 0.5
    d1, d2, (cx, cy, px, py) = skin.voronoi(uc, vc, cell, seed)
    if d2 - d1 < 0.8 and (uc - px > -0.5 or vc - py < 0.5):
        return -1
    if h32(cx, cy, seed, 3) % lift == 0:
        return 1
    return 0


def rugose(t, seed=0, every=3):
    """-1, 0 or +1 for sculpted bone under skin (the rugose nasals, the maxilla of an abelisaurid or of a
    carcharodontosaurid): short ridges along the length of the snout broken by pits, in body space"""
    u, v = skin2.surface_uv(t)
    iu, iv = math.floor(u), math.floor(v)
    if t.face in ("up", "down"):
        iu, iv = math.floor(t.P[2]), math.floor(t.P[0])
    run = h32(iu // 3, iv, seed, 5) % every
    if run == 0 and (iu + iv) % 3 != 2:
        return -1                      # a groove
    if h32(iu, iv, seed, 6) % 7 == 0:
        return 1                       # a knob catching the light
    return 0


def body_scales(t, cell=4.0, seed=0, flat=0.55):
    """the body's own scales at one tone step: -1 on the shaded seam of each scale (a thin one: `flat` < 0.9 keeps
    the seam to about one texel), 0 elsewhere (skin2.scales)"""
    return -1 if skin2.scales(t, cell=cell, seed=seed, flat=flat) == "edge" else 0


# ------------------------------------------------------------------ the teeth (alpha planes)
def teeth_up(t, p, every=2, long_every=3, seed=11, gap_every=0):
    """the upper row seen with the mouth shut: the plane hangs just outside the lower jaw, its top row under the lip.
    Row 0 the base (the lips' shadow, a darker tooth), rows 1.. the crown; a long tooth every `long_every` columns,
    one column in `every` empty (the gaps between teeth); gap_every: a lost tooth now and then"""
    if t.face not in ("east", "west"):
        return None
    col = int(math.floor(t.L[2])); row = t.j
    if (col + 40) % every:
        return None
    if gap_every and h32(col, seed, 4) % gap_every == 0:
        return None
    size = t.h if h32(col, seed) % long_every == 0 else t.h - 1      # rows of this tooth
    if row >= size:
        return None
    if row == 0 and size > 1:
        return p["tooth2"]           # the base, in the lip's shadow
    return p["tooth"]


def teeth_lo(t, p):
    """the lower row inside the snout (shows with the mouth open)"""
    if t.face not in ("east", "west"):
        return None
    col = int(math.floor(t.L[2])); row = t.j
    if row == t.h - 1:
        return p["gum"]
    if (col + 41) % 2 == 0 and row >= (0 if h32(col, 13) % 3 else 1):
        return p["tooth2"] if row == 0 else p["tooth"]
    return None


# ------------------------------------------------------------------ the eye
# east = the animal's left (mirrored onto the right); column 0 at the FRONT, row 0 at the TOP.
# r the dark socket rim, i the iris (the species' colour), p the pupil, g the glint, c the iris' darker lower edge
EYE_ROUND = [    # 3 x 2 inside: the iris either side of a slit pupil, the glint at the top back; the lower rim softer
    "rrrrr",
    "ripgr",
    "riipr",
    ".sss.",
]
EYE_HOODED = [   # the brow's shadow lies on the top of the eye and runs on in front of it
    "rrrrrr",
    "rripgr",
    ".riipr",
    "..sss.",
]


def eye_cmap(p, rim="lid", soft="k1"):
    return {"r": p[rim], "s": p[soft], "i": p["iris"], "p": p["pupil"], "g": p["glint"],
            "c": p.get("iris2", p["iris"])}


def mouth_interior(img, C, p, upper, lower):
    """the palate under the skull's cubes and the floor of the mouth on the jaw's: gum at the rim, mouth or tongue"""
    for name in upper:
        c = C[name]; u, v, ww, hh = c["uv"]["down"]
        for j in range(hh):
            for i in range(ww):
                col = p["gum"] if i in (0, 1, ww - 2, ww - 1) else p["mouth"]
                img[v + j, u + i] = (*col, 255)
    for name in lower:
        c = C[name]; u, v, ww, hh = c["uv"]["up"]
        for j in range(hh):
            for i in range(ww):
                col = p["gum"] if i in (0, ww - 1) else p["tongue"]
                img[v + j, u + i] = (*col, 255)
