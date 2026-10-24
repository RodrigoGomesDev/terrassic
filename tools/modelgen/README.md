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

## Adicionar uma espécie

1. Copie o arquivo mais parecido: `smalltheropod.py` + `velociraptor.py`/`gallimimus.py`/`dilophosaurus.py` para bípedes, `tyrannosaurus.py`/`spinosaurus.py` para terópodes grandes, ou `quadruped.py` + `parasaurolophus.py`/`brachiosaurus.py` para quadrúpedes.
2. Ajuste as proporções a partir das medidas reais (comprimento, altura do quadril, crânio).
3. Adicione o nome em `ALL`, no `build_all.py`, e rode o gerador.
4. No mod: adicione a espécie na tabela de `tools/javagen/gen_species.py` e em `gen_resources.py`, rode os dois, registre em `ModEntities`, `ModItems`, `ModBlocks`, `TerrassicClient` e `ModSpawns`, e desenhe o ovo gerador em `tools/spritegen/sprites.py`.
