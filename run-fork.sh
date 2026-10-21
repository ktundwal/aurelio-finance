#!/usr/bin/env bash
set -euo pipefail

readonly FORK_BRANCH="feature/copilot-sdk-provider"
readonly FORK_URL="https://github.com/ktundwal/aurelio-finance.git"
readonly UPSTREAM_URL="https://github.com/LosaLosSantos/aurelio-finance.git"
readonly ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'EOF'
Usage: ./run-fork.sh [--demo]

Starts the maintained GitHub Copilot fork of Aurelio.
  --demo  Use invented data in backend/demo.db.

The script updates only from the fork's validated Copilot branch. It configures
an `upstream` remote for later manual merges, but never merges upstream/main
while starting the application.
EOF
}

case "${1:-}" in
  -h|--help)
    usage
    exit 0
    ;;
  ""|--demo)
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

for command in git node uv copilot; do
  if ! command -v "$command" >/dev/null 2>&1; then
    printf 'Missing prerequisite: %s\n' "$command" >&2
    exit 1
  fi
done

node_major="$(node --version | sed -E 's/^v([0-9]+).*/\1/')"
if (( node_major < 22 )); then
  printf 'Node.js 22 or newer is required; found %s.\n' "$(node --version)" >&2
  exit 1
fi

cd "$ROOT"

if [[ -n "$(git status --porcelain)" ]]; then
  printf 'The checkout has uncommitted changes; refusing to switch or update branches.\n' >&2
  exit 1
fi

origin_url="$(git remote get-url origin 2>/dev/null || true)"
if [[ "$origin_url" != "$FORK_URL" ]]; then
  printf 'Expected origin to be %s; found %s.\n' "$FORK_URL" "${origin_url:-none}" >&2
  exit 1
fi

if git remote get-url upstream >/dev/null 2>&1; then
  git remote set-url upstream "$UPSTREAM_URL"
else
  git remote add upstream "$UPSTREAM_URL"
fi

git fetch origin "$FORK_BRANCH"
if [[ "$(git branch --show-current)" != "$FORK_BRANCH" ]]; then
  git switch "$FORK_BRANCH"
fi
git merge --ff-only "origin/$FORK_BRANCH"

printf '\nUsing %s at %s.\n' "$FORK_BRANCH" "$(git rev-parse --short HEAD)"
printf 'Copilot CLI: %s\n\n' "$(copilot --version | sed -n '1p')"

exec "$ROOT/start.sh" "$@"
