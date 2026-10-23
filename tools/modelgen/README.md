# modelgen — gerador procedural dos dinossauros

Cada espécie é descrita em Python, em `species/<especie>.py`. A descrição tem três partes:

- **Ossos e cubos**: as articulações são dadas na pose final (ex.: posição do quadril, do joelho e do tornozelo). O `rig.chain()` calcula sozinho os cubos e as rotações.
- **Paleta e padrões**: as texturas são pintadas em 3D, então listras e manchas continuam de um cubo para o outro. Veja `paint.py`.
- **Animações**: são curvas (seno, keyframes) amostradas em keyframes catmull-rom.

O `build_all.py` monta cada modelo **dentro do Blockbench de verdade** (headless, via Playwright), pinta a textura, cria as animações e exporta:

- `art/<especie>/<especie>.bbmodel`, o projeto editável no Blockbench
- `common/src/main/resources/assets/primalera/{geo,animations,textures}/entity/<especie>.*`
- `art/<especie>/previews/*.png`, os renders de cada vista e das poses das animações

## Rodar

```bash
pip install playwright pillow numpy && playwright install chromium

# Blockbench web local
git clone --depth 1 https://github.com/JannisX11/blockbench.git ~/bb
cd ~/bb && npm install --ignore-scripts && node build.js --target=web
python3 -m http.server 8123 &           # serve o Blockbench em http://localhost:8123

cd ~/projects/PrimalEra/tools/modelgen
python3 build_all.py                    # todos
python3 build_all.py triceratops        # só um
python3 contact.py ../../art/preview_sheet.png front34 side back34
```

> Rodar o gerador **sobrescreve** os `.bbmodel` e os assets do mod. Se você editou algum modelo à mão no Blockbench, faça backup antes ou gere só as outras espécies.

## Convenções (iguais às do Blockbench e do GeckoLib)

- 16 px = 1 bloco, Y para cima, chão em y = 0, o animal olha para o **norte (-Z)**.
- `+X` de rotação levanta o que aponta para frente e balança para frente o que aponta para baixo.
- O osso `head` é controlado pelo jogo (olhar). Por isso a cabeça é nivelada pelo osso filho `skull`.
- Os tamanhos dos cubos precisam ser inteiros (box UV). Para ajuste fino, use `inflate`.

## Adicionar uma espécie

1. Copie o arquivo mais parecido: `smalltheropod.py` + `velociraptor.py` para bípedes pequenos, `tyrannosaurus.py` para bípedes grandes, ou `quadruped.py` + `triceratops.py` para quadrúpedes.
2. Ajuste as proporções a partir das medidas reais (comprimento, altura do quadril, crânio).
3. Adicione o nome em `ALL`, no `build_all.py`, e rode o gerador.
4. No mod, crie a classe da entidade e registre em `ModEntities`, `ModItems` e `PrimalEraClient` (e em `ModSpawns`, se for nascer no mundo).
