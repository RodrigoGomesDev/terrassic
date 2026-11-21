# Vozes do Albertossauro: o corredor que pia

Ninguém pôde ouvir no cliente de teste (o som fica mudo), então aqui vão os arquivos e os espectrogramas para
julgar de ouvido. Os `.ogg` desta pasta são cópias exatas dos que vão no mod
(`common/src/main/resources/assets/terrassic/sounds/voice/albertosaurus/`); cada `<evento>.png` mostra as variações do
evento (0 a 5 kHz, tempo na horizontal, um tique por segundo; claro = forte). Lembrete: as vozes continuam
desligadas por padrão (`"vozes": false` em `config/terrassic-world.json`); para ouvir no jogo, ligue a chave.

Como foi feita: no mesmo estilo das outras 53 espécies (`tools/soundgen/arkstyle.py`: trechos de gravações de
domínio público/CC0 de `art/sounds/src`, desacelerados e misturados, com ar de garganta, grave, saturação e sala),
mas com um **perfil próprio** (antes ela era prima de outra espécie) e com funções próprias para os sons dos
comportamentos. Receita em `arkstyle.P["albertosaurus"]` e `arkstyle.EXTRA`; eventos e legendas em
`tools/soundgen/recipes.py` (`OWN_SETS`, que também guarda a versão só sintetizada, usada se as gravações faltarem).
Refazer: `python3 tools/soundgen/build.py albertosaurus` e `python3 tools/soundgen/voice_sheet.py albertosaurus`.

Antes: grou + alce + urso com o corpo do T. rex; o chamado do bando tocava a voz do ambiente.

**Caráter:** o mais agudo e o mais leve dos quatro: pios ocos de grou e alce pouco desacelerados (0,62x e 0,58x, o
T. rex usa 0,42x), um pouco de urso e de jacaré por baixo para não perder o tamanho, aspereza fina e rápida (46/s) e
sala grande (o bando se chama de longe). Ritmo rápido, frases em pios.

| evento | quando toca | como soa |
|---|---|---|
| ambient (3) | chamado de vez em quando | pio oco com um pouco de grave, 2,4 s |
| threat (2) | rugido no alvo, avisos | pio que vira silvo, 3,8 s |
| **call_pack** (2) | `call_pack`: o adulto que pega um alvo chama o bando (substitui o rugido nesse momento) | três pios que SOBEM (0,50/0,56/0,63x), ouvidos a 96 blocos |
| **answer** (2) | `answer`: cada um do bando responde | dois pios curtos que DESCEM, ouvidos a 64 blocos |
| **pant** (2) | `pant`: desistiu da perseguição longa | ar saindo e entrando ~2,3 vezes por segundo, um fio de voz na saída; baixo e perto (16 blocos) |
| hurt (2), death (1) | ferido, morte | pio rachado; pio que cai num sopro |
| step (3) | passos | pisada de terópode de tamanho 0,7 |

Atenção de ouvido: nos pios do chamado a reverberação deixa um tom fino perto de 1,2 kHz soando depois do último pio
(a faixa clara contínua no espectrograma); se parecer metálico, diminuir `room` em `arkstyle._hoots`.

## Medidas de cada som

Faixa forte = a banda mais forte abaixo de 400 Hz; brilho = centroide do espectro; aspereza = quanto o volume tremula entre 15 e 80 Hz (0,2 liso, 0,45 áspero).

| som | duração | faixa forte (Hz) | brilho (Hz) | energia < 250 Hz | aspereza |
|---|---|---|---|---|---|
| ambient_1 | 2.4 s | 65 | 427 | 18% | 0.34 |
| ambient_2 | 2.5 s | 65 | 449 | 26% | 0.35 |
| ambient_3 | 2.4 s | 65 | 491 | 22% | 0.30 |
| answer_1 | 2.8 s | 388 | 742 | 1% | 0.29 |
| answer_2 | 2.6 s | 388 | 845 | 1% | 0.24 |
| call_pack_1 | 3.7 s | 345 | 780 | 1% | 0.29 |
| call_pack_2 | 3.5 s | 345 | 838 | 0% | 0.31 |
| death_1 | 3.9 s | 65 | 712 | 10% | 0.34 |
| hurt_1 | 1.5 s | 65 | 907 | 2% | 0.30 |
| hurt_2 | 1.6 s | 65 | 953 | 2% | 0.29 |
| pant_1 | 2.6 s | 366 | 1077 | 0% | 0.25 |
| pant_2 | 2.3 s | 345 | 1055 | 1% | 0.29 |
| step_1 | 0.9 s | 65 | 257 | 80% | 0.40 |
| step_2 | 1.0 s | 43 | 283 | 68% | 0.39 |
| step_3 | 1.0 s | 108 | 311 | 68% | 0.43 |
| threat_1 | 4.7 s | 65 | 687 | 16% | 0.34 |
| threat_2 | 4.6 s | 65 | 697 | 16% | 0.37 |

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

Tabelas completas do T. rex, do Carnotauro e do Giganotossauro: `python3 tools/soundgen/voice_sheet.py albertosaurus --compare=tyrannosaurus,carnotaurus,giganotosaurus`.
