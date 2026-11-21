"""The silhouette gate of the Maiasaura v4 (the "silhueta primeiro" method of the 1.11, _silhuetas/sil.py):

- the model at rest (no saddle) against its approved blocking (_silhuetas/maiasaura.py, variant C): Dice >= 0.80;
- against the remade Edmontosaurus, Parasaurolophus, Triceratops and Styracosaurus (the game's geo): <= 0.62.

usage:  python3 -B tools/modelgen/handmade/maiasaura/silcheck.py [--png out.png]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SIL = os.path.join(HERE, "..", "_silhuetas")
ENGINE = os.path.join(HERE, "..", "_engine")
sys.path[:0] = [HERE, SIL, ENGINE]

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
import geo  # noqa: E402
import proto as P  # noqa: E402
import sil  # noqa: E402
import maiasaura as BLOCK  # noqa: E402
import maia  # noqa: E402

AGAINST = ("edmontosaurus", "parasaurolophus", "triceratops", "styracosaurus")
MIN_BLOCK, MAX_OTHER = 0.80, 0.62


def model_spec(pose=None):
    m = maia.build(saddle_on=False)
    P.pack(m, maia.TEX_W)
    spec = m.spec()
    if pose:
        mats = geo.bone_mats(spec, pose)
        spec = {**spec, "bones": [dict(b, rotation=[b["rotation"][i] + pose.get(b["name"], ([0, 0, 0],))[0][i]
                                                    for i in range(3)]) for b in spec["bones"]]}
    return spec


def check(spec=None, png=None):
    spec = spec or model_spec()
    mine = sil.signature(spec)
    block = sil.signature(BLOCK.rear().spec())
    d_block = sil.similarity(mine, block)
    rows = [("blocagem C", d_block, d_block >= MIN_BLOCK)]
    for o in AGAINST:
        s = sil.similarity(mine, sil.signature(sil.load_game(o)))
        rows.append((o, s, s <= MAX_OTHER))
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
