# Maturidade por componente — ZEPHIRUM/ZYQL (v1.8.0)

Declaração oficial de escopo e maturidade, componente a componente. Nada aqui é
marketing; cada nível tem critério. Auditorias devem citar este documento.

| Componente | Nível | Critério / limite explícito |
|---|---|---|
| `zyql_quantum_gate` (núcleo trivalente) | *PRODUÇÃO* | DJ interference, 1 call de oráculo, regra de ruído com banda ±0.15 e limite de erro Hoeffding declarado. Validado em silício IBM Heron (Rodadas A/B, 64-16384 shots, job IDs selados) |
| `zyql_runtime` (runtime de produção, v1.8.0) | *PRODUÇÃO* | API estável `decide()`/`Verdict`, validação pré-oráculo, determinismo por seed, recibo SHA3 opcional, thread-safe, 3.4k decisões/s (n=3 local). Limite: n ≤ 8 na fase-oráculo simulada; oráculo caro → backend IBM |
| Selagem Z-QEA (SHA3-256) | *PRODUÇÃO* | Selo verificável offline, tamper→recusa |
| Assinatura ML-DSA-44/FIPS 204 | *PRODUÇÃO* | zqea-seal v2.0.0, chave pública embarcada, entropia quântica IBM |
| Simulador `zquantum` | *BETA* | State-vector didático/local; decisões de produção com ruído real usam IBM Heron via backend |
| Parser/interpretador Lisp `zyql_lisp` | *EXPERIMENTAL* (linguagem de pesquisa) | S-expressions sem otimizador, sem sistema de macros, sem gestão de pacotes. Limites reconhecidos: docs/AUDIT.md. O *runtime de decisão* não depende do parser |
| CLI `zqgate` | *LEGACY/manutenção* | Mantido por compatibilidade |
| VS Code ext / playground / PyPI | *roadmap* | docs/ROADMAP_90D.md |

**Limites globais declarados:** sem correção de erro (execução útil sem EC fica bem
abaixo de 20 qubits — declarado); claims de hardware sempre com job ID + recibo;
simulação rotulada como simulação.
