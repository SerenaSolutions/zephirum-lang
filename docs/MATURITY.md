# Maturidade por componente — ZEPHIRUM/ZYQL (v2.0.0 — 08/11/2026)

Declaração oficial de escopo e maturidade, componente a componente. Nada aqui é
marketing; cada nível tem critério. Auditorias devem citar este documento.

| Componente | Nível | Critério / limite explícito |
|---|---|---|
| `zyql_quantum_gate` (núcleo trivalente) | *PRODUÇÃO* | DJ interference, 1 chamada ao oráculo de fase + 1 sonda clássica f(0), regra de ruído com banda ±0.15 e limite de erro Hoeffding declarado. Validado em silício a production superconducting QPU (Rodadas A/B, 64-16384 shots, job IDs selados) |
| `zyql_runtime` (runtime de produção, v2.3.2) | *PRODUÇÃO* | API estável `decide()`/`Verdict`, validação pré-oráculo, determinismo por seed, recibo SHA3 opcional, thread-safe, 3.4k decisões/s (n=3 local); gate de memória opcional (`require_memory_check`) recusa com NOISE_HAS_MEMORY quando o ambiente tem memória. Limite: n ≤ 8 na fase-oráculo simulada; oráculo caro → backend the provider |
| Selagem Z-QEA (SHA3-256) | *PRODUÇÃO* | Selo verificável offline, tamper→recusa |
| Assinatura ML-DSA-44/FIPS 204 | *BETA* | implementada e verificada no `/verify` (integridade separada de autoria); par de chaves gerado localmente em arquivo 0600, sem chave embarcada. Falta validação externa antes de PRODUÇÃO |
| Simulador `zquantum` | *BETA* | State-vector didático/local; decisões de produção com ruído real usam a production superconducting QPU via backend |
| Parser/interpretador Lisp `zyql_lisp` | *EXPERIMENTAL* (linguagem de pesquisa) | S-expressions sem otimizador, sem sistema de macros, sem gestão de pacotes. Limites reconhecidos: docs/AUDIT.md. O *runtime de decisão* não depende do parser |
| CLI `zqgate` | *LEGACY/manutenção* | Mantido por compatibilidade |
| VS Code ext / playground / PyPI | *roadmap* | docs/ROADMAP_90D.md |

**Limites globais declarados:** sem correção de erro (execução útil sem EC fica bem
abaixo de 20 qubits — declarado); claims de hardware sempre com job ID + recibo;
simulação rotulada como simulação.

> **Pendente de revisão matemática:** `adaptive_margin_family` (margem para testes
> múltiplos) não tem garantia familiar demonstrada. Não deve ser apresentada como
> garantia estatística até a rederivação independente ser aprovada. Ver
> `docs/RESPOSTA_AUDITORIA_EXTERNA_2026-11-07.md`.

## Mecanismos de assinatura (nao confundir)

| Mecanismo | Onde | Status |
|---|---|---|
| SHA3-256 (selo de conteudo) | `src/zqea_sig.py`, runtime | Implementado. Prova integridade, nao autoria. |
| Ed25519 (cadeia legada) | recibos antigos de `zyql_witness` | Mantido por compatibilidade. Nao e pos-quantico. |
| ML-DSA-44 / FIPS 204 | `zqea_sig.assinar/verificar` | Implementado via `pqcrypto`. **Sem certificacao FIPS/CAVP ou CMVP.** Chave gerada localmente, arquivo 0600. |

O que NAO temos e nao pode ser alegado: certificacao FIPS/CAVP, CMVP, gestao
institucional de chaves (HSM/KMS) e auditoria criptografica externa.
