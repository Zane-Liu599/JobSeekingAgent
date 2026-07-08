FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/packages/platform_common/src:/app/services/ai-service/src:/app/src

WORKDIR /app

COPY requirements.txt ./
COPY packages ./packages
COPY src ./src
COPY services/ai-service ./services/ai-service

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && python -m playwright install --with-deps chromium

EXPOSE 8000
