from concurrent import futures
import os
import sys
from pathlib import Path

import grpc
GENERATED_PATH = Path(__file__).resolve().parent.parent / "generated" 
if str(GENERATED_PATH) not in sys.path: 
    sys.path.insert(0, str(GENERATED_PATH))
import users_pb2  # type: ignore
import users_pb2_grpc # type: ignore


AUTH_GRPC_PORT = os.environ.get("USERAUTH_GRPC_PORT", os.environ.get("USER_GRPC_PORT", "50051"))
TOKEN_PREFIX = "token-"


class AuthService(users_pb2_grpc.AuthServiceServicer):
    # MOCK of the Verify token method
    # Any token beginning with the TOKEN_PREFIX will be accepted as valid
    # Otherwise it will be invalid

    def VerifyToken(self, request, context):
        token = (request.token or "").strip()
        if not token.startswith(TOKEN_PREFIX) or len(token) <= len(TOKEN_PREFIX):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Invalid token")
            print(f"mock_auth.py: INVALID TOKEN: {token}")
            return users_pb2.VerifyTokenResponse()

        user_id = token[len(TOKEN_PREFIX):]  # just send whatever comes after "token-"
        print(f"mock_auth.py: VALID TOKEN: {token}. RETURNING user_id={user_id}")
        return users_pb2.VerifyTokenResponse(user_id=user_id)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    users_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port(f"[::]:{AUTH_GRPC_PORT}")
    server.start()
    print(f"Mock Auth gRPC service listening on :{AUTH_GRPC_PORT}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
