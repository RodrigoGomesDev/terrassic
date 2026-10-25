# Divulgação com assets originais — prévias para revisão

Estas cenas usam Blender Cycles e os modelos, animações e texturas entregues no mod.
Não há geração/reinterpretação de dinossauros por IA. São renders externos, não screenshots
do Minecraft nem demonstração de um evento ou comportamento de gameplay.

## Cenas e legendas sugeridas

- `confronto.png`: **Cretáceo Superior — T. rex e Triceratops. Render ilustrativo com os modelos do Terrassic.**
- `jurassico.png`: **Fauna do Jurássico — Brachiosaurus e Stegosaurus. Render com modelos existentes;
  o capítulo do Jurássico continua planejado.**

English:

- **Late Cretaceous — T. rex and Triceratops. Illustrative render using Terrassic models.**
- **Jurassic fauna — Brachiosaurus and Stegosaurus. Render using existing models;
  the Jurassic chapter is still planned.**

## Conferência estrutural

O script `tools/menugen/menu_vanilla.py` verifica a conversão dos modelos por round-trip:
todos os cubos, pivôs, rotações, UVs e inflations devem corresponder ao `.geo.json` original.
Texturas e animações vêm dos recursos do jogo. Os JSONs das imagens registram hashes das fontes
e da saída, contagem de cubos e parâmetros de renderização.

Terreno e árvores usam coordenadas inteiras e faces de cubos 1×1×1; a auditoria verifica ambos.
Plantas usam os planos cruzados próprios do estilo Minecraft, não são sólidos deformados.
As texturas vanilla de 16×16 são lidas do cliente local; o JAR não é redistribuído.

Isso verifica a construção da cena. Não substitui revisão visual de pose, câmera, luz e legibilidade.
As cinco imagens de `../../periodos/v1/` foram reprovadas e não devem ser publicadas.
Não existem modelos entregues para representar fielmente todos os capítulos futuros; os demais
períodos ficam pendentes em vez de reutilizar criaturas inventadas.

## Reprodução

```sh
build/menu-render-venv/bin/python -B tools/menugen/menu_vanilla.py \
  --client-jar /caminho/minecraft-client.jar --width 1280 --samples 24 \
  --scene confronto --golden --out art/divulgacao/originais/v1
```

Repetir com `--scene jurassico` para a segunda cena. Modelos preservados; apenas iluminação,
posicionamento e câmera são definidos pelo render. Aprovação visual do novo estilo ainda pendente.

## Resultado desta execução

- confronto.png: 1280×720, 70156 blocos; modelos: tyrannosaurus (139 cubos), triceratops (139 cubos).
- jurassico.png: 1280×720, 70156 blocos; modelos: brachiosaurus (72 cubos), stegosaurus (144 cubos).

Duas saídas inspecionadas visualmente. Hashes das imagens e de todas as fontes reconferidos.
A construção dos blocos e a fidelidade dos modelos passaram; a apresentação ainda é uma prévia:
névoa e contraste exigem acabamento antes de selecionar material final para as lojas.
