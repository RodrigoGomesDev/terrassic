"""
Banners from one wide master render (cenas2.py desfile): each platform's crop, with and without the title.

usage:  python3 -B banners.py <master.png> <out_dir>

Crops keep the parade band (the animals along the shore) and leave the title in each platform's safe area
(Rodrigo 04/11/2026; sizes checked on the platforms' help pages):
  Discord server banner 1920x1080 (16:9; the channel list covers the bottom, title in the upper half)
  Discord invite splash 1920x1080 (Discord darkens it and writes the server name in the middle: no title)
  Discord profile banner 680x240 (5:2; the avatar covers the bottom left: title on the right)
  Ko-fi cover 1200x400 (3:1; phones trim the sides: title centred)
  X / Twitter header 1500x500 (3:1; the avatar covers the bottom left)
  YouTube 2560x1440 (only the centre 1546x423 shows on every device: title and animals inside it)
  Social preview (GitHub, links) 1280x640 (2:1)
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from banner import title_block  # noqa: E402
from capas import shade_behind  # noqa: E402

# name -> (width, height, top of the crop as a fraction of the master height, title x, title y, title size)
# title x: None = centred, negative = right-aligned that far from the right edge; y as a fraction of the crop
SPECS = {
    "discord_servidor_1920x1080": (1920, 1080, None, None, 0.07, 1.0),
    "discord_convite_1920x1080": (1920, 1080, None, False, 0, 0),
    "discord_perfil_680x240": (680, 240, 0.16, None, 0.08, 0.62),
    "kofi_1200x400": (1200, 400, 0.16, None, 0.07, 0.85),
    "x_twitter_1500x500": (1500, 500, 0.16, None, 0.07, 0.85),
    "youtube_2560x1440": (2560, 1440, None, None, 0.355, 0.62),
    "social_1280x640": (1280, 640, 0.10, None, 0.07, 0.9),
}


def crop(master, w, h, top):
    W, H = master.size
    ch = round(W * h / w)
    if ch > H:  # taller than the master (never with these sizes): trim the sides instead
        cw = round(H * w / h)
        box = ((W - cw) // 2, 0, (W + cw) // 2, H)
    else:
        y0 = round((H - ch) / 2) if top is None else min(H - ch, round(H * top))
        box = (0, y0, W, y0 + ch)
    return master.crop(box).resize((w, h), Image.LANCZOS)


def titled(img, fx, fy, size, lang="en_us"):
    W, H = img.size
    k = 2 if W < 1600 else 1  # small banners: draw at twice the size and scale down, so the letters stay crisp
    big = img.resize((W * k, H * k), Image.LANCZOS) if k > 1 else img
    BW, BH = big.size
    texel = max(1, round(2 * BW / 1920 * size))
    probe = Image.new("RGBA", (BW, BH))
    y = int(BH * fy)
    x0, _y0, x1, _y1 = title_block(probe, 0, y, "pedra", lang, texel)
    tw = x1 - x0
    x = (BW - tw) // 2 if fx is None else (int(BW * (1 + fx)) - tw if fx < 0 else int(BW * fx))
    probe = Image.new("RGBA", (BW, BH))
    bx0, by0, bx1, by1 = title_block(probe, x, y, "pedra", lang, texel)
    m = texel / 2
    big = shade_behind(big, (bx0 + int(20 * m), by0 + int(10 * m), bx1 - int(20 * m), by1 - int(10 * m)), 0.30,
                       int(90 * BW / 1920)).convert("RGBA")
    title_block(big, x, y, "pedra", lang, texel)
    out = big.convert("RGB")
    return out.resize((W, H), Image.LANCZOS) if k > 1 else out


# masters whose middle sky is busy (the flock in revoada): the title goes low, over the open water
SPECS_LOW = {
    "discord_servidor_1920x1080": (1920, 1080, None, 0.34, 0.62, 0.8),
    "discord_convite_1920x1080": (1920, 1080, None, False, 0, 0),
    "discord_perfil_680x240": (680, 240, 0.30, None, 0.66, 0.62),
    "kofi_1200x400": (1200, 400, 0.30, None, 0.64, 0.85),
    "x_twitter_1500x500": (1500, 500, 0.30, None, 0.64, 0.85),
    "youtube_2560x1440": (2560, 1440, None, None, 0.50, 0.62),
    "social_1280x640": (1280, 640, 0.22, None, 0.66, 0.9),
}

if __name__ == "__main__":
    if "--low" in sys.argv:
        sys.argv.remove("--low")
        SPECS = SPECS_LOW
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    master = Image.open(src).convert("RGB")
    for name, (w, h, top, fx, fy, size) in SPECS.items():
        plain = crop(master, w, h, top)
        plain.save(os.path.join(out, f"terrassic_{name}_sem_titulo.png"), optimize=True)
        if fx is not False:
            titled(plain, fx, fy, size).save(os.path.join(out, f"terrassic_{name}.png"), optimize=True)
        print(name, "ok")
