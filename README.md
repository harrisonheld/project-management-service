# Project Management Service


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
3. Starts OUR Project Management HTTP API.

## Smoke test
In a separate terminal:
```sh
./usage.sh
```

`usage.sh` drives gRPC auth login/register via Python stubs and then exercises the public ProjectManagement HTTP endpoints.
