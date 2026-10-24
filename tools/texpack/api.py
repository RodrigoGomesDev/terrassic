"""The texture engine in four calls. Everything else (noise, stamps, plates, rings, boards, leaves, sprites) is in
tex.py, stamps.py, woods.py, leaves.py and plants.py.

    import api
    t = ...                                # a tone map: ints, 0 = darkest (draw it with tex/stamps/woods...)
    img = api.paint(t, "amber")            # palette fitted to the material, painted, 16x16 RGBA
    img = api.paint(t, "bone", alpha=mask) # transparent where mask is False (measured on opaque pixels only)
    m, problems = api.check(img, "amber")  # luma within 14 and contrast within 20 of the material's target
    api.target("oak_planks")               # numbers of any vanilla 16x16 block texture

Materials (materials.py) map a name to a vanilla reference plus our hue; Material(...) works too, for one-offs.
"""
import numpy as np
from PIL import Image

import tex as T
from fit import fit
from materials import MATERIALS, Material, material
from targets import measure
from vanilla import target

TOL_LUMA = 14
TOL_CONTRAST = 20


def goal(mat):
    """(luma, contrast) the material aims at: its vanilla reference nudged by the era."""
    m = material(mat)
    lum, ctr = target(m.ref)[:2]
    return lum + m.dl, ctr + m.dc


def palette(tones, mat, mask=None, n=None):
    """Ramp of n colours (default: the material's) fitted so `tones` painted with it hits the material's goal.
    mask: only these pixels count (the opaque ones, for leaves and plants)."""
    m = material(mat)
    n = n or max(m.n, int(np.max(tones)) + 1)
    lum, ctr = goal(m)
    sample = np.asarray(tones)[mask] if mask is not None else np.ravel(tones)
    return fit(sample, n, lum, ctr, m.hue, m.sat, hue_shift=m.hue_shift, sat_shift=m.sat_shift, gamma=m.gamma)


def paint(tones, mat, alpha=None, extra=()):
    """Tone map -> 16x16 RGBA. alpha: boolean mask of opaque pixels. extra: fixed colours appended after the
    ramp (lichen, amber drops...), addressed by tone indices n, n+1, ..."""
    tones = np.asarray(tones)
    mask = None if alpha is None else np.asarray(alpha, bool)
    base_max = int(tones[mask].max() if mask is not None else tones.max()) + 1 - len(extra)
    pal = palette(np.clip(tones, 0, base_max - 1), mat, mask, n=max(material(mat).n, base_max))
    img = np.asarray(T.colorize(tones, list(pal) + list(extra))).copy()
    if mask is not None:
        img[..., 3] = np.where(mask, 255, 0)
        img[~mask, :3] = (np.array(pal[0]) * .6).round()   # what "fast" graphics shows in the holes
    return Image.fromarray(img, "RGBA")


def check(img, mat):
    m = measure(img)
    lum, ctr = goal(mat)
    lum -= material(mat).dl          # judged against vanilla itself, not the era nudge
    ctr -= material(mat).dc
    problems = []
    if abs(m["lum"] - lum) > TOL_LUMA + abs(material(mat).dl):
        problems.append(f"luma {m['lum']:.0f} vs {lum:.0f}")
    if abs(m["ctr"] - ctr) > TOL_CONTRAST + abs(material(mat).dc):
        problems.append(f"contrast {m['ctr']:.0f} vs {ctr:.0f}")
    return m, problems


__all__ = ["paint", "palette", "check", "goal", "target", "MATERIALS", "Material"]
