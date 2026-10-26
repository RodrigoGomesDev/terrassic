"""Rebrand the original Caçada render without synthesising or moving any scene geometry.

Usage: build/menu-render-venv/bin/python -B tools/capagen/store_cover.py
"""
import json
from pathlib import Path
import zipfile

import numpy as np
from PIL import Image, ImageDraw
import store_cards as brand

ROOT = brand.ROOT
OUT = ROOT / "art/divulgacao/capa/v2"
SOURCE = ROOT / "art/capa/terrassic_capa_cacada_sem_titulo.png"
LOGO = brand.ASSETS / "textures/gui/title/menu/titulo.png"
SLOGANS = {"en_us": "The past has awoken.", "pt_br": "O passado acordou.",
           "es_es": "El pasado despertó."}


def scene():
    rgb = np.asarray(Image.open(SOURCE).convert("RGB"), dtype=float) / 255
    # Continuous pointwise grading only: no repaint, inpainting, resampling or geometry edits.
    lum = rgb @ np.array([.2126, .7152, .0722])
    neutral = lum[..., None]
    rgb = neutral * .32 + rgb * .68
    rgb = np.power(rgb, .88) * np.array([.96, 1.015, 1.12])
    shadow = (1 - np.clip(lum / .48, 0, 1)) ** 2
    rgb += shadow[..., None] * np.array([.016, .019, .028])
    height, width = lum.shape
    y, x = np.mgrid[:height, :width]
    # Basalt/dusk wash in the sky; transparent at the animals' height.
    sky = (np.clip(1 - y / (height * .54), 0, 1) ** 1.5) * .64
    dusk = np.array(brand.P["DUSK_700"]) / 255
    rgb = rgb * (1 - sky[..., None]) + dusk * sky[..., None]
    # Readable logo area with a gradual fade, not a rectangular text panel.
    mask = np.exp(-((x / width - .12) ** 2 / .16 + (y / height - .12) ** 2 / .075)) * .38
    basalt = np.array(brand.P["BASALT_800"]) / 255
    rgb = rgb * (1 - mask[..., None]) + basalt * mask[..., None]
    return Image.fromarray(np.uint8(np.clip(rgb * 255, 0, 255))).convert("RGBA")


def cover(background, lang):
    image = background.copy()
    logo = Image.open(LOGO).convert("RGBA")
    logo = brand.fitted(logo.crop(logo.getbbox()), 895, 160)
    image.alpha_composite(logo, (86, 85))
    d = ImageDraw.Draw(image)
    d.rectangle((88, 278, 160, 281), fill=brand.P["AMBER_500"])
    brand.paste_text(image, SLOGANS[lang], 88, 304, 4, "BONE_100", maximum=960)
    return image.convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bg = scene()
    assert bg.size == (1920, 1080)
    bg.convert("RGB").save(OUT / "cacada_sem_titulo_1920x1080.png")
    for lang in SLOGANS:
        cover(bg, lang).save(OUT / f"terrassic_capa_{lang}_1920x1080.png")
    sources = [SOURCE, LOGO, brand.PALETTE, Path(__file__), Path(brand.__file__),
               ROOT / "tools/fontgen/sedimento.py", ROOT / "tools/fontgen/pixfont.py"]
    manifest = {"method": "Pointwise colour grading and original brand overlay; scene geometry unchanged.",
                "screenshot": False, "default_language": "en_us",
                "sources": {str(p.relative_to(ROOT)): brand.sha(p) for p in sources},
                "outputs": {p.name: brand.sha(p) for p in sorted(OUT.glob("*.png"))}}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    with zipfile.ZipFile(OUT.parent / "terrassic_capa_lojas_v2.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(OUT.iterdir()):
            if p.is_file():
                archive.write(p, p.name)
    print("Four PNGs and cover package generated:", OUT)


if __name__ == "__main__":
    main()
