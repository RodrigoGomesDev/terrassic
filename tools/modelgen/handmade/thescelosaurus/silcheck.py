"""The silhouette gate of the Thescelosaurus v4 (the "silhueta primeiro" method of the 1.11, _silhuetas/sil.py):

- the model at rest against its approved blocking (_silhuetas/thescelosaurus.py, variant A "tipo ave"): Dice >= 0.80;
- against the other small bipeds of the game and the new Corythosaurus (the game's geo): <= 0.62.

usage:  python3 -B tools/modelgen/handmade/thescelosaurus/silcheck.py [--png out.png] [--built]
        (--built: measure the exported geo.json the game loads; default: the model straight from thes.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SIL = os.path.join(HERE, "..", "_silhuetas")
ENGINE = os.path.join(HERE, "..", "_engine")
sys.path[:0] = [HERE, SIL, ENGINE]

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
import proto as P  # noqa: E402
import sil  # noqa: E402
import thescelosaurus as BLOCK  # noqa: E402
import thes  # noqa: E402

AGAINST = (("gallimimus", "Galimimo"), ("pachycephalosaurus", "Paquicefalossauro"), ("dakotaraptor", "Dakotaraptor"),
           ("velociraptor", "Velociraptor"), ("corythosaurus", "Coritossauro v4"))
MIN_BLOCK, MAX_OTHER = 0.80, 0.62


def model_spec():
    m = thes.build()
    P.pack(m, thes.TEX_W)
    return m.spec()


def check(spec=None, png=None):
    if spec is None:
        spec = sil.load_game("thescelosaurus") if "--built" in sys.argv else model_spec()
    mine = sil.signature(spec)
    block = sil.signature(BLOCK.bird().spec())
    d_block = sil.similarity(mine, block)
    rows = [("blocagem A", d_block, d_block >= MIN_BLOCK)]
    for o, name in AGAINST:
        s = sil.similarity(mine, sil.signature(sil.load_game(o)))
        rows.append((name, s, s <= MAX_OTHER))
    if png:
        tiles = []
        for v in ("side", "tq"):
            a, b = mine[v], block[v]
            im = np.zeros(a.shape + (3,), np.uint8) + 236
            im[b] = (170, 170, 200); im[a] = (40, 40, 40); im[a & b] = (0, 0, 0)
            im[a & ~b] = (190, 60, 40)
            tiles.append(Image.fromarray(im).resize((480, 480), Image.NEAREST))
        out = Image.new("RGB", (980, 480), (236, 233, 224))
        out.paste(tiles[0], (0, 0)); out.paste(tiles[1], (500, 0))
        out.save(png)
    return rows


if __name__ == "__main__":
    png = sys.argv[sys.argv.index("--png") + 1] if "--png" in sys.argv else None
    rows = check(png=png)
    bad = 0
    for name, v, ok in rows:
        print(f"  {name:18s} {v:.3f} {'ok' if ok else 'FALHA'}")
        bad += not ok
    sys.exit(1 if bad else 0)
