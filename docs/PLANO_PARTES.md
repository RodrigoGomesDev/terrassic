# Partes de acerto (1.7) — plano para a próxima sessão

Pedido do Rodrigo (04/11/2026), a partir da sugestão da comunidade sobre hitboxes. Status: **a implementar**.

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
