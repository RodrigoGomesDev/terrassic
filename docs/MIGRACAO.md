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

## Ecossistema vivo (06/11/2026)

Pedido do Rodrigo: "sinto que o ecossistema precisa ser melhorado, migração de dinos, etc".

| O quê | Como |
|---|---|
| Pasto que acaba | Pastar come a planta de verdade (`DinosaurEntity.grazeEat`): capim e samambaia somem; onde não sobra nenhuma, às vezes a grama vira terra (o vanilla espalha a grama de volta com o tempo). Folhas e mudas só são mordiscadas. Com a regra `mobGriefing`. Assim a fome passa a empurrar a migração ("escassez"). |
| Destino escolhido | Oito lugares na metade da rosa dos ventos da estação, de 64 a 112 blocos; vence o que tem mais o que comer em volta, com bônus para água a 12 blocos. |
| Fila | Quem escolhe o destino lidera; os outros andam atrás do animal à frente, no espaço do próprio corpo: de longe a manada vira uma coluna. A sentinela do Edmontossauro não fica de vigia enquanto a manada anda. |
| Trilhas | Bichos grandes em migração gastam a grama em caminho (`dirt_path`) de vez em quando (`mobGriefing`): as rotas que se repetem aparecem no mapa. |
| Predadores na sombra | `ShadowHerdGoal`: um predador grande que não está caçando, com uma manada em migração a 64 blocos, acompanha pelo flanco a 24-32 blocos. Quando a fome volta, o alvo é o fraco primeiro (filhote ou ferido abaixo de 60%, `PredatorDinosaur`). Um predador saciado à distância não dispara o alarme da manada; só o que caça ou chega a 12 blocos. |
| Manadas de passagem | `EcoSpawner`: uma em seis manadas de herbívoros já nasce migrando, com o destino do outro lado do jogador: a migração é vista acontecendo. |
| Bebedouro ao entardecer | `WaterholeGoal`: uma vez por dia, no fim da tarde, o herbívoro adulto vai à água mais próxima (até 48 blocos) e bebe; a manada vai junto. As manadas de um vale se encontram nos mesmos lagos, e os predadores sabem disso. |

Teste no cliente (`BehaviorTest`, fase `eco`): seis Edmontossauros comeram o capim em volta, migraram 90 blocos em fila deixando 42 blocos de trilha, um T. rex saciado os acompanhou de longe sem alarme constante, e ao entardecer foram ao lago.

## O que falta

- Pastagem consumida de verdade (grama vira terra ao ser pastada demais) para o gatilho de escassez pesar mais (v0.8, com o tipo de mundo).
- Rotas de migração fixas por bioma e trilhas batidas (estruturas v0.8).
- Migração de pterossauros (bandos no céu) na revisão de voo da v0.4.
