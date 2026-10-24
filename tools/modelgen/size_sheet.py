"""Size comparison sheet: python3 size_sheet.py ../../art ../../art/tamanhos/comparacao_tamanhos.png"""
import json, sys, importlib.util
from PIL import Image, ImageDraw, ImageFont
art = sys.argv[1]
spec = importlib.util.spec_from_file_location("g", art + "/../tools/javagen/gen_species.py"); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
r = json.load(open(art + "/build_report.json"))
OLD = {"velociraptor": 0.5, "compsognathus": 0.3, "pachycephalosaurus": 0.667}
NAMES = {"tyrannosaurus":"T. rex","spinosaurus":"Spinosaurus","dilophosaurus":"Dilophosaurus","velociraptor":"Velociraptor","compsognathus":"Compsognathus","triceratops":"Triceratops","stegosaurus":"Stegosaurus","ankylosaurus":"Ankylosaurus","brachiosaurus":"Brachiosaurus","parasaurolophus":"Parasaurolophus","pachycephalosaurus":"Pachycephalosaurus","gallimimus":"Gallimimus"}
ROWS = [["brachiosaurus","spinosaurus","tyrannosaurus"],["triceratops","stegosaurus","parasaurolophus","ankylosaurus"],["gallimimus","dilophosaurus","pachycephalosaurus","velociraptor","compsognathus"]]
PPB = 30  # pixels per block
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18); small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except Exception:
    font = small = ImageFont.load_default()
def sprite(k, scale):
    im = Image.open(f"{art}/{k}/previews/side.png").convert("RGBA"); im = im.crop(im.split()[-1].getbbox())
    (a, c) = r[k]["bounds_px"]; hb = (c[1]-a[1])/16*scale
    f = hb*PPB/im.height
    return im.resize((max(1, round(im.width*f)), max(1, round(im.height*f))), Image.LANCZOS)
def ghost(im):
    a = im.split()[-1].point(lambda v: 110 if v > 0 else 0)
    gimg = Image.new("RGBA", im.size, (40, 40, 40, 0)); gimg.putalpha(a); return gimg
def player(d, x, y):
    u = PPB*1.8/32  # steve 32 px tall
    for (x0,y0,x1,y1,col) in [(2,0,10,8,(96,64,40)),(2,8,10,20,(40,150,160)),(0,8,2,20,(200,150,110)),(10,8,12,20,(200,150,110)),(2,20,6,32,(50,50,140)),(6,20,10,32,(50,50,140))]:
        d.rectangle([x+x0*u, y-32*u+y0*u, x+x1*u-1, y-32*u+y1*u-1], fill=col)
rows = []
for row in ROWS:
    items = []
    for k in row:
        s = g.SIZES[k]; new = sprite(k, s["scale"]); old = ghost(sprite(k, OLD.get(k, 1.0)))
        items.append((k, s, new, old))
    W = 40 + 30 + sum(max(n.width, o.width, 230) + 40 for _, _, n, o in items)
    H = max(n.height for _, _, n, _ in items) + 90
    img = Image.new("RGBA", (W, H), (245, 241, 230, 255)); d = ImageDraw.Draw(img)
    ground = H - 50
    for yy in range(ground, 0, -PPB): d.line([0, yy, W, yy], fill=(225, 220, 205))
    d.line([0, ground, W, ground], fill=(110, 90, 60), width=2)
    player(d, 20, ground); x = 70
    for k, s, n, o in items:
        img.alpha_composite(n, (x, ground - n.height)); img.alpha_composite(o, (x, ground - o.height))
        (a, c) = r[k]["bounds_px"]; L = (c[2]-a[2])/16*s["scale"]; Hh = (c[1]-a[1])/16*s["scale"]
        d.text((x, ground + 6), NAMES[k], fill=(30, 30, 30), font=font)
        d.text((x, ground + 27), f"{L:.1f} x {Hh:.1f} bl. (real {s['real']:g} m)", fill=(70, 70, 70), font=small)
        x += max(n.width, o.width, 230) + 40
    rows.append(img)
W = max(i.width for i in rows); H = sum(i.height for i in rows) + 60
sheet = Image.new("RGBA", (W, H), (245, 241, 230, 255)); d = ImageDraw.Draw(sheet)
d.text((20, 15), "Terrassic: tamanhos novos (cor) x atuais (sombra cinza). Jogador = 1,8 bloco. 1 linha = 1 bloco.", fill=(30, 30, 30), font=font)
y = 60
for i in rows: sheet.alpha_composite(i, (0, y)); y += i.height
sheet.convert("RGB").save(sys.argv[2]); print(sheet.size)
