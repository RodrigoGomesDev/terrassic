# Terrassic: o mundo do Cretáceo (v0.8)

> Frente paralela "Mundo Terrassic" (branch `paralelo/v0.8-mundo`). Começou em 24/10/2026.
> Base: `HISTORIA.md` §8 ("Mundo Terrassic ou mundo normal", aprovado) e `ESCOPO.md` ("Ambientação").

## 1. O tipo de mundo "Terrassic"

Ao criar o mundo: **Mais opções do mundo → Tipo de mundo → Terrassic** (ou **Terrassic: Biomas Grandes**).

- O relevo é o do Minecraft (montanhas, cavernas, rios e oceanos no mesmo lugar). Só o **mapa de biomas** muda:
  em vez dos biomas vanilla, o Overworld inteiro é feito dos 11 biomas do Cretáceo Superior.
- **Sem vilas e sem estruturas modernas:** as estruturas vanilla só nascem nos biomas vanilla. Ficam as fortalezas
  do End, que são subterrâneas, para o jogador ainda poder ir ao End (Regra 0: o Minecraft é livre). Também ficam
  masmorras, geodos, fósseis de osso e cavernas.
- **Sem animais vanilla.** Ficam os que já existiam no Cretáceo: peixes, lulas, tartarugas-marinhas nas praias e sapos
  no pântano. Não há vacas, porcos, ovelhas, cavalos, golfinhos nem morcegos.
- **À noite, na superfície, não aparecem zumbis nem esqueletos** (`world/CretaceousBiomes`). Nas cavernas eles continuam.
  Bruxas, aldeões-zumbi, afogados, phantoms, patrulhas de saqueadores, cercos de zumbis e o mercador ambulante não
  aparecem em nenhum bioma do Cretáceo. Aranhas, creepers, slimes e endermen continuam (as aranhas dão a linha das lanças).
  O lugar dos monstros da noite fica para os predadores noturnos e as anomalias da Fenda (fase das Tempestades da Fenda).
- **Os dinossauros** chegam pelo `ModSpawns` de sempre: cada palavra da tabela WORLD de `gen_species.py` (forest,
  river, savanna...) também confere a tag `terrassic:habitat/<palavra>`. Espécie nova entra nos biomas do
  Cretáceo sem mexer em nada desta frente.
- **Mundo normal:** continua igual, e os biomas do Cretáceo não aparecem nele. Colocar esses biomas no mundo normal
  exigiria um sistema de regiões como o do TerraBlender; fica como pergunta aberta (seção 5).

## 2. Os 11 biomas

| Bioma | Inspiração real | Chão | Árvores e plantas | Habitats (quem nasce lá) |
|---|---|---|---|---|
| **Planície dos Hadrossauros** | Planícies costeiras de Alberta e Montana | grama | plátanos, ginkgos e magnólias esparsos; capim, samambaia, Williamsonia, cavalinhas | plains, savanna |
| **Floresta de Magnólias** | Florestas de Hell Creek | grama com serrapilheira de samambaia | magnólia, podocarpo, plátano, ginkgo e fetos arbóreos; samambaia-real, licopódio, fungo-prateleira | forest, jungle |
| **Pântano de Ciprestes** | Pântanos costeiros do Cretáceo | grama, turfa, lama e poças | cipreste-do-pântano na água rasa; junco, Calamites, cavalinhas, hepática, alga, nenúfar | swamp |
| **Floresta de Sequoias** | Florestas polares do Alasca | serrapilheira de acículas, podzol | metassequoia, araucária, podocarpo; samambaias, licopódio | forest, taiga |
| **Terras Secas** | Patagônia (Neuquén) | solo laterítico, terra grossa, lama rachada, laterita nos barrancos | araucárias e palmeiras Sabal esparsas, cicas, Williamsonia, arbusto seco | savanna, badlands, desert |
| **Delta do Rio** | Leitos de Kem Kem (Marrocos) | grama, bancos de areia, lama e poças | palmeira Sabal, feto arbóreo, plátano; junco, cavalinhas, Archaefructus, nenúfar | river, swamp, jungle, coast |
| **Mar Interior** | Mar Interior Ocidental | areia com manchas de cascalho | capim-marinho e recifes | ocean |
| **Mar Interior Profundo** | idem, a parte funda | cascalho com manchas de areia | capim-marinho | ocean, deep_sea |
| **Rio do Cretáceo** | — | cascalho e areia no leito | plátano, metassequoia e cipreste nas margens; junco, cavalinhas, seixos | river |
| **Praia do Cretáceo** | — | areia sobre arenito, pedra nos costões | seixos de calcário e de sílex | coast |
| **Serras do Cretáceo** | — | pedra nas encostas e nos cumes, veios de quartzito, grama | araucárias e podocarpos; líquen, licopódio | hill |

Cores próprias (céu, névoa, água, grama e folhas) em cada bioma. Partículas: pólen na Floresta de Magnólias e
poeira nas Terras Secas. Não há neve: o Cretáceo era uma estufa (as Serras só gelam acima de y≈260).

### De onde vem cada bioma (o mapa)

O mapa de biomas é o `OverworldBiomeBuilder` do Minecraft 1.20.1, portado para Python em `gen_world.py`. Cada bioma
vanilla vira o equivalente do Cretáceo. Assim rios, costas, pântanos e montanhas ficam onde o relevo espera.

| Vanilla | Cretáceo |
|---|---|
| oceanos | Mar Interior; os profundos viram Mar Interior Profundo |
| rios | Rio do Cretáceo; nas faixas quentes (temperatura 3 e 4), Delta do Rio |
| pântano | Pântano de Ciprestes |
| mangue | Delta do Rio |
| praias, costão | Praia do Cretáceo |
| planícies, campina, planície nevada, ilha de cogumelos | Planície dos Hadrossauros |
| florestas, selvas | Floresta de Magnólias; nas faixas frias (0 e 1), Floresta de Sequoias |
| taigas, bosque, floresta ventosa | Floresta de Sequoias |
| savanas, deserto, badlands | Terras Secas |
| picos, encostas, colinas ventosas | Serras do Cretáceo |

As 3.795 caixas de clima do vanilla viram 496 depois da fusão. O script confere por amostragem que o resultado é
idêntico ao mapeamento direto.

## 3. Como funciona (arquivos)

| O quê | Onde |
|---|---|
| Biomas, features, world presets, tags e textos | `tools/javagen/gen_world.py`, chamado por `gen_resources.py` (não edite os JSON à mão) |
| Biomas (JSON) | `data/terrassic/worldgen/biome/*.json` |
| Árvores e plantas dos biomas | `data/terrassic/worldgen/{configured,placed}_feature/cretaceous/` (usam as árvores e plantas de `gen_blocks.py`) |
| Tipos de mundo | `data/terrassic/worldgen/world_preset/terrassic{,_large}.json` + `data/minecraft/tags/worldgen/world_preset/normal.json` |
| Superfícies | `world/CretaceousSurface.java`, aplicado por `mixin/NoiseGeneratorSettingsMixin` na frente da regra de superfície do Overworld (só vale nos biomas do Cretáceo) |
| Monstros da noite, chaves e tags | `world/CretaceousBiomes.java` |
| Dinossauros por bioma | `world/ModSpawns.java` (gerado): cada condição também confere `terrassic:habitat/<palavra>` |
| Solos do Cretáceo | `#minecraft:dirt` (serrapilheiras, turfa, solo laterítico: plantas e mudas crescem neles) e `#minecraft:animals_spawnable_on` (+ lama rachada) |

Ordem das features: as que aparecem em mais de um bioma seguem sempre a mesma ordem (`PLANT_ORDER`, `NAMED_ORDER`
em `gen_world.py`). Sem isso o jogo recusa o mundo com "Feature order cycle found".

Arquivos compartilhados que esta frente tocou (só o mínimo; M2 só acrescentou 3 linhas no `terrassic.mixins.json`):
- `tools/javagen/gen_species.py`: a tabela `BIOMES` (13 linhas) ganhou `|| ctx.hasTag(CretaceousBiomes.habitat(...))`.
- `tools/javagen/gen_resources.py`: 3 linhas, para chamar `gen_world` e juntar os textos.
- `Terrassic.java`: 1 linha (`CretaceousBiomes.init()`). `terrassic.mixins.json`: 1 linha.

## 4. Próximas fases desta frente (v0.8)

| Fase | O que entra | Estado |
|---|---|---|
| M1 | Biomas do Cretáceo + tipo de mundo Terrassic | ✅ (falta testar no jogo, `TESTES_V08.md`) |
| M2 | Tela de título: panorama do Cretáceo, logo de pedra, frases e dicas de carregamento com curiosidades reais | ✅ (falta ver no jogo) |
| M3 | Estruturas: Cratera de Chegada, Acampamentos da Katarina, Sítio Fossilífero, Casa do Rio, Colônia de Ninhos, Ossuário | ⏭ |
| M4 | Tempestades da Fenda (céu âmbar, criaturas fora de época) | ○ |
| M5 | HUD: montaria, bando, nova espécie, nome da era | ○ |
| M6 | Música e sons de fundo por bioma (gravações PD/CC0, no Mac) | ○ |

## 5. Tela de título e telas de carregamento (M2)

- **Panorama** (`tools/capagen/panorama.py`): o mesmo entardecer da capa, mas em volta do jogador e em blocos.
  - No céu, a Fenda, estrelas cadentes e o vulcão fumegando.
  - Árvores de blocos do mod (araucária, magnólia, palmeira Sabal, metassequoia), feitas com as texturas do jogo.
  - O lago espelhando a Fenda, com a manada de Parasaurolophus na beira, o T. rex rugindo, um casal de Triceratops,
    dois Alamosaurus ao fundo, Struthiomimus correndo, Pteranodons e um Quetzalcoatlus planando.
  - Todos os modelos e texturas são os do mod. As 6 faces seguem o `CubeMap` vanilla e ficam em
    `assets/terrassic/textures/gui/title/background/`.
  - Prévias: `art/capa/panorama_vistas.png` (4 direções, como o jogo mostra) e `art/capa/panorama_preview.png` (faces abertas).
- **Logo** (`tools/capagen/title.py`): o letreiro de pedra TERRASSIC da capa em 256x64, no lugar do logo do Minecraft,
  com a linha "Capítulo 1 · Ecos do Fim" embaixo. Prévia da tela inteira: `art/capa/tela_titulo_preview.png`.
- **Frases amarelas** (16) e **dicas de carregamento** (48: fatos reais das criaturas e do Cretáceo + dicas de jogo),
  nos 3 idiomas, em `tools/javagen/menu_texts.py`. A dica aparece na criação/carregamento do mundo e em "Carregando terreno".
- Código: `client/TerrassicTitle`, `client/ClientConfig` e os mixins de cliente `TitleScreenMixin`, `LevelLoadingScreenMixin`
  e `ReceivingLevelScreenMixin`. Todos são opcionais (`require = 0`): se outro mod mexer na tela, fica a vanilla, sem crash.
- Desligar: `config/terrassic-client.json` → `"title_screen": false` e/ou `"loading_tips": false`.
- Arte nova: mostrar as prévias ao Rodrigo (regra 12 do ROADMAP). Ela não troca nenhum asset do mod, só o visual vanilla da tela de título.

## 6. Perguntas abertas para o Rodrigo

1. **Biomas do Cretáceo também no mundo normal?** Hoje eles só existem no tipo "Terrassic". Para misturar com o
   vanilla seria preciso um sistema de regiões próprio (sem TerraBlender, que é de terceiros).
2. **Fortalezas do End no mundo Terrassic:** ficaram, para não fechar o End. Se preferir um Cretáceo puro, dá para tirar.
3. **Zumbis e esqueletos nas cavernas:** ficaram, por causa dos ossos e das flechas. Se preferir trocar por criaturas
   da era também no subsolo, isso entra junto com as anomalias da Fenda.
4. **Tela de título:** o panorama e o logo agradam? Dá para trocar a cena (manhã em vez de entardecer, outras espécies).
