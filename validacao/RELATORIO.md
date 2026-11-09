# Relatório de validação da semântica trivalente ZYQL

**Executado em:** 2026-11-09T17:17:34+00:00 · **Ambiente:** Python 3.11.16 (Linux)
**Objeto:** funcao decidir() do app emitido por zyclotron_service.emit_service
**Regra sob teste:** proporcao-v1 (intervalo de Hoeffding)

## Selo e cadeia de custódia

| Item | Valor |
|---|---|
| SHA3-256 do protocolo (selado antes de rodar) | `ed50c6122539df136300ca6e12484e3ecd8ac759cad964461856e11525be7314` |
| SHA3-256 do resultado agregado | `62664883d35592ef9eb63cae9c27c36c383025bc17f6c3551e02284ce5579219` |
| Casos executados | 3630 |
| Recibos distintos emitidos | 3564 |

## Resultado por hipótese

| ID | Hipótese | Forma testada | Violações | Status |
|---|---|---|---|---|
| H1 | Solidez do veredito 1 | veredito 1 implica p̂ − ε > limiar | 0 | **SUPORTADA** |
| H2 | Solidez do veredito 0 | veredito 0 implica p̂ + ε < limiar | 0 | **SUPORTADA** |
| H3 | Completude | distância maior que ε nunca resulta em INCONCLUSIVE | 0 | **SUPORTADA** |
| H4 | Recusa informativa | INCONCLUSIVE só ocorre dentro da faixa de incerteza | 0 | **SUPORTADA** |
| H5 | Contrato fechado | limiar ou Δ inválidos, shots ≤ 0 → REFUSED | 0 | **SUPORTADA** |
| H6 | Monotonicidade do erro | ε decresce com shots e escala como 1/√shots | 0 | **SUPORTADA** |
| H7 | Determinismo e cobertura | mesmo payload → mesmo hash; limiar entra no hash | 0 | **SUPORTADA** |

## Distribuição de vereditos

| Veredito | Casos |
|---|---|
| `1` | 1461 |
| `0` | 1461 |
| `INCONCLUSIVE` | 642 |
| `REFUSED` | 0 |

ε observado entre 0.02371 e 0.203453.

## Leitura honesta

Sete hipóteses, 3630 casos, zero contraexemplo. Isso sustenta que a
implementação **é consistente com a regra que declara** no domínio testado. Não é
demonstração formal, não é prova de superioridade e não cobre hardware: o domínio é
finito e discreto, e ausência de contraexemplo num grid não é universal.

O que a validação compra é verificabilidade: quem quiser refutar tem o protocolo, o
domínio, o selo e o comando. Refutar exige um caso, não uma opinião.

## Limitações declaradas

- dominio finito e discreto: ausencia de contraexemplo nao e prova universal
- uma execucao por configuracao, sem estudo estatistico
- sem assinatura: o recibo prova integridade, nao autoria (marco 03)

## Como reproduzir

```bash
git clone https://github.com/SerenaSolutions/zephirum-lang
cd zephirum-lang
PYTHONPATH=src python3 validacao/validar_semantica.py
```

O script confere o selo do protocolo e aborta com código 2 se o texto mudou desde a
selagem. Para refutar, basta exibir um caso que viole qualquer hipótese: o relatório
lista os contraexemplos quando existirem.
