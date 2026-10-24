# Fauna de caça e comida do Cretáceo

> Pedido do Rodrigo (24/10/2026): no mundo Terrassic não há animais do Minecraft. Se é para ter um bicho para matar e
> ter comida e recursos no começo, ele tem de ser pré-histórico. Esta frente faz duas coisas: a **comida** (o que cai
> dos animais no lugar de bife, carneiro e frango) e a **fauna de caça** do Cretáceo Superior (os "porcos", "galinhas",
> "coelhos" e peixes do nosso mundo). Entra na v0.7, logo depois do Didelphodon e antes do nocaute.

## 1. Comida (fase 88)

| Item | Fome / saturação | De onde vem |
|---|---|---|
| Carne de Dinossauro Crua (`raw_dino_meat`) | 3 / 0,3 (como bife cru) | de **toda** espécie, no lugar de beef, mutton, chicken e porkchop; dos répteis marinhos e do Deinosuchus no lugar do "bacalhau" (era a carne deles mesmos) |
| Carne de Dinossauro Assada (`cooked_dino_meat`) | 8 / 0,8 (como bife assado) | forno (200 ticks), defumador (100), fogueira (600); morrer queimando já assa |
| Carne Nobre Crua (`raw_prime_meat`) | 4 / 0,3 | só das espécies grandes (tabela `PRIME` em `gen_resources.py`): titãs 3-6 (Argentinosaurus 4-8), predadores ápice, ceratopsianos, anquilossauros, hadrossauros, terizinossauros, mosassauros, azdarquídeos 1-3 |
| Carne Nobre Assada (`cooked_prime_meat`) | 10 / 0,9 + Regeneração I por 5 s | idem; o prato de festa do acampamento, como no ARK |

- Os peixes continuam dando bacalhau: o Xiphactinus é peixe, e o que o Spinosaurus, o Pteranodon, o Ichthyornis, o
  Hesperornis e o Archelon soltam é o peixe que tinham na barriga. Quando Enchodus e Lepisosteus entrarem, eles trazem
  os peixes próprios do Cretáceo.
- Couro, penas, ossos, dentes e chifres continuam como estavam; o couro de cada espécie (`<especie>_hide`) também.
- A carcaça (`docs/CARCACAS.md`) não muda: o loot passa pela mesma tabela, então as porções já saem em carne de dinossauro.
  As partículas de "carne" da carcaça usam o item novo.
- Receitas: `data/terrassic/recipes/cooked_*_meat*.json` (smelting, smoking, campfire_cooking), geradas por `cooked()`.
- Sprites 16x16 em `tools/spritegen/sprites.py` (`meats()`): naco irregular vermelho com gordura, assado marrom com
  marcas de grelha; a nobre tem a costela ao lado. Pré-via em `/mnt/project-files/fauna/carne_preview.png`.

Desde a fase 108 (Leptoceratops) os carnívoros aceitam `raw_dino_meat` (e os da tabela `PRIME` também `raw_prime_meat`)
como comida de domesticação e de fome (`food=` em `gen_species.py`; `ModItems` é importado quando a lista cita um item
nosso), e os textos do Guia em `lore.py` falam na carne de dinossauro em vez de bife, frango e carneiro.

## 2. A fauna de caça (uma espécie por fase, modelos únicos no padrão 2x)

| Ordem | Espécie | Papel no mundo | Tamanho real | O que dá | Rig |
|---|---|---|---|---|---|
| 1 | **Leptoceratops** ✅ fase 108 | o "porco": ceratopsiano pequeno sem gola grande, em bandos de 3-5 nas planícies e florestas; foge, mas um macho encurralado dá cabeçada | 2 m, ~70 kg (Hell Creek, Scollard) | carne 2-4, couro 1-2 | ceratopsiano (Protoceratops) |
| 2 | **Vegavis** ✅ fase 109 | a "galinha/pato": ave aquática que grasna (a siringe mais antiga conhecida), em bandos nos rios, deltas e praias; bota ovos em ninhos na margem | 0,6 m (Ilha Vega, Antártica) | carne 1, penas 1-3, ovos (bloco de ovo pequeno) | ave (Ichthyornis/Hesperornis) |
| 3 | **Mesodma** ✅ fase 110 | o "coelho": multituberculado do tamanho de um rato grande, noturno, em tocas sob as raízes; some na grama alta | 15 cm sem a cauda (Hell Creek) | carne 0-1, couro de coelho | mamífero (Didelphodon, 3x) |
| 4 | **Basilemys** ✅ fase 111 | a tartaruga terrestre: lenta, de casco alto, pasta em planícies e deltas; protege-se no casco | 1,3 m de casco (Dinosaur Park) | carne 1-2, casco (escamas) 1-3 | tartaruga (Archelon, terrestre) |
| 5 | **Enchodus** | o "peixe-sabre": peixe marinho com presas, em cardumes no Mar Interior; morde quem nada perto | 1,5 m (Niobrara) | peixe próprio (Enchodus cru/assado), substitui o bacalhau no loot dos marinhos | peixe (Xiphactinus) |
| 6 | **Lepisosteus** | o peixe-agulha de rio (gar), de escamas ganoides duras; em rios e deltas | 1,2 m (Hell Creek) | peixe próprio, escamas (sílex de escama?) | peixe |

Checklist por espécie: modelo e animações no padrão 2x (textura 1 px = 1 px do jogo, anatomia pesquisada, como o
T. rex v3 da thread de tamanhos), `SIZES/GUIDE/WORLD/SPECIES` em `gen_species.py`, nomes e loot em `gen_resources.py`,
ovo v5 em `egg_designs.py` (+ `NEW_SPECIES`), linha `SKULLS` e `HIDE_PATTERN` em `blocks.py`, lore nos 3 idiomas,
`TAMANHOS/ROSTER/ROADMAP/bestiário`, motivo do fóssil em `FOSSIL_MOTIF` (`tools/spritegen/science.py`; sem ele o gerador usa um
motivo pela dieta e `gen_resources.py` falha se algum modelo de item apontar para textura inexistente). Os geradores de mundo (`gen_world.py`) entram com a tag `terrassic:habitat/<palavra>`
pela tabela WORLD, então a fauna nasce nos biomas do Cretáceo sem mexer na frente de mundo. A densidade "estilo ARK"
é da frente config-ark (`docs/REGRAS.md`).

## 3. Testes no jogo

1. Matar um Parasaurolophus: cai carne de dinossauro crua (2-5) e couro; nada de bife.
2. Matar um T. rex: carne crua + carne nobre crua 1-3; morrendo em fogo, caem assadas.
3. Fogueira, forno e defumador assam as duas carnes; a nobre assada dá Regeneração por 5 s.
4. Carcaça de um titã: as porções saem em carne de dinossauro e nobre.
5. Ícones legíveis no inventário ao lado do bife vanilla (mesmo contraste, mesmo contorno).
