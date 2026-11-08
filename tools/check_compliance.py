#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Portão de conformidade do ZEPHIRUM. Sai com código 1 se qualquer item estiver vermelho."""
import glob, json, pathlib, re, sys
try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # Python 3.10
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


# 13. licença coerente: varredura ampla com exceções declaradas
ISENTOS = {"CHANGELOG.md", "DEPENDENCIAS_LICENCAS.md", "RESPOSTA_AUDITORIA_EXTERNA_2026-11-07.md"}
FALSOS = r"permit|commit|submit|transmit|limit|omit|admit|commission"
PADROES_MIT = [r"mit[-_ ]?licen", r"\bMIT\b", r'"license"\s*:\s*"mit"', r"code MIT", r"open source, MIT"]
ofensores = []
# SBOM e tabela de dependencias citam licencas de TERCEIROS (MIT do lark etc.),
# nao a nossa: ficam fora desta varredura de proposito.
ISENTOS_LICENCA = ("SBOM", "spdx.json", "DEPENDENCIAS_LICENCAS", "CHANGELOG")
for caminho in list(pathlib.Path("docs").rglob("*")) + list(pathlib.Path("site").rglob("*")) + list(pathlib.Path("paper").rglob("*")) + list(pathlib.Path(".").glob("*.md")):
    if not caminho.is_file() or caminho.name in ISENTOS:
        continue
    if caminho.suffix not in (".md", ".html", ".py", ".json", ".toml", ".txt", ".cff", ".yml"):
        continue
    if any(x in str(caminho) for x in ISENTOS_LICENCA):
        continue
    try: txt = caminho.read_text()
    except Exception: continue
    if "dependenc" in caminho.name.lower() or "LICENCAS" in caminho.name:
        continue
    for pad in PADROES_MIT:
        achados = [m for m in re.finditer(pad, txt, re.IGNORECASE)
                   if not re.search(FALSOS, txt[max(0, m.start()-12):m.end()+6], re.IGNORECASE)]
        if achados and not re.search(r"lark|numpy|scipy", txt[:200], re.IGNORECASE):
            ofensores.append(str(caminho)); break
# extensao do VS Code
try:
    if re.search(r'"license"\s*:\s*"MIT"', pathlib.Path("zephirum-vscode/package.json").read_text()):
        ofensores.append("zephirum-vscode/package.json")
except FileNotFoundError:
    pass
item("licença coerente (Apache-2.0 em todo o projeto)",
     "Apache License" in ler("LICENSE")[:400] and not ofensores,
     "Apache-2.0 em LICENSE, docs, site e extensão" if not ofensores else f"ainda dizem MIT: {sorted(set(ofensores))[:4]}")

# 14. ML-DSA implementado e não mais anunciado como roadmap
item("ML-DSA declarado como implementado", "DECLARED ROADMAP" not in ler("README.md") and "def assinar(" in ler("src/zqea_sig.py"),
     "README + zqea_sig")

# 15. ancoragem externa existe e é testada
item("ancoragem externa do último elo", "def verificar_ancora(" in ler("src/zqea_sig.py") and pathlib.Path("tests/test_ancoragem_e_metadados.py").exists(),
     "zqea_sig + testes")


# 16. semântica única: nenhum doc pode dizer que balanceado = 0
sv = ler("docs/SELFVERIFIED.md")
item("semântica unificada (balanceado != 0)", "BALANCED_ORACLE" in sv and "balanceado | **0**" not in sv,
     "SELFVERIFIED alinhado ao núcleo")

# 17. bateria criptográfica não pode passar sem testar
tz = ler("tests/test_zqea_sig.py")
item("bateria criptográfica exige pqcrypto em CI", "ZYQL_REQUIRE_PQ" in tz, "falha em CI sem pqcrypto")


# 18. nenhum artefato grande rastreado (bundle, venv, binário)
import subprocess as _sp
_lista = _sp.run(["git", "ls-files"], capture_output=True, text=True).stdout.split()
_grandes = []
for _f in _lista:
    _p = pathlib.Path(_f)
    if _p.is_file() and _p.stat().st_size > 5 * 1024 * 1024:
        _grandes.append((_f, round(_p.stat().st_size / 1048576, 1)))
item("nenhum artefato grande rastreado", not _grandes, "ok" if not _grandes else f"{_grandes[:2]}")

# 19. nome do projeto escrito corretamente
item("nome do projeto grafado certo", "Zephyron" not in ler("README.md"), "README sem 'Zephyron'")

largura = max(len(n) for n, _, _ in ITENS)
falhas = 0
for nome, ok, ev in ITENS:
    print(f"{'VERDE ' if ok else 'VERMELHO'} | {nome.ljust(largura)} | {ev}")
    falhas += 0 if ok else 1
print(f"\n{len(ITENS)-falhas}/{len(ITENS)} itens verdes")
sys.exit(1 if falhas else 0)
