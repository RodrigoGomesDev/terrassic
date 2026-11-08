# Albertossauro refeito (1.10.1)

Terrassic · 08/11/2026 · estudo 13 (Albertossauro) e estudo 14 ("Decisões do Rodrigo"), no padrão do piloto do
Daspletossauro (`art/daspletosaurus/PILOTO.md`)

O segundo dos quatro predadores da 1.10.1. Segue o padrão do piloto à risca: mesmo pixel, mesma pele (skin2), mesmo
encanamento de animação e a mesma checagem de densidade no `build.py`. O que muda é o bicho: um tiranossaurídeo
esguio, de pernas longas e cabeça comprida e baixa, que caça em bando.

## Medidas do padrão

| Regra (estudo 14) | Meta | Medido |
|---|---|---|
| 1 texel = 1 pixel do mundo | 16 ± 2 tx/bloco, `MODEL_SCALE` ≈ 1 | **16,5 tx/bloco**: 174 px a 16,94 px/m, escala 0,972, 10 m (o `build.py` falha fora de 14 a 18) |
| Tons pela silhueta inteira | dorso escuro, flanco médio, ventre claro como uma forma só | `skin2.Profile` do pescoço à ponta da cauda |
| Contraste dorso × ventre | ≥ 70 de luminância | dorso 36 a 51, ventre 137: **86 a 101** |
| Base calma | fração de vizinhos que mudam entre 0,20 e 0,40 | **0,28** (macho e fêmea) |
| Paleta | 20 a 40 cores | **26** no corpo; 36 com a sela no mesmo atlas |
| Escama só onde existe | sem Voronoi | escamas largas só na barriga (`skin.scutes`), escamas na frente do metatarso e dos dedos, focinho rugoso; o corpo é base com manchas suaves e pintas espaçadas |
| Marcas desenhadas | 1 a 3, no espaço do corpo | (1) **faixa lateral clara** do ombro a dois terços da cauda, com uma borda escura em cima; (2) **pintas escuras em par** dos dois lados da espinha, do cernelha à cauda; (3) **faixa escura do olho** até a articulação da mandíbula |
| Olho de 2 a 3 texels | pupila escura e um ponto de cor | olho redondo sob a crista, pupila, ponto dourado e brilho |
| Exagero de uma forma-assinatura | 15 a 30% | o crânio comprido e baixo: 25 px (1,5 m desenhado contra ~1,1 m), só 11 px de altura atrás e 9 de largura, focinho de 7 |
| Pés mais largos que a canela, pata ≥ 3 px | | pé de 7 px (três dedos) contra canela de 5; braço de 3 px |
| QA do motor | zero | coplanares 0, pixel ruim 0, pé fora do chão 0 nas **62 animações** |

## Cor (verde-abeto)

Dorso verde-petróleo escuro (`#15291f` a `#1d3a2c`), flanco verde-musgo frio (`#274c3a` a `#427058`), faixa lateral
`#5f8a70`, ventre cinza-líquen (`#6d927c` a `#99b9a5`). A crista lacrimal é ferrugem apagada no macho (`#7d5236`) e
escura na fêmea; a fêmea é meio tom mais clara.

`colourcheck.py albertosaurus --remade` (só contra os refeitos):

| | 1º | 2º | 3º |
|---|---|---|---|
| macho | Anquilossauro **11,2** | Espinossauro 16,2 | Mosassauro 17,8 |
| fêmea | Anquilossauro **11,3** | Espinossauro 16,0 | Mosassauro 16,7 |

A primeira versão (verde mais acinzentado) dava 6,7 do Anquilossauro, como o estudo já avisava (11,9 com amostras
sintéticas). Subi a saturação do verde até passar de 10, sem sair do natural (saturação ≤ 0,5).
O Daspletossauro e o T. rex ficam bem longe (mogno-fumê e oliva quente).

## Forma

- Crânio comprido e baixo (Currie 2003), focinho que desce pouco, nasais rugosas, crista lacrimal curta e
  triangular na frente de cada olho, sobrancelha baixa, lábios sobre os dentes (Cullen et al. 2023), muitos dentes
  finos.
- Pernas longas: canela e metatarso mais longos que nos tiranossauríneos (Currie 2003; Currie et al. 2003), quadril
  a ~3,0 m, pé longo de três dedos, hálux fora do chão (Holtz 2004). Braços mínimos de dois dedos.
- Tronco raso e esguio, pescoço um pouco mais longo e fino, cauda longa e fina (5 segmentos, como no piloto).
- Sela própria leve (Sela de Albertossauro): manta fina de feltro verde, assento baixo à frente com arção pequeno,
  abas curtas, uma cilha, peitoral e estribos de osso. Receita: couro, lã verde, couro de Albertossauro e osso.
- Prévias: `previews/` (lateral, três quartos, frente, traseira, cabeça, macho e fêmea, com sela,
  `ao_lado_do_daspleto_e_trex.png` nos tamanhos do jogo, GIFs em `previews/animacoes/`). Fotos do jogo em
  `previews/jogo/`.

## Animações (62)

O conjunto padrão dos terópodes do piloto (parado, gestos, voz, golpes, comer, descanso, nocaute e `hatch`), o
conjunto vivo (guarda, passos de lado, giro, finta, bloqueio, recuo, rendição, cansaço) e as próprias:

- `walk` passada longa e leve; `run` corrida de verdade; `sprint` a perseguição longa, mais rente e esticada;
  `drive` o jovem tocando a presa, inclinado em arco, cabeça baixa;
- `call_pack` (o adulto chama o bando, cabeça alta, chamado em pulsos) e `answer` (ergue a cabeça e vira para quem
  chamou); `ambush_crouch` (adulto agachado esperando a presa);
- `attack` mordida leve que fecha aos 0,50 s e solta logo; `snap_bite` mordida sem parar, só pescoço e cabeça,
  por cima da corrida; `sidestep` o pulo de lado da esquiva; `pass_bite` mordida de passagem no pescoço do rival
  (0,45 s); `pant` ofegando depois da perseguição longa;
- o trio do duelo nos tempos fixos: `lunge` 1,8 s (golpe aos 0,50 s), `parry` 1,5 s (contra-golpe aos 0,60 s, a
  mordida de passagem), `stagger` 1,6 s.

## Comportamento (`entity/Albertosaurine`, `ai/PackDriveGoal`, `ai/PackAmbushGoal`)

- **Bando de idades misturadas** (Currie 1998; hipótese, e o Guia diz que é): no spawn natural, grupo de 2 a 4, os
  dois primeiros adultos e o terceiro e o quarto jovens a 0,55 a 0,65 do tamanho. Do mesmo bando ninguém cede lugar.
- **Chamado e resposta**: o adulto selvagem que pega um alvo chama o bando (`call_pack`, no lugar do rugido); os
  outros a até 24 blocos respondem (`answer`) e vêm para o mesmo alvo. Só um chama por caçada.
- **A batida**: os jovens que responderam correm em arco pelo flanco da presa, passam para o lado de lá e a
  pressionam; ela foge deles, para os adultos, que esperam agachados (`ambush_crouch`) e dão o bote quando ela chega.
- **Perseguição longa**: não desiste aos 48 blocos nem aos 20 s; vai até 72 blocos ou 30 s sem acertar um golpe,
  correndo (o `sprint`, em vez de espreitar a presa pequena). Depois ofega (`pant`) e fica 25 s sem fôlego: anda
  cansado, 35% mais lento, e não caça.
- **Duelo de corredor** (`DuelStyle`): o que mais esquiva (0,42) e menos bloqueia (0,06) dos tiranossaurídeos,
  circula rápido, pouca paciência; o jab é o `snap_bite`, a assinatura e o contra-golpe são o `pass_bite`.
- Mordida mais fraca que a dos tiranossauríneos (dano 11), corre mais (0,29), segue o alvo até 36 blocos.
- Linhas de log `[alberto] ...` para o teste em mundo gerado: chamado, resposta, batida (arco, pressão, presa
  fugindo, presa entregue), emboscada (espera e bote), perseguição longa (passou do limite dos outros, desistiu,
  recuperou o fôlego), esquiva, mordida de passagem, filhotes e adultos do bando no spawn.

### A perseguição longa sem mexer no `DinosaurEntity`

A desistência fica em `DinosaurEntity.behaviourTick` (privado: 48 blocos ou 20 s sem golpe). Fiz o limite maior só
com métodos que já existiam: enquanto a perseguição própria está dentro dos 72 blocos e 30 s, o `getTarget()` lê
nulo por um tique de vez em quando dentro do passo de IA (`customServerAiStep`), o que reinicia a contagem da base
(nunca no tique em que a base confere a desistência ou o bando lê o alvo); o `runThresholdSqr()` do servidor não
deixa a corrida cansar pela regra da base durante ela; o `canAttack` guarda a desistência própria por 30 s; e o
`hasRoaredAt` faz ele correr atrás da presa em vez de espreitar. Funciona, mas é um contorno: o certo seria um gancho
`chaseLimit()` no `DinosaurEntity` (quando a frente de comportamento liberar o arquivo).

## Teste no jogo (BehaviorTest, Fabric, som em 0)

Fases `alberto,look,jaws,gaits,duels,moves` e depois `tools/validation/behavior_regression.py`:

Quatro rodadas; a última com o código final (`TERRASSIC_GAIT_ONLY=albertosaurus`, `TERRASSIC_DUEL_ONLY=albertosaurus`).

- **Pernas** (regressão): no máximo 1.122 graus/s no arquivo (`run`, shin) e 87 graus por tique no jogo (limite
  125). Passou. **Mandíbula**: abre 32 graus na rodada completa (na última ele quase não mordeu durante a medida: 1
  grau, passa igual). Passou.
- **Duelo** Albertossauro contra Albertossauro: 21 golpes acertados (12 + 9), 3 erros, 6 mordidas de passagem
  (assinatura) e 4 esquivas pelo cérebro do duelo; nenhum bloqueio e nenhum parry, como pedido para o corredor.
  Passou. O perdedor se rendeu com 38/160 (o duelo acabou aos ~15 s), mas aos 20 s estava morto: ver "Em aberto".
- **A batida** (dois adultos e dois jovens com 13.000 e 14.000 de idade contra um Galimimo): um adulto chama ("3
  answer"), os dois jovens respondem e correm o arco (`drive`), passam para trás da presa e a pressionam, ela foge
  deles, chega aos adultos agachados (`ambush_crouch`) e os dois dão o bote ("comes in reach, it strikes", 11 e 12 s).
  142 quadros de `drive`, 157 de emboscada; a presa morreu, o adulto mais perto chegou a 1,7 bloco.
- **Perseguição longa** (presa mantida 14 blocos à frente, sem golpe): o Albertossauro passou do limite dos outros
  ("still on past the others' limit (51 blocks, 9 s)") e desistiu a 77 blocos ("gives up after 77 blocks"), ofegou
  (`pant`), andou cansado 25 s (`walk_tired`, `idle_tired`) e voltou ("has its breath back"). O Daspletossauro, no
  mesmo trilho, espreitou devagar e largou a ~25 blocos pela regra da base (20 s sem golpe).
- **Animações no cliente** (o teste registra o que cada um tocou sozinho): `sprint`, `drive`, `ambush_crouch`,
  `walk_tired`, `idle_tired`, `guard`, `strafe_*`, `call_pack`, `answer`, `pant`, `snap_bite` (14), `pass_bite`,
  `sidestep`, `lunge`, `submit`, além do conjunto padrão.
- **Fotos** em `previews/jogo/` (vistas de lado, três quartos, frente e cabeça, o bicho com a fêmea, o
  Daspletossauro e o T. rex, emboscada, batida, chamado, resposta, mordida de passagem, sprint, ofegar) e
  `duelo.gif`, `batida.gif`, `perseguicao_longa.gif`. As fotos de vista ficaram de longe e às vezes com um bicho do
  ecossistema entrando no quadro: o mundo de teste repõe animais em volta do jogador.
- **Regressão**: o `behavior_regression.py` passou em tudo que é do Albertossauro; as falhas que sobram são das fases
  que não rodaram nesta bateria (água, noite, território e as outras).
- `./gradlew :fabric:compileJava :forge:compileJava`: compila.

## Em aberto

- **O perdedor do duelo morreu depois de se render** (38/160 ao fim do duelo, 0 cinco segundos depois). Não deu
  para ver no relatório se foi o vencedor que voltou nele ou outro bicho do teste; o piloto não teve isso. Olhar no
  próximo teste (a rendição é genérica, `DinosaurEntity.submitTo`).
- **Gancho da perseguição**: trocar o contorno por um `chaseLimit()` no `DinosaurEntity`.
- **O chamado usa a voz de ameaça** (`roarSound()` é gerado na classe da espécie); o chamado próprio fica para as
  vozes novas.
- **Jovens listrados e mais claros** (cor de folhiço, no estudo): a textura é uma só por sexo; um jovem com pele
  própria precisa de suporte no renderizador.
- **Batida em mundo gerado**: o teste usa um bando invocado; o spawn natural do bando (dois adultos e dois jovens) só
  aparece num mundo gerado. A presa que foge dos jovens é empurrada pelo `PackDriveGoal` (o `HerbivoreDinosaur` só foge
  de predadores adultos, e o arquivo está com a outra frente).
- **Regra da luz** (B6), **gomos e silhueta** (item 4) e a falha do `gen_species.py` fora da faixa de densidade: como no
  piloto, ficam para o próximo patch.
- Ovo e ninho continuam com o desenho gerado (só a cor do ovo-bloco mudou para a do bicho); o ninho na borda da mata
  de coníferas não foi feito.
- Vozes antigas, não ouvidas no jogo.
- As abas da sela não aparecem nas prévias (a face de fora fica de fora, `faces=out("east", ...)`), igual ao piloto do
  Daspletossauro: conferir no jogo e, se for o caso, corrigir nos dois.
- O Guia de Bolso agora lista a sela própria do Daspletossauro e do Albertossauro no tópico "Montaria".
