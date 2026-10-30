# Carga: o baú nas costas (v0.6, fase 63)

Toda espécie montável leva carga depois de domada e adulta. O sistema é o do burro da Minecraft, com as regras do
Terrassic por cima: o código fica em `DinosaurEntity` (hand-written), e cada espécie só diz quantas fileiras leva
(`cargoRows()`, gerado por `tools/javagen/gen_species.py`).

## Regras

| Ação | Como |
|---|---|
| Equipar | Dono usa um **baú** (vanilla) no animal domado e adulto: o baú some e o animal passa a "levar carga". |
| Abrir | v0.12: pela **tela do dino**, botão **Carga**. A tela abre com **agachar + usar com a mão vazia** (a pé) ou com a **tecla do inventário** montado (`client/DinoScreen`). |
| Tirar | **Tesoura**: primeiro tira a sela (se houver), a segunda tesourada tira o baú e derruba tudo que havia dentro. |
| Morte | Derruba o baú e todo o conteúdo. |
| Coleta automática | De pé (não sentado), com baú, recolhe a cada meio segundo os itens caídos a 1 bloco do corpo: o que ele mesmo colhe (Terizinossauro, Deinocheirus), o que o dono derruba perto dele e o que cai de um bloco quebrado montado. |

A tela é o baú genérico de 1 a 6 fileiras, com o nome do animal; nada de tela própria (o painel de montaria vem na v0.8).

## Fileiras por espécie

Sem `cargo=` no gerador, a espécie montável leva fileiras pelo comprimento real (TAMANHOS):

| Comprimento | Fileiras | Exemplos |
|---|---|---|
| ≥ 25 m | 6 | Alamosaurus, Argentinosaurus, Dreadnoughtus |
| ≥ 15 m | 5 | Brachiosaurus, Mosasaurus |
| ≥ 9 m | 4 | Edmontosaurus, Saltasaurus, Opisthocoelicaudia, Terizinossauro, Deinocheirus, T. rex |
| ≥ 6 m | 3 | Tricerátops, Paquirrinossauro, Corythosaurus, Euoplocefalo |
| ≥ 3,5 m | 2 | Gallimimus, Struthiomimus, Protoceratops (se montável) |
| menor | 1 | |

`cargo=N` força o número (`cargo=0` tira a carga de uma montaria). Espécies não montáveis não levam carga a menos que
o gerador diga `cargo=N`.

## Sela de plataforma (fase 64)

Item `platform_saddle` (criativo por enquanto; receita no crafting da v0.8). Só as espécies com `platform=True` no
gerador a aceitam: Brachiosaurus, Alamosaurus, Argentinosaurus e Dreadnoughtus.

| Regra | Como |
|---|---|
| Equipar | Dono usa a sela de plataforma no titã domado, adulto e sem sela. Tesoura tira (derruba a sela de plataforma, não a comum). |
| Lugares | 4: o primeiro no lugar da sela, os outros em fila para trás ao longo do dorso, a 35% da largura do corpo um do outro. |
| Quem sobe | Qualquer jogador com a mão vazia (clique direito); o dono também. Agachar desce. |
| Quem conduz | Só o dono, em qualquer lugar da fila. Sem o dono a bordo o animal anda por conta própria com os passageiros. |
| Carga | A mesma do baú (fase 63): o dono abre com a tecla do inventário montado. |

Construir blocos de verdade em cima de um animal em movimento não cabe no Minecraft sem reescrever o mundo; a
plataforma do Terrassic é a dos lugares e da carga. Um convés de módulos (fogueira, bancada, cama) fica para depois,
se o jogo pedir.

## Tecla do inventário montado

Todo dinossauro é `HasCustomInventoryScreen` (a tecla do inventário manda o pedido ao servidor, que abre a carga). Para
a tecla continuar abrindo o inventário do jogador quando a montaria não tem baú, o mixin de cliente
`InventoryKeyMixin` (`MultiPlayerGameMode.isServerControlledInventory`) só devolve verdadeiro com baú.

## O que falta (fases seguintes)

- Peso e stamina da carga, e o painel de montaria com o peso: v0.8 (HUD).
- O baú e a sela de plataforma não aparecem no modelo ainda: fica para o passe visual das selas por espécie (v0.4 pendente).
