"""Read-only integrity checks. Uses only Python's standard library; never imports generators.

Run from any directory: python3 -B tools/validation/check_project.py
This verifies committed inputs/assets, not their visual quality or gameplay behavior.
"""
import ast
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def assignment(path, name):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return node.value
    raise ValueError(f"{path}: missing table {name}")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def png_dimensions(path):
    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("invalid PNG header")
    return struct.unpack(">II", header[16:24])


def check(root):
    errors = []
    resources = root / "common/src/main/resources"
    assets = resources / "assets/terrassic"
    java = root / "common/src/main/java/com/terrassic/entity"
    generators = root / "tools/javagen"
    documents = {}

    def fail(path, message):
        errors.append(f"{path.relative_to(root)}: {message}")

    # Parse all source resource JSON, including embedded resource packs, without silently accepting duplicate keys.
    for path in sorted(resources.rglob("*.json")):
        try:
            documents[path] = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        except (ValueError, OSError) as exc:
            fail(path, str(exc))

    resource_table = ast.literal_eval(assignment(generators / "gen_resources.py", "SPECIES"))
    species_node = assignment(generators / "gen_species.py", "SPECIES")
    species = {}
    # Read only literal id/cls fields of dict(...) rows. Never execute generator code or its imports.
    if not isinstance(species_node, ast.List):
        raise ValueError("gen_species.SPECIES must be a list of dict(...) rows")
    for row in species_node.elts:
        if not isinstance(row, ast.Call) or not isinstance(row.func, ast.Name) or row.func.id != "dict":
            raise ValueError("unsupported species row; expected dict(...)")
        fields = {kw.arg: kw.value for kw in row.keywords}
        name = ast.literal_eval(fields["id"])
        if name in species:
            fail(generators / "gen_species.py", f"duplicate species: {name}")
        species[name] = ast.literal_eval(fields["cls"])

    expected = set(species)
    for filename, table in [("gen_resources.py", "SPECIES"), ("gen_species.py", "SIZES"),
                            ("gen_species.py", "GUIDE"), ("gen_species.py", "WORLD")]:
        node = assignment(generators / filename, table)
        if not isinstance(node, ast.Dict):
            raise ValueError(f"{filename}.{table} must be a literal dictionary")
        names = [ast.literal_eval(key) for key in node.keys]
        if len(names) != len(set(names)):
            fail(generators / filename, f"duplicate keys in {table}")
        missing, extra = expected - set(names), set(names) - expected
        if missing or extra:
            fail(generators / filename, f"{table}: missing={sorted(missing)}, extra={sorted(extra)}")

    for name, cls in sorted(species.items()):
        required = [java / f"{cls}.java", assets / f"geo/entity/{name}.geo.json",
                    assets / f"animations/entity/{name}.animation.json",
                    assets / f"textures/entity/{name}_male.png", assets / f"textures/entity/{name}_female.png",
                    assets / f"models/item/{name}_spawn_egg.json",
                    resources / f"data/terrassic/loot_tables/entities/{name}.json"]
        if name in resource_table and resource_table[name][3] is not None:
            required.append(assets / f"blockstates/{name}_egg.json")
        for path in required:
            if not path.is_file():
                fail(path, "required species file is missing")

        geo_path = assets / f"geo/entity/{name}.geo.json"
        geo = documents.get(geo_path)
        if geo is not None:
            try:
                geometry = geo["minecraft:geometry"][0]
                desc = geometry["description"]
                if desc["identifier"] != f"geometry.{name}":
                    fail(geo_path, f"unexpected identifier: {desc['identifier']}")
                bones = [bone["name"] for bone in geometry["bones"]]
                if len(bones) != len(set(bones)):
                    fail(geo_path, "duplicate bone names")
                for bone in geometry["bones"]:
                    if "parent" in bone and bone["parent"] not in bones:
                        fail(geo_path, f"unknown parent {bone['parent']} for {bone['name']}")
                for sex in ("male", "female"):
                    texture = assets / f"textures/entity/{name}_{sex}.png"
                    if texture.is_file() and png_dimensions(texture) != (desc["texture_width"], desc["texture_height"]):
                        fail(texture, "texture dimensions differ from geometry description")
            except (KeyError, IndexError, TypeError, ValueError, OSError) as exc:
                fail(geo_path, f"invalid geometry/texture: {exc}")

        anim_path = assets / f"animations/entity/{name}.animation.json"
        anim = documents.get(anim_path)
        if anim is not None:
            animations = anim.get("animations", {})
            if not animations:
                fail(anim_path, "no animations")
            for key in animations:
                if not key.startswith(f"animation.{name}."):
                    fail(anim_path, f"unexpected animation name: {key}")

    languages = {locale: documents.get(assets / f"lang/{locale}.json")
                 for locale in ("pt_br", "en_us", "es_es")}
    keys = set().union(*(set(value) for value in languages.values() if isinstance(value, dict)))
    for locale, values in languages.items():
        path = assets / f"lang/{locale}.json"
        if not isinstance(values, dict):
            fail(path, "missing or invalid language file")
            continue
        missing = keys - values.keys()
        if missing:
            fail(path, f"missing translations: {sorted(missing)}")

    return errors, len(species), len(documents), len(keys)


def main():
    try:
        errors, species, documents, keys = check(ROOT)
    except (ValueError, OSError, KeyError, TypeError, SyntaxError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    print(f"Checked {species} species, {documents} JSON documents, {keys} translation keys in 3 languages.")
    print(f"{'FAIL' if errors else 'PASS'}: {len(errors)} integrity errors. Visual/gameplay review remains separate.")
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
