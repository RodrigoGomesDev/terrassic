# Tamanhos dos dinossauros

Regra: **1 bloco = 1 metro**. O jogador tem 1,8 bloco, então ele é uma pessoa de 1,8 m ao lado do bicho.
Tudo sai da tabela `SIZES` em `tools/javagen/gen_species.py` (rode `python3 gen_species.py` depois de mudar).
Comparação visual: `art/tamanhos/comparacao_tamanhos.png` (cor = novo, sombra cinza = antigo).

| Espécie | Real | Antes no jogo (compr. x alt.) | Agora no jogo (compr. x alt.) | Hitbox (larg. x alt.) | Filhote |
|---|---|---|---|---|---|
| Brachiosaurus | 18-22 m, cabeça a ~13 m | 6,8 x 5,2 | **22,0 x 16,8** | 4,0 x 9,0 | 12% |
| Spinosaurus | 14 m | 7,6 x 3,1 | **14,0 x 5,7** (vela) | 2,5 x 4,6 | 25% |
| Tyrannosaurus | 12-13 m (Sue 12,3; Scotty ~13) | 6,6 x 2,7 | **13,0 x 5,2** | 2,6 x 4,8 | 25% |
| Parasaurolophus | 9,5 m | 6,3 x 2,5 | **9,5 x 3,8** | 2,0 x 3,2 | 30% |
| Triceratops | 9 m | 5,5 x 2,3 | **9,0 x 3,7** | 2,4 x 3,0 | 30% |
| Stegosaurus | 9 m | 5,8 x 2,3 | **9,0 x 3,5** | 2,2 x 3,2 | 30% |
| Ankylosaurus | 6-8 m | 4,4 x 1,3 | **8,0 x 2,3** | 2,6 x 2,1 | 30% |
| Dilophosaurus | 7 m | 4,6 x 2,0 | **7,0 x 3,0** | 1,2 x 2,6 | 35% |
| Gallimimus | 6 m | 3,9 x 2,0 | **6,0 x 3,0** | 1,2 x 2,6 | 35% |
| Pachycephalosaurus | 4,5 m | 3,1 x 1,5 | **4,5 x 2,2** | 1,0 x 1,9 | 40% |
| Velociraptor | 1,5-2,07 m, quadril ~0,5 m, 15-20 kg | 2,1 x 0,8 | 2,1 x 0,8 (igual) | 0,7 x 0,9 | 50% |
| Compsognathus | 1-1,25 m | 1,2 x 0,4 | 1,3 x 0,4 | 0,4 x 0,5 | 50% |
| Mosasaurus (v0.3) | 11-17 m (M. hoffmannii; estimativa máxima ~17 m, Grigoriev 2014) | novo | **17,0 x 3,0** | 3,0 x 2,0 | 20% |
| Tylosaurus (v0.5) | 12-13 m (espécime "Bunker" KUVP 5033 ~13 m; Everhart 2005), esguio, nadadeiras pequenas | novo | **13,0 x 1,9** | 2,6 x 1,8 | 20% |
| Elasmosaurus (v0.5) | ~10,3 m, pescoço ~7 m com 72 vértebras (Sachs 2005) | novo | **10,3 x 1,3** | 2,0 x 1,4 | 20% |
| Xiphactinus (v0.5) | 4,5-6 m, o maior da família (Everhart 2005; "peixe dentro do peixe" FHSM VP-333 ~4 m) | novo | **6,0 x 1,9** (com nadadeiras) | 1,6 x 1,2 | 30% |
| Archelon (v0.5) | 4,6 m de comprimento, 4 m entre as pontas das nadadeiras (Wieland 1896/1902; YPM 3000) | novo | **4,6 x 1,0** (5,0 de envergadura) | 2,2 x 1,1 | 25% |
| Hesperornis (v0.5) | até 1,8 m (Marsh 1880; Bell & Chiappe 2015), ave mergulhadora sem voo | novo | **1,8 x 0,6** | 0,6 x 0,6 | 40% |
| Deinosuchus (v0.5) | 10,6 m bem medidos (Cossette & Brochu 2020), até 12 m em estimativas antigas (Schwimmer 2002) | novo | **12,0 x 1,6** | 2,6 x 1,4 | 20% |
| Baurusuchus (v0.5) | ~3,5 m (Carvalho, Campos & Nobre 2005), crocodilomorfo terrestre de pernas eretas | novo | **3,5 x 1,0** | 1,0 x 1,0 | 30% |
| Edmontosaurus (v0.6) | 12 m, ~4 t (E. annectens; Campione & Evans 2011; espécimes maiores reivindicados) | novo | **12,0 x 3,6** | 2,4 x 3,6 | 20% |
| Corythosaurus (v0.6) | 9 m, 3-4 t (Evans et al. 2009), crista em elmo | novo | **9,0 x 3,3** | 2,0 x 3,3 | 20% |
| Styracosaurus (v0.6) | 5-5,5 m, ~2,7 t (Ryan et al. 2007), chifre nasal 57 cm | novo | **5,5 x 2,9** (com espinhos) | 1,6 x 2,9 | 30% |
| Euoplocephalus (v0.6) | 5,5-6 m, ~2,5 t (Arbour & Currie 2013; Paul 2010), 2 m de largura | novo | **6,0 x 1,7** | 2,0 x 1,8 | 30% |
| Protoceratops (v0.6) | 1,8-2,5 m, 60-180 kg (Dodson 1976; Fastovsky et al. 2011) | novo | **2,0 x 0,8** | 0,7 x 0,8 | 50% |
| Struthiomimus (v0.6) | 4,3 m, ~150 kg (Osborn 1917; Nicholls & Russell 1985) | novo | **4,3 x 2,5** (cabeça erguida) | 1,0 x 2,4 | 35% |
| Thescelosaurus (v0.6) | 3,5-4 m, ~250-300 kg (Boyd 2014) | novo | **4,0 x 1,6** | 1,0 x 1,6 | 35% |
| Pachyrhinosaurus (v0.6) | 6-8 m, ~4 t (Currie et al. 2008) | novo | **8,0 x 4,2** (com chifres do escudo) | 2,4 x 3,6 | 30% |
| Therizinosaurus (v0.6) | 9-10 m, ~5 t (Zanno 2010; Paul 2010), garras de 52 cm | novo | **10,0 x 6,4** (pescoço erguido) | 2,4 x 5,0 | 20% |
| Deinocheirus (v0.6) | 11 m, ~6,4 t (Lee et al. 2014), braços de 2,4 m | novo | **11,0 x 6,1** (pescoço erguido) | 2,4 x 4,8 | 20% |
| Alamosaurus (v0.6) | 26-30 m, 30-80 t (Fowler & Sullivan 2011) | novo | **30,0 x 13,4** (cabeça erguida) | 5,0 x 9,0 | 10% |
| Saltasaurus (v0.6) | 12-13 m, ~7 t (Paul 2010; Bonaparte & Powell 1980) | novo | **12,0 x 4,8** (cabeça erguida) | 2,8 x 3,8 | 15% |
| Argentinosaurus (v0.6) | 30-35 m, 65-75 t (Sellers et al. 2013; Paul 2019) | novo | **35,0 x 15,1** (cabeça erguida) | 6,0 x 10,0 | 8% |
| Opisthocoelicaudia (v0.6) | 11-12 m, ~8,5 t (Borsuk-Bialynicka 1977; Paul 2010) | novo | **12,0 x 3,6** (pescoço baixo; 8,2 empinado) | 2,6 x 3,6 | 15% |
| Dreadnoughtus (v0.6) | 26 m, 26-59 t (Lacovara et al. 2014; Bates et al. 2015) | novo | **26,0 x 15,0** (pescoço de 11 m erguido) | 4,5 x 9,0 | 10% |
| Giganotosaurus (v0.7) | 12-13 m, 6-8 t (Coria & Salgado 1995; Calvo & Coria 1998, dentário MUCPv-95) | novo | **13,0 x 4,6** | 2,4 x 4,4 | 25% |
| Carcharodontosaurus (v0.7) | 12-13,3 m, 6-15 t (Sereno et al. 1996, SGM-Din 1; Therrien & Henderson 2007) | novo | **12,5 x 4,9** | 2,4 x 4,6 | 25% |
| Carnotaurus (v0.7) | 7,5-8 m, 1,3-2,1 t (Bonaparte et al. 1990, MACN-CH 894; Mazzetta et al. 2004) | novo | **8,0 x 3,6** | 1,8 x 3,4 | 30% |
| Tarbosaurus (v0.7) | 10-12 m, 4-5 t (Hurum & Sabath 2003, PIN 551-1; Paul 2010) | novo | **12,0 x 4,5** | 2,5 x 4,3 | 25% |
| Daspletosaurus (v0.7) | 8,5-9 m, 2,5-3,8 t (Russell 1970, CMN 8506; Currie 2003) | novo | **9,0 x 3,9** | 2,1 x 3,8 | 28% |
| Albertosaurus (v0.7) | 8-10 m, 1,7-2,5 t (Currie 2003; Erickson et al. 2004, Dry Island) | novo | **9,5 x 3,8** | 1,9 x 3,6 | 28% |
| Majungasaurus (v0.7) | 6-8 m, ~1,1 t (Sampson & Witmer 2007, FMNH PR 2100; Krause et al. 2007) | novo | **7,5 x 3,2** | 1,6 x 3,0 | 30% |
| Dakotaraptor (v0.7) | ~5,5 m, 220-350 kg (DePalma et al. 2015, PBMNH.P.10.113.T; foice de 24 cm) | novo | **5,5 x 2,1** | 1,0 x 2,0 | 40% |
| Troodon (v0.7) | ~2,4 m, ~50 kg (Russell 1969; Varricchio 1997, Egg Mountain) | novo | **2,4 x 1,1** | 0,6 x 1,1 | 50% |
| Oviraptor (v0.7) | 1,6-2 m, ~33-40 kg (Osborn 1924, AMNH 6517; Paul 2010) | novo | **2,0 x 1,5** (cabeça erguida) | 0,7 x 1,4 | 50% |
| Citipati (v0.7) | 2,5-3 m, ~75-85 kg (Clark, Norell & Barsbold 2001, IGM 100/979 "Big Mama"; Paul 2010) | novo | **3,0 x 2,3** (cabeça erguida, com casque) | 0,9 x 2,0 | 40% |
| Maiasaura (v0.3) | 7-9 m, ~3 t | novo | **9,0 x 2,8** | 2,0 x 2,8 | 20% |
| Quetzalcoatlus (v0.4) | envergadura 10-11 m (Witton & Habib 2010; Andres & Langston 2021), ~5 m de altura em pé | novo | **11 de envergadura** x ~6,8 em pé | 2,5 x 5,0 | 25% |
| Hatzegopteryx (v0.4) | envergadura 10-12 m (Buffetaut et al. 2002; Naish & Witton 2017), crânio ~3 m e meio metro de largura | novo | **12 de envergadura** x ~5,7 em pé | 2,5 x 4,6 | 25% |
| Ichthyornis (v0.4) | envergadura ~60 cm, corpo ~25 cm (Clarke 2004; Field et al. 2018), ave do tamanho de um trinta-réis | novo | **0,66 de envergadura** x 0,3 | 0,4 x 0,4 | 50% |
| Pteranodon (v0.3) | envergadura 5,6-7,25 m nos machos (Bennett 2001), corpo pequeno | novo | **7,25 de envergadura** x 1,9 | 1,3 x 1,7 | 30% |

## Escolhas

- **Regra para toda espécie nova (Rodrigo, 24/10/2026):** tamanho real pelo maior espécime bem documentado,
  1 bloco = 1 metro, com a fonte anotada nesta tabela.

- Antes quase todos estavam com uns 55-65% do tamanho real. Agora estão no tamanho real, usando o **topo das
  estimativas publicadas** (os maiores adultos conhecidos), por pedido do Rodrigo em 24/10/2026.
- O Brachiosaurus usa os 22 m de comprimento. O nosso modelo segura o pescoço mais em pé que as
  reconstruções (o esqueleto montado do Giraffatitan em Berlim tem 13,3 m de altura), então a cabeça fica a
  ~17 blocos. Dá para baixar o pescoço no tools/modelgen se quiser ficar exato.
- A hitbox (caixa de colisão) é menor que o modelo de propósito. No Minecraft ela é quadrada, e bichos com mais
  de uns 2,5 blocos de largura ficam presos entre árvores. A cauda e o pescoço passam um pouco por dentro dos
  blocos, como acontece em outros mods de dinossauro.
- O Velociraptor continua com o tamanho real: os fósseis da Mongólia dão 1,5-2,07 m de comprimento (quase tudo
  cauda), ~0,5 m de altura no quadril e 15-20 kg, do tamanho de um peru. O raptor de Jurassic Park foi
  baseado no Deinonychus (3,4 m). O raptor maior que um humano é o Utahraptor (5,5-7 m, quadril ~1,5 m,
  280-500 kg), que pode entrar no roster como espécie nova.
- Filhotes agora têm tamanho por espécie: um T. rex recém-nascido tem 3 m, e não mais metade do adulto.
- Altura da sela, culling e sombra foram recalculados automaticamente a partir da escala.

## O que testar no Mac

1. `./gradlew :fabric:runClient` compila (a nuvem não consegue baixar as dependências).
2. Montar T. rex, Triceratops, Brachiosaurus, Parasaurolophus e Gallimimus: o jogador fica sentado na sela?
3. T. rex na selva e Stegosaurus/Ankylosaurus na floresta: eles andam ou ficam presos nas árvores?
4. Gigantes andando: os pés escorregam (parece "moonwalk")? Se sim, aumento a velocidade da animação de passo.
5. Chocar um ovo: o filhote nasce pequeno e cresce para o tamanho adulto sem travar no chão?
6. O Brachiosaurus some da tela quando você olha só para a cabeça dele? (culling)

## Fontes das medidas

- Velociraptor: Turner, Makovicky & Norell (2007); resumo em [Live Science](https://www.livescience.com/23922-velociraptor-facts.html).
- Brachiosaurus: Taylor (2009) e [SV-POW, "How big was Brachiosaurus altithorax? I mean, really?"](https://svpow.com/2014/06/02/how-big-was-brachiosaurus-altithorax-i-mean-really/).
- T. rex: Persons et al. (2019), espécime "Scotty"; Spinosaurus: Ibrahim et al. (2020).
- Ankylosaurus: Arbour & Mallon (2017). Demais: verbetes da Wikipedia de cada espécie.
