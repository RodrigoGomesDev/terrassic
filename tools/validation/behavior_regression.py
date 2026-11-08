#!/usr/bin/env python3
"""Reads fabric/run/terrassic_behavior_report.txt after the in-game battery and says what passed and what failed.

Run the battery first (sound muted, see the memory note "patches estaveis"):
    TERRASSIC_BEHAVIOR_TEST=1 TERRASSIC_BEHAVIOR_SPECIES=regressao ./gradlew :fabric:runClient --args="--quickPlaySingleplayer partes"
then:
    python3 tools/validation/behavior_regression.py [report]

Each check comes from a bug that reached players or nearly did (1.9.0 -> 1.9.1): spinning jaws, flipped legs, bouncing
in the water, the carcass turned to another angle, raptors asleep at spawn, sea hunters killing fish after fish, herds
and hunters asleep side by side, the calf never picked, duels that never start. The images (rexmotion_gait_*, _jaw_,
_water_, _duel_) still have to be looked at: a number cannot see an elbow bent the wrong way.
"""
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "fabric/run/terrassic_behavior_report.txt"
text = open(path, encoding="utf-8").read()
results = []


def check(name, ok, detail):
    results.append((name, ok, detail))


# jaws: no jaw may turn more than 90 deg from its open to its shut (they spun thousands of degrees in 1.9.0)
jaws = re.findall(r"jaw (\w+): standing after the run, from (-?[\d.]+) to (-?[\d.]+) deg", text)
check("mandíbulas presentes", len(jaws) >= 15, f"{len(jaws)} espécies medidas")
for sp, lo, hi in jaws:
    span = float(hi) - float(lo)
    # no jaw bone found on the client gives +-3.4e38: that is no measure, not a pass
    check(f"mandíbula {sp}", 0.0 <= span <= 90.0, f"abre {span:.0f} graus")

# legs, in two parts. The files: no leg bone in a walk or a run may turn faster than the exporter's limiter
# (anim2.LEG_RATE, 1500 deg/s = 75 a tick); a joint flipping in the keys shows here. In the game: a gait plays at most
# 1.5x (DinosaurEntity.gaitSpeed), so a fast run legitimately reaches 112 a tick (the Pachycephalosaurus run measured
# 107-118 on both versions, 07/11); more than 125 is a pose coming from somewhere else, not the cycle.
import json, os
LEG = re.compile(r"(thigh|shin|foot|arm|forearm|hand|upper|lower)_?[lr]?$|_(l|r)$")
anims = "common/src/main/resources/assets/terrassic/animations/entity"
for sp, _ in re.findall(r"gait (\w+): legs turn at most (-?[\d.]+) deg", text):
    f = os.path.join(anims, f"{sp}.animation.json")
    if not os.path.exists(f):
        continue
    data = json.load(open(f))["animations"]
    worst, where = 0.0, ""
    for g in ("walk", "run"):
        an = data.get(f"animation.{sp}.{g}")
        if not an:
            continue
        for bone, ch in an.get("bones", {}).items():
            if not LEG.search(bone) or not isinstance(ch.get("rotation"), dict):
                continue
            r = ch["rotation"]
            ks = sorted(r, key=float)
            val = lambda k: (r[k].get("post", r[k]) if isinstance(r[k], dict) else r[k])
            for k0, k1 in zip(ks, ks[1:]):
                dt = float(k1) - float(k0)
                if dt <= 0:
                    continue
                for q in range(3):
                    a0, a1 = val(k0)[q], val(k1)[q]
                    if isinstance(a0, (int, float)) and isinstance(a1, (int, float)):
                        rate = abs(a1 - a0) / dt
                        if rate > worst:
                            worst, where = rate, f"{g} {bone} {k0}s"
    check(f"pernas {sp} (arquivo)", worst <= 1550.0, f"{worst:.0f} graus/s no máximo ({where})")
for sp, j in re.findall(r"gait (\w+): legs turn at most (-?[\d.]+) deg", text):
    check(f"pernas {sp}", 0.0 <= float(j) <= 125.0, f"maior salto {float(j):.0f} graus por tick")
for sp in re.findall(r"frame \d+: the animal is gone.*", text):
    check("bicho sumiu na caminhada", False, sp)

# water: the Deinosuchus floats, no hops
m = re.search(r"deinosuchus: (\d+) hops in 10 s", text)
check("Deinossuco na água", m is not None and int(m.group(1)) <= 3, f"{m.group(1) if m else '?'} quiques")

# carcass: lies at the angle of death (it turned south in 1.8.1)
m = re.search(r"body yaw at death (-?[\d.]+)", text)
n = re.search(r"carcasses on the client: (\d+), yaw (-?[\d.]+)", text)
if m and n:
    diff = abs((float(m.group(1)) - float(n.group(2)) + 180) % 360 - 180)
    check("carcaça no ângulo da morte", int(n.group(1)) == 1 and diff < 5.0, f"diferença {diff:.1f} graus")
else:
    check("carcaça no ângulo da morte", False, "sem medida")

# sleep: a Velociraptor spawned by day is awake; sea hunters do not kill fish after fish
check("Velociraptor acordado ao nascer de dia", "spawned at 07:00, 5 s later: awake" in text, "")
m = re.search(r"with 12 fish for 60 s: (\d+) killed", text)
check("caçador do mar saciado", m is not None and int(m.group(1)) <= 3, f"{m.group(1) if m else '?'} peixes em 60 s")

# night: no sleeping herbivore within 16 blocks of a predator
m = re.search(r"sleeping herbivores: nearest predator ([\d.]+) blocks at the closest, ([\d.]+) on average; (\d+) within 16", text)
check("noite: presa longe do predador", m is not None and int(m.group(3)) == 0, m.group(0) if m else "sem medida")

# hunting: the calf first, never a grown sauropod
check("o mais fraco primeiro", "its target is THE CALF" in text, "")
check("topo não caça saurópode adulto", "far: its target is argentinosaurus" not in text, "")

# duels: every pair fights (lunges or blows landed on each side)
for pair, block in re.findall(r"== Duel: (\w+ against \w+)\n((?:    .*\n)+)", text):
    landed = sum(int(x) for x in re.findall(r"landed (\d+)", block))
    check(f"duelo {pair}", landed > 0, f"{landed} golpes acertados")

# behaviour (1.9.5): a hunter brought low runs and heals; a chase that cannot land a blow is given up
m = re.search(r"10 s later ([\d.]+) blocks from its attacker", text)
check("predador ferido foge", m is not None and float(m.group(1)) > 16.0, f"{m.group(1) if m else '?'} blocos do atacante")
m = re.search(r"100 s later: health (\d+)%", text)
check("selvagem se cura", m is not None and int(m.group(1)) >= 35, f"{m.group(1) if m else '?'}% depois de 100 s")
check("desiste da perseguição", "target none (gave up)" in text and "stays given up" in text, "")

# water (1.9.5): no land animal hops while it swims
for sp in ("edmontosaurus", "triceratops", "tyrannosaurus"):
    m = re.search(sp + r": (\d+) hops in 10 s", text)
    if m:
        check(f"{sp} nadando", int(m.group(1)) <= 3, f"{m.group(1)} quiques")

# steps (1.9.5): the model never jumps a whole block in a tick on a 1-block step
for sp, box, drawn in re.findall(r"  (\w+): box jumps up to ([\d.]+) blocks in a tick, the model up to ([\d.]+)", text):
    if sp == "velociraptor":
        continue        # a small one hops the step: the arc is smooth already
    check(f"degrau {sp}", float(drawn) <= 0.4, f"caixa {box}, modelo {drawn} bloco por tick")

# territory and pack (1.9.5)
check("território: sem aviso fora do alcance", "player 9 blocks off, 4 s: warning false, target none" in text, "")
check("território: ataca quem fica perto", "the player (charged)" in text, "")
m = re.search(r"pack (\d+), pack bonus \+(\d+)%", text)
check("bônus de bando", m is not None and int(m.group(1)) == 2 and int(m.group(2)) == 30, m.group(0) if m else "sem medida")

# paths (1.9.5): every walker gets through the pillars (a straight-line navigation once left three of four stuck)
for sp, how in re.findall(r"  (\w+): body turned \d+ deg in all, (arrived in [\d.]+ s|DID NOT ARRIVE in 30 s)", text):
    check(f"caminho {sp}", how.startswith("arrived"), how)

bad = [r for r in results if not r[1]]
for name, ok, detail in results:
    print(("OK    " if ok else "FALHA ") + name + (f"  ({detail})" if detail else ""))
print(f"\nREGRESSÃO: {len(results) - len(bad)} passaram, {len(bad)} falharam")
sys.exit(1 if bad else 0)
