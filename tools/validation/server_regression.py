"""Run isolated dedicated-server persistence checks with real Minecraft commands.

Requires an existing accepted eula.txt supplied explicitly; never touches a player's worlds.
Reports and disposable worlds stay in build/server-regression for inspection.
"""
import argparse
import json
import os
import queue
import signal
import shutil
import subprocess
import tempfile
import threading
import time
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PET_STATE = ('{Owner:[I;1,2,3,4],Saddled:1b,Chested:1b,Female:1b,Sitting:1b,'
             'Cargo:[{Slot:0b,id:"minecraft:diamond",Count:7b}]}')


def verify_pet(marker):
    return f'execute if data entity @e[tag=reg_pet,limit=1] {PET_STATE} run say {marker}'


def saved_fixture_tags(directory):
    """Inspect the saved region payloads before reload, so missing fixtures cannot pass as despawn success."""
    found = set()
    for path in (directory / "world/entities").glob("*.mca"):
        region = path.read_bytes()
        for slot in range(min(1024, len(region) // 4)):
            location = int.from_bytes(region[slot * 4:slot * 4 + 4], "big")
            if not location:
                continue
            offset = (location >> 8) * 4096
            length = int.from_bytes(region[offset:offset + 4], "big")
            if region[offset + 4] != 2:
                raise RuntimeError(f"Unexpected region compression in {path}")
            payload = zlib.decompress(region[offset + 5:offset + 4 + length])
            found.update(tag for tag in ("reg_pet", "reg_named", "reg_normal", "reg_wild", "reg_control") if tag.encode() in payload)
    return found


def run_server(loader, init, directory, stage, commands, expected, timeout):
    log = directory / f"{stage}.log"
    command = [str(ROOT / "gradlew"), "-I", str(init), f":{loader}:runServer",
               "--offline", "--no-daemon", "--console=plain"]
    lines = queue.Queue()
    process = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True, bufsize=1, start_new_session=True)

    def reader():
        for line in process.stdout:
            lines.put(line)
        lines.put(None)

    threading.Thread(target=reader, daemon=True).start()
    started = False
    ready_at = None
    commands_sent = False
    stopping = False
    saved_at = None
    stopped_watcher = False
    markers = set()
    deadline = time.monotonic() + timeout
    try:
        with log.open("w", encoding="utf-8") as stream:
            while True:
                if time.monotonic() > deadline:
                    raise TimeoutError(f"{loader}/{stage}: timeout; see {log}")
                # Entity sections load asynchronously after the server announces readiness.
                # Allow ticks to load the force-loaded fixture chunk before querying or stopping it.
                if ready_at is not None and not commands_sent and time.monotonic() - ready_at >= 5:
                    process.stdin.write("\n".join(commands + ["save-all flush", "stop"]) + "\n")
                    process.stdin.flush()
                    commands_sent = True
                try:
                    line = lines.get(timeout=1)
                except queue.Empty:
                    if saved_at is not None and time.monotonic() - saved_at >= 5:
                        # Architectury's dev hot-reload watcher can keep the JVM alive after Minecraft stops.
                        # Only terminate after the final save following "Stopping server", never during a save.
                        stream.write("[harness] Minecraft shutdown saved; terminating remaining dev watcher.\n")
                        stream.flush()
                        os.killpg(process.pid, signal.SIGTERM)
                        stopped_watcher = True
                        break
                    continue
                if line is None:
                    break
                stream.write(line)
                stream.flush()
                if "Stopping server" in line:
                    stopping = True
                if stopping and "All dimensions are saved" in line:
                    saved_at = time.monotonic()
                if "Done (" in line and not started:
                    started = True
                    ready_at = time.monotonic()
                    print(f"{loader}/{stage}: dedicated server ready", flush=True)
                if "[Server] " in line:
                    for marker in expected:
                        if f"[Server] {marker}" in line:
                            markers.add(marker)
                            print(f"{loader}/{stage}: {marker}", flush=True)
            code = process.wait(timeout=20)
        if (code and not stopped_watcher) or not started or saved_at is None or markers != set(expected):
            raise RuntimeError(f"{loader}/{stage}: exit={code}, missing={set(expected) - markers}; see {log}")
    finally:
        if process.poll() is None:
            # Stop gracefully first; terminate the isolated process group only if startup/shutdown is stuck.
            try:
                process.stdin.write("stop\n")
                process.stdin.flush()
                process.wait(timeout=15)
            except (OSError, subprocess.TimeoutExpired):
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=10)
        process.stdin.close()
        process.stdout.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--loader", choices=["fabric", "forge"], required=True)
    parser.add_argument("--eula-file", type=Path, required=True, help="Existing eula.txt accepted by the operator")
    parser.add_argument("--timeout", type=int, default=240, help="Seconds per launch")
    args = parser.parse_args()
    accepted = any(line.strip().lower() == "eula=true" for line in args.eula_file.read_text().splitlines())
    if not accepted:
        parser.error("the supplied eula.txt does not contain eula=true")
    reports = ROOT / "build/server-regression"
    reports.mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix=f"{args.loader}-", dir=reports))
    (directory / "eula.txt").write_bytes(args.eula_file.read_bytes())
    flat = json.dumps({"layers": [{"block": "minecraft:bedrock", "height": 1},
                                   {"block": "minecraft:dirt", "height": 2},
                                   {"block": "minecraft:grass_block", "height": 1}], "biome": "minecraft:plains"})
    (directory / "server.properties").write_text(
        "server-ip=127.0.0.1\nserver-port=0\nonline-mode=false\nview-distance=2\nsimulation-distance=2\n"
        "level-type=minecraft:flat\ngenerate-structures=false\nspawn-animals=true\nspawn-monsters=false\n"
        f"generator-settings={flat}\n", encoding="utf-8")
    init = directory / "init.gradle"
    # JSON quoting is valid for these absolute path strings in Groovy. Nothing is passed to a shell.
    init.write_text('gradle.projectsEvaluated {\n'
                    f' def p = gradle.rootProject.project(":{args.loader}")\n'
                    f' p.loom.runs.getByName("server").runDir({json.dumps(str(directory))})\n'
                    ' p.tasks.named("runServer") { standardInput = System.in; jvmArgs "-Xmx2G" }\n}\n')
    print(f"Reports and disposable world: {directory}", flush=True)
    create = ["gamerule doMobSpawning false", "gamerule randomTickSpeed 0", "forceload add 0 0",
              'summon terrassic:edmontosaurus 0 80 0 {Tags:["reg_pet"],NoAI:1b,NoGravity:1b,Invulnerable:1b,Roamer:1b,'
              'Owner:[I;1,2,3,4],Saddled:1b,Chested:1b,Female:1b,Sitting:1b,'
              'Cargo:[{Slot:0b,id:"minecraft:diamond",Count:7b}]}',
              'summon terrassic:gallimimus 4 80 0 {Tags:["reg_wild"],NoAI:1b,NoGravity:1b,Invulnerable:1b,Roamer:1b}',
              'summon terrassic:gallimimus 8 80 0 {Tags:["reg_named"],NoAI:1b,NoGravity:1b,Invulnerable:1b,Roamer:1b,'
              'CustomName:\'{"text":"Regression Named"}\'}',
              'summon terrassic:gallimimus 12 80 0 {Tags:["reg_normal"],NoAI:1b,NoGravity:1b,Invulnerable:1b}',
              'summon minecraft:pig 14 80 0 {Tags:["reg_control"],NoAI:1b,NoGravity:1b,Invulnerable:1b}',
              verify_pet("REG_PET_CREATED"),
              'execute if entity @e[tag=reg_wild] run say REG_WILD_CREATED',
              'execute if entity @e[tag=reg_named] run say REG_NAMED_CREATED',
              'execute if entity @e[tag=reg_normal] run say REG_NORMAL_CREATED',
              'execute if entity @e[tag=reg_control] run say REG_CONTROL_CREATED']
    run_server(args.loader, init, directory, "create", create,
               ["REG_PET_CREATED", "REG_WILD_CREATED", "REG_NAMED_CREATED", "REG_NORMAL_CREATED", "REG_CONTROL_CREATED"], args.timeout)
    saved = saved_fixture_tags(directory)
    print(f"{args.loader}/disk: {sorted(saved)}", flush=True)
    shutil.copytree(directory / "world/entities", directory / "before-reload-entities")
    if saved != {"reg_pet", "reg_named", "reg_normal", "reg_control"}:
        raise RuntimeError(f"Unexpected saved population before reload: {saved}; see {directory}")
    reload = ['forceload query', 'data get entity @e[tag=reg_control,limit=1]', verify_pet("REG_PET_RELOADED"),
              'execute unless entity @e[tag=reg_wild] run say REG_WILD_NOT_SAVED',
              'execute if entity @e[tag=reg_named] run say REG_NAMED_RELOADED',
              'execute if entity @e[tag=reg_normal] run say REG_NORMAL_RELOADED',
              'execute if entity @e[tag=reg_control] run say REG_CONTROL_RELOADED']
    run_server(args.loader, init, directory, "reload", reload,
               ["REG_PET_RELOADED", "REG_WILD_NOT_SAVED", "REG_NAMED_RELOADED", "REG_NORMAL_RELOADED", "REG_CONTROL_RELOADED"], args.timeout)
    print(f"PASS: {args.loader} dedicated startup and entity persistence across restart", flush=True)


if __name__ == "__main__":
    main()
