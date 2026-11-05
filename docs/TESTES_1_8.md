# Testes da 1.8: Estiracossauro, Deinossuco e Elasmossauro

Pedido do Rodrigo (05/11/2026), antes de fechar a 1.8.0: "testar todos esses dinos pra ver se realmente tá tudo funcional,
tudo foi mapeado, sem parecer tanto IA, um carinho em cada dino".

## Como rodar

- Mapeamento: um script confere, para cada espécie, textos (pt, en, es), ovo de criativo, ovo-bloco e ninho, sela e receita,
  couro e loot, sons, spawn nos biomas, Guia e Bestiário, e se toda animação que o código pede existe no `animation.json`.
- Comportamento: `client/dev/BehaviorTest` (`TERRASSIC_BEHAVIOR_TEST=1`, `TERRASSIC_BEHAVIOR_SPECIES=...` opcional) num
  mundo plano (`--quickPlaySingleplayer partes`). Monta uma arena para cada espécie (campo; rio com margem de areia;
  piscina funda aberta para o céu), deixa os bichos viverem e registra toda animação que eles disparam sozinhos
  (`DinosaurEntity.triggerLog`, só em desenvolvimento) e todo movimento desenhado no cliente, com foto da primeira vez de
  cada um. Depois doma com a comida na mão, põe a sela própria, monta (foto em terceira pessoa), faz um casal domado
  procriar e espera o ovo chocar (ou o filhote nascer vivo). Relatório em `run/terrassic_behavior_report.txt`.
- Partes de acerto: `PartsShowcase` com `still,moving` (nadadores medidos numa piscina funda).

## Resultado (cliente Fabric 1.20.1)

| | Estiracossauro | Deinossuco | Elasmossauro |
|---|---|---|---|
| Mapeamento completo | sim | sim | sim |
| Comportamentos próprios vistos acontecendo sozinhos | raspar o chão, investida, chifrada, gancho de lado, exibir a coroa, disputa entre machos, esfregar o chifre, sacudir a coroa, chamado, empurrão de gola | boiar, bote, giro da morte, varrida de cauda, tomar sol, berro, tapa na água, filhote chamando | respirar, mergulhar, engolir pedras, mãe e filhote |
| Doma | na mão, 27 samambaias | adulto não aceita comida na mão (pelo desenho: ovo, filhote ou nocaute) | na mão, 128 peixes |
| Sela própria e montaria | sim | não monta (pelo desenho) | sim |
| Procriação | ovo-bloco, choca | ovo-bloco na margem, choca | filhote nasce vivo |
| Partes de acerto (miras parado) | 324, 0 falhas | 714, 0 falhas | 720, 0 falhas |

## Bugs achados e corrigidos

- **Deinossuco caçava outros Deinossucos.** A regra de presa era `e.isInWaterOrBubble() || e.getBbWidth() < 1.6F && !(e
  instanceof Deinosuchus)`: pela precedência, qualquer coisa na água contava, os da própria espécie também. Agora o
  "não é Deinossuco" vale para os dois casos.
- **Bando que brigou não podia mais ser domado.** O alarme do bando põe o alvo nos outros sem um objetivo de alvo deles
  rodando, e o Minecraft não limpa um alvo morto nesse caso; com alvo, `canBeTamedNow` recusa a comida para sempre. Agora
  `DinosaurEntity` larga todo alvo morto ou removido.
- **Bichos grandes quase não procriavam.** O `BreedGoal` do vanilla só acasala com os centros a menos de 3 blocos, e dois
  bichos de 2,6 blocos de largura empurrando um ao outro ficavam a 3,4. Novo `ai/DinoBreedGoal`: alcance de 3 blocos mais
  a largura do bicho, e procura o par por distância (o filtro do vanilla diminui o alcance pela "visibilidade" do outro e
  não achava um par a 3 blocos). Vale para todas as espécies.
- **Casal que acasalava na água perdia o ovo.** O lugar do ovo era procurado só a 3 blocos; na água não havia, e o ovo
  caía como item. Agora procura até 8 blocos e põe na margem.
- Filhotes de Estiracossauro se empurravam a cada ~15 s; agora uma vez por minuto ou dois.

## Acabamento ("sem cara de IA")

- Estiracossauro: escamas mais calmas (o contorno só em dois terços delas, para não parecer barro rachado), manchas
  escuras grandes e suaves no dorso; Manta de Corrida refeita (abas descendo pelos flancos, barra de apoio baixa, alças com
  botão de osso fora do corpo).
- Deinossuco: placas do dorso de tamanhos e alturas diferentes, fileira de fora desencontrada, uma faltando de vez em
  quando, a borda da frente de cada placa iluminada e a cova marcada; faixas douradas mais largas e quebradas, uma ou
  outra faltando, cruzando também a cauda por cima.
- Elasmossauro: pintas no espaço do modelo (passam de uma peça à outra), em nuvens soltas, em três tamanhos, mais raras
  no pescoço e nos flancos; borda de ataque mais grossa nas nadadeiras; pescoço com degraus menores.
- Cores conferidas de novo depois do acabamento: nenhuma colisão (o mais perto: Parassaurolofo 11,3; T. rex 10,8;
  Tilossauro 11,3).

## O que não foi testado

- Clientes Forge e NeoForge (só compilados); montar e andar montado com o teclado (o teste monta e fotografa, não dirige).
- Limite conhecido: no nado do Elasmossauro a ponta das nadadeiras sai das caixas até ~0,9 m na remada.
