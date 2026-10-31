# Spinosaurus: modelo feito à mão

Quarto modelo do padrão do T. rex e o primeiro feito com o motor único (`../_engine`) e o molde do terópode grande.
O Rodrigo aprovou a proposta e o visual em 31/10/2026 às 03:44Z ("só tem que se atentar a bug de pixels").

- `spino.py`: 73 cubos, UV por face, pele de 256 x 256 para macho e fêmea. A vela e o remo da cauda são placas de 1 px
  com o contorno recortado na textura: a curva sai como linha de pixel, sem escada de cubos.
  Marcas: vela carmim que clareia até cor de osso no macho (ocre na fêmea), faixa escura passando pelo olho, barras
  escuras no remo da cauda. Escala: 16 px por metro como o T. rex, crânio 1,2x.
- `spinoanims.py`: as 26 animações do molde + 4 dele: `fish` (pesca no raso, o bote acerta aos 2,1 s), `display`
  (mostra a vela), `swipe` (garra do polegar, acerta aos 0,55 s) e `swim` (nada com a cauda).
- `build.py`: grava o geo, as animações, as duas texturas e a linha em `art/build_report.json`, e PARA (exit 1) se o QA
  falhar: coplanares, bugs de pixel ou pose fora do chão (medido também entre os quadros). `run` e `death` saem a 40
  quadros por segundo porque a 20 o pé e a rolagem passavam até 0,74 px do chão entre dois quadros.

```bash
python3 -B tools/modelgen/handmade/spinosaurus/build.py   # ~2,5 min
python3 -B tools/javagen/gen_species.py                     # culling pelo tamanho novo
```

Pesquisa (só medidas): Ibrahim et al. 2014 e 2020, Sereno et al. 2022, dal Sasso et al. 2005.
