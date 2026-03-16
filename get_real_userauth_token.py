#!/usr/bin/env python3
import os
import sys
import uuid
from pathlib import Path

import grpc


GENERATED_PATH = Path(__file__).resolve().parent / "generated"
if str(GENERATED_PATH) not in sys.path:
    sys.path.insert(0, str(GENERATED_PATH))

import user_pb2  # type: ignore
import user_pb2_grpc  # type: ignore

def main() -> int:
    target = "user-service.politesky-57421525.centralus.azurecontainerapps.io:443"
    # user_id and username will be the same
    user_id = "harrison"
    username = "harrison"
    password = "password"

    channel = grpc.secure_channel(target, grpc.ssl_channel_credentials())
    stub = user_pb2_grpc.UserServiceStub(channel)

    try:
        #
        # register a new user
        #
        register_response = stub.Register(
            user_pb2.RegisterRequest(userId=user_id, username=username, password=password),
            timeout=8,
        )
        print(f"register_ok={register_response.ok} register_message={register_response.message}")

        #
        # login to get a token
        #
        login_response = stub.Login(
            user_pb2.LoginRequest(userId=user_id, password=password),
            timeout=8,
        )
        if not login_response.ok or not login_response.token:
            print(f"login_ok={login_response.ok} login_message={login_response.message}")
            return 1

        print("login_ok=True")
        print(f"TOKEN={login_response.token}")

        #
        # validate a token to get the userId and username
        #
        validate_response = stub.Me(
            user_pb2.MeRequest(),
            metadata=(("authorization", f"Bearer {login_response.token}"),),
            timeout=8,
        )
        if not validate_response.ok:
            print(f"validate_ok={validate_response.ok} validate_message={validate_response.message}")
            return 1

        print("validate_ok=True")
        print(f"validate_userId={validate_response.userId} validate_username={validate_response.username}")
        return 0
    except grpc.RpcError as exc:
        print(f"code={exc.code().name} details={exc.details()}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())