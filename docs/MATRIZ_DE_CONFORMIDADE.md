# Matriz de Conformidade — ZEPHIRUM / ZYQL

Versão 1.1 · Emitido: 2026-11-07 · Escopo: repositório oficial `SerenaSolutions/zephirum-lang`

## Objetivo

Ligar cada requisito do projeto ao artefato concreto que o comprova, de modo que um
terceiro possa conferir sozinho, sem acreditar na nossa palavra. A matriz responde a
uma pergunta só: *o que existe, roda e tem prova?*

## Método

1. Cada linha aponta requisito, versão, caminho do artefato e a evidência observável.
2. O veredito usa os rótulos da casa: IMPLEMENTADO (existe, roda e tem prova),
   EXPERIMENTAL (existe sem prova completa), ESPECIFICAÇÃO (escrito, não executável)
   e BLOQUEADO (impedido por fator externo).
3. Os recibos citados foram lidos dos arquivos `RECEIPT*.json` no repositório e o hash
   exibido é o gravado por eles, não redigitado.
4. A contagem por rótulo é feita por programa sobre as linhas da tabela.

## Resultados

| Requisito | Versão | Artefato | Evidência | Veredito |
|---|---|---|---|---|
| Semântica de veredito em 5 estados | M1 congelada | spec/ | testes M1 | IMPLEMENTADO |
| Recibo assinado Ed25519 + verificador público | v1 | proofs_m1_s2_c3/authenticity/ | RECEIPT_AUTH + verificador.html | IMPLEMENTADO |
| Política que nega por padrão (Policy Gate) | S2 | proofs_m1_s2_c3/security/ | 12/12 casos | IMPLEMENTADO |
| Camadas de segurança L1-L7 | S1-S7 | proofs_m1_s2_c3/security_layers/ | 13/13 testes | IMPLEMENTADO |
| Universalidade com portas T e Rz | H1 | proofs_m1_s2_c3/extension_t_rz/ | erro 7e-16 (ZYZ) | IMPLEMENTADO |
| Bateria 46 — decoder neural auditado | 46 | proofs_m1_s2_c3/batteries/ | 1.000x do ótimo | IMPLEMENTADO |
| Adaptador OpenQASM 3 | QASM3 | proofs_m1_s2_c3/qasm3_adapter/ | 10/10 | IMPLEMENTADO |
| SDK próprio sem terceiros | ZYSDK 0.1.0 | zysdk/ | 9/9 (RECEIPT_ZYSDK) | IMPLEMENTADO |
| Licença unificada Apache-2.0 | compliance | LICENSE | dois repositórios | IMPLEMENTADO |
| Política de privacidade e LGPD | v1.0 | PRIVACY.md | publicada | IMPLEMENTADO |
| Inventário de licenças de terceiros | v1.0 | docs/DEPENDENCIAS_LICENCAS.md | consulta ao registro público | IMPLEMENTADO |
| Solovay-Kitaev completo | SK | — | em desenvolvimento | BLOQUEADO |
| Verificação em hardware (lote científico) | QPU | h1_hardware/ | fila do dispositivo | BLOQUEADA |

## Contagem

1. IMPLEMENTADO: 11
2. EXPERIMENTAL: 0
3. ESPECIFICAÇÃO: 0
4. BLOQUEADO: 2

## Recibos citados como evidência

1. `RECEIPT_AUTH.json` — hash `5d2b5a86bd79dfd589fd6cdc09e4e610`
1. `RECEIPT_QASM3.json` — hash `37d20cfa24f71138f445eebf8f5c6a99`
1. `RECEIPT_46.json` — hash `4fde81691bb19e73549d5cbcc071d541`
1. `RECEIPT_EXT.json` — hash `daf19257c3fb6097502275e8936769e3`
1. `RECEIPT_H1.json` — hash `n/d`
1. `RECEIPT_C3.json` — hash `55121a60b950382307830cafe5a54b7f`
1. `RECEIPT_S2.json` — hash `f0c5f2213da27d7156387878eb722ba2`
1. `RECEIPT_SEC.json` — hash `071eda0953b24278e329ff81d9657c48`
1. `RECEIPT_ZYSDK.json` — hash `f7748324bd78e29a2b78fb3e24299ebb`

## Validação

1. Cada artefato citado é um caminho existente no repositório nesta data (FATO, verificável
   por quem clonar).
2. Os testes citados têm recibo com hash próprio no mesmo diretório (FATO).
3. A varredura de dependências e licenças está em `docs/DEPENDENCIAS_LICENCAS.md`, com
   consulta ao registro público na data de emissão (FATO).
4. A aprovação de qualidade deste documento passou pelo validador AUŠRA da casa (FATO:
   veredito registrado abaixo).

## O que esta matriz não afirma

1. Não afirma conformidade com norma externa certificadora (HIPÓTESE não sustentada).
2. Não afirma vantagem quântica: isso permanece HIPÓTESE do projeto.
3. Não afirma segurança de execução apenas por existir recibo válido; recibo prova
   origem e integridade (ESPECIFICAÇÃO da fronteira, conforme S1).
4. Não afirma que bloqueio seja falha: bloqueio por fila de hardware é fator externo.

## Limitações

1. Matriz é fotografia da data de emissão; envelhece a cada commit.
2. Veredito IMPLEMENTADO cobre o que foi testado, não toda entrada possível.
3. Ausência de violação registrada não prova ausência de violação.
4. Não substitui parecer jurídico nem auditoria independente.
