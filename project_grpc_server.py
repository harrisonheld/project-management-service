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

import project_pb2  # type: ignore[import-not-found]
import project_pb2_grpc  # type: ignore[import-not-found]


PROJECT_GRPC_PORT = os.environ.get("PROJECT_GRPC_PORT", "50053")


class ProjectGrpcService(project_pb2_grpc.ProjectServiceServicer):
    _PROTO_TO_STATUS = {
        project_pb2.PROJECT_STATUS_UNSPECIFIED: "todo",
        project_pb2.PROJECT_STATUS_TODO: "todo",
        project_pb2.PROJECT_STATUS_IN_PROGRESS: "in_progress",
        project_pb2.PROJECT_STATUS_DONE: "done",
    }
    _STATUS_TO_PROTO = {
        "todo": project_pb2.PROJECT_STATUS_TODO,
        "in_progress": project_pb2.PROJECT_STATUS_IN_PROGRESS,
        "done": project_pb2.PROJECT_STATUS_DONE,
    }

    @staticmethod
    def _authenticate(token: str, context):
        cleaned_token = (token or "").strip()
        if not cleaned_token:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("token is required")
            return None

        auth_status, auth_resp = auth_service.validate_token(cleaned_token)
        if auth_status != 200 or not auth_resp.get("valid"):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details(auth_resp.get("error", "Invalid token"))
            return None

        return auth_resp.get("user_id", "")

    @classmethod
    def _status_proto_to_string(cls, status_enum: int) -> str:
        return cls._PROTO_TO_STATUS.get(status_enum, "todo")

    @classmethod
    def _status_string_to_proto(cls, status: str) -> int:
        normalized = (status or "").strip().lower()
        return cls._STATUS_TO_PROTO.get(normalized, project_pb2.PROJECT_STATUS_TODO)

    @staticmethod
    def _project_to_proto(project):
        status = ProjectGrpcService._status_string_to_proto(project.get("status", "todo"))
        return project_pb2.Project(
            id=str(project.get("_id", project.get("id", ""))),
            slug=project.get("slug", ""),
            name=project.get("name", ""),
            description=project.get("description", ""),
            owner=str(project.get("owner", "")),
            users=[str(u) for u in project.get("users", [])],
            status=status,
        )

    def CreateProject(self, request, context):
        user_id = self._authenticate(request.token, context)
        if not user_id:
            return project_pb2.CreateProjectResponse()

        slug = (request.slug or "").strip()
        name = (request.name or "").strip()
        description = request.description or ""
        status = self._status_proto_to_string(request.status)

        if not slug or not name:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("slug and name required")
            return project_pb2.CreateProjectResponse()

        success, message, data = project_service.create_new_project(
            slug,
            name,
            description,
            user_id,
            status,
        )
        if not success:
            if message == "Slug already exists":
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            else:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details(message)
            return project_pb2.CreateProjectResponse()

        data = data or {}
        return project_pb2.CreateProjectResponse(project_id=str(data.get("project_id", "")))

    def ListProjects(self, request, context):
        user_id = self._authenticate(request.token, context)
        if not user_id:
            return project_pb2.ListProjectsResponse()

        projects = project_service.get_user_projects(user_id)
        return project_pb2.ListProjectsResponse(
            projects=[self._project_to_proto(project) for project in projects]
        )

    def GetProject(self, request, context):
        user_id = self._authenticate(request.token, context)
        if not user_id:
            return project_pb2.GetProjectResponse()

        project_slug = (request.project_slug or "").strip()
        if not project_slug:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("project_slug is required")
            return project_pb2.GetProjectResponse()

        success, message, data = project_service.get_project_details(project_slug)
        if not success:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(message)
            return project_pb2.GetProjectResponse()

        return project_pb2.GetProjectResponse(project=self._project_to_proto(data))

    def UpdateProjectStatus(self, request, context):
        user_id = self._authenticate(request.token, context)
        if not user_id:
            return project_pb2.UpdateProjectStatusResponse()

        project_slug = (request.project_slug or "").strip()
        if not project_slug:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("project_slug is required")
            return project_pb2.UpdateProjectStatusResponse()

        status = self._status_proto_to_string(request.status)
        success, message, data = project_service.update_project_status(project_slug, user_id, status)
        if not success:
            if message == "Project not found":
                context.set_code(grpc.StatusCode.NOT_FOUND)
            elif message == "Only the project owner can update status":
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            else:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details(message)
            return project_pb2.UpdateProjectStatusResponse()

        data = data or {}
        return project_pb2.UpdateProjectStatusResponse(
            message=message,
            project_id=str(data.get("project_id", "")),
            project_slug=data.get("slug", ""),
            project_name=data.get("name", ""),
            status=self._status_string_to_proto(data.get("status", "todo")),
        )

    def JoinProject(self, request, context):
        user_id = self._authenticate(request.token, context)
        if not user_id:
            return project_pb2.JoinProjectResponse()

        project_slug = (request.project_slug or "").strip()
        if not project_slug:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("project_slug is required")
            return project_pb2.JoinProjectResponse()

        success, message, data = project_service.join_project(project_slug, user_id)
        if not success:
            if message == "Project not found":
                context.set_code(grpc.StatusCode.NOT_FOUND)
            else:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details(message)
            return project_pb2.JoinProjectResponse()

        data = data or {}
        return project_pb2.JoinProjectResponse(
            message=message,
            project_id=str(data.get("project_id", "")),
            project_slug=data.get("slug", ""),
            project_name=data.get("name", ""),
        )

    def LeaveProject(self, request, context):
        user_id = self._authenticate(request.token, context)
        if not user_id:
            return project_pb2.LeaveProjectResponse()

        project_slug = (request.project_slug or "").strip()
        if not project_slug:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("project_slug is required")
            return project_pb2.LeaveProjectResponse()

        success, message, data = project_service.leave_project(project_slug, user_id)
        if not success:
            if message == "Project not found":
                context.set_code(grpc.StatusCode.NOT_FOUND)
            else:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details(message)
            return project_pb2.LeaveProjectResponse()

        data = data or {}
        return project_pb2.LeaveProjectResponse(
            message=message,
            project_id=str(data.get("project_id", "")),
            project_slug=data.get("slug", ""),
            project_name=data.get("name", ""),
        )

    def CheckUserInProject(self, request, context):
        project_slug = (request.project_slug or "").strip()

        user_id = self._authenticate(request.token, context)
        if not user_id:
            return project_pb2.CheckUserInProjectResponse()

        if not project_slug:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("project_slug is required")
            return project_pb2.CheckUserInProjectResponse()

        success, message, data = project_service.check_user_in_project(project_slug, user_id)
        if not success:
            if message == "Project not found":
                context.set_code(grpc.StatusCode.NOT_FOUND)
            else:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details(message)
            return project_pb2.CheckUserInProjectResponse()

        data = data or {}
        return project_pb2.CheckUserInProjectResponse(
            in_project=bool(data.get("in_project")),
        )

    def ValidateProject(self, request, context):
        project_id = (request.project_id or "").strip()
        if not project_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("project_id is required")
            return project_pb2.ValidateProjectResponse()

        _, _, data = project_service.validate_project(project_id)
        data = data or {}
        return project_pb2.ValidateProjectResponse(valid=bool(data.get("valid")))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    project_pb2_grpc.add_ProjectServiceServicer_to_server(ProjectGrpcService(), server)
    server.add_insecure_port(f"[::]:{PROJECT_GRPC_PORT}")
    server.start()
    print(f"Project gRPC service listening on :{PROJECT_GRPC_PORT}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
