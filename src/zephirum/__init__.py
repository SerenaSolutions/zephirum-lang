"""ZEPHIRUM / ZYQL: ponto de entrada publico do pacote.

O codigo historico vive em modulos de topo (zqgate, zkernel, zyql_*). Este
pacote existe para que `import zephirum` funcione e para expor a versao.
"""
from importlib import import_module
from importlib.metadata import PackageNotFoundError, version as _version

try:
    __version__ = _version("zephirum")
except PackageNotFoundError:  # execucao direto da arvore, sem instalacao
    __version__ = "0.0.0"

_SUBMODULOS = (
    "zqgate", "zkernel", "zquantum", "quantum_types", "shot_auditor",
    "zyql_lisp", "zyql_protocols", "zyql_runtime", "zyql_witness",
    "zyql_world3", "zyql_worldscale", "zyql_auditkit", "zyql_cirq",
    "zyql_zne", "zyql_mps", "zyql_robust", "zyql_selfverified",
    "zyql_quantum_gate", "zyql_rag_layer", "zyql_llm_compress",
    "zyqml_core", "zqea_kem", "zqea_sig", "oq3", "battery_ci",
)
__all__ = ["__version__"] + list(_SUBMODULOS)


def __getattr__(nome):
    if nome in _SUBMODULOS:
        mod = import_module(nome)
        globals()[nome] = mod
        return mod
    raise AttributeError(f"modulo 'zephirum' nao tem atributo '{nome}'")


def __dir__():
    return sorted(__all__)
