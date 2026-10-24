"""Keeps the head out of the ground in one-shot actions: fit_to_ground(m, "eat", ("neck1", "neck2", "skull")) scales
the pitch of those bones in that animation down until the lowest cube stays at most `tol` px under the ground
(sampled through the whole animation). Needed for long necks and big heads, where the shared action sets (written
for the 1x rigs) push the snout deep into the ground."""
from rig import lowest_point


def _lowest(m, anim, n=12):
    return min(lowest_point(m, anim["bones"], anim["length"] * k / n) for k in range(n + 1))


def fit_to_ground(m, name, bones, tol=0.5, steps=12):
    anim = next(a for a in m.animations if a["name"].endswith("." + name))
    orig = {b: [list(k) for k in anim["bones"][b]["rotation"]] for b in bones if b in anim["bones"]}

    def apply(f):
        for b, ks in orig.items():
            anim["bones"][b]["rotation"] = [[k[0], round(k[1] * f, 3), k[2], k[3]] for k in ks]

    if _lowest(m, anim) >= -tol:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(steps):
        mid = (lo + hi) / 2
        apply(mid)
        if _lowest(m, anim) >= -tol:
            lo = mid
        else:
            hi = mid
    apply(lo)
    return lo
