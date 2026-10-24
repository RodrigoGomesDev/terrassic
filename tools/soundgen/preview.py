"""
Listening previews of the voice sets: one file per set with all its sounds in a row (events in order, a short
pause between sounds), plus a spectrogram sheet when matplotlib is installed. Nothing here goes into the mod.
usage: python3 preview.py OUT_DIR [set ...]
"""
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from recipes import VOICE_SETS  # noqa: E402
from synth import SR, VOICES, norm  # noqa: E402

GAP = 0.7


def render(variant):
    _, voice, params = variant
    return VOICES[voice](**params)


def write_wav(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main():
    out_dir = sys.argv[1]
    only = sys.argv[2:]
    os.makedirs(out_dir, exist_ok=True)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        plt = None
    for vset, evs in VOICE_SETS.items():
        if only and vset not in only:
            continue
        clips, labels = [], []
        for ev, (_, _, variants) in evs.items():
            for i, var in enumerate(variants, start=1):
                clips.append(norm(render(var), 0.8))
                labels.append(f"{ev}_{i}")
        seq = np.concatenate([np.concatenate([c, np.zeros(int(GAP * SR))]) for c in clips])
        with tempfile.TemporaryDirectory() as tmp:
            wav = os.path.join(tmp, "a.wav")
            write_wav(wav, seq)
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", wav, "-af",
                            "highpass=f=24,loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-c:a", "libmp3lame",
                            "-q:a", "2", os.path.join(out_dir, f"{vset}.mp3")], check=True)
        if plt:
            cols = 3
            rows = (len(clips) + cols - 1) // cols
            fig, axes = plt.subplots(rows, cols, figsize=(cols * 4.2, rows * 2.2), squeeze=False)
            for ax in axes.flat:
                ax.axis("off")
            for ax, c, lab in zip(axes.flat, clips, labels):
                ax.axis("on")
                ax.specgram(c, NFFT=2048, Fs=SR, noverlap=1536, cmap="magma", vmin=-110)
                ax.set_ylim(0, 5000)
                ax.set_title(lab, fontsize=9)
                ax.tick_params(labelsize=7)
            fig.suptitle(vset)
            fig.tight_layout()
            fig.savefig(os.path.join(out_dir, f"{vset}.png"), dpi=70)
            plt.close(fig)
        print(vset, len(clips), "sounds", f"{len(seq) / SR:.1f}s")


if __name__ == "__main__":
    main()
