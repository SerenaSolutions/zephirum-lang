#!/usr/bin/env bash
# Espelha os repositórios da casa para o Entire (Git-compatible forge).
#
# Uso:
#   ENTIRE_TOKEN=... ./scripts/mirror_to_entire.sh --dry-run   # mostra o plano
#   ENTIRE_TOKEN=... ./scripts/mirror_to_entire.sh             # espelha de verdade
#
# A BASE é parametrizável porque a página do namespace responde em entire.com:
#   ENTIRE_BASE=https://entire.com/et ENTIRE_NS=ravi-quantinum ./scripts/mirror_to_entire.sh
#
# Regra: nada é enviado sem token. O script NUNCA inventa credencial e nunca
# segue adiante com falha parcial silenciosa: cada repo é reportado um por um.
set -uo pipefail

BASE="${ENTIRE_BASE:-https://entire.com/et}"
NS="${ENTIRE_NS:-ravi-quantinum}"
ORG="${GITHUB_ORG:-SerenaSolutions}"
DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1

if [ -z "${ENTIRE_TOKEN:-}" ] && [ "$DRY" -eq 0 ]; then
  echo "ERRO: ENTIRE_TOKEN ausente. Crie um token no Entire e salve na plataforma"
  echo "      como segredo ENTIRE_TOKEN (nunca cole token no chat)."
  exit 2
fi

# /users/ funciona tanto para conta pessoal quanto para organização (SerenaSolutions é conta)
repos=$(curl -s -H "Authorization: token ${GITHUB_TOKEN}" \
  "https://api.github.com/users/${ORG}/repos?per_page=100" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
if isinstance(d, dict):                      # erro da API não vira lista vazia silenciosa
    print('ERRO_API:' + str(d.get('message')), file=sys.stderr); sys.exit(1)
print('\n'.join(r['name'] for r in d if not r.get('archived')))
") || { echo "falha ao listar repos"; exit 1; }

ok=0; falhou=0
for r in $repos; do
  src="https://github.com/${ORG}/${r}.git"
  dst="${BASE}/${NS}/${r}.git"
  if [ "$DRY" -eq 1 ]; then
    echo "[dry] git push ${src} -> ${dst}"
    ok=$((ok+1)); continue
  fi
  # push com token só no header: a URL final não carrega credencial
  if git -c http.extraheader="Authorization: Bearer ${ENTIRE_TOKEN}" \
        push --quiet "${dst}" "refs/remotes/origin/*:refs/heads/*" 2>/tmp/entire_err_$r; then
    echo "[ok]   $r"; ok=$((ok+1))
  else
    echo "[falha] $r -> $(head -1 /tmp/entire_err_$r)"; falhou=$((falhou+1))
  fi
done
echo "---"
echo "espelhados: $ok | falhas: $falhou | dry-run=$DRY"
[ "$falhou" -eq 0 ] || exit 1
