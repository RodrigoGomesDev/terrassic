# Por que os modelos do Terrassic parecem "AI slop": estudo visual medido

Data: 07/11/2026. Branch medida: `map/1.9.6` (`59df8774`). Nenhum arquivo do repositório foi alterado.
Pasta do estudo: `/Users/rodrigogs/.claude/jobs/fdaa4423/tmp/slop/`. Os scripts de medição estão em `scripts/` e os números brutos em `ours.json`, `refs.json` e `refs_cobble.json`.

## Imagens deste estudo

| Arquivo | O que mostra |
|---|---|
| `cmp_jogo_lado_a_lado.png` (não versionada: tem capturas de outros mods) | Fotos do jogo (T. rex, Terizinossauro e Tricerátopo refeitos, folha do gerador antigo) ao lado de Jurassic World Reborn, Fossils & Archeology, Prehistoric Fauna e Alex's Mobs. |
| `cmp_um_bloco_de_pele.png` (não versionada: tem recortes do vanilla e do Alex's Mobs) | Um bloco (1 x 1 bloco de pele no jogo) recortado da face lateral principal de 14 espécies nossas e de 6 referências (vanilla e Alex's Mobs, todas a 16 texels por bloco), na mesma escala de tela. |
| [`cmp_densidade_texel.png`](../../art/estudos/1.10/cmp_densidade_texel.png) | Texels por bloco das 59 espécies em escala log, com a faixa de 12 a 20 marcada e a linha em 16. |
| `cmp_texturas_inteiras.png` (não versionada: tem recortes do vanilla e do Alex's Mobs) | Atlas inteiros: T. rex, Terizinossauro, Tricerátopo, Albertossauro, Maiassaura e Euoplocéfalo ao lado de Sniffer, Camelo, crocodilo e caimão de Alex's Mobs. |
| `refs/<mod>/*_v.jpg` | Capturas das galerias do Modrinth: Cobblemon, Alex's Mobs, Mowzie's Mobs, Ice and Fire, Fossils & Archeology Revival, Prehistoric Fauna e Jurassic World Reborn. |
| `refs/vanilla_tex`, `refs/alexs_tex`, `refs/iaf_tex`, `refs/cobblemon_tex`, `refs/cobblemon_geo`, `refs/cobblemon_anim` | Texturas, geometrias e animações abertas usadas **só para medir**. Nada foi copiado para o projeto. |

Ressalva: as fotos das galerias de referência foram tiradas com shader (sombra, bloom e céu). As nossas são do cliente de teste, sem shader e num mundo plano. Por isso a comparação de fotos serve para forma, silhueta e desenho da pele, não para iluminação. As conclusões abaixo se apoiam nas medições, que não dependem de shader.

## Como medi

- **Densidade de texel no jogo** = 16 × (texels da UV por pixel do modelo) / `MODEL_SCALE`. O `MODEL_SCALE` foi lido de `common/.../entity/<Espécie>.java`, gerado por `gen_species.py`. Para as referências: no vanilla e no Alex's Mobs o modelo é desenhado a 1 texel por pixel, com escala 1, ou seja 16 tx/bloco. No Cobblemon, a razão UV medida nas geos (`refs/cobblemon_geo`) é 1,0 e o `baseScale` vai de 0,8 a 1, o que dá de 16 a 20 tx/bloco.
- **Textura**: cores distintas, desvio da luminância, fração de vizinhos que mudam de cor (> 3 de 255) e diferença média entre vizinhos. Script em `scripts/texm.py`.
- **Geometria**: número de cubos e quantos têm alguma dimensão de até 1 px.
- **Animação**: chaves por osso por segundo e tipo de interpolação, em `idle` e `walk`.

## Números principais

| | Refeitos à mão (20) | Gerador antigo (39; 35 ativos) | Vanilla | Alex's Mobs | Cobblemon | Ice and Fire |
|---|---|---|---|---|---|---|
| Texels por bloco | **14,8 a 45,3** (mediana 22,7) | **8,4 a 168** (mediana 18,2) | 16 | 16 | 16 a 20 | (pintado em 2x) |
| Cores por textura | 25 a 53 (mediana 40) | **808 a 5.221 (mediana 1.920)** | 11 a 44 | 11 a 30 | 26 a 38 | 680 a 1.564 |
| Fração de vizinhos que mudam | 0,39 | **0,65** | 0,19 a 0,70 (dragão 0,19, Warden 0,34, Sniffer 0,38) | 0,36 a 0,67 | 0,21 a 0,45 | 0,62 a 0,67 |
| Cubos por modelo | mediana 90; 29% com 1 px ou menos | mediana 63; 46% com 1 px ou menos | ~10 a 30 (estimativa, não medido) | ~20 a 40 (estimativa) | 85 a 145; **50 a 64%** com 1 px ou menos | n/m |
| Chaves de animação por osso por s (walk) | **21 a 24**, todas catmull-rom, em todos os ossos | 6 | n/m | n/m | 0,9 a 1,9, linear e catmull misturados, mais Molang | n/m |

Das 59 espécies, **32 ficam fora da faixa de 12 a 20 tx/bloco**. Entre os 20 refeitos, 12 ficam fora.

---

## Diagnóstico, do maior impacto para o menor

### 1. Cada bicho tem um tamanho de pixel diferente, e quase nenhum bate com o do mundo (impacto: muito alto)

No Minecraft o pixel é a unidade do mundo. A grama, o jogador, a vaca e o Sniffer usam 16 texels por bloco. Por isso, quando um mob tem o pixel do tamanho certo, ele parece "do jogo". O Alex's Mobs e o Cobblemon seguem essa regra, e o Prehistoric Fauna também, como se vê em `refs/prehistoric-fauna/5_v.jpg`, onde os pixels do Anquilossauro têm o tamanho dos das folhas.

No nosso mod a mesma câmera mostra:

- Tarbossauro e Carcarodontossauro a **8,4 tx/bloco**: pixels com o dobro do tamanho dos da grama.
- Velociraptor, Paquicefalossauro, Galimimo e Estiracossauro a **30**, e Protocerátopo a **45**: pixels de 2 a 3 vezes menores que os do mundo.
- Fauna pequena antiga: Compsognato 54, Mononykus 63, Enchodus 108, Ichthyornis 131, Mesodma **168**.

Veja [`cmp_densidade_texel.png`](../../art/estudos/1.10/cmp_densidade_texel.png) e `cmp_um_bloco_de_pele.png` (não versionada: tem recortes do vanilla e do Alex's Mobs). Na segunda, o "um bloco" do Tarbossauro tem 8 x 8 texels borrados e o do Protocerátopo tem 45 x 45.

O motivo é estrutural. Cada rig é desenhado na sua própria escala de autoria (16, 20, 24, 32 ou 48 px/m, conforme o `build.py` de cada um), e depois `gen_species.py` aplica um `MODEL_SCALE` que encaixa o comprimento no tamanho real (`docs/TAMANHOS.md`). O tamanho fica certo, mas o tamanho do pixel vira um subproduto aleatório.

Essa mistura de resoluções ("mixels") é o sinal visual mais clássico de arte montada por máquina ou de origens misturadas. Na mesma cena, um T. rex de 15 tx/bloco ao lado de um Tricerátopo de 23 e de um Velociraptor de 30 parecem vir de três jogos diferentes. Dá para ver isso em `fabric/run/screenshots/behavior_tyrannosaurus_call.png`.

### 2. Duas gerações de arte (CORRIGIDO em 07/11: não vale para o jogo)

O estudo contou 35 espécies antigas entre as "ativas", mas desde a v1.5 só os refeitos (`Eras.REMADE`) nascem no
mundo: os antigos ficam registrados e não aparecem. Decisão do Rodrigo (07/11/2026): os antigos **não contam** na
geração dos novos, nem como referência de forma nem na checagem de cor (`colourcheck` só contra os refeitos). Quando
um antigo for refeito, nasce no padrão novo.

### 3. A mesma "pele de Voronoi" carimbada em todas as espécies refeitas (impacto: alto)

Os **20 refeitos** pintam a pele com a mesma função, `_engine/skin.py: scales()`. Ela gera células de Voronoi com borda escura no lado de baixo e da direita, um brilho no canto de cima e da esquerda, e um tom alternativo sorteado (`h32(...) % 4`). Muda só o tamanho da célula, de 2,2 a 5,4 texels, e a semente.

O efeito é um filtro uniforme, como um "vitral" ou "relevo" de editor de imagem: a mesma textura de lama rachada cobre o crânio, o pescoço, a barriga e a cauda, sem hierarquia. Em `cmp_um_bloco_de_pele.png` (não versionada: tem recortes do vanilla e do Alex's Mobs), Giganotossauro, Tricerátopo, Estiracossauro e T. rex têm o mesmo padrão em outras cores.

As referências fazem o contrário. A pele de fundo é calma, quase lisa (o crocodilo e o komodo do Alex's Mobs e o Camelo vanilla). O detalhe é **desenhado** e concentrado onde a anatomia pede: as espirais do elefante do Alex's Mobs, as pintas do Terizinossauro do Fossils, o contrassombreado forte do T. rex do JWR, o rosto do Sniffer.

Há dois agravantes no código:

- **O padrão recomeça em cada face.** `face_uv_coords()` usa coordenadas locais de cada face, e não a posição no corpo, que já chega ao shader como `tx.P`. Por isso as escamas são cortadas em toda aresta e em toda junta entre segmentos. É bem visível no pescoço do Terizinossauro em `fabric/run/screenshots/photo_therizinosaurus_browse.png`, onde cada gomo tem manchas que não continuam no seguinte.
- **A luz do brilho de cada escama está presa ao referencial da face**, não ao mundo. Nas faces espelhadas ou de baixo, o "relevo" aponta para o lado errado, e o olho lê isso como textura sem sentido.

### 4. Corpo feito de gomos soltos e pouca massa na silhueta (impacto: médio a alto)

O número de cubos **não** é o problema. O Cobblemon usa de 85 a 145 cubos, metade com 1 px ou menos (planos de dente, de garra e de nadadeira), e não parece slop. O que pesa é *como* os cubos se juntam.

- Pescoço e cauda são cadeias de caixas do mesmo tamanho, com degraus e frestas visíveis: o pescoço e a cauda do Terizinossauro e a cauda do T. rex em `behavior_tyrannosaurus_look_back.png`. Nas referências, a cauda ou o pescoço é uma peça longa que afina em 2 ou 3 segmentos que se sobrepõem.
- Patas e pés finos e "flutuando" sob um tronco grande: o Terizinossauro tem quatro dedos de 1 px por pé. As referências exageram o volume dos pés e das patas (o elefante do Alex's Mobs, o Anquilossauro do Prehistoric Fauna).
- **A fidelidade é misturada.** O olho tem íris em degradê com reflexo, em 8 a 10 texels, enquanto o corpo é feito de blocos grandes. O contraste de nível de detalhe dentro do mesmo bicho também denuncia geração automática. O Sniffer, o Warden e o Cobblemon usam olhos de 1 a 3 texels, ou no máximo um bloco de cor.
- O realismo de proporção (tamanho real, `docs/TAMANHOS.md`) não vem acompanhado de estilização. As referências exageram uma ou duas formas por bicho (a cabeça e o maxilar do T. rex do JWR, a gola, as presas). Nas nossas, tudo tem o mesmo peso.

### 5. Leitura de valores: pouco contraste entre grandes áreas e muito contraste dentro delas (impacto: médio)

No atlas, o desvio da luminância dos refeitos (mediana 45,7) está dentro da faixa das referências, de 17 a 65. O problema é *onde* esse contraste está. Ele está dentro da escama, entre a borda escura e o brilho da célula, e não entre as massas do corpo (dorso escuro, flanco médio, barriga clara).

O T. rex refeito tem 65% dos pixels nas duas faixas mais escuras e só 3% acima de 153 de luminância. No jogo ele vira uma massa verde-escura com ruído. O T. rex do JWR, ao contrário, tem dorso escuro, flanco médio e barriga e maxilar quase brancos, e a silhueta se lê de longe. Compare as duas fotos no alto de `cmp_jogo_lado_a_lado.png` (não versionada: tem capturas de outros mods).

As faixas laranja diagonais do nosso T. rex cruzam as caixas sem acompanhar a anatomia. Parecem uma decalcomania aplicada, não uma marca do animal.

### 6. Cor própria a qualquer custo (impacto: médio-baixo)

A regra "cada espécie com cor só dela" (`docs/CORES.md`) empurrou paletas para tons pouco naturais: o Tricerátopo ameixa ou lavanda, o Estiracossauro rosa-argila, o Parassaurolofo ruivo-rosado. Isoladas, essas cores são calmas. No conjunto, parecem uma paleta sorteada de propósito para não repetir, outro sinal de geração.

As referências diferenciam espécies pela **forma e pelas marcas** (pintas, listras, máscara, cor da gola) sobre bases naturais que se repetem sem problema: há vários marrons e verdes no Prehistoric Fauna.

### 7. Animação contínua demais (impacto: médio-baixo, hipótese ainda não verificada em vídeo)

O `walk` dos refeitos tem **21 a 24 chaves por osso por segundo**, todas catmull-rom e em todos os ossos. É uma senoide gravada quadro a quadro. O Cobblemon usa de 0,9 a 1,9 chaves por osso por segundo, com poses-chave, interpolação linear e catmull misturadas, e Molang só para respiração.

O resultado provável é movimento sem pose, sem pausa, sem antecipação e sem impacto: tudo oscila o tempo todo com a mesma suavidade. É a cara de animação procedural. Isso combina com a camada `LivelyMotion`, que soma mais mola e balanço por cima. Para confirmar, vale assistir aos GIFs do `BehaviorTest` com esse olhar.

### Hipóteses descartadas pelos números

- **"Cubos demais ou pequenos demais"**: o Cobblemon tem mais cubos e mais cubos de 1 px do que os nossos refeitos.
- **"Paleta grande demais" nos refeitos**: entre 25 e 53 cores, eles estão dentro do padrão vanilla e Cobblemon. Isso só vale para as espécies antigas.
- **"Ruído demais" nos refeitos**: a fração de vizinhos que mudam (0,39) está na faixa do Sniffer e do Warden. O problema é o *tipo* de padrão, que é uniforme, sem forma e cortado por face, não a quantidade.

---

## Decisões do Rodrigo (07/11/2026)

- **Agora (1.10.1), nos quatro predadores primeiro:** item 1 (pixel do tamanho do mundo), item 2 (os antigos não contam)
  e item 3 (trocar o Voronoi carimbado). O Rodrigo analisa os quatro no jogo e só depois decidimos levar o padrão aos
  outros refeitos.
- **Referência de estilo:** Alex's Mobs e os mods do Raxiores (Raxiores of Raxiore), **não** o T. rex do Jurassic World
  Reborn (Voronoi extremo). Nunca os modelos antigos do Terrassic como referência.
- **Manter os detalhes:** os refeitos são bem mais detalhados que os antigos e os detalhes dão personalidade a cada
  bicho; o que falta é **padrão** (mesmo pixel, mesma lógica de pele), não menos detalhe.
- **Item 4 (gomos e silhueta):** fica para o próximo patch.
- **Itens 5 e 6 (valores, cor a qualquer custo):** validar depois, com os quatro prontos.
- **Item 7 (animação):** não é problema para o Rodrigo; fica como está.

## Plano

### A. Padrão de densidade de texel

- **Regra: 16 tx/bloco no jogo, com tolerância de ±2.** Em vez de desenhar em px/m e escalar depois, o rig passa a ser desenhado em pixels do jogo, já no tamanho real.
- Em fórmula: `px_por_metro_de_autoria = 16 × METRE (1,059) / MODEL_SCALE_alvo`. Com `MODEL_SCALE` = 1, isso dá **16,9 px/m** para todo o mod.
- Exceção explícita para os gigantes (saurópodes de 30 a 40 blocos e o atlas acima de 512): no máximo **12 tx/bloco**, nunca 8.
- Exceção para os bichos minúsculos (Mesodma, Ichthyornis, Enchodus): eles ganham *poucos* texels, nunca mais do que 32 tx/bloco. Um Mesodma de 0,3 bloco deve ter de 5 a 6 texels de comprimento, como o Silverfish ou a Abelha do vanilla. Vale aceitar um leve exagero de tamanho, documentado em `TAMANHOS.md`, se ficar ilegível.
- Implementação, só ferramenta e sem mudar arte por enquanto: `gen_species.py` calcula e imprime o tx/bloco de cada espécie (a mesma conta de `scripts/measure_ours.py`) e **falha a geração** quando um refeito novo sai da faixa. Os 12 refeitos que estão fora da faixa entram na fila de reautoria.

### B. Receita de textura, que substitui o Voronoi uniforme

1. **Estrutura de valores primeiro, em 3 massas por bicho**: dorso escuro, flanco médio e ventre claro. A diferença entre o dorso e o ventre deve ser de pelo menos 70 de luminância. O contrassombreado é calculado na posição **do corpo** (`tx.P`, altura relativa ao osso pai), não na face.
2. **Base calma**: de 3 a 4 tons por material, com variação de 1 texel em no máximo 15 a 20% dos pixels. A fração de vizinhos que mudam deve ficar entre 0,20 e 0,40 (a faixa do Cobblemon, do Warden e do Sniffer).
3. **Marcas desenhadas, não sorteadas**: de 1 a 3 marcas por espécie que acompanhem a anatomia, como listras que seguem as costelas, máscara do olho, sela no dorso, faixas na cauda ou pintas na garupa. Elas são descritas como formas (ASCII ou vetor por osso, via `proto.stamp`, que já existe) e contínuas entre os cubos, porque o desenho usa coordenadas do corpo.
4. **Textura de material só onde ela existe**: escamas grandes ou osteodermos no dorso, placas, escamas da barriga em faixas (`skin.scutes`) e queratina nos chifres. O Voronoi fica restrito a esses lugares, com **célula ≥ 4 texels** e sem brilho por célula. No resto do corpo, nada de padrão.
5. **Paleta limitada**: de 20 a 40 cores no atlas inteiro, com rampas compartilhadas por material (pele, ventre, queratina, boca e olho). A meta medida é de 25 a 45 cores, desvio de luminância entre 30 e 50 e saturação de 0,20 a 0,45 (`docs/CORES.md` segue valendo).
6. **Uma regra de luz só**: um destaque de 1 texel na aresta de cima dos cubos voltada para o céu e uma sombra de 1 texel na aresta de baixo, calculadas no mundo (pelo vetor normal da face), nunca por célula.
7. **Olho em 2 a 3 texels**: pupila escura e um ponto de cor ou de brilho. Sem degradê na íris.
8. **Diferenciar espécies pela marca e pela forma**, não pelo matiz. Bases naturais (oliva, pardo, cinza, areia) podem se repetir entre espécies distantes. O `colourcheck.py` passaria a medir também a **diferença de padrão** (marcas), além da média CIELAB.

### C. Regras de forma, cubos e estilização

- **Tronco, pescoço e cauda**: no máximo de 3 a 4 segmentos por cadeia, cada um com sobreposição de 1 a 2 px com o vizinho para não abrir fresta na animação, e afinando de forma monótona. Proibido segmento do mesmo tamanho repetido.
- **Exagero por espécie**: escolher 1 ou 2 formas-assinatura e aumentá-las de 15 a 30% em relação ao fóssil, como a cabeça e o maxilar do T. rex, a gola do Tricerátopo, as garras do Terizinossauro ou a crista do Parassaurolofo. O comprimento total e a altura do quadril continuam reais (`TAMANHOS.md`), então só a distribuição de massa muda.
- **Patas e pés**: espessura mínima de 3 px na pata e de 2 px no dedo para bichos acima de 3 blocos. Pés mais largos que a canela.
- **Planos de 0 px** (como no Cobblemon) para dentes, membranas, penas e espinhos finos, em vez de cubos de 1 px empilhados.
- **Teste de silhueta automático**: renderizar o perfil em preto a 64 px de altura. A cabeça, as patas e a forma-assinatura têm que ser legíveis. O `_engine/shots.py` já renderiza, e falta só o modo silhueta.

### D. Animação

- Trocar a senoide gravada por **poses-chave com tempo**: de 4 a 8 poses por ciclo, com 1 a 3 quadros de pausa no contato e no golpe, `linear` nos impactos e `catmullrom` só nos arcos.
- Deixar a senoide apenas para a respiração e para a ponta da cauda. Na camada `LivelyMotion`, reduzir a amplitude enquanto a animação de ação toca.

### E. Piloto: o **T. rex**

Por que ele:

1. É a cara do mod e aparece em quase toda foto que circula. É ali que a fama de "AI slop" nasce.
2. Já está a 14,8 tx/bloco, então o piloto isola o efeito da **receita de textura e forma**, sem confundir com a mudança de escala.
3. Tem um dos rigs mais completos e é a única espécie com alfa, o que testa a receita também na pele do alfa.

Entregáveis do piloto:

- Reautoria em 16 tx/bloco exatos.
- Pele nova com 3 massas de valor, marcas que seguem as costelas e a máscara, Voronoi só no dorso e no crânio, olho de 2 a 3 texels e no máximo 35 cores.
- Cauda em 4 segmentos que se sobrepõem e cabeça e maxilar 20% maiores.
- Ciclo de caminhada em poses-chave.

Como validar:

- As métricas acima, calculadas pelos scripts deste estudo.
- Foto no `PartsShowcase` na mesma pose de `behavior_tyrannosaurus_look_back.png`, montada lado a lado com a atual.
- Teste cego: as duas fotos, sem legenda, para 5 a 10 jogadores do Discord, perguntando qual parece "feito à mão".

Se o piloto passar, aplicar na ordem:

1. Os 12 refeitos fora da faixa de densidade, começando por Velociraptor, Protocerátopo e Estiracossauro.
2. As 35 espécies antigas ativas, que são o maior volume e o maior impacto. Enquanto não forem refeitas, uma medida de contenção barata vale a pena: **reduzir as texturas antigas para no máximo 32 cores** e corrigir o `MODEL_SCALE` dos extremos (Tarbossauro e Carcarodontossauro a 8,4; Mesodma e Ichthyornis acima de 130) com uma reamostragem do atlas. Isso tira o pior do "ruído fotográfico" sem esperar a reautoria.

Todas as regras da casa continuam valendo: tudo é gerado pelo nosso código, as referências de terceiros foram só medidas e nada foi copiado, os tamanhos seguem `docs/TAMANHOS.md` (o exagero muda proporção interna, não o comprimento) e as cores continuam naturais e calmas (`docs/CORES.md`).

## Padrão v2 (08/11/2026): sem cara de IA, mas sem ficar simplório

O Rodrigo viu o Majungassauro ao lado do Carnotauro: "extremamente simplório", sobretudo a cabeça; reproduzido assim,
"todos vão ser mais do mesmo". Medido nas texturas (cabeça = ossos head/skull/jaw e filhos; vizinhos que mudam de cor):

| | cabeça: vizinhos que mudam | cabeça: cores |
|---|---|---|
| Carnotauro, T. rex, Giganotossauro (refeitos antigos) | 0,24 a 0,38 | 21 a 29 |
| Daspleto, Alberto, Carcharo, Majunga (padrão v1) | 0,14 a 0,18 | 20 a 24 |

O v1 acertou o pixel do mundo e a pele contínua, mas levou a "base calma" para a cabeça, que é onde o olho do jogador
vai primeiro. O v2 mantém o v1 no corpo e devolve o detalhe à cabeça, com números:

- **A cabeça é o foco:** vizinhos que mudam na cabeça ≥ 0,24 (o Carnotauro) e pelo menos 1,3x os do corpo;
  rugosidade, placas e escamas desenhadas no espaço do corpo (contínuas), narina marcada, linha da boca escura.
- **Dentes à mostra:** de lado, com a boca fechada, uma fileira visível (lábios cobrem a base, não o dente inteiro).
- **Olho com órbita:** contorno escuro, arcada por cima, íris de cor de 2 texels ou mais e um ponto de brilho.
- **Um ou dois acentos de cor** (saturação ≥ 0,45) em pele de exibição: base do chifre ou do domo, crista, olho.
- **Ornamentos nascem do crânio:** domo, chifre e crista com a base na cor da pele e só a ponta em queratina; nada de
  anel ou prato em volta (o domo do Majungassauro lia como chapéu).
- **Corpo:** continua calmo e contínuo, mas com a textura de escama do próprio corpo a um passo de tom
  (vizinhos que mudam 0,20 a 0,30) e as marcas desenhadas da espécie.
- Checagem: `tools/modelgen/handmade/_engine/headcheck.py` (cabeça x corpo) roda no build dos refeitos novos.

### Resultados do padrão v2 (08/11/2026, branch `pele/v2`)

Os quatro predadores da 1.10.1 refeitos só na cabeça e na escama do corpo; forma, família de cor, tamanho, densidade
(16,1 a 16,5 tx/bloco), marcas do corpo, animações e comportamento ficaram iguais. Medido pelo
`_engine/headcheck.py` no build (macho; a fêmea fica a 0,01 dos mesmos números). "Dentes" = texels de dente visíveis
de lado, com a boca fechada, num lado; "acento" = texels da cabeça com saturação ≥ 0,45, valor ≥ 0,40 e a 20° ou
mais do matiz do rosto (fora boca, dentes e olho).

| | cabeça: cores | cabeça: vizinhos que mudam | corpo: vizinhos que mudam | cabeça / corpo | dentes | íris | acento |
|---|---|---|---|---|---|---|---|
| Majungassauro v1 | 22 | 0,18 | 0,23 | 0,8x | 0,3 | 1 | 110 (o "prato" ocre) |
| **Majungassauro v2** | 23 | **0,35** | 0,27 | **1,34x** | **5,9** | 3 | 39 |
| Daspletossauro v1 | 24 | 0,14 | 0,20 | 0,7x | 0 | 1 | 20 |
| **Daspletossauro v2** | 26 | **0,37** | 0,27 | **1,38x** | **18,5** | 3 | 20 |
| Albertossauro v1 | 20 | 0,16 | 0,20 | 0,8x | 0,3 | 1 | 19 |
| **Albertossauro v2** | 24 | **0,35** | 0,27 | **1,33x** | **11,0** | 3 | 22 |
| Carcarodontossauro v1 | 20 | 0,18 | 0,16 | 1,1x | 1,7 | 1 | 0 |
| **Carcarodontossauro v2** | 25 | **0,37** | 0,24 | **1,50x** | **16,8** | 3 | 74 |
| Carnotauro (referência) | 29 | 0,24 | 0,28 | 0,9x | 12,9 | 5 | 3 |

O que mudou em cada um (`tools/modelgen/handmade/<espécie>/`):

- **Comum** (`_engine/head2.py`): escamas pequenas e rugosidade do rosto no espaço do corpo, a um passo de tom
  (`face_scale`, `rugose`); fileira de dentes de cima pendurada 0,25 px **fora** da mandíbula e dentro do lábio, então
  aparece de boca fechada e o lábio cobre só a base; linha escura da boca e lábio um tom acima; olho de 3 x 2 por
  dentro (íris de 3 texels, pupila em fenda, brilho) com contorno escuro sob a arcada; narina com borda clara; escama
  do corpo em `skin2.scales` só na borda sombreada, a um passo de tom (célula de 6 a 8 texels).
- **Majungassauro**: o domo deixou de ser chapéu: dois inchaços da própria pele inclinados para a frente sobre o teto
  do crânio e só a coroa de queratina gasta e clara, sem aba nem anel. O ocre do macho saiu do domo (embaixo dele lia
  como aba; num primeiro rascunho, em faixa no domo, ainda lia como chapéu na foto do jogo) e foi para a arcada rugosa
  por cima do olho e uma mancha atrás dele; nasais com nós; íris laranja.
- **Daspletossauro**: chifre lacrimal com base de pele e ponta de osso queimado; protuberância pós-orbital ferrugem
  no macho; prateleira da arcada entre os dois; placas do focinho separadas por costuras de pele; cicatrizes do macho;
  dentes em D de 3 linhas.
- **Albertossauro**: crista lacrimal triangular em dois degraus (base de pele, pele de exibição ferrugem no macho,
  ponta de queratina); arcada baixa; faixa escura do olho até a articulação da mandíbula; dentes finos.
- **Carcarodontossauro**: prateleira da arcada e crista nucal com lados de pele e só a borda de chifre; pele de
  exibição vermelho-tijolo sobre o olho e na crista nucal do macho; sulcos inclinados do maxilar; máscara; lâminas de
  3 linhas. O corpo, que estava liso demais (0,16), ganhou a escama (0,24).
- **Conserto em `skin2.step`**: subir um tom a partir de `k4` caía no cinza da barriga (`b0`) e punha pontos claros
  soltos na pele escura; agora sobe para `k5`.

Cor (`colourcheck.py --remade`): todos a 10 ou mais de qualquer refeito (mais perto: Majungassauro 12,2 do
Anquilossauro, Daspletossauro 11,1 do Dakotaraptor, Albertossauro 11,2 do Anquilossauro, Carcarodontossauro 12,6 do
Protocerátopo). Ícones do mapa regenerados (`tools/spritegen/map_icons.py`).

Imagens: `art/<espécie>/previews/v2_cabeca_antes_depois.png` (v1, v2 e Carnotauro, macho e fêmea, mesmo ângulo),
`lateral.png` e `tres_quartos.png` atualizadas, e as folhas
[`padrao_v2_cabecas.png`](../../art/estudos/1.10/padrao_v2_cabecas.png) (as quatro v2 ao lado do Carnotauro e do
T. rex, 3/4) e [`padrao_v2_cabecas_perfil.png`](../../art/estudos/1.10/padrao_v2_cabecas_perfil.png) (de lado, boca
fechada).

No jogo (08/11/2026, cliente Fabric com som zerado, `TERRASSIC_BEHAVIOR_SPECIES=jaws,look,daspleto,alberto,carcharo,majunga`
e depois só `majunga` com a pintura final): as quatro fases rodaram inteiras (roubo de carcaça, bando e perseguição
longa, emboscada, sangramento e arrasto, mordida que segura, canibal, bebedouro, temperamento) e as 22 mandíbulas
medidas passaram em `behavior_regression.py` (Daspleto 33°, Alberto 32°, Carcharo 33°, Majunga 53°; nenhuma gira). As
outras linhas do script falham por falta de medida, porque essas fases não estavam no lote. Fotos da cabeça no jogo:
`art/<espécie>/previews/jogo/v2_cabeca_jogo.png`. Leitura honesta das fotos: Daspleto, Alberto e Carcharo agora
mostram o mesmo tipo de detalhe do Carnotauro (fileira de dentes, olho em órbita com íris de cor, rosto com textura,
acento). O Majungassauro melhorou bastante (o domo virou parte do crânio, dentes e olho aparecem), mas continua o
mais escuro e o de menos dentes à mostra (focinho curto: 4 dentes de lado), então é o que pede o olhar do Rodrigo
primeiro.
