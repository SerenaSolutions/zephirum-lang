# ZEPHIRUM / ZYQL — Dossiê para avaliação externa

**Destinatário:** agente avaliador independente
**Emitido em:** 30/10/2026, 15:25 (America/Sao_Paulo)
**Finalidade:** fornecer base factual para responder uma única pergunta — *qual é a
posição real deste projeto no mundo hoje, em linguagens quânticas e em decisão
verificável?*
**Regra deste documento:** todo número aqui foi lido na fonte em 30/10/2026, por API ou
por instalação limpa. O que não foi verificado está marcado como tal. O que não se
sustenta está na seção 6, com o mesmo destaque do que se sustenta.

---

## 1. Identidade e artefatos existentes

| Artefato | Endereço | Estado verificado |
|---|---|---|
| Repositório | https://github.com/SerenaSolutions/zephirum-lang | público, MIT, criado 12/10/2026, último push 30/10/2026 |
| Pacote Python | https://pypi.org/project/zephirum/2.1.2/ | 2.1.2 publicado 30/10/2026; wheel + sdist |
| Registro científico | DOI 10.5281/zenodo.23632020 (conceito: ...019) | Zenodo, tipo *Software*, versão v2.1.0, MIT |
| Site | https://serenasolutions.github.io/zephirum-lang/ | HTTP 200 |
| CI de recibos | `python -m battery_ci` (no pacote) | bateria trivalente + verificação de cadeia |

Sinais de adoção, medidos em 30/10/2026: **1 estrela, 0 forks, 1 watcher, 19 issues
abertas, 5 releases** (v1.9.0 → v2.1.1), 24 arquivos de teste, 25 módulos de topo.
É um projeto de autor único, com um mês de vida e nenhum usuário externo registrado.
Qualquer avaliação de posicionamento deve começar por esse fato, não pelo texto do README.

---

## 2. O que a linguagem é

ZYQL não devolve número, devolve veredito em três estados:

- **1** — decisão afirmativa dentro de banda estatística declarada
- **0** — decisão negativa dentro de banda declarada
- **REFUSED** — não há decisão honesta possível, com motivo legível por máquina

REFUSED tem taxonomia: ruído acima da banda, evidência ambígua, sinal ausente,
protocolo adulterado, parada antecipada. A tese é que abstenção rastreável vale mais
que número inventado.

Cada decisão pode ser selada num **recibo Z-QEA**, em quatro camadas:

1. **Integridade** — SHA3-256 do conteúdo
2. **Encadeamento** — `prev_sha3` liga ao recibo anterior; remoção e reordenação detectáveis
3. **Autoria** — ML-DSA-44 (família FIPS 204) sobre o selo
4. **Confidencialidade** — ML-KEM-768, camada opcional

A camada 3 é *auto-consistência de assinatura*, não certificação CAVP. Ver seção 6.

---

## 3. Arquitetura do código (25 módulos de topo, 2 pacotes)

- **Núcleo trivalente:** `zqgate` (pacote, CLI), `battery_ci`, `zyql_witness` (abstenção com prova), `shot_auditor`
- **Linguagem:** `zyql_lisp` (interpretador), `oq3` (transpilador para OpenQASM 3), `quantum_types`
- **Runtime e sistema:** `zkernel` (escalonador, log de auditoria, registro de backends), `zquantum`, `zyql_runtime`
- **Criptografia dos recibos:** `zqea_sig`, `zqea_kem`
- **Simulação:** `zyql_mps` (produto de estados matricial), `zyql_zne` (extrapolação a ruído zero), `zyql_selfverified`
- **Interoperabilidade:** `zyql_cirq`
- **Camadas aplicadas:** `zyqml_core` (aprendizado variacional trivalente), `zyql_llm_compress`, `zyql_rag_layer`
- **Robustez:** `zyql_robust` (guardas adversariais), `zyql_auditkit` (entropia com recibo)
- **Experimentos selados:** `zyql_protocols` (P-08, P-10), `zyql_world3`, `zyql_worldscale`

---

## 4. Evidência experimental — WORLD-3 na IBM `ibm_marrakesh`

Bandas declaradas **antes** da execução. Três jobs independentes, 8.192 shots cada.

| Protocolo | Medida | IC 95% | Banda declarada | Veredito |
|---|---|---|---|---|
| W-02 interferência de dois fótons | visibilidade 0,952 ± 0,001 | [0,947; 0,957] | ≥ 0,70 | **1 — certifica com margem** |
| W-01 caminhada quântica | TVD 0,253 ± 0,048 | [0,244; 0,263] | reprova acima de 0,20 | **REFUSED — dispositivo não sustentou** |
| W-03 Grover 3 qubits | p(marcado) 0,773 ± 0,011 | [0,764; 0,782] | certifica ≥ 0,85 | **REFUSED — amplificação visível, certificação não** |

Fonte: `experiments/world_scale_20261029/AUDITORIA_ULTRA.md` e `w3_analise_ic.json`.
O ponto metodológico mais relevante para o avaliador: **o veredito negativo está
publicado com o mesmo peso do positivo**, e uma auditoria externa apontou falha no
desenho estatístico original (regra de agregação certificava em 12% das vezes com o
dispositivo exatamente na banda), o que obrigou a trocar para regra intervalar —
`docs/POWER_ANALYSIS.md`.

---

## 5. Como verificar sem confiar no projeto

```bash
pip install zephirum==2.1.2
python -c "import zephirum; print(zephirum.__version__)"
python -m battery_ci          # bateria trivalente + verificação da cadeia de recibos
```

O teste que importa: apagar um recibo do meio da cadeia e verificar se a ferramenta
detecta. Se detectar, o mecanismo existe. Se não, não existe.

---

## 6. O que NÃO se alega (leia antes de avaliar)

| Alegação | Situação |
|---|---|
| "Conformidade FIPS 204 certificada" | **não sustentada** — usa biblioteca com ML-DSA-44; não há certificação CAVP do caminho próprio |
| "Prova de qualidade quântica reconhecida por regulador" | **não sustentada** — não existe norma que reconheça recibo quântico como prova regulatória |
| "Revisão por pares concluída" | **não existe** — há preprint e registro Zenodo, sem parecer de periódico |
| "Adotada por terceiros" | **não existe** — 0 forks, nenhum usuário externo registrado |
| "Listada no Qiskit Ecosystem" | **não** — PR #1433 submetido, não aprovado |
| "Cliente pagante" | **não existe** |
| "Oráculo determinístico para DeFi travar fundos" | **não sustentada** — o dispositivo abstece, tem fila e latência |
| "Auditoria de hardware com prova verificável" | **parcial** — prova execução do circuito, não audita o chip |

Fonte: `docs/CLAIMS.md`, que classifica cada frase comercial do projeto em EVIDÊNCIA,
PARCIAL, ROADMAP ou NÃO SUSTENTADO.

---

## 7. Dívida técnica conhecida

- O pacote instala **25 nomes de topo** (`zqgate`, `zkernel`, `zyql_*`), violando boas práticas e sujeito a colisão. Migrar para `zephirum.*` é breaking change e exige versão maior.
- Metadados do PyPI só ficaram corretos em 2.1.2 (30/10/2026); 2.1.0 e 2.1.1 seguem no índice com metadados vazios, e versão publicada não é editável.
- Versão aparece em duas fontes (`pyproject.toml` e `importlib.metadata`); divergência silenciosa é possível.
- Classifiers de framework Qiskit ausentes.

---

## 8. Perguntas objetivas ao agente avaliador

1. Em outubro de 2026, existe alguma linguagem ou biblioteca publicamente disponível que trate **abstenção como resultado de primeira classe com recibo criptográfico encadeado**? Quem são os vizinhos mais próximos (Qiskit, Cirq, PennyLane, Guppy, Q#, Silq, Twist) e em que ponto exatamente este projeto se diferencia deles?
2. O diferencial real é a **semântica trivalente** ou o **recibo verificável**? Qual dos dois sustenta uma posição defensável, e qual é facilmente copiável por um concorrente maior?
3. Com 1 estrela, 0 forks e nenhum usuário externo, qual é a leitura honesta de tração? Que sinal mínimo mudaria essa leitura em 90 dias?
4. A publicação de um veredito **negativo** em QPU real (W-01 recusado) é ativo de credibilidade ou passivo de marketing no estado atual do mercado quântico?
5. Que padrão externo este projeto deveria perseguir primeiro: OpenQASM 3, QIR, ou adoção via Qiskit Ecosystem? Qual abre porta institucional mais rápido?
6. O que falta, concretamente, para que um laboratório ou banco aceite um recibo deste tipo como evidência de auditoria?

---

*Documento gerado a partir de verificação direta em GitHub API, PyPI, Zenodo e
instalação limpa do pacote. Nenhum número foi estimado.*
