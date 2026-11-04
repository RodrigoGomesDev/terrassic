# Ordens dos dinos domados (v0.16)

Pedido do Rodrigo (30/10/2026): mecânicas de ordem como no ARK. Estudo com a tabela completa (o que já existia e o que
faltava): https://claude.ai/artifact/DcT3Nc1WbkV5YFmRX9hvpY. Esta versão traz as ordens de um dino só, pela tela do dino.
A roda do apito (segurar H, todos os dinos que ouvem) entrou na 1.5: seção abaixo.

## 1.7: alcance do apito e "Meus dinos"
Feedback de jogador (04/11): "não dá para ver onde estão os dinos, e o apito só funciona a uns 50 blocos". O apito
alcança **96 blocos** (dentro do alcance de rastreio das entidades, 8 a 10 chunks). **Agachado + H** (ou a tecla
"Meus dinos", sem tecla padrão, ou `/terrassic dinos`) abre a lista de todos os domados com distância, direção,
coordenadas, se esperam ali e quando foram vistos; **Rastrear** põe uma seta no alto da tela. Posições em
`entity/TamedRegistry` (salvas no mundo), pacotes em `network/TamedNetwork`, telas em `client/MyDinosScreen` e
`client/DinoTracker`. Também: o modo Neutro e as ordens valem contra bichos de outros mods que provocaram a briga.

## Na tela do dino

Linha de baixo: **Seguir**, **Esperar**, **Vagar** e **Pare**. Linha de cima: **Modo** (um clique passa para o próximo),
Carga, Ombro e Inventário como antes.

- **Vagar:** anda a até 16 blocos de onde recebeu a ordem, sem te seguir e sem se teleportar até você. Se uma briga, um
  bando ou um voo o levar a mais de 24 blocos, ele volta. Montar, pôr no ombro, Seguir ou Esperar acabam com o vagar.
  Enquanto vaga, só briga com o que estiver dentro dos 16 blocos (vigia a área). O ponto fica salvo no mundo.
- **Pare:** larga o alvo na hora e fica 10 segundos fora de qualquer briga, mesmo se apanhar. Não muda a ordem
  (continua seguindo, esperando ou vagando).
- **Modo** (salvo no dino; o padrão é Neutro):
  - **Passivo:** nunca ataca, nem para se defender ou defender você. O ataque montado (clique esquerdo) continua.
  - **Neutro:** defende a si e a você e entra nas brigas que você começa, **menos contra jogadores e bichos domados**
    (escolha do Rodrigo, 30/10). Se o jogador ou o bicho te bateu nos últimos 5 segundos, conta como defesa e ele entra.
  - **Agressivo:** entra em todas as suas brigas (jogador só se o PvP do servidor permitir) e vai atrás de monstros
    (menos creeper) e dinos selvagens adultos a até 12 blocos. Não age sentado, montado, filhote, dormindo ou desmaiado.
    Herbívoros que fogem em vez de lutar ignoram o modo; répteis marinhos só vão atrás do que está na água.

## Fogo amigo (vale em todos os modos)

Um dino domado nunca ataca outro animal do mesmo dono (dino, lobo, cavalo...). Antes, um soco sem querer num dino seu
fazia os outros irem para cima dele, porque a regra herdada do Minecraft não tinha a proteção que o lobo tem.
Também não ataca um jogador que o dono não pode ferir (PvP desligado ou mesmo time), como o lobo.

## Código

- `entity/DinoStance` (os três modos) e a seção "orders" de `entity/DinosaurEntity`: `canAttack` (passivo, Pare e fogo
  amigo, perguntado por todos os objetivos de alvo ao começar e a cada tick), `wantsToAttack` (as brigas do dono),
  `ordersTick` (solta alvo proibido e mantém o ponto do vagar), `wanderHere`/`stopWandering` (`restrictTo` do vanilla,
  que o passeio aleatório respeita), `stopFighting`.
- `entity/ai/AggressiveStanceGoal`, registrado no construtor de `DinosaurEntity` para todas as espécies.
- `entity/ai/OrderedFollowOwnerGoal` (o seguir vanilla, quieto enquanto vaga) nos herbívoros, predadores e voadores;
  `FollowOwnerPathGoal` e o seguir dos nadadores checam o vagar.
- Tela: `client/DinoScreen`. Textos: `DINO_LANG` em `tools/javagen/gen_resources.py`.

## Roda do apito (1.5)

Segure **H**, aponte com o mouse e solte: a ordem vale para todos os seus dinos que ouvem o apito. Um clique na fatia
também dá a ordem; Esc, ou soltar com o mouse no meio, não dá nenhuma. Um toque rápido em H (soltar em menos de um
quarto de segundo, sem apontar) deixa a roda aberta: aí um clique na fatia, ou H de novo, dá a ordem. Serve para quem
joga no trackpad e para tecla que a janela não consegue ler segurada. Segurar H não repete nada, e o aperto que fecha
a roda não abre outra. Se a tecla for um botão do mouse, vale o mesmo. O desenho é o da prévia aprovada do HUD
(30/10, https://claude.ai/artifact/A8gmsTnR4hExM16C4XD7Bs): seis lajes de basalto em volta da mira, a apontada com
borda de âmbar e o nome no meio, e embaixo quantos dinos ouvem, o que a ordem faz e a tecla. Não escurece o mundo nem
pausa o jogo. A tecla muda em Controles > Terrassic.

Quem ouve: seus dinos domados vivos a até **24 blocos**, menos o que você monta e o que está no seu ombro. A ave do
ombro fica lá em qualquer ordem e nunca entra na contagem; se só ela estava perto, a barra diz que só ela ouviu e fica
no ombro, em vez de "ninguém ouviu". Os montados
por outra pessoa e os desmaiados não obedecem. Cada um que obedece mostra uma nota musical em cima da cabeça, e a barra
de ações diz quem obedeceu (o nome, se for um só, ou quantos). Por enquanto o apito não tem som: os sons do mod estão em
espera.

As seis ordens, em sentido horário a partir do alto:

- **Seguir** e **Esperar aqui:** as mesmas da tela do dino, para todos.
- **Vagar por perto:** cada um vaga em volta de onde está (o Vagar da tela do dino).
- **Atacar meu alvo:** o bicho que você mira, a até 32 blocos e sem parede no meio; se você não mira nada, o último
  que você acertou nos últimos 10 segundos, na mão, com flecha ou com dardo. Esse último o mod guarda sozinho (pelo
  evento de dano): o do vanilla esquece em 5 segundos e só conta golpe na mão, e por isso falhava em 3 dos 4 loaders.
  A mira nunca pega o que você monta nem a ave do ombro. Vale contra jogador e bicho domado de outra pessoa (era a única forma,
  pela decisão do Rodrigo de 30/10) e passa por cima de um Pare. Não obedecem: os passivos, os que estão esperando,
  filhotes, as espécies que fogem em vez de lutar, répteis marinhos com o alvo fora d'água, e ninguém ataca bicho seu.
  Jogador protegido pelo PvP desligado ou pelo time: ninguém vai, e a barra avisa.
- **Juntar o bando:** levantam, param de vagar e de brigar e vêm correndo até você; depois seguem como no Seguir.
- **Ficar passivo:** todos ficam no modo Passivo. Apitado de novo quando todos já estão passivos, voltam ao Neutro.

### Por que H

Conferido no código dos mods populares (01/11): Mekanism, Origins, Curios, JEI, EMI, REI, Create, Iron's Spells, Ars
Nouveau, Sophisticated Backpacks, Apotheosis, Ice and Fire, FTB Ultimine, Twilight Forest, Alex's Caves, Simple Voice
Chat, Quark, Waystones e Advent of Ascension. Só o **Mekanism** usa H, para ligar e desligar o HUD da MekaSuit; JEI,
EMI e REI só usam teclas dentro das telas deles. O vanilla não usa H. As outras letras livres no vanilla estão mais
ocupadas (G: Origins, Curios, Mekanism e Ice and Fire; V: Mekanism, Ars Nouveau, Iron's Spells; B, J, N: Mekanism;
K: Apotheosis). O Xaero, de código fechado, não foi conferido. H também é a tecla da prévia aprovada. Quem joga com Mekanism troca uma das duas
em Controles; o jogo marca o conflito em vermelho.

### Código

- `entity/Whistle`: quem ouve (`hears`, usado também pela roda para contar), as ordens (`blow`), a mira do alvo e o
  último que cada jogador acertou (`init`, pelo `EntityEvent.LIVING_HURT` do Architectury).
- `DinosaurEntity#orderAttack`: o ataque mandado pelo apito.
- `client/WhistleWheelScreen`: a roda; `client/DinoControls`: a tecla e o pacote; `network/DinoNetwork`: `dino_whistle`.
- Textos: `tools/javagen/gen_whistle.py` (os três idiomas). O Guia de Bolso explica o apito no tópico Ordens.
