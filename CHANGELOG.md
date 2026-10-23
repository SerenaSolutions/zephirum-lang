# Changelog

All notable changes to the ZEPHIRUM language are documented here.

## [1.9.0] - 2026-10-23
### Added — upgrade do algoritmo + Rodada C no silício (semânticas inéditas)
- **Margem adaptativa (Hoeffding inverso)**: `decide(f, epsilon=0.05)` — a banda de confiança
  é DERIVADA do erro máximo declarado; com shots suficientes a banda estreita, sem shots
  o núcleo recusa em vez de mentir. `adaptive_margin(eps, shots)` é API pública.
- **Porta de integridade GHZ** (semântica inédita no GitHub): `decide(..., require_device_trust=True)`
  testa o PRÓPRIO QPU (GHZ_3, fidelidade |000>+|111>) antes de confiar no veredito;
  dispositivo decoerido => REFUSED SEM gastar oráculo, modo `REFUSED_DEVICE_DECOHERED`.
- **Cadeia de proveniência**: recibos do runtime selam o selo do anterior
  (`previous_seal`) + `verify_chain([...])`. Ledger tamper-evidente de rodadas.
- **RODADA C no IBM Heron ibm_kingston** (jobs dbdlb7424mrc739iievg / dbdlbv424mrc739iig60,
  256 shots, epsilon=0.05): porta GHZ fidelidade **0.977 → dispositivo confiável**;
  DJ adaptativo **EXATO**: const-1 p0=0.9922→1, const-0 p0=1.0000→0, balanceado p0=0.0039→REFUSED.
  Recibo ML-DSA-44 **encadeado** no selo da Rodada B: experiments/round_c_receipt.json.
- Lição selada no silício: transpilar com optimization_level=2 no Heron (nível 1 mapeou
  a bateria em qubits ruidosos — primeira tentativa RECUSADA honestamente e refeita).
- 5 testes novos no runtime (11/11): banda adaptativa, vereditos adaptativos, porta GHZ,
  recusa sem oráculo, cadeia tamper-evidente.

## [1.8.0] - 2026-10-23
### Added — resposta à auditoria: "runtime de produção no algoritmo"
- `zyql_runtime`: runtime de PRODUÇÃO do núcleo ZYQL. API estável `decide()->Decision`,
  enum `Verdict` (PERMIT/DENY/REFUSED), validação pré-oráculo (ConfigError), determinismo
  por seed, recibo SHA3-256 opcional por decisão (verificável offline), thread-safe,
  zero prints no caminho da lib. Throughput local: ~3.4k decisões/s (n=3).
- CLI `zyql-decide` (console script) + `python -m zyql_runtime`.
- `docs/MATURITY.md`: declaração oficial de maturidade POR COMPONENTE (produção/beta/
  experimental/legacy) com limites explícitos — fim da ambiguidade "protótipo de pesquisa".
- `tests/test_runtime.py`: matriz de vereditos, determinismo, validação pré-oráculo,
  recibo selado→verificado→adulterado→recusado, honestidade do limite de erro, stress 200 decisões.

## [1.7.5] - 2026-10-23
### Fixed
- Badge de versão do README desatualizada (1.6.0) — agora 1.7.5, em sincronia com `pyproject.toml`.
- CI e Makefile agora executam TODOS os testes (`test_canonical.py` + `test_zqea_verify.py`), não apenas o canônico.

### Added
- `tests/test_meta.py`: meta-teste de consistência de versão (pyproject = badge README = CHANGELOG). O mismatch apontado em auditoria externa não pode mais voltar a acontecer despercebido.
- Packaging corrigido para distribuição PyPI: `package-dir = src` + `py-modules` com TODOS os módulos da linguagem (`zquantum`, `zkernel`, `quantum_types`, `zyql_lisp`, `zyql_quantum_gate`, `zyql_rag_layer`, `battery_ci`, `oq3`) + pacote `zqgate` (CLI). Antes, `pip install zephirum` entregaria apenas o CLI antigo, sem a linguagem.

## [1.7.4] - 2026-10-23
### Added
- **Rodada B executada — lacuna de shots baixos FECHADA**: bateria Deutsch-Jozsa n=3 trivalente no IBM Heron `ibm_kingston` (conta independente, backend distinto da Rodada A) em 64, 128, 256 e 384 shots. Vereditos trivalentes (1/0/REFUSED) **EXATOS em todos os níveis**, inclusive 64 shots (abaixo da previsão teórica de 82). Protocolo Estatístico ZYQL agora validado em hardware no intervalo completo [64, 16384] shots. Recibo ML-DSA-44 + entropia quântica: `experiments/round_b_receipt.json` (veredito `RODADA_B_VERIFICADA_TRIVALENTE_EXATO`).
- Scripts da rodada no repositório: `experiments/round_b_battery.py` (submissão) e `experiments/round_b_analyze.py` (análise + selagem v2).
- Documentação atualizada: `docs/ZYQL_STATISTICAL_PROTOCOL.md` (seção Rodada B + proposta concluída), `docs/PROOFS.md` (índice de evidências com a lacuna fechada).

## [1.7.3] - 2026-10-22
### Added
- Validação do Protocolo Estatístico ZYQL em Hardware Real (IBM Heron `ibm_fez`, Rodada A): sweep de 512 a 16384 shots no Deutsch-Jozsa $n=3$ trivalente com 100% de acerto (3/3 casos em todos os 6 níveis), zero recusa espúria e $p(000) \ge 0.9977$ para constantes / $\le 0.0024$ para balanceado. Veredicto **VALIDADO** no intervalo [512, 16384] com recibo selado SHA3-256 (`experiments/refusal_receipt.json`).
- Documentação da lacuna aberta abaixo de 512 shots em `docs/ZYQL_STATISTICAL_PROTOCOL.md` e proposta da Rodada B (sweep 16..256 shots).
- Atualização do índice de provas de conceito em `docs/PROOFS.md` (seção do problema com links para `docs/PROBLEM.md` e `experiments/refusal_receipt.json`).

## [1.7.2] - 2026-10-21
### Added
- Problem solved: minimum shots for reliable trivalent decisions measured on IBM Heron ibm_fez (Rodada A, 18/18 correct at 512..16384, protocol VALIDADO) — docs/PROBLEM.md, docs/ZYQL_STATISTICAL_PROTOCOL.md §6, experiments/refusal_receipt.json (sealed)
- Hello World canônico da linguagem: forma `(hello)` no núcleo Lisp, exemplo `examples/hello_world.zph` selado (Z-QEA).

## [1.7.2] - 2026-10-21
### Added
- Rodada 6 — HARDWARE REAL (IBM Quantum ibm_marrakesh, job dbclitfi0auc73dv77dg,
  512 shots, laboratório próprio): bateria ZYQL completa no silicio — DJ
  trivalente (1/0/REFUSED), palavras de tracado S3 (B_R B_S)^2 -> |01> vs
  (B_S B_R)^2 -> |10> — divergencia nao-abeliana medida no hardware — e Grover
  n=2. Todos os 6 circuitos dentro da banda de ruido declarada (desvio max 0.045).
  Recibo selado: experiments/round6_hardware_receipt.json (veredito HARDWARE_OK).
- Produto zy-ai-rag (SerenaSolutions/zy-ai-rag, v1.0.0): decisao trivalente de IA
  para CI — BM25 + tradutor LLM opcional (Gemini) + portao quantico ZYQL, recibo
  Z-QEA. Modos declarados: LLM ou OFFLINE.

## [1.7.1] - 2026-10-21
### Added
- ZYQL Lisp interpreter (src/zyql_lisp.py) + photonic layer: programs written
  IN the language (.zph) execute against an exact photonic Fock simulator
  (numpy/scipy, cutoff 10, no shots, no hardware, declared honestly).
- Round 5 photonic lab (experiments/round5_photonic_receipt.json, sealed):
  HOM bunching p(1,1)=0 exact; Mach-Zehnder deterministic exit with port
  switching at phase pi; ZYQL trivalent decision ON photonic dual-rail qubits
  (const-0 => 0, const-1 => 1, balanced => REFUSED, 1 oracle call); SU(2)
  beam-splitter rotations: order matters (photonic analog of the braid
  signature). Photonic Hadamard verified exact: BS50 . phase(pi/2) . BS50
  = e^{-i pi/4} H.

## [1.7.0] - 2026-10-21
### Changed
- ZYQL v2 syntax: Lisp-style s-expressions replace the Python-style surface
  (owner decision 2026-10-21). Core is the ZeptonQL trivalent decision —
  declared NOT quantum; quantum execution is an optional explicit layer.
  Spec: docs/ZYQL_LISP_SPEC.md; examples: examples/*_lisp.zph;
  .zph now highlights as Lisp on GitHub (.gitattributes, linguist-language=Lisp,
  mapping to be dropped once Linguist registers ZEPHIRUM natively).
- VS Code grammar updated to the v2 s-expression syntax.

### Added
- Rodada 4 (noiseless, statevector, sealed): experiments/round4_derived.py +
  round4_derived_receipt.json — C11 Grover n=3 (matches theory to 9 decimals),
  C12 DJ n=6 trivalent (1/0/REFUSED exact), C13 GHZ-5 parity, C14 QFT-3
  roundtrip, C15 receipt registry sweep (6 receipts INTEGRAL), C16 Z-ANYON LAB:
  non-Abelian braid battery (commutator L1 = 6, |11> veto exact, period-3 echo
  verified) — NAO_ABELIANO_VERIFICADO.
- Marketplace product line (derived, all ZeptonQL/Z-QEA based):
  zqea-verify (live), z-anyon-lab, zq-gate, zqea-seal — see docs/MARKETPLACE.md.

## [1.6.0] - 2026-10-21
### Added
- docs/PROBLEM.md: dossier da expedição científica sobre a confiabilidade da decisão trivalente ZYQL em hardware quântico real (shots mínimos empíricos, calibração do REFUSED e hipóteses H1/H2).
- S3 qutrit miniature (experiments/): braiding non-commutativity and 3-channel
  fusion space (qutrit-in-qubits), noiseless with exact-zero deviation vs theory
  (canonical rational arithmetic) and verified on real hardware: IBM Heron
  ibm_fez, jobs dbbueufi0auc73dtp7og and dbbugbk24mrc73cif420; full ZYQL
  trivalent battery 3/3 PASS on hardware (receipt sealed in
  experiments/s3_qutrit_full_receipt.json). Scientific sweep of 26 circuits
  (job dbbuh17i0auc73dtpaeg) submitted; harvest pending.
- Packaging: pyproject.toml — `pip install -e .` exposes zkernel, zquantum,
  zyql_quantum_gate, quantum_types, zyql_rag_layer, oq3 as installable modules.
- docs/AUDIT.md: external audit record (GitHub Copilot audit, 2026-10-21) with
  our validation, findings and remediation status.
- docs/ROADMAP.md: public roadmap (compiler, type layer, benchmarks, FIPS 204).
- docs/PARTNERSHIP.md: GitHub partnership dossier.
- GitHub Pages deployment via GitHub Actions (site/).

- PennyLane cross-check (experiments/chemistry/pennylane_crosscheck.py):
  H2 VQE reproduces the battery FCI reference -1.13730604 Ha with error
  4.2e-09 (convention documented: PennyLane default unit is bohr; battery
  geometry is angstrom). Receipt sealed.
- New .zph examples: s3_qutrit.zph (fusion-space miniature), chemistry_h2.zph.
- .gitattributes: honest Linguist stats (receipts generated, assets vendored).
- docs/PROOFS.md: public index of proofs of concept (S3 non-Abelian
  miniature front and center) + proofs section on the Pages site.
- Scientific sweep harvested (job dbbuh17i0auc73dtpaeg, 26 circuits): braid
  angle sweep 10/10 dominant channels correct, non-Abelian window measured at
  theta/pi in [0.3,0.7]; braid-word period 6/6; Pauli error map exact.
  chi-square (4096 shots) fails in all points due to sub-1% uncalibrated
  readout bias — declared honestly; TV <= 4.5%. Master receipt re-sealed
  (C7). Data figure updated with all 10 measured points.
- Z-QEA Receipt Verifier (GitHub Action, Marketplace candidate):
  `.github/actions/zqea-verify` — recomputes the SHA3-256 seal of any receipt
  JSON; INTEGRAL passes the job, a broken seal fails it. Tested both ways
  (tests/test_zqea_verify.py).
- Seal rule upgrade: master receipt re-sealed with the clean canonical rule
  (seal = SHA3-256 over the receipt with the seal field removed —
  self-contained verification, no history chaining). Documented in the
  receipt itself (field selo_regra). New master seal: a4419246...
- docs/MARKETPLACE.md: GitHub Marketplace listing plan (free verifier,
  hosted tier later). Site: sponsor page with declared tiers.
- Sponsor button live: .github/FUNDING.yml (GitHub "Sponsor" on the repo
  points to the tier page); Stripe products/prices created for the three
  tiers ($5/$25/$100 monthly), checkout flow validated in test mode.
- Scientific sweep v2 HARVESTED (job dbcfn70c77vs73866mdg, 30 circuits with
  readout calibration): mitigated chi-square passes 18/20 (raw v1: 0/10),
  dominant channels 20/20, measured readout fidelity 94.6-97.6%. Hypothesis
  CONFIRMED: the v1 chi-square failure was readout bias (instrument), not
  physics. Receipt sealed (scientific_sweep2_receipt.json).
### Fixed
- Broken README quickstart: `from src.zyql_quantum_gate import ...` failed
  (sys.path.insert pointed at repo root, not src/). Modules now use a
  deterministic in-tree fallback and work installed or from source.
- Topics: removed typo tag `betta`.

## [1.5.0] - 2026-10-20
### Added
- Chemistry battery (experiments/chemistry): H2, LiH, H2O, NH3 — Jordan-Wigner
  mapping reproduces PySCF FCI exactly in all four molecules (error 0 / < 1e-10),
  battery receipt 85c20bc9. Nature-derived molecules through the full pipeline.
- Formal statistical protocol (docs/ZYQL_STATISTICAL_PROTOCOL.md): noise band
  d=0.15, binomial error bounds, minimum-shots formula, drift validity window.
- REFUSED formal spec (docs/ZYQL_REFUSED_SPEC.md): six triggers (R1-R6),
  bounded cost model (never consumes QPU), anti-DoS analysis, own receipt type.
- External audit response (docs/AUDIT_RESPONSE_2026-10-19.md): secrets scan
  clean over full history, dependencies locked (requirements-lock.txt).
### Changed
- Receipts documentation: SHA3-256 integrity seal is the implemented label;
  ML-DSA-44 (FIPS 204) signatures are a declared roadmap item (honest labeling).

## [1.4.3] - 2026-10-12
### Added
- `qif` quantum conditional (controlled-X decomposition, no collapse) - verified: Bell 1/2+1/2.
- First-class quantum types (`qbit`/`zyqbit`) with static no-cloning rejection.
- Native neural statement `zyql_rag`: docs -> BM25 -> translator -> interference gate -> receipt.
- Hardware confrontation vs textbook Qiskit (job db6dklcvf2bc73d122t0, ibm_fez): depth 2 / 0 two-qubit gates vs depth 10 / 3 CZ, both decide correctly.

## [1.0.0] - 2026-10-11
### Added
- Trivalent Deutsch-Jozsa decision gate with declared noise band (+-0.15).
- Z-QEA certificates with canonical rational arithmetic.
- ML-DSA-44 (FIPS 204) receipt sealing.
- IBM Quantum lab bridge (verified ingestion: job db4oqmcvf2bc73cutcgg).

## [0.3.0] - 2026-10-10
### Added
- Hybrid Stack (5 layers), RX/RY/RZ/SWAP/Toffoli, Pauli Monte Carlo noise.
- OpenQASM 3 round-trip import/export verified against the reference parser.

## [0.2.0] - 2026-10-09
### Added
- Zephyron -> OpenQASM 3 transpiler; state-vector kernel [re,im] float64.

## [0.1.0] "Ausra Bridge" - 2026-10-07
### Added
- State-vector kernel, parser (12 gates), Bell/GHZ/Grover/QFT verified.
