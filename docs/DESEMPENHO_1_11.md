# Desempenho e Jade na 1.11

Pedido de um jogador (repassado pelo Rodrigo): com 410 mods, o Spark mediu 3,7% de carga para o Terrassic contra 0,5%
de outro mod de dinossauros, com "todos os dinos num lugar, mais ou menos o mesmo número de criaturas"; e integração
com o Jade, com opção de desligar a barra de vida do mod.

## Como medir

Spark é mod de terceiro e não foi usado. A medida é o JFR do próprio JDK, gravado de dentro do cliente:

```sh
TERRASSIC_PERF=1 TERRASSIC_PERF_LABEL=depois caffeinate -dimsu ./gradlew :fabric:runClient
python3 -B tools/validation/perf_report.py fabric/run/perf/terrassic_perf_depois.jfr
```

`client/dev/PerfTest` cria um mundo Terrassic novo (semente 20261108), põe um jogador criativo voando sobre uma clareira
em mata de magnólias (260, 94, 20), espera 60 s para os chunks em volta terminarem de gerar, chama **2 de cada espécie
ativa** (25 terrestres e voadoras numa grade de 36 × 20 blocos, Mosassauro e Elasmossauro num tanque de 13 × 15),
espera 20 s e grava 60 s: amostra de execução a cada 10 ms em todas as threads, amostra de alocação, GC, tempo de CPU da
thread do servidor e da thread de render, ticks e quadros. Relatório em `fabric/run/perf/terrassic_perf_<rótulo>.txt`,
gravação em `.jfr`, foto da cena em `screenshots/perf_scene_<rótulo>.png`. Volume geral 0, sempre com `caffeinate -dimsu`.

Atribuição: uma amostra conta para o mod quando há código do Terrassic em qualquer quadro da pilha (classes
`com.terrassic.*` ou handlers de mixin `$terrassic$`), a mesma atribuição de "este mod está na pilha" que um
profiler de amostragem como o Spark faz. Isso inclui o código vanilla que roda **para** os nossos bichos (física,
colisão, A*), porque ele é chamado de dentro do `tick` deles. A medida em si (`client.dev`) fica de fora.
Custo do mod por tick = (CPU da thread do servidor na janela ÷ ticks) × fração das amostras com o mod.
O MSPT também sai no relatório, mas mistura geração de mundo, pausas de GC e espera; não serve de comparação.

O cenário é caótico de propósito (é o do jogador): os predadores caçam, há duelos, carcaças, fuga e manadas. Duas
rodadas do mesmo código variam bastante (12,6 e 19,9 ms antes da mudança), por isso cada lado foi rodado mais de uma vez.
Outros agentes rodavam clientes e scripts na mesma máquina (macOS ARM, 8 núcleos); a rodada marcada com * teve carga de
15 a 19 na máquina e não deve ser usada sozinha.

## Números

Mesmo cenário e harness (`76cb05db`); antes = código da `dcda48d5` com só o `PerfTest` novo; depois = `perf/jade-1.11`.

| Rodada | Bichos | CPU do servidor (ms/tick) | Com o mod (ms/tick) | % de 50 ms | A* (ms/tick) | Movimento vanilla (ms/tick) | Resto (ms/tick) | FPS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Antes A | 120 | 25.1 | 19.9 | 40% | 13.2 | 3.7 | 3.0 | 53 |
| Antes B | 121 | 19.2 | 12.6 | 25% | 5.6 | 3.8 | 3.2 | 56 |
| Depois A* | 121 | 24.4 | 14.5 | 29% | 3.4 | 5.9 | 5.2 | 31 |
| Depois B | 128 | 16.7 | 11.1 | 22% | 3.3 | 4.5 | 3.3 | 57 |
| Depois C* | 118 | 24.2 | 14.6 | 29% | 4.8 | 4.8 | 5.0 | 29 |
| Depois D* | 124 | 20.8 | 11.6 | 23% | 2.8 | 4.3 | 4.6 | 34 |

\* outro cliente de teste ou script pesado rodava na máquina (carga 13 a 35 em 8 núcleos, FPS caiu para 29-34): o
tempo de CPU por tick sobe sob contenção. Depois A e B: código até `d2929dd2`; C e D: final (`0c260389`, memória de
busca pela posição exata). Médias: antes 16,3 ms/tick; depois 11,1 ms (B, máquina livre) e 11,6-14,6 ms nas contidas.
Busca de caminho: 5,6-13,2 ms/tick antes, 2,8-4,8 depois.

Fração das amostras da thread de render com código do mod na pilha: 84% antes e 82-84% depois (é o
`DinosaurRenderer`, ou seja, o GeckoLib desenhando e animando os modelos).

Gráfico e fotos: `Claude outputs/desempenho-jade-1.11/img/` (`desempenho_antes_depois.png`).

### Onde o tempo estava (antes)

Servidor (fração das amostras da thread do servidor, rodadas A e B):

- **Busca de caminho (A*) 29-53%.** Vanilla, mas chamada pelos nossos objetivos e cara para bicho grande: a cada nó
  o `WalkNodeEvaluator` lê o tipo de **cada bloco que o corpo cobre** (e cada um olha os 26 vizinhos procurando fogo
  ou cacto). Um predador de 4 blocos de largura relia cada bloco dezenas de vezes por busca. Além disso, vários
  objetivos refaziam a busca **a cada tick** enquanto a navegação estava "feita" (o caminho que para antes do alvo
  termina na hora): `FleeHurtGoal` (oito direções e uma busca de 24-32 blocos por tick), `MigrateGoal`
  (até três tentativas por tick), `EatCarcassGoal`.
- **Movimento e colisão 14-18%.** `Entity.move` vanilla com caixas enormes: junta a forma de cada bloco dentro da
  caixa do bicho a cada tick (117 MB/s de `OffsetDoubleList` alocados só nisso).
- **Partes de acerto ~4%.** Toda chamada de `Level#getEntities` (colisão e empurrão de todas as entidades, a cada
  tick) percorria todos os donos de partes e lia a caixa de cada um; a posição das partes alocava seis vetores por
  parte por tick.
- O resto (objetivos, sono, manada, `EcoSpawner`, `AnimIndex`, sons, rede) somou menos de 5%; buscas de vizinhos
  com `getEntitiesOfClass` ficaram abaixo de 1%.

Cliente (thread de render): 46-52% vértices do GeckoLib, 26-28% processamento de animação do GeckoLib (busca linear
nos quadros-chave; as animações refeitas têm 25 a 80 quadros-chave por canal), 5% partes posicionadas a cada quadro
para todos os bichos, menos de 2% na nossa camada viva (`LivelyMotion`/`DinoGeoModel`).

### O que mudou (sem mudar comportamento)

1. `ai/MemoWalkNodeEvaluator`: o tipo de cada bloco é calculado uma vez por busca e lembrado até ela acabar. A busca
   roda inteira sobre uma cópia da região, então a resposta não muda: o caminho sai idêntico ao do vanilla.
2. `ai/MemoPathFinder`: cada bicho lembra as últimas quatro buscas por 1 s. A mesma busca (mesma posição exata de
   partida, mesmo chão/água, mesmos alvos e parâmetros) devolve uma cópia da resposta anterior em vez de buscar de novo.
   Só os terrestres (`DinosaurEntity#createNavigation`, a navegação de chão vanilla com essas duas peças);
   voadores, nadadores e o Deinossuco mantêm a deles.
3. `FleeHurtGoal`: depois de uma corrida que parou curta, a nova direção sai no mínimo 0,5 s depois da anterior
   (antes: a cada tick enquanto a navegação estivesse parada). É a única mudança de ritmo; a escolha da direção é a mesma.
4. Partes (`DinoParts.Index`): as caixas dos donos vão para um vetor plano uma vez por tick, com folga de 4 blocos; a
   consulta só olha de perto quem toca a caixa. O teste exato continua o mesmo. Limite conhecido: um bicho
   teleportado mais de 4 blocos dentro do mesmo tick pode ter as partes ignoradas até o tick seguinte.
5. Posição das partes sem alocar por parte e sem a caixa do vanilla que era jogada fora (`DinoPart.place` usa `setPosRaw`).
6. Cliente: as partes só são reposicionadas a cada quadro para os bichos a até 32 blocos da câmera (mais longe que
   qualquer alcance de arma); os outros usam a posição do tick.
7. Com o Jade instalado, a placa de nome não faz mais a mira por tick (ver abaixo).

Resultado: a busca de caminho caiu de 5,6-13,2 para 2,8-4,8 ms por tick (fração de 29-53% para 13-20%); o total com o mod, de 12,6-19,9 para 11,1-14,6 ms por tick (cerca de -25% na média; a máquina livre deu 11,1).
O total com o mod caiu menos, porque o que sobrou é sobretudo física vanilla dos corpos grandes e a variação do
cenário (quantos estão lutando, fugindo ou comendo) é maior que a diferença.

### Por que não chegou a 1%

- A comparação com o jogador não é direta: os 3,7% dele são uma fração do tick de um servidor com 410 mods; aqui o
  servidor só tem o Terrassic, então quase tudo o que ele faz com os bichos aparece como "com o mod".
- O que sobra é, na maior parte, código vanilla executado para entidades de tamanho real (caixas de 3 a 6 blocos):
  colisão, empurrão, fluido, A* (já memorizado). Cortar isso exige mudar comportamento:
  - pular a física de um bicho parado no chão por alguns ticks (atraso de contato com fogo/cacto/placa e de queda);
  - "LOD" de IA por distância ao jogador (não ajuda no cenário do jogador, onde está todo mundo perto);
  - repath mais espaçado nos objetivos de perseguição do vanilla (`MeleeAttackGoal`, 4-11 ticks);
  - no cliente, diminuir os quadros-chave das animações no exportador (`anim2.py`) e/ou LOD de modelo.
  Ficam como propostas para o Rodrigo aprovar.

## Segunda rodada: física de bicho parado e modelo simplificado longe (aprovadas pelo Rodrigo)

### O que mudou

1. **Física de bicho parado** (`DinosaurEntity.standingStill`, servidor). O JFR mostrou que `Entity.move` (colisão com os
   blocos, `BlockCollisions`, `checkSupportingBlock`) era 28-29% da thread do servidor; `pushEntities`, só 2%. Um bicho no
   chão sem nada a fazer (sem caminho, sem alvo, sem movimento pedido ao `MoveControl`, sem passageiro, sem coleira,
   velocidade horizontal zero, sem dano recente, fora de água, lava, fogo e neve fofa) há meio segundo pula o
   `travel` vanilla e o próprio `pushEntities`; a animação de passo continua (`calculateEntityAnimation`). Acorda na
   hora: caminho ou objetivo que anda, empurrão ou golpe (velocidade), bloco de apoio que perde a colisão (conferido
   a cada tick pelo `mainSupportingBlockPos`). Mesmo parado, a física inteira roda 1 tick em 10 (fogo, cacto, placa:
   atraso de até 0,5 s). Quem se mexe continua empurrando o parado. Na cena do `PerfTest`, 63% das chamadas de `travel`
   cumpriam as condições. `TERRASSIC_NO_STILL=1` desliga, para comparar.
2. **Modelo simplificado longe da câmera** (`client/DinoLod`, cliente). Opções novas em `config/terrassic-client.json`:
   `"lod_near": 32` e `"lod_far": 64` (0 desliga). Depois de `lod_near` os ossos são calculados a cada 2 quadros e depois
   de `lod_far` a cada 3; nos quadros do meio a última pose daquele bicho volta para o modelo compartilhado
   (`DinoLod.Pose`, com as marcas de "mudado" limpas como o GeckoLib deixa, e o `lastRenderedInstance` do GeckoLib
   invalidado para um segundo passe no mesmo quadro, como a sombra de shader). A `LivelyMotion` some aos poucos nos 8
   blocos depois de `lod_near` (mistura da pose com e sem a camada, sem salto) e deixa de rodar além disso. Cubos com
   menos de meio pixel na tela (pelo FOV e pela altura da janela) não são desenhados. Telas (Caderno, HUD) nunca usam o LOD.

### Números

Mesmo `PerfTest` (cena de 2 de cada espécie, câmera sobre a clareira). Antes = `perf/jade-1.11` em `6a58112d`.

| Rodada | Carga da máquina | Bichos | CPU do servidor (ms/tick) | Com o mod (ms/tick) | `Entity.move` (% do servidor) | Animação GeckoLib (% do render) | FPS |
|---|---:|---:|---:|---:|---:|---:|---:|
| Antes 1 | ~5 | 126 | 13.0 | 7.7 | 28.2% | 27.5% | 63 |
| Antes 2 | ~5 | 123 | 14.3 | 8.3 | 29.1% | 25.2% | 57 |
| Depois 1* | 30-40 | 133 | 12.7 | 7.4 | - | - | 48 |
| Depois 2* | 30-40 | 118 | 10.5 | 5.6 | 28% | - | 52 |
| Depois 3* | 4 → 23 | 119 | 21.1 | 11.3 | 25.7% | 22.1% | 38 |
| Depois 4* | 23 → 32 | 116 | 26.4 | 14.9 | 20.8% | 16.7% | 27 |

\* outro agente gerava modelos no Blockbench e rodava um cliente Minecraft na mesma máquina (carga de 20 a 120 em
8 núcleos). Os ms/tick e o FPS dessas rodadas não servem para comparar; as frações dentro de cada thread (amostras com o
método na pilha ÷ amostras da thread) aguentam melhor a contenção e são o que se pode afirmar:

- servidor: `Entity.move` caiu de 28-29% para 21-26% da thread (cerca de -20%); o resto é de bichos que andam;
- cliente: a animação do GeckoLib caiu de 25-27% para 17-22% da thread de render; os vértices (`renderCube`, 42-45%)
  não mudaram, porque na cena quase todos os bichos ficam a menos de 32 blocos da câmera. O LOD rende no cenário
  espalhado do jogador, não nesta cena compacta; o corte de cubos de meio pixel quase não tira vértices.
- a rodada "Depois 2" tem 5,6 ms/tick com o mod, mas com a máquina carregada; não está na conta.

Gráfico: `Claude outputs/desempenho-jade-1.11/img/desempenho_rodada2.svg`.

### Regressão (segunda rodada)

Bateria completa com o código final: 190 passaram, 9 falharam, com a máquina sob carga de 40 a 120. Repetidas só as
fases das falhas (`water,paths,roarfear,maia,thesc` e depois `maia` sozinha), todas passaram: Deinossuco e T. rex na
água, caminho do Edmontossauro, rugido assusta o pequeno, filhote fica no ninho (2,7 blocos), a colônia toda defende,
Tescelossauro dorme na toca. Ficam as duas conhecidas do Coritossauro (manada foge junta, chamado a 50 blocos).

### O que ficou de fora

- Medida limpa (máquina livre) do depois: as quatro rodadas pegaram outro agente trabalhando.
- Menos quadros-chave no exportador (`anim2.py`) e vértices mais baratos (é o maior custo do cliente, 42-45%).
- LOD de IA por distância e repath mais espaçado nos objetivos de perseguição.
- Foto do Jade no Forge: `:forge:runClient -Pjade` carrega o nosso plugin ("Start loading plugin at
  com.terrassic.compat.jade.TerrassicJadePlugin"), mas o próprio Jade 11.13.3 cai no cliente de desenvolvimento antes de
  abrir o mundo: o mixin `jade.mixins.json:StringRenderOutputMixin` não acha o `@Shadow this$0` em
  `Font$StringRenderOutput` com o refmap remapeado pelo Architectury Loom. É do ambiente de dev com o jar do Jade, não
  do Terrassic; falta conferir num Forge de verdade (instância com o jar final e o Jade da loja).

## Jade

- `compat/jade/TerrassicJadePlugin` (comum e servidor) e `JadeDinoTooltip` (cliente). Dependência só de compilação
  (`modCompileOnly maven.modrinth:jade:11.13.3+fabric`, a API é a mesma no Forge); o jar final não leva o Jade.
  Fabric: entrypoint `jade` no `fabric.mod.json` (e `suggests`); Forge: anotação `@WailaPlugin`. Sem o Jade a classe
  nunca é carregada.
- Linhas: título do próprio Jade ("Tiranossauro · Nv 23" ou "Tiranossauro Alfa · Nv 137") e vida; depois
  sexo · filhote/adulto (com nome próprio, a espécie vem antes), "Alfa", "Domado"/"Selvagem" (o dono vem na linha
  "Dono:" do Jade; se ela estiver desligada, o nosso "Domado, dono: X"), "Desmaiado · torpor 56% · acorda em 0:09" e
  "Doma: 4%". Torpor, tempo e progresso vêm de um provedor de servidor (cópia enxuta da ficha da Lente de Campo);
  num servidor sem Jade ficam só as linhas do cliente. Mira numa parte (cabeça, pescoço, cauda) mostra o dono.
- Chave do plugin nas opções do Jade: "Animais do Terrassic". Textos em pt_br, en_us e es_es pelo `gen_resources.py`
  (`JADE_LANG`). Não há conteúdo de história nas linhas.

### A barra de vida

É a placa de nome sobre o bicho que você olha (`client/DinoNameplate`: nome, nível e barra de vida; barras de doma ao lado
quando desmaiado). Já existia `hud_nameplate` em `config/terrassic-client.json` (e na tela HUD do menu de pausa).
Novo: `hud_nameplate_with_jade` (padrão `false`). Com o Jade instalado a placa sai do caminho sozinha; ligar essa
opção a traz de volta. A chave aparece na tela HUD só quando o Jade está instalado ("Placa de nome com o Jade também").

### Teste

`./gradlew :fabric:runClient -Pjade` (também `:forge:runClient -Pjade`) põe o Jade só no cliente de desenvolvimento.
`TERRASSIC_JADE_SHOTS=1 ./gradlew :fabric:runClient -Pjade --args="--quickPlaySingleplayer partes"` fotografa o tooltip
em pt_br: selvagem, filhote, domado, desmaiado em doma, alfa, a placa forçada junto do Jade e a tela HUD.

## Regressão de comportamento

Bateria completa (`TERRASSIC_BEHAVIOR_SPECIES=regressao` + `behavior_regression.py`), 17/11, código de `9768fce8`:
**181 passaram, 2 falharam**.

- `caminho triceratops` (40 blocos entre pilares, "não chegou em 30 s"). Investigado: a única mudança que mexe no
  caminho é a memória de busca. A chave dela foi apertada para a posição exata (o nó de partida do vanilla olha os
  cantos da caixa do corpo, não só o bloco; `0c260389`). Repetida a fase `paths` duas vezes: os quatro chegaram nas
  duas (Tricerátops em 17,2 s e 24,7 s). Fase instável perto do limite de 30 s, não reproduzida.
- `cory: o chamado chega a 50 blocos e acorda` (a manada cochilando correu 1 de 3). A mesma fase `cory` rodada no
  código de antes (`dcda48d5`, sem nenhuma mudança deste trabalho) também falhou ali (0 de 3) e em mais dois itens
  ("a manada foge junta", "um baixa a cabeça e sai"); depois da mudança, outra rodada falhou em "colhe bagas" e
  "um baixa a cabeça". É instabilidade da fase nova do Coritossauro (1.11), não efeito deste trabalho.

Também: `python3 -B tools/validation/check_project.py` (0 erros) e `./gradlew build` (Fabric e Forge, regressões
de pesquisa e movimento) passaram; os jars finais não contêm classes do Jade.

## Modelos: custo de desenho no cliente (20/11)

Pedido: "os modelos estão pesados" (3,7% no Spark contra 0,5% de outro mod; outro jogador pediu modelos otimizados). No
cliente, 82-85% da thread de render era o GeckoLib desenhando os nossos modelos (46-52% escrevendo vértices, 21-28%
animando). Esta parte cuida só da escrita dos vértices; o LOD de animação por distância é do `perf-jade`
(`client/DinoLod`). Nada aqui muda a aparência.

### Como medir

- **Por espécie**: `client/dev/DrawBench` (`TERRASSIC_DRAWBENCH=1`). Mundo superplano sem spawn, jogador espectador
  olhando uma grade de N bichos parados (NoAI, tocando o idle). Para cada espécie mede a vista vazia e a grade desenhada
  de três jeitos no mesmo lugar: **A** = escritor de cubos do próprio GeckoLib, **B** = escritor enxuto, **C** = enxuto e
  sem as faces de trás dos cubos fechados. Por jeito: quadros, CPU da thread de render por quadro, quads escritos e tempo
  dentro do renderizador. Com `TERRASSIC_DRAWBENCH_SHOTS=1` também pausa o jogo (as animações e a camada viva param) e
  fotografa o MESMO quadro nos três jeitos; `tools/validation/drawbench_shots.py` compara pixel a pixel.
  `TERRASSIC_DRAWBENCH_MODES=A,C,A,C,...` alterna os jeitos (a primeira janela de cada jeito é aquecimento do JIT);
  `TERRASSIC_DRAWBENCH_COWS` põe a régua das vacas. Relatórios: `tools/validation/drawbench_report.py`.
- **Cena de 120 bichos**: o `PerfTest` de cima com `TERRASSIC_PERF_ALTERNATE=1` troca A e C a cada 5 s durante a
  gravação, na mesma cena e na mesma hora. Foi preciso: o agente do `perf-jade` rodava clientes na mesma máquina e duas
  rodadas seguidas (A num cliente, C no outro) deram 42 e 30 fps, puro ruído de máquina e de cena. A alternância divide o
  mesmo ruído entre os dois lados. As rodadas finais foram feitas com a máquina livre (carga 3 a 7, nenhum outro cliente).

### Quanto custa um bicho (em vacas)

64 bichos parados na frente da câmera, A e C alternados quatro vezes, sem a primeira janela; o custo é a CPU da thread
de render por quadro acima da vista vazia, dividida por 64. Régua: 512 vacas, **4,3-4,6 µs por vaca por quadro**.
Antes = geo original e escritor do GeckoLib (A); depois = geo cortado e escritor enxuto (C).

| Bicho | quads antes | depois | µs por quadro antes | depois | vacas antes | depois |
|---|---:|---:|---:|---:|---:|---:|
| Tiranossauro | 384 | 190 | 58,6 | 26,6 | 13,6 | 5,7 |
| Euoplocéfalo | 1.230 | 578 | 154,8 | 45,9 | 35,9 | 9,9 |
| Majungassauro (refeito médio, 412 quads) | 412 | 194 | 64,7 | 32,1 | 15,0 | 6,9 |
| Maiassaura | 329 | 207 | 61,2 | 29,9 | 14,2 | 6,4 |

Só no renderizador (tempo dentro de `render`, sem o envio à GPU): Tiranossauro 60,6 → 33,1 µs, Euoplocéfalo 153 → 52 µs,
Majungassauro 67 → 38 µs. O que sobra é sobretudo a animação (GeckoLib procura quadros-chave linearmente) e a cópia dos
vértices para a GPU. Uma vaca vanilla tem 9 cubos (~54 quads) e quase nenhuma animação; um refeito tem 70-110 cubos.

Quads escritos por bicho por quadro (um de cada, ossos escondidos já fora): **14.270 → 7.858 (−45%)**.

| Espécie | antes | depois | | Espécie | antes | depois | |
|---|---:|---:|---:|---|---:|---:|---:|
| euoplocephalus* | 1230 | 578 | −53% | therizinosaurus | 382 | 198 | −48% |
| stegosaurus* | 864 | 415 | −52% | edmontosaurus | 360 | 242 | −33% |
| ankylosaurus | 803 | 583 | −27% | spinosaurus | 358 | 188 | −47% |
| pachyrhinosaurus* | 728 | 362 | −50% | velociraptor | 348 | 179 | −48% |
| deinosuchus | 722 | 464 | −36% | protoceratops | 333 | 233 | −30% |
| pteranodon | 602 | 276 | −54% | dakotaraptor | 332 | 168 | −49% |
| styracosaurus | 571 | 377 | −34% | maiasaura | 329 | 207 | −37% |
| quetzalcoatlus | 490 | 309 | −37% | parasaurolophus | 316 | 192 | −39% |
| triceratops | 477 | 324 | −32% | elasmosaurus | 307 | 187 | −39% |
| giganotosaurus | 466 | 224 | −52% | gallimimus | 304 | 148 | −51% |
| pachycephalosaurus | 460 | 245 | −47% | mosasaurus | 292 | 180 | −38% |
| daspletosaurus | 442 | 209 | −53% | thescelosaurus | 266 | 142 | −47% |
| carcharodontosaurus | 436 | 206 | −53% | tyrannosaurus | 384 | 190 | −51% |
| albertosaurus | 430 | 205 | −52% | majungasaurus | 412 | 194 | −53% |
| carnotaurus | 418 | 199 | −52% | corythosaurus | 409 | 234 | −43% |

\* Fora do jogo padrão: só as 27 espécies refeitas (`Eras.REMADE`) nascem; Euoplocéfalo, Estegossauro e Paquirrinossauro
só aparecem com `especies_antigas`. O Paquirrinossauro está sem o corte de geometria (está sendo refeito); o número
dele é só o das faces de trás.

### Cena de 120 bichos (PerfTest, A e C alternados a cada 5 s)

| Rodada | geo | A: fps | A: ms CPU/quadro | C: fps | C: ms CPU/quadro | C/A |
|---|---|---:|---:|---:|---:|---:|
| 1 | original | 69,6 | 12,27 | 89,3 | 9,49 | −23% |
| 2 | cortado | 71,6 | 11,91 | 94,4 | 9,00 | −24% |
| 3 (final, com cascas seladas) | cortado | 59,2 | 13,82 | 83,1 | 10,17 | −26% |

"ms CPU/quadro" é a thread de render inteira (terreno, céu, partículas, interface), não só os bichos: os bichos caíram
pela metade, o quadro inteiro caiu um quarto, e o fps subiu 28-40%. A rodada 3 teve uma cena mais pesada (lutas e
carcaças na frente da câmera); por isso a comparação vale dentro de cada linha. Fração da thread de render com o mod
na pilha na rodada 3 (metade A, metade C): 80,6% (antes: 84-85%).

### O que mudou

1. **`client/LeanGeoRenderer`** (base de `DinosaurRenderer` e `CarcassRenderer`): escreve os cubos sem alocar nada
   por vértice, quad ou cubo (o GeckoLib fazia um `Vector4f` por vértice, `Vector3f` por quad, `Matrix4f` e três
   `Quaternionf` por cubo: 640 MB/s na cena de 120); cubo sem rotação própria vai direto com a matriz do osso (o
   GeckoLib empilhava e girava por três ângulos zero em cada cubo); a rotação de um cubo girado é calculada uma vez por
   modelo; osso escondido junto com os filhos é pulado inteiro (o GeckoLib já não desenhava os cubos, mas percorria o
   osso e chamava as camadas).
2. **Faces de trás**: o modelo é desenhado sem descarte de faces (`entityCutoutNoCull`), então a CPU escrevia as seis
   faces e a GPU escondia as de trás atrás das da frente. Agora, num cubo fechado e opaco, a face que olha para longe do
   olho não é escrita. O olho sai das matrizes de projeção e de visão do momento (vale no mundo e nas telas). Fica tudo
   como estava num cubo achatado, espelhado, com qualquer texel transparente nas faces (lido da textura que está sendo
   desenhada), num bicho invisível ou esmaecido, e com Iris/Oculus instalados (a passada de sombra tem outro olho).
   "Fechado" = seis faces, ou faces a menos só onde o `geo_cull` provou que o buraco está tapado (abaixo).
3. **`tools/modelgen/geo_cull.py`**: tira do geo.json as faces que nunca aparecem. Só cubos do MESMO osso servem de
   cobertura (as animações mexem os ossos; esconder um osso esconde os cubos dele juntos); só cubo "sólido" cobre
   (sem rotação, sem lado zero, seis faces, todos os texels das seis faces opacos em todas as peles da espécie). Sai a
   face cujo interior inteiro está no interior da união dos sólidos do osso (teste exato numa grade comprimida; face
   encostada na superfície fica, face prensada contra outro sólido sai junto com a face dele); de cubo girado, só se
   os quatro cantos estiverem dentro de um único sólido. Cubos em UV de caixa que perdem face viram UV por face com
   exatamente os números que o GeckoLib calcula (a ferramenta confere face a face). Ao lado escreve
   `assets/terrassic/geo_cull/<id>.json` (fora de `geo/`, que o GeckoLib lê inteiro): os cubos que eram caixas
   inteiras, e as **cascas seladas** (cubo a que o `qa.separate_coplanar` tirou a face colada, quando sólidos do mesmo
   osso tapam o buraco por fora), com o SHA-1 do geo.json; o renderizador só confia no registro se o SHA-1 bater.
   Saíram **1.947 faces de 26.438 (7,4%)** em 57 espécies; mais: Euoplocéfalo 179, Dilofossauro 89, Hatzegopteryx 83,
   Estrutiomimo 82, Argentinossauro 80, Saltassauro 79, Deinoqueiro 71, Estegossauro 68; refeitos: T. rex 43,
   Giganotossauro 37, Carnotauro 32, Albertossauro 22, Majungassauro 22, Carcarodontossauro 23, Daspletossauro 21,
   Coritossauro 17, Quetzalcoatlo 17, Maiassaura 16, Terizinossauro 15, Triceratops 15, Anquilossauro 14,
   Paquicefalossauro 13, Galimimo 12, Estiracossauro 10, Dakotaraptor 9, Tescelossauro 10, Elasmossauro 10, Edmontossauro
   8, Mosassauro 8, Parassaurolofo 7, Espinossauro 7, Protocerátops 3, Deinossuco 1. Os refeitos ganham pouco aqui porque o
   `qa.separate_coplanar` já tirava as faces coladas; o ganho deles vem das faces de trás (e das cascas seladas:
   Deinossuco 641 → 464 quads só com elas).
   Ligado ao fim do export: `_engine/proto.geo_json` (e as cópias do T. rex, Pteranodonte e Velociraptor) registra o
   corte para o fim do processo, quando as peles já foram escritas; só corta se aquele build escreveu o geo.json (uma
   prévia que só lê não mexe). `build_all.py` (modelos antigos) chama depois de escrever. Idempotente.
   **Paquirrinossauro, para rodar quando o refeito entrar** (o build pelo `_engine` já faz sozinho):
   `build/menu-render-venv/bin/python -B tools/modelgen/geo_cull.py pachyrhinosaurus`.
4. `StuckProjectilesLayer` lia dardos e flechas da entidade em cada osso de cada bicho; agora uma vez por quadro.

### Prova de que nada mudou na tela

- **Geometria, fora do jogo**: `tools/modelgen/geo_cull_check.py --ref HEAD` desenha cada espécie (o geo do git contra
  o cortado, e o cortado ainda sem as faces de trás vista a vista, como o jogo escreve) com o renderizador do motor
  (`_engine/geo.py`: z-buffer, sem descarte, recorte abaixo de alfa 10, como o `entityCutoutNoCull`) de 8 direções, em
  3 poses e 2 conjuntos de ossos (macho adulto sem sela; filhote fêmea com sela), e compara pixel a pixel. Com pixel
  exatamente sobre uma aresta esse renderizador desempata a profundidade pela ordem de desenho (uma face tirada, vista
  de quina numa emenda, ganhava o pixel por ser desenhada antes): o quadro é deslocado duas vezes por fração de pixel e
  só conta a diferença que aparece nas duas. Resultado (59 espécies, 2.832 fotos de 420 × 300): **0 pixels persistentes**; 292 pixels de desempate soltos
  em toda a bateria (0 a 14 por espécie), nenhum repetido no segundo deslocamento.
  A ferramenta detecta face visível tirada: tirar a face de cima do corpo e a lateral da mandíbula do T. rex deu
  35.077 pixels diferentes.
- **No jogo, mesmo quadro**: `drawbench_shots.py` com o jogo pausado. A contra B (só a ordem das contas muda) e B
  contra C (faces de trás) ficam em 0-36 pixels por foto de 16 bichos (1708 × 960), todos isolados sobre arestas: é o
  desempate de profundidade na borda entre face da frente e face de trás. Antes da correção das cascas (abaixo) a
  Maiassaura dava 507 pixels em faixas; depois, 2-3.
- Fotos: `Claude outputs/desempenho-modelos-1.11/img/` (`mesmo_quadro_<espécie>.png`: A, C e a diferença em magenta no
  mesmo quadro; `antes_depois_<espécie>.png`: geo original + GeckoLib contra geo cortado + escritor enxuto, rodadas
  diferentes, então pose e sexo podem mudar).

Achado no caminho: a primeira versão tratava como fechado qualquer cubo com faces opacas. Os refeitos têm muitas
"cascas" (cubos de cinco faces: o QA tira a face colada), e por um buraco desses aparece o lado de dentro das outras
faces; descartar as de trás abria faixas no jogo (Maiassaura, Tricerátops, Edmontossauro). Por isso o registro ao lado
do modelo.

### O que o renderizador fazia (auditoria)

- Cada bicho é desenhado UMA vez por quadro. A segunda passada só existe para criaturas da Fenda (`RiftLayer`,
  `isRift`), como deve ser. Sela, arreio, crista, display de macho/fêmea e partes de adulto/filhote são ossos do mesmo
  modelo, escondidos por `setHidden` (que no GeckoLib 4.8 também esconde os filhos). Placa de nome (`DinoNameplate`) é
  texto e barra; aura do alfa são partículas; o chapéu (Hats) só lê a matriz do osso; sombra é a do vanilla (uma por
  bicho).
- Um `RenderType` por bicho (o GeckoLib pega um buffer só); textura resolvida por `ResourceLocation` guardado em
  `DinoGeoModel` (a carcaça monta o nome a cada quadro: pouco, ficou).
- O caro era: alocação por vértice (acima), rotação por cubo, as faces de trás, e — fora daqui — a animação.
- Ossos escondidos ainda são ANIMADOS pelo GeckoLib (o processador de animação não sabe do `hidden`). Não mexi: é a
  frente do `perf-jade`.

### Propostas que mudam a aparência (para o Rodrigo decidir)

1. **Anquilossauro** (o mais caro dos ativos depois do corte: 583 quads, 171 cubos, 76 girados): os osteodermos são
   cubos girados pequenos (412 das 917 faces do modelo); girado não serve de cobertura e quase nunca é cortado. Juntar
   as fileiras de osteodermos em menos cubos maiores, ou pintar os menores na pele, é o maior corte que resta num bicho
   ativo (estimativa: metade daquelas 412 faces).
2. **Deinossuco, Estiracossauro, Tricerátops, Quetzalcoatlo, Edmontossauro**: ainda há cascas cujo buraco não é tapado
   por cubo do mesmo osso (encostam em osso vizinho). Mover o cubo para o osso do vizinho, ou deixar o QA fechar a
   casca com uma face recuada, permite descartar as faces de trás delas (Deinossuco ainda tem 24 cascas abertas).
3. **Modelos antigos** (Euoplocéfalo 205 cubos, Estegossauro 144, Paquirrinossauro 130): só aparecem com
   `especies_antigas`; quando forem refeitos, seguir a contagem dos refeitos (70-110 cubos).
4. **Dentes e garras em cubo**: cubos de até 2 px somam só 4% das faces dos refeitos (0 a 15% por espécie); pouco
   a ganhar pintando-os, e o LOD de cubos pequenos do `perf-jade` já os tira de longe. Não recomendo.
5. Animação: menos quadros-chave no exportador (`anim2.py`, hoje 25-80 por canal) é o próximo grande corte do lado da
   CPU; já proposto acima.

### Testes

`./gradlew :fabric:compileJava :forge:compileJava`, `python3 -B tools/validation/check_project.py` (0 erros),
DrawBench completo antes/depois (31 espécies + vacas), três rodadas alternadas do PerfTest, fotos congeladas.
Não rodei a bateria de comportamento: nada aqui toca entidade, IA ou servidor.

## Bateria final da 1.11.0 (20-21/11)

Código da `rel/1.11.0` de `fbd23208` em diante, com os consertos abaixo (commits `dd94508f` a `a1a279dc`).

### Consertos

- **Coritossauro**, "o chamado chega a 50 blocos": teste. A manada distante ficava a 50 blocos de onde a vizinha nasceu,
  mas a vizinha anda atrás do líder até o muro e o chamador ficava a 60-66 blocos (o alcance é 64). Agora ela é posta a
  50 blocos de onde a vizinha está. O "acordado" era lido no fim do laço, depois de o teste encurtar a vigília para
  8-16 s; o bicho marca quando o alarme o alcança e se o acordou (`alarmsGot`, `wokeToAlarm`).
- **Coritossauro**, "colhe bagas": comportamento. Os objetivos de manada e de pastar tomavam a navegação e o levavam
  para longe do arbusto; enquanto vai ao arbusto o caminho dele vale (desiste após 30 s).
- **Coritossauro**, "um baixa a cabeça e sai": comportamento. O vencedor seguia o perdedor quando o perdedor era o
  líder da manada, e o perdedor era trazido de volta pelo objetivo de manada. O vencedor fica 15 s; o perdedor pasta
  15 s onde parou.
- **Paquirrinossauro**, "raspa a neve": teste. A manada da travessia para em z = 100, a 4 blocos da neve e fora do raio
  de limpeza; a fêmea sozinha se juntava a ela e saía da neve antes do primeiro gesto.
- **Paquirrinossauro**, "o líder entra primeiro" (falhou 3 vezes seguidas na bateria): comportamento. A manada anda lado
  a lado e um seguidor à frente do líder entrava no rio antes dele. Esperando, quem está na água ou à frente do lugar do
  líder recua para trás dele, e o líder só entra com a margem livre (até 13 s).
- **Tescelossauro**: dois testes mal medidos ("dispara a 18 blocos": a distância era lida depois, já na corrida, ou de
  um companheiro que disparou pelo lenço; "dorme na toca": bicho só dorme depois do 60º segundo de vida, e este nascia
  15-20 s antes da noite) e o domado posto a 11 blocos de onde o dono está mesmo (o cliente ainda movia o jogador).
- **Sono que não acordava** (achado no Playtest): o seletor de objetivos só pergunta `canUse`/`canContinueToUse` a cada
  2 ticks (tick do servidor + id par). `DinoSleepGoal` (acordar com caçador perto, `tickCount % 10 == 0`),
  `SafeRestGoal` (`% 40`) e o lanche de chão do Anquilossauro (`% 10`) nunca coincidiam para metade dos bichos: um
  Estiracossauro dormiu a 5 blocos de um Albertossauro acordado. Agora `% N <= 1`.
- **Tescelossauro à noite**: ia até 1,5 bloco do centro da toca, mas a boca de uma toca apertada fica a ~1,6; andava no
  lugar (22 s no Playtest). "Chegou" é o mesmo raio de 2 blocos do `isSleepTime`.
- **Predador que acompanha manada** (`ShadowHerdGoal`): um ponto do flanco inalcançável (Albertossauro entre sequoias)
  o deixava andando no lugar 28 s. Sem avanço em 10 s, tenta o outro flanco; na segunda, desiste por ora.
- **`fall_asleep`**: 18 das 20 espécies do conjunto comum não têm a animação, e o GeckoLib escrevia "Unable to find
  animation" a cada quadro (4.285 linhas numa fase). Só dispara se o rig tem.

### Regressão de comportamento

Primeira bateria completa: **208 de 213**. Repetidas as fases das 5 falhas: caminho do Edmontossauro e do Tricerátops
(13,2 e 17,1 s), filhote do Maiassauro no ninho (2,0 blocos) e Tescelossauro domado passaram; "um baixa a cabeça" era
defeito (consertado). Na repetição apareceram os dois testes mal medidos do Tescelossauro (consertados).

Bateria completa depois dos consertos de sono (camada compartilhada): **208 de 213**. Repetidas: Tiranossauro nadando
(3 quiques), degrau do Tiranossauro (0,18 bloco por tick), manada sem andar no lugar (4 bicho-segundos) e Tescelossauro
se esconde no mato passaram; o domado falhou de novo (30,4 a 30,4 blocos: começava fora do alcance, consertado no
teste) e passou na rodada seguinte (11,5 a 4,8). Tudo o que falhou passou na repetição: são instabilidades perto do
limite (caminho, nado, degrau, esconderijo), não defeitos.

### Rodada num mundo real (Playtest)

`TERRASSIC_PLAYTEST=1`, mundo novo, 10 lugares + a Colônia de Ninhos + um habitat de cada herbívoro novo
(`tools/validation/playtest_report.py`): **89 de 90** na rodada final.

- Nascem e se comportam no mundo: Maiassauro 53, Coritossauro 4, Paquirrinossauro 7, Tescelossauro 32 vistos;
  log com `[maia]` 77, `[cory]` 65, `[pachy]` 3 e `[thesc]` 178 linhas, 16 de toca do Tescelossauro.
- Colônia de Ninhos (-288, -272): 13 ovos de Maiassauro nos ninhos (10 cobertos) e 8 Maiassauros em volta; à noite um
  Dakotaraptor veio pelo ovo e a colônia o expulsou. Fora da colônia, manadas de Maiassauro põem ninhos no campo e os
  defendem (é a regra: colonista defende).
- Ninguém preso 20 s ou mais (a primeira rodada teve dois, consertados acima), ninguém quicando na água, nenhum
  dorminhoco perto de caçador (o mais perto a 19 blocos), sem exceção do mod, 0 "Unable to find animation".
- **Física de bicho parado**: ninguém flutuando (fora do chão, sem subir nem descer, com ar embaixo, 3 s seguidos) nas
  duas rodadas. A única falha: um Protocerátops 1 s dentro de bloco (empurrado e saiu; não se repetiu).
- **LOD**: a câmera vai de 76 a 10 blocos de um bicho parado em 16 s e `client/dev/LodProbe` mede a mudança dos ossos
  por quadro. No cruzamento de 32, 40 e 64 blocos o maior quadro (0,20, 0,20 e 0,17) não passa do maior em volta
  (0,33, 0,33 e 1,20): sem pulo.

### Medida limpa de desempenho

`PerfTest`, máquina livre (`ps`: só o cliente; carga 4-6), 2 rodadas. A cena agora tem 27 espécies em terra (138
bichos; antes 120-126).

| Rodada | Bichos | CPU do servidor (ms/tick) | Com o mod (ms/tick) | % de 50 ms | Render com o mod | FPS |
|---|---:|---:|---:|---:|---:|---:|
| Antes A (`dcda48d5`) | 120 | 25.1 | 19.9 | 40% | 84% | 53 |
| Antes B (`dcda48d5`) | 121 | 19.2 | 12.6 | 25% | 84% | 56 |
| Antes 1 (`6a58112d`) | 126 | 13.0 | 7.7 | 15% | - | 63 |
| Antes 2 (`6a58112d`) | 123 | 14.3 | 8.3 | 17% | - | 57 |
| **Final 1** | 138 | 10.5 | **6.6** | 13% | 79% | **91** |
| **Final 2** | 138 | 9.8 | **5.9** | 12% | 79% | **95** |

Mod no servidor: de 16,3 ms/tick (média antes) para 6,2 (−62%), com mais bichos; FPS de 53-56 para 91-95 (+70%).
Gráfico: `Claude outputs/bateria-1.11/img/desempenho_final.png` (e `.svg`), cena em `cena_perf_final.png`.

### Forge e build

- `./gradlew :forge:runClient` sem o Jade, com `TERRASSIC_PLAYTEST_ONLY=portraits`: mundo Terrassic novo, os 4
  herbívoros chamados em seus habitats e fotografados, sem crash e sem erro do mod no log
  (`Claude outputs/bateria-1.11/img/forge/`).
- `./gradlew build` (Fabric e Forge): passou. `python3 -B tools/validation/check_project.py`: 0 erros.

### Fotos

`Claude outputs/bateria-1.11/img/<espécie>_34.png` e `_lado.png` (Fabric, num bioma real ao meio-dia), feitas por
`TERRASSIC_PLAYTEST=1 TERRASSIC_PLAYTEST_ONLY=portraits` (`TERRASSIC_PLAYTEST_SPECIES=...` escolhe as espécies): chão
aberto de 17 × 17, os outros bichos tirados, câmera do lado com visão livre.
