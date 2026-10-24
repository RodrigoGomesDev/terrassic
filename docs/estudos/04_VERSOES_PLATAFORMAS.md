# 04 — Estratégia de versões e plataformas (Java/Bedrock) para o Terrassic

*Pesquisa feita em 24/10/2026. Contexto: o Terrassic hoje está em 1.20.1, Fabric + Forge, Architectury API 9 e Architectury Loom, mapeamentos Mojang, GeckoLib 4.8.*

> **Sobre as fontes.** A busca web genérica estava bloqueada nesta sessão. Por isso os dados vêm de leitura direta de fontes primárias: blogs oficiais do NeoForge e do Fabric, minecraft.wiki, a API pública do Modrinth, a listagem do CurseForge, o site de arquivos do Forge, o wiki do GeckoLib, o registro npm e minecraft.net. Todas foram consultadas em 24/10/2026. As contagens do Modrinth valem para essa data. Quando algo vem da minha memória e não foi confirmado agora, aparece marcado como *(não verificado)*.

---

## 1. Minecraft Java em 2025–2026: modelo de lançamento e versões

### 1.1 "Game drops" e a nova numeração
- Desde 2024 a Mojang lança "game drops" menores, várias vezes por ano, no lugar de uma grande atualização anual (https://en.wikipedia.org/wiki/Minecraft).
- **Numeração nova a partir de 2026:** o formato agora é `ano.drop.hotfix`. Por exemplo, `26.2.1` seria o primeiro hotfix do segundo drop de 2026. A 1.21.11 foi a última versão com prefixo "1." (https://neoforged.net/news/2025-retrospection/, publicado em 01/01/2026).

### 1.2 Versões lançadas desde a 1.20.1
Datas tiradas da API do Modrinth (https://api.modrinth.com/v2/tag/game_version, consultada em 24/10/2026):

| Versão | Data | Drop / observação |
|---|---|---|
| 1.20.1 | 12/06/2023 | Versão atual do Terrassic (Java 17) |
| 1.20.5 / 1.20.6 | 23/04/2024 e 29/04/2024 | "Armored Paws": **data components** substituem o NBT dos itens; passa a exigir **Java 21** |
| 1.21 / 1.21.1 | 13/06/2024 e 08/08/2024 | "Tricky Trials": a 1.21.1 virou a versão "estável" para mods |
| 1.21.2 a 1.21.4 | out/2024 a 03/12/2024 | Bundles, Pale Garden, *entity render states* |
| 1.21.5 | 25/03/2025 | "Spring to Life": variantes de porco, vaca e galinha por bioma |
| 1.21.6 a 1.21.8 | jun–jul/2025 | "Chase the Skies" (happy ghast) |
| 1.21.9 / 1.21.10 | 30/09/2025 e 07/10/2025 | "The Copper Age" |
| 1.21.11 | 09/12/2025 | "Mounts of Mayhem": `ResourceLocation` vira `Identifier` |
| **26.1** (26.1.1, 26.1.2) | 24/03/2026 (26.1.2 saiu em 09/04/2026) | "Tiny Takeover": **jogo sem ofuscação**, **Java 25** |
| **26.2** | 16/06/2026 | "Chaos Cubed": **renderizador Vulkan experimental** |
| **26.3** | 15/09/2026 | "Wilderness Bound": GLFW substituído por SDL |
| 26.4 (snapshots) | snapshot-1 em 22/09/2026, snapshot-5 em 20/10/2026 | Último drop de 2026: cavernas de gelo, mob "Frostbite" (https://www.minecraft.net/en-us/article/drop-4-2026-testing) |

Em setembro de 2026 a Mojang anunciou "The Sift", uma nova dimensão prevista para 2027 (https://en.wikipedia.org/wiki/Minecraft).

### 1.3 Mudanças técnicas desde a 1.20.1 que afetam mods
1. **Data components na 1.20.5** (abril/2024). O campo `tag` dos itens deixou de existir. Dados customizados vão para `minecraft:custom_data` ou para componentes tipados com codec, e componentes iguais ao valor padrão nem são salvos (https://minecraft.wiki/w/Java_Edition_1.20.5). Para o Terrassic isso pega seringas de DNA, fósseis, ovos e qualquer item que hoje guarda estado em NBT. A mesma versão trouxe atributos novos úteis para dinossauros de tamanhos diferentes, como `generic.scale` e `generic.step_height`, e renomeou vários campos NBT de entidades.
2. **Registros na 1.21.2** (22/10/2024). `Item.Properties` passou a exigir um ID. `registry()` virou `lookup()`. `getHolder` virou `get`, que devolve um `Holder`. `BlockEntityType.Builder` foi removido. Receitas deixaram de ser sincronizadas com o cliente (https://neoforged.net/news/21.2release/).
3. **Separação entre thread de jogo e thread de render.** A partir da 1.21.2 o render passou a usar *render states*. É o motivo do GeckoLib 5 existir: o renderer trabalha sobre um `GeoRenderState` extraído previamente e não tem mais acesso à entidade durante o render (https://wiki.geckolib.com/docs/geckolib5/updating/important/conceptual-changes).
4. **Variantes de mobs por bioma** (wolf na 1.20.5; porco, vaca e galinha na 1.21.5) e cada vez mais conteúdo data-driven. Na 26.1 as trocas de aldeão passaram a vir de datapacks (https://minecraft.wiki/w/Java_Edition_26.1). Na 26.2 entrou o registro `sulfur_cube_archetype`, que define arquétipos de mob em JSON, e novos atributos (`bounciness`, `friction_modifier`, `air_drag_modifier`) (https://minecraft.wiki/w/Java_Edition_26.2). A direção da Mojang é clara: mobs configuráveis por dados.
5. **26.1, jogo sem ofuscação + Java 25** (24/03/2026). Os nomes oficiais da Mojang agora valem em runtime. O Intermediary e o Yarn foram abandonados, e o Fabric Loom ganhou um plugin novo sem remapeamento (`net.fabricmc.fabric-loom`): `modImplementation` virou `implementation` e `remapJar` virou `jar`. "Nenhum mod da 1.21.11 ou anterior funciona sem, no mínimo, recompilação" (https://fabricmc.net/2026/03/14/261.html, 14/03/2026; https://fabricmc.net/2025/10/31/obfuscation.html, 31/10/2025). Outras quebras: `ItemStack` não pode mais ser criado antes de os registros carregarem (entra o `ItemStackTemplate`); `GuiGraphics` virou `GuiGraphicsExtractor`; `Screen#render` virou `extractRenderState`; `ChunkSectionLayer` substitui `RenderType` para terreno (https://neoforged.net/news/26.1release/, 24/03/2026).
6. **Render na 26.2.** Chegou um backend Vulkan 1.2 experimental, com OpenGL como alternativa, e o depth buffer foi invertido (https://minecraft.wiki/w/Java_Edition_26.2). O Fabric avisou que a 26.1 seria a última versão só com OpenGL e que chamadas GL diretas precisam migrar para a API Blaze3D (https://fabricmc.net/2026/03/14/261.html).
7. **26.3** (15/09/2026). GLFW foi substituído por SDL, o que muda constantes de input e o foco de texto em widgets customizados. Combustível e compostagem passaram a ser componentes de item, receitas de poção viraram JSON, e receitas e advancements agora ficam em registros recarregáveis (https://fabricmc.net/2026/09/15/263.html).
8. **Vibrant Visuals** saiu no Bedrock em junho de 2025. Para o Java, a página oficial diz apenas que o trabalho "continua", sem data (https://www.minecraft.net/en-us/updates/minecraft-updates-timeline-and-evolution, consultada em 24/10/2026). O Vulkan da 26.2 parece ser a base técnica para isso. Mods com shaders próprios ou render customizado pesado vão sofrer mais. Mods que usam só GeckoLib, menos.

**Resumo para o Terrassic:** sair da 1.20.1 para a 1.21.1 é um port **médio** (data components, registros, troca de Forge por NeoForge). Ir para a 26.x é um port **pesado**: Java 25, toolchain sem remap, GeckoLib 5 com render states, ItemStackTemplate, GUIs reescritas e Vulkan.

---

## 2. Mod loaders em 2026

### 2.1 Forge e NeoForge
- O **NeoForge** acompanha cada versão em horas: em 2025 os builds saíram entre ~40 minutos e 3 horas depois de cada release da Mojang. Também publica builds para snapshots (https://neoforged.net/news/2025-retrospection/). No início de 2026 a 1.21.1 seguia como sua versão mais popular, com mais de 16.000 mods, e a equipe diz que o crescimento do NeoForge 1.21.1 superou o do Forge 1.20.1 (mesma fonte). O NeoForge praticamente ignorou a 1.20.1: a equipe admite que muitos mods e packs já tinham saído em Forge (https://neoforged.net/news/2024-retrospection/). Para a 26.1, um mantenedor estima que ela "substituirá a 1.21.1 como próxima versão estável de modding", e deixa claro que é palpite pessoal (https://neoforged.net/news/26.1release/, 24/03/2026).
- O **Forge (MinecraftForge)** continua ativo. Tem builds para 26.1, 26.2 e 26.3, e o recomendado para 26.3 é o 66.1.0, de 21/10/2026 (https://files.minecraftforge.net/net/minecraftforge/forge/). O que sumiu foi o ecossistema em volta dele nas versões novas.

### 2.2 Fabric e Quilt
O Fabric lançou suporte para 26.1 (14/03/2026), 26.2 (15/06/2026) e 26.3 (15/09/2026). A recomendação atual é Loader 0.19.5 e Loom 1.17 com Gradle 9.6 (https://fabricmc.net/blog/; https://fabricmc.net/2026/09/15/263.html). O Quilt ainda aparece como loader em vários projetos, mas na prática virou nicho; não é alvo que valha manter separado.

### 2.3 Participação por loader (projetos de mod no Modrinth, 24/10/2026)

| Versão | Total de mods | Forge | NeoForge | Fabric |
|---|---|---|---|---|
| 1.20.1 | 34.846 | 24.211 | (irrelevante) | 17.778 |
| 1.21.1 | 32.259 | 5.247 | 21.515 | 19.478 |
| 1.21.11 | 19.356 | — | — | — |
| 26.1.x | 15.792 | — | — | — |
| 26.2 | 14.109 | 2.599 | 4.956 | 12.795 |
| 26.3 | 8.748 | — | — | — |

Fonte: buscas facetadas na API do Modrinth (por exemplo, https://api.modrinth.com/v2/search?limit=1&facets=[["categories:neoforge"],["versions:1.21.1"],["project_type:mod"]]). Um mod pode aparecer em mais de um loader. O Modrinth puxa para o Fabric; o CurseForge puxa para Forge e NeoForge.

**Leitura:** a partir da 1.21 o **Forge virou o terceiro loader**. Na 1.21.1 o NeoForge tem cerca de 4x mais mods que o Forge. Nas versões 26.x o Fabric lidera, porque o pessoal de performance e vanilla+ atualiza primeiro, e o NeoForge vem em segundo.

### 2.4 Ferramentas multi-loader e multi-versão
- **Architectury API** continua mantida e acompanha as versões novas: 22.0.3 para 26.3, 21.1.11 para 26.2 e 20.1.16 para 26.1.2, todas de 26/09/2026. A linha 1.21.1 (13.0.11) recebeu update em 23/07/2026 (https://api.modrinth.com/v2/project/architectury-api/version). **Porém, de 1.21 em diante ela só tem builds para NeoForge e Fabric, sem Forge.** Na prática, quem usa Architectury API e sobe de versão já está largando o Forge.
- **MultiLoader-Template** (Jared): é um projeto com source set common, NeoForge e Fabric, sem dependência de runtime. O branch atual é `26.2` e exige Java 25. Forge foi removido; o README só o cita como exemplo de loader que dá para tirar (https://github.com/jaredlll08/MultiLoader-Template). Virou o caminho "sem biblioteca" preferido de muitos autores grandes *(a adoção em si não foi verificada)*.
- **Stonecutter**: plugin Gradle para manter várias versões de MC no mesmo código, com comentários condicionais. Mudou para o Codeberg (https://github.com/stonecutter-versioning/stonecutter, que agora é só espelho de codeberg.org/stonecutter/stonecutter). Útil para segurar 1.20.1, 1.21.1 e 26.x no mesmo branch.
- **Sinytra Connector** (roda mods Fabric no NeoForge): continua em **beta** e só para NeoForge. A última versão é a 3.1.0-beta.2 para 26.2, de 14/10/2026 (https://api.modrinth.com/v2/project/connector/version). Não dá para contar com ele como estratégia de distribuição; um build nativo sempre vai ser melhor.

---

## 3. Em que versões o público modado joga de fato

### 3.1 Modpacks (24/10/2026)
Mais populares no CurseForge (https://www.curseforge.com/minecraft/search?class=modpacks&sortBy=popularity):
- **All the Mods 10**: 1.21.1 NeoForge, 22,4M downloads, atualizado em 15/10/2026. A variante ATM10 To the Sky também é 1.21.1 NeoForge, com 3,6M.
- **All the Mods 11**: 26.1.2 NeoForge, 1,1M downloads, atualizado em 15/10/2026. É o primeiro grande "kitchen sink" em 26.x.
- **Prominence II: Hasturian Era**: 1.20.1 Fabric, 13,1M.
- **Better MC [FORGE] BMC4**: 1.20.1 Forge, 18,7M. A versão Fabric (BMC2) também é 1.20.1, com 3,7M no Modrinth.
- **COBBLEVERSE** e **Cobblemon SMP**: 1.21.1 Fabric.
- Packs de terror e zumbi (DeceasedCraft, Cursed Walking, VerityCraft, NightfallCraft): quase todos **1.20.1 Forge**.
- Packs de performance e vanilla+ (Fabulously Optimized, Immersed With Shaders): 26.2 e 26.3 Fabric.

No Modrinth (https://api.modrinth.com/v2/search?index=downloads&facets=[["project_type:modpack"]]) aparecem também o Cobblemon Official Modpack (1.21.1 Fabric, 11,5M) e The Pixelmon Modpack (1.21.1 Forge/NeoForge, atualizado em 22/10/2026). Quantidade de modpacks por versão no Modrinth: 1.20.1 tem 7.271, 1.21.1 tem 4.788, 26.2 tem 1.549 e 26.1.2 tem 1.388.

### 3.2 A concorrência direta (mods de dinossauro, Modrinth, 24/10/2026)
- Fossils and Archeology: Revival: 590k downloads, chega até a 1.20.1.
- Jurassic Reborn: 266k, Forge/NeoForge até a 1.21.1.
- Prehistoric Dinosaurs: 226k, Fabric 1.20.x, parado desde maio de 2024.
- Jurassic Saga e Jurassic Revived: Fabric, Forge e NeoForge, 1.20.1 e 1.21.1.

Fonte: https://api.modrinth.com/v2/search?index=downloads&query=dinosaur&facets=[["project_type:mod"]].

**Nenhum mod de dinossauro relevante está em 26.x.** A briga hoje acontece em 1.20.1 e 1.21.1.

### 3.3 Até quando a 1.20.1 vale a pena
A 1.20.1 ainda tem o **maior catálogo de mods** (34,8k no Modrinth) e a maior base de modpacks. Ela é a "1.12.2 da vez", com força principalmente em packs de aventura, terror e RPG em Forge. Por outro lado, ela não recebe novidade do vanilla e o NeoForge nunca a abraçou. Libs grandes seguem dando patches: o GeckoLib 4.8.4 para 1.20.1 saiu em 20/06/2026. Mesmo assim, o crescimento já está em 1.21.1 e 26.x. **Estimativa:** a 1.20.1 continua relevante como base instalada até 2027, mas lançar algo novo *só* nela vai parecer datado em 2027.

---

## 4. Bibliotecas-chave por versão (24/10/2026)

| Lib | 1.20.1 | 1.21.1 | 26.x |
|---|---|---|---|
| **GeckoLib** | 4.8.4 (Forge e Fabric, 20/06/2026) | **4.9.3** (Forge, NeoForge e Fabric, 16/09/2026) | **5.5.x**: 5.5.6 para 26.2 e 26.3 (16/09/2026); a 26.2 tem até build Forge |
| Architectury API | 9.x (Forge e Fabric) | 13.0.11 (NeoForge e Fabric) | 20.x, 21.x e 22.x (NeoForge e Fabric) |
| JEI | sim | sim | 26.1 a 26.3 (atualizado em 23/10/2026) |
| EMI | sim | sim | **parou na 1.21.1** (último update em 13/05/2026) |
| Jade | sim | sim | 26.3 |
| Curios | sim | sim | 26.3 (Forge, NeoForge e Fabric) |
| Accessories (wisp-forest) | — | sim | parou na 1.21.10 |
| Create (integração possível) | sim | sim | **não existe em 26.x** |

Fontes: https://api.modrinth.com/v2/project/geckolib/version, https://api.modrinth.com/v2/projects?ids=[...], https://api.modrinth.com/v2/project/jei, https://api.modrinth.com/v2/project/create.

- O **GeckoLib 4** cobre da 1.19.3 até a 1.21.4. O **GeckoLib 5** cobre da 1.21.5 até a 26.3 (https://wiki.geckolib.com/), com exceção da 1.21.1, que segue recebendo a linha 4.9. Ou seja, **o port 1.20.1 → 1.21.1 mantém o GeckoLib 4**, quase sem mudar o código dos renderers. Já ir para qualquer versão 1.21.5+ ou 26.x obriga a reescrever renderers, layers e queries Molang no modelo de render state em duas etapas.
- **Cobblemon**, o caso mais parecido com o Terrassic (mod grande de criaturas, com sistema próprio de modelos/animações em formato Bedrock via Blockbench): o último build Forge foi o 1.5.2 para 1.20.1, em 27/05/2024. Depois disso foi para **1.21.1 com Fabric + NeoForge** e **continua lá**: 1.7.0 em novembro de 2025, 1.8.0 em 06/09/2026 e 1.8.2 em 11/10/2026 (https://api.modrinth.com/v2/project/cobblemon/version; https://modrinth.com/mod/cobblemon, 37,1M downloads). A estratégia deles é ficar numa única versão "LTS" por bastante tempo, fazendo grandes atualizações de conteúdo em cima dela, e só pular quando o ecossistema assenta. O mesmo vale para o Create, que está em 1.21.1 desde 2024 e não tem port para 26.x.

---

## 5. Bedrock: dá para fazer uma versão depois?

**Técnica.** No Bedrock não existe código Java. Uma entidade custom é um *behavior pack* (componentes JSON para física, AI, atributos, spawn) mais um *resource pack* (geometria, animações, animation controllers, Molang), e a lógica vai na **Script API em JavaScript**. A versão estável do `@minecraft/server` é a **2.10.0** (15/09/2026), com versões mensais desde 2025 (2.3.0 em 28/10/2025 → 2.10.0). Há uma beta 2.13.0 em preview 26.70, e o `@minecraft/server-ui` está na 2.2.0 (registro npm, https://registry.npmjs.org/@minecraft/server, consultado em 24/10/2026). A documentação é de 15/10/2026 (https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/).

**Vantagem do Terrassic:** os modelos e animações do GeckoLib, exportados do Blockbench, usam o formato de geometria e animação do Bedrock (`.geo.json`, `.animation.json`, Molang) *(fato conhecido do ecossistema; o wiki atual do GeckoLib não detalha o formato)*. Isso significa que **os assets de arte podem ser reaproveitados quase direto**. O que precisa ser reescrito é toda a lógica: dieta, comportamento, genética, incubação.

**Limites.** As AIs ficam presas a componentes prontos mais scripts. Não há render customizado. Entidades muito grandes têm limites de hitbox e culling. A performance com muitos mobs é mais restrita. Sistemas complexos como DNA ou parques precisariam ser reprojetados.

**Distribuição.**
- Add-ons grátis podem ser distribuídos fora do Marketplace (CurseForge Bedrock, MCPEDL), mas o alcance é menor e não há monetização oficial.
- O **Marketplace exige ser Partner**: portfólio, postura de empresa, arte-chave, trailers. Em 24/10/2026 a página informava que **as inscrições estão fechadas** e indicava "publishing partners" (Pathway Studios, Waypoint Studios, Blocklab Studios) como caminho (https://www.minecraft.net/en-us/partner).
- O Marketplace vende add-ons de criaturas com regularidade. O destaque de outubro de 2026 tinha Parasite Outbreak, Cave Dweller e The Bloop, de partners como Mythicus, XP Games e Blocklab (https://www.minecraft.net/en-us/article/marketplace-spotlight-october-2026).
- A Mojang/Universal tem uma DLC oficial **Jurassic World** no Marketplace *(não verificado nesta sessão)*. Isso sugere demanda, mas também concorrência com IP oficial e o cuidado de nunca usar marcas como "Jurassic".

**Como os outros fizeram.** Cobblemon e Pixelmon continuam só no Java em out/2026 (os dois dependem de IP de terceiros, o que inviabiliza o Marketplace). Não encontrei um mod Java grande de criaturas que tenha sido portado com sucesso para o Bedrock pela mesma equipe; normalmente são projetos Bedrock nativos de partners.

**Conclusão Bedrock:** é viável como **projeto paralelo e separado** (Bedrock "Terrassic Lite"), reaproveitando a arte, depois que o Java estiver consolidado. O caminho mais realista para o Marketplace é parceria com um publishing partner. Não vale a pena moldar a arquitetura Java em função do Bedrock além de duas coisas: manter assets em Blockbench/Bedrock e manter os dados das espécies em JSON.

---

## 6. Recomendação

### 6.1 Decisões
1. **Não lançar a v1.0 só em 1.20.1.** Usar a 1.20.1 (Forge + Fabric, como já está) para terminar o núcleo e soltar alphas e betas. Antes da v1.0, portar para **1.21.1 com NeoForge + Fabric** e lançar a 1.0 nas duas versões. A 1.21.1 é hoje o "LTS de fato": tem o ATM10 (o maior pack do CurseForge), Cobblemon (1.8.2 em 11/10/2026), Create, Pixelmon e GeckoLib 4.9 com manutenção ativa.
2. **Forge só na 1.20.1.** Na 1.21.1 o Forge tem cerca de 1/4 dos mods do NeoForge, e a Architectury API nem oferece Forge da 1.21 em diante. Manter Forge em 1.21+ significaria abandonar a Architectury API ou escrever a camada própria só para ele. Não compensa.
3. **26.x: esperar o ecossistema escolher.** Hoje os sinais apontam para 26.1.2 (ATM11 e a estimativa do NeoForge), mas Cobblemon e Create ainda não saíram da 1.21.1, e o 26.4 está em snapshot com Vulkan amadurecendo. Reavaliar no 2º trimestre de 2027 e portar para a versão 26.x que tiver ATM/Cobblemon/Create, ou seja, o próximo "LTS".
4. **Build system.** Continuar com Architectury (Loom + API) em 1.20.1 e 1.21.1, onde funciona bem. Para a 26.x, decidir entre Architectury Loom (que precisa suportar o pipeline sem remap) e MultiLoader-Template com ModDevGradle e Fabric Loom; o template já está na 26.2. Para essa troca ser barata, **reduzir desde já o uso direto da Architectury API** (detalhado em 6.3).
5. **Multi-versão:** branches por versão (`1.20.1`, `1.21.1`) com cherry-pick. Quando chegar a terceira versão, avaliar o Stonecutter.

### 6.2 Cronograma sugerido
| Período | Ação |
|---|---|
| **Nov/2026 – Jan/2027** | Refatorar as camadas de abstração (6.3) ainda na 1.20.1. Alphas públicas em 1.20.1 Forge/Fabric para ganhar feedback e entrar em packs de aventura 1.20.1. |
| **Fev – Abr/2027** | Port para 1.21.1 NeoForge + Fabric (Architectury API 13, GeckoLib 4.9). Data components, registros e networking por payload. A 1.21.1 vira o branch principal. |
| **Mai/2027** | **v1.0** em 1.21.1 (principal) e 1.20.1 (Forge/Fabric). Abordar autores de packs (ATM, Cobblemon packs, BMC). |
| **2º tri/2027** | Escolher a versão 26.x-alvo olhando ATM11, Cobblemon, Create e a maturidade do Vulkan/Vibrant Visuals. Spike técnico de GeckoLib 5 com 2–3 dinossauros. |
| **2º semestre/2027** | Port para 26.x (Java 25, sem remap, GeckoLib 5). A 1.20.1 fica só com bugfix e congela no fim de 2027. |
| **2028+** | Avaliar um Bedrock separado reaproveitando a arte, via publishing partner. |

### 6.3 Como estruturar o código agora para os ports saírem baratos
- **Estado de item sem NBT cru.** Modelar cada dado de item (amostra de DNA, qualidade do fóssil, espécie do ovo) como `record` com `Codec` (o DFU já existe na 1.20.1). Na 1.20.1, gravar via codec em `CompoundTag`. Na 1.21.1, esse codec vira direto um `DataComponentType`. O acesso passa por uma interface (`TerrassicItemData.get(stack)`), e o código de gameplay nunca chama `stack.getTag()`.
- **Espécies data-driven.** Tamanho, escala, hitbox, dieta, temperamento, atributos, variantes, biomas de spawn e drops ficam em JSON, carregados por reload listener (e mais tarde por registro dinâmico de datapack). Isso segue a direção da Mojang (variantes por bioma, arquétipos JSON na 26.2), facilita compatibilidade com packs e servidores e serve de especificação para um eventual Bedrock.
- **Renderers "estilo render state" desde já.** Nos `GeoRenderer` e `GeoModel`, concentrar a leitura da entidade num único ponto que monta um objeto de dados (idade, escala, variante, estado de animação) e renderizar só a partir dele. É exatamente o modelo do GeckoLib 5 (`GeoRenderState`, `addRenderData`). Evitar estado mutável persistente no renderer e evitar GL direto. Usar escala via atributo `scale` quando possível (1.20.5+).
- **Camada de plataforma própria.** Uma interface `Platform`/`Services` no common, implementada por loader (via ServiceLoader, no padrão do MultiLoader-Template), cobrindo registro, rede, eventos e config. A Architectury API pode ficar só *por trás* dessa camada; assim dá para trocá-la sem tocar no gameplay.
- **Registro centralizado** num único wrapper. Isso absorve mudanças como `Item.Properties` com ID na 1.21.2, `Holder` e `Identifier` (`ResourceLocation` renomeado na 1.21.11).
- **Rede baseada em payloads tipados** (records com codec de stream), no formato da 1.20.5+, mesmo rodando na 1.20.1.
- **Poucos mixins**, todos documentados e isolados. Usar tags de convenção `c:`.
- **Mapeamentos Mojang** (já é o caso). Esse é o maior seguro para a 26.x sem ofuscação; não adotar Yarn nem Parchment obrigatório.
- **CI** compilando todos os alvos, com GameTests básicos (spawn, crescimento, reprodução).
- **Assets** sempre em Blockbench, nos formatos Bedrock do GeckoLib, versionados no repositório.

### 6.4 Riscos
- **Fragmentação:** manter 1.20.1, 1.21.1 e depois 26.x multiplica o trabalho. Mitigação: congelar a 1.20.1 em feature freeze após a 1.0.
- **Salto 26.x é caro** (GeckoLib 5, Java 25, toolchain nova). Esperar demais e o mod fica preso na 1.21.1, mas é o que Cobblemon e Create estão fazendo com sucesso. Portar cedo demais custa caro se o ecossistema escolher outra 26.x. Mitigação: o spike técnico e a camada de render-state.
- **Architectury no pós-ofuscação:** a API acompanha (22.0.3 para 26.3), mas a toolchain de build é o ponto frágil. Mitigação: a camada de plataforma própria.
- **Vulkan e Vibrant Visuals no Java** podem quebrar shaders ou render custom. Mitigação: usar só a pipeline do GeckoLib e vanilla.
- **Bedrock:** inscrições de partner fechadas e concorrência com IP oficial. Tratar como opção futura, não como compromisso.
- **Dependências que ficaram para trás** (EMI e Create não estão em 26.x): integrações devem ser opcionais (soft-dependency).
