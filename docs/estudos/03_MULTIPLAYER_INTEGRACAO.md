# Terrassic: multiplayer grande e integração com modpacks

Pesquisa de 24/10/2026. Base: código do repositório (`/home/claude/terrassic`, branch `paralelo/v0.9-salto`, mod 1.20.1, Architectury + GeckoLib 4.8.4) e README/código-fonte de projetos públicos lidos nesta sessão. Os links marcados com **(não acessado)** são referências conhecidas que o proxy desta sessão bloqueou; confira antes de citar em público. Números marcados com **(estimativa)** são contas de ordem de grandeza, não medidas. Antes de decidir qualquer coisa com base neles, meça com o spark.

---

## 1. Resumo executivo

1. **O EcoSpawner, do jeito que está, não aguenta 100-300 jogadores.** As metas por jogador (18 terrestres + 8 voadores + 12 marinhos = 38) vezes 300 jogadores dão cerca de 11.400 dinossauros com IA completa. Com um orçamento realista de cerca de 20 ms por tick para IA, sobram ~1,7 µs por dino por tick, o que não existe para IA de manada, caça e fome **(estimativa)**. O teto global (`max_creatures` = 400, `config/Rule.java:28`) "resolve" isso de um jeito injusto: os primeiros jogadores da lista ficam com tudo e os outros com nada (`EcoSpawner.java:112-114`).
2. **A população se acumula no save.** Os errantes só somem quando a entidade está *tickando* e longe. Em servidor com simulation-distance 6-8, eles congelam na borda e vão para o disco quando o chunk descarrega. Ninhos de errantes viram ovos que chocam filhotes **permanentes**.
3. **O que mais pesa na IA:** varreduras de entidades sem filtro barato antes, a cada 2 ticks. O pior caso é `AvoidEntityGoal<DinosaurEntity>` em todo herbívoro (`HerbivoreDinosaur.java:89-90`). Depois vêm as varreduras de blocos por tick dos gigantes em carga (`Argentinosaurus.java:147-163`) e o tracking range de até 18 chunks (`ModEntities.java:210-215`).
4. **Dados por jogador** num único `SavedData` com todos os UUIDs (`ResearchData.java`) crescem sem limite, são gravados de uma vez só no thread principal e não seguem o jogador numa rede Velocity com vários servidores.
5. **Para modpacks**, faltam: dietas e spawns ajustáveis por datapack ou tags (hoje as dietas são `Ingredient.of(Items...)` fixos no código, `Velociraptor.java:32`), integrações opcionais (Jade, EMI/JEI/REI, KubeJS, FTB Quests), respeito a claims quando um dino montado quebra blocos e uma licença clara para modpacks (hoje `All-Rights-Reserved`, sem permissão explícita).
6. **O plano** (seção 8) tem três fases. Agora: correções baratas e de alto impacto. Até a v1.0: LOD de IA, spawner orçado e dados por jogador em arquivos separados. Depois: datapacks completos, APIs e pathfinding próprio para gigantes.

---

## 2. O que derruba o TPS em mods de criaturas

O servidor tem 50 ms por tick (MSPT). Em servidores modded grandes, o tempo costuma ir para estes lugares, em ordem típica (estimativa baseada em perfis de spark de servidores modded):

| Fonte | Por que custa | Como aparece no spark |
|---|---|---|
| **Seleção de metas (GoalSelector)** | No 1.20.1, o `Mob.serverAiStep` reavalia `canUse()` de todas as metas paradas a cada 2 ticks. Metas que varrem entidades (`AvoidEntityGoal`, `NearestAttackableTargetGoal`, buscas de manada) custam O(n) por mob, ou seja, O(n²) numa manada. | `GoalSelector.tick` → `Level.getEntities` / `EntitySectionStorage` |
| **Pathfinding de mobs grandes** | `WalkNodeEvaluator` testa o tipo de bloco em largura × altura × largura para cada nó. Um hitbox 6×10 testa cerca de 360 blocos por nó, contra 2 de um zumbi (estimativa pela lógica do vanilla). Além disso, gigantes falham mais caminhos em floresta e ficam recalculando. | `PathFinder.findPath`, `WalkNodeEvaluator.getBlockPathType` |
| **Colisão e empurrão** | `LivingEntity.pushEntities` consulta entidades no hitbox a cada tick, e hitbox grande abrange muitas seções. O Lithium ajuda (`mixin.entity.collisions.*`), mas seu `fast_retrieval` só acelera consultas "de um número relativamente pequeno de seções" ([config do Lithium](https://raw.githubusercontent.com/CaffeineMC/lithium/develop/lithium-fabric-mixin-config.md)). | `Entity.move`, `pushEntities` |
| **Varreduras `getEntitiesOfClass` grandes** | O custo é proporcional ao volume da caixa, em seções de 16³. Uma caixa de 160×384×160 (a do EcoSpawner) cobre ~100 colunas × 24 seções. | `ClassInstanceMultiMap` |
| **Laços por jogador** | O(jogadores) por tick, ou O(entidades × jogadores) no rastreador de entidades do vanilla (`ChunkMap.TrackedEntity.updatePlayers`). O mod VMP existe justamente para isso: "Optimizes entity tracking with area maps" ([VMP](https://raw.githubusercontent.com/RelativityMC/VMP-fabric/ver/1.20.1/README.md)). | `ChunkMap.tick`, `TrackedEntity` |
| **Carregamento de chunk por entidades** | `level.getHeight()`, `getBlockState()` ou `getChunk()` fora da área carregada gera ou carrega o chunk **de forma síncrona**. | picos em `ServerChunkCache.getChunk` |
| **Saves grandes** | `SavedData` gigante gravado com gzip no thread principal a cada autosave, e NBT de entidade com inventário. | picos a cada 5 min em `DimensionDataStorage.save` |
| **Pacotes** | Atualizações de `SynchedEntityData`, movimento (`updateInterval` 3 ticks por padrão), gatilhos de animação e partículas. Tudo multiplicado pelo número de jogadores rastreando cada entidade. | uso de rede e `ServerEntity.sendChanges` |

**Ferramenta obrigatória:** o spark ([README](https://raw.githubusercontent.com/lucko/spark/master/README.md)) é um "lightweight" profiler que roda em produção. Bastam ~30 s de perfil para ver os pontos quentes. O fluxo recomendado é `/spark profiler start --timeout 120`, depois `/spark tickmonitor` e `/spark health`. Recomendação para a equipe: manter um mundo de teste com 50-100 bots (ex.: clientes headless) e anexar o perfil do spark a cada release.

**O que se aprende com outros mods (com o grau de certeza indicado):**

- **Ice and Fire:** os dragões usam pathfinding **assíncrono** portado do MineColonies (Raycoms), com um `ThreadPoolExecutor` cujo tamanho vem do config `dragonPathfindingThreads`. Verificado no código: [Pathfinding.java](https://raw.githubusercontent.com/AlexModGuy/Ice_and_Fire/1.20/src/main/java/com/github/alexthe666/iceandfire/pathfinding/raycoms/Pathfinding.java). Lição: mobs gigantes precisam de caminho próprio, e caminho calculado fora do thread principal exige uma cópia segura do mundo (o MineColonies usa um cache de chunks), porque ler blocos de outro thread corrompe estado.
- **Cobblemon** (GitLab, não acessado): o spawner é **por jogador**, com uma "fatia do mundo" ao redor de cada um, e tem um despawner próprio com distâncias e idades mínimas e máximas. O config tem uma opção para **não salvar** os pokémon selvagens no mundo. De memória, as chaves são `maxPokemonPerChunk`, `ticksBetweenSpawnAttempts`, `despawnerNearDistance`, `despawnerFarDistance`, `despawnerMinAgeTicks`, `despawnerMaxAgeTicks` e `savePokemonToWorld`; confira em https://gitlab.com/cable-mc/cobblemon **(não acessado)**. É o modelo mais parecido com o EcoSpawner, e a lição é: selvagem gerado pelo spawner é efêmero e não vai para o disco.
- **Pixelmon** (código fechado): redes grandes costumam limitar cada instância a algo como 100-150 jogadores e escalar horizontalmente atrás de um proxy (estimativa, conhecimento geral da cena). Não há documentação pública confiável dos números.
- **Alex's Mobs**: os packmakers elogiam porque cada mob tem peso de spawn no TOML e biomas num JSON próprio em `config/alexsmobs/` (de memória). O padrão serve para o Terrassic.

**Orçamento de entidades** (estimativa): o vanilla dá a cada jogador isolado ~70 monstros, 10 animais "persistentes" e ~45 ambientes/aquáticos. Servidores modded saudáveis com 100+ jogadores costumam ficar entre 5 e 15 mil entidades carregadas no total. Para mobs com IA rica, uma meta segura é **10-20 criaturas com IA completa por jogador isolado**, com o resto em LOD. Jogadores próximos uns dos outros **compartilham** a mesma população.

---

## 3. Padrões concretos para criaturas em servidor grande

### 3.1 Teto por jogador vs teto global
- **Por jogador** (como o EcoSpawner e o vanilla, que divide o mobcap pelo número de chunks elegíveis): a população escala com a área ocupada. Jogadores próximos não somam metas, porque contam a mesma área. É o certo.
- **Teto global**: só serve como disjuntor. Ele precisa ser **proporcional** (ex.: `max_creatures_per_player × jogadores`, com um teto absoluto) e **justo**: distribua as cotas por rodízio ou dê prioridade a quem está mais abaixo da meta. Nunca percorra sempre a lista na mesma ordem.
- **Teto por região**: some as entidades por "célula" de 4×4 chunks e recuse spawn em célula cheia. Isso protege contra 30 jogadores numa vila.
- **Disjuntor por MSPT**: se o MSPT médio de 5 s passar de, por exemplo, 40 ms, reduza a densidade automaticamente (é o que faz o "Dynamic performance checks" do [ServerCore](https://raw.githubusercontent.com/Wesley1808/ServerCore/main/README.md), que ajusta mobcaps e distâncias conforme o tick time).

### 3.2 Despawn e persistência
- **Selvagem gerado pelo spawner = efêmero.** Sobrescreva `shouldBeSaved()` para devolver `false` quando `roamer && !isTame() && !hasCustomName() && !isLeashed()`. A criatura some quando o chunk descarrega, não acumula e não engorda o NBT. É o equivalente ao `savePokemonToWorld=false`.
- **Distância de despawn ligada à simulation distance.** Use `min(96, simDistance*16 - 16)`. Se o despawn for a 96 blocos e o servidor simular só 80, o mob congela e nunca some.
- **Persistentes** (domados, com nome, presos por guia, chefes) ficam como estão.
- **Ovos selvagens** de errantes: ou não colocar, ou o filhote nascer `roamer`.

### 3.3 LOD de IA (tickar menos quem está longe)
- Divida em faixas por distância ao jogador mais próximo (calculada a cada 20 ticks e guardada em cache na entidade):
  - **≤ 32 blocos:** IA completa.
  - **32-64:** metas reavaliadas a cada 4-8 ticks, sem `LookAtPlayer`/`RandomLookAround` e repath mais lento.
  - **> 64:** só movimento e física. Fome, sono e reprodução passam a ser calculados por **tempo decorrido** (delta do `gameTime`) quando a entidade volta à faixa próxima.
- Implementação: um `int aiLod` na `DinosaurEntity`; no `serverAiStep()`, pule `goalSelector.tick()` conforme a faixa e chame `goalSelector.tickRunningGoals(false)` para manter a navegação. Isso imita a Entity Activation Range do Spigot/Paper, que o ServerCore porta para Fabric ([README](https://raw.githubusercontent.com/Wesley1808/ServerCore/main/README.md)), e o "DAB" do Pufferfish, um fork do Paper que promete "Better Entity Performance … skipping useless work" ([README](https://raw.githubusercontent.com/pufferfish-gg/Pufferfish/ver/1.20/README.md)).
- Projete as mecânicas para **tolerar congelamento**: se um servidor usar a activation range do ServerCore ou de um híbrido, os dinos longe não tickam. Contadores baseados em `tickCount` param; contadores baseados em `gameTime` continuam corretos.

### 3.4 Escalonar trabalho entre ticks
- Use `(tickCount + id) % N` em vez de `tickCount % N`. O `tickCount` volta a 0 quando o chunk carrega, então todos os dinos carregados juntos ficam na mesma fase e criam picos (`DinosaurEntity.java:1063-1080`).
- No EcoSpawner, atenda o jogador *i* só quando `(gameTime + hash(uuid)) % 40 == 0`, em vez de todos no mesmo tick.
- Varreduras globais (`getAllEntities`) devem virar contadores incrementais, incrementados em `ENTITY_ADD` e decrementados no `remove`.

### 3.5 Pathfinding
- **Curto prazo:** limite o `maxVisitedNodes` dos gigantes (o vanilla usa `FOLLOW_RANGE × 16`), use `Navigation` com `setCanFloat` e malus ajustado, faça repath a cada 20-40 ticks e não a cada 10, e use alvos de "waypoint" de 12-16 blocos (o `MigrateGoal` já faz isso).
- **Médio prazo:** navegação própria para largura ≥ 3 que testa o terreno numa **grade mais grossa** (ex.: amostrar só a borda e o centro do hitbox).
- **Assíncrono** só com um snapshot imutável dos chunks, como o Ice and Fire/MineColonies, e com um pool limitado (1-2 threads), resultado entregue no tick seguinte e cancelamento se o alvo mudar. É complexo; deixe para depois de medir.

### 3.6 Tracking range e volume de pacotes
- `clientTrackingRange` em chunks: hoje vai de 8 a 18 (128-288 blocos). Cada jogador nesse raio recebe movimento e metadata. Recomendação: **8 para pequenos e médios, 10-12 para gigantes**, configurável (lido antes do registro) para que o operador possa reduzir.
- `SynchedEntityData`: só mande o que o cliente desenha. Hoje `DATA_HUNGER` (INT) é sincronizado; se a fome muda de 1 em 1, cada mudança vira um pacote para todos que rastreiam. Arredonde para faixas de 10 ou mande só para o dono.
- **Gatilhos de animação:** no GeckoLib, `triggerAnim` chamado no servidor envia um pacote aos jogadores que rastreiam a entidade (documentação do GeckoLib, https://github.com/bernie-g/geckolib/wiki **(não acessado)**). Disparos frequentes (`graze`, `beg`, `eat`) devem ter cooldown. Animações puramente visuais (idle, olhar) devem ser decididas no cliente.
- **Partículas** com `sendParticles` de 50-200 unidades (`RiftStorm.java:178`, `Leap.java`): limite a contagem e o alcance.

### 3.7 Cliente com muitas entidades GeckoLib
- Faça culling por distância no renderer: acima de ~64 blocos, pare de avançar os controllers e congele a pose. Acima de ~128, renderize só a silhueta, ou nada, se não for gigante.
- Mantenha a sombra e o `getBoundingBoxForCulling` justos (hoje há um `cullingInflate` por espécie; bom).
- Varreduras por frame no cliente (`TerrassicHud.java:90-92`, uma caixa de 96 blocos a cada frame) devem ir para cache a cada 10 ticks.
- Teste com Sodium/Embeddium + Iris/Oculus e com o "Entity Culling" (tr7zw). As GeckoLib costumam funcionar, mas camadas emissivas (`RiftLayer`) com shaders são a fonte clássica de bug.

---

## 4. Compatibilidade com mods de performance e software de servidor

| Projeto | Lado | O que significa para o Terrassic |
|---|---|---|
| **Lithium** (Fabric; NeoForge em versões novas) | ambos, sem exigir os dois lados ([README](https://raw.githubusercontent.com/CaffeineMC/lithium/develop/README.md)) | Acelera colisão, pathing (`mixin.ai.pathing`) e consultas por tipo (`replace_entitytype_predicates`: "accesses entities of the correct type directly"). Consultar `PredatorDinosaur.class` em vez de `DinosaurEntity.class` + predicado **aproveita** isso. Não mexa em `EntitySectionStorage` por mixin. |
| **Canary / Radium** | Forge (ports/forks do Lithium) | Os mesmos cuidados. Teste no Forge 1.20.1 com Canary. |
| **ModernFix** | ambos | Melhora "launch times, world load times, memory usage" ([README](https://raw.githubusercontent.com/embeddedt/ModernFix/1.20/README.md)). Tem carregamento dinâmico de recursos: não guarde referência a `BakedModel` em estático, e registre tudo nos eventos certos. |
| **FerriteCore** | ambos | Deduplica blockstates e propriedades. Com 336 blocos, ajuda o Terrassic. Não compare `Property` por identidade em código próprio. |
| **C2ME** | Fabric | Geração de chunk paralela ("taking advantage of multiple CPU cores"), ainda "alpha" ([README](https://raw.githubusercontent.com/RelativityMC/C2ME-fabric/ver/1.20.1/README.md)). Código do Terrassic chamado na worldgen (`finalizeSpawn` com `WorldGenRegion`, `CretaceousSurface.rules()` em lazy init, `Rules.of` `synchronized`) **roda em threads de worker**. Mantenha isso sem estado mutável compartilhado; `Rules.of` sincronizado vira contenção. |
| **VMP** | Fabric, servidor | Otimizado para muitos jogadores: rastreador de entidades, consultas de jogadores próximos e spawn natural ([README](https://raw.githubusercontent.com/RelativityMC/VMP-fabric/ver/1.20.1/README.md)). Recomende para servidores Fabric grandes. |
| **ServerCore** | Fabric | Activation range, mobcaps dinâmicos, "breeding caps" ([README](https://raw.githubusercontent.com/Wesley1808/ServerCore/main/README.md)). Garanta que os dinos tolerem ficar sem tickar (3.3) e que a reprodução selvagem respeite caps externos. |
| **Sodium / Embeddium** (+ Iris / Oculus) | cliente | Os mixins de cliente do Terrassic usam `require = 0` (bom). Os `@Redirect` em `TitleScreenMixin.java:51,61` conflitam com mods de menu (FancyMenu, Drippy Loading Screen). Prefira `@Inject` ou `@WrapOperation` (MixinExtras). |

**Servidores híbridos (Mohist, Arclight, Magma).** Eles aplicam os patches do CraftBukkit/Spigot/Paper sobre o Forge. O README do Mohist lista Bukkit, CraftBukkit, Spigot, Paper, Purpur e Pufferfish como upstream ([README](https://raw.githubusercontent.com/MohistMC/Mohist/1.20.1/README.md)). Por que quebram mods:
1. Os patches reescrevem os mesmos métodos que os mods alvejam por mixin ou coremod (tick de entidade, spawn, chunk), então injeções falham ou duplicam efeito.
2. O remapeamento de nomes para plugins quebra reflexão.
3. Eventos do Bukkit cancelam ações sem que o mod saiba.
4. A activation range e o `entity-broadcast-range` do Spigot também valem para entidades modded.

Postura recomendada: **não dar suporte oficial**, mas não quebrar à toa. Use injeções tolerantes (`require = 0` onde for cosmético), nada de `@Overwrite`, e faça um teste de fumaça no Arclight a cada versão maior.

**Folia.** É um fork do Paper com "regionised multithreading": cada região tem seu próprio loop de tick em paralelo, "there is no main thread anymore". O teste deles teve "~330 players peak", e a recomendação é ter ≥16 núcleos ([README](https://raw.githubusercontent.com/PaperMC/Folia/ver/1.21.4/README.md)). **O Folia não carrega mods Forge/Fabric**, então não é alvo direto. Para Forge/Fabric 1.20.1 não há equivalente maduro; mods como MCMT ou "Async", que paralelizam entidades, quebram com estáticos mutáveis (estimativa). Mesmo assim, o Folia ensina como projetar:
- Nada de estado global mutável lido no tick de entidade (`EcoSpawner.WILD`, `RiftStorm.leaks`, `Leap.PENDING` são estáticos).
- Eventos "globais" devem ser **regionais**.
- Dados devem ser chaveados por jogador ou região.
Se um dia surgir um loader regionalizado, isso já estará pronto.

**Proxy (Velocity).**
- **Fabric:** use FabricProxy-Lite no backend (modern forwarding). O PCF reconhece o FabricProxy-Lite como pioneiro ([PCF](https://raw.githubusercontent.com/adde0109/Proxy-Compatible-Forge/main/README.md)).
- **Forge 1.20.1:** Ambassador no Velocity ("host a modern Forge server behind a Velocity proxy") + PCF para forwarding ([Ambassador](https://raw.githubusercontent.com/adde0109/Ambassador/master/README.md)). Trocar de servidor exige o **mesmo conjunto de mods** nos backends ("Mods must match").
- **Para o Terrassic:** o progresso (`ResearchData`, `LeapProgress`) mora no `SavedData` do mundo, então **não segue o jogador** entre backends (survival → recursos → eventos). Guarde os dados por jogador em arquivo próprio por UUID, com um ponto de extensão para armazenamento compartilhado (seção 8).

---

## 5. Design para muitos jogadores

### 5.1 Progresso pessoal vs eventos compartilhados
- **Pessoal** (já é assim e está certo): Guia de Campo, objetivos, páginas da Katarina, capítulo/salto. Isso respeita a Regra 0. Para equipes, adicione um modo **"conhecimento de equipe"** opcional: o grupo do FTB Teams ou a party do OPAC compartilha os níveis do Guia (`max` dos membros), enquanto as conquistas continuam individuais.
- **Compartilhados:**
  - **Tempestade da Fenda.** Hoje é global: rola uma vez por dia e afeta todos os jogadores do Overworld ao mesmo tempo (`RiftStorm.java:104-128`). Com 300 jogadores, ela cria um pico de spawns e tira a escolha de quem está construindo. Proposta: **tempestades regionais**, com centro e raio (ex.: 256 blocos), várias por dia em pontos diferentes, perto de grupos de jogadores e com teto de leaks por tempestade, não por jogador.
  - **Tirano da Fenda.** É instanciado por altar e escala até 8 jogadores (`LeapAltarBlockEntity.java:325-331`). Bom modelo: chefe local, por grupo. Adicione um cooldown por altar e um limite de altares ativos por região.
  - **Pouso do Salto.** Todos os jogadores pousam no mesmo ponto (`Leap.java:129,189`). Em servidor grande, isso empilha centenas de pessoas e criaturas no mesmo chunk. Espalhe os pousos num anel ou por equipe e proteja o spawn da era contra grief.

### 5.2 Posse e permissões das criaturas
- O dono já é checado para montar, abrir carga e alimentar; a sela de plataforma deixa qualquer um ir de passageiro (ok).
- Faltam:
  - **Confiança/equipe:** permitir que membros da equipe montem, alimentem e mandem sentar (APIs do FTB Teams e do OPAC).
  - **PvP de pets:** respeitar PvP desligado em claims, ou seja, um pet não ataca um jogador protegido nem é atacado por ele.
  - **Limite de domados por jogador**, configurável (servidores de ARK e de Pixelmon fazem isso para evitar "fazendas" de centenas de gigantes). Contar por UUID do dono num índice persistente.
  - **Comandos administrativos:** `/terrassic pets list <jogador>`, `transfer <entidade> <jogador>`, `release`, `tp`, para suporte e para jogadores que saíram.

### 5.3 Anti-grief e claims
- Os gigantes quebram folhas e plantas quando estão em carga, **inclusive quando montados por um jogador** (`Argentinosaurus.java:147-163`; `Styracosaurus.java:107-120`; `Pachyrhinosaurus.java:152-165`). Hoje só respeitam a gamerule global `mobGriefing`. Um jogador montado entra no claim do vizinho e destrói o jardim.
- Correção:
  1. **Montado** → atribua a quebra ao **jogador** e passe pelo evento de quebra do Architectury (`BlockEvent.BREAK`). O FTB Chunks é construído sobre o Architectury ([README](https://raw.githubusercontent.com/FTBTeam/FTB-Chunks/main/README.md)), e o OPAC protege contra quebra por jogador.
  2. **Selvagem** → no Forge, use `ForgeEventFactory.getMobGriefingEvent(level, entity)`, que é o que claims e outros mods escutam. No Fabric, use a gamerule + uma API opcional de claims (OPAC/FTB Chunks via soft-dependency).
- Ovos selvagens, carcaças e cesto (`BasketBlock`) devem respeitar a interação protegida (os eventos de interação do Architectury cobrem isso).

### 5.4 APIs de permissão
- Hoje há `hasPermission(2)` fixo em todos os comandos e na tela de regras (`RulesNetwork.java:61-63`, `LeapCommands.java:40-52`, `RiftStorm.java:280`).
- Troque por nós de permissão com fallback para nível de op:
  - `terrassic.command.storm`
  - `terrassic.command.chapter`
  - `terrassic.rules.edit`
  - `terrassic.pets.admin`
  - `terrassic.pets.limit.<n>` (como "option/meta")
- No Fabric, use a [fabric-permissions-api](https://raw.githubusercontent.com/lucko/fabric-permissions-api/master/README.md) (`Permissions.check(source, "node", 2)`), que precisa de um provedor como o LuckPerms. No Forge, use `PermissionAPI` com `PermissionNode` registrados no `PermissionGatherEvent.Nodes`; o LuckPerms Forge é o provedor.
- Faça isso em uma interface `TerrassicPermissions` no common, com implementação por plataforma.

### 5.5 Config do servidor sincronizado
- As regras (`Rules`) já são do servidor e sincronizam para o cliente só para exibição. Ótimo.
- Separe claramente três camadas:
  1. **Servidor/mundo**: regras, spawn, limites.
  2. **Comum de inicialização**: tracking range, que precisa existir antes do registro.
  3. **Cliente**: HUD, LOD visual.
- Nunca deixe o cliente decidir números de jogo.
- Valide sempre no servidor (o `Rule.clamp` já faz isso).

---

## 6. Padrões de integração com modpacks

**O que os packmakers mais reclamam** (estimativa, conhecimento geral da comunidade):
1. Conteúdo que não dá para ajustar sem código: spawns, dietas, drops.
2. Spawn agressivo demais, sem teto ou configurável só globalmente.
3. Itens duplicados sem tags comuns (carne, couro, ossos).
4. Mixins conflitantes em tela de título e renderização.
5. Configs que resetam ou que não podem ser distribuídas.
6. Falta de JEI/EMI e Jade.
7. Licença que não autoriza modpacks.
8. Crash em servidor dedicado por classe de cliente carregada no common.

**Recomendações concretas:**

- **Datapack primeiro.**
  - `data/<ns>/terrassic_species/<especie>.json` com tamanho, atributos base, grupo, habitat, `tame_method`, dieta (tag), carne e loot. As classes Java continuam definindo comportamento; o JSON define números.
  - O gerador Python que já existe (`gen_species.py`) pode passar a emitir esses JSON.
  - O recarregamento seguro com `/reload` vale para números que não exigem registro.
- **Dietas por tag de item.** Crie `terrassic:diet/<especie>` e use `Ingredient.of(TagKey)`. Os JSON padrão incluem os itens vanilla + `{"id": "#c:foods/raw_meat", "required": false}`, que é a tag comum do Fabric v2/NeoForge 1.21 ([ConventionalItemTags v2](https://raw.githubusercontent.com/FabricMC/fabric/1.21.1/fabric-convention-tags-v2/src/main/java/net/fabricmc/fabric/api/tag/convention/v2/ConventionalItemTags.java): `foods/raw_meat`, `foods/cooked_meat`, `foods/raw_fish`). No 1.20.1 há também `c:foods` no v1 ([v1](https://raw.githubusercontent.com/FabricMC/fabric/1.20.1/fabric-convention-tags-v1/src/main/java/net/fabricmc/fabric/api/tag/convention/v1/ConventionalItemTags.java)). Coloque as carnes do Terrassic nessas tags, e as lanças em `c:spears` / `c:tools/spear`.
- **Spawns.** Já usam tags de bioma `terrassic:habitat/<palavra>` (ótimo). Mantenha os pesos num JSON de datapack, e não no `config/terrassic.json` lido uma vez. No Forge, use biome modifiers JSON; no Fabric, leia o JSON e aplique pela `BiomeModifications`.
- **Tags de entidade** para outros mods: `terrassic:giants`, `terrassic:predators`, `terrassic:rideable`, e entrar em `c:bosses` só com o Tirano.
- **Recipe viewers.** Mostre a Mesa de Pesquisa, a escavação, os ovos (chocar) e as dietas no EMI (que lê JEI), no JEI e no REI. Pelo menos uma "info page" por espécie mostrando dieta e método de domesticação.
- **Jade / WTHIT.** Tooltip de entidade com sexo, fome (faixa), dono, crescimento e "dormindo". Tooltip de ovo com estágio e espécie. É barato e muito pedido.
- **KubeJS / CraftTweaker.** Exponha eventos (`terrassic.tamed`, `terrassic.research_level`, `terrassic.leap`, `terrassic.storm_start`) e um registro de espécies consultável. O KubeJS ([README](https://raw.githubusercontent.com/KubeJS-Mods/KubeJS/main/README.md)) tem plugins por mod. Comece com eventos via Architectury e um plugin KubeJS opcional.
- **FTB Quests.** Os objetivos do Caderno já viram advancements: o FTB Quests usa tarefa de "advancement", então já funciona. Documente os IDs. Adicione **critérios customizados** (trigger de advancement `terrassic:research_level` com espécie/nível) para os quest makers não dependerem da árvore pronta.
- **Curios / Accessories.** A Lente de Âmbar e itens de "roupinhas" futuras podem ir num slot (soft-dependency).
- **Create.** Receitas de moagem e lavagem para fósseis e rochas via datapack condicional (`forge:mod_loaded` / `fabric:load_conditions`).
- **Formato de config.** No Forge, use `ForgeConfigSpec` (TOML, com comentários, sincronizado se `SERVER`). No Fabric, JSON5/TOML. Mantenha **o mesmo arquivo nos dois loaders**: o Architectury não unifica configs, mas o Forge Config API Port permite usar `ForgeConfigSpec` no Fabric. Deixe os configs distribuíveis (sem caminho absoluto) e com defaults em `defaultconfigs/` para que o modpack possa definir os valores de mundo novo.
- **Licença.** Hoje é "All-Rights-Reserved" (`fabric.mod.json`). O CurseForge e o Modrinth distribuem por referência ao arquivo hospedado neles, mas launchers e plataformas que empacotam o jar precisam de permissão. Adicione no README uma frase explícita: **"Pode ser incluído em modpacks públicos"** (ou mude para uma licença como ARR + exceção de modpack).
- **Escopo.** O `docs/ESCOPO.md` diz que o Terrassic "não é modpack e não depende de mods de conteúdo de outras pessoas". Integrações **opcionais** (soft-dependencies) mantêm isso: nada vira dependência obrigatória.

---

## 7. Auditoria do repositório (riscos de escala, por prioridade)

Severidade: **A** = impede 100+ jogadores; **B** = custo alto ou bug multiplayer; **C** = melhoria.

| # | Sev | Onde | Risco | Correção sugerida |
|---|---|---|---|---|
| 1 | A | `world/EcoSpawner.java:112-114` + `config/Rule.java:28` | O teto global de 400 (máx. 2000) é consumido pelos primeiros jogadores de `level.players()`, sempre na mesma ordem; os demais ficam sem fauna. Sem o teto, 300×38 dinos é inviável. | Cota por jogador (`max_per_player`) + teto absoluto proporcional; rodízio de quem é atendido; disjuntor por MSPT. |
| 2 | A | `entity/DinosaurEntity.java:759-761`, `:162` | Errantes só somem tickando e a >96 blocos. Com simulation-distance 6-8, congelam na borda e são **salvos** no chunk, acumulando no save. | `shouldBeSaved()` = false para errante selvagem sem nome; despawn ligado à simulation distance. |
| 3 | A | `DinosaurEntity.java:657-665` + `block/DinoEggBlock.java:114-136` | Errantes nascem com ninho (5% × regra); os ovos persistem no mundo e chocam filhotes **não errantes** (permanentes). A reprodução selvagem (`:1366-1392`) idem. A população cresce com a exploração. | Errante não põe ninho (ou o ovo é marcado "efêmero"); filhote de ovo selvagem nasce `roamer`; teto de ovos por chunk. |
| 4 | A | `entity/HerbivoreDinosaur.java:87-90` | Dois `AvoidEntityGoal` em todo herbívoro varrem jogadores (raio 10) e **todas as `DinosaurEntity`** (raio 14) a cada 2 ticks, mesmo nos que lutam (o `!fightsBack()` está no predicado, depois da varredura). Fica O(n²) por manada. | Subclasse com `canUse()` que sai cedo se `fightsBack()`/domado, intervalo aleatório (`reducedTickDelay(10)`), classe `PredatorDinosaur.class` (o Lithium filtra por tipo). |
| 5 | A | `world/EcoSpawner.java:85-139` | Todos os jogadores são processados no mesmo tick a cada 40, cada um com caixa 160×(altura inteira)×160; `getAllEntities()` a cada 200 ticks. Pico periódico O(jogadores). | Escalonar por hash do UUID; caixa limitada em Y (±64 do jogador); contador incremental de selvagens. |
| 6 | A | `research/ResearchData.java:14-32` | Um `SavedData` com **todos** os jogadores que já entraram, em memória para sempre e regravado inteiro (gzip, thread principal) a cada autosave sujo. Não segue o jogador entre servidores. | Arquivo por UUID (`<world>/terrassic/players/<uuid>.dat`), carregado no login, salvo no logout/autosave, com cache LRU; interface de storage plugável. |
| 7 | B | `entity/PredatorDinosaur.java:90-93` | `NearestAttackableTargetGoal<Player>`/`<Animal>`: a condição `canHunt()` (do próprio mob) é testada **por candidato**, depois de percorrer jogadores/animais. Um predador saciado ou dormindo continua varrendo. | Gate em `canUse()` com `canHunt()` antes da busca; intervalo maior quando saciado. |
| 8 | B | `Argentinosaurus.java:147-163`, `Styracosaurus.java:107-120`, `Pachyrhinosaurus.java:152-165` | Varredura de ~400-500 blocos **por tick** enquanto em carga (estimativa pelo hitbox) e quebra de blocos sem checar claim, inclusive montado. | A cada 2-4 ticks, só a faixa frontal do hitbox; montado → evento de quebra do jogador; selvagem → `getMobGriefingEvent` no Forge. |
| 9 | B | `registry/ModEntities.java:210-215` | `clientTrackingRange` 8-18 chunks (até 288 blocos): cada gigante vai para todos os jogadores nesse raio. Custo O(entidades × jogadores) no rastreador. | 8 (pequenos) / 10-12 (gigantes), configurável na inicialização; recomendar VMP no Fabric. |
| 10 | B | `world/RiftStorm.java:98-100, 118-124, 163-169` | Evento global: leaks para **todos** os jogadores no mesmo tick a cada 200; `getAllEntities()` a cada 100 ticks fora da tempestade. | Tempestades regionais; leaks escalonados; limpeza por evento de carregamento de entidade (tag) em vez de varrer tudo. |
| 11 | B | `DinosaurEntity.java:1053-1083` (e `tickCount % N` em todo lugar) | Fases sincronizadas após carregar o chunk → picos; fome, maturação e cria baseadas em ticks param sob activation range. | `(tickCount + getId()) % N`; temporizadores por `gameTime`. |
| 12 | B | `config/Rules.java:177-192` | `Rules.of` é `static synchronized` e chamado em caminhos quentes (dano, fome, spawn em worldgen paralela com C2ME). | Campo `volatile` com leitura sem lock; atualizar só em `apply`/load. |
| 13 | B | `leap/Leap.java:129,189` | Pouso num ponto fixo por era: empilha jogadores e pets. | Anel de pouso por grupo/equipe, aleatório num raio. |
| 14 | B | `research/Research.java:113-118` + `network/ModNetwork.java:25-29` | Cada mudança reenvia o `Knowledge` inteiro em NBT; com 152 espécies, alguns KB por evento (estimativa). | Pacote delta (espécie, nível, pontos); sincronização completa só no login. |
| 15 | B | Entidades `Velociraptor.java:32` etc. | Dietas fixas em `Ingredient.of(Items…)`: packmakers não ajustam; carnes de outros mods não servem. | Tags `terrassic:diet/<especie>` (seção 6). |
| 16 | C | `entity/ai/SoarGoal.java:100,145-156` | Os seguidores reconsultam o bando a cada 10 ticks para achar o líder. | Guardar o UUID do líder e revalidar a cada 100 ticks. |
| 17 | C | `entity/CarcassEntity.java:183-200` | `move()` a cada tick mesmo parada no chão. | Pular `move` quando `onGround` e velocidade ~0. |
| 18 | C | `client/TerrassicHud.java:90-92` | Varredura de 96 blocos **por frame** no cliente. | Cache a cada 10 ticks. |
| 19 | C | `mixin/client/TitleScreenMixin.java:51,61` | `@Redirect` conflita com mods de menu. | `@WrapOperation` (MixinExtras) ou `@Inject`. |
| 20 | C | `network/RulesNetwork.java:61-63` e comandos | Permissão fixa em op 2. | Nós de permissão (5.4). |
| 21 | C | `DinosaurEntity.java:139-151` (`DATA_HUNGER`, `DATA_GROWTH`) | Metadata sincronizada que muda com frequência gera pacotes a todos os que rastreiam. | Faixas (fome em passos de 10), crescimento já em passos de 1% (ok). |

Pontos que já estão bons: `isPositionEntityTicking` antes de spawnar (`EcoSpawner.java:153`) e `hasChunkAt` antes de ler altura (`MigrateGoal.java:128`, `SoarGoal`, `RiftStorm.leakNear`) evitam carregar chunks; as metas de manada e de carcaça usam intervalos aleatórios; o chefe escala por jogadores; as regras são validadas no servidor com `clamp`; os mixins de cliente usam `require = 0`.

---

## 8. Plano de arquitetura recomendado

**Meta de capacidade** (estimativa): um servidor de 100-300 jogadores em 1.20.1 com Terrassic + outros mods, MSPT médio < 35 ms num CPU moderno de alto clock. Acima de ~150 jogadores, o normal na cena modded é **dividir em vários backends** atrás do Velocity, e não esperar um único processo aguentar 300. Projete para os dois casos.

### Fase 1: agora (antes da v1.0, 1-2 semanas de trabalho estimado)
1. **Errantes efêmeros:** `shouldBeSaved()` false; despawn ligado à simulation distance; errante sem ninho; filhote de ovo selvagem nasce errante (riscos 2-3).
2. **EcoSpawner orçado:**
   - novas regras `max_per_player` (padrão ~24 no total; terrestre 12 / voador 5 / marinho 7) e `max_total` proporcional, com rodízio justo;
   - escalonar jogadores por hash;
   - caixa limitada em Y;
   - contador incremental;
   - disjuntor por MSPT, reduzindo a densidade quando o MSPT médio > 40 ms (riscos 1, 5).
3. **Metas baratas:** `AvoidEntityGoal` e `NearestAttackableTargetGoal` com gate próprio e classe específica; `(tickCount + id) % N` (riscos 4, 7, 11).
4. **Tracking range** 8/10-12, configurável (risco 9).
5. **`Rules.of` sem lock** (risco 12).
6. **Banco de testes:** mundo com 50-100 bots + perfil de spark anexado a cada release; registrar o MSPT por número de jogadores num doc do projeto.

### Fase 2: até a v1.0 "Ecos do Fim"
1. **LOD de IA** em três faixas + simulação por tempo decorrido (3.3).
2. **Dados por jogador** em arquivo por UUID com interface `PlayerDataStore`, implementação em arquivo local e ponto de extensão para armazenamento compartilhado em rede (risco 6). Mesmo tratamento para `LeapProgress`.
3. **Sincronização delta** do Conhecimento (risco 14).
4. **Claims e permissões:**
   - quebra de blocos montada via evento de jogador;
   - `getMobGriefingEvent` no Forge;
   - nós de permissão (fabric-permissions-api / PermissionAPI);
   - confiança de equipe para pets;
   - limite de domados por jogador;
   - comandos `/terrassic pets` (5.2-5.4).
5. **Tempestades regionais** e pouso espalhado (5.1).
6. **Integrações leves (soft-deps):** Jade/WTHIT, EMI (+ JEI/REI), tags `c:`, dietas por tag, documentação dos advancements para o FTB Quests e frase de licença para modpacks.

### Fase 3: depois da v1.0
1. **Espécies por datapack** (números, dieta, habitat, loot) com recarga; o gerador Python emite os JSON.
2. **API pública** (`com.terrassic.api`): eventos (domado, nível de pesquisa, salto, tempestade), registro de espécies e consulta de conhecimento. Plugin KubeJS e critérios de advancement customizados.
3. **Navegação de gigantes** (grade grossa, depois assíncrona com snapshot e pool pequeno, no estilo Ice and Fire/MineColonies), só se o spark mostrar `PathFinder` no topo.
4. **LOD visual no cliente** para GeckoLib (congelar a animação longe, silhueta) e testes contínuos com Sodium/Embeddium/Iris/Oculus.
5. **Guia para donos de servidor** (página no repositório):
   - Fabric: Lithium + VMP + C2ME (com backup) + ServerCore, ou Forge: Canary + ModernFix + FerriteCore;
   - simulation-distance 6-8;
   - mundo pré-gerado (Chunky);
   - valores recomendados das regras por faixa de jogadores;
   - Velocity com FabricProxy-Lite / Ambassador + PCF;
   - aviso de que híbridos não têm suporte.

### Tabela de prioridades

| Prioridade | Item | Impacto | Esforço (estimativa) |
|---|---|---|---|
| 1 | Errantes efêmeros + ovos | evita save inchado e crescimento sem limite | baixo |
| 2 | EcoSpawner orçado e justo | viabiliza 100+ jogadores | médio |
| 3 | Gates nas metas de varredura | −30-50% do custo de IA de manada (estimativa) | baixo |
| 4 | Tracking range | rede e rastreador | baixo |
| 5 | LOD de IA | maior ganho estrutural | médio |
| 6 | Dados por jogador em arquivos | saves e rede Velocity | médio |
| 7 | Claims/permissões/pets | servidores públicos | médio |
| 8 | Dietas/tags/Jade/EMI | aceitação em modpacks | baixo-médio |
| 9 | Datapack de espécies + API | modpacks grandes | alto |
| 10 | Pathfinding de gigantes | só se medido | alto |

---

## 9. Fontes consultadas nesta sessão
- Lithium: https://raw.githubusercontent.com/CaffeineMC/lithium/develop/README.md e https://raw.githubusercontent.com/CaffeineMC/lithium/develop/lithium-fabric-mixin-config.md
- ServerCore: https://raw.githubusercontent.com/Wesley1808/ServerCore/main/README.md
- VMP: https://raw.githubusercontent.com/RelativityMC/VMP-fabric/ver/1.20.1/README.md
- C2ME: https://raw.githubusercontent.com/RelativityMC/C2ME-fabric/ver/1.20.1/README.md
- ModernFix: https://raw.githubusercontent.com/embeddedt/ModernFix/1.20/README.md
- Folia: https://raw.githubusercontent.com/PaperMC/Folia/ver/1.21.4/README.md
- Pufferfish: https://raw.githubusercontent.com/pufferfish-gg/Pufferfish/ver/1.20/README.md
- Mohist: https://raw.githubusercontent.com/MohistMC/Mohist/1.20.1/README.md · Arclight: https://raw.githubusercontent.com/IzzelAliz/Arclight/Trials/README.md
- Ambassador: https://raw.githubusercontent.com/adde0109/Ambassador/master/README.md · PCF: https://raw.githubusercontent.com/adde0109/Proxy-Compatible-Forge/main/README.md
- fabric-permissions-api: https://raw.githubusercontent.com/lucko/fabric-permissions-api/master/README.md
- spark: https://raw.githubusercontent.com/lucko/spark/master/README.md
- Ice and Fire (pathfinding assíncrono): https://raw.githubusercontent.com/AlexModGuy/Ice_and_Fire/1.20/src/main/java/com/github/alexthe666/iceandfire/pathfinding/raycoms/Pathfinding.java
- FTB Chunks: https://raw.githubusercontent.com/FTBTeam/FTB-Chunks/main/README.md · KubeJS: https://raw.githubusercontent.com/KubeJS-Mods/KubeJS/main/README.md
- Tags comuns do Fabric: v1 (1.20.1) e v2 (1.21.1), links na seção 6.
- **Não acessados** (proxy bloqueou; conferir): Cobblemon (gitlab.com/cable-mc/cobblemon), wiki do GeckoLib, docs do NeoForge/Forge (config spec, PermissionAPI), Open Parties and Claims, Jade, EMI, Curios/Accessories, páginas do Modrinth/CurseForge sobre distribuição em modpacks. A busca na web estava desativada nesta sessão; as afirmações sobre Pixelmon, Alex's Mobs e reclamações de packmakers são conhecimento geral, não verificado aqui.
