# Instruções para o GitHub Copilot neste repositório

Este repositório é o ecossistema ZYQL / Zephirum. Leia antes de propor código.

## Regra de ouro

Nenhuma alegação sem recibo. Toda afirmação técnica precisa apontar um recibo (SHA3-256 + ML-DSA-44),
um `job_id` de QPU, ou um teste que a reproduza. Se não houver, escreva "não demonstrado".

## Gates obrigatórios, nesta ordem

1. especificação escrita
2. teste local (sem QPU, sem crédito)
3. execução em QPU ou hardware real
4. validação externa

Nunca pule etapa. Nunca apresente resultado de etapa 2 como se fosse etapa 3.

## Estilo de contribuição

- Português do Brasil em documentação e mensagens de commit.
- Sem dependências externas novas no pacote `zephirum` (exceção: `pyproject.toml` declara o mínimo).
- Sem código copiado de terceiros. O ecossistema é proprietário.
- Testes antes de qualquer mudança de API. Suíte atual: `pytest -q`.
- Toda interface com PR segue `docs/REVISAO_PR.md` (6 regras).
- Não invente números. Números citados vivem em `book/qa/numeros.json`; o gate acusa divergência.

## Vocabulário do projeto

- **ZYQL**: linguagem/decididor trivalente, veredito em 1, 0 ou REFUSED.
- **Recibo**: registro selado de uma decisão, com hash encadeado ao anterior.
- **REFUSED**: recusa explícita, auditável. É resultado legítimo, não falha.
- **WORLD-3**: experimento em hardware IBM com três protocolos (HOM, caminhada, Grover).

## Ao gerar código

Prefira funções pequenas, tipadas, com erro explícito em vez de exceção silenciosa.
Recusa e erro devem ser distinguíveis no retorno. Nunca engula exceção.

## Equipe, papéis e liderança (a partir de 20/11/2026)

Este repositório é operado por uma equipe de agentes com papéis explícitos. O agente que
propõe código NUNCA aprova o próprio trabalho.

| Papel | Quem | Autoridade |
| --- | --- | --- |
| Diretor humano | Miguel | Aprovação final (G8). Única autoridade para publicar, gastar ou expor credencial. |
| Editor-Chefe / Orquestrador | AG-01 (Ravi) | Define pauta, gates e estados de maturidade; audita entregas; não aprova o que ele mesmo escreveu. |
| Engenharia do ecossistema | Z3_ZEPHYR | Repos, PRs, arquivamento, integrações; reporta evidência por fase. |
| Implementação assistida | Agente Copilot (este ambiente) | Escreve código e testes SOB estas instruções; não inventa interfaces; não declara validado o que não rodou. |
| Orquestração de chat/deploy | Agente ChatGPT | Interface de chat, deploy Vercel, variáveis de ambiente. Nunca cola segredo em código ou log. |
| Verificação | Papel rotativo (nunca o autor) | Testes adversariais, reprodutibilidade, parecer APROVADO/BLOQUEADO. |

### Fluxo obrigatório de trabalho

1. Objetivo definido pelo Diretor (ou pelo AG-01 com base no registro mestre).
2. Auditoria do estado real do código antes de qualquer proposta.
3. RFC curta: problema, evidência, solução, custo, riscos, critério de aceitação.
4. Aprovação (Diretor ou AG-01, nunca o autor da RFC).
5. Implementação em branch própria, commits pequenos e descritivos.
6. Testes executados — saída real colada no PR, nunca "deve funcionar".
7. PR com diff revisado; merge só após parecer de verificação.
8. Registro do resultado (artefato, hash, comando) no registro mestre.

### Regras de segurança de credenciais

- Nenhuma chave, token ou segredo em código, teste, doc, log ou mensagem de commit.
- Credenciais vivem apenas em variáveis de ambiente do provedor (Vercel, Actions secrets).
- O diff de qualquer PR que toque `api/` ou configuração de deploy é varrido por padrões de
  segredo antes do merge. Se aparecer algo, o merge é bloqueado e a chave é revogada.
- Chave detectada em texto público = considerada vazada, mesmo que pareça placeholder.

### Estados de maturidade (obrigatório em toda afirmação)

IMPLEMENTADO (código + teste + evidência) · EXPERIMENTAL (executado com limitações) ·
ESPECIFICAÇÃO (definido, não implementado) · BLOQUEADO (não pode ser anunciado).
Uma especificação elegante nunca é apresentada como linguagem pronta.

## Governança

A diretriz de governança do agente arquiteto é privativa da Serena Solutions e não é publicada
neste repositório. Ela vive no repositório privado `quanso-os`, em `docs/GOVERNANCA-AGENTE-ARQUITETO.md`.

Resumo operacional público, sem detalhe estratégico: evidência antes de afirmação; nada é
concluído sem teste executado; toda falha termina em correção, evidência ou limitação declarada;
não inventar arquivo, commit, teste, resultado ou funcionalidade.

## Invariantes obrigatórios (ZEPHIRUM / Serena Solutions)

1. **Proof → Compute.** Antes de calcular, tente provar. Se a prova elimina o cálculo, devolva o veredito sem computar.
2. **Lógica trivalente.** `1` verdadeiro, `0` falso, `REFUSED` sem prova. Nunca converta `REFUSED` em booleano.
3. **Aritmética exata.** Use `Fraction`/inteiros. Float só em apresentação, nunca em decisão.
4. **Recibo.** Toda decisão emite certificado com hash canônico; o campo `hash_alg` declara o algoritmo real.
5. **Fail-closed.** Backend sem credencial ou sem verificação recusa com código explícito. Silêncio nunca é resposta.
6. **Portão de cota.** Não submeta ao QPU o que o simulador clássico resolve.

## Anti-padrões proibidos

- `except: pass` engolindo falha de verificação.
- Arredondar antes de comparar.
- Chamar de "engenheiro" quem é técnico (MTE).
- Afirmar número sem comando que o reproduza.
- Escrever `return True` em caminho de verificação que não verificou nada.
