"""Review sheet: python3 review.py out.png view1 view2 ... (species rows)"""
import os, sys
from PIL import Image
ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "art")
NAMES = ["tyrannosaurus", "spinosaurus", "dilophosaurus", "velociraptor", "compsognathus", "triceratops",
         "stegosaurus", "ankylosaurus", "brachiosaurus", "parasaurolophus", "pachycephalosaurus", "gallimimus"]
out, views = sys.argv[1], sys.argv[2:]
names = [n for n in NAMES if os.environ.get("ONLY", "") in ("", ) or n in os.environ["ONLY"].split(",")]
cw, ch = 330, 250
sheet = Image.new("RGB", (cw * len(views), ch * len(names)), (236, 236, 230))
for r, n in enumerate(names):
    for c, v in enumerate(views):
        p = os.path.join(ART, n, "previews", v + ".png")
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert("RGBA"); bb = im.getbbox()
        if bb: im = im.crop(bb)
        im.thumbnail((cw - 10, ch - 10))
        sheet.paste(im, (c * cw + (cw - im.width) // 2, r * ch + (ch - im.height) // 2), im)
sheet.save(out)
