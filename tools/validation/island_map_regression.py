"""Survey, real transport and save/restart of the map in a disposable Terrassic continent."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from local_server import ROOT, LocalServer
from load_profile import freeze_sources
from minecraft_client import LocalClient


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def connect(server):
    client = LocalClient(server.port, "TerraMap", server.loader)
    try:
        client.wait_for(lambda c: c.knowledge is not None, timeout=60)
        server.command("gamemode creative TerraMap")
        client.wait_for(lambda c: c.island_map is not None, timeout=240)
        return client
    except BaseException:
        client.close()
        raise


def summary(data):
    return {**{k: data[k] for k in ("size", "extent", "sea_level")},
            "heights_sha256": hashlib.sha256(data["heights"]).hexdigest(),
            "kinds_sha256": hashlib.sha256(data["kinds"]).hexdigest(),
            "categories": sorted(set(data["kinds"]))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loader", choices=["fabric", "forge"], required=True)
    parser.add_argument("--eula-file", type=Path, required=True)
    parser.add_argument("--startup-timeout", type=int, default=600)
    args = parser.parse_args()
    server = LocalServer(args.loader, args.eula_file, report="island-map-regression", properties={
        "level-type": "terrassic:terrassic_small", "generator-settings": "{}", "allow-flight": "true",
        "level-seed": "terrassic-map-regression", "spawn-monsters": "false"})
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    _, temporary = freeze_sources(server, revision)
    preset = json.loads((server.source_root / "common/src/main/resources/data/terrassic/worldgen/world_preset/terrassic_small.json").read_text())
    radius = preset["dimensions"]["minecraft:overworld"]["generator"]["biome_source"]["raio"]
    config = server.directory / "config"
    config.mkdir()
    (config / "terrassic-world.json").write_text(json.dumps({"rift_storms": False}))
    result = {"source_commit": revision, "loader": args.loader, "preset": "terrassic:terrassic_small", "radius": radius}
    client = None
    print(f"Reports and disposable world: {server.directory}", flush=True)
    try:
        server.start("map-create", timeout=args.startup_timeout)
        client = connect(server)
        data = client.island_map
        require(data["size"] == 128 and data["extent"] == radius * 2, "map must describe the selected continent preset")
        categories = set(data["kinds"])
        require(categories <= set(range(9)), "map categories must be valid")
        require(bool(categories & {0, 1}) and bool(categories & {4, 5, 6, 7, 8}), "map must contain both sea and land")
        result["created"] = summary(data)
        print(f"{args.loader}: real continent surveyed and received: {result['created']}", flush=True)
        client.close()
        client = None
        server.stop()
        saved = server.directory / "world/data/terrassic_island_map.dat"
        require(saved.is_file(), "map must be saved with the world")
        before = saved.read_bytes()
        modified_before = saved.stat().st_mtime_ns
        result["saved_sha256"] = hashlib.sha256(before).hexdigest()

        server.start("map-reload", timeout=args.startup_timeout)
        client = connect(server)
        result["reloaded"] = summary(client.island_map)
        require(client.island_map == data, "map must round-trip identically through world save/restart and the real connection")
        client.close()
        client = None
        server.stop()
        require(saved.read_bytes() == before, "unchanged cached map must not be rewritten")
        require(saved.stat().st_mtime_ns == modified_before, "saved survey must be reused without rewriting the file")
        require(not any("Terrassic island map surveyed in" in line for line in server.lines), "reload must not finish a new survey")
        result["passed"] = True
        print(f"PASS: {args.loader} continent map transport, persistence and cached reuse", flush=True)
    finally:
        if client is not None:
            client.close()
        try:
            server.stop()
        finally:
            temporary.cleanup()
            (server.directory / "results.json").write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
