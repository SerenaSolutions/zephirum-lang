"""Q-ROUTE: roteamento com busca de Grover e veredito trivalente do ZYQL."""
try:  # fonte unica da verdade: o metadado do pacote instalado
    from importlib.metadata import version as _v
    __version__ = _v("zephirum")
except Exception:  # rodando direto do repositorio, sem instalacao
    __version__ = "0+dev"
