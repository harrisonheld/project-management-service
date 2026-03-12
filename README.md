# Project Management Service
## gRPC API

### ProjectService
See `proto/project.proto` for our gRPC contract.

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
