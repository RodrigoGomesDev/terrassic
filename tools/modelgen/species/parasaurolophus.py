"""
Parasaurolophus walkeri  (Late Cretaceous, North America)

Reference (Wikipedia): length ~9.5 m, mass ~2.5 t, a long hollow crest
(over 1 m) curving back from the top of the skull, with internal tubes that
worked as a resonating chamber (calls); duck-like beak; walked on four legs
and could run on two; long hind legs, lighter forelimbs.

In game: scale ~0.6 -> ~6 blocks long. Males have the full-length crest
("male_display" bone adds the tip), females a shorter one.
"""
import hadrosaur

ID = "parasaurolophus"
SPEC = dict(
    palette={"dorsal": "#46584c", "flank": "#748c76", "belly": "#d8d4b0", "limb": "#5d6c5a", "limb_top": "#6f8670",
             "claw": "#38312a", "claw_base": "#38312a", "beak": "#4a4038", "crest": "#b8402f", "crest_band": "#e8c27a",
             "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622", "eye": "#b8862c", "pupil": "#140f0a"},
    sexes={"male": {"dorsal": "#3c5248", "crest": "#c0402c", "crest_band": "#f0cc7c"},
           "female": {"dorsal": "#5c5848", "flank": "#8c866a", "crest": "#7a6e5a", "crest_band": "#b9ad8e"}},
    snout=(-2.5, -3, -14, 2.5, 2, -6),
    bill=(-3, -3, -16, 3, 0, -14),
    jaw=(-2.5, -5, -15, 2.5, -3, -3),
    crest=[((-1, 3, -2, 1, 5, 8), -30)],          # long hollow tube sweeping back
    male_crest=[((-1, 3, 8, 1, 5, 13), -30)],     # males: full-length tube
    pattern="stripes",
)


def build():
    return hadrosaur.build(ID, SPEC)
