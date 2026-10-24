"""Prévia rápida de um modelo: python3 preview.py <especie> [anim[:t] ...]  -> <especie>_pv.png
Linhas: pose de descanso + cada animação; cols: side, front34, front, head. Each row's camera is centred on that pose; the label shows the
pose's lowest point (ground = 0) so floating / sunken poses are caught."""
import asyncio, importlib, sys, io
import os; _here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, _here); sys.path.insert(0, os.path.join(_here, 'species'))
import numpy as np
from pybench import PyBench, Rig, pose_at
from build_all import bounds
from paint import paint_model, make_shader
from PIL import Image, ImageDraw

HIDE = ("saddle", "female_display")


def pose_bounds(rig, pose):
    pts = np.array([w for c, f, corners, uv in rig.cube_faces(pose, hidden=HIDE) for (_, w) in corners.values()])
    return pts.min(0), pts.max(0)


async def main(name, anims):
    m = importlib.import_module(name).build(); spec = m.spec(); rig = Rig(spec)
    async with PyBench() as bb:
        dump = await bb.build(spec); lo, hi = bounds(dump)
        img = paint_model(m, dump, make_shader(m.palette, m.pattern, m.decals)); b = io.BytesIO(); img.save(b, 'PNG')
        await bb.finish(spec, b.getvalue())
        for h in HIDE:
            await bb.set_visible(h, False)
        L = max(hi[2] - lo[2], hi[1] - lo[1], (hi[0] - lo[0]) * 0.7, 20); d = L * 1.75
        rows = [("rest", None, 0)] + [(a.split(":")[0], f"animation.{name}.{a.split(':')[0]}", float(a.split(":")[1]) if ":" in a else 0.5) for a in anims]
        S = 320
        sheet = Image.new('RGB', (S * 4, S * len(rows)), 'white'); dr = ImageDraw.Draw(sheet)
        for r, (label, anim, t) in enumerate(rows):
            pose = None
            if anim:
                a = next(a for a in spec["animations"] if a["name"] == anim)
                pose = pose_at(a, t)
            plo, phi = pose_bounds(rig, pose)
            cz = (plo[2] + phi[2]) / 2; cy = (plo[1] + phi[1]) / 2; cx = (plo[0] + phi[0]) / 2
            cams = {"side": {"position": [cx + d, cy, cz], "target": [cx, cy, cz], "fov": 40},
                    "front34": {"position": [cx + d * 0.62, cy + L * 0.2, cz - d * 0.72], "target": [cx, cy, cz], "fov": 40},
                    "front": {"position": [cx + 0.01, cy, cz - d], "target": [cx, cy, cz], "fov": 40},
                    "head": {"position": [cx + d * 0.35, phi[1] * 0.8 + 4, plo[2] + 10 - d * 0.3], "target": [cx, phi[1] * 0.8, plo[2] + 10], "fov": 40}}
            for c, (cn, cam) in enumerate(cams.items()):
                shot = await bb.shot(cam, anim, t) if anim else await bb.shot(cam)
                im = Image.open(io.BytesIO(shot)).convert('RGB').resize((S, S))
                sheet.paste(im, (c * S, r * S))
            dr.text((4, r * S + 4), f"{name} {label} t={t}  lowest y={plo[1]:.1f}  height={phi[1]:.1f}", fill='black')
        sheet.save(f'{name}_pv.png')
        print("bounds", lo, hi, "span", hi[0] - lo[0], "height", hi[1])

asyncio.run(main(sys.argv[1], sys.argv[2:]))
