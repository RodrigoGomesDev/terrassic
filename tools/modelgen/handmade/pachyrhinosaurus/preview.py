"""Previews of the Pachyrhinosaurus v4 for the author (art/pachyrhinosaurus/previews): side, 3/4, front, back, head,
male and female, the calf (its own skin, no boss and no hooks, only the brow), with the pack saddle, and next to the
remade ceratopsians it must not look like (Triceratops, Styracosaurus, Protoceratops) at their in-game sizes; with
--gifs, its own animations.

usage:  python3 -B tools/modelgen/handmade/pachyrhinosaurus/preview.py [out_dir] [--quick] [--gifs]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "_engine")
sys.path[:0] = [HERE, ENGINE, os.path.join(ENGINE, "plans"), os.path.join(HERE, "..", "_silhuetas")]
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
import geo  # noqa: E402
import proto as P  # noqa: E402
import shots  # noqa: E402
import skin2  # noqa: E402
import pachy  # noqa: E402

SCALE = [1.0]
ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
HOOKS = tuple(f"hook_{s}{k}" for s in "lr" for k in range(3))
ADULT = ("adult_boss", "adult_hooks", "male_display") + HOOKS
HEAD = ("head", "skull", "jaw", "young_brow", "frill", "female_display") + ADULT


def model(saddle_on):
    m = pachy.build(saddle_on=saddle_on)
    P.pack(m, pachy.TEX_W)
    return m


def spec_tex(m, sex, out, calf=False):
    gp = os.path.join(out, "_tmp.geo.json")
    pachy.preview_faces(m)
    tex = pachy.paint_sex(m, sex)
    if calf:      # the calf: no boss, no hooks, only the brow (young_brow)
        m.cubes = [c for c in m.cubes if c["bone"] not in ADULT]
    else:         # the grown one: no calf's brow; the female without the male's collars
        m.cubes = [c for c in m.cubes if c["bone"] != "young_brow" and (sex == "male" or c["bone"] != "male_display")]
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


def _render_side(name, spec, tex, k):
    if spec is None:
        spec = geo.load_geo(os.path.join(ASSETS, "geo", "entity", f"{name}.geo.json"))
        tex = Image.open(os.path.join(ASSETS, "textures", "entity", f"{name}_male.png"))
        spec = {**spec, "cubes": [c for c in spec["cubes"] if c.get("bone") != "saddle"]}
    pts = np.concatenate([q for c, q in geo.cube_points(spec)])
    L = pts[:, 2].max() - pts[:, 2].min(); Hh = pts[:, 1].max() - pts[:, 1].min()
    return geo.render(spec, tex, 90, 0, (int(L * k * 1.04) + 8, int(Hh * k * 1.04) + 8), bg=shots.BG, margin=0.02)[0].convert("RGB")


def next_to_kin(spec, tex, out, px=3):
    """side-on at their in-game scale: the Pachyrhinosaurus, the Triceratops, the Styracosaurus, the Protoceratops"""
    sizes = {"pachyrhinosaurus": SCALE[0]}
    import sil
    ims = [_render_side("pachyrhinosaurus", spec, tex, sizes["pachyrhinosaurus"] * px)]
    for sp in ("triceratops", "styracosaurus", "protoceratops"):
        ims.append(_render_side(sp, None, None, sil.game_scale(sp) * px))
    side_by_side(ims, gap=40).save(os.path.join(out, "ao_lado_dos_ceratopsianos.png"))


GIFS = ("walk", "run", "charge", "wade", "idle", "brace", "ring_defence", "boss_ram", "boss_push", "head_toss",
        "boss_rub", "snow_dig", "hesitate", "lunge", "parry", "stagger", "roar", "hatch", "graze", "sleep", "lie_down",
        "get_up", "death")


def gifs(out, sex="male"):
    from jsongif import pose_at, load_anims
    spec = geo.load_geo(os.path.join(ASSETS, "geo", "entity", "pachyrhinosaurus.geo.json"))
    tex = Image.open(os.path.join(ASSETS, "textures", "entity", f"pachyrhinosaurus_{sex}.png"))
    btex = Image.open(os.path.join(ASSETS, "textures", "entity", "pachyrhinosaurus_baby.png"))
    A = load_anims(os.path.join(ASSETS, "animations", "entity", "pachyrhinosaurus.animation.json"))
    hid = ("saddle",)
    gdir = os.path.join(out, "animacoes"); os.makedirs(gdir, exist_ok=True)
    for n in GIFS:
        young = n in ("hatch",)
        drop = ADULT if young else ("young_brow", "female_display")
        sp = {**spec, "cubes": [c for c in spec["cubes"] if c["bone"] not in drop]}
        tx = btex if young else tex
        an = A[f"animation.pachyrhinosaurus.{n}"]; L = an["animation_length"]
        fps = 12; N = max(2, int(round(L * fps)))
        poses = [pose_at(an, L * i / N) for i in range(N + (0 if an.get("loop") else 1))]
        yaw, pitch = (60, 12)
        fits = [geo.render(sp, tx, yaw, pitch, (64, 48), pose=p, hidden=hid)[1] for p in poses[::max(1, len(poses) // 8)]]
        fit = (min(f[0] for f in fits), max(f[1] for f in fits), min(f[2] for f in fits), max(f[3] for f in fits))
        ims = [geo.render(sp, tx, yaw, pitch, (560, 380), pose=p, hidden=hid, fit=fit, bg=shots.BG, margin=0.06)[0].convert("RGB")
               for p in poses]
        ims[0].save(os.path.join(gdir, f"{n}.gif"), save_all=True, append_images=ims[1:], duration=int(1000 / fps), loop=0)
        pick = [ims[int(i * (len(ims) - 1) / 4)] for i in range(5)]
        side_by_side([i.resize((280, 190), Image.LANCZOS) for i in pick], gap=4).save(os.path.join(gdir, f"{n}_quadros.png"))
        print("gif", n, len(ims), flush=True)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(ROOT, "art", "pachyrhinosaurus", "previews")
    os.makedirs(out, exist_ok=True)
    m = model(saddle_on=False)
    spec, tex = spec_tex(m, "male", out)
    tex.save(os.path.join(out, "pele_macho.png"))
    pts = np.concatenate([q for c, q in geo.cube_points(spec)])
    L = float(pts[:, 2].max() - pts[:, 2].min())
    SCALE[0] = 16.0 / skin2.density(L, 8.0)
    print(f"length {L:.1f} px, density {skin2.density(L, 8.0):.1f} tx/block, height {pts[:, 1].max():.1f} px, "
          f"colours {skin2.colour_count(tex)}")
    shots.shot(spec, tex, 90, 0, (1400, 620)).save(os.path.join(out, "lateral.png"))
    shots.shot(spec, tex, 35, 18, (1200, 800)).save(os.path.join(out, "tres_quartos.png"))
    shots.shot(spec, tex, 62, 12, (900, 600), bones=HEAD).save(os.path.join(out, "cabeca.png"))
    shots.shot(spec, tex, 90, 0, (900, 600), bones=HEAD).save(os.path.join(out, "cabeca_perfil.png"))
    if "--quick" in sys.argv:
        return
    shots.shot(spec, tex, 0, 8, (800, 700)).save(os.path.join(out, "frente.png"))
    shots.shot(spec, tex, 300, 22, (1200, 760)).save(os.path.join(out, "traseira.png"))
    shots.shot(spec, tex, 0, 4, (700, 600), bones=HEAD).save(os.path.join(out, "cabeca_frente.png"))
    fspec, ftex = spec_tex(model(saddle_on=False), "female", out)
    ftex.save(os.path.join(out, "pele_femea.png"))
    side_by_side([shots.shot(spec, tex, 35, 18, (1000, 680)), shots.shot(fspec, ftex, 35, 18, (1000, 680))]).save(
        os.path.join(out, "macho_e_femea.png"))
    side_by_side([shots.shot(spec, tex, 62, 12, (700, 480), bones=HEAD),
                  shots.shot(fspec, ftex, 62, 12, (700, 480), bones=HEAD)]).save(os.path.join(out, "cabeca_macho_e_femea.png"))
    cspec, ctex = spec_tex(model(saddle_on=False), "baby", out, calf=True)
    ctex.save(os.path.join(out, "pele_filhote.png"))
    shots.shot(cspec, ctex, 35, 18, (1000, 680)).save(os.path.join(out, "filhote.png"))
    sspec, stex = spec_tex(model(saddle_on=True), "male", out)
    shots.shot(sspec, stex, 35, 18, (1200, 800)).save(os.path.join(out, "com_sela.png"))
    next_to_kin(spec, tex, out)
    os.remove(os.path.join(out, "_tmp.geo.json"))
    if "--gifs" in sys.argv:
        gifs(out)


if __name__ == "__main__":
    main()
