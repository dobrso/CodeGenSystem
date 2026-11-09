FROM docker.io/sbx/shell-image:latest

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src/ ./src/
COPY prompts/ ./prompts/
COPY skills/ ./skills/
COPY souls/ ./souls/

RUN uv sync --frozen --no-install-project

ENV OLLAMA_BASE_URL=http://host.docker.internal:11434
ENV PYTHONPATH=/app/src/codegensystem

WORKDIR /app/src/codegensystem