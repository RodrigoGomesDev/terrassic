# T. rex: modelo feito à mão

O T. rex não sai mais do arquétipo `species/large_theropod.py`. Ele é o primeiro modelo do padrão novo do estudo de
29/10/2026: cubos desenhados um a um, UV por face (1 texel = 1 pixel do Minecraft), pele pintada pela forma e 28
animações próprias, com os pés presos no chão por IK.

- `rex2.py`: os 78 cubos (68 do corpo e 10 da sela), a paleta do macho e da fêmea, e a pintura.
- `proto.py`, `skin.py`, `geo.py`: motor do modelo (empacotar UV, pintar, exportar, ler e renderizar o geo).
- `anim2.py`, `rexanim.py`, `rexanims.py`: motor de animação e as 28 animações. `ANIMS` diz quando o jogo toca cada uma.
- `roar_wave.py`: os 8 quadros da onda no ar do rugido alto (partícula `terrassic:roar_wave`).
- `build.py`: grava o geo, as animações, as duas texturas, a partícula e a linha do T. rex em `art/build_report.json`.

```bash
python3 -B tools/modelgen/handmade/tyrannosaurus/build.py     # ou: python3 build_all.py tyrannosaurus
python3 -B tools/javagen/gen_species.py                        # depois, se o tamanho do modelo mudou (culling)
```

Atenção: o GeckoLib desenha as faces leste e oeste com o u invertido em relação a uma leitura ingênua do UV.
`proto.geo_json` já inverte o u nessas faces, e `geo.load_geo` lê o arquivo do jeito que o jogo desenha. Faça a
prévia sempre a partir do arquivo exportado.

O comportamento que usa essas animações fica em `entity/ApexTheropod.java` e `entity/ai/ApexBiteGoal.java`.
