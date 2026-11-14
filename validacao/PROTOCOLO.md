# Protocolo de validação da camada de decisão ZYQL

**Versão:** 1.0 · **Data de selagem:** 2026-11-09 · **Autoria:** Serena Quantum Solutions
**Objeto:** a função `decidir()` do aplicativo emitido por `zyclotron_service.emit_service()`,
regra `proporcao-v1` (intervalo de Hoeffding), com vereditos `1`, `0`, `INCONCLUSIVE`, `REFUSED`.

Este arquivo é selado por SHA3-256 em `validacao/protocolo.sha3` **antes** de qualquer
execução. O validador recomputa o hash e aborta se o texto mudou. A ordem importa:
depois de ver o resultado, mudar a pergunta deixa de ser possível.

## Escopo declarado

Cobre: a semântica de decisão sobre contagens, o contrato de entrada e a integridade
do recibo. Não cobre: hardware quântico, transpilação, QASM 3, correção de erro,
desempenho, nem qualquer alegação de vantagem quântica. Nada aqui diz que o sistema
é rápido ou superior: diz que ele decide de forma consistente com a regra que declara.

## Hipóteses e critério de refutação

Cada hipótese é refutada por **um único contraexemplo** no domínio declarado.
Ausência de contraexemplo no domínio é o resultado; não é prova universal.

| ID | Hipótese | Critério de refutação |
|---|---|---|
| H1 | Solidez do veredito 1: veredito `1` implica `p̂ − ε > limiar` | um caso com veredito `1` e `p̂ − ε ≤ limiar` |
| H2 | Solidez do veredito 0: veredito `0` implica `p̂ + ε < limiar` | um caso com veredito `0` e `p̂ + ε ≥ limiar` |
| H3 | Completude: se `|p̂ − limiar| > ε` então veredito ∈ {`1`,`0`} | um caso decidido como `INCONCLUSIVE` fora da faixa de incerteza |
| H4 | Recusa informativa: `INCONCLUSIVE` implica `|p̂ − limiar| ≤ ε` | um caso `INCONCLUSIVE` com distância maior que ε |
| H5 | Contrato fechado: limiar fora de (0,1) ou não numérico, Δ fora de (0,1) ou não numérico, shots ≤ 0 implicam `REFUSED` | qualquer veredito diferente de `REFUSED` nesses casos |
| H6 | Monotonicidade do erro: ε decresce com shots e escala como 1/√shots | ε não decrescente, ou razão ε(4s)/ε(s) fora de 2 ± 1% |
| H7 | Determinismo e cobertura do recibo: mesmo payload → mesmo `receipt_hash`; payloads que diferem só no limiar → hashes distintos | hash divergente no mesmo payload, ou hash igual com limiar diferente |

## Método

Grade fatorial declarada antes da execução:

- `shots` ∈ {64, 128, 512, 2048}
- `delta` ∈ {0.01, 0.05, 0.2}
- `threshold` ∈ {0.10, 0.20, …, 0.90} (9 valores)
- `k` (contagem da chave `000`) de 0 a `shots`, passo `max(1, shots//32)` → 33 pontos

Total previsto: 4 × 3 × 9 × 33 = **3.564 casos** de decisão, mais os casos de contrato
(H5) e as repetições de determinismo (H7, 50 repetições de um payload por limiar).

Chamada direta da função, sem rede e sem servidor: o objeto medido é o código emitido,
não o transporte HTTP.

## Métricas reportadas

Casos executados, violações por hipótese, taxa de decisão (`1`/`0`/`INCONCLUSIVE`),
ε mínimo e máximo observados, e o `receipt_hash` agregado do resultado.

## Limitações declaradas de antemão

1. O domínio é finito e discreto. Ausência de contraexemplo não é demonstração formal.
2. O intervalo de Hoeffding é conservador por construção; a cobertura empírica é
   medida, não assumida.
3. Uma execução por configuração de hardware, quando houver hardware. Sem estudo
   estatístico de placa.
4. Não há assinatura criptográfica nesta versão: o recibo prova integridade do
   conteúdo, não autoria. Autoria é escopo do marco 03 e está declarada como pendente.
