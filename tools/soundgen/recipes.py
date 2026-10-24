"""
Sound recipes. Sounds are organised in VOICE SETS shared by many species (one per kind of animal), so hundreds
of species need only a few dozen sets: each species picks a set and a pitch in SPECIES_VOICE.

A variant is a procedural voice from synth.py (S(...)), or a cut of a recording (rec(...)) from art/sounds/src/,
listed in sources.py (public domain or CC0 only) and downloaded by fetch.py. A recording can sit over a procedural
layer, and falls back to a procedural voice while it is not downloaded. Every variant then goes through the set's
ffmpeg filter chain (FX[...]).

After editing: python3 build.py (sounds, sounds.json, ModSounds.java), then python3 ../javagen/gen_resources.py
(subtitles) and python3 ../javagen/gen_species.py (species use the sets).
"""

# ffmpeg filter chains per tone (before the shared loudness normalisation)
FX = {
    "deep": "highpass=f=28,lowpass=f=1100,equalizer=f=95:t=q:w=1:g=5,equalizer=f=240:t=q:w=1.4:g=5",
    "tube": "highpass=f=50,equalizer=f=340:t=q:w=2:g=8,equalizer=f=780:t=q:w=3:g=6,equalizer=f=1450:t=q:w=4:g=3,"
            "lowpass=f=3600,aecho=0.7:0.5:28|61:0.3|0.15",
    "beak": "highpass=f=180,equalizer=f=1100:t=q:w=1:g=6,lowpass=f=5200",
    "ground": "highpass=f=25,lowpass=f=700",
    "air": "highpass=f=90,lowpass=f=1800",
}


def S(voice, **params):
    """Procedural voice from synth.py."""
    return ("synth", voice, params)


def rec(pattern, fallback, layer=None, layer_gain=0.45, **params):
    """A recording from art/sounds/src (sources.py id + glob), optionally over a procedural layer (the felt low end).
    params: dur (seconds cut from the source), pick (n-th loudest part, auto) or start, pitch (<1 = slower and
    deeper), file (n-th matching file), fade_in, fade_out (fraction). Falls back to `fallback` until downloaded."""
    src = ("src", pattern, params)
    if layer is not None:
        src = ("mix", [(src, 1.0), (layer, layer_gain)])
    return ("alt", src, fallback)


# set -> event -> (fx, attenuation distance in blocks, [variants])
VOICE_SETS = {
    # big theropods: closed-mouth boom (alligator bellow, bison), felt more than heard
    "boom_large": {
        "ambient": ("deep", 48, [
            rec("wm_alligator_bellow/*", S("boom", dur=2.6, f0=56, f1=46, seed=1), dur=1.8, pitch=0.7,
                layer=S("boom", dur=2.6, f0=48, f1=42, seed=1)),
            rec("wm_alligator_bellow_2/*", S("boom", dur=2.2, f0=60, f1=50, flutter=8.5, seed=2), dur=1.6, pitch=0.7,
                layer=S("boom", dur=2.3, f0=52, f1=44, seed=2)),
            rec("nps_bison_bellow_a/*", S("boom", dur=3.0, f0=50, f1=44, flutter=6.0, depth=0.45, seed=3), dur=1.8,
                pitch=0.6, layer=S("boom", dur=3.0, f0=46, f1=40, seed=3))]),
        "threat": ("deep", 64, [
            rec("nps_grizzly_roar/*", S("boom", dur=3.4, f0=64, f1=42, flutter=9.0, depth=0.55, breath=0.25, seed=4),
                dur=2.0, pitch=0.6, layer=S("boom", dur=3.4, f0=58, f1=40, seed=4), layer_gain=0.6)]),
        "hurt": ("deep", 32, [
            rec("nps_grizzly_warn/*", S("grunt", dur=0.5, f0=120, f1=78, seed=5), dur=0.45, pitch=0.7),
            rec("nps_grizzly_warn/*", S("grunt", dur=0.45, f0=135, f1=90, seed=6), dur=0.45, pitch=0.75, pick=1)]),
        "death": ("deep", 48, [
            rec("nps_bison_bellow_b/*", S("groan", dur=2.6, f0=80, f1=34, seed=7), dur=1.8, pitch=0.55, fade_out=0.6,
                layer=S("groan", dur=3.2, f0=70, f1=30, seed=7))]),
        "step": ("ground", 24, [S("thud", f0=46, seed=8), S("thud", f0=40, seed=9)]),
    },
    # hadrosaurs: resonant crest call (elk bugle and tundra swans slowed down into a horn)
    "horn_hadrosaur": {
        "ambient": ("tube", 64, [
            rec("nps_elk_bugle/*", S("horn", dur=2.6, f0=92, f1=84, seed=11), dur=1.4, pitch=0.5,
                layer=S("horn", dur=2.8, f0=92, f1=84, seed=11), layer_gain=0.35),
            rec("wm_swans/*", S("horn", dur=1.8, f0=98, f1=92, seed=12), dur=1.2, pitch=0.55,
                layer=S("horn", dur=2.2, f0=98, f1=92, seed=12), layer_gain=0.35),
            rec("nps_elk_bugle/*", S("horn", dur=3.2, f0=88, f1=80, vibrato=3.5, seed=13), dur=1.6, pitch=0.45, pick=1,
                layer=S("horn", dur=3.6, f0=88, f1=80, seed=13), layer_gain=0.35)]),
        "hurt": ("tube", 24, [
            rec("wm_geese/*", S("grunt", dur=0.45, f0=180, f1=130, noise=0.3, seed=14), dur=0.3, pitch=0.6),
            rec("wm_geese/*", S("grunt", dur=0.4, f0=200, f1=150, noise=0.3, seed=15), dur=0.3, pitch=0.65, pick=1)]),
        "death": ("tube", 32, [
            rec("nps_elk_bugle/*", S("horn", dur=2.4, f0=96, f1=60, vibrato=6.0, seed=16), dur=1.3, pitch=0.42, pick=2,
                fade_out=0.6)]),
    },
    # pterosaurs: raspy squawk (crane, heron, raven, deeper) and wing beats
    "squawk_pterosaur": {
        "ambient": ("beak", 32, [
            rec("nps_crane/*", S("squawk", dur=0.55, f0=380, f1=300, seed=21), dur=0.6, pitch=0.75),
            rec("wm_heron/*", S("squawk", dur=0.4, f0=420, f1=340, seed=22), dur=0.5, pitch=0.8),
            rec("nps_raven/*", S("squawk", dur=0.7, f0=340, f1=260, rough=0.8, seed=23), dur=0.6, pitch=0.7)]),
        "hurt": ("beak", 24, [rec("wm_pelican/*", S("squawk", dur=0.3, f0=520, f1=420, rough=0.9, seed=24), dur=0.3,
                                  pitch=0.8)]),
        "death": ("beak", 24, [rec("nps_crane/*", S("squawk", dur=0.9, f0=400, f1=180, rough=0.7, seed=25), dur=0.7,
                                   pitch=0.6, pick=1, fade_out=0.6)]),
        "flap": ("air", 16, [rec("oga_wings/*", S("flap", dur=0.45, beats=1, seed=26), dur=0.5, pitch=0.8),
                             rec("oga_wings/*", S("flap", dur=0.5, beats=1, seed=27), dur=0.5, pitch=0.65)]),
    },
}

# species -> (voice set, pitch). Species not listed keep their vanilla sounds (gen_species.py SPECIES "sounds").
SPECIES_VOICE = {
    "tyrannosaurus": ("boom_large", 1.0),
    "parasaurolophus": ("horn_hadrosaur", 1.0),
    "pteranodon": ("squawk_pterosaur", 1.0),
}

# subtitles per set event: (pt_br, en_us, es_es)
SUBTITLES = {
    ("boom_large", "ambient"): ("Estrondo grave", "Deep boom", "Retumbo grave"),
    ("boom_large", "threat"): ("Estrondo ameaçador", "Threatening boom", "Retumbo amenazante"),
    ("boom_large", "hurt"): ("Dinossauro ferido", "Dinosaur hurts", "Dinosaurio herido"),
    ("boom_large", "death"): ("Dinossauro morre", "Dinosaur dies", "Dinosaurio muere"),
    ("boom_large", "step"): ("Passos pesados", "Heavy footsteps", "Pasos pesados"),
    ("horn_hadrosaur", "ambient"): ("Chamado de crista", "Crest call", "Llamada de cresta"),
    ("horn_hadrosaur", "hurt"): ("Dinossauro ferido", "Dinosaur hurts", "Dinosaurio herido"),
    ("horn_hadrosaur", "death"): ("Dinossauro morre", "Dinosaur dies", "Dinosaurio muere"),
    ("squawk_pterosaur", "ambient"): ("Pterossauro grasna", "Pterosaur squawks", "Pterosaurio grazna"),
    ("squawk_pterosaur", "hurt"): ("Pterossauro ferido", "Pterosaur hurts", "Pterosaurio herido"),
    ("squawk_pterosaur", "death"): ("Pterossauro morre", "Pterosaur dies", "Pterosaurio muere"),
    ("squawk_pterosaur", "flap"): ("Bater de asas", "Wings flap", "Aleteo"),
}


def events(voice_set):
    return list(VOICE_SETS[voice_set])


def field(voice_set, event):
    """Java constant in ModSounds."""
    return f"{voice_set}_{event}".upper()


def sound_id(voice_set, event):
    return f"voice.{voice_set}.{event}"
