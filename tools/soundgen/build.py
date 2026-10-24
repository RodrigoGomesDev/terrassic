"""
Builds the mod's own sounds from recipes.py:
  assets/terrassic/sounds/voice/<set>/<event>_<n>.ogg   (mono OGG Vorbis, loudness normalised)
  assets/terrassic/sounds.json
  common/src/main/java/com/terrassic/registry/ModSounds.java
Unchanged sounds are not rewritten (git sees no diff). Needs numpy and ffmpeg (with libvorbis).
Recordings come from art/sounds/src (python3 fetch.py downloads them); without them the procedural fallbacks are used.
usage: python3 build.py
"""
import glob
import json
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from recipes import FX, VOICE_SETS, SUBTITLES, field, sound_id  # noqa: E402
from sources import AUDIO_EXT  # noqa: E402
from synth import SR, VOICES, envelope, norm  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
SRC = os.path.join(ROOT, "art", "sounds", "src")
JAVA = os.path.join(ROOT, "common", "src", "main", "java", "com", "terrassic", "registry", "ModSounds.java")
LOUDNESS = "loudnorm=I=-18:TP=-2:LRA=11"


def src_path(pattern, index=0):
    """art/sounds/src/<id>/<glob> -> the index-th matching file (sorted), or None if not downloaded."""
    hits = sorted(glob.glob(os.path.join(SRC, pattern)))
    hits = [h for h in hits if h.lower().endswith(AUDIO_EXT)]
    return hits[index] if len(hits) > index else None


def available(variant):
    kind = variant[0]
    if kind == "src":
        return src_path(variant[1], variant[2].get("file", 0)) is not None
    if kind == "mix":
        return all(available(v) for v, _ in variant[1])
    if kind == "alt":
        return available(variant[1]) or available(variant[2])
    return True


def decode(path):
    raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def loudest_window(x, n, pick):
    """Start sample of the pick-th loudest window of n samples (windows do not overlap)."""
    hop = 1024
    frames = max(1, len(x) // hop)
    energy = np.array([np.mean(x[i * hop:(i + 1) * hop] ** 2) for i in range(frames)])
    w = max(1, n // hop)
    if frames <= w:
        return 0
    sums = np.convolve(energy, np.ones(w), mode="valid")
    for _ in range(pick):
        i = int(np.argmax(sums))
        sums[max(0, i - w + 1):i + w] = -1
    return int(np.argmax(sums)) * hop


def render_src(pattern, p):
    """A cut of a recording: dur seconds (auto-picked loudest part unless start is given), slowed by pitch."""
    x = decode(src_path(pattern, p.get("file", 0)))
    n = int(p.get("dur", 2.0) * SR)
    start = int(p["start"] * SR) if "start" in p else loudest_window(x, n, p.get("pick", 0))
    x = x[start:start + n]
    pitch = p.get("pitch", 1.0)
    if pitch != 1.0:  # resample: lower pitch = slower and bigger, like a larger animal
        m = int(len(x) / pitch)
        x = np.interp(np.linspace(0, len(x) - 1, m), np.arange(len(x)), x)
    x = x * envelope(len(x), p.get("fade_in", 0.02), p.get("fade_out", 0.25) * len(x) / SR, curve=1.0)
    return norm(x)


def render(variant):
    """Variant -> float mono samples at SR (see recipes.py for the variant kinds)."""
    kind = variant[0]
    if kind == "synth":
        _, voice, params = variant
        return VOICES[voice](**params)
    if kind == "src":
        return render_src(variant[1], variant[2])
    if kind == "mix":
        parts = [(render(v), g) for v, g in variant[1]]
        out = np.zeros(max(len(x) for x, _ in parts))
        for x, g in parts:
            out[:len(x)] += g * x
        return norm(out)
    if kind == "alt":
        return render(variant[1] if available(variant[1]) else variant[2])
    raise ValueError(variant)


def wants_recording(variant):
    kind = variant[0]
    if kind == "src":
        return True
    if kind in ("mix", "alt"):
        parts = [v for v, _ in variant[1]] if kind == "mix" else [variant[1], variant[2]]
        return any(wants_recording(v) for v in parts)
    return False


def uses_recording(variant):
    kind = variant[0]
    if kind == "src":
        return True
    if kind == "mix":
        return any(uses_recording(v) for v, _ in variant[1])
    if kind == "alt":
        return uses_recording(variant[1]) if available(variant[1]) else uses_recording(variant[2])
    return False


def write_wav(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def encode(variant, fx, out):
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "in.wav")
        write_wav(wav, render(variant))
        inp = ["-i", wav]
        chain = f"{fx},{LOUDNESS},aresample={SR}"
        tmp_out = os.path.join(tmp, "out.ogg")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inp, "-af", chain,
                        "-ac", "1", "-ar", str(SR), "-c:a", "libvorbis", "-q:a", "4", "-map_metadata", "-1",
                        "-fflags", "+bitexact", "-flags:a", "+bitexact", tmp_out], check=True)
        data = open(tmp_out, "rb").read()
    if os.path.exists(out) and open(out, "rb").read() == data:
        return False
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(data)
    return True


def main():
    sounds_json = {}
    changed = 0
    recorded = 0
    for vset, evs in VOICE_SETS.items():
        for ev, (fx, dist, variants) in evs.items():
            names = []
            for i, var in enumerate(variants, start=1):
                rel = f"voice/{vset}/{ev}_{i}"
                out = os.path.join(ASSETS, "sounds", rel + ".ogg")
                recorded += uses_recording(var)
                if wants_recording(var) and not uses_recording(var) and os.path.exists(out):
                    pass  # recording not downloaded here: keep the file built where it was (never downgrade)
                else:
                    changed += encode(var, FX[fx], out)
                names.append({"name": f"terrassic:{rel}", "attenuation_distance": dist})
            entry = {"sounds": names}
            if (vset, ev) in SUBTITLES:
                entry["subtitle"] = f"subtitles.terrassic.{sound_id(vset, ev)}"
            sounds_json[sound_id(vset, ev)] = entry
    with open(os.path.join(ASSETS, "sounds.json"), "w", encoding="utf-8") as f:
        json.dump(sounds_json, f, indent=2)
        f.write("\n")

    fields = []
    for vset, evs in VOICE_SETS.items():
        for ev in evs:
            fields.append(f'    public static final RegistrySupplier<SoundEvent> {field(vset, ev)} = register("{sound_id(vset, ev)}");')
    src = f"""package com.terrassic.registry;

import com.terrassic.Terrassic;
import dev.architectury.registry.registries.DeferredRegister;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.sounds.SoundEvent;

/**
 * The mod's own sounds, organised in voice sets shared by many species (assets/terrassic/sounds.json).
 *
 * Generated by tools/soundgen/build.py - edit tools/soundgen/recipes.py.
 */
public final class ModSounds {{
    public static final DeferredRegister<SoundEvent> SOUNDS = DeferredRegister.create(Terrassic.MOD_ID, Registries.SOUND_EVENT);

{chr(10).join(fields)}

    private ModSounds() {{
    }}

    private static RegistrySupplier<SoundEvent> register(String name) {{
        return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(Terrassic.id(name)));
    }}
}}
"""
    with open(JAVA, "w") as f:
        f.write(src)
    print(f"sounds: {sum(len(v[2]) for e in VOICE_SETS.values() for v in e.values())} files ({recorded} from recordings), {changed} changed")


if __name__ == "__main__":
    main()
