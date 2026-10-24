# tools/texpack: pacotes de textura por era

Gera os pacotes de recursos embutidos no mod (`common/src/main/resources/resourcepacks/<era>/`), que trocam texturas
do vanilla pela cara da era. Desenho completo em `docs/TEXTURAS_ERA.md`.

```
python3 build.py           # escreve o pacote do Cretáceo Superior + prévias em art/texpack/previews/
python3 build.py --check   # só confere a qualidade, não escreve nada
```

O `build.py` falha se uma textura ficar a mais de 14 de brilho ou 20 de contraste do bloco vanilla que ela troca.

```
```

| Arquivo | O que faz |
|---|---|
| `tex.py` | Motor: ruído e Voronoi que emendam (o 16x16 é um toro), luz de cima à esquerda, quantização por quantis numa rampa curta, limpeza de pixels soltos, rampas com desvio de matiz, conferências |
| `stamps.py` | Detalhes desenhados (degraus, pintas, seixos, folhas de grama, raízes) postos por ruído azul, e a base calma de um tom principal |
| `fit.py` | Ajuste de paleta: acha a rampa cujo brilho médio e contraste batem com a meta, com o matiz e a saturação da era |
| `targets.py` | A régua: brilho médio, contraste p95-p5 e salto entre vizinhos de cada bloco vanilla, medidos no Mac (só números; nenhum pixel do vanilla está no projeto) |
| `cretaceo.py` | As receitas do Cretáceo Superior (pedra, pedregulho, terra, grama, cascalho, areia, arenito, argila, lama...) e as paletas |
| `preview.py` | Folha de prévia (grande + mosaico 3x3) e diorama isométrico com a luz das faces do Minecraft |
| `vanilla.py` | Os números de cada textura 16x16 do vanilla 1.20.1 medidos no Mac (só números): `target(nome)` |
| `materials.py` | Materiais: nome -> referência vanilla + nosso matiz/saturação/desvio/ajuste da era. Vanilla e do mod (âmbar, resina, osso, giz, laterita, couros, palha...) |
| `api.py` | O motor em quatro chamadas: `paint(tons, "amber", alpha=...)`, `palette`, `check`, `goal` |
| `stamps.py`, `fit.py`, `targets.py` | Base calma + detalhes por ruído azul; paleta ajustada às metas; metas do lote 1 e `measure` |
| `woods.py` | Cascas (8 estilos), anéis fora do centro, tronco descascado, tábuas lascadas; `plates`, `wave`, `draw_line` |
| `leaves.py` | Copas por formas de folha da espécie, em duas camadas, com furos de verdade |
| `plants.py`, `plantart.py` | Plantas em pixel art à mão (grades de texto) pintadas pelo ajuste: cavalinhas, samambaias, cipó |
| `workshop.py` | Bancada, fornalha e tocha |
| `masonry.py` | Construção e chão: fiadas de pedra (musgo, rachaduras, amonite entalhada), tijolos, musgo, terra arada, caminho com pegada, palha, neve, cana, vitória-régia |
| `rocks.py` | Rochas do vanilla (cristais, lapilli, lâminas) e os 16 minérios em veios sobre a pedra e a ardósia do pacote |
| `build.py` | Tabela textura do vanilla -> desenho, blockstates com variantes sorteadas, `pack.mcmeta`, `pack.png` e conferências |
| `pack_lang.py` | Nome e descrição de cada pacote nos 3 idiomas (o `gen_resources.py` junta no lang do mod) |

Para os blocos do próprio mod (thread de blocos, `blocos.py`): desenhe o mapa de tons com `tex`/`stamps`/`woods`,
pinte com `api.paint(tons, material)` e confira com `api.check`. Material novo = uma linha em `materials.py`
apontando para o parente vanilla mais próximo. Os PNGs só são regravados quando os pixels mudam.

Regras de arte (as mesmas para todas as eras):
- 16x16, emenda sem costura, no máximo ~8 tons por material, aglomerados em vez de ruído pixel a pixel.
- Sombra mais fria e saturada, luz mais quente; luz sempre de cima à esquerda.
- Brilho e contraste perto do bloco vanilla equivalente, para os dois conviverem no mesmo mundo.
- Tudo procedural e autoral. Nenhum pixel vem de textura de terceiros, nem do vanilla.

Para mudar uma textura: ajuste a receita ou a semente em `cretaceo.py`/`build.py`, rode `build.py` e olhe
`art/texpack/previews/cretaceo_texturas.png` e `cretaceo_diorama.png` antes de entregar.
