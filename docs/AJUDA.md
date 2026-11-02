# Guia de Bolso do Terrassic (livro de ajuda)

v1.1.2, 31/10/2026. Rodrigo pediu "um livrinho de ajuda", aprovou os tópicos e o visual de livro do Minecraft no mesmo dia
(prévia: https://claude.ai/artifact/7jPEtKqxLkDr6jf9qdUgmF).

## Como o jogador recebe
- Todo jogador ganha **um** Guia ao entrar num mundo pela primeira vez: conquista oculta `terrassic:pocket_guide`
  (gatilho `minecraft:tick`) com a loot table `terrassic:gameplay/pocket_guide`. Não repete ao morrer nem ao relogar.
- Receita sem forma: livro + sílex. Pilha de 1, aba principal do mod.
- Botão direito abre o livro (só no cliente; `item/PocketGuideItem` -> `client/PocketGuideScreen`).

## O livro
- Arte própria (capa de couro costurada, páginas de pergaminho, setas) desenhada por código em
  `tools/spritegen/pocket_guide.py` -> `textures/gui/pocket_guide.png` e o ícone `textures/item/pocket_guide.png`.
- Fonte do jogo, ícones de item, receitas numa grade 3x3 com o resultado (ingredientes com várias opções trocam a cada
  segundo; passar o mouse mostra o nome do item).
- Primeiro o índice (clicar num tópico pula para ele), depois cada tópico começando numa página nova. O texto é diagramado
  quando a tela abre, então cabe em qualquer idioma e escala de interface.
- Virar página: setas do livro, setas do teclado, Page Up/Down e a roda do mouse. Reabre na última página lida na sessão.
- `%key:use%`, `%key:attack%`, `%key:jump%`, `%key:sneak%`, `%key:inventory%`, `%key:dino_screen%`, `%key:descend%` e `%key:whistle%` (1.5)
  viram a tecla que o jogador configurou, entre colchetes.

## Tópicos (13)
Começo, Armas, Zarabatana, Boleadeira, Nocaute, Ovos e filhotes, Montaria, Ordens, Níveis, Fome e sono, Carga e ombro,
Construção, Regras do mundo.

## Onde mexer
- Textos, ícones, receitas mostradas e ordem: `TOPICS` em `tools/javagen/gen_pocket_guide.py` (pt-BR, inglês, espanhol;
  as variantes do espanhol copiam es_es). Depois `python3 -B tools/javagen/gen_resources.py`.
- O gerador falha se um tópico citar uma receita que não existe.
- Textos curtos: cada parágrafo é separado por `\n`, e o livro pula de página sozinho.
- Mudou uma mecânica do jogo? Atualize o tópico dela aqui.
