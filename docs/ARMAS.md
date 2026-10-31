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

## Passo 2: arco de caça e flechas (a fazer)
## Passo 3: lança 3D, estocada no toque rápido (a fazer)
