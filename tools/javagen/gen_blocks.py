"""Generates everything for the primitive building blocks from one table (BLOCKS, one row per block):
block/item models, blockstates, loot tables, recipes (crafting + stonecutter), block/item tags, rock worldgen
features, the lang entries (exported in LANG and merged by gen_resources.py, which also runs this script) and the
Java registration list common/src/main/java/com/terrassic/registry/BuildingBlocks.java.

To add blocks: add a family below (or a row with add()), draw the textures in tools/spritegen/blocks.py, then run
  python3 tools/spritegen/blocks.py && python3 tools/javagen/gen_resources.py
Never edit BuildingBlocks.java or the generated JSON by hand.

Catalog and phases: the "Terrassic - Catalogo de blocos primitivos" doc (336 blocks).  Rules: realistic,
prehistoric materials only, and never a copy of a vanilla block."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from gen_resources import A, D, ROOT, write  # noqa: E402

NS = "terrassic"
JAVA = os.path.join(ROOT, "common", "src", "main", "java", "com", "terrassic", "registry", "BuildingBlocks.java")

# kinds: cube | column | stairs | slab | wall | fence | pane | carpet | palisade
# material (Java ModBlocks.material): stone | soft_stone | hard_stone | pebbles | thatch | mud | wood | bone | hide
BLOCKS = {}


def add(bid, names, kind, tex, tool, material, color, base=None):
    """names = (en, pt, es); tex = texture name, or a tuple (side, end) / (pane, edge); base = full block of a
    stairs/slab (its model is the double slab, its state the stairs' base)."""
    BLOCKS[bid] = {"names": names, "kind": kind, "tex": tex, "tool": tool, "material": material,
                   "color": color, "base": base}


def add_shapes(bid, names, tex, tool, material, color, shapes):
    """A full block plus its stairs / slab / wall, named like vanilla in each language."""
    en, pt, es = names
    add(bid, names, "cube", tex, tool, material, color)
    if "stairs" in shapes:
        add(f"{bid}_stairs", (f"{en} Stairs", f"Escada de {pt}", f"Escaleras de {es}"), "stairs", (tex, tex), tool, material, color, bid)
    if "slab" in shapes:
        add(f"{bid}_slab", (f"{en} Slab", f"Laje de {pt}", f"Losa de {es}"), "slab", (tex, tex), tool, material, color, bid)
    if "wall" in shapes:
        add(f"{bid}_wall", (f"{en} Wall", f"Muro de {pt}", f"Muro de {es}"), "wall", tex, tool, material, color, bid)


# ------------------------------------------------------------- family: thatch, fibres, earth, bone, hide (batch 1)
add("thatch", ("Thatch", "Palha", "Paja"), "column", ("thatch", "thatch_top"), "hoe", "thatch", "COLOR_YELLOW")
add("thatch_stairs", ("Thatch Stairs", "Escada de Palha", "Escaleras de Paja"), "stairs", ("thatch", "thatch_top"), "hoe", "thatch", "COLOR_YELLOW", "thatch")
add("thatch_slab", ("Thatch Slab", "Laje de Palha", "Losa de Paja"), "slab", ("thatch", "thatch_top"), "hoe", "thatch", "COLOR_YELLOW", "thatch")
add("straw_mat", ("Straw Mat", "Esteira de Palha", "Estera de Paja"), "carpet", "straw_mat", "hoe", "thatch", "COLOR_YELLOW")
add("wattle_and_daub", ("Wattle and Daub", "Pau a Pique", "Bahareque"), "cube", "wattle_and_daub", "axe", "mud", "DIRT")
add("log_palisade", ("Log Palisade", "Paliçada de Troncos", "Empalizada de Troncos"), "palisade", ("log_palisade", "log_palisade_top"), "axe", "wood", "PODZOL")
add("bone_fence", ("Bone Fence", "Cerca de Osso", "Valla de Hueso"), "fence", "bone_fence", "pickaxe", "bone", "SAND")
add("hide_screen", ("Hide Screen", "Painel de Couro", "Panel de Cuero"), "pane", ("hide_screen", "hide_screen_edge"), "axe", "hide", "COLOR_BROWN")

# ------------------------------------------------------------- family: rocks (phase 1 and 2)
# rock id: natural block names, stem names used by the variants, Spanish adjective ending (a/o), material, map colour,
#          worldgen vein (size, veins per chunk, min y, max y, replaces: "stone" or another rock id, biome tag)
OVERWORLD = "minecraft:is_overworld"
ROCKS = {
    "limestone": (("Limestone", "Calcário", "Caliza"), ("Limestone", "Calcário", "Caliza"), "a", "stone", "SAND",
                  (56, 3, 0, 120, "stone", OVERWORLD)),
    "shale": (("Shale", "Folhelho", "Lutita"), ("Shale", "Folhelho", "Lutita"), "a", "soft_stone", "DEEPSLATE",
              (48, 3, -16, 60, "stone", OVERWORLD)),
    "chalk": (("Chalk", "Giz", "Creta"), ("Chalk", "Giz", "Creta"), "a", "soft_stone", "QUARTZ",
              (56, 2, 40, 140, "stone", OVERWORLD)),
    "flint": (("Flint Nodules", "Nódulos de Sílex", "Nódulos de Sílex"), ("Flint", "Sílex", "Sílex"), "o", "hard_stone",
              "TERRACOTTA_WHITE", (10, 10, 40, 140, "chalk", OVERWORLD)),
    "laterite": (("Laterite", "Laterita", "Laterita"), ("Laterite", "Laterita", "Laterita"), "a", "stone",
                 "TERRACOTTA_RED", (64, 6, 40, 120, "stone", "minecraft:is_savanna")),
    "quartzite": (("Quartzite", "Quartzito", "Cuarcita"), ("Quartzite", "Quartzito", "Cuarcita"), "a", "hard_stone",
                  "TERRACOTTA_PINK", (56, 5, 60, 220, "stone", "minecraft:is_mountain")),
    "gneiss": (("Gneiss", "Gnaisse", "Gneis"), ("Gneiss", "Gnaisse", "Gneis"), "o", "hard_stone", "STONE",
               (56, 2, -48, 40, "stone", OVERWORLD)),
    "conglomerate": (("Conglomerate", "Conglomerado", "Conglomerado"), ("Conglomerate", "Conglomerado", "Conglomerado"),
                     "o", "stone", "TERRACOTTA_BROWN", (40, 2, 0, 80, "stone", OVERWORLD)),
}
# loose pebbles on the surface: rock -> biome tags where small patches of them lie around
PEBBLE_PATCHES = {
    "limestone": ("minecraft:is_beach",), "flint": ("minecraft:is_beach",), "quartzite": ("minecraft:is_river",),
    "gneiss": ("minecraft:is_river",), "conglomerate": ("minecraft:is_river",), "laterite": ("minecraft:is_savanna",),
}
ROCK_VARIANTS = {}  # rock id -> {variant: block id}
for rid, (base_names, (sen, spt, ses), g, mat, color, _) in ROCKS.items():
    natural = rid if rid != "flint" else "flint_nodules"
    add(natural, base_names, "cube", rid, "pickaxe", mat, color)
    stacked = (f"Stacked {sen}", f"{spt} Empilhado", f"{ses} Apilad{g}")
    add_shapes(f"{rid}_stacked", stacked, f"{rid}_stacked", "pickaxe", mat, color, ("stairs", "slab", "wall"))
    add_shapes(f"{rid}_flagstone", (f"{sen} Flagstones", f"Lajeado de {spt}", f"Enlosado de {ses}"),
               f"{rid}_flagstone", "pickaxe", mat, color, ("stairs", "slab"))
    add_shapes(f"mossy_{rid}_stacked", (f"Mossy {stacked[0]}", f"{stacked[1]} com Musgo", f"{stacked[2]} con Musgo"),
               f"mossy_{rid}_stacked", "pickaxe", mat, color, ("stairs", "slab", "wall"))
    ROCK_VARIANTS[rid] = {"natural": natural, "stacked": f"{rid}_stacked", "flagstone": f"{rid}_flagstone",
                          "mossy": f"mossy_{rid}_stacked", "pebbles": f"{rid}_pebbles"}
for rid, (_, (sen, spt, ses), _, _, color, _) in ROCKS.items():  # pebbles last, all together in the tab
    add(f"{rid}_pebbles", (f"{sen} Pebbles", f"Seixos de {spt}", f"Guijarros de {ses}"), "carpet", f"{rid}_pebbles",
        "shovel", "pebbles", color)

LANG = {"en_us": {}, "pt_br": {}, "es_es": {}}
for _bid, _row in BLOCKS.items():
    for _code, _name in zip(("en_us", "pt_br", "es_es"), _row["names"]):
        LANG[_code][f"block.{NS}.{_bid}"] = _name
LANG["en_us"][f"itemGroup.{NS}.building"] = "Terrassic: Building"
LANG["pt_br"][f"itemGroup.{NS}.building"] = "Terrassic: Construção"
LANG["es_es"][f"itemGroup.{NS}.building"] = "Terrassic: Construcción"


def t(name):
    return f"{NS}:block/{name}"


def m(name):
    return f"{NS}:block/{name}"


def model(name, parent, **textures):
    write(f"{A}/models/block/{name}.json", {"parent": parent, "textures": textures})


def variant(model_name, x=0, y=0, uvlock=False):
    v = {"model": m(model_name)}
    if x:
        v["x"] = x
    if y:
        v["y"] = y
    if uvlock:
        v["uvlock"] = True
    return v


# ------------------------------------------------------------- models and blockstates, per kind
def gen_cube(bid, tex):
    model(bid, "minecraft:block/cube_all", all=t(tex))
    write(f"{A}/blockstates/{bid}.json", {"variants": {"": variant(bid)}})
    return m(bid)


def gen_column(bid, tex):
    side, end = tex
    model(bid, "minecraft:block/cube_column", side=t(side), end=t(end))
    write(f"{A}/blockstates/{bid}.json", {"variants": {"": variant(bid)}})
    return m(bid)


def gen_stairs(bid, tex):
    side, end = tex
    tx = dict(bottom=t(end), top=t(end), side=t(side))
    model(bid, "minecraft:block/stairs", **tx)
    model(f"{bid}_inner", "minecraft:block/inner_stairs", **tx)
    model(f"{bid}_outer", "minecraft:block/outer_stairs", **tx)
    base = {"east": 0, "south": 90, "west": 180, "north": 270}
    variants = {}
    for facing, y0 in base.items():
        for half in ("bottom", "top"):
            for shape in ("straight", "inner_left", "inner_right", "outer_left", "outer_right"):
                name = bid if shape == "straight" else (f"{bid}_inner" if shape.startswith("inner") else f"{bid}_outer")
                y = y0
                if half == "bottom" and shape.endswith("left"):
                    y -= 90
                if half == "top" and shape.endswith("right"):
                    y += 90
                y %= 360
                x = 180 if half == "top" else 0
                variants[f"facing={facing},half={half},shape={shape}"] = variant(name, x, y, uvlock=bool(x or y))
    write(f"{A}/blockstates/{bid}.json", {"variants": variants})
    return m(bid)


def gen_slab(bid, tex, full):
    side, end = tex
    tx = dict(bottom=t(end), top=t(end), side=t(side))
    model(bid, "minecraft:block/slab", **tx)
    model(f"{bid}_top", "minecraft:block/slab_top", **tx)
    write(f"{A}/blockstates/{bid}.json", {"variants": {
        "type=bottom": variant(bid), "type=top": variant(f"{bid}_top"), "type=double": {"model": full}}})
    return m(bid)


def gen_wall(bid, tex):
    model(f"{bid}_post", "minecraft:block/template_wall_post", wall=t(tex))
    model(f"{bid}_side", "minecraft:block/template_wall_side", wall=t(tex))
    model(f"{bid}_side_tall", "minecraft:block/template_wall_side_tall", wall=t(tex))
    model(f"{bid}_inventory", "minecraft:block/wall_inventory", wall=t(tex))
    parts = [{"when": {"up": "true"}, "apply": variant(f"{bid}_post")}]
    for d, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270)):
        parts.append({"when": {d: "low"}, "apply": variant(f"{bid}_side", y=y, uvlock=True)})
        parts.append({"when": {d: "tall"}, "apply": variant(f"{bid}_side_tall", y=y, uvlock=True)})
    write(f"{A}/blockstates/{bid}.json", {"multipart": parts})
    return m(f"{bid}_inventory")


def gen_fence(bid, tex):
    model(f"{bid}_post", "minecraft:block/fence_post", texture=t(tex))
    model(f"{bid}_side", "minecraft:block/fence_side", texture=t(tex))
    model(f"{bid}_inventory", "minecraft:block/fence_inventory", texture=t(tex))
    parts = [{"apply": variant(f"{bid}_post")}]
    for d, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270)):
        parts.append({"when": {d: "true"}, "apply": variant(f"{bid}_side", y=y, uvlock=True)})
    write(f"{A}/blockstates/{bid}.json", {"multipart": parts})
    return m(f"{bid}_inventory")


def gen_pane(bid, tex):
    pane, edge = tex
    tx = dict(pane=t(pane), edge=t(edge))
    for suffix in ("post", "side", "side_alt", "noside", "noside_alt"):
        model(f"{bid}_{suffix}", f"minecraft:block/template_glass_pane_{suffix}", **tx)
    p = lambda s, y=0: variant(f"{bid}_{s}", y=y)  # noqa: E731
    write(f"{A}/blockstates/{bid}.json", {"multipart": [
        {"apply": p("post")},
        {"when": {"north": "true"}, "apply": p("side")},
        {"when": {"east": "true"}, "apply": p("side", 90)},
        {"when": {"south": "true"}, "apply": p("side_alt")},
        {"when": {"west": "true"}, "apply": p("side_alt", 90)},
        {"when": {"north": "false"}, "apply": p("noside")},
        {"when": {"east": "false"}, "apply": p("noside_alt")},
        {"when": {"south": "false"}, "apply": p("noside_alt", 90)},
        {"when": {"west": "false"}, "apply": p("noside", 270)},
    ]})
    return None  # flat item sprite


def gen_carpet(bid, tex):
    model(bid, "minecraft:block/carpet", wool=t(tex))
    write(f"{A}/blockstates/{bid}.json", {"variants": {"": variant(bid)}})
    return m(bid)


def palisade_model(side, top):
    """Four sharpened logs in a 2x2 cluster, staggered heights so the top reads as a stockade."""
    elements = []
    for (x0, z0), h in (((0, 0), 16), ((8, 0), 14), ((0, 8), 13), ((8, 8), 15)):
        body_top = h - 3
        faces = {f: {"texture": "#side"} for f in ("north", "south", "east", "west")}
        faces["down"] = {"texture": "#top", "cullface": "down"}
        faces["up"] = {"texture": "#top"}
        for f, uv in faces.items():
            if f in ("north", "south", "east", "west"):
                u0 = x0 if f in ("north", "south") else z0
                uv["uv"] = [u0, 16 - body_top, u0 + 8, 16]
        elements.append({"from": [x0, 0, z0], "to": [x0 + 8, body_top, z0 + 8], "faces": faces})
        for step, inset in ((1, 1.5), (2, 3)):  # sharpened tip: two narrowing steps
            y0 = body_top + (step - 1) * 1.5
            tip = {f: {"texture": "#top"} for f in ("north", "south", "east", "west", "up")}
            elements.append({"from": [x0 + inset, y0, z0 + inset], "to": [x0 + 8 - inset, y0 + 1.5, z0 + 8 - inset], "faces": tip})
    return {"parent": "minecraft:block/block", "textures": {"side": t(side), "top": t(top), "particle": t(side)},
            "elements": elements}


def gen_palisade(bid, tex):
    write(f"{A}/models/block/{bid}.json", palisade_model(*tex))
    write(f"{A}/blockstates/{bid}.json", {"variants": {"": variant(bid)}})
    return m(bid)


GEN = {"cube": gen_cube, "column": gen_column, "stairs": gen_stairs, "wall": gen_wall, "fence": gen_fence,
       "pane": gen_pane, "carpet": gen_carpet, "palisade": gen_palisade}


# ------------------------------------------------------------- loot
def loot_self(bid, extra=None):
    pools = [{"rolls": 1, "bonus_rolls": 0, "entries": [{"type": "minecraft:item", "name": f"{NS}:{bid}"}],
              "conditions": [{"condition": "minecraft:survives_explosion"}]}]
    if extra:
        pools.append(extra)
    write(f"{D}/loot_tables/blocks/{bid}.json", {"type": "minecraft:block", "pools": pools})


def loot_slab(bid):
    write(f"{D}/loot_tables/blocks/{bid}.json", {"type": "minecraft:block", "pools": [{
        "rolls": 1, "bonus_rolls": 0, "entries": [{"type": "minecraft:item", "name": f"{NS}:{bid}", "functions": [
            {"function": "minecraft:set_count", "count": 2, "add": False, "conditions": [
                {"condition": "minecraft:block_state_property", "block": f"{NS}:{bid}", "properties": {"type": "double"}}]},
            {"function": "minecraft:explosion_decay"}]}]}]})


# flint nodules also give a loose flint now and then (not with Silk Touch)
FLINT_BONUS = {"rolls": 1, "entries": [{"type": "minecraft:item", "name": "minecraft:flint"}], "conditions": [
    {"condition": "minecraft:inverted", "term": {"condition": "minecraft:match_tool", "predicate": {
        "enchantments": [{"enchantment": "minecraft:silk_touch", "levels": {"min": 1}}]}}},
    {"condition": "minecraft:table_bonus", "enchantment": "minecraft:fortune", "chances": [0.25, 0.35, 0.5, 0.8]}]}


# ------------------------------------------------------------- recipes
def ingredient(v):
    return {"tag": v[1:]} if v.startswith("#") else {"item": v}


def shaped(name, pattern, key, result, count=1):
    write(f"{D}/recipes/{name}.json", {
        "type": "minecraft:crafting_shaped", "category": "building", "pattern": pattern,
        "key": {k: ingredient(v) for k, v in key.items()},
        "result": {"item": f"{NS}:{result}", "count": count}})


def shapeless(name, ingredients, result, count=1):
    write(f"{D}/recipes/{name}.json", {
        "type": "minecraft:crafting_shapeless", "category": "building",
        "ingredients": [ingredient(v) for v in ingredients], "result": {"item": f"{NS}:{result}", "count": count}})


def stonecut(source, result, count=1):
    write(f"{D}/recipes/{result}_from_{source}_stonecutting.json", {
        "type": "minecraft:stonecutting", "ingredient": {"item": f"{NS}:{source}"},
        "result": f"{NS}:{result}", "count": count})


def shape_recipes(bid):
    """Vanilla-style stairs / slab / wall recipes (crafting and stonecutter) for every shape of a block."""
    stone = BLOCKS[bid]["tool"] == "pickaxe"
    if f"{bid}_stairs" in BLOCKS:
        shaped(f"{bid}_stairs", ["X  ", "XX ", "XXX"], {"X": f"{NS}:{bid}"}, f"{bid}_stairs", 4)
        if stone:
            stonecut(bid, f"{bid}_stairs")
    if f"{bid}_slab" in BLOCKS:
        shaped(f"{bid}_slab", ["XXX"], {"X": f"{NS}:{bid}"}, f"{bid}_slab", 6)
        if stone:
            stonecut(bid, f"{bid}_slab", 2)
    if f"{bid}_wall" in BLOCKS:
        shaped(f"{bid}_wall", ["XXX", "XXX"], {"X": f"{NS}:{bid}"}, f"{bid}_wall", 6)
        if stone:
            stonecut(bid, f"{bid}_wall")


def recipes():
    shaped("thatch", ["WW", "WW"], {"W": "minecraft:wheat"}, "thatch", 2)
    shaped("straw_mat", ["TT"], {"T": f"{NS}:thatch"}, "straw_mat", 3)
    shaped("wattle_and_daub", ["SM", "MS"], {"S": "minecraft:stick", "M": "minecraft:mud"}, "wattle_and_daub", 2)
    shaped("log_palisade", [" F ", "LLL", "LLL"], {"F": "minecraft:flint", "L": "#minecraft:logs"}, "log_palisade", 6)
    shaped("bone_fence", ["BTB", "BTB"], {"B": "minecraft:bone", "T": "minecraft:string"}, "bone_fence", 3)
    shaped("hide_screen", ["SLS", "SLS"], {"S": "minecraft:stick", "L": "minecraft:leather"}, "hide_screen", 4)
    for rid, v in ROCK_VARIANTS.items():
        nat = v["natural"]
        shaped(v["stacked"], ["RR", "RR"], {"R": f"{NS}:{nat}"}, v["stacked"], 4)
        shaped(v["flagstone"], ["RR"], {"R": f"{NS}:{nat}"}, v["flagstone"], 2)
        shapeless(f"{v['mossy']}_from_vine", [f"{NS}:{v['stacked']}", "minecraft:vine"], v["mossy"])
        shapeless(f"{v['mossy']}_from_moss_block", [f"{NS}:{v['stacked']}", "minecraft:moss_block"], v["mossy"])
        shapeless(v["pebbles"], [f"{NS}:{nat}"], v["pebbles"], 4)
        stonecut(nat, v["pebbles"], 4)
        stonecut(nat, v["stacked"])
        stonecut(nat, v["flagstone"])
        for shape in ("stairs", "slab", "wall"):
            for var in ("stacked", "flagstone"):
                if f"{v[var]}_{shape}" in BLOCKS:
                    stonecut(nat, f"{v[var]}_{shape}", 2 if shape == "slab" else 1)
    for bid in BLOCKS:
        shape_recipes(bid)


# ------------------------------------------------------------- tags
def tags():
    mc = os.path.join(os.path.dirname(D), "minecraft", "tags")
    by_tool = {}
    for bid, row in BLOCKS.items():
        by_tool.setdefault(row["tool"], []).append(f"{NS}:{bid}")
    for tool, ids in by_tool.items():
        write(os.path.join(mc, "blocks", "mineable", f"{tool}.json"), {"replace": False, "values": ids})
    for kind, tag in (("stairs", "stairs"), ("slab", "slabs"), ("wall", "walls"), ("fence", "fences")):
        ids = [f"{NS}:{b}" for b, row in BLOCKS.items() if row["kind"] == kind]
        write(os.path.join(mc, "blocks", f"{tag}.json"), {"replace": False, "values": ids})
        write(os.path.join(mc, "items", f"{tag}.json"), {"replace": False, "values": ids})
    # natural rocks are carved by caves and ravines like the vanilla stones
    natural = [f"{NS}:{v['natural']}" for rid, v in ROCK_VARIANTS.items() if ROCKS[rid][5][4] == "stone"]
    write(os.path.join(mc, "blocks", "base_stone_overworld.json"), {"replace": False, "values": natural})


# ------------------------------------------------------------- worldgen
def worldgen():
    """Rock veins (minecraft:ore) and surface pebble patches (minecraft:random_patch). Returns the FEATURES table
    of BuildingBlocks.java: (placed feature, generation step, biome tag), in placement order (flint nodules come
    after the chalk they grow in)."""
    features = []
    for rid, (_, _, _, _, _, (size, count, lo, hi, target, biome)) in ROCKS.items():
        nat = ROCK_VARIANTS[rid]["natural"]
        if target == "stone":
            rule = {"predicate_type": "minecraft:tag_match", "tag": "minecraft:base_stone_overworld"}
        else:
            rule = {"predicate_type": "minecraft:block_match", "block": f"{NS}:{ROCK_VARIANTS[target]['natural']}"}
        write(f"{D}/worldgen/configured_feature/{nat}.json", {"type": "minecraft:ore", "config": {
            "size": size, "discard_chance_on_air_exposure": 0.0,
            "targets": [{"target": rule, "state": {"Name": f"{NS}:{nat}"}}]}})
        write(f"{D}/worldgen/placed_feature/{nat}.json", {"feature": f"{NS}:{nat}", "placement": [
            {"type": "minecraft:count", "count": count}, {"type": "minecraft:in_square"},
            {"type": "minecraft:height_range", "height": {"type": "minecraft:uniform",
                                                          "min_inclusive": {"absolute": lo}, "max_inclusive": {"absolute": hi}}},
            {"type": "minecraft:biome"}]})
        features.append((nat, "underground_ores", biome))
    ground = ["minecraft:sand", "minecraft:gravel", "minecraft:dirt", "minecraft:grass_block", "minecraft:coarse_dirt",
              "minecraft:stone", "minecraft:red_sand"]
    for rid, biomes in PEBBLE_PATCHES.items():
        peb = ROCK_VARIANTS[rid]["pebbles"]
        write(f"{D}/worldgen/configured_feature/{peb}.json", {"type": "minecraft:random_patch", "config": {
            "tries": 24, "xz_spread": 5, "y_spread": 1, "feature": {
                "feature": {"type": "minecraft:simple_block", "config": {"to_place": {
                    "type": "minecraft:simple_state_provider", "state": {"Name": f"{NS}:{peb}"}}}},
                "placement": [{"type": "minecraft:block_predicate_filter", "predicate": {"type": "minecraft:all_of", "predicates": [
                    {"type": "minecraft:matching_blocks", "blocks": "minecraft:air"},
                    {"type": "minecraft:matching_blocks", "offset": [0, -1, 0], "blocks": ground}]}}]}}})
        write(f"{D}/worldgen/placed_feature/{peb}.json", {"feature": f"{NS}:{peb}", "placement": [
            {"type": "minecraft:rarity_filter", "chance": 3}, {"type": "minecraft:in_square"},
            {"type": "minecraft:heightmap", "heightmap": "WORLD_SURFACE_WG"}, {"type": "minecraft:biome"}]})
        for biome in biomes:
            features.append((peb, "vegetal_decoration", biome))
    return features


# ------------------------------------------------------------- Java
JAVA_KIND = {"cube": "cube", "column": "cube", "palisade": "palisade", "stairs": "stairs", "slab": "slab",
             "wall": "wall", "fence": "fence", "pane": "pane", "carpet": "carpet"}


def gen_java(features):
    lines = []
    for bid, row in BLOCKS.items():
        props = f'material("{row["material"]}", MapColor.{row["color"]})'
        kind = JAVA_KIND[row["kind"]]
        if kind == "stairs":
            lines.append(f'        ModBlocks.stairs("{bid}", "{row["base"]}", {props});')
        else:
            lines.append(f'        ModBlocks.{kind}("{bid}", {props});')
    feats = "\n".join(f'            {{"{f}", "{step}", "{biome}"}},' for f, step, biome in features)
    src = f"""package com.terrassic.registry;

import net.minecraft.world.level.material.MapColor;

import static com.terrassic.registry.ModBlocks.material;

/**
 * GENERATED by tools/javagen/gen_blocks.py - do not edit. Change the BLOCKS table there and run
 * tools/javagen/gen_resources.py. {len(BLOCKS)} primitive building blocks, in creative-tab order.
 */
public final class BuildingBlocks {{
    /** Worldgen of the rocks: {{placed feature, generation step, biome tag}}, in placement order. */
    public static final String[][] FEATURES = {{
{feats}
    }};

    private BuildingBlocks() {{
    }}

    static void register() {{
{chr(10).join(lines)}
    }}
}}
"""
    os.makedirs(os.path.dirname(JAVA), exist_ok=True)
    with open(JAVA, "w", encoding="utf-8") as f:
        f.write(src)


def main():
    for bid, row in BLOCKS.items():
        kind, tex = row["kind"], row["tex"]
        if kind == "slab":
            item_model = gen_slab(bid, tex, m(row["base"]))
        else:
            item_model = GEN[kind](bid, tex)
        if item_model is None:
            write(f"{A}/models/item/{bid}.json", {"parent": "minecraft:item/generated", "textures": {"layer0": t(tex[0])}})
        else:
            write(f"{A}/models/item/{bid}.json", {"parent": item_model})
        if kind == "slab":
            loot_slab(bid)
        else:
            loot_self(bid, FLINT_BONUS if bid == "flint_nodules" else None)
    recipes()
    tags()
    gen_java(worldgen())
    print(f"{len(BLOCKS)} building blocks written")


if __name__ == "__main__":
    main()
