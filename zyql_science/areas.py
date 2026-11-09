#!/usr/bin/env python3
"""Aplicações por grande área. Cada função devolve Decisao — a régua é a mesma."""
from __future__ import annotations
from motor import decidir_proporcao, decidir_comparacao, decidir_energia, Decisao, MIN_N

# ---------- CIÊNCIAS BIOLÓGICAS ----------
def diagnostico(positivos: int, testados: int, sensibilidade_alvo: float,
                delta: float = 0.05) -> Decisao:
    """Um teste diagnóstico atinge a sensibilidade alvo? Decide ou recusa."""
    return decidir_proporcao(positivos, testados, sensibilidade_alvo, delta,
                             regra="diagnostico-v1")

def ensaio_dois_bracos(eventos_a: int, n_a: int, eventos_b: int, n_b: int,
                       delta: float = 0.05) -> Decisao:
    """Braço A tem taxa de evento maior que braço B? Recusa se a amostra não sustenta."""
    return decidir_comparacao((eventos_a, n_a), (eventos_b, n_b), delta, regra="ensaio-v1")

def sobrevivencia_ou_taxa(observados: int, expostos: int, referencia: float,
                          delta: float = 0.05) -> Decisao:
    return decidir_proporcao(observados, expostos, referencia, delta, regra="taxa-v1")

# ---------- CIÊNCIAS EXATAS ----------
def energia_menor(candidato_1: tuple[float, float], candidato_2: tuple[float, float]) -> Decisao:
    """Qual estrutura tem energia menor, com barras de incerteza explícitas."""
    return decidir_energia(candidato_1, candidato_2)

def medicao_concorda(valor: float, incerteza: float, referencia: float,
                     tolerancia: float) -> Decisao:
    """A medição concorda com a referência dentro da tolerância declarada?"""
    dif = abs(valor - referencia); margem = incerteza + tolerancia
    v = "1" if dif <= margem else "0"
    return Decisao(v, p=round(dif, 10), epsilon=round(margem, 10), regra="concordancia-v1")

# ---------- CIÊNCIAS HUMANAS ----------
def diferenca_entre_corpus(a: tuple[int, int], b: tuple[int, int],
                           delta: float = 0.05) -> Decisao:
    """Duas amostras de texto diferem na frequência do fenômeno estudado?"""
    return decidir_comparacao(a, b, delta, regra="corpus-v1")

def concordancia_anotadores(concordantes: int, pares: int, alvo: float,
                            delta: float = 0.05) -> Decisao:
    """A concordância entre anotadores atinge o mínimo exigido?"""
    return decidir_proporcao(concordantes, pares, alvo, delta, regra="concordancia-anotadores-v1")

def resposta_de_politica(atingidos: int, populacao_amostrada: int, meta: float,
                         delta: float = 0.05) -> Decisao:
    """A meta social foi atingida na amostra, com margem declarada?"""
    return decidir_proporcao(atingidos, populacao_amostrada, meta, delta, regra="politica-v1")
