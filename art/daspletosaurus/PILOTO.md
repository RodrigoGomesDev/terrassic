# Daspletossauro: piloto do padrão visual da 1.10.1

Terrassic · 08/11/2026 · estudo 13 (Daspletossauro) e estudo 14 ("Decisões do Rodrigo")

O Daspletossauro é o primeiro bicho feito do zero no padrão novo. A ideia é o Rodrigo olhar e decidir se o padrão
vai para os outros três predadores da 1.10.1 e depois para os refeitos antigos.

## O que segue o padrão novo

| Regra (estudo 14) | Meta | Medido |
|---|---|---|
| 1 texel = 1 pixel do mundo | 16 ± 2 tx/bloco, `MODEL_SCALE` ≈ 1 | **16,3 tx/bloco**: 164 px a 16,94 px/m (`skin2.PX_PER_M`), escala 0,981, 9,5 m |
| Tons pela silhueta inteira (`skin2.Profile`, `bands`) | dorso escuro, flanco médio, ventre claro como uma forma só | contínuos do pescoço à ponta da cauda, sem faixa por cubo |
| Contraste dorso × ventre | ≥ 70 de luminância | dorso 52 a 69, ventre 137: **68 a 85** |
| Base calma | fração de vizinhos que mudam entre 0,20 e 0,40 | **0,27** (T. rex 0,38, Carnotauro 0,37, Giganotossauro 0,37) |
| Paleta | 20 a 40 cores na pele | **28 cores** no corpo (25 na fêmea); 41/38 com a sela no mesmo atlas |
| Escama só onde existe | sem Voronoi do focinho à cauda | escamas largas só na barriga (`skin.scutes`), placas no topo do focinho, escamas na frente dos pés; o corpo é base com manchas suaves (`mottle`) e pintas espaçadas (`fleck`) |
| Marcas desenhadas, não sorteadas | 1 a 3 por espécie, no espaço do corpo | selas escuras quebradas do ombro à cauda (fecham em anéis na cauda fina), placas e chifres de osso queimado, cicatrizes claras no focinho do macho e bossa pós-orbital ferrugem só nele |
| Olho de 2 a 3 texels | pupila escura e um ponto de cor | pupila em fenda de 2 px, um ponto dourado e um brilho, sombra da sobrancelha sob o chifre lacrimal |
| Cor só contra os refeitos (`colourcheck.py --remade`) | > 10 para cada refeito | macho: Tricerátops 11,8, Dakotaraptor 12,7, Parassaurolofo 13,1; fêmea: Tricerátops 10,7, Dakotaraptor 12,0, Parassaurolofo 12,2. T. rex 22,9, Giganotossauro 20,7, Carnotauro 16,7 |
| Exagero de uma forma-assinatura | 15 a 30% | crânio de 26 px (1,5 m desenhado contra 1,1 m real): fundo (15 px) e estreito (10 px, o do T. rex tem 26) |
| Pés mais largos que a canela, pata ≥ 3 px | | pé de 9 px contra canela de 6; braço de 3 px |
| QA do motor | zero | coplanares 0, pixel ruim 0, pé fora do chão 0 nas 58 animações |

A cor é o "mogno-fumê" do estudo 13, um pouco mais para o vinho (b* mais baixo). Com as peles de verdade ela ficava a
9,6 do Parassaurolofo fêmea e a 11 do Dakotaraptor. O ventre é bege-rosado acinzentado.

## Forma e comportamento (estudo 13)

- Crânio fundo e estreito, chifre lacrimal alto na frente do olho, bossa pós-orbital atrás dele, maxila rugosa
  (pequenas covas), placas chatas no topo do focinho e lábios que cobrem os dentes de cima com a boca fechada.
- São os braços mais longos da família (7 + 5 px, dois dedos), num corpo curto, fundo e pesado. Mede 9,5 m e tem o
  quadril a ~2,6 m.
- Tem 58 animações próprias. Entre elas estão a mordida que esmaga (prende e sacode), `face_bite`, o `parry`, que termina numa mordida na cara, `lunge` e
  `stagger` nos tempos fixos, `steal_roar`, `carcass_guard`, `threat` (rosnado de boca fechada), `jaw_test`, `eat`
  (arranca puxando), `face_rub`, o conjunto vivo (guarda, passos de lado, giro, finta, bloqueio, cansaço, deitar e
  levantar), `knockout` e `hatch`.
- Java (`entity/Tyrannosaurine`, `ai/CarcassStealGoal`):
  - no duelo é paciente, bloqueia muito e quase não esquiva; o contra-golpe é a mordida na cara;
  - é ladrão de carcaça: ruge no predador que está comendo; o que tem menos da metade do tamanho dele foge, e o igual
    ou maior tem de brigar;
  - guarda a carcaça e rosna para quem chega;
  - vive em família: um casal e, às vezes, um jovem a 0,6 do tamanho;
  - tem a sua Sela de Daspletossauro.
- Linhas de log `[dasp] ...` para o teste em mundo gerado: roubo de carcaça, mordida na cara, família, rosnado na
  carcaça e focinho esfregado.

## Prévias

`previews/`: `lateral.png`, `tres_quartos.png`, `frente.png`, `traseira.png`, `cabeca.png`, `cabeca_frente.png`,
`macho_e_femea.png`, `cabeca_macho_e_femea.png`, `com_sela.png`, `ao_lado_do_trex.png` (os dois na escala do jogo) e
`animacoes/*.gif` com tiras de quadros (`*_quadros.png`). Fotos do jogo: `previews/jogo/`.

## Teste no jogo (BehaviorTest, Fabric, som em 0)

Fases `daspleto,look,jaws,gaits,duels` e depois `tools/validation/behavior_regression.py`:
- **Mandíbula:** abre 46 graus. **Pernas:** no máximo 1.061 graus/s no arquivo e 106 graus por tick no jogo (limite
  125). Passou.
- **Duelo** Daspletossauro contra Daspletossauro: 20 golpes acertados e 6 mordidas na cara (assinatura). No total o
  `face_bite` disparou 14 vezes. O perdedor se rendeu com 14/208 de vida. Passou.
- **Roubo de carcaça:**
  - Do Dakotaraptor: ele saiu saciado (largou a carcaça), mas os dois terminaram se atacando, porque o
    Dakotaraptor também é presa e o terceiro da arena incomoda.
  - Do T. rex (maior): virou briga, como pedido.
- **Fotos:** `previews/jogo/` mostra a lateral, os três quartos, a frente, a cabeça, o bicho com o T. rex, a guarda
  da carcaça, o roubo das duas vezes e `duelo.gif`. A textura fica nítida e o olho aparece. Em `with_rex` a câmera ficou longe.
- **Outros itens da regressão:** as falhas restantes da regressão são das fases que não rodaram neste teste.

## Em aberto

- **Regra da luz** (item B6: realce de 1 texel na aresta de cima, sombra embaixo). Ainda não foi feita, porque
  precisa saber se a face de cima do cubo está exposta. Hoje a luz vem só do jogo.
- **Gomos e silhueta** (item 4): ficaram para o próximo patch, como decidido. A cauda ainda tem 5 segmentos, não 3 a
  4, e o modo silhueta automático não foi feito.
- O `gen_species.py` ainda não falha quando um refeito sai da faixa de densidade. Por enquanto só o `build.py` do
  Daspletossauro falha.
- A mordida que quebra armadura (opcional no estudo) não entrou.
- O ovo e o ninho continuam com o desenho gerado antigo (verde). O ninho em cova de margem de rio ainda não foi
  feito.
- As vozes são as antigas (sintetizadas); não foram ouvidas no jogo.
- A sela continua com cara de prancha em alguns ângulos (almofada larga e plana): rever com o Rodrigo.
- No roubo de presa pequena, o ladrão às vezes caça o dono da carcaça em vez de só tomá-la (o Dakotaraptor é presa).
  Há duas saídas: poupar quem fugiu por um tempo, ou deixar assim, porque também é plausível.
- A família em spawn natural (o terceiro do grupo jovem) só pode ser vista num mundo gerado, porque o `/summon` não
  forma grupo.
