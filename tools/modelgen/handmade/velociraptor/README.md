# Velociraptor: modelo feito à mão

Terceiro modelo do padrão do T. rex (30/10/2026), depois do T. rex e do Pteranodonte. O Rodrigo aprovou a v3 às 20:45Z,
depois de medida contra o T. rex e o Pteranodonte. São 86 cubos desenhados um a um (78 do animal e 8 do arreio de caça),
com UV por face (1 texel = 1 pixel do Minecraft). A pele tem 256 px de largura e é pintada pela forma, para macho e
fêmea:

- penas em células alternadas e barras escuras com a borda de ferrugem;
- reflexo azul-aço como cor de destaque (iridescência, como no Microraptor);
- olho âmbar de 5 x 4 px e cabeça de 14 peças;
- três dedos com garra, dois dedos no chão e a garra em foice levantada;
- penas da asa em duas camadas, leque na cauda e crista na nuca.

As animações são 28.

- `raptor.py`: os cubos, as paletas (macho castanho com azul-aço, fêmea cinza com reflexo ardósia), a pintura e o
  arreio (osso `saddle`, que o DinoGeoModel só mostra com o arreio posto). `separate_coplanar()` mantém a regra de zero
  faces coplanares. As cristas ficam em x levemente diferentes (-0.15, 0.05, -0.05, 0.15) para não brigarem quando o
  pescoço dobra. O braço fica 0.3 px para fora da perna, para nenhuma face do braço ficar no mesmo plano de uma face
  da perna.
- Os planos sem espessura (crista, dentes, penas da asa, leque da cauda) têm uma face só (`single_face_planes`): o
  GeckoLib desenha sem cortar a face de trás, então o plano já aparece dos dois lados, e com duas faces elas brigavam
  no mesmo plano (visto no jogo no leque da cauda, 30/10).
- `proto.py`, `skin.py`, `geo.py`: motor do modelo (o mesmo do T. rex e do Pteranodonte).
- `anim2.py`: motor de animação. O `solve_leg` tem limite suave no giro da coxa (`THIGH_RANGE`): sem ele, a coxa
  virava e aparecia por cima das costas na corrida e no andar agachado.
- `raptanims.py`: as 28 poses. Desenhadas na escala da v2b e multiplicadas por K = 1.64.
- `build.py`: grava o geo, as animações, as duas texturas e a linha do velociraptor em `art/build_report.json`. A
  tabela `WHEN` diz quando o jogo toca cada animação.

```bash
python3 -B tools/modelgen/handmade/velociraptor/build.py   # demora: as pernas usam IK em todo quadro
python3 -B tools/javagen/gen_species.py                     # depois, se o tamanho do modelo mudou (culling)
```

Igual ao T. rex: o GeckoLib desenha as faces leste e oeste com o u invertido. `proto.geo_json` já inverte, e a prévia
deve ser feita sempre a partir do arquivo exportado.

Escala: 48 px por metro (100 px de comprimento). Com MODEL_SCALE 0.5, o animal aparece com 3,1 m, 1,5x o real (2,07 m).
Foi escolha do Rodrigo, uma exceção como a do Pteranodonte, para ele ameaçar de verdade ao lado do jogador.

## Ovo e arreio

- `tools/spritegen/rapt_extras.py` faz duas coisas:
  - o ninho: uma cova rasa na areia do deserto com seis ovos compridos, azul-esverdeados e pintados, em pares e de pé,
    em 3 fases (rachado, e furado com o focinho e o dente de ovo do filhote). Entra em `CUSTOM_EGGS`.
  - o item `velociraptor_harness` (arreio de caça): um animal de 20 kg não carrega ninguém. O arreio dá armadura e
    não serve para montar.
