# Caderno — persistência individual e sincronização

Frente: Codex, 24/10/2026. Não altera os objetivos, capítulos ou a aparência do Caderno.

## Arquivos por jogador

O conhecimento continua pertencendo ao jogador e ao mundo, independentemente do item Caderno, da dimensão ou
do inventário. O salvamento usa o `DimensionDataStorage` do Overworld e o ciclo normal de `SavedData` do Minecraft:

- Antes: `world/data/terrassic_research.dat`, com todos os UUIDs em `data.Players`.
- Agora: `world/data/terrassic_research_<uuid>.dat`, com `data.Version = 1` e `data.Knowledge`.
- O arquivo antigo permanece intacto, como arquivo de migração/recuperação; não recebe as novas alterações.

A migração é preguiçosa: ao acessar um UUID sem arquivo individual, o sistema importa somente seu conhecimento
antigo e marca esse registro para salvamento. Um arquivo individual existente sempre tem prioridade sobre o
arquivo antigo. Jogadores novos começam vazios, e um jogador nunca herda os dados de outro. Não há exclusão
automática do arquivo antigo nem migração destrutiva em lote.

Os novos arquivos são gravados nos autosaves/encerramento normais do Minecraft. Alterar Alice não marca o
registro de Bob como sujo, nem regrava o arquivo global. Backups do mundo precisam incluir `world/data/` inteiro.
Builds anteriores a essa mudança não leem os novos arquivos individuais; retornar a uma build antiga não incorpora
automaticamente o progresso feito depois da migração.

O cache de `DimensionDataStorage` segue o comportamento do Minecraft: registros já carregados ficam em memória
até encerrar o servidor. Separar os arquivos reduz regravações, mas não implementa expulsão de registros inativos
desse cache nem elimina o custo de ler o arquivo legado na primeira abertura.

## Contrato para outras frentes

- Use `Research.knowledge(player)` ou `ResearchData.get(server).of(uuid)` como antes.
- As mutações de `Knowledge` notificam o próprio registro de salvamento. Não marque o arquivo global como sujo.
- `pages()` agora é uma visão somente de leitura; use `addPage()` para inserir e manter o rastreamento de alteração.
- Métodos novos que alterem conhecimento devem chamar o listener somente quando o valor realmente mudar.
- Níveis ficam entre desconhecido e domesticado; pontos entre 0 e 99; contadores saturam em `Integer.MAX_VALUE`.
  IDs de espécies/páginas desconhecidos continuam preservados, permitindo dados de conteúdo posterior.

## Rede

O servidor continua sendo a autoridade do conhecimento; esta entrega não adiciona um pacote cliente→servidor
que permita editar progresso.

- `terrassic:research_sync`: snapshot completo, no formato NBT anterior. Sempre enviado ao entrar/reconectar.
- `terrassic:research_delta`: alterações desde o último snapshot dessa conexão, apenas se o cliente anuncia o receptor.
- Sem mudanças no conhecimento: nenhum pacote de atualização.
- Cliente sem suporte ao delta: continua recebendo o snapshot completo pelo canal anterior.
- Ao desconectar, descarta-se a base de rede daquele UUID; ao encerrar o servidor, todas as bases são descartadas.

O delta substitui valores/listas/arrays, aplica patches recursivos em compostos e representa remoções explicitamente.
O cliente aplica uma cópia do patch e reconstrói seu modelo local. Ao sair do servidor, limpa o conhecimento local,
como antes. A ordem de aplicação depende da entrega ordenada da conexão Minecraft; não é um protocolo para
transporte com perda/reordenação de pacotes.

Na fixture com 53 espécies (`species_0` a `species_52`), uma alteração de contador mede 2.148 bytes em snapshot
completo e 59 bytes em delta, usando `FriendlyByteBuf.writeNbt`. Isso mede conteúdo NBT dessa fixture, não tráfego
total nem desempenho de um servidor com jogadores.

## Regressões

```sh
./gradlew :common:researchRegression --offline --no-daemon
```

O teste faz parte de `:common:check` e, portanto, da build. Usa classes reais do Minecraft, NBT e arquivos temporários,
sem biblioteca adicional de testes. Os fixtures ficam em `common/src/regression`, fora dos JARs publicados.

Verificações:

- Round-trip de níveis, pontos, páginas, objetivos, contadores e flag da introdução, inclusive pontos antes de avistar.
- Todas as rotas de mutação notificam salvamento; operações sem efeito não sujam o arquivo.
- Dois UUIDs migram de um arquivo legado; cada um mantém seu estado após reabrir o armazenamento.
- Migrar somente Alice não cria o arquivo de Bob. Alterar Alice não altera bytes nem data de modificação de Bob.
- O arquivo legado permanece idêntico, byte por byte; o arquivo individual prevalece sobre o legado antigo.
- Mil pares de NBT cobrem delta com campos removidos, compostos, listas, arrays e mudanças de tipo; cem passam
  também pelo codec `FriendlyByteBuf` real. Aplicar o patch não modifica a base.
- Estado do protocolo: snapshot inicial, supressão de duplicatas, reconstrução do cliente, UUIDs independentes,
  desconexão/reconexão, limpeza ao encerrar e fallback para clientes sem delta.

Esses testes de estado/protocolo não simulam um cliente conectado. Reconexão real, respawn, transição entre
dimensões, telas e compatibilidade com um JAR cliente antigo continuam exigindo validação em jogo/rede real.

Resultado em 24/10/2026: a build completa Fabric/Forge passou em 37 s, incluindo todas as regressões acima.
Os servidores dedicados foram revalidados pelos roteiros de entidades nos dois loaders após a mudança.
