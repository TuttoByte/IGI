FROM python:3.12.2-slim AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc

COPY requirements.txt .

RUN pip wheel --no-cache-dir --no-deps \
    --wheel-dir /app/wheels -r requirements.txt



FROM python:3.12.2-slim

WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY requirements.txt .

RUN pip install --no-cache /wheels/*

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]