# Estudo: a luta épica (06/11/2026)

Pedido do Rodrigo depois de jogar a 1.9 em teste: as lutas "ainda estão muito estáticas, monótonas"; "quero que repasse
completamente as lutas e as animações pra isso, quero algo realmente dinâmico e legal, estude mais aquele mod com as
lutas boas, quero algo épico".

Fonte: o sistema de luta do "Raxiores Of Raxiore" v0.6 (1.20.1 Forge, MCreator, All Rights Reserved). O jar foi aberto
numa pasta temporária fora do repositório só para medir a técnica. Nada foi copiado: nem código, nem modelo, nem
animação, nem som. Aqui ficam as conclusões e o nosso desenho.

## Por que a luta deles parece épica

1. **Duelo é outro modo.** Perto de um rival à altura, o bicho entra em guarda: o corpo de perfil (~48°), a cabeça
   no rival, e anda de lado em volta dele com quatro passos misturados (frente, trás, direita, esquerda). Nunca fica
   parado.
2. **O rumo muda pela distância.** A cada poucos segundos sorteia um rumo: longe, ziguezagueia para dentro; perto,
   recua ou sai de lado; no meio, circula.
3. **Paciência que se esgota.** Cada um tem uma paciência que cai com o tempo, e cai mais rápido quanto mais tempo nada
   acontece. Também ataca na hora em que o outro acabou de gastar o golpe (punição).
4. **Golpes comprometidos.** Além do golpe curto, o bote: o corpo gira do perfil para a frente e é lançado uns 7 a 8
   blocos com o rumo travado. Bate forte; se erra, fica exposto. Tomar um golpe na própria preparação perde o golpe.
5. **Leitura do ritmo.** Ele guarda quando vieram os últimos golpes do outro e mede o compasso; quanto mais regular o
   ritmo do rival, mais certo é o parry. Variar o ritmo e o tipo de golpe é o que vence.
6. **Parry e cambalear.** O golpe que chega é desviado e respondido; quem foi aparado é girado de lado/de costas,
   lento e aberto por uns 2 s.
7. **Guarda que quebra.** Bloquear gasta uma barra; zerada, ele cambaleia e fica um tempo sem defesa.
8. **Impacto.** Tremor de câmera por fonte (com raio, mais forte perto), dois sons por golpe com tom variado, rugido
   em ondas.

## O que fizemos (do nosso jeito)

- `entity/ai/DuelGoal`: o duelo inteiro, numa máquina de estados (guarda, golpe, parry, bloqueado, cambaleio), com
  rumo por distância, paciência que drena, punição depois do golpe gasto, golpe curto, golpe-assinatura, finta e bote,
  leitura do compasso do rival (confiança de 0 a 50), parry com contra-golpe, bloqueio com guarda que quebra, esquiva de
  lado. O agarrão peito a peito e o engalfinhar de chifres saem da guarda (`DinosaurEntity.startClinch`, `lockHorns`).
  O movimento é pela velocidade (o andar de lado do Minecraft limita o passo a um quarto da caminhada).
- `entity/ai/DuelStyle`: cada espécie com o seu jeito: ângulo da guarda (terópodes de perfil; Tricerátops,
  Estiracossauro, Protocerátops e Paquicefalossauro de frente; o Anquilossauro mostra o flanco), alcance da arma, quanto
  o bote leva, o golpe curto e o golpe-assinatura, e o temperamento (parry, bloqueio, esquiva, paciência, passo).
- `DinosaurEntity.impact` + partícula `impact` + `RoarShake.impact`: tremor de câmera por peso e distância, e a poeira
  do próprio bloco do chão nos golpes pesados.
- Animações novas por espécie, com tempos fixos para o Java casar o golpe: `lunge` (1,8 s, golpe aos 0,50 s), `parry`
  (1,5 s, desvio de 0 a 0,25 s, contra-golpe aos 0,60 s) e `stagger` (1,6 s). Cada uma desenhada para o corpo e a arma
  da espécie (estudo 10): o T. rex esmaga e aperta, o Carnotauro bate com os chifres, o Giganotossauro corta
  atravessando, o Espinossauro estala o focinho com os ganchos, o Dakotaraptor salta com as foices, o Terizinossauro
  corta em cruz, os ceratopsianos estocam com os chifres, o Paquicefalossauro bate a cúpula, o Anquilossauro gira a
  clava.
