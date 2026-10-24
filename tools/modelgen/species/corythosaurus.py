"""
Corythosaurus casuarius  (Late Cretaceous, Campanian; Dinosaur Park Formation, Alberta)

Reference (Wikipedia; Brown 1914; Evans et al. 2009): a 9 m, 3-4 t lambeosaurine with a tall rounded helmet crest
(the "Corinthian helmet") on top of the skull, hollow with looping nasal passages that made a deep resonating call;
a narrower duck bill than the Edmontosaurus, a deep snout; skin impressions (AMNH 5240) show small polygonal
tubercles with larger ones in rows along the flanks and a tall row of knobs down the back.

Hadrosaur archetype with its own head (deep snout, narrow bill, the helmet crest in two tiers; males a taller crest)
and a flank-row skin pattern. SIZES scales it to 9 m. Olive green with sandy flanks and a dark back; the crest red
with a pale rim on males, dull brown on females.
"""
import math
import hadrosaur

ID = "corythosaurus"


def body_extra(m):
    # the tall midline row of knobs over the hips and the first tail segment
    for z in range(2, 14, 3):
        m.box("body", (-0.5, 28, z), (0.5, 30, z + 2), name="knob", tag="frill")
    for z in range(16, 24, 3):
        m.box("tail1", (-0.5, 28, z), (0.5, 30, z + 2), name="knob", tag="frill")


def pattern(model, tx, rgb, region):
    P = tx.P
    tag = tx.cube.tag
    if tag == "frill":
        return tx.pal["frill"].copy() * (1.1 if tx.face == "up" else 1.0)
    if tag == "crest":
        col = tx.pal["crest"].copy()
        # the pale rim along the front edge of the helmet and darker growth lines across it
        if tx.face in ("north", "up"):
            col = tx.pal["crest_band"].copy()
        elif math.sin(P[1] * 1.8 + P[2] * 0.4) > 0.75:
            col = col * 0.82
        return col
    if tag == "skin":
        if (int(math.floor(P[2] * 1.2)) + int(math.floor(P[1] * 1.2)) + int(math.floor(P[0] * 1.2))) % 2 == 0:
            rgb = rgb * 0.95                                   # fine tubercles
        if region == "flank" and int(math.floor(P[1] * 0.6 + 0.5)) % 2 == 0 and int(math.floor(P[2] * 0.6)) % 2 == 0:
            rgb = tx.pal["flank_knob"].copy()                  # rows of bigger tubercles along the flanks
        if region in ("dorsal", "flank") and math.sin(P[2] * 0.75 + 0.6 * math.sin(P[1] * 0.5)) > 0.8:
            rgb = rgb * 0.84                                   # faint dark bars
    return rgb


SPEC = dict(
    palette={"dorsal": "#3c5038", "flank": "#8c9a60", "flank_knob": "#a4b070", "belly": "#e2dcb8", "frill": "#2e3e2a",
             "limb": "#5a6a48", "limb_top": "#6c7e56",
             "claw": "#38312a", "claw_base": "#38312a", "beak": "#463c32",
             "crest": "#b8402f", "crest_band": "#e8c27a",
             "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622", "eye": "#b8862c", "pupil": "#140f0a"},
    sexes={"male": {"dorsal": "#304430", "crest": "#c4402a", "crest_band": "#f0d080"},
           "female": {"dorsal": "#4e5a3c", "flank": "#9aa270", "crest": "#7a6248", "crest_band": "#b8a888"}},
    belly=(7, 12),
    snout=(-3, -3, -12, 3, 3, -6),                 # deep snout
    bill=(-3, -3, -15, 3, -1, -12),                # narrower bill than the Edmontosaurus
    jaw=(-2.5, -5, -14, 2.5, -3, -3),
    crest=[(-1, 3, -7, 1, 8, 1), (-0.5, 8, -6, 0.5, 10, 0)],            # the helmet: tall plate with a rounded top
    male_crest=[(-0.5, 10, -5, 0.5, 12, -1), (-1, 8, 1, 1, 10, 3)],     # males: taller and reaching further back
    pattern=pattern, body_extra=body_extra,
)


def build():
    return hadrosaur.build(ID, SPEC)
