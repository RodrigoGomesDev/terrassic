# Domesticação por nocaute (plano)

Status: planejado para a **v0.7** (ver `docs/ROSTER.md`, linha 127). Pedido do Rodrigo em 24/10/2026: domar por nocaute como no ARK, com animação de nocaute nos bichos. Nada disto entra na v0.3; os modelos novos já saem com a animação `knocked_out` pronta.

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
| `knocked_out` | em loop: deitada de lado, respiração lenta | **pronta nos 13 dinossauros terrestres** (falta Pteranodonte e Mosassauro) |
| `wake` | uma vez: levanta e sacode a cabeça | a fazer |
| `eat` | uma vez: come da mão ou do chão | a fazer |
| `tame` | uma vez: reação de domada | a fazer |
| `beg` | em loop: filhote pedindo comida | a fazer |
| `hatch` | uma vez: sai do ovo (quem nasce vivo usa a de nascimento) | a fazer |

Todo arquétipo novo (terópode, ceratopsiano, saurópode, anquilossauro, pterossauro, réptil marinho) sai com `knocked_out`. As espécies antigas que ainda não usam arquétipo ganham a animação quando migrarem.

## Realismo
O nocaute é mecânica de jogo, não comportamento real. O que segue a vida real: tamanho, dieta, comida preferida, comportamento em bando e onde cada animal vive. Animais muito grandes precisam de mais torpor, e predadores de topo acordam mais rápido.
