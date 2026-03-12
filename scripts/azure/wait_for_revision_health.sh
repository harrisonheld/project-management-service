#!/usr/bin/env bash
set -euo pipefail

RESOURCE_GROUP="${1:?resource group required}"
APP_NAME="${2:?container app name required}"
TIMEOUT_SECONDS="${3:-300}"
SLEEP_SECONDS=10
ELAPSED=0

latest_revision() {
  az containerapp revision list \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --query "sort_by([], &properties.createdTime)[-1].name" -o tsv
}

is_healthy() {
  local rev="$1"
  local healthy
  healthy=$(az containerapp revision show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$APP_NAME" \
    --revision "$rev" \
    --query "properties.healthState" -o tsv)

  [[ "$healthy" == "Healthy" ]]
}

REVISION=$(latest_revision)
if [[ -z "$REVISION" ]]; then
  echo "No revision found for app: $APP_NAME"
  exit 1
fi

echo "Waiting for revision to become healthy: $REVISION"

while [[ "$ELAPSED" -lt "$TIMEOUT_SECONDS" ]]; do
  if is_healthy "$REVISION"; then
    echo "Revision is healthy: $REVISION"
    exit 0
  fi

  echo "Revision not healthy yet. waited=${ELAPSED}s revision=$REVISION"
  sleep "$SLEEP_SECONDS"
  ELAPSED=$((ELAPSED + SLEEP_SECONDS))
done

echo "Timed out waiting for healthy revision: $REVISION"
exit 1
