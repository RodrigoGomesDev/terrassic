"""
v0.9 "The End" (docs/SALTO.md): JSON and texts of the Leap Altar, the ritual of the meteors, the Rift Tyrant and the
Leap. Called by gen_resources.py (which merges LANG into the language files); can also run alone.

  block    leap_altar (blockstate by "stage", 2 models built from the mod's own textures, item, loot, recipe)
  tags     terrassic:altar_stones / terrassic:altar_bones: the posts of the ring (read from BuildingBlocks.java,
           every entry optional, so renaming a building block never breaks the altar)
  entity   rift_tyrant (loot), meteor
  art      tools/spritegen/leap_art.py (rift_overlay.png, meteor.png)
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
RES = os.path.join(ROOT, "common", "src", "main", "resources")
A = os.path.join(RES, "assets", "terrassic")
D = os.path.join(RES, "data", "terrassic")
BUILDING = os.path.join(ROOT, "common", "src", "main", "java", "com", "terrassic", "registry", "BuildingBlocks.java")

LANG = {"en_us": {}, "pt_br": {}, "es_es": {}}


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def T(key, en, pt, es):
    LANG["en_us"][key] = en
    LANG["pt_br"][key] = pt
    LANG["es_es"][key] = es


# ------------------------------------------------------------------ texts

def texts():
    T("block.terrassic.leap_altar", "Leap Altar", "Altar do Salto", "Altar del Salto")
    T("entity.terrassic.rift_tyrant", "Rift Tyrant", "Tirano da Fenda", "Tirano de la Grieta")
    T("entity.terrassic.meteor", "Meteor", "Meteoro", "Meteoro")

    T("altar.terrassic.mode.normal", "Normal", "Normal", "Normal")
    T("altar.terrassic.mode.rapido", "Fast", "Rápido", "Rápido")
    T("altar.terrassic.mode.livre", "Free", "Livre", "Libre")
    T("altar.terrassic.status",
      "Leap Altar: %1$s of %2$s amber fragments (mode %3$s).",
      "Altar do Salto: %1$s de %2$s fragmentos de âmbar (modo %3$s).",
      "Altar del Salto: %1$s de %2$s fragmentos de ámbar (modo %3$s).")
    T("altar.terrassic.ring_missing",
      "The altar's ring is incomplete: %s posts missing. Standing stones (menhir or stacked stone) go 3 blocks away "
      "at north, south, east and west; bone (ossuary wall, rib arch, bone pile or a skull trophy) on the 4 diagonals, "
      "2 and 2 blocks away. The sparks show where.",
      "O anel do Altar está incompleto: faltam %s postes. Pedras em pé (menir ou pedra empilhada) ficam a 3 blocos, "
      "no norte, sul, leste e oeste; osso (muro de ossário, arco de costelas, pilha de ossos ou um troféu de crânio) "
      "nas 4 diagonais, a 2 e 2 blocos. As faíscas mostram onde.",
      "El anillo del Altar está incompleto: faltan %s postes. Piedras en pie (menhir o piedra apilada) van a 3 bloques, "
      "al norte, sur, este y oeste; hueso (muro de osario, arco de costillas, pila de huesos o un trofeo de cráneo) en "
      "las 4 diagonales, a 2 y 2 bloques. Las chispas muestran dónde.")
    T("altar.terrassic.hint.need_fragments",
      "Complete objectives in your Field Journal: 2 of each theme give one fragment. With 4 the altar can be lit.",
      "Complete objetivos do Diário de Campo: 2 de cada tema dão um fragmento. Com 4 o Altar pode ser aceso.",
      "Completa objetivos del Diario de Campo: 2 de cada tema dan un fragmento. Con 4 el Altar puede encenderse.")
    T("altar.terrassic.hint.ritual",
      "The core is whole. Sneak and offer raw amber to start the ritual of the meteors, when you are ready: the Rift "
      "Tyrant will answer.",
      "O núcleo está inteiro. Agache e ofereça âmbar bruto para começar o ritual dos meteoros, quando estiver pronto: "
      "o Tirano da Fenda vai responder.",
      "El núcleo está entero. Agáchate y ofrece ámbar en bruto para empezar el ritual de los meteoros, cuando estés "
      "listo: el Tirano de la Grieta responderá.")
    T("altar.terrassic.hint.unstable",
      "With %s fragments you can force an Unstable Leap, without the boss: sneak and offer raw amber twice. You may "
      "land anywhere.",
      "Com %s fragmentos dá para forçar um Salto Instável, sem o chefe: agache e ofereça âmbar bruto duas vezes. "
      "Você pode cair em qualquer lugar.",
      "Con %s fragmentos puedes forzar un Salto Inestable, sin el jefe: agáchate y ofrece ámbar en bruto dos veces. "
      "Puedes caer en cualquier lugar.")
    T("altar.terrassic.hint.leap",
      "The altar is open for you. Stand in the ring with whoever goes along, then sneak and use it with an empty hand "
      "to leap, whenever you want.",
      "O Altar está aberto para você. Fique no anel com quem for junto, agache e use com a mão vazia para saltar, "
      "quando quiser.",
      "El Altar está abierto para ti. Quédate en el anillo con quien vaya contigo, agáchate y úsalo con la mano vacía "
      "para saltar, cuando quieras.")
    T("altar.terrassic.hint.leap_or_ritual",
      "The altar is open for you: sneak with an empty hand to leap. The ritual of the meteors is optional in this "
      "mode (sneak and offer raw amber).",
      "O Altar está aberto para você: agache com a mão vazia para saltar. O ritual dos meteoros é opcional neste modo "
      "(agache e ofereça âmbar bruto).",
      "El Altar está abierto para ti: agáchate con la mano vacía para saltar. El ritual de los meteoros es opcional en "
      "este modo (agáchate y ofrece ámbar en bruto).")
    T("altar.terrassic.unstable_confirm",
      "The Rift trembles. Offer amber again within 5 seconds to leap without the whole core (Unstable Leap).",
      "A Fenda treme. Ofereça âmbar de novo em 5 segundos para saltar sem o núcleo inteiro (Salto Instável).",
      "La Grieta tiembla. Ofrece ámbar de nuevo en 5 segundos para saltar sin el núcleo entero (Salto Inestable).")
    T("altar.terrassic.ritual_running",
      "The ritual has begun. Survive it!",
      "O ritual já começou. Sobreviva!",
      "El ritual ya empezó. ¡Sobrevive!")
    T("altar.terrassic.ritual_start",
      "The amber burns and the sky fills with fire. Something on the other side of the Rift heard the call...",
      "O âmbar queima e o céu se enche de fogo. Algo do outro lado da Fenda ouviu o chamado...",
      "El ámbar arde y el cielo se llena de fuego. Algo al otro lado de la Grieta oyó la llamada...")
    T("altar.terrassic.tyrant_arrives",
      "The Rift Tyrant came through!",
      "O Tirano da Fenda atravessou!",
      "¡El Tirano de la Grieta atravesó!")
    T("altar.terrassic.victory",
      "The Rift Tyrant has fallen and the meteors stop. The altar is open for you: stand in the ring, sneak and use it "
      "with an empty hand to leap, whenever you want.",
      "O Tirano da Fenda caiu e os meteoros param. O Altar está aberto para você: fique no anel, agache e use com a "
      "mão vazia para saltar, quando quiser.",
      "El Tirano de la Grieta cayó y los meteoros se detienen. El Altar está abierto para ti: quédate en el anillo, "
      "agáchate y úsalo con la mano vacía para saltar, cuando quieras.")
    T("altar.terrassic.retreat",
      "The Rift Tyrant went back into the Rift. The ritual is over; offer amber again when you are ready.",
      "O Tirano da Fenda voltou para a Fenda. O ritual acabou; ofereça âmbar de novo quando estiver pronto.",
      "El Tirano de la Grieta volvió a la Grieta. El ritual terminó; ofrece ámbar otra vez cuando estés listo.")
    T("altar.terrassic.broken",
      "The altar broke and the ritual ended. The Rift Tyrant went back into the Rift.",
      "O Altar quebrou e o ritual acabou. O Tirano da Fenda voltou para a Fenda.",
      "El Altar se rompió y el ritual terminó. El Tirano de la Grieta volvió a la Grieta.")
    T("leap.terrassic.no_destination",
      "The light fades... and the Rift does not open. Chapter %s, the Early Cretaceous, arrives in a future version "
      "of Terrassic. Nothing is lost: the altar stays open for you.",
      "A luz se apaga... e a Fenda não se abre. O Capítulo %s, o Cretáceo Inferior, chega numa próxima versão do "
      "Terrassic. Nada se perde: o Altar continua aberto para você.",
      "La luz se apaga... y la Grieta no se abre. El Capítulo %s, el Cretácico Inferior, llega en una próxima versión "
      "de Terrassic. Nada se pierde: el Altar sigue abierto para ti.")

    T("command.terrassic.mode.current", "Mode of this world: %s", "Modo deste mundo: %s", "Modo de este mundo: %s")
    T("command.terrassic.mode.set", "Mode of this world changed to %s", "Modo deste mundo mudou para %s",
      "Modo de este mundo cambiado a %s")
    T("command.terrassic.mode.unknown", "Unknown mode: %s (use normal, rapido or livre)",
      "Modo desconhecido: %s (use normal, rapido ou livre)", "Modo desconocido: %s (usa normal, rapido o livre)")
    T("command.terrassic.chapter.here", "You are already in Chapter %s.", "Você já está no Capítulo %s.",
      "Ya estás en el Capítulo %s.")
    T("command.terrassic.chapter.done", "Taken to Chapter %s.", "Levado ao Capítulo %s.", "Llevado al Capítulo %s.")
    T("command.terrassic.chapter.later", "Chapter %s is not in the game yet.", "O Capítulo %s ainda não está no jogo.",
      "El Capítulo %s aún no está en el juego.")
    T("command.terrassic.ritual.stopped", "Rituals stopped: %s", "Rituais parados: %s", "Rituales detenidos: %s")


# ------------------------------------------------------------------ the altar block

def cube(frm, to, tex, top=None, bottom=None, uv_side=None):
    faces = {}
    for f in ("north", "south", "east", "west"):
        face = {"texture": tex}
        if uv_side:
            face["uv"] = uv_side
        faces[f] = face
    faces["up"] = {"texture": top or tex}
    faces["down"] = {"texture": bottom or tex}
    return {"from": frm, "to": to, "faces": faces}


def altar_model(lit):
    amber = "#amber"
    return {
        "parent": "minecraft:block/block",
        "textures": {
            "stone": "terrassic:block/limestone_stacked",
            "bone": "terrassic:block/ossuary_wall",
            "hide": "terrassic:block/tanned_hide_panel",
            "amber": "terrassic:block/" + ("polished_amber" if lit else "amber_block"),
            "particle": "terrassic:block/limestone_stacked",
        },
        "elements": [
            cube([0, 0, 0], [16, 4, 16], "#stone", uv_side=[0, 12, 16, 16]),            # the stone plinth
            cube([3, 4, 3], [13, 9, 13], "#bone", uv_side=[3, 7, 13, 12]),              # the drum of bone
            cube([2.5, 6, 2.5], [13.5, 8, 13.5], "#hide", uv_side=[0, 7, 16, 9]),      # the hide wrapped around it
            cube([5, 9, 5], [11, 16, 11], amber, uv_side=[5, 0, 11, 7]),               # the amber core
            cube([3.5, 9, 9], [6, 13, 11.5], amber, uv_side=[3, 3, 6, 7]),             # two smaller shards
            cube([10, 9, 4], [12.5, 12, 6.5], amber, uv_side=[10, 4, 13, 7]),
        ],
    }


def altar():
    write(f"{A}/models/block/leap_altar.json", altar_model(False))
    write(f"{A}/models/block/leap_altar_lit.json", altar_model(True))
    write(f"{A}/blockstates/leap_altar.json", {"variants": {
        "stage=0": {"model": "terrassic:block/leap_altar"},
        "stage=1": {"model": "terrassic:block/leap_altar"},
        "stage=2": {"model": "terrassic:block/leap_altar_lit"},
        "stage=3": {"model": "terrassic:block/leap_altar_lit"},
    }})
    write(f"{A}/models/item/leap_altar.json", {"parent": "terrassic:block/leap_altar_lit"})
    write(f"{D}/loot_tables/blocks/leap_altar.json", {"type": "minecraft:block", "pools": [{
        "rolls": 1, "entries": [{"type": "minecraft:item", "name": "terrassic:leap_altar"}],
        "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
    write(f"{D}/recipes/leap_altar.json", {
        "type": "minecraft:crafting_shaped", "category": "misc",
        "pattern": ["HAH", "BBB", "SSS"],
        "key": {"H": {"item": "terrassic:tanned_hide_panel"}, "A": {"item": "terrassic:amber_block"},
                "B": {"item": "terrassic:ossuary_wall"}, "S": {"item": "terrassic:limestone_stacked"}},
        "result": {"item": "terrassic:leap_altar"}})


def ring_tags():
    with open(BUILDING, encoding="utf-8") as f:
        names = re.findall(r'ModBlocks\.\w+\("([a-z0-9_]+)"', f.read())
    stones = ["menhir"] + [n for n in names if n.endswith("_stacked")]
    bones = [n for n in names if n in ("ossuary_wall", "rib_arch", "bone_pile") or n.endswith("_skull_trophy")]
    if "menhir" not in names or not bones:
        raise SystemExit("gen_leap: the ring's building blocks (menhir, ossuary_wall...) are not in BuildingBlocks.java")

    def tag(values, extra=()):
        return {"replace": False, "values": [{"id": f"terrassic:{n}", "required": False} for n in values]
                + [{"id": e, "required": False} for e in extra]}
    write(f"{D}/tags/blocks/altar_stones.json", tag(stones))
    write(f"{D}/tags/blocks/altar_bones.json", tag(bones, ("minecraft:bone_block",)))
    return len(stones), len(bones)


def entities():
    def pool(item, lo, hi):
        return {"rolls": 1, "entries": [{"type": "minecraft:item", "name": item, "functions": [
            {"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}}]}]}
    write(f"{D}/loot_tables/entities/rift_tyrant.json", {"type": "minecraft:entity", "pools": [
        pool("terrassic:raw_amber", 3, 5), pool("terrassic:rex_tooth", 2, 4), pool("terrassic:raw_prime_meat", 6, 10)]})


def main():
    texts()
    altar()
    stones, bones = ring_tags()
    entities()
    print(f"leap: altar, ring tags ({stones} stones, {bones} bones), rift tyrant, {len(LANG['en_us'])} texts")


if __name__ == "__main__":
    main()
