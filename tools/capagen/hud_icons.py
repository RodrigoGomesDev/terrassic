"""
Icons of the Terrassic HUD (v0.8, phase M5), drawn as pixel grids: one 64x32 atlas.

usage:  python3 hud_icons.py  -> common/src/main/resources/assets/terrassic/textures/gui/hud.png

  row 0 (8x8 each, x = 0, 8, 16, ...): follow (footprint), sit, fight (claw), sleep, cargo (basket), hunger (meat), heart
  row 1 (16x16 at x = 0): the Rift alert, a cracked amber shard
Positions are mirrored in client/TerrassicHud.java.
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "common", "src", "main", "resources", "assets", "terrassic", "textures", "gui", "hud.png")

PAL = {
    ".": (0, 0, 0, 0),
    "k": (26, 16, 22, 255),     # outline
    "a": (255, 182, 60, 255),   # amber
    "A": (255, 236, 190, 255),  # amber highlight
    "d": (224, 102, 28, 255),   # deep amber
    "w": (232, 220, 192, 255),  # paper / bone
    "b": (122, 86, 52, 255),    # wicker brown
    "B": (176, 128, 74, 255),   # wicker light
    "r": (196, 46, 46, 255),    # red
    "R": (240, 110, 100, 255),  # red highlight
    "m": (168, 72, 52, 255),    # meat
    "M": (214, 120, 90, 255),   # meat light
    "g": (120, 150, 200, 255),  # sleep blue
}

ICONS8 = [
    # follow: a three-toed footprint
    ["..k.k.k.",
     ".kak.kak",
     ".kak.ka.",
     "..kakak.",
     ".kaaaak.",
     ".kaaaak.",
     "..kaak..",
     "...kk..."],
    # sit: resting, a low mound with a dot
    ["........",
     "........",
     "...kk...",
     "..kwwk..",
     ".kwwwwk.",
     "kwwwwwwk",
     "kkkkkkkk",
     "........"],
    # fight: a curved claw
    ["....kk..",
     "...krk..",
     "..krRk..",
     "..krk...",
     ".krRk...",
     ".krk....",
     "krk.....",
     "kk......"],
    # sleep: z z
    ["....kkkk",
     ".....gk.",
     "....gk..",
     "...kkkk.",
     "kkk.....",
     "..gk....",
     ".gk.....",
     "kkk....."],
    # cargo: a basket
    ["..kkkk..",
     ".k....k.",
     "kkkkkkkk",
     "kBbBbBbk",
     "kbBbBbBk",
     "kBbBbBbk",
     ".kbBbBk.",
     "..kkkk.."],
    # hunger: a piece of meat on a bone
    ["....kkk.",
     "...kMMmk",
     "..kMmmmk",
     ".kMmmmk.",
     ".kmmmk..",
     "kwkkk...",
     "kwk.....",
     ".k......"],
    # heart (our own shape: a rounded leaf-like heart)
    [".kk..kk.",
     "kRrkkrrk",
     "kRrrrrrk",
     "krrrrrrk",
     ".krrrrk.",
     "..krrk..",
     "...kk...",
     "........"],
]

RIFT16 = [
    "......kk........",
    ".....kAak.......",
    "....kAaaak......",
    "...kAaAdaak.....",
    "...kaaAkdaak....",
    "..kAaakAkdaak...",
    "..kaaadkAkdak...",
    ".kAaaaakdAkak...",
    ".kaaaaadkAkdak..",
    ".kdaaaaakdkdak..",
    "..kdaaaaakkdak..",
    "..kddaaaaaddak..",
    "...kddaaaaddk...",
    "....kkddddkk....",
    "......kkkk......",
    "................",
]


def draw(img, grid, ox, oy):
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            img.putpixel((ox + x, oy + y), PAL[ch])


def main():
    img = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    for i, grid in enumerate(ICONS8):
        draw(img, grid, i * 8, 0)
    draw(img, RIFT16, 0, 16)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print("hud icons:", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
