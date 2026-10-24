"""
Sprites of the scientist mechanics (16x16, drawn with code): fossils (one per species, a bone motif on a rock
chunk whose colour tells the era), field tools, notebook, pages, Fossil Rock and the Research Table.

usage: python3 science.py [preview.png]
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from sprites import TEX, Canvas, hexc, shade, mixc  # noqa: E402

# rock colour by era: Jurassic fossils come in red sandstone, Cretaceous ones in grey-brown mudstone
ROCK = {"late_cretaceous": ("#8d8273", "#6b6155"), "jurassic": ("#a86a4c", "#7f4c36"),
        "early_cretaceous": ("#b59a6a", "#8a7350"), "triassic": ("#9a5a5a", "#6e3c3c")}
BONE, BONE_L, BONE_D, HOLE = hexc("#e9dfc4"), hexc("#fbf5e4"), hexc("#bdb091"), hexc("#3c3027")

# rock chunk silhouette (16x16): '#' rock
CHUNK = [
    "................",
    "................",
    ".....######.....",
    "...##########...",
    "..############..",
    ".##############.",
    ".##############.",
    "################",
    "################",
    "################",
    ".##############.",
    ".##############.",
    "..############..",
    "...##########...",
    ".....######.....",
    "................",
]

# bone motifs: 'B' bone, 'L' light bone, 'D' dark bone, 'o' hole (eye socket, nostril)
MOTIFS = {
    "theropod_skull": [
        "................",
        "................",
        "................",
        "......LLLLL.....",
        "....LLBBBBBBL...",
        "...LBBoBBBooBB..",
        "..LBBBBBBBoooB..",
        "..BBBBBBBBBBBB..",
        "..DBBBBBBBBBBD..",
        "...DBDBDBDBBD...",
        "....DBBBBBBD....",
        "....D.D.D.DD....",
        "................",
        "................",
        "................",
        "................",
    ],
    "small_skull": [
        "................",
        "................",
        "................",
        "................",
        ".......LLL......",
        ".....LLBBBL.....",
        "....LBBoBBBB....",
        "...LBBBBBoBB....",
        "...DBDBDBBBD....",
        "....D.D.DBD.....",
        "..........D.....",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "horned_skull": [
        "................",
        "................",
        "..L.........L...",
        "...LLLLLLLLL....",
        "..LBBBBBBBBBL...",
        "..BBoBBBBBoBB...",
        "..LBBBBBBBBBL...",
        "...BBLBBBLBB....",
        "....BBBBBBB.....",
        ".....BBBBB......",
        "......BLB.......",
        "......DBD.......",
        ".......D........",
        "................",
        "................",
        "................",
    ],
    "plates": [
        "................",
        "................",
        "................",
        "....L.....L.....",
        "...LBL...LBL....",
        "..LBBBL.LBBBL...",
        "..DBBBD.DBBBD...",
        "...DBD...DBD....",
        "..LLLLLLLLLLLL..",
        "..BBoBBoBBoBBB..",
        "..DDDDDDDDDDDD..",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "tail_club": [
        "................",
        "................",
        "................",
        "................",
        "..........LLL...",
        ".........LBBBL..",
        "..LLLLLLLBBBBB..",
        "..BDBDBDBBBBBB..",
        "..DDDDDDDBBBBD..",
        ".........DBBD...",
        "..........DD....",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "vertebrae": [
        "................",
        "................",
        "................",
        "...L....L....L..",
        "..LBL..LBL..LBL.",
        "..BBB..BBB..BBB.",
        ".LBoBLLBoBLLBoB.",
        ".BBBBBBBBBBBBBB.",
        ".DBBBDDBBBDDBBD.",
        "..DBD..DBD..DBD.",
        "...D....D....D..",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "crest_skull": [
        "................",
        "...........LL...",
        "..........LBL...",
        ".........LBB....",
        "........LBB.....",
        ".....LLLBBL.....",
        "....LBBBBBBL....",
        "...LBoBBBBoBB...",
        "..LBBBBBBBBBB...",
        "..DBBBBBBBBBD...",
        "...DDDDDDDDD....",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "dome_skull": [
        "................",
        "................",
        "................",
        "......LLLL......",
        "....LLBBBBLL....",
        "...LBBBBBBBBL...",
        "...BLBLBBLBLB...",
        "...BBoBBBBoBB...",
        "...DBBBBBBBBD...",
        "....DBDBDBBD....",
        ".....D.D.DD.....",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "ptero_skull": [
        "................",
        "................",
        "................",
        "..L.............",
        "..LBL...........",
        "...LBBL.........",
        "....DBBBLL......",
        ".....BBoBBLLLL..",
        ".....DBBBBBBBBL.",
        "......DDBBDDDD..",
        "........DD......",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "egg_nest": [
        "................",
        "................",
        "................",
        "................",
        ".....LL...LL....",
        "....LBBL.LBBL...",
        "....BBBB.BBBB...",
        "..LLDBBD.DBBDL..",
        ".LBBLDD.LL.DLBL.",
        ".BBBBB.LBBL.BBB.",
        ".DBBBD.BBBB.DBD.",
        "..DDD..DBBD..D..",
        "........DD......",
        "................",
        "................",
        "................",
    ],
    "mosa_jaw": [
        "................",
        "................",
        "................",
        "................",
        "................",
        "..LLLLLLLLLL....",
        ".LBBBBBBBBBBL...",
        ".BoBoBoBoBoBBL..",
        ".DBBBBBBBBBBBBL.",
        "..DDDDDDDDDBBBD.",
        "............DD..",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "claw": [
        "................",
        "................",
        "..........LL....",
        ".........LBBL...",
        "........LBBBD...",
        ".......LBBBD....",
        "......LBBBD.....",
        ".....LBBBD......",
        "....LBBBD.......",
        "...LBBDD........",
        "..LBBDD.........",
        "..DBDD..........",
        "...DD...........",
        "................",
        "................",
        "................",
    ],
    "sickle_claw": [
        "................",
        "................",
        "................",
        "......LLL.......",
        ".....LBBBL......",
        "....LBBBBBL.....",
        "...LBBBDBBBL....",
        "...BBBD..DBB....",
        "...BBD....DB....",
        "...DBD.....D....",
        "...DBD..........",
        "....DD..........",
        "................",
        "................",
        "................",
        "................",
    ],
    "frilled_skull": [
        "................",
        "................",
        "....LL..LL......",
        "...LBBLLBBL.....",
        "...LBBBBBBBL....",
        "....BBoBBoBBL...",
        "....BBBBBBBBBL..",
        ".....BBBBBBBBBL.",
        "......DBBoBBBBB.",
        "......DBBBBBDBB.",
        ".......DBDBD.DD.",
        "........D.D.....",
        "................",
        "................",
        "................",
        "................",
    ],
    "long_neck": [
        "................",
        "................",
        "..........LLL...",
        ".........LBoBL..",
        "........LBBBBD..",
        ".......LBDDDD...",
        "......LBD.......",
        ".....LBD........",
        "....LBD.........",
        "...LBBD.........",
        "..LBBBBL........",
        "..BBDBBBD.......",
        "..DBD.DBD.......",
        "...D...D........",
        "................",
        "................",
    ],
    "croc_jaw": [
        "................",
        "................",
        "................",
        "................",
        "...LLLLLLLLLLL..",
        "..LBBBBBBBBBBBL.",
        "..BBoBBBBBBBoBB.",
        "..BBBBBBBBBBBBB.",
        "..DBDBDBDBDBDBD.",
        "..D.D.D.D.D.D.D.",
        "..DBDBDBDBDBDBD.",
        "..DBBBBBBBBBBBD.",
        "...DDDDDDDDDDD..",
        "................",
        "................",
        "................",
    ],
    "fish": [
        "................",
        "................",
        "................",
        "..........LLL...",
        "..L.....LLBBBL..",
        "..LL..LLBBoBBL..",
        "...LLLBBBBBBBB..",
        "...BBBBBDBDBDD..",
        "...BBBBBBBBBB...",
        "..DD..DDBBBDD...",
        "..D.....DDBD....",
        "..........D.....",
        "................",
        "................",
        "................",
        "................",
    ],
    "paddle": [
        "................",
        "................",
        "................",
        "......LLL.......",
        ".....LBBBL......",
        ".....LBBBBL.....",
        "....LBBDBBBL....",
        "....LBDBDBBL....",
        "....BBDBDBBB....",
        "....BDBDBDBB....",
        "....DBDBDBBD....",
        ".....DBDBBD.....",
        "......DBDD......",
        ".......DD.......",
        "................",
        "................",
    ],
    "shell": [
        "................",
        "................",
        "................",
        ".....LLLLLL.....",
        "....LBBLBBBL....",
        "...LBBLBBLBBL...",
        "...LBLBBLBBLB...",
        "...BBBLBBLBBB...",
        "...BBLBBLBBLB...",
        "...DBBLBBLBBD...",
        "....DBBDBBBD....",
        ".....DDDDDD.....",
        "................",
        "................",
        "................",
        "................",
    ],
    "bird_skull": [
        "................",
        "................",
        "................",
        "................",
        "........LLL.....",
        ".......LBBBL....",
        "......LBBoBBLLL.",
        "......BBBBBBBBBL",
        "......DBBBBDDDD.",
        "......DBDBD.....",
        ".......D.D......",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "mammal_jaw": [
        "................",
        "................",
        "................",
        "................",
        "................",
        "....LL..........",
        "...LBBL.........",
        "...BBBBLLLLLLL..",
        "...DBBBBBBBBBBL.",
        "....DBBBBBBBBBB.",
        ".....DLDLDLDLBD.",
        "......D.D.D.DD..",
        "................",
        "................",
        "................",
        "................",
    ],
    "crested_skull": [
        "................",
        "...LL...........",
        "...LBL..........",
        "....LBL.........",
        ".....LBLLL......",
        "......LBBBBL....",
        ".....LBBoBBBL...",
        ".....BBBBBBBBLL.",
        ".....DBBBBBBBBB.",
        "......DBDBDBDDD.",
        ".......D.D.D....",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "armor_scute": [
        "................",
        "................",
        "................",
        "......LLLL......",
        "....LLBBBBLL....",
        "...LBBBBBBBBL...",
        "...BBBBLLBBBB...",
        "...BBBLBBLBBB...",
        "...BBBLBBLBBB...",
        "...DBBBLLBBBD...",
        "....DBBBBBBD....",
        ".....DDDDDD.....",
        "................",
        "................",
        "................",
        "................",
    ],
    "beak_skull": [
        "................",
        "................",
        "................",
        "................",
        "..........LLL...",
        "........LLBBBL..",
        "...LLLLLBBoBBB..",
        "..LBBBBBBBBBBD..",
        "..DDBBBBBBBBD...",
        "....DDDDDDDD....",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
}

# species -> motif
FOSSIL_MOTIF = {
    # big theropods
    "tyrannosaurus": "theropod_skull", "spinosaurus": "theropod_skull", "dilophosaurus": "theropod_skull",
    "giganotosaurus": "theropod_skull", "carcharodontosaurus": "theropod_skull", "tarbosaurus": "theropod_skull",
    "daspletosaurus": "theropod_skull", "albertosaurus": "theropod_skull", "carnotaurus": "theropod_skull",
    "majungasaurus": "theropod_skull",
    # small theropods and raptors
    "velociraptor": "small_skull", "compsognathus": "small_skull", "troodon": "small_skull", "dakotaraptor": "sickle_claw",
    "mononykus": "claw", "oviraptor": "beak_skull", "citipati": "beak_skull",
    "gallimimus": "beak_skull", "struthiomimus": "beak_skull", "deinocheirus": "claw", "therizinosaurus": "claw",
    # ceratopsians
    "triceratops": "horned_skull", "styracosaurus": "frilled_skull", "pachyrhinosaurus": "frilled_skull",
    "protoceratops": "frilled_skull", "leptoceratops": "frilled_skull",
    # armoured
    "stegosaurus": "plates", "ankylosaurus": "tail_club", "euoplocephalus": "armor_scute",
    # sauropods
    "brachiosaurus": "vertebrae", "alamosaurus": "long_neck", "saltasaurus": "armor_scute", "argentinosaurus": "vertebrae",
    "opisthocoelicaudia": "long_neck", "dreadnoughtus": "vertebrae",
    # ornithopods
    "parasaurolophus": "crest_skull", "corythosaurus": "crested_skull", "edmontosaurus": "beak_skull",
    "maiasaura": "egg_nest", "pachycephalosaurus": "dome_skull", "thescelosaurus": "small_skull",
    # pterosaurs and birds
    "pteranodon": "ptero_skull", "quetzalcoatlus": "ptero_skull", "hatzegopteryx": "ptero_skull",
    "ichthyornis": "bird_skull", "hesperornis": "bird_skull", "vegavis": "bird_skull",
    # sea
    "mosasaurus": "mosa_jaw", "tylosaurus": "mosa_jaw", "elasmosaurus": "paddle", "xiphactinus": "fish", "enchodus": "fish",
    "archelon": "shell",
    "basilemys": "shell",
    # crocodylomorphs and the mammal
    "deinosuchus": "croc_jaw", "baurusuchus": "croc_jaw", "didelphodon": "mammal_jaw", "mesodma": "mammal_jaw",
}
# a species without its own line falls back by diet: the generator never leaves an icon without a texture
FALLBACK_MOTIF = {"carnivore": "theropod_skull", "piscivore": "fish", "herbivore": "small_skull", "omnivore": "small_skull",
                  "insectivore": "small_skull"}


def rock_chunk(era, seed):
    light, dark = (hexc(c) for c in ROCK[era])
    rnd = random.Random(seed)
    cv = Canvas()
    for y, row in enumerate(CHUNK):
        for x, ch in enumerate(row):
            if ch != "#":
                continue
            c = mixc(light, dark, min(1.0, max(0.0, (y - 3) / 12 + (x - 8) / 30)))
            c = shade(c, 0.92 + 0.12 * rnd.random())
            cv.set(x, y, c)
    for _ in range(10):  # grains
        x, y = rnd.randrange(16), rnd.randrange(16)
        if cv.get(x, y) is not None:
            cv.set(x, y, shade(cv.get(x, y), 0.8))
    return cv


def fossil(species, era, diet="herbivore"):
    cv = rock_chunk(era, species)
    pal = {"B": BONE, "L": BONE_L, "D": BONE_D, "o": HOLE}
    motif = FOSSIL_MOTIF.get(species) or FALLBACK_MOTIF.get(diet, "small_skull")
    for y, row in enumerate(MOTIFS[motif]):
        for x, ch in enumerate(row):
            if ch in pal:
                cv.set(x, y, pal[ch])
    cv.outline(0.45)
    return cv


def grid(rows, pal):
    cv = Canvas()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in pal:
                cv.set(x, y, hexc(pal[ch]))
    return cv


TOOLS = {
    # leather notebook with a bone clasp and an amber dot
    "field_notebook": (["................",
                        "...LLLLLLLLLL...",
                        "..LddddddddddL..",
                        "..LdppppppppdL..",
                        "..LdpwwwwwwpdL..",
                        "..LdppppppppdL..",
                        "..LdpwwwwwppdL..",
                        "..LdppppppppdL..",
                        "..LdpwwwwwwpbbA.",
                        "..LdppppppppbbA.",
                        "..LdpwwwwppppdL.",
                        "..LdppppppppdL..",
                        "..LddddddddddL..",
                        "...LLLLLLLLLL...",
                        "................",
                        "................"],
                       {"L": "#4a2c18", "d": "#7a4a28", "p": "#e8dcc0", "w": "#9c8a6c", "b": "#efe6ca", "A": "#e8a030"}),
    # torn page with handwriting
    "loose_page": (["................",
                    "................",
                    "...pppppppppp...",
                    "...pwwwwwwwpp...",
                    "...pppppppppp...",
                    "...pwwwwwwpppp..",
                    "...pppppppppp...",
                    "...pwwwwwwwwp...",
                    "...pppppppppp...",
                    "..ppwwwwwppppp..",
                    "...pppppppppp...",
                    "...pwwwwwwppp...",
                    "...ppppp.pppp...",
                    "....pp....pp....",
                    "................",
                    "................"],
                   {"p": "#e6d6b0", "w": "#6e5a44"}),
    # brush: stick handle, string wrap, fur tuft at the top
    "hair_brush": (["................",
                    "...........ff...",
                    "..........fFff..",
                    ".........fFFff..",
                    "........fFFff...",
                    "........sff.....",
                    ".......ss.......",
                    "......WW........",
                    ".....WW.........",
                    "....WW..........",
                    "...WW...........",
                    "..WW............",
                    "..W.............",
                    "................",
                    "................",
                    "................"],
                   {"f": "#8a6a4a", "F": "#c8a87e", "s": "#d8d0b8", "W": "#8a6034"}),
    # chisel: flint wedge lashed to a short stick
    "flint_chisel": (["................",
                      "................",
                      "...........FF...",
                      "..........FLFF..",
                      ".........FLFF...",
                      "........sFFF....",
                      ".......ssF......",
                      "......WW........",
                      ".....WW.........",
                      "....WW..........",
                      "...WW...........",
                      "..WW............",
                      "................",
                      "................",
                      "................",
                      "................"],
                     {"F": "#4a4a4e", "L": "#7a7a80", "s": "#d8d0b8", "W": "#8a6034"}),
    # bone tube with a polished amber lens at the front
    "amber_lens": (["................",
                    "................",
                    "................",
                    "..........AAA...",
                    ".........AaaAA..",
                    "........BAaAAA..",
                    ".......BBbAAA...",
                    "......BBbbB.....",
                    ".....BBbbB......",
                    "....BBbbB.......",
                    "...sBbbB........",
                    "..sssbB.........",
                    "..sss...........",
                    "................",
                    "................",
                    "................"],
                   {"A": "#d88a1c", "a": "#f6c25a", "B": "#e2d6b4", "b": "#b8a882", "s": "#6e4426"}),
    # fired clay jar with a cork; resin (amber) and blood versions, and a raw amber nugget
    "clay_jar": (["................", "................", "......kkkk......", "......kkkk......", ".....CCCCCC.....",
                  "......CccC......", ".....CccccC.....", "....CccccccC....", "....CccccccC....", "....CccccccC....",
                  "....CccccccC....", "....CccccccC....", ".....CccccC.....", "......CCCC......", "................", "................"],
                 {"k": "#b8915a", "C": "#8a4a2c", "c": "#b8653c"}),
    "resin_jar": (["................", "................", "......kkkk......", "......kkkk......", ".....CCCCCC.....",
                   "......CccC......", ".....CccccC.....", "....CaaaaacC....", "....CaAAAacC....", "....CaAAAacC....",
                   "....CaaaaacC....", "....CccccccC....", ".....CccccC.....", "......CCCC......", "................", "................"],
                  {"k": "#b8915a", "C": "#8a4a2c", "c": "#b8653c", "a": "#d88a1c", "A": "#f6c25a"}),
    "blood_sample": (["................", "................", "......kkkk......", "......kkkk......", ".....CCCCCC.....",
                      "......CccC......", ".....CccccC.....", "....CrrrrrcC....", "....CrRRrrcC....", "....CrrrrrcC....",
                      "....CccccccC....", "....CccccccC....", ".....CccccC.....", "......CCCC......", "................", "................"],
                     {"k": "#b8915a", "C": "#8a4a2c", "c": "#b8653c", "r": "#8a1c1c", "R": "#c43a2a"}),
    "raw_amber": (["................", "................", "................", "................", "......AAA.......",
                   ".....AaaAA......", "....AaaaaaA.....", "....AaAAaaA.....", "...AaAkAaaaA....", "...AaaAAaaaA....",
                   "....AaaaaaAA....", ".....AAaaAA.....", ".......AA.......", "................", "................", "................"],
                  {"A": "#b86a12", "a": "#f0b040", "k": "#3a2410"}),
    # charcoal stick wrapped in fibre
    "sketching_charcoal": (["................",
                            "................",
                            "............CC..",
                            "...........CcC..",
                            "..........CcC...",
                            ".........CcC....",
                            "........sCC.....",
                            ".......sss......",
                            "......sss.......",
                            ".....CC.........",
                            "....CcC.........",
                            "...CcC..........",
                            "...CC...........",
                            "................",
                            "................",
                            "................"],
                           {"C": "#1e1c1a", "c": "#4a4642", "s": "#b8a888"}),
    # bark sheet with a charcoal drawing of a dinosaur
    "sketch": (["................",
                "................",
                "..pppppppppppp..",
                "..pppppppppppp..",
                "..ppppppkkpppp..",
                "..pppppkpkkkpp..",
                "..ppkkkkkpkppp..",
                "..pkpkkkkkpppp..",
                "..ppppkpkppppp..",
                "..ppppkpkppppp..",
                "..pppppppppppp..",
                "..pppppppppppp..",
                "...ppppppppppp..",
                "................",
                "................",
                "................"],
               {"p": "#d9c49a", "k": "#2c2622"}),
}


def tools():
    for name, (rows, pal) in TOOLS.items():
        cv = grid(rows, pal)
        cv.outline(0.45)
        cv.save(os.path.join(TEX, "item", f"{name}.png"))


def blocks():
    rnd = random.Random("fossil_rock")
    stone = [hexc("#7d7d7d"), hexc("#888888"), hexc("#737373"), hexc("#6a6a6a")]
    cv = Canvas()
    for y in range(16):
        for x in range(16):
            cv.set(x, y, rnd.choice(stone))
    # a rib cage and a vertebra row embedded in the stone
    for (x, y) in ((2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (3, 4), (5, 4), (7, 4), (3, 5), (5, 5), (7, 5), (3, 6), (5, 6), (7, 6),
                   (10, 9), (11, 9), (12, 9), (13, 9), (11, 10), (11, 11), (12, 11), (13, 11), (4, 11), (5, 12), (6, 12), (7, 13), (8, 13)):
        cv.set(x, y, BONE if (x + y) % 3 else BONE_D)
    cv.save(os.path.join(TEX, "block", "fossil_rock.png"))

    # research table: stone top, leather sheet and a bone; plain stone sides; darker legs
    top = Canvas()
    for y in range(16):
        for x in range(16):
            top.set(x, y, rnd.choice(stone[:3]))
    for y in range(3, 11):
        for x in range(2, 10):
            top.set(x, y, shade(hexc("#7a4a28"), 0.9 + 0.15 * rnd.random()))
    for x in range(10, 15):
        top.set(x, 12, BONE)
    top.set(10, 11, BONE_L); top.set(14, 11, BONE_L); top.set(10, 13, BONE_D); top.set(14, 13, BONE_D)
    top.set(12, 4, hexc("#e8a030")); top.set(13, 4, hexc("#c07818"))
    top.save(os.path.join(TEX, "block", "research_table_top.png"))
    side = Canvas()
    for y in range(16):
        for x in range(16):
            c = rnd.choice(stone)
            side.set(x, y, shade(c, 1.1) if y < 1 else c)
    side.save(os.path.join(TEX, "block", "research_table_side.png"))
    leg = Canvas()
    for y in range(16):
        for x in range(16):
            leg.set(x, y, shade(rnd.choice(stone), 0.8))
    leg.save(os.path.join(TEX, "block", "research_table_leg.png"))


def fossils():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "javagen"))
    from gen_species import GUIDE
    for sid, g in GUIDE.items():
        fossil(sid, g["era"], g.get("diet", "herbivore")).save(os.path.join(TEX, "item", f"{sid}_fossil.png"))
    return list(GUIDE)


def preview(path):
    from PIL import Image
    names = [f"{s}_fossil" for s in FOSSIL_MOTIF] + list(TOOLS)
    files = [os.path.join(TEX, "item", f"{n}.png") for n in names] + \
            [os.path.join(TEX, "block", f"{n}.png") for n in ("fossil_rock", "research_table_top", "research_table_side")]
    cell, cols = 16 * 6 + 8, 7
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell, rows * cell), (70, 70, 80, 255))
    for i, f in enumerate(files):
        im = Image.open(f).resize((96, 96), Image.NEAREST)
        sheet.alpha_composite(im, ((i % cols) * cell + 4, (i // cols) * cell + 4))
    sheet.save(path)


if __name__ == "__main__":
    fossils()
    tools()
    blocks()
    if len(sys.argv) > 1:
        preview(sys.argv[1])
    print("science sprites written to", TEX)
