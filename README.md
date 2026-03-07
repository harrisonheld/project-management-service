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

`usage.sh` hits all of our HTTP endpoints and prints the results and status codes. 

The UserAuth service is setup to accept as valid any token in the form `token-<user>` and will return the user_id as `<user>`. Otherwise the token is invalid.
