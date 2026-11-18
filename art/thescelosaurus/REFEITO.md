# Tescelossauro refeito (1.11.0; modelo v4 de 16/11/2026)

Estudo aprovado: `docs/estudos/15_HERBIVOROS_1_11.md` (seção Tescelossauro e "Respostas do Rodrigo", 10/11/2026).
Terceiro dos quatro herbívoros da 1.11.0, feito direto pelo método "silhueta primeiro" (como o Maiassauro v4 e o
Coritossauro v4): primeiro a blocagem em preto (`tools/modelgen/handmade/_silhuetas/thescelosaurus.py`), escolhida pelo
Rodrigo a variante **A, "tipo ave"**, depois o modelo osso por osso sobre ela.

A personalidade dele, separada dos outros bípedes pequenos do jogo: o Galimimo é a avestruz de pescoço longo e pernas
de corredor que foge em linha reta; o Paquicefalossauro, a cúpula, mel listrado, que avisa e dá cabeçada; o Dakotaraptor
e o Velociraptor são os caçadores. O Tescelossauro é **o bicho do mato: tronco curto empinado de ave, pescoço em S,
coxas grossas, cauda dura do tamanho do resto, verde-samambaia de pintas, que congela, dispara com o lenço da cauda
erguido e some no mato**.

## Modelo (`tools/modelgen/handmade/thescelosaurus/thes.py`)

- **Postura:** tronco curto (peito, torso e quadril) empinado 22 graus no osso `body`, como o de uma ave do chão;
  pescoço em S em três peças (`neck1..3`: 52, 0 e -60 graus), a cabeça levada nivelada no alto; braços pequenos dobrados
  sob o peito (mão de cinco dedos com unhas escuras).
- **Pernas:** coxa grossa (`thigh` funda, entrando no quadril, e o `knee` mais estreito), canela longa e fina, metatarso
  longo, dedos deitados no chão com unhas escuras; em meio passo, como na blocagem.
- **Cauda:** reta e dura (tendões ossificados), cinco peças que afinam e se sobrepõem, do comprimento do resto do bicho,
  levada 22 graus acima (a blocagem pedia 14; com 22 a silhueta se afasta do Paquicefalossauro e do Coritossauro v4).
- **Cabeça do padrão v3, desenhada da anatomia dele:** comprida e baixa; olho grande (íris amarelo-clara, pupila
  redonda, brilho) sob a barra de osso da palpebral, que lhe dá o ar desconfiado; placas da bochecha saltando no canto da
  boca; ponta do bico curta, sem dente; **quatro pinos de marfim desiguais do pré-maxilar** debaixo do focinho, atrás
  da ponta (os únicos dentes de verdade dos quatro herbívoros da 1.11), predentário embaixo; narinas grandes na ponta
  (o faro). A faixa escura vai do olho ao canto da boca e uma linha clara corre do olho para trás pelo pescoço até o
  ombro. O macho tem a **sobrancelha amarela** (o acento, `male_display`), vista quando ele levanta a cabeça.
- **Pele desenhada, não gerada ("samambaia", estudo 15):** dorso escuro com **selas escuras quebradas no espinhaço**,
  **fileiras de pintas claras** que seguem as costelas (luz de mata, como no filhote de anta), flanco verde com um grão
  fino de escamas de um passo de tom, barriga creme-esverdeada; coxa com pintas; canelas e pés mais escuros com escudos
  na frente; cauda com **anéis escuros** para a ponta e o **lenço claro** por baixo (aparece na fuga). O filhote é mais
  claro, de pintas maiores (`thescelosaurus_baby.png`).
- **Sem sela:** não é montável (resposta do Rodrigo).

## Medidas (build)

| | valor |
|---|---|
| Comprimento | 4,0 m (Galton 1974), 73,5 px, 17,4 texels por bloco, escala 0,922 |
| Hitbox | 0,95 x 2,22 blocos; filhote 0,3 |
| Silhueta (`silcheck.py --built`, no geo do jogo) | blocagem A 0,822; Galimimo 0,546; Paquicefalossauro 0,594; Dakotaraptor 0,483; Velociraptor 0,442; Coritossauro v4 0,603 |
| `headcheck` | cabeça 0,42 de troca de vizinhos (x1,95 o corpo, 0,21); 6,2 texels de dente visíveis de cada lado; íris 6, brilho 1; acento 16 |
| `uniquecheck` | máximo 0,59 (Majungassauro: os dentes; olho e rosto 0,51 e 0,36); limite 0,78 |
| `colourcheck --remade` | mais perto: Maiassauro 11,0, Terizinossauro 15,2, Mosassauro 17,2 |
| QA | 0 coplanares, 0 pixel bugs, 0 animações fora do chão, 42 animações |

## Animações (`thesanims.py`, 42)

Conjunto padrão (idle, walk, run, swim, turn_left/right, walk_tired, idle_tired, eat, graze, drink, attack, kick_back,
hurt, death, knockout, knocked_out, wake, sit, sleep, wake_sleep, lie_down, get_up, beg, tame, hatch, call, look_back,
shake, sniff) e as dele:

- `freeze`: para no meio do passo, um pé na ponta atrás, cabeça erguida e parada, só as narinas mexem;
- `bolt`: o disparo, corrida em ziguezague (o corpo vira e inclina de um lado e do outro a cada duas passadas), baixo,
  a cauda dura erguida mostrando o lenço;
- `hide` e `peek`: deitado rente, o pescoço estendido no chão; levanta a cabeça, olha em trancos e abaixa;
- `sniff_ground`, `sniff_air`: fareja o chão varrendo com a cabeça baixa; fareja o ar de focinho erguido;
- `dig`: as mãos raspam o chão, o focinho entra e puxa (raízes);
- `burrow_dig`: agachado de frente para o barranco, as mãos raspam, o focinho empurra, um pé joga a terra para trás;
- `burrow_sleep`: dorme enrolado, a cabeça no flanco, a cauda dobrada em volta;
- `tail_flag`, `alarm`: a cauda sobe duas vezes mostrando o lenço; o grito curto com a cauda erguida;
- `kick`: encurralado, o chute para a frente com a perna forte (golpe em 0,5 s); `attack`: a mordida com os dentes da
  frente (0,45 s).

## Comportamento (`entity/Thescelosaurine`, log `[thesc]`)

- **Congela e dispara:** nota um predador ou um jogador em pé a 16 blocos (agachado, só a 6) e congela 1 a 3 s; se o
  perigo chega a 10 blocos, ou ainda está perto quando o congelamento acaba, dispara para o mato mais fechado a 14 blocos
  (folhas, samambaias, arbustos; ou a toca), em ziguezague, e se esconde deitado, espiando, até o perigo sumir por 5 s. Os
  outros que veem o lenço disparam junto. Se o perigo fica longe (16 a 24 blocos), sai de mansinho para o outro lado.
- **Faro:** nota um predador a 24 blocos sem linha de visão (`sniff_air` e congela); fareja o chão e o ar parado.
- **Toca (hipótese, o Guia avisa):** ao entardecer o adulto selvagem sem toca procura um barranco de terra, areia,
  cascalho ou argila a 12 blocos, cava (`burrow_dig`, 12 s) e abre um nicho de 2 de fundo; à noite vai até ela e dorme
  lá dentro (`burrow_sleep`); na fuga corre para ela; os ovos ficam no fundo da toca (`DinosaurEntity.eggCentre`).
  Precisa de `mobGriefing` para abrir o barranco.
- **Encurralado:** morde ou chuta para a frente; o que morde a cauda leva o `kick_back` (`HerbivoreDinosaur.KICKS`).
- **Domado:** segue o dono e desenterra raízes e tubérculos; não é montável.
- Mata, pântano e beira de rio, grupos de 2 a 4. Partes de acerto, conjunto vivo e pele de filhote.

## Ovo e ninho (`tools/spritegen/thesc_extras.py`)

Especulativo (não se conhece ovo): cinco ovos alongados de pé num anel, enterrados até a metade em terra escavada,
creme-oliva com pintas verde-samambaia, e o montinho de terra tirada da toca de um lado; no estágio 2 o focinho do
filhote sai pela ponta de um deles.

## Teste no jogo (`BehaviorTest` fase `thesc`, também na `regressao`)

Fotos (lado, 3/4, frente, cabeça, macho e fêmea, filhote, ao lado do Galimimo, do Paquicefalossauro e do Dakotaraptor),
congela/dispara/esconde com um Dakotaraptor chegando e um capão de samambaias e folhas, faro atrás de um muro de pedra,
jogador em sobrevivência a 12 blocos, toca num barranco de terra ao entardecer e sono nela à noite, ovo na toca, domado
seguindo e achando raízes. Checagens em `tools/validation/behavior_regression.py`.

Resultado no cliente Fabric (17/11/2026, volume 0, `caffeinate -dimsu`): as 13 checagens `thesc` passaram. Congelou pelo
faro a 22 blocos (3 de 3), disparou a 12 (3 de 3, dois pelo lenço), os 3 se esconderam no capão de samambaias e folhas e
saíram 5 s depois de o raptor sumir; farejou o raptor atrás do muro sem vê-lo; notou o jogador em pé a 12 blocos; cavou a
toca em 14 s e dormiu nela à noite; o ovo ficou na toca; domado, seguiu o dono de 10,9 a 4,7 blocos e achou raízes; não
monta. Fotos em `previews/jogo/`.
