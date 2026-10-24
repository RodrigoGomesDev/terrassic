"""Interactive disposable dedicated server, bound to localhost, for network/load regressions."""
import json
import os
import signal
import socket
import subprocess
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class LocalServer:
    def __init__(self, loader, eula_file, report="network-regression", properties=None):
        self.loader = loader
        self.source_root = ROOT
        if not any(line.strip().lower() == "eula=true" for line in eula_file.read_text().splitlines()):
            raise ValueError("supply an existing accepted eula.txt")
        reports = ROOT / "build" / report
        reports.mkdir(parents=True, exist_ok=True)
        self.directory = Path(tempfile.mkdtemp(prefix=f"{loader}-", dir=reports))
        (self.directory / "eula.txt").write_bytes(eula_file.read_bytes())
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            self.port = probe.getsockname()[1]
        flat = {"layers": [{"block": "minecraft:bedrock", "height": 1}, {"block": "minecraft:dirt", "height": 2},
                           {"block": "minecraft:grass_block", "height": 1}], "biome": "minecraft:plains"}
        values = {"server-ip": "127.0.0.1", "server-port": self.port, "online-mode": "false",
                  "enforce-secure-profile": "false", "view-distance": 2, "simulation-distance": 2,
                  "level-type": "minecraft:flat", "generate-structures": "false", "spawn-animals": "true",
                  "spawn-monsters": "false", "generator-settings": json.dumps(flat)}
        values.update(properties or {})
        if values["server-ip"] != "127.0.0.1":
            raise ValueError("regression server must stay bound to localhost")
        (self.directory / "server.properties").write_text("".join(f"{key}={value}\n" for key, value in values.items()))
        self.init = self.directory / "init.gradle"
        self.init.write_text('gradle.projectsEvaluated {\n'
                            f' def p = gradle.rootProject.project(":{loader}")\n'
                            f' p.loom.runs.getByName("server").runDir({json.dumps(str(self.directory))})\n'
                            ' p.tasks.named("runServer") { standardInput = System.in; jvmArgs "-Xmx2G" }\n}\n')
        self.process = None
        self._condition = threading.Condition()
        self._command_lock = threading.Lock()

    def start(self, stage, timeout=360):
        self.lines = []
        self.ready = False
        self.saved = False
        self.stopping = False
        self.ended = False
        self.log_path = self.directory / f"{stage}.log"
        self.process = subprocess.Popen([str(self.source_root / "gradlew"), "-Dorg.gradle.jvmargs=-Xmx1G", "-I", str(self.init), f":{self.loader}:runServer",
                                         "--offline", "--no-daemon", "--console=plain"], cwd=self.source_root,
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        text=True, bufsize=1, start_new_session=True)

        def reader():
            with self.log_path.open("w", encoding="utf-8") as log:
                for line in self.process.stdout:
                    log.write(line)
                    log.flush()
                    with self._condition:
                        self.lines.append(line)
                        self.ready |= "Done (" in line
                        self.stopping |= "Stopping server" in line
                        self.saved |= self.stopping and "All dimensions are saved" in line
                        self._condition.notify_all()
            with self._condition:
                self.ended = True
                self._condition.notify_all()

        self._reader = threading.Thread(target=reader, daemon=True)
        self._reader.start()
        self.wait(lambda: self.ready, timeout)
        self.command("gamerule doMobSpawning false")
        self.command("say REG_NETWORK_READY")
        self.wait(lambda: any("[Server] REG_NETWORK_READY" in line for line in self.lines), 15)
        print(f"{self.loader}/{stage}: server ready on localhost:{self.port}", flush=True)

    def command(self, command):
        with self._command_lock:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()

    def wait(self, predicate, timeout):
        deadline = time.monotonic() + timeout
        with self._condition:
            while not predicate():
                if self.ended:
                    raise RuntimeError(f"server ended early; see {self.log_path}")
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError(f"server condition not reached; see {self.log_path}")
                self._condition.wait(remaining)

    def stop(self):
        if self.process is None:
            return
        try:
            if self.process.poll() is None:
                self.command("save-all flush")
                self.command("stop")
                self.wait(lambda: self.saved, 45)
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # The Architectury dev watcher can outlive a fully saved Minecraft shutdown.
                    os.killpg(self.process.pid, signal.SIGTERM)
                    self.process.wait(timeout=10)
        finally:
            if self.process.poll() is None:
                os.killpg(self.process.pid, signal.SIGTERM)
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(self.process.pid, signal.SIGKILL)
                    self.process.wait(timeout=10)
            self._reader.join(timeout=5)
            self.process.stdin.close()
            self.process.stdout.close()
            self.process = None
