# Vozes do Carcarodontossauro: o gigante que respira

Ninguém pôde ouvir no cliente de teste (o som fica mudo), então aqui vão os arquivos e os espectrogramas para
julgar de ouvido. Os `.ogg` desta pasta são cópias exatas dos que vão no mod
(`common/src/main/resources/assets/terrassic/sounds/voice/carcharodontosaurus/`); cada `<evento>.png` mostra as variações do
evento (0 a 5 kHz, tempo na horizontal, um tique por segundo; claro = forte). Lembrete: as vozes continuam
desligadas por padrão (`"vozes": false` em `config/terrassic-world.json`); para ouvir no jogo, ligue a chave.

Como foi feita: no mesmo estilo das outras 53 espécies (`tools/soundgen/arkstyle.py`: trechos de gravações de
domínio público/CC0 de `art/sounds/src`, desacelerados e misturados, com ar de garganta, grave, saturação e sala),
mas com um **perfil próprio** (antes ela era prima de outra espécie) e com funções próprias para os sons dos
comportamentos. Receita em `arkstyle.P["carcharodontosaurus"]` e `arkstyle.EXTRA`; eventos e legendas em
`tools/soundgen/recipes.py` (`OWN_SETS`, que também guarda a versão só sintetizada, usada se as gravações faltarem).
Refazer: `python3 tools/soundgen/build.py carcharodontosaurus` e `python3 tools/soundgen/voice_sheet.py carcharodontosaurus`.

Antes: alce + urso + jacaré com o corpo do T. rex (primo dele e do Giganotossauro).

**Caráter:** um gigante que mais respira do que ruge: quase sem grito (o alce entra baixinho, 0,34x), muito ar de
garganta e o chiado de jacaré por cima de rosnado de urso e bramido de jacaré, aspereza muito lenta (16/s, um rascar
que se conta) e o grave mais fundo dos quatro. Frases longas e espaçadas. **Na tocaia fica calado**: o ambiente não
toca enquanto ele espera (`Carcharodontosaurine.playAmbientSound`), e a arrancada é silenciosa.

| evento | quando toca | como soa |
|---|---|---|
| ambient (3) | chamado, fora da tocaia | respiração que rasca, 3,7 a 3,9 s |
| threat (2) | `gape_hiss` sobre a presa, rugido no alvo | sopro de boca aberta sobre o rascar grave, 7 s |
| **tear_hiss** (2) | o golpe `tear` acerta (o que faz sangrar) | silvo pelos dentes, a carne rasgando e um rascar curto, 1,5 s |
| hurt (2), death (1) | ferido, morte | tosse grave cheia de ar; rascar que vai parando |
| step (3) | passos | pisada de terópode de tamanho 1,0 |

## Medidas de cada som

Faixa forte = a banda mais forte abaixo de 400 Hz; brilho = centroide do espectro; aspereza = quanto o volume tremula entre 15 e 80 Hz (0,2 liso, 0,45 áspero).

| som | duração | faixa forte (Hz) | brilho (Hz) | energia < 250 Hz | aspereza |
|---|---|---|---|---|---|
| ambient_1 | 3.8 s | 151 | 258 | 77% | 0.40 |
| ambient_2 | 3.7 s | 86 | 247 | 74% | 0.40 |
| ambient_3 | 3.9 s | 129 | 241 | 79% | 0.34 |
| death_1 | 5.5 s | 65 | 342 | 67% | 0.41 |
| hurt_1 | 1.8 s | 194 | 523 | 41% | 0.31 |
| hurt_2 | 1.8 s | 301 | 743 | 11% | 0.30 |
| step_1 | 1.2 s | 108 | 250 | 69% | 0.47 |
| step_2 | 1.3 s | 108 | 204 | 76% | 0.44 |
| step_3 | 1.3 s | 65 | 198 | 78% | 0.48 |
| tear_hiss_1 | 1.6 s | 86 | 827 | 41% | 0.32 |
| tear_hiss_2 | 1.5 s | 86 | 1185 | 33% | 0.26 |
| threat_1 | 7.4 s | 86 | 427 | 62% | 0.38 |
| threat_2 | 7.1 s | 86 | 388 | 64% | 0.36 |

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

Tabelas completas do T. rex, do Carnotauro e do Giganotossauro: `python3 tools/soundgen/voice_sheet.py carcharodontosaurus --compare=tyrannosaurus,carnotaurus,giganotosaurus`.
