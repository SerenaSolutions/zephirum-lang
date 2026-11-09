# Decisão verificável em hardware quântico ruidoso

## Objetivo

Formalizar e medir um protocolo em que toda decisão produzida por um programa
quântico seja **reproduzível localmente**, **delimitada por incerteza declarada** e
**atribuível a um emissor por assinatura criptográfica**, usando a linguagem ZYQL.

## Método

1. Decisão tratada como função parcial de cinco estados: 1, 0, REFUSED, INCONCLUSIVE, ERROR.
2. Limite de erro por desigualdade de Hoeffding, com delta declarado (FATO matemático).
3. Execução em QPU física e confronto com referência exata calculada localmente.
4. Recibo v1 assinado em Ed25519, com chave privada fora do repositório.
5. Verificação por terceiro que não fala com o emissor (chave pública apenas).

## Resultados

1. H1 (512 tiros): constante p(000)=0,9727 -> veredito 1; balanceado p(000)=0,0000 -> veredito 0.
2. Lote 2026-11-09 (2048 tiros): constante p(000)=0,9644 -> 1; balanceado p(000)=0,0000 -> 0.
3. Bell (1024 tiros): fidelidade de correlação 0,9404.
4. Baterias exatas: Steane [[7,1,3]] 42/42 síndromes; Shor exato em inteiros; QPE H2 com desvio 6,6e-4 abaixo da resolução teórica.
5. Incerteza de Hoeffding: 0,0424 com 1024 tiros e delta 0,05.

## Validação

1. Assinatura Ed25519 verificada com chave pública (7/7 casos de adulteração detectados).
2. Fail-closed: app gerado recusa subir se o manifesto for alterado (código 2).
3. Adaptador OpenQASM 3 com ida e volta idêntica (10/10) e conferência por analisador externo.
4. Auditoria cega por agente independente sobre o pacote de execução.

## Limitações

1. Uma execução por circuito; não é estudo estatístico de estabilidade.
2. Ausência de qubit lógico em hardware: as provas de correção são exatas em simulação.
3. Solovay-Kitaev incompleto: ângulo arbitrário sem precisão declarada.
4. Recibo prova origem e integridade, não segurança da execução.
