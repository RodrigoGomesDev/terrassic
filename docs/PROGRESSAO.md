# Terrassic: progressão

> **Status: PROPOSTA, aguarda o Rodrigo** (24/10/2026). Nada daqui entra no código antes da opinião dele.
> Pedido: "quero realmente que você veja algo de progressão, alguma coisa do futuro que nem tem o próprio ARK. Quero tudo original."
> Respeita `HISTORIA.md` (Regra 0: nada move o jogador, eras sempre abertas, a história nunca bloqueia o básico),
> `ESCOPO.md` (um mod só, só materiais da época), `ROADMAP.md` (uma era por vez) e `CONQUISTAS.md` (o único "trava" é o salto).

---

## 0. A ideia em uma frase

No ARK você sobe de nível e gasta pontos. **No Terrassic você aprende com o mundo, cria laços com as criaturas e deixa marcas no tempo.**

Não existe "nível do jogador" nem pontos para distribuir. O jogador fica mais forte porque **sabe mais** (observou os animais), porque **os animais dele têm história** (viveram coisas com ele) e porque **o que ele faz no passado aparece no futuro** (a viagem no tempo vira mecânica, não só cenário). Tudo com pedra, osso, couro, fibra e âmbar: o único "material do futuro" do mod é o **Âmbar Temporal**, que mexe com o tempo.

## 1. O que o ARK faz e o que o Terrassic faz diferente

| No ARK | No Terrassic | Por que é melhor para nós |
|---|---|---|
| Nível do jogador e pontos de engrama liberam receitas | **Descobertas:** cada receita nova vem de **ver um animal fazer algo** (a Maiasaura cobrindo o ninho com folhas ensina o Ninho de Folhas) ou de uma página da Katarina | É o "somos cientistas" virando jogo. Faz o jogador olhar os animais em vez de grindar |
| Nível do dino e pontos em atributos | **Laço e Veterania:** o dino melhora no que ele **faz com você** (quem corre fica rápido, quem carrega fica forte), com memória, temperamento e cicatrizes | Cada dino vira um personagem único, não uma planilha |
| Imprinting só de filhote | Laço para **todos**; filhote criado começa com laço alto | Domar por nocaute também cria vínculo, com o tempo |
| Mutações aleatórias que viram números | **Linhagem visível:** tamanho, padrão, cor e crista herdados dos pais, e **Marcas da Fenda** que nascem nas tempestades | O jogador vê a genética no bicho, não só na tela de status |
| Tecnologia moderna (metal, eletricidade, Tek) | **Instrumentos de Âmbar:** a única "tecnologia avançada" mexe com o tempo (ver o passado de um fóssil, guardar um dino num casulo de âmbar, despertar um fóssil) | Mantém a regra da história (nada moderno atravessa) e ainda dá o "uau" de alta tecnologia |
| Mundo estático: o dino nasce, você mata, ele renasce igual | **Ecologia viva:** a região sente a caça, as manadas lembram de você, criaturas lendárias com nome aparecem | O mundo reage ao jogador |
| Nenhuma consequência entre mapas | **Ecos no tempo:** o que você faz numa era mais antiga aparece nas eras mais novas que já visitou | **Isso nenhum jogo de dinossauro tem.** É o sistema assinatura do Terrassic |

## 2. Os sete eixos

Cada eixo é independente: pode entrar sozinho, e nenhum trava a história (Regra 0). Todos são por jogador em multiplayer, salvo quando o texto diz "do mundo".

### Eixo 1 · Saber: Descobertas (no lugar dos engramas)

**Como funciona.** Cada espécie tem comportamentos reais que já existem no jogo como animação ou IA (pastar, chamar a manada, chocar, cavar, mergulhar para pescar, dar cabeçada, caçar em bando, migrar). Quando um animal **selvagem** faz um desses comportamentos e o jogador está olhando para ele (até 24 blocos, ou 64 com a Lente de Âmbar), o jogador ganha a **Descoberta** ligada àquele comportamento. A Descoberta libera uma receita ou uma técnica.

- Aparece um aviso "Descoberta: Trompa de Crista" com o retrato do animal (o toast do HUD da v0.8).
- O Caderno ganha uma aba **Técnicas**: cada Descoberta com o desenho de quem ensinou, o que foi visto e o que ela libera. As que faltam aparecem como "???" com uma dica ("um bico-de-pato que chama a manada ao entardecer").
- As páginas da Katarina continuam ensinando receitas (as do tipo *receita* da `HISTORIA.md` §9). Descoberta e página são os dois únicos jeitos de aprender: nada de nível.
- As receitas básicas (lança, clava, palha, fogueira, tudo o que o vanilla já tem) **nunca** dependem de Descoberta. A Regra 0 continua: construir, plantar, domar e montar funcionam desde o primeiro minuto.

**Descobertas do Capítulo 1** (todas baseadas em comportamento real ou bem aceito):

| Descoberta | Quem ensina | O que o jogador vê | O que libera |
|---|---|---|---|
| Ninho de Folhas | Maiasaura | A mãe cobrindo os ovos com folhas (a vegetação apodrecendo aquece o ninho) | Bloco de ninho que choca ovos 50% mais rápido |
| Calor do Corpo | Citipati | Um adulto chocando sentado no ninho, braços abertos | Chocar segurando o ovo na mão secundária perto da fogueira |
| Trompa de Crista | Parasaurolophus | A manada se chamando ao entardecer | Trompa: chama os seus dinos domados de até 96 blocos |
| Assobio do Bando | Velociraptor, Dakotaraptor | Um bando cercando a presa pelos lados | Comando "flanquear" para os seus predadores pequenos |
| Pedras de Moela | Alamosaurus, Struthiomimus | Um animal engolindo pedrinhas (gastrólitos, achados com fósseis reais) | Ração de Moela: comida que rende o dobro na domesticação de herbívoros |
| Escudo de Cúpula | Pachycephalosaurus | Dois machos dando cabeçadas | Escudo de osso que empurra quem bate nele |
| Golpe de Cauda | Ankylosaurus, Euoplocephalus | A cauda acertando um predador | Clava de Cauda melhorada (atordoa por 1 s) |
| Armadilha de Margem | Deinosuchus | A emboscada na beira d'água | Bloco armadilha de estacas para margens |
| Cerco de Peixes | Spinosaurus | Pescando de pé na água rasa | Cerco de Peixes (bloco que junta peixes aos poucos) |
| Mergulho de Pesca | Pteranodon, Hesperornis | Um mergulho que sai com peixe | Lança de Pesca (acerta na água sem perder força) |
| Gancho de Coleta | Therizinosaurus | As garras puxando galhos | Gancho: colhe folhas e frutos a 4 blocos |
| Rastreio | Edmontosaurus | A migração passando | Pegadas aparecem no chão atrás das manadas e levam até elas |
| Olhos da Noite | Troodon | Caçando no escuro | Caçar agachado à noite deixa você 50% menos visível para predadores |
| Couro Curtido | Qualquer carcaça com carniceiros | Carniceiros limpando um esqueleto | Curtir couro com casca de árvore (couro rende 2) |
| Carne Seca | Página da Katarina | (página) | Carne seca na fogueira: não estraga e mata a fome devagar |
| Cola de Resina | Mesa de Pesquisa, ao estudar âmbar | (pesquisa) | Cola de Resina, a base das ferramentas compostas e das selas melhores |

Cada era futura ganha as suas (Penas e Cinzas: penas isolantes do Yutyrannus, ninhos em colônia do Hamipterus; Jurássico: a cauda-chicote do Diplodocus, monção e pinhão; Triássico: guardar água como o rincossauro; Era do Gelo: roupas de pele vendo o mamute).

**Perguntas de Campo (domínio de uma espécie).** Cada espécie tem **3 perguntas** no Guia, geradas pelas marcas que ela já tem no gerador (`herd`, `call`, `forage`, `scoop`, `egg_boost`, `brooder`, `night_guard`, migração, ninho): "Veja um Parasaurolophus chamar a manada", "Ache um ninho", "Veja ele fugir de um predador". Respondendo as 3, a espécie chega a um novo nível do Guia, **Dominada**, depois de Estudada. Dominada libera a **técnica de montaria** dela (Eixo 2). Como sai das marcas, funciona sozinho para as 1.203 criaturas do bestiário.

### Eixo 2 · Laço: cada criatura com história

**Laço** vai de 0 a 100, em cinco estágios, e fica salvo no próprio animal:

| Estágio | Laço | O que muda |
|---|---|---|
| Desconfiado | 0-19 | Obedece de perto, pode fugir se ferido |
| Tolerante | 20-39 | Segue sem se perder, aceita sela |
| Companheiro | 40-59 | Atende a Trompa de longe, defende você mesmo sentado |
| Parceiro | 60-89 | Libera a técnica de montaria da espécie (se a espécie estiver Dominada) |
| Inseparável | 90-100 | Se você morrer, ele fica guardando o lugar e os seus itens até você voltar |

**Sobe com:** comida preferida, viajar montado, lutar junto, dormir perto dele (fogueira e cama a até 8 blocos), escovar com o Pincel de Pelo, salvar ele de um ataque. **Desce com:** fome, deixar ele ferido muito tempo, bater nele. Filhote chocado perto do jogador começa em 40; domado por nocaute começa em 0 (e sobe com a eficiência).

**Memória e temperamento.** Cada animal guarda até 12 lembranças com data: "nasceu do ovo que você chocou", "venceu um Carnotaurus ao seu lado", "quase morreu na Tempestade da Fenda". Elas aparecem no Caderno, na aba nova **Companheiros**, como um pequeno diário escrito na voz da Katarina (ela "adotou" o seu bicho nas anotações). Das lembranças nasce um traço de temperamento, que muda o comportamento de leve:
- **Corajoso** (venceu muitas lutas): não foge com pouca vida.
- **Arisco** (se feriu muito): foge antes, mas avisa de predadores.
- **Curioso** (viajou muito): às vezes traz um item achado no chão.
- **Glutão** (comeu muito da sua mão): domesticação de filhotes perto dele é mais rápida.
- **Leal** (Inseparável há muito tempo): segue você entre as eras sem precisar estar no anel do Altar.

**Cicatrizes.** Depois de sobreviver a uma luta dura (vida abaixo de 20%), o animal ganha uma cicatriz desenhada por cima da textura, em 3 tamanhos e lugares por arquétipo. Ninguém tem um T. rex igual ao seu. Dá para desligar na configuração.

**Veterania.** Em vez de pontos, o animal melhora devagar naquilo que **faz**: quem corre montado ganha velocidade, quem carrega ganha carga, quem luta ganha vida e dano, quem voa ganha fôlego, quem nada ganha mergulho. Cada atributo vai até **+25%**, sobe rápido no começo e devagar no fim. Um Pteranodon velho de viagem é mais rápido que um recém-domado, sem planilha nenhuma.

**Técnicas de montaria** (Parceiro + espécie Dominada), uma por espécie, na tecla de ataque secundário:

| Espécie | Técnica |
|---|---|
| Tyrannosaurus | Rugido: predadores menores fogem, herbívoros entram em pânico |
| Triceratops, Styracosaurus | Investida: carrega em linha reta derrubando quem estiver na frente |
| Ankylosaurus | Giro da Clava: acerta tudo em volta |
| Parasaurolophus, Corythosaurus | Chamado: a manada selvagem por perto segue você por um tempo |
| Pteranodon | Mergulho: agarra uma criatura pequena e solta do alto |
| Quetzalcoatlus | Decolagem em quatro apoios: levanta voo parado, sem correr |
| Spinosaurus | Pesca: pega peixes andando na água rasa |
| Therizinosaurus | Colheita: as garras colhem árvores e plantações em volta |
| Brachiosaurus e titãs | Alcance alto: colhe folhas e frutos de copas altas |
| Mosasaurus | Arrancada: avanço rápido debaixo d'água |

**Quando um companheiro morre**, ele deixa um **Dente de Lembrança** com o nome dele. Enterrar o dente com uma lápide de osso guarda a memória no Caderno e, se for numa era mais antiga, o fóssil dele aparece no futuro (Eixo 5).

### Eixo 3 · Linhagem: genética que dá para ver

Cada criatura nasce com **genes visíveis**:
- **Tamanho:** dentro da faixa real da espécie (`TAMANHOS.md`). Um T. rex adulto vai de 11 a 13 m, como os fósseis; os filhotes também variam. Os maiores ganham nome no Guia ("porte Sue").
- **Padrão e cor:** listras, manchas e tons dentro de uma paleta plausível para a espécie (variantes de textura geradas pelo `modelgen`).
- **Crista, chifre e babado:** escala do osso de exibição (machos com crista maior, como já é hoje por sexo).
- **Temperamento de base:** puxa o traço do Eixo 2 para um lado.

**Herança:** o filhote fica perto da média dos pais, com uma pequena variação. Assim criar dinos grandes, com o padrão que você gosta, é um projeto de longo prazo.

**Marcas da Fenda:** um ovo que choca durante uma Tempestade da Fenda, ou perto de Âmbar Temporal, pode nascer com uma Marca: olhos cor de âmbar, listras que brilham fraco no escuro, ou um traço raro (pele que resiste a fogo, fôlego longo). No máximo **3 Marcas por linhagem**, então ninguém empilha mutação infinita como no ARK.

**Árvore da Linhagem:** no Caderno, cada animal mostra pais, avós e filhotes, com retrato e os genes.

> Esta parte encosta no pedido do Rodrigo de filhotes e adultos com tamanhos diferentes. Se a frente de tamanhos implementar a variação antes, a Linhagem só acrescenta a herança por cima.

### Eixo 4 · Âmbar: a tecnologia do tempo

A única "alta tecnologia" do mod. Cada era tem o seu âmbar, cada vez mais forte (o triássico é o mais forte, `HISTORIA.md` §8), e cada instrumento pede âmbar daquela era ou de uma mais antiga.

| Instrumento | Era | O que faz |
|---|---|---|
| Lente de Âmbar | Cap. 1 (já existe) | Observar de longe, registrar no Guia, apontar o Refúgio |
| **Eco de Âmbar** | Cap. 1 (v0.9) | Usado num fóssil, num Ossuário ou num acampamento da Katarina, mostra **o passado daquele lugar**: silhuetas translúcidas cor de âmbar repetem por 10 segundos a cena (como o animal morreu, o que a Katarina fez ali). Revela a silhueta no Guia, às vezes mostra onde algo foi enterrado |
| **Casulo de Âmbar** | Cap. 1 (v0.9) | Guarda um dino domado num casulo do tamanho de um item, para levar no inventário e soltar depois. É o "criopod" do ARK, mas explicado pela história: o âmbar para o tempo dentro dele |
| **Bússola da Fenda** | Cap. 2 | Aponta a anomalia mais próxima (Ilha do Tempo, criatura da Fenda, fragmento) |
| **Despertar Fóssil** | Cap. 2 | Na Mesa de Pesquisa: um esqueleto completo (crânio + 3 ossos da mesma espécie) + Âmbar Temporal voltam o tempo do fóssil e viram um **Ovo Desperto**. A criatura nasce como **Eco**: marcada de âmbar e estéril. Dá para ter um Allosaurus no Cretáceo antes de ir ao Jurássico, mas a era dele continua sendo o lugar para ter uma manada |
| **Relógio de Âmbar** | Cap. 3 | Bloco que acelera o tempo em volta: ovos, plantações e filhotes crescem 2x num raio de 8 blocos |
| **Cápsula de Âmbar** | Cap. 2 em diante | Ver Eixo 5 |
| Altar do Salto | Cap. 1 (v0.9, já planejado) | O salto entre eras |

### Eixo 5 · Rastro: ecos no tempo (o sistema assinatura)

O jogador viaja **para trás**: do Cretáceo Superior (o Overworld) para o Cretáceo Inferior, o Jurássico e o Triássico. Então, para o mundo, **tudo o que ele faz numa era mais antiga aconteceu antes** das eras que ele já visitou. O Terrassic leva isso a sério:

> **"Nada atravessa a Fenda. Mas o tempo atravessa tudo."**

- **Cápsula de Âmbar.** Numa era antiga, o jogador sela até 9 itens em resina. Quando ele volta a uma era mais nova que já visitou, no mesmo X e Z, enterrada na rocha, está a **Cápsula Fossilizada**. O tempo transforma o que tem dentro: madeira vira **madeira petrificada**, osso vira **fóssil**, couro e comida somem, pedra, sílex e âmbar ficam iguais, **sementes viram Sementes Dormentes** (dá para plantar um ginkgo jurássico no Cretáceo, ou trazer de volta uma planta extinta) e **ovos viram Ovos Fósseis** (que o Despertar Fóssil acorda). É o único jeito de mandar coisas "para a frente".
- **O fóssil do seu companheiro.** Um animal seu que morreu e foi enterrado com o Dente de Lembrança numa era antiga aparece como **fóssil com o nome dele** no Sítio Fossilífero mais próximo do mesmo lugar, nas eras mais novas. Estudar esse fóssil na Mesa abre uma página de memória escrita pela Katarina. É o momento mais emocionante que o mod pode ter, e é 100% mecânica, não cena.
- **Marcas na rocha.** Pinturas e marcos de pedra que o jogador faz numa era antiga aparecem gastos, como traço fóssil, nas falésias do mesmo lugar no futuro. A base que você construiu no Jurássico vira um "sítio arqueológico" seu no Cretáceo.
- **Efeito borboleta (leve).** Proteger os ninhos de um grupo numa era antiga (por exemplo, saurópodes no Jurássico) aumenta um pouco os parentes dele na era mais nova (os titanossauros do Cretáceo). Só para quem presta atenção; o Guia comenta.

**Regras de segurança:** os ecos só andam **para a frente no tempo** e só para eras **já visitadas**; nada é apagado, nada muda sozinho onde o jogador está (Regra 0). Cápsulas e fósseis são do mundo (todos veem), o resto é por jogador.

### Eixo 6 · Mundo vivo: a região sente você

- **Equilíbrio da região.** O mundo é dividido em regiões de 256 x 256 blocos que contam quantos animais de cada espécie morreram ali. Caçar demais uma espécie deixa ela rara por uns dias e deixa os predadores com fome, chegando mais perto da sua base. Deixar os herbívoros em paz traz manadas maiores. O Relatório do Caderno mostra a "saúde" da região.
- **As manadas lembram.** Cada jogador tem uma **reputação por espécie**. Manadas que você nunca atacou (e que você defendeu de predadores) deixam você andar no meio delas e até fazer carinho num filhote. Espécies que você caça fogem mais cedo. Predadores que você venceu muitas vezes passam a evitar você: um veterano é respeitado pelo mundo.
- **Criaturas Lendárias.** De vez em quando surge um animal único, maior, com cicatrizes e um nome ("Velho Cicatriz", "a Rainha do Delta", em 3 idiomas). O Relatório lista **Ocorrências** como rumores ("um Tyrannosaurus velho foi visto perto do Delta"). Vencer ou domar uma lendária é uma história; ela não volta a nascer naquele mundo.
- **Crônica do mundo.** Um registro automático dos grandes momentos do mundo (a primeira domesticação, a lendária vencida, a primeira migração vista), para reler no Caderno e mostrar em servidor.

### Eixo 7 · Reconhecimento: títulos

Títulos ganhos por marcos, mostrados embaixo do nome em multiplayer (opcional) e na capa do Caderno: **Naturalista** (Guia da era completo), **Amigo das Manadas** (reputação máxima com 5 herbívoros), **Domador de Gigantes** (um titã Inseparável), **Caçador de Lendas**, **Guardião da Fenda** (final). Título não dá atributo nenhum: é só orgulho. Cada um vira conquista na aba Caderno de Campo.

## 3. Onde cada eixo aparece

| Lugar | O que muda |
|---|---|
| **Caderno de Campo** | Abas novas **Técnicas** (Descobertas) e **Companheiros** (laço, memória, linhagem); Guia com Perguntas de Campo e o nível Dominada; Relatório com a saúde da região, Ocorrências e a Crônica |
| **HUD (v0.8)** | Toast "Descoberta!", "Laço: Parceiro", "Lendária avistada"; o painel de montaria mostra o laço e a técnica pronta |
| **Conquistas** | Aba Caderno de Campo ganha: primeira Descoberta, 10 Descobertas, primeira espécie Dominada, primeiro Inseparável, primeira Cápsula Fossilizada, fóssil de companheiro, lendária, títulos |
| **Dados** | Descobertas, Perguntas e reputação no `Knowledge` (por jogador, já existe); laço, memória, genes e cicatrizes no NBT do animal; regiões, lendárias, cápsulas e ecos num `SavedData` do mundo |

## 4. Como fica uma tarde de jogo (exemplo)

Você está na Lente, escondido no capim, quando a manada de Parasaurolophus começa a se chamar no fim da tarde: **Descoberta: Trompa de Crista.** Na volta, o seu Pteranodon de dois anos (Veterania de voo +18%, Arisco, cicatriz na asa esquerda de quando um Quetzalcoatlus o pegou) quase te derruba de susto: ele avistou alguma coisa. É o "Velho Cicatriz", o Tyrannosaurus lendário que o Relatório mencionava. Você não luta: sopra a Trompa, e o seu Triceratops, Parceiro, chega correndo do outro lado do vale. Três dias depois, no Jurássico, você enterra o Dente de Lembrança desse Triceratops perto do lago. Quando você volta para casa e escava o barranco atrás da sua base, lá está, na rocha: **"Fóssil de Teimoso"**.

## 5. Ordem de implementação proposta

Cada linha é uma fase que compila sozinha. A ordem segue o roadmap: só o que serve ao Capítulo 1 entra antes da v1.0.

| Fase | Conteúdo | Versão | Depende de |
|---|---|---|---|
| P1 | Motor de Descobertas (evento de comportamento visto, aba Técnicas, toast) + as 16 do Capítulo 1 | v0.8 | HUD da v0.8 |
| P2 | Laço, memória, temperamento, aba Companheiros | v0.8 | — |
| P3 | Perguntas de Campo e nível Dominada (geradas das marcas do `gen_species.py`) | v0.8 | P1 |
| P4 | Técnicas de montaria (as 10 espécies da tabela) | v0.8 | P2, P3 |
| P5 | Linhagem: genes de tamanho, padrão e crista, herança, Árvore da Linhagem | v0.8 | frente de tamanhos |
| P6 | Veterania e cicatrizes | v0.9 | P2 |
| P7 | Equilíbrio da região, reputação por espécie, Lendárias, Ocorrências, Crônica | v0.9 | — |
| P8 | Eco de Âmbar (repetição do passado) e Casulo de Âmbar | v0.9 | modelos (camada translúcida) |
| P9 | Títulos e as conquistas novas | v1.0 | P1-P7 |
| P10 | Cápsula de Âmbar, fóssil do companheiro, marcas na rocha, efeito borboleta | v2.0 | a segunda era existir |
| P11 | Despertar Fóssil, Bússola da Fenda, Relógio de Âmbar | v2.0-v3.0 | P10 |

## 6. Decisões para o Rodrigo

1. **Aprovar os eixos** (ou cortar algum). Recomendação: os sete; se precisar escolher, começar por Descobertas, Laço e Ecos no tempo, que são os que o ARK não tem.
2. **Despertar Fóssil:** deixar ter criaturas de eras ainda não visitadas, como "Ecos" estéreis? (Recomendação: sim, estéreis.)
3. **Casulo de Âmbar** (o "criopod" primitivo): sim ou não? (Recomendação: sim, ajuda muito a levar dinos no Altar e alivia o servidor.)
4. **Cicatrizes visíveis** ligadas por padrão? (Recomendação: sim, com opção para desligar.)
5. **Títulos** aparecendo embaixo do nome em multiplayer? (Recomendação: sim, desligável pelo servidor.)
6. **Inseparável guardando os itens** quando o jogador morre: é forte; manter? (Recomendação: sim, só para o jogador dono.)
