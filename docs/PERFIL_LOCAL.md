# Perfil local gradual de servidor

Este roteiro mede uma carga pequena e reproduzível antes de tentar cargas maiores. Não valida a meta de
100 jogadores, uma sessão de sobrevivência nem o custo da geração do continente Terrassic.

```sh
python3 -B tools/validation/load_profile.py --loader fabric --eula-file /caminho/eula.txt --counts 0,4,8,16 --warmup 10 --duration 15
python3 -B tools/validation/load_profile.py --loader forge --eula-file /caminho/eula.txt --counts 0,4,8,16 --warmup 10 --duration 15
```

O operador fornece um `eula.txt` já aceito. Os servidores ficam em localhost, offline, com mundos descartáveis
em `build/load-profile/`. O script salva o SHA da revisão, arquiva as fontes dessa revisão em `source.tar` e
compila em uma pasta temporária separada; alterações de outras frentes na main não mudam o servidor medido.
As dependências precisam estar no cache do Gradle (`--offline`). Os logs, gravações JFR e `results.json` ficam
no diretório de cada execução. As fontes temporárias são removidas ao encerrar o servidor.

## Cenário e interpretação

- Java 21, alvo Java 17, heap de servidor 2 GiB e Gradle 1 GiB.
- Mundo plano de planície, estruturas desativadas, dia fixo, ecossistema ligado, tempestades de fenda desligadas.
- Distâncias do servidor: visão 4 e simulação 4 chunks. Clientes criativos estacionários em uma grade de 32 m.
- Clientes reais de protocolo, com keepalive e confirmação de teleporte, sem renderização, movimento, combate
  ou interação de sobrevivência. Forge negocia FML3. Não são instâncias completas do Minecraft cliente.
- Cada etapa espera o aquecimento e grava JFR. O próximo patamar é cancelado se a média das janelas superar
  `--max-mspt` (35 ms por padrão). Não extrapolar o resultado para mais jogadores.
- `minecraft.ServerTickTime` fornece uma **média móvel por evento periódico**. `mean_window_mspt`,
  `p95_window_mspt` e `max_window_mspt` resumem essas janelas, não a distribuição dos ticks individuais.
  Gravações de 15 s são apenas smoke tests; não estimam uma cauda de latência estável.
- A contagem de criaturas usa a tag temporária com as espécies da revisão arquivada. Ela informa entidades
  carregadas no momento da consulta; não é uma contagem de todas as entidades salvas no mundo.

## Execução Fabric, 24/10/2026

Revisão `34953fe6461953e13ee64ece03b86a817601f75f`, macOS ARM64, 8 CPUs lógicas.
Aquecimento de 10 s e gravação de 15 s por etapa; relatório em `build/load-profile/fabric-1jn077m7/`.

| Conexões | Criaturas do mod | Eventos JFR | Média das janelas (ms) | Máximo das janelas (ms) |
|---:|---:|---:|---:|---:|
| 0 | 0 | 15 | 0,971 | 2,173 |
| 4 | 45 | 16 | 4,274 | 5,937 |
| 8 | 78 | 15 | 9,523 | 15,252 |
| 16 | 82 | 15 | 16,617 | 34,381 |

Todos os patamares concluíram; os clientes foram desconectados e o mundo salvo antes de encerrar.
O custo inclui rede local, entidades vanilla, criaturas do mod e instrumentação JFR no mesmo computador.
O número de criaturas e a área carregada mudam entre etapas; esta tabela não isola custo por jogador ou por criatura.

## Execução Forge, 24/10/2026

Mesma revisão e configuração, execução separada: `build/load-profile/forge-q3dj7u9n/`.

| Conexões | Criaturas do mod | Eventos JFR | Média das janelas (ms) | Máximo das janelas (ms) |
|---:|---:|---:|---:|---:|
| 0 | 0 | 15 | 0,909 | 2,394 |
| 4 | 48 | 16 | 5,988 | 18,023 |
| 8 | 87 | 15 | 11,054 | 27,199 |
| 16 | 111 | 15 | 13,614 | 32,221 |

Todos os patamares concluíram, incluindo negociação FML3, com salvamento ao encerrar. A população não é
idêntica entre execuções; estes resultados não estabelecem qual loader é mais rápido.

## Ampliação inicial: tentativa interrompida antes de medir 32

`build/load-profile/fabric-mtf6xiq1/`, revisão de runtime `a0b9e2e`, aquecimento de 20 s e gravações de 30 s:

| Conexões medidas | Criaturas do mod | Eventos JFR | Média das janelas (ms) | Máximo das janelas (ms) |
|---:|---:|---:|---:|---:|
| 0 | 0 | 30 | 0,756 | 4,053 |
| 16 | 112 | 30 | 15,074 | 97,473 |

O pico de 97,473 ms mostra que uma média abaixo de 35 ms não garante ausência de travadas. O resumo nativo
registrou quatro coletas de lixo e 2.109 ms de duração total de GC nessa gravação; isto não atribui sozinho a causa
de cada pico. O computador também executa outras aplicações; não é uma máquina de benchmark isolada.

A etapa de 32 **não foi medida** nessa tentativa. Um dos logins simultâneos encerrou a conexão; o log contém
`ThreadingDetector` em `LegacyRandomSource.next`, chamado pelo construtor vanilla de
`ServerLoginPacketListenerImpl`, numa thread Netty. Nenhum frame Terrassic aparece nessa pilha de falha.
O roteiro encerrou os clientes e salvou o mundo. As gravações e os resultados das etapas anteriores foram preservados.

O perfil passou a esperar JoinGame de cada cliente antes de iniciar o próximo handshake. Isso permite investigar
carga estável sem misturar um teste de rajada de logins; não constitui uma correção do login vanilla no mod.

## Repetição com entradas sequenciais, até 32 conexões

`build/load-profile/fabric-r7k2no8l/`, revisão de runtime `9dd7bfa`, mesma configuração de 20 s/30 s.
A diferença entre essa revisão e as anteriores é de ferramentas/documentação, sem mudar o runtime do mod.

| Conexões | Criaturas do mod | Eventos JFR | Média das janelas (ms) | Máximo das janelas (ms) |
|---:|---:|---:|---:|---:|
| 0 | 0 | 30 | 0,662 | 1,298 |
| 16 | 105 | 30 | 8,460 | 79,168 |
| 32 | 112 | 30 | 6,035 | 22,892 |

As 32 conexões permaneceram ativas e a execução concluiu com salvamento. Os custos não cresceram de forma
monotônica: aquecimento da JVM, atividade das criaturas, população e pausas variam durante a execução.
O resultado de 32 não demonstra que adicionar jogadores reduz custo, nem permite extrapolar para 100 jogadores
ativos. Em particular, as duas execuções de 30 s tiveram picos acima de 35 ms na etapa de 16 conexões.

## Próximas medições

Comparar repetições mais longas na mesma revisão; depois medir exploração do continente, sobrevivência,
montarias e combate com clientes completos, mantendo memória, entidades, distâncias e máquina registradas.
O JFR integrado permite este primeiro diagnóstico sem dependências novas; o perfil spark exigido pelo roadmap
para uma versão lançada continua pendente.
