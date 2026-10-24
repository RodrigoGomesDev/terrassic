"""
Edmontosaurus annectens  (Late Cretaceous, Maastrichtian; Hell Creek and Lance formations, western North America)

Reference (Wikipedia; Campione & Evans 2011; Bell et al. 2013): one of the largest hadrosaurs, 12 m and ~4 t
(bigger individuals are claimed), with a flat skull, a long low snout ending in a broad flat duck bill, dental
batteries of hundreds of teeth, and no bony crest: the "Dakota" and AMNH 5060 mummies preserve the skin, a row of
scaly frill knobs down the back and, on one specimen, a fleshy cockscomb on top of the head. Lived in huge herds and
was the staple prey of the Tyrannosaurus (healed bite marks on a tail).

Hadrosaur archetype with its own head (long flat bill, no crest, the fleshy comb on males), a dorsal frill of knobs,
and a tubercle skin pattern. Modelled at the family's rig size; SIZES scales it to 12 m. Dusty grey-brown with a
pale belly, a dark stripe down the spine; males with the red comb and darker back, females sandier.
"""
import math
import hadrosaur

ID = "edmontosaurus"


def body_extra(m):
    # the row of scaly knobs down the spine (the frill seen on the mummies), on the back and the first tail segment
    for z in range(-9, 12, 3):
        m.box("body", (-0.5, 29, z), (0.5, 31, z + 2), name="frill", tag="frill")
    for z in range(16, 26, 3):
        m.box("tail1", (-0.5, 28, z), (0.5, 30, z + 2), name="frill", tag="frill")


def head_extra(m, R, ay, az):
    # the broad flat bill has a rounded lip below the snout; big nostril hollows on the snout sides
    m.box("skull", *R(-4, -4, -16, 4, -3, -12), name="bill_lip", tag="beak")
    m.box("skull", *R(-3.5, 0, -11, -2.5, 2, -8), name="nostril_l", tag="nostril")
    m.box("skull", *R(2.5, 0, -11, 3.5, 2, -8), name="nostril_r", tag="nostril")


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "frill":
        col = tx.pal["frill"].copy()
        if tx.face == "up":
            col = col * 1.15
        return col
    if tag == "nostril":
        return tx.pal["nostril"].copy()
    if tag == "crest":
        return tx.pal["crest"].copy() * (0.9 if tx.edge else 1.0)
    if tag == "skin":
        # the mummy skin: small polygonal tubercles everywhere, bigger ones in rows on the flanks; a dark spine stripe
        if (int(math.floor(P[2] * 1.2)) + int(math.floor(P[1] * 1.2)) + int(math.floor(P[0] * 1.2))) % 2 == 0:
            rgb = rgb * 0.94
        if region == "flank" and int(math.floor(P[1] * 0.5)) % 2 == 0 and int(math.floor(P[2] * 0.5)) % 2 == 0:
            rgb = rgb * 1.08
        if region == "dorsal" and tx.face == "up" and abs(P[0]) < 1.6:
            rgb = tx.pal["spine"].copy()
        # soft dark saddle bands over the back, fading before the belly
        if region == "dorsal" and math.sin(P[2] * 0.6) > 0.7:
            rgb = rgb * 0.86
    return rgb


SPEC = dict(
    palette={"dorsal": "#6a6050", "flank": "#9a8c72", "belly": "#e2dac4", "spine": "#3e362c", "frill": "#4e4638",
             "limb": "#7a6e58", "limb_top": "#8a7e66",
             "claw": "#38312a", "claw_base": "#38312a", "beak": "#4a4238", "nostril": "#3a3028",
             "crest": "#b04838", "crest_band": "#b04838",
             "spot": "#3e3226", "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622", "eye": "#b8862c", "pupil": "#140f0a"},
    sexes={"male": {"dorsal": "#5a5044", "flank": "#8c7e66", "crest": "#c04a38"},
           "female": {"dorsal": "#7a6e58", "flank": "#a89a7c", "belly": "#ece4ce", "crest": "#9a6a58"}},
    belly=(8, 11),                                # the biggest and heaviest of the duckbills
    snout=(-3, -3, -13, 3, 2, -6),                # long low snout
    bill=(-4.5, -3, -17, 4.5, -1, -13),           # very broad, flat duck bill
    jaw=(-3, -5, -15, 3, -3, -3),
    crest=[],                                     # no bony crest at all
    male_crest=[(-1, 4, -5, 1, 7, -1), (-0.5, 7, -4, 0.5, 8, -2)],   # the fleshy cockscomb (Bell et al. 2013)
    pattern=pattern, body_extra=body_extra, head_extra=head_extra,
)


def build():
    return hadrosaur.build(ID, SPEC)
