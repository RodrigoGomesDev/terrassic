# Paquirrinossauro refeito (1.11.0)

## v4, "o bisão" (16-18/11/2026, silhueta B)

Estudo aprovado: `docs/estudos/15_HERBIVOROS_1_11.md` (seção Paquirrinossauro e "Respostas do Rodrigo": *P. canadensis*,
8 m, roda de defesa, duelo de bossa, travessia, o almíscar sai). Feito direto pelo método "silhueta primeiro", a partir da
blocagem B escolhida pelo Rodrigo (`tools/modelgen/handmade/_silhuetas/pachyrhinosaurus.py`, `bison`). O WIP antigo na
receita recusada (`wip/paquirrino-receita-antiga`) não foi usado.

- **Postura:** corcova enorme sobre os ombros (5,3 m no topo) e as costas descendo em **degraus** até a cauda curta;
  cada degrau é uma camada da capa com um rolo de lã por cima (`BACK` em `pachy.py`). Barril sobre pernas curtas, as da
  frente mais longas. Cabeça-aríete pendurada do pescoço curto, a bossa voltada para o chão.
- **Medidas:** 137,5 px do bico à cauda, escala 0,931 (8 m, 16,2 texels por bloco); hitbox 2,4 x 4,2; assento 5,34.
- **Silhueta** (`pachyrhinosaurus/silcheck.py`): 0,83 com a blocagem B; Tricerátops 0,56, Estiracossauro 0,66,
  Protocerátops 0,68, Edmontossauro 0,44, Maiassauro 0,64. O alvo era 0,62, mas a própria blocagem B mede 0,72 do
  Estiracossauro e 0,75 do Protocerátops, e a vista de 3/4 normalizada de qualquer quadrúpede atarracado fica perto de
  0,70; a busca de parâmetros (corcova, cabeça, vão sob a barriga, largura, ganchos, gola) não passou de 0,66 sem sair
  dos 0,80 da blocagem. Os três ceratopsianos refeitos estão a 0,78-0,84 entre si; o Paquirrinossauro é o mais
  diferente do grupo (fileira em `fileira_ceratopsianos.png`).
- **Cabeça (padrão v3):** a bossa de *P. canadensis* como uma massa só de chifre (corpo e tampa encaixados, a bossa da
  testa colada atrás), em placas irregulares de chifre gasto com rachaduras e poros, as bordas de cima mais claras; bico
  fundo em gancho, gume claro de 1 texel (o "dente" de lado); olho pequeno e fundo sob a bossa da testa, íris
  castanho-escura com anel claro; rugas fundas em leque a partir da bossa; esporão jugal curto; gola curta e larga de
  borda arredondada e clara com pontinhas cor de chifre; dois ganchos curvos (`adult_hooks`, três peças cada, ponta
  escura). Acento do macho: ocre-dourado na raiz dos ganchos (`male_display`, o colar, e a gola em volta).
- **Pele desenhada:** pardo-tundra com uma **capa castanha de bisão** sobre a corcova e os ombros, mais clara no alto e
  escura embaixo, descendo em **franja de mechas** pelo flanco e pela parte de cima dos braços; garupa mais clara; pernas
  escuras de boi-almiscarado; barriga e papada quase brancas; escama fina só como um passo de tom no flanco baixo.
- **Filhote:** pele própria (`pachyrhinosaurus_baby.png`, mais clara, sem capa), sem bossa nem ganchos (`young_brow`).
- **Sela de Carga:** manta grossa sobre os degraus atrás da corcova (mais grossa atrás para o assento ficar nivelado),
  assento baixo, pega de osso, dois fardos nos flancos.
- **Animações (50):** o conjunto padrão, o vivo e o de luta (guard, strafe, feint, block, recoil, submit, lunge 1,8 s,
  parry 1,5 s, stagger 1,6 s) e as dele: `ring_defence`, `brace` (laço), `boss_ram` (golpe 0,60 s), `boss_push` /
  `horn_lock` (testa colada), `horn_lock_start`/`_break`, `head_toss` (0,35 s), `boss_rub`, `snow_dig`, `hesitate`,
  `wade`, `charge`, `roar`.
- **Portões:** QA limpo, headcheck (cabeça 0,26 x corpo 0,20, olho e gume visíveis, acento 37), uniquecheck (máx. 0,63, Daspletossauro e Protocerátops; limite 0,78),
  colourcheck --remade 10,6 (Velociraptor), silcheck 0,801 com a blocagem (Tricerátops 0,53, Estiracossauro 0,63,
  Protocerátops 0,65, Maiassauro 0,63, Edmontossauro 0,41).
- **Passada da bossa e da corcova (20/11/2026):** bossa mais curta e baixa (18 x 26 x 8 texels, antes 30 de comprido
  até a ponta do bico), uma almofada de chifre sobre o focinho; queratina pardo-acinzentada quente, poucas placas
  grandes com bordas gastas claras, sem poros nem ruído. Corcova em 12 camadas curtas a 4-5 texels uma da outra
  (antes 9 degraus de 6-7), lã do topo contínua no espaço do corpo (tufos 3x4, sem faixa de tábua), espelhos dos
  degraus no tom da lã sem a linha clara de cada degrau.

## Teste no jogo (fase `pachy` da `BehaviorTest`, Fabric, 18-19/11/2026)

`behavior_regression.py`: 13 de 14 checagens do Paquirrinossauro OK na última rodada.
- Roda: 5 adultos na roda, 2 de 2 filhotes no meio, 5 de 5 virados para fora (desvio médio 2 graus), 5 de 5 em
  brace; 10 saídas com 10 golpes, cada um volta ao seu lugar; a roda desfaz com o predador a 28 blocos.
- Duelo de bossa: 2 cabeçadas, testa colada, um cede e sai (3,7 → 8,3 blocos), os dois com 100% de vida.
- Travessia: a manada espera 3 s na margem, o líder entra primeiro, 5 de 5 atravessam.
- Neve: o `snow_dig` passou em três rodadas e falhou nas três últimas (mesmo com o teste pondo meio-dia): instável,
  falta achar o que segura o gesto na arena da neve.
- Consertos achados pelo teste: NPE quando a roda terminava (`ringTick` com a roda já nula), o adulto que saía
  perseguia o predador e arrastava a roda (agora descansa 5 s no lugar entre saídas), o perdedor do duelo voltava
  para o vencedor (anda 10 s para longe; o vencedor fica parado), seguidores que já estavam na água na margem (voltam
  para trás do líder), contagem dupla na outra margem, gesto preso numa travessia já terminada.
