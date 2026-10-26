"""Rebuild the two old store plates from shipped models, fonts and the current palette. No image synthesis.

Usage: build/menu-render-venv/bin/python -B tools/capagen/store_cards.py
"""
import ast
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "tools/menugen"), str(ROOT / "tools/fontgen"), str(ROOT / "tools/capagen")]
from menu_vanilla import original_model
import render3d
import build as fontbuild

OUT = ROOT / "art/divulgacao/cartazes/v1"
ASSETS = ROOT / "common/src/main/resources/assets/terrassic"
PALETTE = ROOT / "common/src/main/java/com/terrassic/client/ui/TerrassicPalette.java"
P = {name: tuple(bytes.fromhex(value)[1:]) for name, value in
     re.findall(r"public static final int (\w+) = 0x([0-9A-F]{8});", PALETTE.read_text())}
fontbuild.make_fonts()
FONT = fontbuild.FONTS["sedimento"]
HEAD = fontbuild.FONTS["entalhe"]
NAMES = {"tyrannosaurus": "Tyrannosaurus", "spinosaurus": "Spinosaurus", "giganotosaurus": "Giganotosaurus",
         "velociraptor": "Velociraptor", "pteranodon": "Pteranodon", "quetzalcoatlus": "Quetzalcoatlus",
         "archelon": "Archelon", "elasmosaurus": "Elasmosaurus", "mosasaurus": "Mosasaurus"}
COPY = {
    "en_us": {"sky": "Skies and seas", "apex": "Cretaceous predators", "kicker": "FIELD GUIDE / LATE CRETACEOUS",
              "sky_sub": "Pterosaurs above the coast. Marine reptiles beneath the waves.",
              "apex_sub": "River hunters, giant theropods and swift raptors. Meet the Cretaceous fauna.",
              "air": "ABOVE THE COAST", "sea": "BENEATH THE WAVES", "wings": "wingspan", "length": "length",
              "footer": "Original Terrassic models / Shown at different scales", "platform": "Minecraft 1.20.1 / Fabric + Forge"},
    "pt_br": {"sky": "Céus e mares", "apex": "Predadores do Cretáceo", "kicker": "GUIA DE CAMPO / CRETÁCEO SUPERIOR",
              "sky_sub": "Pterossauros sobre a costa. Répteis marinhos sob as ondas.",
              "apex_sub": "Caçadores de rio, terópodes gigantes e raptores ágeis. Conheça a fauna do Cretáceo.",
              "air": "SOBRE A COSTA", "sea": "SOB AS ONDAS", "wings": "envergadura", "length": "comprimento",
              "footer": "Modelos originais do Terrassic / Exibidos em escalas diferentes", "platform": "Minecraft 1.20.1 / Fabric + Forge"},
    "es_es": {"sky": "Cielos y mares", "apex": "Depredadores del Cretácico", "kicker": "GUÍA DE CAMPO / CRETÁCICO SUPERIOR",
              "sky_sub": "Pterosaurios sobre la costa. Reptiles marinos bajo las olas.",
              "apex_sub": "Cazadores de río, terópodos gigantes y raptores ágiles. Conoce la fauna del Cretácico.",
              "air": "SOBRE LA COSTA", "sea": "BAJO LAS OLAS", "wings": "envergadura", "length": "longitud",
              "footer": "Modelos originales de Terrassic / Mostrados a distintas escalas", "platform": "Minecraft 1.20.1 / Fabric + Forge"}}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sizes():
    tree = ast.parse((ROOT / "tools/javagen/gen_species.py").read_text())
    node = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "SIZES" for t in n.targets))
    return eval(compile(ast.Expression(node), "SIZES", "eval"), {"__builtins__": {}, "dict": dict})


def text(s, scale=3, color="STONE_200", face=None):
    f = face or FONT
    result = Image.new("RGBA", (max(1, f.text_width(s)), f.cell_h + f.extra + 3))
    f.draw(result, s, 0, f.extra, P[color] + (255,))
    return result.resize((result.width * scale, result.height * scale), Image.Resampling.NEAREST)


def paste_text(image, s, x, y, scale=3, color="STONE_200", face=None, center=False, maximum=None):
    while True:
        tile = text(s, scale, color, face)
        if maximum is None or tile.width <= maximum or scale == 1:
            break
        scale -= 1
    assert maximum is None or tile.width <= maximum, s
    image.alpha_composite(tile, (round(x - tile.width / 2) if center else x, y))


def model(name, evidence):
    animation = "glide" if name in ("pteranodon", "quetzalcoatlus") else "idle"
    rig, texture, pose = original_model(name, animation, .25, "male", evidence)
    hidden = ("female_display", "saddle")
    points = np.array([world for _, _, corners, _ in rig.cube_faces(pose, hidden)
                       for _, world in corners.values()])
    center = (points.min(0) + points.max(0)) / 2
    span = float(np.linalg.norm(points.max(0) - points.min(0)))
    direction = np.array([-1.4, .65, -1.2] if animation == "glide" else [-1.9, .55, -.7])
    camera = {"position": tuple(center + direction * span), "target": tuple(center), "fov": 32}
    rendered = render3d.render(rig, texture, camera, (1400, 900), pose, hidden,
                               key=(.2, .8, -.8), key_col=(1, .95, .85), ambient=(.55, .54, .58),
                               rim_col=(1, .71, .35), rim_power=.35, ss=1)
    return rendered.crop(rendered.getbbox())


def fitted(source, width, height):
    factor = min(width / source.width, height / source.height)
    return source.resize((round(source.width * factor), round(source.height * factor)), Image.Resampling.LANCZOS)


def base(kind, lang):
    image = Image.new("RGBA", (1920, 1080), P["BASALT_800"] + (255,))
    d = ImageDraw.Draw(image)
    d.rectangle((0, 0, 1919, 7), fill=P["AMBER_700"])
    d.rectangle((64, 48, 103, 51), fill=P["AMBER_500"])
    words = COPY[lang]
    paste_text(image, words["kicker"], 118, 39, scale=2, color="STONE_400", maximum=1250)
    paste_text(image, words[kind], 64, 82, scale=5, color="AMBER_500", face=HEAD, maximum=1340)
    paste_text(image, words[kind + "_sub"], 64, 176, scale=3, maximum=1780)
    logo = Image.open(ASSETS / "textures/gui/title/menu/titulo.png").convert("RGBA")
    logo = fitted(logo.crop(logo.getbbox()), 340, 100)
    image.alpha_composite(logo, (1848 - logo.width, 74))
    d.line((64, 1014, 1856, 1014), fill=P["BASALT_500"], width=2)
    paste_text(image, words["footer"], 64, 1030, scale=2, color="STONE_400", maximum=1250)
    platform = text(words["platform"], 2, "STONE_300")
    image.alpha_composite(platform, (1856 - platform.width, 1030))
    return image


def panel(image, rect, tint=None):
    d = ImageDraw.Draw(image)
    x0, y0, x1, y1 = rect
    d.rectangle(rect, fill=P["BASALT_900"], outline=P["BASALT_600"], width=2)
    d.line((x0 + 2, y0 + 2, x1 - 2, y0 + 2), fill=P[tint or "BASALT_500"], width=3)


def label(image, name, real, lang, x, y, width, wings=False):
    paste_text(image, NAMES[name], x, y, center=True, scale=3, color="BONE_100", maximum=width)
    measure = f"{real:g}".replace(".", "," if lang != "en_us" else ".")
    description = COPY[lang]["wings" if wings else "length"]
    paste_text(image, f"{measure} m / {description}", x, y + 37, center=True,
               scale=2, color="AMBER_500", maximum=width)


def compose(kind, lang, models, table):
    im = base(kind, lang)
    if kind == "sky":
        for index, name in enumerate(("pteranodon", "quetzalcoatlus")):
            x = 64 + index * 912
            panel(im, (x, 252, x + 880, 572), "SKY_400")
            paste_text(im, COPY[lang]["air"], x + 24, 268, scale=2, color="STONE_400")
            cut = fitted(models[name], 780, 182)
            im.alpha_composite(cut, (x + (880 - cut.width) // 2, 305 + (182 - cut.height) // 2))
            label(im, name, table[name]["real"], lang, x + 440, 493, 830, wings=True)
        for index, name in enumerate(("archelon", "elasmosaurus", "mosasaurus")):
            x = 64 + index * 608
            panel(im, (x, 608, x + 576, 982), "BASALT_500")
            paste_text(im, COPY[lang]["sea"], x + 24, 626, scale=2, color="STONE_400")
            cut = fitted(models[name], 525, 230)
            im.alpha_composite(cut, (x + (576 - cut.width) // 2, 665 + (230 - cut.height) // 2))
            label(im, name, table[name]["real"], lang, x + 288, 895, 545)
    else:
        for index, name in enumerate(("spinosaurus", "giganotosaurus", "tyrannosaurus", "velociraptor")):
            x = 64 + (index % 2) * 912
            y = 252 + (index // 2) * 380
            panel(im, (x, y, x + 880, y + 350))
            paste_text(im, f"0{index + 1}", x + 24, y + 18, scale=2, color="STONE_400")
            cut = fitted(models[name], 780, 215)
            im.alpha_composite(cut, (x + (880 - cut.width) // 2, y + 40 + (215 - cut.height) // 2))
            label(im, name, table[name]["real"], lang, x + 440, y + 268, 830)
    return im.convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    evidence = []
    models = {}
    for name in NAMES:
        models[name] = model(name, evidence)
        print(name, "original model verified and rendered", flush=True)
    table = sizes()
    outputs = []
    for kind in ("sky", "apex"):
        for lang in COPY:
            path = OUT / f"{kind}_{lang}_1920x1080.png"
            compose(kind, lang, models, table).save(path, optimize=True)
            outputs.append({"file": path.name, "size": [1920, 1080], "sha256": sha(path)})
            print(path.name, flush=True)
    (OUT / "manifest.json").write_text(json.dumps({"method": "software render of original models; native fonts and layout",
        "palette_sha256": sha(PALETTE), "wordmark_sha256": sha(ASSETS / "textures/gui/title/menu/titulo.png"),
        "font_sources": {str(p.relative_to(ROOT)): sha(p) for p in
                         (ROOT / "tools/fontgen").glob("*.py")},
        "sizes_m": {name: table[name]["real"] for name in NAMES},
        "models": evidence, "outputs": outputs}, indent=2) + "\n")
    if (OUT / "README.md").exists():
        archive = OUT.parent / "terrassic_cartazes_lojas.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as pack:
            for path in [OUT / row["file"] for row in outputs] + [OUT / "README.md", OUT / "manifest.json"]:
                pack.write(path, path.name)
        print(archive, flush=True)


if __name__ == "__main__":
    main()
