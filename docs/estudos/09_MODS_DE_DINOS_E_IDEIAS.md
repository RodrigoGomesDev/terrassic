# Estudo: sete mods de dinossauros e três ideias de mundo (06/11/2026)

Pedido do Rodrigo: estudar Primal Frontier Legacy, Jurassic Saga, Raxiores Of Raxiore, The Dawn Era, JurassicWorldCraft,
Prehistoric Epochs: Chronicles e Dinosaur Add-On; e pensar três ideias para o futuro: rochas em forma de crânio gigante,
o habitat dos pterossauros em montanhas altas e templos de outros humanos que cruzaram o Cretáceo.

Método: página de cada projeto. Nos quatro mods Java, o jar foi aberto numa pasta temporária fora do repositório só para
medir a técnica (quantas animações, quantas chaves por segundo, que curvas, que camadas em tempo real). Nada foi copiado:
todos são "All Rights Reserved". Os modelos do Jurassic Saga vêm cifrados e não foram abertos. Os dois de Bedrock (um
pago) foram vistos só pelas páginas.

## 1. Cada um, em uma linha

| Projeto | Plataforma e base | O que tem de melhor | O que levar para o Terrassic |
|---|---|---|---|
| **Raxiores Of Raxiore** | 1.20.1 Forge, MCreator, animação do próprio Minecraft | animação: pouca chave e muito corpo; rugido em berros com tremor; cauda em corrente no mundo | já levado ao T. rex (estudo 08) |
| **Jurassic Saga** | 1.20.1 e 1.21.1, Forge, NeoForge e Fabric, Travelers Lib | camadas em tempo real em todo bicho: **IK das pernas no terreno**, inclinação, olhar repartido pela corrente, buffer de cauda; parque, DNA, híbridos, estresse e fugas | o IK no terreno (pés em degraus e encostas); estresse que muda o comportamento |
| **Primal Frontier (Legacy e o remake)** | 1.20.1 Forge, GeckoLib | 39 animações para uma criatura só, com **variantes de cansaço** (parado, andar e morder cansado) e transições separadas (deitar, levantar, adormecer, acordar, aparecer); curva por chave (seno) | estado de cansaço com animações próprias; transições entre estados |
| **The Dawn Era** | 1.20.1 a 1.20.4, Forge, AstemirLib | 15 bichos, 1,39 milhão de downloads; seis estados de descanso (deitar, descansar, adormecer, dormir, acordar, levantar), **quatro ataques** por predador; "ruínas de civilizações passadas" | as transições de descanso; ataques variados; ruínas (casa com a ideia dos templos) |
| **JurassicWorldCraft** | 1.20.1 Forge, beta | metabolismo, dieta e fases de crescimento; animação ainda mínima | pouco além do que já temos |
| **Prehistoric Epochs: Chronicles** | Bedrock, Marketplace (830 moedas), Next Studio | sobrevivência mais dura com **humanos antigos** no mundo; 4,4 estrelas em mais de mil notas | humanos do passado como conteúdo de exploração (templos) |
| **Dinosaur Add-On** | Bedrock, TryzzMC | 16 dinos, todos domáveis, criáveis e quase todos montáveis; "amigo das conquistas" = não usa recursos experimentais | simplicidade de entrada: montar logo, sela simples (nós já temos o Guia de Bolso) |

## 2. O que separa os bons dos medianos

1. **Camadas em tempo real por cima da animação.** Os dois melhores (Raxiores e Jurassic Saga) chegaram, cada um por um
   caminho, ao mesmo conjunto: cabeça e pescoço seguindo o olhar com atraso, repartidos pela corrente (corpo, peito,
   pescoço, cabeça), cauda que fica para trás nas curvas, corpo que inclina. O Jurassic Saga ainda põe os **pés no
   chão de verdade**: IK de bípede que pousa cada pé no bloco embaixo dele e abaixa o quadril (escadas, encostas).
   Temos as três primeiras no T. rex desde hoje (`LivelyMotion`); falta o IK no terreno.
2. **Estados com transição.** Ninguém bom passa de "em pé" para "deitado" de uma vez: deitar, descansar, adormecer,
   dormir, acordar, levantar são seis animações no Dawn Era. Nós temos "sentar" e "dormir" em laço, e as transições
   só existem para acordar.
3. **Variação.** Quatro ataques diferentes (Dawn Era), dois golpes de garra e uma carga (Primal Frontier), vários gestos
   parados. Um bicho que repete a mesma mordida parece máquina.
4. **O corpo conta o estado.** O Primal Frontier tem andar, parar e morder **cansado**. É a ideia do nosso ofegar levada
   a sério: estado de cansaço que troca as animações.
5. **Curvas.** O Primal Frontier escolhe a curva por chave (seno de entrada, saída, as duas), o Raxiores e o Dawn Era
   usam Catmull-Rom. O que importa não é qual, é ter poucas chaves bem postas e nunca ligar/desligar de uma vez.

## 3. O que adotar, em ordem

1. **IK das pernas no terreno** (bípedes primeiro): cada pé desce até o bloco de baixo, o quadril abaixa pelo pé mais
   baixo, as pernas dobram. Resolve dinos flutuando em degraus e encostas. Camada em `LivelyMotion` + `DinoGeoModel`.
2. **Transições de descanso** no T. rex: `lie_down`, `get_up`, `fall_asleep`, além do `wake_sleep` que já existe.
3. **Mais ataques** no T. rex: mordida baixa (alvo pequeno), mordida de lado, empurrão de cabeça; sorteados.
4. **Cansaço**: depois de correr muito, andar e morder ficam pesados (variantes `walk_tired`, `attack_tired`), e o
   ofegar já existe.
5. Depois de aprovado no T. rex, levar a camada viva e estas animações ao Carnotauro e ao Giganotossauro (mesmos
   ossos), e o IK para todo bípede.

## 4. Ideias de mundo

### 4.1 Rochas-crânio ("Crânios Gigantes")

Não crânios de verdade: **formações de rocha que, por coincidência, lembram ossos**. O jogador reconhece a forma de longe
e se pergunta se é só pedra.

- **Como gerar, com arte nossa:** pegar os nossos próprios modelos (o crânio do T. rex, o pescoço do Alamossauro, a
  caixa torácica do Mossassauro), voxelizar a malha em escala 15 a 25x e erodir com ruído (bordas comidas, buracos,
  rachaduras), em giz e calcário (blocos que já temos), meio enterrada e tomada por vegetação. Assim a forma é nossa e
  a rocha é a do Cretáceo do mod.
- **Variações:** crânio de terópode (a boca vira caverna, com água e um ninho dentro), arco de pescoço de saurópode, um
  "costelar" (fileira de costelas como arcos naturais), espinha de réptil marinho saindo de uma praia.
- **Jogo:** pontos de referência no mapa, abrigo, cavernas com loot e ninhos; raros (um a cada 1.500 blocos) para
  continuarem especiais; o Sítio Fossilífero que já existe pode nascer ao pé de uma delas.
- **Fase sugerida:** junto das próximas estruturas (`gen_structures.py`), primeiro o crânio, depois o pescoço.

### 4.2 Habitat dos pterossauros: Picos de Calcário

Montanhas de **torres de calcário** (carste), altas e estreitas, com plataformas em vários níveis: os pterossauros
vivem e pousam ali.

- **Bioma novo** (`gen_world.py`): "Picos de Calcário", torres de 40 a 90 blocos geradas por ruído em colunas, cada
  uma com patamares e beirais a cada 8 a 15 blocos, musgo e samambaias pendentes, cachoeiras finas e um lago ao pé.
- **Colônia:** ninhos de Pteranodonte e de Quetzalcoatlus nos patamares (o ninho-bloco que já existe), o
  `ColonyGoal` e o `FishingFlightGoal` usando o lago, o spawn dos voadores puxado para o bioma, pousos nos beirais.
- **Jogo:** escalar para roubar ovos é um desafio de verdade (altura, adultos defendendo); o Quetzalcoatlus caça a pé
  no capim da base.
- **Encaixe:** os 11 biomas do Cretáceo já existem; este seria o 12º.

### 4.3 Templos dos Andarilhos

Outros humanos atravessaram a Fenda **em outras épocas** e ficaram no Cretáceo; deixaram construções.

- **Quem:** povos diferentes, cada um com o seu estilo e material (nada copiado de culturas reais): por exemplo, um
  povo da Idade do Bronze que ergueu um templo dentro de uma estátua de tartaruga gigante (a Basilemys do mod), uma
  expedição do século XIX que deixou um forte de madeira e diários, um grupo mais antigo que entalhou pinturas (as
  pinturas rupestres que já temos).
- **Jogo, que é o principal:** salas com quebra-cabeças simples (alavancas, placas de pressão, portas de pedra),
  armadilhas (as estacas que já temos), um guardião (um dino que fez do templo o ninho), loot próprio (ferramentas de
  bronze, mapas para outras estruturas, fragmentos de âmbar).
- **História, só se ligada:** com o modo história desligado (padrão, regra da v0.10), os templos são exploração
  pura; ligado, cada povo deixa páginas que contam a sua travessia e conversam com o diário da Katarina. Todo texto
  passa por `Story.enabled()`.
- **Fase sugerida:** o templo-tartaruga primeiro (é a imagem mais forte), depois o forte da expedição.

## Fontes

- Raxiores Of Raxiore: https://www.curseforge.com/minecraft/mc-mods/raxiores-of-raxiore
- Jurassic Saga: https://www.curseforge.com/minecraft/mc-mods/jurassic-saga (código: github.com/Jurassic-Saga-Team/JurassicSaga)
- Primal Frontier Legacy: https://www.curseforge.com/minecraft/mc-mods/primal-frontier-legacy
- The Dawn Era: https://www.curseforge.com/minecraft/mc-mods/the-dawn-era
- JurassicWorldCraft: https://www.curseforge.com/minecraft/mc-mods/jurassicworldcraft
- Prehistoric Epochs: Chronicles: https://www.bedrockexplorer.com/marketplace-offer/next-studio/prehistoric-epochs-chronicles
- Dinosaur Add-On: https://www.curseforge.com/minecraft-bedrock/addons/dinosaur-add-on
