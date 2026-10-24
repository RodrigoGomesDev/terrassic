# Identidade visual do Terrassic: "Âmbar e Basalto"

> Pedido do Rodrigo (24/10/2026): o mod precisa de uma identidade própria. A tela de Regras estava com cara de ARK
> (vidro escuro, linhas ciano, favos de mel, cantos chanfrados) e isso não pode continuar.
> Base: a capa (`docs/CAPA.md`), a paleta levantada no estudo de marca (`docs/estudos/05_MARCA_COMUNIDADE.md` §4.3) e as
> regras de pixel dos blocos (`docs/TEXTURAS_ERA.md`). Prévias: `art/identidade/paleta.png` e `art/identidade/tela_regras.png`
> (geradas por `tools/capagen/ui_mock.py`, que espelha o código pixel a pixel).

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
- **Texto em caixa normal**, nunca tudo em maiúsculas (o ARK grita; o caderno anota).
- **Fonte do jogo** em toda a interface (legível e compatível com pacotes de recurso); a fonte de blocos própria do
  letreiro só no logotipo.
- **Ícones** 8x8 ou 16x16 com contorno escuro de 1 px e paleta curta (como `tools/capagen/hud_icons.py`).
- **Som de interface:** cliques do vanilla; confirmações importantes com o sino de ametista (já usado no Altar).

## 4. O que já mudou no código (branch paralelo/v0.9-salto)

- `client/ui/TerrassicPalette` e `client/ui/TerrassicUi` (novos).
- **Tela de Regras** (`RulesScreen`): saiu o vidro ciano com favos e cantos chanfrados; entrou a laje de basalto com veio
  de âmbar, abas de pedra, campos rebaixados, controles com fragmento de âmbar, Salvar em âmbar e nomes em caixa normal.
  O botão "Regras do Terrassic" no menu de pausa e na tela de título usa o mesmo botão de pedra.
- **Toast de nova espécie**: laje própria no lugar da moldura de conquista do vanilla, retrato num poço.
- **HUD**: painel e barras com a paleta (basalto, borda âmbar, vida `BLOOD_500`, fome `AMBER_600`, alerta da Fenda `RIFT_500`).
- **Caderno de Campo**: as cores de papel, couro e tinta agora vêm da paleta (mesmos tons de antes).

## 5. Próximos passos de identidade

1. Passar o resto das telas pela paleta: tela de abertura (`IntroScreen`), Caderno (componentes), Mesa de Pesquisa,
   telas de carga e domesticação que vierem (v0.7).
2. **Pacote de texturas do Cretáceo** (`TEXTURAS_ERA.md`): menus e inventários do vanilla em basalto e âmbar dentro do
   pacote embutido (opcional, ligado no mundo Terrassic).
3. **Logotipo em três versões** (estudo 05 §4.3): letreiro completo, monograma "T" de pedra com âmbar (avatar e favicon)
   e o selo do Altar (o anel com os 4 âmbares, sem dinossauro). O ícone atual com o T. rex dentro do anel deve ser
   revisto para fugir da composição do logo de Jurassic Park.
4. Kit de marca para o site e o Discord: paleta acima, tipografia de apoio OFL (Inter ou Atkinson Hyperlegible para
   texto, uma manuscrita discreta para as anotações da Katarina), molduras de "ficha de campo" para revelar espécies.
