# Domesticação por nocaute (plano)

Status: **implementado** (torpor, nocaute, alimentar derrubado, eficiência, acordar; zarabatana, dardo de narcótico e erva sonífera; ver "O que já está no jogo"). Era: planejado para a **v0.7** (ver `docs/ROSTER.md`, linha 127). Pedido do Rodrigo em 24/10/2026: domar por nocaute como no ARK, com animação de nocaute nos bichos. Nada disto entra na v0.3; os modelos novos já saem com a animação `knocked_out` pronta.

## O que já está no jogo
- **Torpor** (só em criaturas selvagens): máximo = a vida máxima (mínimo 10). Clava: 2,5x o dano em torpor e metade do
  dano. Punho: 2 + 2x o dano. Lâminas e pontas: só 10% do dano. Dardo de narcótico: 14 + 6% do máximo, ferida mínima.
  Acordada, o torpor cai 2% do máximo por segundo.
- **Nocaute** com o torpor cheio: pose `knocked_out`, sem IA nem movimento (`isImmobile`). Dorme ~2,5 min com a barra
  cheia (1,5 min para quem morde com 8 ou mais de dano); erva sonífera (+35%) e dardos recarregam sem ferir.
- **Alimentar**: clique com a comida da espécie; carne nobre vale 2 porções; estudada no Guia vale +25%; a regra
  "velocidade de domesticação" multiplica. Meta: vida máxima / 8 porções (de 3 a 30). Clique com outra coisa mostra
  torpor, progresso e eficiência na barra de ação.
- **Eficiência**: começa em 100%; cada ferida enquanto dorme tira 10 (mínimo 20). Domada, ganha até +20% de vida
  máxima (modificador permanente) e acorda com a vida cheia, animação `tame`.
- **Acordar** sem terminar: animação `wake`, metade do progresso some, e quem morde parte para cima de quem a derrubou.
- Os répteis marinhos que não se domavam (Mosassauro, Tilossauro...) agora se domam só assim; domados seguem o dono,
  descansam quando mandados e o defendem.
- Receitas: zarabatana = 3 juncos na diagonal; erva sonífera (2) = lírio-d'água do Cretáceo + orelha-de-pau;
  dardo de narcótico (4) = sílex + erva sonífera + pena.
- Ainda não: boleadeira, inventário de comida da criatura derrubada e a dificuldade de nocaute no Guia (arquivos do Guia
  reservados ao Codex).

## As três formas de domar
| Forma | Para quem | Como |
|---|---|---|
| **Comida** | Pequenos e herbívoros mansos | Dar a comida certa na mão até domar (já existe). |
| **Ovo** | Quem ainda não tem nocaute | Chocar o ovo ou criar o filhote (já existe). |
| **Nocaute** | Grandes predadores, gigantes e criaturas bravas | Derrubar sem matar, manter dormindo e alimentar enquanto dorme. |

Quem tem nocaute continua podendo ser criado desde o ovo. O nocaute é o caminho mais rápido, e mais arriscado.

## Como funciona o nocaute
1. **Torpor.** Cada criatura tem uma barra de torpor, com máximo proporcional à vida e ao tamanho. Golpes contundentes (clava, punho, boleadeira) e dardos de narcótico enchem o torpor; dano cortante quase não enche. O torpor cai devagar sozinho.
2. **Nocaute.** Com o torpor cheio, a criatura cai: animação `knocked_out` (deitada de lado, pernas moles, respiração lenta). Ela não se move, não ataca e não faz barulho de ameaça.
3. **Alimentar.** Com a criatura derrubada, clique com a comida preferida: ela come do inventário dela (como no ARK, abre um inventário pequeno de comida). Cada porção soma progresso de domesticação; a comida preferida soma mais.
4. **Manter dormindo.** Erva sonífera (narcótico fraco) ou dardo recarregam o torpor. Se o torpor zerar, ela acorda brava (animação `wake`) e o progresso cai pela metade.
5. **Eficiência.** Cada golpe que a criatura leva durante a domesticação baixa a eficiência, e uma domada com eficiência alta ganha bônus de vida e de dano. Bater demais custa.
6. **Domada.** No fim, acorda já domada (animação `wake`), com o nome e o sexo de sempre.

Regra 0 do mod continua valendo: nada é automático, o jogador escolhe quando e se vai domar.

## Itens (v0.7)
- **Clava** (já existe) e **punho**: torpor por golpe, pouco dano.
- **Zarabatana** e **dardo de narcótico**: torpor à distância. Dardo feito com veneno de planta e espinho.
- **Boleadeira**: prende as pernas por alguns segundos (a criatura fica lenta), com pouco torpor.
- **Erva sonífera**: comida que recarrega torpor de uma criatura derrubada.
- No Caderno de Campo, o Guia mostra a comida preferida e a dificuldade de nocaute de cada espécie quando ela é "estudada".

## Animações (por arquétipo de modelo)
Mesmos nomes da seção "Domesticação: animações e telas" do `docs/ROSTER.md`. Todo modelo novo sai com todas.

| Animação | Tipo | Estado |
|---|---|---|
| `knockout` | uma vez: cambaleia e tomba | a fazer |
| `knocked_out` | em loop: deitada de lado, respiração lenta | **pronta nas 18 espécies** (o Pteranodonte migrou para o arquétipo de pterossauro e o Mosassauro ganhou a pose deitado de lado, de barbatanas recolhidas, que na água vira boiar). A altura é calibrada por medida (`rig.ground_lift`), então nenhum corpo afunda nem flutua |
| `wake` | uma vez: levanta da pose de nocaute e sacode a cabeça | **pronta** onde há `knocked_out` (`rig.add_wake`) |
| `eat` | uma vez: abaixa a cabeça até a comida e mastiga 4 vezes | **pronta** (`rig.add_actions`) |
| `tame` | uma vez: sacode o corpo, cabeça pra cima e boca aberta, cauda abanando | **pronta** (`rig.add_actions`) |
| `beg` | em loop: olha para cima, inclina a cabeça de um lado para o outro, pulinho | **pronta** (`rig.add_actions`) |
| `hatch` | uma vez: sai do ovo (quem nasce vivo usa a de nascimento) | a fazer |

Todo arquétipo novo (terópode, ceratopsiano, saurópode, anquilossauro, pterossauro, réptil marinho) sai com `knocked_out`, `wake`, `eat`, `beg` e `tame` (o `rig.add_knockout` adiciona as cinco; o Java ainda não as dispara, isso entra com o sistema na v0.7). As espécies antigas que ainda não usam arquétipo ganham a animação quando migrarem.

## Realismo
O nocaute é mecânica de jogo, não comportamento real. O que segue a vida real: tamanho, dieta, comida preferida, comportamento em bando e onde cada animal vive. Animais muito grandes precisam de mais torpor, e predadores de topo acordam mais rápido.
