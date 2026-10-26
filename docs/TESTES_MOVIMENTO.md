# Fonte, voo e locomoção — 26/10/2026

Correções pedidas pelo Rodrigo: letras deformadas em botões claros, aves girando/paradas e grupos sobrepostos.

- Botões âmbar e abas de papel desenham texto escuro sem sombra; fonte e paleta preservadas.
  A comparação com os glifos Sedimento reproduziu o defeito e sua remoção (`build/movement-visual/fonte-comparacao.png`).
- Voo selvagem mantém avanço, aceleração limitada e curvas de até 3 graus/tick, com separação e formação móvel.
  Um adulto selvagem que já esteja no ar retoma o voo imediatamente, incluindo em mundos antigos.
- Fim do voo/anoitecer conduz a planeio descendente. Torpor libera a gravidade mesmo quando a imobilização
  impede atualizações das metas de IA. A falha foi reproduzida em servidor antes da correção.
- Controle terrestre preserva navegação e saltos vanilla, com giro e aceleração graduais; entrada nula continua
  parada. Manadas seguem relações em uma direção e guardam distância proporcional à hitbox.
- Os pontos de inserção dos grupos foram espaçados, preservando o orçamento numérico existente.

## Evidências

`./gradlew build --offline --no-daemon`: passou, incluindo pesquisa/dados e 10.000 passos do controlador de voo
de produção, com alvos próximos, reversões, velocidade limitada e passagem pelo ângulo -180/180.
Integridade: 59 espécies, 4.341 JSONs, 1.848 chaves. Orçamento: 1.000 escalas e 10.000 cenários passaram.

| Servidor descartável | Velocidade horizontal mínima no voo | Distância final da manada terrestre | Transições |
|---|---:|---:|---|
| Fabric `build/movement-regression/fabric-w3pge1hc/` | 0,415 blocos/tick | 7,65 blocos | Planeio ao anoitecer e gravidade após torpor passaram |
| Forge `build/movement-regression/forge-omx3bq8v/` | 0,418 blocos/tick | 8,89 blocos | Planeio ao anoitecer e gravidade após torpor passaram |

Quatro aves começam próximas por fixture para exercitar o afastamento. Houve proximidade transitória
(mínimo 2,06 blocos no Fabric e 1,48 no Forge); o teste não afirma ausência absoluta de aproximações.
Os relatórios guardam 30 amostras de posição, velocidade e rotação por ave e hashes das fontes.
Testes anteriores são diagnósticos, incluindo a falha de gravidade e uma falha do leitor de NBT: Minecraft
omite `NoGravity` quando falso, que o harness agora interpreta corretamente.

## Reprodução e limites

```sh
python3 -B tools/validation/movement_regression.py --loader fabric --eula-file /caminho/eula.txt
python3 -B tools/validation/movement_regression.py --loader forge --eula-file /caminho/eula.txt
```

Mundo descartável, localhost, cliente de protocolo, comandos para fixtures. Não mede estética de animações,
montaria em voo, obstáculos complexos nem população natural. Revisão visual no cliente continua necessária.
O relato posterior de mais de 40 aves abriu uma auditoria própria de população: estes testes não a validam.
