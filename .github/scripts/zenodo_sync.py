#!/usr/bin/env python3
"""Sync a GitHub release of zephirum-lang to the Zenodo concept DOI.

Creates a new Zenodo version of the software record (concept DOI
10.5281/zenodo.23632019) containing the release source archive, with
metadata synchronized from the GitHub release. No manual login required:
runs entirely on the ZENODO_TOKEN repository secret.

Exit codes: 0 = synced (new version DOI printed); 1 = refused (with reason).
"""
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.request
import uuid

ZENODO = "https://zenodo.org/api/deposit/depositions"
CONCEPT_RECORD = "23632020"          # first record of concept 10.5281/zenodo.23632019
CONCEPT_DOI = "10.5281/zenodo.23632019"
REPO = "SerenaSolutions/zephirum-lang"

zenodo_token = os.environ["ZENODO_TOKEN"]
github_token = os.environ.get("GITHUB_TOKEN", "")
tag = sys.argv[1]
release_notes = sys.argv[2] if len(sys.argv) > 2 else ""

def api(url, data=None, method="GET", headers=None, raw=False):
    h = {"Authorization": "Bearer " + zenodo_token,
         "Content-Type": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(
        url, data=json.dumps(data).encode() if isinstance(data, (dict, list)) else data,
        method=method, headers=h)
    try:
        resp = urllib.request.urlopen(req)
        if raw:
            return resp.read()
        return json.load(resp)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"[REFUSED] Zenodo API {method} {url} -> {e.code}: "
                         f"{e.read().decode()[:400]}")

def gh(url, method="GET", data=None, ctype="application/json"):
    h = {"Authorization": "Bearer " + github_token,
         "Accept": "application/vnd.github+json",
         "Content-Type": ctype}
    req = urllib.request.Request(
        "https://api.github.com" + url,
        data=json.dumps(data).encode() if data is not None else None,
        method=method, headers=h)
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"[REFUSED] GitHub API {url} -> {e.code}")

# 0) idempotencia: a tag ja foi sincronizada?
def gh_api(url):
    h2 = {"Authorization": "Bearer " + zenodo_token}
    r2 = urllib.request.Request(url, headers=h2)
    try:
        return json.load(urllib.request.urlopen(r2))
    except urllib.error.HTTPError:
        return None
latest = gh_api(f"https://zenodo.org/api/records/{CONCEPT_DOI.split('zenodo.')[1]}")
if latest and latest.get("metadata", {}).get("version") == tag:
    print(f"[SKIP] release {tag} ja sincronizada no Zenodo ({latest['id']})")
    raise SystemExit(0)

# 1) download do tarball da tag (arquivo publico do release)
tar_name = f"zephirum-lang-{tag}.tar.gz"
tar_url = f"https://github.com/{REPO}/archive/refs/tags/{tag}.tar.gz"
req = urllib.request.Request(tar_url, headers={"User-Agent": "zenodo-sync"})
try:
    tarball = urllib.request.urlopen(req).read()
except urllib.error.HTTPError as e:
    raise SystemExit(f"[REFUSED] tag {tag} nao encontrada ({e.code})")

# 2) nova versao a partir do registro atual do conceito
draft = api(f"{ZENODO}/{CONCEPT_RECORD}/actions/newversion", {}, "POST")
did = draft["id"]
meta = api(f"{ZENODO}/{did}")["metadata"]

# 3) limpeza da regra da casa: nenhuma marca de terceiro em superficie do projeto
desc = meta.get("description", "")
desc = re.sub(r"validated on three IBM Heron superconducting processors "
              r"\(ibm_fez, ibm_marrakesh, ibm_kingston\)",
              "validated on three real superconducting QPUs (backend and job "
              "identifiers are sealed inside the ML-DSA-44 receipts)", desc)
desc += (f"<p><strong>Release {tag}.</strong> Source archive synchronized "
         f"automatically from GitHub by the ZENODO_SYNC action. "
         f"Repository: <a href=\"https://github.com/{REPO}\">{REPO}</a> · "
         f"Project site: <a href=\"https://serenasolutions.github.io/\">"
         f"serenasolutions.github.io</a></p>")
if release_notes:
    safe = release_notes[:2000]
    safe = re.sub(r"<[^>]+>", "", safe)
    desc += f"<p><em>Release notes: {safe}</em></p>"

upd = dict(meta)
upd["version"] = tag
upd["description"] = desc
api(f"{ZENODO}/{did}", {"metadata": upd}, "PUT")

# 4) upload do tarball (multipart classico)
boundary = uuid.uuid4().hex
body = (f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"file\"; filename=\"{tar_name}\"\r\n"
        f"Content-Type: application/gzip\r\n\r\n").encode() + tarball + \
       f"\r\n--{boundary}--\r\n".encode()
api(f"{ZENODO}/{did}/files", body, "POST",
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})

# 5) publicar
pub = api(f"{ZENODO}/{did}/actions/publish", {}, "POST")
version_doi = pub["doi"]
print(f"[SYNCED] release {tag} -> {version_doi} "
      f"(concepto permanente: {CONCEPT_DOI})")

# 6) comentar o DOI na release do GitHub
release = gh(f"/repos/{REPO}/releases/tags/{tag}")
gh(f"/repos/{REPO}/issues/{release['id']}/comments", "POST",
   {"body": f"Archived on Zenodo: {version_doi} (concept DOI {CONCEPT_DOI}). "
            f"Synced automatically by the ZENODO_SYNC action."})
print(f"[NOTED] DOI comentado na release {tag}")
