# Identidade visual do Terrassic: "Âmbar e Basalto"

> Pedido do Rodrigo (24/10/2026): o mod precisa de uma identidade própria. A tela de Regras estava com cara de ARK
> (vidro escuro, linhas ciano, favos de mel, cantos chanfrados) e isso não pode continuar.
> Depois (24/10/2026): "quero uma fonte totalmente nova, tipografia única, tudo único, uma identidade predominante".
> Base: a capa (`docs/CAPA.md`), a paleta levantada no estudo de marca (`docs/estudos/05_MARCA_COMUNIDADE.md` §4.3) e as
> regras de pixel dos blocos (`docs/TEXTURAS_ERA.md`). Tudo é desenhado por código e é asset do Terrassic (All Rights
> Reserved, `LICENSE-ASSETS.md`).
>
> | Prévia | Arquivo | Gerada por |
> |---|---|---|
> | Prancha da marca | `art/identidade/marca/prancha.png` | `tools/capagen/brand.py` |
> | Tela de Regras | `art/identidade/tela_regras.png` | `tools/capagen/ui_mock.py` (espelha o código pixel a pixel) |
> | Página do Caderno (Katarina) | `art/identidade/tela_caderno.png` | `tools/capagen/ui_mock.py` |
> | Paleta | `art/identidade/paleta.png` | `tools/capagen/ui_mock.py` |
> | Espécimes das fontes | `art/identidade/fontes/especime_*.png` | `tools/fontgen/build.py` |

## 1. A ideia em uma frase

**Pedra vulcânica escura com veios de âmbar, e o caderno de papel da Katarina.** Tudo o que o jogador usa tem cara de
algo esculpido em basalto, com o Âmbar Temporal (o coração da história) como o único brilho. Tudo o que o jogador lê
como livro (Caderno de Campo, páginas, Guia) é papel e tinta.

O que nunca usamos:
- **Ciano, vidro, hexágonos, cantos chanfrados de ficção científica, letras maiúsculas em tudo:** é a cara do ARK.
- **Vermelho + amarelo + preto juntos, T. rex de perfil chapado dentro de um círculo:** é a cara de Jurassic Park (risco de marca).
- **Verde e marrom de "acampamento" genérico e texturas de madeira do vanilla na interface:** não diferenciam.
- **A fonte do logo do Minecraft (Minecraft Ten) ou qualquer imitação do logo dele** (regra da Mojang).

## 2. A paleta

Fonte única no código: `common/src/main/java/com/terrassic/client/ui/TerrassicPalette.java`. Nenhuma tela do mod deve
ter cor solta em hexadecimal; use a constante.

| Família | Constante | Hex | Papel |
|---|---|---|---|
| Basalto | `BASALT_950` | `#0E0B0E` | contorno, sombras mais fundas |
| | `BASALT_900` | `#141014` | fundo de campos (poço), trilhos |
| | `BASALT_800` | `#1C181E` | **fundo dos painéis** |
| | `BASALT_700` | `#2A2329` | botão, aba selecionada, elevado |
| | `BASALT_600` | `#3A3036` | linhas, borda de campo, botão em foco |
| | `BASALT_500` | `#524550` | aresta iluminada |
| Pedra e osso | `STONE_400` | `#8A7C6A` | texto secundário, desabilitado |
| | `STONE_300` | `#B3A48C` | ícones neutros |
| | `STONE_200` | `#D8CCB2` | **texto principal** |
| | `BONE_100` | `#EFE6D2` | texto em destaque, números |
| Âmbar | `AMBER_700` | `#B9771C` | âmbar profundo, preenchimento de barras |
| | `AMBER_600` | `#D9952C` | foco, botão principal |
| | `AMBER_500` | `#F2B544` | **o acento**: títulos, seleção, o que age |
| | `AMBER_300` | `#FFD27A` | brilho, hover |
| Sinais | `RIFT_500` | `#F07A1A` | a Fenda: alertas, tempestades, chefes |
| | `DUSK_700` / `DUSK_500` | `#3A2240` / `#5E3866` | marca: tela de título, abertura, trailers |
| | `FERN_400` | `#7FAF55` | feito, ciência, seguro |
| | `BLOOD_500` | `#C4473A` | vida, perigo |
| | `SKY_400` | `#8FB4C8` | stamina, água (sempre fosco, nunca neon) |
| Caderno | `PAPER` / `PAPER_DARK` | `#E9DCBC` / `#D8C79E` | página |
| | `LEATHER` | `#5A3620` | capa do caderno |
| | `INK` / `INK_SOFT` | `#3B2A1A` / `#7A6448` | tinta |

Contraste: `STONE_200` e `BONE_100` sobre `BASALT_800` passam com folga do mínimo de leitura (texto claro em fundo
quase preto); `AMBER_500` sobre `BASALT_800` também. Texto sobre âmbar é sempre `BASALT_900`.

**Uso na marca fora do jogo** (site, Discord, redes): fundo `BASALT_800` ou `DUSK_700`, títulos em `AMBER_500`, texto
`STONE_200`, alertas `RIFT_500`. O pôr do sol roxo e laranja da capa é a "luz" da marca.

## 3. Os componentes (desenhados por código, sem textura)

Implementados em `client/ui/TerrassicUi.java`. Toda tela nova usa estes pedaços.

| Componente | Como é | Onde |
|---|---|---|
| **Laje** (`slab`) | Basalto com chanfro de 1 px como os blocos do vanilla (aresta clara em cima e à esquerda, sombra embaixo e à direita), contorno quase preto, **veio de âmbar** no alto partido no meio por uma gema e **4 cravos de âmbar** nos cantos | janelas e painéis (Regras, avisos) e o toast de espécie |
| **Poço** (`well`) | Rebaixado: sombra em cima e à esquerda; borda âmbar quando em foco | caixas de número, trilho do controle, moldura de retrato |
| **Botão** (`button`) | Pedra esculpida; em foco, texto âmbar e friso âmbar embaixo. O **botão principal** (Salvar, Confirmar) tem a face âmbar com texto escuro | rodapés de tela |
| **Aba** (`tab`) | Texto em pedra; a selecionada sobe um degrau com sublinhado âmbar | abas das Regras, do Caderno |
| **Controle deslizante** (`slider`) | Trilho rebaixado preenchido de âmbar até o cursor, que é um **fragmento de âmbar** (losango); um risquinho sob o trilho marca o valor padrão | Regras |
| **Divisor** (`divider`) | Linha esculpida com um ponto âmbar no meio | separar seções |
| **Barra de rolagem** (`scrollbar`) | Trilho de basalto, polegar âmbar | listas |
| **Marca** (`mark`) | Quadradinho âmbar de 3 px | valor mudado, entrada nova |
| **Página** (`paper`) | Papel com margem mais escura, tinta `INK` | Caderno de Campo, páginas da Katarina |

Regras de composição:
- **Uma cor de acento só.** O âmbar indica "isto age ou está selecionado". Se tudo é âmbar, nada é.
- **Texto em caixa normal**, nunca tudo em maiúsculas (o ARK grita; o caderno anota). A exceção são os títulos em
  "Entalhe", que é uma inscrição e só tem maiúsculas.
- **As fontes próprias** (§4) em todas as telas do mod: Sedimento na interface, Entalhe nos títulos, Caderno no que a
  Katarina escreveu. Os números das caixas de texto ficam na fonte do jogo (o cursor do vanilla mede com ela).
- **Ícones** 8x8 ou 16x16 com contorno escuro de 1 px e paleta curta (como `tools/capagen/hud_icons.py`).
- **Som de interface:** cliques do vanilla; confirmações importantes com o sino de ametista (já usado no Altar).

## 4. Tipografia: três fontes próprias

Desenhadas pixel a pixel em `tools/fontgen/` (uma grade de `#` por letra), com acentos do português e do espanhol
compostos pelo gerador (`À Á Â Ã Ä Ç È É Ê Ë Í Ñ Ó Ô Õ Ú Ü ¡ ¿ º ª` e as minúsculas). Saem como fontes bitmap do
Minecraft (`assets/terrassic/font/*.json` + `textures/font/*.png`; acentuadas numa folha mais alta, como o vanilla) e
como **TrueType** para o site e o material de marca (`art/identidade/fontes/*.ttf`, contornos traçados dos pixels).
O que uma fonte não desenhou cai para a fonte do jogo (provedor `reference` para `minecraft:default`), então nenhum
texto some. Desligar: `"terrassic_fonts": false` em `config/terrassic-client.json`.

| Fonte | Uso | Desenho |
|---|---|---|
| **Sedimento** (8 px) | interface: Regras, botões, abas, Caderno, HUD, avisos, dicas, abertura | Letra **talhada e condensada**: maiúsculas de 4 px (o vanilla usa 5), formas redondas com o **canto superior esquerdo reto** (a entrada do cinzel) e os outros três cortados; `i`, `l` e `1` com bandeira; `l` e `t` terminam numa curva para a direita; descendentes curvam para a esquerda |
| **Entalhe** (12 px, só maiúsculas) | títulos de tela, título da era, nomes de página, letreiro | **Inscrição em pedra**: hastes de 2 px e traços horizontais de 1 px (contraste de letra romana entalhada), serifas que abrem na base e no topo, o mesmo canto superior esquerdo reto da família, 2 px entre letras |
| **Caderno** (8 px) | o que a Katarina escreveu: páginas, a nota pessoal do Guia | **Letra de mão** da família: nasce da Sedimento, os cantos são arredondados (caneta não corta como cinzel), a metade de cima inclina 1 px para a direita e as letras que mais mudam à mão têm desenho próprio (a e g de um andar, e laçado, f com cauda, t cruzado) |

No código: `client/ui/TerrassicFonts` (`ui(...)`, `title(...)`, `hand(...)`), já aplicado na tela de Regras (título em
Entalhe), no Caderno de Campo (títulos de página em Entalhe, texto e guia em Sedimento, páginas e notas da Katarina em
Caderno, o Relatório do Incidente "datilografado" em Sedimento), na abertura (era em Entalhe), no HUD (título da era em
Entalhe), no aviso de nova espécie, na tela de título e nas dicas de carregamento.

## 5. A marca

Propostas geradas por `tools/capagen/brand.py` em `art/identidade/marca/`:

| Peça | O que é |
|---|---|
| **Letreiro** (`letreiro.png`) | TERRASSIC em **Degraus**, a letra de título aprovada em 25/10/2026: maiúsculas pesadas de pedra gasta, cada letra num degrau, acabamento pedra. As quatro versões (basalto, âmbar, osso, pedra), o alfabeto e palavras de exemplo ficam em `letreiro/` |
| **Monograma** (`monograma.png`) | um T de âmbar em Degraus numa laje de basalto com os 4 cravos: avatar, favicon, marca d'água |
| **Selo do Altar** (`selo.png`) | o anel de 4 pedras em pé e 4 ossos em volta do núcleo de âmbar, sobre o crepúsculo: carimbo, merch, tela de carregamento. **Sem dinossauro**, para não lembrar o logo de um certo filme |
| **Ícone** (`icone_proposta.png`) | o selo em 512 px, proposto para trocar o ícone atual (T. rex dentro do anel) |
| **Prancha** (`prancha.png`) | tudo junto: letreiro, slogan nos 3 idiomas, monograma, selo, paleta e as três fontes |

**Degraus** é a letra dos letreiros (capas, banners, site): glifos em `tools/fontgen/degraus.py` (A a Z, números,
pontuação e os acentos do português e do espanhol, grade de 11 linhas), desenho em `tools/capagen/letreiro.py` (degraus,
desgaste, acabamento, contorno e extrusão; o mesmo do site, pixel a pixel). As capas usam Degraus no TERRASSIC e no
slogan (`tools/capagen/titulo.py`), e a tela de título do jogo usa o mesmo letreiro. Não é fonte de interface: os
títulos dentro das telas continuam em Entalhe.

O ícone do selo (`icone_proposta.png`) continua só proposta: o `icon.png` do jogo é o T. rex da capa "Caçada"
(aprovado em 25/10, `docs/CAPA.md`).

## 6. O que já mudou no código

- `client/ui/TerrassicPalette` e `client/ui/TerrassicUi` (novos).
- **Tela de Regras** (`RulesScreen`): saiu o vidro ciano com favos e cantos chanfrados; entrou a laje de basalto com veio
  de âmbar, abas de pedra, campos rebaixados, controles com fragmento de âmbar, Salvar em âmbar e nomes em caixa normal.
  O botão "Regras do Terrassic" no menu de pausa e na tela de título usa o mesmo botão de pedra.
- **Toast de nova espécie**: laje própria no lugar da moldura de conquista do vanilla, retrato num poço.
- **HUD**: painel e barras com a paleta (basalto, borda âmbar, vida `BLOOD_500`, fome `AMBER_600`, alerta da Fenda `RIFT_500`).
- **Caderno de Campo**: as cores de papel, couro e tinta agora vêm da paleta (mesmos tons de antes).
- **Fontes próprias** em todas essas telas (§4) e **botões de couro** no Caderno de Campo (`client/ui/TerrassicButton`):
  as abas, os filtros, a lista de espécies e o virar de página deixaram o botão cinza do vanilla; a aba aberta e a
  espécie escolhida aparecem na cor da página.

## 7. Próximos passos de identidade

1. Passar o resto das telas pela paleta: tela de abertura (`IntroScreen`), Caderno (componentes), Mesa de Pesquisa,
   telas de carga e domesticação que vierem (v0.7).
2. **Pacote de texturas do Cretáceo** (`TEXTURAS_ERA.md`): menus e inventários do vanilla em basalto e âmbar dentro do
   pacote embutido (opcional, ligado no mundo Terrassic).
3. Feito em 25/10: a tela de título usa o Degraus. `textures/gui/title/terrassic.png` (512x128, desenhado como 256x64,
   `tools/capagen/title.py`) e `textures/gui/title/menu/titulo.png` (950x150, `tools/menugen/menu_assets.py`), os dois
   por `titulo.title_in`, que encaixa o letreiro no tamanho que o Java espera.
4. Site e redes (marco "Lançamento"): as fontes em TrueType (`art/identidade/fontes/`) nos títulos e na interface do
   site, a prancha como guia, molduras de "ficha de campo" para revelar espécies.
5. Fontes: ícones de interface como glifos (coração, fome, pegada) para usar dentro do texto; versão "Entalhe" de 24 px
   para o letreiro animado da tela de título.
