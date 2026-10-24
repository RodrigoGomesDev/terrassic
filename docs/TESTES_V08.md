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
- [ ] Criar Mundo → Mais opções → Tipo de mundo: aparecem **Terrassic** e **Terrassic: Biomas Grandes** (nome traduzido nos 3 idiomas).
- [ ] O mundo cria sem erro. Se aparecer "Feature order cycle found", mande o log.
- [ ] `F3` mostra os biomas `terrassic:...`. Com `/locate biome terrassic:dry_lands` (e os outros 10), todos são encontrados.
- [ ] Superfícies: areia nas praias e no Mar Interior, laterita e solo laterítico vermelho nas Terras Secas, serrapilheira nas florestas,
      turfa, lama e poças no Pântano, pedra nas encostas das Serras.
- [ ] Árvores: magnólias na Floresta de Magnólias, metassequoias e araucárias na Floresta de Sequoias, ciprestes na água do Pântano,
      palmeiras e fetos no Delta.
- [ ] Nenhuma vila, posto de saqueadores, portal em ruínas ou naufrágio. Masmorras e geodos continuam.
- [ ] Nenhuma vaca, porco, ovelha, cavalo, golfinho ou morcego. Peixes, lulas, tartarugas nas praias e sapos no Pântano, sim.
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
