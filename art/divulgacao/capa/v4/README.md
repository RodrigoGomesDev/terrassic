# Capa Espreita (v4)

Aprovada pelo Rodrigo em 30/10/2026. Um T. rex espreita de cabeça baixa entre as samambaias de uma floresta
de sequoias na neblina da manhã. Um facho de sol entra por uma fresta da copa e cai no rosto dele.

Render puro no Blender (Cycles), sem IA e sem retoque. O T. rex é o modelo do jogo (`tyrannosaurus.geo.json`,
textura e animação `stalk` do mod, lidos direto dos arquivos), e o cenário é feito com as texturas de bloco do mod.

| Arquivo | O que é |
|---|---|
| `terrassic_capa_en_us_1920x1080.png` | Capa principal (slogan em inglês) |
| `terrassic_capa_pt_br_1920x1080.png` | Slogan em português |
| `terrassic_capa_es_es_1920x1080.png` | Slogan em espanhol |
| `terrassic_capa_sem_titulo_1920x1080.png` | A cena sem letreiro (galeria, posts, fundos) |
| `terrassic_icone_512.png` | Ícone: a cabeça do T. rex recortada da mesma cena |

O letreiro é o Degraus (acabamento pedra) a 83% do tamanho padrão, pedido do Rodrigo.

## Como gerar de novo

Precisa do Blender como módulo Python (`pip install bpy pillow numpy`, Python 3.13). Cerca de 25 minutos em 4 núcleos.

```
cd tools/capagen
SAMPLES=96 SIZE=1920,1080 python3 -B cenas2.py espreita --out /tmp/capa   # -> /tmp/capa/espreita.png
python3 -B capas2.py /tmp/capa/espreita.png espreita /tmp/capa --langs     # capas nos três idiomas
```

O ícone é o recorte quadrado de raio 250 px em volta de (1170, 510) da cena, reduzido para 512.

`cenas2.py` monta as cenas com os modelos do jogo (`geckomesh.py`). `blend.py` ganhou o que um shader pack faz por cima
do Minecraft: relevo por pixel nas texturas, folhas que deixam o sol passar, brilho leve na pele dos bichos, facho de
sol (luz spot) que aparece na neblina, neblina com ondulação e nuvens volumétricas. Tudo é ligado pelo "look" de cada
cena, e as cenas antigas de `cenas.py` não mudam.
