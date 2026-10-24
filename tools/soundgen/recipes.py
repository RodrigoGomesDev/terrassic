"""
Sound recipes. Sounds are organised in VOICE SETS shared by many species (one per kind of animal), so hundreds
of species need only a few dozen sets: each species picks a set and a pitch in SPECIES_VOICE.

A variant is either a procedural voice from synth.py, ("synth", voice, params), or a recorded source,
("src", "file.wav", seconds_start, seconds_length), read from art/sounds/src/ (CC0 only; list each file in
art/sounds/src/CREDITS.md). Every variant then goes through the set's ffmpeg filter chain (FX[...]).

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

# set -> event -> (fx, attenuation distance in blocks, [variants])
VOICE_SETS = {
    # big theropods: closed-mouth boom, felt more than heard
    "boom_large": {
        "ambient": ("deep", 48, [("synth", "boom", dict(dur=2.6, f0=56, f1=46, seed=1)),
                                 ("synth", "boom", dict(dur=2.2, f0=60, f1=50, flutter=8.5, seed=2)),
                                 ("synth", "boom", dict(dur=3.0, f0=50, f1=44, flutter=6.0, depth=0.45, seed=3))]),
        "threat": ("deep", 64, [("synth", "boom", dict(dur=3.4, f0=64, f1=42, flutter=9.0, depth=0.55, breath=0.25, seed=4))]),
        "hurt": ("deep", 32, [("synth", "grunt", dict(dur=0.5, f0=120, f1=78, seed=5)),
                              ("synth", "grunt", dict(dur=0.45, f0=135, f1=90, seed=6))]),
        "death": ("deep", 48, [("synth", "groan", dict(dur=2.6, f0=80, f1=34, seed=7))]),
        "step": ("ground", 24, [("synth", "thud", dict(f0=46, seed=8)), ("synth", "thud", dict(f0=40, seed=9))]),
    },
    # hadrosaurs: resonant crest call
    "horn_hadrosaur": {
        "ambient": ("tube", 64, [("synth", "horn", dict(dur=2.6, f0=92, f1=84, seed=11)),
                                 ("synth", "horn", dict(dur=1.8, f0=98, f1=92, seed=12)),
                                 ("synth", "horn", dict(dur=3.2, f0=88, f1=80, vibrato=3.5, seed=13))]),
        "hurt": ("tube", 24, [("synth", "grunt", dict(dur=0.45, f0=180, f1=130, noise=0.3, seed=14)),
                              ("synth", "grunt", dict(dur=0.4, f0=200, f1=150, noise=0.3, seed=15))]),
        "death": ("tube", 32, [("synth", "horn", dict(dur=2.4, f0=96, f1=60, vibrato=6.0, seed=16))]),
    },
    # pterosaurs: raspy squawk and wing beats
    "squawk_pterosaur": {
        "ambient": ("beak", 32, [("synth", "squawk", dict(dur=0.55, f0=380, f1=300, seed=21)),
                                 ("synth", "squawk", dict(dur=0.4, f0=420, f1=340, seed=22)),
                                 ("synth", "squawk", dict(dur=0.7, f0=340, f1=260, rough=0.8, seed=23))]),
        "hurt": ("beak", 24, [("synth", "squawk", dict(dur=0.3, f0=520, f1=420, rough=0.9, seed=24))]),
        "death": ("beak", 24, [("synth", "squawk", dict(dur=0.9, f0=400, f1=180, rough=0.7, seed=25))]),
        "flap": ("air", 16, [("synth", "flap", dict(dur=0.45, beats=1, seed=26)), ("synth", "flap", dict(dur=0.5, beats=1, seed=27))]),
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
