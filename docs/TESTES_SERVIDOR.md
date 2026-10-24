# Servidor dedicado, persistência e orçamento do ecossistema

Frente: Codex. Minecraft 1.20.1, JDK 21; Fabric e Forge. Estes testes não substituem os roteiros de experiência no jogo.

## Evidências de 24/10/2026

| Verificação | Resultado | Evidência |
|---|---|---|
| Servidor Fabric: criação, arquivo salvo e reinício | Passou | `build/server-regression/fabric-xi88ex2n/{create,reload}.log`; todos os marcadores esperados |
| Servidor Forge: criação, arquivo salvo e reinício | Passou | `build/server-regression/forge-4c1nvndy/{create,reload}.log`; todos os marcadores esperados |
| Orçamento e escalonamento | Passou | 1.000 hashes e 10.000 cenários, executando a classe Java de produção |
| Integridade dos recursos | Passou | 53 espécies, 4.141 JSONs, 1.504 chaves por idioma; sete testes do validador |
| Build final Fabric e Forge | Passou | `./gradlew build --offline --no-daemon`: 20 s, após as regressões completas |

Os logs completos e mundos de teste ficam em `build/` (ignorados pelo Git); esta tabela preserva o resultado
no repositório. As primeiras tentativas do harness falharam por sua configuração `spawn-animals=false`,
corrigida após comparar com um animal vanilla e conferir `ServerLevel.shouldDiscardEntity` no Minecraft local.
Isso não foi tratado como defeito de persistência do mod. O teste final também aguarda o carregamento de
entidades e trata o watcher de desenvolvimento conforme descrito abaixo.

## Regressão automatizada em servidor real

Requer um `eula.txt` já aceito pelo operador. O comando copia esse arquivo para uma pasta de teste; não modifica
mundos existentes nem inicia um servidor público. Cada execução cria um mundo descartável em
`build/server-regression/<loader>-<id>/`, com logs completos, configuração própria, localhost e porta automática.

```sh
python3 -B tools/validation/server_regression.py --loader fabric --eula-file /caminho/eula.txt
python3 -B tools/validation/server_regression.py --loader forge --eula-file /caminho/eula.txt
```

O servidor usa modo offline para não depender de autenticação no teste; está vinculado apenas a `127.0.0.1`.
Os dois loaders devem rodar em sequência: compartilham os arquivos de compilação do common.
O Gradle usa `--offline`; preencha o cache de dependências com uma build normal se necessário.

Na primeira inicialização, o teste cria um Edmontosaurus domado com dono UUID fixo, sela, baú, sexo, postura de
sentar e sete diamantes no slot 0; cria também um errante selvagem, um errante nomeado e um animal natural.
Um porco vanilla funciona como controle. Os animais ficam sem IA/gravidade, em altura segura, para isolar o estado
salvo. Desativa spawn pela gamerule `doMobSpawning` e ticks aleatórios; `spawn-animals` precisa continuar `true`,
pois o Minecraft remove animais existentes quando essa propriedade é `false`. Salva e encerra o Minecraft.
Confere os tags dos fixtures nos arquivos de entidades antes de reiniciar, preservando uma cópia para diagnóstico.
Na segunda inicialização verifica:

- dono, sela, baú, sexo, postura e carga preservados no domado;
- errante selvagem sem nome ausente, pois é população temporária;
- errante nomeado e animal natural preservados.
- animal vanilla de controle preservado.

Os marcadores de confirmação precisam aparecer no log do servidor; comando enviado não conta como teste aprovado.
O teste tem prazo por inicialização e falha se faltarem marcadores. O watcher de hot reload do Architectury pode
manter a JVM de desenvolvimento aberta depois de `stop`: o harness só encerra esse grupo isolado após observar
`Stopping server` e o salvamento final de todas as dimensões, aguardando mais cinco segundos. Isso fica registrado
no log e não é confundido com encerramento espontâneo do Gradle.

## Orçamento e escalonamento

```sh
python3 -B tools/validation/check_spawn_budget.py
```

Compila a classe de produção `SpawnBudget` e o teste em uma pasta temporária, com alvo Java 17. Sem bibliotecas
de teste ou Minecraft. Verifica mil hashes, inclusive extremos negativos/positivos: cada jogador tem uma rodada
por período de 40 ticks, distribuída entre os ticks. Dez mil cenários verificam limites locais, globais, mundo
lotado e consumo de vagas entre grupos/categorias.

## Mudanças cobertas e limites

- Errantes selvagens sem nome não entram no salvamento nem deixam ninhos. Domar ou nomear os torna persistentes.
- Filhotes de ovos selvagens são errantes; ovos colocados pelo jogador continuam produzindo animais persistentes.
- Manadas naturais continuam salvas e podem produzir ninhos. O desaparecimento à distância mantém a regra existente.
- O spawner distribui jogadores por UUID e alterna prioridade dentro do mesmo tick. Cada grupo respeita seu alvo
  local e as vagas restantes da contagem global em cache. Só conta inserções de entidade aceitas pelo servidor.
- A busca local e os pontos de spawn ficam limitados a 80 blocos de diferença vertical. Membros de grupos fora
  de chunks em simulação são ignorados antes de consultar terreno/colisão.
- A contagem global continua aproximada, refeita a cada 200 ticks com jogadores elegíveis. Spawns de outros sistemas
  entre contagens podem ultrapassar o limite: isto não é um teto absoluto para todas as fontes de spawn.
- Metas de fuga e caça fazem a checagem do próprio animal antes de buscar alvos. Rotinas de carga, crescimento,
  reprodução e chamadas de matilha são escalonadas pelo ID da entidade.

Esta primeira regressão não mede rede ou desempenho. Entregas posteriores validaram Caderno individual,
reconexão e reinício com clientes locais de protocolo em Fabric e Forge: consulte `CADERNO_DADOS.md`.
O perfil inicial de ticks com carga gradual está em `PERFIL_LOCAL.md`; a meta de 100 jogadores continua pendente.
Os testes de persistência acima usam entidades geradas por comandos, sem interação de um jogador real.
O roteiro do Caderno também cobre transferência entre dimensões vanilla e respawn via protocolo nos dois loaders.
Eclosão de ovos e comportamento de caça/fuga ainda precisam de validação no jogo.

## Próximos testes de experiência

1. Domar um errante por comida e nomear outro por etiqueta. Recarregar o chunk e o mundo: ambos permanecem.
2. Chocar um ovo selvagem: filhote errante, sem dono. Roubar e recolocar outro ovo: o filhote continua persistente,
   com imprinting se houver jogador perto. Conferir que manadas naturais continuam deixando ninhos.
3. Gallimimus selvagem foge de jogador/predador; domado segue o dono mesmo perto de um predador. Triceratops adulto
   continua se defendendo. Predador saciado não inicia caça; domado ainda defende o dono de um ataque.
4. Dois jogadores próximos e dois distantes: conferir povoamento, grupos parciais quando só restam poucas vagas,
   saída/entrada de jogadores e níveis diferentes de simulation distance. Comparar perfis antes/depois com spark.
5. Repetir os roteiros do Caderno com dois jogadores, reconectar e reiniciar o servidor: progresso individual intacto.
