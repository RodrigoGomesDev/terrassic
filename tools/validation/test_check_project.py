"""Negative fixtures prove that the read-only checker detects broken deliveries.

Run: python3 -B -m unittest discover -s tools/validation -p 'test_*.py'
"""
import json
import tempfile
import unittest
from pathlib import Path

from check_project import check


class ProjectChecks(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.assets = Path("common/src/main/resources/assets/terrassic")
        self.write("tools/javagen/gen_species.py", "SPECIES = [dict(id='example', cls='Example')]\n"
                   "SIZES = {'example': dict(real=1)}\nGUIDE = {'example': 1}\nWORLD = {'example': 1}\n")
        self.write("tools/javagen/gen_resources.py", "SPECIES = {'example': ('Example', 'Exemplo', 'Ejemplo', None)}\n")
        self.write("common/src/main/java/com/terrassic/entity/Example.java", "class Example {}")
        self.write(self.assets / "geo/entity/example.geo.json", json.dumps({"minecraft:geometry": [{
            "description": {"identifier": "geometry.example", "texture_width": 1, "texture_height": 1},
            "bones": [{"name": "root"}]}]}))
        self.write(self.assets / "animations/entity/example.animation.json",
                   '{"animations": {"animation.example.idle": {}}}')
        # Only the PNG signature/IHDR/dimensions are consumed by the checker, not pixel data.
        for sex in ("male", "female"):
            path = self.root / self.assets / f"textures/entity/example_{sex}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR" + (1).to_bytes(4, "big") * 2)
        self.write(self.assets / "models/item/example_spawn_egg.json", '{}')
        self.write("common/src/main/resources/data/terrassic/loot_tables/entities/example.json", '{}')
        for locale in ("pt_br", "en_us", "es_es"):
            self.write(self.assets / f"lang/{locale}.json", '{"entity.terrassic.example": "Example"}')
        self.write(self.assets / "sounds.json", '{"example": {"sounds": ["terrassic:example"]}}')
        self.write(self.assets / "sounds/example.ogg", "OggSfixture")  # Header fixture, not a decodable audio file.

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def errors(self):
        return "\n".join(check(self.root)[0])

    def test_complete_fixture_and_no_writes(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(self.errors(), "")
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_missing_species_asset(self):
        (self.root / self.assets / "animations/entity/example.animation.json").unlink()
        self.assertIn("required species file is missing", self.errors())

    def test_duplicate_json_keys(self):
        self.write(self.assets / "models/item/example_spawn_egg.json", '{"parent":"a","parent":"b"}')
        self.assertIn("duplicate JSON key: parent", self.errors())

    def test_species_tables_disagree(self):
        self.write("tools/javagen/gen_resources.py", "SPECIES = {}\n")
        self.assertIn("SPECIES: missing=['example']", self.errors())

    def test_translation_missing(self):
        self.write(self.assets / "lang/es_es.json", '{}')
        self.assertIn("missing translations", self.errors())

    def test_animation_has_wrong_namespace(self):
        self.write(self.assets / "animations/entity/example.animation.json", '{"animations":{"animation.other.idle":{}}}')
        self.assertIn("unexpected animation name", self.errors())

    def test_texture_dimensions_disagree(self):
        path = self.root / self.assets / "textures/entity/example_female.png"
        path.write_bytes(path.read_bytes()[:16] + (2).to_bytes(4, "big") * 2)
        self.assertIn("texture dimensions differ", self.errors())

    def test_missing_sound_and_broken_container(self):
        audio = self.root / self.assets / "sounds/example.ogg"
        audio.unlink()
        self.assertIn("missing sound file terrassic:example.ogg", self.errors())
        audio.write_bytes(b"not Ogg")
        self.assertIn("invalid Ogg container header", self.errors())

    def test_subtitle_must_exist_in_each_language(self):
        self.write(self.assets / "sounds.json", json.dumps({"example": {
            "subtitle": "subtitles.terrassic.example", "sounds": []}}))
        self.assertIn("subtitle subtitles.terrassic.example missing in es_es", self.errors())

    def test_event_reference_and_cycle(self):
        self.write(self.assets / "sounds.json", json.dumps({
            "example": {"sounds": [{"name": "terrassic:unknown", "type": "event"}]}}))
        self.assertIn("unknown sound event", self.errors())
        self.write(self.assets / "sounds.json", json.dumps({
            "example": {"sounds": [{"name": "terrassic:other", "type": "event"}]},
            "other": {"sounds": [{"name": "terrassic:example", "type": "event"}]}}))
        self.assertIn("cyclic sound event reference", self.errors())

    def test_valid_forward_reference_and_vanilla_sound(self):
        self.write(self.assets / "sounds.json", json.dumps({
            "first": {"sounds": [{"name": "terrassic:example", "type": "event"}]},
            "example": {"subtitle": "subtitles.entity.pig.ambient",
                        "sounds": ["terrassic:example", "minecraft:entity.pig.ambient"]}}))
        self.assertEqual(self.errors(), "")

    def test_invalid_sound_resource_does_not_escape_source_tree(self):
        self.write(self.assets / "sounds.json", json.dumps({
            "example": {"sounds": ["terrassic:../../outside", None, {"name": "Invalid:UPPER"}]}}))
        self.assertIn("unsafe sound resource path", self.errors())
        self.assertIn("invalid sound resource name", self.errors())


if __name__ == "__main__":
    unittest.main()
