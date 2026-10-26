"""Generate actual trees in a disposable server, then inspect saved block palettes for exposed cut trunk tips."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import time
import zlib

from local_server import ROOT, LocalServer
from load_profile import freeze_sources
from minecraft_client import read_nbt

TREES = ("araucaria", "ginkgo", "metasequoia", "taxodium", "tree_fern", "sabal", "magnolia", "podocarpus", "platanus")


def blocks(directory):
    found = {}
    for path in (directory / "world/region").glob("*.mca"):
        region = path.read_bytes()
        for slot in range(1024):
            location = int.from_bytes(region[slot * 4:slot * 4 + 4], "big")
            if not location:
                continue
            offset = (location >> 8) * 4096
            length = int.from_bytes(region[offset:offset + 4], "big")
            if region[offset + 4] != 2:
                raise ValueError("unsupported region compression")
            chunk = read_nbt(zlib.decompress(region[offset + 5:offset + 4 + length]))
            for section in chunk.get("sections", []):
                states = section.get("block_states", {})
                palette = states.get("palette", [])
                relevant = {i for i, s in enumerate(palette) if s["Name"].startswith("terrassic:")
                            and s["Name"].endswith(("_log", "_leaves"))}
                if not relevant:
                    continue
                bits = max(4, (len(palette) - 1).bit_length())
                per_word = 64 // bits
                packed = states.get("data", [])
                for index in range(4096):
                    value = 0 if len(palette) == 1 else (packed[index // per_word] >> ((index % per_word) * bits)) & ((1 << bits) - 1)
                    if value in relevant:
                        position = (chunk["xPos"] * 16 + (index & 15),
                                    section["Y"] * 16 + (index >> 8), chunk["zPos"] * 16 + ((index >> 4) & 15))
                        found[position] = palette[value]
    return found


def audit(world, plot):
    x, z = plot["x"], plot["z"]
    family = plot["tree"]
    logs = {p: s for p, s in world.items() if abs(p[0] - x) <= 11 and abs(p[2] - z) <= 11
            and s["Name"] == f"terrassic:{family}_log"}
    leaves = {p for p, s in world.items() if abs(p[0] - x) <= 11 and abs(p[2] - z) <= 11
              and s["Name"] == f"terrassic:{family}_leaves"}
    if not logs or not leaves:
        raise AssertionError(f"missing tree: {plot}")
    exposed = []
    for (bx, by, bz), state in logs.items():
        if state.get("Properties", {}).get("axis", "y") != "y" or (bx, by + 1, bz) in logs:
            continue
        if not any(lx == bx and lz == bz and ly > by for lx, ly, lz in leaves):
            exposed.append([bx, by, bz])
    return {**plot, "logs": len(logs), "leaves": len(leaves), "uncapped_vertical_tips": exposed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loader", choices=["fabric", "forge"], required=True)
    parser.add_argument("--eula-file", type=Path, required=True)
    parser.add_argument("--compare", action="store_true", help="Include magnolia foliage candidates alongside packaged trees")
    args = parser.parse_args()
    repeats = 5 if args.compare else 8
    server = LocalServer(args.loader, args.eula_file, report="tree-regression", properties={
        "level-seed": "terrassic-canopy-regression"})
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    _, temporary = freeze_sources(server, revision)
    assets = ROOT / "common/src/main/resources/data/terrassic/worldgen/configured_feature"
    for name in TREES:
        relative = f"common/src/main/resources/data/terrassic/worldgen/configured_feature/{name}.json"
        (server.source_root / relative).write_bytes((ROOT / relative).read_bytes())
    pack = server.directory / "world/datapacks/tree-regression"
    features = pack / "data/terrassic_test/worldgen/configured_feature"
    features.mkdir(parents=True)
    (pack / "pack.mcmeta").write_text(json.dumps({"pack": {"pack_format": 15, "description": "Disposable canopy regression"}}))
    variants = []
    if args.compare:
        for name, foliage in [("offset_1", {"type": "minecraft:blob_foliage_placer", "radius": 3, "offset": 1, "height": 3}),
                              ("offset_2", {"type": "minecraft:blob_foliage_placer", "radius": 3, "offset": 2, "height": 3}),
                              ("fancy", {"type": "minecraft:fancy_foliage_placer", "radius": 3, "offset": 4, "height": 4})]:
            feature = json.loads((assets / "magnolia.json").read_text())
            feature["config"]["foliage_placer"] = foliage
            (features / f"magnolia_{name}.json").write_text(json.dumps(feature))
            variants.append((f"terrassic_test:magnolia_{name}", "magnolia"))
    entries = [("terrassic:" + name, name) for name in TREES] + variants
    plots = []
    print(f"Reports and disposable world: {server.directory}", flush=True)
    try:
        server.start("trees", timeout=600)
        server.command("gamerule randomTickSpeed 0")
        server.command("forceload add -112 -112 112 112")
        time.sleep(3)
        for feature, tree in entries:
            for repeat in range(repeats):
                index = len(plots)
                x, z = -84 + (index % 8) * 24, -84 + (index // 8) * 24
                cursor = len(server.lines)
                server.command(f"place feature {feature} {x} -60 {z}")
                success = f'Placed "{feature}" at'
                server.wait(lambda: any(success in s or "Failed to place feature" in s
                                        or "not loaded" in s for s in server.lines[cursor:]), 20)
                if not any(success in s for s in server.lines[cursor:]):
                    raise AssertionError(f"feature placement failed: {feature} {x} {z}")
                plots.append({"feature": feature, "tree": tree, "repeat": repeat, "x": x, "z": z})
        server.stop()
        world = blocks(server.directory)
        results = [audit(world, plot) for plot in plots]
        summary = {}
        for result in results:
            row = summary.setdefault(result["feature"], {"trees": 0, "affected": 0, "exposed_tips": 0})
            row["trees"] += 1
            row["affected"] += bool(result["uncapped_vertical_tips"])
            row["exposed_tips"] += len(result["uncapped_vertical_tips"])
        sources = {str((assets / f"{name}.json").relative_to(ROOT)):
                   hashlib.sha256((assets / f"{name}.json").read_bytes()).hexdigest() for name in TREES}
        (server.directory / "results.json").write_text(json.dumps({"loader": args.loader, "sources": sources,
            "summary": summary, "trees": results}, indent=2) + "\n")
        print(json.dumps(summary, indent=2), flush=True)
        if not args.compare:
            assert all(row["exposed_tips"] == 0 for row in summary.values()), "tree has exposed cut trunk tips"
    finally:
        server.stop()
        temporary.cleanup()


if __name__ == "__main__":
    main()
