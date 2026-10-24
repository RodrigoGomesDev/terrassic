# Terrassic — instruções para agentes

Autor e titular: **Rodrigo Gomes**, pessoa física, sem vínculo empresarial.
Responda em português. Leia `docs/COORDENACAO.md`, `CLAUDE.md` e `docs/ROADMAP.md` antes de editar.

## Coordenação

- A branch de integração e entrega é `main`, conforme pedido do Rodrigo em 24/10/2026.
- Claude principal: features complexas e conteúdo do roadmap, trabalhando na `main`.
- Claude secundário: entregas isoladas em `paralelo/*`; integrar na `main` após revisão e build.
- Codex: integração, validação, estabilidade e desempenho. Registre o escopo antes de alterar arquivos compartilhados.
- Identidade visual: frente já existente; não substituir sua arte ou suas decisões sem consultar a entrega dela.
- Não troque a branch de uma pasta que outra sessão esteja usando. Branches paralelas precisam de checkout separado.
- Antes de editar, confira `git status`, a branch atual e o quadro de arquivos em `docs/COORDENACAO.md`.
- Preserve alterações de outras frentes. Não execute geradores em massa sobre trabalho em andamento.
- Atualize o quadro ao concluir uma entrega: commit, validação executada e pendências reais.
- Autonomia registrada em documentos antigos não é uma ordem para executar todas as fases nesta sessão: siga o pedido atual e a divisão das frentes.

## Implementação

- Java 17 como alvo, JDK 21 para Gradle; Minecraft 1.20.1, Fabric + Forge via Architectury.
- Código comum não depende de classes específicas de um loader ou de classes de cliente no servidor.
- Edite a fonte dos geradores em `tools/`, não apenas os arquivos gerados. Respeite os marcadores `GENERATED`.
- Mantenha português, inglês e espanhol em paridade.
- Escala real: 1 bloco = 1 metro. Conteúdo novo segue a era atual e a fila do roadmap.
- Concluir código, compilar e testar no jogo são estados distintos. Nunca declare validação que não foi executada.
- Não altere licenças com base apenas em resumos de outras sessões: confira os arquivos efetivamente entregues.

## Verificação

```sh
python3 -B tools/validation/check_project.py
./gradlew build --no-daemon
```

Use `--offline` se todas as dependências já estiverem no cache. Validação de recursos e build não substituem
testes de servidor, recarga do mundo, multiplayer e revisão visual no jogo.
