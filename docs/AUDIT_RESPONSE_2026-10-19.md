# Resposta da casa à auditoria externa — 2026-10-19

Auditor recebido pelo dono (2026-10-19) sobre SerenaSolutions/zephirum-lang e
SerenaSolutions/zerone-quantum-os. Adequação item por item, regra da casa:
nenhuma alegação acima do que a evidência sustenta.

## Críticos
1. **Secrets & history scan — EXECUTADO.** Varredura de todos os blobs do
   histórico git (padrões: ghp_, github_pat_, AKIA, PEM privado, qw_, sk-,
   senhas literais): **zero segredos encontrados** no histórico completo.
2. **Dependências — EXECUTADO.** `requirements-lock.txt` adicionado
   (numpy 2.4.6, qiskit 2.6.0, qiskit-ibm-runtime 0.50.0); kernel permanece
   stdlib puro. Dependabot ativo no repositório.
3. **Chaves e assinaturas — RÓTULO CORRIGIDO (achado da auditoria confirmado).**
   O selo IMPLEMENTADO é SHA3-256 (integridade). A alegação de ML-DSA-44/FIPS-204
   era aspiracional na documentação e foi rotulada como DECLARED ROADMAP em
   README e docs/receipts.md. Implementação futura exigirá módulo acreditado
   (CMVP) e chaves em HSM/KMS — nunca primitiva caseira.
4. **CI — VERDE.** ci.yml roda a bateria canônica em Python 3.10 e 3.11 (sem
   dependências, semeada); CodeQL ativo.

## Alta prioridade
5. **Formalização estatística do ZYQL — EXECUTADO.**
   `docs/ZYQL_STATISTICAL_PROTOCOL.md`: estados, banda δ=0.15, regra de decisão,
   probabilidades de erro binomiais com fórmula de shots mínimos
   (n_min = ln(α)/ln(1−δ) ⇒ 29 shots para α=1%; suíte usa 2048), calibração da
   banda contra o piso de ruído observado (q≈0.016 no fez, k=7.5× margem) e
   regra de drift com janela de validade do recibo.
6. **REFUSED formalizado — EXECUTADO.** `docs/ZYQL_REFUSED_SPEC.md`: seis
   gatilhos exaustivos (R1–R6), modelo de custo (REFUSED nunca consome QPU,
   custo clássico polinomial limitado), análise anti-DoS e recibo próprio.

## Médio/longo prazo (registrar honestamente: NÃO executado ainda)
7. Reprodutibilidade de build (cosign/sigstore) — planejado.
8. ZERONE (repo privado): aguarda decisão do dono sobre acesso do auditor
   externo OU tarball; a casa reitera que alegações de QEC multi-rodada
   exigem código, decodificador, taxas lógico×físico e simulações com ruído.
9. Revisão por pares e benchmarks comparativos — as discussões públicas
   abertas na comunidade (validação do ZQ-GATE, Gottesman-Knill como
   certificado, rótulos DECLARED_CLASSICAL × PROVEN_QUANTUM) são o primeiro
   passo dessa via.

## Alegações corrigidas nesta resposta (a regra da casa em ação)
- "ML-DSA-44 seals every decision" → SHA3-256 selo de integridade
  (implementado); ML-DSA-44 = roadmap declarado.
- DJ "one oracle call" → formalizado com banda de ruído e estatística
  binomial explícita; o recibo cita a banda, nunca o modelo ideal como fato.

Nenhum número sem recibo. ASK FIRST. PROVE NEXT. COMPUTE LAST.
