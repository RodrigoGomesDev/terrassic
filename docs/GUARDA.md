# Guarda noturno

O **Troodon** (fase 78) é a primeira espécie com a flag `night_guard` do gerador (`tools/javagen/gen_species.py`).

## Regra

- **Quando vale:** o animal é domado, adulto, acordado e é noite no mundo (`Level.isNight()`). O Troodon é noturno
  (`nocturnal=True`): dorme de dia pelo `DinoSleepGoal` e acorda ao anoitecer, então o turno de guarda coincide
  com as horas em que está acordado.
- **Ataque:** de pé (não sentado), vai atrás de qualquer monstro hostil (`Monster`) num raio de 10 blocos, exceto
  creepers, como o lobo vanilla. Prioridade 4 no `targetSelector`, abaixo de defender o dono e de revidar.
- **Visão noturna:** a cada 2 s, se o dono está a menos de 12 blocos, recebe Visão Noturna ambiente por 15 s
  (sem partículas, com ícone). Sentado também vale: um Troodon "sentado" na porta é um posto de guarda e uma
  lanterna viva.

## Gerador

`night_guard=True` emite `guardsNow()`, o `NearestAttackableTargetGoal<Monster>` em `addExtraGoals()` e um
`customServerAiStep()` para o efeito. Por ter o `customServerAiStep`, é incompatível com `roar`, `display` e
`scoop` na mesma espécie (o gerador aborta com assert).

## Testes humanos

- Domar um Troodon pelo ovo roubado, esperar a noite perto de zumbis: ele deve atacar; não deve atacar creeper.
- Ficar a menos de 12 blocos dele à noite: o ícone de Visão Noturna aparece e se mantém sem piscar.
- De dia ele dorme e nada disso acontece.
