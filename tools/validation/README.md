# Validação de integridade

Execute na raiz do projeto, com Python 3.9 ou superior, sem instalar bibliotecas:

```sh
python3 -B tools/validation/check_project.py
python3 -B -m unittest discover -s tools/validation -p 'test_*.py'
```

O primeiro comando pode rodar de qualquer pasta usando o caminho completo do script. Retorna 0 se passar e 1
se encontrar erro. O script lê as tabelas por AST; não importa nem executa geradores e não grava arquivos.

Verifica:

- JSONs dos recursos comuns e pacotes embutidos, incluindo chaves duplicadas;
- paridade das tabelas SPECIES, SIZES, GUIDE e WORLD e IDs duplicados;
- presença de classes, geometrias, animações, texturas dos dois sexos, modelos dos ovos geradores, loot e blockstates de ovos;
- identificador das geometrias, nomes de ossos duplicados e referências a pais inexistentes;
- cabeçalho/dimensões PNG em relação à geometria e namespace das animações;
- paridade de chaves entre pt_br, en_us e es_es.
- vínculos dos arquivos Ogg próprios em `sounds.json`, cabeçalho do contêiner, referências entre eventos
  (incluindo ciclos) e legendas `subtitles.terrassic.*` nos três idiomas. Referências vanilla ou de outros mods
  não são resolvidas pelo validador local.

Não verifica pixels, animação em execução, ciência, balanceamento, todos os vínculos entre recursos ou código Java.
Arquivos presentes não significam conteúdo completo ou aprovado. Áudio é conferido por vínculo e cabeçalho,
sem decodificação, CRC, audição ou julgamento de volume/qualidade. As classes são verificadas por presença;
a compilação continua sendo responsabilidade do Gradle. O PNG é verificado pelo cabeçalho, não decodificado.

Os testes usam projetos mínimos temporários para confirmar aceitação de uma entrega íntegra, ausência de gravações
e rejeição de arquivos ausentes, JSON duplicado, tabelas divergentes, traduções ausentes, nomes de animação errados
e dimensões de textura incompatíveis. Não alteram o projeto real.

Depois, compile Fabric e Forge com `./gradlew build --no-daemon` e siga os roteiros `docs/TESTES_V*.md`.

Testes adicionais de orçamento e servidor real: [`docs/TESTES_SERVIDOR.md`](../../docs/TESTES_SERVIDOR.md).
`check_spawn_budget.py` testa a classe Java de produção sem dependências; `server_regression.py` verifica estado
de entidades após reiniciar um mundo temporário nos dois loaders.

`network_regression.py` conecta dois clientes de protocolo por sockets reais a um servidor descartável. Verifica
páginas por UUID, snapshot/delta, dimensões, morte/respawn, reconexão e persistência após reinício; suporta FML3 do Forge.
Comandos e limites em [`docs/CADERNO_DADOS.md`](../../docs/CADERNO_DADOS.md). Esses clientes não renderizam o jogo.

`knockout_regression.py` usa fixtures de nocaute, cliques reais de alimentação, salvamento e reinício para conferir
eficiência, progresso, dono e bônus de vida. Comandos e limites em
[`docs/TESTES_NOCAUTE.md`](../../docs/TESTES_NOCAUTE.md); requer EULA explícita e servidor descartável.

`island_map_regression.py` cria um continente Terrassic real, recebe o levantamento por socket e confere cache e
pacote após reiniciar o servidor. Comandos e limites em [`docs/TESTES_MAPA.md`](../../docs/TESTES_MAPA.md).

`load_profile.py` aumenta a carga por etapas em um servidor descartável compilado a partir de uma revisão fixa.
Registra eventos reais de ticks pelo JFR integrado, sem mods de perfil adicionais. Comandos, resultados e
limites em [`docs/PERFIL_LOCAL.md`](../../docs/PERFIL_LOCAL.md).

## Validação automática

O workflow [validation.yml](../../.github/workflows/validation.yml) executa integridade, fixtures Python,
orçamento Java e `./gradlew build` (incluindo `researchRegression`) em pushes da main, branches `paralelo/*`,
pull requests para main e disparos manuais. Executa no Linux com JDK 21 e tem prazo de 30 minutos.

As ações oficiais [Checkout](https://github.com/actions/checkout),
[Setup Java](https://github.com/actions/setup-java) e [Setup Gradle](https://github.com/gradle/actions)
estão fixadas por commit. O job só precisa ler o repositório. Execuções novas substituem a anterior na mesma
referência; o cache é gravado pela main e apenas lido nas demais referências.

A CI não inicia servidores nem aceita EULA automaticamente, não executa testes visuais e não publica releases.
Conexões, persistência em servidor e perfis locais continuam pelos roteiros explícitos acima.
