# modelgen — gerador procedural dos dinossauros

Cada espécie é descrita em Python, em `species/<especie>.py`. A descrição tem três partes:

- **Ossos e cubos**: as articulações são dadas na pose final (ex.: posição do quadril, do joelho e do tornozelo). O `rig.chain()` calcula sozinho os cubos e as rotações.
- **Paleta e padrões**: as texturas são pintadas em 3D, então listras e manchas continuam de um cubo para o outro. Veja `paint.py`.
- **Animações**: são curvas (seno, keyframes) amostradas em keyframes catmull-rom.

O `build_all.py` monta cada modelo **dentro do Blockbench de verdade** (headless, via Playwright), pinta a textura, cria as animações e exporta:

- `art/<especie>/<especie>.bbmodel`, o projeto editável no Blockbench
- `common/src/main/resources/assets/terrassic/{geo,animations,textures}/entity/<especie>.*`
- `art/<especie>/previews/*.png`, os renders de cada vista e das poses das animações

## Rodar

```bash
pip install playwright pillow numpy && playwright install chromium

# Blockbench web local
git clone --depth 1 https://github.com/JannisX11/blockbench.git ~/bb
cd ~/bb && npm install --ignore-scripts && node build.js --target=web
python3 -m http.server 8123 &           # serve o Blockbench em http://localhost:8123

cd ~/projects/Terrassic/tools/modelgen
python3 build_all.py                    # todos
python3 build_all.py triceratops        # só um
python3 contact.py ../../art/preview_sheet.png front34 side back34
```

### Sem Blockbench (backend Python)

`pybench.py` faz o mesmo trabalho do Blockbench headless em Python puro (só precisa de `pillow` e `numpy`):
monta os cubos, calcula o UV, exporta `.geo.json`, `.animation.json` e um `.bbmodel` que abre no Blockbench,
e renderiza as prévias. O `build_all.py` usa ele sozinho quando não há Blockbench em `localhost:8123`, ou com `--py`:

```bash
python3 build_all.py --py pteranodon
python3 checks.py        # confere que o backend Python reconstrói os 12 modelos da v0.2 igualzinho (geo, animações e textura)
```

> Rodar o gerador **sobrescreve** os `.bbmodel` e os assets do mod. Se você editou algum modelo à mão no Blockbench, faça backup antes ou gere só as outras espécies.

## Convenções (iguais às do Blockbench e do GeckoLib)

- 16 px = 1 bloco, Y para cima, chão em y = 0, o animal olha para o **norte (-Z)**.
- `+X` de rotação levanta o que aponta para frente e balança para frente o que aponta para baixo.
- O osso `head` é controlado pelo jogo (olhar). Por isso a cabeça é nivelada pelo osso filho `skull`.
- Os tamanhos dos cubos precisam ser inteiros (box UV). Para ajuste fino, use `inflate`.

## Macho, fêmea e sela

- `m.sexes = {"male": {...}, "female": {...}}` sobrescreve cores da paleta para cada sexo; o gerador pinta
  `<especie>_male.png` e `<especie>_female.png` e guarda as duas no `.bbmodel`.
- Ossos `male_display` / `female_display` só aparecem no jogo para aquele sexo (ex.: crista maior do macho).
- `add_saddle(...)` cria o osso `saddle`, mostrado só quando o dinossauro está selado.
- `sit_tracks(...)` / `quad_sit(...)` criam a animação de descanso (`sit`).

## Arquétipos

Para centenas de espécies, cada família tem **um rig compartilhado** (arquétipo) e cada espécie vira uma ficha curta
(paleta, cabeça, crista, padrão de pele), com cerca de 20 linhas. Corpo, pernas, cauda, sela e animações vêm do arquétipo.

- Todos os dinossauros terrestres têm `knocked_out` via `rig.add_knockout(m)` (os quadrúpedes pelo `quad_anims`).
- `species/hadrosaur.py`: hadrossauros (bico de pato). Usado por `parasaurolophus.py` e `maiasaura.py`.
- `species/large_theropod.py`: terópodes grandes. Usado por `tyrannosaurus.py` e `spinosaurus.py` (vela e cauda-remo entram por ganchos `after_torso`/`after_tail`).
- Todo arquétipo traz a animação `knocked_out` (deitado de lado, para a domesticação por nocaute; ver `docs/DOMESTICACAO.md`).
  A pose usa `rig.add_knockout(m, lift=..., shift=...)`, com altura e deslocamento em fração da altura do quadril.
- O tamanho no jogo vem da escala do renderizador (`SIZES` em `tools/javagen/gen_species.py`), então o rig fica num tamanho só.
- `species/pterosaur.py`: pterossauros (asa em 3 ossos + membranas, voo, andar de quatro com a asa dobrada, `sit` e
  `knocked_out` com as asas recolhidas ao corpo). Usado por `quetzalcoatlus.py`, `hatzegopteryx.py` e `pteranodon.py`
  (migrado na fase 40 sem mudar a geometria: `checks.py pteranodon` dá geo = e textura =).
- Ordem de produção (docs/ROADMAP.md): uma era por vez, na ordem da fila; o arquétipo nasce quando a primeira espécie
  da fila precisa dele. Próximos: réptil marinho, plesiossauro, crocodilo, ceratopsiano, saurópode, anquilossauro.
- **Cada modelo é único**: o arquétipo é só o esqueleto e as animações base; corpo, cabeça, proporções, pele e
  detalhes são da espécie (ganchos `body_parts`, `leg`, `pattern`, `attack`, `after_*`).

## Conferir uma pose sem compilar

```bash
python3 preview.py quetzalcoatlus idle sit knocked_out walk:0.25 fly:0.25   # folha quetzalcoatlus_pv.png (lado, 3/4, frente, cabeça)
python3 posecheck.py quetzalcoatlus idle sit knocked_out                    # extensão de cada cubo; marca o que afunda no chão
```

A folha de prévia centraliza a câmera em cada pose e escreve o ponto mais baixo (`lowest y`): 0 = pés no chão;
negativo = afundou; positivo nas poses de chão = flutuando. Use antes de rodar o `build_all.py`.

## Adicionar uma espécie

1. Se a família já tem arquétipo, copie uma ficha (ex.: `maiasaura.py`) e mude a paleta, a cabeça e a crista. Se não tem, copie o arquivo mais parecido: `smalltheropod.py` + `velociraptor.py`/`gallimimus.py`/`dilophosaurus.py` para bípedes, `tyrannosaurus.py`/`spinosaurus.py` para terópodes grandes, ou `quadruped.py` + `brachiosaurus.py` para quadrúpedes; `pterosaur.py` + `quetzalcoatlus.py` para pterossauros.
2. Ajuste as proporções a partir das medidas reais (comprimento, altura do quadril, crânio).
3. Adicione o nome em `ALL`, no `build_all.py`, e rode o gerador.
4. No mod: adicione a espécie nas tabelas de `tools/javagen/gen_species.py` (`SPECIES`, `SIZES`, `GUIDE`, `WORLD`) e em `gen_resources.py`, e rode os dois. Os registros em `ModEntities`, `ModItems`, `ModBlocks`, `TerrassicClient` e `ModSpawns` são gerados (entre os marcadores GENERATED). Desenhe o ovo gerador em `tools/spritegen/sprites.py`.
