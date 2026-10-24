# Testes da v0.9 "O Fim" (só uma pessoa consegue fazer no jogo)

Detalhes de cada peça em `docs/SALTO.md`. Para testar rápido, num mundo criativo/com comandos:
`/terrassic modo livre` libera ritual e salto sem fragmentos; `/terrassic modo normal` volta ao normal.

## 0. Carregar
1. `./gradlew :fabric:runClient` (e `:forge:runClient`) sobe sem erro; no log nenhum aviso de mixin
   `LevelRendererMixin`, `ClientLevelMixin` ou `FogRendererMixin`.
2. Aba Ciência do criativo: o Altar do Salto aparece com nome nos 3 idiomas; a receita aparece no livro de receitas.

## 1. Altar e anel
1. Pôr o Altar sozinho e usar: mensagem de anel incompleto com "faltam 8 postes" e faíscas laranja nos 8 lugares.
2. Pôr menires (ou pedra empilhada) nas 4 pontas a 3 blocos e muro de ossário, pilha de ossos ou troféu de crânio
   nas diagonais (2, 2): o âmbar passa de brasa fraca a respirar (estado 1) em até 1 s. Tirar um poste: volta ao 0.
3. Terreno irregular: um poste 1 bloco abaixo ou 2 acima do Altar ainda conta.
4. Agachado com um bloco qualquer na mão, clicar no Altar: o bloco é colocado normalmente.
5. Usar com o anel completo e sem fragmentos (modo normal): "0 de 4 fragmentos (modo Normal)" e a dica do Diário.

## 2. Modos e comandos
1. `/terrassic modo` mostra o modo; `/terrassic modo rapido` e `/terrassic modo livre` mudam; sair e voltar ao mundo:
   o modo continua. Nome errado (`/terrassic modo x`) dá erro amigável.
2. Mundo novo depois de pôr `"progression_mode": "livre"` em `config/terrassic-world.json`: começa no modo Livre.
3. Jogador sem permissão não vê os comandos.
4. `/terrassic capitulo 1` no mundo normal: "você já está no Capítulo 1"; no Nether: leva ao spawn do mundo normal.
   `/terrassic capitulo 2`: "ainda não está no jogo".

## 3. Ritual e Tirano (modo livre para ir direto)
1. Agachado com âmbar bruto, usar o Altar: gasta 1 âmbar (sobrevivência), mensagem do ritual, som de portal, conquista
   "Estrelas que caem". O âmbar do Altar solta fogo e lava.
2. Céu e névoa ficam vermelhos aos poucos (dia e noite); chuva de estrelas cadentes; meteoros com rastro de fogo
   caindo em volta, visíveis de longe; estouram sem quebrar blocos, ferem e empurram quem está perto.
3. Deixar uma pilha de itens no chão perto de onde caem meteoros: os itens não somem.
4. Depois de 30 s: o Tirano cai num clarão, ruge, aparece a barra de chefe amarela "Tirano da Fenda"; ele tem as
   rachaduras de âmbar brilhando e é bem maior que um T. rex normal.
5. Rugido: perto dele, você é empurrado e fica lento. Meteoros e fogo não o ferem.
6. Abaixo da metade: barra vermelha, céu escurece, ele fica mais rápido, chama raptores com rachaduras e manda meteoros
   em você com um anel de faíscas no chão antes.
7. Fugir para mais de 48 blocos do Altar: ele desiste e volta. Ficar longe (mais de 96 do Altar e 64 dele) por 30 s:
   ele volta para a Fenda com mensagem; dá para começar de novo.
8. Vencer: conquista "Tirano da Fenda", mensagem de que o Altar abriu, meteoros param em 10 s, céu volta ao normal,
   carcaça de T. rex grande com âmbar, dentes e carne nobre; os raptores somem. O Altar fica no estado aberto.
9. `/terrassic ritual parar` no meio da luta: o Tirano some e o céu volta.
10. Quebrar o Altar no meio do ritual: o ritual acaba e o Tirano volta para a Fenda.
11. Sair do mundo no meio da luta e voltar: o ritual continua (ou acaba em até 30 s se ninguém estiver perto), sem
    sobrar Tirano solto.
12. Modo normal com 4 fragmentos: mesmo fluxo; depois de vencer, usar o Altar mostra a dica de saltar.

## 4. O Salto
1. Altar aberto para você, agachado com a mão vazia (com escudo na outra mão também): clarão branco-dourado de ~5 s,
   som de portal e trovão; outro jogador dentro do anel também vê o clarão; depois, a mensagem de que o Capítulo 2 chega
   numa próxima versão. Ninguém sai do lugar, nada se perde.
2. Segurar o botão no Altar: não repete o clarão.
3. Modo normal com 2 ou 3 fragmentos: agachado com âmbar, primeira vez pede confirmação; segunda em 5 s faz o clarão
   âmbar do Salto Instável, e o âmbar não é gasto (ainda não há destino).

## 5. Estrelas cadentes e criaturas da Fenda
1. À noite sem chuva, olhar o céu por alguns minutos: riscos de luz de vez em quando; com mais fragmentos, mais
   seguidos. Somem na chuva, com cegueira, dentro da lava ou da neve fofa.
2. `"shooting_stars": false` e `"ritual_sky": false` em `config/terrassic-client.json` desligam cada efeito.
3. Tempestade da Fenda (`/terrassic tempestade iniciar`): os vazamentos têm as rachaduras de âmbar pulsando (em vez do
   contorno brilhante). Matar um: conquista "Anomalia".
4. As rachaduras em espécies diferentes (grande, pequena, voadora) parecem rachaduras e não um borrão; ficam
   visíveis no escuro.
5. Forge: os mesmos testes 3.1-3.8 e 4.1.
