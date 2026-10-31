"""Generates the JSON resources: item/block models, blockstates, lang (en_us, pt_br, es_es + other Spanish
variants), recipes and loot tables."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RES = os.path.join(ROOT, "common", "src", "main", "resources")
A = os.path.join(RES, "assets", "terrassic")
D = os.path.join(RES, "data", "terrassic")
sys.path.insert(0, os.path.join(ROOT, "tools", "spritegen"))
from rex_extras import CUSTOM_EGGS as REX_EGGS  # noqa: E402  (eggs with their own nest model: the T. rex pair)
from ptera_extras import CUSTOM_EGGS as PTERA_EGGS  # noqa: E402  (the Pteranodon's clutch in a sand scrape)
from rapt_extras import CUSTOM_EGGS as RAPT_EGGS  # noqa: E402  (the Velociraptor's clutch in a desert scrape)
CUSTOM_EGGS = {**REX_EGGS, **PTERA_EGGS, **RAPT_EGGS}

SPECIES = {  # id: (en, pt, es, large egg; None = no egg block, e.g. live-bearing marine reptiles)
    "tyrannosaurus": ("Tyrannosaurus", "Tiranossauro", "Tiranosaurio", True),
    "spinosaurus": ("Spinosaurus", "Espinossauro", "Espinosaurio", True),
    "dilophosaurus": ("Dilophosaurus", "Dilofossauro", "Dilofosaurio", False),
    "velociraptor": ("Velociraptor", "Velociraptor", "Velociraptor", False),
    "compsognathus": ("Compsognathus", "Compsognato", "Compsognathus", False),
    "triceratops": ("Triceratops", "Tricerátops", "Triceratops", True),
    "styracosaurus": ("Styracosaurus", "Estiracossauro", "Styracosaurus", True),
    "pachyrhinosaurus": ("Pachyrhinosaurus", "Paquirrinossauro", "Pachyrhinosaurus", True),
    "protoceratops": ("Protoceratops", "Protoceratops", "Protoceratops", False),
    "leptoceratops": ("Leptoceratops", "Leptoceratops", "Leptoceratops", False),
    "vegavis": ("Vegavis", "Vegavis", "Vegavis", False),
    "mesodma": ("Mesodma", "Mesodma", "Mesodma", False),
    "basilemys": ("Basilemys", "Basilemys", "Basilemys", False),
    "enchodus": ("Enchodus", "Enchodus", "Enchodus", None),
    "lepisosteus": ("Lepisosteus", "Lepisosteus", "Lepisosteus", None),
    "stegosaurus": ("Stegosaurus", "Estegossauro", "Estegosaurio", True),
    "ankylosaurus": ("Ankylosaurus", "Anquilossauro", "Anquilosaurio", True),
    "euoplocephalus": ("Euoplocephalus", "Euoplocéfalo", "Euoplocephalus", True),
    "therizinosaurus": ("Therizinosaurus", "Terizinossauro", "Therizinosaurus", True),
    "deinocheirus": ("Deinocheirus", "Deinocheirus", "Deinocheirus", True),
    "brachiosaurus": ("Brachiosaurus", "Braquiossauro", "Braquiosaurio", True),
    "alamosaurus": ("Alamosaurus", "Alamossauro", "Alamosaurio", True),
    "saltasaurus": ("Saltasaurus", "Saltassauro", "Saltasaurio", True),
    "argentinosaurus": ("Argentinosaurus", "Argentinossauro", "Argentinosaurio", True),
    "opisthocoelicaudia": ("Opisthocoelicaudia", "Opisthocoelicaudia", "Opisthocoelicaudia", True),
    "dreadnoughtus": ("Dreadnoughtus", "Dreadnoughtus", "Dreadnoughtus", True),
    "giganotosaurus": ("Giganotosaurus", "Giganotossauro", "Giganotosaurio", True),
    "carcharodontosaurus": ("Carcharodontosaurus", "Carcarodontossauro", "Carcarodontosaurio", True),
    "carnotaurus": ("Carnotaurus", "Carnotauro", "Carnotauro", True),
    "tarbosaurus": ("Tarbosaurus", "Tarbossauro", "Tarbosaurio", True),
    "daspletosaurus": ("Daspletosaurus", "Daspletossauro", "Daspletosaurio", True),
    "albertosaurus": ("Albertosaurus", "Albertossauro", "Albertosaurio", True),
    "majungasaurus": ("Majungasaurus", "Majungassauro", "Majungasaurio", True),
    "dakotaraptor": ("Dakotaraptor", "Dakotaraptor", "Dakotaraptor", False),
    "troodon": ("Troodon", "Troodon", "Troodon", False),
    "oviraptor": ("Oviraptor", "Oviraptor", "Oviraptor", False),
    "citipati": ("Citipati", "Citipati", "Citipati", False),
    "mononykus": ("Mononykus", "Mononykus", "Mononykus", False),
    "didelphodon": ("Didelphodon", "Didelphodon", "Didelphodon", False),
    "parasaurolophus": ("Parasaurolophus", "Parassaurolofo", "Parasaurolophus", True),
    "pachycephalosaurus": ("Pachycephalosaurus", "Paquicefalossauro", "Paquicefalosaurio", False),
    "thescelosaurus": ("Thescelosaurus", "Tescelossauro", "Thescelosaurus", False),
    "gallimimus": ("Gallimimus", "Galimimo", "Gallimimus", False),
    "struthiomimus": ("Struthiomimus", "Estrutiomimo", "Struthiomimus", False),
    "maiasaura": ("Maiasaura", "Maiassaura", "Maiasaura", False),
    "pteranodon": ("Pteranodon", "Pteranodonte", "Pteranodonte", False),
    "quetzalcoatlus": ("Quetzalcoatlus", "Quetzalcoatlus", "Quetzalcoatlus", False),
    "hatzegopteryx": ("Hatzegopteryx", "Hatzegopteryx", "Hatzegopteryx", False),
    "ichthyornis": ("Ichthyornis", "Ictiórnis", "Ictiornis", False),
    "mosasaurus": ("Mosasaurus", "Mosassauro", "Mosasaurio", None),
    "tylosaurus": ("Tylosaurus", "Tilossauro", "Tilosaurio", None),
    "elasmosaurus": ("Elasmosaurus", "Elasmossauro", "Elasmosaurio", None),
    "xiphactinus": ("Xiphactinus", "Xifactino", "Xiphactinus", None),
    "archelon": ("Archelon", "Archelon", "Archelon", True),
    "hesperornis": ("Hesperornis", "Hesperórnis", "Hesperornis", False),
    "deinosuchus": ("Deinosuchus", "Deinossuco", "Deinosuchus", True),
    "baurusuchus": ("Baurusuchus", "Baurussuco", "Baurusuchus", False),
    "edmontosaurus": ("Edmontosaurus", "Edmontossauro", "Edmontosaurio", True),
    "corythosaurus": ("Corythosaurus", "Coritossauro", "Corythosaurus", False),
}

ITEMS = {  # id: (en, pt, es, model parent)
    "rex_tooth": ("T. rex Tooth", "Dente de Tiranossauro", "Diente de Tiranosaurio", "item/generated"),
    "mosasaurus_tooth": ("Mosasaurus Tooth", "Dente de Mosassauro", "Diente de Mosasaurio", "item/generated"),
    "triceratops_horn": ("Triceratops Horn", "Chifre de Tricerátops", "Cuerno de Triceratops", "item/generated"),
    "ankylosaurus_club": ("Ankylosaurus Tail Club", "Clava Caudal de Anquilossauro", "Maza Caudal de Anquilosaurio", "item/generated"),
    "flint_knife": ("Flint Knife", "Faca de Sílex", "Cuchillo de Sílex", "item/handheld"),
    "flint_hatchet": ("Flint Hatchet", "Machadinha de Sílex", "Hacha de Mano de Sílex", "item/handheld"),
    "bone_club": ("Bone Club", "Clava de Osso", "Garrote de Hueso", "item/handheld"),
    "flint_spear": ("Flint Spear", "Lança de Sílex", "Lanza de Sílex", "item/handheld"),
    "horn_spear": ("Horn Spear", "Lança de Chifre", "Lanza de Cuerno", "item/handheld"),
    "rex_tooth_dagger": ("T. rex Tooth Dagger", "Adaga de Dente de Tiranossauro", "Daga de Diente de Tiranosaurio", "item/handheld"),
    "tail_club": ("Tail Club", "Clava de Cauda", "Garrote de Cola", "item/handheld"),
    "platform_saddle": ("Platform Saddle", "Sela de Plataforma", "Silla de Plataforma", "item/generated"),
    # species saddles, like ARK: each big rider has its own, with its own recipe (the T. rex first)
    "tyrannosaurus_saddle": ("T. rex Saddle", "Sela de Tiranossauro", "Silla de Tiranosaurio", "item/generated"),
    "pteranodon_saddle": ("Pteranodon Saddle", "Sela de Pteranodonte", "Silla de Pteranodonte", "item/generated"),
    # not a saddle: a hunting vest for the Velociraptor, armour for an animal too small to ride
    "velociraptor_harness": ("Hunting Harness", "Arreio de Caça", "Arnés de caza", "item/generated"),
    # Cretaceous food (docs/FAUNA.md): what the animals drop instead of vanilla beef, mutton and chicken
    "raw_dino_meat": ("Raw Dino Meat", "Carne de Dinossauro Crua", "Carne de Dinosaurio Cruda", "item/generated"),
    "cooked_dino_meat": ("Cooked Dino Meat", "Carne de Dinossauro Assada", "Carne de Dinosaurio Asada", "item/generated"),
    "raw_prime_meat": ("Raw Prime Meat", "Carne Nobre Crua", "Carne Selecta Cruda", "item/generated"),
    "cooked_prime_meat": ("Cooked Prime Meat", "Carne Nobre Assada", "Carne Selecta Asada", "item/generated"),
    # the fish of the Cretaceous waters (docs/FAUNA.md): Enchodus in the sea (the cod's seat)
    "enchodus": ("Raw Enchodus", "Enchodus Cru", "Enchodus Crudo", "item/generated"),
    "cooked_enchodus": ("Cooked Enchodus", "Enchodus Assado", "Enchodus Asado", "item/generated"),
    "lepisosteus": ("Raw Gar", "Peixe-agulha Cru", "Pejelagarto Crudo", "item/generated"),
    "cooked_lepisosteus": ("Cooked Gar", "Peixe-agulha Assado", "Pejelagarto Asado", "item/generated"),
    # knockout taming (docs/DOMESTICACAO.md)
    "blowgun": ("Blowgun", "Zarabatana", "Cerbatana", "item/handheld"),
    "tranq_dart": ("Narcotic Dart", "Dardo de Narcótico", "Dardo Narcótico", "item/generated"),
    "hunting_bow": ("Hunting Bow", "Arco de Caça", "Arco de Caza", "minecraft:item/bow"),
    "flint_arrow": ("Flint Arrow", "Flecha de Sílex", "Flecha de Sílex", "item/generated"),
    "narcotic_arrow": ("Narcotic Arrow", "Flecha de Narcótico", "Flecha Narcótica", "item/generated"),
    "sleep_herb": ("Sleep Herb", "Erva Sonífera", "Hierba Somnífera", "item/generated"),
    # the Field Lens: the card of the dinosaur you look at, taming included (item/FieldLensItem)
    "field_lens": ("Field Lens", "Lupa de Campo", "Lupa de Campo", "item/handheld"),
}

LANG_EXTRA = {
    "en_us": {
        "itemGroup.terrassic.main": "Terrassic",
        "entity.terrassic.spear": "Spear",
        "entity.terrassic.carcass": "Carcass",
        "entity.terrassic.carcass.of": "%s carcass",
        "message.terrassic.sit": "%s is resting",
        "message.terrassic.follow": "%s is following you",
        "message.terrassic.perch": "%s is perched on your shoulder (sneak to shake it off)",
        "message.terrassic.perch_warn": "%s shrieks: something is after you!",
        "message.terrassic.perch_fish": "%s dove and brought you a fish",
        "message.terrassic.cargo_chest": "%s carries cargo now: sneak and use it with an empty hand, then Cargo",
        "message.terrassic.cargo_chest_ride": "%s carries cargo now: sneak + use with an empty hand, or the inventory key while riding, then Cargo",
        "message.terrassic.cargo_off": "%s dropped its cargo chest",
        "message.terrassic.platform": "%s wears the platform saddle: four aboard, anyone may climb on, you drive",
        "entity.terrassic.tranq_dart": "Narcotic Dart",
        "entity.terrassic.flint_arrow": "Flint Arrow",
        "entity.terrassic.narcotic_arrow": "Narcotic Arrow",
        "message.terrassic.knocked_out": "%s collapsed, unconscious! Feed it its food while it sleeps",
        "message.terrassic.ko_status": "%s · torpor %s/%s · taming %s%% · effectiveness %s%%",
        "message.terrassic.ko_tamed": "%s wakes up tame. Taming effectiveness: %s%%",
        "sex.terrassic.male": "male",
        "sex.terrassic.female": "female",
    },
    "pt_br": {
        "itemGroup.terrassic.main": "Terrassic",
        "entity.terrassic.spear": "Lança",
        "entity.terrassic.carcass": "Carcaça",
        "entity.terrassic.carcass.of": "Carcaça de %s",
        "message.terrassic.sit": "%s está descansando",
        "message.terrassic.follow": "%s está te seguindo",
        "message.terrassic.perch": "%s pousou no seu ombro (agache para soltar)",
        "message.terrassic.perch_warn": "%s grita: tem algo atrás de você!",
        "message.terrassic.perch_fish": "%s mergulhou e te trouxe um peixe",
        "message.terrassic.cargo_chest": "%s agora leva carga: agache e use com a mão vazia, depois Carga",
        "message.terrassic.cargo_chest_ride": "%s agora leva carga: agachar + usar com a mão vazia, ou a tecla do inventário montado, depois Carga",
        "message.terrassic.cargo_off": "%s largou o baú de carga",
        "message.terrassic.platform": "%s leva a sela de plataforma: quatro a bordo, qualquer um pode subir, você conduz",
        "entity.terrassic.tranq_dart": "Dardo de Narcótico",
        "entity.terrassic.flint_arrow": "Flecha de Sílex",
        "entity.terrassic.narcotic_arrow": "Flecha de Narcótico",
        "message.terrassic.knocked_out": "%s desabou, desacordado! Dê a comida dele enquanto dorme",
        "message.terrassic.ko_status": "%s · torpor %s/%s · domesticação %s%% · eficiência %s%%",
        "message.terrassic.ko_tamed": "%s acorda domesticado. Eficiência da domesticação: %s%%",
        "sex.terrassic.male": "macho",
        "sex.terrassic.female": "fêmea",
    },
    "es_es": {
        "itemGroup.terrassic.main": "Terrassic",
        "entity.terrassic.spear": "Lanza",
        "entity.terrassic.carcass": "Carcasa",
        "entity.terrassic.carcass.of": "Carcasa de %s",
        "message.terrassic.sit": "%s está descansando",
        "message.terrassic.follow": "%s te está siguiendo",
        "message.terrassic.perch": "%s se posó en tu hombro (agáchate para soltarlo)",
        "message.terrassic.perch_warn": "%s chilla: ¡algo te persigue!",
        "message.terrassic.perch_fish": "%s se zambulló y te trajo un pez",
        "message.terrassic.cargo_chest": "%s ahora lleva carga: agáchate y úsalo con la mano vacía, luego Carga",
        "message.terrassic.cargo_chest_ride": "%s ahora lleva carga: agacharse + usar con la mano vacía, o la tecla del inventario montado, luego Carga",
        "message.terrassic.cargo_off": "%s soltó el baúl de carga",
        "message.terrassic.platform": "%s lleva la silla de plataforma: cuatro a bordo, cualquiera puede subir, tú conduces",
        "entity.terrassic.tranq_dart": "Dardo Narcótico",
        "entity.terrassic.flint_arrow": "Flecha de Sílex",
        "entity.terrassic.narcotic_arrow": "Flecha Narcótica",
        "message.terrassic.knocked_out": "¡%s se desplomó, inconsciente! Dale su comida mientras duerme",
        "message.terrassic.ko_status": "%s · torpor %s/%s · domesticación %s%% · eficacia %s%%",
        "message.terrassic.ko_tamed": "%s despierta domesticado. Eficacia de la domesticación: %s%%",
        "sex.terrassic.male": "macho",
        "sex.terrassic.female": "hembra",
    },
}

# the Field Lens card and the species saddles (client/LensOverlay, DinosaurEntity.speciesSaddle)
LENS_LANG = {
    "en_us": {
        "item.terrassic.field_lens.tip": "Hold it and look at a dinosaur",
        "item.terrassic.field_lens.tip2": "Shows health, food, owner and how to tame it",
        "gui.terrassic.lens.young": "Young · grown %s%%",
        "gui.terrassic.lens.adult": "Adult · size %s%%",
        "gui.terrassic.lens.wild": "Wild",
        "gui.terrassic.lens.yours": "Tamed · yours",
        "gui.terrassic.lens.owner": "Tamed · %s",
        "gui.terrassic.lens.health": "Health",
        "gui.terrassic.lens.hunger": "Fed",
        "gui.terrassic.lens.torpor": "Torpor",
        "gui.terrassic.lens.taming": "Taming",
        "gui.terrassic.lens.effectiveness": "Effectiveness: %s%%",
        "gui.terrassic.lens.how_knockout": "Tame: knock it out, then feed it",
        "gui.terrassic.lens.how_feed": "Tame: feed it by hand (1 in %s per bite)",
        "gui.terrassic.lens.how_feed_or_ko": "Tame: feed it by hand (1 in %s) or knock it out",
        "message.terrassic.tame_try": "%s took the food, still wary (1 in %s)",
        "gui.terrassic.lens.how_feed_now": "Out cold: feed it now (use food on it)",
        "gui.terrassic.lens.eats": "Eats",
        "gui.terrassic.lens.cargo": "Bags: %s/%s slots",
        "message.terrassic.needs_own_saddle": "%s only takes a %s",
    },
    "pt_br": {
        "item.terrassic.field_lens.tip": "Segure e olhe para um dinossauro",
        "item.terrassic.field_lens.tip2": "Mostra vida, comida, dono e como domar",
        "gui.terrassic.lens.young": "Filhote · %s%% crescido",
        "gui.terrassic.lens.adult": "Adulto · tamanho %s%%",
        "gui.terrassic.lens.wild": "Selvagem",
        "gui.terrassic.lens.yours": "Domado · seu",
        "gui.terrassic.lens.owner": "Domado · %s",
        "gui.terrassic.lens.health": "Vida",
        "gui.terrassic.lens.hunger": "Saciedade",
        "gui.terrassic.lens.torpor": "Torpor",
        "gui.terrassic.lens.taming": "Doma",
        "gui.terrassic.lens.effectiveness": "Eficiência: %s%%",
        "gui.terrassic.lens.how_knockout": "Domar: nocauteie e depois alimente",
        "gui.terrassic.lens.how_feed": "Domar: dê comida na mão (1 em %s por porção)",
        "gui.terrassic.lens.how_feed_or_ko": "Domar: comida na mão (1 em %s) ou nocaute",
        "message.terrassic.tame_try": "%s comeu, mas ainda desconfia (1 em %s)",
        "gui.terrassic.lens.how_feed_now": "Desacordado: alimente agora (use a comida nele)",
        "gui.terrassic.lens.eats": "Come",
        "gui.terrassic.lens.cargo": "Bolsas: %s/%s espaços",
        "message.terrassic.needs_own_saddle": "%s só aceita a %s",
    },
    "es_es": {
        "item.terrassic.field_lens.tip": "Sostenla y mira a un dinosaurio",
        "item.terrassic.field_lens.tip2": "Muestra vida, comida, dueño y cómo domarlo",
        "gui.terrassic.lens.young": "Cría · %s%% crecida",
        "gui.terrassic.lens.adult": "Adulto · tamaño %s%%",
        "gui.terrassic.lens.wild": "Salvaje",
        "gui.terrassic.lens.yours": "Domado · tuyo",
        "gui.terrassic.lens.owner": "Domado · %s",
        "gui.terrassic.lens.health": "Vida",
        "gui.terrassic.lens.hunger": "Saciedad",
        "gui.terrassic.lens.torpor": "Sopor",
        "gui.terrassic.lens.taming": "Doma",
        "gui.terrassic.lens.effectiveness": "Eficacia: %s%%",
        "gui.terrassic.lens.how_knockout": "Domar: noquéalo y luego aliméntalo",
        "gui.terrassic.lens.how_feed": "Domar: dale comida en la mano (1 de %s por bocado)",
        "gui.terrassic.lens.how_feed_or_ko": "Domar: comida en la mano (1 de %s) o noqueo",
        "message.terrassic.tame_try": "%s comió, pero aún desconfía (1 de %s)",
        "gui.terrassic.lens.how_feed_now": "Inconsciente: aliméntalo ahora (usa la comida en él)",
        "gui.terrassic.lens.eats": "Come",
        "gui.terrassic.lens.cargo": "Alforjas: %s/%s huecos",
        "message.terrassic.needs_own_saddle": "%s solo acepta la %s",
    },
}
for _lang, _keys in LENS_LANG.items():
    LANG_EXTRA[_lang].update(_keys)

# v0.12: the dino screen and the keys (client/DinoScreen, client/DinoControls); v0.13: levels (entity/DinoLevels)
DINO_LANG = {
    "en_us": {
        "entity.terrassic.leveled": "%s · Lv %s",
        "gui.terrassic.dino.level": "Level %s",
        "gui.terrassic.dino.xp": "Next: %s/%s XP",
        "gui.terrassic.dino.max_level": "Highest level",
        "gui.terrassic.dino.points": "Points: %s",
        "gui.terrassic.dino.spend": "Spend a point on %s",
        "gui.terrassic.stat.health": "Health",
        "gui.terrassic.stat.health.tip": "Maximum health.",
        "gui.terrassic.stat.attack": "Attack",
        "gui.terrassic.stat.attack.tip": "Damage of the bite, horn or stomp.",
        "gui.terrassic.stat.speed": "Speed",
        "gui.terrassic.stat.speed.tip": "Running and flying speed. Wild animals are all born with the same.",
        "gui.terrassic.stat.food": "Food",
        "gui.terrassic.stat.food.tip": "Stomach size: it takes longer to get hungry.",
        "gui.terrassic.stat.torpor": "Torpor",
        "gui.terrassic.stat.torpor.tip": "Resistance to being knocked out. Only matters while wild.",
        "gui.terrassic.lens.effectiveness_levels": "Effectiveness: %s%% (+%s levels)",
        "gui.terrassic.lens.points": "Points to spend: %s",
        "key.categories.terrassic": "Terrassic",
        "key.terrassic.dino_screen": "Dino screen",
        "key.terrassic.descend": "Dive (flying mount)",
        "gui.terrassic.dino.title": "Your dinosaur",
        "gui.terrassic.dino.follow": "Follow",
        "gui.terrassic.dino.wait": "Wait",
        "gui.terrassic.dino.cargo": "Cargo",
        "gui.terrassic.dino.perch": "Shoulder",
        "gui.terrassic.dino.backpack": "Inventory",
        "gui.terrassic.dino.state_following": "Following you",
        "gui.terrassic.dino.state_waiting": "Waiting here",
        "gui.terrassic.dino.state_ridden": "Ridden by you",
        "gui.terrassic.dino.saddled": "Saddled",
        "gui.terrassic.dino.no_saddle": "No saddle",
        "gui.terrassic.dino.hint_ridden": "Left click: its attack · Sneak: get off",
        "gui.terrassic.dino.hint_apex": "Left click: bite · Right click, empty hand: roar · Sneak: get off",
        "gui.terrassic.dino.hint_flyer": "Left click: its attack · %s or sneak in the air: dive · Sneak on the ground: get off",
        # v0.16: orders (docs/ORDENS.md)
        "gui.terrassic.dino.wander": "Wander",
        "gui.terrassic.dino.wander.tip": "Roams within %s blocks of here instead of following you",
        "gui.terrassic.dino.stop": "Stop",
        "gui.terrassic.dino.stop.tip": "Drops its target and stays out of fights for %s seconds, even if hit",
        "gui.terrassic.dino.stance": "Mode: %s",
        "gui.terrassic.dino.stance.click": "Click for the next mode",
        "gui.terrassic.dino.stance.passive": "Passive",
        "gui.terrassic.dino.stance.neutral": "Neutral",
        "gui.terrassic.dino.stance.aggressive": "Aggressive",
        "gui.terrassic.dino.stance.passive.tip": "Never attacks, not even to defend itself or you",
        "gui.terrassic.dino.stance.neutral.tip": "Defends itself and you, and joins your fights, except against players and tamed animals",
        "gui.terrassic.dino.stance.aggressive.tip": "Joins all your fights and goes for monsters and wild dinosaurs within 12 blocks (not creepers)",
        "gui.terrassic.dino.state_wandering": "Roaming around here",
        "message.terrassic.wander": "%s is roaming around here",
        "message.terrassic.stop": "%s stopped fighting",
        "message.terrassic.stance": "%s: %s mode",
    },
    "pt_br": {
        "entity.terrassic.leveled": "%s · Nv %s",
        "gui.terrassic.dino.level": "Nível %s",
        "gui.terrassic.dino.xp": "Próximo: %s/%s XP",
        "gui.terrassic.dino.max_level": "Nível máximo",
        "gui.terrassic.dino.points": "Pontos: %s",
        "gui.terrassic.dino.spend": "Colocar um ponto em %s",
        "gui.terrassic.stat.health": "Vida",
        "gui.terrassic.stat.health.tip": "Vida máxima.",
        "gui.terrassic.stat.attack": "Ataque",
        "gui.terrassic.stat.attack.tip": "Dano da mordida, da chifrada ou do pisão.",
        "gui.terrassic.stat.speed": "Velocidade",
        "gui.terrassic.stat.speed.tip": "Velocidade correndo e voando. Os selvagens nascem todos com a mesma.",
        "gui.terrassic.stat.food": "Fome",
        "gui.terrassic.stat.food.tip": "Tamanho do estômago: demora mais a sentir fome.",
        "gui.terrassic.stat.torpor": "Torpor",
        "gui.terrassic.stat.torpor.tip": "Resistência ao nocaute. Só conta enquanto é selvagem.",
        "gui.terrassic.lens.effectiveness_levels": "Eficiência: %s%% (+%s níveis)",
        "gui.terrassic.lens.points": "Pontos para distribuir: %s",
        "key.categories.terrassic": "Terrassic",
        "key.terrassic.dino_screen": "Tela do dino",
        "key.terrassic.descend": "Mergulhar (montaria voadora)",
        "gui.terrassic.dino.title": "Seu dinossauro",
        "gui.terrassic.dino.follow": "Seguir",
        "gui.terrassic.dino.wait": "Esperar",
        "gui.terrassic.dino.cargo": "Carga",
        "gui.terrassic.dino.perch": "Ombro",
        "gui.terrassic.dino.backpack": "Inventário",
        "gui.terrassic.dino.state_following": "Seguindo você",
        "gui.terrassic.dino.state_waiting": "Esperando aqui",
        "gui.terrassic.dino.state_ridden": "Montado por você",
        "gui.terrassic.dino.saddled": "Selado",
        "gui.terrassic.dino.no_saddle": "Sem sela",
        "gui.terrassic.dino.hint_ridden": "Clique esquerdo: ataque · Agachar: descer",
        "gui.terrassic.dino.hint_apex": "Clique esquerdo: mordida · Clique direito, mão vazia: rugido · Agachar: descer",
        "gui.terrassic.dino.hint_flyer": "Clique esquerdo: ataque · %s ou Agachar no ar: descer voando · Agachar no chão: desmontar",
        # v0.16: orders (docs/ORDENS.md)
        "gui.terrassic.dino.wander": "Vagar",
        "gui.terrassic.dino.wander.tip": "Anda a até %s blocos daqui em vez de te seguir",
        "gui.terrassic.dino.stop": "Pare",
        "gui.terrassic.dino.stop.tip": "Larga o alvo e fica %s segundos fora de briga, mesmo se apanhar",
        "gui.terrassic.dino.stance": "Modo: %s",
        "gui.terrassic.dino.stance.click": "Clique para o próximo modo",
        "gui.terrassic.dino.stance.passive": "Passivo",
        "gui.terrassic.dino.stance.neutral": "Neutro",
        "gui.terrassic.dino.stance.aggressive": "Agressivo",
        "gui.terrassic.dino.stance.passive.tip": "Nunca ataca, nem para se defender ou defender você",
        "gui.terrassic.dino.stance.neutral.tip": "Defende a si e a você e entra nas suas brigas, menos contra jogadores e bichos domados",
        "gui.terrassic.dino.stance.aggressive.tip": "Entra em todas as suas brigas e vai atrás de monstros e dinos selvagens a até 12 blocos (creeper não)",
        "gui.terrassic.dino.state_wandering": "Vagando por aqui",
        "message.terrassic.wander": "%s está vagando por aqui",
        "message.terrassic.stop": "%s parou de brigar",
        "message.terrassic.stance": "%s: modo %s",
    },
    "es_es": {
        "entity.terrassic.leveled": "%s · Nv %s",
        "gui.terrassic.dino.level": "Nivel %s",
        "gui.terrassic.dino.xp": "Siguiente: %s/%s XP",
        "gui.terrassic.dino.max_level": "Nivel máximo",
        "gui.terrassic.dino.points": "Puntos: %s",
        "gui.terrassic.dino.spend": "Poner un punto en %s",
        "gui.terrassic.stat.health": "Vida",
        "gui.terrassic.stat.health.tip": "Vida máxima.",
        "gui.terrassic.stat.attack": "Ataque",
        "gui.terrassic.stat.attack.tip": "Daño del mordisco, la cornada o el pisotón.",
        "gui.terrassic.stat.speed": "Velocidad",
        "gui.terrassic.stat.speed.tip": "Velocidad corriendo y volando. Los salvajes nacen todos con la misma.",
        "gui.terrassic.stat.food": "Hambre",
        "gui.terrassic.stat.food.tip": "Tamaño del estómago: tarda más en tener hambre.",
        "gui.terrassic.stat.torpor": "Torpor",
        "gui.terrassic.stat.torpor.tip": "Resistencia al noqueo. Solo cuenta mientras es salvaje.",
        "gui.terrassic.lens.effectiveness_levels": "Eficacia: %s%% (+%s niveles)",
        "gui.terrassic.lens.points": "Puntos por repartir: %s",
        "key.categories.terrassic": "Terrassic",
        "key.terrassic.dino_screen": "Pantalla del dino",
        "key.terrassic.descend": "Picar (montura voladora)",
        "gui.terrassic.dino.title": "Tu dinosaurio",
        "gui.terrassic.dino.follow": "Seguir",
        "gui.terrassic.dino.wait": "Esperar",
        "gui.terrassic.dino.cargo": "Carga",
        "gui.terrassic.dino.perch": "Hombro",
        "gui.terrassic.dino.backpack": "Inventario",
        "gui.terrassic.dino.state_following": "Siguiéndote",
        "gui.terrassic.dino.state_waiting": "Esperando aquí",
        "gui.terrassic.dino.state_ridden": "Montado por ti",
        "gui.terrassic.dino.saddled": "Ensillado",
        "gui.terrassic.dino.no_saddle": "Sin silla",
        "gui.terrassic.dino.hint_ridden": "Clic izquierdo: ataque · Agacharse: bajar",
        "gui.terrassic.dino.hint_apex": "Clic izquierdo: mordisco · Clic derecho, mano vacía: rugido · Agacharse: bajar",
        "gui.terrassic.dino.hint_flyer": "Clic izquierdo: ataque · %s o agacharse en el aire: picar · Agacharse en el suelo: bajarse",
        # v0.16: orders (docs/ORDENS.md)
        "gui.terrassic.dino.wander": "Pasear",
        "gui.terrassic.dino.wander.tip": "Anda a menos de %s bloques de aquí en vez de seguirte",
        "gui.terrassic.dino.stop": "Alto",
        "gui.terrassic.dino.stop.tip": "Suelta su objetivo y no pelea durante %s segundos, aunque le peguen",
        "gui.terrassic.dino.stance": "Modo: %s",
        "gui.terrassic.dino.stance.click": "Clic para el siguiente modo",
        "gui.terrassic.dino.stance.passive": "Pasivo",
        "gui.terrassic.dino.stance.neutral": "Neutral",
        "gui.terrassic.dino.stance.aggressive": "Agresivo",
        "gui.terrassic.dino.stance.passive.tip": "Nunca ataca, ni para defenderse ni para defenderte",
        "gui.terrassic.dino.stance.neutral.tip": "Se defiende y te defiende, y entra en tus peleas, salvo contra jugadores y animales domados",
        "gui.terrassic.dino.stance.aggressive.tip": "Entra en todas tus peleas y va a por monstruos y dinosaurios salvajes a menos de 12 bloques (creepers no)",
        "gui.terrassic.dino.state_wandering": "Paseando por aquí",
        "message.terrassic.wander": "%s pasea por aquí",
        "message.terrassic.stop": "%s dejó de pelear",
        "message.terrassic.stance": "%s: modo %s",
    },
}
for _lang, _keys in DINO_LANG.items():
    LANG_EXTRA[_lang].update(_keys)

# v0.14: the "Âmbar" HUD (docs/HUD.md): the mount plate, the notices on the right, the special in the compact style
HUD_LANG = {
    "en_us": {
        "hud.terrassic.level": "Lv %s",
        "hud.terrassic.notice.level_up": "Level up",
        "hud.terrassic.notice.tamed": "Tamed",
        "hud.terrassic.notice.hatched": "A baby hatched",
        "hud.terrassic.notice.name_sex": "%s · %s",
        "hud.terrassic.notice.hungry": "Hungry",
        "hud.terrassic.notice.hungry_far": "Hungry, far from you",
        "hud.terrassic.notice.woke": "Woke up angry",
        "hud.terrassic.notice.died": "%s died",
        "hud.terrassic.notice.where": "X %s  Y %s  Z %s",
        "hud.terrassic.special.loud_roar": "Loud roar",
        "hud.terrassic.special.ready": "%s ready",
        "hud.terrassic.special.wait": "%s in %s s",
        "hud.terrassic.knocked_out": "Knocked out",
        "gui.terrassic.dino.mount_keys": "Mount keys",
        "gui.terrassic.hud.button": "HUD",
        "gui.terrassic.hud.title": "Terrassic HUD",
        "gui.terrassic.hud.style": "Style",
        "gui.terrassic.hud.amber": "Amber",
        "gui.terrassic.hud.compact": "Compact",
        "gui.terrassic.hud.hud_mount": "Mount plate",
        "gui.terrassic.hud.hud_nameplate": "Nameplate over the animal",
        "gui.terrassic.hud.hud_taming": "Taming bars",
        "gui.terrassic.hud.hud_notices": "Notices on the right",
        "gui.terrassic.hud.hud_new_species": "New species",
        "gui.terrassic.hud.hud_era_title": "Era title",
        "gui.terrassic.hud.hud_numbers_always": "Numbers on the bars, always",
        "gui.terrassic.hud.scale": "Size: %s",
        "gui.terrassic.hud.scale_auto": "auto",
    },
    "pt_br": {
        "hud.terrassic.level": "Nv %s",
        "hud.terrassic.notice.level_up": "Subiu de nível",
        "hud.terrassic.notice.tamed": "Domesticado",
        "hud.terrassic.notice.hatched": "Nasceu um filhote",
        "hud.terrassic.notice.name_sex": "%s · %s",
        "hud.terrassic.notice.hungry": "Com fome",
        "hud.terrassic.notice.hungry_far": "Com fome, longe de você",
        "hud.terrassic.notice.woke": "Acordou bravo",
        "hud.terrassic.notice.died": "%s morreu",
        "hud.terrassic.notice.where": "X %s  Y %s  Z %s",
        "hud.terrassic.special.loud_roar": "Rugido forte",
        "hud.terrassic.special.ready": "%s pronto",
        "hud.terrassic.special.wait": "%s em %s s",
        "hud.terrassic.knocked_out": "Desmaiado",
        "gui.terrassic.dino.mount_keys": "Teclas da montaria",
        "gui.terrassic.hud.button": "HUD",
        "gui.terrassic.hud.title": "HUD do Terrassic",
        "gui.terrassic.hud.style": "Estilo",
        "gui.terrassic.hud.amber": "Âmbar",
        "gui.terrassic.hud.compact": "Compacto",
        "gui.terrassic.hud.hud_mount": "Placa da montaria",
        "gui.terrassic.hud.hud_nameplate": "Placa de nome sobre o animal",
        "gui.terrassic.hud.hud_taming": "Barras de doma",
        "gui.terrassic.hud.hud_notices": "Avisos à direita",
        "gui.terrassic.hud.hud_new_species": "Espécie nova",
        "gui.terrassic.hud.hud_era_title": "Título da era",
        "gui.terrassic.hud.hud_numbers_always": "Números nas barras sempre",
        "gui.terrassic.hud.scale": "Tamanho: %s",
        "gui.terrassic.hud.scale_auto": "automático",
    },
    "es_es": {
        "hud.terrassic.level": "Nv %s",
        "hud.terrassic.notice.level_up": "Subió de nivel",
        "hud.terrassic.notice.tamed": "Domesticado",
        "hud.terrassic.notice.hatched": "Nació una cría",
        "hud.terrassic.notice.name_sex": "%s · %s",
        "hud.terrassic.notice.hungry": "Con hambre",
        "hud.terrassic.notice.hungry_far": "Con hambre, lejos de ti",
        "hud.terrassic.notice.woke": "Despertó furioso",
        "hud.terrassic.notice.died": "%s murió",
        "hud.terrassic.notice.where": "X %s  Y %s  Z %s",
        "hud.terrassic.special.loud_roar": "Rugido fuerte",
        "hud.terrassic.special.ready": "%s listo",
        "hud.terrassic.special.wait": "%s en %s s",
        "hud.terrassic.knocked_out": "Inconsciente",
        "gui.terrassic.dino.mount_keys": "Teclas de la montura",
        "gui.terrassic.hud.button": "HUD",
        "gui.terrassic.hud.title": "HUD de Terrassic",
        "gui.terrassic.hud.style": "Estilo",
        "gui.terrassic.hud.amber": "Ámbar",
        "gui.terrassic.hud.compact": "Compacto",
        "gui.terrassic.hud.hud_mount": "Placa de la montura",
        "gui.terrassic.hud.hud_nameplate": "Placa de nombre sobre el animal",
        "gui.terrassic.hud.hud_taming": "Barras de doma",
        "gui.terrassic.hud.hud_notices": "Avisos a la derecha",
        "gui.terrassic.hud.hud_new_species": "Especie nueva",
        "gui.terrassic.hud.hud_era_title": "Título de la era",
        "gui.terrassic.hud.hud_numbers_always": "Números en las barras siempre",
        "gui.terrassic.hud.scale": "Tamaño: %s",
        "gui.terrassic.hud.scale_auto": "automático",
    },
}
for _lang, _keys in HUD_LANG.items():
    LANG_EXTRA[_lang].update(_keys)

# Minecraft treats every Spanish locale as its own language and falls back to English when one is missing,
# so the es_es file is copied to the other Spanish variants.
SPANISH_VARIANTS = ("es_ar", "es_cl", "es_ec", "es_mx", "es_uy", "es_ve")


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


# Weapons whose held model changes while in use (client/WeaponPoses registers the predicates; docs/ARMAS.md).
ITEM_OVERRIDES = {
    "blowgun": [{"predicate": {"terrassic:blowing": 1}, "model": "terrassic:item/blowgun_blowing"}],
    "flint_spear": [{"predicate": {"terrassic:held": 1}, "model": "terrassic:item/flint_spear_held"}],
    "horn_spear": [{"predicate": {"terrassic:held": 1}, "model": "terrassic:item/horn_spear_held"}],
    "hunting_bow": [{"predicate": {"pulling": 1}, "model": "terrassic:item/hunting_bow_pulling_0"},
                    {"predicate": {"pulling": 1, "pull": 0.65}, "model": "terrassic:item/hunting_bow_pulling_1"},
                    {"predicate": {"pulling": 1, "pull": 0.9}, "model": "terrassic:item/hunting_bow_pulling_2"}],
}


def _box(frm, to, faces):
    return {"from": frm, "to": to, "faces": faces}


# vanilla item/handheld + item/generated display, copied because a model with its own elements cannot have
# builtin/generated as root (the game would rebuild it from the sprite)
_HANDHELD = {
    "thirdperson_righthand": {"rotation": [0, -90, 55], "translation": [0, 4.0, 0.5], "scale": [0.85, 0.85, 0.85]},
    "thirdperson_lefthand": {"rotation": [0, 90, -55], "translation": [0, 4.0, 0.5], "scale": [0.85, 0.85, 0.85]},
    "firstperson_righthand": {"rotation": [0, -90, 25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
    "firstperson_lefthand": {"rotation": [0, 90, -25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
    "ground": {"rotation": [0, 0, 0], "translation": [0, 2, 0], "scale": [0.5, 0.5, 0.5]},
    "head": {"rotation": [0, 180, 0], "translation": [0, 13, 7], "scale": [1, 1, 1]},
    "fixed": {"rotation": [0, 180, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]},
}


def _spear_held(spear):
    """The 3D spear: a 32 px shaft, 1.5 px thick, laid on the sprite's diagonal (so the handheld pose holds it the same way), flint or
    horn head, sinew binding, leather grip. Texture from tools/spritegen/armas.py."""
    rot = {"origin": [8, 8, 8], "axis": "z", "angle": -45}

    def part(frm, to, side, end):
        faces = {f: {"uv": side, "texture": "#t"} for f in ("north", "south", "east", "west")}
        faces.update({f: {"uv": end, "texture": "#t"} for f in ("up", "down")})
        return {"from": frm, "to": to, "rotation": rot, "faces": faces}
    return {
        "textures": {"t": f"terrassic:item/{spear}_held", "particle": f"terrassic:item/{spear}"},
        "elements": [
            part([7.25, -8, 7.25], [8.75, 24, 8.75], [0, 0, 1, 16], [0, 0, 1, 1]),       # shaft
            part([6.5, 24, 7.5], [9.5, 29, 8.5], [2, 0, 5, 5], [2, 0, 5, 1]),            # head
            part([7.5, 29, 7.5], [8.5, 31, 8.5], [6, 0, 7, 2], [6, 0, 7, 1]),            # tip
            part([7, 22, 7], [9, 24.5, 9], [8, 0, 10, 3], [8, 0, 10, 2]),                # sinew binding
            part([7, 2, 7], [9, 8, 9], [11, 0, 13, 6], [11, 0, 13, 2]),                  # leather grip
        ],
        "display": _HANDHELD,
    }


_TUBE_SIDE = {"uv": [0, 0, 16, 2], "texture": "#t"}
_WRAP = {"uv": [0, 8, 3, 11], "texture": "#t"}
HELD_MODELS = {
    "flint_spear_held": _spear_held("flint_spear"),
    "horn_spear_held": _spear_held("horn_spear"),
    # the hunting bow's draw frames keep the bow's held pose (their parent inherits minecraft:item/bow's display)
    **{f"hunting_bow_pulling_{i}": {"parent": "terrassic:item/hunting_bow",
                                    "textures": {"layer0": f"terrassic:item/hunting_bow_pulling_{i}"}} for i in range(3)},
    # the reed at the lips: a 24 px tube along -Z with the leather mouthpiece at the near end, pointing at the
    # crosshair in first person and straight ahead of the face in the goat-horn pose
    "blowgun_blowing": {
        "textures": {"t": "terrassic:item/blowgun_tube", "particle": "terrassic:item/blowgun"},
        "elements": [
            _box([7, 7, -4], [9, 9, 20], {
                "north": {"uv": [0, 4, 2, 6], "texture": "#t"}, "south": {"uv": [0, 4, 2, 6], "texture": "#t"},
                "east": _TUBE_SIDE, "west": _TUBE_SIDE,
                "up": dict(_TUBE_SIDE, rotation=90), "down": {"uv": [0, 2, 16, 4], "texture": "#t", "rotation": 90}}),
            _box([6.5, 6.5, 16], [9.5, 9.5, 19.5], {f: _WRAP for f in ("north", "south", "east", "west", "up", "down")}),
        ],
        "display": {
            "firstperson_righthand": {"rotation": [8, 0, 0], "translation": [0, -3, -2], "scale": [1, 1, 1]},
            "firstperson_lefthand": {"rotation": [8, 0, 0], "translation": [0, -3, -2], "scale": [1, 1, 1]},
            "thirdperson_righthand": {"rotation": [0, 0, 0], "translation": [0, 0, -10], "scale": [0.8, 0.8, 0.8]},
            "thirdperson_lefthand": {"rotation": [0, 0, 0], "translation": [0, 0, -10], "scale": [0.8, 0.8, 0.8]},
            "gui": {"rotation": [90, -45, 0], "translation": [0, 0, 0], "scale": [0.8, 0.8, 0.8]},
            "fixed": {"rotation": [90, -45, 0], "translation": [0, 0, 0], "scale": [0.8, 0.8, 0.8]},
            "ground": {"rotation": [0, 0, 0], "translation": [0, 2, 0], "scale": [0.4, 0.4, 0.4]},
        },
    },
}


def egg_model(sid, stage, large):
    if sid in CUSTOM_EGGS:
        return CUSTOM_EGGS[sid](sid, stage)
    tex = f"terrassic:block/{sid}_egg_{stage}"
    if large:
        els = [([4, 0, 4], [12, 9, 12]), ([5, 9, 5], [11, 12, 11]), ([6, 12, 6], [10, 13, 10])]
    else:
        els = [([5, 0, 5], [11, 6, 11]), ([6, 6, 6], [10, 8, 10]), ([7, 8, 7], [9, 9, 9])]
    elements = []
    for frm, to in els:
        faces = {f: {"texture": "#egg"} for f in ("north", "south", "east", "west", "up", "down")}
        faces["down"]["cullface"] = "down" if frm[1] == 0 else None
        if faces["down"]["cullface"] is None:
            del faces["down"]["cullface"]
        elements.append({"from": frm, "to": to, "faces": faces})
    return {"parent": "block/block", "textures": {"egg": tex, "particle": tex}, "elements": elements,
            "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, 2 if not large else 0, 0], "scale": [0.8 if large else 1.1] * 3}}}


def main():
    lang = {code: dict(entries) for code, entries in LANG_EXTRA.items()}
    # sound subtitles (tools/soundgen/recipes.py)
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "soundgen"))
    from recipes import SUBTITLES, sound_id
    for (vset, ev), (pt, en, es) in SUBTITLES.items():
        key = f"subtitles.terrassic.{sound_id(vset, ev)}"
        lang["pt_br"][key], lang["en_us"][key], lang["es_es"][key] = pt, en, es
    for sid, (en, pt, es, large) in SPECIES.items():
        lang["en_us"][f"entity.terrassic.{sid}"] = en
        lang["pt_br"][f"entity.terrassic.{sid}"] = pt
        lang["es_es"][f"entity.terrassic.{sid}"] = es
        lang["en_us"][f"item.terrassic.{sid}_spawn_egg"] = f"{en} Spawn Egg"
        lang["pt_br"][f"item.terrassic.{sid}_spawn_egg"] = f"Ovo Gerador de {pt}"
        lang["es_es"][f"item.terrassic.{sid}_spawn_egg"] = f"Huevo Generador de {es}"
        # unique spawn egg sprite (layer0 only; tint colours are white)
        write(f"{A}/models/item/{sid}_spawn_egg.json", {"parent": "item/generated", "textures": {"layer0": f"terrassic:item/{sid}_spawn_egg"}})
        # hide of the species (item terrassic:<sid>_hide; sprite from tools/spritegen/sprites.py, drawn from the model palette)
        lang["en_us"][f"item.terrassic.{sid}_hide"] = f"{en} Hide"
        lang["pt_br"][f"item.terrassic.{sid}_hide"] = f"Couro de {pt}"
        lang["es_es"][f"item.terrassic.{sid}_hide"] = f"Cuero de {es}"
        write(f"{A}/models/item/{sid}_hide.json", {"parent": "item/generated", "textures": {"layer0": f"terrassic:item/{sid}_hide"}})
        if large is None:
            continue
        lang["en_us"][f"block.terrassic.{sid}_egg"] = f"{en} Egg"
        lang["pt_br"][f"block.terrassic.{sid}_egg"] = f"Ovo de {pt}"
        lang["es_es"][f"block.terrassic.{sid}_egg"] = f"Huevo de {es}"
        # egg block: 3 hatch stages
        for st in range(3):
            write(f"{A}/models/block/{sid}_egg_{st}.json", egg_model(sid, st, large))
        write(f"{A}/blockstates/{sid}_egg.json", {"variants": {f"hatch={st}": {"model": f"terrassic:block/{sid}_egg_{st}"} for st in range(3)}})
        write(f"{A}/models/item/{sid}_egg.json", {"parent": f"terrassic:block/{sid}_egg_0"})
        write(f"{D}/loot_tables/blocks/{sid}_egg.json", {"type": "minecraft:block", "pools": [{
            "rolls": 1, "entries": [{"type": "minecraft:item", "name": f"terrassic:{sid}_egg"}],
            "conditions": [{"condition": "minecraft:block_state_property", "block": f"terrassic:{sid}_egg",
                            "properties": {"hatch": "0"}}, {"condition": "minecraft:survives_explosion"}]}]})
    for iid, (en, pt, es, parent) in ITEMS.items():
        lang["en_us"][f"item.terrassic.{iid}"] = en
        lang["pt_br"][f"item.terrassic.{iid}"] = pt
        lang["es_es"][f"item.terrassic.{iid}"] = es
        model = {"parent": parent, "textures": {"layer0": f"terrassic:item/{iid}"}}
        if iid in ITEM_OVERRIDES:
            model["overrides"] = ITEM_OVERRIDES[iid]
        write(f"{A}/models/item/{iid}.json", model)
    for name, model in HELD_MODELS.items():
        write(f"{A}/models/item/{name}.json", model)
    import gen_blocks  # primitive building blocks: their JSON + lang entries
    gen_blocks.main()
    import gen_science  # fossils, field tools, research table, advancements, story and Field Guide texts
    gen_science.main()
    import gen_world  # v0.8: Cretaceous biomes, "Terrassic" world types, biome tags
    gen_world.main()
    sys.path.insert(0, os.path.join(ROOT, "tools", "texpack"))
    from pack_lang import LANG as TEXPACK_LANG  # built-in era resource packs: their names and descriptions
    import gen_rules  # world rules (docs/REGRAS.md): Rule.java + the Rules screen texts
    gen_rules.main()
    import gen_leap  # v0.9 (docs/SALTO.md): Leap Altar, ring tags, Rift Tyrant, ritual and leap texts
    gen_leap.main()
    for code in lang:
        lang[code].update(gen_blocks.LANG[code])
        lang[code].update(gen_science.LANG[code])
        lang[code].update(gen_world.LANG[code])
        lang[code].update(TEXPACK_LANG[code])
        lang[code].update(gen_rules.LANG[code])
        lang[code].update(gen_leap.LANG[code])
    missing = set(lang["en_us"]) ^ set(lang["pt_br"]) | set(lang["en_us"]) ^ set(lang["es_es"])
    if missing:
        raise SystemExit(f"lang keys missing in some language: {sorted(missing)}")
    lang.update({code: lang["es_es"] for code in SPANISH_VARIANTS})
    for code, data in lang.items():
        write(f"{A}/lang/{code}.json", dict(sorted(data.items())))

    # ------------------------------------------------------------- recipes
    def shaped(name, pattern, key, result, count=1):
        write(f"{D}/recipes/{name}.json", {"type": "minecraft:crafting_shaped", "category": "equipment", "pattern": pattern,
                                         "key": {k: {"item": v} for k, v in key.items()},
                                         "result": {"item": result, "count": count}})
    shaped("flint_knife", ["F", "S"], {"F": "minecraft:flint", "S": "minecraft:stick"}, "terrassic:flint_knife")
    shaped("flint_hatchet", ["FF", "FS", " S"], {"F": "minecraft:flint", "S": "minecraft:stick"}, "terrassic:flint_hatchet")
    shaped("bone_club", [" X", "B "], {"X": "minecraft:bone_block", "B": "minecraft:bone"}, "terrassic:bone_club")
    shaped("flint_spear", ["  F", " T ", "S  "], {"F": "minecraft:flint", "T": "minecraft:string", "S": "minecraft:stick"}, "terrassic:flint_spear")
    shaped("horn_spear", ["  H", " T ", "S  "], {"H": "terrassic:triceratops_horn", "T": "minecraft:string", "S": "minecraft:stick"}, "terrassic:horn_spear")
    shaped("rex_tooth_dagger", ["T", "L"], {"T": "terrassic:rex_tooth", "L": "minecraft:leather"}, "terrassic:rex_tooth_dagger")
    shaped("tail_club", [" C", "S "], {"C": "terrassic:ankylosaurus_club", "S": "minecraft:stick"}, "terrassic:tail_club")
    # knockout taming (docs/DOMESTICACAO.md): a reed tube, darts tipped with flint and the sleep herb, which is
    # brewed from the Cretaceous water lily (sedative, like its living relatives) and shelf fungus
    shaped("blowgun", ["  R", " R ", "R  "], {"R": "terrassic:rush"}, "terrassic:blowgun")
    shaped("tranq_dart", ["F", "H", "E"], {"F": "minecraft:flint", "H": "terrassic:sleep_herb", "E": "minecraft:feather"}, "terrassic:tranq_dart", 4)
    # the hunting bow (docs/ARMAS.md): a stick stave backed with bone at the grip, a rush-fibre string; flint arrows
    # fletched with rush; narcotic arrows dipped eight at a time in the sleep herb, like tipped arrows
    shaped("hunting_bow", [" SR", "B R", " SR"], {"S": "minecraft:stick", "B": "minecraft:bone", "R": "terrassic:rush"}, "terrassic:hunting_bow")
    shaped("flint_arrow", ["F", "S", "R"], {"F": "minecraft:flint", "S": "minecraft:stick", "R": "terrassic:rush"}, "terrassic:flint_arrow", 4)
    shaped("narcotic_arrow", ["AAA", "AHA", "AAA"], {"A": "terrassic:flint_arrow", "H": "terrassic:sleep_herb"}, "terrassic:narcotic_arrow", 8)
    # any bow (and the crossbow) takes the mod's arrows
    write(os.path.join(RES, "data", "minecraft", "tags", "items", "arrows.json"),
          {"replace": False, "values": ["terrassic:flint_arrow", "terrassic:narcotic_arrow"]})
    # the T. rex saddle: leather seat and flaps, rush padding, iron rings, and a rex tooth for the pommel
    shaped("tyrannosaurus_saddle", ["LLL", "RTR", "I I"], {"L": "minecraft:leather", "R": "terrassic:rush",
           "T": "terrassic:rex_tooth", "I": "minecraft:iron_ingot"}, "terrassic:tyrannosaurus_saddle")
    # the Pteranodon saddle: a light leather pad on a string harness, a feather for the grab bar's crest
    shaped("pteranodon_saddle", ["LLL", "SFS"], {"L": "minecraft:leather", "S": "minecraft:string", "F": "minecraft:feather"},
           "terrassic:pteranodon_saddle")
    # the Velociraptor's hunting harness: leather flanks, a bone plate, string straps and an iron ring
    shaped("velociraptor_harness", ["LBL", "SNS"], {"L": "minecraft:leather", "B": "minecraft:bone", "S": "minecraft:string",
                                                     "N": "minecraft:iron_nugget"}, "terrassic:velociraptor_harness")
    # the Field Lens: an amber lens in a bone rim on a stick (item/FieldLensItem)
    shaped("field_lens", [" G ", "BAB", " S "], {"G": "minecraft:glass_pane", "A": "terrassic:raw_amber", "B": "minecraft:bone",
                                                  "S": "minecraft:stick"}, "terrassic:field_lens")
    shaped("sleep_herb", ["WF"], {"W": "terrassic:cretaceous_water_lily", "F": "terrassic:shelf_fungus"}, "terrassic:sleep_herb", 2)

    def cooked(raw, result):
        """Furnace, smoker and campfire, like vanilla meat (the loot's furnace_smelt function uses the smelting one)."""
        base = {"category": "food", "ingredient": {"item": f"terrassic:{raw}"}, "result": f"terrassic:{result}", "experience": 0.35}
        write(f"{D}/recipes/{result}.json", dict(base, type="minecraft:smelting", cookingtime=200))
        write(f"{D}/recipes/{result}_from_smoking.json", dict(base, type="minecraft:smoking", cookingtime=100))
        write(f"{D}/recipes/{result}_from_campfire_cooking.json", dict(base, type="minecraft:campfire_cooking", cookingtime=600))
    cooked("raw_dino_meat", "cooked_dino_meat")
    cooked("raw_prime_meat", "cooked_prime_meat")
    cooked("enchodus", "cooked_enchodus")
    cooked("lepisosteus", "cooked_lepisosteus")

    # ------------------------------------------------------------- entity loot
    # Cretaceous food (docs/FAUNA.md): there are no cattle, sheep or chickens in the Terrassic world, so every animal
    # drops its own meat (raw_dino_meat; cooks like beef). The big ones also drop prime cuts (raw_prime_meat).
    MEAT = {"minecraft:beef": "terrassic:raw_dino_meat", "minecraft:mutton": "terrassic:raw_dino_meat",
            "minecraft:chicken": "terrassic:raw_dino_meat", "minecraft:porkchop": "terrassic:raw_dino_meat"}
    SEA_MEAT = {"mosasaurus", "tylosaurus", "elasmosaurus", "deinosuchus"}  # their "cod" below is their own flesh
    FISH = {"minecraft:cod": "terrassic:enchodus", "minecraft:salmon": "terrassic:lepisosteus"}  # the fish the others had in the belly is the Cretaceous one
    PRIME = {  # species: (min, max) prime cuts
        "brachiosaurus": (3, 6), "alamosaurus": (3, 6), "argentinosaurus": (4, 8), "dreadnoughtus": (3, 6), "saltasaurus": (2, 4),
        "opisthocoelicaudia": (2, 4), "tyrannosaurus": (1, 3), "spinosaurus": (1, 3), "giganotosaurus": (1, 3),
        "carcharodontosaurus": (1, 3), "tarbosaurus": (1, 3), "daspletosaurus": (1, 2), "albertosaurus": (1, 2),
        "carnotaurus": (1, 2), "majungasaurus": (1, 2), "triceratops": (1, 3), "styracosaurus": (1, 2), "pachyrhinosaurus": (1, 3),
        "ankylosaurus": (1, 2), "euoplocephalus": (1, 2), "stegosaurus": (1, 2), "therizinosaurus": (1, 2), "deinocheirus": (1, 2),
        "parasaurolophus": (1, 2), "edmontosaurus": (1, 3), "corythosaurus": (1, 2), "maiasaura": (1, 2), "mosasaurus": (2, 4),
        "tylosaurus": (1, 3), "elasmosaurus": (1, 2), "deinosuchus": (1, 2), "quetzalcoatlus": (1, 2), "hatzegopteryx": (1, 2)}

    def item(name, lo, hi, smelt=False, chance=None):
        name = MEAT.get(name, name)
        fns = [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}}]
        if smelt:
            fns.append({"function": "minecraft:furnace_smelt", "conditions": [
                {"condition": "minecraft:entity_properties", "entity": "this", "predicate": {"flags": {"is_on_fire": True}}}]})
        fns.append({"function": "minecraft:looting_enchant", "count": {"type": "minecraft:uniform", "min": 0, "max": 1}})
        pool = {"rolls": 1, "entries": [{"type": "minecraft:item", "name": name, "functions": fns}]}
        if chance is not None:
            pool["conditions"] = [{"condition": "minecraft:killed_by_player"},
                                  {"condition": "minecraft:random_chance_with_looting", "chance": chance, "looting_multiplier": 0.1}]
        return pool
    loot = {
        "tyrannosaurus": [item("minecraft:beef", 4, 8, True), item("minecraft:bone", 2, 5), item("terrassic:rex_tooth", 1, 2, chance=0.6)],
        "spinosaurus": [item("minecraft:beef", 3, 7, True), item("minecraft:bone", 2, 4), item("minecraft:cod", 1, 3, True)],
        "dilophosaurus": [item("minecraft:mutton", 1, 3, True), item("minecraft:bone", 1, 2)],
        "velociraptor": [item("minecraft:chicken", 1, 2, True), item("minecraft:feather", 1, 3)],
        "compsognathus": [item("minecraft:chicken", 0, 1, True), item("minecraft:feather", 0, 2)],
        "triceratops": [item("minecraft:beef", 3, 6, True), item("minecraft:leather", 2, 4), item("terrassic:triceratops_horn", 1, 2, chance=0.5)],
        "stegosaurus": [item("minecraft:beef", 2, 5, True), item("minecraft:leather", 1, 3)],
        "ankylosaurus": [item("minecraft:beef", 2, 5, True), item("minecraft:leather", 2, 4), item("terrassic:ankylosaurus_club", 1, 1, chance=0.4)],
        "euoplocephalus": [item("minecraft:beef", 2, 4, True), item("minecraft:leather", 2, 4), item("terrassic:ankylosaurus_club", 1, 1, chance=0.25)],
        "therizinosaurus": [item("minecraft:beef", 3, 6, True), item("minecraft:feather", 3, 6), item("minecraft:bone", 2, 4)],
        "deinocheirus": [item("minecraft:beef", 3, 6, True), item("minecraft:feather", 2, 4), item("minecraft:bone", 2, 4)],
        "brachiosaurus": [item("minecraft:beef", 8, 14, True), item("minecraft:leather", 4, 8), item("minecraft:bone", 4, 8)],
        "alamosaurus": [item("minecraft:beef", 10, 16, True), item("minecraft:leather", 5, 9), item("minecraft:bone", 5, 9)],
        "saltasaurus": [item("minecraft:beef", 5, 9, True), item("minecraft:leather", 3, 6), item("minecraft:bone", 3, 6)],
        "argentinosaurus": [item("minecraft:beef", 12, 20, True), item("minecraft:leather", 6, 10), item("minecraft:bone", 6, 12)],
        "opisthocoelicaudia": [item("minecraft:beef", 5, 9, True), item("minecraft:leather", 3, 6), item("minecraft:bone", 3, 6)],
        "dreadnoughtus": [item("minecraft:beef", 9, 15, True), item("minecraft:leather", 5, 8), item("minecraft:bone", 5, 9)],
        "giganotosaurus": [item("minecraft:beef", 4, 8, True), item("minecraft:bone", 3, 6), item("minecraft:leather", 1, 3)],
        "carcharodontosaurus": [item("minecraft:beef", 4, 8, True), item("minecraft:bone", 3, 6), item("minecraft:leather", 1, 3)],
        "carnotaurus": [item("minecraft:beef", 3, 6, True), item("minecraft:bone", 2, 4), item("minecraft:leather", 1, 2)],
        "tarbosaurus": [item("minecraft:beef", 4, 8, True), item("minecraft:bone", 3, 6), item("minecraft:leather", 1, 3)],
        "daspletosaurus": [item("minecraft:beef", 3, 7, True), item("minecraft:bone", 2, 5), item("minecraft:leather", 1, 2)],
        "albertosaurus": [item("minecraft:beef", 3, 6, True), item("minecraft:bone", 2, 5), item("minecraft:leather", 1, 2)],
        "majungasaurus": [item("minecraft:beef", 3, 5, True), item("minecraft:bone", 2, 4), item("minecraft:leather", 1, 2)],
        "dakotaraptor": [item("minecraft:chicken", 2, 4, True), item("minecraft:feather", 3, 6), item("minecraft:bone", 1, 3)],
        "troodon": [item("minecraft:chicken", 1, 2, True), item("minecraft:feather", 2, 4), item("minecraft:bone", 0, 2)],
        "oviraptor": [item("minecraft:chicken", 1, 2, True), item("minecraft:feather", 2, 4), item("minecraft:egg", 0, 1)],
        "citipati": [item("minecraft:chicken", 2, 3, True), item("minecraft:feather", 3, 5), item("minecraft:egg", 0, 2)],
        "mononykus": [item("minecraft:feather", 1, 3, True), item("minecraft:bone", 0, 1)],
        "didelphodon": [item("minecraft:rabbit_hide", 1, 2, True), item("minecraft:bone", 0, 1), item("minecraft:egg", 0, 1)],
        "parasaurolophus": [item("minecraft:beef", 2, 5, True), item("minecraft:leather", 1, 3)],
        "pachycephalosaurus": [item("minecraft:mutton", 1, 3, True), item("minecraft:bone", 1, 2)],
        "thescelosaurus": [item("minecraft:mutton", 1, 3, True), item("minecraft:leather", 0, 2)],
        "gallimimus": [item("minecraft:chicken", 1, 3, True), item("minecraft:feather", 2, 4)],
        "struthiomimus": [item("minecraft:chicken", 1, 2, True), item("minecraft:feather", 2, 5)],
        "maiasaura": [item("minecraft:beef", 2, 5, True), item("minecraft:leather", 1, 3)],
        "pteranodon": [item("minecraft:chicken", 1, 2, True), item("minecraft:leather", 0, 2), item("minecraft:cod", 0, 2, True)],
        "quetzalcoatlus": [item("minecraft:chicken", 3, 6, True), item("minecraft:leather", 2, 5), item("minecraft:bone", 3, 6)],
        "hatzegopteryx": [item("minecraft:chicken", 3, 6, True), item("minecraft:leather", 3, 6), item("minecraft:bone", 3, 6)],
        "ichthyornis": [item("minecraft:feather", 1, 2), item("minecraft:cod", 0, 1, True)],
        "mosasaurus": [item("minecraft:cod", 4, 8, True), item("minecraft:leather", 3, 6), item("minecraft:bone", 3, 6),
                       item("terrassic:mosasaurus_tooth", 1, 3, chance=0.6)],
        "tylosaurus": [item("minecraft:cod", 3, 7, True), item("minecraft:leather", 3, 5), item("minecraft:bone", 3, 6)],
        "elasmosaurus": [item("minecraft:cod", 2, 5, True), item("minecraft:leather", 2, 4), item("minecraft:bone", 3, 6)],
        "xiphactinus": [item("minecraft:cod", 3, 6, True), item("minecraft:bone", 2, 5)],
        "archelon": [item("minecraft:scute", 1, 3), item("minecraft:bone", 2, 5), item("minecraft:cod", 1, 2, True)],
        "hesperornis": [item("minecraft:feather", 1, 3), item("minecraft:cod", 0, 1, True), item("minecraft:bone", 1, 2)],
        "deinosuchus": [item("minecraft:cod", 2, 5, True), item("minecraft:leather", 3, 6), item("minecraft:bone", 3, 6)],
        "baurusuchus": [item("minecraft:leather", 1, 3), item("minecraft:bone", 2, 4)],
        "edmontosaurus": [item("minecraft:beef", 3, 6, True), item("minecraft:leather", 2, 4), item("minecraft:bone", 2, 4)],
        "corythosaurus": [item("minecraft:beef", 2, 5, True), item("minecraft:leather", 1, 3), item("minecraft:bone", 2, 4)],
        "styracosaurus": [item("minecraft:beef", 2, 5, True), item("minecraft:leather", 2, 4), item("minecraft:bone", 2, 4)],
        "pachyrhinosaurus": [item("minecraft:beef", 3, 6, True), item("minecraft:leather", 2, 5), item("minecraft:bone", 2, 4)],
        "protoceratops": [item("minecraft:mutton", 1, 2, True), item("minecraft:leather", 0, 1), item("minecraft:bone", 0, 2)],
        "leptoceratops": [item("terrassic:raw_dino_meat", 2, 4, True), item("minecraft:leather", 1, 2), item("minecraft:bone", 0, 2)],
        "vegavis": [item("terrassic:raw_dino_meat", 1, 1, True), item("minecraft:feather", 1, 3), item("minecraft:bone", 0, 1)],
        "mesodma": [item("terrassic:raw_dino_meat", 0, 1, True), item("minecraft:rabbit_hide", 0, 1), item("minecraft:bone", 0, 1)],
        "basilemys": [item("terrassic:raw_dino_meat", 1, 2, True), item("minecraft:scute", 1, 3), item("minecraft:bone", 1, 2)],
        "enchodus": [item("terrassic:enchodus", 1, 1, True), item("minecraft:bone", 0, 1)],
        "lepisosteus": [item("terrassic:lepisosteus", 1, 1, True), item("minecraft:bone", 0, 1)],
    }
    for sid, pools in loot.items():
        if sid in SEA_MEAT:
            for pool in pools:
                for entry in pool["entries"]:
                    if entry["name"] == "minecraft:cod":
                        entry["name"] = "terrassic:raw_dino_meat"
        else:
            for pool in pools:
                for entry in pool["entries"]:
                    entry["name"] = FISH.get(entry["name"], entry["name"])
        if sid in PRIME:
            pools = pools + [item("terrassic:raw_prime_meat", *PRIME[sid], True)]
        # every species drops its own hide (last pool, so the pools above stay as they are)
        write(f"{D}/loot_tables/entities/{sid}.json", {"type": "minecraft:entity", "pools": pools + [item(f"terrassic:{sid}_hide", 1, 3)]})
    missing = [sid for sid in SPECIES if sid not in loot]
    assert set(PRIME) <= set(loot), sorted(set(PRIME) - set(loot))
    assert not missing, f"species without loot table: {missing}"
    # every item model must point at a texture that exists (the Mac found 38 fossil icons without one, 24/10)
    bad = []
    for name in sorted(os.listdir(f"{A}/models/item")):
        with open(f"{A}/models/item/{name}") as f:
            model = json.load(f)
        for key, tex in model.get("textures", {}).items():
            ns, _, path = tex.partition(":")
            if ns == "terrassic" and not os.path.exists(f"{A}/textures/{path}.png"):
                bad.append(f"{name}: {tex}")
    if bad:
        raise SystemExit("item models without texture (run tools/spritegen/sprites.py, science.py or blocks.py):\n  " + "\n  ".join(bad))
    print("resources written")


if __name__ == "__main__":
    main()
