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
from gen_resources import A, D, ROOT, SPECIES, write  # noqa: E402

NS = "terrassic"
JAVA = os.path.join(ROOT, "common", "src", "main", "java", "com", "terrassic", "registry", "BuildingBlocks.java")

# kinds: cube | column | log | leaves | sapling | stairs | slab | wall | fence | fence_gate | door | trapdoor | pane |
#        carpet | palisade | plant | tall_plant | water_plant | multiface | facing | eave | climber | trophy | arch |
#        torch | wall_torch | spikes | bed | prop | hearth | drum | chimes | basket (the last five: model from PROPS)
# material (Java ModBlocks.material): stone | soft_stone | hard_stone | pebbles | thatch | mud | wood | leaves | sapling |
#        plant | plant_cover | water_plant | multiface | bone | hide | earth | plaster | wicker | fiber | net |
#        rug | trophy | bone_loose | feathers | torch | lamp | hearth | prop_wood | prop_stone | clay | bed | spikes |
#        pit_cover | nest | sand_nest | chimes
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
    # Sabal palm: short single trunk with a tuft of fan leaves, on beaches and in the savanna
    "sabal": (("Sabal Palm", "Palmeira Sabal", "Palmera Sabal"), "SAND", "TERRACOTTA_GRAY",
              {"trunk_placer": {"type": "minecraft:straight_trunk_placer", "base_height": 6, "height_rand_a": 3, "height_rand_b": 0},
               "foliage_placer": {"type": "minecraft:acacia_foliage_placer", "radius": 2, "offset": 0},
               "minimum_size": {"type": "minecraft:two_layers_feature_size", "limit": 1, "lower_size": 0, "upper_size": 1}},
              ("minecraft:is_beach", "minecraft:is_savanna"), 5),
    # Magnolia: one of the first flowering trees, a rounded crown on a medium trunk, in forests
    "magnolia": (("Magnolia", "Magnólia", "Magnolia"), "TERRACOTTA_WHITE", "STONE",
                 {"trunk_placer": {"type": "minecraft:fancy_trunk_placer", "base_height": 6, "height_rand_a": 3, "height_rand_b": 0},
                  # Fancy branches end above the attachment's blob cap at offset 0/1. Lift the rounded crown.
                  "foliage_placer": {"type": "minecraft:blob_foliage_placer", "radius": 3, "offset": 2, "height": 3},
                  "minimum_size": {"type": "minecraft:two_layers_feature_size", "limit": 1, "lower_size": 0, "upper_size": 1}},
                 ("minecraft:is_forest",), 6),
    # Podocarpus: a narrow evergreen of mountain and rain forests
    "podocarpus": (("Podocarpus", "Podocarpo", "Podocarpo"), "TERRACOTTA_ORANGE", "TERRACOTTA_BROWN",
                   {"trunk_placer": {"type": "minecraft:straight_trunk_placer", "base_height": 9, "height_rand_a": 3, "height_rand_b": 1},
                    "foliage_placer": {"type": "minecraft:spruce_foliage_placer",
                                       "radius": {"type": "minecraft:uniform", "value": {"min_inclusive": 2, "max_inclusive": 3}},
                                       "offset": {"type": "minecraft:uniform", "value": {"min_inclusive": 0, "max_inclusive": 1}},
                                       "trunk_height": {"type": "minecraft:uniform", "value": {"min_inclusive": 1, "max_inclusive": 3}}},
                    "minimum_size": {"type": "minecraft:two_layers_feature_size", "limit": 2, "lower_size": 0, "upper_size": 2}},
                   ("minecraft:is_taiga", "minecraft:is_jungle"), 5),
    # Platanus / plane tree: big spreading tree of riverbanks, known from Cretaceous fossil leaves
    "platanus": (("Plane Tree", "Platanus", "Plátano de Sombra"), "TERRACOTTA_WHITE", "TERRACOTTA_LIGHT_GRAY",
                 {"trunk_placer": {"type": "minecraft:fancy_trunk_placer", "base_height": 9, "height_rand_a": 5, "height_rand_b": 0},
                  "foliage_placer": {"type": "minecraft:fancy_foliage_placer", "radius": 2, "offset": 4, "height": 4},
                  "minimum_size": {"type": "minecraft:two_layers_feature_size", "limit": 0, "lower_size": 0, "upper_size": 0,
                                   "min_clipped_height": 4}},
                 ("minecraft:is_river", "minecraft:is_forest"), 6),
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

# ------------------------------------------------------------- family: earth, plaster and cave paintings (phase 5)
add("cross_braced_wattle", ("Cross-Braced Wattle", "Pau a Pique Travado", "Bahareque Arriostrado"), "cube",
    "cross_braced_wattle", "axe", "mud", "DIRT")
add("timber_framed_wattle", ("Timber-Framed Wattle", "Pau a Pique com Esteios", "Bahareque con Entramado"), "cube",
    "timber_framed_wattle", "axe", "mud", "DIRT")
add("whitewashed_wattle", ("Whitewashed Wattle", "Pau a Pique Caiado", "Bahareque Encalado"), "cube",
    "whitewashed_wattle", "axe", "mud", "QUARTZ")
add_shapes("rammed_earth", ("Rammed Earth", "Taipa de Pilão", "Tapial"), "rammed_earth", "shovel", "earth", "DIRT",
           ("stairs", "slab", "wall"))
add("packed_earth_floor", ("Packed Earth Floor", "Chão de Terra Batida", "Suelo de Tierra Apisonada"), "cube",
    "packed_earth_floor", "shovel", "earth", "DIRT")
PLASTERS = {
    "clay_plaster": (("Clay Plaster", "Reboco de Barro", "Revoque de Barro"), "TERRACOTTA_LIGHT_GRAY"),
    "red_ochre_plaster": (("Red Ochre Plaster", "Reboco de Ocre Vermelho", "Revoque de Ocre Rojo"), "TERRACOTTA_RED"),
    "yellow_ochre_plaster": (("Yellow Ochre Plaster", "Reboco de Ocre Amarelo", "Revoque de Ocre Amarillo"),
                             "TERRACOTTA_YELLOW"),
    "charcoal_plaster": (("Charcoal Plaster", "Reboco de Carvão", "Revoque de Carbón"), "COLOR_BLACK"),
    "chalk_whitewash": (("Chalk Whitewash", "Caiação de Giz", "Encalado de Tiza"), "QUARTZ"),
}
for _pid, (_names, _color) in PLASTERS.items():
    add(_pid, _names, "cube", _pid, "pickaxe", "plaster", _color)
# cave paintings: a limestone block with a pictogram on its front (facing the player who placed it)
PAINTINGS = {
    "handprint": ("Handprint", "Mão", "Mano"),
    "tyrannosaurus": ("Tyrannosaurus", "Tiranossauro", "Tiranosaurio"),
    "triceratops": ("Triceratops", "Tricerátops", "Triceratops"),
    "brachiosaurus": ("Brachiosaurus", "Braquiossauro", "Braquiosaurio"),
    "stegosaurus": ("Stegosaurus", "Estegossauro", "Estegosaurio"),
    "raptor": ("Raptor", "Raptor", "Raptor"),
    "pteranodon": ("Pteranodon", "Pteranodonte", "Pteranodon"),
    "mosasaurus": ("Mosasaurus", "Mosassauro", "Mosasaurio"),
    "spear_hunt": ("Spear Hunt", "Caça com Lança", "Caza con Lanza"),
    "herd": ("Herd", "Manada", "Manada"),
    "footprints": ("Footprints", "Pegadas", "Huellas"),
    "fire": ("Fire", "Fogo", "Fuego"),
    "sun": ("Sun", "Sol", "Sol"),
    "moon": ("Moon", "Lua", "Luna"),
    "spiral": ("Spiral", "Espiral", "Espiral"),
    "stars": ("Stars", "Estrelas", "Estrellas"),
}
for _name, (_en, _pt, _es) in PAINTINGS.items():
    add(f"cave_painting_{_name}", (f"Cave Painting: {_en}", f"Pintura Rupestre: {_pt}", f"Pintura Rupestre: {_es}"),
        "facing", (f"cave_painting_{_name}", "limestone"), "pickaxe", "soft_stone", "SAND")

# ------------------------------------------------------------- family: roofs and weaving (phase 5)
add("thatch_eave", ("Thatch Eave", "Beiral de Palha", "Alero de Paja"), "eave", "thatch", "hoe", "thatch", "COLOR_YELLOW")
ROOFS = {  # roof id: names, colour, crafted from (2x2)
    "reed_thatch": (("Reed Thatch", "Palha de Junco", "Paja de Junco"), "COLOR_YELLOW", "rush"),
    "cycad_thatch": (("Cycad Frond Thatch", "Cobertura de Cicadácea", "Techo de Cícada"), "COLOR_GREEN", "cycad"),
    "fern_thatch": (("Fern Thatch", "Cobertura de Samambaia", "Techo de Helecho"), "COLOR_BROWN", "bracken"),
}
for _rid, ((_en, _pt, _es), _color, _) in ROOFS.items():
    _tex = (_rid, f"{_rid}_top")
    add(_rid, (_en, _pt, _es), "column", _tex, "hoe", "thatch", _color)
    add(f"{_rid}_stairs", (f"{_en} Stairs", f"Escada de {_pt}", f"Escaleras de {_es}"), "stairs", _tex, "hoe", "thatch",
        _color, _rid)
    add(f"{_rid}_slab", (f"{_en} Slab", f"Laje de {_pt}", f"Losa de {_es}"), "slab", _tex, "hoe", "thatch", _color, _rid)
    add(f"{_rid}_eave", (f"{_en} Eave", f"Beiral de {_pt}", f"Alero de {_es}"), "eave", _rid, "hoe", "thatch", _color)
add("wicker_block", ("Wicker Block", "Bloco de Vime", "Bloque de Mimbre"), "cube", "wicker_block", "axe", "wicker",
    "WOOD")
add("wicker_panel", ("Wicker Panel", "Painel de Vime", "Panel de Mimbre"), "pane", ("wicker_block", "wicker_block"),
    "axe", "wicker", "WOOD")
add("woven_fence", ("Woven Fence", "Cerca Trançada", "Valla Trenzada"), "fence", "wicker_block", "axe", "wicker", "WOOD")
add("wicker_door", ("Wicker Door", "Porta de Vime", "Puerta de Mimbre"), "door", ("wicker_door_top", "wicker_door_bottom"),
    "axe", "wicker", "WOOD")
add("wicker_trapdoor", ("Wicker Trapdoor", "Alçapão de Vime", "Trampilla de Mimbre"), "trapdoor", "wicker_trapdoor",
    "axe", "wicker", "WOOD")
add("reed_mat", ("Reed Mat", "Esteira de Junco", "Estera de Junco"), "carpet", "reed_mat", "hoe", "thatch",
    "COLOR_YELLOW")
add("reed_bundle", ("Reed Bundle", "Feixe de Junco", "Haz de Juncos"), "log", ("reed_bundle", "reed_bundle_top"),
    "hoe", "thatch", "COLOR_YELLOW")
add("rope_coil", ("Rope Coil", "Rolo de Corda", "Rollo de Cuerda"), "log", ("rope_coil", "rope_coil_top"), "hoe",
    "fiber", "COLOR_BROWN")
add("fiber_net", ("Fiber Net", "Rede de Fibra", "Red de Fibra"), "climber", "fiber_net", "hoe", "net", "COLOR_BROWN",
    tags=("climbable",))
BLOCK_ONLY_TAGS = ("climbable",)

# ------------------------------------------------------------- family: hide, bone, trophies and fossils (phase 6)
# hides come from the <species>_hide items of the species generator (one per species, dropped like cow leather)
HIDES = {  # hide id: names (en, pt, es), source item of the frame and panel (None: rawhide from leather)
    "rawhide": (("Rawhide", "Couro Cru", "Cuero Crudo"), None),
    "tanned_hide": (("Tanned Hide", "Couro Curtido", "Cuero Curtido"), None),
    "scaled_hide": (("Scaled Hide", "Couro Escamado", "Cuero Escamoso"), "ankylosaurus_hide"),
    "feathered_hide": (("Feathered Hide", "Couro com Penas", "Cuero con Plumas"), "velociraptor_hide"),
    "fuzzy_hide": (("Fuzzy Pterosaur Hide", "Couro Felpudo de Pterossauro", "Cuero Velloso de Pterosaurio"),
                   "pteranodon_hide"),
}
for _hid, ((_en, _pt, _es), _) in HIDES.items():
    add(f"{_hid}_frame", (f"{_en} Frame", f"{_pt} Esticado", f"{_es} Tensado"), "cube", f"{_hid}_frame", "axe",
        "hide", "COLOR_BROWN")
    if _hid != "rawhide":  # the rawhide panel is hide_screen (batch 1)
        add(f"{_hid}_panel", (f"{_en} Panel", f"Painel de {_pt}", f"Panel de {_es}"), "pane",
            (f"{_hid}_panel", "hide_screen_edge"), "axe", "hide", "COLOR_BROWN")
SKULL_ROCK = {"brachiosaurus": "shale", "stegosaurus": "shale", "dilophosaurus": "shale",
              "compsognathus": "shale"}  # Jurassic beds; the Cretaceous skulls come out of limestone
for _sid, (_en, _pt, _es, _) in SPECIES.items():
    add(f"{_sid}_hide_rug", (f"{_en} Hide Rug", f"Tapete de Couro de {_pt}", f"Alfombra de Piel de {_es}"), "carpet",
        f"{_sid}_hide_rug", "axe", "rug", "COLOR_BROWN")
for _sid, (_en, _pt, _es, _) in SPECIES.items():
    add(f"{_sid}_skull_trophy", (f"{_en} Skull Trophy", f"Troféu de Crânio de {_pt}", f"Trofeo de Cráneo de {_es}"),
        "trophy", f"{_sid}_skull_trophy", "pickaxe", "trophy", "SAND")
for _sid, (_en, _pt, _es, _) in SPECIES.items():
    add(f"{_sid}_skull_fossil", (f"{_en} Skull Fossil", f"Crânio Fóssil de {_pt}", f"Cráneo Fósil de {_es}"),
        "facing", (f"{_sid}_skull_fossil", SKULL_ROCK.get(_sid, "limestone")), "pickaxe", "soft_stone", "SAND")
add("bone_fence_gate", ("Bone Fence Gate", "Portão de Osso", "Puerta de Valla de Hueso"), "fence_gate", "bone_fence",
    "pickaxe", "bone", "SAND")
add("ossuary_wall", ("Ossuary Wall", "Parede de Ossuário", "Muro de Osario"), "cube", "ossuary_wall", "pickaxe", "bone",
    "SAND")
add("rib_arch", ("Rib Arch", "Arco de Costelas", "Arco de Costillas"), "arch", "rib_bone", "pickaxe", "bone", "SAND")
add("tooth_totem", ("Tooth Totem", "Totem de Dentes", "Tótem de Dientes"), "log", ("tooth_totem", "tooth_totem_top"),
    "axe", "wood", "WOOD")
add("bone_pile", ("Bone Pile", "Monte de Ossos", "Montón de Huesos"), "carpet", "bone_pile", "shovel", "bone_loose",
    "SAND")
add("feather_bundle", ("Feather Bundle", "Feixe de Penas", "Haz de Plumas"), "log",
    ("feather_bundle", "feather_bundle_top"), "hoe", "feathers", "COLOR_BROWN")

# ------------------------------------------------------------- family: utilities (phase 7)
def box(a, b, tex, collide=True, rotation=None, faces=None):
    """One model element: tex is a texture or (side, top); collide=False keeps it out of the block's shape (flames,
    ropes); faces limits the faces drawn (flat planes)."""
    return {"from": a, "to": b, "tex": tex, "collide": collide, "rotation": rotation, "faces": faces}


def fire_planes(y0, y1, tex="minecraft:block/campfire_fire"):
    """Two crossed planes of flame, like the campfire's fire."""
    return [box([0.8, y0, 8], [15.2, y1, 8], tex, False, {"origin": [8, 8, 8], "axis": "y", "angle": a, "rescale": True},
                ("north", "south")) for a in (45, -45)]


LOG, LOG_TOP, STRIPPED = "araucaria_log", "araucaria_log_top", "stripped_araucaria_log"
PROPS = {}  # block id: model elements (north facing)
for _tid, _names in (("bone", ("Bone Torch", "Tocha de Osso", "Antorcha de Hueso")),
                     ("resin", ("Resin Torch", "Tocha de Resina", "Antorcha de Resina")),
                     ("reed", ("Reed Torch", "Tocha de Junco", "Antorcha de Junco"))):
    add(f"{_tid}_torch", _names, "torch", f"{_tid}_torch", "axe", "torch", "WOOD")
    add(f"{_tid}_wall_torch", _names, "wall_torch", f"{_tid}_torch", "axe", "torch", "WOOD", f"{_tid}_torch")
add("fat_lamp", ("Stone Fat Lamp", "Lamparina de Pedra com Gordura", "Lámpara de Piedra con Grasa"), "prop", None,
    "pickaxe", "lamp", "STONE")
PROPS["fat_lamp"] = [box([5, 0, 5], [11, 3, 11], ("limestone", "fat_lamp_top")),
                     box([7.5, 3, 7.5], [8.5, 5, 8.5], "lamp_flame", False)]
add("stone_hearth", ("Stone Ring Hearth", "Fogueira de Pedras", "Hogar de Piedras"), "hearth", None, "pickaxe",
    "hearth", "STONE")
PROPS["stone_hearth"] = [box([0, 0, 0], [16, 3, 3], "limestone"), box([0, 0, 13], [16, 3, 16], "limestone"),
                         box([0, 0, 3], [3, 3, 13], "limestone"), box([13, 0, 3], [16, 3, 13], "limestone"),
                         box([3, 0, 3], [13, 1, 13], "hearth_ash"), box([2, 1, 7], [14, 3, 9], (LOG, LOG_TOP)),
                         box([7, 1, 2], [9, 3, 14], (LOG, LOG_TOP))] + fire_planes(1, 15)
add("meat_drying_rack", ("Meat Drying Rack", "Varal de Secar Carne", "Secadero de Carne"), "prop", None, "axe",
    "prop_wood", "WOOD")
PROPS["meat_drying_rack"] = [box([1, 0, 7], [3, 14, 9], (STRIPPED, LOG_TOP)), box([13, 0, 7], [15, 14, 9], (STRIPPED, LOG_TOP)),
                             box([3, 12, 7.5], [13, 13, 8.5], STRIPPED),
                             box([4, 6, 7.5], [6, 12, 8.5], "dried_meat", False),
                             box([7, 7, 7.5], [9, 12, 8.5], "dried_meat", False),
                             box([10, 5, 7.5], [12, 12, 8.5], "dried_meat", False)]
add("mortar_and_pestle", ("Mortar and Pestle", "Pilão", "Mortero"), "prop", None, "pickaxe", "prop_stone", "STONE")
PROPS["mortar_and_pestle"] = [box([4, 0, 4], [12, 5, 12], ("limestone", "hearth_ash")),
                              box([8, 4, 7], [10, 12, 9], STRIPPED, False,
                                  {"origin": [9, 4, 8], "axis": "z", "angle": -22.5})]
add("quern_stone", ("Quern Stone", "Mó de Pedra", "Molino de Piedra"), "prop", None, "pickaxe", "prop_stone", "STONE")
PROPS["quern_stone"] = [box([1, 0, 1], [15, 4, 15], "quartzite"), box([3, 4, 3], [13, 7, 13], "quartzite"),
                        box([11, 7, 7], [12, 11, 8], STRIPPED, False)]
add("firewood_pile", ("Firewood Pile", "Pilha de Lenha", "Pila de Leña"), "log", ("firewood_pile", "firewood_pile_end"),
    "axe", "wood", "WOOD")
add("stone_basin", ("Stone Water Basin", "Bacia de Pedra", "Pila de Piedra"), "prop", None, "pickaxe", "prop_stone",
    "STONE")
PROPS["stone_basin"] = [box([1, 0, 1], [15, 2, 15], "limestone"), box([1, 2, 1], [15, 8, 3], "limestone"),
                        box([1, 2, 13], [15, 8, 15], "limestone"), box([1, 2, 3], [3, 8, 13], "limestone"),
                        box([13, 2, 3], [15, 8, 13], "limestone"),
                        box([3, 6.5, 3], [13, 6.5, 13], "basin_water", False, faces=("up",))]
BEDS = {  # bed id: names, material, foot elements, head elements (head toward north)
    "straw_bed": (("Straw Bed", "Cama de Palha", "Cama de Paja"),
                  [box([0, 0, 0], [16, 4, 16], ("thatch", "thatch_top"))],
                  [box([0, 0, 0], [16, 4, 16], ("thatch", "thatch_top")),
                   box([2, 4, 1], [14, 6, 6], ("thatch", "thatch_top"))]),
    "hide_bed": (("Hide Bed", "Cama de Couro", "Cama de Cuero"),
                 [box([0, 0, 0], [16, 3, 16], (STRIPPED, LOG_TOP)), box([1, 3, 0], [15, 5, 15], "hide_bedroll")],
                 [box([0, 0, 0], [16, 3, 16], (STRIPPED, LOG_TOP)), box([1, 3, 1], [15, 5, 16], "hide_bedroll"),
                  box([2, 5, 2], [14, 7, 6], "hide_bedroll")]),
    "hammock": (("Hammock", "Rede de Dormir", "Hamaca"),
                [box([7, 0, 14], [9, 10, 16], (STRIPPED, LOG_TOP)), box([1, 5, 0], [15, 6, 14], "hammock_cloth")],
                [box([7, 0, 0], [9, 10, 2], (STRIPPED, LOG_TOP)), box([1, 5, 2], [15, 6, 16], "hammock_cloth")]),
}
for _bid, (_names, _foot, _head) in BEDS.items():
    add(_bid, _names, "bed", None, "axe", "bed", "COLOR_BROWN")
add("tanning_rack", ("Tanning Rack", "Cavalete de Curtir Couro", "Bastidor de Curtir"), "prop", None, "axe",
    "prop_wood", "WOOD")
PROPS["tanning_rack"] = [box([0, 0, 7], [2, 16, 9], (STRIPPED, LOG_TOP)), box([14, 0, 7], [16, 16, 9], (STRIPPED, LOG_TOP)),
                         box([2, 14, 7], [14, 16, 9], STRIPPED), box([2, 1, 7], [14, 3, 9], STRIPPED),
                         box([2, 3, 7.5], [14, 14, 8.5], "hide_screen")]
add("flint_knapping_bench", ("Flint Knapping Bench", "Bancada de Lascar Sílex", "Banco de Tallar Sílex"), "prop", None,
    "axe", "prop_wood", "WOOD")
PROPS["flint_knapping_bench"] = [box([2, 0, 2], [14, 10, 14], (LOG, LOG_TOP)),
                                 box([4, 10, 5], [7, 11, 8], "flint", False), box([9, 10, 8], [12, 12, 11], "quartzite", False)]
for _fired, _names in ((False, ("Raw Clay Pot", "Pote de Barro Cru", "Vasija de Barro Crudo")),
                       (True, ("Fired Clay Pot", "Pote de Barro Queimado", "Vasija de Barro Cocido"))):
    _pid = "fired_clay_pot" if _fired else "raw_clay_pot"
    add(_pid, _names, "prop", None, "pickaxe", "clay", "TERRACOTTA_ORANGE" if _fired else "CLAY")
    PROPS[_pid] = [box([4, 0, 4], [12, 9, 12], (_pid, _pid)), box([5, 9, 5], [11, 11, 11], (_pid, _pid)),
                   box([4, 11, 4], [12, 12, 12], (_pid, f"{_pid}_top"))]
add("log_feeding_trough", ("Log Feeding Trough", "Cocho de Tronco", "Comedero de Tronco"), "prop", None, "axe",
    "prop_wood", "WOOD")
PROPS["log_feeding_trough"] = [box([0, 0, 2], [16, 2, 14], (LOG, STRIPPED)), box([0, 2, 2], [16, 7, 4], (LOG, STRIPPED)),
                               box([0, 2, 12], [16, 7, 14], (LOG, STRIPPED)), box([0, 2, 4], [2, 7, 12], (LOG_TOP, STRIPPED)),
                               box([14, 2, 4], [16, 7, 12], (LOG_TOP, STRIPPED))]
for _nid, _names, _mat, _tex in (("straw_nest", ("Straw Nest", "Ninho de Palha", "Nido de Paja"), "nest",
                                  ("thatch", "thatch_top")),
                                 ("sand_nest", ("Sand Nest", "Ninho de Areia", "Nido de Arena"), "sand_nest",
                                  "minecraft:block/sand")):
    add(_nid, _names, "prop", None, "shovel" if _mat == "sand_nest" else "hoe", _mat, "SAND")
    PROPS[_nid] = [box([1, 0, 1], [15, 1, 15], _tex), box([0, 1, 0], [16, 4, 3], _tex), box([0, 1, 13], [16, 4, 16], _tex),
                   box([0, 1, 3], [3, 4, 13], _tex), box([13, 1, 3], [16, 4, 13], _tex)]
add("sharpened_stakes", ("Sharpened Stakes", "Estacas Pontudas", "Estacas Afiladas"), "spikes", "sharpened_stakes",
    "axe", "spikes", "WOOD")
add("bone_spikes", ("Bone Spikes", "Espetos de Osso", "Púas de Hueso"), "spikes", "bone_spikes", "pickaxe", "spikes",
    "SAND")
add("pit_trap_cover", ("Pit Trap Cover", "Cobertura de Armadilha", "Cubierta de Trampa"), "prop", None, "hoe",
    "pit_cover", "PLANT")
PROPS["pit_trap_cover"] = [box([0, 14, 0], [16, 16, 16], "pit_trap_cover")]
add("menhir", ("Menhir", "Menir", "Menhir"), "prop", None, "pickaxe", "prop_stone", "STONE")
PROPS["menhir"] = [box([3, 0, 4], [13, 16, 12], ("menhir", "menhir_top"))]
for _face, _names in (("raptor", ("Raptor Totem", "Totem de Raptor", "Tótem de Raptor")),
                      ("rex", ("Tyrannosaurus Totem", "Totem de Tiranossauro", "Tótem de Tiranosaurio")),
                      ("pterosaur", ("Pterosaur Totem", "Totem de Pterossauro", "Tótem de Pterosaurio"))):
    add(f"{_face}_totem", _names, "facing", (f"{_face}_totem_front", "totem_side"), "axe", "prop_wood", "WOOD")
add("hide_drum", ("Hide Drum", "Tambor de Couro", "Tambor de Cuero"), "drum", None, "axe", "prop_wood", "WOOD")
PROPS["hide_drum"] = [box([3, 0, 3], [13, 10, 13], ("drum_side", "drum_head"))]
add("bone_wind_chimes", ("Bone Wind Chimes", "Móbile de Ossos", "Carillón de Huesos"), "chimes", None, "pickaxe",
    "chimes", "SAND")
PROPS["bone_wind_chimes"] = [box([3, 15, 7.5], [13, 16, 8.5], STRIPPED)] + [
    box([x, y0, 7.5], [x + 1, 15, 8.5], "fiber_net", False) for x, y0 in ((4, 13), (7, 12), (10, 13))] + [
    box([x, y0, 7.5], [x + 1, y1, 8.5], "rib_bone", False) for x, y0, y1 in ((4, 6, 13), (7, 4, 12), (10, 7, 13))]
add("hanging_basket", ("Hanging Basket", "Cesto Pendurado", "Cesta Colgante"), "prop", None, "axe", "wicker", "WOOD")
PROPS["hanging_basket"] = [box([7.5, 10, 7.5], [8.5, 16, 8.5], STRIPPED, False), box([4, 2, 4], [12, 8, 12], "wicker_block"),
                           box([5, 8, 5], [11, 10, 11], "bracken", False)]
add("wicker_basket", ("Wicker Basket", "Cesto de Vime", "Cesto de Mimbre"), "basket", None, "axe", "wicker", "WOOD")
PROPS["wicker_basket"] = [box([2, 0, 2], [14, 12, 14], ("wicker_block", "wicker_basket_top"))]
NO_ITEM_KINDS = ("wall_torch",)

# ------------------------------------------------------------- family: Cretaceous soils (none of them is a vanilla soil)
add("fern_litter", ("Fern Litter", "Serrapilheira de Samambaia", "Hojarasca de Helecho"), "column",
    ("fern_litter_side", "fern_litter"), "shovel", "soil", "DIRT")
add("needle_litter", ("Needle Litter", "Serrapilheira de Acículas", "Pinocha"), "column",
    ("needle_litter_side", "needle_litter"), "shovel", "soil", "DIRT")
add("cracked_mud", ("Cracked Mud", "Lama Rachada", "Barro Agrietado"), "cube", "cracked_mud", "shovel", "earth", "DIRT")
add("volcanic_ash", ("Volcanic Ash", "Cinza Vulcânica", "Ceniza Volcánica"), "cube", "volcanic_ash", "shovel", "ash",
    "COLOR_LIGHT_GRAY")
add("volcanic_ash_layer", ("Volcanic Ash Layer", "Camada de Cinza Vulcânica", "Capa de Ceniza Volcánica"), "carpet",
    "volcanic_ash", "shovel", "ash", "COLOR_LIGHT_GRAY")
add("peat", ("Peat", "Turfa", "Turba"), "cube", "peat", "shovel", "soil", "COLOR_BROWN")
add("lateritic_soil", ("Lateritic Soil", "Solo Laterítico", "Suelo Laterítico"), "cube", "lateritic_soil", "shovel",
    "soil", "TERRACOTTA_RED")
add("salt_crust", ("Salt Crust", "Crosta de Sal", "Costra de Sal"), "cube", "salt_crust", "pickaxe", "salt", "SNOW")

# ------------------------------------------------------------- family: amber and resin
# ordinary fossil resin (raw_amber of the science items); the glowing Temporal Amber of the story is not a block
add("amber_block", ("Block of Amber", "Bloco de Âmbar", "Bloque de Ámbar"), "cube", "amber_block", "pickaxe", "amber",
    "COLOR_ORANGE")
add_shapes("polished_amber", ("Polished Amber", "Âmbar Polido", "Ámbar Pulido"), "polished_amber", "pickaxe", "amber",
           "COLOR_ORANGE", ("stairs", "slab", "wall"))
add("amber_mosaic", ("Amber Mosaic", "Mosaico de Âmbar", "Mosaico de Ámbar"), "cube", "amber_mosaic", "pickaxe", "amber",
    "COLOR_ORANGE")
for _kind, _names in (("insect", ("Amber with Insect", "Âmbar com Inseto", "Ámbar con Insecto")),
                      ("feather", ("Amber with Feather", "Âmbar com Pena", "Ámbar con Pluma")),
                      ("leaf", ("Amber with Leaf", "Âmbar com Folha", "Ámbar con Hoja"))):
    add(f"amber_with_{_kind}", _names, "cube", f"amber_with_{_kind}", "pickaxe", "amber", "COLOR_ORANGE")
add("resin_block", ("Resin Block", "Bloco de Resina", "Bloque de Resina"), "cube", "resin_block", "axe", "resin",
    "COLOR_YELLOW")
add("amber_lantern", ("Amber Lantern", "Lanterna de Âmbar", "Farol de Ámbar"), "prop", None, "pickaxe", "amber_light",
    "COLOR_ORANGE")
PROPS["amber_lantern"] = [box([5, 0, 5], [11, 8, 11], ("amber_lantern", "amber_lantern_top")),
                          box([7, 8, 7], [9, 10, 9], "amber_lantern_top", False)]

LANG = {"en_us": {}, "pt_br": {}, "es_es": {}}
for _bid, _row in BLOCKS.items():
    for _code, _name in zip(("en_us", "pt_br", "es_es"), _row["names"]):
        LANG[_code][f"block.{NS}.{_bid}"] = _name
for _code, _name in zip(("en_us", "pt_br", "es_es"), BLOCKS["wicker_basket"]["names"]):
    LANG[_code][f"container.{NS}.wicker_basket"] = _name
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


# Random turn per block, like vanilla dirt and stone (the game picks one variant per position), so a texture does not
# repeat over a big floor or wall. FREE: the 16 x/y turns of netherrack (isotropic textures). BEDDED: only mirrored
# and turned 180 (layered rock and courses of stone keep running level). TOP: the top face turns (columns, carpets).
FREE_TURN = ({"lateritic_soil", "volcanic_ash", "peat", "packed_earth_floor", "cracked_mud", "salt_crust", "amber_block",
              "laterite", "chalk", "quartzite", "conglomerate", "flint_nodules"} | {f"{r}_flagstone" for r in ROCKS})
BEDDED_TURN = ({"shale", "limestone", "gneiss"} | {f"{r}_stacked" for r in ROCKS} | {f"mossy_{r}_stacked" for r in ROCKS})
TOP_TURN = {"fern_litter", "needle_litter"} | {f"{r}_pebbles" for r in ROCKS}


def turned(bid, tex=None):
    """The blockstate variant(s) of a full block: a list the game picks from at random, or the one model."""
    if bid in FREE_TURN:
        return [variant(bid, x, y) for x in (0, 90, 180, 270) for y in (0, 90, 180, 270)]
    if bid in BEDDED_TURN:
        model(f"{bid}_mirrored", "minecraft:block/cube_mirrored_all", all=t(tex))
        return [variant(name, 0, y) for name in (bid, f"{bid}_mirrored") for y in (0, 180)]
    if bid in TOP_TURN:
        return [variant(bid, 0, y) for y in (0, 90, 180, 270)]
    return variant(bid)


# ------------------------------------------------------------- models and blockstates, per kind
def gen_cube(bid, tex):
    model(bid, "minecraft:block/cube_all", all=t(tex))
    write(f"{A}/blockstates/{bid}.json", {"variants": {"": turned(bid, tex)}})
    return m(bid)


def gen_column(bid, tex):
    side, end = tex
    model(bid, "minecraft:block/cube_column", side=t(side), end=t(end))
    write(f"{A}/blockstates/{bid}.json", {"variants": {"": turned(bid)}})
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
    write(f"{A}/blockstates/{bid}.json", {"variants": {"": turned(bid)}})
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


def gen_facing(bid, tex):
    """A full block with a picture on its front, turned towards the player who placed it."""
    front, side = tex
    model(bid, "minecraft:block/orientable", front=t(front), side=t(side), top=t(side))
    write(f"{A}/blockstates/{bid}.json", {"variants": {
        f"facing={f}": variant(bid, y=y) for f, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270))}})
    return m(bid)


def gen_eave(bid, tex):
    """A thin sheet of roofing tilted 22.5 degrees, sloping down towards its facing: the overhang of a roof."""
    full, edge = [0, 0, 16, 16], [0, 0, 16, 3]
    faces = {d: {"uv": full if d in ("up", "down") else edge, "texture": "#t"}
             for d in ("north", "south", "east", "west", "up", "down")}
    write(f"{A}/models/block/{bid}.json", {
        "parent": "minecraft:block/block", "textures": {"t": t(tex), "particle": t(tex)},
        "elements": [{"from": [0, 11, 0], "to": [16, 14, 16], "faces": faces,
                      "rotation": {"origin": [8, 12.5, 8], "axis": "x", "angle": -22.5, "rescale": True}}]})
    write(f"{A}/blockstates/{bid}.json", {"variants": {
        f"facing={f}": variant(bid, y=y) for f, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270))}})
    return m(bid)


def facing_states(bid):
    write(f"{A}/blockstates/{bid}.json", {"variants": {
        f"facing={f}": variant(bid, y=y) for f, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270))}})


def gen_trophy(bid, tex):
    """A skull mounted on a hewn plank plaque, hung on the wall behind it (the skull is a cutout sprite)."""
    write(f"{A}/models/block/{bid}.json", {
        "parent": "minecraft:block/block",
        "textures": {"skull": t(tex), "plaque": t("araucaria_hewn_planks"), "particle": t("araucaria_hewn_planks")},
        "elements": [
            {"from": [3, 3, 14], "to": [13, 13, 16], "faces": {
                d: {"texture": "#plaque"} for d in ("north", "south", "east", "west", "up", "down")}},
            {"from": [0, 0, 13.5], "to": [16, 16, 13.5], "shade": False, "faces": {
                "north": {"uv": [0, 0, 16, 16], "texture": "#skull"},
                "south": {"uv": [16, 0, 0, 16], "texture": "#skull"}}}]})
    facing_states(bid)
    return m(bid)


def gen_arch(bid, tex):
    """Two ribs standing up and meeting overhead: posts, a lintel and the curve of the corners."""
    boxes = [([0, 0, 6], [3, 16, 10]), ([13, 0, 6], [16, 16, 10]), ([3, 13, 6], [13, 16, 10]),
             ([3, 10, 6], [5, 13, 10]), ([11, 10, 6], [13, 13, 10])]
    write(f"{A}/models/block/{bid}.json", {
        "parent": "minecraft:block/block", "textures": {"t": t(tex), "particle": t(tex)},
        "elements": [{"from": a, "to": b, "faces": {
            d: {"texture": "#t"} for d in ("north", "south", "east", "west", "up", "down")}} for a, b in boxes]})
    facing_states(bid)
    return m(bid)


def element_model(name, elements):
    """A block model from PROPS-style elements; each texture gets a key (t0, t1...), the first is the particle."""
    keys = {}

    def key(tex):
        ref = tex if ":" in tex else t(tex)
        keys.setdefault(ref, f"t{len(keys)}")
        return "#" + keys[ref]
    out = []
    for e in elements:
        side, top = e["tex"] if isinstance(e["tex"], tuple) else (e["tex"], e["tex"])
        faces = e["faces"] or ("north", "south", "east", "west", "up", "down")
        el = {"from": e["from"], "to": e["to"],
              "faces": {d: {"texture": key(top if d in ("up", "down") else side)} for d in faces}}
        if e["rotation"]:
            el["rotation"] = e["rotation"]
        if e["faces"]:
            el["shade"] = False
        out.append(el)
    textures = {k: ref for ref, k in keys.items()}
    textures["particle"] = textures["t0"]
    write(f"{A}/models/block/{name}.json", {"parent": "minecraft:block/block", "textures": textures, "elements": out})


def gen_prop(bid, tex):
    element_model(bid, PROPS[bid])
    facing_states(bid)
    return m(bid)


def gen_torch(bid, tex):
    model(bid, "minecraft:block/template_torch", torch=t(tex))
    write(f"{A}/blockstates/{bid}.json", {"variants": {"": variant(bid)}})
    return None


def gen_wall_torch(bid, tex):
    model(bid, "minecraft:block/template_torch_wall", torch=t(tex))
    write(f"{A}/blockstates/{bid}.json", {"variants": {
        f"facing={f}": variant(bid, y=y) for f, y in (("east", 0), ("south", 90), ("west", 180), ("north", 270))}})
    return None


def gen_spikes(bid, tex):
    model(bid, "minecraft:block/cross", cross=t(tex))
    write(f"{A}/blockstates/{bid}.json", {"variants": {"": variant(bid)}})
    return None


def gen_bed(bid, tex):
    """Two parts, foot and head (the head lies towards the bed's facing), turned like the vanilla bed."""
    _, foot, head = BEDS[bid]
    element_model(f"{bid}_foot", foot)
    element_model(f"{bid}_head", head)
    variants = {}
    for f, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270)):
        for part in ("foot", "head"):
            variants[f"facing={f},part={part}"] = variant(f"{bid}_{part}", y=y)
    write(f"{A}/blockstates/{bid}.json", {"variants": variants})
    return m(f"{bid}_head")


def gen_climber(bid, tex):
    """Hangs on the side of a block or under a ceiling like a vine, and can be climbed (nets)."""
    write(f"{A}/models/block/{bid}.json", {
        "parent": "minecraft:block/block", "ambientocclusion": False,
        "textures": {"texture": t(tex), "particle": t(tex)},
        "elements": [{"from": [0, 0, 0.8], "to": [16, 16, 0.8], "shade": False, "faces": {
            "north": {"uv": [16, 0, 0, 16], "texture": "#texture"}, "south": {"uv": [0, 0, 16, 16], "texture": "#texture"}}}]})
    rot = {"north": {}, "east": {"y": 90}, "south": {"y": 180}, "west": {"y": 270}, "up": {"x": 270}}
    parts = [{"when": {face: "true"}, "apply": variant(bid, r.get("x", 0), r.get("y", 0), uvlock=True)}
             for face, r in rot.items()]
    write(f"{A}/blockstates/{bid}.json", {"multipart": parts})
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
       "sapling": gen_sapling, "fence_gate": gen_fence_gate, "door": gen_door, "trapdoor": gen_trapdoor,
       "facing": gen_facing, "eave": gen_eave, "climber": gen_climber, "trophy": gen_trophy, "arch": gen_arch,
       "torch": gen_torch, "wall_torch": gen_wall_torch, "spikes": gen_spikes, "bed": gen_bed, "prop": gen_prop,
       "hearth": gen_prop, "drum": gen_prop, "chimes": gen_prop, "basket": gen_prop}


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


def loot_part(bid, prop, value):
    """Drops the block only from the part where prop = value (beds: the head)."""
    write(f"{D}/loot_tables/blocks/{bid}.json", {"type": "minecraft:block", "pools": [{
        "rolls": 1, "bonus_rolls": 0, "entries": [{"type": "minecraft:item", "name": f"{NS}:{bid}", "conditions": [
            {"condition": "minecraft:block_state_property", "block": f"{NS}:{bid}", "properties": {prop: value}}]}],
        "conditions": [{"condition": "minecraft:survives_explosion"}]}]})


def loot_as(bid, item):
    write(f"{D}/loot_tables/blocks/{bid}.json", {"type": "minecraft:block", "pools": [{
        "rolls": 1, "bonus_rolls": 0, "entries": [{"type": "minecraft:item", "name": f"{NS}:{item}"}],
        "conditions": [{"condition": "minecraft:survives_explosion"}]}]})


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
    # earth and plaster
    shapeless("cross_braced_wattle", [f"{NS}:wattle_and_daub", "minecraft:stick", "minecraft:stick"], "cross_braced_wattle")
    shapeless("timber_framed_wattle", [f"{NS}:wattle_and_daub", "#minecraft:logs"], "timber_framed_wattle")
    shapeless("whitewashed_wattle", [f"{NS}:wattle_and_daub", f"{NS}:chalk_pebbles"], "whitewashed_wattle")
    shapeless("rammed_earth", ["minecraft:dirt", "minecraft:dirt", "minecraft:gravel", "minecraft:clay_ball"],
              "rammed_earth", 2)
    shapeless("packed_earth_floor", ["minecraft:dirt"] * 4 + [f"{NS}:thatch"], "packed_earth_floor", 4)
    shapeless("clay_plaster", ["minecraft:clay_ball", "minecraft:clay_ball", "minecraft:sand", "minecraft:wheat"],
              "clay_plaster", 2)
    for pid, pigment in (("red_ochre_plaster", f"{NS}:laterite_pebbles"), ("yellow_ochre_plaster", "minecraft:yellow_dye"),
                         ("charcoal_plaster", "minecraft:charcoal"), ("chalk_whitewash", f"{NS}:chalk_pebbles")):
        shapeless(pid, [f"{NS}:clay_plaster", pigment], pid)
    first = "cave_painting_handprint"  # charcoal on limestone; the stonecutter turns it into any other picture
    shapeless(first, [f"{NS}:limestone", "minecraft:charcoal"], first)
    for name in PAINTINGS:
        if f"cave_painting_{name}" != first:
            stonecut(first, f"cave_painting_{name}")
    # roofs and weaving
    shaped("thatch_eave", ["T", "T"], {"T": f"{NS}:thatch"}, "thatch_eave", 4)
    for rid, (_, _, plant) in ROOFS.items():
        shaped(rid, ["PP", "PP"], {"P": f"{NS}:{plant}"}, rid, 2)
        shaped(f"{rid}_eave", ["T", "T"], {"T": f"{NS}:{rid}"}, f"{rid}_eave", 4)
    rush, stick = f"{NS}:rush", "minecraft:stick"
    shaped("wicker_block", ["RSR", "SRS", "RSR"], {"R": rush, "S": stick}, "wicker_block", 2)
    shaped("wicker_panel", ["SRS", "SRS"], {"R": rush, "S": stick}, "wicker_panel", 6)
    shaped("woven_fence", ["SWS", "SWS"], {"W": f"{NS}:wicker_block", "S": stick}, "woven_fence", 3)
    shaped("wicker_door", ["WW", "WW", "WW"], {"W": f"{NS}:wicker_block"}, "wicker_door", 3)
    shaped("wicker_trapdoor", ["WWW", "WWW"], {"W": f"{NS}:wicker_block"}, "wicker_trapdoor", 2)
    shaped("reed_mat", ["RR"], {"R": rush}, "reed_mat", 3)
    shaped("reed_bundle", ["RRR", "RRR", "RRR"], {"R": rush}, "reed_bundle")
    shaped("rope_coil", ["SSS", "SSS", "SSS"], {"S": "minecraft:string"}, "rope_coil")
    shaped("fiber_net", ["S S", " S ", "S S"], {"S": "minecraft:string"}, "fiber_net", 4)
    # hide, bone, trophies and fossils
    for hid, (_, source) in HIDES.items():
        hide = f"{NS}:{source}" if source else "minecraft:leather"
        if hid == "tanned_hide":  # tannin from bark
            shapeless("tanned_hide_frame", [f"{NS}:rawhide_frame", "#minecraft:logs"], "tanned_hide_frame")
            shapeless("tanned_hide_panel", [f"{NS}:hide_screen", "#minecraft:logs"], "tanned_hide_panel")
            continue
        shaped(f"{hid}_frame", ["SHS", "HHH", "SHS"], {"S": "minecraft:stick", "H": hide}, f"{hid}_frame", 2)
        if f"{hid}_panel" in BLOCKS:
            shaped(f"{hid}_panel", ["SHS", "SHS"], {"S": "minecraft:stick", "H": hide}, f"{hid}_panel", 4)
    for sid in SPECIES:
        shaped(f"{sid}_hide_rug", ["HH"], {"H": f"{NS}:{sid}_hide"}, f"{sid}_hide_rug", 2)
        shapeless(f"{sid}_skull_trophy", [f"{NS}:{sid}_fossil", "#minecraft:planks"], f"{sid}_skull_trophy")
        rock = ROCK_VARIANTS[SKULL_ROCK.get(sid, "limestone")]["natural"]
        shapeless(f"{sid}_skull_fossil", [f"{NS}:{sid}_fossil", f"{NS}:{rock}"], f"{sid}_skull_fossil")
    shaped("bone_fence_gate", ["BKB", "BKB"], {"B": "minecraft:bone", "K": "minecraft:bone_block"}, "bone_fence_gate")
    shaped("ossuary_wall", ["KK", "KK"], {"K": "minecraft:bone_block"}, "ossuary_wall", 4)
    shaped("rib_arch", ["BBB", "B B", "B B"], {"B": "minecraft:bone"}, "rib_arch", 2)
    shaped("tooth_totem", ["T", "L", "L"], {"T": f"{NS}:rex_tooth", "L": "#minecraft:logs"}, "tooth_totem", 2)
    shaped("bone_pile", ["BB"], {"B": "minecraft:bone"}, "bone_pile")
    shaped("feather_bundle", ["FFF", "FFF", "FFF"], {"F": "minecraft:feather"}, "feather_bundle")
    # utilities
    charcoal, logs, stick = "minecraft:charcoal", "#minecraft:logs", "minecraft:stick"
    shaped("bone_torch", ["L", "B"], {"L": "minecraft:leather", "B": "minecraft:bone"}, "bone_torch", 4)
    shaped("resin_torch", ["C", "L", "S"], {"C": charcoal, "L": f"{NS}:araucaria_log", "S": stick}, "resin_torch", 4)
    shaped("reed_torch", ["C", "R", "R"], {"C": charcoal, "R": f"{NS}:rush"}, "reed_torch", 4)
    shapeless("fat_lamp", [f"{NS}:limestone", "minecraft:beef", "minecraft:string"], "fat_lamp")
    shaped("stone_hearth", [" L ", "LFL", "SSS"], {"L": logs, "F": "minecraft:flint", "S": "minecraft:cobblestone"},
           "stone_hearth")
    shaped("meat_drying_rack", ["SSS", "STS", "S S"], {"S": stick, "T": "minecraft:string"}, "meat_drying_rack")
    shaped("mortar_and_pestle", ["R S", "RRR"], {"R": f"{NS}:limestone", "S": stick}, "mortar_and_pestle")
    shaped("quern_stone", ["S", "Q", "Q"], {"S": stick, "Q": f"{NS}:quartzite"}, "quern_stone")
    shaped("firewood_pile", ["LLL"], {"L": logs}, "firewood_pile", 3)
    shaped("stone_basin", ["R R", "RRR"], {"R": f"{NS}:limestone"}, "stone_basin")
    shaped("straw_bed", ["TTT", "SSS"], {"T": f"{NS}:thatch", "S": stick}, "straw_bed")
    shaped("hide_bed", ["HHH", "LLL"], {"H": "minecraft:leather", "L": logs}, "hide_bed")
    shaped("hammock", ["S S", "NNN"], {"S": stick, "N": f"{NS}:fiber_net"}, "hammock")
    shaped("tanning_rack", ["SSS", "SLS", "S S"], {"S": stick, "L": "minecraft:leather"}, "tanning_rack")
    shaped("flint_knapping_bench", ["F", "L"], {"F": "minecraft:flint", "L": logs}, "flint_knapping_bench")
    shaped("raw_clay_pot", ["C C", "C C", "CCC"], {"C": "minecraft:clay_ball"}, "raw_clay_pot")
    write(f"{D}/recipes/fired_clay_pot.json", {
        "type": "minecraft:smelting", "category": "blocks", "ingredient": {"item": f"{NS}:raw_clay_pot"},
        "result": f"{NS}:fired_clay_pot", "experience": 0.1, "cookingtime": 200})
    shaped("log_feeding_trough", ["L L", "LLL"], {"L": logs}, "log_feeding_trough")
    shaped("straw_nest", ["T T", "TTT"], {"T": f"{NS}:thatch"}, "straw_nest")
    shaped("sand_nest", ["S S", "SSS"], {"S": "minecraft:sand"}, "sand_nest")
    shaped("sharpened_stakes", ["SFS"], {"S": stick, "F": "minecraft:flint"}, "sharpened_stakes", 2)
    shaped("bone_spikes", ["BFB"], {"B": "minecraft:bone", "F": "minecraft:flint"}, "bone_spikes", 2)
    shaped("pit_trap_cover", ["LSL"], {"L": "#minecraft:leaves", "S": stick}, "pit_trap_cover", 2)
    shaped("menhir", ["G", "G"], {"G": f"{NS}:gneiss"}, "menhir")
    shapeless("raptor_totem", [logs, "minecraft:flint"], "raptor_totem")
    shapeless("rex_totem", [logs, f"{NS}:rex_tooth"], "rex_totem")
    shapeless("pterosaur_totem", [logs, "minecraft:feather"], "pterosaur_totem")
    shaped("hide_drum", ["H", "L"], {"H": "minecraft:leather", "L": logs}, "hide_drum")
    shaped("bone_wind_chimes", ["SSS", "BTB"], {"S": stick, "B": "minecraft:bone", "T": "minecraft:string"},
           "bone_wind_chimes")
    shaped("hanging_basket", ["T", "W", "F"], {"T": "minecraft:string", "W": f"{NS}:wicker_block", "F": f"{NS}:bracken"},
           "hanging_basket")
    shaped("wicker_basket", ["R R", "RRR"], {"R": f"{NS}:rush"}, "wicker_basket")
    # Cretaceous soils
    shapeless("fern_litter", ["minecraft:dirt", "minecraft:dirt", f"{NS}:bracken", f"{NS}:bracken"], "fern_litter", 2)
    shapeless("needle_litter", ["minecraft:dirt", "minecraft:dirt", f"{NS}:metasequoia_leaves"], "needle_litter", 2)
    write(f"{D}/recipes/cracked_mud.json", {
        "type": "minecraft:smelting", "category": "blocks", "ingredient": {"item": "minecraft:mud"},
        "result": f"{NS}:cracked_mud", "experience": 0.1, "cookingtime": 200})
    shapeless("volcanic_ash", ["minecraft:gravel", "minecraft:charcoal"], "volcanic_ash", 2)
    shaped("volcanic_ash_layer", ["AAA"], {"A": f"{NS}:volcanic_ash"}, "volcanic_ash_layer", 6)
    shapeless("peat", ["minecraft:mud", f"{NS}:liverwort", f"{NS}:liverwort"], "peat")
    shapeless("lateritic_soil", ["minecraft:dirt", "minecraft:dirt", f"{NS}:laterite_pebbles"], "lateritic_soil", 2)
    shapeless("salt_crust", ["minecraft:sand", "minecraft:sand", "minecraft:bone_meal"], "salt_crust", 2)
    # amber and resin
    shaped("amber_block", ["AAA", "AAA", "AAA"], {"A": f"{NS}:raw_amber"}, "amber_block")
    shapeless("raw_amber_from_amber_block", [f"{NS}:amber_block"], "raw_amber", 9)
    for cut in ("polished_amber", "amber_mosaic", "amber_with_insect", "amber_with_feather", "amber_with_leaf"):
        stonecut("amber_block", cut)
    shaped("polished_amber", ["AA", "AA"], {"A": f"{NS}:amber_block"}, "polished_amber", 4)
    shaped("resin_block", ["RR", "RR"], {"R": f"{NS}:resin_jar"}, "resin_block")
    shaped("amber_lantern", [" B ", "BAB", " B "], {"B": "minecraft:bone", "A": f"{NS}:polished_amber"}, "amber_lantern")
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
        if tag not in BLOCK_ONLY_TAGS:
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
             "tall_plant": "tallPlant", "water_plant": "waterPlant", "multiface": "multiface", "facing": "facing",
             "eave": "eave", "climber": "climber", "trophy": "trophy", "arch": "arch", "torch": "torch",
             "wall_torch": "wallTorch", "spikes": "spikes", "bed": "bed", "prop": "prop", "hearth": "hearth",
             "drum": "drum", "chimes": "chimes", "basket": "basket"}
BOX_KINDS = ("prop", "hearth", "drum", "chimes", "basket")
# drawn with transparent pixels: rendered as cutout on the client (BuildingBlocksClient)
CUTOUT_KINDS = ("leaves", "sapling", "door", "trapdoor", "plant", "tall_plant", "water_plant", "multiface", "pane",
                "climber", "trophy", "torch", "wall_torch", "spikes", "hearth")


def gen_java(features):
    lines = []
    for bid, row in BLOCKS.items():
        props = f'material("{row["material"]}", MapColor.{row["color"]})'
        kind = JAVA_KIND[row["kind"]]
        if kind in ("stairs", "sapling"):
            lines.append(f'        ModBlocks.{kind}("{bid}", "{row["base"]}", {props});')
        elif row["kind"] in BOX_KINDS:
            boxes = [e["from"] + e["to"] for e in PROPS[bid] if e["collide"]]
            arr = ", ".join("{" + ", ".join(f"{v:g}" for v in b) + "}" for b in boxes)
            lines.append(f'        ModBlocks.{kind}("{bid}", new double[][]{{{arr}}}, {props});')
        else:
            lines.append(f'        ModBlocks.{kind}("{bid}", {props});')
    strip = "\n".join(f'            {{"{a}", "{b}"}},' for a, b in STRIPPABLES)
    cutout = ", ".join(f'"{b}"' for b, row in BLOCKS.items() if row["kind"] in CUTOUT_KINDS)
    on_water = ", ".join(f'"{b}"' for b, row in BLOCKS.items() if row["kind"] == "water_plant")
    torches = "\n".join(f'            {{"{row["base"]}", "{b}"}},' for b, row in BLOCKS.items() if row["kind"] == "wall_torch")
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

    /** {{torch, wall torch}}: one item places either (the wall torch has no item of its own). */
    public static final String[][] WALL_TORCHES = {{
{torches}
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
        if kind in NO_ITEM_KINDS:
            pass
        elif kind == "door":
            write(f"{A}/models/item/{bid}.json", {"parent": "minecraft:item/generated", "textures": {"layer0": f"{NS}:item/{bid}"}})
        elif kind in ("sapling", "plant", "water_plant", "multiface", "climber", "torch", "spikes"):
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
        elif kind == "bed":
            loot_part(bid, "part", "head")
        elif kind == "wall_torch":
            loot_as(bid, row["base"])
        else:
            loot_self(bid, FLINT_BONUS if bid == "flint_nodules" else None)
    recipes()
    tags()
    gen_java(worldgen())
    print(f"{len(BLOCKS)} building blocks written")


if __name__ == "__main__":
    main()
