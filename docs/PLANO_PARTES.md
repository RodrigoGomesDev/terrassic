# Partes de acerto (1.7)

Pedido do Rodrigo (04/11/2026), a partir da sugestão da comunidade sobre hitboxes. Status: **implementado** na `main`
e na `mc/1.21.1` (04/11/2026); validado em servidor real, ainda sem revisão no cliente gráfico (ver abaixo).

## Como ficou
- `entity/parts/DinoPart` (entidade filha comum aos dois loaders, nunca salva nem enviada), `DinoParts` (consultas) e
  `PartOwners` (lista dos donos guardada no `Level`). Mixins comuns em `mixin/parts`: `LevelMixin`
  (`getEntities(Entity, AABB, Predicate)` também devolve as partes que caem na caixa), `ServerLevelMixin`
  (`getEntityOrPart` acha a parte pelo id), `EntityCounterAccessor` (bloco de ids: dono, depois 1..n partes, como o
  dragão) e `AbstractArrowInvoker`; cliente: `PartHitboxMixin` (F3+B: cabeça vermelha, pescoço amarelo, cauda azul).
  Não usa o `PartEntity` do Forge/NeoForge: o mesmo caminho nos dois loaders.
- Medidas geradas: `tools/javagen/parts.py` lê o `.geo.json` em repouso (ossos `head`, `neck*`/`throat`, `tail*`;
  sela, `*_display` e `young_*` fora), corta cabeça/pescoço/cauda em pedaços quadrados (até 2/2/4, nunca menores que
  0,6 m) e o `gen_species.py` grava `PARTS` e `partPivot()` nas 13 espécies de `PARTS_SPECIES`. Os limites batem com o
  `art/build_report.json` (T. rex: idênticos). Escala com `getScale()`; cabeça e pescoço giram com `yHeadRot` (até 75°)
  em torno da base do pescoço; deitado (nocaute, sono) as partes descem a 35%, sentado a 60%.
- Dano: `DinoPart.Kind` (cabeça 1,25; pescoço 1,0; cauda 0,75) em `DinosaurEntity.hurtByPart`; o corpo é a própria caixa
  (100%). O torpor da clava sai do dano já multiplicado. O que o motor só faz com alvo vivo é refeito para a parte:
  desgaste e efeito da arma, último alvo do jogador (lobos e dinos domados seguem), flecha cravada, encantamentos e o
  efeito da flecha/dardo. Lança, dardo e boleadeira desembrulham a parte (`DinoParts.owner`); o dardo cravado é
  desenhado na zona acertada (`DATA_DART_ZONES`, `StuckProjectilesLayer`). Lupa, carvão, apito e controles também.
- Mordida pela cabeça: `ai/HeadMeleeAttackGoal` substitui o `MeleeAttackGoal` de herbívoros, predadores, voadores e
  marinhos: alcança o que toca a cabeça (+0,8 bloco) ou encosta no corpo; sem partes, o alcance do vanilla.
- Desempenho: a lista de donos é cópia na escrita; cada consulta testa primeiro a caixa que envolve todas as partes.

## Validação
`tools/validation/parts_regression.py` (servidor dedicado + cliente de protocolo, ataque pelo id da parte): mesma
machadinha de pedra num T. rex sem armadura dá 9 no corpo, 11,25 na cabeça e 6,75 na cauda; flecha caindo na ponta da
cauda, fora da caixa, acerta; dardo no focinho dá torpor. 7/7 em Fabric e Forge (1.20.1) e em Fabric 1.21.1.
Repetidas depois da mudança: 1.20.1 Fabric e Forge, feedback17 23/23, knockout 18/18, dart 25/25; 1.21.1 Fabric, as
mesmas 23/23, 18/18 e 25/25 (na 1.21 a regressão feedback17 dá 40 de vida máxima ao lobo: o dono lido do NBT não aplica
os efeitos da doma e o lobo de 8 morria na primeira mordida). NeoForge 1.21.1 só compilado (o cliente de protocolo
desta branch é só Fabric). `./gradlew build` passou nas duas branches.

## Pendências
- Cliente gráfico: mira e acerto na cabeça/cauda, F3+B, flecha e dardo vistos no couro, dino montado (o jogador não
  acerta a própria montaria), Better Combat (resolve o alvo por `getEntity`, então só acerta o corpo).
- Pernas e asas (Pteranodonte) não viraram partes: ficam sob a caixa do corpo ou fora dela. Espécies não refeitas não
  têm partes. Inclinação de voo/nado não move as partes.

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
