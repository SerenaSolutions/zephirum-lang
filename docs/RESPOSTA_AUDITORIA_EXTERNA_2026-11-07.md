# Resposta à auditoria externa (commit 54b1051) — 07/11/2026

**Resultado da minha conferência: 7 de 7 achados se confirmam no código.** Nenhum foi refutado.
Corrigidos 6 em sandbox. O achado P1-3 não foi alterado, por exigir decisão de semântica.

| # | Achado | Confirmado | Estado |
|---|---|---|---|
| P1-1 | `(seal caminho)` grava em caminho do programa | sim | **corrigido** |
| P1-2 | cota por chave não autenticada, antes da autenticação, sem expiração | sim | **corrigido** |
| P1-3 | `adaptive_margin_family` com direção contrária à união de testes | sim | **parado para decisão** |
| P2-1 | cadeia com leitura-escrita não atômica e falha silenciosa | sim | **corrigido** |
| P2-2 | `zqea_pq` importado, não existe; `/verify` não validava assinatura | sim | **corrigido** |
| P2-3 | CI não roda test_gateway, test_api, test_billing, test_auditoria | sim | **corrigido** |
| P2-4 | "uma chamada ao oráculo" ignora a sonda clássica f(0) | sim | **corrigido** (texto) |

## O que foi feito em cada um

**P1-1.** `_caminho_de_recibo_permitido` resolve o caminho (realpath) e recusa qualquer alvo fora
de `ZYQL_RECEIPT_DIR` (padrão `./recibos`). Teste cobre `/etc/passwd`, `../../fora.json` e `/tmp/escape.json`.

**P1-2.** Cota por IP **antes** da autenticação, e depois por identidade autenticada
(`chave:SHA3(chave)`). `X-Forwarded-For` só é aceito com `ZYQL_TRUSTED_PROXY=1`.
`_expurgar_cotas` remove identidades inativas e há teto duro de 20 000 entradas.
Teste: chave inventada variando não fura a cota por IP.

**P2-1.** `_CADEIA_LOCK` serializa leitura-escrita; gravação em `.tmp` + `os.replace` (atômica),
com `fsync`. Falha de persistência agora levanta exceção em vez de devolver recibo selado como encadeado.
Teste: 24 threads, 24 elos únicos.

**P2-2.** Assinatura real com `zqea_sig.assinar` (ML-DSA-44), par de chaves persistido em arquivo 0600,
`chave_publica` dentro do corpo assinado, selo recalculado sobre o corpo sem a assinatura.
`/verify` agora distingue `integridade` (hash) de `autoria_verificada` (assinatura), verificando sobre o
recibo integral. Prova: recibo intacto → `hash_ok` + `autoria_verificada: true`; adulterado → recusado.

**P2-3.** CI passou a rodar `pytest tests -q` (a suíte completa), além dos arquivos nomeados.

**P2-4.** Docstring corrigida: 1 consulta ao oráculo de fase **+ 1 sonda clássica f(0)**, contada.

## P1-3 — por que eu não mexi

A regra é: veredito 1 se `p0 >= 1 - m`. Sob oráculo balanceado, `P(p0 >= 1 - m)` **aumenta** quando `m`
aumenta, porque o limiar se aproxima de 0,5. Ou seja: banda mais larga torna a alegação de "constante"
mais agressiva. O documento do código já reconhece isso ao falar da Bonferroni ingênua.

A união padrão exige banda mais larga para k testes, e sob ESTA regra isso aumenta o falso positivo.
Encolher a banda, como faz `2*m(eps) - m(eps/k)`, reduz o falso "constante" mas aumenta o falso "balanceado"
(o teste 0 dispara com `p0 <= m`). Não existe direção grátis: a garantia familiar exige mudar o **limiar**,
não só a margem — separar 0,5 de 1 com distância d tal que `2k*exp(-2*S*d^2) <= eps`, recusando quando
as shots não bastarem.

Isso altera a decisão da linguagem. Pela regra vigente, nenhum agente muda isso sozinho.
Proposta para o supervisor: aprovar a rederivação, com teste de Monte Carlo para `family` em {1, 4, 16, 64},
`shots` em {1024, 4096, 16384} e `epsilon` em {0,05, 0,01}, medindo taxa de erro familiar empírica.
Até a aprovação, o limite não deve ser apresentado como garantia estatística.

## Suíte
154 aprovados (147 anteriores + 7 regressões novas da auditoria).
