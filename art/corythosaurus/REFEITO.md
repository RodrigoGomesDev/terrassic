# Coritossauro refeito (1.11.0; modelo v4 de 16/11/2026)

Estudo aprovado: `docs/estudos/15_HERBIVOROS_1_11.md` (seção Coritossauro e "Respostas do Rodrigo", 10/11/2026). Segundo
dos quatro herbívoros da 1.11.0, depois do Maiassaura, no padrão da 1.10 (estudo 14: 16 texels por bloco, pele `skin2`,
cabeça do padrão v3 desenhada a partir da anatomia dele, pescoço e cauda em peças que afinam e se sobrepõem).

A personalidade dele, separada dos três hadrossauros já refeitos: o Parassaurolofo é o tubo para trás, ruivo, de
bandeira de alarme; o Edmontossauro, a cabeça longa e chata, a sentinela e os sacos do focinho; o Maiassaura, o calombo
baixo e a colônia de ninhos. O Coritossauro é **o elmo em pé, o pescoço alto, o azul-fumaça listrado e a voz e o ouvido
da mata**.

## Modelo v4, "o pavão da mata" (16/11/2026, `tools/modelgen/handmade/corythosaurus/cory.py`)

O v3 de 11/11 foi recusado ("os modelos tão muito padrão... parece sempre o mais do mesmo"): todo bico-de-pato saía
com a mesma silhueta e só a cabeça mudava. O v4 começou pela silhueta em preto (`_silhuetas/`) e segue a variante
**B, "leque alto"**, escolhida pelo Rodrigo, osso por osso (os mesmos pivôs e ângulos da blocagem, em metros x 16,94).

- **Postura:** tronco empinado 18 graus no osso `body` sobre pernas da frente longas (girafa), pescoço quase vertical
  em três peças (`neck1..3`: 62, 8 e -20 graus), a cabeça pequena levada nivelada no alto, cauda alta e dura.
  9,4 m de altura até a ponta do leque; 163 px de comprimento (9 m), 17,1 texels por bloco.
- **O leque (elmo):** cinco lâminas varridas para trás como crista de cacatua, muito maior que o osso, cada uma um osso
  próprio (`fan0..fan4` sob `adult_crest`), fundas o bastante para se encaixarem numa forma só; o macho tem mais duas
  lâminas longas (`fan_m0`, `fan_m1` sob `male_display`): **o leque dele é o maior**. O filhote não tem leque, só a
  testa alta (`young_crest`).
- **Vela:** os espinhos neurais altos desenhados como uma vela de lâminas inclinadas para trás, da cernelha (atrás da
  sela) à base da cauda, a mais alta sobre o quadril.
- **Pele desenhada, não gerada:** azul-fumaça com o dorso e a vela ardósia-breu; **barras brancas largas de ocapi** na
  anca, nas coxas e nos braços, descendo mais finas pelas canelas e antebraços (tabelas `RUMP_BARS`, `THIGH_BARS`,
  `ARM_BARS`); mãos e pés mais escuros com escudos na frente; a garganta no próprio azul do pescoço, com dobras (sem
  placa clara solta entre a mandíbula e o peito); escama fina só como um passo de tom, no flanco baixo e na cauda. No
  leque a cor corre do centro para fora como uma forma só: no macho, terracota escurecendo da raiz até uma borda clara,
  com a raque clara no meio de cada lâmina; na fêmea, ardósia com **arcos claros** que atravessam todas as lâminas.
- Cabeça do padrão v3 mantida (bico estreito de borda reta e lisa, olho grande de íris prateada no anel de pele clara,
  máscara escura do olho para trás, bochechas e mandíbula).
- **Sela de Mata:** entre a base do pescoço e a primeira lâmina da vela, calçada na frente para o assento ficar
  nivelado no dorso inclinado (por isso não precisa de `ridden_idle`; testado, dobrava demais as pernas da frente).

## Medidas (build v4)

| | valor |
|---|---|
| QA do motor | 0 coplanares, 0 pixel ruim, 0 pose fora do chão, 37 animações |
| densidade | 17,13 tx/bloco (16 ± 2) |
| silhueta (`silcheck.py`) | Dice 0,887 com a blocagem B (mínimo 0,80); Edmontossauro 0,33, Parassaurolofo 0,35, Tricerátops 0,38, Estiracossauro 0,47 (máximo 0,62) |
| headcheck macho | cabeça 0,42 vizinhos que mudam (1,83x o corpo, 0,23); borda do bico 7 texels de cada lado; íris 9, brilho 1; acento 48 |
| uniquecheck (limite 0,78) | o mais perto: Velociraptor 0,51, Mosassauro 0,46, Albertossauro 0,44 |
| colourcheck --remade | Galimimo 10,2, Majungassauro 13,6, Giganotossauro 14,3 |
| gen_species | escala 0,925 mantida; `ride_offset` 5,23 e `ride_forward` 1,55 (assento a 86,9 px); hitbox mantido |

## Animações (`coryanims.py`, 37, mesmos nomes)

Reescritas sobre a postura nova: a pastagem e o beber trazem o pescoço alto até o chão (`reach_down`), e o beber abre
as patas da frente como a girafa; a corrida é um **galope em quatro patas** (as da frente são mais longas que as de
trás; o v3 corria em duas); o andar tem passada de 44 px (`Corythosaurine.WALK_PX`/`RUN_PX` acompanham). O leque mexe
em quase tudo (`fan`: abrir, erguer, deitar, tremer): **helmet_display** abre o leque de perfil num estalo e o mantém
aberto tremendo enquanto a cabeça faz a reverência; o alarme ergue e abre o leque; o chamado o levanta; o cochilo, o
deitar, a corrida e a pastagem o deitam para trás. GIFs em `previews/animacoes/` (andar, corrida, exibição, beber,
pastar, alarme); os GIFs das outras animações nessa pasta ainda são do v3.

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
- `corythosaurus.bbmodel` regerado do jogo por `_engine/bbexport.py` (v4).
- Fotos no jogo do v4 (depois da aprovação) e a fase `cory` da `BehaviorTest` de novo com o modelo novo.
