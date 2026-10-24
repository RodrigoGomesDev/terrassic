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

Não verifica pixels, animação em execução, ciência, balanceamento, todos os vínculos entre recursos ou código Java.
Arquivos presentes não significam conteúdo completo ou aprovado. As classes são verificadas por presença;
a compilação continua sendo responsabilidade do Gradle. O PNG é verificado pelo cabeçalho, não decodificado.

Os testes usam projetos mínimos temporários para confirmar aceitação de uma entrega íntegra, ausência de gravações
e rejeição de arquivos ausentes, JSON duplicado, tabelas divergentes, traduções ausentes, nomes de animação errados
e dimensões de textura incompatíveis. Não alteram o projeto real.

Depois, compile Fabric e Forge com `./gradlew build --no-daemon` e siga os roteiros `docs/TESTES_V*.md`.

Testes adicionais de orçamento e servidor real: [`docs/TESTES_SERVIDOR.md`](../../docs/TESTES_SERVIDOR.md).
`check_spawn_budget.py` testa a classe Java de produção sem dependências; `server_regression.py` verifica estado
de entidades após reiniciar um mundo temporário nos dois loaders.
