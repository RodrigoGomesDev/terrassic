#!/usr/bin/env python3
"""Reads the JFR recordings of the performance scene (client/dev/PerfTest, TERRASSIC_PERF=1) and says what share of the
server thread and of the render thread ran Terrassic code, and where (docs/DESEMPENHO_1_11.md).

    TERRASSIC_PERF=1 TERRASSIC_PERF_LABEL=depois1 caffeinate -dimsu ./gradlew :fabric:runClient
    python3 -B tools/validation/perf_report.py fabric/run/perf/terrassic_perf_depois1.jfr [more.jfr ...]

A sample counts for the mod when any frame of its stack is ours (com.terrassic.*, or a mixin handler merged into a
vanilla class with "$terrassic$" in its name): the same "this mod is on the stack" attribution a sampling profiler such
as Spark makes. The measurement itself (com.terrassic.client.dev.*) is left out. Each sample is also put in one bucket
(pathfinding, movement and collisions, ...) by the first matching frame from the bottom of the list below.

Needs the JDK's `jfr` tool (JAVA_HOME/bin/jfr or on the PATH). Streams its text output: no big memory.
"""
import collections
import os
import re
import shutil
import subprocess
import sys

BUCKETS = {
    "Server thread": [
        ("busca de caminho (A*)", "PathFinder.findPath"),
        ("seguir caminho", "PathNavigation.tick"),
        ("movimento e colisão (vanilla)", "Entity.move"),
        ("empurrões (vanilla)", "LivingEntity.pushEntities"),
        ("partes: getEntities", "$terrassic$addParts"),
        ("partes: posição", "DinosaurEntity.placeParts"),
        ("buscas de vizinhos", "getEntitiesOfClass"),
        ("objetivos de IA (resto)", "GoalSelector.tick"),
    ],
    "Render thread": [
        ("partes por quadro", "$terrassic$placeParts"),
        ("GeckoLib: animação", "AnimationProcessor.tickAnimation"),
        ("GeckoLib: animação", "AnimationController"),
        ("camada viva / ajustes do modelo", "setCustomAnimations"),
        ("GeckoLib: vértices", "renderRecursively"),
        ("carcaças", "CarcassRenderer"),
        ("tick das entidades no cliente", "tickNonPassenger"),
    ],
}


def jfr_tool():
    home = os.environ.get("JAVA_HOME")
    for c in ([os.path.join(home, "bin", "jfr")] if home else []) + [
            shutil.which("jfr") or "", "/Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home/bin/jfr"]:
        if c and os.path.exists(c):
            return c
    sys.exit("jfr tool not found: set JAVA_HOME to a JDK 21")


FRAME = re.compile(r"^\s+([\w$./<>\[\]]+)\.([\w$<>]+)\(.*\)\s+line:")


def ours(cls, method):
    if cls.startswith("com.terrassic.client.dev."):
        return False
    return cls.startswith("com.terrassic.") or "$terrassic$" in method


def samples(path):
    """Yields (thread, [(class, method), ...] innermost first) for every execution sample."""
    p = subprocess.Popen([jfr_tool(), "print", "--events", "jdk.ExecutionSample", "--stack-depth", "256", path],
                         stdout=subprocess.PIPE, text=True, bufsize=1 << 20)
    thread, frames, in_stack = None, [], False
    for line in p.stdout:
        if line.startswith("jdk.ExecutionSample"):
            thread, frames, in_stack = None, [], False
        elif "sampledThread = " in line:
            m = re.search(r'sampledThread = "([^"]*)"', line)
            thread = m.group(1) if m else ""
        elif "stackTrace = [" in line:
            in_stack = True
        elif in_stack:
            m = FRAME.match(line)
            if m:
                frames.append((m.group(1), m.group(2)))
            elif line.strip() == "]":
                in_stack = False
                yield thread, frames
    p.wait()


def report(path):
    tot = collections.Counter()
    mod = collections.Counter()
    buckets = {t: collections.Counter() for t in BUCKETS}
    inner = {t: collections.Counter() for t in BUCKETS}
    for thread, frames in samples(path):
        if thread not in BUCKETS:
            continue
        tot[thread] += 1
        mine = [(c, m) for c, m in frames if ours(c, m)]
        if not mine:
            continue
        mod[thread] += 1
        c, m = mine[0]
        inner[thread][c.rsplit(".", 1)[-1] + "." + m] += 1
        names = [c.rsplit(".", 1)[-1] + "." + m for c, m in frames]
        for label, pat in BUCKETS[thread]:
            if any(pat in n for n in names):
                buckets[thread][label] += 1
                break
        else:
            buckets[thread]["outros (código do mod e vanilla abaixo dele)"] += 1
    print(f"# {os.path.basename(path)}")
    for t in BUCKETS:
        n = tot[t]
        share = 100.0 * mod[t] / n if n else 0.0
        print(f"{t}: {n} amostras, {mod[t]} com o mod = {share:.1f}%")
        for label, k in buckets[t].most_common():
            print(f"    {100.0 * k / max(1, n):5.1f}%  {label}")
        print("  quadro mais interno do mod:")
        for name, k in inner[t].most_common(12):
            print(f"    {100.0 * k / max(1, n):5.1f}%  {name}")
    return {t: (tot[t], mod[t]) for t in BUCKETS}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for f in sys.argv[1:]:
        report(f)
        print()
