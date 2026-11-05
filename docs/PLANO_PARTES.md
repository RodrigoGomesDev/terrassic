# Partes de acerto (1.7)

Pedido do Rodrigo (04/11/2026), a partir da sugestão da comunidade sobre hitboxes. Status: **implementado** na `main`
e na `mc/1.21.1` (04/11/2026); validado em servidor real, ainda sem revisão no cliente gráfico (ver abaixo).

## Como ficou
- `entity/parts/DinoPart` (entidade filha comum aos dois loaders, nunca salva nem enviada), `DinoParts` (consultas) e
  `PartOwners` (lista dos donos guardada no `Level`). Mixins comuns em `mixin/parts`: `LevelMixin`
  (`getEntities(Entity, AABB, Predicate)` também devolve as partes que caem na caixa), `ServerLevelMixin`
  (`getEntityOrPart` acha a parte pelo id), `EntityCounterAccessor` (bloco de ids: dono, depois 1..n partes, como o
  dragão) e `AbstractArrowInvoker`. Cliente: `PartFrameMixin` (antes da mira de cada quadro, as partes vão para onde o
  modelo é desenhado naquele quadro) e `PartHitboxMixin` (F3+B: cabeça vermelha, pescoço amarelo, corpo verde, cauda
  azul, asa violeta). Não usa o `PartEntity` do Forge/NeoForge: o mesmo caminho nos dois loaders.
- **Cobrem o modelo inteiro, parado e se mexendo** (correções de 04 e 05/11 depois do teste do Rodrigo, que achou
  espaços). `tools/javagen/parts.py` lê o `.geo.json` e as animações: separa cabeça (o osso `head` e filhos), pescoço,
  corpo (tronco, pernas e braços), cauda e, em quem tem membrana (Pteranodonte), as asas abertas (dobradas no chão
  contam como corpo). Mede o modelo em repouso e em cada quadro-chave das animações de locomoção (`POSES`: parado,
  andar, correr, espreitar, voar, planar, curvas, olhar de lado) e corta cada tipo em pedaços ao longo do seu eixo.
  Três layouts com os mesmos pedaços: **em pé**, **deitado** (dormindo, sentado, nocauteado: poses `sit`/`sleep`/
  `knocked_out`/`brood`) e **cabeça baixa** (pastando, comendo, bebendo: `graze`/`eat`/`drink`/`sift`/`grit`/`pluck`;
  `DinosaurEntity.isHeadDown`: no cliente, a animação que o controlador `action` toca; no servidor, 3 s depois do
  `triggerAnim`). Cada pedaço é uma caixa orientada no corpo do animal: a cabeça gira e inclina com o olhar em torno do
  osso `head` (como o GeckoLib gira esse osso), o voador inteiro inclina e rola como o `DinosaurRenderer` o desenha,
  tudo gira com o corpo; a caixa da parte é a menor que contém a peça (`DinosaurEntity.placeParts`). Ataques (o bote
  que joga a cabeça 2,5 m de lado) ficam de fora de propósito: uma caixa que os cobrisse seria acertada no ar o resto do
  tempo. `tools/javagen/parts_coverage.py` confere os três layouts: todo ponto do modelo dentro de alguma parte, em 7
  ângulos. Espécie refeita nova entra em `gen_species.PARTS_SPECIES`.
- Dano: `DinoPart.Kind` (cabeça 1,25; pescoço e corpo 1,0; cauda e asa 0,75) em `DinosaurEntity.hurtByPart`; a caixa de
  colisão continua contando 100% (nos pequenos ela fica por fora do pedaço do corpo). Pernas contam como corpo. O
  torpor da clava sai do dano já multiplicado. O que o motor só faz com alvo vivo é refeito para a parte: desgaste e
  efeito da arma, último alvo do jogador, flecha cravada, encantamentos e o efeito da flecha/dardo. Lança, dardo e
  boleadeira desembrulham a parte (`DinoParts.owner`); o dardo cravado é desenhado na zona acertada. Lupa, carvão,
  apito e controles também. A parte responde pelo dono do animal (`OwnableEntity`): mods de combate que poupam os
  bichos do jogador poupam as partes também.
- Mordida pela cabeça: `ai/HeadMeleeAttackGoal` substitui o `MeleeAttackGoal` de herbívoros, predadores, voadores e
  marinhos: alcança o que toca a cabeça (+0,8 bloco) ou encosta no corpo; sem partes, o alcance do vanilla.
- Better Combat: `./gradlew :fabric:runClient -PbetterCombat` roda com ele (só no cliente de teste, nunca no jar).

## Validação (05/11/2026, Mac do Rodrigo)
- `parts_coverage.py`: **0% do modelo fora** nas 13 espécies, nos três layouts, em 7 ângulos.
- Servidor real (`parts_regression.py`, ataque pelo id da parte): machadinha de pedra num T. rex sem armadura dá 9 na
  caixa, 9 no pedaço do corpo, 11,25 na cabeça e 6,75 na ponta da cauda; flecha na ponta da cauda acerta; dardo no
  focinho dá torpor. **8/8 em Fabric e Forge 1.20.1.**
- **Cliente gráfico de verdade** (`client/dev/PartsShowcase`, só com `TERRASSIC_PARTS_SHOWCASE=1`;
  `TERRASSIC_PARTS_PHASES` escolhe entre `still`, `flight`, `moving`, `feedback`, `bettercombat`; relatório em
  `run/terrassic_parts_report.txt`, fotos em `run/screenshots/`). Fabric e Forge 1.20.1:
  - parado, de frente e girado 45°: a mira do vanilla varrendo a linha do corpo a cada 10 cm, dos dois lados e de
    cima, mais o Pteranodonte em voo de ponta a ponta das asas: **6.874 e 6.880 miras, 0 falhas**;
  - golpes reais (`gameMode.attack`): caixa e corpo 9, cabeça 11,25, cauda 6,75, asa 6,75 em todas as espécies (no
    Protocerátops, o golpe de lado na cabeça pega o pedaço do corpo, que é mais próximo: as caixas se sobrepõem);
  - **em movimento** (IA ligada 10 s, depois provocado 10 s), todo vértice do modelo como o GeckoLib o desenhou em
    cada quadro, contra as caixas: 0 a 4,7% dos vértices fora; quadros com algum vértice a mais de 0,5 m fora: 0% em
    8 espécies, 0,6 a 7% nas outras, sempre em animações curtas de parado (`yawn`, `stretch`, `call`), no acordar
    levando golpe ou no salto de esquiva do Gallimimus (pior caso 0,95 m).
- `mc/1.21.1` (Fabric): as mesmas regressões e o mesmo cliente (6.880 miras, 0 falhas; golpes iguais); Better Combat
  2.4.0 com a Clava de Cauda a 125/100/75% e a de Osso acertando a cabeça; o domado poupado.
- Better Combat 1.9.0 (Fabric 1.20.1): as 7 armas do mod reconhecidas (Clava de Osso = maça, Clava de Cauda = martelo
  de duas mãos, lanças, faca, adaga, machadinha); a Clava de Cauda dá cabeça 6,875 / corpo 5,5 / cauda 4,125
  (125/100/75%); a varredura acerta o selvagem e não o domado ao lado (o Better Combat vê o domado e as 11 partes como
  FRIENDLY). O Better Combat acha a parte pelo `getEntityOrPart` (1.9 e 2.4).
- `feedback17` 23/23, `knockout` 18/18, `dart_regression` 25/25 em Fabric e Forge 1.20.1 com o código final.

## Pendências
- Clava de Osso com Better Combat: o primeiro golpe do combo não pegou a cabeça do T. rex no teste (o corpo e a cauda
  sim); não investigado.
- Animações curtas de parado e de ataque saem das caixas por até ~1 m durante o movimento (ver acima).
- Pteranodonte em voo: ao bater as asas, a ponta da membrana passa até ~1 m da caixa em menos de 1% dos vértices da
  asa (sempre a da direita; não é o sinal da inclinação nem o lado, testados); a mira de ponta a ponta das asas não
  falha.
- Na 1.21.1, o Better Combat 2.x embute o `tiny-config`, que o cliente de desenvolvimento não carrega de dentro do jar:
  `fabric/build.gradle` o inclui à parte com `-PbetterCombat`.
- Revisão a olho, jogando: o teste automático não substitui.

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
