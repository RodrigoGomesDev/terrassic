"""Generates the JSON resources: item/block models, blockstates, lang (en_us, pt_br, es_es + other Spanish
variants), recipes and loot tables."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RES = os.path.join(ROOT, "common", "src", "main", "resources")
A = os.path.join(RES, "assets", "terrassic")
D = os.path.join(RES, "data", "terrassic")

SPECIES = {  # id: (en, pt, es, large egg; None = no egg block, e.g. live-bearing marine reptiles)
    "tyrannosaurus": ("Tyrannosaurus", "Tiranossauro", "Tiranosaurio", True),
    "spinosaurus": ("Spinosaurus", "Espinossauro", "Espinosaurio", True),
    "dilophosaurus": ("Dilophosaurus", "Dilofossauro", "Dilofosaurio", False),
    "velociraptor": ("Velociraptor", "Velociraptor", "Velociraptor", False),
    "compsognathus": ("Compsognathus", "Compsognato", "Compsognathus", False),
    "triceratops": ("Triceratops", "Tricerátops", "Triceratops", True),
    "styracosaurus": ("Styracosaurus", "Estiracossauro", "Styracosaurus", True),
    "pachyrhinosaurus": ("Pachyrhinosaurus", "Paquirrinossauro", "Pachyrhinosaurus", True),
    "protoceratops": ("Protoceratops", "Protoceratops", "Protoceratops", False),
    "stegosaurus": ("Stegosaurus", "Estegossauro", "Estegosaurio", True),
    "ankylosaurus": ("Ankylosaurus", "Anquilossauro", "Anquilosaurio", True),
    "euoplocephalus": ("Euoplocephalus", "Euoplocéfalo", "Euoplocephalus", True),
    "therizinosaurus": ("Therizinosaurus", "Terizinossauro", "Therizinosaurus", True),
    "deinocheirus": ("Deinocheirus", "Deinocheirus", "Deinocheirus", True),
    "brachiosaurus": ("Brachiosaurus", "Braquiossauro", "Braquiosaurio", True),
    "alamosaurus": ("Alamosaurus", "Alamossauro", "Alamosaurio", True),
    "saltasaurus": ("Saltasaurus", "Saltassauro", "Saltasaurio", True),
    "argentinosaurus": ("Argentinosaurus", "Argentinossauro", "Argentinosaurio", True),
    "opisthocoelicaudia": ("Opisthocoelicaudia", "Opisthocoelicaudia", "Opisthocoelicaudia", True),
    "dreadnoughtus": ("Dreadnoughtus", "Dreadnoughtus", "Dreadnoughtus", True),
    "parasaurolophus": ("Parasaurolophus", "Parassaurolofo", "Parasaurolophus", True),
    "pachycephalosaurus": ("Pachycephalosaurus", "Paquicefalossauro", "Paquicefalosaurio", False),
    "thescelosaurus": ("Thescelosaurus", "Tescelossauro", "Thescelosaurus", False),
    "gallimimus": ("Gallimimus", "Galimimo", "Gallimimus", False),
    "struthiomimus": ("Struthiomimus", "Estrutiomimo", "Struthiomimus", False),
    "maiasaura": ("Maiasaura", "Maiassaura", "Maiasaura", False),
    "pteranodon": ("Pteranodon", "Pteranodonte", "Pteranodonte", False),
    "quetzalcoatlus": ("Quetzalcoatlus", "Quetzalcoatlus", "Quetzalcoatlus", False),
    "hatzegopteryx": ("Hatzegopteryx", "Hatzegopteryx", "Hatzegopteryx", False),
    "ichthyornis": ("Ichthyornis", "Ictiórnis", "Ictiornis", False),
    "mosasaurus": ("Mosasaurus", "Mosassauro", "Mosasaurio", None),
    "tylosaurus": ("Tylosaurus", "Tilossauro", "Tilosaurio", None),
    "elasmosaurus": ("Elasmosaurus", "Elasmossauro", "Elasmosaurio", None),
    "xiphactinus": ("Xiphactinus", "Xifactino", "Xiphactinus", None),
    "archelon": ("Archelon", "Archelon", "Archelon", True),
    "hesperornis": ("Hesperornis", "Hesperórnis", "Hesperornis", False),
    "deinosuchus": ("Deinosuchus", "Deinossuco", "Deinosuchus", True),
    "baurusuchus": ("Baurusuchus", "Baurussuco", "Baurusuchus", False),
    "edmontosaurus": ("Edmontosaurus", "Edmontossauro", "Edmontosaurio", True),
    "corythosaurus": ("Corythosaurus", "Coritossauro", "Corythosaurus", False),
}

ITEMS = {  # id: (en, pt, es, model parent)
    "rex_tooth": ("T. rex Tooth", "Dente de Tiranossauro", "Diente de Tiranosaurio", "item/generated"),
    "mosasaurus_tooth": ("Mosasaurus Tooth", "Dente de Mosassauro", "Diente de Mosasaurio", "item/generated"),
    "triceratops_horn": ("Triceratops Horn", "Chifre de Tricerátops", "Cuerno de Triceratops", "item/generated"),
    "ankylosaurus_club": ("Ankylosaurus Tail Club", "Clava Caudal de Anquilossauro", "Maza Caudal de Anquilosaurio", "item/generated"),
    "flint_knife": ("Flint Knife", "Faca de Sílex", "Cuchillo de Sílex", "item/handheld"),
    "flint_hatchet": ("Flint Hatchet", "Machadinha de Sílex", "Hacha de Mano de Sílex", "item/handheld"),
    "bone_club": ("Bone Club", "Clava de Osso", "Garrote de Hueso", "item/handheld"),
    "flint_spear": ("Flint Spear", "Lança de Sílex", "Lanza de Sílex", "item/handheld"),
    "horn_spear": ("Horn Spear", "Lança de Chifre", "Lanza de Cuerno", "item/handheld"),
    "rex_tooth_dagger": ("T. rex Tooth Dagger", "Adaga de Dente de Tiranossauro", "Daga de Diente de Tiranosaurio", "item/handheld"),
    "tail_club": ("Tail Club", "Clava de Cauda", "Garrote de Cola", "item/handheld"),
}

LANG_EXTRA = {
    "en_us": {
        "itemGroup.terrassic.main": "Terrassic",
        "entity.terrassic.spear": "Spear",
        "message.terrassic.sit": "%s is resting",
        "message.terrassic.follow": "%s is following you",
        "message.terrassic.tamed": "You tamed %s (%s)!",
        "message.terrassic.perch": "%s is perched on your shoulder (sneak to shake it off)",
        "message.terrassic.perch_warn": "%s shrieks: something is after you!",
        "message.terrassic.perch_fish": "%s dove and brought you a fish",
        "message.terrassic.cargo_chest": "%s carries cargo now: sneak and use it with an empty hand to open the chest",
        "message.terrassic.cargo_chest_ride": "%s carries cargo now: sneak + use without a saddle, or the inventory key while riding",
        "message.terrassic.cargo_off": "%s dropped its cargo chest",
        "sex.terrassic.male": "male",
        "sex.terrassic.female": "female",
    },
    "pt_br": {
        "itemGroup.terrassic.main": "Terrassic",
        "entity.terrassic.spear": "Lança",
        "message.terrassic.sit": "%s está descansando",
        "message.terrassic.follow": "%s está te seguindo",
        "message.terrassic.tamed": "Você domesticou %s (%s)!",
        "message.terrassic.perch": "%s pousou no seu ombro (agache para soltar)",
        "message.terrassic.perch_warn": "%s grita: tem algo atrás de você!",
        "message.terrassic.perch_fish": "%s mergulhou e te trouxe um peixe",
        "message.terrassic.cargo_chest": "%s agora leva carga: agache e use com a mão vazia para abrir o baú",
        "message.terrassic.cargo_chest_ride": "%s agora leva carga: agachar + usar sem sela, ou a tecla do inventário montado",
        "message.terrassic.cargo_off": "%s largou o baú de carga",
        "sex.terrassic.male": "macho",
        "sex.terrassic.female": "fêmea",
    },
    "es_es": {
        "itemGroup.terrassic.main": "Terrassic",
        "entity.terrassic.spear": "Lanza",
        "message.terrassic.sit": "%s está descansando",
        "message.terrassic.follow": "%s te está siguiendo",
        "message.terrassic.tamed": "¡Has domesticado a %s (%s)!",
        "message.terrassic.perch": "%s se posó en tu hombro (agáchate para soltarlo)",
        "message.terrassic.perch_warn": "%s chilla: ¡algo te persigue!",
        "message.terrassic.perch_fish": "%s se zambulló y te trajo un pez",
        "message.terrassic.cargo_chest": "%s ahora lleva carga: agáchate y úsalo con la mano vacía para abrir el baúl",
        "message.terrassic.cargo_chest_ride": "%s ahora lleva carga: agacharse + usar sin silla, o la tecla del inventario montado",
        "message.terrassic.cargo_off": "%s soltó el baúl de carga",
        "sex.terrassic.male": "macho",
        "sex.terrassic.female": "hembra",
    },
}

# Minecraft treats every Spanish locale as its own language and falls back to English when one is missing,
# so the es_es file is copied to the other Spanish variants.
SPANISH_VARIANTS = ("es_ar", "es_cl", "es_ec", "es_mx", "es_uy", "es_ve")


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def egg_model(sid, stage, large):
    tex = f"terrassic:block/{sid}_egg_{stage}"
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
    lang = {code: dict(entries) for code, entries in LANG_EXTRA.items()}
    # sound subtitles (tools/soundgen/recipes.py)
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "soundgen"))
    from recipes import SUBTITLES, sound_id
    for (vset, ev), (pt, en, es) in SUBTITLES.items():
        key = f"subtitles.terrassic.{sound_id(vset, ev)}"
        lang["pt_br"][key], lang["en_us"][key], lang["es_es"][key] = pt, en, es
    for sid, (en, pt, es, large) in SPECIES.items():
        lang["en_us"][f"entity.terrassic.{sid}"] = en
        lang["pt_br"][f"entity.terrassic.{sid}"] = pt
        lang["es_es"][f"entity.terrassic.{sid}"] = es
        lang["en_us"][f"item.terrassic.{sid}_spawn_egg"] = f"{en} Spawn Egg"
        lang["pt_br"][f"item.terrassic.{sid}_spawn_egg"] = f"Ovo Gerador de {pt}"
        lang["es_es"][f"item.terrassic.{sid}_spawn_egg"] = f"Huevo Generador de {es}"
        # unique spawn egg sprite (layer0 only; tint colours are white)
        write(f"{A}/models/item/{sid}_spawn_egg.json", {"parent": "item/generated", "textures": {"layer0": f"terrassic:item/{sid}_spawn_egg"}})
        # hide of the species (item terrassic:<sid>_hide; sprite from tools/spritegen/sprites.py, drawn from the model palette)
        lang["en_us"][f"item.terrassic.{sid}_hide"] = f"{en} Hide"
        lang["pt_br"][f"item.terrassic.{sid}_hide"] = f"Couro de {pt}"
        lang["es_es"][f"item.terrassic.{sid}_hide"] = f"Cuero de {es}"
        write(f"{A}/models/item/{sid}_hide.json", {"parent": "item/generated", "textures": {"layer0": f"terrassic:item/{sid}_hide"}})
        if large is None:
            continue
        lang["en_us"][f"block.terrassic.{sid}_egg"] = f"{en} Egg"
        lang["pt_br"][f"block.terrassic.{sid}_egg"] = f"Ovo de {pt}"
        lang["es_es"][f"block.terrassic.{sid}_egg"] = f"Huevo de {es}"
        # egg block: 3 hatch stages
        for st in range(3):
            write(f"{A}/models/block/{sid}_egg_{st}.json", egg_model(sid, st, large))
        write(f"{A}/blockstates/{sid}_egg.json", {"variants": {f"hatch={st}": {"model": f"terrassic:block/{sid}_egg_{st}"} for st in range(3)}})
        write(f"{A}/models/item/{sid}_egg.json", {"parent": f"terrassic:block/{sid}_egg_0"})
        write(f"{D}/loot_tables/blocks/{sid}_egg.json", {"type": "minecraft:block", "pools": [{
            "rolls": 1, "entries": [{"type": "minecraft:item", "name": f"terrassic:{sid}_egg"}],
            "conditions": [{"condition": "minecraft:block_state_property", "block": f"terrassic:{sid}_egg",
                            "properties": {"hatch": "0"}}, {"condition": "minecraft:survives_explosion"}]}]})
    for iid, (en, pt, es, parent) in ITEMS.items():
        lang["en_us"][f"item.terrassic.{iid}"] = en
        lang["pt_br"][f"item.terrassic.{iid}"] = pt
        lang["es_es"][f"item.terrassic.{iid}"] = es
        write(f"{A}/models/item/{iid}.json", {"parent": parent, "textures": {"layer0": f"terrassic:item/{iid}"}})
    import gen_blocks  # primitive building blocks: their JSON + lang entries
    gen_blocks.main()
    import gen_science  # fossils, field tools, research table, advancements, story and Field Guide texts
    gen_science.main()
    for code in lang:
        lang[code].update(gen_blocks.LANG[code])
        lang[code].update(gen_science.LANG[code])
    missing = set(lang["en_us"]) ^ set(lang["pt_br"]) | set(lang["en_us"]) ^ set(lang["es_es"])
    if missing:
        raise SystemExit(f"lang keys missing in some language: {sorted(missing)}")
    lang.update({code: lang["es_es"] for code in SPANISH_VARIANTS})
    for code, data in lang.items():
        write(f"{A}/lang/{code}.json", dict(sorted(data.items())))

    # ------------------------------------------------------------- recipes
    def shaped(name, pattern, key, result, count=1):
        write(f"{D}/recipes/{name}.json", {"type": "minecraft:crafting_shaped", "category": "equipment", "pattern": pattern,
                                         "key": {k: {"item": v} for k, v in key.items()},
                                         "result": {"item": result, "count": count}})
    shaped("flint_knife", ["F", "S"], {"F": "minecraft:flint", "S": "minecraft:stick"}, "terrassic:flint_knife")
    shaped("flint_hatchet", ["FF", "FS", " S"], {"F": "minecraft:flint", "S": "minecraft:stick"}, "terrassic:flint_hatchet")
    shaped("bone_club", [" X", "B "], {"X": "minecraft:bone_block", "B": "minecraft:bone"}, "terrassic:bone_club")
    shaped("flint_spear", ["  F", " T ", "S  "], {"F": "minecraft:flint", "T": "minecraft:string", "S": "minecraft:stick"}, "terrassic:flint_spear")
    shaped("horn_spear", ["  H", " T ", "S  "], {"H": "terrassic:triceratops_horn", "T": "minecraft:string", "S": "minecraft:stick"}, "terrassic:horn_spear")
    shaped("rex_tooth_dagger", ["T", "L"], {"T": "terrassic:rex_tooth", "L": "minecraft:leather"}, "terrassic:rex_tooth_dagger")
    shaped("tail_club", [" C", "S "], {"C": "terrassic:ankylosaurus_club", "S": "minecraft:stick"}, "terrassic:tail_club")

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
        "tyrannosaurus": [item("minecraft:beef", 4, 8, True), item("minecraft:bone", 2, 5), item("terrassic:rex_tooth", 1, 2, chance=0.6)],
        "spinosaurus": [item("minecraft:beef", 3, 7, True), item("minecraft:bone", 2, 4), item("minecraft:cod", 1, 3, True)],
        "dilophosaurus": [item("minecraft:mutton", 1, 3, True), item("minecraft:bone", 1, 2)],
        "velociraptor": [item("minecraft:chicken", 1, 2, True), item("minecraft:feather", 1, 3)],
        "compsognathus": [item("minecraft:chicken", 0, 1, True), item("minecraft:feather", 0, 2)],
        "triceratops": [item("minecraft:beef", 3, 6, True), item("minecraft:leather", 2, 4), item("terrassic:triceratops_horn", 1, 2, chance=0.5)],
        "stegosaurus": [item("minecraft:beef", 2, 5, True), item("minecraft:leather", 1, 3)],
        "ankylosaurus": [item("minecraft:beef", 2, 5, True), item("minecraft:leather", 2, 4), item("terrassic:ankylosaurus_club", 1, 1, chance=0.4)],
        "euoplocephalus": [item("minecraft:beef", 2, 4, True), item("minecraft:leather", 2, 4), item("terrassic:ankylosaurus_club", 1, 1, chance=0.25)],
        "therizinosaurus": [item("minecraft:beef", 3, 6, True), item("minecraft:feather", 3, 6), item("minecraft:bone", 2, 4)],
        "deinocheirus": [item("minecraft:beef", 3, 6, True), item("minecraft:feather", 2, 4), item("minecraft:bone", 2, 4)],
        "brachiosaurus": [item("minecraft:beef", 8, 14, True), item("minecraft:leather", 4, 8), item("minecraft:bone", 4, 8)],
        "alamosaurus": [item("minecraft:beef", 10, 16, True), item("minecraft:leather", 5, 9), item("minecraft:bone", 5, 9)],
        "saltasaurus": [item("minecraft:beef", 5, 9, True), item("minecraft:leather", 3, 6), item("minecraft:bone", 3, 6)],
        "argentinosaurus": [item("minecraft:beef", 12, 20, True), item("minecraft:leather", 6, 10), item("minecraft:bone", 6, 12)],
        "opisthocoelicaudia": [item("minecraft:beef", 5, 9, True), item("minecraft:leather", 3, 6), item("minecraft:bone", 3, 6)],
        "dreadnoughtus": [item("minecraft:beef", 9, 15, True), item("minecraft:leather", 5, 8), item("minecraft:bone", 5, 9)],
        "parasaurolophus": [item("minecraft:beef", 2, 5, True), item("minecraft:leather", 1, 3)],
        "pachycephalosaurus": [item("minecraft:mutton", 1, 3, True), item("minecraft:bone", 1, 2)],
        "thescelosaurus": [item("minecraft:mutton", 1, 3, True), item("minecraft:leather", 0, 2)],
        "gallimimus": [item("minecraft:chicken", 1, 3, True), item("minecraft:feather", 2, 4)],
        "struthiomimus": [item("minecraft:chicken", 1, 2, True), item("minecraft:feather", 2, 5)],
        "maiasaura": [item("minecraft:beef", 2, 5, True), item("minecraft:leather", 1, 3)],
        "pteranodon": [item("minecraft:chicken", 1, 2, True), item("minecraft:leather", 0, 2), item("minecraft:cod", 0, 2, True)],
        "quetzalcoatlus": [item("minecraft:chicken", 3, 6, True), item("minecraft:leather", 2, 5), item("minecraft:bone", 3, 6)],
        "hatzegopteryx": [item("minecraft:chicken", 3, 6, True), item("minecraft:leather", 3, 6), item("minecraft:bone", 3, 6)],
        "ichthyornis": [item("minecraft:feather", 1, 2), item("minecraft:cod", 0, 1, True)],
        "mosasaurus": [item("minecraft:cod", 4, 8, True), item("minecraft:leather", 3, 6), item("minecraft:bone", 3, 6),
                       item("terrassic:mosasaurus_tooth", 1, 3, chance=0.6)],
        "tylosaurus": [item("minecraft:cod", 3, 7, True), item("minecraft:leather", 3, 5), item("minecraft:bone", 3, 6)],
        "elasmosaurus": [item("minecraft:cod", 2, 5, True), item("minecraft:leather", 2, 4), item("minecraft:bone", 3, 6)],
        "xiphactinus": [item("minecraft:cod", 3, 6, True), item("minecraft:bone", 2, 5)],
        "archelon": [item("minecraft:scute", 1, 3), item("minecraft:bone", 2, 5), item("minecraft:cod", 1, 2, True)],
        "hesperornis": [item("minecraft:feather", 1, 3), item("minecraft:cod", 0, 1, True), item("minecraft:bone", 1, 2)],
        "deinosuchus": [item("minecraft:cod", 2, 5, True), item("minecraft:leather", 3, 6), item("minecraft:bone", 3, 6)],
        "baurusuchus": [item("minecraft:leather", 1, 3), item("minecraft:bone", 2, 4)],
        "edmontosaurus": [item("minecraft:beef", 3, 6, True), item("minecraft:leather", 2, 4), item("minecraft:bone", 2, 4)],
        "corythosaurus": [item("minecraft:beef", 2, 5, True), item("minecraft:leather", 1, 3), item("minecraft:bone", 2, 4)],
        "styracosaurus": [item("minecraft:beef", 2, 5, True), item("minecraft:leather", 2, 4), item("minecraft:bone", 2, 4)],
        "pachyrhinosaurus": [item("minecraft:beef", 3, 6, True), item("minecraft:leather", 2, 5), item("minecraft:bone", 2, 4)],
        "protoceratops": [item("minecraft:mutton", 1, 2, True), item("minecraft:leather", 0, 1), item("minecraft:bone", 0, 2)],
    }
    for sid, pools in loot.items():
        # every species drops its own hide (last pool, so the pools above stay as they are)
        write(f"{D}/loot_tables/entities/{sid}.json", {"type": "minecraft:entity", "pools": pools + [item(f"terrassic:{sid}_hide", 1, 3)]})
    missing = [sid for sid in SPECIES if sid not in loot]
    assert not missing, f"species without loot table: {missing}"
    print("resources written")


if __name__ == "__main__":
    main()
