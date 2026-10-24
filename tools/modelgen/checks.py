"""
Checks that the Python backend (pybench.py) rebuilds the committed assets exactly: same .geo.json, same
.animation.json and the same male texture (pixel by pixel) as the files in common/src/main/resources.
Run it after changing pybench.py or paint.py.  Writes nothing.

usage:  python3 checks.py [species ...]
"""
import asyncio
import importlib
import io
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "species"))

from build_all import ALL, ASSETS, clean_anim  # noqa: E402
from paint import make_shader, paint_model  # noqa: E402
from pybench import PyBench  # noqa: E402


async def check(names):
    ok = True
    async with PyBench() as bb:
        for name in names:
            model = importlib.import_module(name).build()
            spec = model.spec()
            dump = await bb.build(spec)
            pal = dict(model.palette)
            pal.update((getattr(model, "sexes", None) or {}).get("male", {}))
            img = paint_model(model, dump, make_shader(pal, model.pattern, model.decals))
            old = np.asarray(Image.open(os.path.join(ASSETS, "textures", "entity", f"{name}_male.png")).convert("RGBA")).astype(int)
            new = np.asarray(img).astype(int)
            tex_diff = int((np.abs(old - new).max(axis=2) > 2).sum()) if old.shape == new.shape else -1
            b = io.BytesIO()
            img.save(b, "PNG")
            out = await bb.finish(spec, b.getvalue())
            with open(os.path.join(ASSETS, "geo", "entity", f"{name}.geo.json")) as f:
                geo_ok = json.load(f) == json.loads(out["geo"])
            with open(os.path.join(ASSETS, "animations", "entity", f"{name}.animation.json")) as f:
                anim_ok = json.load(f) == clean_anim(out["anim"])
            good = tex_diff == 0 and geo_ok and anim_ok
            ok &= good
            print(f"{'ok  ' if good else 'DIFF'} {name}: texture pixels different {tex_diff}, geo {'=' if geo_ok else '!='}, "
                  f"animations {'=' if anim_ok else '!='}")
    return ok


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(check(sys.argv[1:] or ALL)) else 1)
