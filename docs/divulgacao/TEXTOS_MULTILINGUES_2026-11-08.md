# Textos de divulgação — canal e versão

Regra desta pasta: **cada texto foi escrito para um lugar**. Republicar o mesmo
texto em todos os canais é o caminho mais rápido para parecer campanha, e
comunidade técnica reage mal a isso. Um canal por dia.

| Canal | Versão | Observação |
|---|---|---|
| LinkedIn (perfil pessoal) | Português — LinkedIn | Público de negócio e pesquisa aplicada. Não publicar em grupo. |
| Qiskit Slack / canais de desenvolvimento | Inglês — técnico | Link só no primeiro comentário, quando o canal desencoraja link no corpo. |
| Grupo ou Discord brasileiro | Português — informal | Conversa, não mural. |
| Comunidades Qiskit LatAm / Espanha | Espanhol | — |
| Comunidades locais chinesas (WeChat, grupos) | Chinês simplificado | **Não** usar canal oficial do Qiskit: lá o idioma de trabalho é inglês. |
| Comunidade Qiskit Japão | Japonês | Revisão por nativo antes de publicar: registro errado custa credibilidade. |
| Quantum Computing Germany | Alemão | Público que desconfia de entusiasmo; não amaciar o tom. |
| Quantum Paris / grupos francófonos | Francês | — |

Termos que **não** se traduzem, em nenhuma língua: `REFUSED`, `SHA3-256`,
`ML-DSA-44`, `ibm_marrakesh`, `shots`.

O que **não** fazer: disparar tudo no mesmo dia; marcar mantenedores em massa;
encostar no PR #1433 do Qiskit.

---

## Português — LinkedIn

Todo mundo que já colocou um circuito em hardware quântico conhece o momento.

O job volta. O número é bonito. E aí começa a parte que ninguém documenta: decidir se aquele número sustenta a frase que você vai escrever depois.

O Qiskit entrega o circuito, o transpilador, o resultado. O que ele não entrega é a resposta para uma pergunta anterior a tudo isso: a evidência que você tem é suficiente para afirmar o que você quer afirmar?

Passei os últimos meses construindo uma linguagem em que essa pergunta vem antes do resultado. Ela devolve três coisas, não duas: sim, não, e recusado. A recusa é o ponto. Um sistema que só sabe dizer sim e não vai dizer sim com 200 shots e chamar isso de descoberta.

Hoje ela compõe decisões e propaga o erro do conjunto, com recibo selado por SHA3-256 e assinado com ML-DSA-44. Rodou em hardware, com job ID público, e recusou onde a conta mandava recusar.

E é exatamente aí que eu preciso de você. Não estou pedindo estrela no repositório. Estou pedindo alguém com paciência e desconfiança saudável para tentar me derrubar: abri três tarefas pequenas, uma delas é verificar um recibo publicado e dizer se a alegação se sustenta. Leva vinte minutos.

O valor de um recibo não está em quem o emite. Está em quem consegue conferi-lo sem confiar no autor.

---

## Inglês — técnico (Qiskit Slack, Discussões)

I built a small layer that sits in front of a quantum result and returns three verdicts instead of two: 1, 0, and REFUSED. The third one refuses when the shot budget cannot support the claim, and it propagates that refusal through composed decisions so a program of seven decisions cannot quietly approve on the power of one.

It runs against Qiskit and `ibm_marrakesh`, and the receipts carry a SHA3-256 seal plus an ML-DSA-44 signature.

What I am asking is not attention, it is falsification. Three issues are open, sized for someone who has never seen the codebase:

1. Take a published receipt, recompute the seal, verify the signature, and say whether the claim is supported by what was actually measured.
2. Install and run the test battery on a clean machine and paste the real output, including failure.
3. Read the docs, pick three verifiable statements, and check each against the code. Find the ones that overstate.

The third one is the one I would most like someone to do to me. A project that checks quantum results but never checks its own claims is just a louder kind of guessing.

Issues: #55 (receipt verification), #56 (clean-machine run), #57 (docs vs code).

---

## Português — informal (grupo ou Discord)

Pessoal, um pedido honesto, não um lançamento.

Estou terminando uma camada que decide em cima de resultado quântico, e o diferencial dela é recusar quando a evidência não dá. Recusar é chato de vender e é o que salva o pesquisador de publicar besteira com 200 shots.

Preciso de gente fora do projeto para tentar quebrar isso. São três tarefas pequenas no repositório, uma delas é só conferir se um recibo assinado realmente confere. Se você achar um recibo com selo válido e alegação exagerada, você achou o defeito mais importante que existe nesse projeto.

Quem tiver vinte minutos e um pouco de má vontade, me avisa que eu mando o link.

---

## Espanhol

Casi todo el mundo que puso un circuito en hardware cuántico conoce ese momento: el job vuelve, el número sale bonito, y empieza la parte que nadie documenta. ¿Ese número sostiene la frase que vas a escribir después?

Construí una capa que se coloca delante del resultado y devuelve tres veredictos en vez de dos: 1, 0 y REFUSED. El tercero se activa cuando el presupuesto de shots no alcanza para sostener la afirmación, y se propaga por decisiones compuestas, así que un programa de siete decisiones no puede aprobar en silencio con la potencia de una sola.

Corre sobre Qiskit e `ibm_marrakesh`, con recibos sellados en SHA3-256 y firmados con ML-DSA-44.

No pido atención, pido falsación. Hay tres tareas abiertas, dimensionadas para alguien que nunca vio el código: verificar un recibo publicado, correr la batería en una máquina limpia, y leer la documentación buscando afirmaciones que el código no cumple. La tercera es la que más me interesa que alguien me haga.

---

## Chinês simplificado

把电路放到真实量子硬件上的人，都熟悉那一刻：任务返回，数字漂亮，然后是没有人在文档里写的那一步：这个数字够不够支撑你接下来要写的那句话。

我做了一层放在结果前面的东西，给出三种判定而不是两种：1、0 和 REFUSED。第三种在采样预算不足以支撑结论时触发，并沿着组合决策向上传播，所以七个决策组成的程序，不会靠其中一个的力量悄悄通过。

它运行在 Qiskit 和 `ibm_marrakesh` 上，回执带 SHA3-256 校验和 ML-DSA-44 签名。

我要的不是关注，是被推翻。仓库里开了三个任务，规模按完全没看过代码的人来定：核验一份已公开的回执、在一台干净机器上跑完整测试、以及读文档挑出代码并不支持的断言。第三个，最希望有人对我做。

---

## Japonês

量子ハードウェアに回路を載せたことがある人なら、あの瞬間を知っているはずです。ジョブが返り、数字はきれいで、そこから誰も文書化していない作業が始まります。その数字は、この後書く一文を支えられるのか、という判断です。

結果の手前に置く層を作りました。返す判定は二つではなく三つ、1、0、そして REFUSED です。三つ目は、ショット数の予算が主張を支えられないときに作動し、合成された判断へ伝播します。七つの判断からなるプログラムが、そのうち一つ分の力で黙って承認することはできません。

Qiskit と `ibm_marrakesh` で動作し、記録には SHA3-256 の封印と ML-DSA-44 の署名が付きます。

求めているのは注目ではなく反証です。コードを一度も見たことのない人向けの大きさで、三つのタスクを開いています。公開済みの記録を検証する、きれいな環境でテストを走らせる、文書を読んでコードが支えていない記述を探す。三つ目を、誰かに自分へ向けてほしいと思っています。

---

## Alemão

Wer schon einmal einen Schaltkreis auf echter Quantenhardware laufen ließ, kennt diesen Moment: Der Job kommt zurück, die Zahl sieht gut aus, und dann beginnt der Teil, den niemand dokumentiert. Trägt diese Zahl den Satz, den man danach schreiben will?

Ich habe eine Schicht gebaut, die vor dem Ergebnis sitzt und drei Urteile zurückgibt statt zwei: 1, 0 und REFUSED. Das dritte greift, wenn das Shot-Budget die Behauptung nicht tragen kann, und es pflanzt sich durch zusammengesetzte Entscheidungen fort. Ein Programm aus sieben Entscheidungen kann also nicht stillschweigend mit der Kraft einer einzigen zustimmen.

Läuft auf Qiskit und `ibm_marrakesh`, Belege mit SHA3-256-Siegel und ML-DSA-44-Signatur.

Ich bitte nicht um Aufmerksamkeit, sondern um Widerlegung. Drei Aufgaben sind offen, zugeschnitten auf jemanden, der den Code nie gesehen hat: einen veröffentlichten Beleg prüfen, die Testbatterie auf einer sauberen Maschine laufen lassen, und in der Dokumentation Aussagen suchen, die der Code nicht einlöst. Das Dritte ist das, was ich mir am meisten wünsche.

---

## Francês

Quiconque a déjà envoyé un circuit sur du matériel quantique connaît ce moment : le job revient, le chiffre est beau, et commence la partie que personne ne documente. Ce chiffre soutient-il la phrase qu'on va écrire ensuite ?

J'ai construit une couche placée devant le résultat, qui rend trois verdicts au lieu de deux : 1, 0 et REFUSED. Le troisième se déclenche quand le budget de shots ne peut pas porter l'affirmation, et il se propage dans les décisions composées : un programme de sept décisions ne peut pas approuver en silence grâce à la puissance d'une seule.

Tourne sur Qiskit et `ibm_marrakesh`, reçus scellés en SHA3-256 et signés en ML-DSA-44.

Je ne demande pas de l'attention, je demande d'être réfuté. Trois tâches sont ouvertes, calibrées pour quelqu'un qui n'a jamais vu le code : vérifier un reçu publié, lancer la batterie de tests sur une machine propre, et chercher dans la documentation des affirmations que le code ne tient pas. La troisième, c'est celle que j'aimerais le plus qu'on me fasse.
