import logging
import os
import sys
from pathlib import Path

import grpc

logger = logging.getLogger(__name__)


GENERATED_PATH = Path(__file__).resolve().parent.parent / "generated"
if str(GENERATED_PATH) not in sys.path:
    sys.path.insert(0, str(GENERATED_PATH))

import user_pb2
import user_pb2_grpc


USERAUTH_GRPC_ADDR = os.environ.get("USERAUTH_GRPC_ADDR", os.environ.get("USER_GRPC_ADDR", "localhost:50051"))
USERAUTH_GRPC_TLS = (os.environ.get("USERAUTH_GRPC_TLS") or "auto").strip().lower()

_channel = None
_stub = None


def _should_use_tls() -> bool:
    if USERAUTH_GRPC_TLS in {"1", "true", "yes", "on"}:
        return True
    if USERAUTH_GRPC_TLS in {"0", "false", "no", "off"}:
        return False
    return USERAUTH_GRPC_ADDR.endswith(":443")


def _get_stub():
    global _channel, _stub
    if _stub is None:
        if _should_use_tls():
            _channel = grpc.secure_channel(USERAUTH_GRPC_ADDR, grpc.ssl_channel_credentials())
        else:
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
    logger.info("validate_token called")
    try:
        response = _get_stub().Me(
            user_pb2.MeRequest(),
            metadata=(("authorization", f"Bearer {token or ''}"),),
        )
        if not response.ok or not response.userId:
            logger.warning("Token validation failed: invalid response")
            return 401, {"error": "Invalid token", "valid": False}
        logger.info("Token validated for user=%s", response.userId)
        return 200, {
            "valid": True,
            "user_id": response.userId,
            "username": response.username or response.userId,
        }
    except grpc.RpcError as exc:
        logger.warning("Token validation RPC error: %s", exc.details())
        return _grpc_to_http_status(exc.code()), {"error": exc.details() or "Invalid token", "valid": False}
