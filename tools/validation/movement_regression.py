"""Observe real mob AI in an isolated localhost server; never uses player worlds."""
import argparse
import hashlib
import json
import math
import re
import subprocess
import time
from pathlib import Path

from local_server import ROOT, LocalServer
from load_profile import freeze_sources
from minecraft_client import LocalClient


def field(server, tag, name):
    cursor = len(server.lines)
    server.command(f"data get entity @e[tag={tag},limit=1] {name}")
    missing = f"Found no elements matching {name}"
    server.wait(lambda: any("has the following entity data:" in s or missing in s
                            for s in server.lines[cursor:]), 15)
    if name == "NoGravity" and any(missing in s for s in server.lines[cursor:]):
        return [0]  # Vanilla omits the tag when gravity is enabled.
    line = next(s for s in server.lines[cursor:] if "has the following entity data:" in s)
    raw = line.split("entity data:", 1)[1].strip()
    return [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?", raw)]


def require(value, message):
    if not value:
        raise AssertionError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loader", choices=["fabric", "forge"], required=True)
    parser.add_argument("--eula-file", type=Path, required=True)
    args = parser.parse_args()
    server = LocalServer(args.loader, args.eula_file, report="movement-regression", properties={
        "allow-flight": "true", "view-distance": 6, "simulation-distance": 6})
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    _, temporary = freeze_sources(server, revision)
    # Freeze the pending production changes as well, without touching another session's build.
    relatives = ["common/build.gradle"] + [str(p.relative_to(ROOT)) for p in
                 (ROOT / "common/src/main/java/com/terrassic/entity").rglob("*.java")]
    sources = {}
    for relative in relatives:
        data = (ROOT / relative).read_bytes()
        destination = server.source_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        sources[relative] = hashlib.sha256(data).hexdigest()
    result = {"loader": args.loader, "base_revision": revision, "sources": sources, "samples": [], "passed": False}
    client = None
    print(f"Reports and disposable world: {server.directory}", flush=True)
    try:
        server.start("movement", timeout=600)
        client = LocalClient(server.port, "TerraMove", args.loader)
        client.wait_for(lambda c: c.knowledge is not None, timeout=60)
        server.command("gamemode creative TerraMove")
        server.command("tp TerraMove 0 -35 0")
        server.command("gamerule doDaylightCycle false")
        server.command("time set day")
        server.command("forceload add -96 -96 96 96")
        for i, x in enumerate((0, 1, 6, -6)):
            server.command(f'summon terrassic:pteranodon {x} -25 0 '
                           f'{{Tags:["move_{i}"],CustomName:\'"Flight{i}"\',Size:1f,BirthSize:1f,'
                           'Age:0,Invulnerable:1b,Rotation:[0f,0f],Motion:[0d,0d,0.35d]}')
        server.command('summon terrassic:triceratops 18 -60 0 {Tags:["herd_a"],CustomName:\'"HerdA"\',Size:1f}')
        server.command('summon terrassic:triceratops 19 -60 0 {Tags:["herd_b"],CustomName:\'"HerdB"\',Size:1f}')
        # Let the normal goals choose flight; the fixture does not replace or force the controller.
        deadline = time.monotonic() + 60
        while True:
            speeds = [math.hypot(*field(server, f"move_{i}", "Motion")[::2]) for i in range(4)]
            if min(speeds) > .25:
                break
            require(time.monotonic() < deadline, "not all four wild adults entered forward flight")
            time.sleep(.5)
        print(f"{args.loader}: four birds entered flight, measuring AI", flush=True)
        for _ in range(30):
            snapshot = []
            for i in range(4):
                snapshot.append({"position": field(server, f"move_{i}", "Pos"),
                                 "motion": field(server, f"move_{i}", "Motion"),
                                 "rotation": field(server, f"move_{i}", "Rotation")})
            result["samples"].append(snapshot)
            time.sleep(.15)
        horizontal = [math.hypot(b["motion"][0], b["motion"][2]) for s in result["samples"] for b in s]
        require(min(horizontal) > .15, f"bird stalled in air: minimum horizontal speed {min(horizontal)}")
        nearest = [min(math.dist(s[i]["position"], s[j]["position"]) for i in range(4) for j in range(i))
                   for s in result["samples"]]
        require(sum(d < 2 for d in nearest) <= 3, "flock remained piled up")
        distances = [sum(math.dist(a[i]["position"], b[i]["position"])
                         for a, b in zip(result["samples"], result["samples"][1:])) for i in range(4)]
        require(min(distances) > 20, "bird rotated in place instead of advancing")
        herd_gap = math.dist(field(server, "herd_a", "Pos"), field(server, "herd_b", "Pos"))
        require(herd_gap > 3, "ground herd remained overlapping")
        server.command("time set midnight")
        time.sleep(.5)
        landing = field(server, "move_1", "Motion")
        require(field(server, "move_1", "NoGravity")[0] == 0 and landing[1] < 0
                and math.hypot(landing[0], landing[2]) >= .19,
                "resting bird did not transition from cruising to forward descending glide")
        server.command('data merge entity @e[tag=move_0,limit=1] {KnockedOut:1b,Torpor:200f}')
        time.sleep(.5)
        gravity = field(server, "move_0", "NoGravity")[0]
        fall = field(server, "move_0", "Motion")[1]
        require(gravity == 0 and fall < 0, "torpor did not release cruising/gravity")
        result.update(passed=True, minimum_speed=min(horizontal), minimum_spacing=min(nearest),
                      distance_per_bird=distances, final_herd_spacing=herd_gap,
                      knockout_releases_gravity=True, resting_glide=True)
        print(f"PASS {args.loader}: minimum speed={min(horizontal):.3f}, minimum flock gap={min(nearest):.2f}, "
              f"ground herd gap={herd_gap:.2f}", flush=True)
    finally:
        if client:
            client.close()
        try:
            server.stop()
        finally:
            temporary.cleanup()
            (server.directory / "results.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
