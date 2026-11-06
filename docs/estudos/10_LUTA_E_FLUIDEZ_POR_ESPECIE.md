# Estudo: como cada um lutava, e a animação fluida de cada refeito (06/11/2026)

Pedido do Rodrigo: "as animações quero que estude para portar pros outros também... realmente quase um jogo de luta
entre dinos, cada um com sua animação única e fluida, lembrando que tem que ter um estudo por trás sempre".

Base: o T. rex (estudos 08 e 09, `rexflow.py`, `rexduel.py`, `rexmore.py`, `LivelyMotion`, o duelo do `ApexBiteGoal`).
Aqui, por espécie, o que a ciência diz de como brigava e se defendia, e o que isso vira em jogo. Regra da fluidez para
todos (estudo 08): nada para, nada liga ou desliga de uma vez, ação em três tempos (preparo, golpe, assentamento), a
cauda e o pescoço acompanham com atraso, respiração por baixo de toda ação.

## Conjunto comum (cada um com o seu jeito)

`guard` (laço), `strafe_left` / `strafe_right` (laço), `turn_left` / `turn_right` (laço), um **golpe-assinatura**,
`block` (aparar do jeito da espécie), `recoil`, `submit`, `lie_down`, `get_up`, `idle_tired`, `walk_tired`, e a passada
de fluidez nas animações que já existem (respiração, cauda com atraso, sem chaves ligando/desligando).

## Terópodes grandes

| Espécie | Evidência | Estilo de luta em jogo | Assinatura |
|---|---|---|---|
| **Tyrannosaurus** | marcas de mordida no rosto de outros tiranossauros (Peterson et al. 2009); mordida de esmagar osso (Gignac & Erickson 2017) | encara, circula, finta, morde o rosto, empurra com o ombro | feito (estudo 08) |
| **Carnotaurus** | chifres e crânio reforçado para choques de cabeça (Mazzetta et al. 1998, 2009); mordida fraca, rápida; o corredor mais rápido dos grandes terópodes | não morde para segurar: **dá cabeçadas** de lado e de frente com os chifres, mordidas rápidas de corte, muito movimento lateral | `ram`: abaixa a cabeça e investe de chifres; `head_clash` quando dois se chocam |
| **Giganotosaurus** | dentes em lâmina para cortes (Coria & Currie 2006); carcarodontossaurídeos feriam e esperavam a presa sangrar | corta e recua, rodeia, espera; pesado, menos fintas, mais paciência | `slash` lateral longo; `grab_shake` só em presa menor |
| **Spinosaurus** | garras em gancho no polegar (Charig & Milner 1997); focinho de crocodilo, vida semiaquática (Ibrahim et al. 2020); vela de exibição | exibe a vela de lado antes de brigar, golpes de garra, botes de focinho | `sail_display` de lado; `claw_swipe` |

## Raptores

| Espécie | Evidência | Estilo | Assinatura |
|---|---|---|---|
| **Velociraptor** | o fóssil "Dinossauros em Luta" (Velociraptor x Protoceratops, Mongólia, 1971): a foice na garganta, o braço preso no bico; contenção da presa com o pé (Fowler et al. 2011) | ágil, salta, chuta com a foice, recua; bando | `kick` (já existe), `leap`; contra igual: saltos e recuos |
| **Dakotaraptor** | grande dromeossaurídeo com nós de penas (DePalma et al. 2015); contenção da presa | bote, prende, asas para equilíbrio (feito na 1.9) | `pounce`, `pin`, `wing_flash` (feitos) |

## Ceratopsianos

| Espécie | Evidência | Estilo | Assinatura |
|---|---|---|---|
| **Triceratops** | lesões no esquamosal e no folho de muitos crânios: chifres travados em luta entre eles (Farke et al. 2009) | de frente sempre, gira para manter os chifres apontados, investe; contra outro Tricerátops **trava os chifres e empurra** | `horn_lock` (engalfinhar), `charge` (existe) |
| **Styracosaurus** | espinhos do folho para exibição; chifre do nariz para golpes | exibe a coroa, balança a cabeça, golpe curto de chifre do nariz | `crown_display` (existe), `nose_jab` |
| **Protoceratops** | o mesmo fóssil de 1971: mordeu e prendeu o braço do Velociraptor | pequeno e teimoso: mordida que prende, empurrão de folho | `bite_hold` (existe) |

## Cabeças-duras, bicos de pato, encouraçados e outros

| Espécie | Evidência | Estilo | Assinatura |
|---|---|---|---|
| **Pachycephalosaurus** | lesões nas cúpulas: golpes de cabeça entre eles (Peterson et al. 2013) | abaixa a cabeça e dá **cabeçadas** nos flancos e de frente | `butt` / `flank_butt` |
| **Parasaurolophus / Edmontosaurus** | cauda de Edmontosaurus com mordida de tiranossauro cicatrizada: escaparam (DePalma et al. 2013) | fogem; encurralados, chutam e empurram com o corpo | `kick_back`, `shove` |
| **Ankylosaurus** | Zuul crurivastator com espinhos do flanco quebrados e cicatrizados: clava contra clava (Arbour et al. 2022) | vira o flanco, gira a cauda; contra outro: **golpes de clava nos flancos** | `club_l` / `club_r` (existem), `club_duel` |
| **Therizinosaurus** | garras de até 50 cm, mais de exibição e defesa que de caça (Lautenschlager 2014) | abre os braços, corta, tesoura (feito) | `claw_display`, `scissor` (feitos) |
| **Gallimimus** | corredor; sem armas | foge; encurralado, chute | `kick_back` |
| **Deinosuchus** | marcas de mordida em ossos de dinossauros (Rivera-Sylva et al. 2009) | emboscada da água, giro da morte (feito) | `death_roll` (feito) |
| **Mosasaurus / Elasmosaurus** | crânios de mosassauro com mordidas de outros mosassauros (Lindgren et al. 2013) | no mar: investida, mordida de lado; o Elasmossauro, bote de pescoço | `ram_bite`, `neck_strike` (existe) |
| **Pteranodon / Quetzalcoatlus** | cristas para exibição (Bennett 1992); bico em lança | exibição de crista, bicadas | `display` (existe), `jab` |

## Ordem de trabalho da 1.9.0

1. Camada viva (`LivelyMotion`) para todo refeito: cauda em mola com o número de segmentos de cada rig, inclinação na
   curva, ofegar; pés no terreno para os bípedes.
2. Duelo do `ApexBiteGoal` para o Carnotauro e o Giganotossauro (mesma base), cada um com o seu estilo.
3. Passada de fluidez e conjunto comum, por família: raptores, ceratopsianos, cabeças-duras e bicos de pato,
   encouraçado e terizinossauro, marinhos e pterossauros.
4. Engalfinhar chifre com chifre no Tricerátops; cabeçadas do Paquicefalossauro; clava contra clava.
