# Regras do mundo e ecossistema (estilo ARK)

Pedido do Rodrigo (24/10/2026): controlar a geração e as regras do jogo como na tela "Regras do ARK", e a geração
padrão bem mais cheia: voadores voando de verdade pelo céu, muitos animais no mar, rebanhos nas planícies.

## Onde fica

- **Tela "Regras do Terrassic"**: botão no canto superior esquerdo do menu de pausa, ou `/terrassic regras`
  (também `rules` e `reglas`). No Forge, o botão "Config" da lista de mods abre as regras padrão.
- Três abas: **Geral**, **Criação** e **Ecossistema**. Cada regra tem nome, caixa de número e controle deslizante;
  passar o mouse no nome explica a regra. Um tracinho sob o trilho marca o valor padrão e um ponto depois do
  nome indica que a regra foi mudada.
- **Por mundo**: os valores ficam salvos no mundo (`data/terrassic_rules.dat`). Só um operador, ou o dono do mundo
  em um jogador (mesmo sem comandos), pode salvar; os outros jogadores veem a tela só para leitura.
- **Padrão para mundos novos**: o objeto `"rules"` de `config/terrassic-world.json`. Um mundo novo (ou criado antes
  das regras existirem) começa com esses valores. O resto do arquivo não é tocado.
- Fonte única: a tabela `RULES` de `tools/javagen/gen_rules.py` (chave, padrão, faixa, passo, aba e textos nos 3
  idiomas). Ela gera `config/Rule.java` e as traduções (via `gen_resources.py`). Regra nova: linha na tabela, rodar
  `gen_resources.py` e usar `Rules.of(level).get(Rule.X)` no código.

## As regras

1,0 é o jogo como foi desenhado. Todas mudam na hora, sem reiniciar.

| Aba | Regra | Padrão | Faixa | O que faz |
|---|---|---|---|---|
| Geral | Nível de dificuldade | 0,5 | 0 a 1 | Força das criaturas selvagens: 0 = metade da vida e do dano, 0,5 = normal, 1 = 1,5x |
| Geral | Dano dos dinos | 1,0 | 0,1 a 5 | Dano que as criaturas causam (selvagens e domesticadas) |
| Geral | Dano do jogador | 1,0 | 0,1 a 5 | Dano que os jogadores causam nas criaturas |
| Geral | Dano de estruturas | 1,0 | 0 a 5 | Chance de as investidas quebrarem os blocos pelo caminho (0 = nunca) |
| Geral | Resistência do jogador | 1,0 | 0,1 a 5 | Divide o dano que o jogador recebe das criaturas |
| Geral | Resistência dos dinos | 1,0 | 0,1 a 5 | Divide o dano que as criaturas recebem |
| Geral | Resistência de estruturas | 1,0 | 0,1 a 5 | Divide o dano de estruturas |
| Geral | Multiplicador de XP | 1,0 | 0 a 10 | XP de abater criaturas e de criar filhotes |
| Geral | Velocidade de domesticação | 1,0 | 0,1 a 10 | Chance de cada mordida domesticar |
| Criação | Velocidade de chocagem | 1,0 | 0,1 a 10 | Quão rápido os ovos racham e chocam (vale para os chocadores também) |
| Criação | Velocidade de crescimento | 1,0 | 0,1 a 20 | Quão rápido os filhotes viram adultos |
| Criação | Intervalo de acasalamento | 1,0 | 0,1 a 5 | Espera depois de pôr ovos (padrão 5 min) |
| Criação | Consumo de comida | 1,0 | 0 a 5 | Velocidade da fome (0 = nunca sentem fome) |
| Criação | Ninhos selvagens | 1,0 | 0 a 5 | Chance de bandos nascerem com ninho e de selvagens acasalarem sozinhos |
| Criação | Frequência de migração | 1,0 | 0 a 5 | Quão seguido as manadas migram (0 = não migram) |
| Ecossistema | Densidade de vida | 1,0 | 0 a 5 | Multiplica todos os alvos do ecossistema (0 = desliga o spawner novo) |
| Ecossistema | Terrestres | 1,0 | 0 a 5 | Alvo de terrestres ao redor de cada jogador (18 na densidade 1) |
| Ecossistema | Voadores | 1,0 | 0 a 5 | Alvo de voadores no céu (8) |
| Ecossistema | Marinhos | 1,0 | 0 a 5 | Alvo de criaturas no mar (12) |
| Ecossistema | Filhotes nos bandos | 1,0 | 0 a 5 | Parte dos bandos que é filhote (18% dos membros depois do primeiro) |
| Ecossistema | Limite de criaturas | 400 | 50 a 2000 | Máximo de selvagens carregados no mundo (desempenho) |

Detalhes de como cada uma age no código:

- **Dano e resistência** (`Rules.damageTaken` / `Rules.damageDealt`): criatura atingida = dano x (dano do
  jogador, ou dano dos dinos x força do atacante selvagem) / resistência dos dinos / força dela se for selvagem.
  Criatura batendo em jogador ou mob vanilla = dano dos dinos x força selvagem / resistência do jogador (só para
  jogador). O bônus de +20% de "estudado" continua por cima.
- **Força selvagem** = 0,5 + nível de dificuldade (0,5 a 1,5); domesticados não têm.
- **XP**: agora vale o `xp` de cada espécie da tabela do gerador (o `Animal` vanilla ignorava e dava 1 a 3);
  filhotes dão 1 a 3. Vezes o multiplicador.
- **Estruturas**: hoje só as investidas (Styracosaurus, Pachyrhinosaurus, Argentinosaurus etc.) quebram blocos;
  a regra fica pronta para os ataques a construções que vierem depois.

## O ecossistema (spawner novo)

`world/EcoSpawner`: a cada 2 segundos, para cada jogador, conta as criaturas selvagens num raio de 80 blocos em
três tipos e, onde faltar, põe um grupo novo entre 36 e 80 blocos de distância:

- **Espécies do próprio bioma**: usa a lista de spawn do bioma (tabela WORLD do `gen_species.py`, biomas do
  Cretáceo da v0.8, `config/terrassic.json`), com os mesmos pesos e tamanhos de grupo. Cada bioma mantém sua fauna.
- **Terra**: manada, matilha ou casal na superfície, com filhotes de idades (e tamanhos) diferentes.
- **Céu**: bando já voando, 16 a 40 blocos acima do chão, todos na mesma direção (só de dia).
- **Mar**: grupo em água aberta e funda o bastante, entre 6 e 40 blocos abaixo do nível do mar.
- Respeita a regra de jogo `doMobSpawning` e o limite de criaturas.
- As criaturas postas por ele são **errantes** (salvo "Roamer"): como os dinos selvagens do ARK, somem quando
  todos os jogadores estão a mais de 96 blocos, a não ser que sejam domesticadas ou ganhem nome. Assim a população
  segue os jogadores em vez de se acumular. Os animais que nascem com o mundo continuam permanentes, como as vacas.
  Os marinhos selvagens agora só somem a mais de 64 blocos (antes sumiam a qualquer distância além de 32).
- Errantes nascem com ninho em 1 de 20 bandos (os do mundo, 1 de 5), vezes a regra de ninhos.

## Voadores no céu (SoarGoal)

- Selvagens adultos voam alto em **bandos**: o de menor id num raio de 32 blocos lidera, escolhendo pontos 24 a 56
  blocos à frente, 14 a 40 acima do chão, virando aos poucos; os outros mantêm cada um seu lugar na formação.
- Um voo dura de 1 a 3 minutos; depois planam até o chão e descansam de 30 s a 1,5 min. Nunca descem sobre o mar
  aberto (continuam voando até ter terra embaixo). Voltam para perto de onde decolaram quando se afastam 72 blocos.
- Voam de dia (de noite os noturnos); de noite pousam. Não puxam chunks não carregados: na borda, dão a volta.

## Integração com a v0.8 (Mundo Terrassic)

- As regras padrão moram no mesmo `config/terrassic-world.json` da v0.8 (objeto `"rules"`), sem mexer nas outras
  chaves (tempestades da Fenda etc.).
- O spawner lê a lista de spawn de qualquer bioma, então os 11 biomas do Cretáceo funcionam sem código extra.

## Testes que só uma pessoa pode fazer no jogo

1. Menu de pausa: o botão "Regras do Terrassic" aparece no canto superior esquerdo e abre a tela; as três abas,
   a rolagem com a roda do mouse, o texto de ajuda ao passar o mouse nos nomes, digitar valores com vírgula ou
   ponto, arrastar o controle, "Restaurar padrão", "Salvar" e "Cancelar".
2. Salvar, sair e voltar ao mundo: os valores continuam. Criar um mundo novo: começa com o padrão do arquivo.
3. Em servidor com um jogador não operador: a tela abre só para leitura e o servidor recusa mudanças.
4. Forge: lista de mods > Terrassic > Config abre as regras padrão e grava em `config/terrassic-world.json`.
5. Densidade 1: andar por planícies, praias e mar e ver rebanhos, bandos de pterossauros voando alto em formação
   e grupos no mar. Densidade 3 a 5: bem mais cheio, sem travar (conferir o TPS com F3).
6. Voadores: ver o bando circular, descer para descansar depois de alguns minutos e decolar de novo; ao anoitecer,
   pousar. Conferir se não entram em terreno nem ficam presos na água.
7. Dificuldade 1 e dano dos dinos 3: um T. rex selvagem bate bem mais forte; resistência do jogador 3: bem menos.
8. Velocidade de domesticação 10: domestica com uma ou duas mordidas. Chocagem 10: ovo choca em segundos.
   Crescimento 20: filhote cresce em pouco mais de um minuto. Consumo de comida 0: a fome não cai.
9. Ninhos 0: nenhum bando novo com ninho; migração 0: manadas param de migrar.
10. Afastar-se mais de 96 blocos de uma manada errante e voltar: ela pode ter sumido (esperado); uma domesticada
    ou com nome nunca some.
