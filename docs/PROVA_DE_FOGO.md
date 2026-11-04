# PROVA DE FOGO — ZYQL / ZEPHIRUM em hardware IBM

Pacote fechado para um agente externo rodar e conferir, sem conhecer o núcleo e
sem poder "ajustar" o resultado. A regra de decisão e a banda são declaradas no
próprio script, antes da execução, e o recibo carrega os counts crus para que
qualquer terceiro recompute tudo.

## Primeira execução no silício (04/11/2026)

| item | valor |
| --- | --- |
| backend | ibm_marrakesh |
| job | dblnbem74qds73dqqmtg |
| shots por circuito | 1024 |
| epsilon declarado | 0.05 |
| banda Hoeffding | 0.0429 |
| oracle const-0 | **veredito 0** (p_zero 0.9873) |
| oracle const-1 | **veredito 1** (p_zero 0.9932, p_um 0.9961) |
| oracle balanceado | **REFUSED · BALANCED_ORACLE** (p_zero 0.0010) |
| porta GHZ n=3 | fidelidade **0.9131**, dispositivo aprovado |
| confere com o esperado | **true** |
| selo SHA3-256 | `84abc306017b0573d20e39a3d6479326b4fecd5adf8327ea5a88058c33d7fff3` |

Recibo completo: `experiments/prova_de_fogo_receipt.json`.

## O que o teste exige de quem roda

1. Duas medidas independentes, ambas no hardware:
   interferência (Deutsch-Jozsa com âncilla em |−⟩) decide a **classe**;
   leitura direta de f(0) decide o **valor**.
2. Porta de integridade GHZ n=3: fidelidade abaixo de 0,80 veta a rodada inteira,
   mesmo com as duas medidas limpas. O dispositivo precisa provar que está vivo
   antes de o veredito valer.
3. Toda incerteza cai na banda de Hoeffding `sqrt(ln(2/eps)/(2*shots))`. Dentro da
   banda não existe palpite: o resultado é REFUSED com motivo nomeado.

## Contrato para rodar como agente autônomo

```bash
git clone https://github.com/SerenaSolutions/zephirum-lang
cd zephirum-lang
pip install qiskit qiskit-ibm-runtime
export IBM_QUANTUM_TOKEN=<token do laboratório>
python3 experiments/prova_de_fogo.py --shots 1024 --out experiments/prova_de_fogo_receipt.json
```

Saída de máquina: JSON em `--out`, exit code `0` quando confere com o esperado,
`1` quando diverge, `3` quando o job termina mal, `4` quando estoura a espera.

## Como conferir sem confiar em nós

```bash
python3 experiments/verificar_prova_de_fogo.py experiments/prova_de_fogo_receipt.json
```

O verificador recomputa o selo SHA3-256 sobre o recibo, reconfere cada veredito a
partir dos counts crus usando a mesma regra declarada, e recusa quando:

- o selo não bate (recibo alterado),
- o p_entrada_zero não sustenta a classe alegada,
- o f(0) não sustenta o valor alegado,
- a porta GHZ falhou e algum veredito saiu como 1 ou 0.

Ou seja: mudar uma vírgula no recibo derruba a verificação.

## Limites declarados

1. n=3 qubits de entrada. Não é demonstração de escala.
2. A banda cobre erro amostral, não viés sistemático do dispositivo.
3. Ruído correlacionado entre qubits está fora do escopo.
4. Oráculos adversariais fora das classes constante e balanceada não são cobertos.

Quem repete o teste e obtém algo diferente tem, no recibo, os counts para mostrar
exatamente onde discorda. É esse o ponto: a discordância fica auditável.
