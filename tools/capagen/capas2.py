"""
Covers for the cenas2.py scenes: TERRASSIC in Degraus (pedra) + the slogan in osso, over the Cycles render.

usage:  python3 -B capas2.py <render.png> <scene> [out_dir] [--langs]
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from banner import title_block  # noqa: E402
from capas import LANGS, shade_behind  # noqa: E402

# scene -> (title x, y as fractions of the image, finish, how much to darken the sky behind it)
LAYOUT = {
    "falesia": (0.035, 0.06, "pedra", 0.45),
    "voo": (0.035, 0.62, "pedra", 0.45),
    "duelo": (None, 0.04, "pedra", 0.35),      # None = centred
    "familia": (0.035, 0.06, "pedra", 0.45),
    "tempestade": (0.035, 0.06, "pedra", 0.45),
    "floresta": (0.035, 0.06, "pedra", 0.30),
    "espreita": (0.035, 0.06, "pedra", 0.30),
}
# lettering size per scene (1 = the standard 2 px texel at 1920 wide); Rodrigo 30/10: a bit smaller on Espreita
LOGO = {"espreita": 0.83}


def capa(img, scene, lang="en_us", logo=None):
    """logo < 1 shrinks the lettering: the title is drawn with whole texels on a canvas k times bigger, then the
    cover is scaled back down, so the letters keep their pixel shapes at sizes between whole texels."""
    img = img.convert("RGB")
    W, H = img.size
    fx, fy, finish, dark = LAYOUT[scene]
    logo = LOGO.get(scene, 1.0) if logo is None else logo
    base = 2 * W / 1920
    k, texel = min(((k, max(1, round(base * k * logo))) for k in (1, 2, 3, 4)),
                   key=lambda kt: (abs(kt[1] / kt[0] - base * logo), kt[0]))
    big = img.resize((W * k, H * k), Image.LANCZOS) if k > 1 else img
    BW, BH = big.size
    y = int(BH * fy)
    probe = Image.new("RGBA", (BW, BH))
    if fx is None:
        x0, _y0, x1, _y1 = title_block(probe, 0, y, finish, lang, texel)
        x = (BW - (x1 - x0)) // 2
        probe = Image.new("RGBA", (BW, BH))
    else:
        x = int(BW * fx)
    x0, y0, x1, y1 = title_block(probe, x, y, finish, lang, texel)
    m = texel / 2
    big = shade_behind(big, (x0 + int(20 * m), y0 + int(10 * m), x1 - int(20 * m), y1 - int(10 * m)), dark,
                       int(90 * BW / 1920)).convert("RGBA")
    title_block(big, x, y, finish, lang, texel)
    out = big.convert("RGB")
    return out.resize((W, H), Image.LANCZOS) if k > 1 else out


if __name__ == "__main__":
    args = sys.argv[1:]
    langs = "--langs" in args
    args = [a for a in args if a != "--langs"]
    src, scene = args[0], args[1]
    out = args[2] if len(args) > 2 else os.path.dirname(os.path.abspath(src))
    im = Image.open(src)
    capa(im, scene).save(os.path.join(out, f"terrassic_capa_{scene}.png"))
    if langs:
        for lang in LANGS:
            capa(im, scene, lang).save(os.path.join(out, f"terrassic_capa_{scene}_{lang}.png"))
    print(scene, "ok")
