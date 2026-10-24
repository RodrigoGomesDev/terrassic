"""Preview sheets for the texture packs: every texture big, tiled 3x3, and a small isometric diorama of cubes
lit the way Minecraft lights block faces (top 100%, north/south 80%, east/west 60%)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BG = (38, 38, 44, 255)


def font(size=12):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def big(img, k):
    return img.resize((img.width * k, img.height * k), Image.NEAREST)


def tiled(img, n=3):
    out = Image.new("RGBA", (img.width * n, img.height * n))
    for j in range(n):
        for i in range(n):
            out.paste(img, (i * img.width, j * img.height))
    return out


def tint(img, rgb):
    a = np.asarray(img.convert("RGBA"), float)
    a[..., :3] = a[..., :3] * np.array(rgb, float) / 255.0
    return Image.fromarray(a.round().astype(np.uint8), "RGBA")


def over(base, top):
    out = base.copy()
    out.alpha_composite(top)
    return out


def shade(img, f):
    a = np.asarray(img, float).copy()
    a[..., :3] *= f
    return Image.fromarray(a.round().clip(0, 255).astype(np.uint8), "RGBA")


def _face(tex, S, which):
    t = big(tex, S // tex.width)
    if which == "top":
        data = (0.5, 1.0, -S / 2, -0.5, 1.0, S / 2)
    elif which == "left":
        data = (1.0, 0.0, 0.0, -0.5, 1.0, -S / 2)
    else:
        data = (1.0, 0.0, -S, 0.5, 1.0, -1.5 * S)
    out = t.transform((2 * S, 2 * S), Image.AFFINE, data, resample=Image.NEAREST, fillcolor=(0, 0, 0, 0))
    # mask the parallelogram exactly (transform repeats edge pixels outside the source)
    ys, xs = np.mgrid[0:2 * S, 0:2 * S] + 0.5
    a, b, c, d, e, f = data
    u = a * xs + b * ys + c
    v = d * xs + e * ys + f
    inside = (u >= 0) & (u < S) & (v >= 0) & (v < S)
    arr = np.asarray(out).copy()
    arr[~inside] = 0
    return Image.fromarray(arr, "RGBA")


def cube(top, left, right, S=64):
    img = Image.new("RGBA", (2 * S, 2 * S))
    img.alpha_composite(shade(_face(left, S, "left"), 0.8))
    img.alpha_composite(shade(_face(right, S, "right"), 0.6))
    img.alpha_composite(_face(top, S, "top"))
    return img


def diorama(blocks, S=32, pad=16):
    """blocks: {(x, y, z): (top, left, right)}; x to the right-down, z to the left-down, y up."""
    xs = [k[0] for k in blocks]
    zs = [k[2] for k in blocks]
    ys = [k[1] for k in blocks]
    w = (max(xs) + max(zs) + 2) * S + 2 * pad
    h = int((max(xs) + max(zs) + 2) * S / 2 + (max(ys) + 2) * S) + 2 * pad
    img = Image.new("RGBA", (w, h), BG)
    oy = (max(ys) + 1) * S + pad
    ox = (max(zs)) * S + pad
    cache = {}
    for (x, y, z) in sorted(blocks, key=lambda k: (k[0] + k[2], k[1], k[0])):
        faces = blocks[(x, y, z)]
        key = tuple(id(f) for f in faces)
        if key not in cache:
            cache[key] = cube(*faces, S=S)
        sx = ox + (x - z) * S
        sy = oy + (x + z) * S // 2 - y * S
        img.alpha_composite(cache[key], (sx, sy))
    return img


def sheet(items, title, k=8, cols=6):
    """items: [(name, img16)] -> labelled sheet with big view + 3x3 tile."""
    f = font(13)
    cell_w = 16 * k + 16 * 4 * 3 // 2 + 30
    cell_w = max(16 * k, 16 * 3 * 4) + 16
    cell_h = 16 * k + 16 * 3 * 4 + 40
    rows = (len(items) + cols - 1) // cols
    img = Image.new("RGBA", (cols * cell_w + 20, rows * cell_h + 50), BG)
    d = ImageDraw.Draw(img)
    d.text((10, 10), title, fill=(230, 230, 230, 255), font=font(18))
    for n, (name, tex) in enumerate(items):
        cx = 10 + (n % cols) * cell_w
        cy = 44 + (n // cols) * cell_h
        img.alpha_composite(big(tex, k), (cx, cy))
        img.alpha_composite(big(tiled(tex, 3), 4), (cx, cy + 16 * k + 4))
        d.text((cx, cy + 16 * k + 16 * 12 + 8), name, fill=(220, 220, 220, 255), font=f)
    return img


def diorama_culled(blocks, S=32, pad=8, bg=BG):
    """Like diorama(), but a face is left out when a block sits against it (as the game does), so leaves and
    see-through blocks show only their outside."""
    empty = Image.new("RGBA", (16, 16))
    xs = [k[0] for k in blocks]
    zs = [k[2] for k in blocks]
    ys = [k[1] for k in blocks]
    w = (max(xs) + max(zs) + 2) * S + 2 * pad
    h = int((max(xs) + max(zs) + 2) * S / 2 + (max(ys) + 2) * S) + 2 * pad
    img = Image.new("RGBA", (w, h), bg)
    oy = (max(ys) + 1) * S + pad
    ox = max(zs) * S + pad
    for (x, y, z) in sorted(blocks, key=lambda k: (k[0] + k[2], k[1], k[0])):
        top, left, right = blocks[(x, y, z)]
        c = cube(empty if (x, y + 1, z) in blocks else top, empty if (x, y, z + 1) in blocks else left,
                 empty if (x + 1, y, z) in blocks else right, S=S)
        img.alpha_composite(c, (ox + (x - z) * S, oy + (x + z) * S // 2 - y * S))
    return img


def sheet_images(items, title, cols=4, pad=10):
    """items: [(name, image of any size)] -> labelled sheet."""
    w = max(im.width for _, im in items)
    h = max(im.height for _, im in items)
    rows = (len(items) + cols - 1) // cols
    img = Image.new("RGBA", (cols * (w + pad) + pad, rows * (h + 24) + 44), BG)
    d = ImageDraw.Draw(img)
    d.text((10, 10), title, fill=(230, 230, 230, 255), font=font(18))
    for n, (name, im) in enumerate(items):
        x = pad + (n % cols) * (w + pad)
        y = 40 + (n // cols) * (h + 24)
        img.alpha_composite(im, (x, y))
        d.text((x, y + h + 4), name, fill=(220, 220, 220, 255), font=font(13))
    return img
