# ZYQL Science — mapa de aplicação por área do conhecimento

Versão 1.0 · 2026-11-09

## Objetivo

Mostrar, área por área, o que a linguagem ZYQL entrega **hoje** de forma verificável, e
separar isso do que permanece especificação ou hipótese. A propriedade que se aplica a
todas as ciências não é velocidade: é *decisão auditável com erro declarado*.

## Método

1. O motor recebe evidência (contagens, medidas, valores com incerteza).
2. Aplica regra versionada com limite de Hoeffding para o desvio (FATO matemático).
3. Devolve um de cinco estados: 1, 0, REFUSED, INCONCLUSIVE ou ERROR.
4. Toda decisão gera recibo assinado em Ed25519, verificável por terceiro.

Uma decisão sem incerteza declarada não é emitida: o motor recusa antes de adivinhar.

## Resultados por área (medidos nesta entrega: 15/15 casos)

### Ciências biológicas
1. Sensibilidade de teste diagnóstico contra alvo: decide quando a amostra sustenta, e
   recusa quando não sustenta. Caso real: 1950/2000 com alvo 0,90 decide; 372/400 com o
   mesmo alvo e a mesma proporção relativa **recusa** — a diferença é só o tamanho da amostra.
2. Comparação de dois braços de ensaio: 160/400 contra 80/400 decide; 100/400 contra
   96/400 fica INCONCLUSIVE.
3. Taxa por expostos contra referência: mesmo motor, regra própria.
4. Estado: IMPLEMENTADO para as três funções. ESPECIFICAÇÃO para genômica e docking.

### Ciências exatas
1. Comparação de energia entre candidatos com barras de incerteza: decide quando as barras
   não se cruzam, fica INCONCLUSIVE quando se cruzam. Números reais da bateria de H2
   (−1,851199 ± 0,000656 Ha).
2. Concordância entre medição e referência dentro de tolerância declarada.
3. Correção de erro: provas exatas por enumeração (Steane, superfície d=3).
4. Estado: IMPLEMENTADO para decisão e verificação; EXPERIMENTAL em hardware real;
   HIPÓTESE para vantagem quântica em otimização e química.

### Ciências humanas
1. Comparação de frequência entre dois corpora com margem: 620/1000 contra 410/1000 decide;
   505/1000 contra 498/1000 fica INCONCLUSIVE.
2. Concordância entre anotadores contra mínimo exigido (900/1000 com alvo 0,80 decide).
3. Avaliação de meta de política pública sobre amostra, com recusa quando a amostra é
   pequena demais (20 de 25 recusa).
4. Estado: IMPLEMENTADO como método estatístico verificável. As amostras citadas são
   sintéticas e estão rotuladas como tal: não são dados de pesquisa de campo.

## Validação

1. Bateria com 15 casos nas três áreas: 15 aprovados, incluindo casos de recusa.
2. Três recibos assinados em Ed25519, um por área, verificados com chave pública.
3. Comparação com tendência matemática: 4 casos iniciais falharam porque a expectativa do
   autor estava errada, não o motor — o motor recusou afirmar o que a amostra não sustentava.

## Limitações

1. Não substitui norma regulatória de área: um diagnóstico clínico exige validação própria,
   e um estudo humano exige comitê de ética. A ZYQL entrega rastro verificável, não licença.
2. As amostras dos exemplos são sintéticas; nenhum dado de paciente ou de participante foi usado.
3. O motor decide sobre evidência fornecida; não corrige viés de amostragem.
4. A parte quântica permanece coprocessador opcional, e vantagem quântica segue como hipótese.

## Próximos passos

1. Conectar as funções biológicas a um formato padrão de dados de ensaio.
2. Levar a decisão de energia para hardware com o mesmo recibo assinado.
3. Publicar o verificador público apontando para recibos científicos.
