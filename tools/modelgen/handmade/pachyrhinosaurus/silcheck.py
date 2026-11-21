"""The silhouette gate of the Pachyrhinosaurus v4 (16/11/2026): the exported model, in black, against the blocking
Rodrigo chose (variant B, "bisão", _silhuetas/pachyrhinosaurus.py) and against the herbivores it must not look like.

  Dice with the blocking            >= 0.80   (side and 3/4, _silhuetas/sil.py `similarity`)
  similarity to each neighbour      <= 0.62   (Triceratops, Styracosaurus, Protoceratops, Edmontosaurus, Maiasaura)

usage:  python3 -B tools/modelgen/handmade/pachyrhinosaurus/silcheck.py [--local]
        --local: the model built from pachy.py now (not the exported geo), at its drawing scale
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SIL = os.path.join(HERE, "..", "_silhuetas")
sys.path[:0] = [HERE, SIL, os.path.join(HERE, "..", "_engine")]
import sil  # noqa: E402
import pachyrhinosaurus as blocking  # noqa: E402

NEIGHBOURS = (("triceratops", "Tricerátops"), ("styracosaurus", "Estiracossauro"), ("protoceratops", "Protocerátops"),
              ("edmontosaurus", "Edmontossauro"), ("maiasaura", "Maiassauro"))
MIN_BLOCKING, MAX_NEIGHBOUR = 0.80, 0.62
HIDE = ("saddle", "young_brow", "female_display")


def local_spec():
    import proto as P
    import pachy
    m = pachy.build(saddle_on=False)
    P.pack(m, pachy.TEX_W)
    sp = m.spec()
    sp = {**sp, "cubes": [c for c in sp["cubes"] if c["bone"] not in HIDE]}
    for c in sp["cubes"]:
        c["uv"] = {f: (0, 0, 1, 1) for f in c["faces"]}
    return sp


def check(local=False):
    me = sil.signature(local_spec() if local else sil.load_game("pachyrhinosaurus"))
    ref = sil.signature(blocking.bison().spec())
    to_b = sil.similarity(me, ref)
    rows = [(name, sil.similarity(me, sil.signature(sil.load_game(sp)))) for sp, name in NEIGHBOURS]
    fails = []
    if to_b < MIN_BLOCKING:
        fails.append(f"Dice with the blocking {to_b:.2f} < {MIN_BLOCKING}")
    fails += [f"{n} {v:.2f} > {MAX_NEIGHBOUR}" for n, v in rows if v > MAX_NEIGHBOUR]
    return fails, to_b, rows


if __name__ == "__main__":
    fails, to_b, rows = check("--local" in sys.argv)
    print(f"silhouette: blocking B {to_b:.3f} | " + ", ".join(f"{n} {v:.3f}" for n, v in rows))
    for f in fails:
        print("  FAIL", f)
    sys.exit(1 if fails else 0)
