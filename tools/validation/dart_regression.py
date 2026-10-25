"""Real blowgun use/collisions and aquatic knockout save/restart in a disposable server."""
import argparse
import hashlib
import json
import subprocess
import time
import uuid
from pathlib import Path

from knockout_regression import Checks, int_uuid, selector, state
from local_server import ROOT, LocalServer
from load_profile import freeze_sources
from minecraft_client import LocalClient


def connect(server):
    client = LocalClient(server.port, "TerraDart", server.loader)
    try:
        client.wait_for(lambda c: c.knowledge is not None, timeout=30)
        return client
    except BaseException:
        client.close()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loader", choices=["fabric", "forge"], required=True)
    parser.add_argument("--eula-file", type=Path, required=True)
    args = parser.parse_args()
    server = LocalServer(args.loader, args.eula_file, report="dart-regression", properties={"allow-flight": "true"})
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    _, temporary = freeze_sources(server, revision)
    pack = server.directory / "world/datapacks/dart_regression"
    functions = pack / "data/terrassic_test/functions"
    functions.mkdir(parents=True)
    (pack / "pack.mcmeta").write_text(json.dumps({"pack": {"pack_format": 15, "description": "Disposable dart test clocks"}}))
    for ticks in (20, 40):
        (functions / f"dart_wait_{ticks}.mcfunction").write_text(f"say REG_DART_WAIT_{ticks}\n")
    sources = {}
    for relative in ["entity/TranqDart.java", "entity/DinosaurEntity.java", "entity/SwimmingDinosaur.java", "item/BlowgunItem.java"]:
        name = "common/src/main/java/com/terrassic/" + relative
        data = (ROOT / name).read_bytes()
        (server.source_root / name).write_bytes(data)
        copy = server.directory / "tested-sources" / relative
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_bytes(data)
        sources[relative] = hashlib.sha256(data).hexdigest()
    checks = Checks(server)
    client = None
    marine = uuid.UUID("2f000000-0000-4000-8000-000000000001")
    result = {"source_commit": revision, "loader": args.loader, "tested_sources": sources}
    print(f"Reports and disposable world: {server.directory}", flush=True)

    def score(name, command):
        server.command(f"execute store result score {name} dart_metrics run {command}")
        checks.barrier()

    def aim(x):
        server.command(f"tp TerraDart {x} -60 0 0 0")
        checks.barrier()
        time.sleep(0.1)

    def wait_ticks(ticks):
        cursor = len(server.lines)
        marker = f"REG_DART_WAIT_{ticks}"
        server.command(f"schedule function terrassic_test:dart_wait_{ticks} {ticks}t replace")
        server.wait(lambda: any(f"[Server] {marker}" in line for line in server.lines[cursor:]), 30)

    try:
        server.start("dart-create", timeout=600)
        client = connect(server)
        owner = int_uuid(client.profile_uuid)
        server.command("gamemode survival TerraDart")
        server.command("gamerule doDaylightCycle false")
        server.command("time set day")
        server.command("scoreboard objectives add dart_metrics dummy")
        server.command("clear TerraDart terrassic:tranq_dart")
        server.command("item replace entity TerraDart weapon.mainhand with terrassic:blowgun 1")
        for name, x, extra in [("awake", 0, ""), ("protected", 12, ",Invulnerable:1b")]:
            server.command(f"summon terrassic:triceratops {x} -60 5 {{Tags:[\"dart_{name}\"],"
                           f"CustomName:'\"Dart {name}\"',NoAI:1b,NoGravity:1b,Size:1f,BirthSize:1f,Health:110f{extra}}}")
        aim(0)
        client.use_item()
        time.sleep(0.2)
        checks.expect("no ammunition produces no projectile", "entity @e[type=terrassic:tranq_dart]", negate=True)
        checks.expect("no ammunition leaves target unstunned", f"data entity {selector('dart_awake')} Torpor", negate=True)

        server.command("item replace entity TerraDart weapon.offhand with terrassic:tranq_dart 3")
        checks.barrier()
        client.use_item()
        client.use_item()  # Burst: the second request must be blocked by the server cooldown.
        checks.expect("real dart collision adds torpor", f"data entity {selector('dart_awake')} Torpor", timeout=5)
        checks.expect("burst consumes only one offhand dart", 'data entity TerraDart {Inventory:[{Slot:-106b,id:"terrassic:tranq_dart",Count:2b}]}')
        checks.expect("burst wears blowgun once", 'data entity TerraDart {Inventory:[{Slot:0b,id:"terrassic:blowgun",tag:{Damage:1}}]}')
        score("wound", f"data get entity {selector('dart_awake')} Health 1000")
        checks.expect("awake target receives physical wound", "score wound dart_metrics matches 1..109999")

        server.command("kill @e[type=terrassic:tranq_dart]")
        aim(12)
        wait_ticks(20)
        client.use_item()
        bounced = False
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            score("bounce", "data get entity @e[type=terrassic:tranq_dart,limit=1] Motion[2] 1000")
            if checks.condition("score bounce dart_metrics matches ..-1"):
                bounced = True
                break
            time.sleep(0.05)
        checks.results.append({"name": "blocked dart reverses motion on collision", "passed": bounced})
        print(f"{'PASS' if bounced else 'FAIL'} {server.loader}: blocked dart rebounds", flush=True)
        checks.expect("protected target takes no wound", state("dart_protected", "{Health:110f}"))
        checks.expect("rejected dart does not inject torpor", f"data entity {selector('dart_protected')} Torpor", negate=True)

        server.command("kill @e[type=terrassic:tranq_dart]")
        server.command('summon terrassic:triceratops 24 -60 5 {Tags:["dart_ko"],CustomName:\'"Dart KO"\',NoAI:1b,NoGravity:1b,Size:1f,BirthSize:1f,Health:110f,KnockedOut:1b,Torpor:50f,TameProgress:1f,TameEffectiveness:80}')
        aim(24)
        wait_ticks(20)
        score("before", f"data get entity {selector('dart_ko')} Torpor 1000")
        client.use_item()
        time.sleep(0.3)
        score("after", f"data get entity {selector('dart_ko')} Torpor 1000")
        checks.expect("dart maintains knockout by raising torpor", "score after dart_metrics > before dart_metrics")
        checks.expect("maintenance dart preserves health and efficiency", state("dart_ko", "{Health:110f,TameEffectiveness:80,KnockedOut:1b}"))

        aim(0)
        server.command("item replace entity TerraDart weapon.offhand with terrassic:tranq_dart 16")
        checks.barrier()
        for _ in range(10):
            wait_ticks(20)
            client.use_item()
            time.sleep(0.2)
            if checks.condition(state("dart_awake", "{KnockedOut:1b}")):
                break
        checks.expect("repeated real shots knock down an awake animal", state("dart_awake", "{KnockedOut:1b}"))
        checks.expect("dart knockout records shooter as tamer", state("dart_awake", f"{{Tamer:{owner}}}"))

        server.command("gamemode creative TerraDart")
        server.command("fill 36 -60 -12 66 -53 12 minecraft:water")
        server.command("tp TerraDart 48 -58 -3 0 0")
        server.command(f"summon terrassic:mosasaurus 48 -58 0 {{Tags:[\"dart_marine\"],UUID:{int_uuid(marine)},"
                       f"CustomName:'\"Aquatic KO\"',Size:1f,BirthSize:1f,Health:180f,Air:0s,"
                       f"KnockedOut:1b,Torpor:140f,TameProgress:21.5f,TameEffectiveness:90,Tamer:{owner}}}")
        checks.barrier()
        wait_ticks(40)
        server.command(f"execute at {selector('dart_marine')} store result score water dart_metrics if block ~ ~ ~ minecraft:water")
        checks.barrier()
        checks.expect("marine fixture remains in water", "score water dart_metrics matches 1")
        checks.expect("unconscious marine with depleted air takes no drowning damage", state("dart_marine", "{Health:180f,KnockedOut:1b}"))
        client.close()
        client = None
        server.stop()

        server.start("dart-reload", timeout=600)
        client = connect(server)
        checks.expect("aquatic knockout survives restart", state("dart_marine", "{KnockedOut:1b,TameProgress:21.5f,TameEffectiveness:90}"))
        checks.expect("aquatic tamer survives restart", state("dart_marine", f"{{Tamer:{owner}}}"))
        client.wait_for(lambda c: str(marine) in c.entities)
        server.command("tp TerraDart 48 -58 -3 0 30")
        server.command("item replace entity TerraDart weapon.mainhand with terrassic:blowgun 1")
        checks.barrier()
        time.sleep(0.1)
        score("wet_before", f"data get entity {selector('dart_marine')} Torpor 1000")
        client.use_item()
        wait_ticks(20)
        score("wet_after", f"data get entity {selector('dart_marine')} Torpor 1000")
        checks.expect("underwater dart flight delivers maintenance dose", "score wet_after dart_metrics > wet_before dart_metrics")
        checks.expect("underwater maintenance preserves health and efficiency", state("dart_marine", "{Health:180f,TameEffectiveness:90,KnockedOut:1b}"))
        server.command("item replace entity TerraDart weapon.mainhand with minecraft:cod 1")
        checks.barrier()
        client.interact_entity(marine)
        checks.expect("fish feeding tames unconscious marine", state("dart_marine", f"{{Owner:{owner}}}"), timeout=5)
        checks.expect("marine wakes after taming", state("dart_marine", "{KnockedOut:1b}"), negate=True)
        client.wait_for(lambda c: c.knowledge.get("Species", {}).get("mosasaurus", {}).get("Level") == 4)
        checks.results.append({"name": "marine taming reaches notebook over real connection", "passed": True})
        print(f"PASS {server.loader}: marine taming updates notebook", flush=True)
    finally:
        if client is not None:
            client.close()
        try:
            server.stop()
        finally:
            temporary.cleanup()
            (server.directory / "results.json").write_text(json.dumps({"metadata": result, "checks": checks.results}, indent=2))
    failed = [c["name"] for c in checks.results if not c["passed"]]
    if failed:
        raise AssertionError(f"{len(failed)} dart/aquatic checks failed: {failed}; see {server.directory}")
    print(f"PASS: {server.loader} darts and aquatic knockout ({len(checks.results)} checks)", flush=True)


if __name__ == "__main__":
    main()
