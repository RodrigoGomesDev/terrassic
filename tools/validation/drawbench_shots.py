"""Compare the frozen frames DrawBench takes of each species drawn the three ways (TERRASSIC_DRAWBENCH_SHOTS=1).

  python3 tools/validation/drawbench_shots.py fabric/run/screenshots <label> [--out DIR]

The game is paused while the three are taken, so the animals stand exactly still: A (GeckoLib's writer) against B (lean
writer) shows the rounding of a different order of the same matrix sums; B against C (back faces of closed cubes left
out) shows what leaving them out changes. Prints the differing pixels and how many of them touch the sky/ground
(silhouette edge) for each pair; with --out, writes a picture of where they are.
"""
import glob, os, sys

import numpy as np
from PIL import Image


def main(argv):
    folder, label = argv[0], argv[1]
    out = argv[argv.index("--out") + 1] if "--out" in argv else None
    if out:
        os.makedirs(out, exist_ok=True)
    print("| species | A vs B | B vs C | largest step B vs C |")
    print("|---|---:|---:|---:|")
    for a in sorted(glob.glob(os.path.join(folder, f"drawbench_{label}_*_A.png"))):
        sp = a[len(os.path.join(folder, f"drawbench_{label}_")):-len("_A.png")]
        ims = {m: np.asarray(Image.open(a[:-5] + m + ".png").convert("RGB")).astype(int) for m in "ABC"}
        ab = (ims["A"] != ims["B"]).any(2)
        bc = (ims["B"] != ims["C"]).any(2)
        step = int(np.abs(ims["B"] - ims["C"]).max())
        print(f"| {sp} | {int(ab.sum())} | {int(bc.sum())} | {step} |")
        if out and (ab.any() or bc.any()):
            show = ims["C"].copy()
            show[ab] = [255, 200, 0]
            show[bc] = [255, 0, 255]
            Image.fromarray(show.astype(np.uint8)).save(os.path.join(out, f"{sp}_diff.png"))


if __name__ == "__main__":
    main(sys.argv[1:])
