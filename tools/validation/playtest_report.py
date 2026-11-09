#!/usr/bin/env python3
"""Reads the real-world playtest (client/dev/Playtest.java) and says what passed and what failed.

Run the playtest first (sound muted; it creates its own fresh Terrassic world from the title screen):
    TERRASSIC_PLAYTEST=1 ./gradlew :fabric:runClient
then:
    python3 tools/validation/playtest_report.py [report] [game log]

Rule of the author (08/11/2026): besides the flat arenas (behavior_regression.py), every version is played in a real
generated world the way a player meets it. The photos (fabric/run/screenshots/playtest_*.png) still have to be seen.
"""
import re
import sys
from collections import Counter

path = sys.argv[1] if len(sys.argv) > 1 else "fabric/run/terrassic_playtest_report.txt"
log = sys.argv[2] if len(sys.argv) > 2 else "fabric/run/logs/latest.log"
text = open(path, encoding="utf-8").read()
results = []


def check(name, ok, detail):
    results.append((name, ok, detail))


places = re.findall(r"== Place (\d+): ([^\n]+)", text)
check("lugares visitados", len(places) >= 10, f"{len(places)} de 10")
met = [int(x) for x in re.findall(r"animals met: (\d+)", text)]
check("bichos em todo lugar", met and min(met) >= 8, f"mínimo {min(met) if met else 0} por lugar")
species = set()
for block in re.findall(r"species \{([^}]*)\}", text):
    species |= {kv.split("=")[0].strip() for kv in block.split(",") if kv.strip()}
eras = open("common/src/main/java/com/terrassic/config/Eras.java", encoding="utf-8").read()
remade = set(re.findall(r'"(\w+)"', eras[eras.index("REMADE = Set.of("):eras.index(");", eras.index("REMADE = Set.of("))]))
old = sorted(species - remade)
check("só espécies refeitas no mundo", not old, ", ".join(old) or "todas refeitas")
check("espécies vistas", len(species) >= 15, f"{len(species)}: {', '.join(sorted(species))}")

problems = re.findall(r"  PROBLEM ([^\n]+)", text)
stuck = [p for p in problems if "stuck" in p]
long_stuck = [p for p in stuck if int(re.search(r"stuck (\d+) s", p).group(1)) >= 20]
check("ninguém preso 20 s ou mais", not long_stuck, f"{len(long_stuck)}: " + " | ".join(p[:140] for p in long_stuck[:4]))
check("presos (10 a 19 s) poucos", len(stuck) - len(long_stuck) <= 3, f"{len(stuck) - len(long_stuck)}")
walls = sum(int(x) for x in re.findall(r"inside a block (\d+)", text))
check("ninguém dentro de bloco", walls == 0, f"{walls}")
hops = sum(int(x) for x in re.findall(r"hopping in water (\d+)", text))
check("ninguém quicando na água", hops == 0, f"{hops}")

sleepers = [int(x) for x in re.findall(r"closest sleeper to a hunter (\d+)", text)]
check("à noite alguém dormiu", bool(sleepers), f"{len(sleepers)} lugares de noite com dorminhoco")
check("dorme longe do caçador", all(s >= 24 for s in sleepers), f"mais perto: {min(sleepers) if sleepers else '-'} blocos")

# a wild runner herbivore may take the player as target to run from it, but never strikes
RUNNERS = {"edmontosaurus", "gallimimus", "parasaurolophus"}   # the Quetzalcoatlus hunts: it may strike
bad = [m for m in re.findall(r"took the player as target: (\w+) from \d+ blocks, and STRUCK", text) if m in RUNNERS]
check("herbívoro que foge nunca bate", not bad, ", ".join(bad))

try:
    lines = open(log, encoding="utf-8", errors="replace").read().splitlines()
    fired = Counter(re.search(r"\[(\w+)\] ([a-z ]+)", l).group(0)[:40] for l in lines if re.search(r"\[(eco|dasp|alberto|carcharo|majunga)\] ", l))
    # an exception the mod logs as an error or a crash; the known INFO notice "era filter not active
    # (FileNotFoundException ...)" is not one
    crashes = [l for l in lines if "Exception" in l and "terrassic" in l.lower()
               and ("ERROR" in l or "Caused by" in l or "crash" in l.lower()) and "era filter not active" not in l]
    check("sem exceção do mod no log", not crashes, " | ".join(c[:120] for c in crashes[:3]))
    for k, n in sorted(fired.items()):
        results.append((f"disparou {k}", True, str(n)))
except FileNotFoundError:
    pass

for name, ok, detail in results:
    print(f"{'OK   ' if ok else 'FALHA'} {name}  ({detail})")
bad = [r for r in results if not r[1]]
print(f"\nRODADA DE JOGO: {len(results) - len(bad)} passaram, {len(bad)} falharam")
sys.exit(1 if bad else 0)
