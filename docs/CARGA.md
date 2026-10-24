# Carga: o baú nas costas (v0.6, fase 63)

Toda espécie montável leva carga depois de domada e adulta. O sistema é o do burro da Minecraft, com as regras do
Terrassic por cima: o código fica em `DinosaurEntity` (hand-written), e cada espécie só diz quantas fileiras leva
(`cargoRows()`, gerado por `tools/javagen/gen_species.py`).

## Regras

| Ação | Como |
|---|---|
| Equipar | Dono usa um **baú** (vanilla) no animal domado e adulto: o baú some e o animal passa a "levar carga". |
| Abrir | Sem sela: **agachar + usar com a mão vazia**. Com sela: montar e apertar a **tecla do inventário** (o jogo manda a abertura do inventário da montaria, como no cavalo). |
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

## O que falta (fases seguintes)

- Sela-plataforma (fase 64): vários passageiros e convés nos titãs.
- Peso e stamina da carga, e o painel de montaria com o peso: v0.8 (HUD).
- O baú não aparece no modelo ainda (um bloco de baú preso ao osso da sela): fica para o passe visual das selas por espécie (v0.4 pendente).
