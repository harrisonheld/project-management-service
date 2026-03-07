from concurrent import futures
import os
import sys
from pathlib import Path

import grpc

import services.auth_service as auth_service
import services.project_service as project_service


GENERATED_PATH = Path(__file__).resolve().parent / "generated"
if str(GENERATED_PATH) not in sys.path:
    sys.path.insert(0, str(GENERATED_PATH))

import project_pb2
import project_pb2_grpc


PROJECT_GRPC_PORT = os.environ.get("PROJECT_GRPC_PORT", "50053")


class ProjectGrpcService(project_pb2_grpc.ProjectServiceServicer):
    def CheckUserInProject(self, request, context):
        token = (request.token or "").strip()
        project_slug = (request.project_slug or "").strip()

        if not token or not project_slug:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("token and project_slug are required")
            return project_pb2.CheckUserInProjectResponse()

        auth_status, auth_resp = auth_service.validate_token(token)
        if auth_status != 200 or not auth_resp.get("valid"):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details(auth_resp.get("error", "Invalid token"))
            return project_pb2.CheckUserInProjectResponse()

        user_id = auth_resp.get("user_id", "")
        success, message, data = project_service.check_user_in_project(project_slug, user_id)
        if not success:
            if message == "Project not found":
                context.set_code(grpc.StatusCode.NOT_FOUND)
            else:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details(message)
            return project_pb2.CheckUserInProjectResponse()

        return project_pb2.CheckUserInProjectResponse(
            in_project=bool(data.get("in_project")),
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    project_pb2_grpc.add_ProjectServiceServicer_to_server(ProjectGrpcService(), server)
    server.add_insecure_port(f"[::]:{PROJECT_GRPC_PORT}")
    server.start()
    print(f"Project gRPC service listening on :{PROJECT_GRPC_PORT}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
