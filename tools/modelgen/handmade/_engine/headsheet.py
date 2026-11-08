"""Head sheets for the padrão studies (docs/estudos/14): the heads of several remade species side by side, from the
exported geo.json and textures (what GeckoLib draws), each framed on its own head bones, mouth shut.

usage:  python3 -B headsheet.py OUT.png [--side] [--female] species[:label] ...
        --side: from the animal's left (yaw 90); otherwise the 3/4 of the v2 sheets (yaw 62, pitch 12)
        python3 -B headsheet.py --before-after species OLD_DIR OUT.png   (old | new, OLD_DIR from git)
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geo  # noqa: E402
import shots  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
CELL = (700, 440)
BAR = 40


def head_bones(spec):
    hb = {"head", "skull", "jaw"}
    for _ in range(4):
        hb |= {b["name"] for b in spec["bones"] if b.get("parent") in hb}
    return hb


def head_shot(sp, side=False, sex="male", size=CELL, tex_path=None, geo_path=None):
    spec = geo.load_geo(geo_path or os.path.join(ASSETS, "geo", "entity", f"{sp}.geo.json"))
    tex = Image.open(tex_path or os.path.join(ASSETS, "textures", "entity", f"{sp}_{sex}.png"))
    hidden = tuple(b["name"] for b in spec["bones"] if b["name"] == "saddle")
    yaw, pitch = (90, 0) if side else (62, 12)
    hb = head_bones(spec)
    x0, x1, y0, y1 = shots.fit_of(spec, hb, yaw, pitch)
    # a little of the neck behind, as on the v2 sheets
    pad = (x1 - x0) * 0.12
    fit = (x0 - pad * 0.3, x1 + pad, y0 - pad * 0.4, y1 + pad * 0.3)
    return geo.render(spec, tex, yaw, pitch, size, fit=fit, hidden=hidden, bg=shots.BG, margin=0.04)[0].convert("RGB")


def font(size=24):
    for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc",
              "/Library/Fonts/Arial.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def sheet(cells, cols=3, cell=CELL, gap=16):
    """cells: [(label, image)]"""
    rows = (len(cells) + cols - 1) // cols
    W = cols * cell[0] + (cols - 1) * gap
    H = rows * (cell[1] + BAR) + (rows - 1) * gap
    out = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(out); f = font()
    for k, (label, im) in enumerate(cells):
        x = (k % cols) * (cell[0] + gap); y = (k // cols) * (cell[1] + BAR + gap)
        d.rectangle([x, y, x + cell[0] - 1, y + BAR - 1], fill=(40, 44, 52))
        d.text((x + 12, y + 7), label, font=f, fill=(240, 240, 240))
        out.paste(im.resize(cell) if im.size != cell else im, (x, y + BAR))
    return out


def before_after(sp, old_dir, out, old="v2", new="v3"):
    """old | new of one species: male side, male 3/4, female 3/4. old_dir holds <sp>.geo.json and <sp>_<sex>.png of
    the old version (taken from git)"""
    cells = []
    for side, sex, what in ((True, "male", "macho, lado"), (False, "male", "macho, 3/4"), (False, "female", "fêmea, 3/4")):
        cells.append((f"{old}: {what}", head_shot(sp, side, sex, tex_path=os.path.join(old_dir, f"{sp}_{sex}.png"),
                                                  geo_path=os.path.join(old_dir, f"{sp}.geo.json"))))
        cells.append((f"{new}: {what}", head_shot(sp, side, sex)))
    sheet(cells, cols=2).save(out)
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[0] == "--before-after":           # --before-after species old_dir out.png
        print(before_after(args[1], args[2], args[3]))
        sys.exit(0)
    out = args.pop(0)
    side = "--side" in args
    sex = "female" if "--female" in args else "male"
    names = [a for a in args if not a.startswith("--")]
    cells = []
    for a in names:
        sp, _, label = a.partition(":")
        cells.append((label or sp, head_shot(sp, side, sex)))
    sheet(cells, cols=min(3, len(cells))).save(out)
    print(out)
