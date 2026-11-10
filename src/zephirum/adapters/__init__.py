# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Serena Quantum Solutions
"""Camada 2 — adaptadores de transito.

Regra de arquitetura: o nucleo ZYQL (camada 0) nao importa fornecedor algum.
Todo dialogo com SDK externo acontece aqui, e somente aqui. Remover esta
camada deve deixar o nucleo intacto; e o teste de isolamento que garante isso.

Adaptador oficial disponivel hoje:

    zephirum.adapters.qiskit_backend
"""

__all__ = ["qiskit_backend"]
