# Galeria para as lojas — edição 2, 26/10/2026

Quatro temas refeitos com a identidade **Âmbar e Basalto**, modelos originais maiores,
iluminação frontal mais clara, tipografia própria e o letreiro Degraus do menu.
As primeiras pranchas e os arquivos da frente de marca foram preservados.

## Arquivos

Cada tema tem versões `en_us`, `pt_br` e `es_es`:

- `apex_*_1920x1080.png`: predadores, com T. rex em destaque e três espécies complementares.
- `sky_*_1920x1080.png`: céus e mares, com pterossauros e répteis marinhos.
- `herd_*_1920x1080.png`: manadas e titãs, Argentinosaurus em destaque e quatro herbívoros.
- `catalog_*_3840x2160.png`: catálogo completo, **59 espécies**, em 4K para preservar detalhes e nomes.
- `catalog_*_1920x1080.png`: versão reduzida do catálogo.
- `../terrassic_cartazes_lojas_v2.zip`: os 15 PNGs, este guia e o manifesto.

Use os arquivos `en_us` nas páginas internacionais ou escolha o idioma da página.
São pranchas de apresentação dos modelos, renderizadas fora do Minecraft. Não são screenshots.
Não houve publicação automática nas lojas.

## Fidelidade e texto

Os números **59 espécies e 32 montarias** foram conferidos na tabela de espécies atual.
O total de montarias se refere ao elenco completo do mod. O catálogo inclui também as espécies
jurássicas já presentes, por isso seu cabeçalho não identifica todo o elenco como Cretáceo Superior.

Cada modelo vem dos geo, animações e texturas efetivamente empacotados. O round-trip verifica
todos os cubos, pivôs, rotações, UVs e inflations. As pranchas mostram machos; os arquivos de
textura das fêmeas também foram conferidos. Nenhum animal foi reconstruído ou pintado por IA.
Modelos aparecem em escalas diferentes para leitura, como indicado no rodapé; medidas usam a tabela do projeto.
A iluminação não altera os PNGs de textura nem a geometria do mod.

Os títulos, textos e dados mantêm português, inglês e espanhol em paridade. A frase antiga de
domesticação apenas pelo ovo continua removida. Os originais antigos adicionais foram preservados em `referencias/`.

## Reprodução

```sh
build/menu-render-venv/bin/python -B tools/capagen/store_cards_v2.py
```

Cache de renders em `build/store-card-cache/v2/`, invalidado por fonte do render, geometria,
animação, texturas e resolução. Composição feita pelo código do projeto; prompts não se aplicam.
O manifesto registra as fontes, contagens e hashes de cada PNG. A aprovação do acabamento visual fica com Rodrigo.
