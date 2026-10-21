FROM python:3.13.16-slim-bookworm AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY ./weatherapp/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.13.16-slim-bookworm

WORKDIR /app
RUN useradd -ms /bin/bash worker && \
    apt-get update && \
    apt-get install -y --no-install-recommends wget && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

USER worker
ENV PATH="/home/worker/.local/bin:${PATH}"

COPY --chown=worker:worker ./weatherapp .

HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget -q --spider http://127.0.0.1:5001/health || exit 1

ARG GUNICORN_WORKERS=2
ENV WORKERS=${GUNICORN_WORKERS}

EXPOSE 5000
CMD ["sh", "-c", "exec gunicorn wsgi:app --bind 0.0.0.0:5001 --workers ${WORKERS:-2}"]