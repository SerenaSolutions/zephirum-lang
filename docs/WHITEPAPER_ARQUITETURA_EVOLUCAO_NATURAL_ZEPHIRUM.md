# Arquitetura de Evolução Natural do Algoritmo ZEPHIRUM

## Whitepaper de arquitetura

**Versão:** 0.1 — proposta arquitetural  
**Data:** 2026-11-22  
**Status:** documento conceitual; não descreve funcionalidades futuras como já implementadas  
**Repositório canônico:** [SerenaSolutions/zephirum-lang](https://github.com/SerenaSolutions/zephirum-lang)

---

## Resumo

Este whitepaper propõe uma arquitetura evolutiva para o algoritmo de decisão ZYQL, núcleo decisório do ZEPHIRUM. “Evolução natural” é aqui uma metáfora de engenharia: o sistema progride por variação controlada de implementações, seleção baseada em evidências reproduzíveis e preservação de invariantes. Não significa que o algoritmo atual aprenda ou se modifique autonomamente.

A proposta parte das propriedades já documentadas no repositório: decisões trivalentes (`1`, `0`, `REFUSED`), limites estatísticos declarados, execução quântica ou análise de evidência, recibos verificáveis e distinção entre simulação e hardware. Organiza essas propriedades em camadas com contratos estáveis e apresenta um ciclo de evolução que permite experimentar novos métodos sem enfraquecer a semântica de recusa, a reprodutibilidade ou a auditabilidade.

As etapas de seleção adaptativa, promoção de variantes, compatibilidade de recibos e governança descritas como evolução são **propostas**. Não devem ser interpretadas como capacidades já disponíveis no código.

## 1. Escopo e vocabulário

ZEPHIRUM é uma linguagem e runtime para decisões auditáveis; ZYQL é sua camada de decisão. Este documento trata da evolução dessa camada e de suas interfaces com front-end, backends, estatística e recibos. Não especifica um novo algoritmo quântico nem reivindica vantagem quântica geral.

Termos usados:

- **Variante:** implementação ou estratégia alternativa sob avaliação, como simulador, backend de hardware ou estimador estatístico.
- **Evidência:** entradas observadas, contagens, metadados de execução e dados necessários para reproduzir uma decisão.
- **Promoção:** autorização explícita de uma variante para uso num perfil de execução determinado, após passar os gates definidos.
- **Recusa:** resultado de primeira classe quando contrato, evidência, confiança ou integridade não satisfazem as condições declaradas.
- **Evolução natural:** processo controlado de propor, comparar, testar e eventualmente promover variantes, mantendo invariantes verificáveis.

## 2. Princípios de projeto

1. **A semântica trivalente é invariável.** `1` e `0` exprimem conclusões segundo a regra declarada; `REFUSED` (ou um estado inconclusivo específico da interface) impede que evidência insuficiente seja convertida em certeza.
2. **A regra precede os dados.** Limiar, margem, erro tolerado, orçamento de amostras e política de parada devem ser fixados antes da inspeção dos resultados, para limitar escolhas oportunistas.
3. **Reprodutibilidade tem prioridade sobre adaptação.** Uma variante não pode alterar silenciosamente parâmetros ou selecionar a própria métrica de sucesso depois de observar o resultado.
4. **Falha fechada.** Entrada inválida, backend não confiável, protocolo incompleto, recibo inconsistente ou incerteza não resolvida não produzem aprovação.
5. **Proveniência explícita.** Um recibo deve permitir identificar a regra, a versão, o compromisso da entrada, o modo de execução e as limitações da evidência.
6. **Simulação não é hardware.** Resultados simulados devem ser rotulados e nunca apresentados como medição física.
7. **Integridade não é autoria nem correção.** SHA3-256 permite verificar integridade do conteúdo; por si s��, não prova quem o produziu nem que a computação está correta.
8. **Evolução sem regressão semântica.** Uma otimização só é elegível se preservar os contratos ou declarar uma nova versão incompatível.

## 3. Arquitetura proposta

```text
Programa / consulta / payload de evidência
                    │
                    ▼
       1. Front-end e validação de contrato
                    │ forma canônica
                    ▼
       2. Planejador de decisão e política
          (orçamento, regra, perfil, limites)
                    │ plano imutável
                    ▼
       3. Adaptador de backend selecionado
       ┌────────────┼───────────────┐
       ▼            ▼               ▼
   simulador     QPU/hardware   evidência externa
       └────────────┼───────────────┘
                    ▼
       4. Auditor estatístico e de confiança
                    │ evidência qualificada
                    ▼
       5. Núcleo de decisão trivalente
                    │ veredito + motivo
                    ▼
       6. Canonicalizador e recibo Z-QEA
                    │
                    ▼
       7. Verificador independente / cadeia de recibos
                    │
                    ▼
       8. Avaliação de variantes e gates de evolução
```

As camadas 1–7 representam uma decomposição lógica compatível com as capacidades e interfaces descritas no repositório; os limites exatos entre módulos podem diferir na implementação. A camada 8 é uma proposta para o processo evolutivo, não uma afirmação de componente existente.

### 3.1 Front-end e contrato

O front-end aceita um programa ou payload, valida sintaxe, tipos, esquema e parâmetros, e produz uma forma canônica. Erros de sintaxe e violações de contrato devem ser explícitos. Antes da execução, o contrato deve fixar ao menos: objetivo da decisão, chave/resultado alvo, limiar, margem ou `delta`, quantidade máxima de amostras, regra estatística, modo de backend e política de falha.

### 3.2 Planejador e política

O planejador transforma o contrato em um plano imutável de execução. Pode verificar orçamento e pré-condições de confiança antes de invocar um oráculo ou backend. Se uma pré-condição falhar, deve recusar com motivo registrável e evitar trabalho computacional desnecessário, quando aplicável.

### 3.3 Backends intercambiáveis

Backends implementam uma interface explícita: recebem um plano, retornam evidência e metadados, e identificam se o resultado é simulado, derivado de dados fornecidos ou medido em hardware. O backend não escolhe o limiar nem define sozinho o significado do veredito. O adaptador também não deve descartar falhas, contagens ou metadados relevantes.

### 3.4 Auditoria estatística e decisão

O auditor verifica consistência entre contagens e número de tiros, calcula as margens segundo a regra contratada e avalia condições de confiança. Por exemplo, para a regra proporcional documentada, a estimativa `p̂` e a margem `ε` determinam a decisão: `1` quando `p̂ − ε > threshold`; `0` quando `p̂ + ε < threshold`; caso contrário, evidência inconclusiva. Entradas inválidas ou insuficientes podem resultar em `REFUSED`, com motivo explícito.

Essa regra é um exemplo já documentado para um caminho de decisão; não deve ser confundida com uma regra universal para todos os circuitos, protocolos ou backends. Em particular, qualquer regra adaptativa deve declarar previamente seus pressupostos e política de parada. Múltiplas hipóteses ou testes exigem controle de erro familiar compatível com o protocolo.

### 3.5 Recibo e verificação

O recibo canônico deve comprometer, no mínimo, entrada relevante, plano, regra e versão, evidência ou referência verificável à evidência, veredito, motivo de recusa, modo de execução, metadados do backend e vínculo com recibo anterior, quando houver. Campos exatos devem seguir a especificação vigente do projeto. O verificador recalcula canonicalização e selo e valida consistência estrutural e semântica.

O hash detecta alteração do conteúdo coberto, mas não garante proveniência autenticada. Assinatura digital, gestão de chaves, HSM e validação normativa são temas separados; não se deve insinuar que estejam aplicados a todos os recibos sem confirmação explícita da implementação e da configuração.

## 4. Ciclo de evolução natural

A evolução proposta é uma esteira de pesquisa e lançamento, não uma otimização autônoma em produção:

1. **Observar:** coletar resultados de testes e benchmarks, incluindo recusas, falhas e divergências; não usar apenas latência ou taxa de aprovação.
2. **Formular uma hipótese:** descrever qual propriedade se pretende melhorar e quais invariantes não podem mudar.
3. **Gerar uma variante isolada:** alterar backend, algoritmo auxiliar ou otimização com identidade e versão próprias; não substituir o caminho estável.
4. **Testar em referência determinística:** executar casos conhecidos, fronteiras, entradas inválidas, sementes fixas e regressões sem depender de hardware.
5. **Testar adversarialmente:** explorar bandas cinzentas, ruído, contagens inconsistentes, seleção múltipla, reordenação, corrupção de recibos e falhas do backend.
6. **Comparar com protocolo pré-registrado:** estabelecer métricas, amostra, limites e critério de aprovação antes da execução. Incluir falsos positivos e recusas, não apenas desempenho médio.
7. **Reproduzir independentemente:** repetir a avaliação por um processo separado, quando a maturidade e o risco do uso justificarem.
8. **Promover por decisão revisável:** registrar aprovadores, evidências, versão e escopo permitido. Promoção não significa que a variante seja correta em todo domínio.
9. **Monitorar e reverter:** comparar operação com os critérios publicados; regressões, falha de integridade ou evidência incompatível levam a desativação segura e retorno à variante anterior.

O ciclo não seleciona automaticamente variantes com base em recompensas opacas. Qualquer aprendizado ou seleção automática futura exigiria um objetivo auditável, limites de ação, avaliação independente, rastreamento de dados e aprovação explícita antes da promoção.

## 5. Invariantes e critérios de aceitação

Uma variante candidata só deve avançar se demonstrar, no perfil declarado:

- **Semântica:** casos de referência preservam `1`, `0` e recusa conforme a regra; incerteza não se converte em aprovação.
- **Contrato:** entradas inválidas e limites de orçamento são recusados sem execução indevida.
- **Estatística:** margem, `delta`, regra de parada e correção de testes múltiplos são explícitos e reproduzíveis.
- **Equivalência:** otimizações de circuito, transpilações ou kernels passam testes de equivalência pertinentes; equivalência não se infere apenas de benchmark.
- **Recibos:** recibos válidos verificam; alteração de campos cobertos é detectada; versões e regras são identificáveis.
- **Proveniência:** simulação, dados fornecidos e execução física são distinguidos sem ambiguidade.
- **Reprodutibilidade:** comando, versão, dependências, sementes e artefatos necessários são registrados.
- **Segurança operacional:** credenciais não são incorporadas à imagem ou ao recibo; limites de rede, arquivos e recursos pertencem ao ambiente de implantação e devem ser configurados separadamente.
- **Reversibilidade:** a variante estável permanece disponível enquanto a candidata é avaliada.

Nenhum teste finito prova correção universal. Resultados devem ser descritos pelo domínio, protocolo e evidência realmente testados.

## 6. Interfaces recomendadas para versões futuras

Como orientação de evolução, definir contratos versionados para:

- `DecisionRequest`: objetivo, parâmetros pré-declarados, limites e identificador do protocolo;
- `ExecutionPlan`: forma canônica do pedido, versão da regra, backend permitido e orçamento;
- `Evidence`: contagens ou resultados, origem, modo, metadados e referências de execução;
- `DecisionResult`: veredito, motivo, estatísticas reportadas e identificador da regra;
- `Receipt`: compromisso canônico de entradas, plano, evidência e resultado;
- `VerifierResult`: validade estrutural, integridade e checagens semânticas, reportadas separadamente.

Esses nomes são sugestões de design, não nomes de API prometidos. Compatibilidade deve ser explícita: consumidores precisam saber qual versão de esquema e regra estão verificando.

## 7. Fases de implementação sugeridas

| Fase | Entrega proposta | Gate para avançar |
|---|---|---|
| A — inventário | Mapear módulos, formatos de recibo, regras e responsabilidades existentes | Matriz de componentes com referências ao código e lacunas identificadas |
| B — contratos | Documentar esquemas versionados e taxonomia de motivos | Testes de validação, compatibilidade e casos inválidos |
| C — conformidade | Criar bateria comum para backends e verificadores | Mesmos casos de referência e recibos reproduzíveis |
| D — variantes | Integrar candidatos isolados sob configuração explícita | Comparação pré-registrada sem regressão semântica |
| E — promoção controlada | Registrar critérios, revisão e reversão | Evidências e escopo de promoção auditáveis |
| F — avaliação externa | Obter reprodução independente para alegações relevantes | Relato público de protocolo, resultados e limitações |

As fases não implicam cronograma nem compromisso de lançamento. A equipe deve priorizar lacunas de segurança e integridade antes de adicionar seleção adaptativa complexa.

## 8. Riscos e limites

- **Confundir adaptação com aprendizado seguro:** a seleção pós-hoc pode introduzir viés; parâmetros e critérios precisam ser pré-declarados.
- **Excesso de confiança em recibos:** um selo íntegro não valida o algoritmo, a origem do dado nem a execução física.
- **Comparações injustas:** hardware, shots, ruído, versão de transpiler e métricas devem ser comparáveis e divulgados.
- **Mudança de semântica:** alterar o significado de `REFUSED`, margens ou thresholds sem nova versão quebra reprodutibilidade.
- **Dependência de evidência limitada:** amostras finitas e um pequeno número de execuções de hardware não autorizam generalizações universais.
- **Escopo de sandbox:** contêineres são uma camada operacional, não uma prova de isolamento contra todos os ataques. O isolamento depende da configuração e da plataforma.
- **Maturidade:** o próprio projeto descreve seu estado como experimental e muito inicial. A arquitetura proposta não eleva esse nível de maturidade.

## 9. Conclusão

A evolução natural do ZEPHIRUM deve ocorrer pela composição de contratos explícitos, variantes isoladas, testes adversariais, avaliação pré-registrada e promoção revisável. O núcleo da proposta não é maximizar a quantidade de decisões afirmativas: é melhorar desempenho ou cobertura sem apagar incerteza, proveniência e limites estatísticos.

A regra de evolução é simples: **uma variante pode ser mais rápida, mais portátil ou mais eficiente; não pode ser menos honesta sobre o que sabe**. Toda decisão continua sujeita a uma regra declarada, a uma evidência verificável e à possibilidade legítima de recusa.

## Referências do repositório

- [README — arquitetura, semântica, quickstart e limitações](../README.md)
- [Documentação de maturidade](MATURITY.md)
- [Protocolo estatístico ZYQL](ZYQL_STATISTICAL_PROTOCOL.md)
- [Especificação de recibos](receipts.md)
- [Provas e evidências](PROOFS.md)
- [Benchmark da camada de decisão](../benchmarks/BENCHMARK.md)
- [Arquitetura de contêineres](../docker/README.md)

---

Este whitepaper é uma proposta de arquitetura e processo. Para alegações sobre capacidades existentes, prevalecem o código, os testes e a documentação normativa do repositório.
