# Feedback de jogador e a 1.7 (04/11/2026)

Feedback recebido pelo Rodrigo (em inglês, de um jogador) e o que a 1.7 fez com cada ponto. Código compilado contra o
jar do Minecraft mapeado da loom-cache (sem as bibliotecas de terceiros: os erros restantes são os mesmos da `main`
antes da mudança); **build completa com Gradle e teste no jogo ainda pendentes**.

| # | Feedback | O que mudou |
|---|----------|-------------|
| 1 | Não dá para ver onde estão os dinos; o apito só funciona a uns 50 blocos | Apito: 24 → **96 blocos** (`Whistle.RANGE`). Lista **Meus dinos** (agachado + H, ou a tecla "Meus dinos", sem tecla padrão, ou `/terrassic dinos`): todo domado com distância, direção, coordenadas, se espera ali e quando foi visto. **Rastrear** põe uma seta no alto da tela (`client/DinoTracker`). As posições ficam salvas no mundo (`entity/TamedRegistry`, `data/terrassic_tamed.dat`): um domado carregado atualiza a cada 5 s; sai da lista ao morrer. |
| 2 | Dinos não se defendem de bichos de outros mods, nem domados por ordem | A proteção de "Caçar bichos de outros mods" = 0 vale só para a **caça**. O dino briga com o bicho que o atacou, que atacou o dono, que o dono atacou ou que o dono mandou atacar (`DinosaurEntity.provokes`, 30 s renovados a cada golpe). Mob de outro mod registrado como monstro conta como hostil mesmo sem `Enemy`. A etiqueta `terrassic:protected` (Pokémon, NPCs) continua absoluta. |
| 3 | Clava forte demais (velocidade 0,20) e atordoamento longo (uns 20 s) | Clava de Cauda 0,6 → **0,2** ataques/s; Clava de Osso 0,8 → **0,25**. Nocaute: 150 s (90 s nos que mordem forte) → **20 s** (15 s), regra nova "Duração do nocaute" (10 a 300 s). Enquanto o jogador dá comida o bicho não acorda (2 s por porção), então uma doma longa termina. O alfa continua com 60 s. |
| 4 | Dinos nascem demais: pelo menos 3x mais raros que os animais normais, carnívoros ainda mais | "Dinos no mundo normal" 0,35 → **0,25** (um dino para três bichos do Minecraft; mundos salvos com 0,35 migram, `Rules.VERSION` 3). Regra nova **"Carnívoros"** (0,4): o peso de cada carnívoro vezes 0,4 no spawn natural e no EcoSpawner, também nos biomas do Cretáceo. Carnívoro = dieta carnívora ou piscívora com 4+ de dano (`DinosaurEntity.isHunter`). |
| 5 | Pouca vida | Vida **x2** (x1,5 abaixo de 20) em `gen_species.health_of`; a fauna de caça (Leptoceratops, Mesodma, Vegavis, Basilemys, Enchodus, Lepisosteus) fica como estava. Animais salvos passam ao valor novo ao carregar (`refreshBaseHealth`, mantendo a proporção da vida). O torpor cresce junto (é a vida máxima). |
| 6 | Domar fácil demais: uma pilha de carne para carnívoros pequenos, várias para os grandes | Acabou o sorteio 1 em 4 por porção. Toda doma acumula progresso até a meta (`DinosaurEntity.foodGoal`): carnívoro = 64 por cada 100 de vida base, de 1 a 5 pilhas (Velociraptor 1, Carnotauro 2, Giganotossauro 3, T. rex 4); os outros = vida/6, de 6 a 64 porções. Filhote = um quarto. Alfa x1,5 (antes x3). Carne nobre conta 2, espécie estudada +25%, regra "Velocidade de domesticação" multiplica. A Lupa mostra quantas porções faltam e a barra de doma. |
| + | Seção com todos os dinos e seção de domesticação no Guia | Guia de Bolso: tópicos **Os dinossauros** (toda espécie ativa com ovo, dieta, tamanho real, se monta, como doma, quanta comida e os itens que come; `PocketGuideScreen.SpeciesEntry`) e **Domesticação**. Começo, Armas, Nocaute e Ordens atualizados. |
| + | Armas compatíveis com Better Combat | `data/terrassic/weapon_attributes/`: Clava de Osso = maça, Clava de Cauda = martelo (duas mãos), lanças = lança, faca e adaga = adaga, machadinha = machado (tabela `BETTER_COMBAT` em `gen_resources.py`). Sem o Better Combat os arquivos são ignorados. |

## Pendências
- `./gradlew build` dos dois loaders e `check_spawn_budget.py` (pedem JDK 21 e as dependências do Gradle).
- No jogo: lista Meus dinos e a seta (Fabric e Forge), defesa contra mobs de outros mods, doma com pilhas segurando o botão,
  nocaute de 20 s, a nova vida nos combates, o Guia de Bolso com as 13 espécies, e o Better Combat com as clavas.
- Densidade: medir com `/terrassic fauna` num mundo normal (a meta é ~1 dino para 3 animais do Minecraft).

## Testes no servidor real (04/11/2026, Mac do Rodrigo)
`./gradlew build` passou nos dois loaders (regressões de pesquisa incluídas). Servidor dedicado descartável + cliente de
protocolo real (`tools/validation/feedback17_regression.py`, 23 verificações): Fabric 23/23; Forge 22/23 na última
rodada, e a que faltou (o Tricerátops não chegou a morder o lobo em 20 s depois de aceitar a ordem) virou só registro:
o teste agora confere que a ordem é aceita contra o bicho protegido, que é o que a 1.7 muda. Medido: acorda 19,6 s
depois do nocaute da Clava de Cauda; 64ª carne doma o Velociraptor; 10ª semente doma o Gallimimus.
`knockout_regression.py` 18/18 e `dart_regression.py` 25/25 nos dois loaders, ajustados para a 1.7 (regra
`knockout_seconds 300` nos mundos de teste, metas de comida novas, ferida medida contra a vida anterior).
Telas (Meus dinos, seta, Guia de Bolso) ainda sem revisão no jogo: o cliente não pôde ser controlado desta sessão.

## Ainda na 1.7 (pedido do Rodrigo, 04/11): partes de acerto e porte para 1.21.1
Sugestão da comunidade: as hitboxes não batem com os modelos (T. rex 13 m numa caixa 2,6 x 4,8). Decisão: **partes de
acerto como no Ender Dragon**, com dano diferente por parte: **cabeça 125%, corpo 100%, cauda e pernas 75%**. A caixa
de colisão fica como está (andar na mata, caminho). Plano em `docs/PLANO_PARTES.md`. A `mc/1.21.1` também recebe a 1.7.
