# Testes da v0.3 no Mac

Nada da v0.3 foi compilado: a nuvem não alcança o maven do Fabric, do Forge e do Architectury. Esta lista é o que testar no Mac, na ordem. Se algo não compilar, mande o erro do Gradle que eu corrijo.

## 0. Compilar
- `./gradlew build` na raiz. Os pontos com mais risco de erro de compilação (APIs que não deu para conferir):
  - `FlyingDinosaur`: `PlayerRideableJumping` (métodos `onPlayerJump`, `canJump`, `handleStartJump`, `handleStopJump`), `checkFallDamage`, `calculateEntityAnimation`.
  - `SwimmingDinosaur`: `SmoothSwimmingMoveControl`, `damageSources().dryOut()`, `LevelAccessor.getSeaLevel()`.
  - `ModNetwork` (Architectury `NetworkManager`), `ModWorldgen` (`BiomeModifications.addFeature` e `LootEvent.MODIFY_LOOT_TABLE`).
  - `NotebookScreen` e `IntroScreen` (desenho com `GuiGraphics`).
- Depois `./gradlew :fabric:runClient` e, se der, `./gradlew :forge:runClient` (o Forge nunca foi testado).

## 1. Primeira entrada (mundo novo, Sobrevivência)
- [ ] A tela de abertura aparece com as falas em sequência e o título da era. Esc pula.
- [ ] Você recebe o Caderno de Campo. Numa segunda entrada no mesmo mundo, a abertura não aparece de novo.
- [ ] Teste com o jogo em português, inglês e espanhol: nenhum texto aparece como chave crua (`guide.terrassic...`).

## 2. Caderno de Campo
- [ ] Clique direito abre o Caderno com as 4 abas: Diário, Guia, Katarina, Relatório.
- [ ] Diário: 12 objetivos em 4 temas; 3 marcados como "em breve".
- [ ] Guia: lista de espécies; as nunca vistas aparecem como silhueta; o modelo 3D aparece e cabe no quadro (Brachiosaurus e Mosasaurus são os maiores).
- [ ] Chegar a menos de 16 blocos de um dinossauro muda o nível para "avistado".

## 3. Fósseis e Mesa de Pesquisa
- [ ] Rocha Fossilífera aparece no subsolo, dentro da pedra, como um minério (o `/locate` não acha minério; procure numa caverna, ou pegue o bloco no inventário criativo para testar).
- [ ] Pincel de Pelo: segurar clique direito na rocha por 3 s dá um fóssil, sem quebrar.
- [ ] Cinzel de Sílex: 1 s, às vezes dá só osso (fóssil rachado).
- [ ] Mesa de Pesquisa: clique com fóssil estuda (+1 ponto) e devolve um osso; com 3 pontos a espécie fica "estudada".
- [ ] Carvão de Esboço: segurar olhando para um dinossauro por 3 s dá um Esboço; levar à Mesa dá +2 pontos.
- [ ] Espécie estudada: +20% de dano contra ela e domar mais fácil.
- [ ] Páginas Soltas aparecem em baús de estruturas vanilla e viram páginas da Katarina na aba dela.

## 4. Pteranodonte
- [ ] Aparece em praias e costões, em grupos de 2 a 4. Voa por aí e pousa.
- [ ] Não leva dano de queda.
- [ ] Dar peixe na mão (bacalhau, salmão, peixe tropical) doma.
- [ ] Sela: clique com sela no domado; clique de mão vazia monta.
- [ ] No chão: anda como montaria normal. Segurar espaço mostra a barra de pulo; soltar decola.
- [ ] Ir para frente olhando bem para cima também decola.
- [ ] No ar: segurando W voa para onde você olha; espaço bate as asas e sobe; soltar W plana descendo devagar.
- [ ] Pousa ao tocar o chão e volta a andar. Shift desmonta.
- [ ] Animações: asas dobradas no chão; batendo no voo; abertas e paradas no planeio.
- [ ] Ovo: dois domados (macho e fêmea) com peixe põem ovo, que choca.
- [ ] Coisas para observar: o voo está rápido ou lento demais? Sobe fácil demais? A câmera treme? Me diga e eu ajusto os números (`FLIGHT_ACCEL`, `GLIDE_SINK` em `FlyingDinosaur`).

## 5. Mosassauro
- [ ] Aparece no oceano profundo (não congelado), sozinho e fundo, não na superfície. Para testar rápido: ovo gerador na água funda.
- [ ] Nada suave, sem ficar preso. Fica dentro da água.
- [ ] Ataca jogador nadando ou de barco; ignora quem está na praia.
- [ ] Caça peixes, lulas, golfinhos e tartarugas.
- [ ] Na terra, fica lento; depois de 60 s começa a secar e perder vida.
- [ ] Não dá para domar nem montar ainda (clique não faz nada).
- [ ] Some quando você vai longe (como golfinho), a não ser que tenha nome (etiqueta).
- [ ] Animações: cauda ondulando ao nadar; mordida com a mandíbula abrindo para baixo.
- [ ] Drop: bacalhau, couro, osso e às vezes Dente de Mosassauro.

## 6. Maiassaura
- [ ] Aparece em planícies e savanas, em bandos de 3 a 6.
- [ ] Doma com trigo, samambaia ou frutas silvestres; aceita sela e monta.
- [ ] Filhotes de qualquer espécie a até 10 blocos de uma adulta crescem 2x mais rápido, com partículas verdes a cada 5 s.
- [ ] Animações de pastar e de chamado (cabeça para cima, boca aberta).

## 7. Pulo e sela (todas as montarias)
- [ ] Montado, segurar espaço mostra a barra de pulo; soltar pula (mais alto quanto mais carregado). Gallimimus pula mais alto, Tricerátops e Tiranossauro menos, Braquiossauro não pula.
- [ ] Clique com tesoura numa montaria selada (sem ninguém em cima) tira a sela e devolve o item.

## 8. Lente de Âmbar
- [ ] Receita: Âmbar Bruto em cima, osso + painel de vidro + osso embaixo.
- [ ] Segurar clique direito dá o zoom e a moldura da luneta vanilla (primeira pessoa), com o mouse mais lento.
- [ ] Manter um dinossauro no centro por 2 s, a até 64 blocos, registra ele como "avistado" no Guia. Se já era conhecido, mostra o nome e a distância.
- [ ] Este é o primeiro mixin do mod: se o jogo não abrir no Fabric ou no Forge, o erro vai citar `terrassic.mixins.json` ou `PlayerMixin`.

## 8b. Frasco de Argila
- [ ] Receita: 3 tijolos em V. Frasco no abeto ou na árvore da selva vira Frasco com Resina e deixa o tronco descascado (cada tronco dá resina uma vez). Em outras árvores aparece o aviso.
- [ ] Frasco com Resina na mesa de trabalho vira Âmbar Bruto e o frasco volta vazio.
- [ ] A Lente de Âmbar agora pede Âmbar Bruto (não mais favo de mel).
- [ ] Com um frasco vazio no inventário, derrotar um dinossauro enche o frasco com "Amostra de Sangue de <espécie>". Na Mesa de Pesquisa dá +2 pontos e devolve o frasco.

## 9. Configuração de spawn
- [ ] Depois da primeira abertura existe `config/terrassic.json` com `spawn_multiplier` e todas as espécies.
- [ ] `"enabled": false` numa espécie (reiniciando o jogo) faz ela parar de aparecer em mundo novo; `"spawn_multiplier": 0` desliga todas.

## 10. Coisas que já existiam (regressão)
- [ ] As 12 espécies da v0.2 continuam aparecendo, domando e montando como antes.
- [ ] Blocos primitivos (sapê, pedra seca etc.) continuam com textura e receita.
