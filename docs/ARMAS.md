# Armas (refação v1.1)

Pedido do Rodrigo em 31/10/2026: os dardos estavam feios e quase impossíveis de usar; quer armas com animações mais
dinâmicas, um arco mais bolado e uma lança melhor. Proposta aprovada ("pode continuar", 31/10 03:42Z):
https://claude.ai/artifact/79FSKssTmZofQTHUWtj4sw

Regra: só poses que o próprio Minecraft já tem (arco, tridente, chifre de cabra) e modelos 3D simples no estilo da
flecha e do tridente vanilla. Arte desenhada à mão pixel a pixel em `tools/spritegen/armas.py`.

## 1.7: clavas mais lentas e Better Combat
Feedback de jogador (04/11/2026): "a clava é forte demais, 0,20 de velocidade seria justo". Clava de Cauda 0,6 → 0,2
ataques por segundo, Clava de Osso 0,8 → 0,25 (`ModItems`). Better Combat: `data/terrassic/weapon_attributes/` dá às
armas os presets do mod (Clava de Osso = `mace`, Clava de Cauda = `hammer`, lanças = `spear`, faca e adaga = `dagger`,
machadinha = `axe`; tabela `BETTER_COMBAT` em `gen_resources.py`). Antes só a adaga funcionava, pelo nome.

## Passo 1: zarabatana e dardo (feito)
- `item/BlowgunItem`: segurar = pose do chifre de cabra (`UseAnim.TOOT_HORN`) e fôlego até 1 s (`FULL_BREATH` = 20
  ticks, "clique" baixo quando enche); soltar sopra. Menos de 3 ticks não atira. Velocidade 1,4 + 1,6·fôlego,
  espalhamento 1,2 − 1,0·fôlego, potência 1 + 0,5·fôlego. Recarga 8 ticks.
- Primeira pessoa: a propriedade `terrassic:blowing` (`client/WeaponPoses`) troca o modelo por
  `item/blowgun_blowing` (tubo 3D de 24 px com bocal de couro, gerado em `gen_resources.HELD_MODELS`), que aponta
  para a mira.
- `entity/TranqDart`: dose = (16 + 6% do torpor máximo; era 14) · potência. Ao entrar o narcótico: 10 espirais violeta
  (`ENTITY_EFFECT`) no bicho e um "tic" de ametista para quem atirou, mais agudo conforme o torpor enche.
- `client/TranqDartRenderer`: os planos cruzados da flecha vanilla a 60%, textura `textures/entity/tranq_dart.png`
  (vista lateral 16x5 + traseira 5x5 no layout da flecha).
- Dardos por bicho (fôlego cheio, sem contar o torpor que escoa): Velociraptor 1, Triceratops 4, T. rex 5.

## Passo 2: arco de caça e flechas (feito)
- `item/HuntingBowItem` (estende o arco vanilla): recurvo de madeira com tendão, pontas de osso e pega de couro.
  Puxada de 25 ticks (vanilla 20), tiro cheio a 3,3 (vanilla 3,0), +1 de dano, espalhamento 0,8, durabilidade 480.
  Mesma pose e tremida do arco vanilla; quadros de puxada pelas propriedades `pulling`/`pull` registradas para ele em
  `client/WeaponPoses`; zoom da puxada por `mixin/client/BowZoomMixin` (o jogo só dá zoom ao arco vanilla).
- Flechas (`item/TerrassicArrowItem`, tag `minecraft:arrows`, então qualquer arco e a besta usam):
  - `flint_arrow` (`entity/FlintArrow`): dano base 2,5 (vanilla 2). Receita: sílex + graveto + junco = 4.
  - `narcotic_arrow` (`entity/NarcoticArrow`, é um `TranqDart`): potência 2,2 x força do tiro (velocidade/3).
    Receita: 8 flechas de sílex em volta de 1 erva sonífera = 8.
- Arco: graveto, osso e junco no formato do arco vanilla.
- Flechas narcóticas por bicho (puxada cheia): Velociraptor 1, Triceratops 3, T. rex 3.
- `client/PrimitiveArrowRenderer` (era TranqDartRenderer) desenha dardo e flechas com a textura de cada um.
## Passo 3: lança 3D e estocada (feito)
- Toque rápido (menos de 10 ticks) = estocada: o primeiro bicho na mira até 4,5 blocos leva um golpe corpo a corpo
  normal (`player.attack`), com faíscas de crítico e som; recarga 12 ticks. Segurar 10 ticks = arremesso como antes,
  com um "clique" quando fica pronto. Constantes `SpearItem.THROW_CHARGE` e `THRUST_REACH`.
- Na mão e no ar: modelo 3D (`models/item/<lança>_held.json`, gerado em `gen_resources._spear_held`): haste de 32 px
  deitada na diagonal do sprite (a pose de item de mão segura do mesmo jeito), ponta de sílex ou chifre, amarração de
  tendão, pega de couro. Troca pela sobreposição `terrassic:held` que só vale durante `mixin/client/HeldSpearMixin`
  (mãos e voo; inventário, chão e moldura seguem com o sprite), como o tridente vanilla.
- Cravada no chão ela balança como a flecha (`ThrownSpearRenderer`, `shakeTime`).

## v1.1: boleadeira (feito)
Pedido do Rodrigo em 31/10/2026 ("sinto falta de uma boiadeira para derrubar os dinos voantes"). Desenho A e regras
aprovados no mesmo dia: https://claude.ai/artifact/7fjdqYKRkavzwZ64aiwyyk
- `item/BolaItem`: segurar gira acima da cabeça (pose do tridente, `UseAnim.SPEAR`, um "vush" por volta); soltar
  arremessa. Giro cheio em 20 ticks: velocidade 0,9 + 0,9·giro (uns 20 blocos), espalhamento 1,0. Menos de 4 ticks
  não arremessa. Recarga 20 ticks, pilha de 16.
- `entity/ThrownBola` (projétil de item, como a bola de neve): não fere, amarra.
  - Voador no ar: asas presas por `FLYER_TICKS` = 160 (8 s): para de voar e cai, sem dano de queda; o cavaleiro cai junto.
  - Outro bicho do mod: pernas presas por `GROUND_TICKS` = 120 (6 s). Amarrado = `isImmobile` (não anda, não luta, não
    voa); montado, a montaria não anda nem pula.
  - Gigantes (vida de tabela acima de 120, classes gigante/colossal de `KillXp`; filhotes não contam) arrebentam na hora.
  - Nadador dentro da água, bicho desmaiado ou já amarrado: não pega, a boleadeira cai.
  - Jogador (com PvP) lentidão V por 3 s; bicho do Minecraft lentidão V por 6 s.
  - Nunca os bichos do próprio arremessador; os domados de outro jogador só com PvP ligado.
  - Errou: cai onde bateu. Pegou: cai quando o bicho se solta, metade das vezes (na outra a tira arrebentou).
- Estado salvo e sincronizado em `DinosaurEntity` (`isEntangled`, `entangle`, NBT `Entangled`); `FlyingDinosaur` desliga
  a sustentação e o voo montado enquanto amarrado.
- Visual: em voo o modelo 3D `item/bola_thrown` (3 pedras de 3 px em tiras de meio pixel, girando deitado,
  `client/BolaRenderer`); no bicho, `item/bola_wrap` (um laço da largura do corpo nas pernas, ou nas asas, com as pedras
  penduradas) desenhado por `DinosaurRenderer`. Os dois são sobreposições do item ligadas pela propriedade
  `terrassic:bola` (`client/WeaponPoses.BOLA`). Arte: `BOLA` e `BOLA_PARTS` em `tools/spritegen/armas.py`.
- Receitas: 3 sílex + 2 linhas = 2; 3 sílex + 1 couro de qualquer dino (tag `terrassic:hides`) = 2.
- Sons: do Minecraft por enquanto (varrida, tridente, laço); sons próprios em espera (Rodrigo, 31/10).

## v1.1.1: 3D da zarabatana e da lança refeitos
Pedido do Rodrigo em 31/10/2026 (18:38Z): no F5 a zarabatana ficava grande e fora da boca; a lança ficava quebrada
ao ser erguida para o arremesso.
- Zarabatana vista de fora: `mixin/client/BlowgunMouthMixin` desenha o tubo a partir da cabeça, como o Minecraft faz
  com a luneta no olho, com o modelo `item/blowgun_mouth` (tubo em pé de 13,5 px, uns 0,85 bloco, e o bocal de couro
  na boca; pose "head" copiada da luneta). Altura da boca: `MOUTH_DROP` no mixin. A 1ª pessoa não mudou.
- Lança: modelo 3D refeito em pé, como o tridente vanilla (33 px, ponta para cima), com as poses do tridente na mão
  (`trident_in_hand`) e erguida para arremessar (`trident_throwing`, pela propriedade vanilla `throwing`). Como um
  elemento de modelo só vai de -16 a 32, a lança fica 16 px acima da geometria do tridente e as translações das poses
  descem o mesmo tanto (`_SPEAR_DISPLAY` em gen_resources). No ar e cravada, `ThrownSpearRenderer` deita a lança no
  sentido do voo com a base da ponta no ponto da entidade, como o tridente. Na hotbar segue o sprite, inclusive
  durante a carga do arremesso (`HeldSpearMixin`).

## v1.1.4: acabamento das armas
- **Dardo cravado:** o dardo da zarabatana fica espetado no bicho, e as flechas também (sílex, narcótica, comum). Cada um
  fica numa face de verdade do modelo, acompanha o osso na animação e aponta para dentro, com a pena para fora
  (`client/StuckProjectilesLayer`). Saem sozinhos com o tempo, um por vez, como as flechas no jogador. Dardos na conta
  `DinosaurEntity#getStuckDarts`; flechas na conta de flechas do Minecraft. Até 12 de cada aparecem.
- **Dose que não se perde:** um segundo dardo ou flecha narcótica no meio segundo de invencibilidade depois de um golpe
  antes quicava e perdia a dose. Agora a dose entra, e o dardo fica cravado (`DinosaurEntity#hurt`).
- **Espirais mais fortes:** o dobro de espirais violeta, um pouco mais vivas, mais faíscas de bruxa em cima do bicho;
  bichos grandes ganham mais.
- **Dispensador:** atira flecha de sílex, flecha narcótica e dardo como a flecha comum (`item/WeaponDispensing`). Tiro de
  dispensador é fraco: a flecha narcótica leva uns 37% de uma puxada cheia, o dardo a dose de um sopro curto.
