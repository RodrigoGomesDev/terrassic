"""Gradual localhost load smoke test with real protocol clients and Minecraft's built-in JFR.

Stationary creative clients in a disposable flat world are not equivalent to active human players.
JFR exposes periodic rolling-average tick times, not individual tick percentiles.
"""
import argparse
import ast
import concurrent.futures
import json
import os
import platform
import re
import subprocess
import tempfile
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path

from check_project import assignment
from local_server import ROOT, LocalServer
from minecraft_client import LocalClient


def freeze_sources(server, revision):
    """Build from one Git revision while other fronts continue editing/integrating main."""
    inputs = ["build.gradle", "settings.gradle", "gradle.properties", "gradlew", "gradle", "common", "fabric", "forge",
              "tools/javagen/gen_resources.py"]
    archive = server.directory / "source.tar"
    with archive.open("wb") as output:
        subprocess.run(["git", "archive", "--format=tar", revision, *inputs], cwd=ROOT, stdout=output, check=True)
    temporary = tempfile.TemporaryDirectory(prefix="terrassic-profile-source-")
    source = Path(temporary.name)
    with tarfile.open(archive) as tree:
        for member in tree.getmembers():
            if Path(member.name).is_absolute() or ".." in Path(member.name).parts or member.issym() or member.islnk():
                raise ValueError(f"unsupported source archive member: {member.name}")
        tree.extractall(source)
    server.source_root = source
    return inputs, temporary


def wait_seconds(seconds, clients):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        for client in clients:
            if client.error:
                raise RuntimeError(f"{client.name}: {client.error}")
        time.sleep(min(1, max(0, deadline - time.monotonic())))


def wait_line(server, cursor, text, timeout=30):
    server.wait(lambda: any(text in line for line in server.lines[cursor:]), timeout)


def dinosaur_count(server):
    cursor = len(server.lines)
    server.command("scoreboard players set dinos reg_count 0")
    server.command("execute store result score dinos reg_count if entity @e[type=#terrassic_test:dinosaurs]")
    server.command("scoreboard players get dinos reg_count")
    server.wait(lambda: any(re.search(r"dinos has (\d+) \[reg_count\]", line) for line in server.lines[cursor:]), 15)
    matches = [re.search(r"dinos has (\d+) \[reg_count\]", line) for line in server.lines[cursor:]]
    return int(next(match.group(1) for match in reversed(matches) if match))


def profile(server, classes, count, duration, clients):
    before = set((server.directory / "debug").glob("*.jfr"))
    cursor = len(server.lines)
    server.command("jfr start")
    wait_line(server, cursor, "JFR profiling started")
    wait_seconds(duration, clients)
    cursor = len(server.lines)
    server.command("jfr stop")
    wait_line(server, cursor, "JFR profiling stopped and dumped to")
    candidates = set((server.directory / "debug").glob("*.jfr")) - before
    if len(candidates) != 1:
        raise RuntimeError(f"expected one JFR recording, found {candidates}")
    recording = candidates.pop()
    summary = subprocess.run(["java", "-cp", classes, "JfrSummary", str(recording)], text=True, capture_output=True)
    if summary.returncode:
        raise RuntimeError(f"JFR analysis failed: {summary.stderr}")
    result = json.loads(summary.stdout)
    result.update(players=count, dinosaurs=dinosaur_count(server), recording=recording.name, duration_seconds=duration)
    if result["samples"] < 5:
        raise RuntimeError("too few JFR tick-time events for a useful smoke result")
    print(json.dumps(result), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loader", choices=["fabric", "forge"], required=True)
    parser.add_argument("--eula-file", type=Path, required=True)
    parser.add_argument("--counts", default="0,4,8", help="Increasing player counts, maximum 100")
    parser.add_argument("--warmup", type=int, default=15)
    parser.add_argument("--duration", type=int, default=20)
    parser.add_argument("--startup-timeout", type=int, default=600, help="Allow cold snapshot builds before server readiness")
    parser.add_argument("--max-mspt", type=float, default=35, help="Stop increasing load above this rolling-average mean")
    args = parser.parse_args()
    counts = [int(count) for count in args.counts.split(",")]
    if not counts or counts != sorted(set(counts)) or counts[0] < 0 or counts[-1] > 100:
        parser.error("counts must be unique, increasing and between 0 and 100")
    if args.duration < 10 or args.warmup < 5:
        parser.error("use at least 10 seconds of recording and 5 seconds of warmup")
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    server = LocalServer(args.loader, args.eula_file, report="load-profile", properties={
        "view-distance": 4, "simulation-distance": 4, "max-players": max(20, counts[-1] + 2),
        "allow-flight": "true", "level-seed": "terrassic-regression"})
    source_inputs, source_temporary = freeze_sources(server, revision)
    config = server.directory / "config"
    config.mkdir()
    (config / "terrassic-world.json").write_text(json.dumps({"rift_storms": False}))
    pack = server.directory / "world/datapacks/terrassic_regression"
    tag = pack / "data/terrassic_test/tags/entity_types/dinosaurs.json"
    tag.parent.mkdir(parents=True)
    table = ast.literal_eval(assignment(server.source_root / "tools/javagen/gen_resources.py", "SPECIES"))
    tag.write_text(json.dumps({"values": [f"terrassic:{name}" for name in sorted(table)]}))
    (pack / "pack.mcmeta").write_text(json.dumps({"pack": {"pack_format": 15, "description": "Terrassic local regression fixtures"}}))
    clients = []
    results = []
    metadata = {"loader": args.loader, "protocol": 763, "utc": datetime.now(timezone.utc).isoformat(),
                "platform": platform.platform(), "logical_cpus": os.cpu_count(), "heap_mib": 2048,
                "gradle_heap_mib": 1024, "level_seed": "terrassic-regression", "time": "day (frozen)",
                "view_distance": 4, "simulation_distance": 4, "warmup_seconds": args.warmup,
                "requested_counts": counts, "duration_seconds": args.duration, "max_mspt": args.max_mspt,
                "scenario": "stationary creative protocol clients; flat plains; ecosystem enabled; no rendering",
                "source_commit": revision, "source_archive_inputs": source_inputs, "source_archive": "source.tar"}
    print(f"Reports and disposable world: {server.directory}", flush=True)
    try:
        with tempfile.TemporaryDirectory(prefix="terrassic-jfr-") as classes:
            subprocess.run(["javac", "--release", "17", "-d", classes,
                            str(ROOT / "tools/validation/java/JfrSummary.java")], check=True)
            server.start("load", timeout=args.startup_timeout)
            cursor = len(server.lines)
            server.command("datapack list enabled")
            wait_line(server, cursor, "file/terrassic_regression")
            server.command("scoreboard objectives add reg_count dummy")
            server.command("gamerule doMobSpawning true")
            server.command("gamerule doDaylightCycle false")
            server.command("time set day")

            def add_client(index):
                client = LocalClient(server.port, f"TerraLoad{index:03d}", server.loader)
                try:
                    client.wait_for(lambda c: c.knowledge is not None, timeout=30)
                    return client
                except BaseException:
                    client.close()
                    raise

            for count in counts:
                missing = count - len(clients)
                if missing:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                        futures = [pool.submit(add_client, index) for index in range(len(clients), count)]
                        failures = []
                        for future in futures:
                            try:
                                clients.append(future.result())
                            except Exception as exc:
                                failures.append(exc)
                        if failures:
                            raise failures[0]
                    for index, client in enumerate(clients):
                        server.command(f"gamemode creative {client.name}")
                        server.command(f"tp {client.name} {(index % 10) * 32} -59 {(index // 10) * 32}")
                print(f"{args.loader}: warmup with {count} protocol clients", flush=True)
                wait_seconds(args.warmup, clients)
                results.append(profile(server, classes, count, args.duration, clients))
                (server.directory / "results.json").write_text(json.dumps({"metadata": metadata, "stages": results}, indent=2))
                if results[-1]["mean_window_mspt"] > args.max_mspt:
                    print("Stopped increasing load: rolling-average mean exceeded the configured threshold.", flush=True)
                    break
    finally:
        for client in clients:
            client.close()
        try:
            server.stop()
        finally:
            source_temporary.cleanup()
    print(f"COMPLETE: local smoke profile recorded; see {server.directory / 'results.json'}", flush=True)


if __name__ == "__main__":
    main()
