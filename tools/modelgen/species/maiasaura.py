"""
Maiasaura peeblesorum  (Late Cretaceous, Two Medicine Formation, Montana)

Reference (Wikipedia): length ~9 m, mass ~3 t; a flat-headed hadrosaur (no hollow crest) with a small solid
spiky crest in front of the eyes, a broad duck-like beak, heavy body; walked on four legs and could run on two.
Known from big nesting colonies ("Egg Mountain") with eggs, hatchlings and juveniles: the young stayed in the
nest and were fed by the adults, hence the name "good mother lizard".

Same build as the Parasaurolophus (both hadrosaurs) but heavier, with a short deep snout and the little crest.
Males have a taller crest ("male_display").
"""
import hadrosaur

ID = "maiasaura"
SPEC = dict(
    palette={"dorsal": "#5a4a36", "flank": "#8c7a58", "belly": "#e0d6b6", "limb": "#6a5a42", "limb_top": "#7c6a4e",
             "claw": "#38312a", "claw_base": "#38312a", "beak": "#3e362e", "crest": "#9a5a32", "crest_band": "#d8a860",
             "spot": "#3e3226", "tooth": "#d8d0b8", "mouth": "#6e3330", "gum": "#4e2622", "eye": "#b8862c", "pupil": "#140f0a"},
    sexes={"male": {"crest": "#a8502a", "crest_band": "#e8b060"},
           "female": {"dorsal": "#62553e", "flank": "#968660", "crest": "#7c6648", "crest_band": "#b8a078"}},
    belly=(7.5, 11),                              # heavier than the Parasaurolophus
    snout=(-3, -3, -12, 3, 3, -6),                # short deep snout
    bill=(-3.5, -3, -14, 3.5, 0, -12),            # broad duck bill
    jaw=(-3, -5, -13, 3, -3, -3),
    crest=[(-1, 3, -6, 1, 5, -2)],                # small solid crest in front of the eyes
    male_crest=[(-1, 5, -5, 1, 6, -3)],
    pattern="blotches",
)


def build():
    return hadrosaur.build(ID, SPEC)
