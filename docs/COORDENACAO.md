# Terrassic — coordenação entre frentes

Atualizado em 24/10/2026. Titular: **Rodrigo Gomes**, pessoa física, sem vínculo empresarial.

Este quadro organiza responsáveis, arquivos compartilhados e evidências de entrega. O roadmap continua em
`ROADMAP.md`; este arquivo não muda decisões de produto. Cada sessão deve ler o quadro antes de editar.
O [plano mestre recebido do Rodrigo](PLANO_MESTRE.md) preserva a estratégia da outra frente, com uma nota sobre
as diferenças entre suas declarações de entrega e o checkout verificado.

## Responsáveis e próximas entregas

| Frente | Responsável | Escopo | Próxima entrega |
|---|---|---|---|
| Features complexas | Claude principal | Sistemas e conteúdo na ordem da era atual | Após a fauna 108-113: nocaute v0.7 (`DOMESTICACAO.md`); reservar base de entidades, itens, rede e geradores antes de implementar |
| Features paralelas | Claude secundário | Pacotes isolados em `paralelo/*`, com checkout separado | v0.9 integrada; próxima frente independente: roteiros e validação funcional da fauna v0.7 (dietas, loot, reprodução e habitats), sem disputar os arquivos do nocaute |
| Integração e qualidade técnica | Codex | Integração na main, build dos dois loaders, validação de recursos, estabilidade e desempenho | Servidores, persistência, Caderno, dimensões e respawn validados; CI e integração da fauna concluídas; ampliar perfil de carga estacionária gradualmente |
| Identidade visual | Frente de identidade já existente | Marca, paleta, fontes, logo e arte correspondente | Entregar documentação e lista de arquivos; preservar trabalho existente |
| Aprovação visual e experiência | Rodrigo | Aparência, som, sensação de jogo e prioridades de produto | Validar os roteiros de jogo após as entregas técnicas |

As atribuições organizam o trabalho; não significam que outras sessões já leram ou confirmaram este quadro.

Handoff após a fauna: o sistema de torpor/nocaute ainda não está em `DinosaurEntity`; o plano e os critérios estão
em `DOMESTICACAO.md`. A frente principal pode seguir por esse pacote complexo. A paralela começa conferindo os
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
| Codex | `AGENTS.md`, `docs/COORDENACAO.md`, `docs/PLANO_MESTRE.md`, `tools/validation/`, autoria em README/CLAUDE/metadados, ponte no roadmap | Concluído; arquivos liberados; sem alteração de sistemas de gameplay |
| Codex | Testes isolados de servidor; `tools/validation/`, `EcoSpawner.java`, `SpawnBudget.java`, classes-base de IA e persistência (`DinosaurEntity.java`, `HerbivoreDinosaur.java`, `PredatorDinosaur.java`, `DinoEggBlock.java`), docs e ponte de validação em AGENTS/CLAUDE | Concluído; arquivos liberados. Servidores/regressões Fabric e Forge, orçamento e build passaram; arte e tabelas de espécies preservadas |
| Codex | `research/Knowledge.java`, `ResearchData.java`, `Research.java`, `network/ModNetwork.java` e delta NBT, `client/ClientHooks.java`/`ClientResearch.java` (só recepção de dados), `common/build.gradle`, testes e documentação | Concluído; build e regressões de dados/protocolo passaram. Sem alterações de interface/arte ou novas features narrativas |
| Codex | `tools/validation/`, utilitários de teste em `common/src/regression/`, documentação | Concluído: conexões reais em Fabric e Forge, páginas, isolamento, negociação, reconexão e reinício passaram; fixtures Python passaram |
| Codex | `tools/validation/load_profile.py`, `tools/validation/java/JfrSummary.java`, `local_server.py`, documentação | Concluído: perfis Fabric/Forge com 0, 4, 8 e 16 conexões; roteiro e métricas em `PERFIL_LOCAL.md`. Não equivale a jogadores ativos nem valida o alvo de 100 jogadores |
| Codex | `tools/validation/minecraft_client.py`, `network_regression.py`, documentação | Concluído: Caderno após troca de dimensão e morte/respawn, reconexão e reinício passou em Fabric/Forge; arquivos liberados |
| Codex | `tools/validation/load_profile.py`, documentação | Concluído: perfil Fabric até 32 conexões; corrigida a ferramenta para entradas sequenciais após detectar concorrência no login vanilla. Resultados e limites em `PERFIL_LOCAL.md` |
| Codex | `.github/workflows/validation.yml`, `tools/validation/README.md`, documentação | Concluído: CI passou na main com a nova fauna, run `40140246290`; sem deploy ou publicação de release |
| Codex | `tools/validation/check_project.py`, `test_check_project.py`, documentação | Concluído: 481 vínculos de áudio e legendas conferidos; 18 testes passaram. Sem editar sons ou geradores |
| Codex | `tools/validation/load_profile.py`, documentação | Em uso: medir 32, 64 e até 100 conexões estacionárias em Fabric, com limite de média de 35 ms; não valida jogadores ativos |
| Codex | `CLAUDE.md`, linha da fauna em `ROADMAP.md`, documentação de contexto | Em uso: atualizar contagem de espécies e estados verificados de entrega, sem mudar a estratégia ou a fila de produto |
| Claude (nuvem, fauna v0.7) | `gen_species.py`, `gen_resources.py`, `lore.py`, `egg_designs.py`, `sprites.py`, `blocks.py`, `science.py`, `build_all.py`, registros (`ModEntities`, `ModItems`, `ModBlocks`, `BuildingBlocks`), lang, `ROADMAP.md`, `ROSTER.md`, `TAMANHOS.md`, `FAUNA.md`, bestiário; fases 108-113 (Leptoceratops, Vegavis, Mesodma, Basilemys, Enchodus, Lepisosteus), uma espécie por fase sobre a anterior | Concluído; arquivos liberados (fases 108-113) |
| Claude principal / secundário / identidade | A registrar pelas próprias sessões | Escopo exato ainda não confirmado |
| Claude (nuvem, menu e arte 3D) | `client/title/TerrassicMenuScreen.java`, `client/TerrassicTitle.java` (só `renderTip`), `mixin/client/LevelLoadingScreenMixin.java`, `ReceivingLevelScreenMixin.java`, `client/GuideHabitats.java`, `client/NotebookScreen.java` (diorama, layout do Guia e a nova aba Mapa), novos `world/continent/IslandMap.java` e `client/ClientIslandMap.java`, `ModContinent.java` (1 linha), `TerrassicClient` (1 linha), `tools/javagen/menu_texts.py`, lang (só chaves `map.terrassic.*` e `notebook.terrassic.tab.map`, também nas variantes do espanhol), `tools/worldgen/mapa_preview.py`, `tools/menugen/`, `docs/MENU.md`, `docs/MUNDO.md` (seção 11) | Concluído com o commit: mapa da ilha como aba "Mapa" do Caderno de Campo (levantamento do continente no servidor, desenho a tinta no cliente; `docs/MUNDO.md`, seção 11); arquivos liberados com o commit. Ainda não visto no jogo. Entregas anteriores (menu, galeria, telas de carregamento, dioramas e layout do Guia) concluídas e ainda não vistas no jogo |
| Claude (nuvem, nocaute v0.7) | `DinosaurEntity.java`, `SwimmingDinosaur.java`, novos `TranqDart.java` e `BlowgunItem.java`, `ModItems`, `ModEntities`, `TerrassicClient` (1 linha), `gen_resources.py`, `sprites.py`, `lore.py`, lang, `docs/DOMESTICACAO.md` | Concluído com o commit: domesticação por nocaute (torpor, nocaute, alimentar derrubado, eficiência, acordar), zarabatana, dardo e erva sonífera; arquivos liberados. Ainda não testado no jogo |

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
sessão, como registrado abaixo. Os arquivos de licença/permissões anunciados no plano ainda precisam ser entregues;
esta frente não os recriou nem declarou uma licença diferente da que existe nos metadados.

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
