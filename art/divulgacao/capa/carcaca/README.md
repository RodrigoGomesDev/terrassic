# Capa Carcaça na praia

Aprovada pelo Rodrigo em 31/10/2026. Num dia de sol, um bando de Velociraptors come um Pteranodonte morto na areia,
de asas abertas sobre uma mancha de sangue. Um deles sobe na carcaça e grita, outro chega correndo pela esquerda.
O mar fica atrás e o sol fica atrás da câmera.

Render puro no Blender (Cycles), sem IA e sem retoque. Os bichos são os modelos do jogo (Velociraptor v3 e
Pteranodonte v3, com geo, textura e animação lidos direto dos arquivos do mod), e o cenário é feito com as texturas de
bloco do mod.

| Arquivo | O que é |
|---|---|
| `terrassic_capa_en_us_1920x1080.png` | Capa com o slogan em inglês |
| `terrassic_capa_pt_br_1920x1080.png` | Slogan em português |
| `terrassic_capa_es_es_1920x1080.png` | Slogan em espanhol |
| `terrassic_capa_sem_titulo_1920x1080.png` | A cena sem letreiro (galeria, posts, fundos) |

O letreiro é o Degraus (acabamento pedra) a 83% do tamanho padrão, em cima à direita. Cada capa põe o letreiro num
lugar diferente (pedido do Rodrigo): na Espreita (v4) ele fica em cima à esquerda.

## Como gerar de novo

Precisa do Blender como módulo Python (`pip install bpy pillow numpy`, Python 3.13). Cerca de 15 minutos em 4 núcleos.

```
cd tools/capagen
SAMPLES=96 SIZE=1920,1080 python3 -B cenas2.py praia_carcaca --out /tmp/capa   # -> /tmp/capa/praia_carcaca.png
python3 -B capas2.py /tmp/capa/praia_carcaca.png praia_carcaca /tmp/capa --langs
```

A pose do Pteranodonte morto fica em `CARCASS` no `cenas2.py`: a animação de planar com o pescoço, a cabeça e as pernas
dobrados, deitado na areia.
