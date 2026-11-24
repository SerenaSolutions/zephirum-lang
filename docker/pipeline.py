# SPDX-License-Identifier: Apache-2.0
"""Roda a pilha inteira: núcleo, ZCA, portão QASM3, QuanSo OS e tentativa de QPU.

Emite um relatório único em JSON e um resumo legível. Nada é inventado: cada etapa
registra o que realmente aconteceu, inclusive as recusas.
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

BASE = os.environ.get("ZEPHIRUM_URL", "http://127.0.0.1:8099")
RELATORIO = {"iniciado_utc": datetime.now(timezone.utc).isoformat(), "etapas": []}


def http(rota, corpo=None, timeout=30):
    url = BASE + rota
    dados = None if corpo is None else json.dumps(corpo).encode()
    req = urllib.request.Request(url, data=dados, method="GET" if corpo is None else "POST")
    if dados:
        req.add_header("content-type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {"erro": str(e)[:160]}


def etapa(nome, ok, detalhe):
    RELATORIO["etapas"].append({"etapa": nome, "ok": ok, "detalhe": detalhe,
                                "em_utc": datetime.now(timezone.utc).isoformat()})
    marca = "OK " if ok else "!! "
    print(f"[{marca}] {nome}: {detalhe}")


# 1. núcleo vivo
codigo, saude = http("/health")
etapa("nucleo", codigo == 200 and saude.get("estado") == "ok",
      f"HTTP {codigo} · versao {saude.get('versao')} · rotas {len(saude.get('rotas', []))}")

# 2. motor ZCA — as 6 regras
casos = [
    ("frac_eq", {"a": "1/3", "b": "2/6"}, 1),
    ("proporcao", {"a": "2", "b": "5", "c": "7"}, 1),
    ("porcento", {"p": "15", "v": "240"}, 1),
    ("limite", {"valor": "1.2", "limite": "1"}, 1),
    ("prazo", {"validade": "2026-12-01", "hoje": "2026-11-21"}, 0),
    ("ppm_mgm3", {"ppm": "25", "massa_molar": "46.01"}, 1),
]
resultados_zca = {}
for op, args, esperado in casos:
    _, r = http("/zca", {"op": op, "args": args})
    resultados_zca[op] = {"veredito": r.get("veredito"), "resultado": r.get("resultado"),
                          "hash": (r.get("cert") or {}).get("hash")}
    etapa(f"zca:{op}", r.get("veredito") == esperado,
          f"veredito {r.get('veredito')} · {json.dumps(r.get('resultado'), ensure_ascii=False)[:70]}")

# 3. portão QASM3
circuitos = {
    "bell_clifford": ("OPENQASM 3.0;\nqubit[2] q;\nh q[0];\ncx q[0],q[1];\nmeasure q -> c;", 1),
    "h_t_nao_clifford": ("OPENQASM 3.0;\nqubit[1] q;\nh q[0];\nt q[0];\nmeasure q -> c;", 0),
    "porta_inventada": ("OPENQASM 3.0;\nqubit[1] q;\nfrobnicate q[0];", "REFUSED"),
}
for nome, (qasm, esperado) in circuitos.items():
    _, r = http("/qasm3", {"qasm": qasm})
    etapa(f"qasm3:{nome}", r.get("veredito") == esperado,
          f"veredito {r.get('veredito')} · {(r.get('motivo') or r.get('ref') or '')[:60]}")

# 4. QuanSo OS — suíte real no repositório
repo = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "quanso", "QuanSo"))
if os.path.isdir(repo):
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "--tb=no"],
                       cwd=repo, capture_output=True, text=True, timeout=300)
    ultima = [l for l in (p.stdout or "").splitlines() if l.strip()][-1:] or [""]
    etapa("quanso_os", p.returncode == 0, f"{ultima[0][:90]}")
else:
    etapa("quanso_os", False, "repositório QuanSo não encontrado no caminho esperado")

# 5. QPU — tenta de verdade e registra a recusa
qasm_qpu = circuitos["h_t_nao_clifford"][0]
_, ensaio = http("/ensaio", {"qasm": qasm_qpu, "backend": "ibm_brisbane"})
etapa("qpu:ensaio", ensaio.get("permitido_para_qpu") is True,
      f"veredito {ensaio.get('veredito')} · permitido={ensaio.get('permitido_para_qpu')} · {(ensaio.get('detalhe') or '')[:50]}")

_, submissao = http("/submit", {"qasm": qasm_qpu, "backend": "ibm_brisbane", "shots": 1024})
submeteu = submissao.get("veredito") == 1
etapa("qpu:submit", submeteu,
      f"veredito {submissao.get('veredito')} · codigo {submissao.get('codigo')} · {(submissao.get('motivo') or '')[:70]}")

RELATORIO["fim_utc"] = datetime.now(timezone.utc).isoformat()
RELATORIO["resumo"] = {
    "etapas": len(RELATORIO["etapas"]),
    "ok": sum(1 for e in RELATORIO["etapas"] if e["ok"]),
    "falhas": [e["etapa"] for e in RELATORIO["etapas"] if not e["ok"]],
    "zca": resultados_zca,
    "qpu_submeteu": submeteu,
    "qpu_codigo": submissao.get("codigo"),
}
print("\nRESUMO:", json.dumps(RELATORIO["resumo"], ensure_ascii=False)[:300])
with open("relatorio_execucao.json", "w") as f:
    json.dump(RELATORIO, f, ensure_ascii=False, indent=2)
print("relatorio: relatorio_execucao.json")
