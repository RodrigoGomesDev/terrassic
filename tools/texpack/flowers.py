"""TX3c: the flowers of the Late Cretaceous pack. Flowering plants were young then: magnolia-like cups of many
tepals, simple open blossoms, small umbels and bells. Each vanilla flower keeps its colour (dyes still come
from it) but takes one of these early shapes, on a slender stem with one or two leaves. Hand-drawn grids:
a light, b body, c shadow of the petals; o the eye; s stem; l leaf light, k leaf dark."""
import numpy as np
from PIL import Image

from tex import N

BLOOMS = {
    "cup": [          # magnolia-like: tepals cupped upwards
        "..a.a..",
        ".aabaa.",
        "abbabba",
        "abbobba",
        ".bcbcb.",
        "..ccc..",
    ],
    "open": [         # five spread petals and an eye
        "..aa...",
        ".abba.a",
        "aabbaab",
        "bbooobb",
        ".cbobc.",
        ".cc.cc.",
    ],
    "bells": [        # little bells hanging along an arching stalk
        "..sss..",
        ".s...s.",
        "aa...aa",
        "bc.s.bc",
        "...aa..",
        "...bc..",
    ],
    "umbel": [        # a ball of tiny flowers on one stalk
        "..aba..",
        ".abaab.",
        "abbabba",
        ".bacab.",
        "..cbc..",
        "...s...",
    ],
    "star": [         # narrow pointed tepals
        "a.....a",
        ".ab.ba.",
        "..bob..",
        ".cb.bc.",
        "c.....c",
        "...s...",
    ],
    "tulip": [        # a closed cup of three outer tepals
        ".a.a.a.",
        ".ababa.",
        ".abbbb.",
        ".bbbbc.",
        "..bcc..",
        "...s...",
    ],
}

GREEN = {'s': (64, 104, 44), 'l': (98, 150, 66), 'k': (58, 96, 40)}

FLOWERS = {
    # name: (bloom, light, body, shadow, eye, stem top row of the bloom)
    "dandelion": ("cup", (255, 236, 112), (240, 200, 48), (196, 148, 30), (176, 118, 26), 4),
    "poppy": ("open", (238, 92, 72), (200, 40, 34), (140, 24, 26), (40, 30, 30), 3),
    "blue_orchid": ("star", (120, 214, 236), (54, 168, 214), (32, 112, 160), (236, 236, 200), 3),
    "allium": ("umbel", (214, 150, 236), (178, 104, 210), (124, 70, 160), (236, 200, 246), 2),
    "azure_bluet": ("open", (246, 248, 252), (214, 222, 236), (168, 178, 200), (236, 210, 90), 4),
    "red_tulip": ("tulip", (240, 86, 66), (204, 44, 36), (150, 30, 30), (204, 44, 36), 3),
    "orange_tulip": ("tulip", (252, 170, 80), (236, 120, 40), (180, 84, 28), (236, 120, 40), 3),
    "white_tulip": ("tulip", (250, 250, 244), (224, 226, 218), (178, 184, 176), (224, 226, 218), 3),
    "pink_tulip": ("tulip", (250, 196, 216), (236, 150, 184), (190, 108, 144), (236, 150, 184), 3),
    "oxeye_daisy": ("open", (252, 252, 246), (228, 230, 222), (184, 188, 178), (242, 196, 50), 3),
    "cornflower": ("star", (120, 150, 236), (70, 104, 210), (44, 66, 150), (40, 40, 90), 3),
    "lily_of_the_valley": ("bells", (252, 252, 248), (226, 230, 222), (180, 188, 176), (226, 230, 222), 1),
}


def flower(name):
    bloom, a, b, c, o, top = FLOWERS[name]
    img = np.zeros((N, N, 4), np.uint8)
    col = dict(GREEN, a=a, b=b, c=c, o=o)

    def put(x, y, ch):
        if 0 <= x < N and 0 <= y < N and ch in col:
            img[y, x, :3] = col[ch]
            img[y, x, 3] = 255

    rows = BLOOMS[bloom]
    x0, y0 = 4, top
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            put(x0 + i, y0 + j, ch)
    # stem from under the bloom to the ground, leaning a touch, with two leaves
    sy = y0 + len(rows)
    for y in range(sy, N):
        x = 7 if y < 11 else 8
        put(x, y, 's')
    for x, y, ch in ((9, 11, 'l'), (10, 10, 'l'), (11, 9, 'l'), (9, 12, 'k'), (10, 11, 'k'),      # right leaf
                     (7, 13, 'l'), (6, 12, 'l'), (5, 11, 'l'), (7, 14, 'k'), (6, 13, 'k')):   # left leaf
        put(x, y, ch)
    return Image.fromarray(img, "RGBA")


ALL = {n: flower(n) for n in FLOWERS}
