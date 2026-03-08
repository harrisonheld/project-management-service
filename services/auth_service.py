import os
import sys
from pathlib import Path

import grpc


GENERATED_PATH = Path(__file__).resolve().parent.parent / "generated"
if str(GENERATED_PATH) not in sys.path:
    sys.path.insert(0, str(GENERATED_PATH))

import user_pb2
import user_pb2_grpc


USERAUTH_GRPC_ADDR = os.environ.get("USERAUTH_GRPC_ADDR", os.environ.get("USER_GRPC_ADDR", "localhost:50051"))

_channel = None
_stub = None


def _get_stub():
    global _channel, _stub
    if _stub is None:
        _channel = grpc.insecure_channel(USERAUTH_GRPC_ADDR)
        _stub = user_pb2_grpc.UserServiceStub(_channel)
    return _stub


def _grpc_to_http_status(code):
    if code == grpc.StatusCode.INVALID_ARGUMENT:
        return 400
    if code == grpc.StatusCode.UNAUTHENTICATED:
        return 401
    if code == grpc.StatusCode.NOT_FOUND:
        return 404
    if code == grpc.StatusCode.UNAVAILABLE:
        return 503
    return 500


def validate_token(token):
    try:
        response = _get_stub().Me(
            user_pb2.MeRequest(),
            metadata=(("authorization", f"Bearer {token or ''}"),),
        )
        if not response.ok or not response.userId:
            return 401, {"error": "Invalid token", "valid": False}
        return 200, {
            "valid": True,
            "user_id": response.userId,
            "username": response.username or response.userId,
        }
    except grpc.RpcError as exc:
        return _grpc_to_http_status(exc.code()), {"error": exc.details() or "Invalid token", "valid": False}
