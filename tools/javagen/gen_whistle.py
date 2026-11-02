"""The whistle wheel's texts (1.5, docs/ORDENS.md; client/WhistleWheelScreen, entity/Whistle), merged into the lang
files by gen_resources.py. The six order names are the ones of the HUD preview Rodrigo approved (30/10/2026).
Messages that name the animals come in two forms: ".one" with the animal's name, ".many" with how many obeyed.
"""

ORDERS = ("follow", "sit", "wander", "attack", "gather", "passive")

# order: {lang: (name on the wheel, line under the wheel)}
NAMES = {
    "follow": {"pt_br": ("Seguir", "Todos te seguem"),
               "en_us": ("Follow", "All of them follow you"),
               "es_es": ("Seguir", "Todos te siguen")},
    "sit": {"pt_br": ("Esperar aqui", "Ficam parados onde estão"),
            "en_us": ("Wait here", "They stay where they are"),
            "es_es": ("Esperar aquí", "Se quedan donde están")},
    "wander": {"pt_br": ("Vagar por perto", "Andam perto de onde estão"),
               "en_us": ("Wander nearby", "They roam near where they are"),
               "es_es": ("Deambular cerca", "Deambulan cerca de donde están")},
    "attack": {"pt_br": ("Atacar meu alvo", "Vão atrás do que você mira"),
               "en_us": ("Attack my target", "They go for what you aim at"),
               "es_es": ("Atacar mi objetivo", "Van a por lo que apuntas")},
    "gather": {"pt_br": ("Juntar o bando", "Vêm até você agora"),
               "en_us": ("Gather", "They come to you now"),
               "es_es": ("Reunir la manada", "Vienen hacia ti ahora")},
    "passive": {"pt_br": ("Ficar passivo", "Não brigam; de novo, voltam ao neutro"),
                "en_us": ("Stay passive", "No fighting; again, back to neutral"),
                "es_es": ("Quedarse pasivo", "No pelean; otra vez, vuelven a neutral")},
}

# what the player reads in the action bar: (one, many)
DONE = {
    "follow": {"pt_br": ("%s te segue", "%s dinos te seguem"),
               "en_us": ("%s follows you", "%s dinos follow you"),
               "es_es": ("%s te sigue", "%s dinos te siguen")},
    "sit": {"pt_br": ("%s espera aqui", "%s dinos esperam aqui"),
            "en_us": ("%s waits here", "%s dinos wait here"),
            "es_es": ("%s espera aquí", "%s dinos esperan aquí")},
    "wander": {"pt_br": ("%s vaga por perto", "%s dinos vagam por perto"),
               "en_us": ("%s roams nearby", "%s dinos roam nearby"),
               "es_es": ("%s deambula cerca", "%s dinos deambulan cerca")},
    "attack": {"pt_br": ("%s vai atrás de %s", "%s dinos vão atrás de %s"),
               "en_us": ("%s goes for %s", "%s dinos go for %s"),
               "es_es": ("%s va a por %s", "%s dinos van a por %s")},
    "gather": {"pt_br": ("%s vem até você", "%s dinos vêm até você"),
               "en_us": ("%s is coming to you", "%s dinos are coming to you"),
               "es_es": ("%s viene hacia ti", "%s dinos vienen hacia ti")},
    "passive": {"pt_br": ("%s fica passivo", "%s dinos ficam passivos"),
                "en_us": ("%s is now passive", "%s dinos are now passive"),
                "es_es": ("%s se queda pasivo", "%s dinos se quedan pasivos")},
    "neutral": {"pt_br": ("%s volta ao modo neutro", "%s dinos voltam ao modo neutro"),
                "en_us": ("%s is back to neutral", "%s dinos are back to neutral"),
                "es_es": ("%s vuelve al modo neutral", "%s dinos vuelven al modo neutral")},
}

OTHER = {
    "pt_br": {
        "key.terrassic.whistle": "Apito (segure: roda de ordens)",
        "gui.terrassic.whistle.title": "Apito",
        "gui.terrassic.whistle.hearing": "%s dinos ouvem o apito",
        "gui.terrassic.whistle.hearing.one": "1 dino ouve o apito",
        "gui.terrassic.whistle.hearing.none": "Nenhum dino seu ouve o apito",
        "gui.terrassic.whistle.release": "Solte %s para dar a ordem",
        "message.terrassic.whistle.nobody": "Nenhum dino seu ouviu o apito",
        "message.terrassic.whistle.no_target": "Mire num bicho antes de apitar",
        "message.terrassic.whistle.protected": "%s está protegido: o PvP está desligado",
        "message.terrassic.whistle.attack.none": "Nenhum dino seu pode atacar %s",
    },
    "en_us": {
        "key.terrassic.whistle": "Whistle (hold: order wheel)",
        "gui.terrassic.whistle.title": "Whistle",
        "gui.terrassic.whistle.hearing": "%s dinos hear the whistle",
        "gui.terrassic.whistle.hearing.one": "1 dino hears the whistle",
        "gui.terrassic.whistle.hearing.none": "None of your dinos hears the whistle",
        "gui.terrassic.whistle.release": "Let go of %s to give the order",
        "message.terrassic.whistle.nobody": "None of your dinos heard the whistle",
        "message.terrassic.whistle.no_target": "Aim at a creature before you whistle",
        "message.terrassic.whistle.protected": "%s is protected: PvP is off",
        "message.terrassic.whistle.attack.none": "None of your dinos can attack %s",
    },
    "es_es": {
        "key.terrassic.whistle": "Silbato (mantén: rueda de órdenes)",
        "gui.terrassic.whistle.title": "Silbato",
        "gui.terrassic.whistle.hearing": "%s dinos oyen el silbato",
        "gui.terrassic.whistle.hearing.one": "1 dino oye el silbato",
        "gui.terrassic.whistle.hearing.none": "Ningún dino tuyo oye el silbato",
        "gui.terrassic.whistle.release": "Suelta %s para dar la orden",
        "message.terrassic.whistle.nobody": "Ningún dino tuyo oyó el silbato",
        "message.terrassic.whistle.no_target": "Apunta a una criatura antes de silbar",
        "message.terrassic.whistle.protected": "%s está protegido: el PvP está desactivado",
        "message.terrassic.whistle.attack.none": "Ningún dino tuyo puede atacar a %s",
    },
}


def build_lang():
    lang = {code: dict(keys) for code, keys in OTHER.items()}
    for order in ORDERS:
        for code, (name, tip) in NAMES[order].items():
            lang[code][f"gui.terrassic.whistle.{order}"] = name
            lang[code][f"gui.terrassic.whistle.{order}.tip"] = tip
    for order, texts in DONE.items():
        for code, (one, many) in texts.items():
            lang[code][f"message.terrassic.whistle.{order}.one"] = one
            lang[code][f"message.terrassic.whistle.{order}.many"] = many
    return lang
