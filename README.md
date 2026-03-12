# Project Management Service (gRPC-only)

This service now exposes **only gRPC APIs**. No HTTP endpoints are provided.

## gRPC API

### Service
- Address (local): `PROJECT_GRPC_ADDR` (default `localhost:50053`)
- Service: `ProjectService`

### RPCs
- `CreateProject(CreateProjectRequest) returns (CreateProjectResponse)`
- `ListProjects(ListProjectsRequest) returns (ListProjectsResponse)`
- `GetProject(GetProjectRequest) returns (GetProjectResponse)`
- `JoinProject(JoinProjectRequest) returns (JoinProjectResponse)`
- `LeaveProject(LeaveProjectRequest) returns (LeaveProjectResponse)`
- `CheckUserInProject(CheckUserInProjectRequest) returns (CheckUserInProjectResponse)`
- `ValidateProject(ValidateProjectRequest) returns (ValidateProjectResponse)`

### Core messages
```proto
message Project {
  string id = 1;
  string slug = 2;
  string name = 3;
  string description = 4;
  string owner = 5;
  repeated string users = 6;
}
```

All requests include `token` for auth, except `ValidateProject` which accepts `project_id`. Slug-based methods include `project_slug` (or `slug` on create).

### gRPC status mapping
- `INVALID_ARGUMENT`: required fields missing (e.g. empty token, slug, or name)
- `UNAUTHENTICATED`: token invalid/expired
- `NOT_FOUND`: project slug not found
- `ALREADY_EXISTS`: create with duplicate slug
- `FAILED_PRECONDITION`: business rules (already member, not a member, last user cannot leave)

## Authentication behavior

The mock UserAuth service accepts any token shaped like `token-<user>` and resolves `user_id=<user>`. Other tokens are rejected as unauthenticated.

## Developer setup

```sh
cp .env.example .env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run locally

```sh
./run_full_stack.sh
```

`run_full_stack.sh`:
1. Compiles `.proto` files.
2. Starts the mock Auth gRPC service.
3. Starts the Project gRPC service (foreground).

## Smoke test

In a separate terminal:

```sh
source venv/bin/activate
./smoke_grpc.py
```

`smoke_grpc.py` covers create/list/get/join/leave/membership flows and common auth/rule failures using only gRPC.
