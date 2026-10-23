"""Contact sheet of preview renders: python3 contact.py out.png view1 [view2 ...]"""
import sys, os
from PIL import Image
ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "art")
names = ["tyrannosaurus", "triceratops", "stegosaurus", "velociraptor", "compsognathus"]
out, views = sys.argv[1], sys.argv[2:]
cell = 420
sheet = Image.new("RGB", (cell * len(views), cell * len(names)), (235, 235, 235))
for r, n in enumerate(names):
    for c, v in enumerate(views):
        p = os.path.join(ART, n, "previews", v + ".png")
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert("RGBA")
        bg = Image.new("RGBA", im.size, (235, 235, 235, 255)); bg.alpha_composite(im)
        bbox = bg.convert("RGB").point(lambda x: 255 if x < 230 else 0).getbbox()
        if bbox:
            pad = 10
            bbox = (max(0, bbox[0]-pad), max(0, bbox[1]-pad), min(im.width, bbox[2]+pad), min(im.height, bbox[3]+pad))
            bg = bg.crop(bbox)
        bg.thumbnail((cell - 10, cell - 10))
        sheet.paste(bg.convert("RGB"), (c * cell + (cell - bg.width)//2, r * cell + (cell - bg.height)//2))
sheet.save(out)
