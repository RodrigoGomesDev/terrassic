# Alfas

Pedido do Rodrigo (01/11/2026): um alfa é o mesmo bicho da espécie, com o mesmo modelo, só que bem maior, bem mais
forte, com nível alto e uma pele própria por sexo. Desde 02/11 ele tem também animações só dele ("deixaria ele com
animacoes proprias dele"). Plano aprovado na página
"Dinos Alfa" (https://claude.ai/artifact/TrtzdxnXty1ipAs1eERzZJ).

Código: `entity/Alphas.java` (espécies com alfa, nascimento, registro, comando) e a seção "the alpha" de
`entity/DinosaurEntity.java`. Peles: `tools/modelgen/handmade/<espécie>/` grava `<id>_alpha_male.png` e
`<id>_alpha_female.png`; `client/DinoGeoModel` usa essas texturas quando o bicho é alfa.

## Espécies com alfa

| Espécie | Tamanho do alfa | Macho | Fêmea | Toque próprio |
|---|---|---|---|---|
| T. rex | 1,45–1,55×, uns 19 m (era 1,25–1,30× até 02/11; o Tirano da Fenda, 1,65×, segue o maior) | Marfim (branco, faixas como cicatrizes rosadas) | Brasa (vermelho-sangue, faixas quase pretas) | O chão treme a cada passo perto dele |

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
- +25% de vida para cada jogador a mais a até 32 blocos, até +100%. O Minecraft limita a vida máxima a 1024: com o
  T. rex alfa (uns 820) já o segundo jogador encosta no teto. Fica assim; o que pesa no multijogador é a mordida.
- Não é empurrado. Velocidade igual à da espécie.
- Aura: fagulhas de pó na cor da pele do alfa sobem das costas e dos flancos (T. rex macho cinza-claro que apaga em
  cinza, fêmea brasa que esfria em vermelho escuro), com algumas faíscas que brilham no escuro (luz branca no macho,
  chama pequena na fêmea). O dobro quando ele está bravo, nenhuma quando está desmaiado (foi vencido). Quem monta não
  vê a própria aura. Só no cliente, até o alcance normal de partículas (~32 blocos); flag `alpha_aura` no config do
  cliente desliga. Teste 2 (01/11): sorteada dentro da caixa, quase toda nascia escondida no corpo e sumia à noite.
- A caixa de colisão fica na largura do maior bicho comum da espécie, para ele não travar entre as árvores. O modelo
  e a altura crescem.
- T. rex alfa típico: uns 820 de vida e 35 de dano, contra uns 140 e 15 do comum.
- O Tirano da Fenda agora nasce sempre no nível máximo da regra (antes sorteava como um bicho comum). Desde 02/11
  ele tem 1,65× (era 1,35×), com vida e mordida de base reduzidas na mesma proporção: a mesma força de antes.

## Animações próprias (T. rex)

O dono da região: anda sem pressa e marca o território. Feitas em
`tools/modelgen/handmade/tyrannosaurus/alphaanims.py` (gravadas como `alpha_<nome>` no mesmo arquivo de animações) e
disparadas por `entity/RexAlphaMoves.java` (uma classe por espécie com alfa, criada por `entity/AlphaMoves.java`).

| Animação | Quando toca |
|---|---|
| `alpha_walk` | Andando calmo, no lugar do andar comum (passo mais longo, cabeça alta). Correndo ou caçando usa o comum. |
| `alpha_survey` | Parado sem nada para fazer, de vez em quando: cabeça alta, varre a região de um lado ao outro e fareja. |
| `alpha_jaw_rub` | Parado com um tronco a 3,5–4,5 blocos (× tamanho do modelo): vira para ele e esfrega a lateral da mandíbula três vezes; no fim a casca sai do bloco à altura da mandíbula (vira tronco descascado, só com `mobGriefing` ligado). Se entrar em luta, para. |
| `alpha_challenge` | No lugar da ameaça comum: cabeça baixa, balança o corpo e bate os pés três vezes (poeira e baque a cada pisada). |
| `alpha_bite_toss` | 30% das mordidas em algo de até 2 blocos de largura: morde, segura, levanta e arremessa para a esquerda dele, o lado do tranco do pescoço. Fica parado até a animação acabar. |
| `alpha_shove` / `alpha_shove_left` | Alvo ao lado ou atrás, fora do alcance da cabeça (até 4,5 blocos × tamanho): empurrão com o ombro do lado do alvo (direito ou esquerdo), que joga o alvo para longe. Uma vez a cada 4 s. Fica parado até a animação acabar. |
| `alpha_guard` | Uma carcaça com carne a até 12 blocos × tamanho e um jogador a até 16 (× tamanho): ele anda até a presa, para em cima dela e põe o pé sobre ela, rosnando, olho no jogador. Toca 6 s e acaba; uma vez a cada 10 s. |
| `alpha_ko_struggle` | Desmaiado, quando o torpor chega perto do ponto de acordar: tenta levantar uma vez e cai de volta. Aviso de que vai acordar. |

As animações ficam registradas em todo T. rex (o cliente monta os controladores antes de saber que é alfa), mas só o
alfa as toca. Uma espécie nova com alfa ganha a sua própria classe e o seu próprio estudo de animações.

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
- Crânio do alfa (troféu): só de alfa que morreu selvagem, sempre 1. É o crânio em 3D, de perfil, sobre o couro do
  próprio alfa esticado numa armação de galhos (Crânio do Alfa Marfim / Crânio da Alfa Brasa). O crânio ocupa 3/4 do
  tamanho para sobrar um anel de couro em volta: é ele que diz de qual alfa veio. O crânio é de um rei
  velho: duas cavidades cicatrizadas na mandíbula e um sulco curado atrás do olho (como o fóssil Sue) e um dente de
  cima quebrado. As aberturas do crânio são vazadas, com o fundo escuro. Pendura na parede como o troféu comum.
- Tapete de couro do alfa: 2 de todo alfa que morre (domado também). O couro das costas dele: placas rachadas na cor
  da pele e a marca em V das costas, que forma uma faixa quando os tapetes ficam lado a lado (Tapete de Couro Marfim
  / Tapete de Couro Brasa).
- Troféu e tapetes caem no chão ao lado do corpo, do lado das costas (ou do lado das pernas, se o das costas estiver
  bloqueado), fora do espólio da carcaça (um carniceiro comeria junto com a carne), e ficam 10 minutos. Não têm
  receita. Respeitam `doMobLoot`.
- Conquistas na aba Caderno de Campo: "Destronado" (derrubar um alfa selvagem; vale para quem matou, para o dono do
  bicho que matou ou para o último jogador que bateu) e "Coroa emprestada" (domar um alfa).
- Código: `Alphas.spoils`; texturas `tools/spritegen/alfa_trofeus.py` (o desenho do crânio, a máscara `SKULL`, gera
  também as caixas do modelo em `tools/javagen/gen_blocks.py`); conquistas `tools/javagen/conquistas.py`.
- Falta: registro do alfa no Caderno (research/* reservado ao Codex).

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
7. Matar um alfa selvagem: crânio + 2 tapetes no chão ao lado da carcaça, conquista "Destronado". Domar um:
   "Coroa emprestada". Pendurar o crânio na parede (vira para quem coloca) e pôr os 2 tapetes lado a lado.
8. Animações do alfa: andar calmo; parado perto de árvore (casca sai com mobGriefing); chegar perto dele saciado
   (bate os pés); lutar com ele (arremesso, empurrão de lado); carcaça com carne perto dele; nocaute até perto de
   acordar (tenta levantar).
