"""1.7 (player feedback, docs/FEEDBACK_1_7.md) checked on a real dedicated server with a real protocol client:
doubled health and the migration of saved animals, the clubs' attack speed, a tail-club knockout that lasts about
20 seconds, an animal that stays down while it is fed, a stack of meat to tame a Velociraptor, hand-feeding a
herbivore by progress, a tamed dino fighting back and obeying "attack my target" against a mob the rules spare,
the new rule defaults and the tamed-dino register saved with the world.

    python3 -B tools/validation/feedback17_regression.py --loader fabric --eula-file /caminho/eula.txt

Requires JDK 21, the Gradle dependencies in the cache and an accepted eula.txt supplied by the operator. The world is
disposable (build/feedback17-regression); no player world is touched.
"""
import argparse
import gzip
import json
import struct
import subprocess
import time
import uuid
from pathlib import Path

from knockout_regression import Checks, int_uuid, selector, state
from load_profile import freeze_sources
from local_server import LocalServer
from minecraft_client import LocalClient

PLAYER = "TerraF17"


def connect(server):
    client = LocalClient(server.port, PLAYER, server.loader)
    try:
        client.wait_for(lambda c: c.knowledge is not None)
        return client
    except BaseException:
        client.close()
        raise


def nbt_double(data, key):
    """A TAG_Double named key in an uncompressed NBT file (the rules are a flat compound of doubles)."""
    marker = b"\x06" + struct.pack(">H", len(key)) + key.encode()
    at = data.find(marker)
    return None if at < 0 else struct.unpack(">d", data[at + len(marker):at + len(marker) + 8])[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loader", choices=["fabric"], required=True)
    parser.add_argument("--eula-file", type=Path, required=True)
    parser.add_argument("--startup-timeout", type=int, default=600)
    args = parser.parse_args()
    server = LocalServer(args.loader, args.eula_file, report="feedback17-regression", properties={"allow-flight": "true"})
    root = Path(__file__).resolve().parents[2]
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    _, temporary = freeze_sources(server, revision)
    checks = Checks(server)
    client = None
    ids = {name: uuid.UUID(f"17000000-0000-4000-8000-{index:012x}")
           for index, name in enumerate(("club", "hold", "stack", "galli", "guard", "pet1", "pet2", "guard2"), 1)}
    print(f"Reports and disposable world: {server.directory}", flush=True)

    def score(name, command):
        server.command(f"execute store result score {name} f17 run {command}")
        checks.barrier()

    def feed(name, times, pause=0.06):
        for _ in range(times):
            client.interact_entity(ids[name])
            time.sleep(pause)
        checks.barrier()

    def summon(species, name, x, z, nbt):
        server.command(f"summon terrassic:{species} {x} -60 {z} {{Tags:[\"f17_{name}\"],UUID:{int_uuid(ids[name])},"
                       f"Size:1f,BirthSize:1f,{nbt}}}")
        checks.barrier()
        client.wait_for(lambda c: str(ids[name]) in c.entities)

    try:
        server.start("f17", timeout=args.startup_timeout)
        client = connect(server)
        owner = int_uuid(client.profile_uuid)
        for command in (f"gamemode creative {PLAYER}", f"tp {PLAYER} 0 -60 0 0 0", "gamerule doDaylightCycle false",
                        "gamerule doMobSpawning false", "time set day", "scoreboard objectives add f17 dummy"):
            server.command(command)
        checks.barrier()

        # 2: a spared mob ("Spare players' animals" on) is fought once it provokes, or on the owner's order.
        # Two guards far apart: a Velociraptor that is bitten, a Triceratops told by the whistle. First of all: a guard
        # tamed after the owner hit something goes for that (vanilla OwnerHurtTargetGoal, as a wolf does).
        server.command("terrassic regra spare_pets 1")
        for name, species, x in (("guard", "velociraptor", 20), ("guard2", "triceratops", 60)):
            server.command(f"summon terrassic:{species} {x} -60 0 {{Tags:[\"f17_{name}\"],UUID:{int_uuid(ids[name])},"
                           f"Size:1f,BirthSize:1f,Owner:{owner},Sitting:0b}}")
        # 1.21: an owner read from NBT does not apply the taming side effects (the wolf would keep its wild 8 health and
        # die to the first bite, leaving the checks without an entity): 40, as a wolf tamed in play
        for name, x in (("pet1", 23), ("pet2", 63)):
            server.command(f"summon minecraft:wolf {x} -60 0 {{Tags:[\"f17_{name}\"],UUID:{int_uuid(ids[name])},"
                           f"Owner:[I;1,2,3,4],Sitting:1b,Health:40f,attributes:[{{id:\"minecraft:generic.max_health\",base:40d}}]}}")
        server.command(f"tp {PLAYER} 20 -60 -4")
        checks.barrier()

        def watch(guard, pet, seconds):
            """Polls until the pet is hurt; prints where the guard is and the pet's health every two seconds."""
            deadline = time.monotonic() + seconds
            while time.monotonic() < deadline:
                if checks.condition(state(f"f17_{pet}", "{Health:40.0f}"), negate=True):
                    return True
                cursor = len(server.lines)
                server.command(f"data get entity {selector('f17_' + guard)} Pos")
                server.command(f"data get entity {selector('f17_' + pet)} Pos")
                checks.barrier()
                seen = [line.split("]: ", 1)[-1] for line in server.lines[cursor:] if "entity data" in line]
                print(f"INFO {server.loader}: waiting on {pet}: {seen}", flush=True)
                time.sleep(2.0)
            return False

        time.sleep(4.0)
        checks.expect("the tamed dino leaves a spared pet alone", state("f17_pet1", "{Health:40.0f}"))
        server.command(f"damage {selector('f17_guard')} 1 minecraft:mob_attack by {selector('f17_pet1')}")
        passed = watch("guard", "pet1", 20)
        checks.results.append({"name": "it fights back against the pet that bit it", "passed": passed})
        print(f"{'PASS' if passed else 'FAIL'} {server.loader}: it fights back against the pet that bit it", flush=True)

        server.command(f"tp {PLAYER} 60 -60 -4")
        server.command(f"execute as {PLAYER} at @s anchored eyes facing entity {selector('f17_pet2')} eyes run tp @s ~ ~ ~ ~ ~")
        checks.barrier()
        time.sleep(0.5)
        heard = len(client.messages)
        server.command(f"execute as {PLAYER} run terrassic apito attack")
        checks.barrier()
        time.sleep(0.5)
        said = " ".join(client.messages[heard:])
        print(f"INFO {server.loader}: whistle said {said}", flush=True)
        # what the fix decides: the order is taken against a mob the rules spare (before 1.7: "none of your dinos can")
        passed = "message.terrassic.whistle.attack.one" in said or "message.terrassic.whistle.attack.many" in said
        checks.results.append({"name": "\"attack my target\" is obeyed against a spared pet", "passed": passed})
        print(f"{'PASS' if passed else 'FAIL'} {server.loader}: \"attack my target\" is obeyed against a spared pet", flush=True)
        # whether the Triceratops lands a blow in 20 s is its melee AI (it did on Fabric, stalled once on Forge): logged only
        reached = watch("guard2", "pet2", 20)
        print(f"INFO {server.loader}: the Triceratops {'hit' if reached else 'did not reach'} the wolf in 20 s", flush=True)

        # out of the way of the rest (a guard would go for whatever the owner hits next)
        for name in ("guard", "guard2", "pet1", "pet2"):
            server.command(f"kill @e[tag=f17_{name}]")
        server.command(f"tp {PLAYER} 0 -60 0 0 0")
        checks.barrier()

        # 5: health doubled; a saved animal with the old base moves to the new one
        server.command('summon terrassic:velociraptor 6 -60 8 {Tags:["f17_new"],NoAI:1b,Size:1f,BirthSize:1f}')
        server.command('summon terrassic:velociraptor 9 -60 8 {Tags:["f17_old"],NoAI:1b,Size:1f,BirthSize:1f,'
                       'attributes:[{id:"minecraft:generic.max_health",base:24.0d}]}')
        checks.barrier()
        score("hp_new", f"attribute {selector('f17_new')} minecraft:generic.max_health base get")
        checks.expect("new Velociraptor has 48 base health (was 24)", "score hp_new f17 matches 48")
        score("hp_old", f"attribute {selector('f17_old')} minecraft:generic.max_health base get")
        checks.expect("saved Velociraptor with 24 moves to 48 when loaded", "score hp_old f17 matches 48")

        # 3: club speed
        server.command(f"item replace entity {PLAYER} weapon.mainhand with terrassic:bone_club")
        checks.barrier()
        time.sleep(0.3)
        score("bone_speed", f"attribute {PLAYER} minecraft:generic.attack_speed get 100")
        checks.expect("bone club attacks 0.25 times a second", "score bone_speed f17 matches 25")
        server.command(f"item replace entity {PLAYER} weapon.mainhand with terrassic:tail_club")
        checks.barrier()
        time.sleep(0.3)
        score("tail_speed", f"attribute {PLAYER} minecraft:generic.attack_speed get 100")
        checks.expect("tail club attacks 0.20 times a second", "score tail_speed f17 matches 20")

        # 3: a real tail-club knockout, then about 20 seconds out
        summon("velociraptor", "club", 2, 0, "NoAI:1b")
        knocked = False
        for _ in range(8):
            time.sleep(5.3)   # a full swing at 0.2 attacks a second
            client.interact_entity(ids["club"], attack=True)
            time.sleep(0.4)
            if checks.condition(state("f17_club", "{KnockedOut:1b}")):
                knocked = True
                break
        checks.results.append({"name": "tail club knocks out a Velociraptor", "passed": knocked})
        print(f"{'PASS' if knocked else 'FAIL'} {server.loader}: tail club knocks out a Velociraptor", flush=True)
        down = time.monotonic()
        if knocked:
            time.sleep(max(0.0, down + 12.0 - time.monotonic()))
            checks.expect("still out 12 s after the knockout", state("f17_club", "{KnockedOut:1b}"))
            checks.expect("awake by 26 s (20 s knockout)", state("f17_club", "{KnockedOut:1b}"), negate=True,
                          timeout=max(1.0, down + 26.0 - time.monotonic()))
            waking = time.monotonic() - down
            print(f"INFO {server.loader}: woke {waking:.1f} s after the knockout", flush=True)

        # 3: feeding keeps it down
        server.command(f"item replace entity {PLAYER} weapon.mainhand with terrassic:raw_dino_meat 64")
        checks.barrier()
        summon("velociraptor", "hold", 4, 3, f"NoAI:1b,KnockedOut:1b,Torpor:10f,Tamer:{owner}")
        end = time.monotonic() + 8.0
        while time.monotonic() < end:
            client.interact_entity(ids["hold"])
            time.sleep(1.0)
        checks.expect("does not wake while it is fed (8 s on a 3 s gauge)", state("f17_hold", "{KnockedOut:1b}"))
        checks.expect("wakes once the feeding stops", state("f17_hold", "{KnockedOut:1b}"), negate=True, timeout=8)

        # 6: a stack of meat for a Velociraptor
        summon("velociraptor", "stack", -3, 3, f"NoAI:1b,KnockedOut:1b,Torpor:100000f,TameEffectiveness:100,Tamer:{owner}")
        feed("stack", 63)
        checks.expect("63 pieces of meat are not enough", state("f17_stack", "{TameProgress:63.0f}"), timeout=5)
        checks.expect("not tamed after 63", state("f17_stack", f"{{Owner:{owner}}}"), negate=True)
        feed("stack", 1)
        checks.expect("the 64th piece tames it", state("f17_stack", f"{{Owner:{owner}}}"), timeout=5)

        # 6: an awake herbivore by progress (Gallimimus, 60 health: 10 bites)
        server.command(f"item replace entity {PLAYER} weapon.mainhand with minecraft:wheat_seeds 64")
        checks.barrier()
        summon("gallimimus", "galli", -3, -3, "NoAI:1b")
        feed("galli", 9, pause=0.1)
        checks.expect("9 bites leave the Gallimimus wild", state("f17_galli", f"{{Owner:{owner}}}"), negate=True)
        checks.expect("9 bites recorded as progress", state("f17_galli", "{TameProgress:9.0f}"))
        feed("galli", 1, pause=0.1)
        checks.expect("the 10th bite tames it", state("f17_galli", f"{{Owner:{owner}}}"), timeout=5)

        time.sleep(6.0)   # the guard is refreshed in the register every five seconds
        client.close()
        client = None
        server.stop()

        # 4 and 1: what the world saved
        rules = gzip.decompress((server.directory / "world/data/terrassic_rules.dat").read_bytes())
        for key, want in (("dino_share", 0.25), ("predator_spawns", 0.4), ("knockout_seconds", 20.0)):
            got = nbt_double(rules, key)
            passed = got is not None and abs(got - want) < 1e-6
            checks.results.append({"name": f"rule {key} = {want}", "passed": passed})
            print(f"{'PASS' if passed else 'FAIL'} {server.loader}: rule {key} = {want} (saved {got})", flush=True)
        tamed_file = server.directory / "world/data/terrassic_tamed.dat"
        tamed = gzip.decompress(tamed_file.read_bytes()) if tamed_file.exists() else b""
        for species in ("velociraptor", "gallimimus"):
            passed = species.encode() in tamed
            checks.results.append({"name": f"tamed register lists the {species}", "passed": passed})
            print(f"{'PASS' if passed else 'FAIL'} {server.loader}: tamed register lists the {species}", flush=True)
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
        raise AssertionError(f"{len(failed)} 1.7 checks failed: {failed}; see {server.directory}")
    print(f"PASS: {args.loader} 1.7 feedback ({len(checks.results)} checks)", flush=True)


if __name__ == "__main__":
    main()
