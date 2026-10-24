# Testes da v0.8 no Mac

A frente paralela da v0.8 foi compilada na nuvem contra stubs gerados do código real do Minecraft 1.20.1, do
Architectury e do GeckoLib (0 erros), mas não rodou o jogo: a nuvem não alcança o Maven. Esta é a lista do que testar
no Mac, na ordem. Se algo der errado, cole o log (ou o crash report) numa sessão do Claude.

## 0. Compilar
- [ ] `./gradlew build` na raiz.
- [ ] Pontos com mais risco:
  - `mixin/NoiseGeneratorSettingsMixin`: injeta em `surfaceRule()`, o acessor de um record. No Forge confira se o refmap
    pegou (log com `terrassic.mixins.json` e nenhum "could not find target method").
  - `world/CretaceousBiomes`: usa `EntityEvent.LIVING_CHECK_SPAWN` do Architectury.
- [ ] Depois `./gradlew :fabric:runClient` e `./gradlew :forge:runClient`.

## 1. Mundo Terrassic (M1)
- [ ] Criar Mundo → Mais opções → Tipo de mundo: aparecem **Terrassic**, **Terrassic: Ilha Pequena** e **Terrassic: Continente Grande** (nome traduzido nos 3 idiomas).
- [ ] O mundo cria sem erro. Se aparecer "Feature order cycle found", mande o log.
- [ ] `F3` mostra os biomas `terrassic:...`. Com `/locate biome terrassic:dry_lands` (e os outros 10), todos são encontrados.
- [ ] Superfícies: areia nas praias e no Mar Interior, laterita e solo laterítico vermelho nas Terras Secas, serrapilheira nas florestas,
      turfa, lama e poças no Pântano, pedra nas encostas das Serras.
- [ ] Árvores: magnólias na Floresta de Magnólias, metassequoias e araucárias na Floresta de Sequoias, ciprestes na água do Pântano,
      palmeiras e fetos no Delta.
- [ ] Nenhuma vila, posto de saqueadores, portal em ruínas ou naufrágio. Masmorras e geodos continuam.
- [ ] Nenhum animal vanilla: nem vaca, porco, ovelha, cavalo, golfinho, morcego, nem peixe, lula, tartaruga ou sapo (§7).
- [ ] Dinossauros nascem nos biomas certos (raptores e Giganotosaurus nas Terras Secas, hadrossauros na Planície, Spinosaurus e
      Deinosuchus no Delta, mosassauros no Mar Interior Profundo).
- [ ] À noite, na superfície: nada de zumbis e esqueletos (aranhas e creepers podem aparecer). Numa caverna, zumbis e esqueletos aparecem.
- [ ] Um mundo **normal** criado depois continua igual ao de antes (mesmos biomas vanilla, dinossauros nos biomas vanilla).
- [ ] Desempenho: andar rápido (elytra ou modo espectador) não trava mais que num mundo normal.

## 2. Tela de título e carregamento (M2)
- [ ] A tela de título mostra o panorama do Cretáceo girando devagar (Fenda, lago, dinossauros, árvores de blocos), sem costuras visíveis entre as faces.
- [ ] O logo de pedra TERRASSIC aparece no lugar do logo do Minecraft, com "Capítulo 1 · Ecos do Fim" embaixo (traduzido).
- [ ] A frase amarela é do Terrassic e muda a cada vez que a tela abre.
- [ ] Criando ou carregando um mundo: aparece "Você sabia?" e uma dica embaixo do mapa de chunks, sem passar da tela.
- [ ] Entrando num servidor ou trocando de dimensão ("Carregando terreno"): também aparece uma dica.
- [ ] Com `"title_screen": false` em `config/terrassic-client.json`, volta a tela vanilla. Com `"loading_tips": false`, somem as dicas.
- [ ] No Forge: a tela de título abre normalmente (botão "Mods" do Forge continua lá). Se algo do Terrassic não aparecer, o log diz qual injeção não achou o alvo.

## 3. Estruturas (M3a)
- [ ] Mundo novo (Terrassic ou normal): a 18-26 blocos do spawn existe a **Cratera de Chegada** (bacia de cinza e lama rachada, âmbar no centro, cesto na borda com âmbar bruto e uma página). Só uma por mundo.
- [ ] `/locate structure terrassic:katarina_camp_reed` (e `_fern`, `_hide`), `terrassic:fossil_site` e `terrassic:bone_bed` acham as estruturas.
- [ ] O acampamento fica no chão (nem enterrado, nem flutuando), a barraca tem a cumeeira certa, a cama e o cesto funcionam.
- [ ] O cesto do acampamento traz uma Página Solta; ao pegar, ela vira uma página nova da Katarina no Caderno.
- [ ] Sítio Fossilífero: a parede mostra Rocha Fossilífera e crânios fósseis; o pincel tira fósseis dela.
- [ ] Ossuário: esqueleto de titanossauro, ossos espalhados e três Compsognathus.
- [ ] Nenhuma estrutura nasce dentro d'água.

## 4. Refúgio e ninhos (M3b)
- [ ] `/locate structure terrassic:river_house` acha **uma** Casa do Rio, perto de um rio, a umas 220-420 quadras da origem.
- [ ] A casa fica de pé sobre as palafitas (na água ou na margem), telhado inteiro, porta funcionando, cestos com páginas.
- [ ] **Mate** está sentado no deque, com o nome "Mate". Clique de mão vazia: aparece a mensagem e ele passa a ser seu (senta/segue como os outros domados).
- [ ] Agachado, usar a Lente de Âmbar mostra a distância e a direção do Refúgio; perto dele, "Você está no Refúgio da Katarina".
- [ ] Sem agachar, a Lente continua funcionando como luneta.
- [ ] `/locate structure terrassic:nest_colony`: montes com ninhos e ovos de Maiasaura e quatro adultas por perto.

## 5. Tempestades da Fenda (M4)
- [ ] `/terrassic tempestade iniciar`: aparece a mensagem; em uns 5 s o céu, as nuvens e a névoa ficam âmbar e surgem partículas de âmbar.
- [ ] Sons distorcidos de vez em quando.
- [ ] A cada ~10 s surge perto de você (20-34 blocos) um Stegosaurus, Brachiosaurus, Dilophosaurus ou Compsognathus, com clarão âmbar e brilho; no máximo 3 por jogador.
- [ ] Matar uma delas solta âmbar bruto.
- [ ] `/terrassic tempestade parar` (ou esperar 3-5 min): mensagem de fim, o céu volta ao normal e as criaturas somem num clarão, menos as domadas.
- [ ] Quem ficou no Overworld a tempestade toda completa "Sobreviver a uma Tempestade da Fenda" no Diário (e ganha a conquista).
- [ ] Sem comando: com `storm_chance` 1.0 e `storm_min_days` 0 no `config/terrassic-world.json`, a tempestade começa no entardecer.
- [ ] No Nether e no End não há efeito nenhum.

## 6. HUD (M5)
- [ ] Montado num dinossauro: painel no canto superior esquerdo com o modelo dele (inteiro no quadro), nome, vida e fome certas; ícone de cesto se tiver baú.
- [ ] Com dinossauros domados por perto: cartões com retrato, vida e o estado certo (seguindo / sentado / lutando / dormindo).
- [ ] Avistar uma espécie nova: aparece a notificação "Nova espécie avistada" com o modelo. Estudar e domar também avisam.
- [ ] Ao entrar no mundo: título "Cretáceo Superior" e subtítulo do capítulo.
- [ ] Durante uma tempestade: fragmento de âmbar pulsando no topo.
- [ ] F1 esconde tudo; cada opção `hud_*` em `config/terrassic-client.json` desliga a sua parte.
- [ ] Desempenho: com 6 dinossauros no bando, o FPS não cai visivelmente.

## 7. Continente (MUNDO.md §10)
Compilação: atenção a `mixin/ChunkMapMixin` (`@ModifyArg` em `RandomState.create` dentro do construtor de `ChunkMap`) e
`mixin/client/WorldCreationUiStateMixin` (`@Inject` no fim do construtor). No log, procure
"Terrassic continent of radius 1200 blocks (N reads of the continentalness replaced)": N tem que ser maior que 0.
"no vanilla continentalness found" quer dizer que o mundo saiu vanilla: mande o log.
- [ ] **Criar novo mundo** já abre com o tipo **Terrassic** escolhido (Fabric e Forge). Trocar para "Padrão" funciona.
- [ ] Mundo novo Terrassic: nasce em terra, perto do centro. Mapa (ou voar alto) mostra **um continente** cercado de mar,
      com um golfo grande (o Mar Interior) entrando por um lado e ilhotas em volta. Compare com
      `mundo/previas/continente_formato.png`.
- [ ] `/worldborder get` dá **4800**; andando ~2400 blocos do centro em linha reta, você chega à borda no meio do mar.
- [ ] Os biomas seguem o continente: Mar Interior e Mar Interior Profundo no mar, praias na costa, serras e florestas no meio.
- [ ] **Terrassic: Ilha Pequena** (borda 3200) e **Terrassic: Continente Grande** (borda 8000, biomas grandes) criam sem erro.
- [ ] Sair e entrar de novo no mundo: o continente continua igual (mesma costa) e a borda também.
- [ ] Dois mundos com sementes diferentes têm continentes diferentes (o golfo aponta para outro lado).
- [ ] Mundo **Padrão** (vanilla) continua igual ao Minecraft, sem borda nova.
- [ ] Nenhum animal vanilla nos biomas do Cretáceo depois de 10 min andando (nem peixes, lulas ou lulas-brilhantes nas
      cavernas). Ovo de spawn de vaca ainda funciona.
- [ ] Servidor dedicado com `level-type=terrassic\:terrassic` cria o continente.
- [ ] Desempenho: gerar chunks novos não fica visivelmente mais lento que no mundo Terrassic da v0.8.
