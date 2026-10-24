"""Generates the resources of the scientist mechanics (docs/HISTORIA.md, sections 4 to 9): fossils, field tools,
Fossil Rock and Research Table (models, blockstates, loot, recipes, worldgen), the advancement tree of conquistas.py
and every story / Field Guide text from lore.py.  Also writes research/Lore.java (Katarina's page list).

Lang entries are exported in LANG and merged by gen_resources.py.  Item and block ids must match ModItems / ModBlocks."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import conquistas  # noqa: E402
import lore  # noqa: E402
from gen_resources import A, D, ROOT, write  # noqa: E402
from gen_species import GUIDE as GUIDE_DATA, SPECIES as SPECIES_TABLE  # noqa: E402

NS = "terrassic"
CODES = ("pt_br", "en_us", "es_es")
LORE_JAVA = os.path.join(ROOT, "common", "src", "main", "java", "com", "terrassic", "research", "Lore.java")

# id: (en, pt, es, model parent)
ITEMS = {
    "field_notebook": ("Field Notebook", "Caderno de Campo", "Cuaderno de Campo", "item/generated"),
    "loose_page": ("Loose Page", "Página Solta", "Página Suelta", "item/generated"),
    "hair_brush": ("Hair Brush", "Pincel de Pelo", "Pincel de Pelo", "item/handheld"),
    "flint_chisel": ("Flint Chisel", "Cinzel de Sílex", "Cincel de Sílex", "item/handheld"),
    "amber_lens": ("Amber Lens", "Lente de Âmbar", "Lente de Ámbar", "item/generated"),
    "clay_jar": ("Clay Jar", "Frasco de Argila", "Frasco de Arcilla", "item/generated"),
    "resin_jar": ("Jar of Resin", "Frasco com Resina", "Frasco con Resina", "item/generated"),
    "blood_sample": ("Blood Sample", "Amostra de Sangue", "Muestra de Sangre", "item/generated"),
    "raw_amber": ("Raw Amber", "Âmbar Bruto", "Ámbar en Bruto", "item/generated"),
    "sketching_charcoal": ("Sketching Charcoal", "Carvão de Esboço", "Carbón de Boceto", "item/handheld"),
    "sketch": ("Blank Sketch", "Esboço em Branco", "Boceto en Blanco", "item/generated"),
}
BLOCKS = {
    "fossil_rock": ("Fossil Rock", "Rocha Fossilífera", "Roca Fosilífera"),
    "research_table": ("Research Table", "Mesa de Pesquisa", "Mesa de Investigación"),
}
LANG = {c: {} for c in CODES}


def tr(key, values):
    """values = (pt, en, es)"""
    for code, text in zip(CODES, values):
        LANG[code][key] = text


def day(n, code):
    s = f"{n:,}"
    return s if code == "en_us" else s.replace(",", ".")


def species_names():
    import gen_resources
    return {sid: (pt, en, es) for sid, (en, pt, es, _large) in gen_resources.SPECIES.items()}


def gen_lang():
    for iid, (en, pt, es, _parent) in ITEMS.items():
        tr(f"item.{NS}.{iid}", (pt, en, es))
    for bid, (en, pt, es) in BLOCKS.items():
        tr(f"block.{NS}.{bid}", (pt, en, es))
    for sid, (pt, en, es) in species_names().items():
        tr(f"item.{NS}.{sid}_fossil", (f"Fóssil de {pt}", f"{en} Fossil", f"Fósil de {es}"))
    for key, values in lore.UI.items():
        tr(key, values)
    for i, line in enumerate(lore.INTRO):
        tr(f"intro.{NS}.line.{i}", line)
    tr(f"intro.{NS}.era", lore.INTRO_ERA)
    for i, page in enumerate(lore.REPORT):
        tr(f"report.{NS}.{i}.title", page["title"])
        tr(f"report.{NS}.{i}.text", page["text"])
    for page in lore.PAGES:
        tr(f"page.{NS}.{page['id']}.title", tuple(t % day(page["day"], c) for t, c in zip(lore.PAGE_TITLE, CODES)))
        tr(f"page.{NS}.{page['id']}.text", page["text"])
    for sid in GUIDE_DATA:
        for field, values in lore.GUIDE[sid].items():
            tr(f"guide.{NS}.{sid}.{field}", values)
    for era, values in lore.ERAS.items():
        tr(f"era.{NS}.{era}", values)
    for diet, values in lore.DIETS.items():
        tr(f"diet.{NS}.{diet}", values)
    for oid, (name, hint) in lore.OBJECTIVES.items():
        tr(f"objective.{NS}.{oid}", name)
        tr(f"objective.{NS}.{oid}.hint", hint)
    for theme, values in lore.THEMES.items():
        tr(f"theme.{NS}.{theme}", values)
    for code, entries in conquistas.lang().items():
        LANG[code].update(entries)


def gen_models():
    for iid, (_en, _pt, _es, parent) in ITEMS.items():
        write(f"{A}/models/item/{iid}.json", {"parent": parent, "textures": {"layer0": f"{NS}:item/{iid}"}})
    for sid in GUIDE_DATA:
        write(f"{A}/models/item/{sid}_fossil.json", {"parent": "item/generated", "textures": {"layer0": f"{NS}:item/{sid}_fossil"}})
    # fossil rock: plain cube
    write(f"{A}/models/block/fossil_rock.json", {"parent": "minecraft:block/cube_all", "textures": {"all": f"{NS}:block/fossil_rock"}})
    write(f"{A}/blockstates/fossil_rock.json", {"variants": {"": {"model": f"{NS}:block/fossil_rock"}}})
    write(f"{A}/models/item/fossil_rock.json", {"parent": f"{NS}:block/fossil_rock"})
    # research table: stone top with leather and a bone on it, four stone legs
    tex = {"top": f"{NS}:block/research_table_top", "side": f"{NS}:block/research_table_side",
           "leg": f"{NS}:block/research_table_leg", "particle": f"{NS}:block/research_table_side"}

    def box(frm, to, top="#top", side="#side", bottom="#leg"):
        faces = {f: {"texture": side} for f in ("north", "south", "east", "west")}
        faces["up"] = {"texture": top}
        faces["down"] = {"texture": bottom}
        return {"from": frm, "to": to, "faces": faces}
    elements = [box([0, 12, 0], [16, 16, 16])]
    for x, z in ((1, 1), (12, 1), (1, 12), (12, 12)):
        elements.append(box([x, 0, z], [x + 3, 12, z + 3], "#leg", "#leg", "#leg"))
    write(f"{A}/models/block/research_table.json", {"parent": "minecraft:block/block", "textures": tex, "elements": elements})
    write(f"{A}/blockstates/research_table.json", {"variants": {
        f"facing={f}": ({"model": f"{NS}:block/research_table", "y": y} if y else {"model": f"{NS}:block/research_table"})
        for f, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270))}})
    write(f"{A}/models/item/research_table.json", {"parent": f"{NS}:block/research_table"})


def gen_data():
    def shaped(name, pattern, key, result, count=1):
        k = {}
        for c, v in key.items():
            if isinstance(v, list):
                k[c] = [{"tag": x[1:]} if x.startswith("#") else {"item": x} for x in v]
            else:
                k[c] = {"tag": v[1:]} if v.startswith("#") else {"item": v}
        write(f"{D}/recipes/{name}.json", {"type": "minecraft:crafting_shaped", "category": "equipment", "pattern": pattern,
                                         "key": k, "result": {"item": f"{NS}:{result}", "count": count}})

    def shapeless(name, items, result):
        write(f"{D}/recipes/{name}.json", {"type": "minecraft:crafting_shapeless", "category": "misc",
                                         "ingredients": [{"item": i} for i in items], "result": {"item": f"{NS}:{result}"}})
    shapeless("field_notebook", ["minecraft:leather", "minecraft:paper", "minecraft:string"], "field_notebook")
    shaped("amber_lens", [" A ", "BGB"], {"A": f"{NS}:raw_amber", "B": "minecraft:bone", "G": "minecraft:glass_pane"}, "amber_lens")
    shaped("clay_jar", ["B B", " B "], {"B": "minecraft:brick"}, "clay_jar")
    # the resin hardens into amber; the jar comes back (craft remainder)
    shapeless("raw_amber", [f"{NS}:resin_jar"], "raw_amber")
    shapeless("sketching_charcoal", ["minecraft:charcoal", "minecraft:string"], "sketching_charcoal")
    shaped("hair_brush", ["H", "S"], {"H": ["minecraft:rabbit_hide", "#minecraft:wool"], "S": "minecraft:stick"}, "hair_brush")
    shaped("flint_chisel", ["F", "T", "S"], {"F": "minecraft:flint", "T": "minecraft:string", "S": "minecraft:stick"}, "flint_chisel")
    shaped("research_table", ["LBL", "CCC", "C C"], {"L": "minecraft:leather", "B": "minecraft:bone", "C": "minecraft:cobblestone"},
           "research_table")

    # loot: the table drops itself; fossil rock gives itself with silk touch, otherwise cobblestone and maybe a bone
    write(f"{D}/loot_tables/blocks/research_table.json", {"type": "minecraft:block", "pools": [{
        "rolls": 1, "entries": [{"type": "minecraft:item", "name": f"{NS}:research_table"}],
        "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
    silk = {"condition": "minecraft:match_tool", "predicate": {"enchantments": [{"enchantment": "minecraft:silk_touch", "levels": {"min": 1}}]}}
    write(f"{D}/loot_tables/blocks/fossil_rock.json", {"type": "minecraft:block", "pools": [
        {"rolls": 1, "entries": [{"type": "minecraft:alternatives", "children": [
            {"type": "minecraft:item", "name": f"{NS}:fossil_rock", "conditions": [silk]},
            {"type": "minecraft:item", "name": "minecraft:cobblestone", "functions": [{"function": "minecraft:explosion_decay"}]}]}]},
        {"rolls": 1, "conditions": [{"condition": "minecraft:inverted", "term": silk}],
         "entries": [{"type": "minecraft:item", "name": "minecraft:bone", "functions": [
             {"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 0, "max": 1}}]}]}]})
    # both are mined with a pickaxe: merged into the tag file gen_blocks.py wrote (gen_resources runs it first)
    import json
    tag_path = os.path.join(os.path.dirname(D), "minecraft", "tags", "blocks", "mineable", "pickaxe.json")
    tag = {"replace": False, "values": []}
    if os.path.exists(tag_path):
        with open(tag_path, encoding="utf-8") as f:
            tag = json.load(f)
    for bid in BLOCKS:
        if f"{NS}:{bid}" not in tag["values"]:
            tag["values"].append(f"{NS}:{bid}")
    write(tag_path, tag)

    # worldgen: small veins in stone, from y 0 to 96, in every overworld biome (added by ModWorldgen)
    write(f"{D}/worldgen/configured_feature/fossil_rock.json", {"type": "minecraft:ore", "config": {
        "size": 6, "discard_chance_on_air_exposure": 0.0, "targets": [
            {"target": {"predicate_type": "minecraft:tag_match", "tag": "minecraft:stone_ore_replaceables"},
             "state": {"Name": f"{NS}:fossil_rock"}}]}})
    write(f"{D}/worldgen/placed_feature/fossil_rock.json", {"feature": f"{NS}:fossil_rock", "placement": [
        {"type": "minecraft:count", "count": 8}, {"type": "minecraft:in_square"},
        {"type": "minecraft:height_range", "height": {"type": "minecraft:uniform",
                                                      "min_inclusive": {"absolute": 0}, "max_inclusive": {"absolute": 96}}},
        {"type": "minecraft:biome"}]})



def gen_advancements():
    """The advancement tree of tools/javagen/conquistas.py (docs/CONQUISTAS.md). The folder is rewritten from
    scratch so nodes that left the table disappear. Checks that every icon exists and that every id the Java code
    awards is in the game."""
    import glob
    import re
    import shutil
    adv_root = f"{D}/advancements"
    shutil.rmtree(adv_root, ignore_errors=True)
    nodes = conquistas.emitted()
    for n in nodes:
        icon_ns, icon = n["icon"].split(":")
        if icon_ns == NS and not os.path.exists(f"{A}/models/item/{icon}.json"):
            raise SystemExit(f"advancement {n['id']}: icon {n['icon']} has no item model")
        write(f"{adv_root}/{n['id']}.json", conquistas.advancement(n))
    # fragments give one Loose Page: the page item turns into a page that player has not found yet
    write(f"{D}/loot_tables/rewards/katarina_page.json", {"type": "minecraft:advancement_reward", "pools": [{
        "rolls": 1, "entries": [{"type": "minecraft:item", "name": f"{NS}:loose_page"}]}]})

    # the diary objectives must match the Objective enum and lore.OBJECTIVES
    java_dir = os.path.join(ROOT, "common", "src", "main", "java", "com", "terrassic")
    with open(os.path.join(java_dir, "research", "Objective.java"), encoding="utf-8") as f:
        rows = re.findall(r"^\s{4}([A-Z_]+)\(Theme\.[A-Z]+, (true|false)\)", f.read(), re.M)
    enum = [name.lower() for name, _available in rows]
    if enum != conquistas.objective_ids() or list(lore.OBJECTIVES) != enum:
        raise SystemExit(f"Objective enum {enum}, conquistas {conquistas.objective_ids()} and lore.OBJECTIVES "
                         f"{list(lore.OBJECTIVES)} must list the same objectives in the same order")
    for name, available in rows:
        if (available == "true") != (f"chapter1/{name.lower()}" in {n["id"] for n in nodes}):
            raise SystemExit(f"Objective.{name}: 'available' in Java and 'ready' in conquistas.py disagree")
    # every literal id given to Research.award(...) must be written
    ready = {n["id"] for n in nodes}
    for path in glob.glob(os.path.join(java_dir, "**", "*.java"), recursive=True):
        with open(path, encoding="utf-8") as f:
            for nid in re.findall(r"award\([^;]*?\"([a-z0-9_]+/[a-z0-9_]+)\"\)", f.read()):
                if nid not in ready:
                    raise SystemExit(f"{os.path.relpath(path, ROOT)} awards {nid}, which is not a ready node of conquistas.py")


def gen_lore_java():
    rows = []
    for p in lore.PAGES:
        species = f'"{p["species"]}"' if p.get("species") else "null"
        rows.append(f'            new Page("{p["id"]}", {p["day"]}, {species})')
    src = f"""package com.terrassic.research;

import java.util.List;

/**
 * Story content that the code needs to know about: Katarina's pages (texts are translation keys
 * page.terrassic.&lt;id&gt;.title / .text), the number of intro lines (intro.terrassic.line.&lt;n&gt;) and of report pages
 * (report.terrassic.&lt;n&gt;.title / .text).
 *
 * Generated by tools/javagen/gen_science.py from tools/javagen/lore.py - edit the texts there.
 */
public final class Lore {{
    public static final int INTRO_LINES = {len(lore.INTRO)};
    public static final int REPORT_PAGES = {len(lore.REPORT)};

    /** A page of Katarina's notebook. species = the animal it talks about, or null for her diary. */
    public record Page(String id, int day, String species) {{
    }}

    public static final List<Page> ALL = List.of(
{(","+chr(10)).join(rows)});

    private Lore() {{
    }}

    public static Page byId(String id) {{
        for (Page p : ALL) {{
            if (p.id().equals(id)) {{
                return p;
            }}
        }}
        return null;
    }}
}}
"""
    with open(LORE_JAVA, "w") as f:
        f.write(src)


def main():
    missing = [sid for sid in GUIDE_DATA if sid not in lore.GUIDE]
    if missing:
        raise SystemExit(f"lore.GUIDE has no texts for {missing}")
    if [s["id"] for s in SPECIES_TABLE] != list(GUIDE_DATA):
        raise SystemExit("gen_species.GUIDE must list every species of SPECIES, in the same order")
    gen_lang()
    gen_models()
    gen_data()
    gen_advancements()
    gen_lore_java()
    print("science resources written")


if __name__ == "__main__":
    main()
