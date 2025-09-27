FROM mcr.microsoft.com/devcontainers/python:3.11

COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements-dev.txt

WORKDIR /workspace
