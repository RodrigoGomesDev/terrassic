# PrimalEra — contexto para continuar em qualquer sessão do Claude

Leia este arquivo e o README.md antes de começar. Responda em português.
Autor do projeto: Rodrigo Gomes (Grupo Permaneo). Faça os commits no nome dele.

## O que é
Mod de dinossauros para Minecraft 1.20.1, Fabric + Forge (Architectury), modelos GeckoLib no estilo Cobblemon.
Versão atual: **v0.2.0** (tags git v0.1.0 e v0.2.0). A v0.1 compilou e rodou no Mac do Rodrigo (Fabric runClient).
A v0.2 ainda não foi testada no jogo.

## Stack
- Gradle 9.5.1, Architectury Loom 1.17-SNAPSHOT, plugin 3.5-SNAPSHOT, mapeamentos Mojang, Java 17 (rodar com JDK 21).
- Architectury API 9.2.14, GeckoLib 4.8.4, Forge 1.20.1-47.4.8, Fabric Loader 0.17.2, Fabric API 0.92.6+1.20.1.
- Testar: `./gradlew :fabric:runClient` ou `:forge:runClient`. Build: `./gradlew build`.
- NÃO use javax.annotation / org.jetbrains.annotations no common (não estão no classpath).

## Código (common/src/main/java/com/primalera)
- `entity/DinosaurEntity` (extends TamableAnimal): sexo sincronizado (textura por sexo), domesticação,
  sentar/seguir, sela + montaria, procriação só macho+fêmea, procriação põe ovo-bloco, controllers GeckoLib
  ("movement": idle/walk/run/sit; "action": attack + extras via triggerAnim).
- `HerbivoreDinosaur` (lutador ou fugitivo, pasta) e `PredatorDinosaur` (caça, domesticável só filhote).
- 12 espécies GERADAS por `tools/javagen/gen_species.py` (edite a tabela lá e rode o script, não edite os .java).
- `block/DinoEggBlock` (choca em 3 estágios, filhote "marca" o jogador mais próximo).
- `item/` armas: SpearItem + `entity/ThrownSpear` (arremessável), ClubItem, FlintHatchetItem, ModTiers.
- `registry/` ModEntities, ModBlocks, ModItems, ModTabs. Ordem em PrimalEra.init: tabs, entities, blocks, items.
- `client/` DinoGeoModel (textura _male/_female, esconde ossos male_display/female_display/saddle), renderers.
- `world/ModSpawns` spawn por bioma.

## Assets e ferramentas
- Modelos: `tools/modelgen` (Python + Blockbench headless via Playwright; ver tools/modelgen/README.md).
  Exporta art/<especie>/<especie>.bbmodel, geo/animations/texturas para common/src/main/resources/assets/primalera.
  Convenções: 16px = 1 bloco, animal olha para -Z, osso `head` = olhar (não animar; use `skull`),
  animações `animation.<especie>.<idle|walk|run|sit|attack|roar|graze|call|display>`.
- Sprites 16x16: `tools/spritegen/sprites.py` (ovos geradores únicos, armas, ovos-bloco).
- JSON (lang pt_br/en_us, receitas, loot, modelos, blockstates): `tools/javagen/gen_resources.py`.
- Tudo é autoral e gerado por código; referências só de medidas (Wikipedia). Não copiar arte de terceiros.

## Espécies (12)
Predadores: Tyrannosaurus, Spinosaurus, Dilophosaurus, Velociraptor, Compsognathus.
Herbívoros: Triceratops, Stegosaurus, Ankylosaurus, Brachiosaurus, Parasaurolophus, Pachycephalosaurus, Gallimimus.
Montáveis: T. rex, Triceratops, Brachiosaurus, Parasaurolophus, Gallimimus.

## Pendências conhecidas
- Testar v0.2 no jogo (Fabric e Forge) e corrigir o que aparecer.
- Sons ainda são vanilla (placeholders).
- Montaria não pula; sela não pode ser removida.
- Herbívoros selvagens só procriam depois de domesticados.
- Na pasta podem sobrar arquivos antigos da v0.1 (texturas <especie>.png sem _male/_female, GIFs): podem ser apagados.

## Roadmap
- v0.3: fósseis + mesa de DNA, Pteranodon (voador), Mosasaurus (aquático), sons próprios, pulo na montaria,
  tirar sela, config de spawn.
- v0.4: fome/sono, territórios, variantes de cor por bioma, ninhos.
- Portes para 1.21.x.

## Como registrar o progresso
Ao terminar uma etapa: atualize este arquivo (versão, pendências) e faça commit no nome do Rodrigo.
