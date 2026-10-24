"""
Build every dinosaur: geometry -> Blockbench -> painted texture -> animations ->
export (.bbmodel for editing, .geo.json/.animation.json/.png for the mod) and
preview renders.

usage:  python3 build_all.py [--py] [species ...]

--py uses the pure Python backend (pybench.py) instead of the headless Blockbench. Without it the Python backend
is also used when no Blockbench is served on localhost:8123. Both give the same geo, animation and texture files
(checked for all v0.2 species); only the .bbmodel and the preview renders differ a little.
"""
import asyncio
import importlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "species"))

from paint import paint_model, make_shader  # noqa: E402
from pybench import PyBench  # noqa: E402

sys.path.insert(0, os.path.join(HERE, "..", "spritegen"))
from sprites import save_png  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
ART = os.path.join(ROOT, "art")

ALL = ["tyrannosaurus", "spinosaurus", "dilophosaurus", "velociraptor", "compsognathus",
       "triceratops", "stegosaurus", "ankylosaurus", "brachiosaurus", "parasaurolophus",
       "pachycephalosaurus", "gallimimus", "pteranodon", "mosasaurus", "maiasaura",
       "quetzalcoatlus", "hatzegopteryx", "ichthyornis", "tylosaurus", "elasmosaurus",
       "xiphactinus", "archelon", "hesperornis", "deinosuchus", "baurusuchus",
       "edmontosaurus", "corythosaurus", "styracosaurus", "euoplocephalus", "protoceratops", "struthiomimus", "thescelosaurus", "pachyrhinosaurus", "therizinosaurus", "deinocheirus", "alamosaurus", "saltasaurus", "argentinosaurus", "opisthocoelicaudia"]


def clean_anim(anim_json):
    """GeckoLib chokes on "pre": null that Blockbench emits for plain keyframes."""
    data = json.loads(anim_json)
    for a in data.get("animations", {}).values():
        for bone in a.get("bones", {}).values():
            for ch, frames in list(bone.items()):
                if not isinstance(frames, dict):
                    continue
                for t, kf in list(frames.items()):
                    if isinstance(kf, dict):
                        if kf.get("pre") is None:
                            kf.pop("pre", None)
                        if kf.get("lerp_mode") == "linear":
                            frames[t] = kf["post"]
    return data


def bounds(dump):
    xs, ys, zs = [], [], []
    for c in dump:
        for v in c["verts"]:
            xs.append(v["w"][0]); ys.append(v["w"][1]); zs.append(v["w"][2])
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def cameras(lo, hi):
    cx, cy, cz = [(lo[i] + hi[i]) / 2 for i in range(3)]
    L = max(hi[2] - lo[2], (hi[1] - lo[1]) * 1.2, (hi[0] - lo[0]) * 0.8, 20)
    d = L * 1.45
    return {
        "side": {"position": [d, cy + L * 0.05, cz], "target": [0, cy, cz], "fov": 40},
        "front34": {"position": [d * 0.62, cy + L * 0.22, cz - d * 0.72], "target": [0, cy, cz], "fov": 40},
        "back34": {"position": [-d * 0.62, cy + L * 0.30, cz + d * 0.72], "target": [0, cy, cz], "fov": 40},
        "top": {"position": [0.01, cy + d * 1.05, cz], "target": [0, cy, cz], "fov": 40},
    }


def blockbench_available(url="http://localhost:8123/index.html"):
    import urllib.request
    try:
        urllib.request.urlopen(url, timeout=2)
        return True
    except Exception:
        return False


def backend(force_py):
    if force_py or not blockbench_available():
        print("using the Python backend (pybench.py)")
        return PyBench()
    from bbdriver import Blockbench
    return Blockbench()


async def run(names, force_py=False):
    os.makedirs(os.path.join(ASSETS, "geo", "entity"), exist_ok=True)
    os.makedirs(os.path.join(ASSETS, "animations", "entity"), exist_ok=True)
    os.makedirs(os.path.join(ASSETS, "textures", "entity"), exist_ok=True)
    report_path = os.path.join(ART, "build_report.json")
    report = {}
    if os.path.exists(report_path):  # keep the species that are not rebuilt this time
        with open(report_path) as f:
            report = json.load(f)
    async with backend(force_py) as bb:
        for name in names:
            mod = importlib.import_module(name)
            model = mod.build()
            spec = model.spec()
            dump = await bb.build(spec)
            lo, hi = bounds(dump)
            sexes = getattr(model, "sexes", None) or {"male": {}, "female": {}}
            texs = {}
            for sex in ("male", "female"):
                pal = dict(model.palette)
                pal.update(sexes.get(sex, {}))
                shader = make_shader(pal, model.pattern, model.decals)
                texs[sex] = paint_model(model, dump, shader)
            def png(img):
                b = io.BytesIO(); img.save(b, "PNG"); return b.getvalue()
            out = await bb.finish(spec, png(texs["male"]), [(f"{name}_female.png", png(texs["female"]))])
            art = os.path.join(ART, name)
            os.makedirs(os.path.join(art, "previews"), exist_ok=True)
            with open(os.path.join(art, f"{name}.bbmodel"), "w") as f:
                f.write(out["bbmodel"])
            geo = json.loads(out["geo"])
            with open(os.path.join(ASSETS, "geo", "entity", f"{name}.geo.json"), "w") as f:
                json.dump(geo, f, indent=1)
            anim = clean_anim(out["anim"])
            with open(os.path.join(ASSETS, "animations", "entity", f"{name}.animation.json"), "w") as f:
                json.dump(anim, f, indent=1)
            for sex, img in texs.items():
                save_png(img, os.path.join(ASSETS, "textures", "entity", f"{name}_{sex}.png"))
                save_png(img, os.path.join(art, f"{name}_{sex}.png"))
            cams = cameras(lo, hi)
            # previews show the male look; female and saddled looks get their own shots
            await bb.set_visible("female_display", False)
            await bb.set_visible("saddle", False)
            for cname, cam in cams.items():
                shot = await bb.shot(cam)
                open(os.path.join(art, "previews", f"{cname}.png"), "wb").write(shot)
            await bb.set_texture(1)
            await bb.set_visible("male_display", False)
            await bb.set_visible("female_display", True)
            shot = await bb.shot(cams["front34"])
            open(os.path.join(art, "previews", "front34_female.png"), "wb").write(shot)
            await bb.set_texture(0)
            await bb.set_visible("male_display", True)
            await bb.set_visible("female_display", False)
            if any(b.name == "saddle" for b in model.bones):
                await bb.set_visible("saddle", True)
                shot = await bb.shot(cams["front34"])
                open(os.path.join(art, "previews", "front34_saddle.png"), "wb").write(shot)
                await bb.set_visible("saddle", False)
            for a in model.animations:
                short = a["name"].split(".")[-1]
                for k, t in enumerate((0.0, 0.25, 0.5, 0.75)):
                    shot = await bb.shot(cams["side"], a["name"], round(t * a["length"], 3))
                    open(os.path.join(art, "previews", f"anim_{short}_{k}.png"), "wb").write(shot)
            report[name] = {
                "bones": len(spec["bones"]), "cubes": len(spec["cubes"]),
                "texture": [spec["texture_width"], spec["texture_height"]],
                "bounds_px": [lo, hi],
                "animations": [a["name"] for a in model.animations],
                "render_scale": model.render_scale,
            }
            print(name, json.dumps(report[name]))
        if bb.errors:
            print("page errors:", bb.errors[:10])
    with open(report_path, "w") as f:
        json.dump(report, f, indent=1)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    asyncio.run(run(args or ALL, force_py="--py" in sys.argv))
