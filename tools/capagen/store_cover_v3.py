"""Composite the exact shipped wordmark over the selected AI lighting/sky edit.

build/menu-render-venv/bin/python -B tools/capagen/store_cover_v3.py
Image synthesis is performed by the built-in imagegen tool, not this compositor.
"""
import json
from pathlib import Path
import zipfile

from PIL import Image, ImageDraw, ImageFilter
import store_cards as brand
from store_cover import LOGO, SLOGANS

OUT = brand.ROOT / "art/divulgacao/capa/v3"


def main():
    source = OUT / "cena_ia_original.png"
    with Image.open(source) as raw:
        native_size = raw.size
        background = raw.convert("RGBA").resize((1920, 1080), Image.Resampling.LANCZOS)
    for lang, slogan in SLOGANS.items():
        image = background.copy()
        logo = Image.open(LOGO).convert("RGBA")
        logo = brand.fitted(logo.crop(logo.getbbox()), 980, 178)
        # Only the exact brand overlay is composed here; no AI-generated lettering.
        shadow = Image.new("RGBA", image.size)
        ink = Image.new("RGBA", logo.size, brand.P["BASALT_950"] + (0,))
        ink.putalpha(logo.getchannel("A"))
        shadow.alpha_composite(ink, (77, 75))
        image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(9)))
        image.alpha_composite(logo, (70, 68))
        d = ImageDraw.Draw(image)
        d.rectangle((74, 268, 158, 272), fill=brand.P["AMBER_500"])
        tile = brand.text(slogan, 4, "BONE_100")
        text_shadow = Image.new("RGBA", tile.size, brand.P["BASALT_950"] + (0,))
        text_shadow.putalpha(tile.getchannel("A"))
        image.alpha_composite(text_shadow, (77, 298))
        image.alpha_composite(tile, (74, 295))
        image.convert("RGB").save(OUT / f"terrassic_capa_{lang}_1920x1080.png")
    sources = [source, LOGO, brand.PALETTE, Path(__file__), Path(brand.__file__),
               brand.ROOT / "tools/capagen/store_cover.py",
               brand.ROOT / "tools/fontgen/sedimento.py", brand.ROOT / "tools/fontgen/pixfont.py"]
    data = {"method": "Built-in imagegen lighting and sky edit, exact original wordmark composited separately",
            "native_generated_size": native_size, "delivery_size": [1920, 1080],
            "resampled": native_size != (1920, 1080), "screenshot": False,
            "geometry_exactness_certified": False,
            "sources": {str(p.relative_to(brand.ROOT)): brand.sha(p) for p in sources},
            "outputs": {p.name: brand.sha(p) for p in sorted(OUT.glob("terrassic*.png"))}}
    (OUT / "manifest.json").write_text(json.dumps(data, indent=2) + "\n")
    with zipfile.ZipFile(OUT.parent / "terrassic_capa_lojas_v3.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.iterdir()):
            if p.is_file():
                z.write(p, p.name)
    print("Cover variants and ZIP saved", flush=True)


if __name__ == "__main__":
    main()
