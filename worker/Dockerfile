# Build stage
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final stage
FROM python:3.13-slim
WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

RUN useradd -r -u 1001 -s /bin/false appuser && \
    chown -R appuser /app

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD python -c "import redis, os; r = redis.Redis(host=os.getenv('REDIS_HOST','redis')); r.ping()" || exit 1

CMD ["python", "worker.py"]
