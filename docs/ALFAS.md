# Alfas

Pedido do Rodrigo (01/11/2026): um alfa é o mesmo bicho da espécie, com o mesmo modelo e as mesmas animações,
só que bem maior, bem mais forte, com nível alto e uma pele própria por sexo. Plano aprovado na página
"Dinos Alfa" (https://claude.ai/artifact/TrtzdxnXty1ipAs1eERzZJ).

Código: `entity/Alphas.java` (espécies com alfa, nascimento, registro, comando) e a seção "the alpha" de
`entity/DinosaurEntity.java`. Peles: `tools/modelgen/handmade/<espécie>/` grava `<id>_alpha_male.png` e
`<id>_alpha_female.png`; `client/DinoGeoModel` usa essas texturas quando o bicho é alfa.

## Espécies com alfa

| Espécie | Tamanho do alfa | Macho | Fêmea | Toque próprio |
|---|---|---|---|---|
| T. rex | 1,25–1,30× (o Tirano da Fenda, 1,35×, segue o maior) | Marfim (branco, faixas como cicatrizes rosadas) | Brasa (vermelho-sangue, faixas quase pretas) | O chão treme a cada passo perto dele |

Uma espécie nova entra em `Alphas.SPECIES` só quando as duas peles dela existirem e forem aprovadas. O alfa vira uma
seção do estudo de cada dino refeito.

## Nascimento

- Só no nascimento natural de um adulto selvagem (ecossistema ou geração do mundo) de uma espécie com alfa.
- Chance: regra "Chance de alfa", padrão 0,5% (1 em 200).
- Nunca a menos de 1.500 blocos do spawn do mundo (regra).
- No máximo um alfa da mesma espécie a cada 1.024 blocos, e no máximo 4 alfas selvagens vivos no mundo (regra).
- Depois que um alfa morre ou é domado, a região dele fica 7 dias de jogo sem alfa da mesma espécie.
- Nunca nasce de ovo nem de cruza. Regra do Rodrigo: filhote alfa só de macho alfa com fêmea alfa da mesma espécie,
  quando o sistema de ovos e cruza for refeito. Hoje alfa com qualquer um dá filhote comum.
- Anda sozinho: o T. rex alfa nunca nasce com a família de filhotes que o comum às vezes traz.
- Não some quando o jogador se afasta.
- `data/terrassic_alphas.dat` guarda os alfas selvagens (posição atualizada a cada 5 s enquanto carregados; um alfa
  que não aparece há 3 dias deixa de contar no limite), as regiões em descanso e os donos dos alfas domados.

## Força

- Nível sorteado entre 80% e 100% da regra "Nível máximo selvagem" (padrão 150: de 120 a 150), sem o teto de
  "Níveis por distância".
- Vida cresce com o quadrado do tamanho e dano com o tamanho (como todo bicho), mais +25% de vida de alfa selvagem.
  A regra "Força dos alfas" multiplica a vida e o dano do alfa selvagem.
- +25% de vida para cada jogador a mais a até 32 blocos, até +100%.
- Não é empurrado. Velocidade igual à da espécie.
- Aura: fagulhas de pó na cor da pele do alfa sobem das costas e dos flancos (T. rex macho cinza-claro que apaga em
  cinza, fêmea brasa que esfria em vermelho escuro), com algumas faíscas que brilham no escuro (luz branca no macho,
  chama pequena na fêmea). O dobro quando ele está bravo, nenhuma quando está desmaiado (foi vencido). Quem monta não
  vê a própria aura. Só no cliente, até o alcance normal de partículas (~32 blocos); flag `alpha_aura` no config do
  cliente desliga. Teste 2 (01/11): sorteada dentro da caixa, quase toda nascia escondida no corpo e sumia à noite.
- A caixa de colisão fica na largura do maior bicho comum da espécie, para ele não travar entre as árvores. O modelo
  e a altura crescem.
- T. rex alfa típico: uns 590 de vida e 30 de dano, contra uns 140 e 15 do comum.
- O Tirano da Fenda agora nasce sempre no nível máximo da regra (antes sorteava como um bicho comum).

## Nocaute e doma

- Só por nocaute. Comida na mão e filhote não servem.
- Torpor 4× maior; dardo e erva do sono com metade do efeito; acordado ele se recupera como um bicho comum (o teste de 01/11 com 2× deu uns 130 dardos para um jogador só).
- Desmaiado, fica um minuto no chão e levanta quando o torpor cai a um quarto (meia doma perdida, bravo com quem
  o derrubou). Erva do sono segura ele dormindo.
- Só come carne nobre e precisa de 3× mais.
- Cada golpe nele desmaiado tira 20% de eficiência.
- A regra "Dificuldade da doma de alfa" multiplica o torpor e a comida.
- Regra "Alfas podem ser domados" (padrão sim) e "Alfas domados por jogador" (padrão 1 por espécie; 0 = sem limite).
- Domado, mantém tamanho, pele, nome e nível, ganha os níveis da doma e perde o bônus de alfa selvagem.

## Recompensa

- XP dobrada no abate. A carcaça fica com a pele e o nome do alfa e cresce com o tamanho (mais carne e couro).
- Falta (próxima etapa): crânio-troféu garantido, tapete de couro na cor do alfa, conquistas.

## Servidor

- Regra "Avisar quando um alfa cai" (padrão não): o chat avisa quando um alfa selvagem morre ou é domado, e por quem.
- `/terrassic alfa <espécie> [macho|femea]` (também `alpha`, `male`, `female`, `hembra`), só operadores: põe um alfa
  onde o comando roda, sem chance, distância nem limites. Para testar e para eventos.

## Testar

1. `/terrassic alfa tyrannosaurus macho` e `/terrassic alfa tyrannosaurus femea`: pele, tamanho, nome "Tiranossauro
   Alfa · Nv 120–150", tremor dos passos a menos de ~20 blocos (não para quem monta), aura de fagulhas na cor da pele.
2. Ao lado de um T. rex comum: o alfa bem maior; o comum desvia dele.
3. Nocaute: dardos com metade do efeito, só carne nobre, levanta em ~1 min se não der erva do sono.
4. Domar dois alfas da mesma espécie: o segundo recusa com a mensagem do limite.
5. Aba "Alfas" na tela de regras: os 8 valores, salvar e reabrir.
6. Mundo novo longe do spawn com "Chance de alfa" em 10%: alfas aparecem; perto do spawn, nunca.
