# Post LinkedIn — Anúncio científico (pronto pra colar)

**ZEPHIRUM/ZYQL v1.9.0 — a linguagem quântica que desconfia do próprio computador.**

Passamos dois anos ouvindo que linguagens de programação quânticas precisam responder sim ou não. Mas hardware quântico real é ruidoso — e a resposta honesta para "este resultado é confiável?" muitas vezes não é sim nem não: é "eu me recuso a decidir".

Foi com essa inquietação que construímos o ZEPHIRUM (SerenaSolutions/zephirum-lang): uma linguagem de sintaxe Lisp com um núcleo de decisão TRIVALENTE. Cada decisão retorna 1 (permitido), 0 (proibido) ou REFUSED (confiança estatística insuficiente). A recusa não é exceção, não é erro: é um valor de primeira classe, selado em recibo.

Na versão 1.9.0, lançada hoje, o núcleo ganhou três semânticas que nenhuma outra linguagem quântica tem:

1. Margem adaptativa (Hoeffding inverso): o desenvolvedor declara o erro máximo aceitável (epsilon) e a banda de confiança é derivada matematicamente — shots curtos resultam em recusa honesta, nunca em veredito falso.
2. Porta de integridade GHZ: antes de confiar num veredito, o runtime testa o PRÓPRIO processador quântico em coerência (estado GHZ₃). Dispositivo decoerido = REFUSED sem gastar uma única chamada ao oráculo. É a primeira linguagem que desconfia do próprio QPU.
3. Cadeia de proveniência: cada recibo sela o selo do anterior — um ledger tamper-evidente de experimentos.

Tudo validado em silício real: IBM Heron de 156 qubits, com fidelidade GHZ de 0.977 e vereditos trivalentes exatos em todos os níveis de shots testados (64 a 16.384). Cada rodada é selada em recibo de duas camadas: SHA3-256 + assinatura pós-quântica ML-DSA-44 (FIPS 204), com entropia medida em computador quântico.

Código aberto, reproduzível, documentado:
https://github.com/SerenaSolutions/zephirum-lang

O projeto vive de ciência aberta e de quem acredita nele. Se quiser apoiar a pesquisa, nosso GitHub Sponsors está aberto — cada doação vira mais tempo de QPU real:
https://github.com/sponsors/SerenaSolutions

Recusar quando não há confiança não é fraqueza do sistema. É exatamente o que o separa de um sistema que mente.

#QuantumComputing #OpenSource #PostQuantum #Cryptography #Innovation

