# Terrassic: árvore de conquistas

> Desenho de 24/10/2026, feito a partir de `docs/HISTORIA.md` (versão mundial), `docs/ESCOPO.md`, `docs/ROSTER.md` e `docs/DOMESTICACAO.md`.
> Gerado por `tools/javagen/conquistas.py` (árvore, ícones, gatilhos e textos nos 3 idiomas) e escrito pelo `gen_science.py`. Não edite os JSON à mão.

## Por que mudou

A árvore antiga tinha 12 conquistas soltas, todas penduradas na raiz, 4 delas impossíveis (a função ainda não existia), e nada da história aparecia: nem os fragmentos de âmbar, nem o Altar, nem a Katarina, nem a Fenda. A nova segue a história:

1. **Uma aba por capítulo**, com o **Diário de Campo** (4 temas, 2 de 3 objetivos por tema = 1 fragmento de âmbar), a **linha do Salto** (fragmentos, Altar, ritual, chefe, salto), a **linha da Katarina** e a **linha da Fenda**.
2. **Uma aba "Caderno de Campo"**, que vale em qualquer era: Guia de Campo, ferramentas do cientista, domesticação e páginas.
3. **Só entra no jogo o que já dá para fazer.** Cada conquista tem a versão em que a função chega; o gerador só escreve as prontas. Quando a função chegar, basta marcar `ready=True` na tabela.
4. **Abas das outras eras ficam escondidas** até o jogador chegar lá (a raiz de cada uma é "entrar na dimensão da era"), então ninguém vê spoiler.

## Regra 0 continua valendo

- Nenhuma conquista move o jogador nem trava nada. O que trava é só o **salto para uma era nova**, e só no modo Normal.
- A ordem é livre: no Minecraft dá para ganhar uma conquista "filha" antes da "mãe". As linhas da árvore são só um mapa.
- O progresso é por jogador, salvo no `Knowledge` (não no item). Ao entrar no mundo, tudo o que o jogador já fez é conferido de novo e as conquistas que faltam são dadas (mundos antigos não perdem nada).

## O que libera o salto (o que "trava" a máquina do tempo)

| Modo do mundo | Para acender o Altar | Para saltar para a era seguinte |
|---|---|---|
| **Normal** | 4 fragmentos (conquista **O núcleo reunido**) | Começar o ritual quando quiser e vencer o chefe |
| **Salto Instável** | 2 fragmentos quaisquer | Salta na hora, sem chefe, e chega em lugar aleatório (conquista escondida) |
| **Rápido** | 1 objetivo por tema = 1 fragmento | Chefe opcional |
| **Livre** | Nada | Todas as eras abertas; as conquistas continuam valendo como coleção |

Nenhuma outra conquista trava nada: as linhas da Katarina e da Fenda, os desafios e a aba Caderno de Campo são só história e coleção.
Um fragmento é contado, não é item: fragmentos = temas com 2 objetivos feitos. Assim ele não se perde nem se troca, e o Altar (v0.9) só lê esse número.

## Recompensas

| Tipo | Moldura | Recompensa |
|---|---|---|
| Objetivo do Diário | normal | 10 de XP |
| Fragmento de um tema | objetivo (goal) | 50 de XP e **1 Página Solta** (vira uma página da Katarina que o jogador ainda não tem: "ela deixou anotações") |
| O núcleo reunido, chefes, salto | objetivo (goal) | 100 de XP |
| Desafios (Guia completo, todas as páginas, T. rex de estimação...) | desafio | 100 de XP |
| Marcos da história e do Caderno | normal | 10 a 25 de XP |

---

## Aba "Capítulo 1: Ecos do Fim" (`terrassic:chapter1/...`)

Legenda: ✅ entra agora (v0.3); versão = quando a função chega.

```
Ecos do Fim (raiz)
├── Fragmento: Sobrevivência ── Um teto de palha ✅ · A primeira lança ✅ · Céu de âmbar (v0.8)
├── Fragmento: Ciência ──────── Cinco espécies ✅ ─ Naturalista do Cretáceo ✅ (desafio)
│                               Osso na pedra ✅ · Na mesa ✅
├── Fragmento: Domesticação ─── Amizade ✅ · Nasceu ✅ ─ Rei de estimação ✅ (desafio) · Na sela ✅
├── Fragmento: Exploração ───── Rastros dela ✅ · Mar Interior ✅ · A grande fila (v0.6)
├── O núcleo reunido ✅ ─ Estrelas que caem (v0.9) ─ Tirano da Fenda (v0.9) ─ O Salto (v2.0)
├── Ela esteve aqui ✅ ─ Casa do Rio (v0.8) ─ Mate (v0.8)
├── Fora de época ✅ ─ Ilha do Tempo (v0.8) ─ Anomalia (v0.8)
└── Salto Instável (escondida, v2.0)
```

| Id | Nome (pt) | Como ganha | Gatilho | Versão |
|---|---|---|---|---|
| root | Ecos do Fim | Entrar no mundo | `minecraft:tick` | ✅ |
| fragment_survival / science / taming / exploration | Fragmento: (tema) | 2 dos 3 objetivos do tema | código (`Research`) | ✅ |
| shelter | Um teto de palha | Colocar 16 blocos de palha | código | ✅ |
| first_spear | A primeira lança | Fazer uma lança | código | ✅ |
| rift_storm | Céu de âmbar | Sobreviver a uma Tempestade da Fenda | código | v0.8 |
| study_five | Cinco espécies | 5 espécies "Estudadas" no Guia | código | ✅ |
| first_fossil | Osso na pedra | Escavar um fóssil | código | ✅ |
| research_table | Na mesa | Estudar fóssil, esboço ou amostra na Mesa | código | ✅ |
| tame_herbivore | Amizade | Domar um herbívoro na mão | código | ✅ |
| hatch_egg | Nasceu | Estar perto de um ovo quando ele choca | código | ✅ |
| ride | Na sela | Montar uma criatura com sela | código | ✅ |
| katarina_pages | Rastros dela | Achar 3 páginas da Katarina (troca "2 acampamentos": os acampamentos da v0.8 dão páginas, então já contam) | código | ✅ |
| inland_sea | Mar Interior | Avistar um réptil marinho e um pterossauro (troca a "Ruína da Fenda", que não existe na seção 8 da história) | código | ✅ |
| migration | A grande fila | Ver uma migração de hadrossauros | código | v0.6 |
| four_fragments | O núcleo reunido | Os 4 fragmentos: o Altar do Salto pode ser aceso | código | ✅ |
| meteor_ritual | Estrelas que caem | Começar o ritual no Altar | código | v0.9 |
| rift_tyrant | Tirano da Fenda | Vencer o chefe | código | v0.9 |
| leap | O Salto | Saltar para o Capítulo 2 pelo Altar | código | v2.0 |
| unstable_jump | Salto Instável | Saltar com só 2 fragmentos (escondida) | código | v2.0 |
| first_page | Ela esteve aqui | Achar a primeira página da Katarina | código | ✅ |
| river_house | Casa do Rio | Achar o Refúgio da Katarina | código | v0.8 |
| mate | Mate | O Parasaurolophus da Katarina aceita você (piada interna: "mate" é parceiro e chimarrão) | código | v0.8 |
| out_of_time | Fora de época | Avistar no Cretáceo uma criatura de outra era (os "vazamentos da Fenda": Stegosaurus, Brachiosaurus, Dilophosaurus, Compsognathus) | código | ✅ |
| time_island | Ilha do Tempo | Pisar numa Ilha do Tempo | código | v0.8 |
| rift_anomaly | Anomalia | Derrotar uma criatura da Fenda | código | v0.8 |
| all_cretaceous | Naturalista do Cretáceo | Todas as espécies do Cretáceo Superior que existem no mod "Estudadas" (desafio) | código | ✅ |
| pet_rex | Rei de estimação | Ter um Tiranossauro domesticado (só sai do ovo) (desafio) | código | ✅ |

## Aba "Caderno de Campo" (`terrassic:journal/...`), vale em todas as eras

```
Caderno de Campo (raiz)
├── Visto vivo ✅ ─ Anotado ✅ ─ Guia de Campo completo ✅ (desafio)
├── Só os ossos ✅ ─ Ossos do futuro ✅
├── Lágrima de árvore ✅ ─ Olho de âmbar ✅
├── Traço de carvão ✅ ─ Frasco cheio ✅
├── Asas de couro ✅ · Nadadeiras (v0.5) · Manada mista ✅
├── Boa noite (v0.7) ─ Domado no sono (v0.7)
├── Meio caderno ✅ ─ O caderno dela ✅ (desafio)
└── Uma de cada era (v5.0, desafio) · Expedição (pós-final)
```

| Id | Nome (pt) | Como ganha | Gatilho | Versão |
|---|---|---|---|---|
| root | Caderno de Campo | Entrar no mundo | `minecraft:tick` | ✅ |
| first_sighting | Visto vivo | Primeira espécie "Avistada" | código | ✅ |
| first_studied | Anotado | Primeira espécie "Estudada" | código | ✅ |
| guide_complete | Guia de Campo completo | Todas as espécies do mod "Estudadas". Pista do final secreto (seção 7) | código | ✅ |
| first_silhouette | Só os ossos | Estudar um fóssil na Mesa | código | ✅ |
| deep_time | Ossos do futuro | Estudar o fóssil de uma era mais antiga que a sua (no Cretáceo, um jurássico): "os fósseis contam o futuro da história" | código | ✅ |
| raw_amber | Lágrima de árvore | Ter Âmbar Bruto | `inventory_changed` | ✅ |
| amber_lens | Olho de âmbar | Observar uma criatura com a Lente de Âmbar até registrar | código | ✅ |
| first_sketch | Traço de carvão | Terminar um esboço | código | ✅ |
| blood_sample | Frasco cheio | Ter uma Amostra de Sangue | `inventory_changed` | ✅ |
| ride_flyer | Asas de couro | Voar montado num pterossauro | código | ✅ |
| ride_swimmer | Nadadeiras | Nadar montado num réptil marinho | código | v0.5 |
| five_tamed | Manada mista | 5 espécies diferentes domesticadas | código | ✅ |
| knockout | Boa noite | Derrubar uma criatura por nocaute | código | v0.7 |
| knockout_tame | Domado no sono | Domar uma criatura derrubada | código | v0.7 |
| five_pages | Meio caderno | 5 páginas da Katarina | código | ✅ |
| all_pages | O caderno dela | Todas as páginas que existem no mod (desafio) | código | ✅ |
| every_era | Uma de cada era | Uma criatura domesticada de cada era (desafio) | código | v5.0 |
| expedition | Expedição | Completar uma expedição do laboratório | código | pós-final |

---

## Abas das próximas eras (desenho; entram com cada era)

Mesma forma do Capítulo 1: raiz = chegar à era (`minecraft:changed_dimension` para a dimensão dela, por isso a aba só aparece lá), 4 fragmentos com 3 objetivos cada, linha do Salto, linha da Katarina, linha da Fenda e desafios. Objetivos tirados da história (seções 3 e 8).

### Capítulo 2: Penas e Cinzas (v2.0)
| Tema | Objetivos (2 de 3) |
|---|---|
| Sobrevivência | Abrigar-se de uma chuva de cinza · Fazer argamassa de cinza vulcânica · Atravessar a seca das lagoas salgadas |
| Ciência | Estudar 5 espécies da era · Um fóssil perfeito em Calcário Laminado · Juntar penas de 3 espécies |
| Domesticação | Domar um dinossauro com penas · Montar um pterossauro de crista · Chocar um ovo da colônia de pterossauros |
| Exploração | Achar 3 páginas da era · Achar a falésia dos pterossauros · Achar o campo de cinza com fósseis |

Linhas: **Palafita da Katarina** (Refúgio) · O núcleo reunido ─ **Rei do Rio** (Sarcosuchus da Fenda) ─ O Salto · Desafios: Naturalista do Cretáceo Inferior; domar um Yutyrannus.

### Capítulo 3: O Reino dos Gigantes (v3.0)
| Tema | Objetivos (2 de 3) |
|---|---|
| Sobrevivência | Aguentar uma monção inteira · Cruzar entre ilhas na maré baixa · Construir com madeira de araucária |
| Ciência | Estudar 5 espécies da era · Seguir uma trilha de pegadas até a manada · Estudar uma concha de amonite |
| Domesticação | Montar um saurópode na sela de plataforma · Domar um saurópode anão das ilhas · Chocar um ovo na estação úmida |
| Exploração | Achar 3 páginas da era · Ver o Archaeopteryx na lagoa calcária · Mergulhar num recife de esponjas |

Linhas: **Caverna da Katarina** (o mapa na parede) · O núcleo reunido ─ **Leviatã da Fenda** ─ O Salto · Desafios: Naturalista do Jurássico; montar um Brachiosaurus.

### Capítulo 4: A Origem (v4.0)
| Tema | Objetivos (2 de 3) |
|---|---|
| Sobrevivência | Beber água no calor do meio-dia · Atravessar o Deserto Vermelho · Ver o deserto ficar verde no Episódio Pluvial |
| Ciência | Estudar 5 espécies da era · Estudar um dos primeiros dinossauros · Coletar âmbar triássico |
| Domesticação | Domar um dos primeiros dinossauros · Domar um dicinodonte · Nocautear um Prestosuchus |
| Exploração | Achar 3 páginas da era · Achar um oásis · Achar o ossuário de Coelophysis |

Linhas: **Último Acampamento** ─ **Katarina viva** (falar com ela) · O núcleo reunido ─ **Coração da Fenda** (3 fases) ─ finais: **A Guardiã**, **O Guardião**, **Os dois voltam** (escondida: exige o Guia completo das quatro eras) · Desafio: Naturalista do Triássico.

### Epílogo: O Caminho de Volta (v5.0)
Sem fragmentos: é sobrevivência. Roupa de pele · Fogueira com gordura · Marfim de mamute · Domar um mamute · **A Grande Nevasca** (goal) ─ **Altar religado** ─ **Em casa** (créditos).

---

## Como mexer

- Árvore e textos: `tools/javagen/conquistas.py` (`NODES`). Cada nó tem id, mãe, ícone, moldura, gatilho, XP, `ready` e o texto em pt, en e es. Objetivos do Diário usam os textos de `lore.OBJECTIVES` (os mesmos do Caderno).
- O gerador apaga e reescreve `data/terrassic/advancements/`, confere que toda mãe existe e que todo id que o Java usa (`Research.award(..., "<aba>/<id>")`) está na tabela.
- Conquistas por código usam o critério `done` (`minecraft:impossible`) e são dadas por `Research.award`. As de item usam `minecraft:inventory_changed` e não precisam de Java.
- Função nova pronta: marcar `ready=True`, ligar o `Research.award` no evento e (se for objetivo do Diário) `available=true` no `Objective`.
