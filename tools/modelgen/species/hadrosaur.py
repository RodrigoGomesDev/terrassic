"""
Archetype: hadrosaur (duck-billed dinosaurs). One rig for the whole family; a species only gives a short spec:
palette, head (snout, bill, jaw), crest boxes and skin pattern. Body, legs, tail, saddle and animations
(idle, walk, run, sit, graze, headbutt, crest call) are shared. The in-game size comes from the renderer scale
(SIZES in tools/javagen/gen_species.py), so the rig itself stays at one size.

Spec keys (head boxes are relative to the head anchor: x, y, z with -z = forward):
  palette, sexes   colours (see paint.py); the crest uses "crest" and "crest_band", blotches use "spot"
  belly            (half width, bottom y) of the belly box; heavier species are wider and lower
  snout, bill, jaw (x0, y0, z0, x1, y1, z1)
  crest            list of crest boxes: (x0, y0, z0, x1, y1, z1) or (box, rot_x) tilted around crest_origin
  male_crest       extra crest boxes shown only on males (male_display bone), same format
  crest_origin     (y, z) pivot of tilted crest boxes, relative to the head anchor
  pattern          "stripes" (bands across the back) or "blotches" (irregular dark spots)
"""
import math
from rig import Model, track, keys, add_saddle, knockout_tracks
from quadruped import hind_leg, front_leg, quad_anims

DEFAULTS = dict(belly=(7, 12), crest=[], male_crest=[], crest_origin=(4, -2), pattern="stripes")


def build(species_id, spec):
    spec = {**DEFAULTS, **spec}
    m = Model(species_id, render_scale=1.0)
    m.palette = spec["palette"]
    m.sexes = spec["sexes"]
    m.bone("root", None, (0, 0, 0))
    m.bone("body", "root", (0, 23, 8))
    bw, by = spec["belly"]
    m.box("body", (-6, 15, 2), (6, 28, 16), name="hips")
    m.box("body", (-bw, by, -12), (bw, 27, 4), name="belly")
    m.box("body", (-5.5, 12, -20), (5.5, 24, -11), name="chest")
    m.box("body", (-4, 27, -10), (4, 29, 12), name="back")

    neck = m.chain(["neck1", "neck2"], "body", 0, [(21, -19), (24, -25), (25.5, -29)], "-z",
                   [(8, 8), (7, 7)], overlap=(1.5, 1.0))
    ay, az = neck["end"]
    m.bone("head", "neck2", (0, ay, az))
    m.bone("skull", "head", (0, ay, az), (-12 - neck["abs"], 0, 0))

    def R(x0, y0, z0, x1, y1, z1):
        return (x0, ay + y0, az + z0), (x1, ay + y1, az + z1)

    def crest(bone, boxes, name):
        co = (0, ay + spec["crest_origin"][0], az + spec["crest_origin"][1])
        for b in boxes:
            if len(b) == 2:  # tilted
                m.box(bone, *R(*b[0]), name=name, tag="crest", rot=(b[1], 0, 0), origin=co)
            else:
                m.box(bone, *R(*b), name=name, tag="crest")

    m.box("skull", *R(-3.5, -3, -6, 3.5, 4, 1), name="cranium", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(*spec["snout"]), name="snout", paint={"faces": {"down": "mouth"}})
    m.box("skull", *R(*spec["bill"]), name="bill", tag="beak")
    crest("skull", spec["crest"], "crest")
    m.bone("male_display", "skull", (0, ay, az))
    crest("male_display", spec["male_crest"], "crest_tip")
    m.bone("jaw", "skull", (0, ay - 3, az - 3))
    m.box("jaw", *R(*spec["jaw"]), name="jaw", paint={"faces": {"up": "mouth"}})
    m.decals += [
        {"kind": "eye", "bones": ["skull"], "pos": (3.5, ay + 1.0, az - 3.0), "r": 1.0, "side": 1},
        {"kind": "eye", "bones": ["skull"], "pos": (-3.5, ay + 1.0, az - 3.0), "r": 1.0, "side": -1},
    ]

    m.sym(lambda s, sx: front_leg(m, s, sx, 5, [(15, -15), (8, -14), (2, -15.5)], [(4, 5, 0.0), (3, 3, 0.0, "limb")], (4, 2, 1)))
    m.sym(lambda s, sx: hind_leg(m, s, sx, 6, [(23, 9), (13, 6), (5, 11), (2, 9)],
                                 [(7, 10, 0.0), (5, 6, 0.5, "limb"), (4, 4, 0.0, "limb")], (6, 4, 2)))
    m.chain(["tail1", "tail2", "tail3", "tail4"], "body", 0, [(24, 15), (23, 26), (21.5, 37), (20, 47), (19, 55)], "+z",
            [(10, 10), (8, 8), (6, 6), (3, 3)], overlap=(1.0, 1.0))
    add_saddle(m, "body", 29, -6, 4, 8, 7, flap=6)
    m.pattern = PATTERNS[spec["pattern"]]

    call = {
        "neck1": track(rot=keys([(0, 0, 0, 0), (0.35, 16, 0, 0), (1.3, 16, 0, 0), (1.6, 0, 0, 0)])),
        "neck2": track(rot=keys([(0, 0, 0, 0), (0.35, 8, 0, 0), (1.3, 8, 0, 0), (1.6, 0, 0, 0)])),
        "skull": track(rot=keys([(0, 0, 0, 0), (0.35, 14, 0, 0), (1.3, 14, 0, 0), (1.6, 0, 0, 0)])),
        "jaw": track(rot=keys([(0, 0, 0, 0), (0.35, -16, 0, 0), (1.25, -16, 0, 0), (1.5, 0, 0, 0)])),
    }
    # knocked out (taming by knockout, see docs/DOMESTICACAO.md): lying on its side, legs limp, neck and tail flat
    limp = {"neck1": (-10, 0, 0), "neck2": (-6, 0, 0), "skull": (-4, 0, 0), "jaw": (-8, 0, 0),
            "tail1": (-6, 0, 0), "tail2": (-4, 0, 0)}
    for side, k in (("l", 1), ("r", -1)):
        limp.update({f"thigh_{side}": (20 * k, 0, 0), f"shin_{side}": (-25, 0, 0), f"foot_{side}": (20, 0, 0),
                     f"upperarm_{side}": (-25 * k, 0, 0), f"forearm_{side}": (20, 0, 0)})
    quad_anims(m, 4, walk=(1.5, 20, 16, 0.6), run=(0.75, 32, 22, 1.2), attack="headbutt", sit_drop=9,
               graze_neck=-26, graze_skull=-10,
               extra={"call": (1.6, False, call), "knocked_out": (4.0, True, knockout_tracks(4.0, *KNOCKOUT, limp))})
    return m


# root roll (deg), drop and sideways shift (px) that lay the body on the ground
KNOCKOUT = (82, -6, 13)


def _crest_band(tx, rgb):
    band = math.sin((tx.P[1] + tx.P[2]) * 1.4)
    return tx.pal["crest_band"].copy() if band > 0.75 else rgb


def stripes(model, tx, rgb, region):
    if tx.cube.tag == "crest":
        return _crest_band(tx, rgb)
    if tx.cube.tag == "skin" and region in ("dorsal", "flank"):
        st = math.sin(tx.P[2] * 2 * math.pi / 7.0)
        if st > 0.55 and (region == "dorsal" or tx.cy > 0.55):
            rgb = rgb * 0.78
    return rgb


def blotches(model, tx, rgb, region):
    """Irregular dark blotches, like a ground-nesting bird."""
    P = tx.P
    if tx.cube.tag == "crest":
        return _crest_band(tx, rgb)
    if tx.cube.tag == "skin" and region in ("dorsal", "flank"):
        n = math.sin(P[2] * 0.9 + 2.0 * math.sin(P[1] * 0.7)) + math.sin(P[0] * 1.3 + P[2] * 0.4)
        if n > 1.3:
            rgb = tx.pal["spot"].copy()
    return rgb


PATTERNS = {"stripes": stripes, "blotches": blotches}
