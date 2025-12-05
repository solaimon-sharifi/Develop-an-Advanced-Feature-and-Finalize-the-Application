#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
else
  COMPOSE_CMD="docker-compose"
fi

$COMPOSE_CMD down --remove-orphans
$COMPOSE_CMD build --no-cache
$COMPOSE_CMD up -d
$COMPOSE_CMD logs --follow --tail 100
