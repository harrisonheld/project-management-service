#!/usr/bin/env bash
set -euo pipefail

RESOURCE_GROUP="${1:?resource group required}"
APP_NAME="${2:?container app name required}"
PREVIOUS_REVISION="${3:-}"

if [[ -z "$PREVIOUS_REVISION" ]]; then
  echo "No previous revision provided. Unable to roll back."
  exit 1
fi

echo "Rolling back traffic to previous revision: $PREVIOUS_REVISION"

az containerapp revision set-mode \
  --resource-group "$RESOURCE_GROUP" \
  --name "$APP_NAME" \
  --mode multiple

az containerapp ingress traffic set \
  --resource-group "$RESOURCE_GROUP" \
  --name "$APP_NAME" \
  --revision-weight "$PREVIOUS_REVISION=100"

echo "Rollback complete. Active traffic now points to: $PREVIOUS_REVISION"
