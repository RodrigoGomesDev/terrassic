# Estudo: um ecossistema divertido como o do ARK, e que faça sentido (07/11/2026)

Pedido do Rodrigo (06/11, noite): "quero um ESTUDO COMPLETO de como podemos melhorar esse ecossistema para ser divertido
que nem ARK e claro fazendo sentido, estude o sistema de ARK e como podemos configurar o spawn dos dinos, onde eles
ficam, como se portam as manadas... à noite carnívoro e herbívoro dormem um do lado do outro". Estudo na 1.9.1; a
**1.9.5 é a versão do ecossistema**.

Fontes: wiki oficial do ARK (ark.wiki.gg) para números de spawn, temperamento e níveis; relatos de jogadores (Steam,
Reddit, Dododex) marcados como tal; Saurian, Path of Titans, The Isle, Beasts of Bermuda, Jurassic World Evolution e
o mod Primal Fear para comparação. Nada copiado; só as ideias e as medidas.

## 1. Como o ARK monta o mundo

**Progressão por região, não por nível.** O mapa é dividido em zonas por bioma (praia, campo, selva, sequoias, pântano,
montanha, neve, cavernas, oceano raso e fundo). Cada zona tem a sua lista de grupos (espécie, peso, tamanho do grupo:
"Dodo 1-5") e um número desejado de criaturas. O nível dos selvagens não depende da zona: o perigo vem de **quais**
espécies nascem ali e **quantas por grupo**. Contas sobre os pesos da The Island: praia 85-90% presas; campo 25-30%
predadores; montanha ~75% agressivos. A mesma espécie muda de grupo conforme a zona (Raptor 1-2 na selva, 3-6 na
montanha; Rex sozinho no campo, em dupla na montanha). Cada espécie tem um teto por região (Giganotossauro 0,01 do
número da zona, Dodo 0,5). Servidores ajustam tudo por arquivo (ConfigAdd/Override/SubtractNPCSpawnEntriesContainer,
DinoSpawnWeightMultipliers, NPCReplacements, DinoCountMultiplier) e limpam os selvagens de tempos em tempos.

**Alfas**: raros, muito mais fortes (~15x a vida), com aura vermelha, só no interior e na montanha.

## 2. Por que o caos do ARK é divertido: temperamentos com regras

- **Dócil** (revida só se provocado), **arisco** (foge e grita), **pavio curto** (avisa alguns segundos, depois
  ataca), **territorial**, **agressivo**, **oportunista** (pega os fracos), **paciente** (espera e dá o bote),
  **noturno**.
- O Rex ataca quase tudo, menos outros predadores de topo. Predadores selvagens brigam entre si: é a cena que os
  jogadores mais citam como "a melhor parte".
- Bandos com líder (Raptor: o líder dá bônus ao bando; Allossauro: bandos de 3 que se juntam).
- Manadas que se defendem (Tricerátops ganha "Rivalidade" com predador grande por perto e defende o ninho); o
  Parassauro dá alarme para a área; a mãe de um filhote luta mesmo sendo de espécie que foge; pegar um ovo enfurece os
  adultos em volta.
- Carnívoros comem o que matam. Crítica comum: o predador continua caçando depois de comer (há mod só para isso).
- **Sono**: no ARK os selvagens não dormem (só os noturnos/diurnos marcados, como o Megalossauro, que dorme de dia e é
  muito mais fraco acordado fora de hora). Ou seja, o que temos (todos dormindo lado a lado) é um problema nosso, e dá
  para fazer **melhor que o ARK**.

Jogos mais realistas: Saurian (fome, sede, cheiro, rastros), Path of Titans (IA que dorme quando cansada, bichos que
fogem para tocas), The Isle (manadas que se movem por dieta, zonas de patrulha, bebedouros e ninhais fixos), Beasts of
Bermuda (incêndios, enchentes, migração), JWE (brigas de dominância que não matam). Críticas ao ARK que evitamos: mapa
"de arena", espécies amontoadas, ilhas só de presas ou só de predadores.

## 3. Como o Terrassic está hoje (código, 06/11)

- **Spawn**: duas fontes. O vanilla por bioma (`ModSpawns`, populações que ficam para sempre) e o `EcoSpawner`
  (errantes: 18 por jogador em terra num raio de 80, 12 no mar, 4 no céu; somem a 96 blocos; carnívoros x0,4). Não há
  zona de perigo, teto por região nem proporção predador/presa por área; a fauna "segue o jogador" e troca a cada ida
  e volta.
- **Caça**: fome < 85 e não saciado. Matilhas puxam os vizinhos; `ShadowHerdGoal` segue manadas. **Defeito**: a regra
  "o mais fraco primeiro" exige `isPrey` e quase todos os grandes excluem filhotes do `isPrey`: o filhote nunca é
  escolhido. Rex, Giga, Tarbo e Carcharo não têm limite de tamanho de presa.
- **Herbívoros**: lutadores não fogem de predador, só revidam; fugitivos fogem de qualquer predador adulto a 14
  blocos, mesmo saciado ou dormindo. Edmontossauro tem sentinela e alarme (mas não à noite).
- **Sono**: `DinoSleepGoal` adormece onde estiver, sem olhar em volta, e só acorda com dano ou alvo. O bebedouro do
  entardecer termina pouco antes do sono: as manadas dormem na beira d'água, com os predadores ao lado.
- **Sem território nem casa**: nenhum animal tem área de vida; predadores de espécies diferentes não se evitam.
- **Migração** não é salva (para ao recarregar).

## 4. O plano da 1.9.5: o ecossistema

Ordem pensada para cada etapa já mudar o que o jogador vê.

### 4.1 Noite que faz sentido (o exemplo do Rodrigo)
- Cada espécie com ciclo próprio: diurna, noturna (Troodon, Mesodma) ou crepuscular (Velociraptor ativo ao amanhecer
  e ao entardecer, cochilo no meio do dia, como na 1.9.1).
- **Herbívoro só dorme seguro**: sem predador acordado ou com fome a 32 blocos; dorme no meio da manada, com uma
  sentinela acordada por turno (a do Edmontossauro passa a valer à noite); antes de dormir a manada se afasta do
  predador e da beira d'água.
- **Predador dorme saciado e longe das manadas**, de preferência na mata ou junto a uma parede de pedra; com fome, à
  noite ele patrulha.
- Quem dorme **acorda** com dano, alarme da manada, jogador correndo perto ou predador caçando a 10 blocos.
- Noturnos ficam mais fortes e rápidos à noite; um diurno acordado de noite fica mais lento (como o Megalossauro).

### 4.2 Cadeia alimentar e temperamentos
- Temperamento por espécie na tabela de `gen_species` (dócil, arisco, pavio curto, territorial, agressivo,
  oportunista, paciente), com os textos no Guia.
- **Presa do tamanho certo**: até ~1,2x o predador (ou o bando somado); topo não caça topo, disputa território ou
  carniça sem matar (o duelo com rendição já existe). Conserta o "mais fraco primeiro" (filhotes e feridos).
- **Come o que mata**: o predador fica na carcaça comendo e depois saciado por minutos (na 1.9.1 já vale para os
  marinhos). Perseguição com limite de distância e tempo.
- Manadas lutadoras ganham "Rivalidade" com predador grande por perto e cercam os filhotes; a mãe defende o filhote;
  mexer num ovo enfurece os adultos.
- Pavio curto: aviso (rugido, exibição) antes de atacar o jogador que chega perto.

### 4.3 Onde cada um vive (spawn por zona)
- Cada habitat (`terrassic:habitat/*`) ganha uma meta de proporção de predadores: margem e área de chegada até 15%,
  planícies 20-30%, mata fechada, pântano e montanha 50-75%. Quanto mais longe da Cratera de Chegada, grupos maiores e
  mais alfas (alfas de outras espécies quando as peles forem aprovadas).
- Tamanho de grupo por zona (o mesmo raptor em 1-2 na mata, 3-5 na montanha) e teto por espécie numa região.
- **População estável**: os errantes deixam de sumir e reaparecer a cada ida e volta; uma região guarda quem vive
  nela (contagem por região salva), e o respawn repõe aos poucos o que morreu.
- Tudo configurável por arquivo (como os containers do ARK): `config/terrassic-world.json` com pesos, grupos, metas
  de proporção e tetos por habitat, além das regras atuais.

### 4.4 Território, casas e rotas
- Área de vida: cada grupo tem um centro (ninho, bebedouro, toca) e volta para ele; predadores marcam território e
  disputam a borda (rugido, exibição, duelo com rendição).
- Bebedouros e ninhais fixos por região; rotas de migração lentas entre pastos, salvas no mundo.
- Bandos com líder visível (Raptor, Dakotaraptor) e bandos que se juntam.

### 4.5 Como vamos medir (BehaviorTest)
Fases novas no teste em cliente: "noite" (onde cada um dorme, distâncias predador/presa às 0h), "cadeia" (quem ataca
quem num vale povoado por 10 minutos), "zonas" (proporção de predadores por habitat em 512x512), "estável" (a mesma
população depois de ir e voltar).

## 5. Andamento da 1.9.5 (branch `eco/1.9.5`, 07/11/2026)

Medido na `BehaviorTest` (fases `night`, `weak`), cliente Fabric, som zerado:

| Feito | Medida |
|---|---|
| Herbívoro só dorme sem predador acordado a 32 blocos nem dormindo a 28; antes se afasta com a manada (`ai/SafeRestGoal`); acorda com predador caçando perto | dormindo a 34,9-38,9 blocos do predador em média (1.9.1: 25,4); o mais perto a 28,2 (1.9.1: 17,7) |
| Predador com muita fome (abaixo de 40) não dorme, patrulha | — |
| Sentinela do Edmontossauro à noite, passa o turno acordando outro | 2 de 6 acordados com a manada dormindo |
| O mais fraco primeiro: filhote de herbívoro do tamanho do predador ou menor | T. rex com fome escolheu o filhote em 3 de 3 |
| Presa até 1,25x a largura do predador (2x em bando); topo não caça topo | T. rex com fome ignorou o Argentinossauro adulto |
| Spawn por zona (margem 15%, planície 25%, mata fechada/pântano/montanha 60% de predadores), grupos até 1,5x longe da Cratera | 300 escolhas seguidas por zona: planície 4% -> 20%, mata fechada 4% -> 19% (falta predador médio na lista desses biomas; os raros ficam no teto de 2 por região) |

Já existia e foi conferido: predador terrestre come a carcaça e fica saciado de 5 a 7 minutos (`EatCarcassGoal`).

Próximos (na ordem do plano): temperamentos na tabela de espécies e Rivalidade das manadas lutadoras (4.2); spawn por
população estável (4.3; as metas por zona estão feitas, números aprovados pelo Rodrigo em 07/11); predadores médios nas listas da mata fechada e do pântano para a meta de 60% ser alcançável; território,
bebedouros e ninhais fixos, rotas salvas (4.4).

## 6. Comportamento (pedido do Rodrigo, 07/11: "o dino agressivo vem pra cima de mim, mas com pouca vida tenta fugir...")

Do ARK (wiki oficial, notas de patch; o que é relato de jogador está marcado no estudo de apoio): a fuga é um traço por
espécie, sem limiar publicado; o gatilho mais comum é o torpor, não a vida. Os patches corrigiram bichos que fugiam para
a água e se afogavam: a fuga precisa escolher a direção. Fogem: Gallimimo (no primeiro tiro), Dodo (com os vizinhos),
Daeodon (se cura sozinho, 0,5%/s), Carnotauro (de predador maior); nunca fogem: alfas, Giganotossauro, Titanoboa, quem
defende ovo. Não há número público para o alcance de agressão nem para a desistência da perseguição: os números
abaixo são nossos. Bandos dão bônus por membro (Compy +30% de dano por membro até 8; líder do Raptor +25%); pegar um
ovo enfurece os adultos em volta; o rugido do Yutirano dá medo (corre a esmo 20 s) a quem é menor.

| Comportamento | Regra no Terrassic | Estado |
|---|---|---|
| Ferido foge | herbívoro de manada abaixo de 35%, predador abaixo de 25%, os grandes abaixo de 15%; nunca o alfa, a mãe com filhote a 16 blocos nem quem está em duelo (o duelo tem a rendição); foge 24-32 blocos pelo melhor de 8 rumos, nunca para água funda nem penhasco (`ai/FleeHurtGoal`) | feito: Carnotauro a 10% fugiu para 68 blocos em 10 s |
| Recupera e volta | o selvagem cura 0,5% da vida por segundo depois de 10 s sem dano; só volta a atacar acima de 60% | feito: 11% -> 70% em 100 s |
| Desiste da perseguição | 48 blocos de onde começou ou 20 s sem acertar; o mesmo alvo fica de lado por 30 s (os anfíbios seguem na água) | feito: Velociraptor desistiu da presa inalcançável |
| Aviso antes de atacar | pavio curto: exibição/rugido de 3 s quando o jogador chega a 8 blocos | próximo |
| Alcance por temperamento | agressivo 24, caçador pequeno (menos de 1 bloco de largura) 16; agachado -20% (a visibilidade do vanilla); só para notar o jogador, a perseguição segue o alcance da espécie; o território dos herbívoros já tinha o -20% agachado | feito na 1.10.1: Carnotauro nota a 20 e não a 26 (1.9.5: notava a 26), agachado a 20 passa; Velociraptor nota a 14 e não a 18, agachado a 14 passa |
| Chamado de ajuda | manada 16 blocos, bando de predador 24: os lutadores vão no agressor, os corredores e os filhotes correm dele; substitui o alertOthers do vanilla (que usava o alcance de seguir inteiro) | feito na 1.10.1: Tricerátopo a 6 e 12 investem, a 22 fica (1.9.5: o de 22 também ia); Velociraptor a 10 e 20 vêm, a 30 fica |
| Ovo pego e mãe | ovo selvagem pego enfurece os adultos da espécie a 24 blocos por 60 s (voltam ao ladrão se perdem o alvo); quem não luta foge; filhote fica a 6 blocos do adulto mais perto da espécie e foge de predador ou jogador a 8 (para o outro lado da mãe; quem segura a comida dele pode chegar) | feito na 1.10.1: Tricerátopo a 22 do ovo vem (1.9.5: só até 20), a raiva acaba aos 60 s; filhote posto a 14 da mãe volta para 1,7 (1.9.5: ficou a 14); Velociraptor a 4: o filhote foi para 8,2 dele e 3,1 da mãe (1.9.5: ficou a 4) |
| Bônus de bando | +15% de dano e +5% de resistência por membro, até +4 | próximo |
| Medo pelo rugido | rugido do apex assusta por 6-10 s quem tem menos da metade da largura dele, a 24 blocos (40 no rugido alto); nunca o alfa, a mesma espécie, a mãe com filhote, os domados | feito na 1.10.1: Velociraptor a 10 fugiu, Tricerátopo a 12 ficou, Velociraptor a 32 só fugiu do rugido alto |

## 7. Locomoção (pedido do Rodrigo, 07/11: "subir e descer blocos, nadar, parece mod antigo")

Estudo de código de mods modernos com licença conferida (Fossils & Archeology MIT; Ice and Fire LGPL-3.0; Twilight
Forest LGPL-2.1+; Naturalist MIT; Cobblemon MPL-2.0; Alex's Mobs/Caves e Mowzie's Mobs só como ideia): tudo será
escrito por nós. O que trava a fluidez hoje no Terrassic:
1. nadadores sem inclinação do corpo (só a cabeça aponta para baixo);
2. terrestres pequenos e médios quicam na água (o vanilla `FloatGoal`; a mola de flutuação só existe no Deinossuco e no
   Espinossauro);
3. o degrau sobe a caixa inteira num tick e o modelo vai junto, duro;
4. o corpo copia o rumo de cada nó do caminho (zigue-zague nas quinas); a cabeça de todos gira como a de um vanilla;
5. navegação e nós do vanilla (deslocados para +X/+Z nos largos, sem atalho em linha reta).

Plano: **Fluidez 1** (cliente, risco baixo): inclinação dos nadadores pelo vetor de velocidade, flutuação suave para
todos os terrestres, mola visual do degrau (o modelo sobe com atraso amortecido e o corpo inclina um pouco),
controle do corpo pelo rumo real com giro limitado pelo tamanho. **Fluidez 2**: inclinação do corpo pelo terreno (4
amostras), navegação própria com atalho por varredura e nós centrados, passos sincronizados com a animação (som,
poeira, tremor nos gigantes), abrir caminho entre folhas para os grandes.

## 8. Andamento da 1.10.1 (branch `comport/1.10.1`, 08/11/2026)

Os quatro sistemas pedidos, cada um atrás de uma chave (`entity/Behaviour`: `TERRASSIC_OLD_ROAR`, `_AGGRO`, `_EGG`, `_HELP`,
`_BABY`, `_HERD`, `_QUIRKS`, `_FEET`, `_POPULATION` = 1 traz de volta a 1.9.5). As chaves são lidas também durante o jogo,
então cada fase da `BehaviorTest` mede a 1.9.5 e a nova na mesma rodada. Cada sistema escreve uma linha `[eco] ...` no log
do jogo quando dispara (para o playtest em mundo gerado contar): `roar scare`, `aggro`, `egg rage`, `help call`,
`baby flee`, `herd leader`, `quirk`, `region loss`, `region refill`.

| Sistema | Regra | Medida (cliente Fabric, som zerado) |
|---|---|---|
| Medo do rugido e alcance | seção 6 acima | seção 6 acima (fases `roarfear`, `aggro`) |
| Ovo, ajuda, filhotes | seção 6 acima | seção 6 acima (fases `eggrage`, `helpcall`, `babystay`) |
| Manada anda junta | um líder por grupo (o menor id entre os adultos selvagens da classe a 24 blocos) passeia, com metade da frequência; os outros não passeiam sozinhos: vão para o destino do líder mais um lugar próprio (ângulo fixo pelo UUID, distância pelo espaçamento) (`ai/HerdStrollGoal`, `ai/HerdMoveGoal`); o `FollowHerdGoal` continua separando | 6 Edmontossauros em 90 s: espalhamento médio 3,8 blocos (1.9.5: 6,5), a manada andou 11 blocos junta (1.9.5: 3) |
| Manias de repouso | parado no chão, sem alvo, a cada 40-90 s uma de {sniff, shake, yawn, stretch, look_back, look_side, scratch, preen, snort} que o rig tiver; fora das classes que já têm os próprios gestos (os apex, Raptor, Dakotaraptor, Terizinossauro, pterossauros, Paquicefalossauro, Galimimo, Didelfodonte) | hoje só o Anquilossauro ganha (snort): os outros refeitos ou já têm gestos próprios ou não têm essas animações no rig. 3 Anquilossauros parados, 120 s: 9 manias |
| Pés no chão | cada pé (os dois de trás, e os da frente nos quadrúpedes: Tricerátopo, Estiracossauro, Anquilossauro, Protocerátopo, Edmontossauro, Parassaurolofo, Deinossuco) é procurado onde o modelo o desenhou no quadro anterior (matriz do osso no `DinosaurRenderer.renderFinal`); tira-se a inclinação do corpo e a mola do degrau; o que sobra: o corpo desce até o pé mais baixo (no máximo meio bloco) e as outras pernas dobram; some com a caminhada rápida | diferença entre a altura desenhada de cada pé e o chão debaixo dele, num degrau de 1 bloco: T. rex de lado 1,05 -> 0,29; Tricerátopo de lado 0,98 -> 0,59; Tricerátopo de frente 0,97 -> 0,49. Com os limites pequenos o degrau inteiro não fecha: cai pela metade |
| População estável | o mundo em células de 128 blocos (`world/RegionPopulation`, salvo em `terrassic_population.dat`); cada morte de bicho de terra selvagem conta como perda da célula; o EcoSpawner só põe na célula até a cota dela (15 na densidade 1, vezes as regras) menos a perda, e a perda cura um terço da cota por dia de jogo; errante que some quando o jogador vai embora não é perda | cota 5 (bioma fora do Cretáceo): região caçada, jogador chega: 0 postos (1.9.5: 6, acima da cota); depois de 1 dia, 1 na célula; depois de 3 dias, 3; jogador vai a 600 blocos e volta duas vezes: 4 na célula, nunca acima da cota |

Não foi feito: os temperamentos na tabela de espécies (4.2), a Rivalidade das manadas, o aviso do pavio curto e os pés
durante a caminhada normal (só parado e devagar, por segurança contra o giro de ossos da 1.9.1).
