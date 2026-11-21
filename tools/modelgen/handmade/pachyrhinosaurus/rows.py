"""The Pachyrhinosaurus v4 next to the remade ceratopsians of the game, at their in-game sizes, side-on: one row in colour
(the male skins) and one in black (the silhouette, _silhuetas/sil.py), with the 1.70 m person.

usage:  python3 -B tools/modelgen/handmade/pachyrhinosaurus/rows.py out_dir
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "_engine"), os.path.join(HERE, "..", "_silhuetas")]
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402
import geo  # noqa: E402
import sil  # noqa: E402
import sheet  # noqa: E402

ROW = [("pachyrhinosaurus", "Paquirrinossauro v4"), ("triceratops", "Tricerátops"), ("styracosaurus", "Estiracossauro"),
       ("protoceratops", "Protocerátops")]
HIDE = ("saddle", "female_display", "young_brow")


def colour(sp, ppm):
    """the game's model in colour, side-on, scaled like the black one (metres via sil.load_game)"""
    spec = sil.load_game(sp)
    tex = Image.open(os.path.join(sil.ASSETS, "textures", "entity", f"{sp}_male.png"))
    raw = geo.load_geo(os.path.join(sil.ASSETS, "geo", "entity", f"{sp}.geo.json"))
    spec["tw"], spec["th"] = raw["tw"], raw["th"]
    x0, x1, y0, y1 = sil.extent(spec, sil.SIDE)
    W, H = int((x1 - x0) * ppm) + 2, int((y1 - y0) * ppm) + 2
    im = geo.render(spec, tex, 90, 0, (W, H), bg=sheet.BG, margin=0.0)[0].convert("RGB")
    return im


def main(out):
    os.makedirs(out, exist_ok=True)
    ppm = 40
    specs = {sp: sil.load_game(sp) for sp, _n in ROW}
    sigs = {sp: sil.signature(s) for sp, s in specs.items()}
    items = []
    for sp, name in ROW:
        best = max((sil.similarity(sigs[sp], sigs[o]), n) for o, n in ROW if o != sp)
        items.append((specs[sp], name, f"mais parecido: {best[1]} {best[0]:.2f}"))
    black = sheet.row(items, ppm, sil.SIDE)
    # the colour row: the same layout, each model's render pasted where its black shape stands
    ims = [colour(sp, ppm) for sp, _n in ROW]
    hum = sil.human()
    widths = [im.width for im in ims]
    hmax = max(im.height for im in ims)
    pad, gap = 24, int(0.9 * ppm)
    hw = int((sil.extent(hum, (0, 0))[1] - sil.extent(hum, (0, 0))[0]) * ppm)
    W = pad * 2 + hw + gap + sum(widths) + gap * (len(ims) - 1)
    Hh = pad + hmax + 14 + 40
    col = Image.new("RGB", (W, Hh), sheet.BG)
    d = ImageDraw.Draw(col)
    base = pad + hmax
    d.line([(pad // 2, base), (W - pad // 2, base)], fill=sheet.GROUND, width=2)
    sil.draw(col, hum, (0, 0), ppm, (pad, base), sheet.PERSON)
    x = pad + hw + gap
    for im, (sp, name) in zip(ims, ROW):
        col.paste(im, (x, base - im.height))
        d.text((x, base + 8), name, fill=sheet.TEXT, font=sil.font(22, True))
        x += im.width + gap
    img = sheet.stack([col, black], "Paquirrinossauro v4 ao lado dos ceratopsianos",
                      "No tamanho do jogo, de lado: em cima a cor, embaixo a silhueta em preto. "
                      "Semelhança 0..1 (Dice de lado e 3/4).")
    img.save(os.path.join(out, "fileira_ceratopsianos.png"))
    for sp, _n in ROW:
        print(sp, {o: round(sil.similarity(sigs[sp], sigs[o]), 3) for o, _m in ROW if o != sp})


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(sil.ROOT, "art", "pachyrhinosaurus", "previews"))
