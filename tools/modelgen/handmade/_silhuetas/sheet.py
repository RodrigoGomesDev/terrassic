"""Montagem das folhas: fileiras de silhuetas em preto no mesmo chão, com a pessoa de 1,70 m."""
from PIL import Image, ImageDraw

import sil

BG = (236, 233, 224)
INK = (0, 0, 0)
PERSON = (70, 86, 110)
GROUND = (150, 145, 132)
TEXT = (40, 40, 40)
SUB = (95, 95, 95)


def row(items, ppm, view=sil.SIDE, gap=0.9, person=True, label_h=60, pad=24, title_font=22, sub_font=16):
    """items: [(spec, título, subtítulo)]; devolve uma imagem com todos no mesmo chão"""
    hum = sil.human()
    things = ([(hum, None, None)] if person else []) + [(s, t or "", u) for s, t, u in items]
    views = [(0, 0) if t is None else view for _s, t, _u in things]
    ext = [sil.extent(s, v) for (s, _t, _u), v in zip(things, views)]
    widths = [(e[1] - e[0]) * ppm for e in ext]
    hmax = max((e[3] - e[2]) * ppm for e in ext)
    W = int(pad * 2 + sum(widths) + gap * ppm * (len(things) - 1))
    H = int(pad + hmax + 14 + label_h)
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    base = pad + hmax
    d.line([(pad // 2, base), (W - pad // 2, base)], fill=GROUND, width=2)
    x = pad
    f1, f2 = sil.font(title_font, True), sil.font(sub_font)
    for (s, t, u), w, v in zip(things, widths, views):
        sil.draw(img, s, v, ppm, (x, base), PERSON if t is None else INK)
        if t:
            d.text((x, base + 8), t, fill=TEXT, font=f1)
        if u:
            d.text((x, base + 10 + title_font + 2), u, fill=SUB, font=f2)
        x += w + gap * ppm
    return img


def stack(images, title=None, sub=None, pad=24):
    W = max(i.width for i in images) + pad * 2
    head = 0
    if title:
        head = 56 + (28 if sub else 0)
    H = head + sum(i.height for i in images) + pad * (len(images) + 1)
    out = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(out)
    if title:
        d.text((pad, pad), title, fill=TEXT, font=sil.font(30, True))
        if sub:
            d.text((pad, pad + 40), sub, fill=SUB, font=sil.font(18))
    y = head + pad
    for i in images:
        out.paste(i, (pad, y)); y += i.height + pad
    return out
