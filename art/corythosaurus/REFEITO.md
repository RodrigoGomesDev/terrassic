# Coritossauro refeito (1.11.0)

Estudo aprovado: `docs/estudos/15_HERBIVOROS_1_11.md` (seção Coritossauro e "Respostas do Rodrigo", 10/11/2026). Segundo
dos quatro herbívoros da 1.11.0, depois do Maiassaura, no padrão da 1.10 (estudo 14: 16 texels por bloco, pele `skin2`,
cabeça do padrão v3 desenhada a partir da anatomia dele, pescoço e cauda em peças que afinam e se sobrepõem).

A personalidade dele, separada dos três hadrossauros já refeitos: o Parassaurolofo é o tubo para trás, ruivo, de
bandeira de alarme; o Edmontossauro, a cabeça longa e chata, a sentinela e os sacos do focinho; o Maiassaura, o calombo
baixo e a colônia de ninhos. O Coritossauro é **o elmo em pé, o pescoço alto, o azul-fumaça listrado e a voz e o ouvido
da mata**.

## Modelo (`tools/modelgen/handmade/corythosaurus/cory.py`)

- **9 m** (Benson et al. 2012; o topo, resposta do Rodrigo), desenhado a 16,94 px/m: 165 px de comprimento, escala
  0,925 no jogo, **17,3 texels por bloco**. Hitbox 1,9 x 3,4 m (2,01 x 3,60 blocos); filhote a 0,18 do adulto.
- **O elmo (assinatura, ~25% maior que o osso):** placa alta, fina dos lados (3 a 2 px de largura) e em **meia-lua**:
  a frente sobe íngreme do focinho e a de trás desce sobre o crânio (Brown 1914). Feito em camadas que nascem uma dentro
  da outra (`adult_crest`); no macho uma borda de cima a mais (`male_display`): **o elmo do macho é maior**, como
  decidido no estudo. O filhote não tem elmo, só a testa alta (`young_crest`).
- **Padrão v3, desenhado só para ele:** olho **grande** (bicho de penumbra) embaixo da parte de trás do elmo, sem
  sobrancelha, íris **cinza-prateada clara** com pupila redonda larga e brilho alto, borda escura de órbita e um **anel
  de pele clara** em volta, mais largo embaixo; a borda do bico é **reta e lisa** (uma linha clara contínua, sem os
  dentículos do Maiassaura); focinho **curto e estreito**, bico raso de queratina ardósia; o lábio sobe em linha até
  debaixo do elmo; rosto em escamas pequenas e angulosas; narina em fenda no alto do bico. No elmo, **mosaico de placas
  poligonais** que diminuem para a borda, quilha lisa de queratina escura em cima, gasta e mais clara na frente.
- **Postura:** alto na cernelha, com a **crista dos espinhos neurais** (a corcova baixa) dos ombros à cauda; **pescoço
  levado alto** em duas peças que afinam e se sobrepõem, a cabeça com o elmo acima da manada; pernas longas (o mais
  rápido dos três); cauda funda em quatro peças.
- **Cor "azul-fumaça"** (aprovada): corpo ardósia-azulado fosco, dorso e crista mais escuros, **listras verticais
  claras e finas** nos flancos e nas coxas (bongo e ocapi), barriga cinza-névoa, patas escuras, frente do pescoço
  cinza; escamas poligonais em mosaico no flanco baixo e na cauda (Brown 1916). **Elmo terracota** no macho (o campo desce
  da quilha e se desfaz em pontos antes do olho); na **fêmea** o elmo é ardósia com barras claras finas.
- **Filhote:** pele própria (`corythosaurus_baby.png`, fumaça mais clara, listras mais fortes), sem elmo, cabeça 1,2x.
- **Sela de Mata** (`CORYTHOSAURUS_SADDLE`): baixa e estreita, almofada de pano de casca batida com costura verde-musgo
  e franja de tiras tingidas, assento baixo de couro escuro sem patilha alta, pega de osso na frente para se abaixar
  sob os galhos.

## Medidas (build)

| | valor |
|---|---|
| QA do motor | 0 coplanares, 0 pixel ruim, 0 pose fora do chão, 37 animações |
| densidade | 17,30 tx/bloco (16 ± 2) |
| headcheck macho | cabeça 25 cores, 0,44 vizinhos que mudam (1,95x o corpo, 0,22); borda do bico 7 texels de cada lado; íris 9, brilho 1; acento 112 |
| headcheck fêmea | 0,43 (1,94x o corpo) |
| uniquecheck (limite 0,78) | o mais perto: Majungassauro 0,62, Deinossuco 0,61, Espinossauro 0,60, Velociraptor 0,59, Albertossauro 0,58 (Parassaurolofo, Edmontossauro e Maiassaura abaixo disso) |
| colourcheck --remade | macho: Giganotossauro 11,4, Galimimo 15,3, Quetzalcoatlus 15,3 (o estudo previa 12,6) |

## Animações (`coryanims.py`, 37)

Padrão: idle, walk, run (duas patas), swim, turn_left/right, walk_tired, idle_tired, eat, graze, drink, attack (encurralado:
golpe de lado com o elmo e o ombro, aos 0,5 s), kick_back, body_shove, hurt, death, knockout, knocked_out, wake, sit,
sleep, wake_sleep, lie_down, get_up, beg, tame, hatch. Próprias: **deep_call** (o chamado grave pelo elmo: pescoço
esticado, elmo alto, **bico fechado**, três batidas lentas da garganta), **alarm** (o sopro grave e duro meio empinado),
call e answer (curtos), **listen** (para, ergue a cabeça e vira o elmo devagar de um lado e do outro), **nap** (o cochilo
em pé: o elmo desce, uma pata de trás descansa), **fruit_pick** (empina nas patas de trás e arranca o fruto com a cabeça
de lado), **pluck** (puxa bagas do arbusto com a cabeça de lado), **helmet_display** (de perfil, a cabeça erguida
balançando devagar), **wade** (anda na água rasa de cabeça alta). Sem trio de duelo. GIFs em `previews/animacoes/`.

## Comportamento (`common/.../entity/Corythosaurine.java`)

- **O chamado grave** (`deep_call`, a voz no tom mais grave, ouvida a 64 blocos): o **perdido volta** (quem não tem
  outro da espécie a 16 blocos anda até o que chamou, em pernas de 14 blocos); os **herbívoros a 16 blocos se acalmam**
  (largam pânico e alvo, regeneram um pouco: a mecânica `calm` que já existia, agora presa ao chamado e nunca com um
  predador por perto); alguns respondem (`answer`). Domado, o chamado ainda acalma o curral.
- **O alarme** (`alarm`): todo Coritossauro selvagem a 64 blocos, a manada e as manadas vizinhas, acorda e foge da
  ameaça, mesmo quem não a vê.
- **O ouvido da mata:** ouve um predador em movimento (caçando, com alvo ou correndo perto) a 24 blocos **sem linha de
  visão**, para e escuta (`listen`) e dá o alarme 2 s depois; se vê, dá o alarme na hora. Dormindo, também acorda pelo que
  ouve.
- **Catemeral:** não dorme a noite inteira; cochila em turnos de 1 a 3 minutos (`isSleepTime` é o cochilo), acordado 3
  a 6 minutos de dia e 1 a 3 à noite; de dia cochila em pé (`nap`), à noite deitado (`sleep`). Só cochila se outro da
  manada a 24 blocos está acordado; senão "fica de guarda". Sempre há um acordado.
- **Fruta na mata:** com fome procura arbusto de bagas maduro a 10 blocos, vai até ele e arranca (`pluck`; o arbusto
  volta ao estágio 1); sob folhas altas empina (`fruit_pick`). Domado, fruta (maçã, bagas, bagas brilhantes) doma 1,5x e
  trigo 0,75x.
- **O elmo de perfil:** dois machos adultos a 10 blocos ficam de lado um para o outro e mostram o elmo (`helmet_display`)
  por 10 a 15 s; quem tem menos vida (ou por sorte) baixa a cabeça e sai 14 blocos. Diante de um predador menor que ele
  que não o caça, o macho também se mostra.
- Arisco: foge junto; só revida encurralado (coice e quadrilada da `HerbivoreDinosaur`). Mata e beira de pântano
  (`WORLD`: forest, swamp), manadas de 4 a 8. A montaria mais rápida dos hadrossauros (1,25).
- Log: linhas `[cory] ...`.

## Ninho (`tools/spritegen/cory_extras.py`)

Especulativo (não se conhece ovo de Coritossauro): uma cova rasa no chão da mata **entre raízes**, cinco ovos **quase
redondos** (como os do *Hypacrosaurus*, Horner & Currie 1994) em anel, cinza-azulados claros com pintas ardósia, meio
cobertos de **agulhas de conífera** e gravetos. No estágio 2 um ovo racha e o bico estreito do filhote aparece.

## Teste no jogo

Cliente Fabric com som zerado, sempre dentro de `caffeinate -dimsu` (11/11/2026). Fase nova `cory` na `BehaviorTest`
(também na lista `regressao`), com as checagens `cory: ...` em `tools/validation/behavior_regression.py`.

Fase `cory` sozinha (rodada final, 12 de 12 OK):

| | resultado |
|---|---|
| tamanho | hitbox 2,01 x 3,60 blocos; filhote a 0,18 (0,36 x 0,65) |
| cochilos de dia | 4 de 4 cochilaram em 60 s, no máximo 2 ao mesmo tempo, sempre 2 acordados (os de dia em pé) |
| cochilos de noite | 4 de 4 cochilaram, no máximo 2 juntos, sempre 2 acordados (deitados) |
| ouvido | 3 de 3 ouviram o Velociraptor atrás de um muro de pedra (sem linha de visão), escutaram e a manada fugiu inteira |
| chamado a 50 blocos | a outra manada, cochilando a 50 blocos e sem ver nada, acordou e fugiu inteira (3 de 3) |
| reagrupar | o perdido a 44 blocos chegou a 9 do que chamou em 15 s |
| calma | o Edmontossauro assustado largou o pânico e ganhou regeneração |
| fruta | o arbusto maduro foi colhido em 6 s (voltou ao estágio 1) |
| elmo | dois machos de perfil em 1 s; no fim um baixou a cabeça e saiu (de 6 a 14,8 blocos) |

Achados e corrigidos no caminho: o perdido não voltava de 44 blocos (o caminho só é achado dentro do alcance de
seguir: agora anda em pernas de 14 blocos e a perna dele vence as metas da manada); dois decidiam cochilar no mesmo
segundo e a manada inteira dormia (quem acabou de decidir já conta como cochilando).

Lote pedido (`jaws,gaits,look,cory,herdmove,babystay`): mandíbula do Coritossauro abre 7 graus, pernas 1.500 graus/s no
arquivo e 74 graus por tique no jogo, olhar, filhote junto da mãe; tudo OK para ele. Falharam só medidas antigas sem
relação: mandíbula sem medida de Protocerátopo, Velociraptor e Deinossuco e pernas sem medida de Protocerátopo e
Anquilossauro (as mesmas da rodada do Maiassaura), e uma checagem da manada de Edmontossauros (`herdmove`) que oscila de
rodada em rodada: "sem andar no lugar" com o `HerdMoveGoal` a 5 e 6 (limite 4); rodada na base sem o Coritossauro
(stash) falhou a "manada junta" com o mesmo teste, então é instabilidade do teste, não deste trabalho.

Fotos do jogo em `previews/jogo/`. Folha das cabeças ao lado do Parassaurolofo, do Edmontossauro e do Maiassaura:
`previews/cabecas_hadrossauros.png` e `_perfil.png`. Leitura honesta: das quatro é a única com uma placa em pé sobre a
cabeça e a única azul; de longe a silhueta (pescoço alto e elmo) se separa das outras três, e o elmo terracota do macho
é o que se vê primeiro. A cabeça de perfil ainda é bem de blocos (o elmo em camadas), e o elmo do macho, visto de
frente, pode lembrar um gorro; se o Rodrigo quiser o elmo mais fino ou mais curvo, é mexer só na tabela `HELMET`.

## Pendente

- Vozes próprias (usa a do camelo; o chamado grave é a mesma voz num tom mais grave e com alcance de 64 blocos).
- A foto do filhote sozinho (`behavior_cory_calf`) saiu vazia, como a do Maiassaura: precisa de outro ângulo.
- Rodada num mundo gerado (`Playtest`) com mata, pântano e predadores de verdade.
- O `art/corythosaurus/` não tem `.bbmodel` novo (as peles e o geo exportados são os do modelo novo).
