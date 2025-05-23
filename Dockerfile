FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml README_PYPI.md ./
COPY src ./src

RUN pip install --no-cache-dir pdm && \
    pdm install --prod --no-lock --no-editable

ENTRYPOINT ["pdm", "run", "motify"] 