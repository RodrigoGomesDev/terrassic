"""Previews of the Daspletosaurus for the author (art/daspletosaurus/previews): side, 3/4, front, head, male vs
female, next to the T. rex at the same pixel scale (both at their in-game sizes), and the measured numbers.

usage:  python3 -B tools/modelgen/handmade/daspletosaurus/preview.py [out_dir] [--quick]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "_engine")
sys.path[:0] = [HERE, ENGINE, os.path.join(ENGINE, "plans")]
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
import geo  # noqa: E402
import proto as P  # noqa: E402
import shots  # noqa: E402
import skin2  # noqa: E402
import dasple  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")


def model(saddle_on):
    m = dasple.build(saddle_on=saddle_on)
    P.pack(m, dasple.TEX_W)
    return m


def spec_tex(m, sex, out):
    gp = os.path.join(out, "_tmp.geo.json")
    dasple.preview_faces(m)
    json.dump(P.geo_json(m), open(gp, "w"))
    tex = dasple.paint_sex(m, sex)
    return geo.load_geo(gp), tex


def side_by_side(images, gap=24, bg=shots.BG):
    h = max(i.height for i in images)
    w = sum(i.width for i in images) + gap * (len(images) - 1)
    out = Image.new("RGB", (w, h), bg)
    x = 0
    for i in images:
        out.paste(i, (x, h - i.height)); x += i.width + gap
    return out


def next_to_rex(spec, tex, out, px=3):
    """both rigs rendered side-on at their in-game scale (MODEL_SCALE x METRE), px screen pixels per game pixel"""
    rex_geo = geo.load_geo(os.path.join(ASSETS, "geo", "entity", "tyrannosaurus.geo.json"))
    rex_tex = Image.open(os.path.join(ASSETS, "textures", "entity", "tyrannosaurus_male.png"))
    sizes = {"tyrannosaurus": 1.02 * skin2.METRE, "daspletosaurus": SCALE[0]}
    shots_ = []
    for name, (sp, tx) in (("tyrannosaurus", (rex_geo, rex_tex)), ("daspletosaurus", (spec, tex))):
        pts = np.concatenate([q for c, q in geo.cube_points(sp)])
        L = pts[:, 2].max() - pts[:, 2].min(); Hh = pts[:, 1].max() - pts[:, 1].min()
        k = sizes[name] * px
        im = geo.render(sp, tx, 90, 0, (int(L * k * 1.04) + 8, int(Hh * k * 1.04) + 8), bg=shots.BG, margin=0.02)[0].convert("RGB")
        shots_.append(im)
    side_by_side(shots_, gap=40).save(os.path.join(out, "ao_lado_do_trex.png"))


SCALE = [1.0]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(ROOT, "art", "daspletosaurus", "previews")
    quick = "--quick" in sys.argv
    os.makedirs(out, exist_ok=True)
    m = model(saddle_on=False)
    spec, tex = spec_tex(m, "male", out)
    tex.save(os.path.join(out, "pele_macho.png"))
    pts = np.concatenate([q for c, q in geo.cube_points(spec) if c.get("name", "").split("#")[0]])
    L = float(pts[:, 2].max() - pts[:, 2].min())
    SCALE[0] = 9.5 * skin2.METRE * 16.0 / L
    print(f"length {L:.1f} px, model scale {SCALE[0]:.3f}, density {skin2.density(L, 9.5):.1f} tx/block, "
          f"height {pts[:, 1].max():.1f} px, colours {skin2.colour_count(tex)}")
    shots.shot(spec, tex, 90, 0, (1400, 620)).save(os.path.join(out, "lateral.png"))
    shots.shot(spec, tex, 35, 18, (1200, 800)).save(os.path.join(out, "tres_quartos.png"))
    shots.shot(spec, tex, 62, 12, (900, 600), bones=("head", "skull", "jaw")).save(os.path.join(out, "cabeca.png"))
    if quick:
        return
    shots.shot(spec, tex, 0, 8, (800, 700)).save(os.path.join(out, "frente.png"))
    shots.shot(spec, tex, 300, 22, (1200, 760)).save(os.path.join(out, "traseira.png"))
    shots.shot(spec, tex, 0, 4, (700, 600), bones=("head", "skull", "jaw")).save(os.path.join(out, "cabeca_frente.png"))
    fspec, ftex = spec_tex(model(saddle_on=False), "female", out)
    ftex.save(os.path.join(out, "pele_femea.png"))
    side_by_side([shots.shot(spec, tex, 35, 18, (1000, 680)), shots.shot(fspec, ftex, 35, 18, (1000, 680))]).save(
        os.path.join(out, "macho_e_femea.png"))
    side_by_side([shots.shot(spec, tex, 62, 12, (700, 480), bones=("head", "skull", "jaw")),
                  shots.shot(fspec, ftex, 62, 12, (700, 480), bones=("head", "skull", "jaw"))]).save(
        os.path.join(out, "cabeca_macho_e_femea.png"))
    sspec, stex = spec_tex(model(saddle_on=True), "male", out)
    shots.shot(sspec, stex, 35, 18, (1200, 800)).save(os.path.join(out, "com_sela.png"))
    next_to_rex(spec, tex, out)
    os.remove(os.path.join(out, "_tmp.geo.json"))


if __name__ == "__main__":
    main()
