"""standard preview shots, always from the exported geo.json (what GeckoLib draws): side, 3/4, front, head close-up"""
import math
import numpy as np
from PIL import Image
import geo
BG = (198, 214, 230)


def cam(yaw, pitch):
    yr, pr = math.radians(yaw), math.radians(pitch)
    fwd = -np.array([-math.sin(yr) * math.cos(pr), math.sin(pr), -math.cos(yr) * math.cos(pr)])
    right = np.cross(fwd, [0, 1.0, 0]); right /= np.linalg.norm(right); up = np.cross(right, fwd)
    return right, up


def fit_of(spec, bones, yaw, pitch, pose=None, pad=2.0):
    right, up = cam(yaw, pitch)
    pts = np.concatenate([q for c, q in geo.cube_points(spec, pose) if c["bone"] in bones])
    X, Y = pts @ right, pts @ up
    return (X.min() - pad, X.max() + pad, Y.min() - pad, Y.max() + pad)


def shot(spec, tex, yaw, pitch, size, pose=None, bones=None, hidden=(), bg=BG):
    fit = fit_of(spec, bones, yaw, pitch, pose) if bones else None
    return geo.render(spec, tex, yaw, pitch, size, pose=pose, fit=fit, hidden=hidden, bg=bg, margin=0.04)[0].convert("RGB")


def standard(spec, tex, out, head_bones=("head", "skull", "jaw"), hidden=()):
    shot(spec, tex, 90, 0, (1400, 560), hidden=hidden).save(f"{out}/side.png")
    shot(spec, tex, 35, 18, (1200, 760), hidden=hidden).save(f"{out}/tq.png")
    shot(spec, tex, 0, 8, (700, 600), hidden=hidden).save(f"{out}/front.png")
    shot(spec, tex, 300, 22, (1200, 760), hidden=hidden).save(f"{out}/back.png")
    shot(spec, tex, 62, 12, (900, 560), bones=head_bones, hidden=hidden).save(f"{out}/head.png")
