"""
Sound recipes. Sounds are organised in VOICE SETS shared by many species (one per kind of animal), so hundreds
of species need only a few dozen sets: each species picks a set and a pitch in SPECIES_VOICE.

Every sound is procedural (synth.py), made from scratch in code: no recording and nothing from third parties.
A variant is V(P(...), P(...), ...): parts layered on a timeline (start in seconds, voice, gain, parameters),
then saturation (drive) and an outdoor room (room = (reverb time s, wet)). Formant frequencies, f0 and amplitude
take [(fraction of the part, value)] tracks.

Minecraft clamps the playback pitch to 0.5..2 and babies play 1.5x higher, so a species pitch stays near 1 and a
set is designed for the size of its animals.

The old recipe kind rec(...) (cuts of public-domain recordings, sources.py) is still understood by build.py but
no set uses it any more: the bird and mammal recordings made some voices sound like geese, chickens or people.

After editing: python3 build.py (sounds, sounds.json, ModSounds.java), then python3 ../javagen/gen_resources.py
(subtitles) and python3 ../javagen/gen_species.py (species use the sets). Listen with python3 preview.py.
"""

# ffmpeg filter chains (the voice is already shaped in synth.py; this only cleans the extremes)
FX = {
    "voice": "highpass=f=24,lowpass=f=11000",
    "deep": "highpass=f=22,lowpass=f=6000",
    "ground": "highpass=f=24,lowpass=f=5000",
    "air": "highpass=f=60,lowpass=f=9000",
}


def S(voice, **params):
    """A single procedural voice from synth.py."""
    return ("synth", voice, params)


def V(*parts, room=(1.0, 0.15), drive=1.0, hp=None, lp=None):
    """A sound: parts layered on a timeline, then drive and room."""
    return ("synth", "mix", dict(parts=list(parts), room=room, drive_amount=drive, hp=hp, lp=lp))


def P(start, voice, gain=1.0, **params):
    return (start, voice, params, gain)


def rec(pattern, fallback, layer=None, layer_gain=0.45, **params):
    """A cut of a recording from art/sounds/src (kept for reference; no set uses it)."""
    src = ("src", pattern, params)
    if layer is not None:
        src = ("mix", [(src, 1.0), (layer, layer_gain)])
    return ("alt", src, fallback)


def tr(*points):
    """Track: tr(0, 100, 0.5, 140, 1, 90) -> [(0, 100), (0.5, 140), (1, 90)]."""
    return [(points[i], points[i + 1]) for i in range(0, len(points), 2)]


# ---------------------------------------------------------------- throats (formant sets)
# closed mouth of a big animal: everything low and dark
CLOSED_HUGE = [(190, 110, 0), (420, 170, -3), (850, 280, -9), (1700, 500, -18)]
CLOSED_BIG = [(230, 120, 0), (520, 190, -4), (1050, 330, -11), (2100, 600, -20)]
CLOSED_MID = [(280, 150, 0), (650, 230, -5), (1450, 420, -13), (2700, 700, -22)]


def opening(f1, f2, f3, k=1.0):
    """Mouth opening then closing: formants rise to (f1, f2, f3)*k and fall back."""
    return [(tr(0, f1 * 0.55 * k, 0.2, f1 * k, 0.7, f1 * 0.9 * k, 1, f1 * 0.6 * k), 170 * k, 0),
            (tr(0, f2 * 0.65 * k, 0.2, f2 * k, 1, f2 * 0.7 * k), 280 * k, -5),
            (f3 * k, 600 * k, -12), (f3 * 1.6 * k, 800 * k, -20)]


def step_set(f0, weight, crunch=0.8, dur=0.45, n=2):
    return [V(P(0, "thud", dur=dur, f0=f0 * (1 - 0.1 * i), weight=weight, crunch=crunch, seed=900 + i * 7 + int(f0)),
              room=(0.5, 0.08)) for i in range(n)]


def snort(start, gain=1.0, dur=0.18, k=1.0, seed=0):
    """Air blasted through the nostrils."""
    return P(start, "breath", gain, dur=dur, formants=[(450 * k, 380 * k, 0), (1400 * k, 900 * k, -4), (3200 * k, 1500, -14)],
             hp=120 * k, attack=0.01, release=dur * 0.6, seed=seed)


def hiss(start, gain=1.0, dur=0.8, k=1.0, swell=True, seed=0):
    return P(start, "breath", gain, dur=dur, formants=[(2600 * k, 2400 * k, 0), (5200 * k, 3000, -5)], hp=900 * k,
             attack=dur * (0.45 if swell else 0.05), release=dur * 0.35, seed=seed)


def exhale(start, gain=0.5, dur=0.8, k=1.0, seed=0):
    return P(start, "breath", gain, dur=dur, formants=[(300 * k, 300 * k, 0), (900 * k, 600 * k, -6)], lp=2200 * k,
             attack=0.08, release=dur * 0.6, amp=tr(0, 1, 1, 0.4), seed=seed)


# ---------------------------------------------------------------- voice sets
# set -> event -> (fx, attenuation distance in blocks, [variants])
ARCHETYPES = {
    # big theropods (tyrannosaurids, carcharodontosaurids, Spinosaurus): closed-mouth boom with a crocodile
    # throat flutter, a growling open-mouth threat, barks when hurt
    "boom_large": {
        "ambient": ("deep", 48, [
            V(P(0, "call", dur=2.6, f0=tr(0, 44, 0.3, 52, 1, 40), tilt=-7, sub=0.15, flutter=(7.5, 0.4), breath=0.08,
                breath_color=2, formants=CLOSED_HUGE, body=0.2, attack=0.3, release=0.9, seed=1),
              room=(1.6, 0.2)),
            V(P(0, "call", dur=1.2, f0=tr(0, 50, 1, 45), tilt=-7, sub=0.2, flutter=(6.5, 0.35), breath=0.06,
                formants=CLOSED_HUGE, body=0.18, attack=0.15, release=0.5, seed=2),
              P(1.3, "call", dur=1.9, f0=tr(0, 46, 0.4, 55, 1, 40), tilt=-7, sub=0.25, flutter=(6.0, 0.4), breath=0.08,
                formants=CLOSED_HUGE, body=0.2, attack=0.25, release=0.8, seed=3),
              exhale(3.0, 0.35, 0.9, 0.8, seed=4), room=(1.6, 0.2)),
            V(snort(0, 0.5, 0.25, 0.7, seed=5),
              P(0.3, "call", dur=2.2, f0=tr(0, 58, 1, 50), tilt=-7, sub=0.3, fry=0.7, fry_rate=tr(0, 26, 1, 20),
                fry_sharp=5, breath=0.2, breath_color=1, formants=CLOSED_BIG, attack=0.2, release=0.7, seed=6),
              room=(1.4, 0.18)),
        ]),
        "threat": ("deep", 64, [
            V(P(0, "breath", 0.35, dur=0.5, formants=[(500, 600, 0), (1500, 900, -6)], lp=2500, attack=0.35,
                release=0.08, amp=tr(0, 0.2, 1, 0.6), seed=7),
              P(0.42, "call", dur=2.6, f0=tr(0, 62, 0.15, 88, 0.55, 80, 1, 52), tilt=-6, sub=0.55, fry=0.45,
                fry_rate=tr(0, 34, 1, 22), breath=0.3, breath_color=1.5, formants=opening(470, 1080, 2100), lp=3200,
                body=0.09, attack=0.12, release=0.8, seed=8),
              room=(2.0, 0.25), drive=2.2),
            V(P(0, "clack", 0.6, freq=520, q=380, seed=9),
              P(0.12, "call", dur=3.0, f0=tr(0, 55, 0.25, 78, 0.8, 66, 1, 46), tilt=-6.5, sub=0.6, fry=0.35,
                fry_rate=28, breath=0.25, breath_color=1.5, formants=opening(420, 980, 1900), lp=3000, body=0.14,
                attack=0.2, release=1.0, seed=10),
              exhale(2.9, 0.4, 1.0, 0.8, seed=11), room=(2.0, 0.25), drive=2.0),
        ]),
        "hurt": ("deep", 32, [
            V(P(0, "call", dur=0.5, f0=tr(0, 92, 0.3, 84, 1, 58), tilt=-7, sub=0.6, fry=0.45, fry_rate=30,
                breath=0.3, breath_color=1, formants=opening(300, 700, 1500), lp=3500, attack=0.01, release=0.25,
                seed=12), room=(1.0, 0.15), drive=2.0),
            V(snort(0, 0.6, 0.12, 0.8, seed=13),
              P(0.08, "call", dur=0.42, f0=tr(0, 100, 1, 62), tilt=-7, sub=0.6, fry=0.45, fry_rate=34, breath=0.3,
                breath_color=1, formants=opening(290, 680, 1450), lp=3500, attack=0.01, release=0.22, seed=14),
              room=(1.0, 0.15), drive=2.0),
        ]),
        "death": ("deep", 48, [
            V(P(0, "call", dur=3.4, f0=tr(0, 70, 0.25, 76, 1, 32), tilt=-7, sub=0.5, fry=0.4, fry_rate=tr(0, 30, 1, 12),
                breath=0.25, breath_color=1.5, formants=[(tr(0, 320, 1, 170), 160, 0), (tr(0, 760, 1, 400), 260, -6),
                                                         (1700, 500, -15)],
                lp=3000, attack=0.1, release=1.6, amp=tr(0, 1, 0.6, 0.8, 1, 0.4), seed=15),
              exhale(3.0, 0.45, 1.2, 0.8, seed=16), room=(1.8, 0.22), drive=1.6),
        ]),
        "step": ("ground", 24, step_set(44, 1.2, 0.5)),
    },

    # mid theropods (abelisaurids, Dilophosaurus): croaking nasal rattle, hiss into a rising growl
    "growl_theropod": {
        "ambient": ("voice", 32, [
            V(P(0, "call", dur=1.4, f0=tr(0, 95, 0.3, 105, 1, 78), tilt=-7, sub=0.3, fry=0.75, fry_rate=24,
                fry_sharp=5, breath=0.15, formants=CLOSED_MID, notch=(900, 300, 0.7), attack=0.08, release=0.45,
                seed=21), room=(1.2, 0.16)),
            V(snort(0, 0.7, 0.3, 1.0, seed=22),
              P(0.35, "call", dur=0.9, f0=tr(0, 80, 1, 72), tilt=-7, formants=CLOSED_BIG[:3], flutter=(9, 0.3),
                body=0.14, breath=0.1, attack=0.08, release=0.4, seed=23), room=(1.2, 0.16)),
            V(P(0, "clack", 0.7, freq=700, q=450, seed=24), P(0.18, "clack", 0.6, freq=760, q=450, seed=25),
              P(0.4, "call", dur=1.6, f0=tr(0, 75, 1, 62), tilt=-7, sub=0.35, fry=0.5, fry_rate=20, breath=0.15,
                formants=CLOSED_MID, attack=0.15, release=0.6, seed=26), room=(1.2, 0.16)),
        ]),
        "threat": ("voice", 48, [
            V(hiss(0, 0.6, 0.7, seed=27),
              P(0.5, "call", dur=1.8, f0=tr(0, 90, 0.2, 140, 0.6, 125, 1, 85), tilt=-6, sub=0.6, fry=0.4, fry_rate=36,
                breath=0.4, breath_color=0.6, formants=opening(560, 1250, 2400), lp=4200, attack=0.05, release=0.6,
                seed=28), room=(1.5, 0.2), drive=2.4),
        ]),
        "hurt": ("voice", 24, [
            V(P(0, "call", dur=0.4, f0=tr(0, 130, 1, 85), tilt=-6, sub=0.7, fry=0.4, fry_rate=40, breath=0.4,
                formants=opening(380, 850, 1800), lp=4200, attack=0.01, release=0.2, seed=29), drive=2.2),
            V(hiss(0, 0.6, 0.18, swell=False, seed=30),
              P(0.1, "call", dur=0.35, f0=tr(0, 120, 1, 80), tilt=-6, sub=0.7, fry=0.4, fry_rate=36, breath=0.4,
                formants=opening(360, 820, 1700), lp=4200, attack=0.01, release=0.2, seed=31), drive=2.2),
        ]),
        "death": ("voice", 32, [
            V(P(0, "call", dur=2.2, f0=tr(0, 100, 0.2, 106, 1, 45), tilt=-7, sub=0.55, fry=0.55,
                fry_rate=tr(0, 30, 1, 10), breath=0.3, formants=[(tr(0, 360, 1, 200), 170, 0),
                                                                 (tr(0, 820, 1, 460), 260, -6), (1700, 500, -15)],
                attack=0.05, release=1.0, amp=tr(0, 1, 1, 0.5), seed=32),
              hiss(1.9, 0.3, 0.8, swell=False, seed=33), room=(1.4, 0.2), drive=1.6),
        ]),
        "step": ("ground", 16, step_set(58, 0.8, 0.5, 0.35)),
    },

    # dromaeosaurs and Troodon: throat rattle, huffs and beak clicks, raspy croak when hurt
    "rattle_raptor": {
        "ambient": ("voice", 24, [
            V(P(0, "call", dur=1.0, f0=tr(0, 150, 1, 130), tilt=-7, sub=0.2, fry=0.9, fry_rate=tr(0, 38, 1, 30),
                fry_sharp=7, breath=0.2, formants=[(420, 220, 0), (1100, 350, -6), (2600, 700, -14)],
                attack=0.05, release=0.35, seed=41), room=(0.9, 0.14)),
            V(snort(0, 0.8, 0.15, 1.6, seed=42), snort(0.25, 0.7, 0.15, 1.5, seed=43),
              P(0.6, "clack", 0.7, freq=1300, q=700, seed=44), P(0.7, "clack", 0.6, freq=1250, q=700, seed=45),
              P(0.9, "call", dur=0.55, f0=tr(0, 112, 1, 100), tilt=-7, formants=[(380, 200, 0), (950, 300, -7)],
                fry=0.85, fry_rate=30, fry_sharp=6, breath=0.2, attack=0.04, release=0.25, seed=46), room=(0.9, 0.14)),
            V(hiss(0, 0.8, 1.0, 1.0, seed=47),
              P(0.25, "call", 0.6, dur=0.85, f0=125, tilt=-7, fry=0.9, fry_rate=tr(0, 26, 1, 42), fry_sharp=6,
                formants=[(380, 200, 0), (1000, 320, -6)], breath=0.2, attack=0.3, release=0.1, seed=48),
              room=(0.9, 0.14)),
        ]),
        "hurt": ("voice", 16, [
            V(P(0, "call", dur=0.32, f0=tr(0, 260, 0.3, 280, 1, 170), tilt=-6, sub=0.6, fry=0.3, fry_rate=50,
                breath=0.45, formants=[(600, 300, 0), (1500, 450, -4), (3000, 800, -12)], lp=5000, attack=0.008,
                release=0.18, seed=49), drive=2.5),
            V(hiss(0, 0.8, 0.22, swell=False, seed=50), P(0.12, "clack", 0.8, freq=1400, q=800, seed=51),
              P(0.15, "call", 0.7, dur=0.25, f0=tr(0, 230, 1, 160), tilt=-6, sub=0.7, breath=0.5,
                formants=[(560, 280, 0), (1400, 420, -4)], attack=0.005, release=0.15, seed=52), drive=2.3),
        ]),
        "death": ("voice", 24, [
            V(P(0, "call", dur=1.6, f0=tr(0, 170, 1, 90), tilt=-7, sub=0.3, fry=0.9, fry_rate=tr(0, 40, 1, 12),
                fry_sharp=6, breath=0.25, formants=[(tr(0, 480, 1, 300), 220, 0), (tr(0, 1200, 1, 800), 340, -6)],
                attack=0.03, release=0.7, amp=tr(0, 1, 1, 0.4), seed=53),
              hiss(1.3, 0.3, 0.7, swell=False, seed=54), room=(1.0, 0.15)),
        ]),
        "step": ("ground", 12, step_set(90, 0.3, 0.7, 0.18)),
    },

    # small feathered predators (Compsognathus, Mononykus): gliding whistled trills and chatter, never clucks
    "trill_small": {
        "ambient": ("air", 16, [
            V(P(0, "trill", dur=0.7, f0=tr(0, 3200, 1, 2500), rate=26, seed=61), room=(0.6, 0.12)),
            V(P(0, "trill", dur=0.1, f0=tr(0, 4200, 1, 3000), rate=0, seed=62),
              P(0.18, "trill", dur=0.1, f0=tr(0, 4100, 1, 2900), rate=0, seed=63),
              P(0.4, "trill", dur=0.55, f0=tr(0, 2800, 1, 2550), rate=34, seed=64), room=(0.6, 0.12)),
            V(P(0, "call", dur=0.6, f0=420, tilt=-6, fry=0.9, fry_rate=42, fry_sharp=6, breath=0.15,
                formants=[(1200, 500, 0), (2800, 800, -6)], attack=0.02, release=0.2, seed=65),
              P(0.65, "trill", 0.7, dur=0.25, f0=tr(0, 3000, 1, 3400), rate=0, seed=66), room=(0.6, 0.12)),
        ]),
        "hurt": ("air", 12, [
            V(P(0, "trill", dur=0.18, f0=tr(0, 3600, 0.3, 4200, 1, 2600), rate=0, harm=0.4, seed=67),
              hiss(0.1, 0.6, 0.2, 1.3, swell=False, seed=68)),
        ]),
        "death": ("air", 16, [
            V(P(0, "trill", dur=1.1, f0=tr(0, 3000, 1, 1500), rate=tr(0, 30, 1, 10), seed=69), room=(0.7, 0.14)),
        ]),
        "step": ("ground", 8, [V(P(0, "thud", dur=0.12, f0=160, weight=0.15, crunch=0.9, seed=70))]),
    },

    # oviraptorosaurs, ornithomimids, Therizinosaurus, Deinocheirus: closed-mouth drumming and coos like
    # emus and cassowaries, hisses
    "drum_ratite": {
        "ambient": ("voice", 32, [
            V(*[P(t, "call", g, dur=0.3, f0=tr(0, 78 - 2 * i, 1, 70 - 2 * i), tilt=-7.5, formants=CLOSED_BIG[:2],
                  body=0.23, breath=0.05, attack=0.03, release=0.15, seed=80 + i)
                for i, (t, g) in enumerate(((0, 1.0), (0.42, 0.9), (0.8, 0.8), (1.15, 0.65), (1.48, 0.5)))],
              room=(1.2, 0.18)),
            V(P(0, "call", dur=1.6, f0=tr(0, 70, 0.5, 82, 1, 64), tilt=-7.5, formants=CLOSED_BIG[:3], tube=(82, 0.55),
                flutter=(5, 0.25), body=0.18, breath=0.06, attack=0.2, release=0.6, seed=86), room=(1.2, 0.18)),
            V(hiss(0, 0.7, 0.6, seed=87),
              P(0.55, "call", dur=0.4, f0=tr(0, 92, 1, 80), tilt=-7, sub=0.3, formants=CLOSED_BIG[:3], body=0.14,
                fry=0.4, fry_rate=22, breath=0.1, attack=0.03, release=0.2, seed=88), room=(1.0, 0.15)),
        ]),
        "hurt": ("voice", 16, [
            V(hiss(0, 0.8, 0.25, swell=False, seed=89),
              P(0.1, "call", dur=0.3, f0=tr(0, 110, 1, 78), tilt=-7, sub=0.6, fry=0.45, fry_rate=34, tube=(82, 0.5),
                formants=[(300, 180, 0), (750, 280, -6)], notch=(1100, 300, 0.6), breath=0.3, attack=0.01,
                release=0.15, seed=90), drive=2.0),
            V(P(0, "call", dur=0.35, f0=tr(0, 100, 1, 72), tilt=-7, sub=0.6, breath=0.35, fry=0.4, fry_rate=30, tube=(82, 0.5),
                formants=[(290, 170, 0), (720, 260, -6)], attack=0.01, release=0.18, seed=91),
              hiss(0.2, 0.5, 0.25, swell=False, seed=92), drive=2.0),
        ]),
        "death": ("voice", 24, [
            V(P(0, "call", dur=2.0, f0=tr(0, 85, 1, 45), tilt=-7, formants=[(tr(0, 240, 1, 170), 120, 0), (500, 180, -8)],
                fry=0.4, fry_rate=tr(0, 25, 1, 9), body=0.18, breath=0.1, attack=0.05, release=0.9, seed=93),
              hiss(1.6, 0.35, 0.8, swell=False, seed=94), room=(1.2, 0.18)),
        ]),
        "step": ("ground", 16, step_set(55, 0.7, 0.5, 0.32)),
    },

    # lambeosaurs (Parasaurolophus, Corythosaurus): the hollow crest as a horn; the comb of tube resonances is
    # fixed by the crest, the voice glides across it (a didgeridoo-like "wah")
    "horn_hadrosaur": {
        "ambient": ("voice", 64, [
            V(P(0, "call", dur=2.8, f0=tr(0, 58, 0.12, 64, 0.85, 63, 1, 56), tilt=-5, jitter=0.006, shimmer=0.05,
                breath=0.12, formants=[(tr(0, 350, 0.3, 650, 1, 500), 250, 0), (1250, 400, -6), (2400, 600, -14)],
                tube=(48, 0.82), flutter=(4.5, 0.1), attack=0.25, release=0.8, seed=101), room=(2.2, 0.28)),
            V(P(0, "call", dur=0.5, f0=tr(0, 70, 1, 62), tilt=-5, breath=0.1, formants=[(450, 250, 0), (1200, 400, -6)],
                tube=(48, 0.8), attack=0.06, release=0.2, seed=102),
              P(0.6, "call", dur=2.0, f0=tr(0, 60, 0.2, 70, 1, 58), tilt=-5, jitter=0.006, breath=0.12,
                formants=[(tr(0, 380, 0.4, 720, 1, 480), 260, 0), (1300, 420, -6), (2500, 600, -14)],
                tube=(48, 0.82), flutter=(4.0, 0.08), attack=0.15, release=0.7, seed=103), room=(2.2, 0.28)),
            V(P(0, "call", dur=1.4, f0=52, tilt=-7, formants=[(300, 200, 0), (800, 300, -10)], tube=(48, 0.75),
                breath=0.1, attack=0.2, release=0.5, amp=tr(0, 0.8, 1, 1), seed=104),
              exhale(1.3, 0.35, 0.7, 1.0, seed=105), room=(1.6, 0.2)),
        ]),
        "hurt": ("voice", 24, [
            V(P(0, "call", dur=0.45, f0=tr(0, 95, 1, 70), tilt=-4, sub=0.4, fry=0.3, fry_rate=30, breath=0.25,
                formants=[(600, 300, 0), (1400, 400, -5)], tube=(48, 0.7), attack=0.01, release=0.2, seed=106),
              drive=2.0),
            V(P(0, "call", dur=0.4, f0=tr(0, 105, 1, 78), tilt=-4, sub=0.45, breath=0.3,
                formants=[(650, 300, 0), (1500, 420, -5)], tube=(48, 0.7), attack=0.01, release=0.18, seed=107),
              drive=2.0),
        ]),
        "death": ("voice", 32, [
            V(P(0, "call", dur=3.0, f0=tr(0, 66, 0.3, 68, 1, 38), tilt=-5, fry=0.3, fry_rate=tr(0, 20, 1, 8),
                breath=0.15, formants=[(tr(0, 600, 1, 300), 260, 0), (1200, 400, -6)], tube=(48, 0.8),
                attack=0.1, release=1.2, amp=tr(0, 1, 1, 0.4), seed=108),
              exhale(2.6, 0.4, 1.0, seed=109), room=(2.0, 0.25)),
        ]),
    },

    # flat-headed hadrosaurs (Edmontosaurus, Maiasaura): bellow through an inflated nasal sac (nasal notch,
    # chest boom), honks and snorts
    "bellow_hadrosaur": {
        "ambient": ("voice", 48, [
            V(P(0, "call", dur=2.0, f0=tr(0, 62, 0.3, 74, 1, 58), tilt=-7, sub=0.3, formants=CLOSED_BIG, tube=(70, 0.55), fry=0.25, fry_rate=20,
                notch=(750, 250, 0.85), body=0.16, flutter=(3.5, 0.15), breath=0.08, attack=0.2, release=0.6, seed=121),
              room=(1.8, 0.22)),
            V(P(0, "call", dur=0.6, f0=tr(0, 80, 1, 70), tilt=-6, sub=0.2, formants=CLOSED_BIG, notch=(800, 260, 0.85),
                body=0.14, breath=0.08, attack=0.05, release=0.25, seed=122),
              P(0.75, "call", 0.9, dur=0.8, f0=tr(0, 72, 1, 60), tilt=-6, sub=0.2, formants=CLOSED_BIG,
                notch=(760, 260, 0.85), body=0.14, breath=0.08, attack=0.05, release=0.35, seed=123),
              room=(1.8, 0.22)),
            V(snort(0, 0.7, 0.2, 0.9, seed=124),
              P(0.3, "call", dur=1.3, f0=tr(0, 56, 1, 50), tilt=-7, fry=0.55, fry_rate=18, formants=CLOSED_BIG,
                body=0.14, breath=0.12, attack=0.1, release=0.5, seed=125), room=(1.4, 0.18)),
        ]),
        "hurt": ("voice", 24, [
            V(snort(0, 0.6, 0.1, 1.0, seed=126),
              P(0.05, "call", dur=0.45, f0=tr(0, 90, 1, 62), tilt=-6, sub=0.6, breath=0.3, fry=0.4, fry_rate=28, tube=(70, 0.5),
                formants=opening(300, 700, 1500), notch=(750, 250, 0.7), attack=0.01, release=0.2, seed=127),
              drive=2.0),
            V(P(0, "call", dur=0.5, f0=tr(0, 84, 1, 58), tilt=-6, sub=0.6, breath=0.3, fry=0.35, fry_rate=26, tube=(70, 0.5),
                formants=opening(290, 680, 1450), notch=(720, 250, 0.7), attack=0.01, release=0.22, seed=128),
              drive=2.0),
        ]),
        "death": ("voice", 32, [
            V(P(0, "call", dur=2.8, f0=tr(0, 78, 0.2, 82, 1, 40), tilt=-7, sub=0.3, fry=0.35, fry_rate=tr(0, 22, 1, 8),
                formants=CLOSED_BIG, notch=(750, 250, 0.8), body=0.14, breath=0.15, attack=0.08, release=1.2,
                amp=tr(0, 1, 1, 0.4), seed=129),
              exhale(2.4, 0.4, 1.0, seed=130), room=(1.8, 0.22)),
        ]),
    },

    # ceratopsians: nostril snorts, rumbling bellow-grunts, huffing
    "snort_ceratopsian": {
        "ambient": ("voice", 32, [
            V(snort(0, 1.0, seed=141), snort(0.3, 0.8, seed=142),
              P(0.7, "call", dur=0.9, f0=tr(0, 62, 1, 54), tilt=-7, sub=0.35, fry=0.5, fry_rate=22,
                formants=CLOSED_BIG, breath=0.12, attack=0.08, release=0.35, seed=143), room=(1.2, 0.16)),
            V(P(0, "call", dur=1.1, f0=tr(0, 70, 0.25, 82, 1, 58), tilt=-7, sub=0.4, breath=0.25, breath_color=1,
                formants=[(tr(0, 220, 0.3, 380, 1, 220), 150, 0), (700, 250, -6), (1600, 400, -15)],
                attack=0.06, release=0.4, seed=144), room=(1.2, 0.16), drive=1.8),
            V(exhale(0, 0.8, 0.45, 1.3, seed=145), snort(0.55, 0.7, 0.3, 0.9, seed=146),
              exhale(1.0, 0.7, 0.45, 1.2, seed=147), P(1.5, "clack", 0.5, freq=480, q=300, seed=148),
              room=(1.0, 0.14)),
        ]),
        "hurt": ("voice", 24, [
            V(P(0, "call", dur=0.45, f0=tr(0, 92, 1, 60), tilt=-6, sub=0.6, breath=0.3, fry=0.45, fry_rate=30,
                formants=opening(320, 720, 1500), attack=0.01, release=0.2, seed=149), drive=2.0),
            V(snort(0, 0.8, 0.12, seed=150),
              P(0.07, "call", dur=0.4, f0=tr(0, 86, 1, 58), tilt=-6, sub=0.6, breath=0.3, fry=0.4, fry_rate=28,
                formants=opening(300, 690, 1450), attack=0.01, release=0.2, seed=151), drive=2.0),
        ]),
        "death": ("voice", 32, [
            V(P(0, "call", dur=2.4, f0=tr(0, 82, 0.2, 86, 1, 40), tilt=-7, sub=0.45, fry=0.4, fry_rate=tr(0, 26, 1, 9),
                breath=0.2, formants=[(tr(0, 320, 1, 190), 160, 0), (tr(0, 740, 1, 440), 260, -6)],
                attack=0.05, release=1.0, amp=tr(0, 1, 1, 0.45), seed=152),
              exhale(2.1, 0.45, 1.0, seed=153), room=(1.4, 0.18), drive=1.5),
        ]),
        "step": ("ground", 20, step_set(50, 1.0, 0.55)),
    },

    # ankylosaurs and Stegosaurus: honks through long looping nasal passages, snuffling, low creaky groans
    "honk_armored": {
        "ambient": ("voice", 32, [
            V(P(0, "call", dur=1.0, f0=tr(0, 88, 0.3, 96, 1, 80), tilt=-6, sub=0.15, tube=(130, 0.78),
                formants=[(260, 150, 0), (780, 260, -6), (1800, 500, -16)], notch=(1100, 300, 0.6), breath=0.08,
                attack=0.06, release=0.35, seed=161), room=(1.2, 0.16)),
            V(*[snort(i * 0.14, 0.7 - i * 0.08, 0.09, 1.4, seed=162 + i) for i in range(4)],
              P(0.7, "call", dur=0.6, f0=tr(0, 72, 1, 64), tilt=-7, sub=0.3, fry=0.4, fry_rate=20,
                formants=CLOSED_BIG[:3], breath=0.1, attack=0.05, release=0.25, seed=166), room=(1.0, 0.14)),
            V(P(0, "call", dur=1.6, f0=tr(0, 62, 1, 56), tilt=-7, fry=0.6, fry_rate=18, fry_sharp=5,
                formants=CLOSED_BIG[:3], tube=(130, 0.6), breath=0.1, attack=0.15, release=0.5, seed=167),
              room=(1.2, 0.16)),
        ]),
        "hurt": ("voice", 24, [
            V(P(0, "call", dur=0.4, f0=tr(0, 100, 1, 70), tilt=-5, sub=0.6, fry=0.4, fry_rate=28, breath=0.3, tube=(130, 0.7),
                formants=[(330, 200, 0), (800, 300, -5)], attack=0.01, release=0.18, seed=168), drive=2.0),
            V(snort(0, 0.8, 0.12, 1.2, seed=169),
              P(0.08, "call", dur=0.35, f0=tr(0, 94, 1, 66), tilt=-5, sub=0.6, fry=0.4, fry_rate=26, breath=0.3, tube=(130, 0.7),
                formants=[(320, 200, 0), (780, 300, -5)], attack=0.01, release=0.18, seed=170), drive=2.0),
        ]),
        "death": ("voice", 32, [
            V(P(0, "call", dur=2.4, f0=tr(0, 90, 0.2, 94, 1, 42), tilt=-6, sub=0.35, fry=0.4, fry_rate=tr(0, 24, 1, 8),
                tube=(130, 0.75), formants=[(tr(0, 320, 1, 220), 160, 0), (800, 260, -7)], breath=0.15,
                attack=0.05, release=1.0, amp=tr(0, 1, 1, 0.45), seed=171),
              exhale(2.0, 0.4, 1.0, seed=172), room=(1.4, 0.18)),
        ]),
        "step": ("ground", 20, step_set(48, 1.1, 0.7)),
    },

    # sauropods: very low rumbles and moans through a long trachea, huge exhales, ground-shaking steps
    "rumble_sauropod": {
        "ambient": ("deep", 80, [
            V(P(0, "call", dur=3.6, f0=tr(0, 34, 0.3, 40, 0.7, 42, 1, 32), tilt=-7, sub=0.1,
                formants=[(tr(0, 160, 0.5, 220, 1, 150), 90, 0), (tr(0, 380, 0.5, 520, 1, 360), 160, -5),
                          (900, 300, -14)], tube=(38, 0.6), flutter=(2.5, 0.12), body=0.23, breath=0.06,
                attack=0.5, release=1.2, seed=181), room=(2.8, 0.3)),
            V(P(0, "call", dur=2.8, f0=tr(0, 36, 0.6, 52, 1, 46), tilt=-6, tube=(44, 0.8),
                formants=[(300, 200, 0), (750, 250, -8), (1500, 450, -18)], breath=0.08, body=0.18,
                attack=0.4, release=0.9, seed=182), room=(2.8, 0.3)),
            V(P(0, "breath", 0.9, dur=1.6, formants=[(250, 250, 0), (700, 500, -6)], lp=1500,
                amp=tr(0, 0.4, 0.2, 1, 1, 0.3), attack=0.2, release=0.8, seed=183),
              P(0.3, "call", 0.7, dur=2.0, f0=30, tilt=-7, formants=CLOSED_HUGE[:3], body=0.27, flutter=(3, 0.2),
                attack=0.5, release=0.8, seed=184), room=(2.4, 0.26)),
        ]),
        "hurt": ("deep", 32, [
            V(P(0, "call", dur=1.2, f0=tr(0, 58, 0.2, 64, 1, 42), tilt=-6, sub=0.4, breath=0.3, breath_color=1,
                formants=[(330, 180, 0), (800, 260, -6), (1600, 400, -15)], attack=0.03, release=0.5, seed=185),
              room=(1.8, 0.2), drive=1.8),
            V(P(0, "call", dur=1.0, f0=tr(0, 64, 1, 46), tilt=-6, sub=0.45, breath=0.3, breath_color=1,
                formants=[(350, 180, 0), (850, 260, -6), (1700, 400, -15)], attack=0.03, release=0.45, seed=186),
              room=(1.8, 0.2), drive=1.8),
        ]),
        "death": ("deep", 64, [
            V(P(0, "call", dur=4.5, f0=tr(0, 46, 0.2, 50, 1, 22), tilt=-6, sub=0.3, fry=0.3, fry_rate=tr(0, 16, 1, 6),
                formants=[(tr(0, 300, 1, 160), 150, 0), (tr(0, 760, 1, 380), 240, -6)], tube=(40, 0.6), body=0.18,
                breath=0.15, attack=0.2, release=2.0, amp=tr(0, 1, 1, 0.4), seed=187),
              exhale(4.0, 0.5, 1.6, 0.8, seed=188), room=(2.8, 0.3)),
        ]),
        "step": ("ground", 40, step_set(32, 2.0, 0.6, 0.8)),
    },

    # small and mid ornithopods (Pachycephalosaurus, Thescelosaurus): hollow low hoots, chuffs, grunts
    "grunt_ornithopod": {
        "ambient": ("voice", 24, [
            V(P(0, "call", dur=0.28, f0=82, tilt=-7, tube=(95, 0.6), formants=CLOSED_MID[:2], fry=0.35, fry_rate=22,
                body=0.14, breath=0.1, attack=0.03, release=0.12, seed=201),
              P(0.34, "call", dur=0.45, f0=tr(0, 80, 1, 72), tilt=-7, tube=(95, 0.6), formants=CLOSED_MID[:2],
                fry=0.35, fry_rate=20, body=0.14, breath=0.1, attack=0.03, release=0.2, seed=202), room=(1.0, 0.14)),
            V(snort(0, 0.8, 0.12, 1.2, seed=203),
              P(0.12, "call", dur=0.35, f0=tr(0, 110, 1, 80), tilt=-7, sub=0.5, fry=0.5, fry_rate=28,
                formants=CLOSED_MID, breath=0.2, attack=0.02, release=0.15, seed=204), room=(1.0, 0.14)),
            V(*[snort(i * 0.16, 0.6 - i * 0.1, 0.08, 1.5, seed=205 + i) for i in range(3)],
              P(0.55, "call", dur=0.9, f0=tr(0, 70, 1, 64), tilt=-7, fry=0.6, fry_rate=16, formants=CLOSED_MID[:3],
                breath=0.12, attack=0.1, release=0.35, seed=208), room=(1.0, 0.14)),
        ]),
        "hurt": ("voice", 16, [
            V(P(0, "call", dur=0.35, f0=tr(0, 125, 1, 85), tilt=-6, sub=0.7, breath=0.45, fry=0.45, fry_rate=36, tube=(95, 0.5),
                formants=opening(380, 850, 1700), notch=(1100, 350, 0.5), attack=0.008, release=0.16, seed=209),
              drive=2.3),
            V(snort(0, 0.7, 0.1, 1.2, seed=210),
              P(0.06, "call", dur=0.3, f0=tr(0, 115, 1, 80), tilt=-6, sub=0.7, breath=0.45, fry=0.4, fry_rate=34, tube=(95, 0.5),
                formants=opening(360, 820, 1650), notch=(1050, 350, 0.5), attack=0.008, release=0.15, seed=211),
              drive=2.3),
        ]),
        "death": ("voice", 24, [
            V(P(0, "call", dur=1.6, f0=tr(0, 100, 0.2, 104, 1, 48), tilt=-7, sub=0.5, fry=0.6,
                fry_rate=tr(0, 28, 1, 9), breath=0.25, formants=[(tr(0, 340, 1, 220), 170, 0), (tr(0, 800, 1, 500), 260, -6)],
                attack=0.03, release=0.7, amp=tr(0, 1, 1, 0.4), seed=212),
              exhale(1.4, 0.35, 0.7, 1.2, seed=213), room=(1.0, 0.15)),
        ]),
    },

    # pterosaurs: hoarse guttural croaks, beak clatter, membrane wing beats
    "squawk_pterosaur": {
        "ambient": ("voice", 32, [
            V(P(0, "call", dur=0.6, f0=tr(0, 210, 0.25, 240, 1, 170), tilt=-5, jitter=0.03, shimmer=0.2, sub=0.7,
                breath=0.35, fry=0.35, fry_rate=60, formants=[(650, 350, 0), (1450, 450, -3), (2700, 700, -10)],
                lp=5000, attack=0.02, release=0.2, seed=221), room=(1.0, 0.16), drive=2.2),
            V(*[P(i * 0.075, "clack", 0.9 - i * 0.07, dur=0.07, freq=1400 + (i % 2) * 150, q=700, seed=222 + i)
                for i in range(7)],
              P(0.62, "call", 0.8, dur=0.4, f0=tr(0, 200, 1, 160), tilt=-5, sub=0.8, breath=0.4, jitter=0.03,
                formants=[(620, 330, 0), (1400, 450, -3), (2600, 700, -10)], lp=5000, attack=0.02, release=0.15,
                seed=229), room=(1.0, 0.16), drive=2.0),
            V(P(0, "call", dur=1.1, f0=tr(0, 260, 0.2, 300, 1, 190), tilt=-5, jitter=0.04, shimmer=0.25, sub=0.8,
                breath=0.4, fry=0.4, fry_rate=45, formants=[(tr(0, 600, 0.3, 780, 1, 560), 350, 0), (1600, 480, -3),
                                                             (2900, 700, -10)],
                lp=5000, attack=0.03, release=0.35, seed=230), room=(1.2, 0.18), drive=2.2),
        ]),
        "hurt": ("voice", 24, [
            V(P(0, "call", dur=0.25, f0=tr(0, 320, 1, 240), tilt=-5, sub=0.8, breath=0.5, jitter=0.04,
                formants=[(700, 350, 0), (1600, 480, -3), (3000, 700, -10)], lp=5500, attack=0.005, release=0.12,
                seed=231), drive=2.4),
        ]),
        "death": ("voice", 24, [
            V(P(0, "call", dur=1.2, f0=tr(0, 300, 0.2, 320, 1, 140), tilt=-5, sub=0.8, breath=0.45, fry=0.5,
                fry_rate=tr(0, 50, 1, 12), formants=[(tr(0, 700, 1, 450), 350, 0), (tr(0, 1600, 1, 1100), 480, -3)],
                lp=5000, attack=0.02, release=0.5, amp=tr(0, 1, 1, 0.4), seed=232), room=(1.2, 0.18), drive=2.0),
        ]),
        "flap": ("air", 16, [V(P(0, "flap", dur=0.55, size=1.2, seed=233)), V(P(0, "flap", dur=0.5, size=1.0, seed=234))]),
    },

    # Ichthyornis (toothed seabird): harsh rolling "keer" calls and chatter, quick wing beats
    "cry_seabird": {
        "ambient": ("air", 24, [
            V(P(0, "call", dur=0.45, f0=tr(0, 1050, 0.2, 1250, 1, 880), tilt=-5, sub=0.35, breath=0.3,
                formants=[(2400, 1200, 0), (4200, 1500, -6)], fry=0.3, fry_rate=70, attack=0.02, release=0.15,
                seed=241), room=(0.9, 0.16)),
            V(P(0, "call", dur=0.7, f0=tr(0, 980, 1, 900), tilt=-5, sub=0.3, breath=0.3, fry=0.85, fry_rate=14,
                fry_sharp=4, formants=[(2300, 1100, 0), (4000, 1500, -6)], attack=0.02, release=0.15, seed=242),
              room=(0.9, 0.16)),
            V(P(0, "call", dur=0.3, f0=tr(0, 900, 1, 1150), tilt=-5, sub=0.3, breath=0.25,
                formants=[(2200, 1100, 0), (3900, 1500, -6)], attack=0.02, release=0.1, seed=243),
              P(0.38, "call", dur=0.5, f0=tr(0, 1150, 1, 820), tilt=-5, sub=0.35, breath=0.3,
                formants=[(2300, 1100, 0), (4000, 1500, -6)], fry=0.3, fry_rate=60, attack=0.02, release=0.18,
                seed=244), room=(0.9, 0.16)),
        ]),
        "hurt": ("air", 16, [
            V(P(0, "call", dur=0.18, f0=tr(0, 1400, 1, 1000), tilt=-5, sub=0.5, breath=0.45,
                formants=[(2600, 1200, 0), (4400, 1500, -6)], attack=0.005, release=0.08, seed=245), drive=2.0),
        ]),
        "death": ("air", 16, [
            V(P(0, "call", dur=0.9, f0=tr(0, 1200, 1, 600), tilt=-5, sub=0.4, breath=0.35, fry=0.4,
                fry_rate=tr(0, 60, 1, 12), formants=[(2300, 1200, 0), (4000, 1500, -6)], attack=0.02, release=0.4,
                amp=tr(0, 1, 1, 0.4), seed=246), room=(0.9, 0.16)),
        ]),
        "flap": ("air", 12, [V(P(0, "flap", dur=0.35, beats=2, size=0.45, seed=247))]),
    },

    # Hesperornis (flightless diving bird): long rising wails and tremolo laughs, like divers on a lake
    "wail_diver": {
        "ambient": ("voice", 32, [
            V(P(0, "call", dur=1.6, f0=tr(0, 420, 0.3, 620, 0.8, 600, 1, 480), tilt=-12, coherent=False, jitter=0.004,
                breath=0.05, formants=[(900, 600, 0), (2000, 800, -10)], attack=0.15, release=0.4, seed=261),
              room=(1.8, 0.24)),
            V(P(0, "call", dur=1.2, f0=tr(0, 560, 1, 520), tilt=-11, coherent=False, flutter=(9, 0.75), breath=0.06,
                formants=[(950, 600, 0), (2100, 800, -10)], attack=0.05, release=0.3, seed=262), room=(1.8, 0.24)),
            V(P(0, "call", dur=0.8, f0=tr(0, 380, 1, 560), tilt=-11, coherent=False, breath=0.05,
                formants=[(850, 600, 0), (1900, 800, -10)], attack=0.1, release=0.2, seed=263),
              P(0.85, "call", dur=1.1, f0=tr(0, 560, 0.5, 600, 1, 450), tilt=-11, coherent=False, breath=0.05,
                formants=[(900, 600, 0), (2000, 800, -10)], attack=0.05, release=0.35, seed=264), room=(1.8, 0.24)),
        ]),
        "hurt": ("voice", 16, [
            V(P(0, "call", dur=0.3, f0=tr(0, 520, 1, 380), tilt=-6, sub=0.6, breath=0.45,
                formants=[(1000, 500, 0), (2300, 700, -6)], attack=0.005, release=0.12, seed=265), drive=2.0),
        ]),
        "death": ("voice", 24, [
            V(P(0, "call", dur=1.5, f0=tr(0, 560, 0.2, 600, 1, 300), tilt=-10, coherent=False, flutter=(7, 0.5),
                breath=0.1, formants=[(900, 600, 0), (2000, 800, -10)], attack=0.05, release=0.6, amp=tr(0, 1, 1, 0.4),
                seed=266), room=(1.6, 0.22)),
        ]),
    },

    # mosasaurs: blasts of breath at the surface, low underwater rumbles with bubbles, jaw claps
    "blow_mosasaur": {
        "ambient": ("deep", 48, [
            V(P(0, "breath", dur=1.0, formants=[(400, 500, 0), (1500, 1600, -4), (4000, 3000, -12)], attack=0.02,
                release=0.6, amp=tr(0, 1, 1, 0.3), seed=281),
              P(0, "call", 0.6, dur=0.4, f0=40, tilt=-7, formants=CLOSED_HUGE[:2], body=0.27, attack=0.01, release=0.3,
                seed=282),
              P(1.15, "breath", 0.45, dur=0.6, formants=[(tr(0, 300, 1, 700), 400, 0), (1500, 1200, -6)], attack=0.3,
                release=0.1, seed=283), room=(1.6, 0.18)),
            V(P(0, "call", dur=2.0, f0=tr(0, 40, 0.5, 48, 1, 36), tilt=-7, formants=CLOSED_HUGE[:3], lp=900, fry=0.4,
                fry_rate=12, body=0.23, attack=0.3, release=0.7, seed=284),
              *[P(0.2 + 0.23 * i + 0.05 * (i % 3), "trill", 0.25, dur=0.03, f0=tr(0, 300 + 40 * i, 1, 800 + 60 * i),
                  rate=0, harm=0, attack=0.002, release=0.015, seed=285 + i) for i in range(7)],
              room=(2.0, 0.3)),
            V(P(0, "clack", 1.0, dur=0.18, freq=400, q=300, seed=292),
              P(0.15, "call", dur=1.2, f0=tr(0, 64, 1, 52), tilt=-7, sub=0.5, fry=0.5, fry_rate=22, breath=0.2,
                formants=CLOSED_BIG, attack=0.05, release=0.5, seed=293), room=(1.6, 0.2), drive=1.8),
        ]),
        "hurt": ("deep", 24, [
            V(P(0, "breath", 0.8, dur=0.35, formants=[(500, 500, 0), (1800, 1500, -4)], attack=0.01, release=0.2,
                seed=294),
              P(0.03, "call", dur=0.4, f0=tr(0, 85, 1, 56), tilt=-6, sub=0.6, breath=0.3, fry=0.4, fry_rate=24,
                formants=opening(300, 700, 1500), attack=0.01, release=0.2, seed=295), drive=2.0),
        ]),
        "death": ("deep", 32, [
            V(P(0, "call", dur=2.4, f0=tr(0, 70, 0.2, 74, 1, 34), tilt=-7, sub=0.4, fry=0.4, fry_rate=tr(0, 20, 1, 7),
                formants=[(tr(0, 330, 1, 180), 160, 0), (750, 250, -7)], lp=1500, body=0.14, breath=0.15,
                attack=0.05, release=1.0, amp=tr(0, 1, 1, 0.4), seed=296),
              *[P(1.0 + 0.19 * i, "trill", 0.2, dur=0.03, f0=tr(0, 260 + 30 * i, 1, 700 + 40 * i), rate=0, harm=0,
                  attack=0.002, release=0.015, seed=297 + i) for i in range(6)],
              room=(2.0, 0.28)),
        ]),
    },

    # Elasmosaurus: soft whale-like moans and whoops, surface breaths
    "moan_plesiosaur": {
        "ambient": ("voice", 48, [
            V(P(0, "call", dur=2.6, f0=tr(0, 90, 0.4, 130, 0.8, 120, 1, 95), tilt=-11, coherent=False, breath=0.05,
                formants=[(tr(0, 300, 0.5, 600, 1, 350), 250, 0), (1100, 400, -10)], flutter=(6, 0.15),
                attack=0.3, release=0.8, seed=301), room=(2.4, 0.3)),
            V(P(0, "breath", 0.7, dur=0.7, formants=[(500, 500, 0), (1600, 1400, -5)], attack=0.02, release=0.4,
                seed=302),
              P(0.8, "call", dur=0.5, f0=tr(0, 120, 1, 140), tilt=-10, coherent=False, formants=[(450, 250, 0), (1100, 400, -10)],
                attack=0.08, release=0.2, seed=303),
              P(1.4, "call", dur=0.6, f0=tr(0, 135, 1, 110), tilt=-10, coherent=False, formants=[(420, 250, 0), (1050, 400, -10)],
                attack=0.08, release=0.25, seed=304), room=(2.2, 0.28)),
            V(P(0, "call", dur=1.0, f0=tr(0, 110, 1, 220), tilt=-10, coherent=False, breath=0.05,
                formants=[(tr(0, 350, 1, 750), 280, 0), (1300, 450, -10)], attack=0.15, release=0.3, seed=305),
              room=(2.2, 0.28)),
        ]),
        "hurt": ("voice", 24, [
            V(P(0, "call", dur=0.45, f0=tr(0, 120, 1, 80), tilt=-7, sub=0.6, breath=0.35, fry=0.35, fry_rate=26,
                formants=opening(350, 800, 1600), attack=0.01, release=0.2, seed=306), drive=1.8),
        ]),
        "death": ("voice", 32, [
            V(P(0, "call", dur=2.6, f0=tr(0, 140, 0.2, 150, 1, 60), tilt=-10, coherent=False, fry=0.3,
                fry_rate=tr(0, 18, 1, 6), breath=0.1, formants=[(tr(0, 600, 1, 300), 260, 0), (1100, 400, -10)],
                attack=0.1, release=1.0, amp=tr(0, 1, 1, 0.4), seed=307), room=(2.4, 0.3)),
        ]),
    },

    # Archelon: heavy breaths, hisses, low grunts of a giant sea turtle
    "huff_turtle": {
        "ambient": ("voice", 24, [
            V(P(0, "breath", dur=0.5, formants=[(500, 600, 0), (1500, 1000, -6)], attack=0.03, release=0.25, seed=321),
              P(0.6, "breath", 0.7, dur=0.75, formants=[(tr(0, 350, 1, 650), 500, 0), (1400, 1000, -7)], attack=0.35,
                release=0.15, seed=322), room=(1.2, 0.16)),
            V(P(0, "call", dur=0.5, f0=tr(0, 72, 1, 64), tilt=-7, fry=0.7, fry_rate=16, formants=CLOSED_BIG[:3],
                breath=0.15, attack=0.03, release=0.2, seed=323), hiss(0.45, 0.6, 0.5, 0.8, swell=False, seed=324),
              room=(1.2, 0.16)),
            V(P(0, "breath", dur=1.6, formants=[(400, 500, 0), (1200, 900, -6)], lp=2500, attack=0.4, release=0.8,
                seed=325),
              P(0.6, "call", 0.4, dur=0.8, f0=58, tilt=-7.5, fry=0.8, fry_rate=10, formants=CLOSED_BIG[:2], attack=0.1,
                release=0.3, seed=326), room=(1.2, 0.16)),
        ]),
        "hurt": ("voice", 16, [V(hiss(0, 1.0, 0.35, 0.9, swell=False, seed=327),
                                 P(0.02, "call", 0.5, dur=0.25, f0=90, tilt=-7, fry=0.6, fry_rate=22,
                                   formants=CLOSED_MID[:2], attack=0.01, release=0.1, seed=328))]),
        "death": ("voice", 24, [
            V(P(0, "breath", dur=2.2, formants=[(450, 500, 0), (1300, 900, -6)], lp=2500, attack=0.1, release=1.4,
                amp=tr(0, 1, 1, 0.3), seed=329),
              P(0.4, "call", 0.6, dur=1.6, f0=tr(0, 70, 1, 40), tilt=-7, fry=0.8, fry_rate=tr(0, 16, 1, 6),
                formants=CLOSED_BIG[:2], attack=0.1, release=0.8, seed=330), room=(1.2, 0.16)),
        ]),
    },

    # Xiphactinus: the drumming of big fish (a swim-bladder muscle beating fast), grunts and knocks
    "drum_fish": {
        "ambient": ("voice", 24, [
            V(P(0, "call", dur=0.8, f0=tr(0, 26, 1, 22), tilt=-3, formants=[(180, 120, 0), (400, 200, -6)], lp=1200,
                attack=0.04, release=0.2, seed=341), room=(1.4, 0.24)),
            V(*[P(i * 0.32, "call", 1 - i * 0.15, dur=0.18, f0=30, tilt=-3, formants=[(200, 140, 0), (450, 200, -6)],
                  lp=1200, attack=0.01, release=0.08, seed=342 + i) for i in range(3)], room=(1.4, 0.24)),
            V(P(0, "call", dur=1.2, f0=tr(0, 18, 0.5, 30, 1, 20), tilt=-3, formants=[(160, 110, 0), (380, 200, -6)],
                lp=1000, attack=0.1, release=0.3, seed=345), room=(1.4, 0.24)),
        ]),
        "hurt": ("voice", 16, [V(P(0, "call", dur=0.3, f0=45, tilt=-3, formants=[(220, 150, 0), (500, 220, -6)],
                                   lp=1400, attack=0.005, release=0.1, seed=346), drive=1.6)]),
        "death": ("voice", 16, [V(P(0, "call", dur=1.4, f0=tr(0, 34, 1, 8), tilt=-3,
                                    formants=[(200, 140, 0), (450, 200, -6)], lp=1200, attack=0.01, release=0.6,
                                    amp=tr(0, 1, 1, 0.3), seed=347), room=(1.4, 0.24))]),
    },

    # crocodyliforms (Deinosuchus, Baurusuchus): infrasonic bellow with the "water dance" flutter, growls, hisses
    "bellow_croc": {
        "ambient": ("deep", 48, [
            V(P(0, "call", dur=2.2, f0=tr(0, 30, 0.3, 34, 1, 28), tilt=-6, sub=0.2, flutter=(9, 0.55), body=0.27,
                breath=0.06, formants=[(160, 100, 0), (420, 180, -6), (1000, 300, -15)], attack=0.2, release=0.7,
                seed=361), room=(1.6, 0.2)),
            V(P(0, "call", dur=1.6, f0=tr(0, 45, 1, 40), tilt=-7, sub=0.3, fry=0.8, fry_rate=16, fry_sharp=5,
                formants=CLOSED_BIG[:3], breath=0.12, attack=0.15, release=0.5, seed=362), room=(1.4, 0.18)),
            V(hiss(0, 1.0, 1.1, 0.9, seed=363), P(1.15, "clack", 0.7, dur=0.15, freq=600, q=400, seed=364),
              room=(1.2, 0.16)),
        ]),
        "hurt": ("deep", 24, [
            V(hiss(0, 0.8, 0.3, 0.9, swell=False, seed=365),
              P(0.05, "call", dur=0.4, f0=tr(0, 70, 1, 50), tilt=-7, sub=0.5, fry=0.6, fry_rate=24, breath=0.3,
                formants=CLOSED_MID, attack=0.01, release=0.2, seed=366), drive=2.0),
        ]),
        "death": ("deep", 32, [
            V(P(0, "call", dur=2.4, f0=tr(0, 52, 1, 26), tilt=-7, sub=0.3, fry=0.6, fry_rate=tr(0, 18, 1, 6),
                formants=CLOSED_BIG[:3], body=0.18, breath=0.15, attack=0.05, release=1.0, amp=tr(0, 1, 1, 0.4),
                seed=367),
              hiss(2.0, 0.4, 1.0, 0.8, swell=False, seed=368), room=(1.6, 0.2)),
        ]),
        "step": ("ground", 16, [
            V(P(0, "thud", dur=0.3, f0=62, weight=0.7, crunch=0.6, seed=369),
              P(0.05, "breath", 0.3, dur=0.2, formants=[(1500, 1500, 0)], attack=0.01, release=0.15, seed=370),
              room=(0.5, 0.08)),
            V(P(0, "thud", dur=0.3, f0=56, weight=0.7, crunch=0.6, seed=371), room=(0.5, 0.08)),
        ]),
    },

    # Didelphodon (Cretaceous marsupial relative): hisses, growly chatter, sniffing
    "hiss_mammal": {
        "ambient": ("voice", 16, [
            V(hiss(0, 1.0, 0.6, 1.2, seed=381), P(0.62, "clack", 0.5, dur=0.06, freq=2500, q=1200, seed=382),
              P(0.72, "clack", 0.45, dur=0.06, freq=2400, q=1200, seed=383), room=(0.6, 0.1)),
            V(P(0, "call", dur=0.7, f0=260, tilt=-6, fry=0.85, fry_rate=18, fry_sharp=5, breath=0.3,
                formants=[(900, 400, 0), (2200, 600, -6)], attack=0.02, release=0.2, seed=384), room=(0.6, 0.1)),
            V(*[snort(i * 0.15, 0.6, 0.07, 2.2, seed=385 + i) for i in range(3)],
              P(0.55, "trill", 0.4, dur=0.1, f0=tr(0, 2500, 1, 3000), rate=0, harm=0.3, seed=388), room=(0.6, 0.1)),
        ]),
        "hurt": ("voice", 12, [
            V(hiss(0, 0.8, 0.25, 1.3, swell=False, seed=389),
              P(0.03, "call", 0.8, dur=0.25, f0=tr(0, 420, 1, 330), tilt=-6, sub=0.5, breath=0.5,
                formants=[(1000, 450, 0), (2400, 700, -6)], attack=0.005, release=0.1, seed=390), drive=2.0),
        ]),
        "death": ("voice", 16, [
            V(hiss(0, 0.8, 0.9, 1.1, swell=False, seed=391),
              P(0.5, "trill", 0.3, dur=0.3, f0=tr(0, 2400, 1, 1600), rate=0, harm=0.3, seed=392), room=(0.6, 0.1)),
        ]),
        "step": ("ground", 8, [V(P(0, "thud", dur=0.12, f0=140, weight=0.15, crunch=0.9, seed=393))]),
    },
}

# ---------------------------------------------------------------- one voice per species
# Each species gets its OWN voice set, named after it: the archetype above re-voiced for its body (fp = pitch,
# fk = throat/formant scale, tf = timing, rough = grit added) plus a signature sound tied to its anatomy.
_DEFAULT_FORMANTS = ((300, 200, 0), (800, 300, -6), (2000, 500, -14))


def _sc(spec, k):
    if isinstance(spec, (int, float)):
        return spec * k
    return [(t, v * k) for t, v in spec]


def _revoice_part(part, pr):
    start, voice, params, gain = part
    p = dict(params)
    fp, fk, tf = pr["fp"], pr["fk"], pr["tf"]
    for key in ("dur", "attack", "release"):
        if key in p:
            p[key] = p[key] * tf
    if voice == "call":
        p["f0"] = _sc(p.get("f0", 100), fp)
        p["formants"] = [(_sc(f, fk), bw * fk, g) for f, bw, g in p.get("formants", _DEFAULT_FORMANTS)]
        if p.get("tube"):
            p["tube"] = (_sc(p["tube"][0], fk), p["tube"][1])
        if p.get("notch"):
            f, bw, d = p["notch"]
            p["notch"] = (_sc(f, fk), bw * fk, d)
        if p.get("lp"):
            p["lp"] = p["lp"] * fk
        if "fry_rate" in p:
            p["fry_rate"] = _sc(p["fry_rate"], fp ** 0.5)
        if pr["rough"]:
            p["sub"] = min(0.95, p.get("sub", 0.0) + pr["rough"])
            if p.get("fry", 0.0) > 0:
                p["fry"] = min(0.95, p["fry"] + pr["rough"] * 0.5)
        if pr.get("flutter") and p.get("flutter", (0, 0))[1] > 0:
            p["flutter"] = (pr["flutter"], p["flutter"][1])
    elif voice == "breath":
        p["formants"] = [(_sc(f, fk), bw * fk, g) for f, bw, g in p.get("formants", ((900, 900, 0),))]
        for key in ("lp", "hp"):
            if p.get(key):
                p[key] = p[key] * fk
    elif voice == "thud":
        p["f0"] = p.get("f0", 46) * fp ** 0.5
    elif voice == "clack":
        p["freq"] = p.get("freq", 900) * fk
    elif voice == "trill":
        p["f0"] = _sc(p.get("f0", 3000), fp)
    elif voice == "flap":
        p["size"] = p.get("size", 1.0) / fk
    p["seed"] = p.get("seed", 0) + pr["seed"]
    return (start * tf, voice, p, gain)


def _revoice(variant, pr):
    kind, voice, params = variant
    p = dict(params)
    p["parts"] = [_revoice_part(part, pr) for part in params["parts"]]
    return (kind, voice, p)


def species_voice(arch, fp=1.0, fk=1.0, tf=1.0, rough=0.0, seed=0, flutter=None, steps=True, sig=None):
    """An archetype re-voiced for one species. sig: {event: [variants]} added after the archetype's own
    (they are written for this species and are not re-voiced)."""
    pr = dict(fp=fp, fk=fk, tf=tf, rough=rough, seed=seed, flutter=flutter)
    out = {}
    for ev, (fx, dist, variants) in ARCHETYPES[arch].items():
        if ev == "step" and not steps:
            continue
        out[ev] = (fx, dist, [_revoice(v, pr) for v in variants])
    for ev, extra in (sig or {}).items():
        fx, dist, variants = out.get(ev, ("voice", 32, []))
        out[ev] = (fx, dist, variants + extra)
    return out


def boom(start, f0, dur=2.0, gain=1.0, flutter=(7.0, 0.4), formants=None, seed=0, **kw):
    """Closed-mouth boom helper for signatures."""
    return P(start, "call", gain, dur=dur, f0=f0, tilt=-7, sub=kw.pop("sub", 0.2), flutter=flutter, breath=0.06,
             formants=formants or CLOSED_HUGE, body=kw.pop("body", 0.2), attack=kw.pop("attack", dur * 0.15),
             release=kw.pop("release", dur * 0.35), seed=seed, **kw)


# species -> its voice set. The set is named after the species and the pitch is baked into the sounds (1.0).
SPECIES = {
    # ---- big theropods
    "tyrannosaurus": ("boom_large", dict(fp=1.0, fk=1.0, tf=1.1, seed=1000, sig={"ambient": [
        V(exhale(0, 0.3, 0.7, 0.7, seed=1001),
          boom(0.6, tr(0, 40, 0.5, 47, 1, 37), 3.2, flutter=(5.5, 0.5), sub=0.3, seed=1002),
          room=(2.0, 0.24))]})),
    "tarbosaurus": ("boom_large", dict(fp=1.05, fk=1.05, tf=1.0, rough=0.05, seed=1010, sig={"ambient": [
        V(boom(0, tr(0, 48, 1, 44), 1.6, seed=1011), P(1.7, "clack", 0.7, freq=560, q=380, seed=1012),
          P(1.85, "clack", 0.6, freq=600, q=380, seed=1013),
          P(2.1, "call", dur=1.2, f0=tr(0, 60, 1, 50), tilt=-7, sub=0.4, fry=0.6, fry_rate=24, formants=CLOSED_BIG,
            breath=0.15, attack=0.1, release=0.4, seed=1014), room=(1.6, 0.2))]})),
    "daspletosaurus": ("boom_large", dict(fp=1.08, fk=1.08, tf=0.9, rough=0.15, seed=1020, sig={"ambient": [
        V(snort(0, 0.6, 0.2, 0.8, seed=1021),
          P(0.25, "call", dur=2.6, f0=tr(0, 56, 1, 48), tilt=-7, sub=0.5, fry=0.85, fry_rate=tr(0, 16, 0.5, 22, 1, 14),
            fry_sharp=6, formants=CLOSED_BIG, breath=0.2, attack=0.2, release=0.6, seed=1022), room=(1.5, 0.2))]})),
    "albertosaurus": ("boom_large", dict(fp=1.2, fk=1.2, tf=0.85, rough=0.05, seed=1030, sig={"ambient": [
        V(*[P(i * 0.28, "call", 0.9, dur=0.2, f0=tr(0, 82, 1, 70), tilt=-7, sub=0.4, breath=0.25,
              formants=CLOSED_BIG, attack=0.01, release=0.1, seed=1031 + i) for i in range(3)],
          boom(0.95, tr(0, 58, 1, 50), 1.3, seed=1034), room=(1.4, 0.18))]})),
    "giganotosaurus": ("boom_large", dict(fp=0.92, fk=0.94, tf=1.15, rough=0.1, seed=1040, sig={"ambient": [
        V(hiss(0, 0.6, 1.0, 0.6, seed=1041), boom(0.7, tr(0, 38, 0.4, 46, 1, 34), 2.8, flutter=(6.5, 0.45),
                                                    sub=0.35, seed=1042), room=(2.0, 0.25))]})),
    "carcharodontosaurus": ("boom_large", dict(fp=0.96, fk=0.97, tf=1.0, rough=0.2, seed=1050, sig={"ambient": [
        V(P(0, "call", dur=2.4, f0=tr(0, 50, 1, 44), tilt=-6.5, sub=0.55, fry=0.9, fry_rate=tr(0, 12, 0.6, 30, 1, 18),
            fry_sharp=5, formants=CLOSED_BIG, breath=0.25, breath_color=1, attack=0.2, release=0.6, seed=1051),
          P(2.3, "clack", 0.7, freq=520, q=360, seed=1052), room=(1.6, 0.2))]})),
    "spinosaurus": ("boom_large", dict(fp=1.1, fk=1.0, tf=1.0, flutter=10.0, seed=1060, sig={"ambient": [
        V(boom(0, tr(0, 34, 0.3, 38, 1, 32), 2.4, flutter=(11, 0.6), sub=0.25, seed=1061),
          hiss(2.0, 0.5, 0.6, 0.8, swell=False, seed=1062), P(2.65, "clack", 0.8, freq=900, q=500, seed=1063),
          room=(1.6, 0.22))]})),
    # ---- mid theropods
    "carnotaurus": ("growl_theropod", dict(fp=1.0, fk=1.0, tf=1.0, seed=1100, sig={"ambient": [
        V(snort(0, 0.9, 0.14, 1.0, seed=1101), snort(0.2, 0.8, 0.14, 1.0, seed=1102),
          P(0.45, "call", dur=0.7, f0=tr(0, 92, 1, 80), tilt=-6, sub=0.35, tube=(110, 0.6), fry=0.4, fry_rate=26,
            formants=CLOSED_MID[:3], notch=(900, 300, 0.6), breath=0.15, attack=0.03, release=0.3, seed=1103),
          room=(1.2, 0.16))]})),
    "majungasaurus": ("growl_theropod", dict(fp=1.06, fk=1.05, tf=1.1, rough=0.15, seed=1110, sig={"ambient": [
        V(*[P(i * 0.13, "clack", 0.6, dur=0.08, freq=850 + 60 * (i % 2), q=500, seed=1111 + i) for i in range(4)],
          P(0.6, "call", dur=1.5, f0=tr(0, 70, 1, 60), tilt=-7, sub=0.4, fry=0.75, fry_rate=18, formants=CLOSED_BIG,
            breath=0.2, attack=0.1, release=0.5, seed=1115), room=(1.2, 0.16))]})),
    "dilophosaurus": ("growl_theropod", dict(fp=1.35, fk=1.3, tf=0.85, seed=1120, sig={"ambient": [
        V(P(0, "breath", 0.9, dur=0.9, formants=[(3200, 2600, 0), (6000, 3000, -5)], hp=1200, flutter=(35, 0.8),
            attack=0.2, release=0.3, seed=1121),
          P(0.3, "call", 0.7, dur=0.7, f0=160, tilt=-6, fry=0.9, fry_rate=45, fry_sharp=6, breath=0.25,
            formants=[(520, 260, 0), (1400, 420, -5)], attack=0.1, release=0.25, seed=1122), room=(1.0, 0.15))]})),
    # ---- raptors, small predators
    "velociraptor": ("rattle_raptor", dict(fp=1.15, fk=1.15, tf=0.9, seed=1200, steps=False, sig={"ambient": [
        V(*[P(i * 0.11, "call", 1 - i * 0.08, dur=0.08, f0=tr(0, 190 - i * 6, 1, 170 - i * 6), tilt=-6, fry=0.8,
              fry_rate=60, breath=0.3, formants=[(520, 260, 0), (1350, 400, -5)], attack=0.005, release=0.04,
              seed=1201 + i) for i in range(6)], room=(0.9, 0.14))]})),
    "dakotaraptor": ("rattle_raptor", dict(fp=0.85, fk=0.85, tf=1.15, rough=0.1, seed=1210, sig={"ambient": [
        V(boom(0, tr(0, 92, 1, 84), 0.9, flutter=(0, 0), formants=CLOSED_MID[:3], seed=1211, body=0.1),
          P(0.85, "call", dur=0.7, f0=110, tilt=-7, fry=0.9, fry_rate=tr(0, 34, 1, 16), fry_sharp=6, breath=0.2,
            formants=[(380, 200, 0), (950, 300, -6)], attack=0.02, release=0.3, seed=1212), room=(1.0, 0.15))]})),
    "troodon": ("rattle_raptor", dict(fp=1.25, fk=1.3, tf=1.0, seed=1220, sig={"ambient": [
        V(P(0, "trill", dur=1.1, f0=tr(0, 1150, 0.4, 1550, 1, 1050), rate=0, harm=0.25, attack=0.15, release=0.4,
            seed=1221),
          P(1.0, "call", 0.5, dur=0.5, f0=150, tilt=-7, fry=0.85, fry_rate=36, formants=[(450, 220, 0), (1200, 350, -6)],
            breath=0.2, attack=0.02, release=0.2, seed=1222), room=(1.4, 0.22))]})),
    "compsognathus": ("trill_small", dict(seed=1300, steps=False, sig={"ambient": [
        V(*[P(i * 0.12, "trill", 1 - i * 0.1, dur=0.09, f0=tr(0, 4300 - i * 250, 1, 3500 - i * 250), rate=0,
              harm=0.2, seed=1301 + i) for i in range(5)], room=(0.6, 0.12))]})),
    "mononykus": ("trill_small", dict(fp=1.15, fk=1.1, tf=0.85, seed=1310, sig={"ambient": [
        V(P(0, "trill", dur=0.6, f0=tr(0, 4600, 1, 4400), rate=60, sharp=2.0, harm=0.3, seed=1311),
          *[P(0.7 + i * 0.09, "clack", 0.5, dur=0.05, freq=2600, q=1200, seed=1312 + i) for i in range(5)],
          room=(0.5, 0.1))]})),
    "didelphodon": ("hiss_mammal", dict(seed=1320, sig={"ambient": [
        V(*[P(i * 0.05, "clack", 0.5, dur=0.04, freq=3000 + 200 * (i % 3), q=1400, seed=1321 + i) for i in range(10)],
          P(0.55, "call", 0.7, dur=0.5, f0=200, tilt=-6, fry=0.85, fry_rate=22, breath=0.3,
            formants=[(800, 380, 0), (2000, 600, -6)], attack=0.02, release=0.15, seed=1331), room=(0.6, 0.1))]})),
    # ---- feathered plant eaters
    "oviraptor": ("drum_ratite", dict(fp=1.18, fk=1.15, tf=0.9, seed=1400, steps=False, sig={"ambient": [
        V(P(0, "call", dur=0.9, f0=tr(0, 88, 0.6, 118, 1, 112), tilt=-7, tube=(82, 0.55), formants=CLOSED_MID[:2],
            body=0.15, breath=0.06, attack=0.08, release=0.3, seed=1401), room=(1.0, 0.15))]})),
    "citipati": ("drum_ratite", dict(fp=1.05, fk=1.05, tf=1.05, seed=1410, steps=False, sig={"ambient": [
        V(P(0, "call", dur=2.2, f0=tr(0, 68, 1, 64), tilt=-8, fry=0.7, fry_rate=14, fry_sharp=3,
            formants=CLOSED_BIG[:2], body=0.15, breath=0.08, attack=0.4, release=0.8, amp=tr(0, 0.6, 0.5, 1, 1, 0.6),
            seed=1411), P(2.0, "call", 0.6, dur=0.6, f0=tr(0, 80, 1, 74), tilt=-8, tube=(82, 0.5),
                          formants=CLOSED_BIG[:2], attack=0.1, release=0.3, seed=1412), room=(1.0, 0.15))]})),
    "gallimimus": ("drum_ratite", dict(fp=1.0, fk=1.0, tf=0.85, seed=1420, steps=False, sig={"ambient": [
        V(*[P(i * 0.22, "call", 1 - i * 0.12, dur=0.16, f0=tr(0, 112, 1, 104), tilt=-7, tube=(110, 0.5),
              formants=CLOSED_MID[:2], breath=0.08, attack=0.02, release=0.08, seed=1421 + i) for i in range(3)],
          room=(1.0, 0.15))]})),
    "struthiomimus": ("drum_ratite", dict(fp=1.06, fk=1.03, tf=1.0, seed=1430, steps=False, sig={"ambient": [
        V(boom(0, 62, 0.35, flutter=(0, 0), formants=CLOSED_BIG[:2], seed=1431),
          boom(0.5, 60, 0.35, flutter=(0, 0), formants=CLOSED_BIG[:2], seed=1432),
          boom(1.0, tr(0, 60, 0.3, 66, 1, 54), 1.6, flutter=(4, 0.2), formants=CLOSED_BIG[:2], seed=1433),
          room=(1.2, 0.18))]})),
    "therizinosaurus": ("drum_ratite", dict(fp=0.75, fk=0.8, tf=1.2, rough=0.05, seed=1440, sig={"ambient": [
        V(boom(0, tr(0, 52, 1, 46), 1.5, flutter=(3, 0.2), formants=CLOSED_BIG[:3], tube=(70, 0.5), seed=1441),
          *[P(1.5 + i * 0.16, "clack", 0.6, dur=0.07, freq=1700 + 120 * i, q=700, seed=1442 + i) for i in range(3)],
          room=(1.4, 0.2))]})),
    "deinocheirus": ("drum_ratite", dict(fp=0.68, fk=0.75, tf=1.25, rough=0.1, seed=1450, sig={"ambient": [
        V(boom(0, tr(0, 44, 1, 40), 2.0, flutter=(2.2, 0.55), formants=CLOSED_BIG[:3], seed=1451),
          P(1.9, "breath", 0.6, dur=0.5, formants=[(300, 300, 0), (900, 600, -6)], lp=1800, attack=0.05,
            release=0.3, seed=1452), room=(1.6, 0.22))]})),
    # ---- ornithopods
    "parasaurolophus": ("horn_hadrosaur", dict(fp=1.0, fk=1.0, tf=1.05, seed=1500, sig={"ambient": [
        V(P(0, "call", dur=3.4, f0=tr(0, 55, 0.5, 58, 0.85, 66, 1, 60), tilt=-5, jitter=0.006, breath=0.12,
            formants=[(tr(0, 380, 0.5, 520, 0.85, 760, 1, 520), 260, 0), (1300, 420, -6), (2500, 600, -14)],
            tube=(48, 0.84), flutter=(4.0, 0.08), attack=0.3, release=0.8, seed=1501), room=(2.4, 0.3))]})),
    "corythosaurus": ("horn_hadrosaur", dict(fp=1.25, fk=1.25, tf=0.85, seed=1510, sig={"ambient": [
        V(P(0, "call", dur=0.35, f0=78, tilt=-5, breath=0.1, formants=[(560, 280, 0), (1500, 450, -6)],
            tube=(64, 0.8), attack=0.03, release=0.1, seed=1511),
          P(0.45, "call", dur=1.3, f0=tr(0, 84, 1, 76), tilt=-5, breath=0.1, formants=[(tr(0, 500, 1, 700), 280, 0),
                                                                                    (1600, 450, -6)],
            tube=(64, 0.82), flutter=(5, 0.08), attack=0.06, release=0.45, seed=1512), room=(2.0, 0.26))]})),
    "edmontosaurus": ("bellow_hadrosaur", dict(fp=0.9, fk=0.92, tf=1.1, rough=0.05, seed=1520, sig={"ambient": [
        V(boom(0, tr(0, 46, 1, 42), 1.4, flutter=(3, 0.3), formants=CLOSED_HUGE[:3], seed=1521, body=0.3),
          P(1.3, "call", dur=0.7, f0=tr(0, 72, 1, 62), tilt=-6, sub=0.3, tube=(70, 0.55), formants=CLOSED_BIG,
            notch=(750, 250, 0.8), attack=0.04, release=0.3, seed=1522), room=(1.8, 0.22))]})),
    "maiasaura": ("bellow_hadrosaur", dict(fp=1.08, fk=1.05, tf=0.95, seed=1530, sig={"ambient": [
        V(P(0, "call", 0.8, dur=0.8, f0=tr(0, 70, 1, 66), tilt=-8, tube=(70, 0.5), formants=CLOSED_BIG[:3],
            notch=(760, 260, 0.8), attack=0.15, release=0.35, seed=1531),
          P(1.0, "call", 0.7, dur=1.0, f0=tr(0, 68, 1, 60), tilt=-8, tube=(70, 0.5), formants=CLOSED_BIG[:3],
            notch=(760, 260, 0.8), attack=0.15, release=0.45, seed=1532), room=(1.6, 0.2))]})),
    "pachycephalosaurus": ("grunt_ornithopod", dict(fp=1.0, fk=1.0, tf=1.0, seed=1540, sig={"ambient": [
        V(P(0, "clack", 0.9, dur=0.15, freq=380, q=260, seed=1541), P(0.35, "clack", 0.8, dur=0.15, freq=360, q=260,
                                                                       seed=1542),
          P(0.7, "call", dur=0.6, f0=tr(0, 78, 1, 70), tilt=-7, tube=(95, 0.6), formants=CLOSED_MID[:2], fry=0.3,
            fry_rate=20, attack=0.04, release=0.25, seed=1543), room=(1.2, 0.18))]})),
    "thescelosaurus": ("grunt_ornithopod", dict(fp=1.25, fk=1.25, tf=0.85, seed=1550, sig={"ambient": [
        V(*[P(i * 0.2, "call", 0.9, dur=0.12, f0=tr(0, 132, 1, 118), tilt=-7, tube=(120, 0.5), fry=0.4, fry_rate=30,
              formants=CLOSED_MID[:2], breath=0.15, attack=0.01, release=0.06, seed=1551 + i) for i in range(3)],
          room=(0.9, 0.14))]})),
    # ---- ceratopsians, armoured
    "triceratops": ("snort_ceratopsian", dict(fp=1.0, fk=1.0, tf=1.0, seed=1600, sig={"ambient": [
        V(snort(0, 1.0, 0.25, 0.8, seed=1601),
          P(0.35, "call", dur=1.3, f0=tr(0, 56, 0.3, 64, 1, 48), tilt=-7, sub=0.45, breath=0.2,
            formants=CLOSED_BIG, attack=0.08, release=0.5, seed=1602),
          P(1.8, "clack", 0.6, dur=0.18, freq=420, q=260, seed=1603), room=(1.3, 0.18))]})),
    "styracosaurus": ("snort_ceratopsian", dict(fp=1.1, fk=1.08, tf=0.9, rough=0.05, seed=1610, sig={"ambient": [
        V(*[P(i * 0.09, "clack", 0.7, dur=0.1, freq=650 + 80 * i, q=380, seed=1611 + i) for i in range(4)],
          snort(0.5, 1.0, 0.16, 1.1, seed=1615), room=(1.0, 0.15))]})),
    "pachyrhinosaurus": ("snort_ceratopsian", dict(fp=1.04, fk=1.02, tf=1.05, rough=0.1, seed=1620, sig={"ambient": [
        V(*[snort(i * 0.3, 1 - i * 0.2, 0.2, 0.7 - i * 0.05, seed=1621 + i) for i in range(3)],
          P(1.0, "call", dur=0.7, f0=tr(0, 62, 1, 54), tilt=-7, sub=0.5, fry=0.5, fry_rate=20, formants=CLOSED_BIG,
            attack=0.05, release=0.3, seed=1624), room=(1.2, 0.16))]})),
    "protoceratops": ("snort_ceratopsian", dict(fp=1.45, fk=1.5, tf=0.75, seed=1630, steps=False, sig={"ambient": [
        V(snort(0, 0.8, 0.08, 2.0, seed=1631),
          P(0.12, "call", dur=0.25, f0=tr(0, 170, 1, 140), tilt=-6, fry=0.6, fry_rate=34, sub=0.3,
            formants=[(500, 260, 0), (1300, 400, -6)], breath=0.2, attack=0.01, release=0.1, seed=1632),
          snort(0.5, 0.6, 0.08, 2.0, seed=1633), room=(0.8, 0.12))]})),
    "ankylosaurus": ("honk_armored", dict(fp=1.0, fk=1.0, tf=1.0, seed=1700, sig={"ambient": [
        V(P(0, "call", dur=1.8, f0=tr(0, 84, 0.4, 92, 1, 74), tilt=-6, tube=(130, 0.82),
            formants=[(260, 150, 0), (780, 260, -6)], notch=(1100, 300, 0.6), breath=0.15, attack=0.1, release=0.5,
            seed=1701),
          P(1.6, "breath", 0.5, dur=0.6, formants=[(800, 700, 0)], tube=(150, 0.6), attack=0.05, release=0.4,
            seed=1702), room=(1.3, 0.18))]})),
    "euoplocephalus": ("honk_armored", dict(fp=1.08, fk=1.1, tf=0.95, rough=0.05, seed=1710, sig={"ambient": [
        V(P(0, "breath", 0.9, dur=0.7, formants=[(900, 700, 0), (2200, 1200, -6)], tube=(150, 0.7), attack=0.2,
            release=0.2, seed=1711),
          P(0.75, "call", dur=0.5, f0=tr(0, 96, 1, 86), tilt=-6, tube=(150, 0.75), formants=[(300, 160, 0),
                                                                                     (850, 280, -6)],
            attack=0.03, release=0.2, seed=1712), room=(1.1, 0.16))]})),
    "stegosaurus": ("honk_armored", dict(fp=0.9, fk=0.95, tf=1.1, seed=1720, sig={"ambient": [
        V(P(0, "call", dur=0.5, f0=70, tilt=-8, tube=(100, 0.6), formants=CLOSED_BIG[:2], body=0.15, attack=0.05,
            release=0.2, seed=1721),
          P(0.65, "call", dur=0.8, f0=tr(0, 66, 1, 58), tilt=-8, tube=(100, 0.6), formants=CLOSED_BIG[:2], body=0.15,
            attack=0.05, release=0.35, seed=1722), room=(1.3, 0.18))]})),
    # ---- sauropods
    "brachiosaurus": ("rumble_sauropod", dict(fp=1.0, fk=1.0, tf=1.0, seed=1800, sig={"ambient": [
        V(P(0, "call", dur=3.4, f0=tr(0, 36, 0.7, 60, 1, 56), tilt=-6, tube=(44, 0.82),
            formants=[(tr(0, 260, 1, 420), 200, 0), (800, 260, -8)], breath=0.08, body=0.15, attack=0.5, release=0.9,
            seed=1801), room=(2.8, 0.3))]})),
    "alamosaurus": ("rumble_sauropod", dict(fp=0.95, fk=0.96, tf=1.05, seed=1810, sig={"ambient": [
        V(P(0, "call", dur=3.0, f0=tr(0, 38, 1, 35), tilt=-7, formants=CLOSED_HUGE[:3], flutter=(1.5, 0.7),
            body=0.2, attack=0.4, release=0.8, seed=1811), room=(2.6, 0.28))]})),
    "saltasaurus": ("rumble_sauropod", dict(fp=1.3, fk=1.3, tf=0.85, seed=1820, sig={"ambient": [
        V(*[P(i * 0.7, "call", 1 - i * 0.15, dur=0.55, f0=tr(0, 56, 1, 50), tilt=-7, tube=(60, 0.65),
              formants=CLOSED_BIG[:3], attack=0.08, release=0.25, seed=1821 + i) for i in range(3)],
          room=(2.0, 0.26))]})),
    "argentinosaurus": ("rumble_sauropod", dict(fp=0.8, fk=0.82, tf=1.25, rough=0.05, seed=1830, sig={"ambient": [
        V(P(0, "call", dur=4.6, f0=tr(0, 28, 0.5, 32, 1, 24), tilt=-6.5, formants=CLOSED_HUGE[:3], tube=(34, 0.6),
            flutter=(2, 0.15), body=0.25, breath=0.06, attack=0.8, release=1.4, seed=1831), room=(3.0, 0.32))]})),
    "opisthocoelicaudia": ("rumble_sauropod", dict(fp=1.12, fk=1.12, tf=0.95, rough=0.1, seed=1840, sig={"ambient": [
        V(P(0, "call", dur=0.9, f0=tr(0, 50, 1, 44), tilt=-7, sub=0.4, fry=0.6, fry_rate=14, formants=CLOSED_BIG,
            attack=0.1, release=0.35, seed=1841),
          P(1.1, "call", dur=1.1, f0=tr(0, 46, 1, 40), tilt=-7, sub=0.4, fry=0.6, fry_rate=12, formants=CLOSED_BIG,
            attack=0.1, release=0.45, seed=1842), room=(2.2, 0.26))]})),
    "dreadnoughtus": ("rumble_sauropod", dict(fp=0.85, fk=0.88, tf=1.15, rough=0.05, seed=1850, sig={"ambient": [
        V(P(0, "call", dur=3.2, f0=tr(0, 32, 0.5, 38, 1, 30), tilt=-6.5, formants=CLOSED_HUGE[:3], flutter=(4, 0.55),
            body=0.2, attack=0.5, release=1.0, seed=1851),
          P(3.0, "breath", 0.8, dur=1.4, formants=[(250, 250, 0), (700, 500, -6)], lp=1400, attack=0.1,
            release=0.9, seed=1852), room=(2.8, 0.3))]})),
    # ---- skies
    "pteranodon": ("squawk_pterosaur", dict(fp=1.0, fk=1.0, tf=1.0, seed=1900, sig={"ambient": [
        V(P(0, "call", dur=0.35, f0=tr(0, 200, 1, 250), tilt=-5, sub=0.7, breath=0.35, jitter=0.03,
            formants=[(650, 350, 0), (1450, 450, -3)], lp=5000, attack=0.02, release=0.1, seed=1901),
          P(0.45, "call", dur=0.5, f0=tr(0, 250, 1, 180), tilt=-5, sub=0.75, breath=0.4, jitter=0.03,
            formants=[(680, 350, 0), (1500, 450, -3)], lp=5000, attack=0.02, release=0.2, seed=1902),
          room=(1.0, 0.16), drive=2.0)]})),
    "quetzalcoatlus": ("squawk_pterosaur", dict(fp=0.7, fk=0.72, tf=1.25, rough=0.05, seed=1910, sig={"ambient": [
        V(hiss(0, 0.7, 0.6, 0.7, seed=1911),
          P(0.5, "call", dur=0.8, f0=tr(0, 125, 1, 105), tilt=-5, sub=0.8, breath=0.45, jitter=0.04,
            formants=[(480, 260, 0), (1050, 350, -3), (2000, 500, -10)], lp=4000, attack=0.03, release=0.3,
            seed=1912), room=(1.3, 0.2), drive=2.0)]})),
    "hatzegopteryx": ("squawk_pterosaur", dict(fp=0.64, fk=0.68, tf=1.3, rough=0.15, seed=1920, sig={"ambient": [
        V(P(0, "call", dur=1.2, f0=tr(0, 92, 1, 80), tilt=-6, sub=0.9, fry=0.6, fry_rate=22, breath=0.35,
            formants=[(420, 220, 0), (950, 320, -4)], lp=3500, attack=0.05, release=0.4, seed=1921),
          P(1.15, "clack", 0.9, dur=0.12, freq=700, q=400, seed=1922), room=(1.4, 0.2), drive=2.2)]})),
    "ichthyornis": ("cry_seabird", dict(seed=1930, sig={"ambient": [
        V(P(0, "call", dur=0.1, f0=tr(0, 1500, 1, 1300), tilt=-5, sub=0.3, breath=0.2,
            formants=[(2600, 1200, 0), (4300, 1500, -6)], attack=0.005, release=0.04, seed=1931),
          P(0.16, "call", dur=0.12, f0=tr(0, 1450, 1, 1250), tilt=-5, sub=0.3, breath=0.2,
            formants=[(2600, 1200, 0), (4300, 1500, -6)], attack=0.005, release=0.05, seed=1932),
          room=(0.8, 0.14))]})),
    # ---- inland sea and rivers
    "hesperornis": ("wail_diver", dict(seed=1940, sig={"ambient": [
        V(P(0, "call", dur=0.6, f0=tr(0, 300, 1, 260), tilt=-7, sub=0.5, breath=0.3,
            formants=[(800, 400, 0), (1900, 600, -6)], fry=0.4, fry_rate=30, attack=0.02, release=0.25, seed=1941),
          room=(1.4, 0.2))]})),
    "mosasaurus": ("blow_mosasaur", dict(fp=1.0, fk=1.0, tf=1.0, seed=2000, sig={"ambient": [
        V(P(0, "call", dur=3.0, f0=tr(0, 36, 0.5, 44, 1, 34), tilt=-7, formants=CLOSED_HUGE[:3], lp=1000,
            flutter=(3, 0.25), body=0.25, attack=0.6, release=1.0, seed=2001), room=(2.6, 0.34))]})),
    "tylosaurus": ("blow_mosasaur", dict(fp=1.08, fk=1.1, tf=0.9, seed=2010, sig={"ambient": [
        V(P(0, "clack", 1.0, dur=0.2, freq=300, q=220, seed=2011), P(0.3, "clack", 0.9, dur=0.2, freq=320, q=220,
                                                                      seed=2012),
          P(0.7, "breath", dur=0.5, formants=[(500, 500, 0), (1800, 1500, -4)], attack=0.01, release=0.3,
            seed=2013), room=(1.6, 0.22))]})),
    "elasmosaurus": ("moan_plesiosaur", dict(seed=2020, sig={"ambient": [
        V(P(0, "call", dur=1.4, f0=tr(0, 100, 1, 120), tilt=-11, coherent=False, formants=[(400, 250, 0),
                                                                                       (1100, 400, -10)],
            attack=0.3, release=0.4, seed=2021),
          P(1.5, "call", dur=1.6, f0=tr(0, 150, 1, 90), tilt=-11, coherent=False, formants=[(500, 250, 0),
                                                                                      (1200, 400, -10)],
            flutter=(5, 0.12), attack=0.2, release=0.6, seed=2022), room=(2.6, 0.32))]})),
    "archelon": ("huff_turtle", dict(seed=2030, sig={"ambient": [
        V(P(0, "clack", 0.9, dur=0.12, freq=1100, q=600, seed=2031),
          P(0.25, "breath", dur=0.7, formants=[(450, 500, 0), (1300, 900, -6)], attack=0.05, release=0.4,
            seed=2032), room=(1.0, 0.14))]})),
    "xiphactinus": ("drum_fish", dict(seed=2040, sig={"ambient": [
        V(P(0, "call", dur=1.4, f0=tr(0, 20, 0.5, 42, 1, 18), tilt=-3, formants=[(200, 140, 0), (450, 200, -6)],
            lp=1200, attack=0.1, release=0.3, seed=2041), room=(1.4, 0.24))]})),
    "deinosuchus": ("bellow_croc", dict(fp=1.0, fk=1.0, tf=1.1, seed=2100, sig={"ambient": [
        V(P(0, "call", dur=3.0, f0=tr(0, 26, 0.3, 30, 1, 24), tilt=-6, sub=0.25, flutter=(10, 0.6), body=0.3,
            breath=0.06, formants=[(150, 100, 0), (400, 180, -6), (950, 300, -15)], attack=0.3, release=0.9,
            seed=2101), room=(1.8, 0.24))]})),
    "baurusuchus": ("bellow_croc", dict(fp=1.35, fk=1.35, tf=0.85, rough=0.1, seed=2110, sig={"ambient": [
        V(hiss(0, 0.8, 0.5, 1.0, seed=2111),
          P(0.4, "call", dur=0.9, f0=tr(0, 72, 1, 62), tilt=-6, sub=0.6, fry=0.7, fry_rate=26, breath=0.35,
            formants=CLOSED_MID[:3], attack=0.03, release=0.35, seed=2112),
          P(1.3, "clack", 0.8, dur=0.15, freq=700, q=400, seed=2113), room=(1.1, 0.16), drive=1.8)]})),
}

# species that have no footsteps of their own in gen_species.py (their step sounds would be unused)
_NO_STEPS = {"dilophosaurus", "velociraptor", "compsognathus", "oviraptor", "citipati", "gallimimus", "struthiomimus",
             "protoceratops"}

VOICE_SETS = {}
for _sid, (_arch, _prof) in SPECIES.items():
    _prof = dict(_prof)
    if _sid in _NO_STEPS:
        _prof["steps"] = False
    VOICE_SETS[_sid] = species_voice(_arch, **_prof)

# a soft low cut on every sound: the felt sub-bass stays, but the energy moves up where speakers can play it
for _events in VOICE_SETS.values():
    for _ev, (_fx, _dist, _variants) in _events.items():
        for _v in _variants:
            if _v[1] == "mix" and _v[2].get("hp") is None:
                _v[2]["hp"] = 40 if _ev == "step" else 60

# species -> (voice set, pitch). Every species has its own set; the pitch is baked in.
SPECIES_VOICE = {sid: (sid, 1.0) for sid in SPECIES}
ARCHETYPE_OF = {sid: arch for sid, (arch, _) in SPECIES.items()}

# what each set sounds like, per event (pt_br, en_us, es_es); hurt/death/step/flap are shared below
_AMBIENT = {
    "boom_large": ("Estrondo grave", "Deep boom", "Retumbo grave"),
    "growl_theropod": ("Rosnado rouco", "Raspy growl", "Gruñido ronco"),
    "rattle_raptor": ("Chocalhar de garganta", "Throat rattle", "Traqueteo de garganta"),
    "trill_small": ("Trinado agudo", "High trill", "Trino agudo"),
    "drum_ratite": ("Tamborilar grave", "Low drumming", "Tamborileo grave"),
    "horn_hadrosaur": ("Chamado de crista", "Crest call", "Llamada de cresta"),
    "bellow_hadrosaur": ("Bramido nasal", "Nasal bellow", "Bramido nasal"),
    "snort_ceratopsian": ("Bufo pesado", "Heavy snort", "Bufido pesado"),
    "honk_armored": ("Buzina nasal", "Nasal honk", "Bocinazo nasal"),
    "rumble_sauropod": ("Ronco profundo", "Deep rumble", "Rugido profundo"),
    "grunt_ornithopod": ("Grunhido oco", "Hollow grunt", "Gruñido hueco"),
    "squawk_pterosaur": ("Pterossauro grasna", "Pterosaur croaks", "Pterosaurio grazna"),
    "cry_seabird": ("Grito de ave marinha", "Seabird cries", "Grito de ave marina"),
    "wail_diver": ("Lamento de mergulhador", "Diver wails", "Lamento de buceador"),
    "blow_mosasaur": ("Mosassauro bufa", "Mosasaur blows", "Mosasaurio resopla"),
    "moan_plesiosaur": ("Gemido marinho", "Sea moan", "Gemido marino"),
    "huff_turtle": ("Tartaruga respira", "Turtle huffs", "Tortuga resopla"),
    "drum_fish": ("Peixe tamborila", "Fish drums", "Pez tamborilea"),
    "bellow_croc": ("Bramido de crocodilo", "Crocodile bellows", "Bramido de cocodrilo"),
    "hiss_mammal": ("Chiado", "Hiss", "Siseo"),
}
_THREAT = {
    "boom_large": ("Rugido ameaçador", "Threatening roar", "Rugido amenazante"),
    "growl_theropod": ("Silvo e rosnado", "Hiss and growl", "Siseo y gruñido"),
}
_SHARED = {
    "hurt": ("Dinossauro ferido", "Dinosaur hurts", "Dinosaurio herido"),
    "death": ("Dinossauro morre", "Dinosaur dies", "Dinosaurio muere"),
    "step": ("Passos pesados", "Heavy footsteps", "Pasos pesados"),
    "flap": ("Bater de asas", "Wings flap", "Aleteo"),
}
_CREATURE = {  # sets of animals that are not dinosaurs get their own hurt/death subtitles
    "squawk_pterosaur": (("Pterossauro ferido", "Pterosaur hurts", "Pterosaurio herido"),
                         ("Pterossauro morre", "Pterosaur dies", "Pterosaurio muere")),
    "cry_seabird": (("Ave ferida", "Bird hurts", "Ave herida"), ("Ave morre", "Bird dies", "Ave muere")),
    "wail_diver": (("Ave ferida", "Bird hurts", "Ave herida"), ("Ave morre", "Bird dies", "Ave muere")),
    "blow_mosasaur": (("Réptil marinho ferido", "Sea reptile hurts", "Reptil marino herido"),
                      ("Réptil marinho morre", "Sea reptile dies", "Reptil marino muere")),
    "moan_plesiosaur": (("Réptil marinho ferido", "Sea reptile hurts", "Reptil marino herido"),
                        ("Réptil marinho morre", "Sea reptile dies", "Reptil marino muere")),
    "huff_turtle": (("Tartaruga ferida", "Turtle hurts", "Tortuga herida"),
                    ("Tartaruga morre", "Turtle dies", "Tortuga muere")),
    "drum_fish": (("Peixe ferido", "Fish hurts", "Pez herido"), ("Peixe morre", "Fish dies", "Pez muere")),
    "bellow_croc": (("Crocodilo ferido", "Crocodile hurts", "Cocodrilo herido"),
                    ("Crocodilo morre", "Crocodile dies", "Cocodrilo muere")),
    "hiss_mammal": (("Mamífero ferido", "Mammal hurts", "Mamífero herido"),
                    ("Mamífero morre", "Mammal dies", "Mamífero muere")),
}
_LIGHT_STEPS = {"trill_small", "rattle_raptor", "hiss_mammal", "bellow_croc"}

# subtitles per set event: (pt_br, en_us, es_es)
SUBTITLES = {}
for _sid, _events in VOICE_SETS.items():
    _set = ARCHETYPE_OF[_sid]
    for _ev in _events:
        _key = (_sid, _ev)
        if _ev == "ambient":
            SUBTITLES[_key] = _AMBIENT[_set]
        elif _ev == "threat":
            SUBTITLES[_key] = _THREAT[_set]
        elif _ev in ("hurt", "death") and _set in _CREATURE:
            SUBTITLES[_key] = _CREATURE[_set][0 if _ev == "hurt" else 1]
        elif _ev == "step" and _set in _LIGHT_STEPS:
            SUBTITLES[_key] = ("Passos", "Footsteps", "Pasos")
        else:
            SUBTITLES[_key] = _SHARED[_ev]


def events(voice_set):
    return list(VOICE_SETS[voice_set])


def field(voice_set, event):
    """Java constant in ModSounds."""
    return f"{voice_set}_{event}".upper()


def sound_id(voice_set, event):
    if voice_set == "sfx":
        return f"sfx.{event}"
    return f"voice.{voice_set}.{event}"


# ---------------------------------------------------------------- effects (not voices)
# name -> (fx, attenuation distance, [variants], (pt_br, en_us, es_es) subtitle). Sound id sfx.<name>,
# files sounds/sfx/<name>_<n>.ogg, Java constant ModSounds.SFX_<NAME>.
def _chime(f, decay=2.5, strike=0.15, seed=0):
    return P(0, "modes", dur=decay * 1.2, freqs=(f, f * 2.32, f * 4.25, f * 6.63), decays=(1 / decay * 2.2, 1 / decay * 3.4,
                                                                                       1 / decay * 5.5, 1 / decay * 8),
             gains=(1, 0.55, 0.3, 0.15), strike=strike, seed=seed)


SFX = {
    "egg_crack": ("ground", 12, [V(P(0, "crack", dur=0.45, clicks=4 + i, bright=0.9 + 0.1 * i, crumble=0.12, seed=3000 + i),
                                   room=(0.4, 0.08)) for i in range(3)],
                  ("Casca de ovo racha", "Eggshell cracks", "Cáscara de huevo se agrieta")),
    "egg_hatch": ("ground", 16, [V(P(0, "crack", dur=0.7, clicks=10, crumble=0.35, seed=3010 + i),
                                   P(0.25, "rustle", 0.5, dur=0.6, f=2200, grain=30, seed=3012 + i),
                                   P(0.55, "thud", 0.4, dur=0.15, f0=150, weight=0.15, crunch=0.6, seed=3014 + i),
                                   room=(0.5, 0.1)) for i in range(2)],
                  ("Ovo eclode", "Egg hatches", "Huevo eclosiona")),
    "egg_lay": ("ground", 12, [V(P(0, "thud", dur=0.2, f0=95 - 10 * i, weight=0.3, crunch=0.4, seed=3020 + i),
                                 P(0.05, "rustle", 0.7, dur=0.5, f=2000, grain=25, seed=3022 + i), room=(0.4, 0.08))
                               for i in range(2)],
                ("Ovo posto no ninho", "Egg laid in the nest", "Huevo puesto en el nido")),
    "egg_break": ("ground", 12, [V(P(0, "crack", dur=0.25, clicks=4, crumble=0.6, seed=3030),
                                   P(0.08, "wet", 0.8, dur=0.35, low=600, bubbles=3, seed=3031), room=(0.4, 0.08))],
                  ("Ovo quebrado", "Egg breaks", "Huevo roto")),
    "eat": ("voice", 12, [V(P(0, "clack", 0.8, dur=0.08, freq=700 + 120 * i, q=400, seed=3040 + i),
                            P(0.05, "rustle", 0.9, dur=0.35, f=1600 + 300 * i, grain=22 + 4 * i, seed=3043 + i),
                            P(0.1, "wet", 0.4, dur=0.3, low=450, bubbles=2, seed=3046 + i), room=(0.4, 0.08))
                          for i in range(3)],
            ("Dinossauro come", "Dinosaur eats", "Dinosaurio come")),
    "carcass_tear": ("voice", 16, [V(P(0, "wet", dur=0.6 + 0.1 * i, low=420, tear=0.8, bubbles=3, seed=3050 + i),
                                     P(0, "clack", 0.6, dur=0.1, freq=500, q=300, seed=3053 + i), room=(0.5, 0.1))
                                   for i in range(3)],
                     ("Carne rasgada", "Flesh tears", "Carne desgarrada")),
    "carcass_squish": ("voice", 12, [V(P(0, "wet", dur=0.35, low=350 + 80 * i, bubbles=6, seed=3060 + i),
                                       room=(0.4, 0.08)) for i in range(2)],
                       ("Carcaça esmagada", "Carcass squishes", "Cadáver aplastado")),
    "carcass_rot": ("voice", 12, [V(P(0, "wet", dur=0.9, low=260, bubbles=8, seed=3070),
                                    P(0.2, "breath", 0.5, dur=0.7, formants=[(300, 300, 0)], lp=900, seed=3071),
                                    room=(0.6, 0.12))],
                    ("Carcaça apodrece", "Carcass rots away", "Cadáver se pudre")),
    "carcass_bones": ("ground", 16, [V(*[P(0.07 * k + 0.02 * (k % 2), "modes", 0.9 - 0.12 * k, dur=0.25,
                                           freqs=(1200 + 230 * k, 2900 + 410 * k, 4800), decays=(30, 45, 60),
                                           gains=(1, 0.5, 0.3), strike=0.4, seed=3080 + k) for k in range(6)],
                                       P(0.1, "thud", 0.5, dur=0.25, f0=110, weight=0.3, crunch=0.5, seed=3087),
                                       room=(0.5, 0.1))],
                      ("Ossos caem", "Bones clatter", "Huesos caen")),
    "saddle_on": ("voice", 12, [V(P(0, "creak", dur=0.45, f=800 + 150 * i, seed=3090 + i),
                                  P(0.35, "modes", 0.6, dur=0.2, freqs=(1700, 4100), decays=(35, 50), gains=(1, 0.4),
                                    strike=0.3, seed=3092 + i),
                                  P(0.1, "rustle", 0.5, dur=0.4, f=1800, grain=20, seed=3094 + i), room=(0.4, 0.08))
                                for i in range(2)],
                  ("Sela colocada", "Saddle fastened", "Silla colocada")),
    "saddle_off": ("voice", 12, [V(P(0, "creak", dur=0.3, rate=((0, 60), (1, 25)), f=750, seed=3100),
                                   P(0.2, "rustle", 0.7, dur=0.35, f=1600, grain=18, seed=3101),
                                   P(0.45, "thud", 0.6, dur=0.2, f0=120, weight=0.25, crunch=0.5, seed=3102),
                                   room=(0.4, 0.08))],
                   ("Sela retirada", "Saddle removed", "Silla retirada")),
    "cargo": ("voice", 12, [V(P(0, "rustle", dur=0.5, f=2300 - 300 * i, grain=30, seed=3110 + i),
                              P(0.15, "creak", 0.6, dur=0.35, f=1100, seed=3112 + i), room=(0.4, 0.08))
                            for i in range(2)],
              ("Cesto de carga", "Cargo basket", "Cesta de carga")),
    "spear_throw": ("air", 16, [V(P(0, "whoosh", dur=0.45, f0=450 + 80 * i, f1=1500 + 200 * i, seed=3120 + i))
                                for i in range(2)],
                    ("Lança arremessada", "Spear thrown", "Lanza arrojada")),
    "spear_hit": ("ground", 16, [V(P(0, "wet", 0.8, dur=0.25, low=500, bubbles=1, seed=3130 + i),
                                   P(0, "modes", dur=0.3, freqs=(190 + 20 * i, 430, 770), decays=(25, 35, 50),
                                     gains=(1, 0.5, 0.3), strike=0.5, seed=3132 + i), room=(0.4, 0.08))
                                 for i in range(2)],
                  ("Lança acerta", "Spear hits", "Lanza impacta")),
    "spear_ground": ("ground", 16, [V(P(0, "modes", dur=0.35, freqs=(240, 560, 980, 1500), decays=(20, 30, 45, 60),
                                        gains=(1, 0.6, 0.4, 0.25), strike=0.8, seed=3140),
                                      P(0, "thud", 0.6, dur=0.2, f0=130, weight=0.2, crunch=0.8, seed=3141),
                                      room=(0.4, 0.08))],
                     ("Lança se crava", "Spear sticks in", "Lanza se clava")),
    "charcoal": ("voice", 8, [V(P(0, "scratch", dur=0.7 + 0.15 * i, strokes=3 + i, seed=3150 + i)) for i in range(3)],
                 ("Desenho a carvão", "Charcoal sketching", "Dibujo al carbón")),
    "discover": ("voice", 16, [V(_chime(660, 2.6, seed=3160), P(0.12, "modes", 0.6, dur=3.0,
                                                                freqs=(990, 990 * 2.32, 990 * 4.25),
                                                                decays=(0.9, 1.4, 2.4), gains=(1, 0.5, 0.25),
                                                                strike=0.1, seed=3161), room=(1.6, 0.25))],
                 ("Descoberta", "Discovery", "Descubrimiento")),
    "amber_ping": ("voice", 16, [V(_chime(1180, 1.4, seed=3170), room=(1.2, 0.2))],
                   ("Âmbar ressoa", "Amber rings", "Ámbar resuena")),
    "drum": ("ground", 24, [V(P(0, "modes", dur=0.9, freqs=(110 + 8 * i, 176, 237, 290, 410), decays=(6, 9, 12, 16, 24),
                                gains=(1, 0.8, 0.6, 0.45, 0.3), strike=0.7, glide=0.12, seed=3180 + i),
                              room=(0.8, 0.14)) for i in range(2)],
             ("Tambor de couro", "Hide drum", "Tambor de cuero")),
    "chimes": ("ground", 12, [V(_chime(f, 1.2, strike=0.35, seed=3190 + k), room=(0.9, 0.16))
                              for k, f in enumerate((780, 930, 1050))],
               ("Sinos de osso", "Bone chimes", "Campanillas de hueso")),
    "clay_jar": ("voice", 12, [V(P(0, "wet", dur=0.5, low=300, bubbles=5, seed=3200),
                                 P(0, "modes", 0.5, dur=0.4, freqs=(380, 920), decays=(18, 30), gains=(1, 0.4),
                                   strike=0.2, seed=3201), room=(0.4, 0.08))],
                 ("Jarro de argila", "Clay jar", "Jarra de arcilla")),
    "rift_pulse": ("deep", 48, [V(P(0, "drone", dur=2.8, f0=52 + 7 * i, seed=3210 + i), room=(2.4, 0.3))
                                for i in range(2)],
                   ("A Fenda pulsa", "The Rift pulses", "La Grieta pulsa")),
    "rift_tear": ("deep", 48, [V(P(0, "swell", dur=1.1, f0=70, seed=3220),
                                 P(1.08, "clack", 1.0, dur=0.15, freq=1500, q=1200, seed=3221),
                                 P(1.1, "drone", 0.7, dur=1.6, f0=48, voices=4, crackle=0.4, seed=3222),
                                 room=(2.4, 0.3))],
                  ("Algo atravessa a Fenda", "Something comes through the Rift", "Algo cruza la Grieta")),
    "rift_glitch": ("deep", 32, [V(P(0, "drone", dur=1.6 + 0.4 * i, f0=(40, 66, 90)[i], voices=3 + i,
                                     detune=0.02 + 0.01 * i, crackle=0.5, seed=3230 + i), room=(2.0, 0.3))
                                 for i in range(3)],
                    ("O tempo falha", "Time glitches", "El tiempo falla")),
}
for _name, (_fx, _dist, _variants, _sub) in SFX.items():
    for _v in _variants:
        if _v[2].get("hp") is None:
            _v[2]["hp"] = 30
    SUBTITLES[("sfx", _name)] = _sub
