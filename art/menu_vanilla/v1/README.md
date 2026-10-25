# Fundos com os modelos originais — proposta para validação

Direção corrigida pelo Rodrigo em 25/10/2026: cenas e luz cinematográfica agradaram, mas os animais precisam ser
os originais e o resultado precisa parecer mais Minecraft vanilla. As imagens de `art/menu_ia/v1/` não foram aprovadas.

Estas propostas usam Blender Cycles, sem geração de imagem por IA nem reconstrução artística dos animais:

- `confronto.png`: T. rex e Triceratops se enfrentando numa clareira.
- `nevoa.png`: T. rex caminhando pela mesma floresta, como alternativa tranquila para a galeria.

Prévia de estilo em 960×540, 32 amostras. Não é captura do Minecraft nem demonstração do combate implementado.
Os animais usam os `.geo.json`, `.animation.json` e PNGs efetivamente entregues em `assets/terrassic`.
A conversão de coordenadas é conferida por round-trip: todos os cubos, pivôs, rotações, UVs e inflations
reexportados devem ser idênticos à geometria do jogo. Os hashes dos arquivos usados ficam no JSON de cada cena.
Texturas de terreno e vegetação são lidas do cliente vanilla 1.20.1 instalado, em memória; não se distribui aqui
o JAR nem um pacote de texturas extraídas. O tamanho dos blocos permanece 1 metro, com filtros de textura nearest.

## Reprodução

Python 3.11 e ambiente isolado, sem alterar o sistema:

```sh
python3.11 -m venv build/menu-render-venv
build/menu-render-venv/bin/python -m pip install -r tools/menugen/requirements-render.txt
build/menu-render-venv/bin/python -B tools/menugen/menu_vanilla.py \
  --client-jar /caminho/minecraft-client.jar --width 960 --samples 32 --scene confronto
build/menu-render-venv/bin/python -B tools/menugen/menu_vanilla.py \
  --client-jar /caminho/minecraft-client.jar --width 960 --samples 32 --scene nevoa
```

Estado: aguardando validação do estilo por Rodrigo. Não substitui os quatro fundos ativos e não altera o HUD
durante a partida, a marca ou os modelos. Depois da escolha: render final em 1920×1080 e conferência do recorte,
das legendas nos três idiomas e da leitura dos botões/letreiro nas escalas reais da interface.

As duas execuções terminaram com sucesso; round-trip de geometria passou para os 139 cubos de cada animal.
Hashes das fontes e das duas saídas foram reconferidos após renderizar. Integridade do projeto passou com
59 espécies, 4.341 JSONs e 1.845 chaves nos três idiomas. Não foi executado teste visual da interface no jogo.
