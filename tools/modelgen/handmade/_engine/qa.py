"""Shared QA of the hand-made rigs, run by every species build before any preview (the rules learnt on the T. rex,
the Pteranodon and the Velociraptor, so they are checked by code and not found again in game):

  - zero coplanar faces (separate_coplanar moves the smaller face 0.05 px; planes move whole)
  - zero-thickness planes keep ONE face (GeckoLib draws without back-face culling, two faces z-fight)
  - ground: every standing pose touches y = 0 within 0.3 px, no pose goes below it (lowscan)
  - the bar: painted pixels, colours, eye size, head pieces, cubes, compared with the approved models (metrics)
"""
import math
import numpy as np
import geo

FACE_AX = {"east": ("to", 0, 1), "west": ("from", 0, -1), "up": ("to", 1, 1), "down": ("from", 1, -1),
           "south": ("to", 2, 1), "north": ("from", 2, -1)}


def mirror_all(m):
    for c in m.cubes:
        src = c["mirror_of"]
        if src is not None:
            c["from"] = [-src["to"][0], src["from"][1], src["from"][2]]
            c["to"] = [-src["from"][0], src["to"][1], src["to"][2]]


def coplanar_pairs(m):
    for c in m.cubes: c["uv"] = {f: (0, 0, 1, 1) for f in c["faces"]}
    quads = []
    for c, f, cs, r in geo.faces({"bones": m.bones, "cubes": m.cubes}):
        pts = np.array([cs[k] for k in ((0, 0), (1, 0), (1, 1), (0, 1))])
        nrm = np.cross(pts[1] - pts[0], pts[3] - pts[0]); nn = np.linalg.norm(nrm)
        if nn > 1e-9: quads.append((c, f, pts, nrm / nn))
    out = []
    for i in range(len(quads)):
        c1, f1, p1, n1 = quads[i]
        for c2, f2, p2, n2 in quads[i + 1:]:
            # same plane, either facing: GeckoLib does not cull back faces, so opposite faces fight too
            if c1 is c2 or abs(n1 @ n2) < 0.999 or abs((p2[0] - p1[0]) @ n1) > 0.01: continue
            e1 = p1[1] - p1[0]; e1 = e1 / np.linalg.norm(e1); e2 = np.cross(n1, e1)
            b1 = [(p1 @ e).min() for e in (e1, e2)] + [(p1 @ e).max() for e in (e1, e2)]
            b2 = [(p2 @ e).min() for e in (e1, e2)] + [(p2 @ e).max() for e in (e1, e2)]
            ox = min(b1[2], b2[2]) - max(b1[0], b2[0]); oy = min(b1[3], b2[3]) - max(b1[1], b2[1])
            if ox > 0.05 and oy > 0.05:
                out.append((c1, f1, c2, f2))
    for c in m.cubes: c.pop("uv", None)
    return out


def separate_coplanar(m, eps=0.05, rounds=8):
    def area(c, f):
        d = [c["to"][k] - c["from"][k] for k in range(3)]
        ax = FACE_AX[f][1]; return np.prod([d[k] for k in range(3) if k != ax])
    for _ in range(rounds):
        pairs = coplanar_pairs(m)
        if not pairs: return 0
        done = set()
        for c1, f1, c2, f2 in pairs:
            c, f = (c1, f1) if area(c1, f1) <= area(c2, f2) else (c2, f2)
            if c["mirror_of"] is not None:
                c = c["mirror_of"]; f = {"east": "west", "west": "east"}.get(f, f)
            if (id(c), f) in done: continue
            done.add((id(c), f))
            end, ax, sg = FACE_AX[f]
            if c["to"][ax] - c["from"][ax] < 1e-6:
                c["from"][ax] += sg * eps; c["to"][ax] += sg * eps      # a plane moves whole
            else:
                c[end][ax] += sg * eps
        mirror_all(m)
    return len(coplanar_pairs(m))


def single_face_planes(m):
    """a cube with no thickness keeps ONE face (the outer one: east on the left and centred cubes, west on the
    right-hand mirrors, up for flat ones, south for cross planes)"""
    for c in m.cubes:
        d = [c["to"][k] - c["from"][k] for k in range(3)]
        if min(d) > 1e-6: continue
        ax = d.index(min(d))
        keep = {0: "east", 1: "up", 2: "south"}[ax]
        if ax == 0 and c["mirror_of"] is not None: keep = "west"
        c["faces"] = [keep]


# ---------------------------------------------------------------- ground
def lowscan(spec, anims, standing, skip_mats=("teeth", "teeth_lo", "sail", "fin"), fps=20):
    """per animation: lowest point over all frames (must be >= -0.3) and, for standing ones, the highest of the
    per-frame lowest points (must be <= 0.3: the feet stay on the ground). Returns rows and a pass flag."""
    rows, ok = [], True
    for n, (fn, L, *_r) in anims.items():
        lows = []
        for i in range(int(round(L * fps)) + 1):
            p = fn(i / fps)
            lows.append(min(q[:, 1].min() for c, q in geo.cube_points(spec, p) if c.get("mat") not in skip_mats))
        lo, hi = min(lows), max(lows)
        good = lo >= -0.3 and (n not in standing or hi <= 0.3)
        ok &= good
        rows.append((n, round(lo, 2), round(hi, 2), good))
    return rows, ok


# ---------------------------------------------------------------- the bar
def metrics(m, tex, eye_px=None, head_bones=("head", "skull", "jaw")):
    a = np.array(tex.convert("RGBA"))
    op = a[:, :, 3] > 0
    cols = {tuple(x) for x in a[op][:, :3]}
    # share of painted pixels with at least one 4-neighbour of another colour (drawn by form, not flat fills)
    rgb = a[:, :, :3].astype(int)
    diff = np.zeros(op.shape, bool)
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        sh = np.roll(np.roll(rgb, dy, 0), dx, 1); so = np.roll(np.roll(op, dy, 0), dx, 1)
        diff |= so & (np.abs(sh - rgb).sum(2) > 0)
    return {"cubes": len(m.cubes), "head_pieces": sum(1 for c in m.cubes if c["bone"] in head_bones),
            "texture": f"{m.tw}x{m.th}", "painted_px": int(op.sum()), "colours": len(cols),
            "form_share": round(float((diff & op).sum() / max(1, op.sum())), 2), "eye_px": eye_px}


# ---------------------------------------------------------------- pixel bugs
CUTOUT = ("sail", "fin", "teeth", "teeth_lo")


def pixel_bugs(m, tex, cutout=CUTOUT, spikes_ok=("teeth", "teeth_lo")):
    """what reads as a 'pixel bug' in game, found in the texture and the cube sizes:
    mixel   a painted face whose size is not a whole number of pixels (its texels come out stretched)
    hole    a transparent texel on a solid face (the background shows through the animal)
    orphan  on a cut-out face, an opaque texel with at most one opaque neighbour (a stray dot or a 1 px spike)
    thin    a solid cube under 1 px on some axis (shimmers at a distance)"""
    a = np.array(tex.convert("RGBA"))[:, :, 3] > 0
    out = []
    for c in m.cubes:
        d = [c["to"][k] - c["from"][k] for k in range(3)]
        cut = c["mat"] in cutout
        for f in c["faces"]:
            ax = FACE_AX[f][1]
            if any(d[k] > 1e-6 and abs(d[k] - round(d[k])) > 0.11 for k in range(3) if k != ax):
                out.append(("mixel", c["name"], f)); break
        if not cut and min(d) < 1 - 1e-6: out.append(("thin", c["name"], [round(x, 2) for x in d]))
        if c["mirror_of"] is not None: continue
        for f, (u, v, w, h) in c.get("uv", {}).items():
            if w < 0: continue
            reg = a[v:v + h, u:u + w]
            if not cut:
                if (~reg).any(): out.append(("hole", c["name"], f, int((~reg).sum())))
                continue
            p = np.pad(reg, 1)
            nb = p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
            k = int((reg & (nb <= 1)).sum())
            if k and c["mat"] not in spikes_ok: out.append(("orphan", c["name"], f, k))
    return out


def clean_orphans(img, m, cutout=CUTOUT, keep=("teeth", "teeth_lo")):
    """decal pass: clear stray opaque texels on cut-out faces (teeth are allowed to be 1 px)"""
    for c in m.cubes:
        if c["mirror_of"] is not None or c["mat"] not in cutout or c["mat"] in keep: continue
        for f, (u, v, w, h) in c["uv"].items():
            if w < 0: continue
            for _ in range(8):
                reg = img[v:v + h, u:u + w, 3] > 0
                p = np.pad(reg, 1)
                nb = p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
                bad = reg & (nb <= 1)
                if not bad.any(): break
                img[v:v + h, u:u + w][bad] = 0


def pinholes(spec, tex, poses, views=((90, 0), (270, 0), (35, 18), (215, 18), (0, 30), (180, 30), (90, 60)), size=(900, 600),
             hidden=(), max_area=6):
    """cracks where the background shows through the animal (gaps between cubes, cut-outs biting into solid faces):
    small enclosed background islands inside the silhouette, per pose and view. Returns [(pose, view, n, (x, y))]."""
    from scipy import ndimage
    key = (255, 0, 255); out = []
    for pn, pose in poses:
        for yaw, pitch in views:
            im = np.array(geo.render(spec, tex, yaw, pitch, size, pose=pose, hidden=hidden, bg=key)[0].convert("RGB"))
            bgm = (im[:, :, 0] == 255) & (im[:, :, 1] == 0) & (im[:, :, 2] == 255)
            lab, n = ndimage.label(bgm)
            if n <= 1: continue
            sizes = ndimage.sum(bgm, lab, range(1, n + 1))
            edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
            holes = [i + 1 for i, s in enumerate(sizes) if s <= max_area and (i + 1) not in edge]
            if holes:
                ys, xs = np.nonzero(np.isin(lab, holes))
                out.append((pn, (yaw, pitch), len(holes), (int(xs[0]), int(ys[0]))))
    return out
