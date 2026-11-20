"""Remove from the exported geo.json the cube faces that can never be seen (1.11, docs/DESEMPENHO_1_11.md).

GeckoLib draws the six faces of every cube; a face left out of the per-face "uv" is never built (BakedModelFactory
#buildQuad returns null and GeoRenderer#renderCube skips it). Many faces of our models sit inside other cubes of the
same bone, or flush against them: they cost vertices every frame and never reach the screen.

What is removed (conservative on purpose):
  * only cubes of the SAME bone are taken as cover, since animations move the bones against each other (and a hidden
    bone hides all its cubes together, so cover and covered are always shown together);
  * a cube covers only if it is "solid": not rotated, no zero side, all six faces present, and every texel of all six
    faces fully opaque (alpha 255) in every skin of the species (<id>_*.png: male, female, alpha, baby...);
  * a face of an unrotated cube goes when every point of it is in the INTERIOR of the union of the solid cubes of its
    bone (exact test on a compressed grid; a face flush on the surface stays, a face pressed against another solid
    cube goes together with that cube's face, since both are then inside the union);
  * a face of a rotated cube goes only when its four corners are strictly inside one single solid cube (convex).
The boundary of the union of the solid cubes is made only of kept, opaque faces, so a removed face was always behind
an opaque kept face from any point outside the model.

Beside the model it writes assets/terrassic/geo_cull/<id>.json: the cubes that were whole boxes before it took faces
out of them, with the SHA-1 of the geo.json it wrote. client/LeanGeoRenderer leaves out the back faces of closed opaque
cubes; a cube with a face missing counts as closed only if that record says so (a cube left open by design shows its
inside through the gap). A geo.json changed afterwards no longer matches the SHA-1 and the record is ignored.

Box-UV cubes (the older Blockbench models) that lose a face are rewritten with per-face UV giving exactly the numbers
GeckoLib computes for the box (floor of the size, the same offsets), which the tool checks for every kept face.

  python3 tools/modelgen/geo_cull.py                      every geo.json in the assets
  python3 tools/modelgen/geo_cull.py euoplocephalus ...   only those
  python3 tools/modelgen/geo_cull.py --skip pachyrhinosaurus
  python3 tools/modelgen/geo_cull.py --dry                 count only, write nothing
Needs numpy and PIL. Idempotent.
"""
import glob, hashlib, json, math, os, sys

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
GEO_DIR = os.path.join(ASSETS, "geo", "entity")
TEX_DIR = os.path.join(ASSETS, "textures", "entity")
# beside the models, not inside geo/ (GeckoLib would read any json there as a model)
SIDE_DIR = os.path.join(ASSETS, "geo_cull")
FACES = ("north", "south", "east", "west", "up", "down")
# face -> (axis, side) in GeckoLib space (x mirrored from the json: "east" is +x there, BakedModelFactory.VertexSet)
PLANE = {"west": (0, 0), "east": (0, 1), "down": (1, 0), "up": (1, 1), "north": (2, 0), "south": (2, 1)}
TOL = 1e-6


def box_face_uvs(c):
    """The (u, v, w, h) GeckoLib takes for each face of a box-UV cube (BakedModelFactory#buildQuad)."""
    u, v = c["uv"][0], c["uv"][1]
    x, y, z = (math.floor(s) for s in c["size"])
    return {"west": (u + z + x, v + z, z, y), "east": (u, v + z, z, y), "north": (u + z, v + z, x, y),
            "south": (u + z + x + z, v + z, x, y), "up": (u + z, v, x, z), "down": (u + z + x, v + z, x, -z)}


def face_uvs(c):
    if isinstance(c["uv"], list):
        return box_face_uvs(c)
    return {f: (d["uv"][0], d["uv"][1], d["uv_size"][0], d["uv_size"][1]) for f, d in c["uv"].items()}


def box(c):
    """The cube's box in GeckoLib space, in pixels (inflate included)."""
    o, s = c["origin"], c["size"]
    inf = c.get("inflate", 0) or 0
    return (np.array([-(o[0] + s[0]) - inf, o[1] - inf, o[2] - inf], float),
            np.array([-o[0] + inf, o[1] + s[1] + inf, o[2] + s[2] + inf], float))


def rotated(c):
    return bool(c.get("rotation")) and any(abs(a) > 1e-9 for a in c["rotation"])


def rot_matrix(c):
    """GeckoLib's cube rotation (RenderUtils#rotateMatrixAroundCube: Z, then Y, then X, of (-rx, -ry, rz))."""
    rx, ry, rz = c["rotation"]
    ax, ay, az = math.radians(-rx), math.radians(-ry), math.radians(rz)
    cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    X = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Y = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Z = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    p = c.get("pivot", [0, 0, 0])
    return Z @ Y @ X, np.array([-p[0], p[1], p[2]], float)


def face_corners(lo, hi, face):
    a, side = PLANE[face]
    u, v = [i for i in range(3) if i != a]
    out = []
    for cu in (lo[u], hi[u]):
        for cv in (lo[v], hi[v]):
            p = np.zeros(3)
            p[a] = hi[a] if side else lo[a]
            p[u], p[v] = cu, cv
            out.append(p)
    return out


class Skins:
    """Every skin of a species, to tell which faces are fully opaque."""

    def __init__(self, sid, tw, th):
        self.imgs = []
        for path in sorted(glob.glob(os.path.join(TEX_DIR, sid + "_*.png"))):
            a = np.asarray(Image.open(path).convert("RGBA"))[..., 3]
            self.imgs.append((a, a.shape[1] / tw, a.shape[0] / th))

    def opaque(self, rect):
        if not self.imgs:
            return False
        u, v, w, h = rect
        if w == 0 or h == 0:
            return False
        for a, sx, sy in self.imgs:
            x0, x1 = math.floor(min(u, u + w) * sx + 1e-9), math.ceil(max(u, u + w) * sx - 1e-9)
            y0, y1 = math.floor(min(v, v + h) * sy + 1e-9), math.ceil(max(v, v + h) * sy - 1e-9)
            if x0 < 0 or y0 < 0 or x1 > a.shape[1] or y1 > a.shape[0] or x1 <= x0 or y1 <= y0:
                return False
            if (a[y0:y1, x0:x1] < 255).any():
                return False
        return True


def covered_2d(r, rects):
    """True when the open rectangle r = (u0, u1, v0, v1) lies inside the union of the closed rectangles."""
    us = sorted({r[0], r[1], *[x for q in rects for x in (q[0], q[1]) if r[0] < x < r[1]]})
    vs = sorted({r[2], r[3], *[x for q in rects for x in (q[2], q[3]) if r[2] < x < r[3]]})
    for i in range(len(us) - 1):
        mu = (us[i] + us[i + 1]) / 2
        if us[i + 1] - us[i] < TOL:
            continue
        for j in range(len(vs) - 1):
            if vs[j + 1] - vs[j] < TOL:
                continue
            mv = (vs[j] + vs[j + 1]) / 2
            if not any(q[0] < mu < q[1] and q[2] < mv < q[3] for q in rects):
                return False
    return True


def inside_union(lo, hi, face, solids, sides=(True, False)):
    """Every point of the (open) face of the unrotated box lo..hi is interior to the union of the solid boxes
    (sides: which sides of the face's plane must be filled, below and/or above it)."""
    a, side = PLANE[face]
    c = hi[a] if side else lo[a]
    u, v = [i for i in range(3) if i != a]
    r = (lo[u], hi[u], lo[v], hi[v])
    if r[1] - r[0] < TOL or r[3] - r[2] < TOL:
        return False
    for below in sides:
        rects = []
        for slo, shi in solids:
            if below and not (slo[a] < c - TOL and shi[a] > c - TOL):
                continue
            if not below and not (slo[a] < c + TOL and shi[a] > c + TOL):
                continue
            rects.append((slo[u], shi[u], slo[v], shi[v]))
        if not rects or not covered_2d(r, rects):
            return False
    return True


def sealed(lo, hi, face, solids):
    """A face the model left out (qa.separate_coplanar drops the face glued to another cube) is sealed when solid
    cubes of the bone fill its whole rectangle on the far side: nothing is seen through the gap from outside, so the
    cube is as good as closed for the back faces (it goes in the record as closed)."""
    return inside_union(lo, hi, face, solids, sides=(not PLANE[face][1],))


def cull(geo, sid, closed=None):
    """Returns (faces before, faces removed per bone) and rewrites geo in place. closed ({bone: {cube index: faces}},
    updated in place) lists the cubes that were whole boxes before the tool took faces out of them (see SIDE_DIR)."""
    g = geo["minecraft:geometry"][0]
    tw, th = g["description"]["texture_width"], g["description"]["texture_height"]
    skins = Skins(sid, tw, th)
    total, removed = 0, {}
    closed = {} if closed is None else closed
    for b in g["bones"]:
        cubes = b.get("cubes", [])
        was = closed.get(b["name"], {})
        whole = [len(face_uvs(c)) == 6 or was.get(i) == len(face_uvs(c)) for i, c in enumerate(cubes)]
        info = []
        for c in cubes:
            uvs = face_uvs(c)
            lo, hi = box(c)
            solid = (not rotated(c) and not c.get("mirror") and min(c["size"]) > 0 and len(uvs) == 6
                     and (isinstance(c["uv"], dict) or all(s >= 1 for s in c["size"]))
                     and all(skins.opaque(uvs[f]) for f in FACES))
            info.append((c, uvs, lo, hi, solid))
        solids = [(lo, hi) for _c, _u, lo, hi, s in info if s]
        for i, (c, uvs, lo, hi, _s) in enumerate(info):
            total += len(uvs)
            if not solids or c.get("mirror"):
                continue
            drop = []
            for f in uvs:
                if not rotated(c):
                    hidden = inside_union(lo, hi, f, solids)
                else:
                    m, p = rot_matrix(c)
                    pts = [m @ (q - p) + p for q in face_corners(lo, hi, f)]
                    hidden = any(all(((slo + TOL < q) & (q < shi - TOL)).all() for q in pts) for slo, shi in solids)
                if hidden:
                    drop.append(f)
            if not drop:
                if (not whole[i] and len(uvs) < 6 and not rotated(c) and min(c["size"]) > 0
                        and all(sealed(lo, hi, f, solids) for f in FACES if f not in uvs)):
                    closed.setdefault(b["name"], {})[i] = len(uvs)
                continue
            keep = {f: uvs[f] for f in FACES if f in uvs and f not in drop}
            c["uv"] = {f: {"uv": [r[0], r[1]], "uv_size": [r[2], r[3]]} for f, r in keep.items()}
            assert face_uvs(c) == keep, (sid, b["name"])     # GeckoLib takes exactly the same numbers as before
            removed[b["name"]] = removed.get(b["name"], 0) + len(drop)
            if whole[i] or (not rotated(c) and min(c["size"]) > 0
                            and all(sealed(lo, hi, f, solids) for f in FACES if f not in uvs)):
                closed.setdefault(b["name"], {})[i] = len(keep)
    return total, removed


def species_ids():
    return sorted(os.path.basename(p)[:-len(".geo.json")] for p in glob.glob(os.path.join(GEO_DIR, "*.geo.json")))


def side_path(sid):
    return os.path.join(SIDE_DIR, sid + ".json")


def read_side(sid, raw):
    """The closed cubes recorded for this exact geo.json (by its SHA-1); {} when there is none or the geo changed."""
    try:
        side = json.load(open(side_path(sid)))
    except (OSError, ValueError):
        return {}
    if side.get("geo_sha1") != hashlib.sha1(raw.encode("utf-8")).hexdigest():
        return {}
    return {b: {int(i): n for i, n in cubes.items()} for b, cubes in side.get("closed", {}).items()}


def cull_species(sid, dry=False, quiet=False):
    path = os.path.join(GEO_DIR, sid + ".geo.json")
    raw = open(path).read()
    geo = json.loads(raw)
    closed = read_side(sid, raw)
    total, removed = cull(geo, sid, closed)
    n = sum(removed.values())
    if n and not dry:
        out = json.dumps(geo, indent=1) + ("\n" if raw.endswith("\n") else "")
        with open(path, "w") as f:
            f.write(out)
        raw = out
    if closed and not dry:
        os.makedirs(SIDE_DIR, exist_ok=True)
        side = {"comment": "tools/modelgen/geo_cull.py: cubes that were whole boxes before their hidden faces were taken out "
                           "(bone -> cube index -> faces left); LeanGeoRenderer treats them as closed. Valid only for the "
                           "geo.json with this SHA-1.",
                "geo_sha1": hashlib.sha1(raw.encode("utf-8")).hexdigest(),
                "closed": {b: {str(i): k for i, k in sorted(cubes.items())} for b, cubes in sorted(closed.items())}}
        with open(side_path(sid), "w") as f:
            json.dump(side, f, indent=1)
            f.write("\n")
    if not quiet:
        print(f"{sid:22s} {total:5d} faces, {n:4d} removed ({100.0 * n / max(1, total):4.1f}%)"
              + ("" if not n else "  " + ", ".join(f"{k} {v}" for k, v in sorted(removed.items(), key=lambda kv: -kv[1])[:4])),
              flush=True)
    return total, n


def after_build(sid):
    """Called at the end of a model build (_engine/proto.geo_json registers it), once the skins are written."""
    import atexit, time
    path = os.path.join(GEO_DIR, sid + ".geo.json")
    start = time.time()

    def run():
        # only when this process wrote the geo (a preview that only reads it leaves it alone)
        if os.path.exists(path) and os.path.getmtime(path) >= start - 1:
            cull_species(sid)
    atexit.register(run)


def main(argv):
    dry = "--dry" in argv
    skip = set()
    ids = []
    it = iter(argv)
    for a in it:
        if a == "--skip":
            skip.add(next(it))
        elif not a.startswith("--"):
            ids.append(a)
    ids = ids or species_ids()
    tot = rem = 0
    for sid in ids:
        if sid in skip:
            print(f"{sid:22s} skipped")
            continue
        t, n = cull_species(sid, dry)
        tot += t
        rem += n
    print(f"total {tot} faces, {rem} removed ({100.0 * rem / max(1, tot):.1f}%)" + (" [dry]" if dry else ""))


if __name__ == "__main__":
    main(sys.argv[1:])
