"""Branch mc/1.21.1: the generators keep writing the 1.20.1 data layout (so merges from main stay easy); this last step
turns it into the 1.21 layout. Called at the end of gen_resources.py.

Folders became singular, recipes and icons name their item with "id", item predicates take "items" with a #tag, and
enchantment checks moved into "predicates". Vanilla's block texture grass.png is short_grass.png since 1.20.3, and a
creature that breathes under water is now listed in a tag instead of overriding a method.
"""
import json
import os
import re
import shutil

import gen_species

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RES = os.path.join(ROOT, "common", "src", "main", "resources")
DATA = os.path.join(RES, "data")
PACKS = os.path.join(RES, "resourcepacks")
ERA_PACK_FORMAT = 34

RENAMED = {"recipes": "recipe", "advancements": "advancement", "loot_tables": "loot_table", "structures": "structure"}
TAGS = {"blocks": "block", "items": "item", "entity_types": "entity_type", "fluids": "fluid"}


def move(old, new):
    """Old folder over new: what the generators just wrote wins, and nothing stale survives."""
    if not os.path.isdir(old):
        return
    if os.path.isdir(new):
        shutil.rmtree(new)
    os.rename(old, new)


def predicate(item):
    out = dict(item)
    tag = out.pop("tag", None)
    if tag:
        out["items"] = "#" + tag
    enchantments = out.pop("enchantments", None)
    if enchantments:
        out["predicates"] = {"minecraft:enchantments": [
            {"enchantments": e["enchantment"], **({"levels": e["levels"]} if "levels" in e else {})} for e in enchantments]}
    return out


def walk_predicates(node):
    """Every item predicate of a loot table or advancement, wherever it sits."""
    if isinstance(node, dict):
        if node.get("condition") == "minecraft:match_tool":
            node["predicate"] = predicate(node["predicate"])
        conditions = node.get("conditions")
        if isinstance(conditions, dict) and isinstance(conditions.get("items"), list):
            conditions["items"] = [predicate(i) for i in conditions["items"]]
        for value in node.values():
            walk_predicates(value)
    elif isinstance(node, list):
        for value in node:
            walk_predicates(value)


def recipe(doc):
    result = doc.get("result")
    if isinstance(result, str):
        doc["result"] = {"id": result}
        if "count" in doc:
            doc["result"]["count"] = doc.pop("count")
    elif isinstance(result, dict) and "item" in result:
        result["id"] = result.pop("item")


def rewrite(path, change):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    doc = json.loads(text)
    change(doc)
    out = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    if out != text:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(out)


def advancement(doc):
    icon = doc.get("display", {}).get("icon")
    if icon and "item" in icon:
        icon["id"] = icon.pop("item")
    walk_predicates(doc)


def json_files(folder):
    for d, _, fs in os.walk(folder):
        for f in fs:
            if f.endswith(".json"):
                yield os.path.join(d, f)


def water_breathers():
    ids = [f"terrassic:{s['id']}" for s in gen_species.SPECIES if s.get("fish") or s.get("base") == "SwimmingDinosaur"]
    ids += ["terrassic:spinosaurus", "terrassic:deinosuchus"]
    path = os.path.join(DATA, "minecraft", "tags", "entity_type", "can_breathe_under_water.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"replace": False, "values": sorted(set(ids))}, f, indent=2)
        f.write("\n")


def era_packs():
    for era in os.listdir(PACKS):
        meta = os.path.join(PACKS, era, "pack.mcmeta")
        if not os.path.isfile(meta):
            continue
        rewrite(meta, lambda doc: doc["pack"].update(pack_format=ERA_PACK_FORMAT))
        old = os.path.join(PACKS, era, "assets", "minecraft", "textures", "block", "grass.png")
        if os.path.isfile(old):
            os.replace(old, old.replace("grass.png", "short_grass.png"))


def main():
    for ns in os.listdir(DATA):
        base = os.path.join(DATA, ns)
        for old, new in RENAMED.items():
            move(os.path.join(base, old), os.path.join(base, new))
        for old, new in TAGS.items():
            move(os.path.join(base, "tags", old), os.path.join(base, "tags", new))
        for path in json_files(os.path.join(base, "recipe")):
            rewrite(path, recipe)
        for path in json_files(os.path.join(base, "advancement")):
            rewrite(path, advancement)
        for path in json_files(os.path.join(base, "loot_table")):
            rewrite(path, walk_predicates)
    water_breathers()
    era_packs()


if __name__ == "__main__":
    main()
