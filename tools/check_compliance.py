#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Portão de conformidade do ZEPHIRUM. Sai com código 1 se qualquer item estiver vermelho."""
import glob, json, pathlib, re, sys, tomllib
try:
    import tomllib  # 3.11+
except ModuleNotFoundError:  # 3.10
    import tomli as tomllib

RAIZ = pathlib.Path(__file__).resolve().parents[1]
ITENS = []


def item(nome, ok, evidencia=""):
    ITENS.append((nome, bool(ok), evidencia))


def ler(p):
    return (RAIZ / p).read_text(errors="ignore")


# 1. SPDX em todo código Python
pys = [p for p in RAIZ.rglob("*.py") if ".git" not in p.parts]
sem = [str(p.relative_to(RAIZ)) for p in pys if "SPDX-License-Identifier" not in p.read_text(errors="ignore")]
item("SPDX em todos os .py", not sem, f"{len(pys)-len(sem)}/{len(pys)}" + (f"; faltam: {sem[:3]}" if sem else ""))

# 2. versão única
py = tomllib.loads(ler("pyproject.toml"))
versao = py["project"]["version"]
abertas = {
    "pyproject.toml": versao,
    "VERSION": ler("VERSION").strip(),
    "docs/openapi.json": json.loads(ler("docs/openapi.json"))["info"]["version"],
}
try:
    abertas["api/server.py"] = re.search(r'APP_VERSION\s*=\s*"([^"]+)"', ler("api/server.py")).group(1)
except Exception:
    abertas["api/server.py"] = "?"
div = {k: v for k, v in abertas.items() if v != versao}
item("versão única nas fontes", not div, f"{versao}" if not div else f"divergem: {div}")

# 3. gate de CI roda a suíte inteira
ci = ler(".github/workflows/ci.yml")
item("CI roda a suíte completa", "pytest tests -q" in ci, "pytest tests -q" if "pytest tests -q" in ci else "ausente")

# 4. make test roda a suíte inteira
mk = ler("Makefile")
item("make test roda a suíte completa", "pytest tests" in mk, "pytest tests" if "pytest tests" in mk else "ausente")

# 5. cobrança desligada por padrão
bill = ler("api/billing.py")
item("cobrança desligada por padrão", 'os.environ.get("ZYQL_BILLING", "off")' in bill, "ZYQL_BILLING default off")

# 6. privacidade coerente (sem cobrança ativa, seção de modo gratuito)
priv = ler("PRIVACY.md")
item("privacidade declara modo gratuito", "8-A" in priv and "modo gratuito" in priv, "PRIVACY.md §8-A")

# 7. SLA de segurança
item("SLA de resposta em SECURITY.md", "Prazo de resposta" in ler("SECURITY.md"), "SECURITY.md")

# 8. dependências com faixa (nada solto)
deps = py["project"]["dependencies"]
soltas = [d for d in deps if not re.search(r"[<>~=]", d)]
item("dependências com faixa de versão", not soltas, "todas fixadas" if not soltas else f"soltas: {soltas}")

# 9. nenhum segredo literal no repositório
PARTES = ["sk_" + "live_", "sk_" + "test_", "wh" + "sec_[A-Za-z0-9]", "AK" + "IA[0-9A-Z]{8}", "BEGIN [A-Z ]*PRIV" + "ATE KEY"]
padrao = re.compile("(" + "|".join(PARTES) + ")")
vaz = [str(p.relative_to(RAIZ)) for p in RAIZ.rglob("*")
       if p.is_file() and p.suffix in (".py", ".md", ".json", ".yml", ".toml", ".cff", ".h")
       and ".git" not in p.parts and padrao.search(p.read_text(errors="ignore"))
       and "tests/" not in str(p)]
item("nenhum segredo literal", not vaz, "limpo" if not vaz else f"em: {vaz[:3]}")

# 10. header C não promete API inexistente
h = ler("src/zephirum.h")
item("zephirum.h marcado como não implementado", "NAO IMPLEMENTADO" in h, "cabeçalho declarativo")

# 11. margem familiar não é vendida como garantia
mat = ler("docs/MATURITY.md")
item("margem familiar marcada como não demonstrada", "revisão matemática" in mat or "revisão matemática" in mat.lower(), "MATURITY.md")

# 12. pipeline declara consultas clássicas
pl = ler("experiments/pipeline_demo/pipeline.py")
item("pipeline declara consultas clássicas", "consultas_classicas" in pl, "pipeline_demo")


# 13. licença coerente (LICENSE é Apache-2.0 e nenhum doc diz MIT)
lic = ler("LICENSE")[:400]
docs_md = list(pathlib.Path("docs").glob("*.md"))
ofensores = [f.name for f in docs_md if "MIT license" in f.read_text()]
item("licença coerente (Apache-2.0 único)", "Apache License" in lic and not ofensores,
     "Apache-2.0 em LICENSE e docs" if not ofensores else f"dizem MIT: {ofensores}")

# 14. ML-DSA implementado e não mais anunciado como roadmap
item("ML-DSA declarado como implementado", "DECLARED ROADMAP" not in ler("README.md") and "def assinar(" in ler("src/zqea_sig.py"),
     "README + zqea_sig")

# 15. ancoragem externa existe e é testada
item("ancoragem externa do último elo", "def verificar_ancora(" in ler("src/zqea_sig.py") and pathlib.Path("tests/test_ancoragem_e_metadados.py").exists(),
     "zqea_sig + testes")

largura = max(len(n) for n, _, _ in ITENS)
falhas = 0
for nome, ok, ev in ITENS:
    print(f"{'VERDE ' if ok else 'VERMELHO'} | {nome.ljust(largura)} | {ev}")
    falhas += 0 if ok else 1
print(f"\n{len(ITENS)-falhas}/{len(ITENS)} itens verdes")
sys.exit(1 if falhas else 0)
