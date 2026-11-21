# Maiassaura refeito (1.11.0)

## v4, "a mãe empinada" (16/11/2026, silhueta C)

O Rodrigo recusou a v1 ("os modelos tão muito padrão, não sinto que são únicos"): os bicos-de-pato saíam todos com o
mesmo corpo horizontal, cauda reta e pernas finas. A v4 foi feita pelo método "silhueta primeiro" a partir da blocagem
C escolhida por ele (`tools/modelgen/handmade/_silhuetas/maiasaura.py`). O comportamento (`Maiasaurine`, `NestRaidGoal`,
ninho coberto, fase `maia`) e os nomes das 42 animações e dos ossos não mudaram.

- **Postura:** em repouso fica **meio empinada** sobre as patas de trás e a cauda grossa (tripé): corpo 34 graus para
  cima (`REST["body"]`), **barriga enorme e clara à mostra**, braços grossos pendurados, cabeça baixa no S do pescoço
  olhando o ninho. Ao andar **cai para quatro patas** (`maiaanims.posture`: 0 = tripé, 1 = nivelado com as mãos no
  chão). Corre em duas patas; o filhote anda empinado em duas patas como a mãe.
- **Medidas:** 169 px do bico à ponta da cauda em repouso, escala 0,90 (9 m, 17,7 texels por bloco), 5,1 m de altura;
  hitbox 2,0 x 3,2.
- **Silhueta** (`maiasaura/silcheck.py`): semelhança 0,91 com a blocagem C; 0,49 Edmontossauro, 0,50 Parassaurolofo,
  0,53 Tricerátops, 0,57 Estiracossauro.
- **Pele desenhada, não ruído:** contrassombreamento forte no corpo "desenrolado" (espaço dos cubos, acompanha o corpo
  quando empina ou nivela): dorso escuro, flanco palha-verde, borda recortada em ondas, barriga creme com dobras;
  **sela de chevrons** escuros apontando para a frente, dos ombros ao meio da cauda, cada um com a borda de trás clara
  e descendo pelo flanco em barras inclinadas; duas barras escuras na coxa; **máscara facial** escura do focinho ao fim
  do crânio passando pelo olho, lábios e garganta claros; sobrancelha grossa saliente sobre o olho; bico largo caído de
  queratina cinza-oliva com a borda serrilhada. Escama miúda só como um passo de tom, esparsa, por baixo do desenho.

- **Segunda passada (16/11):** calombo como um domo só (base larga e duas camadas encaixadas, 2 px para dentro e
  2 px para cima, cor correndo pela altura); bico de pato em três peças que se alargam e afinam em perfil (raiz 5 px,
  bico 4 px, ponta caída 3 px) com borda clara e serrilhada; sem a placa clara solta do pescoço; o desenho continua
  nos membros (barras inclinadas na coxa, no braço, na canela e no antebraço, escama esparsa), mãos e pés mais
  escuros. Montada e parada, toca `ridden_idle` (nivelada em quatro patas, a sela reta; `Maiasaurine`).
  `art/maiasaura/maiasaura.bbmodel` agora sai de `_engine/bbexport.py`, a partir dos arquivos do jogo.

## v1 (10/11/2026, substituída)

Estudo aprovado: `docs/estudos/15_HERBIVOROS_1_11.md` (seção Maiassaura e "Respostas do Rodrigo", 10/11/2026). Primeiro
dos quatro herbívoros da 1.11.0 e primeiro herbívoro no padrão da 1.10 (estudo 14: 16 texels por bloco, pele `skin2`,
cabeça do padrão v3 desenhada a partir da anatomia dele, pescoço e cauda em peças que afinam e se sobrepõem).

## Modelo (`tools/modelgen/handmade/maiasaura/maia.py`)

- **9 m** (o topo: Wosik et al. 2020), desenhado a 16,94 px/m: 160 px de comprimento, escala 0,955 no jogo,
  **16,75 texels por bloco**. Hitbox 2,0 x 2,6; filhote a 0,15 do adulto.
- **Cabeça (assinatura, ~25% maior que o osso):** curta, funda e larga; bico largo e **caído na ponta** (não o bico
  achatado de pato do Edmontossauro); na frente e por cima dos olhos o **calombo sólido** de osso (nasais e frontais) em
  três camadas que nascem do teto do rosto (base na cor da pele, escamas grandes e chatas, sem degrau de bloco). No
  macho o calombo cora em **ocre-ferrugem** com a **ponta gasta e clara**; na fêmea fica da cor do rosto.
- **Padrão v3, desenhado só para ele:** olho médio atrás e abaixo do calombo, íris castanho-âmbar com pupila redonda,
  brilho alto atrás, **pálpebra de baixo grossa e clara** em duas fileiras; o "dente à mostra" é a **borda serrilhada
  do bico** (dentículos claros de 1 texel, desiguais, com falhas, numa placa de recorte pendurada fora do bico de baixo);
  atrás dela o **lábio de pele** sobre a bateria de dentes e a linha escura da boca; rosto em **escama miúda de seixo**,
  focinho com seixos maiores; narina alta no fundo do bico. Pescoço curto e grosso em **duas peças que afinam** (a
  segunda começa 4 px dentro da primeira); cauda funda, de lados chatos, em **quatro peças** sobrepostas (17, 12, 7 e
  4 px de altura).
- **Corpo:** quadrúpede pesado quando adulto, quadril o ponto mais alto, sem a franja segmentada do Edmontossauro,
  mãos em luva de casco, pés de três dedos com unhas de casco mais largos que a canela.
- **Cor "capim-seco"** (aprovada; um passo mais verde que as amostras do estudo, porque a pele pintada inteira mediu
  8,3 do Edmontossauro com as amostras exatas): dorso um tom mais escuro, **manchas grandes, soltas e verticais** nos
  flancos (sombra de arbusto), barriga creme, cabeça um pouco mais clara que o pescoço.
- **Filhote:** pele própria (`maiasaura_baby.png`, mais clara e lisa, cor de palha, sem manchas), sem calombo
  (`adult_bump`, escondido no filhote) e cabeça 1,3x (`DinosaurEntity.babyHeadScale`, olhos grandes e focinho curto,
  Horner & Makela 1979).
- **Sela de Ninhal** (`MAIASAURA_SADDLE`): esteira larga de junco trançado com trama verde, assento baixo de couro em
  armação de madeira, alforjes fundos de fibra de casca nos flancos, cilha de corda.

## Medidas (build)

| | valor |
|---|---|
| QA do motor | 0 coplanares, 0 pixel ruim, 0 pose fora do chão, 42 animações |
| densidade | 16,75 tx/bloco (16 ± 2) |
| headcheck macho | cabeça 28 cores, 0,38 vizinhos que mudam (1,41x o corpo, 0,27); dentículos 8 texels de cada lado; íris 7, brilho 1; acento 125 |
| headcheck fêmea | 0,37 (1,37x o corpo) |
| uniquecheck (limite 0,78) | o mais perto: Albertossauro 0,64, Velociraptor 0,63, Dakotaraptor 0,61, Majungassauro 0,59, Edmontossauro 0,57 (Parassaurolofo abaixo disso) |
| colourcheck --remade | macho: Terizinossauro 13,0, Edmontossauro 13,5, Carcarodontossauro 14,6; fêmea: Terizinossauro 12,0, Edmontossauro 12,1 |

## Animações (`maiaanims.py`, 42)

Padrão: idle, walk (quatro patas), run (duas patas, como todo hadrossauro), swim, turn_left/right, walk_tired,
idle_tired, eat, graze, drink, attack (investida da mãe com a cabeça funda e o ombro, golpe aos 0,5 s), kick_back,
body_shove, hurt, death, knockout, knocked_out, wake, sit, sleep, wake_sleep, lie_down, get_up, beg, tame, hatch.
Próprias: **biped_walk** e **biped_run** (o filhote e o jovem em duas patas, Cubo et al. 2015), **cover_nest** (arranca
folhas de um lado e do outro e joga no ninho), **feed_young** (o pescoço arfa duas vezes e o bico solta as folhas
mastigadas: hipótese), **nest_guard**, **nest_dig**, **nuzzle**, **adopt**, **rear_browse**, **colony_call** (chamado
curto e nasal: sem sacos e sem crista), call, answer, alarm, **nest_beg** e **nest_sleep** (o filhote no ninho).
Sem trio de duelo (hadrossauro não duela). GIFs em `previews/animacoes/`.

## Comportamento (`common/.../entity/Maiasaurine.java`)

- **Colônia:** a fêmea selvagem perto de uma ninhada selvagem sem dona toma o ninho como casa, pasta a até 12 blocos e
  dorme ao lado; os outros adultos a até 40 blocos de uma casa são da colônia (defensivos); fora dela é dócil e foge.
- **Ninho coberto:** de tempos em tempos a mãe cobre os ovos (`cover_nest`); `DinoEggBlock.COVERED` (estado novo, com
  modelo próprio só para a Maiassaura): coberto choca a velocidade 1,0, aberto a 0,25 (ovo comum 0,5). O jogador cobre
  com folhas ou samambaia. **Hipótese** (vegetação apodrecendo).
- **Filhote de ninho:** nascido na colônia fica no ninho 2 dias de jogo (`Maiasaurine.nestTicks`), pede comida
  (`nest_beg`) e **só cresce alimentado**: a mãe traz folhas (`feed_young`, 2.400 tiques de crescimento); o jogador
  que o alimenta começa a domá-lo (o progresso de doma normal). Alimentado e perto de um adulto cresce o dobro (a "boa
  mãe" agora só vale para a própria espécie). A fêmea adota órfão da espécie a 16 blocos (`adopt`).
- **A colônia inteira defende:** pegar um ovo ou bater num filhote põe todos os adultos da colônia (40 blocos, não os
  24 da raiva de ovo) contra o culpado; a mãe do ninho fica por cima (`nest_guard`).
- **Ladrões à noite:** uma vez por noite a colônia pode atrair um Velociraptor (às vezes um Dakotaraptor) que vem
  buscar um ovo (`ai/NestRaidGoal`); a colônia acorda e o expulsa. Respeita a regra de predadores e a cota da região.
- **Ciclo:** ninho vazio, a mãe põe de novo nele uns dias depois (3 dias), se a região tiver vaga (`RegionPopulation`).
- **Fora da colônia:** manadas de 6 a 12, com o líder da 1.10; quem vê um caçador dá o berro (`alarm`) e correm em bloco.
- Estrutura **Colônia de Ninhos** devolvida a ele (`gen_structures.STAND_IN` sem o Edmontossauro): ninhos a 7 blocos
  (Palmer 1999), monte de lama com cratera, metade já coberta, uma mãe por ninho.
- Log: linhas `[maia] ...`.

## Teste no jogo

Cliente Fabric com som zerado, sempre dentro de `caffeinate -dimsu` (11/11/2026). Fase nova `maia` na `BehaviorTest`
(também na lista `regressao`), com as checagens `maia: ...` em `tools/validation/behavior_regression.py` (12 de 12 OK):

| | resultado |
|---|---|
| filhote | escala 0,15, em duas patas (`biped_walk`/`biped_run` tocados no cliente) |
| a mãe toma o ninho | sim (ninho A), cobre 3 de 3 ovos em 25 s; o ninho sem mãe fica aberto |
| choco | ninhada coberta saiu com 3 tiques aleatórios, a aberta com 11 |
| filhotes da colônia | 6 nasceram, 3 no ninho da mãe; o do ninho a 1,1 bloco dele depois de 30 s, alimentado pela mãe, ainda no ninho |
| sem comida | o filhote sozinho no ninho cresceu 0 tique em 20 s |
| o jogador alimenta | cresceu 402 tiques em 20 s e a doma começou (progresso 1,0) |
| ovo tomado | 4 de 4 adultos vão no jogador, 1 deles a mais de 24 blocos (a colônia, não a raiva de ovo) |
| filhote atacado | 3 de 4 adultos vão no Velociraptor |
| noite | um Velociraptor veio buscar ovo; a colônia acordou e foi nele em 1 s; nenhum ovo comido |

Fases antigas no mesmo lote (`jaws,gaits,look,herdmove,babystay,eggrage`): mandíbula do Maiassaura 10 graus, pernas
1.500 graus/s no arquivo e 73 graus por tique no jogo, manada, filhote junto da mãe e raiva de ovo passaram. Falharam
só medidas de outras espécies, sem relação com o Maiassaura: mandíbula sem medida (osso não lido) de Protocerátopo,
Velociraptor e Deinossuco, e as pernas do Majungassauro a 127 graus por tique (limite 125).

Fotos do jogo em `previews/jogo/` (de lado, 3/4, frente, cabeça, macho e fêmea, ao lado do Edmontossauro e do
Parassaurolofo, ninho coberto, filhotes no ninho, cobrir, alimentar, guardar o ninho, chamado, filhote em duas patas,
saída do ovo, ladrão à noite). Folha das cabeças: `previews/cabecas_hadrossauros.png` e `_perfil.png`.

Leitura honesta da cabeça ao lado dos dois hadrossauros (headsheet): é a única curta e funda, com o calombo em cima
dos olhos, o bico caído com a borda serrilhada clara e o olho âmbar de pálpebra clara; o Edmontossauro tem cabeça longa
e chata e a crista de carne vermelha num prato, o Parassaurolofo o tubo. O acento do macho no calombo foi refeito no
fim (a coroa gasta e clara, o ocre nas encostas) porque a primeira versão, ocre por inteiro, lia como o "chapéu" de
carne do Edmontossauro; as fotos do jogo são de antes desse retoque (só a cor da coroa mudou).

## Pendente

- Vozes próprias (usa a do camelo, como antes).
- O filhote recém-nascido a 0,15 do adulto é pequeno de propósito; no jogo ele se lê dentro do ninho (cabeça grande,
  em duas patas), mas a foto de perto do filhote sozinho (`behavior_maia_calf`) saiu vazia e precisa de outro ângulo.
- Rodada num mundo gerado (`Playtest`) com a Colônia de Ninhos de verdade.
- O `art/maiasaura/maiasaura.bbmodel` ainda é o do modelo antigo (as peles ao lado já são as novas).
