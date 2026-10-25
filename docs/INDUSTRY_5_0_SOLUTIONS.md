# ZEPHIRUM na Indústria 5.0 — soluções de automação com decisão trivalente

Posicionamento honesto: a computação quântica não substitui o CLP da sua
fábrica. O que a ZEPHIRUM (ZYQL) oferece à automação industrial é o que
nenhum sistema binário oferece: um **veredito trivalente (1 / 0 / REFUSED)
com motivo rastreável e recibo criptográfico selado** — a decisão de
automação passa a carregar a própria prova de quando ela é confiável e
de quando ela deve ser recusada. Cada solução abaixo aponta para a
evidência já medida em hardware real (recibos encadeados na cadeia Z-QEA).

## 1. Interlock de segurança (ESD) — plataformas e subestações

Problema: desligamento de emergência decide *trip* vs *não-trip* sobre
sensores fusionados (pressão, vibração, gás). Trip falso custa produção;
trip perdido custa vidas. A lógica de votação clássica (2oo3) não explica
*por que* os dados são insuficientes.

Solução ZEPHIRUM: fusão de sensores com banda de confiança (Hoeffding,
correção de família). O REFUSED volta com motivo: NOISE (saturação do
sensor), NO_SINGLE_PHASE (leituras ambíguas), INSUFFICIENT_CONFIDENCE
(dados demais ruidosos), NO_SIGNAL. O engenheiro de segurança recebe
"segure o estado e investigue o sensor X", não um palpite.

Evidência: estimação de fase com banda de recusa executada em QPU
supercondutor (recibo 2759b0e0) — duas recusas, dois motivos diferentes,
no mesmo primitivo: exatamente a taxonomia que um interlock exige.

## 2. Certificação de decisões de manutenção preditiva

Problema: o modelo preditivo diz "troque o rolamento". Com que confiança?
Quem assina a ordem de serviço responde por ela por anos.

Solução ZEPHIRUM: o fluxo de sensores alimenta o núcleo trivalente; a
decisão de manutenção sai com banda estatística declarada e recibo selado
(SHA3-256 + assinatura pós-quântica ML-DSA-44 — relevante para ativos
industriais com vida útil de 20+ anos, além do horizonte de segurança das
assinaturas clássicas contra adversário quântico). Registro imutável da
árvore de decisão: auditoria, compliance e rastreio regulatoratório.

Evidência: independência de fluxo de medição medida em hardware real
(lag-1 = -0.0104, família de lags com correção de família, recibo ea1cc335);
cadeia de recibos íntegra verificável por qualquer terceiro.

## 3. Gate de qualidade na usinagem

Problema: peça aprovada/reprovada na linha; peça limítrofe é decidida no
"achismo" do operador ou num limiar cego.

Solução ZEPHIRUM: aprova / reprova / **RECUSA a decisão** quando a medida
cai na banda de indecisão — com motivo e margem declarada. A peça
limítrofe vira "inspecionar com instrumento de maior resolução", não um
booleano arriscado. Cada lote de calibração de máquina sai com recibo
encadeado: a calibração de hoje assina a de amanhã.

Evidência: regra de ruído recusando medida fora da banda em hardware real
(DJ selado, p0=0.8999 < 0.97 => REFUSED, recibo ea1cc335).

## 4. Onde NÃO vendemos quântica (muralha da honestidade)

- Otimização combinatória de escalonamento/logística: heurísticas
  clássicas (MILP, meta-heurísticas) ganham nas escalas industriais de
  hoje. Não propomos QAOA como substituto do planejador da fábrica.
- Previsão de defeitos por QML: XGBoost sobre 10k amostras ganha de QNN
  na escala atual de dados. A QML da casa tem veredito de treino —
  REFUSED barren plateau é resultado, não derrota escondida — mas não
  vendemos superioridade.
- A vantagem competitiva real é auditabilidade: **decisões de automação
  com prova selada**, o que reduz risco regulatório, custo de auditoria
  e tempo de resposta em investigação de incidentes.

## 5. Kit de prova (falsificável, gratuito, sem hardware do cliente)

Toda a pilha roda no plano gratuito: núcleo trivalente em Python puro,
recibos Z-QEA verificáveis por ação pública, demonstração executável de
RECUSED-vs-binário. Um piloto começa com o problema do cliente, o núcleo
decidindo offline sobre histórico de sensores dele, e o relatório de
decisões recusadas com motivo — a análise que o CLP dele não faz.

---

*Cada alegação técnica deste documento aponta para um recibo selado
verificável no repositório. Sem recibo, não está escrito aqui.*
