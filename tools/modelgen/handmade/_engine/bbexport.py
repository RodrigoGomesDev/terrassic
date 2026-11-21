"""The Blockbench project of a hand-made rig, rebuilt from the files the game loads (the exported geo.json, the
animation.json and the skins), so art/<species>/<species>.bbmodel shows what is in the mod.

Bedrock mirrors X against Blockbench: pivots and cube origins get -x, rotations (-x, -y, z), animation rotations
(-x, -y, z) and positions (-x, y, z) (the same rule as tools/modelgen/pybench.py). Per-face UV (box_uv off); east and
west swap back, the UV numbers are kept as exported.

usage:  python3 -B tools/modelgen/handmade/_engine/bbexport.py maiasaura [male female baby]
"""
import base64
import json
import os
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
SWAP = {"east": "west", "west": "east"}


def _uid(*a):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "/".join(str(x) for x in a)))


def _vec(v):
    if isinstance(v, dict):
        v = v.get("post", v.get("vector", v.get("pre")))
    return [float(x) for x in v]


def build(sp, skins=("male", "female", "baby")):
    geo = json.load(open(os.path.join(ASSETS, "geo", "entity", f"{sp}.geo.json")))["minecraft:geometry"][0]
    anims = json.load(open(os.path.join(ASSETS, "animations", "entity", f"{sp}.animation.json")))["animations"]
    d = geo["description"]
    groups, outliner, elements = {}, [], []
    for b in geo["bones"]:
        r = b.get("rotation", [0, 0, 0])
        g = {"name": b["name"], "origin": [-b["pivot"][0], b["pivot"][1], b["pivot"][2]],
             "rotation": [-r[0], -r[1], r[2]], "color": 0, "uuid": _uid(sp, "bone", b["name"]), "export": True,
             "isOpen": False, "locked": False, "visibility": True, "autouv": 0, "children": []}
        groups[b["name"]] = g
        (groups[b["parent"]]["children"] if b.get("parent") else outliner).append(g)
        for i, c in enumerate(b.get("cubes", [])):
            o, s = c["origin"], c["size"]
            frm = [-(o[0] + s[0]), o[1], o[2]]
            to = [-o[0], o[1] + s[1], o[2] + s[2]]
            pv = c.get("pivot", [-to[0], frm[1], frm[2]])
            rr = c.get("rotation", [0, 0, 0])
            faces = {}
            for f, uv in c["uv"].items():
                (u, v), (w, h) = uv["uv"], uv["uv_size"]
                faces[SWAP.get(f, f)] = {"uv": [u, v, u + w, v + h], "texture": 0}
            cid = _uid(sp, "cube", b["name"], i)
            elements.append({"name": f"{b['name']}_{i}", "box_uv": False, "rescale": False, "locked": False,
                             "from": frm, "to": to, "autouv": 0, "color": 0, "inflate": c.get("inflate", 0),
                             "origin": [-pv[0], pv[1], pv[2]], "rotation": [-rr[0], -rr[1], rr[2]],
                             "faces": faces, "type": "cube", "uuid": cid})
            g["children"].append(cid)
    tex = []
    for i, s in enumerate(skins):
        p = os.path.join(ASSETS, "textures", "entity", f"{sp}_{s}.png")
        if not os.path.exists(p):
            continue
        tex.append({"path": "", "name": f"{sp}_{s}.png", "folder": "", "namespace": "", "id": str(len(tex)),
                    "particle": False, "render_mode": "default", "visible": True, "mode": "bitmap", "saved": True,
                    "width": d["texture_width"], "height": d["texture_height"], "uuid": _uid(sp, "tex", s),
                    "source": "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()})
    animations = []
    for name, a in anims.items():
        animators = {}
        for bone, tracks in a.get("bones", {}).items():
            if bone not in groups:
                continue
            kfs = []
            for ch in ("rotation", "position", "scale"):
                tr = tracks.get(ch)
                if tr is None:
                    continue
                items = tr.items() if isinstance(tr, dict) and not {"post", "vector", "pre"} & set(tr) else [("0", tr)]
                for t, v in items:
                    x, y, z = _vec(v)
                    if ch == "rotation":
                        x, y = -x, -y
                    elif ch == "position":
                        x = -x
                    lerp = v.get("lerp_mode", "linear") if isinstance(v, dict) else "linear"
                    kfs.append({"channel": ch, "data_points": [{"x": x, "y": y, "z": z}], "time": float(t),
                                "color": -1, "interpolation": lerp, "uuid": _uid(name, bone, ch, t)})
            animators[groups[bone]["uuid"]] = {"name": bone, "type": "bone", "keyframes": kfs}
        animations.append({"uuid": _uid(name), "name": name, "loop": "loop" if a.get("loop") else "once",
                           "override": False, "length": a.get("animation_length", 0), "snapping": 20,
                           "selected": False, "anim_time_update": "", "blend_weight": "", "start_delay": "",
                           "loop_delay": "", "animators": animators})
    return {"meta": {"format_version": "4.5", "model_format": "animated_entity_model", "box_uv": False},
            "name": sp, "model_identifier": sp, "visible_box": [1, 1, 0], "variable_placeholders": "",
            "variable_placeholder_buttons": [],
            "resolution": {"width": d["texture_width"], "height": d["texture_height"]},
            "elements": elements, "outliner": outliner, "textures": tex, "animations": animations}


if __name__ == "__main__":
    sp = sys.argv[1]
    skins = tuple(sys.argv[2:]) or ("male", "female", "baby")
    out = os.path.join(ROOT, "art", sp, f"{sp}.bbmodel")
    with open(out, "w") as f:
        json.dump(build(sp, skins), f, separators=(",", ":"))
    print(out, os.path.getsize(out) // 1024, "KB")
