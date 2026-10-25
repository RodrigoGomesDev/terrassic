# Regressão de nocaute em servidor dedicado

```sh
python3 -B tools/validation/knockout_regression.py --loader fabric --eula-file /caminho/eula.txt
python3 -B tools/validation/knockout_regression.py --loader forge --eula-file /caminho/eula.txt
```

Requer JDK 21, dependências no cache e um `eula.txt` já aceito, fornecido pelo operador. O servidor fica vinculado
somente a localhost e usa um mundo plano descartável em `build/knockout-regression/`; não abre mundos do jogador.
O cliente de protocolo 763 conecta como `TerraKO`; o Forge negocia FML3. Sem contas ou servidores externos.

## O que é exercitado

Fixtures nomeadas de Leptoceratops têm tamanho 1 e atributos conhecidos. Comandos de operador preparam os animais
inconscientes e selecionam o item da mão. As interações de erva sonífera e trigo usam pacotes reais do jogador
para os IDs de entidade recebidos pela conexão, passando pelo handler normal de clique direito do servidor.

O roteiro verifica 18 condições, com marcadores de resultado nos logs:

- eficiência reduzida antes da primeira alimentação é serializada e preservada após reiniciar;
- dano recusado por invulnerabilidade não tira eficiência, e ferimento aceito continua tirando;
- acordar reduz o progresso pela metade e remove o estado de inconsciência;
- erva sonífera pela mão aumenta torpor; trigo avança a domesticação e registra o UUID do jogador;
- completar a domesticação atribui o dono e aplica o bônus de vida correspondente à eficiência;
- dono, progresso parcial, eficiência e bônus de vida sobrevivem ao reinício, sem duplicar o modificador;
- um animal parcialmente domesticado antes do reinício pode terminar o processo depois dele.

## Falhas reproduzidas e correções

Antes da correção, `fabric-rvo_50wp` registrou três verificações falhas: ausência da eficiência antes de qualquer
comida, penalidade por dano rejeitado e perda da eficiência do animal sem alimentação após reinício. As outras
verificações passaram. Logs em `build/knockout-regression/fabric-rvo_50wp/`.

`DinosaurEntity` passou a salvar `TameEffectiveness` enquanto o animal está inconsciente, mesmo com progresso
zero. A penalidade passou a ocorrer depois de `super.hurt`, somente se o dano for aceito e positivo. Os valores
de torpor, alimento, eficiência por ferimento, meta de domesticação e bônus não foram rebalanceados.

A primeira repetição corrigida (`fabric-gm0r3hqp`) passou as 17 verificações então presentes. Depois foi acrescentada
a verificação do ferimento aceito, totalizando 18. O roteiro completo passou nos dois loaders:

| Loader | Diretório em `build/knockout-regression/` | Resultado |
|---|---|---|
| Fabric | `fabric-vfs_4m2n` | 18/18, incluindo reinício |
| Forge | `forge-2du_0p05` | 18/18, incluindo reinício |

O SHA-256 da classe testada em ambas as execuções foi comparado com a fonte corrigida antes do commit: iguais.
Build completa dos dois loaders com regressões de pesquisa passou depois desses testes em 49 s.

## Reprodução e limites

Cada execução arquiva os inputs de uma revisão em `source.tar` e compila fora do checkout compartilhado.
Para testar uma correção ainda não commitada, sobrepõe apenas `DinosaurEntity.java`, salvando a cópia exata em
`DinosaurEntity.tested.java` e seu SHA-256 no `results.json`. Assim uma build de outra frente não troca as classes
do servidor durante o teste. O JSON também lista os resultados de cada condição; erros encerram com código não zero.

As fixtures começam inconscientes por NBT: este roteiro não valida o disparo da zarabatana, a colisão do dardo,
o preenchimento inicial do torpor, a animação ou a leitura das barras no cliente completo. O roteiro complementar
`TESTES_DARDOS.md` cobre disparos terrestres e manutenção/domesticação aquática após reinício. Combate aquático
desde um animal acordado, animações, barras e diferentes espécies continuam na fila funcional. Não confundir
protocolo conectado com revisão visual ou uma partida de sobrevivência.
