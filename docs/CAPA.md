# Terrassic: arte de divulgação

## Ideia futura — vídeo de apresentação da fauna

Pedido de Rodrigo em 26/10/2026: um vídeo curto passeando por muitos dinossauros do Terrassic,
mostrando os animais e o mundo. Guardar a ideia; produção ainda não iniciada.

Direção inicial: movimentos de câmera suaves, alternando manadas, grandes predadores, voadores
e fauna marinha, com os modelos originais do mod e a identidade atual. Definir duração, roteiro,
trilha e formato quando Rodrigo retomar. Caminho inicial sugerido: capturar cenas no próprio jogo,
montar uma primeira versão e só depois avaliar renderizações extras. Cenas precisam ser preparadas
para controlar fauna, luz, enquadramento e estabilidade; não gerar animação por IA que altere os modelos.

## Reformulação da capa Caçada — 26/10/2026

Pedido atual do Rodrigo: adaptar também a capa principal à identidade entregue. Nova versão em
`art/divulgacao/capa/v2/`, com letreiro ativo, Sedimento, céu de crepúsculo e laranja menos dominante.
Reaproveita o render sem título, sem alterar a geometria da cena. Inglês principal, alternativas em
português/espanhol e fundo sem texto; detalhes e limites no README da pasta. Imagens e pacote
conferidos; aprovação estética pendente. Os arquivos anteriores abaixo permanecem preservados.

## O que já existe (aprovado em 25/10/2026)

| Arquivo | Uso |
|---|---|
| `art/capa/terrassic_banner_1920x1080.png` | Banner principal (Modrinth, CurseForge), topo do README. É a capa "Caçada" |
| `art/capa/terrassic_capa_cacada.png` | Capa "Caçada": T. rex e Triceratops frente a frente no entardecer, manadas correndo ao fundo |
| `art/capa/terrassic_capa_neblina.png` | Capa "Neblina": um T. rex espreitando um Alamosaurus na floresta fria e enevoada |
| `art/capa/terrassic_capa_*_sem_titulo.png` | As duas capas sem letreiro (galeria, posts, fundos) |
| `art/capa/terrassic_icon_512.png` | Ícone do projeto: o T. rex da capa "Caçada" rugindo contra o entardecer |
| `art/capa/terrassic_icon_512_transparente.png` | Só o T. rex, fundo transparente |
| `common/src/main/resources/assets/terrassic/icon.png` | O mesmo ícone em 128x128, mostrado na lista de mods do jogo |

O slogan das capas é em inglês ("THE PAST HAS AWOKEN."), em todas, por decisão do Rodrigo (vende melhor no geral).
O letreiro e o slogan usam o **Degraus**, a letra de título aprovada em 25/10/2026 (`docs/IDENTIDADE.md` §5), no
acabamento pedra; o slogan vai em osso, menor e com desgaste leve para ler bem.
As capas antigas em pixel art (banner de 24/10, ícone do anel do Altar do Salto) foram substituídas; `banner.py`, `icon.py`
e `scene.py` ficam só como referência (rodar `icon.py` sobrescreve o ícone novo).

### Como as capas são feitas (`tools/capagen/`)

Os cenários são montados **com os blocos do próprio mod** (texturas do jogo, 1 bloco = 1 metro) e os dinossauros são os
**modelos atuais do mod**, pintados direto do código de `tools/modelgen` e posados com as animações do jogo. A imagem
final é renderizada com path tracing no Blender (Cycles): sol com sombra suave, luz rebatida, neblina volumétrica com
raios de sol, água com transparência. Nada é pintado à mão nem copiado.

| Arquivo | O que faz |
|---|---|
| `voxels.py` | Mundo de blocos: terreno, rochas, árvores (araucária, conífera, samambaia), plantas, malha dos dinossauros |
| `cenas.py` | As cenas (`cacada`, `espreita` = Neblina, e outras: `ribeira`, `vale`, `manada`, `costa`, `falesia`) |
| `blend.py` | Renderização no Blender Cycles (céu, sol, neblina, água, câmera com profundidade de campo) |
| `gl.py` | Prévia rápida em OpenGL (segundos), para acertar câmera e composição antes do render final |
| `capas.py` | Põe o letreiro TERRASSIC e o slogan em Degraus (`titulo.py`, `letreiro.py`) sobre a cena |
| `icone.py` | O ícone, com a mesma cena e luz da capa "Caçada" |

Precisa de `pillow`, `numpy` e `bpy` (`pip install bpy`, o Blender como módulo Python; versão 5.x, Python 3.13).
Para gerar de novo (cerca de 20 a 45 minutos por capa em 4 núcleos):

```
cd tools/capagen
BACKEND=cycles SAMPLES=128 SS=1.5 VSTEP=1 python3 -B cenas.py cacada espreita   # -> art/capa/cenas/
python3 -B capas.py cacada espreita    # -> art/capa/terrassic_capa_cacada.png e terrassic_capa_espreita.png (= Neblina)
SAMPLES=128 python3 -B icone.py   # -> ícones 512 (opaco e transparente)
```

Prévia rápida de uma cena: `xvfb-run -a -s "-screen 0 1920x1080x24" python3 -B cenas.py cacada --small`
(ou `BACKEND=cycles SAMPLES=32 ... --small`, cerca de 1 minuto). O menu do jogo (`tools/menugen`) usa as mesmas peças.
Os textos da página estão em `docs/RESUMO.md`.

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
- Opcional: faixa de legenda com o Degraus, em pt-BR, en-US e es-ES (uma imagem por idioma).
- Gera `art/capa/galeria_<cena>_<idioma>.png` e uma folha de contato para aprovação.

## Capa Espreita (v4) — 30/10/2026

Aprovada pelo Rodrigo: o T. rex v2 espreitando na floresta enevoada com um facho de sol no rosto, render puro no
Blender com o modelo e as texturas do jogo. Arquivos e como gerar de novo em `art/divulgacao/capa/v4/README.md`.
Substitui a v3 (que tinha o fundo editado por IA) nas lojas. As capas são só para loja, site e posts; o menu do jogo
continua o do Minecraft.

## Capa Carcaça na praia — 31/10/2026

Aprovada pelo Rodrigo: Velociraptors comendo um Pteranodonte morto na praia, num dia de sol. Mesmo processo da
Espreita (Blender com os modelos e as texturas do jogo), com o letreiro em cima à direita. Arquivos e como gerar de
novo em `art/divulgacao/capa/carcaca/README.md`.
