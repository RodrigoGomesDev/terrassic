# Dardos e domesticação aquática em servidor dedicado

```sh
python3 -B tools/validation/dart_regression.py --loader fabric --eula-file /caminho/eula.txt
python3 -B tools/validation/dart_regression.py --loader forge --eula-file /caminho/eula.txt
```

Requer JDK 21, dependências no cache e EULA já aceita pelo operador. Cada execução cria um servidor somente em
localhost e um mundo plano descartável em `build/dart-regression/`. Não abre mundos do jogador. O cliente
`TerraDart` usa protocolo 763, com negociação FML3 no Forge; não renderiza o jogo.

## Cobertura

O operador prepara alvos nomeados de tamanho 1 e posiciona o jogador. Disparos usam pacotes reais de uso da
zarabatana; voo, colisão e dano passam pelo servidor normal. O roteiro contém 22 verificações:

- sem munição não sai projétil; dois usos seguidos consomem apenas um dardo da outra mão e uma durabilidade;
- o dardo fere e aumenta o torpor de um Triceratops acordado; disparos sucessivos o derrubam e registram o atirador;
- contra um alvo invulnerável, o projétil inverte seu movimento, sem ferimento nem dose de torpor;
- em um alvo já inconsciente, a dose mantém o nocaute sem tirar vida ou eficiência;
- um Mosassauro inconsciente permanece submerso por 40 ticks com ar inicialmente zero, sem dano por afogamento;
- nocaute aquático, progresso parcial, eficiência e UUID do domesticador sobrevivem ao reinício;
- um disparo dentro da água chega ao Mosassauro e mantém seu nocaute sem ferimento ou perda de eficiência;
- alimentar com bacalhau após o reinício conclui a domesticação, atribui o dono, acorda o animal e comunica
  o nível 4 da espécie ao Caderno pela conexão real.

Os tempos de recarga e permanência submersa usam ticks agendados no próprio servidor. O alvo aquático começa
inconsciente por NBT: o roteiro cobre manutenção, alimentação e persistência na água, não o combate aquático
completo desde um animal acordado. Não valida animações, mira visual, barras, equilíbrio de sobrevivência ou
todos os tamanhos e espécies. O complemento de eficiência e alimentação está em `TESTES_NOCAUTE.md`.

## Falha reproduzida

Na execução anterior à correção, `fabric-yp8pfot_`, o dardo ricocheteou no animal invulnerável e não o feriu,
mas ainda acrescentou torpor. `TranqDart.onHitEntity` aplicava a dose incondicionalmente depois da colisão vanilla.
A dose em animais acordados passou para `DinosaurEntity.hurt`, junto dos golpes que causam torpor, após o motor
aceitar o dano. A manutenção de animais já inconscientes continua no caminho específico sem ferimento.
Fórmula da dose, munição, velocidade e cooldown permanecem iguais.

Essa execução também expôs uma suposição incorreta do teste sobre reposição do campo `Air`; ela foi substituída
pela verificação de submersão e ausência de dano após ticks reais. Não houve mudança na respiração da entidade.

## Evidências e reprodução

Cada servidor compila um snapshot de revisão fixa fora do checkout compartilhado. As quatro classes examinadas
(`DinosaurEntity`, `TranqDart`, `SwimmingDinosaur` e `BlowgunItem`) são sobrepostas com as fontes locais para testar
uma correção antes do commit. Cópias exatas ficam em `tested-sources/`; `results.json` registra seus SHA-256,
a revisão base e cada resultado. `source.tar`, logs e mundo descartável ficam no mesmo diretório.

As primeiras execuções corrigidas passaram 20/20 em Fabric (`fabric-p0auup__`) e Forge (`forge-63w61o4v`),
incluindo salvamento e reinício. A build Fabric/Forge com regressões de pesquisa passou em 3 min 38 s.
A execução ampliada no Fabric (`fabric-flkx1fyi`) passou 22/22, incluindo os dois casos de disparo submerso.
As tentativas paralelas `fabric-629llyay` e `forge-h9ifleck` atingiram timeout durante a preparação do Gradle,
antes de iniciar Minecraft, e não contam como validação de gameplay. As repetições foram feitas em sequência.
A build conjunta com as novas texturas da tela de título também passou, em 2 min 36 s.
