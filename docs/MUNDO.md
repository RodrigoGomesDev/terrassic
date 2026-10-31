# Terrassic: o mundo do Cretáceo (v0.8)

> Frente paralela "Mundo Terrassic" (branch `paralelo/v0.8-mundo`). Começou em 24/10/2026.
> Base: `HISTORIA.md` §8 ("Mundo Terrassic ou mundo normal", aprovado) e `ESCOPO.md` ("Ambientação").

## 1. O tipo de mundo "Terrassic"

Desde a v0.15 o mundo novo vem no **Padrão** do Minecraft, com os dinossauros como um extra (§12). O tipo **Terrassic**
fica em **Mais opções do mundo → Tipo de mundo**, junto com **Terrassic: Ilha Pequena** e **Terrassic: Continente
Grande**; `"mundo_terrassic": true` faz ele voltar a vir escolhido (§10.3).

- O mundo é **um continente só**, como uma Pangeia, com mar em volta e a borda do mundo fechando o mar (§10). O
  relevo dentro dele é o do Minecraft (montanhas, cavernas, rios). Os biomas são os 11 do Cretáceo Superior.
- **Sem vilas e sem estruturas modernas:** as estruturas vanilla só nascem nos biomas vanilla. Ficam as fortalezas
  do End, que são subterrâneas, para o jogador ainda poder ir ao End (Regra 0: o Minecraft é livre). Também ficam
  masmorras, geodos, fósseis de osso e cavernas.
- **Nenhum animal vanilla** (§10.4): nem vacas, porcos, ovelhas, cavalos, golfinhos e morcegos, nem peixes, lulas,
  tartarugas e sapos. A comida e os recursos vêm da fauna pré-histórica.
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
| Monstros da noite, chaves e tags | `world/CretaceousBiomes.java` + `mixin/MobMixin` (em `Mob.checkSpawnRules`; o `LIVING_CHECK_SPAWN` do Architectury não serve para negar spawn, porque Forge e Fabric leem o resultado ao contrário) |
| Dinossauros por bioma | `world/ModSpawns.java` (gerado): cada condição também confere `terrassic:habitat/<palavra>` |
| Solos do Cretáceo | `#minecraft:dirt` (serrapilheiras, turfa, solo laterítico: plantas e mudas crescem neles) e `#minecraft:animals_spawnable_on` (+ lama rachada) |

Ordem das features: as que aparecem em mais de um bioma seguem sempre a mesma ordem (`PLANT_ORDER`, `NAMED_ORDER`
em `gen_world.py`). Sem isso o jogo recusa o mundo com "Feature order cycle found".

Arquivos compartilhados que esta frente tocou (só o mínimo; M2 e M4 só acrescentaram linhas no `terrassic.mixins.json`):
- `tools/javagen/gen_species.py`: a tabela `BIOMES` (13 linhas) ganhou `|| ctx.hasTag(CretaceousBiomes.habitat(...))`.
- `tools/javagen/gen_resources.py`: 3 linhas, para chamar `gen_world` e juntar os textos.
- `Terrassic.java`: 4 linhas (`CretaceousBiomes`, `ArrivalCrater`, `KatarinaRefuge`, `RiftStorm`). `terrassic.mixins.json`: as linhas dos mixins novos.
- `research/Objective.java`: `RIFT_STORM` passou a `true`. `tools/javagen/conquistas.py`: `rift_storm`, `river_house` e `mate` passaram a `ready`.

## 4. Próximas fases desta frente (v0.8)

| Fase | O que entra | Estado |
|---|---|---|
| M1 | Biomas do Cretáceo + tipo de mundo Terrassic | ✅ (falta testar no jogo, `TESTES_V08.md`) |
| M2 | Tela de título: panorama do Cretáceo, logo de pedra, frases e dicas de carregamento com curiosidades reais | ✅ (falta ver no jogo) |
| M3a | Estruturas I: Cratera de Chegada, Acampamentos da Katarina (3 variantes), Sítio Fossilífero, Ossuário | ✅ (falta ver no jogo) |
| M3b | Estruturas II: Casa do Rio (Refúgio, com o "Mate"), Colônia de Ninhos de Maiasaura, Lente de Âmbar apontando o Refúgio | ✅ (falta ver no jogo) |
| M4 | Tempestades da Fenda (céu âmbar, criaturas fora de época) | ✅ (falta ver no jogo) |
| M5 | HUD: montaria, bando, nova espécie, nome da era, alerta da Fenda | ✅ (falta ver no jogo) |
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

## 6. Estruturas (M3)

Todas geradas por código: os moldes `.nbt` por `tools/structgen/template.py` (blocos do mod, conferidos contra os
blockstates), o resto (estrutura, pool, conjunto, tags de bioma, loot) por `tools/javagen/gen_structures.py`.
Prévias isométricas: `art/estruturas/` (`python3 tools/structgen/preview.py`). Nascem nos biomas do Cretáceo **e** nos
biomas vanilla equivalentes, então a história também anda num mundo normal.

| Estrutura | Como é | Onde | Frequência |
|---|---|---|---|
| **Cratera de Chegada** | Bacia rasa de cinza vulcânica e lama rachada, âmbar no centro, cinza na borda, cesto com âmbar bruto e uma página | 18 a 26 blocos do spawn do mundo, uma por mundo, cavada na primeira entrada (`world/ArrivalCrater`) | 1 |
| **Acampamento da Katarina** | Barraca de palha com cumeeira, cama, esteiras, cesto, fogueira de pedras apagada, troncos de sentar, varal ou estaleiro de couro, pedra de giz com as marcas dela | 3 variantes: junco (planícies, pântano, delta), samambaia (florestas), cicadácea com couro (Terras Secas, serras, savana, deserto) | 1 a cada ~30 chunks |
| **Sítio Fossilífero** | Barranco de folhelho, calcário e giz cortado a prumo, com Rocha Fossilífera e crânios fósseis na parede, andaime de galhos, bancada de lascar sílex e cesto de ferramentas | Terras Secas, serras, planícies; badlands, savana, deserto, colinas | 1 a cada ~26 chunks |
| **Ossuário** | Leito de ossos com o esqueleto de um titanossauro (coluna, costelas, crânio), lama rachada, crânios fósseis e três Compsognathus carniceiros | Terras Secas, delta, planícies; badlands, savana, deserto | 1 a cada ~40 chunks |
| **Casa do Rio** (Refúgio da Katarina) | Casa de troncos de cipreste em palafitas, telhado de junco, deque com parapeito, horta em canteiros de serrapilheira; dentro, a cama de couro dela, a Mesa de Pesquisa, dois cestos com páginas, lamparina, estaleiro, tambor, pinturas e um troféu de Parasaurolophus. No deque, **Mate**, o Parasaurolophus dela, sentado | Uma por mundo, a 220-420 blocos da origem, puxada para um rio (anel concêntrico, como as fortalezas) | 1 |
| **Colônia de Ninhos** | Montes de terra com ninhos de palha e ovos de Maiasaura (chocam e os filhotes marcam quem estiver perto), quatro Maiasauras adultas | Planície dos Hadrossauros; planícies, campina, savana | 1 a cada ~36 chunks |

Loot: `loot_tables/chests/katarina_camp.json` traz sempre uma Página Solta, que vira uma página que **aquele** jogador ainda
não tem (`LoosePageItem`), mais comida, sílex, linha, osso, papel, às vezes âmbar bruto e uma ferramenta simples.
`fossil_site.json` traz pincel ou cinzel, 1 ou 2 fósseis de espécies e às vezes uma página.
`katarina_refuge.json` traz duas páginas, metade das vezes uma Lente de Âmbar, frascos, carvão de esboço, âmbar bruto e papel.

**Mate** (`world/KatarinaRefuge`): o molde cria o Parasaurolophus já domado pela Katarina (UUID fixo, ela nunca está online),
então ele fica sentado no deque. O primeiro jogador que tocar nele de mão vazia vira o dono ("Mate cheira as suas mãos,
sente o cheiro da Katarina em você e aceita você"). Conta como domar para o Diário.

**A Lente de Âmbar aponta o Refúgio:** agachado, use a lente. Aparece a distância e a direção ("Refúgio da Katarina: uns 340
blocos, direção noroeste"), com o som de cristal de ametista. Usa a tag de estrutura `terrassic:katarina_refuge`, então
`/locate structure #terrassic:katarina_refuge` também acha.

## 7. Tempestades da Fenda (M4)

`world/RiftStorm` (servidor) e `client/RiftStormClient` (efeitos).
- **Quando:** no entardecer (tempo 12600), com 20% de chance, se já passaram 3 dias desde a última. Dura 3 a 5 minutos.
  Configurável em `config/terrassic-world.json` (`rift_storms`, `storm_chance`, `storm_min_days`, `storm_minutes_min/max`,
  `storm_creatures`). Admin: `/terrassic tempestade iniciar` e `/terrassic tempestade parar`.
- **Como é:** céu, nuvens e névoa ficam âmbar (mixins de cliente `ClientLevelMixin` e `FogRendererMixin`, opcionais), e
  partículas de âmbar flutuam em volta do jogador. De vez em quando o "tempo falha" com sons distorcidos (ametista, sinalizador,
  caverna em tom grave). Aparecem mensagens no começo e no fim.
- **Criaturas de outras eras:** a cada 10 s, perto de cada jogador no Overworld (até 3 por jogador), surge da Fenda uma
  espécie do Guia cuja era não é o Cretáceo Superior. Hoje são os 4 jurássicos; qualquer espécie de outra era que entrar
  depois aparece também. Elas chegam com um clarão de partículas âmbar, som de teleporte grave e brilho por 10 s.
  Têm a tag `terrassic_rift` e soltam âmbar bruto ao morrer. No fim da tempestade voltam para a Fenda, a não ser que alguém
  tenha domado alguma.
- **Diário:** quem está no Overworld quando a tempestade começa e continua vivo quando ela acaba completa o objetivo
  "Sobreviver a uma Tempestade da Fenda" (`Objective.RIFT_STORM` ligado, conquista `chapter1/rift_storm` gerada).
- Conquistas ligadas junto com a M3b: `chapter1/river_house` (estar dentro da Casa do Rio) e `chapter1/mate` (o Mate aceita você).

## 8. HUD (M5)

Desde a v0.14 o HUD tem o visual "Âmbar" e o desenho de cada peça está em `docs/HUD.md`; esta tabela resume.

`client/TerrassicHud` (+ `client/SpeciesToast`, `client/HudNotices`), com os modelos do mod renderizados ao vivo. Os ícones ficam em
`assets/terrassic/textures/gui/hud.png` (`tools/capagen/hud_icons.py`).

| Parte | Quando | O que mostra |
|---|---|---|
| Placa da montaria | Montado num dinossauro | O bicho numa gota de âmbar, nome e nível, vida, fome e o encaixe do especial (canto superior esquerdo) |
| Avisos | Algo acontece com um bicho seu | Placa no meio da borda direita: subiu de nível, domesticado, filhote, fome, acordou, morreu (substitui a barra do bando) |
| Nova espécie | Quando uma espécie sobe de nível no Guia | Notificação com o modelo, o nome e o nível novo. Na silhueta, só "???" |
| Nome da era | Ao entrar no mundo (no Overworld) | "Cretáceo Superior" e "Capítulo 1 · Ecos do Fim" em letras grandes |
| Alerta da Fenda | Durante uma Tempestade da Fenda | Fragmento de âmbar rachado pulsando no topo da tela |

Liga e desliga em `config/terrassic-client.json` (`hud_style`, `hud_mount`, `hud_notices`, `hud_numbers_always`,
`hud_new_species`, `hud_era_title`, `hud_rift_alert`). O F1 esconde tudo. A stamina entra na placa quando o sistema existir.

## 9. Perguntas abertas para o Rodrigo

1. **Biomas do Cretáceo também no mundo normal?** Hoje eles só existem no tipo "Terrassic". Para misturar com o
   vanilla seria preciso um sistema de regiões próprio (sem TerraBlender, que é de terceiros).
2. **Fortalezas do End no mundo Terrassic:** ficaram, para não fechar o End. Se preferir um Cretáceo puro, dá para tirar.
3. **Zumbis e esqueletos nas cavernas:** ficaram, por causa dos ossos e das flechas. Se preferir trocar por criaturas
   da era também no subsolo, isso entra junto com as anomalias da Fenda.
4. **Tela de título:** o panorama e o logo agradam? Dá para trocar a cena (manhã em vez de entardecer, outras espécies).

## 10. Continente Terrassic (pedido do Rodrigo, 24/10/2026)

Depois de testar a v0.8, o Rodrigo pediu: o mundo Terrassic tem que ser **bem menor** que o do Minecraft, um
continente só "como uma Pangeia", com **o resto só mar** (a ideia de mundo fechado do skyblock); esse tipo de mundo
tem que vir **sozinho** ao criar um mundo; e **nenhum animal do Minecraft** (comida e recursos do começo vêm de animais
pré-históricos).

### 10.1 Formato

- **Um continente** centrado em 0,0, um pouco comprido (1,35 : 1), com **costa recortada**.
- O **Mar Interior** entra por uma das costas como um golfo largo e curvo até perto do centro: o continente fica em
  forma de **"C"**, como a Pangeia em volta do mar de Tétis (e como a Laramídia, cortada pelo Mar Interior do Oeste,
  no Cretáceo Superior de verdade). O centro é sempre terra firme: o jogador nasce ali.
- Um anel de **ilhotas** no mar raso em volta (futuras Ilhas do Tempo e praias de desova do Archelon).
- Fora disso, **oceano fundo** até a **borda do mundo**.
- A direção do golfo e o recorte da costa vêm da **semente**: cada mundo tem um continente diferente.
- Prévia do formato: `/mnt/project-files/mundo/previas/continente_formato.png` (mesma matemática do Java).

| Tipo de mundo | Raio | Terra (aprox.) | Borda do mundo |
|---|---|---|---|
| Terrassic (padrão) | 1 200 blocos | ~5 km² | 4 800 × 4 800 |
| Terrassic: Ilha Pequena | 800 blocos | ~2,4 km² | 3 200 × 3 200 |
| Terrassic: Continente Grande (biomas grandes) | 2 000 blocos | ~13 km² | 8 000 × 8 000 |

Para comparar: atravessar o continente padrão correndo leva uns 7 minutos; a pé, uns 10.

### 10.2 Como funciona (técnico)

O terreno do Minecraft decide altura, profundidade do mar e bioma a partir da **continentalidade**. O mod troca só
esse valor; o resto (cavernas, aquíferos, minérios, regras de superfície) continua o do Minecraft.

- Os tipos de mundo (`data/terrassic/worldgen/world_preset/terrassic*.json`, gerados por `tools/javagen/gen_world.py`,
  tabela `WORLD_TYPES`) usam as configurações de ruído normais do Minecraft e embrulham o mapa de biomas na fonte de
  biomas `terrassic:continente` (`world/continent/ContinentBiomeSource.java`), que guarda o **raio** (`"raio"`). O raio
  fica salvo no próprio mundo: mudar a config depois não muda um mundo que já existe.
- Quando um mundo assim abre, `mixin/ChunkMapMixin` passa o roteador de ruído por `world/continent/ContinentRouter`
  logo antes de ele ser ligado à semente: toda leitura da continentalidade vanilla (a do bioma e a das funções de
  relevo offset, factor, jaggedness, depth...) vira `ContinentDensity` (tipo de função de densidade
  `terrassic:continente`): terra no meio (com a variação vanilla por cima, para ter planícies, morros e planaltos),
  costa perto do raio, mar raso no golfo e nas ilhotas, oceano fundo fora. Nada do Minecraft é copiado.
- **Borda do mundo** (`world/continent/ModContinent`): num mundo novo, ao abrir, a borda é centrada em 0,0 com lado
  de 4 raios (config `borda_em_raios`, padrão 2,0 a partir do centro). Uma borda que alguém já mudou não é tocada;
  `/worldborder` continua valendo; `"borda": false` desliga.
- Nada disso muda os tipos de mundo do Minecraft ("Padrão" etc.).

### 10.3 Mundo Terrassic como padrão (desligado na v0.15)

- Com `"mundo_terrassic": true` em `config/terrassic-world.json`, **Criar novo mundo** já vem no tipo **Terrassic**
  (`mixin/client/WorldCreationUiStateMixin`). O jogador pode escolher qualquer outro tipo na lista.
- **Desde a v0.15 vem desligado**: o jogo abre no **Padrão** do Minecraft (§12). A chave é nova porque todo arquivo
  de config já tinha `"mundo_padrao": true` escrito; a chave antiga é ignorada.
- **Servidor dedicado**: em `server.properties`, `level-type=terrassic\:terrassic` (ou `terrassic\:terrassic_small`,
  `terrassic\:terrassic_large`).

### 10.4 Sem animais do Minecraft

- Os biomas do Cretáceo não têm mais nenhum animal vanilla: saíram também peixes, lulas, lulas-brilhantes das cavernas,
  tartarugas e sapos (`gen_world.py`). Monstros das cavernas continuam como na M1.
- Se outra coisa tentar pôr um animal vanilla num bioma do Cretáceo (outro mod, um pacote de dados, o cavalo-esqueleto
  das tempestades), `world/CretaceousBiomes` recusa. Ovos de spawn e geradores continuam funcionando.
- A comida e os recursos do começo vêm dos **dinossauros pequenos** (Protoceratops, Thescelosaurus, Oviraptor,
  Mononykus, Didelphodon, Gallimimus...), que já deixam carne, couro, penas, ossos e ovos, e o ecossistema da config
  ARK (`world/EcoSpawner`) mantém terra, céu e mar cheios em volta do jogador.
- **Fauna de caça** pedida para a fila de espécies (v0.3): Leptoceratops (o "porco": carne e couro), Vegavis (a
  "galinha/pato": penas, ovos, carne de ave), Mesodma (o "coelho"), Basilemys (tartaruga terrestre: carne e casco),
  Enchodus (peixe do mar) e Lepisosteus (peixe-agulha de rio). Todos do Cretáceo Superior.

### 10.5 Testes no jogo

Veja `docs/TESTES_V08.md`, seção 7 ("Continente").

## 11. Mapa da ilha (pedido do Rodrigo, 25/10/2026)

O Rodrigo pediu um mapa da ilha. Ele fica numa aba nova do Caderno de Campo, **Mapa** (entre Guia e Katarina),
desenhado a tinta no papel do caderno, como um mapa antigo de expedição.

### 11.1 O que aparece

- **Página da esquerda**: o mapa do quadrado de -2R a +2R (R = raio do continente), ou seja, o continente inteiro e
  o mar em volta até perto da borda do mundo. Norte para cima, escala de 500 m (1 bloco = 1 m), marca "N".
- **Mar** em aguada clara (mais escura no mar profundo) com linhas de onda acompanhando a costa; **costa** em tinta;
  **terra** sombreada pelo relevo (luz do noroeste), com uma marquinha por bioma: árvores nas florestas, tufos nos
  pântanos e no delta, pontinhos nas terras secas, traços no planalto; rios em tinta suave; praias mais claras.
- **Você**: seta vermelha com contorno de tinta, girando para onde o jogador olha.
- **Página da direita**: legenda (9 tipos de terreno e "Você"), sua posição (X, Z) e as coordenadas do ponto sob o
  mouse quando ele passa pelo mapa.
- Um mundo que não é continente Terrassic (ou enquanto o levantamento ainda roda) mostra só um aviso.
- **No Nether e no End** o mapa continua sendo o da ilha (Overworld), mas a seta some e, no lugar da posição, aparece
  "Você está longe da ilha" (as coordenadas dessas dimensões não valem no mapa). Apontado pelo roteiro do Codex
  (`docs/TESTES_MAPA.md`).

Prévia (mesmo algoritmo do Java, com um continente falso): `/mnt/project-files/mundo/previas/mapa_ilha_previa.png`,
gerada por `tools/worldgen/mapa_preview.py`.

### 11.2 Como funciona (técnico)

- **Levantamento** (`world/continent/IslandMap`): quando um mundo de continente abre pela primeira vez, uma tarefa
  em segundo plano consulta o **próprio gerador de mundo** em 128 × 128 pontos (altura do chão com
  `getBaseHeight(OCEAN_FLOOR_WG)` e bioma com `getNoiseBiome`). **Nenhum chunk é gerado**, então o mapa mostra a ilha
  inteira desde o começo, sem precisar explorar. Leva alguns segundos e não trava o servidor.
- Cada bioma vira uma categoria (mar profundo, mar, praia, rio, pântano/delta, planície, floresta, planalto, terras
  secas): os 11 biomas do Cretáceo pelo nome, qualquer outro pelas tags do Minecraft.
- O resultado fica salvo com o mundo (`data/terrassic_island_map.dat`, uns 33 KB) e é enviado a cada jogador que
  entra (pacote `terrassic:island_map`, uns 33 KB uma vez por entrada). Mundos que não são continente não têm mapa.
- **Desenho** (`client/ClientIslandMap`): o cliente monta uma textura de 256 × 256 (2 pixels por ponto, com alturas
  interpoladas) na primeira vez que a aba abre, mais uma faixa com as amostras da legenda. Sai do mundo, o mapa é
  descartado.
- Cores só da paleta do Caderno (`TerrassicPalette`: PAPER, PAPER_DARK, INK, INK_SOFT, BLOOD_500).

### 11.3 Testes no jogo (para o Rodrigo)

1. Criar um mundo Terrassic novo, esperar uns segundos, abrir o Caderno, aba **Mapa**: o continente em "C" com o
   golfo, as ilhotas e o mar em volta; a seta vermelha no centro, onde você nasceu.
2. Andar e virar: a seta acompanha posição e direção; "Você: X, Z" muda.
3. Passar o mouse no mapa: as coordenadas do ponto aparecem à direita. Conferir um ponto indo até ele.
4. Conferir se florestas, pântanos, terras secas e planalto do mapa batem com o que se vê no mundo.
5. Sair e entrar de novo no mundo: o mapa aparece na hora (veio salvo, sem novo levantamento; no log não aparece de
   novo "island map surveyed").
6. Num mundo "Padrão" do Minecraft: a aba mostra só o aviso.
7. Entrar no Nether e no End e abrir a aba: sem seta, com o aviso "Você está longe da ilha"; voltar e a seta reaparece.
8. As cinco abas cabem no topo do caderno nos três idiomas, em várias escalas de interface.

## 12. Minecraft normal com dinossauros (v0.15, pedido do Rodrigo, 30/10/2026)

> "essa v0 eu quero que seja um acrescental ao minecraft, ent quero jogar um minecraft normal, com dinossauros"

### 12.1 O que muda

- **Mundo novo no Padrão do Minecraft.** O tipo Terrassic continua na lista (§10.3).
- **A fauna do Minecraft fica inteira.** Vacas, ovelhas, porcos, galinhas, cavalos, lobos, lulas e golfinhos nascem
  como sempre. Nada do Minecraft é tirado nos biomas do Minecraft (os biomas do Cretáceo continuam sem eles, §10.4).
- **Os dinos são um extra: cerca de 1 em cada 3 animais** (era 1 em 4 até a v1.0.1; no teste do Rodrigo de 31/10 o
  spawn ainda estava "meio baixo", e a medição do Mac deu 1 dino para 5 animais com 0,25). Antes, numa planície ou savana, uns 2 em cada 3 animais que
  nasciam eram dinos (peso somado 89 contra uns 46 a 50 dos animais do Minecraft).
- **A reposição em volta do jogador** (`world/EcoSpawner`) fica com uns 54% do alvo fora do Cretáceo: 10 em terra,
  6 no mar e 2 voadores por região (contra 18, 12 e 4 no continente).
- As colônias de Pteranodon na costa continuam como estão (uma a cada 600 a 800 blocos de litoral).

### 12.2 A regra "Dinos no mundo normal"

Aba **Ecossistema** das Regras do Terrassic, salva por mundo. Padrão **0,35** (0,25 até a v1.0.1), de 0 a 1. Desde a v0.15.1 as regras não
mudam dentro do jogo (REGRAS.md): vale o `"dino_share"` do objeto `"rules"` de `config/terrassic-world.json` na hora
de criar o mundo.

| Valor | Efeito fora do Cretáceo |
|---|---|
| 0 | Nenhum dino nasce sozinho (ovos de spawn e o continente continuam) |
| 0,25 | Cerca de 1 animal em 4 a 5 é dino; reposição com um terço do alvo |
| 0,35 (padrão) | Cerca de 1 animal em 3 é dino; reposição com uns 54% do alvo |
| 0,5 | Metade e metade; reposição cheia |
| 1 | Sem limite: todos os dinos que o bioma tiver, como antes da v0.15 |

Nos biomas do Cretáceo (tipo de mundo Terrassic) a regra não muda nada: lá os dinos são a fauna.

### 12.3 Como funciona (técnico)

- `world/VanillaShare`: quando o gerador do Minecraft escolhe um dino da lista do bioma (nascimento natural ou na
  geração do chunk), ele passa com a chance `parte / (1 − parte) × peso do Minecraft / peso dos dinos`, contada por
  bioma e por categoria (terra ou mar). Exemplo, planície (pesos medidos no Mac, 118 do mod e 46 do Minecraft): 0,35 / 0,65 × 46 / 118 ≈ 21%.
- O sorteio é o mesmo para o bando inteiro (mesmo chunk, mesmo tick, mesma espécie): a manada nasce inteira ou não nasce.
- Bioma sem animal do Minecraft daquela categoria (as badlands): passa a parte (25%) do que nasceria.
- Chamado nas regras de nascimento de `DinosaurEntity` (terra) e `SwimmingDinosaur` (mar). Voadores já não nascem
  pelo gerador do Minecraft. O `EcoSpawner` não passa por esse sorteio; os alvos dele é que são multiplicados por
  `VanillaShare.ecoFactor` (o bioma onde o jogador está).

### 12.4 Testes no jogo (para o Rodrigo)

1. Criar mundo novo: o tipo vem em **Padrão**. Em Mais opções, os três tipos Terrassic ainda aparecem.
2. Andar uns 2.000 blocos por planícies, florestas e savanas: vacas, ovelhas, porcos e cavalos em quantidade normal,
   e de vez em quando um bando de dinos (uns 1 em 3 animais).
3. Com `"dino_share": 0` no objeto `"rules"` de `config/terrassic-world.json`, criar um mundo novo: não nascem dinos.
   Com 1: muitos dinos como antes.
4. Mundo do tipo Terrassic: os biomas do Cretáceo continuam cheios de dinos e sem animais do Minecraft.
5. Mundo antigo (de antes da v0.15): abre normal, a regra aparece com 0,35.
6. Mundo ou config de antes da v1.0.1 com 0,25 (o padrão antigo): passa sozinho para 0,35. Outro valor fica como está.
