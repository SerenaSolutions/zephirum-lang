#!/usr/bin/env bash
# Deposito da nova versao v1.9.0 no Zenodo (requer ZENODO_TOKEN do dono).
# Fluxo: nova versao do record 23302046 -> upload zip + tese -> metadata -> publish
set -euo pipefail
RECORD=23302046
Z="https://zenodo.org/api"
[ -z "${ZENODO_TOKEN:-}" ] && { echo "ERRO: export ZENODO_TOKEN=... primeiro"; exit 1; }
DIR="$(cd "$(dirname "$0")" && pwd)"
# 1. cria o draft de nova versao
DRAFT_ID=$(curl -s -X POST "$Z/records/$RECORD/versions" -H "Authorization: Bearer $ZENODO_TOKEN" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['id']); import sys as s" )
echo "draft: $DRAFT_ID"
# 2. upload dos arquivos
for f in "$DIR/zephirum-software-v1.9.0.zip"; do
  curl -s -X PUT "$Z/records/$DRAFT_ID/files/files/$(basename $f)" \
    -H "Authorization: Bearer $ZENODO_TOKEN" -H "Content-Type: application/octet-stream" --data-binary @"$f" >/dev/null
done
echo "arquivos enviados"
# 3. metadata + publish
curl -s -X PATCH "$Z/records/$DRAFT_ID/draft" -H "Authorization: Bearer $ZENODO_TOKEN" \
  -H "Content-Type: application/json" --data @"$DIR/v190_metadata.json" >/dev/null
curl -s -X POST "$Z/records/$DRAFT_ID/draft/actions/publish" -H "Authorization: Bearer $ZENODO_TOKEN" | head -c 400
echo; echo "PUBLICADO. DOI da versao nova aparece acima."
