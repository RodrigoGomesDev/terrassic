# Capa Caçada — edição 2

Reformulação solicitada por Rodrigo em 26/10/2026 para CurseForge e Modrinth.

- `terrassic_capa_en_us_1920x1080.png`: versão principal; mantém o slogan em inglês conforme a decisão anterior.
- `terrassic_capa_pt_br_1920x1080.png` e `terrassic_capa_es_es_1920x1080.png`: alternativas traduzidas.
- `cacada_sem_titulo_1920x1080.png`: mesma correção de cor, sem marca e slogan.
- Pacote: `../terrassic_capa_lojas_v2.zip`.

Letreiro atual do menu, Sedimento, paleta Java Âmbar e Basalto. Céu em tons de crepúsculo,
laranja menos dominante e sombras com mais detalhe. A cena é o render anterior sem título:
não houve síntese de imagem, alteração da geometria, remoção de objetos nem regeneração dos modelos.
Isso preserva a composição e os modelos representados naquele render; não certifica que todos os
assets do render antigo correspondam byte a byte aos modelos atuais. É arte promocional, não screenshot.

Gerador: `build/menu-render-venv/bin/python -B tools/capagen/store_cover.py`.
O manifest registra hashes da fonte, marca, paleta, tipografia e quatro PNGs.
Originais e capas anteriores preservados. Não substitui fundos do menu, ícone nem publica nas lojas.
PNG inglês inspecionado visualmente; integridade dos quatro PNGs e conteúdo do ZIP conferidos.
Acabamento aguarda revisão visual do Rodrigo.
