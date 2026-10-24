"""Generates the JSON resources of the primitive building blocks: block/item models, blockstates, recipes,
loot tables and block tags.  Lang entries are exported in LANG and merged by gen_resources.py.

Block ids must match ModBlocks.BUILDING (Java).  Textures come from tools/spritegen/blocks.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from gen_resources import A, D, write  # noqa: E402

NS = "terrassic"

# id: (en, pt, es, kind, texture(s), mineable tool)
# kind: cube | column | stairs | slab | wall | fence | pane | carpet | palisade
BLOCKS = {
    "thatch": ("Thatch", "Palha", "Paja", "column", ("thatch", "thatch_top"), "hoe"),
    "thatch_stairs": ("Thatch Stairs", "Escada de Palha", "Escaleras de Paja", "stairs", ("thatch", "thatch_top"), "hoe"),
    "thatch_slab": ("Thatch Slab", "Laje de Palha", "Losa de Paja", "slab", ("thatch", "thatch_top", "thatch"), "hoe"),
    "straw_mat": ("Straw Mat", "Esteira de Palha", "Estera de Paja", "carpet", "straw_mat", "hoe"),
    "wattle_and_daub": ("Wattle and Daub", "Pau a Pique", "Bahareque", "cube", "wattle_and_daub", "axe"),
    "log_palisade": ("Log Palisade", "Paliçada de Troncos", "Empalizada de Troncos", "palisade", ("log_palisade", "log_palisade_top"), "axe"),
    "dry_stone": ("Dry Stone", "Pedra Empilhada", "Piedra Seca", "cube", "dry_stone", "pickaxe"),
    "dry_stone_stairs": ("Dry Stone Stairs", "Escada de Pedra Empilhada", "Escaleras de Piedra Seca", "stairs", ("dry_stone",) * 2, "pickaxe"),
    "dry_stone_slab": ("Dry Stone Slab", "Laje de Pedra Empilhada", "Losa de Piedra Seca", "slab", ("dry_stone", "dry_stone", "dry_stone"), "pickaxe"),
    "dry_stone_wall": ("Dry Stone Wall", "Muro de Pedra Empilhada", "Muro de Piedra Seca", "wall", "dry_stone", "pickaxe"),
    "bone_fence": ("Bone Fence", "Cerca de Osso", "Valla de Hueso", "fence", "bone_fence", "pickaxe"),
    "hide_screen": ("Hide Screen", "Painel de Couro", "Panel de Cuero", "pane", ("hide_screen", "hide_screen_edge"), "axe"),
    "fur_rug": ("Fur Rug", "Tapete de Pele", "Alfombra de Piel", "carpet", "fur_rug", "axe"),
}

LANG = {"en_us": {}, "pt_br": {}, "es_es": {}}
for _bid, (_en, _pt, _es, *_rest) in BLOCKS.items():
    LANG["en_us"][f"block.{NS}.{_bid}"] = _en
    LANG["pt_br"][f"block.{NS}.{_bid}"] = _pt
    LANG["es_es"][f"block.{NS}.{_bid}"] = _es
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


# ------------------------------------------------------------- per kind
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
    side, end, _ = tex
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
                uv["uv"] = [x0 if f in ("north", "south") else z0, 16 - body_top,
                            (x0 if f in ("north", "south") else z0) + 8, 16]
        elements.append({"from": [x0, 0, z0], "to": [x0 + 8, body_top, z0 + 8], "faces": faces})
        # sharpened tip: two narrowing steps
        for step, inset in ((1, 1.5), (2, 3)):
            y0 = body_top + (step - 1) * 1.5
            y1 = body_top + step * 1.5
            tip = {f: {"texture": "#top"} for f in ("north", "south", "east", "west", "up")}
            elements.append({"from": [x0 + inset, y0, z0 + inset], "to": [x0 + 8 - inset, y1, z0 + 8 - inset], "faces": tip})
    return {"parent": "minecraft:block/block", "textures": {"side": t(side), "top": t(top), "particle": t(side)},
            "elements": elements}


def gen_palisade(bid, tex):
    write(f"{A}/models/block/{bid}.json", palisade_model(*tex))
    write(f"{A}/blockstates/{bid}.json", {"variants": {"": variant(bid)}})
    return m(bid)


# ------------------------------------------------------------- loot, recipes, tags
def loot_self(bid):
    write(f"{D}/loot_tables/blocks/{bid}.json", {"type": "minecraft:block", "pools": [{
        "rolls": 1, "bonus_rolls": 0, "entries": [{"type": "minecraft:item", "name": f"{NS}:{bid}"}],
        "conditions": [{"condition": "minecraft:survives_explosion"}]}]})


def loot_slab(bid):
    write(f"{D}/loot_tables/blocks/{bid}.json", {"type": "minecraft:block", "pools": [{
        "rolls": 1, "bonus_rolls": 0, "entries": [{"type": "minecraft:item", "name": f"{NS}:{bid}", "functions": [
            {"function": "minecraft:set_count", "count": 2, "add": False, "conditions": [
                {"condition": "minecraft:block_state_property", "block": f"{NS}:{bid}", "properties": {"type": "double"}}]},
            {"function": "minecraft:explosion_decay"}]}]}]})


def shaped(name, pattern, key, result, count=1):
    write(f"{D}/recipes/{name}.json", {
        "type": "minecraft:crafting_shaped", "category": "building", "pattern": pattern,
        "key": {k: ({"tag": v[1:]} if v.startswith("#") else {"item": v}) for k, v in key.items()},
        "result": {"item": f"{NS}:{result}", "count": count}})


def recipes():
    shaped("thatch", ["WW", "WW"], {"W": "minecraft:wheat"}, "thatch", 2)
    shaped("thatch_stairs", ["T  ", "TT ", "TTT"], {"T": f"{NS}:thatch"}, "thatch_stairs", 4)
    shaped("thatch_slab", ["TTT"], {"T": f"{NS}:thatch"}, "thatch_slab", 6)
    shaped("straw_mat", ["TT"], {"T": f"{NS}:thatch"}, "straw_mat", 3)
    shaped("wattle_and_daub", ["SM", "MS"], {"S": "minecraft:stick", "M": "minecraft:mud"}, "wattle_and_daub", 2)
    shaped("log_palisade", [" F ", "LLL", "LLL"], {"F": "minecraft:flint", "L": "#minecraft:logs"}, "log_palisade", 6)
    shaped("dry_stone", ["CC", "CC"], {"C": "minecraft:cobblestone"}, "dry_stone", 4)
    shaped("dry_stone_stairs", ["D  ", "DD ", "DDD"], {"D": f"{NS}:dry_stone"}, "dry_stone_stairs", 4)
    shaped("dry_stone_slab", ["DDD"], {"D": f"{NS}:dry_stone"}, "dry_stone_slab", 6)
    shaped("dry_stone_wall", ["DDD", "DDD"], {"D": f"{NS}:dry_stone"}, "dry_stone_wall", 6)
    shaped("bone_fence", ["BTB", "BTB"], {"B": "minecraft:bone", "T": "minecraft:string"}, "bone_fence", 3)
    shaped("hide_screen", ["SLS", "SLS"], {"S": "minecraft:stick", "L": "minecraft:leather"}, "hide_screen", 4)
    shaped("fur_rug", ["LL"], {"L": "minecraft:leather"}, "fur_rug", 2)


def tags():
    by_tool = {}
    for bid, (_, _, _, kind, _, tool) in BLOCKS.items():
        by_tool.setdefault(tool, []).append(f"{NS}:{bid}")
    mc = os.path.join(os.path.dirname(D), "minecraft", "tags", "blocks")
    for tool, ids in by_tool.items():
        write(os.path.join(mc, "mineable", f"{tool}.json"), {"replace": False, "values": ids})
    kinds = {"stairs": "stairs", "slab": "slabs", "wall": "walls", "fence": "fences"}
    for kind, tag in kinds.items():
        ids = [f"{NS}:{b}" for b, v in BLOCKS.items() if v[3] == kind]
        write(os.path.join(mc, f"{tag}.json"), {"replace": False, "values": ids})
    item_tags = os.path.join(os.path.dirname(D), "minecraft", "tags", "items")
    for kind, tag in (("stairs", "stairs"), ("slab", "slabs"), ("wall", "walls"), ("fence", "fences")):
        ids = [f"{NS}:{b}" for b, v in BLOCKS.items() if v[3] == kind]
        write(os.path.join(item_tags, f"{tag}.json"), {"replace": False, "values": ids})


def main():
    full_models = {}
    for bid, (_, _, _, kind, tex, _) in BLOCKS.items():
        if kind == "cube":
            item_model = gen_cube(bid, tex)
        elif kind == "column":
            item_model = gen_column(bid, tex)
        elif kind == "stairs":
            item_model = gen_stairs(bid, tex)
        elif kind == "slab":
            full = m(bid.replace("_slab", ""))
            item_model = gen_slab(bid, tex, full)
        elif kind == "wall":
            item_model = gen_wall(bid, tex)
        elif kind == "fence":
            item_model = gen_fence(bid, tex)
        elif kind == "pane":
            item_model = gen_pane(bid, tex)
        elif kind == "carpet":
            item_model = gen_carpet(bid, tex)
        elif kind == "palisade":
            item_model = gen_palisade(bid, tex)
        else:
            raise ValueError(kind)
        full_models[bid] = item_model
        if item_model is None:
            write(f"{A}/models/item/{bid}.json", {"parent": "minecraft:item/generated", "textures": {"layer0": t(tex[0])}})
        else:
            write(f"{A}/models/item/{bid}.json", {"parent": item_model})
        (loot_slab if kind == "slab" else loot_self)(bid)
    recipes()
    tags()
    print("building block resources written")


if __name__ == "__main__":
    main()
