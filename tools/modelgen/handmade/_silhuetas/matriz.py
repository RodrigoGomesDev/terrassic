"""A matriz de semelhança de silhueta: as 12 blocagens entre si e contra os refeitos de terra do jogo."""
import importlib
import sys

import sil
import folhas

if __name__ == "__main__":
    sigs = {}
    for sp in folhas.SPECIES:
        mod = importlib.import_module(sp)
        for key, short, _t, fn in mod.VARIANTS:
            sigs[f"{mod.NAME[:5]} {key}"] = sil.signature(fn().spec())
    refs = {n: s for n, (_sp, s) in folhas.neighbours().items()}
    names = list(sigs)
    print("        " + " ".join(f"{n:>8s}" for n in names))
    for a in names:
        row = [sil.similarity(sigs[a], sigs[b]) if a != b else 0 for b in names]
        best = max((sil.similarity(sigs[a], s), n) for n, s in refs.items())
        print(f"{a:8s}" + " ".join(f"{v:8.2f}" for v in row) + f"   | jogo: {best[0]:.2f} {best[1]}")
