# Terrassic — coordenação entre frentes

Atualizado em 24/10/2026. Titular: **Rodrigo Gomes**, pessoa física, sem vínculo empresarial.

Este quadro organiza responsáveis, arquivos compartilhados e evidências de entrega. O roadmap continua em
`ROADMAP.md`; este arquivo não muda decisões de produto. Cada sessão deve ler o quadro antes de editar.
O [plano mestre recebido do Rodrigo](PLANO_MESTRE.md) preserva a estratégia da outra frente, com uma nota sobre
as diferenças entre suas declarações de entrega e o checkout verificado.

## Responsáveis e próximas entregas

| Frente | Responsável | Escopo | Próxima entrega |
|---|---|---|---|
| Features complexas | Claude principal | Sistemas e conteúdo na ordem da era atual | Retomar sua fase corrente; registrar aqui arquivos em uso antes de editar |
| Features paralelas | Claude secundário | Pacotes isolados em `paralelo/*`, com checkout separado | v0.9 integrada; escolher próxima fase livre e registrar escopo |
| Integração e qualidade técnica | Codex | Integração na main, build dos dois loaders, validação de recursos, estabilidade e desempenho | Servidores e persistência de entidades validados; próximos: Caderno/reconexão, comportamento com jogadores e perfil de carga |
| Identidade visual | Frente de identidade já existente | Marca, paleta, fontes, logo e arte correspondente | Entregar documentação e lista de arquivos; preservar trabalho existente |
| Aprovação visual e experiência | Rodrigo | Aparência, som, sensação de jogo e prioridades de produto | Validar os roteiros de jogo após as entregas técnicas |

As atribuições organizam o trabalho; não significam que outras sessões já leram ou confirmaram este quadro.

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
| Codex | `tools/validation/load_profile.py`, `tools/validation/java/JfrSummary.java`, documentação | Em preparação: perfil local gradual com clientes criativos estacionários e JFR; não equivale a jogadores ativos nem valida o alvo de 100 jogadores |
| Claude (nuvem, fauna v0.7) | `gen_species.py`, `gen_resources.py`, `lore.py`, `egg_designs.py`, `sprites.py`, `blocks.py`, `science.py`, `build_all.py`, registros (`ModEntities`, `ModItems`, `ModBlocks`, `BuildingBlocks`), lang, `ROADMAP.md`, `ROSTER.md`, `TAMANHOS.md`, `FAUNA.md`, bestiário; fases 108-113 (Leptoceratops, Vegavis, Mesodma, Basilemys, Enchodus, Lepisosteus), uma espécie por fase sobre a anterior | Em uso (fases 108-113) |
| Claude principal / secundário / identidade | A registrar pelas próprias sessões | Escopo exato ainda não confirmado |

## Estado observado no checkout

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

## Fila de engenharia, sem sobrepor as features

| Prioridade | Trabalho | Condição de entrada / evidência esperada |
|---|---|---|
| 1 | Build dos dois loaders e integridade de recursos | Primeira entrega validada; repetir após alterações de código/recursos |
| 2 | Inicialização de servidor dedicado Fabric e Forge | Concluída no ambiente de desenvolvimento, com logs e roteiro automatizado |
| 3 | Persistência de domados, carga e progresso | Entidades e carga validadas após reinício; faltam Caderno e reconexão de jogadores |
| 4 | Errantes efêmeros e controle de ninhos | Implementado; persistência validada nos dois loaders. Eclosão/ninhos ainda exigem teste no jogo |
| 5 | Spawner justo e distribuído no tempo | Implementados escalonamento e orçamento por grupo; testes aritméticos passaram. Falta simulação com jogadores/perfil e cota proporcional por jogador |
| 6 | Reduzir buscas de IA e medir custo | Saídas antecipadas implementadas; falta medir MSPT e confirmar comportamento com jogadores |
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
