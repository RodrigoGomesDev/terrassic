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

# kinds: cube | column | log | leaves | sapling | stairs | slab | wall | fence | fence_gate | door | trapdoor | pane |
#        carpet | palisade | plant | tall_plant | water_plant | multiface
# material (Java ModBlocks.material): stone | soft_stone | hard_stone | pebbles | thatch | mud | wood | leaves | sapling |
#        plant | plant_cover | water_plant | multiface | bone | hide
BLOCKS = {}


def add(bid, names, kind, tex, tool, material, color, base=None, tags=()):
    """names = (en, pt, es); tex = texture name, or a tuple (side, end) / (pane, edge); base = full block of a
    stairs/slab (its model is the double slab, its state the stairs' base) or the tree id of a sapling;
    tags = extra vanilla tags (block and item), e.g. "logs"."""
    BLOCKS[bid] = {"names": names, "kind": kind, "tex": tex, "tool": tool, "material": material,
                   "color": color, "base": base, "tags": tags}


def add_shapes(bid, names, tex, tool, material, color, shapes, tags=(), shape_names=None):
    """A full block plus its stairs / slab / wall, named like vanilla in each language (or shape_names[shape])."""
    en, pt, es = names
    shape_names = shape_names or {}
    wooden = "planks" in tags  # hewn planks: <tree>_hewn_stairs / _slab, tagged wooden_stairs / wooden_slabs
    stem = bid.removesuffix("_planks") if wooden else bid
    add(bid, names, "cube", tex, tool, material, color, tags=tags)
    if "stairs" in shapes:
        add(f"{stem}_stairs", shape_names.get("stairs", (f"{en} Stairs", f"Escada de {pt}", f"Escaleras de {es}")),
            "stairs", (tex, tex), tool, material, color, bid, ("wooden_stairs",) if wooden else ())
    if "slab" in shapes:
        add(f"{stem}_slab", shape_names.get("slab", (f"{en} Slab", f"Laje de {pt}", f"Losa de {es}")),
            "slab", (tex, tex), tool, material, color, bid, ("wooden_slabs",) if wooden else ())
    if "wall" in shapes:
        add(f"{bid}_wall", (f"{en} Wall", f"Muro de {pt}", f"Muro de {es}"), "wall", tex, tool, material, color, bid)


# ------------------------------------------------------------- family: thatch, fibres, earth, bone, hide (batch 1)
add("thatch", ("Thatch", "Palha", "Paja"), "column", ("thatch", "thatch_top"), "hoe", "thatch", "COLOR_YELLOW")
add("thatch_stairs", ("Thatch Stairs", "Escada de Palha", "Escaleras de Paja"), "stairs", ("thatch", "thatch_top"), "hoe", "thatch", "COLOR_YELLOW", "thatch")
add("thatch_slab", ("Thatch Slab", "Laje de Palha", "Losa de Paja"), "slab", ("thatch", "thatch_top"), "hoe", "thatch", "COLOR_YELLOW", "thatch")
add("straw_mat", ("Straw Mat", "Esteira de Palha", "Estera de Paja"), "carpet", "straw_mat", "hoe", "thatch", "COLOR_YELLOW")
add("wattle_and_daub", ("Wattle and Daub", "Pau a Pique", "Bahareque"), "cube", "wattle_and_daub", "axe", "mud", "DIRT")
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

# ------------------------------------------------------------- family: prehistoric woods (phase 3 and 4)
SWAMP = "minecraft:has_structure/swamp_hut"  # 1.20.1 has no is_swamp biome tag
# tree id: names (en, pt, es), map colour of the wood, bark map colour,
#          tree feature (minecraft:tree config parts), biome tags, rarity (1 tree in N chunks per placement)
WOODS = {
    # Araucaria / monkey puzzle: tall bare trunk crowned by a flat umbrella of stiff branches
    "araucaria": (("Araucaria", "Araucária", "Araucaria"), "SAND", "COLOR_BROWN",
                  {"trunk_placer": {"type": "minecraft:straight_trunk_placer", "base_height": 11, "height_rand_a": 4, "height_rand_b": 2},
                   "foliage_placer": {"type": "minecraft:acacia_foliage_placer", "radius": 3, "offset": 0},
                   "minimum_size": {"type": "minecraft:two_layers_feature_size", "limit": 1, "lower_size": 0, "upper_size": 2}},
                  ("minecraft:is_forest", "minecraft:is_savanna"), 6),
    # Ginkgo: broad, irregular crown of fan leaves on a medium trunk
    "ginkgo": (("Ginkgo", "Ginkgo", "Ginkgo"), "TERRACOTTA_WHITE", "STONE",
               {"trunk_placer": {"type": "minecraft:fancy_trunk_placer", "base_height": 8, "height_rand_a": 5, "height_rand_b": 0},
                "foliage_placer": {"type": "minecraft:fancy_foliage_placer", "radius": 2, "offset": 4, "height": 4},
                "minimum_size": {"type": "minecraft:two_layers_feature_size", "limit": 0, "lower_size": 0, "upper_size": 0,
                                 "min_clipped_height": 4}},
               ("minecraft:is_forest",), 5),
    # Metasequoia / dawn redwood: tall narrow cone of soft needles, likes wet ground
    "metasequoia": (("Dawn Redwood", "Metassequoia", "Metasecuoya"), "TERRACOTTA_ORANGE", "TERRACOTTA_BROWN",
                    {"trunk_placer": {"type": "minecraft:straight_trunk_placer", "base_height": 14, "height_rand_a": 5, "height_rand_b": 2},
                     "foliage_placer": {"type": "minecraft:spruce_foliage_placer",
                                        "radius": {"type": "minecraft:uniform", "value": {"min_inclusive": 2, "max_inclusive": 3}},
                                        "offset": {"type": "minecraft:uniform", "value": {"min_inclusive": 0, "max_inclusive": 2}},
                                        "trunk_height": {"type": "minecraft:uniform", "value": {"min_inclusive": 2, "max_inclusive": 4}}},
                     "minimum_size": {"type": "minecraft:two_layers_feature_size", "limit": 2, "lower_size": 0, "upper_size": 2}},
                    ("minecraft:is_taiga", "minecraft:is_river"), 4),
    # Taxodium / bald cypress: swamp tree, straight trunk and a flattened, layered crown
    "taxodium": (("Bald Cypress", "Cipreste-do-pântano", "Ciprés Calvo"), "TERRACOTTA_LIGHT_GRAY", "TERRACOTTA_GRAY",
                 {"trunk_placer": {"type": "minecraft:straight_trunk_placer", "base_height": 10, "height_rand_a": 4, "height_rand_b": 1},
                  "foliage_placer": {"type": "minecraft:blob_foliage_placer", "radius": 3, "offset": 0, "height": 3},
                  "minimum_size": {"type": "minecraft:two_layers_feature_size", "limit": 1, "lower_size": 0, "upper_size": 1}},
                 (SWAMP, "minecraft:is_river"), 3),
    # Tree fern: short shaggy trunk with an umbrella of fronds, under the jungle canopy
    "tree_fern": (("Tree Fern", "Feto Arbóreo", "Helecho Arborescente"), "TERRACOTTA_BROWN", "COLOR_BROWN",
                  {"trunk_placer": {"type": "minecraft:straight_trunk_placer", "base_height": 4, "height_rand_a": 2, "height_rand_b": 0},
                   "foliage_placer": {"type": "minecraft:acacia_foliage_placer", "radius": 2, "offset": 0},
                   "minimum_size": {"type": "minecraft:two_layers_feature_size", "limit": 1, "lower_size": 0, "upper_size": 1}},
                  ("minecraft:is_jungle",), 2),
}
STRIPPABLES = []  # (log, stripped log)
for tid, ((en, pt, es), wood_color, bark_color, _, _, _) in WOODS.items():
    logs = ("logs", "logs_that_burn")
    add(f"{tid}_log", (f"{en} Log", f"Tronco de {pt}", f"Tronco de {es}"), "log", (f"{tid}_log", f"{tid}_log_top"),
        "axe", "wood", bark_color, tags=logs)
    add(f"stripped_{tid}_log", (f"Stripped {en} Log", f"Tronco de {pt} Descascado", f"Tronco de {es} Descortezado"), "log",
        (f"stripped_{tid}_log", f"stripped_{tid}_log_top"), "axe", "wood", wood_color, tags=logs)
    add(f"{tid}_wood", (f"{en} Wood", f"Lenho de {pt}", f"Leño de {es}"), "log", (f"{tid}_log", f"{tid}_log"),
        "axe", "wood", bark_color, tags=logs)
    add(f"stripped_{tid}_wood", (f"Stripped {en} Wood", f"Lenho de {pt} Descascado", f"Leño de {es} Descortezado"), "log",
        (f"stripped_{tid}_log", f"stripped_{tid}_log"), "axe", "wood", wood_color, tags=logs)
    add(f"{tid}_leaves", (f"{en} Leaves", f"Folhas de {pt}", f"Hojas de {es}"), "leaves", f"{tid}_leaves", "hoe", "leaves",
        "PLANT", tags=("leaves",))
    add(f"{tid}_sapling", (f"{en} Sapling", f"Muda de {pt}", f"Brote de {es}"), "sapling", f"{tid}_sapling", "axe", "sapling",
        "PLANT", base=tid, tags=("saplings",))
    add_shapes(f"{tid}_hewn_planks", (f"Hewn {en} Planks", f"Tábuas Lavradas de {pt}", f"Tablas Labradas de {es}"),
               f"{tid}_hewn_planks", "axe", "wood", wood_color, ("stairs", "slab"), tags=("planks",),
               shape_names={"stairs": (f"Hewn {en} Stairs", f"Escada Lavrada de {pt}", f"Escaleras Labradas de {es}"),
                            "slab": (f"Hewn {en} Slab", f"Laje Lavrada de {pt}", f"Losa Labrada de {es}")})
    add(f"{tid}_branch_fence", (f"{en} Branch Fence", f"Cerca de Galhos de {pt}", f"Valla de Ramas de {es}"), "fence",
        f"{tid}_branch_fence", "axe", "wood", bark_color, tags=("wooden_fences",))
    add(f"{tid}_branch_fence_gate", (f"{en} Branch Gate", f"Portão de Galhos de {pt}", f"Puerta de Ramas de {es}"),
        "fence_gate", f"{tid}_branch_fence", "axe", "wood", bark_color, tags=("fence_gates",))
    add(f"{tid}_palisade", (f"{en} Palisade", f"Paliçada de {pt}", f"Empalizada de {es}"), "palisade",
        (f"{tid}_log", f"{tid}_log_top"), "axe", "wood", bark_color)
    add(f"{tid}_lashed_door", (f"Lashed {en} Door", f"Porta de Troncos de {pt}", f"Puerta de Troncos de {es}"), "door",
        (f"{tid}_lashed_door_top", f"{tid}_lashed_door_bottom"), "axe", "wood", wood_color, tags=("wooden_doors",))
    add(f"{tid}_lashed_trapdoor", (f"Lashed {en} Trapdoor", f"Alçapão de Troncos de {pt}", f"Trampilla de Troncos de {es}"),
        "trapdoor", f"{tid}_lashed_trapdoor", "axe", "wood", wood_color, tags=("wooden_trapdoors",))
    STRIPPABLES += [(f"{tid}_log", f"stripped_{tid}_log"), (f"{tid}_wood", f"stripped_{tid}_wood")]

# ------------------------------------------------------------- family: prehistoric plants (phase 4)
# plant id: names, kind, texture (tall plants: <id>_bottom / <id>_top), worldgen patch (biome tags, 1 patch in N chunks)
PLANTS = {
    "horsetail": (("Horsetail", "Cavalinha", "Cola de Caballo"), "plant", ("minecraft:is_river", "minecraft:is_forest"), 4),
    "tall_horsetail": (("Tall Horsetail", "Cavalinha Alta", "Cola de Caballo Alta"), "tall_plant", ("minecraft:is_river",), 6),
    "calamites": (("Calamites", "Calamites", "Calamites"), "tall_plant", (SWAMP, "minecraft:is_river"), 8),
    "bracken": (("Bracken", "Samambaia", "Helecho Común"), "plant", ("minecraft:is_forest", "minecraft:is_taiga"), 3),
    "tall_bracken": (("Tall Bracken", "Samambaia Alta", "Helecho Común Alto"), "tall_plant", ("minecraft:is_forest",), 6),
    "royal_fern": (("Royal Fern", "Samambaia-real", "Helecho Real"), "plant", ("minecraft:is_jungle", SWAMP), 5),
    "young_cycad": (("Young Cycad", "Cicadácea Jovem", "Cícada Joven"), "plant", ("minecraft:is_savanna", "minecraft:is_jungle"), 5),
    "cycad": (("Cycad", "Cicadácea", "Cícada"), "tall_plant", ("minecraft:is_savanna", "minecraft:is_jungle"), 8),
    "williamsonia": (("Williamsonia", "Williamsonia", "Williamsonia"), "plant", ("minecraft:is_savanna", "minecraft:is_forest"), 8),
    "archaefructus": (("Archaefructus", "Archaefructus", "Archaefructus"), "water_plant", ("minecraft:is_river",), 6),
    "cretaceous_water_lily": (("Cretaceous Water Lily", "Nenúfar do Cretáceo", "Nenúfar del Cretácico"), "water_plant",
                              (SWAMP, "minecraft:is_river"), 4),
    "cretaceous_grass": (("Cretaceous Grass", "Capim do Cretáceo", "Hierba del Cretácico"), "plant", ("minecraft:is_savanna",), 2),
    "clubmoss": (("Clubmoss", "Licopódio", "Licopodio"), "plant", ("minecraft:is_taiga", "minecraft:is_forest"), 5),
    "spikemoss": (("Spikemoss", "Selaginela", "Selaginela"), "plant", ("minecraft:is_jungle",), 4),
    "liverwort": (("Liverwort", "Hepática", "Hepática"), "carpet", (SWAMP, "minecraft:is_river"), 6),
    "lichen": (("Lichen", "Líquen", "Liquen"), "multiface", ("minecraft:is_mountain",), 1),
    "rush": (("Rush", "Junco", "Junco"), "tall_plant", (SWAMP, "minecraft:is_river"), 4),
    "swamp_algae": (("Swamp Algae", "Alga de Pântano", "Alga de Pantano"), "water_plant", (SWAMP,), 3),
    "shelf_fungus": (("Shelf Fungus", "Fungo-prateleira", "Hongo Repisa"), "multiface", ("minecraft:is_forest", "minecraft:is_taiga"), 1),
}
PLANT_MATERIAL = {"plant": "plant", "tall_plant": "plant", "water_plant": "water_plant", "carpet": "plant_cover",
                  "multiface": "multiface"}
for pid, (names, kind, _, _) in PLANTS.items():
    tex = (f"{pid}_top", f"{pid}_bottom") if kind == "tall_plant" else pid
    add(pid, names, kind, tex, "hoe", PLANT_MATERIAL[kind], "PLANT")

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


def gen_log(bid, tex):
    """Pillar (logs, wood): upright model plus the lying one, rotated by the axis property like vanilla logs."""
    side, end = tex
    model(bid, "minecraft:block/cube_column", side=t(side), end=t(end))
    model(f"{bid}_horizontal", "minecraft:block/cube_column_horizontal", side=t(side), end=t(end))
    write(f"{A}/blockstates/{bid}.json", {"variants": {
        "axis=y": variant(bid), "axis=z": variant(f"{bid}_horizontal", x=90),
        "axis=x": variant(f"{bid}_horizontal", x=90, y=90)}})
    return m(bid)


def gen_leaves(bid, tex):
    model(bid, "minecraft:block/leaves", all=t(tex))
    write(f"{A}/blockstates/{bid}.json", {"variants": {"": variant(bid)}})
    return m(bid)


def gen_sapling(bid, tex):
    model(bid, "minecraft:block/cross", cross=t(tex))
    write(f"{A}/blockstates/{bid}.json", {"variants": {"": variant(bid)}})
    return None  # flat item sprite (the block texture)


def gen_fence_gate(bid, tex):
    for suffix in ("", "_open", "_wall", "_wall_open"):
        model(f"{bid}{suffix}", f"minecraft:block/template_fence_gate{suffix}", texture=t(tex))
    variants = {}
    for facing, y in (("south", 0), ("west", 90), ("north", 180), ("east", 270)):
        for in_wall in ("false", "true"):
            for open_ in ("false", "true"):
                name = bid + ("_wall" if in_wall == "true" else "") + ("_open" if open_ == "true" else "")
                variants[f"facing={facing},in_wall={in_wall},open={open_}"] = variant(name, y=y, uvlock=True)
    write(f"{A}/blockstates/{bid}.json", {"variants": variants})
    return m(bid)


def gen_door(bid, tex):
    top, bottom = tex
    parts = {}
    for half, part in (("lower", "bottom"), ("upper", "top")):
        for hinge in ("left", "right"):
            for open_ in ("", "_open"):
                name = f"{bid}_{part}_{hinge}{open_}"
                model(name, f"minecraft:block/door_{part}_{hinge}{open_}", top=t(top), bottom=t(bottom))
                parts[(half, hinge, bool(open_))] = name
    variants = {}
    for facing, y0 in (("east", 0), ("south", 90), ("west", 180), ("north", 270)):
        for half in ("lower", "upper"):
            for hinge in ("left", "right"):
                for open_ in (False, True):
                    y = (y0 + ((90 if hinge == "left" else 270) if open_ else 0)) % 360
                    variants[f"facing={facing},half={half},hinge={hinge},open={str(open_).lower()}"] = \
                        variant(parts[(half, hinge, open_)], y=y)
    write(f"{A}/blockstates/{bid}.json", {"variants": variants})
    return None  # item sprite in textures/item


def gen_trapdoor(bid, tex):
    for part in ("bottom", "top", "open"):
        model(f"{bid}_{part}", f"minecraft:block/template_orientable_trapdoor_{part}", texture=t(tex))
    variants = {}
    for facing, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270)):
        for half in ("bottom", "top"):
            variants[f"facing={facing},half={half},open=false"] = variant(f"{bid}_{half}", y=y)
            if half == "bottom":
                variants[f"facing={facing},half={half},open=true"] = variant(f"{bid}_open", y=y)
            else:
                variants[f"facing={facing},half={half},open=true"] = variant(f"{bid}_open", x=180, y=(y + 180) % 360)
    write(f"{A}/blockstates/{bid}.json", {"variants": variants})
    return m(f"{bid}_bottom")


def gen_plant(bid, tex):
    model(bid, "minecraft:block/cross", cross=t(tex))
    write(f"{A}/blockstates/{bid}.json", {"variants": {"": variant(bid)}})
    return None


def gen_tall_plant(bid, tex):
    top, bottom = tex
    model(f"{bid}_top", "minecraft:block/cross", cross=t(top))
    model(f"{bid}_bottom", "minecraft:block/cross", cross=t(bottom))
    write(f"{A}/blockstates/{bid}.json", {"variants": {"half=upper": variant(f"{bid}_top"),
                                                       "half=lower": variant(f"{bid}_bottom")}})
    return None


def gen_water_plant(bid, tex):
    model(bid, "minecraft:block/lily_pad", texture=t(tex))
    write(f"{A}/blockstates/{bid}.json", {"variants": {"": variant(bid)}})
    return None


def gen_multiface(bid, tex):
    """Grows flat on any face of a block, like glow lichen: one thin face model, rotated per direction."""
    write(f"{A}/models/block/{bid}.json", {
        "parent": "minecraft:block/block", "ambientocclusion": False,
        "textures": {"texture": t(tex), "particle": t(tex)},
        "elements": [{"from": [0, 0, 0.1], "to": [16, 16, 0.1], "shade": False, "faces": {
            "north": {"uv": [16, 0, 0, 16], "texture": "#texture"}, "south": {"uv": [0, 0, 16, 16], "texture": "#texture"}}}]})
    rot = {"north": {}, "east": {"y": 90}, "south": {"y": 180}, "west": {"y": 270}, "up": {"x": 270}, "down": {"x": 90}}
    parts = []
    for face, r in rot.items():
        parts.append({"when": {face: "true"}, "apply": variant(bid, r.get("x", 0), r.get("y", 0), uvlock=True)})
    write(f"{A}/blockstates/{bid}.json", {"multipart": parts})
    return None


GEN = {"plant": gen_plant, "tall_plant": gen_tall_plant, "water_plant": gen_water_plant, "multiface": gen_multiface,
       "cube": gen_cube, "column": gen_column, "stairs": gen_stairs, "wall": gen_wall, "fence": gen_fence,
       "pane": gen_pane, "carpet": gen_carpet, "palisade": gen_palisade, "log": gen_log, "leaves": gen_leaves,
       "sapling": gen_sapling, "fence_gate": gen_fence_gate, "door": gen_door, "trapdoor": gen_trapdoor}


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


SHEARS_OR_SILK = {"condition": "minecraft:any_of", "terms": [
    {"condition": "minecraft:match_tool", "predicate": {"items": ["minecraft:shears"]}},
    {"condition": "minecraft:match_tool", "predicate": {"enchantments": [{"enchantment": "minecraft:silk_touch", "levels": {"min": 1}}]}}]}


def loot_leaves(bid, sapling):
    """Like vanilla leaves: the block with shears or Silk Touch, otherwise a sapling now and then and some sticks."""
    write(f"{D}/loot_tables/blocks/{bid}.json", {"type": "minecraft:block", "pools": [
        {"rolls": 1, "bonus_rolls": 0, "entries": [{"type": "minecraft:alternatives", "children": [
            {"type": "minecraft:item", "name": f"{NS}:{bid}", "conditions": [SHEARS_OR_SILK]},
            {"type": "minecraft:item", "name": f"{NS}:{sapling}", "conditions": [
                {"condition": "minecraft:survives_explosion"},
                {"condition": "minecraft:table_bonus", "enchantment": "minecraft:fortune",
                 "chances": [0.05, 0.0625, 0.083333336, 0.1]}]}]}]},
        {"rolls": 1, "bonus_rolls": 0, "conditions": [{"condition": "minecraft:inverted", "term": SHEARS_OR_SILK}],
         "entries": [{"type": "minecraft:item", "name": "minecraft:stick", "functions": [
             {"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 1.0, "max": 2.0}},
             {"function": "minecraft:explosion_decay"}],
             "conditions": [{"condition": "minecraft:table_bonus", "enchantment": "minecraft:fortune",
                             "chances": [0.02, 0.022222223, 0.025, 0.033333335, 0.1]}]}]}]})


def loot_door(bid):
    """Only the lower half drops the block (doors, tall plants)."""
    write(f"{D}/loot_tables/blocks/{bid}.json", {"type": "minecraft:block", "pools": [{
        "rolls": 1, "bonus_rolls": 0, "entries": [{"type": "minecraft:item", "name": f"{NS}:{bid}", "conditions": [
            {"condition": "minecraft:block_state_property", "block": f"{NS}:{bid}", "properties": {"half": "lower"}}]}],
        "conditions": [{"condition": "minecraft:survives_explosion"}]}]})


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
    stem = bid.removesuffix("_planks") if "planks" in BLOCKS[bid]["tags"] else bid
    if stem != bid:
        if f"{stem}_stairs" in BLOCKS:
            shaped(f"{stem}_stairs", ["X  ", "XX ", "XXX"], {"X": f"{NS}:{bid}"}, f"{stem}_stairs", 4)
        if f"{stem}_slab" in BLOCKS:
            shaped(f"{stem}_slab", ["XXX"], {"X": f"{NS}:{bid}"}, f"{stem}_slab", 6)
        return
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
    for tid in WOODS:
        logs = f"#{NS}:{tid}_logs"
        planks = f"{NS}:{tid}_hewn_planks"
        shapeless(f"{tid}_hewn_planks", [logs], f"{tid}_hewn_planks", 4)
        shaped(f"{tid}_wood", ["LL", "LL"], {"L": f"{NS}:{tid}_log"}, f"{tid}_wood", 3)
        shaped(f"stripped_{tid}_wood", ["LL", "LL"], {"L": f"{NS}:stripped_{tid}_log"}, f"stripped_{tid}_wood", 3)
        shaped(f"{tid}_branch_fence", ["PSP", "PSP"], {"P": planks, "S": "minecraft:stick"}, f"{tid}_branch_fence", 3)
        shaped(f"{tid}_branch_fence_gate", ["SPS", "SPS"], {"P": planks, "S": "minecraft:stick"}, f"{tid}_branch_fence_gate")
        shaped(f"{tid}_palisade", [" F ", "LLL", "LLL"], {"F": "minecraft:flint", "L": f"{NS}:{tid}_log"}, f"{tid}_palisade", 6)
        shaped(f"{tid}_lashed_door", ["PP", "PP", "PP"], {"P": planks}, f"{tid}_lashed_door", 3)
        shaped(f"{tid}_lashed_trapdoor", ["PPP", "PPP"], {"P": planks}, f"{tid}_lashed_trapdoor", 2)
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
    extra = {}
    for bid, row in BLOCKS.items():
        for tag in row["tags"]:
            extra.setdefault(tag, []).append(f"{NS}:{bid}")
    for tag, ids in extra.items():
        write(os.path.join(mc, "blocks", f"{tag}.json"), {"replace": False, "values": ids})
        write(os.path.join(mc, "items", f"{tag}.json"), {"replace": False, "values": ids})
    for tid in WOODS:  # terrassic:<tree>_logs: the four log blocks of a tree, for the planks recipe
        ids = [f"{NS}:{tid}_log", f"{NS}:stripped_{tid}_log", f"{NS}:{tid}_wood", f"{NS}:stripped_{tid}_wood"]
        write(os.path.join(os.path.dirname(D), NS, "tags", "blocks", f"{tid}_logs.json"), {"replace": False, "values": ids})
        write(os.path.join(os.path.dirname(D), NS, "tags", "items", f"{tid}_logs.json"), {"replace": False, "values": ids})
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
    for tid, (_, _, _, tree, biomes, rarity) in WOODS.items():
        # configured feature <tree>: also what the sapling grows into (PrehistoricTreeGrower)
        config = {"ignore_vines": True, "force_dirt": False,
                  "dirt_provider": {"type": "minecraft:simple_state_provider", "state": {"Name": "minecraft:dirt"}},
                  "trunk_provider": {"type": "minecraft:simple_state_provider",
                                     "state": {"Name": f"{NS}:{tid}_log", "Properties": {"axis": "y"}}},
                  "foliage_provider": {"type": "minecraft:simple_state_provider", "state": {
                      "Name": f"{NS}:{tid}_leaves", "Properties": {"distance": "7", "persistent": "false", "waterlogged": "false"}}},
                  "decorators": []}
        config.update(tree)
        write(f"{D}/worldgen/configured_feature/{tid}.json", {"type": "minecraft:tree", "config": config})
        write(f"{D}/worldgen/placed_feature/{tid}_tree.json", {"feature": f"{NS}:{tid}", "placement": [
            {"type": "minecraft:rarity_filter", "chance": rarity}, {"type": "minecraft:in_square"},
            {"type": "minecraft:surface_water_depth_filter", "max_water_depth": 0},
            {"type": "minecraft:heightmap", "heightmap": "OCEAN_FLOOR"}, {"type": "minecraft:biome"},
            {"type": "minecraft:block_predicate_filter", "predicate": {"type": "minecraft:would_survive", "state": {
                "Name": f"{NS}:{tid}_sapling", "Properties": {"stage": "0"}}}}]})
        for biome in biomes:
            features.append((f"{tid}_tree", "vegetal_decoration", biome))
    for pid, (_, kind, biomes, rarity) in PLANTS.items():
        state = {"Name": f"{NS}:{pid}"}
        if kind == "multiface":  # lichen on mountain rock, shelf fungus on tree trunks
            hosts = ([f"{NS}:{ROCK_VARIANTS[r]['natural']}" for r in ROCKS] + ["minecraft:stone", "minecraft:andesite",
                     "minecraft:granite", "minecraft:diorite", "minecraft:cobblestone", "minecraft:mossy_cobblestone"]
                     if pid == "lichen" else
                     [f"{NS}:{w}_log" for w in WOODS] + [f"minecraft:{w}_log" for w in ("oak", "birch", "spruce", "dark_oak", "jungle")])
            write(f"{D}/worldgen/configured_feature/{pid}.json", {"type": "minecraft:multiface_growth", "config": {
                "block": f"{NS}:{pid}", "search_range": 20 if pid == "lichen" else 6, "chance_of_spreading": 0.5,
                "can_place_on_floor": pid == "lichen", "can_place_on_ceiling": False, "can_place_on_wall": True,
                "can_be_placed_on": hosts}})
            placement = ([{"type": "minecraft:count", "count": 12}, {"type": "minecraft:in_square"},
                          {"type": "minecraft:height_range", "height": {"type": "minecraft:uniform",
                           "min_inclusive": {"absolute": 70}, "max_inclusive": {"absolute": 220}}}]
                         if pid == "lichen" else
                         [{"type": "minecraft:count", "count": 4}, {"type": "minecraft:in_square"},
                          {"type": "minecraft:heightmap", "heightmap": "MOTION_BLOCKING_NO_LEAVES"}])
            write(f"{D}/worldgen/placed_feature/{pid}.json", {"feature": f"{NS}:{pid}",
                                                             "placement": placement + [{"type": "minecraft:biome"}]})
        else:
            if kind == "water_plant":
                where = [{"type": "minecraft:matching_blocks", "blocks": "minecraft:air"},
                         {"type": "minecraft:matching_fluids", "offset": [0, -1, 0], "fluids": "minecraft:water"}]
            else:
                if kind == "tall_plant":
                    state["Properties"] = {"half": "lower"}
                where = [{"type": "minecraft:matching_blocks", "blocks": "minecraft:air"},
                         {"type": "minecraft:would_survive", "state": state}]
            write(f"{D}/worldgen/configured_feature/{pid}.json", {"type": "minecraft:random_patch", "config": {
                "tries": 32 if kind != "tall_plant" else 16, "xz_spread": 6, "y_spread": 2, "feature": {
                    "feature": {"type": "minecraft:simple_block", "config": {"to_place": {
                        "type": "minecraft:simple_state_provider", "state": state}}},
                    "placement": [{"type": "minecraft:block_predicate_filter", "predicate": {
                        "type": "minecraft:all_of", "predicates": where}}]}}})
            write(f"{D}/worldgen/placed_feature/{pid}.json", {"feature": f"{NS}:{pid}", "placement": [
                {"type": "minecraft:rarity_filter", "chance": rarity}, {"type": "minecraft:in_square"},
                {"type": "minecraft:heightmap", "heightmap": "WORLD_SURFACE_WG"}, {"type": "minecraft:biome"}]})
        for biome in biomes:
            features.append((pid, "vegetal_decoration", biome))
    return features


# ------------------------------------------------------------- Java
JAVA_KIND = {"cube": "cube", "column": "cube", "palisade": "palisade", "stairs": "stairs", "slab": "slab",
             "wall": "wall", "fence": "fence", "pane": "pane", "carpet": "carpet", "log": "log", "leaves": "leaves",
             "sapling": "sapling", "fence_gate": "fenceGate", "door": "door", "trapdoor": "trapdoor", "plant": "plant",
             "tall_plant": "tallPlant", "water_plant": "waterPlant", "multiface": "multiface"}
# drawn with transparent pixels: rendered as cutout on the client (BuildingBlocksClient)
CUTOUT_KINDS = ("leaves", "sapling", "door", "trapdoor", "plant", "tall_plant", "water_plant", "multiface")


def gen_java(features):
    lines = []
    for bid, row in BLOCKS.items():
        props = f'material("{row["material"]}", MapColor.{row["color"]})'
        kind = JAVA_KIND[row["kind"]]
        if kind in ("stairs", "sapling"):
            lines.append(f'        ModBlocks.{kind}("{bid}", "{row["base"]}", {props});')
        else:
            lines.append(f'        ModBlocks.{kind}("{bid}", {props});')
    strip = "\n".join(f'            {{"{a}", "{b}"}},' for a, b in STRIPPABLES)
    cutout = ", ".join(f'"{b}"' for b, row in BLOCKS.items() if row["kind"] in CUTOUT_KINDS)
    on_water = ", ".join(f'"{b}"' for b, row in BLOCKS.items() if row["kind"] == "water_plant")
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

    /** {{log, stripped log}}: an axe strips the first into the second. */
    public static final String[][] STRIPPABLES = {{
{strip}
    }};

    /** Blocks drawn with transparent pixels, rendered as cutout. */
    public static final String[] CUTOUT = {{{cutout}}};

    /** Blocks that float on water: their item places them on the water surface. */
    public static final String[] ON_WATER = {{{on_water}}};

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
        if kind == "door":
            write(f"{A}/models/item/{bid}.json", {"parent": "minecraft:item/generated", "textures": {"layer0": f"{NS}:item/{bid}"}})
        elif kind in ("sapling", "plant", "water_plant", "multiface"):
            write(f"{A}/models/item/{bid}.json", {"parent": "minecraft:item/generated", "textures": {"layer0": t(tex)}})
        elif item_model is None:
            write(f"{A}/models/item/{bid}.json", {"parent": "minecraft:item/generated", "textures": {"layer0": t(tex[0])}})
        else:
            write(f"{A}/models/item/{bid}.json", {"parent": item_model})
        if kind == "slab":
            loot_slab(bid)
        elif kind == "leaves":
            loot_leaves(bid, bid.replace("_leaves", "_sapling"))
        elif kind in ("door", "tall_plant"):
            loot_door(bid)
        else:
            loot_self(bid, FLINT_BONUS if bid == "flint_nodules" else None)
    recipes()
    tags()
    gen_java(worldgen())
    print(f"{len(BLOCKS)} building blocks written")


if __name__ == "__main__":
    main()
