"""The uniqueness check of the "padrão v3" (docs/estudos/14_POR_QUE_PARECE_IA.md, section "Padrão v3", 08/11/2026).

The v2 heads passed every number of headcheck.py and still read "copia e cola" (Rodrigo): one shared ready-made eye,
one tooth row, one face speckle and one mouth, only the hue changed. This check compares the heads of every remade
species pair by pair, on the files the game loads (the exported geo.json and the male texture), in three parts:

1. EYE: the drawn eye cut out of the texture (the glint, the iris and the pupil and one texel round them), read as a
   map of classes (glint, pupil, iris, dark rim, skin) and compared by overlap (Dice) at the best small shift, either
   way round, times how close the iris hues are;
2. TEETH: the row seen from the side with the mouth shut (rendered from the geo, the tooth colours marked), read as a
   sequence of teeth and gaps in texels: tooth width, gap, length, the longest against the mean, the spread of the
   lengths and of the gaps, the teeth per texel of row;
3. FACE: the side faces of the head (minus eye, teeth and mouth), read as texture statistics: neighbours that change,
   their orientation (along or across the head), the mean size of a blob of one tone, the size of a tone step, and
   the share of texels above and below the face's middle tone.

Each part is a similarity in 0..1 (1 = the same); the pair's similarity is their mean. A NEW species fails when it is
at THRESHOLD or above against any other remade species (the old remakes are the references of what "its own" means).

usage from a build.py:    fails, rows = uniquecheck.check("majungasaurus"); print(uniquecheck.table(rows))
standalone:               python3 -B uniquecheck.py [species ...]       (the full table; no args = all remakes)
"""
import colorsys
import importlib.util
import itertools
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geo  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
HAND = os.path.join(HERE, "..")

# the remade species with a head (Eras.REMADE) and the file that holds their palette
SPECIES = {
    "tyrannosaurus": "tyrannosaurus/rex2.py", "carnotaurus": "carnotaurus/carno.py",
    "giganotosaurus": "giganotosaurus/giga.py", "protoceratops": "protoceratops/protocera.py",
    "spinosaurus": "spinosaurus/spino.py", "velociraptor": "velociraptor/raptor.py",
    "pteranodon": "pteranodon/ptera.py", "triceratops": "triceratops/tricera.py",
    "gallimimus": "gallimimus/galli.py", "pachycephalosaurus": "pachycephalosaurus/pachy.py",
    "parasaurolophus": "parasaurolophus/para.py", "ankylosaurus": "ankylosaurus/ankylo.py",
    "mosasaurus": "mosasaurus/mosa.py", "styracosaurus": "styracosaurus/styraco.py",
    "deinosuchus": "deinosuchus/deino.py", "elasmosaurus": "elasmosaurus/elasmo.py",
    "therizinosaurus": "therizinosaurus/theri.py", "quetzalcoatlus": "quetzalcoatlus/quetz.py",
    "edmontosaurus": "edmontosaurus/edmonto.py", "dakotaraptor": "dakotaraptor/dakota.py",
    "daspletosaurus": "daspletosaurus/dasple.py", "albertosaurus": "albertosaurus/alberto.py",
    "carcharodontosaurus": "carcharodontosaurus/carcharo.py", "majungasaurus": "majungasaurus/majunga.py",
}
# the heads compared: the remade predators, every one with an eye, a tooth row and a face (the herbivores share
# eye stamps among themselves - the ceratopsians one, the hadrosaurs and the ankylosaur another - and are left for
# their own pass; `python3 -B uniquecheck.py --all` prints them too)
HEADS = ("tyrannosaurus", "carnotaurus", "giganotosaurus", "spinosaurus", "velociraptor", "dakotaraptor",
         "mosasaurus", "deinosuchus", "daspletosaurus", "albertosaurus", "carcharodontosaurus", "majungasaurus")
# the species built to the padrão v3: the ones the check can fail (the others are references)
NEW = ("daspletosaurus", "albertosaurus", "carcharodontosaurus", "majungasaurus")
# calibrated on 08/11/2026 (study 14, "Padrão v3: resultados"): the old remakes against each other reach 0.73 at most
# (Giganotosaurus x Mosasaurus), the four v2 heads against each other 0.82 to 0.91
THRESHOLD = 0.78
IRIS_KEYS = ("iris", "iris2", "iris3", "eye", "eye2", "eye_hi", "eY", "eE", "ee")
MOUTH_KEYS = ("gum", "mouth", "mouth2", "tongue")


# ------------------------------------------------------------------ loading
def _hex(v):
    if isinstance(v, str):
        v = v.lstrip("#")
        return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))
    if isinstance(v, (tuple, list)) and len(v) >= 3 and all(isinstance(x, (int, np.integer)) for x in v[:3]):
        return tuple(int(x) for x in v[:3])
    return None


def palette(sp):
    """the RGB of glint, pupil, irises, teeth and mouth of a species, read from its module (pal_for or PAL + EYE)"""
    path = os.path.join(HAND, SPECIES[sp])
    folder = os.path.dirname(path)
    sys.path[:0] = [folder, HERE, os.path.join(HERE, "plans")]
    try:
        spec = importlib.util.spec_from_file_location(f"_uq_{sp}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        del sys.path[:3]
    p = {}
    for src in (getattr(mod, "PAL", None), getattr(mod, "EYE", None)):
        if isinstance(src, dict):
            p.update(src)
    if hasattr(mod, "pal_for"):
        try:
            p.update(mod.pal_for("male"))
        except TypeError:
            pass
    rgb = {k: _hex(v) for k, v in p.items() if _hex(v) is not None}
    return {"glint": rgb.get("glint"), "pupil": rgb.get("pupil"),
            "iris": [rgb[k] for k in IRIS_KEYS if k in rgb],
            "teeth": [v for k, v in rgb.items() if k.startswith("tooth")],
            "mouth": [rgb[k] for k in MOUTH_KEYS if k in rgb]}


def load(sp):
    spec = geo.load_geo(os.path.join(ASSETS, "geo", "entity", f"{sp}.geo.json"))
    tex = np.asarray(Image.open(os.path.join(ASSETS, "textures", "entity", f"{sp}_male.png")).convert("RGBA"))
    return spec, tex


def head_bones(spec):
    names = {b["name"] for b in spec["bones"]}
    head = {n for n in names if n in ("head", "skull", "jaw")}
    for _ in range(4):
        head |= {b["name"] for b in spec["bones"] if b.get("parent") in head}
    return head


def _rects(spec, bones, faces=None):
    out = set()
    for c in spec["cubes"]:
        if c["bone"] not in bones:
            continue
        for f, (u, v, w, h) in c["uv"].items():
            if faces and f not in faces:
                continue
            u0, u1 = sorted((int(round(u)), int(round(u + w)))); v0, v1 = sorted((int(round(v)), int(round(v + h))))
            if u1 > u0 and v1 > v0:
                out.add((u0, v0, u1, v1, f))
    return sorted(out)


def _sel(t, cols):
    m = np.zeros(t.shape[:2], bool)
    for c in cols:
        if c is not None:
            m |= np.all(t[..., :3] == np.array(c, np.uint8), axis=-1)
    return m & (t[..., 3] > 0)


LUM = np.array([0.299, 0.587, 0.114])


# ------------------------------------------------------------------ 1. the eye
def eye_crop(spec, tex, pal):
    """the class map of the drawn eye: 'g' glint, 'p' pupil, 'i' iris, 'd' dark rim, 's' skin; and the iris hue"""
    hb = head_bones(spec)
    side = _rects(spec, hb, ("east", "west", "north", "south"))
    head_m = np.zeros(tex.shape[:2], bool)
    for u0, v0, u1, v1, _f in side:
        head_m[v0:v1, u0:u1] = True
    head_m &= tex[..., 3] > 0
    gl = _sel(tex, [pal["glint"]]) & head_m
    ir = _sel(tex, pal["iris"]) & head_m
    pu = _sel(tex, [pal["pupil"]]) & head_m
    best = None
    for y, x in zip(*np.nonzero(gl)):
        rect = next(((u0, v0, u1, v1) for u0, v0, u1, v1, _f in side if u0 <= x < u1 and v0 <= y < v1), None)
        if rect is None:
            continue
        u0, v0, u1, v1 = rect
        y0, y1, x0, x1 = max(v0, y - 4), min(v1, y + 5), max(u0, x - 4), min(u1, x + 5)
        n = int(ir[y0:y1, x0:x1].sum() + pu[y0:y1, x0:x1].sum())
        if best is None or n > best[0]:
            best = (n, (y0, y1, x0, x1), rect)
    if best is None or best[0] == 0:
        return None
    (y0, y1, x0, x1), (u0, v0, u1, v1) = best[1], best[2]
    eye = (gl | ir | pu)[y0:y1, x0:x1]
    ys, xs = np.nonzero(eye)
    cy0, cy1 = max(v0, y0 + ys.min() - 1), min(v1, y0 + ys.max() + 2)
    cx0, cx1 = max(u0, x0 + xs.min() - 1), min(u1, x0 + xs.max() + 2)
    lum = tex[..., :3].astype(float) @ LUM
    med = float(np.median(lum[head_m]))
    cls = np.full((cy1 - cy0, cx1 - cx0), "s")
    sub = (slice(cy0, cy1), slice(cx0, cx1))
    cls[lum[sub] < 0.5 * med] = "d"
    cls[ir[sub]] = "i"
    cls[pu[sub]] = "p"
    cls[gl[sub]] = "g"
    irs = tex[sub][ir[sub]][:, :3]
    hue = colorsys.rgb_to_hsv(*(irs.mean(0) / 255.0))[0] if len(irs) else None
    return {"cls": cls, "hue": hue, "box": (cx0, cy0, cx1, cy1)}


def eye_sim(a, b):
    if a is None or b is None:
        return None
    A = a["cls"]
    best = 0.0
    for B in (b["cls"], b["cls"][:, ::-1]):
        H = max(A.shape[0], B.shape[0]) + 4; W = max(A.shape[1], B.shape[1]) + 4
        ca = np.full((H, W), "s"); ca[2:2 + A.shape[0], 2:2 + A.shape[1]] = A
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                cb = np.full((H, W), "s")
                y, x = 2 + dy, 2 + dx
                if y < 0 or x < 0 or y + B.shape[0] > H or x + B.shape[1] > W:
                    continue
                cb[y:y + B.shape[0], x:x + B.shape[1]] = B
                na, nb = ca != "s", cb != "s"
                same = (ca == cb) & na
                d = 2.0 * same.sum() / max(1, na.sum() + nb.sum())
                best = max(best, d)
    dh = 1.0
    if a["hue"] is not None and b["hue"] is not None:
        h = abs(a["hue"] - b["hue"]); h = min(h, 1 - h) * 360.0
        dh = max(0.0, 1.0 - h / 90.0)            # a quarter turn of hue apart = nothing shared
    return best * (0.75 + 0.25 * dh)


# ------------------------------------------------------------------ 2. the teeth
def teeth_row(spec, tex, pal):
    """the visible tooth row from the animal's left at rest, as a list of column lengths in texels (0 = a gap)"""
    hb = head_bones(spec)
    head_m = np.zeros(tex.shape[:2], bool)
    for u0, v0, u1, v1, _f in _rects(spec, hb):
        head_m[v0:v1, u0:u1] = True
    tm = _sel(tex, pal["teeth"]) & head_m
    if not tm.any():
        return None
    probe = np.zeros_like(tex)
    probe[..., :3] = 128
    probe[..., 3] = tex[..., 3]
    probe[tm, :3] = (255, 0, 0)
    import shots
    hidden = tuple(b["name"] for b in spec["bones"] if b["name"] == "saddle")
    fit = shots.fit_of(spec, hb, 90, 0)
    img, _fit, sc = geo.render(spec, Image.fromarray(probe, "RGBA"), 90, 0, (1200, 800), fit=fit, hidden=hidden,
                               bg=(128, 128, 128), margin=0.04)
    a = np.asarray(img.convert("RGB")).astype(int)
    hit = (a[..., 0] > 60) & (a[..., 1] < 20) & (a[..., 2] < 20)
    if not hit.any():
        return None
    xs = np.nonzero(hit.any(0))[0]
    x0, x1 = xs.min(), xs.max() + 1
    per = hit[:, x0:x1].sum(0) / sc                       # texels of tooth in each screen column
    n = max(1, int(round((x1 - x0) / sc)))
    cols = [float(per[int(k * sc):max(int(k * sc) + 1, int((k + 1) * sc))].mean()) for k in range(n)]
    return [round(c * 2) / 2 for c in cols]


def teeth_feats(row):
    if not row:
        return None
    teeth, gaps, cur, gap = [], [], [], 0
    for c in row + [0]:
        if c >= 0.5:
            if cur == [] and gap and teeth:
                gaps.append(gap)
            cur.append(c); gap = 0
        else:
            if cur:
                teeth.append(cur); cur = []
            gap += 1
    if not teeth:
        return None
    L = np.array([max(t) for t in teeth]); W = np.array([len(t) for t in teeth]); G = np.array(gaps or [0])
    return {"n": len(teeth), "width": float(W.mean()), "gap": float(G.mean()), "len": float(L.mean()),
            "long": float(L.max() / max(L.mean(), 0.5)), "cv_len": float(L.std() / max(L.mean(), 0.5)),
            "cv_gap": float(G.std() / max(G.mean(), 0.5)), "per_tx": len(teeth) / max(1, len(row)),
            "taper": float(np.mean([(max(t) - min(t)) / max(t) for t in teeth if len(t) > 1]) if any(
                len(t) > 1 for t in teeth) else 0.0)}


TEETH_SCALE = {"width": 1.0, "gap": 1.0, "len": 1.0, "long": 0.5, "cv_len": 0.25, "cv_gap": 0.4, "per_tx": 0.12,
               "taper": 0.25}


def _feat_sim(a, b, scale):
    if a is None or b is None:
        return None
    d = [min(1.0, abs(a[k] - b[k]) / s) for k, s in scale.items()]
    return 1.0 - float(np.mean(d))


# ------------------------------------------------------------------ 3. the face
def face_feats(spec, tex, pal, eye):
    hb = head_bones(spec)
    lum = tex[..., :3].astype(float) @ LUM
    not_skin = _sel(tex, pal["teeth"] + pal["mouth"] + pal["iris"] + [pal["glint"], pal["pupil"]])
    if eye is not None:
        x0, y0, x1, y1 = eye["box"]
        not_skin[y0:y1, x0:x1] = True
    ch_h = ch_v = n_h = n_v = 0
    blobs = steps = 0.0
    nblob = npx = 0
    up = down = 0
    for u0, v0, u1, v1, f in _rects(spec, hb, ("east", "west")):
        if (u1 - u0) * (v1 - v0) < 12:
            continue
        sub = tex[v0:v1, u0:u1]
        ok = (sub[..., 3] > 0) & ~not_skin[v0:v1, u0:u1]
        if ok.sum() < 8:
            continue
        rgb = sub[..., :3].astype(int)
        dh = np.abs(np.diff(rgb, axis=1)).sum(2) > 12; okh = ok[:, 1:] & ok[:, :-1]
        dv = np.abs(np.diff(rgb, axis=0)).sum(2) > 12; okv = ok[1:, :] & ok[:-1, :]
        ch_h += int((dh & okh).sum()); n_h += int(okh.sum())
        ch_v += int((dv & okv).sum()); n_v += int(okv.sum())
        L = lum[v0:v1, u0:u1]
        dl = np.abs(np.diff(L, axis=1))[dh & okh]
        steps += float(dl.sum())
        med = float(np.median(L[ok]))
        up += int((L[ok] > med + 6).sum()); down += int((L[ok] < med - 6).sum())
        # blobs of one tone (4-connected, same RGB)
        seen = np.zeros(ok.shape, bool)
        key = rgb[..., 0] * 65536 + rgb[..., 1] * 256 + rgb[..., 2]
        for y, x in zip(*np.nonzero(ok)):
            if seen[y, x]:
                continue
            stack = [(y, x)]; seen[y, x] = True; size = 0
            while stack:
                cy, cx = stack.pop(); size += 1
                for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                    if 0 <= ny < ok.shape[0] and 0 <= nx < ok.shape[1] and ok[ny, nx] and not seen[ny, nx] \
                            and key[ny, nx] == key[cy, cx]:
                        seen[ny, nx] = True; stack.append((ny, nx))
            nblob += 1; blobs += size
        npx += int(ok.sum())
    if not npx:
        return None
    hch, vch = ch_h / max(1, n_h), ch_v / max(1, n_v)
    return {"change": (hch + vch) / 2, "orient": hch / max(1e-6, hch + vch), "blob": blobs / max(1, nblob),
            "step": steps / max(1, ch_h), "light": up / npx, "dark": down / npx}


FACE_SCALE = {"change": 0.20, "orient": 0.15, "blob": 3.0, "step": 14.0, "light": 0.25, "dark": 0.25}


# ------------------------------------------------------------------ the check
def measure(sp):
    spec, tex = load(sp)
    pal = palette(sp)
    eye = eye_crop(spec, tex, pal)
    row = teeth_row(spec, tex, pal)
    return {"eye": eye, "row": row, "teeth": teeth_feats(row), "face": face_feats(spec, tex, pal, eye)}


def compare(a, b):
    parts = {"eye": eye_sim(a["eye"], b["eye"]), "teeth": _feat_sim(a["teeth"], b["teeth"], TEETH_SCALE),
             "face": _feat_sim(a["face"], b["face"], FACE_SCALE)}
    have = [v for v in parts.values() if v is not None]
    parts["all"] = float(np.mean(have)) if have else 0.0
    return parts


def check(species, others=None, cache=None):
    """(failures, rows) for one NEW species against every other remade species with a head"""
    others = others or [s for s in HEADS if s != species]
    cache = cache if cache is not None else {}
    for s in [species] + list(others):
        if s not in cache:
            try:
                cache[s] = measure(s)
            except (FileNotFoundError, OSError):
                cache[s] = None
    rows, fails = [], []
    for o in others:
        if cache.get(o) is None or cache.get(species) is None:
            continue
        r = compare(cache[species], cache[o])
        rows.append((species, o, r))
        if r["all"] >= THRESHOLD:
            fails.append(f"uniquecheck: {species} too close to {o}: {r['all']:.2f} >= {THRESHOLD} "
                         f"(eye {_f(r['eye'])}, teeth {_f(r['teeth'])}, face {_f(r['face'])})")
    return fails, rows


def _f(v):
    return "  -  " if v is None else f"{v:.2f}"


def table(rows, top=None):
    rows = sorted(rows, key=lambda r: -r[2]["all"])[:top]
    out = [f"{'pair':44s}  eye   teeth face  | all"]
    for a, b, r in rows:
        mark = " FAIL" if r["all"] >= THRESHOLD else ""
        out.append(f"{a + ' x ' + b:44s} {_f(r['eye'])} {_f(r['teeth'])} {_f(r['face'])} | {r['all']:.2f}{mark}")
    return "\n".join(out)


def all_pairs(names):
    cache = {s: measure(s) for s in names}
    return [(a, b, compare(cache[a], cache[b])) for a, b in itertools.combinations(names, 2)], cache


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    names = args or (list(SPECIES) if "--all" in sys.argv else list(HEADS))
    rows, cache = all_pairs(names)
    for s in names:
        m = cache[s]
        t = m["teeth"]
        print(f"{s:20s} eye {None if m['eye'] is None else m['eye']['cls'].shape} "
              f"teeth {None if t is None else {k: round(v, 2) for k, v in t.items()}}")
        print(f"{'':20s} face {None if m['face'] is None else {k: round(v, 2) for k, v in m['face'].items()}}")
    print(table(rows))
