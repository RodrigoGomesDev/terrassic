"""Previews of the Albertosaurus for the author (art/albertosaurus/previews): side, 3/4, front, head, male vs
female, next to the Daspletosaurus and the T. rex at the same pixel scale (all at their in-game sizes), and the
measured numbers.

usage:  python3 -B tools/modelgen/handmade/albertosaurus/preview.py [out_dir] [--quick] [--gifs]
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
import alberto  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")


def model(saddle_on):
    m = alberto.build(saddle_on=saddle_on)
    P.pack(m, alberto.TEX_W)
    return m


def spec_tex(m, sex, out):
    gp = os.path.join(out, "_tmp.geo.json")
    alberto.preview_faces(m)
    json.dump(P.geo_json(m), open(gp, "w"))
    tex = alberto.paint_sex(m, sex)
    return geo.load_geo(gp), tex


def side_by_side(images, gap=24, bg=shots.BG):
    h = max(i.height for i in images)
    w = sum(i.width for i in images) + gap * (len(images) - 1)
    out = Image.new("RGB", (w, h), bg)
    x = 0
    for i in images:
        out.paste(i, (x, h - i.height)); x += i.width + gap
    return out


def next_to_kin(spec, tex, out, px=3):
    """the three rigs rendered side-on at their in-game scale (MODEL_SCALE x METRE), px screen pixels per game pixel:
    the Albertosaurus, the Daspletosaurus and the T. rex"""
    shots_ = []
    sizes = {"tyrannosaurus": 1.02 * skin2.METRE, "daspletosaurus": 0.981, "albertosaurus": SCALE[0]}
    for name in ("albertosaurus", "daspletosaurus", "tyrannosaurus"):
        if name == "albertosaurus":
            sp, tx = spec, tex
        else:
            sp = geo.load_geo(os.path.join(ASSETS, "geo", "entity", f"{name}.geo.json"))
            tx = Image.open(os.path.join(ASSETS, "textures", "entity", f"{name}_male.png"))
            sp = {**sp, "cubes": [c for c in sp["cubes"] if c.get("bone") != "saddle"]}
        pts = np.concatenate([q for c, q in geo.cube_points(sp)])
        L = pts[:, 2].max() - pts[:, 2].min(); Hh = pts[:, 1].max() - pts[:, 1].min()
        k = sizes[name] * px
        im = geo.render(sp, tx, 90, 0, (int(L * k * 1.04) + 8, int(Hh * k * 1.04) + 8), bg=shots.BG, margin=0.02)[0].convert("RGB")
        shots_.append(im)
    side_by_side(shots_, gap=40).save(os.path.join(out, "ao_lado_do_daspleto_e_trex.png"))


SCALE = [1.0]
GIFS = ("walk", "run", "sprint", "drive", "idle", "attack", "snap_bite", "pass_bite", "parry", "sidestep", "lunge",
        "call_pack", "answer", "ambush_crouch", "pant", "eat")


def gifs(out, sex="male"):
    """GIFs straight from the exported files (what GeckoLib plays), with a strip of frames of each"""
    from jsongif import pose_at, load_anims
    spec = geo.load_geo(os.path.join(ASSETS, "geo", "entity", "albertosaurus.geo.json"))
    tex = Image.open(os.path.join(ASSETS, "textures", "entity", f"albertosaurus_{sex}.png"))
    A = load_anims(os.path.join(ASSETS, "animations", "entity", "albertosaurus.animation.json"))
    hid = [c["name"] for c in spec["cubes"] if c["bone"] == "saddle"]
    gdir = os.path.join(out, "animacoes"); os.makedirs(gdir, exist_ok=True)
    for n in GIFS:
        an = A[f"animation.albertosaurus.{n}"]; L = an["animation_length"]
        fps = 12; N = max(2, int(round(L * fps)))
        poses = [pose_at(an, L * i / N) for i in range(N + (0 if an.get("loop") else 1))]
        yaw, pitch = (60, 12)
        fits = [geo.render(spec, tex, yaw, pitch, (64, 48), pose=p, hidden=hid)[1] for p in poses[::max(1, len(poses) // 8)]]
        fit = (min(f[0] for f in fits), max(f[1] for f in fits), min(f[2] for f in fits), max(f[3] for f in fits))
        ims = [geo.render(spec, tex, yaw, pitch, (560, 380), pose=p, hidden=hid, fit=fit, bg=shots.BG, margin=0.06)[0].convert("RGB")
               for p in poses]
        ims[0].save(os.path.join(gdir, f"{n}.gif"), save_all=True, append_images=ims[1:], duration=int(1000 / fps), loop=0)
        pick = [ims[int(i * (len(ims) - 1) / 4)] for i in range(5)]
        strip = side_by_side([i.resize((280, 190), Image.LANCZOS) for i in pick], gap=4)
        strip.save(os.path.join(gdir, f"{n}_quadros.png"))
        print("gif", n, len(ims), flush=True)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(ROOT, "art", "albertosaurus", "previews")
    quick = "--quick" in sys.argv
    os.makedirs(out, exist_ok=True)
    m = model(saddle_on=False)
    spec, tex = spec_tex(m, "male", out)
    tex.save(os.path.join(out, "pele_macho.png"))
    pts = np.concatenate([q for c, q in geo.cube_points(spec) if c.get("name", "").split("#")[0]])
    L = float(pts[:, 2].max() - pts[:, 2].min())
    SCALE[0] = 10.0 * skin2.METRE * 16.0 / L
    print(f"length {L:.1f} px, model scale {SCALE[0]:.3f}, density {skin2.density(L, 10.0):.1f} tx/block, "
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
    next_to_kin(spec, tex, out)
    os.remove(os.path.join(out, "_tmp.geo.json"))
    if "--gifs" in sys.argv:
        gifs(out)


if __name__ == "__main__":
    main()
