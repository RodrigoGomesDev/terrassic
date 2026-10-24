"""The advancement tree (docs/CONQUISTAS.md): one tab per chapter and the "Field Notebook" tab that counts in every
era.  gen_science.py writes the JSON from NODES and merges LANG.

Each node: id "<tab>/<name>", parent, icon, frame, trigger, xp, ready, hidden, texts (pt, en, es).
- trigger "code": criterion "done" (minecraft:impossible), awarded by Research.award / Research.objective.
- trigger "tick": the tab root, granted on the first tick in the world.
- trigger ("item", id): granted by minecraft:inventory_changed when the player has that item, no Java needed.
- ready=False: the feature is not in the game yet; the node is documented here but not written.
- objective nodes (chapter1/<Objective id>) take their texts from lore.OBJECTIVES, shared with the notebook.
- fragment nodes give 1 Loose Page (loot table rewards/katarina_page) on top of the XP.
"""
import lore

NS = "terrassic"

TABS = {  # tab: background texture of the advancements screen
    "chapter1": "minecraft:textures/block/packed_mud.png",
    "journal": f"{NS}:textures/block/fossil_rock.png",
}


def N(nid, parent, icon, texts=None, frame="task", trigger="code", xp=10, ready=True, hidden=False, page=False):
    return dict(id=nid, parent=parent, icon=icon, texts=texts, frame=frame, trigger=trigger, xp=xp, ready=ready,
                hidden=hidden, page=page)


def T(title, desc):
    """title and desc are (pt, en, es)"""
    return (title, desc)


def fragment_texts(theme):
    pt, en, es = lore.THEMES[theme]
    return T((f"Fragmento: {pt}", f"Fragment: {en}", f"Fragmento: {es}"),
             (f"Complete 2 dos 3 objetivos de {pt}. Um pedaço do núcleo de âmbar volta para você, com uma página da Katarina.",
              f"Complete 2 of the 3 {en} objectives. A piece of the amber core comes back to you, with one of Katarina's pages.",
              f"Completa 2 de los 3 objetivos de {es}. Un pedazo del núcleo de ámbar vuelve a ti, con una página de Katarina."))


# Diary objectives of Chapter 1 per theme, in the order of the Objective enum; False = not in the game yet
CHAPTER1_THEMES = {
    "survival": [("shelter", "terrassic:thatch", True), ("first_spear", "terrassic:flint_spear", True),
                 ("rift_storm", "minecraft:amethyst_shard", False)],
    "science": [("study_five", "minecraft:writable_book", True), ("first_fossil", "terrassic:hair_brush", True),
                ("research_table", "terrassic:research_table", True)],
    "taming": [("tame_herbivore", "minecraft:fern", True), ("hatch_egg", "terrassic:triceratops_egg", True),
               ("ride", "minecraft:saddle", True)],
    "exploration": [("katarina_pages", "terrassic:loose_page", True), ("inland_sea", "terrassic:mosasaurus_spawn_egg", True),
                    ("migration", "terrassic:maiasaura_spawn_egg", False)],
}

NODES = [
    # ================================================================ Chapter 1: Echoes of the End
    N("chapter1/root", None, "terrassic:tyrannosaurus_spawn_egg", T(
        ("Ecos do Fim", "Echoes of the End", "Ecos del Fin"),
        ("Cretáceo Superior, 68 milhões de anos atrás. Você acordou de mãos vazias.",
         "Late Cretaceous, 68 million years ago. You woke up empty-handed.",
         "Cretácico Superior, hace 68 millones de años. Despertaste con las manos vacías.")), trigger="tick", xp=0),
]
for _theme, _objectives in CHAPTER1_THEMES.items():
    NODES.append(N(f"chapter1/fragment_{_theme}", "chapter1/root", "terrassic:raw_amber", fragment_texts(_theme),
                   frame="goal", xp=50, page=True))
    for _oid, _icon, _ready in _objectives:
        NODES.append(N(f"chapter1/{_oid}", f"chapter1/fragment_{_theme}", _icon, ready=_ready))

NODES += [
    # chapter feats hanging from their objective
    N("chapter1/all_cretaceous", "chapter1/study_five", "terrassic:field_notebook", T(
        ("Naturalista do Cretáceo", "Cretaceous Naturalist", "Naturalista del Cretácico"),
        ("Estude todas as espécies do Cretáceo Superior do Guia de Campo.",
         "Study every Late Cretaceous species in the Field Guide.",
         "Estudia todas las especies del Cretácico Superior de la Guía de Campo.")), frame="challenge", xp=100),
    N("chapter1/pet_rex", "chapter1/hatch_egg", "terrassic:tyrannosaurus_egg", T(
        ("Rei de estimação", "A pet king", "Rey de compañía"),
        ("Domestique um Tiranossauro, o rei do Cretáceo.", "Tame a Tyrannosaurus, king of the Cretaceous.",
         "Domestica un Tiranosaurio, el rey del Cretácico.")), frame="challenge", xp=100),

    # the Leap: what lights the Altar and opens the next era
    N("chapter1/four_fragments", "chapter1/root", "minecraft:amethyst_cluster", T(
        ("O núcleo reunido", "The core, whole again", "El núcleo reunido"),
        ("Junte os 4 fragmentos de âmbar do capítulo. Com eles o Altar do Salto pode ser aceso, quando você quiser.",
         "Gather the chapter's 4 amber fragments. With them the Leap Altar can be lit, whenever you choose.",
         "Reúne los 4 fragmentos de ámbar del capítulo. Con ellos se puede encender el Altar del Salto, cuando tú quieras.")),
      frame="goal", xp=100),
    N("chapter1/meteor_ritual", "chapter1/four_fragments", "minecraft:fire_charge", T(
        ("Estrelas que caem", "Falling stars", "Estrellas que caen"),
        ("Comece o ritual no Altar do Salto. O céu vai se encher de fogo.",
         "Start the ritual at the Leap Altar. The sky will fill with fire.",
         "Empieza el ritual en el Altar del Salto. El cielo se llenará de fuego.")), xp=25, ready=False),
    N("chapter1/rift_tyrant", "chapter1/meteor_ritual", "terrassic:rex_tooth", T(
        ("Tirano da Fenda", "Rift Tyrant", "Tirano de la Grieta"),
        ("Vença o Tirano da Fenda enquanto os meteoros caem.", "Defeat the Rift Tyrant while the meteors fall.",
         "Vence al Tirano de la Grieta mientras caen los meteoros.")), frame="goal", xp=100, ready=False),
    N("chapter1/leap", "chapter1/rift_tyrant", "minecraft:ender_eye", T(
        ("O Salto", "The Leap", "El Salto"),
        ("Ative o Altar e salte para o Cretáceo Inferior, atrás da Katarina.",
         "Activate the Altar and leap to the Early Cretaceous, after Katarina.",
         "Activa el Altar y salta al Cretácico Inferior, tras Katarina.")), frame="goal", xp=100, ready=False),
    N("chapter1/unstable_jump", "chapter1/root", "minecraft:chorus_fruit", T(
        ("Salto Instável", "Unstable Leap", "Salto Inestable"),
        ("Salte com só 2 fragmentos. Onde você foi parar?", "Leap with only 2 fragments. Where did you end up?",
         "Salta con solo 2 fragmentos. ¿Dónde fuiste a parar?")), hidden=True, xp=25, ready=False),

    # Katarina's trail
    N("chapter1/first_page", "chapter1/root", "minecraft:paper", T(
        ("Ela esteve aqui", "She was here", "Ella estuvo aquí"),
        ("Ache uma página do caderno da Katarina.", "Find a page from Katarina's notebook.",
         "Encuentra una página del cuaderno de Katarina.")), xp=10),
    N("chapter1/river_house", "chapter1/first_page", "minecraft:campfire", T(
        ("Casa do Rio", "River House", "Casa del Río"),
        ("Ache o Refúgio da Katarina na margem do rio.", "Find Katarina's Refuge on the riverbank.",
         "Encuentra el Refugio de Katarina a orillas del río.")), xp=25, ready=False),
    N("chapter1/mate", "chapter1/river_house", "terrassic:parasaurolophus_spawn_egg", T(
        ("Mate", "Mate", "Mate"),
        ("O Parasaurolophus da Katarina aceita você como dono. Bom Mate.",
         "Katarina's Parasaurolophus accepts you as its owner. Good mate.",
         "El Parasaurolophus de Katarina te acepta como dueño. Buen mate.")), xp=25, ready=False),

    # the Rift
    N("chapter1/out_of_time", "chapter1/root", "terrassic:stegosaurus_spawn_egg", T(
        ("Fora de época", "Out of time", "Fuera de época"),
        ("Aviste uma criatura de outra era. Ela não devia estar aqui.", "Spot a creature from another era. It should not be here.",
         "Avista una criatura de otra era. No debería estar aquí.")), xp=10),
    N("chapter1/time_island", "chapter1/out_of_time", "minecraft:packed_ice", T(
        ("Ilha do Tempo", "Time Island", "Isla del Tiempo"),
        ("Pise num pedaço de outra era que a Fenda colou neste mundo.",
         "Step onto a piece of another era that the Rift stuck into this world.",
         "Pisa un pedazo de otra era que la Grieta pegó en este mundo.")), xp=25, ready=False),
    N("chapter1/rift_anomaly", "chapter1/time_island", "minecraft:crying_obsidian", T(
        ("Anomalia", "Anomaly", "Anomalía"),
        ("Derrote uma criatura da Fenda, de olhos cor de âmbar.", "Defeat a Rift creature with amber eyes.",
         "Derrota a una criatura de la Grieta de ojos color ámbar.")), xp=25, ready=False),

    # ================================================================ Field Notebook (every era)
    N("journal/root", None, "terrassic:field_notebook", T(
        ("Caderno de Campo", "Field Notebook", "Cuaderno de Campo"),
        ("O caderno que a Katarina começou e você continua. Vale em qualquer era.",
         "The notebook Katarina started and you carry on. It counts in every era.",
         "El cuaderno que Katarina empezó y tú continúas. Vale en cualquier era.")), trigger="tick", xp=0),
    # Field Guide
    N("journal/first_sighting", "journal/root", "terrassic:gallimimus_spawn_egg", T(
        ("Visto vivo", "Seen alive", "Visto con vida"),
        ("Chegue perto de um dinossauro, ou observe um pela Lente de Âmbar.",
         "Get close to a dinosaur, or watch one through the Amber Lens.",
         "Acércate a un dinosaurio, u obsérvalo con la Lente de Ámbar."))),
    N("journal/first_studied", "journal/first_sighting", "terrassic:sketch", T(
        ("Anotado", "Noted down", "Anotado"),
        ("Estude uma espécie até o nível \"Estudado\": esboço, fóssil, amostra ou derrotar uma.",
         "Study a species up to \"Studied\": a sketch, a fossil, a sample or defeating one.",
         "Estudia una especie hasta \"Estudiado\": un boceto, un fósil, una muestra o derrotar uno.")), xp=25),
    N("journal/guide_complete", "journal/first_studied", "minecraft:enchanted_book", T(
        ("Guia de Campo completo", "Complete Field Guide", "Guía de Campo completa"),
        ("Estude todas as espécies do Guia. A Katarina vai querer ler isto.",
         "Study every species in the Guide. Katarina will want to read this.",
         "Estudia todas las especies de la Guía. Katarina querrá leer esto.")), frame="challenge", xp=100),
    N("journal/first_silhouette", "journal/root", "terrassic:triceratops_fossil", T(
        ("Só os ossos", "Only bones", "Solo huesos"),
        ("Estude um fóssil na Mesa de Pesquisa.", "Study a fossil at the Research Table.",
         "Estudia un fósil en la Mesa de Investigación."))),
    N("journal/deep_time", "journal/first_silhouette", "terrassic:stegosaurus_fossil", T(
        ("Ossos do futuro", "Bones of the future", "Huesos del futuro"),
        ("Estude o fóssil de uma era mais antiga que a sua. São animais que você ainda vai conhecer vivos.",
         "Study a fossil from an era older than yours. These are animals you have yet to meet alive.",
         "Estudia el fósil de una era más antigua que la tuya. Son animales que aún vas a conocer con vida.")), xp=25),
    # scientist tools
    N("journal/raw_amber", "journal/root", "terrassic:raw_amber", T(
        ("Lágrima de árvore", "Tree tear", "Lágrima de árbol"),
        ("Deixe a resina de um frasco endurecer em Âmbar Bruto.", "Let the resin in a jar harden into Raw Amber.",
         "Deja que la resina de un frasco se endurezca en Ámbar en Bruto.")), trigger=("item", "terrassic:raw_amber")),
    N("journal/amber_lens", "journal/raw_amber", "terrassic:amber_lens", T(
        ("Olho de âmbar", "Amber eye", "Ojo de ámbar"),
        ("Observe uma criatura pela Lente de Âmbar até ela entrar no Guia.",
         "Watch a creature through the Amber Lens until it goes into the Guide.",
         "Observa una criatura con la Lente de Ámbar hasta que entre en la Guía."))),
    N("journal/first_sketch", "journal/root", "terrassic:sketching_charcoal", T(
        ("Traço de carvão", "Charcoal lines", "Trazos de carbón"),
        ("Desenhe uma criatura com o Carvão de Esboço.", "Draw a creature with the Sketching Charcoal.",
         "Dibuja una criatura con el Carbón de Boceto."))),
    N("journal/blood_sample", "journal/first_sketch", "terrassic:blood_sample", T(
        ("Frasco cheio", "A full jar", "Frasco lleno"),
        ("Leve um Frasco de Argila vazio e derrote um dinossauro.", "Carry an empty Clay Jar and defeat a dinosaur.",
         "Lleva un Frasco de Arcilla vacío y derrota a un dinosaurio.")), trigger=("item", "terrassic:blood_sample")),
    # taming and riding
    N("journal/ride_flyer", "journal/root", "terrassic:pteranodon_spawn_egg", T(
        ("Asas de couro", "Leather wings", "Alas de cuero"),
        ("Voe montado num pterossauro domesticado.", "Fly a tamed pterosaur.",
         "Vuela montado en un pterosaurio domesticado.")), xp=25),
    N("journal/ride_swimmer", "journal/root", "terrassic:mosasaurus_spawn_egg", T(
        ("Nadadeiras", "Flippers", "Aletas"),
        ("Nade montado num réptil marinho domesticado.", "Swim riding a tamed marine reptile.",
         "Nada montado en un reptil marino domesticado.")), xp=25, ready=False),
    N("journal/five_tamed", "journal/root", "minecraft:lead", T(
        ("Manada mista", "Mixed herd", "Manada mixta"),
        ("Domestique 5 espécies diferentes.", "Tame 5 different species.", "Domestica 5 especies diferentes.")), xp=25),
    N("journal/every_era", "journal/five_tamed", "terrassic:brachiosaurus_spawn_egg", T(
        ("Uma de cada era", "One from every era", "Uno de cada era"),
        ("Tenha uma criatura domesticada de cada era.", "Have a tamed creature from every era.",
         "Ten una criatura domesticada de cada era.")), frame="challenge", xp=100, ready=False),
    N("journal/knockout", "journal/root", "terrassic:bone_club", T(
        ("Boa noite", "Good night", "Buenas noches"),
        ("Derrube uma criatura sem matar: clava, boleadeira ou dardo.",
         "Knock a creature out without killing it: club, bola or dart.",
         "Derriba una criatura sin matarla: garrote, boleadoras o dardo.")), ready=False),
    N("journal/knockout_tame", "journal/knockout", "minecraft:fern", T(
        ("Domado no sono", "Tamed in its sleep", "Domado en sueños"),
        ("Alimente uma criatura derrubada até ela acordar domada.", "Feed a knocked-out creature until it wakes up tame.",
         "Alimenta a una criatura derribada hasta que despierte domada.")), xp=25, ready=False),
    # Katarina's pages
    N("journal/five_pages", "journal/root", "terrassic:loose_page", T(
        ("Leitor atento", "Close reader", "Lector atento"),
        ("Junte 5 páginas da Katarina.", "Collect 5 of Katarina's pages.", "Reúne 5 páginas de Katarina.")), xp=25),
    N("journal/all_pages", "journal/five_pages", "minecraft:writable_book", T(
        ("O caderno dela", "Her notebook", "Su cuaderno"),
        ("Junte todas as páginas da Katarina.", "Collect every one of Katarina's pages.",
         "Reúne todas las páginas de Katarina.")), frame="challenge", xp=100),
    # after the ending
    N("journal/expedition", "journal/root", "minecraft:map", T(
        ("Expedição", "Expedition", "Expedición"),
        ("Complete um pedido de pesquisa do laboratório.", "Complete a research request from the lab.",
         "Completa un pedido de investigación del laboratorio.")), xp=25, ready=False),
]

CODES = ("pt_br", "en_us", "es_es")


def key(nid, field):
    tab, name = nid.split("/")
    return f"advancements.{NS}.{tab}.{name}.{field}"


def objective_ids():
    return [oid for objectives in CHAPTER1_THEMES.values() for oid, _icon, _ready in objectives]


def lang():
    """{code: {key: text}} for every node with its own texts (objectives use objective.terrassic.*)."""
    out = {c: {} for c in CODES}
    for n in NODES:
        if n["texts"] is None:
            continue
        for field, values in zip(("title", "description"), n["texts"]):
            for code, text in zip(CODES, values):
                out[code][key(n["id"], field)] = text
    return out


def advancement(n):
    if n["texts"] is None:  # a diary objective
        name = n["id"].split("/")[1]
        title, desc = {"translate": f"objective.{NS}.{name}"}, {"translate": f"objective.{NS}.{name}.hint"}
    else:
        title, desc = {"translate": key(n["id"], "title")}, {"translate": key(n["id"], "description")}
    display = {"icon": {"item": n["icon"]}, "title": title, "description": desc}
    if n["frame"] != "task":
        display["frame"] = n["frame"]
    if n["hidden"]:
        display["hidden"] = True
    tab = n["id"].split("/")[0]
    if n["parent"] is None:
        display.update(background=TABS[tab], show_toast=False, announce_to_chat=False)
    trigger = n["trigger"]
    if trigger == "tick":
        criteria = {"tick": {"trigger": "minecraft:tick"}}
    elif trigger == "code":
        criteria = {"done": {"trigger": "minecraft:impossible"}}
    else:
        criteria = {"has": {"trigger": "minecraft:inventory_changed", "conditions": {"items": [{"items": [trigger[1]]}]}}}
    data = {}
    if n["parent"]:
        data["parent"] = f"{NS}:{n['parent']}"
    data["display"] = display
    data["criteria"] = criteria
    rewards = {}
    if n["xp"]:
        rewards["experience"] = n["xp"]
    if n["page"]:
        rewards["loot"] = [f"{NS}:rewards/katarina_page"]
    if rewards:
        data["rewards"] = rewards
    return data


def emitted():
    """Nodes that go into the game (ready); fails if a ready node hangs from one that is not."""
    ready = {n["id"] for n in NODES if n["ready"]}
    for n in NODES:
        if n["ready"] and n["parent"] and n["parent"] not in ready:
            raise SystemExit(f"advancement {n['id']} is ready but its parent {n['parent']} is not")
    ids = [n["id"] for n in NODES]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate advancement ids in conquistas.NODES")
    return [n for n in NODES if n["ready"]]
