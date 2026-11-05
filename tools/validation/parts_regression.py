"""1.7 hit parts (docs/PLANO_PARTES.md) checked on a real dedicated server with a real protocol client: the same
weapon on the head, the body and the tail of a T. rex deals 125%, 100% and 75%; the attack packet names the part by its
id (owner id + 1..n), which the server must resolve (ServerLevel#getEntityOrPart); an arrow falling on the tail tip,
outside the collision box, hits the animal; a dart falling on the head doses it.

    python3 -B tools/validation/parts_regression.py --loader fabric --eula-file /caminho/eula.txt

Requires JDK 21, the Gradle dependencies in the cache and an accepted eula.txt supplied by the operator. The world is
disposable (build/parts-regression); no player world is touched.
"""
import argparse
import json
import re
import subprocess
import time
import uuid
from pathlib import Path

from knockout_regression import Checks, int_uuid, selector
from load_profile import freeze_sources
from local_server import LocalServer
from minecraft_client import LocalClient, varint

PLAYER = "TerraParts"
ROOT = Path(__file__).resolve().parents[2]


def rex_parts():
    """The Tyrannosaurus parts in the generated order (id = owner id + 1 + index): [(kind, forward, side)] standing."""
    text = (ROOT / "common/src/main/java/com/terrassic/entity/Tyrannosaurus.java").read_text()
    return [(kind, float(f), float(s)) for kind, f, s in
            re.findall(r"DinoPart\.Kind\.(\w+),\s*new float\[\]\{(-?[0-9.]+)F, (-?[0-9.]+)F", text)]


PARTS = rex_parts()
HEAD = max((i for i, p in enumerate(PARTS) if p[0] == "HEAD"), key=lambda i: PARTS[i][1])      # the snout piece
TAIL_TIP = min((i for i, p in enumerate(PARTS) if p[0] == "TAIL"), key=lambda i: PARTS[i][1])  # the tail tip
BODY = next(i for i, p in enumerate(PARTS) if p[0] == "BODY")
HEAD_FORWARD, TAIL_FORWARD, BODY_FORWARD = PARTS[HEAD][1], PARTS[TAIL_TIP][1], PARTS[BODY][1]
WEAPON_DAMAGE = 9.0   # stone axe, no armour on the target (Attributes below), no crit, full swing


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loader", choices=["fabric"], required=True)
    parser.add_argument("--eula-file", type=Path, required=True)
    parser.add_argument("--startup-timeout", type=int, default=600)
    args = parser.parse_args()
    server = LocalServer(args.loader, args.eula_file, report="parts-regression")
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    _, temporary = freeze_sources(server, revision)
    checks = Checks(server)
    client = None
    rex = uuid.UUID("17000000-0000-4000-8000-0000000000a1")
    tag = "parts_rex"
    print(f"Reports and disposable world: {server.directory}", flush=True)

    def value(key):
        """A float of the T. rex's NBT (0 when it is not saved)."""
        cursor = len(server.lines)
        server.command(f"data get entity {selector(tag)} {key}")
        checks.barrier()
        line = next((line for line in server.lines[cursor:] if "entity data:" in line), None)
        return float(re.search(r"entity data: ([0-9.E-]+)f", line).group(1)) if line else 0.0

    def health():
        return value("Health")

    def record(name, passed, detail=""):
        checks.results.append({"name": name, "passed": passed, "detail": detail})
        print(f"{'PASS' if passed else 'FAIL'} {server.loader}: {name} {detail}", flush=True)

    def hit(entity_id, stand_x, stand_z):
        """Stands beside the target, waits for a full swing, attacks it by id and returns the damage dealt."""
        server.command(f"tp {PLAYER} {stand_x} -60 {stand_z} 90 0")
        checks.barrier()
        time.sleep(1.6)
        before = health()
        client.send(22, varint(entity_id) + varint(1) + b"\x00")   # ServerboundInteractPacket ATTACK, not sneaking
        time.sleep(0.8)   # past the 10 invulnerable ticks for the next one
        return before - health()

    try:
        server.start("parts", timeout=args.startup_timeout)
        client = LocalClient(server.port, PLAYER, server.loader)
        client.wait_for(lambda c: c.knowledge is not None)
        for command in (f"gamemode survival {PLAYER}", f"effect give {PLAYER} minecraft:resistance 1000 4 true",
                        f"tp {PLAYER} 0 -60 0", "gamerule doDaylightCycle false", "gamerule doMobSpawning false",
                        "time set day", f"item replace entity {PLAYER} weapon.mainhand with minecraft:stone_axe"):
            server.command(command)
        # facing +Z (Rotation 0): head forward at +Z, tail at -Z; no armour, so the damage is the weapon's times the rules
        server.command(f"summon terrassic:tyrannosaurus 0 -60 0 {{Tags:[\"{tag}\"],UUID:{int_uuid(rex)},NoAI:1b,"
                       f"Size:1f,BirthSize:1f,Rotation:[0f,0f],attributes:[{{id:\"minecraft:generic.armor\",base:0d}}]}}")
        checks.barrier()
        client.wait_for(lambda c: str(rex) in c.entities)
        rex_id = client.entities[str(rex)]
        time.sleep(1.0)

        body = hit(rex_id, 2.5, 0)
        body_part = hit(rex_id + 1 + BODY, 2.5, BODY_FORWARD)
        head = hit(rex_id + 1 + HEAD, 2.5, HEAD_FORWARD)
        tail = hit(rex_id + 1 + TAIL_TIP, 2.0, TAIL_FORWARD)
        print(f"INFO {server.loader}: body {body:.3f}, body part {body_part:.3f}, head {head:.3f}, tail {tail:.3f}", flush=True)
        record("the body takes the blow", body > 0.0, f"({body:.3f})")
        record("the body part = 100% of the body", body > 0.0 and abs(body_part / body - 1.0) < 0.02, f"({body_part:.3f})")
        record("the head part takes the blow by its id", head > 0.0, f"({head:.3f})")
        record("the tail part takes the blow by its id", tail > 0.0, f"({tail:.3f})")
        if body > 0.0:
            record("head = 125% of the body", abs(head / body - 1.25) < 0.02, f"({head / body:.3f})")
            record("tail = 75% of the body", abs(tail / body - 0.75) < 0.02, f"({tail / body:.3f})")

        # an arrow falling on the tail tip, well outside the 2.6-block collision box
        before = health()
        server.command(f"summon minecraft:arrow 0 -54 {TAIL_FORWARD} {{Motion:[0d,-1.5d,0d],damage:2d,pickup:0b}}")
        checks.barrier()
        time.sleep(1.5)
        arrow = before - health()
        record("an arrow on the tail tip hits the animal", arrow > 0.0, f"({arrow:.3f})")

        # a narcotic dart falling on the snout doses it (dart's own after-effect through the part)
        server.command(f"summon terrassic:tranq_dart 0 -53 {HEAD_FORWARD} {{Motion:[0d,-1.5d,0d],pickup:0b}}")
        checks.barrier()
        time.sleep(1.5)
        torpor = value("Torpor")
        record("a dart on the head doses the animal", torpor > 0.0, f"(torpor {torpor:.2f})")
    finally:
        if client is not None:
            client.close()
        try:
            server.stop()
        finally:
            temporary.cleanup()
            (server.directory / "results.json").write_text(json.dumps({"source_commit": revision, "loader": args.loader,
                                                                        "checks": checks.results}, indent=2))
    failed = [r["name"] for r in checks.results if not r["passed"]]
    if failed:
        raise AssertionError(f"{len(failed)} hit-part checks failed: {failed}; see {server.directory}")
    print(f"PASS: {args.loader} hit parts ({len(checks.results)} checks)", flush=True)


if __name__ == "__main__":
    main()
