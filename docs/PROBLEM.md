# Problema Científico — Confiabilidade da Decisão Trivalente em Hardware Quântico Real: Shots Mínimos Empíricos e Calibração do REFUSED

Status: DOSSIÊ DE EXPEDIÇÃO CIENTÍFICA
Data: 2026-10-21 (ISO 8601)
Repositório: `SerenaSolutions/zephirum-lang`

---

## 1. O Problema

O protocolo estatístico formal da casa (`docs/ZYQL_STATISTICAL_PROTOCOL.md`) estabelece o modelo para decisões trivalentes ZYQL (`1`, `0` e `REFUSED`). No protocolo declarativo:
- É adotada uma banda de ruído nominal $\delta = \pm 0.15$.
- São aplicados bounds de erro binomiais e a cota de Hoeffding.
- A fórmula de shots mínimos para um nível de erro $\alpha$ é formulada teoricamente como:
  $$n_{\min}(\alpha) = \frac{\ln(\alpha)}{\ln(1 - \delta)}$$
  (para $\alpha = 0.01$ e $\delta = 0.15$, resulta teoricamente em $n_{\min} = 29$ shots, enquanto o protocolo de referência utiliza $n = 2048$).

**A lacuna empírica:** Essa fórmula teórica e a banda de ruído de decisão jamais foram validadas sistematicamente em função da variação contínua de shots em hardware quântico real (QPU física como o IBM Heron `ibm_fez`).

Além disso, a varredura científica v1 (job `dbbuh17i0auc73dtpaeg`) revelou que o teste de aderência estatística de qui-quadrado ($\chi^2$) foi reprovado em todos os pontos devido a um viés de leitura não calibrado (sub-1% readout bias), embora a variância total ($TV \le 4.5\%$) estivesse contida. Apenas na varredura v2 (job `dbcfn70c77vs73866mdg`), mediante mitigação de leitura, o $\chi^2$ aprovou em 18 de 20 circuitos.

**Questão Científica Central:** Quantos shots um computador quântico real necessita empiricamente para tomar uma decisão trivalente ZYQL com acurácia estatística $\ge 95\%$, e sob quais condições a recusa honesta (`REFUSED`) deve ser calibrada em hardware real?

---

## 2. Hipóteses Científicas

- **H1 (Conservadorismo / Insuficiência da Fórmula Teórica):** A fórmula teórica de shots mínimos $n_{\min} = \frac{\ln \alpha}{\ln(1-\delta)}$ é irreal na QPU física, pois assume ruído estocástico i.i.d. sem contabilizar o viés assimétrico e a fidelidade de leitura (readout error floor) do hardware real.
- **H2 (Existência do Limiar Empírico de Confiança):** Existe um número mínimo empírico de shots $n_{\min}^{\text{emp}}$ dentro da faixa avaliada no qual a bateria trivalente (`1` para constante-1, `0` para constante-0, `REFUSED` para balanceado) obtém acurácia $\ge 95\%$ nas decisões.

---

## 3. Plano de Rodadas de Experimentos

### Rodada A — Sweep de Shots na Bateria DJ Trivalente ($n=3$)
- **Níveis de Shots:** Varredura em $S = \{512, 1024, 2048, 4096, 8192, 16384\}$.
- **Bateria de Circuitos Deutsch-Jozsa Trivalente ($n=3$ qubits):**
  1. **Caso Constante-1:** Espera-se probabilidade do estado base $p(000) > 0.85 \implies$ decisão `1`.
  2. **Caso Constante-0:** Espera-se probabilidade do estado base $p(000) > 0.85 \implies$ decisão `0`.
  3. **Caso Balanceado:** Espera-se probabilidade do estado base $p(000) < 0.15 \implies$ decisão `REFUSED` (recusa honesta por interferência destrutiva).
- **Métricas:** Taxa de acerto global da decisão por nível de shots e frequência de acionamentos espúrios de `REFUSED` em regimes de baixos shots.

### Rodada B — Calibração do REFUSED e Mitigação de Leitura
- Caso a Rodada A evidencie discrepância relevante em shots baixos ou viés de leitura que induza decisões errôneas/recusas espúrias, a Rodada B aplicará mitigação de matriz de leitura para recalibrar os limiares do `REFUSED` e ajustar o parâmetro da banda de ruído $\delta$ em hardware.

---

## 4. Critérios de Sucesso

1. **Curva Empírica Shots × Acurácia:** Mapeamento completo e reprodutível do desempenho da decisão trivalente frente ao número de shots ($512$ a $16384$).
2. **Shots Mínimo Empírico ($n_{\min}^{\text{emp}}$):** Determinação rigorosa do menor valor de shots que garante a cota de $\ge 95\%$ de decisões corretas.
3. **Veredicto do Protocolo Estatístico:** Emissão de parecer formal selado indicando se `docs/ZYQL_STATISTICAL_PROTOCOL.md` é **VALIDADO** como está ou **CORRIGIDO** com a inclusão de parâmetros empíricos medidos em hardware.

---

## 5. Honestidade da Casa e Transparência

- ** HARDWARE REAL:** Todos os dados coletados na expedição são categorizados e rotulados explicitamente como **HARDWARE REAL** (QPU física IBM Heron `ibm_fez`).
- **Isenção de Endosso:** A plataforma IBM Quantum é utilizada estritamente como ambiente e laboratório de teste físico, sem qualquer implicação de endosso, suporte ou parceria institucional pela IBM.
- **Recibo Z-QEA Selado:** Todas as evidências, matrizes de amostragem e conclusões são acompanhadas por um recibo Z-QEA selado via SHA3-256 (regra de selagem limpa sem autorreferência), permitindo verificação pública no GitHub via `.github/actions/zqea-verify`.
