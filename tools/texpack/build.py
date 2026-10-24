"""Builds the built-in era resource packs into common/src/main/resources/resourcepacks/<era>/ and preview sheets
into art/texpack/previews/.

usage: python3 build.py            -> writes the Late Cretaceous pack (the Overworld era) + previews
       python3 build.py --check    -> only runs the quality checks, writes nothing

The pack overrides vanilla textures (assets/minecraft/textures/block/<name>.png) and, for the big terrain blocks,
the vanilla blockstates, so every block of stone, dirt, sand and gravel picks one of several drawings and rotations
(no visible repetition). Extra drawings live in the pack under assets/terrassic/.../cretaceo/.
The pack name and description are lang keys of the mod (pack.terrassic.<era>), so they read in all three languages.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cretaceo as C  # noqa: E402
import preview as P  # noqa: E402
import tex as T  # noqa: E402
from targets import TARGETS, measure  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PACKS = os.path.join(ROOT, "common", "src", "main", "resources", "resourcepacks")
PREVIEWS = os.path.join(ROOT, "art", "texpack", "previews")
PACK_FORMAT = 15  # Minecraft 1.20.1
NAMES = {"cretaceo": "Cretáceo Superior"}

# vanilla texture name -> (drawing, natural). natural = a material that must tile seamlessly.
GRASS_SIDE, GRASS_OVERLAY = C.grass_side(3, 1)
CRETACEO = {
    "stone": (C.stone(4), True),
    "cobblestone": (C.cobblestone(1), True),
    "mossy_cobblestone": (C.mossy_cobblestone(1), True),
    "dirt": (C.dirt(1), True),
    "coarse_dirt": (C.coarse_dirt(7), True),
    "rooted_dirt": (C.rooted_dirt(5), True),
    "grass_block_top": (C.grass_top(1), True),
    "grass_block_side": (GRASS_SIDE, False),
    "grass_block_side_overlay": (GRASS_OVERLAY, False),
    "grass_block_snow": (C.snow_side(5, 1), False),
    "podzol_top": (C.podzol_top(1), True),
    "podzol_side": (C.podzol_side(3, 1), False),
    "gravel": (C.gravel(1), True),
    "sand": (C.sand(1), True),
    "sandstone": (C.sandstone_side(1), False),
    "sandstone_top": (C.sandstone_top(1), True),
    "sandstone_bottom": (C.sandstone_bottom(2), True),
    "cut_sandstone": (C.cut_sandstone(1), False),
    "chiseled_sandstone": (C.chiseled_sandstone(1), False),
    "clay": (C.clay(1), True),
    "mud": (C.mud(1), True),
}

# extra drawings used by the weighted blockstates: name -> image
CRETACEO_EXTRA = {
    "stone_2": C.stone(5),
    "stone_3": C.stone(8),
    "stone_fossil": C.stone_fossil(4),
    "dirt_2": C.dirt(4),
    "gravel_2": C.gravel(2),
    "sand_2": C.sand(2),
}


def ext(era, name):
    return f"terrassic:block/{era}/{name}"


def rotations(model, weight, ys=(0, 90, 180, 270)):
    out = []
    for y in ys:
        e = {"model": model, "weight": weight}
        if y:
            e["y"] = y
        out.append(e)
    return out


def blockstates(era):
    """Weighted blockstates: the vanilla drawing stays the most common one, the extras break the repetition.
    The ammonite shows on one face of about 1 stone block in 90."""
    return {
        "stone": rotations("minecraft:block/stone", 25, (0, 180))
        + rotations("minecraft:block/stone_mirrored", 25, (0, 180))
        + rotations(ext(era, "stone_2"), 10)
        + rotations(ext(era, "stone_3"), 10)
        + rotations(ext(era, "stone_fossil"), 1, (0, 180)),
        "dirt": rotations("minecraft:block/dirt", 3) + rotations(ext(era, "dirt_2"), 2),
        "sand": rotations("minecraft:block/sand", 3) + rotations(ext(era, "sand_2"), 2),
        "gravel": rotations("minecraft:block/gravel", 3) + rotations(ext(era, "gravel_2"), 2),
    }


def models(era):
    out = {}
    for name in ("stone_2", "stone_3", "dirt_2", "gravel_2", "sand_2"):
        out[name] = {"parent": "minecraft:block/cube_all", "textures": {"all": ext(era, name)}}
    # the fossil shows on a single face; the other five are the normal stone
    s = "minecraft:block/stone"
    out["stone_fossil"] = {"parent": "minecraft:block/cube", "textures": {
        "particle": s, "down": s, "up": s, "north": ext(era, "stone_fossil"), "south": s, "east": s, "west": s}}
    return out


# ------------------------------------------------------------------ checks
def check(name, img, natural):
    """Seam, size and opacity, plus the distance to the vanilla block it replaces: luma mean within 14 and
    p95-p5 contrast within 20 (targets.py). Textures drawn on purpose away from vanilla go in OFF_TARGET."""
    m = measure(img)
    problems = []
    if natural and T.seam_score(img) > 2.0:
        problems.append(f"seam {T.seam_score(img):.2f}")
    if img.size != (16, 16):
        problems.append(f"size {img.size}")
    if natural and np.asarray(img)[..., 3].min() < 255:
        problems.append("transparent pixels in an opaque block")
    if name in TARGETS and name not in OFF_TARGET:
        lum, ctr, nb, _ = TARGETS[name]
        if abs(m["lum"] - lum) > 14:
            problems.append(f"luma {m['lum']:.0f} vs vanilla {lum:.0f}")
        if abs(m["ctr"] - ctr) > 20:
            problems.append(f"contrast {m['ctr']:.0f} vs vanilla {ctr:.0f}")
    return m, problems


# the turf strip of grass_block_side sits under the tinted overlay, so its own luma is never seen
OFF_TARGET = {"grass_block_side"}


def run_checks(table, extra):
    bad = []
    for name, (img, natural) in table.items():
        m, problems = check(name, img, natural)
        v = TARGETS.get(name)
        ref = f"| vanilla luma {v[0]:5.1f} contrast {v[1]:5.1f} jump {v[2]:4.1f}" if v else ""
        print(f"  {name:26s} luma {m['lum']:5.1f} contrast {m['ctr']:5.1f} jump {m['nb']:4.1f} colours {m['colours']:2d} "
              f"{ref}  {'; '.join(problems)}")
        if problems:
            bad.append(name)
    for name, img in extra.items():
        _, problems = check(name, img, name != "stone_fossil")
        if problems:
            bad.append(name)
    if bad:
        raise SystemExit(f"quality check failed: {bad}")


# ------------------------------------------------------------------ output
def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def save_png(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, optimize=True)


def pack_icon(table):
    """128x128 pack.png: a little isometric patch of the pack's own blocks on a dusk-amber sky."""
    g = (142, 170, 82)
    top = P.tint(table["grass_block_top"][0], g)
    side = P.over(table["grass_block_side"][0], P.tint(table["grass_block_side_overlay"][0], g))
    d = table["dirt"][0]
    st = table["stone"][0]
    sa = table["sand"][0]
    cb = table["mossy_cobblestone"][0]
    blocks = {}
    for x in range(3):
        for z in range(3):
            h = 2 if (x, z) != (0, 0) else 3
            for y in range(h):
                if (x, z) == (2, 2) or (x, z) == (2, 1):
                    f = (sa, sa, sa)
                elif (x, z) == (0, 0):
                    f = (st, st, st)
                else:
                    f = (top, side, side) if y == h - 1 else (d, d, d)
                blocks[(x, y, z)] = f
    blocks[(1, 2, 0)] = (cb, cb, cb)
    dio = P.diorama(blocks, S=16, pad=4)
    sky = np.zeros((128, 128, 4))
    for y in range(128):
        t = y / 127
        sky[y, :, :3] = np.array([52, 40, 58]) * (1 - t) + np.array([196, 126, 64]) * t
    sky[..., 3] = 255
    icon = Image.fromarray(sky.astype(np.uint8), "RGBA")
    arr = np.asarray(dio).copy()
    bg = np.all(arr[..., :3] == np.array(P.BG[:3]), axis=2)
    arr[bg, 3] = 0
    dio = Image.fromarray(arr, "RGBA")
    dio.thumbnail((124, 124), Image.NEAREST)
    icon.alpha_composite(dio, ((128 - dio.width) // 2, (128 - dio.height) // 2 + 6))
    return icon


def preview(era, table, extra):
    items = [(name, img) for name, (img, _) in table.items()] + list(extra.items())
    P.sheet(items, f"Terrassic: pacote {NAMES[era]} (texturas do vanilla redesenhadas)", cols=9).save(
        os.path.join(PREVIEWS, f"{era}_texturas.png"))
    g = (142, 170, 82)
    top = P.tint(table["grass_block_top"][0], g)
    side = P.over(table["grass_block_side"][0], P.tint(table["grass_block_side_overlay"][0], g))
    tx = {k: v[0] for k, v in table.items()}
    d, sa, gr = tx["dirt"], tx["sand"], tx["gravel"]
    stn = [tx["stone"], extra["stone_2"], extra["stone_3"]]
    blocks = {}
    for x in range(10):
        for z in range(10):
            h = 2 + (1 if x + z > 10 else 0) + (1 if (x > 6 and z < 4) else 0)
            for y in range(h):
                topb = y == h - 1
                if x < 2 and z > 4:
                    f = (sa, sa, sa) if (x + z) % 3 else (extra["sand_2"],) * 3
                elif z == 5 and x >= 2:
                    f = (gr, d, d) if topb else (d, d, d)
                elif x > 6 and z < 4:
                    s = stn[(x * 7 + z * 3 + y) % 3]
                    f = (s, s, s) if y >= 1 else (d, d, d)
                elif x < 3 and z < 3:
                    f = (tx["podzol_top"], tx["podzol_side"], tx["podzol_side"]) if topb else (d, d, d)
                elif x == 6 and z == 8:
                    f = (tx["mud"],) * 3 if topb else (d, d, d)
                else:
                    f = (top, side, side) if topb else (d, d, d)
                blocks[(x, y, z)] = f
    ss = (tx["sandstone_top"], tx["sandstone"], tx["sandstone"])
    blocks[(3, 4, 8)] = ss
    blocks[(3, 5, 8)] = ss
    blocks[(4, 4, 8)] = (tx["sandstone_top"], tx["cut_sandstone"], tx["cut_sandstone"])
    blocks[(5, 4, 8)] = (tx["sandstone_top"], tx["chiseled_sandstone"], tx["chiseled_sandstone"])
    blocks[(6, 4, 7)] = (tx["cobblestone"],) * 3
    blocks[(7, 4, 7)] = (tx["mossy_cobblestone"],) * 3
    blocks[(6, 5, 7)] = (tx["mossy_cobblestone"],) * 3
    blocks[(2, 3, 1)] = (tx["coarse_dirt"],) * 3
    blocks[(1, 3, 1)] = (tx["clay"],) * 3
    blocks[(7, 4, 9)] = (tx["rooted_dirt"],) * 3
    blocks[(8, 5, 2)] = (stn[0], stn[0], extra["stone_fossil"])
    P.diorama(blocks, S=48).save(os.path.join(PREVIEWS, f"{era}_diorama.png"))


def build(era, table, extra):
    root = os.path.join(PACKS, era)
    write_json(os.path.join(root, "pack.mcmeta"), {
        "pack": {"pack_format": PACK_FORMAT, "description": {"translate": f"pack.terrassic.{era}.description"}}})
    save_png(pack_icon(table), os.path.join(root, "pack.png"))
    for name, (img, _) in table.items():
        save_png(img, os.path.join(root, "assets", "minecraft", "textures", "block", f"{name}.png"))
    for name, img in extra.items():
        save_png(img, os.path.join(root, "assets", "terrassic", "textures", "block", era, f"{name}.png"))
    for block, entries in blockstates(era).items():
        write_json(os.path.join(root, "assets", "minecraft", "blockstates", f"{block}.json"), {"variants": {"": entries}})
    for name, model in models(era).items():
        write_json(os.path.join(root, "assets", "terrassic", "models", "block", era, f"{name}.json"), model)
    os.makedirs(PREVIEWS, exist_ok=True)
    preview(era, table, extra)


if __name__ == "__main__":
    print("cretaceo:")
    run_checks(CRETACEO, CRETACEO_EXTRA)
    if "--check" not in sys.argv:
        build("cretaceo", CRETACEO, CRETACEO_EXTRA)
        print(f"wrote {os.path.join(PACKS, 'cretaceo')} and previews in {PREVIEWS}")
