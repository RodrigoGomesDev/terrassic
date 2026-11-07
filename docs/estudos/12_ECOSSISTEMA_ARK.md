# Estudo: um ecossistema divertido como o do ARK, e que faça sentido (07/11/2026)

Pedido do Rodrigo (06/11, noite): "quero um ESTUDO COMPLETO de como podemos melhorar esse ecossistema para ser divertido
que nem ARK e claro fazendo sentido, estude o sistema de ARK e como podemos configurar o spawn dos dinos, onde eles
ficam, como se portam as manadas... à noite carnívoro e herbívoro dormem um do lado do outro". Estudo na 1.9.1; a
**1.9.5 é a versão do ecossistema**.

Fontes: wiki oficial do ARK (ark.wiki.gg) para números de spawn, temperamento e níveis; relatos de jogadores (Steam,
Reddit, Dododex) marcados como tal; Saurian, Path of Titans, The Isle, Beasts of Bermuda, Jurassic World Evolution e
o mod Primal Fear para comparação. Nada copiado; só as ideias e as medidas.

## 1. Como o ARK monta o mundo

**Progressão por região, não por nível.** O mapa é dividido em zonas por bioma (praia, campo, selva, sequoias, pântano,
montanha, neve, cavernas, oceano raso e fundo). Cada zona tem a sua lista de grupos (espécie, peso, tamanho do grupo:
"Dodo 1-5") e um número desejado de criaturas. O nível dos selvagens não depende da zona: o perigo vem de **quais**
espécies nascem ali e **quantas por grupo**. Contas sobre os pesos da The Island: praia 85-90% presas; campo 25-30%
predadores; montanha ~75% agressivos. A mesma espécie muda de grupo conforme a zona (Raptor 1-2 na selva, 3-6 na
montanha; Rex sozinho no campo, em dupla na montanha). Cada espécie tem um teto por região (Giganotossauro 0,01 do
número da zona, Dodo 0,5). Servidores ajustam tudo por arquivo (ConfigAdd/Override/SubtractNPCSpawnEntriesContainer,
DinoSpawnWeightMultipliers, NPCReplacements, DinoCountMultiplier) e limpam os selvagens de tempos em tempos.

**Alfas**: raros, muito mais fortes (~15x a vida), com aura vermelha, só no interior e na montanha.

## 2. Por que o caos do ARK é divertido: temperamentos com regras

- **Dócil** (revida só se provocado), **arisco** (foge e grita), **pavio curto** (avisa alguns segundos, depois
  ataca), **territorial**, **agressivo**, **oportunista** (pega os fracos), **paciente** (espera e dá o bote),
  **noturno**.
- O Rex ataca quase tudo, menos outros predadores de topo. Predadores selvagens brigam entre si: é a cena que os
  jogadores mais citam como "a melhor parte".
- Bandos com líder (Raptor: o líder dá bônus ao bando; Allossauro: bandos de 3 que se juntam).
- Manadas que se defendem (Tricerátops ganha "Rivalidade" com predador grande por perto e defende o ninho); o
  Parassauro dá alarme para a área; a mãe de um filhote luta mesmo sendo de espécie que foge; pegar um ovo enfurece os
  adultos em volta.
- Carnívoros comem o que matam. Crítica comum: o predador continua caçando depois de comer (há mod só para isso).
- **Sono**: no ARK os selvagens não dormem (só os noturnos/diurnos marcados, como o Megalossauro, que dorme de dia e é
  muito mais fraco acordado fora de hora). Ou seja, o que temos (todos dormindo lado a lado) é um problema nosso, e dá
  para fazer **melhor que o ARK**.

Jogos mais realistas: Saurian (fome, sede, cheiro, rastros), Path of Titans (IA que dorme quando cansada, bichos que
fogem para tocas), The Isle (manadas que se movem por dieta, zonas de patrulha, bebedouros e ninhais fixos), Beasts of
Bermuda (incêndios, enchentes, migração), JWE (brigas de dominância que não matam). Críticas ao ARK que evitamos: mapa
"de arena", espécies amontoadas, ilhas só de presas ou só de predadores.

## 3. Como o Terrassic está hoje (código, 06/11)

- **Spawn**: duas fontes. O vanilla por bioma (`ModSpawns`, populações que ficam para sempre) e o `EcoSpawner`
  (errantes: 18 por jogador em terra num raio de 80, 12 no mar, 4 no céu; somem a 96 blocos; carnívoros x0,4). Não há
  zona de perigo, teto por região nem proporção predador/presa por área; a fauna "segue o jogador" e troca a cada ida
  e volta.
- **Caça**: fome < 85 e não saciado. Matilhas puxam os vizinhos; `ShadowHerdGoal` segue manadas. **Defeito**: a regra
  "o mais fraco primeiro" exige `isPrey` e quase todos os grandes excluem filhotes do `isPrey`: o filhote nunca é
  escolhido. Rex, Giga, Tarbo e Carcharo não têm limite de tamanho de presa.
- **Herbívoros**: lutadores não fogem de predador, só revidam; fugitivos fogem de qualquer predador adulto a 14
  blocos, mesmo saciado ou dormindo. Edmontossauro tem sentinela e alarme (mas não à noite).
- **Sono**: `DinoSleepGoal` adormece onde estiver, sem olhar em volta, e só acorda com dano ou alvo. O bebedouro do
  entardecer termina pouco antes do sono: as manadas dormem na beira d'água, com os predadores ao lado.
- **Sem território nem casa**: nenhum animal tem área de vida; predadores de espécies diferentes não se evitam.
- **Migração** não é salva (para ao recarregar).

## 4. O plano da 1.9.5: o ecossistema

Ordem pensada para cada etapa já mudar o que o jogador vê.

### 4.1 Noite que faz sentido (o exemplo do Rodrigo)
- Cada espécie com ciclo próprio: diurna, noturna (Troodon, Mesodma) ou crepuscular (Velociraptor ativo ao amanhecer
  e ao entardecer, cochilo no meio do dia, como na 1.9.1).
- **Herbívoro só dorme seguro**: sem predador acordado ou com fome a 32 blocos; dorme no meio da manada, com uma
  sentinela acordada por turno (a do Edmontossauro passa a valer à noite); antes de dormir a manada se afasta do
  predador e da beira d'água.
- **Predador dorme saciado e longe das manadas**, de preferência na mata ou junto a uma parede de pedra; com fome, à
  noite ele patrulha.
- Quem dorme **acorda** com dano, alarme da manada, jogador correndo perto ou predador caçando a 10 blocos.
- Noturnos ficam mais fortes e rápidos à noite; um diurno acordado de noite fica mais lento (como o Megalossauro).

### 4.2 Cadeia alimentar e temperamentos
- Temperamento por espécie na tabela de `gen_species` (dócil, arisco, pavio curto, territorial, agressivo,
  oportunista, paciente), com os textos no Guia.
- **Presa do tamanho certo**: até ~1,2x o predador (ou o bando somado); topo não caça topo, disputa território ou
  carniça sem matar (o duelo com rendição já existe). Conserta o "mais fraco primeiro" (filhotes e feridos).
- **Come o que mata**: o predador fica na carcaça comendo e depois saciado por minutos (na 1.9.1 já vale para os
  marinhos). Perseguição com limite de distância e tempo.
- Manadas lutadoras ganham "Rivalidade" com predador grande por perto e cercam os filhotes; a mãe defende o filhote;
  mexer num ovo enfurece os adultos.
- Pavio curto: aviso (rugido, exibição) antes de atacar o jogador que chega perto.

### 4.3 Onde cada um vive (spawn por zona)
- Cada habitat (`terrassic:habitat/*`) ganha uma meta de proporção de predadores: margem e área de chegada até 15%,
  planícies 20-30%, mata fechada, pântano e montanha 50-75%. Quanto mais longe da Cratera de Chegada, grupos maiores e
  mais alfas (alfas de outras espécies quando as peles forem aprovadas).
- Tamanho de grupo por zona (o mesmo raptor em 1-2 na mata, 3-5 na montanha) e teto por espécie numa região.
- **População estável**: os errantes deixam de sumir e reaparecer a cada ida e volta; uma região guarda quem vive
  nela (contagem por região salva), e o respawn repõe aos poucos o que morreu.
- Tudo configurável por arquivo (como os containers do ARK): `config/terrassic-world.json` com pesos, grupos, metas
  de proporção e tetos por habitat, além das regras atuais.

### 4.4 Território, casas e rotas
- Área de vida: cada grupo tem um centro (ninho, bebedouro, toca) e volta para ele; predadores marcam território e
  disputam a borda (rugido, exibição, duelo com rendição).
- Bebedouros e ninhais fixos por região; rotas de migração lentas entre pastos, salvas no mundo.
- Bandos com líder visível (Raptor, Dakotaraptor) e bandos que se juntam.

### 4.5 Como vamos medir (BehaviorTest)
Fases novas no teste em cliente: "noite" (onde cada um dorme, distâncias predador/presa às 0h), "cadeia" (quem ataca
quem num vale povoado por 10 minutos), "zonas" (proporção de predadores por habitat em 512x512), "estável" (a mesma
população depois de ir e voltar).
