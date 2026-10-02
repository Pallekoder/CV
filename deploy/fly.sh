#!/usr/bin/env bash
# Put the world on Fly.io, always on, with a volume so it keeps itself.
#   FLY_API_TOKEN=... deploy/fly.sh [app-name] [region]
# Needs flyctl (https://fly.io/docs/flyctl/install/). No local Docker needed:
# the image is built on Fly's builders.
set -euo pipefail
cd "$(dirname "$0")/.."
APP="${1:-the-world-$(head -c 4 /dev/urandom | od -An -tx1 | tr -d ' \n')}"
REGION="${2:-ams}"
FLY="${FLYCTL:-flyctl}"

if ! $FLY apps list --json 2>/dev/null | grep -q "\"Name\": *\"$APP\""; then
  $FLY apps create "$APP" --org personal
fi
sed -i.bak "s/^app = .*/app = \"$APP\"/; s/^primary_region = .*/primary_region = \"$REGION\"/" fly.toml && rm -f fly.toml.bak

if ! $FLY volumes list -a "$APP" --json 2>/dev/null | grep -q '"name": *"world_data"'; then
  $FLY volumes create world_data -a "$APP" --region "$REGION" --size 1 --yes
fi

if [ -z "${WORLD_TOKEN:-}" ]; then
  WORLD_TOKEN="$(head -c 24 /dev/urandom | base64 | tr -d '/+=' | head -c 24)"
  echo "steering token (keep it; the page asks for it once): $WORLD_TOKEN"
fi
$FLY secrets set -a "$APP" WORLD_TOKEN="$WORLD_TOKEN" --stage >/dev/null

$FLY deploy -a "$APP" --remote-only --ha=false --yes
echo
echo "the world is running at https://$APP.fly.dev"
