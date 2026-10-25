"""
Covers: the block scenes from cenas.py with the TERRASSIC title and the slogan. The slogan is in English on every
cover (Rodrigo 2026-10-24: sells better everywhere); --langs renders the pt-BR / es-ES variants too.

usage:  BACKEND=cycles python3 cenas.py <scene> && python3 capas.py [scene ...] [--langs]
        -> art/capa/terrassic_capa_<scene>.png (and _<lang>.png with --langs)
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import render3d as r3  # noqa: E402
from banner import title_block  # noqa: E402

ART = os.path.join(r3.ROOT, "art", "capa")
LANGS = ("pt_br", "en_us", "es_es")  # only with --langs
# scene -> (title x, y as fractions of the image, finish, how much to darken the sky behind it)
LAYOUT = {
    "ribeira": (0.05, 0.07, "pedra", 0.55),
    "falesia": (0.04, 0.07, "pedra", 0.75),
    "neblina": (0.25, 0.06, "pedra", 0.6),
    "vale": (0.04, 0.06, "pedra", 0.5),
    "manada": (0.25, 0.05, "pedra", 0.6),
    "cacada": (0.04, 0.06, "pedra", 0.55),
    "costa": (0.03, 0.68, "pedra", 0.5),
    "espreita": (0.25, 0.05, "pedra", 0.6),
}


def shade_behind(img, box, strength=0.55, blur=90):
    """Darken softly behind the title so it reads on any sky."""
    W, H = img.size
    m = Image.new("L", (W, H), 0)
    x0, y0, x1, y1 = box
    m.paste(255, (x0, y0, x1, y1))
    m = m.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(img.convert("RGB"), float)
    k = np.asarray(m, float)[..., None] / 255 * strength
    return Image.fromarray((a * (1 - k)).astype(np.uint8), "RGB")


def capa(scene, lang):
    img = Image.open(os.path.join(ART, "cenas", f"{scene}.png")).convert("RGB")
    W, H = img.size
    fx, fy, finish, dark = LAYOUT[scene]
    x, y = int(W * fx), int(H * fy)
    img = shade_behind(img, (x + 20, y + 10, x + 930, y + 250), dark)
    img = img.convert("RGBA")
    title_block(img, x, y, finish, lang)
    return img.convert("RGB")


if __name__ == "__main__":
    args = sys.argv[1:]
    langs = "--langs" in args
    names = [a for a in args if a != "--langs"] or list(LAYOUT)
    for name in names:
        capa(name, "en_us").save(os.path.join(ART, f"terrassic_capa_{name}.png"))
        if langs:
            for lang in LANGS:
                capa(name, lang).save(os.path.join(ART, f"terrassic_capa_{name}_{lang}.png"))
        print(name, "ok")
