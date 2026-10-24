# Terrassic: roadmap

> Atualizado em 24/10/2026. Junta num lugar só todas as ideias combinadas com o Rodrigo até agora.
> Os detalhes de cada assunto continuam nos documentos próprios (lista no fim). Quando uma fase mudar de estado,
> atualize a linha dela aqui.

**Legenda de estado:** ✅ feito · 🔄 em andamento · ⏭ próxima · ○ planejada · ❓ depende de resposta ou teste do Rodrigo

**Como ler:** o roadmap é organizado **por era**. Tudo o que pertence a uma era (modelos 3D, criaturas, ovos, vozes,
lore, flora, blocos do material da era, biomas, estruturas, eventos, chefe) fica na seção da era, numa fila em ordem.
O que serve a todas as eras (motor do mod, geradores, interface, idiomas, build) fica nas frentes transversais (seção 6).

---

## 1. Visão

O Terrassic é **um mod só, gigante e 100% autoral** de Minecraft 1.20.1 (Fabric + Forge): um mundo pré-histórico no
estilo do **ARK**, com criaturas selvagens perigosas, domesticação, montarias que andam, voam e nadam, criaturas com
utilidade, construção primitiva e uma história para seguir. Não é modpack e não depende de conteúdo de terceiros
(só das bibliotecas GeckoLib e Architectury, embutidas no jar).

O jogador segue a **Dra. Katarina Usha** pelo "Salto": uma máquina do tempo que leva para trás, era por era
(Cretáceo Superior, "Penas e Cinzas", Jurássico, Triássico), com um epílogo na Era do Gelo no caminho de volta.
Cada era é um capítulo jogável do começo ao fim, com 200 a 300 criaturas do mundo todo, e não só dinossauros.

**A v1.0 é o Capítulo 1 completo ("Ecos do Fim", Cretáceo Superior no Overworld).** Depois vem uma versão grande por era.

## 2. Pilares e regras fixas

Valem para todas as frentes. Quem pega uma fase não precisa perguntar de novo.

| # | Regra | Origem |
|---|---|---|
| 1 | **Regra 0, o Minecraft é livre.** Nada move o jogador sozinho; o Altar só acende e ele salta quando quiser. Toda era visitada fica aberta para sempre. A ordem é livre e a história nunca bloqueia o básico. Progresso por jogador. | `HISTORIA.md` §0 |
| 2 | **Conquistas guiam, não prendem.** O único "trava" é o salto para uma era nova no modo Normal, e dá para pular (Salto Instável, modos Rápido/Livre, `/terrassic capitulo`). | `CONQUISTAS.md` |
| 3 | **Global, não brasileiro.** Laboratório internacional, sem país; espécies do mundo todo na proporção dos fósseis. Só piadas internas brasileiras ("Mate", "saudade"). | aprovado 24/10 |
| 4 | **ARK + vida real.** Comportamento por temperamento (Pacífico, Arisco, Defensivo, Territorial, Agressivo); quem paria filhote vivo é domado como filhote; montaria só se aguenta ~300 kg; gigantes de 25 m ou mais só por nocaute. | bestiário |
| 5 | **Tamanho real.** 1 bloco = 1 metro, pelo maior espécime bem documentado, com fonte em `TAMANHOS.md`. | aprovado 24/10 |
| 6 | **Um modelo 3D único e detalhado por espécie.** Arquétipo é só esqueleto de partida, nunca clone. Todo modelo novo sai com o conjunto completo de animações, incluindo as de domesticação. | Rodrigo 24/10 |
| 7 | **Arte harmônica com o Minecraft.** Texturas 16x16, paleta e contraste do vanilla, realista mas cabendo ao lado do vanilla. Nunca duplicar um bloco vanilla. | aprovado 24/10 |
| 8 | **Tudo autoral e gerado por código** em `tools/`. Referência de terceiros só para medidas. Sons só de domínio público ou CC0, com licença anotada. | `ESCOPO.md` |
| 9 | **Três idiomas em tudo:** pt-BR, inglês e espanhol (es_es copiado para as variantes). | aprovado |
| 10 | **Só materiais da época:** madeira, pedra, osso, couro, fibra, sílex, argila, âmbar. Nos blocos de construção, nada de vidro, tijolo cozido ou metal. | `ESCOPO.md` |
| 11 | **Uma era por vez, fechada e jogável**, antes da próxima (seção 4). | `ESCOPO.md`, Rodrigo 24/10 |
| 12 | **Arte nova que troca um asset existente (ovos, capa) passa pelo Rodrigo antes.** O resto segue sem esperar. | Rodrigo 24/10 |

## 3. Como trabalhamos

- **Autonomia (Rodrigo, 24/10/2026):** implementar todas as fases possíveis sem esperar aprovação. Quando o limite de
  uso acabar, esperar voltar e continuar de onde parou, começando pelos **modelos 3D** (a fila da era atual) e depois
  as outras fases desta lista. O que só um humano consegue testar no jogo vai para `docs/TESTES_V03.md` (e listas
  parecidas nas próximas versões) e o trabalho segue.
- **Git com um escritor só.** A nuvem não tem git: cada frente entrega uma lista de arquivos e uma mensagem de commit;
  só a sessão no Mac do Rodrigo faz commit e push em `main`, uma fase por vez, compilando cada commit num clone limpo.
  Pacote e listas em `sync/`; a numeração das fases e `docs/COMMITS_PENDENTES.md` ficam com a frente de sistemas.
- **Arquivos compartilhados.** Quem entregou uma fase congela os arquivos dela até o commit ser confirmado. Os pontos de
  conflito mais comuns são `tools/javagen/gen_species.py`, `tools/javagen/lore.py`, `tools/javagen/gen_resources.py`
  (lang) e `CLAUDE.md`: duas frentes não mexem neles ao mesmo tempo.
- **Uma fase precisa compilar sozinha**, porque cada commit é testado isolado.
- Tudo que precisa de internet aberta (sons, Maven do Fabric/Architectury, compilar, rodar o jogo) roda no Mac.

## 4. Ordem de produção: uma era por vez

1. **Só se produz conteúdo da era atual.** Enquanto o Capítulo 1 não fecha (v1.0), modelos 3D, ovos, vozes, lore,
   flora e estruturas são todos do Cretáceo Superior. Nada de fazer "um pouco de cada era".
2. **Dentro da era, por versão** (v0.4 céus, v0.5 mar, v0.6 planícies, v0.7 predadores), e dentro da versão primeiro
   a espécie que traz um sistema novo (Pteranodon para o voo, Elasmosaurus para o nado, Edmontosaurus para a carga,
   Therizinosaurus para a coleta), depois as que só reaproveitam o sistema.
3. **Arquétipo nasce quando a primeira espécie da fila precisa dele**, nunca antes. Ele é só o esqueleto e as
   animações base; corpo, cabeça, proporções, pele e detalhes são de cada espécie (regra 6).
4. **Cada espécie sai como um pacote completo**, na mesma fase ou em fases seguidas:
   modelo único + todas as animações (`idle walk run sit attack` + as da espécie + `knockout knocked_out wake eat tame beg hatch`),
   texturas de macho e fêmea, ovo no estilo v5 (ou filhote, nos que nascem vivos), tamanho com fonte, linhas em
   `SPECIES`/`SIZES`/`GUIDE`/`WORLD`, texto do Guia nos 3 idiomas, motivo de fóssil, conjunto de voz e spawn.
5. **Exceções permitidas:** consertar ou melhorar algo que já está no jogo (inclusive os 4 jurássicos da v0.2) e as
   frentes transversais, que servem a todas as eras.
6. Depois que o núcleo da era (as espécies do `ROSTER.md`) estiver no jogo, a era é completada com o resto do
   bestiário em levas, ainda na mesma ordem.

---

## 5. As eras

### Era 1 · Capítulo 1 "Ecos do Fim" · Cretáceo Superior (Overworld) · v0.3 a v1.0  ← ERA ATUAL

#### Fila de criaturas e modelos 3D (nesta ordem)

| # | Versão | Criaturas | Esqueleto (arquétipo) | Estado |
|---|---|---|---|---|
| 1 | v0.2 | T. rex, Spinosaurus, Triceratops, Ankylosaurus, Parasaurolophus, Pachycephalosaurus, Gallimimus, Velociraptor + os 4 "vazamentos da Fenda" (Stegosaurus, Brachiosaurus, Dilophosaurus, Compsognathus) | vários | ✅ no jogo |
| 2 | v0.3 | Pteranodon, Mosasaurus, Maiasaura | pterossauro, réptil marinho, hadrossauro | ✅ (`knocked_out` completo desde a fase 40) |
| 3 | revisão | As 12 da v0.2: deixar cada uma única e detalhada, sem clone, com o conjunto completo de animações | terópode grande ✅, hadrossauro ✅ | ⏭ |
| 4 | v0.4 céus | Quetzalcoatlus, Hatzegopteryx (azdarquídeos), Ichthyornis (ave de ombro) | pterossauro ✅, ave ✅ | ✅ modelos, animações, Java e Guia prontos (fases 36 e 39); falta testar no jogo |
| 5 | v0.5 Mar Interior | Mosasaurus montável, Tylosaurus, Elasmosaurus, Xiphactinus, Archelon, Hesperornis, Deinosuchus, Baurusuchus | réptil marinho ✅, plesiossauro ✅, peixe ✅, tartaruga ✅, ave mergulhadora ✅, crocodilo ✅ | ✅ Tylosaurus (41), Elasmosaurus + Mosasaurus montável (42), Xiphactinus (43), Archelon (44), Hesperornis (45), Deinosuchus (46), Baurusuchus (47) |
| 6 | v0.6 planícies e titãs | Edmontosaurus, Corythosaurus, Styracosaurus, Euoplocephalus, Protoceratops, Struthiomimus, Thescelosaurus, Pachyrhinosaurus, Therizinosaurus, Deinocheirus, Alamosaurus, Saltasaurus, Argentinosaurus, Opisthocoelicaudia, Dreadnoughtus | hadrossauro ✅, ceratopsiano ✅, anquilossauro ✅, ornitomimossauro ✅, saurópode (titanossauro) | 🔄 Edmontosaurus (48), Corythosaurus (49), Styracosaurus (50), Euoplocephalus (51), Protoceratops (52), Struthiomimus (53), Thescelosaurus (54), Pachyrhinosaurus (55) |
| 7 | v0.7 predadores ápice | Giganotosaurus, Carcharodontosaurus, Carnotaurus, Tarbosaurus, Daspletosaurus, Albertosaurus, Majungasaurus, Dakotaraptor, Troodon, Oviraptor, Citipati, Mononykus, Didelphodon | terópode grande, abelissaurídeo, terópode pequeno, oviraptorossauro, mamífero pequeno | ○ |
| 8 | depois da v1.0 | O resto das 327 criaturas do Cretáceo Superior no bestiário, em levas | os mesmos | ○ |

#### Sistemas que estreiam nesta era (servem às próximas)
| Versão | Sistemas | Estado |
|---|---|---|
| v0.2 | Sexo, ovos-bloco, domar com comida, sentar/seguir, sela, montaria, lança, clava, machadinha de sílex | ✅ |
| v0.3 | Caderno de Campo (Diário, Guia, Katarina, Relatório), tela de abertura, níveis do Guia, Rocha Fossilífera, pincel e cinzel, Mesa de Pesquisa, Carvão de Esboço, Lente de Âmbar, Frasco de Argila, Âmbar Bruto, Amostra de Sangue, voo simples, pulo na montaria, tesoura tira a sela, configuração de spawn, registros por tabela, Guia com filtros e páginas | ✅ (falta teste no jogo) |
| v0.3 | Árvore de conquistas nova: aba por capítulo + aba Caderno de Campo, trava só o salto (`CONQUISTAS.md`) | 🔄 |
| v0.4 | Voo completo com stamina, sela por espécie (couro, osso, fibra), criaturas de ombro com bônus, temperamentos | ○ |
| v0.5 | Nado montado (mergulhar sem afogar), sela aquática, filhotes de quem nasce vivo | ✅ fase 42: domar/sentar/seguir/montar na água com a sela comum (olhar para baixo mergulha), Respiração Aquática no jogador, 15% dos spawns vivíparos nascem filhotes; sela aquática própria fica para o crafting da v0.8 |
| v0.6 | Cadeia alimentar, carcaças, bandos, fome e sono, ninhos selvagens, migração, procriação de selvagens, inventário de carga, coleta automática, sela de plataforma | ○ |
| v0.7 | Nocaute completo: torpor, barras de torpor e domesticação, eficiência, comer desmaiado, punho, zarabatana e dardo, boleadeira, erva sonífera (`DOMESTICACAO.md`); territórios; ferramentas de osso e sílex completas | ○ |
| v0.8 | Tipo de mundo "Terrassic" + mundo normal, Tempestades da Fenda e criaturas "da Fenda", páginas da Katarina por jogador | ○ |
| v0.9 | Fragmentos de âmbar, Altar do Salto, ritual dos meteoros, Salto Instável, modos Normal/Rápido/Livre, `/terrassic capitulo` | ○ |
| depois | DNA e clonagem a partir das amostras | ○ |

#### Mundo, flora e blocos da era
| Fase | O que entra | Estado |
|---|---|---|
| Blocos base | Lote 1 (palha, esteira, pau a pique, paliçada, cerca de osso, painel de couro) + pedras I e II (calcário, folhelho, giz, sílex, laterita, quartzito, gnaisse, conglomerado, seixos), com veios no mundo | ✅ |
| Madeiras I | Araucária, Ginkgo, Metassequoia com árvores no mundo (153 blocos no total) | ✅ (aguarda commit) |
| Madeiras II e plantas | Taxodium (cipreste do pântano), feto arbóreo, 19 plantas | ⏭ |
| Flora que falta | Magnólia (as primeiras flores), palmeira, sequoia, cicas, samambaias, grama rala | ○ |
| Blocos base restantes | Terra, reboco, pinturas rupestres, palha e trançados (57); couro, osso, troféus e fósseis por espécie (53); utilidades primitivas (33) | ○ |
| Biomas (v0.8) | Planície dos Hadrossauros, Floresta de Magnólias, Pântano de Ciprestes, Floresta de Sequoias, Terras Secas, Delta do Rio, Mar Interior | ○ |
| Estruturas (v0.8) | Cratera de Chegada, Acampamentos da Katarina, Casa do Rio (Refúgio, com o Parasaurolophus "Mate"), Sítio Fossilífero, Colônia de Ninhos de Maiasaura, praia de desova de Archelon, Ilhas do Tempo, Ossuário | ○ |
| Eventos (v0.8) | Migração de hadrossauros, estrelas cadentes cada vez mais frequentes, Tempestades da Fenda | ○ |

#### História, sons e arte da era
| Fase | O que entra | Estado |
|---|---|---|
| História | "O Salto", versão mundial, lore com a Katarina Usha | ✅ (lore aguarda commit) |
| Páginas | ~44 páginas da Katarina por jogador, nos baús das estruturas | ○ (v0.8) |
| Chefe e final | Tirano da Fenda; ritual dos meteoros; salto com o clarão do impacto (o mundo não é destruído) | ○ (v0.9) |
| Vozes | Piloto (T. rex, Parasaurolophus, Pteranodon) com gravações PD/CC0; cisnes e gansos | ✅ (aguarda commit) |
| Vozes | Um conjunto de voz para cada espécie da fila, junto com o modelo dela | ⏭ |
| Ambiente | Sons de fundo e música do Cretáceo; céu, névoa e partículas da era | ○ (v0.8) |
| Ovos | 15 ovos no estilo v5 aprovado | ✅ (aguarda commit) |
| Ovos | Um ovo v5 para cada espécie da fila, com prévia para o Rodrigo | contínuo |
| Galeria | 9 imagens dentro do jogo pelo "modo estúdio" (`CAPA.md`), depois do pacote de texturas, do mundo, das estruturas e de bem mais criaturas | ○ |

---

### Era 2 · Capítulo 2 "Penas e Cinzas" · Cretáceo Inferior · v2.0
Começa só depois da v1.0.
- **Criaturas (29 no plano, 211 no bestiário):** Iguanodon, Ouranosaurus, Psittacosaurus, Sauropelta, Gastonia, Amargasaurus, Nigersaurus, Baryonyx, Suchomimus, Irritator, Acrocanthosaurus, Concavenator, Utahraptor (❓), Deinonychus, Yutyrannus, Microraptor, Sinornithosaurus, Mei, Sinosauropteryx, Sarcosuchus, Bernissartia, Tapejara, Hamipterus, Anhanguera, Ornithocheirus, Confuciusornis, Kronosaurus, Leptocleidus, Repenomamus.
- **Esqueletos novos prováveis:** iguanodonte, espinossaurídeo, dinossauro com penas, pterossauro de crista, pliossauro.
- **Biomas:** Lagoa Salgada, Mangue, Floresta de Coníferas, Planalto Vulcânico, Lajedo Calcário, Rio dos Gigantes.
- **Materiais e blocos:** Calcário Laminado (com os fósseis mais perfeitos), cinza vulcânica (argamassa), penas.
- **Estruturas:** Palafita da Katarina, falésia dos pterossauros, campo de cinza com fósseis.
- **Eventos:** chuva de cinza, seca das lagoas salgadas. **Chefe:** Rei do Rio (Sarcosuchus da Fenda).

### Era 3 · Capítulo 3 "O Reino dos Gigantes" · Jurássico · v3.0
- **Criaturas (34 no plano, 235 no bestiário):** Diplodocus, Apatosaurus, Brontosaurus, Camarasaurus, Mamenchisaurus, Europasaurus, Kentrosaurus, Camptosaurus, Dryosaurus, Gargoyleosaurus, Scelidosaurus, Allosaurus, Megalosaurus, Torvosaurus, Ceratosaurus, Cryolophosaurus, Monolophosaurus, Guanlong, Archaeopteryx, Anchiornis, Dimorphodon, Rhamphorhynchus, Pterodactylus, Liopleurodon, Ichthyosaurus, Ophthalmosaurus, Plesiosaurus, Cryptoclidus, Metriorhynchus, Leedsichthys. Stegosaurus, Brachiosaurus, Dilophosaurus e Compsognathus passam a nascer aqui.
- **Esqueletos novos prováveis:** saurópode de pescoço longo, estegossauro, alossaurídeo, ictiossauro, pterossauro de cauda longa.
- **Biomas:** Floresta de Araucárias, Samambaial, Planície de Coníferas, Arquipélago, Lagoa de Solnhofen, Mar Raso com recifes.
- **Materiais e blocos:** pinhão, madeira de araucária, calcário de Solnhofen, conchas de amonite; cicas e cavalinhas gigantes, sem flores nem grama.
- **Estruturas:** Caverna da Katarina, trilha de pegadas de saurópodes, recifes. **Eventos:** monções, marés. **Chefe:** Leviatã da Fenda (Liopleurodon).

### Era 4 · Capítulo 4 "A Origem" · Triássico · v4.0
- **Criaturas (24 no plano, 223 no bestiário):** Staurikosaurus, Saturnalia, Buriolestes, Liliensternus, Chindesaurus, Riojasaurus, Thecodontosaurus, Herrerasaurus, Eoraptor, Coelophysis, Plateosaurus, Prestosuchus, Postosuchus, Desmatosuchus, Effigia, Hyperodapedon, Lisowicia, Placerias, Tanystropheus, Eudimorphodon, Sharovipteryx, Nothosaurus, Shonisaurus, Cymbospondylus.
- **Esqueletos novos prováveis:** pseudossúquio, rincossauro, dicinodonte, prossaurópode, primeiros dinossauros.
- **Biomas:** Deserto Vermelho, Oásis, Rio de Estação, Floresta de Dicroidium, Floresta de Coníferas, Lago.
- **Materiais e blocos:** arenito vermelho, madeira de conífera antiga, âmbar triássico. **Sistema novo:** calor e água.
- **Estruturas:** Último Acampamento (a Katarina viva), Coração da Fenda, ossuário de Coelophysis.
- **Eventos:** Episódio Pluvial. **Chefe e final:** Coração da Fenda, os três finais e os créditos.

### Epílogo · "O Caminho de Volta" · Era do Gelo · v5.0
- **Criaturas (14 no plano, 205 no bestiário):** mamute-lanoso, tigre-dentes-de-sabre, lobo-terrível, rinoceronte-lanoso, megatério, Megaloceros, Doedicurus, Argentavis (vazamento do Mioceno), urso-das-cavernas, leão-das-cavernas, gliptodonte, Toxodon, mastodonte, castor-gigante.
- **Esqueletos novos prováveis:** proboscídeo, felino, canídeo, urso, cervídeo, preguiça-gigante, gliptodonte.
- **Biomas:** Geleira, Mar Congelado, Tundra, Taiga, Cavernas de Gelo, Estepe do Mamute.
- **Materiais e blocos:** pele grossa, marfim de mamute, gordura, gelo. **Sistema novo:** frio e roupas de pele.
- **Estruturas:** caverna com pinturas rupestres, cemitério de mamutes, toca de urso-das-cavernas, Altar soterrado.
- **Evento final:** a Grande Nevasca.

### Anomalias da Fenda (entram com a era em que fazem sentido)
Dunkleosteus, Megalodon (opcional) e as versões "da Fenda" de criaturas de outras eras (olhos e rachaduras de âmbar).

---

## 6. Frentes transversais (servem a todas as eras)

### T1. Motor do mod (Java em `common/`)
| Fase | O que entra | Estado |
|---|---|---|
| T1.1 | Renomeação PrimalEra → Terrassic | ✅ |
| T1.2 | Subir `mod_version` para 0.3.0 ao fechar a v0.3; tirar o `--mixin.config` duplicado do Forge dev | ⏭ |
| T1.3 | API pública para mods complementares (espaço de roupa nos dinos, registro de cosméticos) | ○ |
| T1.4 | Renascer na era em que morreu (cama da era ou Altar) | ❓ (`HISTORIA.md` §11) |

### T2. Geradores (`tools/`)
| Fase | O que entra | Estado |
|---|---|---|
| T2.1 | `modelgen` em Python puro (`pybench.py`), folhas de contato para revisão, `knocked_out` nos 13 terrestres | ✅ |
| T2.2 | Arquétipos prontos: hadrossauro, terópode grande; pterossauro em andamento. Os outros nascem pela fila da era (seção 4) | 🔄 |
| T2.3 | `spritegen` (ovos v5, armas, ciência, blocos), `soundgen` (conjuntos de voz, gravações PD/CC0), `javagen` (espécies, recursos, ciência, blocos, conquistas), `roster`, `capagen` | ✅ (crescem com cada era) |
| T2.4 | Ficha curta de lore por espécie (modelo de texto) para escalar o Guia | ⏭ |

### T3. Interface: menu do Minecraft, HUD e visual
| Fase | O que entra | Versão | Estado |
|---|---|---|---|
| T3.1 | **Menu principal do Minecraft com a cara do Terrassic** (pedido do Rodrigo): reaproveita a capa em `tools/capagen` para combinar com a página do mod, com o letreiro de pedra TERRASSIC (`logo.py`/`font.py`) e o céu de entardecer com a Fenda (`scene.py`). O panorama sai do `capagen` como as 6 faces do cubo, com a mesma cena e os nossos modelos. Botões e fundo em couro, osso e pedra; dicas de carregamento com curiosidades reais nos 3 idiomas | v0.8 | ○ |
| T3.2 | HUD próprio com retratos dos nossos modelos: montaria (vida, stamina, carga), bando, nova espécie, nome da era, temperatura, alerta da Fenda, objetivos; tudo configurável | v0.8 | ○ |
| T3.3 | Pacote de texturas próprio embutido e opcional (vanilla mais rústico, menus e inventários em couro, osso e pedra, fonte do Caderno) | v0.8 | ○ |
| T3.4 | Motor de céu, névoa, partículas e música por era (o conteúdo de cada era fica na seção da era) | v0.8 | ○ |

### T4. Idiomas
| Fase | O que entra | Estado |
|---|---|---|
| T4.1 | pt_br, en_us, es_es + variantes do espanhol em tudo o que existe | ✅ |
| T4.2 | Conferir no jogo que nenhum texto aparece como chave crua | ❓ (teste humano) |

### T5. Pesquisa
| Fase | O que entra | Estado |
|---|---|---|
| T5.1 | Bestiário mundial: 1.203 criaturas, 200-300+ por era, com não-dinossauros (`docs/bestiario/`) | ✅ |
| T5.2 | Plano por era (`ROSTER.md`), troca das 13 espécies brasileiras | ✅ |
| T5.3 | Tamanhos reais com fontes (`TAMANHOS.md`), uma linha por espécie nova | contínuo |

### T6. Qualidade, build e lançamento
| Fase | O que entra | Estado |
|---|---|---|
| T6.1 | Build e `runClient` no Fabric e no Forge, cada commit compilado num clone limpo | ✅ (contínuo) |
| T6.2 | Testes no mundo da v0.3 (`TESTES_V03.md`) | ❓ (teste humano) |
| T6.3 | Testes dos tamanhos reais: árvores, altura da sela, pés deslizando, filhotes, culling | ❓ (teste humano) |
| T6.4 | Ouvir os sons no jogo | ❓ (teste humano) |
| T6.5 | GeckoLib e Architectury embutidos no jar (jar-in-jar), página no Modrinth e no CurseForge | ○ (v1.0) |
| T6.6 | Limpar arquivos antigos da v0.1 (texturas sem `_male`/`_female`, GIFs) | ○ |

### T7. Colaboração e futuro
| Fase | O que entra | Estado |
|---|---|---|
| T7.1 | Guia `CONTRIBUTING` para a segunda conta do Rodrigo trabalhar pelo GitHub em branches próprias | ❓ (oferecido) |
| T7.2 | Mods complementares do Rodrigo: Guarda-Roupa, Decoração, Desafios (dependem da T1.3) | ○ (depois da v1.0) |
| T7.3 | Porte para 1.21.x | ○ |
| T7.4 | Talvez uma versão Bedrock | ○ (só ideia) |

## 7. O que pode andar em paralelo agora

Cada linha é uma frente que uma sessão pode tocar sem esbarrar nas outras (cuidado só com os arquivos da seção 3).
Todas trabalham na mesma fila, a da Era 1:

| Frente | Próxima fase | Arquivos principais |
|---|---|---|
| Modelos 3D da Era 1 | ✅ `knocked_out` nas 18 espécies, revisão das 12 da v0.2, azdarquídeos e Ichthyornis (v0.4); a seguir os arquétipos do Mar Interior (v0.5) | `tools/modelgen/` |
| Sistemas da v0.4 | Voo completo, stamina, sela por espécie, ombro, temperamentos | `common/` (entidades) |
| Blocos e flora da Era 1 | Taxodium, feto arbóreo, plantas; depois magnólia, palmeira, sequoia, cicas | `tools/spritegen/blocks.py`, `tools/javagen/gen_blocks.py` |
| Conquistas | Terminar a árvore nova | `tools/javagen/conquistas.py`, `docs/CONQUISTAS.md` |
| Vozes da Era 1 | Conjuntos de voz na ordem da fila | `tools/soundgen/` |
| Ovos da Era 1 | Ovo v5 de cada espécie da fila | `tools/spritegen/egg_designs.py` |
| Lore | Ficha curta por espécie, na ordem da fila | `tools/javagen/lore.py` |

**Dependências que seguram a ordem:** espécie nova no código só depois do modelo, do ovo, do tamanho e do texto;
nado montado antes do mar (v0.5); carga e plataforma antes dos titãs (v0.6); nocaute precisa das animações de
domesticação e das armas antes dos predadores ápice (v0.7); estruturas usam os blocos restantes; o HUD e o menu usam
retratos dos modelos; o Altar e o chefe (v0.9) fecham o capítulo e dependem de quase tudo.

## 8. Versões

| Versão | Tema | Estado |
|---|---|---|
| v0.1 | Primeiro protótipo | ✅ |
| v0.2 | Primeiros dinossauros (12) | ✅ |
| **v0.3** | Fundação da história e do cientista, Pteranodon, Mosasaurus, Maiasaura, sons piloto, es_es, blocos base, ovos v5, tamanhos reais | 🔄 (falta: conquistas, testes no jogo, `mod_version` 0.3.0) |
| v0.4 | Os céus | ○ |
| v0.5 | O Mar Interior | ○ |
| v0.6 | Planícies, manadas e titãs | ○ |
| v0.7 | Predadores ápice e nocaute | ○ |
| v0.8 | Mundo Terrassic: biomas, estruturas, menu do Minecraft, HUD, ambientação, pacote de texturas | ○ |
| v0.9 | O Fim: Altar do Salto e chefe | ○ |
| **v1.0** | **Capítulo 1 "Ecos do Fim" completo**, testado no Fabric e no Forge, 3 idiomas, lançamento | ○ |
| v2.0 | Penas e Cinzas | ○ |
| v3.0 | O Reino dos Gigantes | ○ |
| v4.0 | A Origem e os finais | ○ |
| v5.0 | O Caminho de Volta | ○ |
| depois | Encher cada era até o bestiário, mods complementares, 1.21.x, talvez Bedrock | ○ |

## 9. Perguntas abertas para o Rodrigo

1. **Sobrenome da Katarina:** "Usha" (o que está no mod hoje) ou "Ushakova"?
2. **Utahraptor:** entra (5,5-7 m, o raptor maior que uma pessoa)? Ele é do Cretáceo Inferior, então iria para a Era 2; o Velociraptor continua com 2 m.
3. **Testes no jogo** (só um humano faz): `docs/TESTES_V03.md`, tamanhos reais, ouvir os sons, conferir os 3 idiomas.
4. **Guia CONTRIBUTING** para a segunda conta: escrevo?
5. **Renascer na era** em que o jogador morreu (cama da era ou Altar), em vez de voltar ao mundo normal?

## 10. Documentos de cada assunto

| Assunto | Documento |
|---|---|
| História, eras, mundo, finais | `docs/HISTORIA.md` |
| Escopo do produto, HUD, ambientação, complementares | `docs/ESCOPO.md` |
| Plano de criaturas por versão | `docs/ROSTER.md` |
| Todas as criaturas possíveis | `docs/bestiario/` |
| Tamanhos e fontes | `docs/TAMANHOS.md` |
| Domesticação por nocaute | `docs/DOMESTICACAO.md` |
| Conquistas | `docs/CONQUISTAS.md` |
| Sons | `docs/SONS.md`, `docs/SONS_DOWNLOAD.md`, `docs/LICENSES-SOUNDS.md` |
| Capa e imagens | `docs/CAPA.md`, `docs/RESUMO.md` |
| Testes da v0.3 | `docs/TESTES_V03.md` |
| Modelos | `tools/modelgen/README.md` |
