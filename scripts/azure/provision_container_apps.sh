#!/usr/bin/env bash
set -euo pipefail

# Usage:
# ./scripts/azure/provision_container_apps.sh \
#   <resource-group> <location> <acr-name> <log-analytics-name> <aca-env-name> <aca-app-name>
#
# Example:
# ./scripts/azure/provision_container_apps.sh rg-ece282 eastus acrpms123 log-pms aca-env-pms aca-pms

RESOURCE_GROUP="${1:?resource group required}"
LOCATION="${2:?azure region required}"
ACR_NAME="${3:?acr name required}"
LOG_ANALYTICS_NAME="${4:?log analytics workspace name required}"
ACA_ENV_NAME="${5:?container app environment name required}"
ACA_APP_NAME="${6:?container app name required}"

IMAGE_NAME="project-management-service"
INITIAL_TAG="bootstrap"
INITIAL_IMAGE="$ACR_NAME.azurecr.io/$IMAGE_NAME:$INITIAL_TAG"

az extension add --name containerapp --upgrade --yes

az group create --name "$RESOURCE_GROUP" --location "$LOCATION"

if ! az acr show --resource-group "$RESOURCE_GROUP" --name "$ACR_NAME" >/dev/null 2>&1; then
  az acr create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$ACR_NAME" \
    --sku Basic \
    --admin-enabled false
fi

# Push bootstrap image so first ACA create has a valid image reference.
az acr login --name "$ACR_NAME"
docker pull hello-world:latest
docker tag hello-world:latest "$INITIAL_IMAGE"
docker push "$INITIAL_IMAGE"

az monitor log-analytics workspace create \
  --resource-group "$RESOURCE_GROUP" \
  --workspace-name "$LOG_ANALYTICS_NAME" \
  --location "$LOCATION"

LOG_ANALYTICS_CUSTOMER_ID=$(az monitor log-analytics workspace show \
  --resource-group "$RESOURCE_GROUP" \
  --workspace-name "$LOG_ANALYTICS_NAME" \
  --query customerId -o tsv)

LOG_ANALYTICS_SHARED_KEY=$(az monitor log-analytics workspace get-shared-keys \
  --resource-group "$RESOURCE_GROUP" \
  --workspace-name "$LOG_ANALYTICS_NAME" \
  --query primarySharedKey -o tsv)

if ! az containerapp env show --name "$ACA_ENV_NAME" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
  az containerapp env create \
    --name "$ACA_ENV_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --logs-workspace-id "$LOG_ANALYTICS_CUSTOMER_ID" \
    --logs-workspace-key "$LOG_ANALYTICS_SHARED_KEY"
fi

if ! az containerapp show --name "$ACA_APP_NAME" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
  az containerapp create \
    --name "$ACA_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --environment "$ACA_ENV_NAME" \
    --image "$INITIAL_IMAGE" \
    --target-port 50053 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 2 \
    --cpu 0.5 \
    --memory 1.0Gi \
    --revisions-mode multiple \
    --env-vars PROJECT_GRPC_PORT=50053
fi

az containerapp identity assign \
  --name "$ACA_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --system-assigned >/dev/null

ACA_PRINCIPAL_ID=$(az containerapp show \
  --name "$ACA_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query identity.principalId -o tsv)

ACR_ID=$(az acr show \
  --name "$ACR_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query id -o tsv)

if ! az role assignment list --assignee "$ACA_PRINCIPAL_ID" --scope "$ACR_ID" --query "[?roleDefinitionName=='AcrPull'] | length(@)" -o tsv | grep -q "^1$"; then
  az role assignment create \
    --assignee-object-id "$ACA_PRINCIPAL_ID" \
    --assignee-principal-type ServicePrincipal \
    --role AcrPull \
    --scope "$ACR_ID" >/dev/null
fi

az containerapp registry set \
  --name "$ACA_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --server "$ACR_NAME.azurecr.io" \
  --identity system >/dev/null

echo "Provisioning complete."
echo "Add these GitHub repository variables:"
echo "AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, ACR_NAME, ACA_APP_NAME"
