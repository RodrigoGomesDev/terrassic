# Migração (v0.6, fase 69)

Manadas selvagens de herbívoros não ficam para sempre no mesmo vale: quando o pasto acaba, ou de tempos em tempos,
partem juntas para longe. Fecha os sistemas da v0.6 (cadeia alimentar, carcaças, fome e sono, bandos, ninhos,
migração, carga, coleta, sela-plataforma).

| Regra | Como |
|---|---|
| Quem | `MigrateGoal` (prioridade 8, antes do `FollowHerdGoal`) em todo `HerbivoreDinosaur` selvagem adulto, acordado, sem alvo, sem montaria e sem agressor recente. Predadores não migram (seguem a caça); pterossauros e répteis marinhos têm IA própria. |
| Gatilho | Sorteio a cada ~1 min (1/1200 ticks). Parte se está com fome (< 50) e não há pasto ao alcance (`grazeNearby`), ou, sem motivo, em 1 de 20 sorteios (~20 min). |
| Destino | 64 a 96 blocos na **direção da estação**: um ângulo tirado do dia do mundo (estações de 6 dias) e da espécie. Todas as manadas de Edmontosaurus do mundo derivam para o mesmo lado durante 6 dias, depois mudam. Altura pelo heightmap; só se o chunk está carregado. |
| Manada junta | Quem parte passa o destino (`setMigrationTarget`) aos adultos selvagens da espécie a 24 blocos, que partem no mesmo tick; filhotes seguem os pais (`FollowParentGoal`). Não é salvo: manada recarregada se assenta onde está. |
| Caminho | O pathfinder não vê 80 blocos: o goal anda em pontos de 12 blocos na direção do destino, e se não há caminho tenta 40° para um lado e para o outro. Desiste depois de 5 tentativas bloqueadas (rio largo, paredão) ou 3 min, ou a 6 blocos do destino. |
| Interrupções | Dormir, alvo, montaria ou ser ferido param a migração; a manada retoma no próximo sorteio. |

## O que falta

- Pastagem consumida de verdade (grama vira terra ao ser pastada demais) para o gatilho de escassez pesar mais (v0.8, com o tipo de mundo).
- Rotas de migração fixas por bioma e trilhas batidas (estruturas v0.8).
- Migração de pterossauros (bandos no céu) na revisão de voo da v0.4.
