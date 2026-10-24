"""
Spinosaurus aegyptiacus  (Cretaceous, North Africa)

Reference (Wikipedia): length ~14 m (one of the longest theropods), a sail on
the back up to ~1.65 m tall made of elongated neural spines, a long narrow
crocodile-like snout with conical teeth and a rosette at the tip, relatively
short hind legs, strong arms with big thumb claws, and a deep paddle-like tail
(2020 finding) for swimming. A semi-aquatic fish eater.

In game: scale ~0.5 -> ~7.5 blocks long, sail top ~2.9 blocks.
Males have a taller, red-orange sail ("male_display" bone); females a duller one.
"""
import math
import large_theropod

ID = "spinosaurus"
# sail: thin vertical vanes along the spine (z0, length, height), tallest over the middle of the back
SAIL = [(-22, 6, 5), (-16, 6, 10), (-10, 6, 14), (-4, 6, 16), (2, 6, 14), (8, 6, 9), (14, 4, 4)]


def sail(m):
    for z0, ln, h in SAIL:
        m.box("body", (-0.5, 30, z0), (0.5, 30 + h, z0 + ln), name="sail", tag="sail")
    m.bone("male_display", "body", (0, 30, 0))
    for z0, ln, h in SAIL[1:-1]:
        m.box("male_display", (-0.5, 30 + h, z0 + 1), (0.5, 30 + h + 3, z0 + ln - 1), name="sail_top", tag="sail")


def paddle_tail(m, tail):
    """Tall thin fin above and below the last tail segments (2020 finding)."""
    for k, (up, down) in ((1, (3, 2)), (2, (5, 4)), (3, (6, 5))):
        sg = tail["segments"][k]
        y0, z0 = sg["unposed"]
        L = int(round(sg["len"]))
        hh = (7, 5, 3)[k - 1] / 2
        m.box(f"tail{k+1}", (-0.5, y0 + hh, z0), (0.5, y0 + hh + up, z0 + L), name="fin", tag="fin")
        m.box(f"tail{k+1}", (-0.5, y0 - hh - down, z0 + 1), (0.5, y0 - hh, z0 + L), name="fin", tag="fin")


def pattern(model, tx, rgb, region):
    P = tx.P
    if tx.cube.tag == "sail":
        top = tx.cube.to[1]
        base = 30.0
        g = (P[1] - base) / max(1.0, top - base) if tx.cube.bone in ("body", "male_display") else 0.5
        col = tx.pal["sail"] * (1 - 0.35 * max(0.0, min(1.0, g))) + tx.pal["sail_edge"] * 0.35 * max(0.0, min(1.0, g))
        if int(math.floor(P[2])) % 3 == 0:
            col = col * 0.78   # neural spines
        if P[1] > top - 1.0:
            col = tx.pal["sail_edge"].copy()
        return col
    if tx.cube.tag == "fin":
        col = tx.pal["fin"].copy()
        if int(math.floor(P[2])) % 3 == 0:
            col = col * 0.82
        if P[1] > tx.cube.to[1] - 1.0 or P[1] < tx.cube.frm[1] + 1.0:
            col = col * 0.7 + tx.pal["sail"] * 0.3
        return col
    if tx.cube.tag == "skin" and region in ("dorsal", "flank"):
        band = math.sin(P[2] * 2 * math.pi / 9.0 + 0.5 * math.sin(P[0]))
        if region == "dorsal" and band > 0.4:
            rgb = rgb * 0.8
    return rgb


TEETH_DOWN = {"faces": {"down": "mouth"}, "teeth": {"edge": "bottom", "rows": 1}}
SPEC = dict(
    palette={"dorsal": "#464a42", "flank": "#6b6f60", "belly": "#d0c8a8", "limb": "#55584c", "limb_top": "#66695a",
             "claw": "#2e2a26", "claw_base": "#3b342e", "claw_tip": "#bfb39a", "sail": "#b8402a", "sail_edge": "#eea444",
             "fin": "#575a4c", "tooth": "#efe7d2", "mouth": "#7c3430", "gum": "#5b2421", "eye": "#d8a838",
             "pupil": "#17110c", "dorsal_dark": "#3d3227"},
    sexes={"male": {"sail": "#bd3e26", "sail_edge": "#f2ac46"},
           "female": {"sail": "#7a6a58", "sail_edge": "#ad9a72", "dorsal": "#4e4e44"}},
    pattern=pattern, after_torso=sail, after_tail=paddle_tail,
    body=(26, 8),
    torso=[("hips", (-5.5, 19, 1, 5.5, 30, 14)), ("belly", (-6.5, 16, -14, 6.5, 30, 2)),
           ("chest", (-5.5, 16, -24, 5.5, 28, -13)), ("shoulders", (-4.5, 24, -28, 4.5, 30, -22))],
    neck=([(27, -26), (31, -31), (33.5, -35)], [(8, 8), (7, 7)]), skull_tilt=-4,
    head=[  # long narrow crocodile-like snout with a rosette at the tip
        dict(bone="skull", box=(-3.5, -2, -7, 3.5, 4, 1), name="cranium", paint={"faces": {"down": "mouth"}}),
        dict(bone="skull", box=(-2, -2, -21, 2, 2, -7), name="snout", paint=TEETH_DOWN),
        dict(bone="skull", box=(-2.5, -2, -24, 2.5, 2, -21), name="rosette", paint=TEETH_DOWN),
        dict(bone="skull", box=(-1, 4, -8, 1, 5, -3), name="crest", tag="dorsal_dark"),
        dict(bone="jaw", box=(-2, -4, -23, 2, -2, -6), name="jaw",
             paint={"faces": {"up": "mouth"}, "teeth": {"edge": "top", "rows": 1}}),
        dict(bone="jaw", box=(-3, -5, -7, 3, -2, -1), name="jaw_back", paint={"faces": {"up": "mouth"}}),
    ],
    jaw_pivot=(-2, -2), eyes=(1.0, 2.0, -4.0, 3.5),
    arm=(5.5, [(21, -20), (16, -21), (12.5, -24)], [(3, 3), (2, 3)],         # strong arms with big thumb claws
         [("thumb_claw", (-1, -3, -1.5, 0, 0, -0.5)), ("claw", (0, -2, -1.5, 1, 0, -0.5))]),
    leg=(6, [(26, 7), (16, 2), (7, 8), (2, 5.5)], [(6, 8, -0.5), (4, 5, 0.5, "limb"), (3, 3, 0.0, "limb")],  # short legs
         [("toes", "limb", (-2.5, -2, -6, 2.5, 0, 1)), ("claws", "claw", (-2.5, -2, -7, 2.5, -1, -6))]),
    tail=([(26, 13), (25.5, 25), (25, 37), (25, 49), (25, 61)], [(9, 9), (7, 7), (5, 5), (3, 3)]),
    saddle=None,
    sit=(11, 60, -112, 58, -6, {"tail1": (7, 0, 0), "tail2": (3, 0, 0), "neck1": (-6, 0, 0), "skull": (4, 0, 0)}),
)


def build():
    return large_theropod.build(ID, SPEC)
