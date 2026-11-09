# Lote científico em hardware — 2026-11-09

## Objetivo
Provar, em hardware quântico real, as duas decisões do programa de referência
(oráculo constante e oráculo balanceado) e a correlação de um par emaranhado,
com recibo assinado e verificável por terceiro.

## Método
1. Três circuitos: Deutsch-Jozsa constante, Deutsch-Jozsa balanceado e Bell.
2. 1024 tiros por circuito, regra proporção-v1 com delta 0,05.
3. Recibo v1 assinado em Ed25519; chave privada fora do repositório.

## Resultados
1. Constante: p(000) = 0.9678 -> veredito 1
2. Balanceado: p(000) = 0.0000 -> veredito 0
3. Bell: fidelidade de correlação = 0.9404
4. Incerteza de Hoeffding por circuito: 0.0424

## Validação
1. Assinatura verificada com a chave pública anexa: ASSINATURA_VALIDA
2. Cadeia de recibos verificada: integral
3. Evidência bruta anexa em EVIDENCIA.json, com hash comprometido no recibo.

## Limitações
1. Uma execução por circuito; não é estudo estatístico de estabilidade.
2. Ruído do plano aberto está presente e aparece no p(000) constante abaixo de 1.
3. Recibo prova origem e integridade, não segurança da execução.
4. Identificador do dispositivo e da execução ficam em registro interno, fora do material público.
