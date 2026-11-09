# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Ligacao com o nucleo C++ (RF-04 e RF-07 na camada nativa).

Se a biblioteca compartilhada nao estiver compilada, o modulo declara ausencia
em vez de esconder a queda para Python.
"""
import ctypes, pathlib

_LIB = pathlib.Path(__file__).resolve().parents[2] / "cpp" / "libzyql.so"


def disponivel():
    return _LIB.exists()


def _lib():
    if not disponivel():
        raise RuntimeError("libzyql.so ausente: rode make -C cpp")
    l = ctypes.CDLL(str(_LIB))
    l.zyql_rota.argtypes = [ctypes.c_int] * 4
    l.zyql_rota.restype = ctypes.c_int
    l.zyql_veredito.argtypes = [ctypes.c_double, ctypes.c_double]
    l.zyql_veredito.restype = ctypes.c_int
    return l


ROTAS = {1: "CLASSICO", 2: "QUANTICO", 0: "REFUSED"}
VEREDITOS = {1: 1, 0: 0, 2: "REFUSED"}


def rota(tem_classica, estrutural, profundidade, orcamento):
    return ROTAS[_lib().zyql_rota(int(tem_classica), int(estrutural),
                                  int(profundidade), int(orcamento))]


def veredito(p0, epsilon):
    return VEREDITOS[_lib().zyql_veredito(float(p0), float(epsilon))]
