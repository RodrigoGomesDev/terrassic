# Terrassic — coordenação entre frentes

Atualizado em 25/10/2026. Titular: **Rodrigo Gomes**, pessoa física, sem vínculo empresarial.

Foco atual pedido pelo Rodrigo: Codex assume os fundos do menu/interface; Claude não mexe nessa frente por
enquanto. Após comparar as propostas, Rodrigo selecionou explicitamente a imagem cinematográfica de confronto
T. rex × Triceratops como referência: reduzir a poluição visual, usar sol quadrado Minecraft e criar ambientes
semelhantes para apresentação. Essa seleção orienta `art/menu_ia/v2/`; não aprova automaticamente toda a v1 nem
substitui os fundos ativos. Os renders de modelos originais em `art/menu_vanilla/v1/` continuam disponíveis.

## Links oficiais — informados pelo Rodrigo em 25/10

Entrega Codex — revisão geométrica dos fundos (25/10): `art/menu_ia/v3/` e documentação das propostas.
Rodrigo aprovou a direção visual da v2, mas apontou erros nos blocos. Revisar terreno da floresta,
margens do rio e falésias, preservando cenas e iluminação. A conferência estética anterior não validou
a geometria voxel. Três edições inspecionadas, PNGs conferidos e originais preservados; detalhes e limites
em `art/menu_ia/v3/README.md`. Fundos ativos permanecem inalterados. Geometria exata e modelos originais
não certificados por geração raster; aprovação final pendente. Entrega no commit desta atualização.

- Modrinth: https://modrinth.com/mod/terrassic
- CurseForge: https://www.curseforge.com/minecraft/mc-mods/terrassic
- Wiki: https://github.com/RodrigoGomesDev/terrassic/wiki

## Integração da identidade — 25/10

Entrega `8ee3b7e3` (`sync/identidade`) conciliada com a main, incluindo os quatro commits de licença/titular,
tipografia, kit de marca e textos de loja/Discord. A ficha do Guia continua à direita, os dioramas foram mantidos,
assim como o painel de basalto das dicas; fontes e botões próprios foram combinados com esse layout.
Os documentos de licença entregues são empacotados nos dois JARs finais, com os mesmos bytes dos arquivos fonte.
Os links oficiais acima também estão no README; não houve publicação de páginas ou mensagens externas.

Evidências: build Fabric/Forge com regressões passou em 2 min 2 s; integridade de 59 espécies/4.322 JSONs/1.827
chaves passou; 18 testes Python e 10.000 cenários de orçamento passaram. Comparação antes da atualização de
documentação confirmou 95 arquivos locais intactos, 50 arquivos exclusivos da identidade iguais à entrega e
439 arquivos exclusivos da main preservados. Seis atlas bitmap têm referências e grades válidas; os nove recursos
de fonte e os três documentos de licença foram conferidos por conteúdo dentro dos JARs.

Backup recuperável dos dois históricos e dos arquivos locais em
`build/integration-backups/identity-merge-kq8zkgdi/` (`source.bundle`, `manifest.json`, `local-files/`).
O ícone e o letreiro ativos foram preservados; propostas continuam em `art/identidade/marca/`.
Fontes e telas ainda precisam de revisão visual no jogo; build e conferência de arquivos não substituem isso.

Atualização recebida durante os testes de dardos: `890fef2d`/`d064276d` (fase 167, letreiro Degraus nas capas,
banner e kit de marca) incorporada por fast-forward. Não houve regeneração de arte nem alteração nos arquivos
locais de marca; a implementação da zarabatana não se sobrepõe a essa entrega.
A entrega seguinte, `cdbb23bd` (tela de título em Degraus), também foi incorporada por fast-forward. As duas
entregas passaram na CI de origem; o novo letreiro ativo passa a ser o entregue pela própria frente de identidade.

## Conferência Terrassic e Terrassic Sync — 25/10

- `~/projects/terrassic` é o checkout de desenvolvimento, na main. Incorporados por fast-forward 52 commits
  recebidos após `96004f7b`, até `98a5a1f0`: nocaute, Guia, telas e remasterizações. Integridade passou com
  59 espécies, 4.319 JSONs e 1.827 chaves por idioma; build Fabric/Forge com regressões passou em 37 s.
- `~/projects/terrassic-sync` é uma pasta de transporte, sem `.git`: bundles, LEIA-ME e prévias.
  Os bundles antigos de base, main, v0.8 e v0.9 pertencem ao histórico anterior e não devem ser mesclados novamente.
- `paralelo-identidade.bundle` foi verificado e lido como `sync/identidade`, sem trocar a main. Contém **quatro**
  commits após `96004f7b` (o LEIA-ME ainda diz três): licenças/titular, fontes, kit de marca e textos da loja/Discord.
  Fontes/arte e documentos de licença foram entregues nesse pacote; integração concluída nesta entrega, descrita acima.
- Simulação de integração contra `98a5a1f0`: conflitos em `NotebookScreen.java`, `TerrassicTitle.java` e neste
  quadro. Preservar a ficha do Guia/dioramas e as fontes/componentes ao conciliar. A simulação não abriu um merge
  no checkout; as telas da entrega continuam sem validação visual no jogo.
- A edição local de `tools/capagen/icone.py` foi preservada ao atualizar a main. Backup adicional em
  `build/integration-backups/identity-_g6mztrn/icone.saved.py`; arte e geradores locais não foram incluídos em commits.
- O nocaute já foi entregue por `db12c4c3`; o handoff antigo abaixo precede essa implementação. Persistência e
  interação do novo sistema ainda precisam de testes específicos. O perfil anterior chegou a 100 conexões
  estacionárias, documentado em `PERFIL_LOCAL.md`; não valida jogadores ativos nem as remasterizações novas.

Este quadro organiza responsáveis, arquivos compartilhados e evidências de entrega. O roadmap continua em
`ROADMAP.md`; este arquivo não muda decisões de produto. Cada sessão deve ler o quadro antes de editar.
O [plano mestre recebido do Rodrigo](PLANO_MESTRE.md) preserva a estratégia da outra frente, com uma nota sobre
as diferenças entre suas declarações de entrega e o checkout verificado.

## Responsáveis e próximas entregas

| Frente | Responsável | Escopo | Próxima entrega |
|---|---|---|---|
| Features complexas | Claude principal | Sistemas e conteúdo na ordem da era atual | Nocaute básico integrado; próximos pacotes: inventário de alimentação, boleadeira e territórios (`DOMESTICACAO.md`). Preservar os testes do Codex e reservar os arquivos compartilhados antes de implementar |
| Features paralelas | Claude secundário | Pacotes isolados em `paralelo/*`, com checkout separado | v0.9 integrada; próxima frente independente: roteiros e validação funcional da fauna v0.7 (dietas, loot, reprodução e habitats), sem disputar os arquivos do nocaute |
| Integração e qualidade técnica | Codex | Integração na main, build dos dois loaders, validação de recursos, estabilidade e desempenho | Nocaute 18/18 e dardos/água 22/22 passaram nos dois loaders; próximas reservas: eclosão/imprinting, combate aquático desde o animal acordado e comportamento com jogadores |
| Identidade visual | Frente de identidade já existente | Marca, paleta, fontes, logo e arte correspondente | Entrega integrada; próxima revisão: legibilidade das fontes e navegação das telas nos três idiomas, preservando a arte existente |
| Aprovação visual e experiência | Rodrigo | Aparência, som, sensação de jogo e prioridades de produto | Validar os roteiros de jogo após as entregas técnicas |

As atribuições organizam o trabalho; não significam que outras sessões já leram ou confirmaram este quadro.

Handoff após a fauna: o sistema básico de torpor/nocaute já está em `DinosaurEntity`; critérios e pendências estão
em `DOMESTICACAO.md`. Codex validou persistência e interação; a principal pode preparar os pacotes restantes,
consultando as reservas atuais da classe-base. A paralela começa conferindo os
seis animais recém-entregues contra `FAUNA.md`, registra resultados e só reserva código se encontrar um problema.
Codex continua com integração, dados, rede e desempenho. Identidade mantém a arte e o acabamento das interfaces.
Todas as frentes fazem fetch, leem este quadro e conferem a CI antes de abrir trabalho; não recriar sistemas já
entregues pelo Codex (Caderno por UUID/delta, persistência, ferramentas e testes).

## Regras de integração

1. `main` é a entrega consolidada. O Claude principal e o Codex editam nela em turnos coordenados; não editar
   os mesmos arquivos simultaneamente. A frente paralela usa outra pasta/checkout para não trocar a branch de todos.
2. Antes de começar: verificar `git status`, branch, remoto e este quadro. Registrar responsável, tarefa e arquivos.
3. Arquivos mais disputados: `gen_species.py`, `gen_resources.py`, `lore.py`, `DinosaurEntity.java`, registros,
   arquivos de idiomas, `CLAUDE.md` e `ROADMAP.md`. Reservar explicitamente antes de alterar ou regenerar.
4. Uma entrega informa commit/base, arquivos, comandos de validação e o que falta testar. Não declarar uma versão
   pronta só porque o código existe. Cada fase deve compilar isoladamente.
5. Integrar por fast-forward quando possível; preservar commits e revisar divergências antes de mesclar.
6. Fazer commits com autoria do Rodrigo conforme a configuração do repositório. Não reescrever o histórico publicado.
7. Ao concluir, liberar os arquivos e atualizar este quadro. Uma reserva antiga sem sessão ativa deve ser confirmada
   antes de impedir trabalho; não presumir que a frente continua editando indefinidamente.

## Reservas desta entrega

| Responsável | Arquivos | Estado |
|---|---|---|
| Codex | `art/menu_ia/v2/` e documentação de coordenação | Entregues três propostas para apresentação: floresta/confronto refinada, rio com Espinossauro e falésias com Pteranodonte. Sol quadrado, nuvens em blocos e menor poluição visual; PNGs 1672×941 conferidos visualmente, prompts e hashes salvos. Sem alteração do menu ativo; escolha e legibilidade na interface ainda pendentes |
| Codex | `tools/menugen/menu_vanilla.py`, ambiente reproduzível em `requirements-render.txt`, propostas em `art/menu_vanilla/v1/` e documentação | Prévias de confronto e exploração entregues para validação: 960×540, 32 amostras Cycles, modelos/texturas/animações empacotados e cenário com texturas vanilla lidas do cliente local. Round-trip de geometria dos dois animais (139 cubos cada) e hashes das fontes/saídas passaram; integridade 59 espécies/4.341 JSONs/1.845 chaves passou. Sem mudança dos fundos ativos; render final e legibilidade no jogo dependem da escolha visual |
| Codex | Novas propostas em `art/menu_ia/`, prompts e documentação desta proposta | Não aprovadas pelo Rodrigo: cenas e iluminação agradaram, mas o estilo deve ser mais Minecraft vanilla e usar os modelos originais. Três PNGs 1672×941 preservados apenas como estudo; não integrar ao menu. Substituídas como direção de trabalho pelo render determinístico em `art/menu_vanilla/` |
| Codex | `TranqDart.java`, `BlowgunItem.java`, `DinosaurEntity.java`, `SwimmingDinosaur.java` (somente estabilidade se houver falha reproduzida), `tools/validation/minecraft_client.py`, novo roteiro de dardos/água e documentação | Concluído em `36b21fb4`/`fbb144b3`: dose em alvo acordado depende de dano aceito; 22/22 passaram em Fabric e Forge, incluindo disparo submerso, alimentação e reinício. Build conjunta passou em 1 min 33 s; fontes conferidas por hash. Sem mudança de balanceamento, modelos ou respiração; arquivos liberados |
| Codex | `IslandMap.java` (leitura), `tools/validation/minecraft_client.py`, `island_map_regression.py`, documentação | Concluído em 25/10: continente real, transporte, reinício e cache sem regravação passaram em Fabric/Forge. Mesmos vetores nos dois loaders; sem mudar a implementação, desenho ou layout do mapa |
| Codex | `DinosaurEntity.java` (persistência/penalidade do nocaute), `tools/validation/minecraft_client.py`, novo `knockout_regression.py`, `CLAUDE.md`, `README.md` e documentação de coordenação/testes | Concluído em 25/10: dois bugs reproduzidos e corrigidos; regressão real 18/18 passou em Fabric e Forge, com recarga, alimentar/acordar/domesticar. Build passou em 49 s; arquivos liberados, sem mudar balanceamento, modelos ou interface |
| Codex | Integração de `sync/identidade`: `NotebookScreen.java`, `TerrassicTitle.java`, `common/build.gradle` (empacotar documentos entregues), `README.md` (links oficiais), coordenação e revisão dos arquivos mesclados | Concluído em 25/10: ficha à direita, dioramas, painel de dicas, fontes e componentes preservados; build dos dois loaders e verificações passaram; arquivos liberados. Arquivos locais de marca fora do commit |
| Codex | `AGENTS.md`, `docs/COORDENACAO.md`, `docs/PLANO_MESTRE.md`, `tools/validation/`, autoria em README/CLAUDE/metadados, ponte no roadmap | Concluído; arquivos liberados; sem alteração de sistemas de gameplay |
| Codex | Testes isolados de servidor; `tools/validation/`, `EcoSpawner.java`, `SpawnBudget.java`, classes-base de IA e persistência (`DinosaurEntity.java`, `HerbivoreDinosaur.java`, `PredatorDinosaur.java`, `DinoEggBlock.java`), docs e ponte de validação em AGENTS/CLAUDE | Concluído; arquivos liberados. Servidores/regressões Fabric e Forge, orçamento e build passaram; arte e tabelas de espécies preservadas |
| Codex | `research/Knowledge.java`, `ResearchData.java`, `Research.java`, `network/ModNetwork.java` e delta NBT, `client/ClientHooks.java`/`ClientResearch.java` (só recepção de dados), `common/build.gradle`, testes e documentação | Concluído; build e regressões de dados/protocolo passaram. Sem alterações de interface/arte ou novas features narrativas |
| Codex | `tools/validation/`, utilitários de teste em `common/src/regression/`, documentação | Concluído: conexões reais em Fabric e Forge, páginas, isolamento, negociação, reconexão e reinício passaram; fixtures Python passaram |
| Codex | `tools/validation/load_profile.py`, `tools/validation/java/JfrSummary.java`, `local_server.py`, documentação | Concluído: perfis Fabric/Forge com 0, 4, 8 e 16 conexões; roteiro e métricas em `PERFIL_LOCAL.md`. Não equivale a jogadores ativos nem valida o alvo de 100 jogadores |
| Codex | `tools/validation/minecraft_client.py`, `network_regression.py`, documentação | Concluído: Caderno após troca de dimensão e morte/respawn, reconexão e reinício passou em Fabric/Forge; arquivos liberados |
| Codex | `tools/validation/load_profile.py`, documentação | Concluído: perfil Fabric até 32 conexões; corrigida a ferramenta para entradas sequenciais após detectar concorrência no login vanilla. Resultados e limites em `PERFIL_LOCAL.md` |
| Codex | `.github/workflows/validation.yml`, `tools/validation/README.md`, documentação | Concluído: CI passou na main com a nova fauna, run `40140246290`; sem deploy ou publicação de release |
| Codex | `tools/validation/check_project.py`, `test_check_project.py`, documentação | Concluído: 481 vínculos de áudio e legendas conferidos; 18 testes passaram. Sem editar sons ou geradores |
| Codex | `tools/validation/load_profile.py`, documentação | Concluído: 32, 64 e 100 conexões estacionárias em Fabric, resultados em `PERFIL_LOCAL.md`; não valida jogadores ativos |
| Codex | `CLAUDE.md`, linha da fauna em `ROADMAP.md`, documentação de contexto | Concluído; contexto atualizado com as entregas efetivamente integradas, preservando a fila de produto |
| Claude (nuvem, fauna v0.7) | `gen_species.py`, `gen_resources.py`, `lore.py`, `egg_designs.py`, `sprites.py`, `blocks.py`, `science.py`, `build_all.py`, registros (`ModEntities`, `ModItems`, `ModBlocks`, `BuildingBlocks`), lang, `ROADMAP.md`, `ROSTER.md`, `TAMANHOS.md`, `FAUNA.md`, bestiário; fases 108-113 (Leptoceratops, Vegavis, Mesodma, Basilemys, Enchodus, Lepisosteus), uma espécie por fase sobre a anterior | Concluído; arquivos liberados (fases 108-113) |
| Claude (nuvem, blocos primitivos: padrão calmo) | `tools/texpack/chao.py` (novo), `folhas.py`, `torroes.py`, `blocos.py`, `README.md`, `tools/javagen/gen_blocks.py` (giro aleatório nos blockstates), 49 blockstates, 19 modelos `*_mirrored`, 119 texturas de chão, folhas e fósseis de crânio, `CLAUDE.md` (só o parágrafo CHÃO do motor de texturas) | Concluído com o commit: padrão calmo aprovado pelo Rodrigo em 25/10 (rochas em grão fino, solos em torrões, cores calmas, giro por bloco); arquivos liberados com o commit. Ainda não visto no jogo |
| Claude (nuvem, blocos primitivos: madeiras e paredes) | `tools/texpack/madeira.py` e `paredes.py` (novos), `blocos.py`, 66 texturas de madeira, parede e telhado, `CLAUDE.md` (só a linha MADEIRAS/PAREDES do motor de texturas) | Concluído com o commit: troncos, tábuas, rebocos, palhas e esteiras no padrão calmo, conferidos numa cena de aldeia; arquivos liberados com o commit. Ainda não visto no jogo |
| Claude principal / secundário / identidade | A registrar pelas próprias sessões | Escopo exato ainda não confirmado |
| Claude (nuvem, menu e arte 3D) | `client/ClientIslandMap.java`, `client/NotebookScreen.java` (só `renderMap`), `tools/javagen/menu_texts.py`, lang (só a chave `map.terrassic.elsewhere`, também nas variantes do espanhol), `docs/MUNDO.md` (seção 11) | Concluído com o commit (fase 168): fora do Overworld o mapa esconde a seta e troca a posição por um aviso, como apontado em `TESTES_MAPA.md`; arquivos liberados com o commit. Entregas anteriores (menu, galeria, telas de carregamento, dioramas, layout do Guia e mapa da ilha, fase 166) concluídas e ainda não vistas no jogo |
| Claude (nuvem, nocaute v0.7) | `DinosaurEntity.java`, `SwimmingDinosaur.java`, novos `TranqDart.java` e `BlowgunItem.java`, `ModItems`, `ModEntities`, `TerrassicClient` (1 linha), `gen_resources.py`, `sprites.py`, `lore.py`, lang, `docs/DOMESTICACAO.md` | Concluído com o commit: domesticação por nocaute (torpor, nocaute, alimentar derrubado, eficiência, acordar), zarabatana, dardo e erva sonífera; arquivos liberados. Ainda não testado no jogo |
| Claude secundário (identidade visual) | Branch `paralelo/identidade` (base `96004f7b`, main após a reescrita de histórico): `client/ui/` (paleta, componentes, `TerrassicButton`, `TerrassicFonts`), telas `RulesScreen`, `NotebookScreen`, `IntroScreen`, `TerrassicHud`, `SpeciesToast`, `TerrassicTitle`, `ClientConfig`, `assets/terrassic/font/`, `textures/font/`, `tools/fontgen/`, `tools/capagen/brand.py` e `ui_mock.py`, `art/identidade/`, `docs/IDENTIDADE.md`; licença (`LICENSE`, `COPYING`, `LICENSE-ASSETS.md`, `CLA.md`, campo `license` dos metadados), linhas de licença/identidade em `CLAUDE.md`, `README.md`, `ESTRATEGIA.md` e `ROADMAP.md` (T3.6, perguntas) | Integrada na main em `e4bbe9ef`; build Fabric/Forge e integridade passaram. Fontes e telas ainda precisam de revisão visual no jogo. Letreiro da tela de título e `icon.png` não foram trocados (propostas em `art/identidade/marca/`) |

## Levantamento inicial e entregas anteriores (histórico)

- Remoto `origin` consultado com sucesso em 24/10/2026: `origin/main` em `fe984c2` naquele momento.
- A `main` local incorporou por fast-forward a `paralelo/v0.9-salto`, até `3023eae`: três commits, sem conflitos.
- As demais branches locais existentes não contêm commits ausentes dessa base (conferir novamente antes de integrar).
- Versão declarada: `0.2.0`. Há código posterior à v0.2; isso não equivale a versões já lançadas ou aprovadas no jogo.
- Inventário inicial: 53 espécies; geometria, animações e texturas macho/fêmea presentes; 1.504 chaves em cada idioma
  principal; 586 blockstates. O validador reproduz as verificações de integridade.
- v0.9: Altar, ritual, chefe e efeito do Salto implementados. A dimensão do Capítulo 2 ainda não existe.
- Build limpa Fabric/Forge: `./gradlew clean build --offline --no-daemon` passou em 45 s, 28 tarefas executadas.
  Há avisos de APIs obsoletas no common/Forge; nenhum erro de compilação. Não há testes Java configurados.
- Validador: `python3 -B tools/validation/check_project.py` passou (53 espécies, 4.141 JSONs, 1.504 chaves,
  zero erros de integridade). Sete testes do validador passaram com `python3 -B -m unittest discover -s
  tools/validation -p 'test_*.py'`.
- Metadados de autoria conferidos também dentro dos dois JARs finais: apenas Rodrigo Gomes, sem referência empresarial.
- Servidor dedicado em desenvolvimento e persistência de entidades após reinício **validados em Fabric e Forge**
  nesta segunda entrega: dono, sela, baú, sexo, postura e carga preservados; nomeados/naturais preservados;
  errantes selvagens sem nome ausentes do salvamento. Animal vanilla de controle preservado. Roteiro e evidências
  em `TESTES_SERVIDOR.md`; logs em `build/server-regression/`.
- População: errantes temporários não deixam ninhos; filhotes de ovos selvagens são errantes. Spawner distribui
  jogadores por UUID, alterna prioridade dentro do mesmo tick e limita o tamanho dos grupos às vagas disponíveis.
  A contagem global continua em cache, não é teto absoluto para outras fontes de spawn.
- IA: fuga/caça checam o estado do animal antes de buscar alvos; carga, crescimento, reprodução e matilha têm
  rotinas escalonadas por entidade. O custo em MSPT ainda não foi medido.
- Testes do orçamento: passaram 1.000 hashes e 10.000 cenários com a classe Java de produção.
- Build final da segunda entrega: `./gradlew build --offline --no-daemon` passou em 20 s, após as regressões
  completas nos dois loaders. JARs gerados em `fabric/build/libs` e `forge/build/libs`.
- Testes com jogador real, reconexão, Caderno, eclosão, caça/fuga e medição de desempenho seguem pendentes.

### Terceira entrega: Caderno individual e delta de rede

- Implementados arquivos de pesquisa por UUID com migração preguiçosa e preservação do arquivo global antigo.
- Toda mutação real de `Knowledge` marca somente seu próprio arquivo para salvamento. `pages()` é somente leitura;
  usar `addPage()` ao inserir. Contrato e procedimento em `CADERNO_DADOS.md`.
- Snapshot completo ao entrar/reconectar; deltas para clientes que anunciam suporte; fallback para o canal completo
  anterior. Estado de rede separado por UUID e descartado ao sair/encerrar.
- Regressões com armazenamento/NBT reais passaram para isolamento de UUIDs, preservação do legado, recarga,
  dirty tracking e patches: 1.000 pares de NBT e 100 round-trips pelo codec real passaram na build final.
- Build Fabric/Forge com `:common:researchRegression` incluída passou em 37 s. Fixtures e classes de regressão
  foram conferidos como ausentes dos JARs finais. Logs de regressão ficam sob `common/build/`.
- Servidores Fabric e Forge revalidados com a nova implementação: `fabric-4fzbf69k` e `forge-hrik4quw`
  em `build/server-regression/`, com todos os marcadores de criação/recarga de entidades.
- Transporte com clientes conectados, telas, respawn e troca de dimensões ainda não validados nesta entrega.

### Quarta entrega: conexões reais de teste

- Cliente de protocolo local implementado, sem renderização e restrito ao servidor de teste em localhost.
- Fabric passou com dois UUIDs, páginas diferentes, delta para cliente capaz, snapshot para cliente sem delta,
  reconexão e reinício do servidor; introdução não repetiu. Logs em `build/network-regression/fabric-fjkqmtwr/`.
- Forge passou com negociação FML3 e os mesmos cenários: `build/network-regression/forge-zted3u2n/`.
  Roteiro e limites em `CADERNO_DADOS.md`; não confundir cliente de protocolo com teste visual ou JAR cliente antigo.
- Treze testes Python passaram, incluindo codec e wrapper de negociação. Nenhuma mudança adicional de produção
  foi necessária nesta quarta entrega.

### Quinta entrega: perfil gradual local

- Snapshot fixo `34953fe` compilado fora do checkout compartilhado, sem mudar de branch.
- Fabric e Forge concluíram patamares de 0, 4, 8 e 16 clientes estacionários, com ecossistema ligado.
- Na etapa de 16: Fabric teve 82 criaturas do mod e média de janelas de 16,617 ms; Forge teve 111 e 13,614 ms.
  São amostras curtas, populações diferentes e mundo plano; não usar para comparar loaders ou anunciar 100 jogadores.
- `PERFIL_LOCAL.md` documenta cenário, comandos, limitações, revisão e diretórios das gravações JFR.
- Treze fixtures Python, integridade de 54 espécies e testes do orçamento passaram; sem alterar gameplay nesta entrega.

### Sexta entrega: Caderno após dimensões e respawn

- Fabric (`fabric-rhjx7o6o`) e Forge (`forge-9vf1dt2d`), em `build/network-regression/`, passaram o roteiro ampliado.
- Alice recebeu nova página no Nether, voltou ao Overworld, morreu, solicitou respawn e recebeu outra página.
  Progresso anterior preservado, atualizações continuaram, Bob permaneceu independente e a introdução não repetiu.
- Reconexão e reinício preservaram também as páginas obtidas após as transições. Sem mudança de produção.
- Telas/renderização continuam fora do alcance desses clientes de protocolo; não declarar teste visual.

### Sétima entrega: CI, áudio e ampliação do perfil

- Workflow na main e em `paralelo/*`, PRs para main e disparo manual: integridade, fixtures, orçamento e build
  dos dois loaders com regressões de pesquisa. Ações oficiais fixadas por commit; permissões de leitura.
- Primeira execução passou todas as etapas, mas foi substituída por novo push durante a finalização.
  A execução seguinte concluiu com sucesso: https://github.com/RodrigoGomesDev/terrassic/actions/runs/40140246290.
- Validador também cobre arquivos de áudio próprios, cabeçalho Ogg, eventos inexistentes/cíclicos e legendas
  próprias nos três idiomas. Não valida audição ou decodificação. 18 fixtures Python passaram.
- Perfil Fabric até 32 conexões concluiu depois de sequenciar logins. A tentativa anterior e seus picos de tick
  foram preservados em `PERFIL_LOCAL.md`; não declarar 100 jogadores ou comparar médias como capacidade garantida.

## Fila de engenharia, sem sobrepor as features

| Prioridade | Trabalho | Condição de entrada / evidência esperada |
|---|---|---|
| 1 | Build dos dois loaders e integridade de recursos | Primeira entrega validada; repetir após alterações de código/recursos |
| 2 | Inicialização de servidor dedicado Fabric e Forge | Concluída no ambiente de desenvolvimento, com logs e roteiro automatizado |
| 3 | Persistência de domados, carga e progresso | Entidades, carga, Caderno por UUID, dimensões, respawn, reconexão e reinício validados nos dois loaders; faltam telas |
| 4 | Errantes efêmeros e controle de ninhos | Implementado; persistência validada nos dois loaders. Eclosão/ninhos ainda exigem teste no jogo |
| 5 | Spawner justo e distribuído no tempo | Implementados escalonamento e orçamento por grupo; testes aritméticos passaram. Falta simulação com jogadores/perfil e cota proporcional por jogador |
| 6 | Reduzir buscas de IA e medir custo | Saídas antecipadas implementadas; perfil inicial com clientes de protocolo em `PERFIL_LOCAL.md`; falta comportamento com jogadores completos e perfil prolongado |
| 7 | Tags/datapacks e integrações opcionais | Alinhar contrato com o Claude principal antes de mudar geradores |

## Estado das entregas de outras frentes

O plano mestre anexado pelo Rodrigo cita `docs/estudos/`, `docs/IDENTIDADE.md`, licença LGPL do código e documentos
de permissões dos assets. Estudos e identidade não estavam na conferência inicial e foram recebidos durante esta
sessão, como registrado abaixo. Os documentos de licença/permissões chegaram no bundle de identidade e foram
integrados em `e4bbe9ef`, incluindo empacotamento nos JARs; a integração está registrada no início deste quadro.

## Próximos passos por frente — 25/10

1. **Claude principal:** inventário de alimentação da criatura derrubada, boleadeira e territórios, em pacotes
   separados. Registrar e publicar a reserva antes de alterar a classe-base e os geradores; preservar as regressões.
2. **Claude secundário / identidade:** revisão de legibilidade e navegação das telas em pt-BR, inglês e espanhol;
   testar também dietas, loot e habitats da fauna v0.7. Novos pacotes em `paralelo/*`, com checkout separado.
3. **Codex:** regressão de dardos/água concluída (`TESTES_DARDOS.md`); próximas reservas podem cobrir eclosão e
   imprinting, nocaute aquático desde o animal acordado e comportamento de IA. Depois medir exploração do
   continente com geração de chunks e clientes em movimento. O teste de 100 conexões
   estacionárias não valida esses cenários.

Nocaute: `TESTES_NOCAUTE.md` registra as duas falhas reproduzidas e as correções. Os 18 casos completos passaram
nos dois loaders, inclusive dono, progresso, bônus e alimentação após reinício. Arte e barras no cliente completo
continuam fora desse teste. O LEIA-ME de `terrassic-sync` também foi atualizado, com backup, para registrar a
identidade já integrada; não repetir os merges antigos.

Reservas que precisem ser vistas pela frente remota devem ser publicadas na main antes de trabalho prolongado.
Uma reserva no arquivo local, sem commit/push, ainda não é visível para a sessão em nuvem.

Mapa recebido em `ef976e28`/`2f6ee171`: nova aba do Caderno, levantamento no servidor e imagem dinâmica no cliente.
Integrado sem conflito com o nocaute. Integridade passou com 59 espécies, 4.322 JSONs e 1.844 chaves por idioma;
build conjunta passou em 34 s. Transporte e persistência do mapa num continente real passaram depois disso em
Fabric (`fabric-wryv_6ba`) e Forge (`forge-ws0rc_v5`), com a mesma seed, nove categorias e vetores idênticos entre
loaders e após reinício; conteúdo e timestamp do cache foram preservados. Roteiro e limites em `TESTES_MAPA.md`.
A CI da main conjunta também passou: https://github.com/RodrigoGomesDev/terrassic/actions/runs/40206865365.

Próximas verificações do mapa: visualização e coordenadas fora do Overworld, dimensões grandes e interrupção do
levantamento ao fechar o servidor. Esses casos não foram cobertos pelo roteiro de transporte/cache.

Atualização `9b60910b` integrada em `fbb144b3`: a seta e as coordenadas do mapa são ocultadas fora do Overworld,
com mensagem traduzida. Código revisado e build conjunta passou; a troca de dimensão no cliente renderizado ainda
precisa ser conferida. Integridade final passou com 59 espécies, 4.322 JSONs e 1.845 chaves por idioma.
Dardos: `fabric-flkx1fyi` e `forge-jjugws9u` passaram 22/22 em `build/dart-regression/`, com as mesmas fontes de
produção verificadas por hash. Detalhes, baseline e limites em `TESTES_DARDOS.md`. O nocaute inicial do Mosassauro
é fixture por NBT; combate aquático completo desde um animal acordado continua pendente.

O plano mestre também define o projeto como pessoal. As referências empresariais foram removidas dos arquivos
atuais nesta entrega; o histórico Git permanece preservado.

### Integrações recebidas durante a validação de rede

- A outra frente incorporou `8ca5aae` e `6f0e6af`: continente, remasterizações, texpack/filtro de era, ajustes do
  Tirano, paleta/componentes de interface, estratégia e estudos. `IDENTIDADE.md`, `ESTRATEGIA.md` e `estudos/`
  agora estão presentes; o inventário antigo acima descreve a primeira conferência, não uma ausência atual.
- `a483f1b` entregou o menu "Névoa". Foi integrado com os testes de rede em `e5bc18d`.
- A build Fabric/Forge conjunta passou em 34 s, com as regressões do Caderno. O validador passou com 53 espécies,
  4.153 JSONs e 1.516 chaves por idioma. Teste visual do novo menu continua com a frente correspondente.
- Referências empresariais reapareceram nos estudos recebidos; foram ajustadas à decisão de titularidade pessoal
  do Rodrigo, inclusive as hipóteses de cessão para empresa. Não foram criados documentos de licença por esta frente.
- Integrados também `9678b59`/`801eb01` (vozes e efeitos próprios) e `9de2bed` (Leptoceratops e comida dos carnívoros).
  Conflito no quadro de reservas resolvido preservando as duas frentes. Validador: 54 espécies, 4.180 JSONs e
  1.743 chaves por idioma; build dos dois loaders com regressões passou em 27 s. A reserva da fauna 108-113 segue
  com o Claude; o perfil do Codex só lê um snapshot fixo dessas fontes.
- Integradas as fases 109-113 recebidas em `455c1ea`: Vegavis, Mesodma, Basilemys, Enchodus e Lepisosteus.
  A frente liberou os arquivos. Conflito de coordenação resolvido mantendo os estados de conclusão das duas frentes.
  Integridade: 59 espécies, 4.313 JSONs, 1.810 chaves por idioma, áudio íntegro pelos vínculos/cabeçalhos;
  build Fabric/Forge com regressões passou em 34 s. A CI da entrega recebida também passou no Linux.
