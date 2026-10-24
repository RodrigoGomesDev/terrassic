# Bestiário do Terrassic

Todas as criaturas planejadas para o mod: **1203** no total, de 200 a mais de 300 por era. Não são só dinossauros: entram pterossauros, répteis marinhos, crocodilos antigos, anfíbios, peixes, insetos e os mamíferos e aves de cada época, para cada era ter um ecossistema completo no estilo ARK.

Este bestiário é a lista do que **pode** entrar. O plano de versões (o que entra em cada versão e com qual mecânica) continua em [`docs/ROSTER.md`](../ROSTER.md); as criaturas de lá aparecem aqui em negrito, com a versão. As outras entram aos poucos, era por era.

| Era | Capítulo | Criaturas | Domáveis | Montáveis | Plataforma | Ombro | Voadoras | Aquáticas | Mamíferos | No plano |
|---|---|---|---|---|---|---|---|---|---|---|
| [Cretáceo Superior](01_cretaceo_superior.md) | Capítulo 1: Ecos do Fim (Overworld) | 327 | 309 | 196 | 18 | 26 | 13 | 49 | 9 | 49 |
| [Cretáceo Inferior](02_cretaceo_inferior.md) | Capítulo 2: A Lagoa de Araripe | 211 | 194 | 100 | 11 | 42 | 26 | 20 | 10 | 29 |
| [Jurássico](03_jurassico.md) | Capítulo 3: O Reino dos Gigantes | 235 | 205 | 118 | 17 | 47 | 32 | 50 | 14 | 34 |
| [Triássico](04_triassico.md) | Capítulo 4: A Origem | 223 | 196 | 78 | 3 | 51 | 15 | 56 | 21 | 24 |
| [Era do Gelo](05_era_do_gelo.md) | Epílogo: O Caminho de Volta | 205 | 201 | 124 | 1 | 27 | 11 | 9 | 160 | 14 |
| [Anomalias da Fenda](06_anomalias.md) | Em qualquer era | 2 | 2 | 2 | 0 | 0 | 0 | 2 | 0 | 2 |

## Legenda

| Coluna | Significado |
|---|---|
| **Tipo** | 🦖 terrestre · 🐾 mamífero terrestre · 🪽 voador ou planador · 🌊 aquático · 🐊 anfíbio (anda e nada) |
| **Nicho** | O lugar da criatura na cadeia alimentar da era (define spawn, bando e quem caça quem) |
| **Domar** | **Comida**: alimentar até domesticar · **Ovo**: só criado desde o ovo · **Filhote**: animal que paria filhotes vivos (mamíferos, mosassauros, plesiossauros, ictiossauros), criado desde recém-nascido · **Nocaute**: derrubar com armas de narcótico e alimentar enquanto dorme · **—**: não domesticável |
| **Montaria** | ✅ montável · 🪑 sela de plataforma (dá para construir em cima) · 🦜 vai no ombro · — não montável |
| **Tamanho** | Comprimento do corpo, envergadura (env.) nos voadores ou altura (alt.). 1 bloco = 1 m |
| **Comportamento** | Como o animal selvagem reage ao jogador, no estilo ARK: **Pacífico** ignora · **Arisco** foge · **Defensivo** só revida · **Territorial** ataca quem chega perto · **Agressivo** caça o jogador |
| **Versão** | Versão do plano em `docs/ROSTER.md`; vazio = ainda sem versão |

## Regras

- **Tamanhos:** topo das estimativas publicadas para adultos, 1 bloco = 1 m (regra aprovada pelo Rodrigo). Aqui são valores de planejamento; quando a espécie for implementada, o tamanho final e a fonte vão para `docs/TAMANHOS.md`.
- **Domar e montaria (ARK + vida real)** saem de regras automáticas para as criaturas sem versão. Herbívoros e onívoros se domam com comida, menos os gigantes (25 m ou mais), que precisam de nocaute como no ARK. Carnívoros pequenos se criam do ovo (ou do filhote, nos que pariam filhotes vivos) e os grandes, com nocaute. Peixes, invertebrados e bichos minúsculos não se domam. Para montar, o animal precisa aguentar uma pessoa (uns 300 kg): bípedes a partir de ~4,5 m, quadrúpedes pesados a partir de ~3 m, mamíferos a partir de ~1,8 m e voadores a partir de 5 m de envergadura. Gigantes (18 m ou mais) ganham sela de plataforma; criaturas pequenas vão no ombro. Quando uma criatura entrar no plano, os valores do `ROSTER.md` passam a valer.
- **Mundial:** as espécies vêm do mundo todo, na proporção dos fósseis conhecidos (América do Norte, Ásia, Europa, África, América do Sul, Austrália e Antártida), sem foco em um país.
- **Uma criatura, uma era:** cada gênero aparece numa era só, a que melhor representa a espécie. Criaturas de fora das 5 eras (Megalodon, Dunkleosteus) ficam nas Anomalias da Fenda.
- **Correção científica:** o Argentavis está no Epílogo pelo plano, mas viveu no Mioceno (6 milhões de anos), não na Era do Gelo. No jogo ele fica como vazamento da Fenda.
- **Pessoas:** nenhuma espécie humana (Neandertal etc.) entra; a única pessoa do mod é a Katarina.

## Como editar

Os dados ficam em `tools/roster/roster_data.py`, uma linha por criatura. Depois de editar, rode `python3 tools/roster/gen_roster.py`: ele reescreve esta pasta e o `bestiario.json` (para as ferramentas). Não edite os .md desta pasta à mão.
