"""Previews of the Thescelosaurus v4 for the author: side, 3/4, front, back, head (male and female, side and 3/4), the
calf (its own skin, the spots bolder); with --gifs, its animations from the exported files.

usage:  python3 -B tools/modelgen/handmade/thescelosaurus/preview.py [out_dir] [--quick] [--gifs [names...]]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "_engine")
sys.path[:0] = [HERE, ENGINE]
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
import geo  # noqa: E402
import proto as P  # noqa: E402
import shots  # noqa: E402
import skin2  # noqa: E402
import thes  # noqa: E402

ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
HEAD = ("head", "skull", "jaw", "cheek_l", "cheek_r", "male_display", "female_display")


def model():
    m = thes.build()
    P.pack(m, thes.TEX_W)
    return m


def spec_tex(m, sex, out):
    gp = os.path.join(out, "_tmp.geo.json")
    thes.preview_faces(m)
    tex = thes.paint_sex(m, sex)
    hide = "female_display" if sex == "male" else "male_display"
    m.cubes = [c for c in m.cubes if c["bone"] != hide]
    json.dump(P.geo_json(m), open(gp, "w"))
    return geo.load_geo(gp), tex


def side_by_side(images, gap=24, bg=shots.BG):
    h = max(i.height for i in images)
    w = sum(i.width for i in images) + gap * (len(images) - 1)
    out = Image.new("RGB", (w, h), bg)
    x = 0
    for i in images:
        out.paste(i, (x, h - i.height)); x += i.width + gap
    return out


GIFS = ("walk", "run", "freeze", "bolt", "idle", "sniff_ground", "sniff_air", "burrow_dig", "burrow_sleep", "hide",
        "peek", "dig", "kick", "tail_flag", "attack", "graze", "sleep", "hatch")


def gifs(out, names=None, sex="male"):
    from jsongif import pose_at, load_anims
    spec = geo.load_geo(os.path.join(ASSETS, "geo", "entity", "thescelosaurus.geo.json"))
    spec = {**spec, "cubes": [c for c in spec["cubes"] if c["bone"] != "female_display"]}
    tex = Image.open(os.path.join(ASSETS, "textures", "entity", f"thescelosaurus_{sex}.png"))
    btex = Image.open(os.path.join(ASSETS, "textures", "entity", "thescelosaurus_baby.png"))
    A = load_anims(os.path.join(ASSETS, "animations", "entity", "thescelosaurus.animation.json"))
    gdir = os.path.join(out, "animacoes"); os.makedirs(gdir, exist_ok=True)
    for n in names or GIFS:
        key = f"animation.thescelosaurus.{n}"
        if key not in A:
            print("no", n); continue
        tx = btex if n == "hatch" else tex
        an = A[key]; L = an["animation_length"]
        fps = 15; N = max(2, int(round(L * fps)))
        poses = [pose_at(an, L * i / N) for i in range(N + (0 if an.get("loop") else 1))]
        yaw, pitch = (62, 10)
        fits = [geo.render(spec, tx, yaw, pitch, (64, 48), pose=p)[1] for p in poses[::max(1, len(poses) // 10)]]
        fit = (min(f[0] for f in fits), max(f[1] for f in fits), min(f[2] for f in fits), max(f[3] for f in fits))
        ims = [geo.render(spec, tx, yaw, pitch, (560, 380), pose=p, fit=fit, bg=shots.BG, margin=0.06)[0].convert("RGB")
               for p in poses]
        ims[0].save(os.path.join(gdir, f"{n}.gif"), save_all=True, append_images=ims[1:], duration=int(1000 / fps), loop=0)
        pick = [ims[int(i * (len(ims) - 1) / 5)] for i in range(6)]
        side_by_side([i.resize((280, 190), Image.LANCZOS) for i in pick], gap=4).save(os.path.join(gdir, f"{n}_quadros.png"))
        print("gif", n, len(ims), flush=True)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else os.path.join(ROOT, "art", "thescelosaurus", "previews")
    os.makedirs(out, exist_ok=True)
    if "--gifs" in sys.argv:
        gifs(out, args[1:] or None)
        return
    m = model()
    spec, tex = spec_tex(m, "male", out)
    tex.save(os.path.join(out, "pele_macho.png"))
    pts = np.concatenate([q for c, q in geo.cube_points(spec)])
    L = float(pts[:, 2].max() - pts[:, 2].min())
    print(f"length {L:.1f} px, density {skin2.density(L, thes.REAL_M):.1f} tx/block, height {pts[:, 1].max():.1f} px, "
          f"colours {skin2.colour_count(tex)}")
    shots.shot(spec, tex, 90, 0, (1400, 760)).save(os.path.join(out, "lateral.png"))
    shots.shot(spec, tex, 35, 18, (1200, 860)).save(os.path.join(out, "tres_quartos.png"))
    shots.shot(spec, tex, 62, 12, (900, 600), bones=HEAD).save(os.path.join(out, "cabeca.png"))
    shots.shot(spec, tex, 90, 0, (900, 600), bones=HEAD).save(os.path.join(out, "cabeca_perfil.png"))
    if "--quick" in sys.argv:
        os.remove(os.path.join(out, "_tmp.geo.json"))
        return
    shots.shot(spec, tex, 0, 8, (800, 760)).save(os.path.join(out, "frente.png"))
    shots.shot(spec, tex, 300, 22, (1200, 860)).save(os.path.join(out, "traseira.png"))
    shots.shot(spec, tex, 0, 4, (700, 600), bones=HEAD).save(os.path.join(out, "cabeca_frente.png"))
    fspec, ftex = spec_tex(model(), "female", out)
    ftex.save(os.path.join(out, "pele_femea.png"))
    side_by_side([shots.shot(spec, tex, 35, 18, (1000, 720)), shots.shot(fspec, ftex, 35, 18, (1000, 720))]).save(
        os.path.join(out, "macho_e_femea.png"))
    side_by_side([shots.shot(spec, tex, 62, 12, (700, 480), bones=HEAD),
                  shots.shot(fspec, ftex, 62, 12, (700, 480), bones=HEAD)]).save(os.path.join(out, "cabeca_macho_e_femea.png"))
    side_by_side([shots.shot(spec, tex, 90, 0, (700, 480), bones=HEAD),
                  shots.shot(fspec, ftex, 90, 0, (700, 480), bones=HEAD)]).save(os.path.join(out, "cabeca_perfil_macho_e_femea.png"))
    cspec, ctex = spec_tex(model(), "baby", out)
    ctex.save(os.path.join(out, "pele_filhote.png"))
    shots.shot(cspec, ctex, 35, 18, (1000, 720)).save(os.path.join(out, "filhote.png"))
    os.remove(os.path.join(out, "_tmp.geo.json"))


if __name__ == "__main__":
    main()
