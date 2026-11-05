"""Hit parts (1.7, docs/PLANO_PARTES.md): boxes that cover the whole model of each remade species at rest (head, neck,
body, tail, and a flyer's wings), so a blow or an arrow that lands anywhere on the animal hits it, even outside its
collision box (kept narrow so it walks through forests). A blow on the head counts 125%, neck and body 100%, tail and
wings 75% (DinoPart.Kind).

Each kind is cut along its own axis (forward for the body line, sideways for a wing) into pieces about as long as they
are wide. A piece is a rectangle that turns with the animal: its length runs along the body, its width across, and in
game its box is the smallest one holding that turned rectangle (DinosaurEntity#tickParts), so the pieces leave no gap
at any angle. Every sample point of the model belongs to exactly one piece, which holds it; tools/javagen/parts_coverage.py
checks it.

Units: metres at model scale 1.0 (the renderer's MODEL_SCALE is applied here; the creature's own size, getScale(), in game).

    python3 tools/javagen/parts.py            # prints the table for every species with parts
"""
import json
import math
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
GEO = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "geo", "entity")
ANIM = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic", "animations", "entity")
# The animations whose poses the parts must hold: standing and moving (and, for a flyer, flying; for a swimmer, swimming).
# The strikes are left out on purpose: a lunge throws the head 2.5 m aside for a fraction of a second, and a box that
# held it would be hit in empty air the rest of the time. Resting, sleeping and knocked out are left out too
# (DinosaurEntity#tickParts lowers the parts for lying down), and so are the displays. Every keyframe time of these, up
# to POSE_SAMPLES per animation, is one pose.
POSES = ("idle", "walk", "run", "stalk", "fly", "glide", "bank_left", "bank_right", "look_side")
FLIGHT_POSES = ("fly", "glide", "bank_left", "bank_right")
# Lying down (asleep, sitting, brooding, knocked out): a layout of its own, with the same pieces (DinoPart.Spec#lying).
LYING_POSES = ("sit", "sleep", "knocked_out", "brood")
# Head down to eat or drink (DinosaurEntity#isHeadDown): a third layout, so the head is hit where it is without making
# the standing head box reach the ground.
HEAD_DOWN_POSES = ("graze", "eat", "drink", "sift", "grit", "pluck")
SWIM_POSES = ("swim",)
POSE_SAMPLES = 16

KINDS = ("head", "neck", "body", "tail", "wing_l", "wing_r")
# At most this many pieces per kind (DinoParts.MAX_PARTS holds the total).
MAX_PIECES = {"head": 2, "neck": 3, "body": 4, "tail": 5, "wing_l": 3, "wing_r": 3}
MAX_TOTAL = 20
# A piece is never shorter than this (metres at scale 1.0): small creatures get few pieces, not a string of beads.
MIN_STEP = 0.5
# Thinner than this (metres at scale 1.0) it is widened about its centre: a tail tip still has to be hittable.
MIN_SIZE = 0.3
# Added on every side (metres at scale 1.0): the model moves a little in its idle and walk.
PAD = 0.05
# Bones shown only for one sex, one age or with gear: not part of the body at rest (art/build_report.json leaves them out).
HIDDEN = ("saddle", "male_display", "female_display")


def _load(species):
    with open(os.path.join(GEO, f"{species}.geo.json")) as f:
        return json.load(f)["minecraft:geometry"][0]


def _kind(bone, parents, membrane, flying=True):
    """head / neck / tail / wing_l / wing_r / body for a bone, from its own name or its ancestors'. A flyer's wing is a
    wing only spread (at rest and in the flight poses); folded on the ground it lies against the body and counts as it."""
    name = bone
    while name is not None:
        if name == "head":
            return "head"
        if name.startswith("neck") or name == "throat":
            return "neck"
        if name.startswith("tail"):
            return "tail"
        if membrane and name.startswith("arm_"):
            if not flying:
                return "body"
            return "wing_l" if name.endswith("_l") else "wing_r"
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
    """A grid of points through a cube (every ~2 px), in model pixels."""
    o, s = cube["origin"], cube["size"]
    inf = cube.get("inflate", 0)
    steps = [max(1, int(math.ceil(abs(s[i]) / 2.0))) for i in range(3)]
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


def _value(frame):
    v = frame.get("post", frame.get("pre")) if isinstance(frame, dict) else frame
    return [float(c) for c in v]


def _channel(channel, t):
    """A bone channel (rotation or position) at time t, linear between its keyframes."""
    if not isinstance(channel, dict):
        return _value(channel)
    keys = sorted((float(k), _value(v)) for k, v in channel.items())
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            f = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return [a + (b - a) * f for a, b in zip(v0, v1)]
    return keys[-1][1]


def poses(species, swimmer=False, wanted=None):
    """[({bone: (rotation, position)}, airborne)]: the rest pose (unless lying), then the sampled poses of the wanted
    animations (POSES by default)."""
    lying = wanted is not None and (set(wanted) <= set(LYING_POSES) or set(wanted) <= set(HEAD_DOWN_POSES))
    out = [] if lying else [({}, True)]
    path = os.path.join(ANIM, f"{species}.animation.json")
    if not os.path.exists(path):
        return out
    with open(path) as f:
        anims = json.load(f)["animations"]
    wanted = (wanted or POSES) + (SWIM_POSES if swimmer and not lying else ())
    for name, anim in anims.items():
        if name.split(".")[-1] not in wanted:
            continue
        bones = anim.get("bones", {})
        times = sorted({float(k) for ch in bones.values() for c in ch.values() if isinstance(c, dict) for k in c})
        if len(times) > POSE_SAMPLES:
            times = [times[round(i * (len(times) - 1) / (POSE_SAMPLES - 1))] for i in range(POSE_SAMPLES)]
        for t in times or [0.0]:
            pose = {}
            for bone, ch in bones.items():
                rot = _channel(ch["rotation"], t) if "rotation" in ch else [0.0, 0.0, 0.0]
                pos = _channel(ch["position"], t) if "position" in ch else [0.0, 0.0, 0.0]
                pose[bone] = (rot, pos)
            out.append((pose, name.split(".")[-1] in FLIGHT_POSES))
    return out


def points(species, animated=True, wanted=None):
    """Every sample point of the model, by kind: {kind: [(x, y, z) px]}, at rest and, if animated, in every pose of
    poses(). Planes (teeth, membranes) count too: a wing membrane is what a flyer is hit on."""
    geo = _load(species)
    bones = {b["name"]: b for b in geo["bones"]}
    parents = {b["name"]: b.get("parent") for b in geo["bones"]}
    membrane = any(name.startswith("mem_") for name in bones)

    def hidden(name):
        while name is not None:
            if name in HIDDEN or name.startswith("young_"):
                return True
            name = parents.get(name)
        return False

    local = {}
    for b in geo["bones"]:
        if hidden(b["name"]):
            continue
        pts = []
        for cube in b.get("cubes", []):
            pts.extend(_samples(cube))
        local[b["name"]] = pts
    swimmer = species in ("mosasaurus",)
    out = {}
    for n, (pose, airborne) in enumerate(poses(species, swimmer, wanted) if animated else [({}, True)]):
        for name, pts in local.items():
            if n > 0 or wanted is not None:
                pts = pts[::4]   # the animated poses with fewer samples: they only widen the boxes a little
            chain = name
            while chain is not None:
                bone = bones[chain]
                rot = list(bone.get("rotation", [0, 0, 0]))
                anim_rot, anim_pos = pose.get(chain, ([0.0, 0.0, 0.0], [0.0, 0.0, 0.0]))
                rot = [r + a for r, a in zip(rot, anim_rot)]
                if any(rot):
                    pts = [_rot(p, bone.get("pivot", [0, 0, 0]), rot) for p in pts]
                if any(anim_pos):
                    pts = [[p[0] + anim_pos[0], p[1] + anim_pos[1], p[2] + anim_pos[2]] for p in pts]
                chain = parents.get(chain)
            out.setdefault(_kind(name, parents, membrane, airborne), []).extend(pts)
    return out


def neck_base(species):
    """Where the head turns to look: the pivot of the bone "head", which GeckoLib turns by the creature's head yaw and
    pitch (DefaultedEntityGeoModel). (forward, up) px at rest."""
    for b in _load(species)["bones"]:
        if b["name"] == "head":
            return -b["pivot"][2], b["pivot"][1]
    return 0.0, 0.0


def _grow(lo, hi, least):
    """Pads an interval and widens it about its centre to at least `least`."""
    lo, hi = lo - PAD, hi + PAD
    if hi - lo < least:
        mid = (lo + hi) / 2
        lo, hi = mid - least / 2, mid + least / 2
    return lo, hi


def parts(species, model_scale, wanted=None, pieces=None):
    """[(kind, forward, side, up, length, width, height)] in metres at scale 1.0. forward/side: the centre, from the
    creature's centre (forward negative = behind; side positive = the model's +x); up: the bottom above its feet;
    length along the body, width across it."""
    k = model_scale / 16.0
    result = []
    rest = points(species, animated=False)
    counts = {}
    for kind, pts in points(species, wanted=wanted).items():
        # metres: forward = -z (the model faces -Z), side = x, up = y
        m = [(-q[2] * k, q[0] * k, q[1] * k) for q in pts]
        along = 1 if kind.startswith("wing") else 0          # a wing is cut outwards, the rest along the body
        across = 1 - along
        lo, hi = min(p[along] for p in m), max(p[along] for p in m)
        # how many pieces from the shape at rest (thin): the swing of a moving tail would make it one wide piece
        r = [(-q[2] * k, q[0] * k) for q in rest.get(kind, pts)]
        breadth = max(p[across] for p in r) - min(p[across] for p in r)
        length = hi - lo
        n = max(1, min(MAX_PIECES[kind], int(round(length / max(breadth, 1e-3))), int(length / MIN_STEP) or 1))
        if pieces is not None:
            n = pieces.get(kind, 0)
            if n == 0:
                continue
        counts[kind] = n
        step = length / n
        for i in range(n):
            a, b = lo + step * i, lo + step * (i + 1)
            sl = [p for p in m if a - 1e-9 <= p[along] <= b + 1e-9]
            if not sl:
                continue
            s0, s1 = _grow(a, b, MIN_SIZE)
            c0, c1 = min(p[across] for p in sl), max(p[across] for p in sl)
            if across == 1:
                c = max(abs(c0), abs(c1))                     # the body line is centred: as wide as its widest side
                c0, c1 = -c, c
            c0, c1 = _grow(c0, c1, MIN_SIZE)
            y0, y1 = _grow(min(p[2] for p in sl), max(p[2] for p in sl), MIN_SIZE)
            if along == 0:
                fwd, side, ln, wd = (s0 + s1) / 2, (c0 + c1) / 2, s1 - s0, c1 - c0
            else:
                fwd, side, ln, wd = (c0 + c1) / 2, (s0 + s1) / 2, c1 - c0, s1 - s0
            result.append((kind, round(fwd, 3), round(side, 3), round(y0, 3), round(ln, 3), round(wd, 3),
                           round(y1 - y0, 3)))
    if pieces is not None:
        for kind, n in pieces.items():
            have = sum(1 for r in result if r[0] == kind)
            # a kind the lying poses do not show (a flyer's wings, folded into the body): empty pieces, never switched on
            result.extend((kind, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0) for _ in range(n - have))
    order = {kind: i for i, kind in enumerate(KINDS)}
    result.sort(key=lambda r: (order[r[0]], -r[1] if r[0] != "tail" else r[1], r[2]))
    assert len(result) <= MAX_TOTAL, f"{species}: {len(result)} parts, more than DinoParts.MAX_PARTS"
    return result


def has_poses(species, wanted):
    with open(os.path.join(ANIM, f"{species}.animation.json")) as f:
        names = {n.split(".")[-1] for n in json.load(f)["animations"]}
    return bool(names & set(wanted))


def layouts(species, model_scale):
    """(standing, lying, head down): the three layouts, piece for piece in the same order (the others have the standing
    pieces' counts; a species without head-down poses keeps standing there)."""
    standing = parts(species, model_scale)
    pieces = {}
    for row in standing:
        pieces[row[0]] = pieces.get(row[0], 0) + 1
    lying = parts(species, model_scale, wanted=LYING_POSES, pieces=pieces)
    low = parts(species, model_scale, wanted=HEAD_DOWN_POSES, pieces=pieces) if has_poses(species, HEAD_DOWN_POSES) else standing
    for other in (lying, low):
        assert [r[0] for r in other] == [r[0] for r in standing], species
    return standing, lying, low


def bounds(species):
    pts = [q for v in points(species).values() for q in v]
    return [[min(q[i] for q in pts) for i in range(3)], [max(q[i] for q in pts) for i in range(3)]]


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    import gen_species
    for sid in sorted(gen_species.PARTS_SPECIES):
        rows = parts(sid, gen_species.SIZES[sid]["scale"])
        print(sid, len(rows), "parts")
        for row in rows:
            print("   ", row)
