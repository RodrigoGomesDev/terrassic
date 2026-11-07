# Ícones nos minimapas e mapas (1.9.6)

Cada espécie aparece nos mods de mapa com o **próprio rosto**, desenhado a partir do modelo dela (não é o ovo do
inventário). Os quatro mapas que mostram mobs leem o ícone dos recursos do jogo: são só arquivos no nosso jar, sem
código e sem dependência; sem o mapa instalado, ficam parados. Funciona igual em Fabric, Forge e NeoForge.

Gerador: `tools/spritegen/map_icons.py` (lê `gen_species.SPECIES`). A cabeça (o osso `head` e os filhos) é renderizada do
`geo.json` exportado, com a pele do macho, em pixels exatos da textura e contorno escuro de 1 px: matriz de 32x32 e
uma de 16x16 reduzida dela guardando o pixel de mais contraste de cada 2x2 (olho, dentes, chifre). Ângulo de três
quartos; bicos e focinhos compridos mais de frente e de cima (`VIEW`).

| Mapa | Arquivo (por espécie `<id>`) | Tamanho |
|---|---|---|
| Xaero's Minimap / World Map | `assets/xaerominimap/entity/icon/definition/terrassic/<id>.json` + `.../sprite/terrassic/<id>.png` | 64x64 (desenho de 32 no meio) |
| JourneyMap 6 | `assets/journeymap/icon/entity/terrassic/<id>.png` | 16x16 |
| JourneyMap 5.x | `assets/terrassic/textures/entity_icon/<id>_male.png`, `_female` (e `_alpha_*` no T. rex) | 16x16 |
| FTB Chunks | `assets/ftbchunks/textures/faces/terrassic/<id>.png` e `assets/ftblibrary/...` (2101.1.11+) | 16x16 |
| VoxelMap | `assets/minecraft/textures/icons/com.terrassic.entity.<classe>16.png` | 16x16 |

O que o jogador liga: no Xaero, "Display Icons" em "Always" nas configurações do radar de entidades; no JourneyMap,
"Mob Display" em "Icons". Espécie nova: rodar o gerador (renomear a classe Java quebra o ícone do VoxelMap).

Ainda não visto num mapa de verdade: rodar os mapas no cliente de teste exige baixar e executar o mod de terceiros, o que
pede a permissão do Rodrigo.
