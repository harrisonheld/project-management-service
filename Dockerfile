# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.8
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# Generate gRPC stubs in-image so runtime does not depend on prebuilt artifacts.
RUN mkdir -p generated \
    && touch generated/__init__.py \
    && python -m grpc_tools.protoc \
      -I./proto \
      --python_out=./generated \
      --grpc_python_out=./generated \
      ./proto/user.proto \
      ./proto/project.proto

RUN groupadd --system app \
    && useradd --system --gid app --create-home --home-dir /home/app app \
    && chown -R app:app /app

USER app

EXPOSE 50053

CMD ["python", "project_grpc_server.py"]
