"""Proof that geo_cull.py changes nothing on screen (1.11, docs/DESEMPENHO_1_11.md, "Modelos").

For each species: the geo.json as it is (or as git has it at --ref) against the same model after geo_cull, drawn by the
engine's own renderer (_engine/geo.py: flat shading, z-buffer, no back-face culling, cutout below alpha 10, like the
game's entityCutoutNoCull) from 8 directions, in 3 poses of its animations and 2 sets of shown bones (adult male with
no saddle; young female with the saddle), then compared pixel by pixel. Both sides are built from the faces GeckoLib
takes (geo_cull.face_uvs), so the box-UV cubes rewritten face by face are checked too.

It also leaves out, view by view, the back faces LeanGeoRenderer skips (cubes that were whole boxes, opaque in the
skin), so "after" is what the game writes; --no-backfaces checks the geometry cut alone.

  python3 tools/modelgen/geo_cull_check.py [species ...] [--ref HEAD] [--out DIR] [--jobs 8] [--no-backfaces]
Prints the differing pixels per species (must be 0) and, with --out, saves a contact sheet per species.
"""
import copy, json, math, os, subprocess, sys
from multiprocessing import Pool

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "handmade", "_engine"))
import geo_cull as G  # noqa: E402
import geo  # noqa: E402

VIEWS = [(0, 8), (180, 8), (90, 0), (270, 0), (35, 25), (215, 25), (60, 70), (20, -45)]
SIZE = (420, 300)


def load_text(sid, ref):
    path = os.path.join(G.GEO_DIR, sid + ".geo.json")
    if not ref:
        return open(path).read()
    rel = os.path.relpath(path, G.ROOT)
    return subprocess.run(["git", "-C", G.ROOT, "show", f"{ref}:{rel}"], capture_output=True, text=True, check=True).stdout


def spec_of(geo_json, tmp):
    """geo.py's spec of this geo.json, with each cube's faces as GeckoLib draws them (key = the side it sits on)."""
    with open(tmp, "w") as f:
        json.dump(geo_json, f)
    spec = geo.load_geo(tmp)
    cubes = [c for b in geo_json["minecraft:geometry"][0]["bones"] for c in b.get("cubes", [])]
    assert len(cubes) == len(spec["cubes"])
    for sc, c in zip(spec["cubes"], cubes):
        sc["uv"] = dict(G.face_uvs(c))
    return spec


def poses(sid):
    path = os.path.join(G.ASSETS, "animations", "entity", sid + ".animation.json")
    if not os.path.exists(path):
        return [("rest", None)]
    anims = geo.load_anims(path)
    out = [("rest", None)]
    for name, t in (("walk", 0.3), ("attack", 0.45), ("run", 0.2), ("idle", 0.7)):
        if name in anims and len(out) < 3:
            out.append((name, geo.pose_at(anims[name], min(t, anims[name]["length"]))))
    return out


def hidden_sets(spec):
    names = [b["name"] for b in spec["bones"]]
    male = tuple(n for n in names if n == "female_display" or n == "saddle" or n.startswith("young_"))
    young = tuple(n for n in names if n == "male_display" or n.startswith("adult_"))
    return [("male", male), ("young_female_saddle", young)]


OUTWARD = {"east": (0, 1), "west": (0, -1), "up": (1, 1), "down": (1, -1), "south": (2, 1), "north": (2, -1)}


def without_back_faces(spec, closed, pose, yaw, pitch):
    """What LeanGeoRenderer writes: the faces of the closed opaque cubes that look away from the eye left out
    (here the eye is far away along the view, as geo.render draws: orthographic)."""
    yr, pr = math.radians(yaw), math.radians(pitch)
    fwd = -np.array([-math.sin(yr) * math.cos(pr), math.sin(pr), -math.cos(yr) * math.cos(pr)])
    mats = geo.bone_mats(spec, pose)
    out = copy.deepcopy(spec)
    for c, whole in zip(out["cubes"], closed):
        if not whole:
            continue
        m = mats[c["bone"]] @ geo.affine(c["rotation"], c["origin"])
        for f in list(c["uv"]):
            a, sign = OUTWARD[f]
            n = np.zeros(3)
            n[a] = sign
            if (m[:3, :3] @ n) @ fwd > 0:
                del c["uv"][f]
    return out


def check(args):
    sid, ref, out, backfaces = args
    raw = load_text(sid, ref)
    before = json.loads(raw)
    after = copy.deepcopy(before)
    record = {}
    _total, removed = G.cull(after, sid, record)
    tmp = f"/tmp/geo_cull_check_{sid}_{os.getpid()}.json"
    sa, sb = spec_of(before, tmp), spec_of(after, tmp)
    os.remove(tmp)
    texs = sorted(p for p in os.listdir(G.TEX_DIR) if p.startswith(sid + "_") and p.endswith(".png"))
    tex = Image.open(os.path.join(G.TEX_DIR, (sid + "_male.png") if (sid + "_male.png") in texs else texs[0]))
    # closed as LeanGeoRenderer sees it: a whole box before geo_cull or listed in its record (a shell whose gap is sealed
    # by solid cubes), no zero side, not mirrored, opaque in this skin
    g = before["minecraft:geometry"][0]
    skin = G.Skins(sid, g["description"]["texture_width"], g["description"]["texture_height"])
    alpha = np.asarray(tex.convert("RGBA"))[..., 3]
    skin.imgs = [(alpha, alpha.shape[1] / g["description"]["texture_width"], alpha.shape[0] / g["description"]["texture_height"])]
    closed = [backfaces and min(c["size"]) > 0 and not c.get("mirror") and (c.get("inflate", 0) or 0) >= 0
              and (len(G.face_uvs(c)) == 6 or i in record.get(b["name"], {}))
              and all(skin.opaque(r) for r in G.face_uvs(c).values())
              for b in g["bones"] for i, c in enumerate(b.get("cubes", []))]
    diff = shots = raw = 0
    sheet = []
    for pname, pose in poses(sid):
        for hname, hidden in hidden_sets(sa):
            row = []
            for yaw, pitch in VIEWS:
                _i, fit0, _s = geo.render(sa, tex, yaw, pitch, (8, 6), pose=pose, hidden=hidden)
                # The frame is shifted by a fraction of a pixel, twice. With the model's round numbers some pixel
                # centres fall exactly on an edge, where this renderer breaks a depth tie by drawing order: a removed
                # face seen edge-on along a seam may have won such a pixel by being drawn first. A tie moves with the
                # shift; a face really uncovered differs in both. "persistent" counts only those.
                maps = []
                for frac in (0.137, 0.531):
                    k = (fit0[1] - fit0[0]) / SIZE[0] * frac
                    fit = (fit0[0] + k, fit0[1] + k, fit0[2] + 0.71 * k, fit0[3] + 0.71 * k)
                    ia, _, _ = geo.render(sa, tex, yaw, pitch, SIZE, pose=pose, hidden=hidden, fit=fit, bg=(198, 214, 230))
                    sc = without_back_faces(sb, closed, pose, yaw, pitch) if backfaces else sb
                    ib, _, _ = geo.render(sc, tex, yaw, pitch, SIZE, pose=pose, hidden=hidden, fit=fit, bg=(198, 214, 230))
                    maps.append((np.asarray(ia) != np.asarray(ib)).any(axis=2))
                d = maps[0]
                near = maps[1].copy()
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        near |= np.roll(np.roll(maps[1], dy, 0), dx, 1)
                raw += int(d.sum())
                diff += int((d & near).sum())
                shots += 1
                row.append(ib if not d.any() else Image.fromarray(np.where(d[..., None], [255, 0, 255], np.asarray(ib)).astype(np.uint8)))
            sheet.append(row)
    if out:
        w, h = SIZE
        img = Image.new("RGB", (w * len(VIEWS) // 2, h * len(sheet) // 2))
        for j, row in enumerate(sheet):
            for i, im in enumerate(row):
                img.paste(im.resize((w // 2, h // 2)), (i * w // 2, j * h // 2))
        img.save(os.path.join(out, f"{sid}.png"))
    return sid, sum(removed.values()), shots, raw, diff


def main(argv):
    ref, out, jobs, ids, backfaces = None, None, 8, [], True
    it = iter(argv)
    for a in it:
        if a == "--ref":
            ref = next(it)
        elif a == "--out":
            out = next(it)
        elif a == "--jobs":
            jobs = int(next(it))
        elif a == "--no-backfaces":
            backfaces = False
        else:
            ids.append(a)
    ids = ids or G.species_ids()
    if out:
        os.makedirs(out, exist_ok=True)
    total = 0
    with Pool(jobs) as pool:
        for sid, n, shots, raw, diff in pool.imap_unordered(check, [(s, ref, out, backfaces) for s in ids]):
            total += diff
            print(f"{sid:22s} {n:4d} faces removed, {shots} pictures, {raw} pixels differ, {diff} persistent", flush=True)
    print("total persistent pixels differing:", total)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
