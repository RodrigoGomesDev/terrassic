"""Table of the per-species draw cost from client/dev/DrawBench (docs/DESEMPENHO_1_11.md, "Modelos").

  python3 tools/validation/drawbench_report.py fabric/run/perf/terrassic_drawbench_<label>.tsv [other.tsv]

Per species and way (A = GeckoLib's cube writer, B = lean writer, C = lean + back faces of closed cubes left out):
quads written per animal per frame, time inside the renderer per animal (ms), and the render-thread CPU per frame
above the empty view, per animal (ms); "cows" = that cost over one cow's. With two files, the first column set is
the first file's way A (before) and the second the second file's way C (after).
"""
import csv, sys
from collections import defaultdict


def load(path):
    rows = defaultdict(dict)
    with open(path) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            rows[r["species"]][r["way"]] = r
    out = {}
    for sp, ways in rows.items():
        # an empty view counts only if nothing of ours was drawn in it (the first runs left carcasses in "empty2")
        empties = [float(ways[k]["cpu_ms_per_frame"]) for k in ("empty", "empty2")
                   if k in ways and float(ways[k]["quads_per_frame"]) == 0 and (k == "empty" or sp != "minecraft:cow")]
        base = sum(empties) / max(1, len(empties))
        d = {}
        for w, r in ways.items():
            n = int(r["count"])
            if not n:
                continue
            d[w] = dict(n=n, quads=float(r["quads_per_frame"]) / n, rend=float(r["renderer_ms_per_frame"]) / n,
                        cpu=(float(r["cpu_ms_per_frame"]) - base) / n, fps=1000.0 / float(r["wall_ms_per_frame"]))
        out[sp.split(":")[1]] = d
    return out


def main(argv):
    a = load(argv[0])
    b = load(argv[1]) if len(argv) > 1 else None
    cow = a.get("cow", {}).get("A", {}).get("cpu") or 1e-9
    print(f"one cow: {cow:.4f} ms of render-thread CPU per frame")
    if b is None:
        print("| species | quads A | quads C | renderer ms A | B | C | frame ms A | C | cows A | cows C |")
        print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for sp in sorted(a, key=lambda s: -a[s].get("A", {}).get("rend", 0)):
            if sp == "cow":
                continue
            w = a[sp]
            print(f"| {sp} | {w['A']['quads']:.0f} | {w['C']['quads']:.0f} | {w['A']['rend']:.3f} | {w['B']['rend']:.3f} | "
                  f"{w['C']['rend']:.3f} | {w['A']['cpu']:.3f} | {w['C']['cpu']:.3f} | {w['A']['cpu'] / cow:.1f} | {w['C']['cpu'] / cow:.1f} |")
        return
    print("| species | quads before | after | renderer ms before | after | frame ms before | after | cows before | after |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for sp in sorted(a, key=lambda s: -a[s].get("A", {}).get("rend", 0)):
        if sp == "cow" or sp not in b:
            continue
        x, y = a[sp]["A"], b[sp]["C"]
        print(f"| {sp} | {x['quads']:.0f} | {y['quads']:.0f} | {x['rend']:.3f} | {y['rend']:.3f} | {x['cpu']:.3f} | {y['cpu']:.3f} | "
              f"{x['cpu'] / cow:.1f} | {y['cpu'] / cow:.1f} |")


if __name__ == "__main__":
    main(sys.argv[1:])
