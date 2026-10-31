"""Load Bedrock/GeckoLib geo + animation json into a B-space spec; pose; render with Minecraft-like flat shading."""
import json, math
import numpy as np
from PIL import Image

def rot_matrix(r):
    x, y, z = (math.radians(a) for a in r)
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    rx = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]); ry = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]); rz = np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
    return rz @ ry @ rx

def T(v):
    m = np.eye(4); m[:3, 3] = v; return m

def affine(r, p):
    m = np.eye(4); m[:3, :3] = rot_matrix(r); return T(p) @ m @ T(-np.array(p, float))

FACES = ["north", "south", "east", "west", "up", "down"]

def box_uv(face, uv, size):
    u, v = uv; w, h, d = size
    return {"north": (u+d, v+d, w, h), "east": (u, v+d, d, h), "south": (u+2*d+w, v+d, w, h),
            "west": (u+d+w, v+d, d, h), "up": (u+d, v, w, d), "down": (u+d+w, v, w, d)}[face]

def corners(face, lo, hi):
    x0, y0, z0 = lo; x1, y1, z1 = hi
    return {"north": {(0,0):(x1,y1,z0),(1,0):(x0,y1,z0),(0,1):(x1,y0,z0),(1,1):(x0,y0,z0)},
            "south": {(0,0):(x0,y1,z1),(1,0):(x1,y1,z1),(0,1):(x0,y0,z1),(1,1):(x1,y0,z1)},
            "east":  {(0,0):(x1,y1,z1),(1,0):(x1,y1,z0),(0,1):(x1,y0,z1),(1,1):(x1,y0,z0)},
            "west":  {(0,0):(x0,y1,z0),(1,0):(x0,y1,z1),(0,1):(x0,y0,z0),(1,1):(x0,y0,z1)},
            "up":    {(0,0):(x1,y1,z1),(1,0):(x0,y1,z1),(0,1):(x1,y1,z0),(1,1):(x0,y1,z0)},
            "down":  {(0,0):(x1,y0,z1),(1,0):(x0,y0,z1),(0,1):(x1,y0,z0),(1,1):(x0,y0,z0)}}[face]

def load_geo(path):
    g = json.load(open(path))["minecraft:geometry"][0]
    bones, cubes = [], []
    for b in g["bones"]:
        p = b.get("pivot", [0,0,0]); r = b.get("rotation", [0,0,0])
        bones.append({"name": b["name"], "parent": b.get("parent"), "origin": [-p[0], p[1], p[2]], "rotation": [-r[0], -r[1], r[2]]})
        for i, c in enumerate(b.get("cubes", [])):
            o, s = c["origin"], c["size"]
            frm = [-(o[0]+s[0]), o[1], o[2]]; to = [frm[0]+s[0], o[1]+s[1], o[2]+s[2]]
            cp = c.get("pivot", [0,0,0]); cr = c.get("rotation", [0,0,0])
            uv = c.get("uv", [0,0])
            if isinstance(uv, dict):
                fu = {}
                for f, v in uv.items():
                    a, bb, w, h = v["uv"][0], v["uv"][1], v["uv_size"][0], v["uv_size"][1]
                    if f in ("east", "west"):
                        # read the way GeckoLib draws it: bedrock x is mirrored and side faces run u the other way
                        f = {"east": "west", "west": "east"}[f]; a, w = a + w, -w
                    fu[f] = (a, bb, w, h)
            else:
                fu = {f: box_uv(f, uv, [int(round(x)) for x in s]) for f in FACES}
                if c.get("mirror"):
                    fu = {f: (a+w, bb, -w, h) for f, (a, bb, w, h) in fu.items()}
                    fu["east"], fu["west"] = fu["west"], fu["east"]
            cubes.append({"bone": b["name"], "name": f'{b["name"]}#{i}', "from": frm, "to": to, "inflate": c.get("inflate", 0) or 0,
                          "origin": [-cp[0], cp[1], cp[2]], "rotation": [-cr[0], -cr[1], cr[2]], "uv": fu})
    return {"bones": bones, "cubes": cubes, "tw": g["description"]["texture_width"], "th": g["description"]["texture_height"]}

def _vec(v):
    if isinstance(v, dict):
        v = v.get("post", v.get("vector", v.get("pre")))
    if isinstance(v, (int, float)): v = [v, v, v]
    return [float(x) if not isinstance(x, str) else 0.0 for x in v]

def load_anims(path):
    a = json.load(open(path))["animations"]; out = {}
    for name, an in a.items():
        bones = {}
        for bn, tr in an.get("bones", {}).items():
            d = {}
            for ch in ("rotation", "position"):
                if ch in tr:
                    v = tr[ch]
                    if isinstance(v, dict) and not ("post" in v or "vector" in v):
                        ks = sorted((float(t), _vec(x), isinstance(x, dict) and x.get("lerp_mode") == "linear") for t, x in v.items())
                    else:
                        ks = [(0.0, _vec(v), False)]
                    if ch == "rotation": ks = [(t, [-x[0], -x[1], x[2]], l) for t, x, l in ks]
                    else: ks = [(t, [-x[0], x[1], x[2]], l) for t, x, l in ks]
                    d[ch] = ks
            bones[bn] = d
        out[name.split(".")[-1]] = {"length": float(an.get("animation_length", 1.0)), "bones": bones}
    return out

def sample(ks, t):
    if not ks: return [0,0,0]
    if t <= ks[0][0]: return ks[0][1]
    if t >= ks[-1][0]: return ks[-1][1]
    for i in range(len(ks)-1):
        if ks[i][0] <= t <= ks[i+1][0]:
            p0 = np.array(ks[max(i-1,0)][1]); p1 = np.array(ks[i][1]); p2 = np.array(ks[i+1][1]); p3 = np.array(ks[min(i+2,len(ks)-1)][1])
            u = (t-ks[i][0])/max(1e-9, ks[i+1][0]-ks[i][0])
            if len(ks[i+1]) > 2 and ks[i+1][2]: return list(p1 + (p2 - p1) * u)
            return list(0.5*((2*p1)+(-p0+p2)*u+(2*p0-5*p1+4*p2-p3)*u*u+(-p0+3*p1-3*p2+p3)*u**3))
    return ks[-1][1]

def pose_at(anim, t):
    return {b: (sample(tr.get("rotation", []), t), sample(tr.get("position", []), t)) for b, tr in anim["bones"].items()}

def bone_mats(spec, pose=None):
    mats = {}
    for b in spec["bones"]:
        rot = list(b["rotation"]); off = [0,0,0]; scl = None
        if pose and b["name"] in pose:
            e = pose[b["name"]]; r, p = e[0], e[1]; rot = [rot[i]+r[i] for i in range(3)]; off = p
            if len(e) > 2 and e[2] is not None: scl = e[2]
        local = T(off) @ affine(rot, b["origin"])
        if scl is not None:
            o = np.array(b["origin"], float); S_ = np.eye(4); S_[0, 0], S_[1, 1], S_[2, 2] = scl
            local = local @ T(o) @ S_ @ T(-o)
        mats[b["name"]] = (mats[b["parent"]] if b["parent"] else np.eye(4)) @ local
    return mats

def faces(spec, pose=None, hidden=()):
    mats = bone_mats(spec, pose); hid = set()
    for b in spec["bones"]:
        if b["name"] in hidden or b["parent"] in hid: hid.add(b["name"])
    out = []
    for c in spec["cubes"]:
        if c["bone"] in hid: continue
        inf = c["inflate"]; lo = [c["from"][i]-inf for i in range(3)]; hi = [c["to"][i]+inf for i in range(3)]
        m = mats[c["bone"]] @ affine(c["rotation"], c["origin"])
        for f in FACES:
            if f not in c["uv"]: continue
            cs = {st: (m @ np.array([*p, 1.0]))[:3] for st, p in corners(f, lo, hi).items()}
            out.append((c, f, cs, c["uv"][f]))
    return out

def cube_points(spec, pose=None, hidden=()):
    mats = bone_mats(spec, pose); res = []
    for c in spec["cubes"]:
        if c["bone"] in hidden: continue
        lo, hi = c["from"], c["to"]; m = mats[c["bone"]] @ affine(c["rotation"], c["origin"])
        pts = [(m @ np.array([x, y, z, 1.0]))[:3] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
        res.append((c, np.array(pts)))
    return res

SHADE = {"up": 1.0, "down": 0.5, "north": 0.8, "south": 0.8, "east": 0.6, "west": 0.6}

def render(spec, tex, yaw=35, pitch=20, size=(700, 520), pose=None, hidden=(), fit=None, bg=(255,255,255), ortho=True, ground=None, extra=None, margin=0.08):
    """Orthographic render; Minecraft entity lighting approximated by face-normal shading (top bright, sides darker)."""
    W, H = size
    tex = np.asarray(tex.convert("RGBA"), float); th, tw = tex.shape[:2]
    sx, sy = tw / spec["tw"], th / spec["th"]
    yr, pr = math.radians(yaw), math.radians(pitch)
    # camera basis: looking at the model from direction (yaw around Y, pitch down)
    fwd = np.array([math.sin(yr)*math.cos(pr), -math.sin(pr), -math.cos(yr)*math.cos(pr)])*-1  # from camera to target
    fwd = -np.array([-math.sin(yr)*math.cos(pr), math.sin(pr), -math.cos(yr)*math.cos(pr)])
    up0 = np.array([0,1.0,0]); right = np.cross(fwd, up0); right /= np.linalg.norm(right); up = np.cross(right, fwd)
    F = faces(spec, pose, hidden) + (extra or [])
    pts = np.array([p for _c, _f, cs, _u in F for p in cs.values()])
    X = pts @ right; Y = pts @ up
    if fit is None:
        fit = (X.min(), X.max(), Y.min(), Y.max())
    x0, x1, y0, y1 = fit
    sc = min(W*(1-2*margin)/(x1-x0), H*(1-2*margin)/(y1-y0))
    cx, cy = (x0+x1)/2, (y0+y1)/2
    img = np.zeros((H, W, 3)); img[:] = bg; zb = np.full((H, W), np.inf)
    light_dirs = {}
    for c, f, cs, rect in F:
        u0, v0, uw, vh = rect
        if uw == 0 or vh == 0: continue
        P = {st: np.array([W/2 + (p@right - cx)*sc, H/2 - (p@up - cy)*sc, p@fwd]) for st, p in cs.items()}
        n = np.cross(cs[(1,0)]-cs[(0,0)], cs[(0,1)]-cs[(0,0)]); nn = np.linalg.norm(n)
        if nn < 1e-9: continue
        n /= nn
        # back-face cull (normals point outward because of corner order)
        pass
        # minecraft-ish: blend of axis shades by normal
        shade = 0.5*max(0,-n[1]) + 1.0*max(0,n[1]) + 0.8*abs(n[2]) + 0.6*abs(n[0])
        shade /= max(1e-6, abs(n[0])+abs(n[1])+abs(n[2]))
        shade = 0.25 + 0.75*shade
        tint = c.get("tint")
        for tri in (((0,0),(1,0),(1,1)), ((0,0),(1,1),(0,1))):
            a, b, cc = (P[k] for k in tri)
            xs = (a[0], b[0], cc[0]); ys = (a[1], b[1], cc[1])
            X0, X1 = max(0, int(min(xs))), min(W-1, int(max(xs))+1); Y0, Y1 = max(0, int(min(ys))), min(H-1, int(max(ys))+1)
            if X0 > X1 or Y0 > Y1: continue
            den = (b[1]-cc[1])*(a[0]-cc[0]) + (cc[0]-b[0])*(a[1]-cc[1])
            if abs(den) < 1e-9: continue
            gx, gy = np.meshgrid(np.arange(X0, X1+1)+0.5, np.arange(Y0, Y1+1)+0.5)
            l1 = ((b[1]-cc[1])*(gx-cc[0]) + (cc[0]-b[0])*(gy-cc[1]))/den
            l2 = ((cc[1]-a[1])*(gx-cc[0]) + (a[0]-cc[0])*(gy-cc[1]))/den
            l3 = 1-l1-l2
            inside = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
            if not inside.any(): continue
            z = l1*a[2] + l2*b[2] + l3*cc[2]
            st = [np.array(k, float) for k in tri]
            s = l1*st[0][0] + l2*st[1][0] + l3*st[2][0]; t = l1*st[0][1] + l2*st[1][1] + l3*st[2][1]
            U = u0 + np.clip(s, 0, 1)*uw; V = v0 + np.clip(t, 0, 1)*vh
            fu = np.floor(U*sx - 1e-4) if uw > 0 else np.ceil(U*sx + 1e-4) - 1
            fu = np.clip(fu, min(u0, u0+uw)*sx, max(u0, u0+uw)*sx - 1)
            fv = np.clip(np.floor(V*sy - 1e-4), min(v0, v0+vh)*sy, max(v0, v0+vh)*sy - 1)
            tu = np.clip(fu.astype(int), 0, tw-1); tv = np.clip(fv.astype(int), 0, th-1)
            col = tex[tv, tu]
            sub = zb[Y0:Y1+1, X0:X1+1]
            ok = inside & (z < sub - 1e-4) & (col[..., 3] > 10)
            sub[ok] = z[ok]
            cl = col[..., :3]*shade
            if tint is not None: cl = cl*np.array(tint)
            img[Y0:Y1+1, X0:X1+1][ok] = cl[ok]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)), fit, sc
