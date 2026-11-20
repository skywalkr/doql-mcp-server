FROM python:3.15-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN useradd --create-home --uid 1000 app

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install . \
    && rm -rf build src/*.egg-info

USER app

EXPOSE 8000
ENTRYPOINT ["doql-mcp"]
CMD ["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]
