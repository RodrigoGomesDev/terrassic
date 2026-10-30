# Níveis no estilo ARK (v0.13)

Pedido do Rodrigo no plano da versão estável (30/10/2026): cada criatura nasce com um nível e pontos de status
sorteados; domada, ganha níveis bônus pela eficiência da doma e continua subindo com experiência, e o dono gasta os
pontos na tela do dino. A média dos selvagens fica igual à força de antes, então o jogo não fica mais difícil no
geral: o que muda é que agora há bichos fracos, comuns e raros muito fortes.

Código: `entity/DinoLevels.java` (nível, pontos, curva, XP) e a seção "levels" de `entity/DinosaurEntity.java`
(modificadores de atributo, doma, XP, nome). Tela: `client/DinoScreen.java`.

## Status

| Status | O que faz | Selvagem, por ponto | Domado, por ponto |
|---|---|---|---|
| Vida | Vida máxima | +3% | +4% |
| Ataque | Dano da mordida, chifrada, pisão | +2,5% | +2% |
| Velocidade | Velocidade andando, correndo e voando | 0 (como no ARK) | +1% |
| Fome | Tamanho do estômago: demora mais a ter fome | +2% | +5% |
| Torpor | Resistência ao nocaute | +3% | 0 (só conta selvagem) |

Os pontos selvagens são escalados para que um nível 40 tenha exatamente os valores da tabela da espécie
(`gen_species.py`), que é o jogo de antes dos níveis: valor = (1 + p × pontos) / (1 + p × pontos médios do nível 40).
Os pontos que o dono gasta somam por cima, em porcentagem do valor selvagem.

Resultado médio (simulado): nível 1 com uns 70% da vida e 80% do dano; nível 150 com quase o dobro da vida
(1,8 a 2x) e uma vez e meia o dano.

**Stamina e Peso**, que estão no plano, entram junto com os sistemas em que agem (stamina de montaria e peso da
carga). Até lá não aparecem, para nenhum ponto ser gasto num status que não faz nada.

## Pesos por espécie

Cada nível acima do 1 vira um ponto sorteado entre Vida, Ataque, Fome e Torpor, com pesos tirados da vida e do
dano da tabela:

| Tipo | Como é reconhecido | Vida | Ataque | Fome | Torpor |
|---|---|---|---|---|---|
| Gigantes | vida ≥ 200 ou dano/vida < 0,07 (saurópodes, hadrossauros, Archelon) | 4 | 1 | 2 | 1 |
| Caçadores ágeis | dano/vida ≥ 0,14 (raptores, Dilophosaurus, Troodon, peixes) | 2,5 | 3 | 1 | 1,5 |
| Os demais | (T. rex, ceratopsídeos, anquilossauros, pterossauros) | 3 | 2 | 1,5 | 1,5 |

## Nascimento

- O nível vem de uma curva (Kumaraswamy a = 0,8, b = 1,65) em que metade dos selvagens fica até o nível 40, um
  quarto passa de 75 e uns 5% passam de 120, até o máximo da regra (padrão 150).
- **Níveis por distância** (regra, ligada por padrão): até 500 blocos do ponto de nascimento do mundo o máximo é 30,
  subindo em linha reta até o máximo da regra a 3.000 blocos. A curva encolhe junto, então perto do início quase
  tudo é fraco. Não é do ARK; deixa o começo justo num mundo de Minecraft.
- Filhotes chocados e nascidos de cruza sorteiam o nível como os selvagens, no primeiro tick.

## Doma

- Níveis bônus = metade do nível selvagem × eficiência (sorteados nos status como os selvagens).
- Nocaute: a eficiência já existia (cai 10% a cada golpe no bicho desmaiado). Substitui o antigo bônus de +20% de
  vida; quem foi domado antes da v0.13 mantém o bônus antigo.
- Comida na mão: eficiência 100% (o bicho não apanhou).
- Filhotes (ovo ou comida de filhote): sem bônus.
- A Lupa mostra, no bicho desmaiado, "Eficiência: 84% (+14 níveis)".

## Experiência do domado

Até 75 níveis a mais; cada um é 1 ponto para o dono gastar na tela do dino (Vida, Ataque, Velocidade ou Fome).

| Fonte | XP |
|---|---|
| Matar uma criatura ou mob (montado ou não) | a vida máxima da vítima |
| Levar o dono montado | 1 a cada 8 blocos |
| Coletar itens no baú de carga | 1 a cada 4 itens |

O próximo nível pede 10 + 5 × (níveis já ganhos + 1) de XP: 15 no primeiro, 385 no último, uns 15 mil no total.
A regra "XP dos domesticados" multiplica tudo (0 = não sobem). Ao subir, o dono vê na barra de ação "X subiu para o
nível N: ponto novo na tela do dino", com o som de nível.

## Onde aparece

- No nome: "Velociraptor · Nv 34" (Lupa de Campo, painel de montaria, mensagens, plaquinha de nome).
- Tela do dino: coluna da direita com o nível, a barra de XP (passe o mouse para ver os números), os pontos e cada
  status em % do valor normal da espécie, com um "+" ao lado quando há ponto para gastar. Passar o mouse no nome do
  status explica o que ele faz.
- Lupa: "Pontos para distribuir: N" nos seus dinos com pontos sobrando.

## Regras de mundo novas (docs/REGRAS.md)

| Regra | Padrão | Faixa |
|---|---|---|
| Nível máximo selvagem | 150 | 30 a 300 |
| XP dos domesticados | 1,0 | 0 a 10 |
| Níveis por distância | 1 (ligada) | 0 ou 1 |

## Mundos antigos

Uma criatura salva antes da v0.13 recebe um nível na primeira vez que carrega: as selvagens sorteiam; as domadas
ficam com a distribuição média do nível 40, ou seja, com os mesmos status de antes, sem perder nada.

## Fica para depois

- Herança dos pais, mutação e impressão (cuidar do filhote): precisam que o ovo guarde os pais, entram com a criação.
- Stamina e Peso (ver acima).
- Mostrar o nível no novo HUD (estudo de HUD separado).
