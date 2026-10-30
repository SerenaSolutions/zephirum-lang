# Análise da tese de mercado: o que sustentamos e o que nao

Documento de disciplina. Toda frase comercial do projeto precisa aparecer aqui
classificada. **EVIDENCIA** = temos codigo + recibo. **PARCIAL** = mecanismo existe,
alegacao maior nao. **ROADMAP** = nao implementado. **NAO SUSTENTADO** = sem base.

## Camada tecnica

| Alegacao | Status | Base |
|---|---|---|
| Recibos com SHA3-256 selando cada decisao | **EVIDENCIA** | `zyql_witness`, WORLD-3, notebook |
| Assinatura pos-quantica ML-DSA-44 do recibo | **EVIDENCIA (novo)** | `src/zqea_sig.py`, 8 testes |
| Cadeia encadeada: remocao/alteracao detectavel | **EVIDENCIA (novo)** | `verificar_cadeia`, teste de elo removido |
| Disponibilidade de sigilo pos-quantico (ML-KEM-768) | **EVIDENCIA** | `zqea_kem`, test_kem |
| "Conformidade FIPS 204" certificada | **NAO SUSTENTADO** | usamos biblioteca com ML-DSA-44; nao ha certificacao CAVP do nosso caminho |
| Prova de "qualidade quantica" reconhecida por regulador | **NAO SUSTENTADO** | nao existe norma que reconheca recibo quantico como prova regulatoria |

## Mercado 1: PQC e ciberseguranca

| Alegacao | Status | Base |
|---|---|---|
| Ferramenta de auditoria de hardware com prova verificavel | **PARCIAL** | provamos execucao do circuito; nao auditamos o chip |
| Migracao FIPS 204 em instituicoes financeiras | **ROADMAP** | nosso papel seria ferramenta, nao certificadora |
| Oraculo deterministico para DeFi travar fundos | **NAO SUSTENTADO** | dispositivo abstem (REFUSED), tem fila e latencia; travar fundos bilionarios nisso e irresponsavel hoje |

## Mercado 2: QaaS e fomento

| Alegacao | Status | Base |
|---|---|---|
| Plataformas QaaS pagariam licenca pela tecnologia | **ROADMAP** | nenhuma conversa iniciada; dependemos do merge #1433 |
| Contratos de aquisicao (M&A) | **NAO SUSTENTADO** | especulacao sem ativo negociado |
| Fundos soberanos para deep tech validada em hardware | **ROADMAP** | existe fomento (ex. MCTI/CIQUANTA); exige empresa, nao repositorio |

## Mercado 3: financeiro

| Alegacao | Status | Base |
|---|---|---|
| Grover/caminhada para otimizacao de portfolio | **NAO SUSTENTADO** | sem vantagem demonstrada; nosso W-03 e 3 qubits |
| Nucleo exato e auditavel atrai VC | **ROADMAP** | tracao medida por clientes, nao por recibos |

## O que a tese acerta

A intersecao esta correta: recibo verificavel e a unica coisa que **nao** se copia
de um concorrente em uma semana. E o que ja roda, nao o que prometemos.

## O que falta antes de qualquer conversa comercial

1. Revisao externa (PR #1433 e preprint) — sem isso nao ha credibilidade.
2. Publicacao no PyPI (#24) — sem `pip install` nao ha produto.
3. Power analysis e seed do transpilador — sem isso um revisor derruba os numeros.
4. Piloto com um cliente real, mesmo gratuito, medindo uma dor concreta.

Ordem nao negociavel: 1 -> 2 -> 3 -> 4. Vender antes disso queima a unica vantagem
que temos, que e ser o unico com recibo honesto.
