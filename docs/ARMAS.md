# Armas (refação v1.1)

Pedido do Rodrigo em 31/10/2026: os dardos estavam feios e quase impossíveis de usar; quer armas com animações mais
dinâmicas, um arco mais bolado e uma lança melhor. Proposta aprovada ("pode continuar", 31/10 03:42Z):
https://claude.ai/artifact/79FSKssTmZofQTHUWtj4sw

Regra: só poses que o próprio Minecraft já tem (arco, tridente, chifre de cabra) e modelos 3D simples no estilo da
flecha e do tridente vanilla. Arte desenhada à mão pixel a pixel em `tools/spritegen/armas.py`.

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
## Passo 3: lança 3D, estocada no toque rápido (a fazer)
