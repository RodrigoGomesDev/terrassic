"""
Pure Python stand-in for bbdriver.Blockbench: same interface (build, finish, set_texture, set_visible, shot), no
browser needed.  It reproduces what the headless Blockbench gives us:

  * build()   : the cube vertex dump used by paint.py (unposed and world positions + box UV of every face corner)
  * finish()  : the .bbmodel project, the GeckoLib/Bedrock .geo.json and the .animation.json
  * shot()    : preview renders (a small z-buffered software rasteriser, textured, with simple lighting),
                optionally posed at a time of an animation (catmull-rom keyframes, like GeckoLib)

Coordinates are Blockbench's ("B-space", see rig.py).  Bedrock files mirror X: pivots and cube origins get -x,
rotations get (-x, -y, z), animation positions (-x, y, z) and rotations (-x, -y, z).  tools/modelgen/README.md
explains when to use which backend; checks.py compares both outputs for the existing species.
"""
import base64
import io
import json
import math
import uuid

import numpy as np
from PIL import Image

FACE_ORDER = ["east", "west", "up", "down", "south", "north"]


# ------------------------------------------------------------------ math
def rot_matrix(rot_deg):
    """Blockbench / three.js Euler 'ZYX' (degrees): R = Rz * Ry * Rx."""
    x, y, z = (math.radians(a) for a in rot_deg)
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return rz @ ry @ rx


def affine(rot_deg, pivot):
    """4x4 matrix rotating about a pivot."""
    m = np.eye(4)
    r = rot_matrix(rot_deg)
    p = np.array(pivot, dtype=float)
    m[:3, :3] = r
    m[:3, 3] = p - r @ p
    return m


def translate(v):
    m = np.eye(4)
    m[:3, 3] = v
    return m


def num(v, digits=4):
    """JSON number the way Blockbench writes them: ints without .0, at most 4 decimals."""
    v = round(float(v), digits)
    if v == 0:
        return 0
    return int(v) if v == int(v) else v


# ------------------------------------------------------------------ box UV
def face_uv(face, uv, size):
    """UV rectangle (u0, v0, u1, v1) of a face for box UV at offset uv, like Blockbench / Minecraft."""
    u, v = uv
    w, h, d = size
    return {
        "north": (u + d, v + d, u + d + w, v + d + h),
        "east": (u, v + d, u + d, v + d + h),
        "south": (u + 2 * d + w, v + d, u + 2 * d + 2 * w, v + d + h),
        "west": (u + d + w, v + d, u + 2 * d + w, v + d + h),
        "up": (u + d, v, u + d + w, v + d),
        "down": (u + d + w, v, u + d + 2 * w, v + d),
    }[face]


def face_corners(face, lo, hi):
    """The 4 corners of a face as {(s, t): xyz}, s = 0 at the left of its UV rect, t = 0 at the top."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    if face == "north":   # seen from -Z: +X on the left
        return {(0, 0): (x1, y1, z0), (1, 0): (x0, y1, z0), (0, 1): (x1, y0, z0), (1, 1): (x0, y0, z0)}
    if face == "south":   # seen from +Z: -X on the left
        return {(0, 0): (x0, y1, z1), (1, 0): (x1, y1, z1), (0, 1): (x0, y0, z1), (1, 1): (x1, y0, z1)}
    if face == "east":    # seen from +X: +Z on the left
        return {(0, 0): (x1, y1, z1), (1, 0): (x1, y1, z0), (0, 1): (x1, y0, z1), (1, 1): (x1, y0, z0)}
    if face == "west":    # seen from -X: -Z on the left
        return {(0, 0): (x0, y1, z0), (1, 0): (x0, y1, z1), (0, 1): (x0, y0, z0), (1, 1): (x0, y0, z1)}
    if face == "up":      # seen from above, north at the bottom of the UV rect
        return {(0, 0): (x1, y1, z1), (1, 0): (x0, y1, z1), (0, 1): (x1, y1, z0), (1, 1): (x0, y1, z0)}
    if face == "down":    # seen from below, north at the bottom of the UV rect
        return {(0, 0): (x1, y0, z1), (1, 0): (x0, y0, z1), (0, 1): (x1, y0, z0), (1, 1): (x0, y0, z0)}
    raise ValueError(face)


# ------------------------------------------------------------------ rig evaluation
class Rig:
    def __init__(self, spec):
        self.spec = spec
        self.bones = {b["name"]: b for b in spec["bones"]}
        self.order = [b["name"] for b in spec["bones"]]  # parents always come first (rig.Model.bone)

    def bone_matrices(self, pose=None):
        """World matrix of every bone. pose = {bone: (rot_xyz_deg, pos_xyz_px[, scale_xyz])} added to the rest pose
        (GeckoLib order: move, then rotate and scale about the pivot)."""
        mats = {}
        for name in self.order:
            b = self.bones[name]
            rot = list(b["rotation"])
            off = [0.0, 0.0, 0.0]
            scale = (1.0, 1.0, 1.0)
            if pose and name in pose:
                r, p = pose[name][:2]
                rot = [rot[i] + r[i] for i in range(3)]
                off = list(p)
                if len(pose[name]) > 2:
                    scale = pose[name][2]
            local = translate(off) @ affine(rot, b["origin"])
            if scale != (1.0, 1.0, 1.0):
                sm = np.diag([scale[0], scale[1], scale[2], 1.0])
                piv = np.array(b["origin"], dtype=float)
                local = local @ translate(piv) @ sm @ translate(-piv)
            parent = mats[b["parent"]] if b["parent"] else np.eye(4)
            mats[name] = parent @ local
        return mats

    def cube_faces(self, pose=None, hidden=()):
        """[(cube, face, {(s,t): (local_xyz, world_xyz)}, uv_rect)] for every face of every visible cube."""
        mats = self.bone_matrices(pose)
        hidden_bones = set()
        for name in self.order:  # a hidden bone hides its children
            b = self.bones[name]
            if name in hidden or (b["parent"] in hidden_bones):
                hidden_bones.add(name)
        out = []
        for c in self.spec["cubes"]:
            if c["bone"] in hidden_bones:
                continue
            inf = c.get("inflate", 0.0) or 0.0
            lo = [c["from"][i] - inf for i in range(3)]
            hi = [c["to"][i] + inf for i in range(3)]
            size = [int(round(c["to"][i] - c["from"][i])) for i in range(3)]
            m = mats[c["bone"]] @ affine(c["rotation"], c["origin"])
            for face in FACE_ORDER:
                corners = {}
                for st, p in face_corners(face, lo, hi).items():
                    w = m @ np.array([p[0], p[1], p[2], 1.0])
                    corners[st] = (np.array(p, dtype=float) - np.array(c["origin"], dtype=float), w[:3])
                out.append((c, face, corners, face_uv(face, c["uv_offset"], size)))
        return out


# ------------------------------------------------------------------ animation sampling (catmull-rom, like GeckoLib)
def snap(t, snapping=20):
    return math.floor(t * snapping + 0.5) / snapping


def keyframes(track):
    """[(time, x, y, z)] sorted, times snapped to 1/20 s, later duplicates replacing earlier ones."""
    ks = {}
    for k in track:
        ks[snap(k[0])] = (k[1], k[2], k[3])
    return sorted((t, *v) for t, v in ks.items())


def sample(track, t):
    ks = keyframes(track)
    if not ks:
        return (0.0, 0.0, 0.0)
    if t <= ks[0][0]:
        return ks[0][1:]
    if t >= ks[-1][0]:
        return ks[-1][1:]
    for i in range(len(ks) - 1):
        if ks[i][0] <= t <= ks[i + 1][0]:
            p0 = np.array(ks[max(i - 1, 0)][1:])
            p1 = np.array(ks[i][1:])
            p2 = np.array(ks[i + 1][1:])
            p3 = np.array(ks[min(i + 2, len(ks) - 1)][1:])
            u = (t - ks[i][0]) / max(1e-9, ks[i + 1][0] - ks[i][0])
            v = 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)
            return tuple(v)
    return ks[-1][1:]


def pose_at(animation, t):
    pose = {}
    for bone, tracks in animation["bones"].items():
        r = sample(tracks["rotation"], t) if "rotation" in tracks else (0.0, 0.0, 0.0)
        p = sample(tracks["position"], t) if "position" in tracks else (0.0, 0.0, 0.0)
        sc = tuple(sample(tracks["scale"], t)) if "scale" in tracks else (1.0, 1.0, 1.0)
        pose[bone] = (r, p, sc)
    return pose


# ------------------------------------------------------------------ exporters
def outliner_order(spec):
    """Bones depth first, children in creation order (the order Blockbench exports them)."""
    children = {}
    for b in spec["bones"]:
        children.setdefault(b["parent"], []).append(b)
    out = []

    def visit(parent):
        for b in children.get(parent, []):
            out.append(b)
            visit(b["name"])
    visit(None)
    return out


def geo_json(spec, lo, hi):
    bones = []
    for b in outliner_order(spec):
        out = {"name": b["name"]}
        if b["parent"]:
            out["parent"] = b["parent"]
        out["pivot"] = [num(-b["origin"][0]), num(b["origin"][1]), num(b["origin"][2])]
        r = b["rotation"]
        if any(abs(a) > 1e-9 for a in r):
            out["rotation"] = [num(-r[0]), num(-r[1]), num(r[2])]
        cubes = []
        for c in spec["cubes"]:
            if c["bone"] != b["name"]:
                continue
            size = [int(round(c["to"][i] - c["from"][i])) for i in range(3)]
            cube = {"origin": [num(-c["to"][0]), num(c["from"][1]), num(c["from"][2])], "size": size}
            if c.get("inflate"):
                cube["inflate"] = num(c["inflate"])
            cr = c["rotation"]
            if any(abs(a) > 1e-9 for a in cr):
                cube["pivot"] = [num(-c["origin"][0]), num(c["origin"][1]), num(c["origin"][2])]
                cube["rotation"] = [num(-cr[0]), num(-cr[1]), num(cr[2])]
            cube["uv"] = list(c["uv_offset"])
            cubes.append(cube)
        if cubes:
            out["cubes"] = cubes
        bones.append(out)
    # visible box, as Blockbench computes it (in blocks, centred on x/z)
    lo8, hi8 = [v + 8 for v in lo], [v + 8 for v in hi]
    radius = max(hi8[0], hi8[2], -lo8[0], -lo8[2], 0.0)
    width = math.ceil(radius * 2 / 16)
    y_min = math.floor(lo8[1] / 16)
    y_max = math.ceil(hi8[1] / 16)
    desc = {"identifier": f"geometry.{spec['id']}", "texture_width": spec["texture_width"],
            "texture_height": spec["texture_height"], "visible_bounds_width": width,
            "visible_bounds_height": num(y_max - y_min + 0.5),
            "visible_bounds_offset": [0, num((y_min + y_max) / 2 - 0.25), 0]}
    return {"format_version": "1.12.0", "minecraft:geometry": [{"description": desc, "bones": bones}]}


def anim_json(spec):
    anims = {}
    for a in spec["animations"]:
        out = {}
        if a["loop"] == "loop":
            out["loop"] = True
        elif a["loop"] == "hold":
            out["loop"] = "hold_on_last_frame"
        out["animation_length"] = num(a["length"])
        bones = {}
        interp = a.get("interp", "catmullrom")
        for bone, tracks in a["bones"].items():
            bt = {}
            for channel in ("rotation", "position", "scale"):
                if channel not in tracks:
                    continue
                frames = {}
                for t, x, y, z in keyframes(tracks[channel]):
                    if channel == "rotation":
                        v = [num(-x), num(-y), num(z)]
                    elif channel == "position":
                        v = [num(-x), num(y), num(z)]
                    else:
                        v = [num(x), num(y), num(z)]
                    key = repr(round(t, 4))
                    frames[key] = v if interp == "linear" else {"post": v, "lerp_mode": interp}
                bt[channel] = frames
            bones[bone] = bt
        out["bones"] = bones
        anims[a["name"]] = out
    return {"format_version": "1.8.0", "animations": anims}


def bbmodel(spec, textures):
    """A Blockbench project (format 4.x) with the same groups, cubes, textures and animations."""
    uuids = {}
    elements, outliner = [], []
    groups = {}
    for b in spec["bones"]:
        g = {"name": b["name"], "origin": b["origin"], "rotation": b["rotation"], "color": 0,
             "uuid": str(uuid.uuid5(uuid.NAMESPACE_URL, spec["id"] + "/bone/" + b["name"])),
             "export": True, "isOpen": False, "locked": False, "visibility": True, "autouv": 0, "children": []}
        groups[b["name"]] = g
        uuids[b["name"]] = g["uuid"]
        (groups[b["parent"]]["children"] if b["parent"] else outliner).append(g)
    for i, c in enumerate(spec["cubes"]):
        cid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{spec['id']}/cube/{i}"))
        size = [int(round(c["to"][k] - c["from"][k])) for k in range(3)]
        faces = {}
        for f in FACE_ORDER:
            u0, v0, u1, v1 = face_uv(f, c["uv_offset"], size)
            faces[f] = {"uv": [u0, v0, u1, v1], "texture": 0}
        elements.append({"name": c["name"], "box_uv": True, "rescale": False, "locked": False, "from": c["from"], "to": c["to"],
                         "autouv": 0, "color": 0, "inflate": c.get("inflate", 0.0), "origin": c["origin"],
                         "rotation": c["rotation"], "uv_offset": c["uv_offset"], "faces": faces, "type": "cube", "uuid": cid})
        groups[c["bone"]]["children"].append(cid)
    tex = []
    for i, (name, png) in enumerate(textures):
        tex.append({"path": "", "name": name, "folder": "", "namespace": "", "id": str(i), "particle": False,
                    "render_mode": "default", "visible": True, "mode": "bitmap", "saved": True,
                    "uuid": str(uuid.uuid5(uuid.NAMESPACE_URL, spec["id"] + "/tex/" + name)),
                    "source": "data:image/png;base64," + base64.b64encode(png).decode()})
    animations = []
    for a in spec["animations"]:
        animators = {}
        for bone, tracks in a["bones"].items():
            kfs = []
            for channel in ("rotation", "position", "scale"):
                for t, x, y, z in keyframes(tracks.get(channel, [])):
                    kfs.append({"channel": channel, "data_points": [{"x": x, "y": y, "z": z}], "time": t, "color": -1,
                                "interpolation": a.get("interp", "catmullrom"),
                                "uuid": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{a['name']}/{bone}/{channel}/{t}"))})
            animators[uuids[bone]] = {"name": bone, "type": "bone", "keyframes": kfs}
        animations.append({"uuid": str(uuid.uuid5(uuid.NAMESPACE_URL, a["name"])), "name": a["name"],
                           "loop": a["loop"], "override": False, "length": a["length"], "snapping": 20,
                           "selected": False, "anim_time_update": "", "blend_weight": "", "start_delay": "",
                           "loop_delay": "", "animators": animators})
    return {"meta": {"format_version": "4.5", "model_format": "bedrock", "box_uv": True},
            "name": spec["id"], "model_identifier": spec["id"], "visible_box": [1, 1, 0],
            "variable_placeholders": "", "variable_placeholder_buttons": [],
            "resolution": {"width": spec["texture_width"], "height": spec["texture_height"]},
            "elements": elements, "outliner": outliner, "textures": tex, "animations": animations}


# ------------------------------------------------------------------ preview renderer
def render(rig, texture, cam, size=(816, 816), pose=None, hidden=(), zoom=1.45):
    """Perspective software render of the textured model (white background, soft light)."""
    W, H = size
    tex = np.asarray(texture.convert("RGBA"), dtype=float)
    th, tw = tex.shape[:2]
    pos = np.array(cam["position"], dtype=float)
    tgt = np.array(cam["target"], dtype=float)
    fwd = tgt - pos
    fwd /= np.linalg.norm(fwd)
    up0 = np.array([0.0, 1.0, 0.0])
    if abs(np.dot(fwd, up0)) > 0.99:
        up0 = np.array([0.0, 0.0, -1.0])
    right = np.cross(fwd, up0)
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    f = zoom / math.tan(math.radians(cam.get("fov", 40)) / 2)
    img = np.full((H, W, 3), 255.0)
    zbuf = np.full((H, W), np.inf)
    light = np.array([0.4, 0.8, -0.45])
    light /= np.linalg.norm(light)

    def project(p):
        d = p - pos
        z = np.dot(d, fwd)
        x = np.dot(d, right) / z * f
        y = np.dot(d, up) / z * f
        return np.array([W / 2 + x * H / 2, H / 2 - y * H / 2, z])

    for c, face, corners, (u0, v0, u1, v1) in rig.cube_faces(pose, hidden):
        if u1 <= u0 or v1 <= v0:
            continue
        P = {st: project(w) for st, (_l, w) in corners.items()}
        n = np.cross(corners[(1, 0)][1] - corners[(0, 0)][1], corners[(0, 1)][1] - corners[(0, 0)][1])
        nn = np.linalg.norm(n)
        if nn < 1e-9:
            continue
        n /= nn
        shade = min(1.08, 0.74 + 0.30 * max(0.0, float(np.dot(n, light))) + 0.08 * max(0.0, float(n[1])))
        for tri in (((0, 0), (1, 0), (1, 1)), ((0, 0), (1, 1), (0, 1))):
            a, b, cc = (P[k] for k in tri)
            if min(a[2], b[2], cc[2]) <= 1e-3:
                continue
            xs = (a[0], b[0], cc[0])
            ys = (a[1], b[1], cc[1])
            x0, x1 = max(0, int(min(xs))), min(W - 1, int(max(xs)) + 1)
            y0, y1 = max(0, int(min(ys))), min(H - 1, int(max(ys)) + 1)
            if x0 > x1 or y0 > y1:
                continue
            den = (b[1] - cc[1]) * (a[0] - cc[0]) + (cc[0] - b[0]) * (a[1] - cc[1])
            if abs(den) < 1e-9:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            l1 = ((b[1] - cc[1]) * (gx - cc[0]) + (cc[0] - b[0]) * (gy - cc[1])) / den
            l2 = ((cc[1] - a[1]) * (gx - cc[0]) + (a[0] - cc[0]) * (gy - cc[1])) / den
            l3 = 1 - l1 - l2
            inside = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
            if not inside.any():
                continue
            iz = l1 / a[2] + l2 / b[2] + l3 / cc[2]
            z = 1.0 / iz
            st = [np.array(k, dtype=float) for k in tri]
            s = (l1 * st[0][0] / a[2] + l2 * st[1][0] / b[2] + l3 * st[2][0] / cc[2]) * z
            t = (l1 * st[0][1] / a[2] + l2 * st[1][1] / b[2] + l3 * st[2][1] / cc[2]) * z
            tu = np.clip((u0 + s * (u1 - u0)).astype(int), 0, tw - 1)
            tv = np.clip((v0 + t * (v1 - v0)).astype(int), 0, th - 1)
            col = tex[tv, tu]
            sub = zbuf[y0:y1 + 1, x0:x1 + 1]
            ok = inside & (z < sub) & (col[..., 3] > 10)
            sub[ok] = z[ok]
            img[y0:y1 + 1, x0:x1 + 1][ok] = col[..., :3][ok] * shade
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")
    return out


class PyBench:
    """Drop-in replacement of bbdriver.Blockbench (async interface kept so build_all.py can use either)."""

    def __init__(self):
        self.errors = []
        self.rig = None
        self.spec = None
        self.textures = []
        self.current = 0
        self.hidden = set()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def build(self, spec):
        self.spec = spec
        self.rig = Rig(spec)
        self.hidden = set()
        dump = []
        faces = self.rig.cube_faces()
        for ci, c in enumerate(spec["cubes"]):
            verts = []
            for c2, face, corners, (u0, v0, u1, v1) in faces[ci * 6:(ci + 1) * 6]:
                for (s, t), (l, w) in corners.items():
                    verts.append({"l": list(map(float, l)), "w": list(map(float, w)),
                                  "uv": [u0 + s * (u1 - u0), v0 + t * (v1 - v0)]})
            dump.append({"name": c["name"], "from": c["from"], "to": c["to"], "order": FACE_ORDER, "verts": verts})
        return dump

    async def finish(self, spec, png_bytes, extra=None):
        self.textures = [(f"{spec['id']}_male.png", png_bytes)] + list(extra or [])
        self.current = 0
        lo, hi = self.bounds()
        return {"bbmodel": json.dumps(bbmodel(spec, self.textures)),
                "geo": json.dumps(geo_json(spec, lo, hi)),
                "anim": json.dumps(anim_json(spec))}

    def bounds(self):
        pts = [w for _c, _f, corners, _uv in self.rig.cube_faces() for _l, w in corners.values()]
        a = np.array(pts)
        return list(a.min(axis=0)), list(a.max(axis=0))

    async def set_texture(self, index):
        self.current = index

    async def set_visible(self, bone, visible):
        if visible:
            self.hidden.discard(bone)
        else:
            self.hidden.add(bone)

    async def shot(self, cam, anim=None, time=0.0):
        pose = None
        if anim:
            a = next(a for a in self.spec["animations"] if a["name"] == anim)
            pose = pose_at(a, time)
        tex = Image.open(io.BytesIO(self.textures[self.current][1]))
        img = render(self.rig, tex, cam, pose=pose, hidden=self.hidden)
        b = io.BytesIO()
        img.save(b, "PNG")
        return b.getvalue()
