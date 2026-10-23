"""
Build every dinosaur: geometry -> Blockbench -> painted texture -> animations ->
export (.bbmodel for editing, .geo.json/.animation.json/.png for the mod) and
preview renders.

usage:  python3 build_all.py [species ...]
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
from bbdriver import Blockbench  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "primalera")
ART = os.path.join(ROOT, "art")

ALL = ["tyrannosaurus", "triceratops", "stegosaurus", "velociraptor", "compsognathus"]


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
    L = max(hi[2] - lo[2], (hi[1] - lo[1]) * 1.2, 20)
    d = L * 1.45
    return {
        "side": {"position": [d, cy + L * 0.05, cz], "target": [0, cy, cz], "fov": 40},
        "front34": {"position": [d * 0.62, cy + L * 0.22, cz - d * 0.72], "target": [0, cy, cz], "fov": 40},
        "back34": {"position": [-d * 0.62, cy + L * 0.30, cz + d * 0.72], "target": [0, cy, cz], "fov": 40},
        "top": {"position": [0.01, cy + d * 1.05, cz], "target": [0, cy, cz], "fov": 40},
    }


async def run(names):
    os.makedirs(os.path.join(ASSETS, "geo", "entity"), exist_ok=True)
    os.makedirs(os.path.join(ASSETS, "animations", "entity"), exist_ok=True)
    os.makedirs(os.path.join(ASSETS, "textures", "entity"), exist_ok=True)
    report = {}
    async with Blockbench() as bb:
        for name in names:
            mod = importlib.import_module(name)
            model = mod.build()
            spec = model.spec()
            dump = await bb.build(spec)
            lo, hi = bounds(dump)
            shader = make_shader(model.palette, model.pattern, model.decals)
            tex = paint_model(model, dump, shader)
            buf = io.BytesIO(); tex.save(buf, "PNG")
            out = await bb.finish(spec, buf.getvalue())
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
            tex.save(os.path.join(ASSETS, "textures", "entity", f"{name}.png"))
            tex.save(os.path.join(art, f"{name}.png"))
            cams = cameras(lo, hi)
            for cname, cam in cams.items():
                png = await bb.shot(cam)
                open(os.path.join(art, "previews", f"{cname}.png"), "wb").write(png)
            for a in model.animations:
                short = a["name"].split(".")[-1]
                for k, t in enumerate((0.0, 0.25, 0.5, 0.75)):
                    png = await bb.shot(cams["side"], a["name"], round(t * a["length"], 3))
                    open(os.path.join(art, "previews", f"anim_{short}_{k}.png"), "wb").write(png)
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
    with open(os.path.join(ART, "build_report.json"), "w") as f:
        json.dump(report, f, indent=1)


if __name__ == "__main__":
    asyncio.run(run(sys.argv[1:] or ALL))
