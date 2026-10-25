"""
Textures of the Terrassic main menu (client/title/TerrassicMenuScreen.java, docs/MENU.md):

  textures/gui/title/menu/fundo_<cena>.png  1920x1080 scene behind the menu (rendered by menu_cenas.py with the
                                            Blender backend of tools/capagen), with the left side and the bottom
                                            darkened so the title, the options and the placard stay readable
  textures/gui/title/menu/titulo.png        the TERRASSIC title in Degraus, like the covers (tools/capagen/titulo.py,
                                            finish "pedra"), on the 950x150 canvas TerrassicMenuScreen expects
  textures/gui/title/menu/icones.png        16x16 option icons (icones.py): one column per icon, rows idle/hover/dim

usage:
  BACKEND=cycles SAMPLES=96 python3 -B menu_cenas.py ../capagen /tmp/cenas nevoa --wip <folder with tyrannosaurus_v3.py>
  python3 -B menu_assets.py /tmp/cenas
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "textures", "gui", "title", "menu")
sys.path.insert(0, os.path.join(ROOT, "tools", "capagen"))
sys.path.insert(0, HERE)

import icones  # noqa: E402

SCENES = ["nevoa", "triceratops", "espinossauro", "pteranodonte"]
ICON_ORDER = ["singleplayer", "multiplayer", "mods", "options", "quit", "language", "accessibility", "rules"]
SHADE = np.array([12, 11, 10], float)


def background(src):
    """The scene with the left side (title, options) and the bottom (placard, footer) darkened."""
    img = Image.open(src).convert("RGB").resize((1920, 1080), Image.LANCZOS)
    a = np.asarray(img, float)
    xx = np.linspace(0, 1, a.shape[1])[None, :, None]
    yy = np.linspace(0, 1, a.shape[0])[:, None, None]
    left = np.clip(1 - xx / 0.60, 0, 1) ** 1.3 * 0.86
    bottom = np.clip((yy - 0.70) / 0.30, 0, 1) ** 1.4 * 0.75
    top = np.clip(1 - yy / 0.12, 0, 1) * 0.25
    k = 1 - (1 - left) * (1 - bottom) * (1 - top)
    return Image.fromarray((a * (1 - k) + SHADE * k).astype(np.uint8), "RGB")


def icon_atlas():
    out = Image.new("RGBA", (16 * len(ICON_ORDER), 48), (0, 0, 0, 0))
    for i, name in enumerate(ICON_ORDER):
        for j, state in enumerate(("idle", "hover", "dim")):
            out.alpha_composite(icones.icon(name, state), (i * 16, j * 16))
    return out


def main(scene_dir):
    os.makedirs(OUT, exist_ok=True)
    for scene in SCENES:
        background(os.path.join(scene_dir, scene + ".png")).save(os.path.join(OUT, f"fundo_{scene}.png"), optimize=True)
    icon_atlas().save(os.path.join(OUT, "icones.png"))
    import titulo
    titulo.title_in(950, 150, "pedra").save(os.path.join(OUT, "titulo.png"), optimize=True)  # TITLE_W x TITLE_H
    print("menu textures written to", OUT)


if __name__ == "__main__":
    main(sys.argv[1])
