#!/bin/bash
# Run the full ProjectManagement app with gRPC internal service mocks

set -euo pipefail

if [ -f .env ]; then
    source .env
else
    echo ".env file not found. Please create it from .env.example."
    exit 1
fi

if [ -d venv ]; then
    source venv/bin/activate
else
    echo "Python venv not found. Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

#
# compile protobuf files
#
mkdir -p generated
touch generated/__init__.py

echo "Generating gRPC Python code from .proto files..."
python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./generated \
    --grpc_python_out=./generated \
    ./proto/user.proto \
    ./proto/project.proto

export USERAUTH_GRPC_PORT="${USERAUTH_GRPC_PORT:-50051}"
export USERAUTH_GRPC_ADDR="${USERAUTH_GRPC_ADDR:-localhost:${USERAUTH_GRPC_PORT}}"
export USER_GRPC_ADDR="${USER_GRPC_ADDR:-${USERAUTH_GRPC_ADDR}}"
export PROJECT_GRPC_PORT="${PROJECT_GRPC_PORT:-50053}"
export PROJECT_GRPC_ADDR="${PROJECT_GRPC_ADDR:-localhost:${PROJECT_GRPC_PORT}}"

python mocks/mock_auth.py &
MOCK_USERAUTH_PID=$!
sleep 1

python project_grpc_server.py &
PROJECT_GRPC_PID=$!
sleep 1

trap "kill $MOCK_USERAUTH_PID 2>/dev/null || true; kill $PROJECT_GRPC_PID 2>/dev/null || true" EXIT

export FLASK_APP=app.py
export FLASK_ENV=development
flask run
