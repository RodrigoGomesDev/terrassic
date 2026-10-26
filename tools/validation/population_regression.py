"""Real regional sky-population regression: old birds outside 80 blocks, two players and camera turns."""
import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

from local_server import ROOT, LocalServer
from load_profile import freeze_sources
from minecraft_client import LocalClient


def require(value, message):
    if not value:
        raise AssertionError(message)


def count(server):
    cursor = len(server.lines)
    server.command("execute store result score flyers eco_count if entity @e[type=#terrassic_test:flyers]")
    server.command("scoreboard players get flyers eco_count")
    pattern = re.compile(r"flyers has (\d+) \[eco_count\]")
    server.wait(lambda: any(pattern.search(s) for s in server.lines[cursor:]), 15)
    return int(next(pattern.search(s).group(1) for s in server.lines[cursor:] if pattern.search(s)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loader", choices=["fabric", "forge"], required=True)
    parser.add_argument("--eula-file", type=Path, required=True)
    args = parser.parse_args()
    flat = {"layers": [{"block": "minecraft:bedrock", "height": 1}, {"block": "minecraft:dirt", "height": 2},
                       {"block": "minecraft:grass_block", "height": 1}], "biome": "minecraft:beach"}
    server = LocalServer(args.loader, args.eula_file, report="population-regression", properties={
        "allow-flight": "true", "view-distance": 8, "simulation-distance": 8,
        "generator-settings": json.dumps(flat)})
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    _, temporary = freeze_sources(server, revision)
    sources = {}
    for relative in ["common/src/main/java/com/terrassic/world/EcoSpawner.java",
                     "common/src/main/java/com/terrassic/world/SpawnBudget.java",
                     "common/src/main/java/com/terrassic/entity/PredatorDinosaur.java",
                     "common/src/main/java/com/terrassic/entity/ai/FollowOwnerPathGoal.java",
                     "common/src/main/java/com/terrassic/entity/FlyingDinosaur.java"]:
        data = (ROOT / relative).read_bytes()
        (server.source_root / relative).write_bytes(data)
        sources[relative] = hashlib.sha256(data).hexdigest()
    config = server.directory / "config"
    config.mkdir()
    (config / "terrassic-world.json").write_text(json.dumps({"rift_storms": False, "rules": {
        "spawn_density": 1, "land_spawns": 0, "sea_spawns": 0, "flyer_spawns": 1}}))
    pack = server.directory / "world/datapacks/sky-regression"
    tag = pack / "data/terrassic_test/tags/entity_types"
    tag.mkdir(parents=True)
    (pack / "pack.mcmeta").write_text(json.dumps({"pack": {"pack_format": 15, "description": "Disposable sky regression"}}))
    species = ["pteranodon", "quetzalcoatlus", "hatzegopteryx", "ichthyornis", "vegavis"]
    (tag / "flyers.json").write_text(json.dumps({"values": ["terrassic:" + s for s in species]}))
    clients = []
    result = {"loader": args.loader, "sources": sources, "existing": [], "replenishment": [], "passed": False}
    print(f"Reports and disposable world: {server.directory}", flush=True)
    try:
        server.start("population", timeout=600)
        for i in range(2):
            client = LocalClient(server.port, f"TerraEco{i}", args.loader)
            clients.append(client)
            client.wait_for(lambda c: c.knowledge is not None, timeout=60)
            server.command(f"gamemode creative TerraEco{i}")
            server.command(f"tp TerraEco{i} {i * 6} -60 0")
        server.command("gamerule doDaylightCycle false")
        server.command("time set day")
        server.command("scoreboard objectives add eco_count dummy")
        server.command("forceload add 144 -16 176 16")
        for i in range(6):
            # Pin only the fixtures: old persistent birds must count even above/beyond the old 80-block box.
            x, y = (40 + i * 6, 40) if i < 3 else (155 + (i - 3) * 6, -30)
            server.command(f'summon terrassic:pteranodon {x} {y} 0 {{Tags:["eco_fixture"],'
                           f'CustomName:\'"Existing{i}"\',NoAI:1b,NoGravity:1b,Age:0}}')
        server.command("gamerule doMobSpawning true")
        for step in range(23):
            server.command(f"tp TerraEco0 0 -60 0 {step * 45 % 360} 0")
            amount = count(server)
            result["existing"].append(amount)
            require(amount == 6, f"existing regional birds were ignored or removed: {amount}")
            time.sleep(2)
        print(f"PASS {args.loader}: six existing birds outside the old census prevented all replenishment", flush=True)
        server.command("kill @e[tag=eco_fixture]")
        time.sleep(2)
        for step in range(23):
            server.command(f"tp TerraEco0 0 -60 0 {step * 45 % 360} 0")
            amount = count(server)
            result["replenishment"].append(amount)
            require(amount <= 4, f"two nearby players exceeded shared regional target: {amount}")
            time.sleep(2)
        require(max(result["replenishment"]) > 0, "test passed only because no flyers could spawn")
        result["passed"] = True
        print(f"PASS {args.loader}: camera turns and two nearby players kept new sky population <=4", flush=True)
    finally:
        for client in clients:
            client.close()
        try:
            server.stop()
        finally:
            temporary.cleanup()
            (server.directory / "results.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
