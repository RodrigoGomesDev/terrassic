"""Structures of the Late Cretaceous (v0.8, "Mundo Terrassic", phase M3): Katarina's camps, fossil sites and bone
beds. Everything is generated here:

  * the templates (data/terrassic/structures/<structure>/<variant>.nbt), built block by block with
    tools/structgen/template.py from the mod's own building blocks (validated against the blockstate files);
  * the worldgen JSON: structure, template pool and structure set for each (data/terrassic/worldgen/...);
  * the biome tags data/terrassic/tags/worldgen/biome/has_structure/<structure>.json: the Cretaceous biomes of the
    "Terrassic" world type AND the matching vanilla biomes, so the story also works in a normal world;
  * the loot tables of the baskets (data/terrassic/loot_tables/chests/...). Camps always hold a loose page of
    Katarina's notebook, which turns into a page that player has not found yet (LoosePageItem).

The arrival crater (Cratera de Chegada) is not a template: world/ArrivalCrater.java digs it next to the world spawn the
first time a player joins.

Called by gen_world.py (which gen_resources.py runs). Standalone: python3 gen_structures.py
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "structgen"))

from nbt import IntArray  # noqa: E402
from template import Template  # noqa: E402

NS = "terrassic"
RES = os.path.normpath(os.path.join(HERE, "..", "..", "common", "src", "main", "resources"))
DATA = os.path.join(RES, "data")
WG = os.path.join(DATA, NS, "worldgen")
STRUCTURES = os.path.join(DATA, NS, "structures")


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


# ---------------------------------------------------------------------------------------------------------------
# Katarina's camp: a small thatched ridge tent, a cold hearth, a basket with one of her pages
# ---------------------------------------------------------------------------------------------------------------

CAMP_VARIANTS = {
    # variant: roof stairs, ridge, closed gable end, bed, mat, seat log, extra block by the tent
    "reed": dict(roof="reed_thatch_stairs", ridge="reed_thatch", end="wicker_block", bed="straw_bed",
                 mat="reed_mat", log="stripped_platanus_log", extra=("meat_drying_rack", {"facing": "west"})),
    "fern": dict(roof="fern_thatch_stairs", ridge="fern_thatch", end="wicker_block", bed="straw_bed",
                 mat="straw_mat", log="stripped_magnolia_log", extra=("meat_drying_rack", {"facing": "west"})),
    "hide": dict(roof="cycad_thatch_stairs", ridge="cycad_thatch", end="tanned_hide_frame", bed="hide_bed",
                 mat="reed_mat", log="stripped_araucaria_log", extra=("tanning_rack", {"facing": "west"})),
}


def camp(variant, seed):
    m = CAMP_VARIANTS[variant]
    rng = random.Random(seed)
    t = Template(11, 5, 11)
    cx, cz = 5, 5
    # trodden ground in a rough circle, and room above it
    for x in range(11):
        for z in range(11):
            r = math.hypot(x - cx, z - cz)
            if r <= 4.2 or (r <= 5.0 and rng.random() < 0.55):
                t.set(x, 0, z, "packed_earth_floor")
                t.clear(x, 1, z, x, 2, z)
    # ridge tent along x on the north side: stairs rising to the ridge on both slopes
    for x in range(3, 8):
        t.set(x, 1, 1, m["roof"], facing="south", half="bottom", shape="straight")
        t.set(x, 2, 2, m["roof"], facing="south", half="bottom", shape="straight")
        t.set(x, 3, 3, m["ridge"])
        t.set(x, 2, 4, m["roof"], facing="north", half="bottom", shape="straight")
        t.set(x, 1, 5, m["roof"], facing="north", half="bottom", shape="straight")
    for z in (2, 3, 4):  # west end closed, east end open
        t.set(2, 1, z, m["end"])
    t.set(2, 2, 3, m["end"])
    t.set(3, 1, 3, m["bed"], facing="east", part="foot")
    t.set(4, 1, 3, m["bed"], facing="east", part="head")
    t.set(5, 1, 3, m["mat"])
    t.set(6, 1, 3, m["mat"])
    t.basket(6, 1, 4, f"{NS}:chests/katarina_camp", facing="south")
    # the hearth and seats in front
    t.set(5, 1, 7, "stone_hearth", facing="south")
    t.set(3, 1, 7, m["log"], axis="z")
    t.set(7, 1, 7, m["log"], axis="z")
    t.set(5, 1, 9, m["log"], axis="x")
    block, props = m["extra"]
    t.set(8, 1, 4, block, **props)
    t.set(2, 1, 6, "rope_coil", axis="y")
    t.set(8, 1, 9, "bone_pile")
    # the stone with her chalk marks
    t.set(9, 1, 6, "chalk")
    t.set(10, 1, 6, "chalk")
    t.set(9, 2, 6, "chalk")
    t.set(9, 1, 5, rng.choice(["cave_painting_handprint", "cave_painting_spiral", "cave_painting_footprints"]),
          facing="west")
    return t


# ---------------------------------------------------------------------------------------------------------------
# Fossil site: an eroded bank of layered rock with fossils showing, and someone's digging tools
# ---------------------------------------------------------------------------------------------------------------

FOSSIL_SKULLS = ["tyrannosaurus", "triceratops", "edmontosaurus", "alamosaurus", "pachycephalosaurus",
                 "ankylosaurus", "velociraptor", "stegosaurus", "brachiosaurus", "dilophosaurus"]
LAYERS = ["shale", "shale", "limestone", "limestone", "chalk"]


def fossil_site(seed):
    rng = random.Random(seed)
    t = Template(13, 6, 11)
    # half-dome of layered rock, cut flat on the south face at z = 5
    for x in range(13):
        for z in range(11):
            r = math.hypot((x - 6) / 6.4, (z - 5) / 4.6)
            if r > 1.0:
                continue
            if z <= 5:
                h = int(round(4.6 * (1 - r * r) ** 0.6))
                for y in range(0, h + 1):
                    t.set(x, y, z, LAYERS[min(y, len(LAYERS) - 1)])
            else:  # the dig in front: gravel and trodden earth, cleared above
                t.set(x, 0, z, "minecraft:gravel" if rng.random() < 0.35 else "packed_earth_floor")
                t.clear(x, 1, z, x, 3, z)
    # fossils showing in the wall and in the floor
    wall = [(x, y) for x in range(2, 11) for y in range(1, 4) if t.get(x, y, 5) is not None]
    rng.shuffle(wall)
    for x, y in wall[:7]:
        t.set(x, y, 5, "fossil_rock")
    for x, y in wall[7:9]:
        t.set(x, y, 5, rng.choice(FOSSIL_SKULLS) + "_skull_fossil", facing="south")
    t.set(4, 0, 7, "fossil_rock")
    t.set(8, 0, 8, "fossil_rock")
    t.set(6, 1, 8, "bone_pile")
    # tools: scaffold posts with rope, a knapping bench and the basket
    for x, z in ((1, 7), (11, 7)):
        t.set(x, 1, z, "araucaria_branch_fence")
        t.set(x, 2, z, "araucaria_branch_fence")
    t.set(1, 3, 7, "rope_coil", axis="x")
    t.set(10, 1, 9, "flint_knapping_bench", facing="north")
    t.basket(2, 1, 9, f"{NS}:chests/fossil_site", facing="north")
    return t


# ---------------------------------------------------------------------------------------------------------------
# Bone bed (Ossuário): where a herd died together; a titanosaur skeleton, bones everywhere, scavengers around
# ---------------------------------------------------------------------------------------------------------------

def bone_bed(seed):
    rng = random.Random(seed)
    t = Template(17, 4, 13)
    for x in range(17):
        for z in range(13):
            r = math.hypot((x - 8) / 8.2, (z - 6) / 6.2)
            if r > 1.0 and not (r <= 1.12 and rng.random() < 0.4):
                continue
            k = rng.random()
            if k < 0.08:
                t.set(x, 0, z, "minecraft:bone_block", axis=rng.choice(["x", "y", "z"]))
            elif k < 0.13:
                t.set(x, 0, z, "fossil_rock")
            elif k < 0.45:
                t.set(x, 0, z, "cracked_mud")
            else:
                t.set(x, 0, z, "minecraft:coarse_dirt")
            t.clear(x, 1, z, x, 3, z)
            if rng.random() < 0.12:
                t.set(x, 1, z, "bone_pile")
    # the skeleton: spine, ribs, neck and skull
    for x in range(4, 13):
        t.set(x, 2, 6, "minecraft:bone_block", axis="x")
    for x in range(5, 11, 2):
        for z in (4, 8):
            t.set(x, 1, z, "bone_fence")
        t.set(x, 2, 5, "bone_fence")
        t.set(x, 2, 7, "bone_fence")
    t.set(13, 1, 6, "minecraft:bone_block", axis="x")
    t.set(14, 1, 6, "alamosaurus_skull_fossil", facing="east")
    for x in range(1, 4):  # the tail, sinking into the mud
        t.set(x, 1, 6, "minecraft:bone_block", axis="x")
    for x, z in ((3, 2), (12, 10), (7, 10)):
        t.set(x, 0, z, rng.choice(FOSSIL_SKULLS) + "_skull_fossil", facing=rng.choice(["north", "south", "east"]))
    # scavengers picking at the bones
    for x, z in ((6.5, 2.5), (10.5, 9.5), (3.5, 9.5)):
        t.entity(x, 1, z, {"id": f"{NS}:compsognathus"})
    return t


# ---------------------------------------------------------------------------------------------------------------
# Katarina's Refuge, the River House (Casa do Rio): her log house on stilts at the water, unique like a stronghold,
# with her tamed Parasaurolophus "Mate" sitting on the deck
# ---------------------------------------------------------------------------------------------------------------

KATARINA_UUID = (0x4B617461, 0x72696E61, 0x20557368, 0x61000001)  # also in world/KatarinaRefuge.java


def fence_line(t, block, cells, y):
    """Fence posts joined to their neighbours along a list of (x, z) cells."""
    cs = set(cells)
    for x, z in cells:
        t.set(x, y, z, block, north=(x, z - 1) in cs, south=(x, z + 1) in cs, east=(x + 1, z) in cs,
              west=(x - 1, z) in cs)


def river_house(seed):
    rng = random.Random(seed)
    t = Template(21, 16, 17)
    P = 5  # platform level: the first air above the ground or the water
    # stilts down into the riverbed (or the bank) and the platform
    for x in (1, 5, 9, 13, 17, 19):
        for z in (1, 5, 9, 13, 15):
            for y in range(0, P):
                t.set(x, y, z, "taxodium_log", axis="y")
    for x in range(1, 20):
        for z in range(1, 16):
            t.set(x, P, z, "taxodium_hewn_planks")
            t.clear(x, P + 1, z, x, P + 3, z)
    # the house: log corners and posts, timber-framed wattle, a lashed door, windows
    x0, x1, z0, z1 = 2, 12, 2, 10
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            edge = x in (x0, x1) or z in (z0, z1)
            if not edge:
                continue
            post = (x in (x0, x1) and (z - z0) % 4 == 0) or (z in (z0, z1) and (x - x0) % 5 == 0) or \
                (x in (x0, x1) and z in (z0, z1))
            for y in range(P + 1, P + 4):
                if post:
                    t.set(x, y, z, "taxodium_log", axis="y")
                elif y == P + 2 and ((z in (z0, z1) and (x - x0) % 5 in (2, 3)) or (x in (x0, x1) and (z - z0) % 4 == 2)):
                    t.set(x, y, z, "minecraft:air")  # window
                else:
                    t.set(x, y, z, "timber_framed_wattle")
    t.set(7, P + 1, z1, "taxodium_lashed_door", facing="south", half="lower", hinge="left", open="false")
    t.set(7, P + 2, z1, "taxodium_lashed_door", facing="south", half="upper", hinge="left", open="false")
    # gabled reed thatch roof along x, closed gables
    for i in range(6):
        y = P + 4 + i
        zs, zn = z0 - 1 + i, z1 + 1 - i
        for x in range(x0 - 1, x1 + 2):
            if zs < zn:
                t.set(x, y, zs, "reed_thatch_stairs", facing="south", half="bottom", shape="straight")
                t.set(x, y, zn, "reed_thatch_stairs", facing="north", half="bottom", shape="straight")
            else:
                t.set(x, y, zs, "reed_thatch")
        for x in (x0, x1):
            for z in range(zs + 1, zn):
                t.set(x, y, z, "timber_framed_wattle")
        for x in range(x0 + 1, x1):
            for z in range(zs + 1, zn):
                t.set(x, y, z, "minecraft:air")
    for x in range(x0 + 1, x1):
        for z in range(z0 + 1, z1):
            t.clear(x, P + 1, z, x, P + 3, z)
    # inside: her bed, the research table, baskets, the notes on the walls
    t.set(3, P + 1, 3, "hide_bed", facing="east", part="foot")
    t.set(4, P + 1, 3, "hide_bed", facing="east", part="head")
    t.set(11, P + 1, 3, "research_table", facing="west")
    t.basket(11, P + 1, 5, f"{NS}:chests/katarina_refuge", facing="west")
    t.basket(3, P + 1, 9, f"{NS}:chests/katarina_refuge", facing="east")
    t.set(11, P + 1, 9, "fat_lamp", facing="west")
    t.set(9, P + 1, 9, "tanning_rack", facing="north")
    t.set(4, P + 1, 9, "hide_drum", facing="east")
    for x, z in ((5, 5), (6, 5), (5, 6), (6, 6), (7, 6)):
        t.set(x, P + 1, z, "straw_mat")
    t.set(5, P + 2, z0, "cave_painting_herd", facing="south")
    t.set(9, P + 2, z0, "cave_painting_triceratops", facing="south")
    t.set(x0, P + 2, 6, "parasaurolophus_skull_trophy", facing="east")
    # the garden on the south deck: raised beds of fern litter with the plants she grew
    for x in range(2, 9):
        for z in (13, 14):
            t.set(x, P + 1, z, "fern_litter")
            t.set(x, P + 2, z, rng.choice(["young_cycad", "williamsonia", "horsetail", "royal_fern", "bracken"]))
    # railings around the deck, with gaps for the stairs to the water and to the house
    rail = [(x, 1) for x in range(13, 20)] + [(19, z) for z in range(1, 16)] + [(x, 15) for x in range(10, 20)] + \
        [(1, z) for z in range(11, 16)] + [(x, 15) for x in range(1, 6)]
    fence_line(t, "taxodium_branch_fence", rail, P + 1)
    t.set(15, P + 1, 3, "log_feeding_trough", facing="west")
    t.set(18, P + 1, 14, "rope_coil", axis="y")
    # Mate: hers, still waiting on the deck. Tamed to Katarina (offline) and sitting, so he stays; the first player
    # who touches him becomes his owner (world/KatarinaRefuge).
    t.entity(16.0, P + 1, 8.5, {"id": f"{NS}:parasaurolophus", "CustomName": '{"text":"Mate"}',
                                "Owner": IntArray([v - (1 << 32) if v >= 1 << 31 else v for v in KATARINA_UUID]),
                                "Sitting": True, "Tags": ["terrassic_mate"], "PersistenceRequired": True})
    return t


# ---------------------------------------------------------------------------------------------------------------
# Maiasaura nesting colony: mounds of earth with clutches of eggs, the herd around them
# ---------------------------------------------------------------------------------------------------------------

def nest_colony(seed):
    rng = random.Random(seed)
    t = Template(21, 3, 21)
    for x in range(21):
        for z in range(21):
            r = math.hypot(x - 10, z - 10)
            if r <= 9.6 or (r <= 10.4 and rng.random() < 0.5):
                t.set(x, 0, z, "cracked_mud" if rng.random() < 0.3 else "packed_earth_floor")
                t.clear(x, 1, z, x, 2, z)
    nests = []
    for gx in (4, 10, 16):
        for gz in (4, 10, 16):
            if (gx, gz) == (10, 10) and rng.random() < 0.5:
                continue
            cx, cz = gx + rng.randint(-1, 1), gz + rng.randint(-1, 1)
            if math.hypot(cx - 10, cz - 10) > 8.5:
                continue
            nests.append((cx, cz))
    for cx, cz in nests:
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if dx or dz:
                    t.set(cx + dx, 0, cz + dz, "minecraft:coarse_dirt")
        cells = [(cx, cz), (cx + 1, cz), (cx, cz + 1), (cx - 1, cz), (cx, cz - 1)]
        rng.shuffle(cells)
        n_eggs = rng.randint(1, 3)
        for x, z in cells[:n_eggs]:
            t.set(x, 1, z, "maiasaura_egg", hatch="0")
        x, z = cells[n_eggs]
        t.set(x, 1, z, "straw_nest", facing=rng.choice(["north", "south", "east", "west"]))
    for x, z in ((7.5, 13.5), (13.5, 6.5), (3.5, 10.5), (16.5, 15.5)):
        t.entity(x, 1, z, {"id": f"{NS}:maiasaura"})
    return t


# ---------------------------------------------------------------------------------------------------------------
# Worldgen JSON, biome tags, loot
# ---------------------------------------------------------------------------------------------------------------

CRETACEOUS = lambda *ids: [f"{NS}:{i}" for i in ids]  # noqa: E731

STRUCTURE_LIST = [
    # id, templates {variant: builder}, biomes, terrain adaptation, spacing, separation, salt, set name
    ("katarina_camp_reed", {"reed": lambda: camp("reed", 11)},
     CRETACEOUS("hadrosaur_plains", "cypress_swamp", "river_delta") +
     ["minecraft:plains", "minecraft:sunflower_plains", "minecraft:meadow", "minecraft:swamp",
      "minecraft:mangrove_swamp"], "beard_thin", "katarina_camp"),
    ("katarina_camp_fern", {"fern": lambda: camp("fern", 12)},
     CRETACEOUS("magnolia_forest", "redwood_forest") + ["#minecraft:is_forest", "#minecraft:is_taiga",
                                                         "#minecraft:is_jungle"], "beard_thin", "katarina_camp"),
    ("katarina_camp_hide", {"hide": lambda: camp("hide", 13)},
     CRETACEOUS("dry_lands", "cretaceous_highlands") + ["#minecraft:is_savanna", "#minecraft:is_badlands",
                                                        "minecraft:desert", "minecraft:windswept_hills"],
     "beard_thin", "katarina_camp"),
    ("fossil_site", {"bank": lambda: fossil_site(21)},
     CRETACEOUS("dry_lands", "cretaceous_highlands", "hadrosaur_plains") +
     ["#minecraft:is_badlands", "#minecraft:is_savanna", "minecraft:desert", "#minecraft:is_hill",
      "minecraft:stony_shore"], "beard_thin", "fossil_site"),
    ("bone_bed", {"titanosaur": lambda: bone_bed(31)},
     CRETACEOUS("dry_lands", "river_delta", "hadrosaur_plains") +
     ["#minecraft:is_badlands", "#minecraft:is_savanna", "minecraft:desert"], "beard_thin", "bone_bed"),
    ("river_house", {"house": lambda: river_house(41)},
     CRETACEOUS("cretaceous_river", "river_delta", "hadrosaur_plains", "magnolia_forest", "redwood_forest",
                "cypress_swamp", "dry_lands", "cretaceous_beach") +
     ["#minecraft:is_river", "minecraft:plains", "minecraft:sunflower_plains", "minecraft:meadow", "minecraft:swamp",
      "minecraft:mangrove_swamp", "#minecraft:is_forest", "#minecraft:is_taiga", "#minecraft:is_jungle",
      "#minecraft:is_savanna", "#minecraft:is_beach", "minecraft:desert"], "beard_thin", "river_house"),
    ("nest_colony", {"maiasaura": lambda: nest_colony(51)},
     CRETACEOUS("hadrosaur_plains") + ["minecraft:plains", "minecraft:sunflower_plains", "minecraft:meadow",
                                       "#minecraft:is_savanna"], "beard_thin", "nest_colony"),
]

START_HEIGHT = {"river_house": -5}  # the house stands on stilts: its platform is 5 blocks above the template base

STRUCTURE_SETS = {
    # set: spacing, separation (chunks), salt  -- or a dict for a concentric_rings placement
    "katarina_camp": (30, 10, 1958241307),
    "fossil_site": (26, 9, 1958241308),
    "bone_bed": (40, 14, 1958241309),
    "nest_colony": (36, 12, 1958241310),
    # one Refuge per world, 220-420 blocks from the origin, pulled towards a river (like a stronghold)
    "river_house": {"type": "minecraft:concentric_rings", "distance": 5, "spread": 1, "count": 1,
                    "preferred_biomes": "#terrassic:refuge_preferred", "salt": 1958241311},
}

LOOT = {
    "katarina_camp": [
        {"rolls": 1, "entries": [{"type": "minecraft:item", "name": f"{NS}:loose_page"}]},
        {"rolls": {"type": "minecraft:uniform", "min": 2, "max": 4}, "entries": [
            {"type": "minecraft:item", "name": "minecraft:cooked_cod", "weight": 4,
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 1, "max": 3}}]},
            {"type": "minecraft:item", "name": "minecraft:cooked_salmon", "weight": 3,
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 1, "max": 3}}]},
            {"type": "minecraft:item", "name": "minecraft:cooked_beef", "weight": 2,
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 1, "max": 2}}]},
            {"type": "minecraft:item", "name": "minecraft:flint", "weight": 4,
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 2, "max": 5}}]},
            {"type": "minecraft:item", "name": "minecraft:string", "weight": 3,
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 1, "max": 3}}]},
            {"type": "minecraft:item", "name": "minecraft:bone", "weight": 3,
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 1, "max": 4}}]},
            {"type": "minecraft:item", "name": "minecraft:paper", "weight": 2,
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 1, "max": 2}}]},
            {"type": "minecraft:item", "name": f"{NS}:raw_amber", "weight": 1},
        ]},
        {"rolls": 1, "conditions": [{"condition": "minecraft:random_chance", "chance": 0.6}], "entries": [
            {"type": "minecraft:item", "name": f"{NS}:flint_knife"},
            {"type": "minecraft:item", "name": f"{NS}:hair_brush"},
            {"type": "minecraft:item", "name": f"{NS}:flint_chisel"},
            {"type": "minecraft:item", "name": f"{NS}:sketching_charcoal"},
            {"type": "minecraft:item", "name": f"{NS}:clay_jar"},
        ]},
    ],
    "katarina_refuge": [
        {"rolls": 2, "entries": [{"type": "minecraft:item", "name": f"{NS}:loose_page"}]},
        {"rolls": 1, "conditions": [{"condition": "minecraft:random_chance", "chance": 0.5}],
         "entries": [{"type": "minecraft:item", "name": f"{NS}:amber_lens"}]},
        {"rolls": {"type": "minecraft:uniform", "min": 3, "max": 5}, "entries": [
            {"type": "minecraft:item", "name": f"{NS}:clay_jar", "weight": 2},
            {"type": "minecraft:item", "name": f"{NS}:sketching_charcoal", "weight": 2},
            {"type": "minecraft:item", "name": f"{NS}:hair_brush", "weight": 1},
            {"type": "minecraft:item", "name": f"{NS}:raw_amber", "weight": 2,
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 1, "max": 3}}]},
            {"type": "minecraft:item", "name": "minecraft:paper", "weight": 3,
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 2, "max": 5}}]},
            {"type": "minecraft:item", "name": "minecraft:cooked_salmon", "weight": 2,
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 2, "max": 4}}]},
            {"type": "minecraft:item", "name": "minecraft:feather", "weight": 1,
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 2, "max": 6}}]},
        ]},
    ],
    "fossil_site": [
        {"rolls": 1, "entries": [{"type": "minecraft:item", "name": f"{NS}:hair_brush", "weight": 2},
                                 {"type": "minecraft:item", "name": f"{NS}:flint_chisel", "weight": 1}]},
        {"rolls": {"type": "minecraft:uniform", "min": 1, "max": 2}, "entries": [
            {"type": "minecraft:item", "name": f"{NS}:{s}_fossil"} for s in FOSSIL_SKULLS]},
        {"rolls": 1, "conditions": [{"condition": "minecraft:random_chance", "chance": 0.5}],
         "entries": [{"type": "minecraft:item", "name": f"{NS}:loose_page"}]},
        {"rolls": {"type": "minecraft:uniform", "min": 1, "max": 3}, "entries": [
            {"type": "minecraft:item", "name": "minecraft:bone",
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 2, "max": 6}}]},
            {"type": "minecraft:item", "name": "minecraft:flint",
             "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 1, "max": 4}}]},
            {"type": "minecraft:item", "name": "minecraft:paper"},
        ]},
    ],
}


# messages of the Refuge (world/KatarinaRefuge): (en_us, pt_br, es_es)
TEXTS = {
    "message.terrassic.mate_greets": ("%s sniffs your hands, finds Katarina's scent on you and accepts you.",
                                      "%s cheira as suas mãos, sente o cheiro da Katarina em você e aceita você.",
                                      "%s huele tus manos, reconoce el olor de Katarina en ti y te acepta."),
    "message.terrassic.refuge_direction": ("Katarina's Refuge: about %s blocks, heading %s",
                                           "Refúgio da Katarina: uns %s blocos, direção %s",
                                           "Refugio de Katarina: unos %s bloques, rumbo %s"),
    "message.terrassic.refuge_here": ("You are at Katarina's Refuge.", "Você está no Refúgio da Katarina.",
                                      "Estás en el Refugio de Katarina."),
    "message.terrassic.storm_start": ("The sky turns amber and time stutters... A Rift Storm! Creatures from other eras are coming through.",
                                      "O céu fica âmbar e o tempo falha... Uma Tempestade da Fenda! Criaturas de outras eras estão atravessando.",
                                      "El cielo se vuelve ámbar y el tiempo falla... ¡Una Tormenta de la Grieta! Criaturas de otras eras están cruzando."),
    "message.terrassic.storm_end": ("The Rift calms down. What came through goes back, unless someone tamed it.",
                                    "A Fenda se acalma. O que atravessou volta, a não ser que alguém tenha domado.",
                                    "La Grieta se calma. Lo que cruzó regresa, salvo que alguien lo haya domado."),
    "message.terrassic.refuge_unknown": ("The amber does not point anywhere here.",
                                         "O âmbar não aponta para lugar nenhum aqui.",
                                         "El ámbar no señala ningún lugar aquí."),
}
for _key, _words in {"n": ("north", "norte", "norte"), "ne": ("north-east", "nordeste", "noreste"),
                     "e": ("east", "leste", "este"), "se": ("south-east", "sudeste", "sureste"),
                     "s": ("south", "sul", "sur"), "sw": ("south-west", "sudoeste", "suroeste"),
                     "w": ("west", "oeste", "oeste"), "nw": ("north-west", "noroeste", "noroeste")}.items():
    TEXTS[f"direction.terrassic.{_key}"] = _words
LANG = {"en_us": {}, "pt_br": {}, "es_es": {}}
for _k, (_en, _pt, _es) in TEXTS.items():
    LANG["en_us"][_k], LANG["pt_br"][_k], LANG["es_es"][_k] = _en, _pt, _es


def main():
    sets = {}
    for sid, templates, biomes, adaptation, set_name in STRUCTURE_LIST:
        elements = []
        for variant, build in templates.items():
            build().save(os.path.join(STRUCTURES, sid, variant + ".nbt"))
            elements.append({"weight": 1, "element": {
                "element_type": "minecraft:single_pool_element", "location": f"{NS}:{sid}/{variant}",
                "processors": "minecraft:empty", "projection": "rigid"}})
        write(os.path.join(WG, "template_pool", sid, "start.json"), {"fallback": "minecraft:empty", "elements": elements})
        write(os.path.join(DATA, NS, "tags", "worldgen", "biome", "has_structure", sid + ".json"),
              {"replace": False, "values": biomes})
        write(os.path.join(WG, "structure", sid + ".json"), {
            "type": "minecraft:jigsaw", "biomes": f"#{NS}:has_structure/{sid}", "step": "surface_structures",
            "spawn_overrides": {}, "terrain_adaptation": adaptation, "start_pool": f"{NS}:{sid}/start", "size": 1,
            "start_height": {"absolute": START_HEIGHT.get(sid, -1)}, "project_start_to_heightmap": "WORLD_SURFACE_WG",
            "max_distance_from_center": 80, "use_expansion_hack": False})
        sets.setdefault(set_name, []).append(sid)
    for set_name, sids in sets.items():
        placement = STRUCTURE_SETS[set_name]
        if not isinstance(placement, dict):
            spacing, separation, salt = placement
            placement = {"type": "minecraft:random_spread", "spacing": spacing, "separation": separation, "salt": salt}
        write(os.path.join(WG, "structure_set", set_name + ".json"), {
            "structures": [{"structure": f"{NS}:{s}", "weight": 1} for s in sids], "placement": placement})
    write(os.path.join(DATA, NS, "tags", "worldgen", "biome", "refuge_preferred.json"), {"replace": False, "values": [
        f"{NS}:cretaceous_river", f"{NS}:river_delta", "#minecraft:is_river"]})
    write(os.path.join(DATA, NS, "tags", "worldgen", "structure", "katarina_refuge.json"),
          {"replace": False, "values": [f"{NS}:river_house"]})
    for name, pools in LOOT.items():
        write(os.path.join(DATA, NS, "loot_tables", "chests", name + ".json"), {"type": "minecraft:chest", "pools": pools})
    print(f"{len(STRUCTURE_LIST)} structures written ({len(sets)} structure sets)")


if __name__ == "__main__":
    main()
