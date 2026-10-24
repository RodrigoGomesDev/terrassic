# Terrassic: texturas, filtro e pacote por era

> **Status:** desenho técnico (24/10/2026) + **lote 1 do pacote do Cretáceo em produção** (`tools/texpack/`).
> Pedido do Rodrigo: "os blocos estão muito simplórios, pixel art realmente ruim, os blocos do Minecraft são muito mais polidos";
> "quero texturas/shaders deixando mais old"; "texturepack mudando de acordo com a era"; "tudo original, com mais carinho".
> Vale junto com `ESCOPO.md` (pacote de texturas embutido e opcional) e `ROADMAP.md` T3.3 e T3.4.

**Como li "mais old":** envelhecido e primitivo, não "Minecraft antigo". Pedra gasta e com veios, terra com raízes e
seixos, madeira rachada e escurecida, cores de terra, luz quente de fim de tarde. Tudo na mesma resolução (16x16) e com o
mesmo contraste do vanilla, para os blocos do mod e os do vanilla parecerem do mesmo jogo.

---

## 1. Por que os blocos atuais parecem simplórios

Comparando os blocos do mod com os do vanilla, os problemas são sempre os mesmos:

| Problema nos nossos | O que o vanilla faz |
|---|---|
| Ruído pixel a pixel (cada pixel sorteado), que vira "chuvisco" | **Aglomerados** de 2 a 6 pixels com forma; quase nenhum pixel solto |
| Muitas cores parecidas, ou 2 cores chapadas | **Rampa de 5 a 8 tons** por material, com passos visíveis |
| Sombra só mais escura | **Sombra muda de cor** (mais fria e saturada), luz mais quente: dá volume |
| Sem relevo: tudo plano | Luz sempre de cima à esquerda: cada pedra, tábua ou torrão tem borda clara em cima e escura embaixo |
| Repetição visível quando o bloco se repete | Textura que emenda sem costura + **variantes sorteadas** (rotação e modelos alternativos no blockstate) |
| Desenho "de ícone" (árvore, crânio) dentro de um bloco cheio | Bloco cheio é material, não desenho |

## 2. O motor novo de texturas (`tools/texpack/`)

Um gerador novo, independente do `tools/spritegen/blocks.py`, escrito para resolver a tabela acima. Tudo é autoral e
procedural: nenhum pixel vem de textura de terceiros (nem do vanilla, que só serve de régua de contraste no jogo).

- `tex.py`: a biblioteca. Ruído que emenda nas bordas (o bloco 16x16 é um toro), células de Voronoi que emendam,
  mapa de altura com luz de cima à esquerda, **rampas de cor com desvio de matiz** (sombra fria, luz quente),
  quantização para a rampa, limpeza de pixels soltos (filtro de maioria), contorno de formas, e conferência
  automática de que a textura emenda.
- `palettes.py`: as rampas de cada material, por era.
- `cretaceo.py`: as receitas das texturas do Cretáceo Superior (pedra, pedregulho, terra, grama, cascalho, areia...).
- `preview.py`: folha de prévia (cada textura ampliada, em mosaico 3x3 e num diorama de cubos em perspectiva).
- `build.py`: escreve o pacote embutido em `common/src/main/resources/resourcepacks/<era>/` e a prévia em `art/texpack/`.

Regras de qualidade que o gerador confere sozinho (falha se não passar):
1. Emenda nas 4 bordas (diferença entre a borda e a vizinha do outro lado igual à do meio da textura).
2. No máximo 8 tons por textura opaca (fora a grama, que é cinza e recebe a cor do bioma).
3. No máximo 3% de pixels isolados (pixel sem nenhum vizinho do mesmo tom).
4. Brilho médio e contraste dentro da faixa do material equivalente no vanilla (tabela em `palettes.py`).

**Motor v2 (24/10, depois de o Rodrigo achar a v1 "bem ruim").** O Mac mediu as 927 texturas de bloco do vanilla
1.20.1 (só números: cores, brilho, contraste, salto entre vizinhos). A v1 estava escura demais, com até o dobro do
contraste do vanilla, pedra cinza puxada para o marrom e ruído espalhado por todo o bloco. A v2 desenha em três passos:
uma base calma de um tom principal com manchas grandes; detalhes desenhados (degraus, pintas, seixos, folhas, raízes)
espalhados por ruído azul, como se fossem postos à mão; e a paleta ajustada para o brilho e o contraste do bloco vanilla
que ela troca (`targets.py`), com o matiz da era. O `build.py` recusa a textura que sair da faixa.

Depois que o Rodrigo aprovar o visual do lote 1, o mesmo motor serve para **refazer os 528 blocos do mod** (junto com a
frente de blocos), para que blocos do mod e do pacote tenham a mesma mão.

## 3. Como funciona no jogo: quatro camadas

### Camada A · Pacote embutido por era (texturas do vanilla trocadas)
Um **pacote de recursos dentro do jar do mod**, que aparece no menu Pacotes de Recursos já ligado e que o jogador pode
desligar. O Cretáceo Superior é a era do Overworld, então **o pacote do Cretáceo é o pacote padrão do mod**.

- Pasta no jar: `resourcepacks/cretaceo/` com `pack.mcmeta` (formato 15, o da 1.20.1), `pack.png` e
  `assets/minecraft/textures/block/*.png`. O nome e a descrição saem do lang do mod (`pack.terrassic.cretaceo`).
- **Fabric:** `ResourceManagerHelper.registerBuiltinResourcePack(id, container, nome, ResourcePackActivationType.DEFAULT_ENABLED)`
  (Fabric API, módulo resource-loader). Ligado na primeira vez; se o jogador desligar, fica desligado.
- **Forge:** `AddPackFindersEvent` (tipo `CLIENT_RESOURCES`) cria o pacote com `Pack.readMetaAndCreate` e
  `PathPackResources` apontando para `resourcepacks/cretaceo` dentro do jar. O Forge 1.20.1 não tem "ligado por padrão";
  o mod liga o pacote **uma vez só**, na primeira execução, pondo o id dele na lista de pacotes do `options.txt`
  (marcado em `config/terrassic-client.json`, para não religar se o jogador desligar).
- **Variantes sem costura:** o pacote também troca os `blockstates` de pedra, terra, cascalho e areia para sortear
  rotações e 2 a 4 modelos alternativos (como o vanilla já faz com a pedra lisa), um deles raro com um detalhe
  (concha fóssil na pedra, raiz na terra, osso pequeno no cascalho).
- Só textura e modelo: nada de código no pacote, então ele funciona com Sodium, Embeddium, Iris e Oculus.

### Camada B · Cor e atmosfera por bioma e por dimensão (sem recarregar nada)
O que muda de cor sem trocar textura vem dos **efeitos de bioma** (JSON do worldgen, já usados pelos 11 biomas da branch
v0.8): `sky_color`, `fog_color`, `water_color`, `water_fog_color`, `grass_color`, `foliage_color`, partículas, som de
ambiente e música. A grama e as folhas do pacote são cinza justamente para receber essa cor. Cada era futura é uma
dimensão própria com os seus biomas, então a cor muda sozinha ao saltar.

O céu de cada era (sol mais quente, Fenda no céu, meteoros, cinza) usa `DimensionSpecialEffects` próprios:
Fabric `DimensionRenderingRegistry`, Forge `RegisterDimensionSpecialEffectsEvent`.

### Camada C · Textura por era sem recarregar (v2.0, quando existir a segunda era)
O problema: pacotes de recursos são do jogo inteiro, não de uma dimensão. Recarregar o pacote ao saltar funciona, mas
leva de 10 a 60 segundos com muitos mods.

A solução: **todas as eras carregadas juntas, e o modelo escolhe na hora de montar o chunk.**
1. As texturas de cada era ficam no atlas de blocos com nome próprio (`terrassic:block/era/jurassico/stone`...).
2. Para uma lista curta de blocos do vanilla que aparecem em todas as eras (pedra, pedregulho, terra, cascalho, areia,
   argila, arenito), o mod embrulha o modelo assado do vanilla num `EraBakedModel`: um `BakedModel` comum que, em
   `getQuads`, devolve as faces do modelo da era da dimensão atual.
3. A era atual é uma variável lida pelas threads que montam os chunks; ela muda quando o cliente troca de dimensão, e
   trocar de dimensão já remonta todos os chunks. Sem recarregar recursos, sem tela de espera.
4. Registro: Fabric `ModelLoadingPlugin` (carregar os modelos extras e `modifyModelAfterBake`); Forge
   `ModelEvent.RegisterAdditional` + `ModelEvent.ModifyBakingResult`.
5. Por ser um `BakedModel` simples (não usa a API de renderização do Fabric), o Sodium e o Embeddium montam ele sem
   precisar do Indium, e o Iris e o Oculus também.

Plano B, se a camada C der problema com algum mod: recarregar o pacote da era **durante a cena do salto** no Altar,
que já é uma tela cheia de luz âmbar de alguns segundos.

### Camada D · Filtro da era (o "shader" sem depender de shader)
Um efeito de pós-processamento do próprio Minecraft (`PostChain`, o mesmo sistema da visão da aranha e do creeper),
desenhado pelo mod (`common/.../client/EraFilter.java`) no fim do mundo, antes da mão e do HUD. **Pronto (TX5).**
- **Vem dentro do pacote da era:** `assets/terrassic/shaders/post/era_cretaceo.json` (os números da era) e um único
  programa GLSL para todas as eras, `assets/minecraft/shaders/program/terrassic_era_grade.*` (o vanilla só procura
  programas no espaço `minecraft`). Desligar o pacote desliga o filtro. Gerado por `tools/texpack/filters.py`.
- **Gradação do Cretáceo:** 8% menos saturação, luz quente (vermelho ×1,035, azul ×0,95), pretos um pouco
  levantados e quentes (ar de foto antiga) e vinheta suave. Prévia: `art/texpack/previews/cretaceo_filtro.png`.
- **Config** em `config/terrassic-packs.json`: `"era_filter": true/false` e `"era_filter_strength"` (0 a 1,
  padrão 0,6). O arquivo é criado com esses valores na primeira vez.
- Ganchos: Fabric `WorldRenderEvents.END` (entrypoint `client`), Forge `RenderLevelStageEvent` na fase
  `AFTER_WEATHER`. Recarregar pacotes (F3+T) refaz o filtro.
- **Desliga sozinho quando um shaderpack do Iris ou do Oculus está ativo** (consulta a API do Iris por reflexão, sem
  depender dele). Assim nunca briga com shaders de terceiros.
- Grão de filme ficou de fora: em movimento parece sujeira na tela. Pode voltar como opção.
- Com Sodium/Embeddium funciona normal (eles não mexem no pós-processamento).

Para quem usa shaders: um **shaderpack próprio "Terrassic Âmbar"** para Iris/Oculus pode vir depois, como download
separado, usando as pastas por dimensão do Iris para ter um visual por era. Não é necessário para o mod.

### Interface (menus, inventário, botões)
Na 1.20.1 o vanilla ainda usa `gui/widgets.png`, `gui/container/*.png` e `gui/options_background.png` (o fundo de terra
dos menus). O pacote do Cretáceo troca esses arquivos por couro, osso e pedra (lote 4). Na 1.21 os botões viram
sprites separados: o gerador já escreve as peças separadas para o porte.

## 4. O visual de cada era

| Era | Clima da imagem | Pedra | Solo | Céu e névoa | Filtro |
|---|---|---|---|---|---|
| **Cretáceo Superior** (Overworld) | Quente, fim de tarde, verde-oliva e ocre | Calcário acinzentado-bege com veios e conchinhas raras | Terra marrom-avermelhada com raízes e seixos; grama rala | Azul quente, névoa dourada no horizonte | Levemente quente, saturação -5%, vinheta leve |
| **Penas e Cinzas** (Cret. Inferior) | Frio e cinzento, cinza vulcânica | Basalto escuro e calcário laminado | Terra escura com cinza | Céu leitoso, névoa cinza | Frio, saturação -20%, grão mais forte |
| **Jurássico** | Úmido, verde fundo | Calcário claro de Solnhofen | Terra úmida, musgo | Céu azul-esverdeado, névoa baixa | Verde, contraste suave |
| **Triássico** | Seco e quente, vermelho | Arenito vermelho em camadas | Areia e terra vermelha | Céu amarelado, ar tremendo de calor | Quente forte, saturação +10% |
| **Era do Gelo** | Frio e limpo | Granito cinza-azulado | Terra congelada, neve | Branco-azulado | Frio, saturação -25%, mais claro |

## 5. Lotes do pacote do Cretáceo

| Lote | O que entra | Estado |
|---|---|---|
| TX1 | **Terreno:** pedra (+3 variantes), pedregulho, pedregulho com musgo, terra (+2), terra grossa, grama (topo, lado, lado com neve), podzol, cascalho (+1), areia (+1), arenito (topo, lado, base, entalhado, liso), argila, lama, terra enraizada. Mais o registro do pacote no Fabric e no Forge | ✓ |
| TX2 | **Madeiras** das 8 árvores (casca própria de cada uma, anéis fora do centro com rachadura, descascado, tábuas lascadas com cavilha) com variantes raras de tronco (resina âmbar no abeto, líquen no carvalho, musgo na selva); **folhas** por formato de folha da espécie; **plantas** do Cretáceo (o capim vira cavalinhas com samambaias baixas, a samambaia grande vira samambaia-arborescente, o cipó vira samambaia trepadeira); **bancada** de tronco com ferramentas de pedra, sílex e osso; **fornalha** de pedras e barro com fuligem e brasas; **tocha** de resina. Baú no lote 3; a fogueira fica para depois (o desenho depende do mapeamento do modelo) | ✓ |
| TX3 | **Rochas do vanilla** desenhadas pelo que são feitas (granito e diorito em cristais entrelaçados, andesito fino com fenocristais, tufo com lapilli, ardósia em lâminas, calcita com clivagem) e os **16 minérios** em veios naturais sobre a pedra e a ardósia do próprio pacote: carvão em camada, limonita enferrujada, malaquita com cobre nativo, ouro em veio de quartzo, cinábrio, lazurita com pirita, diamante em bolsão de kimberlito, esmeralda em veio de calcita | ✓ |
| TX3b | **Construção e chão:** tijolos de pedra em fiadas lavradas à mão (com musgo, rachados e um entalhado com amonite), tijolos queimados em argamassa de cal, bloco de musgo, terra arada (seca e molhada), caminho batido com uma pegada de terópode, fardo de palha amarrado, neve; a cana-de-açúcar vira cavalinha gigante e a vitória-régia ganha folha entalhada com nervuras | ✓ |
| TX3c | **Flores:** as 12 flores pequenas em formas das primeiras plantas com flor (taça de tépalas como a magnólia, flor aberta, sininhos, umbela, estrela, tulipa fechada), cada uma mantendo a cor que dá o corante | ✓ |
| TX4 | Interface: botões, inventário, baús, fornalha, fundo dos menus, barra de itens, em couro, osso e pedra | ○ |
| TX5 | Filtro da era (camada D) | ✓ |
| TX6 | Refazer os blocos do mod com o motor novo: a thread de blocos usa `tools/texpack/api.py` e `materials.py` (decisão do Rodrigo, 24/10) | 🔄 |
| TX7 | Camada C (troca por era sem recarregar) e os pacotes das outras eras | ○ (v2.0) |

## 6. Testes no jogo (só um humano consegue)

- O pacote "Terrassic: Cretáceo Superior" aparece **ligado** no menu Pacotes de Recursos no Fabric e no Forge, e
  desligar faz o vanilla voltar.
- Ao lado dos blocos vanilla que o pacote não troca, nada parece fora do lugar (contraste e brilho).
- Pedra, terra, cascalho e areia em área grande não mostram repetição.
- A grama recebe a cor dos biomas (planície, pântano, deserto do vanilla e os biomas do Cretáceo da v0.8).
- Funciona com Sodium (Fabric) e Embeddium (Forge), com e sem shaderpack do Iris/Oculus.
- Lote 2: troncos em pé e deitados (eixos x, y, z) mostram de vez em quando a variante (resina no abeto, líquen no
  carvalho, musgo na selva) e o topo continua certo; folhas em gráficos "rápido" ficam escuras e cheias, sem
  buracos pretos estranhos; cavalinhas e samambaias recebem a cor do bioma; a tocha aparece certa no chão e na
  parede; a fornalha acesa mostra as brasas; a bancada lê como bancada (grade no topo, ferramentas nos lados).
- Lote 3: numa caverna, cada minério se reconhece de longe pela cor do mineral; a ardósia deitada e em pé fica
  coerente; granito, diorito e andesito ao lado da pedra do pacote não destoam; o baú simples e o duplo fecham
  sem costura, a trava de osso fica na frente e o interior aparece ao abrir.
- Lote 3b: o caminho mostra as pegadas em sequência como uma trilha; a terra arada lê como sulcos, seca e
  molhada; a cana (cavalinha) e a vitória-régia recebem a cor do bioma.
- Filtro (TX5): no mundo a imagem fica levemente quente e com vinheta, a mão e o HUD não mudam; `"era_filter":
  false` em `config/terrassic-packs.json` (e F3+T ou reiniciar) desliga; força 0 e 1 mudam a intensidade; desligar
  o pacote no menu desliga o filtro; com shaderpack do Iris/Oculus o filtro não aparece; nada de tela preta ao
  redimensionar a janela, no F1, no modo espectador nem com gráficos "Fabuloso" (no Forge, em Fabuloso, a água e
  as partículas podem ficar fora do filtro: anotar se destoar).
