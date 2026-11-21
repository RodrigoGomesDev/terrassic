# Vozes do Daspletossauro: o tirano que range

Ninguém pôde ouvir no cliente de teste (o som fica mudo), então aqui vão os arquivos e os espectrogramas para
julgar de ouvido. Os `.ogg` desta pasta são cópias exatas dos que vão no mod
(`common/src/main/resources/assets/terrassic/sounds/voice/daspletosaurus/`); cada `<evento>.png` mostra as variações do
evento (0 a 5 kHz, tempo na horizontal, um tique por segundo; claro = forte). Lembrete: as vozes continuam
desligadas por padrão (`"vozes": false` em `config/terrassic-world.json`); para ouvir no jogo, ligue a chave.

Como foi feita: no mesmo estilo das outras 53 espécies (`tools/soundgen/arkstyle.py`: trechos de gravações de
domínio público/CC0 de `art/sounds/src`, desacelerados e misturados, com ar de garganta, grave, saturação e sala),
mas com um **perfil próprio** (antes ela era prima de outra espécie) e com funções próprias para os sons dos
comportamentos. Receita em `arkstyle.P["daspletosaurus"]` e `arkstyle.EXTRA`; eventos e legendas em
`tools/soundgen/recipes.py` (`OWN_SETS`, que também guarda a versão só sintetizada, usada se as gravações faltarem).
Refazer: `python3 tools/soundgen/build.py daspletosaurus` e `python3 tools/soundgen/voice_sheet.py daspletosaurus`.

Antes: o perfil era o do T. rex quase igual (grito de alce desacelerado + rugido de urso + jacaré + bisão).

**Caráter:** grave, de boca quase fechada, frases curtas que rangem. Sem o grito de alce do T. rex: no lugar do grito
entra o bramido de bisão desacelerado (0,55x), por cima do rosnado de aviso de urso e de um grunhido de bisão; a
aspereza é lenta (22 por segundo, um "rangido" de garganta, o T. rex tem 38) e a saturação é a mais alta dos quatro.
É o mais escuro: 80 a 94% da energia abaixo de 250 Hz no ambiente (T. rex: 52 a 60%).

| evento | quando toca | como soa |
|---|---|---|
| ambient (3) | chamado de vez em quando | rangido grave e curto, 2,8 a 3 s |
| threat (2) | rugido no alvo, `jaw_test`, avisos | o rangido abrindo em bramido, 5,6 s |
| **steal_roar** (2) | `CarcassStealGoal`: ruge para quem está comendo e toma a carcaça | a ameaça maior e mais forte (corpo 1,3x, mais bramido, mais saturação), 7 s, ouvida a 96 blocos |
| **carcass_growl** (2) | agachado sobre a carcaça, rosna para outro carnívoro que chega | rosnado longo e baixo de boca fechada, só urso e jacaré, filtrado abaixo de 3,2 kHz, e o estalo da mandíbula no fim |
| hurt (2), death (1) | ferido, morte | latido grave e rouco; gemido que cai |
| step (3) | passos | pisada de terópode de tamanho 0,85 (a mesma regra dos outros) |

## Medidas de cada som

Faixa forte = a banda mais forte abaixo de 400 Hz; brilho = centroide do espectro; aspereza = quanto o volume tremula entre 15 e 80 Hz (0,2 liso, 0,45 áspero).

| som | duração | faixa forte (Hz) | brilho (Hz) | energia < 250 Hz | aspereza |
|---|---|---|---|---|---|
| ambient_1 | 2.8 s | 172 | 286 | 79% | 0.39 |
| ambient_2 | 3.0 s | 65 | 202 | 86% | 0.30 |
| ambient_3 | 2.9 s | 65 | 121 | 94% | 0.22 |
| carcass_growl_1 | 3.4 s | 151 | 213 | 85% | 0.38 |
| carcass_growl_2 | 3.4 s | 65 | 153 | 91% | 0.30 |
| death_1 | 4.6 s | 108 | 323 | 71% | 0.40 |
| hurt_1 | 1.6 s | 194 | 430 | 62% | 0.37 |
| hurt_2 | 1.7 s | 86 | 260 | 82% | 0.30 |
| steal_roar_1 | 7.2 s | 65 | 234 | 83% | 0.36 |
| steal_roar_2 | 7.1 s | 65 | 224 | 83% | 0.32 |
| step_1 | 1.1 s | 65 | 230 | 79% | 0.42 |
| step_2 | 1.1 s | 43 | 220 | 78% | 0.45 |
| step_3 | 1.2 s | 108 | 239 | 79% | 0.46 |
| threat_1 | 5.6 s | 172 | 304 | 74% | 0.38 |
| threat_2 | 5.6 s | 65 | 270 | 78% | 0.37 |

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

Tabelas completas do T. rex, do Carnotauro e do Giganotossauro: `python3 tools/soundgen/voice_sheet.py daspletosaurus --compare=tyrannosaurus,carnotaurus,giganotosaurus`.
