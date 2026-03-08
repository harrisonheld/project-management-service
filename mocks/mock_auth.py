from concurrent import futures
import os
import sys
from pathlib import Path

import grpc
GENERATED_PATH = Path(__file__).resolve().parent.parent / "generated" 
if str(GENERATED_PATH) not in sys.path: 
    sys.path.insert(0, str(GENERATED_PATH))
import user_pb2  # type: ignore
import user_pb2_grpc # type: ignore


AUTH_GRPC_PORT = os.environ.get("USERAUTH_GRPC_PORT", os.environ.get("USER_GRPC_PORT", "50051"))
TOKEN_PREFIX = "token-"


class AuthService(user_pb2_grpc.UserServiceServicer):
    def Register(self, request, context):
        return user_pb2.RegisterResponse(ok=True, message="registered")

    def Login(self, request, context):
        user_id = (request.userId or "").strip()
        if not user_id:
            return user_pb2.LoginResponse(ok=False, token="", message="userId required")
        return user_pb2.LoginResponse(ok=True, token=f"{TOKEN_PREFIX}{user_id}", message="ok")

    def Me(self, request, context):
        metadata = dict(context.invocation_metadata())
        auth = metadata.get("authorization") or metadata.get("Authorization") or ""
        token = auth.split(" ", 1)[1].strip() if auth.startswith("Bearer ") else ""

        if not token.startswith(TOKEN_PREFIX) or len(token) <= len(TOKEN_PREFIX):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Invalid token")
            return user_pb2.MeResponse(ok=False, userId="", username="", message="unauthorized")

        user_id = token[len(TOKEN_PREFIX):]
        return user_pb2.MeResponse(ok=True, userId=user_id, username=user_id, message="ok")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port(f"[::]:{AUTH_GRPC_PORT}")
    server.start()
    print(f"Mock User gRPC service listening on :{AUTH_GRPC_PORT}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
