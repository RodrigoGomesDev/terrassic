# PrimalEra — v0.1.0

Mod de dinossauros para **Minecraft 1.20.1**, **Fabric + Forge** (multi-loader com Architectury), com modelos 3D animados no estilo do Cobblemon (cubos low-poly, animações GeckoLib) feitos a partir de reconstruções científicas reais.

![Elenco v0](art/preview_sheet.png)

## O que tem na v0

| Dinossauro | Real | No jogo | Comportamento | Onde nasce | Comida (procriar/atrair) |
|---|---|---|---|---|---|
| **Tyrannosaurus** | 12,3 m, 3,8 m de quadril, ~8 t | ~6,6 blocos de comprimento, escala 0,55 | Predador hostil, caça jogadores e animais grandes, **ruge** ao escolher um alvo | Savana, selva (raro, sozinho) | Carne crua de vaca, porco e ovelha |
| **Triceratops** | 8–9 m, ~3 m, 6–10 t | ~5,5 blocos, escala 0,6 | Neutro, em manada; revida com chifrada e muito knockback. Pasta | Savana, planície (2–4) | Trigo, samambaia |
| **Stegosaurus** | 6,5–9 m, ~3,5 t | ~4,5 blocos, escala 0,6 | Neutro; revida com golpe de cauda (thagomizer). Pasta | Floresta, planície (1–3) | Samambaia, melancia, trigo |
| **Velociraptor** | 1,5–2 m, 0,5 m de quadril, 15–20 kg, com penas | ~2 blocos, tamanho real | Caçador em bando: quando um escolhe um alvo, o bando todo ataca. Salta no alvo. Foge do T. rex | Savana, badlands, deserto (2–4) | Carnes cruas |
| **Compsognathus** | 0,7–1,4 m, 0,3–3,5 kg | ~1,2 blocos | Arisco, foge de jogadores, mas o grupo inteiro ataca quem machuca um deles | Floresta, selva (3–6) | Frango, bacalhau, salmão |

Para todos:
- Modelos e texturas próprios, com as animações `idle`, `walk`, `run` e `attack`, mais `roar` (T. rex) e `graze` (herbívoros). A cabeça acompanha o olhar.
- Procriação com filhotes, que aparecem menores e crescem com o tempo.
- Ovos geradores na aba criativa **PrimalEra**.
- Spawn natural por bioma e loot (carne, couro, ossos ou penas).
- No modo Pacífico os predadores não atacam o jogador.

Os sons são placeholders do vanilla (ravager, raposa, papagaio e vaca, com pitch alterado).

## Como compilar e testar

Pré-requisitos: **JDK 21** para rodar o Gradle. O mod é compilado para Java 17, que é o que o Minecraft 1.20.1 usa.

```bash
# macOS (Homebrew)
brew install --cask temurin@21

cd ~/projects/PrimalEra
./gradlew build                 # gera os jars (a 1ª vez baixa Minecraft/Forge/Fabric, demora)

./gradlew :fabric:runClient     # abre o jogo com o mod (Fabric)
./gradlew :forge:runClient      # idem (Forge)
```

Os jars ficam em `fabric/build/libs/primalera-fabric-0.1.0.jar` e `forge/build/libs/primalera-forge-0.1.0.jar`.

Dependências para jogar (coloque na pasta `mods` junto com o jar):

| | Fabric | Forge |
|---|---|---|
| Loader | Fabric Loader ≥ 0.15 + **Fabric API** | Forge 47.x |
| **Architectury API** | 9.2.x (Fabric) | 9.2.x (Forge) |
| **GeckoLib** | 4.x para 1.20.1 (Fabric) | 4.x para 1.20.1 (Forge) |

Para testar rápido no jogo, use os ovos da aba criativa ou `/summon primalera:tyrannosaurus`.

> ⚠️ Não foi possível compilar no ambiente onde este projeto foi gerado, porque não havia acesso aos repositórios Maven do Minecraft. O código passou por revisão estática e foi compilado com stubs das APIs. Os modelos e animações foram validados no Blockbench de verdade. Se o primeiro `./gradlew build` reclamar de alguma versão, veja "Problemas comuns" abaixo.

### Problemas comuns
- **Versão não encontrada.** Ajuste o `gradle.properties`. As versões usadas são `architectury_api_version=9.2.14`, `geckolib_version=4.8.4`, `forge_version=1.20.1-47.4.8` e `fabric_api_version=0.92.6+1.20.1`. Qualquer 9.2.x / 4.x para 1.20.1 funciona.
- **`NoClassDefFoundError com/eliotlash/mclib` no `:forge:runClient`.** A linha `forgeRuntimeLibrary` no `forge/build.gradle` já trata disso. Se ainda acontecer, confira se o repositório do GeckoLib (cloudsmith) está acessível.
- **"Unsupported class file major version".** O Gradle está rodando com um JDK antigo. Use o JDK 21 (`java -version`).

## Estrutura

```
PrimalEra/
├── common/                 código compartilhado (99% do mod)
│   └── src/main/java/com/primalera/
│       ├── PrimalEra.java          ponto de entrada comum
│       ├── entity/                 DinosaurEntity (base GeckoLib), HerbivoreDinosaur, 5 espécies
│       ├── registry/               entidades, itens (ovos), aba criativa
│       ├── world/ModSpawns.java    spawn por bioma + regras de spawn
│       └── client/                 DinosaurRenderer (um renderer para todos) + registro
│   └── src/main/resources/assets/primalera/
│       ├── geo/entity/*.geo.json            modelos (GeckoLib / Bedrock)
│       ├── animations/entity/*.animation.json
│       └── textures/entity/*.png
├── fabric/   forge/         só o ponto de entrada de cada loader + metadados
├── art/<especie>/           ★ arquivos .bbmodel para editar no Blockbench + previews
└── tools/modelgen/          gerador procedural dos modelos (Python + Blockbench headless)
```

## Editando os modelos no Blockbench

1. Abra `art/<especie>/<especie>.bbmodel` no Blockbench. O formato é *Bedrock Entity* e não precisa de plugin.
2. Edite os cubos, a textura (aba Paint) ou as animações (aba Animate).
3. Exporte por cima dos arquivos do mod:
   - **File › Export › Export Bedrock Geometry** → `common/src/main/resources/assets/primalera/geo/entity/<especie>.geo.json`
   - **Animation › Export Animations** → `.../animations/entity/<especie>.animation.json`
   - Textura: clique com o direito na textura › **Save As** → `.../textures/entity/<especie>.png`
4. Salve o `.bbmodel` também.

Regras que precisam ser mantidas:
- O osso **`head`** é girado pelo jogo (olhar). Não anime esse osso. Anime `skull`, `neck1` e `jaw` no lugar dele.
- Os nomes das animações seguem `animation.<especie>.<nome>`. O código procura `idle`, `walk`, `run` e `attack`, além de `roar` e `graze`.
- Raptor e compy foram modelados maiores e são reduzidos no código (escala 0,5 e 0,3), para a textura ter mais detalhe.

Se você preferir **regenerar tudo por código** (proporções, cores, padrões e animações são parâmetros em Python), veja `tools/modelgen/README.md`.

## Próximos passos (roadmap)

- **v0.2**: domesticar o raptor (filhote criado por você vira companheiro), montar no triceratops, ovos de dinossauro que chocam, sons próprios.
- **v0.3**: Fósseis no mundo, mesa de extração de DNA e mais espécies (Brachiosaurus, Parasaurolophus, Ankylosaurus, Pteranodon e Spinosaurus), reaproveitando os esqueletos-base bípede e quadrúpede do gerador.
- **v0.4**: Ciclo de sono, fome e territórios, variantes de cor (macho/fêmea) e config de spawn.
- **Portes**: com o Architectury a lógica fica em `common/`. Para 1.21.x as mudanças principais são a versão do GeckoLib (a API muda um pouco entre versões) e os componentes de item/registro do vanilla.

## Créditos das referências

Medidas e anatomia: Wikipedia (artigos *Tyrannosaurus*, *Triceratops*, *Stegosaurus*, *Velociraptor* e *Compsognathus*) e a literatura citada neles. Os modelos e texturas são originais. Nenhuma arte de paleoartista foi copiada; as imagens serviram só como referência de proporção.
