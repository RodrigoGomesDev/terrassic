"""Hit parts (1.7, docs/PLANO_PARTES.md): boxes for the head, the neck and the tail of each remade species, measured
from its GeckoLib model at rest, so a blow or an arrow that lands on the snout or the tail tip hits the creature even
outside its collision box (kept narrow so it walks through forests).

The body stays the collision box itself (100%). Every part is a square box (Minecraft boxes do not turn), so a long
head, neck or tail is cut into pieces about as long as they are wide. Units: metres at model scale 1.0 (the renderer's
MODEL_SCALE is applied here; the creature's own size, getScale(), is applied in game).

    python3 tools/javagen/parts.py            # prints the table for every remade species
"""
import json
import math
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
GEO = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "geo", "entity")

# Damage multiplier per kind, mirrored in DinoPart.Kind (Java): head 125%, neck/body 100%, tail and legs 75%.
KINDS = ("head", "neck", "tail")
# At most this many pieces per kind.
MAX_PIECES = {"head": 2, "neck": 2, "tail": 4}
# Pieces narrower than this (metres at scale 1.0) are widened: a tail tip still has to be hittable.
MIN_SIZE = 0.35
# A piece is never shorter than this (metres at scale 1.0): small creatures get one or two pieces, not a string of beads.
MIN_STEP = 0.6
# Bones shown only for one sex, one age or with gear: not part of the body at rest (art/build_report.json leaves them out).
HIDDEN = ("saddle", "male_display", "female_display")


def _kind(bone, parents):
    """head / neck / tail / body for a bone, from its own name or its ancestors'."""
    name = bone
    while name is not None:
        if name == "head":
            return "head"
        if name.startswith("neck") or name == "throat":
            return "neck"
        if name.startswith("tail"):
            return "tail"
        name = parents.get(name)
    return "body"


def _rot(p, pivot, rot):
    """Rotates point p about pivot by a Bedrock bone/cube rotation (degrees, applied X, then Y, then Z)."""
    x, y, z = p[0] - pivot[0], p[1] - pivot[1], p[2] - pivot[2]
    rx, ry, rz = (math.radians(a) for a in rot)
    # GeckoLib reads Bedrock X and Y rotations negated
    rx, ry = -rx, -ry
    c, s = math.cos(rx), math.sin(rx)
    y, z = y * c - z * s, y * s + z * c
    c, s = math.cos(ry), math.sin(ry)
    x, z = x * c + z * s, -x * s + z * c
    c, s = math.cos(rz), math.sin(rz)
    x, y = x * c - y * s, x * s + y * c
    return [x + pivot[0], y + pivot[1], z + pivot[2]]


def _samples(cube):
    """A grid of points through a cube (every ~4 px), in model pixels."""
    o, s = cube["origin"], cube["size"]
    inf = cube.get("inflate", 0)
    steps = [max(1, int(math.ceil(abs(s[i]) / 4.0))) for i in range(3)]
    pts = []
    for i in range(steps[0] + 1):
        for j in range(steps[1] + 1):
            for k in range(steps[2] + 1):
                pts.append([o[0] - inf + (s[0] + 2 * inf) * i / steps[0],
                            o[1] - inf + (s[1] + 2 * inf) * j / steps[1],
                            o[2] - inf + (s[2] + 2 * inf) * k / steps[2]])
    if cube.get("rotation"):
        pivot = cube.get("pivot", [0, 0, 0])
        pts = [_rot(p, pivot, cube["rotation"]) for p in pts]
    return pts


def points(species):
    """Every sample point of the model at rest, by kind: {kind: [(x, y, z) px]}."""
    with open(os.path.join(GEO, f"{species}.geo.json")) as f:
        geo = json.load(f)["minecraft:geometry"][0]
    bones = {b["name"]: b for b in geo["bones"]}
    parents = {b["name"]: b.get("parent") for b in geo["bones"]}
    out = {}
    def hidden(name):
        while name is not None:
            if name in HIDDEN or name.startswith("young_"):
                return True
            name = parents.get(name)
        return False

    for b in geo["bones"]:
        if hidden(b["name"]):
            continue
        pts = []
        for cube in b.get("cubes", []):
            if min(abs(v) for v in cube["size"]) < 0.01:
                continue   # planes (teeth, membranes) do not take a hit box of their own
            pts.extend(_samples(cube))
        # up the chain: this bone's rotation, then its parent's...
        name = b["name"]
        while name is not None:
            bone = bones[name]
            if bone.get("rotation"):
                pts = [_rot(p, bone.get("pivot", [0, 0, 0]), bone["rotation"]) for p in pts]
            name = parents.get(name)
        out.setdefault(_kind(b["name"], parents), []).extend(pts)
    return out


def neck_base(species):
    """Where the head turns (the first neck bone's pivot, or the head's): (forward, up) px at rest."""
    with open(os.path.join(GEO, f"{species}.geo.json")) as f:
        geo = json.load(f)["minecraft:geometry"][0]
    for b in geo["bones"]:
        if b["name"].startswith("neck") or b["name"] == "head":
            return -b["pivot"][2], b["pivot"][1]
    return 0.0, 0.0


def parts(species, model_scale):
    """[(kind, forward, up, width, height)] in metres at scale 1.0: forward from the creature's centre (negative =
    behind), up = the bottom of the box above its feet."""
    k = model_scale / 16.0
    pts = points(species)
    result = []
    for kind in KINDS:
        p = pts.get(kind)
        if not p:
            continue
        # the model faces -Z: forward = -z
        fz = [-q[2] for q in p]
        lo, hi = min(fz), max(fz)
        width = (max(q[0] for q in p) - min(q[0] for q in p))
        length = hi - lo
        n = max(1, min(MAX_PIECES[kind], int(round(length / max(width, 1e-3))), int(length * k / MIN_STEP)))
        step = length / n
        for i in range(n):
            a, b = lo + step * i, lo + step * (i + 1)
            sl = [q for q, f in zip(p, fz) if a - 1e-6 <= f <= b + 1e-6]
            if not sl:
                continue
            w = max(max(q[0] for q in sl) - min(q[0] for q in sl), step)
            y0, y1 = min(q[1] for q in sl), max(q[1] for q in sl)
            result.append((kind, round((a + b) / 2 * k, 3), round(y0 * k, 3),
                           round(max(w * k, MIN_SIZE), 3), round(max((y1 - y0) * k, MIN_SIZE), 3)))
    return result


def bounds(species):
    pts = [q for v in points(species).values() for q in v]
    return [[min(q[i] for q in pts) for i in range(3)], [max(q[i] for q in pts) for i in range(3)]]


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    import gen_species
    report = json.load(open(os.path.join(ROOT, "art", "build_report.json")))
    for sid in sorted(gen_species.PARTS_SPECIES):
        print(sid, "model", [[round(v, 1) for v in c] for c in bounds(sid)],
              "report", [[round(v, 1) for v in c] for c in report[sid]["bounds_px"]])
        for row in parts(sid, gen_species.SIZES[sid]["scale"]):
            print("   ", row)
