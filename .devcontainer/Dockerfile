# https://hub.docker.com/_/python
# Cf. https://luis-sena.medium.com/creating-the-perfect-python-dockerfile-51bdec41f1c8
FROM python:3.14-slim AS base

# No credential is baked into this image.  A build argument copied into ENV stays in the image and
# in `docker history`, so a token belongs in the environment of a running container, passed by the
# devcontainer or by compose, never in a layer.  Nothing this image installs needs one:
# `requirements-dev.txt` comes from public PyPI.

# Setup env
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

# Install OS dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      ca-certificates \
      git \
    && rm -rf /var/lib/apt/lists/*

# Install APM
RUN pip install -r requirements-dev.txt
