"""Build a reviewable, isolated Blockbench pilot and source-rendered previews.

build/menu-render-venv/bin/python -B tools/modelgen/pilots/preview_trex.py
No game assets or existing art are overwritten.
"""
import asyncio
import hashlib
import io
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw

import trex_v1 as pilot
from pybench import PyBench, Rig
from trex_v1 import evaluate as pose_at
from paint import paint_model, make_shader

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "art/pilotos/trex/v1"
ASSETS = ROOT / "common/src/main/resources/assets/terrassic"
sys.path.insert(0, str(ROOT / "tools/capagen"))
import render3d


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def framing(rig, poses):
    pts = np.concatenate([pilot.point_cloud(rig, p) for p in poses])
    centre = (pts.min(0) + pts.max(0)) / 2
    direction = np.array([1.6, .48, -1.25]); direction /= np.linalg.norm(direction)
    forward = -direction
    right = np.cross(forward, [0, 1, 0]); right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    local = pts - centre
    tangent = np.tan(np.radians(32) / 2)
    distance = max(np.max(np.abs(local @ right) / (tangent * 1.6) - local @ forward),
                   np.max(np.abs(local @ up) / tangent - local @ forward)) * 1.16
    return {"position": (centre + direction * distance).tolist(), "target": centre.tolist(), "fov": 32}


def frame(rig, tex, pose, cam, label, size=(640, 400)):
    image = Image.new("RGBA", size, (30, 31, 37, 255))
    # Reference grid in y=0. Fixed camera; no pose-dependent recentering.
    eye, target = np.array(cam["position"]), np.array(cam["target"])
    fwd = target-eye; fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0,1,0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    def project(p):
        d = np.array(p)-eye
        f = 1/np.tan(np.radians(cam["fov"])/2)
        return (size[0]/2 + d@right/(d@fwd)*f*size[1]/2,
                size[1]/2 - d@up/(d@fwd)*f*size[1]/2)
    draw = ImageDraw.Draw(image)
    for k in range(-160, 161, 16):
        draw.line([project((k,0,-160)), project((k,0,160))], fill=(53,54,60), width=1)
        draw.line([project((-160,0,k)), project((160,0,k))], fill=(53,54,60), width=1)
    model = render3d.render(rig, tex, cam, size, pose, pilot.HIDE, ss=1,
                           key=(.4,.8,-.7), ambient=(.52,.52,.57), rim_power=.4)
    image.alpha_composite(model)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, size[0], 42), fill=(20, 21, 26, 255))
    draw.text((12, 8), label, fill=(236,218,183))
    low = float(pilot.point_cloud(rig, pose)[:,1].min())
    draw.text((12, 24), f"Ground reference: y=0 | lowest corner: {low:.2f} authoring px | PILOT", fill=(170,172,178))
    return image.convert("RGB")


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    inputs = sorted(p for p in ASSETS.rglob("*") if p.is_file())
    before = {str(p.relative_to(ROOT)):sha(p) for p in inputs}
    m = pilot.build(); spec = m.spec(); rig = Rig(spec)
    async with PyBench() as bb:
        dump = await bb.build(spec)
        texs = {}
        for sex in ("male", "female"):
            pal = dict(m.palette); pal.update(m.sexes.get(sex, {}))
            texs[sex] = paint_model(m, dump, make_shader(pal, m.pattern, m.decals))
            texs[sex].save(OUT / f"tyrannosaurus_{sex}.png")
        def png(im):
            b=io.BytesIO();im.save(b,"PNG");return b.getvalue()
        exports = await bb.finish(spec, png(texs["male"]), [("tyrannosaurus_female.png", png(texs["female"]))])
        for key, name in (("geo","tyrannosaurus.geo.json"), ("anim","tyrannosaurus.animation.json"),
                          ("bbmodel","tyrannosaurus.bbmodel")):
            (OUT/name).write_text(exports[key]+"\n")
    anims = {a["name"].split(".")[-1]:a for a in spec["animations"]}
    report = {"pilot": "T. rex v1, isolated, not installed in the mod", "cubes":len(m.cubes),
              "bones":len(m.bones), "offline_ground_correction_range_px":m._pilot_ground_correction_range,
              "production_asset_count":len(before),
              "production_assets_sha256":hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),
              "clips":{}, "source_hashes":{str(p.relative_to(ROOT)):sha(p)
                for p in [Path(__file__), Path(pilot.__file__), Path(pilot.original.__file__)]}}
    for clip in ("death", "knockout", "dead", "wake", "sit", "sleep", "lie_down", "stand_up"):
        a=anims[clip]
        lows=[]
        for t in np.linspace(0,a["length"],round(a["length"]*40)+1):
            lows.append(float(pilot.point_cloud(rig,pose_at(a,float(t)))[:,1].min()))
        report["clips"][clip]={"duration_s":a["length"],"min_y_px":min(lows),"max_lowest_y_px":max(lows)}
        assert min(lows) > -.5, f"{clip}: excessive penetration on the reference plane"
    end = pose_at(anims["death"], anims["death"]["length"])
    start = pose_at(anims["dead"], 0)
    assert end == start, "Death/carcass pose discontinuity"
    assert pose_at(anims["dead"], 0) == pose_at(anims["dead"], 1), "Moving corpse"
    # Old/new recovery, using the actual old source. There was no old authored death clip.
    old = pilot.original.build(); old_spec=old.spec(); old_rig=Rig(old_spec)
    old_tex=Image.open(ASSETS/"textures/entity/tyrannosaurus_male.png").convert("RGBA")
    old_wake=next(a for a in old.animations if a["name"].endswith(".wake"))
    for clip in ("death", "wake", "lie_down"):
        a=anims[clip]
        times=np.linspace(0,a["length"],round(a["length"]*15)+1)
        poses=[pose_at(a,float(t)) for t in times]
        cam=framing(rig,poses)
        gif=[frame(rig,texs["male"],p,cam,f"TERRASSIC / T. REX - {clip} / {t:.2f}s") for t,p in zip(times,poses)]
        # A short hold lets the viewer inspect the final contact.
        gif += [gif[-1]]*10
        gif[0].save(OUT/f"trex_{clip}.gif",save_all=True,append_images=gif[1:],duration=67,loop=0)
        if clip == "wake":
            compare=[]
            allposes=poses+[pose_at(old_wake,float(t)) for t in np.linspace(0,old_wake["length"],31)]
            # Both models have identical primary scale; shared camera from union.
            cam=framing(rig,allposes)
            for t,p in zip(times,poses):
                op=pose_at(old_wake,min(float(t),old_wake["length"]))
                left=frame(old_rig,old_tex,op,cam,f"SHIPPED / wake {min(t,1.8):.2f}s",(640,400))
                right=frame(rig,texs["male"],p,cam,f"PILOT / wake {t:.2f}s",(640,400))
                pair=Image.new("RGB",(1280,400));pair.paste(left,(0,0));pair.paste(right,(640,0));compare.append(pair)
            compare += [compare[-1]]*10
            compare[0].save(OUT/"trex_antes_depois.gif",save_all=True,append_images=compare[1:],duration=67,loop=0)
    poses=[("idle",0), ("roar",.9), ("death",.8), ("death",1.6), ("dead",0), ("sleep",0)]
    cam=framing(rig,[pose_at(anims[c],t) for c,t in poses])
    sheet=Image.new("RGB",(1280,1200))
    for i,(c,t) in enumerate(poses):
        sheet.paste(frame(rig,texs["male"],pose_at(anims[c],t),cam,f"T. REX PILOT / {c} {t:.2f}s"),((i%2)*640,(i//2)*400))
    sheet.save(OUT/"trex_poses.png")
    assert before == {str(p.relative_to(ROOT)):sha(p) for p in inputs}, "Game assets changed"
    report["production_assets_unchanged"]=True
    report["output_hashes"]={p.name:sha(p) for p in sorted(OUT.iterdir())
                             if p.is_file() and p.name!='validacao.json' and p.suffix!='.blend1'}
    (OUT/"validacao.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report["clips"],indent=2),flush=True)


if __name__ == "__main__":
    asyncio.run(main())
