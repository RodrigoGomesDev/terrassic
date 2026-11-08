# Majungassauro refeito (1.10.1)

Terrassic · 08/11/2026 · estudo 13 (Majungassauro, e as respostas do Rodrigo: 8 m, a presa segura na boca é mecânica
de verdade e o jogador escapa batendo) e estudo 14 ("Decisões do Rodrigo"), no padrão do piloto do Daspletossauro
(`art/daspletosaurus/PILOTO.md`), do Albertossauro e do Carcarodontossauro (`art/*/REFEITO.md`)

O quarto e último predador da 1.10.1. Mesmo pixel, mesma pele (skin2), mesmo encanamento de animação e a mesma
checagem de densidade no `build.py`. O ponto principal do estudo era **não parecer nem agir como o Carnotauro**, o
primo abelissaurídeo de quase o mesmo comprimento: `previews/ao_lado_do_carnotauro.png` (um em cima do outro) e
`previews/carnotauro_lado_a_lado.png` são as comparações-chave; `previews/os_cinco.png` põe T. rex, Daspletossauro,
Albertossauro, Carcarodontossauro e Majungassauro lado a lado nos tamanhos do jogo.

## Medidas do padrão

| Regra (estudo 14) | Meta | Medido |
|---|---|---|
| 1 texel = 1 pixel do mundo | 16 ± 2 tx/bloco, `MODEL_SCALE` ≈ 1 | **16,1 tx/bloco**: 137 px a 16,94 px/m, escala 0,991, 8 m (o `build.py` falha fora de 14 a 18) |
| Tons pela silhueta inteira | dorso escuro, flanco médio, ventre claro como uma forma só | `skin2.Profile` do pescoço à ponta da cauda; no alto das costas largas o meio é mais escuro que as bordas |
| Base calma | sem Voronoi | escamas largas só na barriga (`skin.scutes`), escamas na frente do metatarso e dos dedos, focinho rugoso (covas esparsas); o resto é base com manchas suaves |
| Paleta | 20 a 40 cores | **38** no atlas com a sela (o corpo sozinho fica perto de 26) |
| Marcas desenhadas | 1 a 3, no espaço do corpo | (1) **faixas transversais largas e rasgadas** no dorso, do ombro à cauda, que viram anéis perto da ponta; (2) **domo e nasal de chifre escuro**, e no macho a pele em volta do domo **ocre-laranja apagado** (na fêmea cinza-pardo); (3) **listra clara** do canto da boca descendo pelo pescoço |
| Olho de 2 a 3 texels | pupila escura e um ponto de cor | sob a base do domo: pálpebra, pupila, ponto dourado e brilho |
| Exagero de uma forma-assinatura | 15 a 30% | a cabeça: 16 px do occipital ao focinho (0,95 m desenhado contra ~0,7 m), 11 px de largura no crânio, e o domo 4 px acima do teto |
| Pés mais largos que a canela, pata ≥ 3 px | | pé de 7 px (três dedos) contra canela de 6; braço de 3 px, dois tocos de dedo |
| QA do motor | zero | coplanares 0, pixel ruim 0, pé fora do chão 0 nas **64 animações** |

## As separações do Carnotauro (estudo 13)

| | Carnotauro (refeito) | Majungassauro |
|---|---|---|
| Cabeça | curtíssima e alta, **dois chifres** sobre os olhos | curta, funda e **larga**, nasal grosso e rugoso, **um domo** no teto sobre os olhos, sem chifre |
| Pernas | longas, de corredor | **curtas e grossas**, metatarso curto |
| Altura | linha das costas a 0,35 do comprimento | **0,29** do comprimento (18% mais baixa), centro de gravidade baixo |
| Braços | tocos | tocos ainda menores (dois tocos, sem garra) |
| Jeito | investe com os chifres em campo aberto | **morde e segura**, arrancada curta e baixa, empurra com o domo por baixo |
| Cor | vermelho-tijolo, chifres pretos | **cinza-basalto** (azul-ardósia apagado), faixas escuras largas |

## Cor ("cinza-basalto", a lama seca da Maevarano)

O estudo propunha "sálvia-seca", mas os verdes estão tomados por dois predadores grandes (o T. rex, verde-musgo, e o
Albertossauro, verde-abeto), e o pedido foi uma família de matiz claramente diferente dos outros três novos e da
ferrugem do Carnotauro. Medi a assinatura em CIELAB de todos os refeitos (machos e fêmeas): o espaço livre para um bicho
grande e de cor natural está nos cinzas frios. A pele é um **cinza-azulado escuro de lama seca** (`#2b4051` a `#607280`
no flanco, dorso `#1c303f`), faixas `#142f41`, ventre cinza-pedra (`#778087` a `#9ea7af`), domo e nasal de chifre
escuro (`#1f1b1a` a `#4c463f`), ocre `#8a5a30`/`#a8723c` em volta do domo do macho. Saturação baixa (croma ~14 no
flanco): é cinza com um pouco de azul, não azul. A fêmea é um tom mais clara.

Primeiras tentativas (no mesmo eixo): o cinza neutro do estudo de base dava 7,5 do Giganotossauro (ardósia muito clara
e quase sem croma); um cinza-azulado médio, 8,8. A saída foi escurecer o corpo, esfriar um pouco mais e deixar o ventre
cinza-pedra (não creme), o que o afasta do Giganotossauro pela luminosidade (o Giganotossauro é claro) e do
Anquilossauro (cinza-petróleo esverdeado) pelo matiz.

`colourcheck.py majungasaurus --remade` (contra machos e fêmeas dos refeitos):

| | 1º | 2º | 3º | Daspleto | Alberto | Carcharo | Carnotauro | T. rex |
|---|---|---|---|---|---|---|---|---|
| macho | Anquilossauro **12,1** | Giganotossauro 13,0 | Tricerátops 13,4 | 18,7 | 20,4 | 32,0 | 32,7 | 28,4 |
| fêmea | Giganotossauro **12,4** | Anquilossauro 12,5 | Tricerátops 13,3 | | | | | |

Todos acima de 10; dos outros três novos e do Carnotauro, acima de 18. No jogo (`previews/jogo/behavior_majunga_with_carno.png`)
o cinza-azulado lê de longe como outra família ao lado da ferrugem do Carnotauro. **Para o Rodrigo decidir**: é a
primeira pele fria entre os grandes predadores; se preferir algo mais quente, o espaço que sobra é estreito (os
marrons e areias estão tomados).

## Forma

- Crânio curto, fundo e largo (11 px no crânio, 9 no focinho rombudo), o alto do focinho caindo pouco (`TOP_ROT`
  -8°), nasal grosso e rugoso em cima, o **domo** em dois degraus sobre os frontais (base de pele, cúpula de chifre
  gasto mais claro em cima), lábios sobre dentes curtos e recurvados, a fileira de forames sobre o lábio.
- Pescoço curto e grosso levado quase reto, tronco largo e atarracado (17 px de largura), braços-toco de 3 px com dois
  tocos de dedo, pernas curtas (quadril a 27 px, contra 56 do Carcarodontossauro), pé largo de três dedos, cauda grossa
  na base em 5 segmentos.
- Sela própria (**Sela de Majungassauro**, a sela de briga): esteira de fibra de ráfia (a palmeira de Madagascar) com
  duas listras tingidas de vermelho-terra, assento baixo de couro (montaria estável, nada para se segurar na
  arrancada), uma **alça de corda** na frente para quando ele segura e sacode, cilha larga de ráfia e estribos curtos de
  osso. Receita: couro, junco, couro de Majungassauro, barbante e osso. Sprite em `tools/spritegen/majunga_extras.py`.

## Animações (64)

O conjunto padrão dos terópodes do piloto (parado, gestos, voz, golpes, comer, descanso, nocaute e `hatch`), o conjunto
vivo (guarda, passos de lado, giro, finta, bloqueio, recuo, rendição, cansaço) e as próprias. As poses foram escritas
primeiro para as pernas longas do Carcarodontossauro; aqui toda translação do corpo passa por `Q` = 0,5 e os passos por
`K` = 0,44 (`majungaanims.add`, `theropod.Plan`).

- `walk` de buldogue (passos curtos e rápidos, 1,4 s, corpo baixo rolando, cabeça larga parada), `run` curta, `burst`
  (passadas explosivas e rentes, cabeça esticada, a boca abrindo), `stalk`;
- `bite_hold` (estica baixo e fecha aos 0,35 s, **não abre**: puxa para trás e para baixo e os pés se firmam),
  `hold_shake` (laço: a cabeça arrancada para um lado e para o outro duas vezes por ciclo, o corpo torcendo contra, a
  cauda ao contrário; a boca nunca abre), `hold_release` (abre jogando a cabeça de lado e dá um passo atrás);
- `dome_shove` (o golpe-assinatura do duelo, 0,45 s: cabeça abaixo da do rival, o domo à frente, o corpo baixo empurra
  **para cima e para dentro**, sem tirar os pés do chão), `dome_display` (cabeça baixa e meio de lado, o domo contra o
  céu, ronco), `waterhole_threat` (domo à frente, sopro de boca entreaberta, pisão aos 1,0 s);
- `carcass_guard` (agachado sobre a carne, a cabeça baixa e os olhos para cima, rosnado, estalo da boca aos 1,8 s),
  `tooth_spit` (depois de comer: mastiga, sacode e cospe um dente; D'Emic et al. 2019), `ambush_crouch` e `ambush_look`;
- o trio do duelo nos tempos fixos: `lunge` 1,8 s (fecha aos 0,50 s e **segura** sacudindo duas vezes antes de soltar),
  `parry` 1,5 s (aguenta na cabeça baixa e responde com o domo por baixo aos 0,60 s), `stagger` 1,6 s (quase não cede:
  um tranco, um passo e volta à guarda).

## Comportamento (`entity/Majungasaurine`, `ai/WaterholeGuardGoal`)

- **Morde e segura** (Sampson & Witmer 2007, hipótese pelo focinho largo, o pescoço forte e a mandíbula flexível): o
  `bite_hold` é a mordida principal (65% quando pode segurar). Presa até **1,2 vez o tamanho dele** (tamanho linear)
  fica presa de **2 a 3 s** e é sacudida (`hold_shake`), levando um pouco de dano a cada segundo (30% do ataque); a
  pequena (até 0,55 vez) é **carregada na boca** e sacudida com a cabeça; a maior fica presa no lugar, lenta. O jogador
  preso fica **lento** (Lentidão IV renovada a cada 5 tiques, só enquanto preso) e leva 1,5 de dano por segundo; **escapa
  batendo nele 3 vezes** (um golpe de 5 ou mais conta 2) ou quando passam **3 s**. Depois ele solta com um tranco
  (`hold_release`) e não pega o mesmo jogador de novo por 8 s (o bicho, por 5 s): nunca uma presa que dura. Enquanto
  segura, o `ApexBiteGoal` fica parado com ele pela pausa (`pauseAfter`), sem truque na classe-base.
- **Arrancada curta e baixa**: um alvo novo a até **14 blocos** é atacado de imediato, sem rugido, 1,5 s com +60% de
  velocidade (`burst`); se não acerta, desiste a **24 blocos** de onde começou e deixa aquela presa em paz por 30 s.
- **Canibal** (Rogers, Krause & Curry Rogers 2003): come a carcaça de outro Majungassauro como qualquer carcaça (linha
  de log própria); com fome abaixo de 20, um vizinho da espécie abaixo de 25% da vida vira presa (`cannibalPrey`, no
  `isPrey` gerado; um ferido assim também não aceita duelo); dois com fome (abaixo de 70) na mesma carcaça **duelam**
  por ela, o perdedor se rende e vai, o vencedor come.
- **Bebedouro** (Rogers 2005, hipótese; o jogo não tem estações, então é à tarde, das 12h às 19h): uma vez por dia vai
  à água mais perto (até 32 blocos, achada por `WaterholeGoal.findWater`, o mesmo das manadas que descem para beber no
  fim da tarde), agacha na beira de frente para a água por até 2 min, **avisa com o domo** quem chega a 8 blocos (jogador,
  outro carnívoro, herbívoro grande) e **expulsa** quem continua vindo até 4,5 blocos; presa é deixada aos objetivos de
  caça da base, e a arrancada sai do agachado.
- **Pavio curto**: mostra o domo ao jogador que chega a 8 blocos e ataca se ele continuar vindo (4,5 blocos).
- **Duelo** (`DuelStyle`): de frente (perfil 10°), bloqueia muito (0,42), quase não esquiva (0,03), circula pouco
  (0,30), paciente (95); o jab é a mordida rápida, a assinatura e o contra-golpe são o empurrão de domo. No `DuelGoal` ele
  **quase não cambaleia**: o giro e o empurrão do cambaleio valem 45% dos dos outros (`Majungasaurine.staggerGive`).
- Solitário. Linhas de log `[majunga] ...`: arrancada (e quando desiste), segura/solta (quanto tempo, por quê), canibal
  (come, caça), briga pela carcaça, guarda da carcaça, bebedouro (vai, agacha, avisa, expulsa, levanta), pavio, duelo
  (segura, empurrão de domo).

## Teste no jogo (BehaviorTest, Fabric, som em 0)

Fase nova `majunga` na `BehaviorTest` (fotos, segura uma presa pequena, segura o jogador com e sem golpes, canibal,
briga pela carcaça, bebedouro, pavio) e a espécie nas listas de olhar, mandíbulas, passos, duelos (contra si e contra o
Carnotauro) e golpes. Cinco rodadas; as duas primeiras completas, as três últimas perdidas (a terceira encheu o disco
no meio das fotos; na quarta e na quinta o cliente travou ao abrir a janela, com outro cliente de outra pasta parado no
mesmo ponto: provavelmente a tela do Mac bloqueada). Números da rodada 2 (e da 1 onde dito):

- **Tamanho**: caixa 1,80 x 2,54, escala 1,0 (`MODEL_SCALE` 0,991). No jogo ao lado do Carnotauro
  (`previews/jogo/behavior_majunga_with_carno.png`) é claramente mais baixo, de pernas curtas, e o cinza-azulado lê
  como outra família ao lado da ferrugem.
- **Segura a presa pequena**: arrancada a 7 blocos ("burst: charges the leptoceratops, 7,0 blocks off"), mordida e
  presa na boca, **carregada com a cabeça** (a presa ficou a 0,2 bloco do ponto da boca o tempo todo), solta pelo tempo
  depois de **2,3 a 3,0 s** ("hold: lets the leptoceratops go after 2,4 s (time)"); nunca passou de 3 s.
  `previews/jogo/segura_presa_pequena.gif`.
- **Segura o jogador**: na rodada 2 a mordida pegou ("hold: bites and holds the player") mas a repulsão da própria
  mordida jogava o jogador para fora da boca e ele soltava em 0,4 s ("pulled free"). Corrigido (repulsão do ataque 0,4,
  a presa parada ao fechar a boca, 10 tiques antes de contar a distância); **a medida depois da correção (3 golpes
  soltam; sem golpes, 3 s) ficou para a próxima rodada**: as três últimas se perderam. Na rodada 1 o jogador nem era
  alcançado porque o próprio teste movia a câmera (que é o jogador); corrigido no teste.
- **Canibal**: um faminto (fome 30) comeu a carcaça de um Majungassauro morto, carne 7 → 1 ("cannibal: eats the carcass
  of a majungasaurus"); um faminto (fome 10) pegou o vizinho a 15% de vida em 0,1 a 1,3 s ("cannibal: hunts the wounded
  majungasaurus #1952 (28/186, own hunger 11)"), segurou-o (grande demais para carregar: preso no lugar) e o matou.
  `previews/jogo/canibal_come.gif`, `canibal_caca.gif`.
- **Briga pela carcaça**: na rodada 1 nunca começou (espera inicial e limite de fome; corrigido); na rodada 2 os dois
  famintos chegaram à carcaça do Edmontossauro e **duelaram desde 4,7 s** (mordidas que seguram, empurrões de domo, um
  contra-golpe de domo no parry), o vencedor comeu (fome 51 e 69 no fim). `previews/jogo/briga_pela_carcaca.gif`.
- **Bebedouro**: foi à poça (20 blocos), **agachou na beira em 4,5 s**, avisou o Tricerátops a 7,9 blocos
  ("waterhole: warns the triceratops off with the dome") e, quando ele foi posto a 4,1 blocos, levantou e o expulsou
  (duelo, mordida que segura, empurrão de domo). Igual nas duas rodadas. `previews/jogo/bebedouro.gif`.
- **Pavio**: o jogador posto a 7,6 blocos levou o domo ("temper: warns the player with the dome at 7,6 blocks") e, posto
  a 4,7 blocos logo depois, foi atacado com a arrancada. (Na rodada 2 o jogador morreu aqui, em modo sobrevivência, e o
  resto da bateria rodou na tela de morte: o teste agora dá resistência ao jogador nessa fase.)
- **Duelos**: Majungassauro contra Majungassauro, **14 golpes acertados**, 5 assinaturas (empurrão de domo), 2
  bloqueios, **nenhum cambaleio**, nenhuma esquiva; contra o Carnotauro, 13 acertados, o Majungassauro aparou **2 vezes**
  e o Carnotauro cambaleou 2 (o Majungassauro nenhuma), fim com 147/203 contra 54/133. `behavior_regression.py`: os dois
  duelos passam; as pernas no arquivo passam (1.263 graus/s no máximo, limite 1.550).
  `previews/jogo/duelo.gif`, `duelo_com_carnotauro.gif`.
- **Mandíbula e passos no jogo**: não medidos (a fase rodou com o jogador morto na rodada 2 e se perdeu nas seguintes).
  **Pendente**, junto com o olhar (`look`).
- Fotos em `previews/jogo/` (vistas, cabeça, ao lado do Carnotauro, mordida que segura, solta, laço da sacudida,
  empurrão de domo, guarda da carcaça, ameaça do bebedouro, agachado, arrancada, bote do duelo) e os GIFs acima.
- `./gradlew :fabric:compileJava :forge:compileJava`: compila.

Para refazer só o que ficou pendente (som em 0):
`TERRASSIC_BEHAVIOR_TEST=1 TERRASSIC_BEHAVIOR_SPECIES=majunga,look,jaws,gaits TERRASSIC_GAIT_ONLY=majungasaurus ./gradlew :fabric:runClient --args="--quickPlaySingleplayer partes"`
e depois `python3 tools/validation/behavior_regression.py`.

## Em aberto

- **Teste pendente**: o jogador preso depois da correção (escapar com 3 golpes; sem golpes, soltar aos 3 s), a
  mandíbula, os passos e o olhar no jogo (comando acima).
- **O domo no jogo** pode ler como um chapeuzinho de longe (`previews/jogo/behavior_majunga_head.png`): a base de pele
  ocre e a cúpula escura em degraus. Se incomodar, juntar a base à pele do crânio e clarear a cúpula.
- **Gancho no `DinosaurEntity`** (não mexi): depois que um duelo termina em rendição fora da arena de teste, o
  vencedor e o rendido entram num laço de "lets the beaten go" / retomar o alvo a cada tique (visto com os dois caindo
  no vazio da arena; o `HurtByTargetGoal` põe o alvo de volta). É o mesmo gancho pedido no REFEITO do Carcarodontossauro:
  em `submitTo`, `rival.setLastHurtByMob(null)` e guardar no vencedor o UUID do rendido por 2400 tiques, com `canAttack`
  recusando-o. Do meu lado o log `[majunga]` já não repete.
- **Cor fria**: a primeira entre os grandes predadores; conferir no jogo ao lado dos outros e decidir.
- **Dente caído como item**: fora, até o Rodrigo decidir (estudo 13). O `tooth_spit` é só animação.
- **Ovo e ninho**: o ovo-bloco só trocou a cor (cinza-basalto); a cova rasa em areia seca coberta de capim (especulativo
  no estudo) não foi feita.
- **Vozes antigas**, não ouvidas no jogo; o domo e o bebedouro usam a voz de ameaça.
- **Jovens**: a mesma pele e o mesmo domo do adulto (o filhote real não tinha domo; Ratsimbaholison et al. 2016).
- As abas da sela continuam sem aparecer nas prévias, como nos outros três.
- O bebedouro e a briga pela carcaça em mundo gerado (rio de verdade, manadas descendo para beber) só se veem num
  mundo gerado; o teste usa uma poça na arena plana.
- A mordida do jogador preso é a mordida normal (ataque 11) mais 1,5 por segundo: no modo normal duas mordidas e meia
  segurada tiram meia vida; se ficar duro demais, baixar o dano da mordida que segura.
