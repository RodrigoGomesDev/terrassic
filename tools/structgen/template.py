"""Structure templates built by code (v0.8, phase M3): a small block-placing API, validated against the mod's
blockstate files, written as vanilla .nbt structure files (DataVersion of Minecraft 1.20.1).

    t = Template(9, 6, 9)
    t.set(4, 1, 4, "terrassic:stone_hearth", facing="south")
    t.fill(0, 0, 0, 8, 0, 8, "terrassic:packed_earth_floor")
    t.basket(5, 1, 2, "terrassic:chests/katarina_camp")
    t.entity(4.5, 1, 6.5, {"id": "terrassic:compsognathus"})
    t.save("…/data/terrassic/structures/katarina_camp/reed.nbt")

Positions not set stay "structure void": the terrain there is kept. Set "minecraft:air" to clear a block.
"""
import json
import os

from nbt import IntArray, write  # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ASSETS = os.path.join(ROOT, "common", "src", "main", "resources", "assets", "terrassic")
DATA_VERSION = 3465  # Minecraft 1.20.1

_STATES = {}


def _terrassic_states(block):
    """Allowed {property: {values}} of a terrassic block, read from its blockstate file."""
    if block in _STATES:
        return _STATES[block]
    path = os.path.join(ASSETS, "blockstates", block + ".json")
    if not os.path.exists(path):
        raise ValueError(f"unknown block terrassic:{block}")
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    props = {}

    def add(cond):
        for k, v in cond.items():
            if k in ("OR", "AND"):
                for c in v:
                    add(c)
                continue
            props.setdefault(k, set()).update(str(v).split("|"))
    if "variants" in d:
        for key in d["variants"]:
            for part in filter(None, key.split(",")):
                k, v = part.split("=")
                props.setdefault(k, set()).add(v)
    else:
        for p in d["multipart"]:
            if "when" in p:
                add(p["when"])
    _STATES[block] = props
    return props


class Template:
    def __init__(self, sx, sy, sz):
        self.size = (sx, sy, sz)
        self.blocks = {}
        self.entities = []

    def inside(self, x, y, z):
        return 0 <= x < self.size[0] and 0 <= y < self.size[1] and 0 <= z < self.size[2]

    def set(self, x, y, z, block, nbt=None, **props):
        if not self.inside(x, y, z):
            raise ValueError(f"{block} at {(x, y, z)} is outside the template {self.size}")
        name = block if ":" in block else "terrassic:" + block
        if name.startswith("terrassic:"):
            allowed = _terrassic_states(name.split(":", 1)[1])
            for k, v in props.items():
                if k not in allowed or str(v).lower() not in allowed[k]:
                    raise ValueError(f"{name}: bad property {k}={v} (allowed {allowed})")
        state = (name, tuple(sorted((k, str(v).lower()) for k, v in props.items())))
        self.blocks[(x, y, z)] = (state, nbt)

    def get(self, x, y, z):
        b = self.blocks.get((x, y, z))
        return b[0][0] if b else None

    def fill(self, x0, y0, z0, x1, y1, z1, block, **props):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.set(x, y, z, block, **props)

    def clear(self, x0, y0, z0, x1, y1, z1):
        self.fill(x0, y0, z0, x1, y1, z1, "minecraft:air")

    def basket(self, x, y, z, loot, facing="north"):
        """A wicker basket (9 slots) filled from a loot table when first opened, per vanilla rules."""
        self.set(x, y, z, "terrassic:wicker_basket", nbt={"id": "terrassic:wicker_basket", "LootTable": loot},
                 facing=facing)

    def entity(self, x, y, z, nbt):
        self.entities.append(((float(x), float(y), float(z)), nbt))

    def to_nbt(self):
        palette, index = [], {}
        blocks = []
        for (x, y, z), (state, nbt) in sorted(self.blocks.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
            if state not in index:
                index[state] = len(palette)
                entry = {"Name": state[0]}
                if state[1]:
                    entry["Properties"] = {k: v for k, v in state[1]}
                palette.append(entry)
            b = {"pos": [x, y, z], "state": index[state]}
            if nbt:
                b["nbt"] = nbt
            blocks.append(b)
        ents = []
        for (x, y, z), nbt in self.entities:
            ents.append({"pos": [x, y, z], "blockPos": [int(x), int(y), int(z)], "nbt": nbt})
        root = {"DataVersion": DATA_VERSION, "size": list(self.size), "palette": palette, "blocks": blocks}
        if ents:
            root["entities"] = ents
        else:
            root["entities"] = []
        return root

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        write(path, self.to_nbt())
