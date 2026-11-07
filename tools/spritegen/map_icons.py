#!/usr/bin/env python3
"""Map icons (1.9.6): every species' face on the minimaps and world maps, drawn from its own model.

The four map mods that show mobs read the icon from the game's resources, so these are only files in our jar: no
code, no dependency (docs/MINIMAPA.md). Each icon is the species' head rendered from its exported geo.json (what
GeckoLib draws) with the male skin, point-sampled so the texels stay crisp, a dark one-pixel outline round it:
  32 x 32 master (Xaero, drawn in the middle of a 64 x 64 frame), 16 x 16 for the others, reduced from the 32 keeping
  the pixel of most contrast of each 2 x 2 (the eye, the teeth, a horn) instead of averaging them away.
It is not the spawn egg: it is the animal's face.

    uv run -q --with numpy --with pillow python3 tools/spritegen/map_icons.py [--sheet out.png]
"""
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path[:0] = [os.path.join(ROOT, "tools", "modelgen", "handmade", "_engine"), os.path.join(ROOT, "tools", "javagen")]
import geo  # noqa: E402
import gen_species  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets")
TERR = os.path.join(ASSETS, "terrassic")
KEY = (255, 0, 255)
OUTLINE = (28, 24, 20, 255)
ALPHAS = {"tyrannosaurus"}          # species with alpha skins (entity/Alphas.SPECIES): JourneyMap 5 keys the icon on them

# the view of the head: yaw (0 = from the front, 90 = from the side), pitch (from above). Three quarters by default;
# long beaks and snouts from more in front and above, so they do not shrink to a stick
VIEW = {"default": (55, 18)}
for sp in ("quetzalcoatlus", "pteranodon", "hatzegopteryx", "ichthyornis", "elasmosaurus", "deinosuchus", "baurusuchus",
           "lepisosteus", "xiphactinus", "enchodus", "spinosaurus", "mosasaurus", "tylosaurus"):
    VIEW[sp] = (30, 32)


def _head_spec(spec):
    kids = {}
    for b in spec["bones"]:
        kids.setdefault(b["parent"], []).append(b["name"])
    names, i = ["head"], 0
    while i < len(names):
        names += kids.get(names[i], [])
        i += 1
    keep = set(names)
    return dict(spec, cubes=[c for c in spec["cubes"] if c["bone"] in keep])


def _outline(rgba):
    al = rgba[..., 3] > 0
    ring = np.zeros_like(al)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ring |= np.roll(np.roll(al, dy, 0), dx, 1)
    ring &= ~al
    rgba[ring] = OUTLINE
    return rgba


def master(sp, px=32):
    """the 32 x 32 face (outline included)"""
    spec = geo.load_geo(os.path.join(TERR, "geo", "entity", f"{sp}.geo.json"))
    tex = Image.open(os.path.join(TERR, "textures", "entity", f"{sp}_male.png"))
    yaw, pitch = VIEW.get(sp, VIEW["default"])
    inner = px - 2
    im, _, _ = geo.render(_head_spec(spec), tex, yaw=yaw, pitch=pitch, size=(inner, inner), bg=KEY, margin=0.02)
    a = np.asarray(im).astype(int)
    solid = ~((abs(a[..., 0] - 255) < 10) & (a[..., 1] < 10) & (abs(a[..., 2] - 255) < 10))
    out = np.zeros((px, px, 4), np.uint8)
    out[1:1 + inner, 1:1 + inner, :3] = a
    out[1:1 + inner, 1:1 + inner, 3] = solid * 255
    return _outline(out)


def small(m32):
    """16 x 16 from the 32: each 2 x 2 keeps its most contrasting pixel when it stands out (eye, teeth), else the one
    nearest the block's mean; opaque when at least two of the four are"""
    body = m32.copy()
    body[(body[..., :3] == OUTLINE[:3]).all(-1)] = 0       # the outline is redrawn at 16
    out = np.zeros((16, 16, 4), np.uint8)
    for y in range(16):
        for x in range(16):
            blk = body[2 * y:2 * y + 2, 2 * x:2 * x + 2].reshape(4, 4)
            op = blk[blk[:, 3] > 0]
            if len(op) < 2:
                continue
            rgb = op[:, :3].astype(float)
            mean = rgb.mean(0)
            dist = np.abs(rgb - mean).sum(1)
            pick = op[int(dist.argmax())] if dist.max() > 90 else op[int(dist.argmin())]
            out[y, x] = (*pick[:3], 255)
    return _outline(out)


def write(path, img):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(img, "RGBA").save(path)


def main():
    sheet = None
    if "--sheet" in sys.argv:
        sheet = sys.argv[sys.argv.index("--sheet") + 1]
    tiles = []
    for d in gen_species.SPECIES:
        sp, cls = d["id"], d["cls"]
        m32 = master(sp)
        s16 = small(m32)
        frame = np.zeros((64, 64, 4), np.uint8)
        frame[16:48, 16:48] = m32
        # Xaero's Minimap / World Map: a definition and its sprite
        write(os.path.join(ASSETS, "xaerominimap", "entity", "icon", "sprite", "terrassic", f"{sp}.png"), frame)
        dfn = os.path.join(ASSETS, "xaerominimap", "entity", "icon", "definition", "terrassic", f"{sp}.json")
        os.makedirs(os.path.dirname(dfn), exist_ok=True)
        with open(dfn, "w") as f:
            json.dump({"variants": {"default": f"outlined_sprite:terrassic/{sp}.png"}}, f, indent=2)
            f.write("\n")
        # JourneyMap 6, and 5.x (its icon follows the skin's path: one per sex, per alpha skin)
        write(os.path.join(ASSETS, "journeymap", "icon", "entity", "terrassic", f"{sp}.png"), s16)
        skins = ["_male", "_female"] + (["_alpha_male", "_alpha_female"] if sp in ALPHAS else [])
        for skin in skins:
            write(os.path.join(TERR, "textures", "entity_icon", f"{sp}{skin}.png"), s16)
        # FTB Chunks (1.20.1 and 1.21.1 up to 2101.1.10) and FTB Library (FTB Chunks 2101.1.11+)
        write(os.path.join(ASSETS, "ftbchunks", "textures", "faces", "terrassic", f"{sp}.png"), s16)
        write(os.path.join(ASSETS, "ftblibrary", "textures", "faces", "terrassic", f"{sp}.png"), s16)
        # VoxelMap: by the entity class' full name in lower case
        write(os.path.join(ASSETS, "minecraft", "textures", "icons", f"com.terrassic.entity.{cls.lower()}16.png"), s16)
        tiles.append((sp, m32, s16))
    print(f"map icons: {len(tiles)} species")
    if sheet:
        cell = 112
        o = Image.new("RGBA", (cell * 2 * 10, cell * ((len(tiles) + 9) // 10)), (96, 132, 78, 255))
        for i, (sp, m32, s16) in enumerate(tiles):
            x, y = (i % 10) * cell * 2, (i // 10) * cell
            o.alpha_composite(Image.fromarray(m32, "RGBA").resize((cell - 8, cell - 8), Image.NEAREST), (x + 4, y + 4))
            o.alpha_composite(Image.fromarray(s16, "RGBA").resize((cell - 8, cell - 8), Image.NEAREST), (x + cell + 4, y + 4))
        o.save(sheet)


if __name__ == "__main__":
    main()
