"""Generates the Cretaceous world of Chapter 1 (v0.8, "Mundo Terrassic"):

  * the 11 biomes of the Late Cretaceous (data/terrassic/worldgen/biome/*.json) with their plants, trees,
    rocks, colours, particles and the vanilla mobs that fit the era (no cows, villagers, zombies on the surface,
    bats or dolphins);
  * the placed/configured features those biomes use (data/terrassic/worldgen/*_feature/cretaceous/...),
    built on the trees and plants of the building-block phases (gen_blocks.py);
  * the world types "Terrassic" and "Terrassic: Large Biomes" (data/terrassic/worldgen/world_preset/*.json),
    listed on the Create World screen. The overworld uses the vanilla terrain; only the biome map changes. The
    biome map is the vanilla OverworldBiomeBuilder (ported below) with every vanilla biome mapped to its
    Cretaceous counterpart, so rivers, coasts, swamps and mountains land where the terrain expects them;
  * biome tags: terrassic:cretaceous (all of them), terrassic:habitat/<word> (which species spawn there: the
    words are the ones of the WORLD table in gen_species.py) and a few vanilla tags (no patrols, no wandering
    traders, map outlines, underwater music...);
  * block tags so the Cretaceous soils grow plants and spawn animals (#minecraft:dirt, #animals_spawnable_on);
  * the lang entries (biome names and world types) in LANG, merged by gen_resources.py.

Surface blocks (sand beaches, laterite in the Dry Lands, litter in the forests, mud in the swamps) come from
world/CretaceousSurface.java, injected into the overworld surface rule by mixin/NoiseGeneratorSettingsMixin.

Run through gen_resources.py (or directly: python3 gen_world.py).
"""
import json
import os

NS = "terrassic"
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, "..", "..", "common", "src", "main", "resources"))
DATA = os.path.join(RES, "data")
WG = os.path.join(DATA, NS, "worldgen")

LANG = {"en_us": {}, "pt_br": {}, "es_es": {}}


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def merge_tag(path, values):
    """Writes a tag with replace=false, keeping what another generator already put in the same file."""
    old = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = json.load(f).get("values", [])
    write(path, {"replace": False, "values": sorted(set(old) | set(values))})


# ---------------------------------------------------------------------------------------------------------------
# Biomes
# ---------------------------------------------------------------------------------------------------------------

MOOD = {"sound": "minecraft:ambient.cave", "tick_delay": 6000, "block_search_extent": 8, "offset": 2.0}


def spawn(mob, weight, lo, hi):
    return {"type": mob, "weight": weight, "minCount": lo, "maxCount": hi}


# Vanilla monsters that stay in the Cretaceous: zombies and skeletons only underground (CretaceousBiomes blocks them
# where the sky is visible), no zombie villagers, witches, drowned or phantoms. Spiders, creepers and slimes keep
# the caves (and the string for spears) as in vanilla.
MONSTERS = [spawn("minecraft:spider", 100, 4, 4), spawn("minecraft:zombie", 95, 4, 4),
            spawn("minecraft:skeleton", 100, 4, 4), spawn("minecraft:creeper", 100, 4, 4),
            spawn("minecraft:slime", 100, 4, 4), spawn("minecraft:enderman", 10, 1, 4)]
CAVE_WATER = [spawn("minecraft:glow_squid", 10, 4, 6)]

# placed features of the global overworld generation, in vanilla order (BiomeDefaultFeatures)
BASE = {
    "lakes": ["minecraft:lake_lava_underground", "minecraft:lake_lava_surface"],
    "local_modifications": ["minecraft:amethyst_geode"],
    "underground_structures": ["minecraft:monster_room", "minecraft:monster_room_deep",
                               "minecraft:fossil_upper", "minecraft:fossil_lower"],
    "underground_ores": [
        "minecraft:ore_dirt", "minecraft:ore_gravel", "minecraft:ore_granite_upper", "minecraft:ore_granite_lower",
        "minecraft:ore_diorite_upper", "minecraft:ore_diorite_lower", "minecraft:ore_andesite_upper",
        "minecraft:ore_andesite_lower", "minecraft:ore_tuff", "minecraft:ore_coal_upper", "minecraft:ore_coal_lower",
        "minecraft:ore_iron_upper", "minecraft:ore_iron_middle", "minecraft:ore_iron_small", "minecraft:ore_gold",
        "minecraft:ore_gold_lower", "minecraft:ore_redstone", "minecraft:ore_redstone_lower", "minecraft:ore_diamond",
        "minecraft:ore_diamond_large", "minecraft:ore_diamond_buried", "minecraft:ore_lapis",
        "minecraft:ore_lapis_buried", "minecraft:ore_copper", "minecraft:underwater_magma"],
    "fluid_springs": ["minecraft:spring_water", "minecraft:spring_lava"],
    "vegetal_decoration": ["minecraft:glow_lichen"],
    "top_layer_modification": ["minecraft:freeze_top_layer"],
}
DISKS = ["minecraft:disk_sand", "minecraft:disk_clay", "minecraft:disk_gravel"]
STEPS = ["raw_generation", "lakes", "local_modifications", "underground_structures", "surface_structures",
         "strongholds", "underground_ores", "underground_decoration", "fluid_springs", "vegetal_decoration",
         "top_layer_modification"]

# Vegetation is written as (plant, density): density > 0 = that many patches per chunk, density < 0 = one patch
# every |density| chunks. Plants are the configured features of gen_blocks.py; a placed variant
# terrassic:cretaceous/<plant>_c<n> / _r<n> is generated for each density used. Strings are placed features used
# as they are (vanilla or existing terrassic ones).
#
# trees = (density, water depth allowed, [(wood, chance), ...], default wood)
BIOMES = {
    "hadrosaur_plains": dict(
        names=("Hadrosaur Plains", "Planície dos Hadrossauros", "Llanura de los Hadrosaurios"),
        doc="Open grassland of the first grasses, with groves of plane trees and ginkgos: where the herds graze.",
        temp=0.9, downfall=0.35, rain=True,
        sky=0x7BAEF0, fog=0xC6DCF5, water=0x3F76E4, water_fog=0x050533, grass=0xA3B85A, foliage=0x84A33E,
        trees=(-2, 0, [("platanus", 0.4), ("ginkgo", 0.3)], "magnolia"),
        veg=[("cretaceous_grass", 5), ("bracken", -2), ("williamsonia", -4), ("young_cycad", -6), ("horsetail", -4),
             ("archaefructus", -6), "minecraft:brown_mushroom_normal", "minecraft:red_mushroom_normal"],
        habitats=["plains", "savanna"]),
    "magnolia_forest": dict(
        names=("Magnolia Forest", "Floresta de Magnólias", "Bosque de Magnolias"),
        doc="Warm forest of the first flowering trees, with tree ferns and a fern understory.",
        temp=0.85, downfall=0.85, rain=True,
        sky=0x79A9EA, fog=0xC4D9F0, water=0x3D7AD8, water_fog=0x050533, grass=0x6DAF46, foliage=0x5A9B35,
        particle=("minecraft:spore_blossom_air", 0.0015),
        trees=(8, 0, [("magnolia", 0.5), ("podocarpus", 0.2), ("platanus", 0.15)], "ginkgo"),
        extra_trees=(-2, "tree_fern"),
        veg=[("royal_fern", 2), ("bracken", 2), ("tall_bracken", -2), ("clubmoss", -2), ("cretaceous_grass", 2),
             ("williamsonia", -3), "terrassic:shelf_fungus",
             "minecraft:brown_mushroom_normal", "minecraft:red_mushroom_normal"],
        habitats=["forest", "jungle"]),
    "cypress_swamp": dict(
        names=("Cypress Swamp", "Pântano de Ciprestes", "Pantano de Cipreses"),
        doc="Bald cypresses standing in shallow water, rushes, horsetails and water lilies.",
        temp=0.8, downfall=0.9, rain=True,
        sky=0x7FA6C9, fog=0xB7C7B0, water=0x4D6A4E, water_fog=0x1D2A20, grass=0x6E7A3A, foliage=0x5E7330,
        trees=(4, 2, [("taxodium", 0.85)], "tree_fern"),
        veg=[("rush", 3), ("calamites", 1), ("horsetail", 2), ("tall_horsetail", -2), ("royal_fern", -2),
             ("liverwort", 2), ("swamp_algae", 3), ("cretaceous_water_lily", 2), ("cretaceous_grass", 1),
             "minecraft:seagrass_swamp", "minecraft:brown_mushroom_swamp", "minecraft:red_mushroom_swamp"],
        disks=True, habitats=["swamp"], tags=["water_on_map_outlines", "has_closer_water_fog",
                                             "allows_surface_slime_spawns"],
        spawners=dict(creature=[spawn("minecraft:frog", 10, 2, 5)],
                      water_ambient=[spawn("minecraft:tropical_fish", 4, 2, 4)])),
    "redwood_forest": dict(
        names=("Redwood Forest", "Floresta de Sequoias", "Bosque de Secuoyas"),
        doc="Cool, tall forest of dawn redwoods and araucarias in the north, carpeted with needles.",
        temp=0.55, downfall=0.8, rain=True,
        sky=0x7FA8D8, fog=0xBFCFE0, water=0x3A6FC4, water_fog=0x050533, grass=0x5E8C44, foliage=0x4E7D38,
        trees=(7, 0, [("metasequoia", 0.6), ("araucaria", 0.25)], "podocarpus"),
        veg=[("bracken", 3), ("tall_bracken", -2), ("clubmoss", 1), ("horsetail", -3), ("cretaceous_grass", 1),
             "terrassic:shelf_fungus", "minecraft:brown_mushroom_taiga", "minecraft:red_mushroom_taiga"],
        habitats=["forest", "taiga"]),
    "dry_lands": dict(
        names=("Dry Lands", "Terras Secas", "Tierras Secas"),
        doc="Semi-arid red soils with scattered araucarias, palms and cycads, after Late Cretaceous Patagonia.",
        temp=1.6, downfall=0.05, rain=False,
        sky=0x8CB4E6, fog=0xE3D7BC, water=0x4A86C9, water_fog=0x050533, grass=0xB8A85C, foliage=0x9E9A4A,
        particle=("minecraft:white_ash", 0.004),
        trees=(-5, 0, [("araucaria", 0.55), ("sabal", 0.25)], "podocarpus"),
        veg=[("cretaceous_grass", 1), ("young_cycad", -2), ("cycad", -3), ("williamsonia", -6),
             "terrassic:laterite_pebbles", "minecraft:patch_dead_bush"],
        ores=["minecraft:ore_gold_extra", "terrassic:laterite"],
        habitats=["savanna", "badlands", "desert"]),
    "river_delta": dict(
        names=("River Delta", "Delta do Rio", "Delta del Río"),
        doc="Hot river channels, sandbars and mud flats with palms and tree ferns, after the Kem Kem beds.",
        temp=1.2, downfall=0.8, rain=True,
        sky=0x80B0EC, fog=0xCADFEA, water=0x3E8C9A, water_fog=0x0A2A30, grass=0x7DB04B, foliage=0x5FA03A,
        trees=(2, 1, [("sabal", 0.4), ("tree_fern", 0.3)], "platanus"),
        veg=[("rush", 3), ("horsetail", 2), ("tall_horsetail", 1), ("calamites", -2), ("archaefructus", 1),
             ("cretaceous_water_lily", 1), ("cretaceous_grass", 2), ("royal_fern", -3),
             "terrassic:conglomerate_pebbles", "minecraft:seagrass_river"],
        disks=True, habitats=["river", "swamp", "jungle", "coast"],
        tags=["water_on_map_outlines", "has_closer_water_fog"],
        spawners=dict(water_ambient=[spawn("minecraft:tropical_fish", 6, 2, 4), spawn("minecraft:salmon", 4, 1, 4)])),
    "inner_sea": dict(
        names=("Inner Sea", "Mar Interior", "Mar Interior"),
        doc="The warm, shallow Western Interior Seaway: sand, seagrass and reefs.",
        temp=0.8, downfall=0.5, rain=True,
        sky=0x7BAEF0, fog=0xC6DCF5, water=0x3AA3D8, water_fog=0x0A3348, grass=0x8EB971, foliage=0x71A74D,
        veg=["minecraft:seagrass_warm", "minecraft:warm_ocean_vegetation"],
        disks=True, habitats=["ocean"],
        tags=["water_on_map_outlines", "plays_underwater_music", "produces_corals_from_bonemeal"],
        spawners=dict(water_creature=[spawn("minecraft:squid", 3, 1, 4)],
                      water_ambient=[spawn("minecraft:tropical_fish", 25, 8, 8), spawn("minecraft:cod", 10, 3, 6)])),
    "deep_inner_sea": dict(
        names=("Deep Inner Sea", "Mar Interior Profundo", "Mar Interior Profundo"),
        doc="The deep water of the seaway, home of the mosasaurs.",
        temp=0.8, downfall=0.5, rain=True,
        sky=0x7BAEF0, fog=0xC6DCF5, water=0x2E7FC0, water_fog=0x061F38, grass=0x8EB971, foliage=0x71A74D,
        veg=["minecraft:seagrass_deep_warm"],
        disks=True, habitats=["ocean", "deep_sea"],
        tags=["water_on_map_outlines", "plays_underwater_music"],
        spawners=dict(water_creature=[spawn("minecraft:squid", 6, 1, 4)],
                      water_ambient=[spawn("minecraft:cod", 10, 3, 6)])),
    "cretaceous_river": dict(
        names=("Cretaceous River", "Rio do Cretáceo", "Río del Cretácico"),
        doc="Rivers with gravel and sand bars, plane trees on the banks and horsetails in the shallows.",
        temp=0.8, downfall=0.6, rain=True,
        sky=0x7BAEF0, fog=0xC6DCF5, water=0x3D7DD4, water_fog=0x050533, grass=0x84B356, foliage=0x6AA23E,
        trees=(-3, 0, [("platanus", 0.5), ("metasequoia", 0.3)], "taxodium"),
        veg=[("rush", 1), ("horsetail", 1), ("archaefructus", -2), ("cretaceous_water_lily", -2),
             ("cretaceous_grass", 1), "terrassic:quartzite_pebbles", "terrassic:gneiss_pebbles",
             "minecraft:seagrass_river"],
        disks=True, habitats=["river"],
        tags=["water_on_map_outlines", "plays_underwater_music", "reduce_water_ambient_spawns"],
        spawners=dict(water_creature=[spawn("minecraft:squid", 2, 1, 4)],
                      water_ambient=[spawn("minecraft:salmon", 5, 1, 5)])),
    "cretaceous_beach": dict(
        names=("Cretaceous Shore", "Praia do Cretáceo", "Playa del Cretácico"),
        doc="Sand and limestone shores of the seaway, where pterosaurs and sea turtles come ashore.",
        temp=0.85, downfall=0.4, rain=True,
        sky=0x7BAEF0, fog=0xC6DCF5, water=0x3AA3D8, water_fog=0x0A3348, grass=0x9DB85A, foliage=0x84A33E,
        veg=["terrassic:limestone_pebbles", "terrassic:flint_pebbles"],
        habitats=["coast"],
        spawners=dict(creature=[spawn("minecraft:turtle", 5, 2, 5)])),
    "cretaceous_highlands": dict(
        names=("Cretaceous Highlands", "Serras do Cretáceo", "Sierras del Cretácico"),
        doc="Mountains of bare stone and quartzite, araucarias on the slopes and lichen on the rocks.",
        temp=0.45, downfall=0.5, rain=True,
        sky=0x86AEDF, fog=0xC9D6E3, water=0x3D72C8, water_fog=0x050533, grass=0x88A462, foliage=0x6F8F4A,
        trees=(-3, 0, [("araucaria", 0.6)], "podocarpus"),
        veg=[("cretaceous_grass", 1), ("clubmoss", -2), ("bracken", -3), "terrassic:lichen"],
        ores=["minecraft:ore_emerald", "terrassic:quartzite"],
        habitats=["hill"]),
}

# words of the WORLD table in gen_species.py (ModSpawns); a biome in terrassic:habitat/<word> gets those species
HABITATS = ["forest", "jungle", "savanna", "badlands", "taiga", "hill", "river", "plains", "desert", "swamp",
            "coast", "deep_sea", "ocean"]

# Order of the vegetation features across all biomes (features shared by two biomes must keep the same relative order
# or the game refuses the world with "Feature order cycle found").
PLANT_ORDER = ["cretaceous_grass", "bracken", "tall_bracken", "royal_fern", "clubmoss", "williamsonia", "young_cycad",
               "cycad", "horsetail", "tall_horsetail", "calamites", "archaefructus", "rush", "liverwort",
               "swamp_algae", "cretaceous_water_lily"]
NAMED_ORDER = ["terrassic:shelf_fungus", "terrassic:lichen", "terrassic:laterite_pebbles",
               "terrassic:conglomerate_pebbles", "terrassic:quartzite_pebbles", "terrassic:gneiss_pebbles",
               "terrassic:limestone_pebbles", "terrassic:flint_pebbles", "minecraft:patch_dead_bush",
               "minecraft:seagrass_warm", "minecraft:seagrass_deep_warm", "minecraft:seagrass_river",
               "minecraft:seagrass_swamp", "minecraft:warm_ocean_vegetation",
               "minecraft:brown_mushroom_normal", "minecraft:red_mushroom_normal",
               "minecraft:brown_mushroom_taiga", "minecraft:red_mushroom_taiga",
               "minecraft:brown_mushroom_swamp", "minecraft:red_mushroom_swamp"]
ORE_ORDER = ["minecraft:ore_emerald", "minecraft:ore_gold_extra"] + DISKS + ["terrassic:laterite", "terrassic:quartzite"]


def density_placement(density):
    if density > 1:
        return [{"type": "minecraft:count", "count": density}]
    if density < -1:
        return [{"type": "minecraft:rarity_filter", "chance": -density}]
    return []


def plant_variant(plant, density):
    """Placed feature for a vegetation patch at the given density; returns its id."""
    name = f"cretaceous/{plant}_{'c' if density > 0 else 'r'}{abs(density)}"
    write(os.path.join(WG, "placed_feature", name + ".json"), {
        "feature": f"{NS}:{plant}",
        "placement": density_placement(density) + [
            {"type": "minecraft:in_square"},
            {"type": "minecraft:heightmap", "heightmap": "WORLD_SURFACE_WG"},
            {"type": "minecraft:biome"}]})
    return f"{NS}:{name}"


def checked_tree(wood):
    """Tree that only grows where its sapling would survive (the feature a random selector picks from)."""
    name = f"cretaceous/{wood}_checked"
    write(os.path.join(WG, "placed_feature", name + ".json"), {
        "feature": f"{NS}:{wood}",
        "placement": [{"type": "minecraft:block_predicate_filter", "predicate": {
            "type": "minecraft:would_survive",
            "state": {"Name": f"{NS}:{wood}_sapling", "Properties": {"stage": "0"}}}}]})
    return f"{NS}:{name}"


def tree_placement(density, water_depth):
    return density_placement(density) + [
        {"type": "minecraft:in_square"},
        {"type": "minecraft:surface_water_depth_filter", "max_water_depth": water_depth},
        {"type": "minecraft:heightmap", "heightmap": "OCEAN_FLOOR"},
        {"type": "minecraft:biome"}]


def biome_trees(bid, spec):
    """random_selector of the biome's woods + the placed feature that scatters it; returns the placed id."""
    density, water_depth, mix, default = spec
    name = f"cretaceous/{bid}_trees"
    write(os.path.join(WG, "configured_feature", name + ".json"), {
        "type": "minecraft:random_selector",
        "config": {"features": [{"feature": checked_tree(w), "chance": c} for w, c in mix],
                   "default": checked_tree(default)}})
    write(os.path.join(WG, "placed_feature", name + ".json"), {
        "feature": f"{NS}:{name}", "placement": tree_placement(density, water_depth)})
    return f"{NS}:{name}"


def extra_trees(bid, spec):
    density, wood = spec
    name = f"cretaceous/{bid}_{wood}"
    write(os.path.join(WG, "placed_feature", name + ".json"), {
        "feature": f"{NS}:{wood}",
        "placement": tree_placement(density, 0) + [{"type": "minecraft:block_predicate_filter", "predicate": {
            "type": "minecraft:would_survive",
            "state": {"Name": f"{NS}:{wood}_sapling", "Properties": {"stage": "0"}}}}]})
    return f"{NS}:{name}"


def veg_key(entry):
    """Sort key giving every vegetation feature one global position (see PLANT_ORDER)."""
    if isinstance(entry, tuple):
        plant, density = entry
        return (1, PLANT_ORDER.index(plant), -density if density > 0 else 1000 - density)
    return (2, NAMED_ORDER.index(entry), 0)


def biome_json(bid, b):
    feats = {s: [] for s in STEPS}
    for step, lst in BASE.items():
        feats[step] += lst
    extra_ores = sorted(b.get("ores", []) + (DISKS if b.get("disks") else []), key=ORE_ORDER.index)
    feats["underground_ores"] += extra_ores
    veg = feats["vegetal_decoration"]
    if "trees" in b:
        veg.append(biome_trees(bid, b["trees"]))
    if "extra_trees" in b:
        veg.append(extra_trees(bid, b["extra_trees"]))
    for entry in sorted(b["veg"], key=veg_key):
        veg.append(plant_variant(*entry) if isinstance(entry, tuple) else entry)

    sp = b.get("spawners", {})
    land = bid not in ("inner_sea", "deep_inner_sea")
    effects = {"sky_color": b["sky"], "fog_color": b["fog"], "water_color": b["water"],
               "water_fog_color": b["water_fog"], "grass_color": b["grass"], "foliage_color": b["foliage"],
               "mood_sound": MOOD}
    if "particle" in b:
        effects["particle"] = {"options": {"type": b["particle"][0]}, "probability": b["particle"][1]}
    return {
        "has_precipitation": b["rain"],
        "temperature": b["temp"],
        "downfall": b["downfall"],
        "effects": effects,
        "spawners": {
            "monster": MONSTERS if land else [m for m in MONSTERS if m["type"] != "minecraft:slime"],
            "creature": sp.get("creature", []),
            "ambient": [],
            "axolotls": [],
            "underground_water_creature": CAVE_WATER,
            "water_creature": sp.get("water_creature", []),
            "water_ambient": sp.get("water_ambient", []),
            "misc": []},
        "spawn_costs": {},
        "carvers": {"air": ["minecraft:cave", "minecraft:cave_extra_underground", "minecraft:canyon"]},
        "features": [feats[s] for s in STEPS],
    }


# ---------------------------------------------------------------------------------------------------------------
# Biome map: vanilla OverworldBiomeBuilder (1.20.1) ported, then every vanilla biome mapped to a Cretaceous one
# ---------------------------------------------------------------------------------------------------------------

def q(v):
    """Climate.quantizeCoord"""
    return int(v * 10000.0)


def span(a, b):
    return (q(a), q(b))


def join(p1, p2):
    return (min(p1[0], p2[0]), max(p1[1], p2[1]))


FULL = span(-1.0, 1.0)
TEMPS = [span(-1.0, -0.45), span(-0.45, -0.15), span(-0.15, 0.2), span(0.2, 0.55), span(0.55, 1.0)]
HUMS = [span(-1.0, -0.35), span(-0.35, -0.1), span(-0.1, 0.1), span(0.1, 0.3), span(0.3, 1.0)]
EROS = [span(-1.0, -0.78), span(-0.78, -0.375), span(-0.375, -0.2225), span(-0.2225, 0.05), span(0.05, 0.45),
        span(0.45, 0.55), span(0.55, 1.0)]
FROZEN = TEMPS[0]
UNFROZEN = join(TEMPS[1], TEMPS[4])
MUSHROOM_C = span(-1.2, -1.05)
DEEP_OCEAN_C = span(-1.05, -0.455)
OCEAN_C = span(-0.455, -0.19)
COAST_C = span(-0.19, -0.11)
INLAND_C = span(-0.11, 0.55)
NEAR_C = span(-0.11, 0.03)
MID_C = span(0.03, 0.3)
FAR_C = span(0.3, 1.0)

OCEANS = [["deep_frozen_ocean", "deep_cold_ocean", "deep_ocean", "deep_lukewarm_ocean", "warm_ocean"],
          ["frozen_ocean", "cold_ocean", "ocean", "lukewarm_ocean", "warm_ocean"]]
MIDDLE = [["snowy_plains", "snowy_plains", "snowy_plains", "snowy_taiga", "taiga"],
          ["plains", "plains", "forest", "taiga", "old_growth_spruce_taiga"],
          ["flower_forest", "plains", "forest", "birch_forest", "dark_forest"],
          ["savanna", "savanna", "forest", "jungle", "jungle"],
          ["desert", "desert", "desert", "desert", "desert"]]
MIDDLE_V = [["ice_spikes", None, "snowy_taiga", None, None],
            [None, None, None, None, "old_growth_pine_taiga"],
            ["sunflower_plains", None, None, "old_growth_birch_forest", None],
            [None, None, "plains", "sparse_jungle", "bamboo_jungle"],
            [None, None, None, None, None]]
PLATEAU = [["snowy_plains", "snowy_plains", "snowy_plains", "snowy_taiga", "snowy_taiga"],
           ["meadow", "meadow", "forest", "taiga", "old_growth_spruce_taiga"],
           ["meadow", "meadow", "meadow", "meadow", "dark_forest"],
           ["savanna_plateau", "savanna_plateau", "forest", "forest", "jungle"],
           ["badlands", "badlands", "badlands", "wooded_badlands", "wooded_badlands"]]
PLATEAU_V = [["ice_spikes", None, None, None, None],
             ["cherry_grove", None, "meadow", "meadow", "old_growth_pine_taiga"],
             ["cherry_grove", "cherry_grove", "forest", "birch_forest", None],
             [None, None, None, None, None],
             ["eroded_badlands", "eroded_badlands", None, None, None]]
SHATTERED = [["windswept_gravelly_hills", "windswept_gravelly_hills", "windswept_hills", "windswept_forest",
              "windswept_forest"],
             ["windswept_gravelly_hills", "windswept_gravelly_hills", "windswept_hills", "windswept_forest",
              "windswept_forest"],
             ["windswept_hills", "windswept_hills", "windswept_hills", "windswept_forest", "windswept_forest"],
             [None, None, None, None, None],
             [None, None, None, None, None]]


class Builder:
    def __init__(self):
        self.out = []  # (temp, hum, cont, eros, weird, vanilla biome)

    def add(self, t, h, c, e, w, biome):
        self.out.append((t, h, c, e, w, biome))

    # -- pickers (same names as OverworldBiomeBuilder) --
    def middle(self, t, h, w):
        if w[1] < 0:
            return MIDDLE[t][h]
        return MIDDLE_V[t][h] or MIDDLE[t][h]

    def middle_or_badlands(self, t, h, w):
        return self.badlands(h, w) if t == 4 else self.middle(t, h, w)

    def middle_or_badlands_or_slope(self, t, h, w):
        return self.slope(t, h, w) if t == 0 else self.middle_or_badlands(t, h, w)

    def windswept_savanna(self, t, h, w, other):
        return "windswept_savanna" if t > 1 and h < 4 and w[1] >= 0 else other

    def shattered_coast(self, t, h, w):
        b = self.middle(t, h, w) if w[1] >= 0 else self.beach(t, h)
        return self.windswept_savanna(t, h, w, b)

    def beach(self, t, h):
        return "snowy_beach" if t == 0 else ("desert" if t == 4 else "beach")

    def badlands(self, h, w):
        if h < 2:
            return "badlands" if w[1] < 0 else "eroded_badlands"
        return "badlands" if h < 3 else "wooded_badlands"

    def plateau(self, t, h, w):
        if w[1] >= 0 and PLATEAU_V[t][h]:
            return PLATEAU_V[t][h]
        return PLATEAU[t][h]

    def peak(self, t, h, w):
        if t <= 2:
            return "jagged_peaks" if w[1] < 0 else "frozen_peaks"
        return "stony_peaks" if t == 3 else self.badlands(h, w)

    def slope(self, t, h, w):
        if t >= 3:
            return self.plateau(t, h, w)
        return "snowy_slopes" if h <= 1 else "grove"

    def shattered(self, t, h, w):
        return SHATTERED[t][h] or self.middle(t, h, w)

    # -- slices --
    def build(self):
        self.add(FULL, FULL, MUSHROOM_C, FULL, FULL, "mushroom_fields")
        for i, t in enumerate(TEMPS):
            self.add(t, FULL, DEEP_OCEAN_C, FULL, FULL, OCEANS[0][i])
            self.add(t, FULL, OCEAN_C, FULL, FULL, OCEANS[1][i])
        self.mid(span(-1.0, -0.93333334))
        self.high(span(-0.93333334, -0.7666667))
        self.peaks(span(-0.7666667, -0.56666666))
        self.high(span(-0.56666666, -0.4))
        self.mid(span(-0.4, -0.26666668))
        self.low(span(-0.26666668, -0.05))
        self.valleys(span(-0.05, 0.05))
        self.low(span(0.05, 0.26666668))
        self.mid(span(0.26666668, 0.4))
        self.high(span(0.4, 0.56666666))
        self.peaks(span(0.56666666, 0.7666667))
        self.high(span(0.7666667, 0.93333334))
        self.mid(span(0.93333334, 1.0))
        return self.out

    def peaks(self, w):
        for ti, t in enumerate(TEMPS):
            for hi, h in enumerate(HUMS):
                m, mb, mbs = self.middle(ti, hi, w), self.middle_or_badlands(ti, hi, w), self.middle_or_badlands_or_slope(ti, hi, w)
                pl, sh = self.plateau(ti, hi, w), self.shattered(ti, hi, w)
                ws, pk = self.windswept_savanna(ti, hi, w, sh), self.peak(ti, hi, w)
                self.add(t, h, join(COAST_C, FAR_C), EROS[0], w, pk)
                self.add(t, h, join(COAST_C, NEAR_C), EROS[1], w, mbs)
                self.add(t, h, join(MID_C, FAR_C), EROS[1], w, pk)
                self.add(t, h, join(COAST_C, NEAR_C), join(EROS[2], EROS[3]), w, m)
                self.add(t, h, join(MID_C, FAR_C), EROS[2], w, pl)
                self.add(t, h, MID_C, EROS[3], w, mb)
                self.add(t, h, FAR_C, EROS[3], w, pl)
                self.add(t, h, join(COAST_C, FAR_C), EROS[4], w, m)
                self.add(t, h, join(COAST_C, NEAR_C), EROS[5], w, ws)
                self.add(t, h, join(MID_C, FAR_C), EROS[5], w, sh)
                self.add(t, h, join(COAST_C, FAR_C), EROS[6], w, m)

    def high(self, w):
        for ti, t in enumerate(TEMPS):
            for hi, h in enumerate(HUMS):
                m, mb, mbs = self.middle(ti, hi, w), self.middle_or_badlands(ti, hi, w), self.middle_or_badlands_or_slope(ti, hi, w)
                pl, sh = self.plateau(ti, hi, w), self.shattered(ti, hi, w)
                ws, sl, pk = self.windswept_savanna(ti, hi, w, m), self.slope(ti, hi, w), self.peak(ti, hi, w)
                self.add(t, h, COAST_C, join(EROS[0], EROS[1]), w, m)
                self.add(t, h, NEAR_C, EROS[0], w, sl)
                self.add(t, h, join(MID_C, FAR_C), EROS[0], w, pk)
                self.add(t, h, NEAR_C, EROS[1], w, mbs)
                self.add(t, h, join(MID_C, FAR_C), EROS[1], w, sl)
                self.add(t, h, join(COAST_C, NEAR_C), join(EROS[2], EROS[3]), w, m)
                self.add(t, h, join(MID_C, FAR_C), EROS[2], w, pl)
                self.add(t, h, MID_C, EROS[3], w, mb)
                self.add(t, h, FAR_C, EROS[3], w, pl)
                self.add(t, h, join(COAST_C, FAR_C), EROS[4], w, m)
                self.add(t, h, join(COAST_C, NEAR_C), EROS[5], w, ws)
                self.add(t, h, join(MID_C, FAR_C), EROS[5], w, sh)
                self.add(t, h, join(COAST_C, FAR_C), EROS[6], w, m)

    def swamps(self, w, cont):
        self.add(join(TEMPS[1], TEMPS[2]), FULL, cont, EROS[6], w, "swamp")
        self.add(join(TEMPS[3], TEMPS[4]), FULL, cont, EROS[6], w, "mangrove_swamp")

    def mid(self, w):
        self.add(FULL, FULL, COAST_C, join(EROS[0], EROS[2]), w, "stony_shore")
        self.swamps(w, join(NEAR_C, FAR_C))
        for ti, t in enumerate(TEMPS):
            for hi, h in enumerate(HUMS):
                m, mb, mbs = self.middle(ti, hi, w), self.middle_or_badlands(ti, hi, w), self.middle_or_badlands_or_slope(ti, hi, w)
                sh, pl, be = self.shattered(ti, hi, w), self.plateau(ti, hi, w), self.beach(ti, hi)
                ws, sc, sl = self.windswept_savanna(ti, hi, w, m), self.shattered_coast(ti, hi, w), self.slope(ti, hi, w)
                self.add(t, h, join(NEAR_C, FAR_C), EROS[0], w, sl)
                self.add(t, h, join(NEAR_C, MID_C), EROS[1], w, mbs)
                self.add(t, h, FAR_C, EROS[1], w, sl if ti == 0 else pl)
                self.add(t, h, NEAR_C, EROS[2], w, m)
                self.add(t, h, MID_C, EROS[2], w, mb)
                self.add(t, h, FAR_C, EROS[2], w, pl)
                self.add(t, h, join(COAST_C, NEAR_C), EROS[3], w, m)
                self.add(t, h, join(MID_C, FAR_C), EROS[3], w, mb)
                if w[1] < 0:
                    self.add(t, h, COAST_C, EROS[4], w, be)
                    self.add(t, h, join(NEAR_C, FAR_C), EROS[4], w, m)
                else:
                    self.add(t, h, join(COAST_C, FAR_C), EROS[4], w, m)
                self.add(t, h, COAST_C, EROS[5], w, sc)
                self.add(t, h, NEAR_C, EROS[5], w, ws)
                self.add(t, h, join(MID_C, FAR_C), EROS[5], w, sh)
                self.add(t, h, COAST_C, EROS[6], w, be if w[1] < 0 else m)
                if ti == 0:
                    self.add(t, h, join(NEAR_C, FAR_C), EROS[6], w, m)

    def low(self, w):
        self.add(FULL, FULL, COAST_C, join(EROS[0], EROS[2]), w, "stony_shore")
        self.swamps(w, join(NEAR_C, FAR_C))
        for ti, t in enumerate(TEMPS):
            for hi, h in enumerate(HUMS):
                m, mb, mbs = self.middle(ti, hi, w), self.middle_or_badlands(ti, hi, w), self.middle_or_badlands_or_slope(ti, hi, w)
                be, ws, sc = self.beach(ti, hi), self.windswept_savanna(ti, hi, w, m), self.shattered_coast(ti, hi, w)
                self.add(t, h, NEAR_C, join(EROS[0], EROS[1]), w, mb)
                self.add(t, h, join(MID_C, FAR_C), join(EROS[0], EROS[1]), w, mbs)
                self.add(t, h, NEAR_C, join(EROS[2], EROS[3]), w, m)
                self.add(t, h, join(MID_C, FAR_C), join(EROS[2], EROS[3]), w, mb)
                self.add(t, h, COAST_C, join(EROS[3], EROS[4]), w, be)
                self.add(t, h, join(NEAR_C, FAR_C), EROS[4], w, m)
                self.add(t, h, COAST_C, EROS[5], w, sc)
                self.add(t, h, NEAR_C, EROS[5], w, ws)
                self.add(t, h, join(MID_C, FAR_C), EROS[5], w, m)
                self.add(t, h, COAST_C, EROS[6], w, be)
                if ti == 0:
                    self.add(t, h, join(NEAR_C, FAR_C), EROS[6], w, m)

    def valleys(self, w):
        river = lambda frozen: "frozen_river" if frozen else "river"
        self.add(FROZEN, FULL, COAST_C, join(EROS[0], EROS[1]), w, "stony_shore" if w[1] < 0 else "frozen_river")
        self.add(UNFROZEN, FULL, COAST_C, join(EROS[0], EROS[1]), w, "stony_shore" if w[1] < 0 else "river")
        self.add(FROZEN, FULL, NEAR_C, join(EROS[0], EROS[1]), w, river(True))
        self.add(UNFROZEN, FULL, NEAR_C, join(EROS[0], EROS[1]), w, river(False))
        self.add(FROZEN, FULL, join(COAST_C, FAR_C), join(EROS[2], EROS[5]), w, river(True))
        self.add(UNFROZEN, FULL, join(COAST_C, FAR_C), join(EROS[2], EROS[5]), w, river(False))
        self.add(FROZEN, FULL, COAST_C, EROS[6], w, river(True))
        self.add(UNFROZEN, FULL, COAST_C, EROS[6], w, river(False))
        self.swamps(w, join(INLAND_C, FAR_C))
        self.add(FROZEN, FULL, join(INLAND_C, FAR_C), EROS[6], w, river(True))
        for ti, t in enumerate(TEMPS):
            for hi, h in enumerate(HUMS):
                self.add(t, h, join(MID_C, FAR_C), join(EROS[0], EROS[1]), w, self.middle_or_badlands(ti, hi, w))


def temp_index(t):
    """Index of the temperature band a (quantized) temperature span starts in."""
    for i, band in enumerate(TEMPS):
        if band[0] <= t[0] < band[1]:
            return i
    return 4


FOREST_FAMILY = {"forest", "flower_forest", "birch_forest", "old_growth_birch_forest", "dark_forest", "cherry_grove",
                 "jungle", "sparse_jungle", "bamboo_jungle"}
TO_CRETACEOUS = {
    "mushroom_fields": "hadrosaur_plains",
    "beach": "cretaceous_beach", "snowy_beach": "cretaceous_beach", "stony_shore": "cretaceous_beach",
    "swamp": "cypress_swamp", "mangrove_swamp": "river_delta",
    "plains": "hadrosaur_plains", "sunflower_plains": "hadrosaur_plains", "snowy_plains": "hadrosaur_plains",
    "ice_spikes": "hadrosaur_plains", "meadow": "hadrosaur_plains",
    "taiga": "redwood_forest", "snowy_taiga": "redwood_forest", "old_growth_pine_taiga": "redwood_forest",
    "old_growth_spruce_taiga": "redwood_forest", "grove": "redwood_forest", "windswept_forest": "redwood_forest",
    "savanna": "dry_lands", "savanna_plateau": "dry_lands", "windswept_savanna": "dry_lands",
    "desert": "dry_lands", "badlands": "dry_lands", "eroded_badlands": "dry_lands", "wooded_badlands": "dry_lands",
    "stony_peaks": "cretaceous_highlands", "jagged_peaks": "cretaceous_highlands",
    "frozen_peaks": "cretaceous_highlands", "snowy_slopes": "cretaceous_highlands",
    "windswept_hills": "cretaceous_highlands", "windswept_gravelly_hills": "cretaceous_highlands",
}


def to_cretaceous(entry):
    t, h, c, e, w, vb = entry
    if vb.endswith("ocean"):
        return "deep_inner_sea" if c == DEEP_OCEAN_C else "inner_sea"
    if vb in ("river", "frozen_river"):
        # the hot rivers become the delta (Kem Kem: river channels crossing a dry land)
        return "river_delta" if temp_index(t) >= 3 else "cretaceous_river"
    if vb in FOREST_FAMILY:
        return "redwood_forest" if temp_index(t) <= 1 else "magnolia_forest"
    return TO_CRETACEOUS[vb]


def merge(entries):
    """Merges hypercubes that touch along one axis and have the same biome (shrinks the list ~10x)."""
    cur = [tuple(e) for e in entries]
    changed = True
    while changed:
        changed = False
        for axis in range(5):
            groups = {}
            for e in cur:
                key = tuple(v for i, v in enumerate(e) if i != axis)
                groups.setdefault(key, []).append(e[axis])
            nxt = []
            for key, spans in groups.items():
                spans.sort()
                merged = [list(spans[0])]
                for s in spans[1:]:
                    if s[0] <= merged[-1][1]:
                        merged[-1][1] = max(merged[-1][1], s[1])
                    else:
                        merged.append(list(s))
                if len(merged) < len(spans):
                    changed = True
                for m in merged:
                    vals = list(key)
                    vals.insert(axis, (m[0], m[1]))
                    nxt.append(tuple(vals))
            cur = nxt
    return cur


def param(s):
    a, b = s[0] / 10000.0, s[1] / 10000.0
    return a if a == b else [a, b]


def biome_source():
    raw = Builder().build()
    seen, entries = set(), []
    for e in raw:  # vanilla can add the same cube twice; the first one wins in vanilla too (RTree keeps both, equal)
        k = e[:5]
        if k in seen:
            continue
        seen.add(k)
        entries.append(e[:5] + (to_cretaceous(e),))
    merged = merge(entries)
    merged.sort(key=lambda e: (e[5], e[0], e[1], e[2], e[3], e[4]))
    return [{"biome": f"{NS}:{e[5]}", "parameters": {
        "temperature": param(e[0]), "humidity": param(e[1]), "continentalness": param(e[2]),
        "erosion": param(e[3]), "weirdness": param(e[4]), "depth": [0.0, 1.0], "offset": 0.0}} for e in merged], len(entries)


def world_preset(settings, biomes):
    return {"dimensions": {
        "minecraft:overworld": {"type": "minecraft:overworld", "generator": {
            "type": "minecraft:noise", "settings": settings,
            "biome_source": {"type": "minecraft:multi_noise", "biomes": biomes}}},
        "minecraft:the_nether": {"type": "minecraft:the_nether", "generator": {
            "type": "minecraft:noise", "settings": "minecraft:nether",
            "biome_source": {"type": "minecraft:multi_noise", "preset": "minecraft:nether"}}},
        "minecraft:the_end": {"type": "minecraft:the_end", "generator": {
            "type": "minecraft:noise", "settings": "minecraft:end",
            "biome_source": {"type": "minecraft:the_end"}}}}}


def main():
    for bid, b in BIOMES.items():
        write(os.path.join(WG, "biome", bid + ".json"), biome_json(bid, b))
        en, pt, es = b["names"]
        LANG["en_us"][f"biome.{NS}.{bid}"] = en
        LANG["pt_br"][f"biome.{NS}.{bid}"] = pt
        LANG["es_es"][f"biome.{NS}.{bid}"] = es

    biomes, raw_count = biome_source()
    write(os.path.join(WG, "world_preset", "terrassic.json"), world_preset("minecraft:overworld", biomes))
    write(os.path.join(WG, "world_preset", "terrassic_large.json"), world_preset("minecraft:large_biomes", biomes))
    merge_tag(os.path.join(DATA, "minecraft", "tags", "worldgen", "world_preset", "normal.json"),
              [f"{NS}:terrassic", f"{NS}:terrassic_large"])
    for code, (a, b) in {"en_us": ("Terrassic", "Terrassic: Large Biomes"),
                         "pt_br": ("Terrassic", "Terrassic: Biomas Grandes"),
                         "es_es": ("Terrassic", "Terrassic: Biomas Grandes")}.items():
        LANG[code][f"generator.{NS}.terrassic"] = a
        LANG[code][f"generator.{NS}.terrassic_large"] = b

    # biome tags
    all_ids = [f"{NS}:{bid}" for bid in BIOMES]
    tags = os.path.join(DATA, NS, "tags", "worldgen", "biome")
    write(os.path.join(tags, "cretaceous.json"), {"replace": False, "values": all_ids})
    for word in HABITATS:
        write(os.path.join(tags, "habitat", word + ".json"), {"replace": False, "values": [
            f"{NS}:{bid}" for bid, b in BIOMES.items() if word in b["habitats"]]})
    vanilla = os.path.join(DATA, "minecraft", "tags", "worldgen", "biome")
    for tag in ("is_overworld", "without_patrol_spawns", "without_wandering_trader_spawns", "without_zombie_sieges"):
        merge_tag(os.path.join(vanilla, tag + ".json"), all_ids)
    by_tag = {}
    for bid, b in BIOMES.items():
        for tag in b.get("tags", []):
            by_tag.setdefault(tag, []).append(f"{NS}:{bid}")
    for tag, ids in by_tag.items():
        merge_tag(os.path.join(vanilla, tag + ".json"), ids)

    # the Cretaceous soils of gen_blocks.py grow plants and saplings and let animals spawn on them
    blocks = os.path.join(DATA, "minecraft", "tags", "blocks")
    soils = [f"{NS}:fern_litter", f"{NS}:needle_litter", f"{NS}:peat", f"{NS}:lateritic_soil"]
    merge_tag(os.path.join(blocks, "dirt.json"), soils)
    merge_tag(os.path.join(blocks, "animals_spawnable_on.json"), soils + [f"{NS}:cracked_mud"])

    print(f"{len(BIOMES)} Cretaceous biomes, world types written ({raw_count} climate cubes -> {len(biomes)})")


if __name__ == "__main__":
    main()
