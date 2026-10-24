# Carcaças (v0.6, fase 65)

Um dinossauro morto não explode em itens: deixa uma **carcaça** (`CarcassEntity`), o próprio modelo da espécie
deitado na pose `knocked_out`, com a textura do sexo certo e o tamanho do animal (filhote pequeno). O loot da morte
(tabela de loot da espécie) fica dentro dela; a sela, o baú e a carga caem no chão normalmente.

## Regras

| Coisa | Como |
|---|---|
| Porções ("carne") | `max(2, largura da hitbox × 4)`: Compsognathus 2, Velociraptor ~3, T. rex ~12, Alamosaurus 20. Cada porção leva uma fatia proporcional das pilhas de loot. |
| Colher (jogador) | Bater ou usar a carcaça: uma porção por golpe de mão; **duas** com ferramenta ou arma de nível (faca/machadinha/clava/machado/espada; gasta 1 de durabilidade). Os itens caem aos pés do jogador. |
| Carniceiros | Todo `PredatorDinosaur` (selvagem ou domado, sem alvo, não sentado) anda até a carcaça mais próxima a 24 blocos e morde a cada 1,5 s: a porção some, ele cura 4 e toca a animação `eat`. |
| Saciado | Depois de `2 + largura × 2` mordidas o animal fica saciado por 5-7 min: **um predador selvagem saciado não caça** (`canHunt()`), nem jogadores nem presas. É o primeiro pedaço da cadeia alimentar: caça, come, descansa. |
| Apodrecer | `2 min + 1 min por bloco de largura` (T. rex ~5 min, titãs ~7-8 min); no último minuto solta "moscas" (partículas). Ao apodrecer, ou ao acabar a carne, o loot que sobrou cai no chão: nada se perde. |
| Física | Cai até o chão, não empurra nem é empurrada, não bloqueia (atravessável), pode ser mirada. |
| Salvar | Espécie, sexo, tamanho, carne, vida restante e loot vão para o NBT. |

A carcaça é um `Entity` comum com GeckoLib (`GeoEntity`), registrada à mão em `ModEntities.CARCASS` (categoria MISC) e
desenhada por `CarcassRenderer`, que acha o modelo/textura/animação pela espécie e usa a escala do modelo em
`TerrassicClient.MODEL_SCALES`.

## O que falta

- Pterossauros e répteis marinhos ainda não comem carcaças (o goal é terrestre; o voo e o nado têm IA própria).
- Fome de verdade (o predador caçar porque está com fome, não só deixar de caçar quando cheio) e sono: fase 66.
- Carcaças de criaturas vanilla e de jogadores: não.
