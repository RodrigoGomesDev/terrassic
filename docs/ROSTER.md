# Terrassic: lista de criaturas e roadmap (por era)

Este é o plano de todas as criaturas do mod e em que versão cada uma entra. O mod é organizado **por era**, seguindo a história em `docs/HISTORIA.md`: cada era vira um capítulo jogável do começo ao fim antes de começar a próxima (ver `docs/ESCOPO.md`). O estilo é o do ARK: mundo primitivo, criaturas selvagens perigosas, domesticação, montarias e criaturas com utilidade. Tudo com cara de época antiga: madeira, pedra, osso, couro e sílex, sem tecnologia moderna.

**Bestiário completo:** a lista de tudo o que pode entrar no mod, com 200 a mais de 300 criaturas por era (1.203 no total, de todos os continentes, incluindo animais pré-históricos que não são dinossauros), está em `docs/bestiario/`. Este arquivo continua sendo o plano de versões: quando uma criatura do bestiário ganhar versão, ela entra aqui.

Para mudar a lista, edite este arquivo. Quando uma espécie for implementada, marque-a como ✅ e adicione-a em `tools/javagen/gen_species.py`.

## Legenda

| Coluna | Significado |
|---|---|
| **Tipo** | 🦖 terrestre · 🪽 voador · 🌊 aquático · 🐊 anfíbio (anda e nada) · 🐾 mamífero |
| **Dieta** | Herbívoro, Carnívoro, Piscívoro (peixe), Onívoro, Insetívoro, Filtrador |
| **Domar** | **Comida**: alimentar até domesticar · **Ovo**: só criado desde o ovo · **Filhote**: animais que pariam filhotes vivos (mamíferos, mosassauros, plesiossauros, ictiossauros), criados desde recém-nascidos · **Nocaute**: derrubar com armas de narcótico e alimentar enquanto dorme (v0.7) · **—**: não domesticável |
| **Montaria** | ✅ montável · 🪑 sela de plataforma (dá para construir em cima) · 🦜 vai no ombro · — não montável |
| **Utilidade** | O papel da criatura domesticada, no estilo ARK |
| **Tamanho** | Comprimento real (ou envergadura nos voadores). No jogo a escala é cerca de metade |

Nota: pterossauros, répteis marinhos, crocodilos antigos e mamíferos não são dinossauros, mas viviam nos mesmos ecossistemas e entram no mod.

## Resumo

| Versão | Era / tema | Criaturas novas | Total |
|---|---|---|---|
| v0.2 ✅ | Primeiros dinossauros | 12 | 12 |
| v0.3 | Cretáceo: fundação da história e do cientista | 3 | 15 |
| v0.4 ✅ | Cretáceo: os céus | 3 | 18 |
| v0.5 | Cretáceo: o Mar Interior | 7 | 25 |
| v0.6 | Cretáceo: planícies, manadas e titãs | 15 | 40 |
| v0.7 | Cretáceo: predadores ápice | 13 | 53 |
| v0.8 | Mundo Terrassic: biomas, estruturas, ambientação, HUD | 0 | 53 |
| v0.9 | O Fim: objetivos, Altar do Salto, chefe | 0 | 53 |
| **v1.0** | **Capítulo 1 "Ecos do Fim" completo** | — | 53 |
| v2.0 | Capítulo 2: Cretáceo Inferior, Penas e Cinzas | 29 | 82 |
| v3.0 | Capítulo 3: Jurássico | 30 | 112 |
| v4.0 | Capítulo 4: Triássico e o final | 24 | 136 |
| v5.0 | Epílogo: Era do Gelo | 14 | 150 |
| junto com a era | Anomalias da Fenda | 2 | 152 |

O Capítulo 3 tem 34 criaturas, mas 4 delas (Stegosaurus, Brachiosaurus, Dilophosaurus, Compsognathus) já existem desde a v0.2. Até a v3.0 elas vivem no mundo normal como "vazamentos da Fenda"; na v3.0 passam a nascer no Jurássico e ficam mais raras no Overworld.

---

# Capítulo 1: Ecos do Fim (Cretáceo Superior, Overworld) — v0.2 a v1.0

## v0.2 ✅ Primeiros dinossauros (já no mod)

| Espécie | Era de origem | Tipo | Dieta | Domar | Montaria | Utilidade hoje / planejada | Tamanho |
|---|---|---|---|---|---|---|---|
| Tyrannosaurus | Cretáceo Sup. | 🦖 | Carnívoro | Ovo | ✅ | Montaria de combate; rugido assusta criaturas menores | 12 m |
| Spinosaurus | Cretáceo Sup. | 🐊 | Piscívoro | Ovo | ✅ (nado na v0.5) | Montaria anfíbia, rápida na água | 15 m |
| Velociraptor | Cretáceo Sup. | 🦖 | Carnívoro | Ovo | — | Caça em bando com o dono | 2 m |
| Triceratops | Cretáceo Sup. | 🦖 | Herbívoro | Comida | ✅ | Montaria tanque; coleta frutas e sementes (v0.6) | 9 m |
| Ankylosaurus | Cretáceo Sup. | 🦖 | Herbívoro | Comida | ✅ na v0.6 | Quebra pedra e minério de forma eficiente | 8 m |
| Parasaurolophus | Cretáceo Sup. | 🦖 | Herbívoro | Comida | ✅ | Montaria rápida para iniciantes; o chamado alerta o bando. O "Mate" da Katarina é um deles | 9,5 m |
| Pachycephalosaurus | Cretáceo Sup. | 🦖 | Herbívoro | Comida | — | Derruba inimigos com cabeçadas | 4,5 m |
| Gallimimus | Cretáceo Sup. | 🦖 | Onívoro | Comida | ✅ | A montaria terrestre mais rápida | 6 m |
| Stegosaurus | Jurássico (vazamento) | 🦖 | Herbívoro | Comida | ✅ na v0.6 | Montaria; coleta frutas e sementes | 9 m |
| Brachiosaurus | Jurássico (vazamento) | 🦖 | Herbívoro | Comida | 🪑 na v0.6 | Montaria gigante; sela de plataforma | 22 m |
| Dilophosaurus | Jurássico (vazamento) | 🦖 | Carnívoro | Ovo | — | Guarda da base | 7 m |
| Compsognathus | Jurássico (vazamento) | 🦖 | Carnívoro | Comida (peixe) | 🦜 na v0.4 | Mascote de ombro, avisa quando há perigo | 1 m |

## v0.3 Fundação da história e do cientista

Sistemas: tela de abertura e "Relatório do Incidente", **Caderno de Campo** (tela própria com Diário, Guia, Katarina e Relatório), Guia de Campo com níveis por espécie, **fósseis** (pincel e cinzel) e **Mesa de Pesquisa**, Lente de Âmbar, Carvão de Esboço, Frasco de Argila, tradução **es_es**, sons próprios, pulo na montaria, tirar a sela, configuração de spawn. Primeiro voo montado simples com o Pteranodon.

| Espécie | Tipo | Dieta | Domar | Montaria | Utilidade | Tamanho |
|---|---|---|---|---|---|---|
| **Pteranodon** | 🪽 | Piscívoro | Comida (peixe) | ✅ | Primeira montaria voadora: leve, rápida, não carrega peso | 6–7 m env. |
| **Mosasaurus** | 🌊 | Carnívoro | Filhote | ✅ na v0.5 | Terror do Mar Interior; nesta versão só selvagem | 15 m |
| **Maiasaura** | 🦖 | Herbívoro | Comida | ✅ | "Boa mãe": vive em colônias de ninhos; filhotes perto dela crescem mais rápido | 9 m |

**Andamento (24/10/2026, feito na nuvem, ainda não compilado):** prontos o Caderno de Campo com as 4 abas, a tela de abertura, o Guia com níveis, fósseis com pincel e cinzel, a Mesa de Pesquisa, o Carvão de Esboço, a tradução es_es, o **Pteranodon** (voo montado simples: decolar, voar para onde olha, bater asas, planar), o **Mosasaurus** selvagem (oceano profundo, caça quem está na água ou de barco, seca se encalhar), a **Maiasaura** (filhotes perto dela crescem 2x mais rápido), o pulo na montaria (espaço, como o cavalo) tirar a sela (com tesoura, porque shift + clique já manda sentar), a **Lente de Âmbar** (luneta com zoom; observar 2 s registra no Guia), o **Frasco de Argila** (resina de abeto ou árvore da selva vira Âmbar Bruto, ingrediente da Lente; levado no inventário, enche com uma Amostra de Sangue ao derrotar um dinossauro, que vale +2 pontos na Mesa de Pesquisa) e a configuração de spawn (`config/terrassic.json`). Falta: sons próprios (plano em `docs/SONS.md`). O DNA e a clonagem a partir das amostras ficam para depois.
Nota científica: o Mosasaurus paria filhotes vivos, sem ovo. Quando ele ficar domável (v0.5), o caminho mais fiel é domar o filhote recém-nascido em vez de chocar um ovo.

## v0.4 ✅ Os céus do Cretáceo (modelos, animações e Java prontos; falta testar no jogo)

Sistemas: voo montado completo (subir, descer, planar, stamina), criaturas de ombro, sela por espécie.

| Espécie | Tipo | Dieta | Domar | Montaria | Utilidade | Tamanho |
|---|---|---|---|---|---|---|
| **Quetzalcoatlus** | 🪽 | Carnívoro | Nocaute (até lá, Ovo) | 🪑 | O maior voador: carrega o jogador e uma criatura pequena nas garras | 10–11 m env. |
| **Hatzegopteryx** | 🪽 | Carnívoro | Nocaute (até lá, Ovo) | ✅ | Voador pesado de combate; a mordida derruba criaturas médias | 10–12 m env. |
| **Ichthyornis** | 🪽 | Piscívoro | Comida (peixe) | 🦜 | Ave de ombro que pesca e traz peixe para o dono | 0,6 m env. |

## v0.5 O Mar Interior

Sistemas: montaria aquática (nadar e mergulhar sem se afogar), sela aquática, criaturas de rio, mar e pântano. O Mosasaurus fica montável (não conta como espécie nova).

Progresso: Tylosaurus ✅ (fase 41: modelo no arquétipo marinho, Java e Guia; selvagem até o nocaute da v0.7). Elasmosaurus ✅ e sistema aquático (fase 42: domar na água, descansar boiando, montar e mergulhar sem se afogar, filhotes de quem nasce vivo; Mosasaurus montável pelo filhote). Xiphactinus ✅ (fase 43: peixe predador de 6 m no arquétipo marinho, selvagem e indomável, caça em grupos pequenos em oceano e oceano profundo). Archelon ✅ (fase 44: arquétipo de tartaruga, pacífica, domada na mão, montaria blindada, ovo grande; nocaute de costas). Hesperornis ✅ (fase 45: arquétipo de ave mergulhadora, bandos na costa, domada com peixe, ovo pequeno). Deinosuchus ✅ (fase 46: arquétipo de crocodilo com patas abertas, anfíbio de rio/pântano/praia, emboscada que deixa a presa lenta, ovo grande). Baurusuchus ✅ (fase 47: crocodilo terrestre ereto no mesmo arquétipo, corredor das planícies secas, ovo pequeno). **v0.5 completa: 7 espécies + Mosasaurus montável.**

| Espécie | Tipo | Dieta | Domar | Montaria | Utilidade | Tamanho |
|---|---|---|---|---|---|---|
| **Mosasaurus** (montável) | 🌊 | Carnívoro | Filhote | 🪑 | Montaria aquática gigante com plataforma | 15 m |
| **Tylosaurus** | 🌊 | Carnívoro | Nocaute | ✅ | Investida com o focinho que atordoa | 13 m |
| **Elasmosaurus** | 🌊 | Piscívoro | Comida (peixe) | ✅ | Pescoço longo; montaria para explorar e pescar | 10 m |
| **Xiphactinus** | 🌊 | Carnívoro | — | — | Peixe predador gigante; comida e amostras | 5 m |
| **Archelon** | 🌊 | Herbívoro | Comida | 🪑 | Tartaruga gigante, lenta e resistente; sela com bolsa | 4 m |
| **Hesperornis** | 🌊 | Piscívoro | Comida (peixe) | — | Ave mergulhadora; traz peixe do fundo | 1,5 m |
| **Deinosuchus** | 🐊 | Carnívoro | Nocaute | ✅ | Crocodilo gigante; emboscada e giro mortal | 10–12 m |
| **Baurusuchus** | 🐊 | Carnívoro | Ovo | — | Crocodilo terrestre rápido; guarda da base | 3,5 m |

## v0.6 Planícies, manadas e titãs

Sistemas: **ecossistema** (cadeia alimentar por tamanho, carcaças, bandos, ninhos selvagens, migração de hadrossauros), inventário de carga, coleta automática, fome e sono, sela de plataforma. Stegosaurus e Ankylosaurus passam a ser montáveis; Brachiosaurus ganha sela de plataforma.

| Espécie | Tipo | Dieta | Domar | Montaria | Utilidade | Tamanho |
|---|---|---|---|---|---|---|
| **Edmontosaurus** | 🦖 | Herbívoro | Comida | ✅ | Montaria de carga básica; manadas enormes que migram | 12 m |
| **Corythosaurus** | 🦖 | Herbívoro | Comida | ✅ | O chamado da crista acalma a manada em volta | 9 m |
| **Styracosaurus** | 🦖 | Herbívoro | Comida | ✅ | Investida com chifres que abre caminho na mata | 5,5 m |
| **Euoplocephalus** | 🦖 | Herbívoro | Comida | — | Guarda; a cauda de clava atordoa | 6 m |
| **Protoceratops** | 🦖 | Herbívoro | Comida | — | Cava e acha raízes e fósseis rasos | 2 m |
| **Struthiomimus** | 🦖 | Onívoro | Comida | ✅ | Montaria leve e rápida | 4,3 m |
| **Thescelosaurus** | 🦖 | Herbívoro | Comida | — | Desenterra raízes e tubérculos | 3–4 m |
| **Pachyrhinosaurus** | 🦖 | Herbívoro | Comida | ✅ | Solta um cheiro que acalma ou irrita os animais em volta | 6–8 m |
| **Therizinosaurus** | 🦖 | Herbívoro | Nocaute | ✅ | Garras gigantes: colhe fibra, folhas e madeira; luta bem | 9–10 m |
| **Deinocheirus** | 🦖 | Onívoro | Comida | ✅ | Braços enormes; pesca e colhe na margem dos rios | 11 m |
| **Alamosaurus** | 🦖 | Herbívoro | Comida | 🪑 | Titanossauro; plataforma para construir em cima | 26–30 m |
| **Saltasaurus** | 🦖 | Herbívoro | Comida | ✅ | Titanossauro pequeno e blindado; montaria resistente | 12 m |
| **Argentinosaurus** | 🦖 | Herbívoro | Nocaute | 🪑 | O maior animal terrestre do mod; uma casa que anda | 35 m |
| **Opisthocoelicaudia** | 🦖 | Herbívoro | Comida | ✅ | Titanossauro da Mongólia; carga média | 12 m |
| **Dreadnoughtus** | 🦖 | Herbívoro | Comida | 🪑 | Titanossauro da Patagônia; plataforma | 26 m |

Progresso: Edmontosaurus ✅ (fase 48: hadrossauro de cabeça chata com bico largo, crista carnuda nos machos e fileira de nós no dorso; manadas de 4-8, montaria; carga chega com os sistemas). Corythosaurus ✅ (fase 49: crista em elmo, chamado que acalma os herbívoros em volta, manadas de 3-6 em floresta e planície, montaria). Styracosaurus ✅ (fase 50: arquétipo ceratopsiano, chifre nasal e escudo de espinhos, investida que quebra folhas e mato no caminho, montaria). Euoplocephalus ✅ (fase 51: arquétipo anquilossauro, meios-anéis no pescoço, pálpebras de osso, clava que atordoa (lentidão e fraqueza); guarda, não montaria). Protoceratops ✅ (fase 52: ceratopsiano de 2 m no mesmo arquétipo, bandos no deserto e savana; cava em chão macio e, domado, traz raízes, legumes, ossos e fósseis rasos; ovo pequeno). Struthiomimus ✅ (fase 53: ornitomimossauro leve de pescoço longo e mãos de gancho, bandos que fogem, onívoro domado com sementes, frutas ou ovos; a montaria mais leve e rápida). Thescelosaurus ✅ (fase 54: ornitópode robusto de nariz no chão, morde se encurralado; cava e, domado, desenterra raízes e tubérculos, sem fósseis). Pachyrhinosaurus ✅ (fase 55: ceratopsiano pesado de bossa nasal no arquétipo, manadas da taiga; almíscar que acalma os herbívoros e atrai os predadores selvagens para si; montaria que abre caminho). Therizinosaurus ✅ (fase 56: terópode herbívoro peludo no rig dos grandes terópodes, garras gigantes, rasgo de garra, pasta puxando folhas das copas (quebra folhas com drops); só pelo ovo até o nocaute; montaria alta). Deinocheirus ✅ (fase 57: ornitomimossauro gigante corcunda de bico de pato no rig dos grandes terópodes; pesca à beira d'água com os braços (domado traz peixe e algas), varredura de braços, domado com peixe ou plantas; montaria alta). Alamosaurus ✅ (fase 58: arquétipo saurópode/titanossauro, dorso nivelado, pescoço de cinco segmentos, cauda-chicote como ataque, osteodermos; domado com folhas; montaria alta, plataforma com os sistemas). Saltasaurus ✅ (fase 59: titanossauro blindado no arquétipo saurópode, pescoço curto, placas ovais sobre pele de ossículos pintada, quilhas nos machos, empina e pisa; domado com folhas; montaria-tanque). Argentinosaurus ✅ (fase 60: o maior do mod no arquétipo saurópode, quadris altos, pescoço de seis segmentos, papada e tubérculos, pisão de uma pata com tremor; só ovo até o nocaute; abre caminho na mata; montaria, plataforma com os sistemas).

## v0.7 Predadores ápice

Sistemas: **nocaute** (zarabatana com dardo de narcótico, boleadeira e ervas soníferas), territórios, ninhos selvagens com ovos para roubar.

| Espécie | Tipo | Dieta | Domar | Montaria | Utilidade | Tamanho |
|---|---|---|---|---|---|---|
| **Giganotosaurus** | 🦖 | Carnívoro | Nocaute (muito difícil) | ✅ | Fica mais forte quanto mais leva dano (fúria) | 12–13 m |
| **Carcharodontosaurus** | 🦖 | Carnívoro | Nocaute | ✅ | Fica mais forte cada vez que mata uma presa | 12 m |
| **Carnotaurus** | 🦖 | Carnívoro | Nocaute | ✅ | Chifres; montaria de combate rápida | 8 m |
| **Tarbosaurus** | 🦖 | Carnívoro | Nocaute | ✅ | Primo asiático do T. rex; mais resistente | 10–12 m |
| **Daspletosaurus** | 🦖 | Carnívoro | Nocaute | ✅ | Caça em casal | 8–9 m |
| **Albertosaurus** | 🦖 | Carnívoro | Nocaute | ✅ | Tiranossauro leve e rápido; caça em bando | 9 m |
| **Majungasaurus** | 🦖 | Carnívoro | Nocaute | ✅ | Abelissaurídeo de Madagascar; arrancada curta muito rápida | 8 m |
| **Dakotaraptor** | 🦖 | Carnívoro | Ovo | ✅ | Raptor grande; montaria de caça ágil que pula alto | 5,5 m |
| **Troodon** | 🦖 | Carnívoro | Ovo | — | Caçador noturno, enxerga no escuro; bom guarda à noite | 2,4 m |
| **Oviraptor** | 🦖 | Onívoro | Comida | — | Aumenta a chance de ovos dos dinos domesticados por perto | 2 m |
| **Citipati** | 🦖 | Onívoro | Comida | — | Choca ovos mais rápido quando fica no ninho | 3 m |
| **Mononykus** | 🦖 | Insetívoro | Comida | 🦜 | Cava cupinzeiros; acha insetos para isca | 1 m |
| **Didelphodon** | 🐾 | Onívoro | Comida | — | Mamífero que rouba ovos; domesticado, acha ovos perdidos | 0,8 m |

## v0.8 Mundo Terrassic

Sem criaturas novas. Sistemas: tipo de mundo "Terrassic" (sem vilas e sem animais vanilla) e suporte ao mundo normal; biomas e flora do Cretáceo; estruturas (Cratera de Chegada, Acampamentos e Refúgio da Katarina com o Mate, Sítio Fossilífero, Colônia de Ninhos, Ilhas do Tempo, Ossuário); páginas da Katarina por jogador; Tempestades da Fenda; céu, névoa, partículas, sons e música; HUD próprio; tela de título; pacote de texturas embutido.

## v0.9 O Fim

Sem criaturas novas. Sistemas: Diário com os 12 objetivos do Capítulo 1, fragmentos de âmbar, Altar do Salto, ritual dos meteoros, chefe **Tirano da Fenda**, Salto Instável, modos Normal/Rápido/Livre, comando `/terrassic capitulo`.

## v1.0 Ecos do Fim

Capítulo 1 completo, testado no Fabric e no Forge, com os três idiomas completos.

---

# Capítulo 2: Penas e Cinzas (Cretáceo Inferior) — v2.0

| Espécie | Tipo | Dieta | Domar | Montaria | Utilidade | Tamanho |
|---|---|---|---|---|---|---|
| **Iguanodon** | 🦖 | Herbívoro | Comida | ✅ | Transforma frutas em sementes; anda em 2 ou 4 patas | 10 m |
| **Ouranosaurus** | 🦖 | Herbívoro | Comida | ✅ | A vela nas costas aguenta o calor; montaria para terras quentes | 8 m |
| **Psittacosaurus** | 🦖 | Herbívoro | Comida | — | Bico que quebra sementes duras e nozes | 2 m |
| **Sauropelta** | 🦖 | Herbívoro | Comida | — | Guarda; espinhos no pescoço | 5 m |
| **Gastonia** | 🦖 | Herbívoro | Comida | — | Coberto de espinhos; quem bate leva dano | 5 m |
| **Amargasaurus** | 🦖 | Herbívoro | Comida | ✅ | Saurópode com espinhos no pescoço; montaria que se defende | 10 m |
| **Nigersaurus** | 🦖 | Herbívoro | Comida | ✅ | Pasta rente ao chão; colhe plantas baixas em quantidade | 9 m |
| **Baryonyx** | 🐊 | Piscívoro | Ovo | ✅ | Montaria de rio; pesca e luta dentro e fora da água | 9 m |
| **Suchomimus** | 🐊 | Piscívoro | Ovo | ✅ | Pescador grande de rio | 11 m |
| **Irritator** | 🐊 | Piscívoro | Ovo | — | Espinossaurídeo de crânio comprido; pescador de lagoa | 6–8 m |
| **Acrocanthosaurus** | 🦖 | Carnívoro | Nocaute | ✅ | Predador de topo da era; montaria de combate | 11,5 m |
| **Concavenator** | 🦖 | Carnívoro | Nocaute | ✅ | Corcunda; caçador de mata fechada | 6 m |
| **Utahraptor** | 🦖 | Carnívoro | Ovo | ✅ | O maior raptor; montaria de ataque | 6–7 m |
| **Deinonychus** | 🦖 | Carnívoro | Ovo | — | Caça em bando de 4 a 6 | 3,4 m |
| **Yutyrannus** | 🦖 | Carnívoro | Nocaute | ✅ | Tiranossauro com penas; não sente frio no Planalto Vulcânico | 9 m |
| **Microraptor** | 🪽 | Carnívoro | Ovo | — | Planador de quatro asas; derruba o jogador da montaria | 0,8 m |
| **Sinornithosaurus** | 🦖 | Carnívoro | Ovo | — | Pequeno raptor com penas; guarda de base | 1 m |
| **Mei** | 🦖 | Carnívoro | Comida | 🦜 | Troodontídeo minúsculo de ombro; dorme enrolado como pássaro e avisa de predadores | 0,5 m |
| **Sinosauropteryx** | 🦖 | Carnívoro | Comida | 🦜 | Pequeno com penas listradas; acha ovos e lagartos | 1 m |
| **Sarcosuchus** | 🐊 | Carnívoro | Nocaute | ✅ | Crocodilo gigante de rio; emboscada na margem (o chefe "Rei do Rio" é um deles) | 9 m |
| **Bernissartia** | 🐊 | Onívoro | Comida | — | Crocodilo pequeno; quebra conchas e caça lagartos | 0,6 m |
| **Tapejara** | 🪽 | Onívoro | Comida | — | Crista colorida; voa junto com o dono e avisa de predadores (com 3,5 m de envergadura e uns 15 kg, não aguenta uma pessoa) | 3,5 m env. |
| **Hamipterus** | 🪽 | Piscívoro | Comida (peixe) | — | Vive em colônias enormes com ninhos; pesca para o dono (pequeno demais para montar) | 3,5 m env. |
| **Anhanguera** | 🪽 | Piscívoro | Comida (peixe) | ✅ | Pesca em voo rasante | 4,5 m env. |
| **Ornithocheirus** | 🪽 | Piscívoro | Nocaute | ✅ | Planador de longa distância; gasta pouca stamina | 5 m env. |
| **Confuciusornis** | 🪽 | Onívoro | Comida | 🦜 | Ave de ombro; deixa o jogador planar ao cair | 0,7 m env. |
| **Kronosaurus** | 🌊 | Carnívoro | Nocaute | ✅ | Mordida enorme; montaria marinha de combate | 10 m |
| **Leptocleidus** | 🌊 | Piscívoro | Comida | ✅ | Plesiossauro pequeno de lagoa; montaria aquática para iniciantes | 3 m |
| **Repenomamus** | 🐾 | Carnívoro | — | — | Mamífero que caça filhotes de dinossauro; proteja seus ninhos dele | 1 m |

Chefe: **Rei do Rio** (Sarcosuchus da Fenda).

# Capítulo 3: O Reino dos Gigantes (Jurássico) — v3.0

| Espécie | Tipo | Dieta | Domar | Montaria | Utilidade | Tamanho |
|---|---|---|---|---|---|---|
| **Brachiosaurus** (v0.2) | 🦖 | Herbívoro | Comida | 🪑 | Montaria gigante; sela de plataforma | 22 m |
| **Diplodocus** | 🦖 | Herbívoro | Comida | 🪑 | Carrega vários passageiros; ótimo para mudança de base | 25 m |
| **Apatosaurus** | 🦖 | Herbívoro | Comida | 🪑 | Pescoço forte; derruba árvores com o corpo | 21–23 m |
| **Brontosaurus** | 🦖 | Herbívoro | Comida | 🪑 | Plataforma estável; a cauda estala como chicote | 22 m |
| **Camarasaurus** | 🦖 | Herbívoro | Comida | ✅ | Saurópode comum das manadas; carga grande | 15–18 m |
| **Mamenchisaurus** | 🦖 | Herbívoro | Comida | 🪑 | O pescoço mais longo; alcança copas e frutos altos | 26 m |
| **Europasaurus** | 🦖 | Herbívoro | Comida | ✅ | Saurópode anão das ilhas; o primeiro saurópode montável | 6 m |
| **Stegosaurus** (v0.2) | 🦖 | Herbívoro | Comida | ✅ | Montaria; coleta frutas e sementes | 9 m |
| **Kentrosaurus** | 🦖 | Herbívoro | Comida | — | Guarda; espinhos devolvem dano a quem bate nele | 4,5 m |
| **Camptosaurus** | 🦖 | Herbívoro | Comida | ✅ | Montaria simples de carga | 7 m |
| **Dryosaurus** | 🦖 | Herbívoro | Comida | — | Pequeno e rápido; foge e avisa de perigo | 3 m |
| **Gargoyleosaurus** | 🦖 | Herbívoro | Comida | — | Anquilossauro pequeno; quebra pedra devagar | 3–4 m |
| **Scelidosaurus** | 🦖 | Herbívoro | Comida | — | Blindado e resistente; bom para iniciantes | 4 m |
| **Allosaurus** | 🦖 | Carnívoro | Nocaute | ✅ | Caça em grupos de 3; ataque que causa sangramento | 9 m |
| **Megalosaurus** | 🦖 | Carnívoro | Nocaute | ✅ | Dorme de dia, caça à noite | 6–9 m |
| **Torvosaurus** | 🦖 | Carnívoro | Nocaute | ✅ | O maior predador do Jurássico | 10 m |
| **Ceratosaurus** | 🦖 | Carnívoro | Nocaute | ✅ | Chifre no focinho; caça perto da água | 6–7 m |
| **Cryolophosaurus** | 🦖 | Carnívoro | Nocaute | ✅ | Crista em leque; aguenta frio | 6,5 m |
| **Dilophosaurus** (v0.2) | 🦖 | Carnívoro | Ovo | — | Guarda da base | 7 m |
| **Monolophosaurus** | 🦖 | Carnívoro | Ovo | — | Crista única; caçador solitário | 5 m |
| **Guanlong** | 🦖 | Carnívoro | Ovo | — | Tiranossauro primitivo com crista; guarda | 3 m |
| **Compsognathus** (v0.2) | 🦖 | Carnívoro | Comida (peixe) | 🦜 | Mascote de ombro, avisa quando há perigo | 1 m |
| **Archaeopteryx** | 🪽 | Carnívoro | Comida | 🦜 | No ombro, deixa o jogador planar ao cair | 0,5 m |
| **Anchiornis** | 🪽 | Carnívoro | Comida | 🦜 | Penas pretas e vermelhas; enxerga bem no escuro | 0,4 m |
| **Dimorphodon** | 🪽 | Carnívoro | Comida | 🦜 | Ataca quem ataca o dono | 1,5 m env. |
| **Rhamphorhynchus** | 🪽 | Piscívoro | Comida (peixe) | 🦜 | Pesca sozinho e traz peixe para o dono | 1,8 m env. |
| **Pterodactylus** | 🪽 | Carnívoro | Comida | 🦜 | Pequeno e ágil; caça insetos em volta da base | 1 m env. |
| **Liopleurodon** | 🌊 | Carnívoro | Nocaute | ✅ | Muito forte e muito rápido na água (o chefe "Leviatã da Fenda" é um deles) | 6–7 m |
| **Ichthyosaurus** | 🌊 | Piscívoro | Comida (peixe) | ✅ | Montaria aquática rápida e amigável, como um golfinho | 2–3 m |
| **Ophthalmosaurus** | 🌊 | Piscívoro | Comida (peixe) | ✅ | Olhos enormes; enxerga no fundo escuro | 4 m |
| **Plesiosaurus** | 🌊 | Piscívoro | Comida | ✅ | Pescoço longo; boa para explorar | 3,5 m |
| **Cryptoclidus** | 🌊 | Piscívoro | Comida | ✅ | Plesiossauro de praia; montaria aquática para iniciantes | 4 m |
| **Metriorhynchus** | 🌊 | Carnívoro | Ovo | ✅ | Crocodilo marinho; rápido em águas rasas | 3 m |
| **Leedsichthys** | 🌊 | Filtrador | Comida | 🪑 | O maior peixe que já existiu; pacífico, uma ilha que nada | 16 m |

Chefe: **Leviatã da Fenda** (Liopleurodon gigante).

# Capítulo 4: A Origem (Triássico) — v4.0

| Espécie | Tipo | Dieta | Domar | Montaria | Utilidade | Tamanho |
|---|---|---|---|---|---|---|
| **Staurikosaurus** | 🦖 | Carnívoro | Ovo | — | Um dos primeiros dinossauros; caçador rápido | 2 m |
| **Saturnalia** | 🦖 | Onívoro | Comida | — | Pequeno ancestral dos saurópodes; colhe folhas | 1,5 m |
| **Buriolestes** | 🦖 | Carnívoro | Comida | 🦜 | Pequeno de ombro; caça insetos e lagartos | 1,5 m |
| **Liliensternus** | 🦖 | Carnívoro | Ovo | — | O maior predador dinossauro do Triássico Superior; guarda | 5,2 m |
| **Chindesaurus** | 🦖 | Carnívoro | Ovo | — | Pequeno e rápido; foge e avisa de perigo | 2 m |
| **Riojasaurus** | 🦖 | Herbívoro | Comida | ✅ | Um dos primeiros gigantes de pescoço longo; montaria de carga | 10 m |
| **Thecodontosaurus** | 🦖 | Herbívoro | Comida | — | Colhe folhas e frutos baixos | 2,5 m |
| **Herrerasaurus** | 🦖 | Carnívoro | Ovo | ✅ | Montaria de caça; o maior dinossauro carnívoro da era | 6 m |
| **Eoraptor** | 🦖 | Onívoro | Comida | 🦜 | Pequeno de ombro; acha sementes | 1 m |
| **Coelophysis** | 🦖 | Carnívoro | Ovo | — | Caça em bandos grandes | 3 m |
| **Plateosaurus** | 🦖 | Herbívoro | Comida | ✅ | A primeira montaria de carga do Triássico | 8 m |
| **Prestosuchus** | 🦖 | Carnívoro | Nocaute | ✅ | Parente dos crocodilos; predador de topo (o Guardião do Coração da Fenda é um deles) | 7 m |
| **Postosuchus** | 🦖 | Carnívoro | Nocaute | ✅ | Parente dos crocodilos que anda em duas patas | 5 m |
| **Desmatosuchus** | 🦖 | Herbívoro | Comida | ✅ | Blindado com espinhos; montaria tanque | 4,5 m |
| **Effigia** | 🦖 | Onívoro | Comida | ✅ | Parente dos crocodilos que parece um Gallimimus; montaria rápida | 2–3 m |
| **Hyperodapedon** | 🦖 | Herbívoro | Comida | — | Rincossauro; cava raízes. Um dos fósseis mais comuns do Triássico | 1,3 m |
| **Lisowicia** | 🐾 | Herbívoro | Comida | ✅ | Dicinodonte do tamanho de um elefante; carga pesada | 4,5 m |
| **Placerias** | 🐾 | Herbívoro | Comida | ✅ | Dicinodonte com presas; cava água no deserto | 3,5 m |
| **Tanystropheus** | 🐊 | Piscívoro | Comida | — | Pescoço gigante; pesca da margem | 6 m |
| **Eudimorphodon** | 🪽 | Piscívoro | Comida (peixe) | 🦜 | Um dos primeiros pterossauros; pesca para o dono | 1 m env. |
| **Sharovipteryx** | 🪽 | Insetívoro | Comida | 🦜 | Planador; deixa o jogador planar ao cair | 0,3 m |
| **Nothosaurus** | 🌊 | Piscívoro | Comida (peixe) | ✅ | Montaria aquática de rio e costa | 4 m |
| **Shonisaurus** | 🌊 | Piscívoro | Comida | 🪑 | Ictiossauro gigante; plataforma no mar | 15 m |
| **Cymbospondylus** | 🌊 | Carnívoro | Nocaute | ✅ | O primeiro gigante dos mares | 14–17 m |

Chefe: **Coração da Fenda** (com o Guardião, um Prestosuchus da Fenda). A Katarina é a única pessoa do mod, no Último Acampamento.

# Epílogo: O Caminho de Volta (Era do Gelo) — v5.0

| Espécie | Tipo | Dieta | Domar | Montaria | Utilidade | Tamanho |
|---|---|---|---|---|---|---|
| **Mamute-lanoso** | 🐾 | Herbívoro | Comida | ✅ | Derruba árvores e coleta madeira em quantidade | 4 m alt. |
| **Tigre-dentes-de-sabre (Smilodon)** | 🐾 | Carnívoro | Nocaute | ✅ | Montaria ágil que pula alto | 2 m |
| **Lobo-terrível** | 🐾 | Carnívoro | Filhote | ✅ | Caça em matilha, rastreia criaturas | 1,7 m |
| **Rinoceronte-lanoso** | 🐾 | Herbívoro | Comida | ✅ | Investida que derruba inimigos | 4 m |
| **Megatério** | 🐾 | Herbívoro | Comida | ✅ | Preguiça gigante; forte contra insetos e aranhas | 6 m |
| **Megaloceros** | 🐾 | Herbívoro | Comida | ✅ | Montaria muito rápida que pula alto | 2 m alt. |
| **Doedicurus** | 🐾 | Herbívoro | Comida | — | Tatu gigante; coleta pedra rolando como bola | 4 m |
| **Argentavis** | 🪽 | Carnívoro | Nocaute | ✅ | Ave gigante; carrega peso e criaturas médias voando | 6–7 m env. |
| **Urso-das-cavernas** | 🐾 | Onívoro | Nocaute | ✅ | Montaria forte; acha mel e frutas | 3 m |
| **Leão-das-cavernas** | 🐾 | Carnívoro | Nocaute | ✅ | Caçador rápido na neve | 2,1 m |
| **Gliptodonte** | 🐾 | Herbívoro | Comida | — | Tatu gigante blindado; escudo vivo para a base | 3 m |
| **Toxodon** | 🐾 | Herbívoro | Comida | ✅ | Montaria resistente da estepe do sul | 2,7 m |
| **Mastodonte-americano** | 🐾 | Herbívoro | Comida | ✅ | Mastodonte; carga pesada | 3 m alt. |
| **Castor-gigante** | 🐾 | Herbívoro | Comida | — | Derruba árvores e faz represas | 2,2 m |

# Anomalias da Fenda (em qualquer era)

Aparecem perto das Ilhas do Tempo e nas Tempestades da Fenda. Entram junto com a versão da era em que fazem mais sentido.

| Espécie | Tipo | Dieta | Domar | Montaria | Utilidade | Tamanho |
|---|---|---|---|---|---|---|
| **Dunkleosteus** (Devoniano) | 🌊 | Carnívoro | Ovo | ✅ | Peixe blindado; morde e quebra blocos de pedra no fundo do mar | 4–8 m |
| **Megalodon** (Mioceno, opcional) | 🌊 | Carnívoro | Nocaute | ✅ | Tubarão gigante; caça em cardume | 15 m |

Além delas, criaturas de outras eras aparecem como **versões "da Fenda"** (olhos e rachaduras cor de âmbar), mais fortes e com amostras raras.

---

## Sistemas de montaria (estilo ARK)

| Sistema | Versão | O que faz |
|---|---|---|
| Sela de couro | v0.2 ✅ | Sela simples, usada nas montarias terrestres |
| Pulo e tirar a sela | v0.3 | Espaço pula com a montaria; tesoura tira a sela (shift + clique manda sentar) |
| Voo simples | v0.3 | Pteranodon: subir, descer e planar |
| Voo completo e sela por espécie | v0.4 | Stamina voando; cada espécie usa a sua sela, feita com couro, osso e fibra |
| Criaturas de ombro | v0.4 | Criaturas pequenas ficam no ombro e dão um bônus |
| Nado montado | v0.5 | Montarias aquáticas mergulham sem o jogador se afogar |
| Inventário de carga e sela de plataforma | v0.6 | Montarias grandes carregam itens; dá para construir em cima dos gigantes |
| Nocaute | v0.7 | Derrubar criaturas selvagens com armas de narcótico e domesticar enquanto dormem, com animações de nocaute, sono, comer e acordar (ver abaixo) |

## Domesticação: animações e telas (anotado em 24/10/2026)

Pedido do Rodrigo: domar tem que ser visível e gostoso de ver, como no ARK. Todo modelo novo já deve sair com estas
animações, mesmo antes do sistema existir, para não precisar refazer os modelos depois.

| Animação | Quando toca | Detalhe |
|---|---|---|
| `knockout` | O torpor chega no máximo | O bicho cambaleia, cai de lado (ou afunda devagar, nos aquáticos; plana até o chão, nos voadores) |
| `knocked_out` | Enquanto está desmaiado | Deitado, respiração lenta, olho fechado; partículas de "Zzz" |
| `wake` | Acorda sozinho ou foi domado | Levanta sacudindo a cabeça; se não foi domado, sai bravo ou foge |
| `eat` | Recebe comida (na mão ou desmaiado) | Mastiga; partícula do item que comeu |
| `tame` | Domesticação completa | Pulo ou rugido curto de alegria, partículas de coração |
| `beg` | Domado e com fome | Pede comida ao dono (cabeça baixa, som curto) |
| `hatch` | Filhote sai do ovo | O filhote quebra a casca e "marca" o jogador mais próximo |

Telas e efeitos: barra de **torpor** (narcótico) e barra de **domesticação** em cima do bicho desmaiado, com a
**efetividade** caindo se ele levar dano, como no ARK; aviso quando o torpor está acabando; o bicho desmaiado pode ser
atacado por predadores, então é preciso protegê-lo. Os filhotes que nascem vivos (mamíferos e répteis marinhos) usam
uma animação de nascimento no lugar de `hatch`.

## Ordem sugerida dentro de cada versão

Primeiro as criaturas que trazem um sistema novo (Pteranodon para o voo, Elasmosaurus para o nado, Edmontosaurus para a carga e a migração, Therizinosaurus para a coleta), depois as que só reaproveitam o sistema. Assim cada versão traz uma mecânica nova testada por uma espécie antes de ganhar as outras.
