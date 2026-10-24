"""
Procedural voices for the Terrassic creatures (numpy only). Every sound in the mod is built here: no recording,
no sample from anyone else.

How a voice is made (source-filter, like a real throat):
  1. a SOURCE: a harmonic buzz with a moving fundamental (f0), jitter and shimmer (a living voice is never
     steady), subharmonics (period doubling = growl), "fry" (the voice breaking into separate pulses = rattle),
     a slow flutter (the throat tremolo of crocodiles and booming birds) and breath noise;
  2. a FILTER: the throat, mouth and nasal passages as moving resonances (formants), plus tube resonances
     (the hollow crests of lambeosaurs, the long trachea of sauropods) and nasal notches. Big animals have long
     vocal tracts, so their formants sit low: this, more than the pitch, is what makes a sound feel huge;
  3. a ROOM: a short outdoor reverb, longer for the giants, and a soft saturation for power.

Style: the living relatives of the dinosaurs (birds, crocodiles) mostly call with the mouth closed: booms,
coos, bellows, hisses, rattles. Film roars are an invention; here the big predators boom and growl, the
hadrosaurs blow their crests like horns, the sauropods rumble, the small feathered ones trill and rattle.
Things that make a sound read as a person or a farm animal are avoided on purpose: no clean hum at human
pitch with vowel formants (villager), no short broadband clucks (chicken).

recipes.py combines these voices into the sounds of each voice set.
"""
import numpy as np

SR = 44100


def _n(dur):
    return max(1, int(round(dur * SR)))


def _t(dur):
    return np.arange(_n(dur)) / SR


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) if len(x) else 0.0
    return x / m * peak if m > 0 else x


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


def smooth(x, width):
    """Moving average over `width` samples (keeps the length)."""
    width = int(width)
    if width <= 1:
        return x
    c = np.cumsum(np.concatenate([np.zeros(1), np.pad(x, (width // 2, width - 1 - width // 2), mode="edge")]))
    return (c[width:] - c[:-width]) / width


def track(spec, n):
    """A number, or [(fraction of the sound, value), ...] -> n values, smoothly interpolated."""
    if np.isscalar(spec):
        return np.full(n, float(spec))
    pts = sorted(spec)
    xs = np.array([p[0] for p in pts], dtype=float)
    ys = np.array([p[1] for p in pts], dtype=float)
    u = np.linspace(0.0, 1.0, n)
    return smooth(np.interp(u, xs, ys), max(1, int(0.03 * SR)))


def wobble(n, rate, rng):
    """Slow random modulation in [-1, 1] with about `rate` changes per second."""
    knots = max(4, int(n / SR * rate) + 2)
    k = rng.uniform(-1, 1, knots)
    x = np.interp(np.linspace(0, knots - 1, n), np.arange(knots), k)
    return smooth(x, max(1, int(SR / rate / 2)))


# ------------------------------------------------------------------ source

def harmonics(f, tilt=-9.0, rng=None, coherent=True, sub=0.0, shimmer=0.0, max_h=140):
    """Harmonic buzz over a time-varying fundamental f (Hz per sample). tilt = dB per octave (-12 soft, -6 bright).
    coherent phases give a pulse-like vocal buzz; sub adds the half-frequency series (period doubling = growl)."""
    rng = rng or np.random.default_rng(0)
    n = len(f)
    phase = 2 * np.pi * np.cumsum(f) / SR
    top = 0.45 * SR
    fmin = max(float(np.min(f)), 8.0)
    out = np.zeros(n)
    k_max = int(min(max_h, top / fmin))
    for k in range(1, k_max + 1):
        a = k ** (tilt / 6.02)
        mask = np.clip((top - k * f) / 400.0, 0, 1)
        ph = 0.0 if coherent else rng.uniform(0, 2 * np.pi)
        out += a * mask * np.cos(k * phase + ph)
    if sub:
        half = phase / 2
        for k in range(1, k_max + 1, 2):
            a = (k / 2) ** (tilt / 6.02) if k > 1 else 1.0
            mask = np.clip((top - k * f / 2) / 400.0, 0, 1)
            out += sub * a * mask * np.cos(k * half + rng.uniform(0, 2 * np.pi))
    if shimmer:
        out *= 1 + shimmer * wobble(n, 70, rng)
    return out


def pulses(n, rate, sharp, rng, jitter=0.15):
    """Train of soft pulses at `rate` Hz (0..1): the voice breaking into separate beats (rattle, fry, trill)."""
    r = track(rate, n) * (1 + jitter * wobble(n, 25, rng))
    ph = 2 * np.pi * np.cumsum(r) / SR
    return (0.5 + 0.5 * np.cos(ph)) ** sharp


def noise(n, rng, color=0.0):
    """White noise; color > 0 darkens it with a gentle low-pass at about 443/color Hz (color in ms, the old
    moving-average width), done in the frequency domain so it leaves no ripples."""
    x = rng.standard_normal(n)
    if color:
        fc = 443.0 / color
        spec = np.fft.rfft(x)
        f = np.fft.rfftfreq(n, 1.0 / SR)
        x = np.fft.irfft(spec / np.sqrt(1 + (f / fc) ** 2), n)
        x /= np.std(x) + 1e-12
    return x


# ------------------------------------------------------------------ filter (STFT, zero phase)

def _resonance(freqs, fc, bw):
    return 1.0 / (1.0 + ((freqs[None, :] - fc[:, None]) / (bw / 2.0)) ** 2)


def comb(x, freq, q):
    """Tube resonance: a feedback delay line (y[n] = x[n] + q y[n - D]) gives resonances at freq, 2 freq, 3 freq...
    Done in the time domain, block by block, so the narrow peaks stay exact. freq may be a track (its mean is used)."""
    if not np.isscalar(freq):
        freq = float(np.mean([p[1] for p in freq]))
    d = max(1, int(round(SR / freq)))
    y = np.array(x, dtype=float)
    for s in range(d, len(y), d):
        e = min(len(y), s + d)
        y[s:e] += q * y[s - d:e - d]
    return y * (1 - q)


def spectral_filter(x, formants=(), floor=0.02, tube=None, notch=None, lp=None, hp=None, n_fft=2048, hop=512):
    """Shape x with moving resonances.
    formants: [(freq, bandwidth, gain_db)], freq a number or [(fraction, Hz)] track.
    tube: (freq, q) comb of resonances at freq, 2 freq, 3 freq... (crest / long trachea), see comb().
    notch: (freq, bandwidth, depth 0..1) nasal anti-resonance. lp / hp: soft cut-offs in Hz."""
    n = len(x)
    if tube is not None:
        x = comb(x, *tube)
    win = np.hanning(n_fft + 1)[:-1]
    pad = n_fft
    xp = np.concatenate([np.zeros(pad), x, np.zeros(pad + n_fft)])
    frames = 1 + (len(xp) - n_fft) // hop
    idx = np.arange(n_fft)[None, :] + hop * np.arange(frames)[:, None]
    spec = np.fft.rfft(xp[idx] * win, axis=1)
    freqs = np.fft.rfftfreq(n_fft, 1.0 / SR)
    centre = (hop * np.arange(frames) + n_fft / 2 - pad) / max(1, n)
    frac = np.clip(centre, 0, 1)

    def at(spec_):
        if np.isscalar(spec_):
            return np.full(frames, float(spec_))
        pts = sorted(spec_)
        return np.interp(frac, [p[0] for p in pts], [p[1] for p in pts])

    g = np.full((frames, len(freqs)), floor)
    for fc, bw, gdb in formants:
        g += 10 ** (gdb / 20.0) * _resonance(freqs, at(fc), bw)
    if notch is not None:
        fz, bwz, depth = notch
        g *= 1 - depth * _resonance(freqs, at(fz), bwz)
    if lp is not None:
        g /= np.sqrt(1 + (freqs[None, :] / lp) ** 4)
    if hp is not None:
        g /= np.sqrt(1 + (hp / np.maximum(freqs[None, :], 1.0)) ** 4)
    y = np.fft.irfft(spec * g, n=n_fft, axis=1) * win
    out = np.zeros(len(xp))
    wsum = np.zeros(len(xp))
    for i in range(frames):
        s = hop * i
        out[s:s + n_fft] += y[i]
        wsum[s:s + n_fft] += win ** 2
    out /= np.maximum(wsum, 1e-3)
    return out[pad:pad + n]


# ------------------------------------------------------------------ room

def reverb(x, rt=1.2, wet=0.18, damp=3500.0, seed=99):
    """Outdoor-ish reverb: a few early reflections and a dark exponential tail (FFT convolution)."""
    if wet <= 0:
        return x
    rng = np.random.default_rng(seed)
    n = _n(rt)
    t = np.arange(n) / SR
    tail = noise(n, rng, color=1000.0 / damp) * np.exp(-6.9 * t / rt)
    tail *= np.clip(t / 0.02, 0, 1)
    for d, g in ((0.011, 0.5), (0.023, 0.35), (0.037, 0.3), (0.052, 0.2)):
        i = _n(d)
        if i < n:
            tail[i] += g * np.sqrt(np.sum(tail ** 2) / n) * 40
    tail /= np.sqrt(np.sum(tail ** 2)) + 1e-9
    m = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(tail, m), m)[:len(x) + n]
    dry = np.concatenate([x, np.zeros(n)])
    y *= np.sqrt(np.sum(dry ** 2) / (np.sum(y ** 2) + 1e-12))
    out = dry + wet * y
    # trim the silent end of the tail
    level = np.abs(out) > 1e-3 * np.max(np.abs(out))
    end = int(np.nonzero(level)[0][-1]) + 1 if level.any() else len(out)
    return out[:min(len(out), end + _n(0.05))] * envelope(min(len(out), end + _n(0.05)), 0, 0.05, 1.0)


def drive(x, amount, over=4):
    """Soft saturation (power, grit), oversampled so the new harmonics do not fold back as whistles."""
    if amount <= 1.0:
        return x
    x = norm(x, 1.0)
    n = len(x)
    spec = np.fft.rfft(x)
    up = np.fft.irfft(spec, n * over) * over
    up = np.tanh(amount * up) / np.tanh(amount)
    spec_up = np.fft.rfft(up)[:len(spec)]
    return np.fft.irfft(spec_up, n) / over


# ------------------------------------------------------------------ voices

def call(dur=1.5, f0=100, tilt=-9.0, jitter=0.01, shimmer=0.08, sub=0.0, coherent=True,
         fry=0.0, fry_rate=30, fry_sharp=4.0, flutter=(0.0, 0.0), breath=0.1, breath_color=0.0,
         formants=((300, 200, 0), (800, 300, -6), (2000, 500, -14)), tube=None, notch=None, lp=None, hp=None,
         body=0.0, attack=0.06, release=0.3, amp=None, seed=0):
    """The general voiced call. f0, amp and formant frequencies accept [(fraction, value)] tracks.
    fry: depth of the pulse train (rattle) at fry_rate; flutter: (rate Hz, depth) slow tremolo;
    breath: noise through the same throat; body: a pure low hum at f0 (chest resonance, felt more than heard)."""
    rng = np.random.default_rng(seed)
    n = _n(dur)
    f = track(f0, n)
    if jitter:
        f = f * (1 + jitter * wobble(n, 30, rng))
    src = harmonics(f, tilt, rng, coherent, sub, shimmer)
    src = norm(src, 1.0)
    if breath:
        src = src + breath * norm(noise(n, rng, breath_color), 1.0) * 0.6
    if fry:
        src *= (1 - fry) + fry * pulses(n, fry_rate, fry_sharp, rng)
    rate, depth = flutter
    if depth:
        t = np.arange(n) / SR
        src *= 1 - depth * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t * (1 + 0.04 * wobble(n, 3, rng))))
    y = spectral_filter(src, formants, tube=tube, notch=notch, lp=lp, hp=hp)
    if body:
        ph = 2 * np.pi * np.cumsum(f) / SR
        y = norm(y, 1.0) + body * (np.sin(ph) + 0.5 * np.sin(2 * ph))
    env = envelope(n, attack, release, 1.6)
    if amp is not None:
        env *= track(amp, n)
    return norm(y * env)


def breath(dur=0.6, formants=((900, 900, 0), (2500, 1500, -6)), color=0.0, attack=0.05, release=0.3, amp=None,
           flutter=(0.0, 0.0), lp=None, hp=None, tube=None, seed=0):
    """Shaped noise: snorts, hisses, exhales, blows."""
    rng = np.random.default_rng(seed)
    n = _n(dur)
    x = noise(n, rng, color)
    rate, depth = flutter
    if depth:
        x *= (1 - depth) + depth * pulses(n, rate, 2.0, rng, 0.3)
    y = spectral_filter(x, formants, floor=0.01, lp=lp, hp=hp, tube=tube)
    env = envelope(n, attack, release, 1.4)
    if amp is not None:
        env *= track(amp, n)
    return norm(y * env, 0.45)  # noise is much louder than a voice at the same peak


def thud(dur=0.45, f0=46, crunch=0.5, weight=1.0, seed=0):
    """Footstep: a low decaying thump, the ground giving way (dull crunch) and a little debris."""
    rng = np.random.default_rng(seed)
    t = _t(dur)
    n = len(t)
    decay = 9.0 / weight
    body = np.sin(2 * np.pi * np.cumsum(f0 * (1 - 0.35 * t / dur)) / SR) * np.exp(-t * decay)
    body += 0.5 * np.sin(2 * np.pi * np.cumsum(2.1 * f0 * (1 - 0.3 * t / dur)) / SR) * np.exp(-t * decay * 1.8)
    hit = spectral_filter(noise(n, rng), ((220, 260, 0), (700, 600, -8)), floor=0.005) * np.exp(-t * 20)
    grit = spectral_filter(noise(n, rng), ((1600, 2500, 0),), floor=0.01) * np.exp(-t * 18)
    grit *= pulses(n, 55, 6, rng, 0.6)
    knock = np.sin(2 * np.pi * 3.3 * f0 * t) * np.exp(-t * decay * 3.5)
    y = 0.75 * norm(body, 1.0) + 0.45 * knock + crunch * norm(hit, 1.0) + 0.3 * crunch * norm(grit, 1.0)
    return norm(y * envelope(n, 0.003, dur * 0.4, 1.0))


def flap(dur=0.5, beats=1, size=1.0, seed=0):
    """Wing beat of a membrane wing: a soft push of air with a low thump and the skin snapping taut."""
    rng = np.random.default_rng(seed)
    t = _t(dur)
    n = len(t)
    out = np.zeros(n)
    for b in range(beats):
        c = (b + 0.45) / beats * dur
        w = dur / beats / 3.2
        g = np.exp(-((t - c) / w) ** 2)
        air = spectral_filter(noise(n, rng), ((350 / size, 500 / size, 0), (1400 / size, 1600, -9)), floor=0.01)
        thump = np.sin(2 * np.pi * (60 / size) * t) * np.exp(-((t - c - w * 0.3) / (w * 0.5)) ** 2)
        snap = spectral_filter(noise(n, rng), ((900 / size, 700, 0),), floor=0.01) * np.exp(-((t - c - w) / 0.006) ** 2)
        out += g * norm(air, 1.0) + 0.6 * thump + 0.5 * norm(snap, 1.0)
    return norm(out)


def clack(dur=0.12, freq=900.0, q=600.0, seed=0):
    """A hard knock: jaws or beak snapping shut, horn on horn."""
    rng = np.random.default_rng(seed)
    t = _t(dur)
    x = spectral_filter(noise(len(t), rng), ((freq, q, 0), (freq * 2.3, q * 1.5, -8)), floor=0.005)
    return norm(x * np.exp(-t * 60))


def trill(dur=0.8, f0=((0, 3000), (1, 2400)), rate=24, sharp=3.0, vibrato=(0.0, 0.0), harm=0.15, attack=0.02,
          release=0.15, seed=0):
    """A whistled trill: a near-pure tone broken into fast pulses (small feathered dinosaurs). Not a cluck: the
    pulses are tonal, fast and gliding."""
    rng = np.random.default_rng(seed)
    n = _n(dur)
    f = track(f0, n)
    rate_v, depth = vibrato
    if depth:
        f = f * (1 + depth * np.sin(2 * np.pi * rate_v * np.arange(n) / SR))
    f = f * (1 + 0.006 * wobble(n, 20, rng))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + harm * np.sin(2 * ph) + harm * 0.4 * np.sin(3 * ph)
    if rate:
        x *= pulses(n, rate, sharp, rng, 0.08)
    return norm(x * envelope(n, attack, release, 1.2))


def silence(dur=0.1):
    return np.zeros(_n(dur))


# ------------------------------------------------------------------ assembly

def mix(parts, room=(1.0, 0.15), drive_amount=1.0, peak=0.9, hp=None, lp=None, **_):
    """parts: [(start s, voice name, params, gain)] layered on one timeline, then saturation and room."""
    rendered = []
    for start, voice, params, gain in parts:
        x = VOICES[voice](**params)
        rendered.append((_n(start) if start > 0 else 0, x, gain))
    n = max(s + len(x) for s, x, _ in rendered)
    out = np.zeros(n)
    for s, x, g in rendered:
        out[s:s + len(x)] += g * x
    out = drive(out, drive_amount)
    if hp or lp:
        out = spectral_filter(out, (), floor=1.0, hp=hp, lp=lp)
    rt, wet = room
    out = reverb(out, rt, wet)
    return norm(out, peak)


VOICES = {"call": call, "breath": breath, "thud": thud, "flap": flap, "clack": clack, "trill": trill,
          "silence": silence, "mix": mix}
