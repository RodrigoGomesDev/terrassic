# Terrassic: estado da arte em modelos 3D e animação de criaturas, e o pipeline para 200+ espécies

> Pesquisa 02 · 24/10/2026 · escopo: bibliotecas de animação, técnicas de "vida", criaturas gigantes, performance, direção de arte e pipeline.
>
> **Como foi feita.** A busca na web estava bloqueada nesta sessão. Por isso quase tudo veio de **leitura direta de código-fonte e documentação oficial**: GeckoLib 4.8.4 (branch 1.20.1) e 5.5.6 (branch 26.2), wiki do GeckoLib 5 (repositório Tslat/Geckolib-Wiki), wiki do AzureLib, Ice and Fire (branch 1.20), Citadel/Alex's Mobs (1.20), JurassiCraft (1.12, abril/2021), Sodium, Entity Culling, a documentação do OptiFine/Iris, o código decompilado do Minecraft 1.20.1 e o catálogo de plugins do Blockbench 5.2.2. O GitLab do Cobblemon e a wiki dele bloquearam o acesso, então o que digo do Cobblemon vem do que eu já sabia e está marcado **(não verificado agora)**. Os números que são estimativas estão marcados **(estimativa)**.
>
> Medi também o repositório do Terrassic (`tools/modelgen`, `art/build_report.json`, `tools/javagen/gen_species.py`, `DinosaurEntity`), com 53 modelos no relatório de build.

---

## 0. Resumo em 8 pontos

1. **Fique no GeckoLib.** Use o 4.8 no 1.20.1 e o GeckoLib 5 quando portar (ele cobre do 1.21.5 ao 26.3). O formato `.geo.json` e `.animation.json` é o mesmo, então o porte reescreve o código Java e mantém os assets. O GeckoLib 5 obriga a separar os dados da renderização ("render state"). Vale escrever a camada procedural já nesse estilo hoje.
2. **O maior problema visual de hoje é a densidade de texel.** No jogo, ela varia de **4,9 px/m** (Brachiosaurus) a **66,7 px/m** (Mononykus), uma faixa de 13 vezes. O vanilla usa 16 px por bloco em quase todos os mobs. Lado a lado, um Compsognathus e um Argentinosaurus parecem de jogos diferentes. Os filhotes pioram a conta, porque o filhote de T. rex fica com cerca de 63 px/m.
3. **Hoje o pé escorrega.** O controlador "movement" toca `walk` e `run` em velocidade fixa. O GeckoLib 4 tem `setAnimationSpeedHandler`, mas ele multiplica o tempo total da animação, então mudar a velocidade no meio do ciclo faz a fase pular. A solução é um controlador que acumula a fase pela distância andada. O pipeline já conhece a perna, então pode calcular o passo sozinho.
4. **Falta a camada procedural** que os melhores mods usam: olhar distribuído pelo pescoço, cauda com inércia (ChainBuffer), IK de pé no terreno (o LegSolver do JurassiCraft, reaproveitado pelo Ice and Fire), respiração aditiva e ociosos aleatórios. O GeckoLib 5 já tem controladores aditivos.
5. **Os gigantes precisam de hitbox multiparte.** O Argentinosaurus tem 35 m e hitbox de 6 × 10, então pescoço e cauda não existem para o combate. O vanilla só trata partes no Ender Dragon (código fixo). O Forge tem `PartEntity`, o Fabric não, então o Architectury vai precisar de mixin. Outro caminho são as "bone hitboxes" do AzureLib.
6. **A conta de performance é por vértice na CPU.** O GeckoLib transforma 24 vértices por cubo, um por um, todo frame, e não passa pelo caminho rápido que o Sodium dá ao `ModelPart` vanilla. Com shaders, a conta dobra, porque as entidades vão também para o passe de sombra. Isso pede orçamento de cubos, remoção de faces escondidas e **LOD gerado pelo pipeline** (as tags `tooth_cube`, `claw`, `scute` já existem).
7. **Paleoarte:** o padrão atual é bom (lábios no T. rex, escamas segundo Bell et al.). Faltam três regras: contrassombreamento como base, penas por "franjas" de planos com recorte, e **filhote com geometria própria**. Cristas, chifres e domos mudam com a idade, então só encolher o adulto não basta. O dimorfismo sexual quase não tem evidência anatômica, então deve aparecer mais na cor do que na forma.
8. **Pipeline:** a autoria por código é a vantagem competitiva do Terrassic (consistência, LOD, orçamento, validação). O risco é o gerador sobrescrever edições feitas à mão. Para aceitar arte da comunidade, a proposta é um "contrato de rig", overrides por cubo que sobrevivem ao gerador, e um CI de qualidade que roda o checklist da seção 7.

---

## 1. Bibliotecas de modelo e animação

| Opção | Versões do MC | Prós para 200+ criaturas | Contras |
|---|---|---|---|
| **GeckoLib 4** (4.8.4 no Terrassic) | 1.19.3 a 1.21.4 | Padrão de fato (Mowzie's Mobs, Prehistoric Fauna e centenas de outros). Formato Bedrock exportado pelo plugin oficial do Blockbench. Molang com `query.ground_speed`, `query.yaw_speed`, `query.distance_from_camera`. Controladores, `triggerableAnim`, keyframes de som, partícula e instrução. Glowmask. | Renderiza cubo por cubo na CPU (`GeoRenderer.renderCube` aloca `Matrix4f`/`Vector3f` por cubo e por face). O `setAnimationSpeed` multiplica o tempo total (`adjustTick = speed × (tick − offset)`), o que faz a fase pular ao mudar a velocidade. Manipula o osso direto (estado vaza entre passes). |
| **GeckoLib 5** (5.5.6, set/2026) | 1.21.5 até **26.3** ([wiki](https://wiki.geckolib.com)) | Reescrito para o "render state" do vanilla: extrai `GeoRenderState`, o animável é descartado e tudo é instanciado e sem estado. `AnimationController` e `AnimationProcessor` foram reescritos, e o wiki fala em ganho de desempenho. `BoneSnapshots` pula ossos não modificados. `BoneUpdater`s para mexer em osso por código. `BonePositionListener` dá a posição do osso no mundo. **Controladores aditivos** (`additiveAnimations()`). Glowmask que não apaga a textura base e opção `shouldRespectWorldLighting`. | Porte trabalhoso: todo acesso direto a `GeoBone` vira `BoneUpdater`, e o renderer não lê mais a entidade depois da extração ([conceptual changes](https://wiki.geckolib.com/docs/geckolib5/updating/important/conceptual-changes)). Continua gerando a geometria na CPU (`submitCustomGeometry`). |
| **AzureLib** (fork do GeckoLib 4, API própria "Az*") | 1.7.10 a 26.3 (branches no GitHub) | **Bone hitboxes** prontas (`AzHitboxSet` por osso, multiplicador de dano, papéis combat/interact/anchor, depuração com F3+B) ([doc](https://moddedmc.wiki/en/project/azurelib/latest/docs/misc/hitboxes)). **AzureNavigation**: pathfinder que considera a caixa inteira, baseado no `MMPathNavigateGround` do Mowzie's/pau101 ([doc](https://moddedmc.wiki/en/project/azurelib/latest/docs/misc/azurenavigation_101)). Controladores aditivos e procedural em `setCustomAnimations`. | Um mantenedor principal e ecossistema menor. As hitboxes de osso dependem de **poses relatadas pelos clientes**: um cliente modificado pode deslocá-las até `maxReach`, e sem jogador por perto voltam à caixa vanilla. A API diverge do GeckoLib, então trocar custa caro. |
| **Cobblemon** (Bedrock geo + "posers" JSON + Molang) **(não verificado agora)** | 1.21.1 / 1.20.1 / 1.19.2 ([Modrinth](https://modrinth.com/mod/cobblemon)) | Um único sistema dirigido por dados para mais de 1000 modelos: cada espécie tem um JSON de poses (em pé, andando, voando, nadando, dormindo, batalha) com condições, tempo de transição, olhar (`q.look`), animações Bedrock e "quirks" (piscar e ociosos aleatórios). Pelo que lembro, converte a geometria Bedrock em `ModelPart` vanilla e assim herda o caminho rápido do Sodium. | É código do Cobblemon (MPL), não uma biblioteca. Copiar o **modelo de dados** é o que interessa, não a dependência. |
| **Modelo Java vanilla** (`ModelPart` + `AnimationDefinition`, como Warden, Camelo, Farejador e Tatu) | todas | Sem dependência. O Sodium otimiza `ModelPart` (`EntityRenderer.renderCuboid` transforma 8 cantos e escreve direto no buffer). Existe o plugin "Animation to Java" no Blockbench. | Animação vira código Java, sem Molang. A API muda quase a cada versão grande (render state no 1.21.2, coletor de submissão no 1.21.9+), então o porte de 200 espécies vira inferno. Só vale como **alvo de LOD distante** (seção 4). |
| **PlayerAnimator / Emotecraft** | jogador | Animam só o jogador. O PlayerAnimator foi **descontinuado** em favor do PAL ([README](https://github.com/KosmX/minecraftPlayerAnimator)). | Útil só para a pose do cavaleiro (abraçar o pescoço, segurar as rédeas) via PAL. Fora isso, irrelevante. |

**Veredito.** Mantenha GeckoLib 4.8 no 1.20.1 e planeje o GeckoLib 5 no porte. Não troque por AzureLib só pelas hitboxes: dá para fazer hitbox multiparte no servidor (seção 3) sem confiar no cliente. Desde já, escreva a camada procedural como uma função pura do tipo `PoseInput` → deltas por osso, alimentada por um "snapshot" da entidade. Isso mapeia 1:1 para `GeoRenderState` + `BoneUpdater` do GeckoLib 5.

---

## 2. Técnicas que fazem a criatura parecer viva

O que os mods de referência fazem, com evidência no código:

**2.1 Olhar distribuído pelo pescoço.** O Citadel (base do Alex's Mobs e do Ice and Fire) tem `faceTarget(yaw, pitch, rotationDivisor, AdvancedModelBox... boxes)`, que divide o olhar entre vários ossos. O Terrassic gira só o osso `head` (`DefaultedEntityGeoModel(..., "head")`). Num saurópode de 10 m de pescoço, ou num T. rex, isso parece uma cabeça de boneco. **Fazer:** dividir yaw e pitch em `neck1..n` + `head`, com pesos (ex.: 15/25/25/35 %), limites por espécie, suavização (lerp de ~0,2 por tick) e um atraso maior nos animais grandes.

**2.2 Cauda e pescoço com inércia (movimento secundário).** O Ice and Fire usa `ChainBuffer tail_buffer` e `IFChainBuffer` para rolagem e arfagem. O JurassiCraft tem `FixedChainBuffer`. O Alex's Mobs tem `LaviathanNeckSolver` (acumula a diferença `yBodyRotO − yBodyRot` e devolve aos poucos, com tempo de buffer e decremento por segmento). O Citadel tem `chainSwing`/`chainWave`/`chainFlap` para ondas com defasagem por segmento. **Fazer:** um `ChainBuffer` por cadeia (cauda, pescoço, cauda-remo dos marinhos), alimentado pela velocidade de giro do corpo. É barato e é a técnica que mais "vende" peso.

**2.3 IK de pé no terreno.** O `LegSolver` do Ice and Fire diz no cabeçalho "Code from JurassiCraft, used with permission, by paul101". Ele mede a altura do chão sob cada pé (`getCollisionShape`), limita por `range` e sobe ou desce 0,25 por tick. O `LegArticulator` do JurassiCraft baixa o corpo pela média, estica a coxa e a canela de cada lado e, nos quadrúpedes, **inclina o tronco** (`atan2(comprimento, alturaTrás − alturaFrente)`) e compensa no pescoço e nos braços. **Fazer:** levar isso para os arquétipos (bípede e quadrúpede). Em escada e encosta, é a diferença entre "mod amador" e "AAA".

**2.4 Ciclo de passo casado com a velocidade (pé sem escorregar).** O JurassiCraft dispara som de passada pelo ângulo do pé (`FootStatus.DOWN`), o que só funciona porque o ciclo está sincronizado. No Terrassic, `movementAnimation` escolhe `walkAnim`/`runAnim` sem ajustar a velocidade. **Fazer:**
- O `modelgen` calcula, para cada `walk`/`run`, o **comprimento da passada** (distância que o pé de apoio percorre para trás num ciclo, na escala do jogo) e grava `stride_m` e `cycle_s` no `build_report.json`.
- No Java, um `AnimationController` próprio sobrescreve `adjustTick` para **acumular** a fase (`fase += dt × velocidade / (stride_m / cycle_s)`). Assim não há salto quando a velocidade muda, ao contrário do `setAnimationSpeed` puro.
- Misturar walk e run pela velocidade (ou trocar com transição curta perto do limiar) e manter o padrão de passo (passo → trote → galope nos quadrúpedes, e nunca galope em saurópode).
- Referência de velocidade: T. rex ~5 a 8 m/s no máximo ([Sellers et al. 2017](https://peerj.com/articles/3420/); [Hutchinson & Garcia 2002](https://www.nature.com/articles/415349a)).

**2.5 Camadas aditivas.** Respiração (escala do tórax de 1,00 a 1,02 a ~0,2 Hz nos grandes, mais rápida nos pequenos), piscar, olhar, tremor de dor e inclinação na curva (`query.yaw_speed`) somados por cima de walk/idle. O GeckoLib 5 tem `additiveAnimations()`. No 4, dá para usar Molang ou um `setCustomAnimations` próprio. **Corpo de cima e de baixo:** no GeckoLib, uma animação só controla os ossos que têm keyframes. Por isso `roar`, `eat` e `call` devem animar **só pescoço, cabeça, mandíbula e braços**, para tocar enquanto o animal anda. Hoje são animações de corpo inteiro que congelam as pernas.

**2.6 Ociosos aleatórios (o "quirk" do Cobblemon).** De 8 a 20 s entre eventos: farejar, sacudir, coçar, bocejar, olhar em volta, mexer a cauda, trocar o peso de perna. Dois ou três por arquétipo, com variação de ritmo por indivíduo (semente pelo UUID), já tiram o efeito "clone".

**2.7 Transições.** O Ice and Fire faz pose a pose (`transitionTo`, com `distance()` pelo menor ângulo). No GeckoLib, `transitionLength` dá o blend. Use transição proporcional à massa (4 a 6 ticks nos pequenos, 10 a 14 nos gigantes) e animações de passagem (`sit_down`, `stand_up`, `lie_down`) como one-shot antes do loop.

**2.8 Peso, morte e olhos.**
- **Peso:** som e partícula nas passadas (poeira e tremor de câmera perto dos gigantes), mandíbula sincronizada ao rugido, e cabeça estabilizada na corrida.
- **Morte:** nenhum mod grande usa ragdoll físico com rig de cubos (é caro e dessincroniza com o servidor). O padrão é queda animada + carcaça, que o Terrassic já tem (`knocked_out` + `CarcassRenderer`). Falta ajustar a pose deitada ao terreno com o LegSolver e ter 2 variantes de queda.
- **Olhos:** pupila com 1 px de brilho e pálpebra para piscar e dormir. É o que o jogador lê primeiro.

---

## 3. Criaturas gigantes

**Hitbox multiparte.** No vanilla, o Ender Dragon é tratado por código fixo: `ServerLevel.dragonParts` (um `Int2ObjectMap<EnderDragonPart>`) e `getSubEntities()`. O Forge generaliza isso com `PartEntity`/`isMultipartEntity()`. **O Fabric não tem equivalente.** Com Architectury, faça uma camada `common` própria (partes como `Entity` sem física, posicionadas a cada tick a partir do esqueleto do arquétipo) + um mixin no Fabric para a busca por ID e o pick do jogador. O Ice and Fire mostra o padrão: um `EntityDragonPart` por cabeça, pescoço, asas e 4 segmentos de cauda, cada um com `damageMultiplier` (cabeça 1,5, cauda 1,0, asa 0,5), e o `hurt()` repassado ao pai. **Proposta:** usar partes só a partir de ~8 m. Posição calculada no servidor por uma tabela de pontos que o pipeline exporta (pescoço, cabeça e cauda na pose idle, com uma oscilação aproximada), sem depender do cliente. Ponto fraco na cabeça (×1,5) e cauda como arma do anquilossauro ou do saurópode.

**Colisão com o terreno.** A AABB vanilla é quadrada em XZ, então dar 26 de largura a um bicho de 26 m é absurdo. Hoje o Terrassic usa a largura do corpo (6 × 10 no Argentinosaurus), o que está correto. Pescoço e cauda atravessam blocos. Mitigação barata: levantar a ponta da cauda e o pescoço quando um raio para baixo encontra um bloco (o mesmo princípio do LegSolver).

**Pathfinding.** O `NodeEvaluator` vanilla usa `entityWidth = floor(largura + 1)` e testa uma coluna desse tamanho por nó, então o custo cresce com a largura ao quadrado e o bicho trava em floresta. Precedentes:
- O **Ravager** quebra folhas quando tem colisão horizontal (laço com `LeavesBlock` em `aiStep`, respeitando `mobGriefing`).
- O `MMPathNavigateGround` (Mowzie's/pau101), base da `AzureNavigation`, varre a caixa inteira e pega atalhos.
- **Fazer:** caixa de navegação ≤ 3 blocos para os gigantes, quebra de folhas e plantas baixas (regra do mundo), e manada guiada por um líder com os seguidores em "boids", para não rodar A* em 15 saurópodes.

**Culling e distância de renderização.** O vanilla renderiza até `tamanhoMédioDaAABB × 64 × entityDistanceScaling` (`Entity.shouldRenderAtSqrDistance`), limitado pelo `clientTrackingRange` em chunks (o Ender Dragon usa 10). O Terrassic já infla `getBoundingBoxForCulling()` pelo excesso do modelo, o que está correto. Faltam duas coisas:
- `clientTrackingRange` de 10 a 12 para animais acima de ~10 m, para o gigante aparecer no horizonte.
- Testar com o **Entity Culling** (traçado assíncrono de visibilidade, [README](https://github.com/tr7zw/EntityCulling)). Modelo muito maior que a hitbox some quando a caixa fica atrás de um morro, então precisa entrar na whitelist ou usar a caixa de culling correta. O próprio AzureLib documenta esse problema.

**Câmera ao montar.** No 1.20.1, um mixin em `Camera` escala a distância da terceira pessoa com a altura do animal (ex.: 4 + 0,6 × altura). A partir do 1.21.6 existe o atributo `camera_distance` (criado com o Happy Ghast) **(verificar no porte)**. A posição do cavaleiro deve seguir o osso `saddle`: no GeckoLib 4, `GeoBone.getWorldPosition()` com `setTrackingMatrices(true)`; no 5, `BonePositionListener`. Assim o cavaleiro balança com o passo. No servidor, basta uma aproximação.

---

## 4. Performance de renderização em escala

**Custo do GeckoLib.** Por entidade e por frame: avaliar os controladores (keyframes ou Molang por osso) e depois transformar **24 vértices por cubo** na CPU. O código do 4.8.4 cria `new Matrix4f` por cubo e `new Vector3f` por face. O Sodium tem um caminho rápido só para `ModelPart` vanilla (`EntityRenderer.renderCuboid`). Com Iris e shaders que ligam `shadowEntities=true` ([doc do OptiFine](https://github.com/sp614x/optifine/blob/master/OptiFineDoc/doc/shaders.properties)), cada entidade é desenhada **duas vezes** (sombra + gbuffer). Entidades fora do frustum não animam no cliente, porque o GeckoLib anima durante a renderização.

**Conta de ordem de grandeza (estimativa):**
- Um zumbi vanilla tem ~12 cubos, cerca de 290 vértices.
- A mediana do Terrassic é ~52 cubos (1.250 vértices). O T. rex v3 tem 139 cubos (3.340 vértices).
- 150 dinossauros na tela × 52 cubos dão ~190 mil vértices/frame. Com sombra de shader, ~375 mil, ou seja, **5 a 10 zumbis por dinossauro**.
- Isso é viável, desde que os modelos de 130+ cubos sejam poucos e haja LOD.

**Medidas, por impacto:**
1. **Orçamento por classe de tamanho** (tabela da seção 7) e cubos contados no CI.
2. **Remover faces escondidas.** Box UV desenha as 6 faces sempre. Com UV por face, o `buried.py` (que já acha cubos enterrados) pode ser estendido para **faces** e desligá-las (o GeckoLib pula face nula). O Blockbench tem o plugin "Optimize" com esse fim. Ganho estimado: 15 a 30 % dos quads.
3. **LOD gerado pelo pipeline.** `getModelResource()` pode trocar o `.geo.json` por distância, desde que os nomes dos ossos sejam compatíveis.
   - **LOD0**, até ~32 m: tudo, com IK e física.
   - **LOD1**, de 32 a 96 m: sem as tags `tooth_cube`, `claw`, `scute`, `rugose` e `boss`, com cubos fundidos, ≤ 35 % dos cubos e sem procedural (`query.distance_from_camera`).
   - **LOD2**, além de 96 m (só para os gigantes que aparecem longe): ≤ 12 cubos, só idle e walk.
   - Opcional: assar o LOD2 como `ModelPart` vanilla para ganhar o caminho do Sodium.
4. **Reduzir a frequência da animação** no LOD1 e LOD2: reaproveitar o snapshot de ossos a cada 2 ou 3 frames (o `BoneSnapshots` do GeckoLib 5 facilita).
5. **Texturas.** Cada textura de entidade é um bind separado. O `MultiBufferSource` agrupa por `RenderType`, então machos de T. rex vão juntos. Textura de entidade não tem mipmap no vanilla **(pelo que sei)**, então textura densa em bicho distante cintila. É mais um motivo contra 66 px/m.
   - VRAM: 512² RGBA ≈ 1 MB. 200 espécies × 2 sexos × (1 + 2 morfos) × 256² ≈ 300 MB se todas carregassem **(estimativa)**. Como só carregam as vistas, uma sessão típica com 40 a 60 espécies fica em ~60 a 90 MB.
6. **Emissivos.** No 1.20.1, use `AutoGlowingGeoLayer` (um passe extra, ou seja, o custo de mais uma renderização da entidade) só onde importa (olhos bioluminescentes, por exemplo). No Forge com Oculus, o próprio GeckoLib avisa sobre a necessidade de um mod de compatibilidade. No GeckoLib 5, prefira `shouldRespectWorldLighting`, que fica melhor com shaders.

---

## 5. Direção de arte

**5.1 Densidade de texel: o problema nº 1.** Medido no repositório (`16 / scale`, px por metro no jogo):

| Faixa | Exemplos |
|---|---|
| 4,9 a 5,9 px/m | Brachiosaurus, Argentinosaurus, Alamosaurus, Dreadnoughtus (pixels 3× maiores que os do vanilla) |
| 7 a 12 px/m | a maioria dos grandes: Spinosaurus 8,6; Triceratops 9,8; Giganotosaurus 9,1 |
| 14 a 20 px/m | T. rex v3 15,7 (o ideal); Pachycephalosaurus 16,7; Pteranodon 20 |
| 25 a 67 px/m | Velociraptor 33; Compsognathus 52; Didelphodon 61; Ichthyornis 65; Mononykus 67 (pixels 2 a 4× menores que os do vanilla, ou seja, "mixels") |

O vanilla desenha quase tudo a 16 px/bloco. O Ender Dragon é renderizado em escala 1, com o corpo 24 × 24 × 64 px. As exceções são poucas e deliberadas (Ghast em escala 4,5, Gigante em 6). **Regra proposta:**
- **16 px/m como padrão** até ~15 m, como o T. rex v3 já faz.
- **Piso de 8 px/m** acima de 15 m (saurópodes e mosassauro), com textura de 512².
- **Teto de 32 px/m** só abaixo de 1 m (Ichthyornis, por exemplo).
- O pipeline passa a autorar cada espécie em `render_scale` próximo de 1 e reprova no CI quem sair da faixa.
- O filhote resolve isso com geometria própria (5.4). Não basta escalar o adulto: o filhote de Argentinosaurus (escala 0,08) vai a ~65 px/m.

**5.2 Estilo de pixel que conversa com o vanilla.** As regras que o `docs/TEXTURAS_ERA.md` já definiu para blocos valem para a pele das criaturas:
- Aglomerados de 2 a 6 px em vez de ruído por pixel.
- Rampa de 5 a 8 tons por material, com sombra mais fria e luz mais quente.
- Pouca oclusão pintada, porque o jogo já sombreia as faces.
- Contraste e brilho dentro da faixa dos mobs vanilla. Dá para medir os mobs de 1.20.1 como foi feito com os blocos: Ravager e Warden (128²) e Sniffer.

Por que os estilos de referência ficam coerentes:
- **Alex's Mobs**: silhuetas exageradas e legíveis, paleta curta e detalhe só no rosto.
- **Cobblemon**: um guia de estilo único, poses e quirks padronizados e revisão central.

**5.3 Rigor paleontológico (o diferencial "melhor já visto").**
- **Lábios** nos terópodes ([Cullen et al. 2023, Science](https://www.science.org/doi/10.1126/science.abo7877)). Já está feito no T. rex.
- **Penas**:
  - Dromeossaurídeos com penas de pena verdadeira (Velociraptor tem botões de pena na ulna, [Turner et al. 2007](https://www.science.org/doi/10.1126/science.1145076)).
  - Tiranossauroides basais emplumados ([Yutyrannus, Xu et al. 2012](https://www.nature.com/articles/nature10906)).
  - Filamentos já em ornitísquios ([Kulindadromeus, Godefroit et al. 2014](https://www.science.org/doi/10.1126/science.1253351)).
  - O T. rex adulto tem escamas nas áreas conhecidas ([Bell et al. 2017](https://royalsocietypublishing.org/doi/10.1098/rsbl.2017.0092)).
  - Em cubo, a técnica certa é a **franja**: planos de espessura zero com recorte alfa (`entityCutoutNoCull`) ao longo do pescoço, dos braços e da cauda, como as asas da Abelha e do Vex. Dão silhueta fofa por 2 quads cada.
- **Contrassombreamento** como padrão de cor (dorso escuro, ventre claro), com evidência fóssil em [Psittacosaurus](https://www.cell.com/current-biology/fulltext/S0960-9822(16)30672-8), [Borealopelta](https://www.cell.com/current-biology/fulltext/S0960-9822(17)30853-9) e [Sinosauropteryx](https://www.cell.com/current-biology/fulltext/S0960-9822(17)31209-5) (cauda listrada e máscara no olho).
- **Postura**:
  - Mãos de terópode com as palmas voltadas uma para a outra, nunca "de coelho".
  - Pescoço de saurópode erguido acima da horizontal ([Taylor, Wedel & Naish 2009](https://www.app.pan.pl/article/item/app54-213.html)).
  - Cauda sem arrastar no chão.
  - Spinosaurus com a questão aquática em aberto: mostrar a cauda-remo ([Ibrahim et al. 2020](https://www.nature.com/articles/s41586-020-2190-3)) e o comportamento de vadear ([Sereno et al. 2022](https://elifesciences.org/articles/80092)).
- **Fugir dos designs de Jurassic Park** (gola do Dilophosaurus, raptor gigante e pelado), por precisão e por marca registrada.
- **Esqueletos de referência** (Scott Hartman, GDI) servem para **medir** proporções, não para copiar contorno. Anote a fonte em `docs/TAMANHOS.md`, como a regra atual já pede.

**5.4 Filhotes.** Cabeça relativamente maior (1,4 a 1,8×), olho grande, focinho curto, e pernas longas nos terópodes (juvenis de tiranossaurídeos eram esguios e corredores). O ponto mais importante: **estruturas de exibição mudam com a idade**. Chifres do Triceratops juvenil curvados para trás (Horner & Goodwin 2006), crista ausente ou pequena em lambeossaurinos jovens (Dodson 1975), domo dos paquicefalossauros crescendo (Horner & Goodwin 2009). **Fazer:** um parâmetro `ontogeny` de 0 a 1 em cada ficha de espécie, que o arquétipo usa para gerar `<especie>_juvenile.geo.json` com o mesmo rig e as mesmas animações. Isso também resolve a densidade de texel dos filhotes. Padrão juvenil com manchas é especulativo (analogia com crocodilianos e filhotes de ratita) e deve ser marcado assim no bestiário.

**5.5 Dimorfismo sexual e morfos.** A evidência anatômica de dimorfismo em dinossauros é fraca na maioria dos casos (revisão de Mallon 2017, *Paleobiology*). **Fazer:** a diferença entre os sexos fica na **cor** (macho com estruturas de exibição mais saturadas, fêmea mais críptica), tamanho no máximo 5 a 10 % diferente, e osso `male_display` só onde for defensável. Tudo marcado como especulativo. Para os morfos, **assar no build** 2 ou 3 variantes de paleta por espécie, mais um morfo raro (leucístico ou melânico, ~1/500, um "shiny" do Terrassic). Isso é melhor que tingir camadas em tempo real, porque cada camada extra é outra renderização inteira do modelo.

---

## 6. Pipeline em escala

**O que o Terrassic já tem e quase ninguém tem:** geração determinística (Blockbench headless ou `pybench.py`, com `checks.py` provando igualdade), prévias e GIFs, `posecheck.py`/`floating.py`/`buried.py`, arquétipos com ficha curta e textura pintada em 3D. Para 200+ espécies, é o caminho certo.

**Riscos e mudanças:**
1. **O gerador sobrescreve a edição manual.** Isso impede um artista de refinar um modelo. A proposta é uma **camada de override** `species/overrides/<especie>.json`, com chave pelo nome estável do cubo ou osso (posição, tamanho, inflate, UV, pixels de textura por região). O gerador reaplica a camada depois de gerar, e um script extrai o diff de um `.bbmodel` editado. Assim artista e código convivem.
2. **Contrato de rig por arquétipo:** nomes de ossos obrigatórios (`root`, `body`, `neck1..n`, `head`, `skull`, `jaw`, `tail1..n`, pernas `*_thigh/_shin/_foot`, `saddle`, `male_display`...), pivôs, orientação (−Z), e lista de animações obrigatórias e opcionais. Esse contrato alimenta a camada procedural (olhar, cauda, IK) sem código por espécie.
3. **Animações como dados, ao estilo dos posers do Cobblemon:** um `poser` por arquétipo gerado pelo pipeline (estados, condições, transição, ociosos e pesos), lido por um único sistema Java. Hoje cada estado está fixo em `DinosaurEntity.movementAnimation`.
4. **Cobertura de animações.** Medido nos 53 modelos: todos têm idle, walk, run, attack, sit, knocked_out, wake, eat, beg e tame. Só 26 têm `graze`, 11 têm `roar` e 5 têm `call`. **Ninguém tem** `sleep` (usa sit), `hatch`, `swim` para os terrestres, `hurt`, `death`, `turn`, `drink` nem ociosos variantes. Conferir no CI contra o contrato.
5. **Validação nova:**
   - Densidade de texel.
   - Orçamento de cubos, ossos e textura.
   - **Escorregamento do pé**: velocidade do pé de apoio no mundo ≈ 0 com o corpo andando a `stride_m/cycle_s`; reprova acima de ~5 %.
   - Simetria.
   - UV sobreposto e % de textura vazia.
   - Paleta (tons por material, brilho e contraste contra mobs vanilla).
   - Silhueta contra um esqueleto de referência.
   - Turntable de 8 ângulos e folha de comparação com jogador e vaca na mesma escala.
   - Teste de regressão por imagem (diff de prévias com limiar) no CI.
6. **Versionamento:** `.bbmodel`, PNG e JSON gerados ficam no git (são pequenos). `model_version` por espécie no `build_report.json`, changelog de arte e tag de release. O Blockbench está no 5.2.2 (out/2026). O plugin GeckoLib para Blockbench 5 é o "GeckoLib Models & Animations" 4.2.5 (o "Animation Utils" foi substituído).
7. **Contribuição da comunidade:**
   - Comece por **texturas e morfos**, que são mais fáceis de revisar. Modelos inteiros vêm depois.
   - Entregar um **template `.bbmodel` por arquétipo** (rig travado e UV pronto), um guia de estilo com paletas, e um **plugin próprio do Blockbench** ("Terrassic Check") que roda as mesmas checagens do CI dentro do editor.
   - Pull request com CI verde + revisão de paleoarte, e créditos no bestiário.
   - Licença clara (acordo de contribuição cedendo os direitos sob a licença do mod) e proibição de decalque de paleoarte com direitos autorais.
   - O plugin "glTF to Minecraft" (converte glTF em cubos) pode servir de esboço a partir de escaneamentos com licença aberta, mas só como referência.

---

## 7. Recomendações para o Terrassic, por impacto

1. **Densidade de texel unificada** (16 px/m padrão, piso de 8, teto de 32) e re-autoria dos extremos: saurópodes, mosassauro e os pequenos abaixo de 2 m. *É o que mais destoa visualmente hoje.*
2. **Passo casado com a velocidade:** `stride_m` vindo do pipeline + controlador que acumula fase + passos com som e partícula. *Acaba com o pé deslizando em 53 espécies de uma vez.*
3. **Camada procedural compartilhada:** olhar no pescoço, ChainBuffer na cauda e no pescoço, LegSolver bípede e quadrúpede, respiração e ociosos aleatórios, ligada pelo contrato de rig e escrita como função pura (pronta para o GeckoLib 5).
4. **Animações parciais e aditivas:** roar, eat, call e attack só no corpo de cima, para tocar andando. Mais as que faltam: sleep, hatch, swim, hurt, death e turn.
5. **Filhote com geometria própria** (`ontogeny`), juvenis com proporções e estruturas corretas.
6. **Multiparte para animais acima de 8 m**, calculada no servidor, com mixin no Fabric. `clientTrackingRange` de 10 a 12 e teste com Entity Culling.
7. **LOD0/1/2 gerados por tag**, remoção de faces escondidas e orçamento no CI.
8. **Override de arte + plugin "Terrassic Check" + templates**, abrindo para a comunidade.
9. **Morfos assados e regras de cor** (contrassombreamento, macho mais saturado, morfo raro).
10. **Navegação para gigantes:** caixa de navegação ≤ 3, quebra de folhas, manada com líder.

### Orçamento por classe de tamanho (proposta; os números são estimativa calibrada no repositório)

| Classe | Exemplos | Cubos LOD0 | Ossos | Textura (por sexo) | px/m | LOD1 / LOD2 |
|---|---|---|---|---|---|---|
| Minúsculo (< 1 m) | Ichthyornis, Didelphodon | ≤ 35 | ≤ 22 | 64 × 64 | 16 a 32 | não precisa |
| Pequeno (1 a 3 m) | Velociraptor, Compsognathus, Protoceratops | ≤ 50 | ≤ 26 | 64 × 64 a 128 × 128 | 16 | ≤ 20 / não |
| Médio (3 a 8 m) | Dilophosaurus, Stegosaurus, Triceratops | ≤ 80 | ≤ 32 | 128 × 128 a 256 × 128 | 16 | ≤ 28 / não |
| Grande (8 a 15 m) | T. rex, Spinosaurus, Edmontosaurus | ≤ 140 | ≤ 40 | 256 × 256 a 256 × 512 | 16 | ≤ 45 / ≤ 12 |
| Colossal (> 15 m) | Argentinosaurus, Mosasaurus | ≤ 150 | ≤ 45 | 512 × 512 | ≥ 8 | ≤ 50 / ≤ 12 |

Alvo de cena **(estimativa)**: ≤ 400 mil vértices de entidades por frame no pior caso, com shaders, num servidor cheio. Medir com o Spark e o perfilador F3 numa cena de teste com 150 animais.

### Checklist de qualidade do modelo (toda espécie passa antes de entrar)

**Anatomia e fonte**
- [ ] Tamanho real anotado em `docs/TAMANHOS.md`. Proporções do crânio, do pescoço, da cauda e dos membros conferidas com um esqueleto de referência (silhueta lado a lado).
- [ ] Postura correta (mãos, pescoço, cauda fora do chão), tegumento justificado (escama, filamento, pena) e lábios onde couber.
- [ ] Nada de design de Jurassic Park. A especulação está marcada no bestiário.

**Geometria e textura**
- [ ] Densidade de texel dentro da faixa da classe. Cubos, ossos e textura dentro do orçamento.
- [ ] Nenhuma peça solta (`floating.py`) ou enterrada (`buried.py`). Faces escondidas removidas.
- [ ] Rampa de 5 a 8 tons por material, aglomerados sem ruído por pixel, contrassombreamento, e brilho e contraste dentro da faixa vanilla.
- [ ] Macho e fêmea (diferença principalmente de cor), 2 a 3 morfos + 1 raro, e filhote com geometria própria.
- [ ] Silhueta reconhecível a 32 m (testado no LOD1) e rosto legível a 8 m (olho com brilho, pálpebra).

**Rig e animação**
- [ ] Rig segue o contrato do arquétipo. O `saddle` alinha o cavaleiro, e as partes multiparte estão definidas se o animal tiver mais de 8 m.
- [ ] Animações obrigatórias completas: idle (com respiração), 2 ou mais ociosos variantes, walk, run, turn, sit_down/sit/stand_up, sleep, eat, drink, graze ou hunt, attack, roar ou call (só corpo de cima), hurt, death, knockout/knocked_out/wake, tame, beg, hatch, e swim, fly ou glide quando couber.
- [ ] Pé sem escorregar (métrica < 5 %), `stride_m` exportado e passada com som e partícula.
- [ ] Nenhuma pose afunda no chão ou flutua (`posecheck.py`: ponto mais baixo = 0 nas poses de chão).
- [ ] Transições sem estalo (blend proporcional à massa) e animações parciais tocando por cima do walk.

**Prova e regressão**
- [ ] Prévias: turntable de 8 ângulos, GIF de cada animação e folha de escala com jogador e vaca.
- [ ] Diff de imagem contra a versão anterior aprovado.
- [ ] Teste no jogo: Sodium + Iris com shader que liga sombra de entidade, Entity Culling ligado, 20 indivíduos na tela e em encosta (IK).
