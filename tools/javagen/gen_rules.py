"""World rules in the style of ARK's "server settings" (docs/REGRAS.md): one table, RULES, is the single source of
the rule keys, their defaults and ranges, the tab they show on in the Rules screen and their texts in the three
languages. Writes common/src/main/java/com/terrassic/config/Rule.java (the enum the game reads) and exposes LANG,
which gen_resources.py merges into the lang files. Run it directly or through gen_resources.py.

Every rule is a multiplier (or a 0..1 level) saved per world (RulesData) and seeded from the defaults in
config/terrassic-world.json when a world is created. 1.0 is the game as designed; the Rules screen edits them.
"""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
JAVA = os.path.join(ROOT, "common", "src", "main", "java", "com", "terrassic", "config", "Rule.java")

TABS = {  # id: (pt, en, es)
    "general": ("Geral", "General", "General"),
    "breeding": ("Criação", "Breeding", "Cría"),
    "spawning": ("Ecossistema", "Ecosystem", "Ecosistema"),
}

# key, tab, default, min, max, step,
#   (pt label, pt tip), (en label, en tip), (es label, es tip)
RULES = [
    ("difficulty", "general", 0.5, 0.0, 1.0, 0.05,
     ("Nível de dificuldade", "Força das criaturas selvagens: 0 = metade da vida e do dano, 0,5 = normal, 1 = uma vez e meia."),
     ("Difficulty level", "Strength of wild creatures: 0 = half health and damage, 0.5 = normal, 1 = one and a half."),
     ("Nivel de dificultad", "Fuerza de las criaturas salvajes: 0 = mitad de vida y daño, 0,5 = normal, 1 = una vez y media.")),
    ("dino_damage", "general", 1.0, 0.1, 5.0, 0.1,
     ("Dano dos dinos", "Dano que as criaturas causam (selvagens e domesticadas)."),
     ("Dino damage", "Damage the creatures deal (wild and tamed)."),
     ("Daño de los dinos", "Daño que causan las criaturas (salvajes y domesticadas).")),
    ("player_damage", "general", 1.0, 0.1, 5.0, 0.1,
     ("Dano do jogador", "Dano que os jogadores causam nas criaturas."),
     ("Player damage", "Damage players deal to the creatures."),
     ("Daño del jugador", "Daño que los jugadores causan a las criaturas.")),
    ("structure_damage", "general", 1.0, 0.0, 5.0, 0.1,
     ("Dano de estruturas", "Quanto as criaturas quebram blocos pelo caminho (investidas que abrem a mata). 0 = nunca."),
     ("Structure damage", "How much the creatures break blocks in their way (charges that clear the brush). 0 = never."),
     ("Daño a estructuras", "Cuánto rompen bloques las criaturas a su paso (embestidas que abren el monte). 0 = nunca.")),
    ("player_resistance", "general", 1.0, 0.1, 5.0, 0.1,
     ("Resistência do jogador", "Divide o dano que os jogadores recebem das criaturas. 2 = metade do dano."),
     ("Player resistance", "Divides the damage players take from the creatures. 2 = half the damage."),
     ("Resistencia del jugador", "Divide el daño que los jugadores reciben de las criaturas. 2 = la mitad del daño.")),
    ("dino_resistance", "general", 1.0, 0.1, 5.0, 0.1,
     ("Resistência dos dinos", "Divide o dano que as criaturas recebem. 2 = aguentam o dobro."),
     ("Dino resistance", "Divides the damage the creatures take. 2 = they last twice as long."),
     ("Resistencia de los dinos", "Divide el daño que reciben las criaturas. 2 = aguantan el doble.")),
    ("structure_resistance", "general", 1.0, 0.1, 5.0, 0.1,
     ("Resistência de estruturas", "Divide o dano de estruturas: 2 = as criaturas quebram metade dos blocos."),
     ("Structure resistance", "Divides structure damage: 2 = the creatures break half as many blocks."),
     ("Resistencia de estructuras", "Divide el daño a estructuras: 2 = las criaturas rompen la mitad de los bloques.")),
    ("xp_multiplier", "general", 1.0, 0.0, 10.0, 0.1,
     ("Multiplicador de XP", "Experiência ao abater criaturas e ao criar filhotes."),
     ("XP multiplier", "Experience from slaying creatures and from breeding."),
     ("Multiplicador de XP", "Experiencia al abatir criaturas y al criar.")),
    ("taming_speed", "general", 1.0, 0.1, 10.0, 0.1,
     ("Velocidade de domesticação", "Chance de cada mordida de comida domesticar. 2 = o dobro de chance."),
     ("Taming speed", "Chance of each bite of food taming the animal. 2 = twice the chance."),
     ("Velocidad de domesticación", "Probabilidad de que cada bocado domestique. 2 = el doble.")),

    ("hatch_speed", "breeding", 1.0, 0.1, 10.0, 0.1,
     ("Velocidade de chocagem", "Quão rápido os ovos racham e chocam."),
     ("Hatching speed", "How fast the eggs crack and hatch."),
     ("Velocidad de eclosión", "Qué tan rápido se agrietan y eclosionan los huevos.")),
    ("maturation_speed", "breeding", 1.0, 0.1, 20.0, 0.1,
     ("Velocidade de crescimento", "Quão rápido os filhotes viram adultos."),
     ("Maturation speed", "How fast the babies grow up."),
     ("Velocidad de crecimiento", "Qué tan rápido crecen las crías.")),
    ("mating_interval", "breeding", 1.0, 0.1, 5.0, 0.1,
     ("Intervalo de acasalamento", "Espera depois de pôr ovos até poder acasalar de novo. 0,5 = metade."),
     ("Mating interval", "Wait after laying eggs before mating again. 0.5 = half."),
     ("Intervalo de apareamiento", "Espera tras poner huevos antes de volver a aparearse. 0,5 = la mitad.")),
    ("food_drain", "breeding", 1.0, 0.0, 5.0, 0.1,
     ("Consumo de comida", "Quão rápido a fome das criaturas esvazia. 0 = nunca sentem fome."),
     ("Food drain", "How fast the creatures' hunger empties. 0 = never hungry."),
     ("Consumo de comida", "Qué tan rápido se vacía el hambre de las criaturas. 0 = nunca tienen hambre.")),
    ("nest_frequency", "breeding", 1.0, 0.0, 5.0, 0.1,
     ("Ninhos selvagens", "Chance de um bando nascer com ninho e de os selvagens acasalarem sozinhos."),
     ("Wild nests", "Chance of a herd spawning with a nest and of wild animals breeding on their own."),
     ("Nidos salvajes", "Probabilidad de que una manada aparezca con nido y de que los salvajes se apareen solos.")),
    ("migration", "breeding", 1.0, 0.0, 5.0, 0.1,
     ("Frequência de migração", "Quão seguido as manadas partem atrás de pasto novo. 0 = não migram."),
     ("Migration frequency", "How often herds set off for new grazing. 0 = they never migrate."),
     ("Frecuencia de migración", "Qué tan seguido parten las manadas en busca de pasto. 0 = no migran.")),

    ("spawn_density", "spawning", 1.0, 0.0, 5.0, 0.1,
     ("Densidade de vida", "Controla a reposição de fauna. 0 desliga a reposição; terrestres e marinhos ainda podem nascer naturalmente."),
     ("Wildlife density", "Controls wildlife replenishment. 0 disables replenishment; land and sea creatures may still spawn naturally."),
     ("Densidad de vida", "Controla la reposición de fauna. 0 desactiva la reposición; las criaturas terrestres y marinas aún pueden aparecer naturalmente.")),
    ("land_spawns", "spawning", 1.0, 0.0, 5.0, 0.1,
     ("Terrestres", "Manadas, bandos e predadores em terra."),
     ("Land creatures", "Herds, flocks and predators on land."),
     ("Terrestres", "Manadas, bandadas y depredadores en tierra.")),
    ("flyer_spawns", "spawning", 1.0, 0.0, 5.0, 0.1,
     ("Voadores", "Alvo regional de 4 voadores na densidade 1, com reposição a cada 20 segundos. 0 desliga a reposição do céu."),
     ("Flyers", "Regional target of 4 flyers at density 1, replenished every 20 seconds. 0 disables sky replenishment."),
     ("Voladores", "Objetivo regional de 4 voladores con densidad 1, con reposición cada 20 segundos. 0 desactiva la reposición del cielo.")),
    ("sea_spawns", "spawning", 1.0, 0.0, 5.0, 0.1,
     ("Marinhos", "Répteis marinhos, peixes e tartarugas no mar."),
     ("Sea creatures", "Marine reptiles, fish and turtles in the sea."),
     ("Marinos", "Reptiles marinos, peces y tortugas en el mar.")),
    ("baby_share", "spawning", 1.0, 0.0, 5.0, 0.1,
     ("Filhotes nos bandos", "Quantos filhotes andam junto com os adultos."),
     ("Babies in herds", "How many babies travel with the adults."),
     ("Crías en las manadas", "Cuántas crías andan con los adultos.")),
    ("max_creatures", "spawning", 400.0, 50.0, 2000.0, 10.0,
     ("Limite de criaturas", "Máximo de criaturas selvagens carregadas no mundo (desempenho)."),
     ("Creature limit", "Most wild creatures loaded in the world at once (performance)."),
     ("Límite de criaturas", "Máximo de criaturas salvajes cargadas en el mundo (rendimiento).")),
]

UI = {  # key suffix: (pt, en, es)
    "title": ("Regras do Terrassic", "Terrassic Rules", "Reglas de Terrassic"),
    "world": ("Regras deste mundo", "Rules of this world", "Reglas de este mundo"),
    "defaults": ("Regras padrão para mundos novos", "Default rules for new worlds", "Reglas por defecto para mundos nuevos"),
    "save": ("Salvar", "Save", "Guardar"),
    "cancel": ("Cancelar", "Cancel", "Cancelar"),
    "reset": ("Restaurar padrão", "Reset to defaults", "Restablecer"),
    "read_only": ("Só um operador pode mudar as regras deste mundo.", "Only an operator can change the rules of this world.",
                  "Solo un operador puede cambiar las reglas de este mundo."),
    "saved": ("Regras do mundo atualizadas por %s.", "World rules updated by %s.", "Reglas del mundo actualizadas por %s."),
    "denied": ("Você não tem permissão para mudar as regras.", "You are not allowed to change the rules.",
               "No tienes permiso para cambiar las reglas."),
    "button": ("Regras do Terrassic", "Terrassic Rules", "Reglas de Terrassic"),
    "version": ("Valores salvos com o mundo", "Values saved with the world", "Valores guardados con el mundo"),
}


def java_const(key):
    return key.upper()


def num(v):
    return f"{float(v)!r}D"


def gen_java():
    tabs = ", ".join(t.upper() for t in TABS)
    lines = [
        "package com.terrassic.config;",
        "",
        "/**",
        " * The world rules (docs/REGRAS.md). GENERATED by tools/javagen/gen_rules.py from its RULES table: edit the table",
        " * there and run the script, do not edit this file. The values live in {@link Rules}, one set per world.",
        " */",
        "public enum Rule {",
    ]
    body = []
    for key, tab, default, lo, hi, step, *_ in RULES:
        body.append(f"    {java_const(key)}(\"{key}\", Tab.{tab.upper()}, {num(default)}, {num(lo)}, {num(hi)}, {num(step)})")
    lines.append(",\n".join(body) + ";")
    lines += [
        "",
        "    /** The tabs of the Rules screen, in order. */",
        "    public enum Tab {",
        f"        {tabs};",
        "",
        "        public String id() {",
        "            return this.name().toLowerCase(java.util.Locale.ROOT);",
        "        }",
        "    }",
        "",
        "    public final String key;",
        "    public final Tab tab;",
        "    public final double defaultValue;",
        "    public final double min;",
        "    public final double max;",
        "    public final double step;",
        "",
        "    Rule(String key, Tab tab, double defaultValue, double min, double max, double step) {",
        "        this.key = key;",
        "        this.tab = tab;",
        "        this.defaultValue = defaultValue;",
        "        this.min = min;",
        "        this.max = max;",
        "        this.step = step;",
        "    }",
        "",
        "    /** The value kept inside the range and snapped to the step. */",
        "    public double clamp(double value) {",
        "        if (Double.isNaN(value)) {",
        "            return this.defaultValue;",
        "        }",
        "        double snapped = Math.round(value / this.step) * this.step;",
        "        return Math.max(this.min, Math.min(this.max, Math.round(snapped * 1000.0D) / 1000.0D));",
        "    }",
        "",
        "    /** Whether the value is a whole number (a count rather than a multiplier). */",
        "    public boolean whole() {",
        "        return this.step >= 1.0D;",
        "    }",
        "",
        "    public String langKey() {",
        "        return \"rules.terrassic.\" + this.key;",
        "    }",
        "",
        "    public String tipKey() {",
        "        return \"rules.terrassic.\" + this.key + \".tip\";",
        "    }",
        "",
        "    public static Rule byKey(String key) {",
        "        for (Rule r : values()) {",
        "            if (r.key.equals(key)) {",
        "                return r;",
        "            }",
        "        }",
        "        return null;",
        "    }",
        "}",
        "",
    ]
    return "\n".join(lines)


def gen_lang():
    lang = {"pt_br": {}, "en_us": {}, "es_es": {}}
    for tid, (pt, en, es) in TABS.items():
        k = f"rules.terrassic.tab.{tid}"
        lang["pt_br"][k], lang["en_us"][k], lang["es_es"][k] = pt, en, es
    for key, tab, default, lo, hi, step, pt, en, es in RULES:
        for code, (label, tip) in (("pt_br", pt), ("en_us", en), ("es_es", es)):
            lang[code][f"rules.terrassic.{key}"] = label
            lang[code][f"rules.terrassic.{key}.tip"] = tip
    for suffix, (pt, en, es) in UI.items():
        k = f"rules.terrassic.ui.{suffix}"
        lang["pt_br"][k], lang["en_us"][k], lang["es_es"][k] = pt, en, es
    return lang


LANG = gen_lang()


def main():
    keys = [r[0] for r in RULES]
    assert len(keys) == len(set(keys)), "duplicate rule key"
    for key, tab, default, lo, hi, step, *_ in RULES:
        assert tab in TABS, f"{key}: unknown tab {tab}"
        assert lo <= default <= hi, f"{key}: default outside its range"
        assert step > 0, f"{key}: step must be positive"
    text = gen_java()
    old = open(JAVA, encoding="utf-8").read() if os.path.exists(JAVA) else None
    if old != text:
        with open(JAVA, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    print(f"rules: {len(RULES)} rules -> {os.path.relpath(JAVA, ROOT)}")


if __name__ == "__main__":
    main()
