"""1.7 spawn density (player feedback, point 4: "at least three times rarer than normal animals, carnivores rarer
still"), measured on a real dedicated server in a normal Minecraft world with a real protocol client: the player is
taken to several places far apart, the world spawns around them for a while, and the wild land animals within 128
blocks are counted with `/terrassic fauna` (dinosaurs against Minecraft's own), plus the carnivores among the dinos.

    python3 -B tools/validation/density_regression.py --loader fabric --eula-file /caminho/eula.txt

The world is disposable (build/density-regression); no player world is touched. The default rules apply
(dino_share 0.25: one dino for three Minecraft animals; predator_spawns 0.4).
"""
import argparse
import ast
import json
import re
import subprocess
import sys
import time
from pathlib import Path

from knockout_regression import Checks
from check_project import assignment
from load_profile import freeze_sources
from local_server import ROOT, LocalServer
from minecraft_client import LocalClient

sys.path.insert(0, str(ROOT / "tools" / "javagen"))
import gen_species  # noqa: E402

PLAYER = "TerraDensity"
# The biomes measured (temperate and warm ones, where dinosaurs and Minecraft's animals live together; a snowy region
# has neither), each found with /locate from a different corner of the map, and how long the world fills each one.
BIOMES = [("plains", 0, 0), ("forest", 3000, 0), ("savanna", 0, 3000), ("jungle", -3000, 0), ("swamp", 0, -3000),
          ("taiga", 3000, 3000), ("flower_forest", -3000, -3000), ("sparse_jungle", 3000, -3000)]
SETTLE = 120


def hunters():
    """The carnivores as DinosaurEntity#isHunter decides: carnivore or piscivore diet and 4+ attack damage."""
    species = {s["id"]: s for s in gen_species.SPECIES}
    return sorted(k for k, v in gen_species.GUIDE.items() if v["diet"] in ("carnivore", "piscivore") and k in species
                  and species[k]["attrs"].get("ATTACK_DAMAGE", 0) >= 4)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loader", choices=["fabric", "forge"], required=True)
    parser.add_argument("--eula-file", type=Path, required=True)
    parser.add_argument("--startup-timeout", type=int, default=900)
    args = parser.parse_args()
    server = LocalServer(args.loader, args.eula_file, report="density-regression",
                         properties={"level-type": "minecraft:normal", "generator-settings": "{}",
                                     "generate-structures": "true", "level-seed": "terrassic-density",
                                     "view-distance": 8, "simulation-distance": 8, "allow-flight": "true"})
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    _, temporary = freeze_sources(server, revision)
    pack = server.directory / "world/datapacks/terrassic_density"
    tag = pack / "data/terrassic_test/tags/entity_types/hunters.json"
    tag.parent.mkdir(parents=True)
    tag.write_text(json.dumps({"values": [f"terrassic:{name}" for name in hunters()]}))
    table = ast.literal_eval(assignment(server.source_root / "tools/javagen/gen_resources.py", "SPECIES"))
    (pack / "data/terrassic_test/tags/entity_types/dinosaurs.json").write_text(
        json.dumps({"values": [f"terrassic:{name}" for name in sorted(table)]}))
    (pack / "pack.mcmeta").write_text(json.dumps({"pack": {"pack_format": 15, "description": "Terrassic density fixtures"}}))
    checks = Checks(server)
    client = None
    rows = []
    print(f"Reports and disposable world: {server.directory}", flush=True)
    try:
        server.start("density", timeout=args.startup_timeout)
        client = LocalClient(server.port, PLAYER, server.loader)
        client.wait_for(lambda c: c.knowledge is not None)
        for command in (f"op {PLAYER}", f"gamemode creative {PLAYER}", "gamerule doDaylightCycle false", "time set noon",
                        "scoreboard objectives add dens dummy"):
            server.command(command)
        checks.barrier()
        for biome_id, ox, oz in BIOMES:
            cursor = len(server.lines)
            server.command(f"execute positioned {ox} 100 {oz} run locate biome minecraft:{biome_id}")
            checks.barrier()
            found = re.search(r"is at \[(-?\d+), [~\-0-9]+, (-?\d+)\]", " ".join(server.lines[cursor:]))
            if not found:
                print(f"INFO {server.loader}: no {biome_id} found", flush=True)
                continue
            x, z = int(found.group(1)), int(found.group(2))
            # on the ground, in creative: a spectator does not count for the natural spawns
            server.command(f"execute in minecraft:overworld run tp {PLAYER} {x} 200 {z}")
            checks.barrier()
            time.sleep(3)
            server.command(f"spreadplayers {x} {z} 0 1 false {PLAYER}")
            checks.barrier()
            time.sleep(SETTLE)
            cursor = len(server.lines)
            server.command(f"execute as {PLAYER} at @s run terrassic fauna")
            server.command(f"execute as {PLAYER} at @s store result score all dens if entity @e[type=!player,distance=..128]")
            server.command(f"execute as {PLAYER} at @s store result score hunters dens if entity "
                           f"@e[type=#terrassic_test:hunters,distance=..128]")
            server.command("scoreboard players get hunters dens")
            server.command("scoreboard players get all dens")
            checks.barrier()
            # /terrassic fauna answers the player; the server log carries the same lines
            said = " ".join(server.lines[cursor:])
            m = re.search(r"terra (\d+) dinos / (\d+) vanilla; mar (\d+) dinos / (\d+) vanilla", said)
            biome = re.search(r"bioma ([a-z_:]+)", said)
            h = re.search(r"hunters has (\d+)", " ".join(server.lines[cursor:]))
            row = {"spot": [x, z], "biome": biome.group(1) if biome else "?",
                   "dinos": int(m.group(1)) if m else None, "vanilla": int(m.group(2)) if m else None,
                   "sea_dinos": int(m.group(3)) if m else None, "sea_vanilla": int(m.group(4)) if m else None,
                   "hunters": int(h.group(1)) if h else None,
                   "entities": int(a.group(1)) if (a := re.search(r"all has (\d+)", said)) else None}
            rows.append(row)
            print(f"INFO {server.loader}: {row}", flush=True)
        dinos = sum(r["dinos"] or 0 for r in rows)
        vanilla = sum(r["vanilla"] or 0 for r in rows)
        hunting = sum(r["hunters"] or 0 for r in rows)
        sea = sum(r["sea_dinos"] or 0 for r in rows)
        ratio = vanilla / dinos if dinos else float("inf")
        print(f"INFO {server.loader}: land {dinos} dinos / {vanilla} Minecraft animals (1 dino for {ratio:.1f}); "
              f"carnivores {hunting} (land and sea, {sea} sea dinos)", flush=True)
        checks.results.append({"name": "every spot measured", "passed": all(r["dinos"] is not None for r in rows)})
        checks.results.append({"name": "at least three Minecraft animals per dino on land", "passed": dinos > 0 and ratio >= 3.0,
                               "detail": f"{dinos} / {vanilla}"})
        checks.results.append({"name": "carnivores rarer than the other dinos", "passed": hunting < dinos - hunting + sea,
                               "detail": f"{hunting} of {dinos + sea}"})
        for r in checks.results:
            print(f"{'PASS' if r['passed'] else 'FAIL'} {server.loader}: {r['name']} {r.get('detail', '')}", flush=True)
    finally:
        if client is not None:
            client.close()
        try:
            server.stop()
        finally:
            temporary.cleanup()
            (server.directory / "results.json").write_text(json.dumps({"source_commit": revision, "loader": args.loader,
                                                                        "rows": rows, "checks": checks.results}, indent=2))
    failed = [r["name"] for r in checks.results if not r["passed"]]
    if failed:
        raise AssertionError(f"{len(failed)} density checks failed: {failed}; see {server.directory}")
    print(f"PASS: {args.loader} spawn density ({len(rows)} spots)", flush=True)


if __name__ == "__main__":
    main()
