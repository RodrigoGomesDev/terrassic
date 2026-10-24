# v0.9 "O Fim": Altar do Salto, ritual dos meteoros, Tirano da Fenda e o Salto

> Frente paralela de 24/10/2026, branch `paralelo/v0.9-salto` a partir da main fe984c2. Segue `HISTORIA.md`
> §0, §1, §3 (Capítulo 1, "Final") e §5, e a linha do Salto de `CONQUISTAS.md`.

## 1. O que entra

| Peça | O que faz | Código |
|---|---|---|
| Altar do Salto | Bloco de pedra, osso e couro com o âmbar em cima. Mostra fragmentos, modo e o próximo passo; acende conforme o anel e o ritual | `leap/LeapAltarBlock`, `LeapAltarBlockEntity` |
| Anel | 4 pedras em pé nas pontas (a 3 blocos) e 4 de osso nas diagonais (a 2 e 2 blocos) | `leap/AltarRing`, tags `altar_stones` e `altar_bones` |
| Modos | Normal, Rápido e Livre por mundo | `leap/LeapProgress` |
| Ritual dos meteoros | 30 s de meteoros e céu vermelho, depois o chefe | `LeapAltarBlockEntity`, `leap/Meteor` |
| Tirano da Fenda | Chefe do Capítulo 1 | `leap/RiftTyrant` |
| O Salto e o Salto Instável | Clarão do impacto, leva quem está no anel e os bichos deles | `leap/Leap` |
| Estrelas cadentes | À noite, cada vez mais frequentes; chuva delas no ritual | `client/LeapClient`, `mixin/client/LevelRendererMixin` |
| Criaturas da Fenda | Rachaduras de âmbar brilhando sobre o modelo | `DinosaurEntity.isRift`, `client/RiftLayer` |
| Comandos | `/terrassic modo`, `/terrassic capitulo`, `/terrassic ritual parar` | `leap/LeapCommands` |

Os registros ficam em `leap/LeapRegistry` (bloco, block entity, item, Tirano e meteoro), fora de
`ModBlocks`/`ModItems`/`ModEntities`, para esta frente não mexer nos arquivos de registro compartilhados.
Textos e JSON: `tools/javagen/gen_leap.py` (chamado por `gen_resources.py`). Arte: `tools/spritegen/leap_art.py`.

## 2. O Altar do Salto

Receita (bancada):

```
couro curtido   bloco de âmbar   couro curtido        (tanned_hide_panel, amber_block)
muro de ossário muro de ossário  muro de ossário      (ossuary_wall)
calcário emp.   calcário emp.    calcário emp.        (limestone_stacked)
```

O anel, visto de cima (A = Altar):

```
. . . S . . .      S = pedra em pé: menir ou qualquer pedra empilhada (17 blocos na tag)
. B . . . B .      B = osso: muro de ossário, arco de costelas, pilha de ossos, qualquer troféu de crânio,
. . . . . . .          bloco de osso do vanilla (56 blocos na tag)
S . . A . . S
. . . . . . .      Cada poste vale em qualquer altura da coluna, de 1 abaixo do Altar até 2 acima
. B . . . B .      (segue o terreno, e um troféu pode ficar em cima de uma pedra).
. . . S . . .
```

As tags são geradas a partir de `BuildingBlocks.java` com todas as entradas opcionais: renomear um bloco de
construção nunca quebra o Altar.

**Estados do bloco** (`stage`): 0 frio (anel incompleto, brasa fraca), 1 anel completo (âmbar respira), 2 ritual
(fogo e lava saindo do âmbar), 3 aberto (o Tirano foi vencido aqui; brilho e faíscas subindo). Luz 3, 8, 15 e 12.
O modelo usa só texturas que o mod já tem (calcário empilhado, muro de ossário, couro curtido, âmbar bruto e polido).

**Como usar** (Regra 0: nada acontece sozinho):

| Ação | O que acontece |
|---|---|
| Usar | Diz os fragmentos, o modo e o próximo passo. Com o anel incompleto, diz quantos postes faltam e mostra faíscas nos lugares |
| Agachar e usar com âmbar bruto | Com o núcleo inteiro: começa o ritual (gasta 1 âmbar). Com 2-3 fragmentos no modo Normal: pede confirmação e, na segunda oferenda em 5 s, faz o Salto Instável |
| Agachar e usar com a mão vazia | Salta, se o Altar estiver aberto para você |
| Agachar com outro bloco na mão | Coloca o bloco normalmente (para construir o anel em volta) |

Os cliques no Altar passam pelo evento de clique em bloco do Architectury, porque o vanilla não chama `Block.use`
para quem está agachado com item na mão. Há uma recarga de 12 ticks por jogador (segurar o botão não repete a ação).

## 3. Modos (Normal, Rápido, Livre)

| Modo | Ritual | Salto | Salto Instável |
|---|---|---|---|
| Normal | 4 fragmentos (2 de 3 objetivos por tema) | depois de vencer o Tirano | 2 ou 3 fragmentos, sem chefe |
| Rápido | 4 fragmentos, mas 1 objetivo por tema já faz o fragmento | com 4 fragmentos (o chefe é opcional) | 2 ou 3 fragmentos |
| Livre | sempre | sempre | não precisa |

- O progresso é **por jogador**: os fragmentos vêm do Diário de Campo de cada um, e vencer o Tirano fica salvo por
  jogador (`data/terrassic_leap.dat`). Quem estava na luta (a até 96 blocos do Altar ou do Tirano, ou que entrou no
  ritual e está a até 160) ganha a vitória.
- O modo é do mundo, salvo com ele. Mundo novo começa com `"progression_mode"` de `config/terrassic-world.json`
  (padrão `"normal"`). Operadores mudam com `/terrassic modo <normal|rapido|livre>` (também `/terrassic mode`).

## 4. O ritual dos meteoros e o Tirano da Fenda

1. **Chamado** (`"ritual_call_seconds"`, 30 s): o céu e a névoa ficam vermelhos a até 192 blocos do Altar (mais forte
   perto), as estrelas cadentes viram chuva, de dia ou de noite, e meteoros caem de 10 a 40 blocos do Altar.
   Quem está a até 48 blocos entra no ritual e ganha "Estrelas que caem".
2. **Luta**: o Tirano cai de 20 a 28 blocos do Altar, num clarão, e ruge. Os meteoros continuam, menos.
3. **Depois**: o Tirano morre, quem lutou ganha "Tirano da Fenda" e o Altar abre para essas pessoas; os meteoros
   param em 10 s.
4. **Fracasso**: se ninguém ficar perto (96 blocos do Altar ou 64 do Tirano) por 30 s, ou se o Altar quebrar, o
   Tirano volta para a Fenda. Dá para tentar de novo com outra oferenda.

**Meteoros**: entidades que descem a uns 70 graus deixando fogo e fumaça (partículas sempre visíveis) e estouram onde
caem. O estouro fere, queima e empurra só criaturas vivas (nunca blocos, itens no chão, molduras ou suportes de
armadura). `"meteor_damage": false` deixa só luz e som. Um em dez deixa um âmbar bruto ("uma estrela que caiu").
Meteoros não são salvos no mundo e não nascem fora da área que roda entidades (num servidor com distância de
simulação curta eles ficariam parados no céu).

**Tirano da Fenda** (`rift_tyrant`): um T. rex da Fenda, 35% maior que o maior rex (tamanho 1,35), com o modelo e as
animações do T. rex e as rachaduras de âmbar brilhando.

| Atributo | Valor |
|---|---|
| Vida | ~770 com 1 jogador (420 de base x 1,35²); +50% por jogador a mais, até 8 |
| Mordida | ~22 (16 x 1,35), mais o empurrão |
| Armadura | 12, robustez 4, não leva empurrão |
| Imune a | fogo, queda, afogamento e aos próprios meteoros |

- Caça todo jogador por perto (menos criativo e espectador), não dorme, não sente fome, não é domável, montável
  nem procria, nunca some sozinho.
- **Rugido da Fenda** a cada ~12 s com alguém a até 12 blocos: empurra e deixa lento quem está a até 10 blocos.
- **Abaixo da metade da vida** a barra fica vermelha e escurece o céu, ele fica mais rápido, chama raptores da Fenda
  (2 por vez, até 4) a cada 30 s e manda meteoros no alvo, com um anel de faíscas no chão onde vão cair.
- Não sai a mais de 48 blocos do Altar: larga quem fugiu para longe e volta. Se o ritual dele acabou, ou se ele não é
  o Tirano do ritual atual, volta para a Fenda sozinho.
- A regra "Nível de dificuldade" (`REGRAS.md`) vale para ele como para qualquer selvagem.
- Deixa uma carcaça de T. rex grande com 1-3 âmbar bruto, 2-4 dentes de rex e 6-10 carnes nobres.

## 5. O Salto e o Salto Instável

- O salto leva o jogador, **todo mundo que estiver dentro do anel** (3,5 blocos do Altar) e os bichos domesticados
  dessas pessoas que estiverem no anel (HISTORIA.md §0, item 7, e §1).
- Na tela: clarão branco-dourado (âmbar no instável) de uns 5 s, som de portal e trovão; o salto acontece com a tela
  branca.
- Cada era se registra com `Leap.registerDestination(capítulo, new Destination(dimensão, pouso, pouso instável))`.
  **O Capítulo 2 chega na v2.0**: até lá a cena toca inteira e a Fenda não abre. O jogador fica onde está, recebe a
  mensagem de que o Cretáceo Inferior chega numa próxima versão e não perde nada (o Salto Instável não gasta o âmbar
  enquanto não há destino). As conquistas "O Salto" e "Salto Instável" ficam com `ready=False` em `conquistas.py`
  até lá; o código já as entrega quando houver destino.
- `/terrassic capitulo 1` leva ao mundo normal; os outros capítulos respondem que ainda não estão no jogo.

## 6. Estrelas cadentes e criaturas da Fenda

**Estrelas cadentes** ("estrelas que caem cada vez mais", HISTORIA.md §3): riscos de luz no céu da noite, 0,6 por
minuto sem fragmentos e +1,6 por fragmento (~7 por minuto com 4); no ritual, chuva de dia ou de noite. Desenhadas
depois do céu vanilla (`LevelRendererMixin`), somem com chuva, na lava, na neve fofa e com cegueira ou escuridão.
Desligáveis em `config/terrassic-client.json` (`"shooting_stars"`; `"ritual_sky"` para o céu vermelho).

**Criaturas da Fenda**: `DinosaurEntity` ganhou uma marca sincronizada (`isRift`, salva como `"Rift"`). O renderer
desenha o modelo de novo com `textures/entity/rift_overlay.png` (rachaduras de âmbar), aditivo e com brilho próprio,
pulsando devagar. É uma textura só para todas as espécies: as rachaduras seguem o mapa UV de cada modelo, então
espécie nova ou remodelada não precisa de arte. Recebem a marca: os vazamentos das Tempestades da Fenda (no lugar
do brilho de contorno de antes), o Tirano e os raptores dele. Matar uma dá a conquista "Anomalia", que passou a
ficar debaixo de "Fora de época" (antes estava debaixo de "Ilha do Tempo", que ainda não existe).

## 7. Arquivos tocados fora da frente

Mudanças pequenas e aditivas em arquivos de outras frentes:

- `entity/DinosaurEntity.java`: o campo `DATA_RIFT`, `isRift`/`setRift` e a linha no NBT.
- `client/DinosaurRenderer.java`: uma linha (`addRenderLayer(new RiftLayer<>(this))`).
- `Terrassic.java`: `Leap.init()`.
- `tools/javagen/gen_resources.py`: chamada de `gen_leap` e a mescla do LANG.
- `tools/javagen/conquistas.py`: `meteor_ritual`, `rift_tyrant` e `rift_anomaly` prontas.

## 8. Decisões (o Rodrigo deixou a frente decidir, 24/10/2026)

1. **Força do Tirano**: os números da tabela valem para 1 jogador. Em multiplayer a vida sobe 50% por jogador a mais
   na luta (contados a até 96 blocos do Altar quando ele chega), até 8 jogadores (x4,5): 2 jogadores ~1.150,
   4 jogadores ~1.900. A mordida não muda (cada um continua levando o mesmo dano).
2. **Construir o Altar** não exige fragmentos (Regra 0: construir é livre); só o uso depende deles.
3. **Refazer o ritual** devolve só 1-3 âmbar: dá para lutar de novo (para quem não estava na primeira vez, ou por
   diversão) sem virar fazenda de âmbar.
