# Carcarodontossauro refeito (1.10.1)

Terrassic · 08/11/2026 · estudo 13 (Carcarodontossauro) e estudo 14 ("Decisões do Rodrigo"), no padrão do piloto do
Daspletossauro (`art/daspletosaurus/PILOTO.md`) e do Albertossauro (`art/albertosaurus/REFEITO.md`)

O terceiro dos quatro predadores da 1.10.1. Mesmo pixel, mesma pele (skin2), mesmo encanamento de animação e a mesma
checagem de densidade no `build.py`. O ponto principal do estudo era **não parecer nem agir como o Giganotossauro**,
que tem o mesmo comprimento (12,5 m): `previews/ao_lado_do_giganoto.png` é a comparação-chave.

Do *C. saharicus* conhecemos bem o crânio e pouco do corpo (o esqueleto de Stromer virou *Tameryraptor*, Kellermann et
al. 2025): **as proporções do corpo vêm dos parentes** (Giganotosaurus, Mapusaurus, Acrocanthosaurus) e são hipótese. O
Guia diz isso, e diz a idade: Cenomaniano, 100 a 94 Ma, uns 30 milhões de anos antes de Hell Creek.

## Medidas do padrão

| Regra (estudo 14) | Meta | Medido |
|---|---|---|
| 1 texel = 1 pixel do mundo | 16 ± 2 tx/bloco, `MODEL_SCALE` ≈ 1 | **16,3 tx/bloco**: 215 px a 16,94 px/m, escala 0,983, 12,5 m (o `build.py` falha fora de 14 a 18) |
| Tons pela silhueta inteira | dorso escuro, flanco médio, ventre claro como uma forma só | `skin2.Profile` do pescoço à ponta da cauda |
| Base calma | sem Voronoi | escamas largas só na barriga (`skin.scutes`), escamas na frente do metatarso e dos dedos, focinho rugoso; o resto é base com manchas suaves e pintas espaçadas |
| Paleta | 20 a 40 cores | **24** no corpo; 37 com a sela no mesmo atlas |
| Marcas desenhadas | 1 a 3, no espaço do corpo | (1) **barras verticais curtas e quebradas** no dorso e no alto do flanco, do ombro à cauda (sombra de mangue), cada uma com a ponta de baixo rasgada; (2) **testa, lacrimal e crista nucal de chifre escuro**; (3) **máscara escura atrás do olho** até a articulação da mandíbula, preta no macho e chumbo na fêmea |
| Olho de 2 a 3 texels | pupila escura e um ponto de cor | sob a prateleira da testa: pupila, ponto dourado e brilho |
| Exagero de uma forma-assinatura | 15 a 30% | o crânio: 31 px de comprido (1,8 m desenhado contra 1,4 a 1,6 m) e 22 de alto com a mandíbula |
| Pés mais largos que a canela, pata ≥ 3 px | | pé de 9 px (três dedos) contra canela de 7; braço de 3 px, três dedos |
| QA do motor | zero | coplanares 0, pixel ruim 0, pé fora do chão 0 nas **61 animações** |

## As cinco separações do Giganotossauro (estudo 13)

| | Giganotossauro (refeito) | Carcarodontossauro |
|---|---|---|
| Cabeça | baixa e comprida, faca: 26,7 x 14,2 px no jogo (altura/comprimento 0,53) | alta e triangular: 31,5 x 22,3 px (0,71, **~33% mais alta** para o comprimento), maxilar fundo e reto embaixo com o alto do focinho caindo em rampa, prateleira de osso sobre os olhos e crista nucal atrás |
| Pescoço e tronco | pescoço longo, corpo longo e magro | pescoço grosso e curto (16 px de largura no ombro), levado mais baixo; tronco de 33 px de fundo, peito bem abaixo do quadril |
| Cauda | crista alta de espinhos | lisa, funda na base (o músculo caudofemoral), sem crista |
| Jeito | inquieto, corta de lado, recua e circula | de tocaia, arranca, rasga de frente e responde com a testa |
| Cor | ardósia azulada | arenito-malva |

## Cor (arenito-malva)

Dorso malva-sombra (`#431f2d` a `#5a3141`), flanco arenito-malva (`#774858` a `#916373`), ventre quase branco levemente
rosado (`#dbc4c9` a `#ebdcdf`), testa e crista cor de chifre escuro (`#2a2224` a `#5e4f53`), máscara `#231b1f` (macho) e
`#54474d` (fêmea). A fêmea é meio tom mais clara.

`colourcheck.py carcharodontosaurus --remade` (só contra os refeitos):

| | 1º | 2º | 3º |
|---|---|---|---|
| macho | Tricerátops **10,9** | Estiracossauro 12,1 | Daspletossauro 15,2 |
| fêmea | Estiracossauro **10,7** | Tricerátops 11,5 | Daspletossauro 16,2 |

A primeira versão (o arenito-malva do estudo, mais cinza) dava 7,0 do Tricerátops e 9,3 do Estiracossauro: o malva
apagado fica entre o violeta do Tricerátops e o rosado quente do Estiracossauro. Subi o vermelho (a*) dos tons médios e
escuros e deixei a barriga quase branca, como o estudo pede. Do Giganotossauro fica a 14+. **Atenção:** em
`previews/os_quatro.png` o Daspletossauro (mogno-vinho) e o Carcarodontossauro (malva) são da mesma família de cor; a
conta os separa (15), mas de longe os dois puxam para o vinho. Rever com o Rodrigo.

## Forma

- Crânio alto e triangular de perfil: um maxilar fundo e reto embaixo e o alto do focinho caindo em rampa da testa até
  a ponta (`TOP_ROT`), sulcos no maxilar subindo para trás (o traço só do gênero), nasais rugosas, prateleira de osso
  sobre as órbitas, crista nucal atrás, lábios sobre os dentes de lâmina (14 por lado).
- Pescoço grosso e curto levado baixo, tronco fundo e pesado (5 a 7 t), braços pequenos de três dedos, pernas grossas,
  cauda funda na base e lisa (5 segmentos, como os outros dois).
- Sela própria (Sela de Carcarodontossauro): manta de lã crua tecida com borda escura, assento fundo de couro com pito
  alto (para segurar na arrancada), cilha e peitoral de corda com um botão de osso, estribos de osso. Receita: couro,
  lã branca, couro de Carcarodontossauro, barbante e osso.
- Prévias: `previews/` (lateral, três quartos, frente, traseira, cabeça, macho e fêmea, com sela,
  `ao_lado_do_giganoto.png`, `os_quatro.png` com T. rex, Daspletossauro e Albertossauro nos tamanhos do jogo, GIFs em
  `previews/animacoes/`). Fotos do jogo em `previews/jogo/`.

## Animações (61)

O conjunto padrão dos terópodes do piloto (parado, gestos, voz, golpes, comer, descanso, nocaute e `hatch`), o conjunto
vivo (guarda, passos de lado, giro, finta, bloqueio, recuo, rendição, cansaço) e as próprias:

- `walk` pesado e rolado, pescoço baixo e cabeça parada; `run`; `burst` a arrancada da tocaia (passadas longas e rentes,
  cabeça esticada, a boca já abrindo); `drag` andando de ré com a cabeça baixa puxando a carcaça;
- `ambush_crouch` agachado na margem, imóvel, só a cabeça vira um pouco (o `ambush_still` do estudo) e `ambush_look`, o
  único gesto na tocaia (os gestos em pé levantariam o bicho);
- `tear` morde (0,45 s) e puxa para trás serrando a cabeça; `brow_butt` a cabeçada de testa (0,45 s);
  `brow_display` vira a cabeça de lado e mostra a testa e a máscara (abre o duelo; o macho também faz sozinho);
  `gape_hiss` boca bem aberta com sopro sobre a presa;
- o trio do duelo nos tempos fixos: `lunge` 1,8 s (golpe aos 0,50 s, depois puxa serrando), `parry` 1,5 s (aguenta o
  golpe virando a cabeça e responde com a testa aos 0,60 s), `stagger` 1,6 s.

## Comportamento (`entity/Carcharodontosaurine`, `ai/RiverAmbushGoal`, `ai/CarcassDragGoal`, `effect/BleedingEffect`)

- **Tocaia na margem** (Stevens 2006, hipótese): com fome e sem nada à vista, vai até um lugar seco na beira da água
  (ou fica nas plantas onde está, se não há água a 14 blocos) e espera agachado, de frente para a margem por onde a
  presa desce. Da tocaia só pega o que chega a 11 blocos (`canAttack`): o jogador que passa mais longe é deixado em
  paz. Quando pega, sai numa arrancada de 2 s (+75% de velocidade, sem rugir) e, se não acerta nada, desiste a 24
  blocos de onde estava e deixa aquela presa em paz por 30 s. A tocaia dura até um minuto.
- **Mordida que rasga e sangramento** (mecânica nova, resposta do Rodrigo): o `tear` é a mordida principal (60% contra
  presa grande e contra o jogador); a vítima fica com o efeito `terrassic:bleeding` (registrado pelo mod, ícone e tipo
  de dano próprios): 1 de vida por segundo, 5 s no jogador e 8 s nos bichos. Justo com o jogador: o sangramento
  sozinho nunca o leva abaixo de um coração, não empurra, e o leite cura. No duelo, o bote (que termina num rasgo)
  também sangra.
- **Arrasta a carcaça** (hipótese): logo depois de matar uma presa pequena ou média (até a largura dele), puxa a
  carcaça de ré até a sombra mais perto (folhas em cima, de 4 a 10 blocos), ou para longe da água, ou 6 blocos para
  trás; depois come ali (o `EatCarcassGoal` de sempre). Objetivo próprio de prioridade maior, sem mexer no comum.
- **Guarda da carcaça**: sopro de boca aberta (`gape_hiss`) num comedor de carne que chega a 10 blocos e cabeçada de
  testa no menor que chega perto demais.
- **Duelo** (`DuelStyle`): paciente (110), bloqueia médio (0,30), quase não esquiva (0,05), circula pouco (0,30),
  de perfil só 25°; o jab é a mordida rápida, a assinatura e o contra-golpe são a cabeçada de testa.
- **Troféus** (já existia): cada presa morta dá +8% de ataque e +3% de velocidade, até 5, esquecidos aos poucos.
- Solitário. Linhas de log `[carcharo] ...`: tocaia (vai à margem, agacha, levanta sem presa, arranca, desiste),
  rasgo e sangramento, arrasto (para onde e quanto), guarda (sopro, cabeçada), cabeçada no duelo.

## O perdedor do duelo que morria depois de se render (Albertossauro)

Achado e corrigido em `ai/DuelGoal`. Na rendição (`DinosaurEntity.submitTo`) o vencedor perde o alvo, mas os golpes do
perdedor ainda estão na ficha dele: no tique seguinte o `HurtByTargetGoal` do vanilla (que roda antes dos objetivos de
movimento) põe o vencedor de volta no perdedor, o `DuelGoal` continua contra um rival que não luta mais (ele não pode
atacar quem o venceu) e o perdedor morre. Agora o `DuelGoal` do vencedor vê que o rival se rendeu (fora do duelo, sem
alvo, abaixo da metade da vida), solta o alvo, esquece a ficha (`setLastHurtByMob(null)`) e não volta a duelar com ele
por 2 minutos (`[duel] ... lets the beaten ... go`).

O lugar certo seria a própria rendição. **Gancho pedido no `DinosaurEntity`** (para a hora do merge): em `submitTo`,
depois de `rival.setTarget(null)`, chamar `rival.setLastHurtByMob(null)` e guardar no vencedor o UUID do rendido por
2400 tiques, com `canAttack` recusando-o nesse tempo (o espelho do `yieldedTo` que o perdedor já tem). Com isso a
proteção no `DuelGoal` fica redundante e pode sair.

## Teste no jogo (BehaviorTest, Fabric, som em 0)

Fase nova `carcharo` (fotos, tocaia num canal de água na arena, arrancada que erra, sangramento, rasgo, arrasto e
guarda) e as fases `look,jaws,gaits,duels,moves` (`TERRASSIC_GAIT_ONLY=carcharodontosaurus`,
`TERRASSIC_DUEL_ONLY=carcharodontosaurus,albertosaurus`); depois `tools/validation/behavior_regression.py`. Seis rodadas:
as primeiras acharam defeitos do próprio teste (o mundo de teste repõe bichos em volta do jogador; morto com `/kill`,
cada um deixava uma carcaça, e o carnívoro com fome largava a tocaia para comer; a espera de `-1` repetia por 10 min;
as fotos automáticas tiravam o jogador do chão no modo sobrevivência) e dois do bicho, corrigidos (a busca da margem era
curta demais e o arrasto levava a carcaça para longe da sombra quando ele já estava perto dela). Os números são da
última rodada (e da segunda para os duelos e as pernas):

- **Tocaia**: em 17 s foi até a beira do canal e agachou de costas para a água (100 quadros em `ambush_crouch`); uma
  presa a 25 blocos ficou 5 s sem ser notada ("let go"); a presa posta a 9 blocos trouxe a arrancada ("bursts out at
  the leptoceratops, 8,9 blocks off"), sem rugido. No segundo caçador a presa foi mantida 14 blocos à frente: ele
  arrancou a 11,3 blocos e desistiu **a 24 blocos de onde estava** ("missed the leptoceratops, gives up 24 blocks").
- **Sangramento**, efeito dado por comando: o Edmontossauro perde **1 de vida por segundo durante 8 s** (364,7 → 357,7)
  e o jogador em modo sobrevivência **1 por segundo durante 5 s** (20 → 15), depois para. No ataque de verdade, o
  Edmontossauro sangrou em 102 dos 200 quadros e morreu em 12 s; cada rasgo renova o efeito (log `tear: the
  edmontosaurus bleeds`).
- **Arrasto**: matou o Leptoceratops, puxou a carcaça de ré **9,6 blocos até a sombra** de uma copa de folhas ("drag
  ends: ... now in the shade"; o teste mediu 4,5 blocos do lugar da morte até o ponto final, sob as folhas).
- **Guarda da carcaça**: o Dakotaraptor posto a 2,5 blocos da carcaça levou cabeçadas de testa (80 → 49); o outro, a 12
  blocos, não.
- **Duelos** (regressão): Carcarodontossauro contra Carcarodontossauro, 13 golpes acertados, 7 cabeçadas de testa
  (assinatura), poucas esquivas e bloqueios, nenhum perdedor em 20 s (são 277 de vida); contra o Giganotossauro, 13
  golpes acertados, os botes do Carcarodontossauro deixam o Giganotossauro sangrando ("duel tear: the giganotosaurus
  bleeds"), o Giganotossauro aparou um. Passou.
- **Rendição** (Albertossauro contra Albertossauro, com a correção): o perdedor se rendeu com 39/152, o vencedor o
  soltou no mesmo instante ("[duel] albertosaurus lets the beaten albertosaurus go (39/152)") e aos 20 s o perdedor
  estava vivo, com 39/152. Na rodada do Albertossauro ele estava morto.
- **Mandíbula** 43 graus de giro (passou); **pernas** 1.241 graus/s no máximo no arquivo e 105 graus por tique no jogo
  (limite 125). Passou.
- **Fotos** em `previews/jogo/`: vistas (lado, três quartos, frente, cabeça), ao lado da fêmea e do Giganotossauro, a
  tocaia, a arrancada, o rasgo, a cabeçada, a exibição da testa, o sopro e os GIFs `tocaia.gif`, `arrancada.gif`,
  `perde_a_presa.gif`, `rasgo.gif`, `arrasto.gif`, `guarda_da_carcaca.gif`, `duelo.gif` e `duelo_com_giganoto.gif`.
  A textura sai nítida no jogo, o olho e a máscara aparecem, a testa escura lê de longe.
- **Regressão**: o `behavior_regression.py` passou em tudo que é do Carcarodontossauro; as falhas que sobram são das
  fases que não rodaram nesta bateria (água, noite, território e as outras), como nos dois anteriores.
- `./gradlew :fabric:compileJava :forge:compileJava`: compila.

## Em aberto

- **Cor perto do Daspletossauro de longe** (ver acima).
- **Gancho da rendição** no `DinosaurEntity` (acima).
- As abas da sela continuam sem aparecer nas prévias (`faces=out("east", ...)`), igual aos dois anteriores: conferir no
  jogo e, se for o caso, corrigir nos três.
- **Vozes antigas**, não ouvidas no jogo; o sopro (`gape_hiss`) usa a voz de ameaça.
- **Ovo e ninho**: o ovo-bloco só trocou a cor para a do bicho; o monte de areia e restos de mangue na margem
  (especulativo no estudo) não foi feito.
- **Dente caído como item**: fora, até o Rodrigo decidir (estudo 13).
- **Jovens**: a mesma pele do adulto.
- A tocaia em mundo gerado (beira de rio de verdade, presas que vêm beber) só se vê num mundo gerado; o teste usa um
  canal de água na arena plana.
- Regra da luz (B6), gomos e silhueta (item 4) e a falha do `gen_species.py` fora da faixa de densidade: como nos
  outros dois, para o próximo patch.
