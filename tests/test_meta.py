"""Meta-teste: consistencia de versao entre pyproject, badge do README e CHANGELOG."""
import re, sys, os
ROOT = os.path.join(os.path.dirname(__file__), "..")

py = open(os.path.join(ROOT, "pyproject.toml")).read()
v_py = re.search(r'version = "([^"]+)"', py).group(1)

readme = open(os.path.join(ROOT, "README.md")).read()
v_rd = re.search(r'badge/version-([0-9.]+)', readme).group(1)

ch = open(os.path.join(ROOT, "CHANGELOG.md")).read()
v_ch = re.search(r'## \[([0-9.]+)\]', ch).group(1)

assert v_py == v_rd == v_ch, f"INCONSISTENTE: pyproject={v_py} readme={v_rd} changelog={v_ch}"
print(f"test_meta: versao consistente {v_py} em pyproject/README/CHANGELOG")
