"""Builds the built-in era resource packs into common/src/main/resources/resourcepacks/<era>/ and preview sheets
into art/texpack/previews/.

usage: python3 build.py            -> writes the Late Cretaceous pack (the Overworld era) + previews
       python3 build.py --check    -> only runs the quality checks, writes nothing

The pack overrides vanilla textures (assets/minecraft/textures/block/<name>.png) and, for the big terrain blocks,
the vanilla blockstates, so every block of stone, dirt, sand and gravel picks one of several drawings and rotations
(no visible repetition). Extra drawings live in the pack under assets/terrassic/.../cretaceo/.
Batch 2 adds the eight woods (bark, rings, stripped, planks, with rare log variants: amber resin on spruce,
lichen on oak, moss on jungle), the leaves, the ground plants (horsetails and ferns), the crafting table, the
furnace and the torch. Batch 3 adds the vanilla rocks (granite, diorite, andesite, tuff, deepslate, calcite)
and the sixteen ores, in natural veins on the pack's own stone and deepslate, plus the chest. Batch 3b adds the
building and ground blocks (stone bricks, bricks, moss, farmland, path, hay, snow, sugar cane, lily pad);
batch 3c the twelve small flowers in early-angiosperm shapes; batch 3d the ground of the biomes (laterite sand, red
sandstone, terracotta, mud, roots, ice, flowstone, mycelium) and the fungi and undergrowth. The pack also carries the era filter (filters.py):
a post chain the mod draws over the world, a light warm and faded colour grade.
The pack name and description are lang keys of the mod (pack.terrassic.<era>), so they read in all three languages.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cretaceo as C  # noqa: E402
import filters as FX  # noqa: E402
import preview as P  # noqa: E402
import leaves as LV  # noqa: E402
import plants as PL  # noqa: E402
import flowers as FL  # noqa: E402
import fungi as FG  # noqa: E402
import masonry as MS  # noqa: E402
import rocks as RK  # noqa: E402
import terrain as TR  # noqa: E402
import tex as T  # noqa: E402
import woods as WD  # noqa: E402
import workshop as WS  # noqa: E402
from targets import TARGETS, measure  # noqa: E402
from vanilla import VANILLA  # noqa: E402

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

# batch 2: woods, leaves, plants, workshop
LOG_VARIANTS = {"spruce_log": ("spruce_log_resin", 1, 5), "oak_log": ("oak_log_lichen", 1, 3),
                "jungle_log": ("jungle_log_moss", 1, 2)}   # log: (extra drawing, its weight, plain weight)
_variant_names = {v[0] for v in LOG_VARIANTS.values()}
for _name, _img in WD.ALL.items():
    if _name not in _variant_names:
        CRETACEO[_name] = (_img, not _name.endswith("_top"))
for _name, _img in list(LV.ALL.items()) + list(PL.ALL.items()) + list(WS.ALL.items()):
    CRETACEO[_name] = (_img, False)
# batch 3: rocks and ores
for _name, _img in RK.ALL.items():
    CRETACEO[_name] = (_img, True)
# batch 3c: flowers (cutouts)
for _name, _img in FL.ALL.items():
    CRETACEO[_name] = (_img, False)
# batch 3b: building and ground (cutouts and the path side are not seamless tiles)
for _name, _img in MS.ALL.items():
    CRETACEO[_name] = (_img, _name not in ("sugar_cane", "lily_pad", "dirt_path_side", "chiseled_stone_bricks"))
# batch 3d: the ground of the biomes (sands, terracotta, mud, roots, ice) and fungi and undergrowth
NOT_TILES = {"red_sandstone", "cut_red_sandstone", "chiseled_red_sandstone", "mycelium_side", "mangrove_roots_side",
             "mangrove_roots_top", "ice"}  # banded sides like the yellow sandstone; cutouts; see-through ice
for _name, _img in TR.ALL.items():
    CRETACEO[_name] = (_img, _name not in NOT_TILES)
for _name, _img in FG.ALL.items():
    CRETACEO[_name] = (_img, _name.endswith("_block") or _name in ("mushroom_stem", "mushroom_block_inside"))

# entity textures (64x64 atlases): path under assets/minecraft/textures/ -> image
CRETACEO_ENTITY = {f"entity/chest/{k}": v for k, v in WS.CHESTS.items()}

# extra drawings used by the weighted blockstates: name -> image
CRETACEO_EXTRA = {
    "stone_2": C.stone(5),
    "stone_3": C.stone(8),
    "stone_fossil": C.stone_fossil(4),
    "dirt_2": C.dirt(4),
    "gravel_2": C.gravel(2),
    "sand_2": C.sand(2),
}
CRETACEO_EXTRA.update({v[0]: WD.ALL[v[0]] for v in LOG_VARIANTS.values()})


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


def log_blockstates(era):
    """Logs keep their axis; each axis picks the plain log or, now and then, the variant drawing."""
    out = {}
    for log, (var, w_var, w_plain) in LOG_VARIANTS.items():
        def pick(model_plain, model_var, **rot):
            return [dict(model=model_plain, weight=w_plain, **rot), dict(model=model_var, weight=w_var, **rot)]
        out[log] = {
            "axis=y": pick(f"minecraft:block/{log}", ext(era, var)),
            "axis=z": pick(f"minecraft:block/{log}_horizontal", ext(era, var + "_horizontal"), x=90),
            "axis=x": pick(f"minecraft:block/{log}_horizontal", ext(era, var + "_horizontal"), x=90, y=90),
        }
    return out


def models(era):
    out = {}
    for name in ("stone_2", "stone_3", "dirt_2", "gravel_2", "sand_2"):
        out[name] = {"parent": "minecraft:block/cube_all", "textures": {"all": ext(era, name)}}
    # the fossil shows on a single face; the other five are the normal stone
    s = "minecraft:block/stone"
    out["stone_fossil"] = {"parent": "minecraft:block/cube", "textures": {
        "particle": s, "down": s, "up": s, "north": ext(era, "stone_fossil"), "south": s, "east": s, "west": s}}
    for log, (var, _, _) in LOG_VARIANTS.items():
        tex = {"end": f"minecraft:block/{log}_top", "side": ext(era, var)}
        out[var] = {"parent": "minecraft:block/cube_column", "textures": tex}
        out[var + "_horizontal"] = {"parent": "minecraft:block/cube_column_horizontal", "textures": tex}
    return out


# ------------------------------------------------------------------ checks
def check(name, img, natural):
    """Seam, size and opacity, plus the distance to the vanilla block it replaces: luma mean within 14 and
    p95-p5 contrast within 20 (targets.py). Textures drawn on purpose away from vanilla go in OFF_TARGET."""
    m = measure(img)
    problems = []
    if natural and T.seam_score(img) > 2.0 and T.seam_excess(img) > 1.2:
        problems.append(f"seam {T.seam_score(img):.2f} (wrap {T.seam_excess(img):.2f}x the strongest inner line)")
    if img.size != (16, 16):
        problems.append(f"size {img.size}")
    if natural and np.asarray(img)[..., 3].min() < 255:
        problems.append("transparent pixels in an opaque block")
    ref = TARGETS.get(name) or VANILLA.get(name)
    if ref and name not in OFF_TARGET:
        lum, ctr = ref[:2]
        if abs(m["lum"] - lum) > 14:
            problems.append(f"luma {m['lum']:.0f} vs vanilla {lum:.0f}")
        if abs(m["ctr"] - ctr) > 20:
            problems.append(f"contrast {m['ctr']:.0f} vs vanilla {ctr:.0f}")
    return m, problems


# the turf strip of grass_block_side sits under the tinted overlay, so its own luma is never seen;
# the workshop faces are drawings (tools on wood, a lit kiln, a torch), judged by eye rather than by the numbers
# deep coal and iron: our deepslate holds fewer, smaller blebs than vanilla's big spots, by design
OFF_TARGET = {"grass_block_side", "crafting_table_side", "crafting_table_front", "furnace_front_on", "torch",
              "deepslate_coal_ore", "deepslate_iron_ore", "mycelium_side"} | set(FL.ALL)
# flowers are small drawings whose colour is their dye: judged by eye, like the workshop


def run_checks(table, extra):
    bad = []
    for name, (img, natural) in table.items():
        m, problems = check(name, img, natural)
        v = TARGETS.get(name) or VANILLA.get(name)
        ref = f"| vanilla luma {v[0]:5.1f} contrast {v[1]:5.1f} jump {v[2]:4.1f}" if v else ""
        print(f"  {name:26s} luma {m['lum']:5.1f} contrast {m['ctr']:5.1f} jump {m['nb']:4.1f} colours {m['colours']:2d} "
              f"{ref}  {'; '.join(problems)}")
        if problems:
            bad.append(name)
    for name, img in extra.items():
        _, problems = check(name, img, name != "stone_fossil")
        if name in _variant_names:
            _, problems = check(name.rsplit("_", 1)[0], img, True)
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
    """Writes only when the pixels changed: re-encoding an untouched PNG would show up as a change in git."""
    if os.path.exists(path):
        old = np.asarray(Image.open(path).convert("RGBA"))
        new = np.asarray(img.convert("RGBA"))
        if old.shape == new.shape and (old == new).all():
            return
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
    save_png(P.sheet(items, f"Terrassic: pacote {NAMES[era]} (texturas do vanilla redesenhadas)", cols=9), os.path.join(PREVIEWS, f"{era}_texturas.png"))
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
    save_png(P.diorama(blocks, S=48), os.path.join(PREVIEWS, f"{era}_diorama.png"))


FOLIAGE = {"oak": (119, 171, 47), "dark_oak": (119, 171, 47), "birch": (128, 167, 85), "spruce": (97, 153, 97),
           "jungle": (48, 187, 11), "acacia": (174, 164, 42), "mangrove": (141, 177, 39)}
GRASS_TINT = (121, 192, 90)
SKY = (150, 186, 226, 255)


def preview_batch2(era, table):
    tx = {k: v[0] for k, v in table.items()}
    gtop = P.tint(tx["grass_block_top"], GRASS_TINT)
    gside = P.over(tx["grass_block_side"], P.tint(tx["grass_block_side_overlay"], GRASS_TINT))
    woods = list(WD.WOODS)
    # woods sheet: bark, rings, stripped, stripped rings, planks for each wood
    rows = []
    for w in woods:
        rows += [(f"{w}_log", tx[f"{w}_log"]), (f"{w}_log_top", tx[f"{w}_log_top"]),
                 (f"stripped_{w}_log", tx[f"stripped_{w}_log"]), (f"stripped_{w}_log_top", tx[f"stripped_{w}_log_top"]),
                 (f"{w}_planks", tx[f"{w}_planks"])]
    rows += [(v[0], WD.ALL[v[0]]) for v in LOG_VARIANTS.values()]
    save_png(P.sheet(rows, f"Terrassic: pacote {NAMES[era]}, madeiras", cols=10), os.path.join(PREVIEWS, f"{era}_madeiras.png"))
    # one small tree of each wood on a patch of grass
    scenes = []
    for w in woods:
        lf = tx[f"{w}_leaves"]
        lf = P.tint(lf, FOLIAGE[w]) if w in FOLIAGE else lf
        lg, lt = tx[f"{w}_log"], tx[f"{w}_log_top"]
        b = {(x, 0, z): (gtop, gside, gside) for x in range(3) for z in range(3)}
        for y in range(1, 5):
            b[(1, y, 1)] = (lt, lg, lg)
        for y in (3, 4):
            for x in range(3):
                for z in range(3):
                    if (x, z) != (1, 1) and not (y == 4 and x != 1 and z != 1):
                        b[(x, y, z)] = (lf, lf, lf)
        b[(1, 5, 1)] = (lf, lf, lf)
        scenes.append((w, P.diorama_culled(b, S=32, bg=SKY)))
    save_png(P.sheet_images(scenes, f"Terrassic: pacote {NAMES[era]}, árvores", cols=4), os.path.join(PREVIEWS, f"{era}_arvores.png"))
    plants = ["grass", "fern", "tall_grass_top", "tall_grass_bottom", "large_fern_top", "large_fern_bottom", "vine",
              "dead_bush", "crafting_table_top", "crafting_table_side", "crafting_table_front", "furnace_top",
              "furnace_side", "furnace_front", "furnace_front_on", "torch"]
    tinted = {"grass", "fern", "tall_grass_top", "tall_grass_bottom", "large_fern_top", "large_fern_bottom"}
    items = [(n, P.tint(tx[n], GRASS_TINT) if n in tinted else P.tint(tx[n], FOLIAGE["oak"]) if n == "vine" else tx[n])
             for n in plants]
    save_png(P.sheet(items, f"Terrassic: pacote {NAMES[era]}, plantas e oficina", cols=8), os.path.join(PREVIEWS, f"{era}_plantas_oficina.png"))


def chest_preview():
    """The single chest as it stands in the world, assembled from its atlas (lid over base, top, front, side)."""
    c = np.asarray(WS.CHESTS["normal"])
    lid, base = WS._box_faces(14, 5, 14, 0, 0), WS._box_faces(14, 10, 14, 0, 19)

    def face(a, b):
        out = np.zeros((16, 16, 4), np.uint8)
        out[1:6, 1:15] = c[a[1]:a[3], a[0]:a[2]]
        out[6:16, 1:15] = c[b[1]:b[3], b[0]:b[2]]
        return Image.fromarray(out, "RGBA")

    top = np.zeros((16, 16, 4), np.uint8)
    top[1:15, 1:15] = c[0:14, 14:28]
    return P.cube(Image.fromarray(top, "RGBA"), face(lid["south"], base["south"]), face(lid["east"], base["east"]), S=64)


def preview_batch3(era, table):
    items = [(n, table[n][0]) for n in RK.ALL]
    save_png(P.sheet_images([("chest", chest_preview()), ("entity/chest/normal", P.big(WS.CHESTS["normal"], 2))],
                            f"Terrassic: pacote {NAMES[era]}, baú", cols=2), os.path.join(PREVIEWS, f"{era}_bau.png"))
    save_png(P.sheet(items, f"Terrassic: pacote {NAMES[era]}, rochas e minérios", cols=8), os.path.join(PREVIEWS, f"{era}_rochas_minerios.png"))
    tints = {"sugar_cane": GRASS_TINT, "lily_pad": (32, 128, 48)}
    items = [(n, P.tint(table[n][0], tints[n]) if n in tints else table[n][0]) for n in MS.ALL]
    save_png(P.sheet(items, f"Terrassic: pacote {NAMES[era]}, construção e chão", cols=8),
             os.path.join(PREVIEWS, f"{era}_construcao_chao.png"))
    meadow = []
    for n in FL.ALL:
        bg = Image.new("RGBA", (16, 16), (110, 150, 80, 255))
        bg.alpha_composite(table[n][0])
        meadow.append((n, bg))
    save_png(P.sheet(meadow, f"Terrassic: pacote {NAMES[era]}, flores", cols=6), os.path.join(PREVIEWS, f"{era}_flores.png"))


def preview_batch3d(era, table):
    tx = {k: v[0] for k, v in table.items()}
    save_png(P.sheet([(n, tx[n]) for n in TR.ALL], f"Terrassic: pacote {NAMES[era]}, terreno dos biomas", cols=8),
             os.path.join(PREVIEWS, f"{era}_terreno.png"))
    items = []
    for n in FG.ALL:
        bg = Image.new("RGBA", (16, 16), (110, 150, 80, 255))
        bg.alpha_composite(tx[n])
        items.append((n, bg))
    save_png(P.sheet(items, f"Terrassic: pacote {NAMES[era]}, fungos e arbustos", cols=6),
             os.path.join(PREVIEWS, f"{era}_fungos.png"))
    # three small landscapes: a badland mesa, a mangrove shore, an ice field
    gtop = P.tint(tx["grass_block_top"], GRASS_TINT)
    gside = P.over(tx["grass_block_side"], P.tint(tx["grass_block_side_overlay"], GRASS_TINT))
    strata = ["terracotta", "orange_terracotta", "yellow_terracotta", "white_terracotta", "red_terracotta",
              "brown_terracotta", "light_gray_terracotta"]
    mesa = {}
    for x in range(4):
        for z in range(4):
            mesa[(x, 0, z)] = (tx["red_sand"],) * 3
    for x in range(2):
        for z in range(2):
            for y in range(1, 6 - x - z):
                c = tx[strata[y % len(strata)]]
                mesa[(x, y, z)] = (c, c, c)
    mesa[(3, 1, 3)] = (tx["red_sandstone_top"], tx["red_sandstone"], tx["red_sandstone"])
    mesa[(2, 1, 3)] = (tx["red_sandstone_top"], tx["chiseled_red_sandstone"], tx["chiseled_red_sandstone"])
    shore = {}
    for x in range(4):
        for z in range(4):
            shore[(x, 0, z)] = (tx["mud"],) * 3 if x + z > 2 else (gtop, gside, gside)
    shore[(2, 1, 2)] = (tx["muddy_mangrove_roots_top"], tx["muddy_mangrove_roots_side"], tx["muddy_mangrove_roots_side"])
    shore[(3, 1, 2)] = (tx["mangrove_roots_top"], tx["mangrove_roots_side"], tx["mangrove_roots_side"])
    shore[(3, 1, 3)] = (tx["packed_mud"],) * 3
    shore[(3, 2, 3)] = (tx["mud_bricks"],) * 3
    shore[(0, 1, 0)] = (tx["mycelium_top"], tx["mycelium_side"], tx["mycelium_side"])
    shore[(1, 1, 0)] = (tx["red_mushroom_block"],) * 3
    shore[(0, 1, 1)] = (tx["mushroom_stem"],) * 3
    shore[(0, 2, 1)] = (tx["brown_mushroom_block"],) * 3
    field = {}
    for x in range(4):
        for z in range(4):
            field[(x, 0, z)] = (tx["packed_ice"],) * 3 if (x + z) % 3 else (tx["blue_ice"],) * 3
    field[(1, 1, 1)] = (tx["powder_snow"],) * 3
    field[(2, 1, 1)] = (tx["snow"],) * 3
    field[(3, 1, 3)] = (tx["dripstone_block"],) * 3
    field[(3, 2, 3)] = (tx["dripstone_block"],) * 3
    scenes = [("mesa", P.diorama_culled(mesa, S=32, bg=SKY)), ("manguezal", P.diorama_culled(shore, S=32, bg=SKY)),
              ("gelo", P.diorama_culled(field, S=32, bg=SKY))]
    save_png(P.sheet_images(scenes, f"Terrassic: pacote {NAMES[era]}, paisagens", cols=3),
             os.path.join(PREVIEWS, f"{era}_paisagens.png"))


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def write_filter(era, root):
    program = os.path.join(root, "assets", "minecraft", "shaders", "program", FX.PROGRAM)
    write_json(program + ".json", FX.program())
    write_text(program + ".fsh", FX.FRAGMENT)
    write_json(os.path.join(root, "assets", "terrassic", "shaders", "post", f"era_{era}.json"), FX.post_chain(era))


def preview_filter(era):
    """The tree scenes and the diorama without and with the era filter, as the game grades the whole screen."""
    items = []
    for name in (f"{era}_arvores.png", f"{era}_diorama.png"):
        img = Image.open(os.path.join(PREVIEWS, name)).convert("RGBA")
        items += [(f"{name[:-4]} sem filtro", img), (f"{name[:-4]} com filtro", FX.grade(img, era))]
    save_png(P.sheet_images(items, f"Terrassic: pacote {NAMES[era]}, filtro de era", cols=2),
             os.path.join(PREVIEWS, f"{era}_filtro.png"))


def build(era, table, extra):
    root = os.path.join(PACKS, era)
    write_json(os.path.join(root, "pack.mcmeta"), {
        "pack": {"pack_format": PACK_FORMAT, "description": {"translate": f"pack.terrassic.{era}.description"}}})
    save_png(pack_icon(table), os.path.join(root, "pack.png"))
    for name, (img, _) in table.items():
        save_png(img, os.path.join(root, "assets", "minecraft", "textures", "block", f"{name}.png"))
    for name, img in extra.items():
        save_png(img, os.path.join(root, "assets", "terrassic", "textures", "block", era, f"{name}.png"))
    for path, img in CRETACEO_ENTITY.items():
        save_png(img, os.path.join(root, "assets", "minecraft", "textures", *path.split("/")) + ".png")
    for block, entries in blockstates(era).items():
        write_json(os.path.join(root, "assets", "minecraft", "blockstates", f"{block}.json"), {"variants": {"": entries}})
    for block, variants in log_blockstates(era).items():
        write_json(os.path.join(root, "assets", "minecraft", "blockstates", f"{block}.json"), {"variants": variants})
    for name, model in models(era).items():
        write_json(os.path.join(root, "assets", "terrassic", "models", "block", era, f"{name}.json"), model)
    write_filter(era, root)
    os.makedirs(PREVIEWS, exist_ok=True)
    preview(era, table, extra)
    preview_batch2(era, table)
    preview_batch3(era, table)
    preview_batch3d(era, table)
    preview_filter(era)


if __name__ == "__main__":
    print("cretaceo:")
    run_checks(CRETACEO, CRETACEO_EXTRA)
    if "--check" not in sys.argv:
        build("cretaceo", CRETACEO, CRETACEO_EXTRA)
        print(f"wrote {os.path.join(PACKS, 'cretaceo')} and previews in {PREVIEWS}")
