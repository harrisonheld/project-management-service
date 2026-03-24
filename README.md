# Project Management Service

### Endpoint
- Local: `localhost:50053` (insecure)
- Deployed: `projectapp.jollyocean-e8f011bb.centralus.azurecontainerapps.io:443` (TLS)

### RPCs
- `CreateProject`
- `ListProjects`
- `GetProject`
- `UpdateProjectStatus`
- `JoinProject`
- `LeaveProject`
- `CheckUserInProject`
- `ValidateProject`

### ProjectService
See `proto/project.proto` for our gRPC contract.

# New Feature - Project Statuses
### Project status values
- `PROJECT_STATUS_TODO`
- `PROJECT_STATUS_IN_PROGRESS`
- `PROJECT_STATUS_DONE`

CreateProject accepts an optional `status` field (defaults to `PROJECT_STATUS_TODO` when omitted), and `GetProject`/`ListProjects` return each project's status.

`UpdateProjectStatus` allows the project owner to change status by slug.

## Developer setup
```sh
cp .env.example .env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### UserAuth endpoint configuration
Set these in `.env` to control which UserAuth service this app calls:

- `USERAUTH_GRPC_ADDR` (example: `user-service.politesky-57421525.centralus.azurecontainerapps.io:443`)
- `USERAUTH_GRPC_TLS` (`true`, `false`, or `auto`)

Notes:
- `USERAUTH_GRPC_TLS=true` uses `grpc.secure_channel(..., grpc.ssl_channel_credentials())`.
- `USERAUTH_GRPC_TLS=false` uses insecure gRPC (useful for local mock services).
- `USERAUTH_GRPC_TLS=auto` enables TLS automatically when the address ends with `:443`.

## Run full stack locally
```sh
./run_full_stack.sh
```

`run_full_stack.sh` does the following:
1. Compiles our .proto files.
2. Starts the mock Auth gRPC service.
3. Starts the Project gRPC service.

## Smoke test
In a separate terminal:
```sh
./smoke_grpc.py
```

`smoke_grpc.py` hits all of the gRPC endpoints we provide.

Our mock of the UserAuth service is setup to accept as valid any token in the form `token-<user>` and will return the user_id as `<user>`. Otherwise the token is invalid.

## CI/CD to Azure Container Apps

This repo now includes GitHub Actions and helper scripts to build Docker images and deploy to Azure Container Apps.

### Files added
- `.github/workflows/ci.yml`: validates Python code, builds Docker image, scans it, pushes to ACR on `main`.
- `.github/workflows/deploy.yml`: deploys the new image to Azure Container Apps after CI succeeds on `main`.
- `scripts/azure/provision_container_apps.sh`: one-time Azure provisioning script.
- `scripts/azure/wait_for_revision_health.sh`: waits for the latest revision to become healthy.
- `scripts/azure/rollback_to_previous_revision.sh`: shifts traffic back to previous revision if deploy fails.

### 1) Provision Azure resources

Run:

```bash
./scripts/azure/provision_container_apps.sh \
	<resource-group> <location> <acr-name> <log-analytics-name> <aca-env-name> <aca-app-name>
```

Example location: `eastus`.

### 2) Configure GitHub OIDC (recommended)

Create an Entra app and federated credential for this repo/branch (`main`) so Actions can log into Azure without secrets.

Then add these GitHub Repository Variables:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_RESOURCE_GROUP`
- `ACR_NAME`
- `ACA_APP_NAME`

Optional: use a protected GitHub Environment named `production` for manual approval before deploy.

### 3) Workflow behavior

- Pull request to `main`: runs validation checks.
- Push to `main`: runs validation, builds image, scans image, pushes to ACR.
- After CI succeeds on `main`: deploy workflow updates Container App revision to image tag = commit SHA.
- If health wait fails: rollback script sends traffic back to previous active revision.
