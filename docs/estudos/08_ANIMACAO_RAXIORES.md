# Estudo: por que as animações do Raxiores parecem tão vivas (06/11/2026)

Pedido do Rodrigo: "estude o mod Raxiores... as animações dele dos dinos são extremamente boas, queria algo assim;
implemente somente no T. rex por hora".

Fonte: "Raxiores Of Raxiore" v0.6 (1.20.1 Forge, de The_Raxiores; animadores creditados Ari Cat e Dinosaur Man),
CurseForge, projeto 1231016. O jar foi aberto só para medir a técnica, numa pasta temporária fora do repositório. Nada
dele foi copiado: nem modelo, nem textura, nem curva. Licença deles: All Rights Reserved. Aqui ficam só as conclusões e
os números que guiaram o nosso jeito.

## Como é feito

1. **Poucas chaves, desenhadas à mão.** As animações do T. rex deles são keyframes do formato do próprio Minecraft
   (`AnimationDefinition`, exportado do Blockbench pelo MCreator), todos com Catmull-Rom, de **2 a 5 chaves por segundo
   por osso**. O nosso exporta 10 a 20 chaves por segundo e mesmo assim parecia mais duro: a qualidade não vem da
   densidade, vem de **onde** as poses estão e de **quanto** o corpo se mexe.
2. **Camadas somadas com peso.** A cada quadro o modelo soma: parado, andar e correr com pesos que dependem da
   velocidade (nunca troca de uma vez), mais as animações de ação.
3. **Poses estáticas guiadas por "seguidores".** Há poses de um quadro só (pescoço para cima, para baixo, de lado;
   cauda dobrada 1 a 4; corpo torcido). O código calcula alvos a cada tick e um seguidor persegue cada alvo 40% por
   tick; o peso de cada pose é o seguidor. Resultado: a cabeça vira para o alvo com atraso macio, o corpo torce na
   curva, nada estala.
4. **A cauda é uma corrente no mundo.** Cada segmento é um ponto no plano do chão que persegue o anterior a 3 blocos,
   com um ângulo máximo; o desvio entre onde ele está e onde estaria rígido vira o peso da pose "cauda dobrada". Quando
   o bicho vira, a cauda fica para trás e depois alcança, sem nenhuma chave desenhada para isso.
5. **Girar no lugar tem animação própria** (passos para a esquerda e para a direita). O bicho não gira deslizando os
   pés.

## O que medimos (caminhada do T. rex, amplitude de cada lado)

| | Raxiores | o nosso antes |
|---|---|---|
| rolar do quadril | 11,4° | 2,4° |
| giro do quadril | 6,8° | 2,2° |
| peito girando contra o quadril | 7,8° | não havia |
| cauda, da base à ponta | 6,4° → 25,8° | 2,7° → 6,0° |
| cabeça | 3 a 4°, estabilizada | ~1° |
| coxa (passo) | 37° | 45° (as nossas pernas já eram boas, plantadas por IK) |
| dedos no impulso | 22° | 22° |

O nosso tinha boas pernas e um tronco parado: o peso não passava de um pé para o outro e a cauda quase não respondia.

## O que fizemos no T. rex (só nele, por enquanto)

Animações (`tools/modelgen/handmade/tyrannosaurus/rexanims.py`, `gait2`, `idle`, `turn`):
- o quadril rola ~8° sobre o pé de apoio e gira ~5° com a perna que passa; a queda depois de cada pisada é rápida e a
  subida lenta;
- o pescoço gira e rola contra o quadril e o crânio estabiliza o olhar, um pouco atrasado;
- a cauda é um chicote: o balanço cresce da base à ponta (1 a 4 vezes) e cada segmento atrasa ~0,13 do ciclo;
- cada coxa cancela o rolar e o giro do quadril (o pé apoiado escorrega só 1,2 px de lado) e abre um pouco no passo;
- os bracinhos pendem e atrasam; os dedos dobram no impulso;
- parado: o peso passa de um pé para o outro, a respiração é funda e a cauda faz um S lento;
- `turn_left` / `turn_right`: o T. rex dá passos ao girar parado, a cabeça entra na curva primeiro e a cauda vai para o
  outro lado.

Camada em tempo real (`entity/LivelyMotion`, aplicada em `client/DinoGeoModel`): cauda em mola (inércia que cresce até
a ponta, mola amortecida, cada segmento empurra o seguinte), corpo inclinando para dentro da curva e pescoço olhando para
ela, e a taxa de giro suavizada que escolhe os passos de girar no lugar (`ApexTheropod.turnInPlace`). Liga só onde
`livelyMotion()` é verdadeiro: hoje, o T. rex.

## Próximos

Se o Rodrigo aprovar no jogo: levar `gait2`, a camada viva e os passos de giro para o Carnotauro e o Giganotossauro
(mesmos ossos), depois para os quadrúpedes (os quatro pés precisam de outra corrente de peso).
