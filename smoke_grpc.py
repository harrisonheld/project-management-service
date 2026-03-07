#!/usr/bin/env python3
import os
import uuid
import sys
from pathlib import Path

import grpc
import requests


GENERATED_PATH = Path(__file__).resolve().parent / "generated"
if str(GENERATED_PATH) not in sys.path:
	sys.path.insert(0, str(GENERATED_PATH))

import project_pb2  # type: ignore
import project_pb2_grpc  # type: ignore


FLASK_RUN_PORT = os.environ.get("FLASK_RUN_PORT", "5000")
PROJECT_URL = os.environ.get("PROJECT_URL", f"http://localhost:{FLASK_RUN_PORT}")
PROJECT_GRPC_ADDR = os.environ.get("PROJECT_GRPC_ADDR", "localhost:50053")
SMOKE_SLUG = os.environ.get("SMOKE_SLUG", f"smoke-project-{uuid.uuid4().hex[:8]}")
OWNER_TOKEN = os.environ.get("SMOKE_OWNER_TOKEN", f"token-smoke-owner-{uuid.uuid4().hex[:6]}")
OTHER_TOKEN = os.environ.get("SMOKE_OTHER_TOKEN", f"token-smoke-other-{uuid.uuid4().hex[:6]}")


def _create_project(project_url: str, token: str, slug: str) -> None:
	body = {
		"slug": slug,
		"name": "Smoke Project",
		"description": "Created by smoke_grpc.py",
	}
	headers = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer {token}",
	}
	resp = requests.post(f"{project_url}/projects", json=body, headers=headers, timeout=10)
	if resp.status_code != 201:
		raise AssertionError(f"project setup failed: HTTP {resp.status_code} body={resp.text}")
	print(f"PASS: setup project created -> slug={slug}")


def _assert_membership(stub, token: str, slug: str, expected: bool, label: str) -> None:
	response = stub.CheckUserInProject(
		project_pb2.CheckUserInProjectRequest(token=token, project_slug=slug)
	)
	if response.in_project != expected:
		raise AssertionError(
			f"{label}: expected in_project={expected}, got {response.in_project}"
		)
	print(f"PASS: {label} -> in_project={response.in_project}")


def _assert_unauthenticated(stub, token: str, slug: str, label: str) -> None:
	try:
		stub.CheckUserInProject(project_pb2.CheckUserInProjectRequest(token=token, project_slug=slug))
		raise AssertionError(f"{label}: expected UNAUTHENTICATED error, call succeeded")
	except grpc.RpcError as exc:
		if exc.code() != grpc.StatusCode.UNAUTHENTICATED:
			raise AssertionError(
				f"{label}: expected UNAUTHENTICATED, got {exc.code().name}: {exc.details()}"
			)
		print(f"PASS: {label} -> {exc.code().name}")


def main() -> int:
	channel = grpc.insecure_channel(PROJECT_GRPC_ADDR)
	stub = project_pb2_grpc.ProjectServiceStub(channel)

	try:
		_create_project(PROJECT_URL, OWNER_TOKEN, SMOKE_SLUG)
		_assert_membership(stub, OWNER_TOKEN, SMOKE_SLUG, True, "owner membership")
		_assert_membership(stub, OTHER_TOKEN, SMOKE_SLUG, False, "other user non-membership")
		_assert_unauthenticated(stub, "not-a-real-token", SMOKE_SLUG, "invalid token rejection")
	except AssertionError as exc:
		print(f"FAIL: {exc}")
		return 1
	except requests.RequestException as exc:
		print(f"FAIL: HTTP setup error: {exc}")
		return 1
	except grpc.RpcError as exc:
		print(f"FAIL: unexpected gRPC error {exc.code().name}: {exc.details()}")
		return 1

	print("gRPC smoke tests passed")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

