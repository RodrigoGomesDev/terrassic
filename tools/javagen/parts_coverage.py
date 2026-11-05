"""Checks that the hit parts leave no gaps (1.7): every sample point of each remade model at rest, turned to several
body yaws, must fall inside the collision box or one of the part boxes, placed as DinosaurEntity#tickParts places them.

    python3 tools/javagen/parts_coverage.py          # report; exit 1 when a species leaves model points uncovered
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import gen_species  # noqa: E402
import parts  # noqa: E402

YAWS = (0, 15, 30, 45, 60, 90, 135)
TOLERANCE = 0.01   # blocks: a point on a face counts as inside


def boxes(sid, yaw, collision=False):
    """The part boxes at a body yaw, as DinosaurEntity#tickParts makes them (the collision box only if asked)."""
    size = gen_species.SIZES[sid]
    w, h = size["w"], size["h"]
    out = [(-w / 2, 0.0, -w / 2, w / 2, h, w / 2, "collision")] if collision else []
    r = math.radians(yaw)
    fx, fz = -math.sin(r), math.cos(r)
    sx, sz = -math.cos(r), -math.sin(r)
    for kind, f, side, up, ln, wd, ph in parts.parts(sid, size["scale"]):
        x, z = fx * f + sx * side, fz * f + sz * side
        hx = (ln * abs(fx) + wd * abs(sx)) / 2
        hz = (ln * abs(fz) + wd * abs(sz)) / 2
        out.append((x - hx, up, z - hz, x + hx, up + ph, z + hz, kind))
    return out


def coverage(sid):
    k = gen_species.SIZES[sid]["scale"] / 16.0
    pts = [(kind, p) for kind, ps in parts.points(sid).items() for p in ps]
    worst = (0.0, None, [])
    for yaw in YAWS:
        r = math.radians(yaw)
        fx, fz = -math.sin(r), math.cos(r)
        sx, sz = -math.cos(r), -math.sin(r)   # the model's +x in the world (the renderer turns it 180 - yaw)
        bx = boxes(sid, yaw)
        missed = []
        for kind, (x, y, z) in pts:
            forward, side, up = -z * k, x * k, y * k
            wx, wz = fx * forward + sx * side, fz * forward + sz * side
            if not any(b[0] - TOLERANCE <= wx <= b[3] + TOLERANCE and b[1] - TOLERANCE <= up <= b[4] + TOLERANCE
                       and b[2] - TOLERANCE <= wz <= b[5] + TOLERANCE for b in bx):
                missed.append((kind, round(forward, 2), round(up, 2), round(side, 2)))
        share = len(missed) / max(1, len(pts))
        if share > worst[0] or worst[1] is None:
            worst = (share, yaw, missed)
    return len(pts), worst


if __name__ == "__main__":
    bad = 0
    for sid in sorted(gen_species.PARTS_SPECIES):
        n, (share, yaw, missed) = coverage(sid)
        kinds = {}
        for m in missed:
            kinds[m[0]] = kinds.get(m[0], 0) + 1
        print(f"{sid:20s} {n:6d} pts  worst yaw {yaw:3d}: {share * 100:5.1f}% uncovered {kinds}")
        for m in missed[:: max(1, len(missed) // 4)][:4]:
            print("      e.g.", m)
        bad += share > 0.0
    sys.exit(1 if bad else 0)
