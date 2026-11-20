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
