FROM python:3.12-slim-bookworm

ARG SERVICE_NAME

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/packages/platform_common/src:/app/services/${SERVICE_NAME}/src:/app/src

WORKDIR /app

COPY requirements.txt ./
COPY packages ./packages
COPY src ./src
COPY services/${SERVICE_NAME} ./services/${SERVICE_NAME}

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

EXPOSE 8000
