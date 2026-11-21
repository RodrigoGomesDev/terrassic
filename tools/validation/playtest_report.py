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
check("lugares visitados", len(places) >= 10, f"{len(places)} de 10 (mais a Colônia e 4 habitats na 1.11)")
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

floats = sum(int(x) for x in re.findall(r"\| floating (\d+)", text))
check("ninguém flutuando (física de bicho parado)", floats == 0,
      f"{floats}: " + " | ".join(p[:140] for p in problems if "floating" in p)[:400])

# 1.11.0: the four remade herbivores in the world
m = re.search(r"== Nest Colony: ([^\n]+)", text)
check("Colônia de Ninhos achada", m is not None and "NOT FOUND" not in m.group(1), m.group(1) if m else "sem medida")
m = re.search(r"colony: (\d+) maiasaura eggs in the nests \((\d+) covered\), (\d+) maiasaura within 48 blocks", text)
check("ninhos do Maiassauro na Colônia", m is not None and int(m.group(1)) >= 4 and int(m.group(3)) >= 1, m.group(0) if m else "sem medida")
m = re.search(r"== New herbivores met on the whole tour: ([^\n]+)", text)
if m:
    for kv in m.group(1).split("(")[0].split():
        sp, n = kv.split("=")
        check(f"nasce no mundo: {sp}", int(n) >= 1, f"{n} vistos")
else:
    check("herbívoros novos no mundo", False, "sem medida")
for edge, big, nf, p95, rmax, nr in re.findall(r"lod crossing (\d+) blocks: largest frame change ([\d.]+) \((\d+) frames\); round it p95 ([\d.]+), largest ([\d.]+) \((\d+) frames\)", text):
    ok = int(nf) > 0 and float(big) <= max(1.5 * float(rmax), 0.02)
    check(f"LOD sem pulo a {edge} blocos", ok, f"{float(big):.4f} no cruzamento, até {float(rmax):.4f} em volta ({nf}/{nr} quadros)")

sleepers = [int(x) for x in re.findall(r"closest sleeper to a hunter (\d+)", text)]
check("à noite alguém dormiu", bool(sleepers), f"{len(sleepers)} lugares de noite com dorminhoco")
near = re.findall(r"PROBLEM asleep near a hunter: ([^\n]+)", text)
check("dorme longe do caçador", not near, (" | ".join(near[:3])) or f"mais perto: {min(sleepers) if sleepers else '-'} blocos (24 de caçador em ação, 16 de caçador parado)")

# a wild runner herbivore may take the player as target to run from it, but never strikes
RUNNERS = {"edmontosaurus", "gallimimus", "parasaurolophus"}   # the Quetzalcoatlus hunts: it may strike
bad = [m for m in re.findall(r"took the player as target: (\w+) from \d+ blocks, and STRUCK", text) if m in RUNNERS]
check("herbívoro que foge nunca bate", not bad, ", ".join(bad))

try:
    lines = open(log, encoding="utf-8", errors="replace").read().splitlines()
    fired = Counter(re.search(r"\[(\w+)\] ([a-z ]+)", l).group(0)[:40] for l in lines if re.search(r"\[(eco|dasp|alberto|carcharo|majunga|maia|cory|pachy|thesc)\] ", l))
    # an exception the mod logs as an error or a crash; the known INFO notice "era filter not active
    # (FileNotFoundException ...)" is not one
    crashes = [l for l in lines if "Exception" in l and "terrassic" in l.lower()
               and ("ERROR" in l or "Caused by" in l or "crash" in l.lower()) and "era filter not active" not in l]
    check("sem exceção do mod no log", not crashes, " | ".join(c[:120] for c in crashes[:3]))
    for k, n in sorted(fired.items()):
        results.append((f"disparou {k}", True, str(n)))
    for tag, name in (("maia", "Maiassauro"), ("cory", "Coritossauro"), ("pachy", "Paquirrinossauro"), ("thesc", "Tescelossauro")):
        n = sum(1 for l in lines if f"[{tag}] " in l)
        check(f"comportamento do {name} no mundo", n > 0, f"{n} linhas [{tag}] no log")
    burrows = [l for l in lines if "[thesc] " in l and "burrow" in l]
    check("toca do Tescelossauro no mundo", bool(burrows), f"{len(burrows)} linhas de toca")
    unable = sum(1 for l in lines if "Unable to find animation" in l)
    check("nenhuma animação faltando no log", unable == 0, f"{unable} linhas")
except FileNotFoundError:
    pass

for name, ok, detail in results:
    print(f"{'OK   ' if ok else 'FALHA'} {name}  ({detail})")
bad = [r for r in results if not r[1]]
print(f"\nRODADA DE JOGO: {len(results) - len(bad)} passaram, {len(bad)} falharam")
sys.exit(1 if bad else 0)
