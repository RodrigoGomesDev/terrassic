"""Listening material for a species' voice set when nobody can listen in the game (numpy and Pillow only, no
matplotlib): copies the built .ogg files to art/<species>/vozes/, draws a spectrogram sheet per event
(art/<species>/vozes/<event>.png) and prints measurements of each sound (length, pitch band, brightness, how rough)
next to the same measurements of other species, as a table for VOZES.md.

usage: python3 voice_sheet.py SPECIES [SPECIES ...] [--compare tyrannosaurus,carnotaurus,giganotosaurus]
"""
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SOUNDS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "sounds", "voice")
SR = 44100
FMAX = 5000.0


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, "<f4").astype(float)


def stft(x, n=2048, hop=256):
    w = np.hanning(n)
    x = np.concatenate([np.zeros(n // 2), x, np.zeros(n)])
    frames = [x[i:i + n] * w for i in range(0, len(x) - n, hop)]
    return np.abs(np.fft.rfft(np.array(frames), axis=1)), np.fft.rfftfreq(n, 1 / SR)


def measure(x):
    """length s; the strongest band below 400 Hz (where the voice's pitch sits); spectral centroid (brightness);
    share of energy under 250 Hz; roughness = how much the loudness flickers 15-80 Hz (rattle, grind)."""
    mag, f = stft(x)
    p = mag ** 2
    tot = p.sum(axis=0)
    low = (f > 25) & (f < 400)
    pitch = float(f[low][np.argmax(tot[low])])
    centroid = float((tot * f).sum() / tot.sum())
    under = float(tot[f < 250].sum() / tot.sum())
    k = SR // 400
    env = np.convolve(np.abs(x), np.ones(k) / k, "same")[::k]
    fs = SR / k
    loud = env > 0.2 * env.max()
    e = env[loud] - env[loud].mean() if loud.sum() > 64 else env - env.mean()
    E = np.abs(np.fft.rfft(e * np.hanning(len(e))))
    ff = np.fft.rfftfreq(len(e), 1 / fs)
    rough = float(E[(ff > 15) & (ff < 80)].sum() / (E[(ff > 1) & (ff < 150)].sum() + 1e-9))
    return dict(dur=len(x) / SR, pitch=pitch, centroid=centroid, under=under, rough=rough)


def colour(v):
    """0..1 -> a dark-to-bright heat ramp (black, plum, red, amber, pale yellow)"""
    stops = np.array([[0, 0, 4], [60, 15, 110], [180, 50, 90], [250, 140, 40], [252, 250, 190]], float)
    v = np.clip(v, 0, 1) * (len(stops) - 1)
    i = np.minimum(v.astype(int), len(stops) - 2)
    t = (v - i)[..., None]
    return (stops[i] * (1 - t) + stops[i + 1] * t).astype(np.uint8)


def spectrogram(x, w=520, h=200):
    mag, f = stft(x)
    keep = f <= FMAX
    db = 20 * np.log10(mag[:, keep].T + 1e-9)
    db = np.clip((db - (db.max() - 80)) / 80, 0, 1)[::-1]
    img = Image.fromarray(colour(db)).resize((w, h), Image.BILINEAR)
    return img


def sheet(sid, out_dir):
    src = os.path.join(SOUNDS, sid)
    files = sorted(n for n in os.listdir(src) if n.endswith(".ogg"))
    events = {}
    for n in files:
        events.setdefault(n.rsplit("_", 1)[0], []).append(n)
    os.makedirs(out_dir, exist_ok=True)
    rows = {}
    for ev, names in events.items():
        tiles = []
        for n in names:
            shutil.copyfile(os.path.join(src, n), os.path.join(out_dir, n))
            x = decode(os.path.join(src, n))
            rows[n[:-4]] = measure(x)
            tiles.append((n[:-4], x))
        tw, th = 520, 200
        img = Image.new("RGB", (tw + 70, (th + 40) * len(tiles)), (236, 232, 224))
        dr = ImageDraw.Draw(img)
        for i, (name, x) in enumerate(tiles):
            y0 = i * (th + 40)
            img.paste(spectrogram(x, tw, th), (60, y0 + 28))
            dr.text((60, y0 + 8), f"{sid} / {name}  ({len(x) / SR:.1f} s, 0-5 kHz)", fill=(20, 20, 20))
            for khz in range(0, 6):
                yy = y0 + 28 + th - int(th * khz * 1000 / FMAX)
                dr.text((8, min(yy - 6, y0 + 28 + th - 12)), f"{khz} kHz", fill=(60, 60, 60))
            for s in range(int(len(x) / SR) + 1):
                xx = 60 + int(tw * s * SR / len(x))
                dr.line([(xx, y0 + 28 + th), (xx, y0 + 33 + th)], fill=(60, 60, 60))
        img.save(os.path.join(out_dir, f"{ev}.png"))
    return rows


def table(rows):
    lines = ["| som | duração | faixa forte (Hz) | brilho (Hz) | energia < 250 Hz | aspereza |", "|---|---|---|---|---|---|"]
    for name, m in rows.items():
        lines.append(f"| {name} | {m['dur']:.1f} s | {m['pitch']:.0f} | {m['centroid']:.0f} | {m['under'] * 100:.0f}% | "
                     f"{m['rough']:.2f} |")
    return "\n".join(lines)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    compare = []
    for a in sys.argv[1:]:
        if a.startswith("--compare"):
            compare = a.split("=", 1)[1].split(",")
    for sid in args:
        rows = sheet(sid, os.path.join(ROOT, "art", sid, "vozes"))
        print(f"## {sid}\n\n{table(rows)}\n")
    for sid in compare:
        src = os.path.join(SOUNDS, sid)
        rows = {n[:-4]: measure(decode(os.path.join(src, n))) for n in sorted(os.listdir(src))
                if n.endswith(".ogg") and not n.startswith("step")}
        print(f"## {sid} (comparação)\n\n{table(rows)}\n")


if __name__ == "__main__":
    main()
