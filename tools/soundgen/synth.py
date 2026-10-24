"""
Procedural voices for the dinosaurs (numpy). Each function returns a mono float array at SR, roughly in [-1, 1];
build.py then runs it through an ffmpeg filter chain (formants, EQ, loudness) and encodes it as OGG.

Style: closed-mouth sounds like the dinosaurs' living relatives (crocodiles booming, ostriches and cassowaries
"drumming", birds calling) instead of film roars. These are placeholders/layers until recorded CC0 sources are
dropped in art/sounds/src (see recipes.py).
"""
import numpy as np

SR = 44100


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def envelope(n, attack, release, curve=2.0):
    """Smooth attack/release envelope over n samples (times in seconds)."""
    e = np.ones(n)
    a = min(n, int(attack * SR))
    r = min(n - a, int(release * SR))
    if a:
        e[:a] = np.linspace(0, 1, a) ** curve
    if r:
        e[n - r:] = np.linspace(1, 0, r) ** curve
    return e


def glide(dur, f_start, f_end, jitter=0.0, rng=None, shape=1.0):
    """Instantaneous frequency curve from f_start to f_end, with slow random wobble."""
    t = _t(dur)
    x = (t / dur) ** shape
    f = f_start + (f_end - f_start) * x
    if jitter and rng is not None:
        knots = rng.normal(0, jitter, 8)
        f *= 1 + np.interp(t, np.linspace(0, dur, 8), knots)
    return f


def harmonic(freq, weights, rng):
    """Sum of harmonics of a time-varying fundamental (phase-continuous)."""
    phase = 2 * np.pi * np.cumsum(freq) / SR
    out = np.zeros_like(freq)
    for k, w in enumerate(weights, start=1):
        out += w * np.sin(k * phase + rng.uniform(0, 2 * np.pi))
    return out


def smooth_noise(n, rng, smooth=8):
    """Noise lowpassed by a moving average (cheap and dark)."""
    x = rng.standard_normal(n + smooth)
    k = np.ones(smooth) / smooth
    return np.convolve(x, k, mode="same")[:n]


def norm(x):
    m = np.max(np.abs(x)) or 1.0
    return x / m * 0.9


# ------------------------------------------------------------------ voices

def boom(dur=2.4, f0=52, f1=44, flutter=7.0, depth=0.35, breath=0.12, seed=0):
    """Closed-mouth booming: a deep harmonic hum with a crocodile-like throat flutter (amplitude tremolo)."""
    rng = np.random.default_rng(seed)
    f = glide(dur, f0, f1, jitter=0.03, rng=rng)
    tone = harmonic(f, [1.0, 0.8, 0.55, 0.4, 0.28, 0.18, 0.12, 0.08], rng)
    t = _t(dur)
    trem = 1 - depth * (0.5 + 0.5 * np.sin(2 * np.pi * flutter * t + rng.uniform(0, 6)))
    air = smooth_noise(len(t), rng, 24) * breath
    return norm((tone * trem + air) * envelope(len(t), 0.35, 0.9))


def horn(dur=2.6, f0=92, f1=86, vibrato=4.5, seed=0):
    """Resonant tube call (Parasaurolophus crest): bright harmonic source, formants added in ffmpeg."""
    rng = np.random.default_rng(seed)
    t = _t(dur)
    f = glide(dur, f0 * 0.94, f0, rng=rng, shape=0.3) * (1 + 0.012 * np.sin(2 * np.pi * vibrato * t))
    f = f + (f1 - f0) * np.clip((t - dur * 0.7) / (dur * 0.3), 0, 1)
    tone = harmonic(f, [1 / k ** 0.9 for k in range(1, 24)], rng)
    air = smooth_noise(len(t), rng, 4) * 0.04
    return norm((tone + air) * envelope(len(t), 0.18, 0.7, 1.5))


def squawk(dur=0.55, f0=380, f1=300, rough=0.6, seed=0):
    """Harsh bird call (Pteranodon, Gallimimus): FM with a noisy, raspy edge and a rise-fall pitch."""
    rng = np.random.default_rng(seed)
    t = _t(dur)
    contour = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.6
    f = f1 + (f0 - f1) * contour
    mod = np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 2.5
    car = np.sin(2 * np.pi * np.cumsum(f) / SR + mod)
    rasp = rng.standard_normal(len(t)) * rough * (0.5 + 0.5 * np.sin(2 * np.pi * 60 * t))
    return norm((car + 0.35 * rasp * np.abs(car)) * envelope(len(t), 0.03, 0.18, 1.2))


def grunt(dur=0.4, f0=110, f1=80, noise=0.4, seed=0):
    """Short pained grunt: quick pitch drop, breathy."""
    rng = np.random.default_rng(seed)
    t = _t(dur)
    f = glide(dur, f0, f1, rng=rng, shape=0.5)
    tone = harmonic(f, [1.0, 0.7, 0.5, 0.35, 0.25, 0.15], rng)
    air = smooth_noise(len(t), rng, 6) * noise
    return norm((tone + air) * envelope(len(t), 0.015, 0.25, 1.5))


def groan(dur=2.0, f0=70, f1=38, seed=0):
    """Dying groan: long falling hum that loses its strength and wavers."""
    rng = np.random.default_rng(seed)
    t = _t(dur)
    f = glide(dur, f0, f1, jitter=0.05, rng=rng, shape=1.4)
    tone = harmonic(f, [1.0, 0.75, 0.5, 0.35, 0.2, 0.12], rng)
    trem = 1 - 0.4 * (t / dur) * (0.5 + 0.5 * np.sin(2 * np.pi * 5 * t))
    air = smooth_noise(len(t), rng, 16) * 0.15
    fade = np.linspace(1, 0.25, len(t))
    return norm((tone * trem * fade + air) * envelope(len(t), 0.1, 0.8))


def thud(dur=0.35, f0=48, seed=0):
    """Heavy footstep: low decaying thump plus a dull ground crunch."""
    rng = np.random.default_rng(seed)
    t = _t(dur)
    body = np.sin(2 * np.pi * f0 * t * (1 - 0.3 * t / dur)) * np.exp(-t * 14)
    crunch = smooth_noise(len(t), rng, 12) * np.exp(-t * 30) * 0.6
    return norm(body + crunch)


def flap(dur=0.45, beats=2, seed=0):
    """Big wing beat: soft whooshes of filtered noise."""
    rng = np.random.default_rng(seed)
    t = _t(dur)
    out = np.zeros(len(t))
    for b in range(beats):
        c = (b + 0.5) / beats * dur
        out += np.exp(-((t - c) / (dur / beats / 3.5)) ** 2) * smooth_noise(len(t), rng, 30)
    return norm(out)


def hiss(dur=0.9, seed=0):
    """Threat hiss: breathy noise swelling and fading."""
    rng = np.random.default_rng(seed)
    t = _t(dur)
    return norm(rng.standard_normal(len(t)) * envelope(len(t), 0.12, 0.4, 1.3))


VOICES = {"boom": boom, "horn": horn, "squawk": squawk, "grunt": grunt, "groan": groan, "thud": thud,
          "flap": flap, "hiss": hiss}
