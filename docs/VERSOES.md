# Versões do Terrassic

Regra decidida pelo Rodrigo em 05/11/2026. Vale para o Claude, o Codex e quem mais publicar: siga sempre esta regra,
sem perguntar a cada versão.

## O número: `MAIOR.MENOR.CORREÇÃO`

| Parte | Quando sobe | Exemplos |
|-------|-------------|----------|
| **CORREÇÃO** (1.7.0 → 1.7.**1**) | Conserto e ajuste fino: sem conteúdo novo, sem mudar como se joga | crash (Terralith, 1.6.1); hitbox com espaço; texto errado no Guia; densidade fora da meta; desempenho |
| **MENOR** (1.7.x → 1.**8**.0) | Conteúdo ou mecânica nova que o jogador nota; mundos antigos abrem normalmente | espécie refeita; partes de acerto; "Meus dinos"; fase de blocos; mudanças de balanceamento pedidas pela comunidade |
| **MAIOR** (1.x → **2**.0.0) | Marco grande (uma era nova do `ROADMAP.md`: 2.0 Penas e Cinzas, 3.0 Jurássico...) ou algo que quebra mundos ou configurações salvas | era nova; troca de ids que perde dinos, itens ou blocos salvos |

Na dúvida entre menor e correção: **se o jogador precisa ler o changelog para entender o que mudou no jogo dele, é
menor; se ele só percebe que "parou de dar problema", é correção.** Ao subir a menor, a correção volta a 0; ao subir a
maior, menor e correção voltam a 0.

## Uma versão, duas linhas do Minecraft

- O mesmo número nas duas branches quando o conteúdo é o mesmo: `main` (Minecraft 1.20.1, Fabric e Forge) e
  `mc/1.21.1` (Fabric e NeoForge). Uma correção que só uma linha precisa ainda sobe o número nas duas, para os números
  não se desencontrarem (a outra linha leva a mesma versão, mesmo sem mudança própria).
- A versão do Minecraft vai depois do `+` nas lojas e nas tags: `1.7.0+1.20.1` e `1.7.0+1.21.1`. Os jars já trazem o
  Minecraft no nome (`terrassic-fabric-1.21.1-1.7.0.jar`); `mod_version` em `gradle.properties` é só `1.7.0`.
- Tags git: `v1.7.0` na `main` e `v1.7.0-1.21.1` na `mc/1.21.1` (o Rexpert anuncia no #avisos quando vê a tag).

## Quando o número sobe

Só quando uma build vai para a pasta de builds (`~/Desktop/terrassic-builds`). Durante o trabalho, o número fica parado:
vários commits de um mesmo pacote saem numa versão só.

1. Fechar o pacote: código, testes (`tools/validation/README.md`) e documentos.
2. Subir `mod_version` nas duas branches, pela tabela acima, com um commit "X.Y.Z: número da versão".
3. Compilar as duas branches (`./gradlew build`) e copiar os 4 jars para `~/Desktop/terrassic-builds`:
   `terrassic-fabric-1.20.1-X.Y.Z.jar`, `terrassic-forge-1.20.1-X.Y.Z.jar`, `terrassic-fabric-1.21.1-X.Y.Z.jar`,
   `terrassic-neoforge-1.21.1-X.Y.Z.jar`. Notas, quando houver, em `vX.Y.Z/` ao lado.
4. O Codex publica as builds nas lojas e coloca o changelog.
5. **O mesmo changelog entra no repositório como `docs/changelog/X.Y.Z.md`**, com uma seção `## Português` e uma
   `## English` (o formato dos que já estão lá), **no mesmo push** da versão ou antes dele. Os avisos do Rexpert no #builds e no
   #avisos publicam a seção `## English`: o servidor do Discord é em inglês, e os commits (em português, na língua da equipe) não vão
   mais para lá. Sem o arquivo, o aviso sai só com "A new build is out".
6. Depois disso, push da `main` e da `mc/1.21.1`: em até 30 minutos o Rexpert vê o `mod_version` novo na `main` e
   posta no #builds (`rexpert/src/lib/builds.js`).
7. Tags (`vX.Y.Z` e `vX.Y.Z-1.21.1`) quando o Rodrigo quiser o anúncio oficial no #avisos.

## Versões de teste

Para a comunidade testar antes de fechar uma versão menor ou maior: `1.8.0-beta.1`, `1.8.0-beta.2`... Só a `1.8.0`
final ganha tag e anúncio oficial. Correções não precisam de beta.

## Exemplos da história

- 1.6.0 → 1.6.1: crash do Terralith, só correção. Certo.
- 1.6.1 → 1.7.0: feedback de jogador (vida, doma, spawn, clava) com coisas novas (Meus dinos, partes de acerto, seções do
  Guia). Certo: menor.
- Os espaços nas hitboxes, achados depois, seriam 1.7.1 se a 1.7.0 já tivesse ido para os jogadores; como ainda não
  tinha saído, entraram na própria 1.7.0.
- 1.1.4 → 1.5.0 (02/11): três números de uma vez, sem publicação no meio. Pela regra, seria 1.2.0.
