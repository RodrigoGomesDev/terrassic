"""All story and science text of the mod, in the three languages: (pt_br, en_us, es_es).

gen_resources.py turns every entry into translation keys and writes research/KatarinaPages.java from PAGES.
Tone (docs/HISTORIA.md, section 9): short sentences, first person in Katarina's pages, no unexplained jargon.
"""

# ------------------------------------------------------------------ intro screen (first time in the world)
INTRO = [
    ("Santa Maria, Rio Grande do Sul. Laboratório do Projeto Terrassic.",
     "Santa Maria, Rio Grande do Sul, Brazil. Terrassic Project laboratory.",
     "Santa Maria, Rio Grande do Sul, Brasil. Laboratorio del Proyecto Terrassic."),
    ("A máquina foi feita só para olhar o passado. Ninguém deveria atravessar.",
     "The machine was built only to look at the past. No one was supposed to cross.",
     "La máquina se hizo solo para mirar el pasado. Nadie debía cruzar."),
    ("Há nove dias, a Dra. Katarina Brandt atravessou. E não voltou.",
     "Nine days ago, Dr. Katarina Brandt crossed. And she never came back.",
     "Hace nueve días, la Dra. Katarina Brandt cruzó. Y no volvió."),
    ("O núcleo de âmbar ainda brilhava quando você entrou na câmara.",
     "The amber core was still glowing when you stepped into the chamber.",
     "El núcleo de ámbar todavía brillaba cuando entraste en la cámara."),
    ("Então veio a luz. E depois, o silêncio.",
     "Then came the light. And then, silence.",
     "Entonces llegó la luz. Y después, el silencio."),
]
INTRO_ERA = ("Cretáceo Superior — 68 milhões de anos atrás",
             "Late Cretaceous — 68 million years ago",
             "Cretácico Superior — hace 68 millones de años")

# ------------------------------------------------------------------ "Relatório do Incidente" (notebook, Report tab)
REPORT = [
    dict(title=("O achado", "The find", "El hallazgo"),
         text=("Março. Numa rocha do Triássico, perto de Santa Maria, a equipe achou um âmbar que brilhava sozinho. "
               "Não era resina comum: dentro dele, a luz se movia devagar, como água.\n\n"
               "A Dra. Katarina Brandt passou a noite inteira olhando para ele. De manhã ela disse: \"Isto não guarda o passado. Isto mostra o passado.\"",
               "March. In a Triassic rock near Santa Maria, the team found a piece of amber that glowed on its own. "
               "It was not ordinary resin: inside it, the light moved slowly, like water.\n\n"
               "Dr. Katarina Brandt spent the whole night staring at it. In the morning she said: \"This does not keep the past. It shows the past.\"",
               "Marzo. En una roca del Triásico, cerca de Santa Maria, el equipo encontró un ámbar que brillaba solo. "
               "No era resina común: dentro de él, la luz se movía despacio, como agua.\n\n"
               "La Dra. Katarina Brandt pasó la noche entera mirándolo. Por la mañana dijo: \"Esto no guarda el pasado. Esto muestra el pasado.\"")),
    dict(title=("Registros do laboratório", "Laboratory log", "Registros del laboratorio"),
         text=("Dia 1: a máquina mostra imagens de uma floresta de samambaias. Dia 3: as imagens ficam nítidas. Dia 5: um animal olha de volta para a câmera.\n\n"
               "Dia 6: a Katarina pede para desligar os limites de energia. A direção nega.\n\n"
               "Dia 7: alguém desligou os limites de energia.",
               "Day 1: the machine shows images of a fern forest. Day 3: the images become sharp. Day 5: an animal looks back at the camera.\n\n"
               "Day 6: Katarina asks to remove the power limits. The board says no.\n\n"
               "Day 7: someone removed the power limits.",
               "Día 1: la máquina muestra imágenes de un bosque de helechos. Día 3: las imágenes se vuelven nítidas. Día 5: un animal mira de vuelta a la cámara.\n\n"
               "Día 6: Katarina pide quitar los límites de energía. La dirección lo niega.\n\n"
               "Día 7: alguien quitó los límites de energía.")),
    dict(title=("A última mensagem", "The last message", "El último mensaje"),
         text=("Gravado pela máquina às 3h12 da manhã:\n\n"
               "\"Se alguém vier atrás de mim: não traga nada. Nada atravessa além de nós. "
               "Nem roupa, nem ferramenta, nem papel. Você vai chegar com as mãos vazias. Aprenda com os bichos. Eles sabem viver lá.\"",
               "Recorded by the machine at 3:12 a.m.:\n\n"
               "\"If anyone comes after me: bring nothing. Nothing crosses but us. "
               "No clothes, no tools, no paper. You will arrive empty-handed. Learn from the animals. They know how to live there.\"",
               "Grabado por la máquina a las 3:12 de la madrugada:\n\n"
               "\"Si alguien viene tras de mí: no traigas nada. Nada cruza salvo nosotros. "
               "Ni ropa, ni herramientas, ni papel. Vas a llegar con las manos vacías. Aprende de los animales. Ellos saben vivir allí.\"")),
    dict(title=("Minha nota", "My note", "Mi nota"),
         text=("Escrevo isto às pressas, na câmara. Nove dias e ninguém foi atrás dela. O núcleo ainda está ligado.\n\n"
               "Se este caderno for achado vazio na câmara, é porque eu fui. Vou encontrar a Katarina e trazer as duas de volta.\n\n"
               "Tudo o que eu aprender lá vai ficar escrito aqui.",
               "I am writing this in a hurry, in the chamber. Nine days and no one went after her. The core is still on.\n\n"
               "If this notebook is found empty in the chamber, it means I went. I will find Katarina and bring us both back.\n\n"
               "Everything I learn there will be written here.",
               "Escribo esto deprisa, en la cámara. Nueve días y nadie fue a buscarla. El núcleo sigue encendido.\n\n"
               "Si este cuaderno aparece vacío en la cámara, es porque fui. Voy a encontrar a Katarina y traernos a las dos de vuelta.\n\n"
               "Todo lo que aprenda allí quedará escrito aquí.")),
]

# ------------------------------------------------------------------ Katarina's pages, Chapter 1 (Late Cretaceous)
# kind: diary (her story) | species (a note about one animal). Pages are found as Loose Pages in chests until her
# camps exist; each one makes sense on its own (rule 0: any order).
PAGES = [
    dict(id="c1_day_3", day=3, kind="diary",
         text=("Nada atravessou comigo. Nem o relógio, nem a lanterna, nem o caderno. Este aqui é de casca de árvore costurada com tendão. "
               "Se alguém do projeto achar isto: eu estou viva, e estou com fome.",
               "Nothing crossed with me. Not the watch, not the flashlight, not the notebook. This one is tree bark sewn with sinew. "
               "If anyone from the project finds this: I am alive, and I am hungry.",
               "Nada cruzó conmigo. Ni el reloj, ni la linterna, ni el cuaderno. Este es de corteza de árbol cosida con tendón. "
               "Si alguien del proyecto encuentra esto: estoy viva, y tengo hambre.")),
    dict(id="c1_day_9", day=9, kind="diary",
         text=("Aprendi a lascar sílex batendo uma pedra na outra. A primeira lâmina cortou mais o meu dedo do que a carne. A quinta cortou bem. "
               "Amarrei uma num galho com fibra. Agora eu tenho uma lança, e um pouco menos de medo.",
               "I learned to knap flint by striking one stone against another. The first blade cut my finger more than the meat. The fifth one cut well. "
               "I tied one to a branch with fibre. Now I have a spear, and a little less fear.",
               "Aprendí a tallar sílex golpeando una piedra contra otra. La primera hoja me cortó más el dedo que la carne. La quinta cortó bien. "
               "Até una a una rama con fibra. Ahora tengo una lanza, y un poco menos de miedo.")),
    dict(id="c1_day_17", day=17, kind="species", species="velociraptor",
         text=("Os pequenos de penas caçam em grupo. Um aparece na frente, faz barulho, e os outros vêm pelos lados. "
               "Se você vir um sozinho, procure os outros. Eles nunca estão sozinhos. Eles têm medo do grande.",
               "The small feathered ones hunt in groups. One shows up in front and makes noise, and the others come from the sides. "
               "If you see one alone, look for the others. They are never alone. They are afraid of the big one.",
               "Los pequeños con plumas cazan en grupo. Uno aparece delante y hace ruido, y los otros llegan por los lados. "
               "Si ves uno solo, busca a los demás. Nunca están solos. Le tienen miedo al grande.")),
    dict(id="c1_day_41", day=41, kind="species", species="tyrannosaurus",
         text=("Os bicos-de-pato andam em fila pela margem todo fim de tarde, sempre no mesmo caminho. Atrás da fila, sempre a uns cem passos, vem o grande. "
               "Ele não corre atrás deles. Ele espera o que fica para trás.",
               "The duckbills walk in a line along the shore every evening, always on the same path. Behind the line, always about a hundred steps back, comes the big one. "
               "He does not chase them. He waits for whoever falls behind.",
               "Los picos de pato caminan en fila por la orilla cada tarde, siempre por el mismo camino. Detrás de la fila, siempre a unos cien pasos, viene el grande. "
               "No los persigue. Espera al que se queda atrás.")),
    dict(id="c1_day_88", day=88, kind="species", species="triceratops",
         text=("Nunca chegue entre um tricerátops e o filhote. Eu vi um derrubar uma árvore só porque ela estava no caminho. "
               "Mas se você chegar devagar, de mãos abertas, com samambaia, ele deixa. Eles gostam de samambaia mais do que de qualquer coisa.",
               "Never get between a triceratops and its calf. I saw one knock down a tree just because it was in the way. "
               "But if you come slowly, with open hands and ferns, it lets you near. They love ferns more than anything.",
               "Nunca te pongas entre un tricerátops y su cría. Vi a uno derribar un árbol solo porque estaba en el camino. "
               "Pero si llegas despacio, con las manos abiertas y helechos, te deja acercarte. Les gustan los helechos más que nada.")),
    dict(id="c1_day_150", day=150, kind="diary",
         text=("Achei ossos na rocha do barranco. Ossos de animais que eu não vi vivos aqui, com placas nas costas e pescoços enormes. "
               "Bichos do Jurássico, milhões de anos antes de mim. Penso em quem vai achar os meus ossos um dia, e escrevo mais rápido.",
               "I found bones in the rock of the ravine. Bones of animals I have not seen alive here, with plates on their backs and enormous necks. "
               "Jurassic animals, millions of years before me. I think of whoever will find my bones one day, and I write faster.",
               "Encontré huesos en la roca del barranco. Huesos de animales que no he visto vivos aquí, con placas en la espalda y cuellos enormes. "
               "Animales del Jurásico, millones de años antes que yo. Pienso en quien encontrará mis huesos algún día, y escribo más rápido.")),
    dict(id="c1_day_212", day=212, kind="species", species="ankylosaurus",
         text=("O blindado não corre. Ele nem precisa. Vi um raptor pular nas costas dele e escorregar nas placas. "
               "Depois a cauda veio, de lado, como um machado. Não chegue por trás dele. Nunca.",
               "The armoured one does not run. It does not need to. I saw a raptor jump on its back and slide off the plates. "
               "Then the tail came, sideways, like an axe. Do not approach it from behind. Ever.",
               "El acorazado no corre. Ni lo necesita. Vi a un raptor saltar sobre su espalda y resbalar en las placas. "
               "Después llegó la cola, de lado, como un hacha. No te acerques por detrás. Nunca.")),
    dict(id="c1_day_340", day=340, kind="diary",
         text=("Hoje o Mate comeu da minha mão. Três meses de samambaia e paciência. Ele me segue até o rio e dorme do lado da fogueira. "
               "Pela primeira vez desde o salto, não me sinto sozinha.",
               "Today Mate ate from my hand. Three months of ferns and patience. He follows me to the river and sleeps by the fire. "
               "For the first time since the jump, I do not feel alone.",
               "Hoy Mate comió de mi mano. Tres meses de helechos y paciencia. Me sigue hasta el río y duerme junto al fuego. "
               "Por primera vez desde el salto, no me siento sola.")),
    dict(id="c1_day_610", day=610, kind="species", species="spinosaurus",
         text=("No rio grande mora um que tem uma vela nas costas. Ele fica parado na água até o peixe esquecer que ele existe. "
               "Ele não sai da água atrás de mim. Mas eu também não entro mais no rio.",
               "In the big river lives one with a sail on its back. It stands still in the water until the fish forget it exists. "
               "It does not leave the water to chase me. But I do not go into the river any more.",
               "En el río grande vive uno con una vela en la espalda. Se queda quieto en el agua hasta que los peces olvidan que existe. "
               "No sale del agua para perseguirme. Pero yo tampoco entro más al río.")),
    dict(id="c1_day_1203", day=1203, kind="diary",
         text=("As estrelas caem toda noite agora. Achei âmbar brilhando numa rocha que não devia ter âmbar nenhum, e debaixo dela uma pegada de três dedos, pequena, "
               "de um animal que eu só conheço dos livros do Triássico. A Fenda está trazendo o passado para cá. E eu acho que fui eu que abri.",
               "The stars fall every night now. I found amber glowing in a rock that should have no amber at all, and under it a three-toed footprint, small, "
               "from an animal I only know from Triassic books. The Rift is bringing the past here. And I think I am the one who opened it.",
               "Las estrellas caen todas las noches ahora. Encontré ámbar brillando en una roca que no debería tener ámbar, y debajo una huella de tres dedos, pequeña, "
               "de un animal que solo conozco por los libros del Triásico. La Grieta está trayendo el pasado aquí. Y creo que fui yo quien la abrió.")),
]
PAGE_TITLE = ("Dia %s", "Day %s", "Día %s")

# ------------------------------------------------------------------ Field Guide texts per species
# sci: science box (when it lived, where the fossils are, real size). behavior and taming unlock at "studied",
# utility and Katarina's note at "tamed".
GUIDE = {
    "tyrannosaurus": dict(
        sci=("Viveu há 68 a 66 milhões de anos, no oeste da América do Norte. Até 12 m de comprimento e 8 toneladas: uma das mordidas mais fortes que já existiram.",
             "Lived 68 to 66 million years ago in western North America. Up to 12 m long and 8 tonnes: one of the strongest bites that ever existed.",
             "Vivió hace 68 a 66 millones de años en el oeste de América del Norte. Hasta 12 m de largo y 8 toneladas: una de las mordidas más fuertes que existieron."),
        behavior=("Caçador solitário de campos e florestas abertas. Ruge quando escolhe uma presa e persegue jogadores e animais grandes. Os raptores fogem dele.",
                  "Solitary hunter of open fields and forests. It roars when it picks a prey and chases players and large animals. Raptors flee from it.",
                  "Cazador solitario de campos y bosques abiertos. Ruge cuando elige una presa y persigue a jugadores y animales grandes. Los raptores huyen de él."),
        taming=("Só se doma desde o ovo ou como filhote alimentado à mão. Gosta de carne crua: boi, porco e carneiro.",
                "Can only be tamed from an egg or as a hand-fed baby. Likes raw meat: beef, pork and mutton.",
                "Solo se doma desde el huevo o como cría alimentada a mano. Le gusta la carne cruda: vaca, cerdo y cordero."),
        utility=("Montaria de combate. Com sela, é o animal mais forte que você pode montar.",
                 "Combat mount. With a saddle, it is the strongest animal you can ride.",
                 "Montura de combate. Con silla, es el animal más fuerte que puedes montar."),
        note=("Ele não corre atrás. Ele espera o que fica para trás.",
              "He does not chase. He waits for whoever falls behind.",
              "No persigue. Espera al que se queda atrás.")),
    "spinosaurus": dict(
        sci=("Viveu há cerca de 95 milhões de anos, nos rios do norte da África. Uns 14 m de comprimento, com uma vela de espinhos nas costas.",
             "Lived about 95 million years ago in the rivers of North Africa. About 14 m long, with a sail of spines on its back.",
             "Vivió hace unos 95 millones de años en los ríos del norte de África. Unos 14 m de largo, con una vela de espinas en la espalda."),
        behavior=("Vive em rios e pântanos, nada bem e não se afoga. Caça peixes e quem estiver na água.",
                  "Lives in rivers and swamps, swims well and does not drown. Hunts fish and whoever is in the water.",
                  "Vive en ríos y pantanos, nada bien y no se ahoga. Caza peces y a quien esté en el agua."),
        taming=("Só se doma desde o ovo ou como filhote. Gosta de peixe: bacalhau, salmão e peixe tropical.",
                "Can only be tamed from an egg or as a baby. Likes fish: cod, salmon and tropical fish.",
                "Solo se doma desde el huevo o como cría. Le gusta el pescado: bacalao, salmón y pez tropical."),
        utility=("Um guarda para a margem do rio. Em breve, uma montaria anfíbia.",
                 "A guard for the riverbank. Soon, an amphibious mount.",
                 "Un guardián para la orilla del río. Pronto, una montura anfibia."),
        note=("Ele fica parado até o peixe esquecer que ele existe.",
              "It stands still until the fish forget it exists.",
              "Se queda quieto hasta que los peces olvidan que existe.")),
    "dilophosaurus": dict(
        sci=("Viveu há cerca de 190 milhões de anos, no Jurássico Inferior do Arizona. Uns 7 m de comprimento, com duas cristas finas na cabeça.",
             "Lived about 190 million years ago, in the Early Jurassic of Arizona. About 7 m long, with two thin crests on its head.",
             "Vivió hace unos 190 millones de años, en el Jurásico Inferior de Arizona. Unos 7 m de largo, con dos crestas finas en la cabeza."),
        behavior=("Um vazamento da Fenda: não é desta era. Mostra as cristas antes de atacar e caça animais pequenos.",
                  "A leak from the Rift: it does not belong to this era. It flashes its crests before attacking and hunts small animals.",
                  "Una fuga de la Grieta: no es de esta era. Muestra las crestas antes de atacar y caza animales pequeños."),
        taming=("Só se doma desde o ovo ou como filhote. Gosta de frango, coelho, carneiro e porco.",
                "Can only be tamed from an egg or as a baby. Likes chicken, rabbit, mutton and pork.",
                "Solo se doma desde el huevo o como cría. Le gusta el pollo, el conejo, el cordero y el cerdo."),
        utility=("Guarda da base: ataca quem ataca você.",
                 "Base guard: it attacks whoever attacks you.",
                 "Guardián de la base: ataca a quien te ataca."),
        note=("As cristas ficam vermelhas quando ele está com raiva. Ou quando está feliz. Ainda não sei a diferença.",
              "The crests turn red when it is angry. Or when it is happy. I still do not know the difference.",
              "Las crestas se ponen rojas cuando está enojado. O cuando está feliz. Todavía no sé la diferencia.")),
    "velociraptor": dict(
        sci=("Viveu há 75 a 71 milhões de anos, nos desertos da Mongólia. Tinha penas e só uns 2 m de comprimento, quase tudo cauda.",
             "Lived 75 to 71 million years ago in the deserts of Mongolia. It had feathers and was only about 2 m long, mostly tail.",
             "Vivió hace 75 a 71 millones de años en los desiertos de Mongolia. Tenía plumas y solo unos 2 m de largo, casi todo cola."),
        behavior=("Caça em bando: quando um escolhe um alvo, os outros por perto vêm junto. Pula na presa e foge do T. rex.",
                  "Hunts in packs: when one picks a target, the others nearby join in. Leaps at its prey and flees from T. rex.",
                  "Caza en manada: cuando uno elige un objetivo, los demás cercanos se unen. Salta sobre su presa y huye del T. rex."),
        taming=("Só se doma desde o ovo ou como filhote. Come quase qualquer carne crua.",
                "Can only be tamed from an egg or as a baby. Eats almost any raw meat.",
                "Solo se doma desde el huevo o como cría. Come casi cualquier carne cruda."),
        utility=("Companheiro de caça: luta ao seu lado.",
                 "Hunting companion: it fights by your side.",
                 "Compañero de caza: lucha a tu lado."),
        note=("Se você vir um sozinho, procure os outros.",
              "If you see one alone, look for the others.",
              "Si ves uno solo, busca a los demás.")),
    "compsognathus": dict(
        sci=("Viveu há cerca de 150 milhões de anos, nas ilhas do Jurássico da Alemanha e da França. Do tamanho de uma galinha.",
             "Lived about 150 million years ago on the Jurassic islands of Germany and France. The size of a chicken.",
             "Vivió hace unos 150 millones de años en las islas jurásicas de Alemania y Francia. Del tamaño de una gallina."),
        behavior=("Anda em grupos, foge de jogadores e come restos. Mas se você machucar um, o grupo inteiro vem.",
                  "Lives in groups, avoids players and eats scraps. But if you hurt one, the whole group comes.",
                  "Vive en grupos, huye de los jugadores y come restos. Pero si hieres a uno, viene todo el grupo."),
        taming=("Domestica como um gato: dê peixe ou frango cru na mão.",
                "Tamed like a cat: hand-feed it fish or raw chicken.",
                "Se domestica como un gato: dale pescado o pollo crudo en la mano."),
        utility=("Mascote. Em breve vai no ombro e avisa quando há perigo.",
                 "A pet. Soon it will ride on your shoulder and warn you of danger.",
                 "Mascota. Pronto irá en tu hombro y te avisará del peligro."),
        note=("Roubou o meu peixe três vezes. Na quarta eu dei o peixe para ele.",
              "It stole my fish three times. The fourth time I gave it the fish.",
              "Me robó el pescado tres veces. A la cuarta se lo di.")),
    "triceratops": dict(
        sci=("Viveu há 68 a 66 milhões de anos, no oeste da América do Norte. Uns 9 m de comprimento, três chifres e um escudo de osso no pescoço.",
             "Lived 68 to 66 million years ago in western North America. About 9 m long, three horns and a bony shield on its neck.",
             "Vivió hace 68 a 66 millones de años en el oeste de América del Norte. Unos 9 m de largo, tres cuernos y un escudo de hueso en el cuello."),
        behavior=("Pacífico, mas defende o bando com investidas de chifre. Nunca chegue entre um adulto e o filhote.",
                  "Peaceful, but defends the herd with horn charges. Never get between an adult and its calf.",
                  "Pacífico, pero defiende la manada con embestidas de cuerno. Nunca te pongas entre un adulto y su cría."),
        taming=("Dê comida na mão até ele aceitar. Gosta de samambaia e trigo.",
                "Hand-feed it until it accepts you. Likes ferns and wheat.",
                "Dale comida en la mano hasta que te acepte. Le gustan los helechos y el trigo."),
        utility=("Montaria tanque: forte e difícil de derrubar.",
                 "Tank mount: strong and hard to bring down.",
                 "Montura tanque: fuerte y difícil de derribar."),
        note=("Eles gostam de samambaia mais do que de qualquer coisa.",
              "They love ferns more than anything.",
              "Les gustan los helechos más que nada.")),
    "stegosaurus": dict(
        sci=("Viveu há 155 a 150 milhões de anos, no Jurássico dos Estados Unidos e de Portugal. Uns 9 m de comprimento, placas nas costas e espinhos na cauda.",
             "Lived 155 to 150 million years ago, in the Jurassic of the United States and Portugal. About 9 m long, plates on its back and spikes on its tail.",
             "Vivió hace 155 a 150 millones de años, en el Jurásico de Estados Unidos y Portugal. Unos 9 m de largo, placas en la espalda y púas en la cola."),
        behavior=("Um vazamento da Fenda. Lento e calmo, mas a cauda de espinhos acerta com força quem ataca.",
                  "A leak from the Rift. Slow and calm, but its spiked tail hits hard whoever attacks.",
                  "Una fuga de la Grieta. Lento y tranquilo, pero su cola de púas golpea fuerte a quien ataca."),
        taming=("Dê comida na mão. Gosta de samambaia, melancia e trigo.",
                "Hand-feed it. Likes ferns, melon and wheat.",
                "Dale comida en la mano. Le gustan los helechos, la sandía y el trigo."),
        utility=("Guarda pacífico. Em breve, montaria.",
                 "A peaceful guard. Soon, a mount.",
                 "Un guardián tranquilo. Pronto, una montura."),
        note=("As placas ficam rosadas no sol da manhã. Acho que é assim que ele se esquenta.",
              "The plates turn pink in the morning sun. I think that is how it warms up.",
              "Las placas se ponen rosadas con el sol de la mañana. Creo que así se calienta.")),
    "ankylosaurus": dict(
        sci=("Viveu há 68 a 66 milhões de anos, na América do Norte. Uns 7 m de comprimento, coberto de placas de osso, com uma clava na cauda.",
             "Lived 68 to 66 million years ago in North America. About 7 m long, covered in bony plates, with a club on its tail.",
             "Vivió hace 68 a 66 millones de años en América del Norte. Unos 7 m de largo, cubierto de placas de hueso, con una maza en la cola."),
        behavior=("Um tanque vivo. Não foge: gira e bate com a clava da cauda. Quase nada atravessa a armadura.",
                  "A living tank. It does not flee: it turns and swings its tail club. Almost nothing gets through its armour.",
                  "Un tanque vivo. No huye: gira y golpea con la maza de la cola. Casi nada atraviesa su armadura."),
        taming=("Dê comida na mão. Gosta de samambaia e frutas silvestres.",
                "Hand-feed it. Likes ferns and sweet berries.",
                "Dale comida en la mano. Le gustan los helechos y las bayas."),
        utility=("Defensor resistente. Em breve, montaria que quebra pedra.",
                 "A tough defender. Soon, a mount that breaks stone.",
                 "Un defensor resistente. Pronto, una montura que rompe piedra."),
        note=("Não chegue por trás dele. Nunca.",
              "Do not approach it from behind. Ever.",
              "No te acerques por detrás. Nunca.")),
    "brachiosaurus": dict(
        sci=("Viveu há cerca de 154 milhões de anos, no Jurássico da América do Norte. Até 22 m de comprimento e a cabeça a mais de 12 m do chão.",
             "Lived about 154 million years ago in the Jurassic of North America. Up to 22 m long, with its head more than 12 m off the ground.",
             "Vivió hace unos 154 millones de años en el Jurásico de América del Norte. Hasta 22 m de largo y la cabeza a más de 12 m del suelo."),
        behavior=("Um vazamento da Fenda. Come folhas do alto das árvores e só luta se for machucado.",
                  "A leak from the Rift. Eats leaves from the treetops and only fights if hurt.",
                  "Una fuga de la Grieta. Come hojas de lo alto de los árboles y solo pelea si lo hieren."),
        taming=("Dê folhas na mão, de qualquer árvore.",
                "Hand-feed it leaves, from any tree.",
                "Dale hojas en la mano, de cualquier árbol."),
        utility=("A montaria mais alta do jogo. Em breve, sela de plataforma.",
                 "The tallest mount in the game. Soon, a platform saddle.",
                 "La montura más alta del juego. Pronto, silla de plataforma."),
        note=("Lá de cima dá para ver o rio inteiro. E o rio inteiro vê você.",
              "From up there you can see the whole river. And the whole river sees you.",
              "Desde arriba se ve todo el río. Y todo el río te ve a ti.")),
    "parasaurolophus": dict(
        sci=("Viveu há 76 a 73 milhões de anos, na América do Norte. Uns 9,5 m de comprimento, com uma crista oca que funcionava como trombeta.",
             "Lived 76 to 73 million years ago in North America. About 9.5 m long, with a hollow crest that worked like a trumpet.",
             "Vivió hace 76 a 73 millones de años en América del Norte. Unos 9,5 m de largo, con una cresta hueca que funcionaba como trompeta."),
        behavior=("Anda em bando e foge do perigo. O chamado da crista avisa os outros.",
                  "Lives in herds and flees from danger. The call of its crest warns the others.",
                  "Vive en manada y huye del peligro. El llamado de su cresta avisa a los demás."),
        taming=("Dê comida na mão com paciência. Gosta de trigo, samambaia e frutas silvestres.",
                "Hand-feed it patiently. Likes wheat, ferns and sweet berries.",
                "Dale comida en la mano con paciencia. Le gustan el trigo, los helechos y las bayas."),
        utility=("Montaria rápida e fácil, boa para começar.",
                 "A fast and easy mount, good to start with.",
                 "Una montura rápida y fácil, buena para empezar."),
        note=("O Mate é um deles. Ele dorme do lado da fogueira.",
              "Mate is one of them. He sleeps by the fire.",
              "Mate es uno de ellos. Duerme junto al fuego.")),
    "pachycephalosaurus": dict(
        sci=("Viveu há 70 a 66 milhões de anos, na América do Norte. Uns 4,5 m de comprimento, com uma cúpula de osso de 25 cm de espessura na cabeça.",
             "Lived 70 to 66 million years ago in North America. About 4.5 m long, with a bony dome 25 cm thick on its head.",
             "Vivió hace 70 a 66 millones de años en América del Norte. Unos 4,5 m de largo, con una cúpula de hueso de 25 cm de grosor en la cabeza."),
        behavior=("Calmo até ser provocado. Aí dá cabeçadas que jogam longe.",
                  "Calm until provoked. Then it headbutts hard enough to send you flying.",
                  "Tranquilo hasta que lo provocan. Entonces da cabezazos que te lanzan lejos."),
        taming=("Dê frutas na mão: frutas silvestres, frutas brilhantes ou maçã.",
                "Hand-feed it fruit: sweet berries, glow berries or apples.",
                "Dale fruta en la mano: bayas, bayas luminosas o manzanas."),
        utility=("Derruba inimigos com cabeçadas.",
                 "Knocks enemies down with headbutts.",
                 "Derriba enemigos con cabezazos."),
        note=("Dois machos se enfrentaram a manhã inteira. O barulho parecia de troncos batendo.",
              "Two males fought the whole morning. It sounded like logs crashing.",
              "Dos machos pelearon toda la mañana. Sonaba como troncos chocando.")),
    "gallimimus": dict(
        sci=("Viveu há cerca de 70 milhões de anos, na Mongólia. Uns 6 m de comprimento, parecido com um avestruz, com bico sem dentes.",
             "Lived about 70 million years ago in Mongolia. About 6 m long, ostrich-like, with a toothless beak.",
             "Vivió hace unos 70 millones de años en Mongolia. Unos 6 m de largo, parecido a un avestruz, con pico sin dientes."),
        behavior=("O dinossauro mais rápido. Anda em bandos que fogem de jogadores e predadores.",
                  "The fastest dinosaur. Lives in flocks that flee from players and predators.",
                  "El dinosaurio más rápido. Vive en bandadas que huyen de jugadores y depredadores."),
        taming=("Dê comida na mão: sementes, frutas silvestres ou maçã.",
                "Hand-feed it: seeds, sweet berries or apples.",
                "Dale comida en la mano: semillas, bayas o manzanas."),
        utility=("A montaria terrestre mais rápida.",
                 "The fastest land mount.",
                 "La montura terrestre más rápida."),
        note=("Tentei correr atrás de um. Ele voltou para ver se eu estava bem.",
              "I tried to run after one. It came back to see if I was all right.",
              "Intenté correr detrás de uno. Volvió para ver si yo estaba bien.")),
    "maiasaura": dict(
        sci=("Viveu há cerca de 76 milhões de anos em Montana, nos Estados Unidos. Uns 9 m, bico de pato e uma cristinha maciça na frente dos olhos. Foi achada em colônias inteiras de ninhos, com ovos, filhotes e jovens: o nome quer dizer \"lagarta boa mãe\".",
             "Lived about 76 million years ago in Montana, USA. About 9 m, a duck bill and a small solid crest in front of the eyes. Found in whole colonies of nests, with eggs, hatchlings and juveniles: the name means \"good mother lizard\".",
             "Vivió hace unos 76 millones de años en Montana, Estados Unidos. Unos 9 m, pico de pato y una pequeña cresta maciza delante de los ojos. Se encontró en colonias enteras de nidos, con huevos, crías y jóvenes: el nombre significa \"lagarta buena madre\"."),
        behavior=("Vive em bandos nas planícies e savanas. Filhotes de qualquer espécie perto de um adulto crescem duas vezes mais rápido. Foge do perigo, mas se defende.",
                  "Lives in herds on plains and savannas. Babies of any species near an adult grow twice as fast. It flees from danger, but defends itself.",
                  "Vive en manadas en llanuras y sabanas. Las crías de cualquier especie cerca de un adulto crecen el doble de rápido. Huye del peligro, pero se defiende."),
        taming=("Dê comida na mão: trigo, samambaia ou frutas silvestres.",
                "Hand-feed it: wheat, ferns or sweet berries.",
                "Dale comida en la mano: trigo, helechos o bayas dulces."),
        utility=("Babá do criadouro: deixe uma perto dos filhotes. Também é montaria.",
                 "Nursery nanny: keep one near the babies. Also a mount.",
                 "Niñera del criadero: deja una cerca de las crías. También es montura."),
        note=("Um filhote de tricerátops se perdeu no bando delas. Ninguém pareceu se importar. Ele foi alimentado igual aos outros.",
              "A baby triceratops got lost in their herd. Nobody seemed to mind. It was fed like the others.",
              "Una cría de triceratops se perdió en su manada. A nadie pareció importarle. La alimentaron igual que a las demás.")),
    "pteranodon": dict(
        sci=("Viveu há cerca de 85 milhões de anos sobre o mar interior da América do Norte. Não é um dinossauro: é um pterossauro, um réptil voador. Asas de 6 a 7 m, bico sem dentes e uma crista longa para trás.",
             "Lived about 85 million years ago over the inland sea of North America. Not a dinosaur: a pterosaur, a flying reptile. Wings of 6 to 7 m, a toothless beak and a long crest pointing back.",
             "Vivió hace unos 85 millones de años sobre el mar interior de América del Norte. No es un dinosaurio: es un pterosaurio, un reptil volador. Alas de 6 a 7 m, pico sin dientes y una cresta larga hacia atrás."),
        behavior=("Vive nas praias e costões. Plana mais do que bate as asas e pesca na beira da água. Não ataca ninguém, mas se defende.",
                  "Lives on beaches and rocky shores. Glides more than it flaps and fishes at the water's edge. It attacks no one, but it defends itself.",
                  "Vive en playas y costas rocosas. Planea más de lo que aletea y pesca en la orilla. No ataca a nadie, pero se defiende."),
        taming=("Dê peixe na mão: bacalhau, salmão ou peixe tropical. Com sela, voa: pule para decolar, olhe para onde quer ir e segure para frente. Solte para planar.",
                "Hand-feed it fish: cod, salmon or tropical fish. With a saddle it flies: jump to take off, look where you want to go and hold forward. Let go to glide.",
                "Dale pescado en la mano: bacalao, salmón o pez tropical. Con silla, vuela: salta para despegar, mira hacia donde quieres ir y mantén adelante. Suelta para planear."),
        utility=("A primeira montaria voadora. Leve e rápida, mas não carrega peso.",
                 "The first flying mount. Light and fast, but it carries no load.",
                 "La primera montura voladora. Ligera y rápida, pero no carga peso."),
        note=("A crista não serve para voar. Acho que serve para ser vista. Funcionou comigo.",
              "The crest is not for flying. I think it is for being seen. It worked on me.",
              "La cresta no sirve para volar. Creo que sirve para ser vista. Conmigo funcionó.")),
    "mosasaurus": dict(
        sci=("Viveu há cerca de 70 milhões de anos nos mares da Europa e da América do Norte. Não é um dinossauro: é um lagarto marinho, parente dos varanos e das cobras. Uns 15 m, nadadeiras no lugar das patas e uma cauda com barbatana em meia-lua. Paria filhotes vivos, na água.",
             "Lived about 70 million years ago in the seas of Europe and North America. Not a dinosaur: a marine lizard, related to monitor lizards and snakes. About 15 m, flippers instead of legs and a tail with a crescent fin. It gave birth to live young, in the water.",
             "Vivió hace unos 70 millones de años en los mares de Europa y América del Norte. No es un dinosaurio: es un lagarto marino, pariente de los varanos y las serpientes. Unos 15 m, aletas en lugar de patas y una cola con aleta en media luna. Paría crías vivas, en el agua."),
        behavior=("Vive no oceano profundo. Caça tudo o que está na água: peixes, lulas, golfinhos, tartarugas e quem estiver nadando ou de barco. Encalhado na terra, fica fraco e seca.",
                  "Lives in the deep ocean. Hunts everything in the water: fish, squid, dolphins, turtles and whoever is swimming or in a boat. Stranded on land it is weak and dries out.",
                  "Vive en el océano profundo. Caza todo lo que está en el agua: peces, calamares, delfines, tortugas y a quien esté nadando o en barco. Varado en tierra se debilita y se seca."),
        taming=("Ainda não se sabe domar. Por enquanto, fique longe do mar fundo.",
                "Nobody knows how to tame it yet. For now, stay away from deep water.",
                "Todavía no se sabe domarlo. Por ahora, aléjate del mar profundo."),
        utility=("Nenhuma. É o motivo de atravessar o mar pela costa.",
                 "None. It is the reason to cross the sea along the coast.",
                 "Ninguna. Es el motivo para cruzar el mar por la costa."),
        note=("Vi a sombra passar debaixo do barco. Era maior que o barco. Remei até a praia sem olhar para trás.",
              "I saw the shadow pass under the boat. It was bigger than the boat. I rowed to the beach without looking back.",
              "Vi la sombra pasar debajo del bote. Era más grande que el bote. Remé hasta la playa sin mirar atrás.")),
}

ERAS = {
    "late_cretaceous": ("Cretáceo Superior", "Late Cretaceous", "Cretácico Superior"),
    "early_cretaceous": ("Cretáceo Inferior", "Early Cretaceous", "Cretácico Inferior"),
    "jurassic": ("Jurássico", "Jurassic", "Jurásico"),
    "triassic": ("Triássico", "Triassic", "Triásico"),
}
DIETS = {
    "carnivore": ("Carnívoro", "Carnivore", "Carnívoro"),
    "piscivore": ("Piscívoro (peixe)", "Piscivore (fish)", "Piscívoro (peces)"),
    "herbivore": ("Herbívoro", "Herbivore", "Herbívoro"),
    "omnivore": ("Onívoro", "Omnivore", "Omnívoro"),
}

# ------------------------------------------------------------------ Field Journal objectives (Chapter 1)
OBJECTIVES = {
    "shelter": (("Um teto de palha", "A thatch roof", "Un techo de paja"),
                ("Coloque 16 blocos de palha (palha, escada ou laje de palha).", "Place 16 thatch blocks (thatch, thatch stairs or slabs).",
                 "Coloca 16 bloques de paja (paja, escaleras o losas de paja).")),
    "first_spear": (("A primeira lança", "The first spear", "La primera lanza"),
                    ("Faça uma lança: sílex, fio e graveto.", "Craft a spear: flint, string and a stick.", "Fabrica una lanza: sílex, hilo y un palo.")),
    "rift_storm": (("Céu de âmbar", "Amber sky", "Cielo de ámbar"),
                   ("Sobreviva a uma Tempestade da Fenda. Elas ainda não começaram.", "Survive a Rift Storm. They have not started yet.",
                    "Sobrevive a una Tormenta de la Grieta. Todavía no han empezado.")),
    "study_five": (("Cinco espécies", "Five species", "Cinco especies"),
                   ("Estude 5 espécies até o nível \"Estudado\" do Guia.", "Study 5 species up to the \"Studied\" level of the Guide.",
                    "Estudia 5 especies hasta el nivel \"Estudiado\" de la Guía.")),
    "first_fossil": (("Osso na pedra", "Bone in the stone", "Hueso en la piedra"),
                     ("Escave um fóssil de Rocha Fossilífera com o Pincel de Pelo ou o Cinzel de Sílex.",
                      "Dig a fossil out of Fossil Rock with the Hair Brush or the Flint Chisel.",
                      "Excava un fósil de la Roca Fosilífera con el Pincel de Pelo o el Cincel de Sílex.")),
    "research_table": (("Mesa de trabalho", "At the table", "En la mesa"),
                       ("Estude um fóssil ou um esboço na Mesa de Pesquisa.", "Study a fossil or a sketch at the Research Table.",
                        "Estudia un fósil o un boceto en la Mesa de Investigación.")),
    "tame_herbivore": (("Amizade", "Friendship", "Amistad"),
                       ("Domestique um herbívoro dando comida na mão.", "Tame a herbivore by hand-feeding it.", "Domestica un herbívoro dándole comida en la mano.")),
    "hatch_egg": (("Nasceu", "Hatched", "Nació"),
                  ("Fique perto de um ovo de dinossauro quando ele chocar.", "Stay near a dinosaur egg when it hatches.",
                   "Quédate cerca de un huevo de dinosaurio cuando eclosione.")),
    "ride": (("Na sela", "In the saddle", "En la silla"),
             ("Monte uma criatura domesticada com sela.", "Ride a tamed creature with a saddle.", "Monta una criatura domesticada con silla.")),
    "katarina_camps": (("Rastros dela", "Her tracks", "Sus rastros"),
                       ("Ache 2 acampamentos da Katarina. Ainda não há acampamentos no mundo.", "Find 2 of Katarina's camps. There are no camps in the world yet.",
                        "Encuentra 2 campamentos de Katarina. Todavía no hay campamentos en el mundo.")),
    "rift_ruin": (("Ruína da Fenda", "Rift Ruin", "Ruina de la Grieta"),
                  ("Ache uma Ruína da Fenda. Elas ainda não aparecem no mundo.", "Find a Rift Ruin. They do not appear in the world yet.",
                   "Encuentra una Ruina de la Grieta. Todavía no aparecen en el mundo.")),
    "migration": (("A grande fila", "The long line", "La gran fila"),
                  ("Veja uma migração de bicos-de-pato. Elas ainda não acontecem.", "Watch a duckbill migration. They do not happen yet.",
                   "Observa una migración de picos de pato. Todavía no ocurren.")),
}
THEMES = {
    "survival": ("Sobrevivência", "Survival", "Supervivencia"),
    "science": ("Ciência", "Science", "Ciencia"),
    "taming": ("Domesticação", "Taming", "Domesticación"),
    "exploration": ("Exploração", "Exploration", "Exploración"),
}

# ------------------------------------------------------------------ notebook screen, messages, tooltips
UI = {
    "notebook.terrassic.title": ("Caderno de Campo", "Field Notebook", "Cuaderno de Campo"),
    "notebook.terrassic.tab.journal": ("Diário", "Journal", "Diario"),
    "notebook.terrassic.tab.guide": ("Guia", "Guide", "Guía"),
    "notebook.terrassic.tab.katarina": ("Katarina", "Katarina", "Katarina"),
    "notebook.terrassic.tab.report": ("Relatório", "Report", "Informe"),
    "notebook.terrassic.journal.header": ("Capítulo 1: Ecos do Fim", "Chapter 1: Echoes of the End", "Capítulo 1: Ecos del Fin"),
    "notebook.terrassic.journal.intro": ("Complete 2 de 3 objetivos de cada tema. A ordem é sua.",
                                         "Complete 2 of 3 objectives in each theme. Any order you like.",
                                         "Completa 2 de 3 objetivos de cada tema. En el orden que quieras."),
    "notebook.terrassic.journal.theme": ("%s (%s de 2)", "%s (%s of 2)", "%s (%s de 2)"),
    "notebook.terrassic.guide.count": ("%s de %s espécies registradas", "%s of %s species recorded", "%s de %s especies registradas"),
    "notebook.terrassic.guide.unknown": ("???", "???", "???"),
    "notebook.terrassic.guide.unknown_hint": ("Ainda não registrada. Ache um fóssil, veja uma de perto ou faça um esboço.",
                                              "Not recorded yet. Find a fossil, see one up close or make a sketch.",
                                              "Aún no registrada. Encuentra un fósil, mira una de cerca o haz un boceto."),
    "notebook.terrassic.guide.era": ("Era: %s", "Era: %s", "Era: %s"),
    "notebook.terrassic.guide.diet": ("Dieta: %s", "Diet: %s", "Dieta: %s"),
    "notebook.terrassic.guide.length": ("Tamanho real: %s m", "Real length: %s m", "Tamaño real: %s m"),
    "notebook.terrassic.guide.points": ("Pontos de estudo: %s de %s", "Study points: %s of %s", "Puntos de estudio: %s de %s"),
    "notebook.terrassic.guide.level.1": ("Silhueta", "Silhouette", "Silueta"),
    "notebook.terrassic.guide.level.2": ("Avistado", "Sighted", "Avistado"),
    "notebook.terrassic.guide.level.3": ("Estudado", "Studied", "Estudiado"),
    "notebook.terrassic.guide.level.4": ("Domesticado", "Tamed", "Domesticado"),
    "notebook.terrassic.guide.silhouette_hint": ("Só conheço os ossos. Preciso ver um vivo.", "I only know its bones. I need to see a living one.",
                                                 "Solo conozco sus huesos. Necesito ver uno vivo."),
    "notebook.terrassic.guide.study_hint": ("Estude mais para saber como ele vive: esboço (2 pontos), fóssil (1) ou derrotar um (3).",
                                            "Study more to learn how it lives: a sketch (2 points), a fossil (1) or defeating one (3).",
                                            "Estudia más para saber cómo vive: un boceto (2 puntos), un fósil (1) o derrotar uno (3)."),
    "notebook.terrassic.guide.tame_hint": ("Domestique um para saber mais.", "Tame one to learn more.", "Domestica uno para saber más."),
    "notebook.terrassic.guide.behavior": ("Comportamento", "Behaviour", "Comportamiento"),
    "notebook.terrassic.guide.taming": ("Como domar", "How to tame", "Cómo domar"),
    "notebook.terrassic.guide.utility": ("Utilidade", "Use", "Utilidad"),
    "notebook.terrassic.guide.note": ("Nota da Katarina", "Katarina's note", "Nota de Katarina"),
    "notebook.terrassic.guide.bonus": ("Estudado: domar fica mais fácil e você acerta os pontos fracos (+20% de dano).",
                                       "Studied: taming is easier and you hit its weak spots (+20% damage).",
                                       "Estudiado: domar es más fácil y golpeas sus puntos débiles (+20% de daño)."),
    "notebook.terrassic.guide.rideable": ("Montável com sela", "Rideable with a saddle", "Se puede montar con silla"),
    "notebook.terrassic.guide.egg_only": ("Só se doma desde filhote", "Only tamed as a baby", "Solo se doma de cría"),
    "notebook.terrassic.katarina.empty": ("Nenhuma página encontrada ainda. Procure páginas soltas em baús antigos.",
                                          "No pages found yet. Look for loose pages in old chests.",
                                          "Aún no hay páginas. Busca páginas sueltas en cofres antiguos."),
    "notebook.terrassic.katarina.count": ("%s de %s páginas", "%s of %s pages", "%s de %s páginas"),
    "notebook.terrassic.prev": ("< Anterior", "< Previous", "< Anterior"),
    "notebook.terrassic.next": ("Próxima >", "Next >", "Siguiente >"),
    "notebook.terrassic.page": ("%s / %s", "%s / %s", "%s / %s"),
    "intro.terrassic.skip": ("Esc para pular", "Esc to skip", "Esc para saltar"),
    "message.terrassic.guide.1": ("Guia de Campo: silhueta de %s revelada", "Field Guide: %s silhouette revealed", "Guía de Campo: silueta de %s revelada"),
    "message.terrassic.guide.2": ("Guia de Campo: %s avistado", "Field Guide: %s sighted", "Guía de Campo: %s avistado"),
    "message.terrassic.guide.3": ("Guia de Campo: %s estudado", "Field Guide: %s studied", "Guía de Campo: %s estudiado"),
    "message.terrassic.guide.4": ("Guia de Campo: %s domesticado", "Field Guide: %s tamed", "Guía de Campo: %s domesticado"),
    "message.terrassic.theme_done": ("Diário de Campo: tema %s concluído", "Field Journal: %s theme complete", "Diario de Campo: tema %s completado"),
    "message.terrassic.page_found": ("Página da Katarina guardada no Caderno: %s", "Katarina's page added to the Notebook: %s",
                                     "Página de Katarina guardada en el Cuaderno: %s"),
    "message.terrassic.fossil_broke": ("O fóssil rachou. Só sobrou um osso.", "The fossil cracked. Only a bone is left.", "El fósil se rompió. Solo quedó un hueso."),
    "message.terrassic.lens_seen": ("%s a %s blocos", "%s, %s blocks away", "%s a %s bloques"),
    "message.terrassic.sketch_done": ("Esboço pronto: %s", "Sketch done: %s", "Boceto listo: %s"),
    "message.terrassic.sketch_lost": ("Você perdeu o animal de vista.", "You lost sight of the animal.", "Perdiste de vista al animal."),
    "tooltip.terrassic.study_at_table": ("Estude na Mesa de Pesquisa", "Study it at the Research Table", "Estúdialo en la Mesa de Investigación"),
    "item.terrassic.sketch.of": ("Esboço de %s", "Sketch of %s", "Boceto de %s"),
    "itemGroup.terrassic.science": ("Terrassic: Ciência", "Terrassic: Science", "Terrassic: Ciencia"),
    "advancements.terrassic.root.title": ("Terrassic", "Terrassic", "Terrassic"),
    "advancements.terrassic.root.description": ("O Diário de Campo do Capítulo 1", "The Field Journal of Chapter 1", "El Diario de Campo del Capítulo 1"),
}
