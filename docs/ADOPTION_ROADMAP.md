# Roadmap de Adoção — ZEPHIRUM/ZYQL (vindo da auditoria externa de 2026-10-22)

Auditoria externa independente avaliou o repo como "cientificamente interessante e bem
documentado", com camada de pesquisa sólida e falta de "motor de adoção". Estado de cada
ponto (feito / em andamento / pendente / depende do dono):

1. **Site oficial + landing page** — PENDENTE. Pages já ativo no ecossistema (ravi-quantuno);
   falta landing própria do zephirum-lang.
2. **Playground online** — PENDENTE. Prioridade alta (editor web .zph + decisão trivalente + recibo).
3. **PyPI** — PRONTO, falta apenas o PYPI_TOKEN do dono. Packaging corrigido em 1.7.5:
   `pip install zephirum` agora entrega a linguagem inteira (verificado por import real).
4. **Releases com changelog** — FEITO (v1.7.4/v1.7.5 com notas completas). Wheels anexados: pendente.
5. **Exemplos por domínio** — PARCIAL (hello, DJ, química em experiments/). Faltam exemplos de
   decisão de segurança, gating de IA, otimização.
6. **Benchmark comparativo** — PARCIAL. Confronto multilíngue (Qiskit/QASM3/Cirq/PennyLane/Braket)
   existe no quantum-poc com recibos; falta matriz pública contínua (custo, ruído, queries).
7. **Discussions + roadmap público** — FEITO. Discussions ativo; este doc é o roadmap público.
8. **Templates de issue** — FEITO (herdados da org .github: bug report, feature, científico).
9. **Extensão VS Code (.zph)** — PENDENTE.
10. **Notebooks / Colab** — PENDENTE. "Hello, Zephirum" em notebook é o próximo passo barato.
11. **Receipts explorer visual** — PARCIAL. CLI zqea-verify (--strict-pq) existe; falta modo visual/plot.
12. **Open research lab** — PARCIAL. experiments/ tem setup + jobs + recibos selados (Rodadas A/B);
   falta padronizar seeds/CSV por experimento.
13. **Badges** — PARCIAL. Version badge agora sincronizada (meta-teste vigia); faltam CI/PyPI/downloads.
14. **Blog técnico** — PENDENTE (docs/blog/): "Why REFUSED is not failure", "Trivalent vs Boolean".
15. **Integrações** — PENDENTE (API REST wrapper, Docker image).

Resposta da casa à auditoria: os pontos de inconsistência real (badge 1.6.0, CI rodando só
um teste, packaging sem os módulos da linguagem) foram corrigidos na v1.7.5 com meta-teste
de guarda. A claims de hardware são seladas em recibos ML-DSA-44 (duas camadas, não só
SHA3-256 como dizia a auditoria) e a reprodutibilidade externa depende de conta IBM Quantum
— as credenciais não podem, por design, viver no repo.
