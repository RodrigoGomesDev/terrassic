# Capa Caçada — laranja, shader e chuva de estrelas

Pedido do Rodrigo em 26/10/2026: manter o laranja, melhorar a iluminação com aparência de shader,
adicionar chuva de estrelas; nuvens e estrelas com mais aparência de Minecraft e logo evidente.

Três capas 1920×1080 com slogan em inglês (principal), português e espanhol. Logo original do jogo
composto separadamente, sem letras sintetizadas. ZIP em `../terrassic_capa_lojas_v3.zip`.

O fundo foi editado com a ferramenta integrada imagegen, em três passos: iluminação/meteoros,
sol quadrado, nuvens retangulares/meteoros pixelados. `cena_ia_original.png` preserva o resultado nativo
1672×941; entrega redimensionada para 1920×1080. Não é render nativo em 4K nem screenshot, e não instala
shader no jogo. Os modelos são referência da cena original; a preservação exata de geometria após
edição raster por IA não é certificada. Revisão visual do fundo e capa inglesa executada; aprovação
estética do Rodrigo pendente. v2, menu e marca local preservados.

Prompt final (ferramenta integrada, referência: edição com sol quadrado):

> Edit this image. Change only clouds and shooting stars; preserve dinosaurs, blocky models, ground,
> plants, square sun, orange shader lighting and framing. Replace detailed clouds with large simple
> rectangular voxel slabs, square corners and square cutouts, like vanilla Minecraft clouds lit orange.
> Replace realistic meteors with around seven Minecraft pixel shooting stars, bright square cores and
> short staircase diagonal trails of discrete square amber particles. No smooth fire tails. Upper-right
> background; upper-left quiet for the original logo. No text or logo. Preserve dinosaur silhouette and
> pixel textures. Polished warm orange sunset, cinematic Minecraft shader lighting, wide 16:9.

Compositor reproduzível: `build/menu-render-venv/bin/python -B tools/capagen/store_cover_v3.py`.
O manifest registra origem, tamanho nativo, redimensionamento e hashes. Quatro PNGs (fundo + três capas)
e conteúdo do ZIP conferidos; nenhum código ou recurso do mod alterado.
