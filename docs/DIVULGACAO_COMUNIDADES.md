# Divulgação nas comunidades quânticas brasileiras

**Objetivo:** levar o ZEPHIRUM/ZYQL a quem já trabalha com computação quântica no Brasil,
começando por Campinas, São Paulo, Curitiba e Nordeste. A apresentação é do projeto e do que
ele mede: nada de credencial emprestada.
**Situação:** materiais prontos, alvos verificados, publicação depende de conta própria em
cada plataforma. Nenhuma mensagem foi enviada por mim: eu não tenho conta nessas
comunidades, e inventar uma seria o oposto de divulgação.

---

## 1. Alvos verificados

Só entra aqui o que eu consegui confirmar com fonte pública hoje, 09/11/2026.

| Polo | Alvo | O que é | Link verificado | Canal de entrada |
|---|---|---|---|---|
| Curitiba | **Curitiba Quantum Week** (UTFPR) | Semana de palestras e minicursos, edição 2026 confirmada, inclui minicurso de programação em Ket | `utfpr.edu.br/campus/curitiba/agenda-eventos/curitiba-quantum-week-2025-inicia-em-19-de-maio-1` | Submissão de palestra/minicurso pela organização do evento |
| Curitiba / Ponta Grossa | **II Quantum Workshop UEPG & UFPR** | Workshop acadêmico de dois dias (30–31/07) | Instagram oficial do evento | Contato com a comissão organizadora |
| São Paulo | **ICTP-SAIFR** (IFT-Unesp) | Instituto internacional com programação de tecnologias quânticas e comunicação quântica | `sbfisica.org.br` (nota sobre encontro de comunicação quântica) | Inscrição em atividades e contato científico |
| São Paulo | **IME-USP / IMEECC-Unicamp** | Cursos de introdução à computação quântica e decomposição de circuitos | `ime.unicamp.br`, `ic.unicamp.br/~seminarios` | Seminários: proposta de exposé técnica |
| São Paulo (online) | **Meetup "Computação quântica: do conceito à inovação"** (Sympla) | Meetup recorrente, edição no setor financeiro | `sympla.com.br/evento/meetup-computacao-quantica-do-conceito-a-inovacao-no-sistema-financeiro/3218410` | Página do organizador no Sympla |
| Nordeste | **CIQUANTA-PB** (Campina Grande / João Pessoa) | Centro Internacional de Computação Quântica da Paraíba, residência do MCTI | `ciquanta.secties.pb.gov.br` | Portal oficial, perfil Empreendedores |
| Nordeste | **CESAR** (Recife) | Evento "O Brasil em diálogo sobre o futuro quântico" (28–29/07) | página oficial do CESAR | Contato institucional |

**O que não confirmei e por isso não afirmo:** e-mails, grupos de Telegram/Discord, listas de
discussão e datas de edição futura. Cada um desses exige verificação no canal oficial antes
de qualquer envio.

---

## 2. O que dizer em cada lugar (três textos prontos)

### 2.1 Para grupo de mensagens / meetup (curto)

> Pesquisadores de Campinas, São Paulo, Curitiba e Nordeste: o ZEPHIRUM é uma linguagem de
> decisão para computação quântica. A ideia é simples e incômoda: antes de computar, ela
> decide se a pergunta merece um computador quântico. Cada veredito é 1, 0 ou REFUSED, com
> erro declarado e recibo SHA3 verificável, e o mesmo portão responde "os tiros não bastam"
> quando é o caso.
> É experimental e está em estágio inicial, e diz isso na própria documentação.
> Reproduz em cinco minutos: `pip install zephirum`. Protocolo de validação pré-registrado,
> com sete hipóteses falsificáveis e 3.630 casos executados, em
> github.com/SerenaSolutions/zephirum-lang

### 2.2 Para professor / coordenador de laboratório (e-mail curto)

> Assunto: linguagem de decisão trivalente para laboratório de computação quântica
>
> Professor(a), mantenho o ZEPHIRUM, uma linguagem de decisão trivalente com recibos
> verificáveis, publicada em Apache-2.0 e instalável por `pip install zephirum`. O que pode
> interessar ao seu grupo: um protocolo de validação pré-registrado, com sete hipóteses
> falsificáveis e 3.630 casos executados, uma demonstração de integração com Qiskit que
> inclui controle negativo, e recibos que qualquer pessoa pode recomputar por hash.
> Nada disso foi reproduzido por terceiros ainda, e é exatamente isso que buscamos.
> Se houver espaço em seminário ou aula, preparo uma apresentação de 20 minutos com o código
> rodando ao vivo. Repositório: github.com/SerenaSolutions/zephirum-lang

### 2.3 Para LinkedIn (institucional)

> O ZEPHIRUM é uma linguagem de decisão para computação quântica, e a tese dela é
> desconfortável: a maior parte das perguntas feitas a um computador quântico não deveria
> chegar lá antes de passar por um portão que sabe dizer não.
>
> Cada veredito é 1, 0 ou REFUSED, com incerteza declarada e recibo verificável por hash.
> Quando os dados não sustentam uma conclusão, a resposta é a recusa, e a recusa vem com
> motivo e com prova do que foi executado.
>
> O que está aberto e verificável: protocolo selado antes da execução, 3.630 casos, zero
> contravenções, demonstração executável com controle negativo.
> O que ainda não existe, e não anuncio como se existisse: assinatura criptográfica dos
> recibos, reprodução por terceiro independente e estudo estatístico em hardware.
>
> Classificação honesta: experimental, estágio inicial. O projeto é aberto e aceita
> refutação com um contraexemplo, que vale mais que um aplauso.

---

## 3. Ordem recomendada

1. **Curitiba Quantum Week** e **II Quantum Workshop UEPG/UFPR**: são os dois canais com
   chamada aberta para palestra. Uma submissão aceita é inserção com endosso de terceiro,
   não autopromoção.
2. **CIQUANTA-PB**: coincide com a inscrição como empreendedor que já está pendente.
   Um formulário, dois objetivos.
3. **ICTP-SAIFR e seminários do IME/USP e Unicamp**: entrada acadêmica, a mais lenta e a mais
   valiosa, porque gera refutação em vez de aplauso.
4. **Meetup no Sympla e CESAR**: divulgação de alcance, menor peso científico.

## 4. Regra de conduta

Toda mensagem sai com a classificação `experimental` e com a distinção entre recibo de
integridade e autoria assinada. Divulgação que infla resultado compra atenção hoje e cobra
juros na primeira pergunta técnica.
