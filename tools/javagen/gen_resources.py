"""Generates the JSON resources: item/block models, blockstates, lang (en_us, pt_br), recipes and loot tables."""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RES = os.path.join(ROOT, "common", "src", "main", "resources")
A = os.path.join(RES, "assets", "primalera")
D = os.path.join(RES, "data", "primalera")

SPECIES = {  # id: (en, pt, large egg)
    "tyrannosaurus": ("Tyrannosaurus", "Tiranossauro", True),
    "spinosaurus": ("Spinosaurus", "Espinossauro", True),
    "dilophosaurus": ("Dilophosaurus", "Dilofossauro", False),
    "velociraptor": ("Velociraptor", "Velociraptor", False),
    "compsognathus": ("Compsognathus", "Compsognato", False),
    "triceratops": ("Triceratops", "Tricerátops", True),
    "stegosaurus": ("Stegosaurus", "Estegossauro", True),
    "ankylosaurus": ("Ankylosaurus", "Anquilossauro", True),
    "brachiosaurus": ("Brachiosaurus", "Braquiossauro", True),
    "parasaurolophus": ("Parasaurolophus", "Parassaurolofo", True),
    "pachycephalosaurus": ("Pachycephalosaurus", "Paquicefalossauro", False),
    "gallimimus": ("Gallimimus", "Galimimo", False),
}

ITEMS = {  # id: (en, pt, model parent)
    "rex_tooth": ("T. rex Tooth", "Dente de Tiranossauro", "item/generated"),
    "triceratops_horn": ("Triceratops Horn", "Chifre de Tricerátops", "item/generated"),
    "ankylosaurus_club": ("Ankylosaurus Tail Club", "Clava Caudal de Anquilossauro", "item/generated"),
    "flint_knife": ("Flint Knife", "Faca de Sílex", "item/handheld"),
    "flint_hatchet": ("Flint Hatchet", "Machadinha de Sílex", "item/handheld"),
    "bone_club": ("Bone Club", "Clava de Osso", "item/handheld"),
    "flint_spear": ("Flint Spear", "Lança de Sílex", "item/handheld"),
    "horn_spear": ("Horn Spear", "Lança de Chifre", "item/handheld"),
    "rex_tooth_dagger": ("T. rex Tooth Dagger", "Adaga de Dente de Tiranossauro", "item/handheld"),
    "tail_club": ("Tail Club", "Clava de Cauda", "item/handheld"),
}

LANG_EXTRA = {
    "en_us": {
        "itemGroup.primalera.main": "PrimalEra",
        "entity.primalera.spear": "Spear",
        "message.primalera.sit": "%s is resting",
        "message.primalera.follow": "%s is following you",
        "message.primalera.tamed": "You tamed %s (%s)!",
        "sex.primalera.male": "male",
        "sex.primalera.female": "female",
    },
    "pt_br": {
        "itemGroup.primalera.main": "PrimalEra",
        "entity.primalera.spear": "Lança",
        "message.primalera.sit": "%s está descansando",
        "message.primalera.follow": "%s está te seguindo",
        "message.primalera.tamed": "Você domesticou %s (%s)!",
        "sex.primalera.male": "macho",
        "sex.primalera.female": "fêmea",
    },
}


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def egg_model(sid, stage, large):
    tex = f"primalera:block/{sid}_egg_{stage}"
    if large:
        els = [([4, 0, 4], [12, 9, 12]), ([5, 9, 5], [11, 12, 11]), ([6, 12, 6], [10, 13, 10])]
    else:
        els = [([5, 0, 5], [11, 6, 11]), ([6, 6, 6], [10, 8, 10]), ([7, 8, 7], [9, 9, 9])]
    elements = []
    for frm, to in els:
        faces = {f: {"texture": "#egg"} for f in ("north", "south", "east", "west", "up", "down")}
        faces["down"]["cullface"] = "down" if frm[1] == 0 else None
        if faces["down"]["cullface"] is None:
            del faces["down"]["cullface"]
        elements.append({"from": frm, "to": to, "faces": faces})
    return {"parent": "block/block", "textures": {"egg": tex, "particle": tex}, "elements": elements,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 2 if not large else 0, 0], "scale": [0.8 if large else 1.1] * 3}}}


def main():
    lang = {"en_us": dict(LANG_EXTRA["en_us"]), "pt_br": dict(LANG_EXTRA["pt_br"])}
    for sid, (en, pt, large) in SPECIES.items():
        lang["en_us"][f"entity.primalera.{sid}"] = en
        lang["pt_br"][f"entity.primalera.{sid}"] = pt
        lang["en_us"][f"item.primalera.{sid}_spawn_egg"] = f"{en} Spawn Egg"
        lang["pt_br"][f"item.primalera.{sid}_spawn_egg"] = f"Ovo Gerador de {pt}"
        lang["en_us"][f"block.primalera.{sid}_egg"] = f"{en} Egg"
        lang["pt_br"][f"block.primalera.{sid}_egg"] = f"Ovo de {pt}"
        # unique spawn egg sprite (layer0 only; tint colours are white)
        write(f"{A}/models/item/{sid}_spawn_egg.json", {"parent": "item/generated", "textures": {"layer0": f"primalera:item/{sid}_spawn_egg"}})
        # egg block: 3 hatch stages
        for st in range(3):
            write(f"{A}/models/block/{sid}_egg_{st}.json", egg_model(sid, st, large))
        write(f"{A}/blockstates/{sid}_egg.json", {"variants": {f"hatch={st}": {"model": f"primalera:block/{sid}_egg_{st}"} for st in range(3)}})
        write(f"{A}/models/item/{sid}_egg.json", {"parent": f"primalera:block/{sid}_egg_0"})
        write(f"{D}/loot_tables/blocks/{sid}_egg.json", {"type": "minecraft:block", "pools": [{
            "rolls": 1, "entries": [{"type": "minecraft:item", "name": f"primalera:{sid}_egg"}],
            "conditions": [{"condition": "minecraft:block_state_property", "block": f"primalera:{sid}_egg",
                            "properties": {"hatch": "0"}}, {"condition": "minecraft:survives_explosion"}]}]})
    for iid, (en, pt, parent) in ITEMS.items():
        lang["en_us"][f"item.primalera.{iid}"] = en
        lang["pt_br"][f"item.primalera.{iid}"] = pt
        write(f"{A}/models/item/{iid}.json", {"parent": parent, "textures": {"layer0": f"primalera:item/{iid}"}})
    for code, data in lang.items():
        write(f"{A}/lang/{code}.json", dict(sorted(data.items())))

    # ------------------------------------------------------------- recipes
    def shaped(name, pattern, key, result, count=1):
        write(f"{D}/recipes/{name}.json", {"type": "minecraft:crafting_shaped", "category": "equipment", "pattern": pattern,
                                         "key": {k: {"item": v} for k, v in key.items()},
                                         "result": {"item": result, "count": count}})
    shaped("flint_knife", ["F", "S"], {"F": "minecraft:flint", "S": "minecraft:stick"}, "primalera:flint_knife")
    shaped("flint_hatchet", ["FF", "FS", " S"], {"F": "minecraft:flint", "S": "minecraft:stick"}, "primalera:flint_hatchet")
    shaped("bone_club", [" X", "B "], {"X": "minecraft:bone_block", "B": "minecraft:bone"}, "primalera:bone_club")
    shaped("flint_spear", ["  F", " T ", "S  "], {"F": "minecraft:flint", "T": "minecraft:string", "S": "minecraft:stick"}, "primalera:flint_spear")
    shaped("horn_spear", ["  H", " T ", "S  "], {"H": "primalera:triceratops_horn", "T": "minecraft:string", "S": "minecraft:stick"}, "primalera:horn_spear")
    shaped("rex_tooth_dagger", ["T", "L"], {"T": "primalera:rex_tooth", "L": "minecraft:leather"}, "primalera:rex_tooth_dagger")
    shaped("tail_club", [" C", "S "], {"C": "primalera:ankylosaurus_club", "S": "minecraft:stick"}, "primalera:tail_club")

    # ------------------------------------------------------------- entity loot
    def item(name, lo, hi, smelt=False, chance=None):
        fns = [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}}]
        if smelt:
            fns.append({"function": "minecraft:furnace_smelt", "conditions": [
                {"condition": "minecraft:entity_properties", "entity": "this", "predicate": {"flags": {"is_on_fire": True}}}]})
        fns.append({"function": "minecraft:looting_enchant", "count": {"type": "minecraft:uniform", "min": 0, "max": 1}})
        pool = {"rolls": 1, "entries": [{"type": "minecraft:item", "name": name, "functions": fns}]}
        if chance is not None:
            pool["conditions"] = [{"condition": "minecraft:killed_by_player"},
                                  {"condition": "minecraft:random_chance_with_looting", "chance": chance, "looting_multiplier": 0.1}]
        return pool
    loot = {
        "tyrannosaurus": [item("minecraft:beef", 4, 8, True), item("minecraft:bone", 2, 5), item("primalera:rex_tooth", 1, 2, chance=0.6)],
        "spinosaurus": [item("minecraft:beef", 3, 7, True), item("minecraft:bone", 2, 4), item("minecraft:cod", 1, 3, True)],
        "dilophosaurus": [item("minecraft:mutton", 1, 3, True), item("minecraft:bone", 1, 2)],
        "velociraptor": [item("minecraft:chicken", 1, 2, True), item("minecraft:feather", 1, 3)],
        "compsognathus": [item("minecraft:chicken", 0, 1, True), item("minecraft:feather", 0, 2)],
        "triceratops": [item("minecraft:beef", 3, 6, True), item("minecraft:leather", 2, 4), item("primalera:triceratops_horn", 1, 2, chance=0.5)],
        "stegosaurus": [item("minecraft:beef", 2, 5, True), item("minecraft:leather", 1, 3)],
        "ankylosaurus": [item("minecraft:beef", 2, 5, True), item("minecraft:leather", 2, 4), item("primalera:ankylosaurus_club", 1, 1, chance=0.4)],
        "brachiosaurus": [item("minecraft:beef", 8, 14, True), item("minecraft:leather", 4, 8), item("minecraft:bone", 4, 8)],
        "parasaurolophus": [item("minecraft:beef", 2, 5, True), item("minecraft:leather", 1, 3)],
        "pachycephalosaurus": [item("minecraft:mutton", 1, 3, True), item("minecraft:bone", 1, 2)],
        "gallimimus": [item("minecraft:chicken", 1, 3, True), item("minecraft:feather", 2, 4)],
    }
    for sid, pools in loot.items():
        write(f"{D}/loot_tables/entities/{sid}.json", {"type": "minecraft:entity", "pools": pools})
    print("resources written")


if __name__ == "__main__":
    main()
