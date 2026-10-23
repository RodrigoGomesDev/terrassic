"""Render animated GIF previews (front 3/4 view) of each animation: art/<sp>/previews/<anim>.gif"""
import asyncio, io, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from PIL import Image
from bbdriver import Blockbench
from build_all import ART, cameras, bounds

async def main(names):
    async with Blockbench() as bb:
        for n in names:
            content = open(os.path.join(ART, n, f"{n}.bbmodel")).read()
            info = await bb.page.evaluate("""(args)=>{ const [c,p]=args; loadModelFile({content:c, path:p, name:p});
                 let xs=[],ys=[],zs=[]; for (const cube of Cube.all){ cube.mesh.updateMatrixWorld(true); const b=new THREE.Box3().setFromObject(cube.mesh); xs.push(b.min.x,b.max.x); ys.push(b.min.y,b.max.y); zs.push(b.min.z,b.max.z);} 
                 return {anims: Animation.all.map(a=>[a.name,a.length]), lo:[Math.min(...xs),Math.min(...ys),Math.min(...zs)], hi:[Math.max(...xs),Math.max(...ys),Math.max(...zs)]}; }""", [content, f"{n}.bbmodel"])
            cam = cameras(info["lo"], info["hi"])["front34"]
            for name, length in info["anims"]:
                short = name.split(".")[-1]
                frames = []
                nf = max(12, min(40, int(length * 15)))
                for i in range(nf):
                    png = await bb.shot(cam, name, round(i * length / nf, 3))
                    im = Image.open(io.BytesIO(png)).convert("RGBA")
                    bg = Image.new("RGBA", im.size, (236, 236, 230, 255)); bg.alpha_composite(im)
                    frames.append(bg.convert("RGB"))
                # common crop
                box = None
                for f in frames:
                    b = f.point(lambda x: 255 if x < 226 else 0).getbbox()
                    if b: box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
                pad = 12
                box = (max(0, box[0]-pad), max(0, box[1]-pad), box[2]+pad, box[3]+pad)
                frames = [f.crop(box) for f in frames]
                frames = [f.resize((int(f.width * 420 / max(f.size)), int(f.height * 420 / max(f.size)))) for f in frames]
                out = os.path.join(ART, n, "previews", f"{short}.gif")
                frames[0].save(out, save_all=True, append_images=frames[1:], duration=int(1000 * length / nf), loop=0, optimize=True)
                print(out)

asyncio.run(main(sys.argv[1:] or ["tyrannosaurus", "triceratops", "stegosaurus", "velociraptor", "compsognathus"]))
