# Relatório técnico: ZEPHIRUM no ecossistema Qiskit

**Data:** 2026-11-09 · **Autoria:** Serena Quantum Solutions
**Versão congelada:** 2.5.7 · **Licença:** Apache-2.0
**Escopo:** registro do que foi incorporado, do que foi medido e do que segue em aberto.

Este relatório é escrito para ser conferido, não para ser acreditado. Todo número aqui
tem comando de reprodução, hash de recibo ou identificador de job. Onde não foi
possível reverificar um fato, ele não é afirmado.

---

## 1. Sumário

| Pergunta | Resposta verificada |
|---|---|
| Entramos no ecossistema Qiskit? | **Sim.** PR #1433 mergeado em `Qiskit/ecosystem`, commit `d327b86` |
| Foi aprovado o quê? | Um arquivo de metadado de membro, 81 linhas, categoria SDK |
| Foi validada a linguagem? | **Não por terceiros.** A camada de decisão tem validação interna selada |
| A semântica foi avaliada pela comunidade? | Não. Nenhuma revisão técnica externa até hoje |
| É certificação IBM? | **Não.** É entrada em lista curada mantida pela comunidade Qiskit |

---

## 2. O que foi exatamente incorporado

Verificado hoje na API do GitHub:

| Campo | Valor |
|---|---|
| Pull request | #1433 — "Add ZEPHIRUM" |
| Repositório de destino | `Qiskit/ecosystem`, branch `main` |
| Branch de origem | `submission-b2b5fe46` |
| Commit de merge | `d327b86e21a4ac794842519951387bb9013abda1` |
| Data do merge | 2026-11-09T16:00:00Z |
| Merge executado por | `1ucian0` (Luciano Bello) |
| Autor do commit de merge | `qiskit-bot` (automação do GitHub) |
| Arquivos alterados | **1**: `resources/members/zephirum_b2b5fe46.toml` (+81, −0) |
| Commits no PR | 17 (13 do bot, 4 de Luciano Bello) |

O arquivo é metadado: nome, URL, descrição, rótulos, interfaces, pacote PyPI, UUID,
categoria, maturidade e status. **Nenhuma linha de código ZYQL foi incorporada ao
Qiskit.** O que passou a existir é o registro de que o projeto é membro.

Declarado pelo próprio arquivo, e vale repetir porque é o retrato honesto do momento:

```
category = "SDK"
maturity = "experimental"
status   = "Very Early Project"
```

O ecossistema nos classifica como experimental e em estágio muito inicial. Isso não é
diminuição: é o que assinamos ao submeter, e é o que deve constar de qualquer anúncio.

---

## 3. Contribuição de Luciano Bello

Registro explícito, porque crédito de revisão não é detalhe de cortesia:

| Commit | Autor | Mensagem |
|---|---|---|
| (merge) | `1ucian0` | merge do PR #1433 |
| `e1babe49` | Luciano Bello | reformat |
| `57e063a8` | Luciano Bello | Update resources/members/zephirum_b2b5fe46.toml |
| `672dc63f` | Luciano Bello | Apply suggestion from @1ucian0 |
| `d1f61b4b` | Luciano Bello | Apply batched suggestions from code review |

**Nuance registrada com honestidade:** as revisões do PR constam com estado `COMMENTED`,
não `APPROVED`. A aceitação se deu pelo merge, não por uma review formal de aprovação.
Dizer "aprovado por Luciano Bello" é impreciso; o correto é "mergeado por Luciano Bello,
após revisão e edições dele no arquivo".

Uma afirmação que circulou anteriormente sobre um commit `c50f973` no gerador de
metadados `pypi.py` **não foi reverificada nesta passagem** e por isso não é afirmada aqui.

---

## 4. O que já foi medido, com recibo

### 4.1 Camada de decisão (semântica trivalente)

Protocolo selado **antes** da execução: `ed50c6122539df136300ca6e12484e3ecd8ac759cad964461856e11525be7314`

| Métrica | Valor |
|---|---|
| Casos executados | 3630 |
| Hipóteses testadas | 7 (H1–H7) |
| Violações | 0 |
| Vereditos 1 / 0 / INCONCLUSIVE | 1461 / 1461 / 642 |
| ε observado | 0.02371 a 0.203453 |
| Recibos distintos | 3564 (sem colisão) |
| Recibo agregado | `62664883d35592ef9eb63cae9c27c36c383025bc17f6c3551e02284ce5579219` |

Relatório público: <https://zephirum.vercel.app/validacao>

### 4.2 Suíte e integridade de engenharia

| Item | Estado |
|---|---|
| Testes | 222 passando (215 da suíte + 7 do guard de metadado) |
| Python no CI | 3.10, 3.11 e 3.12 |
| Provas em formato de script | 17/17 |
| Guard de metadado | verde, rodando diariamente às 07:00 UTC |
| Coleta do pytest | estável (arquivos de prova não abortam mais a coleta) |

### 4.3 Execução em QPU (registro anterior)

Job `dbouacgou4as73csnbb0` em `ibm_marrakesh`, 2.048 tiros: constante com p₀ = 0,978,
balanceada com p₀ = 0,0073. **Uma execução por circuito.** Sustenta que o dispositivo
se comportou como esperado naquela janela; não sustenta desempenho, nem repetibilidade,
nem estatística.

### 4.4 Demonstração ZYQL + Qiskit (executável)

Circuito GHZ de 3 qubits, `AerSimulator`, 2.048 tiros, seed 1701, pergunta declarada
antes de rodar: *a fração GHZ passa de 0,80?*

| Cenário | Profundidade | Fração GHZ | Veredito | ε | Recibo |
|---|---|---|---|---|---|
| ideal | 4 | 1.0000 | **1** | 0.03001 | `2c9eacd9b7a54a7d5d001a0aef7cd220…` |
| ruido 2% | 6 | 0.9746 | **1** | 0.03001 | `12bd488ca7bfd94fcead4a3c1623be8e…` |
| controle - | 3 | 0.5171 | **0** | 0.03001 | `8cb2e5defd9867bab68faf3e002bafb1…` |

O controle negativo é o ponto: com o terceiro entrelaçamento removido de propósito, a
fração cai para 0.5171 e a camada responde **0**. Se respondesse 1,
a linguagem estaria quebrada. Ela distingue estado bom de estado quebrado, e diz quando
os tiros não bastam.

---

## 5. O que ainda não foi demonstrado

Lista curta, e é a parte mais importante do relatório:

1. **Autoria dos recibos.** Hoje o recibo prova integridade (SHA3-256), não autoria.
   ML-DSA-44 é a issue #68 e depende de decisão de custódia de chave.
2. **Reprodução por terceiro.** Nenhum agente externo rodou o protocolo até agora.
   Sem isso, tudo acima é medição própria.
3. **Estatística em hardware.** Uma execução por circuito não é estudo. Falta protocolo
   de repetição com intervalo de confiança declarado e selo antes do submit.
4. **Avaliação da semântica pela comunidade.** O merge registrou um membro; ninguém
   revisou a trivalência, a gramática ou os recibos.
5. **Cinco defeitos do Zyclotron** além do limiar (já corrigido), ainda sem lista formal.

Transformar qualquer um desses cinco em "concluído" sem evidência seria exatamente
o que este relatório existe para impedir.

---

## 6. Reprodução

```bash
git clone https://github.com/SerenaSolutions/zephirum-lang
cd zephirum-lang

# 1. validação da camada de decisão (confere o selo e aborta se o protocolo mudou)
PYTHONPATH=src python3 validacao/validar_semantica.py

# 2. demonstração ZYQL + Qiskit (ideal, ruído 2% e controle negativo)
PYTHONPATH=src python3 demo/demonstracao_qiskit.py

# 3. guard de metadado contra PyPI e Qiskit/ecosystem
python3 scripts/verificar_metadado.py
```

---

## 7. Limitações declaradas

- O domínio de 3630 casos é finito e discreto: ausência de contraexemplo não é prova universal.
- A demonstração usa simulador com ruído declarado, não hardware.
- A entrada no ecossistema é metadado; não implica endosso da IBM, nem da Qiskit,
  nem de qualquer mantenedor sobre as capacidades da linguagem.
- Este relatório foi produzido pelo mesmo time que construiu o sistema. Validação
  independente é o item 2 da seção 5, e segue aberta.

---

> Perguntar primeiro. Provar depois. Computar por último.
