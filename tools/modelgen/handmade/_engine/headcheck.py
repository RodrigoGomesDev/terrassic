"""The head check of the "padrão v2" (docs/estudos/14_POR_QUE_PARECE_IA.md, section "Padrão v2", 08/11/2026).

The v1 standard fixed the pixel and the body-space skin but carried the calm base into the head, and the heads read
"simplório" next to the old remakes. The v2 numbers, measured on the texture texels painted on each region's cubes
(head = the bones head, skull and jaw and their children; body = the bones body*, neck*, tail*, chest*):

- head "neighbours change" (share of horizontally adjacent texels whose RGB differs by more than 12) >= 0.24 (the
  Carnotaurus) and >= 1.3x the body's; the body between 0.20 and 0.30 (calm but scaled at one tone step);
- TEETH: seen from the side at rest (mouth shut) a row of tooth texels shows below the lip line;
- EYE: an iris of >= 2 texels and a glint, both visible from the side, inside a dark rim (the socket);
- ACCENT (the male): a few texels of display skin with saturation >= 0.45 on the head (not the mouth, the teeth or
  the iris), bright enough (HSV value >= 0.40) and >= 20 degrees of hue away from the face's own colour.

usage from a build.py:   fails = headcheck.check(m, tex, p["iris"], p["glint"], sex=sex); print(headcheck.line(...))
standalone (any exported species):  python3 -B headcheck.py carnotaurus majungasaurus ...   (numbers only)
"""
import colorsys
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geo  # noqa: E402

HEAD_MIN = 0.24          # the Carnotaurus' head
HEAD_OVER_BODY = 1.3
BODY_RANGE = (0.20, 0.30)
TEETH_MIN = 5            # tooth texels visible from the side with the mouth shut (one side): a row of 3 or more
ACCENT_SAT = 0.45
ACCENT_MIN = 4           # texels
ACCENT_VAL = 0.40        # HSV value: bright enough to read as a colour
ACCENT_HUE = 20.0        # degrees away from the face's median hue
NOT_SKIN = ("teeth", "teeth_lo", "mouth", "tongue", "gular", "claw")


def head_bones(spec):
    names = {b["name"] for b in spec["bones"]}
    head = {n for n in names if n in ("head", "skull", "jaw")}
    head |= {b["name"] for b in spec["bones"] if b.get("parent") in head}
    return head


def body_bones(spec):
    return {b["name"] for b in spec["bones"] if b["name"].startswith(("body", "neck", "tail", "chest"))}


def _mask(spec, shape, cubes, skip=lambda c, f: False):
    m = np.zeros(shape, bool)
    for c in cubes:
        for f, (u, v, w, h) in c["uv"].items():
            if skip(c, f):
                continue
            u0, u1 = sorted((int(u), int(u + w))); v0, v1 = sorted((int(v), int(v + h)))
            m[v0:v1, u0:u1] = True
    return m


def region(spec, tex, bones):
    """(colours, neighbours change, value range p5..p95) of the texels painted on the cubes of these bones"""
    t = np.asarray(tex.convert("RGBA"))
    m = _mask(spec, t.shape[:2], [c for c in spec["cubes"] if c["bone"] in bones])
    px = t[m & (t[..., 3] > 0)][:, :3]
    sub = t[..., :3].astype(int)
    ch = (np.abs(np.diff(sub, axis=1)).sum(2) > 12)[m[:, 1:] & m[:, :-1]]
    lum = px @ [0.299, 0.587, 0.114]
    return len({tuple(p) for p in px}), float(ch.mean()), float(np.percentile(lum, 95) - np.percentile(lum, 5))


def _side_marks(spec, tex, marks, bones, yaw=90):
    """render the head from one side at rest with every texel grey except the marked ones; returns visible texels of
    each mark (screen pixels / scale^2: at rest one texel is one model pixel on a side face)"""
    t = np.asarray(tex.convert("RGBA")).copy()
    probe = np.zeros_like(t)
    probe[..., :3] = 128
    probe[..., 3] = t[..., 3]
    keys = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255)]
    for k, sel in enumerate(marks):
        probe[sel & (t[..., 3] > 0), :3] = keys[k]
    hidden = tuple(b["name"] for b in spec["bones"] if b["name"] == "saddle")
    import shots
    fit = shots.fit_of(spec, bones, yaw, 0)
    img, _fit, sc = geo.render(spec, Image.fromarray(probe, "RGBA"), yaw, 0, (900, 600), fit=fit, hidden=hidden,
                               bg=(128, 128, 128), margin=0.04)
    a = np.asarray(img.convert("RGB")).astype(int)
    out = []
    for k in range(len(marks)):
        kk = np.array(keys[k])
        on = (kk > 0)
        # shaded by the face light: the marked channels stay well above the others
        hit = np.all(a[..., on] > 60, axis=-1) & np.all(a[..., ~on] < 20, axis=-1) if (~on).any() else \
            np.all(a > 60, axis=-1)
        out.append(float(hit.sum()) / (sc * sc))
    return out


def _colour_sel(t, rgb):
    return np.all(t[..., :3] == np.array(rgb, np.uint8), axis=-1) & (t[..., 3] > 0)


def check(m, tex, iris, glint, sex="male", accent=True):
    """returns (failures, numbers). m: the proto.Model after P.pack (cubes keep their 'mat'); iris, glint: the RGB
    (or a list of RGBs for the iris) the eye decal uses"""
    spec = m.spec()
    t = np.asarray(tex.convert("RGBA"))
    hb, bb = head_bones(spec), body_bones(spec)
    hc, hn, hv = region(spec, tex, hb)
    bc, bn, bv = region(spec, tex, bb)
    head_cubes = [c for c in spec["cubes"] if c["bone"] in hb]
    head_m = _mask(spec, t.shape[:2], head_cubes)
    teeth_m = _mask(spec, t.shape[:2], [c for c in head_cubes if c.get("mat") == "teeth"])
    # the outer skin: not the mouth's own materials, nor the faces inside the mouth (the palate under the skull's
    # cubes, the floor on top of the jaw's)
    inner = lambda c, f: (f == "down" and c["bone"] != "jaw") or (f == "up" and c["bone"] == "jaw")
    skin_m = _mask(spec, t.shape[:2], [c for c in head_cubes if c.get("mat") not in NOT_SKIN], inner)
    irises = iris if isinstance(iris[0], (list, tuple)) else [iris]
    iris_m = np.zeros(t.shape[:2], bool)
    for i in irises:
        iris_m |= _colour_sel(t, i)
    iris_m &= head_m
    glint_m = _colour_sel(t, glint) & head_m
    iris_tx, glint_tx = int(iris_m.sum()), int(glint_m.sum())
    vis = {}
    for yaw, side in ((90, "east"), (270, "west")):
        vt, vi, vg = _side_marks(spec, tex, [teeth_m, iris_m, glint_m], hb, yaw)
        vis[side] = (vt, vi, vg)
    # the socket: the darkest texel in the ring around the eye decal is well under the head's median value
    lum = t[..., :3].astype(float) @ [0.299, 0.587, 0.114]
    eye = iris_m | glint_m
    ring = np.zeros_like(eye)
    ys, xs = np.nonzero(eye)
    for y, x in zip(ys, xs):
        ring[max(0, y - 1):y + 2, max(0, x - 1):x + 2] = True
    ring &= ~eye & head_m & (t[..., 3] > 0)
    med = float(np.median(lum[head_m & (t[..., 3] > 0)]))
    rim = float(lum[ring].min()) if ring.any() else 255.0
    # the accent: saturated display skin on the head (not the mouth, the teeth or the eye)
    hsv = np.array([colorsys.rgb_to_hsv(*(c / 255.0)) for c in t[..., :3].reshape(-1, 3)]).reshape(t.shape[:2] + (3,))
    # (darks are saturated in HSV by arithmetic: an accent is bright enough to read as a colour, and away from the
    # face's own hue, so a saturated body ramp does not count)
    solid = skin_m & (t[..., 3] > 0) & ~eye
    tinted = solid & (hsv[..., 1] > 0.15)
    hue0 = float(np.median(hsv[tinted][:, 0])) if tinted.any() else 0.0
    dh = np.abs(hsv[..., 0] - hue0); dh = np.minimum(dh, 1.0 - dh) * 360.0
    acc_m = solid & (hsv[..., 1] >= ACCENT_SAT) & (hsv[..., 2] >= ACCENT_VAL) & (dh >= ACCENT_HUE)
    acc = int(acc_m.sum())

    nums = {"head": (hc, round(hn, 3), round(hv)), "body": (bc, round(bn, 3), round(bv)),
            "ratio": round(hn / max(bn, 1e-6), 2), "teeth_visible": [round(vis[s][0], 1) for s in vis],
            "iris": iris_tx, "glint": glint_tx, "eye_visible": [round(vis[s][1] + vis[s][2], 1) for s in vis],
            "rim": round(rim), "head_median": round(med), "accent": acc}
    fails = []
    if hn < HEAD_MIN:
        fails.append(f"head neighbours change {hn:.2f} < {HEAD_MIN}")
    if hn < HEAD_OVER_BODY * bn:
        fails.append(f"head {hn:.2f} < {HEAD_OVER_BODY}x body {bn:.2f}")
    if not BODY_RANGE[0] <= bn <= BODY_RANGE[1]:
        fails.append(f"body neighbours change {bn:.2f} outside {BODY_RANGE}")
    for s in vis:
        if vis[s][0] < TEETH_MIN:
            fails.append(f"teeth: {vis[s][0]:.1f} texels visible on the {s} side with the mouth shut (< {TEETH_MIN})")
        if vis[s][1] < 1.5 or vis[s][2] < 0.5:
            fails.append(f"eye not visible on the {s} side (iris {vis[s][1]:.1f}, glint {vis[s][2]:.1f})")
    if iris_tx < 2 or glint_tx < 1:           # one decal per eye (the side faces share or mirror it)
        fails.append(f"eye: iris {iris_tx} texels, glint {glint_tx} (both sides)")
    if rim > 0.6 * med:
        fails.append(f"eye socket: darkest rim texel {rim:.0f} not under 0.6 x head median {med:.0f}")
    if accent and sex == "male" and acc < ACCENT_MIN:
        fails.append(f"accent: {acc} head texels with saturation >= {ACCENT_SAT} (< {ACCENT_MIN})")
    return fails, nums


def line(name, sex, nums):
    h, b = nums["head"], nums["body"]
    return (f"headcheck {name} {sex}: head {h[0]} colours, {h[1]:.2f} change, range {h[2]} | body {b[0]}, {b[1]:.2f},"
            f" {b[2]} | x{nums['ratio']} | teeth {nums['teeth_visible']} | iris {nums['iris']} glint {nums['glint']}"
            f" rim {nums['rim']}/{nums['head_median']} | accent {nums['accent']}")


if __name__ == "__main__":
    ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
    A = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
    for sp in sys.argv[1:]:
        spec = geo.load_geo(f"{A}/geo/entity/{sp}.geo.json")
        tex = Image.open(f"{A}/textures/entity/{sp}_male.png")
        hc, hn, hv = region(spec, tex, head_bones(spec))
        bc, bn, bv = region(spec, tex, body_bones(spec))
        print(f"{sp:20s} head: {hc:3d} colours, {hn:.2f} neighbours change, value range {hv:3.0f} | "
              f"body: {bc:3d}, {bn:.2f}, {bv:3.0f} | x{hn / max(bn, 1e-6):.2f}")
