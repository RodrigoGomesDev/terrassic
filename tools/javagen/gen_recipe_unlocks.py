"""Recipe book unlocks (v1.0.2): one vanilla-style advancement per recipe of the mod.

The game shows a recipe in the recipe book only after the player unlocks it, and vanilla unlocks its own recipes
with hidden advancements under advancements/recipes/ (pick up one of the ingredients -> the recipe is learned).
The mod had none, so its recipes worked on the crafting table but never showed in the book: without JEI nobody
found out how to make the blowgun, the bow or the spears. This script reads every recipe the other generators
wrote and gives each the same kind of advancement. Run by gen_resources.py at the end; can also run alone.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D = os.path.join(ROOT, "common", "src", "main", "resources", "data", "terrassic")
RECIPES = os.path.join(D, "recipes")
OUT = os.path.join(D, "advancements", "recipes")

# recipe book tab of each recipe type when the recipe has no "category"
DEFAULT_CATEGORY = {"minecraft:stonecutting": "building_blocks"}


def _ingredients(recipe):
    """Every distinct ingredient of the recipe, as ('item'|'tag', id)."""
    kind = recipe["type"]
    if kind == "minecraft:crafting_shaped":
        raw = list(recipe["key"].values())
    elif kind == "minecraft:crafting_shapeless":
        raw = list(recipe["ingredients"])
    else:
        raw = [recipe["ingredient"]]
    found = []
    for ing in raw:
        for alt in ing if isinstance(ing, list) else [ing]:
            key = ("item", alt["item"]) if "item" in alt else ("tag", alt["tag"])
            if key not in found:
                found.append(key)
    return found


def _criterion_name(key):
    return "has_" + key[1].split(":")[-1].replace("/", "_")


def unlock(name, recipe):
    rid = f"terrassic:{name}"
    criteria = {"has_the_recipe": {"trigger": "minecraft:recipe_unlocked", "conditions": {"recipe": rid}}}
    for key in _ingredients(recipe):
        predicate = {"items": [key[1]]} if key[0] == "item" else {"tag": key[1]}
        cname = _criterion_name(key)
        if cname in criteria:  # minecraft:flint and terrassic:flint
            cname = "has_" + key[1].replace(":", "_").replace("/", "_")
        criteria[cname] = {"trigger": "minecraft:inventory_changed", "conditions": {"items": [predicate]}}
    return {
        "parent": "minecraft:recipes/root",
        "criteria": criteria,
        "requirements": [sorted(criteria)],
        "rewards": {"recipes": [rid]},
        "sends_telemetry_event": False,
    }


def main():
    # regenerated from scratch: a recipe that was removed takes its unlock with it
    if os.path.isdir(OUT):
        for base, _, files in os.walk(OUT, topdown=False):
            for f in files:
                os.remove(os.path.join(base, f))
            os.rmdir(base)
    count = 0
    for file in sorted(os.listdir(RECIPES)):
        if not file.endswith(".json"):
            continue
        with open(os.path.join(RECIPES, file), encoding="utf-8") as f:
            recipe = json.load(f)
        name = file[:-5]
        category = recipe.get("category", DEFAULT_CATEGORY.get(recipe["type"], "misc"))
        path = os.path.join(OUT, category, file)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(unlock(name, recipe), f, indent=2, ensure_ascii=False)
            f.write("\n")
        count += 1
    print(f"recipe unlocks written: {count}")


if __name__ == "__main__":
    main()
