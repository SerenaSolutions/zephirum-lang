# RODADA I — GATE DE MEMÓRIA DO RUÍDO (pré-registro)

**Data do pré-registro:** 2026-10-31, antes de qualquer disparo e antes de qualquer dado.
**Pergunta científica:** a hipótese de independência das amostras — axioma escondido de
todo limite Hoeffding da linguagem — vale neste dispositivo, nesta profundidade?

## Por que isto é o teste mais duro que a casa pode fazer

Todo veredito ZYQL com banda adaptativa carrega `eps' = sqrt(ln(2/δ)/(2S))`, que SÓ é
válido se as amostras forem independentes (canal markoviano, sem memória). Se o ambiente
guarda memória, o limite é inválido e o veredito pode estar errado **sem que a banda
denuncie** — o erro é sistemático, não amostral. Nenhuma linguagem quântica hoje testa
esse axioma no próprio hardware antes de decidir.

## Medida

Distância de traço entre duas evoluções do sistema a partir de estados iniciais distintos
(medida BLP de não-markovianidade, Breuer–Laine–Piilo 2009):

    D(k) = ½ · || ρ_a(k) − ρ_b(k) ||₁ = ½ · | r_a(k) − r_b(k) |

com `r` o vetor de Bloch reconstruído por tomografia de 3 bases (X, Y, Z).
Revival: `Δ(k) = D(k+1) − D(k) > 0`. Contração CPTP garante `Δ(k) ≤ 0` em dinâmica
markoviana; revival é assinatura de memória.

## Modelo de colisão (implementável sem circuitos dinâmicos)

Sistema `S = q0`; ambiente com duas construções:

1. **MEMÓRIA** — um único âncora `E = q1` reaproveitado em todas as colisões; as
   correlações S–E persistem entre passos.
2. **SEM MEMÓRIA (controle)** — âncoras frescas `q1..q4`, uma por passo, cada uma
   iniciada em |0⟩; o ambiente é descartado a cada colisão (canal markoviano).

Colisão: `U = CX(S → âncora)`. Estados iniciais de S: |0⟩ e |+⟩.
Passos: k ∈ {0, 1, 2, 3, 4}. Bases de medida de S: X, Y, Z.

Circuito por célula: preparo → k aplicações de U → rotação de base → medida.
54 circuitos, 2048 shots cada.

## Predições declaradas ANTES do dado

- **P1 (memória):** espera-se pelo menos um revival `Δ(k) > m_D` na variante MEMÓRIA,
  pois as correlações S–E acumulam e podem devolver informação ao sistema.
- **P2 (controle):** a variante SEM MEMÓRIA deve apresentar `Δ(k) ≤ m_D` em todos os k
  (contração CPTP), salvo ruído de hardware acima da banda.
- **P3 (D(0)):** `D(0) = √2/2 ≈ 0.7071` para o par (|0⟩, |+⟩). Se D(0) destoar disso
  além de `m_D`, o preparo/medida está comprometido e a rodada é REFUSED por instrumento.

## Regra de decisão (selada antes do dado)

Banda: `m_exp = sqrt(ln(2/ε)/(2S))` com `ε = 0.05`, `S = 2048`.
Propagação declarada (conservadora): erro por componente de Bloch `≤ 2·m_exp`;
`m_D = √3 · m_exp` (fator ½ já embutido) — arredondado para cima em 4 casas.

- **VEREDITO 1 — MEMÓRIA DETECTADA:** existe k com `Δ(k) > m_D` na variante MEMÓRIA
  **e** todos os `Δ(k) ≤ m_D` no controle. Consequência declarada: para decisões nesta
  profundidade de dispositivo, a banda Hoeffding **não é automaticamente válida**; o
  runtime deve emitir `REFUSED / NOISE_HAS_MEMORY` quando o gate acusar memória.
- **VEREDITO 0 — REGIME MARKOVIANO CONFIRMADO:** nenhum revival acima da banda em
  nenhuma das variantes. Consequência: a banda Hoeffding é aplicável nesta profundidade
  (dentro do escopo testado).
- **REFUSED — INCONCLUSIVO:** revival dentro da banda (não separável do ruído), **ou**
  revival também no controle (anomalia: contradiz a contração CPTP), **ou** P3 violada
  (instrumento comprometido). Recusa implica não-afirmação, sem retry e sem maquiagem.

## Escopo declarado e limites (sem maquiagem)

- Duas QPUs bastam; rodada disparada em `ibm_marrakesh` (fila menor no disparo).
- O resultado vale para a profundidade k ≤ 4 e para este modelo de colisão; **não** se
  extrapola para outros canais, outras profundidades ou ruído correlacionado espacial.
- Revival ausente **não prova** ausência de memória em geral: só que não foi detectada
  nesta geometria, nesta profundidade e com esta potência estatística.
- Nenhum resultado é reivindicado antes de todos os jobs estarem DONE e a análise única
  (sem peeking) ser executada.

## Selagem

Recibo `round_i_receipt.json` (v2: SHA3-256 + ML-DSA-44) encadeado no selo da Rodada D,
com job IDs, contagens cruas, banda, Δ(k) e veredito.
