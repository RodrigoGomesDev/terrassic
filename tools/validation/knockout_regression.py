"""Real dedicated-server checks for knockout save/reload, rejected damage and hand feeding.

Fixture setup uses operator commands; feeding uses a real local protocol connection. No player worlds are used.
"""
import argparse
import hashlib
import json
import struct
import subprocess
import time
import uuid
from pathlib import Path

from local_server import ROOT, LocalServer
from load_profile import freeze_sources
from minecraft_client import LocalClient


class Checks:
    def __init__(self, server):
        self.server = server
        self.sequence = 0
        self.results = []

    def condition(self, condition, negate=False):
        self.sequence += 1
        label = f"REG_KO_{self.sequence}"
        cursor = len(self.server.lines)
        yes, no = ("unless", "if") if negate else ("if", "unless")
        self.server.command(f"execute {yes} {condition} run say {label}_YES")
        self.server.command(f"execute {no} {condition} run say {label}_NO")
        self.server.wait(lambda: any(f"[Server] {label}_" in line for line in self.server.lines[cursor:]), 15)
        return any(f"[Server] {label}_YES" in line for line in self.server.lines[cursor:])

    def expect(self, name, condition, timeout=0, negate=False):
        deadline = time.monotonic() + timeout
        while True:
            passed = self.condition(condition, negate=negate)
            if passed or time.monotonic() >= deadline:
                break
            time.sleep(0.1)
        self.results.append({"name": name, "passed": passed})
        print(f"{'PASS' if passed else 'FAIL'} {self.server.loader}: {name}", flush=True)
        return passed

    def barrier(self):
        self.sequence += 1
        label = f"REG_KO_BARRIER_{self.sequence}"
        cursor = len(self.server.lines)
        self.server.command(f"say {label}")
        self.server.wait(lambda: any(f"[Server] {label}" in line for line in self.server.lines[cursor:]), 15)


def selector(tag):
    return f"@e[tag={tag},limit=1]"


def state(tag, nbt):
    return f"data entity {selector(tag)} {nbt}"


def int_uuid(value):
    return "[I;" + ",".join(map(str, struct.unpack(">4i", value.bytes))) + "]"


def connect(server):
    client = LocalClient(server.port, "TerraKO", server.loader)
    try:
        client.wait_for(lambda c: c.knowledge is not None)
        return client
    except BaseException:
        client.close()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loader", choices=["fabric", "forge"], required=True)
    parser.add_argument("--eula-file", type=Path, required=True)
    parser.add_argument("--startup-timeout", type=int, default=600)
    args = parser.parse_args()
    server = LocalServer(args.loader, args.eula_file, report="knockout-regression", properties={"allow-flight": "true"})
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    _, temporary = freeze_sources(server, revision)
    # Allow testing the pending fix without exposing the running server to other sessions' builds.
    relative = "common/src/main/java/com/terrassic/entity/DinosaurEntity.java"
    source = (ROOT / relative).read_bytes()
    (server.source_root / relative).write_bytes(source)
    (server.directory / "DinosaurEntity.tested.java").write_bytes(source)
    metadata = {"source_commit": revision, "dinosaur_source_sha256": hashlib.sha256(source).hexdigest(),
                "loader": args.loader, "protocol": 763, "scenario": "operator fixtures, real hand interactions, save/restart"}
    checks = Checks(server)
    client = None
    ids = {name: uuid.UUID(f"1f000000-0000-4000-8000-{index:012x}")
           for index, name in enumerate(("zero", "rejected", "wake", "partial", "finished"), 1)}
    print(f"Reports and disposable world: {server.directory}", flush=True)
    try:
        server.start("ko-create", timeout=args.startup_timeout)
        client = connect(server)
        owner = int_uuid(client.profile_uuid)
        server.command("gamemode creative TerraKO")
        server.command("tp TerraKO 0 -60 0")
        server.command("gamerule doDaylightCycle false")
        server.command("time set day")
        server.command("scoreboard objectives add ko_metrics dummy")

        fixtures = [("zero", 12, 0, "TameEffectiveness:60,Torpor:20f"),
                    ("rejected", 20, 0, "TameEffectiveness:90,TameProgress:1f,Torpor:20f,Invulnerable:1b"),
                    ("wake", 28, 0, "TameEffectiveness:70,TameProgress:4f,Torpor:0.001f"),
                    ("partial", 2, 2, "TameEffectiveness:70,TameProgress:1f,Torpor:8f"),
                    ("finished", -2, 2, "TameEffectiveness:70,TameProgress:2f,Torpor:20f")]
        for name, x, z, fields in fixtures:
            server.command(f"summon terrassic:leptoceratops {x} -60 {z} {{Tags:[\"ko_{name}\"],"
                           f"UUID:{int_uuid(ids[name])},CustomName:'\"KO {name}\"',Size:1f,BirthSize:1f,"
                           f"Health:20f,KnockedOut:1b,Tamer:{owner},{fields}}}")
        checks.barrier()
        client.wait_for(lambda c: str(ids["partial"]) in c.entities and str(ids["finished"]) in c.entities)
        checks.expect("efficiency saved before any food", state("ko_zero", "{KnockedOut:1b,TameEffectiveness:60}"))

        server.command(f"damage {selector('ko_rejected')} 1 minecraft:generic")
        checks.barrier()
        checks.expect("invulnerable fixture takes no wound", state("ko_rejected", "{Health:20f}"))
        checks.expect("rejected damage preserves efficiency", state("ko_rejected", "{TameEffectiveness:90}"))
        server.command(f"data merge entity {selector('ko_rejected')} {{Invulnerable:0b}}")
        server.command(f"damage {selector('ko_rejected')} 1 minecraft:generic")
        checks.barrier()
        checks.expect("accepted wound still reduces efficiency", state("ko_rejected", "{TameEffectiveness:80}"))
        checks.expect("wake halves progress", state("ko_wake", "{TameProgress:2f}"), timeout=5)
        checks.expect("wake clears unconscious flag", state("ko_wake", "{KnockedOut:1b}"), negate=True)

        server.command(f"execute store result score before ko_metrics run data get entity {selector('ko_partial')} Torpor 1000")
        server.command("item replace entity TerraKO weapon.mainhand with terrassic:sleep_herb 16")
        checks.barrier()
        client.interact_entity(ids["partial"])
        time.sleep(0.3)
        server.command(f"execute store result score after ko_metrics run data get entity {selector('ko_partial')} Torpor 1000")
        checks.barrier()
        checks.expect("real hand interaction with sleep herb raises torpor", "score after ko_metrics > before ko_metrics")

        server.command("item replace entity TerraKO weapon.mainhand with minecraft:wheat 32")
        checks.barrier()
        client.interact_entity(ids["partial"])
        checks.expect("real wheat interaction advances partial tame", state("ko_partial", "{TameProgress:2f}"), timeout=5)
        checks.expect("feeding records the real player's UUID", state("ko_partial", f"{{Tamer:{owner}}}"))
        client.interact_entity(ids["finished"])
        checks.expect("real hand feeding finishes taming", state("ko_finished", f"{{Owner:{owner}}}"), timeout=5)
        server.command(f"execute store result score hp ko_metrics run attribute {selector('ko_finished')} minecraft:generic.max_health get 1000")
        checks.barrier()
        checks.expect("70 percent efficiency grants expected health bonus", "score hp ko_metrics matches 22799..22801")
        client.close()
        client = None
        server.stop()

        server.start("ko-reload", timeout=args.startup_timeout)
        client = connect(server)
        checks.expect("unfed unconscious efficiency survives restart", state("ko_zero", "{KnockedOut:1b,TameEffectiveness:60}"))
        checks.expect("partial progress and efficiency survive restart", state("ko_partial", "{KnockedOut:1b,TameProgress:2f,TameEffectiveness:70}"))
        checks.expect("tamer UUID survives restart", state("ko_partial", f"{{Tamer:{owner}}}"))
        checks.expect("finished tame and owner survive restart", state("ko_finished", f"{{Owner:{owner}}}"))
        server.command(f"execute store result score hp ko_metrics run attribute {selector('ko_finished')} minecraft:generic.max_health get 1000")
        checks.barrier()
        checks.expect("health bonus survives restart without doubling", "score hp ko_metrics matches 22799..22801")
        client.wait_for(lambda c: str(ids["partial"]) in c.entities)
        server.command("item replace entity TerraKO weapon.mainhand with minecraft:wheat 32")
        checks.barrier()
        client.interact_entity(ids["partial"])
        checks.expect("partial tame can finish after restart", state("ko_partial", f"{{Owner:{owner}}}"), timeout=5)
        checks.expect("completed tame clears knockout", state("ko_partial", "{KnockedOut:1b}"), negate=True)
    finally:
        if client is not None:
            client.close()
        try:
            server.stop()
        finally:
            temporary.cleanup()
            (server.directory / "results.json").write_text(json.dumps({"metadata": metadata, "checks": checks.results}, indent=2))
    failed = [result["name"] for result in checks.results if not result["passed"]]
    if failed:
        raise AssertionError(f"{len(failed)} knockout checks failed: {failed}; see {server.directory}")
    print(f"PASS: {args.loader} knockout interactions and persistence ({len(checks.results)} checks)", flush=True)


if __name__ == "__main__":
    main()
