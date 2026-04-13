FROM python:3.11-slim-bookworm

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BROKER_DATA_DIR=/workspace/data \
    BROKER_ARTIFACT_DIR=/workspace/artifacts \
    BROKER_RUNTIME_HOST=127.0.0.1 \
    BROKER_RUNTIME_PORT=9876

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    ffmpeg \
    jq \
    blender \
    && rm -rf /var/lib/apt/lists/*

COPY sandbox-image/requirements.txt /opt/codex/requirements.txt
RUN python3 -m pip install -r /opt/codex/requirements.txt

COPY broker /opt/codex/broker
COPY sandbox-runtime /opt/codex/sandbox-runtime
COPY sandbox-image/start-all.sh /opt/codex/start-all.sh
COPY sandbox-image/install_warp.sh /opt/codex/install_warp.sh
RUN chmod +x /opt/codex/start-all.sh /opt/codex/install_warp.sh && /opt/codex/install_warp.sh

WORKDIR /opt/codex/broker
EXPOSE 8080 3001 22
CMD ["/bin/bash", "/opt/codex/start-all.sh"]
