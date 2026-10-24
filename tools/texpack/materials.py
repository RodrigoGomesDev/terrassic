"""Materials: what each texture is made of, and which vanilla texture it is measured against.

A Material says: aim luma and contrast at the vanilla texture `ref` (vanilla.py), nudged by dl/dc for the era's
look, painted with our own hue and saturation (HSV), with hue shift (shadows cooler, lights warmer) and a number
of tones. Vanilla materials point at themselves; the mod's own materials point at the closest vanilla relative,
so a Terrassic block never looks out of place next to a vanilla one. To add a material, add a line here (or ask
the texture thread for one); never change the numbers in vanilla.py."""
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Material:
    ref: str                # vanilla texture whose numbers we aim at
    hue: float              # HSV hue 0..1 of the middle tone
    sat: float              # HSV saturation of the middle tone
    hue_shift: float = .02  # shadows rotate by -hue_shift, lights by +hue_shift
    sat_shift: float = .04  # shadows gain, lights lose this much saturation
    dl: float = -3.0        # era nudge on the luma mean (Cretaceous: a touch darker, weathered)
    dc: float = 0.0         # nudge on the contrast
    n: int = 5              # tones in the ramp
    gamma: float = 1.0      # <1 packs the light tones together (boards with dark gaps, for instance)

    def like(self, **kw):
        return replace(self, **kw)


M = Material
MATERIALS = {
    # ---- stone and earth (vanilla references are the blocks themselves)
    "stone": M("stone", .08, .045, dl=-4, dc=2, n=4),
    "cobblestone": M("cobblestone", .08, .035, dl=-4, n=6),
    "andesite": M("andesite", .07, .05, n=5),
    "tuff": M("tuff", .12, .08, n=5),
    "deepslate": M("deepslate", .62, .05, n=5),
    "calcite": M("calcite", .12, .04, n=5),
    "dirt": M("dirt", .055, .42, n=5),
    "mud": M("mud", .07, .25, n=5),
    "clay": M("clay", .60, .08, n=5),
    "sand": M("sand", .12, .30, n=5),
    "gravel": M("gravel", .08, .06, n=5),
    "mud_bricks": M("mud_bricks", .07, .40, n=6),
    "packed_mud": M("packed_mud", .07, .42, n=5),
    "bricks": M("bricks", .03, .45, n=6),
    "terracotta": M("terracotta", .05, .50, n=4),
    # ---- the mod's rocks
    "chalk": M("calcite", .12, .05, dc=-25),
    "limestone": M("calcite", .11, .10, dl=-40, dc=-15),
    "quartzite": M("diorite", .05, .06, dc=-25),
    "gneiss": M("andesite", .08, .06, dc=15, n=6),
    "shale": M("deepslate", .60, .07),
    "flint": M("deepslate", .08, .12, dl=-25, dc=-10),
    "conglomerate": M("cobblestone", .08, .12, n=6),
    "laterite": M("granite", .04, .55, n=6),
    "basalt": M("basalt_side", .65, .06),
    "obsidian_glass": M("obsidian", .75, .45, dl=8),
    # ---- organic
    "amber": M("honey_block_side", .085, .85, dl=-35, dc=10, hue_shift=.03, sat_shift=-.05),
    "resin": M("honeycomb_block", .10, .75, dl=-10, hue_shift=.03),
    "bone": M("bone_block_top", .12, .14, hue_shift=.015, sat_shift=.03),
    "bone_side": M("bone_block_side", .12, .12, dc=8),
    "reed": M("hay_block_side", .20, .45, n=5),
    "thatch": M("hay_block_top", .13, .55, n=5),
    "wicker": M("hay_block_side", .10, .50, dl=-15, n=5),
    "tanned_hide": M("brown_wool", .07, .50, dl=10, dc=10),
    "scaled_hide": M("brown_wool", .10, .35, dl=15, dc=20, n=6),
    "feathers": M("white_wool", .10, .06, dl=-25, dc=10),
    "moss": M("moss_block", .22, .58),
    # ---- woods: vanilla wood X has X_bark, X_rings, X_stripped, X_stripped_rings, X_planks
}

# vanilla woods: hue and saturation of the wood (bark may differ, see woods.WOODS)
_WOODS = {"oak": (.090, .46), "spruce": (.075, .55), "birch": (.115, .30), "jungle": (.095, .55),
          "acacia": (.055, .62), "dark_oak": (.080, .58), "mangrove": (.010, .55), "cherry": (.985, .30)}
for _w, (_h, _s) in _WOODS.items():
    MATERIALS[f"{_w}_bark"] = M(f"{_w}_log", _h, _s, n=6, sat_shift=.06)
    MATERIALS[f"{_w}_rings"] = M(f"{_w}_log_top", _h, _s)
    MATERIALS[f"{_w}_stripped"] = M(f"stripped_{_w}_log", _h, _s, n=4, hue_shift=.012)
    MATERIALS[f"{_w}_stripped_rings"] = M(f"stripped_{_w}_log_top", _h, _s)
    MATERIALS[f"{_w}_planks"] = M(f"{_w}_planks", _h, _s, gamma=.55)


def material(name_or_mat):
    return name_or_mat if isinstance(name_or_mat, Material) else MATERIALS[name_or_mat]
