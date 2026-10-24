# Bandos, manadas e matilhas (v0.6, fase 67)

Os grupos já nasciam juntos (tamanho de grupo por espécie em `WORLD`, `tools/javagen/gen_species.py`), mas se
espalhavam ao vagar. Agora ficam juntos, fogem juntos e caçam juntos.

| Regra | Como |
|---|---|
| Coesão | `FollowHerdGoal` (herbívoros e predadores, prioridade 8/7): um adulto selvagem a mais de 7 blocos do adulto selvagem mais próximo da sua espécie anda até ficar a 4. Sem líder nem registro: cada um guarda um vizinho perto e a manada deriva junta enquanto vagueia. Procura a 24 blocos; não vale domado, filhote (segue os pais), dormindo, montado ou com alvo. |
| Debandada | Um herbívoro que foge (não briga) e é ferido faz a manada toda correr: os outros da espécie a 16 blocos tomam o agressor como quem os feriu (dispara o `PanicGoal` deles) e acordam. Os que brigam já se defendiam juntos (`HurtByTargetGoal.setAlertOthers`). |
| Matilha | `pack=True` (Velociraptor, Dilophosaurus, Baurusuchus, Compsognathus; o Velociraptor já tinha a versão própria, agora é a regra geral em `PredatorDinosaur`): um caçador selvagem com alvo traz, a cada segundo, os caçadores selvagens ociosos da espécie a 16 blocos para o mesmo alvo (se puderem caçar: acordados, com fome, não saciados). |

## O que falta

- Tamanhos de grupo da HISTORIA (hadrossauros 8-20, raptores 3-5) ficam para o balanço de spawn da v0.8, com o tipo de mundo.
- Pterossauros e répteis marinhos não entram (IA própria de voo e nado).
- Barra do bando no HUD (v0.8).
