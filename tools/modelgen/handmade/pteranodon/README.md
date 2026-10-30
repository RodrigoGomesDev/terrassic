# Pteranodonte: modelo feito à mão

Segundo modelo do padrão do T. rex (30/10/2026). O Rodrigo aprovou o visual da segunda volta às 00:54Z. São 103 cubos
desenhados um a um, com UV por face (1 texel = 1 pixel do Minecraft). A pele de 256 x 128 é pintada pela forma, para
macho e fêmea. A membrana da asa é feita de painéis com 1 px de espessura que dobram junto com os ossos, e há 27
animações próprias.

- `ptera.py`: os cubos (corpo, cabeça, crista do macho e da fêmea, asas, painéis da membrana, pernas e sela), as
  paletas e a pintura. `separate_coplanar()` mantém a regra de zero faces coplanares.
- `proto.py`, `skin.py`, `geo.py`: motor do modelo (o mesmo do T. rex, com escala por osso).
- `anim2.py`: motor de animação, que exporta também o canal `scale` (a membrana dobra por escala no eixo z).
- `pteranim.py`: postura no chão de quatro (IK com mãos e pés no chão), andar, voar, planar, decolar e pousar.
- `pteranims2.py`: as outras 21 animações.
- `build.py`: grava o geo, as animações, as duas texturas e a linha do pteranodonte em `art/build_report.json`. A
  tabela `ANIMS` diz quando o jogo toca cada animação.

```bash
python3 -B tools/modelgen/handmade/pteranodon/build.py     # demora: as poses de chão usam IK
python3 -B tools/javagen/gen_species.py                     # depois, se o tamanho do modelo mudou (culling)
```

Igual ao T. rex: o GeckoLib desenha as faces leste e oeste com o u invertido. `proto.geo_json` já inverte, e a prévia
deve ser feita sempre a partir do arquivo exportado.

## Ovo e sela

- `tools/spritegen/ptera_extras.py` faz duas coisas:
  - o ninho, com dois ovos de casca de couro meio enterrados na areia, em 3 fases (amassado, rasgado com a ponta do
    bico aparecendo) e entrando em `CUSTOM_EGGS`;
  - a sela própria `pteranodon_saddle`.
- O ovo de spawn novo é o `pteranodon()` de `tools/spritegen/egg_designs.py`, visto de frente como o do T. rex.
