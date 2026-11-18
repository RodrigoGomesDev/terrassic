"""The Thescelosaurus v4 next to the other small bipeds of the game (the Gallimimus, the Pachycephalosaurus, the
Dakotaraptor), at their in-game sizes, side-on: one row in colour (the male skins) and one in black (the silhouette,
_silhuetas/sil.py), with the 1.70 m person. Each column is as wide as its animal or its labels, whichever is wider,
so the names never run into each other.

usage:  python3 -B tools/modelgen/handmade/thescelosaurus/rows.py out_dir
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "_engine"), os.path.join(HERE, "..", "_silhuetas")]
from PIL import Image, ImageDraw  # noqa: E402
import geo  # noqa: E402
import sil  # noqa: E402
import sheet  # noqa: E402

ROW = [("thescelosaurus", "Tescelossauro v4"), ("gallimimus", "Galimimo"), ("pachycephalosaurus", "Paquicefalossauro"),
       ("dakotaraptor", "Dakotaraptor")]
PPM = 60


def colour(sp, spec):
    """the game's model in colour, side-on, at PPM pixels per metre (metres via sil.load_game)"""
    tex = Image.open(os.path.join(sil.ASSETS, "textures", "entity", f"{sp}_male.png"))
    raw = geo.load_geo(os.path.join(sil.ASSETS, "geo", "entity", f"{sp}.geo.json"))
    spec = dict(spec, tw=raw["tw"], th=raw["th"])
    x0, x1, y0, y1 = sil.extent(spec, sil.SIDE)
    W, H = int((x1 - x0) * PPM) + 2, int((y1 - y0) * PPM) + 2
    return geo.render(spec, tex, 90, 0, (W, H), bg=sheet.BG, margin=0.0)[0].convert("RGB")


def black(spec):
    x0, x1, y0, y1 = sil.extent(spec, sil.SIDE)
    W, H = int((x1 - x0) * PPM) + 2, int((y1 - y0) * PPM) + 2
    im = Image.new("RGB", (W, H), sheet.BG)
    sil.draw(im, spec, sil.SIDE, PPM, (0, H - 1))
    return im


def main(out):
    os.makedirs(out, exist_ok=True)
    specs = {sp: sil.load_game(sp) for sp, _n in ROW}
    sigs = {sp: sil.signature(s) for sp, s in specs.items()}
    f1, f2 = sil.font(24, True), sil.font(17)
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    tw = lambda s, f: int(probe.textlength(s, font=f))
    subs = {}
    for sp, _name in ROW:
        best = max((sil.similarity(sigs[sp], sigs[o]), n) for o, n in ROW if o != sp)
        subs[sp] = f"mais parecido: {best[1]} {best[0]:.2f}"
    cols = [(colour(sp, specs[sp]), black(specs[sp])) for sp, _n in ROW]
    hum = sil.human()
    hx0, hx1, hy0, hy1 = sil.extent(hum, (0, 0))
    hw = int((hx1 - hx0) * PPM)
    widths = [max(c.width, tw(name, f1), tw(subs[sp], f2)) for (c, _b), (sp, name) in zip(cols, ROW)]
    pad, gap = 28, 40
    W = pad * 2 + hw + gap + sum(widths) + gap * (len(ROW) - 1)

    def strip(which, label_sub):
        hmax = max(c[which].height for c in cols)
        H = pad + hmax + 12 + (64 if label_sub else 36)
        im = Image.new("RGB", (W, H), sheet.BG)
        d = ImageDraw.Draw(im)
        base = pad + hmax
        d.line([(pad // 2, base), (W - pad // 2, base)], fill=sheet.GROUND, width=2)
        sil.draw(im, hum, (0, 0), PPM, (pad, base), sheet.PERSON)
        x = pad + hw + gap
        for (c, (sp, name)), w in zip(zip(cols, ROW), widths):
            pic = c[which]
            im.paste(pic, (x + (w - pic.width) // 2, base - pic.height))
            d.text((x, base + 8), name, fill=sheet.TEXT, font=f1)
            if label_sub:
                d.text((x, base + 38), subs[sp], fill=sheet.SUB, font=f2)
            x += w + gap
        return im

    img = sheet.stack([strip(0, False), strip(1, True)], "Tescelossauro v4 ao lado dos outros bípedes pequenos",
                      "No tamanho do jogo, de lado: em cima a cor, embaixo a silhueta em preto. "
                      "Semelhança 0..1 (Dice de lado e 3/4).")
    img.save(os.path.join(out, "fileira_bipedes.png"))
    for sp, _n in ROW:
        print(sp, {o: round(sil.similarity(sigs[sp], sigs[o]), 3) for o, _m in ROW if o != sp})


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(sil.ROOT, "art", "thescelosaurus", "previews"))
