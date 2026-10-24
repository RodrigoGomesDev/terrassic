# Terrassic: arte de divulgação

## O que já existe (aprovado em 24/10/2026)

| Arquivo | Uso |
|---|---|
| `art/capa/terrassic_banner_1920x1080.png` | Banner e galeria (Modrinth, CurseForge), topo do README |
| `art/capa/terrassic_icon_512.png` | Ícone do projeto, T. rex de corpo inteiro saindo do anel do Altar do Salto (fundo escuro) |
| `art/capa/terrassic_icon_512_transparente.png` | O mesmo ícone com fundo transparente |

Tudo gerado por `tools/capagen/` (`python3 banner.py && python3 icon.py`): cenário em pixel art, letreiro com a fonte de
blocos própria e os modelos do mod renderizados com as texturas e animações do jogo. Os textos da página estão em `docs/RESUMO.md`.

## Próximo passo: imagens dentro do jogo (plano, ainda não feito)

A capa mostra o clima do mod; a galeria tem que mostrar **o jogo de verdade**. Fazer quando a v0.3 estiver testada no jogo
e repetir a cada versão que trouxer algo visível (criaturas, blocos, telas novas).

### Cenas (Capítulo 1, Cretáceo Superior)

1. **Manada no rio:** Parasaurolophus e Maiasaura bebendo, um Spinosaurus na água. Mostra escala real e ecossistema.
2. **O encontro:** jogador com lança de sílex diante de um T. rex. Mostra tamanho (1 bloco = 1 metro) e o perigo.
3. **Montaria:** jogador montado num Triceratops ou Gallimimus correndo pela savana.
4. **Voo:** jogador montado num Pteranodon sobre a costa, vista de cima.
5. **Mar:** Mosasaurus caçando debaixo d'água.
6. **Ninho:** ovos chocando, filhotes seguindo o jogador.
7. **Cientista:** o Caderno de Campo aberto (Guia com uma espécie estudada) e a Mesa de Pesquisa com fósseis.
8. **Acampamento primitivo:** casa de palha, pau a pique e paliçada, com um dino domesticado sentado. Mostra os blocos.
9. **Elenco:** todas as criaturas lado a lado numa planície, do Compsognathus ao Brachiosaurus.

As próximas eras ganham as cenas delas quando forem jogáveis.

### Como capturar (no Mac, `./gradlew :fabric:runClient`)

- Janela em **1920x1080**: argumentos `--width 1920 --height 1080` na configuração de run (ou janela maximizada num monitor 1080p).
- Gráficos "Fabuloso", distância de renderização 16+, FOV 70, GUI escala 2. Sem shaders nem outros mods (o mod é autoral).
- **F1** esconde o HUD; **F2** salva o print em `fabric/run/screenshots/`. Para as cenas do Caderno, com HUD.
- Mundo criativo de testes, com comandos para montar a cena:
  `/gamerule doDaylightCycle false`, `/time set 12500` (pôr do sol) ou `/time set 1000` (manhã), `/weather clear`,
  `/gamerule doMobSpawning false`, `/summon terrassic:tyrannosaurus ~ ~ ~ {NoAI:1b}` para posar sem o bicho andar.
- Tirar 3 a 5 prints por cena e escolher o melhor.

### Montagem (`tools/capagen/screens.py`, a fazer)

- Lê os prints escolhidos de `art/capa/prints/` (PNG direto do jogo, sem edição de pintura).
- Corta em 16:9 e exporta 1920x1080 para a galeria e 960x540 para o README.
- Opcional: faixa de legenda com a fonte de blocos do letreiro, em pt-BR, en-US e es-ES (uma imagem por idioma).
- Gera `art/capa/galeria_<cena>_<idioma>.png` e uma folha de contato para aprovação.
