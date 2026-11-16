"""The silhouette gate of the Corythosaurus v4 (16/11/2026): the exported model, in black, against the blocking Rodrigo
chose (variant B, "leque alto", _silhuetas/corythosaurus.py) and against the herbivores it must not look like.

  Dice with the blocking            >= 0.80   (side and 3/4, _silhuetas/sil.py `similarity`)
  similarity to each neighbour      <= 0.62   (Edmontosaurus, Parasaurolophus, Triceratops, Styracosaurus)

usage:  python3 -B tools/modelgen/handmade/corythosaurus/silcheck.py [--sheet out_dir]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SIL = os.path.join(HERE, "..", "_silhuetas")
sys.path[:0] = [SIL]
import sil  # noqa: E402
import corythosaurus as blocking  # noqa: E402

NEIGHBOURS = (("edmontosaurus", "Edmontossauro"), ("parasaurolophus", "Parassaurolofo"),
              ("triceratops", "Tricerátops"), ("styracosaurus", "Estiracossauro"))
MIN_BLOCKING, MAX_NEIGHBOUR = 0.80, 0.62


def check():
    me = sil.signature(sil.load_game("corythosaurus"))
    ref = sil.signature(blocking.high_fan().spec())
    to_b = sil.similarity(me, ref)
    rows = [(name, sil.similarity(me, sil.signature(sil.load_game(sp)))) for sp, name in NEIGHBOURS]
    fails = []
    if to_b < MIN_BLOCKING:
        fails.append(f"Dice with the blocking {to_b:.2f} < {MIN_BLOCKING}")
    fails += [f"{n} {v:.2f} > {MAX_NEIGHBOUR}" for n, v in rows if v > MAX_NEIGHBOUR]
    return fails, to_b, rows


if __name__ == "__main__":
    fails, to_b, rows = check()
    print(f"silhouette: blocking B {to_b:.3f} | " + ", ".join(f"{n} {v:.3f}" for n, v in rows))
    for f in fails:
        print("  FAIL", f)
    sys.exit(1 if fails else 0)
