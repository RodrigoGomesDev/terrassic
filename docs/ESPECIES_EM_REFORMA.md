# Espécies em reforma (v1.5)

Decisão do Rodrigo (02/11/2026): na 1.5, só os dinos refeitos um a um aparecem no mundo. As espécies que ainda têm o
modelo antigo ficam desligadas do mesmo jeito que os jurássicos desde a v0.10: continuam registradas, mundos salvos
mantêm os bichos que já têm, mas elas não nascem, não aparecem nas abas do criativo, no Guia de Campo, nas fissuras da
Fenda nem nos fósseis.

- Lista dos refeitos: `Eras.REMADE` em `common/src/main/java/com/terrassic/config/Eras.java`. Cada espécie refeita e
  aprovada entra ali na versão em que ficar pronta.
- Hoje: T. rex, Carnotauro, Giganotossauro, Protoceratops, Tricerátops, Galimimo (regra de estudo próprio) e Spinosaurus,
  Velociraptor, Pteranodon (refeitos antes da regra; passam pela revisão da regra universal antes da 1.5; quem não passar
  sai da lista). O Tricerátops e o Galimimo são os dois primeiros dos seis do pacote 1.5 (depois: Paquicefalossauro,
  Parassaurolofo, Anquilossauro, Mosassauro).
- Para ligar todas de volta: `"especies_antigas": true` em `config/terrassic-world.json` e reiniciar o jogo ou o servidor.
  O valor é lido uma vez, no início.
- Efeito no tipo de mundo Terrassic (desligado por padrão): a fauna de caça do Cretáceo também fica desligada; o mundo
  padrão do Minecraft continua com os animais vanilla.
