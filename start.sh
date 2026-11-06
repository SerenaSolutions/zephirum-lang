#!/usr/bin/env bash
# Sobe o gateway ZYQL no Replit. A chave vem do ambiente, nunca do codigo.
set -e
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -e ".[api,pq]"
if [ -z "$ZYQL_API_TOKEN" ]; then
  echo "AVISO: ZYQL_API_TOKEN vazio. Emita uma chave com: python -m api.gateway issue --name replit --scopes read,decide,qsr,lang"
fi
exec uvicorn api.gateway:app --host 0.0.0.0 --port "${PORT:-8000}"
