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
| Integração e qualidade técnica | Codex | Integração na main, build dos dois loaders, validação de recursos, estabilidade e desempenho | Validador de integridade, diagnóstico de build e fila de multiplayer |
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
- Testes no jogo, servidor dedicado e medição de desempenho não executados; seguem pendentes.

## Fila de engenharia, sem sobrepor as features

| Prioridade | Trabalho | Condição de entrada / evidência esperada |
|---|---|---|
| 1 | Build dos dois loaders e integridade de recursos | Comando reproduzível, resultado e diagnóstico |
| 2 | Inicialização de servidor dedicado Fabric e Forge | Logs de inicialização sem referências indevidas ao cliente |
| 3 | Persistência de domados, carga e progresso | Recarregar mundo e reconectar preservando estado e dono |
| 4 | Errantes efêmeros e controle de ninhos | Reservar `DinosaurEntity`/`DinoEggBlock` com o Claude principal; preservar animais nomeados e domados |
| 5 | Spawner justo e distribuído no tempo | Reservar `EcoSpawner`; testar jogadores próximos/distantes e limites de população |
| 6 | Reduzir buscas de IA e medir custo | Reservar classes-base; comparar perfil e comportamento antes/depois |
| 7 | Tags/datapacks e integrações opcionais | Alinhar contrato com o Claude principal antes de mudar geradores |

## Entregas externas ainda ausentes daqui

O plano mestre anexado pelo Rodrigo cita `docs/estudos/`, `docs/IDENTIDADE.md`, licença LGPL do código e documentos
de permissões dos assets. Esses arquivos não estavam neste checkout na conferência inicial. Não recriar o trabalho
dessas frentes nem anunciar as licenças como aplicadas antes de receber e integrar os arquivos correspondentes.

O plano mestre também define o projeto como pessoal. As referências empresariais foram removidas dos arquivos
atuais nesta entrega; o histórico Git permanece preservado.
