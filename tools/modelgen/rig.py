"""
Terrassic model generator - rig primitives.

Coordinate system (same as what you see in Blockbench, "B-space"):
  * units are pixels (16 px = 1 block)
  * Y up, ground at y = 0
  * the animal faces NORTH (-Z); the tail points to +Z
  * X is left/right; models are symmetric around x = 0

Rotation conventions (Blockbench / three.js, Euler order ZYX, degrees):
  * +X rotation lifts parts that point forward (-Z) and swings parts that hang
    down (-Y) forward.
  * +Y rotation turns a forward-pointing part towards -X.
  * +Z rotation tilts an upward-pointing part towards -X.

GeckoLib renders exactly what Blockbench shows (it mirrors X back on load), so
what the previews show is what the game shows.
"""
import math

def _r(v, n=4):
    return round(float(v), n)


class Cube:
    def __init__(self, bone, frm, to, tag="skin", inflate=0.0, rot=None, origin=None, name=None, paint=None):
        self.bone = bone
        self.frm = [_r(a) for a in frm]
        self.to = [_r(b) for b in to]
        for i in range(3):
            if self.to[i] < self.frm[i]:
                self.frm[i], self.to[i] = self.to[i], self.frm[i]
        size = [self.to[i] - self.frm[i] for i in range(3)]
        for s in size:
            if abs(s - round(s)) > 1e-3:
                raise ValueError(f"cube {name} on {bone} has non-integer size {size} (box UV needs integers)")
            if round(s) < 1:
                raise ValueError(f"cube {name} on {bone} has zero size {size}")
        self.size = [int(round(s)) for s in size]
        self.tag = tag
        self.inflate = inflate
        self.rot = [_r(a) for a in (rot or (0, 0, 0))]
        if origin is None:
            origin = [(self.frm[i] + self.to[i]) / 2 for i in range(3)]
        self.origin = [_r(a) for a in origin]
        self.name = name or tag
        self.paint = paint or {}
        self.uv = [0, 0]

    @property
    def uv_size(self):
        dx, dy, dz = self.size
        return (2 * (dx + dz), dz + dy)


class Bone:
    def __init__(self, name, parent, pivot, rot=(0, 0, 0)):
        self.name = name
        self.parent = parent
        self.pivot = [_r(a) for a in pivot]
        self.rot = [_r(a) for a in rot]


def angle_x(u, d):
    """Signed angle (deg) about +X that rotates unit vector u (y,z) onto d (y,z)."""
    uy, uz = u
    dy, dz = d
    cross = uy * dz - uz * dy
    dot = uy * dy + uz * dz
    return math.degrees(math.atan2(cross, dot))


AXES = {"-y": (-1.0, 0.0), "+z": (0.0, 1.0), "-z": (0.0, -1.0), "+y": (1.0, 0.0)}


class Model:
    def __init__(self, ident, render_scale=1.0):
        self.id = ident
        self.render_scale = render_scale
        self.bones = []
        self.cubes = []
        self.decals = []        # eyes, nostrils, etc.
        self.animations = []
        self.palette = {}
        self.pattern = None     # callable(P, N, tag, rgb, cube) -> rgb
        self._bone_index = {}
        self._abs_rot = {}      # accumulated X rotation (only used for planar chains)

    # ------------------------------------------------------------------ bones
    def bone(self, name, parent, pivot, rot=(0, 0, 0)):
        if name in self._bone_index:
            raise ValueError("duplicate bone " + name)
        b = Bone(name, parent, pivot, rot)
        self.bones.append(b)
        self._bone_index[name] = b
        parent_abs = self._abs_rot.get(parent, 0.0) if parent else 0.0
        self._abs_rot[name] = parent_abs + rot[0]
        return name

    def abs_rot(self, bone):
        return self._abs_rot.get(bone, 0.0)

    # ------------------------------------------------------------------ cubes
    def box(self, bone, frm, to, tag="skin", **kw):
        c = Cube(bone, frm, to, tag=tag, **kw)
        self.cubes.append(c)
        return c

    def cbox(self, bone, center, size, tag="skin", **kw):
        frm = [center[i] - size[i] / 2 for i in range(3)]
        to = [center[i] + size[i] / 2 for i in range(3)]
        return self.box(bone, frm, to, tag=tag, **kw)

    def sym(self, fn):
        """Call fn(side, sx) for the left (+X, 'l') and right (-X, 'r') sides."""
        fn("l", 1.0)
        fn("r", -1.0)

    # ------------------------------------------------------------------ chains
    def chain(self, names, parent, x, points, axis, sections, tag="skin",
              overlap=(1.0, 1.0), paints=None, inflate=0.0):
        """
        Build a planar (YZ) bone chain whose joints sit at the given POSED points.

        names    : bone names, one per segment
        points   : [(y, z), ...] joint positions in the final pose (len = len(names)+1)
        axis     : direction the segments are modelled along in the unposed
                   model: '-y' (legs, arms), '+z' (tails), '-z' (necks)
        sections : per segment (w, h[, off]) cross section; w along X, h along
                   the other perpendicular axis; off shifts the box along that
                   perpendicular axis (e.g. to push thigh muscle forward).
        Returns dict with the unposed end point and the absolute angle of the
        last segment, so children can be attached and levelled.
        """
        assert len(points) == len(names) + 1
        u = AXES[axis]
        parent_abs = self.abs_rot(parent)
        if abs(parent_abs) > 1e-6:
            raise ValueError("chain parent must have no accumulated rotation: " + parent)
        uy, uz = u
        cur = (points[0][0], points[0][1])  # unposed pivot of current segment
        prev_abs = 0.0
        out = []
        for i, name in enumerate(names):
            p0, p1 = points[i], points[i + 1]
            dy, dz = p1[0] - p0[0], p1[1] - p0[1]
            L = math.hypot(dy, dz)
            d = (dy / L, dz / L)
            ang = angle_x(u, d)
            rel = ang - prev_abs
            pname = parent if i == 0 else names[i - 1]
            self.bone(name, pname, (x, cur[0], cur[1]), (rel, 0, 0))
            sec = sections[i]
            w, h = sec[0], sec[1]
            off = sec[2] if len(sec) > 2 else 0.0
            ov0, ov1 = overlap if isinstance(overlap, tuple) else (overlap, overlap)
            length = int(round(L + ov0 + ov1))
            start = -ov0
            end = start + length
            # endpoints along the axis
            ay0, az0 = cur[0] + uy * start, cur[1] + uz * start
            ay1, az1 = cur[0] + uy * end, cur[1] + uz * end
            if axis in ("-y", "+y"):
                frm = (x - w / 2, min(ay0, ay1), cur[1] - h / 2 + off)
                to = (x + w / 2, max(ay0, ay1), cur[1] + h / 2 + off)
            else:
                frm = (x - w / 2, cur[0] - h / 2 + off, min(az0, az1))
                to = (x + w / 2, cur[0] + h / 2 + off, max(az0, az1))
            paint = (paints[i] if paints else None) or {}
            t = sec[3] if len(sec) > 3 else tag
            self.box(name, frm, to, tag=t, origin=(x, cur[0], cur[1]), name=name, paint=paint, inflate=inflate)
            out.append({"bone": name, "unposed": cur, "len": L, "abs": ang})
            cur = (cur[0] + uy * L, cur[1] + uz * L)
            prev_abs = ang
        return {"end": cur, "abs": prev_abs, "segments": out}

    # ------------------------------------------------------------- animation
    def anim(self, name, length, loop=True, bones=None):
        self.animations.append({"name": f"animation.{self.id}.{name}", "length": length,
                                "loop": "loop" if loop else "once", "bones": bones or {}})

    # ------------------------------------------------------------- packing
    def pack_uv(self):
        rects = sorted(self.cubes, key=lambda c: (-c.uv_size[1], -c.uv_size[0]))
        best = None
        for W in (64, 128, 256, 512):
            if max(c.uv_size[0] for c in rects) > W:
                continue
            x = y = shelf_h = 0
            pos = {}
            for c in rects:
                w, h = c.uv_size
                if x + w > W:
                    x = 0
                    y += shelf_h
                    shelf_h = 0
                pos[id(c)] = (x, y)
                x += w
                shelf_h = max(shelf_h, h)
            used_h = y + shelf_h
            H = 16
            while H < used_h:
                H *= 2
            if H > 4 * W:
                continue
            area = W * H
            if best is None or area < best[0] or (area == best[0] and abs(W - H) < abs(best[1] - best[2])):
                best = (area, W, H, pos)
        _, W, H, pos = best
        for c in self.cubes:
            c.uv = list(pos[id(c)])
        self.tex_w, self.tex_h = W, H
        return W, H

    # ------------------------------------------------------------- export spec
    def spec(self):
        self.pack_uv()
        return {
            "id": self.id,
            "texture_width": self.tex_w,
            "texture_height": self.tex_h,
            "bones": [{"name": b.name, "parent": b.parent, "origin": b.pivot, "rotation": b.rot} for b in self.bones],
            "cubes": [{"name": c.name, "bone": c.bone, "from": c.frm, "to": c.to, "origin": c.origin,
                       "rotation": c.rot, "inflate": c.inflate, "uv_offset": c.uv} for c in self.cubes],
            "animations": self.animations,
        }


# ---------------------------------------------------------------- animation helpers
def wave(n, fn, length, digits=2):
    """Sample fn(phase 0..1) -> (x,y,z) at n+1 evenly spaced keys over [0,length]."""
    keys = []
    for i in range(n + 1):
        ph = i / n
        v = fn(ph % 1.0)
        keys.append([round(ph * length, 4)] + [round(a, digits) for a in v])
    return keys


def sinx(amp, phase=0.0, offset=0.0, harmonic=1):
    return lambda p: (offset + amp * math.sin(2 * math.pi * (harmonic * p + phase)), 0.0, 0.0)


def siny(amp, phase=0.0, offset=0.0, harmonic=1):
    return lambda p: (0.0, offset + amp * math.sin(2 * math.pi * (harmonic * p + phase)), 0.0)


def sinz(amp, phase=0.0, offset=0.0, harmonic=1):
    return lambda p: (0.0, 0.0, offset + amp * math.sin(2 * math.pi * (harmonic * p + phase)))


def combo(*fns):
    def f(p):
        x = y = z = 0.0
        for g in fns:
            a, b, c = g(p)
            x += a; y += b; z += c
        return (x, y, z)
    return f


def track(rot=None, pos=None):
    t = {}
    if rot is not None:
        t["rotation"] = rot
    if pos is not None:
        t["position"] = pos
    return t


def keys(points):
    """Explicit keyframes: [(time, x, y, z), ...]"""
    return [[round(t, 4), x, y, z] for (t, x, y, z) in points]


# ---------------------------------------------------------------- saddle
def add_saddle(m, parent, top_y, z0, z1, width, body_half_width, flap=4):
    """Saddle bone sitting on the back (top_y = top surface of the body). Hidden in game unless saddled."""
    zc = (z0 + z1) / 2
    m.bone("saddle", parent, (0, top_y, zc))
    w = width
    m.box("saddle", (-w / 2, top_y - 1, z0), (w / 2, top_y + 1, z1), tag="saddle", name="seat")
    m.box("saddle", (-w / 2 + 1, top_y + 1, z1 - 1), (w / 2 - 1, top_y + 2, z1), tag="saddle", name="cantle")
    m.box("saddle", (-1, top_y + 1, z0), (1, top_y + 2, z0 + 1), tag="saddle", name="pommel")
    bw = body_half_width
    for sx in (1, -1):
        x0 = bw if sx > 0 else -bw - 1
        m.box("saddle", (x0, top_y - flap, zc - 1), (x0 + 1, top_y, zc + 1), tag="saddle", name="strap")
        m.box("saddle", (x0, top_y - flap - 1, zc - 1), (x0 + 1, top_y - flap, zc + 1), tag="saddle", name="buckle")


# ---------------------------------------------------------------- resting pose
def sit_tracks(length, drop, joints, breathe=0.25, extra=None):
    """
    Constant resting pose with a little breathing.
    drop   : how much the body (and the leg roots) go down, in px
    joints : {bone: (rot_x, rot_y, rot_z)} constant rotations (legs folded, tail down...)
    Leg root bones listed in 'roots' must also be moved down by 'drop'.
    """
    tracks = {}
    tracks["body"] = track(pos=keys([(0, 0, -drop, 0), (length / 2, 0, -drop + breathe, 0), (length, 0, -drop, 0)]),
                           rot=keys([(0, 0, 0, 0), (length / 2, 0.6, 0, 0), (length, 0, 0, 0)]))
    for bone, rot in joints.items():
        if bone.startswith("@"):  # '@bone' = leg root: move down with the body
            name = bone[1:]
            tracks[name] = track(rot=keys([(0, *rot), (length, *rot)]),
                                 pos=keys([(0, 0, -drop, 0), (length, 0, -drop, 0)]))
        else:
            tracks[bone] = track(rot=keys([(0, *rot), (length, *rot)]))
    if extra:
        tracks.update(extra)
    return tracks
