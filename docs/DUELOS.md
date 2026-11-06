# Duelos entre dinossauros (06/11/2026)

Pedido do Rodrigo: "quero que melhore as batalhas entre dinos também" (com um vídeo do Raxiores de referência).
O Raxiores luta como um jogo de luta: guarda, paciência, aparar, guarda que quebra, engalfinhar, agarrar. Aqui, com
o nosso jeito e começando pelo T. rex (`ApexBiteGoal`, `ApexTheropod`, animações em `rexduel.py`):

| Fase | O que acontece |
|---|---|
| Encarar | A ~8 blocos de um rival grande (outro T. rex, ou um herbívoro que briga: Tricerátops, Anquilossauro, Estiracossauro...), para, encara e ameaça (`threat`). Entra em guarda (`guard`: agachado, cabeça baixa, rosnando). |
| Circular | Anda de lado em volta do rival (`strafe_left` / `strafe_right`), de frente para ele, mantendo a distância, enquanto a paciência (35 a 80 ticks) se esgota. |
| Atacar | Contra outro T. rex: finta (`feint`, morde o ar e recua) ou parte para a mordida; colado, empurra com o ombro (`shove`). Contra chifres: espera o flanco, finta enquanto o chifre aponta para ele; se o rival investe, revida na hora. |
| Bloquear | Em duelo, levando a mordida de frente, apara 40% das vezes com o pescoço (`block`): o dano cai a 25% e o atacante cambaleia (`recoil`, 18 ticks sem golpes). |
| Render-se | Abaixo de 30% da vida (50% numa disputa de território) o perdedor se rende (`submit`: cabeça e cauda baixas, vira) e foge; não volta a atacar o vencedor por 2 minutos. O vencedor solta o rugido alto. |
| Território | Dois machos selvagens de tamanho quase igual (até 3%) não desviam um do outro: uma vez em três brigam até um se render. |

Teste no cliente (`BehaviorTest`, fase `rexduel`): dois T. rex encararam, circularam, fintaram, apararam e se morderam
por 30 s; um T. rex contra um Tricerátops terminou com os dois pela metade da vida.

Próximos: o mesmo para o Carnotauro e o Giganotossauro (mesmos ossos); engalfinhar chifre com chifre nos ceratopsianos.
