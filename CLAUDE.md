# Terrassic — contexto para continuar em qualquer sessão do Claude

Leia `AGENTS.md`, `docs/COORDENACAO.md`, este arquivo e o README.md antes de começar. Responda em português.
Autor do projeto: Rodrigo Gomes. Faça os commits no nome dele.

## Coordenação atual (24/10/2026)

Projeto pessoal do Rodrigo, sem vínculo com qualquer empresa. A entrega consolidada fica na **main**.
Claude principal: features complexas na main. Claude secundário: features isoladas em `paralelo/*` com checkout
separado. Codex: integração, validação, estabilidade e desempenho. A frente de identidade visual continua própria.
Consulte `docs/COORDENACAO.md` antes de reservar arquivos ou iniciar uma fase; não execute a fila inteira por conta
da instrução de autonomia histórica abaixo. A v0.9 foi integrada na main até `3023eae`.
Validação de integridade sem regenerar assets: `python3 -B tools/validation/check_project.py`.
Build não equivale a teste no jogo; os estados e as evidências atuais ficam no quadro de coordenação.
Segunda entrega Codex: `docs/TESTES_SERVIDOR.md` registra inicialização dedicada e persistência de entidades
validadas em Fabric e Forge. Errantes selvagens sem nome são temporários e não deixam ninhos; os filhotes de
ovos selvagens também são errantes. Domados/nomeados e ovos colocados pelo jogador continuam persistentes.
Spawner e classes-base de IA receberam escalonamento e checagens antecipadas. Falta perfil de carga e teste
de comportamento com jogadores; não anunciar desempenho para 100 jogadores com base nesses testes.

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
- Regras do mundo estilo ARK (docs/REGRAS.md): `config/Rules` + `RulesData` (salvas por mundo, padrão no objeto `"rules"`
  de `config/terrassic-world.json`), enum `config/Rule` GERADO por `tools/javagen/gen_rules.py` (tabela RULES: chave, faixa,
  aba e textos nos 3 idiomas). Tela `client/RulesScreen` (botão no menu de pausa, `/terrassic regras`, Config do Forge),
  pacotes em `network/RulesNetwork`. Use `Rules.of(level).get(Rule.X)`. Ecossistema denso: `world/EcoSpawner` mantém
  terrestres, voadores e marinhos ao redor de cada jogador usando a lista de spawn do bioma; os que ele põe são "errantes"
  (`DinosaurEntity.isRoamer`, somem a 96+ blocos se selvagens e sem nome). Voadores selvagens voam em bandos (`ai/SoarGoal`).
- 53 espécies GERADAS por `tools/javagen/gen_species.py` (edite a tabela lá e rode o script, não edite os .java).
- REGRA (Rodrigo, 24/10/2026): toda espécie nova usa o tamanho real dos fósseis (topo das estimativas publicadas
  para adultos, 1 bloco = 1 metro), com a fonte anotada em `docs/TAMANHOS.md`.
- Tamanhos: tabela `SIZES` em `gen_species.py` (1 bloco = 1 metro; escala do modelo, hitbox, filhote, sombra).
  O script lê `art/build_report.json` (medidas dos modelos) e gera as constantes WIDTH/HEIGHT/MODEL_SCALE/SHADOW,
  `babyScale()`, culling e altura da sela; `ModEntities` e `TerrassicClient` só leem essas constantes.
  Comparação visual: `art/tamanhos/comparacao_tamanhos.png`. A `render_scale` dos arquivos de tools/modelgen
  é só a escala de autoria (o "In game: scale ~..." nos comentários de lá está desatualizado).
- `block/DinoEggBlock` (choca em 3 estágios, filhote "marca" o jogador mais próximo).
- Blocos de construção primitivos em `ModBlocks.BUILDING` (aba própria `ModTabs.BUILDING`), registrados pela lista
  GERADA `registry/BuildingBlocks.java`. Meta: catálogo de 336 blocos em 7 fases (doc "Terrassic — Catálogo de blocos
  primitivos"). Regras do Rodrigo: realistas, só materiais da época, e NUNCA cópia de bloco vanilla (por isso a
  pedra empilhada de pedregulho e o tapete de pele genérico saíram). Feito: lote 1 (palha, esteira, pau a pique,
  paliçada, cerca de osso, painel de couro) + fase 1 de pedras (calcário, folhelho, giz, sílex: natural, empilhada,
  lajeado, empilhada com musgo, com escada/laje/muro), com veios no mundo (sílex nasce dentro do giz) + fase 2
  (laterita na savana, quartzito nas montanhas, gnaisse, conglomerado, e seixos soltos das 8 rochas em praias,
  rios e savana) + fase 3 (madeiras Araucária, Ginkgo, Metassequoia: tronco, descascado, lenho, folhas, muda,
  tábuas lavradas com escada/laje, cerca e portão de galhos, paliçada, porta e alçapão de troncos; árvores nascem em
  floresta/savana/taiga/rio e as mudas crescem via `block/PrehistoricTreeGrower`). 153 blocos. A paliçada genérica
  saiu (cada madeira tem a sua) + fase 4 (Cipreste-do-pântano em pântano/rio, Feto Arbóreo na selva, e 19 plantas do
  Mesozoico: cavalinhas, Calamites, samambaias, cicadáceas, Williamsonia, Archaefructus, nenúfar, capim, licopódio,
  selaginela, hepática, líquen nas pedras da montanha, junco, alga de pântano, fungo-prateleira nos troncos; todas nascem
  no mundo). 200 blocos + fase 5 (pau a pique travado/com esteios/caiado, taipa de pilão, terra batida, 5 rebocos,
  16 pinturas rupestres viradas para o jogador via `block/FacingBlock`, coberturas de junco/cicadácea/samambaia com
  escada, laje e beiral inclinado, vime, cerca trançada, esteira e feixe de junco, rolo de corda, rede de fibra
  escalável como trepadeira). 251 blocos + fase 6 (couros esticados e painéis, e por espécie: tapete de couro
  `<espécie>_hide_rug`, troféu de crânio e crânio fóssil na rocha, gerados de `gen_resources.SPECIES`; crânio de
  espécie sem desenho em `SKULLS` de blocks.py usa o do velociraptor; osso, feixe de penas) + fase 7 (tochas de
  osso/resina/junco com versão de parede, lamparina, fogueira de pedras `block/HearthBlock`, varal, pilão, mó, bacia,
  camas de palha/couro e rede `block/PrimitiveBedBlock`, potes cru e queimado, cocho, ninhos, estacas
  `block/SpikesBlock`, armadilha, menir, totens, tambor `DrumBlock`, móbile `ChimesBlock`, cesto de 9 espaços
  `BasketBlock` + `registry/ModBlockEntities`). Blocos de modelo próprio: tabela PROPS em gen_blocks.py. Fase 8: crânio próprio por espécie
  (SKULLS em blocks.py; espécie nova precisa de uma linha lá, como do desenho do ovo), madeiras do Cretáceo II (Palmeira
  Sabal, Magnólia, Podocarpo, Platanus, com árvores no mundo), âmbar e resina (comum, de raw_amber/resin_jar; o Âmbar
  Temporal da história não é bloco), solos do Cretáceo (serrapilheiras, lama rachada, cinza vulcânica, turfa, solo
  laterítico, crosta de sal).
- `item/` armas: SpearItem + `entity/ThrownSpear` (arremessável), ClubItem, FlintHatchetItem, ModTiers.
- `registry/` ModEntities, ModBlocks, ModItems, ModTabs. Ordem em Terrassic.init: tabs, entities, blocks, items.
- `client/` DinoGeoModel (textura _male/_female, esconde ossos male_display/female_display/saddle), renderers.
- `world/ModSpawns` spawn por bioma. `world/ModWorldgen`: veios de Rocha Fossilífera e Páginas Soltas em baús vanilla.
- `research/` (v0.3, mecânicas de cientista): `Knowledge` (o que cada jogador sabe: nível do Guia e pontos por espécie,
  páginas da Katarina, objetivos, contadores), salvo por jogador em `ResearchData` (SavedData do overworld, não no item),
  `Research` (eventos que enchem o Knowledge, completam objetivos e dão conquistas com `Research.award`; nunca move o
  jogador), `Objective` (12 objetivos do Capítulo 1 em 4 temas; 2 de 3 = 1 fragmento de âmbar), `GuideSpecies` e `Lore` (GERADOS).
  Conquistas: árvore em `docs/CONQUISTAS.md`, gerada por `tools/javagen/conquistas.py` (aba por capítulo + aba Caderno de Campo;
  só entram as `ready=True`; o gerador confere ícones, o enum `Objective` e todo id usado em `Research.award`).
  Níveis do Guia: silhueta (fóssil na Mesa), avistado (16 blocos com visão), estudado (avistado + 3 pontos: fóssil 1,
  esboço 2, derrotar 3), domesticado. Estudado = domar mais fácil e +20% de dano contra a espécie.
- `network/ModNetwork`: pacotes servidor→cliente (Knowledge em NBT, abrir a tela de abertura). Receptores em `client/ClientHooks`.
- `client/NotebookScreen` (Caderno de Campo: Diário, Guia, Katarina, Relatório, desenhado sem textura) e `client/IntroScreen`.

## Assets e ferramentas
- Modelos: `tools/modelgen` (Python + Blockbench headless via Playwright; ver tools/modelgen/README.md).
  Exporta art/<especie>/<especie>.bbmodel, geo/animations/texturas para common/src/main/resources/assets/terrassic.
  Convenções: 16px = 1 bloco, animal olha para -Z, osso `head` = olhar (não animar; use `skull`),
  animações `animation.<especie>.<idle|walk|run|sit|attack|roar|graze|call|display>`.
  Planejadas para domesticação (todo modelo novo já deve ter): knockout, knocked_out, wake, eat, tame, beg, hatch
  (ver docs/ROSTER.md, seção "Domesticação: animações e telas").
- Sprites 16x16: `tools/spritegen/sprites.py` (ovos geradores únicos, armas, ovos-bloco).
- JSON (lang pt_br/en_us/es_es + variantes do espanhol, receitas, loot, modelos, blockstates): `tools/javagen/gen_resources.py`.
- Ciência: `tools/javagen/gen_science.py` (itens, Rocha Fossilífera, Mesa, receitas, worldgen, conquistas de `conquistas.py`, `Lore.java`) e
  `tools/javagen/lore.py` (TODO o texto de história, Guia, objetivos e tela, nos 3 idiomas). Sprites em `tools/spritegen/science.py`.
  Espécie nova precisa de entrada em `GUIDE` (gen_species.py), em `lore.GUIDE` e um motivo em `FOSSIL_MOTIF` (science.py).
- Blocos de construção: texturas em `tools/spritegen/blocks.py`, pintadas com o motor v2 `tools/spritegen/pixelkit.py`
  (grade de ÍNDICES de tom, 4 a 6 tons por material, aglomerados sem pixel solto, relevo de 1 px: borda clara em
  cima/esquerda, sombra embaixo/direita, junta no tom mais escuro; como as texturas vanilla) e domadas por
  `pk.tame` no build (contraste p95-p5 de luminância até 68, perto da mediana vanilla 64; motivos fortes têm teto
  próprio em TAME_CAPS). Meta medida no vanilla 1.20.1: 6 a 12 cores, contraste ~64, diferença entre vizinhos ~16.
  Estilo moderno (1.14+): face calma de um tom dominante (`pk.calm`), chanfro de 2 níveis (`pk.bevel`) e
  detalhes desenhados espalhados por ruído azul (`pk.scatter`), nunca ruído pixel a pixel.
  Mudas e plantas ainda usam o desenho antigo; tudo o resto vem da tabela BLOCKS de `tools/javagen/gen_blocks.py` (modelos, blockstates,
  loot, receitas de bancada e cortador de pedra, tags, veios de rocha, lang pt/en/es e o Java `BuildingBlocks.java`),
  chamado por gen_resources.py. Bloco novo: linha/família em gen_blocks.py + textura em blocks.py; material novo,
  case em `ModBlocks.material()`. Não editar BuildingBlocks.java à mão.
- Mundo Terrassic (v0.8, main 9da2414, `docs/MUNDO.md`): tipo de mundo "Terrassic" com os 11 biomas do Cretáceo
  (`world/CretaceousBiomes`, `CretaceousSurface`, `ModWorldgen`; JSON de biomas, tags e tipos de mundo gerados por
  `tools/javagen/gen_world.py`, chamado por gen_resources.py, e estruturas por `gen_structures.py`), sem animais nem
  monstros vanilla na superfície; estruturas (Cratera de Chegada, acampamentos, Sítio Fossilífero, Ossuário, Casa do Rio
  com o "Mate", Colônia de Ninhos: `world/ArrivalCrater`, `KatarinaRefuge`), Tempestades da Fenda (`world/RiftStorm`,
  `/terrassic tempestade`, `config/terrassic-world.json`), tela de título e dicas (`tools/capagen`, `menu_texts.py`) e HUD
  (`terrassic-client.json`). Espécie nova entra nos biomas pela tabela WORLD de gen_species.py (tag `terrassic:habitat/<palavra>`).
  Pedidos do Rodrigo em aberto: mundo menor tipo Pangeia cercada de mar e escolhido automaticamente; menu mais elaborado.
- Pacote de texturas por era (`docs/TEXTURAS_ERA.md`): `tools/texpack` gera o pacote embutido
  `common/src/main/resources/resourcepacks/<era>/` (Cretáceo: 21 texturas vanilla redesenhadas, formato 15); Fabric o registra
  ligado por padrão (`TerrassicFabric.registerEraPacks`), Forge via `forge/EraPacks` (`AddPackFindersEvent`, ligado uma vez na
  primeira execução, `config/terrassic-packs.json`). As chaves de lang do pacote vêm de `tools/texpack/pack_lang.py`, mescladas por
  gen_resources.py. Propostas de progressão (sete eixos, aguardam o Rodrigo): `docs/PROGRESSAO.md`.
- Comida do Cretáceo (`docs/FAUNA.md`): itens `raw_/cooked_dino_meat` e `raw_/cooked_prime_meat` (ModItems, seção
  "Cretaceous food"); o loot de toda espécie troca beef/mutton/chicken pela carne própria (`MEAT`/`PRIME`/`SEA_MEAT` em
  gen_resources.py, receitas de forno/defumador/fogueira), sprites em `sprites.py` (`meats()`). Fauna de caça do Cretáceo
  (Leptoceratops, Vegavis, Mesodma, Basilemys, Enchodus, Lepisosteus) substitui os animais vanilla do mundo Terrassic.
- Tudo é autoral e gerado por código; referências só de medidas (Wikipedia). Não copiar arte de terceiros.

## Espécies (12)
Predadores: Tyrannosaurus, Spinosaurus, Dilophosaurus, Velociraptor, Compsognathus.
Herbívoros: Triceratops, Stegosaurus, Ankylosaurus, Brachiosaurus, Parasaurolophus, Pachycephalosaurus, Gallimimus.
Montáveis: T. rex, Triceratops, Brachiosaurus, Parasaurolophus, Gallimimus.

## Pendências conhecidas
- Testar v0.2 no Forge e conferir a build depois da renomeação para Terrassic.
- Tamanhos novos (24/10/2026, escala real, aprovados) ainda não compilados/testados no jogo: conferir caminho na floresta,
  altura da sela, pés deslizando na caminhada dos gigantes e filhotes.
- Sons ainda são vanilla (placeholders).
- Montaria pula com espaço (barra de pulo do cavalo, força por espécie em `jump` no gen_species); tesoura tira a sela.
- Herbívoros selvagens só procriam depois de domesticados.
- Na pasta podem sobrar arquivos antigos da v0.1 (texturas <especie>.png sem _male/_female, GIFs): podem ser apagados.

## Roadmap e lista de criaturas
- **`docs/ROADMAP.md`: o roadmap único, organizado POR ERA**: visão, regras fixas, a fila de cada era (modelos 3D, criaturas,
  ovos, vozes, flora, blocos, mundo, estruturas, chefe), as frentes transversais, o que anda em paralelo, as versões e as
  perguntas abertas. Atualize a linha da fase lá quando ela mudar de estado.
- REGRA (Rodrigo, 24/10/2026): só se produz conteúdo da ERA ATUAL (hoje o Cretáceo Superior, até a v1.0), na ordem da fila
  dela; nada de gerar modelos 3D "um pouco de cada era". Arquétipo nasce quando a primeira espécie da fila precisa dele.
- REGRA (Rodrigo, 24/10/2026): ser autônomo. Implementar todas as fases possíveis sem esperar; se o limite de uso acabar,
  voltar assim que ele renovar, começando pelos modelos 3D e depois as fases restantes do roadmap.
- Plano de criaturas por versão: `docs/ROSTER.md` (152, por era). Bestiário completo: `docs/bestiario/` (1.203 criaturas do mundo todo),
  gerado por `tools/roster/gen_roster.py` a partir de `tools/roster/roster_data.py` (não edite os .md à mão). Consulte antes de adicionar uma espécie.
- Uma era por vez: v0.3–v0.9 Capítulo 1 (Cretáceo Superior), **v1.0 "Ecos do Fim"**, v2.0 Penas e Cinzas, v3.0 Jurássico,
  v4.0 Triássico e final, v5.0 Era do Gelo. Stegosaurus, Brachiosaurus, Dilophosaurus e Compsognathus são jurássicos e ficam
  no Overworld como "vazamentos da Fenda" até a v3.0.

## História, eras e escopo
- `docs/HISTORIA.md`: história (premissa "O Salto", Dra. Katarina Usha, a Fenda, Altar do Salto), 4 capítulos indo para trás no tempo
  (Cretáceo Superior no Overworld, Cretáceo Inferior/Penas e Cinzas, Jurássico, Triássico) + epílogo na Era do Gelo, ecossistema completo por era,
  mecânicas de cientista, avanço de capítulo com pulo, finais, mundo e livros. Aprovado pelo Rodrigo em 24/10/2026.
- Regra 0: o Minecraft é livre. Nunca mover o jogador de era automaticamente; eras sempre abertas e revisitáveis; a história nunca bloqueia o básico.
- `docs/ESCOPO.md`: um mod só, completo e autoral (sem modpack, sem mods de terceiros além das bibliotecas GeckoLib e Architectury embutidas),
  mods complementares futuros, pacote de texturas embutido, HUD próprio e ambientação.
- Todo texto em pt_br, en_us e es_es.

## Como registrar o progresso
Ao terminar uma etapa: atualize este arquivo (versão, pendências) e faça commit no nome do Rodrigo.
