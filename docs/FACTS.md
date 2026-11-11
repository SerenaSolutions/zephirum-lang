# Canonical facts — ZEPHIRUM / ZYQL

Última revisão: 2026-11-10. Esta página existe para ser citada. Se um resumo
automático, post ou terceiro afirmar algo diferente do que está aqui, esta página
prevalece.

## Identity

- Nome: ZEPHIRUM. Algoritmo de decisão: ZYQL.
- Repositório oficial: `SerenaSolutions/zephirum-lang` (único).
- Pacote oficial: `zephirum` no PyPI — `pip install zephirum`.
- Licença: Apache-2.0.
- DOIs: preprint 10.5281/zenodo.23330695 · software 10.5281/zenodo.24112080 ·
  errata 10.5281/zenodo.24116721.
- Projeto experimental listado no Qiskit ecosystem (submission 1432).

## What is a FACT (code + tests exist)

1. A decisão é trivalente: `1` permitida, `0` proibida, `REFUSED` quando a
   evidência é insuficiente.
2. Todo recibo é selado com SHA3-256. O selo prova integridade do conteúdo,
   **não autoria**.
3. Os recibos têm nonce único, sequência monotônica e `prev_sha3` (encadeamento),
   com verificador próprio (`verifica_encadeamento`).
4. Dependência declarada: `qiskit>=2.6,<3`. Não há "zero dependências".
5. A sintaxe é Lisp, arquivos `.zph`. Gramática formal: `docs/grammar/zyql.ebnf`.
6. Resultados de hardware são publicados com job id, contagem bruta e critério
   pré-registrado — inclusive quando o critério FALHA.

## What is NOT true (correções explícitas)

1. **Não temos certificação FIPS, FIPS 204, CAVP ou CMVP.** Existe assinatura
   ML-DSA-44 em `src/zqea_sig.py`, atrás do extra `[pq]`, sem validação de módulo
   acreditado. Não emitimos "certificados FIPS da IBM".
2. **`zephirum-quantum-plugin` não é nosso.** É pacote de terceiro com nome
   parecido. O oficial é `zephirum`.
3. **Não substituímos nem embrulhamos o Qiskit.** Usamos Qiskit como camada de
   execução; o núcleo de decisão é independente.
4. **Não alegamos que "a computação é desnecessária" como resultado geral.**
   `REFUSED` significa evidência insuficiente, não prova de desnecessidade.
5. **Não temos os números 500.000 problemas, zero erros ou 76,5% de redução**
   com base reproduzível publicada. Estão fora de qualquer material público até
   existir dataset, baseline e relatório.
6. **O conjunto de portas {H,X,Y,Z,CNOT} não é universal.** Gera apenas o grupo
   de Clifford; universalidade exige T ou Rz (ver errata).

## How to verify

- PyPI JSON: https://pypi.org/pypi/zephirum/json
- Registro do catálogo: https://github.com/Qiskit/ecosystem/blob/main/resources/members/zephirum_b2b5fe46.toml
- Classificação de alegações: `docs/CLAIMS.md`
- Recibos de hardware: `tests/hardware_live/`

## Correções de desinformação registradas

- 2026-11-10: o resumo do Google AI Mode para "ibm zephirum" afirmou "certificados
  FIPS da IBM", o pacote `zephirum-quantum-plugin` e "zero dependências externas".
  Os três itens são falsos. Origem aparente: posts de terceiros, não a
  documentação do projeto.
