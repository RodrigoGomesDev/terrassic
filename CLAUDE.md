# Terrassic — contexto para continuar em qualquer sessão do Claude

Leia este arquivo e o README.md antes de começar. Responda em português.
Autor do projeto: Rodrigo Gomes (Grupo Permaneo). Faça os commits no nome dele.

## O que é
Mod de dinossauros para Minecraft 1.20.1, Fabric + Forge (Architectury), modelos GeckoLib no estilo Cobblemon.
Versão atual: **v0.2.0** (tags git v0.1.0 e v0.2.0). A v0.1 compilou e rodou no Mac do Rodrigo (Fabric runClient).
A v0.2 rodou no Fabric (runClient) em 23/10/2026 sem crash; Forge ainda não testado.
Nome: o projeto se chamava **PrimalEra** e foi renomeado para **Terrassic** em 23/10/2026: mod id `terrassic`,
pacote `com.terrassic`, classe principal `Terrassic`, namespace `assets/terrassic` e `data/terrassic`.
Mundos salvos com a versão PrimalEra perdem dinossauros, ovos e itens do mod (o id antigo `primalera:` não existe mais).

## Stack
- Gradle 9.5.1, Architectury Loom 1.17-SNAPSHOT, plugin 3.5-SNAPSHOT, mapeamentos Mojang, Java 17 (rodar com JDK 21).
- Architectury API 9.2.14, GeckoLib 4.8.4, Forge 1.20.1-47.4.8, Fabric Loader 0.17.2, Fabric API 0.92.6+1.20.1.
- Testar: `./gradlew :fabric:runClient` ou `:forge:runClient`. Build: `./gradlew build`.
- NÃO use javax.annotation / org.jetbrains.annotations no common (não estão no classpath).

## Código (common/src/main/java/com/terrassic)
- `entity/DinosaurEntity` (extends TamableAnimal): sexo sincronizado (textura por sexo), domesticação,
  sentar/seguir, sela + montaria (pulo com espaço, tesoura tira a sela), procriação só macho+fêmea, procriação põe ovo-bloco, controllers GeckoLib
  ("movement": idle/walk/run/sit; "action": attack + extras via triggerAnim).
- `HerbivoreDinosaur` (lutador ou fugitivo, pasta) e `PredatorDinosaur` (caça, domesticável só filhote).
- `FlyingDinosaur` (à mão): voadores. Navegação de voo, plana, sem dano de queda, voo montado (pular decola/bate asas, olhar dirige, soltar plana). Precisa das animações `fly` e `glide`. Spawn por `checkFlyerSpawnRules` (areia, cascalho, pedra, grama).
- `SwimmingDinosaur` (à mão): répteis marinhos. Nado como golfinho (SmoothSwimming + WaterBoundPathNavigation), respira na água, seca após 60 s encalhado, some longe do jogador como golfinho, por enquanto só selvagem (sem domar, sem cria). Categoria WATER_CREATURE; spawn por `checkSeaSpawnRules`. Em `gen_resources.SPECIES` o 4º campo `None` = espécie sem bloco de ovo.
- Mixins: `common/src/main/resources/terrassic.mixins.json` (pacote `com.terrassic.mixin`), ligado em `fabric.mod.json` ("mixins") e em `forge/build.gradle` (`loom.forge.mixinConfig`). Hoje só `PlayerMixin`: a Lente de Âmbar conta como luneta (`isScoping`).
- Configuração: `config/terrassic.json` (`config/SpawnConfig.java`), lida uma vez na inicialização; multiplicador global e por espécie (`enabled`, `weight_multiplier`). Todo spawn em `ModSpawns` passa por ela.
- 15 espécies GERADAS por `tools/javagen/gen_species.py` (edite a tabela lá e rode o script, não edite os .java).
- Tamanhos: tabela `SIZES` em `gen_species.py` (1 bloco = 1 metro; escala do modelo, hitbox, filhote, sombra).
  O script lê `art/build_report.json` (medidas dos modelos) e gera as constantes WIDTH/HEIGHT/MODEL_SCALE/SHADOW,
  `babyScale()`, culling e altura da sela; `ModEntities` e `TerrassicClient` só leem essas constantes.
  Comparação visual: `art/tamanhos/comparacao_tamanhos.png`. A `render_scale` dos arquivos de tools/modelgen
  é só a escala de autoria (o "In game: scale ~..." nos comentários de lá está desatualizado).
- `block/DinoEggBlock` (choca em 3 estágios, filhote "marca" o jogador mais próximo).
- Blocos de construção primitivos em `ModBlocks.BUILDING` (aba própria `ModTabs.BUILDING`): palha (+escada, laje),
  esteira de palha, tapete de pele, pau a pique, paliçada de troncos, pedra empilhada (+escada, laje, muro),
  cerca de osso, painel de couro. Só materiais da época primitiva: nada de vidro, tijolo cozido ou metal.
- `item/` armas: SpearItem + `entity/ThrownSpear` (arremessável), ClubItem, FlintHatchetItem, ModTiers.
- `registry/` ModEntities, ModBlocks, ModItems, ModTabs. Ordem em Terrassic.init: tabs, entities, blocks, items.
- `client/` DinoGeoModel (textura _male/_female, esconde ossos male_display/female_display/saddle), renderers.
- `world/ModSpawns` spawn por bioma. `world/ModWorldgen`: veios de Rocha Fossilífera e Páginas Soltas em baús vanilla.
- `research/` (v0.3, mecânicas de cientista): `Knowledge` (o que cada jogador sabe: nível do Guia e pontos por espécie,
  páginas da Katarina, objetivos, contadores), salvo por jogador em `ResearchData` (SavedData do overworld, não no item),
  `Research` (eventos que enchem o Knowledge e completam objetivos; nunca move o jogador), `Objective` (12 objetivos do
  Capítulo 1, cada um é uma conquista vanilla `terrassic:chapter1/<id>`), `GuideSpecies` e `Lore` (GERADOS).
  Níveis do Guia: silhueta (fóssil na Mesa), avistado (16 blocos com visão), estudado (avistado + 3 pontos: fóssil 1,
  esboço 2, derrotar 3), domesticado. Estudado = domar mais fácil e +20% de dano contra a espécie.
- `network/ModNetwork`: pacotes servidor→cliente (Knowledge em NBT, abrir a tela de abertura). Receptores em `client/ClientHooks`.
- `client/NotebookScreen` (Caderno de Campo: Diário, Guia, Katarina, Relatório, desenhado sem textura) e `client/IntroScreen`.

## Assets e ferramentas
- Modelos: `tools/modelgen` (Python + Blockbench headless via Playwright; ver tools/modelgen/README.md).
  Exporta art/<especie>/<especie>.bbmodel, geo/animations/texturas para common/src/main/resources/assets/terrassic.
  Convenções: 16px = 1 bloco, animal olha para -Z, osso `head` = olhar (não animar; use `skull`),
  animações `animation.<especie>.<idle|walk|run|sit|attack|roar|graze|call|display>`.
- Sprites 16x16: `tools/spritegen/sprites.py` (ovos geradores únicos, armas, ovos-bloco).
- JSON (lang pt_br/en_us/es_es + variantes do espanhol, receitas, loot, modelos, blockstates): `tools/javagen/gen_resources.py`.
- Ciência: `tools/javagen/gen_science.py` (itens, Rocha Fossilífera, Mesa, receitas, worldgen, conquistas, `Lore.java`) e
  `tools/javagen/lore.py` (TODO o texto de história, Guia, objetivos e tela, nos 3 idiomas). Sprites em `tools/spritegen/science.py`.
  Espécie nova precisa de entrada em `GUIDE` (gen_species.py), em `lore.GUIDE` e um motivo em `FOSSIL_MOTIF` (science.py).
- Blocos de construção: texturas em `tools/spritegen/blocks.py`; JSON (modelos, blockstates, loot, receitas, tags
  minecraft:mineable/walls/fences/stairs/slabs) em `tools/javagen/gen_blocks.py`, chamado por gen_resources.py
  (que também junta o lang). Para um bloco novo: tabela BLOCKS em gen_blocks.py + textura em blocks.py + registro em ModBlocks.
- Tudo é autoral e gerado por código; referências só de medidas (Wikipedia). Não copiar arte de terceiros.

## Espécies (12)
Predadores: Tyrannosaurus, Spinosaurus, Dilophosaurus, Velociraptor, Compsognathus.
Herbívoros: Triceratops, Stegosaurus, Ankylosaurus, Brachiosaurus, Parasaurolophus, Pachycephalosaurus, Gallimimus.
Montáveis: T. rex, Triceratops, Brachiosaurus, Parasaurolophus, Gallimimus.

## Pendências conhecidas
- Testar v0.2 no Forge e conferir a build depois da renomeação para Terrassic.
- Tamanhos novos (24/10/2026, escala real) ainda não compilados/testados no jogo: conferir caminho na floresta,
  altura da sela, pés deslizando na caminhada dos gigantes e filhotes.
- Sons ainda são vanilla (placeholders).
- Montaria pula com espaço (barra de pulo do cavalo, força por espécie em `jump` no gen_species); tesoura tira a sela.
- Herbívoros selvagens só procriam depois de domesticados.
- Na pasta podem sobrar arquivos antigos da v0.1 (texturas <especie>.png sem _male/_female, GIFs): podem ser apagados.

## Roadmap e lista de criaturas
A lista completa das criaturas (152, organizadas POR ERA, seguindo a história) e a versão de cada uma estão em `docs/ROSTER.md`.
Consulte e atualize esse arquivo antes de adicionar uma espécie. Cada era é fechada jogável antes da próxima:
- v0.3–v0.9: Capítulo 1 (Cretáceo Superior, Overworld). v0.3 história + cientista (Caderno de Campo, fósseis, Mesa de Pesquisa,
  Lente de Âmbar, es_es, sons, pulo/tirar sela) + Pteranodon, Mosasaurus, Maiasaura; v0.4 céus; v0.5 Mar Interior; v0.6 manadas,
  carga e titãs; v0.7 predadores ápice + nocaute; v0.8 mundo Terrassic, estruturas, HUD, ambientação; v0.9 Altar do Salto e chefe.
- v1.0 "Ecos do Fim" (Capítulo 1 completo). v2.0 Cretáceo Inferior/Araripe, v3.0 Jurássico, v4.0 Triássico e final, v5.0 Era do Gelo.
- Stegosaurus, Brachiosaurus, Dilophosaurus e Compsognathus são jurássicos: ficam no Overworld como "vazamentos da Fenda" até a v3.0.
- Portes para 1.21.x.

## História, eras e escopo
- `docs/HISTORIA.md`: história (premissa "O Salto", Dra. Katarina Brandt, a Fenda, Altar do Salto), 4 capítulos indo para trás no tempo
  (Cretáceo Superior no Overworld, Cretáceo Inferior/Araripe, Jurássico, Triássico) + epílogo na Era do Gelo, ecossistema completo por era,
  mecânicas de cientista, avanço de capítulo com pulo, finais, mundo e livros. Aprovado pelo Rodrigo em 24/10/2026.
- Regra 0: o Minecraft é livre. Nunca mover o jogador de era automaticamente; eras sempre abertas e revisitáveis; a história nunca bloqueia o básico.
- `docs/ESCOPO.md`: um mod só, completo e autoral (sem modpack, sem mods de terceiros além das bibliotecas GeckoLib e Architectury embutidas),
  mods complementares futuros, pacote de texturas embutido, HUD próprio e ambientação.
- Todo texto em pt_br, en_us e es_es.

## Como registrar o progresso
Ao terminar uma etapa: atualize este arquivo (versão, pendências) e faça commit no nome do Rodrigo.
