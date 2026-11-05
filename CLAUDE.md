# Terrassic — contexto para continuar em qualquer sessão do Claude

Leia `AGENTS.md`, `docs/COORDENACAO.md`, este arquivo e o README.md antes de começar. Responda em português.
Autor do projeto: Rodrigo Gomes. Faça os commits no nome dele.

## Coordenação atual (25/10/2026)

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
Spawner e classes-base de IA receberam escalonamento e checagens antecipadas. Faltam testes de comportamento
com jogadores completos e a validação da meta de 100 jogadores ativos; não anunciar essa capacidade com base nos smoke tests.
Terceira entrega Codex: Caderno salvo em arquivos `terrassic_research_<uuid>.dat`, migração preguiçosa do arquivo
global antigo preservado, dirty tracking automático em `Knowledge` e sincronização incremental com fallback para
o snapshot completo. Leia `docs/CADERNO_DADOS.md` antes de alterar o conhecimento; `pages()` é somente leitura,
use `addPage()`. Regressões de dados/protocolo fazem parte da build (`:common:researchRegression`).
Entregas seguintes: clientes locais de protocolo passaram em Fabric e Forge com páginas por UUID, snapshot/delta,
troca de dimensão, morte/respawn, reconexão e reinício (`CADERNO_DADOS.md`). Perfis JFR locais passaram até
16 conexões nos dois loaders e 100 no Fabric (`PERFIL_LOCAL.md`); são clientes estacionários sem renderização,
não uma validação de 100 jogadores ativos. A CI no GitHub valida integridade, fixtures, orçamento e build dos dois
loaders, incluindo regressões de pesquisa. `tools/validation/README.md` reúne os comandos.
Fauna 108-113 integrada: 59 espécies. Nocaute v0.7 também integrado (`DOMESTICACAO.md`): torpor, alimentar derrubado,
eficiência, erva, zarabatana e dardo. Codex validou 18 casos de persistência/interação nos dois loaders, incluindo
correções de eficiência antes da primeira comida e dano rejeitado (`TESTES_NOCAUTE.md`); consultar as reservas antes de alterar
`DinosaurEntity`. Ainda faltam inventário de alimentação, boleadeira e informações de dificuldade no Guia.
Regressão complementar de zarabatana e domesticação aquática: 22/22 passaram nos dois loaders
(`docs/TESTES_DARDOS.md`). Dose de torpor em alvo acordado agora depende de dano aceito; disparos reais, munição,
cooldown, manutenção submersa, alimentação e reinício foram exercitados. O animal aquático começa inconsciente
por NBT; combate aquático desde um alvo acordado e revisão visual continuam pendentes. Arquivos liberados.
Identidade de `terrassic-sync` integrada na main em `e4bbe9ef`: fontes, botões, marca proposta, licenças e textos.
Ícone e letreiro ativos preservados; fontes/telas ainda exigem revisão visual no jogo. Sync é transporte de bundles,
não outro checkout: seu LEIA-ME já registra a integração; não repetir merges dos bundles antigos.
Licença: código LGPL-3.0 (`LICENSE` + `COPYING`), assets All Rights Reserved com permissões explícitas
(`LICENSE-ASSETS.md`), contribuições pelo `CLA.md`. Commits: **Rodrigo Gomes <rodrigogomessims@gmail.com>**, sem linha
de coautoria de IA (pedido do Rodrigo, 24/10/2026).

## O que é
Mod de dinossauros para Minecraft 1.20.1, Fabric + Forge (Architectury), modelos GeckoLib no estilo Cobblemon.
Versão atual: **v1.1.4** (01/11/2026, acabamento das armas: dardo cravado, dose na invencibilidade, espirais, dispensador; Guia de Bolso desde a v1.1.2, docs/AJUDA.md; tags git v0.1.0, v0.2.0, v1.0.0, v1.0.1, v1.0.2, v1.1.0, v1.1.1, v1.1.2 e v1.1.3; `mod_version` em gradle.properties). A v0.1 compilou e rodou no Mac do Rodrigo (Fabric runClient).
**1.7.0 (04/11/2026, `mod_version`)**: feedback de jogador em `docs/FEEDBACK_1_7.md` — apito a 96 blocos e lista "Meus dinos"
com rastreio (`entity/TamedRegistry`, `network/TamedNetwork`, `client/MyDinosScreen`, `client/DinoTracker`, agachado + H,
`/terrassic dinos`); defesa e ordens contra mobs de outros mods (`DinosaurEntity.provokes`); clavas a 0,25/0,2 ataques/s;
nocaute de 20 s (regra `knockout_seconds`) que não acaba enquanto o bicho come; spawn 0,25 e regra `predator_spawns` 0,4;
vida x2 (`gen_species.health_of`, salvos migram); doma por progresso com pilhas de carne (`foodGoal`); Guia de Bolso com
"Os dinossauros" e "Domesticação"; Better Combat (`data/terrassic/weapon_attributes`). Compilado só contra o jar do
Minecraft da loom-cache; build Gradle e teste no jogo pendentes.
**1.8.0 (05/11/2026, `mod_version`)**: três refeitos com estudo próprio (Estiracossauro, Deinossuco, Elasmossauro; rigs
`Centrosaurine`, `Crocodylian`, `Plesiosaurid`), Manta de Corrida e Sela de Pescoço, ovos e ninhos novos, e as correções
do teste de comportamento (`docs/TESTES_1_8.md`: `ai/DinoBreedGoal`, alvo morto, presa do Deinossuco, ovo na margem).
**1.7.1 (05/11/2026, `mod_version`)**: Guia de Bolso rediagramado (margens, índice numa página dupla, sem linha
órfã, tópicos curtos dividindo página) e sprite de livro; as espécies saíram do Guia para quatro **Bestiários** fabricáveis
(Carnívoros, Herbívoros, Voadores, Marinhos; `VOLUMES` em `gen_pocket_guide.py`, `docs/AJUDA.md`). Fotos de todas as
páginas: fase `guide` do `PartsShowcase`. Pelo `VERSOES.md` seria 1.8.0; o Rodrigo escolheu 1.7.1.
**Partes de acerto (1.7, `docs/PLANO_PARTES.md`)**: cabeça 125%, pescoço 100%, cauda 75% nas 13 espécies refeitas
(`entity/parts/DinoPart`, mixins em `mixin/parts`, medidas de `tools/javagen/parts.py` via `gen_species.PARTS_SPECIES`;
espécie refeita nova entra lá); mordida medida da cabeça (`ai/HeadMeleeAttackGoal`). Regressão: `parts_regression.py`.
A `mc/1.21.1` tem a 1.7 inteira portada (Fabric + NeoForge compilam; regressões de protocolo só Fabric nessa branch).
Partes seguem o modelo animado (três layouts: em pé, deitado, cabeça baixa; posição por quadro no cliente,
`PartFrameMixin`). Validação da 1.7 estável (05/11): tabela em `docs/FEEDBACK_1_7.md`; teste no cliente real com
`client/dev/PartsShowcase` (`TERRASSIC_PARTS_SHOWCASE=1`, fases `still,flight,moving,feedback,bettercombat,density`);
Better Combat no cliente de teste com `./gradlew :fabric:runClient -PbetterCombat`.
A v0.2 rodou no Fabric (runClient) em 23/10/2026 sem crash; o cliente gráfico Forge ainda não foi validado.
Os servidores dedicados Fabric e Forge foram validados posteriormente pelos roteiros de entidades e Caderno.
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
- `Raptor` (à mão, rig do Velociraptor v3): 28 animações (`tools/modelgen/handmade/velociraptor`, tabela `WHEN` em build.py), bate e corre em `ai/RaptorStrikeGoal` (espreita, salto com abertura de 1,5x, pino de presa menor, mordida e chute com o golpe no tempo da animação, salto para trás) e `ai/RaptorRetreatGoal` (domado abaixo de 30% recua para trás do dono até 60%). Arreio de caça: item `VELOCIRAPTOR_HARNESS` no osso `saddle`, +4 de armadura, nunca montável. Domado recupera 1 HP a cada 4 s após 10 s sem dano, se comeu nos últimos 5 min. Bandos de 1 a 3.
- `Abelisaur` (à mão, rig do Carnotaurus, 33 animações, `tools/modelgen/handmade/carnotaurus`) e `Giganotosaurine` (à mão, rig do Giganotosaurus, 35 animações, `tools/modelgen/handmade/giganotosaurus`) são vidas de `ApexTheropod`, desenhadas a 24 px/m (escala 0,667). `reachScale()` escala as distâncias de mordida do T. rex para cada rig; `pauseAfter()` dá a pausa depois do golpe em `ai/ApexBiteGoal` (o Giganotossauro corta, recua, olha de lado e circula, e anda em par). Rig novo: conferir o assento pela sela (`ride_offset` = topo do assento - 0,2 bloco, dividido pela escala).
- Alfas (`docs/ALFAS.md`, `entity/Alphas`): animal raro, maior e mais forte, com pele própria por sexo (`<id>_alpha_male/female.png`), aura em `client/AlphaAura`, regras na aba Alfas e registro em `terrassic_alphas.dat`. Só o T. rex tem alfa; espécie nova entra em `Alphas.SPECIES` quando as peles estiverem aprovadas. `/terrassic alfa <espécie> [macho|femea]` para testar.
- `Protoceratopsid` (à mão, rig do Protoceratops, 26 animações, a 48 px/m, `tools/modelgen/handmade/protoceratops`): primeiro quadrúpede dos rigs feitos à mão. REGRA (Rodrigo, 02/11/2026): toda espécie tem modelo e cor únicos; `docs/CORES.md` e `tools/modelgen/handmade/_engine/colourcheck.py` medem a pele nova contra as outras.
- `Centrosaurine` (à mão, rig do Styracosaurus, 25 animações, a 32 px/m, `tools/modelgen/handmade/styracosaurus`): primeiro
  refeito da 1.8 (estudo aprovado em 05/11/2026). Coroa de espinhos em `adult_frill` (longos em `male_display`, curtos em
  `female_display`), pontinhas do filhote em `young_frill`; raspa o chão antes da investida, exibe a coroa a predadores,
  machos se exibem lado a lado; Manta de Corrida própria (`STYRACOSAURUS_SADDLE`); ninho em monte de talos de junco
  (`tools/spritegen/styr_extras.py`). Fotos do jogo: fase `photo` do `PartsShowcase`.
- `Crocodylian` (à mão, rig do Deinosuchus, 23 animações, a 20 px/m, `tools/modelgen/handmade/deinosuchus`): segundo
  refeito da 1.8. Boia como tronco parado na água (`float`), bote da beira d'água no primeiro golpe, giro da morte em
  alvo na água, toma sol de boca aberta perto da água, o macho berra na água; não é montável. Ninho: cova na areia da
  praia que a mãe abre perto de chocar (`tools/spritegen/deino_extras.py`).
- `Plesiosaurid` (à mão, rig do Elasmosaurus, 21 animações, a 20 px/m, `tools/modelgen/handmade/elasmosaurus`): terceiro
  refeito da 1.8. Voa debaixo d'água com as quatro nadadeiras, pescoço de sete ossos quase reto, toda mordida é o bote
  de pescoço, sobe para respirar e mergulha, engole pedras no fundo; Sela de Pescoço própria (`ELASMOSAURUS_SADDLE`,
  `tools/spritegen/elas_extras.py`); sem ovo (pare filhotes vivos).
- Testes da 1.8 (`docs/TESTES_1_8.md`): `client/dev/BehaviorTest` (`TERRASSIC_BEHAVIOR_TEST=1`) monta arenas e registra os
  comportamentos que os bichos fazem sozinhos, doma, sela, montaria, procriação e choco. Achou e corrigiu: Deinossuco
  caçando a própria espécie, alvo morto bloqueando a doma, procriação de bichos grandes (`ai/DinoBreedGoal` em todas as
  bases) e ovo perdido na água (lugar do ovo procurado até 8 blocos).
- `SwimmingDinosaur` (à mão): répteis marinhos. Nado como golfinho (SmoothSwimming + WaterBoundPathNavigation), respira na água, seca após 60 s encalhado, some longe do jogador como golfinho, por enquanto só selvagem (sem domar, sem cria). Categoria WATER_CREATURE; spawn por `checkSeaSpawnRules`. Em `gen_resources.SPECIES` o 4º campo `None` = espécie sem bloco de ovo.
- Mixins: `common/src/main/resources/terrassic.mixins.json` (pacote `com.terrassic.mixin`), ligado em `fabric.mod.json` ("mixins") e em `forge/build.gradle` (`loom.forge.mixinConfig`). Hoje só `PlayerMixin`: a Lente de Âmbar conta como luneta (`isScoping`).
- Configuração: `config/terrassic.json` (`config/SpawnConfig.java`), lida uma vez na inicialização; multiplicador global e por espécie (`enabled`, `weight_multiplier`). Todo spawn em `ModSpawns` passa por ela.
- Regras do mundo estilo ARK (docs/REGRAS.md): `config/Rules` + `RulesData` (salvas por mundo, padrão no objeto `"rules"`
  de `config/terrassic-world.json`), enum `config/Rule` GERADO por `tools/javagen/gen_rules.py` (tabela RULES: chave, faixa,
  aba e textos nos 3 idiomas). Tela `client/RulesScreen` (botão no menu de pausa, `/terrassic regras`, Config do Forge),
  pacotes em `network/RulesNetwork`. Use `Rules.of(level).get(Rule.X)`. Ecossistema denso: `world/EcoSpawner` mantém
  terrestres, voadores e marinhos ao redor de cada jogador usando a lista de spawn do bioma; os que ele põe são "errantes"
  (`DinosaurEntity.isRoamer`, somem a 96+ blocos se selvagens e sem nome). Voadores selvagens voam em bandos (`ai/SoarGoal`).
- 59 espécies GERADAS por `tools/javagen/gen_species.py` (edite a tabela lá e rode o script, não edite os .java).
- REGRA (Rodrigo, 24/10/2026): toda espécie nova usa o tamanho real dos fósseis (topo das estimativas publicadas
  para adultos), com a fonte anotada em `docs/TAMANHOS.md`. Desde 05/11/2026 o jogador é uma pessoa de 1,70 m: 1 metro =
  1,059 bloco (`METRE` em `gen_species.py`, aplicado na geração; a tabela continua em metros).
- Tamanhos: tabela `SIZES` em `gen_species.py` (em metros, vezes `METRE`; escala do modelo, hitbox, filhote, sombra).
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
- `item/` armas: SpearItem + `entity/ThrownSpear` (arremessável), ClubItem, FlintHatchetItem, ModTiers; BolaItem +
  `entity/ThrownBola` (v1.1, amarra e derruba voadores; `docs/ARMAS.md`).
- `registry/` ModEntities, ModBlocks, ModItems, ModTabs. Ordem em Terrassic.init: tabs, entities, blocks, items.
- `client/` DinoGeoModel (textura _male/_female, esconde ossos male_display/female_display/saddle), renderers.
- `world/ModSpawns` spawn por bioma. `world/ModWorldgen`: veios de Rocha Fossilífera e Páginas Soltas em baús vanilla.
- `research/` (v0.3, mecânicas de cientista): `Knowledge` (o que cada jogador sabe: nível do Guia e pontos por espécie,
  páginas da Katarina, objetivos, contadores), salvo por UUID em `ResearchData` (SavedData do overworld, não no item;
  `docs/CADERNO_DADOS.md`),
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
- Blocos de construção: texturas em `tools/spritegen/blocks.py`. As SUPERFÍCIES (pedras, madeiras, folhas, palha,
  telhados, esteiras, vime, pau a pique, rebocos, taipa, solos, âmbar, couros e tapetes) são desenhadas pelo mesmo
  motor dos pacotes de era, em `tools/texpack/blocos.py` (receitas nossas; tex/stamps/fit/api/materials/woods/leaves são
  da thread de progressão, não mexa): mapa de tons com base calma + detalhes carimbados por ruído azul, paleta ajustada
  (`fit`) para o BRILHO e o matiz do material real e o CONTRASTE do bloco vanilla do mesmo papel (`own(cor, papel)`,
  ROLE; `drift()` lista quem passa de 40 do papel). Fósseis de crânio são assentados na pedra nova da era.
  CHÃO (padrão aprovado pelo Rodrigo em 25/10): rochas, solos e âmbar bruto vêm de `tools/texpack/chao.py` e as folhas
  de `folhas.py`. Regra: nada pode repetir de longe. Rocha = grão fino (6 tons, `macro` <= 4; com junta <= 7,5; vítreo
  8 a 10), solo = torrões de 2 a 3 px (`torroes.py`), cores calmas (saturação <= 0,50), junta nunca quase preta.
  Medir com progressao/estudo/metricas.py e mostrar numa cena (estudo/cena) antes de commitar. Giro aleatório por
  bloco nos blockstates (gen_blocks: FREE_TURN, BEDDED_TURN, TOP_TURN), como a terra e a pedra do vanilla.
  MADEIRAS (troncos, descascados, tábuas) vêm de `tools/texpack/madeira.py` (veios longos, 4 tábuas, anéis de 2 px,
  saturação ~0,48) e PAREDES e TELHADOS (rebocos, pau a pique, enxaimel, caiado, taipa, palhas, esteiras) de
  `tools/texpack/paredes.py`, no mesmo padrão calmo (cena da aldeia: progressao/estudo/cena/cena4.py).
  Os MOTIVOS desenhados (crânios, totens, pinturas, portas, vasos, tochas, plantas) ainda usam o motor v2
  `tools/spritegen/pixelkit.py` (grade de índices de tom) domados por `pk.tame` (contraste até 68; TAME_CAPS).
  Meta medida no vanilla 1.20.1: 6 a 12 cores, contraste ~64, diferença entre vizinhos ~16.
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
- Identidade visual (`docs/IDENTIDADE.md`): toda tela do mod usa a paleta `client/ui/TerrassicPalette`, os componentes
  `client/ui/TerrassicUi`/`TerrassicButton` (nunca o botão cinza do vanilla) e as fontes próprias via
  `client/ui/TerrassicFonts`: Sedimento (interface), Entalhe (títulos), Caderno (o que a Katarina escreveu). Fontes geradas
  por `tools/fontgen/build.py` (bitmap do Minecraft + TrueType em `art/identidade/fontes/`); kit de marca por `tools/capagen/brand.py`.
- Tudo é autoral e gerado por código; referências só de medidas (Wikipedia). Não copiar arte de terceiros.

## Espécies (59 registradas, 55 ativas)
59 espécies em `gen_species.SPECIES`. Na v1 só o Cretáceo Superior está ligado: Stegosaurus, Brachiosaurus,
Dilophosaurus e Compsognathus (jurássicos) continuam registrados, mas não nascem. Lista, era e status de cada uma
em `docs/ROSTER.md`; tamanhos em `docs/TAMANHOS.md`.

## Pendências conhecidas
- Receitas no livro de receitas (v1.0.2): `tools/javagen/gen_recipe_unlocks.py` (chamado no fim do gen_resources)
  gera uma conquista oculta por receita em `data/terrassic/advancements/recipes/`; pegar um ingrediente libera a receita.
  Receita nova não precisa de nada a mais: basta rodar o gen_resources.
- Testar v0.2 no Forge e conferir a build depois da renomeação para Terrassic.
- Tamanhos novos (24/10/2026, escala real, aprovados) ainda não compilados/testados no jogo: conferir caminho na floresta,
  altura da sela, pés deslizando na caminhada dos gigantes e filhotes.
- Vozes próprias por espécie (v3, sintetizadas em `tools/soundgen`, ver `docs/SONS.md`); ainda não ouvidas dentro do jogo.
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
- **v0.10 (30/10/2026): modo história DESLIGADO, nada apagado.** A v1 estável é só o Cretáceo: dinossauros, itens, Guia de Campo e Mapa.
  Todo código de história pergunta `config/Story.enabled()` (chave "historia" em `config/terrassic-world.json`, padrão false);
  o cliente recebe o valor no login (`ClientResearch.story()`). Eras ativas em `config/Eras.java` (só Cretáceo): espécies de
  outras eras ficam registradas, mas sem spawn, fora do criativo, do Guia e dos baús. Código novo de história deve passar por esses portões.
- `docs/ESCOPO.md`: um mod só, completo e autoral (sem modpack, sem mods de terceiros além das bibliotecas GeckoLib e Architectury embutidas),
  mods complementares futuros, pacote de texturas embutido, HUD próprio e ambientação.
- Todo texto em pt_br, en_us e es_es.

## Discord
Bot da comunidade: **Rexpert** (`/Users/rodrigogs/projects/rexpert`, repositório à parte, não commitado aqui).
Suporte, diagnóstico de log, Guia de Campo, relatos de bug e avisos; documentado em `rexpert/README.md` e
`rexpert/docs/ROADMAP.md`. Rodando no homelab do Rodrigo (`rexpert/docs/HOMELAB.md`), token nunca neste repositório.
- **Avisos de versão têm dois canais, os dois postados pelo Rexpert:** `#avisos` quando aparece uma **tag** `vX.Y.Z`
  (lançamento oficial) e `#builds` quando `mod_version` sobe em `gradle.properties` na `main`, **sem precisar de
  tag** (o Rexpert confere a cada 30 min; `rexpert/src/lib/builds.js`). Até 05/11/2026 o `#builds` era um webhook
  deste repositório (`discord-build.yml`, "Terrassic Builds"); saiu para o bot postar com a própria cara.
- **O texto dos avisos é em inglês** (o servidor é organizado em inglês, pedido do Rodrigo em 05/11/2026): os dois
  avisos (#builds e #avisos) publicam a seção `## English` de `docs/changelog/X.Y.Z.md`, o mesmo changelog das lojas,
  que entra no repositório junto com a versão (`docs/VERSOES.md`, passo 5). Os commits continuam em português e não vão
  mais para o Discord.
- **Terceiro canal, `#new-species`:** quem avisa é o repositório do **site** (`terrassic-site`,
  `.github/workflows/discord-species.yml`), **só quando a arte de anúncio APROVADA entra em
  `public/assets/announce/<id>.webp`** (ou `.png`/`.jpg`, até 8 MB): posta essa imagem e a ficha do Guia, em inglês.
  A arte é feita e aprovada à mão (pedido do Rodrigo em 05/11/2026: nada de imagem automática). Marcar a espécie em
  `models.ready` só atualiza o site; trocar uma arte que já está lá não posta de novo. Ao liberar uma espécie refeita
  no site, rode `npm run build && npm run thumbs` lá antes do push.
  Estrutura do servidor (canais, cargos, banners, painéis): `rexpert/docs/SERVIDOR.md`.
- Daqui para frente, a versão em `gradle.properties` é o sinal de "saiu build nova" para a comunidade: ao fechar
  um lote de trabalho que vale avisar, suba `mod_version`. Taguear (`git tag vX.Y.Z`) continua sendo só para quando
  quiser o anúncio oficial maior em `#avisos`; passou muito tempo sem taguear (`v1.1.4` → `1.5.0` direto em
  `gradle.properties`, 39 commits sem tag em 02/11/2026) e `#avisos` ficou mudo nesse meio tempo — não é bug do bot.

## Versões
Regra em `docs/VERSOES.md` (Rodrigo, 05/11/2026; seguir sempre, sem perguntar): SemVer (correção = conserto, menor =
conteúdo ou mecânica nova, maior = era nova ou quebra de mundo); o mesmo número nas duas branches; o número sobe só
quando a build vai para `~/Desktop/terrassic-builds`; o Codex publica e põe o changelog; depois push da main e da
mc/1.21.1 (aviso no #builds).

## Como registrar o progresso
Ao terminar uma etapa: atualize este arquivo (versão, pendências) e faça commit no nome do Rodrigo.
