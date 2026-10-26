# Pranchas para CurseForge e Modrinth — 26/10/2026

Atualização das duas imagens antigas anexadas pelo Rodrigo: céus/mares e predadores.
Seis PNGs RGB de 1920×1080, com fundo Basalto, títulos em Âmbar, texto em Pedra/Osso,
tipografia Sedimento/Entalhe e o letreiro Degraus atualmente usado no menu.

- `sky_en_us_1920x1080.png` e `apex_en_us_1920x1080.png`: versões em inglês para as páginas internacionais.
- Os mesmos temas em `pt_br` e `es_es`: português e espanhol.
- Pacote completo: `../terrassic_cartazes_lojas.zip`.

Os animais foram renderizados dos `.geo.json`, animações e texturas originais do mod. A conversão
de coordenadas é verificada por round-trip. Não houve pintura ou reconstrução dos animais por IA.
As medidas vêm da tabela `SIZES` do projeto: envergadura para os pterossauros, comprimento nos demais.
Os modelos são ampliados individualmente para leitura; a prancha informa que as escalas visuais diferem.

O texto antigo sobre domesticar predadores somente a partir do ovo foi removido porque não representa
o sistema atual de nocaute. As artes são pranchas promocionais de modelos, não capturas do jogo.
Nenhuma imagem foi publicada automaticamente nas lojas ou aplicada sobre a arte da frente de marca.

## Reprodução e conferência

```sh
build/menu-render-venv/bin/python -B tools/capagen/store_cards.py
```

O gerador usa a paleta Java e o letreiro empacotado como fontes únicas. Prompts não se aplicam:
render e composição são feitos pelo código do projeto. Hashes das fontes e das seis saídas,
medidas e contagem de cubos ficam em `manifest.json`. Originais antigos preservados em `referencias/`.
