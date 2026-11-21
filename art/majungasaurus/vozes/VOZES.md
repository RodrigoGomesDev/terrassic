# Vozes do Majungassauro: o pavio curto que bufa

Ninguém pôde ouvir no cliente de teste (o som fica mudo), então aqui vão os arquivos e os espectrogramas para
julgar de ouvido. Os `.ogg` desta pasta são cópias exatas dos que vão no mod
(`common/src/main/resources/assets/terrassic/sounds/voice/majungasaurus/`); cada `<evento>.png` mostra as variações do
evento (0 a 5 kHz, tempo na horizontal, um tique por segundo; claro = forte). Lembrete: as vozes continuam
desligadas por padrão (`"vozes": false` em `config/terrassic-world.json`); para ouvir no jogo, ligue a chave.

Como foi feita: no mesmo estilo das outras 53 espécies (`tools/soundgen/arkstyle.py`: trechos de gravações de
domínio público/CC0 de `art/sounds/src`, desacelerados e misturados, com ar de garganta, grave, saturação e sala),
mas com um **perfil próprio** (antes ela era prima de outra espécie) e com funções próprias para os sons dos
comportamentos. Receita em `arkstyle.P["majungasaurus"]` e `arkstyle.EXTRA`; eventos e legendas em
`tools/soundgen/recipes.py` (`OWN_SETS`, que também guarda a versão só sintetizada, usada se as gravações faltarem).
Refazer: `python3 tools/soundgen/build.py majungasaurus` e `python3 tools/soundgen/voice_sheet.py majungasaurus`.

Antes: o mesmo perfil do Carnotauro (pelicano + urso + jacaré + bisão), com a ameaça tocando no domo e no bebedouro.

**Caráter:** curto e nasal, em rajadas: latido de bisão e rosnado alto de aviso de urso, uma garça desacelerada como
um grito nasal curto, corpo curto (frases de 1,7 s no ambiente, o Carnotauro tem 2,4 s). Mais grave que o Carnotauro
(59 a 71% abaixo de 250 Hz contra 28 a 42%).

| evento | quando toca | como soa |
|---|---|---|
| ambient (3) | chamado de vez em quando | bufos e grunhidos nasais em rajada, 1,7 s |
| threat (2) | rugido no alvo | rosnado nasal, 3,3 s |
| **temper** (2) | `dome_display` ao jogador a 8 blocos, `waterhole_threat` no bebedouro, rosnado sobre a carcaça | rufar de 6 a 7 grunhidos de garganta que acelera e cresce, e um bufo no fim |
| hurt (2), death (1) | ferido, morte | grunhido nasal curto; três grunhidos que caem |
| step (3) | passos | pisada de terópode de tamanho 0,55 |

## Medidas de cada som

Faixa forte = a banda mais forte abaixo de 400 Hz; brilho = centroide do espectro; aspereza = quanto o volume tremula entre 15 e 80 Hz (0,2 liso, 0,45 áspero).

| som | duração | faixa forte (Hz) | brilho (Hz) | energia < 250 Hz | aspereza |
|---|---|---|---|---|---|
| ambient_1 | 1.8 s | 172 | 356 | 71% | 0.34 |
| ambient_2 | 1.7 s | 65 | 440 | 59% | 0.25 |
| ambient_3 | 1.8 s | 86 | 498 | 67% | 0.36 |
| death_1 | 3.1 s | 172 | 594 | 51% | 0.33 |
| hurt_1 | 1.1 s | 280 | 569 | 33% | 0.33 |
| hurt_2 | 1.2 s | 280 | 672 | 26% | 0.36 |
| step_1 | 0.8 s | 86 | 280 | 75% | 0.41 |
| step_2 | 0.8 s | 65 | 295 | 69% | 0.42 |
| step_3 | 0.9 s | 108 | 284 | 73% | 0.40 |
| temper_1 | 2.9 s | 258 | 329 | 52% | 0.31 |
| temper_2 | 2.7 s | 258 | 305 | 59% | 0.31 |
| threat_1 | 3.3 s | 194 | 528 | 50% | 0.28 |
| threat_2 | 3.4 s | 194 | 516 | 51% | 0.33 |

## Comparação com os parentes e com os outros três

| espécie | brilho médio do ambiente (Hz) | grave < 250 Hz (ambiente) | brilho médio da ameaça (Hz) | grave < 250 Hz (ameaça) |
|---|---|---|---|---|
| daspletosaurus | 203 | 86% | 287 | 76% |
| albertosaurus | 456 | 22% | 692 | 16% |
| carcharodontosaurus | 249 | 77% | 408 | 63% |
| majungasaurus | 431 | 66% | 522 | 50% |
| tyrannosaurus | 402 | 55% | 416 | 54% |
| carnotaurus | 462 | 35% | 614 | 36% |
| giganotosaurus | 407 | 56% | 511 | 38% |

Tabelas completas do T. rex, do Carnotauro e do Giganotossauro: `python3 tools/soundgen/voice_sheet.py majungasaurus --compare=tyrannosaurus,carnotaurus,giganotosaurus`.
