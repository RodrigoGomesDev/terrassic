"""Gera o bestiário completo (docs/bestiario/) a partir de roster_data.py.

- Domar, montaria, nicho e uso saem de regras simples (tamanho, dieta, ambiente e grupo).
- As criaturas que já têm versão no plano (docs/ROSTER.md) usam os valores de lá e mostram a versão.
Rode:  python3 gen_roster.py
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from roster_data import DATA, ERAS  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
OUT = os.path.join(ROOT, "docs", "bestiario")
ROSTER = os.path.join(ROOT, "docs", "ROSTER.md")

# código: (rótulo, ambiente padrão)  T terrestre, V voador, A aquático, F anfíbio
GROUPS = {
    "TIR": ("Tiranossauro", "T"), "ABE": ("Ceratossauro/abelissauro", "T"), "CAR": ("Carnossauro", "T"),
    "ESP": ("Espinossauro", "F"), "MEG": ("Megalossauro", "T"), "TER": ("Terópode", "T"),
    "CEL": ("Celurossauro pequeno", "T"), "RAP": ("Raptor", "T"), "TRO": ("Troodontídeo", "T"),
    "ORN": ("Ornitomimossauro", "T"), "OVI": ("Oviraptorossauro", "T"), "TZN": ("Terizinossauro", "T"),
    "ALV": ("Alvarezssauro", "T"), "PAR": ("Paraviano (planador)", "V"), "AVE": ("Ave", "T"),
    "AVV": ("Ave", "V"), "SAU": ("Saurópode", "T"), "TIT": ("Titanossauro", "T"),
    "SPM": ("Sauropodomorfo", "T"), "DIN": ("Dinossauro primitivo", "T"), "CER": ("Ceratopsiano", "T"),
    "ANQ": ("Anquilossauro", "T"), "NOD": ("Nodossauro", "T"), "EST": ("Estegossauro", "T"),
    "HAD": ("Hadrossauro", "T"), "IGU": ("Iguanodonte", "T"), "ORP": ("Ornitópode", "T"),
    "PAQ": ("Paquicefalossauro", "T"), "HET": ("Heterodontossauro", "T"), "PTE": ("Pterossauro", "V"),
    "MOS": ("Mosassauro", "A"), "PLE": ("Plesiossauro", "A"), "PLI": ("Pliossauro", "A"),
    "ICT": ("Ictiossauro", "A"), "SAP": ("Notossauro/placodonte", "A"), "TAL": ("Talatossauro", "A"),
    "CRO": ("Crocodiliforme", "F"), "CRM": ("Crocodilo marinho", "A"), "CRT": ("Crocodiliforme terrestre", "T"),
    "PSE": ("Pseudossúquio", "T"), "FIT": ("Fitossauro", "F"), "ARC": ("Arcossauriforme", "T"),
    "RIN": ("Rincossauro", "T"), "REP": ("Réptil", "T"), "LAG": ("Lagarto/serpente", "T"),
    "ESF": ("Esfenodonte", "T"), "TAR": ("Tartaruga", "F"), "TAM": ("Tartaruga marinha", "A"),
    "COR": ("Coristodero", "F"), "ANF": ("Anfíbio", "F"), "PEI": ("Peixe", "A"), "TUB": ("Tubarão/raia", "A"),
    "INV": ("Invertebrado", "A"), "INS": ("Inseto", "V"), "MAM": ("Mamífero", "T"),
    "DIC": ("Dicinodonte", "T"), "CIN": ("Cinodonte", "T"), "MMA": ("Mamífero marinho", "A"),
    "PRB": ("Proboscídeo", "T"), "XEN": ("Xenartro", "T"), "UNG": ("Ungulado", "T"), "FEL": ("Felino", "T"),
    "CAN": ("Canídeo/mustelídeo", "T"), "URS": ("Urso", "T"), "HIE": ("Hiena", "T"), "MAR": ("Marsupial", "T"),
    "PRI": ("Primata", "T"), "ROE": ("Roedor/pequeno mamífero", "T"),
}
MAMMALS = {"MAM", "DIC", "CIN", "MMA", "PRB", "XEN", "UNG", "FEL", "CAN", "URS", "HIE", "MAR", "PRI", "ROE"}
FISH = {"PEI", "TUB"}
# Grupos com prova de que pariam filhotes vivos (sem ovo): filhote recém-nascido em vez de ovo.
LIVE_BIRTH = MAMMALS | {"MOS", "PLE", "PLI", "ICT", "SAP"}
# Quadrúpedes pesados: aguentam um cavaleiro com menos comprimento que um bípede.
BULKY = {"CER", "ANQ", "NOD", "EST", "SAU", "TIT", "DIC", "PSE", "TAR", "TAM", "HAD", "IGU"}
BUGS = {"INV", "INS"}
DIETS = {"H": "Herbívoro", "C": "Carnívoro", "P": "Piscívoro", "O": "Onívoro", "I": "Insetívoro", "F": "Filtrador"}
EMOJI = {"T": "🦖", "V": "🪽", "A": "🌊", "F": "🐊"}
VERSION_HEADERS = [  # (regex do título no ROSTER.md, versão)
    (r"^## (v\d+\.\d+)", None), (r"^# Capítulo 2", "v2.0"), (r"^# Capítulo 3", "v3.0"),
    (r"^# Capítulo 4", "v4.0"), (r"^# Epílogo", "v5.0"), (r"^# Anomalias", "com a era"),
]


def key(name):
    return re.sub(r"\*", "", name).split(" (")[0].strip().lower()


def num(x):
    return f"{x:g}".replace(".", ",")


def read_plan():
    """Lê as tabelas do ROSTER.md: nome -> colunas da primeira vez que a criatura aparece."""
    plan, version, header = {}, None, None
    for line in open(ROSTER, encoding="utf-8"):
        for rx, v in VERSION_HEADERS:
            m = re.match(rx, line)
            if m:
                version = v or m.group(1)
                if "✅" in line:
                    version += " ✅"
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] in ("Espécie", "Versão", "Coluna", "Sistema"):
            header = cells
            continue
        if header is None or header[0] != "Espécie" or version is None:
            continue
        k = key(cells[0])
        if k not in plan:
            plan[k] = dict(zip(header, cells), version=version)
    return plan


def parse(era_id):
    sections, cur = [], None
    for line in DATA[era_id].strip().splitlines():
        if not line.strip():
            continue
        if line.startswith("#"):
            cur = (line.lstrip("# ").strip(), [])
            sections.append(cur)
            continue
        if cur is None:
            cur = ("", [])
            sections.append(cur)
        f = (line.split("|") + ["", ""])[:6]
        name, grp, diet, size, marks, note = [x.strip() for x in f]
        height = size.endswith("a")
        val = float(size.rstrip("a"))
        tokens = marks.split()
        hab = next((t[1] for t in tokens if t.startswith("@")), GROUPS[grp][1])
        cur[1].append(dict(name=name, grp=grp, diet=diet, size=val, height=height, hab=hab,
                           live="VIVO" in tokens or grp in LIVE_BIRTH, note=note))
    return sections


def derive(c):
    grp, diet, hab, val = c["grp"], c["diet"], c["hab"], c["size"]
    mammal = grp in MAMMALS
    eff = val * (1.0 if grp == "AVE" else 1.5) if c["height"] else val
    baby = "Filhote" if c["live"] else "Ovo"
    # domar
    if grp in BUGS:
        tame = "—"
    elif grp in FISH:
        tame = "Comida" if diet == "F" and eff >= 10 else "Nocaute" if diet == "C" and eff >= 6 else "—"
    elif eff < 0.25:
        tame = "—"
    elif diet in "HOFI":
        # como no ARK, os gigantes não aceitam comida da mão: precisam de nocaute
        tame = "Nocaute" if eff >= 25 else "Comida"
    elif diet == "P":
        tame = "Comida (peixe)" if eff < 2 else baby if eff < 6 else "Nocaute"
    else:
        big = eff * (3 if mammal else 1)
        tame = "Comida" if big < 1.5 else baby if big < 6 else "Nocaute"
    # montaria
    if tame == "—":
        mount = "—"
    elif hab == "V":
        # só voadores grandes aguentam o jogador (o Pteranodon de 7 m é o primeiro)
        mount = "🪑" if eff >= 9 else "✅" if eff >= 5 else "🦜" if eff <= 1.5 else "—"
    elif hab == "A":
        mount = "🪑" if eff >= 12 else "✅" if eff >= 3 else "—"
    elif c["height"]:
        mount = "✅" if val >= 1.4 else "—"
    else:
        # precisa ter uns 300 kg para carregar uma pessoa: bípedes a partir de ~4,5 m, quadrúpedes pesados ~3 m
        ride = 1.8 if mammal else 3 if grp in BULKY else 4.5
        mount = "🪑" if eff >= 18 else "✅" if eff >= ride else "🦜" if eff <= 1.2 else "—"
    # nicho
    scale = eff * (2.5 if mammal and hab != "A" else 1)
    if grp in BUGS:
        niche = "Fauna marinha" if hab == "A" else "Fauna pequena"
    elif diet == "F":
        niche = "Filtrador gigante" if eff >= 10 else "Filtrador"
    elif diet == "C":
        niche = ("Predador de topo" if scale >= 10 else "Predador grande" if scale >= 5
                 else "Predador médio" if scale >= 1.5 else "Caçador pequeno")
    elif diet == "P":
        niche = "Pescador grande" if eff >= 5 else "Pescador"
    elif diet == "I":
        niche = "Comedor de insetos"
    elif diet == "O":
        niche = "Onívoro grande" if scale >= 5 else "Onívoro médio" if scale >= 1.5 else "Onívoro pequeno"
    else:
        niche = ("Gigante" if scale >= 18 else "Herbívoro grande" if scale >= 6
                 else "Herbívoro médio" if scale >= 2 else "Herbívoro pequeno")
    # comportamento do animal selvagem (como no ARK: pacífico, arisco, defensivo, territorial, agressivo)
    if grp in BUGS or (grp in FISH and eff < 2) or diet == "F":
        mood = "Pacífico"
    elif diet in "CP":
        mood = "Agressivo" if scale >= 3 else "Territorial" if scale >= 1.5 else "Arisco"
    elif grp in {"ANQ", "NOD", "CER", "EST", "PAQ", "TZN", "PRB", "URS"} or scale >= 10:
        mood = "Territorial"
    elif scale >= 3:
        mood = "Defensivo"
    else:
        mood = "Arisco"
    # uso
    if mount == "🪑":
        use = "Plataforma para construir em cima"
    elif mount == "✅":
        use = ("Montaria voadora" if hab == "V" else "Montaria aquática" if hab == "A"
               else "Montaria de combate" if diet in "CP" else "Montaria de carga" if scale >= 8
               else "Montaria rápida")
    elif mount == "🦜":
        use = "Vai no ombro (bônus)"
    elif tame != "—":
        use = ("Guarda da base" if diet in "CP" else "Controla pragas, acha isca" if diet == "I"
               else "Coleta (frutas, sementes, fibra)")
    elif grp in BUGS:
        use = "Recurso: conchas, fósseis e isca"
    elif eff < 0.25:
        use = "Vida pequena do bioma"
    else:
        use = "Recurso: carne, couro, osso e amostras"
    if c["note"]:
        use = f"{use}; {c['note']}"
    return dict(tame=tame, mount=mount, niche=niche, mood=mood, use=use)


def size_txt(c):
    unit = " alt." if c["height"] else " env." if c["hab"] == "V" else ""
    return f"{num(c['size'])} m{unit}"


def build():
    plan = read_plan()
    os.makedirs(OUT, exist_ok=True)
    all_json, stats, used = {}, [], set()
    era_list = list(ERAS) + [("anomalias", "Anomalias da Fenda", "Em qualquer era", "fora das 5 eras")]
    for i, (era_id, title, chapter, age) in enumerate(era_list, 1):
        sections = parse(era_id)
        rows, n = [], 0
        st = dict(total=0, tame=0, mount=0, plat=0, shoulder=0, fly=0, sea=0, mammal=0, plan=0)
        out = [f"# {title}", "", f"**{chapter}** · {age}", "",
               "Legenda e regras em [README.md](README.md). Negrito = já tem versão no plano (`docs/ROSTER.md`).", ""]
        for sec_title, creatures in sections:
            if sec_title:
                out += [f"## {sec_title}", ""]
            out += ["| # | Criatura | Grupo | Tipo | Dieta | Tamanho | Nicho | Comportamento | Domar | Montaria | Uso no jogo | Versão |",
                    "|---|---|---|---|---|---|---|---|---|---|---|---|"]
            for c in creatures:
                n += 1
                d = derive(c)
                p = plan.get(key(c["name"]))
                version = ""
                if p:
                    used.add(key(c["name"]))
                    version = p["version"]
                    d["tame"] = p.get("Domar", d["tame"])
                    d["mount"] = p.get("Montaria", d["mount"])
                    d["use"] = p.get("Utilidade", p.get("Utilidade hoje / planejada", d["use"]))
                    st["plan"] += 1
                emoji = "🐾" if c["grp"] in MAMMALS and c["hab"] == "T" else EMOJI[c["hab"]]
                name = f"**{c['name']}**" if p else c["name"]
                out.append(f"| {n} | {name} | {GROUPS[c['grp']][0]} | {emoji} | {DIETS[c['diet']]} | {size_txt(c)} "
                           f"| {d['niche']} | {d['mood']} | {d['tame']} | {d['mount']} | {d['use']} | {version} |")
                st["total"] += 1
                st["tame"] += d["tame"] != "—"
                st["mount"] += d["mount"].startswith(("✅", "🪑"))
                st["plat"] += d["mount"].startswith("🪑")
                st["shoulder"] += d["mount"].startswith("🦜")
                st["fly"] += c["hab"] == "V"
                st["sea"] += c["hab"] == "A"
                st["mammal"] += c["grp"] in MAMMALS
                rows.append(dict(c, **d, era=era_id, group=GROUPS[c["grp"]][0], version=version))
            out.append("")
        fname = f"{i:02d}_{era_id}.md"
        with open(os.path.join(OUT, fname), "w", encoding="utf-8") as fh:
            fh.write("\n".join(out))
        all_json[era_id] = rows
        stats.append((title, chapter, fname, st))
    missing = sorted(set(plan) - used)
    with open(os.path.join(OUT, "bestiario.json"), "w", encoding="utf-8") as fh:
        json.dump(all_json, fh, ensure_ascii=False, indent=1)
    write_index(stats, missing)
    for title, _, _, st in stats:
        print(f"{title}: {st['total']}")
    if missing:
        print("No ROSTER.md mas fora do bestiário:", ", ".join(missing))


def write_index(stats, missing):
    total = sum(st["total"] for *_, st in stats)
    lines = [
        "# Bestiário do Terrassic",
        "",
        f"Todas as criaturas planejadas para o mod: **{total}** no total, de 200 a mais de 300 por era. Não são só "
        "dinossauros: entram pterossauros, répteis marinhos, crocodilos antigos, anfíbios, peixes, insetos e os "
        "mamíferos e aves de cada época, para cada era ter um ecossistema completo no estilo ARK.",
        "",
        "Este bestiário é a lista do que **pode** entrar. O plano de versões (o que entra em cada versão e com "
        "qual mecânica) continua em [`docs/ROSTER.md`](../ROSTER.md); as criaturas de lá aparecem aqui em negrito, "
        "com a versão. As outras entram aos poucos, era por era.",
        "",
        "| Era | Capítulo | Criaturas | Domáveis | Montáveis | Plataforma | Ombro | Voadoras | Aquáticas "
        "| Mamíferos | No plano |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for title, chapter, fname, st in stats:
        lines.append(f"| [{title}]({fname}) | {chapter} | {st['total']} | {st['tame']} | {st['mount']} | {st['plat']} "
                     f"| {st['shoulder']} | {st['fly']} | {st['sea']} | {st['mammal']} | {st['plan']} |")
    lines += [
        "",
        "## Legenda",
        "",
        "| Coluna | Significado |",
        "|---|---|",
        "| **Tipo** | 🦖 terrestre · 🐾 mamífero terrestre · 🪽 voador ou planador · 🌊 aquático · 🐊 anfíbio (anda e nada) |",
        "| **Nicho** | O lugar da criatura na cadeia alimentar da era (define spawn, bando e quem caça quem) |",
        "| **Domar** | **Comida**: alimentar até domesticar · **Ovo**: só criado desde o ovo · **Filhote**: animal que "
        "paria filhotes vivos (mamíferos, mosassauros, plesiossauros, ictiossauros), criado desde recém-nascido · **Nocaute**: derrubar com armas de narcótico e alimentar enquanto dorme · **—**: não domesticável |",
        "| **Montaria** | ✅ montável · 🪑 sela de plataforma (dá para construir em cima) · 🦜 vai no ombro · — não montável |",
        "| **Tamanho** | Comprimento do corpo, envergadura (env.) nos voadores ou altura (alt.). 1 bloco = 1 m |",
        "| **Comportamento** | Como o animal selvagem reage ao jogador, no estilo ARK: **Pacífico** ignora · **Arisco** "
        "foge · **Defensivo** só revida · **Territorial** ataca quem chega perto · **Agressivo** caça o jogador |",
        "| **Versão** | Versão do plano em `docs/ROSTER.md`; vazio = ainda sem versão |",
        "",
        "## Regras",
        "",
        "- **Tamanhos:** topo das estimativas publicadas para adultos, 1 bloco = 1 m (regra aprovada pelo Rodrigo). "
        "Aqui são valores de planejamento; quando a espécie for implementada, o tamanho final e a fonte vão para "
        "`docs/TAMANHOS.md`.",
        "- **Domar e montaria (ARK + vida real)** saem de regras automáticas para as criaturas sem versão. Herbívoros "
        "e onívoros se domam com comida, menos os gigantes (25 m ou mais), que precisam de nocaute como no ARK. "
        "Carnívoros pequenos se criam do ovo (ou do filhote, nos que pariam filhotes vivos) e os grandes, com nocaute. "
        "Peixes, invertebrados e bichos minúsculos não se domam. Para montar, o animal precisa aguentar uma pessoa "
        "(uns 300 kg): bípedes a partir de ~4,5 m, quadrúpedes pesados a partir de ~3 m, mamíferos a partir de ~1,8 m e "
        "voadores a partir de 5 m de envergadura. Gigantes (18 m ou mais) ganham sela de plataforma; criaturas "
        "pequenas vão no ombro. Quando uma criatura entrar no plano, os valores do `ROSTER.md` passam a valer.",
        "- **Mundial:** as espécies vêm do mundo todo, na proporção dos fósseis conhecidos (América do Norte, Ásia, "
        "Europa, África, América do Sul, Austrália e Antártida), sem foco em um país.",
        "- **Uma criatura, uma era:** cada gênero aparece numa era só, a que melhor representa a espécie. "
        "Criaturas de fora das 5 eras (Megalodon, Dunkleosteus) ficam nas Anomalias da Fenda.",
        "- **Correção científica:** o Argentavis está no Epílogo pelo plano, mas viveu no Mioceno (6 milhões de "
        "anos), não na Era do Gelo. No jogo ele fica como vazamento da Fenda.",
        "- **Pessoas:** nenhuma espécie humana (Neandertal etc.) entra; a única pessoa do mod é a Katarina.",
        "",
        "## Como editar",
        "",
        "Os dados ficam em `tools/roster/roster_data.py`, uma linha por criatura. Depois de editar, rode "
        "`python3 tools/roster/gen_roster.py`: ele reescreve esta pasta e o `bestiario.json` (para as ferramentas). "
        "Não edite os .md desta pasta à mão.",
    ]
    if missing:
        lines += ["", "Atenção: estão no ROSTER.md mas não no bestiário: " + ", ".join(missing) + "."]
    with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    build()
