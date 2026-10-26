"""Four store plates, original shipped models and current brand; preserves the first edition.

Usage: build/menu-render-venv/bin/python -B tools/capagen/store_cards_v2.py
"""
import copy
import hashlib
import inspect
import json
from pathlib import Path
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import store_cards as base

ROOT, P = base.ROOT, base.P
sys.path.insert(0, str(ROOT / "tools/javagen"))
import gen_species

OUT = ROOT / "art/divulgacao/cartazes/v2"
CACHE = ROOT / "build/store-card-cache/v2"
TABLE = base.sizes()
SPECIES = gen_species.SPECIES
COUNT = len(SPECIES)
MOUNTS = sum(bool(s.get("rideable")) for s in SPECIES)
EN = json.loads((base.ASSETS / "lang/en_us.json").read_text())
NAMES = {s["id"]: EN["entity.terrassic." + s["id"]] for s in SPECIES}
HEROES = set(base.NAMES) | {"ankylosaurus", "triceratops", "argentinosaurus", "parasaurolophus", "therizinosaurus"}
COPY = copy.deepcopy(base.COPY)
for lang, values in {
    "en_us": {"herd": "Herds and titans", "herd_sub": "From armoured herbivores to a 35-metre titanosaur.",
              "catalog": f"{COUNT} creatures", "catalog_sub": "Modelled, textured and animated for Terrassic. Male and female variants.",
              "catalog_kicker": "TERRASSIC / FIELD CATALOGUE", "mounts": "rideable species", "detail": "DETAIL",
              "collected": "A whole prehistoric world", "variants": "Land / skies / seas"},
    "pt_br": {"herd": "Manadas e titãs", "herd_sub": "De herbívoros encouraçados a um titanossauro de 35 metros.",
              "catalog": f"{COUNT} criaturas", "catalog_sub": "Modeladas, texturizadas e animadas para Terrassic. Macho e fêmea por espécie.",
              "catalog_kicker": "TERRASSIC / CATÁLOGO DE CAMPO", "mounts": "espécies de montaria", "detail": "DETALHE",
              "collected": "Um mundo pré-histórico inteiro", "variants": "Terra / céus / mares"},
    "es_es": {"herd": "Manadas y titanes", "herd_sub": "De herbívoros acorazados a un titanosaurio de 35 metros.",
              "catalog": f"{COUNT} criaturas", "catalog_sub": "Modeladas, texturizadas y animadas para Terrassic. Macho y hembra por especie.",
              "catalog_kicker": "TERRASSIC / CATÁLOGO DE CAMPO", "mounts": "especies de montura", "detail": "DETALLE",
              "collected": "Todo un mundo prehistórico", "variants": "Tierra / cielos / mares"},
}.items():
    COPY[lang].update(values)


def render_model(name, rig, texture, pose, size):
    hidden = ("female_display", "saddle")
    points = np.array([world for _, _, corners, _ in rig.cube_faces(pose, hidden) for _, world in corners.values()])
    center = (points.min(0) + points.max(0)) / 2
    flying = next(s["base"] for s in SPECIES if s["id"] == name) == "FlyingDinosaur"
    direction = np.array([-1.3, .75, -1.25] if flying else [-1.9, .48, -.65])
    direction /= np.linalg.norm(direction)
    forward = -direction
    right = np.cross(forward, [0, 1, 0]); right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    local = points - center
    tangent = np.tan(np.radians(22) / 2)
    depth = local @ forward
    distance = max(np.max(np.abs(local @ right) / (tangent * size[0] / size[1]) - depth),
                   np.max(np.abs(local @ up) / tangent - depth)) * 1.12
    camera = {"position": tuple(center + direction * distance), "target": tuple(center), "fov": 22}
    image = base.render3d.render(rig, texture, camera, size, pose, hidden,
                                key=(-.6, .9, -.7), key_col=(1, .96, .88), ambient=(.56, .57, .61),
                                rim_col=(1, .72, .37), rim_power=.40, ss=1)
    assert image.getbbox(), name
    return image.crop(image.getbbox())


def models():
    CACHE.mkdir(parents=True, exist_ok=True)
    images, evidence = {}, []
    render_hash = hashlib.sha256(inspect.getsource(render_model).encode()).hexdigest()
    for species in SPECIES:
        name = species["id"]
        animation = "glide" if species["base"] == "FlyingDinosaur" else "idle"
        rig, texture, pose = base.original_model(name, animation, .25, "male", evidence)
        female = base.ASSETS / f"textures/entity/{name}_female.png"
        assert female.is_file(), name
        evidence[-1]["female_texture_sha256"] = base.sha(female)
        size = (1800, 1100) if name in HEROES else (780, 480)
        key = hashlib.sha256(json.dumps([evidence[-1], size, render_hash, base.sha(Path(base.render3d.__file__))],
                                       sort_keys=True).encode()).hexdigest()
        cached = CACHE / f"{name}-{key[:16]}.png"
        if not cached.exists():
            render_model(name, rig, texture, pose, size).save(cached)
        images[name] = Image.open(cached).convert("RGBA")
        print(name, "verified", flush=True)
    return images, evidence


def background(width=1920, height=1080):
    y, x = np.mgrid[0:height, 0:width]
    xx, yy = x / width, y / height
    t = (yy * .55)[..., None]
    rgb = np.array(P["BASALT_800"]) * (1 - t) + np.array(P["BASALT_950"]) * t
    warm = np.exp(-((xx - .78) ** 2 / .10 + (yy - .56) ** 2 / .17))[..., None] * .11
    rgb = rgb * (1 - warm) + np.array(P["AMBER_700"]) * warm
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert("RGBA")


def header(image, kind, lang, factor=1):
    words = COPY[lang]
    def txt(s, x, y, scale=3, color="STONE_200", face=None, maximum=None):
        base.paste_text(image, s, x * factor, y * factor, scale * factor, color, face,
                        maximum=None if maximum is None else maximum * factor)
    d = ImageDraw.Draw(image)
    d.rectangle((64 * factor, 46 * factor, 110 * factor, 49 * factor), fill=P["AMBER_500"])
    txt(words["catalog_kicker"] if kind == "catalog" else words["kicker"], 128, 37, 2, "STONE_400", maximum=1200)
    txt(words[kind], 64, 88, 5, "BONE_100", base.HEAD, maximum=1340)
    txt(words[kind + "_sub"], 64, 180, 3, maximum=1780)
    logo = Image.open(base.ASSETS / "textures/gui/title/menu/titulo.png").convert("RGBA")
    logo = base.fitted(logo.crop(logo.getbbox()), 330 * factor, 92 * factor)
    image.alpha_composite(logo, (1856 * factor - logo.width, 78 * factor))
    d.line((64 * factor, 1014 * factor, 1856 * factor, 1014 * factor), fill=P["BASALT_600"], width=factor)
    txt(words["footer"], 64, 1032, 2, "STONE_400", maximum=1280)
    platform = base.text(words["platform"], 2 * factor, "STONE_300")
    image.alpha_composite(platform, (1856 * factor - platform.width, 1032 * factor))


def animal(image, source, box, shadow=True):
    x, y, w, h = box
    tile = base.fitted(source, w, h)
    px, py = round(x + (w - tile.width) / 2), round(y + (h - tile.height) / 2)
    if shadow:
        layer = Image.new("RGBA", image.size)
        d = ImageDraw.Draw(layer)
        d.ellipse((px + tile.width * .12, py + tile.height - 9, px + tile.width * .9,
                   py + tile.height + 13), fill=P["BASALT_950"] + (180,))
        image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(8)))
    image.alpha_composite(tile, (px, py))


def label(image, name, lang, x, y, width, scale=3, wings=False):
    base.paste_text(image, NAMES[name], x, y, scale, "BONE_100", maximum=width)
    number = f"{TABLE[name]['real']:g}".replace(".", "," if lang != "en_us" else ".")
    base.paste_text(image, f"{number} m / {COPY[lang]['wings' if wings else 'length']}", x, y + 34,
                    2, "AMBER_500", maximum=width)


def compose(kind, lang, pictures):
    image = background()
    header(image, kind, lang)
    d = ImageDraw.Draw(image)
    if kind == "apex":
        for name, box, label_pos in [
            ("spinosaurus", (64, 270, 730, 255), (76, 552)),
            ("giganotosaurus", (64, 640, 730, 235), (76, 895)),
            ("tyrannosaurus", (830, 280, 1020, 555), (900, 860))]:
            animal(image, pictures[name], box)
            label(image, name, lang, *label_pos, 720)
        d.line((76, 615, 770, 615), fill=P["BASALT_600"])
        animal(image, pictures["velociraptor"], (1465, 820, 370, 135))
        base.paste_text(image, "Velociraptor / 2.07 m" if lang == "en_us" else "Velociraptor / 2,07 m",
                        1440, 961, 2, "STONE_200", maximum=410)
    elif kind == "sky":
        for i, name in enumerate(("pteranodon", "quetzalcoatlus")):
            x = 64 + i * 920
            animal(image, pictures[name], (x, 266, 860, 245), shadow=False)
            label(image, name, lang, x + 20, 528, 800, wings=True)
        water = Image.new("RGBA", image.size)
        wd = ImageDraw.Draw(water)
        wd.rectangle((0, 632, 1919, 1008), fill=P["SKY_400"] + (10,))
        image.alpha_composite(water)
        d = ImageDraw.Draw(image)
        d.line((64, 630, 1856, 630), fill=P["BASALT_500"], width=2)
        for i, name in enumerate(("archelon", "elasmosaurus", "mosasaurus")):
            x = 64 + i * 608
            animal(image, pictures[name], (x, 692, 560, 212), shadow=False)
            label(image, name, lang, x + 16, 921, 540)
    elif kind == "herd":
        base.paste_text(image, str(MOUNTS), 72, 320, 13, "AMBER_500")
        base.paste_text(image, COPY[lang]["mounts"], 76, 453, 3, maximum=420)
        animal(image, pictures["argentinosaurus"], (400, 246, 1040, 460))
        base.paste_text(image, "35 m", 1510, 348, 8, "AMBER_500", maximum=320)
        base.paste_text(image, "Argentinosaurus", 1480, 450, 3, "BONE_100", maximum=380)
        for i, name in enumerate(("ankylosaurus", "triceratops", "parasaurolophus", "therizinosaurus")):
            x = 64 + i * 456
            animal(image, pictures[name], (x, 740, 414, 174))
            label(image, name, lang, x + 8, 927, 430)
    return image.convert("RGB")


def catalog(lang, pictures):
    image = background(3840, 2160)
    header(image, "catalog", lang, factor=2)
    ordered = sorted(NAMES, key=lambda name: (-TABLE[name]["real"], name))
    cell_w, cell_h = 448, 188
    for i, name in enumerate(ordered):
        x, y = 128 + (i % 8) * cell_w, 490 + (i // 8) * cell_h
        d = ImageDraw.Draw(image)
        d.line((x + 8, y + cell_h - 6, x + cell_w - 20, y + cell_h - 6), fill=P["BASALT_600"])
        animal(image, pictures[name], (x + 20, y + 8, cell_w - 46, 126), shadow=False)
        base.paste_text(image, NAMES[name], x + (cell_w - 24) // 2, y + 144, scale=3,
                        color="BONE_100", center=True, maximum=cell_w - 30)
    if len(ordered) == 59:
        x, y = 1530, 1840
        base.paste_text(image, COPY[lang]["collected"], x, y, 5, "AMBER_500", maximum=2100)
        base.paste_text(image, COPY[lang]["variants"], x, y + 70, 4, "STONE_300", maximum=2100)
    return image.convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pictures, evidence = models()
    outputs = []
    for kind in ("apex", "sky", "herd", "catalog"):
        for lang in COPY:
            image = catalog(lang, pictures) if kind == "catalog" else compose(kind, lang, pictures)
            path = OUT / f"{kind}_{lang}_{image.width}x{image.height}.png"
            image.save(path, optimize=True)
            outputs.append({"file": path.name, "size": list(image.size), "sha256": base.sha(path)})
            if kind == "catalog":
                preview = OUT / f"catalog_{lang}_1920x1080.png"
                image.resize((1920, 1080), Image.Resampling.LANCZOS).save(preview, optimize=True)
                outputs.append({"file": preview.name, "size": [1920, 1080], "sha256": base.sha(preview)})
            print(path.name, flush=True)
    manifest = {"species": COUNT, "rideable_species": MOUNTS, "method": "original-model software rendering; native composition",
                "palette_sha256": base.sha(base.PALETTE),
                "wordmark_sha256": base.sha(base.ASSETS / "textures/gui/title/menu/titulo.png"),
                "species_table_sha256": base.sha(ROOT / "tools/javagen/gen_species.py"),
                "font_sources": {str(p.relative_to(ROOT)): base.sha(p) for p in (ROOT / "tools/fontgen").glob("*.py")},
                "models": evidence, "outputs": outputs}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if (OUT / "README.md").exists():
        with zipfile.ZipFile(OUT.parent / "terrassic_cartazes_lojas_v2.zip", "w", zipfile.ZIP_DEFLATED) as archive:
            for path in [OUT / row["file"] for row in outputs] + [OUT / "README.md", OUT / "manifest.json"]:
                archive.write(path, path.name)


if __name__ == "__main__":
    main()
