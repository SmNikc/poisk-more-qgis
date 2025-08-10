#!/usr/bin/env bash
set -euo pipefail

# Usage: bash scripts/apply_ruleset.sh owner=SmNikc repo=poisk-more-qgis token=YOUR_GH_TOKEN

for arg in "$@"; do
  key="${arg%%=*}"; val="${arg#*=}"
  case "$key" in
    owner) OWNER="$val" ;;
    repo)  REPO="$val"  ;;
    token) TOKEN="$val" ;;
    *) echo "Unknown arg: $arg" ; exit 1 ;;
  esac
done

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI 'gh' is required"; exit 1
fi
export GITHUB_TOKEN="$TOKEN"

echo "[Ruleset] Applying example ruleset to $OWNER/$REPO"
gh api -X POST repos/$OWNER/$REPO/rulesets \
  -H "Accept: application/vnd.github+json" \
  -F data@scripts/ruleset_main.json
echo "Done."