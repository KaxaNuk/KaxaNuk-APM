# https://hub.docker.com/_/python
# Cf. https://luis-sena.medium.com/creating-the-perfect-python-dockerfile-51bdec41f1c8
FROM python:3.14-slim AS base
ARG GITHUB_TOKEN

# Setup env
ENV GITHUB_TOKEN=${GITHUB_TOKEN}

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
