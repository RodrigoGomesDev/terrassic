# População de voadores — auditoria e correção, 26/10/2026

Rodrigo relatou aves aparecendo ao virar a câmera e mais de 40 voadores visíveis. O objetivo é
um céu com encontros espaçados, sem reposição contínua de bandos na frente do jogador.

## Causas encontradas

1. O EcoSpawner repunha até oito aves por jogador a cada dois segundos, contando apenas uma caixa
   de 80 blocos em X/Z e altura. Aves fora dessa caixa podiam continuar carregadas e visíveis,
   deixando vagas falsas para novos bandos. Virar a câmera não era um gatilho do código, mas revelava
   animais inseridos enquanto o jogador observava outra direção.
2. As mesmas espécies também estavam no spawn natural/de geração de chunks. Esses nascimentos
   podiam criar animais permanentes sem passar pelo orçamento do EcoSpawner.
3. A regra de despawn do mod após 96 blocos não significava desaparecimento imediato: o bytecode
   local do Minecraft 1.20.1 confirma que `Mob.checkDespawn` também usa limites da categoria,
   persistência, tempo sem ação e sorteio. Assim, diminuir somente esse número não resolveria o ciclo.
4. O teste real encontrou um crash anterior na classificação de fauna: instanciar Deinosuchus
   chamava `FollowOwnerGoal`, incompatível com sua navegação anfíbia. Navegações alternativas agora
   usam uma meta de seguir o dono que delega ao próprio navegador, sem teletransporte.

## Política implementada

| Parâmetro padrão | Antes | Agora |
|---|---|---|
| Alvo de aves | 8 na área de cada jogador | 4 no céu regional compartilhado |
| Contagem | 80 blocos em X/Z e Y | 192 blocos em X/Z, toda a altura do mundo |
| Rodada de reposição | 2 segundos | 20 segundos, distribuída por UUID |
| Inserção | 36–80 blocos | 64–112 blocos, evitando proximidade e visão direta dos jogadores |
| Fontes automáticas de aves selvagens | Natural/de chunks + EcoSpawner | EcoSpawner usa as tabelas do bioma como fonte única de reposição |

Os multiplicadores de densidade/voadores continuam respeitados. O alvo é um orçamento de **novas
inserções**, não um comando para apagar animais existentes. Toda ave selvagem carregada na região,
inclusive antiga ou nomeada, ocupa orçamento; aves domadas são preservadas e não entram nele.
Nenhum mundo do Rodrigo foi aberto, limpo ou migrado pelo teste. Ovos, comandos, spawn eggs e conteúdo
de eventos não são uma promessa de teto absoluto de quatro entidades em qualquer circunstância.
Populações permanentes antigas acima do alvo bloqueiam novas inserções; não são eliminadas automaticamente.

Terrestres e marinhos mantêm sua política de reposição atual. A geração completa de terreno, distribuição
de vegetação e comportamento de todas as espécies não foi redesenhada por esta correção.

## Testes executados

`population_regression.py` cria um servidor descartável de praia com dois clientes próximos. Coloca seis
aves nomeadas e imóveis como fixtures: três acima do limite vertical antigo, três além de 80 blocos
horizontalmente. Durante 46 segundos e várias rotações de câmera, todas precisam permanecer e nenhuma
ave nova pode aparecer. As fixtures são removidas apenas no mundo descartável; por mais 46 segundos,
a reposição deve funcionar e o total de novos voadores nunca pode ultrapassar quatro.

| Loader | Relatório | Resultado |
|---|---|---|
| Fabric | `build/population-regression/fabric-vvpjdt17/` | Passou: seis antigas preservadas sem reposição, população nova positiva e ≤4 |
| Forge | `build/population-regression/forge-0k9_njty/` | Passou: mesmos critérios, com dois clientes FML3 |

Os JSONs guardam cada contagem e hashes das fontes. Fontes da execução Forge conferidas integralmente
contra a entrega; no Fabric, somente dois Javadocs foram atualizados depois do teste, com reconstrução
dos comentários anteriores conferida pelos hashes originais (`post-test-comments.json`). O primeiro teste registrou o crash de Deinosuchus;
ele não foi tratado como sucesso. As repetições corrigidas completaram as duas fases.
Build Fabric/Forge com regressões passou em 38 s. Integridade (59 espécies, 4.341 JSONs, 1.848 chaves)
e orçamento (incluindo 1.000 escalas de céu de 400 ticks e cenários de região lotada) passaram.

```sh
python3 -B tools/validation/population_regression.py --loader fabric --eula-file /caminho/eula.txt
python3 -B tools/validation/population_regression.py --loader forge --eula-file /caminho/eula.txt
```

## Pendências de experiência

- Rever visualmente o céu em mundo Terrassic normal, praias, montanhas e costa, explorando chunks novos.
- Avaliar a sensação da densidade em sessões longas e com jogadores distantes; o teste cobriu dois próximos.
- Conferir montaria aérea e seguimento anfíbio com jogador no cliente gráfico.
- Mundo antigo já superpovoado deve ser observado separadamente: a nova política impede reposição,
  mas não apaga as aves permanentes que o mundo já tinha.
