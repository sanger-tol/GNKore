FROM python:3.13.11-slim-bookworm

LABEL maintainer=dp24@sanger.ac.uk

LABEL org.opencontainers.image.licenses="MIT"

USER root

RUN apt-get update \
    && apt-get install -y procps

RUN pip install uv requests

COPY . /usr/bin/genomenotekore

RUN uv pip install /usr/bin/genomenotekore --system

WORKDIR /tmp
