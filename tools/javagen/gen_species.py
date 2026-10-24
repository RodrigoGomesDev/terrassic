"""Generates the boilerplate species classes (one file per dinosaur).
Behaviour that is shared lives in DinosaurEntity / HerbivoreDinosaur / PredatorDinosaur; here each species only
sets numbers, food, sounds and a few overrides. Re-run after editing SPECIES:  python3 gen_species.py
"""
import json
import os
import re
import sys
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "common", "src", "main", "java", "com", "terrassic", "entity")
GUIDE_OUT = os.path.join(os.path.dirname(OUT), "research", "GuideSpecies.java")
REPORT = os.path.join(os.path.dirname(__file__), "..", "..", "art", "build_report.json")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "soundgen"))
from recipes import SPECIES_VOICE, VOICE_SETS, field as sound_field  # noqa: E402

# In-game size of each species. 1 block = 1 metre, so the player (1.8 blocks) is a 1.8 m tall person.
# Lengths are the upper end of the published estimates for adults (largest known specimens), see docs/TAMANHOS.md.
# scale  = renderer scale of the GeckoLib model (the model's pixel size comes from tools/modelgen,
#          see art/build_report.json); length = scale * model length.
# w, h   = hitbox in blocks. Kept narrower than the model on purpose: Minecraft hitboxes are square and
#          mobs wider than ~2.5 blocks get stuck in forests. Height covers the body, not always the head.
# baby   = size of a hatchling relative to the adult (hitbox and model).
# shadow = shadow radius in blocks.
# Riding offsets (ride_offset, ride_forward in SPECIES) are given at scale 1.0 and multiplied by scale.
SIZES = {
    #                   real length (m)  scale   w     h    baby   shadow
    "tyrannosaurus":      dict(real=13.0, scale=1.96, w=2.6, h=4.8, baby=0.25, shadow=2.4),
    "spinosaurus":        dict(real=14.0, scale=1.85, w=2.5, h=4.6, baby=0.25, shadow=2.4),
    "dilophosaurus":      dict(real=7.0,  scale=1.53, w=1.2, h=2.6, baby=0.35, shadow=1.0),
    "velociraptor":       dict(real=2.07, scale=0.48,  w=0.7, h=0.9, baby=0.5,  shadow=0.4),
    "compsognathus":      dict(real=1.25, scale=0.31,  w=0.4, h=0.5, baby=0.5,  shadow=0.25),
    "triceratops":        dict(real=9.0,  scale=1.63, w=2.4, h=3.0, baby=0.3,  shadow=2.0),
    # Styracosaurus albertensis: 5-5.5 m, ~2.7 t (Ryan et al. 2007); frill spikes included in the height.
    "styracosaurus":      dict(real=5.5,  scale=1.1,  w=1.6, h=2.9, baby=0.3,  shadow=1.4),
    # Pachyrhinosaurus canadensis: 6-8 m, ~4 t (Currie et al. 2008); the heavy polar centrosaurine.
    "pachyrhinosaurus":   dict(real=8.0,  scale=1.5,  w=2.4, h=3.6, baby=0.3,  shadow=2.0),
    # Protoceratops andrewsi: 1.8-2.5 m, 60-180 kg (Dodson 1976; Fastovsky et al. 2011). Modelled at 2x.
    "protoceratops":      dict(real=2.0,  scale=0.43, w=0.7, h=0.8, baby=0.5,  shadow=0.5),
    "stegosaurus":        dict(real=9.0,  scale=1.54, w=2.2, h=3.2, baby=0.3,  shadow=1.8),
    "ankylosaurus":       dict(real=8.0,  scale=1.83, w=2.6, h=2.1, baby=0.3,  shadow=1.9),
    # Euoplocephalus tutus: 5.5-6 m, ~2.5 t (Arbour & Currie 2013; Paul 2010); the widest body for its length.
    "euoplocephalus":     dict(real=6.0,  scale=1.43, w=2.0, h=1.8, baby=0.3,  shadow=1.6),
    # Therizinosaurus cheloniformis: 9-10 m, ~5 t (Zanno 2010; Paul 2010); stands ~6 blocks tall with the neck up.
    "therizinosaurus":    dict(real=10.0, scale=1.94, w=2.4, h=5.0, baby=0.2,  shadow=2.0),
    # Deinocheirus mirificus: 11 m, ~6.4 t (Lee et al. 2014); the biggest ornithomimosaur, humped and duck-billed.
    "deinocheirus":       dict(real=11.0, scale=1.72, w=2.4, h=4.8, baby=0.2,  shadow=2.2),
    # real Brachiosaurus: 18-22 m long, head ~13 m up (Giraffatitan mount in Berlin: 13.3 m). Sized by the
    # 22 m length; our model holds the neck more upright than that, so the head reaches ~17 blocks.
    "brachiosaurus":      dict(real=22.0, scale=3.26, w=4.0, h=9.0, baby=0.12, shadow=4.5),
    # Alamosaurus sanjuanensis: 26-30 m, 30-80 t (Fowler & Sullivan 2011; Tykoski & Fiorillo 2017); head ~13 blocks up.
    "alamosaurus":        dict(real=30.0, scale=3.02, w=5.0, h=9.0, baby=0.1,  shadow=5.5),
    # Saltasaurus loricatus: 12-13 m, ~7 t (Paul 2010), the armoured titanosaur; back at ~4 blocks.
    "saltasaurus":        dict(real=12.0, scale=1.81, w=2.8, h=3.8, baby=0.15, shadow=3.0),
    # Argentinosaurus huinculensis: 30-35 m, 65-75 t (Sellers et al. 2013; Paul 2019); head ~15 blocks up.
    "argentinosaurus":    dict(real=35.0, scale=3.08, w=6.0, h=10.0, baby=0.08, shadow=6.5),
    # Opisthocoelicaudia skarzynskii: 11-12 m, ~8.5 t (Borsuk-Bialynicka 1977; Paul 2010); rears to 8 blocks.
    "opisthocoelicaudia": dict(real=12.0, scale=1.56, w=2.6, h=3.6, baby=0.15, shadow=2.8),
    # Dreadnoughtus schrani: 26 m, 26-59 t (Lacovara et al. 2014; Bates et al. 2015); the 11 m neck carried high.
    "dreadnoughtus":      dict(real=26.0, scale=2.69, w=4.5, h=9.0, baby=0.1,  shadow=5.0),
    "parasaurolophus":    dict(real=9.5,  scale=1.51, w=2.0, h=3.2, baby=0.3,  shadow=1.6),
    "pachycephalosaurus": dict(real=4.5,  scale=0.96, w=1.0, h=1.9, baby=0.4,  shadow=0.8),
    # Thescelosaurus neglectus: 3.5-4 m, ~250-300 kg (Boyd 2014); a stout digger, modelled at 1.25x.
    "thescelosaurus":     dict(real=4.0,  scale=0.89, w=1.0, h=1.6, baby=0.35, shadow=0.8),
    "gallimimus":         dict(real=6.0,  scale=1.54, w=1.2, h=2.6, baby=0.35, shadow=0.9),
    # Struthiomimus altus: 4.3 m, ~150 kg (Osborn 1917; Nicholls & Russell 1985), the lighter ostrich mimic.
    "struthiomimus":      dict(real=4.3,  scale=1.07, w=1.0, h=2.4, baby=0.35, shadow=0.8),
    "maiasaura":          dict(real=9.0,  scale=1.45, w=2.0, h=2.8, baby=0.2,  shadow=1.6),
    # Edmontosaurus annectens: 12 m, ~4 t (Campione & Evans 2011); the hadrosaur rig scaled up from the Maiasaura.
    "edmontosaurus":      dict(real=12.0, scale=1.93, w=2.4, h=3.6, baby=0.2,  shadow=2.0),
    # Corythosaurus casuarius: 9 m, 3-4 t (Evans et al. 2009); the hadrosaur rig at the Maiasaura scale.
    "corythosaurus":      dict(real=9.0,  scale=1.45, w=2.0, h=3.3, baby=0.2,  shadow=1.6),
    # Pteranodon: "real" is the wingspan (largest males ~7.25 m). The body is small (hitbox ~ folded on the ground).
    "pteranodon":         dict(real=7.25, scale=1.07, w=1.3, h=1.7, baby=0.3,  shadow=1.0),
    # Azhdarchids: "real" is the wingspan. Quetzalcoatlus northropi 10-11 m (Witton & Habib 2010; Andres & Langston
    # 2021), standing as tall as a giraffe; Hatzegopteryx thambema 10-12 m (Buffetaut et al. 2002; Naish & Witton 2017).
    "quetzalcoatlus":     dict(real=11.0, scale=1.47, w=2.5, h=5.0, baby=0.25, shadow=2.0),
    "hatzegopteryx":      dict(real=12.0, scale=1.52, w=2.5, h=4.6, baby=0.25, shadow=2.1),
    # Ichthyornis dispar: a tern-sized toothed seabird, wingspan ~60 cm (Clarke 2004; Field et al. 2018). Modelled at 4x.
    "ichthyornis":        dict(real=0.66, scale=0.245, w=0.4, h=0.4, baby=0.5, shadow=0.2),
    # Mosasaurus hoffmannii: largest estimates ~17 m (Grigoriev 2014: 17.1 m from the jaw CCMGE 1/12457).
    "mosasaurus":         dict(real=17.0, scale=2.21, w=3.0, h=2.0, baby=0.2,  shadow=2.3),
    # Tylosaurus proriger: 12-13 m (the "Bunker" specimen KUVP 5033 ~13 m; Everhart 2005). Sleeker than the Mosasaurus.
    "tylosaurus":         dict(real=13.0, scale=1.58, w=2.6, h=1.8, baby=0.2,  shadow=2.0),
    # Elasmosaurus platyurus: ~10.3 m, of which ~7 m of neck (Sachs 2005). "real" is the total length.
    "elasmosaurus":       dict(real=10.3, scale=1.42, w=2.0, h=1.4, baby=0.2,  shadow=1.5),
    # Xiphactinus audax: 4.5-6 m, the biggest of its family (Everhart 2005; the "fish within a fish" FHSM VP-333 is ~4 m).
    "xiphactinus":        dict(real=6.0, scale=1.16, w=1.6, h=1.2, baby=0.3,  shadow=1.0),
    # Archelon ischyros: 4.6 m long, 4 m flipper to flipper (Wieland 1896/1902; YPM 3000), the largest turtle ever.
    "archelon":           dict(real=4.6, scale=1.18, w=2.2, h=1.1, baby=0.25, shadow=1.6),
    # Hesperornis regalis: up to 1.8 m long (Marsh 1880; Bell & Chiappe 2015). Modelled at 2x.
    "hesperornis":        dict(real=1.8, scale=0.39, w=0.6, h=0.6, baby=0.4,  shadow=0.4),
    # Deinosuchus riograndensis: 10.6 m well measured (Cossette & Brochu 2020), up to 12 m in older estimates (Schwimmer 2002).
    "deinosuchus":        dict(real=12.0, scale=1.64, w=2.6, h=1.4, baby=0.2,  shadow=2.2),
    # Baurusuchus salgadoensis: ~3.5 m (Carvalho, Campos & Nobre 2005), a land crocodylomorph on upright legs.
    "baurusuchus":        dict(real=3.5, scale=0.78, w=1.0, h=1.0, baby=0.3,  shadow=0.9),
}

# Field Guide data (texts live in tools/javagen/lore.py). era: late_cretaceous | early_cretaceous | jurassic | triassic.
# diet: carnivore | piscivore | herbivore | omnivore. fossil = relative chance of its fossil in fossil rock.
GUIDE = {
    "tyrannosaurus":      dict(era="late_cretaceous", diet="carnivore", fossil=2),
    "spinosaurus":        dict(era="late_cretaceous", diet="piscivore", fossil=2),
    "dilophosaurus":      dict(era="jurassic",        diet="carnivore", fossil=4),
    "velociraptor":       dict(era="late_cretaceous", diet="carnivore", fossil=4),
    "compsognathus":      dict(era="jurassic",        diet="carnivore", fossil=3),
    "triceratops":        dict(era="late_cretaceous", diet="herbivore", fossil=5),
    "styracosaurus":      dict(era="late_cretaceous", diet="herbivore", fossil=4),
    "pachyrhinosaurus":   dict(era="late_cretaceous", diet="herbivore", fossil=5),
    "protoceratops":      dict(era="late_cretaceous", diet="herbivore", fossil=6),
    "stegosaurus":        dict(era="jurassic",        diet="herbivore", fossil=5),
    "ankylosaurus":       dict(era="late_cretaceous", diet="herbivore", fossil=4),
    "euoplocephalus":     dict(era="late_cretaceous", diet="herbivore", fossil=5),
    "therizinosaurus":    dict(era="late_cretaceous", diet="herbivore", fossil=2),
    "deinocheirus":       dict(era="late_cretaceous", diet="omnivore",  fossil=1),
    "brachiosaurus":      dict(era="jurassic",        diet="herbivore", fossil=3),
    "alamosaurus":        dict(era="late_cretaceous", diet="herbivore", fossil=2),
    "saltasaurus":        dict(era="late_cretaceous", diet="herbivore", fossil=3),
    "argentinosaurus":    dict(era="late_cretaceous", diet="herbivore", fossil=1),
    "opisthocoelicaudia": dict(era="late_cretaceous", diet="herbivore", fossil=3),
    "dreadnoughtus":      dict(era="late_cretaceous", diet="herbivore", fossil=2),
    "parasaurolophus":    dict(era="late_cretaceous", diet="herbivore", fossil=5),
    "pachycephalosaurus": dict(era="late_cretaceous", diet="herbivore", fossil=4),
    "thescelosaurus":     dict(era="late_cretaceous", diet="herbivore", fossil=5),
    "gallimimus":         dict(era="late_cretaceous", diet="omnivore",  fossil=4),
    "struthiomimus":      dict(era="late_cretaceous", diet="omnivore",  fossil=4),
    "maiasaura":          dict(era="late_cretaceous", diet="herbivore", fossil=5),
    "edmontosaurus":      dict(era="late_cretaceous", diet="herbivore", fossil=5),
    "corythosaurus":      dict(era="late_cretaceous", diet="herbivore", fossil=5),
    "pteranodon":         dict(era="late_cretaceous", diet="piscivore", fossil=3),
    "quetzalcoatlus":     dict(era="late_cretaceous", diet="carnivore", fossil=2),
    "hatzegopteryx":      dict(era="late_cretaceous", diet="carnivore", fossil=1),
    "ichthyornis":        dict(era="late_cretaceous", diet="piscivore", fossil=4),
    "mosasaurus":         dict(era="late_cretaceous", diet="carnivore", fossil=2),
    "tylosaurus":         dict(era="late_cretaceous", diet="carnivore", fossil=3),
    "elasmosaurus":       dict(era="late_cretaceous", diet="piscivore", fossil=3),
    "xiphactinus":        dict(era="late_cretaceous", diet="carnivore", fossil=3),
    "archelon":           dict(era="late_cretaceous", diet="omnivore", fossil=3),
    "hesperornis":        dict(era="late_cretaceous", diet="piscivore", fossil=4),
    "deinosuchus":        dict(era="late_cretaceous", diet="carnivore", fossil=2),
    "baurusuchus":        dict(era="late_cretaceous", diet="carnivore", fossil=3),
}

# Where each species lives in the world (ModSpawns) and its entity tracking range (ModEntities).
# biomes: any of BIOMES below. weight and group (min, max) as in vanilla spawn entries; weights can be scaled or
# turned off per species in config/terrassic.json (SpawnConfig). The spawn category and placement rule follow the
# base class: SwimmingDinosaur -> WATER_CREATURE in water, FlyingDinosaur -> flyer rule, others -> on the ground.
WORLD = {
    "tyrannosaurus":      dict(biomes=("savanna", "jungle"), weight=1, group=(1, 1), track=10),
    "spinosaurus":        dict(biomes=("river", "swamp"), weight=2, group=(1, 1), track=10),
    "dilophosaurus":      dict(biomes=("forest", "jungle"), weight=3, group=(1, 2), track=8),
    "velociraptor":       dict(biomes=("savanna", "badlands", "desert"), weight=6, group=(2, 4), track=8),
    "compsognathus":      dict(biomes=("forest", "jungle"), weight=8, group=(3, 6), track=8),
    "triceratops":        dict(biomes=("savanna", "plains"), weight=6, group=(2, 4), track=10),
    "styracosaurus":      dict(biomes=("savanna", "plains", "forest"), weight=5, group=(2, 5), track=10),  # herds at the forest edge
    "pachyrhinosaurus":   dict(biomes=("taiga", "hill", "forest"), weight=4, group=(2, 5), track=10),     # cold country herds
    "protoceratops":      dict(biomes=("desert", "badlands", "savanna"), weight=7, group=(2, 5), track=8),    # dunes and dry scrub
    "stegosaurus":        dict(biomes=("forest", "plains"), weight=4, group=(1, 3), track=10),
    "ankylosaurus":       dict(biomes=("forest", "plains", "badlands"), weight=3, group=(1, 2), track=10),
    "euoplocephalus":     dict(biomes=("plains", "forest", "savanna"), weight=4, group=(1, 3), track=10),  # grazes the open floodplain
    "therizinosaurus":    dict(biomes=("forest", "jungle", "swamp"), weight=2, group=(1, 2), track=12),    # browses the high canopy
    "deinocheirus":       dict(biomes=("river", "swamp"), weight=3, group=(1, 2), track=12),                # wades the river margins
    "brachiosaurus":      dict(biomes=("savanna", "plains"), weight=1, group=(1, 2), track=14),
    "alamosaurus":        dict(biomes=("badlands", "savanna", "desert"), weight=1, group=(1, 2), track=16),  # the dry southwest
    "saltasaurus":        dict(biomes=("savanna", "plains", "river"), weight=2, group=(2, 4), track=14),  # the Patagonian floodplain
    "argentinosaurus":    dict(biomes=("savanna", "plains"), weight=1, group=(1, 1), track=18),  # one at a time, and rarely
    "opisthocoelicaudia": dict(biomes=("desert", "badlands", "savanna"), weight=2, group=(1, 3), track=14),  # the Gobi
    "dreadnoughtus":      dict(biomes=("plains", "forest", "savanna"), weight=1, group=(1, 2), track=16),  # temperate Patagonia
    "parasaurolophus":    dict(biomes=("plains", "forest"), weight=5, group=(2, 5), track=10),
    "pachycephalosaurus": dict(biomes=("taiga", "hill"), weight=4, group=(2, 3), track=8),
    "thescelosaurus":     dict(biomes=("forest", "plains", "swamp"), weight=5, group=(2, 4), track=8),     # the undergrowth
    "gallimimus":         dict(biomes=("savanna", "plains", "desert"), weight=6, group=(3, 6), track=10),
    "struthiomimus":      dict(biomes=("plains", "savanna", "forest"), weight=6, group=(3, 6), track=10),   # flocks on the floodplain
    "maiasaura":          dict(biomes=("plains", "savanna"), weight=4, group=(3, 6), track=10),   # nesting colonies
    "edmontosaurus":      dict(biomes=("plains", "forest", "savanna"), weight=6, group=(4, 8), track=10),  # big herds
    "corythosaurus":      dict(biomes=("forest", "plains"), weight=5, group=(3, 6), track=10),            # wooded floodplains
    "pteranodon":         dict(biomes=("coast",), weight=8, group=(2, 4), track=10),
    "quetzalcoatlus":     dict(biomes=("plains", "savanna", "badlands"), weight=3, group=(1, 2), track=12),  # stalks open country
    "hatzegopteryx":      dict(biomes=("hill", "forest"), weight=2, group=(1, 1), track=12),                 # island top predator
    "ichthyornis":        dict(biomes=("coast",), weight=10, group=(3, 6), track=8),                            # flocks on the shore
    "mosasaurus":         dict(biomes=("deep_sea",), weight=2, group=(1, 1), track=12),           # despawns like dolphins
    "tylosaurus":         dict(biomes=("deep_sea", "ocean"), weight=3, group=(1, 1), track=12),  # also the shallower open sea
    "elasmosaurus":       dict(biomes=("ocean", "deep_sea"), weight=4, group=(1, 2), track=12),  # fishes the open sea in pairs
    "xiphactinus":        dict(biomes=("ocean", "deep_sea"), weight=6, group=(1, 3), track=12),  # small hunting packs
    "archelon":           dict(biomes=("ocean", "coast"), weight=4, group=(1, 2), track=12),      # cruises near the shore
    "hesperornis":        dict(biomes=("coast", "ocean"), weight=8, group=(2, 5), track=10),      # rafts of divers
    "deinosuchus":        dict(biomes=("river", "swamp", "coast"), weight=3, group=(1, 1), track=10),  # ambush at the water's edge
    "baurusuchus":        dict(biomes=("savanna", "badlands", "plains"), weight=4, group=(1, 2), track=10),  # hot dry plains
}

# biome predicate -> (Java expression in ModSpawns, description for the doc comment)
BIOMES = {
    "forest": ("ctx.hasTag(BiomeTags.IS_FOREST)", "forest"),
    "jungle": ("ctx.hasTag(BiomeTags.IS_JUNGLE)", "jungle"),
    "savanna": ("ctx.hasTag(BiomeTags.IS_SAVANNA)", "savanna"),
    "badlands": ("ctx.hasTag(BiomeTags.IS_BADLANDS)", "badlands"),
    "taiga": ("ctx.hasTag(BiomeTags.IS_TAIGA)", "taiga"),
    "hill": ("ctx.hasTag(BiomeTags.IS_HILL)", "hills"),
    "river": ("ctx.hasTag(BiomeTags.IS_RIVER)", "river"),
    "plains": ('key.equals("minecraft:plains") || key.equals("minecraft:sunflower_plains")', "plains"),
    "desert": ('key.equals("minecraft:desert")', "desert*"),
    "swamp": ('key.equals("minecraft:swamp") || key.equals("minecraft:mangrove_swamp")', "swamp, mangrove"),
    "coast": ('ctx.hasTag(BiomeTags.IS_BEACH) || key.equals("minecraft:stony_shore")', "beach, stony shore"),
    "deep_sea": ('ctx.hasTag(BiomeTags.IS_DEEP_OCEAN) && !key.contains("frozen")', "deep ocean (not frozen)"),
    "ocean": ('ctx.hasTag(BiomeTags.IS_OCEAN) && !key.contains("frozen")', "ocean (not frozen)"),
}

SPECIES = [
 # id, Class, base, doc, attrs, food, sounds(ambient,hurt,death,pitch,volume,interval), extras(dict)
 dict(id="tyrannosaurus", cls="Tyrannosaurus", base="PredatorDinosaur",
      doc="Tyrannosaurus rex - apex predator. Hunts players and big animals, roars when it locks onto a target. Rideable when tamed (raised from an egg or a baby).",
      attrs=dict(MAX_HEALTH=160, MOVEMENT_SPEED=0.24, ATTACK_DAMAGE=16, ATTACK_KNOCKBACK=1.5, ARMOR=6, KNOCKBACK_RESISTANCE=0.9, FOLLOW_RANGE=32),
      food="Items.BEEF, Items.PORKCHOP, Items.MUTTON",
      sounds=("RAVAGER_AMBIENT", "RAVAGER_HURT", "RAVAGER_DEATH", 0.6, 2.0, 240), step=("RAVAGER_STEP", 0.9, 0.6),
      xp=40, step_height=1.5, head=(35, 25), rideable=True, jump=0.5, ride_offset=2.1, ride_speed=1.1,
      prey="!(e instanceof Tyrannosaurus) && !(e instanceof Compsognathus) && !(e instanceof Brachiosaurus) && !e.isBaby()",
      roar=True, prey_interval=200),
 dict(id="spinosaurus", cls="Spinosaurus", base="PredatorDinosaur",
      doc="Spinosaurus aegyptiacus - huge river predator with a sail. Lives by rivers and swamps, hunts fish, swims well and does not drown.",
      attrs=dict(MAX_HEALTH=140, MOVEMENT_SPEED=0.23, ATTACK_DAMAGE=14, ATTACK_KNOCKBACK=1.0, ARMOR=4, KNOCKBACK_RESISTANCE=0.85, FOLLOW_RANGE=32),
      food="Items.COD, Items.SALMON, Items.TROPICAL_FISH",
      sounds=("RAVAGER_AMBIENT", "RAVAGER_HURT", "RAVAGER_DEATH", 0.75, 2.0, 260), step=("RAVAGER_STEP", 0.8, 0.7),
      xp=35, step_height=1.5, head=(35, 25),
      prey="!(e instanceof DinosaurEntity) && e.isInWaterOrBubble()", roar=True, prey_interval=160, fish=True),
 dict(id="dilophosaurus", cls="Dilophosaurus", base="PredatorDinosaur",
      doc="Dilophosaurus wetherilli - mid-sized Jurassic predator with a pair of thin head crests. Flashes its crests before attacking.",
      attrs=dict(MAX_HEALTH=40, MOVEMENT_SPEED=0.30, ATTACK_DAMAGE=7, FOLLOW_RANGE=24, ARMOR=2),
      food="Items.CHICKEN, Items.RABBIT, Items.MUTTON, Items.PORKCHOP",
      sounds=("HOGLIN_AMBIENT", "HOGLIN_HURT", "HOGLIN_DEATH", 1.25, 1.2, 220),
      xp=12, step_height=1.0, head=(45, 30),
      prey="e.getBbWidth() < 1.0F && !(e instanceof DinosaurEntity)", display=True, prey_interval=100),
 dict(id="velociraptor", cls="Velociraptor", base="PredatorDinosaur",
      doc="Velociraptor mongoliensis - fast feathered pack hunter. When one raptor picks a target, the rest of the pack nearby joins in. Leaps at its prey and avoids T. rex.",
      attrs=dict(MAX_HEALTH=24, MOVEMENT_SPEED=0.34, ATTACK_DAMAGE=5, FOLLOW_RANGE=24),
      food="Items.CHICKEN, Items.RABBIT, Items.MUTTON, Items.BEEF, Items.PORKCHOP",
      sounds=("FOX_SCREECH", "FOX_HURT", "FOX_DEATH", 0.8, 1.0, 200),
      xp=8, run=0.03, prey="e.getBbWidth() < 1.0F && !(e instanceof Velociraptor)", prey_interval=80, pack=True, leap=True),
 dict(id="compsognathus", cls="Compsognathus", base="PredatorDinosaur",
      doc="Compsognathus longipes - tiny skittish scavenger living in groups. Avoids players but the group swarms whoever hurts one of them. Can be tamed with fish, like a cat.",
      attrs=dict(MAX_HEALTH=6, MOVEMENT_SPEED=0.32, ATTACK_DAMAGE=1.5),
      food="Items.CHICKEN, Items.COD, Items.SALMON",
      sounds=("PARROT_AMBIENT", "PARROT_HURT", "PARROT_DEATH", 1.2, 1.0, 120),
      xp=2, run=0.03, prey="false", hunts_players=False, feeding_tame=True, skittish=True),
 dict(id="triceratops", cls="Triceratops", base="HerbivoreDinosaur",
      doc="Triceratops horridus - armoured herd herbivore that charges with its horns. Rideable when tamed.",
      attrs=dict(MAX_HEALTH=110, MOVEMENT_SPEED=0.22, ATTACK_DAMAGE=11, ATTACK_KNOCKBACK=2.5, ARMOR=10, KNOCKBACK_RESISTANCE=0.85, FOLLOW_RANGE=20),
      food="Items.WHEAT, Items.FERN, Items.LARGE_FERN",
      sounds=("RAVAGER_AMBIENT", "RAVAGER_HURT", "RAVAGER_DEATH", 1.25, 1.0, 300), step=("RAVAGER_STEP", 0.6, 0.8),
      xp=20, rideable=True, jump=0.45, ride_offset=1.55, ride_speed=1.05),
 dict(id="styracosaurus", cls="Styracosaurus", base="HerbivoreDinosaur",
      doc="Styracosaurus albertensis - 5.5 m horned herbivore with a spiked frill and one long nose horn. Territorial: fights back with the horn. Tamed with plants; ridden or charging at an enemy it breaks the leaves and bushes in its way.",
      attrs=dict(MAX_HEALTH=80, MOVEMENT_SPEED=0.24, ATTACK_DAMAGE=9, ATTACK_KNOCKBACK=2.0, ARMOR=7, KNOCKBACK_RESISTANCE=0.7, FOLLOW_RANGE=20),
      food="Items.WHEAT, Items.FERN, Items.LARGE_FERN",
      sounds=("RAVAGER_AMBIENT", "RAVAGER_HURT", "RAVAGER_DEATH", 1.4, 0.9, 280), step=("RAVAGER_STEP", 0.5, 0.9),
      xp=16, rideable=True, jump=0.5, ride_offset=1.5, ride_speed=1.1, trample=True),
 dict(id="pachyrhinosaurus", cls="Pachyrhinosaurus", base="HerbivoreDinosaur",
      doc="Pachyrhinosaurus canadensis - 8 m horned herbivore of the cold north with a bony boss instead of a nose horn. Territorial: gores with the boss. Its musk calms the herbivores around it and draws the predators onto itself. Tamed with plants; rideable, breaks the brush in its way.",
      attrs=dict(MAX_HEALTH=120, MOVEMENT_SPEED=0.21, ATTACK_DAMAGE=11, ATTACK_KNOCKBACK=2.4, ARMOR=9, KNOCKBACK_RESISTANCE=0.85, FOLLOW_RANGE=20),
      food="Items.WHEAT, Items.FERN, Items.LARGE_FERN, Items.SWEET_BERRIES",
      sounds=("RAVAGER_AMBIENT", "RAVAGER_HURT", "RAVAGER_DEATH", 1.1, 1.0, 300), step=("RAVAGER_STEP", 0.6, 0.8),
      xp=22, rideable=True, jump=0.45, ride_offset=1.6, ride_speed=1.05, trample=True, musk=True),
 dict(id="protoceratops", cls="Protoceratops", base="HerbivoreDinosaur",
      doc="Protoceratops andrewsi - sheep-sized frilled herbivore of the dunes. Bites back when bothered. Digs in soft ground: a tame one turns up roots, bones and shallow fossils.",
      attrs=dict(MAX_HEALTH=24, MOVEMENT_SPEED=0.26, ATTACK_DAMAGE=4, ATTACK_KNOCKBACK=0.5, ARMOR=3, KNOCKBACK_RESISTANCE=0.2, FOLLOW_RANGE=16),
      food="Items.WHEAT, Items.CARROT, Items.BEETROOT, Items.FERN",
      sounds=("TURTLE_AMBIENT_LAND", "TURTLE_HURT", "TURTLE_DEATH", 1.1, 1.0, 240), xp=7, run=0.02, dig=True),
 dict(id="stegosaurus", cls="Stegosaurus", base="HerbivoreDinosaur",
      doc="Stegosaurus stenops - slow herbivore that defends itself with the spiked tail (thagomizer).",
      attrs=dict(MAX_HEALTH=90, MOVEMENT_SPEED=0.20, ATTACK_DAMAGE=10, ATTACK_KNOCKBACK=1.2, ARMOR=8, KNOCKBACK_RESISTANCE=0.8, FOLLOW_RANGE=20),
      food="Items.FERN, Items.LARGE_FERN, Items.MELON_SLICE, Items.WHEAT",
      sounds=("COW_AMBIENT", "COW_HURT", "COW_DEATH", 0.55, 1.5, 320), step=("RAVAGER_STEP", 0.5, 1.0), xp=18),
 dict(id="ankylosaurus", cls="Ankylosaurus", base="HerbivoreDinosaur",
      doc="Ankylosaurus magniventris - living tank covered in bony armour, swings a heavy tail club when attacked. Drops its tail club.",
      attrs=dict(MAX_HEALTH=100, MOVEMENT_SPEED=0.17, ATTACK_DAMAGE=12, ATTACK_KNOCKBACK=2.0, ARMOR=16, ARMOR_TOUGHNESS=4, KNOCKBACK_RESISTANCE=1.0, FOLLOW_RANGE=16),
      food="Items.FERN, Items.LARGE_FERN, Items.SWEET_BERRIES",
      sounds=("SNIFFER_IDLE", "SNIFFER_HURT", "SNIFFER_DEATH", 0.7, 1.2, 300), step=("RAVAGER_STEP", 0.5, 1.1), xp=20),
 dict(id="euoplocephalus", cls="Euoplocephalus", base="HerbivoreDinosaur",
      doc="Euoplocephalus tutus - 6 m armoured herbivore with bony eyelids and a tail club. Territorial: a blow of the club leaves whatever it hits slowed and weakened (stunned). Tamed with ferns and berries; a guard, not a mount.",
      attrs=dict(MAX_HEALTH=85, MOVEMENT_SPEED=0.18, ATTACK_DAMAGE=9, ATTACK_KNOCKBACK=1.8, ARMOR=14, ARMOR_TOUGHNESS=3, KNOCKBACK_RESISTANCE=1.0, FOLLOW_RANGE=16),
      food="Items.FERN, Items.LARGE_FERN, Items.SWEET_BERRIES, Items.MELON_SLICE",
      sounds=("SNIFFER_IDLE", "SNIFFER_HURT", "SNIFFER_DEATH", 0.85, 1.1, 300), step=("RAVAGER_STEP", 0.45, 1.15), xp=18,
      hit_effects=[("MobEffects.MOVEMENT_SLOWDOWN", 80, 3), ("MobEffects.WEAKNESS", 80, 0)]),
 dict(id="therizinosaurus", cls="Therizinosaurus", base="HerbivoreDinosaur",
      doc="Therizinosaurus cheloniformis - 10 m feathered herbivore with metre-long claws. Browses the canopy, pulling leaves down with the claws. Territorial: slashes hard. Egg-tamed for now (knockout taming comes in v0.7); a tall mount that harvests leaves as it goes.",
      attrs=dict(MAX_HEALTH=140, MOVEMENT_SPEED=0.2, ATTACK_DAMAGE=14, ATTACK_KNOCKBACK=1.5, ARMOR=5, KNOCKBACK_RESISTANCE=0.8, FOLLOW_RANGE=24),
      food="Items.APPLE, Items.SWEET_BERRIES, Items.GLOW_BERRIES, Items.MELON_SLICE",
      sounds=("SNIFFER_IDLE", "SNIFFER_HURT", "SNIFFER_DEATH", 0.55, 2.0, 320), step=("RAVAGER_STEP", 0.8, 0.6),
      xp=30, step_height=1.2, head=(30, 25), rideable=True, jump=0.5, ride_offset=2.6, ride_speed=1.0, egg_only=True, forage=True),
 dict(id="deinocheirus", cls="Deinocheirus", base="HerbivoreDinosaur",
      doc="Deinocheirus mirificus - 11 m humped, duck-billed ornithomimosaur of the river margins with 2.4 m arms. Omnivore: scoops fish and weed out of the water (a tame one brings them to you). Territorial: swipes with the arms. Tamed with fish or plants; a tall mount.",
      attrs=dict(MAX_HEALTH=150, MOVEMENT_SPEED=0.21, ATTACK_DAMAGE=12, ATTACK_KNOCKBACK=1.8, ARMOR=4, KNOCKBACK_RESISTANCE=0.8, FOLLOW_RANGE=24),
      food="Items.COD, Items.SALMON, Items.KELP, Items.MELON_SLICE, Items.SWEET_BERRIES",
      sounds=("SNIFFER_IDLE", "SNIFFER_HURT", "SNIFFER_DEATH", 0.5, 2.0, 320), step=("RAVAGER_STEP", 0.8, 0.6),
      xp=32, step_height=1.2, head=(30, 25), rideable=True, jump=0.4, ride_offset=2.8, ride_speed=0.95, scoop=True),
 dict(id="brachiosaurus", cls="Brachiosaurus", base="HerbivoreDinosaur",
      doc="Brachiosaurus altithorax - gigantic long-necked browser, eats leaves. Peaceful unless hurt. Rideable when tamed - the tallest mount in the game.",
      attrs=dict(MAX_HEALTH=300, MOVEMENT_SPEED=0.18, ATTACK_DAMAGE=18, ATTACK_KNOCKBACK=2.0, ARMOR=8, KNOCKBACK_RESISTANCE=1.0, FOLLOW_RANGE=16),
      food_tag="ItemTags.LEAVES",
      sounds=("SNIFFER_IDLE", "SNIFFER_HURT", "SNIFFER_DEATH", 0.45, 3.0, 360), step=("RAVAGER_STEP", 1.2, 0.5),
      xp=50, step_height=1.6, head=(25, 30), rideable=True, platform=True, jump=0.0, ride_offset=2.7, ride_forward=0.8, ride_speed=1.0),
 dict(id="alamosaurus", cls="Alamosaurus", base="HerbivoreDinosaur",
      doc="Alamosaurus sanjuanensis - 30 m titanosaur, the last and largest sauropod of North America. Eats leaves; peaceful unless hurt, then the whip tail cracks. Rideable when tamed (the building platform saddle comes with the v0.6 systems).",
      attrs=dict(MAX_HEALTH=360, MOVEMENT_SPEED=0.17, ATTACK_DAMAGE=20, ATTACK_KNOCKBACK=2.5, ARMOR=10, KNOCKBACK_RESISTANCE=1.0, FOLLOW_RANGE=16),
      food_tag="ItemTags.LEAVES",
      sounds=("SNIFFER_IDLE", "SNIFFER_HURT", "SNIFFER_DEATH", 0.4, 3.0, 380), step=("RAVAGER_STEP", 1.3, 0.45),
      xp=60, step_height=1.8, head=(25, 30), rideable=True, platform=True, jump=0.0, ride_offset=3.2, ride_forward=0.6, ride_speed=0.95),
 dict(id="saltasaurus", cls="Saltasaurus", base="HerbivoreDinosaur",
      doc="Saltasaurus loricatus - 12 m armoured titanosaur: oval osteoderms over a skin of bony pebbles, a short neck and a low wide body. Herd animal; hurt, it rears and stomps. Eats leaves; rideable when tamed, a living tank.",
      attrs=dict(MAX_HEALTH=220, MOVEMENT_SPEED=0.19, ATTACK_DAMAGE=14, ATTACK_KNOCKBACK=1.5, ARMOR=18, ARMOR_TOUGHNESS=6, KNOCKBACK_RESISTANCE=1.0, FOLLOW_RANGE=16),
      food_tag="ItemTags.LEAVES",
      sounds=("SNIFFER_IDLE", "SNIFFER_HURT", "SNIFFER_DEATH", 0.55, 2.4, 340), step=("RAVAGER_STEP", 1.0, 0.6),
      xp=40, step_height=1.5, head=(30, 30), rideable=True, jump=0.0, ride_offset=2.3, ride_forward=0.2, ride_speed=1.0),
 dict(id="argentinosaurus", cls="Argentinosaurus", base="HerbivoreDinosaur",
      doc="Argentinosaurus huinculensis - 35 m titanosaur, the largest land animal of the mod: a house that walks. Clears the brush in its path when it moves with purpose; hurt, it lifts a forefoot and treads, and the ground shakes (slowness). Egg-tamed for now (knockout taming comes in v0.7); rideable, the platform saddle comes with the v0.6 systems.",
      attrs=dict(MAX_HEALTH=600, MOVEMENT_SPEED=0.15, ATTACK_DAMAGE=28, ATTACK_KNOCKBACK=3.0, ARMOR=12, ARMOR_TOUGHNESS=4, KNOCKBACK_RESISTANCE=1.0, FOLLOW_RANGE=16),
      food_tag="ItemTags.LEAVES",
      sounds=("SNIFFER_IDLE", "SNIFFER_HURT", "SNIFFER_DEATH", 0.3, 3.5, 420), step=("RAVAGER_STEP", 1.6, 0.4),
      xp=80, step_height=2.0, head=(20, 25), rideable=True, platform=True, jump=0.0, ride_offset=3.7, ride_forward=0.4, ride_speed=0.9,
      egg_only=True, trample=True, hit_effects=[("MobEffects.MOVEMENT_SLOWDOWN", 60, 2)]),
 dict(id="opisthocoelicaudia", cls="Opisthocoelicaudia", base="HerbivoreDinosaur",
      doc="Opisthocoelicaudia skarzynskii - 12 m stocky titanosaur of the Gobi with a rod-stiff tail it props on to rear up and browse the canopy (the tripod). Peaceful; hurt, it shoves with the hips and slams a forefoot. Hand-tamed with leaves; rideable, a steady pack animal (the cargo inventory comes with the v0.6 systems).",
      attrs=dict(MAX_HEALTH=200, MOVEMENT_SPEED=0.2, ATTACK_DAMAGE=12, ATTACK_KNOCKBACK=1.5, ARMOR=8, KNOCKBACK_RESISTANCE=1.0, FOLLOW_RANGE=16),
      food_tag="ItemTags.LEAVES",
      sounds=("SNIFFER_IDLE", "SNIFFER_HURT", "SNIFFER_DEATH", 0.6, 2.2, 320), step=("RAVAGER_STEP", 0.9, 0.65),
      xp=36, step_height=1.5, head=(30, 30), rideable=True, jump=0.0, ride_offset=2.2, ride_forward=0.1, ride_speed=1.0, forage=True),
 dict(id="dreadnoughtus", cls="Dreadnoughtus", base="HerbivoreDinosaur",
      doc="Dreadnoughtus schrani - 26 m titanosaur that fears nothing: an 11 m neck carried high over a huge shoulder. Hurt, it bellows and swings the neck like a crane boom, the head knocking whatever stands at its side. Hand-tamed with leaves; rideable (the building platform saddle comes with the v0.6 systems).",
      attrs=dict(MAX_HEALTH=420, MOVEMENT_SPEED=0.17, ATTACK_DAMAGE=18, ATTACK_KNOCKBACK=2.0, ARMOR=10, KNOCKBACK_RESISTANCE=1.0, FOLLOW_RANGE=16),
      food_tag="ItemTags.LEAVES",
      sounds=("SNIFFER_IDLE", "SNIFFER_HURT", "SNIFFER_DEATH", 0.4, 3.0, 400), step=("RAVAGER_STEP", 1.3, 0.45),
      xp=56, step_height=1.8, head=(20, 30), rideable=True, platform=True, jump=0.0, ride_offset=3.4, ride_forward=0.2, ride_speed=0.95, call=True),
 dict(id="parasaurolophus", cls="Parasaurolophus", base="HerbivoreDinosaur",
      doc="Parasaurolophus walkeri - duck-billed herbivore with a long hollow crest it uses to call. Flees from danger with the herd. Rideable when tamed.",
      attrs=dict(MAX_HEALTH=60, MOVEMENT_SPEED=0.27, ATTACK_DAMAGE=4, ARMOR=2, KNOCKBACK_RESISTANCE=0.3, FOLLOW_RANGE=20),
      food="Items.WHEAT, Items.FERN, Items.SWEET_BERRIES",
      sounds=("CAMEL_AMBIENT", "CAMEL_HURT", "CAMEL_DEATH", 0.7, 1.6, 260), xp=12,
      fights=False, rideable=True, jump=0.65, ride_offset=1.6, ride_speed=1.15, call=True),
 dict(id="pachycephalosaurus", cls="Pachycephalosaurus", base="HerbivoreDinosaur",
      doc="Pachycephalosaurus wyomingensis - bipedal herbivore with a thick bony dome. Headbutts hard (huge knockback) when provoked.",
      attrs=dict(MAX_HEALTH=40, MOVEMENT_SPEED=0.28, ATTACK_DAMAGE=8, ATTACK_KNOCKBACK=3.0, ARMOR=4, KNOCKBACK_RESISTANCE=0.4, FOLLOW_RANGE=16),
      food="Items.SWEET_BERRIES, Items.GLOW_BERRIES, Items.APPLE",
      sounds=("GOAT_AMBIENT", "GOAT_HURT", "GOAT_DEATH", 0.7, 1.0, 240), xp=10, run=0.02),
 dict(id="thescelosaurus", cls="Thescelosaurus", base="HerbivoreDinosaur",
      doc="Thescelosaurus neglectus - 4 m stout ornithopod of the undergrowth, nose to the ground. Bites back when cornered. Roots in soft soil: a tame one turns up roots and tubers.",
      attrs=dict(MAX_HEALTH=34, MOVEMENT_SPEED=0.25, ATTACK_DAMAGE=5, ATTACK_KNOCKBACK=0.6, ARMOR=2, KNOCKBACK_RESISTANCE=0.3, FOLLOW_RANGE=16),
      food="Items.CARROT, Items.POTATO, Items.BEETROOT, Items.FERN",
      sounds=("PIG_AMBIENT", "PIG_HURT", "PIG_DEATH", 0.75, 1.0, 260), xp=9, run=0.02, dig="tubers"),
 dict(id="gallimimus", cls="Gallimimus", base="HerbivoreDinosaur",
      doc="Gallimimus bullatus - ostrich-like ornithomimid, the fastest dinosaur. Flocks flee from players and predators. A very fast mount when tamed.",
      attrs=dict(MAX_HEALTH=30, MOVEMENT_SPEED=0.36, ATTACK_DAMAGE=3, FOLLOW_RANGE=20),
      food="Items.WHEAT_SEEDS, Items.SWEET_BERRIES, Items.APPLE",
      sounds=("CHICKEN_AMBIENT", "CHICKEN_HURT", "CHICKEN_DEATH", 0.55, 1.2, 200), xp=8, run=0.03,
      fights=False, rideable=True, jump=0.8, ride_offset=1.1, ride_forward=0.12, ride_speed=1.35),
 dict(id="struthiomimus", cls="Struthiomimus", base="HerbivoreDinosaur",
      doc="Struthiomimus altus - 4.3 m ostrich mimic of the floodplains. Flocks flee from danger. Omnivore, tamed with seeds, berries or eggs; the lightest and fastest mount.",
      attrs=dict(MAX_HEALTH=26, MOVEMENT_SPEED=0.37, ATTACK_DAMAGE=3, FOLLOW_RANGE=20),
      food="Items.WHEAT_SEEDS, Items.MELON_SEEDS, Items.SWEET_BERRIES, Items.EGG",
      sounds=("CHICKEN_AMBIENT", "CHICKEN_HURT", "CHICKEN_DEATH", 0.7, 1.1, 200), xp=8, run=0.03,
      fights=False, rideable=True, jump=0.9, ride_offset=1.0, ride_forward=0.1, ride_speed=1.45),
 dict(id="maiasaura", cls="Maiasaura", base="HerbivoreDinosaur",
      doc="Maiasaura peeblesorum - the \"good mother\" hadrosaur. Lives in nesting colonies; babies of any species near an adult grow twice as fast. Rideable when tamed.",
      attrs=dict(MAX_HEALTH=65, MOVEMENT_SPEED=0.25, ATTACK_DAMAGE=5, ARMOR=3, KNOCKBACK_RESISTANCE=0.4, FOLLOW_RANGE=20),
      food="Items.WHEAT, Items.FERN, Items.SWEET_BERRIES",
      sounds=("CAMEL_AMBIENT", "CAMEL_HURT", "CAMEL_DEATH", 0.6, 1.6, 260), xp=12,
      rideable=True, jump=0.6, ride_offset=1.45, ride_speed=1.05, call=True, nurse=True),
 dict(id="edmontosaurus", cls="Edmontosaurus", base="HerbivoreDinosaur",
      doc="Edmontosaurus annectens - 12 m flat-headed duckbill, the biggest of the hadrosaurs, grazing in large herds on the plains. Tamed with plants; a steady riding and pack mount (the cargo inventory arrives with the v0.6 systems).",
      attrs=dict(MAX_HEALTH=90, MOVEMENT_SPEED=0.24, ATTACK_DAMAGE=6, ARMOR=3, KNOCKBACK_RESISTANCE=0.6, FOLLOW_RANGE=24),
      food="Items.WHEAT, Items.FERN, Items.APPLE, Items.SWEET_BERRIES",
      sounds=("CAMEL_AMBIENT", "CAMEL_HURT", "CAMEL_DEATH", 0.5, 1.8, 280), xp=14,
      rideable=True, jump=0.5, ride_offset=1.55, ride_speed=1.0, call=True),
 dict(id="corythosaurus", cls="Corythosaurus", base="HerbivoreDinosaur",
      doc="Corythosaurus casuarius - 9 m helmet-crested duckbill of the wooded floodplains. Its deep call calms every herbivore around it (they stop panicking and heal a little). Tamed with plants; rideable.",
      attrs=dict(MAX_HEALTH=70, MOVEMENT_SPEED=0.26, ATTACK_DAMAGE=4, ARMOR=2, KNOCKBACK_RESISTANCE=0.3, FOLLOW_RANGE=20),
      food="Items.WHEAT, Items.FERN, Items.APPLE, Items.SWEET_BERRIES",
      sounds=("CAMEL_AMBIENT", "CAMEL_HURT", "CAMEL_DEATH", 0.6, 1.6, 260), xp=12,
      fights=False, rideable=True, jump=0.6, ride_offset=1.55, ride_speed=1.1, call=True, calm=True),
 # ---- flyers (FlyingDinosaur: flying navigation, no fall damage, ridden flight)
 dict(id="pteranodon", cls="Pteranodon", base="FlyingDinosaur",
      doc="Pteranodon longiceps - big crested pterosaur that fishes along the coast. Tamed by hand-feeding fish; the first flying mount (light and fast).",
      attrs=dict(MAX_HEALTH=30, MOVEMENT_SPEED=0.25, FLYING_SPEED=0.6, ATTACK_DAMAGE=4, FOLLOW_RANGE=24),
      food="Items.COD, Items.SALMON, Items.TROPICAL_FISH",
      sounds=("PARROT_AMBIENT", "PARROT_HURT", "PARROT_DEATH", 0.45, 1.4, 220), xp=12, run=0.03,
      rideable=True, ride_offset=0.95, ride_forward=0.05, ride_speed=1.0,
      prey="e instanceof AbstractFish"),
 dict(id="quetzalcoatlus", cls="Quetzalcoatlus", base="FlyingDinosaur",
      doc="Quetzalcoatlus northropi - the largest flyer ever, a giraffe-tall azhdarchid that stalks open country on all fours and spears small prey like a giant stork. Egg-tamed for now (knockout taming comes in v0.7); a heavy flying mount.",
      attrs=dict(MAX_HEALTH=90, MOVEMENT_SPEED=0.3, FLYING_SPEED=0.7, ATTACK_DAMAGE=9, ARMOR=2, KNOCKBACK_RESISTANCE=0.6, FOLLOW_RANGE=32),
      food="Items.CHICKEN, Items.RABBIT, Items.PORKCHOP, Items.MUTTON, Items.BEEF",
      sounds=("PARROT_AMBIENT", "PARROT_HURT", "PARROT_DEATH", 0.6, 1.8, 300), xp=28, run=0.04,
      rideable=True, ride_offset=2.25, ride_forward=0.0, ride_speed=0.9, egg_only=True,
      prey="e.getBbWidth() < 1.0F && !(e instanceof FlyingDinosaur) && !e.isBaby()", prey_interval=140),
 dict(id="hatzegopteryx", cls="Hatzegopteryx", base="FlyingDinosaur",
      doc="Hatzegopteryx thambema - robust azhdarchid from Hateg Island with a very wide skull and a short, massive neck; the island's top predator, taking prey the size of a horse. Egg-tamed for now (knockout taming comes in v0.7); a heavy combat flyer.",
      attrs=dict(MAX_HEALTH=110, MOVEMENT_SPEED=0.28, FLYING_SPEED=0.62, ATTACK_DAMAGE=13, ATTACK_KNOCKBACK=1.0, ARMOR=3, KNOCKBACK_RESISTANCE=0.7, FOLLOW_RANGE=32),
      food="Items.PORKCHOP, Items.MUTTON, Items.BEEF, Items.CHICKEN",
      sounds=("PARROT_AMBIENT", "PARROT_HURT", "PARROT_DEATH", 0.5, 2.0, 320), xp=32, run=0.04,
      rideable=True, ride_offset=2.15, ride_forward=0.0, ride_speed=0.85, egg_only=True,
      prey="e.getBbWidth() < 1.6F && !(e instanceof FlyingDinosaur) && !e.isBaby()", prey_interval=160),
 dict(id="ichthyornis", cls="Ichthyornis", base="FlyingDinosaur",
      doc="Ichthyornis dispar - tern-sized toothed seabird of the Western Interior Seaway shores. Tamed with fish; rides on the owner's shoulder, calls out when a monster is after them and now and then dives for a fish.",
      attrs=dict(MAX_HEALTH=8, MOVEMENT_SPEED=0.25, FLYING_SPEED=0.75, ATTACK_DAMAGE=1, FOLLOW_RANGE=20),
      food="Items.COD, Items.SALMON, Items.TROPICAL_FISH",
      sounds=("PARROT_AMBIENT", "PARROT_HURT", "PARROT_DEATH", 1.6, 0.5, 160), xp=3, run=0.03,
      prey="e instanceof AbstractFish && e.getBbWidth() < 0.6F", prey_interval=100, shoulder=True, fisher=True),
 # ---- marine reptiles (SwimmingDinosaur: smooth swimming, wild only for now)
 dict(id="mosasaurus", cls="Mosasaurus", base="SwimmingDinosaur",
      doc="Mosasaurus hoffmannii - giant marine lizard, terror of the inland sea. Lives in deep oceans and hunts anything in the water, players swimming or in boats included. Gives birth to live calves, and only a calf can be tamed (fed fish); grown and saddled it is the giant aquatic mount.",
      attrs=dict(MAX_HEALTH=180, MOVEMENT_SPEED=1.1, ATTACK_DAMAGE=18, ATTACK_KNOCKBACK=1.0, ARMOR=6, KNOCKBACK_RESISTANCE=1.0, FOLLOW_RANGE=32),
      food="Items.COD, Items.SALMON, Items.TROPICAL_FISH",
      sounds=("RAVAGER_AMBIENT", "RAVAGER_HURT", "RAVAGER_DEATH", 0.45, 2.0, 400), xp=40, run=0.04,
      prey="e instanceof WaterAnimal || e instanceof Turtle || e instanceof Pteranodon",
      prey_imports=["net.minecraft.world.entity.animal.WaterAnimal", "net.minecraft.world.entity.animal.Turtle"],
      tame="baby", live_young=True, rideable=True, ride_offset=0.95, ride_forward=-0.1, ride_speed=1.0, dive=1.0),
 dict(id="tylosaurus", cls="Tylosaurus", base="SwimmingDinosaur",
      doc="Tylosaurus proriger - the top predator of the Western Interior Seaway before the Mosasaurus: slender, 13 m, small flippers and a toothless reinforced rostrum it rams prey with (the hit slows and dazes). Wild only for now (knockout taming in v0.7).",
      attrs=dict(MAX_HEALTH=150, MOVEMENT_SPEED=1.25, ATTACK_DAMAGE=14, ATTACK_KNOCKBACK=1.5, ARMOR=4, KNOCKBACK_RESISTANCE=0.9, FOLLOW_RANGE=32),
      food="Items.COD, Items.SALMON, Items.TROPICAL_FISH",
      sounds=("RAVAGER_AMBIENT", "RAVAGER_HURT", "RAVAGER_DEATH", 0.6, 2.0, 380), xp=36, run=0.05,
      prey="e instanceof WaterAnimal || e instanceof Turtle || e instanceof FlyingDinosaur || e instanceof Mosasaurus && e.isBaby()",
      prey_imports=["net.minecraft.world.entity.animal.WaterAnimal", "net.minecraft.world.entity.animal.Turtle"],
      hit_effects=[("MobEffects.MOVEMENT_SLOWDOWN", 100, 2), ("MobEffects.CONFUSION", 100, 0)], live_young=True),
 dict(id="elasmosaurus", cls="Elasmosaurus", base="SwimmingDinosaur",
      doc="Elasmosaurus platyurus - plesiosaur with a 7 m neck on a 10 m body, flying under water on four long paddles and snapping fish with needle teeth. Hand-tamed with fish; the first aquatic mount (look down to dive, up to surface; the rider never drowns). Gives birth to live young.",
      attrs=dict(MAX_HEALTH=70, MOVEMENT_SPEED=1.1, ATTACK_DAMAGE=5, ARMOR=2, KNOCKBACK_RESISTANCE=0.5, FOLLOW_RANGE=28),
      food="Items.COD, Items.SALMON, Items.TROPICAL_FISH",
      sounds=("DOLPHIN_AMBIENT_WATER", "DOLPHIN_HURT", "DOLPHIN_DEATH", 0.55, 1.6, 320), xp=18, run=0.05,
      prey="e instanceof AbstractFish",
      tame="feeding", live_young=True, rideable=True, ride_offset=0.95, ride_forward=0.0, ride_speed=1.1, dive=1.2),
 dict(id="xiphactinus", cls="Xiphactinus", base="SwimmingDinosaur",
      doc="Xiphactinus audax - a 6 m predatory bony fish with a bulldog face and fangs, fast and always hungry: it swallows fish whole and lunges at anything that enters its water. Wild only (cannot be tamed).",
      attrs=dict(MAX_HEALTH=40, MOVEMENT_SPEED=1.35, ATTACK_DAMAGE=7, ARMOR=1, KNOCKBACK_RESISTANCE=0.3, FOLLOW_RANGE=24),
      food="Items.COD, Items.SALMON, Items.TROPICAL_FISH",
      sounds=("COD_AMBIENT", "COD_HURT", "COD_DEATH", 0.5, 1.6, 300), xp=14, run=0.06,
      prey="e instanceof AbstractFish || e instanceof Squid || e instanceof Ichthyornis && e.isInWater()",
      prey_imports=["net.minecraft.world.entity.animal.AbstractFish", "net.minecraft.world.entity.animal.Squid"], prey_interval=80),
 dict(id="archelon", cls="Archelon", base="SwimmingDinosaur",
      doc="Archelon ischyros - the largest turtle ever, 4.6 m long and 4 m across the flippers, a leathery shell over a rib frame and a hooked beak. Peaceful grazer of squid and seaweed that only bites back; hand-tamed with kelp or fish, lays eggs (on land, or drops the egg in the water), and carries a rider as a slow armoured aquatic mount.",
      attrs=dict(MAX_HEALTH=120, MOVEMENT_SPEED=0.9, ATTACK_DAMAGE=6, ARMOR=14, KNOCKBACK_RESISTANCE=0.8, FOLLOW_RANGE=24),
      food="Items.KELP, Items.SEAGRASS, Items.COD, Items.SALMON",
      sounds=("TURTLE_AMBIENT_LAND", "TURTLE_HURT", "TURTLE_DEATH", 0.5, 1.6, 400), xp=12, run=0.03,
      prey="e instanceof Squid", prey_imports=["net.minecraft.world.entity.animal.Squid"], hunts_players=False,
      tame="feeding", rideable=True, ride_offset=0.9, ride_forward=0.1, ride_speed=0.75, dive=0.8),
 dict(id="hesperornis", cls="Hesperornis", base="SwimmingDinosaur",
      doc="Hesperornis regalis - flightless toothed diving bird of the inland sea, 1.8 m, built like a loon: it kicks with lobed feet and spears fish under water. Rafts of them float off the coast; tamed with fish, lays small eggs. Never attacks players, only fights back.",
      attrs=dict(MAX_HEALTH=14, MOVEMENT_SPEED=1.1, ATTACK_DAMAGE=2, FOLLOW_RANGE=16),
      food="Items.COD, Items.SALMON, Items.TROPICAL_FISH",
      sounds=("PARROT_AMBIENT", "PARROT_HURT", "PARROT_DEATH", 0.7, 0.6, 200), xp=4, run=0.03,
      prey="e instanceof AbstractFish && e.getBbWidth() < 0.8F", hunts_players=False, tame="feeding", dive=1.3),
 dict(id="deinosuchus", cls="Deinosuchus", base="PredatorDinosaur",
      doc="Deinosuchus riograndensis - 12 m alligator of the inland sea's shores. Basks by rivers, swamps and beaches, swims as well as it walks, and ambushes anything that comes to the water: its grip slows the victim. Egg taming only until the knockout (v0.7).",
      attrs=dict(MAX_HEALTH=160, MOVEMENT_SPEED=0.2, ATTACK_DAMAGE=18, ATTACK_KNOCKBACK=1.5, ARMOR=10, KNOCKBACK_RESISTANCE=0.9, FOLLOW_RANGE=28),
      food="Items.COD, Items.SALMON, Items.TROPICAL_FISH, Items.BEEF, Items.PORKCHOP",
      sounds=("RAVAGER_AMBIENT", "RAVAGER_HURT", "RAVAGER_DEATH", 0.55, 2.0, 320), step=("RAVAGER_STEP", 0.6, 0.6),
      xp=38, step_height=1.0, head=(40, 20),
      prey="e.isInWaterOrBubble() || e.getBbWidth() < 1.6F && !(e instanceof Deinosuchus)", prey_interval=140, fish=True,
      amphibious=True, hit_effects=[("MobEffects.MOVEMENT_SLOWDOWN", 60, 1)]),
 dict(id="baurusuchus", cls="Baurusuchus", base="PredatorDinosaur",
      doc="Baurusuchus salgadoensis - 3.5 m land crocodylomorph on upright legs with a deep dog-like skull and blade teeth: a fast runner of the hot plains that hunts anything smaller than itself, alone or in pairs. Egg taming only until the knockout (v0.7); a tamed one is a base guard.",
      attrs=dict(MAX_HEALTH=55, MOVEMENT_SPEED=0.3, ATTACK_DAMAGE=9, ARMOR=5, KNOCKBACK_RESISTANCE=0.5, FOLLOW_RANGE=24),
      food="Items.BEEF, Items.PORKCHOP, Items.CHICKEN, Items.MUTTON",
      sounds=("HOGLIN_AMBIENT", "HOGLIN_HURT", "HOGLIN_DEATH", 0.8, 1.4, 260), step=("RAVAGER_STEP", 0.5, 1.0),
      xp=16, step_height=1.0, head=(45, 25),
      prey="e.getBbWidth() < 1.4F && !(e instanceof Baurusuchus)", prey_interval=100),
]


def model_bounds():
    with open(REPORT) as f:
        return {k: v["bounds_px"] for k, v in json.load(f).items()}


def culling(size, bounds):
    """How far the scaled model sticks out of the hitbox, plus a margin."""
    (x0, y0, z0), (x1, y1, z1) = bounds
    k = size["scale"] / 16.0
    out = max((z1 - z0) * k / 2, (x1 - x0) * k / 2) - size["w"] / 2
    out = max(out, (y1 - y0) * k - size["h"])
    return round(max(out, 0.0) + 0.5, 1)


def gen(s, bounds):
    cls, base = s["cls"], s["base"]
    size = SIZES[s["id"]]
    s = dict(s, cull=culling(size, bounds[s["id"]]))
    voice = SPECIES_VOICE.get(s["id"])  # own voice set (tools/soundgen) or None = vanilla sounds
    imports = {
        "com.terrassic.registry.ModEntities", "net.minecraft.server.level.ServerLevel", "net.minecraft.sounds.SoundEvent",
        "net.minecraft.sounds.SoundEvents", "net.minecraft.world.damagesource.DamageSource", "net.minecraft.world.entity.AgeableMob",
        "net.minecraft.world.entity.EntityType", "net.minecraft.world.entity.ai.attributes.AttributeSupplier",
        "net.minecraft.world.entity.ai.attributes.Attributes", "net.minecraft.world.entity.animal.Animal",
        "net.minecraft.world.item.crafting.Ingredient", "net.minecraft.world.level.Level",
    }
    body = []
    body.append(f"    /** Hitbox (blocks). Adult real length ~{size['real']} m. */")
    body.append(f"    public static final float WIDTH = {size['w']}F;")
    body.append(f"    public static final float HEIGHT = {size['h']}F;")
    body.append("    /** Renderer scale of the GeckoLib model and shadow radius, read by TerrassicClient. */")
    body.append(f"    public static final float MODEL_SCALE = {size['scale']}F;")
    body.append(f"    public static final float SHADOW = {size['shadow']}F;")
    if "food_tag" in s:
        imports.add("net.minecraft.tags.ItemTags")
        body.append(f"    private static final Ingredient FOOD = Ingredient.of({s['food_tag']});")
    else:
        imports.add("net.minecraft.world.item.Items")
        body.append(f"    private static final Ingredient FOOD = Ingredient.of({s['food']});")
    if s.get("roar") or s.get("display"):
        body.append("    private int displayCooldown;")
    if s.get("pack"):
        body.append("    private static boolean alertingPack;")
    body.append("")
    body.append(f"    public {cls}(EntityType<? extends {cls}> type, Level level) {{")
    body.append("        super(type, level);")
    if "step_height" in s:
        body.append(f"        this.setMaxUpStep({s['step_height']}F);")
    if s.get("amphibious"):
        imports.add("net.minecraft.world.level.pathfinder.BlockPathTypes")
        body.append("        this.setPathfindingMalus(BlockPathTypes.WATER, 0.0F);")
    body.append(f"        this.xpReward = {s.get('xp', 5)};")
    body.append("    }")
    body.append("")
    body.append("    public static AttributeSupplier.Builder createAttributes() {")
    body.append("        return Animal.createMobAttributes()")
    for k, v in s["attrs"].items():
        body.append(f"                .add(Attributes.{k}, {float(v)}D)")
    body[-1] += ";"
    body.append("    }")
    body.append("")
    body.append("    @Override\n    public String speciesId() {\n        return \"%s\";\n    }\n" % s["id"])
    body.append("    @Override\n    protected Ingredient food() {\n        return FOOD;\n    }\n")
    extras = []
    if base == "HerbivoreDinosaur":
        extras.append("graze")
    if s.get("roar"):
        extras.append("roar")
    if s.get("display"):
        extras.append("display")
    if s.get("call"):
        extras.append("call")
    if s.get("dig"):
        extras.append("dig")
    if s.get("musk"):
        extras.append("scent")
    if s.get("scoop"):
        extras.append("fish")
    if base == "PredatorDinosaur" and extras:
        body.append("    @Override\n    protected String[] extraActions() {\n        return new String[]{%s};\n    }\n" % ", ".join(f'"{e}"' for e in extras))
    elif base == "HerbivoreDinosaur" and len(extras) > 1:
        body.append("    @Override\n    protected String[] extraActions() {\n        return new String[]{%s};\n    }\n" % ", ".join(f'"{e}"' for e in extras))
    body.append(f"    @Override\n    protected float babyScale() {{\n        return {size['baby']}F;\n    }}\n")
    if "cull" in s:
        body.append(f"    @Override\n    protected double cullingInflate() {{\n        return {s['cull']}D;\n    }}\n")
    if "run" in s:
        body.append(f"    @Override\n    protected double runThresholdSqr() {{\n        return {s['run']}D;\n    }}\n")
    if "head" in s:
        body.append(f"    @Override\n    public int getMaxHeadYRot() {{\n        return {s['head'][0]};\n    }}\n")
        body.append(f"    @Override\n    public int getMaxHeadXRot() {{\n        return {s['head'][1]};\n    }}\n")
    if s.get("rideable"):
        body.append("    @Override\n    public boolean isRideable() {\n        return true;\n    }\n")
        body.append(f"    @Override\n    protected float riddenSpeedFactor() {{\n        return {s['ride_speed']}F;\n    }}\n")
        body.append(f"    @Override\n    public double getPassengersRidingOffset() {{\n        return {round(s['ride_offset'] * size['scale'], 2)}D * this.getScale();\n    }}\n")
        if "jump" in s:
            body.append(f"    @Override\n    protected double jumpStrength() {{\n        return {s['jump']}D;\n    }}\n")
        if s.get("ride_forward"):
            body.append(f"    @Override\n    protected double riderForwardOffset() {{\n        return {round(s['ride_forward'] * size['scale'], 2)}D;\n    }}\n")
    # cargo (docs/CARGA.md): every rideable species carries a chest, rows by real size; cargo=N overrides (0 = none)
    rows = s.get("cargo")
    if rows is None and s.get("rideable"):
        real = size["real"]
        rows = 6 if real >= 25 else 5 if real >= 15 else 4 if real >= 9 else 3 if real >= 6 else 2 if real >= 3.5 else 1
    if rows:
        body.append(f"    @Override\n    public int cargoRows() {{\n        return {rows};\n    }}\n")
    if s.get("platform"):
        body.append("    @Override\n    protected boolean platformSpecies() {\n        return true;\n    }\n")
    if s.get("shoulder"):
        body.append("    @Override\n    public boolean canPerch() {\n        return true;\n    }\n")
    if s.get("fisher"):
        body.append("    @Override\n    protected boolean perchFishes() {\n        return true;\n    }\n")
    if base == "SwimmingDinosaur":
        # tame = None (wild until knockout taming) | "feeding" (hand-fed) | "baby" (live-bearers: only calves take food)
        if s.get("tame"):
            body.append("    @Override\n    protected boolean tameable() {\n        return true;\n    }\n")
        if s.get("tame") == "baby":
            body.append("    @Override\n    public TameMethod tameMethod() {\n        return TameMethod.BABY_FEEDING;\n    }\n")
        if s.get("live_young"):
            body.append("    @Override\n    protected boolean liveYoung() {\n        return true;\n    }\n")
        if "dive" in s:
            body.append(f"    @Override\n    protected double diveSpeed() {{\n        return {s['dive']}D;\n    }}\n")
        if s.get("hunts_players") is False:
            body.append("    @Override\n    protected boolean huntsPlayers() {\n        return false;\n    }\n")
    if s.get("fights") is False:
        body.append("    @Override\n    protected boolean fightsBack() {\n        return false;\n    }\n")
    if s.get("hit_effects"):
        # status effects put on whatever this animal hits (ramming, venom, a stunning tail blow...)
        imports.add("net.minecraft.world.entity.Entity")
        imports.add("net.minecraft.world.entity.LivingEntity")
        imports.add("net.minecraft.world.effect.MobEffectInstance")
        imports.add("net.minecraft.world.effect.MobEffects")
        fx = "\n".join(f"            living.addEffect(new MobEffectInstance({e}, {d}, {a}));" for e, d, a in s["hit_effects"])
        body.append("    @Override\n    public boolean doHurtTarget(Entity target) {\n        boolean hit = super.doHurtTarget(target);\n"
                    "        if (hit && target instanceof LivingEntity living) {\n" + fx + "\n        }\n        return hit;\n    }\n")
    if base in ("FlyingDinosaur", "SwimmingDinosaur"):
        imports.add("net.minecraft.world.entity.LivingEntity")
        imports.add("net.minecraft.world.entity.animal.AbstractFish")   # the default prey; prey_imports only adds
        imports.update(s.get("prey_imports", []))
        body.append(f"    @Override\n    protected boolean isPrey(LivingEntity e) {{\n        return {s['prey']};\n    }}\n")
    if base == "PredatorDinosaur":
        imports.add("net.minecraft.world.entity.LivingEntity")
        body.append(f"    @Override\n    protected boolean isPrey(LivingEntity e) {{\n        return {s['prey']};\n    }}\n")
        if "prey_interval" in s:
            body.append(f"    @Override\n    protected int preyInterval() {{\n        return {s['prey_interval']};\n    }}\n")
        if s.get("hunts_players") is False:
            body.append("    @Override\n    protected boolean huntsPlayers() {\n        return false;\n    }\n")
        if s.get("feeding_tame"):
            body.append("    @Override\n    public TameMethod tameMethod() {\n        return TameMethod.FEEDING;\n    }\n")
    if s.get("egg_only") and base != "PredatorDinosaur":
        # egg / baby taming only (knockout taming later): adults ignore food offered by hand
        # (top level: this used to sit inside the predator branch, where its own condition made it dead code)
        body.append("    @Override\n    public TameMethod tameMethod() {\n        return TameMethod.BABY_FEEDING;\n    }\n")
    # extra goals
    goals = []
    if s.get("leap"):
        imports.add("net.minecraft.world.entity.ai.goal.LeapAtTargetGoal")
        goals.append("        this.goalSelector.addGoal(2, new LeapAtTargetGoal(this, 0.4F));")
    if s["id"] == "velociraptor":
        imports.add("net.minecraft.world.entity.ai.goal.AvoidEntityGoal")
        goals.append("        this.goalSelector.addGoal(2, new AvoidEntityGoal<>(this, Tyrannosaurus.class, 14.0F, 1.2D, 1.5D, e -> !this.isTame()));")
    if s.get("skittish"):
        imports.add("net.minecraft.world.entity.ai.goal.AvoidEntityGoal")
        imports.add("net.minecraft.world.entity.EntitySelector")
        imports.add("net.minecraft.world.entity.player.Player")
        goals.append("        this.goalSelector.addGoal(2, new AvoidEntityGoal<>(this, Player.class, 8.0F, 1.1D, 1.4D,\n                e -> EntitySelector.NO_CREATIVE_OR_SPECTATOR.test(e) && !this.isTame() && this.getTarget() == null));")
    if s.get("fish"):
        imports.add("net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal")
        imports.add("net.minecraft.world.entity.animal.AbstractFish")
        goals.append("        this.targetSelector.addGoal(5, new NearestAttackableTargetGoal<>(this, AbstractFish.class, 40, true, false, e -> this.canHunt()));")
    if goals:
        body.append("    @Override\n    protected void addExtraGoals() {\n" + "\n".join(goals) + "\n    }\n")
    if s.get("amphibious"):
        # walks the river bed and swims across: the frog / axolotl navigation
        imports.add("net.minecraft.world.entity.ai.navigation.AmphibiousPathNavigation")
        imports.add("net.minecraft.world.entity.ai.navigation.PathNavigation")
        body.append("    @Override\n    protected PathNavigation createNavigation(Level level) {\n        return new AmphibiousPathNavigation(this, level);\n    }\n")
    if s.get("fish"):
        body.append("    @Override\n    public boolean canBreatheUnderwater() {\n        return true;\n    }\n")
        body.append("    @Override\n    public boolean isPushedByFluid() {\n        return false;\n    }\n")
    if s.get("roar") or s.get("display"):
        imports.add("net.minecraft.world.entity.LivingEntity")
        anim = "roar" if s.get("roar") else "display"
        snd = "SoundEvents.RAVAGER_ROAR, 3.0F, %sF" % (0.55 if s["id"] == "tyrannosaurus" else 0.7) if s.get("roar") else "SoundEvents.HOGLIN_ANGRY, 1.2F, 1.3F"
        if voice and "threat" in VOICE_SETS[voice[0]]:
            snd = f"ModSounds.{sound_field(voice[0], 'threat')}.get(), 3.0F, {voice[1]}F"
        body.append(f"""    @Override
    public void setTarget(LivingEntity target) {{
        LivingEntity previous = this.getTarget();
        super.setTarget(target);
        if (!this.level().isClientSide() && target != null && previous == null && this.displayCooldown <= 0 && !this.isVehicle()) {{
            this.displayCooldown = 400;
            triggerAnim(ACTION_CONTROLLER, "{anim}");
            this.playSound({snd});
        }}
    }}

    @Override
    protected void customServerAiStep() {{
        super.customServerAiStep();
        if (this.displayCooldown > 0) {{
            this.displayCooldown--;
        }}
    }}
""")
    if s.get("pack"):
        imports.add("net.minecraft.world.entity.LivingEntity")
        body.append("""    @Override
    public void setTarget(LivingEntity target) {
        super.setTarget(target);
        if (target != null && !this.level().isClientSide() && !alertingPack && !this.isTame()) {
            alertingPack = true;
            try {
                for (Velociraptor other : this.level().getEntitiesOfClass(Velociraptor.class, this.getBoundingBox().inflate(16.0D),
                        r -> r != this && r != target && r.getTarget() == null && !r.isBaby() && !r.isTame())) {
                    other.setTarget(target);
                }
            } finally {
                alertingPack = false;
            }
        }
    }
""")
    if s.get("call"):
        imports.add("net.minecraft.world.damagesource.DamageSource")
        call = "this.callOut()" if s.get("calm") else 'triggerAnim(ACTION_CONTROLLER, "call")'
        body.append(f"""    @Override
    public boolean hurt(DamageSource source, float amount) {{
        boolean hurt = super.hurt(source, amount);
        if (hurt && !this.level().isClientSide() && this.random.nextInt(3) == 0) {{
            {call};
        }}
        return hurt;
    }}

    @Override
    public void playAmbientSound() {{
        super.playAmbientSound();
        if (!this.level().isClientSide() && this.random.nextInt(3) == 0) {{
            {call};
        }}
    }}
""")
        if s.get("calm"):
            # the calming call: herbivores within 12 blocks stop panicking, drop their target and heal a little
            imports.add("net.minecraft.server.level.ServerLevel")
            imports.add("net.minecraft.world.effect.MobEffectInstance")
            imports.add("net.minecraft.world.effect.MobEffects")
            body.append("""    /** The crest call: every herbivore within 12 blocks calms down (panic and target cleared) and regenerates briefly. */
    private void callOut() {
        triggerAnim(ACTION_CONTROLLER, "call");
        if (this.level() instanceof ServerLevel server) {
            for (HerbivoreDinosaur other : server.getEntitiesOfClass(HerbivoreDinosaur.class, this.getBoundingBox().inflate(12.0D), e -> e != this)) {
                other.setLastHurtByMob(null);
                other.setTarget(null);
                other.getNavigation().stop();
                other.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 100, 0));
            }
        }
    }
""")
    if s.get("musk"):
        # the musk: when hurt or now and then, a scent that calms the herbivores around and draws the wild predators onto itself
        imports.update({"net.minecraft.server.level.ServerLevel", "net.minecraft.world.damagesource.DamageSource",
                        "net.minecraft.core.particles.ParticleTypes", "net.minecraft.world.effect.MobEffectInstance",
                        "net.minecraft.world.effect.MobEffects"})
        body.append("""    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hurt = super.hurt(source, amount);
        if (hurt && !this.level().isClientSide() && this.random.nextInt(2) == 0) {
            this.releaseMusk();
        }
        return hurt;
    }

    @Override
    public void playAmbientSound() {
        super.playAmbientSound();
        if (!this.level().isClientSide() && !this.isBaby() && this.random.nextInt(4) == 0) {
            this.releaseMusk();
        }
    }

    /** The musk: herbivores within 12 blocks calm down (panic and target cleared, brief regeneration); wild adult
     *  predators within 12 blocks get irritated and turn on this animal instead of whatever they were hunting. */
    private void releaseMusk() {
        triggerAnim(ACTION_CONTROLLER, "scent");
        if (this.level() instanceof ServerLevel server) {
            server.sendParticles(ParticleTypes.SNEEZE, this.getX(), this.getY() + this.getBbHeight() * 0.8D, this.getZ(),
                    10, this.getBbWidth() * 0.5D, 0.3D, this.getBbWidth() * 0.5D, 0.02D);
            for (HerbivoreDinosaur other : server.getEntitiesOfClass(HerbivoreDinosaur.class, this.getBoundingBox().inflate(12.0D), e -> e != this)) {
                other.setLastHurtByMob(null);
                other.setTarget(null);
                other.getNavigation().stop();
                other.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 100, 0));
            }
            for (PredatorDinosaur predator : server.getEntitiesOfClass(PredatorDinosaur.class, this.getBoundingBox().inflate(12.0D),
                    p -> !p.isTame() && !p.isBaby())) {
                predator.setTarget(this);
            }
        }
    }
""")
    if s.get("scoop"):
        # fishing: idle at the water's edge it scoops with both arms now and then; a tame one brings up a fish or some weed
        imports.update({"net.minecraft.server.level.ServerLevel", "net.minecraft.core.BlockPos", "net.minecraft.core.particles.ParticleTypes",
                        "net.minecraft.tags.FluidTags", "net.minecraft.world.item.ItemStack"})
        body.append("""    /** Fishing: idle within two blocks of water it scoops with both arms now and then (splash); a tame one brings up a
     *  cod, a salmon, kelp or seagrass and drops it at its feet. */
    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.isBaby() || this.getTarget() != null || this.isVehicle() || this.isInSittingPose() || !this.getNavigation().isDone()
                || this.random.nextInt(700) != 0 || !(this.level() instanceof ServerLevel server)) {
            return;
        }
        BlockPos feet = this.blockPosition();
        BlockPos water = null;
        for (BlockPos p : new BlockPos[]{feet.north(2), feet.south(2), feet.east(2), feet.west(2),
                feet.north(2).below(), feet.south(2).below(), feet.east(2).below(), feet.west(2).below()}) {
            if (server.getFluidState(p).is(FluidTags.WATER)) {
                water = p;
                break;
            }
        }
        if (water == null) {
            return;
        }
        triggerAnim(ACTION_CONTROLLER, "fish");
        server.sendParticles(ParticleTypes.SPLASH, water.getX() + 0.5D, water.getY() + 1.0D, water.getZ() + 0.5D, 12, 0.4D, 0.1D, 0.4D, 0.1D);
        this.playSound(SoundEvents.GENERIC_SPLASH, 0.6F, 1.0F);
        if (!this.isTame()) {
            return;
        }
        int roll = this.random.nextInt(100);
        ItemStack found = ItemStack.EMPTY;
        if (roll < 35) {
            found = new ItemStack(Items.COD);
        } else if (roll < 60) {
            found = new ItemStack(Items.SALMON);
        } else if (roll < 75) {
            found = new ItemStack(Items.KELP);
        } else if (roll < 85) {
            found = new ItemStack(Items.SEAGRASS);
        }
        if (!found.isEmpty()) {
            this.spawnAtLocation(found);
        }
    }
""")
    if s.get("forage"):
        # browsing: idle under a tree (or carrying a rider), now and then it hooks a leaf block down and breaks it (drops as usual)
        imports.update({"net.minecraft.core.BlockPos", "net.minecraft.tags.BlockTags", "net.minecraft.world.level.GameRules",
                        "net.minecraft.world.level.block.state.BlockState", "net.minecraft.world.phys.AABB", "java.util.ArrayList", "java.util.List"})
        body.append("""    /** Browsing: idle under a tree, or now and then with a rider, it hooks a leaf block down with the claws and breaks it
     *  (the leaves drop their usual saplings, sticks and apples). Respects mobGriefing. */
    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.isBaby() || this.getTarget() != null || this.isInSittingPose() || !this.level().getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING)
                || this.random.nextInt(this.isVehicle() ? 120 : 400) != 0) {
            return;
        }
        AABB box = this.getBoundingBox().inflate(2.0D, 0.0D, 2.0D).expandTowards(0.0D, 2.0D, 0.0D);
        List<BlockPos> leaves = new ArrayList<>();
        for (BlockPos pos : BlockPos.betweenClosed((int) Math.floor(box.minX), (int) Math.floor(box.minY + this.getBbHeight() * 0.4D), (int) Math.floor(box.minZ),
                (int) Math.floor(box.maxX), (int) Math.floor(box.maxY), (int) Math.floor(box.maxZ))) {
            BlockState state = this.level().getBlockState(pos);
            if (state.is(BlockTags.LEAVES)) {
                leaves.add(pos.immutable());
            }
        }
        if (!leaves.isEmpty()) {
            triggerAnim(ACTION_CONTROLLER, "graze");
            this.level().destroyBlock(leaves.get(this.random.nextInt(leaves.size())), true, this);
        }
    }
""")
    if s.get("trample"):
        # the charge: moving fast after a target or under a rider, it clears the leaves and plants in its way
        imports.update({"net.minecraft.core.BlockPos", "net.minecraft.tags.BlockTags", "net.minecraft.world.level.GameRules",
                        "net.minecraft.world.level.block.Blocks", "net.minecraft.world.level.block.state.BlockState", "net.minecraft.world.phys.AABB"})
        body.append("""    /** The charge: moving fast with a target or a rider, it breaks the leaves and plants in its way. */
    @Override
    public void aiStep() {
        super.aiStep();
        if (!this.level().isClientSide() && !this.isBaby() && (this.getTarget() != null || this.isVehicle())
                && this.getDeltaMovement().horizontalDistanceSqr() > 0.01D
                && this.level().getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING)) {
            AABB box = this.getBoundingBox().inflate(0.4D, 0.0D, 0.4D);
            for (BlockPos pos : BlockPos.betweenClosed((int) Math.floor(box.minX), (int) Math.floor(box.minY), (int) Math.floor(box.minZ),
                    (int) Math.floor(box.maxX), (int) Math.floor(box.maxY), (int) Math.floor(box.maxZ))) {
                BlockState state = this.level().getBlockState(pos);
                if (state.is(BlockTags.LEAVES) || state.is(BlockTags.FLOWERS) || state.is(BlockTags.SAPLINGS)
                        || state.is(Blocks.GRASS) || state.is(Blocks.TALL_GRASS) || state.is(Blocks.FERN) || state.is(Blocks.LARGE_FERN)
                        || state.is(Blocks.DEAD_BUSH) || state.is(Blocks.SWEET_BERRY_BUSH)) {
                    this.level().destroyBlock(pos, true, this);
                }
            }
        }
    }
""")
    if s.get("dig"):
        # digging: idle on soft ground it scrapes with the forefeet now and then; a tame one turns something up.
        # dig=True: roots, vegetables, bones, shallow fossils, flint on gravel; dig="tubers": roots and vegetables, no fossils
        imports.update({"net.minecraft.server.level.ServerLevel", "net.minecraft.core.BlockPos", "net.minecraft.core.particles.BlockParticleOption",
                        "net.minecraft.core.particles.ParticleTypes", "net.minecraft.tags.BlockTags",
                        "net.minecraft.world.item.ItemStack", "net.minecraft.world.level.block.Blocks", "net.minecraft.world.level.block.state.BlockState"})
        if s["dig"] == "tubers":
            what = "roots and tubers"
            loot = """        if (roll < 24) {
            found = new ItemStack(Items.HANGING_ROOTS);
        } else if (roll < 58) {
            found = new ItemStack(this.random.nextBoolean() ? Items.CARROT : Items.POTATO);
        } else if (roll < 72) {
            found = new ItemStack(Items.BEETROOT);
        } else if (roll < 78) {
            found = new ItemStack(Items.BONE);
        } else if (roll < 84 && ground.is(Blocks.GRAVEL)) {
            found = new ItemStack(Items.FLINT);
        }"""
        else:
            what = "roots, a vegetable, a bone or a shallow fossil"
            imports.update({"net.minecraft.world.item.Item", "com.terrassic.registry.ModItems",
                            "dev.architectury.registry.registries.RegistrySupplier", "java.util.ArrayList", "java.util.List"})
            loot = """        if (roll < 28) {
            found = new ItemStack(Items.HANGING_ROOTS);
        } else if (roll < 44) {
            found = new ItemStack(this.random.nextBoolean() ? Items.CARROT : Items.POTATO);
        } else if (roll < 54) {
            found = new ItemStack(Items.BEETROOT);
        } else if (roll < 66) {
            found = new ItemStack(Items.BONE);
        } else if (roll < 74) {
            List<RegistrySupplier<Item>> fossils = new ArrayList<>(ModItems.FOSSILS.values());
            found = new ItemStack(fossils.get(this.random.nextInt(fossils.size())).get());
        } else if (roll < 80 && ground.is(Blocks.GRAVEL)) {
            found = new ItemStack(Items.FLINT);
        }"""
        body.append("""    /** Digging: idle on dirt, sand, gravel or clay it scrapes with the forefeet now and then; a tame one turns up
     *  """ + what + """ (dropped at its feet). */
    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (this.isBaby() || this.getTarget() != null || this.isVehicle() || this.isInSittingPose() || !this.getNavigation().isDone()
                || this.random.nextInt(900) != 0 || !(this.level() instanceof ServerLevel server)) {
            return;
        }
        BlockPos below = this.blockPosition().below();
        BlockState ground = server.getBlockState(below);
        if (!(ground.is(BlockTags.DIRT) || ground.is(BlockTags.SAND) || ground.is(Blocks.GRAVEL) || ground.is(Blocks.CLAY))) {
            return;
        }
        triggerAnim(ACTION_CONTROLLER, "dig");
        server.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, ground), this.getX(), this.getY() + 0.1D, this.getZ(),
                12, 0.3D, 0.1D, 0.3D, 0.05D);
        this.playSound(ground.getSoundType().getHitSound(), 0.8F, 1.0F);
        if (!this.isTame()) {
            return;
        }
        int roll = this.random.nextInt(100);
        ItemStack found = ItemStack.EMPTY;
""" + loot + """
        if (!found.isEmpty()) {
            this.spawnAtLocation(found);
        }
    }
""")
    if s.get("nurse"):
        imports.update({"net.minecraft.core.particles.ParticleTypes"})
        body.append("""    /** "Good mother": every 5 s, babies of any species within 10 blocks of an adult grow 5 s more (2x as fast). */
    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (!this.isBaby() && this.tickCount % 100 == 0 && this.level() instanceof ServerLevel server) {
            for (DinosaurEntity baby : server.getEntitiesOfClass(DinosaurEntity.class, this.getBoundingBox().inflate(10.0D),
                    DinosaurEntity::isBaby)) {
                baby.ageUp(5);
                server.sendParticles(ParticleTypes.HAPPY_VILLAGER, baby.getX(), baby.getY() + baby.getBbHeight(), baby.getZ(),
                        2, 0.3D, 0.2D, 0.3D, 0.0D);
            }
        }
    }
""")
    # breeding offspring + sounds
    body.append(f"""    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob partner) {{
        return ModEntities.{s['id'].upper()}.get().create(level);
    }}
""")
    amb, hurt, death, pitch, vol, interval = s["sounds"]
    amb, hurt, death = (f"SoundEvents.{x}" for x in (amb, hurt, death))
    if voice:
        vset, pitch = voice
        amb, hurt, death = (f"ModSounds.{sound_field(vset, e)}.get()" for e in ("ambient", "hurt", "death"))
    body.append(f"""    @Override
    protected SoundEvent getAmbientSound() {{
        return {amb};
    }}

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {{
        return {hurt};
    }}

    @Override
    protected SoundEvent getDeathSound() {{
        return {death};
    }}

    @Override
    public float getVoicePitch() {{
        return super.getVoicePitch() * {pitch}F;
    }}

    @Override
    protected float getSoundVolume() {{
        return {vol}F;
    }}

    @Override
    public int getAmbientSoundInterval() {{
        return {interval};
    }}""")
    if "step" in s:
        imports.add("net.minecraft.core.BlockPos")
        imports.add("net.minecraft.world.level.block.state.BlockState")
        st, v, p = s["step"]
        st = f"SoundEvents.{st}"
        if voice and "step" in VOICE_SETS[voice[0]]:
            st, p = f"ModSounds.{sound_field(voice[0], 'step')}.get()", 1.0
        body.append(f"""
    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {{
        this.playSound({st}, {v}F, {p}F);
    }}""")
    if voice and "flap" in VOICE_SETS[voice[0]]:
        body.append(f"""
    @Override
    protected SoundEvent flapSound() {{
        return ModSounds.{sound_field(voice[0], 'flap')}.get();
    }}""")
    if voice:
        imports.add("com.terrassic.registry.ModSounds")
    src = "package com.terrassic.entity;\n\n" + "\n".join(f"import {i};" for i in sorted(imports)) + "\n\n"
    src += f"/**\n * {s['doc']}\n *\n * Generated by tools/javagen/gen_species.py - edit the table there.\n */\n"
    src += f"public class {cls} extends {base} {{\n" + "\n".join(body) + "\n}\n"
    with open(os.path.join(OUT, cls + ".java"), "w") as f:
        f.write(src)


def gen_guide(bounds):
    """research/GuideSpecies.java: one Field Guide entry per species, in roster order."""
    rows = []
    for s in SPECIES:
        sid, size, g = s["id"], SIZES[s["id"]], GUIDE[s["id"]]
        (x0, y0, z0), (x1, y1, z1) = bounds[sid]
        k = size["scale"] / 16.0
        biggest = max((z1 - z0) * k, (y1 - y0) * k, (x1 - x0) * k)
        gui = round(100.0 / biggest, 2)  # pixels per block so the adult fits a ~100 px box in the notebook
        egg_only = s.get("egg_only", (s["base"] == "PredatorDinosaur" and not s.get("feeding_tame")) or s.get("tame") == "baby")
        rows.append(f'            new GuideSpecies("{sid}", "{g["era"]}", "{g["diet"]}", {size["real"]}F, {str(bool(s.get("rideable"))).lower()}, '
                    f'{str(egg_only).lower()}, {g["fossil"]}, {gui}F)')
    src = f"""package com.terrassic.research;

import java.util.List;

/**
 * Field Guide entry of a species: era, diet, real length (m), whether it can be ridden, whether only eggs/babies
 * can be tamed, how common its fossil is and the scale used to draw it in the notebook (pixels per block).
 * Names and texts are translation keys: entity.terrassic.&lt;id&gt; and guide.terrassic.&lt;id&gt;.*.
 *
 * Generated by tools/javagen/gen_species.py - edit the GUIDE table there.
 */
public record GuideSpecies(String id, String era, String diet, float length, boolean rideable, boolean eggOnly,
                           int fossilWeight, float guiScale) {{
    public static final List<GuideSpecies> ALL = List.of(
{(","+chr(10)).join(rows)});

    public static GuideSpecies byId(String id) {{
        for (GuideSpecies s : ALL) {{
            if (s.id.equals(id)) {{
                return s;
            }}
        }}
        return null;
    }}
}}
"""
    with open(GUIDE_OUT, "w") as f:
        f.write(src)


# ---- per-species registrations, written between "BEGIN GENERATED <tag>" / "END GENERATED <tag>" marker lines in
# the hand-written registry classes, so adding a species never needs Java edits by hand.
JAVA = os.path.join(os.path.dirname(OUT))
GROUP_TITLE = {"PredatorDinosaur": "predators", "HerbivoreDinosaur": "herbivores", "FlyingDinosaur": "flyers",
               "SwimmingDinosaur": "marine reptiles"}


def fill(path, tag, lines):
    """Replaces the lines between the BEGIN/END GENERATED <tag> markers (markers kept)."""
    with open(path, encoding="utf-8") as f:
        src = f.read().split("\n")
    mark = lambda word: re.compile(rf"{word} GENERATED {re.escape(tag)}( \(|$)")  # noqa: E731
    begin = [i for i, l in enumerate(src) if mark("BEGIN").search(l.rstrip())]
    end = [i for i, l in enumerate(src) if mark("END").search(l.rstrip())]
    if len(begin) != 1 or len(end) != 1 or end[0] < begin[0]:
        raise SystemExit(f"{path}: markers for '{tag}' missing or broken")
    src[begin[0] + 1:end[0]] = lines
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(src))


def gen_registrations():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from gen_resources import SPECIES as NAMES  # (en, pt, es, large egg or None)

    reg = os.path.join(JAVA, "registry")
    up = lambda s: s["id"].upper()  # noqa: E731
    imports = [f"import com.terrassic.entity.{s['cls']};" for s in sorted(SPECIES, key=lambda s: s["cls"])]

    fields, group = [], None
    for s in SPECIES:
        if s["base"] != group:
            group = s["base"]
            fields.append(f"    // ---- {GROUP_TITLE[group]}")
        cat = "WATER_CREATURE" if s["base"] == "SwimmingDinosaur" else "CREATURE"
        fields.append(f"    public static final RegistrySupplier<EntityType<{s['cls']}>> {up(s)} =")
        fields.append(f"            mob(\"{s['id']}\", {s['cls']}::new, MobCategory.{cat}, {s['cls']}.WIDTH, {s['cls']}.HEIGHT, "
                      f"{WORLD[s['id']]['track']});")
    attrs = [f"        EntityAttributeRegistry.register({up(s)}, {s['cls']}::createAttributes);" for s in SPECIES]
    path = os.path.join(reg, "ModEntities.java")
    fill(path, "imports", imports)
    fill(path, "species", fields)
    fill(path, "attributes", attrs)

    fill(os.path.join(reg, "ModItems.java"), "spawn eggs",
         [f"    public static final RegistrySupplier<Item> {up(s)}_SPAWN_EGG = egg(\"{s['id']}\", ModEntities.{up(s)});"
          for s in SPECIES])
    fill(os.path.join(reg, "ModItems.java"), "hides",
         [f"    public static final RegistrySupplier<Item> {up(s)}_HIDE = hide(\"{s['id']}\");" for s in SPECIES])
    fill(os.path.join(reg, "ModBlocks.java"), "eggs",
         [f"        egg(\"{s['id']}\", ModEntities.{up(s)}, {str(NAMES[s['id']][3]).lower()});"
          for s in SPECIES if NAMES[s["id"]][3] is not None])

    path = os.path.join(JAVA, "client", "TerrassicClient.java")
    fill(path, "imports", imports)
    fill(path, "renderers", [f"        renderer(ModEntities.{up(s)}, \"{s['id']}\", {s['cls']}.MODEL_SCALE, {s['cls']}.SHADOW);"
                             for s in SPECIES])

    path = os.path.join(JAVA, "world", "ModSpawns.java")
    table = [" *  %-19s %-31s %-7s %s" % ("Species", "Biomes", "weight", "group")]
    placements, preds, adds = [], [], []
    used = [b for b in BIOMES if any(b in WORLD[s["id"]]["biomes"] for s in SPECIES)]
    for s in SPECIES:
        w = WORLD[s["id"]]
        lo, hi = w["group"]
        table.append(" *  %-19s %-31s %-7s %s" % (s["cls"], ", ".join(BIOMES[b][1] for b in w["biomes"]), w["weight"],
                                                 f"{lo}-{hi}" if lo != hi else lo))
        if s["base"] == "FlyingDinosaur":
            placements.append(f"        SpawnPlacementsRegistry.register(ModEntities.{up(s)}, SpawnPlacements.Type.ON_GROUND,")
            placements.append("                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, FlyingDinosaur::checkFlyerSpawnRules);")
        elif s["base"] == "SwimmingDinosaur":
            placements.append(f"        SpawnPlacementsRegistry.register(ModEntities.{up(s)}, SpawnPlacements.Type.IN_WATER,")
            placements.append("                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, SwimmingDinosaur::checkSeaSpawnRules);")
        else:
            placements.append(f"        placement(ModEntities.{up(s)});")
        cat = "MobCategory.WATER_CREATURE, " if s["base"] == "SwimmingDinosaur" else ""
        adds.append(f"            if ({' || '.join(_camel(b) for b in w['biomes'])}) {{")
        adds.append(f"                add(props, {cat}ModEntities.{up(s)}.get(), {w['weight']}, {lo}, {hi});")
        adds.append("            }")
    for b in used:
        preds.append(f"            boolean {_camel(b)} = {BIOMES[b][0]};")
    fill(path, "table", table)
    fill(path, "placements", placements)
    fill(path, "biomes", preds + [""] + adds)


def _camel(name):
    head, *rest = name.split("_")
    return head + "".join(r.capitalize() for r in rest)


if __name__ == "__main__":
    bounds = model_bounds()
    for s in SPECIES:
        gen(s, bounds)
    gen_guide(bounds)
    gen_registrations()
    print("generated", len(SPECIES))
