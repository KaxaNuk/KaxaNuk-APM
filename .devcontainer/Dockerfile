# https://hub.docker.com/_/python
FROM python:3.14-slim AS base

# No credential is baked into this image.  A build argument copied into ENV stays in the image and
# in `docker history`, so a token belongs in the environment of a running container, passed by the
# devcontainer or by compose, never in a layer.  Nothing this image installs needs one:
# `requirements-dev.txt` comes from public PyPI.

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
# Keep Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Enable Python tracebacks on segfaults
ENV PYTHONFAULTHANDLER=1
# Turn off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace
COPY . /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      ca-certificates \
      git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements-dev.txt
