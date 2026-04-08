FROM python:3.11-slim

WORKDIR /app

COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY automation/ ./automation/
COPY registry/ ./registry/

ENV PYTHONUNBUFFERED=1

EXPOSE 5000
