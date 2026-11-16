"""Entrega 2: a fileira atual dos bicos-de-pato em preto (só a cabeça muda)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sil  # noqa: E402
import sheet  # noqa: E402

OUT = os.path.join(sil.ROOT, "..", "..", "Claude outputs", "silhuetas-1.11", "img")
if not os.path.isdir(OUT):
    OUT = "/Users/rodrigogs/projects/terrassic/Claude outputs/silhuetas-1.11/img"

ROW = [("edmontosaurus", "Edmontossauro"), ("parasaurolophus", "Parassaurolofo"),
       ("maiasaura", "Maiassauro (hoje)"), ("corythosaurus", "Coritossauro (hoje)")]

if __name__ == "__main__":
    specs = {sp: sil.load_game(sp) for sp, _n in ROW}
    sigs = {sp: sil.signature(s) for sp, s in specs.items()}
    items = []
    for sp, name in ROW:
        best = max((sil.similarity(sigs[sp], sigs[o]), n) for o, n in ROW if o != sp)
        items.append((specs[sp], name, f"mais parecido: {best[1]} {best[0]:.2f}"))
    ppm = 42
    a = sheet.row(items, ppm, sil.SIDE)
    b = sheet.row([(s, None, None) for s, _t, _u in items], ppm, sil.TQ, person=True, label_h=10)
    img = sheet.stack([a, b], "O problema de hoje: só a cabeça muda",
                       "Os quatro bicos-de-pato do jogo em preto, de lado e de 3/4, no tamanho do jogo. "
                       "Semelhança de silhueta 0..1 (Dice de lado e 3/4).")
    img.save(os.path.join(OUT, "02_problema_bicos_de_pato.png"))
    for sp, _n in ROW:
        print(sp, {o: round(sil.similarity(sigs[sp], sigs[o]), 3) for o, _m in ROW if o != sp})
