# Partes de acerto (1.7)

Pedido do Rodrigo (04/11/2026), a partir da sugestão da comunidade sobre hitboxes. Status: **implementado** na `main`
e na `mc/1.21.1` (04/11/2026); validado em servidor real, ainda sem revisão no cliente gráfico (ver abaixo).

## Como ficou
- `entity/parts/DinoPart` (entidade filha comum aos dois loaders, nunca salva nem enviada), `DinoParts` (consultas) e
  `PartOwners` (lista dos donos guardada no `Level`). Mixins comuns em `mixin/parts`: `LevelMixin`
  (`getEntities(Entity, AABB, Predicate)` também devolve as partes que caem na caixa), `ServerLevelMixin`
  (`getEntityOrPart` acha a parte pelo id), `EntityCounterAccessor` (bloco de ids: dono, depois 1..n partes, como o
  dragão) e `AbstractArrowInvoker`; cliente: `PartHitboxMixin` (F3+B: cabeça vermelha, pescoço amarelo, corpo verde,
  cauda azul, asa violeta). Não usa o `PartEntity` do Forge/NeoForge: o mesmo caminho nos dois loaders.
- **Cobrem o modelo inteiro** (correção de 04/11 depois do teste do Rodrigo, que achou espaços: o tronco ficava só com
  a caixa de colisão, estreita, e as caixas quadradas deixavam cantos nas diagonais). `tools/javagen/parts.py` lê o
  `.geo.json` em repouso e separa cabeça, pescoço (`neck*`/`throat`), corpo (tronco, pernas e braços), cauda (`tail*`) e,
  em quem tem membrana (`mem_*`, Pteranodonte), as asas; cada tipo é cortado ao longo do seu eixo (o corpo para a
  frente, a asa para fora) em pedaços (até 2/3/4/5/3 por tipo, nunca menores que 0,5 m, folga de 5 cm). Cada pedaço é
  um retângulo (comprimento ao longo do corpo, largura de lado, altura) que gira com o animal: no jogo a caixa é a menor
  que contém o retângulo girado (`DinoPart.place`), então vizinhos sempre se encontram. `tools/javagen/parts_coverage.py`
  confere: todo ponto do modelo (amostras a cada ~2 px) dentro de alguma parte em 7 ângulos; 0% de fora nas 13 espécies.
  O `gen_species.py` grava `PARTS` e `partPivot()` em `PARTS_SPECIES`. Escala com `getScale()`; cabeça e pescoço giram
  com `yHeadRot` (até 75°) em torno da base do pescoço; deitado (nocaute, sono) as partes descem a 35%, sentado a 60%.
  As asas só valem no ar (`FlyingDinosaur.isAirborne`; no chão estão dobradas).
- Dano: `DinoPart.Kind` (cabeça 1,25; pescoço e corpo 1,0; cauda e asa 0,75) em `DinosaurEntity.hurtByPart`; a caixa de
  colisão continua contando 100% (nos pequenos ela fica por fora do pedaço do corpo). O torpor da clava sai do dano já
  multiplicado. O que o motor só faz com alvo vivo é refeito para a parte: desgaste e efeito da arma, último alvo do
  jogador, flecha cravada, encantamentos e o efeito da flecha/dardo. Lança, dardo e boleadeira desembrulham a parte
  (`DinoParts.owner`); o dardo cravado é desenhado na zona acertada. Lupa, carvão, apito e controles também.
- Mordida pela cabeça: `ai/HeadMeleeAttackGoal` substitui o `MeleeAttackGoal` de herbívoros, predadores, voadores e
  marinhos: alcança o que toca a cabeça (+0,8 bloco) ou encosta no corpo; sem partes, o alcance do vanilla.
- Pernas contam como corpo (100%): ficam no pedaço do corpo e sob a caixa de colisão.

## Validação
- `parts_coverage.py`: 0% do modelo descoberto, 13 espécies x 7 ângulos.
- Servidor real (`parts_regression.py`, ataque pelo id da parte): machadinha de pedra num T. rex sem armadura dá 9 na
  caixa, 9 no pedaço do corpo, 11,25 na cabeça e 6,75 na ponta da cauda; flecha na ponta da cauda acerta; dardo no
  focinho dá torpor. 8/8 em Fabric e Forge 1.20.1 e em Fabric 1.21.1.
- **Cliente gráfico de verdade** (`client/dev/PartsShowcase`, ligado só com `TERRASSIC_PARTS_SHOWCASE=1`; rodar
  `TERRASSIC_PARTS_SHOWCASE=1 ./gradlew :fabric:runClient --args="--quickPlaySingleplayer <mundo plano>"`): as 13
  espécies de frente e giradas 45°, F3+B fotografado de lado e de cima (`run/screenshots/parts_*.png`), a mira do
  vanilla (`GameRenderer.pick`) varrendo a linha do corpo a cada 10 cm dos dois lados e de cima, e golpes reais
  (`gameMode.attack`) com machadinha na caixa, no corpo, na cabeça e na ponta da cauda. Fabric 1.20.1, Forge 1.20.1 e
  Fabric 1.21.1: **6.408 miras, 0 falhas; 47 golpes, todos exatos** (9 / 9 / 11,25 / 6,75), relatório em
  `run/terrassic_parts_report.txt`. As fotos conferidas uma a uma: o modelo fica dentro das caixas em todas.
- Antes: `feedback17`, `knockout` e `dart_regression` repetidos (1.20.1 Fabric e Forge: 23/23, 18/18, 25/25; 1.21.1
  Fabric: os mesmos). NeoForge 1.21.1 só compilado. `./gradlew build` passou nas duas branches.

## Pendências
- A mira foi testada com o animal parado (idle); na corrida e nas animações de ataque a cauda e o pescoço se movem um
  pouco além da folga. Asas do Pteranodonte em voo não foram fotografadas (o teste usa o animal parado no chão).
- Better Combat resolve o alvo por `getEntity`, então com ele só a caixa de colisão é acertada.

## Plano original

## O que fazer
1. **Partes de acerto** em `DinosaurEntity` (só espécies ativas primeiro: as 13 de `config/Eras.REMADE`):
   cabeça, pescoço quando houver, corpo, cauda (e pernas nos grandes). Cada parte é uma entidade filha que não colide,
   não é salva e não empurra; segue a rotação do corpo (`yBodyRot`) e a da cabeça (`yHeadRot`) a cada tick.
   Medidas por espécie numa tabela nova em `tools/javagen/gen_species.py` (`PARTS`: deslocamento à frente/atrás,
   altura, largura e altura de cada parte, em metros, a partir do modelo; o `art/build_report.json` dá os limites),
   gerada para cada classe como as outras constantes. Escala com `getScale()` (tamanho e filhote).
2. **Dano por parte**: golpe na parte chega ao dono como `hurt(source, amount * mult)`: cabeça 1,25; corpo 1,0;
   cauda e pernas 0,75 (constantes num lugar só, para ajustar). Torpor da clava segue o mesmo multiplicador.
   Flechas, dardos, lança e boleadeira têm de acertar as partes também (dardo cravado: guardar a parte acertada).
3. **Loaders**: o vanilla só trata partes do Ender Dragon.
   - Forge: `isMultipartEntity()` + `getParts()` (`PartEntity`), já lido por `Level.getEntities`, `ServerLevel` e
     `ClientLevel` (ids das partes = id do dono + 1..n, como o dragão).
   - Fabric: mixins em `Level.getEntities(Entity, AABB, Predicate)` (incluir as partes), `ServerLevel` /
     `ClientLevel` (procurar a parte pelo id no pacote de interação/ataque). Ids reservados no `setId`/`recreateFromPacket`.
   - Código comum com `@ExpectPlatform` ou uma interface comum; nada de classe de loader no common.
4. **Alcance pela cabeça**: as espécies sem `ApexBiteGoal` usam o `MeleeAttackGoal` do vanilla (alcance pela largura da
   caixa). Passar a medir da parte da cabeça, para morderem quem está na frente do focinho e não alcançarem atrás.
5. **Desempenho**: até `MAX_CREATURES` (400) dinos x 4 partes; atualizar posição só quando carregado e perto de jogador.
6. **Testes**: regressão em servidor real (como `feedback17_regression.py`): atacar a cabeça, o corpo e a cauda com a
   mesma arma e comparar o dano 125/100/75; flecha na cauda; o dino não fica preso em mata de 3 blocos. No cliente:
   F3+B mostra as partes; mira e acerto na cabeça e na cauda.

## Porte da 1.7 para a 1.21.1 (`mc/1.21.1`)
Todos os arquivos do commit `7fb53ef2` e os testes da validação. Pontos que mudam na 1.21: pacotes viram
`CustomPacketPayload` (TamedNetwork), `ItemStack`/NBT com componentes, atributos por `Holder`, pastas de data no
singular (`advancement`, `loot_table`), `data/terrassic/weapon_attributes` continua igual (Better Combat 1.21).
Mesmas regressões, adaptando o protocolo do cliente de teste. Tags `v1.7.0` e `v1.7.0-1.21.1` só com as duas prontas.

## Pendências de revisão no jogo
Lista Meus dinos (agachado + H) e a seta; tópicos novos do Guia de Bolso; Better Combat com as clavas.
