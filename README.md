# Project Management Service

## HTTP API (for Frontend Team)

### Base URL
- Local: `http://localhost:5000`

### Authentication
- All endpoints require `Authorization: Bearer <token>`. This token is to be obtained by calling the User Service.
- If you provide an invalid token, you will get one of the following errors:
- If the header is missing or malformed, API returns `401` with:
	- `{"error":"Missing or invalid Authorization header"}`
- If token validation fails, API returns `401` with:
	- `{"error":"Invalid or expired token"}`
---

### 1) Create Project
- **Method / Path**: `POST /projects`
- **Headers**:
	- `Content-Type: application/json`
	- `Authorization: Bearer <token>`
- **Request Body**:
```json
{
	"slug": "project-alpha",
	"name": "Project Alpha",
	"description": "Optional description"
}
```
- **Success**: `201 Created`
```json
{
	"project_id": "69ac7a257bebdeca3b00a8c0"
}
```
- **Errors**:
	- `400` if `slug` or `name` missing:
		- `{"error":"slug and name required"}`
	- `400` if slug already exists:
		- `{"error":"Slug already exists"}`
	- `401` auth errors (see Authentication section)

---

### 2) Get My Projects
- **Method / Path**: `GET /projects`
- **Headers**:
	- `Authorization: Bearer <token>`
- **Success**: `200 OK`
```json
[
	{
		"id": "69ac7a257bebdeca3b00a8c0",
		"name": "Project Alpha",
		"slug": "project-alpha",
		"owner": "alice123",
		"users": ["alice123", "bob456"],
		"description": "Optional description"
	}
]
```
- **Errors**:
	- `401` auth errors

---

### 3) Get Project Details by Slug
- **Method / Path**: `GET /projects/<slug>`
- **Headers**:
	- `Authorization: Bearer <token>`
- **Success**: `200 OK`
```json
{
	"_id": "69ac7a257bebdeca3b00a8c0",
	"slug": "project-alpha",
	"name": "Project Alpha",
	"description": "Optional description",
	"owner": "alice123",
	"users": ["alice123", "bob456"]
}
```
- **Errors**:
	- `404` if project not found:
		- `{"error":"Not found"}`
	- `401` auth errors

---

### 4) Join Project
- **Method / Path**: `POST /projects/<slug>/join`
- **Headers**:
	- `Authorization: Bearer <token>`
- **Request Body**: none
- **Success**: `200 OK`
```json
{
	"message": "Successfully joined project",
	"project_id": "69ac7a257bebdeca3b00a8c0",
	"slug": "project-alpha",
	"name": "Project Alpha"
}
```
- **Errors**:
	- `404` if project not found:
		- `{"error":"Project not found"}`
	- `400` if already a member:
		- `{"error":"Already a member of this project"}`
	- `401` auth errors

---

### 5) Leave Project
- **Method / Path**: `POST /projects/<slug>/leave`
- **Headers**:
	- `Authorization: Bearer <token>`
- **Request Body**: none
- **Success**: `200 OK`
```json
{
	"message": "Successfully left project",
	"project_id": "69ac7a257bebdeca3b00a8c0",
	"slug": "project-alpha",
	"name": "Project Alpha"
}
```
- **Errors**:
	- `404` if project not found:
		- `{"error":"Project not found"}`
	- `400` if requester is not a member:
		- `{"error":"Not a member of this project"}`
	- `400` if requester is last remaining member:
		- `{"error":"The last user cannot leave the project"}`
	- `401` auth errors

---

### 6) Check Membership
- **Method / Path**: `GET /projects/<slug>/membership`
- **Headers**:
	- `Authorization: Bearer <token>`
- **Request Body**: none
- **Success**: `200 OK`
```json
{
	"message": "Membership checked",
	"project_slug": "project-alpha",
	"user_id": "alice123",
	"in_project": true
}
```
- **Errors**:
	- `404` if project not found:
		- `{"error":"Project not found"}`
	- `401` auth errors

---

## gRPC API (for Resource team)

### ProjectService
- **Address (local)**: `PROJECT_GRPC_ADDR` (default `localhost:50053`)
- **RPC**: `CheckUserInProject(CheckUserInProjectRequest) returns (CheckUserInProjectResponse)`

**Request**
```proto
message CheckUserInProjectRequest {
  string token = 1;
  string project_slug = 2;
}
```

**Response**
```proto
message CheckUserInProjectResponse {
  bool in_project = 1;
}
```

**gRPC error mapping**
- `INVALID_ARGUMENT`: token or project_slug missing
- `UNAUTHENTICATED`: token invalid
- `NOT_FOUND`: project slug not found

---

### Frontend notes
- `owner` and `users[]` are user IDs (strings from auth service).
- Project lookup for details uses `slug`.
- `join`/`leave` infer acting user from bearer token; no user ID in request body.

## Developer setup
```sh
cp .env.example .env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run full stack locally
```sh
./run_full_stack.sh
```

`run_full_stack.sh` does the following:
1. Compiles our .proto files.
2. Starts the mock Auth gRPC service.
3. Starts the Project gRPC service.
4. Starts OUR Project Management HTTP API.

## Smoke test
In a separate terminal:
```sh
./smoke_http.sh
./smoke_grpc.py
```

`smoke_http.sh` hits all of our HTTP endpoints and prints the results and status codes. 
`smoke_grpc.sh` hits all of the gRPC endpoints we provide.


The UserAuth service is setup to accept as valid any token in the form `token-<user>` and will return the user_id as `<user>`. Otherwise the token is invalid.
