# Ordens dos dinos domados (v0.16)

Pedido do Rodrigo (30/10/2026): mecânicas de ordem como no ARK. Estudo com a tabela completa (o que já existia e o que
faltava): https://claude.ai/artifact/DcT3Nc1WbkV5YFmRX9hvpY. Esta versão traz as ordens de um dino só, pela tela do dino.
A roda do apito (segurar H, todos os dinos que ouvem) vem na v0.16.1.

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
