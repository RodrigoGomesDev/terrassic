"""The universal colour rule (Rodrigo, 02/11/2026): every species has a colour of its own.

A species' colour signature = the mean CIELAB of the dark, middle and light parts of its male skin (20 / 60 / 20 %
by lightness). Two species read as "the same colour" in game below a distance of about 10 (the old tan ceratopsians
and raptors sit at 5-8 from each other). check() compares one species with every other skin in the mod:

- against the species already remade by hand (their colours are taken), closer than CLASH is an error;
- against the old ones, closer than CLASH is a warning: they are remade one at a time and each gets a free colour
  then (docs/CORES.md).

usage: python3 -B tools/modelgen/handmade/_engine/colourcheck.py protoceratops
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TEX = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "textures", "entity")
HANDMADE = ("tyrannosaurus", "velociraptor", "pteranodon", "spinosaurus", "carnotaurus", "giganotosaurus", "protoceratops", "triceratops", "gallimimus")
CLASH = 10.0


def _lab(rgb):
    c = rgb / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])], 1)


def signature(path):
    a = np.asarray(Image.open(path).convert("RGBA")).reshape(-1, 4)
    lab = _lab(a[a[:, 3] > 200][:, :3].astype(float))
    q = np.percentile(lab[:, 0], [20, 80])
    parts = [lab[lab[:, 0] <= q[0]], lab[(lab[:, 0] > q[0]) & (lab[:, 0] < q[1])], lab[lab[:, 0] >= q[1]]]
    return np.concatenate([p.mean(0) for p in parts])


def check(species, tex_dir=TEX):
    """returns (errors, warnings, nearest): lists of (distance, other species)"""
    mine = signature(os.path.join(tex_dir, f"{species}_male.png"))
    dist = []
    for fn in sorted(os.listdir(tex_dir)):
        if fn.endswith("_male.png") and fn[:-9] != species:
            dist.append((float(np.linalg.norm(mine - signature(os.path.join(tex_dir, fn))) / np.sqrt(3)), fn[:-9]))
    dist.sort()
    errors = [d for d in dist if d[0] < CLASH and d[1] in HANDMADE]
    warnings = [d for d in dist if d[0] < CLASH and d[1] not in HANDMADE]
    return errors, warnings, dist[:5]


if __name__ == "__main__":
    e, w, near = check(sys.argv[1])
    print("nearest:", ", ".join(f"{o} {d:.1f}" for d, o in near))
    for d, o in w:
        print(f"  warning: {o} {d:.1f} (old model: gets a free colour when it is remade)")
    for d, o in e:
        print(f"  ERROR: {o} {d:.1f} (already remade: the colour is taken)")
    sys.exit(1 if e else 0)
